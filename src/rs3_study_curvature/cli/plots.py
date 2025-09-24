import typer
from pathlib import Path
from rs3_study_curvature.viz.plots import dist_plots, class_plots, kappa_profiles

app = typer.Typer()


@app.command()
def distributions(config: Path):
    dist_plots(config)


@app.command()
def by_class(config: Path):
    class_plots(config)


@app.command()
def profiles(config: Path):
    kappa_profiles(config)
