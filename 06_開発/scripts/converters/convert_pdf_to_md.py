#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF to Markdown Converter
0L1Mjwjc2Jw8vV2dQR6rQGTXJCH8W1qewxqGZk2U.pdf を Markdown形式に変換
"""

import pdfplumber
import re
import os
from pathlib import Path

def clean_text(text):
    """テキストをクリーンアップ"""
    if not text:
        return ""
    
    # 余分な空白を削除
    text = re.sub(r'\s+', ' ', text)
    # 行頭・行末の空白を削除
    text = text.strip()
    return text

def is_heading(text, font_size=None, is_bold=None):
    """見出しかどうかを判定"""
    if not text:
        return False
    
    text = text.strip()
    
    # 短いテキストで、特定のパターンがある場合は見出しの可能性
    if len(text) < 100:
        # 数字で始まるパターン（例: "1. ", "第1章"）
        if re.match(r'^[第\d]+[章節項]', text):
            return True
        # 数字とピリオドで始まる（例: "1. ", "1.1 "）
        if re.match(r'^\d+\.?\s+', text):
            return True
        # 全角数字で始まる
        if re.match(r'^[０-９]+[\.．]', text):
            return True
    
    return False

def format_as_markdown(text, is_heading_text=False):
    """テキストをMarkdown形式に整形"""
    if not text:
        return ""
    
    text = clean_text(text)
    
    if not text:
        return ""
    
    # 見出しの場合は#を追加
    if is_heading_text and is_heading(text):
        # 見出しレベルの判定
        if re.match(r'^[第\d]+章', text):
            return f"# {text}\n\n"
        elif re.match(r'^[第\d]+節', text):
            return f"## {text}\n\n"
        elif re.match(r'^\d+\.\s+', text):
            return f"### {text}\n\n"
        else:
            return f"## {text}\n\n"
    
    return f"{text}\n\n"

def extract_text_from_pdf(pdf_path):
    """PDFからテキストを抽出"""
    all_text = []
    page_count = 0
    
    print(f"PDFファイルを読み込み中: {pdf_path}")
    
    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)
        print(f"総ページ数: {total_pages}")
        
        for page_num, page in enumerate(pdf.pages, 1):
            page_count += 1
            if page_count % 50 == 0:
                print(f"処理中: {page_count}/{total_pages} ページ")
            
            # テキストを抽出
            text = page.extract_text()
            
            if text:
                # ページ番号を追加（最初のページ以外）
                if page_num > 1:
                    all_text.append(f"\n\n---\n\n## ページ {page_num}\n\n")
                
                # テキストを行ごとに分割
                lines = text.split('\n')
                
                for line in lines:
                    cleaned = clean_text(line)
                    if cleaned:
                        # 見出しの可能性をチェック
                        if is_heading(cleaned):
                            all_text.append(format_as_markdown(cleaned, is_heading_text=True))
                        else:
                            all_text.append(cleaned + "\n")
    
    print(f"処理完了: {page_count} ページ")
    return ''.join(all_text)

def convert_pdf_to_markdown(pdf_path, output_path=None):
    """PDFをMarkdownに変換"""
    pdf_path = Path(pdf_path)
    
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDFファイルが見つかりません: {pdf_path}")
    
    # 出力ファイル名を決定
    if output_path is None:
        output_path = pdf_path.parent / f"{pdf_path.stem}.md"
    else:
        output_path = Path(output_path)
    
    print(f"変換を開始します...")
    markdown_content = extract_text_from_pdf(pdf_path)
    
    # メタデータを追加
    header = f"""---
title: {pdf_path.stem}
source: {pdf_path.name}
converted_from_pdf: true
---

"""
    
    full_content = header + markdown_content
    
    # ファイルに保存
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(full_content)
    
    print(f"変換完了: {output_path}")
    print(f"出力ファイルサイズ: {len(full_content)} 文字")
    
    return output_path

if __name__ == "__main__":
    # PDFファイルのパス
    pdf_file = Path("/Users/ishiinobuyuki/Documents/Obsidian Vault/0L1Mjwjc2Jw8vV2dQR6rQGTXJCH8W1qewxqGZk2U.pdf")
    
    # 変換実行
    try:
        output_file = convert_pdf_to_markdown(pdf_file)
        print(f"\n✅ 変換が完了しました: {output_file}")
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
