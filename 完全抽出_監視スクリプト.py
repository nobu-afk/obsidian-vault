#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完全抽出進行状況監視スクリプト
"""

import os
import time
from datetime import datetime

def monitor_complete_extraction():
    """完全抽出の進行状況を監視"""
    
    target_file = 'terminalhill_complete_all_articles.txt'
    total_articles = 5652
    
    print("=" * 80)
    print(f"完全記事抽出進行状況監視 - {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 80)
    
    if os.path.exists(target_file):
        # ファイルサイズを取得
        size = os.path.getsize(target_file)
        size_mb = size / (1024 * 1024)
        
        # 記事数を概算（記事区切りの = を数える）
        try:
            with open(target_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                article_count = content.count('================================================================================')
                # 記事区切りは2個で1記事なので半分
                estimated_articles = article_count // 2
        except Exception as e:
            print(f"ファイル読み込みエラー: {e}")
            estimated_articles = 0
        
        print(f"📄 出力ファイル: {target_file}")
        print(f"   📏 ファイルサイズ: {size_mb:.2f} MB ({size:,} bytes)")
        print(f"   📊 推定記事数: {estimated_articles:,} / {total_articles:,}")
        
        if estimated_articles > 0:
            progress_percent = (estimated_articles / total_articles) * 100
            print(f"   🎯 進行率: {progress_percent:.1f}%")
            
            # 予想完了時間を計算（現在時刻基準）
            if progress_percent >= 1:  # 1%以上進行していれば計算
                current_time = time.time()
                # ファイル作成時刻を取得
                file_creation_time = os.path.getctime(target_file)
                elapsed_time = current_time - file_creation_time
                
                estimated_total_time = (100 / progress_percent) * elapsed_time
                remaining_time = estimated_total_time - elapsed_time
                remaining_hours = remaining_time / 3600
                
                completion_time = datetime.fromtimestamp(current_time + remaining_time)
                print(f"   ⏱️ 経過時間: {elapsed_time/3600:.1f} 時間")
                print(f"   🕐 予想残り時間: {remaining_hours:.1f} 時間")
                print(f"   🏁 予想完了時刻: {completion_time.strftime('%H:%M:%S')}")
                
                # 抽出速度を計算
                articles_per_hour = estimated_articles / (elapsed_time / 3600)
                print(f"   ⚡ 抽出速度: {articles_per_hour:.0f} 記事/時間")
        
        print()
        
        # 最近の記事タイトルを表示（ファイルの最後の部分）
        try:
            with open(target_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                
            # 最後の記事情報を探す
            recent_titles = []
            for i in range(len(lines)-1, max(0, len(lines)-100), -1):
                line = lines[i].strip()
                if line.startswith('記事 ') and ':' in line:
                    title_part = line.split(':', 1)[1].strip()
                    recent_titles.append(title_part)
                    if len(recent_titles) >= 3:
                        break
            
            if recent_titles:
                print("📖 最近処理された記事:")
                for i, title in enumerate(reversed(recent_titles), 1):
                    print(f"   {i}. {title[:60]}...")
        except:
            pass
        
    else:
        print(f"❌ {target_file} - まだ作成されていません")
    
    print()
    
    # プロセス情報
    import subprocess
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        python_processes = [line for line in result.stdout.split('\n') if 'complete_scraper' in line]
        
        if python_processes:
            print("🔄 実行中のプロセス:")
            for proc in python_processes:
                print(f"   {proc}")
        else:
            print("⚠️  完全抽出プロセスが見つかりません")
    except:
        print("プロセス情報の取得に失敗")
    
    print()
    
    # システムリソース情報
    try:
        result = subprocess.run(['df', '-h', '.'], capture_output=True, text=True)
        lines = result.stdout.strip().split('\n')
        if len(lines) >= 2:
            header = lines[0]
            data = lines[1]
            print("💽 ディスク使用量:")
            print(f"   {header}")
            print(f"   {data}")
    except:
        pass

if __name__ == "__main__":
    monitor_complete_extraction() 