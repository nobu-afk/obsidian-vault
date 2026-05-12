#!/usr/bin/env python3
"""
audit_wp_refs.py
WordPress 撤退後の漏れ検出。HTML/CSS/JS/PHP 配下の wp-content / wp-includes / wp-json /
wp-admin / wp-login / wp-cron 参照を列挙する。

実行:
  python3 06_開発/scripts/audit_wp_refs.py                # 人間用レポート
  python3 06_開発/scripts/audit_wp_refs.py --json         # JSON 出力
  python3 06_開発/scripts/audit_wp_refs.py --strict       # 1 件でも検出で exit 1（CI 用）

スキャン対象:
  - 05_プロダクト/**/*.html (本番 LP / corporate / 診断 UI)
  - 05_プロダクト/**/*.css
  - 05_プロダクト/**/*.js
  - 05_プロダクト/**/*.php
  - _assets/**

除外:
  - _archive 配下
  - .git 配下
  - node_modules 配下
"""

import argparse
import json
import re
import sys
from pathlib import Path

VAULT_ROOT = Path(__file__).resolve().parents[2]

SCAN_DIRS = [
    VAULT_ROOT / "05_プロダクト",
    VAULT_ROOT / "_assets",
]

SCAN_SUFFIXES = {".html", ".htm", ".css", ".js", ".php"}

EXCLUDE_PARTS = {"_archive", ".git", "node_modules", "_backup"}

PATTERNS = [
    ("wp-content", re.compile(r"wp-content(?:/[^\s\"'<>)]*)?")),
    ("wp-includes", re.compile(r"wp-includes(?:/[^\s\"'<>)]*)?")),
    ("wp-json", re.compile(r"/wp-json/[^\s\"'<>)]*")),
    ("wp-admin", re.compile(r"/wp-admin/[^\s\"'<>)]*")),
    ("wp-login", re.compile(r"wp-login\.php[^\s\"'<>)]*")),
    ("wp-cron", re.compile(r"wp-cron\.php[^\s\"'<>)]*")),
]


def should_scan(path: Path) -> bool:
    if path.suffix.lower() not in SCAN_SUFFIXES:
        return False
    for part in path.parts:
        if part in EXCLUDE_PARTS:
            return False
    return True


def scan_file(path: Path):
    findings = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return findings
    line_starts = None
    for kind, pattern in PATTERNS:
        for match in pattern.finditer(text):
            if line_starts is None:
                line_starts = [0]
                for i, ch in enumerate(text):
                    if ch == "\n":
                        line_starts.append(i + 1)
            offset = match.start()
            lineno = _bisect_line(line_starts, offset)
            line_end = text.find("\n", offset)
            line = text[line_starts[lineno - 1]: line_end if line_end != -1 else len(text)]
            findings.append({
                "file": str(path.relative_to(VAULT_ROOT)),
                "line": lineno,
                "kind": kind,
                "match": match.group(0),
                "context": line.strip()[:160],
            })
    return findings


def _bisect_line(line_starts, offset):
    lo, hi = 0, len(line_starts) - 1
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if line_starts[mid] <= offset:
            lo = mid
        else:
            hi = mid - 1
    return lo + 1


def collect_targets():
    files = []
    for root in SCAN_DIRS:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file() and should_scan(path):
                files.append(path)
    return files


def main():
    parser = argparse.ArgumentParser(description="WordPress 参照の漏れ検出")
    parser.add_argument("--json", action="store_true", help="JSON で出力")
    parser.add_argument("--strict", action="store_true",
                        help="1 件でも検出されたら exit 1（CI 用）")
    args = parser.parse_args()

    files = collect_targets()
    all_findings = []
    for path in files:
        all_findings.extend(scan_file(path))

    if args.json:
        json.dump({
            "scanned_files": len(files),
            "findings_count": len(all_findings),
            "findings": all_findings,
        }, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    else:
        print(f"WP 参照監査レポート")
        print(f"スキャン対象: {len(files)} ファイル")
        print(f"検出件数: {len(all_findings)} 件")
        print()
        if not all_findings:
            print("✅ WP 参照ゼロ。撤退漏れなし。")
        else:
            by_file = {}
            for f in all_findings:
                by_file.setdefault(f["file"], []).append(f)
            for fname in sorted(by_file):
                items = by_file[fname]
                print(f"❌ {fname}  ({len(items)} 件)")
                for it in items:
                    print(f"   L{it['line']:>4} [{it['kind']}] {it['match']}")
                print()

    if args.strict and all_findings:
        sys.exit(1)


if __name__ == "__main__":
    main()
