#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import argparse
from pathlib import Path

def fix_garbled_text(text):
    """文字化けしたテキストを修正"""
    
    # よく見られる文字化けパターンと正しい文字のマッピング
    fixes = {
        # 基本的な文字化けパターン
        '��': '',  # 不正な文字を削除
        '�': '',   # 不正な文字を削除
        
        # HTML エンティティのデコード
        '&lt;': '<',
        '&gt;': '>',
        '&amp;': '&',
        '&quot;': '"',
        '&#39;': "'",
        
        # よくある日本語の文字化けパターン
        '縺�': 'い',
        '縺�': 'う',
        '縺�': 'え',
        '縺�': 'お',
        '縺�': 'か',
        '縺�': 'き',
        '縺�': 'く',
        '縺�': 'け',
        '縺�': 'こ',
        '縺�': 'さ',
        '縺�': 'し',
        '縺�': 'す',
        '縺�': 'せ',
        '縺�': 'そ',
        '縺�': 'た',
        '縺�': 'ち',
        '縺�': 'つ',
        '縺�': 'て',
        '縺�': 'と',
        '縺�': 'な',
        '縺�': 'に',
        '縺�': 'ぬ',
        '縺�': 'ね',
        '縺�': 'の',
        '縺�': 'は',
        '縺�': 'ひ',
        '縺�': 'ふ',
        '縺�': 'へ',
        '縺�': 'ほ',
        '縺�': 'ま',
        '縺�': 'み',
        '縺�': 'む',
        '縺�': 'め',
        '縺�': 'も',
        '縺�': 'や',
        '縺�': 'ゆ',
        '縺�': 'よ',
        '縺�': 'ら',
        '縺�': 'り',
        '縺�': 'る',
        '縺�': 'れ',
        '縺�': 'ろ',
        '縺�': 'わ',
        '縺�': 'を',
        '縺�': 'ん',
    }
    
    # 文字化け修正を適用
    fixed_text = text
    for garbled, correct in fixes.items():
        fixed_text = fixed_text.replace(garbled, correct)
    
    # 連続する不正文字を除去
    fixed_text = re.sub(r'[��]+', '', fixed_text)
    
    # 改行の正規化
    fixed_text = re.sub(r'\r\n', '\n', fixed_text)
    fixed_text = re.sub(r'\r', '\n', fixed_text)
    
    return fixed_text

def decode_with_multiple_encodings(data):
    """複数のエンコーディングでデコードを試行"""
    encodings = [
        'utf-8',
        'cp932',
        'shift_jis',
        'euc-jp', 
        'iso-2022-jp',
        'utf-8-sig',
        'latin1'
    ]
    
    for encoding in encodings:
        try:
            if isinstance(data, bytes):
                decoded = data.decode(encoding)
            else:
                # 既にstr型の場合、再エンコード・デコードを試行
                decoded = data.encode('latin1').decode(encoding)
            
            # 文字化けが少ないかチェック
            garbled_count = decoded.count('�')
            if garbled_count == 0:
                print(f"✅ デコード成功: {encoding}")
                return decoded
            elif garbled_count < len(decoded) * 0.1:  # 10%未満の文字化けなら許容
                print(f"⚠️ 部分的にデコード成功: {encoding} (文字化け: {garbled_count}文字)")
                return decoded
                
        except (UnicodeDecodeError, UnicodeEncodeError):
            continue
    
    return None

def fix_file(input_file, output_file):
    """ファイルの文字化けを修正"""
    print(f"📂 処理開始: {input_file}")
    
    # バイナリモードで読み込み
    with open(input_file, 'rb') as f:
        raw_data = f.read()
    
    print(f"📏 ファイルサイズ: {len(raw_data):,} bytes")
    
    # 複数エンコーディングでデコード試行
    decoded_text = decode_with_multiple_encodings(raw_data)
    
    if decoded_text is None:
        # 最後の手段として UTF-8 で読み込み、エラーを無視
        print("⚠️ 全エンコーディング失敗、強制デコード実行")
        decoded_text = raw_data.decode('utf-8', errors='replace')
    
    # 文字化け修正を適用
    print("🔧 文字化け修正処理中...")
    fixed_text = fix_garbled_text(decoded_text)
    
    # 修正前後の比較
    original_garbled = decoded_text.count('�')
    fixed_garbled = fixed_text.count('�')
    print(f"📊 修正結果: {original_garbled} → {fixed_garbled} 個の文字化け文字")
    
    # UTF-8で保存
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(fixed_text)
    
    print(f"✅ 修正完了: {output_file}")
    
    # 統計情報
    lines = fixed_text.split('\n')
    print(f"📊 統計:")
    print(f"   - 総行数: {len(lines):,}")
    print(f"   - 総文字数: {len(fixed_text):,}")
    print(f"   - 出力ファイルサイズ: {Path(output_file).stat().st_size / (1024*1024):.2f} MB")
    
    return True

def main():
    parser = argparse.ArgumentParser(description='高度な文字化け修正ツール')
    parser.add_argument('input_file', help='入力ファイル')
    parser.add_argument('--output', '-o', help='出力ファイル')
    parser.add_argument('--preview', '-p', action='store_true', help='修正後の先頭を表示')
    
    args = parser.parse_args()
    
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"❌ ファイルが見つかりません: {args.input_file}")
        return
    
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = input_path.parent / f"{input_path.stem}_fixed_advanced{input_path.suffix}"
    
    success = fix_file(input_path, output_path)
    
    if success and args.preview:
        print("\n📖 修正後の内容確認（先頭30行）:")
        print("=" * 80)
        with open(output_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if i >= 30:
                    print("...")
                    break
                print(f"{i+1:2d}: {line.rstrip()}")
        print("=" * 80)

if __name__ == "__main__":
    main() 