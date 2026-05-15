# WordPress本番更新フロー 調査結果（M-7b）

> **作成：** 2026-04-20
> **目的：** `05_プロダクト/Gravity/LP/` 配下のWordPress関連ファイルの本番反映フロー確認
> **関連：** G-1（Profile更新・260420更新済）／G-2（Footer統一）／URL配置換え後の整合確認

---

## 🔍 調査結果

### 本番確認：WordPress稼働中
- **テーマ：** `growth`（`/wp-content/themes/growth/`）
- **ドメイン：** growthfix.jp
- **CSS/JS パス：** `https://growthfix.jp/wp-content/themes/growth/assets/img/` 等を利用

### ローカルファイルの性質分析

| ファイル | 種別 | WP関数使用 | 推定配置先 |
|---|---|---|---|
| `growthfix-top-index.html` | ピュアHTML | 0箇所 | WP管理画面の固定ページ HTML or テーマテンプレート |
| `growthfix-profile-index.html` | ピュアHTML | 0箇所 | `/wp-content/themes/growth/profile.php` または固定ページ |
| `growthfix-service-index.html` | ピュアHTML | 0箇所 | 同様 |
| `seminar-ceiling.html` | ピュアHTML | 0箇所 | WordPress固定ページ（`/seminar/ceiling/`） |
| `index.html` | ピュアHTML | 0箇所 | Gravityシリーズ TOP（`/gravity/`・実稼働確認済） |
| `gf-footer.php` | PHPパーシャル | 18箇所 | `/wp-content/themes/growth/` 直下 |
| `gf-footer-contact.php` | PHPパーシャル | 17箇所 | 同上 |

---

## 🎯 反映フローの3つの仮説

### 仮説A：WordPress管理画面の固定ページ（最有力）
- ローカルHTMLファイル＝WP管理画面の「ページ」→「編集」→「HTML直接入力」で保存されたコンテンツのスナップショット
- **反映手順：** WP管理画面にログイン→該当ページを開く→HTMLモード→ローカルファイルの内容をコピペ→保存
- **メリット：** WordPress の他機能（SEO設定・サイドバー等）と整合
- **デメリット：** 自動化不可・手動操作

### 仮説B：テーマテンプレートファイルとして直接配置
- ローカルファイル＝`/wp-content/themes/growth/` 配下のテンプレート（profile.php / service.php 等）
- **反映手順：** FTPで該当パスに直接アップロード
- **メリット：** deploy.sh 自動化可能
- **デメリット：** WP テーマの命名規約・階層ルール理解が必要

### 仮説C：外部HTMLで、WPヘッダー/フッターだけ共通化
- ローカルファイル＝純HTMLで直接 `/profile/index.html` 等として配置
- gf-footer.php だけ WPテーマとして動く形式
- **反映手順：** 純HTMLはFTP直接配置／gf-footer.phpはテーマディレクトリへ

---

## 🛠 検証手順（石井が実施）

### Step 1：本番ページのHTMLソース確認（5分）

```bash
# /profile/ の HTML source を取得
curl -s "https://growthfix.jp/profile/" > check_profile.html
# 行頭10行を確認
head -30 check_profile.html
```

確認ポイント：
- `<body class="page-*">` 等のWordPressクラスがあるか → 固定ページ（仮説A or B）
- `<!-- Served from wp-includes/ -->` や `wp-json` リンク → WordPress経由
- ヘッダーに `<link rel="profile" href="https://gmpg.org/xfn/11">` → WP標準

### Step 2：WordPress管理画面で固定ページ一覧確認（石井）

1. `https://growthfix.jp/wp-admin/` にログイン
2. 「ページ」メニューで以下のページが存在するか確認：
   - トップページ
   - プロフィール（/profile/）
   - サービス（/service/）
   - セミナー（/seminar/ceiling/）

### Step 3：テーマファイル一覧確認（FTP）

```bash
# /wp-content/themes/growth/ のファイル一覧取得
curl -u "xs992119:${FTP_PASS}" "ftp://sv16489.xserver.jp/growthfix.jp/public_html/wp-content/themes/growth/" --list-only
```

確認ポイント：
- `profile.php` / `service.php` があるか → テーマテンプレート
- `page-profile.php` / `page-service.php` → カスタムページテンプレート
- `front-page.php` → トップページテンプレート

---

## 📋 判定後のアクション

### 仮説A（管理画面固定ページ）の場合

| タスク | 手順 |
|---|---|
| Profile更新（G-1で作成済） | WP管理画面→ページ→プロフィール→HTMLモード→`growthfix-profile-index.html` の内容貼り付け |
| Hub LP（260420で更新済） | 同上・/gravity/ ページを編集 |
| Service | 同上 |
| gf-footer.php | FTPで `/wp-content/themes/growth/` に配置 |

### 仮説B（テーマテンプレート）の場合

| タスク | 手順 |
|---|---|
| Profile | FTPで `/wp-content/themes/growth/profile.php`（または `page-profile.php`）に配置／ローカルHTMLをPHP互換に変換 |
| Hub LP | `front-page.php` or `gravity-template.php` に配置 |
| Service | `service.php` or `page-service.php` に配置 |
| gf-footer.php | 同テーマディレクトリ配下 |

### 仮説C（純HTML配置）の場合

| タスク | 手順 |
|---|---|
| 各HTML | FTPで `/profile/index.html` 等に直接配置（ルートからの相対パス） |
| gf-footer.php | 別途テーマ配下 |

---

## 💡 推奨：Step 1〜3 の順に調査 → 判定結果に応じて対応

### 優先度
1. **仮説A/Bどちらか判定**（30分・石井が管理画面確認）
2. **Profile本番反映**（G-1 成果を反映・30分）
3. **Hub LP 本番反映**（260420 Hub修正を反映・30分）
4. **Service ページ更新**（60分・Blueprint/Scan追加反映）
5. **gf-footer.php の反映**（軸分離Footer・30分）

### 合計所要時間
- 調査：30分（石井）
- 実装：2-3時間（仮説A想定）

---

## ⚠️ リスク

1. **WordPress更新中の本番ダウン**：管理画面経由更新は比較的安全だが、テーマファイル直接上書きはテスト必須
2. **テーマバックアップ**：FTPで `wp-content/themes/growth/` 全体をローカルへ一旦コピー推奨
3. **キャッシュ**：W3TC（Browser Cache）が効いているため、更新反映に数分遅延あり
4. **WordPressプラグイン干渉**：セキュリティプラグインが管理画面のHTMLモード保存を制限している可能性

---

## 🔗 関連ローカルファイル（更新済）

- `05_プロダクト/Gravity/LP/growthfix-top-index.html`（260420 Blueprint命名反映・Footer軸分離）
- `05_プロダクト/Gravity/LP/growthfix-profile-index.html`（260420 G-1 3点セット追加・「組織の引力設計者」統一）
- `05_プロダクト/Gravity/LP/growthfix-service-index.html`（260420 Blueprint新規追加・Scan再定義）
- `05_プロダクト/Gravity/LP/gf-footer.php`（260420 G-3 軸分離）
- `05_プロダクト/Gravity/LP/gf-footer-contact.php`（260420 G-3 軸分離）
- `05_プロダクト/Gravity/LP/seminar-ceiling.html`（260420 Blueprint命名）

---

## 🔗 関連ドキュメント

- `04_GrowthFix/01_サービス設計/260420_実装TODO網羅リスト.md`（M-7b）
- `04_GrowthFix/01_サービス設計/260420_URL配置換え計画_Blueprint新URL_Scan差替.md`
- `memory/MEMORY.md`（FTP情報）
