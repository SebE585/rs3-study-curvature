# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, List, Tuple
import numpy as np
import pandas as pd
from scipy import stats


@dataclass
class TestResult:
    metric: str
    n_osm: int
    n_bd: int
    mean_osm: float
    mean_bd: float
    std_osm: float
    std_bd: float
    diff_mean: float
    # Tests
    t_welch: float
    p_t_welch: float
    ks_stat: float
    p_ks: float
    mw_stat: float
    p_mw: float
    # Tailles d'effet
    cohens_d: float
    cliffs_delta: float


def _cohens_d(x: np.ndarray, y: np.ndarray) -> float:
    # Welch-cohens d (pooled via deux variances avec tailles différentes)
    nx, ny = len(x), len(y)
    vx, vy = x.var(ddof=1), y.var(ddof=1)
    pooled = ((nx - 1) * vx + (ny - 1) * vy) / (nx + ny - 2) if (nx + ny - 2) > 0 else np.nan
    if pooled <= 0 or np.isnan(pooled):
        return np.nan
    return (np.mean(x) - np.mean(y)) / np.sqrt(pooled)


def _cliffs_delta(x: np.ndarray, y: np.ndarray) -> float:
    # Mesure non-paramétrique d'effet (entre -1 et 1)
    # Implémentation O((n+m) log (n+m)) via tri et comptage.
    x_sorted = np.sort(x)
    y_sorted = np.sort(y)
    i = j = more = less = 0
    nx, ny = len(x_sorted), len(y_sorted)
    while i < nx and j < ny:
        if x_sorted[i] > y_sorted[j]:
            more += nx - i
            j += 1
        elif x_sorted[i] < y_sorted[j]:
            less += ny - j
            i += 1
        else:
            # égalité : avancer les deux
            i += 1
            j += 1
    denom = nx * ny
    return (more - less) / denom if denom else np.nan


def run_all_tests(a: np.ndarray, b: np.ndarray) -> Tuple[float, float, float, float, float, float]:
    # Welch t-test (variances potentiellement inégales)
    t_welch, p_t = stats.ttest_ind(a, b, equal_var=False, nan_policy="omit")
    # KS test (distributions)
    ks_stat, p_ks = stats.ks_2samp(a, b, method="asymp")
    # Mann-Whitney (différence de rangs)
    mw_stat, p_mw = stats.mannwhitneyu(a, b, alternative="two-sided", method="asymptotic")
    return t_welch, p_t, ks_stat, p_ks, mw_stat, p_mw


def summarize_metric(metric: str, a: np.ndarray, b: np.ndarray) -> TestResult:
    a = a[~np.isnan(a)]
    b = b[~np.isnan(b)]
    t_welch, p_t, ks_stat, p_ks, mw_stat, p_mw = run_all_tests(a, b)
    return TestResult(
        metric=metric,
        n_osm=len(a),
        n_bd=len(b),
        mean_osm=float(np.mean(a)) if len(a) else np.nan,
        mean_bd=float(np.mean(b)) if len(b) else np.nan,
        std_osm=float(np.std(a, ddof=1)) if len(a) > 1 else np.nan,
        std_bd=float(np.std(b, ddof=1)) if len(b) > 1 else np.nan,
        diff_mean=float(np.mean(a) - np.mean(b)) if len(a) and len(b) else np.nan,
        t_welch=float(t_welch) if np.isfinite(t_welch) else np.nan,
        p_t_welch=float(p_t) if np.isfinite(p_t) else np.nan,
        ks_stat=float(ks_stat),
        p_ks=float(p_ks),
        mw_stat=float(mw_stat),
        p_mw=float(p_mw),
        cohens_d=float(_cohens_d(a, b)),
        cliffs_delta=float(_cliffs_delta(a, b)),
    )


def results_to_df(results: List[TestResult]) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []
    for r in results:
        rows.append(r.__dict__)
    cols = [
        "metric",
        "n_osm",
        "n_bd",
        "mean_osm",
        "mean_bd",
        "std_osm",
        "std_bd",
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
    return pd.DataFrame(rows)[cols]
