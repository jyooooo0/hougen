import json
import pandas as pd
from data_processor import load_data, get_municipality_distribution

# 1. Load GeoJSON properties
with open("yamagata_06.json", "r", encoding="utf-8") as f:
    geojson = json.load(f)

print(f"Total Features: {len(geojson['features'])}")

print("GeoJSON Properties Structure:")
for i, feature in enumerate(geojson["features"][:10]):
    props = feature["properties"]
    print(f"Feature {i}: {props}")

# 2. Load Dataframe Municipality Names
df = load_data()
df_yamagata = df[df["市町村名"] != "県外/不明"]
print("\nDataframe Municipalities Sample:")
print(df_yamagata["市町村名"].unique()[:5])

# 3. Check Intersection
geojson_names = set([f["properties"]["N03_004"] for f in geojson["features"]])
df_names = set(df_yamagata["市町村名"].unique())

common = geojson_names.intersection(df_names)
missing_in_geojson = df_names - geojson_names
missing_in_df = geojson_names - df_names

with open("debug_output.txt", "w", encoding="utf-8") as out:
    out.write(f"Common: {len(common)}\n")
    out.write(f"Missing in GeoJSON: {missing_in_geojson}\n")
    out.write(f"Missing in DF: {missing_in_df}\n")
    out.write("\nGeoJSON Sample:\n")
    out.write(str(list(geojson_names)[:5]))
    out.write("\nDF Sample:\n")
    out.write(str(list(df_names)[:5]))
