# 06_開発/backups/ ── バックアップ集約 SSOT

> **目的：** Vault 内の本番設定 / システム / 重要ファイルのバックアップを 1 ヶ所に集約する単一の真実
> **作成：** 2026-05-12（260512・統合タスクマスター #19 完了）
> **位置付け：** 「破壊的変更前のロールバック装置」「過去設定の参照源」として運用
> **運用原則：** **重要な変更を行う前に該当ファイルを本ディレクトリにコピーし、日付付きファイル名で保存**

---

## 📁 ディレクトリ構成

```
06_開発/backups/
├── README.md（本ファイル・運用ルール SSOT）
├── htaccess/                    ← Apache/Nginx ルーティング設定
│   ├── htaccess_backup_260420.txt（旧位置から集約予定）
│   └── htaccess_backup_260511.txt（WP 撤退前バックアップ）
├── html/                        ← 重要 HTML ファイル
│   └── WP_V9_index_backup_260511.html（WP V9 ベース版）
├── assets/                      ← 画像・CSS・JS のバックアップ
│   └── space_bg_hubble_backup.jpg
└── archive/                     ← 30 日以上経過した古いバックアップ
```

---

## 🎯 運用ルール

### 1. バックアップ作成タイミング

**必須：** 以下の操作前は必ずバックアップを取る

- 本番 `.htaccess` を編集する前（WP 撤退・リダイレクト追加・SEO 設定変更等）
- WhitePaper / 重要 LP HTML を大幅改修する前（30% 以上の構造変更）
- データベース操作前（DB 削除・スキーマ変更）
- システム設定ファイル変更前（site-chrome.js / mobile.css 等の基盤層）

**推奨：** 以下の操作前もバックアップ推奨

- LP の Hero / Pricing セクションの大幅書き換え
- メイン navigation の構造変更
- フォーム action URL の変更

### 2. ファイル命名規則

**形式：** `{元ファイル名}_backup_{YYMMDD}.{拡張子}` または `{YYMMDD}_{元ファイル名}.{拡張子}`

**例：**
- ✅ `htaccess_backup_260511.txt`
- ✅ `index_backup_260511.html`
- ✅ `260512_recruit_LP_pre_v1.2.html`
- ❌ `htaccess.bak`（日付なし）
- ❌ `backup.html`（元ファイル名不明）

### 3. 保管期間

- **常時保管：** 重要システム変更（WP 撤退・DB 削除・site-chrome.js 改修）= 1 年以上
- **30 日経過：** `archive/` サブディレクトリに移動（書き換えはしない・履歴として残す）
- **90 日以上経過：** ユーザー判断で削除可能（systematic な変更履歴が他に存在する場合のみ）

### 4. 復元手順

```bash
# 1. バックアップ確認
ls -la 06_開発/backups/htaccess/

# 2. 復元（例：.htaccess 戻し）
cp 06_開発/backups/htaccess/htaccess_backup_260511.txt \
   /path/to/current/.htaccess

# 3. FTP デプロイ
curl -T .htaccess "ftp://sv16489.xserver.jp/growthfix.jp/public_html/.htaccess" \
  --user "xs992119:cgq1fv99"

# 4. 動作確認
curl -sS -o /dev/null -w "%{http_code}\n" https://growthfix.jp/
```

### 5. 散在バックアップの集約手順（260512 確立）

過去に Vault 内の様々な場所に散在していたバックアップを本ディレクトリに集約する手順：

```bash
# 1. find で散在バックアップを検出
find "/Users/ishiinobuyuki/Documents/Obsidian Vault/" \
  -name "*backup*" -type f \
  | grep -v "_archive" \
  | grep -v "06_開発/backups"

# 2. 用途別サブディレクトリに mv（手動・破壊的なので注意）
mv 06_開発/server_config/backup/htaccess_backup_260420.txt \
   06_開発/backups/htaccess/

mv 05_プロダクト/WhitePaper/V9/index_backup_260511.html \
   06_開発/backups/html/WP_V9_index_backup_260511.html

mv 05_プロダクト/Gravity/LP/images/space_bg_hubble_backup.jpg \
   06_開発/backups/assets/

# 3. 集約完了の確認
ls -la 06_開発/backups/htaccess/
ls -la 06_開発/backups/html/
ls -la 06_開発/backups/assets/
```

**注意：** mv は破壊的操作のため、新規パスの動作確認後に実行する（参照されているリンクが切れないか確認）。

---

## 📋 現在のバックアップインベントリ（260512 集約前）

| ファイル | 旧位置 | 推奨集約先 | 日付 | 用途 |
|---|---|---|---|---|
| `htaccess_backup_260511.txt` | 06_開発/backups/ | 06_開発/backups/htaccess/ | 260511 | WP 撤退前 .htaccess |
| `htaccess_backup_260420.txt` | 06_開発/server_config/backup/ | 06_開発/backups/htaccess/ | 260420 | 旧 .htaccess |
| `index_backup_260511.html` | 05_プロダクト/WhitePaper/V9/ | 06_開発/backups/html/ | 260511 | WP V9 ベース版 |
| `space_bg_hubble_backup.jpg` | 05_プロダクト/Gravity/LP/images/ | 06_開発/backups/assets/ | 不明 | Hubble 画像 |

**集約タイミング：** ユーザー実行 or 次セッションで Bash 経由で実施。本 README は集約計画 SSOT として先行コミット。

---

## 🛡 関連 SSOT

- WP 撤退記録：`memory/project_wp_decommission_260511.md`
- 自動化スクリプト：`06_開発/scripts/wp_decommission.py`（FTP 再帰削除・将来同種作業のテンプレ）
- FTP 情報：`06_開発/開発ツール/FTP情報_メインFTPアカウント.md`
- design.md Part 3：`09_会社OS/公開/ガイドライン/design.md`

---

## 改訂履歴

| 版 | 日付 | 内容 |
|---|---|---|
| v1.0 | 2026-05-12 | 初版作成（統合タスクマスター #19・バックアップ集約 SSOT 確立）|
