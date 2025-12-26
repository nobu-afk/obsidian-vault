#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2022年以降記事テスト取得スクリプト（数個のURLのみテスト）
"""

import re
import requests
from bs4 import BeautifulSoup

def get_correct_encoding_content(url):
    """正しいエンコーディングで記事内容を取得"""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    })
    
    encodings = ['euc-jp', 'utf-8', 'shift_jis', 'iso-2022-jp']
    
    for encoding in encodings:
        try:
            response = session.get(url, timeout=30)
            response.raise_for_status()
            
            if encoding == 'utf-8':
                text = response.text
            else:
                text = response.content.decode(encoding, errors='ignore')
            
            # 日本語妥当性チェック
            japanese_chars = re.findall(r'[あ-んア-ンー一-龯]', text)
            japanese_count = len(japanese_chars)
            
            garbled_patterns = ['�', '縺', '繝', '繧']
            has_garbled = any(pattern in text for pattern in garbled_patterns)
            
            if japanese_count > 50 and not has_garbled:
                return text, encoding
                
        except Exception as e:
            print(f"    {encoding} エラー: {e}")
            continue
    
    return None, None

def test_post2022_urls():
    """2022年以降のURL数個をテスト"""
    test_urls = [
        "https://terminalhill.jugem.jp/?eid=5700",
        "https://terminalhill.jugem.jp/?eid=5800", 
        "https://terminalhill.jugem.jp/?eid=5900",
        "https://terminalhill.jugem.jp/?eid=6000",
        "https://terminalhill.jugem.jp/?eid=6100"
    ]
    
    print("🔄 2022年以降記事URL テスト開始")
    
    for url in test_urls:
        print(f"\n📋 テスト: {url}")
        
        html_content, encoding = get_correct_encoding_content(url)
        if html_content:
            print(f"  ✅ 成功 エンコーディング: {encoding}")
            
            # 簡単な内容チェック
            soup = BeautifulSoup(html_content, 'html.parser')
            title_element = soup.select_one('h1.title') or soup.select_one('title')
            if title_element:
                title = title_element.get_text(strip=True)
                print(f"  📄 タイトル: {title[:50]}...")
            
            # 日付チェック
            date_match = re.search(r'(\d{4})\.(\d{2})\.(\d{2})', html_content)
            if date_match:
                y, m, d = date_match.groups()
                date = f"{y}-{m}-{d}"
                print(f"  📅 日付: {date}")
                
                try:
                    year = int(y)
                    if year >= 2022:
                        print(f"  ✅ 2022年以降確認")
                    else:
                        print(f"  ❌ 2022年未満")
                except:
                    pass
        else:
            print(f"  ❌ 失敗")

if __name__ == "__main__":
    test_post2022_urls() 