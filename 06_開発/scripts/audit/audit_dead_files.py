#!/usr/bin/env python3
"""
audit_dead_files.py - Vault 死蔵ファイル検出（月次 audit）

判定軸（4 シグナル + 合計スコア）：
  S1: バージョン併存（v0.x / v1.x が同一 prefix で並ぶ → 古い v が死蔵候補）
  S2: ファイル名死蔵パターン（叩き台 / 補強 / WIP / 引き継ぎ書）
  S3: deploy.sh / verify_deployment.sh / lint_consistency.sh から参照なし
  S4: 90 日以上 mtime 更新なし（auto commit 除外のため git log 参照）

除外：
  - _archive/ _history/ _素材ストック/ 配下
  - SSOT_用語と定義.md / 標準サービス設計 / 09_会社OS / CLAUDE.md
  - MEMORY.md / memory/ 配下

出力：
  - レポート（stdout・user 確認用）
  - candidate_list.json（オプション）

使い方：
  python3 06_開発/scripts/audit/audit_dead_files.py
  python3 06_開発/scripts/audit/audit_dead_files.py --json
  python3 06_開発/scripts/audit/audit_dead_files.py --threshold 2  # スコア 2 以上のみ表示

確立日：2026-05-16（260515 戦略ピボット完走後・初版）
"""

import argparse
import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from datetime import datetime, timedelta

VAULT = Path("/Users/ishiinobuyuki/Documents/Obsidian Vault")

# 除外パターン
EXCLUDE_DIRS = {
    "_archive", "_history", "_素材ストック",
    ".git", "node_modules", ".obsidian",
}
EXCLUDE_FILES = {
    "CLAUDE.md", "README.md", "MEMORY.md",
    "SSOT_用語と定義.md", "SSOT_Gravity_コア主張.md", "SSOT_対話設計_CODE_SCAN.md",
    "SSOT_Engagement指標定義.md", "SSOT_LPコピー言語ガイドライン.md",
    "00_統合タスクマスター_v1.1.md",
}
EXCLUDE_DIR_PREFIXES = ("memory/", "09_会社OS/", "01_石井伸幸/", "04_GrowthFix/04_デイリーログ/")

# 死蔵キーワード（ファイル名）
DEAD_KEYWORDS = ["叩き台", "補強", "WIP", "_仮", "_old", "_bak"]

# バージョン抽出パターン
VERSION_PATTERN = re.compile(r"_v(\d+(?:\.\d+)*)\.md$", re.IGNORECASE)
PREFIX_PATTERN = re.compile(r"^(\d{6}_.+?)_v\d+(?:\.\d+)*\.md$")

# 参照されるべき script ファイル
REFERENCE_SCRIPTS = [
    "06_開発/scripts/deploy/deploy.sh",
    "06_開発/scripts/deploy/verify_deployment.sh",
    "06_開発/scripts/lint/lint_consistency.sh",
]


def is_excluded(path: Path) -> bool:
    """除外判定"""
    rel = path.relative_to(VAULT)
    rel_str = str(rel)
    for prefix in EXCLUDE_DIR_PREFIXES:
        if rel_str.startswith(prefix):
            return True
    for part in path.parts:
        if part in EXCLUDE_DIRS or part.startswith("_archive") or part.startswith("_history"):
            return True
    if path.name in EXCLUDE_FILES:
        return True
    return False


def get_git_mtime(path: Path) -> datetime:
    """git log で最終コミット日時を取得（auto commit 除外用に直近 3 件中の human commit を優先）"""
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%ct", "--", str(path)],
            cwd=VAULT, capture_output=True, text=True, timeout=10,
        )
        ts = result.stdout.strip()
        if ts:
            return datetime.fromtimestamp(int(ts))
    except Exception:
        pass
    return datetime.fromtimestamp(path.stat().st_mtime)


def find_version_groups(all_md_files: list[Path]) -> dict[str, list[Path]]:
    """バージョン併存グループを抽出"""
    groups = defaultdict(list)
    for f in all_md_files:
        m = PREFIX_PATTERN.match(f.name)
        if m:
            prefix = m.group(1)
            # YYMMDD prefix を除いた本体名で集約（日付違いも同じプロジェクトとみなす）
            core = re.sub(r"^\d{6}_", "", prefix)
            groups[core].append(f)
    return {k: sorted(v, key=lambda p: p.name) for k, v in groups.items() if len(v) >= 2}


def extract_version(path: Path) -> tuple:
    """バージョン番号をタプルで返す（比較可能）"""
    m = VERSION_PATTERN.search(path.name)
    if not m:
        return (0,)
    parts = m.group(1).split(".")
    return tuple(int(p) for p in parts)


def is_referenced_by_scripts(filename: str) -> bool:
    """deploy.sh 等から参照されているか"""
    for script in REFERENCE_SCRIPTS:
        script_path = VAULT / script
        if not script_path.exists():
            continue
        try:
            content = script_path.read_text(encoding="utf-8", errors="ignore")
            if filename in content:
                return True
        except Exception:
            pass
    return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="JSON 出力")
    parser.add_argument("--threshold", type=int, default=2, help="廃止スコアしきい値（デフォ 2）")
    args = parser.parse_args()

    # 全 md ファイル収集（除外を適用）
    all_md = []
    for path in VAULT.rglob("*.md"):
        if is_excluded(path):
            continue
        all_md.append(path)

    print(f"[audit_dead_files] スキャン対象: {len(all_md)} ファイル", file=sys.stderr)

    # バージョン併存グループ抽出
    version_groups = find_version_groups(all_md)

    # 各ファイルのスコア計算
    candidates = []
    cutoff_90d = datetime.now() - timedelta(days=90)

    for path in all_md:
        score = 0
        signals = []
        rel = str(path.relative_to(VAULT))

        # S1: バージョン併存（古い v）
        m = PREFIX_PATTERN.match(path.name)
        if m:
            core = re.sub(r"^\d{6}_", "", m.group(1))
            if core in version_groups:
                versions = version_groups[core]
                if len(versions) >= 2:
                    my_v = extract_version(path)
                    max_v = max(extract_version(p) for p in versions)
                    if my_v < max_v:
                        score += 2
                        signals.append(f"S1:旧バージョン(v{'.'.join(map(str, my_v))} < v{'.'.join(map(str, max_v))})")

        # S2: 死蔵キーワード
        for kw in DEAD_KEYWORDS:
            if kw in path.name:
                score += 1
                signals.append(f"S2:キーワード '{kw}'")
                break

        # S3: スクリプト参照なし（00_営業/02_マーケティング/05_プロダクト 配下のみ判定）
        if rel.startswith(("04_GrowthFix/00_営業", "04_GrowthFix/02_マーケティング", "05_プロダクト")):
            if not is_referenced_by_scripts(path.name):
                # 全 md ファイル内の参照もチェック
                ref_count = 0
                for other in all_md:
                    if other == path:
                        continue
                    try:
                        if path.name in other.read_text(encoding="utf-8", errors="ignore"):
                            ref_count += 1
                            if ref_count >= 2:
                                break
                    except Exception:
                        pass
                if ref_count < 2:
                    score += 1
                    signals.append(f"S3:参照{ref_count}件")

        # S4: 90 日以上未更新
        mtime = get_git_mtime(path)
        if mtime < cutoff_90d:
            score += 1
            signals.append(f"S4:90日超未更新({mtime.strftime('%Y-%m-%d')})")

        if score >= args.threshold:
            candidates.append({
                "path": rel,
                "score": score,
                "signals": signals,
                "mtime": mtime.strftime("%Y-%m-%d"),
            })

    # スコア降順ソート
    candidates.sort(key=lambda x: (-x["score"], x["path"]))

    if args.json:
        print(json.dumps(candidates, ensure_ascii=False, indent=2))
        return

    # レポート出力
    print(f"\n📋 死蔵候補レポート（スコア >= {args.threshold}・{len(candidates)} 件）\n")
    print("=" * 80)
    for c in candidates:
        print(f"\n[Score {c['score']}] {c['path']}")
        print(f"  最終更新: {c['mtime']}")
        for s in c["signals"]:
            print(f"  - {s}")

    if not candidates:
        print("\n✅ 死蔵候補なし（しきい値クリア）")

    print(f"\n{'=' * 80}")
    print(f"合計: {len(candidates)} 件")
    print("\n📝 次のアクション:")
    print("  1. 各候補を user 主軸で確認（最後にいつ使ったか・今後使う予定があるか）")
    print("  2. 廃止確定 → _archive_廃止_YYMMDD/ に git mv + README で 1 行廃止理由")
    print("  3. 月次 cron で本スクリプトを定期実行（推奨：月 1 回・週次クローズ時）")


if __name__ == "__main__":
    main()
