#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import chardet
import argparse
from pathlib import Path

def detect_encoding(file_path):
    """ファイルのエンコーディングを検出"""
    with open(file_path, 'rb') as f:
        raw_data = f.read()
        result = chardet.detect(raw_data)
        return result['encoding'] if result else None

def fix_encoding(input_file, output_file):
    """文字化けを修正してファイルを保存"""
    print(f"📂 処理開始: {input_file}")
    
    # エンコーディングを検出
    detected_encoding = detect_encoding(input_file)
    print(f"🔍 検出エンコーディング: {detected_encoding}")
    
    # 複数のエンコーディングを試行
    encodings_to_try = [
        detected_encoding,
        'utf-8',
        'cp932',
        'shift_jis',
        'euc-jp',
        'iso-2022-jp',
        'latin1'
    ]
    
    content = None
    used_encoding = None
    
    for encoding in encodings_to_try:
        if encoding is None:
            continue
        try:
            with open(input_file, 'r', encoding=encoding) as f:
                content = f.read()
                used_encoding = encoding
                print(f"✅ 読み込み成功: {encoding}")
                break
        except Exception as e:
            print(f"❌ {encoding}で読み込み失敗: {str(e)[:50]}...")
            continue
    
    if content is None:
        print("❌ すべてのエンコーディングで読み込みに失敗しました")
        return False
    
    # UTF-8で保存
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ 修正完了: {output_file}")
        print(f"📊 使用エンコーディング: {used_encoding} → UTF-8")
        return True
    except Exception as e:
        print(f"❌ 保存エラー: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='文字化けしたテキストファイルを修正')
    parser.add_argument('input_file', help='入力ファイル')
    parser.add_argument('--output', '-o', help='出力ファイル（指定しない場合は_fixed付きで保存）')
    
    args = parser.parse_args()
    
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"❌ ファイルが見つかりません: {args.input_file}")
        return
    
    if args.output:
        output_path = Path(args.output)
    else:
        # _fixedを付けて保存
        output_path = input_path.parent / f"{input_path.stem}_fixed{input_path.suffix}"
    
    success = fix_encoding(input_path, output_path)
    
    if success:
        # ファイルサイズ確認
        input_size = input_path.stat().st_size / (1024 * 1024)  # MB
        output_size = output_path.stat().st_size / (1024 * 1024)  # MB
        print(f"📏 サイズ比較: {input_size:.2f}MB → {output_size:.2f}MB")
        
        # 先頭部分を確認
        print("\n📖 修正後の内容確認（先頭20行）:")
        print("=" * 50)
        with open(output_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if i >= 20:
                    break
                print(line.rstrip())
        print("=" * 50)

if __name__ == "__main__":
    main() 