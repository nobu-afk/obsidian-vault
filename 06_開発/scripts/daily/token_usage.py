#!/usr/bin/env python3
"""Claude Code transcript からトークン使用量を集計し、月次／日次のコスト推計を出力する。

使い方:
    python3 token_usage.py                 直近30日のサマリー
    python3 token_usage.py --month 2026-04 指定月のサマリー
    python3 token_usage.py --json          JSON出力（daily skill 連携用）
    python3 token_usage.py --daily YYYY-MM-DD  特定日のサマリー

設計:
- ~/.claude/projects/**/*.jsonl を走査して message.usage を抽出
- (日付JST × モデル) で集計
- config_token_pricing.json から単価を引いて USD/JPY を概算
- JST（UTC+9）で日付をまとめる
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECTS_ROOT = Path.home() / ".claude" / "projects"
PRICING_PATH = SCRIPT_DIR.parent / "config" / "config_token_pricing.json"
JST = dt.timezone(dt.timedelta(hours=9))


def load_pricing() -> dict:
    with PRICING_PATH.open() as f:
        return json.load(f)


def iter_transcripts(root: Path):
    yield from root.rglob("*.jsonl")


def parse_jst_date(timestamp: str) -> str:
    """ISO timestamp (UTC) → YYYY-MM-DD (JST)"""
    if not timestamp:
        return ""
    if timestamp.endswith("Z"):
        timestamp = timestamp[:-1] + "+00:00"
    try:
        ts = dt.datetime.fromisoformat(timestamp)
    except ValueError:
        return ""
    return ts.astimezone(JST).strftime("%Y-%m-%d")


def extract_usage(line: str):
    """JSONL の1行から (date_jst, model, usage_dict) を返す。usage が無ければ None。"""
    try:
        d = json.loads(line)
    except json.JSONDecodeError:
        return None
    msg = d.get("message")
    if not isinstance(msg, dict):
        return None
    usage = msg.get("usage")
    if not isinstance(usage, dict):
        return None
    model = msg.get("model") or "default"
    date_jst = parse_jst_date(d.get("timestamp", ""))
    if not date_jst:
        return None
    return date_jst, model, usage


def cost_for(model: str, usage: dict, pricing: dict) -> float:
    """モデル別単価でコスト概算（USD）。"""
    rates = pricing["models"].get(model) or pricing["models"]["default"]
    input_t = usage.get("input_tokens", 0) or 0
    output_t = usage.get("output_tokens", 0) or 0
    cache_read = usage.get("cache_read_input_tokens", 0) or 0
    cache_create_5m = (
        usage.get("cache_creation", {}).get("ephemeral_5m_input_tokens", 0) or 0
    )
    cache_create_1h = (
        usage.get("cache_creation", {}).get("ephemeral_1h_input_tokens", 0) or 0
    )
    cost = (
        input_t * rates["input"]
        + output_t * rates["output"]
        + cache_read * rates["cache_read"]
        + cache_create_5m * rates["cache_creation_5m"]
        + cache_create_1h * rates["cache_creation_1h"]
    ) / 1_000_000
    return cost


def aggregate(filter_func=None) -> dict:
    """(date, model) → {input, output, cache_read, cache_create, cost_usd, calls} を集計。"""
    pricing = load_pricing()
    agg: dict = defaultdict(lambda: defaultdict(float))
    if not PROJECTS_ROOT.exists():
        return {"agg": agg, "pricing": pricing}
    for path in iter_transcripts(PROJECTS_ROOT):
        try:
            with path.open(encoding="utf-8") as f:
                for line in f:
                    parsed = extract_usage(line)
                    if parsed is None:
                        continue
                    date_jst, model, usage = parsed
                    if filter_func and not filter_func(date_jst):
                        continue
                    key = (date_jst, model)
                    agg[key]["input"] += usage.get("input_tokens", 0) or 0
                    agg[key]["output"] += usage.get("output_tokens", 0) or 0
                    agg[key]["cache_read"] += (
                        usage.get("cache_read_input_tokens", 0) or 0
                    )
                    cache_create = usage.get("cache_creation", {}) or {}
                    agg[key]["cache_create_5m"] += (
                        cache_create.get("ephemeral_5m_input_tokens", 0) or 0
                    )
                    agg[key]["cache_create_1h"] += (
                        cache_create.get("ephemeral_1h_input_tokens", 0) or 0
                    )
                    agg[key]["cost_usd"] += cost_for(model, usage, pricing)
                    agg[key]["calls"] += 1
        except OSError:
            continue
    return {"agg": agg, "pricing": pricing}


def fmt_int(v) -> str:
    return f"{int(v):,}"


def render_summary(agg: dict, pricing: dict, label: str) -> str:
    """日付×モデル の集計テーブルをテキスト出力。"""
    if not agg:
        return f"## {label}\n\n（該当データなし）\n"

    by_date: dict = defaultdict(dict)
    for (date, model), v in agg.items():
        by_date[date][model] = v

    lines = [f"## {label}", ""]
    grand_input = grand_output = grand_cache_r = grand_cost = grand_calls = 0
    for date in sorted(by_date.keys()):
        models = by_date[date]
        d_input = sum(m["input"] for m in models.values())
        d_output = sum(m["output"] for m in models.values())
        d_cache_r = sum(m["cache_read"] for m in models.values())
        d_cost = sum(m["cost_usd"] for m in models.values())
        d_calls = sum(m["calls"] for m in models.values())
        grand_input += d_input
        grand_output += d_output
        grand_cache_r += d_cache_r
        grand_cost += d_cost
        grand_calls += d_calls
        cost_jpy = d_cost * pricing["usd_jpy"]
        lines.append(
            f"- {date} | calls {fmt_int(d_calls)} | in {fmt_int(d_input)} | out {fmt_int(d_output)} | cache_r {fmt_int(d_cache_r)} | ${d_cost:,.2f} (¥{cost_jpy:,.0f})"
        )

    lines.append("")
    total_jpy = grand_cost * pricing["usd_jpy"]
    lines.append(
        f"**合計** calls {fmt_int(grand_calls)} | in {fmt_int(grand_input)} | out {fmt_int(grand_output)} | cache_r {fmt_int(grand_cache_r)} | **${grand_cost:,.2f} (¥{total_jpy:,.0f})**"
    )
    return "\n".join(lines) + "\n"


def render_json(agg: dict, pricing: dict) -> str:
    """daily skill 連携用 JSON 出力。"""
    out = {
        "generated_at_jst": dt.datetime.now(JST).isoformat(timespec="seconds"),
        "usd_jpy": pricing["usd_jpy"],
        "by_date": {},
        "totals": {
            "input": 0,
            "output": 0,
            "cache_read": 0,
            "cost_usd": 0.0,
            "cost_jpy": 0.0,
            "calls": 0,
        },
    }
    for (date, model), v in agg.items():
        slot = out["by_date"].setdefault(
            date, {"models": {}, "input": 0, "output": 0, "cache_read": 0, "cost_usd": 0.0, "calls": 0}
        )
        slot["models"][model] = {
            "input": int(v["input"]),
            "output": int(v["output"]),
            "cache_read": int(v["cache_read"]),
            "cost_usd": round(v["cost_usd"], 4),
            "calls": int(v["calls"]),
        }
        slot["input"] += int(v["input"])
        slot["output"] += int(v["output"])
        slot["cache_read"] += int(v["cache_read"])
        slot["cost_usd"] += v["cost_usd"]
        slot["calls"] += int(v["calls"])
        out["totals"]["input"] += int(v["input"])
        out["totals"]["output"] += int(v["output"])
        out["totals"]["cache_read"] += int(v["cache_read"])
        out["totals"]["cost_usd"] += v["cost_usd"]
        out["totals"]["calls"] += int(v["calls"])

    # round
    for date_data in out["by_date"].values():
        date_data["cost_usd"] = round(date_data["cost_usd"], 2)
        date_data["cost_jpy"] = round(date_data["cost_usd"] * pricing["usd_jpy"])
    out["totals"]["cost_usd"] = round(out["totals"]["cost_usd"], 2)
    out["totals"]["cost_jpy"] = round(out["totals"]["cost_usd"] * pricing["usd_jpy"])

    return json.dumps(out, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Claude Code トークン使用量集計")
    parser.add_argument("--month", help="YYYY-MM 形式（指定月のみ）")
    parser.add_argument("--daily", help="YYYY-MM-DD 形式（指定日のみ）")
    parser.add_argument("--days", type=int, default=30, help="直近N日（デフォルト30）")
    parser.add_argument("--json", action="store_true", help="JSON出力")
    args = parser.parse_args()

    if args.month:
        prefix = args.month
        filter_func = lambda d: d.startswith(prefix)
        label = f"トークン使用量（{prefix}）"
    elif args.daily:
        target = args.daily
        filter_func = lambda d: d == target
        label = f"トークン使用量（{target}）"
    else:
        cutoff = (dt.datetime.now(JST) - dt.timedelta(days=args.days)).strftime("%Y-%m-%d")
        filter_func = lambda d: d >= cutoff
        label = f"トークン使用量（直近{args.days}日・{cutoff} 以降）"

    result = aggregate(filter_func=filter_func)
    if args.json:
        print(render_json(result["agg"], result["pricing"]))
    else:
        print(render_summary(result["agg"], result["pricing"], label))


if __name__ == "__main__":
    main()
