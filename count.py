import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# Load the neighborhood GeoJSON
neighborhoods_gdf = gpd.read_file('local-area-boundary.geojson')

# Load the bike lanes CSV
bikelanes_df = pd.read_csv('bikeways.csv', delimiter=';')

# Convert bike lanes DataFrame to GeoDataFrame
bikelanes_gdf = gpd.GeoDataFrame(
    bikelanes_df,
    geometry=[Point(float(xy.split(',')[1]), float(xy.split(',')[0])) for xy in bikelanes_df['geo_point_2d']],
    crs='EPSG:4326'
)

# Perform spatial join to associate bike lanes with neighborhoods
bikelanes_with_neigh = gpd.sjoin(bikelanes_gdf, neighborhoods_gdf, how='left', predicate='within')

# Print columns to find the correct name
print(bikelanes_with_neigh.columns)

# Assuming the neighborhood field is named differently, replace 'neighborhood_name' with the correct field name
# Example: if the neighborhood name field is 'name', update accordingly
neighborhood_field = 'name'  # Replace 'name' with the correct column name from the print output

# Count bike lanes per neighborhood
count_by_neighborhood = bikelanes_with_neigh.groupby(neighborhood_field).size().reset_index(name='bike_lane_count')

# Save the result to a new CSV file
count_by_neighborhood.to_csv('bike_lanes_count_by_neighborhood.csv', index=False)
