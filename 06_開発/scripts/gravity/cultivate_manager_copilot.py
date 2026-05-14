"""
CT-3 マネージャー副操縦士（v1.0・260514）

マネージャー個別のコンプレックス（弱点・成長課題）を入力し、
補完プログラム（学習・実践・対話設計）を自動生成する。
Cultivate v2.0「結束磁場」エージェントの核。

使い方:
  python3 cultivate_manager_copilot.py --input <JSON_PATH> --output <OUTPUT_PATH>
  python3 cultivate_manager_copilot.py --demo
  python3 cultivate_manager_copilot.py --demo --dry-run

入力スキーマ（JSON）:
  {
    "manager_name": "マネージャー名（ハッシュ化推奨）",
    "company": "会社名",
    "tenure_years": 5,
    "team_size": 8,
    "complexes": ["数字管理が苦手", "1on1 で空気を作れない"],
    "strengths": ["業務遂行力", "技術知見"],
    "kpis": {"team_engagement": 65, "1on1_freq_per_month": 1.5},
    "context": "200 字以内の自由記述"
  }

出力:
  - <OUTPUT_PATH>.md：Markdown レポート（A4 3-4p）
  - <OUTPUT_PATH>.json：JSON 構造化データ（補完プログラム全件）
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

MGMT_AXES = ["数字管理", "業務遂行", "ピープル", "引力相性"]

SYSTEM_PROMPT = """\
あなたは Gravity Cultivate の「マネージャー副操縦士」AI です。
マネージャーのコンプレックス（弱点・成長課題）と強みを入力として受け取り、
個別補完プログラムを日本語で生成してください。

## 出力形式（JSON のみ・他のテキスト禁止）

```json
{
  "summary": "このマネージャーの現状を 2 文で要約（強み + 主要コンプレックス）",
  "learning_resources": {
    "papers": [
      {"id": "P1", "title": "論文タイトル", "author": "著者名", "year": 2000, "relevance": "このマネージャーへの関連理由（1 文）"},
      {"id": "P2", "title": "論文タイトル 2", "author": "著者名 2", "year": 2001, "relevance": "関連理由"},
      {"id": "P3", "title": "論文タイトル 3", "author": "著者名 3", "year": 2002, "relevance": "関連理由"}
    ],
    "books": [
      {"id": "B1", "title": "書籍タイトル", "author": "著者名", "relevance": "関連理由（1 文）"},
      {"id": "B2", "title": "書籍タイトル 2", "author": "著者名 2", "relevance": "関連理由"}
    ],
    "videos": [
      {"id": "V1", "title": "動画・コンテンツタイトル", "source": "YouTube / Udemy 等", "relevance": "関連理由（1 文）"},
      {"id": "V2", "title": "動画・コンテンツタイトル 2", "source": "source 2", "relevance": "関連理由"}
    ]
  },
  "practice_program": {
    "one_on_one_script": [
      "1on1 改善スクリプト ステップ 1（冒頭の入り方）",
      "1on1 改善スクリプト ステップ 2（本題への橋渡し）",
      "1on1 改善スクリプト ステップ 3（深堀りフレーズ）",
      "1on1 改善スクリプト ステップ 4（振り返りと宿題設定）"
    ],
    "weekly_reflection_template": [
      "週次振り返りの設問 1（行動レベルでの問い）",
      "週次振り返りの設問 2（感情・エネルギーへの問い）",
      "週次振り返りの設問 3（チームへの影響への問い）",
      "週次振り返りの設問 4（来週へのコミット）"
    ],
    "kpi_actions": [
      {"kpi_key": "KPI 名称", "current": "現状値の説明", "target": "目標値の説明", "action": "具体的改善アクション（1 文）"},
      {"kpi_key": "KPI 名称 2", "current": "現状値 2", "target": "目標値 2", "action": "改善アクション 2"}
    ]
  },
  "dialogue_questions": [
    {"id": "Q01", "complex_target": "コンプレックスの名称（入力から引用）", "question": "1on1 で使う質問文（コーチング型・オープン質問）", "intent": "この質問で何を引き出したいか（1 文）"},
    {"id": "Q02", "complex_target": "コンプレックス 2", "question": "質問 2", "intent": "意図 2"},
    {"id": "Q03", "complex_target": "コンプレックス 3", "question": "質問 3", "intent": "意図 3"},
    {"id": "Q04", "complex_target": "コンプレックス 4", "question": "質問 4", "intent": "意図 4"},
    {"id": "Q05", "complex_target": "コンプレックス 5", "question": "質問 5", "intent": "意図 5"}
  ],
  "coverage_matrix": {
    "数字管理": {"level": "low / medium / high のいずれか", "reason": "判定理由（1 文）"},
    "業務遂行": {"level": "low / medium / high のいずれか", "reason": "判定理由（1 文）"},
    "ピープル": {"level": "low / medium / high のいずれか", "reason": "判定理由（1 文）"},
    "引力相性": {"level": "low / medium / high のいずれか", "reason": "判定理由（1 文）"}
  },
  "priority_message": "このマネージャーへの今月最優先メッセージ（経営者・事業部長に伝える 1 文）"
}
```

## 制約
- papers は必ず 3 件。実在する論文名（Bandura / Edmondson / Saks / Meyer-Allen 等の Cultivate 学術基盤から選ぶ）。
- books は必ず 2 件。実在する書籍名。
- videos は必ず 2 件。YouTube 等で実際に入手可能なコンテンツ。
- dialogue_questions はコンプレックス数が 5 件未満の場合でも 5-10 件を維持すること（複数の角度から同じコンプレックスを問う）。
- coverage_matrix の 4 軸は必ず評価すること。
- JSON 以外のテキストを出力しないこと。
"""


def _create_sample_input() -> dict:
    return {
        "manager_name": "佐藤 健一",
        "company": "株式会社テックドライブ",
        "tenure_years": 4,
        "team_size": 7,
        "complexes": [
            "数字管理が苦手（売上予測・工数管理を後回しにする）",
            "1on1 で場の空気を作れない（沈黙が怖くてすぐ話してしまう）",
            "メンバーの感情を読むのが苦手"
        ],
        "strengths": ["高い業務遂行力", "技術的な深い知見", "粘り強い問題解決"],
        "kpis": {
            "team_engagement": 62,
            "one_on_one_freq_per_month": 1.5,
            "task_completion_rate": 78
        },
        "context": "エンジニア出身でプレイヤーとして優秀だったが、マネージャー昇格後に部下との関係構築に課題を抱えている。数字で管理することに苦手意識があり、感覚で判断することが多い。"
    }


def _build_user_prompt(data: dict, masked_name: str) -> str:
    complexes = "\n".join(f"  - {c}" for c in data.get("complexes", []))
    strengths = "\n".join(f"  - {s}" for s in data.get("strengths", []))
    kpis = "\n".join(f"  - {k}: {v}" for k, v in data.get("kpis", {}).items())
    return f"""マネージャープロファイルを以下に示します。個別補完プログラムを生成してください。

## マネージャープロファイル
- 名前：{masked_name}
- 会社：{data.get('company', '')}
- マネージャー歴：{data.get('tenure_years', '')} 年
- チームサイズ：{data.get('team_size', '')} 名

## コンプレックス（弱点・成長課題）
{complexes}

## 強み
{strengths}

## KPI 現状
{kpis}

## 自由記述コンテキスト
{data.get('context', '')}
"""


def _mock_output(data: dict, masked_name: str) -> dict:
    complexes = data.get("complexes", ["課題 1", "課題 2", "課題 3"])
    return {
        "summary": f"{masked_name}は業務遂行力に強みを持つ一方、{complexes[0]}と{complexes[1] if len(complexes) > 1 else '対人関係'}に課題がある。",
        "learning_resources": {
            "papers": [
                {"id": "P1", "title": "The Impact of Self-Efficacy on Motivation and Performance", "author": "Bandura, A.", "year": 1977, "relevance": "自己効力感の 4 源泉（達成体験）が 1on1 設計の学術根拠"},
                {"id": "P2", "title": "Psychological Safety and Learning Behavior in Work Teams", "author": "Edmondson, A.", "year": 1999, "relevance": "心理的安全性の構築が 1on1 での沈黙活用に直結"},
                {"id": "P3", "title": "Antecedents and Consequences of Employee Engagement", "author": "Saks, A. M.", "year": 2006, "relevance": "エンゲージメントの Job × Organization 2 軸が KPI 設計の基盤"}
            ],
            "books": [
                {"id": "B1", "title": "コーチング・バイブル（第 4 版）", "author": "ヘンリー・キムジーハウス ほか", "relevance": "オープン質問と傾聴の実践スクリプトが 1on1 改善に直結"},
                {"id": "B2", "title": "HIGH OUTPUT MANAGEMENT", "author": "アンドリュー・S・グローブ", "relevance": "数字管理・業績評価の実践フレームがコンプレックス補完の核"}
            ],
            "videos": [
                {"id": "V1", "title": "How Great Managers Coach Their Teams", "source": "YouTube - Google re:Work", "relevance": "1on1 の場の作り方を映像で体感できる"},
                {"id": "V2", "title": "データドリブン意思決定 入門", "source": "YouTube - ビジネス統計学チャンネル", "relevance": "数字管理への苦手意識を体系的に解消する入門コンテンツ"}
            ]
        },
        "practice_program": {
            "one_on_one_script": [
                "「今週、一番エネルギーを使ったのはどんな場面でしたか？」（感情から入る）",
                "「その場面で、自分がうまくできたと感じた点は？」（達成体験を引き出す）",
                "「来週、一つだけ変えるとしたら何ですか？」（具体行動にコミット）",
                "「私からできる支援は何かありますか？」（関係構築で締める）"
            ],
            "weekly_reflection_template": [
                "今週、自分が最も集中できた業務は何でしたか？",
                "チームの誰かが成長した瞬間に気づきましたか？",
                "自分のエネルギーが下がった場面はどこですか？",
                "来週、チームとして達成したい小さな成功は何ですか？"
            ],
            "kpi_actions": [
                {"kpi_key": "エンゲージメントスコア", "current": "62（要改善水準）", "target": "75 以上", "action": "週 1 回の 1on1 を 30 分確保し、業務指示より感情確認を優先する"},
                {"kpi_key": "1on1 実施頻度", "current": "月 1.5 回", "target": "月 4 回（毎週）", "action": "カレンダーに毎週固定枠を入れ、スキップ率 0% を 3 ヶ月続ける"}
            ]
        },
        "dialogue_questions": [
            {"id": "Q01", "complex_target": complexes[0], "question": "数字を見るとき、どんな感情が湧きますか？", "intent": "数字への感情的ブロックを言語化させる"},
            {"id": "Q02", "complex_target": complexes[0], "question": "チームの数字が悪かったとき、最初に何を確認しますか？", "intent": "数字管理の現状パターンを把握する"},
            {"id": "Q03", "complex_target": complexes[1] if len(complexes) > 1 else complexes[0], "question": "1on1 で沈黙が 3 秒続いたとき、何が頭をよぎりますか？", "intent": "沈黙への恐怖の根源を探る"},
            {"id": "Q04", "complex_target": complexes[1] if len(complexes) > 1 else complexes[0], "question": "相手が話しやすい 1on1 と、話しにくい 1on1 の違いは何だと思いますか？", "intent": "心理的安全性の自己認識を引き出す"},
            {"id": "Q05", "complex_target": complexes[2] if len(complexes) > 2 else complexes[0], "question": "メンバーの「調子が悪そう」と感じた瞬間を、最近いつ体験しましたか？", "intent": "感情読み取りの実体験を掘り起こす"}
        ],
        "coverage_matrix": {
            "数字管理": {"level": "low", "reason": "コンプレックスの第一項目であり、週次 KPI 管理の習慣が未定着"},
            "業務遂行": {"level": "high", "reason": "強みフィールドに明記あり・タスク完了率 78% も実力を裏付ける"},
            "ピープル": {"level": "medium", "reason": "1on1 実施はあるが頻度・質ともに改善余地あり"},
            "引力相性": {"level": "medium", "reason": "技術志向 × Why 不明確のため、組織引力との接続は今後のコーチングで深堀りが必要"}
        },
        "priority_message": f"{masked_name}の今月最優先は「毎週 1on1 を 30 分固定で実施し、業務指示より感情確認を 1 件以上行う」ことです。"
    }


def _level_bar(level: str) -> str:
    mapping = {"low": "█░░ 低", "medium": "██░ 中", "high": "███ 高"}
    return mapping.get(level, level)


def _build_markdown(data: dict, result: dict, masked_name: str, is_dry_run: bool) -> str:
    company = data.get("company", "")
    lines = []
    lines.append(md_h1(f"マネージャー個別補完プログラム — {masked_name}"))
    lines.append(f"**所属：** {company}  ")
    lines.append(f"**マネージャー歴：** {data.get('tenure_years', '')} 年 / **チームサイズ：** {data.get('team_size', '')} 名  ")
    lines.append(f"**生成日時：** {now_jst_str()}")
    if is_dry_run:
        lines.append("\n> **[DRY-RUN]** Claude API は呼び出されていません。モックデータを使用。\n")

    lines.append(md_h2("現状サマリー"))
    lines.append(md_blockquote(result.get("summary", "")))

    lines.append(md_h2("1. 学習リソース"))

    papers = result.get("learning_resources", {}).get("papers", [])
    lines.append(md_h3("論文（3 本）"))
    lines.append(md_table(
        ["ID", "タイトル", "著者 / 年", "このマネージャーへの関連"],
        [[p["id"], p["title"], f"{p.get('author', '')} ({p.get('year', '')})", p.get("relevance", "")] for p in papers]
    ))

    books = result.get("learning_resources", {}).get("books", [])
    lines.append(md_h3("書籍（2 冊）"))
    lines.append(md_table(
        ["ID", "タイトル", "著者", "関連理由"],
        [[b["id"], b["title"], b.get("author", ""), b.get("relevance", "")] for b in books]
    ))

    videos = result.get("learning_resources", {}).get("videos", [])
    lines.append(md_h3("動画・コンテンツ（2 本）"))
    lines.append(md_table(
        ["ID", "タイトル", "ソース", "関連理由"],
        [[v["id"], v["title"], v.get("source", ""), v.get("relevance", "")] for v in videos]
    ))

    lines.append(md_h2("2. 実践プログラム"))

    practice = result.get("practice_program", {})
    lines.append(md_h3("1on1 改善スクリプト"))
    for i, step in enumerate(practice.get("one_on_one_script", []), 1):
        lines.append(f"**Step {i}：** {step}  ")

    lines.append(md_h3("週次振り返りテンプレート"))
    for i, q in enumerate(practice.get("weekly_reflection_template", []), 1):
        lines.append(f"{i}. {q}")

    lines.append(md_h3("KPI 改善アクション"))
    kpi_actions = practice.get("kpi_actions", [])
    if kpi_actions:
        lines.append(md_table(
            ["KPI", "現状", "目標", "改善アクション"],
            [[a.get("kpi_key", ""), a.get("current", ""), a.get("target", ""), a.get("action", "")] for a in kpi_actions]
        ))

    lines.append(md_h2("3. 対話設計（コンプレックス別質問テンプレート）"))
    dialogue = result.get("dialogue_questions", [])
    lines.append(md_table(
        ["ID", "対象コンプレックス", "質問文", "引き出したい意図"],
        [[q["id"], q.get("complex_target", ""), q.get("question", ""), q.get("intent", "")] for q in dialogue]
    ))

    lines.append(md_h2("4. 4 マネジメント × カバレッジマトリクス"))
    matrix = result.get("coverage_matrix", {})
    lines.append(md_table(
        ["軸", "カバレッジ", "判定理由"],
        [[axis, _level_bar(matrix.get(axis, {}).get("level", "")), matrix.get(axis, {}).get("reason", "")] for axis in MGMT_AXES]
    ))

    lines.append(md_h2("5. 今月の優先メッセージ"))
    lines.append(md_blockquote(result.get("priority_message", "")))

    lines.append("\n> **引き渡し先：** 経営者・事業部長への月次定例報告資料に転記し、Cultivate 月次コーチング前日の CT-6 事前準備レポートと合わせて活用。\n")

    lines.append(md_footer("cultivate_manager_copilot.py"))
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="CT-3 マネージャー副操縦士",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python3 cultivate_manager_copilot.py --demo
  python3 cultivate_manager_copilot.py --demo --dry-run
  python3 cultivate_manager_copilot.py --input manager.json --output report
  python3 cultivate_manager_copilot.py --input manager.json --output report --mask
        """,
    )
    parser.add_argument("--input", help="入力 JSON ファイルパス")
    parser.add_argument("--output", help="出力ファイルパス（拡張子なし。.md と .json を生成）")
    parser.add_argument("--demo", action="store_true", help="同梱サンプルプロファイルで動作確認")
    parser.add_argument("--dry-run", action="store_true", help="Claude API を呼ばず mock 出力を確認")
    parser.add_argument("--mask", action="store_true", help="マネージャー名を SHA256 短縮ハッシュ化")
    args = parser.parse_args()

    if not args.demo and not args.input:
        parser.error("--input または --demo のいずれかを指定してください。")

    if args.demo:
        data = _create_sample_input()
        output_base = args.output or os.path.join(SCRIPT_DIR, "cultivate_samples", "manager_copilot_demo")
        print("[INFO] --demo: サンプルマネージャープロファイルを使用します。", file=sys.stderr)
    else:
        data = load_input_json(args.input)
        if not args.output:
            parser.error("--output を指定してください。")
        output_base = args.output

    masked_name = mask_name(data.get("manager_name", ""), args.mask)

    if args.dry_run:
        result = _mock_output(data, masked_name)
    else:
        user_prompt = _build_user_prompt(data, masked_name)
        raw = call_claude(SYSTEM_PROMPT, user_prompt, dry_run=False, max_tokens=5000)
        try:
            result = parse_claude_json(raw)
        except (json.JSONDecodeError, ValueError) as e:
            print(f"[WARN] JSON パース失敗: {e}。mock 出力にフォールバック。", file=sys.stderr)
            result = _mock_output(data, masked_name)

    md_text = _build_markdown(data, result, masked_name, args.dry_run)

    os.makedirs(os.path.dirname(os.path.abspath(output_base)), exist_ok=True)
    save_output(md_text, output_base + ".md")
    save_json(result, output_base + ".json")

    print(md_text)


if __name__ == "__main__":
    main()
