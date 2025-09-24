#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tracer les quantiles (médiane + bandes) en fonction de la distance max d'appariement.

Entrées possibles (plusieurs fichiers):
 - nearest_quants_d20.csv
 - nearest_quants_d30.csv
 - nearest_quants_d50.csv
(Le script extrait automatiquement d=20/30/50 depuis le nom de fichier.)

Formats CSV acceptés:
 1) Long:
    metric,quantile,value
    diff_length_m,0.50,-36.7
    ...

 2) Large (metrics en lignes):
    ,0.10,0.50,0.90
    diff_length_m,-76.8,-26.7,-4.85
    diff_curv_mean_1perm,-0.0186,-0.0081,-1.07e-08
    ...

 3) Large (quantiles en lignes -> sera transposé)

Usage:
  python tools/plot_quantiles.py \
      --in-files "/path/nearest_quants_d20.csv" "/path/nearest_quants_d30.csv" "/path/nearest_quants_d50.csv" \
      --out-dir  "/path/figs" \
      --metrics  "diff_length_m,diff_radius_min_m,diff_curv_mean_1perm" \
      --q-bands  "0.10,0.50,0.90;0.25,0.75"

Génère:
  - PNG par métrique: quantiles_<metric>.png avec médiane + bandes [q25,q75] et [q10,q90]
  - CSV long combiné: combined_quantiles_long.csv
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd
import matplotlib.pyplot as plt
from bisect import bisect_left


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Tracer les quantiles par distance d'appariement")
    p.add_argument(
        "--in-files",
        nargs="+",
        required=True,
        help="Liste de fichiers quantiles (ex: nearest_quants_d20.csv nearest_quants_d30.csv ...)",
    )
    p.add_argument(
        "--out-dir",
        type=str,
        required=True,
        help="Répertoire de sortie pour les PNG/CSV",
    )
    p.add_argument(
        "--metrics",
        type=str,
        default="",
        help="Liste de métriques à tracer, séparées par des virgules. Vide = toutes.",
    )
    p.add_argument(
        "--q-bands",
        type=str,
        default="0.10,0.50,0.90;0.25,0.75",
        help="Bandes de quantiles 'qmin,qmed,qmax;qlow,qup' (par défaut: '0.10,0.50,0.90;0.25,0.75')",
    )
    p.add_argument(
        "--dpi",
        type=int,
        default=130,
        help="DPI des figures (défaut: 130)",
    )
    return p.parse_args()


def extract_d_from_name(path: Path) -> float | None:
    """
    Extrait d=XX depuis le nom du fichier (cherche 'dXX' ou '_XX' après 'nearest_quants').
    """
    s = path.name
    # cas le plus courant: nearest_quants_d30.csv
    m = re.search(r"d(\d+)", s)
    if m:
        return float(m.group(1))
    # fallback: nearest_quants_30.csv
    m2 = re.search(r"_(\d+)\.csv$", s)
    if m2:
        return float(m2.group(1))
    return None


def tidy_from_csv(path: Path) -> pd.DataFrame:
    """
    Charge un CSV de quantiles et retourne un DataFrame long:
    colonnes = ['metric', 'quantile', 'value'] (quantile flottant).
    """
    df = pd.read_csv(path)

    # Si format "long" déjà conforme
    if {"metric", "quantile", "value"}.issubset(df.columns):
        out = df[["metric", "quantile", "value"]].copy()
        out["quantile"] = out["quantile"].astype(float)
        return out

    # Essayer de détecter un format "large":
    # 1) metrics en lignes, quantiles en colonnes (noms colonnes = '0.10','0.50', etc)
    # 2) quantiles en lignes, metrics en colonnes -> on transpose
    df0 = df.copy()

    # Si première colonne est un index de metrics sans nom
    if df0.columns[0].lower().startswith("unnamed") or df0.columns[0] == "":
        df0 = df0.rename(columns={df0.columns[0]: "metric"})

    # Cas: colonnes ressemblent à des quantiles:
    def _cols_look_like_quants(cols: List[str]) -> bool:
        ok = 0
        for c in cols:
            try:
                float(str(c).replace("q", "").replace("Q", ""))
                ok += 1
            except Exception:
                pass
        return ok >= max(2, int(0.5 * len(cols)))  # majorité de colonnes numériques

    # Cas A: lignes = metrics, colonnes = quantiles
    if "metric" in df0.columns and _cols_look_like_quants([c for c in df0.columns if c != "metric"]):
        long = df0.melt(id_vars=["metric"], var_name="quantile", value_name="value")
        # nettoyer les labels de quantiles 'q10' -> '0.10'
        long["quantile"] = (
            long["quantile"].astype(str).str.lower().str.replace("q", "", regex=False).apply(lambda s: f"{float(s) / 100:.2f}" if s.isdigit() else s)
        )
        long["quantile"] = long["quantile"].astype(float)
        return long[["metric", "quantile", "value"]]

    # Cas B: lignes = quantiles, colonnes = metrics
    # Si la première colonne ressemble à des quantiles
    first_col = df0.columns[0]
    try:
        # essayer: la première colonne contient des quantiles (ex: '0.10','0.50', 'q10', etc.)
        q_series = (
            df0[first_col]
            .astype(str)
            .str.lower()
            .str.replace("q", "", regex=False)
            .apply(lambda s: f"{float(s) / 100:.2f}" if s.isdigit() else s)
            .astype(float)
        )
        # succès -> transposer
        tmp = df0.drop(columns=[first_col]).T
        tmp.index.name = "metric"
        tmp.columns = q_series.values
        long = tmp.reset_index().melt(id_vars=["metric"], var_name="quantile", value_name="value")
        long["quantile"] = long["quantile"].astype(float)
        return long[["metric", "quantile", "value"]]
    except Exception:
        pass

    raise ValueError(f"Format CSV inconnu pour: {path}. " "Attendu soit (metric,quantile,value), soit large avec metrics/quantiles.")


def parse_qbands(s: str) -> Tuple[Tuple[float, float, float], Tuple[float, float]]:
    """
    '0.10,0.50,0.90;0.25,0.75' -> ((0.10,0.50,0.90), (0.25,0.75))
    """
    left, right = s.split(";")
    qmin, qmed, qmax = [float(x) for x in left.split(",")]
    ql, qu = [float(x) for x in right.split(",")]
    return (qmin, qmed, qmax), (ql, qu)


def main():
    args = parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    metrics_filter = [m.strip() for m in args.metrics.split(",") if m.strip()] if args.metrics else None
    (qmin, qmed, qmax), (ql, qu) = parse_qbands(args.q_bands)

    all_long = []  # d, metric, quantile, value

    for f in args.in_files:
        path = Path(f)
        d = extract_d_from_name(path)
        if d is None:
            print(f"[WARN] distance introuvable dans le nom: {path.name} — ignoré.")
            continue
        try:
            df_long = tidy_from_csv(path)
        except Exception as e:
            print(f"[WARN] {path}: {e} — ignoré.")
            continue

        df_long["d"] = d
        all_long.append(df_long)

    if not all_long:
        raise SystemExit("Aucun fichier valide après parsing.")

    long = pd.concat(all_long, ignore_index=True)

    # Filtrer les métriques si demandé
    if metrics_filter:
        long = long[long["metric"].isin(metrics_filter)]

    # Sauvegarde du combiné long
    combined_csv = out_dir / "combined_quantiles_long.csv"
    long.sort_values(["metric", "quantile", "d"]).to_csv(combined_csv, index=False)
    print(f"Écrit (combiné long): {combined_csv}")

    def _dedup_quantile_columns(df: pd.DataFrame) -> pd.DataFrame:
        """
        Après les fusions successives, des colonnes dupliquées peuvent apparaître
        sous forme 'q0.50_x', 'q0.50_y', etc. On coalesce ces colonnes en une seule
        par label ('q0.50'), en prenant la première valeur non-nulle.
        """
        import re as _re

        if df.empty:
            return df

        res = df[["d"]].copy()
        for c in [c for c in df.columns if c != "d"]:
            base = _re.sub(r"(_x|_y)+$", "", c)
            if base in res.columns:
                # coalesce: garder la première valeur non-nulle rencontrée
                res[base] = res[base].where(res[base].notna(), df[c])
            else:
                res[base] = df[c]
        return res

    def _nearest_label(qcols: List[str], target: float) -> str:
        """
        Parmi les colonnes de type 'q0.50', renvoie l'étiquette dont la valeur
        de quantile est la plus proche de `target`.
        """
        best = None
        best_err = None
        for c in qcols:
            if isinstance(c, str) and c.startswith("q"):
                try:
                    val = float(c[1:])
                except Exception:
                    continue
                err = abs(val - target)
                if best is None or err < best_err:
                    best = c
                    best_err = err
        return best if best is not None else f"q{target:.2f}"

    def _sorted_available_quants(gdf: pd.DataFrame) -> List[float]:
        qs = sorted({float(q) for q in gdf["quantile"].unique()})
        return qs

    def _closest(qs: List[float], target: float) -> float:
        """Return the available quantile closest to target."""
        if not qs:
            raise ValueError("Aucune liste de quantiles disponible.")
        # qs is sorted
        i = bisect_left(qs, target)
        if i == 0:
            return qs[0]
        if i == len(qs):
            return qs[-1]
        before = qs[i - 1]
        after = qs[i]
        return after if (after - target) < (target - before) else before

    # Tracés par métrique
    for metric, g in long.groupby("metric"):
        # On veut avoir les valeurs pour qmin/qmed/qmax et ql/qu à chaque d
        avail_qs = _sorted_available_quants(g)
        requested = {
            "outer_low": qmin,
            "median": qmed,
            "outer_high": qmax,
            "inner_low": ql,
            "inner_high": qu,
        }
        # Fallback: si un quantile demandé n'existe pas, prendre le plus proche disponible
        chosen: Dict[str, float] = {
            k: (_closest(avail_qs, v) if round(v, 6) not in {round(a, 6) for a in avail_qs} else v) for k, v in requested.items()
        }

        # Alerter si un fallback a été appliqué
        for k, v in requested.items():
            if round(v, 6) != round(chosen[k], 6):
                print(f"[INFO] metric={metric}: quantile demandé {k}={v:.2f} remplacé par {chosen[k]:.2f} (dispo).")

        def pick(q: float, label: str) -> pd.DataFrame:
            gg = g[g["quantile"].round(6) == round(q, 6)]
            return gg.sort_values("d")[["d", "value"]].rename(columns={"value": label})

        parts = []
        # outer band
        parts.append(pick(chosen["outer_low"], f"q{chosen['outer_low']:.2f}"))
        parts.append(pick(chosen["outer_high"], f"q{chosen['outer_high']:.2f}"))
        # inner band
        parts.append(pick(chosen["inner_low"], f"q{chosen['inner_low']:.2f}"))
        parts.append(pick(chosen["inner_high"], f"q{chosen['inner_high']:.2f}"))
        # median
        parts.append(pick(chosen["median"], f"q{chosen['median']:.2f}"))

        # Fusion progressive sur 'd'
        base = None
        for p in parts:
            base = p if base is None else base.merge(p, on="d", how="outer")

        # Dédupliquer/normaliser les colonnes de quantiles éventuellement suffixées (_x/_y)
        if base is not None and not base.empty:
            base = _dedup_quantile_columns(base)

        if base is None or base.empty:
            print(f"[WARN] metric={metric}: pas de données — skip.")
            continue

        base = base.sort_values("d")

        # Plot
        fig = plt.figure(figsize=(6.5, 4.0))
        ax = plt.gca()

        qcols = [c for c in base.columns if c != "d"]
        inner_low_lbl = _nearest_label(qcols, ql) if qcols else f"q{ql:.2f}"
        inner_high_lbl = _nearest_label(qcols, qu) if qcols else f"q{qu:.2f}"
        outer_low_lbl = _nearest_label(qcols, qmin) if qcols else f"q{qmin:.2f}"
        outer_high_lbl = _nearest_label(qcols, qmax) if qcols else f"q{qmax:.2f}"
        median_lbl = _nearest_label(qcols, qmed) if qcols else f"q{qmed:.2f}"

        if inner_low_lbl in base and inner_high_lbl in base:
            ax.fill_between(
                base["d"],
                base[inner_low_lbl],
                base[inner_high_lbl],
                alpha=0.25,
                label=f"[{inner_low_lbl[1:]}, {inner_high_lbl[1:]}]",
            )

        if outer_low_lbl in base and outer_high_lbl in base:
            ax.fill_between(
                base["d"],
                base[outer_low_lbl],
                base[outer_high_lbl],
                alpha=0.15,
                label=f"[{outer_low_lbl[1:]}, {outer_high_lbl[1:]}]",
            )

        # médiane
        if median_lbl in base:
            ax.plot(
                base["d"],
                base[median_lbl],
                marker="o",
                linewidth=2,
                label=f"médiane ({median_lbl[1:]})",
            )

        ax.set_xlabel("Distance max d'appariement (m)")
        ax.set_ylabel(metric)
        ax.set_title(f"Quantiles vs distance — {metric}")
        ax.grid(True, linestyle="--", alpha=0.4)
        ax.legend(loc="best", frameon=True)

        out_png = out_dir / f"quantiles_{metric}.png"
        plt.tight_layout()
        plt.savefig(out_png, dpi=args.dpi)
        plt.close(fig)
        print(f"Écrit (figure): {out_png}")


if __name__ == "__main__":
    main()
