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

class FixedBlogScraper:
    def __init__(self, delay=2):
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ja,ja-JP;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
    def get_article_content(self, url):
        """記事内容を取得（文字化け対策済み）"""
        try:
            print(f"取得中: {url}")
            
            # リクエスト送信
            response = self.session.get(url, timeout=30)
            
            # エンコーディングを正しく設定
            if response.encoding == 'ISO-8859-1':
                # 自動検出されたエンコーディングが正しくない場合
                response.encoding = 'utf-8'
            elif not response.encoding:
                response.encoding = 'utf-8'
            
            print(f"    エンコーディング: {response.encoding}")
            
            if response.status_code != 200:
                print(f"    ❌ HTTP {response.status_code}")
                return None
                
            # HTML解析
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # タイトル取得
            title_elem = soup.find('title')
            title = title_elem.get_text().strip() if title_elem else "タイトル不明"
            
            # メイン記事内容を取得
            content_selectors = [
                '.entry',
                '.article-body',
                '.post-content',
                '.content',
                'article',
                '.main-content'
            ]
            
            content = None
            used_selector = None
            
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    content = elements[0].get_text().strip()
                    used_selector = selector
                    print(f"    本文抽出: {selector} を使用")
                    break
            
            if not content:
                # フォールバック: body全体から取得
                body = soup.find('body')
                if body:
                    content = body.get_text().strip()
                    used_selector = 'body'
                    print(f"    本文抽出: {selector} を使用（フォールバック）")
            
            if not content:
                print("    ❌ 本文が見つかりません")
                return None
            
            # 日付取得の試行
            date = self.extract_date(soup, response.text)
            
            # 長さチェック
            if len(content) < 100:
                print(f"    ⚠️ 短すぎる内容: {len(content)}文字")
                return None
            
            print(f"    ✅ タイトル: {title[:50]}...")
            print(f"    ✅ 本文: {len(content)}文字")
            
            return {
                'url': url,
                'title': title,
                'content': content,
                'date': date,
                'char_count': len(content),
                'selector_used': used_selector
            }
            
        except requests.exceptions.RequestException as e:
            print(f"    ❌ リクエストエラー: {e}")
            return None
        except Exception as e:
            print(f"    ❌ 予期しないエラー: {e}")
            return None
    
    def extract_date(self, soup, html_text):
        """記事の日付を抽出"""
        # 複数のパターンで日付を探索
        date_patterns = [
            r'(\d{4})\.\d{1,2}\.\d{1,2}',  # YYYY.MM.DD
            r'(\d{4})-\d{1,2}-\d{1,2}',   # YYYY-MM-DD
            r'(\d{4})/\d{1,2}/\d{1,2}',   # YYYY/MM/DD
        ]
        
        # HTML内で日付を検索
        for pattern in date_patterns:
            matches = re.findall(pattern, html_text)
            if matches:
                return matches[0] + "年代"
        
        # meta タグから取得を試行
        date_meta = soup.find('meta', {'name': 'date'})
        if date_meta and date_meta.get('content'):
            return date_meta['content']
        
        return "日付不明"
    
    def scrape_url_list(self, url_file, output_file):
        """URLリストからスクレイピング実行"""
        print(f"📋 URLリスト読み込み: {url_file}")
        
        # URLリスト読み込み
        try:
            with open(url_file, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip()]
        except UnicodeDecodeError:
            # UTF-8で読めない場合は別のエンコーディングを試行
            with open(url_file, 'r', encoding='cp932') as f:
                urls = [line.strip() for line in f if line.strip()]
        
        print(f"📊 総URL数: {len(urls)}")
        
        # 結果収集
        results = []
        success_count = 0
        
        for i, url in enumerate(urls, 1):
            print(f"\n記事取得中 ({i}/{len(urls)})")
            
            article_data = self.get_article_content(url)
            
            if article_data:
                results.append(article_data)
                success_count += 1
            
            # 進行状況表示
            if i % 50 == 0:
                success_rate = (success_count / i) * 100
                print(f"📊 進行状況: {i}/{len(urls)} ({i/len(urls)*100:.1f}%)")
                print(f"📈 成功率: {success_count}/{i} ({success_rate:.1f}%)")
                print("-" * 40)
            
            # 遅延
            if i < len(urls):
                time.sleep(self.delay)
        
        # 結果をファイルに保存
        print(f"\n記事データを保存中: {output_file}")
        self.save_results(results, output_file)
        
        # 最終統計
        total_chars = sum(article['char_count'] for article in results)
        avg_chars = total_chars / len(results) if results else 0
        
        print(f"\n✅ 完了: {len(results)}記事を抽出しました")
        print(f"📊 統計情報:")
        print(f"   総文字数: {total_chars:,}")
        print(f"   平均文字数: {avg_chars:.0f}")
        print(f"   成功率: {len(results)}/{len(urls)} ({len(results)/len(urls)*100:.1f}%)")
        
        return results
    
    def save_results(self, results, output_file):
        """結果をファイルに保存（UTF-8エンコーディング）"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                for i, article in enumerate(results, 1):
                    f.write("=" * 80 + "\n")
                    f.write(f"記事 {i}/{len(results)}: {article['title']}\n")
                    f.write(f"URL: {article['url']}\n")
                    f.write(f"日付: {article['date']}\n")
                    f.write(f"文字数: {article['char_count']}\n")
                    f.write("=" * 80 + "\n\n")
                    f.write(article['content'])
                    f.write("\n\n")
            
            print(f"✅ 保存完了: {len(results)}記事を{output_file}に保存しました")
            
            # ファイルサイズ確認
            file_size = Path(output_file).stat().st_size / (1024 * 1024)
            print(f"📏 ファイルサイズ: {file_size:.2f} MB")
            
        except Exception as e:
            print(f"❌ 保存エラー: {e}")

def main():
    parser = argparse.ArgumentParser(description='文字化け対策済みブログスクレイパー')
    parser.add_argument('--url-list', required=True, help='URLリストファイル')
    parser.add_argument('--output', required=True, help='出力ファイル名')
    parser.add_argument('--delay', type=int, default=2, help='リクエスト間隔（秒）')
    parser.add_argument('--sample', type=int, help='サンプル数（指定した場合は先頭N件のみ処理）')
    
    args = parser.parse_args()
    
    # スクレイパー初期化
    scraper = FixedBlogScraper(delay=args.delay)
    
    print(f"🚀 文字化け対策スクレイピング開始")
    print(f"📁 URLリスト: {args.url_list}")
    print(f"📁 出力ファイル: {args.output}")
    print(f"⏱️ 遅延設定: {args.delay}秒")
    
    if args.sample:
        print(f"🔬 サンプルモード: 先頭{args.sample}件のみ処理")
    
    print("=" * 80)
    
    # URLリストを読み込み
    try:
        with open(args.url_list, 'r', encoding='utf-8') as f:
            all_urls = [line.strip() for line in f if line.strip()]
    except UnicodeDecodeError:
        with open(args.url_list, 'r', encoding='cp932') as f:
            all_urls = [line.strip() for line in f if line.strip()]
    
    # サンプルモード処理
    if args.sample:
        all_urls = all_urls[:args.sample]
    
    # 一時URLファイル作成
    temp_url_file = f"temp_urls_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(temp_url_file, 'w', encoding='utf-8') as f:
        for url in all_urls:
            f.write(url + '\n')
    
    try:
        # スクレイピング実行
        results = scraper.scrape_url_list(temp_url_file, args.output)
        
        if results:
            print(f"\n🎉 成功: {len(results)}記事が正常に取得されました")
        else:
            print(f"\n❌ 失敗: 記事を取得できませんでした")
    
    finally:
        # 一時ファイル削除
        Path(temp_url_file).unlink(missing_ok=True)

if __name__ == "__main__":
    main() 