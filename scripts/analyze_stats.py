#!/usr/bin/env python3
"""
Analyse des statistiques de courbure et génération d'un résumé Markdown.
"""

import numpy as np
import pandas as pd
from pathlib import Path
import os


def main():
    inp = Path("out/plots/linkedin/edges_stats.parquet")
    outp = Path("out/stats/summary.md")

    if not inp.exists():
        raise SystemExit(
            f"[analyze-stats] Missing {inp}. "
            "Run 'make linkedin-map' first to generate the stats file."
        )

    df = pd.read_parquet(inp)

    # Optional clipping thresholds (env overrides)
    R_MIN = float(os.environ.get("RS3_RADIUS_MIN_M", "5"))      # ignore unrealistically tight radii (<5 m)
    R_MAX = float(os.environ.get("RS3_RADIUS_CLIP_M", "5000"))  # clip very large radii (>5 km)

    def safe(x: pd.Series) -> pd.Series:
        return x.replace([float("inf"), float("-inf")], np.nan)

    r = safe(df["radius_min"]).dropna()
    r_raw = r.copy()
    r = r[(r >= R_MIN) & (r <= R_MAX)]
    kmax = safe(df["kappa_max"]).dropna()
    kmean = safe(df["kappa_mean"]).dropna()

    outp.parent.mkdir(parents=True, exist_ok=True)
    with outp.open("w", encoding="utf-8") as f:
        f.write("# Résumé des statistiques de courbure\n\n")

        f.write("## Rayon minimal (m)\n")
        f.write(f"(filtre: {R_MIN:.0f} m ≤ R ≤ {R_MAX/1000:.1f} km) — n_brut = {len(r_raw)}, n_filtré = {len(r)}\n")
        if len(r):
            f.write(
                f"- min = {float(np.min(r)):.3f}\n"
                f"- médiane = {float(np.median(r)):.3f}\n"
                f"- p90 = {float(np.percentile(r, 90)):.3f}\n\n"
            )
        else:
            f.write("- Aucune valeur dans l'intervalle\n\n")

        f.write("## κ max (1/m)\n")
        if len(kmax):
            f.write(
                f"- n = {len(kmax)}\n"
                f"- médiane = {float(np.median(kmax)):.6f}\n"
                f"- p90 = {float(np.percentile(kmax, 90)):.6f}\n\n"
            )
        else:
            f.write("- Aucune valeur disponible\n\n")

        f.write("## κ moyen (1/m)\n")
        if len(kmean):
            f.write(
                f"- n = {len(kmean)}\n"
                f"- médiane = {float(np.median(kmean)):.6f}\n"
                f"- p90 = {float(np.percentile(kmean, 90)):.6f}\n\n"
            )
        else:
            f.write("- Aucune valeur disponible\n\n")

    print(f"[analyze-stats] Écrit → {outp}")


if __name__ == "__main__":
    main()
