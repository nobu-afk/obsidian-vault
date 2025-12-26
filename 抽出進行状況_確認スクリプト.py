#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
記事抽出進行状況確認スクリプト
"""

import os
import time
from datetime import datetime

def check_progress():
    """抽出進行状況をチェック"""
    
    target_files = [
        'terminalhill_all_5652_articles.txt',
        'terminalhill_all_articles.txt'
    ]
    
    print("=" * 60)
    print(f"記事抽出進行状況チェック - {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 60)
    
    for filename in target_files:
        if os.path.exists(filename):
            # ファイルサイズを取得
            size = os.path.getsize(filename)
            size_mb = size / (1024 * 1024)
            
            # 行数を概算（記事区切りの = を数える）
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                    article_count = content.count('================================================================================')
                    # 記事区切りは2個で1記事なので半分
                    estimated_articles = article_count // 2
            except:
                estimated_articles = 0
            
            print(f"📄 ファイル: {filename}")
            print(f"   サイズ: {size_mb:.2f} MB ({size:,} bytes)")
            print(f"   推定記事数: {estimated_articles:,}")
            if estimated_articles > 0:
                progress_percent = (estimated_articles / 5652) * 100
                print(f"   進行率: {progress_percent:.1f}%")
                
                # 予想残り時間を計算
                if progress_percent > 1:  # 1%以上進行していれば計算
                    estimated_total_time = (100 / progress_percent) * (time.time() - start_time)
                    remaining_time = estimated_total_time - (time.time() - start_time)
                    remaining_hours = remaining_time / 3600
                    print(f"   予想残り時間: {remaining_hours:.1f} 時間")
            print()
        else:
            print(f"❌ {filename} - まだ作成されていません")
            print()
    
    # プロセス情報
    import subprocess
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        python_processes = [line for line in result.stdout.split('\n') if 'blog_scraper' in line]
        
        if python_processes:
            print("🔄 実行中のプロセス:")
            for proc in python_processes:
                print(f"   {proc}")
        else:
            print("⚠️  抽出プロセスが見つかりません")
    except:
        print("プロセス情報の取得に失敗")

if __name__ == "__main__":
    start_time = time.time()
    check_progress() 