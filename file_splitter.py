#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TerminalHill記事データファイル分割システム
1,820万文字の巨大ファイルを500,000文字ずつ15個に分割
"""

import re
import os
from datetime import datetime

class FileSplitter:
    def __init__(self, max_chars_per_file=500000, max_files=15):
        self.max_chars_per_file = max_chars_per_file
        self.max_files = max_files
        self.current_file_num = 1
        self.current_chars = 0
        self.total_articles = 0
        self.total_chars = 0
        
    def split_large_file(self, input_file, output_prefix):
        """巨大ファイルを指定文字数で分割"""
        print(f"🔄 ファイル分割開始: {input_file}")
        print(f"📊 分割設定: {self.max_chars_per_file:,}文字 × {self.max_files}ファイル")
        
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 記事ごとに分割
            articles = self.extract_articles(content)
            print(f"📝 総記事数: {len(articles):,}記事")
            
            # ファイルに分割
            self.split_articles_to_files(articles, output_prefix)
            
            print(f"\n✅ 分割完了!")
            print(f"📊 作成ファイル数: {self.current_file_num - 1}")
            print(f"📝 総記事数: {self.total_articles:,}記事")
            print(f"📄 総文字数: {self.total_chars:,}文字")
            
        except Exception as e:
            print(f"❌ エラー: {e}")
            
    def extract_articles(self, content):
        """記事を個別に抽出"""
        # 記事の境界パターン（URL:で始まる行）
        article_pattern = r'(URL: https://terminalhill\.jugem\.jp/.*?(?=URL: https://terminalhill\.jugem\.jp/|$))'
        
        articles = re.findall(article_pattern, content, re.DOTALL)
        
        if not articles:
            # パターンが見つからない場合は行ごとに分割
            lines = content.split('\n')
            articles = []
            current_article = []
            
            for line in lines:
                if line.startswith('URL: https://terminalhill.jugem.jp/') and current_article:
                    articles.append('\n'.join(current_article))
                    current_article = [line]
                else:
                    current_article.append(line)
            
            if current_article:
                articles.append('\n'.join(current_article))
        
        return articles
        
    def split_articles_to_files(self, articles, output_prefix):
        """記事を複数ファイルに分割"""
        current_content = []
        current_chars = 0
        articles_in_file = 0
        
        for i, article in enumerate(articles):
            article_chars = len(article)
            
            # ファイルサイズチェック
            if (current_chars + article_chars > self.max_chars_per_file and current_content) or \
               self.current_file_num > self.max_files:
                
                # 現在のファイルを保存
                self.save_current_file(current_content, output_prefix, articles_in_file, current_chars)
                
                # 次のファイルの準備
                current_content = []
                current_chars = 0
                articles_in_file = 0
                self.current_file_num += 1
                
                if self.current_file_num > self.max_files:
                    print(f"⚠️ 最大ファイル数{self.max_files}に達しました")
                    break
            
            # 記事を追加
            current_content.append(article)
            current_chars += article_chars
            articles_in_file += 1
            self.total_articles += 1
            self.total_chars += article_chars
            
            # 進行状況表示
            if (i + 1) % 100 == 0:
                print(f"📊 処理中: {i + 1:,}/{len(articles):,}記事 "
                      f"(ファイル{self.current_file_num}: {current_chars:,}文字)")
        
        # 最後のファイルを保存
        if current_content:
            self.save_current_file(current_content, output_prefix, articles_in_file, current_chars)
            
    def save_current_file(self, content_list, output_prefix, articles_count, chars_count):
        """現在のファイルを保存"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{output_prefix}_part{self.current_file_num:02d}_{timestamp}.txt"
        
        # ヘッダー情報
        header = f"""TerminalHill ブログ記事データセット - Part {self.current_file_num:02d}
================================================================================
作成日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}
記事数: {articles_count:,}記事
文字数: {chars_count:,}文字
ファイル: {filename}
================================================================================

"""
        
        # ファイル保存
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(header)
            f.write('\n'.join(content_list))
            
        print(f"✅ 保存完了: {filename} ({articles_count:,}記事, {chars_count:,}文字)")

def main():
    splitter = FileSplitter(max_chars_per_file=500000, max_files=15)
    splitter.split_large_file(
        'terminalhill_INTELLIGENT_5652_COMPLETE_CLEANED.txt',
        'terminalhill_SPLIT'
    )

if __name__ == "__main__":
    main() 