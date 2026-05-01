"""
Fitbit OAuth2 認証セットアップ（初回のみ実行）

使い方:
  1. config_fitbit.json に client_id, client_secret を記入済み
  2. python fitbit_auth.py を実行
  3. ブラウザで認証 → リダイレクト先URLをコピーして貼り付け
  4. config_fitbit.json に access_token, refresh_token が保存される
"""

import json
import os
import sys
import webbrowser
from urllib.request import urlopen, Request
from urllib.parse import urlencode, urlparse, parse_qs
import base64

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config_fitbit.json")
AUTHORIZE_URL = "https://www.fitbit.com/oauth2/authorize"
TOKEN_URL = "https://api.fitbit.com/oauth2/token"

SCOPES = [
    "activity",
    "heartrate",
    "oxygen_saturation",
    "profile",
    "respiratory_rate",
    "settings",
    "sleep",
    "temperature",
    "weight",
]


def load_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


def save_config(config):
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)
    print(f"トークンを {CONFIG_PATH} に保存しました")


def exchange_code_for_token(config, code):
    credentials = f"{config['client_id']}:{config['client_secret']}"
    b64_credentials = base64.b64encode(credentials.encode()).decode()

    data = urlencode({
        "client_id": config["client_id"],
        "grant_type": "authorization_code",
        "redirect_uri": config["redirect_uri"],
        "code": code,
    }).encode()

    req = Request(TOKEN_URL, data=data, method="POST")
    req.add_header("Authorization", f"Basic {b64_credentials}")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")

    with urlopen(req) as resp:
        return json.loads(resp.read().decode())


def main():
    config = load_config()

    if not config.get("client_id") or not config.get("client_secret"):
        print("エラー: config_fitbit.json に client_id と client_secret を記入してください")
        sys.exit(1)

    params = urlencode({
        "response_type": "code",
        "client_id": config["client_id"],
        "redirect_uri": config["redirect_uri"],
        "scope": " ".join(SCOPES),
        "expires_in": "31536000",
    })
    auth_url = f"{AUTHORIZE_URL}?{params}"

    print("ブラウザで認証ページを開きます...")
    print(f"\nURL: {auth_url}\n")
    webbrowser.open(auth_url)

    print("=" * 60)
    print("手順:")
    print("  1. ブラウザでFitbitにログインして「許可」を押す")
    print("  2. growthfix.jp にリダイレクトされる")
    print("  3. ブラウザのアドレスバーのURLをコピー")
    print("  4. 下に貼り付けてEnter")
    print("=" * 60)
    print()

    redirect_url = input("リダイレクト先のURL: ").strip()

    parsed = urlparse(redirect_url)
    query = parse_qs(parsed.query)

    if "code" not in query:
        # フラグメント（#）にcodeがある場合もチェック
        if parsed.fragment:
            frag_query = parse_qs(parsed.fragment)
            if "code" in frag_query:
                query = frag_query

    if "code" not in query:
        print("エラー: URLに認証コードが含まれていません")
        print(f"  受け取ったURL: {redirect_url}")
        sys.exit(1)

    code = query["code"][0]
    print(f"\n認証コード取得: {code[:10]}...")
    print("トークンを取得中...")

    token_data = exchange_code_for_token(config, code)

    config["access_token"] = token_data["access_token"]
    config["refresh_token"] = token_data["refresh_token"]
    save_config(config)

    print("\nセットアップ完了。以下で動作確認できます:")
    print("  python fitbit_daily.py --markdown")


if __name__ == "__main__":
    main()
