# .htaccess 設定：gravity-scan-deep → gravity-scan 301リダイレクト

> **作成：** 2026-04-20（URL配置換え Step 4）
> **目的：** `/gravity-scan-deep/` への既存リンクを新Scan URL `/gravity-scan/` に永続リダイレクト
> **デプロイ先：** `growthfix.jp/public_html/.htaccess`（サーバー）
> **必要工数：** 実施時 30分（エディタ編集＋FTP＋動作確認）

---

## 🎯 リダイレクト方針（260420 A案）

### なぜ必要か
- 旧 `/gravity-scan-deep/`（Scan DEEP）の**全ページを廃止**
- 新体系では旧DEEPのコンテンツを `/gravity-scan/`（新Scan）に統合済み（Step 3-B完了）
- 既存の被リンク／ブックマーク／検索エンジンキャッシュを**301リダイレクト**で継承→SEO資産保全

### リダイレクト対象外
- `/gravity-scan/`（これは新Scan本体として稼働）
- `/gravity-blueprint/`（新URL・新規）

---

## 📝 追記すべき .htaccess 設定

**以下のブロックをサーバー側 `.htaccess` に追記：**

```apache
# === 260420 URL配置換え：Scan DEEP廃止・Scan統合 ===
# /gravity-scan-deep/... を /gravity-scan/... に永続リダイレクト
RewriteEngine On
RewriteRule ^gravity-scan-deep/?$ /gravity-scan/ [R=301,L]
RewriteRule ^gravity-scan-deep/(.*)$ /gravity-scan/$1 [R=301,L]
```

### 置き場所の目安
- 既に `RewriteEngine On` がある場合はその下に RewriteRule 2行だけ追記
- なければブロック全体を追加
- 他のリダイレクトルールがある場合は**優先順位に注意**（先頭に置くのが安全）

---

## 🔧 デプロイ手順

### Step 1：サーバーから現状の .htaccess 取得（バックアップ）

```bash
# ローカルPC から FTP 経由で取得（curl or lftp）
curl -o htaccess_backup_260420.txt \
  "ftp://sv16489.xserver.jp/growthfix.jp/public_html/.htaccess" \
  --user "xs992119:${FTP_PASS}"
# ファイルを 06_開発/server_config/htaccess_backup_YYMMDD.txt として保管
```

### Step 2：ローカルで編集

1. 取得した `.htaccess` を開き、上記リダイレクトブロックを追記
2. 保存して次のステップへ

### Step 3：サーバーへアップロード

```bash
curl -T "編集後.htaccess のパス" \
  "ftp://sv16489.xserver.jp/growthfix.jp/public_html/.htaccess" \
  --user "xs992119:${FTP_PASS}"
```

### Step 4：動作確認

```bash
# ルート → 新Scan
curl -I https://growthfix.jp/gravity-scan-deep/ | head -3
# 期待: HTTP/2 301, Location: /gravity-scan/

# サブページ → サブページ保持
curl -I https://growthfix.jp/gravity-scan-deep/sample/ | head -3
# 期待: HTTP/2 301, Location: /gravity-scan/sample/

# 新Scan は直アクセス可能
curl -I https://growthfix.jp/gravity-scan/ | head -3
# 期待: HTTP/2 200
```

---

## ⚠️ 注意事項

1. **既存の他リダイレクトと衝突しないか確認**：サーバーの現状 .htaccess に既にある設定を把握
2. **キャッシュ・CDN があれば更新**：Xserver は CDN 基本なしだが念のため
3. **検索エンジン反映は 1-2週間**：Google Search Console で `/gravity-scan-deep/` のインデックス降格を確認
4. **広告リンク・メルマガ等の旧URL**：301 で吸収されるが、引き続き更新可能なものは更新推奨

---

## 🗓️ 実施タイミング

### 推奨：Step 6 本番デプロイと同日
- Blueprint / Scan の新コンテンツが本番稼働したタイミングでリダイレクトを有効化
- そうしないと`/gravity-scan-deep/` からリダイレクトされた先の `/gravity-scan/` が旧Blueprint版のまま見える

### 段階デプロイシナリオ（推奨）
1. Step 6：LP/診断のデプロイ（新Scan ＋ Blueprint）を本番反映
2. 本番の `/gravity-scan/` が新Scan版で動作することを確認
3. `/gravity-blueprint/` が新規URL で稼働することを確認
4. **その後** .htaccess 追記してリダイレクトを有効化

---

## 📋 実施チェックリスト

- [ ] Step 1：サーバー現 .htaccess 取得・バックアップ
- [ ] Step 2：ローカルで編集・リダイレクト行追記
- [ ] Step 3：サーバーへアップロード
- [ ] Step 4-1：`/gravity-scan-deep/` → `/gravity-scan/` の 301 確認
- [ ] Step 4-2：`/gravity-scan-deep/{サブパス}/` → `/gravity-scan/{サブパス}/` の 301 確認
- [ ] Step 4-3：`/gravity-scan/` 直アクセスで 200 確認
- [ ] Step 4-4：`/gravity-blueprint/` 直アクセスで 200 確認
- [ ] ブラウザでの手動確認（Chrome／Safari）
- [ ] Google Search Console で `/gravity-scan-deep/` のインデックス状況観察（1-2週間）

---

## 🔗 関連

- `04_GrowthFix/01_サービス設計/260420_URL配置換え計画_Blueprint新URL_Scan差替.md`（本計画の全体）
- `06_開発/scripts/deploy.sh`（LP/診断のデプロイは別・.htaccessは含まない）
- `memory/MEMORY.md`（FTP情報参照）
