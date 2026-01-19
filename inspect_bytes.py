
def inspect_bytes():
    filename = "N03-20240101_06.geojson"
    print(f"Inspecting bytes of {filename}...")
    try:
        with open(filename, "rb") as f:
            data = f.read(200)
        
        print(data)
        print("\nHex dump:")
        print(data.hex())

    except Exception as e:
        print(f"Error reading file: {e}")

if __name__ == "__main__":
    inspect_bytes()
