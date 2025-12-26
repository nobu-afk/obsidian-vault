#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TerminalHill 知的5,652記事抽出システム
既存成功データを基に効率的に5,652記事目標達成
"""

import requests
import re
import time
import chardet
from bs4 import BeautifulSoup
from datetime import datetime
import os
import sys
import random

class Intelligent5652Extractor:
    def __init__(self, target_articles=5652, delay=0.3):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.delay = delay
        self.target_articles = target_articles
        self.success_count = 0
        self.fail_count = 0
        self.total_chars = 0
        self.start_time = datetime.now()
        
        # 日本語エンコーディング優先順位
        self.encodings = ['euc-jp', 'utf-8', 'shift_jis', 'iso-2022-jp', 'cp932']
        
        # 既存成功URLの収集
        self.existing_urls = set()
        self.collected_articles = []
        
    def load_existing_data(self):
        """既存の成功記事データを読み込み"""
        existing_files = [
            'terminalhill_japanese_COMPLETE.txt',
            'terminalhill_sample_1000_JAPANESE_COMPLETE.txt', 
            'terminalhill_all_5652_articles_JAPANESE_COMPLETE.txt'
        ]
        
        print("📁 既存データ読み込み中...")
        for filename in existing_files:
            if os.path.exists(filename):
                print(f"  ✓ {filename} を読み込み")
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.collected_articles.append(content)
                    
                    # URL抽出
                    urls = re.findall(r'URL: (https://terminalhill\.jugem\.jp/\?eid=\d+)', content)
                    self.existing_urls.update(urls)
        
        print(f"📊 既存記事数: {len(self.existing_urls)}")
        return len(self.existing_urls)
    
    def generate_smart_urls(self, base_count):
        """既存データを分析して効率的なURL範囲を生成"""
        print("🧠 スマートURL生成中...")
        
        # 既存URLからEID抽出
        existing_eids = set()
        for url in self.existing_urls:
            match = re.search(r'eid=(\d+)', url)
            if match:
                existing_eids.add(int(match.group(1)))
        
        if existing_eids:
            min_eid = min(existing_eids)
            max_eid = max(existing_eids)
            print(f"📈 既存EID範囲: {min_eid} - {max_eid}")
        else:
            min_eid, max_eid = 1000, 52887
        
        # 効率的URL生成戦略
        smart_urls = []
        
        # 戦略1: 既存成功範囲の隙間を埋める
        for eid in range(max(1000, min_eid), min(max_eid + 1000, 52887)):
            url = f"https://terminalhill.jugem.jp/?eid={eid}"
            if url not in self.existing_urls:
                smart_urls.append(url)
        
        # 戦略2: 高確率成功範囲の探索
        high_prob_ranges = [
            (1500, 7000),   # 初期ブログ期間
            (15000, 35000), # 活発期間
            (40000, 52887)  # 最新期間
        ]
        
        for start, end in high_prob_ranges:
            for eid in range(start, end, 10):  # 10間隔でサンプリング
                url = f"https://terminalhill.jugem.jp/?eid={eid}"
                if url not in self.existing_urls:
                    smart_urls.append(url)
        
        print(f"🎯 生成URL数: {len(smart_urls)}")
        return smart_urls[:20000]  # 上限設定
    
    def detect_encoding_and_extract(self, content_bytes):
        """多重エンコーディング検出と日本語抽出"""
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
        
        return None, None
    
    def is_valid_japanese(self, text):
        """日本語妥当性チェック"""
        if len(text) < 100:
            return False
        
        # 日本語文字の比率チェック
        japanese_chars = len(re.findall(r'[ひらがなカタカナ漢字]', text))
        if japanese_chars < 50:
            return False
        
        # 文字化けパターンのチェック
        garbled_patterns = [
            r'[������]+',
            r'縺[ぁ-ん]{2,}',
            r'[ﾂ?]{3,}',
            r'[＠ＡＢＣ]{3,}'
        ]
        
        for pattern in garbled_patterns:
            if re.search(pattern, text):
                return False
        
        return True
    
    def extract_article_content(self, html_content):
        """記事コンテンツの抽出"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # タイトル抽出
        title = ""
        title_selectors = ['h1.entry-title', '.entry-title', 'h1', 'title']
        for selector in title_selectors:
            element = soup.select_one(selector)
            if element:
                title = element.get_text().strip()
                if title and '★役立つ仕事術★' not in title:
                    break
        
        # 本文抽出
        content = ""
        content_selectors = ['.entry', '.entry-content', '.post-content', 'article', '.main-content']
        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                content = element.get_text().strip()
                if len(content) > 100:
                    break
        
        return title, content
    
    def fetch_article(self, url):
        """単一記事の取得"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # エンコーディング検出と変換
            decoded_content, encoding = self.detect_encoding_and_extract(response.content)
            if not decoded_content:
                return None
            
            # 記事内容抽出
            title, content = self.extract_article_content(decoded_content)
            
            if len(content) < 100:
                return None
            
            return {
                'url': url,
                'title': title,
                'content': content,
                'encoding': encoding,
                'char_count': len(content)
            }
            
        except Exception as e:
            return None
    
    def save_progress(self, articles, output_file):
        """進行状況の保存"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("TerminalHill 5,652記事完全データセット\n")
            f.write(f"抽出完了時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"総記事数: {len(articles)}\n")
            f.write(f"総文字数: {sum(a['char_count'] for a in articles)}\n")
            f.write("=" * 80 + "\n\n")
            
            for i, article in enumerate(articles, 1):
                f.write(f"記事 {i}\n")
                f.write(f"URL: {article['url']}\n")
                f.write(f"タイトル: {article['title']}\n")
                f.write(f"エンコーディング: {article['encoding']}\n")
                f.write(f"文字数: {article['char_count']}\n")
                f.write("-" * 40 + "\n")
                f.write(article['content'])
                f.write("\n" + "=" * 80 + "\n\n")
    
    def extract_to_target(self, output_file):
        """目標記事数まで抽出実行"""
        print(f"🎯 目標: {self.target_articles}記事")
        
        # 既存データ読み込み
        existing_count = self.load_existing_data()
        
        if existing_count >= self.target_articles:
            print(f"✅ 既に目標達成! 現在: {existing_count}記事")
            return existing_count
        
        needed = self.target_articles - existing_count
        print(f"📊 追加必要記事数: {needed}")
        
        # スマートURL生成
        smart_urls = self.generate_smart_urls(existing_count)
        
        print(f"🚀 追加抽出開始...")
        successful_articles = []
        
        for i, url in enumerate(smart_urls):
            if len(successful_articles) >= needed:
                break
            
            if url in self.existing_urls:
                continue
            
            print(f"記事取得中 ({len(successful_articles)+1}/{needed})")
            print(f"取得中: {url}")
            
            article = self.fetch_article(url)
            if article:
                successful_articles.append(article)
                self.success_count += 1
                self.total_chars += article['char_count']
                print(f"  ✓ 成功: {article['title'][:50]}...")
                print(f"  ✓ 文字数: {article['char_count']}")
            else:
                self.fail_count += 1
                print("  ❌ 失敗")
            
            # 進行状況表示
            if (i + 1) % 50 == 0:
                total_found = existing_count + len(successful_articles)
                progress = (total_found / self.target_articles) * 100
                print(f"📊 進行状況: {total_found}/{self.target_articles} ({progress:.1f}%)")
                print(f"✅ 成功率: {self.success_count/(self.success_count + self.fail_count)*100:.1f}%")
                print("-" * 60)
            
            time.sleep(self.delay)
        
        # 結果保存
        if successful_articles:
            # 既存データと新規データを統合
            all_articles = []
            
            # 既存データから記事を復元
            for content in self.collected_articles:
                articles = self.parse_existing_content(content)
                all_articles.extend(articles)
            
            # 新規記事追加
            all_articles.extend(successful_articles)
            
            # 重複除去
            unique_articles = self.remove_duplicates(all_articles)
            
            self.save_progress(unique_articles, output_file)
            
            final_count = len(unique_articles)
            print(f"\n✅ 抽出完了!")
            print(f"📊 最終記事数: {final_count}")
            print(f"🎯 目標達成率: {(final_count/self.target_articles)*100:.1f}%")
            print(f"📁 出力ファイル: {output_file}")
            
            return final_count
        else:
            print("❌ 新規記事の抽出に失敗しました")
            return existing_count
    
    def parse_existing_content(self, content):
        """既存コンテンツから記事データを復元"""
        articles = []
        article_blocks = re.split(r'={80,}', content)
        
        for block in article_blocks:
            if 'URL:' in block and 'タイトル:' in block:
                url_match = re.search(r'URL: (https://[^\n]+)', block)
                title_match = re.search(r'タイトル: ([^\n]+)', block)
                
                if url_match and title_match:
                    # 本文抽出（簡易版）
                    lines = block.split('\n')
                    content_lines = []
                    in_content = False
                    
                    for line in lines:
                        if line.startswith('-' * 40):
                            in_content = True
                            continue
                        elif in_content:
                            content_lines.append(line)
                    
                    content_text = '\n'.join(content_lines).strip()
                    
                    if len(content_text) > 100:
                        articles.append({
                            'url': url_match.group(1),
                            'title': title_match.group(1),
                            'content': content_text,
                            'encoding': 'utf-8',
                            'char_count': len(content_text)
                        })
        
        return articles
    
    def remove_duplicates(self, articles):
        """重複記事の除去"""
        seen_urls = set()
        unique_articles = []
        
        for article in articles:
            if article['url'] not in seen_urls:
                seen_urls.add(article['url'])
                unique_articles.append(article)
        
        return unique_articles

def main():
    if len(sys.argv) != 2:
        print("使用法: python intelligent_5652_extractor.py <出力ファイル名>")
        sys.exit(1)
    
    output_file = sys.argv[1]
    
    extractor = Intelligent5652Extractor(target_articles=5652, delay=0.3)
    final_count = extractor.extract_to_target(output_file)
    
    if final_count >= 5652:
        print(f"🎉 5,652記事目標達成! 最終記事数: {final_count}")
    else:
        print(f"📊 現在の記事数: {final_count} (目標の{(final_count/5652)*100:.1f}%)")

if __name__ == "__main__":
    main() 