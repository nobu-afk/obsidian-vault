#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Part16-18 再分割スクリプト v2
500,000文字以内で正確に分割（ヘッダー含む）
"""

import re
import os
from datetime import datetime

def extract_articles_from_file(filename):
    """ファイルから記事を抽出"""
    articles = []
    
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # ヘッダー部分をスキップして記事部分のみ抽出
    lines = content.split('\n')
    current_article = []
    in_article = False
    
    for line in lines:
        if line.startswith('記事 ') and '/' in line and ':' in line:
            if current_article:
                articles.append('\n'.join(current_article))
                current_article = []
            in_article = True
            current_article.append(line)
        elif in_article:
            current_article.append(line)
    
    # 最後の記事を追加
    if current_article:
        articles.append('\n'.join(current_article))
    
    return articles

def extract_article_metadata(article_text):
    """記事からメタデータを抽出"""
    lines = article_text.split('\n')
    
    # タイトル
    title_match = re.search(r'記事 \d+/\d+: (.+)', lines[0]) if lines else None
    title = title_match.group(1) if title_match else "タイトル不明"
    
    # URL
    url = ""
    for line in lines:
        if line.startswith('URL: '):
            url = line.replace('URL: ', '')
            break
    
    # 日付
    date = ""
    for line in lines:
        if line.startswith('日付: '):
            date = line.replace('日付: ', '')
            break
    
    return {
        'title': title,
        'url': url,
        'date': date,
        'content': article_text,
        'char_count': len(article_text)
    }

def calculate_header_size(part_num, start_date, end_date, article_count):
    """ヘッダーサイズを正確に計算"""
    header = f"""TerminalHill記事データセット - Part {part_num:02d}
分割日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}
最大文字数: 500,000文字 (2022年以降記事 - 正しいエンコーディング - 再分割版)
期間: {start_date} 〜 {end_date}
記事数: {article_count}
================================================================================

"""
    return len(header)

def split_articles_to_500k_accurate(articles, start_part_num):
    """記事を500K文字以内で正確に分割"""
    max_chars = 500_000
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    part_num = start_part_num
    current_articles = []
    files_created = []
    
    for i, article in enumerate(articles):
        # 現在の記事グループに追加した場合のサイズを計算
        test_articles = current_articles + [article]
        
        # 仮のヘッダーサイズを計算
        if test_articles:
            first_meta = extract_article_metadata(test_articles[0])
            last_meta = extract_article_metadata(test_articles[-1])
            header_size = calculate_header_size(part_num, first_meta['date'], last_meta['date'], len(test_articles))
            
            # 記事内容のサイズ
            content_size = sum(len(art) + 2 for art in test_articles)  # +2 for \n\n between articles
            
            total_size = header_size + content_size
            
            if total_size <= max_chars:
                # 追加可能
                current_articles.append(article)
            else:
                # 現在のファイルを保存
                if current_articles:
                    filename = save_file_accurate(current_articles, part_num, timestamp)
                    
                    # 実際のファイルサイズを取得
                    actual_size = os.path.getsize(filename)
                    with open(filename, 'r', encoding='utf-8') as f:
                        actual_chars = len(f.read())
                    
                    files_created.append({
                        'filename': filename,
                        'articles': len(current_articles),
                        'chars': actual_chars,
                        'bytes': actual_size
                    })
                    part_num += 1
                
                # 新ファイル開始
                current_articles = [article]
        else:
            # 最初の記事
            current_articles = [article]
    
    # 最後のファイル保存
    if current_articles:
        filename = save_file_accurate(current_articles, part_num, timestamp)
        
        actual_size = os.path.getsize(filename)
        with open(filename, 'r', encoding='utf-8') as f:
            actual_chars = len(f.read())
        
        files_created.append({
            'filename': filename,
            'articles': len(current_articles),
            'chars': actual_chars,
            'bytes': actual_size
        })
    
    return files_created

def save_file_accurate(articles, part_num, timestamp):
    """ファイル保存（正確なサイズ計算）"""
    # 最初と最後の記事から日付範囲を取得
    first_meta = extract_article_metadata(articles[0])
    last_meta = extract_article_metadata(articles[-1])
    
    start_date = first_meta['date']
    end_date = last_meta['date']
    
    header = f"""TerminalHill記事データセット - Part {part_num:02d}
分割日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}
最大文字数: 500,000文字 (2022年以降記事 - 正しいエンコーディング - 再分割版)
期間: {start_date} 〜 {end_date}
記事数: {len(articles)}
================================================================================

"""
    
    content = header
    for article in articles:
        content += article + "\n\n"
    
    filename = f"terminalhill_500K_part{part_num:02d}_{timestamp}.txt"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    char_count = len(content)
    size_mb = round(char_count / 1024 / 1024, 2)
    status = "✅" if char_count <= 500_000 else "❌"
    
    print(f"{status} {filename}: {len(articles)}記事, {char_count:,}文字 ({size_mb}MB) [{start_date}〜{end_date}]")
    return filename

def fix_part16_18_split_v2():
    """Part16-18を正しく再分割 v2"""
    print("🔄 Part16-18 再分割開始（500,000文字以内 - v2）")
    
    # 元ファイル名
    original_files = [
        'terminalhill_500K_part16_20250703_173231.txt',
        'terminalhill_500K_part17_20250703_173231.txt',
        'terminalhill_500K_part18_20250703_173231.txt'
    ]
    
    # 全記事を統合
    all_articles = []
    for filename in original_files:
        if os.path.exists(filename):
            print(f"📖 読み込み中: {filename}")
            articles = extract_articles_from_file(filename)
            all_articles.extend(articles)
            print(f"  抽出記事数: {len(articles)}")
        else:
            print(f"❌ ファイルが見つかりません: {filename}")
    
    print(f"📊 総記事数: {len(all_articles)}")
    
    # 日付順でソート
    article_metas = []
    for article in all_articles:
        meta = extract_article_metadata(article)
        meta['content'] = article
        article_metas.append(meta)
    
    # 日付でソート
    article_metas.sort(key=lambda x: x['date'])
    sorted_articles = [meta['content'] for meta in article_metas]
    
    print(f"📅 期間: {article_metas[0]['date']} 〜 {article_metas[-1]['date']}")
    
    # 500K以内で再分割（Part16から開始）
    files_created = split_articles_to_500k_accurate(sorted_articles, 16)
    
    # 結果表示
    total_articles = sum(f['articles'] for f in files_created)
    total_chars = sum(f['chars'] for f in files_created)
    
    print(f"\n=== 再分割完了 v2 ===")
    print(f"新規ファイル数: {len(files_created)}")
    print(f"総記事数: {total_articles:,}")
    print(f"総文字数: {total_chars:,}")
    
    all_within_limit = True
    for f in files_created:
        size_mb = round(f['chars'] / 1024 / 1024, 2)
        status = "✅" if f['chars'] <= 500_000 else "❌ 超過"
        if f['chars'] > 500_000:
            all_within_limit = False
        print(f"  {status} {f['filename']}: {f['articles']}記事, {f['chars']:,}文字 ({size_mb}MB)")
    
    if all_within_limit:
        print("🎉 すべてのファイルが500,000文字以内に収まりました！")
    else:
        print("⚠️ 一部ファイルが制限を超過しています")
    
    return files_created

if __name__ == "__main__":
    fix_part16_18_split_v2() 