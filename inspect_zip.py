
import zipfile

def inspect_zip():
    filename = "N03.zip"
    print(f"Inspecting {filename}...")
    try:
        with zipfile.ZipFile(filename, 'r') as z:
            print("Contents:")
            for info in z.infolist():
                print(f"{info.filename} ({info.file_size} bytes)")
    except Exception as e:
        print(f"Error reading zip: {e}")

if __name__ == "__main__":
    inspect_zip()
