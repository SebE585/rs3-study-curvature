from typing import Optional, Tuple
import geopandas as gpd
import os
import numpy as np
import pandas as pd

from rs3_study_curvature.data.io import ensure_out_dir, write_parquet, write_geojson
from rs3_study_curvature.data.streets import load_streets_from_osm, load_streets_from_ign, buffer_m, explode_to_lines
from rs3_study_curvature.geometry.curvature import annotate_curvature_on_gdf
from rs3_study_curvature.geometry.clothoid import fit_local_clothoid
from rs3_study_curvature.viz.map_plot import plot_map
from rs3_study_curvature.viz.distrib_plot import plot_distributions


def _to_m(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    if gdf.crs is None:
        gdf = gdf.set_crs(4326)
    return gdf.to_crs(3857)


def run_map(
    out_dir: str,
    bbox: Tuple[float, float, float, float],
    street: Optional[str],
    street_buffer_m: float,
    plot_centroids: bool,
    fit_clothoid: bool,
    clothoid_step_m: float,
    clothoid_window_m: float,
    clothoid_r2_min: float,
):
    od = ensure_out_dir(out_dir)
    minx, miny, maxx, maxy = bbox
    # Sélection explicite de la source (OSM/IGN) via env
    src = os.environ.get("RS3_STREETS_SOURCE", "osm").lower()
    ign_path = os.environ.get("RS3_IGN_PATH")
    print(f"[linkedin.map] source={src} RS3_IGN_PATH={ign_path}")
    if src == "ign":
        streets = load_streets_from_ign((minx, miny, maxx, maxy), street=street)
    else:
        streets = load_streets_from_osm((minx, miny, maxx, maxy), street=street)
    # Log du nombre d'entités appariées (si dispo)
    try:
        matched = int(streets.get("count", pd.Series([len(streets)])).iloc[0])
        print(f"[linkedin.map] matched_rows={matched}")
    except Exception:
        pass
    edges = explode_to_lines(streets)

    # Sauvegarde des segments bruts pour comparaison (si demandé)
    if os.environ.get("RS3_STREETS_KEEP_SEGMENTS", "0") in ("1", "true", "True"):
        try:
            write_geojson(edges.to_crs(4326), str(od / "edges_raw.geojson"))
            print(f"[linkedin.map] saved raw edges → {od / 'edges_raw.geojson'} (rows={len(edges)})")
        except Exception as e:
            print(f"[linkedin.map] warn: could not save edges_raw.geojson ({e})")

    edges_m = _to_m(edges)

    # stats de courbure (pour filtres éventuels)
    edges_stats = annotate_curvature_on_gdf(edges_m, step_m=max(2.0, clothoid_step_m))
    write_parquet(edges_stats.to_crs(4326).drop(columns="geometry"), str(od / "edges_stats.parquet"))
    write_geojson(edges.to_crs(4326), str(od / "edges.geojson"))

    # Filtrage visuel des virages intéressants (rayon)
    # Env overrides:
    #   RS3_RADIUS_MIN_M  (default 5 m)   -> ignore artefacts trop serrés
    #   RS3_R_VISU_MAX_M  (default 150 m) -> n'afficher en rouge que R_min <= ce seuil
    R_MIN = float(os.environ.get("RS3_RADIUS_MIN_M", "5"))
    R_VISU_MAX = float(os.environ.get("RS3_R_VISU_MAX_M", "150"))
    # radius_min peut contenir inf -> remplacer pour le masque
    r_series = edges_stats["radius_min"].replace([np.inf, -np.inf], np.nan)
    mask_visu = (r_series >= R_MIN) & (r_series <= R_VISU_MAX)

    # Couche 'candidats' (segments respectant le filtre de rayon), en WGS84
    try:
        candidates = edges.loc[mask_visu.values].copy()
    except Exception:
        # fallback alignement par position
        import numpy as _np

        candidates = edges.iloc[_np.where(mask_visu.values)[0]].copy()

    buf = buffer_m(edges, meters=street_buffer_m)

    # Clothoïdes (option) + filtrage visuel sur rayon
    fits_geom = []
    if fit_clothoid:
        from shapely.geometry import LineString

        for i, geom in enumerate(edges_m.geometry):
            if not isinstance(geom, LineString):
                continue
            # Appliquer d'abord le filtre rayon pour éviter des fits inutiles
            if not bool(mask_visu.iloc[i]):
                continue
            fit = fit_local_clothoid(geom, step_m=clothoid_step_m, window_m=clothoid_window_m)
            if fit.r2 >= clothoid_r2_min:
                # on visualise la portion [s_start, s_end] — proxy simple: garder tout le segment
                fits_geom.append(geom)

    clothoid_gdf = gpd.GeoDataFrame({"r2_ok": [True] * len(fits_geom)}, geometry=fits_geom, crs=3857) if fits_geom else gpd.GeoDataFrame(columns=["r2_ok", "geometry"], crs=3857)

    # Log résumé des filtrages
    tot = len(edges_m)
    n_visu = int(mask_visu.sum())
    n_fit = len(fits_geom)
    print(f"[linkedin.map] segments={tot} | R_min∈[{R_MIN:.0f}m;{R_VISU_MAX:.0f}m] -> {n_visu} candidats | clothoïdes retenues (R²≥{clothoid_r2_min}): {n_fit}")

    # Options de style passées à plot_map via variables d'environnement
    plot_kwargs = {}
    if os.environ.get("RS3_LEGEND_LOC"):
        plot_kwargs["legend_loc"] = os.environ["RS3_LEGEND_LOC"]
    if os.environ.get("RS3_EDGE_COLOR"):
        plot_kwargs["edge_color"] = os.environ["RS3_EDGE_COLOR"]
    if os.environ.get("RS3_CAND_COLOR"):
        plot_kwargs["cand_color"] = os.environ["RS3_CAND_COLOR"]
    if os.environ.get("RS3_CLOTHOID_COLOR"):
        plot_kwargs["clothoid_color"] = os.environ["RS3_CLOTHOID_COLOR"]
    if os.environ.get("RS3_BUFFER_ALPHA"):
        try:
            plot_kwargs["buffer_alpha"] = float(os.environ["RS3_BUFFER_ALPHA"])
        except Exception:
            pass

    out_png = str(od / "linkedin_map.png")
    plot_map(
        out_png=out_png,
        edges=edges,
        buffer=buf,
        candidates=candidates,
        samples=None,  # tu peux alimenter avec des points si besoin
        clothoid_fits=clothoid_gdf.to_crs(4326) if len(clothoid_gdf) else None,
        title=f"Carte — {street or 'sélection'} [{src.upper()}]",
        **plot_kwargs,
    )
    print(f"✅ Carte enregistrée: {out_png}")


def run_distrib(out_dir: str, bbox: Tuple[float, float, float, float]):
    od = ensure_out_dir(out_dir)
    minx, miny, maxx, maxy = bbox
    streets = load_streets_from_osm((minx, miny, maxx, maxy), street=None)
    edges = streets.explode(index_parts=False).reset_index(drop=True)
    edges_m = _to_m(edges)
    edges_stats = annotate_curvature_on_gdf(edges_m, step_m=5.0)

    out_png = str(od / "linkedin_distrib.png")
    plot_distributions(out_png, edges_stats.drop(columns="geometry"))
    print(f"✅ Distributions enregistrées: {out_png}")
