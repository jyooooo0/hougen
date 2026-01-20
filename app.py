# -*- coding: utf-8 -*-
"""
山形県方言分布可視化ダッシュボード
Streamlit + Plotly による方言アンケート結果の可視化
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import folium
from streamlit_folium import st_folium
from branca.element import MacroElement, Template, Element
from shapely.geometry import shape
import json
import math
from data_processor import (
    load_data,
    get_question_distribution,
    get_municipality_distribution,
    get_free_text_by_municipality,
    QUESTION_LABELS,
    QUESTION_COLUMNS,
)
from municipalities import MUNICIPALITIES, REGIONS, get_coordinates

# ======================================
# ページ設定
# ======================================
st.set_page_config(
    page_title="山形県方言分布ダッシュボード",
    page_icon="🍒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ======================================
# カスタムCSS（モダン・グラスモーフィズムデザイン）
# ======================================
st.markdown("""
<style>
    /* ========== インポート ========== */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@300;400;500;700&family=Zen+Maru+Gothic:wght@400;500;700&display=swap');
    
    /* ========== CSS変数（ダークモード対応） ========== */
    :root {
        --bg-primary: #0f0f1a;
        --bg-secondary: #1a1a2e;
        --bg-card: rgba(30, 30, 50, 0.8);
        --bg-glass: rgba(255, 255, 255, 0.05);
        --border-glass: rgba(255, 255, 255, 0.1);
        --text-primary: #f0f0f5;
        --text-secondary: #a0a0b0;
        --text-muted: #6a6a7a;
        --accent-primary: #e85a6b;
        --accent-secondary: #ff8fa3;
        --accent-tertiary: #4ecdc4;
        --accent-gold: #ffd700;
        --gradient-cherry: linear-gradient(135deg, #e85a6b 0%, #ff8fa3 50%, #ffb3c1 100%);
        --gradient-ocean: linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%);
        --gradient-sunset: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        --shadow-soft: 0 8px 32px rgba(0, 0, 0, 0.3);
        --shadow-glow: 0 0 30px rgba(232, 90, 107, 0.2);
        --radius-sm: 8px;
        --radius-md: 16px;
        --radius-lg: 24px;
        --font-sans: 'Noto Sans JP', sans-serif;
        --font-display: 'Zen Maru Gothic', sans-serif;
    }
    
    /* ========== ベーススタイル ========== */
    .stApp {
        background: var(--bg-primary) !important;
        font-family: var(--font-sans) !important;
    }
    
    .main .block-container {
        padding-top: 2rem !important;
        max-width: 1400px !important;
    }
    
    /* ========== サイドバー ========== */
    [data-testid="stSidebar"] {
        background: var(--bg-secondary) !important;
        border-right: 1px solid var(--border-glass) !important;
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: var(--text-primary) !important;
    }
    
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stMetric label {
        color: var(--text-secondary) !important;
    }
    
    /* ========== ヘッダーカード ========== */
    .hero-header {
        background: var(--gradient-cherry);
        border-radius: var(--radius-lg);
        padding: 2.5rem 3rem;
        margin-bottom: 2rem;
        text-align: center;
        position: relative;
        overflow: hidden;
        box-shadow: var(--shadow-glow);
    }
    
    .hero-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: shimmer 15s infinite linear;
    }
    
    @keyframes shimmer {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .hero-header h1 {
        font-family: var(--font-display) !important;
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        color: white !important;
        margin: 0 !important;
        text-shadow: 0 2px 10px rgba(0,0,0,0.2);
        position: relative;
        z-index: 1;
    }
    
    .hero-header p {
        color: rgba(255, 255, 255, 0.9) !important;
        font-size: 1.1rem !important;
        margin: 0.75rem 0 0 0 !important;
        font-weight: 300;
        position: relative;
        z-index: 1;
    }
    
    /* ========== グラスモーフィズムカード ========== */
    .glass-card {
        background: var(--bg-glass);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid var(--border-glass);
        border-radius: var(--radius-md);
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: var(--shadow-soft);
        transition: all 0.3s ease;
    }
    
    .glass-card:hover {
        border-color: rgba(255, 255, 255, 0.2);
        box-shadow: var(--shadow-soft), var(--shadow-glow);
        transform: translateY(-2px);
    }
    
    /* ========== セクションタイトル ========== */
    .section-title {
        font-family: var(--font-display) !important;
        font-size: 1.6rem !important;
        font-weight: 700 !important;
        color: var(--text-primary) !important;
        margin-bottom: 1.5rem !important;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid var(--accent-primary);
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .section-title .icon {
        font-size: 1.4rem;
    }
    
    /* ========== フリーテキストカード ========== */
    .free-text-card {
        background: var(--bg-glass);
        backdrop-filter: blur(8px);
        border-left: 4px solid var(--accent-tertiary);
        border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
        padding: 1rem 1.25rem;
        margin: 0.75rem 0;
        color: var(--text-primary);
        font-size: 0.95rem;
        line-height: 1.6;
        transition: all 0.2s ease;
    }
    
    .free-text-card:hover {
        background: rgba(255, 255, 255, 0.08);
        transform: translateX(4px);
    }
    
    .free-text-card strong {
        color: var(--accent-tertiary);
    }
    
    /* ========== 凡例スタイル ========== */
    .legend-container {
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
        padding: 1rem;
        background: var(--bg-glass);
        border-radius: var(--radius-md);
        margin-top: 1rem;
    }
    
    .legend-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        background: rgba(255, 255, 255, 0.05);
        border-radius: var(--radius-sm);
        font-size: 0.9rem;
        color: var(--text-primary);
        transition: all 0.2s ease;
    }
    
    .legend-item:hover {
        background: rgba(255, 255, 255, 0.1);
    }
    
    .legend-color {
        width: 24px;
        height: 24px;
        border-radius: 6px;
        border: 2px solid rgba(255, 255, 255, 0.2);
    }
    
    /* ========== Plotlyチャート背景 ========== */
    .js-plotly-plot .plotly .main-svg {
        background: transparent !important;
    }
    
    /* ========== Foliumマップ修正 ========== */
    iframe {
        border-radius: var(--radius-md) !important;
        border: 1px solid var(--border-glass) !important;
    }
    
    /* マップコンテナのオーバーレイ問題を修正 */
    [data-testid="stDecoration"] {
        display: none !important;
    }
    
    div[data-testid="stElementToolbar"] {
        display: none !important;
    }
    
    /* Foliumマップのグレーオーバーレイを無効化 */
    .stFoliumComponent > div > div {
        background: transparent !important;
    }
    
    /* ========== Streamlit グレーオーバーレイ完全修正 ========== */
    /* Stale要素のグレーアウトを無効化 */
    .stale-element {
        opacity: 1 !important;
    }
    
    [data-stale="true"] {
        opacity: 1 !important;
    }
    
    /* ローディングオーバーレイを無効化 */
    .stApp > div:first-child > div:first-child > div[data-testid="stAppViewBlockContainer"] > div::before {
        display: none !important;
    }
    
    /* スケルトンローディングを透明に */
    .stSkeleton {
        background: transparent !important;
    }
    
    /* 全体のオーバーレイ要素を無効化 */
    div[class*="overlay"],
    div[class*="Overlay"] {
        display: none !important;
    }
    
    /* Streamlit の再実行時のフェードアウトを無効化 */
    .element-container {
        opacity: 1 !important;
        transition: none !important;
    }
    
    /* 古い要素マーカーを非表示 */
    .stMarkdown[data-stale],
    .stPlotlyChart[data-stale],
    [data-testid="stFolium"][data-stale] {
        opacity: 1 !important;
    }
    
    /* ========== メトリクスカード ========== */
    [data-testid="stMetric"] {
        background: var(--bg-glass);
        border: 1px solid var(--border-glass);
        border-radius: var(--radius-md);
        padding: 1rem;
    }
    
    [data-testid="stMetricLabel"] {
        color: var(--text-secondary) !important;
    }
    
    [data-testid="stMetricValue"] {
        color: var(--accent-primary) !important;
        font-family: var(--font-display) !important;
    }
    
    /* ========== セレクトボックス ========== */
    .stSelectbox > div > div {
        background: var(--bg-glass) !important;
        border-color: var(--border-glass) !important;
        color: var(--text-primary) !important;
    }
    
    /* ========== マークダウンテキスト ========== */
    .stMarkdown {
        color: var(--text-primary) !important;
    }
    
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: var(--text-primary) !important;
        font-family: var(--font-display) !important;
    }
    
    /* ========== 水平線 ========== */
    hr {
        border-color: var(--border-glass) !important;
        margin: 2rem 0 !important;
    }
    
    /* ========== フッター ========== */
    .footer {
        text-align: center;
        padding: 2rem;
        color: var(--text-muted);
        font-size: 0.85rem;
        border-top: 1px solid var(--border-glass);
        margin-top: 3rem;
    }
    
    .footer a {
        color: var(--accent-primary);
        text-decoration: none;
    }
    
    /* ========== アニメーション ========== */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .animate-fade-in {
        animation: fadeIn 0.5s ease-out;
    }
    
    /* ========== スピナー ========== */
    .stSpinner > div {
        border-color: var(--accent-primary) transparent transparent transparent !important;
    }
    /* ========== モバイル対応 ========== */
    @media (max-width: 768px) {
        .hero-header {
            padding: 2rem 1rem !important;
        }
        
        .hero-header h1 {
            font-size: 1.8rem !important;
        }
        
        .section-title {
            font-size: 1.5rem !important;
            padding-left: 0.5rem !important;
        }
        
        .glass-card {
            padding: 1rem !important;
            margin-bottom: 1rem !important;
        }
        
        /* 凡例を折り返し表示に */
        .legend-container {
            flex-wrap: wrap;
            justify-content: center;
        }
        
        /* マップの高さ調整 */
        iframe {
            height: 400px !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# ======================================
# カラーパレット（プロット用）
# ======================================
YAMAGATA_COLORS = [
    "#E95464",  # 韓紅 (Karakurenai) - 鮮やかな赤
    "#F4A460",  # 洒落柿 (Sharegaki) - 洗練されたオレンジ
    "#8B4F35",  # 煉瓦色 (Rengairo) - 落ち着いた赤茶
    "#2F5D50",  # 老竹色 (Oitakeiro) - 深い緑
    "#91B493",  # 白緑 (Byakuroku) - 淡い緑
    "#4B6584",  # 鉄御納戸 (Tetsuonando) - グレイッシュな青
    "#A5B2C6",  # 藤鼠 (Fujinezu) - 紫がかったグレー
    "#D7C4BB",  # 亜麻色 (Amairo) - ベージュ
    "#E6C35C",  # 黄金 (Kogane) - 上品なゴールド
    "#7B5544",  # 栗色 (Kuriiro) - ダークブラウン
    "#6FA0B6",  # 錆浅葱 (Sabiasagi) - くすんだ青緑
    "#C08EAF",  # 長春色 (Choshuniro) - 落ち着いたピンク
    "#766C5B",  # 利休茶 (Rikyucha) - 緑がかった茶色
    "#3A4F52",  # 鉄色 (Tetsuiro) - 非常に濃い青緑
    "#BDBDB8",  # 潤色 (Urumiiro) - ウォームグレー
]

# ======================================
# データ読み込み（キャッシュ）
# ======================================
# @st.cache_data(ttl=3600)  <-- キャッシュ無効化（スマホ同期問題調査のため）
def get_data():
    """データの読み込み（キャッシュ無効化中）"""
    return load_data()

# ======================================
# メインアプリ
# ======================================
def main():
    # ヘッダー
    st.markdown("""
    <div class="hero-header animate-fade-in">
        <h1>🍒 山形県方言分布ダッシュボード</h1>
        <p>県内35市町村の方言アンケート結果</p>
    </div>
    """, unsafe_allow_html=True)
    
    # データ読み込み
    try:
        with st.spinner("データを読み込んでいます..."):
            df = get_data()
            # 【デバッグ用】全データ件数の表示
            st.caption(f"DEBUG info: Total Records Loaded = {len(df)}")
    except Exception as e:
        st.error(f"""
        ⚠️ **データの読み込みに失敗しました**
        
        Googleスプレッドシートにアクセスできません。以下を確認してください：
        
        1. スプレッドシートが「リンクを知っている全員」に公開されているか
        2. インターネット接続が正常か
        
        **エラー詳細**: {str(e)}
        """)
        st.stop()
    
    # ======================================
    # サイドバー
    # ======================================
    with st.sidebar:
        st.markdown("## 🔍 分析設定")
        
        # 設問選択（Q1/Q2プレフィックスなし）
        question_options = {v: k for k, v in QUESTION_LABELS.items()}
        selected_question_label = st.selectbox(
            "分析する設問を選択",
            options=list(question_options.keys()),
            index=1,  # デフォルト: ありがとう
        )
        selected_question = question_options[selected_question_label]
        
        st.markdown("---")
        
        # 市町村フィルター
        st.markdown("### 🗺️ 市町村フィルター")
        
        # 地域選択
        region_options = ["すべて"] + list(REGIONS.keys())
        selected_region = st.selectbox("地域を選択", region_options)
        
        # 市町村選択（自由記入欄表示用）
        if selected_region == "すべて":
            municipality_options = ["選択してください"] + list(MUNICIPALITIES.keys())
        else:
            municipality_options = ["選択してください"] + REGIONS[selected_region]
        
        selected_municipality = st.selectbox(
            "自由記入欄を見る市町村",
            municipality_options,
        )
        
        st.markdown("---")
        
        # データ概要
        st.markdown("### 📊 データ概要")
        total_responses = len(df)
        yamagata_responses = len(df[df["市町村名"] != "県外/不明"])
        st.metric("総回答数", f"{total_responses}件")
        st.metric("県内回答数", f"{yamagata_responses}件")
        
        unique_municipalities = df[df["市町村名"] != "県外/不明"]["市町村名"].nunique()
        st.metric("回答のあった市町村", f"{unique_municipalities}箇所")
        
        st.markdown("---")
        
        # Googleフォームリンク
        st.markdown('''
        <div style="margin-top: 1rem;">
            <a href="https://docs.google.com/forms/d/10fb2A-ylveWaGYSppMXzI9JdmgXBjOKrsXc01CwguqQ/viewform" target="_blank" style="
                display: flex;
                align-items: center;
                gap: 0.5rem;
                padding: 0.75rem 1rem;
                background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%);
                color: white;
                text-decoration: none;
                border-radius: 12px;
                font-weight: 500;
                font-size: 0.9rem;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(78, 205, 196, 0.3);
            ">
                📝 アンケートに回答する
            </a>
        </div>
        ''', unsafe_allow_html=True)
    
    # ======================================
    # メインパネル
    # ======================================
    
    # --- 地図ビジュアライゼーション（メイン） ---
    # --- 地図ビジュアライゼーション（メイン） ---
    st.markdown(f"""
    <div class="section-title">
        <span class="icon">🗺️</span>
        方言分布マップ
        <span style="
            font-size: 0.9rem;
            background: linear-gradient(135deg, #e85a6b 0%, #c41e3a 100%);
            color: white;
            padding: 0.3rem 0.8rem;
            border-radius: 20px;
            margin-left: 1rem;
            vertical-align: middle;
            display: inline-block;
            box-shadow: 0 2px 5px rgba(232, 90, 107, 0.4);
        ">
            Q. {QUESTION_LABELS[selected_question]}
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    # マップ用データの作成（市町村ごとの最多回答を抽出）
    map_dist = get_municipality_distribution(df, selected_question)
    
    if not map_dist.empty:
        # GeoJSONの読み込み（ローカルファイル）
        @st.cache_data
        def get_geojson():
            import json
            try:
                with open("yamagata_municipalities.geojson", "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                st.error(f"地図データの読み込みエラー: {e}")
                return None

        geojson = get_geojson()
        
        # 最多回答（ドミナント）を特定
        map_data = []
        for city in map_dist.index:
            row = map_dist.loc[city]
            if row.sum() == 0:
                continue
            
            # 最も多い回答を取得
            top_answer = row.idxmax()
            count = row[top_answer]
            total = row.sum()
            ratio = count / total
            
            # 上位3回答の詳細を作成
            sorted_answers = row[row > 0].sort_values(ascending=False).head(3)
            top3_details = []
            for ans, cnt in sorted_answers.items():
                pct = cnt / total * 100
                top3_details.append(f"{ans}: {pct:.0f}%")
            top3_str = " / ".join(top3_details)
            
            map_data.append({
                "市町村": city,
                "最も多い方言": top_answer,
                "回答数": count,
                "総回答数": total,
                "割合": f"{ratio:.1%}",
                "上位回答": top3_str,
            })
            

        df_map_viz = pd.DataFrame(map_data)
        
        # 座標情報を追加（ラベル表示用）
        # 明示的にfloat型に変換
        df_map_viz["緯度"] = df_map_viz["市町村"].apply(lambda x: get_coordinates(x)[0]).astype(float)
        df_map_viz["経度"] = df_map_viz["市町村"].apply(lambda x: get_coordinates(x)[1]).astype(float)
        
        if not df_map_viz.empty and geojson:
            # --- Folium マップの実装（ダークモード対応）---
            
            # 1. 基本色の定義（上位回答に色を割り当て）
            total_dist = get_question_distribution(df, selected_question)
            top_answers = total_dist["回答"].tolist()
            
            # 回答 -> 色（Hex）の辞書作成
            base_color_map = {}
            for i, ans in enumerate(top_answers):
                if i < len(YAMAGATA_COLORS):
                    base_color_map[ans] = YAMAGATA_COLORS[i]
                else:
                    base_color_map[ans] = "#808080"  # その他はグレー

            # 2. 市町村ごとの最多回答の色を準備
            municipality_colors = {}  # 市町村名 -> 色
            for city in map_dist.index:
                row = map_dist.loc[city]
                total = row.sum()
                if total == 0:
                    continue
                
                # 最も多い回答を取得
                top_answer = row.idxmax()
                color = base_color_map.get(top_answer, "#808080")
                municipality_colors[city] = color
            
            # 3. Foliumマップの作成（ダークモード対応タイル）
            # 山形県全体が見えるように調整（中心を少し西・南へ、ズームを引く）
            m = folium.Map(
                location=[38.35, 140.1], 
                zoom_start=7.5,
                tiles="CartoDB dark_matter"  # ダークモード対応タイル
            )
            
            # ツールチップ用のデータを準備
            tooltip_data = {}
            for _, row in df_map_viz.iterrows():
                city = row['市町村']
                tooltip_data[city] = {
                    'top_ans': row['最も多い方言'],
                    'top3_str': row['上位回答'],
                    'total_count': row['総回答数']
                }

            # 4. GeoJsonデータの構築（プロパティ注入）
            processed_features = []
            
            for feature in geojson['features']:
                props = feature['properties']
                city_name = props.get('N03_004')
                
                # 該当なしの場合はスキップまたはデフォルト表示
                if not city_name:
                    continue
                    
                color = municipality_colors.get(city_name, '#404050')
                tip_info = tooltip_data.get(city_name, {})
                
                # ツールチップ/ポップアップHTMLの構築
                if tip_info:
                    html_content = f"""
                    <div style="font-family: sans-serif; font-size: 14px; padding: 5px; min-width: 200px;">
                        <b style="font-size: 16px;">{city_name}</b><br>
                        <hr style="margin: 5px 0; border-color: #ccc;">
                        <b>最多回答:</b> {tip_info.get('top_ans', 'N/A')}<br>
                        <b>詳細:</b> {tip_info.get('top3_str', 'N/A')}<br>
                        <b>回答数:</b> {tip_info.get('total_count', 0)}件
                    </div>
                    """
                else:
                    html_content = f"<b>{city_name}</b>"
                
                # プロパティに情報を注入
                feature['properties']['fillColor'] = color
                feature['properties']['popup_content'] = html_content
                processed_features.append(feature)
            
            # 更新されたGeoJSONデータ
            geojson['features'] = processed_features
            
            # スタイル関数の定義（プロパティを参照）
            def style_function(feature):
                return {
                    'fillColor': feature['properties'].get('fillColor', '#404050'),
                    'color': '#ffffff',
                    'weight': 1.5,
                    'fillOpacity': 0.75,
                    'opacity': 0.8
                }
            
            def highlight_function(feature):
                return {
                    'fillColor': '#4ecdc4',  # ハイライト時はティール色
                    'color': '#ffffff',
                    'weight': 3,
                    'fillOpacity': 0.95,
                    'opacity': 1.0
                }
            
            # 単一のGeoJsonレイヤーとして追加
            folium.GeoJson(
                data=geojson,
                name="山形県方言",
                style_function=style_function,
                highlight_function=highlight_function,
                popup=folium.GeoJsonPopup(
                    fields=['popup_content'],
                    aliases=[''],
                    labels=False,
                    localize=True,
                    style="max-width: 300px;" # ポップアップのスタイル制限
                )
            ).add_to(m)

            # 5. ラベル（市町村名＋最多回答）を追加
            # DivIconを使用して文字のみを表示
            # GeoJSONから重心を計算して配置
            for feature in geojson['features']:
                props = feature['properties']
                city_name = props.get('N03_004')
                
                # 表示すべきデータがあるか確認
                if not city_name:
                    continue
                    
                # マップデータから回答を取得
                row = df_map_viz[df_map_viz['市町村'] == city_name]
                if row.empty:
                    continue
                    
                top_ans = row.iloc[0]['最も多い方言']
                if not top_ans:
                    continue

                # 重心（または代表点）の計算
                try:
                    polygon = shape(feature['geometry'])
                    # representative_point() はポリゴン内部にあることが保証される
                    # centroid は形によってはポリゴン外になることがある（三日月型など）
                    center = polygon.representative_point()
                    lat, lon = center.y, center.x
                except Exception as e:
                    # 計算失敗時はフォールバック
                    lat, lon = row.iloc[0]['緯度'], row.iloc[0]['経度']

                # 文字ラベルのマーカーを追加
                folium.map.Marker(
                    [lat, lon],
                    icon=folium.DivIcon(
                        html=f"""
                            <div style="
                                font-family: 'Noto Sans JP', sans-serif;
                                font-size: 7pt;
                                font-weight: 500;
                                color: white;
                                background-color: rgba(0, 0, 0, 0.4);
                                padding: 2px 4px;
                                border-radius: 4px;
                                white-space: nowrap;
                                width: max-content;
                                display: inline-block;
                                line-height: 1.2;
                                text-align: center;
                                transform: translate(-50%, -50%);
                                pointer-events: none;
                                box-shadow: 0 0 2px rgba(0,0,0,0.2);
                            ">
                                {top_ans}
                            </div>
                        """
                    )
                ).add_to(m)

            # Streamlitで表示
            st_folium(m, width=None, height=700)
            
            # --- 凡例をマップ下に表示（モダンなデザイン） ---
            legend_items = []
            for i, ans in enumerate(top_answers[:10]):
                color = base_color_map[ans]
                legend_items.append(f'<div class="legend-item"><div class="legend-color" style="background-color: {color};"></div><span>{ans}</span></div>')
            legend_html = '<div class="legend-container">' + ''.join(legend_items) + '</div>'
            st.markdown(legend_html, unsafe_allow_html=True)
            
        elif not df_map_viz.empty:
            # GeoJSONがない場合のフォールバック（散布図）
            st.warning("地図データの読み込みに失敗しました。簡易表示に切り替えます。")
            
            fig_scatter = px.scatter_mapbox(
                df_map_viz.dropna(subset=["緯度", "経度"]),
                lat="緯度",
                lon="経度",
                color="最も多い方言",
                size="総回答数",
                hover_name="市町村",
                hover_data=["最も多い方言", "割合"],
                zoom=7.5,
                center={"lat": 38.5, "lon": 140.1},
                mapbox_style="carto-positron",
                title=f"「{QUESTION_LABELS[selected_question]}」の地域別分布（ポイント表示）",
            )
            
            # テキストラベルを追加
            fig_scatter.add_trace(go.Scattermapbox(
                lat=df_map_viz["緯度"],
                lon=df_map_viz["経度"],
                mode='markers+text',
                marker=dict(size=4, color='black', opacity=0.6),
                text=df_map_viz["最も多い方言"],
                textposition="top center",
                textfont=dict(size=11, color='black', family="Arial Black"),
                showlegend=False,
                hoverinfo='skip'
            ))

            fig_scatter.update_layout(height=600)
            st.plotly_chart(fig_scatter, use_container_width=True, config={'displayModeBar': False})
    else:
        st.info("表示するデータがありません")

    st.markdown("---")
    
    # --- 全体サマリー ---
    st.markdown(f'''
    <div class="section-title">
        <span class="icon">📈</span>
        {QUESTION_LABELS[selected_question]} の回答サマリー
    </div>
    ''', unsafe_allow_html=True)
    
    # 上位10回答の分布
    distribution = get_question_distribution(df, selected_question)
    
    if not distribution.empty:
        # 【重要】データ型変換とカラム名変更（Plotlyの挙動安定化のため）
        # 全体に対して適用
        distribution["件数"] = pd.to_numeric(distribution["件数"], errors='coerce')
        distribution = distribution.rename(columns={"回答": "Answer", "件数": "Count"})
        
        # 件数で降順ソート
        distribution = distribution.sort_values("Count", ascending=False)
        
        # 【デバッグ用】データ件数の確認
        if not distribution.empty:
            max_count = distribution.iloc[0]['Count']
            st.caption(f"DEBUG info: Top Answer Count (Bar Chart) = {max_count}")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # --- パイチャート (graph_objectsを使用) ---
            top_n = 8
            top_dist = distribution.head(top_n).copy()
            others_count = distribution.iloc[top_n:]["Count"].sum() if len(distribution) > top_n else 0
            
            # その他を追加
            if others_count > 0:
                top_dist = pd.concat([
                    top_dist,
                    pd.DataFrame({"Answer": ["その他"], "Count": [others_count]})
                ], ignore_index=True)
            

            # 【デバッグ用】（折りたたみ表示）
            with st.expander("詳細データを見る"):
                st.dataframe(top_dist)
            
            import plotly.graph_objects as go
            
            # Pandas Seriesをリストに変換（Plotlyの互換性向上のため）
            pie_labels = top_dist["Answer"].tolist()
            pie_values = top_dist["Count"].astype(int).tolist()
            
            fig_pie = go.Figure(data=[go.Pie(
                labels=pie_labels,
                values=pie_values,
                hole=0.3,
                marker=dict(colors=YAMAGATA_COLORS),
                textinfo='percent+label',
                textposition='inside'
            )])
            
            fig_pie.update_layout(
                title="回答の割合（上位8件 + その他）",
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.3, font=dict(color="#f0f0f5")),
                margin=dict(t=50, b=80, l=20, r=20),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#f0f0f5"),
            )
            st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})
        
        with col2:
            # --- 棒グラフ (graph_objectsを使用) ---
            bar_data = distribution.head(15).copy()
            # グラフ上は見やすいように下から積み上げる形にする（降順データの逆順）
            bar_data_rev = bar_data.iloc[::-1]
            
            # Pandas Seriesをリストに変換（Plotlyの互換性向上のため）
            bar_x_values = bar_data_rev["Count"].astype(int).tolist()
            bar_y_values = bar_data_rev["Answer"].tolist()
            
            # 最大値を計算してX軸の範囲を設定
            max_value = max(bar_x_values) if bar_x_values else 0
            
            fig_bar = go.Figure(data=[go.Bar(
                x=bar_x_values,
                y=bar_y_values,
                orientation='h',
                marker=dict(
                    color=bar_x_values,
                    colorscale=["#FFB3B3", "#C41E3A"]
                ),
                text=bar_x_values,
                texttemplate='%{x}',  # 【重要】X軸の値（件数）を直接表示
                textposition='outside',
                textfont=dict(color="#f0f0f5", size=14, family="Arial Black"),
                cliponaxis=False
            )])
            
            fig_bar.update_layout(
                title=dict(text="回答の件数（上位15件）", font=dict(size=16)),
                showlegend=False,
                margin=dict(t=50, b=20, l=10, r=80),  # 右マージンを十分に確保
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#f0f0f5"),
                xaxis=dict(
                    title="件数",
                    range=[0, max_value * 1.25],  # 最大値の1.25倍まで表示（ラベルスペース確保）
                    tickformat='d',
                    dtick=max(1, max_value // 5),
                    fixedrange=True, # ズーム禁止（誤操作防止）
                ),
                yaxis=dict(
                    title="",
                    fixedrange=True, # ズーム禁止
                ),
                uniformtext_minsize=10,
                uniformtext_mode='show' # 常に表示
            )
            # fig_bar.update_traces(textposition='outside', cliponaxis=False) # 上記で設定済みのため削除
            st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})
    
    st.markdown("---")
    
    # --- 市町村別スタックバーチャート ---
    st.markdown('''
    <div class="section-title">
        <span class="icon">🏘️</span>
        市町村別の回答分布
    </div>
    ''', unsafe_allow_html=True)
    
    cross_tab = get_municipality_distribution(df, selected_question)
    
    if not cross_tab.empty:
        # 地域でフィルタリング
        if selected_region != "すべて":
            filter_municipalities = REGIONS[selected_region]
            cross_tab = cross_tab[cross_tab.index.isin(filter_municipalities)]
        
        if not cross_tab.empty:
            # 回答数でソート
            cross_tab = cross_tab.loc[cross_tab.sum(axis=1).sort_values(ascending=True).index]
            
            # 上位回答のみを表示（色分けの複雑さを避けるため）
            top_answers = distribution.head(10)["Answer"].tolist()
            
            # データを整形
            plot_data = []
            for municipality in cross_tab.index:
                for answer in cross_tab.columns:
                    count = cross_tab.loc[municipality, answer]
                    if count > 0:
                        # 上位10以外は「その他」にまとめる
                        display_answer = answer if answer in top_answers else "その他"
                        plot_data.append({
                            "市町村": municipality,
                            "回答": display_answer,
                            "件数": count
                        })
            
            plot_df = pd.DataFrame(plot_data)
            plot_df = plot_df.groupby(["市町村", "回答"])["件数"].sum().reset_index()
            
            # スタックバーチャート
            fig_stack = px.bar(
                plot_df,
                x="件数",
                y="市町村",
                color="回答",
                orientation='h',
                title=f"市町村別「{QUESTION_LABELS[selected_question]}」の回答分布",
                color_discrete_sequence=YAMAGATA_COLORS,
                barmode='stack',
            )
            
            chart_height = max(400, len(cross_tab) * 25)
            fig_stack.update_layout(
                height=chart_height,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.15,
                    xanchor="center",
                    x=0.5,
                    font=dict(color="#f0f0f5"),
                ),
                margin=dict(t=50, b=100, l=20, r=20),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#f0f0f5"),
            )
            
            st.plotly_chart(fig_stack, use_container_width=True, config={'displayModeBar': False})
        else:
            st.warning(f"{selected_region}地方のデータがありません")
    
    st.markdown("---")
    
    # --- 自由記入欄 ---
    st.markdown('''
    <div class="section-title">
        <span class="icon">💬</span>
        面白い方言（自由記入欄）
    </div>
    ''', unsafe_allow_html=True)
    
    if selected_municipality != "選択してください":
        free_texts = get_free_text_by_municipality(df, selected_municipality)
        
        if free_texts:
            st.markdown(f"### {selected_municipality}からの声 ({len(free_texts)}件)")
            for i, text in enumerate(free_texts, 1):
                st.markdown(f"""
                <div class="free-text-card">
                    <strong>#{i}</strong> {text}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info(f"{selected_municipality}からの自由記入はありません")
    else:
        # 全体からランダムに表示
        st.markdown("左のサイドバーで市町村を選択すると、その地域の声が表示されます。")
        
        all_free_texts = df[["市町村名", "【自由記入欄】 面白い方言"]].dropna(subset=["【自由記入欄】 面白い方言"])
        all_free_texts = all_free_texts[all_free_texts["【自由記入欄】 面白い方言"].str.strip() != ""]
        
        if not all_free_texts.empty:
            st.markdown("### 🎲 ピックアップ（全県から）")
            sample_size = min(5, len(all_free_texts))
            samples = all_free_texts.sample(sample_size)
            
            for _, row in samples.iterrows():
                st.markdown(f"""
                <div class="free-text-card">
                    <strong>📍 {row['市町村名']}</strong><br>
                    {row['【自由記入欄】 面白い方言']}
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ======================================
    # 方言分析・解説セクション
    # ======================================
    st.markdown('''
    <div class="section-title">
        <span class="icon">📚</span>
        山形の方言、なぜこんなに違うの？
    </div>
    ''', unsafe_allow_html=True)
    
    # 解説コンテンツ
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.markdown('''
        <div class="glass-card">
            <h4 style="color: #e85a6b; margin-top: 0;">🏔️ 山が方言を分けた</h4>
            <p style="line-height: 1.8;">
                山形県の方言が地域によって大きく違う最大の理由は<b>「出羽山地」</b>です。
                月山や朝日連峰が壁となって、庄内地方と内陸部を分断してきました。
            </p>
            <p style="line-height: 1.8;">
                昔は山を越えるのが大変だったので、庄内は日本海側の文化、
                内陸は他の東北地方の文化とつながりながら、それぞれ独自の言葉が育ちました。
            </p>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown('''
        <div class="glass-card">
            <h4 style="color: #4ecdc4; margin-top: 0;">❄️ 雪ことばの豊かさ</h4>
            <p style="line-height: 1.8;">
                「雪かき」だけでも<b>「雪はき」「雪ほり」「雪よせ」</b>など、
                地域によって呼び方が違います。
            </p>
            <p style="line-height: 1.8;">
                <b>はき</b>＝掃く（軽い雪）、<b>ほり</b>＝掘る（どっさり積もった雪）、
                <b>よせ</b>＝寄せる（移動させる）。
                雪国ならではの細やかな表現の違いですね。
            </p>
        </div>
        ''', unsafe_allow_html=True)
    
    with col_right:
        st.markdown('''
        <div class="glass-card">
            <h4 style="color: #ff8fa3; margin-top: 0;">🌏 4つの方言圏</h4>
            <table style="width: 100%; border-collapse: collapse; margin: 1rem 0;">
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
                    <td style="padding: 0.5rem; color: #e85a6b;"><b>庄内</b></td>
                    <td style="padding: 0.5rem;">鶴岡・酒田など。西日本に近いアクセント</td>
                </tr>
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
                    <td style="padding: 0.5rem; color: #4ecdc4;"><b>最上</b></td>
                    <td style="padding: 0.5rem;">新庄周辺。庄内と内陸の中間的な特徴</td>
                </tr>
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
                    <td style="padding: 0.5rem; color: #ffd700;"><b>村山</b></td>
                    <td style="padding: 0.5rem;">山形市など。典型的な東北弁</td>
                </tr>
                <tr>
                    <td style="padding: 0.5rem; color: #91B493;"><b>置賜</b></td>
                    <td style="padding: 0.5rem;">米沢など。福島との接点あり</td>
                </tr>
            </table>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown('''
        <div class="glass-card">
            <h4 style="color: #ffd700; margin-top: 0;">🗣️ 語尾の違い</h4>
            <p style="line-height: 1.8;">
                庄内では「〜のー」、内陸では「〜ずー」が多いと言われています。
            </p>
            <p style="line-height: 1.8;">
                同じ県内でも語尾だけで出身地がわかることも。
                「どこ出身？」って話題になることもありますね。
            </p>
        </div>
        ''', unsafe_allow_html=True)
    
    # 豆知識
    st.markdown('''
    <div class="glass-card" style="margin-top: 1rem;">
        <h4 style="color: #e85a6b; margin-top: 0;">💡 方言トリビア</h4>
        <div style="display: flex; flex-wrap: wrap; gap: 1rem;">
            <div style="flex: 1; min-width: 250px; padding: 1rem; background: rgba(255,255,255,0.03); border-radius: 8px;">
                <p style="margin: 0;"><b>「はっこい」と「しゃっこい」</b></p>
                <p style="margin: 0.5rem 0 0 0; color: #a0a0b0; font-size: 0.9rem;">
                    「冷たい」の方言。実は古語「つめたし」が変化したもの。
                    t音がh音やsh音に弱くなる東北方言の特徴です。
                </p>
            </div>
            <div style="flex: 1; min-width: 250px; padding: 1rem; background: rgba(255,255,255,0.03); border-radius: 8px;">
                <p style="margin: 0;"><b>語尾の「のー」と「ずー」</b></p>
                <p style="margin: 0.5rem 0 0 0; color: #a0a0b0; font-size: 0.9rem;">
                    庄内では「〜のー」、内陸では「〜ずー」が多い傾向。
                    同じ県でも語尾で出身地がわかることも！
                </p>
            </div>
            <div style="flex: 1; min-width: 250px; padding: 1rem; background: rgba(255,255,255,0.03); border-radius: 8px;">
                <p style="margin: 0;"><b>若い世代の標準語化</b></p>
                <p style="margin: 0.5rem 0 0 0; color: #a0a0b0; font-size: 0.9rem;">
                    都市部を中心に標準語化が進んでいますが、
                    庄内地方は比較的方言が残っています。
                </p>
            </div>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    # フッター
    st.markdown("""
    <div class="footer">
        🍒 山形県方言分布ダッシュボード | データ：Googleスプレッドシートより
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
