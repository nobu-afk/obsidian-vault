# Fitbit API トラブルシューティングガイド

## よくある問題と解決方法

### 1. 認証関連のエラー

#### エラー: "invalid_client" または "invalid_client_secret"

**原因**: Client IDまたはClient Secretが間違っている

**解決方法**:
- Fitbit開発者ポータルで正しいClient IDとClient Secretを確認
- Base64エンコードが正しく行われているか確認
- 環境変数や設定ファイルから正しく読み込まれているか確認

#### エラー: "invalid_grant" または "invalid_code"

**原因**: 
- 認可コードが既に使用されている（認可コードは1回しか使用できない）
- 認可コードの有効期限（約10分）が切れている
- Redirect URIが登録時のものと一致していない

**解決方法**:
- 新しい認証フローを開始し、新しい認可コードを取得
- Redirect URIがアプリ登録時のものと完全に一致しているか確認（末尾のスラッシュも含めて）

#### エラー: "redirect_uri_mismatch"

**原因**: リクエストで使用しているRedirect URIが、アプリ登録時に設定したものと一致していない

**解決方法**:
- Fitbit開発者ポータルで登録されているRedirect URIを確認
- 認証URL生成時とトークン交換時の両方で同じRedirect URIを使用しているか確認
- URLエンコードが正しく行われているか確認

### 2. トークン関連のエラー

#### エラー: 401 Unauthorized

**原因**: 
- アクセストークンが期限切れ（8時間で期限切れ）
- アクセストークンが無効

**解決方法**:
- リフレッシュトークンを使用して新しいアクセストークンを取得
- 認証フローを最初からやり直す

#### エラー: "invalid_token" または "expired_token"

**原因**: トークンが無効または期限切れ

**解決方法**:
```python
# リフレッシュトークンで更新
try:
    new_token_data = fitbit_auth.refresh_token(refresh_token)
    access_token = new_token_data['access_token']
except Exception as e:
    # リフレッシュも失敗した場合は再認証が必要
    print("再認証が必要です")
```

### 3. APIリクエスト関連のエラー

#### エラー: 403 Forbidden

**原因**: 
- 必要なスコープ（権限）が付与されていない
- リクエストしているデータにアクセスする権限がない

**解決方法**:
- 認証時に必要なスコープを要求しているか確認
- Fitbit開発者ポータルでアプリの権限設定を確認
- ユーザーが承認時に必要な権限を許可したか確認

#### エラー: 429 Too Many Requests

**原因**: APIのレート制限に達した

**解決方法**:
- リクエスト頻度を減らす
- レート制限の詳細を確認:
  - 150リクエスト/時間/ユーザー
  - 150リクエスト/時間/アプリケーション
- エラーレスポンスの`Retry-After`ヘッダーを確認し、指定された時間後に再試行

#### エラー: 404 Not Found

**原因**: 
- APIエンドポイントのURLが間違っている
- リソースが存在しない（例: 指定した日付のデータがない）

**解決方法**:
- APIエンドポイントのURLを確認
- [Fitbit API ドキュメント](https://dev.fitbit.com/build/reference/web-api/)で正しいエンドポイントを確認
- データが存在する日付を指定しているか確認

### 4. 実装関連のエラー

#### エラー: "ModuleNotFoundError: No module named 'requests'"

**原因**: 必要なPythonパッケージがインストールされていない

**解決方法**:
```bash
pip install requests flask
```

#### エラー: SSL証明書エラー

**原因**: SSL証明書の検証に失敗

**解決方法**:
- 本番環境では`verify=True`を維持（デフォルト）
- 開発環境で一時的に無効化する場合（非推奨）:
```python
import requests
requests.packages.urllib3.disable_warnings()
response = requests.get(url, verify=False)
```

### 5. データ取得関連の問題

#### 問題: データが取得できない（空のレスポンス）

**原因**: 
- 指定した日付にデータが存在しない
- デバイスが同期されていない

**解決方法**:
- Fitbitアプリでデバイスが同期されているか確認
- 過去の日付で試す
- エラーレスポンスの内容を確認

#### 問題: 日付形式のエラー

**原因**: 日付の形式が正しくない

**解決方法**:
- Fitbit APIは`YYYY-MM-DD`形式を要求
- 例: `2024-01-15`（正しい）、`2024/01/15`（間違い）

## デバッグのヒント

### 1. リクエストとレスポンスのログ出力

```python
import logging

logging.basicConfig(level=logging.DEBUG)

# requestsライブラリのログを有効化
import http.client
http.client.HTTPConnection.debuglevel = 1
```

### 2. レスポンスの詳細確認

```python
response = requests.get(url, headers=headers)
print(f"Status Code: {response.status_code}")
print(f"Headers: {response.headers}")
print(f"Body: {response.text}")
```

### 3. トークンの状態確認

```python
# トークンが有効かどうかテスト
try:
    api = FitbitAPI(access_token)
    profile = api.get_user_profile()
    print("トークンは有効です")
except Exception as e:
    print(f"トークンが無効です: {e}")
```

## チェックリスト

認証フローで問題が発生した場合、以下を確認してください:

- [ ] Client IDとClient Secretが正しいか
- [ ] Redirect URIがアプリ登録時のものと完全に一致しているか
- [ ] 必要なスコープを要求しているか
- [ ] 認可コードが有効期限内（10分以内）か
- [ ] 認可コードを複数回使用していないか
- [ ] Base64エンコードが正しく行われているか
- [ ] リクエストヘッダーが正しく設定されているか
- [ ] HTTPSを使用しているか（本番環境）

## サポートリソース

- [Fitbit開発者フォーラム](https://community.fitbit.com/t5/Web-API-Development/bd-p/web-api)
- [Fitbit API ドキュメント](https://dev.fitbit.com/build/reference/web-api/)
- [OAuth 2.0仕様](https://oauth.net/2/)

## よくある質問（FAQ）

### Q: アクセストークンはどのくらいの期間有効ですか？

A: アクセストークンは8時間有効です。期限切れ後はリフレッシュトークンを使用して更新する必要があります。

### Q: リフレッシュトークンはどのくらいの期間有効ですか？

A: リフレッシュトークンは長期間有効ですが、ユーザーがアプリの権限を取り消した場合や、一定期間使用されなかった場合は無効になることがあります。

### Q: 複数のユーザーのデータを取得できますか？

A: 各ユーザーが個別に認証・承認する必要があります。1つのアプリで複数のユーザーのトークンを管理できますが、各ユーザーごとに認証フローを実行する必要があります。

### Q: レート制限を超えた場合はどうなりますか？

A: 429エラーが返され、`Retry-After`ヘッダーに再試行可能な時間が示されます。その時間が経過するまで待ってから再試行してください。














