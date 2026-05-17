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
    """Claude APIに送るプロンプトを構築（Gravity CODE レポート v2.0・260517）"""
    client_name = data.get("client_name", "（未記入）")

    prompt = f"""あなたは Gravity CODE の引力解析エンジンです。
40 分の対話セッション記録を分析し、「あなたに人が集まる理由レポート」を生成してください。

## レポートの目的（最重要・LP の約束）

このレポートは「**あなたに人が集まる理由**」を経営者本人に返すものです。
顧客像（誰が集まるか）の描写ではなく、**経営者本人の魅力源（なぜ集まるか）を 1 文で言語化**することが核心です。

## 分析フレーム：強み × 想い × 偏愛

経営者個人の引力は次の 3 要素で記述します。**この 3 要素以外の用語（Why／才能／want to／have to／ソースコード／動詞解析）は出力に使わないこと**。
これらは社内設計用語であり、レポートでは強み・想い・偏愛・引力・魅力で統一します。

- **強み（Talent）**：頼まれなくても自然にできてしまう動きと、それが発揮される場（関係・場・時間）
- **想い（Why）**：何をするときに自分が燃えるか。富や評価を取り除いても残る、本音の動機
- **偏愛（Passion）**：譲れない好みと、絶対に選ばない嫌い。経営判断の根底にある好き嫌いの軸

3 要素は別々に立つのではなく、互いに引き合って初めて「引力」になります。

## 4 型判定

3 要素の整合度で 4 型に必ず分類します（表記は固定・接頭辞「個人」を必ず付ける）：

1. **個人整合型** — 3 要素が揃った状態
2. **個人想いズレ型** — 想いが社会的期待・過去の成功体験で塗り替えられている
3. **個人強みズレ型** — 本来の動きでなく「こうあるべき」で仕事をしている
4. **個人偏愛ズレ型** — 譲れない好みでなく社会の期待で判断軸ができている

## 4 型 → 次の一手（固定マッピング・絶対遵守）

| 4 型判定 | RECOMMENDED |
|---|---|
| 個人整合型 | 無料 Web 診断 → Gravity（組織の引力設計プログラム） |
| 個人想いズレ型 | Gravity Coaching |
| 個人強みズレ型 | Gravity Coaching |
| 個人偏愛ズレ型 | Gravity Coaching |

**禁則用語（絶対に使わない）**：Gravity Scan / Gravity Shift / SCAN / Shift R / Shift C / ソースコード / 動詞解析 / want to / have to / Why × 才能 × 偏愛（旧3要素）

## クライアント情報

- 名前：{client_name}
- 役割：{data.get('client_role', '（未記入）')}
- 入力データ：{data.get('input_data', 'セッション対話ログ（40 分）')}

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

以下の 5 セクション構成で Markdown を出力してください。断定的・構造的な文体で。
曖昧な表現（「〜かもしれません」「〜と思われます」）は避けてください。
すべての記述は、セッション記録中の固有のエピソード・発言を根拠として紐づけ、
この経営者本人にしか当てはまらない固有の記述にしてください。

---

# {client_name} ── あなたに人が集まる理由レポート

## 01. あなたに人が集まる理由

**1 文の魅力源を冒頭に置く（最重要）**：
「あなたに人が集まる理由は、〇〇である」を 1 文で言語化。
強み・想い・偏愛の 3 要素が交差した一点を「人を引き寄せる磁場」として記述。

魅力の証拠：対話記録から、その魅力が実際に発火した瞬間・場面を 2-3 件引用。
「あなたに集まった人が繰り返し言うこと／場面で起きていたこと」の形で記述。

末尾に短く 1 行で「この魅力が発火しない場の存在」を予告（詳細は 04 で展開）。

## 02. あなたの引力 3 要素

3 要素は別々に立つのではなく、互いに引き合って初めて引力になることを明示。

### 強み（Talent）
- **動詞マップ**：自然にできてしまう動きを動詞 3 つで連鎖表現（例：A する → B する → C する）。各動詞に対話記録の根拠を 1 行で添える
- **発揮される場**：強みが最大化する場（関係・場・時間）
- **停止する場**：強みが発火しない場

### 想い（Why）
- 何をするときに自分が燃えるか。富や評価を取り除いても残る本音の動機を 2-3 文で記述
- 対話記録から、その想いが現れた発言・エピソードを根拠として添える

### 偏愛（Passion）
- **譲れない好み**：絶対にやりたいこと・選びたい場面を 2-3 個
- **絶対に選ばない嫌い**：絶対に避けたい場面・条件を 2-3 個
- 経営判断の根底にある好き嫌いの軸として記述

## 03. 3 要素の整合度 → 4 型判定

統合マップ：
- 強み = （整合 / ズレ）
- 想い = （整合 / ズレ）
- 偏愛 = （整合 / ズレ）

判定：【個人整合型 / 個人想いズレ型 / 個人強みズレ型 / 個人偏愛ズレ型】のいずれか 1 つを断定。
判定理由を 2-3 文で。

## 04. 最大リスク

放置すると引力が漏れる場・条件を、対話記録の固有エピソードと紐づけて記述。
- 引力が漏れる具体的な場（セッション内で言及された場面）
- そのまま続けた場合の 5 年後の劣化シナリオ
- 直近の意思決定への影響（あれば）

## 05. 次の一手

4 型判定に応じた RECOMMENDED を 1 つ提示（固定マッピング遵守）：
- 個人整合型 → **無料 Web 診断** → Gravity（組織の引力設計プログラム）
- 個人想いズレ型 / 個人強みズレ型 / 個人偏愛ズレ型 → **Gravity Coaching**（月 1 × 90 分 × 6 ヶ月）

RECOMMENDED の根拠：型判定に基づき、なぜそのサービスが次の一手なのかを 2-3 文で記述。
40 分では辿り着けなかった領域に触れること。

**最後の問い**：このレポートを読み終えた経営者に残す 1 つの問い。
「もし〇〇という環境が手に入るとしたら、あなたは何を恐れるか？」型で。

---

CTA URL：
- Gravity Coaching → https://growthfix.jp/gravity/coaching/
- 無料 Web 診断 → https://growthfix.jp/gravity/diagnose/
- Gravity（組織軸） → https://growthfix.jp/gravity/
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
