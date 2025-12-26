#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
正しいURLリスト生成スクリプト
terminalhill.jugem.jpドメインの正しいURLを生成
"""

import requests
from bs4 import BeautifulSoup
import time
import re
from datetime import datetime

def generate_correct_urls():
    """正しいURLリストを生成"""
    
    base_url = "https://terminalhill.jugem.jp/"
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    })
    
    all_article_links = set()
    
    def extract_article_links(soup):
        """記事リンクを抽出"""
        article_links = set()
        
        # JUGEMの記事パターン: ?eid=数字
        eid_links = soup.find_all('a', href=re.compile(r'\?eid=\d+'))
        for link in eid_links:
            href = link.get('href')
            if href and '?eid=' in href:
                if '#comments' not in href:
                    # 正しいドメインに修正
                    if href.startswith('http://04goto.com/'):
                        href = href.replace('http://04goto.com/', 'https://terminalhill.jugem.jp/')
                    elif href.startswith('http://terminalhill.jugem.jp/'):
                        href = href.replace('http://terminalhill.jugem.jp/', 'https://terminalhill.jugem.jp/')
                    elif not href.startswith('http'):
                        href = base_url + href.lstrip('/')
                    
                    clean_url = href.split('#')[0]
                    article_links.add(clean_url)
        
        return article_links
    
    print("正しいURLリストを生成中...")
    print("=" * 60)
    
    # 月別アーカイブから収集
    year_months = []
    for year in range(2010, 2026):
        for month in range(1, 13):
            year_months.append(f"{year}{month:02d}")
    
    found_articles = 0
    for ym in year_months:
        archive_url = f"{base_url}?month={ym}"
        try:
            response = session.get(archive_url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                articles = extract_article_links(soup)
                if articles:
                    all_article_links.update(articles)
                    found_articles += len(articles)
                    print(f"✓ {ym}: {len(articles)}記事発見 (累計: {len(all_article_links)})")
        except:
            continue
        
        time.sleep(0.5)  # 高速処理
    
    # ページネーションからも収集
    print("\nページネーション探索中...")
    for page_num in range(1, 101):
        page_url = f"{base_url}?page={page_num}"
        try:
            response = session.get(page_url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                articles = extract_article_links(soup)
                if articles:
                    all_article_links.update(articles)
                    print(f"✓ ページ{page_num}: {len(articles)}記事")
                else:
                    break
        except:
            break
        
        time.sleep(0.5)
    
    print(f"\n📊 最終結果: {len(all_article_links)}個の正しいURL")
    
    # ファイルに保存
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"correct_urls_{timestamp}.txt"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"正しい記事URL一覧 (terminalhill.jugem.jp)\n")
        f.write(f"生成日時: {datetime.now()}\n")
        f.write(f"総記事数: {len(all_article_links)}\n\n")
        f.write("全記事URL一覧:\n")
        
        for url in sorted(all_article_links):
            f.write(f"{url}\n")
    
    print(f"✅ 正しいURLリストを {filename} に保存しました")
    return filename, len(all_article_links)

if __name__ == "__main__":
    filename, count = generate_correct_urls()
    print(f"\n🎯 次のステップ:")
    print(f"python complete_scraper.py --url-list {filename} --output terminalhill_correct_all_articles.txt --delay 2") 