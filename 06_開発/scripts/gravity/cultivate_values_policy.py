"""
CT-2 VAL リュー × ポリシー実装エンジン（v1.0・260514）

経営者偏愛（passions.love / hate）から VAL リュー 10 件 → 行動ポリシー 50 件を自動生成。
Cultivate v2.0「挑戦磁場」エージェントの核。

使い方:
  python3 cultivate_values_policy.py --input <JSON_PATH> --output <OUTPUT_PATH>
  python3 cultivate_values_policy.py --demo
  python3 cultivate_values_policy.py --demo --dry-run

入力スキーマ（JSON）:
  CT-1 と同じ ceo_profile_*.json（または単独入力）
  必須フィールド: ceo_name, company, passions.love, passions.hate

出力:
  - <OUTPUT_PATH>.md：Markdown レポート（A4 4-5p）
  - <OUTPUT_PATH>.json：JSON 構造化データ（VAL リュー 10 件 × ポリシー 50 件）
"""

import os
import sys
import json
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _common.claude_client import (
    call_claude, load_input_json, save_output, save_json,
    mask_name, now_jst_str, parse_claude_json, md_h1, md_h2, md_h3,
    md_table, md_blockquote, md_footer,
)

SYSTEM_PROMPT = """\
あなたは Gravity Cultivate の「VAL リュー × ポリシー設計」の専門 AI です。
経営者の偏愛（love / hate）を入力として受け取り、VAL リュー 10 件とポリシー各 5 件（計 50 件）を
日本語で生成してください。

## VAL リュー命名規則
- 偏愛 love / hate から本質を抽出した動詞ベースまたは比喩ベースの命名
- ぶつ切り単語（名詞のみ）禁則。「〇〇する」「〇〇である」「〇〇を大切にする」の動的形式
- 例：「根拠なき議論は廃する」「才能の芽を見抜き、育てる」「疑問を口にする勇気を称える」

## 出力形式（JSON のみ・他のテキスト禁止）

```json
{
  "values": [
    {
      "id": "V01",
      "name": "VAL リュー名（動詞形式）",
      "definition": "1 行定義（20-40 字）",
      "source_passion": "love または hate のどの偏愛から来ているか（元の言葉を引用）",
      "intensity": "core / strong / standard のいずれか",
      "policies": [
        {"id": "P01", "behavior": "推奨行動（動詞始まり・具体的）", "context": "どの場面でその行動をとるか"},
        {"id": "P02", "behavior": "推奨行動 2", "context": "場面 2"},
        {"id": "P03", "behavior": "推奨行動 3", "context": "場面 3"},
        {"id": "P04", "behavior": "推奨行動 4", "context": "場面 4"},
        {"id": "P05", "behavior": "推奨行動 5", "context": "場面 5"}
      ]
    }
  ]
}
```

## 制約
- values は必ず 10 件。
- 各 VAL リューに必ず 5 件のポリシー。
- intensity：love からの抽出は "core" / "strong" が多く、hate からの反転抽出は "standard" が多い。
- policies の id は V01-P01〜V10-P05 の連番形式（V01-P01, V01-P02, ..., V10-P05）。
- JSON 以外のテキストを出力しないこと。
"""


def _create_sample_input() -> dict:
    return {
        "ceo_name": "田中 拓海",
        "company": "株式会社テックドライブ",
        "why": "すべての人が自分の才能を最大限に発揮し、仕事を通じて本当の意味で成長できる組織を作ること",
        "talents": ["複雑な問題を構造化して整理する力", "人の強みを見抜いて引き出す力", "高速で仮説検証するマインドセット"],
        "passions": {
            "love": ["データに基づく意思決定", "メンバーの成長瞬間に立ち会うこと", "業界の常識を疑うこと"],
            "hate": ["慣習だけで動く意思決定", "人の可能性を狭める評価システム", "スピードなき完璧主義"]
        },
        "industry": "SaaS / HRテクノロジー"
    }


def _build_user_prompt(data: dict, masked_name: str) -> str:
    love = data.get("passions", {}).get("love", [])
    hate = data.get("passions", {}).get("hate", [])
    return f"""経営者プロファイルを以下に示します。VAL リュー 10 件とポリシー 50 件を生成してください。

## 経営者プロファイル
- 経営者名：{masked_name}
- 会社名：{data.get('company', '')}
- 業界：{data.get('industry', '')}
- Why：{data.get('why', '')}
- 才能：{', '.join(data.get('talents', []))}
- 偏愛（love）：{', '.join(love)}
- 偏愛（hate）：{', '.join(hate)}

love の数：{len(love)} 件、hate の数：{len(hate)} 件から合計 10 VAL リューを設計してください。
"""


def _mock_output(data: dict, masked_name: str) -> dict:
    love = data.get("passions", {}).get("love", ["成長", "データ", "挑戦"])
    hate = data.get("passions", {}).get("hate", ["慣習", "停滞", "臆病"])
    values = []
    names = [
        "根拠をもって語る", "成長の瞬間を称える", "常識を問い直す",
        "慣習より証拠を選ぶ", "才能の芽を見抜き育てる", "スピードで学ぶ",
        "失敗を教材にする", "可能性に境界線を引かない", "仲間の挑戦を物語にする", "共に達成し次を目指す"
    ]
    sources = love[:3] + [f"hate: {h}" for h in hate[:3]] + love[:2] + hate[:2]
    for i in range(10):
        vid = f"V{i+1:02d}"
        policies = [
            {
                "id": f"{vid}-P{j+1:02d}",
                "behavior": f"週次 1on1 で行動 {j+1} を実践する",
                "context": f"チームミーティングまたは個別面談の場面 {j+1}"
            }
            for j in range(5)
        ]
        values.append({
            "id": vid,
            "name": names[i],
            "definition": f"{names[i]}ことで組織の引力を高め、事業成長を実現する",
            "source_passion": sources[i] if i < len(sources) else love[0],
            "intensity": "core" if i < 3 else ("strong" if i < 6 else "standard"),
            "policies": policies
        })
    return {"values": values}


def _build_markdown(data: dict, result: dict, masked_name: str, is_dry_run: bool) -> str:
    company = data.get("company", "")
    values = result.get("values", [])
    lines = []
    lines.append(md_h1(f"VAL リュー × ポリシー設計レポート — {company}"))
    lines.append(f"**経営者：** {masked_name}  ")
    lines.append(f"**生成日時：** {now_jst_str()}  ")
    lines.append(f"**VAL リュー数：** {len(values)} 件 / **ポリシー数：** {sum(len(v.get('policies', [])) for v in values)} 件")
    if is_dry_run:
        lines.append("\n> **[DRY-RUN]** Claude API は呼び出されていません。モックデータを使用。\n")

    lines.append(md_h2("VAL リュー一覧（10 件）"))
    core_vals = [v for v in values if v.get("intensity") == "core"]
    strong_vals = [v for v in values if v.get("intensity") == "strong"]
    std_vals = [v for v in values if v.get("intensity") == "standard"]

    intensity_label = {"core": "コア（最重要）", "strong": "強（重要）", "standard": "標準"}
    lines.append(md_table(
        ["ID", "VAL リュー名", "定義", "強度", "源泉"],
        [
            [v["id"], f"**{v['name']}**", v["definition"], intensity_label.get(v.get("intensity", ""), ""), v.get("source_passion", "")]
            for v in values
        ]
    ))

    lines.append(md_h2("各 VAL リューの詳細 × ポリシー"))
    for v in values:
        vid = v.get("id", "")
        name = v.get("name", "")
        defn = v.get("definition", "")
        src = v.get("source_passion", "")
        policies = v.get("policies", [])
        lines.append(md_h3(f"{vid}. {name}"))
        lines.append(f"**定義：** {defn}  ")
        lines.append(f"**源泉：** {src}\n")
        lines.append(md_table(
            ["ポリシー ID", "推奨行動", "場面"],
            [[p.get("id", ""), p.get("behavior", ""), p.get("context", "")] for p in policies]
        ))

    lines.append(md_h2("VAL リュー × ポリシー集計"))
    lines.append(md_table(
        ["強度", "件数", "VAL リュー"],
        [
            ["コア（最重要）", len(core_vals), " / ".join(v["name"] for v in core_vals)],
            ["強（重要）", len(strong_vals), " / ".join(v["name"] for v in strong_vals)],
            ["標準", len(std_vals), " / ".join(v["name"] for v in std_vals)],
        ]
    ))
    lines.append(f"\n**総ポリシー数：** {sum(len(v.get('policies', [])) for v in values)} 件\n")

    lines.append(md_h2("導入・運用ガイド"))
    lines.append("> **挑戦磁場への接続：** このポリシー集は Cultivate v2.0「挑戦磁場」の行動仕様として機能します。")
    lines.append("> - 週次ウィンセッションで Core VAL リューに紐づくポリシーの実践事例を共有")
    lines.append("> - 月次定例でポリシーの実装率をスコア化（Verbal Persuasion 源泉として CE 構築に活用）")
    lines.append("> - 四半期ごとに「有名無実化したポリシー」を廃止・「新規追加候補」を経営者と協議\n")

    lines.append(md_footer("cultivate_values_policy.py"))
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="CT-2 VAL リュー × ポリシー実装エンジン",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python3 cultivate_values_policy.py --demo
  python3 cultivate_values_policy.py --demo --dry-run
  python3 cultivate_values_policy.py --input profile.json --output report
  python3 cultivate_values_policy.py --input profile.json --output report --mask
        """,
    )
    parser.add_argument("--input", help="入力 JSON ファイルパス")
    parser.add_argument("--output", help="出力ファイルパス（拡張子なし。.md と .json を生成）")
    parser.add_argument("--demo", action="store_true", help="同梱サンプルプロファイルで動作確認")
    parser.add_argument("--dry-run", action="store_true", help="Claude API を呼ばず mock 出力を確認")
    parser.add_argument("--mask", action="store_true", help="経営者名を SHA256 短縮ハッシュ化")
    args = parser.parse_args()

    if not args.demo and not args.input:
        parser.error("--input または --demo のいずれかを指定してください。")

    if args.demo:
        data = _create_sample_input()
        output_base = args.output or os.path.join(SCRIPT_DIR, "cultivate_samples", "values_policy_demo")
        print("[INFO] --demo: サンプルプロファイルを使用します。", file=sys.stderr)
    else:
        data = load_input_json(args.input)
        if not args.output:
            parser.error("--output を指定してください。")
        output_base = args.output

    masked_name = mask_name(data.get("ceo_name", ""), args.mask)

    if args.dry_run:
        result = _mock_output(data, masked_name)
    else:
        user_prompt = _build_user_prompt(data, masked_name)
        raw = call_claude(SYSTEM_PROMPT, user_prompt, dry_run=False, max_tokens=6000)
        try:
            result = parse_claude_json(raw)
        except (json.JSONDecodeError, ValueError) as e:
            print(f"[WARN] JSON パース失敗: {e}。mock 出力にフォールバック。", file=sys.stderr)
            result = _mock_output(data, masked_name)

    if len(result.get("values", [])) != 10:
        print(f"[WARN] VAL リュー数が 10 件ではありません（{len(result.get('values', []))} 件）。", file=sys.stderr)

    md_text = _build_markdown(data, result, masked_name, args.dry_run)

    os.makedirs(os.path.dirname(os.path.abspath(output_base)), exist_ok=True)
    save_output(md_text, output_base + ".md")
    save_json(result, output_base + ".json")

    print(md_text)


if __name__ == "__main__":
    main()
