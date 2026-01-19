# -*- coding: utf-8 -*-
"""
山形県方言アンケート分析スクリプト
"""

import sys
sys.path.insert(0, '.')
from data_processor import load_data, get_question_distribution, QUESTION_LABELS, QUESTION_COLUMNS
import pandas as pd

df = load_data()

print('=' * 60)
print('山形県方言アンケート分析レポート')
print('=' * 60)
print()
print(f'総回答数: {len(df)}件')
yamagata_df = df[df["市町村名"] != "県外/不明"]
print(f'県内回答数: {len(yamagata_df)}件')
print(f'回答のあった市町村: {yamagata_df["市町村名"].nunique()}箇所')
print()

print('=' * 60)
print('地域別回答数')
print('=' * 60)
print(df['地域'].value_counts())
print()

for q_key, q_label in QUESTION_LABELS.items():
    dist = get_question_distribution(df, q_key)
    if not dist.empty:
        print('=' * 60)
        print(f'{q_key}: {q_label}')
        print('=' * 60)
        print(dist.head(5).to_string(index=False))
        print()
