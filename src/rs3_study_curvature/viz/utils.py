# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Optional
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def _setup_figure(width: float, height: float, dpi: int):
    fig = plt.figure(figsize=(width, height), dpi=dpi)
    ax = fig.add_subplot(111)
    return fig, ax


def plot_hist_kde(
    df_a: pd.DataFrame,
    df_b: pd.DataFrame,
    col: str,
    label_a: str,
    label_b: str,
    bins="fd",
    kde: bool = True,
    width: float = 9.0,
    height: float = 6.0,
    dpi: int = 140,
    out_path: Optional[str] = None,
    xlabel: Optional[str] = None,
):
    a = pd.to_numeric(df_a[col], errors="coerce").dropna().values
    b = pd.to_numeric(df_b[col], errors="coerce").dropna().values

    fig, ax = _setup_figure(width, height, dpi)
    ax.hist(a, bins=bins, alpha=0.6, density=True, label=label_a)
    ax.hist(b, bins=bins, alpha=0.6, density=True, label=label_b)
    ax.set_title(f"Distribution — {col}")
    ax.set_xlabel(xlabel or col)
    ax.set_ylabel("Densité")
    ax.legend()

    if kde:
        try:
            from scipy.stats import gaussian_kde

            grid = np.linspace(
                np.nanmin([a.min() if len(a) else np.nan, b.min() if len(b) else np.nan]),
                np.nanmax([a.max() if len(a) else np.nan, b.max() if len(b) else np.nan]),
                400,
            )
            if len(a) > 1:
                ax.plot(grid, gaussian_kde(a)(grid), linewidth=1.5, label=f"KDE {label_a}")
            if len(b) > 1:
                ax.plot(grid, gaussian_kde(b)(grid), linewidth=1.5, label=f"KDE {label_b}")
        except Exception:
            pass

    fig.tight_layout()
    if out_path:
        fig.savefig(out_path)
    plt.close(fig)


def plot_box_violin(
    df_a: pd.DataFrame,
    df_b: pd.DataFrame,
    col: str,
    label_a: str,
    label_b: str,
    width: float = 9.0,
    height: float = 6.0,
    dpi: int = 140,
    out_path_box: Optional[str] = None,
    out_path_violin: Optional[str] = None,
    xlabel: Optional[str] = None,
):
    a = pd.to_numeric(df_a[col], errors="coerce").dropna().values
    b = pd.to_numeric(df_b[col], errors="coerce").dropna().values

    # Boxplot
    fig_b, ax_b = _setup_figure(width, height, dpi)
    ax_b.boxplot([a, b], labels=[label_a, label_b], showfliers=False)
    ax_b.set_title(f"Boxplot — {col}")
    ax_b.set_ylabel(xlabel or col)
    fig_b.tight_layout()
    if out_path_box:
        fig_b.savefig(out_path_box)
    plt.close(fig_b)

    # Violin
    fig_v, ax_v = _setup_figure(width, height, dpi)
    # parts = ax_v.violinplot([a, b], showmeans=True, showextrema=True, showmedians=True)
    ax_v.set_xticks([1, 2], [label_a, label_b])
    ax_v.set_title(f"Violin — {col}")
    ax_v.set_ylabel(xlabel or col)
    fig_v.tight_layout()
    if out_path_violin:
        fig_v.savefig(out_path_violin)
    plt.close(fig_v)
