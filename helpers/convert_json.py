import geopandas as gpd

gdf = gpd.read_file("data/gadm41_LUX_3.json")
gdf.to_file("data/luxembourg_cantons.geojson", driver="GeoJSON")
