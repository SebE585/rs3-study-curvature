# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse, os, time, pandas as pd

def main():
    ap = argparse.ArgumentParser(description="Rapport Markdown — courbure/virages")
    ap.add_argument("--kpis", required=False, help="CSV KPIs (out/stats/curve_kpis.csv)")
    ap.add_argument("--plots-dir", required=False, help="répertoire des figures (out/plots/curves_*)")
    ap.add_argument("--docs-rel", default=None, help="racine relative pour les images côté docs/")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    lines = ["# Courbure — Analyse des virages",
             "",
             "Ce rapport se concentre sur les courbes détectées (séquences à forte courbure/faible rayon) et leur comparaison OSM vs BD TOPO.",
             ""]

    if args.kpis and os.path.exists(args.kpis):
        df = pd.read_csv(args.kpis, index_col=0)
        lines += ["## Indicateurs clés (KPIs)", "", df.to_markdown(), ""]
    else:
        lines += ["## Indicateurs clés (KPIs)", "", "_KPIs non trouvés — lancez `make curve-stats`._", ""]

    if args.plots_dir and os.path.isdir(args.plots_dir):
        rel = args.plots_dir
        if args.docs_rel:
            # réécrire le préfixe vers docs/
            base = os.path.basename(args.plots_dir.rstrip("/"))
            rel = os.path.join(args.docs_rel.rstrip("/"), base)
        lines += ["## Figures", ""]
        lines += [f"![Profil moyen de courbure]({rel}/mean_kappa_profile.png)", ""]
    else:
        lines += ["## Figures", "", "_Aucune figure détectée — lancez `make curve-profiles`._", ""]

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"✅ Rapport courbure → {args.out}")

if __name__ == "__main__":
    main()