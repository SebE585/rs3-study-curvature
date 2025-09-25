import numpy as np
import pandas as pd


def summary_radius(df: pd.DataFrame, r_col: str = "radius_min") -> pd.DataFrame:
    r = df[r_col].replace([np.inf, -np.inf], np.nan).dropna()
    return pd.DataFrame(
        {
            "n": [len(r)],
            "min": [float(np.min(r))] if len(r) else [np.nan],
            "p50": [float(np.median(r))] if len(r) else [np.nan],
            "p90": [float(np.percentile(r, 90))] if len(r) else [np.nan],
        }
    )
