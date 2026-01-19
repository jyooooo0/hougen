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
        # Print repr to avoid encoding errors in console
        print([n for n in sorted_names]) 
        # Actually printing the list directly might still try to encode elements if not using repr?
        # Python's list __repr__ calls repr() on items, so it should be safe? 
        # No, str items in a list are printed as is in some shells?
        # Let's explicitly ascii-safe it for the console log
        print("Names (safe view):")
        for n in sorted_names:
            print(n.encode('utf-8', 'replace').decode('utf-8', 'replace') if os.name != 'nt' else n.encode('cp932', 'replace').decode('cp932', 'replace'))
        
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
