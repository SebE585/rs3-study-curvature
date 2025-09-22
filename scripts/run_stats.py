# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import os
import time
from typing import List
import yaml
import pandas as pd
import numpy as np
import math

from rs3_study_curvature.io_utils import load_pair, ensure_numeric_columns, dropna_both
from rs3_study_curvature.stats_utils import summarize_metric, results_to_df

def _ensure_dir(p: str):
    os.makedirs(p, exist_ok=True)


# --- Helper: resolve metric column, optionally derive radius from curvature ---
def resolve_metric_series(df: pd.DataFrame, metric: str) -> pd.Series | None:
    """Return a numeric Series for the requested metric.
    - If the column exists: return it coerced to numeric.
    - If metric == 'radius_m' and 'curvature' exists: derive radius = 1/|curvature| (avoid div by 0).
    - If metric == 'curvature' and 'radius_m' exists: derive curvature = 1/radius_m (sign unknown; use positive).
    - Otherwise: return None.
    """
    if metric in df.columns:
        return pd.to_numeric(df[metric], errors="coerce")

    # Derive radius from curvature if needed
    if metric == "radius_m" and "curvature" in df.columns:
        curv = pd.to_numeric(df["curvature"], errors="coerce")
        # radius = 1/|curvature|; handle zeros/NaN
        with np.errstate(divide='ignore', invalid='ignore'):
            rad = 1.0 / np.abs(curv.to_numpy())
        rad[~np.isfinite(rad)] = np.nan
        return pd.Series(rad, index=df.index, name="radius_m")

    # Derive curvature from radius if needed
    if metric == "curvature" and "radius_m" in df.columns:
        rad = pd.to_numeric(df["radius_m"], errors="coerce").to_numpy()
        with np.errstate(divide='ignore', invalid='ignore'):
            curv = 1.0 / rad
        curv[~np.isfinite(curv)] = np.nan
        return pd.Series(curv, index=df.index, name="curvature")

    return None

def main():
    parser = argparse.ArgumentParser(description="OSM vs BD TOPO — Tests statistiques globaux")
    parser.add_argument("--config", required=True, help="YAML de configuration")
    args = parser.parse_args()

    with open(args.config, "r") as f:
        cfg = yaml.safe_load(f)

    osm_path = cfg["inputs"]["osm"]
    bd_path  = cfg["inputs"]["bdtopo"]
    metrics  = [m["name"] for m in cfg["metrics"]]
    # labels are not needed for stats computation; plotting script uses them

    out_root   = cfg["outputs"]["root"]
    out_stats  = cfg["outputs"]["stats_dir"]
    _ensure_dir(out_root); _ensure_dir(out_stats)

    osm, bd = load_pair(osm_path, bd_path)
    osm = ensure_numeric_columns(osm, metrics)
    bd  = ensure_numeric_columns(bd, metrics)

    results = []
    for m in metrics:
        # Resolve/derive metric columns gracefully (supports radius_m from curvature)
        s_osm = resolve_metric_series(osm, m)
        s_bd  = resolve_metric_series(bd, m)
        if s_osm is None or s_bd is None:
            missing_side = "OSM" if s_osm is None else "BDTOPO"
            print(
                f"[SKIP] Colonne manquante pour '{m}' côté {missing_side}. "
                "(Astuce: 'radius_m' est dérivé de 'curvature' et inversement si l'un des deux existe.)"
            )
            continue

        a, b = dropna_both(s_osm, s_bd)
        a = a.to_numpy()
        b = b.to_numpy()
        if len(a) < 2 or len(b) < 2:
            print(f"[WARN] Trop peu de données pour {m} (OSM={len(a)}, BD={len(b)}).")
            continue
        res = summarize_metric(m, a, b)
        results.append(res)

    if not results:
        print("Aucun résultat : vérifie les colonnes/chemins.")
        return

    df = results_to_df(results)
    ts = time.strftime("%Y%m%d_%H%M%S")
    out_csv = os.path.join(out_stats, f"global_tests_{ts}.csv")
    df.to_csv(out_csv, index=False)
    print(f"✅ Tests enregistrés → {out_csv}")

    # Joli aperçu console
    with pd.option_context("display.max_columns", None, "display.width", 140):
        print(df)

if __name__ == "__main__":
    main()