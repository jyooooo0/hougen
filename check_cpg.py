
def check_cpg():
    try:
        with open("N03-20240101_06.cpg", "r", encoding="ascii", errors="ignore") as f:
            print(f"CPG content: {f.read()}")
    except Exception as e:
        print(f"Error reading cpg: {e}")

if __name__ == "__main__":
    check_cpg()
