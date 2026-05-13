"""
Gravity Scan レポート自動生成スクリプト

ヒアリング入力シート（Markdown）を読み込み、
Claude APIで分析 → レポートテンプレートに流し込んで下書きを生成する。

使い方:
  python3 gravity_scan_report.py <ヒアリング入力シート.md>

出力:
  同じディレクトリに「<会社名>_停滞構造レポート.md」を生成
"""

import os
import re
import sys
import json
from datetime import datetime

# ============================================================
# 設定
# ============================================================
TEMPLATE_PATH = os.path.expanduser(
    "~/Documents/Obsidian Vault/05_プロダクト/Gravity/Scan/レポート/テンプレート_停滞構造レポート.md"
)
REPORT_OUTPUT_DIR = os.path.expanduser(
    "~/Documents/Obsidian Vault/05_プロダクト/Gravity/Scan/レポート"
)


# ============================================================
# ヒアリングシート解析
# ============================================================
def parse_hearing_sheet(filepath):
    """ヒアリング入力シートを解析して構造化データにする"""
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

    # 各セクションのテキストを抽出
    sections = {
        "pre_org_chart": "組織図・チーム構成",
        "pre_schedule": "経営者の1週間のスケジュール",
        "pre_turnover": "直近1年の入退社情報",
        "pre_other": "その他受領データ",
        "q_main_concern": "現状の一番の困りごと",
        "q1": "この人を採って良かった",
        "q2": "ミスマッチだった",
        "q3": "採用の最終判断",
        "q4": "今一番採用したい",
        "memo_hiring": "採用領域の構造的所感",
        "q5": "評価はどうやって決めて",
        "q6": "給与・報酬はどう決めて",
        "q7": "不満の声",
        "q8": "もっと評価されるべき",
        "memo_evaluation": "評価・報酬領域の構造的所感",
        "q9": "にしかできない判断",
        "q10": "任せたいけど任せられて",
        "q11": "任せた結果",
        "q12": "リーダー層に一番求めて",
        "memo_management": "マネジメント・権限移譲の構造的所感",
        "q13": "意思決定はどういうフロー",
        "q14": "うちの会社らしさ",
        "q15": "ここが詰まっている",
        "q16": "半年後、組織がどうなって",
        "memo_culture": "組織設計・カルチャーの構造的所感",
        "q_closing": "気づいていなかったこと",
    }

    for key, search_text in sections.items():
        pattern = re.escape(search_text) + r".*?```\n(.*?)```"
        match = re.search(pattern, content, re.DOTALL)
        if match:
            data[key] = match.group(1).strip()
        else:
            data[key] = ""

    # 総合分析メモ
    analysis_sections = {
        "analysis_core": "停滞の核（一言で）",
        "analysis_surface_structure": "4領域の表面 vs 構造",
        "analysis_causal_loop": "因果ループの仮説",
        "analysis_issues": "構造的課題（優先順位順）",
        "analysis_roadmap": "Gravityで取り組む場合の6ヶ月ロードマップ案",
    }

    for key, search_text in analysis_sections.items():
        pattern = re.escape(search_text) + r".*?```\n(.*?)```"
        match = re.search(pattern, content, re.DOTALL)
        if match:
            data[key] = match.group(1).strip()
        else:
            data[key] = ""

    return data


# ============================================================
# Claude API連携（レポート分析生成）
# ============================================================
def generate_analysis_with_claude(hearing_data):
    """Claude APIを使ってヒアリングデータからレポート分析を生成"""
    try:
        import anthropic
    except ImportError:
        print("⚠️ anthropic パッケージが未インストールです。")
        print("   pip3 install anthropic")
        print("   テンプレートベースの生成にフォールバックします。")
        return None

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        config_path = os.path.join(os.path.dirname(__file__), "config_anthropic.json")
        if os.path.exists(config_path):
            with open(config_path) as f:
                api_key = json.load(f).get("api_key", "")

    if not api_key:
        print("⚠️ ANTHROPIC_API_KEY が未設定です。")
        print("   テンプレートベースの生成にフォールバックします。")
        return None

    client = anthropic.Anthropic(api_key=api_key)

    # ヒアリングデータを整形
    hearing_text = format_hearing_for_prompt(hearing_data)

    prompt = f"""あなたは組織コンサルタント「石井伸幸」のアシスタントです。
以下のヒアリングデータを分析し、Gravity Scan停滞構造レポートの各セクションを生成してください。

# ヒアリングデータ

{hearing_text}

# 出力形式

以下のJSON形式で出力してください。すべての値は日本語の文字列です。

```json
{{
  "core_issue_statement": "御社の停滞の核を1-2文で定義（「御社の停滞の核は〜」で始める）",
  "executive_summary": "全体像を3-5文で記述",
  "severity_hiring": "1-5の数値",
  "severity_evaluation": "1-5の数値",
  "severity_management": "1-5の数値",
  "severity_culture": "1-5の数値",
  "one_line_hiring": "採用領域の一言所見",
  "one_line_evaluation": "評価領域の一言所見",
  "one_line_management": "マネジメント領域の一言所見",
  "one_line_culture": "組織設計領域の一言所見",
  "surface_hiring": "採用の表面の症状",
  "structure_hiring": "採用の構造的原因",
  "surface_evaluation": "評価の表面の症状",
  "structure_evaluation": "評価の構造的原因",
  "surface_management": "マネジメントの表面の症状",
  "structure_management": "マネジメントの構造的原因",
  "surface_culture": "組織設計の表面の症状",
  "structure_culture": "組織設計の構造的原因",
  "causal_loop_diagram": "テキストベースの因果ループ図（矢印と改行で表現）",
  "causal_loop_explanation": "ループの読み方を2-3文で",
  "causal_loop_implication": "このループが意味することを2-3文で",
  "issues": [
    {{
      "title": "課題タイトル",
      "surface": "表面の症状",
      "structure": "構造的原因",
      "impact": "影響範囲",
      "severity": "★の数（例：★★★★☆）",
      "analysis": "3-5文の詳細分析"
    }}
  ],
  "priority_rationale": "なぜこの順番かを3-5文で説明",
  "action_self_driven": "自走する場合のアクション（箇条書き3-5個）",
  "gravity_roadmap": [
    {{"month": "1ヶ月目", "theme": "テーマ", "output": "アウトプット"}},
    {{"month": "2ヶ月目", "theme": "テーマ", "output": "アウトプット"}},
    {{"month": "3ヶ月目", "theme": "テーマ", "output": "アウトプット"}},
    {{"month": "4ヶ月目", "theme": "テーマ", "output": "アウトプット"}},
    {{"month": "5ヶ月目", "theme": "テーマ", "output": "アウトプット"}},
    {{"month": "6ヶ月目", "theme": "テーマ", "output": "アウトプット"}}
  ]
}}
```

# 分析のガイドライン

- 「表面の症状」は経営者が自覚している問題（ヒアリング回答から抽出）
- 「構造的原因」は経営者が気づいていない根本原因（石井の分析視点で）
- 因果ループ図は、4領域の課題が相互に強化し合うループを描く
- 課題は3-5個、優先順位は構造的依存関係に基づいて決定
- 「こう直せ」ではなく「何が起きているか」の可視化に徹する
- 石井のメモ（所感）があれば、その分析視点を最大限活用する
"""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        response_text = response.content[0].text

        # JSONを抽出
        json_match = re.search(r"```json\n(.*?)```", response_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(1))
        else:
            # JSON部分だけの場合
            return json.loads(response_text)
    except Exception as e:
        print(f"⚠️ Claude API エラー: {e}")
        return None


def format_hearing_for_prompt(data):
    """ヒアリングデータをプロンプト用テキストに整形"""
    lines = []
    lines.append(f"会社名: {data.get('company_name', '不明')}")
    lines.append(f"代表者: {data.get('ceo_name', '不明')}")
    lines.append(f"従業員数: {data.get('employee_count', '不明')}名")
    lines.append(f"業種: {data.get('industry', '不明')}")
    lines.append("")

    lines.append("## 事前データの所感")
    lines.append(f"組織図: {data.get('pre_org_chart', '(なし)')}")
    lines.append(f"スケジュール: {data.get('pre_schedule', '(なし)')}")
    lines.append(f"入退社: {data.get('pre_turnover', '(なし)')}")
    lines.append(f"その他: {data.get('pre_other', '(なし)')}")
    lines.append("")

    lines.append("## ヒアリング回答")
    lines.append(f"一番の困りごと: {data.get('q_main_concern', '')}")
    lines.append("")

    lines.append("### 採用")
    lines.append(f"Q1（良い採用）: {data.get('q1', '')}")
    lines.append(f"Q2（ミスマッチ）: {data.get('q2', '')}")
    lines.append(f"Q3（判断構造）: {data.get('q3', '')}")
    lines.append(f"Q4（採用ニーズ）: {data.get('q4', '')}")
    lines.append(f"石井メモ: {data.get('memo_hiring', '')}")
    lines.append("")

    lines.append("### 評価・報酬")
    lines.append(f"Q5（評価方法）: {data.get('q5', '')}")
    lines.append(f"Q6（報酬決定）: {data.get('q6', '')}")
    lines.append(f"Q7（不満）: {data.get('q7', '')}")
    lines.append(f"Q8（過小評価）: {data.get('q8', '')}")
    lines.append(f"石井メモ: {data.get('memo_evaluation', '')}")
    lines.append("")

    lines.append("### マネジメント・権限移譲")
    lines.append(f"Q9（CEO専権）: {data.get('q9', '')}")
    lines.append(f"Q10（委譲障壁）: {data.get('q10', '')}")
    lines.append(f"Q11（委譲失敗）: {data.get('q11', '')}")
    lines.append(f"Q12（リーダー期待）: {data.get('q12', '')}")
    lines.append(f"石井メモ: {data.get('memo_management', '')}")
    lines.append("")

    lines.append("### 組織設計・カルチャー")
    lines.append(f"Q13（意思決定フロー）: {data.get('q13', '')}")
    lines.append(f"Q14（会社らしさ）: {data.get('q14', '')}")
    lines.append(f"Q15（詰まり）: {data.get('q15', '')}")
    lines.append(f"Q16（理想像）: {data.get('q16', '')}")
    lines.append(f"石井メモ: {data.get('memo_culture', '')}")
    lines.append("")

    lines.append(f"### 締め")
    lines.append(f"気づき: {data.get('q_closing', '')}")
    lines.append("")

    lines.append("## 石井の総合分析メモ")
    lines.append(f"停滞の核: {data.get('analysis_core', '')}")
    lines.append(f"表面vs構造: {data.get('analysis_surface_structure', '')}")
    lines.append(f"因果ループ仮説: {data.get('analysis_causal_loop', '')}")
    lines.append(f"課題リスト: {data.get('analysis_issues', '')}")
    lines.append(f"ロードマップ案: {data.get('analysis_roadmap', '')}")

    return "\n".join(lines)


# ============================================================
# テンプレートベース生成（Claude API未使用時のフォールバック）
# ============================================================
def generate_from_manual_analysis(hearing_data):
    """石井の総合分析メモからテンプレートに直接流し込む"""
    result = {}

    # 基本情報
    result["company_name"] = hearing_data.get("company_name", "（会社名）")
    result["ceo_name"] = hearing_data.get("ceo_name", "（代表者名）")
    result["employee_count"] = hearing_data.get("employee_count", "（人数）")
    result["industry"] = hearing_data.get("industry", "（業種）")
    result["scan_date"] = hearing_data.get("scan_date", "（診断日）")
    result["report_date"] = datetime.now().strftime("%Y-%m-%d")
    result["hearing_duration"] = hearing_data.get("hearing_duration", "90")

    # 石井メモからの転記
    result["core_issue_statement"] = hearing_data.get("analysis_core", "（分析メモを記入してください）")

    # 表面 vs 構造
    surface_structure = hearing_data.get("analysis_surface_structure", "")
    lines = surface_structure.split("\n")
    for line in lines:
        if "採用" in line and "→" in line:
            parts = line.split("→")
            if len(parts) >= 2:
                result["surface_hiring"] = parts[0].replace("採用：表面", "").strip()
                result["structure_hiring"] = parts[-1].strip()
        elif "評価" in line and "→" in line:
            parts = line.split("→")
            if len(parts) >= 2:
                result["surface_evaluation"] = parts[0].replace("評価：表面", "").strip()
                result["structure_evaluation"] = parts[-1].strip()
        elif "権限" in line and "→" in line:
            parts = line.split("→")
            if len(parts) >= 2:
                result["surface_management"] = parts[0].replace("権限：表面", "").strip()
                result["structure_management"] = parts[-1].strip()
        elif "組織" in line and "→" in line:
            parts = line.split("→")
            if len(parts) >= 2:
                result["surface_culture"] = parts[0].replace("組織：表面", "").strip()
                result["structure_culture"] = parts[-1].strip()

    # 因果ループ
    result["causal_loop_diagram"] = hearing_data.get("analysis_causal_loop", "（因果ループ図を記入）")

    # 課題リスト
    result["analysis_issues"] = hearing_data.get("analysis_issues", "")

    # ロードマップ
    result["analysis_roadmap"] = hearing_data.get("analysis_roadmap", "")

    return result


# ============================================================
# レポート生成
# ============================================================
def build_report(template, analysis, hearing_data):
    """テンプレートにデータを流し込んでレポートを生成"""
    report = template

    # 基本情報
    report = report.replace("{{company_name}}", hearing_data.get("company_name", ""))
    report = report.replace("{{ceo_name}}", hearing_data.get("ceo_name", ""))
    report = report.replace("{{employee_count}}", hearing_data.get("employee_count", ""))
    report = report.replace("{{industry}}", hearing_data.get("industry", ""))
    report = report.replace("{{scan_date}}", hearing_data.get("scan_date", ""))
    report = report.replace("{{report_date}}", datetime.now().strftime("%Y-%m-%d"))
    report = report.replace("{{hearing_duration}}", hearing_data.get("hearing_duration", "90"))

    if analysis:
        # Claude API分析結果を流し込み
        simple_fields = [
            "core_issue_statement", "executive_summary",
            "severity_hiring", "severity_evaluation", "severity_management", "severity_culture",
            "one_line_hiring", "one_line_evaluation", "one_line_management", "one_line_culture",
            "surface_hiring", "structure_hiring",
            "surface_evaluation", "structure_evaluation",
            "surface_management", "structure_management",
            "surface_culture", "structure_culture",
            "causal_loop_diagram", "causal_loop_explanation", "causal_loop_implication",
            "priority_rationale", "action_self_driven",
        ]
        for field in simple_fields:
            report = report.replace("{{" + field + "}}", str(analysis.get(field, "")))

        # 課題セクション
        issues = analysis.get("issues", [])
        for i, issue in enumerate(issues[:3], 1):
            report = report.replace(f"{{{{issue_{i}_title}}}}", issue.get("title", ""))
            report = report.replace(f"{{{{issue_{i}_surface}}}}", issue.get("surface", ""))
            report = report.replace(f"{{{{issue_{i}_structure}}}}", issue.get("structure", ""))
            report = report.replace(f"{{{{issue_{i}_impact}}}}", issue.get("impact", ""))
            report = report.replace(f"{{{{issue_{i}_severity}}}}", issue.get("severity", ""))
            report = report.replace(f"{{{{issue_{i}_analysis}}}}", issue.get("analysis", ""))

        # 追加課題（4個目以降）
        additional = ""
        for i, issue in enumerate(issues[3:], 4):
            additional += f"\n### 課題{i}：{issue.get('title', '')}\n\n"
            additional += f"| 項目 | 内容 |\n|---|---|\n"
            additional += f"| 表面の症状 | {issue.get('surface', '')} |\n"
            additional += f"| 構造的原因 | {issue.get('structure', '')} |\n"
            additional += f"| 影響範囲 | {issue.get('impact', '')} |\n"
            additional += f"| 深刻度 | {issue.get('severity', '')} |\n\n"
            additional += f"**詳細分析：**\n\n{issue.get('analysis', '')}\n\n---\n"
        report = report.replace("{{additional_issues}}", additional)

        # 優先順位
        for i, issue in enumerate(issues[:3], 1):
            report = report.replace(f"{{{{priority_{i}_title}}}}", issue.get("title", ""))
            reason = f"課題{i}の構造的原因がこの課題の前提になっているため"
            report = report.replace(f"{{{{priority_{i}_reason}}}}", reason)

        # Gravityロードマップ
        roadmap = analysis.get("gravity_roadmap", [])
        for i, item in enumerate(roadmap[:6], 1):
            report = report.replace(f"{{{{gravity_m{i}_theme}}}}", item.get("theme", ""))
            report = report.replace(f"{{{{gravity_m{i}_output}}}}", item.get("output", ""))

    # 未置換のプレースホルダーを「（要記入）」に変換
    report = re.sub(r"\{\{[^}]+\}\}", "（要記入）", report)

    return report


# ============================================================
# メイン
# ============================================================
def main():
    if len(sys.argv) < 2:
        print("使い方: python3 gravity_scan_report.py <ヒアリング入力シート.md>")
        print()
        print("例: python3 gravity_scan_report.py ~/Documents/Obsidian\\ Vault/05_プロダクト/Gravity/Scan/レポート/サンプル_hearing.md")
        sys.exit(1)

    input_path = sys.argv[1]
    if not os.path.exists(input_path):
        print(f"❌ ファイルが見つかりません: {input_path}")
        sys.exit(1)

    print("📋 Gravity Scan レポート生成")
    print(f"   入力: {os.path.basename(input_path)}")
    print()

    # STEP 1: ヒアリングシート解析
    print("🔍 ヒアリングシート解析中...")
    hearing_data = parse_hearing_sheet(input_path)
    company = hearing_data.get("company_name", "Unknown")
    print(f"   ✅ {company}（{hearing_data.get('employee_count', '?')}名・{hearing_data.get('industry', '?')}）")
    print()

    # STEP 2: 分析生成
    print("🧠 分析生成中...")
    analysis = generate_analysis_with_claude(hearing_data)

    if analysis:
        print("   ✅ Claude APIで分析完了")
    else:
        print("   📝 テンプレートベースで生成（石井メモから転記）")
        analysis = generate_from_manual_analysis(hearing_data)
    print()

    # STEP 3: レポート生成
    print("📄 レポート生成中...")
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        template = f.read()

    report = build_report(template, analysis, hearing_data)

    # 出力
    today = datetime.now().strftime("%y%m%d")
    safe_company = re.sub(r'[\\/:*?"<>|]', '_', company)
    output_filename = f"{today}_{safe_company}_停滞構造レポート.md"
    output_path = os.path.join(REPORT_OUTPUT_DIR, output_filename)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"   ✅ 生成完了: {output_filename}")
    print(f"   📁 {output_path}")
    print()
    print("💡 「（要記入）」の箇所を手動で補完してください。")


if __name__ == "__main__":
    main()
