.PHONY: help venv install install-dev fmt fix lint typecheck test check etl stats stats-by-class plots figures profiles report docs docs-serve serve clean clean-pyc clean-all env pre-commit _ensure_cli

.DEFAULT_GOAL := help
SHELL := /bin/bash

# Virtualenv activation prefix for all commands
PY = . .venv/bin/activate &&
PYTHON := .venv/bin/python
PIP := .venv/bin/pip
CFG ?= configs/config.yaml

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
