# -*- coding: utf-8 -*-
"""
Googleスプレッドシートからのデータ読み込みと前処理
"""

import pandas as pd
import requests
import streamlit as st
from io import StringIO
from municipalities import extract_municipality, get_coordinates, get_region

# Googleスプレッドシートの公開CSVエクスポートURL
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1ObFXkVmc_4AFsbAKKmzh14Uy6Zks_tF06Pspa8x0Ftk/export?format=csv"

# 設問カラムの定義
QUESTION_COLUMNS = {
    "Q1": "Q1.語尾につける言葉",
    "Q2": "Q2.「ありがとう」を方言で言うと？",
    "Q3": "Q3.「冷たい」を方言で言うと？",
    "Q4": "Q4.「たくさん」を方言で言うと？",
    "Q5": "Q5.「雪かき」を方言で言うと？",
    "Q6": "Q6.「お腹いっぱい」を方言で言うと？",
    "Q7": "Q7.「捨てる」を方言で言うと？",
    "Q8": "Q8.「食べる」を方言で言うと？",
    "Q9": "Q9.「目」を方言で言うと？",
    "Q10": "Q10.「かわいい」を方言で言うと？",
    "Q11": "Q11.「怒る」を方言で言うと？",
    "Q12": "Q12.「かき混ぜる」を方言で言うと？",
}

# 設問の簡易ラベル（UI表示用）
QUESTION_LABELS = {
    "Q1": "語尾につける言葉",
    "Q2": "ありがとう",
    "Q3": "冷たい",
    "Q4": "たくさん",
    "Q5": "雪かき",
    "Q6": "お腹いっぱい",
    "Q7": "捨てる",
    "Q8": "食べる",
    "Q9": "目",
    "Q10": "かわいい",
    "Q11": "怒る",
    "Q12": "かき混ぜる",
}


def load_data(url: str = SPREADSHEET_URL) -> pd.DataFrame:
    """
    Googleスプレッドシートからデータを読み込み、前処理を行う
    
    Returns:
        前処理済みのDataFrame
    """
    try:
        # CSVデータの取得
        response = requests.get(url, timeout=10)
        response.encoding = 'utf-8'
        
        # HTMLが返ってきた場合はエラー（認証が必要な可能性）
        if response.text.strip().startswith('<!DOCTYPE') or response.text.strip().startswith('<html'):
            raise ValueError("スプレッドシートにアクセスできません。公開設定を確認してください。")
        
        # DataFrameに変換
        df = pd.read_csv(StringIO(response.text))
        
        # カラム名の確認
        if "現在お住まいの場所" not in df.columns:
            # カラム名をデバッグ出力
            print(f"利用可能なカラム: {list(df.columns)}")
            raise KeyError("'現在お住まいの場所' カラムが見つかりません")
        
        # 市町村名の名寄せ
        df["市町村名"] = df["現在お住まいの場所"].apply(extract_municipality)
        
        # 緯度経度の追加
        df["緯度"] = df["市町村名"].apply(lambda x: get_coordinates(x)[0])
        df["経度"] = df["市町村名"].apply(lambda x: get_coordinates(x)[1])
        
        # 地域の追加
        df["地域"] = df["市町村名"].apply(get_region)
        
        return df
        
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"ネットワークエラー: {e}")
    except Exception as e:
        raise RuntimeError(f"データ読み込みエラー: {e}")


def normalize_dialect_term(text: str, question_key: str) -> str:
    """
    回答の表記ゆれを正規化する
    
    Args:
        text: 回答テキスト
        question_key: 設問キー（Q1, Q2 など）
        
    Returns:
        正規化されたテキスト
    """
    if not text or not isinstance(text, str):
        return None
        
    # 基本的なクリーニング
    text = text.strip()
    # 長音の統一
    text = text.replace("〜", "ー").replace("～", "ー")
    
    if not text:
        return None

    # Q1: 語尾
    if question_key == "Q1":
        # 長音の揺れを吸収
        if text in ["の", "のー", "のぉー"]:
            return "のー"
        if text in ["ず", "ずー", "ずぅー"]:
            return "ずー"
        if text in ["にゃ", "にゃー"]:
            return "にゃー"
        if text in ["べ", "べー"]:
            return "べー"
            
    # Q2: ありがとう
    elif question_key == "Q2":
        # もっけ（庄内弁）のバリエーション正規化
        if text.startswith("もっけ"):
            return "もっけだの"
            
        # 「ありがとう」の長音表記などは統一するが、濁点は区別する
        if text in ["ありがと", "ありがとう", "ありがとうー"]:
            return "ありがとう"  # 標準語的/清音
        if text in ["ありがど", "ありがどー"]:
            return "ありがど"    # 濁音短縮
        if text in ["ありがとさま", "ありがと様"]:
            return "ありがとさま" # 清音＋さま
            
    # Q3: 冷たい
    elif question_key == "Q3":
        # はっこいのバリエーション
        if text in ["はっこ", "はっこい", "はっこー"]:
            return "はっこい"
            
    return text


@st.cache_data
def get_normalized_answers(df: pd.DataFrame, col_name: str, question_key: str) -> list:
    """
    指定されたカラムの回答を分割・正規化してフラットなリストとして返す
    """
    all_answers = []
    
    for val in df[col_name].dropna():
        # 分割（全角・半角カンマ）
        parts = str(val).replace("、", ",").split(",")
        
        for part in parts:
            normalized = normalize_dialect_term(part, question_key)
            if normalized:
                all_answers.append(normalized)
                
    return all_answers


@st.cache_data
def get_question_distribution(df: pd.DataFrame, question_key: str) -> pd.DataFrame:
    """
    特定の設問の回答分布を取得（分割・正規化済み）
    """
    col_name = QUESTION_COLUMNS.get(question_key)
    if col_name is None or col_name not in df.columns:
        return pd.DataFrame()
    
    # 正規化された全回答リストを取得
    answers = get_normalized_answers(df, col_name, question_key)
    
    if not answers:
        return pd.DataFrame(columns=["回答", "件数"])
    
    # 分布を計算
    distribution = pd.Series(answers).value_counts().reset_index()
    distribution.columns = ["回答", "件数"]
    distribution = distribution.sort_values("件数", ascending=False)
    
    return distribution


@st.cache_data
def get_municipality_distribution(df: pd.DataFrame, question_key: str) -> pd.DataFrame:
    """
    市町村ごとの設問回答分布を取得（分割・正規化済み）
    """
    col_name = QUESTION_COLUMNS.get(question_key)
    if col_name is None or col_name not in df.columns:
        return pd.DataFrame()
    
    # 県外/不明を除外
    df_filtered = df[df["市町村名"] != "県外/不明"].copy()
    
    # レコードごとに展開してリスト化 [(municipality, answer), ...]
    expanded_data = []
    
    for _, row in df_filtered.iterrows():
        municipality = row["市町村名"]
        raw_answer = row[col_name]
        
        if pd.isna(raw_answer):
            continue
            
        parts = str(raw_answer).replace("、", ",").split(",")
        for part in parts:
            normalized = normalize_dialect_term(part, question_key)
            if normalized:
                expanded_data.append({
                    "市町村名": municipality,
                    "回答": normalized
                })
    
    if not expanded_data:
        return pd.DataFrame()
        
    df_expanded = pd.DataFrame(expanded_data)
    
    # クロス集計
    cross_tab = pd.crosstab(df_expanded["市町村名"], df_expanded["回答"])
    
    return cross_tab



def get_free_text_by_municipality(df: pd.DataFrame, municipality: str) -> list:
    """
    指定した市町村の自由記入欄を取得
    
    Args:
        df: 前処理済みDataFrame
        municipality: 市町村名
        
    Returns:
        自由記入欄の内容リスト
    """
    free_text_col = "【自由記入欄】 面白い方言"
    
    if free_text_col not in df.columns:
        return []
    
    # 該当市町村のデータをフィルタ
    df_filtered = df[df["市町村名"] == municipality]
    
    # 自由記入欄を取得（空でないもののみ）
    texts = df_filtered[free_text_col].dropna().tolist()
    texts = [t.strip() for t in texts if t.strip()]
    
    return texts


if __name__ == "__main__":
    # テスト
    print("データ読み込みテスト...")
    df = load_data()
    print(f"  データ件数: {len(df)}")
    print(f"  カラム: {list(df.columns)}")
    print(f"\n市町村名の分布:")
    print(df["市町村名"].value_counts().head(10))
    
    print(f"\nQ2の回答分布:")
    q2_dist = get_question_distribution(df, "Q2")
    print(q2_dist.head(10))
