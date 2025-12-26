#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ブログ記事テキスト抽出ツール
研究目的でのテキスト分析用

使用方法:
python blog_scraper.py --url https://terminalhill.jugem.jp/ --output articles.txt

必要なライブラリ:
pip install requests beautifulsoup4 lxml
"""

import requests
from bs4 import BeautifulSoup
import time
import re
import argparse
import os
from urllib.parse import urljoin, urlparse
from datetime import datetime

class BlogScraper:
    def __init__(self, base_url, delay=1):
        """
        ブログスクレイパーの初期化
        
        Args:
            base_url (str): ベースURL
            delay (int): リクエスト間の待機時間（秒）
        """
        self.base_url = base_url
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
    def get_page(self, url):
        """
        ページを取得する
        
        Args:
            url (str): 取得するURL
            
        Returns:
            BeautifulSoup: パースされたHTML
        """
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
        記事リンクを抽出する
        
        Args:
            soup (BeautifulSoup): パースされたHTML
            
        Returns:
            list: 記事URLのリスト
        """
        article_links = []
        
        # 一般的なブログのリンクパターンを試行
        selectors = [
            'a[href*="/entry/"]',  # はてなブログ系
            'a[href*="/archives/"]',  # アーカイブ系
            '.entry-title a',  # エントリータイトル
            '.post-title a',   # ポストタイトル
            'h2 a',            # 見出し内のリンク
            'h3 a',            # 見出し内のリンク
            'article a',       # article要素内のリンク
        ]
        
        for selector in selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get('href')
                if href:
                    full_url = urljoin(self.base_url, href)
                    if self.is_article_url(full_url):
                        article_links.append(full_url)
        
        # 重複を除去
        return list(set(article_links))
    
    def is_article_url(self, url):
        """
        記事URLかどうかを判定する
        
        Args:
            url (str): 判定するURL
            
        Returns:
            bool: 記事URLの場合True
        """
        # 除外するパターン
        exclude_patterns = [
            '/category/',
            '/tag/',
            '/search/',
            '/admin/',
            '/login/',
            '/contact/',
            '/about/',
            'javascript:',
            'mailto:',
            '#'
        ]
        
        for pattern in exclude_patterns:
            if pattern in url:
                return False
                
        # 同じドメインの記事のみを対象とする
        base_domain = urlparse(self.base_url).netloc
        url_domain = urlparse(url).netloc
        
        return base_domain == url_domain
    
    def extract_article_text(self, soup, url):
        """
        記事のテキストを抽出する
        
        Args:
            soup (BeautifulSoup): パースされたHTML
            url (str): 記事のURL
            
        Returns:
            dict: 記事情報（タイトル、本文、日付など）
        """
        article_data = {
            'url': url,
            'title': '',
            'content': '',
            'date': '',
            'extracted_at': datetime.now().isoformat()
        }
        
        # タイトルを抽出
        title_selectors = [
            'h1',
            '.entry-title',
            '.post-title',
            'title'
        ]
        
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                article_data['title'] = title_elem.get_text().strip()
                break
        
        # 日付を抽出
        date_selectors = [
            '.entry-date',
            '.post-date',
            'time',
            '.date'
        ]
        
        for selector in date_selectors:
            date_elem = soup.select_one(selector)
            if date_elem:
                article_data['date'] = date_elem.get_text().strip()
                break
        
        # 本文を抽出
        content_selectors = [
            '.entry-content',
            '.post-content',
            'article',
            '.content',
            'main',
            '#main'
        ]
        
        content_elem = None
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                break
        
        if content_elem:
            # 不要な要素を除去
            for unwanted in content_elem.select('script, style, nav, footer, .sidebar, .comment'):
                unwanted.decompose()
            
            # テキストを抽出
            text = content_elem.get_text()
            # 改行や空白を整理
            text = re.sub(r'\n\s*\n', '\n\n', text)
            text = re.sub(r' +', ' ', text)
            article_data['content'] = text.strip()
        
        return article_data
    
    def scrape_site(self, max_articles=None):
        """
        サイト全体をスクレイピングする
        
        Args:
            max_articles (int): 最大記事数（Noneの場合は全て）
            
        Returns:
            list: 抽出した記事データのリスト
        """
        print(f"サイトのスクレイピングを開始: {self.base_url}")
        
        # トップページから記事リンクを取得
        soup = self.get_page(self.base_url)
        if not soup:
            return []
        
        article_links = self.extract_article_links(soup)
        print(f"発見された記事数: {len(article_links)}")
        
        # アーカイブページからも記事を探す
        archive_links = self.find_archive_pages(soup)
        for archive_url in archive_links:
            time.sleep(self.delay)
            archive_soup = self.get_page(archive_url)
            if archive_soup:
                more_links = self.extract_article_links(archive_soup)
                article_links.extend(more_links)
        
        # 重複除去
        article_links = list(set(article_links))
        print(f"総記事数: {len(article_links)}")
        
        if max_articles:
            article_links = article_links[:max_articles]
            print(f"取得対象記事数: {max_articles}")
        
        # 各記事を取得
        articles = []
        for i, url in enumerate(article_links, 1):
            print(f"記事取得中 ({i}/{len(article_links)}): {url}")
            
            time.sleep(self.delay)
            article_soup = self.get_page(url)
            if article_soup:
                article_data = self.extract_article_text(article_soup, url)
                if article_data['content']:  # 本文が取得できた場合のみ追加
                    articles.append(article_data)
                    print(f"  ✓ タイトル: {article_data['title'][:50]}...")
                else:
                    print(f"  ✗ 本文取得失敗")
            else:
                print(f"  ✗ ページ取得失敗")
        
        return articles
    
    def find_archive_pages(self, soup):
        """
        アーカイブページのURLを探す
        
        Args:
            soup (BeautifulSoup): パースされたHTML
            
        Returns:
            list: アーカイブページのURLリスト
        """
        archive_links = []
        
        # アーカイブリンクの候補
        archive_selectors = [
            'a[href*="archive"]',
            'a[href*="month"]',
            'a[href*="年"]',
            'a[href*="月"]',
            '.archive a',
            '.monthly a',
            '.calendar a'
        ]
        
        for selector in archive_selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get('href')
                if href:
                    full_url = urljoin(self.base_url, href)
                    archive_links.append(full_url)
        
        return list(set(archive_links))[:10]  # 最大10ページまで

def save_articles(articles, output_file):
    """
    記事データをファイルに保存する
    
    Args:
        articles (list): 記事データのリスト
        output_file (str): 出力ファイル名
    """
    print(f"\n記事データを保存中: {output_file}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# ブログ記事テキストデータ\n")
        f.write(f"# 抽出日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"# 総記事数: {len(articles)}\n\n")
        f.write("=" * 80 + "\n\n")
        
        for i, article in enumerate(articles, 1):
            f.write(f"記事 {i}/{len(articles)}\n")
            f.write(f"URL: {article['url']}\n")
            f.write(f"タイトル: {article['title']}\n")
            f.write(f"日付: {article['date']}\n")
            f.write("-" * 80 + "\n")
            f.write(article['content'])
            f.write("\n\n" + "=" * 80 + "\n\n")
    
    print(f"✓ 保存完了: {len(articles)}記事を{output_file}に保存しました")

def main():
    parser = argparse.ArgumentParser(description='ブログ記事テキスト抽出ツール')
    parser.add_argument('--url', required=True, help='ブログのURL')
    parser.add_argument('--output', default='blog_articles.txt', help='出力ファイル名')
    parser.add_argument('--max-articles', type=int, help='最大記事数')
    parser.add_argument('--delay', type=int, default=1, help='リクエスト間の待機時間（秒）')
    
    args = parser.parse_args()
    
    # スクレイピング実行
    scraper = BlogScraper(args.url, delay=args.delay)
    articles = scraper.scrape_site(max_articles=args.max_articles)
    
    if articles:
        save_articles(articles, args.output)
        print(f"\n完了: {len(articles)}記事を抽出しました")
        
        # 統計情報
        total_chars = sum(len(article['content']) for article in articles)
        avg_chars = total_chars // len(articles) if articles else 0
        print(f"総文字数: {total_chars:,}")
        print(f"平均文字数: {avg_chars:,}")
    else:
        print("記事を取得できませんでした")

if __name__ == "__main__":
    main() 