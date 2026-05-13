#!/usr/bin/env python3
"""Dropbox から特定ファイルを _cache/ にダウンロード（分析用）

使い方:
    python3 download_for_analysis.py "/01_DMM.com/01_HRビジネスパートナー/06_組織開発（データ）/02_Wevox全体/220701_wevoxコメント精査SS.xlsx"
    python3 download_for_analysis.py --batch path1 path2 path3
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from dropbox_client import get_client

VAULT_ROOT = Path("/Users/ishiinobuyuki/Documents/Obsidian Vault")
CACHE_DIR = VAULT_ROOT / "06_開発/scripts/dropbox/_cache"


def download_file(dbx, dropbox_path: str) -> Path | None:
    """Download a single file from Dropbox to _cache/."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    # Use safe filename: replace path separators
    safe_name = dropbox_path.lstrip("/").replace("/", "_")
    local_path = CACHE_DIR / safe_name
    try:
        print(f"⬇️  Downloading: {dropbox_path}")
        with local_path.open("wb") as f:
            metadata, response = dbx.files_download(dropbox_path)
            f.write(response.content)
        size_kb = local_path.stat().st_size / 1024
        print(f"✅ Saved: {local_path} ({size_kb:.1f} KB)")
        return local_path
    except Exception as e:
        print(f"❌ Failed: {dropbox_path}")
        print(f"   Error: {e}")
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Download Dropbox files to _cache/")
    parser.add_argument("paths", nargs="+", help="Dropbox file path(s)")
    args = parser.parse_args()

    dbx = get_client()
    success = 0
    for path in args.paths:
        if download_file(dbx, path):
            success += 1
    print(f"\nTotal: {success}/{len(args.paths)} files downloaded")
    return 0 if success == len(args.paths) else 1


if __name__ == "__main__":
    sys.exit(main())
