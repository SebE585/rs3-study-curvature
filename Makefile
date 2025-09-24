.PHONY: venv install etl test docs serve figs quantiles stats dists all report report-docs report-by-class report-by-class-docs bias-sweep bias-sweep-docs curves curves-all curves-all-rows match-curves curve-profiles curve-stats curve-stats-by-class curve-stats-rows report-curves report-curves-docs

venv:
	python -m venv .venv && . .venv/bin/activate && pip install -U pip

install:
	. .venv/bin/activate && pip install -e .[docs]

etl:
	. .venv/bin/activate && python -m rs3_study_curvature.cli.build_curvature --config configs/config.yaml

test:
	. .venv/bin/activate && pytest

docs:
	. .venv/bin/activate && mkdocs build

serve:
	. .venv/bin/activate && mkdocs serve -a 0.0.0.0:8000

figs:
	python tools/compare_quick.py --in-dir $(OUT) --osm-name roadinfo_segments_osm.parquet --bd-name roadinfo_segments_bdtopo.parquet --q 0.99 --drop-inf
	python tools/compare_nearest.py --in-dir $(OUT) --osm-name roadinfo_segments_osm.parquet --bd-name roadinfo_segments_bdtopo.parquet --max-dist 30 --match-class
	python tools/make_gpkg_hotspots.py --in-dir $(OUT) --osm-name roadinfo_segments_osm.parquet --bd-name roadinfo_segments_bdtopo.parquet --metric diff_curv_mean_1perm --top-n 5000 --out $(OUT)/compare__hotspots.gpkg

DISTS=20 30 50

QUANTS_DIR=/Users/sebastien.edet/rs3-data/ref/roadinfo
OUT ?= $(QUANTS_DIR)
DISTS=20 30 50

quantiles:
	for d in $(DISTS); do \
	  python tools/compare_nearest.py \
	    --in-dir "$(QUANTS_DIR)" \
	    --osm-name roadinfo_segments_osm.parquet \
	    --bd-name  roadinfo_segments_bdtopo.parquet \
	    --max-dist $$d \
	    --metrics "length_m,radius_min_m,curv_mean_1perm" \
	    --drop-inf \
	    --quantiles "0.10,0.25,0.50,0.75,0.90" \
	    --out-summary   "$(QUANTS_DIR)/nearest_diffs_d$${d}.csv" \
	    --out-quantiles "$(QUANTS_DIR)/nearest_quants_d$${d}.csv"; \
	done; \
	python tools/plot_quantiles.py \
	  --in-files \
	    "$(QUANTS_DIR)/nearest_quants_d20.csv" \
	    "$(QUANTS_DIR)/nearest_quants_d30.csv" \
	    "$(QUANTS_DIR)/nearest_quants_d50.csv" \
	  --out-dir "$(QUANTS_DIR)/figs_quantiles" \
	  --metrics "diff_length_m,diff_radius_min_m,diff_curv_mean_1perm" \
	  --q-bands "0.10,0.50,0.90;0.25,0.75"

# === Stats & Distributions (global) ===

# Python interpreter (inside venv)
PY ?= python

# Config for stats/distributions (align with project convention `configs/`)
CONF ?= configs/config.yaml

# Latest artifacts helpers
LATEST_STATS := $(shell ls -t out/stats/global_tests_*.csv 2>/dev/null | head -1)
LATEST_PLOTS := $(shell ls -dt out/plots/global_* 2>/dev/null | head -1)
REPORT_DOCS  := docs/reports/curvature_report.md
PLOTS_DOCS_DIR := docs/assets/reports/$(notdir $(LATEST_PLOTS))

# 1) Tests statistiques globaux (OSM vs BD TOPO)
stats:
	. .venv/bin/activate && $(PY) scripts/run_stats.py --config $(CONF)

# 2) Distributions globales (histos/KDE/box/violin)
dists:
	. .venv/bin/activate && $(PY) scripts/plot_distributions.py --config $(CONF)

# 4) Rapport Markdown auto-généré
report:
	. .venv/bin/activate && $(PY) scripts/gen_report.py --config $(CONF) --stats $(LATEST_STATS) --plots-dir $(LATEST_PLOTS) --out out/report.md


# 5) Copier le rapport + figures dans la doc MkDocs
report-docs: report
	@mkdir -p docs/reports
	@mkdir -p $(PLOTS_DOCS_DIR)
	@if [ -d "$(LATEST_PLOTS)" ]; then cp -R $(LATEST_PLOTS)/. $(PLOTS_DOCS_DIR)/; fi
	. .venv/bin/activate && $(PY) scripts/gen_report.py \
		--config $(CONF) \
		--stats $(LATEST_STATS) \
		--plots-dir $(PLOTS_DOCS_DIR) \
		--docs-rel ../assets/reports/$(notdir $(LATEST_PLOTS)) \
		--out $(REPORT_DOCS)
	@echo "✅ Rapport + figures prêts pour MkDocs → $(REPORT_DOCS) et $(PLOTS_DOCS_DIR)"

# --- Analyses par classe ---
stats-by-class:
	. .venv/bin/activate && $(PY) scripts/run_stats_by_class.py --config $(CONF)

dists-by-class:
	. .venv/bin/activate && $(PY) scripts/plot_distributions_by_class.py --config $(CONF)

report-by-class:
	. .venv/bin/activate && $(PY) scripts/gen_report_by_class.py --config $(CONF) --out out/report_by_class.md

report-by-class-docs: report-by-class
	@mkdir -p docs/reports
	@mkdir -p docs/assets/reports
	LATEST_PLOTS_BY_CLASS=$$(ls -dt out/plots/by_class_* 2>/dev/null | head -1); \
	if [ -n "$$LATEST_PLOTS_BY_CLASS" ]; then \
	  PLOTS_DOCS_DIR=docs/assets/reports/$$(basename $$LATEST_PLOTS_BY_CLASS); \
	  mkdir -p $$PLOTS_DOCS_DIR; \
	  cp -R $$LATEST_PLOTS_BY_CLASS/. $$PLOTS_DOCS_DIR/; \
	  . .venv/bin/activate && $(PY) scripts/gen_report_by_class.py \
		--config $(CONF) \
		--docs-rel ../assets/reports/$$(basename $$LATEST_PLOTS_BY_CLASS) \
		--out docs/reports/curvature_by_class.md; \
	  echo "✅ Rapport + figures par classe prêts pour MkDocs → docs/reports/curvature_by_class.md et $$PLOTS_DOCS_DIR"; \
	else \
	  echo "[WARN] Aucun plots par classe trouvé"; \
	fi

# --- Bias sweep (nécessite make quantiles au préalable) ---
bias-sweep:
	. .venv/bin/activate && $(PY) scripts/bias_sweep_matching.py \
		--in-dir "$(QUANTS_DIR)" \
		--metrics "diff_length_m,diff_radius_min_m,diff_curv_mean_1perm" \
		--q "0.50" \
		--out-dir "out/bias_sweep" \
		--out-md "docs/reports/bias_sweep.md"

bias-sweep-docs: bias-sweep
	@mkdir -p docs/reports
	@mkdir -p docs/assets/reports
	LATEST_BIAS_DIR=$$(ls -dt out/bias_sweep* 2>/dev/null | head -1); \
	if [ -n "$$LATEST_BIAS_DIR" ]; then \
	  PLOTS_DOCS_DIR=docs/assets/reports/$$(basename $$LATEST_BIAS_DIR); \
	  mkdir -p $$PLOTS_DOCS_DIR; \
	  cp -R $$LATEST_BIAS_DIR/. $$PLOTS_DOCS_DIR/; \
	  sed -i '' "s|out/bias_sweep|../assets/reports/$$(basename $$LATEST_BIAS_DIR)|g" docs/reports/bias_sweep.md; \
	  echo "✅ Rapport bias sweep + figures prêts pour MkDocs → docs/reports/bias_sweep.md et $$PLOTS_DOCS_DIR"; \
	else \
	  echo "[WARN] Aucun dossier bias_sweep trouvé"; \
	fi

mkdocs-publish:
	. .venv/bin/activate && mkdocs build
	. .venv/bin/activate && mkdocs gh-deploy

# --- Analyse des virages / courbure ------------------------------------------

CURVES_OUT := out/curves
CURVES_LAST := $(shell ls -dt $(CURVES_OUT) 2>/dev/null | head -1)

curves:
	@mkdir -p out/curves
	. .venv/bin/activate && $(PY) scripts/extract_curves.py --config $(CONF) --kappa-min 0.0001 --r-max 150 --out-dir out/curves

match-curves: curves
	. .venv/bin/activate && $(PY) scripts/match_curves.py \
		--osm out/curves/osm.parquet \
		--bd  out/curves/bd.parquet \
		--max-dist 50 \
		--len-ratio-max 2.0 \
		--out out/curves/matched.parquet

curve-profiles:
	. .venv/bin/activate && $(PY) scripts/curve_profiles.py \
		--config $(CONF) \
		--curves-osm out/curves/osm.parquet \
		--curves-bd  out/curves/bd.parquet \
		--out-dir out/plots

curve-stats: match-curves
	@mkdir -p out/stats
	. .venv/bin/activate && $(PY) scripts/curve_metrics.py \
		--matched out/curves/matched.parquet \
		--out-csv out/stats/curve_kpis.csv

report-curves: curve-profiles curve-stats
	@mkdir -p out
	# prends le dernier dossier de figures curves_*
	@LATEST_CURVES=$$(ls -dt out/plots/curves_* 2>/dev/null | head -1); \
	if [ -n "$$LATEST_CURVES" ]; then \
	  . .venv/bin/activate && $(PY) scripts/gen_report_curves.py \
		--kpis out/stats/curve_kpis.csv \
		--plots-dir $$LATEST_CURVES \
		--out out/curves_report.md; \
	  echo "✅ Rapport courbure → out/curves_report.md"; \
	else \
	  . .venv/bin/activate && $(PY) scripts/gen_report_curves.py \
		--kpis out/stats/curve_kpis.csv \
		--out out/curves_report.md; \
	  echo "⚠️  Rapport généré sans figures (lancez make curve-profiles)"; \
	fi

report-curves-docs: report-curves
	@mkdir -p docs/reports
	@mkdir -p docs/assets/reports
	@LATEST_CURVES=$$(ls -dt out/plots/curves_* 2>/dev/null | head -1); \
	if [ -n "$$LATEST_CURVES" ]; then \
	  PLOTS_DOCS_DIR=docs/assets/reports/$$(basename $$LATEST_CURVES); \
	  mkdir -p $$PLOTS_DOCS_DIR; \
	  cp -R $$LATEST_CURVES/. $$PLOTS_DOCS_DIR/; \
	  . .venv/bin/activate && $(PY) scripts/gen_report_curves.py \
		--kpis out/stats/curve_kpis.csv \
		--plots-dir $$LATEST_CURVES \
		--docs-rel ../assets/reports \
		--out docs/reports/curves_report.md; \
	  echo "✅ Rapport + figures courbure prêts → docs/reports/curves_report.md et $$PLOTS_DOCS_DIR"; \
	else \
	  . .venv/bin/activate && $(PY) scripts/gen_report_curves.py \
		--kpis out/stats/curve_kpis.csv \
		--docs-rel ../assets/reports \
		--out docs/reports/curves_report.md; \
	  echo "⚠️  Rapport courbure sans figures (pas de dossier out/plots/curves_*)"; \
	fi

curve-stats-by-class: match-curves
	@mkdir -p out/stats
	. .venv/bin/activate && $(PY) scripts/curve_metrics.py \
		--matched out/curves/matched.parquet \
		--out-csv out/stats/curve_kpis.csv \
		--by-class-csv out/stats/curve_kpis_by_class.csv
	@echo "✅ KPIs courbure (global + par classe) → out/stats/curve_kpis.csv et out/stats/curve_kpis_by_class.csv"

curve-stats-rows: match-curves
	@mkdir -p out/stats
	. .venv/bin/activate && $(PY) scripts/curve_metrics.py \
		--matched out/curves/matched.parquet \
		--out-csv out/stats/curve_kpis.csv \
		--by-class-csv out/stats/curve_kpis_by_class.csv \
		--save-rows out/stats/curve_kpis_rows.parquet
	@echo "✅ KPIs (global + par classe) + lignes → out/stats/curve_kpis_rows.parquet"

curves-all: curve-profiles curve-stats-by-class report-curves-docs
	@echo "✅ Courbes: profils + KPIs (global & par classe) + rapport doc"

curves-all-rows: curve-profiles curve-stats-rows report-curves-docs
	@echo "✅ Courbes: profils + KPIs (global, par classe & lignes) + rapport doc"

# 3) Tout en une passe
all: stats dists
	@echo "✅ Stats + Distributions générées."