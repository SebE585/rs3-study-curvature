.PHONY: help venv install install-dev fmt fix lint typecheck test check etl stats stats-by-class plots figures profiles report docs docs-serve serve clean clean-pyc clean-all env pre-commit _ensure_cli linkedin-map linkedin-distrib romilly compare-osm-ign analyze-stats

.DEFAULT_GOAL := help
SHELL := /bin/bash

# Virtualenv activation prefix for all commands
PY = . .venv/bin/activate &&
PYTHON := .venv/bin/python
PIP := .venv/bin/pip
CFG ?= configs/config.yaml
OUT_DIR_LINKEDIN ?= out/plots/linkedin
OUT_DIR_ROMILLY  ?= out/romilly

# Data paths
RS3_DATA_ROOT ?= ../../rs3-data
RS3_OSM_PATH ?= $(RS3_DATA_ROOT)/osm/normandie-highways.geojson
RS3_IGN_PATH ?= $(RS3_DATA_ROOT)/bdtopo/troncon_de_route.gpkg
RS3_STREETS_SOURCE ?= osm

# Tool shortcuts
RUFF := ruff
MYPY := mypy
PYTEST := pytest -q
MYPY_FLAGS := --ignore-missing-imports --namespace-packages

## Ensure CLI runtime deps are present (typer)
_ensure_cli:
	${PY} python -c "import typer" >/dev/null 2>&1 || ${PY} pip install --quiet typer

## Show this help
help:
	@grep -E '^[a-zA-Z0-9][^:]*:.*##' $(MAKEFILE_LIST) | sort | awk -F':|##' '{printf "\033[36m%-18s\033[0m %s\n", $$1, $$3}'

## Create virtualenv and upgrade pip
venv:
	python -m venv .venv && ${PY} pip install -U pip

## Install project (runtime) deps
install: venv
	${PY} pip install -e .[docs]

## Install project with dev extras (lint, test, docs)
install-dev: venv
	${PY} pip install -e .[docs,dev]

## Format code (ruff format)
fmt:
	${PY} ${RUFF} format src tests

## Autofix lint issues where safe, then format
fix:
	${PY} ${RUFF} check --fix src tests || true
	${PY} ${RUFF} format src tests

## Lint code (ruff + mypy)
lint:
	${PY} ${RUFF} check src tests
	${PY} ${MYPY} ${MYPY_FLAGS} src

## Type check only (mypy)
typecheck:
	${PY} ${MYPY} ${MYPY_FLAGS} src

## Run tests (pytest -q)
test:
	${PY} ${PYTEST}

## Convenience: format + lint + test
check: fmt lint test

## Run ETL from config
etl: _ensure_cli
	${PY} ${PYTHON} -m rs3_study_curvature.cli.main compute from-config $(CFG)

## Compute global stats
stats: _ensure_cli
	${PY} ${PYTHON} -m rs3_study_curvature.cli.main stats global $(CFG)

## Compute stats by class
stats-by-class: _ensure_cli
	${PY} ${PYTHON} -m rs3_study_curvature.cli.main stats by-class $(CFG)

## Generate plots (distributions and by-class)
plots: _ensure_cli
	${PY} ${PYTHON} -m rs3_study_curvature.cli.main plots distributions $(CFG)
	${PY} ${PYTHON} -m rs3_study_curvature.cli.main plots by-class $(CFG)

## Alias: generate figures (same as plots)
figures: plots

## Generate κ profiles plots
profiles: _ensure_cli
	${PY} ${PYTHON} -m rs3_study_curvature.cli.main plots profiles $(CFG)

## Build Markdown report
report: _ensure_cli
	mkdir -p out/reports
	@echo "[report] Building Markdown report via Typer CLI..."
	${PY} ${PYTHON} -m rs3_study_curvature.cli.main report curves $(CFG) out/reports/curves.md

## Build docs (MkDocs)
docs:
	${PY} python -c "import mkdocs" >/dev/null 2>&1 || ${PY} ${PIP} install --quiet mkdocs
	${PY} mkdocs build --strict

report-doc: report
	mkdir -p docs/reports
	cp -f out/reports/curves.md docs/reports/curves.md

## Serve docs locally
docs-serve: serve
## Serve docs locally (alias)
serve:
	${PY} python -c "import mkdocs" >/dev/null 2>&1 || ${PY} ${PIP} install --quiet mkdocs
	${PY} mkdocs serve -a 0.0.0.0:8000

## Clean generated artifacts (out/ and processed data)
clean:
	rm -rf out/* data/interim/* data/processed/*

## Clean Python caches
clean-pyc:
	find . -name "__pycache__" -type d -prune -exec rm -rf {} +; \
	find . -name "*.pyc" -o -name "*.pyo" -delete

## Clean everything (artifacts + caches)
clean-all: clean clean-pyc

## Show environment info
env:
	${PY} python -V && ${PY} pip -V && ${PY} pip list | head -n 20

## Run pre-commit hooks on all files
pre-commit:
	${PY} pre-commit run --all-files

linkedin-map:
	# Usage: make linkedin-map BBOX="minx miny maxx maxy" STREET="Rue Blingue" BUF=40
	RS3_STREETS_SOURCE=$(RS3_STREETS_SOURCE) RS3_OSM_PATH=$(RS3_OSM_PATH) RS3_IGN_PATH=$(RS3_IGN_PATH) \
	python -m rs3_study_curvature.cli linkedin-map \
	  --out-dir $(OUT_DIR_LINKEDIN) \
	  $(BBOX) \
	  $(if $(STREET),--street "$(STREET)") \
	  --street-buffer-m $(if $(BUF),$(BUF),40) \
	  --fit-clothoid

linkedin-distrib:
	# Usage: make linkedin-distrib BBOX="minx miny maxx maxy"
	RS3_STREETS_SOURCE=$(RS3_STREETS_SOURCE) RS3_OSM_PATH=$(RS3_OSM_PATH) RS3_IGN_PATH=$(RS3_IGN_PATH) \
	python -m rs3_study_curvature.cli linkedin-distrib \
	  --out-dir $(OUT_DIR_LINKEDIN) \
	  $(BBOX)

romilly:
	# Usage: make romilly BBOX="minx miny maxx maxy" STREET="Rue Blingue" BUF=40
	RS3_STREETS_SOURCE=$(RS3_STREETS_SOURCE) RS3_OSM_PATH=$(RS3_OSM_PATH) RS3_IGN_PATH=$(RS3_IGN_PATH) \
	python -m rs3_study_curvature.cli romilly-analyze \
	  --out-dir $(OUT_DIR_ROMILLY) \
	  $(BBOX) \
	  $(if $(STREET),--street "$(STREET)") \
	  --street-buffer-m $(if $(BUF),$(BUF),40)

compare-osm-ign:
	# Usage: make compare-osm-ign BBOX="minx miny maxx maxy" STREET="Rue ..." BUF=40
	# Génère deux cartes: OSM -> $(OUT_DIR_LINKEDIN)_osm, IGN -> $(OUT_DIR_LINKEDIN)_ign
	$(MAKE) linkedin-map BBOX="$(BBOX)" STREET="$(STREET)" BUF="$(BUF)" OUT_DIR_LINKEDIN=$(OUT_DIR_LINKEDIN)_osm RS3_STREETS_SOURCE=osm
	$(MAKE) linkedin-map BBOX="$(BBOX)" STREET="$(STREET)" BUF="$(BUF)" OUT_DIR_LINKEDIN=$(OUT_DIR_LINKEDIN)_ign RS3_STREETS_SOURCE=ign

analyze-stats:
	# Summarize curvature stats into Markdown
	mkdir -p out/stats
	${PY} ${PYTHON} scripts/analyze_stats.py


## Publish changes: lint, commit, and push
publish:
	@set -e; \
	git add -A; \
	${PY} pre-commit run -a || ( \
		echo "🔁 pre-commit fixed files; re-adding and re-running..."; \
		git add -A; \
		${PY} pre-commit run -a \
	); \
	git commit -m "$${MSG:-Auto: publish}" || echo "Nothing to commit"; \
	git push

## Emergency publish (skip hooks) — use only if hooks block and you understand the risks
publish-now:
	@git add -A
	@git commit -m "$${MSG:-Emergency publish (no hooks)}" || echo "Nothing to commit"
	@git push
