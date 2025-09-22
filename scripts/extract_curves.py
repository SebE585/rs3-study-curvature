# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse, os, yaml
import numpy as np, pandas as pd


def _ensure_dir(p: str):
    os.makedirs(p, exist_ok=True)


def _load(cfg_path: str):
    cfg = yaml.safe_load(open(cfg_path))
    osm = pd.read_parquet(cfg["inputs"]["osm"])
    bd  = pd.read_parquet(cfg["inputs"]["bdtopo"])
    return cfg, osm, bd


def _resolve_cols(df: pd.DataFrame):
    cols = {}
    cols["length"] = next((c for c in ["length_m","len_m","length"] if c in df.columns), None)
    cols["kappa"]  = next((c for c in ["curvature","curv_mean_1perm","curv_mean","kappa"] if c in df.columns), None)
    cols["radius"] = next((c for c in ["radius_min_m","radius_m","radius_p85_m"] if c in df.columns), None)
    cols["class"]  = next((c for c in ["class_norm","highway","class","road_class","fclass"] if c in df.columns), None)
    for c in ["x_centroid","y_centroid"]:
        if c not in df.columns:
            df[c] = np.nan
    return cols, df


def _flag_turns(df: pd.DataFrame, cols: dict, kappa_min: float, r_max: float) -> pd.Series:
    k = pd.to_numeric(df[cols["kappa"]], errors="coerce") if cols["kappa"] else None
    r = pd.to_numeric(df[cols["radius"]], errors="coerce") if cols["radius"] else None
    cond_k = (k.abs() >= kappa_min) if k is not None else pd.Series(False, index=df.index)
    cond_r = (r <= r_max) if r is not None else pd.Series(False, index=df.index)
    flags = (cond_k.fillna(False) | cond_r.fillna(False))
    # Fallback si aucun segment ne passe les seuils: prendre top 5% |kappa| ou bottom 5% rayon
    if not bool(flags.any()):
        if k is not None and k.notna().any():
            thr = k.abs().quantile(0.95)
            flags = (k.abs() >= thr)
        elif r is not None and r.notna().any():
            thr = r.quantile(0.05)
            flags = (r <= thr)
        else:
            flags = pd.Series(False, index=df.index)
    return flags.fillna(False)


def _group_consecutive(flags: pd.Series, road_id: pd.Series | None):
    # groupe des runs contigus True, réinitialisés à chaque changement de road_id si fourni
    f = flags.fillna(False).astype(bool).to_numpy()
    if road_id is not None:
        rid = road_id.fillna("__nan__").astype(str).to_numpy()
    else:
        rid = np.full(len(f), "__all__")
    groups = np.full(len(f), -1, dtype=int)
    gid = -1
    for i in range(len(f)):
        if f[i]:
            if i>0 and f[i-1] and rid[i]==rid[i-1]:
                groups[i]=gid
            else:
                gid+=1; groups[i]=gid
    return pd.Series(groups, index=flags.index)


def _summarize(df: pd.DataFrame, grp: pd.Series, cols: dict, source: str) -> pd.DataFrame:
    good = grp>=0
    if good.sum()==0:
        return pd.DataFrame(columns=[
            "curve_id","source","class","n_segments","arc_len","kappa_max","r_min","r_p85","apex_x","apex_y"
        ])
    df2 = df.loc[good].copy()
    df2["curve_gid"] = grp[good].values
    L = pd.to_numeric(df2[cols["length"]], errors="coerce") if cols["length"] else pd.Series(1.0, index=df2.index)
    K = pd.to_numeric(df2[cols["kappa"]],  errors="coerce") if cols["kappa"]  else pd.Series(np.nan, index=df2.index)
    R = pd.to_numeric(df2[cols["radius"]], errors="coerce") if cols["radius"] else pd.Series(np.nan, index=df2.index)

    rows=[]
    for gid, dfc in df2.groupby("curve_gid"):
        cl = dfc[cols["class"]].mode(dropna=False)
        cl = cl.iloc[0] if len(cl)>0 else np.nan
        arc_len = L.loc[dfc.index].sum(min_count=1)
        kmax = K.loc[dfc.index].abs().max(skipna=True)
        rmin = R.loc[dfc.index].min(skipna=True)
        rp85 = np.nanpercentile(R.loc[dfc.index].dropna().values, 15) if R.loc[dfc.index].notna().any() else np.nan
        # apex: segment de |kappa| max, sinon rayon min, sinon premier
        cand = dfc.index
        if np.isfinite(kmax) and not np.isnan(kmax):
            cand = dfc.loc[(K.loc[dfc.index].abs()==kmax)].index
        elif np.isfinite(rmin) and not np.isnan(rmin):
            cand = dfc.loc[(R.loc[dfc.index]==rmin)].index
        idx0 = cand[0]
        apex_x = pd.to_numeric(dfc.loc[idx0, "x_centroid"], errors="coerce")
        apex_y = pd.to_numeric(dfc.loc[idx0, "y_centroid"], errors="coerce")
        rows.append(dict(
            curve_id=f"{source}_{int(gid)}",
            source=source, class_=cl, n_segments=len(dfc),
            arc_len=arc_len, kappa_max=kmax, r_min=rmin, r_p85=rp85,
            apex_x=apex_x, apex_y=apex_y
        ))
    out = pd.DataFrame(rows)
    out.rename(columns={"class_":"class"}, inplace=True)
    return out


def main():
    ap = argparse.ArgumentParser(description="Extraction de virages à partir des segments (OSM/BD)")
    ap.add_argument("--config", required=True)
    ap.add_argument("--kappa-min", type=float, default=1e-4, help="seuil |kappa| minimal (1/m)")
    ap.add_argument("--r-max", type=float, default=150.0, help="seuil rayon maximal (m)")
    ap.add_argument("--out-dir", default="out/curves")
    args = ap.parse_args()

    cfg, osm, bd = _load(args.config)
    _ensure_dir(args.out_dir)

    for src_name, df in [("osm", osm), ("bd", bd)]:
        cols, df = _resolve_cols(df)
        # logs diagnostics utiles
        if cols["kappa"]:
            k = pd.to_numeric(df[cols["kappa"]], errors="coerce")
            print(f"[{src_name}] kappa nnz={k.notna().sum()}/{len(k)} min={k.min(skipna=True)} max={k.max(skipna=True)}")
        if cols["radius"]:
            r = pd.to_numeric(df[cols["radius"]], errors="coerce")
            print(f"[{src_name}] radius nnz={r.notna().sum()}/{len(r)} min={r.min(skipna=True)} max={r.max(skipna=True)}")

        rid = df["road_id"] if "road_id" in df.columns else None
        flags = _flag_turns(df, cols, args.kappa_min, args.r_max)
        grp = _group_consecutive(flags, rid)
        curves = _summarize(df, grp, cols, source=src_name.upper())
        out_parquet = os.path.join(args.out_dir, f"{src_name}.parquet")
        curves.to_parquet(out_parquet, index=False)
        print(f"✅ Virages {src_name} → {out_parquet} (n={len(curves)})")


if __name__ == "__main__":
    main()