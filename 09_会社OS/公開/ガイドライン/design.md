# design.md

GrowthFix のブランドガイド・デザイン基準。引力ブランディング2層構造／5サービス完全分化／LP 共通ヘッダー・フッター／モバイル最適化／WhitePaper 構造の単一情報源。

> **正の単一情報源（SSOT）：** `05_プロダクト/_共通/SSOT_用語と定義.md`（参謀名・タグライン・廃止用語の正）
> **テンプレ：** `05_プロダクト/_共通/`（site-*\_template.html / b-*\_template.html / mobile.css）

---

## Part 1: 思想層

### Why（なぜデザインも引力経営の一部か）

引力経営は「思想運動体」である。デザインは思想の**視覚言語**であり、思想とデザインは切り離せない。

LP・WP・名刺・SNS バナーが「綺麗にまとめられた」AI 生成テンプレ感を放った瞬間、引力経営の思想は希薄化する。「あ、これも普通のコンサルね」と片付けられて終わる。

GrowthFix のデザインは、**経営者を引き止める引力場**として機能する必要がある。

### 定義

**視覚言語：**
> 経営者の引力源（Why × 才能 × 偏愛）を、視覚的に伝達する装置

**ブランド原則の階層：**

```
[1] 思想（引力経営・社長の翻訳者・抜く翻訳者）
       ↓ 視覚化
[2] 視覚言語（色・フォント・レイアウト・写真・モーション）
       ↓ 媒体への展開
[3] 媒体（LP・WP・名刺・SNS バナー・スライド）
```

[1] 思想 → [2] 視覚言語 への変換が**翻訳**の一形態。design.md はその翻訳パターンを定義する。

### 中核原則

#### ★ 本命：思想がデザインを駆動する

「綺麗なデザイン」を目指さない。**「思想が滲むデザイン」を目指す。**

セルフチェック：
- [ ] AI が出した「綺麗なまとめ」のような均質感がないか？
- [ ] 引力（重力・求心力）の物理メタファーが視覚的に立っているか？
- [ ] 識学・他社コンサルと差別化されている独自感があるか？
- [ ] 経営者個人の「異常性」が見える要素が入っているか？

#### サテライト 1：引力ブランディング 2 層構造

| 層 | 名称 | 配置 |
|---|---|---|
| **存在層**（アイデンティティ） | **組織の引力研究の人 ／ 引力の参謀** | profile / achievement / top / WP / whitepaper_optin / seminar-acting |
| **機能層**（5 サービス完全分化・260426） | サービス毎の固有参謀名 | 各 LP の hero-eyebrow |

5 サービス参謀名（機能層）：
- CODE → **引力の参謀**
- Scan → **引力の参謀（組織軸）**
- Coaching → **心の参謀**
- Shift → **変革の参謀**
- Orbit → **共鳴の参謀**

詳細：`参謀.md` および SSOT §1。

#### サテライト 2：節制（黒×白×アクセント1色）

色を盛らない。フォントを盛らない。装飾を盛らない。

「足す」のではなく「抜く」を、視覚にも適用する。情報密度は高くてよいが、**視覚的ノイズは最小化**する。

#### サテライト 3：モバイルファースト

経営者は移動中・空き時間にスマホで読む。Android Chrome 360px viewport で本文 15-17px、見出し h1 25-36px が読みやすく整っているか、毎回確認する。

詳細：`reference_mobile_css_strategy.md`

#### サテライト 4：誤公開リスクの低減

公開 MD と非公開 MD を物理フォルダで分離（本「09_会社OS/」フォルダの構造そのもの）。視覚的に「これは公開」「これは内部」が一目で判別できる構造を維持する。

---

## Part 2: 実装層

### 引力ブランディング 2 層の視覚反映

| 用途 | 配置語彙 |
|---|---|
| **profile / achievement / top / WP** | 「組織の引力研究の人」「引力の参謀」（存在層） |
| **CODE LP hero-eyebrow** | 「引力の参謀」（機能層・存在層と同語だがレイヤー違い） |
| **Scan LP hero-eyebrow** | 「引力の参謀（組織軸）」 |
| **Coaching LP hero-eyebrow** | 「心の参謀」 |
| **Shift LP hero-eyebrow** | 「変革の参謀」 |
| **Orbit LP hero-eyebrow** | 「共鳴の参謀」 |

統一タグライン形式：
> **{参謀名} ── {動詞のキャッチ}**

例：「変革の参謀 ── 引力の設計図を、幹部と共に組織に実装する3ヶ月」

### LP 共通ヘッダー・フッター運用ルール

雛形ファイル：`05_プロダクト/_共通/`

| ファイル | 用途 |
|---|---|
| `site-header_template.html` `site-footer_template.html` | 個別 6 LP 用 |
| `b-header_template.html` `b-footer_template.html` | Hub（Gravity LP）専用 |
| `README.md` | プレースホルダ規約・運用ルール |
| `260416_差分リスト.md` | 現状 7 LP の雛形外差分 |

**運用ルール：**
1. 共通部（タグライン・サービスリンク・著作権表記）変更時は**雛形を先に更新**
2. その後各 LP に展開
3. 1 LP 限定の暫定修正は雛形に反映せず、差分リストに記録
4. 3 ファイル以上を触る規模の変更は、必ず雛形から着手

**プレースホルダ：**
`{{PRODUCT_NAME}}` `{{LOGO_HREF}}` `{{NAV_ITEMS}}` `{{MOBILE_NAV_ITEMS}}` `{{CTA_LABEL}}` `{{CTA_ANCHOR}}` `{{PRODUCT_SLUG}}`

### モバイル最適化（mobile.css 戦略）

**配置：** `05_プロダクト/_共通/mobile.css` → 本番 `https://growthfix.jp/assets/css/mobile.css`

**読み込み形式：** 各 HTML の `</head>` 直前または `</main>` 後（必ず**最終 CSS** として配置）

**キャッシュバスター：** URL 末尾に `?v=YYMMDDx`（CSS 更新時にインクリメント）

**適用ページ（19 本）：** コーポレート 11（top / service / profile / contact / knowledge / news / news/gravity-release / news/site-renewal / privacy-policy / achievement / whitepaper）／LP 6（gravity / code / blueprint / coaching / shift / orbit）／診断 UI 2（CODE/executive・Scan/diagnose）

**適用対象外：** `gravity-code/diagnose/`（CODE 診断システム）／`gravity-shift/diagnose/`（Shift 内部ダッシュボード）── 独自 UI のため

**設計方針：**
- 768px 以下：見出し clamp 化、container 強制 100% 幅、横並び縦積み化
- 600px 以下：セクション余白圧縮、container padding 16px
- 375px 以下：iPhone SE 等向け padding 12px
- WP テーマ専用 override：`.service .item { display:grid !important }` 対策

**.htaccess キャッシュ戦略：**
1. HTML は毎回サーバ確認（Cache-Control: no-cache）
2. CSS/JS/画像は長期キャッシュ（1 年・W3TC ルール）
3. nginx キャッシュも HTML だけ off

詳細：`reference_mobile_css_strategy.md`

### WhitePaper 構造

| URL | 用途 | 形式 |
|---|---|---|
| `/whitepaper/` | オプトイン LP（UTAGE フォーム） | LP・lead magnet 入口 |
| `/whitepaper-read/` | 本体 V9 | HTML（25 ページ相当） |
| `/whitepaper.pdf` | PDF 版 | 25 ページ・4MB |

**PDF 再生成手順：** HTML 更新 → Chrome ヘッドレスで PDF 再生成 → 本番デプロイ。詳細：`reference_whitepaper_pdf_regen.md`

**注意：** `/whitepaper/`（オプトイン）と `/whitepaper-read/`（本体）を混同して上書きデプロイした事故あり（260424夜→260425朝復旧）。

### コーポレート TOP（`/`）の特殊ルール

- `/public_html/index.html` は手動編集の最新版
- 動的化（WP テンプレート切り替え）すると古いテーマに戻る
- 編集は直接 FTP で。`/knowledge/` 更新時はトップも手動同期必要

詳細：`reference_wp_static_index_conflict.md`

### カラーパレット（実装時の参照）

具体的なカラーコードは各 LP の CSS で個別管理されているが、共通指針：

- **基調色：** 黒系（#0f172a / #1e293b / #1f2937）／白系（#ffffff / #f8fafc / #f1f5f9）
- **アクセント：** サービス別に 1 色（Shift＝青系 #1e40af、CODE/Coaching＝ベージュ系 #b8a88a 等）
- **Gravity 思想色：** 重力・宇宙・軌道のメタファーで暗色寄りを基調

サービス間で色を盛らない。LP 単独で完成度を上げ、コーポレート全体ではモノトーン基調を維持する。

### フォント

- **日本語：** Noto Sans JP（weight 400/500/700/900）
- **英語：** Alex Brush（装飾用）／システムフォント（本文）
- **アイコン：** Remix Icon（CDN）

統一原則：1 ページ内のフォントファミリは 2 系統まで。ウェイトで階層を作る。

### 廃止デザイン要素（残してはいけない）

| 禁止要素 | 理由 |
|---|---|
| 旧サービス名（Scan / Scan DEEP / Gravity Light / Core） | 廃止サービス |
| 旧医療メタファー（セラピスト・外科医・ホームドクター） | 5 サービス参謀体系に統一済み |
| 旧 V1「天井」セミナー直訴求要素 | 凍結中（acting 版に刷新） |
| 旧 6 サービス体系の図解 | 5 サービス化済み |
| 旧 13 ページ WP 表記 | 25 ページに更新済み |

定期的に SSOT §7 と整合性 lint で検出する。

### 整合性チェック運用

`06_開発/scripts/lint_consistency.sh` を週次／改定後に実行。

**検出対象：**
- 廃止用語の残留
- 参謀名・価格・期間の表記揺れ
- WP ページ数の表記不整合
- 4型→次サービス推奨ルールの不整合

### 言葉・語彙

- **引力ブランディング 2 層構造**（存在層／機能層）
- **5 サービス完全分化**（260426 確定）
- **統一タグライン形式**（{参謀名} ── {動詞のキャッチ}）
- **節制**（足すではなく抜く視覚言語）
- **整合性 lint**（SSOT 機械チェック）

---

## Part 3: ハーネス層（260429・実行時ガード）

LP / WP / コーポレート / 診断 UI のビジュアル品質と SSOT 整合性を実行時にテストする層。19 LP 一括運用の機械化と、デザイン違反の自動検出を担保する。

### 良いアウトプットの合格基準（Pass条件）

- [ ] **モバイル監査全項目通過**：`05_プロダクト/_共通/_LP変更時_モバイル確認チェックリスト.md`
- [ ] **`verify_deployment.sh` 23 項目通過**：HTTP 200 / 共通アセット稼働 / バージョン整合
- [ ] **`audit_mobile_sync.py` 通過**：mobile.css 同期監査
- [ ] **SSOT 準拠**：5 サービス価格・期間・参謀名 が `05_プロダクト/_共通/SSOT_用語と定義.md` と一致
- [ ] **引力ブランディング 2 層構造整合**：存在層と機能層の役割分離が破綻していない
- [ ] **統一タグライン形式**：参謀名 ── 動詞のキャッチ の構造を満たす
- [ ] **「節制」原則**：足すではなく抜く視覚言語
- [ ] **3 行レイアウト等の仕様認識**：ユーザーが「変わっていない／おかしい」と指摘した時はスクショ先行（`feedback_screenshot_first_before_fix`）

### 悪いアウトプット例（NG例）

- ❌ HTML 直接編集後にモバイル監査スキップ：機械チェック前のデプロイ
- ❌ mobile.css と 19 LP の同期忘れ：`audit_mobile_sync.py` を実行していない
- ❌ SSOT 違反のまま LP デプロイ：旧価格・廃止用語混入
- ❌ 共通アセット側を触らずに LP 個別 HTML/CSS で修正：保守工数を線形に増やす
- ❌ 仕様認識違いを技術修正で解こうとする：スクショで実物確認していない
- ❌ A/B テスト導入時に各 LP 個別 JS 実装：`ab-test.js` 共通基盤を経由していない
- ❌ ABEMA・HTTPS 通信不可・低速回線 で崩れる装飾を共通アセットに混入

### 実行時テスト（チェックフック）

LP 編集後の必須シーケンス：

1. `audit_mobile_sync.py` 実行
2. ローカル目視（モバイル幅 768px / 600px / 375px）
3. デプロイ
4. `verify_deployment.sh` 実行
5. モバイル監査チェックリスト全項目目視
6. `lint_consistency.sh` 実行（SSOT 整合）

「変わっていない／おかしい」報告時：

1. スクショを依頼（仮説修正を走らせる前に）
2. 仕様認識違いか実装違いかを判定
3. 認識違いなら仕様確認・実装違いなら修正

### 機械チェック対応

| スクリプト | 対象 |
|---|---|
| `audit_mobile_sync.py` | mobile.css 同期 |
| `verify_deployment.sh` | LP デプロイ後 23 項目 |
| `lint_consistency.sh` | SSOT 整合 |
| `bump_cache_buster.sh` | mobile.css?v= 一括 bump |

### 関連MD

- `参謀.md`（参謀名・umbrella と固有名の使い分け）
- `商品.md`（5 サービスの統一タグライン形式）
- `引力.md`（視覚化すべき思想・タグライン3層）
- `culture.md`（学者モード化を避けるセルフチェック）
- `AI.md`（自動化スクリプト群・lint 運用）

### 参考メモリ

- `project_gravity_identity_triple_layer.md` ── ブランディング層構造
- `feedback_lp_header_footer_template.md` ── LP 共通ヘッダー・フッター運用
- `reference_mobile_css_strategy.md` ── モバイル最適化戦略
- `reference_whitepaper_url_structure.md` ── WP オプトイン／本体分離
- `reference_whitepaper_pdf_regen.md` ── PDF 再生成手順

### 関連 SSOT

- `05_プロダクト/_共通/SSOT_用語と定義.md`（正の単一情報源）
- `05_プロダクト/_共通/`（雛形・mobile.css）
- `06_開発/scripts/lint_consistency.sh`（整合性チェック）
