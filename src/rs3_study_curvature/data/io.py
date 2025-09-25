from pathlib import Path
import pandas as pd
import geopandas as gpd

def ensure_out_dir(out_dir: str) -> Path:
    p = Path(out_dir)
    p.mkdir(parents=True, exist_ok=True)
    return p

def write_parquet(df: pd.DataFrame, path: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)

def read_parquet(path: str) -> pd.DataFrame:
    return pd.read_parquet(path)

def write_geojson(gdf: gpd.GeoDataFrame, path: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    gdf.to_file(path, driver="GeoJSON")

def read_geojson(path: str) -> gpd.GeoDataFrame:
    return gpd.read_file(path)
