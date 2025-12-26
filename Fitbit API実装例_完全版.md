# Fitbit API実装例 - 完全版

## 概要

このファイルには、Fitbit APIを使用するための完全な実装例（Python）が含まれています。コピー&ペーストで使用できる実用的なコードです。

## 必要なライブラリ

```bash
pip install requests flask
```

## 完全な実装コード

### fitbit_auth.py - 認証モジュール

```python
"""
Fitbit OAuth 2.0認証モジュール
"""
import requests
import base64
import urllib.parse
from typing import Dict, Optional


class FitbitAuth:
    """Fitbit OAuth 2.0認証を管理するクラス"""
    
    AUTHORIZE_URL = "https://www.fitbit.com/oauth2/authorize"
    TOKEN_URL = "https://api.fitbit.com/oauth2/token"
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        """
        初期化
        
        Args:
            client_id: FitbitアプリのClient ID
            client_secret: FitbitアプリのClient Secret
            redirect_uri: コールバックURL
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
    
    def get_authorization_url(self, scopes: list, state: Optional[str] = None) -> str:
        """
        認証URLを生成
        
        Args:
            scopes: 必要な権限のリスト（例: ['activity', 'heartrate', 'sleep']）
            state: CSRF対策用のパラメータ（オプション）
        
        Returns:
            認証URL
        """
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": " ".join(scopes)
        }
        
        if state:
            params["state"] = state
        
        return f"{self.AUTHORIZE_URL}?{urllib.parse.urlencode(params)}"
    
    def _get_basic_auth_header(self) -> str:
        """Basic認証用のヘッダーを生成"""
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded}"
    
    def exchange_code_for_token(self, auth_code: str) -> Dict:
        """
        認可コードをアクセストークンと交換
        
        Args:
            auth_code: 認可コード
        
        Returns:
            トークンデータ（access_token, refresh_token等を含む辞書）
        
        Raises:
            Exception: トークン取得に失敗した場合
        """
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": self._get_basic_auth_header()
        }
        
        data = {
            "grant_type": "authorization_code",
            "code": auth_code,
            "redirect_uri": self.redirect_uri
        }
        
        response = requests.post(self.TOKEN_URL, headers=headers, data=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(
                f"トークン取得に失敗しました: {response.status_code} - {response.text}"
            )
    
    def refresh_token(self, refresh_token: str) -> Dict:
        """
        リフレッシュトークンを使用してアクセストークンを更新
        
        Args:
            refresh_token: リフレッシュトークン
        
        Returns:
            新しいトークンデータ
        
        Raises:
            Exception: トークン更新に失敗した場合
        """
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": self._get_basic_auth_header()
        }
        
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }
        
        response = requests.post(self.TOKEN_URL, headers=headers, data=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(
                f"トークン更新に失敗しました: {response.status_code} - {response.text}"
            )
```

### fitbit_api.py - APIクライアント

```python
"""
Fitbit APIクライアント
"""
import requests
from typing import Dict, Optional
from datetime import datetime, timedelta


class FitbitAPI:
    """Fitbit APIにアクセスするためのクライアントクラス"""
    
    BASE_URL = "https://api.fitbit.com"
    
    def __init__(self, access_token: str):
        """
        初期化
        
        Args:
            access_token: アクセストークン
        """
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {access_token}"
        }
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """
        APIリクエストを送信
        
        Args:
            method: HTTPメソッド（GET, POST等）
            endpoint: APIエンドポイント（例: '/1/user/-/profile.json'）
            **kwargs: requestsの追加パラメータ
        
        Returns:
            APIレスポンス（JSON）
        
        Raises:
            Exception: リクエストに失敗した場合
        """
        url = f"{self.BASE_URL}{endpoint}"
        response = requests.request(method, url, headers=self.headers, **kwargs)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            raise Exception("認証エラー: トークンが無効または期限切れです")
        elif response.status_code == 429:
            raise Exception("レート制限に達しました。しばらく待ってから再試行してください")
        else:
            raise Exception(
                f"APIリクエストに失敗しました: {response.status_code} - {response.text}"
            )
    
    def get_user_profile(self) -> Dict:
        """ユーザーのプロフィール情報を取得"""
        return self._make_request("GET", "/1/user/-/profile.json")
    
    def get_activities(self, date: Optional[str] = None) -> Dict:
        """
        アクティビティデータを取得
        
        Args:
            date: 日付（YYYY-MM-DD形式）。Noneの場合は今日
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        return self._make_request("GET", f"/1/user/-/activities/date/{date}.json")
    
    def get_heartrate(self, date: Optional[str] = None) -> Dict:
        """
        心拍数データを取得
        
        Args:
            date: 日付（YYYY-MM-DD形式）。Noneの場合は今日
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        return self._make_request("GET", f"/1/user/-/heart/date/{date}.json")
    
    def get_sleep(self, date: Optional[str] = None) -> Dict:
        """
        睡眠データを取得
        
        Args:
            date: 日付（YYYY-MM-DD形式）。Noneの場合は今日
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        return self._make_request("GET", f"/1/user/-/sleep/date/{date}.json")
    
    def get_weight(self, date: Optional[str] = None) -> Dict:
        """
        体重データを取得
        
        Args:
            date: 日付（YYYY-MM-DD形式）。Noneの場合は今日
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        return self._make_request("GET", f"/1/user/-/body/log/weight/date/{date}.json")
    
    def get_activity_summary(self, start_date: str, end_date: str) -> Dict:
        """
        期間内のアクティビティサマリーを取得
        
        Args:
            start_date: 開始日（YYYY-MM-DD形式）
            end_date: 終了日（YYYY-MM-DD形式）
        """
        return self._make_request(
            "GET",
            f"/1/user/-/activities/list.json?afterDate={start_date}&sort=asc&limit=20&offset=0"
        )
```

### app.py - Flaskアプリケーション例

```python
"""
Fitbit認証フローを実装したFlaskアプリケーション例
"""
from flask import Flask, request, redirect, session, jsonify
from fitbit_auth import FitbitAuth
from fitbit_api import FitbitAPI
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # セッション管理用の秘密鍵

# Fitbitアプリの認証情報（環境変数から取得することを推奨）
CLIENT_ID = os.getenv("FITBIT_CLIENT_ID", "YOUR_CLIENT_ID")
CLIENT_SECRET = os.getenv("FITBIT_CLIENT_SECRET", "YOUR_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8888/callback"

# Fitbit認証インスタンス
fitbit_auth = FitbitAuth(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)


@app.route('/')
def index():
    """ホームページ"""
    return """
    <h1>Fitbit API デモ</h1>
    <p><a href="/auth">Fitbitで認証する</a></p>
    """


@app.route('/auth')
def auth():
    """認証開始"""
    scopes = ['activity', 'heartrate', 'sleep', 'profile']
    auth_url = fitbit_auth.get_authorization_url(scopes)
    return redirect(auth_url)


@app.route('/callback')
def callback():
    """認証コールバック"""
    auth_code = request.args.get('code')
    error = request.args.get('error')
    
    if error:
        return f"認証エラー: {error}", 400
    
    if not auth_code:
        return "認可コードが取得できませんでした", 400
    
    try:
        # 認可コードをアクセストークンと交換
        token_data = fitbit_auth.exchange_code_for_token(auth_code)
        
        # セッションに保存（本番環境ではデータベース等に保存）
        session['access_token'] = token_data['access_token']
        session['refresh_token'] = token_data['refresh_token']
        session['user_id'] = token_data.get('user_id')
        
        return redirect('/dashboard')
    except Exception as e:
        return f"エラーが発生しました: {str(e)}", 500


@app.route('/dashboard')
def dashboard():
    """ダッシュボード（データ表示）"""
    access_token = session.get('access_token')
    
    if not access_token:
        return redirect('/auth')
    
    try:
        api = FitbitAPI(access_token)
        
        # 各種データを取得
        profile = api.get_user_profile()
        activities = api.get_activities()
        heartrate = api.get_heartrate()
        sleep = api.get_sleep()
        
        return jsonify({
            "profile": profile,
            "activities": activities,
            "heartrate": heartrate,
            "sleep": sleep
        })
    except Exception as e:
        return f"APIエラー: {str(e)}", 500


@app.route('/refresh')
def refresh():
    """トークンを更新"""
    refresh_token = session.get('refresh_token')
    
    if not refresh_token:
        return "リフレッシュトークンがありません", 400
    
    try:
        token_data = fitbit_auth.refresh_token(refresh_token)
        session['access_token'] = token_data['access_token']
        session['refresh_token'] = token_data['refresh_token']
        
        return jsonify({"message": "トークンを更新しました", "token_data": token_data})
    except Exception as e:
        return f"トークン更新エラー: {str(e)}", 500


if __name__ == '__main__':
    app.run(port=8888, debug=True)
```

## 使用方法

### 1. 環境変数の設定

```bash
export FITBIT_CLIENT_ID="your_client_id"
export FITBIT_CLIENT_SECRET="your_client_secret"
```

### 2. アプリケーションの起動

```bash
python app.py
```

### 3. ブラウザでアクセス

1. `http://localhost:8888` にアクセス
2. 「Fitbitで認証する」をクリック
3. Fitbitアカウントでログイン・承認
4. 自動的にダッシュボードにリダイレクトされ、データが表示される

## 注意事項

1. **セキュリティ**: 本番環境では、Client Secretやトークンは環境変数や安全な設定ファイルから読み込むこと
2. **トークン管理**: アクセストークンは8時間で期限切れになるため、リフレッシュトークンで更新する必要がある
3. **レート制限**: Fitbit APIにはレート制限があるため、過度なリクエストは避けること
4. **エラーハンドリング**: 本番環境では、より詳細なエラーハンドリングを実装すること

## 参考リンク

- [Fitbit Web API ドキュメント](https://dev.fitbit.com/build/reference/web-api/)
- [Fitbit API Explorer](https://dev.fitbit.com/build/reference/web-api/explore/)














