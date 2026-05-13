#!/usr/bin/env python3
"""Dropbox API クライアント（基盤）

GrowthFix Vault から Dropbox 内資料にアクセスして R/C/Orbit 業務抽出に活用する基盤。

使い方:
    # 接続テスト + ルートフォルダ構造取得
    python3 dropbox_client.py --test

    # 特定パス配下のフォルダ構造取得
    python3 dropbox_client.py --list-folder "/DMM_HRBP"

    # 検索（フォルダ名・ファイル名）
    python3 dropbox_client.py --search "HRBP"
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

try:
    import dropbox
    from dropbox.exceptions import ApiError, AuthError
    from dropbox.files import FolderMetadata, FileMetadata
except ImportError:
    print("ERROR: dropbox SDK not installed. Run: pip3 install --user --break-system-packages dropbox")
    sys.exit(1)


VAULT_ROOT = Path("/Users/ishiinobuyuki/Documents/Obsidian Vault")
TOKEN_PATH = VAULT_ROOT / "06_開発/scripts/config/dropbox_token.json"


def load_token() -> str:
    """Load access token from config JSON."""
    if not TOKEN_PATH.exists():
        print(f"ERROR: Token file not found: {TOKEN_PATH}")
        sys.exit(1)
    with TOKEN_PATH.open() as f:
        config = json.load(f)
    token = config.get("access_token", "")
    if not token or token == "PASTE_YOUR_TOKEN_HERE":
        print("ERROR: access_token not set in config file")
        sys.exit(1)
    return token


def get_client() -> dropbox.Dropbox:
    """Initialize Dropbox client with token."""
    token = load_token()
    return dropbox.Dropbox(token)


def test_connection(dbx: dropbox.Dropbox) -> dict:
    """Test API connection and return account info."""
    try:
        account = dbx.users_get_current_account()
        space = dbx.users_get_space_usage()
        return {
            "ok": True,
            "name": account.name.display_name,
            "email": account.email,
            "account_type": str(account.account_type),
            "used_gb": round(space.used / 1024 / 1024 / 1024, 2),
            "allocated_gb": round(space.allocation.get_individual().allocated / 1024 / 1024 / 1024, 2) if space.allocation.is_individual() else None,
        }
    except AuthError as e:
        return {"ok": False, "error": "AuthError", "detail": str(e)}
    except ApiError as e:
        return {"ok": False, "error": "ApiError", "detail": str(e)}


def list_folder(dbx: dropbox.Dropbox, path: str = "", recursive: bool = False, max_entries: int = 200) -> list[dict]:
    """List folder contents (non-recursive by default to avoid huge dumps)."""
    entries: list[dict] = []
    try:
        result = dbx.files_list_folder(path, recursive=recursive, limit=max_entries)
        for entry in result.entries:
            entries.append(_entry_to_dict(entry))
        # Pagination
        while result.has_more and len(entries) < max_entries * 5:
            result = dbx.files_list_folder_continue(result.cursor)
            for entry in result.entries:
                entries.append(_entry_to_dict(entry))
    except ApiError as e:
        return [{"error": "ApiError", "detail": str(e), "path": path}]
    return entries


def search(dbx: dropbox.Dropbox, query: str, max_results: int = 100) -> list[dict]:
    """Search files/folders by name."""
    entries: list[dict] = []
    try:
        result = dbx.files_search_v2(query, options=dropbox.files.SearchOptions(max_results=max_results))
        for match in result.matches:
            metadata = match.metadata.get_metadata()
            entries.append(_entry_to_dict(metadata))
    except ApiError as e:
        return [{"error": "ApiError", "detail": str(e), "query": query}]
    return entries


def _entry_to_dict(entry) -> dict:
    """Convert Dropbox entry metadata to dict."""
    base = {
        "name": entry.name,
        "path": entry.path_display,
    }
    if isinstance(entry, FolderMetadata):
        base["type"] = "folder"
    elif isinstance(entry, FileMetadata):
        base["type"] = "file"
        base["size_kb"] = round(entry.size / 1024, 1)
        base["modified"] = entry.client_modified.isoformat() if entry.client_modified else None
        base["extension"] = Path(entry.name).suffix.lower()
    else:
        base["type"] = "other"
    return base


def main() -> int:
    parser = argparse.ArgumentParser(description="Dropbox API client for GrowthFix Vault")
    parser.add_argument("--test", action="store_true", help="Test connection")
    parser.add_argument("--list-folder", type=str, default=None, metavar="PATH", help='List folder (e.g., "" for root, "/DMM_HRBP" for subfolder)')
    parser.add_argument("--recursive", action="store_true", help="Recursive listing (use with caution)")
    parser.add_argument("--search", type=str, default=None, metavar="QUERY", help="Search by name")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    dbx = get_client()

    if args.test or (not args.list_folder and not args.search):
        info = test_connection(dbx)
        if args.json:
            print(json.dumps(info, ensure_ascii=False, indent=2))
        else:
            if info.get("ok"):
                print("=== Dropbox 接続成功 ===")
                print(f"  Name        : {info['name']}")
                print(f"  Email       : {info['email']}")
                print(f"  Account Type: {info['account_type']}")
                print(f"  Storage Used: {info['used_gb']} GB / {info['allocated_gb']} GB")
            else:
                print(f"=== 接続失敗 ===")
                print(f"  Error : {info['error']}")
                print(f"  Detail: {info['detail']}")
                return 1

    if args.list_folder is not None:
        entries = list_folder(dbx, args.list_folder, recursive=args.recursive)
        if args.json:
            print(json.dumps(entries, ensure_ascii=False, indent=2))
        else:
            print(f"\n=== Folder: {args.list_folder or '(root)'} ===")
            print(f"Total entries: {len(entries)}")
            folders = [e for e in entries if e.get("type") == "folder"]
            files = [e for e in entries if e.get("type") == "file"]
            print(f"  Folders: {len(folders)}")
            print(f"  Files  : {len(files)}")
            print("\n--- Folders ---")
            for e in folders[:50]:
                print(f"  📁 {e['name']}")
            if len(folders) > 50:
                print(f"  ... +{len(folders) - 50} more folders")
            print("\n--- Files (first 30) ---")
            for e in files[:30]:
                print(f"  📄 {e['name']} ({e.get('size_kb', '?')} KB)")
            if len(files) > 30:
                print(f"  ... +{len(files) - 30} more files")

    if args.search:
        results = search(dbx, args.search)
        if args.json:
            print(json.dumps(results, ensure_ascii=False, indent=2))
        else:
            print(f"\n=== Search: '{args.search}' ===")
            print(f"Total results: {len(results)}")
            for e in results[:50]:
                icon = "📁" if e.get("type") == "folder" else "📄"
                print(f"  {icon} {e['path']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
