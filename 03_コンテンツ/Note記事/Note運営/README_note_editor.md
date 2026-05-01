# Note.com 記事編集自動化ツール

Playwrightを使用してNote.comの記事編集を自動化するPythonスクリプトです。

## 機能

- ✅ Note.comへの自動ログイン（クッキー保存対応）
- ✅ 指定記事の編集ページへのアクセス
- ✅ 本文内の特定文字列の検索と削除
- ✅ 新しいテキストの入力とリンク設定
- ✅ 公開設定と保存の自動実行

## セットアップ

### 1. 必要なパッケージのインストール

```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. 環境変数の設定

`.env.example`をコピーして`.env`ファイルを作成し、必要な情報を入力してください。

```bash
cp .env.example .env
```

`.env`ファイルの内容：

```env
# Note.com 認証情報
NOTE_EMAIL=your_email@example.com
NOTE_PASSWORD=your_password

# 記事編集設定
NOTE_EDIT_URL=https://note.com/username/n/nnnnnnnnnnnn/edit
NOTE_OLD_TEXT=[消したい文字列]
NOTE_NEW_TEXT=[新しいテキスト]
NOTE_LINK_URL=https://example.com

# 実行設定（trueでブラウザを非表示、falseで表示）
NOTE_HEADLESS=false
```

## 使用方法

### 方法1: 環境変数を使用

`.env`ファイルに設定を記入した後：

```bash
python note_editor.py
```

### 方法2: コマンドライン引数を使用

```bash
python note_editor.py <編集URL> <削除テキスト> <新規テキスト> [リンクURL]
```

例：

```bash
python note_editor.py \
  "https://note.com/username/n/nnnnnnnnnnnn/edit" \
  "古いテキスト" \
  "新しいテキスト" \
  "https://example.com"
```

### 方法3: Pythonスクリプトから直接使用

```python
import asyncio
from note_editor import NoteEditor

async def main():
    async with NoteEditor(headless=False) as editor:
        # ログイン
        await editor.login(
            email="your_email@example.com",
            password="your_password"
        )
        
        # 記事編集
        await editor.edit_article(
            edit_url="https://note.com/username/n/nnnnnnnnnnnn/edit",
            old_text="[消したい文字列]",
            new_text="[新しいテキスト]",
            link_url="https://example.com"
        )

asyncio.run(main())
```

## クッキーの保存

初回ログイン後、クッキーは自動的に`note_cookies.json`に保存されます。
次回以降は、このクッキーを使用して自動ログインします。

**注意**: クッキーファイルには認証情報が含まれます。Gitにコミットしないよう注意してください。

## トラブルシューティング

### ログインに失敗する

- メールアドレスとパスワードが正しいか確認
- 2段階認証が有効な場合は、一時的に無効化するか、別の方法を検討
- クッキーファイルを削除して再ログインを試す

```bash
rm note_cookies.json
```

### エディタが見つからない

- 編集URLが正しいか確認（`/edit`で終わっているか）
- 記事の編集権限があるか確認
- ページの読み込みを待つ時間を増やす（`note_editor.py`の`wait_until`を調整）

### テキストが見つからない

- 削除したいテキストが正確に一致しているか確認（空白や改行に注意）
- 大文字小文字が一致しているか確認
- スクリプト実行時にブラウザを表示モード（`NOTE_HEADLESS=false`）にして、実際の動作を確認

### リンクが設定できない

- Note.comのエディタのUIが変更されている可能性があります
- ブラウザを表示モードにして、手動でリンクを設定する手順を確認
- 必要に応じて、スクリプトのセレクターを調整

## セキュリティに関する注意

- `.env`ファイルと`note_cookies.json`は**絶対にGitにコミットしない**でください
- `.gitignore`に以下を追加することを推奨：

```
.env
note_cookies.json
*.cookies
```

## ライセンス

このスクリプトは自由に使用・改変できます。

## 更新履歴

- v1.0.0: 初回リリース
  - 基本的な編集機能
  - クッキー保存機能
  - リンク設定機能
