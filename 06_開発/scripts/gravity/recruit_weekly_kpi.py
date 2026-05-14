"""
RT-5 週次採用 KPI レポートエンジン（v1.0・260514 Recruit v2.0 対応）

Gravity Recruit v2.0（月 35 万 × 6 ヶ月）の RT-5 実装。
採用ファネル 8 KPI を週次集計し、ボトルネック自動検出 +
改善施策提案（Claude API）を行う。

使い方:
  python3 recruit_weekly_kpi.py --demo
  python3 recruit_weekly_kpi.py --input kpi.csv --week 2026-W19 --output report.md
  python3 recruit_weekly_kpi.py --input kpi.json --week 2026-W19 --dry-run

入力:
  CSV: ヘッダ行 + 1 行（各 KPI の実数値）
  JSON: {kpi_key: value, ...} 形式の直接数値入力
  --benchmark: ベンチマーク定義 JSON（省略時は同梱デフォルト値を使用）

出力:
  - stdout: Markdown レポート（A4 2p 想定）
  - --output 指定時: ファイルにも書き込む
  - --json 指定時: JSON サマリーのみ stdout 出力

ファネル 8 KPI（順序）:
  1. 母集団形成数（スカウト送付 + 応募）
  2. スカウト返信率
  3. 書類選考通過率
  4. 一次面接設定率
  5. 一次面接通過率
  6. 二次面接通過率
  7. オファー率
  8. 内定承諾率

ボトルネック検出:
  業界ベンチマークとの差分が -15%pt 以上のステップを「ボトルネック」判定。
  最大 Delta のステップを最重要ボトルネックとして優先表示する。

Claude API 使用:
  --dry-run で API 呼び出しをスキップ。config_claude.json の api_key を使用。
  モデル: claude-sonnet-4-6。
"""

import os
import sys
import csv
import json
import argparse
from datetime import datetime, timezone, timedelta

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "..", "config", "config_claude.json")
JST = timezone(timedelta(hours=9))

FUNNEL_STEPS = [
    {
        "key":   "pool_count",
        "label": "①母集団形成数（スカウト送付 + 応募）",
        "unit":  "人",
        "is_rate": False,
        "benchmark": None,
    },
    {
        "key":   "scout_reply_rate",
        "label": "②スカウト返信率",
        "unit":  "%",
        "is_rate": True,
        "benchmark": 10.0,
    },
    {
        "key":   "doc_pass_rate",
        "label": "③書類選考通過率",
        "unit":  "%",
        "is_rate": True,
        "benchmark": 30.0,
    },
    {
        "key":   "interview1_set_rate",
        "label": "④一次面接設定率",
        "unit":  "%",
        "is_rate": True,
        "benchmark": 70.0,
    },
    {
        "key":   "interview1_pass_rate",
        "label": "⑤一次面接通過率",
        "unit":  "%",
        "is_rate": True,
        "benchmark": 50.0,
    },
    {
        "key":   "interview2_pass_rate",
        "label": "⑥二次面接通過率",
        "unit":  "%",
        "is_rate": True,
        "benchmark": 60.0,
    },
    {
        "key":   "offer_rate",
        "label": "⑦オファー率",
        "unit":  "%",
        "is_rate": True,
        "benchmark": 80.0,
    },
    {
        "key":   "acceptance_rate",
        "label": "⑧内定承諾率",
        "unit":  "%",
        "is_rate": True,
        "benchmark": 75.0,
    },
]

BOTTLENECK_THRESHOLD_PT = -15.0

RT_AGENT_MAP = {
    "scout_reply_rate":    "RT-4（Bizreach 全件分析エンジン）",
    "doc_pass_rate":       "RT-1（引力軸 JD 生成エンジン）",
    "interview1_set_rate": "RT-2（面接設計エンジン）",
    "interview1_pass_rate":"RT-2（面接設計エンジン）",
    "interview2_pass_rate":"RT-2（面接設計エンジン）",
    "offer_rate":          "RT-3（オファー設計エンジン）",
    "acceptance_rate":     "RT-3（オファー設計エンジン）",
}


def _load_anthropic():
    """anthropic SDK を遅延ロード"""
    try:
        import anthropic
        return anthropic
    except ImportError:
        return None


def _load_config() -> dict:
    """config_claude.json からAPIキーを読み込む"""
    path = os.path.normpath(CONFIG_PATH)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"[WARN] config_claude.json 読み込み失敗: {e}", file=sys.stderr)
        return {}


def _create_sample_data() -> dict:
    """--demo フラグ用サンプル KPI（HACHI 社 Week19 想定・意図的にボトルネックあり）"""
    return {
        "pool_count":           45,
        "scout_reply_rate":     8.5,
        "doc_pass_rate":        22.0,
        "interview1_set_rate":  65.0,
        "interview1_pass_rate": 48.0,
        "interview2_pass_rate": 55.0,
        "offer_rate":           78.0,
        "acceptance_rate":      70.0,
    }


def _load_csv_input(path: str) -> dict:
    """CSV から KPI 値を読み込む（ヘッダ: key, value）"""
    result = {}
    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = row.get("key", "").strip()
            val_str = row.get("value", "").strip()
            if key and val_str:
                try:
                    result[key] = float(val_str)
                except ValueError:
                    pass
    return result


def _load_json_input(path: str) -> dict:
    """JSON ファイルから KPI 値を読み込む"""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_benchmark(path: str | None) -> dict:
    """ベンチマーク JSON を読み込む。None の場合はデフォルト値を返す"""
    if path is None:
        return {s["key"]: s["benchmark"] for s in FUNNEL_STEPS if s["benchmark"] is not None}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _detect_bottlenecks(kpis: dict, benchmarks: dict) -> list[dict]:
    """ボトルネックステップを検出し、Delta 降順でソートして返す"""
    bottlenecks = []
    for step in FUNNEL_STEPS:
        key   = step["key"]
        bench = benchmarks.get(key)
        val   = kpis.get(key)
        if bench is None or val is None or not step["is_rate"]:
            continue
        delta = val - bench
        if delta < BOTTLENECK_THRESHOLD_PT:
            bottlenecks.append({
                "key":       key,
                "label":     step["label"],
                "actual":    val,
                "benchmark": bench,
                "delta":     delta,
                "rt_agent":  RT_AGENT_MAP.get(key, "手動対応"),
            })
    bottlenecks.sort(key=lambda x: x["delta"])
    return bottlenecks


def _call_claude(bottlenecks: list[dict], week: str, api_key: str) -> str:
    """Claude API でボトルネック別改善施策を生成する"""
    anthropic = _load_anthropic()
    if anthropic is None:
        return "[ERROR] anthropic SDK が未インストールです（pip install anthropic）"

    if not bottlenecks:
        return "[INFO] ボトルネックが検出されなかったため施策生成をスキップしました"

    primary = bottlenecks[0]
    bt_list = "\n".join(
        f"- {b['label']}: 実績 {b['actual']:.1f}% / ベンチ {b['benchmark']:.1f}% / 差分 {b['delta']:.1f}pt"
        for b in bottlenecks
    )

    prompt = (
        f"あなたは採用コンサルタントです。{week} 週の採用ファネル分析結果を受け取りました。\n\n"
        f"検出されたボトルネック:\n{bt_list}\n\n"
        f"最重要ボトルネック: {primary['label']}（差分 {primary['delta']:.1f}pt）\n\n"
        f"以下の条件で改善施策を提案してください:\n"
        f"1. 最重要ボトルネック ({primary['label']}) に対して 5 件の具体的施策\n"
        f"2. その他のボトルネック各ステップに対して 3 件ずつの施策\n"
        f"3. GrowthFix の「引力経営」思想（集まる × 躍動 × 留まる）に基づく施策\n"
        f"4. 各施策は「施策名（1 行）+ 概要（1-2 文）+ 期待効果（数値目標）」の形式\n"
        f"5. RT-1〜RT-6 エージェントとの連動可能性がある場合は末尾に注記\n\n"
        f"Markdown 形式で出力してください。"
    )

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        system="あなたは採用 KPI の専門コンサルタントです。ファネル別ボトルネック分析と施策立案が専門です。",
        messages=[{"role": "user", "content": prompt}],
        extra_headers={"anthropic-beta": "prompt-caching-2024-07-31"},
    )
    return message.content[0].text


def _build_report(kpis: dict, benchmarks: dict, bottlenecks: list[dict],
                  measures_text: str, week: str, dry_run: bool) -> str:
    now_jst = datetime.now(JST).strftime("%Y-%m-%d %H:%M JST")
    lines = []

    lines.append("# RT-5 週次採用 KPI レポート")
    lines.append("")
    lines.append(f"**週次:** {week}  ")
    lines.append(f"**生成日時:** {now_jst}  ")
    lines.append(f"**ボトルネック閾値:** ベンチマーク比 {abs(BOTTLENECK_THRESHOLD_PT):.0f}pt 以上の乖離  ")
    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## p.1 採用ファネル 8 KPI 実績")
    lines.append("")
    lines.append("| # | KPI | 実績 | ベンチマーク | 差分 | 判定 |")
    lines.append("|:-:|---|:-:|:-:|:-:|:-:|")

    for step in FUNNEL_STEPS:
        key   = step["key"]
        label = step["label"]
        val   = kpis.get(key)
        bench = benchmarks.get(key)
        unit  = step["unit"]

        if val is None:
            val_str   = "-"
            bench_str = f"{bench:.1f}{unit}" if bench is not None else "-"
            delta_str = "-"
            judge     = "データなし"
        elif not step["is_rate"]:
            val_str   = f"{int(val)}{unit}"
            bench_str = "-"
            delta_str = "-"
            judge     = "-"
        else:
            val_str   = f"{val:.1f}{unit}"
            bench_str = f"{bench:.1f}{unit}" if bench is not None else "-"
            if bench is not None:
                delta = val - bench
                delta_str = f"+{delta:.1f}pt" if delta >= 0 else f"{delta:.1f}pt"
                if delta < BOTTLENECK_THRESHOLD_PT:
                    judge = "BN（要対応）"
                elif delta < 0:
                    judge = "△（やや低い）"
                elif delta >= 10:
                    judge = "◎（優良）"
                else:
                    judge = "○（良好）"
            else:
                delta_str = "-"
                judge     = "-"

        lines.append(f"| - | {label} | **{val_str}** | {bench_str} | {delta_str} | {judge} |")

    lines.append("")
    lines.append("> BN = Bottleneck（ボトルネック）。ベンチマーク比 -15pt 以上の乖離を判定。")
    lines.append("")

    lines.append("## p.2 ボトルネック分析")
    lines.append("")

    if not bottlenecks:
        lines.append("> ボトルネックは検出されませんでした。全ステップがベンチマーク圏内です。")
        lines.append("")
    else:
        lines.append(f"**検出ボトルネック数:** {len(bottlenecks)} ステップ")
        lines.append("")
        lines.append("| 優先度 | KPI | 実績 | ベンチ | 差分 | 連動エージェント |")
        lines.append("|:-:|---|:-:|:-:|:-:|---|")
        for i, bn in enumerate(bottlenecks, 1):
            priority = "最重要" if i == 1 else f"第{i}優先"
            lines.append(
                f"| {priority} | {bn['label']} | {bn['actual']:.1f}% "
                f"| {bn['benchmark']:.1f}% | **{bn['delta']:.1f}pt** | {bn['rt_agent']} |"
            )
        lines.append("")

    lines.append("## p.3 改善施策提案（Claude API 生成）")
    lines.append("")

    if dry_run:
        lines.append("> **[dry-run モード]** Claude API 呼び出しをスキップしました。")
        lines.append("> `--dry-run` を外すとボトルネック別改善施策が生成されます。")
    else:
        lines.append(measures_text)

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*本レポートは Gravity Recruit RT-5 週次採用 KPI レポートエンジンの自動生成物です。*")
    lines.append("")

    return "\n".join(lines)


def _build_json_summary(kpis: dict, benchmarks: dict, bottlenecks: list[dict], week: str) -> dict:
    return {
        "week": week,
        "generated_at": datetime.now(JST).isoformat(),
        "kpis": kpis,
        "benchmarks": benchmarks,
        "bottleneck_count": len(bottlenecks),
        "bottlenecks": bottlenecks,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="RT-5 週次採用 KPI レポートエンジン",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python3 recruit_weekly_kpi.py --demo
  python3 recruit_weekly_kpi.py --input kpi.csv --week 2026-W19 --dry-run
  python3 recruit_weekly_kpi.py --input kpi.json --week 2026-W19 --output report.md
  python3 recruit_weekly_kpi.py --demo --json
        """,
    )
    parser.add_argument("--input",     help="入力ファイルパス（CSV または JSON）")
    parser.add_argument("--week",      help="対象週 YYYY-Www（例: 2026-W19）")
    parser.add_argument("--benchmark", help="ベンチマーク定義 JSON パス（省略時はデフォルト値）")
    parser.add_argument("--output",    help="出力 Markdown ファイルパス")
    parser.add_argument("--dry-run",   action="store_true", help="Claude API を呼ばずに分析のみ出力")
    parser.add_argument("--demo",      action="store_true", help="同梱サンプル KPI で動作確認")
    parser.add_argument("--json",      action="store_true", help="JSON サマリーのみ stdout 出力")
    args = parser.parse_args()

    if not args.demo and not args.input:
        parser.error("--input または --demo のいずれかを指定してください")

    week = args.week or datetime.now(JST).strftime("%Y-W%V")

    if args.demo:
        print("[INFO] demo モード: サンプル KPI（HACHI 社 Week19 想定）を使用", file=sys.stderr)
        kpis = _create_sample_data()
    else:
        input_path = os.path.abspath(args.input)
        print(f"[INFO] 入力ファイル読み込み: {input_path}", file=sys.stderr)
        try:
            if input_path.endswith(".json"):
                kpis = _load_json_input(input_path)
            else:
                kpis = _load_csv_input(input_path)
        except (FileNotFoundError, OSError, json.JSONDecodeError) as e:
            print(f"[ERROR] 入力ファイル読み込み失敗: {e}", file=sys.stderr)
            sys.exit(1)

    try:
        benchmarks = _load_benchmark(args.benchmark)
    except (FileNotFoundError, OSError, json.JSONDecodeError) as e:
        print(f"[ERROR] ベンチマーク読み込み失敗: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"[INFO] KPI 分析: {week} / {len(kpis)} 項目", file=sys.stderr)
    bottlenecks = _detect_bottlenecks(kpis, benchmarks)
    print(f"[INFO] ボトルネック検出: {len(bottlenecks)} ステップ", file=sys.stderr)

    if args.json:
        summary = _build_json_summary(kpis, benchmarks, bottlenecks, week)
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return

    measures_text = ""
    if not args.dry_run:
        config  = _load_config()
        api_key = config.get("api_key", "")
        if not api_key:
            print("[WARN] api_key が config_claude.json に見つかりません。施策生成をスキップします。", file=sys.stderr)
            args.dry_run = True
        else:
            print("[INFO] Claude API 呼び出し中...", file=sys.stderr)
            try:
                measures_text = _call_claude(bottlenecks, week, api_key)
                print("[OK]  Claude API 施策生成完了", file=sys.stderr)
            except Exception as e:
                print(f"[WARN] Claude API 呼び出し失敗: {e}", file=sys.stderr)
                measures_text = f"[ERROR] API 呼び出し失敗: {e}"

    report = _build_report(kpis, benchmarks, bottlenecks, measures_text, week, args.dry_run)
    print(report)

    if args.output:
        output_path = os.path.abspath(args.output)
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"[OK]  レポート書き込み完了: {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
