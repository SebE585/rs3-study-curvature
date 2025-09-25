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


def _normalize_metrics(cfg: dict) -> list[dict]:
    """
    Accept either:
      - metrics: ["length_m", "curvature", ...]
      - metrics: [{"name": "length_m", "label": "Longueur (m)"}, ...]
    and return a list of dicts with keys "name" and "label".
    """
    raw = cfg.get("metrics", [])
    norm: list[dict] = []
    for m in raw:
        if isinstance(m, str):
            norm.append({"name": m, "label": m})
        elif isinstance(m, dict) and "name" in m:
            norm.append({"name": m["name"], "label": m.get("label", m["name"])})
    return norm


def _normalize_outputs(cfg: dict) -> tuple[str, str]:
    """
    Ensure outputs directories exist and return (out_root, out_plots).
    Fallbacks:
      out_root = "out"
      out_plots = os.path.join(out_root, "plots")
    """
    out_root = cfg.get("outputs", {}).get("root") or "out"
    out_plots = cfg.get("outputs", {}).get("plots_dir") or os.path.join(out_root, "plots")
    _ensure_dir(out_root)
    _ensure_dir(out_plots)
    return out_root, out_plots


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

    # Charge la configuration
    with open(args.config, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}

    # Normalisation des chemins de sortie (avec valeurs par défaut)
    out_root, out_plots = _normalize_outputs(cfg)

    # Paramètres de tracés (avec valeurs par défaut)
    bins = cfg.get("hist", {}).get("bins", "fd")
    kde = bool(cfg.get("kde", {}).get("enabled", True))
    dpi = int(cfg.get("fig", {}).get("dpi", 140))
    width = float(cfg.get("fig", {}).get("width", 9.0))
    height = float(cfg.get("fig", {}).get("height", 6.0))

    # Entrées
    inputs = cfg.get("inputs", {})
    osm_path = inputs.get("osm")
    bd_path = inputs.get("bdtopo")
    if not osm_path or not bd_path:
        raise SystemExit("⚠️  'inputs.osm' et 'inputs.bdtopo' doivent être définis dans le YAML.")

    # Liste des métriques (format souple)
    metrics = _normalize_metrics(cfg)
    if not metrics:
        raise SystemExit("⚠️  'metrics' est vide. Utilisez une liste de noms ou de {name,label}.")

    try:
        osm, bd = load_pair(osm_path, bd_path)
    except Exception as e:
        raise SystemExit(f"❌ Impossible de charger les données: {e}")

    metric_names = [m["name"] for m in metrics]
    labels = {m["name"]: m["label"] for m in metrics}

    # S'assure que les colonnes numériques existantes sont au bon format
    osm = ensure_numeric_columns(osm, metric_names)
    bd = ensure_numeric_columns(bd, metric_names)

    ts = time.strftime("%Y%m%d_%H%M%S")
    out_dir_ts = os.path.join(out_plots, f"global_{ts}")
    _ensure_dir(out_dir_ts)

    for m in metric_names:
        # Résout la série métrique (gère le couplage radius_m ↔ curvature)
        s_osm = resolve_metric_series(osm, m)
        s_bd = resolve_metric_series(bd, m)
        if s_osm is None or s_bd is None:
            missing_side = "OSM" if s_osm is None else "BDTOPO"
            print(f"[SKIP] Colonne manquante pour '{m}' côté {missing_side}. " "(Astuce: 'radius_m' est dérivé de 'curvature' et inversement si l'un des deux existe.)")
            continue

        # DataFrames minimaux pour les fonctions de tracé
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
