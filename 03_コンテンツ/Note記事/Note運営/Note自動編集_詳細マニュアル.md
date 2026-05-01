# Note.com 記事編集自動化ツール - 詳細マニュアル

このマニュアルでは、Note.comの記事編集を自動化するツールの使い方を、初心者でも理解できるように詳しく説明します。

---

## 📋 目次

1. [事前準備](#事前準備)
2. [インストール手順](#インストール手順)
3. [設定ファイルの準備](#設定ファイルの準備)
4. [使い方（3つの方法）](#使い方3つの方法)
5. [実際の使用例](#実際の使用例)
6. [トラブルシューティング](#トラブルシューティング)
7. [よくある質問（FAQ）](#よくある質問faq)

---

## 事前準備

### 必要なもの

- **Python 3.8以上**がインストールされていること
- **Note.comのアカウント**を持っていること
- **編集したい記事の編集URL**を用意すること
- **ターミナル（コマンドライン）**が使えること

### Pythonのバージョン確認

ターミナルで以下のコマンドを実行して、Pythonがインストールされているか確認します：

```bash
python3 --version
```

または

```bash
python --version
```

**出力例**: `Python 3.9.7` のように表示されればOKです。

もしPythonがインストールされていない場合は、[Python公式サイト](https://www.python.org/downloads/)からダウンロードしてインストールしてください。

---

## インストール手順

### ステップ1: プロジェクトフォルダに移動

ターミナルで、このツールのファイルがあるフォルダに移動します。

```bash
cd "/Users/ishiinobuyuki/Documents/Obsidian Vault"
```

### ステップ2: 必要なパッケージをインストール

以下のコマンドを順番に実行します：

```bash
# 1. Pythonパッケージをインストール
pip3 install -r requirements.txt

# または pip を使う場合
pip install -r requirements.txt
```

**よくあるミス**: `requirements.txt` の `r` と `e` の間にスペースが入って `r equirements.txt` になっていると、\n`No such file or directory: 'r equirements.txt'` が出ます。スペースなしで `requirements.txt` と入力してください。

**もう1つの注意**: `cd "/Users/ishiinobuyuki/Documents/Obsidian Vault"` を実行して、`requirements.txt` があるフォルダに移動してから実行してください（`~` で実行すると見つかりません）。

**注意**: `pip3` と `pip` のどちらを使うかは、システムによって異なります。エラーが出た場合は、もう一方を試してください。

### ステップ3: Playwrightブラウザをインストール

```bash
playwright install chromium
```

このコマンドで、Playwrightが使用するChromiumブラウザがダウンロードされます（初回のみ時間がかかります）。

### ステップ4: インストール確認

以下のコマンドで、インストールが正しく完了したか確認します：

```bash
python3 -c "import playwright; print('Playwright OK')"
python3 -c "import dotenv; print('dotenv OK')"
```

両方とも「OK」と表示されれば、インストール成功です。

---

## 設定ファイルの準備

### ステップ1: .envファイルを作成

`.env.example`ファイルをコピーして、`.env`ファイルを作成します。

**方法A: ターミナルでコピー**

```bash
cp .env.example .env
```

**重要（ここで詰まりがち）**：
- `.env` の中身（`NOTE_EMAIL=...` など）を**ターミナルに貼り付けて実行しない**でください。`#` 行などがコマンド扱いになり、`zsh: command not found: #` のようなエラーになります。\n- `.env` は **ファイルをエディタで開いて編集**します（例：`nano .env`）。\n- `NOTE_OLD_TEXT` を2回書くと、**後ろの1行で上書き**されます（複数置換したい場合は、スクリプト側の対応が必要です）。

**方法B: 手動で作成**

1. `.env.example`ファイルを開く
2. 内容をコピー
3. 新しいファイル`.env`を作成して貼り付け

### ステップ2: .envファイルを編集

`.env`ファイルをテキストエディタで開き、以下の情報を入力します：

```env
# Note.com 認証情報（必須）
NOTE_EMAIL=nobu@growx87.com
NOTE_PASSWORD=Bijinesu08

# 記事編集設定（必須）
NOTE_EDIT_URL=https://editor.note.com/notes/n3b5600729769/edit/

# 削除したい文字列（複数指定可能）
# 方法1: 改行区切りで1つの変数に（推奨）
NOTE_OLD_TEXT=https://note.com/growthfix_corp/m/m300254967727
https://utage-system.com/p/baep8BHALGvn

# 方法2: 別々の変数で指定
# NOTE_OLD_TEXT_1=https://note.com/growthfix_corp/m/m300254967727
# NOTE_OLD_TEXT_2=https://utage-system.com/p/baep8BHALGvn

NOTE_NEW_TEXT=
NOTE_LINK_URL=

# 実行設定（オプション）
NOTE_HEADLESS=false
```

#### 各項目の説明

**NOTE_EMAIL**
- Note.comにログインする際に使用するメールアドレス
- 例: `user@example.com`

**NOTE_PASSWORD**
- Note.comのパスワード
- **重要**: このファイルはGitにコミットしないでください

**NOTE_EDIT_URL**
- 編集したい記事の編集ページのURL
- 取得方法:
  1. Note.comにログイン
  2. 編集したい記事を開く
  3. 右上の「編集」ボタンをクリック
  4. ブラウザのアドレスバーに表示されるURLをコピー
  5. 例: `https://note.com/username/n/n1234567890/edit`

**NOTE_OLD_TEXT**
- 記事本文から削除したい文字列
- **複数の文字列を削除する場合**:
  - 方法1: 改行区切りで1つの変数に記述（推奨）
    ```
    NOTE_OLD_TEXT=https://example.com/old1
    https://example.com/old2
    ```
  - 方法2: 別々の変数で指定
    ```
    NOTE_OLD_TEXT_1=https://example.com/old1
    NOTE_OLD_TEXT_2=https://example.com/old2
    ```
- 完全一致で検索されます（大文字小文字も区別）
- 例（単一）: `[このテキストを削除]`
- 例（複数）: 上記の方法1または方法2を使用

**NOTE_NEW_TEXT**
- 削除した文字列の代わりに入力する新しいテキスト
- 例: `新しいテキスト`

**NOTE_LINK_URL**
- 新しいテキストに設定するリンクのURL（オプション）
- リンクを設定しない場合は空欄にしてもOK
- 例: `https://example.com/page`

**NOTE_HEADLESS**
- `false`: ブラウザを表示して実行（推奨・初回はこちら）
- `true`: ブラウザを非表示で実行（動作確認後）

### ステップ3: ファイルの保存

`.env`ファイルを保存します。

**重要**: `.env`ファイルには機密情報が含まれているため、Gitにコミットしないでください。`.gitignore`に既に追加済みです。

---

## 使い方（3つの方法）

### 方法1: 環境変数を使用（推奨）

`.env`ファイルに設定を記入した後、以下のコマンドを実行するだけです：

```bash
python3 note_editor.py
```

または

```bash
python note_editor.py
```

**メリット**: 設定をファイルに保存できるため、繰り返し使用する場合に便利

### 方法2: コマンドライン引数を使用

`.env`ファイルを使わず、コマンドラインで直接指定する方法です：

```bash
python3 note_editor.py \
  "https://note.com/username/n/n1234567890/edit" \
  "削除したいテキスト" \
  "新しいテキスト" \
  "https://example.com"
```

**引数の順番**:
1. 編集URL
2. 削除したいテキスト
3. 新しいテキスト
4. リンクURL（オプション）

**メリット**: 1回だけ実行する場合に便利

### 方法3: Pythonスクリプトから直接使用

他のPythonスクリプトから呼び出す方法です：

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
            edit_url="https://note.com/username/n/n1234567890/edit",
            old_text="削除したいテキスト",
            new_text="新しいテキスト",
            link_url="https://example.com"
        )

if __name__ == "__main__":
    asyncio.run(main())
```

**メリット**: 複数の記事を連続で編集する場合など、カスタマイズが必要な場合に便利

---

## 実際の使用例

### 例1: 記事内のリンクを更新する

**シナリオ**: 記事内の「詳細はこちら」というテキストのリンク先を変更したい

**設定**:
```env
NOTE_EDIT_URL=https://note.com/myaccount/n/n1234567890/edit
NOTE_OLD_TEXT=詳細はこちら
NOTE_NEW_TEXT=詳細はこちら
NOTE_LINK_URL=https://new-link.com
```

**実行**:
```bash
python3 note_editor.py
```

**結果**: 「詳細はこちら」のテキストはそのままで、リンク先だけが更新されます。

### 例2: テキストを置き換える

**シナリオ**: 記事内の「旧サービス名」を「新サービス名」に変更したい

**設定**:
```env
NOTE_EDIT_URL=https://note.com/myaccount/n/n1234567890/edit
NOTE_OLD_TEXT=旧サービス名
NOTE_NEW_TEXT=新サービス名
NOTE_LINK_URL=
```

**実行**:
```bash
python3 note_editor.py
```

**結果**: 「旧サービス名」が「新サービス名」に置き換えられます。

### 例3: テキストを追加してリンクを設定

**シナリオ**: 記事の最後に「無料診断を受ける」というテキストとリンクを追加したい

**設定**:
```env
NOTE_EDIT_URL=https://note.com/myaccount/n/n1234567890/edit
NOTE_OLD_TEXT=
NOTE_NEW_TEXT=無料診断を受ける
NOTE_LINK_URL=https://example.com/diagnosis
```

**注意**: `NOTE_OLD_TEXT`を空欄にすると、テキストの削除は行われず、新しいテキストが追加されます。

---

## 実行の流れ（詳細）

### 1. スクリプト起動

```bash
python3 note_editor.py
```

### 2. ログイン処理

- 初回実行時:
  - ブラウザが開く
  - Note.comのログインページが表示される
  - 自動的にメールアドレスとパスワードが入力される
  - ログインボタンがクリックされる
  - ログイン成功後、クッキーが`note_cookies.json`に保存される

- 2回目以降:
  - 保存されたクッキーを使用して自動ログイン
  - ログインページをスキップ

### 3. 記事編集ページへの移動

- 指定した編集URLにアクセス
- エディタが読み込まれるまで待機

### 4. テキストの検索と削除

- 本文内から`NOTE_OLD_TEXT`を検索
- 見つかった場合、そのテキストを選択して削除
- 見つからない場合、警告メッセージを表示（処理は続行）

### 5. 新しいテキストの入力

- カーソルを本文の最後に移動
- `NOTE_NEW_TEXT`を入力

### 6. リンクの設定

- `NOTE_LINK_URL`が指定されている場合:
  - 入力したテキストを選択
  - リンクボタンをクリック（またはキーボードショートカット）
  - URLを入力して確定

### 7. 保存

- 「保存」または「公開」ボタンをクリック
- 保存完了を確認

### 8. 完了

- 5秒後にブラウザが自動的に閉じる
- ターミナルに「処理完了」と表示される

---

## トラブルシューティング

### 問題1: 「ModuleNotFoundError: No module named 'playwright'」

**原因**: Playwrightがインストールされていない

**解決方法**:
```bash
pip3 install playwright
playwright install chromium
```

### 問題2: ログインに失敗する

**原因A**: メールアドレスまたはパスワードが間違っている

**解決方法**:
- `.env`ファイルの`NOTE_EMAIL`と`NOTE_PASSWORD`を確認
- Note.comに直接ログインして、認証情報が正しいか確認

**原因B**: 2段階認証が有効になっている

**解決方法**:
- 一時的に2段階認証を無効化する
- または、アプリパスワードを使用する（Note.comが対応している場合）

**原因C**: クッキーが無効になっている

**解決方法**:
```bash
# クッキーファイルを削除して再ログイン
rm note_cookies.json
python3 note_editor.py
```

### 問題3: 「エディタが見つかりません」

**原因A**: 編集URLが間違っている

**解決方法**:
- URLが`/edit`で終わっているか確認
- 記事の編集権限があるか確認
- ブラウザを表示モード（`NOTE_HEADLESS=false`）にして、実際にアクセスできるか確認

**原因B**: ページの読み込みが遅い

**解決方法**:
- `note_editor.py`の`timeout=15000`の値を大きくする（例: `timeout=30000`）

### 問題4: テキストが見つからない

**原因**: 削除したいテキストが正確に一致していない

**解決方法**:
1. ブラウザを表示モードにして実行
2. 記事の本文を確認
3. 以下の点をチェック:
   - 空白や改行が含まれていないか
   - 大文字小文字が一致しているか
   - 全角・半角が一致しているか
   - 特殊文字がエスケープされているか

**確認方法**:
```bash
# ブラウザを表示して実行
NOTE_HEADLESS=false python3 note_editor.py
```

### 問題5: リンクが設定できない

**原因**: Note.comのエディタUIが変更されている可能性

**解決方法**:
1. ブラウザを表示モードにして実行
2. エディタのツールバーを確認
3. リンクボタンの位置を特定
4. `note_editor.py`の`link_button_selectors`に新しいセレクターを追加

**手動で確認する手順**:
1. Note.comで記事を編集
2. テキストを選択
3. リンクボタンがどこにあるか確認
4. ブラウザの開発者ツール（F12）で要素を検証

### 問題6: 保存ボタンが見つからない

**原因**: Note.comのUIが変更されている

**解決方法**:
- ブラウザを表示モードにして、手動で保存ボタンをクリック
- `note_editor.py`の`publish_selectors`に新しいセレクターを追加

### 問題7: 「Permission denied」エラー

**原因**: ファイルの権限が不足している

**解決方法**:
```bash
chmod +x note_editor.py
```

### 問題8: ブラウザが起動しない（macOS）

**原因**: macOSのセキュリティ設定

**解決方法**:
1. システム環境設定 → セキュリティとプライバシー
2. Playwrightの実行を許可

---

## よくある質問（FAQ）

### Q1: 複数の記事を一度に編集できますか？

**A**: 現在のバージョンでは、1記事ずつ編集する必要があります。複数記事を編集する場合は、Pythonスクリプトからループ処理を書くか、シェルスクリプトで複数回実行してください。

**例**:
```bash
# 記事1
NOTE_EDIT_URL=https://note.com/user/n/n1111111111/edit python3 note_editor.py

# 記事2
NOTE_EDIT_URL=https://note.com/user/n/n2222222222/edit python3 note_editor.py
```

### Q2: クッキーはどこに保存されますか？

**A**: プロジェクトフォルダ内の`note_cookies.json`に保存されます。このファイルには認証情報が含まれているため、Gitにコミットしないでください。

### Q3: パスワードをコマンドラインで指定できますか？

**A**: はい、環境変数として指定できます：

```bash
NOTE_EMAIL=user@example.com NOTE_PASSWORD=password python3 note_editor.py
```

ただし、コマンド履歴に残るため、セキュリティ上推奨しません。

### Q4: 実行中にブラウザを閉じても大丈夫ですか？

**A**: 処理が完了する前にブラウザを閉じると、編集が保存されない可能性があります。保存完了のメッセージが表示されるまで待ってください。

### Q5: エラーが発生した場合、どこを確認すればいいですか？

**A**: 
1. ターミナルのエラーメッセージを確認
2. ブラウザを表示モード（`NOTE_HEADLESS=false`）にして、実際の動作を確認
3. `.env`ファイルの設定が正しいか確認
4. Note.comのサイトが正常に動作しているか確認

### Q6: 他のブラウザ（Firefox、Safari）を使えますか？

**A**: 現在のバージョンではChromiumのみ対応しています。FirefoxやSafariを使用する場合は、`note_editor.py`の`chromium`を`firefox`や`webkit`に変更してください。

### Q7: 実行時間はどのくらいかかりますか？

**A**: 
- 初回ログイン: 約10-20秒
- 2回目以降（クッキー使用）: 約5-10秒
- 記事編集: 約5-10秒

合計で約10-30秒程度です。

### Q8: スクリプトを定期実行できますか？

**A**: はい、cron（Linux/macOS）やタスクスケジューラ（Windows）を使用して定期実行できます。

**macOS/Linuxの例**:
```bash
# 毎日午前9時に実行
0 9 * * * cd /path/to/project && /usr/bin/python3 note_editor.py
```

### Q9: 複数のテキストを一度に置換できますか？

**A**: 現在のバージョンでは、1つのテキストのみ対応しています。複数のテキストを置換する場合は、スクリプトを複数回実行するか、カスタマイズが必要です。

### Q10: 記事の下書き保存はできますか？

**A**: 現在のバージョンでは「公開」または「保存」ボタンをクリックします。下書き保存のみを行いたい場合は、`note_editor.py`の保存ボタンのセレクターを調整してください。

---

## セキュリティに関する注意事項

### ⚠️ 重要な注意点

1. **`.env`ファイルは絶対にGitにコミットしない**
   - パスワードなどの機密情報が含まれています
   - `.gitignore`に追加済みですが、確認してください

2. **`note_cookies.json`もコミットしない**
   - 認証情報が含まれています

3. **パスワードの管理**
   - 強力なパスワードを使用する
   - 定期的にパスワードを変更する
   - パスワードを他人と共有しない

4. **実行環境**
   - 信頼できる環境でのみ実行する
   - 公共のWi-Fiなど、セキュリティが不確実な環境では使用しない

---

## サポート

問題が解決しない場合は、以下を確認してください：

1. **エラーメッセージの全文**を確認
2. **ブラウザを表示モード**にして、実際の動作を確認
3. **Note.comのサイト**が正常に動作しているか確認
4. **PythonとPlaywrightのバージョン**が最新か確認

---

## 更新履歴

- **v1.0.0** (2024): 初回リリース
  - 基本的な編集機能
  - クッキー保存機能
  - リンク設定機能

---

**作成日**: 2024年
**最終更新**: 2024年
