"""
Orbit 月次引力レポート 自動生成スクリプト（Phase 1）

Orbit v3.0 単一プラン（月15万）の3点セット納品物のうち
「② 月次引力レポート A4 3p」を自動生成するスクリプト。

使い方:
  python3 orbit_monthly_report.py --client <CLIENT_ID> --month YYYY-MM [オプション]

例:
  python3 orbit_monthly_report.py --client sample_orbit_client --month 2026-05
  python3 orbit_monthly_report.py --client sample_orbit_client --month 2026-05 --trend
  python3 orbit_monthly_report.py --client sample_orbit_client --month 2026-05 --pdf

入力:
  06_開発/scripts/orbit_data/<CLIENT_ID>_<YYYY-MM>.json（当月・前月の2ファイルを読み込む）
  06_開発/scripts/orbit_data/orbit_actions_map.json（α/β/γ/δ自動マッピングルール）

出力:
  - stdout: Markdown形式レポート（p.1 スコア表 / p.2 改善提案 / p.3 離職予兆）
  - orbit_reports/<CLIENT_ID>_<YYYY-MM>.png: 引力8項目グループ棒グラフ（--no-chart で抑制）
  - orbit_reports/<CLIENT_ID>_<YYYY-MM>_trend.png: 過去6ヶ月時系列グラフ（--trend で生成）
  - orbit_reports/<CLIENT_ID>_<YYYY-MM>.pdf: A4 3p PDF（--pdf で生成、要 reportlab）

Phase 1 拡張:
  - Score IntEnum 化（M-1 解消）
  - α/β/γ/δ 自動マッピング（orbit_actions_map.json）
  - 過去6ヶ月時系列グラフ（--trend）
  - PDF 出力（--pdf、reportlab オプション依存）

引力8項目 SSOT: 05_プロダクト/_共通/SSOT_用語と定義.md §13.1（v0.4・7→8項目化済）

NOTE: matplotlibがない場合、PNGはスキップしてテキストレポートのみ出力する。
      pip install matplotlib でインストール可能。
      reportlabがない場合、PDFはスキップする（pip install reportlab）。
"""

import os
import sys
import json
import glob
import argparse
from datetime import datetime, timezone, timedelta
from enum import IntEnum


def _load_matplotlib():
    """matplotlib を遅延ロード（PNG 生成時のみ ~300ms の起動コストを払う）"""
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
    """reportlab を遅延ロード（PDF 生成時のみ）"""
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


# ============================================================
# 定数・マッピング
# ============================================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR   = os.path.join(SCRIPT_DIR, "orbit_data")
REPORT_DIR = os.path.join(SCRIPT_DIR, "orbit_reports")
ACTIONS_MAP_PATH = os.path.join(DATA_DIR, "orbit_actions_map.json")

JST = timezone(timedelta(hours=9))

MAX_AUTO_ACTIONS = 5  # 自動マッピングで出力するアクション最大件数


# ============================================================
# Score IntEnum（拡張 1: M-1 解消）
# ============================================================

class Score(IntEnum):
    """引力スコア 4 段階。記号 ◎/○/△/× の単一定義点。"""
    EXCELLENT        = 4  # ◎
    GOOD             = 3  # ○
    NEEDS_ATTENTION  = 2  # △
    CRITICAL         = 1  # ×

    @property
    def symbol(self) -> str:
        return {4: "◎", 3: "○", 2: "△", 1: "×"}[self.value]

    @property
    def label(self) -> str:
        return {4: "良好", 3: "概ね良好", 2: "要改善", 1: "要緊急対応"}[self.value]

    @classmethod
    def from_symbol(cls, sym: str) -> "Score":
        """◎/○/△/× → Score。不明な場合は ValueError を送出。"""
        mapping = {"◎": cls.EXCELLENT, "○": cls.GOOD, "△": cls.NEEDS_ATTENTION, "×": cls.CRITICAL}
        if sym not in mapping:
            raise ValueError(f"不正なスコア記号: '{sym}'。◎/○/△/× のいずれかを指定してください。")
        return mapping[sym]

    @classmethod
    def from_symbol_safe(cls, sym: str) -> "Score | None":
        """◎/○/△/× → Score。不明な場合は None。"""
        try:
            return cls.from_symbol(sym)
        except ValueError:
            return None


# 引力8項目の表示設定（SSOT §13.1 準拠）
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

# 離職予兆5シグナル（SSOT 商品.md 準拠）
DEPARTURE_ITEMS = [
    {"key": "physical",      "label": "身体シグナル",    "desc": "遅刻・欠勤・体調不良の頻度変化"},
    {"key": "facial",        "label": "表情シグナル",    "desc": "会議・1on1 での表情・発話量変化"},
    {"key": "overload",      "label": "過負荷シグナル",  "desc": "残業・週末対応・タスク滞留"},
    {"key": "meaning",       "label": "意味付けシグナル","desc": "仕事への意義言語化・質問の変化"},
    {"key": "relationships", "label": "人間関係シグナル","desc": "チーム間コミュニケーション密度変化"},
]

PRIORITY_LABEL = {"high": "高", "medium": "中", "low": "低"}

# カラー設定（グラフ用）
COLOR_CURRENT  = "#2563EB"
COLOR_PREVIOUS = "#93C5FD"
COLOR_AXIS_R   = "#DBEAFE"
COLOR_AXIS_C   = "#EDE9FE"

# 時系列グラフ用カラーパレット（8項目分）
TREND_COLORS = [
    "#2563EB", "#7C3AED", "#059669", "#D97706",
    "#DC2626", "#0891B2", "#BE185D", "#65A30D",
]


# ============================================================
# データ読み込み
# ============================================================

def load_json(client_id: str, month: str) -> dict:
    """orbit_data/<CLIENT_ID>_<YYYY-MM>.json を読み込む"""
    filename = f"{client_id}_{month}.json"
    filepath = os.path.join(DATA_DIR, filename)
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError as e:
        raise FileNotFoundError(
            f"データファイルが見つかりません: {filepath}\n"
            f"  orbit_data/ 配下に {filename} を配置してください。\n"
            f"  スキーマ: orbit_data/SCHEMA.md"
        ) from e


def load_actions_map() -> dict:
    """orbit_actions_map.json を読み込む。失敗時は空の rules を返す。"""
    try:
        with open(ACTIONS_MAP_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"[WARN] orbit_actions_map.json の読み込みに失敗しました: {e}", file=sys.stderr)
        return {"rules": []}


def load_all_months(client_id: str) -> list[dict]:
    """orbit_data/<CLIENT_ID>_*.json を全期間分 glob で取得して時系列順に返す"""
    pattern = os.path.join(DATA_DIR, f"{client_id}_????-??.json")
    paths = sorted(glob.glob(pattern))
    results = []
    for p in paths:
        try:
            with open(p, "r", encoding="utf-8") as f:
                results.append(json.load(f))
        except (json.JSONDecodeError, OSError) as e:
            print(f"[WARN] ファイル読み込みをスキップ: {p} ({e})", file=sys.stderr)
    return results


def validate_data(data: dict) -> None:
    """必須フィールドの存在チェック"""
    required_top = ["client_id", "month", "gravity_scores"]
    for key in required_top:
        if key not in data:
            raise ValueError(f"必須フィールド '{key}' がJSONに存在しません")

    gs = data["gravity_scores"]
    if "current" not in gs:
        raise ValueError("gravity_scores.current が存在しません")

    for item in GRAVITY_ITEMS:
        k = item["key"]
        if k not in gs["current"]:
            raise ValueError(f"gravity_scores.current.{k} が存在しません")
        val = gs["current"][k]
        if Score.from_symbol_safe(val) is None:
            raise ValueError(
                f"gravity_scores.current.{k} の値 '{val}' が不正です。"
                f"◎/○/△/× のいずれかを指定してください"
            )

    if "departure_signals" in data:
        for item in DEPARTURE_ITEMS:
            k = item["key"]
            if k not in data["departure_signals"]:
                raise ValueError(f"departure_signals.{k} が存在しません")


def sym_to_score(sym: str) -> Score | None:
    """◎/○/△/× → Score。不正値・未入力は None。"""
    return Score.from_symbol_safe(sym)


# ============================================================
# 拡張 2: α/β/γ/δ 自動マッピング
# ============================================================

def _rule_matches(rule: dict, current_scores: dict) -> bool:
    """ルールの trigger 条件と当月スコアを照合する（trigger 内キーが全て AND 条件）"""
    trigger = rule.get("trigger", {})
    for key, allowed_syms in trigger.items():
        sym = current_scores.get(key)
        if sym is None or sym not in allowed_syms:
            return False
    return True


def auto_map_actions(current_scores: dict, rules: list, max_items: int = MAX_AUTO_ACTIONS) -> list[dict]:
    """
    スコアパターンとルールを照合し、適合したアクションを priority 順で返す。
    max_items 件に制限。
    """
    matched = []
    for rule in rules:
        if _rule_matches(rule, current_scores):
            matched.append({
                "id":       rule.get("id", ""),
                "axis":     rule.get("axis", "-"),
                "priority": rule.get("priority", "low"),
                "action":   rule.get("action", ""),
            })

    # priority 順ソート（high → medium → low）
    priority_order = {"high": 0, "medium": 1, "low": 2}
    matched.sort(key=lambda x: priority_order.get(x["priority"], 2))
    return matched[:max_items]


def resolve_actions(data: dict, rules: list) -> tuple[list[dict], str]:
    """
    改善アクションを解決する。
    - JSON に alpha_beta_gamma_delta_actions があれば優先（手動入力）
    - なければ auto_map_actions で自動生成
    戻り値: (actions_list, source_label)
    """
    manual = data.get("alpha_beta_gamma_delta_actions", [])
    if manual:
        return manual, "manual"
    current = data.get("gravity_scores", {}).get("current", {})
    auto = auto_map_actions(current, rules)
    return auto, "auto"


# ============================================================
# レポート生成: p.1 スコア表（Markdown）
# ============================================================

def build_page1(data: dict) -> str:
    """p.1: 引力8項目スコア表（今月 / 先月比）"""
    gs = data["gravity_scores"]
    current  = gs.get("current", {})
    previous = gs.get("previous", {})

    month      = data.get("month", "")
    client_id  = data.get("client_id", "")
    now_jst    = datetime.now(JST).strftime("%Y-%m-%d %H:%M JST")

    lines = []
    lines.append("# Gravity Orbit 月次引力レポート")
    lines.append("")
    lines.append(f"**クライアント:** {client_id}  ")
    lines.append(f"**対象月:** {month}  ")
    lines.append(f"**生成日時:** {now_jst}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## p.1 引力 8 項目スコア（今月 vs 先月）")
    lines.append("")

    for axis_name in ["集まる", "躍動"]:
        items_in_axis = [it for it in GRAVITY_ITEMS if it["axis"] == axis_name]
        axis_emoji = "R" if axis_name == "集まる" else "C"
        lines.append(f"### [{axis_emoji}] {axis_name}軸")
        lines.append("")
        lines.append(f"| 項目 | 今月 ({month}) | 先月 | 変化 |")
        lines.append("|---|:-:|:-:|:-:|")

        for item in items_in_axis:
            k         = item["key"]
            cur_sym   = current.get(k, "?")
            prev_sym  = previous.get(k, "-")
            cur_sc    = sym_to_score(cur_sym)
            prev_sc   = sym_to_score(prev_sym)

            if prev_sc is None:
                delta_str = "（初月）"
            else:
                diff = int(cur_sc) - int(prev_sc) if cur_sc is not None else 0
                if diff > 0:
                    delta_str = f"▲ +{diff}"
                elif diff < 0:
                    delta_str = f"▼ {diff}"
                else:
                    delta_str = "→ 変化なし"

            label_txt = cur_sc.label if cur_sc is not None else ""
            lines.append(f"| {item['label']} | **{cur_sym}** {label_txt} | {prev_sym} | {delta_str} |")

        lines.append("")

    # 総合サマリー
    cur_scores  = [sym_to_score(current.get(it["key"],  "?")) for it in GRAVITY_ITEMS]
    prev_scores = [sym_to_score(previous.get(it["key"], "-")) for it in GRAVITY_ITEMS]
    valid_cur   = [int(s) for s in cur_scores  if s is not None]
    valid_prev  = [int(s) for s in prev_scores if s is not None]

    avg_cur  = sum(valid_cur)  / len(valid_cur)  if valid_cur  else 0
    avg_prev = sum(valid_prev) / len(valid_prev) if valid_prev else 0

    lines.append("### 総合引力スコア")
    lines.append("")
    lines.append("| | 今月 | 先月 | 差分 |")
    lines.append("|---|:-:|:-:|:-:|")
    prev_avg_str = f"{avg_prev:.2f}" if avg_prev > 0 else "-"
    diff_avg     = avg_cur - avg_prev if avg_prev > 0 else 0
    diff_avg_str = (
        f"+{diff_avg:.2f}" if diff_avg > 0 else
        (f"{diff_avg:.2f}" if diff_avg < 0 else "±0")
    )
    lines.append(f"| 平均スコア（1-4） | **{avg_cur:.2f}** | {prev_avg_str} | {diff_avg_str} |")
    lines.append("")
    lines.append(
        "> スコア基準: "
        f"{Score.EXCELLENT.symbol}=4（{Score.EXCELLENT.label}）/ "
        f"{Score.GOOD.symbol}=3（{Score.GOOD.label}）/ "
        f"{Score.NEEDS_ATTENTION.symbol}=2（{Score.NEEDS_ATTENTION.label}）/ "
        f"{Score.CRITICAL.symbol}=1（{Score.CRITICAL.label}）"
    )
    lines.append("")

    return "\n".join(lines)


# ============================================================
# レポート生成: p.2 改善提案（Markdown）
# ============================================================

def build_page2(data: dict, rules: list) -> str:
    """p.2: α/β/γ/δ マッピング由来の改善提案"""
    actions, source = resolve_actions(data, rules)
    month = data.get("month", "")

    lines = []
    lines.append("---")
    lines.append("")
    lines.append("## p.2 改善提案（α/β/γ/δ マッピング）")
    lines.append("")
    lines.append(f"**対象月:** {month}")

    if source == "auto":
        lines.append("")
        lines.append("> **[自動生成]** スコアパターンから orbit_actions_map.json を参照して提案を自動生成しました。")
        lines.append("> 手動で alpha_beta_gamma_delta_actions を JSON に記載することで上書き可能です。")
    lines.append("")

    if not actions:
        lines.append("> 改善提案データがありません（スコアパターンに一致するルールがありませんでした）")
        lines.append("")
        return "\n".join(lines)

    # 優先度順にソート（high → medium → low）
    priority_order = {"high": 0, "medium": 1, "low": 2}
    sorted_actions = sorted(actions, key=lambda x: priority_order.get(x.get("priority", "low"), 2))

    lines.append("| # | 軸 | 優先度 | 改善提案 |")
    lines.append("|:-:|:-:|:-:|---|")
    for i, act in enumerate(sorted_actions, 1):
        axis      = act.get("axis", "-")
        action    = act.get("action", "")
        priority  = act.get("priority", "low")
        pri_label = PRIORITY_LABEL.get(priority, priority)
        pri_icon  = "高" if priority == "high" else ("中" if priority == "medium" else "低")
        lines.append(f"| {i} | `{axis}` | {pri_icon}（{pri_label}） | {action} |")

    lines.append("")
    lines.append("")
    lines.append("### 軸凡例")
    lines.append("")
    lines.append("| 軸コード | 意味 |")
    lines.append("|---|---|")
    lines.append("| R-α | 集まる軸 × 最優先介入（採用設計・メッセージ）|")
    lines.append("| R-β | 集まる軸 × 中期施策（プロセス改善）|")
    lines.append("| R-γ | 集まる軸 × 補強施策（データ整備・計測）|")
    lines.append("| R-δ | 集まる軸 × 維持施策（習慣化・モニタリング）|")
    lines.append("| C-α | 躍動軸 × 最優先介入（エンゲージメント・1on1）|")
    lines.append("| C-β | 躍動軸 × 中期施策（文化・対話設計）|")
    lines.append("| C-γ | 躍動軸 × 補強施策（サーベイ・KPI 整備）|")
    lines.append("| C-δ | 躍動軸 × 維持施策（習慣化・モニタリング）|")
    lines.append("")

    return "\n".join(lines)


# ============================================================
# レポート生成: p.3 離職予兆 5 シグナル（Markdown）
# ============================================================

def build_page3(data: dict) -> str:
    """p.3: 離職予兆 5 シグナル早期警戒スコア"""
    signals = data.get("departure_signals", {})
    month   = data.get("month", "")

    lines = []
    lines.append("---")
    lines.append("")
    lines.append("## p.3 離職予兆 5 シグナル 早期警戒スコア")
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
            f"緊急 1on1 の設定と対象者の個別フォロープランを立案。"
        )

    lines.append(f"### 総合警戒レベル: {alert_level}")
    lines.append("")
    lines.append(alert_comment)
    lines.append("")
    lines.append("")
    lines.append("### 心理的安全性 4 行動チェック（Edmondson 1999 準拠）")
    lines.append("")
    lines.append("月次セッションで以下 4 行動の観察・記録を実施：")
    lines.append("")
    lines.append("| # | 行動 | 今月の観察 |")
    lines.append("|:-:|---|---|")
    lines.append("| 1 | 失敗を認める発言 | （セッション記録に記入）|")
    lines.append("| 2 | 異議申し立て | （セッション記録に記入）|")
    lines.append("| 3 | 無知の表明 | （セッション記録に記入）|")
    lines.append("| 4 | 助けを求める | （セッション記録に記入）|")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*本レポートは Gravity Orbit 月次引力レポート（A4 3p）の自動生成物です。*  ")
    lines.append(
        "*四半期 4 型再判定書は別途 `orbit_quarterly_review.py` で生成します。*"
    )
    lines.append("")

    return "\n".join(lines)


# ============================================================
# グラフ生成: 棒グラフ（今月 vs 先月）
# ============================================================

def build_chart(data: dict, output_path: str) -> bool:
    """引力8項目グループ棒グラフ（今月 vs 先月）を PNG に保存。成功時 True を返す。"""
    loaded = _load_matplotlib()
    if loaded is None:
        print("[INFO] matplotlib が見つかりません。PNG 出力をスキップします。", file=sys.stderr)
        print("[INFO] インストール: pip install matplotlib", file=sys.stderr)
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
                sym, ha="center", va="bottom", fontsize=11, fontweight="bold",
                color=COLOR_CURRENT)
    for bar, num in zip(bars_prev, prev_vals):
        sym = Score(num).symbol if num in (1, 2, 3, 4) else "?"
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05,
                sym, ha="center", va="bottom", fontsize=10,
                color="#4B5563")

    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=20, ha="right", fontsize=9)
    ax.set_yticks([1, 2, 3, 4])
    ax.set_yticklabels(
        [f"{s.symbol}({s.value})" for s in [Score.CRITICAL, Score.NEEDS_ATTENTION, Score.GOOD, Score.EXCELLENT]],
        fontsize=10
    )
    ax.set_ylim(0, 5)
    ax.set_ylabel("スコア", fontsize=11)
    ax.set_title(f"引力 8 項目スコア — {month}", fontsize=14, fontweight="bold", pad=12)

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


# ============================================================
# 拡張 3: 過去 6 ヶ月時系列グラフ
# ============================================================

def build_trend_chart(client_id: str, target_month: str, output_path: str) -> bool:
    """
    過去 6 ヶ月（または利用可能な全期間）の引力 8 項目を時系列折れ線グラフで出力する。
    出力: orbit_reports/<CLIENT_ID>_<YYYY-MM>_trend.png
    """
    loaded = _load_matplotlib()
    if loaded is None:
        print("[INFO] matplotlib が見つかりません。trend PNG 出力をスキップします。", file=sys.stderr)
        return False
    plt, mpatches, fm = loaded

    all_data = load_all_months(client_id)
    if not all_data:
        print(f"[WARN] {client_id} の時系列データが見つかりません。trend グラフをスキップします。", file=sys.stderr)
        return False

    # target_month 以前の最大 6 ヶ月を抽出
    filtered = [d for d in all_data if d.get("month", "") <= target_month]
    filtered = filtered[-6:]  # 最新 6 件

    if len(filtered) < 2:
        print(f"[WARN] 時系列データが 2 ヶ月未満（{len(filtered)} 件）のため trend グラフをスキップします。", file=sys.stderr)
        return False

    months = [d.get("month", "") for d in filtered]

    # 日本語フォント設定
    jp_fonts = ["Hiragino Sans", "Hiragino Kaku Gothic Pro", "Yu Gothic", "MS Gothic", "DejaVu Sans"]
    available = {f.name for f in fm.fontManager.ttflist}
    chosen_font = next((f for f in jp_fonts if f in available), None)
    if chosen_font:
        plt.rcParams["font.family"] = chosen_font
    plt.rcParams["axes.unicode_minus"] = False

    fig, ax = plt.subplots(figsize=(14, 6))
    fig.patch.set_facecolor("#FAFAFA")
    ax.set_facecolor("#FAFAFA")

    for idx, item in enumerate(GRAVITY_ITEMS):
        key    = item["key"]
        label  = item["label"]
        color  = TREND_COLORS[idx % len(TREND_COLORS)]
        linestyle = "-" if item["axis"] == "集まる" else "--"

        vals = []
        for d in filtered:
            sym = d.get("gravity_scores", {}).get("current", {}).get(key, None)
            sc  = sym_to_score(sym) if sym else None
            vals.append(int(sc) if sc is not None else None)

        # None 除外して折れ線描画
        valid_x = [i for i, v in enumerate(vals) if v is not None]
        valid_y = [v for v in vals if v is not None]
        if valid_x:
            ax.plot(valid_x, valid_y, marker="o", label=label, color=color,
                    linestyle=linestyle, linewidth=1.8, markersize=5)

    ax.set_xticks(list(range(len(months))))
    ax.set_xticklabels(months, rotation=15, ha="right", fontsize=9)
    ax.set_yticks([1, 2, 3, 4])
    ax.set_yticklabels(
        [f"{s.symbol}({s.value})" for s in [Score.CRITICAL, Score.NEEDS_ATTENTION, Score.GOOD, Score.EXCELLENT]],
        fontsize=10
    )
    ax.set_ylim(0.5, 4.5)
    ax.set_ylabel("スコア", fontsize=11)
    ax.set_title(
        f"引力 8 項目 時系列トレンド — {client_id}（直近 {len(filtered)} ヶ月）",
        fontsize=13, fontweight="bold", pad=12
    )

    # 集まる / 躍動の凡例補助
    r_patch = mpatches.Patch(color="#DBEAFE", alpha=0.7, label="集まる軸（実線）")
    c_patch = mpatches.Patch(color="#EDE9FE", alpha=0.7, label="躍動軸（破線）")
    handles, item_labels = ax.get_legend_handles_labels()
    ax.legend(handles=handles + [r_patch, c_patch],
              labels=item_labels + ["集まる軸（実線）", "躍動軸（破線）"],
              loc="lower right", fontsize=8, ncol=2)

    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return True


# ============================================================
# 拡張 4: PDF 出力（reportlab オプション依存）
# ============================================================

def _register_jp_font(rl: dict) -> str | None:
    """日本語フォントを reportlab に登録し、フォント名を返す。登録できなければ None。"""
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


def build_pdf(
    client_id: str,
    month: str,
    markdown_text: str,
    chart_path: str | None,
    output_path: str,
) -> bool:
    """
    Markdown レポートを A4 3p PDF に変換して出力する。
    reportlab がない場合は False を返す。
    """
    rl = _load_reportlab()
    if rl is None:
        print("[INFO] reportlab not installed, skipping PDF", file=sys.stderr)
        print("[INFO] インストール: pip install reportlab", file=sys.stderr)
        return False

    A4           = rl["A4"]
    colors       = rl["colors"]
    mm           = rl["mm"]
    SimpleDocTemplate = rl["SimpleDocTemplate"]
    Paragraph    = rl["Paragraph"]
    Spacer       = rl["Spacer"]
    Table        = rl["Table"]
    TableStyle   = rl["TableStyle"]
    Image        = rl["Image"]
    PageBreak    = rl["PageBreak"]
    getSampleStyleSheet = rl["getSampleStyleSheet"]
    ParagraphStyle = rl["ParagraphStyle"]

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=20 * mm, rightMargin=20 * mm,
        topMargin=20 * mm, bottomMargin=20 * mm,
        title=f"Gravity Orbit 月次引力レポート {month}",
        author="GrowthFix",
    )

    styles  = getSampleStyleSheet()
    jp_font = _register_jp_font(rl)
    base_fn = jp_font if jp_font else "Helvetica"

    style_title = ParagraphStyle(
        "OTitle", parent=styles["Title"],
        fontName=base_fn, fontSize=16, spaceAfter=8,
        textColor=colors.HexColor("#1E3A5F"),
    )
    style_h2 = ParagraphStyle(
        "OH2", parent=styles["Heading2"],
        fontName=base_fn, fontSize=12, spaceBefore=10, spaceAfter=4,
        textColor=colors.HexColor("#2563EB"),
    )
    style_body = ParagraphStyle(
        "OBody", parent=styles["Normal"],
        fontName=base_fn, fontSize=9, leading=14, spaceAfter=4,
    )
    style_small = ParagraphStyle(
        "OSmall", parent=styles["Normal"],
        fontName=base_fn, fontSize=8, textColor=colors.grey,
    )

    story = []

    # p.1 表紙 + スコア表
    now_jst = datetime.now(JST).strftime("%Y-%m-%d %H:%M JST")
    story.append(Paragraph("Gravity Orbit 月次引力レポート", style_title))
    story.append(Paragraph(f"クライアント: {client_id} | 対象月: {month} | 生成: {now_jst}", style_small))
    story.append(Spacer(1, 6 * mm))

    # グラフ埋め込み
    if chart_path and os.path.exists(chart_path):
        try:
            img = Image(chart_path, width=170 * mm, height=85 * mm)
            story.append(img)
            story.append(Spacer(1, 4 * mm))
        except Exception as e:
            story.append(Paragraph(f"[グラフ埋め込みエラー: {e}]", style_small))

    # スコア凡例
    story.append(Paragraph(
        f"スコア基準: ◎=4（良好）/ ○=3（概ね良好）/ △=2（要改善）/ ×=1（要緊急対応）",
        style_small
    ))
    story.append(PageBreak())

    # p.2 改善提案（Markdown テキストから該当部分を抜粋）
    story.append(Paragraph("p.2 改善提案（α/β/γ/δ マッピング）", style_h2))
    story.append(Spacer(1, 3 * mm))
    in_p2 = False
    for line in markdown_text.splitlines():
        if line.startswith("## p.2"):
            in_p2 = True
            continue
        if in_p2 and line.startswith("## p.3"):
            break
        if in_p2 and line.strip():
            # Markdown テーブル行を簡易テキスト化
            if line.startswith("|") and not line.startswith("|---|"):
                cells = [c.strip() for c in line.split("|")[1:-1]]
                story.append(Paragraph(" | ".join(cells), style_body))
            elif not line.startswith("|---"):
                story.append(Paragraph(line.lstrip("#> "), style_body))

    story.append(PageBreak())

    # p.3 離職予兆
    story.append(Paragraph("p.3 離職予兆 5 シグナル 早期警戒スコア", style_h2))
    story.append(Spacer(1, 3 * mm))
    in_p3 = False
    for line in markdown_text.splitlines():
        if line.startswith("## p.3"):
            in_p3 = True
            continue
        if in_p3 and line.strip():
            if line.startswith("|") and not line.startswith("|---|"):
                cells = [c.strip() for c in line.split("|")[1:-1]]
                story.append(Paragraph(" | ".join(cells), style_body))
            elif not line.startswith("|---") and not line.startswith("---"):
                story.append(Paragraph(line.lstrip("#> ").lstrip("*"), style_body))

    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph(
        "本レポートは Gravity Orbit 月次引力レポート（A4 3p）の自動生成物です。",
        style_small
    ))

    try:
        doc.build(story)
        return True
    except Exception as e:
        print(f"[ERROR] PDF 生成に失敗しました: {e}", file=sys.stderr)
        return False


# ============================================================
# メイン処理
# ============================================================

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Orbit 月次引力レポート 自動生成（Phase 1）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python3 orbit_monthly_report.py --client sample_orbit_client --month 2026-05
  python3 orbit_monthly_report.py --client sample_orbit_client --month 2026-05 --trend
  python3 orbit_monthly_report.py --client sample_orbit_client --month 2026-05 --pdf

入力ファイル:
  orbit_data/<CLIENT_ID>_<YYYY-MM>.json
  orbit_data/orbit_actions_map.json

出力:
  - stdout: Markdown 形式レポート（p.1 / p.2 / p.3）
  - orbit_reports/<CLIENT_ID>_<YYYY-MM>.png: 棒グラフ（要 matplotlib）
  - orbit_reports/<CLIENT_ID>_<YYYY-MM>_trend.png: 時系列グラフ（--trend 時）
  - orbit_reports/<CLIENT_ID>_<YYYY-MM>.pdf: A4 PDF（--pdf 時・要 reportlab）
        """,
    )
    parser.add_argument("--client",   required=True,  help="クライアントID（例: sample_orbit_client）")
    parser.add_argument("--month",    required=True,  help="対象月 YYYY-MM（例: 2026-05）")
    parser.add_argument("--no-chart", action="store_true", help="PNG グラフ出力をスキップ")
    parser.add_argument("--trend",    action="store_true", help="過去 6 ヶ月時系列グラフを生成")
    parser.add_argument("--pdf",      action="store_true", help="PDF 出力（要 reportlab）")
    args = parser.parse_args()

    client_id = args.client
    month     = args.month

    # 月フォーマット検証
    try:
        datetime.strptime(month, "%Y-%m")
    except ValueError:
        print(f"[ERROR] --month の形式が不正です: '{month}'（正しい形式: YYYY-MM）", file=sys.stderr)
        sys.exit(1)

    # データ読み込み
    print(f"[INFO] データ読み込み: {client_id} / {month}", file=sys.stderr)
    try:
        data = load_json(client_id, month)
    except FileNotFoundError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)

    # バリデーション
    try:
        validate_data(data)
    except ValueError as e:
        print(f"[ERROR] データ検証エラー: {e}", file=sys.stderr)
        sys.exit(1)

    # α/β/γ/δ ルール読み込み
    actions_map = load_actions_map()
    rules = actions_map.get("rules", [])

    # レポート生成（Markdown 3p）
    report_parts = [
        build_page1(data),
        build_page2(data, rules),
        build_page3(data),
    ]
    full_report = "\n".join(report_parts)
    print(full_report)

    os.makedirs(REPORT_DIR, exist_ok=True)

    # 棒グラフ生成
    chart_path = None
    if not args.no_chart:
        chart_path = os.path.join(REPORT_DIR, f"{client_id}_{month}.png")
        print(f"[INFO] PNG 生成: {chart_path}", file=sys.stderr)
        try:
            if build_chart(data, chart_path):
                size_kb = os.path.getsize(chart_path) // 1024
                print(f"[OK]  PNG 出力完了: {chart_path} ({size_kb} KB)", file=sys.stderr)
            else:
                chart_path = None
        except (ValueError, OSError, RuntimeError) as e:
            print(f"[WARN] PNG 生成中にエラーが発生しました: {e}", file=sys.stderr)
            chart_path = None
    else:
        print("[INFO] --no-chart 指定につき PNG 出力をスキップ", file=sys.stderr)

    # 時系列グラフ生成（--trend）
    if args.trend:
        trend_path = os.path.join(REPORT_DIR, f"{client_id}_{month}_trend.png")
        print(f"[INFO] 時系列 PNG 生成: {trend_path}", file=sys.stderr)
        try:
            if build_trend_chart(client_id, month, trend_path):
                size_kb = os.path.getsize(trend_path) // 1024
                print(f"[OK]  trend PNG 出力完了: {trend_path} ({size_kb} KB)", file=sys.stderr)
        except (ValueError, OSError, RuntimeError) as e:
            print(f"[WARN] trend PNG 生成中にエラーが発生しました: {e}", file=sys.stderr)

    # PDF 生成（--pdf）
    if args.pdf:
        pdf_path = os.path.join(REPORT_DIR, f"{client_id}_{month}.pdf")
        print(f"[INFO] PDF 生成: {pdf_path}", file=sys.stderr)
        try:
            if build_pdf(client_id, month, full_report, chart_path, pdf_path):
                size_kb = os.path.getsize(pdf_path) // 1024
                print(f"[OK]  PDF 出力完了: {pdf_path} ({size_kb} KB)", file=sys.stderr)
        except (ValueError, OSError, RuntimeError) as e:
            print(f"[WARN] PDF 生成中にエラーが発生しました: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
