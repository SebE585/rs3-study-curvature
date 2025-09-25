from typing import Optional, Tuple

from rs3_study_curvature.data.io import ensure_out_dir, write_parquet, write_geojson
from rs3_study_curvature.data.streets import load_streets_from_osm, buffer_m, explode_to_lines
from rs3_study_curvature.geometry.curvature import annotate_curvature_on_gdf
from rs3_study_curvature.viz.map_plot import plot_map
from rs3_study_curvature.viz.distrib_plot import plot_distributions


def run_analysis(
    out_dir: str,
    bbox: Tuple[float, float, float, float],
    street: Optional[str],
    street_buffer_m: float,
):
    """
    Workflow Romilly — générique et réutilisable pour n'importe quelle ville/rue.
    Produit: edges.geojson, edges_stats.parquet, carte.png, distrib.png
    """
    od = ensure_out_dir(out_dir)
    minx, miny, maxx, maxy = bbox

    streets = load_streets_from_osm((minx, miny, maxx, maxy), street=street)
    edges = explode_to_lines(streets)
    edges_m = edges.to_crs(3857)

    stats = annotate_curvature_on_gdf(edges_m, step_m=5.0)
    write_parquet(stats.drop(columns="geometry"), str(od / "edges_stats.parquet"))
    write_geojson(edges, str(od / "edges.geojson"))

    # Carte
    buf = buffer_m(edges, meters=street_buffer_m)
    out_map = str(od / "carte.png")
    plot_map(out_map, edges=edges, buffer=buf, samples=None, clothoid_fits=None, title=f"Romilly — {street or 'sélection'}")
    # Distrib
    out_distrib = str(od / "distrib.png")
    plot_distributions(out_distrib, stats.drop(columns="geometry"), title="Romilly — distributions")

    print(f"✅ Analyse Romilly — terminé.\n - {out_map}\n - {out_distrib}\n - {od/'edges.geojson'}\n - {od/'edges_stats.parquet'}")
