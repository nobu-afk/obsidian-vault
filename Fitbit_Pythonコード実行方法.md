# Fitbit Pythonコード実行方法

## 認可コードを取得しました！

取得した認可コード: `ef0f276ba1c6bd8ddb992c905dac7cd1cf1d51ab`

## Pythonコードの実行方法

### 方法1: スクリプトファイルを実行する（推奨）

#### ステップ1: Pythonファイルを作成

`fitbit_get_token.py` というファイルが既に作成されています。このファイルを使用します。

#### ステップ2: ターミナルを開く

1. **macOSの場合**:
   - `Command + Space` でSpotlight検索を開く
   - 「ターミナル」または「Terminal」と入力してEnter
   - または、Finder > アプリケーション > ユーティリティ > ターミナル

2. **Windowsの場合**:
   - `Windows + R` で「ファイル名を指定して実行」を開く
   - `cmd` と入力してEnter
   - または、スタートメニューから「コマンドプロンプト」を検索

#### ステップ3: ファイルがあるディレクトリに移動

ターミナルで以下のコマンドを実行：

```bash
cd "/Users/ishiinobuyuki/Documents/Obsidian Vault"
```

または、Finderでファイルを右クリックして「ターミナルで開く」を選択することもできます。

#### ステップ4: 必要なライブラリをインストール（初回のみ）

```bash
pip install requests
```

または、Python 3の場合：

```bash
pip3 install requests
```

#### ステップ5: スクリプトを実行

```bash
python fitbit_get_token.py
```

または、Python 3の場合：

```bash
python3 fitbit_get_token.py
```

#### ステップ6: 認可コードを入力

プロンプトが表示されたら、取得した認可コードを入力：

```
認可コードを入力してください: ef0f276ba1c6bd8ddb992c905dac7cd1cf1d51ab
```

Enterキーを押すと、アクセストークンが取得されます。

### 方法2: Python対話モードで実行する

#### ステップ1: Pythonを起動

ターミナルで以下を実行：

```bash
python
```

または：

```bash
python3
```

#### ステップ2: コードを1行ずつ実行

Python対話モード（`>>>` プロンプト）で、以下のコードを1行ずつコピー&ペーストして実行：

```python
import requests
import base64

CLIENT_ID = "23TMWD"
CLIENT_SECRET = "db52ab48f6b791dec60d7cf8169bda6c"
REDIRECT_URI = "http://localhost:8888"
auth_code = "ef0f276ba1c6bd8ddb992c905dac7cd1cf1d51ab"

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
    token_data = response.json()
    print("✅ 成功！")
    print(f"Access Token: {token_data['access_token']}")
    print(f"Refresh Token: {token_data['refresh_token']}")
else:
    print(f"❌ エラー: {response.status_code}")
    print(response.text)
```

### 方法3: Jupyter Notebookで実行する

Jupyter Notebookを使用している場合：

1. 新しいノートブックを作成
2. 上記のコードをセルに貼り付け
3. `Shift + Enter` で実行

## 実行結果

成功すると、以下のような出力が表示されます：

```
============================================================
アクセストークンを取得中...
============================================================

✅ アクセストークンの取得に成功しました！
============================================================

📝 トークン情報:
  Access Token: eyJhbGciOiJIUzI1NiJ9...
  Refresh Token: a1b2c3d4e5f6...
  有効期限: 28800秒（約8.0時間）
  ユーザーID: XXXXXX
  スコープ: activity heartrate sleep profile

💾 トークンを fitbit_tokens.txt に保存しました
============================================================

🎉 これでFitbit APIを使用する準備が整いました！
```

## トラブルシューティング

### エラー: `pip: command not found`

**解決方法**:
- `pip3` を試す
- または、`python -m pip install requests` を実行

### エラー: `python: command not found`

**解決方法**:
- `python3` を試す
- Pythonがインストールされているか確認: `python3 --version`

### エラー: `ModuleNotFoundError: No module named 'requests'`

**解決方法**:
```bash
pip install requests
```

または：

```bash
pip3 install requests
```

### エラー: 認可コードが無効

**原因**: 
- 認可コードは約10分で期限切れになります
- 既に使用済みのコードは再度使用できません

**解決方法**:
- 再度認証URLを開いて、新しい認可コードを取得してください

## 次のステップ

アクセストークンを取得できたら、以下のファイルを参照してください：

- `Fitbit API実装例_完全版.md` - APIを使用してデータを取得する方法
- `Fitbit API_トラブルシューティング.md` - エラーが発生した場合の対処法

## クイックスタート（コピー&ペースト用）

ターミナルで以下を実行：

```bash
cd "/Users/ishiinobuyuki/Documents/Obsidian Vault"
pip3 install requests
python3 fitbit_get_token.py
```

認可コードを入力：
```
ef0f276ba1c6bd8ddb992c905dac7cd1cf1d51ab
```

Enterキーを押すと完了です！














