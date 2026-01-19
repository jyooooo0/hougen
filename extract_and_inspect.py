
import zipfile
import json
import os

def extract_and_inspect():
    zip_filename = "N03.zip"
    target_file = "N03-20240101_06.geojson"
    extracted_path = "extracted_" + target_file
    
    print(f"Extracting {target_file} from {zip_filename} to {extracted_path}...")
    try:
        with zipfile.ZipFile(zip_filename, 'r') as z:
            with z.open(target_file) as source, open(extracted_path, "wb") as target:
                target.write(source.read())
        
        print("Extraction complete.")
        
        # Inspect encoding
        print("Inspecting encoding...")
        try:
             # Try UTF-8 first
            with open(extracted_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            print("Successfully read as UTF-8.")
            features = data.get("features", [])
            print(f"Feature match: {json.dumps(features[0]['properties'], ensure_ascii=False)}")
            
            # Check for Mojibake characters
            props = features[0]['properties']
            name = props.get('N03_004', '')
            if '' in name:
                 print("WARNING: UTF-8 read contains replacement characters (Mojibake).")
            else:
                 print("UTF-8 seems clean.")

        except UnicodeDecodeError:
            print("UTF-8 decode failed. Trying Shift-JIS (cp932)...")
            # Try CP932
            with open(extracted_path, "r", encoding="cp932") as f:
                data = json.load(f)
            print("Successfully read as CP932.")
            print(f"Feature match: {json.dumps(data['features'][0]['properties'], ensure_ascii=False)}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    extract_and_inspect()
