import pandas as pd
import numpy as np

def summarize_segments(df: pd.DataFrame) -> pd.DataFrame:
    q = df.quantile([0.5, 0.85, 0.95])
    return pd.DataFrame({
        "n": [len(df)],
        "radius_p85_m_med": [q.loc[0.5, "radius_p85_m"]],
        "curv_mean_1perm_med": [q.loc[0.5, "curv_mean_1perm"]],
    })