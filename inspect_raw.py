import shapefile

def inspect():
    # Read as latin-1 to preserve bytes as code points 0-255
    sf = shapefile.Reader("N03-20240101_06.shp", encoding="iso-8859-1")
    
    # Header
    fields = [f[0] for f in sf.fields[1:]]
    try:
        idx = fields.index('N03_004')
    except ValueError:
        print("N03_004 not found")
        return

    print("Raw bytes inspection (first 10 records):")
    for i, record in enumerate(sf.records()[:10]):
        raw_name = record[idx]
        # Convert back to bytes
        byte_seq = raw_name.encode('iso-8859-1')
        print(f"{i}: {byte_seq.hex()} | {byte_seq}")

if __name__ == '__main__':
    inspect()
