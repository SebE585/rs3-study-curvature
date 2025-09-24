# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
import os
import time
import yaml
import pandas as pd
import numpy as np
from rs3_study_curvature.io_utils import load_pair, ensure_numeric_columns
from rs3_study_curvature.plot_utils import plot_hist_kde, plot_box_violin


def _ensure_dir(p: str):
    os.makedirs(p, exist_ok=True)


def _resolve_class_col(osm: pd.DataFrame, bd: pd.DataFrame, cfg: dict, cli_override: str | None) -> str:
    ordered: list[str] = []
    if cli_override:
        ordered.append(cli_override)
    elif cfg.get("class_column"):
        ordered.append(cfg["class_column"])
    ordered += cfg.get("class_column_candidates", [])
    defaults = ["class_norm", "highway", "class", "road_class", "fclass"]
    for d in defaults:
        if d not in ordered:
            ordered.append(d)
    for c in ordered:
        if c in osm.columns and c in bd.columns:
            return c
    raise SystemExit("Colonne de classe introuvable. Essayez --class-col ou définissez class_column/class_column_candidates dans le YAML.")


def resolve_metric_series(df: pd.DataFrame, metric: str) -> pd.Series | None:
    # Direct
    if metric in df.columns:
        return pd.to_numeric(df[metric], errors="coerce")
    # Aliases & derivations
    curvature_aliases = ["curvature", "curv_mean_1perm", "curv_mean", "kappa"]
    radius_aliases = ["radius_m", "radius_min_m", "radius_p85_m"]
    if metric == "curvature":
        for col in curvature_aliases:
            if col in df.columns:
                return pd.to_numeric(df[col], errors="coerce")
        for col in radius_aliases:
            if col in df.columns:
                rad = pd.to_numeric(df[col], errors="coerce").to_numpy()
                with np.errstate(divide="ignore", invalid="ignore"):
                    curv = 1.0 / rad
                curv[~np.isfinite(curv)] = np.nan
                return pd.Series(curv, index=df.index, name="curvature")
        return None
    if metric == "radius_m":
        for col in ["radius_m", "radius_min_m", "radius_p85_m"]:
            if col in df.columns:
                return pd.to_numeric(df[col], errors="coerce")
        for col in curvature_aliases:
            if col in df.columns:
                curv = pd.to_numeric(df[col], errors="coerce")
                with np.errstate(divide="ignore", invalid="ignore"):
                    rad = 1.0 / np.abs(curv.to_numpy())
                rad[~np.isfinite(rad)] = np.nan
                return pd.Series(rad, index=df.index, name="radius_m")
        return None
    return None


def main():
    ap = argparse.ArgumentParser(description="OSM vs BD TOPO — Distributions par classe")
    ap.add_argument("--config", required=True)
    ap.add_argument(
        "--class-col",
        default=None,
        help="nom de la colonne classe à utiliser (override)",
    )
    args = ap.parse_args()

    cfg = yaml.safe_load(open(args.config))
    metrics = cfg["metrics"]
    metric_names = [m["name"] for m in metrics]
    labels = {m["name"]: m.get("label", m["name"]) for m in metrics}

    bins = cfg.get("hist", {}).get("bins", "fd")
    kde = bool(cfg.get("kde", {}).get("enabled", True))
    dpi = int(cfg.get("fig", {}).get("dpi", 140))
    width = float(cfg.get("fig", {}).get("width", 9.0))
    height = float(cfg.get("fig", {}).get("height", 6.0))

    osm, bd = load_pair(cfg["inputs"]["osm"], cfg["inputs"]["bdtopo"])
    class_col = _resolve_class_col(osm, bd, cfg, args.class_col)
    print(f"[by-class] Utilisation de la colonne de classe: {class_col}")

    osm = ensure_numeric_columns(osm, metric_names)
    bd = ensure_numeric_columns(bd, metric_names)

    classes = sorted(list(set(pd.Series(osm[class_col]).dropna().unique()).intersection(set(pd.Series(bd[class_col]).dropna().unique()))))

    ts = time.strftime("%Y%m%d_%H%M%S")
    out_root = cfg["outputs"]["plots_dir"]
    out_dir_root = os.path.join(out_root, f"by_class_{ts}")
    _ensure_dir(out_dir_root)

    for c in classes:
        osm_c = osm[osm[class_col] == c]
        bd_c = bd[bd[class_col] == c]
        out_dir = os.path.join(out_dir_root, c)
        _ensure_dir(out_dir)

        for m in metric_names:
            s_osm = resolve_metric_series(osm_c, m)
            s_bd = resolve_metric_series(bd_c, m)
            if s_osm is None or s_bd is None:
                print(f"[SKIP {c}] '{m}' absent (ou non dérivable) d’un côté.")
                continue
            tmp_osm = pd.DataFrame({m: pd.to_numeric(s_osm, errors="coerce")})
            tmp_bd = pd.DataFrame({m: pd.to_numeric(s_bd, errors="coerce")})

            out_hist = os.path.join(out_dir, f"{m}__hist_kde.png")
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

            out_box = os.path.join(out_dir, f"{m}__box.png")
            out_vio = os.path.join(out_dir, f"{m}__violin.png")
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

    print(f"✅ Distributions par classe exportées → {out_dir_root}")


if __name__ == "__main__":
    main()
