import typer
from pathlib import Path
from rs3_study_curvature.analysis.report import build_report

app = typer.Typer()


@app.command()
def curves(config: Path, out_md: Path):
    build_report(config, out_md)
