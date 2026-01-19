
import pandas as pd
from data_processor import load_data, get_municipality_distribution
from municipalities import get_coordinates

def debug_map_data():
    print("Loading data...")
    df = load_data()
    print(f"Data Loaded: {len(df)} records")
    
    # Simulate app logic
    question_key = "Q2" # Default
    map_dist = get_municipality_distribution(df, question_key)
    
    map_data = []
    for city in map_dist.index:
        row = map_dist.loc[city]
        if row.sum() == 0:
            continue
        top_answer = row.idxmax()
        count = row[top_answer]
        total = row.sum()
        ratio = count / total
        
        map_data.append({
            "市町村": city,
            "最も多い方言": top_answer,
            "回答数": count,
            "総回答数": total,
            "割合": f"{ratio:.1%}"
        })
        
    df_map_viz = pd.DataFrame(map_data)
    
    print("\nAdding Coordinates...")
    df_map_viz["緯度"] = df_map_viz["市町村"].apply(lambda x: get_coordinates(x)[0])
    df_map_viz["経度"] = df_map_viz["市町村"].apply(lambda x: get_coordinates(x)[1])
    
    print("\n--- Map Data Preview ---")
    print(df_map_viz[["市町村", "最も多い方言", "緯度", "経度"]].head(10))
    
    print("\nChecking for Null Coordinates:")
    nulls = df_map_viz[df_map_viz["緯度"].isnull()]
    print(nulls)

if __name__ == "__main__":
    debug_map_data()
