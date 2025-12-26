#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
デバッグ用データセット統合スクリプト
"""

import re
from datetime import datetime
from collections import defaultdict

def debug_file_content(filename):
    """ファイル内容をデバッグ"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"\n🔍 {filename} のデバッグ:")
        print(f"  ファイルサイズ: {len(content):,}文字")
        
        # 区切り線の数をカウント
        separator_count = content.count('=' * 80)
        print(f"  区切り線の数: {separator_count}")
        
        # URLパターンの確認
        url_matches = re.findall(r'URL: https://terminalhill\.jugem\.jp/\?eid=(\d+)', content)
        print(f"  URLマッチ数: {len(url_matches)}")
        
        if url_matches:
            print(f"  EID例: {url_matches[:5]}")
        
        # セクションに分割してテスト
        sections = content.split('=' * 80)
        print(f"  セクション数: {len(sections)}")
        
        url_sections = 0
        for section in sections:
            if 'URL: https://terminalhill.jugem.jp' in section:
                url_sections += 1
        
        print(f"  URL含有セクション: {url_sections}")
        
        # 最初のURL含有セクションを詳細分析
        for i, section in enumerate(sections):
            if 'URL: https://terminalhill.jugem.jp' in section:
                print(f"\n📋 最初のURL含有セクション（セクション{i}）:")
                lines = section.split('\n')[:10]
                for j, line in enumerate(lines):
                    print(f"    {j}: {repr(line[:100])}")
                break
        
        return True
        
    except Exception as e:
        print(f"❌ {filename} のデバッグでエラー: {e}")
        return False

def extract_articles_debug(filename):
    """デバッグ付き記事抽出"""
    articles = {}
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        sections = content.split('=' * 80)
        print(f"\n🔍 {filename} の抽出デバッグ:")
        print(f"  総セクション数: {len(sections)}")
        
        url_sections = 0
        extracted = 0
        
        for i, section in enumerate(sections):
            if 'URL: https://terminalhill.jugem.jp' in section:
                url_sections += 1
                
                # URL抽出
                url_match = re.search(r'URL: (https://terminalhill\.jugem\.jp/\?eid=(\d+))', section)
                if url_match:
                    url = url_match.group(1)
                    eid = int(url_match.group(2))
                    
                    # タイトル抽出
                    title_match = re.search(r'記事 \d+(?:/\d+)?: (.+)', section)
                    title = title_match.group(1).strip() if title_match else "タイトル不明"
                    
                    # 日付抽出
                    date_match = re.search(r'日付: (.+)', section)
                    date = date_match.group(1).strip() if date_match else "日付不明"
                    
                    # 本文抽出
                    lines = section.split('\n')
                    content_lines = []
                    start_content = False
                    
                    for line in lines:
                        if line.startswith('=') or 'URL:' in line or '日付:' in line or ('記事' in line and ':' in line):
                            continue
                        if not line.strip() and not start_content:
                            start_content = True
                            continue
                        if start_content and line.strip():
                            content_lines.append(line)
                    
                    content_text = '\n'.join(content_lines).strip()
                    
                    if content_text and len(content_text) > 100:
                        articles[eid] = {
                            'eid': eid,
                            'url': url,
                            'title': title,
                            'date': date,
                            'content': content_text,
                            'char_count': len(content_text),
                            'source_file': filename
                        }
                        extracted += 1
                        
                        if extracted <= 3:  # 最初の3記事をデバッグ出力
                            print(f"\n  記事 {extracted}:")
                            print(f"    EID: {eid}")
                            print(f"    タイトル: {title[:50]}...")
                            print(f"    日付: {date}")
                            print(f"    本文文字数: {len(content_text)}")
        
        print(f"  URL含有セクション: {url_sections}")
        print(f"  抽出成功: {extracted}")
        return articles
        
    except Exception as e:
        print(f"❌ 抽出エラー: {e}")
        return {}

if __name__ == "__main__":
    print("🔍 デバッグモード：データセット統合")
    print("=" * 60)
    
    files = ['terminalhill_clean_all_articles.txt', 'terminalhill_sample_1000.txt']
    
    for filename in files:
        print(f"\n{'='*20} {filename} {'='*20}")
        debug_file_content(filename)
        articles = extract_articles_debug(filename)
        print(f"✅ 最終抽出数: {len(articles)}記事")
    
    print("\n🎯 デバッグ完了") 