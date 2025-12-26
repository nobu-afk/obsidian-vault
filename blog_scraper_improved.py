#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
改良版ブログ記事テキスト抽出ツール
terminalhill.jugem.jp 専用に最適化

使用方法:
python blog_scraper_improved.py --url https://terminalhill.jugem.jp/ --output articles.txt
"""

import requests
from bs4 import BeautifulSoup
import time
import re
import argparse
import os
from urllib.parse import urljoin, urlparse
from datetime import datetime

class ImprovedBlogScraper:
    def __init__(self, base_url, delay=1):
        """
        改良版ブログスクレイパーの初期化
        """
        self.base_url = base_url
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
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
        """
        記事リンクを抽出する（JUGEM特化版）
        """
        article_links = []
        
        # JUGEMの記事パターン: ?eid=数字
        eid_links = soup.find_all('a', href=re.compile(r'\?eid=\d+'))
        for link in eid_links:
            href = link.get('href')
            if href:
                full_url = urljoin(self.base_url, href)
                article_links.append(full_url)
                print(f"  発見: {link.get_text().strip()[:30]}... -> {full_url}")
        
        # h2タグ内のリンクも確認
        h2_links = soup.select('h2 a[href*="?eid="]')
        for link in h2_links:
            href = link.get('href')
            if href:
                full_url = urljoin(self.base_url, href)
                article_links.append(full_url)
                print(f"  H2発見: {link.get_text().strip()[:30]}... -> {full_url}")
        
        # 重複を除去
        unique_links = list(set(article_links))
        print(f"  重複除去後: {len(unique_links)}個の記事リンク")
        return unique_links
    
    def extract_article_text(self, soup, url):
        """
        記事のテキストを抽出する（JUGEM特化版）
        """
        article_data = {
            'url': url,
            'title': '',
            'content': '',
            'date': '',
            'extracted_at': datetime.now().isoformat()
        }
        
        # タイトルを抽出（JUGEMの構造に特化）
        title_selectors = [
            'h1',
            'h2',
            '.entry-title',
            'title'
        ]
        
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                title_text = title_elem.get_text().strip()
                # JUGEMサイトのタイトルを除外
                if title_text and not title_text.startswith('����Ω�ĻŻ'):
                    article_data['title'] = title_text
                    break
        
        # 日付を抽出
        date_patterns = [
            r'(\d{4})\.(\d{1,2})\.(\d{1,2})',  # 2025.01.08 形式
            r'(\d{4})/(\d{1,2})/(\d{1,2})',   # 2025/01/08 形式
        ]
        
        page_text = soup.get_text()
        for pattern in date_patterns:
            matches = re.findall(pattern, page_text)
            if matches:
                year, month, day = matches[0]
                article_data['date'] = f"{year}.{month.zfill(2)}.{day.zfill(2)}"
                break
        
        # 本文を抽出（JUGEM特化）
        content_selectors = [
            '.entry',      # JUGEMの記事コンテナ
            '#main .entry',
            'article',
            '.content',
            '#main'
        ]
        
        content_elem = None
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                print(f"    本文抽出: {selector} を使用")
                break
        
        if content_elem:
            # 不要な要素を除去
            for unwanted in content_elem.select('script, style, nav, footer, .sidebar, .comment, .navigation'):
                unwanted.decompose()
            
            # 広告やメニューを除去
            for unwanted in content_elem.select('.ad, .menu, .ranking, .link'):
                unwanted.decompose()
            
            # テキストを抽出
            text = content_elem.get_text()
            
            # テキストをクリーンアップ
            text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)  # 過度な改行を削除
            text = re.sub(r' +', ' ', text)               # 複数スペースを単一に
            text = re.sub(r'\t+', ' ', text)              # タブをスペースに
            
            # JUGEMの定型文を除去
            cleanup_patterns = [
                r'����click����������ꤤ���ޤ���.*?\n',
                r'��󥭥󥰤˻��ä��Ƥ��ޤ���.*?\n',
                r'Tweet.*?\n',
                r'Posted by.*?\n',
                r'comments\(\d+\).*?\n',
            ]
            
            for pattern in cleanup_patterns:
                text = re.sub(pattern, '', text, flags=re.MULTILINE)
            
            article_data['content'] = text.strip()
        
        return article_data
    
    def find_archive_pages(self, soup):
        """アーカイブページを探す"""
        archive_links = []
        
        # 月別アーカイブ (?month=YYYYMM)
        month_links = soup.find_all('a', href=re.compile(r'\?month=\d{6}'))
        for link in month_links:
            href = link.get('href')
            if href:
                full_url = urljoin(self.base_url, href)
                archive_links.append(full_url)
        
        print(f"アーカイブページ発見: {len(archive_links)}個")
        return archive_links
    
    def scrape_site(self, max_articles=None):
        """
        サイト全体をスクレイピングする
        """
        print(f"サイトのスクレイピングを開始: {self.base_url}")
        
        # トップページから記事リンクを取得
        soup = self.get_page(self.base_url)
        if not soup:
            return []
        
        article_links = self.extract_article_links(soup)
        print(f"トップページで発見された記事数: {len(article_links)}")
        
        # アーカイブページからも記事を探す
        archive_links = self.find_archive_pages(soup)
        for i, archive_url in enumerate(archive_links[:20]):  # 最大20ページ
            print(f"アーカイブページ取得中 ({i+1}/{min(len(archive_links), 20)})")
            time.sleep(self.delay)
            archive_soup = self.get_page(archive_url)
            if archive_soup:
                more_links = self.extract_article_links(archive_soup)
                article_links.extend(more_links)
                print(f"  追加記事: {len(more_links)}個")
        
        # 重複除去
        article_links = list(set(article_links))
        print(f"総記事数: {len(article_links)}")
        
        if max_articles:
            article_links = article_links[:max_articles]
            print(f"取得対象記事数: {max_articles}")
        
        # 各記事を取得
        articles = []
        for i, url in enumerate(article_links, 1):
            print(f"記事取得中 ({i}/{len(article_links)})")
            
            time.sleep(self.delay)
            article_soup = self.get_page(url)
            if article_soup:
                article_data = self.extract_article_text(article_soup, url)
                if article_data['content'] and len(article_data['content']) > 100:  # 100文字以上の場合のみ
                    articles.append(article_data)
                    print(f"  ✓ タイトル: {article_data['title'][:30]}...")
                    print(f"  ✓ 本文: {len(article_data['content'])}文字")
                else:
                    print(f"  ✗ 本文取得失敗または短すぎる")
            else:
                print(f"  ✗ ページ取得失敗")
        
        return articles

def save_articles(articles, output_file):
    """記事データをファイルに保存する"""
    print(f"\n記事データを保存中: {output_file}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# ブログ記事テキストデータ\n")
        f.write(f"# 抽出元: https://terminalhill.jugem.jp/\n")
        f.write(f"# 抽出日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"# 総記事数: {len(articles)}\n\n")
        f.write("=" * 80 + "\n\n")
        
        for i, article in enumerate(articles, 1):
            f.write(f"記事 {i}/{len(articles)}\n")
            f.write(f"URL: {article['url']}\n")
            f.write(f"タイトル: {article['title']}\n")
            f.write(f"日付: {article['date']}\n")
            f.write(f"文字数: {len(article['content'])}\n")
            f.write("-" * 80 + "\n")
            f.write(article['content'])
            f.write("\n\n" + "=" * 80 + "\n\n")
    
    print(f"✓ 保存完了: {len(articles)}記事を{output_file}に保存しました")

def main():
    parser = argparse.ArgumentParser(description='改良版ブログ記事テキスト抽出ツール')
    parser.add_argument('--url', required=True, help='ブログのURL')
    parser.add_argument('--output', default='terminalhill_articles.txt', help='出力ファイル名')
    parser.add_argument('--max-articles', type=int, help='最大記事数')
    parser.add_argument('--delay', type=int, default=2, help='リクエスト間の待機時間（秒）')
    
    args = parser.parse_args()
    
    # スクレイピング実行
    scraper = ImprovedBlogScraper(args.url, delay=args.delay)
    articles = scraper.scrape_site(max_articles=args.max_articles)
    
    if articles:
        save_articles(articles, args.output)
        print(f"\n✅ 完了: {len(articles)}記事を抽出しました")
        
        # 統計情報
        total_chars = sum(len(article['content']) for article in articles)
        avg_chars = total_chars // len(articles) if articles else 0
        titles_with_content = sum(1 for article in articles if article['title'])
        dates_found = sum(1 for article in articles if article['date'])
        
        print(f"📊 統計情報:")
        print(f"   総文字数: {total_chars:,}")
        print(f"   平均文字数: {avg_chars:,}")
        print(f"   タイトル取得率: {titles_with_content}/{len(articles)} ({titles_with_content/len(articles)*100:.1f}%)")
        print(f"   日付取得率: {dates_found}/{len(articles)} ({dates_found/len(articles)*100:.1f}%)")
    else:
        print("❌ 記事を取得できませんでした")

if __name__ == "__main__":
    main() 