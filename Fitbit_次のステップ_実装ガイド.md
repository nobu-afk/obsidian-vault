# Fitbit API - 次のステップ実装ガイド

## 取得済み情報

以下の情報を既に取得済みです：

- **Client ID**: `23TMWD`
- **Client Secret**: `db52ab48f6b791dec60d7cf8169bda6c`
- **Redirect URL**: `http://localhost:8888`
- **認証URI**: `https://www.fitbit.com/oauth2/authorize`
- **トークンURI**: `https://api.fitbit.com/oauth2/token`

## 次のステップ：アクセストークンを取得する

### ステップ1: 認証URLを生成してブラウザで開く

まず、ユーザーをFitbitの認証ページにリダイレクトする必要があります。

#### 方法1: ブラウザで直接開く（テスト用）

以下のURLをブラウザのアドレスバーに貼り付けて開いてください：

```
https://www.fitbit.com/oauth2/authorize?response_type=code&client_id=23TMWD&redirect_uri=http://localhost:8888&scope=activity%20heartrate%20sleep%20profile
```

**注意**: 
- `scope`パラメータは必要な権限を指定します（例: `activity heartrate sleep profile`）
- URLエンコードされているため、スペースは`%20`になっています

#### 方法2: Pythonスクリプトで生成（推奨）

```python
import urllib.parse

def get_authorization_url():
    base_url = "https://www.fitbit.com/oauth2/authorize"
    params = {
        "response_type": "code",
        "client_id": "23TMWD",
        "redirect_uri": "http://localhost:8888",
        "scope": "activity heartrate sleep profile"  # 必要な権限を指定
    }
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    print(f"以下のURLをブラウザで開いてください:\n{url}")
    return url

if __name__ == "__main__":
    get_authorization_url()
```

### ステップ2: ユーザーが認証・承認する

1. 上記のURLをブラウザで開く
2. Fitbitアカウントでログイン（まだログインしていない場合）
3. アプリが要求する権限を確認し、「許可」をクリック

### ステップ3: 認可コードを取得する

認証が成功すると、ブラウザが以下のようなURLにリダイレクトされます：

```
http://localhost:8888/?code=XXXXXX&state=YYYYYY
```

**重要**: 
- `code=`の後の値（`XXXXXX`の部分）が**認可コード**です
- このコードは約10分間のみ有効です
- このコードをコピーして次のステップで使用します

**⚠️ エラーが表示される場合**: 
- `ERR_CONNECTION_REFUSED` エラーが表示されても問題ありません
- **URLバーを見てください**。認可コードが含まれています
- エラーページが表示されても、URLバーから認可コードをコピーできます

**より簡単な方法**: 
- ローカルサーバーを起動すると、認可コードが自動的に表示されます
- 詳細は `Fitbit_認可コード取得方法_エラー対処.md` を参照してください

### ステップ4: 認可コードをアクセストークンと交換する

認可コードを取得したら、以下のPythonスクリプトでアクセストークンを取得します：

```python
import requests
import base64

def get_access_token(auth_code):
    """
    認可コードをアクセストークンと交換する
    """
    # 認証情報
    client_id = "23TMWD"
    client_secret = "db52ab48f6b791dec60d7cf8169bda6c"
    redirect_uri = "http://localhost:8888"
    
    # Basic認証用のヘッダーを作成
    credentials = f"{client_id}:{client_secret}"
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
        "redirect_uri": redirect_uri
    }
    
    # POSTリクエストを送信
    response = requests.post(token_url, headers=headers, data=data)
    
    if response.status_code == 200:
        token_data = response.json()
        print("✅ アクセストークンの取得に成功しました！")
        print(f"\nAccess Token: {token_data['access_token']}")
        print(f"Refresh Token: {token_data['refresh_token']}")
        print(f"有効期限: {token_data['expires_in']}秒（約{token_data['expires_in']/3600:.1f}時間）")
        print(f"ユーザーID: {token_data.get('user_id', 'N/A')}")
        print(f"\n⚠️ これらのトークンは安全な場所に保存してください！")
        return token_data
    else:
        print(f"❌ エラーが発生しました: {response.status_code}")
        print(f"レスポンス: {response.text}")
        return None

# 使用例
if __name__ == "__main__":
    # ステップ3で取得した認可コードをここに貼り付ける
    authorization_code = input("認可コードを入力してください: ").strip()
    
    token_data = get_access_token(authorization_code)
    
    if token_data:
        # トークンをファイルに保存（オプション）
        with open("fitbit_tokens.txt", "w") as f:
            f.write(f"Access Token: {token_data['access_token']}\n")
            f.write(f"Refresh Token: {token_data['refresh_token']}\n")
            f.write(f"User ID: {token_data.get('user_id', 'N/A')}\n")
        print("\n✅ トークンを fitbit_tokens.txt に保存しました")
```

### ステップ5: アクセストークンを使用してAPIにアクセスする

アクセストークンを取得したら、以下のようにFitbit APIにアクセスできます：

```python
import requests
from datetime import datetime

def get_fitbit_data(access_token, endpoint):
    """
    Fitbit APIからデータを取得する
    """
    base_url = "https://api.fitbit.com"
    url = f"{base_url}{endpoint}"
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"エラー: {response.status_code} - {response.text}")
        return None

# 使用例
if __name__ == "__main__":
    # ステップ4で取得したアクセストークン
    access_token = "YOUR_ACCESS_TOKEN_HERE"
    
    # 今日の日付
    today = datetime.now().strftime("%Y-%m-%d")
    
    # プロフィール情報を取得
    print("📊 プロフィール情報を取得中...")
    profile = get_fitbit_data(access_token, "/1/user/-/profile.json")
    if profile:
        print(f"ユーザー名: {profile['user']['fullName']}")
    
    # 今日のアクティビティを取得
    print("\n🏃 今日のアクティビティを取得中...")
    activities = get_fitbit_data(access_token, f"/1/user/-/activities/date/{today}.json")
    if activities:
        summary = activities['summary']
        print(f"歩数: {summary.get('steps', 0):,}歩")
        print(f"消費カロリー: {summary.get('caloriesOut', 0):,}kcal")
        print(f"距離: {summary.get('distances', [{}])[0].get('distance', 0):.2f}km")
    
    # 今日の心拍数を取得
    print("\n❤️ 今日の心拍数を取得中...")
    heartrate = get_fitbit_data(access_token, f"/1/user/-/heart/date/{today}.json")
    if heartrate:
        print("心拍数データを取得しました")
    
    # 今日の睡眠データを取得
    print("\n😴 今日の睡眠データを取得中...")
    sleep = get_fitbit_data(access_token, f"/1/user/-/sleep/date/{today}.json")
    if sleep:
        if sleep.get('sleep'):
            total_sleep = sleep['sleep'][0]['duration'] / 1000 / 60  # ミリ秒を分に変換
            print(f"総睡眠時間: {total_sleep/60:.1f}時間")
```

## 完全な実装例（一括実行用）

以下のスクリプトを実行すると、認証からデータ取得まで一気に行えます：

```python
import requests
import base64
import urllib.parse
from datetime import datetime

# 認証情報
CLIENT_ID = "23TMWD"
CLIENT_SECRET = "db52ab48f6b791dec60d7cf8169bda6c"
REDIRECT_URI = "http://localhost:8888"

def step1_generate_auth_url():
    """ステップ1: 認証URLを生成"""
    base_url = "https://www.fitbit.com/oauth2/authorize"
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": "activity heartrate sleep profile"
    }
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    print("=" * 60)
    print("ステップ1: 認証URLを生成しました")
    print("=" * 60)
    print(f"\n以下のURLをブラウザで開いてください:\n\n{url}\n")
    print("認証後、リダイレクトされたURLから認可コードを取得してください。")
    print("（例: http://localhost:8888/?code=XXXXXX の XXXXXX の部分）\n")
    return url

def step2_get_access_token(auth_code):
    """ステップ2: アクセストークンを取得"""
    credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    
    token_url = "https://api.fitbit.com/oauth2/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {encoded_credentials}"
    }
    data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": REDIRECT_URI
    }
    
    response = requests.post(token_url, headers=headers, data=data)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"トークン取得エラー: {response.status_code} - {response.text}")

def step3_get_data(access_token):
    """ステップ3: Fitbitデータを取得"""
    base_url = "https://api.fitbit.com"
    today = datetime.now().strftime("%Y-%m-%d")
    
    print("\n" + "=" * 60)
    print("ステップ3: Fitbitデータを取得中...")
    print("=" * 60)
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # プロフィール
    try:
        profile = requests.get(f"{base_url}/1/user/-/profile.json", headers=headers).json()
        print(f"\n👤 ユーザー名: {profile['user']['fullName']}")
    except:
        print("\n❌ プロフィール取得に失敗")
    
    # アクティビティ
    try:
        activities = requests.get(
            f"{base_url}/1/user/-/activities/date/{today}.json", 
            headers=headers
        ).json()
        summary = activities['summary']
        print(f"\n🏃 今日のアクティビティ:")
        print(f"  歩数: {summary.get('steps', 0):,}歩")
        print(f"  消費カロリー: {summary.get('caloriesOut', 0):,}kcal")
        if summary.get('distances'):
            print(f"  距離: {summary['distances'][0].get('distance', 0):.2f}km")
    except Exception as e:
        print(f"\n❌ アクティビティ取得に失敗: {e}")
    
    # 睡眠
    try:
        sleep = requests.get(
            f"{base_url}/1/user/-/sleep/date/{today}.json", 
            headers=headers
        ).json()
        if sleep.get('sleep'):
            total_sleep = sleep['sleep'][0]['duration'] / 1000 / 60
            print(f"\n😴 睡眠データ:")
            print(f"  総睡眠時間: {total_sleep/60:.1f}時間")
    except:
        print("\n❌ 睡眠データ取得に失敗")

def main():
    print("\n🚀 Fitbit API アクセストークン取得ツール\n")
    
    # ステップ1: 認証URLを表示
    step1_generate_auth_url()
    
    # ステップ2: 認可コードを入力してもらう
    auth_code = input("\n認可コードを入力してください: ").strip()
    
    if not auth_code:
        print("❌ 認可コードが入力されていません")
        return
    
    try:
        # アクセストークンを取得
        print("\n" + "=" * 60)
        print("ステップ2: アクセストークンを取得中...")
        print("=" * 60)
        
        token_data = step2_get_access_token(auth_code)
        
        print("\n✅ アクセストークンの取得に成功しました！")
        print(f"\n📝 トークン情報:")
        print(f"  Access Token: {token_data['access_token'][:30]}...")
        print(f"  Refresh Token: {token_data['refresh_token'][:30]}...")
        print(f"  有効期限: {token_data['expires_in']}秒（約{token_data['expires_in']/3600:.1f}時間）")
        print(f"  ユーザーID: {token_data.get('user_id', 'N/A')}")
        
        # トークンをファイルに保存
        with open("fitbit_tokens.txt", "w") as f:
            f.write(f"Access Token: {token_data['access_token']}\n")
            f.write(f"Refresh Token: {token_data['refresh_token']}\n")
            f.write(f"User ID: {token_data.get('user_id', 'N/A')}\n")
            f.write(f"Expires In: {token_data['expires_in']}秒\n")
        print("\n💾 トークンを fitbit_tokens.txt に保存しました")
        
        # ステップ3: データを取得
        step3_get_data(token_data['access_token'])
        
        print("\n" + "=" * 60)
        print("✅ 完了！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")

if __name__ == "__main__":
    main()
```

## 実行手順まとめ

1. **認証URLを生成**
   - 上記のPythonスクリプトを実行するか、手動でURLを生成

2. **ブラウザで認証**
   - 生成されたURLをブラウザで開く
   - Fitbitアカウントでログイン・承認

3. **認可コードを取得**
   - リダイレクトされたURLから認可コードをコピー

4. **アクセストークンを取得**
   - 認可コードを使ってPythonスクリプトでトークンを取得

5. **APIにアクセス**
   - 取得したアクセストークンでFitbit APIからデータを取得

## 必要なライブラリのインストール

```bash
pip install requests
```

## 注意事項

- ⚠️ **Client Secretは秘密情報です**。GitHubなどに公開しないでください
- ⚠️ **アクセストークンは8時間で期限切れ**になります。期限切れ後はリフレッシュトークンで更新してください
- ⚠️ **認可コードは1回しか使用できません**。使用後は無効になります

## 次のステップ

アクセストークンを取得できたら、以下のファイルを参照してください：
- `Fitbit API実装例_完全版.md` - より詳細な実装例
- `Fitbit API_トラブルシューティング.md` - エラーが発生した場合の対処法

