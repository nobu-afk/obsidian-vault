# Fitbit OAuth 2.0認証フロー実装手順

## 概要

Fitbit APIを使用するには、OAuth 2.0認証フローを通じてアクセストークンを取得する必要があります。このドキュメントでは、認証フローの詳細な実装手順を説明します。

## OAuth 2.0認証フローの流れ

```
1. ユーザーを認証エンドポイントにリダイレクト
   ↓
2. ユーザーがFitbitアカウントでログイン・承認
   ↓
3. 認可コードがリダイレクトURLに返される
   ↓
4. 認可コードをアクセストークンと交換
   ↓
5. アクセストークンを使用してAPIにアクセス
```

## 1. 認証エンドポイントの構築

### 1.1 認証URLの生成

ユーザーを以下のURLにリダイレクトします：

```
https://www.fitbit.com/oauth2/authorize?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope={SCOPES}
```

#### パラメータ説明

- **response_type**: `code`（認可コードフロー）
- **client_id**: アプリ登録時に取得したClient ID
- **redirect_uri**: アプリ登録時に設定したRedirect URL（URLエンコード必須）
- **scope**: 必要な権限（スペース区切り、URLエンコード必須）

#### スコープ一覧（主要なもの）

- `activity`: アクティビティデータの読み取り
- `heartrate`: 心拍数データの読み取り
- `location`: 位置情報の読み取り
- `nutrition`: 栄養データの読み取り
- `profile`: プロフィール情報の読み取り
- `settings`: 設定情報の読み取り
- `sleep`: 睡眠データの読み取り
- `social`: ソーシャル機能へのアクセス
- `weight`: 体重データの読み取り

**例**: `activity heartrate sleep profile`

### 1.2 実装例（Python）

```python
import urllib.parse

def get_authorization_url(client_id, redirect_uri, scopes):
    base_url = "https://www.fitbit.com/oauth2/authorize"
    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": " ".join(scopes)
    }
    return f"{base_url}?{urllib.parse.urlencode(params)}"

# 使用例
client_id = "YOUR_CLIENT_ID"
redirect_uri = "http://localhost:8888/callback"
scopes = ["activity", "heartrate", "sleep", "profile"]

auth_url = get_authorization_url(client_id, redirect_uri, scopes)
print(f"このURLにアクセスしてください: {auth_url}")
```

## 2. 認可コードの受け取り

### 2.1 コールバック処理

ユーザーが認証・承認すると、設定したRedirect URLに以下の形式でリダイレクトされます：

```
http://localhost:8888/callback?code={AUTHORIZATION_CODE}&state={STATE}
```

#### パラメータ

- **code**: 認可コード（一時的なコード、有効期限は約10分）
- **state**: CSRF対策用のパラメータ（オプション、送信した値がそのまま返る）

### 2.2 実装例（Flask）

```python
from flask import Flask, request, redirect
import urllib.parse

app = Flask(__name__)

@app.route('/callback')
def callback():
    # 認可コードを取得
    auth_code = request.args.get('code')
    state = request.args.get('state')
    
    if not auth_code:
        return "認証に失敗しました", 400
    
    # 認可コードをアクセストークンと交換
    access_token = exchange_code_for_token(auth_code)
    
    return f"認証成功！アクセストークン: {access_token[:20]}..."

# トークン交換関数（次のセクションで実装）
def exchange_code_for_token(auth_code):
    # 実装は次のセクションを参照
    pass
```

## 3. アクセストークンの取得

### 3.1 トークンエンドポイントへのリクエスト

認可コードをアクセストークンと交換するため、以下のエンドポイントにPOSTリクエストを送信します：

**エンドポイント**: `https://api.fitbit.com/oauth2/token`

**リクエストヘッダー**:
```
Content-Type: application/x-www-form-urlencoded
Authorization: Basic {BASE64_ENCODED_CLIENT_CREDENTIALS}
```

**リクエストボディ**:
```
grant_type=authorization_code&code={AUTHORIZATION_CODE}&redirect_uri={REDIRECT_URI}
```

#### Base64エンコード方法

Client IDとClient Secretを `{CLIENT_ID}:{CLIENT_SECRET}` の形式で結合し、Base64エンコードします。

### 3.2 実装例（Python）

```python
import requests
import base64
import urllib.parse

def exchange_code_for_token(auth_code, client_id, client_secret, redirect_uri):
    """
    認可コードをアクセストークンと交換する
    """
    # トークンエンドポイント
    token_url = "https://api.fitbit.com/oauth2/token"
    
    # Basic認証用のヘッダーを作成
    credentials = f"{client_id}:{client_secret}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    
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
        return token_data
    else:
        raise Exception(f"トークン取得に失敗: {response.status_code} - {response.text}")

# 使用例
client_id = "YOUR_CLIENT_ID"
client_secret = "YOUR_CLIENT_SECRET"
redirect_uri = "http://localhost:8888/callback"
auth_code = "取得した認可コード"

token_data = exchange_code_for_token(auth_code, client_id, client_secret, redirect_uri)

print(f"Access Token: {token_data['access_token']}")
print(f"Refresh Token: {token_data['refresh_token']}")
print(f"Expires In: {token_data['expires_in']}秒")
```

### 3.3 レスポンス形式

成功時のレスポンス例：

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiJ9...",
  "expires_in": 28800,
  "refresh_token": "a1b2c3d4e5f6...",
  "scope": "activity heartrate sleep profile",
  "token_type": "Bearer",
  "user_id": "XXXXXX"
}
```

#### レスポンスフィールド

- **access_token**: APIアクセス用のトークン（有効期限: 8時間）
- **refresh_token**: アクセストークンを更新するためのトークン（長期間有効）
- **expires_in**: アクセストークンの有効期限（秒）
- **scope**: 付与された権限
- **token_type**: トークンの種類（通常は "Bearer"）
- **user_id**: FitbitユーザーID

## 4. アクセストークンの使用

### 4.1 APIリクエストの送信

取得したアクセストークンを使用して、Fitbit APIにリクエストを送信します。

**リクエストヘッダー**:
```
Authorization: Bearer {ACCESS_TOKEN}
```

### 4.2 実装例

```python
import requests

def get_user_profile(access_token):
    """
    ユーザーのプロフィール情報を取得
    """
    url = "https://api.fitbit.com/1/user/-/profile.json"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"APIリクエストに失敗: {response.status_code} - {response.text}")

# 使用例
access_token = "取得したアクセストークン"
profile = get_user_profile(access_token)
print(profile)
```

## 5. リフレッシュトークンによる更新

アクセストークンは8時間で期限切れになります。期限切れ後は、リフレッシュトークンを使用して新しいアクセストークンを取得できます。

### 5.1 実装例

```python
def refresh_access_token(refresh_token, client_id, client_secret):
    """
    リフレッシュトークンを使用してアクセストークンを更新
    """
    token_url = "https://api.fitbit.com/oauth2/token"
    
    credentials = f"{client_id}:{client_secret}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {encoded_credentials}"
    }
    
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }
    
    response = requests.post(token_url, headers=headers, data=data)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"トークン更新に失敗: {response.status_code} - {response.text}")

# 使用例
refresh_token = "保存しておいたリフレッシュトークン"
new_token_data = refresh_access_token(refresh_token, client_id, client_secret)
print(f"新しいAccess Token: {new_token_data['access_token']}")
```

## 6. エラーハンドリング

### 6.1 よくあるエラー

- **400 Bad Request**: リクエストパラメータが不正
- **401 Unauthorized**: 認証情報が無効または期限切れ
- **403 Forbidden**: 必要な権限がない
- **429 Too Many Requests**: レート制限に達した

### 6.2 エラーハンドリング例

```python
def safe_api_request(url, access_token):
    """
    エラーハンドリング付きAPIリクエスト
    """
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if response.status_code == 401:
            # トークンが期限切れの可能性
            return {"error": "認証エラー: トークンを更新してください"}
        elif response.status_code == 429:
            # レート制限
            return {"error": "レート制限に達しました。しばらく待ってから再試行してください"}
        else:
            return {"error": f"APIエラー: {e}"}
```

## 参考リンク

- [Fitbit Web API ドキュメント](https://dev.fitbit.com/build/reference/web-api/)
- [OAuth 2.0仕様](https://oauth.net/2/)














