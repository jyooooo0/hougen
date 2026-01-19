# -*- coding: utf-8 -*-
"""
山形県35市町村のデータ定義と名寄せロジック
"""

# 山形県の市町村リスト（35市町村）と代表緯度経度
MUNICIPALITIES = {
    # 村山地方（13市町村）
    "山形市": {"lat": 38.2404, "lon": 140.3633, "region": "村山"},
    "寒河江市": {"lat": 38.3786, "lon": 140.2674, "region": "村山"},
    "上山市": {"lat": 38.1497, "lon": 140.2744, "region": "村山"},
    "村山市": {"lat": 38.4842, "lon": 140.3808, "region": "村山"},
    "天童市": {"lat": 38.3622, "lon": 140.3786, "region": "村山"},
    "東根市": {"lat": 38.4311, "lon": 140.3908, "region": "村山"},
    "尾花沢市": {"lat": 38.5997, "lon": 140.4039, "region": "村山"},
    "山辺町": {"lat": 38.2869, "lon": 140.2633, "region": "村山"},
    "中山町": {"lat": 38.3258, "lon": 140.2783, "region": "村山"},
    "河北町": {"lat": 38.4264, "lon": 140.3150, "region": "村山"},
    "西川町": {"lat": 38.4383, "lon": 140.1383, "region": "村山"},
    "朝日町": {"lat": 38.3086, "lon": 140.1406, "region": "村山"},
    "大江町": {"lat": 38.3844, "lon": 140.2011, "region": "村山"},

    # 最上地方（8市町村）
    "新庄市": {"lat": 38.7622, "lon": 140.3050, "region": "最上"},
    "金山町": {"lat": 38.8831, "lon": 140.3408, "region": "最上"},
    "最上町": {"lat": 38.7533, "lon": 140.5117, "region": "最上"},
    "舟形町": {"lat": 38.6922, "lon": 140.3083, "region": "最上"},
    "真室川町": {"lat": 38.8567, "lon": 140.2508, "region": "最上"},
    "大蔵村": {"lat": 38.6853, "lon": 140.1917, "region": "最上"},
    "鮭川村": {"lat": 38.8183, "lon": 140.2350, "region": "最上"},
    "戸沢村": {"lat": 38.7331, "lon": 140.1483, "region": "最上"},

    # 置賜地方（9市町村）
    "米沢市": {"lat": 37.9119, "lon": 140.1167, "region": "置賜"},
    "長井市": {"lat": 38.1064, "lon": 140.0439, "region": "置賜"},
    "南陽市": {"lat": 38.0519, "lon": 140.1478, "region": "置賜"},
    "高畠町": {"lat": 38.0022, "lon": 140.1908, "region": "置賜"},
    "川西町": {"lat": 38.0019, "lon": 140.0453, "region": "置賜"},
    "小国町": {"lat": 38.0583, "lon": 139.7386, "region": "置賜"},
    "白鷹町": {"lat": 38.1811, "lon": 140.0994, "region": "置賜"},
    "飯豊町": {"lat": 37.9483, "lon": 139.9833, "region": "置賜"},

    # 庄内地方（5市町村）
    "鶴岡市": {"lat": 38.7272, "lon": 139.8267, "region": "庄内"},
    "酒田市": {"lat": 38.9144, "lon": 139.8361, "region": "庄内"},
    "三川町": {"lat": 38.8019, "lon": 139.8475, "region": "庄内"},
    "庄内町": {"lat": 38.8467, "lon": 139.9058, "region": "庄内"},
    "遊佐町": {"lat": 39.0156, "lon": 139.9094, "region": "庄内"},
}

# 市町村名のリスト（優先度順：長い名前を先にマッチ）
MUNICIPALITY_NAMES = sorted(MUNICIPALITIES.keys(), key=lambda x: -len(x))

# 地域別にもグループ化
REGIONS = {
    "村山": ["山形市", "寒河江市", "上山市", "村山市", "天童市", "東根市", "尾花沢市",
             "山辺町", "中山町", "河北町", "西川町", "朝日町", "大江町"],
    "最上": ["新庄市", "金山町", "最上町", "舟形町", "真室川町", "大蔵村", "鮭川村", "戸沢村"],
    "置賜": ["米沢市", "長井市", "南陽市", "高畠町", "川西町", "小国町", "白鷹町", "飯豊町"],
    "庄内": ["鶴岡市", "酒田市", "三川町", "庄内町", "遊佐町"],
}


def extract_municipality(location_text: str) -> str:
    """
    住所テキストから市町村名を抽出する名寄せ関数
    
    Args:
        location_text: 「現在お住まいの場所」カラムの値
        
    Returns:
        市町村名、または「県外/不明」
    """
    if not location_text or not isinstance(location_text, str):
        return "県外/不明"
    
    # まず長い市町村名からマッチを試みる（例：「庄内町」は「庄内」より先にマッチ）
    for municipality in MUNICIPALITY_NAMES:
        if municipality in location_text:
            return municipality
    
    # 旧地域名から現在の市町村への変換
    old_name_mapping = {
        # 鶴岡市の旧町村
        "温海": "鶴岡市",
        "あつみ": "鶴岡市",
        "藤島": "鶴岡市",
        "羽黒": "鶴岡市",
        "櫛引": "鶴岡市",
        "朝日": "鶴岡市",  # 鶴岡市朝日地域
        "湯野浜": "鶴岡市",
        "大山": "鶴岡市",
        "由良": "鶴岡市",
        "越沢": "鶴岡市",
        
        # 酒田市の旧町村
        "平田": "酒田市",
        "松山": "酒田市",
        "八幡": "酒田市",
        "本楯": "酒田市",
        
        # 庄内町の旧町
        "余目": "庄内町",
        "立川": "庄内町",
    }
    
    for old_name, new_municipality in old_name_mapping.items():
        if old_name in location_text:
            return new_municipality
    
    # 山形県内の地域名のみのマッチ
    region_keywords = ["村山", "最上", "置賜", "庄内"]
    for region in region_keywords:
        if region in location_text:
            # 地域名だけでは市町村を特定できないので、不明扱い
            return "県外/不明"
    
    # 他県名や県外キーワードの検出
    outside_keywords = ["東京", "神奈川", "宮城", "秋田", "岩手", "福島", "新潟", 
                        "北海道", "埼玉", "千葉", "大阪", "愛知", "県外"]
    for keyword in outside_keywords:
        if keyword in location_text:
            return "県外/不明"
    
    return "県外/不明"


def get_coordinates(municipality: str) -> tuple:
    """
    市町村名から緯度経度を取得
    
    Returns:
        (lat, lon) のタプル。存在しない場合は (None, None)
    """
    if municipality in MUNICIPALITIES:
        data = MUNICIPALITIES[municipality]
        return (data["lat"], data["lon"])
    return (None, None)


def get_region(municipality: str) -> str:
    """
    市町村名から地域名を取得
    
    Returns:
        地域名（村山/最上/置賜/庄内）、または「不明」
    """
    if municipality in MUNICIPALITIES:
        return MUNICIPALITIES[municipality]["region"]
    return "不明"


if __name__ == "__main__":
    # テスト
    test_cases = [
        "鶴岡市温海の木野俣",
        "酒田市",
        "庄内町(旧余目町)",
        "東京都",
        "神奈川県横浜市",
        "山形市南原町",
        "越沢",
        "藤島",
        "",
        None,
    ]
    
    print("名寄せテスト結果:")
    for test in test_cases:
        result = extract_municipality(test)
        print(f"  {test!r} → {result}")
