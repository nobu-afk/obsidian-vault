#!/usr/bin/env python3
"""
Gravity CODE — ソースコード解析レポート自動生成スクリプト

セッション入力シート（Markdown）を読み込み、
Claude APIでソースコード解析レポートを生成する。

使い方:
  python3 gravity_code_report.py <入力シートのパス> [出力先パス]

例:
  python3 gravity_code_report.py input.md output.md
"""

import sys
import os
import re
from datetime import date

# --- Claude API ---
try:
    from anthropic import Anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False


def parse_session_sheet(filepath: str) -> dict:
    """セッション入力シートのMarkdownをパースして辞書に変換"""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    data = {}

    # 基本情報（YAML部分）
    yaml_match = re.search(r"```yaml\n(.*?)```", content, re.DOTALL)
    if yaml_match:
        for line in yaml_match.group(1).strip().split("\n"):
            if ":" in line:
                key, val = line.split(":", 1)
                data[key.strip()] = val.strip()

    # 各セクションのコードブロックを抽出
    sections = re.findall(
        r"(?:^|\n)(?:###?\s+.+\n+)?(?:\*\*Q[：:].*?\*\*\n+)?```\n(.*?)```",
        content,
        re.DOTALL,
    )
    data["raw_sections"] = [s.strip() for s in sections if s.strip()]

    # 石井メモを抽出
    memos = re.findall(r"石井メモ[：:]\n```\n(.*?)```", content, re.DOTALL)
    data["analyst_memos"] = [m.strip() for m in memos if m.strip()]

    # 総合分析メモを抽出
    analysis_match = re.search(
        r"## 石井の総合分析メモ\n(.*?)$", content, re.DOTALL
    )
    if analysis_match:
        data["total_analysis"] = analysis_match.group(1).strip()

    return data


def build_prompt(data: dict) -> str:
    """Claude APIに送るプロンプトを構築"""
    client_name = data.get("client_name", "（未記入）")

    prompt = f"""あなたはGravity CODEのソースコード解析エンジンです。
以下のセッション記録を分析し、「ソースコード解析レポート」を生成してください。

## 分析の原則

### 核心：動詞で定義する
- クライアントの本質を「名詞（肩書き・属性）」ではなく「動詞（機能・動作）」で定義すること
- 「マーケター」「経営者」は名詞であり本質ではない
- 「検知する」「接続する」「再設計する」が本質（関数）である

### want toの抽出方法
- 「権威者に禁止されたのに、やってしまっていたこと」がwant toの原石
- 行動の「結果」ではなく、行動を「引き起こす源泉にある動作」を抽出する
- 複数のエピソードに共通して繰り返されている「動作パターン」を動詞で特定する

### have toの検知
- 「こうあるべき」「普通は〜する」と語られる自己定義はhave toの可能性が高い
- 本人が語る自己像と、エピソードから浮かび上がる動作パターンのズレがhave toの証拠

## クライアント情報

- 名前：{client_name}
- 役割：{data.get('client_role', '（未記入）')}
- 入力データ：{data.get('input_data', 'セッション対話ログ')}

## セッション記録・分析メモ

"""

    # セッション回答を追加
    if data.get("raw_sections"):
        prompt += "### セッション回答\n\n"
        for i, section in enumerate(data["raw_sections"], 1):
            prompt += f"【回答{i}】\n{section}\n\n"

    # 分析メモを追加
    if data.get("analyst_memos"):
        prompt += "### アナリストメモ\n\n"
        for i, memo in enumerate(data["analyst_memos"], 1):
            prompt += f"【メモ{i}】\n{memo}\n\n"

    # 総合分析を追加
    if data.get("total_analysis"):
        prompt += f"### 総合分析\n\n{data['total_analysis']}\n\n"

    prompt += f"""## 出力フォーマット

以下の構成でMarkdownを出力してください。断定的・構造的な文体で。
曖昧な表現（「〜かもしれません」「〜と思われます」）は避けてください。

---

# {client_name} ── ソースコード解析レポート

## 1. サマリー
「{client_name}とは、〇〇する機能である。」を一文で定義。
動詞の連鎖（コアプロセス）を「>」で記述。

## 2. 駆動源
- エンジンの正体
- 発火条件（番号付きリスト、各条件にエピソードを根拠として添える）
- 停止条件（番号付きリスト、各条件にエピソードを根拠として添える）

## 3. フィルター
- 適合度が高い環境（3-5個）
- 適合度が低い環境（3-5個）
- have toの検出結果（検出されたもの各々に「検出N」のラベルを付ける）

## 4. 実行パターン
- コアプロセス（動詞の連鎖）
- 各動詞の説明（箇条書き）
- 強みが最大化する場面
- 精度が落ちる場面

## 5. 取扱説明書
- やるべきこと（3-5個、番号付き）
- やってはいけないこと（3-5個、番号付き）

## 推奨パス
以下の3つの選択肢から、この人に合ったものを提案：
- Gravity Coaching（have toの影響が大きい場合）
- Gravity Scan（組織の停滞が主因の場合）
- CODE単独完結（ソースコードが明確でhave toが軽微な場合）

> Analyst's Note：
> この人間のソースコードの特徴を1段落で総括

---

すべての記述に、セッション記録中の具体的なエピソード・発言を根拠として紐づけてください。
一般論や自己啓発的な表現は一切使わないこと。この人間にしか当てはまらない固有の記述をすること。
"""

    return prompt


def generate_with_claude(prompt: str) -> str:
    """Claude APIでレポートを生成"""
    client = Anthropic()
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=8000,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def generate_manual(data: dict, template_path: str) -> str:
    """Claude APIが使えない場合、テンプレートに分析メモを埋め込む"""
    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()

    replacements = {
        "{{client_name}}": data.get("client_name", "（未記入）"),
        "{{client_role}}": data.get("client_role", "（未記入）"),
        "{{input_data}}": data.get("input_data", "セッション対話ログ"),
        "{{session_date}}": data.get("session_date", "（未記入）"),
        "{{report_date}}": date.today().strftime("%Y-%m-%d"),
    }

    for key, val in replacements.items():
        template = template.replace(key, val)

    # 残りのプレースホルダーに分析メモを参照するよう注記
    template = re.sub(
        r"\{\{(\w+)\}\}",
        r"【要記入：\1 — 総合分析メモを参照して記入してください】",
        template,
    )

    return template


def main():
    if len(sys.argv) < 2:
        print("使い方: python3 gravity_code_report.py <入力シートのパス> [出力先パス]")
        sys.exit(1)

    input_path = sys.argv[1]
    if not os.path.exists(input_path):
        print(f"エラー: ファイルが見つかりません: {input_path}")
        sys.exit(1)

    # 出力先
    if len(sys.argv) >= 3:
        output_path = sys.argv[2]
    else:
        today = date.today().strftime("%y%m%d")
        output_path = os.path.join(
            os.path.dirname(input_path),
            f"{today}_ソースコード解析レポート.md",
        )

    print(f"入力: {input_path}")
    print(f"出力: {output_path}")

    # パース
    data = parse_session_sheet(input_path)
    print(f"  基本情報: {data.get('client_name', '?')} / {data.get('client_role', '?')}")
    print(f"  セッション回答: {len(data.get('raw_sections', []))}件")
    print(f"  アナリストメモ: {len(data.get('analyst_memos', []))}件")

    # 生成
    if HAS_ANTHROPIC and os.environ.get("ANTHROPIC_API_KEY"):
        print("\nClaude APIでレポートを生成中...")
        prompt = build_prompt(data)
        report = generate_with_claude(prompt)
        print("生成完了")
    else:
        print("\nClaude APIが利用できません。テンプレートベースで生成します。")
        template_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "..",
            "05_プロダクト",
            "GravityCode",
            "レポート",
        )
        template_path = os.path.join(
            template_dir, "テンプレート_ソースコード解析レポート.md"
        )
        if os.path.exists(template_path):
            report = generate_manual(data, template_path)
        else:
            print(f"テンプレートが見つかりません: {template_path}")
            sys.exit(1)

    # 書き出し
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\nレポートを保存しました: {output_path}")


if __name__ == "__main__":
    main()
