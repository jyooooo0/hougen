# -*- coding: utf-8 -*-
"""
市町村ごとにGeoJSONのポリゴンをマージするスクリプト
"""

import json
from collections import defaultdict

# 入力ファイルと出力ファイル
INPUT_FILE = "N03-20240101_06.geojson"
OUTPUT_FILE = "yamagata_municipalities.geojson"

def merge_geojson():
    # GeoJSONを読み込み
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"入力フィーチャ数: {len(data['features'])}")
    
    # 市町村ごとにフィーチャをグループ化
    municipality_features = defaultdict(list)
    
    for feature in data['features']:
        props = feature.get('properties', {})
        city_name = props.get('N03_004', '')
        if city_name:
            municipality_features[city_name].append(feature)
    
    print(f"市町村数: {len(municipality_features)}")
    
    # 各市町村の座標を結合（MultiPolygonに変換）
    merged_features = []
    
    for city_name, features in municipality_features.items():
        # すべてのポリゴン座標を収集
        all_polygons = []
        
        for feat in features:
            geom = feat.get('geometry', {})
            geom_type = geom.get('type', '')
            coords = geom.get('coordinates', [])
            
            if geom_type == 'Polygon':
                all_polygons.append(coords)
            elif geom_type == 'MultiPolygon':
                all_polygons.extend(coords)
        
        if not all_polygons:
            continue
        
        # 最初のフィーチャからプロパティを取得
        props = features[0].get('properties', {}).copy()
        
        # マージしたフィーチャを作成
        merged_feature = {
            "type": "Feature",
            "properties": props,
            "geometry": {
                "type": "MultiPolygon",
                "coordinates": all_polygons
            }
        }
        
        merged_features.append(merged_feature)
        print(f"  {city_name}: {len(features)} -> 1 (ポリゴン数: {len(all_polygons)})")
    
    # 新しいGeoJSONを作成
    output_geojson = {
        "type": "FeatureCollection",
        "features": merged_features
    }
    
    # 出力
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_geojson, f, ensure_ascii=False)
    
    print(f"\n出力ファイル: {OUTPUT_FILE}")
    print(f"出力フィーチャ数: {len(merged_features)}")

if __name__ == "__main__":
    merge_geojson()
