from dataclasses import dataclass
import numpy as np
from shapely.geometry import LineString


@dataclass
class ClothoidFit:
    k0: float
    k1: float
    r2: float
    s_start: float
    s_end: float


def fit_local_clothoid(line_m: LineString, step_m: float = 8.0, window_m: float = 60.0) -> ClothoidFit:
    """
    Ajuste kappa(s) ~ k0 + k1*s sur une fenêtre locale le long de la ligne.
    Simplification robuste (moindres carrés avec intercept).
    Retourne paramètres et R².
    """
    from rs3_study_curvature.geometry.curvature import compute_curvature_along_line, _arclength

    xy = np.asarray(line_m.coords, dtype=float)
    s_raw = _arclength(xy)
    if s_raw[-1] < window_m:
        s, kappa, _ = compute_curvature_along_line(line_m, step_m=step_m)
        X = np.c_[np.ones_like(s), s]
        coef, *_ = np.linalg.lstsq(X, kappa, rcond=None)
        yhat = X @ coef
        ss_res = float(np.sum((kappa - yhat) ** 2))
        ss_tot = float(np.sum((kappa - kappa.mean()) ** 2) + 1e-12)
        r2 = 1.0 - ss_res / ss_tot
        return ClothoidFit(k0=float(coef[0]), k1=float(coef[1]), r2=r2, s_start=0.0, s_end=float(s[-1]))

    # Prend la fenêtre au centre
    s_mid = 0.5 * s_raw[-1]
    s_a, s_b = s_mid - 0.5 * window_m, s_mid + 0.5 * window_m
    s, kappa, _ = compute_curvature_along_line(line_m, step_m=step_m)
    mask = (s >= max(0.0, s_a)) & (s <= min(s_b, s[-1]))
    s_loc, k_loc = s[mask], kappa[mask]
    X = np.c_[np.ones_like(s_loc), s_loc]
    coef, *_ = np.linalg.lstsq(X, k_loc, rcond=None)
    yhat = X @ coef
    ss_res = float(np.sum((k_loc - yhat) ** 2))
    ss_tot = float(np.sum((k_loc - k_loc.mean()) ** 2) + 1e-12)
    r2 = 1.0 - ss_res / ss_tot
    return ClothoidFit(k0=float(coef[0]), k1=float(coef[1]), r2=r2, s_start=float(s_loc[0]), s_end=float(s_loc[-1]))
