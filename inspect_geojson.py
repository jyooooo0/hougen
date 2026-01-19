import json

def inspect_geojson():
    filename = "yamagata_municipalities.geojson"
    print(f"Inspecting {filename}...")
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        features = data.get("features", [])
        print(f"Total features: {len(features)}")
        
        if not features:
            print("No features found.")
            return

        # Check properties of the first feature
        print("\nProperties of the first feature:")
        print(json.dumps(features[0].get("properties", {}), indent=2, ensure_ascii=False))

        # Collect all municipality names
        names = set()
        for feature in features:
            props = feature.get("properties", {})
            name = props.get("N03_004")
            if name:
                names.add(name)
        
        print(f"\nUnique Municipality Names (N03_004): {len(names)}")
        print(sorted(list(names)))

    except Exception as e:
        print(f"Error reading file: {e}")

if __name__ == "__main__":
    inspect_geojson()
