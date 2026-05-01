#!/usr/bin/env python3
"""
inject_ab_test_script.py
全 19 LP の <head> に ab-test.js の script タグを seminar-bar.js より先に挿入する。

実行:
  python3 06_開発/scripts/inject_ab_test_script.py [--dry-run]

動作:
  - seminar-bar.js の script タグを検出
  - その直前に ab-test.js の script タグを挿入
  - 既に ab-test.js の script タグがあればスキップ
"""

import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
LP_DIR = PROJECT_ROOT / "05_プロダクト"

DRY_RUN = "--dry-run" in sys.argv

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

AB_TEST_TAG = '<script src="https://growthfix.jp/assets/js/ab-test.js?v=20260429a" defer></script>'

# seminar-bar.js の script タグを検出する正規表現（version 違いも許容）
SEMINAR_BAR_PATTERN = re.compile(
    r'(\s*)<script\s+src="https://growthfix\.jp/assets/js/seminar-bar\.js[^"]*"\s+defer>\s*</script>'
)

added = 0
skipped = 0
errors = 0

print(f"📝 ab-test.js script 挿入（{'DRY-RUN' if DRY_RUN else '本番実行'}）")
print(f"   対象: {len(TARGETS)} LP")
print()

for rel_path in TARGETS:
    file_path = LP_DIR / rel_path

    if not file_path.exists():
        print(f"  ❌ NOT FOUND: {rel_path}")
        errors += 1
        continue

    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"  ❌ READ FAIL ({rel_path}): {e}")
        errors += 1
        continue

    if "ab-test.js" in content:
        print(f"  ⏭  SKIP（既に ab-test.js あり）: {rel_path}")
        skipped += 1
        continue

    match = SEMINAR_BAR_PATTERN.search(content)
    if not match:
        print(f"  ❌ seminar-bar.js script not found: {rel_path}")
        errors += 1
        continue

    # seminar-bar.js の前にインデントを揃えて挿入
    indent = match.group(1)
    seminar_tag = match.group(0).strip()
    replacement = f"{indent}{AB_TEST_TAG}\n  {seminar_tag}"
    new_content = content[:match.start()] + replacement + content[match.end():]

    if DRY_RUN:
        print(f"  📋 [dry] {rel_path}: ab-test.js 追加予定")
    else:
        try:
            file_path.write_text(new_content, encoding="utf-8")
            print(f"  ✅ {rel_path}: ab-test.js 追加完了")
            added += 1
        except Exception as e:
            print(f"  ❌ WRITE FAIL ({rel_path}): {e}")
            errors += 1

print()
print("📊 集計")
print(f"  追加: {added}")
print(f"  スキップ: {skipped}")
print(f"  エラー: {errors}")
