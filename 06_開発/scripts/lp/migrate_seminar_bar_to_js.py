#!/usr/bin/env python3
"""
migrate_seminar_bar_to_js.py
全LPのインライン LIVE WEBINAR バー HTML を削除し、JSスクリプトタグに置換する。

実行:
  python3 06_開発/scripts/migrate_seminar_bar_to_js.py [--dry-run]

動作:
  1. <body> 直後の <!-- LIVE WEBINAR... --> + <section class="next-seminar-bar">...</section>
     を検出して削除
  2. </head> 直前に <script src="https://growthfix.jp/assets/js/seminar-bar.js" defer></script> を挿入
  3. 既に script タグがある場合はスキップ
  4. 変更前後の差分件数を表示
"""

import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
LP_DIR = PROJECT_ROOT / "05_プロダクト"

DRY_RUN = "--dry-run" in sys.argv

# 19 LP の対象一覧（lint 対象と整合）
TARGETS = [
    "top_本番/index.html",
    "Gravity/LP/index.html",
    "GravityCode/LP/index.html",
    "GravityCode/診断_executive_本番/index.html",
    "GravityBlueprint/LP/index.html",
    "GravityBlueprint/診断_本番/index.html",
    "GravityCoaching/LP/index.html",
    "GravityShift/LP/index.html",
    "GravityOrbit/LP/index.html",
    "service_本番/index.html",
    "profile_本番/index.html",
    "achievement_本番/index.html",
    "contact_本番/index.html",
    "privacy-policy_本番/index.html",
    "news_本番/index.html",
    "news_本番/site-renewal/index.html",
    "news_本番/gravity-release/index.html",
    "knowledge_本番/index.html",
    "whitepaper_optin_本番/index.html",
]

SCRIPT_TAG = '<script src="https://growthfix.jp/assets/js/seminar-bar.js?v=20260429a" defer></script>'

# インライン LIVE WEBINAR バーを検出する正規表現
# コメント "<!-- LIVE WEBINAR..." 含めてから </section> までを丸ごと削除
INLINE_BAR_PATTERN = re.compile(
    r'\n?\s*<!--\s*LIVE WEBINAR.*?-->\s*\n?'
    r'\s*<section\s+class="next-seminar-bar".*?</section>\s*\n?',
    re.DOTALL,
)

# section だけのバージョン（コメントなし）も念のため
INLINE_BAR_NO_COMMENT_PATTERN = re.compile(
    r'\n?\s*<section\s+class="next-seminar-bar".*?</section>\s*\n?',
    re.DOTALL,
)

removed_count = 0
script_added_count = 0
skipped_count = 0
error_count = 0

print("📝 LIVE WEBINAR バー JS 化マイグレーション")
print(f"   対象: {len(TARGETS)} LP")
print(f"   モード: {'DRY-RUN' if DRY_RUN else '本番実行'}")
print()

for rel_path in TARGETS:
    file_path = LP_DIR / rel_path

    if not file_path.exists():
        print(f"  ❌ NOT FOUND: {rel_path}")
        error_count += 1
        continue

    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"  ❌ READ FAIL ({rel_path}): {e}")
        error_count += 1
        continue

    original = content

    # 1. インラインバーを削除（コメント付き優先）
    new_content, n1 = INLINE_BAR_PATTERN.subn("\n", content)
    if n1 == 0:
        # コメントなしバージョンも試す
        new_content, n1 = INLINE_BAR_NO_COMMENT_PATTERN.subn("\n", content)

    bar_removed = n1 > 0

    # 2. script タグを </head> 直前に挿入（既にあればスキップ）
    if "seminar-bar.js" in new_content:
        script_added = False
    elif "</head>" in new_content:
        new_content = new_content.replace(
            "</head>",
            f"  {SCRIPT_TAG}\n</head>",
            1,
        )
        script_added = True
    else:
        script_added = False

    if new_content == original:
        print(f"  ⏭  SKIP (no change): {rel_path}")
        skipped_count += 1
        continue

    if bar_removed:
        removed_count += 1
    if script_added:
        script_added_count += 1

    if DRY_RUN:
        status = []
        if bar_removed:
            status.append("バー削除✓")
        if script_added:
            status.append("script追加✓")
        print(f"  📋 [dry] {rel_path}: {' / '.join(status)}")
    else:
        try:
            file_path.write_text(new_content, encoding="utf-8")
            status = []
            if bar_removed:
                status.append("バー削除✓")
            if script_added:
                status.append("script追加✓")
            print(f"  ✅ {rel_path}: {' / '.join(status)}")
        except Exception as e:
            print(f"  ❌ WRITE FAIL ({rel_path}): {e}")
            error_count += 1

print()
print("📊 集計")
print(f"  バー削除: {removed_count} ファイル")
print(f"  script タグ追加: {script_added_count} ファイル")
print(f"  スキップ: {skipped_count} ファイル")
print(f"  エラー: {error_count} ファイル")

if DRY_RUN:
    print()
    print("（dry-run 完了。本番反映するには --dry-run を外して再実行）")
