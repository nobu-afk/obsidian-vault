#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
クリーンなURLリスト生成スクリプト
既存の成功データから正しいURLパターンを抽出
"""

import re
from datetime import datetime

def generate_clean_urls():
    """既存の成功したデータから正しいURLリストを生成"""
    
    # 既存の成功したファイルから記事IDを抽出
    successful_articles = set()
    
    print("既存の成功データから記事IDを抽出中...")
    
    # blog_scraper_improved.pyで成功した記事IDを使用
    # (以前のファイルから抽出)
    try:
        with open('terminalhill_all_5652_articles.txt', 'r', encoding='utf-8') as f:
            content = f.read()
            # URL: https://terminalhill.jugem.jp/?eid=数字 のパターンを抽出
            url_pattern = r'URL: https://terminalhill\.jugem\.jp/\?eid=(\d+)'
            matches = re.findall(url_pattern, content)
            for match in matches:
                successful_articles.add(int(match))
        print(f"✓ 既存データから {len(successful_articles)}記事のIDを抽出")
    except FileNotFoundError:
        print("既存データが見つからないため、範囲指定で生成します")
    
    # 確実に存在する記事ID範囲を生成 (以前の分析結果を基に)
    base_ids = set()
    
    # 既存データがある場合はそれを使用、なければ一般的な範囲
    if successful_articles:
        base_ids = successful_articles
    else:
        # 確実に存在するIDの範囲 (以前のテストで確認済み)
        for eid in range(137, 52888):  # 以前の分析で判明した範囲
            if eid % 100 == 0:  # サンプリング
                base_ids.add(eid)
    
    # 正しいURLフォーマットで生成
    clean_urls = set()
    base_url = "https://terminalhill.jugem.jp/?eid="
    
    for article_id in base_ids:
        clean_url = f"{base_url}{article_id}"
        clean_urls.add(clean_url)
    
    # 追加の確実なURL（過去のテストで成功したもの）
    confirmed_working_urls = [
        "https://terminalhill.jugem.jp/?eid=522",
        "https://terminalhill.jugem.jp/?eid=2088", 
        "https://terminalhill.jugem.jp/?eid=2794",
        "https://terminalhill.jugem.jp/?eid=3175",
        "https://terminalhill.jugem.jp/?eid=3238",
        "https://terminalhill.jugem.jp/?eid=3292",
        "https://terminalhill.jugem.jp/?eid=3665",
        "https://terminalhill.jugem.jp/?eid=3970",
        "https://terminalhill.jugem.jp/?eid=4012",
        "https://terminalhill.jugem.jp/?eid=4456",
        "https://terminalhill.jugem.jp/?eid=4469",
        "https://terminalhill.jugem.jp/?eid=4533",
        "https://terminalhill.jugem.jp/?eid=4656",
        "https://terminalhill.jugem.jp/?eid=4675",
        "https://terminalhill.jugem.jp/?eid=4859",
        "https://terminalhill.jugem.jp/?eid=5082",
        "https://terminalhill.jugem.jp/?eid=5290",
        "https://terminalhill.jugem.jp/?eid=5330",
        "https://terminalhill.jugem.jp/?eid=5440",
        "https://terminalhill.jugem.jp/?eid=5462",
        "https://terminalhill.jugem.jp/?eid=5543",
        "https://terminalhill.jugem.jp/?eid=5637",
        "https://terminalhill.jugem.jp/?eid=5808",
        "https://terminalhill.jugem.jp/?eid=5847",
        "https://terminalhill.jugem.jp/?eid=5908",
        "https://terminalhill.jugem.jp/?eid=5938",
        "https://terminalhill.jugem.jp/?eid=5963",
        "https://terminalhill.jugem.jp/?eid=5970",
        "https://terminalhill.jugem.jp/?eid=5989",
        "https://terminalhill.jugem.jp/?eid=5996",
        "https://terminalhill.jugem.jp/?eid=6031",
        "https://terminalhill.jugem.jp/?eid=6050",
        "https://terminalhill.jugem.jp/?eid=6158",
        "https://terminalhill.jugem.jp/?eid=6188",
        "https://terminalhill.jugem.jp/?eid=6467",
        "https://terminalhill.jugem.jp/?eid=6470",
        "https://terminalhill.jugem.jp/?eid=6476",
        "https://terminalhill.jugem.jp/?eid=6507",
        "https://terminalhill.jugem.jp/?eid=6529",
        "https://terminalhill.jugem.jp/?eid=6535",
        "https://terminalhill.jugem.jp/?eid=6547",
        "https://terminalhill.jugem.jp/?eid=6560",
        "https://terminalhill.jugem.jp/?eid=6562",
        "https://terminalhill.jugem.jp/?eid=6563",
        "https://terminalhill.jugem.jp/?eid=6567",
        "https://terminalhill.jugem.jp/?eid=6590",
        "https://terminalhill.jugem.jp/?eid=6624",
        "https://terminalhill.jugem.jp/?eid=6641",
        "https://terminalhill.jugem.jp/?eid=6654",
        "https://terminalhill.jugem.jp/?eid=6661",
        "https://terminalhill.jugem.jp/?eid=6683",
        "https://terminalhill.jugem.jp/?eid=6687",
        "https://terminalhill.jugem.jp/?eid=6693",
        "https://terminalhill.jugem.jp/?eid=6717",
        "https://terminalhill.jugem.jp/?eid=6721",
        "https://terminalhill.jugem.jp/?eid=6724",
        "https://terminalhill.jugem.jp/?eid=6746",
        "https://terminalhill.jugem.jp/?eid=6749",
        "https://terminalhill.jugem.jp/?eid=6776",
        "https://terminalhill.jugem.jp/?eid=6836",
        "https://terminalhill.jugem.jp/?eid=6839",
        "https://terminalhill.jugem.jp/?eid=6899",
        "https://terminalhill.jugem.jp/?eid=6904",
        "https://terminalhill.jugem.jp/?eid=6906",
        "https://terminalhill.jugem.jp/?eid=6933",
        "https://terminalhill.jugem.jp/?eid=6934",
        "https://terminalhill.jugem.jp/?eid=6936"
    ]
    
    for url in confirmed_working_urls:
        clean_urls.add(url)
    
    print(f"✅ 最終的なクリーンURLリスト: {len(clean_urls)}記事")
    
    # ファイルに保存
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"clean_urls_{timestamp}.txt"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"クリーンな記事URL一覧 (terminalhill.jugem.jp)\n")
        f.write(f"生成日時: {datetime.now()}\n")
        f.write(f"総記事数: {len(clean_urls)}\n\n")
        f.write("全記事URL一覧:\n")
        
        # IDでソート
        sorted_urls = sorted(clean_urls, key=lambda x: int(re.findall(r'eid=(\d+)', x)[0]))
        for url in sorted_urls:
            f.write(f"{url}\n")
    
    print(f"✅ クリーンなURLリストを {filename} に保存しました")
    return filename, len(clean_urls)

if __name__ == "__main__":
    filename, count = generate_clean_urls()
    print(f"\n🎯 次のステップ:")
    print(f"python complete_scraper.py --url-list {filename} --output terminalhill_clean_all_articles.txt --delay 2") 