#!/usr/bin/env python3
"""Phase 3 重要ファイル選定スクリプト

各社の構造 JSON から、分析対象として高インパクトな
ファイルを抽出する（既深掘り 9 除外 / 機密性高すぎ除外 /
xlsx/pptx/pdf/docx に限定）。
"""
from __future__ import annotations

import json
from pathlib import Path

CACHE = Path("/Users/ishiinobuyuki/Documents/Obsidian Vault/06_開発/scripts/dropbox/_structure_cache")

# 既深掘り済 9 ファイル名（重複回避）
ALREADY_ANALYZED = {
    "220630_【admin】スカウト文章等について.xlsx",
    "面接官研修.pptx",
    "220701_wevox コメント精査 SS.xlsx",
    "入社後面談【中途】.xlsx",
    "220701_バリュー策定ワークショップ.pptx",
    "220822_退職・社員アンケート（回答）.xlsx",
    "220901_リファラル50（運用フロー）.pdf",
    "220912_prj-bo改善16.pptx",
    "220912_20211102_人事分科会用.pptx",
}

# 機密性高すぎパスパターン（除外）
SENSITIVE_PATH_KEYWORDS = [
    "源泉", "給与計算", "賞与計算", "退職金計算",
    "雇用契約書", "労働条件通知書",
    "住所", "生年月日", "履歴書", "職務経歴書",
    "労務リスト", "従業員名簿",
    "メールアドレス一覧",
    "勤怠データ",
]

# 機密性高すぎ拡張子
EXCLUDE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".heic", ".mp4", ".mov",
                       ".zip", ".csv", ".numbers", ".pages", ".key",
                       ".eml", ".msg", ".log", ".txt"}

# 分析対象拡張子
TARGET_EXTENSIONS = {".xlsx", ".pptx", ".pdf", ".docx", ".doc", ".xls", ".ppt"}


def load_structure(filename: str) -> list[dict]:
    p = CACHE / filename
    with p.open() as f:
        return json.load(f)


def is_sensitive(path: str, name: str) -> bool:
    pn = f"{path}/{name}"
    for kw in SENSITIVE_PATH_KEYWORDS:
        if kw in pn:
            return True
    return False


def is_target(entry: dict) -> bool:
    if entry.get("type") != "file":
        return False
    if entry["name"] in ALREADY_ANALYZED:
        return False
    ext = entry.get("extension", "")
    if ext in EXCLUDE_EXTENSIONS:
        return False
    if ext not in TARGET_EXTENSIONS:
        return False
    if is_sensitive(entry.get("path", ""), entry["name"]):
        return False
    # サイズ下限: 50KB（テンプレ重視・スカスカファイル除外）
    if entry.get("size_kb", 0) < 50:
        return False
    return True


def select(entries: list[dict], top_n: int = 25, label: str = "") -> list[dict]:
    files = [e for e in entries if is_target(e)]
    files.sort(key=lambda x: x.get("size_kb", 0), reverse=True)
    return files[:top_n]


def main():
    # MOON-X 全件
    moonx = load_structure("moonx_structure.json")
    moonx_sel = select(moonx, top_n=25, label="MOON-X")

    # プレイド全件
    plaid = load_structure("plaid_structure.json")
    plaid_sel = select(plaid, top_n=25, label="プレイド")

    # DMM HRBP（複数ファイル統合）
    dmm_all: list[dict] = []
    for fn in ["dmm_hrbp_full_structure.json", "dmm_01_recruit.json",
                "dmm_03_dev.json", "dmm_06_data.json"]:
        try:
            dmm_all.extend(load_structure(fn))
        except FileNotFoundError:
            pass
    # path で重複排除
    seen = set()
    dmm_uniq = []
    for e in dmm_all:
        p = e.get("path", "")
        if p in seen:
            continue
        seen.add(p)
        dmm_uniq.append(e)
    dmm_sel = select(dmm_uniq, top_n=25, label="DMM")

    out = {
        "MOON-X": moonx_sel,
        "プレイド": plaid_sel,
        "DMM": dmm_sel,
        "summary": {
            "MOON-X_total_files": sum(1 for e in moonx if e.get("type") == "file"),
            "プレイド_total_files": sum(1 for e in plaid if e.get("type") == "file"),
            "DMM_total_files": sum(1 for e in dmm_uniq if e.get("type") == "file"),
            "MOON-X_selected": len(moonx_sel),
            "プレイド_selected": len(plaid_sel),
            "DMM_selected": len(dmm_sel),
        }
    }

    out_path = CACHE / "priority_files_v1.json"
    with out_path.open("w") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"=== 選定結果 ===")
    print(json.dumps(out["summary"], ensure_ascii=False, indent=2))
    print(f"\n保存先: {out_path}")

    for company in ["MOON-X", "プレイド", "DMM"]:
        print(f"\n--- {company} top {len(out[company])} ---")
        for e in out[company]:
            print(f"  {e.get('size_kb', '?'):>8.1f} KB  [{e.get('extension', '')}]  {e['path']}")


if __name__ == "__main__":
    main()
