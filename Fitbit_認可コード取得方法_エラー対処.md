# Fitbit 認可コード取得方法 - エラー対処ガイド

## エラーについて

`ERR_CONNECTION_REFUSED` エラーは、ローカルサーバーが起動していないために発生しますが、**これは問題ありません**。

リダイレクトされたURLのアドレスバーに認可コードが含まれているので、そこから取得できます。

## 方法1: URLバーから認可コードを取得する（最も簡単）

### 手順

1. **認証URLをブラウザで開く**
   ```
   https://www.fitbit.com/oauth2/authorize?response_type=code&client_id=23TMWD&redirect_uri=http://localhost:8888&scope=activity%20heartrate%20sleep%20profile
   ```

2. **Fitbitでログイン・承認する**

3. **リダイレクト後のURLを確認**
   - エラーページが表示されますが、**URLバーを見てください**
   - 以下のような形式になっています：
     ```
     http://localhost:8888/?code=XXXXXX&state=YYYYYY
     ```
   - または：
     ```
     http://localhost:8888/?error=access_denied
     ```

4. **認可コードをコピー**
   - `code=` の後の値（`XXXXXX`の部分）が認可コードです
   - このコードをコピーして、次のステップで使用します

### 注意点

- 認可コードは約10分間のみ有効です
- エラーページが表示されても、URLバーに認可コードが含まれていれば問題ありません

## 方法2: 簡単なローカルサーバーを起動する（推奨）

ローカルサーバーを起動すると、認可コードを自動的に取得・表示できます。

### Pythonで簡単なサーバーを起動

以下のPythonスクリプトを `fitbit_callback_server.py` として保存してください：

```python
"""
Fitbit認証コールバック用の簡単なサーバー
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import webbrowser

class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """GETリクエストを処理"""
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        
        # 認可コードを取得
        if 'code' in query_params:
            auth_code = query_params['code'][0]
            
            # 成功ページを表示
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Fitbit認証成功</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        max-width: 600px;
                        margin: 50px auto;
                        padding: 20px;
                        background-color: #f5f5f5;
                    }}
                    .success {{
                        background-color: #4CAF50;
                        color: white;
                        padding: 20px;
                        border-radius: 5px;
                        margin-bottom: 20px;
                    }}
                    .code-box {{
                        background-color: #fff;
                        padding: 15px;
                        border: 2px solid #4CAF50;
                        border-radius: 5px;
                        font-family: monospace;
                        word-break: break-all;
                        margin: 20px 0;
                    }}
                    .copy-btn {{
                        background-color: #2196F3;
                        color: white;
                        padding: 10px 20px;
                        border: none;
                        border-radius: 5px;
                        cursor: pointer;
                        font-size: 16px;
                    }}
                    .copy-btn:hover {{
                        background-color: #0b7dda;
                    }}
                </style>
            </head>
            <body>
                <div class="success">
                    <h1>✅ 認証成功！</h1>
                    <p>認可コードを取得しました。以下のコードをコピーして、次のステップで使用してください。</p>
                </div>
                
                <h2>認可コード:</h2>
                <div class="code-box" id="auth-code">{auth_code}</div>
                
                <button class="copy-btn" onclick="copyCode()">コードをコピー</button>
                
                <script>
                    function copyCode() {{
                        const code = document.getElementById('auth-code').textContent;
                        navigator.clipboard.writeText(code).then(function() {{
                            alert('認可コードをコピーしました！');
                        }});
                    }}
                </script>
                
                <hr>
                <p><strong>次のステップ:</strong></p>
                <ol>
                    <li>上記の認可コードをコピー</li>
                    <li>Pythonスクリプトでアクセストークンを取得</li>
                </ol>
            </body>
            </html>
            """
            
            self.wfile.write(html.encode('utf-8'))
            
            # コンソールにも表示
            print("\n" + "=" * 60)
            print("✅ 認可コードを取得しました！")
            print("=" * 60)
            print(f"\n認可コード: {auth_code}\n")
            print("このコードをコピーして、次のステップで使用してください。")
            print("=" * 60 + "\n")
            
        elif 'error' in query_params:
            # エラーページを表示
            error = query_params['error'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Fitbit認証エラー</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        max-width: 600px;
                        margin: 50px auto;
                        padding: 20px;
                        background-color: #f5f5f5;
                    }}
                    .error {{
                        background-color: #f44336;
                        color: white;
                        padding: 20px;
                        border-radius: 5px;
                    }}
                </style>
            </head>
            <body>
                <div class="error">
                    <h1>❌ 認証エラー</h1>
                    <p>エラー: {error}</p>
                    <p>もう一度認証を試してください。</p>
                </div>
            </body>
            </html>
            """
            
            self.wfile.write(html.encode('utf-8'))
            print(f"\n❌ 認証エラー: {error}\n")
        else:
            # その他のリクエスト
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'Fitbit認証コールバックサーバーが起動しています。')
    
    def log_message(self, format, *args):
        """ログメッセージを抑制（オプション）"""
        pass  # ログを表示しない場合はコメントアウト


def main():
    """サーバーを起動"""
    port = 8888
    server_address = ('', port)
    httpd = HTTPServer(server_address, CallbackHandler)
    
    print("=" * 60)
    print("🚀 Fitbit認証コールバックサーバーを起動しました")
    print("=" * 60)
    print(f"\nサーバーURL: http://localhost:{port}")
    print("\n以下の認証URLをブラウザで開いてください:")
    print("\nhttps://www.fitbit.com/oauth2/authorize?response_type=code&client_id=23TMWD&redirect_uri=http://localhost:8888&scope=activity%20heartrate%20sleep%20profile")
    print("\n" + "=" * 60)
    print("サーバーを停止するには Ctrl+C を押してください")
    print("=" * 60 + "\n")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\nサーバーを停止しました。")
        httpd.server_close()


if __name__ == '__main__':
    main()
```

### 実行方法

1. **サーバーを起動**
   ```bash
   python fitbit_callback_server.py
   ```

2. **認証URLをブラウザで開く**
   - サーバー起動時に表示されるURLをコピー
   - または、以下のURLを開く：
     ```
     https://www.fitbit.com/oauth2/authorize?response_type=code&client_id=23TMWD&redirect_uri=http://localhost:8888&scope=activity%20heartrate%20sleep%20profile
     ```

3. **Fitbitでログイン・承認**

4. **認可コードを取得**
   - ブラウザに成功ページが表示され、認可コードが表示されます
   - 「コードをコピー」ボタンでコピーできます
   - ターミナルにも認可コードが表示されます

## 方法3: ワンライナーでサーバーを起動（最も簡単）

Python 3の場合：

```bash
python3 -m http.server 8888
```

ただし、この方法では認可コードを自動表示できません。URLバーから取得する必要があります。

## 次のステップ: アクセストークンを取得

認可コードを取得したら、以下のPythonスクリプトでアクセストークンを取得します：

```python
import requests
import base64

# 認証情報
CLIENT_ID = "23TMWD"
CLIENT_SECRET = "db52ab48f6b791dec60d7cf8169bda6c"
REDIRECT_URI = "http://localhost:8888"

# 認可コードを入力（上記の方法で取得したコード）
auth_code = input("認可コードを入力してください: ").strip()

# Basic認証用のヘッダーを作成
credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
encoded_credentials = base64.b64encode(credentials.encode()).decode()

# トークンエンドポイントにリクエスト
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

print("\nアクセストークンを取得中...")
response = requests.post(token_url, headers=headers, data=data)

if response.status_code == 200:
    token_data = response.json()
    print("\n✅ アクセストークンの取得に成功しました！")
    print(f"\nAccess Token: {token_data['access_token']}")
    print(f"Refresh Token: {token_data['refresh_token']}")
    print(f"有効期限: {token_data['expires_in']}秒（約{token_data['expires_in']/3600:.1f}時間）")
    print(f"ユーザーID: {token_data.get('user_id', 'N/A')}")
    
    # トークンをファイルに保存
    with open("fitbit_tokens.txt", "w") as f:
        f.write(f"Access Token: {token_data['access_token']}\n")
        f.write(f"Refresh Token: {token_data['refresh_token']}\n")
        f.write(f"User ID: {token_data.get('user_id', 'N/A')}\n")
        f.write(f"Expires In: {token_data['expires_in']}秒\n")
    print("\n💾 トークンを fitbit_tokens.txt に保存しました")
else:
    print(f"\n❌ エラーが発生しました: {response.status_code}")
    print(f"レスポンス: {response.text}")
```

## まとめ

- **方法1（URLバーから取得）**: 最も簡単。エラーページが表示されても、URLバーから認可コードをコピーできます
- **方法2（ローカルサーバー起動）**: 推奨。認可コードが自動的に表示され、コピーも簡単です
- **方法3（ワンライナー）**: 簡単ですが、URLバーから取得する必要があります

どの方法でも認可コードは取得できます。お好みの方法をお選びください！














