from pathlib import Path
from typing import Optional
import matplotlib.pyplot as plt
import geopandas as gpd
from .helpers import theme
from matplotlib.lines import Line2D
from matplotlib.patches import Patch


def _try_contextily(ax, gdf):
    try:
        import contextily as cx

        gdf3857 = gdf.to_crs(3857)
        cx.add_basemap(ax, source=cx.providers.Stamen.TonerLite)
        return gdf3857
    except Exception:
        return None


def plot_map(
    out_png: str,
    edges: gpd.GeoDataFrame,
    buffer: Optional[gpd.GeoDataFrame] = None,
    candidates: Optional[gpd.GeoDataFrame] = None,
    samples: Optional[gpd.GeoDataFrame] = None,
    clothoid_fits: Optional[gpd.GeoDataFrame] = None,
    title: str = "RS3 — Carte",
    legend_loc: str = "lower right",
    edge_color: str = "#B0B0B0",
    cand_color: str = "#1f77b4",
    clothoid_color: str = "#d62728",
    buffer_alpha: float = 0.1,
):
    theme()
    # If no edges, render a minimal map (optional buffer + title) and exit gracefully
    if edges is None or len(edges) == 0:
        fig, ax = plt.subplots(figsize=(8, 8))
        try:
            if buffer is not None and len(buffer):
                # Try plotting buffer in WebMercator to be consistent with basemap style if added later
                try:
                    buffer.to_crs(3857).plot(ax=ax, color=cand_color, alpha=buffer_alpha, edgecolor="none")
                except Exception:
                    buffer.plot(ax=ax, color=cand_color, alpha=buffer_alpha, edgecolor="none")
        except Exception:
            pass
        ax.set_title(title)
        ax.set_axis_off()
        Path(out_png).parent.mkdir(parents=True, exist_ok=True)
        fig.tight_layout()
        fig.savefig(out_png, dpi=200)
        plt.close(fig)
        print(f"✅ Carte enregistrée (vide): {out_png}")
        return

    fig, ax = plt.subplots(figsize=(8, 8))

    gdf = edges
    used_3857 = False
    gdf3857 = _try_contextily(ax, gdf)
    if gdf3857 is not None:
        used_3857 = True
        gdf_to_plot = gdf3857
    else:
        gdf_to_plot = gdf

    # Base network in light gray for context
    gdf_to_plot.plot(ax=ax, linewidth=1.6, color=edge_color)

    # Optional: highlight candidate segments passing the R filter
    if candidates is not None and len(candidates):
        cand_to_plot = candidates.to_crs(3857) if used_3857 else candidates
        cand_to_plot.plot(ax=ax, linewidth=2.2, color=cand_color)

    if buffer is not None and len(buffer):
        (buffer.to_crs(3857) if used_3857 else buffer).plot(ax=ax, color=cand_color, alpha=buffer_alpha)

    if clothoid_fits is not None and len(clothoid_fits):
        (clothoid_fits.to_crs(3857) if used_3857 else clothoid_fits).plot(ax=ax, color=clothoid_color, linewidth=3)

    if samples is not None and len(samples):
        (samples.to_crs(3857) if used_3857 else samples).plot(ax=ax, color="#ff7f0e", markersize=8)

    # Manual legend (avoid PatchCollection warning by creating custom handles)
    legend_handles = [Line2D([0], [0], color=edge_color, lw=2, label="Réseau (toutes rues)")]
    if candidates is not None and len(candidates):
        legend_handles.append(Line2D([0], [0], color=cand_color, lw=2.2, label="Candidats (R filtré)"))
    if buffer is not None:
        legend_handles.append(Patch(facecolor=cand_color, alpha=buffer_alpha, label="Buffer"))
    if clothoid_fits is not None and len(clothoid_fits):
        legend_handles.append(Line2D([0], [0], color=clothoid_color, lw=3, label="Clothoïde (fit)"))
    if samples is not None and len(samples):
        legend_handles.append(Line2D([0], [0], marker="o", linestyle="None", label="Échantillons"))

    # Optional context note (data source and R filter) from env
    import os

    src = os.environ.get("RS3_STREETS_SOURCE")
    rmin = os.environ.get("RS3_RADIUS_MIN_M")
    rmax = os.environ.get("RS3_R_VISU_MAX_M")
    note_parts = []
    if src:
        note_parts.append(f"source={src}")
    if rmin or rmax:
        note_parts.append(f"R∈[{rmin or '—'}; {rmax or '—'}] m")
    if note_parts:
        ax.text(0.01, 0.01, " | ".join(note_parts), transform=ax.transAxes, fontsize=9, ha="left", va="bottom", alpha=0.7)

    ax.set_title(title)
    try:
        if legend_handles:
            ax.legend(handles=legend_handles, loc=legend_loc, framealpha=0.85)
    except Exception:
        pass
    Path(out_png).parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out_png)
    plt.close(fig)
