from typing import Optional, Tuple
import warnings
import os
import geopandas as gpd
from shapely.geometry import LineString, MultiLineString
from shapely.ops import unary_union
import pandas as pd
from shapely.geometry import box
import unicodedata
import time
from pyproj import Transformer, CRS
try:
    import fiona as _fiona  # optional, used to peek CRS cheaply
except Exception:
    _fiona = None

def _casefold_no_accents(s: str) -> str:
    if s is None:
        return ""
    # Remove accents then casefold
    return unicodedata.normalize("NFKD", str(s)).encode("ASCII", "ignore").decode("ASCII").casefold()

# Helper: strip French voie types for fuzzy matching
_FR_VOIE_TOKENS = {
    "rue", "av", "ave", "avenue", "bd", "bld", "boulevard", "chemin", "chem", "che",
    "route", "rt", "impasse", "imp", "allee", "allée", "all", "place", "pl", "quai", "qa",
    "cours", "crs", "sentier", "sente", "voie", "square", "sq", "rocade", "roc",
    "faubourg", "fg", "chaussée", "chaussee", "ch", "cd", "rd", "vc"
}

def _normalize_street_text(s: str) -> str:
    s2 = _casefold_no_accents(s)
    # remove punctuation
    for ch in ",;:.!?()[]{}'\"-_/\\":
        s2 = s2.replace(ch, " ")
    toks = [t for t in s2.split() if t and t not in _FR_VOIE_TOKENS]
    return " ".join(toks)

def _normalize_name_column(gdf: gpd.GeoDataFrame, fallback: str = "") -> gpd.GeoDataFrame:
    # Try common name columns (OSM + IGN/BDTopo)
    if "name" not in gdf.columns:
        for cand in [
            "nom", "nom_voie", "voie", "road_name", "libelle", "label",
            "NOM", "NOM_VOIE", "LIBELLE"
        ]:
            if cand in gdf.columns:
                gdf = gdf.rename(columns={cand: "name"})
                break
    if "name" not in gdf.columns:
        gdf["name"] = fallback
    else:
        def _norm(n):
            if isinstance(n, list):
                return ", ".join(map(str, n))
            return str(n) if n is not None else ""
        gdf["name"] = gdf["name"].map(_norm)
    return gdf

def _optional_import_osmnx():
    try:
        import osmnx as ox
        return ox
    except Exception as e:
        warnings.warn(f"osmnx non disponible ({e}); lecture de rues désactivée.")
        return None

def load_streets_from_osm(bbox: Tuple[float, float, float, float], street: Optional[str]=None) -> gpd.GeoDataFrame:
    """
    Charge un graphe/rues OSM via osmnx dans la BBox (WGS84).
    Filtre 'street' si fourni (contains, casefold).
    """
    ox = _optional_import_osmnx()
    if ox is None:
        raise RuntimeError("osmnx requis pour interroger OSM")

    # Temporarily relax Overpass max area to avoid massive bbox splitting
    prev_max_area = getattr(ox.settings, "max_query_area_size", None)
    try:
        desired_max = float(os.environ.get("RS3_OSMNX_MAXAREA", 7.5e7))  # 75 km² default
    except Exception:
        desired_max = 7.5e7
    try:
        if prev_max_area is not None and prev_max_area < desired_max:
            ox.settings.max_query_area_size = desired_max
    except Exception:
        pass

    minx, miny, maxx, maxy = bbox
    # Build bbox tuple in (north, south, east, west) order as commonly used by OSMnx
    bbox_tuple = (maxy, miny, maxx, minx)
    # If a street name is provided, try to fetch only those features to avoid huge bbox graphs
    if street:
        tags = {"highway": True, "name": street}

        place = os.environ.get("RS3_OSMNX_PLACE")
        if place:
            try:
                place_gdf = ox.geocode_to_gdf(place)
            except Exception:
                place_gdf = None
            if place_gdf is not None and len(place_gdf):
                try:
                    polys = [geom for geom in place_gdf.geometry if geom is not None]
                    collected = []
                    for poly in polys:
                        try:
                            f = ox.features_from_polygon(polygon=poly, tags=tags)
                        except Exception:
                            try:
                                f = ox.geometries_from_polygon(polygon=poly, tags=tags)
                            except Exception:
                                f = None
                        if f is not None and len(f):
                            collected.append(f)
                    if collected:
                        try:
                            feats = gpd.pd.concat(collected, ignore_index=False)
                        except Exception:
                            feats = gpd.GeoDataFrame(pd.concat(collected, ignore_index=False))
                    else:
                        feats = None
                except Exception:
                    feats = None
            if feats is not None and len(feats):
                feats = feats[[geom.geom_type in ("LineString", "MultiLineString") for geom in feats.geometry]]
                if len(feats):
                    gdf = feats.copy()
                    if gdf.crs is None:
                        gdf.set_crs("EPSG:4326", inplace=True)
                    gdf = gdf.reset_index(drop=True)
                    if "name" not in gdf.columns:
                        gdf["name"] = street
                    else:
                        def _norm(n):
                            if isinstance(n, list):
                                return ", ".join(map(str, n))
                            return str(n) if n is not None else ""
                        gdf["name"] = gdf["name"].map(_norm)
                    geom = unary_union(gdf.geometry.values)
                    out = gpd.GeoDataFrame(
                        {"name": [street], "count": [len(gdf)]},
                        geometry=[geom if isinstance(geom, (LineString, MultiLineString)) else geom],
                        crs="EPSG:4326",
                    )
                    if os.environ.get("RS3_STREETS_KEEP_SEGMENTS", "0") in ("1", "true", "True"):
                        gdf = gdf[[geom.geom_type in ("LineString", "MultiLineString") for geom in gdf.geometry]].copy()
                        gdf = gdf.reset_index(drop=True)
                        gdf["source"] = "osm"
                        try:
                            if prev_max_area is not None:
                                ox.settings.max_query_area_size = prev_max_area
                        except Exception:
                            pass
                        print(f"[streets] OSM(features) returning raw segments (no dissolve): rows={len(gdf)}")
                        if len(gdf) == 0:
                            try:
                                if prev_max_area is not None:
                                    ox.settings.max_query_area_size = prev_max_area
                            except Exception:
                                pass
                            return gpd.GeoDataFrame(geometry=[], crs="EPSG:4326")
                        return gpd.GeoDataFrame(gdf, geometry="geometry", crs=gdf.crs or "EPSG:4326").to_crs("EPSG:4326")
                    try:
                        if prev_max_area is not None:
                            ox.settings.max_query_area_size = prev_max_area
                    except Exception:
                        pass
                    return out

        # Optional tiling to avoid huge Overpass splits
        # Controlled by env RS3_OSMNX_TILE_DEG (tile size in degrees, default 0.01) and RS3_OSMNX_TILE_ENABLE (default 1)
        tile_enable = os.environ.get("RS3_OSMNX_TILE_ENABLE", "1") not in ("0", "false", "False")
        tile_deg = float(os.environ.get("RS3_OSMNX_TILE_DEG", "0.01"))
        feats = None
        if tile_enable and (maxx - minx > tile_deg or maxy - miny > tile_deg):
            collected = []
            x = minx
            while x < maxx:
                x2 = min(x + tile_deg, maxx)
                y = miny
                while y < maxy:
                    y2 = min(y + tile_deg, maxy)
                    try:
                        # Try v2 API first (bbox tuple order is north, south, east, west)
                        _bbox = (y2, y, x2, x)
                        f = ox.features_from_bbox(bbox=_bbox, tags=tags)
                    except Exception:
                        try:
                            f = ox.geometries_from_bbox(north=y2, south=y, east=x2, west=x, tags=tags)
                        except Exception:
                            f = None
                    if f is not None and len(f):
                        collected.append(f)
                    y = y2
                x = x2
            if collected:
                try:
                    feats = gpd.pd.concat(collected, ignore_index=False)
                except Exception:
                    feats = gpd.GeoDataFrame(pd.concat(collected, ignore_index=False))

        if feats is None or len(feats) == 0:
            try:
                # OSMnx v2+: features_from_bbox with a bbox tuple
                feats = ox.features_from_bbox(bbox=bbox_tuple, tags=tags)
            except Exception:
                try:
                    # v1 fallback: geometries_from_bbox with named bounds
                    feats = ox.geometries_from_bbox(north=maxy, south=miny, east=maxx, west=minx, tags=tags)
                except Exception:
                    feats = None
        if feats is not None and len(feats):
            # keep only linear street geometries
            feats = feats[[geom.geom_type in ("LineString", "MultiLineString") for geom in feats.geometry]]
            if len(feats):
                gdf = feats.copy()
                # ensure CRSs
                if gdf.crs is None:
                    gdf.set_crs("EPSG:4326", inplace=True)
                gdf = gdf.reset_index(drop=True)
                # normalize 'name' column
                if "name" not in gdf.columns:
                    gdf["name"] = street
                else:
                    def _norm(n):
                        if isinstance(n, list):
                            return ", ".join(map(str, n))
                        return str(n) if n is not None else ""
                    gdf["name"] = gdf["name"].map(_norm)
                if street:
                    print(f"[streets] OSM name filter matched rows={len(gdf)} for query={street!r}")
                if os.environ.get("RS3_STREETS_KEEP_SEGMENTS", "0") in ("1", "true", "True"):
                    gdf = gdf[[geom.geom_type in ("LineString", "MultiLineString") for geom in gdf.geometry]].copy()
                    gdf = gdf.reset_index(drop=True)
                    gdf["source"] = "osm"
                    try:
                        if prev_max_area is not None:
                            ox.settings.max_query_area_size = prev_max_area
                    except Exception:
                        pass
                    print(f"[streets] OSM(features) returning raw segments (no dissolve): rows={len(gdf)}")
                    return gdf.set_crs("EPSG:4326")
                # dissolve to a single feature
                geom = unary_union(gdf.geometry.values)
                out = gpd.GeoDataFrame(
                    {"name": [street], "count": [len(gdf)]},
                    geometry=[geom if isinstance(geom, (LineString, MultiLineString)) else geom],
                    crs="EPSG:4326",
                )
                try:
                    if prev_max_area is not None:
                        ox.settings.max_query_area_size = prev_max_area
                except Exception:
                    pass
                return out
    G = None
    # Try common variants across OSMnx versions
    try:
        # OSMnx v2/v3 often expect a single bbox tuple
        G = ox.graph_from_bbox(bbox_tuple, network_type="drive")
    except TypeError:
        try:
            # Older signature with keyword-only bounds
            G = ox.graph_from_bbox(north=maxy, south=miny, east=maxx, west=minx, network_type="drive")
        except TypeError:
            # Very old signature with 4 positional bounds
            G = ox.graph_from_bbox(maxy, miny, maxx, minx, network_type="drive")
    except AttributeError:
        # Some installs expose functions under ox.graph.*
        try:
            G = ox.graph.graph_from_bbox(bbox=bbox_tuple, network_type="drive")
        except TypeError:
            G = ox.graph.graph_from_bbox(north=maxy, south=miny, east=maxx, west=minx, network_type="drive")
    try:
        gdf = ox.graph_to_gdfs(G, nodes=False, edges=True)
    except AttributeError:
        gdf = ox.graph.graph_to_gdfs(G, nodes=False, edges=True)
    gdf = gdf.reset_index(drop=True)

    # nom canonique
    name = gdf.get("name")
    if name is None:
        gdf["name"] = ""
    else:
        # name peut être liste; normaliser
        def _norm(n):
            if isinstance(n, list):
                return ", ".join(map(str, n))
            return str(n) if n is not None else ""
        gdf["name"] = gdf["name"].map(_norm)

    # Build normalized name for fuzzy contains (strip voie type + accents)
    if "name" in gdf.columns:
        gdf["name_norm"] = gdf["name"].map(_normalize_street_text)
    else:
        gdf["name_norm"] = ""

    if street:
        s_raw = _casefold_no_accents(street)
        s_fuz = _normalize_street_text(street)
        before = len(gdf)
        g1 = gdf[gdf["name"].map(lambda x: s_raw in _casefold_no_accents(x))] if "name" in gdf.columns else gdf.iloc[[]]
        g2 = gdf[gdf["name_norm"].map(lambda x: s_fuz in x)] if "name_norm" in gdf.columns else gdf.iloc[[]]
        gdf = pd.concat([g1, g2], ignore_index=False).drop_duplicates().reset_index(drop=True)
        print(f"[streets] OSM name filter matched rows={len(gdf)} (from {before}) for query={street!r}")

    if os.environ.get("RS3_STREETS_KEEP_SEGMENTS", "0") in ("1", "true", "True"):
        gdf = gdf[[geom.geom_type in ("LineString", "MultiLineString") for geom in gdf.geometry]].copy()
        gdf = gdf.reset_index(drop=True)
        gdf["source"] = "osm"
        try:
            if prev_max_area is not None:
                ox.settings.max_query_area_size = prev_max_area
        except Exception:
            pass
        print(f"[streets] OSM(graph) returning raw segments (no dissolve): rows={len(gdf)}")
        if len(gdf) == 0:
            try:
                if prev_max_area is not None:
                    ox.settings.max_query_area_size = prev_max_area
            except Exception:
                pass
            return gpd.GeoDataFrame(geometry=[], crs="EPSG:4326")
        return gpd.GeoDataFrame(gdf, geometry="geometry", crs=gdf.crs or "EPSG:4326").to_crs("EPSG:4326")

    # Dissolve pour avoir une seule MultiLineString
    if len(gdf) == 0:
        try:
            if prev_max_area is not None:
                ox.settings.max_query_area_size = prev_max_area
        except Exception:
            pass
        return gdf.set_crs("EPSG:4326")

    geom = unary_union(gdf.geometry.values)
    out = gpd.GeoDataFrame(
        {"name": [street or "selection"], "count": [len(gdf)]},
        geometry=[geom if isinstance(geom, (LineString, MultiLineString)) else geom],
        crs="EPSG:4326",
    )
    try:
        if prev_max_area is not None:
            ox.settings.max_query_area_size = prev_max_area
    except Exception:
        pass
    return out

def load_streets_from_ign(bbox: Tuple[float, float, float, float], street: Optional[str] = None) -> gpd.GeoDataFrame:
    """Charge une couche IGN/BDTopo (RS3_IGN_PATH) et clippe à la BBox.
    Filtre par nom si possible (contains, insensible aux accents/casse).
    Optimisé: lecture directe avec bbox si possible, réduction de colonnes, option segments bruts.
    """
    path = os.environ.get("RS3_IGN_PATH")
    if not path:
        raise RuntimeError("RS3_IGN_PATH not set: provide path to IGN/BDTopo lines (GeoPackage/GeoJSON/Shapefile)")
    layer = os.environ.get("RS3_IGN_LAYER")  # optionnel: nom de couche GPKG
    name_col_override = os.environ.get("RS3_IGN_COL_NAME")  # optionnel: colonne explicite pour le nom de voie

    t0 = time.perf_counter()
    minx, miny, maxx, maxy = bbox

    # Lecture rapide avec bbox quand le driver le permet (Fiona/GDAL) — en respectant le CRS de la couche
    # 1) déterminer le CRS de la couche sans tout lire (via Fiona si dispo, sinon read_file(rows=1))
    layer_crs = None
    if _fiona is not None:
        try:
            with _fiona.Env():
                with _fiona.open(path, layer=layer) as src:
                    try:
                        layer_crs = CRS.from_user_input(src.crs) if src.crs else None
                    except Exception:
                        layer_crs = None
        except Exception:
            layer_crs = None
    if layer_crs is None:
        try:
            gpeek = gpd.read_file(path, layer=layer, rows=1)
            layer_crs = CRS.from_user_input(gpeek.crs) if gpeek.crs else None
        except Exception:
            layer_crs = None

    # 2) transformer la bbox (WGS84) vers le CRS de la couche si nécessaire
    minx, miny, maxx, maxy = bbox
    bbox_for_read = (minx, miny, maxx, maxy)
    if layer_crs and layer_crs.to_string() not in ("EPSG:4326", "OGC:CRS84"):
        try:
            t = Transformer.from_crs("EPSG:4326", layer_crs, always_xy=True)
            x1, y1 = t.transform(minx, miny)
            x2, y2 = t.transform(maxx, maxy)
            xmin, xmax = (x1, x2) if x1 <= x2 else (x2, x1)
            ymin, ymax = (y1, y2) if y1 <= y2 else (y2, y1)
            bbox_for_read = (xmin, ymin, xmax, ymax)
        except Exception:
            bbox_for_read = (minx, miny, maxx, maxy)

    force_full = os.environ.get("RS3_IGN_FORCE_FULL_READ", "0") in ("1", "true", "True")
    if layer_crs is not None:
        try:
            print(f"[streets] IGN layer CRS={layer_crs.to_string()} bbox_for_read={bbox_for_read}")
        except Exception:
            pass

    gdf = None
    # 3 étapes: bbox -> mask -> full+clip
    if not force_full:
        try:
            read_kwargs = {"bbox": bbox_for_read}
            if layer:
                read_kwargs["layer"] = layer
            gdf = gpd.read_file(path, **read_kwargs)
            print(f"[streets] IGN read(bbox): path={path} layer={layer} rows={len(gdf)} crs={gdf.crs}")
            if len(gdf) == 0:
                gdf = None  # déclenche fallback mask
        except Exception as e:
            print(f"[streets] IGN read(bbox) failed → trying mask ({e})")
            gdf = None
    if gdf is None:
        # Fallback 2: lecture avec mask (spatial filter) côté driver
        try:
            mask_geom = box(*bbox_for_read) if (layer_crs and layer_crs.to_string() != "EPSG:4326") else box(minx, miny, maxx, maxy)
            read_kwargs = {"mask": mask_geom}
            if layer:
                read_kwargs["layer"] = layer
            gdf = gpd.read_file(path, **read_kwargs)
            print(f"[streets] IGN read(mask): path={path} layer={layer} rows={len(gdf)} crs={gdf.crs}")
            if len(gdf) == 0:
                gdf = None
        except Exception as e:
            print(f"[streets] IGN read(mask) failed → fallback full read ({e})")
            gdf = None
    if gdf is None:
        # Fallback 3: lecture complète puis clip
        gdf = gpd.read_file(path, layer=layer) if layer else gpd.read_file(path)
        print(f"[streets] IGN read(full): path={path} layer={layer} rows={len(gdf)} crs={gdf.crs}")
        clip_box = gpd.GeoDataFrame(geometry=[box(minx, miny, maxx, maxy)], crs="EPSG:4326")
        try:
            if gdf.crs and str(gdf.crs) != "EPSG:4326":
                clip_box = clip_box.to_crs(gdf.crs)
            gdf = gdf.clip(clip_box)
        except Exception:
            pass

    # Print available columns for debug if requested
    if os.environ.get("RS3_IGN_NAME_DEBUG", "0") in ("1","true","True"):
        try:
            print("[streets] IGN columns:", list(gdf.columns))
        except Exception:
            pass

    # Reprojection en WGS84
    if gdf.crs is None:
        gdf = gdf.set_crs("EPSG:4326")
    elif str(gdf.crs) != "EPSG:4326":
        try:
            gdf = gdf.to_crs("EPSG:4326")
        except Exception as e:
            print(f"[streets] WARN: reprojection to EPSG:4326 failed ({e})")

    # Réduction des colonnes pour alléger
    possible_cols = [
        name_col_override if name_col_override else None,
        "name", "nom", "nom_voie", "voie", "road_name", "libelle", "label",
        "NOM", "NOM_VOIE", "LIBELLE",
    ]
    possible_cols = [c for c in possible_cols if c]
    keep_cols = [c for c in possible_cols if c in gdf.columns]
    name_unavailable = False
    if keep_cols:
        keep_cols = list(dict.fromkeys(keep_cols))  # unique en conservant l'ordre
        if "geometry" not in keep_cols:
            keep_cols.append("geometry")
        gdf = gdf[keep_cols]
        if not any(c for c in keep_cols if c != "geometry"):
            name_unavailable = True
    else:
        gdf = gdf[["geometry"]]
        name_unavailable = True

    # Normalisation du nom SANS fallback sur la requête
    gdf = _normalize_name_column(gdf, fallback="")
    # If the resulting name column is empty everywhere, consider names unavailable
    try:
        if "name" in gdf.columns:
            all_empty = (gdf["name"].astype(str).str.strip() == "").all()
            if all_empty:
                name_unavailable = True
    except Exception:
        pass
    # Build normalized name for fuzzy contains (strip voie type + accents)
    if "name" in gdf.columns:
        gdf["name_norm"] = gdf["name"].map(_normalize_street_text)
    else:
        gdf["name_norm"] = ""
    if os.environ.get("RS3_IGN_NAME_DEBUG", "0") in ("1","true","True"):
        try:
            sample = gdf[["name","name_norm"]].dropna().drop_duplicates().head(20)
            print("[streets] IGN name samples:\n", sample.to_string(index=False))
        except Exception:
            pass

    # Filtre attributaire optionnel (contains + fuzzy contains sans type de voie)
    if street:
        if name_unavailable:
            print("[streets] IGN: no usable name column/values; skipping attribute name filter and keeping spatial selection only")
        else:
            s_raw = _casefold_no_accents(street)
            s_fuz = _normalize_street_text(street)
            before = len(gdf)
            # 1) try strict contains on raw name
            g1 = gdf[gdf["name"].map(lambda x: s_raw in _casefold_no_accents(x))] if "name" in gdf.columns else gdf.iloc[[]]
            # 2) try fuzzy contains on normalized name
            g2 = gdf[gdf["name_norm"].map(lambda x: s_fuz in x)] if "name_norm" in gdf.columns else gdf.iloc[[]]
            gdf = pd.concat([g1, g2], ignore_index=False).drop_duplicates().reset_index(drop=True)
            print(f"[streets] IGN name filter matched rows={len(gdf)} (from {before}) for query={street!r}")
            # optional: if still zero, propose close matches
            if len(gdf) == 0 and os.environ.get("RS3_IGN_SUGGEST", "1") in ("1","true","True"):
                try:
                    import difflib
                    universe = (gdf[["name","name_norm"]] if "name" in gdf.columns else pd.DataFrame({"name_norm":[]}))
                    names = list({*(universe.get("name", pd.Series(dtype=str)).dropna().tolist()), *(universe.get("name_norm", pd.Series(dtype=str)).dropna().tolist())})
                    sugg = difflib.get_close_matches(s_fuz, names, n=5, cutoff=0.6)
                    if sugg:
                        print(f"[streets] IGN suggestions (normalized): {sugg}")
                except Exception:
                    pass

    # Option: renvoyer les segments bruts (pas de dissolve) pour comparaison/rapidité
    if os.environ.get("RS3_STREETS_KEEP_SEGMENTS", "0") in ("1", "true", "True"):
        # garder uniquement les géométries linéaires et s'assurer de conserver un GeoDataFrame
        if "geometry" in gdf.columns:
            mask_lines = [getattr(geom, "geom_type", None) in ("LineString", "MultiLineString") for geom in gdf.geometry]
            if len(mask_lines) == len(gdf):
                gdf = gdf.loc[mask_lines].copy()
            else:
                gdf = gdf.copy()
        # reconstruire un GeoDataFrame explicite si nécessaire
        if not isinstance(gdf, gpd.GeoDataFrame):
            gdf = gpd.GeoDataFrame(gdf, geometry=gdf["geometry"] if "geometry" in gdf.columns else None)
        gdf = gdf.reset_index(drop=True)
        if "geometry" not in gdf.columns:
            gdf["geometry"] = None
        gdf["source"] = "ign"
        # définir CRS si manquant
        if getattr(gdf, "crs", None) is None:
            try:
                gdf.set_crs("EPSG:4326", inplace=True)
            except Exception:
                pass
        print(f"[streets] IGN returning raw segments (no dissolve): rows={len(gdf)} (t={time.perf_counter()-t0:.2f}s)")
        # si vide, retourner un GeoDataFrame vide bien formé
        if len(gdf) == 0:
            return gpd.GeoDataFrame(geometry=[], crs="EPSG:4326")
        return gdf.to_crs("EPSG:4326")

    if len(gdf) == 0:
        print(f"[streets] IGN: no feature after filtering (t={time.perf_counter()-t0:.2f}s)")
        return gdf.set_crs("EPSG:4326")

    # Dissolve → une seule (multi)géométrie
    geom = unary_union(gdf.geometry.values)
    out = gpd.GeoDataFrame(
        {"name": [street or "selection"], "count": [len(gdf)]},
        geometry=[geom if isinstance(geom, (LineString, MultiLineString)) else geom],
        crs="EPSG:4326",
    )
    print(f"[streets] IGN dissolved rows={len(gdf)} → 1 feature (t={time.perf_counter()-t0:.2f}s)")
    return out

def buffer_m(gdf: gpd.GeoDataFrame, meters: float) -> gpd.GeoDataFrame:
    if gdf.crs is None:
        gdf = gdf.set_crs("EPSG:4326")
    # proj métrique (approx local) — WebMercator convient pour buffering rapide
    gdf_m = gdf.to_crs(3857)
    buf = gdf_m.buffer(meters)
    return gpd.GeoDataFrame(gdf_m.drop(columns="geometry"), geometry=buf, crs=3857).to_crs(4326)

def explode_to_lines(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    return gdf.explode(index_parts=False).reset_index(drop=True)

def load_streets(bbox: Tuple[float, float, float, float], street: Optional[str] = None) -> gpd.GeoDataFrame:
    source = os.environ.get("RS3_STREETS_SOURCE", "osm").lower()
    print(f"[streets] source={source}")
    if source == "ign":
        return load_streets_from_ign(bbox, street=street)
    return load_streets_from_osm(bbox, street=street)
