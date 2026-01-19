# -*- coding: utf-8 -*-
import zipfile
import json
import shapefile
from collections import defaultdict
import os

def recover_geojson():
    print("1. Extracting Shapefiles from N03.zip...")
    with zipfile.ZipFile("N03.zip", 'r') as z:
        z.extractall(".")
    
    print("2. Reading Shapefile with UTF-8 encoding (according to .cpg)...")
    # Use pyshp to read the shapefile
    # Try reading with 'utf-8'
    try:
        sf = shapefile.Reader("N03-20240101_06.shp", encoding="utf-8")
    except Exception as e:
        print(f"Standard load failed: {e}")
        return
    
    print(f"   Found {len(sf.shapes())} shapes.")
    
    # Verify field names
    fields = [f[0] for f in sf.fields[1:]]
    print(f"   Fields: {fields}")
    # Expecting N03_004 to be the municipality name
    name_index = -1
    for i, f in enumerate(fields):
        if f == 'N03_004':
            name_index = i
            break
            
    if name_index == -1:
        print("Error: Could not find N03_004 field.")
        return

    print("3. Grouping features by municipality...")
    municipality_features = defaultdict(list)
    
    for shape, record in zip(sf.shapes(), sf.records()):
        city_name = record[name_index]
        if not city_name:
            continue
            
        # pyshp returns coordinates as list of [x, y]
        # GeoJSON needs list of lists of [x, y]
        
        # Determine geometry type
        # ShapeType 5 is Polygon
        if shape.shapeType != 5:
            continue
            
        municipality_features[city_name].append(shape)

    print(f"   Found {len(municipality_features)} unique municipalities.")
    
    # Safe print
    sample_names = list(municipality_features.keys())[:5]
    # print("   Sample names:", [n.encode('utf-8', 'replace').decode('utf-8') for n in sample_names])
    print("   Sample names printing skipped due to encoding issues.")

    print("4. Merging polygons and creating GeoJSON...")
    features = []
    
    for city_name, shapes in municipality_features.items():
        all_polygons = []
        
        for shape in shapes:
            # pyshp parts indicate separate rings (outer/inner) or separate polygons
            # For simplicity in this recovery script without shapely:
            # We treat each part as a separate polygon loop.
            # However, simpler approach for visualization: just take valid points.
            # Correct approach for GeoJSON Polygon: [ [outer_ring], [hole1], ... ]
            # MultiPolygon: [ [[outer], [hole]], [[outer]] ]
            
            # shape.parts is a list of starting indices for each part
            parts = shape.parts
            points = shape.points
            
            # Add the total length as the end of the last part
            parts_full = list(parts) + [len(points)]
            
            for i in range(len(parts)):
                start = parts_full[i]
                end = parts_full[i+1]
                ring = points[start:end]
                
                # Ensure closed ring
                if ring[0] != ring[-1]:
                    ring.append(ring[0])
                
                # Note: This simple extraction treats all rings as polygons (MultiPolygon).
                # Inner holes might be rendered as filled polygons, but for this viz 
                # (highlighting areas), it's usually acceptable if 'fillOpacity' is high.
                # Ideally, we distinguish holes, but pyshp alone makes it tricky without shapely.
                all_polygons.append(ring)

        feature = {
            "type": "Feature",
            "properties": {
                "N03_004": city_name
            },
            "geometry": {
                "type": "MultiPolygon",
                "coordinates": [[poly] for poly in all_polygons] # Wrap each ring as a polygon
            }
        }
        features.append(feature)

    output_geojson = {
        "type": "FeatureCollection",
        "features": features
    }

    output_file = "yamagata_municipalities.geojson"
    print(f"5. Saving to {output_file}...")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_geojson, f, ensure_ascii=False)
        
    print("Done. Successfully recovered GeoJSON.")

if __name__ == "__main__":
    recover_geojson()
