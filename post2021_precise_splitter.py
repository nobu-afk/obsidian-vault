#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TerminalHill記事データ 2021-11-27 以降 分割スクリプト
• 1ファイル 500,000 文字以内
• Part16 から連番付与 (既存 Part01-15 を維持)
• 元ファイル: terminalhill_clean_all_articles_fixed.txt
"""

import re
import os
from datetime import datetime

THRESHOLD_DATE = datetime(2021, 11, 26)  # これより後の日付を抽出
INPUT_FILE = "terminalhill_clean_all_articles_fixed.txt"
OUTPUT_PREFIX = "terminalhill_500K"
START_PART_NUM = 16
MAX_CHARS = 500_000


def extract_articles(content: str):
    """記事単位で抽出し、日付フィルタを通す"""
    pattern = r'(URL: https://terminalhill\.jugem\.jp/\?eid=\d+.*?)(?=URL: https://terminalhill\.jugem\.jp/\?eid=\d+|$)'
    raw_articles = re.findall(pattern, content, re.DOTALL)

    filtered = []
    date_re = re.compile(r'日付: ([0-9]{4})[-.]([0-9]{2})[-.]([0-9]{2})')

    for art in raw_articles:
        m = date_re.search(art)
        if not m:
            continue  # 日付取れないものは除外
        y, mo, d = map(int, m.groups())
        art_date = datetime(y, mo, d)
        if art_date > THRESHOLD_DATE:
            filtered.append(art)
    return filtered


def split_and_save(articles):
    part_num = START_PART_NUM
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    header_tpl = """TerminalHill記事データセット - Part {part:02d}
分割日時: {now}
最大文字数: {max:,}文字
================================================================================\n\n"""

    buf = header_tpl.format(part=part_num, now=datetime.now().strftime('%Y年%m月%d日 %H:%M:%S'), max=MAX_CHARS)
    buf_chars = len(buf)
    arts_in_file = 0

    stats = []  # list of dicts

    for art in articles:
        art_chars = len(art)
        if buf_chars + art_chars + 2 <= MAX_CHARS:  # +2 for \n\n
            buf += art + "\n\n"
            buf_chars += art_chars + 2
            arts_in_file += 1
        else:
            # save current
            filename = f"{OUTPUT_PREFIX}_part{part_num:02d}_{timestamp}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(buf)
            stats.append({'filename': filename, 'articles': arts_in_file, 'chars': buf_chars})
            print(f"✅ {filename}: {arts_in_file}記事, {buf_chars:,}文字")

            # reset for next part
            part_num += 1
            buf = header_tpl.format(part=part_num, now=datetime.now().strftime('%Y年%m月%d日 %H:%M:%S'), max=MAX_CHARS)
            buf += art + "\n\n"
            buf_chars = len(buf)
            arts_in_file = 1
    # save last
    if arts_in_file > 0:
        filename = f"{OUTPUT_PREFIX}_part{part_num:02d}_{timestamp}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(buf)
        stats.append({'filename': filename, 'articles': arts_in_file, 'chars': buf_chars})
        print(f"✅ {filename}: {arts_in_file}記事, {buf_chars:,}文字")

    # summary
    total_articles = sum(s['articles'] for s in stats)
    total_chars = sum(s['chars'] for s in stats)
    print("\n=== 分割完了 ===")
    print(f"総ファイル数: {len(stats)}")
    print(f"総記事数: {total_articles:,}")
    print(f"総文字数: {total_chars:,}")
    for s in stats:
        size_mb = round(s['chars'] / 1024 / 1024, 2)
        print(f"  {s['filename']}: {s['articles']}記事, {s['chars']:,}文字 ({size_mb}MB)")


if __name__ == "__main__":
    if not os.path.exists(INPUT_FILE):
        print(f"❌ 入力ファイルが見つかりません: {INPUT_FILE}")
        exit(1)

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    arts = extract_articles(content)
    print(f"フィルタ後記事数: {len(arts):,}件")
    if not arts:
        print("対象記事が見つかりません")
        exit(1)
    split_and_save(arts) 