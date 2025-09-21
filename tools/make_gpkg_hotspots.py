#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Génère un GPKG de « hotspots » (points aux centroïdes OSM) sur la base
des plus grands écarts d'une métrique choisie (différences OSM-BD).

Si GeoPandas/pyogrio ne sont pas installés, écrit un CSV fallback.

Exemples :
    python tools/make_gpkg_hotspots.py \
      --in-dir /path/ref/roadinfo \
      --osm-name roadinfo_segments_osm.parquet \
      --bd-name  roadinfo_segments_bdtopo.parquet \
      --metric diff_curv_mean_1perm \
      --top-n 5000 \
      --out /path/ref/roadinfo/compare__hotspots.gpkg
"""

from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import pandas as pd

try:
    import geopandas as gpd
    from shapely.geometry import Point
    HAS_GEO = True
except Exception:
    HAS_GEO = False

# Import fonction d’appariement depuis compare_nearest si dispo
try:
    from tools.compare_nearest import nearest_match  # type: ignore
except Exception:
    nearest_match = None


def _read_parquet(path: Path) -> pd.DataFrame:
    return pd.read_parquet(path)


def _ensure_pairs(osm: pd.DataFrame, bd: pd.DataFrame) -> pd.DataFrame:
    """Si import de nearest_match échoue, on implémente un petit fallback KDTree/BruteForce."""
    try:
        from scipy.spatial import cKDTree
        HAVE_TREE = True
    except Exception:
        HAVE_TREE = False

    for c in ("x_centroid", "y_centroid"):
        if c not in osm.columns or c not in bd.columns:
            raise SystemExit("Colonnes x_centroid/y_centroid manquantes. Re-génère compute_curvature.")

    Xo = osm[["x_centroid", "y_centroid"]].to_numpy(float)
    Xb = bd[["x_centroid", "y_centroid"]].to_numpy(float)

    if HAVE_TREE:
        idx = cKDTree(Xb).query(Xo, k=1)[1]
        dist = np.sqrt(((Xo - Xb[idx]) ** 2).sum(axis=1))
    else:
        # bruteforce par batch
        idx = np.empty(len(Xo), dtype=np.int64)
        dist = np.empty(len(Xo), dtype=float)
        B = 5000
        for i in range(0, len(Xo), B):
            S = Xo[i:i+B]
            d2 = ((S[:, None, :] - Xb[None, :, :]) ** 2).sum(axis=2)
            j = d2.argmin(axis=1)
            idx[i:i+B] = j
            dist[i:i+B] = np.sqrt(d2[np.arange(len(j)), j])

    m = osm.copy()
    m["_bd_idx"] = idx
    m["_dist_m"] = dist
    bd_r = bd.reset_index(drop=True).add_suffix("_bd")
    return pd.concat([m, bd_r.loc[idx].reset_index(drop=True)], axis=1)


def _compute_diffs(pairs: pd.DataFrame) -> pd.DataFrame:
    # Différences (OSM - BD), avec gestion inf pour radius_min_m
    r_osm = pairs.get("radius_min_m")
    r_bd = pairs.get("radius_min_m_bd")

    if r_osm is not None:
        r_osm = r_osm.replace([np.inf, -np.inf], np.nan)
    else:
        r_osm = pd.Series(np.nan, index=pairs.index)

    if r_bd is not None:
        r_bd = r_bd.replace([np.inf, -np.inf], np.nan)
    else:
        r_bd = pd.Series(np.nan, index=pairs.index)

    pairs["diff_length_m"] = pairs.get("length_m", np.nan) - pairs.get("length_m_bd", np.nan)
    pairs["diff_radius_min_m"] = r_osm - r_bd
    pairs["diff_curv_mean_1perm"] = pairs.get("curv_mean_1perm", np.nan) - pairs.get("curv_mean_1perm_bd", np.nan)
    return pairs


def main():
    ap = argparse.ArgumentParser(description="Générer un GPKG points (hotspots) des plus gros écarts OSM vs BD")
    ap.add_argument("--in-dir", type=Path, default=Path("ref/roadinfo"))
    ap.add_argument("--osm-name", default="roadinfo_segments_osm.parquet")
    ap.add_argument("--bd-name", default="roadinfo_segments_bdtopo.parquet")
    ap.add_argument("--metric", default="diff_curv_mean_1perm",
                    choices=["diff_curv_mean_1perm", "diff_radius_min_m", "diff_length_m"],
                    help="Métrique de tri (OSM - BD)")
    ap.add_argument("--top-n", type=int, default=5000, help="Nombre de hotspots")
    ap.add_argument("--out", type=Path, default=Path("compare__hotspots.gpkg"))
    ap.add_argument("--abs", action="store_true", help="Trier par valeur absolue du diff (par défaut True pour curv)")
    args = ap.parse_args()

    in_dir = args.in_dir
    osm = _read_parquet(in_dir / args.osm_name)
    bd = _read_parquet(in_dir / args.bd_name)

    # Appariement
    if nearest_match is not None:
        pairs = nearest_match(osm, bd, max_dist=None, match_class=False, class_col_osm=None, class_col_bd=None)
    else:
        pairs = _ensure_pairs(osm, bd)

    pairs = _compute_diffs(pairs)

    metric = args.metric
    use_abs = args.abs or (metric == "diff_curv_mean_1perm")
    key = pairs[metric].abs() if use_abs else pairs[metric]
    top = pairs.loc[key.sort_values(ascending=False).head(args.top_n).index].copy()

    if HAS_GEO:
        gdf = gpd.GeoDataFrame(
            top.drop(columns=["geometry"], errors="ignore"),
            geometry=[Point(xy) for xy in zip(top["x_centroid"], top["y_centroid"])],
            crs="EPSG:2154",
        )
        args.out.parent.mkdir(parents=True, exist_ok=True)
        gdf.to_file(args.out, layer="hotspots", driver="GPKG")
        print("GPKG écrit:", args.out)
    else:
        # Fallback CSV
        csv_out = args.out.with_suffix(".csv")
        csv_out.parent.mkdir(parents=True, exist_ok=True)
        top.to_csv(csv_out, index=False)
        print("[WARN] GeoPandas manquant — CSV écrit à la place:", csv_out)


if __name__ == "__main__":
    main()