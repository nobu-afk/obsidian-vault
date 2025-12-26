#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
残りの記事取得スクリプト
既存の2つのファイルから取得済み記事を除外し、残りを抽出
"""

import requests
from bs4 import BeautifulSoup
import time
import re
from datetime import datetime

def extract_existing_article_ids():
    """既存ファイルから取得済み記事IDを抽出"""
    existing_ids = set()
    
    files = [
        'terminalhill_all_5652_articles.txt',
        'terminalhill_clean_all_articles.txt'
    ]
    
    for filename in files:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
                # URL: https://terminalhill.jugem.jp/?eid=数字 のパターンを抽出
                url_pattern = r'URL: https://terminalhill\.jugem\.jp/\?eid=(\d+)'
                matches = re.findall(url_pattern, content)
                for match in matches:
                    existing_ids.add(int(match))
            print(f"✓ {filename}: {len(matches)}記事のIDを抽出")
        except FileNotFoundError:
            print(f"⚠️ {filename} が見つかりません")
    
    return existing_ids

def generate_remaining_article_range():
    """残りの記事ID範囲を生成"""
    # 包括分析で発見された記事ID範囲: 137〜52,887
    # より広範囲をカバーするため、100〜53,000で検索
    return range(100, 53001)

def extract_remaining_articles():
    """残りの記事を抽出"""
    
    print("🔍 既存記事IDの抽出中...")
    existing_ids = extract_existing_article_ids()
    print(f"✓ 取得済み記事数: {len(existing_ids)}記事")
    
    print("\n🎯 残りの記事ID範囲を生成中...")
    all_possible_ids = set(generate_remaining_article_range())
    remaining_ids = sorted(all_possible_ids - existing_ids)
    
    print(f"✓ 残り記事数: {len(remaining_ids)}記事")
    print(f"ID範囲: {min(remaining_ids)} 〜 {max(remaining_ids)}")
    
    # 残りの記事URLリストを生成
    remaining_urls = []
    for article_id in remaining_ids:
        remaining_urls.append(f"https://terminalhill.jugem.jp/?eid={article_id}")
    
    # URLリストをファイルに保存
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    url_file = f"remaining_urls_{timestamp}.txt"
    
    with open(url_file, 'w', encoding='utf-8') as f:
        for url in remaining_urls:
            f.write(url + '\n')
    
    print(f"✓ 残りURLリスト保存: {url_file}")
    print(f"📊 残り記事URL数: {len(remaining_urls)}個")
    
    return url_file, len(remaining_urls)

if __name__ == "__main__":
    print("=" * 80)
    print("🚀 残りの記事抽出準備")
    print("=" * 80)
    
    url_file, remaining_count = extract_remaining_articles()
    
    print(f"\n✅ 準備完了!")
    print(f"📁 URLファイル: {url_file}")
    print(f"🎯 残り記事数: {remaining_count:,}記事")
    print(f"\n次のステップ:")
    print(f"python complete_scraper.py --url-list {url_file} --output terminalhill_remaining_articles.txt --delay 2 &") 