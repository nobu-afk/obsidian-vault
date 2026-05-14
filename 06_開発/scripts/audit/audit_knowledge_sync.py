#!/usr/bin/env python3
"""audit_knowledge_sync.py — memory + SSOT + 会社OS の参照リンク整合性検証

検出項目:
  [1] 死リンク       : SSOT/会社OS/CLAUDE.md で参照される memory file が実在しない
  [2] 孤児 memory    : MEMORY.md にエントリがない memory file（type=user は除外可）
  [3] frontmatter    : memory の name/description/type が欠損 or 不正
  [4] 索引重複       : MEMORY.md に同じ memory file への複数エントリ
  [5] 逆参照不在     : feedback/project memory が会社OS or SSOT から参照されていない

使い方:
  python3 06_開発/scripts/audit_knowledge_sync.py            # 検証実行
  python3 06_開発/scripts/audit_knowledge_sync.py --json     # JSON 出力
  python3 06_開発/scripts/audit_knowledge_sync.py --strict   # 警告も exit 1
"""
import argparse
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

WORKERS = 16

VAULT = Path("/Users/ishiinobuyuki/Documents/Obsidian Vault")
MEMORY_DIR = Path(
    "/Users/ishiinobuyuki/.claude/projects/-Users-ishiinobuyuki-Documents-Obsidian-Vault/memory"
)
MEMORY_INDEX = MEMORY_DIR / "MEMORY.md"

SCAN_TARGETS = [
    VAULT / "CLAUDE.md",
    VAULT / "09_会社OS",
    VAULT / "05_プロダクト/_共通",
]

RED, YEL, GRN, NC = "\033[0;31m", "\033[0;33m", "\033[0;32m", "\033[0m"


def list_memory_files() -> dict[str, Path]:
    """memory dir 直下の *.md（MEMORY.md 除く）を {filename: path} で返す"""
    files = {}
    for p in MEMORY_DIR.glob("*.md"):
        if p.name == "MEMORY.md":
            continue
        files[p.name] = p
    return files


def parse_frontmatter(path: Path) -> dict:
    """frontmatter dict を返す（無ければ {}）"""
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    return fm


def find_memory_refs_in_text(text: str) -> set[str]:
    """text 中で参照されている memory file 名を抽出（基本ファイル名のみ）"""
    refs = set()
    # パターン1: memory/feedback_xxx.md or feedback_xxx.md（type prefix 付き拡張子付き）
    for m in re.finditer(r"\b(feedback|project|reference|user)_[\w\-.]+\.md\b", text):
        refs.add(m.group(0))
    # パターン2: 拡張子なし（CLAUDE.md / culture.md 内で見かける）
    for m in re.finditer(
        r"`(?:memory/)?((?:feedback|project|reference|user)_[\w\-]+)`", text
    ):
        refs.add(m.group(1) + ".md")
    return refs


def _scan_one_file(path: Path) -> tuple[Path, set[str]]:
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return path, set()
    return path, find_memory_refs_in_text(text)


def scan_external_refs() -> dict[str, set[Path]]:
    """SSOT/会社OS/CLAUDE.md で参照されている memory ref → 参照元 path の dict"""
    all_paths: list[Path] = []
    for target in SCAN_TARGETS:
        if target.is_file():
            all_paths.append(target)
        else:
            all_paths.extend(target.rglob("*.md"))

    refs: dict[str, set[Path]] = {}
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        for p, file_refs in ex.map(_scan_one_file, all_paths):
            for ref in file_refs:
                refs.setdefault(ref, set()).add(p)
    return refs


def parse_index_entries() -> dict[str, list[int]]:
    """MEMORY.md の memory pointer entry を {filename: [line_numbers]} で返す"""
    entries: dict[str, list[int]] = {}
    text = MEMORY_INDEX.read_text(encoding="utf-8")
    for i, line in enumerate(text.splitlines(), 1):
        for m in re.finditer(r"\(([\w\-.]+\.md)\)", line):
            entries.setdefault(m.group(1), []).append(i)
        # 拡張子なしリンク（既存索引で散在）
        for m in re.finditer(r"\[([^\]]+)\]\(((?:feedback|project|reference|user)_[\w\-]+)\)", line):
            entries.setdefault(m.group(2) + ".md", []).append(i)
    return entries


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--strict", action="store_true", help="警告も exit 1")
    args = ap.parse_args()

    findings = {"high": [], "medium": [], "low": []}

    memory_files = list_memory_files()
    external_refs = scan_external_refs()
    index_entries = parse_index_entries()

    # [1] 死リンク：参照されているが実在しない memory file
    for ref, sources in external_refs.items():
        if ref not in memory_files:
            for src in sorted(sources):
                rel = src.relative_to(VAULT) if src.is_relative_to(VAULT) else src
                findings["high"].append(
                    {"type": "dead_link", "ref": ref, "source": str(rel)}
                )

    # [2] 孤児 memory：MEMORY.md にエントリがない
    for name in sorted(memory_files):
        if name not in index_entries and not name.startswith("user_"):
            findings["medium"].append({"type": "orphan", "file": name})

    # [3] frontmatter 整合
    sorted_items = sorted(memory_files.items())
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        fms = list(ex.map(lambda kv: parse_frontmatter(kv[1]), sorted_items))
    for (name, _), fm in zip(sorted_items, fms):
        missing = [k for k in ("name", "description", "type") if not fm.get(k)]
        if missing:
            findings["medium"].append(
                {"type": "frontmatter_missing", "file": name, "fields": missing}
            )
        elif fm.get("type") not in ("feedback", "project", "reference", "user"):
            findings["medium"].append(
                {"type": "frontmatter_type_invalid", "file": name, "value": fm.get("type")}
            )

    # [4] 索引重複
    for name, lines in index_entries.items():
        if len(lines) > 1:
            findings["low"].append(
                {"type": "duplicate_index", "file": name, "lines": lines}
            )

    # [5] 逆参照不在：feedback/project memory が外部から一切参照されていない（孤立警告）
    for name, path in sorted(memory_files.items()):
        if not (name.startswith("feedback_") or name.startswith("project_")):
            continue
        if name in external_refs:
            continue
        # MEMORY.md からの参照だけだと孤立扱い（feedback/project は本来運用 MD から参照されるべき）
        findings["low"].append({"type": "no_back_ref", "file": name})

    if args.json:
        print(json.dumps(findings, ensure_ascii=False, indent=2))
        sys.exit(1 if (findings["high"] or (args.strict and findings["medium"])) else 0)

    # 人間可読出力
    print(f"📚 memory file 数: {len(memory_files)}")
    print(f"📑 MEMORY.md エントリ数: {sum(len(v) for v in index_entries.values())}")
    print(f"🔗 外部参照される memory ref 数: {len(external_refs)}")
    print()

    high_n = len(findings["high"])
    med_n = len(findings["medium"])
    low_n = len(findings["low"])

    if high_n:
        print(f"{RED}🔴 HIGH: {high_n} 件{NC}")
        # 死リンクを ref ごとにグループ化
        by_ref: dict[str, list[str]] = {}
        for f in findings["high"]:
            by_ref.setdefault(f["ref"], []).append(f["source"])
        for ref, srcs in sorted(by_ref.items()):
            print(f"  [dead_link] {ref}")
            for s in srcs[:3]:
                print(f"     ← {s}")
            if len(srcs) > 3:
                print(f"     ← ... 他 {len(srcs) - 3} 箇所")
        print()

    if med_n:
        print(f"{YEL}🟡 MEDIUM: {med_n} 件{NC}")
        orphans = [f["file"] for f in findings["medium"] if f["type"] == "orphan"]
        fm_missing = [f for f in findings["medium"] if f["type"] == "frontmatter_missing"]
        fm_invalid = [f for f in findings["medium"] if f["type"] == "frontmatter_type_invalid"]
        if orphans:
            print(f"  [orphan] MEMORY.md エントリなし: {len(orphans)} 件")
            for o in orphans[:5]:
                print(f"     - {o}")
            if len(orphans) > 5:
                print(f"     - ... 他 {len(orphans) - 5} 件")
        if fm_missing:
            print(f"  [frontmatter_missing] 必須フィールド欠損: {len(fm_missing)} 件")
            for f in fm_missing[:3]:
                print(f"     - {f['file']} (missing: {','.join(f['fields'])})")
        if fm_invalid:
            print(f"  [frontmatter_type_invalid] type 値不正: {len(fm_invalid)} 件")
            for f in fm_invalid[:3]:
                print(f"     - {f['file']} (value: {f['value']})")
        print()

    if low_n:
        print(f"🔵 LOW: {low_n} 件")
        dup = [f for f in findings["low"] if f["type"] == "duplicate_index"]
        no_back = [f for f in findings["low"] if f["type"] == "no_back_ref"]
        if dup:
            print(f"  [duplicate_index] MEMORY.md 重複エントリ: {len(dup)} 件")
            for d in dup[:3]:
                print(f"     - {d['file']} (lines: {d['lines']})")
        if no_back:
            print(f"  [no_back_ref] 会社OS/SSOT/CLAUDE.md から逆参照なし: {len(no_back)} 件")
            for n in no_back[:5]:
                print(f"     - {n['file']}")
            if len(no_back) > 5:
                print(f"     - ... 他 {len(no_back) - 5} 件")
        print()

    print("=" * 50)
    if high_n == 0 and med_n == 0 and low_n == 0:
        print(f"{GRN}✅ 全チェック通過{NC}")
        sys.exit(0)
    elif high_n == 0:
        print(f"{YEL}⚠ 警告 {med_n + low_n} 件（HIGH なし）{NC}")
        sys.exit(1 if args.strict else 0)
    else:
        print(f"{RED}❌ HIGH {high_n} 件 / MEDIUM {med_n} 件 / LOW {low_n} 件{NC}")
        sys.exit(1)


if __name__ == "__main__":
    main()
