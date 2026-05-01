"""
Meta広告デイリーレポート自動取得スクリプト
- Meta Marketing APIから前日の広告データを取得
- デイリーログ（mdファイル）の数値テーブルを自動更新

使い方:
  python meta_ads_daily.py              # 前日分を取得して当日のmdに反映
  python meta_ads_daily.py 2026-03-11   # 指定日のデータを取得
"""

import os
import re
import sys
import json
from datetime import datetime, timedelta
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode

# ============================================================
# 設定
# ============================================================
AD_ACCOUNT_ID = "1832186337593481"
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config_meta.json")
DAILY_LOG_DIR = os.path.expanduser(
    "~/Documents/Obsidian Vault/04_GrowthFix/04_デイリーログ"
)

# 広告名とmdテーブルのマッピング（広告名に含まれるキーワードで判定）
AD_NAME_MAP = {
    # セミナー広告（現行）
    "01_ceiling": "セミナー_天井",
    "02_ceiling": "セミナー_天井B",
    "01_code": "セミナー_CODE",
    # 旧広告（停止中・データ参照用に残す）
    "p1_white": "P1_white",
    "p1_navy": "P1_navy",
    "p2_white": "P2_white",
    "p2_navy": "P2_navy",
    "p3_white": "P3_white",
    "p4_white": "P4_white",
    "p5_判断グセ診断用": "P5_判断",
    "p6_盲点チェック用": "P6_盲点",
    "p6_判断グセ診断用": "P6_判断",
}


# ============================================================
# トークン管理
# ============================================================
def load_token():
    if not os.path.exists(CONFIG_PATH):
        print("❌ config_meta.json が見つかりません。")
        print("   以下のコマンドで作成してください：")
        print(f'   echo \'{{"access_token": "YOUR_TOKEN"}}\' > {CONFIG_PATH}')
        sys.exit(1)
    with open(CONFIG_PATH) as f:
        config = json.load(f)
    token = config.get("access_token", "")
    if not token:
        print("❌ access_token が空です。config_meta.json を確認してください。")
        sys.exit(1)
    return token


# ============================================================
# Meta API呼び出し
# ============================================================
def api_get(endpoint, params):
    url = f"https://graph.facebook.com/v21.0/{endpoint}?{urlencode(params)}"
    req = Request(url)
    try:
        with urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except HTTPError as e:
        body = e.read().decode()
        print(f"❌ API エラー ({e.code}): {body}")
        sys.exit(1)
    except URLError as e:
        print(f"❌ 接続エラー: {e.reason}")
        sys.exit(1)


def fetch_ad_insights(token, date_str):
    """指定日の広告レベルのインサイトを取得"""
    params = {
        "access_token": token,
        "level": "ad",
        "fields": "ad_name,impressions,clicks,ctr,spend",
        "time_range": json.dumps({"since": date_str, "until": date_str}),
        "limit": 100,
    }
    data = api_get(f"act_{AD_ACCOUNT_ID}/insights", params)
    return data.get("data", [])


def fetch_account_info(token):
    """アカウント情報を取得してトークンの有効性を確認"""
    params = {
        "access_token": token,
        "fields": "name,account_status",
    }
    return api_get(f"act_{AD_ACCOUNT_ID}", params)


# ============================================================
# データ整形
# ============================================================
def map_ad_data(insights):
    """APIレスポンスをmd用のデータに変換"""
    empty = {"impressions": "-", "clicks": "-", "ctr": "-", "spend": "-"}
    result = {name: dict(empty) for name in AD_NAME_MAP.values()}
    totals = {"impressions": 0, "clicks": 0, "spend": 0.0}

    for row in insights:
        ad_name = row.get("ad_name", "").lower()
        matched_key = None
        for keyword, display_name in AD_NAME_MAP.items():
            if keyword in ad_name:
                matched_key = display_name
                break
        if not matched_key:
            print(f"  ⚠️ マッピングできない広告名: {row.get('ad_name')}")
            continue

        imp = int(row.get("impressions", 0))
        clk = int(row.get("clicks", 0))
        ctr = row.get("ctr", "0")
        spend = float(row.get("spend", 0))

        result[matched_key] = {
            "impressions": f"{imp:,}",
            "clicks": f"{clk:,}",
            "ctr": f"{float(ctr):.2f}%",
            "spend": f"¥{spend:,.0f}",
        }
        totals["impressions"] += imp
        totals["clicks"] += clk
        totals["spend"] += spend

    total_ctr = (
        f"{(totals['clicks'] / totals['impressions'] * 100):.2f}%"
        if totals["impressions"] > 0
        else "-"
    )
    result["合計"] = {
        "impressions": f"{totals['impressions']:,}",
        "clicks": f"{totals['clicks']:,}",
        "ctr": total_ctr,
        "spend": f"¥{totals['spend']:,.0f}",
    }
    return result


# ============================================================
# mdファイル更新
# ============================================================
def get_daily_log_path(date_str):
    """日付からmdファイルパスを生成"""
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    filename = dt.strftime("%y%m%d") + "_daily.md"
    return os.path.join(DAILY_LOG_DIR, filename)


def update_daily_log(filepath, ad_data):
    """mdファイルのMeta広告テーブルを更新（カラム構造を動的に検出）"""
    if not os.path.exists(filepath):
        print(f"❌ デイリーログが見つかりません: {filepath}")
        return False

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # ヘッダー行（"| 指標 |"で始まる行）を探す
    header_idx = None
    for i, line in enumerate(lines):
        if line.strip().startswith("| 指標 |") and "合計" in line:
            header_idx = i
            break

    if header_idx is None:
        print("⚠️ Meta広告テーブルが見つかりませんでした。手動で確認してください。")
        return False

    # ヘッダーからカラム名を抽出
    header_cols = [c.strip() for c in lines[header_idx].strip().split("|")[1:-1]]
    # header_cols = ["指標", "P5_判断", "P6_盲点", "P6_判断", "合計"] etc.
    data_cols = header_cols[1:]  # "指標"を除く

    def build_row(label, metric):
        vals = []
        for col in data_cols:
            if col in ad_data:
                vals.append(ad_data[col][metric])
            else:
                vals.append("-")
        return "| " + label + " | " + " | ".join(vals) + " |\n"

    # セパレータ行の次（header_idx + 2）から4行を置換
    data_start = header_idx + 2
    new_lines = lines[:data_start]
    new_lines.append(build_row("インプレッション", "impressions"))
    new_lines.append(build_row("クリック", "clicks"))
    new_lines.append(build_row("CTR", "ctr"))
    new_lines.append(build_row("費用", "spend"))

    # 既存のデータ行をスキップ
    skip = data_start
    for j in range(data_start, min(data_start + 4, len(lines))):
        if lines[j].strip().startswith("|"):
            skip = j + 1
        else:
            break
    new_lines.extend(lines[skip:])

    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    return True


# ============================================================
# メイン
# ============================================================
def main():
    # 日付の決定（引数 or 前日）
    if len(sys.argv) > 1:
        target_date = sys.argv[1]
    else:
        target_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    print(f"📊 Meta広告データ取得: {target_date}")
    print()

    # トークン読み込み
    token = load_token()

    # アカウント確認
    print("🔍 アカウント確認中...")
    info = fetch_account_info(token)
    print(f"   ✅ {info.get('name', 'Unknown')} (Status: {info.get('account_status')})")
    print()

    # インサイト取得
    print("📥 広告データ取得中...")
    insights = fetch_ad_insights(token, target_date)

    if not insights:
        print("   ⚠️ データなし（配信がない or まだ反映されていません）")
        return

    print(f"   ✅ {len(insights)}件の広告データを取得")
    print()

    # データ整形
    ad_data = map_ad_data(insights)

    # 結果表示
    print("📋 取得結果:")
    # アクティブな広告（データありのもの）+ 合計を表示
    active_cols = [k for k in ad_data if k != "合計" and ad_data[k]["impressions"] != "-"]
    if not active_cols:
        active_cols = list(AD_NAME_MAP.values())
    cols = active_cols + ["合計"]
    print(f"  {'指標':<12} " + "  ".join(f"{c:>10}" for c in cols))
    print("  " + "-" * (14 + 12 * len(cols)))
    for label, metric in [
        ("インプレッション", "impressions"),
        ("クリック", "clicks"),
        ("CTR", "ctr"),
        ("費用", "spend"),
    ]:
        vals = "  ".join(f"{ad_data[c][metric]:>10}" for c in cols)
        print(f"  {label:<12} {vals}")
    print()

    # mdファイル更新
    # 取得データの日付の翌日のログに記入（前日データを翌日の振り返りに）
    # ただし引数指定の場合はその日のログに記入
    log_date = target_date
    log_path = get_daily_log_path(log_date)

    if os.path.exists(log_path):
        print(f"📝 デイリーログ更新中: {os.path.basename(log_path)}")
        if update_daily_log(log_path, ad_data):
            print("   ✅ 更新完了!")
        else:
            print("   ❌ 更新失敗")
    else:
        print(f"⚠️ デイリーログが見つかりません: {os.path.basename(log_path)}")
        print("   数値はコンソール出力を参照してください。")


if __name__ == "__main__":
    main()
