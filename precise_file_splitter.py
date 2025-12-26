#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TerminalHill記事データファイル精密分割システム
1ファイル500,000文字以内で正確に分割
"""

import re
import os
from datetime import datetime

class PreciseFileSplitter:
    def __init__(self, max_chars_per_file=500000):
        self.max_chars_per_file = max_chars_per_file
        self.current_file_num = 1
        self.current_chars = 0
        self.total_articles = 0
        self.total_chars = 0
        self.files_created = []
        
    def split_large_file(self, input_file, output_prefix):
        """巨大ファイルを正確に500,000文字以内で分割"""
        print(f"🔄 精密分割開始: {input_file}")
        print(f"📊 分割設定: {self.max_chars_per_file:,}文字以内/ファイル")
        
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 記事ごとに分割（記事境界を検出）
            articles = self._split_articles(content)
            print(f"📋 総記事数: {len(articles):,}記事")
            
            # 分割実行
            self._create_files(articles, output_prefix)
            
            # 結果レポート
            self._print_summary()
            
        except Exception as e:
            print(f"❌ エラー: {e}")
            
    def _split_articles(self, content):
        """記事ごとに分割"""
        # TerminalHillの記事パターン
        # "URL: https://terminalhill.jugem.jp/?eid=" で始まる記事を検出
        article_pattern = r'(URL: https://terminalhill\.jugem\.jp/\?eid=\d+.*?)(?=URL: https://terminalhill\.jugem\.jp/\?eid=\d+|$)'
        
        articles = re.findall(article_pattern, content, re.DOTALL)
        return articles
        
    def _create_files(self, articles, output_prefix):
        """記事を500,000文字以内のファイルに分割"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        current_content = ""
        current_chars = 0
        articles_in_file = 0
        
        # ヘッダー情報
        header = f"""TerminalHill記事データセット - Part {self.current_file_num:02d}
分割日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}
最大文字数: {self.max_chars_per_file:,}文字
================================================================================

"""
        current_content = header
        current_chars = len(header)
        
        for i, article in enumerate(articles):
            article_chars = len(article)
            
            # 次の記事を追加しても500,000文字以内かチェック
            if current_chars + article_chars <= self.max_chars_per_file:
                current_content += article + "\n\n"
                current_chars += article_chars + 2  # \n\n分
                articles_in_file += 1
            else:
                # 現在のファイルを保存
                self._save_file(current_content, output_prefix, timestamp, 
                              articles_in_file, current_chars)
                
                # 新しいファイル開始
                self.current_file_num += 1
                header = f"""TerminalHill記事データセット - Part {self.current_file_num:02d}
分割日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}
最大文字数: {self.max_chars_per_file:,}文字
================================================================================

"""
                current_content = header + article + "\n\n"
                current_chars = len(header) + article_chars + 2
                articles_in_file = 1
        
        # 最後のファイル保存
        if current_content.strip():
            self._save_file(current_content, output_prefix, timestamp, 
                          articles_in_file, current_chars)
            
    def _save_file(self, content, output_prefix, timestamp, articles, chars):
        """ファイル保存"""
        filename = f"{output_prefix}_part{self.current_file_num:02d}_{timestamp}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
            
        # 統計更新
        self.total_articles += articles
        self.total_chars += chars
        self.files_created.append({
            'filename': filename,
            'articles': articles,
            'chars': chars,
            'size_mb': round(chars / 1024 / 1024, 2)
        })
        
        print(f"✅ Part{self.current_file_num:02d}: {articles}記事, {chars:,}文字 → {filename}")
        
    def _print_summary(self):
        """結果サマリー表示"""
        print("\n" + "="*80)
        print("🎉 精密分割完了!")
        print("="*80)
        print(f"📊 総ファイル数: {len(self.files_created)}ファイル")
        print(f"📝 総記事数: {self.total_articles:,}記事")
        print(f"💾 総文字数: {self.total_chars:,}文字")
        print(f"📁 平均文字数/ファイル: {self.total_chars//len(self.files_created):,}文字")
        print()
        
        print("📋 分割ファイル詳細:")
        for file_info in self.files_created:
            print(f"  {file_info['filename']}")
            print(f"    記事数: {file_info['articles']:,}, 文字数: {file_info['chars']:,}, サイズ: {file_info['size_mb']}MB")
        
        # 500,000文字制限チェック
        over_limit = [f for f in self.files_created if f['chars'] > self.max_chars_per_file]
        if over_limit:
            print(f"\n⚠️ 制限超過ファイル: {len(over_limit)}個")
            for f in over_limit:
                print(f"  {f['filename']}: {f['chars']:,}文字 (制限: {self.max_chars_per_file:,})")
        else:
            print(f"\n✅ 全ファイルが{self.max_chars_per_file:,}文字以内で分割完了!")

if __name__ == "__main__":
    splitter = PreciseFileSplitter(max_chars_per_file=500000)
    
    # 元ファイル名を確認
    input_file = "terminalhill_INTELLIGENT_5652_COMPLETE_CLEANED.txt"
    output_prefix = "terminalhill_500K"
    
    if os.path.exists(input_file):
        splitter.split_large_file(input_file, output_prefix)
    else:
        print(f"❌ ファイルが見つかりません: {input_file}")
        print("利用可能なファイル:")
        for f in os.listdir('.'):
            if f.startswith('terminalhill') and f.endswith('.txt'):
                size = os.path.getsize(f) / 1024 / 1024
                print(f"  {f} ({size:.1f}MB)") 