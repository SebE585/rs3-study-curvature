# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse, os, time, yaml
import numpy as np, pandas as pd
import matplotlib.pyplot as plt


def _ensure_dir(p): os.makedirs(p, exist_ok=True)

def _load_from_config(cfg_path: str):
    cfg = yaml.safe_load(open(cfg_path))
    return cfg["inputs"]["osm"], cfg["inputs"]["bdtopo"]


def kappa_of(df: pd.DataFrame) -> pd.Series:
    if "curv_mean_1perm" in df.columns:
        return pd.to_numeric(df["curv_mean_1perm"], errors="coerce")
    if "curvature" in df.columns:
        return pd.to_numeric(df["curvature"], errors="coerce")
    if "radius_min_m" in df.columns:
        with np.errstate(divide='ignore', invalid='ignore'):
            k = 1.0 / pd.to_numeric(df["radius_min_m"], errors="coerce")
        return k.replace([np.inf,-np.inf], np.nan)
    return pd.Series(np.nan, index=df.index)


def main():
    ap = argparse.ArgumentParser(description="Profils de courbure approximés par virage")
    ap.add_argument("--segments-osm", default=None, help="parquet segments OSM")
    ap.add_argument("--segments-bd",  default=None, help="parquet segments BD")
    ap.add_argument("--config", default=None, help="YAML contenant inputs.osm et inputs.bdtopo")
    ap.add_argument("--curves-osm", required=True)
    ap.add_argument("--curves-bd",  required=True)
    ap.add_argument("--out-dir", default="out/plots")
    args = ap.parse_args()

    if (args.segments_osm is None or args.segments_bd is None):
        if not args.config:
            raise SystemExit("Fournir --config ou --segments-osm/--segments-bd")
        so_path, sb_path = _load_from_config(args.config)
    else:
        so_path, sb_path = args.segments_osm, args.segments_bd

    so = pd.read_parquet(so_path)
    sb = pd.read_parquet(sb_path)
    co = pd.read_parquet(args.curves_osm)
    cb = pd.read_parquet(args.curves_bd)

    def select_turns(seg: pd.DataFrame):
        k = kappa_of(seg).abs()
        r = pd.to_numeric(seg["radius_min_m"], errors="coerce") if "radius_min_m" in seg.columns else pd.Series(np.nan, index=seg.index)
        mask = (k >= 1e-4) | (r <= 150)
        s = seg.loc[mask].copy()
        s["pos"] = s.groupby(seg.get("road_id","rid")).cumcount()
        s["pos_norm"] = s["pos"] / s.groupby(seg.get("road_id","rid"))["pos"].transform(lambda x: max(int(x.max()),1))
        return s

    so_t = select_turns(so)
    sb_t = select_turns(sb)

    def mean_profile(s: pd.DataFrame):
        if s.empty:
            return np.linspace(0, 1, 21)[:-1] + 0.5/20, np.zeros(20)
        bins = np.linspace(0, 1, 21)
        labels = list(range(len(bins) - 1))
        # Bin with explicit integer labels to keep category order
        s["bin"] = pd.cut(s["pos_norm"].clip(0, 1), bins=bins, labels=labels, include_lowest=True, ordered=True)
        # Compute mean |kappa| per bin
        prof = s.groupby("bin", observed=False)["pos_norm"].apply(lambda g: kappa_of(s.loc[g.index]).abs().mean(skipna=True))
        # Reindex to ensure we have one value per bin (fill missing with NaN -> 0 for plotting)
        prof = prof.reindex(pd.Index(labels, name="bin"))
        x = (bins[:-1] + bins[1:]) / 2
        y = prof.to_numpy()
        y = np.nan_to_num(y, nan=0.0)
        return x, y

    xo, yo = mean_profile(so_t)
    xb, yb = mean_profile(sb_t)

    ts = time.strftime("%Y%m%d_%H%M%S")
    out_dir = os.path.join(args.out_dir, f"curves_{ts}")
    _ensure_dir(out_dir)

    plt.figure()
    plt.plot(xo, yo, label="OSM")
    plt.plot(xb, yb, label="BD TOPO")
    plt.xlabel("Position normalisée dans la courbe (0→1)")
    plt.ylabel("|kappa| moyen (1/m)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "mean_kappa_profile.png"), dpi=160)
    print(f"✅ Profils de courbure → {out_dir}")

if __name__ == "__main__":
    main()