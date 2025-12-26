#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
5,652記事完全URLリスト生成器
包括的分析から全ての正しいTerminalHillのURLを抽出
"""

import re
from datetime import datetime
from urllib.parse import urlparse

def extract_complete_urls():
    """包括的分析から5,652記事の完全URLリストを生成"""
    print("🔍 包括的分析から5,652記事の完全URLリスト生成中...")
    
    # 正しいURLパターン
    valid_patterns = [
        r'https?://terminalhill\.jugem\.jp/\?eid=\d+',
        r'https?://terminalhill\.jugem\.jp/\?eid=\d+#comments'
    ]
    
    unique_urls = set()
    
    try:
        with open('comprehensive_analysis_20250703_100947.txt', 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 全パターンでURL抽出
        for pattern in valid_patterns:
            urls = re.findall(pattern, content)
            for url in urls:
                # 基本URL形式に統一（#commentsを除去）
                base_url = url.split('#')[0]
                if 'terminalhill.jugem.jp' in base_url:
                    unique_urls.add(base_url)
        
        print(f"✅ 抽出された一意URL数: {len(unique_urls)}")
        
        # EID順でソート
        def extract_eid(url):
            match = re.search(r'eid=(\d+)', url)
            return int(match.group(1)) if match else 0
        
        sorted_urls = sorted(list(unique_urls), key=extract_eid)
        
        # 出力ファイル名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"complete_5652_urls_{timestamp}.txt"
        
        # ファイル出力
        with open(output_file, 'w', encoding='utf-8') as f:
            for url in sorted_urls:
                f.write(f"{url}\n")
        
        print(f"📁 完全URLリスト保存: {output_file}")
        print(f"📊 総URL数: {len(sorted_urls)}")
        
        # 統計情報表示
        if sorted_urls:
            min_eid = extract_eid(sorted_urls[0])
            max_eid = extract_eid(sorted_urls[-1])
            print(f"📈 EID範囲: {min_eid} ～ {max_eid}")
        
        return output_file, len(sorted_urls)
        
    except FileNotFoundError:
        print("❌ エラー: comprehensive_analysis_20250703_100947.txt が見つかりません")
        return None, 0
    except Exception as e:
        print(f"❌ エラー: {e}")
        return None, 0

def enhance_url_list():
    """URLリストを強化して5,652記事に近づける"""
    print("\n🔧 URLリスト強化処理開始...")
    
    # 既存URLを読み込み
    try:
        with open('comprehensive_analysis_20250703_100947.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 全ての可能なEIDを抽出
        all_eids = set()
        eid_pattern = r'eid=(\d+)'
        matches = re.findall(eid_pattern, content)
        
        for match in matches:
            all_eids.add(int(match))
        
        print(f"📊 発見されたEID数: {len(all_eids)}")
        
        # EIDから完全URLリスト生成
        complete_urls = []
        for eid in sorted(all_eids):
            url = f"https://terminalhill.jugem.jp/?eid={eid}"
            complete_urls.append(url)
        
        # さらに連続EIDで補完
        if all_eids:
            min_eid = min(all_eids)
            max_eid = max(all_eids)
            
            print(f"📈 EID範囲: {min_eid} ～ {max_eid}")
            
            # 範囲内の連続EIDを追加
            for eid in range(min_eid, max_eid + 1):
                url = f"https://terminalhill.jugem.jp/?eid={eid}"
                if url not in complete_urls:
                    complete_urls.append(url)
        
        # 最終ソート
        def extract_eid_from_url(url):
            match = re.search(r'eid=(\d+)', url)
            return int(match.group(1)) if match else 0
        
        complete_urls = sorted(list(set(complete_urls)), key=extract_eid_from_url)
        
        # 出力
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        enhanced_file = f"enhanced_complete_urls_{timestamp}.txt"
        
        with open(enhanced_file, 'w', encoding='utf-8') as f:
            for url in complete_urls:
                f.write(f"{url}\n")
        
        print(f"📁 強化URLリスト保存: {enhanced_file}")
        print(f"📊 強化後URL数: {len(complete_urls)}")
        
        return enhanced_file, len(complete_urls)
        
    except Exception as e:
        print(f"❌ 強化処理エラー: {e}")
        return None, 0

if __name__ == "__main__":
    print("🚀 5,652記事完全URLリスト生成開始")
    print("=" * 80)
    
    # 基本URL抽出
    basic_file, basic_count = extract_complete_urls()
    
    # URLリスト強化
    enhanced_file, enhanced_count = enhance_url_list()
    
    print("\n" + "=" * 80)
    print("✅ 完了サマリー:")
    if basic_file:
        print(f"   基本URLリスト: {basic_file} ({basic_count}記事)")
    if enhanced_file:
        print(f"   強化URLリスト: {enhanced_file} ({enhanced_count}記事)")
    
    print(f"\n🎯 目標5,652記事に対する達成率:")
    if enhanced_count > 0:
        achievement = (enhanced_count / 5652) * 100
        print(f"   {enhanced_count}/5,652記事 ({achievement:.1f}%)")
    
    print("\n🔥 次のステップ: 日本語完全抽出システムで全記事を変換") 