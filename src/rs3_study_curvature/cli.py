"""
CLI unifiée (Typer) — conserve aussi la compat ascendante via rs3_study_curvature.viz.linkedin
Exemples:
  python -m rs3_study_curvature.cli linkedin-map \
    --out-dir out/plots/linkedin \
    --bbox 1.22 49.30 1.30 49.36 \
    --street "Rue Blingue" --street-buffer-m 40 \
    --plot-centroids --fit-clothoid \
    --clothoid-step-m 8 --clothoid-window-m 60 --clothoid-r2-min 0.7 \
    --legend-loc upper left \
    --edge-color '#cccccc' --cand-color '#1f78b4' --clothoid-color '#e31a1c'

  python -m rs3_study_curvature.cli linkedin-distrib \
    --out-dir out/plots/linkedin \
    --bbox 1.22 49.30 1.30 49.36
"""

from typing import Optional, Tuple
import typer
import os

from rs3_study_curvature.workflows import linkedin as wf_linkedin
from rs3_study_curvature.workflows import romilly as wf_romilly

app = typer.Typer(add_completion=False)

BBox = Tuple[float, float, float, float]


@app.command("linkedin-map")
def linkedin_map(
    out_dir: str = typer.Option(..., help="Dossier de sortie (PNG/GeoJSON/Parquet)"),
    minx: float = typer.Argument(..., help="BBox minx miny maxx maxy (lon/lat WGS84)"),
    miny: float = typer.Argument(...),
    maxx: float = typer.Argument(...),
    maxy: float = typer.Argument(...),
    street: Optional[str] = typer.Option(None, help="Nom de rue (filtre contient)"),
    street_buffer_m: float = typer.Option(40, help="Buffer autour de la rue (m)"),
    plot_centroids: bool = typer.Option(False, help="Afficher les centroïdes/échantillons"),
    fit_clothoid: bool = typer.Option(False, help="Ajuster des clothoïdes"),
    clothoid_step_m: float = typer.Option(8.0, help="Pas d'échantillonnage s (m)"),
    clothoid_window_m: float = typer.Option(60.0, help="Fenêtre locale (m)"),
    clothoid_r2_min: float = typer.Option(0.7, help="Seuil R² minimal des fits"),
    legend_loc: Optional[str] = typer.Option(None, help="Position de la légende Matplotlib (ex: 'lower right', 'upper left')"),
    edge_color: Optional[str] = typer.Option(None, help="Couleur du réseau (hex ex: '#B0B0B0')"),
    cand_color: Optional[str] = typer.Option(None, help="Couleur des candidats (hex ex: '#1f77b4')"),
    clothoid_color: Optional[str] = typer.Option(None, help="Couleur des clothoïdes (hex ex: '#d62728')"),
    buffer_alpha: Optional[float] = typer.Option(None, help="Opacité du buffer [0-1]"),
):
    bbox: BBox = (minx, miny, maxx, maxy)
    # Propager d'éventuels styles vers le workflow via variables d'environnement
    if legend_loc is not None:
        os.environ["RS3_LEGEND_LOC"] = str(legend_loc)
    if edge_color is not None:
        os.environ["RS3_EDGE_COLOR"] = str(edge_color)
    if cand_color is not None:
        os.environ["RS3_CAND_COLOR"] = str(cand_color)
    if clothoid_color is not None:
        os.environ["RS3_CLOTHOID_COLOR"] = str(clothoid_color)
    if buffer_alpha is not None:
        os.environ["RS3_BUFFER_ALPHA"] = str(buffer_alpha)
    wf_linkedin.run_map(
        out_dir=out_dir,
        bbox=bbox,
        street=street,
        street_buffer_m=street_buffer_m,
        plot_centroids=plot_centroids,
        fit_clothoid=fit_clothoid,
        clothoid_step_m=clothoid_step_m,
        clothoid_window_m=clothoid_window_m,
        clothoid_r2_min=clothoid_r2_min,
    )


@app.command("linkedin-distrib")
def linkedin_distrib(
    out_dir: str = typer.Option(..., help="Dossier de sortie"),
    minx: float = typer.Argument(..., help="BBox minx miny maxx maxy"),
    miny: float = typer.Argument(...),
    maxx: float = typer.Argument(...),
    maxy: float = typer.Argument(...),
):
    bbox: BBox = (minx, miny, maxx, maxy)
    wf_linkedin.run_distrib(out_dir=out_dir, bbox=bbox)


@app.command("romilly-analyze")
def romilly_analyze(
    out_dir: str = typer.Option(..., help="Dossier de sortie"),
    minx: float = typer.Argument(..., help="BBox minx miny maxx maxy"),
    miny: float = typer.Argument(...),
    maxx: float = typer.Argument(...),
    maxy: float = typer.Argument(...),
    street: Optional[str] = typer.Option(None, help="Nom de rue"),
    street_buffer_m: float = typer.Option(40, help="Buffer m"),
):
    bbox: BBox = (minx, miny, maxx, maxy)
    wf_romilly.run_analysis(out_dir=out_dir, bbox=bbox, street=street, street_buffer_m=street_buffer_m)


if __name__ == "__main__":
    app()
