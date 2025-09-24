# -*- coding: utf-8 -*-
from __future__ import annotations

import os
from typing import Tuple
import pandas as pd


def _read_any(path: str) -> pd.DataFrame:
    """
    Charge un CSV ou Parquet selon l'extension.
    - .csv/.tsv -> pandas.read_csv (séparateur auto pour .tsv)
    - .parquet -> pandas.read_parquet
    """
    ext = os.path.splitext(path)[1].lower()
    if ext == ".csv":
        return pd.read_csv(path)
    if ext == ".tsv":
        return pd.read_csv(path, sep="\t")
    if ext == ".parquet":
        return pd.read_parquet(path)
    raise ValueError(f"Format non supporté pour: {path}")


def load_pair(osm_path: str, bdtopo_path: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Charge OSM et BD TOPO en DataFrames."""
    osm = _read_any(osm_path)
    bd = _read_any(bdtopo_path)
    return osm, bd


def ensure_numeric_columns(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """Convertit en numérique les colonnes listées (coerce -> NaN si non convertible)."""
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def dropna_both(a: pd.Series, b: pd.Series):
    """Aligne deux Series et drop les NaN sur l'une ou l'autre."""
    s = pd.concat({"a": a, "b": b}, axis=1)
    s = s.dropna()
    return s["a"], s["b"]
