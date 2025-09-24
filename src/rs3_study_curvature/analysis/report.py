# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
import os
from typing import Optional
import pandas as pd


def _generate_report(*, kpis: Optional[str] = None, plots_dir: Optional[str] = None, docs_rel: Optional[str] = None, out: str) -> None:
    """Core generator used by both argparse CLI and Typer wrapper.

    Parameters
    ----------
    kpis : str | None
        Path to a CSV file with KPIs (optional).
    plots_dir : str | None
        Directory containing figures (e.g. out/plots/curves_*). Optional.
    docs_rel : str | None
        If set, the images path is rewritten to be relative to the docs root (e.g. "docs").
    out : str
        Output Markdown file path (required).
    """
    lines = [
        "# Courbure — Analyse des virages",
        "",
        "Ce rapport se concentre sur les courbes détectées (séquences à forte courbure/faible rayon) et leur comparaison OSM vs BD TOPO.",
        "",
    ]

    if kpis and os.path.exists(kpis):
        df = pd.read_csv(kpis, index_col=0)
        lines += ["## Indicateurs clés (KPIs)", "", df.to_markdown(), ""]
    else:
        lines += [
            "## Indicateurs clés (KPIs)",
            "",
            "_KPIs non trouvés — lancez `make curve-stats`._",
            "",
        ]

    if plots_dir and os.path.isdir(plots_dir):
        rel = plots_dir
        if docs_rel:
            # réécrire le préfixe vers docs/
            base = os.path.basename(plots_dir.rstrip("/"))
            rel = os.path.join(docs_rel.rstrip("/"), base)
        lines += ["## Figures", ""]
        lines += [f"![Profil moyen de courbure]({rel}/mean_kappa_profile.png)", ""]
    else:
        lines += [
            "## Figures",
            "",
            "_Aucune figure détectée — lancez `make curve-profiles`._",
            "",
        ]

    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"✅ Rapport courbure → {out}")


def main():
    """Argparse entrypoint (kept for direct module execution)."""
    ap = argparse.ArgumentParser(description="Rapport Markdown — courbure/virages")
    # Accept --config for compatibility with callers, but it's unused here.
    ap.add_argument("--config", required=False, help="(optionnel) chemin du fichier config.yaml")
    ap.add_argument("--kpis", required=False, help="CSV KPIs (out/stats/curve_kpis.csv)")
    ap.add_argument(
        "--plots-dir",
        required=False,
        help="répertoire des figures (out/plots/curves_*)",
    )
    ap.add_argument("--docs-rel", default=None, help="racine relative pour les images côté docs/")
    ap.add_argument("--out", required=True, help="fichier Markdown de sortie")
    args = ap.parse_args()

    _generate_report(kpis=args.kpis, plots_dir=args.plots_dir, docs_rel=args.docs_rel, out=args.out)


def build_report(
    config: Optional[str] = None,
    out_md: Optional[str] = None,
    *,
    kpis: Optional[str] = None,
    plots_dir: Optional[str] = None,
    docs_rel: Optional[str] = None,
) -> None:
    """Wrapper utilisé par la CLI Typer (`cli/report.py`).

    On ne dépend pas du contenu de `config` ici, mais on accepte l'argument pour
    compatibilité avec la signature Typer actuelle. L'essentiel est `out_md`.
    """
    if not out_md:
        raise ValueError("'out_md' est requis pour écrire le rapport")
    _generate_report(kpis=kpis, plots_dir=plots_dir, docs_rel=docs_rel, out=str(out_md))


if __name__ == "__main__":
    main()
