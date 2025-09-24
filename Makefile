.PHONY: help venv install install-dev fmt fix lint typecheck test check etl stats stats-by-class plots profiles report docs docs-serve serve clean clean-pyc clean-all env pre-commit

.DEFAULT_GOAL := help
SHELL := /bin/bash

# Virtualenv activation prefix for all commands
PY = . .venv/bin/activate &&
CFG ?= configs/config.yaml

# Tool shortcuts
RUFF := ruff
MYPY := mypy
PYTEST := pytest -q
MYPY_FLAGS := --ignore-missing-imports --namespace-packages

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
etl:
	${PY} rs3c compute from-config --config $(CFG)

## Compute global stats
stats:
	${PY} rs3c stats global --config $(CFG)

## Compute stats by class
stats-by-class:
	${PY} rs3c stats by-class --config $(CFG)

## Generate plots (distributions and by-class)
plots:
	${PY} rs3c plots distributions --config $(CFG)
	${PY} rs3c plots by-class --config $(CFG)

## Generate κ profiles plots
profiles:
	${PY} rs3c plots profiles --config $(CFG)

## Build Markdown report
report:
	mkdir -p out/reports
	${PY} rs3c report curves --config $(CFG) --out-md out/reports/curves.md

## Build docs (MkDocs)
docs:
	${PY} mkdocs build --strict

## Serve docs locally
docs-serve: serve
## Serve docs locally (alias)
serve:
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
