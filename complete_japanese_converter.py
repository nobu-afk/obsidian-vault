#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import argparse
from datetime import datetime
from pathlib import Path
import sys
import codecs

class CompleteJapaneseConverter:
    def __init__(self, delay=2):
        self.delay = delay
        self.session = requests.Session()
        
        # 日本語対応のヘッダー設定
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'ja,ja-JP;q=0.9,en;q=0.8',
            'Accept-Charset': 'utf-8, shift_jis, euc-jp, iso-2022-jp',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        })
        
        self.total_chars = 0
        self.success_count = 0
        self.fail_count = 0

    def extract_urls_from_garbled_file(self, file_path):
        """文字化けファイルからURLを抽出"""
        urls = []
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                # URLパターンを検索
                url_pattern = r'https?://terminalhill\.jugem\.jp/\?eid=\d+'
                found_urls = re.findall(url_pattern, content)
                urls.extend(found_urls)
                
                # コメント付きURLも検索
                comment_pattern = r'https?://terminalhill\.jugem\.jp/\?eid=\d+#comments'
                found_comment_urls = re.findall(comment_pattern, content)
                urls.extend(found_comment_urls)
                
        except Exception as e:
            print(f"ファイル読み込みエラー: {e}")
        
        # 重複除去とソート
        unique_urls = list(set(urls))
        def get_eid(url):
            match = re.search(r'eid=(\d+)', url)
            return int(match.group(1)) if match else 0
        unique_urls.sort(key=get_eid)
        
        print(f"📋 {file_path}から{len(unique_urls)}個のURLを抽出しました")
        return unique_urls

    def get_page_content_with_encoding(self, url):
        """複数エンコーディングを試して正しい日本語を取得"""
        encodings = ['euc-jp', 'utf-8', 'shift_jis', 'iso-2022-jp', 'cp932']
        
        for encoding in encodings:
            try:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                # 指定エンコーディングでデコード
                if encoding == 'utf-8':
                    text = response.text
                else:
                    text = response.content.decode(encoding, errors='ignore')
                
                # 日本語の妥当性チェック
                if self.has_valid_japanese(text):
                    print(f"    成功エンコーディング: {encoding}")
                    return text, encoding
                    
            except Exception as e:
                continue
        
        print(f"    ❌ 全エンコーディング失敗")
        return None, None

    def has_valid_japanese(self, text):
        """日本語の妥当性をチェック"""
        if not text:
            return False
        
        # 日本語文字のカウント
        japanese_chars = re.findall(r'[あ-んア-ンー一-龯]', text)
        japanese_count = len(japanese_chars)
        
        # 文字化け文字のチェック
        garbled_patterns = ['�', '�', '縺', '繝', '繧', '繝�']
        has_garbled = any(pattern in text for pattern in garbled_patterns)
        
        return japanese_count > 50 and not has_garbled

    def extract_article_data(self, html_content):
        """記事データを抽出"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # タイトル抽出
        title = ""
        title_selectors = ['h1.title', '.title', 'h1', 'h2.title', '.entry-title']
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                title = title_elem.get_text(strip=True)
                if title and len(title) > 3:
                    break
        
        # 本文抽出
        content = ""
        content_selectors = ['.entry', '.content', '.post-content', '.article-content', 'article']
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                # 不要な要素を除去
                for unwanted in content_elem.select('script, style, .ad, .advertisement'):
                    unwanted.decompose()
                
                content = content_elem.get_text(separator='\n', strip=True)
                if content and len(content) > 100:
                    print(f"    本文抽出: {selector} を使用")
                    break
        
        # 日付抽出
        date = ""
        date_selectors = ['.date', '.post-date', '.published', 'time', '.entry-date']
        for selector in date_selectors:
            date_elem = soup.select_one(selector)
            if date_elem:
                date_text = date_elem.get_text(strip=True)
                # 日付パターンをチェック
                if re.search(r'\d{4}', date_text):
                    date = date_text
                    break
        
        return title, content, date

    def convert_file_to_japanese(self, input_file, output_file):
        """文字化けファイルを日本語版に変換"""
        print(f"\n🚀 {input_file} → {output_file} 変換開始")
        
        # URLを抽出
        urls = self.extract_urls_from_garbled_file(input_file)
        if not urls:
            print("❌ URLが見つかりませんでした")
            return
        
        # 出力ファイルを準備
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# TerminalHill ブログ記事データセット (日本語完全版)\n")
            f.write(f"# 抽出開始: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# エンコーディング: UTF-8\n")
            f.write(f"# 対象記事数: {len(urls)}\n\n")
        
        # 各URLを処理
        for i, url in enumerate(urls, 1):
            print(f"記事取得中 ({i}/{len(urls)})")
            print(f"取得中: {url}")
            
            try:
                # コンテンツ取得
                html_content, encoding = self.get_page_content_with_encoding(url)
                if not html_content:
                    self.fail_count += 1
                    print(f"  ❌ 取得失敗")
                    time.sleep(self.delay)
                    continue
                
                # 記事データ抽出
                title, content, date = self.extract_article_data(html_content)
                
                if not content or len(content) < 100:
                    self.fail_count += 1
                    print(f"  ❌ 本文取得失敗")
                    time.sleep(self.delay)
                    continue
                
                # 文字数カウント
                char_count = len(content)
                self.total_chars += char_count
                self.success_count += 1
                
                print(f"  ✓ タイトル: {title[:50]}{'...' if len(title) > 50 else ''}")
                print(f"  ✓ 本文: {char_count}文字")
                
                # EID抽出
                eid_match = re.search(r'eid=(\d+)', url)
                eid = eid_match.group(1) if eid_match else "unknown"
                
                # ファイルに保存
                with open(output_file, 'a', encoding='utf-8') as f:
                    f.write("=" * 80 + "\n")
                    f.write(f"URL: {url}\n")
                    f.write(f"EID: {eid}\n")
                    f.write(f"タイトル: {title}\n")
                    f.write(f"日付: {date}\n")
                    f.write(f"文字数: {char_count}\n")
                    f.write(f"取得日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("=" * 80 + "\n")
                    f.write(content)
                    f.write("\n\n")
                
                # 進行状況表示
                if i % 50 == 0:
                    success_rate = (self.success_count / i) * 100
                    print(f"📊 進行状況: {i}/{len(urls)} ({i/len(urls)*100:.1f}%)")
                    print(f"✅ 成功率: {success_rate:.1f}%")
                    remaining_time = ((len(urls) - i) * self.delay) / 3600
                    print(f"⏱️ 残り予想時間: {remaining_time:.1f}時間")
                    print("-" * 40)
                
            except Exception as e:
                self.fail_count += 1
                print(f"  ❌ エラー: {e}")
            
            time.sleep(self.delay)
        
        # 最終統計
        total_processed = self.success_count + self.fail_count
        success_rate = (self.success_count / total_processed * 100) if total_processed > 0 else 0
        avg_chars = self.total_chars / self.success_count if self.success_count > 0 else 0
        
        print(f"\n✅ 抽出完了!")
        print(f"📊 最終統計:")
        print(f"   成功記事数: {self.success_count}")
        print(f"   失敗記事数: {self.fail_count}")
        print(f"   成功率: {success_rate:.1f}%")
        print(f"   総文字数: {self.total_chars:,}")
        print(f"   平均文字数: {avg_chars:.0f}")

def main():
    converter = CompleteJapaneseConverter(delay=2)
    
    # 2つのファイルを変換
    files_to_convert = [
        ("terminalhill_sample_1000.txt", "terminalhill_sample_1000_JAPANESE_COMPLETE.txt"),
        ("terminalhill_all_5652_articles.txt", "terminalhill_all_5652_articles_JAPANESE_COMPLETE.txt")
    ]
    
    for input_file, output_file in files_to_convert:
        if Path(input_file).exists():
            converter.convert_file_to_japanese(input_file, output_file)
        else:
            print(f"❌ ファイルが見つかりません: {input_file}")

if __name__ == "__main__":
    main() 