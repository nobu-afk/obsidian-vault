"""
Orbit 月次引力施策レポート 自動生成エンジン v3（OT-3・v1.0・260514）

Orbit v3.0「マンスリー施策レポート装置」の A4 5-7 枚 PDF + Markdown を自動生成。
OT-1（orbit_data_fetcher.py）と OT-2（orbit_paper_matcher.py）の出力を統合。

v3.0 との差分（既存 orbit_monthly_report.py = A4 3p 版）:
  - 章構成を A4 5-7 枚に拡張（p.4 論文×データ突合・p.5 推奨施策・p.6 心理的契約）
  - OT-2 出力（_matched.json）を p.4/p.5 に反映
  - Wevox / カオナビ等の既存タレマネデータ取得元情報を p.1 サマリーに表示
  - p.6 Page 6 心理的契約再校正（Rousseau-Hansen-Tomprou 2018 準拠）
  - p.7 軸 15 個ゲート進捗（既存 orbit_monthly_report.py の実装を流用）

使い方:
  python3 orbit_monthly_report_v3.py --client sample_orbit_client --month 2026-05
  python3 orbit_monthly_report_v3.py --client sample_orbit_client --month 2026-05 --pdf
  python3 orbit_monthly_report_v3.py --demo
  python3 orbit_monthly_report_v3.py --demo --pdf

入力:
  orbit_data/<CLIENT_ID>_<YYYY-MM>.json（OT-1 出力 or 既存 orbit_data）
  orbit_data/<CLIENT_ID>_<YYYY-MM>_matched.json（OT-2 出力・省略可）

出力:
  - stdout: Markdown 形式レポート（p.1-7）
  - orbit_reports/<CLIENT_ID>_<YYYY-MM>_v3.png: 引力8項目グループ棒グラフ
  - orbit_reports/<CLIENT_ID>_<YYYY-MM>_v3.pdf: A4 5-7p PDF（--pdf 時・要 reportlab）
"""

import os
import sys
import json
import argparse
from datetime import datetime
from enum import IntEnum

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _common.claude_client import JST, now_jst_str  # noqa: E402

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR   = os.path.join(SCRIPT_DIR, "orbit_data")
REPORT_DIR = os.path.join(SCRIPT_DIR, "orbit_reports")


def _load_matplotlib():
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches
        import matplotlib.font_manager as fm
        return plt, mpatches, fm
    except ImportError:
        return None


def _load_reportlab():
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.units import mm
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
        )
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        return {
            "A4": A4, "colors": colors, "mm": mm,
            "SimpleDocTemplate": SimpleDocTemplate,
            "Paragraph": Paragraph, "Spacer": Spacer,
            "Table": Table, "TableStyle": TableStyle,
            "Image": Image, "PageBreak": PageBreak,
            "getSampleStyleSheet": getSampleStyleSheet,
            "ParagraphStyle": ParagraphStyle,
            "pdfmetrics": pdfmetrics, "TTFont": TTFont,
        }
    except ImportError:
        return None


class Score(IntEnum):
    EXCELLENT        = 4
    GOOD             = 3
    NEEDS_ATTENTION  = 2
    CRITICAL         = 1

    @property
    def symbol(self) -> str:
        return {4: "◎", 3: "○", 2: "△", 1: "×"}[self.value]

    @property
    def label(self) -> str:
        return {4: "良好", 3: "概ね良好", 2: "要改善", 1: "要緊急対応"}[self.value]

    @classmethod
    def from_symbol_safe(cls, sym: str):
        mapping = {"◎": cls.EXCELLENT, "○": cls.GOOD, "△": cls.NEEDS_ATTENTION, "×": cls.CRITICAL}
        return mapping.get(sym)


GRAVITY_ITEMS = [
    {"key": "recruitment_pipeline",  "label": "①採用パイプライン",           "axis": "集まる"},
    {"key": "final_decline_rate",    "label": "②最終面接辞退率",             "axis": "集まる"},
    {"key": "recruitment_wall_pof",  "label": "⑦採用最大壁+PO Fit",         "axis": "集まる"},
    {"key": "talent_retention",      "label": "③優秀人材定着率",             "axis": "躍動"},
    {"key": "executive_voice",       "label": "④幹部発話量",                 "axis": "躍動"},
    {"key": "engagement",            "label": "⑤エンゲージメント",           "axis": "躍動"},
    {"key": "departure_signal",      "label": "⑥離脱予兆",                   "axis": "躍動"},
    {"key": "psych_safety_cost",     "label": "⑧心理的安全性+採用コスト",   "axis": "躍動"},
]

DEPARTURE_ITEMS = [
    {"key": "physical",      "label": "身体シグナル",    "desc": "遅刻・欠勤・体調不良の頻度変化"},
    {"key": "facial",        "label": "表情シグナル",    "desc": "会議・1on1 での表情・発話量変化"},
    {"key": "overload",      "label": "過負荷シグナル",  "desc": "残業・週末対応・タスク滞留"},
    {"key": "meaning",       "label": "意味付けシグナル","desc": "仕事への意義言語化・質問の変化"},
    {"key": "relationships", "label": "人間関係シグナル","desc": "チーム間コミュニケーション密度変化"},
]

AXES_15 = [
    {"key": "scout_reply_rate",         "label": "スカウト返信率",            "axis": "集まる"},
    {"key": "final_decline_rate",       "label": "最終面接辞退率",            "axis": "集まる"},
    {"key": "recruit_unit_cost",        "label": "採用単価",                  "axis": "集まる"},
    {"key": "early_attrition_rate",     "label": "入社後早期離脱率",          "axis": "集まる"},
    {"key": "referral_rate",            "label": "リファラル率",              "axis": "集まる"},
    {"key": "individual_sales_15x",     "label": "個人売上 1.5 倍",           "axis": "躍動"},
    {"key": "ai_armed_score",           "label": "AI 武装スコア",             "axis": "躍動"},
    {"key": "task_5kpi",                "label": "業務遂行 5 KPI",            "axis": "躍動"},
    {"key": "one_on_one_rate",          "label": "1on1 実施率",               "axis": "躍動"},
    {"key": "individual_gravity_score", "label": "個人引力スコア",            "axis": "躍動"},
    {"key": "talent_retention_rate",    "label": "優秀人材離職率",            "axis": "留まる"},
    {"key": "engagement_score",         "label": "エンゲージメントスコア",    "axis": "留まる"},
    {"key": "drumbeat_retention",       "label": "ドラムビート定着率",        "axis": "留まる"},
    {"key": "career_path_clarity",      "label": "キャリアパス言語化率",      "axis": "留まる"},
    {"key": "succession_pool",          "label": "後継者プール冗長度",        "axis": "留まる"},
]

COLOR_CURRENT  = "#2563EB"
COLOR_PREVIOUS = "#93C5FD"
COLOR_AXIS_R   = "#DBEAFE"
COLOR_AXIS_C   = "#EDE9FE"
COLOR_AXIS_O   = "#D1FAE5"
PRIORITY_LABEL = {"high": "高", "medium": "中", "low": "低"}


def sym_to_score(sym: str):
    return Score.from_symbol_safe(sym)


def load_json(client_id: str, month: str) -> dict:
    filepath = os.path.join(DATA_DIR, f"{client_id}_{month}.json")
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError as e:
        raise FileNotFoundError(
            f"データファイルが見つかりません: {filepath}\n"
            f"  orbit_data/ 配下に {client_id}_{month}.json を配置してください。"
        ) from e


def load_matched_json(client_id: str, month: str) -> dict:
    filepath = os.path.join(DATA_DIR, f"{client_id}_{month}_matched.json")
    if not os.path.exists(filepath):
        return {}
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def build_page1_summary(data: dict, matched: dict) -> str:
    gs       = data["gravity_scores"]
    current  = gs.get("current", {})
    previous = gs.get("previous", {})
    month    = data.get("month", "")
    client_id = data.get("client_id", "")
    source   = data.get("source", "手動入力")
    now_jst  = datetime.now(JST).strftime("%Y-%m-%d %H:%M JST")

    cur_scores  = [sym_to_score(current.get(it["key"],  "?")) for it in GRAVITY_ITEMS]
    prev_scores = [sym_to_score(previous.get(it["key"], "-")) for it in GRAVITY_ITEMS]
    valid_cur   = [int(s) for s in cur_scores  if s is not None]
    valid_prev  = [int(s) for s in prev_scores if s is not None]
    avg_cur  = sum(valid_cur)  / len(valid_cur)  if valid_cur  else 0
    avg_prev = sum(valid_prev) / len(valid_prev) if valid_prev else 0
    diff_avg = avg_cur - avg_prev if avg_prev > 0 else 0
    diff_str = f"+{diff_avg:.2f}" if diff_avg > 0 else (f"{diff_avg:.2f}" if diff_avg < 0 else "±0")

    weak_items = [it["label"] for it in GRAVITY_ITEMS
                  if current.get(it["key"], "?") in ("△", "×")]
    improved   = [it["label"] for it in GRAVITY_ITEMS
                  if sym_to_score(current.get(it["key"], "?")) is not None
                  and sym_to_score(previous.get(it["key"], "?")) is not None
                  and int(sym_to_score(current.get(it["key"]))) > int(sym_to_score(previous.get(it["key"])))]

    papers_count = matched.get("papers_matched", 0)
    actions_count = len(matched.get("signals", []))

    lines = []
    lines.append("# Gravity Orbit 月次引力施策レポート v3")
    lines.append("")
    lines.append(f"**クライアント:** {client_id}  ")
    lines.append(f"**対象月:** {month}  ")
    lines.append(f"**データソース:** {source}  ")
    lines.append(f"**生成日時:** {now_jst}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## p.1 サマリー（前月比 + 主要 KPI）")
    lines.append("")
    lines.append("| 指標 | 今月 | 先月 | 変化 |")
    lines.append("|---|:-:|:-:|:-:|")
    prev_avg_str = f"{avg_prev:.2f}" if avg_prev > 0 else "初月"
    lines.append(f"| 引力平均スコア（8 項目・1-4 スケール）| **{avg_cur:.2f}** | {prev_avg_str} | {diff_str} |")
    lines.append(f"| 要改善 / 要緊急対応 項目数 | **{len(weak_items)} 件** | - | - |")
    lines.append(f"| 今月改善した項目数 | **{len(improved)} 件** | - | - |")
    lines.append(f"| 突合論文数（OT-2）| **{papers_count} 本** | - | - |")
    lines.append(f"| 生成施策シナリオ数 | **{actions_count} 件** | - | - |")
    lines.append("")

    if weak_items:
        lines.append(f"**要対応項目:** {' / '.join(weak_items)}")
        lines.append("")
    if improved:
        lines.append(f"**改善項目:** {' / '.join(improved)}")
        lines.append("")

    lines.append("> スコア基準: ◎=4（良好）/ ○=3（概ね良好）/ △=2（要改善）/ ×=1（要緊急対応）")
    lines.append("")

    return "\n".join(lines)


def build_page2_scores(data: dict) -> str:
    gs       = data["gravity_scores"]
    current  = gs.get("current", {})
    previous = gs.get("previous", {})
    month    = data.get("month", "")

    lines = []
    lines.append("---")
    lines.append("")
    lines.append("## p.2 引力 8 項目スコア表 + グループ棒グラフ")
    lines.append("")
    lines.append(f"**対象月:** {month}")
    lines.append("")

    for axis_name in ["集まる", "躍動"]:
        items_in_axis = [it for it in GRAVITY_ITEMS if it["axis"] == axis_name]
        axis_code = "R" if axis_name == "集まる" else "C"
        lines.append(f"### [{axis_code}] {axis_name}軸")
        lines.append("")
        lines.append(f"| 項目 | 今月 ({month}) | 先月 | 変化 |")
        lines.append("|---|:-:|:-:|:-:|")

        for item in items_in_axis:
            k        = item["key"]
            cur_sym  = current.get(k, "?")
            prev_sym = previous.get(k, "-")
            cur_sc   = sym_to_score(cur_sym)
            prev_sc  = sym_to_score(prev_sym)

            if prev_sc is None:
                delta_str = "（初月）"
            else:
                diff = int(cur_sc) - int(prev_sc) if cur_sc is not None else 0
                delta_str = f"▲ +{diff}" if diff > 0 else (f"▼ {diff}" if diff < 0 else "→ 変化なし")

            label_txt = cur_sc.label if cur_sc is not None else ""
            lines.append(f"| {item['label']} | **{cur_sym}** {label_txt} | {prev_sym} | {delta_str} |")

        lines.append("")

    lines.append("> グラフは orbit_reports/<CLIENT_ID>_<YYYY-MM>_v3.png に保存されます。")
    lines.append("")

    return "\n".join(lines)


def build_page3_departure(data: dict) -> str:
    signals = data.get("departure_signals", {})
    month   = data.get("month", "")

    lines = []
    lines.append("---")
    lines.append("")
    lines.append("## p.3 離職予兆 5 シグナル")
    lines.append("")
    lines.append(f"**対象月:** {month}")
    lines.append("")

    if not signals:
        lines.append("> 離職予兆データがありません（departure_signals が空）")
        lines.append("")
        return "\n".join(lines)

    lines.append("| シグナル | 観察ポイント | スコア | 評価 |")
    lines.append("|---|---|:-:|---|")

    alert_count = 0
    for item in DEPARTURE_ITEMS:
        k   = item["key"]
        sym = signals.get(k, "?")
        sc  = sym_to_score(sym)
        eval_txt = sc.label if sc is not None else "?"
        if sc is not None and sc <= Score.NEEDS_ATTENTION:
            alert_count += 1
        lines.append(f"| **{item['label']}** | {item['desc']} | {sym} | {eval_txt} |")

    lines.append("")

    if alert_count == 0:
        alert_level   = "GREEN（警戒なし）"
        alert_comment = "全シグナル良好。現状維持と月次モニタリングを継続。"
    elif alert_count <= 2:
        alert_level   = "YELLOW（要注意）"
        alert_comment = f"{alert_count} 項目が要改善水準。次回セッションで重点ヒアリングを実施。"
    else:
        alert_level   = "RED（要緊急対応）"
        alert_comment = (
            f"{alert_count} 項目が要改善水準。"
            "緊急 1on1 の設定と対象者の個別フォロープランを立案。"
        )

    lines.append(f"### 総合警戒レベル: {alert_level}")
    lines.append("")
    lines.append(alert_comment)
    lines.append("")

    return "\n".join(lines)


def build_page4_paper_match(matched: dict) -> str:
    signals      = matched.get("signals", [])
    matched_papers = matched.get("matched_papers", [])
    month        = matched.get("month", "")

    lines = []
    lines.append("---")
    lines.append("")
    lines.append("## p.4 論文 × データ突合（OT-2 出力反映）")
    lines.append("")
    if month:
        lines.append(f"**突合基準月:** {month}")
        lines.append("")

    if not matched_papers:
        lines.append("> OT-2（orbit_paper_matcher.py）の出力ファイルが見つかりません。")
        lines.append("> `python3 orbit_paper_matcher.py --client <CLIENT_ID> --month <YYYY-MM>` を先に実行してください。")
        lines.append("")
        return "\n".join(lines)

    lines.append(f"突合論文数: **{len(matched_papers)} 本**（引力スコア弱点との重複あり）")
    lines.append("")
    lines.append("| 論文 | 著者 | 被引用数 | 関連軸 | マッチシグナル |")
    lines.append("|---|---|:-:|---|---|")
    for p in matched_papers[:8]:
        axes_str    = " / ".join(p.get("axes", []))
        signals_str = " / ".join(p.get("matched_signals", []))
        lines.append(
            f"| {p.get('paper_id', '')} | {p.get('author', '')} ({p.get('year', '')}) | "
            f"{p.get('citations', 0):,} | {axes_str} | {signals_str} |"
        )
    lines.append("")

    if signals:
        lines.append("### 施策シナリオ概要（詳細は p.5）")
        lines.append("")
        for sig in signals:
            papers_cited = " / ".join(sig.get("papers", []))
            lines.append(f"- **{sig.get('type', '')}** → 根拠: {papers_cited}")
        lines.append("")

    return "\n".join(lines)


def build_page5_actions(matched: dict) -> str:
    signals = matched.get("signals", [])

    lines = []
    lines.append("---")
    lines.append("")
    lines.append("## p.5 推奨施策 5 件（優先度付き）")
    lines.append("")

    if not signals:
        lines.append("> 施策データがありません。OT-2 を実行して施策を生成してください。")
        lines.append("")
        return "\n".join(lines)

    priority_order = {"high": 0, "medium": 1, "low": 2}
    sorted_signals = sorted(signals, key=lambda x: priority_order.get(x.get("priority", "low"), 2))
    shown = sorted_signals[:5]

    lines.append("| # | シナリオ | 優先度 | 根拠論文 |")
    lines.append("|:-:|---|:-:|---|")
    for i, sig in enumerate(shown, 1):
        pri  = sig.get("priority", "low")
        plbl = PRIORITY_LABEL.get(pri, pri)
        papers_cited = " / ".join(sig.get("papers", []))
        lines.append(f"| {i} | {sig.get('type', '')} | {plbl} | {papers_cited} |")

    lines.append("")

    for i, sig in enumerate(shown, 1):
        pri  = sig.get("priority", "low")
        plbl = PRIORITY_LABEL.get(pri, pri)
        lines.append(f"### [{i}] {sig.get('type', '')}（優先度: {plbl}）")
        lines.append("")
        for act in sig.get("actions", []):
            lines.append(f"- {act}")
        rationale = sig.get("rationale", "")
        if rationale:
            lines.append("")
            lines.append(f"> **論文根拠:** {rationale}")
        lines.append("")

    return "\n".join(lines)


def build_page6_psych_contract(data: dict) -> str:
    month     = data.get("month", "")
    client_id = data.get("client_id", "")

    lines = []
    lines.append("---")
    lines.append("")
    lines.append("## p.6 Page 6 心理的契約再校正（VRBs 3 次元測定）")
    lines.append("")
    lines.append(f"**対象月:** {month}  ")
    lines.append(f"**参照理論:** Rousseau-Hansen-Tomprou 2018（累積被引用 31,000+）")
    lines.append("")
    lines.append("### 心理的契約 3 次元（Rousseau 1989 × Tomprou 2015 統合）")
    lines.append("")
    lines.append("| 次元 | 指標 | 当月観察 | 状態 |")
    lines.append("|---|---|---|:-:|")
    lines.append("| **関係的契約**（長期信頼・キャリア支援） | 1on1 での「将来の約束」言語化頻度 | （セッション記録） | - |")
    lines.append("| **取引的契約**（報酬・役割の明確化） | JD・評価基準の透明度チェック | （セッション記録） | - |")
    lines.append("| **バランス型契約**（柔軟性・相互調整） | ライフイベント対応・WFH 対応件数 | （セッション記録） | - |")
    lines.append("")
    lines.append("### VRBs（Violation → Recovery → Breach）進捗")
    lines.append("")
    lines.append("| フェーズ | 状態 | 推奨アクション |")
    lines.append("|---|:-:|---|")
    lines.append("| **Violation（違反認識）** | 確認中 | 「期待 vs 実際」ギャップを 1on1 で直接確認 |")
    lines.append("| **Recovery（修復交渉）** | 確認中 | 違反後 72h 以内の対話設定 → 修復合意 |")
    lines.append("| **Breach（破綻回避）** | 確認中 | Phase 2-4 装置（継続維持 / 個別再交渉 / 破綻修復）の稼働確認 |")
    lines.append("")
    lines.append("> **Phase 12-14 学術根拠（累積被引用 31,000+）:**")
    lines.append("> Mitchell JE (2001, 3,200+) / Rousseau (1989, 4,100+) / Meyer-Allen (1991, 8,900+)")
    lines.append("> Crossley (2007, 1,800+) / Tomprou (2015, 420+) / Rousseau-Hansen-Tomprou (2018)")
    lines.append("")
    lines.append("### 月次セッション（経営者・CHRO 対象 60 分）アジェンダ")
    lines.append("")
    lines.append("| 時間 | 内容 |")
    lines.append("|---|---|")
    lines.append("| 0-10 分 | 当月レポート概観（サマリー・KPI 前月比） |")
    lines.append("| 10-25 分 | 要注意シグナルの詳細ヒアリング（離職予兆・心理的契約） |")
    lines.append("| 25-45 分 | 推奨施策 3-5 件の合意（来月の打ち手を確定） |")
    lines.append("| 45-60 分 | 軸 15 個ゲート進捗確認 + 次月データ取得方法確認 |")
    lines.append("")

    return "\n".join(lines)


def build_page7_axes15(data: dict) -> str:
    axes_data = data.get("axes_15", {})
    month     = data.get("month", "")

    if not axes_data:
        lines = []
        lines.append("---")
        lines.append("")
        lines.append("## p.7 軸 15 個ゲート進捗（5 年継続装置）")
        lines.append("")
        lines.append(f"**対象月:** {month}")
        lines.append("")
        lines.append("> axes_15 データがありません（JSON に `axes_15` フィールドを追加してください）。")
        lines.append("")
        lines.append("### 軸 15 個ゲート構造（集まる 5 / 躍動 5 / 留まる 5）")
        lines.append("")
        lines.append("| # | 軸名 | 軸 | 現状値 | クリア |")
        lines.append("|:-:|---|:-:|---|:-:|")
        for i, item in enumerate(AXES_15, 1):
            lines.append(f"| {i} | {item['label']} | {item['axis']} | - | 未クリア |")
        lines.append("")
        lines.append("> 3 ヶ月で 1 軸クリア = ファイブスター演出（R10 詳細設計で実装予定）")
        lines.append("")
        return "\n".join(lines)

    lines = []
    lines.append("---")
    lines.append("")
    lines.append("## p.7 軸 15 個ゲート進捗（5 年継続装置・260513 R4）")
    lines.append("")
    lines.append(f"**対象月:** {month}")
    lines.append("")

    for axis_name in ["集まる", "躍動", "留まる"]:
        axis_items = [a for a in AXES_15 if a["axis"] == axis_name]
        cleared_count = sum(
            1 for a in axis_items
            if axes_data.get(a["key"], {}).get("cleared", False)
        )

        lines.append(f"### {axis_name}軸（{cleared_count} / 5 クリア）")
        lines.append("")
        lines.append("| # | 軸名 | 現状値 | クリア判定 | コメント |")
        lines.append("|:-:|---|---|:-:|---|")

        for i, item in enumerate(axis_items, 1):
            key     = item["key"]
            entry   = axes_data.get(key, {})
            value   = entry.get("value", "-")
            cleared = entry.get("cleared", False)
            comment = entry.get("comment", "")
            mark    = "★ クリア" if cleared else "未クリア"
            lines.append(f"| {i} | **{item['label']}** | {value} | {mark} | {comment} |")

        lines.append("")

    total_cleared = sum(
        1 for a in AXES_15
        if axes_data.get(a["key"], {}).get("cleared", False)
    )
    lines.append(f"### 全 15 軸 累計クリア数: {total_cleared} / 15")
    lines.append("")

    if total_cleared == 0:
        progress = "立ち上げ期（軸クリア前・基準値固定中）"
    elif total_cleared <= 5:
        progress = "初期定着期（1-5 軸クリア）"
    elif total_cleared <= 10:
        progress = "中期成熟期（6-10 軸クリア）"
    elif total_cleared < 15:
        progress = "後期完成期（11-14 軸クリア・全クリアまで残りわずか）"
    else:
        progress = "★★★★★ 全軸クリア達成（5 年継続装置の到達点）"

    lines.append(f"**進捗段階:** {progress}")
    lines.append("")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*本レポートは Gravity Orbit 月次引力施策レポート v3（A4 5-7p）の自動生成物です。*")
    lines.append("")

    return "\n".join(lines)


def build_chart_v3(data: dict, output_path: str) -> bool:
    loaded = _load_matplotlib()
    if loaded is None:
        print("[INFO] matplotlib が見つかりません。PNG 出力をスキップします。", file=sys.stderr)
        return False
    plt, mpatches, fm = loaded

    gs       = data["gravity_scores"]
    current  = gs.get("current", {})
    previous = gs.get("previous", {})
    month    = data.get("month", "")

    labels     = [it["label"] for it in GRAVITY_ITEMS]
    axis_types = [it["axis"]  for it in GRAVITY_ITEMS]
    cur_vals   = [int(sym_to_score(current.get(it["key"],  "×")) or Score.CRITICAL) for it in GRAVITY_ITEMS]
    prev_vals  = [int(sym_to_score(previous.get(it["key"], "×")) or Score.CRITICAL) for it in GRAVITY_ITEMS]

    n     = len(labels)
    x     = list(range(n))
    bar_w = 0.35

    jp_fonts = ["Hiragino Sans", "Hiragino Kaku Gothic Pro", "Yu Gothic", "MS Gothic", "DejaVu Sans"]
    available = {f.name for f in fm.fontManager.ttflist}
    chosen_font = next((f for f in jp_fonts if f in available), None)
    if chosen_font:
        plt.rcParams["font.family"] = chosen_font
    plt.rcParams["axes.unicode_minus"] = False

    fig, ax = plt.subplots(figsize=(12, 6))
    fig.patch.set_facecolor("#FAFAFA")
    ax.set_facecolor("#FAFAFA")

    for i, axis in enumerate(axis_types):
        color = COLOR_AXIS_R if axis == "集まる" else COLOR_AXIS_C
        ax.axvspan(i - 0.5, i + 0.5, color=color, alpha=0.25, zorder=0)

    bars_cur  = ax.bar([xi - bar_w / 2 for xi in x], cur_vals,  bar_w,
                       label=f"今月 ({month})", color=COLOR_CURRENT,  zorder=3)
    bars_prev = ax.bar([xi + bar_w / 2 for xi in x], prev_vals, bar_w,
                       label="先月",            color=COLOR_PREVIOUS, zorder=3)

    for bar, num in zip(bars_cur, cur_vals):
        sym = Score(num).symbol if num in (1, 2, 3, 4) else "?"
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05,
                sym, ha="center", va="bottom", fontsize=11, fontweight="bold", color=COLOR_CURRENT)
    for bar, num in zip(bars_prev, prev_vals):
        sym = Score(num).symbol if num in (1, 2, 3, 4) else "?"
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05,
                sym, ha="center", va="bottom", fontsize=10, color="#4B5563")

    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=20, ha="right", fontsize=9)
    ax.set_yticks([1, 2, 3, 4])
    ax.set_yticklabels(
        [f"{s.symbol}({s.value})" for s in [Score.CRITICAL, Score.NEEDS_ATTENTION, Score.GOOD, Score.EXCELLENT]],
        fontsize=10
    )
    ax.set_ylim(0, 5)
    ax.set_ylabel("スコア", fontsize=11)
    ax.set_title(f"引力 8 項目スコア — {month} [Orbit v3 Report]", fontsize=14, fontweight="bold", pad=12)

    legend_items = [
        mpatches.Patch(color=COLOR_CURRENT,  label=f"今月 ({month})"),
        mpatches.Patch(color=COLOR_PREVIOUS, label="先月"),
        mpatches.Patch(color=COLOR_AXIS_R,   alpha=0.5, label="集まる軸"),
        mpatches.Patch(color=COLOR_AXIS_C,   alpha=0.5, label="躍動軸"),
    ]
    ax.legend(handles=legend_items, loc="upper right", fontsize=9)
    ax.grid(axis="y", linestyle="--", alpha=0.5, zorder=1)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return True


def _register_jp_font(rl: dict):
    pdfmetrics = rl["pdfmetrics"]
    TTFont     = rl["TTFont"]
    candidates = [
        "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/Library/Fonts/Arial Unicode MS.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont("JpFont", path))
                return "JpFont"
            except Exception:
                continue
    return None


def build_pdf_v3(
    client_id: str,
    month: str,
    markdown_text: str,
    chart_path: str,
    output_path: str,
) -> bool:
    rl = _load_reportlab()
    if rl is None:
        print("[INFO] reportlab not installed, skipping PDF. pip install reportlab", file=sys.stderr)
        return False

    A4                = rl["A4"]
    colors            = rl["colors"]
    mm                = rl["mm"]
    SimpleDocTemplate = rl["SimpleDocTemplate"]
    Paragraph         = rl["Paragraph"]
    Spacer            = rl["Spacer"]
    PageBreak         = rl["PageBreak"]
    getSampleStyleSheet = rl["getSampleStyleSheet"]
    ParagraphStyle    = rl["ParagraphStyle"]
    Image             = rl["Image"]

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=18 * mm, rightMargin=18 * mm,
        topMargin=18 * mm, bottomMargin=18 * mm,
        title=f"Gravity Orbit 月次引力施策レポート v3 — {month}",
        author="GrowthFix",
    )

    styles  = getSampleStyleSheet()
    jp_font = _register_jp_font(rl)
    base_fn = jp_font if jp_font else "Helvetica"

    style_title = ParagraphStyle(
        "OTitle", parent=styles["Title"],
        fontName=base_fn, fontSize=16, spaceAfter=6,
        textColor=colors.HexColor("#1E3A5F"),
    )
    style_h2 = ParagraphStyle(
        "OH2", parent=styles["Heading2"],
        fontName=base_fn, fontSize=12, spaceBefore=10, spaceAfter=4,
        textColor=colors.HexColor("#2563EB"),
    )
    style_h3 = ParagraphStyle(
        "OH3", parent=styles["Heading3"],
        fontName=base_fn, fontSize=10, spaceBefore=6, spaceAfter=3,
        textColor=colors.HexColor("#1D4ED8"),
    )
    style_body = ParagraphStyle(
        "OBody", parent=styles["Normal"],
        fontName=base_fn, fontSize=9, leading=14, spaceAfter=3,
    )
    style_small = ParagraphStyle(
        "OSmall", parent=styles["Normal"],
        fontName=base_fn, fontSize=8, textColor=colors.grey,
    )

    def _add_section(story, markdown_text, start_marker, end_marker=None):
        in_section = False
        for line in markdown_text.splitlines():
            if start_marker in line:
                in_section = True
                continue
            if end_marker and end_marker in line and in_section:
                break
            if in_section and line.strip():
                if line.startswith("###"):
                    story.append(Paragraph(line.lstrip("#").strip(), style_h3))
                elif line.startswith("##"):
                    story.append(Paragraph(line.lstrip("#").strip(), style_h2))
                elif line.startswith("|") and not line.startswith("|---|"):
                    cells = [c.strip() for c in line.split("|")[1:-1]]
                    story.append(Paragraph(" | ".join(cells), style_body))
                elif line.startswith("|---"):
                    pass
                elif line.startswith("---"):
                    pass
                else:
                    clean = line.lstrip("#>*- ").strip()
                    if clean:
                        story.append(Paragraph(clean, style_body))

    now_jst = datetime.now(JST).strftime("%Y-%m-%d %H:%M JST")
    story = []

    story.append(Paragraph("Gravity Orbit 月次引力施策レポート v3", style_title))
    story.append(Paragraph(f"クライアント: {client_id} | 対象月: {month} | 生成: {now_jst}", style_small))
    story.append(Spacer(1, 4 * mm))

    _add_section(story, markdown_text, "## p.1 サマリー", "## p.2")

    story.append(PageBreak())

    story.append(Paragraph("p.2 引力 8 項目スコア表 + グループ棒グラフ", style_h2))
    story.append(Spacer(1, 3 * mm))
    if chart_path and os.path.exists(chart_path):
        try:
            img = Image(chart_path, width=165 * mm, height=82 * mm)
            story.append(img)
            story.append(Spacer(1, 3 * mm))
        except Exception as e:
            story.append(Paragraph(f"[グラフ埋め込みエラー: {e}]", style_small))
    _add_section(story, markdown_text, "## p.2 引力", "## p.3")

    story.append(PageBreak())

    story.append(Paragraph("p.3 離職予兆 5 シグナル", style_h2))
    story.append(Spacer(1, 3 * mm))
    _add_section(story, markdown_text, "## p.3 離職予兆", "## p.4")

    story.append(PageBreak())

    story.append(Paragraph("p.4 論文 × データ突合", style_h2))
    story.append(Spacer(1, 3 * mm))
    _add_section(story, markdown_text, "## p.4 論文", "## p.5")

    story.append(PageBreak())

    story.append(Paragraph("p.5 推奨施策（優先度付き）", style_h2))
    story.append(Spacer(1, 3 * mm))
    _add_section(story, markdown_text, "## p.5 推奨施策", "## p.6")

    story.append(PageBreak())

    story.append(Paragraph("p.6 心理的契約再校正（VRBs 3 次元測定）", style_h2))
    story.append(Spacer(1, 3 * mm))
    _add_section(story, markdown_text, "## p.6 Page 6", "## p.7")

    story.append(PageBreak())

    story.append(Paragraph("p.7 軸 15 個ゲート進捗（5 年継続装置）", style_h2))
    story.append(Spacer(1, 3 * mm))
    _add_section(story, markdown_text, "## p.7 軸 15 個ゲート", None)

    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph(
        "本レポートは Gravity Orbit 月次引力施策レポート v3（A4 5-7p）の自動生成物です。",
        style_small
    ))

    try:
        doc.build(story)
        return True
    except Exception as e:
        print(f"[ERROR] PDF 生成に失敗しました: {e}", file=sys.stderr)
        return False


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Orbit 月次引力施策レポート 自動生成エンジン v3（OT-3）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python3 orbit_monthly_report_v3.py --client sample_orbit_client --month 2026-05
  python3 orbit_monthly_report_v3.py --client sample_orbit_client --month 2026-05 --pdf
  python3 orbit_monthly_report_v3.py --demo
  python3 orbit_monthly_report_v3.py --demo --pdf

入力:
  orbit_data/<CLIENT_ID>_<YYYY-MM>.json       (OT-1 出力)
  orbit_data/<CLIENT_ID>_<YYYY-MM>_matched.json (OT-2 出力・省略可)

出力:
  - stdout: Markdown 形式レポート（p.1-7）
  - orbit_reports/<CLIENT_ID>_<YYYY-MM>_v3.png
  - orbit_reports/<CLIENT_ID>_<YYYY-MM>_v3.pdf （--pdf 時）
        """,
    )
    parser.add_argument("--client",   default="sample_orbit_client", help="クライアントID")
    parser.add_argument("--month",    help="対象月 YYYY-MM（例: 2026-05）")
    parser.add_argument("--no-chart", action="store_true", help="PNG グラフ出力をスキップ")
    parser.add_argument("--pdf",      action="store_true", help="PDF 出力（要 reportlab）")
    parser.add_argument("--demo",     action="store_true",
                        help="sample_orbit_client / 2026-05 でデモ実行")
    args = parser.parse_args()

    if args.demo:
        args.client = "sample_orbit_client"
        args.month  = "2026-05"

    if not args.month:
        print("[ERROR] --month を指定してください（例: --month 2026-05）", file=sys.stderr)
        sys.exit(1)

    try:
        datetime.strptime(args.month, "%Y-%m")
    except ValueError:
        print(f"[ERROR] --month の形式が不正です: '{args.month}'（正しい形式: YYYY-MM）", file=sys.stderr)
        sys.exit(1)

    client_id = args.client
    month     = args.month

    print(f"[INFO] データ読み込み: {client_id} / {month}", file=sys.stderr)
    try:
        data = load_json(client_id, month)
    except FileNotFoundError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)

    matched = load_matched_json(client_id, month)
    if matched:
        print(f"[INFO] OT-2 突合データ読み込み完了（施策シナリオ: {len(matched.get('signals', []))} 件）",
              file=sys.stderr)
    else:
        print("[INFO] OT-2 突合データなし → p.4/p.5 はスケルトン表示", file=sys.stderr)

    report_parts = [
        build_page1_summary(data, matched),
        build_page2_scores(data),
        build_page3_departure(data),
        build_page4_paper_match(matched),
        build_page5_actions(matched),
        build_page6_psych_contract(data),
        build_page7_axes15(data),
    ]
    full_report = "\n".join(p for p in report_parts if p)
    print(full_report)

    os.makedirs(REPORT_DIR, exist_ok=True)

    chart_path = None
    if not args.no_chart:
        chart_path = os.path.join(REPORT_DIR, f"{client_id}_{month}_v3.png")
        print(f"[INFO] PNG 生成: {chart_path}", file=sys.stderr)
        try:
            if build_chart_v3(data, chart_path):
                size_kb = os.path.getsize(chart_path) // 1024 or 1
                print(f"[OK]  PNG 出力完了: {chart_path} ({size_kb} KB)", file=sys.stderr)
            else:
                chart_path = None
        except (ValueError, OSError, RuntimeError) as e:
            print(f"[WARN] PNG 生成エラー: {e}", file=sys.stderr)
            chart_path = None
    else:
        print("[INFO] --no-chart 指定につき PNG 出力をスキップ", file=sys.stderr)

    if args.pdf:
        pdf_path = os.path.join(REPORT_DIR, f"{client_id}_{month}_v3.pdf")
        print(f"[INFO] PDF 生成: {pdf_path}", file=sys.stderr)
        try:
            if build_pdf_v3(client_id, month, full_report, chart_path or "", pdf_path):
                size_kb = os.path.getsize(pdf_path) // 1024 or 1
                print(f"[OK]  PDF 出力完了: {pdf_path} ({size_kb} KB)", file=sys.stderr)
        except (ValueError, OSError, RuntimeError) as e:
            print(f"[WARN] PDF 生成エラー: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
