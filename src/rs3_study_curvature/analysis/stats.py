from __future__ import annotations
from pathlib import Path
import pandas as pd
from typing import Any, Dict


def summarize_segments(df: pd.DataFrame) -> pd.DataFrame:
    q: Any = df.quantile([0.5, 0.85, 0.95])
    return pd.DataFrame(
        {
            "n": [len(df)],
            "radius_p85_m_med": [q.loc[0.5, "radius_p85_m"]],
            "curv_mean_1perm_med": [q.loc[0.5, "curv_mean_1perm"]],
        }
    )


def run_global_stats(config_path: Path) -> None:
    """
    CLI helper: compute and print a minimal global summary.
    Non-breaking placeholder; expand with real logic later.
    """
    import yaml  # type: ignore

    cfg: Dict[str, Any] = {}
    try:
        with open(config_path, "r") as f:
            cfg = yaml.safe_load(f) or {}
    except Exception:
        pass
    print("[stats] run_global_stats — config loaded with keys:", list(cfg.keys()))


def run_stats_by_class(config_path: Path) -> None:
    """
    CLI helper: compute and print a minimal per-class summary.
    Non-breaking placeholder; expand with real logic later.
    """
    print("[stats] run_stats_by_class — using config:", config_path)
