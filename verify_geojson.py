import json
import os

def verify_geojson():
    filename = "yamagata_municipalities.geojson"
    print(f"Verifying {filename}...")
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        features = data.get("features", [])
        print(f"Total features: {len(features)}")
        
        names = set()
        for feature in features:
            props = feature.get("properties", {})
            name = props.get("N03_004")
            if name:
                names.add(name)
        
        print(f"Unique Municipality Names: {len(names)}")
        sorted_names = sorted(list(names))
        # Print names safely
        print("Names (safe view):")
        for n in sorted_names:
            print(ascii(n))
            # Also try to print normally but handle error
            try:
                print(n)
            except UnicodeEncodeError:
                print(f"  (Cannot print {ascii(n)} in current console encoding)")
        
        # Check for mojibake or replacement chars
        mojibake_count = 0
        for name in sorted_names:
            if '\ufffd' in name or '' in name:
                print(f"WARNING: Mojibake detected in: {name}")
                mojibake_count += 1
                
        if mojibake_count == 0:
            print("SUCCESS: No mojibake detected in municipality names.")
        else:
            print(f"FAILURE: {mojibake_count} names contain garbled characters.")

    except Exception as e:
        print(f"Error reading file: {e}")

if __name__ == "__main__":
    verify_geojson()
