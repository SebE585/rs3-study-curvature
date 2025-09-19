#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
compare_quick.py — comparatif rapide OSM vs BD TOPO à partir des fichiers segments *.parquet

- Lit deux fichiers parquet (pandas) : roadinfo_segments_osm.parquet et *_bdtopo.parquet
- Produit :
  - compare__summary_segments.csv : stats globales par source
  - compare__hist_length_m.png, compare__hist_radius_min_m.png, compare__hist_curv_mean_1perm.png
- Gestion robuste des NaN/Inf et coupe au 99e centile (configurable)
"""

from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def _finite_series(s: pd.Series) -> pd.Series:
    """Retourne uniquement les valeurs finies (ni NaN, ni ±inf)."""
    return s.replace([np.inf, -np.inf], np.nan).dropna()


def _robust_clip(s: pd.Series, q: float = 0.99) -> pd.Series:
    """Coupe la série au quantile q (par défaut 99e centile) après nettoyage."""
    s2 = _finite_series(s)
    if s2.empty:
        return s2
    upper = s2.quantile(q)
    return s2.clip(upper=upper)


def quick_summary(df: pd.DataFrame, name: str) -> dict:
    rmin = _finite_series(df["radius_min_m"])
    out = {
        "source": name,
        "n_segments": int(len(df)),
        "len_m_mean": float(df["length_m"].mean()),
        "len_m_median": float(df["length_m"].median()),
        "len_m_sum_km": float(df["length_m"].sum() / 1000.0),
        "rmin_p10": float(np.nanpercentile(rmin.values, 10)) if len(rmin) else np.nan,
        "rmin_p50": float(np.nanpercentile(rmin.values, 50)) if len(rmin) else np.nan,
        "rmin_p90": float(np.nanpercentile(rmin.values, 90)) if len(rmin) else np.nan,
        "curv_mean_med": float(_finite_series(df["curv_mean_1perm"]).median()),
    }
    return out


def make_hists(osm: pd.DataFrame, bd: pd.DataFrame, out_dir: Path, q: float = 0.99) -> None:
    plots = [
        ("length_m", "Longueur [m]"),
        ("radius_min_m", "Rayon minimal [m]"),
        ("curv_mean_1perm", "Courbure moyenne [1/m]"),
    ]
    for col, title in plots:
        osm_v = _robust_clip(osm[col], q=q)
        bd_v  = _robust_clip(bd[col], q=q)

        plt.figure()
        # NB: on ne fixe pas les couleurs (consigne matplotlib “ne pas forcer les couleurs”)
        osm_v.hist(bins=60, alpha=0.5, label="OSM")
        bd_v.hist(bins=60, alpha=0.5, label="BD TOPO")
        plt.title(f"{title} (clip {int(q*100)}e pct)")
        plt.legend()
        plt.tight_layout()
        png = out_dir / f"compare__hist_{col}.png"
        plt.savefig(png, dpi=150)
        plt.close()


def main():
    ap = argparse.ArgumentParser(description="Comparatif rapide OSM vs BD TOPO (segments).")
    ap.add_argument(
        "--in-dir",
        type=Path,
        default=Path("/Users/sebastien.edet/rs3-data/ref/roadinfo"),
        help="Dossier contenant les .parquet",
    )
    ap.add_argument("--osm-name", default="roadinfo_segments_osm.parquet")
    ap.add_argument("--bd-name",  default="roadinfo_segments_bdtopo.parquet")
    ap.add_argument("--q", type=float, default=0.99, help="Quantile de clipping pour les histogrammes (0-1).")
    args = ap.parse_args()

    out_dir = args.in_dir
    osm_pq = out_dir / args.osm_name
    bd_pq  = out_dir / args.bd_name

    if not osm_pq.exists():
        raise FileNotFoundError(f"Introuvable: {osm_pq}")
    if not bd_pq.exists():
        raise FileNotFoundError(f"Introuvable: {bd_pq}")

    # IMPORTANT : lire avec pandas (et pas geopandas) car les fichiers n’ont pas de meta geoparquet
    seg_osm = pd.read_parquet(osm_pq)
    seg_bd  = pd.read_parquet(bd_pq)

    # Récap global
    summary = pd.DataFrame([quick_summary(seg_osm, "osm"), quick_summary(seg_bd, "bdtopo")])
    csv_path = out_dir / "compare__summary_segments.csv"
    summary.to_csv(csv_path, index=False)
    print(summary)
    print("\nÉcrit:", csv_path)

    # Histogrammes robustes
    make_hists(seg_osm, seg_bd, out_dir=out_dir, q=args.q)
    print("PNG écrits dans:", out_dir)


if __name__ == "__main__":
    main()