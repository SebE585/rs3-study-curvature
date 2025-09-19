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