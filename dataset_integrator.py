#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
データセット統合スクリプト
複数のファイルから記事を統合し、重複除去して最終データセットを作成
"""

import re
from datetime import datetime
from collections import defaultdict

def extract_articles_from_file(filename):
    """ファイルから記事を抽出"""
    articles = {}
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 記事の区切りで分割
        sections = content.split('=' * 80)
        
        for section in sections:
            if 'URL: https://terminalhill.jugem.jp' in section:
                # URL抽出
                url_match = re.search(r'URL: (https://terminalhill\.jugem\.jp/\?eid=(\d+))', section)
                if url_match:
                    url = url_match.group(1)
                    eid = int(url_match.group(2))
                    
                    # タイトル抽出
                    title_match = re.search(r'記事 \d+(?:/\d+)?: (.+?)\n', section)
                    title = title_match.group(1) if title_match else "タイトル不明"
                    
                    # 日付抽出
                    date_match = re.search(r'日付: (.+?)\n', section)
                    date = date_match.group(1) if date_match else "日付不明"
                    
                    # 本文抽出（最後の区切り線の後）
                    content_parts = section.split('\n\n')
                    content_text = ""
                    for i, part in enumerate(content_parts):
                        if '=' in part and len(part) > 50:  # 区切り線をスキップ
                            continue
                        if 'URL:' in part or '日付:' in part or '記事' in part[:20]:
                            continue
                        if part.strip():
                            content_text += part + "\n\n"
                    
                    content_text = content_text.strip()
                    
                    if content_text and len(content_text) > 100:  # 100文字以上の記事のみ
                        articles[eid] = {
                            'eid': eid,
                            'url': url,
                            'title': title,
                            'date': date,
                            'content': content_text,
                            'char_count': len(content_text),
                            'source_file': filename
                        }
        
        print(f"✓ {filename}: {len(articles)}記事を抽出")
        return articles
        
    except FileNotFoundError:
        print(f"⚠️ {filename} が見つかりません")
        return {}
    except Exception as e:
        print(f"❌ {filename} の処理中エラー: {e}")
        return {}

def integrate_datasets():
    """データセットを統合"""
    
    print("🔄 データセット統合開始")
    print("=" * 60)
    
    # 統合対象ファイル
    source_files = [
        'terminalhill_clean_all_articles.txt',
        'terminalhill_sample_1000.txt'
    ]
    
    all_articles = {}
    file_stats = {}
    
    # 各ファイルから記事を抽出
    for filename in source_files:
        articles = extract_articles_from_file(filename)
        file_stats[filename] = len(articles)
        
        # 重複チェックして統合
        duplicates = 0
        for eid, article in articles.items():
            if eid in all_articles:
                duplicates += 1
                # より文字数の多い記事を採用
                if article['char_count'] > all_articles[eid]['char_count']:
                    all_articles[eid] = article
            else:
                all_articles[eid] = article
        
        print(f"  重複: {duplicates}記事")
    
    print(f"\n📊 統合結果:")
    print(f"  統合前総数: {sum(file_stats.values())}記事")
    print(f"  重複除去後: {len(all_articles)}記事")
    print(f"  重複数: {sum(file_stats.values()) - len(all_articles)}記事")
    
    # 統計情報
    total_chars = sum(article['char_count'] for article in all_articles.values())
    avg_chars = total_chars / len(all_articles) if all_articles else 0
    
    # EIDでソート
    sorted_articles = sorted(all_articles.values(), key=lambda x: x['eid'])
    
    # 年代分析
    year_stats = defaultdict(int)
    for article in sorted_articles:
        if '201' in article['date'] or '202' in article['date']:
            year = article['date'][:4]
            year_stats[year] += 1
    
    print(f"\n📈 データセット詳細:")
    print(f"  総記事数: {len(all_articles):,}記事")
    print(f"  総文字数: {total_chars:,}文字")
    print(f"  平均文字数: {avg_chars:.0f}文字/記事")
    print(f"  EID範囲: {min(all_articles.keys())} 〜 {max(all_articles.keys())}")
    
    if year_stats:
        print(f"\n📅 年代別記事数:")
        for year in sorted(year_stats.keys()):
            print(f"    {year}年: {year_stats[year]}記事")
    
    # 統合ファイルを作成
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"terminalhill_integrated_dataset_{timestamp}.txt"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        # ヘッダー情報
        f.write("=" * 80 + "\n")
        f.write("TerminalHill.jugem.jp 統合データセット\n")
        f.write(f"作成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"総記事数: {len(all_articles):,}記事\n")
        f.write(f"総文字数: {total_chars:,}文字\n")
        f.write(f"平均文字数: {avg_chars:.0f}文字/記事\n")
        f.write(f"EID範囲: {min(all_articles.keys())} 〜 {max(all_articles.keys())}\n")
        f.write("データ用途: 東京大学修士論文研究\n")
        f.write("=" * 80 + "\n\n")
        
        # 記事データ
        for i, article in enumerate(sorted_articles, 1):
            f.write("=" * 80 + "\n")
            f.write(f"記事 {i}/{len(all_articles)}: {article['title']}\n")
            f.write(f"URL: {article['url']}\n")
            f.write(f"日付: {article['date']}\n")
            f.write(f"文字数: {article['char_count']}\n")
            f.write(f"ソース: {article['source_file']}\n")
            f.write("=" * 80 + "\n\n")
            f.write(article['content'])
            f.write("\n\n")
    
    print(f"\n✅ 統合完了!")
    print(f"📁 出力ファイル: {output_file}")
    print(f"📊 最終データセット:")
    print(f"   記事数: {len(all_articles):,}記事")
    print(f"   文字数: {total_chars:,}文字")
    print(f"   品質: 高品質（重複除去済み）")
    
    return output_file, len(all_articles), total_chars

if __name__ == "__main__":
    print("🚀 TerminalHill データセット統合")
    print("=" * 60)
    
    output_file, article_count, total_chars = integrate_datasets()
    
    print(f"\n🎯 東京大学修士論文研究用データセット完成!")
    print(f"📁 {output_file}")
    print(f"📊 {article_count:,}記事 / {total_chars:,}文字") 