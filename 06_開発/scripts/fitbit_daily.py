"""
Fitbit デイリーデータ取得スクリプト
- 睡眠、歩数、心拍、SpO2、HRV等を取得
- JSON形式で標準出力（他スキルから呼び出し可能）
- デイリーログへの直接書き込みも可能

使い方:
  python fitbit_daily.py              # 前日分を取得
  python fitbit_daily.py 2026-04-09   # 指定日のデータを取得
  python fitbit_daily.py --markdown   # マークダウンテーブル形式で出力
"""

import json
import os
import sys
from datetime import datetime, timedelta
from urllib.request import urlopen, Request
from urllib.error import HTTPError
from urllib.parse import urlencode
import base64

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config_fitbit.json")
API_BASE = "https://api.fitbit.com"
TOKEN_URL = "https://api.fitbit.com/oauth2/token"


def load_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


def save_config(config):
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)


def refresh_access_token(config):
    credentials = f"{config['client_id']}:{config['client_secret']}"
    b64_credentials = base64.b64encode(credentials.encode()).decode()

    data = urlencode({
        "grant_type": "refresh_token",
        "refresh_token": config["refresh_token"],
    }).encode()

    req = Request(TOKEN_URL, data=data, method="POST")
    req.add_header("Authorization", f"Basic {b64_credentials}")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")

    with urlopen(req) as resp:
        token_data = json.loads(resp.read().decode())

    config["access_token"] = token_data["access_token"]
    config["refresh_token"] = token_data["refresh_token"]
    save_config(config)
    return config


def api_get(config, path):
    url = f"{API_BASE}{path}"
    req = Request(url)
    req.add_header("Authorization", f"Bearer {config['access_token']}")
    req.add_header("Accept", "application/json")

    try:
        with urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except HTTPError as e:
        if e.code == 401:
            config = refresh_access_token(config)
            req = Request(url)
            req.add_header("Authorization", f"Bearer {config['access_token']}")
            req.add_header("Accept", "application/json")
            with urlopen(req) as resp:
                return json.loads(resp.read().decode())
        raise


def fetch_sleep(config, date_str):
    data = api_get(config, f"/1.2/user/-/sleep/date/{date_str}.json")
    if not data.get("sleep"):
        return None

    # メインスリープから直接取得（アプリ表示値に近い）
    main_sleep = None
    for s in data["sleep"]:
        if s.get("isMainSleep"):
            main_sleep = s
            break

    if not main_sleep:
        main_sleep = data["sleep"][0]

    # メインスリープのステージデータを使用（summaryではなく個別ログ）
    levels = main_sleep.get("levels", {})
    levels_summary = levels.get("summary", {})
    stages = {
        "deep": levels_summary.get("deep", {}).get("minutes", 0),
        "light": levels_summary.get("light", {}).get("minutes", 0),
        "rem": levels_summary.get("rem", {}).get("minutes", 0),
        "wake": levels_summary.get("wake", {}).get("minutes", 0),
    }

    # 睡眠時間：メインスリープのduration（ミリ秒）からwakeを引く
    duration_ms = main_sleep.get("duration", 0)
    time_in_bed = duration_ms // 60000  # ミリ秒→分
    total_minutes = main_sleep.get("minutesAsleep", 0)
    # minutesAsleepが0や異常値の場合、ステージ合算で代替
    if total_minutes == 0:
        total_minutes = stages["deep"] + stages["light"] + stages["rem"]

    hours = total_minutes // 60
    mins = total_minutes % 60
    efficiency = main_sleep.get("efficiency")

    # 睡眠スコア：efficiency（効率%）とは別物
    score = None

    # 方法1: sleep logのsleepScore フィールド（新しいAPIバージョン）
    score = main_sleep.get("sleepScore")

    # 方法2: Sleep Score API（複数エンドポイントを試行）
    if score is None:
        score_endpoints = [
            f"/1.2/user/-/sleep/date/{date_str}/score.json",
            f"/1/user/-/sleep/score/date/{date_str}.json",
        ]
        for endpoint in score_endpoints:
            try:
                score_data = api_get(config, endpoint)
                if score_data:
                    # レスポンス形式のバリエーションに対応
                    if isinstance(score_data, dict):
                        score = (score_data.get("sleepScore")
                                or score_data.get("overallScore")
                                or score_data.get("score"))
                    elif isinstance(score_data, list) and len(score_data) > 0:
                        score = (score_data[0].get("overallScore")
                                or score_data[0].get("sleepScore")
                                or score_data[0].get("score"))
                if score is not None:
                    break
            except Exception:
                continue

    return {
        "total_minutes": total_minutes,
        "total_display": f"{hours}h{mins:02d}m",
        "time_in_bed": time_in_bed,
        "score": score,
        "deep_minutes": stages["deep"],
        "light_minutes": stages["light"],
        "rem_minutes": stages["rem"],
        "wake_minutes": stages["wake"],
        "efficiency": efficiency,
    }


def fetch_activity(config, date_str):
    data = api_get(config, f"/1/user/-/activities/date/{date_str}.json")
    summary = data.get("summary", {})

    return {
        "steps": summary.get("steps", 0),
        "distance_km": round(sum(
            d.get("distance", 0)
            for d in summary.get("distances", [])
            if d.get("activity") == "total"
        ), 2),
        "floors": summary.get("floors", 0),
        "calories_total": summary.get("caloriesOut", 0),
        "calories_active": summary.get("activityCalories", 0),
        "active_zone_minutes": summary.get("activeZoneMinutes", {}).get("totalMinutes", 0),
        "fairly_active_minutes": summary.get("fairlyActiveMinutes", 0),
        "very_active_minutes": summary.get("veryActiveMinutes", 0),
    }


def fetch_heart_rate(config, date_str):
    data = api_get(config, f"/1/user/-/activities/heart/date/{date_str}/1d.json")
    hr_data = data.get("activities-heart", [])
    if not hr_data:
        return None

    value = hr_data[0].get("value", {})
    resting = value.get("restingHeartRate")
    zones = {}
    for zone in value.get("heartRateZones", []):
        zones[zone["name"]] = {
            "minutes": zone.get("minutes", 0),
            "calories": round(zone.get("caloriesOut", 0), 1),
        }

    return {
        "resting_hr": resting,
        "zones": zones,
    }


def fetch_spo2(config, date_str):
    try:
        data = api_get(config, f"/1/user/-/spo2/date/{date_str}.json")
        if data and "value" in data:
            return {
                "avg": data["value"].get("avg"),
                "min": data["value"].get("min"),
                "max": data["value"].get("max"),
            }
    except HTTPError:
        pass
    return None


def fetch_hrv(config, date_str):
    try:
        data = api_get(config, f"/1/user/-/hrv/date/{date_str}.json")
        if data and "hrv" in data and len(data["hrv"]) > 0:
            value = data["hrv"][0].get("value", {})
            return {
                "daily_rmssd": round(value.get("dailyRmssd", 0), 1),
                "deep_rmssd": round(value.get("deepRmssd", 0), 1),
            }
    except HTTPError:
        pass
    return None


def fetch_breathing_rate(config, date_str):
    try:
        data = api_get(config, f"/1/user/-/br/date/{date_str}.json")
        if data and "br" in data and len(data["br"]) > 0:
            value = data["br"][0].get("value", {})
            return {"breathing_rate": value.get("breathingRate")}
    except HTTPError:
        pass
    return None


def fetch_skin_temp(config, date_str):
    try:
        data = api_get(config, f"/1/user/-/temp/skin/date/{date_str}.json")
        if data and "tempSkin" in data and len(data["tempSkin"]) > 0:
            value = data["tempSkin"][0].get("value", {})
            return {"skin_temp_variation": value.get("nightlyRelative")}
    except HTTPError:
        pass
    return None


def fetch_all(config, date_str):
    result = {"date": date_str}

    sleep = fetch_sleep(config, date_str)
    if sleep:
        result["sleep"] = sleep

    activity = fetch_activity(config, date_str)
    if activity:
        result["activity"] = activity

    hr = fetch_heart_rate(config, date_str)
    if hr:
        result["heart_rate"] = hr

    spo2 = fetch_spo2(config, date_str)
    if spo2:
        result["spo2"] = spo2

    hrv = fetch_hrv(config, date_str)
    if hrv:
        result["hrv"] = hrv

    br = fetch_breathing_rate(config, date_str)
    if br:
        result["breathing_rate"] = br

    temp = fetch_skin_temp(config, date_str)
    if temp:
        result["skin_temp"] = temp

    return result


def format_markdown(data):
    lines = []
    lines.append("### Fitbit データ")
    lines.append("")

    # 睡眠
    sleep = data.get("sleep")
    if sleep:
        lines.append("**睡眠**")
        lines.append("")
        lines.append("| 指標 | 値 |")
        lines.append("|------|-----|")
        lines.append(f"| 合計睡眠 | {sleep['total_display']}（※アプリ表示と最大30分程度の誤差あり） |")
        if sleep.get("score"):
            lines.append(f"| 睡眠スコア | {sleep['score']} |")
        if sleep.get("efficiency"):
            lines.append(f"| 睡眠効率 | {sleep['efficiency']}%（※アプリの睡眠スコアとは別指標） |")
        if sleep.get("deep_minutes"):
            lines.append(f"| 深い睡眠 | {sleep['deep_minutes']}分 |")
        if sleep.get("rem_minutes"):
            lines.append(f"| REM | {sleep['rem_minutes']}分 |")
        if sleep.get("light_minutes"):
            lines.append(f"| 浅い睡眠 | {sleep['light_minutes']}分 |")
        if sleep.get("wake_minutes"):
            lines.append(f"| 覚醒 | {sleep['wake_minutes']}分 |")
        goal_met = "達成" if sleep["total_minutes"] >= 420 else "未達"
        lines.append(f"| **7h目標** | **{goal_met}** |")
        lines.append("")

    # アクティビティ
    activity = data.get("activity")
    if activity:
        lines.append("**アクティビティ**")
        lines.append("")
        lines.append("| 指標 | 値 |")
        lines.append("|------|-----|")
        lines.append(f"| 歩数 | {activity['steps']:,} |")
        if activity.get("distance_km"):
            lines.append(f"| 距離 | {activity['distance_km']}km |")
        if activity.get("floors"):
            lines.append(f"| 階数 | {activity['floors']} |")
        lines.append(f"| 消費カロリー | {activity['calories_total']:,}kcal |")
        if activity.get("active_zone_minutes"):
            lines.append(f"| アクティブゾーン | {activity['active_zone_minutes']}分 |")
        exercise_mins = activity.get("fairly_active_minutes", 0) + activity.get("very_active_minutes", 0)
        if exercise_mins:
            lines.append(f"| 運動時間 | {exercise_mins}分 |")
        lines.append("")

    # 心拍
    hr = data.get("heart_rate")
    if hr and hr.get("resting_hr"):
        lines.append("**心拍・バイタル**")
        lines.append("")
        lines.append("| 指標 | 値 |")
        lines.append("|------|-----|")
        lines.append(f"| 安静時心拍 | {hr['resting_hr']}bpm |")

        hrv = data.get("hrv")
        if hrv and hrv.get("daily_rmssd"):
            lines.append(f"| HRV (RMSSD) | {hrv['daily_rmssd']}ms |")

        spo2 = data.get("spo2")
        if spo2 and spo2.get("avg"):
            lines.append(f"| SpO2 | {spo2['avg']}% |")

        br = data.get("breathing_rate")
        if br and br.get("breathing_rate"):
            lines.append(f"| 呼吸数 | {br['breathing_rate']}/分 |")

        temp = data.get("skin_temp")
        if temp and temp.get("skin_temp_variation") is not None:
            lines.append(f"| 皮膚温変動 | {temp['skin_temp_variation']:+.1f}°C |")

        lines.append("")

    # バランスホイール用サマリー（1行）
    summary_parts = []
    if sleep:
        summary_parts.append(f"睡眠{sleep['total_display']}")
        if sleep.get("score"):
            summary_parts[-1] += f"（スコア{sleep['score']}）"
        elif sleep.get("efficiency"):
            summary_parts[-1] += f"（効率{sleep['efficiency']}%）"
    if activity:
        summary_parts.append(f"{activity['steps']:,}歩")
    if hr and hr.get("resting_hr"):
        summary_parts.append(f"安静時心拍{hr['resting_hr']}")
    if data.get("hrv", {}).get("daily_rmssd"):
        summary_parts.append(f"HRV {data['hrv']['daily_rmssd']}")

    lines.append(f"> **バランスホイール記入用:** {' / '.join(summary_parts)}")
    lines.append("")

    return "\n".join(lines)


def main():
    config = load_config()

    if not config.get("access_token"):
        print("エラー: まず fitbit_auth.py を実行してください")
        sys.exit(1)

    # 日付の決定
    if len(sys.argv) > 1 and not sys.argv[1].startswith("--"):
        date_str = sys.argv[1]
    else:
        yesterday = datetime.now() - timedelta(days=1)
        date_str = yesterday.strftime("%Y-%m-%d")

    markdown_mode = "--markdown" in sys.argv

    print(f"Fitbitデータ取得中: {date_str}", file=sys.stderr)

    data = fetch_all(config, date_str)

    if markdown_mode:
        print(format_markdown(data))
    else:
        print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
