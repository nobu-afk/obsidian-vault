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

class JapaneseBlogScraper:
    def __init__(self, delay=2):
        self.delay = delay
        self.session = requests.Session()
        
        # 日本語対応のヘッダー設定
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'ja,ja-JP;q=0.9,en;q=0.8',
            'Accept-Charset': 'utf-8,shift_jis,euc-jp,iso-2022-jp',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        })
        
        self.success_count = 0
        self.failure_count = 0
        self.total_chars = 0

    def detect_and_decode_content(self, response):
        """レスポンスのエンコーディングを検出して正しくデコード"""
        # 複数のエンコーディングを試行
        encodings = ['utf-8', 'shift_jis', 'euc-jp', 'iso-2022-jp', 'cp932']
        
        # レスポンスのエンコーディング情報を確認
        declared_encoding = response.encoding
        if declared_encoding:
            encodings.insert(0, declared_encoding)
            
        # Content-Typeヘッダーからcharsetを抽出
        content_type = response.headers.get('content-type', '')
        charset_match = re.search(r'charset=([^;]+)', content_type)
        if charset_match:
            charset = charset_match.group(1).strip()
            if charset not in encodings:
                encodings.insert(0, charset)
        
        # 各エンコーディングを試行
        for encoding in encodings:
            try:
                response.encoding = encoding
                text = response.text
                # 文字化けチェック - 基本的な日本語文字が含まれているか
                if self.has_valid_japanese(text):
                    print(f"    成功エンコーディング: {encoding}")
                    return text
            except (UnicodeDecodeError, UnicodeError):
                continue
                
        # すべて失敗した場合は元のテキストを返す
        print(f"    ⚠️ エンコーディング検出失敗、原文のまま使用")
        return response.text

    def has_valid_japanese(self, text):
        """テキストに有効な日本語が含まれているかチェック"""
        # ひらがな、カタカナ、漢字の存在をチェック
        hiragana = re.search(r'[あ-ん]', text)
        katakana = re.search(r'[ア-ン]', text)
        kanji = re.search(r'[一-龯]', text)
        
        # 文字化けパターンをチェック
        garbled_patterns = ['��', '縺', '�']
        has_garbled = any(pattern in text for pattern in garbled_patterns)
        
        # 日本語が含まれており、文字化けが少ない場合はTrue
        japanese_count = len(re.findall(r'[あ-んア-ン一-龯]', text))
        return japanese_count > 10 and not has_garbled

    def extract_article_content(self, url):
        """記事のコンテンツを抽出"""
        try:
            print(f"取得中: {url}")
            
            # リクエスト実行
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # エンコーディング検出とデコード
            html_content = self.detect_and_decode_content(response)
            
            # BeautifulSoupでパース
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # メタデータを抽出
            article_data = {
                'url': url,
                'title': '',
                'content': '',
                'date': '',
                'char_count': 0
            }
            
            # タイトル抽出（複数のセレクタを試行）
            title_selectors = [
                'h1.title',
                '.entry-title',
                'h1',
                'title',
                '.post-title',
                '.article-title'
            ]
            
            for selector in title_selectors:
                title_element = soup.select_one(selector)
                if title_element:
                    title_text = title_element.get_text(strip=True)
                    if title_text and self.has_valid_japanese(title_text):
                        article_data['title'] = title_text
                        print(f"  ✓ タイトル: {title_text[:50]}...")
                        break
            
            # 本文抽出（複数のセレクタを試行）
            content_selectors = [
                '.entry',
                '.post-content',
                '.article-content',
                '.content',
                'article',
                '.main-content'
            ]
            
            for selector in content_selectors:
                content_element = soup.select_one(selector)
                if content_element:
                    # 不要な要素を除去
                    for unwanted in content_element.select('script, style, .ad, .advertisement, nav, footer, header'):
                        unwanted.decompose()
                    
                    content_text = content_element.get_text(separator='\n', strip=True)
                    if content_text and len(content_text) > 100:
                        article_data['content'] = content_text
                        article_data['char_count'] = len(content_text)
                        print(f"  ✓ 本文: {len(content_text)}文字")
                        print(f"    本文抽出: {selector} を使用")
                        break
            
            # 日付抽出
            date_selectors = [
                '.entry-date',
                '.post-date',
                '.date',
                'time'
            ]
            
            for selector in date_selectors:
                date_element = soup.select_one(selector)
                if date_element:
                    date_text = date_element.get_text(strip=True)
                    if date_text:
                        article_data['date'] = date_text
                        break
            
            # EIDをURLから抽出
            eid_match = re.search(r'eid=(\d+)', url)
            if eid_match:
                article_data['eid'] = eid_match.group(1)
            
            # 成功判定
            if article_data['content'] and len(article_data['content']) > 100:
                self.success_count += 1
                self.total_chars += article_data['char_count']
                return article_data
            else:
                print(f"  ❌ 本文が短すぎるか取得できませんでした")
                self.failure_count += 1
                return None
                
        except Exception as e:
            print(f"  ❌ エラー: {url} - {str(e)}")
            self.failure_count += 1
            return None

    def save_article_data(self, article_data, output_file):
        """記事データをファイルに保存"""
        separator = "=" * 80
        
        # UTF-8で明示的に書き込み
        with open(output_file, 'a', encoding='utf-8', newline='\n') as f:
            f.write(f"{separator}\n")
            f.write(f"URL: {article_data['url']}\n")
            f.write(f"EID: {article_data.get('eid', 'N/A')}\n")
            f.write(f"タイトル: {article_data['title']}\n")
            f.write(f"日付: {article_data['date']}\n")
            f.write(f"文字数: {article_data['char_count']}\n")
            f.write(f"取得日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{separator}\n")
            f.write(f"{article_data['content']}\n")
            f.write(f"\n")

    def scrape_articles(self, url_list, output_file, sample_size=None):
        """複数記事のスクレイピング実行"""
        print(f"🚀 日本語対応記事抽出開始: {len(url_list)}記事")
        print(f"📁 出力ファイル: {output_file}")
        print(f"⏱️ 遅延設定: {self.delay}秒")
        print("=" * 80)
        
        # 出力ファイルを初期化（UTF-8でBOM無し）
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# TerminalHill ブログ記事データセット\n")
            f.write(f"# 抽出開始: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# エンコーディング: UTF-8\n")
            f.write(f"# 対象記事数: {len(url_list)}\n\n")
        
        # サンプルサイズの制限
        if sample_size and sample_size < len(url_list):
            url_list = url_list[:sample_size]
            print(f"🎯 サンプル制限: {sample_size}記事")
        
        start_time = time.time()
        
        for i, url in enumerate(url_list, 1):
            print(f"記事取得中 ({i}/{len(url_list)})")
            
            # 記事データを抽出
            article_data = self.extract_article_content(url)
            
            if article_data:
                # ファイルに保存
                self.save_article_data(article_data, output_file)
            
            # 進行状況表示
            if i % 50 == 0:
                success_rate = (self.success_count / i) * 100
                elapsed_time = time.time() - start_time
                remaining_time = (elapsed_time / i) * (len(url_list) - i) / 3600
                
                print(f"📊 進行状況: {i}/{len(url_list)} ({i/len(url_list)*100:.1f}%)")
                print(f"✅ 成功率: {success_rate:.1f}%")
                print(f"⏱️ 残り予想時間: {remaining_time:.1f}時間")
                print("-" * 40)
            
            # レート制限
            if i < len(url_list):
                time.sleep(self.delay)
        
        # 最終統計
        total_time = (time.time() - start_time) / 3600
        success_rate = (self.success_count / len(url_list)) * 100
        avg_chars = self.total_chars / max(self.success_count, 1)
        
        print(f"\n✅ 抽出完了!")
        print(f"📊 最終統計:")
        print(f"   成功記事数: {self.success_count}")
        print(f"   失敗記事数: {self.failure_count}")
        print(f"   成功率: {success_rate:.1f}%")
        print(f"   総文字数: {self.total_chars:,}")
        print(f"   平均文字数: {avg_chars:.0f}")
        print(f"   実行時間: {total_time:.1f}時間")

def main():
    parser = argparse.ArgumentParser(description='日本語対応ブログスクレイパー')
    parser.add_argument('--url-list', required=True, help='URLリストファイル')
    parser.add_argument('--output', required=True, help='出力ファイル名')
    parser.add_argument('--delay', type=int, default=2, help='リクエスト間隔（秒）')
    parser.add_argument('--sample', type=int, help='サンプル記事数（制限用）')
    
    args = parser.parse_args()
    
    # URLリストを読み込み
    try:
        with open(args.url_list, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip()]
        print(f"📋 読み込み完了: {len(urls)}個の記事URL")
    except Exception as e:
        print(f"❌ URLリスト読み込みエラー: {e}")
        return
    
    if not urls:
        print("❌ 記事URLが見つかりませんでした")
        return
    
    # スクレイピング実行
    scraper = JapaneseBlogScraper(delay=args.delay)
    scraper.scrape_articles(urls, args.output, args.sample)

if __name__ == "__main__":
    main() 