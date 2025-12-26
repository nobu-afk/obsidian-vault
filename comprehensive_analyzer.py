#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
包括的サイト分析ツール
全記事数の正確な把握とアーカイブ構造の完全調査
"""

import requests
from bs4 import BeautifulSoup
import time
import re
from urllib.parse import urljoin, urlparse
from datetime import datetime
import sys

class ComprehensiveAnalyzer:
    def __init__(self, base_url, delay=1):
        self.base_url = base_url
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.all_article_links = set()
        self.archive_pages = set()
        
    def get_page(self, url):
        """ページを取得する"""
        try:
            print(f"取得中: {url}")
            response = self.session.get(url)
            response.raise_for_status()
            response.encoding = 'utf-8'
            return BeautifulSoup(response.text, 'html.parser')
        except requests.RequestException as e:
            print(f"エラー: {url} - {e}")
            return None

    def extract_article_links(self, soup):
        """記事リンクを抽出"""
        article_links = set()
        
        # JUGEMの記事パターン: ?eid=数字
        eid_links = soup.find_all('a', href=re.compile(r'\?eid=\d+'))
        for link in eid_links:
            href = link.get('href')
            if href and '?eid=' in href:
                # コメントページを除外
                if '#comments' not in href:
                    full_url = urljoin(self.base_url, href)
                    # クエリパラメータをクリーンアップ
                    clean_url = full_url.split('#')[0]
                    article_links.add(clean_url)
        
        return article_links

    def find_archive_patterns(self, soup):
        """アーカイブページのパターンを発見"""
        archive_links = set()
        
        # 月別アーカイブ (?month=YYYYMM)
        month_links = soup.find_all('a', href=re.compile(r'\?month=\d{6}'))
        for link in month_links:
            href = link.get('href')
            if href:
                full_url = urljoin(self.base_url, href)
                archive_links.add(full_url)
        
        # カテゴリアーカイブ (?cid=数字)
        category_links = soup.find_all('a', href=re.compile(r'\?cid=\d+'))
        for link in category_links:
            href = link.get('href')
            if href:
                full_url = urljoin(self.base_url, href)
                archive_links.add(full_url)
        
        # ページネーション
        page_links = soup.find_all('a', href=re.compile(r'\?page=\d+'))
        for link in page_links:
            href = link.get('href')
            if href:
                full_url = urljoin(self.base_url, href)
                archive_links.add(full_url)
        
        return archive_links

    def analyze_date_range(self, soup):
        """記事の日付範囲を分析"""
        dates = []
        
        # ページ内の日付パターンを探す
        date_patterns = [
            r'(\d{4})\.(\d{1,2})\.(\d{1,2})',  # 2025.01.08
            r'(\d{4})/(\d{1,2})/(\d{1,2})',   # 2025/01/08
            r'(\d{4})-(\d{1,2})-(\d{1,2})',   # 2025-01-08
        ]
        
        page_text = soup.get_text()
        for pattern in date_patterns:
            matches = re.findall(pattern, page_text)
            for year, month, day in matches:
                try:
                    date_str = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                    dates.append(date_str)
                except:
                    continue
        
        return dates

    def comprehensive_crawl(self):
        """包括的なクロール実行"""
        print("=" * 80)
        print("包括的サイト分析を開始")
        print("=" * 80)
        
        # Step 1: トップページ分析
        print("\n1. トップページ分析")
        soup = self.get_page(self.base_url)
        if not soup:
            return
        
        # 初期記事とアーカイブリンクを取得
        initial_articles = self.extract_article_links(soup)
        initial_archives = self.find_archive_patterns(soup)
        
        self.all_article_links.update(initial_articles)
        self.archive_pages.update(initial_archives)
        
        print(f"   初期記事リンク: {len(initial_articles)}個")
        print(f"   初期アーカイブページ: {len(initial_archives)}個")
        
        # Step 2: 日付範囲分析
        print("\n2. 日付範囲分析")
        dates = self.analyze_date_range(soup)
        if dates:
            dates.sort()
            print(f"   最古の日付: {dates[0]}")
            print(f"   最新の日付: {dates[-1]}")
            print(f"   発見された日付数: {len(set(dates))}")
        
        # Step 3: 月別アーカイブの完全探索
        print("\n3. 月別アーカイブの完全探索")
        
        # より多くの月別アーカイブを推測して試行
        year_months = []
        for year in range(2020, 2026):  # 2020-2025年
            for month in range(1, 13):
                year_months.append(f"{year}{month:02d}")
        
        found_archives = 0
        for ym in year_months:
            archive_url = f"{self.base_url}?month={ym}"
            if archive_url not in self.archive_pages:
                time.sleep(self.delay)
                archive_soup = self.get_page(archive_url)
                if archive_soup:
                    # このページに記事があるかチェック
                    articles_in_page = self.extract_article_links(archive_soup)
                    if articles_in_page:
                        self.archive_pages.add(archive_url)
                        self.all_article_links.update(articles_in_page)
                        found_archives += 1
                        print(f"   {ym}: {len(articles_in_page)}記事発見")
        
        print(f"   追加アーカイブページ: {found_archives}個")
        
        # Step 4: 既知のアーカイブページからの記事収集
        print("\n4. 既知のアーカイブページからの記事収集")
        processed_archives = 0
        
        for archive_url in list(self.archive_pages):
            if processed_archives % 10 == 0:
                print(f"   処理中: {processed_archives}/{len(self.archive_pages)}")
            
            time.sleep(self.delay)
            archive_soup = self.get_page(archive_url)
            if archive_soup:
                articles_in_page = self.extract_article_links(archive_soup)
                self.all_article_links.update(articles_in_page)
                
                # さらなるアーカイブページを発見
                more_archives = self.find_archive_patterns(archive_soup)
                new_archives = more_archives - self.archive_pages
                if new_archives:
                    self.archive_pages.update(new_archives)
                    print(f"   新しいアーカイブページ発見: {len(new_archives)}個")
            
            processed_archives += 1
        
        # Step 5: ページネーション探索
        print("\n5. ページネーション探索")
        
        # ?page=数字 のパターンでページネーションを探索
        for page_num in range(1, 51):  # 最大50ページまで
            page_url = f"{self.base_url}?page={page_num}"
            time.sleep(self.delay)
            page_soup = self.get_page(page_url)
            if page_soup:
                articles_in_page = self.extract_article_links(page_soup)
                if articles_in_page:
                    self.all_article_links.update(articles_in_page)
                    print(f"   ページ{page_num}: {len(articles_in_page)}記事")
                else:
                    # 記事がなくなったら終了
                    print(f"   ページ{page_num}: 記事なし（探索終了）")
                    break
        
        # Step 6: 結果サマリー
        print("\n" + "=" * 80)
        print("包括的分析結果")
        print("=" * 80)
        print(f"総記事数: {len(self.all_article_links):,}")
        print(f"アーカイブページ数: {len(self.archive_pages):,}")
        
                 # 記事IDの範囲を分析
         eids = []
         for url in self.all_article_links:
             match = re.search(r'eid=(\d+)', url)
             if match:
                 eids.append(int(match.group(1)))
         
         eid_range = None
         if eids:
             eids.sort()
             eid_range = (min(eids), max(eids))
             print(f"記事ID範囲: {min(eids)} - {max(eids)}")
             print(f"ID範囲の幅: {max(eids) - min(eids) + 1}")
             print(f"欠番の可能性: {max(eids) - min(eids) + 1 - len(eids)}個")
         
         # 記事URLの一部をサンプル表示
         print(f"\n記事URLサンプル（最初の10個）:")
         for i, url in enumerate(sorted(self.all_article_links)[:10]):
             print(f"   {i+1:2d}. {url}")
         
         return {
             'total_articles': len(self.all_article_links),
             'archive_pages': len(self.archive_pages),
             'article_links': self.all_article_links,
             'archive_links': self.archive_pages,
             'eid_range': eid_range
         }

def main():
    if len(sys.argv) != 2:
        print("使用方法: python comprehensive_analyzer.py <URL>")
        sys.exit(1)
    
    url = sys.argv[1]
    analyzer = ComprehensiveAnalyzer(url, delay=1)
    results = analyzer.comprehensive_crawl()
    
    # 結果をファイルに保存
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"comprehensive_analysis_{timestamp}.txt"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"包括的サイト分析結果\n")
        f.write(f"実行日時: {datetime.now()}\n")
        f.write(f"対象URL: {url}\n")
        f.write(f"総記事数: {results['total_articles']:,}\n")
        f.write(f"アーカイブページ数: {results['archive_pages']:,}\n\n")
        
        f.write("全記事URL一覧:\n")
        for url in sorted(results['article_links']):
            f.write(f"{url}\n")
        
        f.write("\nアーカイブページ一覧:\n")
        for url in sorted(results['archive_links']):
            f.write(f"{url}\n")
    
    print(f"\n詳細結果を {filename} に保存しました")

if __name__ == "__main__":
    main() 