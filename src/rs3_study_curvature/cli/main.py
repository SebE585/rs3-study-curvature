from __future__ import annotations
import typer
from . import compute, stats, report, plots

app = typer.Typer(add_completion=False, no_args_is_help=True)
app.add_typer(compute.app, name="compute", help="ETL: extraction κ/r, profils")
app.add_typer(stats.app, name="stats", help="Stats globales, par classes")
app.add_typer(report.app, name="report", help="Rapports Markdown/PDF")
app.add_typer(plots.app, name="plots", help="Distribution, profils, quantiles")

if __name__ == "__main__":
    app()
