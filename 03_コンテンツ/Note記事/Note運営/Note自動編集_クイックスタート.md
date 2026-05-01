# Note.com 記事編集自動化ツール - クイックスタートガイド

5分で始められる簡易版マニュアルです。詳細は「Note自動編集_詳細マニュアル.md」を参照してください。

---

## 🚀 3ステップで始める

### ステップ1: インストール（2分）

```bash
# このツールのフォルダに移動（重要）
cd "/Users/ishiinobuyuki/Documents/Obsidian Vault"

# パッケージをインストール
pip3 install -r requirements.txt

# ブラウザをインストール
playwright install chromium
```

### ステップ2: 設定ファイルを作成（1分）

```bash
# .envファイルを作成
cp .env.example .env
```

`.env`ファイルを**エディタで開いて**、以下を入力（**ターミナルに貼り付けて実行しない**）：

```bash
# 例：macOSならこれで編集できます
nano .env
```

```env
NOTE_EMAIL=あなたのメールアドレス
NOTE_PASSWORD=あなたのパスワード
NOTE_EDIT_URL=https://note.com/ユーザー名/n/記事ID/edit
NOTE_OLD_TEXT=削除したいテキスト
NOTE_NEW_TEXT=新しいテキスト
NOTE_LINK_URL=https://リンク先URL
NOTE_HEADLESS=false
```

### ステップ3: 実行（30秒）

```bash
python3 note_editor.py
```

ブラウザが開いて、自動的に編集が実行されます！

---

## 📝 編集URLの取得方法

1. Note.comにログイン
2. 編集したい記事を開く
3. 右上の「編集」ボタンをクリック
4. ブラウザのアドレスバーのURLをコピー
   - 例: `https://note.com/username/n/n1234567890/edit`

---

## ⚠️ よくあるエラーと対処法

### エラー: 「ModuleNotFoundError」

```bash
pip3 install playwright python-dotenv
playwright install chromium
```

### エラー: 「ログインに失敗」

1. `.env`のメールアドレスとパスワードを確認
2. クッキーファイルを削除: `rm note_cookies.json`
3. 再実行

### エラー: 「エディタが見つかりません」

- 編集URLが正しいか確認（`/edit`で終わっているか）
- 記事の編集権限があるか確認

---

## 💡 使用例

### 例: リンクを更新

```env
NOTE_OLD_TEXT=詳細はこちら
NOTE_NEW_TEXT=詳細はこちら
NOTE_LINK_URL=https://new-link.com
```

### 例: テキストを置換

```env
NOTE_OLD_TEXT=旧サービス名
NOTE_NEW_TEXT=新サービス名
NOTE_LINK_URL=
```

### 例: 複数のURLを削除

```env
# 改行区切りで複数のURLを指定
NOTE_OLD_TEXT=https://note.com/growthfix_corp/m/m300254967727
https://utage-system.com/p/baep8BHALGvn
NOTE_NEW_TEXT=
NOTE_LINK_URL=
```

---

## 📚 詳細情報

- **詳細マニュアル**: `Note自動編集_詳細マニュアル.md`
- **README**: `README_note_editor.md`

---

**トラブルが発生したら**: ブラウザを表示モード（`NOTE_HEADLESS=false`）にして、実際の動作を確認してください。
