#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2022年以降 TerminalHill記事 正しいエンコーディング再取得・分割スクリプト
"""

import re
import os
import time
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import random

class Post2022Rescraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        self.articles = []
        self.start_part_num = 16
        self.max_chars = 500_000

    def get_correct_encoding_content(self, url):
        """正しいエンコーディングで記事内容を取得"""
        encodings = ['euc-jp', 'utf-8', 'shift_jis', 'iso-2022-jp']
        
        for encoding in encodings:
            try:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                if encoding == 'utf-8':
                    text = response.text
                else:
                    text = response.content.decode(encoding, errors='ignore')
                
                if self.has_valid_japanese(text):
                    return text, encoding
                    
            except Exception:
                continue
        
        return None, None

    def has_valid_japanese(self, text):
        """日本語妥当性チェック"""
        if not text:
            return False
        
        japanese_chars = re.findall(r'[あ-んア-ンー一-龯]', text)
        japanese_count = len(japanese_chars)
        
        garbled_patterns = ['�', '縺', '繝', '繧']
        has_garbled = any(pattern in text for pattern in garbled_patterns)
        
        return japanese_count > 50 and not has_garbled

    def extract_article_data(self, url, html_content):
        """記事データを抽出"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        title = ""
        title_selectors = ['h1.title', '.entry-title', 'h1', 'title']
        for selector in title_selectors:
            element = soup.select_one(selector)
            if element:
                title = element.get_text(strip=True)
                if self.has_valid_japanese(title):
                    break
        
        date = ""
        date_patterns = [
            r'(\d{4})\.(\d{2})\.(\d{2})',
            r'(\d{4})-(\d{2})-(\d{2})',
            r'(\d{4})/(\d{2})/(\d{2})'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, html_content)
            if match:
                y, m, d = match.groups()
                date = f"{y}-{m}-{d}"
                break
        
        content = ""
        content_selectors = ['.entry', '.post-content', '.content', 'article']
        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                for tag in element.find_all(['script', 'style', 'nav', 'footer']):
                    tag.decompose()
                
                content = element.get_text(separator='\n', strip=True)
                if self.has_valid_japanese(content) and len(content) > 200:
                    break
        
        return {
            'url': url,
            'title': title,
            'date': date,
            'content': content,
            'char_count': len(content)
        }

    def generate_2022_plus_urls(self):
        """2022年以降の記事URLを生成"""
        urls = []
        estimated_eids = list(range(5637, 7000))
        
        for eid in estimated_eids:
            urls.append(f"https://terminalhill.jugem.jp/?eid={eid}")
        
        return urls

    def scrape_post2022_articles(self):
        """2022年以降の記事を再取得"""
        print("🔄 2022年以降記事の正しいエンコーディング再取得開始")
        
        urls = self.generate_2022_plus_urls()
        print(f"📋 対象URL数: {len(urls)}")
        
        success_count = 0
        
        for i, url in enumerate(urls, 1):
            try:
                print(f"[{i}/{len(urls)}] {url}")
                
                html_content, encoding = self.get_correct_encoding_content(url)
                if not html_content:
                    print(f"  ❌ エンコーディング取得失敗")
                    continue
                
                article_data = self.extract_article_data(url, html_content)
                
                if article_data['date']:
                    try:
                        year = int(article_data['date'][:4])
                        if year < 2022:
                            print(f"  ⏭️ 2022年未満: {article_data['date']}")
                            continue
                    except:
                        pass
                
                if article_data['content'] and len(article_data['content']) > 200:
                    article_data['encoding'] = encoding
                    self.articles.append(article_data)
                    success_count += 1
                    print(f"  ✅ 成功: {article_data['title'][:30]}... ({article_data['char_count']}文字)")
                else:
                    print(f"  ❌ コンテンツ不足")
                
                time.sleep(random.uniform(0.5, 1.5))
                
            except Exception as e:
                print(f"  ❌ エラー: {e}")
                continue
        
        print(f"\n✅ 再取得完了: {success_count}記事")
        return success_count > 0

if __name__ == "__main__":
    scraper = Post2022Rescraper()
    scraper.scrape_post2022_articles()
