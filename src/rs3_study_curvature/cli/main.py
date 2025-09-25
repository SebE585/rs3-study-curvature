from __future__ import annotations
import typer
from typing import Any, TYPE_CHECKING

from rs3_study_curvature.workflows import linkedin, romilly

app: typer.Typer = typer.Typer(add_completion=False, no_args_is_help=True)

# Pour la vérification statique, on déclare des alias optionnels
if TYPE_CHECKING:  # utilisé uniquement par mypy
    from . import compute as _compute
    from . import stats as _stats
    from . import report as _report
    from . import plots as _plots
else:
    _compute = _stats = _report = _plots = None  # type: ignore[assignment]


def _safe_subapp(mod: Any) -> typer.Typer:
    """Retourne mod.app s'il existe et est un Typer, sinon un Typer vide.
    Cette fonction encapsule getattr + cast pour satisfaire mypy.
    """
    candidate: Any = getattr(mod, "app", None)
    if isinstance(candidate, typer.Typer):
        return candidate
    return typer.Typer()


# Essaye d'importer les sous-modules optionnels et ajoute leurs sous-commandes
try:
    from . import compute as _compute  # type: ignore[no-redef]
except Exception:
    _compute = None  # type: ignore[assignment]

try:
    from . import stats as _stats  # type: ignore[no-redef]
except Exception:
    _stats = None  # type: ignore[assignment]

try:
    from . import report as _report  # type: ignore[no-redef]
except Exception:
    _report = None  # type: ignore[assignment]

try:
    from . import plots as _plots  # type: ignore[no-redef]
except Exception:
    _plots = None  # type: ignore[assignment]

if _compute is not None:
    app.add_typer(_safe_subapp(_compute), name="compute", help="ETL: extraction κ/r, profils")
if _stats is not None:
    app.add_typer(_safe_subapp(_stats), name="stats", help="Stats globales, par classes")
if _report is not None:
    app.add_typer(_safe_subapp(_report), name="report", help="Rapports Markdown/PDF")
if _plots is not None:
    app.add_typer(_safe_subapp(_plots), name="plots", help="Distribution, profils, quantiles")

# Sous-commandes principales (présentes dans le repo)
app.add_typer(_safe_subapp(linkedin), name="linkedin", help="Cartes et distributions LinkedIn")
app.add_typer(_safe_subapp(romilly), name="romilly", help="Cartes et distributions Romilly")


if __name__ == "__main__":
    app()
