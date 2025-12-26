#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
包括的サイト分析ツール（修正版）
全記事数の正確な把握とアーカイブ構造の完全調査
"""

import requests
from bs4 import BeautifulSoup
import time
import re
from urllib.parse import urljoin
from datetime import datetime
import sys

def comprehensive_analysis(base_url, delay=1):
    """包括的なサイト分析を実行"""
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })
    
    all_article_links = set()
    
    def get_page(url):
        try:
            print(f"取得中: {url}")
            response = session.get(url)
            response.raise_for_status()
            response.encoding = 'utf-8'
            return BeautifulSoup(response.text, 'html.parser')
        except requests.RequestException as e:
            print(f"エラー: {url} - {e}")
            return None
    
    def extract_article_links(soup):
        """記事リンクを抽出"""
        article_links = set()
        
        # JUGEMの記事パターン: ?eid=数字
        eid_links = soup.find_all('a', href=re.compile(r'\?eid=\d+'))
        for link in eid_links:
            href = link.get('href')
            if href and '?eid=' in href:
                # コメントページを除外
                if '#comments' not in href:
                    full_url = urljoin(base_url, href)
                    # クエリパラメータをクリーンアップ
                    clean_url = full_url.split('#')[0]
                    article_links.add(clean_url)
        
        return article_links
    
    print("=" * 80)
    print("包括的サイト分析を開始")
    print("=" * 80)
    
    # Step 1: トップページ分析
    print("\n1. トップページ分析")
    soup = get_page(base_url)
    if not soup:
        return
    
    initial_articles = extract_article_links(soup)
    all_article_links.update(initial_articles)
    
    print(f"   初期記事リンク: {len(initial_articles)}個")
    
    # Step 2: 月別アーカイブの完全探索
    print("\n2. 月別アーカイブの完全探索")
    
    # より広い範囲で月別アーカイブを探索
    year_months = []
    for year in range(2010, 2026):  # 2010-2025年
        for month in range(1, 13):
            year_months.append(f"{year}{month:02d}")
    
    found_archives = 0
    for ym in year_months:
        archive_url = f"{base_url}?month={ym}"
        time.sleep(delay)
        archive_soup = get_page(archive_url)
        if archive_soup:
            articles_in_page = extract_article_links(archive_soup)
            if articles_in_page:
                all_article_links.update(articles_in_page)
                found_archives += 1
                print(f"   {ym}: {len(articles_in_page)}記事発見")
    
    print(f"   有効なアーカイブページ: {found_archives}個")
    
    # Step 3: ページネーション探索
    print("\n3. ページネーション探索")
    
    for page_num in range(1, 101):  # 最大100ページまで
        page_url = f"{base_url}?page={page_num}"
        time.sleep(delay)
        page_soup = get_page(page_url)
        if page_soup:
            articles_in_page = extract_article_links(page_soup)
            if articles_in_page:
                all_article_links.update(articles_in_page)
                print(f"   ページ{page_num}: {len(articles_in_page)}記事")
            else:
                print(f"   ページ{page_num}: 記事なし（探索終了）")
                break
    
    # Step 4: カテゴリアーカイブ探索
    print("\n4. カテゴリアーカイブ探索")
    
    for cid in range(1, 51):  # カテゴリID 1-50
        category_url = f"{base_url}?cid={cid}"
        time.sleep(delay)
        category_soup = get_page(category_url)
        if category_soup:
            articles_in_page = extract_article_links(category_soup)
            if articles_in_page:
                all_article_links.update(articles_in_page)
                print(f"   カテゴリ{cid}: {len(articles_in_page)}記事")
    
    # Step 5: 結果サマリー
    print("\n" + "=" * 80)
    print("包括的分析結果")
    print("=" * 80)
    print(f"総記事数: {len(all_article_links):,}")
    
    # 記事IDの範囲を分析
    eids = []
    for url in all_article_links:
        match = re.search(r'eid=(\d+)', url)
        if match:
            eids.append(int(match.group(1)))
    
    if eids:
        eids.sort()
        print(f"記事ID範囲: {min(eids)} - {max(eids)}")
        print(f"ID範囲の幅: {max(eids) - min(eids) + 1}")
        print(f"欠番の可能性: {max(eids) - min(eids) + 1 - len(eids)}個")
    
    # 記事URLの一部をサンプル表示
    print(f"\n記事URLサンプル（最初の10個）:")
    for i, url in enumerate(sorted(all_article_links)[:10]):
        print(f"   {i+1:2d}. {url}")
    
    # 結果をファイルに保存
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"comprehensive_analysis_{timestamp}.txt"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"包括的サイト分析結果\n")
        f.write(f"実行日時: {datetime.now()}\n")
        f.write(f"対象URL: {base_url}\n")
        f.write(f"総記事数: {len(all_article_links):,}\n\n")
        
        f.write("全記事URL一覧:\n")
        for url in sorted(all_article_links):
            f.write(f"{url}\n")
    
    print(f"\n詳細結果を {filename} に保存しました")
    
    return {
        'total_articles': len(all_article_links),
        'article_links': all_article_links,
        'eid_range': (min(eids), max(eids)) if eids else None
    }

def main():
    if len(sys.argv) != 2:
        print("使用方法: python comprehensive_analyzer_fixed.py <URL>")
        sys.exit(1)
    
    url = sys.argv[1]
    results = comprehensive_analysis(url, delay=1)

if __name__ == "__main__":
    main() 