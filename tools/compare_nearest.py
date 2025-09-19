#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import pandas as pd

try:
    from scipy.spatial import cKDTree as KDTree  # option rapide si dispo
except Exception:
    KDTree = None

from shapely.geometry import Point
from shapely.strtree import STRtree

def _nearest_idx_shapely(src_xy: np.ndarray, tgt_xy: np.ndarray) -> np.ndarray:
    """Fallback sans SciPy: STRtree Shapely."""
    tgt_pts = [Point(xy) for xy in tgt_xy]
    tree = STRtree(tgt_pts)
    out = np.empty(len(src_xy), dtype=np.int64)
    for i, (x, y) in enumerate(src_xy):
        p = Point(float(x), float(y))
        j = tree.nearest(p)  # retourne la géométrie
        out[i] = tgt_pts.index(j)
    return out

def main():
    ap = argparse.ArgumentParser(description="Match OSM→BDTOPO par plus proche voisin (centroïdes).")
    ap.add_argument("--in-dir", type=Path, default=Path("/Users/sebastien.edet/rs3-data/ref/roadinfo"))
    ap.add_argument("--osm-name", default="roadinfo_segments_osm.parquet")
    ap.add_argument("--bd-name",  default="roadinfo_segments_bdtopo.parquet")
    ap.add_argument("--out", default="compare__nearest_diffs.csv")
    args = ap.parse_args()

    osm = pd.read_parquet(args.in_dir / args.osm_name)
    bd  = pd.read_parquet(args.in_dir / args.bd_name)

    for col in ["x_centroid","y_centroid"]:
        if col not in osm.columns or col not in bd.columns:
            raise SystemExit(f"Colonne manquante '{col}'. Re-génère les sorties avec compute_curvature modifié.")

    osm_xy = osm[["x_centroid","y_centroid"]].to_numpy(dtype="float64", copy=False)
    bd_xy  = bd[["x_centroid","y_centroid"]].to_numpy(dtype="float64", copy=False)

    if KDTree is not None:
        tree = KDTree(bd_xy)
        dist, idx = tree.query(osm_xy, k=1)
    else:
        idx = _nearest_idx_shapely(osm_xy, bd_xy)

    matched = pd.concat(
        [osm.reset_index(drop=True),
         bd.iloc[idx].reset_index(drop=True)],
        axis=1,
        keys=["osm","bd"]
    )
    # aplatir colonnes multi-index
    matched.columns = [f"{a}_{b}" for a,b in matched.columns.to_flat_index()]

    # diffs sur quelques métriques
    for col in ["length_m","radius_min_m","curv_mean_1perm"]:
        if f"osm_{col}" in matched.columns and f"bd_{col}" in matched.columns:
            matched[f"diff_{col}"] = matched[f"osm_{col}"] - matched[f"bd_{col}"]

    # stats rapides
    stats = matched[[c for c in matched.columns if c.startswith("diff_")]].describe().T
    print(stats)

    out_csv = args.in_dir / args.out
    matched.to_csv(out_csv, index=False)
    print("\nÉcrit:", out_csv)

if __name__ == "__main__":
    main()