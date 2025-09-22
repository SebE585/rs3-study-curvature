# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse, os, time, yaml, pandas as pd

def _ensure_dir(p: str):
    if p and not os.path.exists(p): os.makedirs(p, exist_ok=True)

def _latest(dir_: str, prefix: str) -> str | None:
    if not os.path.isdir(dir_): return None
    cands = [os.path.join(dir_, n) for n in os.listdir(dir_) if n.startswith(prefix)]
    if not cands: return None
    cands.sort(reverse=True)
    return cands[0]

def main():
    ap = argparse.ArgumentParser(description="Rapport MkDocs — par classe")
    ap.add_argument("--config", required=True)
    ap.add_argument("--stats-dir", default="out/stats/by_class")
    ap.add_argument("--plots-root", default="out/plots")
    ap.add_argument("--out", default="out/report_by_class.md")
    ap.add_argument("--docs-rel", default=None, help="chemin relatif vers les plots pour intégration docs/")
    args = ap.parse_args()

    cfg = yaml.safe_load(open(args.config))
    metrics = cfg.get("metrics", [])
    labels = {m["name"]: m.get("label", m["name"]) for m in metrics}

    latest_stats = _latest(args.stats_dir, "tests_by_class_")
    df = None
    classes = []
    if latest_stats and os.path.exists(latest_stats):
        df = pd.read_csv(latest_stats)
        if "class" in df.columns:
            classes = df["class"].dropna().unique().tolist()
    else:
        print("[WARN] Aucun CSV by_class trouvé — le rapport sera généré en mode *plots-only*.")

    # détecter le dossier plots by_class le plus récent
    plots_parent = _latest(args.plots_root, "by_class_")
    if not plots_parent:
        print("[WARN] Aucun dossier plots 'by_class_' trouvé, le rapport n’inclura pas d’images.")
    if (not classes) and plots_parent and os.path.isdir(plots_parent):
        classes = sorted([d for d in os.listdir(plots_parent) if os.path.isdir(os.path.join(plots_parent, d))])
    out_path = args.out; _ensure_dir(os.path.dirname(out_path))

    lines = []
    lines += ["---", "title: Comparatif OSM vs BD TOPO — Par classe",
              f"date: {time.strftime('%Y-%m-%d %H:%M:%S')}", "---", ""]
    lines += ["# Comparatif par classe", ""]
    # Tableau récap global (agrégé par classe/metric)
    show_cols = [c for c in ["class","metric","n_osm","n_bd","mean_osm","mean_bd",
                             "diff_mean","cohens_d","cliffs_delta","ks_stat","p_ks"] if df is not None and c in df.columns]
    if df is not None and not df.empty and show_cols:
        lines += ["## Tableau récapitulatif", "", df[show_cols].to_markdown(index=False), ""]
    else:
        lines += ["## Tableau récapitulatif", "", "*Aucun CSV par classe disponible — section omise.*", ""]

    for c in classes:
        lines += [f"## {c}", ""]
        if df is not None and not df.empty and "class" in df.columns:
            dfc = df[df["class"] == c]
            if not dfc.empty and show_cols:
                lines += [dfc[show_cols].to_markdown(index=False), ""]
        # images si dispo
        if plots_parent:
            plots_dir = os.path.join(plots_parent, c)
            for m in dfc["metric"].unique() if df is not None and not df.empty and "metric" in df.columns else []:
                def relp(basename: str) -> str:
                    full = os.path.join(plots_dir, basename)
                    if not os.path.exists(full): return None
                    if args.docs_rel:
                        # ex: assets/reports/by_class_YYYY.../class/...
                        tail = os.path.join(os.path.basename(plots_parent), c, basename)
                        return os.path.join(args.docs_rel, tail).replace("\\","/")
                    return os.path.relpath(full, start=os.path.dirname(out_path)).replace("\\","/")
                for suff in ("__hist_kde.png","__box.png","__violin.png"):
                    p = relp(f"{m}{suff}")
                    if p: lines += [f"![{c} {m} {suff}]({p})"]
            lines += [""]

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"✅ Rapport par classe généré → {out_path}")

if __name__ == "__main__":
    main()