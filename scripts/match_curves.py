# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
import os
import numpy as np
import pandas as pd

def _ensure_dir(p): os.makedirs(p, exist_ok=True)

def try_ckdtree():
    try:
        from scipy.spatial import cKDTree
        return cKDTree
    except Exception:
        return None

def main():
    ap = argparse.ArgumentParser(description="Appariement des virages OSM vs BD")
    ap.add_argument("--osm", required=True)
    ap.add_argument("--bd", required=True)
    ap.add_argument("--max-dist", type=float, default=50.0, help="distance max apex (m)")
    ap.add_argument("--len-ratio-max", type=float, default=2.0, help="tolérance sur ratio des longueurs d’arc")
    ap.add_argument("--out", default="out/curves/matched.parquet")
    args = ap.parse_args()

    osm = pd.read_parquet(args.osm)
    bd  = pd.read_parquet(args.bd)

    osm = osm.dropna(subset=["apex_x","apex_y"])
    bd  = bd.dropna(subset=["apex_x","apex_y"])

    Xo = osm[["apex_x","apex_y"]].to_numpy(dtype=float)
    Xb = bd[ ["apex_x","apex_y"]].to_numpy(dtype=float)

    cKDTree = try_ckdtree()
    matches=[]
    if cKDTree is not None:
        tree = cKDTree(Xb)
        dists, idxs = tree.query(Xo, k=1)
        for i,(d,j) in enumerate(zip(dists, idxs)):
            if np.isfinite(d) and d<=args.max_dist:
                lo = float(osm.iloc[i].get("arc_len", np.nan))
                lb = float(bd.iloc[j].get("arc_len", np.nan))
                if np.isfinite(lo) and np.isfinite(lb):
                    ratio = max(lo,lb)/max(min(lo,lb),1e-6)
                    if ratio <= args.len_ratio_max:
                        matches.append((i,j,d,ratio))
    else:
        # brute force par batch
        B = 5000
        for s in range(0, len(Xo), B):
            xo = Xo[s:s+B]
            # distances vers tous Xb (broadcast) — attention mémoire
            for ii,row in enumerate(xo):
                dif = Xb - row
                ds = np.sqrt((dif**2).sum(axis=1))
                j = np.argmin(ds)
                d = ds[j]
                if np.isfinite(d) and d<=args.max_dist:
                    i = s+ii
                    lo = float(osm.iloc[i].get("arc_len", np.nan))
                    lb = float(bd.iloc[j].get("arc_len", np.nan))
                    if np.isfinite(lo) and np.isfinite(lb):
                        ratio = max(lo,lb)/max(min(lo,lb),1e-6)
                        if ratio <= args.len_ratio_max:
                            matches.append((i,j,d,ratio))

    if not matches:
        print("Aucun appariement trouvé.")
        pd.DataFrame(columns=["osm_idx","bd_idx","dist","len_ratio"]).to_parquet(args.out, index=False)
        return

    idx_o, idx_b, dist, lr = map(np.array, zip(*matches))
    m = pd.DataFrame(dict(
        osm_idx=idx_o, bd_idx=idx_b, dist=dist, len_ratio=lr
    ))
    out = osm.reset_index(drop=True).iloc[idx_o].add_prefix("osm_").reset_index(drop=True)
    out = pd.concat([out, bd.reset_index(drop=True).iloc[idx_b].add_prefix("bd_").reset_index(drop=True)], axis=1)
    out["match_dist"] = dist
    out["match_len_ratio"] = lr

    _ensure_dir(os.path.dirname(args.out))
    out.to_parquet(args.out, index=False)
    print(f"✅ Appariements de virages → {args.out} (n={len(out)})")

if __name__ == "__main__":
    main()
