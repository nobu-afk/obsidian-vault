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

例：「変革の参謀 ── 組織の引力タイプを、幹部と共に組織に実装する3ヶ月」

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

### LP 共通アセット運用標準（260509 確立）

LP 5 ページ（Gravity TOP / CODE / Recruit / Cultivate / Coaching）で重複していた CSS / JS を集約：

| ファイル | 配信パス | 役割 |
|---|---|---|
| **lp-icons.css** | `https://growthfix.jp/assets/css/lp-icons.css` | `ri-arrow-right-line` / `ri-arrow-right-s-line` を inline SVG（mask-image + currentColor）化。旧 remixicon CDN（150KB+ font fetch）撤去 |
| **lp-common.js** | `https://growthfix.jp/assets/js/lp-common.js` | Mobile menu toggle / Smooth scroll / IntersectionObserver / Form submit の共通 JS（Recruit/Cultivate/Shift script.js 完全一致重複の解消）|

**新規 LP 追加時のチェックリスト：**
- [ ] **remixicon CDN 禁止** → `<link href="https://growthfix.jp/assets/css/lp-icons.css">` を参照
- [ ] アイコンが lp-icons.css 未収録の場合 → 同 CSS に inline SVG 形式で追記
- [ ] menu-toggle / smooth-scroll / form-submit を独自実装する前に lp-common.js で十分か検討
- [ ] **inline style 禁則**：CSS class があるのに `style=""` で上書きしない（class 化を先・inline は最終手段）
- [ ] **死蔵ファイル退避**：HTML から相対参照ゼロのローカル `script.js` / `styles.css` は `_archive/YYMMDD_LP死蔵ファイル退避/` に退避

**死蔵ファイル退避ルール（260509 H-6 学び）：**
- ローカル LP ファイル編集前に `grep src="script.js"` で HTML 参照を確認
- 0 件 = 死蔵 → `_archive/` 退避（5/9 退避実績：5 LP × 2 ファイル / ~190KB）
- 1 件以上 = 現役 → 編集 OK

詳細：`memory/reference_lp_assets_260509.md` ／ `05_プロダクト/_共通/SSOT_用語と定義.md` § 共通 CSS/JS 運用ルール

### モバイル最適化（mobile.css 戦略）

**配置：** `05_プロダクト/_共通/mobile.css` → 本番 `https://growthfix.jp/assets/css/mobile.css`

**読み込み形式：** 各 HTML の `</head>` 直前または `</main>` 後（必ず**最終 CSS** として配置）

**キャッシュバスター：** URL 末尾に `?v=YYMMDDx`（CSS 更新時にインクリメント）

**適用ページ（19 本）：** コーポレート 11（top / service / profile / contact / knowledge / news / news/gravity-release / news/site-renewal / privacy-policy / achievement / whitepaper）／LP 6（gravity / code / blueprint / coaching / shift / orbit）／診断 UI 2（CODE/executive・Scan/diagnose）

**適用対象外：** `gravity-code/diagnose/`（CODE 診断システム）── 独自 UI のため

**廃止履歴：** `gravity-shift/diagnose/` は 260508 廃止 → `/gravity-scan/` へ 301 統合。詳細：`memory/project_shift_diagnose_ui_abolished_260508.md`

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
- [ ] **LP 社内用語ゼロ通過**（260511 確立）：`lint_lp_internal_terms.py` を実行し、THEORY セクション外で内部 KPI 数値・内部略称・内部運用語が検出されないことを確認

### 悪いアウトプット例（NG例）

- ❌ HTML 直接編集後にモバイル監査スキップ：機械チェック前のデプロイ
- ❌ mobile.css と 19 LP の同期忘れ：`audit_mobile_sync.py` を実行していない
- ❌ SSOT 違反のまま LP デプロイ：旧価格・廃止用語混入
- ❌ 共通アセット側を触らずに LP 個別 HTML/CSS で修正：保守工数を線形に増やす
- ❌ 仕様認識違いを技術修正で解こうとする：スクショで実物確認していない
- ❌ A/B テスト導入時に各 LP 個別 JS 実装：`ab-test.js` 共通基盤を経由していない
- ❌ ABEMA・HTTPS 通信不可・低速回線 で崩れる装飾を共通アセットに混入
- ❌ **LP に内部 KPI 数値・社内略称・運用語を残置**（260511 確立）：`継続率 N% 目標` `R の N% より高い` `完成度 N% → M%` `翻訳度 N% → M%` `発議 月N → 月M` `C 中核 / R 中核` 等を LP 本文・FAQ に書き込む。これらは営業提案書 v0.3 の領域

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

### 正本ファイル運用ルール（260507 確立・本番事故再発防止）

**Why（経緯）：** 2026-05-07 夕方、Blueprint legacy 一掃 Phase 1+2 で `TrueFit/LP/coaching/index.html`（別商品 TRUE FIT Coaching の試作 LP）を `/gravity-coaching/` に誤デプロイし、約 6 時間別商品が本番表示された事故が発生。原因は「ディレクトリ名一致での推測」と「正本ディレクトリ外の古いコピー残置」。再発防止のため運用ルールを SSOT 化。

#### 正本ディレクトリパターン（13 LP・絶対パス）

```
ローカル正本                                           本番 URL
──────────────────────────────────────────────────────────────────
05_プロダクト/top_本番/index.html                      /
05_プロダクト/Gravity/LP/index.html                    /gravity/
05_プロダクト/GravityCode/LP/index.html                /gravity-code/
05_プロダクト/GravityCode/LP/sample-report.html        /gravity-code/sample-report.html
05_プロダクト/GravityCode/診断_executive_本番/         /gravity-code/executive/（CODE 診断 UI）
05_プロダクト/GravityScan/LP/index.html                /gravity-scan/
05_プロダクト/GravityScan/診断_本番/generate.php       /gravity-scan/diagnose/generate.php
05_プロダクト/GravityCoaching/LP/index.html            /gravity-coaching/  ← 正本（事故起因）
05_プロダクト/GravityRecruit/LP/index.html             /gravity-recruit/
05_プロダクト/GravityCultivate/LP/index.html           /gravity-cultivate/
05_プロダクト/GravityOrbit/LP/index.html               /gravity-orbit/
05_プロダクト/WhitePaper/V9/index.html                 /whitepaper-read/
05_プロダクト/Gravity/LP/seminar-acting.html           /seminar/acting/
05_プロダクト/service_本番/index.html                  /service/
──────────────────────────────────────────────────────────────────
```

**命名規則（正本判定ルール）：**

1. **`{Service名}_本番/`** または **`Gravity{Service名}/LP/`** が正本ディレクトリ
2. ディレクトリ名にサービス名が含まれていても、上記パターンと一致しないものは正本ではない
3. 「ペンディング・廃止・試作・古いコピー・バックアップ」は `_archive/` に物理隔離する

#### 正本外ファイルの禁則

`05_プロダクト/` 配下で正本ディレクトリの外にある HTML/PHP は **本番デプロイ対象外**。具体的に以下は禁則：

- ❌ `Gravity/LP/growthfix-*-index.html` などの古いコーポレートコピー → `_archive/` 行き
- ❌ `TrueFit/`・`GravityXxx_廃止/` などペンディング/廃止サービス → `_archive/` 行き
- ❌ `GravityCode/診断_本番/` （正本は `診断_executive_本番/`） → 素性確認後 archive 化判断
- ❌ ディレクトリ直下の古い設計メモ MD（`260227_*` `260330_*` `260414_*` など完了済タスクメモ）→ archive 化

#### lp-implementer プロンプト運用ルール（事故再発防止）

1. **デプロイマッピングは Opus メインスレッドが SSOT 照合済の状態で確定し、lp-implementer に渡す**
2. **lp-implementer に「ディレクトリ名から推測してデプロイ先を決めてください」と書かない**
3. lp-implementer が SSOT に存在しないファイルに遭遇したら **Opus にエスカレーション**
4. 大規模 grep ベース置換タスク（Blueprint legacy 一掃のような汚染除去）では、grep ヒット = 正本ではないことを必ず疑う

#### 機械チェック対応

- `lint_consistency.sh` セクション [8]「正本パターン違反検出」（260507 追加）── 正本外 HTML/PHP の有無を検出
- 四半期 1 度の `/company-os-review` で `_archive/` 候補を棚卸し
- 発見次第 `_archive/` に即移動 + `_廃止_YYMMDD_README.md` で経緯記録

**詳細：** `memory/feedback_lp_deployment_path_ssot_check.md`

### LP 社内用語ゼロ原則（260511 確立・FAQ 膨張から逆算したルール）

**Why（経緯）：** 2026-05-11、R/C LP の minimal 化作業中に FAQ④「終了後フォロー」内で `継続率 70% 目標・R の 50% より高い` という内部 KPI 数値・社内略称比較が露出していることが発覚。LP は **funnel 内側型 minimal** の運用カテゴリで「サービス内容 + 料金 + 商談誘導」を担う薄いサブ装置であり、営業提案書 v0.3（1377 行）が詳細展開の主役。LP に内部 KPI / 略称 / 運用語が混入すると ① 経営者の認知負荷増、② 競合比較の自社開示、③ 営業の主役奪い、の三重損失が発生する。**LP は外的接客語のみ、社内用語は営業提案書に閉じる**を原則化。

#### ルール

**LP 本文・FAQ・サービス進め方欄に、以下を一切書かない：**

| 種類 | 例 | 代替表現 |
|---|---|---|
| **🔴 内部 KPI 数値達成表現** | `完成度 0% → 80%` `翻訳度 0% → 50%` `発議 月1 → 月5` `エンゲージメント 4.5 → 5.5` `継続率 70% 目標` | 「3 ヶ月で〇〇な状態をつくる」等の定性表現 |
| **🔴 社内略称比較** | `R の 50% より高い` `C の 70%` `Shift Full の N%` | 比較表現自体を削除 |
| **🔴 社内略称（参謀名でない）** | `C 中核` `R 中核` `Shift R/C/Full` | 「中核プログラム」「Gravity Recruit / Cultivate」等の正式名 |
| **🟡 内部運用語** | `minimal LP` `funnel 内側型` `Push 型 / Pull 型` `二段運用` `接続装置` `信用装置` `言語マップ` `転換装置` `ハーネス` | LP には書かない（思想層 SSOT で運用） |
| **🟡 内部分類コード** | `Tier 1/2/3` `Phase 1/2` `8 項目スコア` `9 マス診断`（FAQ レベル） | 「経営者の現状ヒアリング」等の自然語 |

#### 例外（LP 残置 OK）

- **Hero バッジレベルの基本仕様**：価格・期間・対象規模 / セッション形式・録画 / Notion+PDF 納品
- **THEORY セクション内**：学術名・被引用数・論文タイトル・編集者ポジション宣言（学術濃度を意図して残す層）
- **正式なサービス名**：`Gravity Recruit` `Gravity Cultivate` `Gravity Coaching` `Gravity Scan` `Gravity CODE` `Gravity Orbit` `Gravity Shift`
- **正式な納品物名**：`3 ヶ月予言の書` `組織 OS 診断書` `躍動組織の実装書` `採用基盤の実装書` `Week 0 体験設計書`
- **正式なフレーム名（経営者向けに翻訳済）**：`Why × 才能 × 偏愛` `組織の引力 4 型（整合 / 拡散 / 渇望 / 不毛）` `4 マネジメント（数字 / 業務 / ピープル / 引力相性）`

#### NG / OK 例

```
❌ NG：継続改善は Orbit（月 15 万・最低 6 ヶ月）で実施（継続率 70% 目標・R の 50% より高い）。
✅ OK：継続改善は Orbit（月 15 万・最低 6 ヶ月）で実施。Cultivate 卒業後も多くの経営者が Orbit で伴走を継続されます。

❌ NG：採用基盤の完成度 0% → 80% × 社長の引力翻訳度 0% → 50% を 3 ヶ月で達成します。
✅ OK：3 ヶ月で採用基盤を組織に実装し、社長の引力で次の 1 名を採れる状態をつくります。

❌ NG：中間経営職育成（C 中核）の運用などの詳細は無料相談でご案内します。
✅ OK：中間経営職育成（中核プログラム）の運用などの詳細は無料相談でご案内します。
```

#### 機械チェック

- **`06_開発/scripts/lint_lp_internal_terms.py`**（260511 新規）── LP 編集後に自動実行
  - 対象：`05_プロダクト/Gravity*/LP/index.html` + `top_本番/index.html` + `service_本番/index.html`
  - 検出方法：`<section id="theory">...</section>` 範囲を除外した上で内部用語パターンを正規表現マッチ
  - 出力：HIT 行 + 該当パターン + 提案代替表現
  - 推奨運用：LP 編集後の hook で `audit_mobile_sync.py` と並列実行
- **手動実行：** `python3 06_開発/scripts/lint_lp_internal_terms.py`

#### 関連

- **営業提案書 v0.3** ── 内部 KPI 数値・略称比較は全てここに格納：`04_GrowthFix/02_マーケティング/260509_GravityRC_営業提案_サービス資料_v0.3.md`
- **接続装置.md** ── 「外的コンセプトで集めて内的世界観で磁化」原則（LP は外的接客語の領域）
- **判断基準_運用レイヤー.md** §minimal LP 戦略選択原則 ── funnel 内側型 minimal の運用カテゴリ定義

### 機械チェック対応

| スクリプト | 対象 |
|---|---|
| `audit_mobile_sync.py` | mobile.css 同期 |
| `verify_deployment.sh` | LP デプロイ後 23 項目 |
| `lint_consistency.sh` | SSOT 整合 |
| `lint_lp_internal_terms.py` | LP 社内用語ゼロ（260511 新規） |
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
