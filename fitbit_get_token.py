"""
Fitbit アクセストークン取得スクリプト
認可コードを使ってアクセストークンを取得します
"""
import requests
import base64

# 認証情報
CLIENT_ID = "23TMWD"
CLIENT_SECRET = "db52ab48f6b791dec60d7cf8169bda6c"
REDIRECT_URI = "http://localhost:8888"

# 認可コード（またはブラウザのURL全体）を入力してもらう
# 例1: 認可コードだけ
#   ef0f276ba1c6bd8ddb992c905dac7cd1cf1d51ab
# 例2: URL全体
#   http://localhost:8888/?code=ef0f276ba1c6bd8ddb992c905dac7cd1cf1d51ab#_=_
raw_input_value = input("認可コード または ブラウザのURL全体を貼り付けてください: ").strip()

# 入力が空の場合は終了
if not raw_input_value:
    print("⚠️ 認可コード（またはURL）が入力されていません")
    print("ブラウザのURLバーに表示された文字列、または code= の後ろの文字列を貼り付けてください。")
    exit(1)

# URLが貼られた場合は、そこから code パラメータだけを抜き出す
auth_code = raw_input_value
if "http://" in raw_input_value or "https://" in raw_input_value:
    # クエリパラメータ部分から code= を抜き出す
    from urllib.parse import urlparse, parse_qs

    parsed = urlparse(raw_input_value)
    query_params = parse_qs(parsed.query)
    code_values = query_params.get("code")
    if not code_values:
        print("⚠️ URLから code パラメータを見つけられませんでした。")
        print("例: http://localhost:8888/?code=xxxxx のようなURLを貼り付けてください。")
        exit(1)
    auth_code = code_values[0]

# 万一「#_=」などが末尾についていた場合は削る
if "#" in auth_code:
    auth_code = auth_code.split("#", 1)[0]

# 最終的に認可コードが空でないかチェック
if not auth_code:
    print("⚠️ 認可コードを正しく取得できませんでした。")
    print("URLの code= の後ろの文字列をもう一度確認してください。")
    exit(1)

print("\n" + "=" * 60)
print("アクセストークンを取得中...")
print("=" * 60)

# Basic認証用のヘッダーを作成
credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
encoded_credentials = base64.b64encode(credentials.encode()).decode()

# トークンエンドポイント
token_url = "https://api.fitbit.com/oauth2/token"

# リクエストヘッダー
headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Authorization": f"Basic {encoded_credentials}"
}

# リクエストボディ
data = {
    "grant_type": "authorization_code",
    "code": auth_code,
    "redirect_uri": REDIRECT_URI
}

# POSTリクエストを送信
try:
    response = requests.post(token_url, headers=headers, data=data)
    
    if response.status_code == 200:
        token_data = response.json()
        
        print("\n✅ アクセストークンの取得に成功しました！")
        print("=" * 60)
        print(f"\n📝 トークン情報:")
        print(f"  Access Token: {token_data['access_token']}")
        print(f"  Refresh Token: {token_data['refresh_token']}")
        print(f"  有効期限: {token_data['expires_in']}秒（約{token_data['expires_in']/3600:.1f}時間）")
        print(f"  ユーザーID: {token_data.get('user_id', 'N/A')}")
        print(f"  スコープ: {token_data.get('scope', 'N/A')}")
        
        # トークンをファイルに保存
        with open("fitbit_tokens.txt", "w") as f:
            f.write(f"Access Token: {token_data['access_token']}\n")
            f.write(f"Refresh Token: {token_data['refresh_token']}\n")
            f.write(f"User ID: {token_data.get('user_id', 'N/A')}\n")
            f.write(f"Expires In: {token_data['expires_in']}秒\n")
            f.write(f"Scope: {token_data.get('scope', 'N/A')}\n")
        
        print("\n💾 トークンを fitbit_tokens.txt に保存しました")
        print("=" * 60)
        print("\n🎉 これでFitbit APIを使用する準備が整いました！")
        
    else:
        print(f"\n❌ エラーが発生しました: {response.status_code}")
        print(f"レスポンス: {response.text}")
        print("\n考えられる原因:")
        print("  - 認可コードが期限切れ（約10分で期限切れ）")
        print("  - 認可コードが既に使用済み")
        print("  - Redirect URIが一致していない")
        
except Exception as e:
    print(f"\n❌ エラーが発生しました: {e}")
    print("\n必要なライブラリがインストールされているか確認してください:")
    print("  pip install requests")


