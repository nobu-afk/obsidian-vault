"""
Orbit タレマネデータ取得・正規化エンジン（OT-1・v1.0・260514）

Wevox / カオナビ / SmartHR の API or CSV からタレマネデータを取得し、
Orbit 標準 JSON スキーマに正規化して orbit_data/<CLIENT_ID>_<YYYY-MM>.json に出力する。

v1.0 スコープ:
  - Wevox API（モック stub）
  - カオナビ API（モック stub）
  - SmartHR CSV（実装）
  - 汎用 CSV（--source csv）実装
  - 機密マスキング: 氏名 → SHA-256 ハッシュ前6桁 / メールアドレス → ドメインのみ
  - --demo フラグ: 同梱サンプル CSV から正規化 JSON 生成

使い方:
  python3 orbit_data_fetcher.py --source csv --client demo --month 2026-05
  python3 orbit_data_fetcher.py --source wevox --client demo --month 2026-05
  python3 orbit_data_fetcher.py --source kaonavi --client demo --month 2026-05
  python3 orbit_data_fetcher.py --source smarthr --client demo --month 2026-05
  python3 orbit_data_fetcher.py --demo --month 2026-05

入力:
  --source csv    : --input で CSV パスを指定（省略時は demo CSV を使用）
  --source wevox  : --config の api_key で Wevox API 呼び出し（MVP はモック）
  --source kaonavi: --config の api_key でカオナビ API 呼び出し（MVP はモック）
  --source smarthr: SmartHR CSV エクスポート形式（実装）
  --config        : 設定 JSON ファイルパス（デフォルト: config/config_orbit_sources.json）

出力:
  orbit_data/<CLIENT_ID>_<YYYY-MM>.json（Orbit 標準スキーマ準拠）

Orbit 標準スキーマ: orbit_data/SCHEMA.md
"""

import os
import sys
import csv
import json
import hashlib
import argparse
import io
from datetime import datetime, timezone, timedelta
from typing import Optional


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR   = os.path.join(SCRIPT_DIR, "orbit_data")
CONFIG_DIR = os.path.join(SCRIPT_DIR, "..", "config")

JST = timezone(timedelta(hours=9))

GRAVITY_SCORE_KEYS = [
    "recruitment_pipeline",
    "final_decline_rate",
    "talent_retention",
    "executive_voice",
    "engagement",
    "departure_signal",
    "recruitment_wall_pof",
    "psych_safety_cost",
]

DEPARTURE_SIGNAL_KEYS = [
    "physical",
    "facial",
    "overload",
    "meaning",
    "relationships",
]

VALID_SCORES = {"◎", "○", "△", "×"}

DEMO_CSV_CONTENT = """\
member_id,name,email,department,engagement_score,absence_days,overtime_hours,one_on_one_done,has_departure_risk
M001,山田太郎,yamada@example.com,営業部,3.2,1,12,true,false
M002,鈴木花子,suzuki@example.com,マーケティング,2.1,3,28,false,true
M003,田中次郎,tanaka@example.com,エンジニア,3.8,0,8,true,false
M004,佐藤美咲,sato@demo.co.jp,人事部,2.5,2,20,true,false
M005,伊藤健,ito@demo.co.jp,営業部,1.8,5,35,false,true
M006,渡辺裕子,watanabe@example.com,エンジニア,3.5,0,10,true,false
M007,高橋正彦,takahashi@example.com,営業部,2.8,1,15,false,false
M008,中村あき,nakamura@demo.co.jp,マーケティング,3.1,0,9,true,false
"""


def _mask_name(name: str, enabled: bool = True) -> str:
    """氏名を SHA-256 ハッシュ前 6 桁でマスキング（enabled=False で素通し）"""
    if not enabled:
        return name
    return "M-" + hashlib.sha256(name.encode("utf-8")).hexdigest()[:6]


def _mask_email(email: str, enabled: bool = True) -> str:
    """メールアドレスをドメインのみに変換（enabled=False で素通し）"""
    if not enabled:
        return email
    if "@" in email:
        return "@" + email.split("@", 1)[1]
    return "@unknown"


def _score_from_float(val: float, thresholds: tuple = (3.5, 2.5, 1.5)) -> str:
    """数値スコアを ◎/○/△/× に変換。thresholds = (◎閾値, ○閾値, △閾値)"""
    if val >= thresholds[0]:
        return "◎"
    elif val >= thresholds[1]:
        return "○"
    elif val >= thresholds[2]:
        return "△"
    else:
        return "×"


def _score_from_bool_inverted(val: bool) -> str:
    """リスクフラグ（true=悪）を ×/○ に変換"""
    return "×" if val else "○"


def _parse_csv_members(reader, mask: bool = True) -> list[dict]:
    """CSV リーダーからメンバーリストを解析・マスキングして返す（mask=False で素通し）"""
    members = []
    for row in reader:
        try:
            engagement = float(row.get("engagement_score", 0))
            absence    = int(row.get("absence_days", 0))
            overtime   = int(row.get("overtime_hours", 0))
            one_on_one = row.get("one_on_one_done", "false").strip().lower() == "true"
            departure  = row.get("has_departure_risk", "false").strip().lower() == "true"

            member = {
                "member_id":   _mask_name(row.get("name", row.get("member_id", "unknown")), mask),
                "email_domain": _mask_email(row.get("email", ""), mask),
                "department":  row.get("department", ""),
                "engagement_score": engagement,
                "absence_days":     absence,
                "overtime_hours":   overtime,
                "one_on_one_done":  one_on_one,
                "has_departure_risk": departure,
            }
            members.append(member)
        except (ValueError, KeyError) as e:
            print(f"[WARN] 行スキップ: {e}", file=sys.stderr)
    return members


def _derive_gravity_scores(members: list[dict]) -> dict:
    """メンバーデータから引力8項目スコア（◎/○/△/×）を導出"""
    if not members:
        return {k: "△" for k in GRAVITY_SCORE_KEYS}

    n = len(members)

    avg_engagement = sum(m["engagement_score"] for m in members) / n
    engagement_sym = _score_from_float(avg_engagement)

    departure_count = sum(1 for m in members if m["has_departure_risk"])
    departure_ratio = departure_count / n
    if departure_ratio <= 0.05:
        departure_sym = "◎"
    elif departure_ratio <= 0.15:
        departure_sym = "○"
    elif departure_ratio <= 0.30:
        departure_sym = "△"
    else:
        departure_sym = "×"

    avg_overtime = sum(m["overtime_hours"] for m in members) / n
    if avg_overtime <= 10:
        psych_safety_sym = "◎"
    elif avg_overtime <= 20:
        psych_safety_sym = "○"
    elif avg_overtime <= 30:
        psych_safety_sym = "△"
    else:
        psych_safety_sym = "×"

    one_on_one_rate = sum(1 for m in members if m["one_on_one_done"]) / n
    if one_on_one_rate >= 0.9:
        exec_voice_sym = "◎"
    elif one_on_one_rate >= 0.7:
        exec_voice_sym = "○"
    elif one_on_one_rate >= 0.5:
        exec_voice_sym = "△"
    else:
        exec_voice_sym = "×"

    return {
        "recruitment_pipeline": "△",
        "final_decline_rate":   "△",
        "talent_retention":     _score_from_float(avg_engagement, (3.5, 2.8, 2.0)),
        "executive_voice":      exec_voice_sym,
        "engagement":           engagement_sym,
        "departure_signal":     departure_sym,
        "recruitment_wall_pof": "△",
        "psych_safety_cost":    psych_safety_sym,
    }


def _derive_departure_signals(members: list[dict]) -> dict:
    """メンバーデータから離職予兆5シグナルを導出"""
    if not members:
        return {k: "△" for k in DEPARTURE_SIGNAL_KEYS}

    n = len(members)

    avg_absence = sum(m["absence_days"] for m in members) / n
    physical_sym = _score_from_float(-avg_absence + 5, (4.5, 3.5, 2.0))

    avg_overtime = sum(m["overtime_hours"] for m in members) / n
    overload_sym = _score_from_float(-avg_overtime + 35, (30, 20, 10))

    departure_count = sum(1 for m in members if m["has_departure_risk"])
    risk_ratio = departure_count / n
    meaning_sym = "×" if risk_ratio > 0.3 else ("△" if risk_ratio > 0.15 else "○")

    one_on_one_rate = sum(1 for m in members if m["one_on_one_done"]) / n
    rel_sym = _score_from_float(one_on_one_rate * 4)

    avg_engagement = sum(m["engagement_score"] for m in members) / n
    facial_sym = _score_from_float(avg_engagement)

    return {
        "physical":      physical_sym,
        "facial":        facial_sym,
        "overload":      overload_sym,
        "meaning":       meaning_sym,
        "relationships": rel_sym,
    }


def _build_orbit_json(
    client_id: str,
    month: str,
    members: list[dict],
    source: str,
    raw_count: int,
) -> dict:
    """Orbit 標準 JSON を組み立てる"""
    gravity_scores = _derive_gravity_scores(members)
    departure_signals = _derive_departure_signals(members)

    now_jst = datetime.now(JST).strftime("%Y-%m-%d %H:%M JST")

    prev_month_dt = datetime.strptime(month, "%Y-%m") - timedelta(days=1)
    prev_month = prev_month_dt.strftime("%Y-%m")

    return {
        "client_id":     client_id,
        "month":         month,
        "previous_month": prev_month,
        "source":        source,
        "fetched_at":    now_jst,
        "member_count":  raw_count,
        "gravity_scores": {
            "current":  gravity_scores,
            "previous": {k: "△" for k in GRAVITY_SCORE_KEYS},
        },
        "departure_signals": departure_signals,
        "members_masked": members,
        "memo": f"[OT-1 自動生成] source={source} / member_count={raw_count} / fetched={now_jst}",
    }


def fetch_from_csv(csv_path: str, client_id: str, month: str, mask: bool = True) -> dict:
    """汎用 CSV / SmartHR CSV エクスポートからデータ取得・正規化"""
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        members = _parse_csv_members(reader, mask)
    print(f"[INFO] CSV 読み込み完了: {len(members)} 件 (mask={mask})", file=sys.stderr)
    return _build_orbit_json(client_id, month, members, "csv", len(members))


def fetch_from_demo(client_id: str, month: str, mask: bool = True) -> dict:
    """同梱サンプル CSV からデモデータを生成"""
    reader = csv.DictReader(io.StringIO(DEMO_CSV_CONTENT))
    members = _parse_csv_members(reader, mask)
    print(f"[INFO] デモ CSV 読み込み完了: {len(members)} 件 (mask={mask})", file=sys.stderr)
    return _build_orbit_json(client_id, month, members, "demo", len(members))


def fetch_from_wevox_mock(client_id: str, month: str, api_key: Optional[str] = None, mask: bool = True) -> dict:
    """Wevox API モック（MVP: stub レスポンス）"""
    print(f"[INFO] Wevox API モック実行中（実 API キーなし・stub レスポンス・mask={mask}）", file=sys.stderr)
    mock_members = [
        {"member_id": _mask_name("WevoxUser1", mask), "email_domain": "@example.com", "department": "営業部",
         "engagement_score": 3.2, "absence_days": 1, "overtime_hours": 14,
         "one_on_one_done": True, "has_departure_risk": False},
        {"member_id": _mask_name("WevoxUser2", mask), "email_domain": "@example.com", "department": "開発部",
         "engagement_score": 2.0, "absence_days": 4, "overtime_hours": 32,
         "one_on_one_done": False, "has_departure_risk": True},
        {"member_id": _mask_name("WevoxUser3", mask), "email_domain": "@client.jp", "department": "人事部",
         "engagement_score": 3.7, "absence_days": 0, "overtime_hours": 7,
         "one_on_one_done": True, "has_departure_risk": False},
        {"member_id": _mask_name("WevoxUser4", mask), "email_domain": "@client.jp", "department": "営業部",
         "engagement_score": 2.6, "absence_days": 2, "overtime_hours": 22,
         "one_on_one_done": True, "has_departure_risk": False},
        {"member_id": _mask_name("WevoxUser5", mask), "email_domain": "@example.com", "department": "開発部",
         "engagement_score": 1.5, "absence_days": 6, "overtime_hours": 40,
         "one_on_one_done": False, "has_departure_risk": True},
    ]
    return _build_orbit_json(client_id, month, mock_members, "wevox_mock", len(mock_members))


def fetch_from_kaonavi_mock(client_id: str, month: str, api_key: Optional[str] = None, mask: bool = True) -> dict:
    """カオナビ API モック（MVP: stub レスポンス）"""
    print(f"[INFO] カオナビ API モック実行中（実 API キーなし・stub レスポンス・mask={mask}）", file=sys.stderr)
    mock_members = [
        {"member_id": _mask_name("KaonaviUser1", mask), "email_domain": "@corp.jp", "department": "管理部",
         "engagement_score": 3.4, "absence_days": 0, "overtime_hours": 9,
         "one_on_one_done": True, "has_departure_risk": False},
        {"member_id": _mask_name("KaonaviUser2", mask), "email_domain": "@corp.jp", "department": "営業部",
         "engagement_score": 2.3, "absence_days": 3, "overtime_hours": 25,
         "one_on_one_done": False, "has_departure_risk": True},
        {"member_id": _mask_name("KaonaviUser3", mask), "email_domain": "@corp.jp", "department": "技術部",
         "engagement_score": 3.9, "absence_days": 0, "overtime_hours": 5,
         "one_on_one_done": True, "has_departure_risk": False},
    ]
    return _build_orbit_json(client_id, month, mock_members, "kaonavi_mock", len(mock_members))


def save_orbit_json(data: dict, client_id: str, month: str) -> str:
    """Orbit 標準 JSON を orbit_data/<CLIENT_ID>_<YYYY-MM>.json に保存"""
    os.makedirs(DATA_DIR, exist_ok=True)
    output_path = os.path.join(DATA_DIR, f"{client_id}_{month}.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Orbit タレマネデータ取得・正規化エンジン（OT-1）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python3 orbit_data_fetcher.py --source csv --client demo --month 2026-05
  python3 orbit_data_fetcher.py --source wevox --client HACHI --month 2026-05
  python3 orbit_data_fetcher.py --source kaonavi --client HACHI --month 2026-05
  python3 orbit_data_fetcher.py --source smarthr --client demo --month 2026-05 --input members.csv
  python3 orbit_data_fetcher.py --demo --month 2026-05

出力:
  orbit_data/<CLIENT_ID>_<YYYY-MM>.json
        """,
    )
    parser.add_argument("--source",  choices=["wevox", "kaonavi", "smarthr", "csv"],
                        help="データソース種別")
    parser.add_argument("--client",  default="demo", help="クライアントID（例: HACHI）")
    parser.add_argument("--month",   required=True,  help="対象月 YYYY-MM（例: 2026-05）")
    parser.add_argument("--input",   help="CSV ファイルパス（--source csv/smarthr 時）")
    parser.add_argument("--config",  help="設定 JSON ファイルパス（API キー等）")
    parser.add_argument("--demo",    action="store_true", help="同梱サンプル CSV からデモ実行")
    parser.add_argument("--dry-run", action="store_true", help="ファイル保存をスキップ（JSON を stdout に出力）")
    parser.add_argument("--mask",    action=argparse.BooleanOptionalAction, default=True,
                        help="氏名/メールを SHA-256 ハッシュ化（デフォルト ON・--no-mask で素通し）")
    args = parser.parse_args()

    try:
        datetime.strptime(args.month, "%Y-%m")
    except ValueError:
        print(f"[ERROR] --month の形式が不正です: '{args.month}'（正しい形式: YYYY-MM）", file=sys.stderr)
        sys.exit(1)

    if not args.demo and not args.source:
        print("[ERROR] --source または --demo を指定してください", file=sys.stderr)
        sys.exit(1)

    api_key = None
    if args.config:
        try:
            with open(args.config, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                api_key = cfg.get("api_key")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"[WARN] config 読み込みに失敗: {e}", file=sys.stderr)

    client_id = args.client
    month     = args.month

    if args.demo:
        data = fetch_from_demo(client_id, month, args.mask)
    elif args.source in ("csv", "smarthr"):
        csv_path = args.input
        if not csv_path:
            print("[INFO] --input 未指定のため同梱デモ CSV を使用します", file=sys.stderr)
            data = fetch_from_demo(client_id, month, args.mask)
        else:
            if not os.path.exists(csv_path):
                print(f"[ERROR] CSV ファイルが見つかりません: {csv_path}", file=sys.stderr)
                sys.exit(1)
            data = fetch_from_csv(csv_path, client_id, month, args.mask)
    elif args.source == "wevox":
        data = fetch_from_wevox_mock(client_id, month, api_key, args.mask)
    elif args.source == "kaonavi":
        data = fetch_from_kaonavi_mock(client_id, month, api_key, args.mask)
    else:
        print(f"[ERROR] 未対応の source: {args.source}", file=sys.stderr)
        sys.exit(1)

    if args.dry_run:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        print(f"[INFO] dry-run モード: ファイル保存をスキップしました", file=sys.stderr)
    else:
        output_path = save_orbit_json(data, client_id, month)
        size_kb = os.path.getsize(output_path) // 1024 or 1
        print(f"[OK] 出力完了: {output_path} ({size_kb} KB)", file=sys.stderr)
        print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
