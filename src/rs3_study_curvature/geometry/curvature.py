from typing import Tuple
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import LineString, MultiLineString


def _linestring_to_xy(line: LineString) -> np.ndarray:
    return np.asarray(line.coords, dtype=float)


def _arclength(xy: np.ndarray) -> np.ndarray:
    seg = np.sqrt(np.sum(np.diff(xy, axis=0) ** 2, axis=1))
    s = np.concatenate([[0.0], np.cumsum(seg)])
    return s


def compute_curvature_along_line(
    line: LineString,
    step_m: float = 5.0,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Approxime la courbure (kappa) le long d'une LineString.
    - Discrétise la géométrie au pas step_m (m dans CRS métrique)
    - Utilise la formule de courbure discrète via dérivées finies.
    Retourne (s, kappa, radius) avec s en mètres depuis l'origine.
    """
    xy = _linestring_to_xy(line)
    s_raw = _arclength(xy)
    if s_raw[-1] < 3 * step_m:
        # trop court; renvoyer un seul point
        return np.array([0.0]), np.array([0.0]), np.array([np.inf])

    # re-échantillonnage régulier
    s_new = np.arange(0, s_raw[-1] + 1e-9, step_m)
    x_new = np.interp(s_new, s_raw, xy[:, 0])
    y_new = np.interp(s_new, s_raw, xy[:, 1])

    # dérivées finies centrales
    dx = np.gradient(x_new, step_m)
    dy = np.gradient(y_new, step_m)
    ddx = np.gradient(dx, step_m)
    ddy = np.gradient(dy, step_m)

    denom = (dx * dx + dy * dy) ** 1.5 + 1e-12
    kappa = np.abs(dx * ddy - dy * ddx) / denom
    with np.errstate(divide="ignore"):
        radius = np.where(kappa > 0, 1.0 / kappa, np.inf)
    return s_new, kappa, radius


def annotate_curvature_on_gdf(gdf_m: gpd.GeoDataFrame, step_m: float = 5.0) -> gpd.GeoDataFrame:
    """
    gdf_m en CRS métrique. Explode les lignes et calcule des stats simples de courbure.
    """
    # Empty guard: if no edges, return an empty GeoDataFrame with expected schema
    if gdf_m is None or len(gdf_m) == 0:
        cols = ["s_len_m", "kappa_mean", "kappa_max", "radius_min", "geometry"]
        df = pd.DataFrame(columns=cols)
        return gpd.GeoDataFrame(df, geometry="geometry", crs=getattr(gdf_m, "crs", 3857))

    rows = []
    for _, row in gdf_m.iterrows():
        geom = row.geometry
        if geom is None:
            continue
        # iterate parts: accept LineString or MultiLineString
        parts = []
        if isinstance(geom, LineString):
            parts = [geom]
        elif isinstance(geom, MultiLineString):
            parts = list(geom.geoms)
        else:
            continue
        for part in parts:
            s, k, r = compute_curvature_along_line(part, step_m=step_m)
            rows.append(
                {
                    **{k_: row.get(k_) for k_ in row.index if k_ != "geometry"},
                    "s_len_m": float(s[-1]),
                    "kappa_mean": float(np.nanmean(k)) if k.size else np.nan,
                    "kappa_max": float(np.nanmax(k)) if k.size else np.nan,
                    "radius_min": float(np.nanmin(r[np.isfinite(r)])) if r.size and np.any(np.isfinite(r)) else np.inf,
                    "geometry": part,
                }
            )
    # If nothing was computed, return an empty GeoDataFrame with the expected schema
    if not rows:
        cols = ["s_len_m", "kappa_mean", "kappa_max", "radius_min", "geometry"]
        df = pd.DataFrame(columns=cols)
        return gpd.GeoDataFrame(df, geometry="geometry", crs=gdf_m.crs)
    return gpd.GeoDataFrame(pd.DataFrame(rows), geometry="geometry", crs=gdf_m.crs)
