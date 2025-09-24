#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Résumé global OSM vs BD TOPO :
- statistiques agrégées
- histogrammes (clippés au quantile q)
- gestion des infinis optionnelle pour radius_min_m
"""

from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def _read_parquet(path: Path) -> pd.DataFrame:
    # On lit comme Pandas (non-Geo) car les Parquet générés ne portent pas toujours les meta GeoPandas
    return pd.read_parquet(path)


def _fmt_km(x: float) -> float:
    return float(x) / 1000.0


def quick_summary(df: pd.DataFrame, name: str, drop_inf: bool) -> dict:
    rmin = df["radius_min_m"]
    if drop_inf:
        rmin = rmin.replace([np.inf, -np.inf], np.nan).dropna()

    out = {
        "source": name,
        "n_segments": int(len(df)),
        "len_m_mean": float(df["length_m"].mean()),
        "len_m_median": float(df["length_m"].median()),
        "len_m_sum_km": _fmt_km(float(df["length_m"].sum())),
        "rmin_p10": float(np.nanpercentile(rmin, 10)) if len(rmin) else np.nan,
        "rmin_p50": float(np.nanpercentile(rmin, 50)) if len(rmin) else np.nan,
        "rmin_p90": float(np.nanpercentile(rmin, 90)) if len(rmin) else np.nan,
        "curv_mean_med": float(df["curv_mean_1perm"].median()),
    }
    return out


def write_hists(osm: pd.DataFrame, bd: pd.DataFrame, out_dir: Path, q: float, drop_inf: bool) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    def _clip_series(s: pd.Series, q: float, drop_inf: bool) -> pd.Series:
        ss = s.copy()
        if drop_inf:
            ss = ss.replace([np.inf, -np.inf], np.nan)
        upper = ss.quantile(q)
        return ss.clip(upper=upper)

    for col in ["length_m", "radius_min_m", "curv_mean_1perm"]:
        plt.figure()
        _clip_series(osm[col], q, drop_inf).dropna().hist(bins=60, alpha=0.5, label="OSM")
        _clip_series(bd[col], q, drop_inf).dropna().hist(bins=60, alpha=0.5, label="BDTOPO")
        plt.title(col)
        plt.legend()
        plt.tight_layout()
        png = out_dir / f"compare__hist_{col}.png"
        plt.savefig(png, dpi=150)
        plt.close()


def main():
    ap = argparse.ArgumentParser(description="Résumé rapide OSM vs BDTOPO (tables Parquet non-geo)")
    ap.add_argument("--in-dir", type=Path, default=Path("ref/roadinfo"), help="Dossier des sorties")
    ap.add_argument("--osm-name", default="roadinfo_segments_osm.parquet")
    ap.add_argument("--bd-name", default="roadinfo_segments_bdtopo.parquet")
    ap.add_argument(
        "--q",
        type=float,
        default=0.99,
        help="Quantile de clipping pour les histogrammes",
    )
    ap.add_argument("--drop-inf", action="store_true", help="Ignorer ±inf pour radius_min_m")
    ap.add_argument(
        "--out-summary",
        default="compare__summary_segments.csv",
        help="Nom du CSV résumé",
    )
    args = ap.parse_args()

    in_dir = args.in_dir
    out_summary = in_dir / args.out_summary

    seg_osm = _read_parquet(in_dir / args.osm_name)
    seg_bd = _read_parquet(in_dir / args.bd_name)

    summary = pd.DataFrame(
        [
            quick_summary(seg_osm, "osm", args.drop_inf),
            quick_summary(seg_bd, "bdtopo", args.drop_inf),
        ]
    )
    print(summary)
    summary.to_csv(out_summary, index=False)
    print("\nÉcrit:", out_summary)

    write_hists(seg_osm, seg_bd, in_dir, q=args.q, drop_inf=args.drop_inf)
    print("PNG écrits dans:", in_dir)


if __name__ == "__main__":
    main()
