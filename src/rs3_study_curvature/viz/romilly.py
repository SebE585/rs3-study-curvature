from __future__ import annotations
import os
import datetime as dt
from typing import Iterable, Optional, Tuple

import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import typer
from shapely.geometry import box, Point

try:
    from shapely.validation import make_valid  # type: ignore

    HAS_MAKE_VALID = True
except Exception:  # pragma: no cover
    HAS_MAKE_VALID = False
import unicodedata
import re

try:
    import pyogrio  # type: ignore

    HAS_PYOGRIO = True
except Exception:  # pragma: no cover
    HAS_PYOGRIO = False

try:
    from pyproj import Transformer  # type: ignore

    HAS_PYPROJ = True
except Exception:  # pragma: no cover
    HAS_PYPROJ = False

app = typer.Typer(add_completion=False)

# --- chemins par défaut (modifiables par options CLI)
DEFAULT_OSM_GEOM = "../../rs3-data/osm/normandie-highways.geojson"
DEFAULT_IGN_GEOM = "../../rs3-data/bdtopo/troncon_de_route.gpkg"
DEFAULT_OSM_SEG = "../../rs3-data/ref/roadinfo/roadinfo_segments_osm.parquet"
DEFAULT_IGN_SEG = "../../rs3-data/ref/roadinfo/roadinfo_segments_bdtopo.parquet"

# --- bbox Romilly-sur-Andelle (WGS84) : approx
ROMILLY_BBOX = (1.22, 49.30, 1.30, 49.36)  # (xmin, ymin, xmax, ymax) lon/lat

# colonnes utiles des tables segments (pour limiter l'I/O)
SEG_COLUMNS = [
    "x_centroid",
    "y_centroid",
    "radius_min_m",
    "radius_p85_m",
    "curv_mean_1perm",
    "class",
    "name",
]

# === Helpers noms de voies & fallback spatial ===
NAME_COL_HINTS = ("name", "nom", "voie", "libel", "topo")


def _normalize_text(s: str) -> str:
    if s is None:
        return ""
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode("ascii")
    s = s.lower()
    # enlever ponctuation légère et termes génériques
    s = re.sub(r"[\W_]+", " ", s, flags=re.U)
    s = re.sub(r"\b(rue|avenue|av|bd|boulevard|chemin|route|impasse|allee|place|quai|square|cours)\b", "", s)
    return re.sub(r"\s+", " ", s).strip()


def _guess_name_columns(df: pd.DataFrame) -> list[str]:
    cands: list[str] = []
    for c in df.columns:
        cl = c.lower()
        if any(h in cl for h in NAME_COL_HINTS) and df[c].dtype == object:
            cands.append(c)
    preferred = [c for c in ["name", "nom_voie", "nom", "libelle"] if c in df.columns]
    # dédupliquer en gardant l'ordre
    return list(dict.fromkeys(preferred + cands))


def _filter_by_street_name(gdf: gpd.GeoDataFrame, street: str) -> gpd.GeoDataFrame:
    if not street or gdf.empty:
        return gdf
    target = _normalize_text(street)
    cols = _guess_name_columns(gdf)
    if not cols:
        return gdf.iloc[0:0]
    mask = False
    for c in cols:
        norm = gdf[c].astype(str).map(_normalize_text)
        mask = mask | norm.str.contains(re.escape(target))
    return gdf[mask].copy()


def _fallback_overlap(source: gpd.GeoDataFrame, target: gpd.GeoDataFrame, buf_m: float = 50.0) -> gpd.GeoDataFrame:
    """Si 'target' n'a pas matché par le nom, on récupère ce qui chevauche 'source' (buffer en mètres)."""
    if source.empty or target.empty:
        return target.iloc[0:0]
    src3857 = source.to_crs(3857)
    tgt3857 = target.to_crs(3857)
    try:
        area = src3857.buffer(buf_m).union_all()
    except Exception:
        # compat geopandas <0.14
        area = src3857.buffer(buf_m).unary_union
    hit = tgt3857[tgt3857.intersects(area)].copy()
    return hit.to_crs(4326)


# --- Geometry cleaning and robust buffer helpers ---
def _clean_geoms(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Nettoie des géométries potentiellement invalides sans casser les lignes.
    - utilise shapely.make_valid si dispo
    - pour les Polygons uniquement, utilise buffer(0) comme fallback
    - supprime les géométries NA/invalides restantes
    """
    if gdf is None or len(gdf) == 0:
        return gdf
    out = gdf.copy()
    geom = out.geometry
    try:
        if HAS_MAKE_VALID:
            geom = geom.apply(lambda g: make_valid(g) if g is not None else None)
        else:

            def _fix(g):
                if g is None:
                    return None
                # buffer(0) seulement pour Polygons
                if getattr(g, "geom_type", "").endswith("Polygon"):
                    try:
                        return g.buffer(0)
                    except Exception:
                        return g
                return g

            geom = geom.apply(_fix)
    except Exception:
        pass
    # drop NA et invalid
    try:
        mask_valid = geom.notna()
        try:
            mask_valid = mask_valid & geom.is_valid
        except Exception:
            pass
        out = out[mask_valid].copy()
        out.set_geometry(geom[mask_valid], inplace=True)
    except Exception:
        out = out[out.geometry.notna()].copy()
    return out


def _safe_union_buffer(streets: gpd.GeoSeries | gpd.GeoDataFrame, street_buffer_m: float, debug: bool = False):
    """Construit de manière robuste une zone tampon autour des géométries de la rue.
    Stratégie *buffer-then-union* (on tamponne d'abord chaque géométrie en 3857,
    puis on dissout), ce qui évite plusieurs plantages GEOS observés lors d'union
    préalable sur des segments cassés/multiples.
    Retourne une unique géométrie (MultiPolygon/Polygon) en EPSG:3857.
    """
    # Normalise entrée → GeoSeries 4326
    if isinstance(streets, gpd.GeoDataFrame):
        geoms = streets.geometry
        src_crs = streets.crs or 4326
    else:
        # streets peut être une Series pandas simple ; on force GeoSeries + CRS
        src_crs = getattr(streets, "crs", 4326) or 4326
        geoms = gpd.GeoSeries(streets, crs=src_crs)

    # Nettoyage des géométries problématiques
    gdf = gpd.GeoDataFrame(geometry=geoms, crs=src_crs)
    gdf = _clean_geoms(gdf)
    if len(gdf) == 0:
        return gpd.GeoSeries([], crs=3857).unary_union

    try:
        # 1) reprojection en 3857
        g3857 = gdf.to_crs(3857)
        # 2) buffer individuel (évite les unions de lignes avant tampon)
        buf = g3857.buffer(float(street_buffer_m))
        # 3) dissolution du buffer
        try:
            merged = buf.union_all()
        except Exception:
            merged = buf.unary_union
        return merged
    except Exception as e:
        if debug:
            try:
                import typer

                typer.echo(f"[DEBUG] _safe_union_buffer fallback (buffer-then-union failed): {e!r}")
            except Exception:
                pass
        # Repli: bbox des géométries → buffer
        xmin_b, ymin_b, xmax_b, ymax_b = gdf.to_crs(4326).total_bounds
        return gpd.GeoSeries([box(xmin_b, ymin_b, xmax_b, ymax_b)], crs=4326).to_crs(3857).buffer(float(street_buffer_m)).unary_union


def _guess_name_column(df: pd.DataFrame) -> Optional[str]:
    """Devine la colonne contenant le nom de voie ("name"/"nom").
    Retourne None si introuvable.
    """
    # candidats évidents
    for c in df.columns:
        lc = c.lower()
        if lc in ("name", "nom", "nom_voie", "road_name"):
            return c
    # fallback: contient "name" ou "nom"
    for c in df.columns:
        lc = c.lower()
        if "name" in lc or "nom" in lc:
            return c
    return None


def _filter_by_street(df: pd.DataFrame, street: Optional[str]) -> pd.DataFrame:
    """Filtre un DataFrame/GeoDataFrame par nom de voie (contient, insensible à la casse).
    Si aucune colonne de nom n'est trouvée, retourne un DF vide si `street` est fourni, sinon `df`.
    """
    if not street:
        return df
    col = _guess_name_column(df)
    if col is None:
        # pas de nom → on ne peut pas filtrer, mais on n'invente pas
        return df.iloc[0:0].copy()
    s = df[col].astype(str).str.casefold()
    needle = street.casefold()
    return df[s.str.contains(needle, na=False)].copy()


def _to_3857_bbox(bbox4326: Tuple[float, float, float, float]) -> Tuple[float, float, float, float]:
    """Transforme une bbox WGS84 -> WebMercator (EPSG:3857) pour filtrer
    rapidement les centroids dans les Parquet.
    """
    if not HAS_PYPROJ:
        # fallback grossier: on retourne la bbox 4326 telle quelle (filtrage moins précis)
        return bbox4326
    xmin, ymin, xmax, ymax = bbox4326
    tx = Transformer.from_crs(4326, 3857, always_xy=True)
    x0, y0 = tx.transform(xmin, ymin)
    x1, y1 = tx.transform(xmax, ymax)
    xmin_m, xmax_m = (min(x0, x1), max(x0, x1))
    ymin_m, ymax_m = (min(y0, y1), max(y0, y1))
    return xmin_m, ymin_m, xmax_m, ymax_m


# --- Helper pour deviner le CRS des centroids dans les Parquet de segments
def _guess_seg_crs(df: pd.DataFrame) -> int:
    """Heuristique pour deviner le CRS des colonnes x_centroid/y_centroid dans les Parquet de segments.
    Retourne EPSG (int). Par défaut 3857 si doute.
    """
    # Si les colonnes n'existent pas, on garde 3857 par défaut
    if not {"x_centroid", "y_centroid"}.issubset(df.columns):
        return 3857
    x = pd.to_numeric(df["x_centroid"], errors="coerce")
    y = pd.to_numeric(df["y_centroid"], errors="coerce")
    # Lambert-93 (EPSG:2154): X ~ [0, 1.2e6], Y ~ [6e6, 7.3e6]
    if x.between(0, 1_200_000, inclusive="both").mean() > 0.95 and y.between(6_000_000, 7_300_000, inclusive="both").mean() > 0.95:
        return 2154
    # WebMercator (EPSG:3857): X ~ [-2e7, 2e7], Y ~ [-2e7, 2e7] et typiquement |Y| <= ~2.0e7
    if x.between(-20_100_000, 20_100_000, inclusive="both").mean() > 0.95 and y.between(-20_100_000, 20_100_000, inclusive="both").mean() > 0.95:
        return 3857
    # WGS84 degrés (EPSG:4326): X entre -180 et 180, Y entre -90 et 90
    if x.between(-180, 180, inclusive="both").mean() > 0.95 and y.between(-90, 90, inclusive="both").mean() > 0.95:
        return 4326
    # fallback
    return 3857


def _read_geom(path: str, bbox4326: Tuple[float, float, float, float]) -> gpd.GeoDataFrame:
    """Lit rapidement un fichier géo avec un filtrage bbox (WGS84).
    ⚠️ Avec pyogrio, la bbox doit être dans le même CRS que la donnée :
    on lit d'abord le CRS natif puis on transforme la bbox 4326 -> CRS natif.
    Ensuite, on reprojette en 4326 et on re-clippe.
    """
    src_crs = None
    # 1) déterminer le CRS natif sans tout charger
    if HAS_PYOGRIO:
        try:
            info = pyogrio.read_info(path)  # type: ignore[attr-defined]
            src_crs = info.get("crs") if isinstance(info, dict) else getattr(info, "crs", None)
        except Exception:
            src_crs = None

    # 2) préparer la bbox dans le CRS natif si possible
    bbox_native = bbox4326
    if src_crs is not None and HAS_PYPROJ:
        try:
            tx = Transformer.from_crs(4326, src_crs, always_xy=True)  # type: ignore[name-defined]
            xmin, ymin, xmax, ymax = bbox4326
            x0, y0 = tx.transform(xmin, ymin)
            x1, y1 = tx.transform(xmax, ymax)
            bbox_native = (min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))
        except Exception:
            bbox_native = bbox4326

    # 3) lecture
    if HAS_PYOGRIO:
        try:
            gdf = pyogrio.read_dataframe(path, bbox=bbox_native)  # type: ignore[attr-defined]
        except Exception:
            # fallback sans bbox puis découpe après coup
            gdf = gpd.read_file(path)
    else:
        # fiona attend aussi la bbox dans le CRS natif ; si on ne sait pas le CRS, lisons tout puis clippons
        try:
            if src_crs is not None and HAS_PYPROJ:
                gdf = gpd.read_file(path, bbox=bbox_native)
            else:
                gdf = gpd.read_file(path)
        except Exception:
            gdf = gpd.read_file(path)

    # 4) définir le CRS si manquant, reprojeter en 4326
    try:
        if gdf.crs is None:
            if src_crs is not None:
                gdf = gdf.set_crs(src_crs, allow_override=True)
            else:
                # hypothèse France métropolitaine si inconnu
                gdf = gdf.set_crs(2154, allow_override=True)
        gdf = gdf.to_crs(4326)
    except Exception:
        # dernier recours : forcer 2154 puis 4326
        gdf = gdf.set_crs(2154, allow_override=True).to_crs(4326)

    # 5) nettoyage + clip final avec la bbox WGS84 d'origine
    gdf = gdf[gdf.geometry.notna()].copy()
    try:
        bbox_poly = gpd.GeoSeries([box(*bbox4326)], crs=4326)
        gdf = gdf[gdf.intersects(bbox_poly.iloc[0])].copy()
    except Exception:
        pass
    return gdf


def _read_segments_centroids(parquet_path: str, bbox4326: Tuple[float, float, float, float], classes: Optional[Iterable[str]] = None, street: Optional[str] = None) -> gpd.GeoDataFrame:
    """Lit le parquet 'segments' (sans géométrie) de façon économe:
    - ne charge que quelques colonnes
    - filtre par bbox en CRS natif des centroids (deviné automatiquement)
    - filtre optionnellement par classes
    """
    # On lit d'abord au minimum pour récupérer les colonnes et deviner le CRS
    base = pd.read_parquet(parquet_path, columns=["x_centroid", "y_centroid"])  # lève si absent
    use_cols = [c for c in SEG_COLUMNS if c in base.columns or c in SEG_COLUMNS]
    for base_col in ("x_centroid", "y_centroid"):
        if base_col not in use_cols:
            use_cols.append(base_col)

    df = pd.read_parquet(parquet_path, columns=list(dict.fromkeys(use_cols)))

    # filtre par rue si possible (prioritaire sur classes)
    if street:
        name_col = _guess_name_column(df)
        if name_col is not None:
            s = df[name_col].astype(str).str.casefold()
            df = df[s.str.contains(street.casefold(), na=False)].copy()

    if not {"x_centroid", "y_centroid"}.issubset(df.columns):
        raise ValueError(f"Colonnes x_centroid/y_centroid manquantes dans {parquet_path}")

    # Devine le CRS natif des centroids
    crs_epsg = _guess_seg_crs(df)

    # Transforme la bbox 4326 -> crs_epsg pour un filtrage rapide
    if HAS_PYPROJ and crs_epsg in (2154, 3857):
        tx = Transformer.from_crs(4326, crs_epsg, always_xy=True)
        xmin, ymin, xmax, ymax = bbox4326
        x0, y0 = tx.transform(xmin, ymin)
        x1, y1 = tx.transform(xmax, ymax)
        xmin_n, xmax_n = (min(x0, x1), max(x0, x1))
        ymin_n, ymax_n = (min(y0, y1), max(y0, y1))
    else:
        # si on ne sait pas transformer, on ne pré-filtre pas par bbox en coordonnées natives
        xmin_n = df["x_centroid"].min()
        xmax_n = df["x_centroid"].max()
        ymin_n = df["y_centroid"].min()
        ymax_n = df["y_centroid"].max()

    # Filtrage grossier par bbox
    df = df[(df["x_centroid"] >= xmin_n) & (df["x_centroid"] <= xmax_n) & (df["y_centroid"] >= ymin_n) & (df["y_centroid"] <= ymax_n)].copy()

    # Filtre éventuel par classes
    if classes is not None and "class" in df.columns:
        df = df[df["class"].isin(classes)].copy()

    # Construction géométrie dans le CRS natif puis reprojection en WGS84
    geom = [Point(x, y) if pd.notna(x) and pd.notna(y) else None for x, y in zip(df["x_centroid"], df["y_centroid"])]
    gdf = gpd.GeoDataFrame(df, geometry=geom, crs=crs_epsg)
    gdf = gdf[gdf.geometry.notna()].to_crs(4326)
    return gdf


def _derive_radius(series_df: pd.DataFrame) -> pd.Series:
    """Retourne un rayon estimé propre (mètres), en privilégiant radius_min_m puis p85,
    sinon 1/curv_mean_1perm. Nettoie les valeurs infinies/sentinelles et
    ignore les segments rectilignes (is_straight == True).
    """
    # priorité: min → p85 → 1/curv
    if "radius_min_m" in series_df.columns:
        r = pd.to_numeric(series_df["radius_min_m"], errors="coerce")
    elif "radius_p85_m" in series_df.columns:
        r = pd.to_numeric(series_df["radius_p85_m"], errors="coerce")
    elif "curv_mean_1perm" in series_df.columns:
        k = pd.to_numeric(series_df["curv_mean_1perm"], errors="coerce")
        r = 1.0 / k.replace(0, pd.NA)
    else:
        r = pd.Series([pd.NA] * len(series_df), index=series_df.index, dtype="float64")

    # nettoyage: inf/neg/sentinelles gigantesques (ex: ~9.378e7) → NA
    r = pd.to_numeric(r, errors="coerce")
    r = r.mask(~np.isfinite(r), pd.NA)
    r = r.mask(r <= 0, pd.NA)
    r = r.mask(r > 1_000_000, pd.NA)  # cap: > 1000 km = NA

    # si flag is_straight disponible → NA
    if "is_straight" in series_df.columns:
        try:
            r = r.mask(series_df["is_straight"] is True, pd.NA)
        except Exception:
            pass
    return r


def _metrics_block(name: str, df: pd.DataFrame, clotho_pts: Optional[gpd.GeoDataFrame] = None, clotho_step_m: Optional[float] = None) -> pd.Series:
    """
    Calcule un bloc de métriques enrichies pour un ensemble de points (avec 'radius_guess').
    - Compte de points totaux et valides
    - Statistiques robustes sur les rayons (min/p10/med/p90/max)
    - Part de segments quasi droits (>1000 m)
    - Dispersion sur log10(R)
    - Indicateurs clothoïdes (nb points, longueur estimée, ratio sur le nombre de points)
    """
    r = pd.to_numeric(df.get("radius_guess", pd.Series(dtype="float64")), errors="coerce")
    r = r.mask(~np.isfinite(r), pd.NA)
    valid = r.dropna()

    # Stats de rayon
    def _q(s, q):
        try:
            return float(s.quantile(q))
        except Exception:
            return float("nan")

    stats = {
        "features": int(len(df)),
        "valid_count": int(len(valid)),
        "rayon_min(m)": float(valid.min()) if len(valid) else float("nan"),
        "rayon_p10(m)": _q(valid, 0.10) if len(valid) else float("nan"),
        "rayon_med(m)": float(valid.median(skipna=True)) if len(valid) else float("nan"),
        "rayon_p90(m)": _q(valid, 0.90) if len(valid) else float("nan"),
        "rayon_max(m)": float(valid.max()) if len(valid) else float("nan"),
        "pct_>1000m": float((valid.gt(1000).mean() * 100.0)) if len(valid) else float("nan"),
    }

    # Dispersion en log10(R)
    try:
        logr = np.log10(valid.astype(float))
        stats["sigma_log10R"] = float(np.nanstd(logr))
    except Exception:
        stats["sigma_log10R"] = float("nan")

    # Clothoïdes
    n_clo = int(len(clotho_pts)) if clotho_pts is not None else 0
    stats["clothoid_pts"] = float(n_clo)
    if clotho_step_m is not None and np.isfinite(clotho_step_m):
        stats["clothoid_len_est(m)"] = float(n_clo) * float(clotho_step_m)
    else:
        stats["clothoid_len_est(m)"] = float("nan")
    stats["clothoid_pts_pct"] = (float(n_clo) / float(len(df)) * 100.0) if len(df) else 0.0

    return pd.Series(stats, name=name)


# === Rayon géométrique local (option A) depuis les géométries OSM visibles ===
def _circumradius(p0, p1, p2):
    """
    Rayon du cercle circonscrit aux 3 points (en mètres dans le CRS projeté).
    Retourne np.nan si les points sont quasi colinéaires.
    """
    x1, y1 = p0
    x2, y2 = p1
    x3, y3 = p2
    # Formule basée sur l'aire du triangle
    a = np.hypot(x2 - x1, y2 - y1)
    b = np.hypot(x3 - x2, y3 - y2)
    c = np.hypot(x1 - x3, y1 - y3)
    s = (a + b + c) / 2.0
    area_sq = max(s * (s - a) * (s - b) * (s - c), 0.0)
    if area_sq <= 0:
        return np.nan
    area = np.sqrt(area_sq)
    # Rayon R = (a*b*c) / (4 * Aire)
    R = (a * b * c) / (4.0 * area) if area > 0 else np.nan
    # Filtre valeurs aberrantes
    if not np.isfinite(R) or R <= 0 or R > 1_000_000:
        return np.nan
    return R


def _densify_line_to_points(line, step_m):
    """
    Echantillonne une LineString en points espacés d'environ step_m (en mètres, CRS projeté).
    Retourne une liste de tuples (x, y).
    """
    try:
        length = line.length
    except Exception:
        return []
    if not np.isfinite(length) or length <= 0:
        return []
    n = max(int(np.ceil(length / float(step_m))), 1)
    # On veut des points réguliers le long de la ligne (incl. extrémités)
    dists = np.linspace(0, length, num=n + 1)
    pts = []
    for d in dists:
        try:
            pt = line.interpolate(d)
            pts.append((pt.x, pt.y))
        except Exception:
            continue
    return pts


def _radii_from_lines(lines_gdf: gpd.GeoDataFrame, step_m: float = 15.0, max_points: int = 5000) -> gpd.GeoDataFrame:
    """
    Calcule des rayons locaux à partir de géométries linéaires :
    - reprojette en EPSG:3857
    - densifie chaque ligne en points tous les 'step_m'
    - applique une fenêtre glissante de 3 points pour estimer le rayon (cercle osculateur approché)

    Retourne un GeoDataFrame de points (EPSG:4326) avec colonne 'radius_guess' (m).
    On limite le nombre total de points pour éviter les figures trop lourdes.
    """
    if lines_gdf is None or len(lines_gdf) == 0:
        return gpd.GeoDataFrame(columns=["radius_guess", "geometry"], geometry="geometry", crs=4326)
    try:
        g3857 = _clean_geoms(lines_gdf).to_crs(3857)
    except Exception:
        g3857 = lines_gdf.copy()
        if g3857.crs is None:
            g3857 = g3857.set_crs(4326, allow_override=True)
        g3857 = g3857.to_crs(3857)

    radii = []
    geoms = []
    total_pts = 0
    for geom in g3857.geometry:
        if geom is None:
            continue
        try:
            # Gérer MultiLineString en itérant sur les parties
            parts = list(geom.geoms) if getattr(geom, "geom_type", "") == "MultiLineString" else [geom]
        except Exception:
            parts = [geom]
        for part in parts:
            pts = _densify_line_to_points(part, step_m)
            # fenêtre glissante de taille 3
            for i in range(1, max(len(pts) - 1, 0)):
                p0, p1, p2 = pts[i - 1], pts[i], pts[i + 1]
                R = _circumradius(p0, p1, p2)
                if not np.isnan(R):
                    radii.append(R)
                    geoms.append(Point(p1[0], p1[1]))
                    total_pts += 1
                    if total_pts >= max_points:
                        break
            if total_pts >= max_points:
                break
        if total_pts >= max_points:
            break

    if len(geoms) == 0:
        return gpd.GeoDataFrame(columns=["radius_guess", "geometry"], geometry="geometry", crs=4326)

    gpts = gpd.GeoDataFrame({"radius_guess": radii}, geometry=gpd.GeoSeries(geoms, crs=3857))
    try:
        gpts = gpts.to_crs(4326)
    except Exception:
        pass
    return gpts


# === Clothoïde: k(s) ≈ a*s + b (option légère, locale) ===


def _curvature_profile_from_line(line, step_m: float = 12.0):
    """
    Depuis une LineString en EPSG:3857, renvoie (s_mid, k_mid, pts_mid) où :
    - s_mid: abscisses curvilignes (m) au milieu des triplets
    - k_mid: courbure locale 1/R (1/m)
    - pts_mid: points shapely (EPSG:3857) correspondants
    """
    pts = _densify_line_to_points(line, step_m)
    if len(pts) < 3:
        return np.array([]), np.array([]), []
    # abscisse cumulée
    dists = [0.0]
    for i in range(1, len(pts)):
        dists.append(dists[-1] + float(np.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1])))
    dists = np.array(dists)
    s_mid, k_mid, pts_mid = [], [], []
    for i in range(1, len(pts) - 1):
        p0, p1, p2 = pts[i - 1], pts[i], pts[i + 1]
        R = _circumradius(p0, p1, p2)
        if np.isnan(R) or R <= 0:
            continue
        k = 1.0 / float(R)
        s = 0.5 * (dists[i - 1] + dists[i + 1])
        s_mid.append(s)
        k_mid.append(k)
        pts_mid.append(Point(p1[0], p1[1]))
    if len(s_mid) == 0:
        return np.array([]), np.array([]), []
    return np.array(s_mid), np.array(k_mid), pts_mid


def _fit_windows_ks(s_mid: np.ndarray, k_mid: np.ndarray, window_m: float, step_m: float, r2_min: float = 0.85):
    """
    Ajuste k(s) ≈ a*s + b par régression linéaire dans des fenêtres glissantes de taille ~window_m.
    Retourne des index centraux conservés et les paramètres a,b,r2 pour ces index.
    """
    if len(s_mid) == 0:
        return [], [], [], []
    win_pts = max(int(round(window_m / step_m)), 3)
    win_pts = int(np.clip(win_pts, 3, 999999))
    keep_idx, a_list, b_list, r2_list = [], [], [], []
    for i in range(win_pts // 2, len(s_mid) - win_pts // 2):
        lo = i - win_pts // 2
        hi = i + win_pts // 2 + 1
        x = s_mid[lo:hi]
        y = k_mid[lo:hi]
        if len(x) < 3:
            continue
        # régression linéaire simple
        A = np.vstack([x, np.ones_like(x)]).T
        try:
            coeff, *_ = np.linalg.lstsq(A, y, rcond=None)
            a, b = float(coeff[0]), float(coeff[1])
            y_hat = a * x + b
            ss_res = float(np.sum((y - y_hat) ** 2))
            ss_tot = float(np.sum((y - np.mean(y)) ** 2))
            r2 = 1.0 - ss_res / max(ss_tot, 1e-12)
        except Exception:
            continue
        if np.isfinite(r2) and r2 >= r2_min:
            keep_idx.append(i)
            a_list.append(a)
            b_list.append(b)
            r2_list.append(r2)
    return keep_idx, a_list, b_list, r2_list


def _clothoid_points_from_lines(lines_gdf: gpd.GeoDataFrame, step_m: float = 12.0, window_m: float = 120.0, r2_min: float = 0.85, max_points: int = 3000) -> gpd.GeoDataFrame:
    """
    Détecte des portions localement clothoïdales sur des lignes:
    - reprojette en 3857
    - calcule k(s) par triplets
    - garde les centres de fenêtres où R² de la régression linéaire k(s) est élevé
    Retourne un GeoDataFrame de points (EPSG:4326) avec colonnes ['a','b','r2'].
    """
    if lines_gdf is None or len(lines_gdf) == 0:
        return gpd.GeoDataFrame(columns=["a", "b", "r2", "geometry"], geometry="geometry", crs=4326)
    try:
        g3857 = _clean_geoms(lines_gdf).to_crs(3857)
    except Exception:
        g3857 = lines_gdf.copy()
        if g3857.crs is None:
            g3857 = g3857.set_crs(4326, allow_override=True)
        g3857 = g3857.to_crs(3857)
    geoms = []
    a_vals, b_vals, r2_vals = [], [], []
    total = 0
    for geom in g3857.geometry:
        try:
            parts = list(geom.geoms) if getattr(geom, "geom_type", "") == "MultiLineString" else [geom]
        except Exception:
            parts = [geom]
        for part in parts:
            s_mid, k_mid, pts_mid = _curvature_profile_from_line(part, step_m=step_m)
            if len(s_mid) == 0:
                continue
            idx, a_list, b_list, r2_list = _fit_windows_ks(s_mid, k_mid, window_m=window_m, step_m=step_m, r2_min=r2_min)
            for j in range(len(idx)):
                geoms.append(pts_mid[idx[j]])
                a_vals.append(a_list[j])
                b_vals.append(b_list[j])
                r2_vals.append(r2_list[j])
                total += 1
                if total >= max_points:
                    break
            if total >= max_points:
                break
        if total >= max_points:
            break
    if len(geoms) == 0:
        return gpd.GeoDataFrame(columns=["a", "b", "r2", "geometry"], geometry="geometry", crs=4326)
    out = gpd.GeoDataFrame({"a": a_vals, "b": b_vals, "r2": r2_vals}, geometry=gpd.GeoSeries(geoms, crs=3857))
    try:
        out = out.to_crs(4326)
    except Exception:
        pass
    return out


@app.command()
def romilly(
    out_dir: str = typer.Option("out/plots/romilly", help="Dossier de sortie"),
    bbox: tuple[float, float, float, float] = typer.Option(ROMILLY_BBOX, help="BBOX WGS84 xmin,ymin,xmax,ymax"),
    osm_geom: str = typer.Option(DEFAULT_OSM_GEOM, help="Géométries OSM (GeoJSON/GeoPackage)"),
    ign_geom: str = typer.Option(DEFAULT_IGN_GEOM, help="Géométries IGN BD TOPO (GPKG/FGDB/…)"),
    osm_seg: str = typer.Option(DEFAULT_OSM_SEG, help="Segments OSM (parquet – centroids seulement)"),
    ign_seg: str = typer.Option(DEFAULT_IGN_SEG, help="Segments IGN (parquet – centroids seulement)"),
    classes: Optional[str] = typer.Option(None, help="Filtrer par classes (séparées par des virgules), ex: 'primary,secondary'"),
    max_plotted: Optional[int] = typer.Option(5000, help="Limiter le nombre de géométries tracées par couche pour accélérer le rendu (None pour tout tracer)"),
    street: Optional[str] = typer.Option(None, help="Filtrer par nom de voie (ex: 'Rue Blingue'). Ignore --classes si fourni."),
    debug: bool = typer.Option(False, help="Logs de debug (colonnes de noms détectées, comptages, etc.)"),
    street_buffer_m: float = typer.Option(60.0, help="Rayon (m) du buffer autour de la rue pour capter/afficher géométries & segments"),
    plot_centroids: bool = typer.Option(False, help="Affiche aussi les centroids des segments OSM/IGN (points)."),
    geom_radius_step_m: float = typer.Option(15.0, help="Pas d'échantillonnage (m) pour le calcul local du rayon depuis les géométries (option A)"),
    max_geom_centroids: int = typer.Option(4000, help="Nombre max de points (centroïdes géométriques) à générer pour l'option A"),
    force_geom_radius_osm: bool = typer.Option(
        False,
        help="Forcer le calcul géométrique des rayons pour OSM (option A), même si des rayons existent dans les segments.",
    ),
    force_geom_radius_ign: bool = typer.Option(
        False,
        help="Forcer le calcul géométrique des rayons pour IGN (option A), même si des rayons existent dans les segments.",
    ),
    fit_clothoid: bool = typer.Option(
        False,
        "--fit-clothoid",
        "--clothoid",
        "-C",
        help="Activer la détection locale de clothoïdes (k(s)≈a*s+b).",
    ),
    clothoid_step_m: float = typer.Option(
        12.0,
        "--clothoid-step-m",
        help="Pas d'échantillonnage (m) pour k(s).",
        min=0.1,
    ),
    clothoid_window_m: float = typer.Option(
        120.0,
        "--clothoid-window-m",
        help="Taille de fenêtre (m) pour la régression linéaire.",
        min=1.0,
    ),
    clothoid_r2_min: float = typer.Option(
        0.85,
        "--clothoid-r2-min",
        help="Seuil R² minimal pour accepter une portion clothoïdale.",
        min=0.0,
        max=1.0,
    ),
):
    os.makedirs(out_dir, exist_ok=True)
    xmin, ymin, xmax, ymax = bbox

    # 1) lire géométries + filtre bbox (via driver/bbox)
    g_osm = _read_geom(osm_geom, bbox)
    g_ign = _read_geom(ign_geom, bbox)
    # Préserver les couches originales pour clipping ultérieur
    g_osm_all = g_osm.copy()
    g_ign_all = g_ign.copy()
    if debug:
        typer.echo(f"[DEBUG] post-read geom → OSM_all={len(g_osm_all)} IGN_all={len(g_ign_all)}")

    if debug:
        typer.echo(f"[DEBUG] OSM cols nom: {_guess_name_columns(g_osm)} ; IGN cols nom: {_guess_name_columns(g_ign)}")

    classes_list = [c.strip() for c in classes.split(",")] if classes else None
    if street:
        classes_list = None  # le filtre rue l'emporte
        # filtre par nom "intelligent"
        g_osm_sel = _filter_by_street_name(g_osm, street)
        g_ign_sel = _filter_by_street_name(g_ign, street)
        # fallback spatial si besoin (chevauchement)
        if g_osm_sel.empty and not g_ign_sel.empty:
            g_osm_sel = _fallback_overlap(g_ign_sel, g_osm)
        if g_ign_sel.empty and not g_osm_sel.empty:
            g_ign_sel = _fallback_overlap(g_osm_sel, g_ign)
        g_osm, g_ign = g_osm_sel, g_ign_sel
        if debug:
            typer.echo(f"[DEBUG] Après filtre rue → OSM={len(g_osm)} IGN={len(g_ign)} (avec fallback spatial si nécessaire)")
        # recadrer la bbox autour de l'emprise trouvée
        if not g_osm.empty or not g_ign.empty:
            bounds = []
            if not g_osm.empty:
                bounds.append(g_osm.total_bounds)
            if not g_ign.empty:
                bounds.append(g_ign.total_bounds)
            if bounds:
                pd.DataFrame(bounds).agg(["min", "max"], axis=0)
                xmin_b, ymin_b, xmax_b, ymax_b = (
                    float(min(bb[0] for bb in bounds)),
                    float(min(bb[1] for bb in bounds)),
                    float(max(bb[2] for bb in bounds)),
                    float(max(bb[3] for bb in bounds)),
                )
                pad = 0.001
                xmin, ymin, xmax, ymax = xmin_b - pad, ymin_b - pad, xmax_b + pad, ymax_b + pad
    else:
        # filtre éventuel par classes si champ présent
        if classes_list is not None and "class" in g_osm.columns:
            g_osm = g_osm[g_osm["class"].isin(classes_list)].copy()
        if classes_list is not None and "class" in g_ign.columns:
            g_ign = g_ign[g_ign["class"].isin(classes_list)].copy()

    # downsampling optionnel pour la figure
    if max_plotted is not None and len(g_osm) > max_plotted:
        g_osm = g_osm.sample(max_plotted, random_state=42).copy()
    if max_plotted is not None and len(g_ign) > max_plotted:
        g_ign = g_ign.sample(max_plotted, random_state=42).copy()

    # 2) lire segments (centroids) → filtre bbox/spatial → rayon
    if street and (len(g_osm) or len(g_ign)):
        # Construit une GeoSeries 4326 des géométries sélectionnées (OSM+IGN)
        if len(g_osm) or len(g_ign):
            parts = []
            if len(g_osm):
                parts.append(g_osm.geometry)
            if len(g_ign):
                parts.append(g_ign.geometry)
            streets = gpd.GeoSeries(pd.concat(parts, ignore_index=True), crs=4326)
        else:
            streets = None

        if streets is not None and len(streets) > 0:
            if debug:
                try:
                    typer.echo(f"[DEBUG] building buffer over {len(streets)} street geoms (r={street_buffer_m}m)")
                except Exception:
                    pass
            area3857 = _safe_union_buffer(streets, street_buffer_m, debug)
            # lire par bbox (rapide) puis filtrer finement par inclusion dans le buffer
            s_osm = _read_segments_centroids(osm_seg, (xmin, ymin, xmax, ymax), None, street=None).to_crs(3857)
            s_ign = _read_segments_centroids(ign_seg, (xmin, ymin, xmax, ymax), None, street=None).to_crs(3857)
            s_osm = s_osm[s_osm.geometry.within(area3857)].to_crs(4326).copy()
            s_ign = s_ign[s_ign.geometry.within(area3857)].to_crs(4326).copy()

            # IMPORTANT: pour l'affichage, on clippe les couches complètes, pas les filtres par nom
            def _clip_to_buf(df):
                if df is None or len(df) == 0:
                    return df
                df3857 = df.to_crs(3857)
                clipped = df3857[df3857.intersects(area3857)].copy()
                return clipped.to_crs(4326)

            g_osm_draw = _clip_to_buf(g_osm_all)
            g_ign_draw = _clip_to_buf(g_ign_all)
            # Fallback d'affichage: si aucune géométrie IGN (ou OSM) n'a été clippée mais que des centroids existent,
            # on construit une zone à partir des centroids et on re-clippe la couche complète.
            if (g_ign_draw is None or len(g_ign_draw) == 0) and len(s_ign) > 0:
                area_from_pts_ign = s_ign.to_crs(3857).buffer(street_buffer_m).unary_union
                gi3857 = _clean_geoms(g_ign_all).to_crs(3857)
                g_ign_draw = gi3857[gi3857.intersects(area_from_pts_ign)].copy().to_crs(4326)
            if (g_osm_draw is None or len(g_osm_draw) == 0) and len(s_osm) > 0:
                area_from_pts_osm = s_osm.to_crs(3857).buffer(street_buffer_m).unary_union
                go3857 = _clean_geoms(g_osm_all).to_crs(3857)
                g_osm_draw = go3857[go3857.intersects(area_from_pts_osm)].copy().to_crs(4326)
        else:
            s_osm = _read_segments_centroids(osm_seg, bbox, None, street=None)
            s_ign = _read_segments_centroids(ign_seg, bbox, None, street=None)
            g_osm_draw = None
            g_ign_draw = None
    else:
        g_osm_draw = None
        g_ign_draw = None
        classes_list = [c.strip() for c in classes.split(",")] if classes else None
        s_osm = _read_segments_centroids(osm_seg, bbox, classes_list, street=street)
        s_ign = _read_segments_centroids(ign_seg, bbox, classes_list, street=street)

    s_osm["radius_guess"] = _derive_radius(s_osm)
    s_ign["radius_guess"] = _derive_radius(s_ign)

    # --- Fallback/force: calcul géométrique local des rayons depuis les lignes ---
    # Détermine les couches à afficher (déjà nettoyées plus haut)
    _ign_plot = g_ign_draw if street else g_ign
    _osm_plot = g_osm_draw if street else g_osm

    # OSM: forcer ou fallback si pas de valeurs exploitables
    try:
        need_geom_osm = force_geom_radius_osm or (len(s_osm) == 0) or (pd.isna(s_osm["radius_guess"]).all())
    except Exception:
        need_geom_osm = True
    if need_geom_osm:
        osm_lines_for_radius = _osm_plot if (_osm_plot is not None and len(_osm_plot)) else g_osm_draw
        if osm_lines_for_radius is None or len(osm_lines_for_radius) == 0:
            osm_lines_for_radius = g_osm
        if osm_lines_for_radius is not None and len(osm_lines_for_radius) > 0:
            if debug:
                typer.echo(f"[DEBUG] OSM → calcul géométrique local (step={geom_radius_step_m} m, max_pts={max_geom_centroids}) [force={force_geom_radius_osm}]")
            s_osm = _radii_from_lines(osm_lines_for_radius, step_m=float(geom_radius_step_m), max_points=int(max_geom_centroids))
            s_osm["source"] = "osm"
        elif debug:
            typer.echo("[DEBUG] OSM → pas de géométrie de ligne disponible pour le calcul local.")

    # IGN: forcer ou fallback si pas de valeurs exploitables
    try:
        need_geom_ign = force_geom_radius_ign or (len(s_ign) == 0) or (pd.isna(s_ign["radius_guess"]).all())
    except Exception:
        need_geom_ign = True
    if need_geom_ign:
        ign_lines_for_radius = _ign_plot if (_ign_plot is not None and len(_ign_plot)) else g_ign_draw
        if ign_lines_for_radius is None or len(ign_lines_for_radius) == 0:
            ign_lines_for_radius = g_ign
        if ign_lines_for_radius is not None and len(ign_lines_for_radius) > 0:
            if debug:
                typer.echo(f"[DEBUG] IGN → calcul géométrique local (step={geom_radius_step_m} m, max_pts={max_geom_centroids}) [force={force_geom_radius_ign}]")
            s_ign = _radii_from_lines(ign_lines_for_radius, step_m=float(geom_radius_step_m), max_points=int(max_geom_centroids))
            s_ign["source"] = "ign"
        elif debug:
            typer.echo("[DEBUG] IGN → pas de géométrie de ligne disponible pour le calcul local.")

    # 3) figure
    ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    fig, ax = plt.subplots(figsize=(8, 8))
    # fenêtre bbox
    gpd.GeoSeries([box(xmin, ymin, xmax, ymax)], crs=4326).boundary.plot(ax=ax, linewidth=1, linestyle="--")

    # Tracé
    # _ign_plot/_osm_plot déjà définis plus haut pour les calculs de rayon
    _ign_plot = _clean_geoms(_ign_plot) if (_ign_plot is not None and len(_ign_plot)) else _ign_plot
    _osm_plot = _clean_geoms(_osm_plot) if (_osm_plot is not None and len(_osm_plot)) else _osm_plot
    if _ign_plot is not None and len(_ign_plot):
        _ign_plot.plot(ax=ax, linewidth=1.6, alpha=0.95, color="C0", zorder=2)
    if _osm_plot is not None and len(_osm_plot):
        _osm_plot.plot(ax=ax, linewidth=1.2, alpha=0.85, color="C1", zorder=3)

    # Optionnel: afficher les centroids des segments
    if plot_centroids:
        try:
            if len(s_ign) > 0:
                s_ign.plot(ax=ax, markersize=6, alpha=0.7, color="C0", zorder=4)
            if len(s_osm) > 0:
                s_osm.plot(ax=ax, markersize=6, alpha=0.7, color="C1", zorder=5)
        except Exception:
            pass
        # Optionnel : annoter les tailles/type de points

    # --- Clothoïdes locales (optionnel) ---
    clotho_osm = gpd.GeoDataFrame()
    clotho_ign = gpd.GeoDataFrame()
    if fit_clothoid:
        if _osm_plot is not None and len(_osm_plot):
            clotho_osm = _clothoid_points_from_lines(_osm_plot, step_m=float(clothoid_step_m), window_m=float(clothoid_window_m), r2_min=float(clothoid_r2_min), max_points=3000)
            if len(clotho_osm):
                clotho_osm.plot(ax=ax, markersize=10, marker="x", alpha=0.9, color="C3", zorder=6)
        if _ign_plot is not None and len(_ign_plot):
            clotho_ign = _clothoid_points_from_lines(_ign_plot, step_m=float(clothoid_step_m), window_m=float(clothoid_window_m), r2_min=float(clothoid_r2_min), max_points=3000)
            if len(clotho_ign):
                clotho_ign.plot(ax=ax, markersize=10, marker="+", alpha=0.9, color="C0", zorder=6)

    ax.set_xlim([xmin, xmax])
    ax.set_ylim([ymin, ymax])

    title = "Romilly-sur-Andelle — comparaison des tracés (OSM vs IGN)"
    if street:
        title += f" — {street}"
    ax.set_title(title)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")

    # Légende via proxys pour éviter l'avertissement PatchCollection
    handles = []
    plotted_ign = _ign_plot is not None and len(_ign_plot) > 0
    plotted_osm = _osm_plot is not None and len(_osm_plot) > 0
    if plotted_ign:
        handles.append(Line2D([], [], color="C0", linewidth=1.6, label="IGN BD TOPO"))
    if plotted_osm:
        handles.append(Line2D([], [], color="C1", linewidth=1.8, label="OSM"))
    # Légende pour points clothoïdes
    if fit_clothoid and clotho_osm is not None and len(clotho_osm) > 0:
        handles.append(Line2D([], [], linestyle="None", marker="x", color="C3", label="Clothoïde (OSM)"))
    if fit_clothoid and clotho_ign is not None and len(clotho_ign) > 0:
        handles.append(Line2D([], [], linestyle="None", marker="+", color="C0", label="Clothoïde (IGN)"))
    if handles:
        ax.legend(handles=handles, loc="best")
    ax.set_aspect("equal")
    fig.tight_layout()

    png_path = os.path.join(out_dir, f"romilly_map_{ts}.png")
    fig.savefig(png_path, dpi=220)
    plt.close(fig)

    # 4) stats enrichies
    summary = pd.concat(
        [
            _metrics_block("OSM", s_osm, clotho_osm if fit_clothoid else None, clothoid_step_m if fit_clothoid else None),
            _metrics_block("IGN", s_ign, clotho_ign if fit_clothoid else None, clothoid_step_m if fit_clothoid else None),
        ],
        axis=1,
    )
    csv_path = os.path.join(out_dir, f"romilly_summary_{ts}.csv")
    summary.to_csv(csv_path)

    if street and (summary.loc["features", "OSM"] == 0 and summary.loc["features", "IGN"] == 0):
        typer.echo("⚠️  Aucun segment trouvé pour cette rue avec les données chargées.")

    if debug:
        typer.echo(f"[DEBUG] Après filtre rue → OSM={len(g_osm)} IGN={len(g_ign)} (avec fallback spatial si nécessaire)")
    if debug:
        typer.echo(f"[DEBUG] street_buffer_m={street_buffer_m} m")
    if debug:
        n_osm_plot = len(_osm_plot) if (_osm_plot is not None and hasattr(_osm_plot, "__len__")) else 0
        n_ign_plot = len(_ign_plot) if (_ign_plot is not None and hasattr(_ign_plot, "__len__")) else 0
        typer.echo(f"[DEBUG] plotted -> OSM={n_osm_plot} IGN={n_ign_plot}")
    if debug:
        typer.echo(f"[DEBUG] centroids -> OSM={len(s_osm) if s_osm is not None else 0} (incl. géométriques si fallback) IGN={len(s_ign) if s_ign is not None else 0}")
    if debug and fit_clothoid:
        typer.echo(f"[DEBUG] clothoïdes -> OSM={len(clotho_osm) if clotho_osm is not None else 0} IGN={len(clotho_ign) if clotho_ign is not None else 0} (step={clothoid_step_m}m, win={clothoid_window_m}m, R2≥{clothoid_r2_min})")

    typer.echo("✅ Terminé.")
    typer.echo(f"🗺️ Carte: {png_path}")
    typer.echo(f"📄 Stats: {csv_path}")
    typer.echo("\nAperçu stats:")
    typer.echo(summary.to_string())


if __name__ == "__main__":
    app()
