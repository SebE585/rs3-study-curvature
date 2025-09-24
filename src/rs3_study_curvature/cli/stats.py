import typer
from pathlib import Path
from rs3_study_curvature.analysis.stats import run_stats_by_class, run_global_stats

app = typer.Typer()


@app.command()
def global_(config: Path):
    run_global_stats(config)


@app.command()
def by_class(config: Path):
    run_stats_by_class(config)
