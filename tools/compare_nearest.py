#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Compare nearest OSM ↔ BD TOPO segments and export stats/matches.

Additions vs previous version:
- --out-summary, --out-matches, --per-class
- Robust handling of geopandas suffixes (_left/_right) for metrics & class
- Optional --drop-inf to ignore +/-inf in radius before computing diffs
- Clear diagnostics and safe fallbacks
"""
from __future__ import annotations

import argparse
import json
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, LineString
from unicodedata import normalize as u_normalize

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

def _strip_accents(s: str) -> str:
    return "".join(c for c in u_normalize("NFKD", s) if ord(c) < 128)


def _norm_class(val: str | float | int | None) -> str | None:
    if val is None or (isinstance(val, float) and not np.isfinite(val)):
        return None
    s = str(val).strip().lower()
    s = _strip_accents(s)
    for bad in ["/", "\\", ",", ";"]:
        s = s.replace(bad, " ")
    s = " ".join(s.split())
    return s or None


def _load_mapping(path: Path | None) -> dict[str, str]:
    if not path:
        return {}
    try:
        if path.suffix.lower() in {".yml", ".yaml"}:
            import yaml  # lazy
            data = yaml.safe_load(Path(path).read_text()) or {}
        else:
            data = json.loads(Path(path).read_text())
        # normalize keys/values
        return { _norm_class(k): _norm_class(v) for k, v in data.items() if k is not None }
    except Exception as e:  # pragma: no cover (logging only)
        warnings.warn(f"[WARN] Échec lecture mapping {path}: {e} — mapping ignoré.")
        return {}


def _default_bdtopo_to_osm_map() -> dict[str, str]:
    # Clefs BD TOPO (nature) → valeurs OSM highway (normalisées)
    return {
        "autoroute": "motorway",
        "bretelle": "motorway_link",
        "bretelle d autoroute": "motorway_link",
        "route a 2 chaussees": "trunk",
        "route principale": "primary",
        "route secondaire": "secondary",
        "route tertiaire": "tertiary",
        "route communale": "unclassified",
        "chemin": "track",
        "piste": "track",
        "piste cyclable": "cycleway",
        "rond point": "junction",
        "aire de service": "service",
        "voie de desserte": "service",
    }


def _apply_mapping(series: pd.Series, mapping: dict[str, str]) -> pd.Series:
    return series.map(lambda v: mapping.get(v, v) if v is not None else None)


def _build_points(df: pd.DataFrame, crs: str = "EPSG:2154") -> gpd.GeoDataFrame:
    # Expect x_centroid / y_centroid added by compute_curvature.py
    if not {"x_centroid", "y_centroid"}.issubset(df.columns):
        raise RuntimeError("Colonnes manquantes x_centroid / y_centroid — régénérez les sorties.")
    geom = [Point(x, y) for x, y in zip(df["x_centroid"].to_numpy(), df["y_centroid"].to_numpy())]
    return gpd.GeoDataFrame(df.copy(), geometry=geom, crs=crs)


def _resolve_col(joined: pd.DataFrame, base: str, prefer_left: bool = True) -> tuple[str | None, str | None]:
    """Return (left, right) columns for a base name, handling geopandas suffixes."""
    left = None
    right = None
    # left
    if f"{base}_left" in joined.columns:
        left = f"{base}_left"
    elif base in joined.columns:
        left = base
    # right
    if f"{base}_right" in joined.columns:
        right = f"{base}_right"
    elif base in joined.columns and base != left:
        right = base
    return left, right


def _describe(df: pd.DataFrame) -> pd.DataFrame:
    cols = [c for c in df.columns if c.startswith("diff_")]
    if not cols:
        return pd.DataFrame()
    d = df[cols].describe().T
    d["count"] = d["count"].map(lambda x: f"{int(x):,}".replace(",", " "))
    return d


# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------

def main(argv=None):
    p = argparse.ArgumentParser(description="Nearest-neighbor comparison between OSM and BD TOPO segments")
    p.add_argument("--in-dir", type=Path, default=Path("."))
    p.add_argument("--osm-name", type=str, default="roadinfo_segments_osm.parquet")
    p.add_argument("--bd-name", type=str, default="roadinfo_segments_bdtopo.parquet")

    p.add_argument("--max-dist", type=float, default=30.0, help="Distance max (m) pour sjoin_nearest")
    p.add_argument("--match-class", action="store_true", help="Contraindre l'appariement à la même classe normalisée")
    p.add_argument("--class-col-osm", type=str, default="class")
    p.add_argument("--class-col-bd", type=str, default="class")
    p.add_argument("--class-map", type=Path, default=None, help="YAML/JSON mapping BD→OSM (prioritaire)")

    p.add_argument("--drop-inf", action="store_true", help="Ignore les ±inf de radius_min avant calcul des écarts")

    p.add_argument("--out-summary", type=Path, default=None, help="Chemin CSV de synthèse (describe)")
    p.add_argument("--out-matches", type=Path, default=None, help="Chemin CSV des appariements détaillés")
    p.add_argument("--out-byclass", type=Path, default=None, help="Chemin CSV des stats par classe (si --per-class)")
    p.add_argument("--export-geo", type=Path, default=None, help="Export Geo* des appariements sous forme de segments (LineString)")
    p.add_argument("--per-class", action="store_true", help="Écrit un CSV par classe normalisée (_byclass)")
    p.add_argument("--diag-classes", action="store_true", help="Affiche des stats de classes (brut/normalisé) et impression console")
    p.add_argument("--out-class-stats", type=Path, default=None, help="Chemin CSV des stats de classes (optionnel)")

    p.add_argument("--metrics", type=str, default="length_m,radius_min_m,curv_mean_1perm",
                   help="Liste de métriques à comparer (séparées par des virgules)")
    p.add_argument("--out-quantiles", type=Path, default=None,
                   help="Chemin CSV des quantiles (si non fourni, écrit à côté de --out-summary avec suffixe __quantiles)")
    p.add_argument(
        "--quantiles",
        type=str,
        default="0.10,0.25,0.50,0.75,0.90",
        help="Liste de quantiles (0-1) séparés par des virgules, ex: '0.10,0.50,0.90'. Par défaut: 0.10,0.25,0.50,0.75,0.90",
    )
    p.add_argument("--keep-cols", type=str, default="",
                   help="Colonnes supplémentaires à conserver dans --out-matches (séparées par des virgules)")
    args = p.parse_args(argv)

    # Parse metrics list and extra columns
    metrics = [m.strip() for m in args.metrics.split(",") if m.strip()]
    extra_keep = [c.strip() for c in args.keep_cols.split(",") if c.strip()]

    in_dir = args.in_dir
    df_osm = pd.read_parquet(in_dir / args.osm_name)
    df_bd = pd.read_parquet(in_dir / args.bd_name)

    # Build GeoDataFrames with points first (we also keep class columns in plain df)
    g_osm = _build_points(df_osm, crs="EPSG:2154")
    g_bd = _build_points(df_bd, crs="EPSG:2154")

    # Prepare class normalization + mapping
    if args.match_class:
        osm_cls_col = args.class_col_osm if args.class_col_osm in g_osm.columns else None
        bd_cls_col = args.class_col_bd if args.class_col_bd in g_bd.columns else None
        if osm_cls_col is None or bd_cls_col is None:
            print("[WARN] match_class demandé mais colonnes de classe manquantes — aucune contrainte appliquée.", file=sys.stderr)
            args.match_class = False
        else:
            g_osm["_class_norm"] = g_osm[osm_cls_col].map(_norm_class)
            g_bd["_class_norm"] = g_bd[bd_cls_col].map(_norm_class)
            mp = _default_bdtopo_to_osm_map()
            user_mp = _load_mapping(args.class_map)
            if user_mp:
                mp.update(user_mp)
            g_bd["_class_norm"] = _apply_mapping(g_bd["_class_norm"], mp)

    # --- Diagnostics de classes (facultatif) ---
    if args.diag_classes:
        # Construire un mapping complet (défaut + utilisateur)
        mp_all = _default_bdtopo_to_osm_map()
        user_mp = _load_mapping(args.class_map)
        if user_mp:
            mp_all.update(user_mp)

        def _mk_counts(gdf: gpd.GeoDataFrame, raw_col: str | None, mapping: dict[str, str], label: str) -> pd.DataFrame:
            if raw_col is None or raw_col not in gdf.columns:
                return pd.DataFrame(columns=["source", "class", "count_raw", "count_norm"])  # empty
            sr_raw = gdf[raw_col].map(_norm_class)
            sr_norm = _apply_mapping(sr_raw, mapping) if mapping else sr_raw
            vc_raw = sr_raw.value_counts(dropna=True)
            vc_norm = sr_norm.value_counts(dropna=True)
            dfc = pd.DataFrame({"count_raw": vc_raw, "count_norm": vc_norm}).fillna(0).astype(int).reset_index().rename(columns={"index": "class"})
            dfc.insert(0, "source", label)
            return dfc

        # Colonnes de classe choisies (même si match_class est False)
        osm_cls_raw = args.class_col_osm if args.class_col_osm in g_osm.columns else None
        bd_cls_raw  = args.class_col_bd  if args.class_col_bd  in g_bd.columns  else None

        cs_osm = _mk_counts(g_osm, osm_cls_raw, {}, "osm")
        cs_bd  = _mk_counts(g_bd,  bd_cls_raw,  mp_all, "bdtopo")
        class_stats = pd.concat([cs_osm, cs_bd], ignore_index=True, sort=False)

        if not class_stats.empty:
            print("[INFO] Top classes (normalisées) OSM:")
            try:
                print(class_stats[class_stats["source"]=="osm"].sort_values("count_norm", ascending=False).head(15))
            except Exception:
                print(class_stats[class_stats["source"]=="osm"].head(15))
            print("[INFO] Top classes (normalisées) BD TOPO (après mapping):")
            try:
                print(class_stats[class_stats["source"]=="bdtopo"].sort_values("count_norm", ascending=False).head(15))
            except Exception:
                print(class_stats[class_stats["source"]=="bdtopo"].head(15))

            if args.out_class_stats:
                class_stats.to_csv(args.out_class_stats, index=False)
                print(f"Écrit (stats classes): {args.out_class_stats}")
        else:
            print("[INFO] Aucune statistique de classes disponible (colonnes introuvables).")

    # Spatial join
    # Ensure both sides have active geometry named 'geometry' with same CRS;
    # copy right geometry to a separate column so we can export later.
    # (Avoids recursion issues in GeoPandas when the right geometry column is renamed.)
    if g_osm.crs != g_bd.crs:
        try:
            g_bd = g_bd.to_crs(g_osm.crs)
        except Exception as e:
            warnings.warn(f"[WARN] Reprojection BD→OSM CRS a échoué ({e}); tentative de jonction telle quelle.")

    g_bd_r = g_bd.copy()
    g_bd_r["geometry_right"] = g_bd_r.geometry  # keep an explicit copy for export
    # keep active geometry as 'geometry' for the spatial join
    right_cols = [c for c in g_bd_r.columns if c != "geometry_right"] + ["geometry_right"]

    joined = gpd.sjoin_nearest(
        g_osm,
        g_bd_r[right_cols],
        how="left",
        max_distance=args.max_dist,
        distance_col="_dist_m",
    )

    # Diagnostics
    n_total = len(g_osm)
    n_matched = int(joined["_dist_m"].notna().sum()) if "_dist_m" in joined.columns else len(joined)
    print(f"[INFO] Appariements trouvés: {n_matched:,} / {n_total:,} (max_dist={args.max_dist} m)")

    # Class constraint (after join: cols suffixed with _left/_right)
    if args.match_class:
        lcls, rcls = _resolve_col(joined, "_class_norm")
        if lcls and rcls:
            before = len(joined)
            joined = joined[joined[lcls].notna() & joined[rcls].notna() & (joined[lcls] == joined[rcls])]
            after = len(joined)
            print(f"[INFO] Contrainte de classe: {after:,} / {before:,} appariements conservés")
        else:
            warnings.warn("[WARN] Colonnes de classes normalisées manquantes après sjoin — contrainte ignorée.")

    # Compute diffs
    out_cols: list[str] = []
    for m in metrics:
        lcol, rcol = _resolve_col(joined, m)
        if lcol is None or rcol is None:
            continue
        if args.drop_inf and m == "radius_min_m":
            # mask infinities before diff
            mask_inf = ~np.isfinite(joined[lcol]) | ~np.isfinite(joined[rcol])
            joined.loc[mask_inf, [lcol, rcol]] = np.nan
        diff_col = f"diff_{m}"
        joined[diff_col] = joined[lcol] - joined[rcol]
        out_cols.append(diff_col)

    if not out_cols:
        print("[WARN] Aucune métrique commune trouvée dans le DataFrame joint — vérifie les noms/suffixes de colonnes.")
        print("Colonnes disponibles (extrait):", list(joined.columns)[:40])
        out_path = args.out_summary or (in_dir / "compare__nearest_diffs.csv")
        pd.DataFrame({"note": ["no_common_metrics"]}).to_csv(out_path, index=False)
        print(f"\nÉcrit: {out_path}")
        return

    # Summary describe
    summary = joined[out_cols].describe()
    out_summary = args.out_summary or (in_dir / "compare__nearest_diffs.csv")
    summary.to_csv(out_summary)
    print(summary)
    print(f"\nÉcrit: {out_summary}")

    # Optional quantiles export
    try:
        # Parse and validate quantile levels
        if args.quantiles:
            try:
                q_levels = sorted({float(q.strip()) for q in args.quantiles.split(",") if q.strip() != ""})
            except ValueError:
                raise ValueError(f"Valeurs de --quantiles invalides: {args.quantiles!r}")
        else:
            q_levels = [0.10, 0.25, 0.50, 0.75, 0.90]
        # keep only in (0,1)
        q_levels = [q for q in q_levels if 0.0 <= q <= 1.0]
        if not q_levels:
            raise ValueError("Aucun quantile valide fourni (attendu valeurs entre 0 et 1).")
        qdf = joined[out_cols].quantile(q_levels)
        # Label index as q0.10, q0.50, etc. to be consistent with plotting tools
        qdf.index = [f"q{q:0.2f}" for q in q_levels]
        out_q = args.out_quantiles
        if out_q is None:
            # derive from out_summary
            base = Path(out_summary)
            out_q = base.with_name(base.stem + "__quantiles.csv")
        pd.DataFrame(qdf).to_csv(out_q)
        print(f"Écrit (quantiles): {out_q}")
    except Exception as e:
        warnings.warn(f"[WARN] Export des quantiles impossible: {e}")

    # Optional matches export
    if args.out_matches:
        keep = [
            c for c in [
                "road_id_left", "road_id_right", "class_left", "class_right", "name_left", "name_right",
                "_dist_m",
            ]
            if c in joined.columns
        ]
        # include user-requested extra columns if present
        for c in extra_keep:
            if c in joined.columns and c not in keep:
                keep.append(c)
        keep += out_cols
        # also keep original metric columns if available
        for m in metrics:
            lcol, rcol = _resolve_col(joined, m)
            if lcol: keep.append(lcol)
            if rcol: keep.append(rcol)
        joined[keep].to_csv(args.out_matches, index=False)
        print(f"Écrit (appariements): {args.out_matches}")

    # Optional per-class stats
    if args.per_class:
        lcls, rcls = _resolve_col(joined, "_class_norm")
        if lcls and rcls:
            by = joined[[lcls, rcls] + out_cols].copy()
            by.rename(columns={lcls: "class_left", rcls: "class_right"}, inplace=True)
            grp = by.groupby(["class_left", "class_right"]).agg(
                count=(out_cols[0], "count"),
                mean_curv=("diff_curv_mean_1perm", "mean"),
                mean_len=("diff_length_m", "mean"),
            ).reset_index()
            out_byclass = args.out_byclass or (in_dir / "compare__nearest_byclass.csv")
            grp.to_csv(out_byclass, index=False)
            print(f"Écrit (par classe): {out_byclass}")
        else:
            print("[INFO] Stats par classe non écrites (classes absentes).")

    # Optional Geo export of matches as LineStrings between OSM and BD centroids
    if args.export_geo:
        geom_left = joined["geometry"] if "geometry" in joined.columns else None
        geom_right = joined["geometry_right"] if "geometry_right" in joined.columns else None
        # Fallback: rebuild right geometry from centroid columns if needed
        if geom_right is None and {"x_centroid_right", "y_centroid_right"}.issubset(joined.columns):
            try:
                geom_right = gpd.GeoSeries(
                    [Point(x, y) if pd.notna(x) and pd.notna(y) else None
                     for x, y in zip(joined["x_centroid_right"], joined["y_centroid_right"])],
                    crs="EPSG:2154",
                )
                joined["geometry_right"] = geom_right
            except Exception:
                pass
        if geom_left is None or ("geometry_right" not in joined.columns):
            warnings.warn("[WARN] Impossible de créer les segments géométriques (geometry/geometry_right manquants).")
        else:
            # Build LineStrings for rows with both geometries present
            lines = []
            for gl, gr in zip(geom_left, joined["geometry_right"]):
                if gl is not None and gr is not None and pd.notna(gl) and pd.notna(gr):
                    try:
                        lines.append(LineString([gl, gr]))
                    except Exception:
                        lines.append(None)
                else:
                    lines.append(None)
            gexp = gpd.GeoDataFrame(
                joined.copy(),
                geometry=lines,
                crs="EPSG:2154",
            )
            # Keep a compact set of columns
            keep = [c for c in [
                "road_id_left", "road_id_right", "class_left", "class_right", "name_left", "name_right",
                "_dist_m",
                "diff_length_m", "diff_radius_min_m", "diff_curv_mean_1perm"
            ] if c in gexp.columns]
            keep = keep + ["geometry"]
            gexp = gexp[keep]
            # Pick driver from extension
            out_path = Path(args.export_geo)
            ext = out_path.suffix.lower()
            driver = "GPKG" if ext == ".gpkg" else ("GeoJSON" if ext in {".geojson", ".json"} else None)
            if driver:
                gexp.to_file(out_path, driver=driver)
            else:
                # default to GPKG if unknown
                gexp.to_file(out_path.with_suffix(".gpkg"), driver="GPKG")
                out_path = out_path.with_suffix(".gpkg")
            print(f"Écrit (segments géo): {out_path}")


if __name__ == "__main__":
    main()