#!/usr/bin/env python3
"""
LP 社内用語ゼロ原則チェッカ（260512 新規）

SSOT: 09_会社OS/公開/ガイドライン/design.md §LP 社内用語ゼロ原則

対象 LP の本文・FAQ・サービスの進め方欄に、内部 KPI 数値・社内略称・運用語が
混入していないか検出する。THEORY セクション（<section id="theory">...</section>）
内は学術濃度層として例外扱い。

Usage:
  python3 06_開発/scripts/lint_lp_internal_terms.py
  python3 06_開発/scripts/lint_lp_internal_terms.py --json   # JSON 出力
  python3 06_開発/scripts/lint_lp_internal_terms.py path/to/index.html  # 個別実行

Exit code:
  0: HIT ゼロ
  1: HIT あり
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Iterable

# ─────────────────────────────────────────────────────────────
# 検出パターン定義
# ─────────────────────────────────────────────────────────────

PATTERNS: list[tuple[str, str, str, str]] = [
    # (severity, category, regex, suggested replacement hint)

    # 🔴 内部 KPI 数値達成表現
    ("HIGH", "内部 KPI 数値", r"継続率\s*\d+\s*%[^」）]*", "「Orbit で伴走を継続される経営者も多数」等の定性表現に"),
    ("HIGH", "内部 KPI 数値", r"完成度\s*\d+\s*%\s*→\s*\d+\s*%", "「N ヶ月で〇〇な状態をつくる」等の定性表現に"),
    ("HIGH", "内部 KPI 数値", r"翻訳度\s*\d+\s*%\s*→\s*\d+\s*%", "「社長の引力で次の 1 名を採れる状態」等に"),
    ("HIGH", "内部 KPI 数値", r"発議\s*月\s*\d+\s*→\s*月\s*\d+", "「幹部が自律発議する組織」等の定性表現に"),
    ("HIGH", "内部 KPI 数値", r"エンゲージメント\s*\d+\.\d+\s*→\s*\d+\.\d+", "「優秀層が辞めない組織」等の定性表現に"),
    ("HIGH", "内部 KPI 数値", r"承諾実績\s*\d+\s*件以上", "「実装が組織に根付いた状態」等に"),
    ("HIGH", "内部 KPI 数値", r"社長依存度\s*\d+\s*%\s*→\s*\d+\s*%", "「社長の手離れが進む状態」等の定性表現に"),

    # 🔴 社内略称比較
    ("HIGH", "社内略称比較", r"[RC]\s*の\s*\d+\s*%[^」）]*", "比較表現自体を削除"),

    # 🔴 社内略称（参謀名でない）
    ("HIGH", "社内略称", r"\bC\s*中核\b", "「中核プログラム」に"),
    ("HIGH", "社内略称", r"\bR\s*中核\b", "「中核プログラム」に"),
    # Shift R/C/Full は内部運用名・LP 上では「Gravity Shift」または「Recruit/Cultivate」を使う
    ("HIGH", "社内略称", r"\bShift\s+R\b", "「Gravity Recruit」または「Gravity Shift」に"),
    ("HIGH", "社内略称", r"\bShift\s+C\b", "「Gravity Cultivate」または「Gravity Shift」に"),
    ("HIGH", "社内略称", r"\bShift\s+Full\b", "「Gravity Shift」に"),

    # 🟡 内部運用語（思想層 SSOT で運用するもの）
    ("MEDIUM", "内部運用語", r"minimal LP", "LP には書かない（思想層 SSOT で運用）"),
    ("MEDIUM", "内部運用語", r"funnel 内側型", "LP には書かない"),
    ("MEDIUM", "内部運用語", r"Push 型 minimal", "LP には書かない"),
    ("MEDIUM", "内部運用語", r"Pull 型 minimal", "LP には書かない"),
    ("MEDIUM", "内部運用語", r"二段運用", "LP には書かない"),
    ("MEDIUM", "内部運用語", r"接続装置", "LP には書かない（思想層用語）"),
    ("MEDIUM", "内部運用語", r"信用装置", "LP には書かない"),
    ("MEDIUM", "内部運用語", r"言語マップ", "LP には書かない"),
    ("MEDIUM", "内部運用語", r"転換装置", "LP には書かない"),
    ("MEDIUM", "内部運用語", r"ハーネスエンジニアリング", "LP には書かない"),

    # 🟡 内部分類コード（FAQ レベルでの混入チェック）
    ("MEDIUM", "内部分類", r"\b8 項目スコア\b", "「経営者の現状ヒアリング」等の自然語に"),
    ("MEDIUM", "内部分類", r"\b9 マス診断\b", "「Why × 才能 × 偏愛 ヒアリング」等の自然語に"),
]

# 例外パス（ホワイトリスト）
WHITELIST_PATHS = {
    # （必要に応じて追加）
}

# 検査対象 LP（正本ディレクトリ）
TARGET_LPS = [
    "GravityRecruit/LP/index.html",
    "GravityCultivate/LP/index.html",
    "GravityCoaching/LP/index.html",
    "GravityCode/LP/index.html",
    "GravityScan/LP/index.html",
    "GravityOrbit/LP/index.html",
    "GravityShift/LP/index.html",
    "Gravity/LP/index.html",
    "top_本番/index.html",
    "service_本番/index.html",
    "profile_本番/index.html",
]


# ─────────────────────────────────────────────────────────────
# 検査ロジック
# ─────────────────────────────────────────────────────────────

THEORY_SECTION_RE = re.compile(r'<section[^>]*id="theory"', re.IGNORECASE)
SCRIPT_SECTION_RE = re.compile(r'<script[^>]*>.*?</script>', re.DOTALL | re.IGNORECASE)
COMMENT_RE = re.compile(r'<!--.*?-->', re.DOTALL)


def find_theory_range(content: str) -> tuple[int, int]:
    """THEORY セクションの (start, end) を返す。なければ (-1, -1)。"""
    m = THEORY_SECTION_RE.search(content)
    if not m:
        return (-1, -1)
    start = m.start()
    end = content.find("</section>", start)
    if end == -1:
        return (-1, -1)
    return (start, end + len("</section>"))


def is_inside_excluded(pos: int, ranges: list[tuple[int, int]]) -> bool:
    """指定位置が除外範囲（THEORY / script / comment）に入っているか。"""
    return any(s <= pos < e for s, e in ranges)


def collect_excluded_ranges(content: str) -> list[tuple[int, int]]:
    ranges: list[tuple[int, int]] = []
    th = find_theory_range(content)
    if th[0] >= 0:
        ranges.append(th)
    for m in SCRIPT_SECTION_RE.finditer(content):
        ranges.append((m.start(), m.end()))
    for m in COMMENT_RE.finditer(content):
        ranges.append((m.start(), m.end()))
    return ranges


def lint_file(path: Path) -> list[dict]:
    """1 ファイルを検査して HIT リストを返す。"""
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        content = f.read()

    excluded = collect_excluded_ranges(content)
    hits: list[dict] = []
    for severity, category, pattern, hint in PATTERNS:
        for m in re.finditer(pattern, content):
            if is_inside_excluded(m.start(), excluded):
                continue
            line_no = content[:m.start()].count("\n") + 1
            line_start = content.rfind("\n", 0, m.start()) + 1
            line_end = content.find("\n", m.end())
            line_text = content[line_start:line_end if line_end != -1 else None].strip()
            hits.append({
                "severity": severity,
                "category": category,
                "line": line_no,
                "match": m.group(0),
                "hint": hint,
                "context": line_text[:140],
            })
    return hits


def render_text(results: dict[str, list[dict]]) -> str:
    """人間用テキスト出力。"""
    lines: list[str] = []
    total_high = 0
    total_med = 0
    for path, hits in results.items():
        if not hits:
            continue
        lines.append(f"\n========== {path} ==========")
        seen: set[tuple[int, str]] = set()
        for h in sorted(hits, key=lambda x: (x["line"], x["match"])):
            key = (h["line"], h["match"])
            if key in seen:
                continue
            seen.add(key)
            mark = "🔴" if h["severity"] == "HIGH" else "🟡"
            if h["severity"] == "HIGH":
                total_high += 1
            else:
                total_med += 1
            lines.append(f"  {mark} L{h['line']:>3} [{h['category']}] {h['match']}")
            lines.append(f"        ↳ {h['context'][:100]}")
            lines.append(f"        → 提案: {h['hint']}")

    if total_high == 0 and total_med == 0:
        lines.append("\n✅ 全 LP で社内用語ゼロ通過（HIT 0 件）")
    else:
        lines.append("")
        lines.append("=" * 60)
        lines.append(f"📊 検出サマリ：HIGH {total_high} 件 ／ MEDIUM {total_med} 件")
        lines.append("=" * 60)
        lines.append("📋 推奨アクション：")
        lines.append("  1. HIGH（内部 KPI / 略称）は必ず削除または定性表現に置換")
        lines.append("  2. MEDIUM（運用語）は思想層 SSOT に格納し LP からは除去")
        lines.append("  3. 詳細は営業提案書 v0.3 に展開：")
        lines.append("     04_GrowthFix/02_マーケティング/260509_GravityRC_営業提案_サービス資料_v0.3.md")
        lines.append("  4. SSOT: 09_会社OS/公開/ガイドライン/design.md §LP 社内用語ゼロ原則")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="LP 社内用語ゼロ原則チェッカ")
    parser.add_argument("paths", nargs="*", help="検査対象ファイル（省略時は全 LP）")
    parser.add_argument("--json", action="store_true", help="JSON 出力")
    parser.add_argument("--vault-root", default=None, help="Vault ルート（省略時は自動推定）")
    args = parser.parse_args()

    if args.vault_root:
        vault = Path(args.vault_root).resolve()
    else:
        # スクリプトの位置から推定
        vault = Path(__file__).resolve().parent.parent.parent

    products_root = vault / "05_プロダクト"

    if args.paths:
        targets = [Path(p).resolve() for p in args.paths]
    else:
        targets = [products_root / lp for lp in TARGET_LPS]

    results: dict[str, list[dict]] = {}
    for path in targets:
        rel = str(path.relative_to(vault)) if vault in path.parents or vault == path.parent else str(path)
        results[rel] = lint_file(path)

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print(render_text(results))

    has_high = any(any(h["severity"] == "HIGH" for h in hits) for hits in results.values())
    return 1 if has_high else 0


if __name__ == "__main__":
    sys.exit(main())
