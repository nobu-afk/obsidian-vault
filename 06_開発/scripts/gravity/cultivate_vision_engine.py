"""
CT-1 引力 → 躍動ビジョンエンジン（v1.0・260514）

経営者の Why × 才能 × 偏愛 入力から、文化 3 層（表層行動 / 中層信念 / 深層 Why）
+ 8 類型マッピングを自動生成する。Cultivate v2.0「学習磁場」エージェントの核。

使い方:
  python3 cultivate_vision_engine.py --input <JSON_PATH> --output <OUTPUT_PATH>
  python3 cultivate_vision_engine.py --demo
  python3 cultivate_vision_engine.py --demo --dry-run

入力スキーマ（JSON）:
  {
    "ceo_name": "経営者名",
    "company": "会社名",
    "why": "Why 文",
    "talents": ["才能 1", "才能 2", "才能 3"],
    "passions": {"love": ["偏愛 1", "偏愛 2"], "hate": ["嫌い 1", "嫌い 2"]},
    "industry": "業界"
  }

出力:
  - <OUTPUT_PATH>.md：Markdown レポート（A4 2-3p）
  - <OUTPUT_PATH>.json：JSON 構造化データ（文化 3 層 + 8 類型マッピング）
"""

import os
import sys
import json
import argparse

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _common.claude_client import (
    call_claude, load_input_json, save_output, save_json,
    mask_name, now_jst_str, parse_claude_json, md_h1, md_h2, md_h3,
    md_table, md_blockquote, md_footer, run_cultivate_pipeline,
)

ARCHETYPE_LABELS = [
    "探求型", "職人型", "連帯型", "挑戦型",
    "革新型", "育成型", "効率型", "共創型",
]

SYSTEM_PROMPT = """\
あなたは Gravity Cultivate の「文化ビジョン設計」の専門 AI です。
経営者の Why × 才能 × 偏愛を入力として受け取り、以下を日本語で生成してください。

## 出力形式（JSON のみ・他のテキスト禁止）

```json
{
  "culture_layers": {
    "surface": {
      "label": "表層行動（B-1）",
      "behaviors": ["行動例 1", "行動例 2", "行動例 3", "行動例 4", "行動例 5"]
    },
    "mid": {
      "label": "中層信念（B-2）",
      "beliefs": ["信念 1", "信念 2", "信念 3"]
    },
    "deep": {
      "label": "深層 Why（B-3）",
      "why_statement": "Why を 1-2 文で凝縮した宣言文",
      "source": "Why × 才能 × 偏愛のどの組み合わせから来ているかの説明"
    }
  },
  "archetype_mapping": {
    "primary": "8 類型のうち最も強く該当する 1 類型の名称",
    "secondary": "次点の 1 類型の名称",
    "rationale": "判定理由（偏愛・才能・Why から 3 文以内）",
    "archetype_scores": {
      "探求型": 0,
      "職人型": 0,
      "連帯型": 0,
      "挑戦型": 0,
      "革新型": 0,
      "育成型": 0,
      "効率型": 0,
      "共創型": 0
    }
  },
  "vision_statement": "経営者の引力から導いた組織ビジョン文（1 文・具体的・「〜する組織」形式）",
  "learning_field_theme": "学習磁場で重点的に構築する達成体験のテーマ（1 文）"
}
```

## 制約
- archetype_scores の合計は 100。各類型は 0-40 の範囲で配分。
- behaviors は動詞始まりの具体行動（「〇〇する」「〇〇を確認する」等）。
- beliefs は「〇〇であるべき」「〇〇が正しい」等の信念文。
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
    return f"""経営者プロファイルを以下に示します。文化 3 層 + 8 類型マッピングを生成してください。

## 経営者プロファイル
- 経営者名：{masked_name}
- 会社名：{data.get('company', '')}
- 業界：{data.get('industry', '')}
- Why：{data.get('why', '')}
- 才能：{', '.join(data.get('talents', []))}
- 偏愛（love）：{', '.join(data.get('passions', {}).get('love', []))}
- 偏愛（hate）：{', '.join(data.get('passions', {}).get('hate', []))}
"""


def _mock_output(data: dict, masked_name: str) -> dict:
    return {
        "culture_layers": {
            "surface": {
                "label": "表層行動（B-1）",
                "behaviors": [
                    "週次 1on1 で相手の成長目標を必ず確認する",
                    "意思決定の根拠をデータで示す",
                    "仮説と検証結果をチームで共有する",
                    "失敗事例を学習機会として全員と振り返る",
                    "業界通説に対して「本当にそうか？」と問い直す"
                ]
            },
            "mid": {
                "label": "中層信念（B-2）",
                "beliefs": [
                    "人は正しい環境と機会があれば必ず成長できる",
                    "データなき議論は感情論に過ぎない",
                    "スピードと学習の掛け算が唯一の競争優位である"
                ]
            },
            "deep": {
                "label": "深層 Why（B-3）",
                "why_statement": f"すべての才能が解き放たれ、仕事そのものが成長の場になる組織を{masked_name}は作り続ける。",
                "source": "「人の強みを引き出す才能」×「成長瞬間への偏愛」×「可能性を狭める評価への嫌悪」の交点から来ている"
            }
        },
        "archetype_mapping": {
            "primary": "育成型",
            "secondary": "探求型",
            "rationale": f"{masked_name}の「人の強みを見抜いて引き出す才能」と「成長瞬間への偏愛」は育成型の核心。同時に「データ × 仮説検証」への強い引力が探求型の特性を色濃く示す。",
            "archetype_scores": {
                "探求型": 25, "職人型": 5, "連帯型": 10, "挑戦型": 15,
                "革新型": 10, "育成型": 30, "効率型": 3, "共創型": 2
            }
        },
        "vision_statement": "一人ひとりが才能の根拠を持ち、仮説と達成の連鎖で事業部売上 1.5 倍を実現し続ける組織",
        "learning_field_theme": "「小さな達成体験 × データ可視化」で個人の自己効力感を週次で積み上げる学習磁場"
    }


def _build_markdown(data: dict, result: dict, masked_name: str, is_dry_run: bool) -> str:
    company = data.get("company", "")
    lines = []
    lines.append(md_h1(f"文化ビジョン設計レポート — {company}"))
    lines.append(f"**経営者：** {masked_name}  ")
    lines.append(f"**業界：** {data.get('industry', '')}  ")
    lines.append(f"**生成日時：** {now_jst_str()}")
    if is_dry_run:
        lines.append("\n> **[DRY-RUN]** Claude API は呼び出されていません。モックデータを使用。\n")

    lines.append(md_h2("1. 深層 Why（引力の根源）"))
    deep = result.get("culture_layers", {}).get("deep", {})
    lines.append(md_blockquote(deep.get("why_statement", "")))
    lines.append(f"\n**源泉：** {deep.get('source', '')}\n")

    lines.append(md_h2("2. 文化 3 層構造"))

    mid = result.get("culture_layers", {}).get("mid", {})
    lines.append(md_h3("中層信念（B-2）"))
    for belief in mid.get("beliefs", []):
        lines.append(f"- {belief}")

    surface = result.get("culture_layers", {}).get("surface", {})
    lines.append(md_h3("表層行動（B-1）"))
    lines.append(md_table(
        ["#", "推奨行動"],
        [[i + 1, b] for i, b in enumerate(surface.get("behaviors", []))]
    ))

    lines.append(md_h2("3. 8 類型マッピング"))
    arch = result.get("archetype_mapping", {})
    lines.append(f"**主類型：** {arch.get('primary', '')}  ")
    lines.append(f"**副類型：** {arch.get('secondary', '')}  ")
    lines.append(f"\n**判定理由：** {arch.get('rationale', '')}\n")

    scores = arch.get("archetype_scores", {})
    lines.append(md_table(
        ["類型", "スコア（合計 100）", "比率"],
        [
            [k, v, "█" * (v // 5) + f" {v}"]
            for k, v in sorted(scores.items(), key=lambda x: -x[1])
        ]
    ))

    lines.append(md_h2("4. 組織ビジョン文"))
    lines.append(md_blockquote(result.get("vision_statement", "")))

    lines.append(md_h2("5. 学習磁場テーマ（CT-1 設計指針）"))
    lines.append(f"> {result.get('learning_field_theme', '')}\n")

    lines.append(md_footer("cultivate_vision_engine.py"))
    return "\n".join(lines)

def main() -> None:
    run_cultivate_pipeline(
        description="CT-1 引力 → 躍動ビジョンエンジン",
        demo_basename="vision_engine_demo",
        name_field="ceo_name",
        mask_help="経営者名を SHA256 短縮ハッシュ化",
        system_prompt=SYSTEM_PROMPT,
        sample_fn=_create_sample_input,
        mock_fn=_mock_output,
        user_prompt_fn=_build_user_prompt,
        build_md_fn=_build_markdown,
        max_tokens=4096,
        script_dir=SCRIPT_DIR,
        script_name=os.path.basename(__file__),
    )


if __name__ == "__main__":
    main()
