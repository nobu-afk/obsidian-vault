"""
RT-4 Bizreach スカウト全件分析エンジン（v1.0・260514 Recruit v2.0 対応）

Gravity Recruit v2.0（月 35 万 × 6 ヶ月）の RT-4 実装。
Bizreach スカウト送付ログ CSV を全件分析し、
業界別・件名パターン別・本文長別の返信率を算出する。
クロス分析結果から送信文面最適化提案を 3 本生成する。

使い方:
  python3 recruit_bizreach_analyzer.py --input <CSV_PATH> [オプション]

例:
  python3 recruit_bizreach_analyzer.py --demo
  python3 recruit_bizreach_analyzer.py --input data.csv --industry IT --output report.md
  python3 recruit_bizreach_analyzer.py --input data.csv --dry-run

入力 CSV 列（順不同・ヘッダ行あり）:
  送信日, 候補者ID, 業界, 職種, 経験年数, スカウト件名, スカウト本文, 返信状況, 返信日, 返信内容

出力:
  - stdout: Markdown 分析レポート
  - --output 指定時: ファイルにも書き込む
  - --json 指定時: JSON サマリーのみ stdout 出力

機密マスキング:
  候補者 ID → SHA-256 ハッシュ（先頭 8 文字）。実 ID はログに残さない。

Claude API 使用:
  --dry-run フラグで API 呼び出しをスキップし、分析サマリーのみ出力する。
  config_claude.json の api_key を使用。モデル: claude-sonnet-4-6。
"""

import os
import sys
import csv
import json
import hashlib
import argparse
from datetime import datetime, timezone, timedelta

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "..", "config", "config_claude.json")
JST = timezone(timedelta(hours=9))

SUBJECT_PATTERNS = {
    "名前呼びかけ型": lambda s: "さん" in s[:10],
    "会社名直球型":   lambda s: any(kw in s for kw in ["株式会社", "（株）", "(株)"]),
    "興味喚起型":     lambda s: any(kw in s for kw in ["ご縁", "チャンス", "機会", "いかがでしょう", "ぜひ", "特別"]),
    "実績訴求型":     lambda s: any(kw in s for kw in ["実績", "年収", "万円", "%", "倍"]),
}

BODY_BUCKETS = {
    "短文（300字未満）": (0, 300),
    "中文（300-600字）": (300, 600),
    "長文（600字超）":   (600, 10000),
}

BENCHMARK_REPLY_RATE = {
    "IT":     0.12,
    "コンサル": 0.10,
    "メーカー": 0.08,
    "金融":   0.07,
    "医療":   0.09,
    "その他":  0.07,
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


def _mask_id(raw_id: str) -> str:
    """候補者 ID を SHA-256 ハッシュ先頭 8 文字にマスク"""
    return hashlib.sha256(raw_id.encode()).hexdigest()[:8]


def _classify_subject(subject: str) -> str:
    for label, fn in SUBJECT_PATTERNS.items():
        if fn(subject):
            return label
    return "その他型"


def _classify_body_length(body: str) -> str:
    length = len(body)
    for label, (lo, hi) in BODY_BUCKETS.items():
        if lo <= length < hi:
            return label
    return "長文（600字超）"


def _create_sample_data() -> list[dict]:
    """--demo フラグ用架空データ（20 件）"""
    import random
    random.seed(42)
    industries = ["IT", "コンサル", "メーカー", "金融", "医療"]
    occupations = ["エンジニア", "営業", "マーケター", "人事", "経営企画"]
    subject_templates = [
        "田中さん、引力経営に興味はありませんか？",
        "株式会社GrowthFixより特別なご提案",
        "ぜひ一度お話しさせてください",
        "年収アップ実績多数の企業からのご連絡",
        "山田さんへ、ご縁のお声がけです",
    ]
    body_short  = "はじめまして。弊社は引力経営の理念で組織を変革しています。ご興味あれば是非。"
    body_medium = ("はじめまして。株式会社GrowthFixの石井と申します。"
                   "貴殿のご経歴を拝見し、ぜひお話しする機会をいただきたく連絡いたしました。"
                   "弊社では引力経営の理念に基づき、採用・育成・定着の全プロセスを科学的にデザインしています。"
                   "現在、次世代リーダー候補を探しており、貴殿のご経験が大変参考になると確信しております。")
    body_long   = body_medium * 2 + "詳しくはオンライン面談でお伝えできれば幸いです。ご検討のほどよろしくお願いいたします。"

    rows = []
    for i in range(20):
        ind = random.choice(industries)
        subj_tpl = random.choice(subject_templates)
        body_choice = random.choice([body_short, body_medium, body_long])
        replied = random.random() < BENCHMARK_REPLY_RATE.get(ind, 0.08) * 1.5
        rows.append({
            "送信日":       f"2026-04-{i+1:02d}",
            "候補者ID":     f"BZ{10000+i}",
            "業界":         ind,
            "職種":         random.choice(occupations),
            "経験年数":     str(random.randint(3, 15)),
            "スカウト件名": subj_tpl,
            "スカウト本文": body_choice,
            "返信状況":     "返信あり" if replied else "未返信",
            "返信日":       f"2026-04-{i+2:02d}" if replied else "",
            "返信内容":     "ご連絡ありがとうございます。" if replied else "",
        })
    return rows


def _load_csv(path: str) -> list[dict]:
    """CSV ファイルを読み込み、候補者 ID をマスクして返す"""
    rows = []
    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["候補者ID"] = _mask_id(row.get("候補者ID", ""))
            rows.append(row)
    return rows


def _analyze(rows: list[dict], target_industry: str | None) -> dict:
    """分析メイン：業界別・件名パターン別・本文長別・クロス集計"""
    total = len(rows)
    if target_industry:
        rows = [r for r in rows if r.get("業界") == target_industry]

    def is_replied(r: dict) -> bool:
        return r.get("返信状況", "") == "返信あり"

    industry_stats: dict[str, dict] = {}
    subject_stats:  dict[str, dict] = {}
    body_stats:     dict[str, dict] = {}
    cross_stats:    dict[tuple, dict] = {}

    for row in rows:
        ind  = row.get("業界", "その他")
        subj = row.get("スカウト件名", "")
        body = row.get("スカウト本文", "")
        pat  = _classify_subject(subj)
        blen = _classify_body_length(body)
        rep  = is_replied(row)

        for key, store in [(ind, industry_stats), (pat, subject_stats), (blen, body_stats)]:
            if key not in store:
                store[key] = {"total": 0, "replied": 0}
            store[key]["total"] += 1
            if rep:
                store[key]["replied"] += 1

        cross_key = (ind, pat, blen)
        if cross_key not in cross_stats:
            cross_stats[cross_key] = {"total": 0, "replied": 0}
        cross_stats[cross_key]["total"] += 1
        if rep:
            cross_stats[cross_key]["replied"] += 1

    def rate(d: dict) -> float:
        return d["replied"] / d["total"] if d["total"] > 0 else 0.0

    industry_rates = {k: {"rate": rate(v), **v} for k, v in industry_stats.items()}
    subject_rates  = {k: {"rate": rate(v), **v} for k, v in subject_stats.items()}
    body_rates     = {k: {"rate": rate(v), **v} for k, v in body_stats.items()}

    cross_list = []
    for (ind, pat, blen), v in cross_stats.items():
        cross_list.append({
            "industry": ind, "subject_pattern": pat, "body_length": blen,
            "total": v["total"], "replied": v["replied"], "rate": rate(v),
        })
    cross_list.sort(key=lambda x: x["rate"], reverse=True)

    return {
        "total_records": total,
        "filtered_records": len(rows),
        "target_industry": target_industry,
        "industry_rates": industry_rates,
        "subject_rates": subject_rates,
        "body_rates": body_rates,
        "cross_top5": cross_list[:5],
    }


def _call_claude(analysis: dict, api_key: str) -> str:
    """Claude API で業界特化文面テンプレート 3 本を生成する"""
    anthropic = _load_anthropic()
    if anthropic is None:
        return "[ERROR] anthropic SDK が未インストールです（pip install anthropic）"

    top5 = analysis.get("cross_top5", [])
    if not top5:
        return "[INFO] クロス分析結果がないため文面生成をスキップしました"

    best = top5[0]
    industry = best.get("industry", "IT")
    pat      = best.get("subject_pattern", "名前呼びかけ型")
    blen     = best.get("body_length", "中文（300-600字）")
    rate_pct = f"{best.get('rate', 0) * 100:.1f}%"

    prompt = (
        f"あなたは採用のプロです。以下の最高返信率パターンに基づき、"
        f"Bizreach スカウトの件名・本文テンプレートを 3 種類作成してください。\n\n"
        f"最高返信率パターン:\n"
        f"- 業界: {industry}\n"
        f"- 件名タイプ: {pat}\n"
        f"- 本文長さ: {blen}\n"
        f"- 返信率: {rate_pct}\n\n"
        f"条件:\n"
        f"1. 件名は 30 文字以内\n"
        f"2. 本文は{blen}に合わせた文字数\n"
        f"3. GrowthFix の「引力経営」思想（集まる×躍動×留まる）を自然に組み込む\n"
        f"4. 各テンプレートは「【件名】」「【本文】」で明示\n"
        f"5. 候補者の名前部分は{{氏名}}プレースホルダー使用\n\n"
        f"テンプレート 3 種類を出力してください。"
    )

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        system="あなたは採用コンサルタントです。Bizreach スカウト文面の返信率最大化が専門です。",
        messages=[{"role": "user", "content": prompt}],
        extra_headers={"anthropic-beta": "prompt-caching-2024-07-31"},
    )
    return message.content[0].text


def _build_report(analysis: dict, template_text: str, dry_run: bool) -> str:
    now_jst = datetime.now(JST).strftime("%Y-%m-%d %H:%M JST")
    lines = []

    lines.append("# RT-4 Bizreach スカウト全件分析レポート")
    lines.append("")
    lines.append(f"**生成日時:** {now_jst}  ")
    lines.append(f"**総件数:** {analysis['total_records']} 件  ")
    if analysis.get("target_industry"):
        lines.append(f"**対象業界フィルタ:** {analysis['target_industry']}（{analysis['filtered_records']} 件）  ")
    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## 1. 業界別返信率")
    lines.append("")
    lines.append("| 業界 | 送付数 | 返信数 | 返信率 | ベンチマーク | 差分 |")
    lines.append("|---|:-:|:-:|:-:|:-:|:-:|")
    for ind, st in sorted(analysis["industry_rates"].items(), key=lambda x: -x[1]["rate"]):
        bench = BENCHMARK_REPLY_RATE.get(ind, BENCHMARK_REPLY_RATE["その他"])
        delta = st["rate"] - bench
        delta_str = f"+{delta*100:.1f}pt" if delta >= 0 else f"{delta*100:.1f}pt"
        lines.append(
            f"| {ind} | {st['total']} | {st['replied']} "
            f"| **{st['rate']*100:.1f}%** | {bench*100:.1f}% | {delta_str} |"
        )
    lines.append("")

    lines.append("## 2. 件名パターン別返信率")
    lines.append("")
    lines.append("| 件名パターン | 送付数 | 返信数 | 返信率 |")
    lines.append("|---|:-:|:-:|:-:|")
    for pat, st in sorted(analysis["subject_rates"].items(), key=lambda x: -x[1]["rate"]):
        lines.append(
            f"| {pat} | {st['total']} | {st['replied']} | **{st['rate']*100:.1f}%** |"
        )
    lines.append("")

    lines.append("## 3. 本文長別返信率")
    lines.append("")
    lines.append("| 本文長 | 送付数 | 返信数 | 返信率 |")
    lines.append("|---|:-:|:-:|:-:|")
    for blen, st in sorted(analysis["body_rates"].items(), key=lambda x: -x[1]["rate"]):
        lines.append(
            f"| {blen} | {st['total']} | {st['replied']} | **{st['rate']*100:.1f}%** |"
        )
    lines.append("")

    lines.append("## 4. クロス分析 Top 5（業界 × 件名 × 本文長）")
    lines.append("")
    lines.append("| # | 業界 | 件名パターン | 本文長 | 送付数 | 返信率 |")
    lines.append("|:-:|---|---|---|:-:|:-:|")
    for i, row in enumerate(analysis["cross_top5"], 1):
        lines.append(
            f"| {i} | {row['industry']} | {row['subject_pattern']} "
            f"| {row['body_length']} | {row['total']} | **{row['rate']*100:.1f}%** |"
        )
    lines.append("")

    lines.append("## 5. 最適化文面テンプレート（Claude API 生成）")
    lines.append("")
    if dry_run:
        lines.append("> **[dry-run モード]** Claude API 呼び出しをスキップしました。")
        lines.append("> `--dry-run` を外すと文面テンプレート 3 本が生成されます。")
    else:
        lines.append(template_text)
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*本レポートは Gravity Recruit RT-4 Bizreach スカウト分析エンジンの自動生成物です。*")
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="RT-4 Bizreach スカウト全件分析エンジン",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python3 recruit_bizreach_analyzer.py --demo
  python3 recruit_bizreach_analyzer.py --input data.csv --dry-run
  python3 recruit_bizreach_analyzer.py --input data.csv --industry IT --output report.md
  python3 recruit_bizreach_analyzer.py --input data.csv --json
        """,
    )
    parser.add_argument("--input",    help="入力 CSV ファイルパス")
    parser.add_argument("--industry", help="業界フィルタ（例: IT / コンサル / メーカー / 金融 / 医療）")
    parser.add_argument("--output",   help="出力 Markdown ファイルパス")
    parser.add_argument("--dry-run",  action="store_true", help="Claude API を呼ばずに分析サマリーのみ出力")
    parser.add_argument("--demo",     action="store_true", help="同梱架空データ 20 件で動作確認")
    parser.add_argument("--json",     action="store_true", help="JSON サマリーのみ stdout 出力")
    args = parser.parse_args()

    if not args.demo and not args.input:
        parser.error("--input または --demo のいずれかを指定してください")

    if args.demo:
        print("[INFO] demo モード: 架空データ 20 件を使用", file=sys.stderr)
        rows = _create_sample_data()
    else:
        print(f"[INFO] CSV 読み込み: {args.input}", file=sys.stderr)
        try:
            rows = _load_csv(args.input)
        except (FileNotFoundError, OSError) as e:
            print(f"[ERROR] CSV 読み込み失敗: {e}", file=sys.stderr)
            sys.exit(1)

    print(f"[INFO] 分析対象: {len(rows)} 件", file=sys.stderr)
    analysis = _analyze(rows, args.industry)

    if args.json:
        print(json.dumps(analysis, ensure_ascii=False, indent=2))
        return

    template_text = ""
    if not args.dry_run:
        config = _load_config()
        api_key = config.get("api_key", "")
        if not api_key:
            print("[WARN] api_key が config_claude.json に見つかりません。文面生成をスキップします。", file=sys.stderr)
            args.dry_run = True
        else:
            print("[INFO] Claude API 呼び出し中...", file=sys.stderr)
            try:
                template_text = _call_claude(analysis, api_key)
                print("[OK]  Claude API 文面生成完了", file=sys.stderr)
            except Exception as e:
                print(f"[WARN] Claude API 呼び出し失敗: {e}", file=sys.stderr)
                template_text = f"[ERROR] API 呼び出し失敗: {e}"

    report = _build_report(analysis, template_text, args.dry_run)
    print(report)

    if args.output:
        output_path = os.path.abspath(args.output)
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"[OK]  レポート書き込み完了: {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
