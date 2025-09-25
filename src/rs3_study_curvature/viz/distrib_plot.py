from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from .helpers import theme


def plot_distributions(out_png: str, df: pd.DataFrame, r_col: str = "radius_min", k_col: str = "kappa_max", title: str = "RS3 — Distributions"):
    theme()
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))

    # Rayon
    r = df[r_col].replace([np.inf, -np.inf], np.nan).dropna()
    axes[0].hist(np.clip(r, 0, np.percentile(r, 99)), bins=40)
    axes[0].set_title("Distribution du rayon (m)")
    axes[0].set_xlabel("R (m)")
    axes[0].set_ylabel("Count")

    # Kappa
    k = df[k_col].replace([np.inf, -np.inf], np.nan).dropna()
    axes[1].hist(np.clip(k, 0, np.percentile(k, 99)), bins=40)
    axes[1].set_title("Distribution de la courbure κ (1/m)")
    axes[1].set_xlabel("κ")
    axes[1].set_ylabel("Count")

    fig.suptitle(title)
    fig.tight_layout()
    Path(out_png).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png)
    plt.close(fig)
