#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_gpkg_hotspots.py — Exporte un GPKG de "hotspots" (points OSM) pour les
plus grands écarts (par défaut diff_curv_mean_1perm) entre OSM et BD TOPO.

- Matche OSM ↔ BD via la même grille que compare_nearest.py
- Construit une GeoDataFrame de points (x_centroid,y_centroid) en EPSG:2154
- Trie par |metric| décroissant et écrit le Top-N en GPKG

Exemple:
  python tools/make_gpkg_hotspots.py \
    --in-dir /path/to/ref/roadinfo \
    --osm-name roadinfo_segments_osm.parquet \
    --bd-name  roadinfo_segments_bdtopo.parquet \
    --metric diff_curv_mean_1perm \
    --top-n 5000 \
    --out /path/to/ref/roadinfo/compare__hotspots.gpkg
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
import math
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Exporter un GPKG des plus gros écarts (hotspots)")
    p.add_argument("--in-dir", default=".", help="Répertoire des Parquet")
    p.add_argument("--osm-name", default="roadinfo_segments_osm.parquet")
    p.add_argument("--bd-name", default="roadinfo_segments_bdtopo.parquet")
    p.add_argument("--out", required=True, help="Chemin du GPKG de sortie")
    p.add_argument("--metric", default="diff_curv_mean_1perm",
                   help="Nom de la métrique d'écart à utiliser (sera calculée si absente)")
    p.add_argument("--top-n", type=int, default=5000)
    p.add_argument("--max-dist", type=float, default=30.0,
                   help="Distance max pour le matching (m, EPSG:2154)")
    p.add_argument("--match-class", action="store_true",
                   help="Appariement contraint par classe si disponible (road_class/class/highway/nature)")
    return p.parse_args()


@dataclass
class GridIndex:
    cell: float
    buckets: dict

    @classmethod
    def build(cls, xs: np.ndarray, ys: np.ndarray, cell: float):
        buckets = defaultdict(list)
        inv = 1.0 / cell
        for i, (x, y) in enumerate(zip(xs, ys)):
            bx = int(math.floor(x * inv))
            by = int(math.floor(y * inv))
            buckets[(bx, by)].append(i)
        return cls(cell, buckets)

    def candidates(self, x: float, y: float):
        inv = 1.0 / self.cell
        bx = int(math.floor(x * inv))
        by = int(math.floor(y * inv))
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                yield from self.buckets.get((bx+dx, by+dy), [])


def ensure_xy(df: pd.DataFrame):
    need = [c for c in ("x_centroid", "y_centroid") if c not in df.columns]
    if need:
        raise RuntimeError(f"Colonnes manquantes {need}. Re-génère les sorties ETL (compute_curvature).")
    return df


def pick_class_column(df: pd.DataFrame) -> str | None:
    for c in ["road_class", "class", "highway", "nature"]:
        if c in df.columns:
            return c
    return None


def match_osm_to_bd(osm: pd.DataFrame, bd: pd.DataFrame, max_dist: float, match_class: bool):
    xs_o, ys_o = osm["x_centroid"].to_numpy(float), osm["y_centroid"].to_numpy(float)
    xs_b, ys_b = bd["x_centroid"].to_numpy(float), bd["y_centroid"].to_numpy(float)

    cls_o = pick_class_column(osm) if match_class else None
    cls_b = pick_class_column(bd) if match_class else None
    if match_class and (cls_o is None or cls_b is None):
        cls_o = cls_b = None

    grid = GridIndex.build(xs_b, ys_b, cell=max(1.0, float(max_dist)))

    nn_j = np.full(len(osm), -1, dtype=np.int64)
    nn_d = np.full(len(osm), np.nan, dtype=float)

    for i in range(len(osm)):
        xo, yo = xs_o[i], ys_o[i]
        best_j = -1
        best_d2 = np.inf
        for j in grid.candidates(xo, yo):
            dx, dy = xs_b[j] - xo, ys_b[j] - yo
            d2 = dx*dx + dy*dy
            if d2 < best_d2:
                if cls_o is not None:
                    a, b = osm[cls_o].iat[i], bd[cls_b].iat[j]
                    if not (pd.isna(a) or pd.isna(b)) and str(a) != str(b):
                        continue
                best_d2 = d2
                best_j = j
        if best_j >= 0:
            d = math.sqrt(best_d2)
            if d <= max_dist:
                nn_j[i] = best_j
                nn_d[i] = d

    out = osm.copy()
    out["_bd_idx"] = nn_j
    out["nn_dist_m"] = nn_d
    out = out[out["_bd_idx"] >= 0]
    out = out.merge(bd.reset_index().rename(columns={"index": "_bd_idx"}), on="_bd_idx",
                    suffixes=("_osm", "_bd"))
    return out


def main():
    a = parse_args()
    in_dir = Path(a.in_dir)
    f_osm = in_dir / a.osm_name
    f_bd = in_dir / a.bd_name
    if not f_osm.exists() or not f_bd.exists():
        raise SystemExit(f"Fichier manquant: {f_osm if not f_osm.exists() else ''} {f_bd if not f_bd.exists() else ''}")

    osm = ensure_xy(pd.read_parquet(f_osm))
    bd = ensure_xy(pd.read_parquet(f_bd))

    matched = match_osm_to_bd(osm, bd, a.max_dist, a.match_class)

    # Calcul de la métrique si besoin
    if a.metric not in matched.columns:
        # fabrique écarts standards
        r_osm = matched["radius_min_m_osm"].replace([np.inf, -np.inf], np.nan)
        r_bd = matched["radius_min_m_bd"].replace([np.inf, -np.inf], np.nan)
        diffs = {
            "diff_length_m": matched["length_m_osm"] - matched["length_m_bd"],
            "diff_radius_min_m": r_osm - r_bd,
            "diff_curv_mean_1perm": matched["curv_mean_1perm_osm"] - matched["curv_mean_1perm_bd"],
        }
        for k, v in diffs.items():
            matched[k] = v
        if a.metric not in diffs:
            raise SystemExit(f"Métrique inconnue: {a.metric}. Dispo: {list(diffs.keys())}")

    # Construction GeoDataFrame (points OSM)
    g = gpd.GeoDataFrame(
        matched,
        geometry=gpd.points_from_xy(matched["x_centroid_osm"], matched["y_centroid_osm"]),
        crs="EPSG:2154",
    )

    # Top-N par |metric|
    g = g.loc[g[a.metric].abs().sort_values(ascending=False).index]
    g_top = g.head(a.top_n).copy()

    # Colonnes utiles
    keep = [
        "road_id_osm", "road_id_bd", "nn_dist_m",
        "length_m_osm", "length_m_bd",
        "radius_min_m_osm", "radius_min_m_bd",
        "curv_mean_1perm_osm", "curv_mean_1perm_bd",
        a.metric, "geometry"
    ]
    keep = [c for c in keep if c in g_top.columns] + ["geometry"]
    g_top = g_top[keep]

    out_path = Path(a.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    g_top.to_file(out_path, layer="hotspots", driver="GPKG")
    print(f"Écrit: {out_path} ({len(g_top)} entités)")


if __name__ == "__main__":
    main()