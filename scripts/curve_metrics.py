# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse, os
import numpy as np
import pandas as pd


def _ensure_dir(p: str) -> None:
    if p:
        os.makedirs(p, exist_ok=True)


def alat(v_kmh: float, r_m: pd.Series | np.ndarray) -> np.ndarray:
    """Accélération latérale (m/s²) pour vitesse v_kmh et rayon r (m).
    Accepte Series ou ndarray et renvoie un ndarray, NaN si rayon manquant/infini/0.
    """
    v = v_kmh / 3.6
    r = pd.to_numeric(r_m, errors="coerce").to_numpy() if isinstance(r_m, pd.Series) else np.asarray(r_m, dtype=float)
    with np.errstate(divide='ignore', invalid='ignore'):
        a = (v * v) / r
    a[~np.isfinite(a)] = np.nan
    return a


def _numeric_agg(df: pd.DataFrame) -> pd.DataFrame:
    """Agrège uniquement les colonnes numériques avec stats utiles."""
    num = df.select_dtypes(include=[np.number])
    if num.empty:
        return pd.DataFrame(columns=["count", "mean", "median", "std", "q25", "q75", "iqr"])
    agg = num.agg(["count", "mean", "median", "std"]).T
    q25 = num.quantile(0.25)
    q75 = num.quantile(0.75)
    agg["q25"] = q25
    agg["q75"] = q75
    agg["iqr"] = q75 - q25
    return agg


def main() -> None:
    ap = argparse.ArgumentParser(description="KPIs sur les virages appariés")
    ap.add_argument("--matched", required=True, help="Parquet des virages appariés (match_curves.py)")
    ap.add_argument("--out-csv", default="out/stats/curve_kpis.csv", help="Chemin de sortie du CSV agrégé (global)")
    ap.add_argument("--by-class-csv", default="out/stats/curve_kpis_by_class.csv", help="Chemin de sortie du CSV agrégé par classe")
    ap.add_argument("--save-rows", default=None, help="Chemin (parquet/csv) pour sauvegarder les KPIs ligne-à-ligne (optionnel)")
    args = ap.parse_args()

    df = pd.read_parquet(args.matched)

    # Colonnes attendues
    r_osm = pd.to_numeric(df.get("osm_r_min"), errors="coerce")
    r_bd  = pd.to_numeric(df.get("bd_r_min"),  errors="coerce")
    k_osm = pd.to_numeric(df.get("osm_kappa_max"), errors="coerce")
    k_bd  = pd.to_numeric(df.get("bd_kappa_max"),  errors="coerce")

    # KPIs élémentaires (ligne à ligne)
    kpis = pd.DataFrame({
        "diff_r_min": r_osm - r_bd,
        "diff_kappa_max": k_osm - k_bd,
        "alat50_diff": alat(50, r_osm) - alat(50, r_bd),
        "alat80_diff": alat(80, r_osm) - alat(80, r_bd),
        "alat110_diff": alat(110, r_osm) - alat(110, r_bd),
        "class": df.get("osm_class", df.get("bd_class"))
    })

    # Sauvegarde optionnelle des lignes
    if args.save_rows:
        _ensure_dir(os.path.dirname(args.save_rows))
        if args.save_rows.lower().endswith(".parquet"):
            kpis.to_parquet(args.save_rows, index=False)
        else:
            kpis.to_csv(args.save_rows, index=False)

    # Agrégation globale
    agg_global = _numeric_agg(kpis)
    _ensure_dir(os.path.dirname(args.out_csv))
    agg_global.to_csv(args.out_csv)
    print(f"✅ KPIs (global) → {args.out_csv}")

    # Agrégation par classe (si colonne présente)
    if "class" in kpis.columns and kpis["class"].notna().any():
        kpis["class"] = kpis["class"].astype(str).replace({"nan": np.nan})
        grouped = kpis.groupby("class", dropna=True)
        parts = []
        for cl, g in grouped:
            ag = _numeric_agg(g)
            ag.insert(0, "class", cl)
            parts.append(ag)
        if parts:
            byc = pd.concat(parts, axis=0)
            _ensure_dir(os.path.dirname(args.by_class_csv))
            byc.to_csv(args.by_class_csv, index_label="metric")
            print(f"✅ KPIs (par classe) → {args.by_class_csv}")
        else:
            print("[WARN] Aucune classe exploitable pour l'agrégation par classe.")
    else:
        print("[WARN] Colonne 'class' absente ou vide — agrégation par classe sautée.")


if __name__ == "__main__":
    main()