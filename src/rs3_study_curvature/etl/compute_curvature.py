from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import math
import time
from threading import Thread, Event
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import LineString
import rasterio
import yaml
import logging
from tqdm import tqdm
from pyproj import Transformer
try:
    from pyrosm import OSM
except Exception:  # pragma: no cover
    OSM = None
try:
    import pyogrio
except Exception:  # pragma: no cover
    pyogrio = None

logging.basicConfig(level=logging.INFO, format='[roadinfo] %(levelname)s %(message)s')
log = logging.getLogger(__name__)

# --- Heartbeat helper for progress ---
class Heartbeat:
    """Background heartbeat that logs a message every `interval` seconds while a long task runs."""
    def __init__(self, message: str, interval: float = 5.0):
        self.message = message
        self.interval = float(interval)
        self._stop = Event()
        self._thread = Thread(target=self._run, daemon=True)

    def _run(self):
        t = 0.0
        while not self._stop.wait(self.interval):
            t += self.interval
            log.info(f"{self.message}… ({int(t)}s)")

    def __enter__(self):
        self._thread.start()
        return self

    def __exit__(self, exc_type, exc, tb):
        self._stop.set()
        self._thread.join(timeout=1.0)

def _load_bdtopo(path: Path, layer: str | None, bbox_l93: tuple[float,float,float,float] | None, crs: str) -> gpd.GeoDataFrame:
    read_kwargs = {}
    if layer:
        read_kwargs["layer"] = layer

    # Try to detect source CRS using pyogrio; default to EPSG:4326 for GeoJSON without CRS
    data_crs_str = None
    if pyogrio is not None:
        try:
            info = pyogrio.read_info(path, layer=layer) if layer else pyogrio.read_info(path)
            # info["crs"] can be WKT or None; info may also have "crs_name"
            wkt = info.get("crs_wkt") or info.get("crs")
            if wkt:
                from pyproj import CRS
                data_crs_str = CRS.from_wkt(wkt).to_string()
        except Exception:
            data_crs_str = None

    # --- Extra CRS detection fallbacks for GPKG/BD TOPO ---
    if data_crs_str is None and path.suffix.lower() == ".gpkg":
        # Try to parse pyogrio info fields more defensively
        if pyogrio is not None:
            try:
                info = pyogrio.read_info(path, layer=layer) if layer else pyogrio.read_info(path)
                # pyogrio may expose CRS in different shapes; try them all
                if info is not None:
                    cand = None
                    for k in ("crs_wkt", "crs", "crs_name"):
                        cand = cand or info.get(k)
                    if cand:
                        try:
                            from pyproj import CRS
                            data_crs_str = CRS.from_user_input(cand).to_string()
                        except Exception:
                            data_crs_str = None
            except Exception:
                pass
        # Fallback via fiona if available
        if data_crs_str is None:
            try:
                import fiona
                with fiona.open(path, layer=layer) as src:
                    crs_wkt = getattr(src, "crs_wkt", None)
                    crs_dict = getattr(src, "crs", None)
                    cand = crs_wkt or crs_dict
                    if cand:
                        from pyproj import CRS
                        data_crs_str = CRS.from_user_input(cand).to_string()
            except Exception:
                pass
        # Last resort: assume BD TOPO is in Lambert-93
        if data_crs_str is None:
            log.warning("CRS non détecté pour GPKG — hypothèse EPSG:2154 (Lambert-93) pour BD TOPO.")
            data_crs_str = "EPSG:2154"

    if data_crs_str is None and path.suffix.lower() in (".geojson", ".json"):
        data_crs_str = "EPSG:4326"

    # Prepare bbox in the DATA CRS if provided
    if bbox_l93 and data_crs_str and data_crs_str != crs:
        try:
            tr = Transformer.from_crs(crs, data_crs_str, always_xy=True)
            minx, miny, maxx, maxy = bbox_l93
            x1, y1 = tr.transform(minx, miny)
            x2, y2 = tr.transform(maxx, maxy)
            read_kwargs["bbox"] = (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))
            log.info(f"Chargement vecteur avec bbox={read_kwargs['bbox']} en {data_crs_str} (depuis L93)…")
        except Exception as e:
            log.warning(f"Échec reprojection bbox L93→{data_crs_str}: {e}. Lecture sans bbox, filtrage en mémoire.")
    elif bbox_l93 and data_crs_str == crs:
        read_kwargs["bbox"] = bbox_l93
        log.info(f"Chargement vecteur avec bbox L93={bbox_l93}…")
    elif bbox_l93 and data_crs_str is None:
        log.info("CRS source inconnu, lecture sans bbox (filtrage en mémoire après reprojection).")

    # Prefer pyogrio engine when available to avoid Fiona dependency
    if pyogrio is not None:
        read_kwargs["engine"] = "pyogrio"

    log.info(f"Lecture vecteur: path={path} layer={layer} bbox={read_kwargs.get('bbox')} engine={'pyogrio' if pyogrio is not None else 'fiona'}")

    start = time.perf_counter()
    with Heartbeat("Lecture vecteur/IO en cours", interval=5):
        gdf = gpd.read_file(path, **read_kwargs)
    log.info(f"Lecture vecteur terminée en {time.perf_counter() - start:.1f}s")

    # If no CRS set on read, assume WGS84 for GeoJSON
    if gdf.crs is None and data_crs_str:
        gdf = gdf.set_crs(data_crs_str, allow_override=True)
    elif gdf.crs is None and path.suffix.lower() in (".geojson", ".json"):
        gdf = gdf.set_crs("EPSG:4326")

    if gdf.crs is None and path.suffix.lower() == ".gpkg" and data_crs_str is None:
        log.warning("GPKG sans CRS déclaré — set_crs(EPSG:2154) par défaut.")
        gdf = gdf.set_crs("EPSG:2154")

    # Fallback: if we read zero rows with bbox, retry full read (engine=pyogrio if available) and filter in memory
    if len(gdf) == 0 and bbox_l93:
        log.warning("0 entités lues avec bbox; relecture sans bbox puis clip mémoire…")
        full_kwargs = {k: v for k, v in read_kwargs.items() if k != "bbox"}
        gdf_full = gpd.read_file(path, **full_kwargs)
        if gdf_full.crs is None and data_crs_str:
            gdf_full = gdf_full.set_crs(data_crs_str, allow_override=True)
        elif gdf_full.crs is None and path.suffix.lower() in (".geojson", ".json"):
            gdf_full = gdf_full.set_crs("EPSG:4326")
        gdf_full_l93 = gdf_full.to_crs(crs)
        minx, miny, maxx, maxy = bbox_l93
        gdf = gdf_full_l93.cx[minx:maxx, miny:maxy]

    return gdf.to_crs(crs)

def _load_osm(pbf_path: Path, bbox_wgs84: tuple[float,float,float,float] | None, crs: str, highways: list[str] | None) -> gpd.GeoDataFrame:
    if OSM is None:
        raise RuntimeError("pyrosm n'est pas installé. `pip install pyrosm`.")
    if not pbf_path.exists():
        raise FileNotFoundError(f"OSM PBF introuvable: {pbf_path}")
    log.info(f"Chargement OSM depuis {pbf_path} bbox WGS84={bbox_wgs84}…")
    if bbox_wgs84:
        # pyrosm requires a list (not a tuple) or a shapely geometry for bounding_box
        try:
            bb = [float(bbox_wgs84[0]), float(bbox_wgs84[1]), float(bbox_wgs84[2]), float(bbox_wgs84[3])]
        except Exception:
            raise ValueError("bbox_wgs84 doit être une séquence [minlon, minlat, maxlon, maxlat].")
        osm = OSM(str(pbf_path), bounding_box=bb)
    else:
        osm = OSM(str(pbf_path))
    # pyrosm attend bbox en (minx, miny, maxx, maxy) WGS84
    start = time.perf_counter()
    with Heartbeat("pyrosm: parsing PBF + construction du réseau (peut être long)", interval=5):
        edges = osm.get_network(network_type="driving")
    log.info(f"Réseau OSM chargé: {0 if edges is None else len(edges):,} segments en {time.perf_counter() - start:.1f}s")
    if edges is None or len(edges) == 0:
        raise RuntimeError("OSM: aucune route chargée avec ces paramètres.")
    if highways:
        edges = edges[edges["highway"].isin(highways)]
    # Assurer LineString uniquement
    edges = edges[edges.geometry.type.isin(["LineString","MultiLineString"])].explode(index_parts=False, ignore_index=True)
    edges = edges.rename(columns={"id": "road_id"})
    # Ensure we have a string identifier for each segment; if original OSM id is missing,
    # fall back to the GeoDataFrame index (as string). Using a Series here avoids the
    # pandas TypeError when filling with an Index directly.
    if "road_id" not in edges.columns:
        edges["road_id"] = edges.index.map(str)
    else:
        fallback_ids = pd.Series(edges.index.map(str), index=edges.index)
        edges["road_id"] = edges["road_id"].astype(object).fillna(fallback_ids)
    log.info(f"OSM: après explode/filtrage géométrique → {len(edges):,} segments")
    return edges.to_crs(crs)

def densify(line: LineString, step: float) -> LineString:
    L = line.length
    if L <= step:
        return line
    ds = np.arange(0, L, step)
    pts = [line.interpolate(float(d)) for d in ds] + [line.interpolate(L)]
    return LineString(pts)

def radius3(p1: np.ndarray, p2: np.ndarray, p3: np.ndarray) -> float:
    a = np.linalg.norm(p2 - p1); b = np.linalg.norm(p3 - p2); c = np.linalg.norm(p3 - p1)
    s = 0.5 * (a + b + c)
    A2 = max(s * (s - a) * (s - b) * (s - c), 0.0)
    if A2 <= 1e-16:
        return math.inf
    return (a * b * c) / (4.0 * math.sqrt(A2))

def curvature_profile(line: LineString) -> pd.DataFrame:
    xy = np.asarray(line.coords, dtype=float)
    if len(xy) < 3:
        return pd.DataFrame({"s_m": [0.0], "radius_m": [math.inf], "curvature_1perm": [0.0]})
    seglens = np.linalg.norm(np.diff(xy, axis=0), axis=1)
    svals, radii = [], []
    s = 0.0
    for i in range(1, len(xy) - 1):
        R = radius3(xy[i-1], xy[i], xy[i+1])
        radii.append(R)
        svals.append(s + seglens[i-1])
        s += seglens[i-1]
    r = np.array(radii)
    return pd.DataFrame({"s_m": svals, "radius_m": r, "curvature_1perm": np.where(np.isfinite(r), 1.0/r, 0.0)})

def slope_profile(line: LineString, dem_path: Path) -> pd.DataFrame:
    with rasterio.open(dem_path) as ds:
        band = ds.read(1)
        xs, ys = np.asarray(line.coords).T
        rows, cols = ds.index(xs, ys)
        zs = band[rows, cols].astype(float)
    d = np.linalg.norm(np.diff(np.vstack([xs, ys]).T, axis=0), axis=1)
    dz = np.diff(zs)
    slope = np.where(d > 0, (dz / d) * 100.0, 0.0)
    s_cum = np.cumsum(d) - d/2
    return pd.DataFrame({"s_m": s_cum, "slope_pct": slope})

@dataclass
class Cfg:
    bdtopo_gpkg: Path
    dem_tif: Path | None
    out_dir: Path
    crs: str
    simplify_tol: float
    densify_step: float
    min_seg_len: float
    robust_p: int
    clip_radius_min: float
    slope_enabled: bool
    layer: str | None = None
    bbox_l93: tuple[float, float, float, float] | None = None  # (minx, miny, maxx, maxy) in EPSG:2154
    bbox_wgs84: tuple[float, float, float, float] | None = None  # (minlon, minlat, maxlon, maxlat)

def build_from_config(cfg_path: Path) -> None:
    y = yaml.safe_load(Path(cfg_path).read_text())

    def _mk_cfg(y_local: dict, overrides: dict[str, object] | None = None) -> Cfg:
        o = overrides or {}
        cfg = Cfg(
            bdtopo_gpkg=Path(y_local["inputs"]["bdtopo_gpkg"]),
            dem_tif=(Path(y_local["inputs"]["dem_tif"]) if y_local["inputs"].get("dem_tif") else None),
            out_dir=Path(y_local["outputs"]["dir"]).resolve(),
            crs=y_local["processing"]["crs_meters"],
            simplify_tol=float(y_local["processing"]["simplify_tol_m"]),
            densify_step=float(y_local["processing"]["densify_step_m"]),
            min_seg_len=float(y_local["processing"]["min_seg_len_m"]),
            robust_p=int(y_local["processing"]["curvature"]["robust_percentile"]),
            clip_radius_min=float(y_local["processing"]["curvature"]["clip_radius_min_m"]),
            slope_enabled=bool(y_local["processing"]["slope"]["enabled"]),
            layer=(o.get("layer") if o.get("layer") is not None else y_local["processing"].get("layer") or y_local["inputs"].get("layer")),
            bbox_l93=tuple(y_local["processing"].get("bbox_l93")) if y_local["processing"].get("bbox_l93") else None,
            bbox_wgs84=tuple(y_local["processing"].get("bbox")) if y_local["processing"].get("bbox") else None,
        )
        cfg.out_dir.mkdir(parents=True, exist_ok=True)
        return cfg

    def _run_once(y_local: dict, source: str, out_suffix: str = "", layer: str | None = None, highways: list[str] | None = None) -> None:
        cfg = _mk_cfg(y_local, overrides={"layer": layer})

        # BBox effective en L93
        eff_bbox_l93 = None
        if cfg.bbox_l93:
            eff_bbox_l93 = cfg.bbox_l93
            log.info(f"BBox L93 fournie: {eff_bbox_l93}")
        elif cfg.bbox_wgs84:
            try:
                transformer = Transformer.from_crs("EPSG:4326", cfg.crs, always_xy=True)
                minlon, minlat, maxlon, maxlat = cfg.bbox_wgs84
                x1, y1 = transformer.transform(minlon, minlat)
                x2, y2 = transformer.transform(maxlon, maxlat)
                eff_bbox_l93 = (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))
                log.info(f"BBox WGS84={cfg.bbox_wgs84} → {eff_bbox_l93} en {cfg.crs}")
            except Exception as e:
                log.warning(f"Échec conversion bbox WGS84→{cfg.crs}: {e}. Lecture sans bbox.")

        # Lecture des données
        src = source.lower().strip()
        if src == "osm":
            if OSM is None:
                log.error("OSM demandé mais pyrosm n'est pas installé — run OSM ignoré.")
                return
            highways = highways or ((y_local.get("processing", {}).get("osm", {}) or {}).get("highways"))
            gdf = _load_osm(Path(y_local["inputs"].get("osm_pbf", "")), cfg.bbox_wgs84, cfg.crs, highways)
        else:
            gdf = _load_bdtopo(cfg.bdtopo_gpkg, cfg.layer, eff_bbox_l93, cfg.crs)

        log.info(f"Couche chargée: {len(gdf):,} tronçons | CRS={gdf.crs}")

        # --- Standardize attribute columns (class/name/maxspeed) for downstream tools ---
        class_candidates = [
            "highway",  # OSM
            "class", "classe", "nature", "type", "CATEGORIE", "CATEGORIE_ROUTE",
        ]
        name_candidates = [
            "name",  # OSM
            "nom", "NOM", "NOM_VOIE", "NOM_ITI", "LIBELLE", "LIBELLE_VOIE",
        ]
        class_col = next((c for c in class_candidates if c in gdf.columns), None)
        name_col = next((c for c in name_candidates if c in gdf.columns), None)
        maxspeed_col = "maxspeed" if "maxspeed" in gdf.columns else None
        if class_col:
            log.info(f"Colonne classe détectée: '{class_col}' → sera exportée comme 'class'.")
        if name_col:
            log.info(f"Colonne nom détectée: '{name_col}' → sera exportée comme 'name'.")
        if maxspeed_col:
            log.info("Colonne 'maxspeed' détectée → exportée telle quelle.")

        seg_rows, prof_rows = [], []
        log.info("Début du calcul de courbure/pente…")
        for _, r in tqdm(gdf.iterrows(), total=len(gdf), desc="curvature", unit="seg"):
            geom = r.geometry
            if not isinstance(geom, LineString) or geom.length < cfg.min_seg_len:
                continue
            line = densify(geom.simplify(cfg.simplify_tol), cfg.densify_step)
            if not np.isfinite(line.length) or line.length <= 0:
                continue

            # Centroid (for matching / diagnostics)
            c = line.centroid

            prof = curvature_profile(line)
            rad = prof["radius_m"].replace([np.inf, -np.inf], np.nan).dropna()
            if rad.empty:
                # Segment parfaitement rectiligne (aucune courbure mesurable à l'échelle d'échantillonnage)
                # On évite d'écrire des +inf qui perturbent les stats en aval.
                r_min = None
                r_p85 = None
                curv_mean = 0.0
                is_straight = True
            else:
                r_min = max(float(rad.min()), cfg.clip_radius_min)
                r_p85 = float(np.percentile(rad, cfg.robust_p))
                curv_mean = float((1.0 / rad).clip(upper=1.0 / cfg.clip_radius_min).mean())
                is_straight = False

            slope_mean = None; slope_p95 = None
            if cfg.slope_enabled and cfg.dem_tif is not None:
                sp = slope_profile(line, cfg.dem_tif)
                slope_mean = float(sp["slope_pct"].mean())
                slope_p95 = float(np.percentile(sp["slope_pct"], 95))
                prof = prof.merge(sp, on="s_m", how="outer").sort_values("s_m")

            road_id = str(r.get("ID", _))
            seg_rows.append({
                "road_id": road_id,
                "x_centroid": float(c.x),
                "y_centroid": float(c.y),
                "length_m": float(line.length),
                "radius_min_m": r_min,
                "radius_p85_m": r_p85,
                "curv_mean_1perm": curv_mean,
                "slope_mean_pct": slope_mean,
                "slope_p95_pct": slope_p95,
                "is_straight": is_straight,
                "source": src,
                # standardized attributes (if present)
                "class": (str(r.get(class_col)) if class_col is not None and pd.notna(r.get(class_col)) else None),
                "name": (str(r.get(name_col)) if name_col is not None and pd.notna(r.get(name_col)) else None),
                "maxspeed": (str(r.get(maxspeed_col)) if maxspeed_col is not None and pd.notna(r.get(maxspeed_col)) else None),
            })
            prof["road_id"] = road_id
            prof["source"] = src
            prof_rows.append(prof)

        # Résolution des chemins de sortie (patterns ou valeurs par défaut)
        out = y_local.get("outputs", {})
        seg_pat = out.get("segments_pattern")
        pro_pat = out.get("profile_pattern")
        if out_suffix and seg_pat:
            seg_path = Path(out["dir"]) / seg_pat.format(suffix=out_suffix)
        elif out_suffix:
            seg_path = Path(out["dir"]) / f"roadinfo_segments{out_suffix}.parquet"
        else:
            seg_path = Path(out["dir"]) / out.get("segments_parquet", "roadinfo_segments.parquet")
        if out_suffix and pro_pat:
            prof_path = Path(out["dir"]) / pro_pat.format(suffix=out_suffix)
        elif out_suffix:
            prof_path = Path(out["dir"]) / f"roadinfo_profile{out_suffix}.parquet"
        else:
            prof_path = Path(out["dir"]) / out.get("profile_parquet", "roadinfo_profile.parquet")

        seg_path = seg_path.resolve(); prof_path = prof_path.resolve()
        Path(out["dir"]).mkdir(parents=True, exist_ok=True)

        # --- Write segments ---
        seg_df = pd.DataFrame(seg_rows)
        try:
            seg_df.to_parquet(seg_path, index=False)
            log.info(f"Écrit: {seg_path} ({len(seg_df):,} lignes)")
        except Exception as e:
            log.warning(f"Échec écriture Parquet pour segments ({e}). Fallback CSV.")
            seg_path_csv = seg_path.with_suffix(".csv")
            seg_df.to_csv(seg_path_csv, index=False)
            log.info(f"Écrit: {seg_path_csv} ({len(seg_df):,} lignes)")

        # --- Write profile ---
        if prof_rows:
            prof_df = pd.concat(prof_rows, ignore_index=True)
            try:
                prof_df.to_parquet(prof_path, index=False)
                log.info(f"Écrit: {prof_path} ({len(prof_df):,} échantillons)")
            except Exception as e:
                log.warning(f"Échec écriture Parquet pour profile ({e}). Fallback CSV.")
                prof_path_csv = prof_path.with_suffix(".csv")
                prof_df.to_csv(prof_path_csv, index=False)
                log.info(f"Écrit: {prof_path_csv} ({len(prof_df):,} échantillons)")

    # --- Orchestration: single-run vs multi-run ---
    multi = (y.get("processing", {}).get("multi", {}) or {})
    if multi.get("enabled") and multi.get("runs"):
        for run in multi["runs"]:
            name = run.get("name", "run")
            src = run.get("source", y["processing"].get("source", "bdtopo"))
            suffix = run.get("out_suffix", f"_{name}")
            layer = run.get("layer") or y["processing"].get("layer") or y["inputs"].get("layer")
            highways = run.get("highways")
            log.info(f"===== RUN {name} | source={src} | suffix={suffix} =====")
            _run_once(y, source=src, out_suffix=suffix, layer=layer, highways=highways)
    else:
        # Backward compatible single run
        src = y["processing"].get("source", "bdtopo")
        _run_once(y, source=src, out_suffix="", layer=y["processing"].get("layer") or y["inputs"].get("layer"))
