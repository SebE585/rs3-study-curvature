# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
import os
import time
import yaml
import pandas as pd
import numpy as np
import re
import unicodedata
from typing import Dict, Tuple

# -----------------------------
# I/O fallbacks (robust loaders)
# -----------------------------
try:
    from rs3_study_curvature.io_utils import load_pair, ensure_numeric_columns  # type: ignore
except Exception:  # pragma: no cover - fallback if module path changed/missing
    import warnings

    try:
        import geopandas as gpd  # type: ignore
    except Exception:  # pragma: no cover
        gpd = None  # type: ignore

    def _read_any(path: str) -> pd.DataFrame:
        """Best-effort reader for tabular/geo files -> pandas.DataFrame."""
        lower = path.lower()
        if lower.endswith((".parquet", ".pq")):
            return pd.read_parquet(path)
        if lower.endswith(".feather"):
            return pd.read_feather(path)
        if lower.endswith((".csv", ".tsv")):
            sep = "," if lower.endswith(".csv") else "\t"
            return pd.read_csv(path, sep=sep)
        if lower.endswith((".gpkg", ".geojson", ".json", ".shp")) and gpd is not None:
            df = gpd.read_file(path)
            if "geometry" in df.columns:
                df = df.drop(columns=["geometry"])  # type: ignore[assignment]
            return pd.DataFrame(df)
        warnings.warn(f"Format de fichier non reconnu pour: {path}. Tentative avec pandas.read_table().")
        return pd.read_table(path)

    def load_pair(osm_path: str, bd_path: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        return _read_any(osm_path), _read_any(bd_path)

    def ensure_numeric_columns(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
        for c in columns:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors="coerce")
        return df


# ---------------------------------
# Plot helpers (with safe fallbacks)
# ---------------------------------
try:
    from .plot_utils import plot_hist_kde, plot_box_violin  # type: ignore
except Exception:
    try:
        from rs3_study_curvature.viz.plot_utils import plot_hist_kde, plot_box_violin  # type: ignore
    except Exception:
        import matplotlib.pyplot as plt  # type: ignore

        def plot_hist_kde(
            df_osm: pd.DataFrame,
            df_bd: pd.DataFrame,
            col: str,
            label_osm: str,
            label_bd: str,
            *,
            bins: int | str = "fd",
            kde: bool = True,  # kept for API compat, ignored here
            width: float = 9.0,
            height: float = 6.0,
            dpi: int = 140,
            out_path: str | None = None,
            xlabel: str | None = None,
        ) -> None:
            s1 = pd.to_numeric(df_osm[col], errors="coerce").dropna()
            s2 = pd.to_numeric(df_bd[col], errors="coerce").dropna()
            fig = plt.figure(figsize=(width, height), dpi=dpi)
            ax = fig.gca()
            ax.hist(s1, bins=bins, alpha=0.5, density=True, label=label_osm)
            ax.hist(s2, bins=bins, alpha=0.5, density=True, label=label_bd)
            ax.set_xlabel(xlabel or col)
            ax.set_ylabel("Density")
            ax.legend()
            fig.tight_layout()
            if out_path:
                fig.savefig(out_path)
                plt.close(fig)

        def plot_box_violin(
            df_osm: pd.DataFrame,
            df_bd: pd.DataFrame,
            col: str,
            label_osm: str,
            label_bd: str,
            *,
            width: float = 9.0,
            height: float = 6.0,
            dpi: int = 140,
            out_path_box: str | None = None,
            out_path_violin: str | None = None,
            xlabel: str | None = None,
        ) -> None:
            s1 = pd.to_numeric(df_osm[col], errors="coerce").dropna()
            s2 = pd.to_numeric(df_bd[col], errors="coerce").dropna()

            fig_box = plt.figure(figsize=(width, height), dpi=dpi)
            axb = fig_box.gca()
            axb.boxplot([s1, s2], labels=[label_osm, label_bd], showfliers=False)
            axb.set_xlabel(xlabel or col)
            axb.set_ylabel(col)
            fig_box.tight_layout()
            if out_path_box:
                fig_box.savefig(out_path_box)
                plt.close(fig_box)

            fig_v = plt.figure(figsize=(width, height), dpi=dpi)
            axv = fig_v.gca()
            axv.violinplot([s1, s2], showmeans=True, showmedians=True)
            axv.set_xticks([1, 2], [label_osm, label_bd])
            axv.set_xlabel(xlabel or col)
            axv.set_ylabel(col)
            fig_v.tight_layout()
            if out_path_violin:
                fig_v.savefig(out_path_violin)
                plt.close(fig_v)


# -----------------------
# Utils: files & labels
# -----------------------


def _ensure_dir(p: str) -> None:
    os.makedirs(p, exist_ok=True)


def _slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^A-Za-z0-9_.\-]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("._")
    return value or "NA"


def _normalize_label(v: str) -> str:
    s = str(v)
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    s = s.lower()
    s = s.replace("/", "_").replace("-", "_").replace(" ", "_")
    s = re.sub(r"_+", "_", s).strip("_")
    return s


def _map_classes(series: pd.Series, mapping: Dict[str, str] | None) -> pd.Series:
    if not mapping:
        return series
    # mapping keys are expected in normalized form
    return series.map(lambda x: mapping.get(x, x))


# -----------------------
# Metrics resolution
# -----------------------


def resolve_metric_series(df: pd.DataFrame, metric: str) -> pd.Series | None:
    if metric in df.columns:
        return pd.to_numeric(df[metric], errors="coerce")
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


# -----------------------
# Main
# -----------------------


def main() -> None:
    ap = argparse.ArgumentParser(description="OSM vs BD TOPO — Distributions par classe")
    ap.add_argument("--config", required=True)
    ap.add_argument("--class-col", default=None, help="nom de la colonne classe à utiliser (override)")
    args = ap.parse_args()

    cfg = yaml.safe_load(open(args.config, "r", encoding="utf-8"))

    # --- metrics & fig params ---
    metrics = cfg.get("metrics", [])
    if not metrics:
        raise SystemExit("Aucune métrique définie dans la configuration (clé 'metrics').")
    if isinstance(metrics, list) and metrics and isinstance(metrics[0], str):
        metric_names = list(metrics)
        labels = {m: m for m in metric_names}
    else:
        metric_names = [m["name"] for m in metrics]
        labels = {m["name"]: m.get("label", m["name"]) for m in metrics}

    bins = cfg.get("hist", {}).get("bins", "fd")
    kde = bool(cfg.get("kde", {}).get("enabled", True))
    dpi = int(cfg.get("fig", {}).get("dpi", 140))
    width = float(cfg.get("fig", {}).get("width", 9.0))
    height = float(cfg.get("fig", {}).get("height", 6.0))

    # --- load data ---
    osm, bd = load_pair(cfg["inputs"]["osm"], cfg["inputs"]["bdtopo"])

    # --- resolve class column ---
    ordered: list[str] = []
    if args.class_col:
        ordered.append(args.class_col)
    elif cfg.get("class_column"):
        ordered.append(cfg["class_column"])
    ordered += cfg.get("class_column_candidates", [])
    defaults = ["class_norm", "highway", "class", "road_class", "fclass"]
    for d in defaults:
        if d not in ordered:
            ordered.append(d)

    class_col = None
    for c in ordered:
        if c in osm.columns and c in bd.columns:
            class_col = c
            break
    if not class_col:
        raise SystemExit("Colonne de classe introuvable. Essayez --class-col ou définissez class_column/class_column_candidates dans le YAML.")
    print(f"[by-class] Utilisation de la colonne de classe: {class_col}")

    osm = ensure_numeric_columns(osm, metric_names)
    bd = ensure_numeric_columns(bd, metric_names)

    # --- normalization & optional mapping ---
    # 1) Normalize raw labels
    osm_norm = pd.Series(osm[class_col].astype(str).map(_normalize_label), index=osm.index)
    bd_norm = pd.Series(bd[class_col].astype(str).map(_normalize_label), index=bd.index)

    # 2) Load mapping from config *file* if provided, else fallback to default path
    #    The mapping file is a flat dict: normalized_french_label -> osm_highway
    #    (e.g. "route a 1 chaussee" -> "primary", "route empierree" -> "track", ...)
    file_map: Dict[str, str] = {}
    mapping_path = None
    # Priority: explicit key, then default location
    if isinstance(cfg.get("class_mapping_file"), str):
        mapping_path = cfg.get("class_mapping_file")
    elif isinstance(cfg.get("class_mapping"), str):
        # allow legacy key pointing to a file path
        mapping_path = cfg.get("class_mapping")
    if mapping_path is None and os.path.exists("configs/class_map.yml"):
        mapping_path = "configs/class_map.yml"

    if mapping_path and os.path.exists(mapping_path):
        try:
            with open(mapping_path, "r", encoding="utf-8") as fm:
                raw_map = yaml.safe_load(fm) or {}
            # normalize keys & values
            file_map = {_normalize_label(k): _normalize_label(v) for k, v in raw_map.items()}
        except Exception as e:
            print(f"[by-class] Impossible de lire le mapping '{mapping_path}': {e}")

    # 3) Also accept inline dicts in config under class_mapping.osm / class_mapping.bdtopo
    inline_map_osm: Dict[str, str] | None = None
    inline_map_bd: Dict[str, str] | None = None
    if isinstance(cfg.get("class_mapping"), dict):
        cm = cfg.get("class_mapping")
        if isinstance(cm.get("osm"), dict):
            inline_map_osm = {_normalize_label(k): _normalize_label(v) for k, v in cm["osm"].items()}
        if isinstance(cm.get("bdtopo"), dict):
            inline_map_bd = {_normalize_label(k): _normalize_label(v) for k, v in cm["bdtopo"].items()}

    # 4) Build final maps. The file map applies to both sides (handles *_link, FR labels, etc.).
    #    Inline maps, if provided, override the file map for their respective source.
    map_osm: Dict[str, str] = dict(file_map)
    map_bd: Dict[str, str] = dict(file_map)
    if inline_map_osm:
        map_osm.update(inline_map_osm)
    if inline_map_bd:
        map_bd.update(inline_map_bd)

    # Apply mapping (keys not present stay normalized)
    osm_norm = _map_classes(osm_norm, map_osm)
    bd_norm = _map_classes(bd_norm, map_bd)

    classes = sorted(list(set(pd.Series(osm_norm).dropna().unique()).intersection(set(pd.Series(bd_norm).dropna().unique()))))
    print(f"[by-class] Classes communes après mapping: {classes[:20]} (n={len(classes)})")

    # --- preview CSV (to help mapping) ---
    overview = []
    for val, cnt in pd.Series(osm_norm).value_counts().items():
        overview.append({"class_norm": str(val), "source": "OSM", "count": int(cnt)})
    for val, cnt in pd.Series(bd_norm).value_counts().items():
        overview.append({"class_norm": str(val), "source": "BDTOPO", "count": int(cnt)})
    overview_df = pd.DataFrame(overview)

    ts_preview = time.strftime("%Y%m%d_%H%M%S")
    outputs = cfg.get("outputs", {}) or {}
    out_root = outputs.get("plots_dir") or outputs.get("root") or "out/plots"
    os.makedirs(out_root, exist_ok=True)
    preview_csv = os.path.join(out_root, f"by_class_preview_{ts_preview}.csv")
    try:
        overview_df.to_csv(preview_csv, index=False)
        print(f"[by-class] Aperçu des classes écrit → {preview_csv}")
    except Exception as e:
        print(f"[by-class] Impossible d'écrire l'aperçu des classes: {e}")

    if not classes:
        print("[by-class] Aucune classe commune OSM/BDTOPO après normalisation/mapping. Vérifiez --class-col et/ou 'class_mapping' dans la config.")
        return
    else:
        print(f"[by-class] {len(classes)} classe(s) commune(s) détectée(s): {classes[:10]}{'...' if len(classes)>10 else ''}")

    # --- output roots ---
    ts = time.strftime("%Y%m%d_%H%M%S")
    out_dir_root = os.path.join(out_root, f"by_class_{ts}")
    _ensure_dir(out_dir_root)

    # --- per-class exports ---
    for c in classes:
        slug = _slugify(str(c))
        out_dir = os.path.join(out_dir_root, slug)
        _ensure_dir(out_dir)
        print(f"[by-class] Classe '{c}' → dossier '{slug}'")

        # filter using normalized series equality
        mask_osm = osm_norm == c
        mask_bd = bd_norm == c

        for m in metric_names:
            s_osm = resolve_metric_series(osm.loc[mask_osm], m)
            s_bd = resolve_metric_series(bd.loc[mask_bd], m)
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
