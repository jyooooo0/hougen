
import json

def check_encoding():
    filename = "yamagata_municipalities.geojson"
    print(f"Checking encoding for {filename}...")
    
    encodings = ["cp932", "shift_jis", "utf-8"]
    
    for enc in encodings:
        print(f"\nTrying encoding: {enc}")
        try:
            with open(filename, "r", encoding=enc) as f:
                data = json.load(f)
            
            features = data.get("features", [])
            if features:
                 # Check first feature
                print("First feature properties:")
                print(json.dumps(features[0].get("properties", {}), indent=2, ensure_ascii=False))
                print(f"Success with {enc}!")
                return
        except Exception as e:
            print(f"Failed with {enc}: {e}")

if __name__ == "__main__":
    check_encoding()
