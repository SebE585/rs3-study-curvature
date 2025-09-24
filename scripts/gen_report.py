# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import os
import time
from typing import List, Dict

import yaml
import pandas as pd


def _ensure_dir(p: str):
    if p and not os.path.exists(p):
        os.makedirs(p, exist_ok=True)


def _auto_pick_latest(
    pattern_dir: str, prefix: str, ext: str | None = None
) -> str | None:
    """Return the lexicographically latest path within a directory for a given prefix.
    If ext is provided, filter files by that extension. Returns None if nothing found.
    """
    if not os.path.isdir(pattern_dir):
        return None
    candidates: List[str] = []
    for name in os.listdir(pattern_dir):
        full = os.path.join(pattern_dir, name)
        if not os.path.isdir(full) and ext is not None:
            if not name.endswith(ext):
                continue
        if os.path.basename(full).startswith(prefix) or prefix in full:
            candidates.append(full)
    if not candidates:
        return None
    candidates.sort(reverse=True)
    return candidates[0]


def _effect_size_bucket(d: float | None) -> str:
    if d is None or pd.isna(d):
        return "na"
    ad = abs(d)
    if ad < 0.2:  # Cohen's rule of thumb
        return "très faible"
    if ad < 0.5:
        return "faible"
    if ad < 0.8:
        return "moyen"
    return "fort"


def main():
    parser = argparse.ArgumentParser(
        description="Génère un rapport Markdown avec résultats stats + figures"
    )
    parser.add_argument("--config", required=True, help="YAML de configuration")
    parser.add_argument(
        "--stats",
        required=False,
        help="CSV résultats stats globaux (auto si non fourni)",
    )
    parser.add_argument(
        "--plots-dir",
        required=False,
        help="Répertoire des figures (auto si non fourni)",
    )
    parser.add_argument(
        "--out", default="out/report.md", help="Fichier de sortie Markdown"
    )
    parser.add_argument(
        "--title", default="Rapport comparatif OSM vs BD TOPO", help="Titre du rapport"
    )
    parser.add_argument(
        "--docs-rel",
        default=None,
        help="Chemin relatif depuis le rapport vers les figures (par ex. '../out/plots/...)'",
    )
    args = parser.parse_args()

    with open(args.config, "r") as f:
        cfg = yaml.safe_load(f)

    metrics = cfg.get("metrics", [])
    labels: Dict[str, str] = {m["name"]: m.get("label", m["name"]) for m in metrics}

    # Auto-pick latest stats CSV and plots dir if not provided
    stats_csv = args.stats or _auto_pick_latest("out/stats", "global_tests_", ".csv")
    plots_dir = args.plots_dir or _auto_pick_latest("out/plots", "global_")

    if not stats_csv or not os.path.exists(stats_csv):
        raise FileNotFoundError(
            "Impossible de localiser le CSV des résultats (utilise --stats)."
        )

    if not plots_dir or not os.path.isdir(plots_dir):
        print(
            "[WARN] Répertoire de figures introuvable — la section Distributions affichera seulement la table."
        )
        plots_dir = None

    df = pd.read_csv(stats_csv)

    out_path = args.out
    _ensure_dir(os.path.dirname(out_path))

    # Compute a few highlights
    highlights: List[str] = []
    for _, r in df.iterrows():
        metric = r.get("metric", "?")
        dmean = r.get("diff_mean")
        d = r.get("cohens_d")
        ks = r.get("ks_stat")
        bucket = _effect_size_bucket(d)
        arrow = (
            "↑" if (pd.notna(dmean) and dmean > 0) else ("↓" if pd.notna(dmean) else "")
        )
        if (pd.notna(d) and abs(d) >= 0.5) or (pd.notna(ks) and ks >= 0.2):
            highlights.append(
                f"**{metric}** : effet {bucket} (Cohen d={d:.2f}), KS={ks:.3f}, Δmoy={dmean:.3f} {arrow}"
            )

    # Build Markdown content
    lines: List[str] = []
    # YAML front-matter (MkDocs-compatible)
    lines.append("---")
    lines.append(f"title: {args.title}")
    lines.append(f"date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("---\n")

    lines.append(f"# {args.title}")
    lines.append("")
    lines.append(f"_Généré automatiquement le {time.strftime('%Y-%m-%d %H:%M:%S')}_")
    lines.append("")

    if highlights:
        lines.append("## Points saillants")
        for h in highlights:
            lines.append(f"- {h}")
        lines.append("")

    lines.append("## Résultats statistiques globaux")
    lines.append("")
    # Reorder/pretty-print table if columns present
    desired_cols = [
        "metric",
        "n_osm",
        "n_bd",
        "mean_osm",
        "mean_bd",
        "diff_mean",
        "t_welch",
        "p_t_welch",
        "ks_stat",
        "p_ks",
        "mw_stat",
        "p_mw",
        "cohens_d",
        "cliffs_delta",
    ]
    cols = [c for c in desired_cols if c in df.columns]
    df_print = df[cols] if cols else df
    lines.append(df_print.to_markdown(index=False))
    lines.append("")

    lines.append("## Distributions graphiques")
    lines.append("")

    # Which metrics to show? Use those present in the stats CSV (ensures coherence)
    for m in df["metric"].unique():
        label = labels.get(m, m)
        lines.append(f"### {label}")
        lines.append("")
        if plots_dir is None:
            lines.append("*Aucune figure disponible (répertoire introuvable).*\n")
            continue
        # Compute relative path to plots from the report location if requested
        base_dir = plots_dir
        rel_root = os.path.dirname(out_path)

        def _rel(p: str) -> str:
            full = os.path.join(base_dir, p)
            if args.docs_rel:
                # caller provided an explicit base relative root
                return os.path.join(args.docs_rel, p).replace("\\", "/")
            return os.path.relpath(full, start=rel_root).replace("\\", "/")

        # Files
        p_hist = f"{m}__hist_kde.png"
        p_box = f"{m}__box.png"
        p_vio = f"{m}__violin.png"

        any_fig = False
        if os.path.exists(os.path.join(base_dir, p_hist)):
            lines.append(f"![{m} hist]({_rel(p_hist)})")
            any_fig = True
        if os.path.exists(os.path.join(base_dir, p_box)):
            lines.append(f"![{m} box]({_rel(p_box)})")
            any_fig = True
        if os.path.exists(os.path.join(base_dir, p_vio)):
            lines.append(f"![{m} violin]({_rel(p_vio)})")
            any_fig = True
        if not any_fig:
            lines.append("*Aucune figure trouvée pour cette métrique.*")
        lines.append("")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"✅ Rapport Markdown généré → {out_path}")


if __name__ == "__main__":
    main()
