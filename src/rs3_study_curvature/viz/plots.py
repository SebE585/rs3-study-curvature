# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import os
import time
import yaml
import pandas as pd
import numpy as np

from rs3_study_curvature.io import load_pair, ensure_numeric_columns
from rs3_study_curvature.viz.utils import plot_hist_kde, plot_box_violin


def dist_plots(config):  # type: ignore[unused-ignore]
    import sys

    sys.argv = ["plots.py", "--config", str(config)]
    main()


def class_plots(config):  # type: ignore[unused-ignore]
    from .plots_by_class import main as _main
    import sys

    sys.argv = ["plots_by_class.py", "--config", str(config)]
    _main()


def kappa_profiles(config):  # type: ignore[unused-ignore]
    from .profiles import main as _main
    import sys

    sys.argv = ["profiles.py", "--config", str(config)]
    _main()


def _ensure_dir(p: str):
    os.makedirs(p, exist_ok=True)


# --- Helper: resolve metric column, optionally derive radius/curvature ---
def resolve_metric_series(df: pd.DataFrame, metric: str) -> pd.Series | None:
    """Return a numeric Series for the requested metric.
    - If the column exists: return it coerced to numeric.
    - If metric == 'radius_m' and 'curvature' exists: derive radius = 1/|curvature| (avoid div by 0).
    - If metric == 'curvature' and 'radius_m' exists: derive curvature = 1/radius_m.
    - Otherwise: return None.
    """
    if metric in df.columns:
        return pd.to_numeric(df[metric], errors="coerce")

    if metric == "radius_m" and "curvature" in df.columns:
        curv = pd.to_numeric(df["curvature"], errors="coerce")
        with np.errstate(divide="ignore", invalid="ignore"):
            rad = 1.0 / np.abs(curv.to_numpy())
        rad[~np.isfinite(rad)] = np.nan
        return pd.Series(rad, index=df.index, name="radius_m")

    if metric == "curvature" and "radius_m" in df.columns:
        rad = pd.to_numeric(df["radius_m"], errors="coerce").to_numpy()
        with np.errstate(divide="ignore", invalid="ignore"):
            curv = 1.0 / rad
        curv[~np.isfinite(curv)] = np.nan
        return pd.Series(curv, index=df.index, name="curvature")

    return None


def main():
    parser = argparse.ArgumentParser(description="OSM vs BD TOPO — Distributions globales")
    parser.add_argument("--config", required=True, help="YAML de configuration")
    args = parser.parse_args()

    with open(args.config, "r") as f:
        cfg = yaml.safe_load(f)

    osm_path = cfg["inputs"]["osm"]
    bd_path = cfg["inputs"]["bdtopo"]
    metrics = cfg["metrics"]

    out_root = cfg["outputs"]["root"]
    out_plots = cfg["outputs"]["plots_dir"]
    _ensure_dir(out_root)
    _ensure_dir(out_plots)

    bins = cfg.get("hist", {}).get("bins", "fd")
    kde = bool(cfg.get("kde", {}).get("enabled", True))
    dpi = int(cfg.get("fig", {}).get("dpi", 140))
    width = float(cfg.get("fig", {}).get("width", 9.0))
    height = float(cfg.get("fig", {}).get("height", 6.0))

    osm, bd = load_pair(osm_path, bd_path)
    metric_names = [m["name"] for m in metrics]
    labels = {m["name"]: m.get("label", m["name"]) for m in metrics}
    osm = ensure_numeric_columns(osm, metric_names)
    bd = ensure_numeric_columns(bd, metric_names)

    ts = time.strftime("%Y%m%d_%H%M%S")
    out_dir_ts = os.path.join(out_plots, f"global_{ts}")
    _ensure_dir(out_dir_ts)

    for m in metric_names:
        # Resolve metric series (supports bidirectional derivation radius_m ↔ curvature)
        s_osm = resolve_metric_series(osm, m)
        s_bd = resolve_metric_series(bd, m)
        if s_osm is None or s_bd is None:
            missing_side = "OSM" if s_osm is None else "BDTOPO"
            print(
                f"[SKIP] Colonne manquante pour '{m}' côté {missing_side}. "
                "(Astuce: 'radius_m' est dérivé de 'curvature' et inversement si l'un des deux existe.)"
            )
            continue

        # Build minimal DataFrames with the resolved numeric series so that plot_utils works unchanged
        tmp_osm = pd.DataFrame({m: s_osm})
        tmp_bd = pd.DataFrame({m: s_bd})

        # Histogrammes + KDE
        out_hist = os.path.join(out_dir_ts, f"{m}__hist_kde.png")
        plot_hist_kde(
            tmp_osm,
            tmp_bd,
            m,
            "OSM",
            "BD TOPO",
            bins=bins,
            kde=kde,
            width=width,
            height=height,
            dpi=dpi,
            out_path=out_hist,
            xlabel=labels[m],
        )

        # Boxplot + Violin
        out_box = os.path.join(out_dir_ts, f"{m}__box.png")
        out_vio = os.path.join(out_dir_ts, f"{m}__violin.png")
        plot_box_violin(
            tmp_osm,
            tmp_bd,
            m,
            "OSM",
            "BD TOPO",
            width=width,
            height=height,
            dpi=dpi,
            out_path_box=out_box,
            out_path_violin=out_vio,
            xlabel=labels[m],
        )

    print(f"✅ Distributions exportées → {out_dir_ts}")


if __name__ == "__main__":
    main()
