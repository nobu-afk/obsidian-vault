"""
Orbit 論文 × AI 突合分析エンジン（OT-2・v1.0・260514）

OT-1 出力の Orbit 標準 JSON と論文ライブラリ JSON を突合し、
「離職予兆シグナル → 該当論文 → 推奨施策 3-5 件」のマッピング JSON を生成する。

Claude API（claude-sonnet-4-6）で施策を生成。prompt caching（ephemeral）で
system prompt + 論文ライブラリをキャッシュし API コストを削減。

v1.0 スコープ:
  - 論文ライブラリ JSON: 同梱簡易 DB（Gravity 引力経営 20 本）を使用
  - Claude API 呼び出し: config/config_claude.json の api_key を使用
  - --dry-run フラグ: Claude API を呼ばずにモック結果を出力
  - --demo フラグ: orbit_data/sample_orbit_client_2026-05.json を入力として実行

使い方:
  python3 orbit_paper_matcher.py --client sample_orbit_client --month 2026-05
  python3 orbit_paper_matcher.py --client sample_orbit_client --month 2026-05 --dry-run
  python3 orbit_paper_matcher.py --demo --dry-run

入力:
  orbit_data/<CLIENT_ID>_<YYYY-MM>.json（OT-1 出力 or 既存 orbit_data）
  orbit_data/orbit_papers_db.json（論文ライブラリ・同梱 or 指定）

出力:
  orbit_data/<CLIENT_ID>_<YYYY-MM>_matched.json（施策マッピング JSON）
  stdout: 生成された施策 JSON の要約

論文ライブラリ SSOT: 04_GrowthFix/02_マーケティング/260509_Gravity_論文引用ライブラリ_v2.0.md
Claude API モデル: claude-sonnet-4-6（prompt caching 有効）
"""

import os
import sys
import json
import argparse
from datetime import datetime
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _common.claude_client import (  # noqa: E402
    parse_claude_json, JST, MODEL as CLAUDE_MODEL, CONFIG_PATH,
)

SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
DATA_DIR    = os.path.join(SCRIPT_DIR, "orbit_data")
PAPERS_DB_PATH = os.path.join(DATA_DIR, "orbit_papers_db.json")

EMBEDDED_PAPERS_DB = {
    "version": "1.0",
    "generated": "260514",
    "papers": [
        {
            "id": "Saks2006",
            "author": "Saks AM",
            "year": 2006,
            "title": "Antecedents and Consequences of Employee Engagement",
            "journal": "Journal of Managerial Psychology",
            "citations": 4800,
            "axes": ["躍動"],
            "signals": ["engagement", "departure_signal"],
            "summary": "エンゲージメントの2軸（職務・組織）を測定。低エンゲージメントは離職意図と強く相関（β=-.40）。",
            "intervention": "職務エンゲージメント向上: 意義ある業務割当 + 1on1 月2回以上",
        },
        {
            "id": "Mitchell2001",
            "author": "Mitchell TR et al.",
            "year": 2001,
            "title": "Why People Stay: Using Job Embeddedness to Predict Voluntary Turnover",
            "journal": "Academy of Management Journal",
            "citations": 3200,
            "axes": ["留まる"],
            "signals": ["departure_signal", "talent_retention"],
            "summary": "Job Embeddedness 3次元（Links / Fit / Sacrifice）が自発的離職を予測。Fit が最強予測因子。",
            "intervention": "Embedded Self 診断: Links(つながり) / Fit(適合) / Sacrifice(代償) の月次測定と介入",
        },
        {
            "id": "Rousseau1989",
            "author": "Rousseau DM",
            "year": 1989,
            "title": "Psychological and Implied Contracts in Organizations",
            "journal": "Employee Responsibilities and Rights Journal",
            "citations": 4100,
            "axes": ["留まる"],
            "signals": ["meaning", "relationships"],
            "summary": "心理的契約の違反・破綻が組織コミットメントと満足度を急落させる。3段階: 認識→違反→破綻。",
            "intervention": "月次心理的契約チェック: 「約束された期待」vs「実際の提供」のギャップ測定",
        },
        {
            "id": "MeyerAllen1991",
            "author": "Meyer JP, Allen NJ",
            "year": 1991,
            "title": "A Three-Component Conceptualization of Organizational Commitment",
            "journal": "Human Resource Management Review",
            "citations": 8900,
            "axes": ["留まる"],
            "signals": ["talent_retention", "engagement"],
            "summary": "情動的(AC)・継続的(CC)・規範的(NC)コミットメントの3成分モデル。AC が最も強く業績・定着に相関。",
            "intervention": "情動的コミットメント強化: Why 共有セッション月1回 + キャリア対話",
        },
        {
            "id": "Edmondson1999",
            "author": "Edmondson AC",
            "year": 1999,
            "title": "Psychological Safety and Learning Behavior in Work Teams",
            "journal": "Administrative Science Quarterly",
            "citations": 7200,
            "axes": ["躍動"],
            "signals": ["psych_safety_cost", "executive_voice", "facial"],
            "summary": "心理的安全性が学習行動・チームパフォーマンスを促進。リーダーの行動が最大の規定因子。",
            "intervention": "リーダー4行動: 失敗の承認 / 異議歓迎 / 質問奨励 / 助けを求める文化",
        },
        {
            "id": "Schneider1987",
            "author": "Schneider B",
            "year": 1987,
            "title": "The People Make the Place",
            "journal": "Personnel Psychology",
            "citations": 3800,
            "axes": ["集まる"],
            "signals": ["recruitment_pipeline", "recruitment_wall_pof"],
            "summary": "ASA（誘引-選抜-離脱）モデル: 組織は特定のPersonalityタイプを引き寄せ・選択・保持する。",
            "intervention": "採用 JD に Why × 才能 × 偏愛を記述 → P-O Fit 向上 → 辞退率低下",
        },
        {
            "id": "Crossley2007",
            "author": "Crossley CD et al.",
            "year": 2007,
            "title": "Development of a Global Measure of Job Embeddedness",
            "journal": "Journal of Applied Psychology",
            "citations": 1800,
            "axes": ["留まる"],
            "signals": ["talent_retention", "departure_signal"],
            "summary": "Job Embeddedness のグローバル単一尺度を開発。6項目逆転あり（Crossley順転誤訳注意）。",
            "intervention": "JE 簡易6問サーベイ月次実施 → 低スコア者への個別介入フラグ設定",
        },
        {
            "id": "Bandura1977",
            "author": "Bandura A",
            "year": 1977,
            "title": "Self-efficacy: Toward a Unifying Theory of Behavioral Change",
            "journal": "Psychological Review",
            "citations": 24000,
            "axes": ["躍動"],
            "signals": ["executive_voice", "engagement"],
            "summary": "自己効力感の4源泉: 達成経験 / 代理経験 / 言語的説得 / 生理的覚醒。達成経験が最強。",
            "intervention": "幹部の小さな成功体験を月次で記録・言語化 → 次の挑戦への自己効力感向上",
        },
        {
            "id": "Wrzesniewski1997",
            "author": "Wrzesniewski A et al.",
            "year": 1997,
            "title": "Jobs, Careers, and Callings: People's Relations to Their Work",
            "journal": "Journal of Research in Personality",
            "citations": 2900,
            "axes": ["躍動"],
            "signals": ["meaning", "engagement"],
            "summary": "仕事への関わり方3類型: Job / Career / Calling。Calling は最高の主観的幸福・組織コミットと相関。",
            "intervention": "1on1 で Calling 発見セッション: 「なぜこの仕事を選んだか」の物語化",
        },
        {
            "id": "Tomprou2015",
            "author": "Tomprou M et al.",
            "year": 2015,
            "title": "The Psychological Contracts of Violation Victims",
            "journal": "Journal of Organizational Behavior",
            "citations": 420,
            "axes": ["留まる"],
            "signals": ["meaning", "relationships", "facial"],
            "summary": "心理的契約違反後の4段階回復モデル: 沈黙 → 発言 → 離脱 → 適応。初期介入が重要。",
            "intervention": "違反発覚後72h以内の対話設定 → 修復合意書（書面不要・口頭でも有効）",
        },
        {
            "id": "VallerAndHoulgaard2003",
            "author": "Vallerand RJ et al.",
            "year": 2003,
            "title": "Les passions de l'ame: On Obsessive and Harmonious Passion",
            "journal": "Journal of Personality and Social Psychology",
            "citations": 3600,
            "axes": ["躍動"],
            "signals": ["engagement", "overload"],
            "summary": "調和的情熱(HP)は燃え尽きを防ぎ持続的エンゲージメントを生む。強迫的情熱(OP)は過負荷リスク。",
            "intervention": "過負荷者への調和的情熱チェック: 「やめられる感覚があるか」を確認",
        },
        {
            "id": "Sampson1997",
            "author": "Sampson RJ et al.",
            "year": 1997,
            "title": "Neighborhoods and Violent Crime: A Multilevel Study of Collective Efficacy",
            "journal": "Science",
            "citations": 8583,
            "axes": ["躍動"],
            "signals": ["executive_voice", "psych_safety_cost"],
            "summary": "集合的効力感(CE)がコミュニティの問題解決力を予測。CE は組織にも適用可。",
            "intervention": "チーム CE 向上: 集団的目標設定 + 相互モニタリング文化の醸成",
        },
        {
            "id": "Saks2006b",
            "author": "Saks AM",
            "year": 2006,
            "title": "Antecedents and Consequences of Employee Engagement (Organizational Embeddedness)",
            "journal": "Journal of Managerial Psychology",
            "citations": 4800,
            "axes": ["留まる"],
            "signals": ["departure_signal", "overload"],
            "summary": "組織エンゲージメントと離職意図の相関（r=-.46）。支援的環境が最大の促進因子。",
            "intervention": "直属上長の支援行動チェック月次実施 → 「助けてもらえた体験」の記録",
        },
        {
            "id": "MeyerMeta2002",
            "author": "Meyer JP et al.",
            "year": 2002,
            "title": "Affective, Continuance, and Normative Commitment: A Meta-Analysis",
            "journal": "Journal of Vocational Behavior",
            "citations": 6300,
            "axes": ["留まる"],
            "signals": ["talent_retention", "departure_signal"],
            "summary": "AC は業績・離職両方を予測。CC は業績を予測しない（単なる「辞められない」はリスク）。",
            "intervention": "CC 偏重チェック: 「辞めたいが辞められない」層の特定 → AC 向上施策へ転換",
        },
        {
            "id": "CableJudge1996",
            "author": "Cable DM, Judge TA",
            "year": 1996,
            "title": "Person-Organization Fit, Job Choice Decisions, and Organizational Entry",
            "journal": "Organizational Behavior and Human Decision Processes",
            "citations": 2400,
            "axes": ["集まる"],
            "signals": ["recruitment_pipeline", "final_decline_rate"],
            "summary": "P-O Fit が内定受諾意図を最も強く予測（β=.42）。価値観の合致が報酬より重要。",
            "intervention": "採用選考に P-O Fit 問答（Why × 組織文化）を明示的に組み込む",
        },
    ]
}


def load_orbit_json(client_id: str, month: str) -> dict:
    """orbit_data/<CLIENT_ID>_<YYYY-MM>.json を読み込む"""
    filepath = os.path.join(DATA_DIR, f"{client_id}_{month}.json")
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"データファイルが見つかりません: {filepath}") from e


def load_papers_db(papers_db_path: Optional[str] = None) -> dict:
    """論文ライブラリ JSON を読み込む。ファイルがない場合は埋め込み DB を使用。"""
    path = papers_db_path or PAPERS_DB_PATH
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                db = json.load(f)
                print(f"[INFO] 論文ライブラリ読み込み: {path}（{len(db.get('papers', []))} 本）",
                      file=sys.stderr)
                return db
        except json.JSONDecodeError as e:
            print(f"[WARN] 論文ライブラリ JSON エラー: {e} → 埋め込み DB を使用", file=sys.stderr)
    print(f"[INFO] 論文ライブラリ未検出 → 埋め込み DB を使用（{len(EMBEDDED_PAPERS_DB['papers'])} 本）",
          file=sys.stderr)
    return EMBEDDED_PAPERS_DB


def _match_papers_to_signals(orbit_data: dict, papers: list[dict]) -> list[dict]:
    """離職予兆シグナルと引力スコアを基に関連論文を突合"""
    gravity_current    = orbit_data.get("gravity_scores", {}).get("current", {})
    departure_signals  = orbit_data.get("departure_signals", {})

    weak_keys = set()
    for k, v in gravity_current.items():
        if v in ("△", "×"):
            weak_keys.add(k)
    for k, v in departure_signals.items():
        if v in ("△", "×"):
            weak_keys.add(k)

    matched = []
    for paper in papers:
        paper_signals = set(paper.get("signals", []))
        overlap = weak_keys & paper_signals
        if overlap:
            matched.append({
                "paper_id":     paper["id"],
                "author":       paper["author"],
                "year":         paper["year"],
                "title":        paper["title"],
                "axes":         paper.get("axes", []),
                "matched_signals": list(overlap),
                "summary":      paper.get("summary", ""),
                "intervention": paper.get("intervention", ""),
                "citations":    paper.get("citations", 0),
            })

    matched.sort(key=lambda x: x["citations"], reverse=True)
    return matched[:8]


def _build_prompt(orbit_data: dict, matched_papers: list[dict]) -> tuple[str, str]:
    """Claude API 用の system prompt と user message を構築"""
    client_id = orbit_data.get("client_id", "")
    month     = orbit_data.get("month", "")
    gravity   = orbit_data.get("gravity_scores", {}).get("current", {})
    signals   = orbit_data.get("departure_signals", {})

    papers_json = json.dumps(matched_papers, ensure_ascii=False, indent=2)

    system_prompt = f"""あなたは Gravity Orbit の人事施策 AI アナリストです。
以下のルールに従って「来月の優先施策 3-5 件」を JSON 形式で生成してください。

## 出力ルール
1. JSON のみ出力（説明文不要）
2. フォーマット: {{"signals": [{{"type": "string", "papers": ["paper_id"], "priority": "high/medium/low", "actions": ["string", ...], "rationale": "string"}}]}}
3. 施策は「経営者・CHRO が来月すぐ実行できる具体的アクション」で記述
4. 引力経営思想（集まる × 躍動する × 留まる の3軸）と整合させること
5. 論文根拠を必ず papers フィールドに含める
6. priority: high（今月中に着手）/ medium（来月着手）/ low（翌月以降）

## 引力経営コンテキスト
- 集まる軸 = 採用引力（Schneider ASA / P-O Fit）
- 躍動軸 = エンゲージメント・パフォーマンス（Saks / Edmondson / Bandura）
- 留まる軸 = 継続引力（Mitchell JE / Rousseau 心理的契約 / Meyer-Allen コミットメント）

## 論文ライブラリ（突合済み・高被引用順）
{papers_json}"""

    weak_gravity  = {k: v for k, v in gravity.items()  if v in ("△", "×")}
    weak_signals  = {k: v for k, v in signals.items()   if v in ("△", "×")}

    user_message = f"""クライアント: {client_id} / 対象月: {month}

## 当月の弱点スコア（引力8項目）
{json.dumps(weak_gravity, ensure_ascii=False, indent=2)}

## 当月の離職予兆シグナル（要注意項目）
{json.dumps(weak_signals, ensure_ascii=False, indent=2)}

上記データと論文ライブラリを突合し、来月の優先施策 3-5 件を JSON で出力してください。"""

    return system_prompt, user_message


def call_claude_api(system_prompt: str, user_message: str, api_key: str) -> dict:
    """Claude API を呼び出し施策 JSON を取得（prompt caching 有効）"""
    try:
        import anthropic
    except ImportError:
        print("[ERROR] anthropic SDK がインストールされていません。pip install anthropic", file=sys.stderr)
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=2048,
        system=[
            {
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[
            {"role": "user", "content": user_message}
        ],
    )

    raw_text = response.content[0].text.strip()

    try:
        result = parse_claude_json(raw_text)
    except json.JSONDecodeError:
        result = {"raw_response": raw_text, "parse_error": "JSON parse failed"}

    usage = response.usage
    print(f"[INFO] Claude API 使用量: input={usage.input_tokens} / output={usage.output_tokens} tokens",
          file=sys.stderr)
    if hasattr(usage, "cache_read_input_tokens"):
        print(f"[INFO] prompt cache: read={usage.cache_read_input_tokens} / create={usage.cache_creation_input_tokens} tokens",
              file=sys.stderr)

    return result


def build_mock_result(orbit_data: dict, matched_papers: list[dict]) -> dict:
    """dry-run 時のモック施策結果を生成"""
    gravity  = orbit_data.get("gravity_scores", {}).get("current", {})
    signals  = orbit_data.get("departure_signals", {})

    mock_signals = []

    if gravity.get("engagement") in ("△", "×") or signals.get("meaning") in ("△", "×"):
        mock_signals.append({
            "type": "エンゲージメント低下 + 意味付けシグナル",
            "papers": ["Saks2006", "Wrzesniewski1997"],
            "priority": "high",
            "actions": [
                "1on1 を月2回から週1回に増加（Saks2006: エンゲージメント低下時の介入効果 β=.40）",
                "次回 1on1 で Calling 発見セッション: 「なぜこの仕事を選んだか」の物語化",
                "エンゲージメントサーベイ 5 問を月次導入し継続測定開始",
            ],
            "rationale": "Saks(2006)はエンゲージメント低下と離職意図の強相関を実証。Wrzesniewski(1997)のCalling転換が最も強力な介入。",
        })

    if gravity.get("departure_signal") in ("△", "×") or signals.get("physical") in ("△", "×"):
        mock_signals.append({
            "type": "離職予兆シグナル（身体 + 離脱予兆）",
            "papers": ["Mitchell2001", "Crossley2007"],
            "priority": "high",
            "actions": [
                "Job Embeddedness 6 問チェックを今月中に実施し、低スコア者 (Links/Fit/Sacrifice) を特定",
                "低スコア者に個別面談: 「辞めたいと感じたことがあるか」を明示的に確認",
                "Sacrifice 強化: キャリアパス言語化 + 月次フォローアップ面談設定",
            ],
            "rationale": "Mitchell(2001)はJob Embeddedness3次元が自発的離職を最も強く予測することを実証。早期特定が鍵。",
        })

    if gravity.get("psych_safety_cost") in ("△", "×") or signals.get("relationships") in ("△", "×"):
        mock_signals.append({
            "type": "心理的安全性低下",
            "papers": ["Edmondson1999"],
            "priority": "medium",
            "actions": [
                "リーダー 4 行動チェック: 失敗の承認 / 異議歓迎 / 質問奨励 / 助けを求める文化の月次観察",
                "経営者が「私も失敗した」発言を次回全社ミーティングで1回行う",
                "心理的安全性サーベイ 3 問を月次導入（Edmondson 1999 尺度準拠）",
            ],
            "rationale": "Edmondson(1999)はリーダー行動が心理的安全性の最大規定因子であることを実証。トップの行動変容が最速。",
        })

    if not mock_signals:
        mock_signals.append({
            "type": "維持施策（全体良好）",
            "papers": ["MeyerAllen1991"],
            "priority": "low",
            "actions": [
                "情動的コミットメント維持: Why 共有セッション月1回継続",
                "月次引力スコアの経営会議報告を継続",
                "来月の全体サーベイ実施計画を確認",
            ],
            "rationale": "Meyer-Allen(1991)のAC（情動的コミットメント）が業績・定着を最も強く予測。現状良好でも維持施策が重要。",
        })

    return {
        "signals": mock_signals,
        "_meta": {"dry_run": True, "model": CLAUDE_MODEL},
    }


def save_matched_json(data: dict, client_id: str, month: str) -> str:
    """施策マッピング JSON を orbit_data/<CLIENT_ID>_<YYYY-MM>_matched.json に保存"""
    os.makedirs(DATA_DIR, exist_ok=True)
    output_path = os.path.join(DATA_DIR, f"{client_id}_{month}_matched.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Orbit 論文 × AI 突合分析エンジン（OT-2）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python3 orbit_paper_matcher.py --client sample_orbit_client --month 2026-05
  python3 orbit_paper_matcher.py --client sample_orbit_client --month 2026-05 --dry-run
  python3 orbit_paper_matcher.py --demo --dry-run

出力:
  orbit_data/<CLIENT_ID>_<YYYY-MM>_matched.json
        """,
    )
    parser.add_argument("--client",  default="sample_orbit_client", help="クライアントID")
    parser.add_argument("--month",   help="対象月 YYYY-MM（例: 2026-05）")
    parser.add_argument("--papers-db", help="論文ライブラリ JSON パス（省略時は埋め込み DB）")
    parser.add_argument("--config",  default=CONFIG_PATH, help="Claude 設定 JSON パス")
    parser.add_argument("--dry-run", action="store_true", help="Claude API を呼ばずにモック結果を出力")
    parser.add_argument("--demo",    action="store_true",
                        help="sample_orbit_client_2026-05.json を入力として実行")
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

    api_key = None
    if not args.dry_run:
        try:
            with open(args.config, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                api_key = cfg.get("api_key")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"[WARN] Claude 設定読み込み失敗: {e}", file=sys.stderr)
            print("[INFO] --dry-run モードで続行します", file=sys.stderr)
            args.dry_run = True

    print(f"[INFO] データ読み込み: {args.client} / {args.month}", file=sys.stderr)
    try:
        orbit_data = load_orbit_json(args.client, args.month)
    except FileNotFoundError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)

    papers_db   = load_papers_db(args.papers_db)
    papers      = papers_db.get("papers", [])
    matched     = _match_papers_to_signals(orbit_data, papers)

    print(f"[INFO] 突合完了: {len(matched)} 本の論文がマッチ", file=sys.stderr)
    for p in matched:
        print(f"  - {p['paper_id']} ({p['author']}, {p['year']}) → {p['matched_signals']}", file=sys.stderr)

    if args.dry_run:
        print("[INFO] dry-run モード: Claude API をスキップ（モック結果を使用）", file=sys.stderr)
        result = build_mock_result(orbit_data, matched)
    else:
        system_prompt, user_message = _build_prompt(orbit_data, matched)
        print("[INFO] Claude API 呼び出し中...", file=sys.stderr)
        result = call_claude_api(system_prompt, user_message, api_key)

    now_jst = datetime.now(JST).strftime("%Y-%m-%d %H:%M JST")
    output = {
        "client_id":    args.client,
        "month":        args.month,
        "generated_at": now_jst,
        "papers_matched": len(matched),
        "dry_run":      args.dry_run,
        "matched_papers": matched,
        **result,
    }

    output_path = save_matched_json(output, args.client, args.month)
    size_kb = os.path.getsize(output_path) // 1024 or 1
    print(f"[OK] 出力完了: {output_path} ({size_kb} KB)", file=sys.stderr)

    signals = output.get("signals", [])
    print(f"\n--- 施策サマリー ({len(signals)} 件) ---")
    for i, sig in enumerate(signals, 1):
        print(f"\n[{i}] {sig.get('type', '')} (priority: {sig.get('priority', '')})")
        for act in sig.get("actions", []):
            print(f"  - {act}")
        papers_cited = sig.get("papers", [])
        if papers_cited:
            print(f"  根拠論文: {', '.join(papers_cited)}")


if __name__ == "__main__":
    main()
