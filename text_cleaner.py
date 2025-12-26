#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TerminalHill記事データクリーナー
指定された不要な文言を記事データから削除
"""

import re
import os
from datetime import datetime

class TextCleaner:
    def __init__(self):
        # 削除対象の文言パターン
        self.patterns_to_remove = [
            # ランキング関連
            r'2つのランキングに参加しています！応援clickよろしくお願いします！.*?人気ブログランキングへ.*?ビジネスブログ100選へ',
            r'2つのランキングに参加しています.*?ビジネスブログ100選へ',
            r'人気ブログランキングへ.*?ビジネスブログ100選へ',
            
            # メルマガ関連（長いパターン）
            r'★無料メルマガ・役立つ仕事術★.*?powered by まぐまぐ.*?PCからの登録は.*?サイドバーのフォームでご登録下さい。.*?携帯からの登録は.*?下記より空メールを送って下さい。.*?■規約に同意して登録■解除.*?携帯でメルマガの説明を確認してからの登録はここをクリック.*?［毎週木曜日午前中発行］.*?PCメール／携帯メール共に登録可能。',
            r'★無料メルマガ・役立つ仕事術★.*?PCメール／携帯メール共に登録可能。',
            r'powered by まぐまぐ.*?PCメール／携帯メール共に登録可能。',
            
            # 相談室関連
            r'★相談室へのお問合せ★.*?お名前・相談の種類・お住まいの都道府県をお知らせ下さい。.*?折り返し、詳しいご案内を返信致します。',
            r'★相談室へのお問合せ★.*?折り返し、詳しいご案内を返信致します。',
            
            # Tweet
            r'Tweet',
            
            # 個別パターン
            r'2つのランキングに参加しています！応援clickよろしくお願いします！',
            r'人気ブログランキングへ',
            r'ビジネスブログ100選へ',
            r'★無料メルマガ・役立つ仕事術★',
            r'powered by まぐまぐ',
            r'PCからの登録は、サイドバーのフォームでご登録下さい。',
            r'携帯からの登録は、下記より空メールを送って下さい。',
            r'■規約に同意して登録■解除',
            r'携帯でメルマガの説明を確認してからの登録はここをクリック',
            r'［毎週木曜日午前中発行］PCメール／携帯メール共に登録可能。',
            r'★相談室へのお問合せ★',
            r'お名前・相談の種類・お住まいの都道府県をお知らせ下さい。',
            r'折り返し、詳しいご案内を返信致します。'
        ]
        
        self.removed_count = 0
        self.total_articles = 0
        
    def clean_text(self, text):
        """テキストから不要な文言を削除"""
        original_text = text
        
        # 各パターンを削除
        for pattern in self.patterns_to_remove:
            # 複数行にわたる場合を考慮
            text = re.sub(pattern, '', text, flags=re.DOTALL | re.IGNORECASE)
        
        # 連続する空行を整理
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        text = re.sub(r'^\s+|\s+$', '', text, flags=re.MULTILINE)
        
        # 削除があったかチェック
        if len(text) < len(original_text):
            self.removed_count += 1
            
        return text
    
    def clean_file(self, input_file, output_file=None):
        """ファイルをクリーニング"""
        if output_file is None:
            output_file = input_file.replace('.txt', '_CLEANED.txt')
            
        print(f"🧹 クリーニング開始: {input_file}")
        
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # ファイル情報
            original_size = len(content)
            original_lines = content.count('\n')
            
            # 記事を分離
            articles = content.split('URL: https://terminalhill.jugem.jp')
            self.total_articles = len(articles) - 1  # 最初の空要素を除く
            
            cleaned_articles = []
            for i, article in enumerate(articles):
                if i == 0 and not article.strip():
                    continue  # 最初の空要素をスキップ
                    
                if article.strip():
                    if i > 0:
                        article = 'URL: https://terminalhill.jugem.jp' + article
                    cleaned_article = self.clean_text(article)
                    cleaned_articles.append(cleaned_article)
            
            # 結合
            cleaned_content = '\n'.join(cleaned_articles)
            
            # 統計情報
            cleaned_size = len(cleaned_content)
            cleaned_lines = cleaned_content.count('\n')
            size_reduction = original_size - cleaned_size
            
            # 保存
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)
                
            print(f"✅ クリーニング完了!")
            print(f"📊 統計情報:")
            print(f"   入力ファイル: {input_file}")
            print(f"   出力ファイル: {output_file}")
            print(f"   記事数: {self.total_articles}")
            print(f"   不要文言削除された記事: {self.removed_count}")
            print(f"   削除率: {self.removed_count/self.total_articles*100:.1f}%")
            print(f"   元サイズ: {original_size:,} 文字")
            print(f"   新サイズ: {cleaned_size:,} 文字")
            print(f"   削減量: {size_reduction:,} 文字 ({size_reduction/original_size*100:.1f}%)")
            
            return output_file
            
        except Exception as e:
            print(f"❌ エラー: {e}")
            return None

def main():
    """メイン処理"""
    cleaner = TextCleaner()
    
    # クリーニング対象ファイル
    files_to_clean = [
        'terminalhill_INTELLIGENT_5652_COMPLETE.txt',
        'terminalhill_all_5652_articles_JAPANESE_COMPLETE.txt',
        'terminalhill_japanese_COMPLETE.txt',
        'terminalhill_sample_1000_JAPANESE_COMPLETE.txt'
    ]
    
    print("🚀 TerminalHill記事データクリーニング開始")
    print("=" * 60)
    
    for file_path in files_to_clean:
        if os.path.exists(file_path):
            cleaner.removed_count = 0  # カウンターリセット
            cleaned_file = cleaner.clean_file(file_path)
            if cleaned_file:
                print(f"✅ {file_path} → {cleaned_file}")
            print("-" * 60)
        else:
            print(f"⚠️ ファイルが見つかりません: {file_path}")
    
    print("🎉 全ファイルのクリーニング完了!")

if __name__ == "__main__":
    main() 