# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse, os, glob, pandas as pd, numpy as np
import matplotlib.pyplot as plt
from typing import List

def _ensure_dir(p: str): os.makedirs(p, exist_ok=True)

def load_quants(files: List[str]) -> pd.DataFrame:
    rows = []
    for f in files:
        d = None
        for tok in os.path.basename(f).split("_"):
            if tok.startswith("d") and tok[1:].isdigit():
                d = int(tok[1:])
        df = pd.read_csv(f)
        df["dist_m"] = d
        rows.append(df)
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()

def main():
    ap = argparse.ArgumentParser(description="Bias sweep — sensibilité à la distance d’appariement")
    ap.add_argument("--in-dir", dest="in_dir", required=True, help="répertoire contenant nearest_quants_d*.csv")
    ap.add_argument("--metrics", default="diff_length_m,diff_radius_min_m,diff_curv_mean_1perm")
    ap.add_argument("--q", default="0.50", help="quantile à tracer (ex: 0.50 pour médiane)")
    ap.add_argument("--out-dir", default="out/bias_sweep")
    ap.add_argument("--out-md", default="out/bias_sweep/report_bias_sweep.md")
    args = ap.parse_args()

    _ensure_dir(args.out_dir)
    files = sorted(glob.glob(os.path.join(args.in_dir, "nearest_quants_d*.csv")))
    if not files:
        raise SystemExit("Aucun fichier nearest_quants_d*.csv trouvé; lance d’abord `make quantiles`.")
    df = load_quants(files)
    if df.empty: raise SystemExit("Fichiers de quantiles vides.")

    metrics = [m.strip() for m in args.metrics.split(",") if m.strip()]
    q = float(args.q)

    md_lines = ["---", "title: Sensibilité à la distance d’appariement", "---", "",
                "# Sensibilité à la distance d’appariement", ""]
    for m in metrics:
        # chaque CSV devrait contenir des colonnes de type m_quantile (ex: diff_length_m_q50)
        # On cherche la colonne correspondant au quantile
        qcol = None
        for c in df.columns:
            if c.startswith(m + "_q"):
                suf = c.split("_q")[-1]
                try:
                    val = float(suf)
                    # if it's like 50, interpret as 0.50; if 0.5 or 0.50 keep as is
                    if val > 1.0:
                        val = val / 100.0
                    if abs(val - q) < 1e-6:
                        qcol = c
                        break
                except Exception:
                    continue
        if qcol is None:
            print(f"[WARN] Quantile {q} non trouvé pour {m} — skip.")
            continue
        sub = df[["dist_m", qcol]].dropna().sort_values("dist_m")
        if sub.empty: continue
        fig = plt.figure(figsize=(7,4), dpi=140)
        ax = fig.add_subplot(111)
        ax.plot(sub["dist_m"], sub[qcol], marker="o")
        ax.set_title(f"{m} — quantile {q}")
        ax.set_xlabel("Distance d’appariement (m)")
        ax.set_ylabel(f"{m} (q={q})")
        fig.tight_layout()
        out_png = os.path.join(args.out_dir, f"bias_{m}_q{int(q*100)}.png")
        fig.savefig(out_png); plt.close(fig)
        md_lines += [f"## {m}", "", f"![{m}]({os.path.relpath(out_png, start=os.path.dirname(args.out_md)).replace('\\','/')})", ""]

    _ensure_dir(os.path.dirname(args.out_md))
    with open(args.out_md, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
    print(f"✅ Bias sweep: figures → {args.out_dir} ; rapport → {args.out_md}")

if __name__ == "__main__":
    main()