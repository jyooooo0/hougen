from data_processor import normalize_dialect_term, load_data, get_question_distribution

# Test specific normalization cases
print("--- Normalization Function Tests ---")
cases = [
    ("Q1", "のー"), ("Q1", "の"), ("Q1", "の〜"),
    ("Q1", "ずー"), ("Q1", "ず"), ("Q1", "ずぅー"),
    ("Q2", "ありがと"), ("Q2", "ありがど"), ("Q2", "ありがとう"),
    ("Q2", "もっけだの"), ("Q2", "もっけ"),
    ("Q3", "つったい"), ("Q3", "つっだい"), ("Q3", "はっこい"), ("Q3", "ひゃっこい")
]

for q, text in cases:
    normalized = normalize_dialect_term(text, q)
    print(f"[{q}] {text} -> {normalized}")

print("\n--- Distribution Test (Top 10) ---")
df = load_data()
for q in ["Q1", "Q2", "Q3"]:
    dist = get_question_distribution(df, q)
    print(f"\n[{q}]")
    print(dist.head(10))
