#!/usr/bin/env bash
set -euo pipefail

mkdir -p data/raw data/interim data/processed out/plots out/reports src/rs3_study_curvature/{etl,analysis,viz,io,cli}

# Déplacer scripts -> modules/CLI
git mv scripts/extract_curves.py              src/rs3_study_curvature/etl/compute_curvature.py || true
git mv scripts/run_stats.py                   src/rs3_study_curvature/analysis/stats.py        || true
git mv scripts/run_stats_by_class.py          src/rs3_study_curvature/analysis/stats_by_class.py || true
git mv scripts/gen_report_curves.py           src/rs3_study_curvature/analysis/report.py       || true
git mv scripts/plot_distributions.py          src/rs3_study_curvature/viz/plots.py             || true
git mv scripts/plot_distributions_by_class.py src/rs3_study_curvature/viz/plots_by_class.py    || true
git mv scripts/curve_profiles.py              src/rs3_study_curvature/viz/profiles.py          || true
git mv tools/*.py                             src/rs3_study_curvature/analysis/                || true

# I/O & utils
git mv src/rs3_study_curvature/io_utils.py    src/rs3_study_curvature/io/__init__.py           || true
git mv src/rs3_study_curvature/plot_utils.py  src/rs3_study_curvature/viz/utils.py             || true
git mv src/rs3_study_curvature/stats_utils.py src/rs3_study_curvature/analysis/utils.py        || true

# Sorties
mkdir -p out/plots out/reports
# Rien à supprimer: on garde l'historique git

echo "⚙️ Migration terminée. Ajuste les imports si besoin (analysis.utils, viz.utils, io.*)."
