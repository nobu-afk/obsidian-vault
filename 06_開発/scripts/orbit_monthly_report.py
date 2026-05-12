"""
Orbit 月次引力レポート 自動生成スクリプト（Phase 0 骨格）

Orbit v3.0 単一プラン（月15万）の3点セット納品物のうち
「② 月次引力レポート A4 3p」を自動生成するベーススクリプト。

使い方:
  python3 orbit_monthly_report.py --client <CLIENT_ID> --month YYYY-MM

例:
  python3 orbit_monthly_report.py --client sample_orbit_client --month 2026-05

入力:
  06_開発/scripts/orbit_data/<CLIENT_ID>_<YYYY-MM>.json
  （当月・前月の2ファイルを読み込む。前月ファイルは gravity_scores.previous からも取得可）

出力:
  - stdout: Markdown形式レポート（p.1 スコア表 / p.2 改善提案 / p.3 離職予兆）
  - orbit_reports/<CLIENT_ID>_<YYYY-MM>.png: 引力8項目グループ棒グラフ（要matplotlib）

引力8項目 SSOT: 05_プロダクト/_共通/SSOT_用語と定義.md §13.1（v0.4・7→8項目化済）

NOTE: matplotlibがない場合、PNGはスキップしてテキストレポートのみ出力する。
      pip install matplotlib でインストール可能。
"""

import os
import sys
import json
import argparse
from datetime import datetime, timezone, timedelta


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

# ============================================================
# 定数・マッピング
# ============================================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "orbit_data")
REPORT_DIR = os.path.join(SCRIPT_DIR, "orbit_reports")

JST = timezone(timedelta(hours=9))

# スコア記号 → 数値変換
SCORE_MAP = {"◎": 4, "○": 3, "△": 2, "×": 1}
# 数値 → 記号
SCORE_LABEL = {4: "◎", 3: "○", 2: "△", 1: "×"}
# 数値 → 日本語評価
SCORE_TEXT = {4: "良好", 3: "概ね良好", 2: "要改善", 1: "要緊急対応"}

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
    {"key": "physical",      "label": "身体シグナル",   "desc": "遅刻・欠勤・体調不良の頻度変化"},
    {"key": "facial",        "label": "表情シグナル",   "desc": "会議・1on1 での表情・発話量変化"},
    {"key": "overload",      "label": "過負荷シグナル", "desc": "残業・週末対応・タスク滞留"},
    {"key": "meaning",       "label": "意味付けシグナル","desc": "仕事への意義言語化・質問の変化"},
    {"key": "relationships", "label": "人間関係シグナル","desc": "チーム間コミュニケーション密度変化"},
]

# 優先度ラベル
PRIORITY_LABEL = {"high": "高", "medium": "中", "low": "低"}

# カラー設定（グラフ用）
COLOR_CURRENT  = "#2563EB"  # 青（今月）
COLOR_PREVIOUS = "#93C5FD"  # 薄青（先月）
COLOR_AXIS_R   = "#DBEAFE"  # 集まる軸ハイライト（薄青）
COLOR_AXIS_C   = "#EDE9FE"  # 躍動軸ハイライト（薄紫）

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
        if val not in SCORE_MAP:
            raise ValueError(
                f"gravity_scores.current.{k} の値 '{val}' が不正です。"
                f"◎/○/△/× のいずれかを指定してください"
            )

    if "departure_signals" in data:
        for item in DEPARTURE_ITEMS:
            k = item["key"]
            if k not in data["departure_signals"]:
                raise ValueError(f"departure_signals.{k} が存在しません")


def score_to_num(symbol: str) -> int:
    """◎/○/△/× → 1-4 の数値に変換。不正値は 0"""
    return SCORE_MAP.get(symbol, 0)


# ============================================================
# レポート生成: p.1 スコア表（Markdown）
# ============================================================

def build_page1(data: dict) -> str:
    """p.1: 引力8項目スコア表（今月 / 先月比）"""
    gs = data["gravity_scores"]
    current  = gs.get("current", {})
    previous = gs.get("previous", {})

    month = data.get("month", "")
    client_id = data.get("client_id", "")
    now_jst = datetime.now(JST).strftime("%Y-%m-%d %H:%M JST")

    lines = []
    lines.append(f"# Gravity Orbit 月次引力レポート")
    lines.append(f"")
    lines.append(f"**クライアント:** {client_id}  ")
    lines.append(f"**対象月:** {month}  ")
    lines.append(f"**生成日時:** {now_jst}")
    lines.append(f"")
    lines.append(f"---")
    lines.append(f"")
    lines.append(f"## p.1 引力 8 項目スコア（今月 vs 先月）")
    lines.append(f"")

    # 集まる軸 / 躍動軸 に分けて表示
    for axis_name in ["集まる", "躍動"]:
        items_in_axis = [it for it in GRAVITY_ITEMS if it["axis"] == axis_name]
        axis_emoji = "R" if axis_name == "集まる" else "C"
        lines.append(f"### [{axis_emoji}] {axis_name}軸")
        lines.append(f"")
        lines.append(f"| 項目 | 今月 ({month}) | 先月 | 変化 |")
        lines.append(f"|---|:-:|:-:|:-:|")

        for item in items_in_axis:
            k = item["key"]
            cur_sym  = current.get(k, "?")
            prev_sym = previous.get(k, "-")
            cur_num  = score_to_num(cur_sym)
            prev_num = score_to_num(prev_sym)

            if prev_sym == "-" or prev_num == 0:
                delta_str = "（初月）"
            else:
                diff = cur_num - prev_num
                if diff > 0:
                    delta_str = f"▲ +{diff}"
                elif diff < 0:
                    delta_str = f"▼ {diff}"
                else:
                    delta_str = "→ 変化なし"

            lines.append(f"| {item['label']} | **{cur_sym}** {SCORE_TEXT.get(cur_num, '')} | {prev_sym} | {delta_str} |")

        lines.append(f"")

    # 総合サマリー
    cur_nums  = [score_to_num(current.get(it["key"], "?")) for it in GRAVITY_ITEMS]
    prev_nums = [score_to_num(previous.get(it["key"], "-")) for it in GRAVITY_ITEMS]
    valid_cur  = [n for n in cur_nums  if n > 0]
    valid_prev = [n for n in prev_nums if n > 0]

    avg_cur  = sum(valid_cur)  / len(valid_cur)  if valid_cur  else 0
    avg_prev = sum(valid_prev) / len(valid_prev) if valid_prev else 0

    lines.append(f"### 総合引力スコア")
    lines.append(f"")
    lines.append(f"| | 今月 | 先月 | 差分 |")
    lines.append(f"|---|:-:|:-:|:-:|")
    prev_avg_str = f"{avg_prev:.2f}" if avg_prev > 0 else "-"
    diff_avg     = avg_cur - avg_prev if avg_prev > 0 else 0
    diff_avg_str = f"+{diff_avg:.2f}" if diff_avg > 0 else (f"{diff_avg:.2f}" if diff_avg < 0 else "±0")
    lines.append(f"| 平均スコア（1-4） | **{avg_cur:.2f}** | {prev_avg_str} | {diff_avg_str} |")
    lines.append(f"")
    lines.append(f"> スコア基準: ◎=4（良好）/ ○=3（概ね良好）/ △=2（要改善）/ ×=1（要緊急対応）")
    lines.append(f"")

    return "\n".join(lines)


# ============================================================
# レポート生成: p.2 改善提案（Markdown）
# ============================================================

def build_page2(data: dict) -> str:
    """p.2: α/β/γ/δ マッピング由来の改善提案"""
    actions = data.get("alpha_beta_gamma_delta_actions", [])
    month = data.get("month", "")

    lines = []
    lines.append(f"---")
    lines.append(f"")
    lines.append(f"## p.2 改善提案（α/β/γ/δ マッピング）")
    lines.append(f"")
    lines.append(f"**対象月:** {month}")
    lines.append(f"")

    if not actions:
        lines.append(f"> 改善提案データがありません（alpha_beta_gamma_delta_actions が空）")
        lines.append(f"")
        return "\n".join(lines)

    # 優先度順にソート（high → medium → low）
    priority_order = {"high": 0, "medium": 1, "low": 2}
    sorted_actions = sorted(actions, key=lambda x: priority_order.get(x.get("priority", "low"), 2))

    lines.append(f"| # | 軸 | 優先度 | 改善提案 |")
    lines.append(f"|:-:|:-:|:-:|---|")
    for i, act in enumerate(sorted_actions, 1):
        axis     = act.get("axis", "-")
        action   = act.get("action", "")
        priority = act.get("priority", "low")
        pri_label = PRIORITY_LABEL.get(priority, priority)
        pri_icon  = "🔴" if priority == "high" else ("🟡" if priority == "medium" else "🟢")
        lines.append(f"| {i} | `{axis}` | {pri_icon} {pri_label} | {action} |")

    lines.append(f"")
    lines.append(f"")
    lines.append(f"### 軸凡例")
    lines.append(f"")
    lines.append(f"| 軸コード | 意味 |")
    lines.append(f"|---|---|")
    lines.append(f"| R-α | 集まる軸 × 最優先介入（採用設計・メッセージ）|")
    lines.append(f"| R-β | 集まる軸 × 中期施策（プロセス改善）|")
    lines.append(f"| R-γ | 集まる軸 × 補強施策（データ整備・計測）|")
    lines.append(f"| R-δ | 集まる軸 × 維持施策（習慣化・モニタリング）|")
    lines.append(f"| C-α | 躍動軸 × 最優先介入（エンゲージメント・1on1）|")
    lines.append(f"| C-β | 躍動軸 × 中期施策（文化・対話設計）|")
    lines.append(f"| C-γ | 躍動軸 × 補強施策（サーベイ・KPI 整備）|")
    lines.append(f"| C-δ | 躍動軸 × 維持施策（習慣化・モニタリング）|")
    lines.append(f"")
    lines.append(f"> Phase 0: 改善提案は入力 JSON をそのまま貼り付け。")
    lines.append(f"> Phase 1 以降: スコアパターン → 提案テンプレートの自動マッピングを実装予定。")
    lines.append(f"")

    return "\n".join(lines)


# ============================================================
# レポート生成: p.3 離職予兆 5 シグナル（Markdown）
# ============================================================

def build_page3(data: dict) -> str:
    """p.3: 離職予兆 5 シグナル早期警戒スコア"""
    signals = data.get("departure_signals", {})
    month = data.get("month", "")

    lines = []
    lines.append(f"---")
    lines.append(f"")
    lines.append(f"## p.3 離職予兆 5 シグナル 早期警戒スコア")
    lines.append(f"")
    lines.append(f"**対象月:** {month}")
    lines.append(f"")

    if not signals:
        lines.append(f"> 離職予兆データがありません（departure_signals が空）")
        lines.append(f"")
        return "\n".join(lines)

    # シグナルスコア表
    lines.append(f"| シグナル | 観察ポイント | スコア | 評価 |")
    lines.append(f"|---|---|:-:|---|")

    alert_count = 0
    for item in DEPARTURE_ITEMS:
        k        = item["key"]
        sym      = signals.get(k, "?")
        num      = score_to_num(sym)
        eval_txt = SCORE_TEXT.get(num, "?")
        if num <= 2:
            alert_count += 1
        lines.append(f"| **{item['label']}** | {item['desc']} | {sym} | {eval_txt} |")

    lines.append(f"")

    # 警戒レベル判定
    if alert_count == 0:
        alert_level = "GREEN（警戒なし）"
        alert_comment = "全シグナル良好。現状維持と月次モニタリングを継続。"
    elif alert_count <= 2:
        alert_level = "YELLOW（要注意）"
        alert_comment = f"{alert_count} 項目が要改善水準。次回セッションで重点ヒアリングを実施。"
    else:
        alert_level = "RED（要緊急対応）"
        alert_comment = f"{alert_count} 項目が要改善水準。緊急 1on1 の設定と対象者の個別フォロープランを立案。"

    lines.append(f"### 総合警戒レベル: {alert_level}")
    lines.append(f"")
    lines.append(f"{alert_comment}")
    lines.append(f"")
    lines.append(f"")
    lines.append(f"### 心理的安全性 4 行動チェック（Edmondson 1999 準拠）")
    lines.append(f"")
    lines.append(f"月次セッションで以下 4 行動の観察・記録を実施：")
    lines.append(f"")
    lines.append(f"| # | 行動 | 今月の観察 |")
    lines.append(f"|:-:|---|---|")
    lines.append(f"| 1 | 失敗を認める発言 | （セッション記録に記入）|")
    lines.append(f"| 2 | 異議申し立て | （セッション記録に記入）|")
    lines.append(f"| 3 | 無知の表明 | （セッション記録に記入）|")
    lines.append(f"| 4 | 助けを求める | （セッション記録に記入）|")
    lines.append(f"")
    lines.append(f"---")
    lines.append(f"")
    lines.append(f"*本レポートは Gravity Orbit 月次引力レポート（A4 3p）の自動生成物です。*  ")
    lines.append(f"*次月の Quarterly 4型再判定書は別途 `orbit_quarterly_review.py`（Phase 1 実装予定）で生成します。*")
    lines.append(f"")

    return "\n".join(lines)


# ============================================================
# グラフ生成（matplotlib）
# ============================================================

def build_chart(data: dict, output_path: str) -> bool:
    """引力8項目グループ棒グラフ（今月 vs 先月）を PNG に保存。成功時 True を返す。"""
    loaded = _load_matplotlib()
    if loaded is None:
        print("[INFO] matplotlib が見つかりません。PNG 出力をスキップします。", file=sys.stderr)
        print("[INFO] インストール: pip install matplotlib", file=sys.stderr)
        return False
    plt, mpatches, fm = loaded

    gs = data["gravity_scores"]
    current  = gs.get("current", {})
    previous = gs.get("previous", {})
    month    = data.get("month", "")

    labels     = [it["label"] for it in GRAVITY_ITEMS]
    axis_types = [it["axis"] for it in GRAVITY_ITEMS]
    cur_vals   = [score_to_num(current.get(it["key"], "×"))  for it in GRAVITY_ITEMS]
    prev_vals  = [score_to_num(previous.get(it["key"], "×")) for it in GRAVITY_ITEMS]

    n = len(labels)
    x = list(range(n))
    bar_w = 0.35

    # フォント設定（日本語対応）
    # macOS 標準の Hiragino Sans を優先、なければシステムデフォルト
    jp_fonts = ["Hiragino Sans", "Hiragino Kaku Gothic Pro", "Yu Gothic", "MS Gothic", "DejaVu Sans"]
    available = {f.name for f in fm.fontManager.ttflist}
    chosen_font = next((f for f in jp_fonts if f in available), None)
    if chosen_font:
        plt.rcParams["font.family"] = chosen_font
    plt.rcParams["axes.unicode_minus"] = False

    fig, ax = plt.subplots(figsize=(12, 6))
    fig.patch.set_facecolor("#FAFAFA")
    ax.set_facecolor("#FAFAFA")

    # 軸ハイライト（集まる / 躍動の背景色分け）
    for i, axis in enumerate(axis_types):
        color = COLOR_AXIS_R if axis == "集まる" else COLOR_AXIS_C
        ax.axvspan(i - 0.5, i + 0.5, color=color, alpha=0.25, zorder=0)

    # 棒グラフ描画
    bars_cur  = ax.bar([xi - bar_w / 2 for xi in x], cur_vals,  bar_w,
                       label=f"今月 ({month})", color=COLOR_CURRENT,  zorder=3)
    bars_prev = ax.bar([xi + bar_w / 2 for xi in x], prev_vals, bar_w,
                       label="先月",            color=COLOR_PREVIOUS, zorder=3)

    # 値ラベル（棒の上に記号表示）
    for bar, num in zip(bars_cur, cur_vals):
        sym = SCORE_LABEL.get(num, "?")
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05,
                sym, ha="center", va="bottom", fontsize=11, fontweight="bold",
                color=COLOR_CURRENT)
    for bar, num in zip(bars_prev, prev_vals):
        sym = SCORE_LABEL.get(num, "?")
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05,
                sym, ha="center", va="bottom", fontsize=10,
                color="#4B5563")

    # 軸設定
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=20, ha="right", fontsize=9)
    ax.set_yticks([1, 2, 3, 4])
    ax.set_yticklabels(["×(1)", "△(2)", "○(3)", "◎(4)"], fontsize=10)
    ax.set_ylim(0, 5)
    ax.set_ylabel("スコア", fontsize=11)
    ax.set_title(f"引力 8 項目スコア — {month}", fontsize=14, fontweight="bold", pad=12)

    # 凡例
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
# メイン処理
# ============================================================

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Orbit 月次引力レポート 自動生成（Phase 0）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python3 orbit_monthly_report.py --client sample_orbit_client --month 2026-05

入力ファイル:
  orbit_data/<CLIENT_ID>_<YYYY-MM>.json

出力:
  - stdout: Markdown 形式レポート（p.1 / p.2 / p.3）
  - orbit_reports/<CLIENT_ID>_<YYYY-MM>.png: 棒グラフ（要 matplotlib）
        """,
    )
    parser.add_argument("--client", required=True,  help="クライアントID（例: sample_orbit_client）")
    parser.add_argument("--month",  required=True,  help="対象月 YYYY-MM（例: 2026-05）")
    parser.add_argument("--no-chart", action="store_true", help="PNG グラフ出力をスキップ")
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

    # レポート生成（Markdown 3p）
    report_parts = [
        build_page1(data),
        build_page2(data),
        build_page3(data),
    ]
    full_report = "\n".join(report_parts)
    print(full_report)

    # グラフ生成
    if not args.no_chart:
        chart_path = os.path.join(REPORT_DIR, f"{client_id}_{month}.png")
        print(f"[INFO] PNG 生成: {chart_path}", file=sys.stderr)
        try:
            if build_chart(data, chart_path):
                size_kb = os.path.getsize(chart_path) // 1024
                print(f"[OK]  PNG 出力完了: {chart_path} ({size_kb} KB)", file=sys.stderr)
        except (ValueError, OSError, RuntimeError) as e:
            print(f"[WARN] PNG 生成中にエラーが発生しました: {e}", file=sys.stderr)
    else:
        print("[INFO] --no-chart 指定につき PNG 出力をスキップ", file=sys.stderr)


if __name__ == "__main__":
    main()
