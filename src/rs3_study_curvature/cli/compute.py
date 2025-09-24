import typer
from pathlib import Path
from rs3_study_curvature.etl.compute_curvature import build_from_config

app = typer.Typer()


@app.command()
def from_config(config: Path):
    """Construit les courbures/profils depuis un YAML."""
    build_from_config(config)
