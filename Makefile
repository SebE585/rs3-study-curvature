.PHONY: venv install etl test docs serve figs quantiles stats dists all report report-docs

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
	@if [ -d "$(LATEST_PLOTS)" ]; then cp -R $(LATEST_PLOTS)/* $(PLOTS_DOCS_DIR)/; fi
	. .venv/bin/activate && $(PY) scripts/gen_report.py \
		--config $(CONF) \
		--stats $(LATEST_STATS) \
		--plots-dir $(PLOTS_DOCS_DIR) \
		--docs-rel assets/reports/$(notdir $(LATEST_PLOTS)) \
		--out $(REPORT_DOCS)
	@echo "✅ Rapport + figures prêts pour MkDocs → $(REPORT_DOCS) et $(PLOTS_DOCS_DIR)"

# 3) Tout en une passe
all: stats dists
	@echo "✅ Stats + Distributions générées."