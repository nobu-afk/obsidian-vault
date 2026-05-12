"""
Orbit 四半期 4 型再判定書 自動生成スクリプト

Orbit v3.0 単一プラン（月15万）の3点セット納品物のうち
「③ Quarterly 4型再判定書 A4 5p」を自動生成するスクリプト。

使い方:
  python3 orbit_quarterly_review.py --client <CLIENT_ID> --quarter YYYY-Q<N>

例:
  python3 orbit_quarterly_review.py --client sample_orbit_client --quarter 2026-Q2

入力:
  06_開発/scripts/orbit_data/<CLIENT_ID>_YYYY-MM.json（当四半期の月データ）

出力:
  - stdout: Markdown 形式（A4 5p 相当）
    - p.1 4 型再判定（整合/拡散/渇望/不毛）
    - p.2 構造進化検知（先 quarter との比較）
    - p.3 KPI 達成状況（Orbit 5 KPI）
    - p.4 次期戦略提案
    - p.5 石井深堀コメント枠

4 型判定ロジック（SSOT §13.1 集まる/躍動 2 軸）:
  集まる軸（①②⑦）平均 vs 躍動軸（③④⑤⑥⑧）平均 → 2x2 マトリクス
  - 集まる ≥ 3.0 + 躍動 ≥ 3.0 → 整合型（→ Orbit 継続推奨）
  - 集まる ≥ 3.0 + 躍動 < 3.0 → 拡散型（→ Shift C 推奨）
  - 集まる < 3.0 + 躍動 ≥ 3.0 → 渇望型（→ Shift R 推奨）
  - 集まる < 3.0 + 躍動 < 3.0 → 不毛型（→ Shift Full 推奨）

引力8項目 SSOT: 05_プロダクト/_共通/SSOT_用語と定義.md §13.1
"""

import os
import sys
import json
import glob
import argparse
import re
from datetime import datetime, timezone, timedelta
from enum import IntEnum


# ============================================================
# 定数・マッピング
# ============================================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR   = os.path.join(SCRIPT_DIR, "orbit_data")
REPORT_DIR = os.path.join(SCRIPT_DIR, "orbit_reports")

JST = timezone(timedelta(hours=9))

# Score IntEnum（orbit_monthly_report.py と同一定義）
class Score(IntEnum):
    """引力スコア 4 段階"""
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
    def from_symbol_safe(cls, sym: str) -> "Score | None":
        mapping = {"◎": cls.EXCELLENT, "○": cls.GOOD, "△": cls.NEEDS_ATTENTION, "×": cls.CRITICAL}
        return mapping.get(sym)


# 引力8項目（SSOT §13.1 準拠）
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

# 集まる軸・躍動軸のキー分類
AXIS_R_KEYS = [it["key"] for it in GRAVITY_ITEMS if it["axis"] == "集まる"]  # ①②⑦
AXIS_C_KEYS = [it["key"] for it in GRAVITY_ITEMS if it["axis"] == "躍動"]    # ③④⑤⑥⑧

# 4 型定義（SSOT 組織の引力 4 型）
TYPE_DEFINITIONS = {
    "整合型": {
        "condition": "集まる ≥ 3.0 かつ 躍動 ≥ 3.0",
        "description": "採用力と組織活力が両立している状態。Orbit 継続で引力を複利的に強化できる段階。",
        "next_service": "Orbit 継続推奨",
        "next_service_detail": "現状の引力を維持・強化しながら Gravity 型成長加速を継続。月次引力レポートによるモニタリングを徹底。",
    },
    "拡散型": {
        "condition": "集まる ≥ 3.0 かつ 躍動 < 3.0",
        "description": "採用力はあるが組織内活力が不足している状態。採用した人材が躍動できる環境の設計が急務。",
        "next_service": "Shift C（躍動組織設計）推奨",
        "next_service_detail": "幹部発話量・エンゲージメント・心理的安全性を中心とした Shift C（150 万・6 ヶ月）の導入を検討。",
    },
    "渇望型": {
        "condition": "集まる < 3.0 かつ 躍動 ≥ 3.0",
        "description": "組織内は活性化しているが採用力が不足している状態。優秀人材を引きつける採用基盤の構築が優先課題。",
        "next_service": "Shift R（採用基盤設計）推奨",
        "next_service_detail": "採用パイプライン・面接設計・PO Fit 判定を中心とした Shift R（80 万・3 ヶ月）の導入を検討。",
    },
    "不毛型": {
        "condition": "集まる < 3.0 かつ 躍動 < 3.0",
        "description": "採用力・組織活力が共に不足している状態。採用と躍動の両軸を同時に立て直す抜本的な構造改革が必要。",
        "next_service": "Shift Full（R+C 統合）推奨",
        "next_service_detail": "採用基盤と躍動組織設計を同時に行う Shift Full（220 万・9 ヶ月）の導入を強く推奨。",
    },
}

# Orbit 5 KPI 定義（project_orbit_direct.md 準拠）
ORBIT_5KPI = [
    {
        "id": "KPI-1",
        "name": "引力 8 項目改善率",
        "description": "四半期初月対比での ×/△ 項目数の減少率",
        "target": "×/△ 項目数 20% 以上削減",
    },
    {
        "id": "KPI-2",
        "name": "4 型推移",
        "description": "四半期での引力タイプ変化（不毛→渇望/拡散→整合の方向性）",
        "target": "整合型へのベクトル維持、または同型内でのスコア向上",
    },
    {
        "id": "KPI-3",
        "name": "採用パイプライン健全性",
        "description": "recruitment_pipeline + final_decline_rate の平均スコア",
        "target": "○（3.0）以上",
    },
    {
        "id": "KPI-4",
        "name": "エンゲージメントスコア改善率",
        "description": "engagement スコアの四半期初月対比改善幅",
        "target": "1 段階以上の改善（△→○ 等）",
    },
    {
        "id": "KPI-5",
        "name": "Gravity 型成長度",
        "description": "8 項目平均スコアの四半期での変化量",
        "target": "平均スコア +0.3 以上の改善",
    },
]


# ============================================================
# 四半期ユーティリティ
# ============================================================

def parse_quarter(quarter_str: str) -> tuple[int, int]:
    """
    YYYY-Q1 〜 YYYY-Q4 をパースして (year, quarter_num) を返す。
    不正形式は ValueError を送出。
    """
    m = re.fullmatch(r"(\d{4})-Q([1-4])", quarter_str)
    if not m:
        raise ValueError(
            f"quarter の形式が不正です: '{quarter_str}'（正しい形式: YYYY-Q1 〜 YYYY-Q4）"
        )
    return int(m.group(1)), int(m.group(2))


def quarter_months(year: int, q: int) -> list[str]:
    """四半期の YYYY-MM リストを返す（例: 2026-Q2 → ['2026-04', '2026-05', '2026-06']）"""
    q_start = {1: 1, 2: 4, 3: 7, 4: 10}[q]
    return [f"{year}-{q_start + i:02d}" for i in range(3)]


def prev_quarter(year: int, q: int) -> tuple[int, int]:
    """前四半期の (year, quarter_num) を返す"""
    if q == 1:
        return year - 1, 4
    return year, q - 1


def load_json_safe(client_id: str, month: str) -> dict | None:
    """月データを読み込む。ファイルがなければ None を返す（警告なし）"""
    filename = f"{client_id}_{month}.json"
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        return None
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"[WARN] {filepath} の読み込みに失敗しました: {e}", file=sys.stderr)
        return None


def extract_scores(data: dict) -> dict[str, Score | None]:
    """JSON データから gravity_scores.current を {key: Score} 形式で抽出"""
    current = data.get("gravity_scores", {}).get("current", {})
    return {
        item["key"]: Score.from_symbol_safe(current.get(item["key"], "?"))
        for item in GRAVITY_ITEMS
    }


def calc_axis_avg(scores: dict[str, Score | None], axis_keys: list[str]) -> float | None:
    """指定軸キーの平均スコアを計算。全て None の場合は None を返す"""
    vals = [int(scores[k]) for k in axis_keys if scores.get(k) is not None]
    return sum(vals) / len(vals) if vals else None


def determine_type(r_avg: float | None, c_avg: float | None) -> str:
    """集まる / 躍動の平均スコアから 4 型を判定"""
    if r_avg is None or c_avg is None:
        return "判定不能（データ不足）"
    if r_avg >= 3.0 and c_avg >= 3.0:
        return "整合型"
    elif r_avg >= 3.0 and c_avg < 3.0:
        return "拡散型"
    elif r_avg < 3.0 and c_avg >= 3.0:
        return "渇望型"
    else:
        return "不毛型"


def calc_overall_avg(scores: dict[str, Score | None]) -> float | None:
    """全 8 項目の平均スコアを計算"""
    vals = [int(s) for s in scores.values() if s is not None]
    return sum(vals) / len(vals) if vals else None


# ============================================================
# レポート生成: 集計データ構造
# ============================================================

def build_quarterly_summary(monthly_data: list[dict]) -> dict:
    """
    当四半期の月次データから集計サマリーを構築する。
    戻り値: {
        "months": list[str],
        "monthly_scores": list[dict],  # [{key: Score|None, ...}]
        "avg_scores": dict,            # {key: float|None}
        "r_avg": float|None,
        "c_avg": float|None,
        "overall_avg": float|None,
        "gravity_type": str,
        "alert_items": list[str],      # ×/△ 項目キー
        "first_month_scores": dict,    # 四半期初月スコア
        "last_month_scores": dict,     # 四半期最終月スコア
    }
    """
    months = [d.get("month", "") for d in monthly_data]
    monthly_scores = [extract_scores(d) for d in monthly_data]

    # 項目ごとの四半期平均
    avg_scores = {}
    for item in GRAVITY_ITEMS:
        k = item["key"]
        vals = [int(ms[k]) for ms in monthly_scores if ms.get(k) is not None]
        avg_scores[k] = sum(vals) / len(vals) if vals else None

    # 軸平均
    r_avg = calc_axis_avg(avg_scores, AXIS_R_KEYS)
    c_avg = calc_axis_avg(avg_scores, AXIS_C_KEYS)
    overall_avg = calc_overall_avg(avg_scores)

    # 4 型判定
    gravity_type = determine_type(r_avg, c_avg)

    # 警戒項目（平均 < 2.5 = △ 寄り or ×）
    alert_items = [k for k, v in avg_scores.items() if v is not None and v < 2.5]

    # 初月・最終月スコア
    first_month_scores = monthly_scores[0] if monthly_scores else {}
    last_month_scores  = monthly_scores[-1] if monthly_scores else {}

    return {
        "months": months,
        "monthly_scores": monthly_scores,
        "avg_scores": avg_scores,
        "r_avg": r_avg,
        "c_avg": c_avg,
        "overall_avg": overall_avg,
        "gravity_type": gravity_type,
        "alert_items": alert_items,
        "first_month_scores": first_month_scores,
        "last_month_scores":  last_month_scores,
    }


# ============================================================
# p.1 4 型再判定
# ============================================================

def build_page1(
    client_id: str,
    quarter_str: str,
    summary: dict,
    months_count: int,
    now_jst: str,
) -> str:
    """p.1: 組織引力 4 型再判定"""
    gravity_type = summary["gravity_type"]
    r_avg        = summary["r_avg"]
    c_avg        = summary["c_avg"]
    overall_avg  = summary["overall_avg"]
    avg_scores   = summary["avg_scores"]
    months       = summary["months"]

    type_def = TYPE_DEFINITIONS.get(gravity_type, {})

    lines = []
    lines.append("# Gravity Orbit 四半期 4 型再判定書")
    lines.append("")
    lines.append(f"**クライアント:** {client_id}  ")
    lines.append(f"**対象四半期:** {quarter_str}（{', '.join(months)} — {months_count} ヶ月分）  ")
    lines.append(f"**生成日時:** {now_jst}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## p.1 組織引力 4 型 再判定")
    lines.append("")

    if months_count < 3:
        lines.append(
            f"> [WARNING] データが {months_count} ヶ月分のみです（3 ヶ月満ていない）。"
            f"判定精度が低くなる可能性があります。3 ヶ月揃ってから本番運用することを推奨します。"
        )
        lines.append("")

    # 4 型マトリクス
    lines.append("### 2x2 引力マトリクス（四半期平均スコアによる判定）")
    lines.append("")
    lines.append(f"| | 躍動軸 ≥ 3.0（良好） | 躍動軸 < 3.0（不足） |")
    lines.append("|---|---|---|")
    lines.append(
        f"| **集まる軸 ≥ 3.0（良好）** | "
        f"{'**★ 整合型**' if gravity_type == '整合型' else '整合型'} | "
        f"{'**★ 拡散型**' if gravity_type == '拡散型' else '拡散型'} |"
    )
    lines.append(
        f"| **集まる軸 < 3.0（不足）** | "
        f"{'**★ 渇望型**' if gravity_type == '渇望型' else '渇望型'} | "
        f"{'**★ 不毛型**' if gravity_type == '不毛型' else '不毛型'} |"
    )
    lines.append("")

    # 判定結果
    r_avg_str = f"{r_avg:.2f}" if r_avg is not None else "データなし"
    c_avg_str = f"{c_avg:.2f}" if c_avg is not None else "データなし"
    o_avg_str = f"{overall_avg:.2f}" if overall_avg is not None else "データなし"

    lines.append(f"### 判定結果: **{gravity_type}**")
    lines.append("")
    lines.append(f"| 軸 | 四半期平均スコア | 判定閾値 | 状態 |")
    lines.append("|---|:-:|:-:|---|")
    lines.append(
        f"| 集まる軸（①②⑦） | **{r_avg_str}** | 3.0 | "
        f"{'良好' if r_avg is not None and r_avg >= 3.0 else '不足'} |"
    )
    lines.append(
        f"| 躍動軸（③④⑤⑥⑧） | **{c_avg_str}** | 3.0 | "
        f"{'良好' if c_avg is not None and c_avg >= 3.0 else '不足'} |"
    )
    lines.append(f"| 全 8 項目平均 | **{o_avg_str}** | — | — |")
    lines.append("")

    if type_def:
        lines.append(f"**{gravity_type} の意味:**")
        lines.append(f"> {type_def.get('description', '')}")
        lines.append("")

    # 項目別四半期平均
    lines.append("### 引力 8 項目 四半期平均スコア詳細")
    lines.append("")
    lines.append("| 項目 | 軸 | 四半期平均 | 評価 |")
    lines.append("|---|:-:|:-:|---|")
    for item in GRAVITY_ITEMS:
        k    = item["key"]
        avg  = avg_scores.get(k)
        axis = item["axis"]
        if avg is not None:
            # 最近傍スコアで評価テキスト取得
            nearest = Score(max(1, min(4, round(avg))))
            eval_txt = nearest.label
            avg_str  = f"{avg:.2f}"
        else:
            eval_txt = "データなし"
            avg_str  = "-"
        lines.append(f"| {item['label']} | {axis} | {avg_str} | {eval_txt} |")

    lines.append("")

    # 推奨ネクストサービス
    if type_def:
        lines.append(f"### 推奨ネクストサービス: {type_def.get('next_service', '-')}")
        lines.append("")
        lines.append(f"{type_def.get('next_service_detail', '')}")
        lines.append("")

    return "\n".join(lines)


# ============================================================
# p.2 構造進化検知（先 quarter との比較）
# ============================================================

def build_page2(
    summary: dict,
    prev_summary: dict | None,
    quarter_str: str,
    prev_quarter_str: str,
) -> str:
    """p.2: 構造進化検知（今 Q vs 前 Q の比較）"""
    lines = []
    lines.append("---")
    lines.append("")
    lines.append("## p.2 構造進化検知")
    lines.append("")
    lines.append(f"**比較軸:** {prev_quarter_str} → {quarter_str}")
    lines.append("")

    if prev_summary is None:
        lines.append("> 前四半期データが存在しないため比較できません。")
        lines.append("> 次四半期以降のレポートで自動比較が可能になります。")
        lines.append("")
        return "\n".join(lines)

    # 4 型変化
    prev_type = prev_summary.get("gravity_type", "-")
    curr_type = summary["gravity_type"]
    type_changed = prev_type != curr_type

    lines.append("### 引力タイプの変化")
    lines.append("")
    lines.append(f"| | {prev_quarter_str} | {quarter_str} | 変化 |")
    lines.append("|---|:-:|:-:|:-:|")
    change_marker = "**変化あり**" if type_changed else "変化なし"
    lines.append(f"| 引力タイプ | {prev_type} | **{curr_type}** | {change_marker} |")

    prev_r = prev_summary.get("r_avg")
    prev_c = prev_summary.get("c_avg")
    prev_o = prev_summary.get("overall_avg")
    curr_r = summary["r_avg"]
    curr_c = summary["c_avg"]
    curr_o = summary["overall_avg"]

    def _diff_str(cur: float | None, prev: float | None) -> str:
        if cur is None or prev is None:
            return "-"
        d = cur - prev
        return f"+{d:.2f}" if d > 0 else (f"{d:.2f}" if d < 0 else "±0")

    lines.append(
        f"| 集まる軸平均 | "
        f"{f'{prev_r:.2f}' if prev_r is not None else '-'} | "
        f"**{f'{curr_r:.2f}' if curr_r is not None else '-'}** | "
        f"{_diff_str(curr_r, prev_r)} |"
    )
    lines.append(
        f"| 躍動軸平均 | "
        f"{f'{prev_c:.2f}' if prev_c is not None else '-'} | "
        f"**{f'{curr_c:.2f}' if curr_c is not None else '-'}** | "
        f"{_diff_str(curr_c, prev_c)} |"
    )
    lines.append(
        f"| 全体平均 | "
        f"{f'{prev_o:.2f}' if prev_o is not None else '-'} | "
        f"**{f'{curr_o:.2f}' if curr_o is not None else '-'}** | "
        f"{_diff_str(curr_o, prev_o)} |"
    )
    lines.append("")

    # 項目別変化
    lines.append("### 引力 8 項目 スコア変化（四半期平均）")
    lines.append("")
    lines.append(f"| 項目 | {prev_quarter_str} | {quarter_str} | 変化 |")
    lines.append("|---|:-:|:-:|:-:|")

    prev_avg = prev_summary.get("avg_scores", {})
    curr_avg = summary["avg_scores"]

    for item in GRAVITY_ITEMS:
        k    = item["key"]
        pv   = prev_avg.get(k)
        cv   = curr_avg.get(k)
        pv_s = f"{pv:.2f}" if pv is not None else "-"
        cv_s = f"{cv:.2f}" if cv is not None else "-"
        diff = _diff_str(cv, pv)
        if cv is not None and pv is not None:
            d = cv - pv
            if d >= 0.5:
                diff = f"▲ {diff}"
            elif d <= -0.5:
                diff = f"▼ {diff}"
        lines.append(f"| {item['label']} | {pv_s} | **{cv_s}** | {diff} |")

    lines.append("")

    # 変化の総評
    if curr_o is not None and prev_o is not None:
        delta = curr_o - prev_o
        if delta > 0:
            comment = f"全体引力スコアが {delta:+.2f} 改善しました。組織引力の強化が確認できています。"
        elif delta < 0:
            comment = f"全体引力スコアが {delta:.2f} 低下しました。次期の集中介入が必要です。"
        else:
            comment = "全体引力スコアに変化はありませんでした。維持できている項目と悪化傾向の項目を精査してください。"
        lines.append(f"> {comment}")
        lines.append("")

    return "\n".join(lines)


# ============================================================
# p.3 KPI 達成状況
# ============================================================

def build_page3(summary: dict, first_month_data: dict | None, quarter_str: str) -> str:
    """p.3: Orbit 5 KPI 達成状況"""
    lines = []
    lines.append("---")
    lines.append("")
    lines.append("## p.3 KPI 達成状況（Orbit 5 KPI）")
    lines.append("")
    lines.append(f"**対象四半期:** {quarter_str}")
    lines.append("")

    curr_avg     = summary["avg_scores"]
    overall_avg  = summary["overall_avg"]
    gravity_type = summary["gravity_type"]
    r_avg        = summary["r_avg"]
    alert_items  = summary["alert_items"]
    first_scores = summary["first_month_scores"]
    last_scores  = summary["last_month_scores"]

    lines.append("| KPI | 名称 | 目標 | 実績 | 達成 |")
    lines.append("|:-:|---|---|---|:-:|")

    # KPI-1: 引力 8 項目改善率（初月対比 ×/△ 項目数減少率）
    first_weak = sum(1 for sc in first_scores.values() if sc is not None and sc <= Score.NEEDS_ATTENTION)
    last_weak  = sum(1 for sc in last_scores.values()  if sc is not None and sc <= Score.NEEDS_ATTENTION)
    if first_weak > 0:
        improvement_rate = (first_weak - last_weak) / first_weak * 100
        kpi1_actual = f"×/△: {first_weak}→{last_weak}件（{improvement_rate:.0f}%改善）"
        kpi1_ok = "O" if improvement_rate >= 20 else "×"
    else:
        kpi1_actual = "初月データなし"
        kpi1_ok = "-"
    lines.append(f"| KPI-1 | 引力 8 項目改善率 | ×/△ 20%以上削減 | {kpi1_actual} | {kpi1_ok} |")

    # KPI-2: 4 型推移
    kpi2_actual = gravity_type
    kpi2_ok = "O" if gravity_type == "整合型" else ("△" if "整合" in gravity_type else "-")
    lines.append(f"| KPI-2 | 4 型推移 | 整合型方向のベクトル | {kpi2_actual} | {kpi2_ok} |")

    # KPI-3: 採用パイプライン健全性（①② 平均）
    pipe_vals = [
        avg for k, avg in curr_avg.items()
        if k in ("recruitment_pipeline", "final_decline_rate") and avg is not None
    ]
    pipe_avg = sum(pipe_vals) / len(pipe_vals) if pipe_vals else None
    if pipe_avg is not None:
        kpi3_actual = f"集まる主要 2 項目平均 {pipe_avg:.2f}"
        kpi3_ok = "O" if pipe_avg >= 3.0 else "×"
    else:
        kpi3_actual = "データなし"
        kpi3_ok = "-"
    lines.append(f"| KPI-3 | 採用パイプライン健全性 | ○（3.0）以上 | {kpi3_actual} | {kpi3_ok} |")

    # KPI-4: エンゲージメントスコア改善率（初月→最終月）
    first_eng = first_scores.get("engagement")
    last_eng  = last_scores.get("engagement")
    if first_eng is not None and last_eng is not None:
        eng_diff = int(last_eng) - int(first_eng)
        kpi4_actual = f"{first_eng.symbol}→{last_eng.symbol}（{'+' if eng_diff >= 0 else ''}{eng_diff}段階）"
        kpi4_ok = "O" if eng_diff >= 1 else ("△" if eng_diff == 0 else "×")
    else:
        kpi4_actual = "データなし"
        kpi4_ok = "-"
    lines.append(f"| KPI-4 | エンゲージメント改善率 | 1 段階以上改善 | {kpi4_actual} | {kpi4_ok} |")

    # KPI-5: Gravity 型成長度（全体平均スコア変化）
    first_overall = calc_avg_safe([int(s) for s in first_scores.values() if s is not None])
    last_overall  = calc_avg_safe([int(s) for s in last_scores.values()  if s is not None])
    if first_overall is not None and last_overall is not None:
        growth = last_overall - first_overall
        kpi5_actual = f"平均 {first_overall:.2f}→{last_overall:.2f}（{'+' if growth >= 0 else ''}{growth:.2f}）"
        kpi5_ok = "O" if growth >= 0.3 else ("△" if growth >= 0 else "×")
    elif overall_avg is not None:
        kpi5_actual = f"四半期平均 {overall_avg:.2f}（初月比較不可）"
        kpi5_ok = "-"
    else:
        kpi5_actual = "データなし"
        kpi5_ok = "-"
    lines.append(f"| KPI-5 | Gravity 型成長度 | 平均 +0.3 以上 | {kpi5_actual} | {kpi5_ok} |")

    lines.append("")
    lines.append("> O=達成 / △=部分達成・経過観察 / ×=未達 / -=判定不能")
    lines.append("")

    # 警戒項目サマリー
    if alert_items:
        lines.append("### 要注意項目（四半期平均 2.5 未満）")
        lines.append("")
        for k in alert_items:
            item_def = next((it for it in GRAVITY_ITEMS if it["key"] == k), None)
            label = item_def["label"] if item_def else k
            avg   = curr_avg.get(k)
            avg_s = f"{avg:.2f}" if avg is not None else "-"
            lines.append(f"- **{label}**: 四半期平均 {avg_s}（要集中介入）")
        lines.append("")

    return "\n".join(lines)


def calc_avg_safe(vals: list[int]) -> float | None:
    """リストが空なら None、そうでなければ平均を返す"""
    return sum(vals) / len(vals) if vals else None


# ============================================================
# p.4 次期戦略提案
# ============================================================

def build_page4(summary: dict, quarter_str: str) -> str:
    """p.4: 次期戦略提案"""
    gravity_type = summary["gravity_type"]
    r_avg        = summary["r_avg"]
    c_avg        = summary["c_avg"]
    alert_items  = summary["alert_items"]
    curr_avg     = summary["avg_scores"]

    type_def = TYPE_DEFINITIONS.get(gravity_type, {})

    lines = []
    lines.append("---")
    lines.append("")
    lines.append("## p.4 次期戦略提案")
    lines.append("")
    lines.append(f"**{quarter_str} の判定結果（{gravity_type}）を踏まえた次期アクション**")
    lines.append("")

    # タイプ別推奨
    if type_def:
        lines.append(f"### サービス方針: {type_def.get('next_service', '-')}")
        lines.append("")
        lines.append(f"{type_def.get('next_service_detail', '')}")
        lines.append("")

    # 軸別フォーカス
    lines.append("### 次期フォーカス軸")
    lines.append("")
    r_str = f"{r_avg:.2f}" if r_avg is not None else "不明"
    c_str = f"{c_avg:.2f}" if c_avg is not None else "不明"

    if r_avg is not None and r_avg < 3.0:
        lines.append(f"**[集まる軸 優先（現 {r_str}）]** 採用力の強化を最優先課題として設定する。")
        lines.append("")
        # 集まる軸の最低スコア項目を特定
        r_items_sorted = sorted(
            [(k, v) for k, v in curr_avg.items() if k in AXIS_R_KEYS and v is not None],
            key=lambda x: x[1]
        )
        if r_items_sorted:
            worst_key = r_items_sorted[0][0]
            worst_def = next((it for it in GRAVITY_ITEMS if it["key"] == worst_key), None)
            worst_label = worst_def["label"] if worst_def else worst_key
            lines.append(f"- 最優先改善項目: **{worst_label}**（四半期平均 {r_items_sorted[0][1]:.2f}）")
        lines.append("")

    if c_avg is not None and c_avg < 3.0:
        lines.append(f"**[躍動軸 優先（現 {c_str}）]** 組織活力の強化を重要課題として設定する。")
        lines.append("")
        c_items_sorted = sorted(
            [(k, v) for k, v in curr_avg.items() if k in AXIS_C_KEYS and v is not None],
            key=lambda x: x[1]
        )
        if c_items_sorted:
            worst_key = c_items_sorted[0][0]
            worst_def = next((it for it in GRAVITY_ITEMS if it["key"] == worst_key), None)
            worst_label = worst_def["label"] if worst_def else worst_key
            lines.append(f"- 最優先改善項目: **{worst_label}**（四半期平均 {c_items_sorted[0][1]:.2f}）")
        lines.append("")

    if gravity_type == "整合型":
        lines.append(f"**[現状維持・強化フェーズ（{r_str} / {c_str}）]**")
        lines.append("両軸が良好水準にあります。現状の引力を維持しながら更なる高みを目指す。")
        lines.append("")

    # 次期重点アクション（上位 3 件）
    lines.append("### 次期重点アクション（TOP 3）")
    lines.append("")

    action_candidates = []

    # 最低スコア項目ベースのアクション
    sorted_items = sorted(
        [(k, v) for k, v in curr_avg.items() if v is not None],
        key=lambda x: x[1]
    )
    for rank, (k, avg_val) in enumerate(sorted_items[:3], 1):
        item_def = next((it for it in GRAVITY_ITEMS if it["key"] == k), None)
        label    = item_def["label"] if item_def else k
        axis     = item_def["axis"] if item_def else "-"
        sc_near  = Score(max(1, min(4, round(avg_val))))
        action_candidates.append(
            f"{rank}. **【{axis}軸】{label}** の改善（現 {avg_val:.2f} = {sc_near.label}）"
            f" — 次四半期で {Score(min(4, int(sc_near) + 1)).symbol} への引き上げを目標に設定"
        )

    for ac in action_candidates:
        lines.append(ac)

    lines.append("")
    lines.append(
        "> 具体的な改善施策は月次引力レポート p.2（α/β/γ/δ マッピング）を参照してください。"
    )
    lines.append("")

    return "\n".join(lines)


# ============================================================
# p.5 石井深堀コメント枠
# ============================================================

def build_page5(client_id: str, quarter_str: str, gravity_type: str) -> str:
    """p.5: 石井深堀コメント枠（空欄テンプレート）"""
    lines = []
    lines.append("---")
    lines.append("")
    lines.append("## p.5 石井深堀コメント")
    lines.append("")
    lines.append(f"**クライアント:** {client_id} | **四半期:** {quarter_str} | **判定タイプ:** {gravity_type}")
    lines.append("")
    lines.append("*（以下のフレームに沿って月次セッション後に記入する）*")
    lines.append("")

    sections = [
        ("この四半期で最も印象的だった変化・成長", "（記入欄）"),
        ("経営者の「覚悟」と「実行力」の観察",     "（記入欄）"),
        ("組織の引力が高まった瞬間（具体エピソード）", "（記入欄）"),
        ("次四半期の「一言仮説」（予言の書 更新候補）", "（記入欄）"),
        ("石井から経営者へのメッセージ",              "（記入欄）"),
    ]

    for idx, (title, placeholder) in enumerate(sections, 1):
        lines.append(f"### {idx}. {title}")
        lines.append("")
        lines.append(placeholder)
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(
        "*本レポートは Gravity Orbit 四半期 4 型再判定書（A4 5p）の自動生成物です。*  "
    )
    lines.append(
        "*月次引力レポートは別途 `orbit_monthly_report.py` で生成します。*"
    )
    lines.append("")

    return "\n".join(lines)


# ============================================================
# メイン処理
# ============================================================

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Orbit 四半期 4 型再判定書 自動生成",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python3 orbit_quarterly_review.py --client sample_orbit_client --quarter 2026-Q2

入力ファイル:
  orbit_data/<CLIENT_ID>_YYYY-MM.json（当四半期 3 ヶ月分）

出力:
  stdout: Markdown（A4 5p 相当）
  orbit_reports/<CLIENT_ID>_<QUARTER>.md: ファイル保存
        """,
    )
    parser.add_argument("--client",  required=True, help="クライアントID（例: sample_orbit_client）")
    parser.add_argument("--quarter", required=True, help="四半期 YYYY-Q1〜Q4（例: 2026-Q2）")
    args = parser.parse_args()

    client_id    = args.client
    quarter_str  = args.quarter

    # 四半期パース
    try:
        year, q_num = parse_quarter(quarter_str)
    except ValueError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)

    months = quarter_months(year, q_num)
    print(f"[INFO] 四半期: {quarter_str}（{', '.join(months)}）", file=sys.stderr)
    print(f"[INFO] クライアント: {client_id}", file=sys.stderr)

    # 当四半期データ読み込み
    monthly_data = []
    for m in months:
        d = load_json_safe(client_id, m)
        if d is not None:
            monthly_data.append(d)
        else:
            print(f"[WARN] {client_id}_{m}.json が見つかりません（スキップ）", file=sys.stderr)

    if not monthly_data:
        print(f"[ERROR] {quarter_str} のデータが 1 件も見つかりません。終了します。", file=sys.stderr)
        sys.exit(1)

    months_count = len(monthly_data)
    if months_count < 3:
        print(
            f"[WARNING] データが {months_count} ヶ月分のみです（3 ヶ月未満）。"
            f"判定結果はレポートに警告として記載されます。",
            file=sys.stderr
        )

    # 当四半期集計
    summary = build_quarterly_summary(monthly_data)
    gravity_type = summary["gravity_type"]
    print(f"[INFO] 判定結果: {gravity_type}", file=sys.stderr)

    # 前四半期データ読み込み（比較用）
    prev_y, prev_q = prev_quarter(year, q_num)
    prev_quarter_str = f"{prev_y}-Q{prev_q}"
    prev_months = quarter_months(prev_y, prev_q)
    prev_data = []
    for m in prev_months:
        d = load_json_safe(client_id, m)
        if d is not None:
            prev_data.append(d)
    prev_summary = build_quarterly_summary(prev_data) if prev_data else None
    if prev_summary:
        print(f"[INFO] 前四半期 ({prev_quarter_str}) データ {len(prev_data)} ヶ月分を読み込みました。", file=sys.stderr)
    else:
        print(f"[INFO] 前四半期 ({prev_quarter_str}) データなし（比較は省略）。", file=sys.stderr)

    now_jst = datetime.now(JST).strftime("%Y-%m-%d %H:%M JST")

    # レポート生成
    report_parts = [
        build_page1(client_id, quarter_str, summary, months_count, now_jst),
        build_page2(summary, prev_summary, quarter_str, prev_quarter_str),
        build_page3(summary, monthly_data[0] if monthly_data else None, quarter_str),
        build_page4(summary, quarter_str),
        build_page5(client_id, quarter_str, gravity_type),
    ]
    full_report = "\n".join(report_parts)
    print(full_report)

    # ファイル保存
    os.makedirs(REPORT_DIR, exist_ok=True)
    safe_quarter = quarter_str.replace("-", "_")
    out_path = os.path.join(REPORT_DIR, f"{client_id}_{safe_quarter}.md")
    try:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(full_report)
        size_kb = os.path.getsize(out_path) // 1024
        print(f"[OK]  四半期レポート出力完了: {out_path} ({size_kb} KB)", file=sys.stderr)
    except OSError as e:
        print(f"[WARN] ファイル保存に失敗しました: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
