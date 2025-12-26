#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TerminalHill 超強力日本語完全抽出システム
52,751記事から5,652記事（18年間）を日本語で完全出力
"""

import requests
import re
import time
import chardet
from bs4 import BeautifulSoup
from datetime import datetime
import argparse
import os
import sys

class UltraJapaneseExtractor:
    def __init__(self, delay=1, max_retries=3, batch_size=100):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.delay = delay
        self.max_retries = max_retries
        self.batch_size = batch_size
        self.success_count = 0
        self.fail_count = 0
        self.total_chars = 0
        self.start_time = datetime.now()
        
        # 日本語エンコーディング優先順位
        self.encodings = ['euc-jp', 'utf-8', 'shift_jis', 'iso-2022-jp', 'cp932']
        
    def detect_japanese_encoding(self, content_bytes):
        """多重エンコーディング検出で最適な日本語エンコーディングを特定"""
        # 各エンコーディングを試行
        for encoding in self.encodings:
            try:
                decoded = content_bytes.decode(encoding, errors='ignore')
                if self.is_valid_japanese(decoded):
                    return decoded, encoding
            except:
                continue
        
        # chardetによる自動検出
        try:
            detected = chardet.detect(content_bytes)
            if detected and detected.get('confidence', 0) > 0.7:
                encoding = detected.get('encoding')
                if encoding:
                    decoded = content_bytes.decode(encoding, errors='ignore')
                    if self.is_valid_japanese(decoded):
                        return decoded, encoding
        except:
            pass
        
        # UTF-8でフォールバック
        try:
            decoded = content_bytes.decode('utf-8', errors='ignore')
            return decoded, 'utf-8'
        except:
            return content_bytes.decode('utf-8', errors='replace'), 'utf-8'
    
    def is_valid_japanese(self, text):
        """日本語テキストの妥当性チェック"""
        if len(text) < 50:
            return False
        
        # 日本語文字の割合をチェック
        japanese_chars = len(re.findall(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]', text))
        total_chars = len(text)
        
        if total_chars == 0:
            return False
        
        japanese_ratio = japanese_chars / total_chars
        
        # 文字化けパターンをチェック
        garbled_patterns = [
            r'縺�', r'縺�', r'縺�', r'繧�', r'繝�',
            r'�', r'��', r'???', r'��',
            r'[?]{3,}', r'[�]{3,}'
        ]
        
        for pattern in garbled_patterns:
            if re.search(pattern, text):
                return False
        
        return japanese_ratio > 0.1
    
    def extract_article_content(self, html_content):
        """記事内容を抽出"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # タイトル抽出
        title = ""
        title_selectors = ['title', 'h1', '.entry-title', '.post-title']
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                title = title_elem.get_text().strip()
                break
        
        # 本文抽出
        content = ""
        content_selectors = ['.entry', '.post-content', '.article-content', '.main-content', 'article']
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                # スクリプトやスタイルを除去
                for elem in content_elem.find_all(['script', 'style', 'nav', 'footer', 'header']):
                    elem.decompose()
                content = content_elem.get_text().strip()
                break
        
        # 日付抽出
        date = ""
        date_patterns = [
            r'(\d{4})\.(\d{1,2})\.(\d{1,2})',
            r'(\d{4})/(\d{1,2})/(\d{1,2})',
            r'(\d{4})-(\d{1,2})-(\d{1,2})'
        ]
        for pattern in date_patterns:
            match = re.search(pattern, html_content)
            if match:
                date = f"{match.group(1)}-{match.group(2).zfill(2)}-{match.group(3).zfill(2)}"
                break
        
        return title, content, date
    
    def extract_single_article(self, url):
        """単一記事の抽出"""
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(url, timeout=30)
                
                if response.status_code == 200:
                    # 日本語エンコーディング検出
                    html_content, encoding = self.detect_japanese_encoding(response.content)
                    
                    if self.is_valid_japanese(html_content):
                        title, content, date = self.extract_article_content(html_content)
                        
                        if content and len(content) > 100:
                            eid_match = re.search(r'eid=(\d+)', url)
                            eid = eid_match.group(1) if eid_match else "unknown"
                            
                            return {
                                'url': url,
                                'eid': eid,
                                'title': title,
                                'content': content,
                                'date': date,
                                'encoding': encoding,
                                'char_count': len(content),
                                'success': True
                            }
                
                time.sleep(self.delay)
                
            except Exception as e:
                if attempt == self.max_retries - 1:
                    return {
                        'url': url,
                        'error': str(e),
                        'success': False
                    }
                time.sleep(self.delay * 2)
        
        return {'url': url, 'success': False}
    
    def save_batch(self, articles, output_file, is_first_batch=False):
        """バッチ保存"""
        mode = 'w' if is_first_batch else 'a'
        
        with open(output_file, mode, encoding='utf-8') as f:
            if is_first_batch:
                f.write("# TerminalHill ブログ記事データセット (日本語完全版)\n")
                f.write(f"# 抽出開始: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("# エンコーディング: UTF-8\n")
                f.write(f"# 抽出システム: Ultra Japanese Extractor\n\n")
            
            for article in articles:
                if article.get('success'):
                    f.write("=" * 80 + "\n")
                    f.write(f"URL: {article['url']}\n")
                    f.write(f"EID: {article['eid']}\n")
                    f.write(f"タイトル: {article['title']}\n")
                    f.write(f"日付: {article['date']}\n")
                    f.write(f"エンコーディング: {article['encoding']}\n")
                    f.write(f"文字数: {article['char_count']}\n")
                    f.write(f"取得日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("=" * 80 + "\n")
                    f.write(article['content'])
                    f.write("\n\n")
    
    def extract_all_articles(self, url_file, output_file, target_count=5652):
        """全記事抽出メイン処理"""
        print(f"🚀 TerminalHill 超強力日本語完全抽出開始!")
        print(f"📁 URLファイル: {url_file}")
        print(f"📁 出力ファイル: {output_file}")
        print(f"🎯 目標記事数: {target_count}")
        print("=" * 80)
        
        # URLリスト読み込み
        try:
            with open(url_file, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"❌ エラー: {url_file} が見つかりません")
            return
        
        print(f"📋 読み込み完了: {len(urls)}個のURL")
        
        # バッチ処理
        current_batch = []
        processed = 0
        is_first_batch = True
        
        for i, url in enumerate(urls):
            if self.success_count >= target_count:
                print(f"\n🎯 目標記事数 {target_count} に到達しました！")
                break
            
            print(f"\n記事取得中 ({processed + 1}/{len(urls)})")
            print(f"取得中: {url}")
            
            article = self.extract_single_article(url)
            
            if article.get('success'):
                print(f"  ✅ 成功エンコーディング: {article['encoding']}")
                print(f"  ✓ タイトル: {article['title'][:50]}...")
                print(f"  ✓ 本文: {article['char_count']}文字")
                
                current_batch.append(article)
                self.success_count += 1
                self.total_chars += article['char_count']
            else:
                print(f"  ❌ 取得失敗")
                self.fail_count += 1
            
            processed += 1
            
            # バッチ保存
            if len(current_batch) >= self.batch_size or processed % 500 == 0:
                if current_batch:
                    self.save_batch(current_batch, output_file, is_first_batch)
                    current_batch = []
                    is_first_batch = False
                
                # 進行状況表示
                if processed % 100 == 0:
                    elapsed = datetime.now() - self.start_time
                    success_rate = (self.success_count / processed) * 100 if processed > 0 else 0
                    
                    print(f"\n📊 進行状況: {processed}/{len(urls)} ({(processed/len(urls)*100):.1f}%)")
                    print(f"✅ 成功率: {success_rate:.1f}%")
                    print(f"📄 抽出記事数: {self.success_count}")
                    print(f"📊 総文字数: {self.total_chars:,}")
                    print(f"⏱️ 経過時間: {elapsed}")
                    print("-" * 40)
        
        # 最終バッチ保存
        if current_batch:
            self.save_batch(current_batch, output_file, is_first_batch)
        
        # 最終統計
        elapsed = datetime.now() - self.start_time
        print(f"\n✅ 抽出完了!")
        print(f"📊 最終統計:")
        print(f"   成功記事数: {self.success_count}")
        print(f"   失敗記事数: {self.fail_count}")
        print(f"   成功率: {(self.success_count/(self.success_count+self.fail_count)*100):.1f}%")
        print(f"   総文字数: {self.total_chars:,}")
        print(f"   平均文字数: {self.total_chars//self.success_count if self.success_count > 0 else 0}")
        print(f"   実行時間: {elapsed}")
        
        return self.success_count

def main():
    parser = argparse.ArgumentParser(description='TerminalHill 超強力日本語完全抽出システム')
    parser.add_argument('--url-file', required=True, help='URLリストファイル')
    parser.add_argument('--output', default='terminalhill_ULTRA_JAPANESE_COMPLETE.txt', help='出力ファイル名')
    parser.add_argument('--delay', type=float, default=1.0, help='リクエスト間隔（秒）')
    parser.add_argument('--target', type=int, default=5652, help='目標記事数')
    parser.add_argument('--batch-size', type=int, default=100, help='バッチサイズ')
    
    args = parser.parse_args()
    
    extractor = UltraJapaneseExtractor(
        delay=args.delay,
        batch_size=args.batch_size
    )
    
    result_count = extractor.extract_all_articles(
        args.url_file,
        args.output,
        args.target
    )
    
    print(f"\n🎉 完了: {result_count}記事を抽出しました!")

if __name__ == "__main__":
    main() 