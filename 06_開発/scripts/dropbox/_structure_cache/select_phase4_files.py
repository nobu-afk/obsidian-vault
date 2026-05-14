#!/usr/bin/env python3
"""Phase 4 ファイル選定ロジック
引き継ぎ書 §3 + §6.2 の選定ルール準拠
"""
import json
import os
import re
from pathlib import Path

CACHE = Path(__file__).parent
OUT = CACHE / 'phase4_selection.json'

# ファイル拡張子フィルタ
VALID_EXT = {'.xlsx', '.pptx', '.pdf', '.docx', '.doc', '.xls', '.ppt'}

# サイズ制約 50KB - 30MB
MIN_SIZE = 50 * 1024
MAX_SIZE = 30 * 1024 * 1024

# 除外パターン（機密性高すぎ・個人情報）
EXCLUDE_PATTERNS = [
    r'給料',
    r'給与台帳',
    r'年収',
    r'退職金',
    r'業務委託契約書',
    r'労働契約',
    r'個別評価',
    r'添削済',  # 個別添削
    r'窪さん打ち合わせ',
    r'_archive',
    r'\.DS_Store',
    r'~\$',  # Excel/Word 一時ファイル
    r'^\..*',  # 隠しファイル
]


def is_excluded(path: str) -> bool:
    for p in EXCLUDE_PATTERNS:
        if re.search(p, path, re.IGNORECASE):
            return True
    return False


def load(name):
    with open(CACHE / name) as f:
        return json.load(f)


def get_files(data, source_tag):
    out = []
    for e in data:
        if e.get('type') != 'file':
            continue
        path = e.get('path', '')
        name = e.get('name', '')
        size = e.get('size', 0)
        ext = os.path.splitext(name)[1].lower()
        if ext not in VALID_EXT:
            continue
        if size < MIN_SIZE or size > MAX_SIZE:
            continue
        if is_excluded(path):
            continue
        out.append({
            'name': name,
            'path': path,
            'size': size,
            'ext': ext,
            'source': source_tag,
        })
    return out


def main():
    sources = {
        'minagine_007_道具箱.json': '007_道具箱',
        'minagine_008_コンサル用.json': '008_コンサル用',
        'jinji_univ_consulting.json': 'jinji_consulting',
        'minagine_003_運用.json': '003_運用支援パック',
        'minagine_009_運用.json': '009_運用サポート',
        'minagine_001_営業.json': '001_営業資料',
        'minagine_007_order.json': '007_オーダーコンサル_root',
        'minagine_008_hyouka.json': '008_人事評価_root',
        'jinji_univ_full.json': 'jinji_univ_root',
    }

    all_files = []
    for fname, tag in sources.items():
        data = load(fname)
        files = get_files(data, tag)
        all_files.extend(files)

    # path で重複排除
    seen = set()
    deduped = []
    for f in all_files:
        if f['path'] in seen:
            continue
        seen.add(f['path'])
        deduped.append(f)

    # サマリ出力
    print(f"Total filtered files: {len(deduped)}")
    by_source = {}
    by_ext = {}
    for f in deduped:
        by_source[f['source']] = by_source.get(f['source'], 0) + 1
        by_ext[f['ext']] = by_ext.get(f['ext'], 0) + 1
    print("By source:")
    for k, v in sorted(by_source.items()):
        print(f"  {k}: {v}")
    print("By ext:")
    for k, v in sorted(by_ext.items()):
        print(f"  {k}: {v}")

    # サイズ Top 50 を表示
    deduped_sorted = sorted(deduped, key=lambda x: -x['size'])
    print("\n--- Top 50 by size ---")
    for f in deduped_sorted[:50]:
        size_mb = f['size'] / 1024 / 1024
        print(f"  [{size_mb:.1f}MB] {f['source']} :: {f['name']}")

    with open(OUT, 'w') as f:
        json.dump(deduped, f, ensure_ascii=False, indent=2)
    print(f"\n→ Saved {len(deduped)} files to {OUT}")


if __name__ == '__main__':
    main()
