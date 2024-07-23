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

# Assuming the neighborhood field is named differently, replace 'name' with the correct field name from the print output
# Example: if the neighborhood name field is 'name', update accordingly
neighborhood_field = 'name'  # Replace 'name' with the correct column name from the print output

# Group by neighborhood and year of construction, and count bike lanes
count_by_neighborhood_year = bikelanes_with_neigh.groupby([neighborhood_field, 'Year of Construction']).size().reset_index(name='bike_lane_count')

# Pivot the table to have years as columns
pivot_table = count_by_neighborhood_year.pivot_table(
    index=neighborhood_field, 
    columns='Year of Construction', 
    values='bike_lane_count', 
    fill_value=0
).reset_index()

# Convert all year columns to integers
for col in pivot_table.columns:
    if col != neighborhood_field:
        pivot_table[col] = pivot_table[col].astype(int)

# Add a total column
pivot_table['total'] = pivot_table.drop(columns=neighborhood_field).sum(axis=1)

# Group by neighborhood and count AAA bike lanes
aaa_count = bikelanes_with_neigh[bikelanes_with_neigh['AAA Segment'] == 'YES'].groupby(neighborhood_field).size().reset_index(name='aaa_total')

# Merge the AAA count with the pivot table
result = pd.merge(pivot_table, aaa_count, on=neighborhood_field, how='left')

# Fill NaN values in aaa_total with 0
result['aaa_total'] = result['aaa_total'].fillna(0).astype(int)

# Save the result to a new CSV file
result.to_csv('bike_lanes_count_by_neighborhood_year.csv', index=False)
