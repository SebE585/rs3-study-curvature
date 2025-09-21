.PHONY: venv install etl test docs serve

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

QUANTS_DIR=/Users/sebastien.edet/rs3-data/ref/roadinfo
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