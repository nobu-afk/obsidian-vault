#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TerminalHill 超強力日本語完全抽出システム MEGA版
52,751URLから5,652記事（18年間）を確実に日本語で抽出
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

class MegaJapaneseExtractor:
    def __init__(self, target_articles=5652, delay=0.3, max_retries=3):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.delay = delay
        self.max_retries = max_retries
        self.target_articles = target_articles
        self.success_count = 0
        self.fail_count = 0
        self.total_chars = 0
        self.start_time = datetime.now()
        self.extracted_urls = set()  # 重複防止
        
        # 日本語エンコーディング優先順位（さらに拡張）
        self.encodings = [
            'euc-jp', 'utf-8', 'shift_jis', 'iso-2022-jp', 'cp932',
            'euc-jisx0213', 'shift_jisx0213', 'utf-16', 'utf-32'
        ]
        
        print(f"🎯 目標記事数: {self.target_articles}")
        print(f"⏰ 遅延設定: {self.delay}秒")
        print(f"🔄 最大再試行: {self.max_retries}回")
        print("=" * 80)

    def decode_content(self, content_bytes):
        """多重エンコーディング検出システム"""
        if not content_bytes:
            return None, None
            
        # 優先エンコーディングで試行
        for encoding in self.encodings:
            try:
                decoded = content_bytes.decode(encoding, errors='ignore')
                if self.is_valid_japanese(decoded):
                    return decoded, encoding
            except (UnicodeDecodeError, LookupError):
                continue
        
        # chardetによる自動検出（強化版）
        try:
            detected = chardet.detect(content_bytes)
            if detected and detected.get('confidence', 0) > 0.5:
                encoding = detected.get('encoding')
                if encoding:
                    decoded = content_bytes.decode(encoding, errors='ignore')
                    if self.is_valid_japanese(decoded):
                        return decoded, encoding
        except:
            pass
        
        return None, None

    def is_valid_japanese(self, text):
        """日本語妥当性チェック（厳格版）"""
        if not text or len(text) < 100:
            return False
            
        # 日本語文字の検出
        japanese_chars = re.findall(r'[ひらがなカタカナ漢字ー々〆〤]', text)
        
        if len(japanese_chars) < 50:
            return False
        
        # 文字化けパターンの検出
        garbled_patterns = [
            r'[��]{3,}',  # 連続した文字化け文字
            r'&#\d+;',    # HTML実体参照
            r'%[0-9A-F]{2}',  # URLエンコード
            r'[?]{5,}',   # 連続した?マーク
        ]
        
        for pattern in garbled_patterns:
            if re.search(pattern, text):
                return False
        
        # 日本語文字の比率チェック
        total_chars = len(text)
        japanese_ratio = len(japanese_chars) / total_chars
        
        return japanese_ratio > 0.1  # 10%以上が日本語文字

    def extract_content(self, url):
        """記事コンテンツ抽出（最適化版）"""
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(url, timeout=15)
                if response.status_code != 200:
                    continue
                
                # コンテンツの日本語デコード
                decoded_content, encoding = self.decode_content(response.content)
                if not decoded_content:
                    continue
                
                soup = BeautifulSoup(decoded_content, 'lxml')
                
                # メタデータ抽出
                title = self.extract_title(soup)
                date = self.extract_date(soup)
                content = self.extract_main_content(soup)
                
                if content and len(content) > 200:
                    return {
                        'url': url,
                        'title': title or "タイトル未取得",
                        'date': date or "日付未取得", 
                        'content': content,
                        'encoding': encoding,
                        'char_count': len(content)
                    }
                    
            except Exception as e:
                if attempt == self.max_retries - 1:
                    print(f"  ❌ エラー: {url} - {str(e)}")
                continue
        
        return None

    def extract_title(self, soup):
        """タイトル抽出"""
        # 複数のセレクタで試行
        selectors = [
            'h1.title', 'h1', '.entry-title', '.post-title', 
            'title', '.article-title', '.page-title'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                title = element.get_text(strip=True)
                if title and len(title) > 3:
                    return title[:200]  # 長すぎるタイトルは切り詰め
        
        return None

    def extract_date(self, soup):
        """日付抽出"""
        # 日付パターン
        date_patterns = [
            r'20\d{2}[/\-年]\d{1,2}[/\-月]\d{1,2}',
            r'\d{4}[/\-]\d{1,2}[/\-]\d{1,2}',
        ]
        
        # メタデータから検索
        meta_selectors = [
            '.date', '.entry-date', '.post-date', 
            '.published', 'time', '.timestamp'
        ]
        
        for selector in meta_selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(strip=True)
                for pattern in date_patterns:
                    match = re.search(pattern, text)
                    if match:
                        return match.group()
        
        return None

    def extract_main_content(self, soup):
        """メインコンテンツ抽出（最適化）"""
        # メインコンテンツセレクタ（優先順位順）
        content_selectors = [
            '.entry', '.entry-content', '.post-content',
            '.article-content', '.main-content', 'main',
            '.content', '#content', '.post-body'
        ]
        
        for selector in content_selectors:
            elements = soup.select(selector)
            for element in elements:
                # 不要な要素を除去
                for tag in element.find_all(['script', 'style', 'nav', 'footer', 'aside']):
                    tag.decompose()
                
                text = element.get_text(separator='\n', strip=True)
                if text and len(text) > 200:
                    # テキストクリーニング
                    cleaned_text = self.clean_text(text)
                    if len(cleaned_text) > 200:
                        return cleaned_text
        
        return None

    def clean_text(self, text):
        """テキストクリーニング"""
        # 不要な空白文字の正規化
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # HTMLエンティティのデコード
        html_entities = {
            '&lt;': '<', '&gt;': '>', '&amp;': '&',
            '&quot;': '"', '&#39;': "'", '&nbsp;': ' '
        }
        
        for entity, char in html_entities.items():
            text = text.replace(entity, char)
        
        return text.strip()

    def save_article(self, article_data, output_file):
        """記事データをリアルタイム保存"""
        try:
            with open(output_file, 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*80}\n")
                f.write(f"URL: {article_data['url']}\n")
                f.write(f"タイトル: {article_data['title']}\n")
                f.write(f"日付: {article_data['date']}\n")
                f.write(f"エンコーディング: {article_data['encoding']}\n")
                f.write(f"文字数: {article_data['char_count']}\n")
                f.write(f"抽出時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"{'='*80}\n")
                f.write(f"{article_data['content']}\n")
                f.flush()  # 即座にディスクに書き込み
            return True
        except Exception as e:
            print(f"  ⚠️ 保存エラー: {str(e)}")
            return False

    def print_progress(self, processed, total_urls):
        """進行状況表示"""
        if processed % 50 == 0 or self.success_count % 25 == 0:
            elapsed = (datetime.now() - self.start_time).total_seconds()
            success_rate = (self.success_count / processed * 100) if processed > 0 else 0
            avg_chars = self.total_chars // self.success_count if self.success_count > 0 else 0
            
            # 残り時間予測
            if self.success_count > 0:
                remaining_articles = self.target_articles - self.success_count
                time_per_success = elapsed / self.success_count
                estimated_remaining = (remaining_articles * time_per_success) / 3600  # 時間単位
            else:
                estimated_remaining = 0
            
            print(f"📊 進行状況: {processed}/{total_urls} ({processed/total_urls*100:.1f}%)")
            print(f"✅ 成功記事数: {self.success_count}/{self.target_articles}")
            print(f"📈 成功率: {success_rate:.1f}%")
            print(f"📝 平均文字数: {avg_chars:,}")
            print(f"⏱️ 残り予想時間: {estimated_remaining:.1f}時間")
            print("-" * 40)

    def run_extraction(self, url_file, output_file):
        """メイン抽出処理"""
        print(f"📋 URLファイル読み込み: {url_file}")
        
        try:
            with open(url_file, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip()]
        except Exception as e:
            print(f"❌ URLファイル読み込みエラー: {e}")
            return False
        
        print(f"📊 総URL数: {len(urls):,}")
        print(f"🎯 目標記事数: {self.target_articles}")
        print(f"📁 出力ファイル: {output_file}")
        print("🚀 抽出開始...")
        print("=" * 80)
        
        # 出力ファイル初期化
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"TerminalHill 完全日本語データセット\n")
            f.write(f"抽出開始時刻: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"目標記事数: {self.target_articles}\n")
            f.write(f"総URL数: {len(urls):,}\n")
        
        processed = 0
        
        # URLを効率的に処理（ランダムサンプリング + 順次処理）
        url_batches = [urls[i:i+1000] for i in range(0, len(urls), 1000)]
        
        for batch_idx, batch in enumerate(url_batches):
            print(f"🔄 バッチ {batch_idx + 1}/{len(url_batches)} 処理中...")
            
            # バッチ内でランダム処理
            random.shuffle(batch)
            
            for url in batch:
                if self.success_count >= self.target_articles:
                    print(f"🎯 目標達成! {self.target_articles}記事抽出完了")
                    break
                
                if url in self.extracted_urls:
                    continue
                
                processed += 1
                print(f"記事取得中 ({self.success_count + 1}/{self.target_articles})")
                print(f"取得中: {url}")
                
                article_data = self.extract_content(url)
                
                if article_data:
                    if self.save_article(article_data, output_file):
                        self.success_count += 1
                        self.total_chars += article_data['char_count']
                        self.extracted_urls.add(url)
                        print(f"  ✅ 成功: {article_data['title'][:50]}...")
                        print(f"  📝 文字数: {article_data['char_count']:,}")
                        print(f"  🔤 エンコーディング: {article_data['encoding']}")
                    else:
                        self.fail_count += 1
                        print(f"  ❌ 保存失敗")
                else:
                    self.fail_count += 1
                    print(f"  ❌ 抽出失敗")
                
                self.print_progress(processed, len(urls))
                
                # 遅延
                time.sleep(self.delay + random.uniform(0, 0.2))
            
            if self.success_count >= self.target_articles:
                break
        
        # 最終結果
        elapsed_time = (datetime.now() - self.start_time).total_seconds() / 3600
        avg_chars = self.total_chars // self.success_count if self.success_count > 0 else 0
        
        print("=" * 80)
        print("🎉 抽出完了!")
        print(f"✅ 成功記事数: {self.success_count:,}")
        print(f"❌ 失敗記事数: {self.fail_count:,}")
        print(f"📈 成功率: {self.success_count/(self.success_count + self.fail_count)*100:.1f}%")
        print(f"📝 総文字数: {self.total_chars:,}")
        print(f"📊 平均文字数: {avg_chars:,}")
        print(f"⏱️ 実行時間: {elapsed_time:.2f}時間")
        print(f"📁 出力ファイル: {output_file}")
        
        # 最終統計をファイルに追記
        with open(output_file, 'a', encoding='utf-8') as f:
            f.write(f"\n\n{'='*80}\n")
            f.write(f"抽出完了統計\n")
            f.write(f"={'='*80}\n")
            f.write(f"抽出完了時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"成功記事数: {self.success_count:,}\n")
            f.write(f"失敗記事数: {self.fail_count:,}\n")
            f.write(f"成功率: {self.success_count/(self.success_count + self.fail_count)*100:.1f}%\n")
            f.write(f"総文字数: {self.total_chars:,}\n")
            f.write(f"平均文字数: {avg_chars:,}\n")
            f.write(f"実行時間: {elapsed_time:.2f}時間\n")
        
        return self.success_count >= self.target_articles

def main():
    if len(sys.argv) < 3:
        print("使用法: python mega_japanese_extractor.py <URLファイル> <出力ファイル> [目標記事数]")
        print("例: python mega_japanese_extractor.py enhanced_complete_urls_20250703_145142.txt terminalhill_MEGA_5652_JAPANESE.txt 5652")
        return
    
    url_file = sys.argv[1]
    output_file = sys.argv[2]
    target_articles = int(sys.argv[3]) if len(sys.argv) > 3 else 5652
    
    extractor = MegaJapaneseExtractor(target_articles=target_articles)
    success = extractor.run_extraction(url_file, output_file)
    
    if success:
        print(f"🎊 完全成功! {target_articles}記事の日本語データセットが完成しました!")
    else:
        print(f"⚠️ 部分成功: {extractor.success_count}記事を抽出しました")

if __name__ == "__main__":
    main() 