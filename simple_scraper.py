#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
シンプル記事抽出スクリプト
1行に1URLのシンプルなファイル形式対応
"""

import requests
from bs4 import BeautifulSoup
import time
import re
from datetime import datetime
import argparse

def load_simple_urls(filename):
    """シンプルなURLリストファイルから記事URLを読み込み"""
    urls = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and line.startswith('http'):
                    urls.append(line)
                    
        print(f"📋 読み込み完了: {len(urls)}個の記事URL")
        return urls
    except Exception as e:
        print(f"❌ エラー: URLリストの読み込みに失敗 - {e}")
        return []

def extract_article_content(url, session):
    """記事の内容を抽出"""
    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # タイトル抽出
        title_element = soup.find('title')
        title = title_element.get_text().strip() if title_element else "タイトルなし"
        
        # 記事本文抽出（JUGEMの記事構造に基づく）
        content = ""
        
        # メインコンテンツを探す
        entry_selectors = [
            '.entry',
            '.entry-content', 
            '.post-content',
            '#main .entry',
            '.article-body'
        ]
        
        for selector in entry_selectors:
            entry = soup.select_one(selector)
            if entry:
                print(f"    本文抽出: {selector} を使用")
                # HTMLタグを除去してテキストのみ抽出
                content = entry.get_text(separator='\n', strip=True)
                break
        
        # フォールバック: メインコンテンツが見つからない場合
        if not content:
            main_content = soup.find('body')
            if main_content:
                content = main_content.get_text(separator='\n', strip=True)
                print("    本文抽出: body全体を使用")
        
        # 日付抽出
        date_text = "日付不明"
        date_patterns = [
            r'(\d{4})\.(\d{1,2})\.(\d{1,2})',
            r'(\d{4})/(\d{1,2})/(\d{1,2})',
            r'(\d{4})-(\d{1,2})-(\d{1,2})'
        ]
        
        page_text = soup.get_text()
        for pattern in date_patterns:
            matches = re.findall(pattern, page_text)
            if matches:
                year, month, day = matches[0]
                date_text = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                break
        
        return {
            'title': title,
            'content': content,
            'date': date_text,
            'char_count': len(content)
        }
        
    except Exception as e:
        print(f"  ❌ エラー: {url} - {e}")
        return None

def simple_scrape(url_list_file, output_file, delay=2, start_from=0):
    """シンプルな記事抽出を実行"""
    
    # 記事URLリストを読み込み
    urls = load_simple_urls(url_list_file)
    if not urls:
        print("❌ 記事URLが見つかりませんでした")
        return
    
    # 開始位置を調整
    if start_from > 0:
        urls = urls[start_from:]
        print(f"📍 {start_from}番目から再開します")
    
    total_urls = len(urls)
    
    # セッション設定
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })
    
    print(f"🚀 シンプル記事抽出開始: {total_urls}記事")
    print(f"📁 出力ファイル: {output_file}")
    print(f"⏱️ 遅延設定: {delay}秒")
    print("=" * 80)
    
    extracted_articles = []
    failed_count = 0
    start_time = time.time()
    
    for i, url in enumerate(urls, 1):
        print(f"記事取得中 ({i}/{total_urls})")
        print(f"取得中: {url}")
        
        # 記事内容を抽出
        article = extract_article_content(url, session)
        
        if article and article['char_count'] > 100:  # 100文字以上の記事のみ
            article['url'] = url
            article['index'] = start_from + i
            extracted_articles.append(article)
            
            print(f"  ✓ タイトル: {article['title'][:50]}...")
            print(f"  ✓ 本文: {article['char_count']}文字")
        else:
            failed_count += 1
            print(f"  ❌ 取得失敗")
        
        # 進行状況表示
        if i % 50 == 0:
            elapsed = time.time() - start_time
            rate = i / elapsed if elapsed > 0 else 0
            remaining = (total_urls - i) / rate if rate > 0 else 0
            print(f"\n📊 進行状況: {i}/{total_urls} ({i/total_urls*100:.1f}%)")
            print(f"⏱️ 残り予想時間: {remaining/3600:.1f}時間")
            print("-" * 40)
        
        # 遅延
        time.sleep(delay)
    
    # 結果をファイルに保存
    print(f"\n記事データを保存中: {output_file}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for article in extracted_articles:
            f.write("=" * 80 + "\n")
            f.write(f"記事 {article['index']}: {article['title']}\n")
            f.write(f"URL: {article['url']}\n")
            f.write(f"日付: {article['date']}\n")
            f.write("=" * 80 + "\n\n")
            f.write(article['content'])
            f.write("\n\n")
    
    # 統計情報
    total_chars = sum(article['char_count'] for article in extracted_articles)
    avg_chars = total_chars / len(extracted_articles) if extracted_articles else 0
    
    print(f"✓ 保存完了: {len(extracted_articles)}記事を{output_file}に保存しました")
    print(f"✅ 完了: {len(extracted_articles)}記事を抽出しました")
    print(f"📊 統計情報:")
    print(f"   総文字数: {total_chars:,}")
    print(f"   平均文字数: {avg_chars:.0f}")
    print(f"   成功率: {len(extracted_articles)}/{total_urls} ({len(extracted_articles)/total_urls*100:.1f}%)")
    print(f"   失敗件数: {failed_count}")
    
    elapsed_total = time.time() - start_time
    print(f"   実行時間: {elapsed_total/60:.1f}分")

def main():
    parser = argparse.ArgumentParser(description='シンプル記事抽出スクリプト')
    parser.add_argument('--url-list', required=True, help='記事URLリストファイル')
    parser.add_argument('--output', required=True, help='出力ファイル名')
    parser.add_argument('--delay', type=int, default=2, help='リクエスト間の遅延（秒）')
    parser.add_argument('--start-from', type=int, default=0, help='開始位置（0から開始）')
    
    args = parser.parse_args()
    
    simple_scrape(args.url_list, args.output, args.delay, args.start_from)

if __name__ == "__main__":
    main() 