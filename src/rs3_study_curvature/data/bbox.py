from shapely.geometry import box
import geopandas as gpd

def bbox_to_gdf(minx: float, miny: float, maxx: float, maxy: float, crs="EPSG:4326") -> gpd.GeoDataFrame:
    return gpd.GeoDataFrame({"name": ["bbox"]}, geometry=[box(minx, miny, maxx, maxy)], crs=crs)
