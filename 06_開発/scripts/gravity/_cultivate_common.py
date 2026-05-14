"""
Gravity Cultivate — 共通処理モジュール（v1.0・260514）

CT-1 / CT-2 / CT-3 から import して使う共通処理：
  - Claude API ロード・呼び出し（prompt caching 有効）
  - config_claude.json 読み込み
  - Markdown レポート整形ユーティリティ
  - SHA256 短縮ハッシュ（--mask フラグ用）
  - JST 日時取得

依存: anthropic（pip install anthropic）、標準ライブラリのみ
"""

import os
import sys
import json
import hashlib
from datetime import datetime, timezone, timedelta

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "..", "config", "config_claude.json")
JST = timezone(timedelta(hours=9))
MODEL = "claude-sonnet-4-6"


def now_jst_str() -> str:
    return datetime.now(JST).strftime("%Y-%m-%d %H:%M JST")


def short_hash(text: str, length: int = 8) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:length]


def mask_name(name: str, enabled: bool) -> str:
    if not enabled or not name:
        return name
    return f"ID-{short_hash(name)}"


def load_config() -> dict:
    path = os.path.normpath(CONFIG_PATH)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError as e:
        raise FileNotFoundError(
            f"config_claude.json が見つかりません: {path}"
        ) from e
    except json.JSONDecodeError as e:
        raise ValueError(f"config_claude.json の JSON が不正です: {e}") from e


def load_input_json(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"入力 JSON が見つかりません: {path}") from e
    except json.JSONDecodeError as e:
        raise ValueError(f"入力 JSON の形式が不正です: {e}") from e


def save_output(content: str, path: str) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    size_kb = os.path.getsize(path) // 1024
    print(f"[OK]  出力完了: {path} ({size_kb} KB)", file=sys.stderr)


def save_json(data: dict, path: str) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[OK]  JSON 出力完了: {path}", file=sys.stderr)


def _load_anthropic():
    try:
        from anthropic import Anthropic
        return Anthropic
    except ImportError:
        return None


def call_claude(
    system_prompt: str,
    user_prompt: str,
    dry_run: bool = False,
    max_tokens: int = 4096,
) -> str:
    if dry_run:
        print("[DRY-RUN] Claude API 呼び出しをスキップします。", file=sys.stderr)
        return "[DRY-RUN] mock 出力：Claude API を呼び出した場合の結果がここに入ります。"

    Anthropic = _load_anthropic()
    if Anthropic is None:
        print(
            "[ERROR] anthropic SDK が見つかりません。pip install anthropic を実行してください。",
            file=sys.stderr,
        )
        print("[INFO]  --dry-run フラグで API 呼び出しをスキップできます。", file=sys.stderr)
        sys.exit(1)

    cfg = load_config()
    api_key = cfg.get("api_key", "")
    if not api_key:
        print("[ERROR] config_claude.json に api_key が設定されていません。", file=sys.stderr)
        sys.exit(1)

    client = Anthropic(api_key=api_key)
    print(f"[INFO] Claude API 呼び出し中（モデル: {MODEL}）...", file=sys.stderr)

    response = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        system=[
            {
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": user_prompt}],
    )
    return response.content[0].text


def md_h1(text: str) -> str:
    return f"# {text}\n"


def md_h2(text: str) -> str:
    return f"\n## {text}\n"


def md_h3(text: str) -> str:
    return f"\n### {text}\n"


def md_table_row(cells: list) -> str:
    return "| " + " | ".join(str(c) for c in cells) + " |"


def md_table(headers: list, rows: list) -> str:
    lines = [
        md_table_row(headers),
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append(md_table_row(row))
    return "\n".join(lines)


def md_blockquote(text: str) -> str:
    return "\n".join(f"> {line}" for line in text.splitlines())


def md_footer(script_name: str) -> str:
    return (
        f"\n---\n\n"
        f"*本レポートは {script_name} による自動生成物です（{now_jst_str()}）。*\n"
    )
