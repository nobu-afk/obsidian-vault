# URL配置換え計画：Blueprint新URL＋Scan URL差替（260420）

> **作成：** 2026-04-20
> **起点：** 260420 石井提案（M-7後・G-2完了後）
> **置換対象：** `260419_サービス改名ロードマップ_Blueprint_Scan.md`（部分上書き）
> **重要度：** 🔴 最大（URL構造の根本変更）

---

## 🎯 方針確定（260420 A案採用）

### Before（260419 決定）
URL維持・表示名のみ変更
```
/gravity-scan/        ← 「Blueprint」表示（URLは不整合）
/gravity-scan-deep/   ← 「Scan」表示（URLは不整合）
```

### After（260420 A案）
**URL配置換え＋リダイレクト**
```
/gravity-blueprint/   ← 新規URL（現 /gravity-scan/ のコンテンツ移植）
/gravity-scan/        ← 新Scan配置（現 /gravity-scan-deep/ のコンテンツ更新）
/gravity-scan-deep/   ← 301リダイレクト → /gravity-scan/
```

---

## 📐 URLとサービス対応表（最終形）

| URL | サービス | 対象 | 価格 | 診断URL |
|---|---|---|---|---|
| `/gravity-blueprint/` | Gravity Blueprint | 個人CEO | 10万（アンカー20万） | `/gravity-blueprint/diagnose/` |
| `/gravity-scan/` | Gravity Scan（新） | CEO＋幹部2-3名 | 30-50万 | `/gravity-scan/diagnose/`（旧DEEP診断システムをベースに拡張） |
| `/gravity-scan-deep/` | 🗄️ 廃止 | - | - | 301リダイレクト |

---

## 📊 リダイレクト設計（.htaccess）

```apache
# 旧 /gravity-scan/（Blueprint相当時代）→ 新 /gravity-blueprint/
# ⚠️ 注意：このリダイレクトは一切しない
# 理由：/gravity-scan/ は「新Scan」として再利用するため、過去のリンクは「新Scan」を見せて良い
# SEO資産：被リンクは「新Scan」のURL評価として継承される

# 旧 /gravity-scan-deep/ → 新 /gravity-scan/
RewriteEngine On
RewriteRule ^gravity-scan-deep/?$ /gravity-scan/ [R=301,L]
RewriteRule ^gravity-scan-deep/(.*)$ /gravity-scan/$1 [R=301,L]
```

**SEO戦略：**
- `/gravity-scan/` の既存被リンク → 新Scan（CEO+幹部診断）ページへ引き継ぎ（自然・アクセスした人は「Scan」を見るので違和感なし）
- `/gravity-scan-deep/` の被リンク → 301で `/gravity-scan/` に統合
- `/gravity-blueprint/` は新URL：**Note連載・SNS・メール等で新URL告知を積極的に行う**ことでSEO資産を育てる
- ※ 旧Blueprint（/gravity-scan/）コンテンツ時代の被リンクは少数のため、移行ロスは最小

---

## 🛠 実装ステップ（7段階・総所要 6-8h）

### Step 1：ローカル準備（新ディレクトリ構造の設計）（30分）

- [ ] `05_プロダクト/GravityBlueprint/` ディレクトリ新規作成
  ```
  GravityBlueprint/
  ├── LP/
  │   ├── index.html（現 /gravity-scan/ のLPを移植）
  │   ├── script.js
  │   └── styles.css（必要なら）
  └── 診断_本番/
      ├── app.js（現 GravityScan/診断_本番/ を移植）
      ├── generate.php
      ├── index.html
      └── style.css
  ```
- [ ] `05_プロダクト/GravityScan/` のコンテンツを「新Scan（CEO+幹部診断）」仕様に変更準備
  - 現 `LP/index.html` を `_archive/` へ退避
  - 現 `DEEP_本番/lp.html` を新 `LP/index.html` へ発展・統合
  - 現 `DEEP_本番/` の診断システムを `診断_本番/` へ統合

### Step 2：GravityBlueprint/ 新規作成（1h）

- [ ] ディレクトリ構造作成
- [ ] `GravityScan/LP/index.html`（Blueprint版）→ `GravityBlueprint/LP/index.html` へコピー
- [ ] `GravityScan/LP/script.js` → `GravityBlueprint/LP/script.js`
- [ ] `GravityScan/診断_本番/` 全ファイル → `GravityBlueprint/診断_本番/`
- [ ] 各ファイル内の参照URL修正：
  - 内部リンク `/gravity-scan/` → `/gravity-blueprint/`
  - Footer内の「Blueprint」リンク先を `/gravity-blueprint/` に更新
- [ ] Footerの footer-current クラスを Blueprint に適用

### ✅ Step 1-2 完了（2026-04-20実施）

**完了内容：**
- `GravityBlueprint/` 新ディレクトリ作成（`LP/` + `診断_本番/` + 各 `_archive/`）
- 現 `GravityScan/LP/` と `GravityScan/診断_本番/` の内容を `GravityBlueprint/` にコピー
- GravityBlueprint/ 内の全表記を「Gravity Blueprint」に置換
- URL参照（`/gravity-scan/`→`/gravity-blueprint/`、sessionStorage key、CSS コメント等）を全更新
- `GravityScan/LP/_archive/index_260417_Blueprint版_移植前保管.html` にバックアップ配置

**残存課題（Step 3で対応）：**
- `GravityBlueprint/診断_本番/generate.php` L221 `$recommended = 'Gravity Scan DEEP';` を「Gravity Scan」（新Scan）命名に調整要

---

### ✅ Step 3-A 完了（2026-04-20実施・LPのみ）

**完了内容：**
- `GravityScan/LP/index.html` を `DEEP_LP/index.html` ベースに再構築
- 全「Gravity Scan DEEP」→「Gravity Scan」置換
- URL `/gravity-scan-deep/` → `/gravity-scan/` 更新
- FAQ の Blueprint/Scan の差別化説明を追加（新体系反映）
- Footer を G-2 統一版に差し替え（軸分離＋Profile 3点セット＋Blueprint リンク追加）
- `GravityScan/LP/_archive/index_260420_Step3移植直前_Blueprint版.html` に旧版を保管

**残存課題（Step 3-B・別日）：**
- **診断システム移行**：`GravityScan/診断_本番/` は現在 Blueprint診断が入っている（Step 1-2でコピー元として使用された）。新Scan用の multi-step 診断（CEO hearing/ Exec hearing/ Analyze/ Integrate）への置き換えが必要
- ベースファイル：`GravityScan/DEEP_本番/` 配下の5ファイル（analyze.html / hearing-ceo.html / hearing-exec.html / integrate.html / api/）を`診断_本番/` に統合
- 260420 Q27決定の3指標（硬直化4要因／熱量4象限／人材4象限）を診断プロンプトに搭載
- styles.css／script.js の整合確認（Blueprint版が残っている・新Scan LPと合わせて検証要）
- 所要：2-3h（別日）

---

### ✅ Step 3-B 完了（2026-04-20実施・診断システム移行）

**完了内容：**
- `GravityScan/診断_本番/` の旧Blueprint版コンテンツを `_archive/` に退避
- `GravityScan/DEEP_本番/` の multi-step 診断システム（5HTML + 5PHP）を `GravityScan/診断_本番/` に統合移動
- 全ファイルで「Gravity Scan DEEP」→「Gravity Scan」命名置換（10ファイル対応）
- URL参照 `gravity-scan-deep` → `gravity-scan` 置換
- `DEEP_本番/` ディレクトリ空化後削除
- `DEEP_LP/` を `_archive/DEEP_LP_260420_内容統合済_GravityScanLP/` へ退避
- `deploy.sh` を大幅刷新：
  - Blueprint 診断（個人CEO・60分単発）を新規追加
  - Scan 診断（CEO+幹部・multi-step）を旧DEEP構造で再構築（9ファイル対応）

**新しい診断システム構造：**
```
GravityScan/診断_本番/
├── _archive/                  (旧Blueprint版バックアップ)
├── index.html                 ダッシュボード
├── hearing-ceo.html           CEOヒアリング
├── hearing-exec.html          幹部ヒアリング
├── integrate.html             認識ギャップ分析
├── analyze.html               レポート生成
└── api/
    ├── project.php
    ├── hearing.php
    ├── generate-gap.php
    ├── generate-report.php
    └── generate-report_v2.php
```

**残存課題（別タスク）：**
- **Q27 3指標搭載**：硬直化4要因・熱量4象限・人材4象限をプロンプト（generate-gap.php / generate-report.php）に実装
- 所要：2-3h／プロンプト精緻化フェーズ（別日）
- TODO: J'-3 として網羅リスト記録済み

---

### Step 3-B-2（オプション）：診断プロンプト改訂（別日）

**新 `/gravity-scan/` のコンテンツ源泉：**
- `GravityScan/DEEP_本番/lp.html`（旧DEEP LP）をベースに
- 260420 Q27決定の3指標（硬直化4要因／熱量4象限／人材4象限）を搭載
- 価格：30-50万（2-3名推奨）
- ページタイトル：「Gravity Scan｜CEO＋幹部の盲点を、多視点で丸裸にする」等

- [ ] 新 `GravityScan/LP/index.html` 作成
  - DEEP_本番/lp.html をベースに全面書き起こし
  - 3指標搭載訴求
  - 「AIガラス張り診断」セクション追加（引力の整合性診断は Scan 内部機能として）
- [ ] 新 `GravityScan/診断_本番/` 構築
  - 現 `DEEP_本番/` の診断システム（hearing-ceo.html / hearing-exec.html / analyze.html / integrate.html / generate_report.php）を流用・統合
  - 「GRAVITY BLUEPRINT」命名は個人CEO向け Blueprint側に移譲
  - 新Scan のレポート名称は別途決定要（例：「GRAVITY SCAN REPORT」「組織の引力スキャン」など）

### ✅ Step 4 計画完了（2026-04-20実施）

**完了内容：**
- `.htaccess` 追記内容と手順書を `06_開発/server_config/htaccess_scan-deep_redirect.md` に整備
- リダイレクトルール（`/gravity-scan-deep/` → `/gravity-scan/`・301）
- デプロイ手順（FTP取得→編集→アップロード→確認）
- 動作確認 curl コマンド4本
- 実施チェックリスト
- 実施タイミングは「Step 6 本番デプロイ直後」と明記

**実施待ち：** サーバー側 `.htaccess` の実際の編集は Step 6（本番デプロイ）完了後に実行
- TODO: Step 6 完了後に手動で実施
- 所要：30分（エディタ作業＋FTP＋動作確認）

---

### ✅ Step 7 完了（2026-04-20実施・主要メモリ＋ドキュメント）

**完了内容：**

#### メモリ更新（5件）
- `memory/MEMORY.md` — デプロイ先URLリスト／5サービス体系／象限マッピング／Blueprint/Scan値決めリンク
- `memory/project_gravity_series_gen2_260415.md` — 冒頭に260420命名変更注記
- `memory/project_deep_pricing.md` — 命名「Scan（旧DEEP）」へ更新
- `memory/feedback_lp_header_footer_template.md` — 7LP→6LP、Blueprint/Scan命名
- `memory/user_core_mission_talent_liberation.md` — サービス階層を A案命名で更新

#### ドキュメント更新（2件）
- `260419_サービス改名ロードマップ_Blueprint_Scan.md` — 冒頭に「A案で部分上書き」注記
- `260420_gravity-scan参照箇所リスト.md` — 冒頭に「部分的に古くなっている」注記

**残存課題（別タスク化・Step 5b等）：**
- Note Vol.0/1/2骨子、FAQ v2、Sushitech動線、Scan日程依頼文のURL／命名参照調整（Step 5b-1 として TODO 記録済）
- 過去 daily ログ・weekly_close は歴史記録として維持（更新不要）

---

### Step 4b：実サーバーへの .htaccess 反映（Step 6完了後）

- [ ] サーバー `growthfix.jp/public_html/.htaccess` に追記：
  ```apache
  # Scan DEEP廃止→Scan統合（260420 A案）
  RewriteEngine On
  RewriteRule ^gravity-scan-deep/?$ /gravity-scan/ [R=301,L]
  RewriteRule ^gravity-scan-deep/(.*)$ /gravity-scan/$1 [R=301,L]
  ```
- [ ] リダイレクト動作確認（curl でステータスコード確認）

### ✅ Step 5 完了（2026-04-20実施）

**完了内容：**
- 5LP（Coaching/CODE/Orbit/Shift/Scan自身）の Footer 内 Blueprint リンクを `/gravity-scan/` → `/gravity-blueprint/` に更新
- 2雛形（site-footer_template.html / b-footer_template.html）も同様更新
- 対象 6ファイル・全箇所置換完了

**残存課題（別タスク）：**
- **本文内の Gravity Scan 参照の文脈別整合**：各LPの service-connect-band や Gravityとの違い等の本文で「Gravity Scan」と呼んでいる箇所が、Blueprint（個人CEO）を指すか新Scan（CEO+幹部）を指すか文脈別に整合確認が必要
  - 例：CODE LP L86「Gravity Scan は組織の引力を解剖します」は旧Blueprint文脈 → 「Gravity Blueprint」に変更が妥当
  - 例：Shift LP の「Scanで描いた設計図」は Blueprint 文脈 → 「Blueprint で描いた設計図」
- 所要：1-2h（各LPを丁寧に見直し）
- TODO: Step 5b として追加

---

### Step 5b：本文内 Scan/Blueprint 文脈整合（別日）

**G-2 で追加した各LPの Footer 内リンク：**
```
<a href="https://growthfix.jp/gravity-scan/">Gravity Blueprint</a>
```
↓
```
<a href="https://growthfix.jp/gravity-blueprint/">Gravity Blueprint</a>
```

- [ ] GravityCoaching/LP/index.html
- [ ] GravityCode/LP/index.html
- [ ] GravityOrbit/LP/index.html
- [ ] GravityShift/LP/index.html
- [ ] GravityScan/LP/index.html（新Scan版・完成後）
- [ ] `_共通/site-footer_template.html`（雛形）
- [ ] `_共通/b-footer_template.html`（雛形）
- [ ] Gravity Hub／Profile／Service ページ（`growthfix-top/profile/service-index.html`）

### Step 6：deploy.sh 更新＋FTPデプロイ（1h）

- [ ] `deploy.sh` に GravityBlueprint 用行追加：
  ```bash
  upload "$VAULT/05_プロダクト/GravityBlueprint/LP/index.html"     "gravity-blueprint/index.html"       "Blueprint LP"
  upload "$VAULT/05_プロダクト/GravityBlueprint/LP/script.js"      "gravity-blueprint/script.js"        "Blueprint script.js"
  upload "$VAULT/05_プロダクト/GravityBlueprint/診断_本番/app.js"  "gravity-blueprint/diagnose/app.js"  "Blueprint diagnose app.js"
  upload "$VAULT/05_プロダクト/GravityBlueprint/診断_本番/generate.php" "gravity-blueprint/diagnose/generate.php" "Blueprint diagnose generate.php"
  upload "$VAULT/05_プロダクト/GravityBlueprint/診断_本番/index.html" "gravity-blueprint/diagnose/index.html" "Blueprint diagnose index.html"
  upload "$VAULT/05_プロダクト/GravityBlueprint/診断_本番/style.css" "gravity-blueprint/diagnose/style.css" "Blueprint diagnose style.css"
  ```
- [ ] FTP一括デプロイ → 本番確認

### Step 7：ドキュメント・メモリ・GA設定 更新（1h）

- [ ] `memory/MEMORY.md` の URL リスト更新（`/gravity-scan/` の説明を「新Scan」に、`/gravity-blueprint/` を追加）
- [ ] `project_gravity_identity_gravitational.md`・`project_gravity_series_gen2_260415.md` 等の URL 言及箇所更新
- [ ] Note Vol.0/Vol.1/Vol.2 骨子内の URL 更新
- [ ] FAQ v2（260420_FAQ_想定問答集_Sushitech_v2.md）の URL 更新
- [ ] Sushitech当日動線／Scan日程依頼文 等の URL 更新
- [ ] GA4 管理画面：新URL `/gravity-blueprint/` のイベント設定追加（`260420_GA4_Blueprint改名チェックリスト.md` 実施）

---

## 📋 更新が必要なファイル・リソース一覧

### 🔴 本番サーバー
- 新規：`/gravity-blueprint/` ディレクトリ＋配下ファイル
- 更新：`/gravity-scan/` 配下（新Scan版に差替）
- 設定：`.htaccess`（301リダイレクト）
- 削除候補：`/gravity-scan-deep/` の物理ファイル（1ヶ月後に削除・301維持）

### 🟡 ローカル Vault
- 新規：`05_プロダクト/GravityBlueprint/`
- リネーム・再構築：`05_プロダクト/GravityScan/`
- アーカイブ化：`GravityScan/DEEP_LP/`、`DEEP_本番/`（→内容はGravityScan/LP/とGravityScan/診断_本番/へ統合後、_archive/へ）

### 🟢 ドキュメント・メモリ（30件以上）
- FAQ v2、Note骨子3本、Sushitech動線、Scan日程依頼文、Profile ページ
- memory: MEMORY.md、project_gravity系、user_*系
- TODO、戦略アップデート、sparring_log、scan-prep スキル（関連URL言及あれば）

---

## ⚠️ 注意事項

1. **実装順序を厳守**：Step 1→2→3→4→5→6→7
   - 特にStep 4（リダイレクト）はStep 2・3（新コンテンツ配置）完了後
   - Step 5（LP更新）は本番デプロイ後に実行しないと 404 発生
2. **GravityScan/ の既存Blueprint版コンテンツをロスト**：Step 3で上書きされる前にBackup
   - `GravityScan/LP/_archive/index_Blueprint版260417.html` として退避
   - `GravityScan/診断_本番/_archive/` にBlueprint版を退避（既にファイル移動された可能性あり・確認）
3. **リダイレクト一方向**：`/gravity-scan/` → `/gravity-blueprint/` のリダイレクトは**しない**（意図的）
   - 理由：旧Blueprint時代にアクセスした人が来ても、新Scan（CEO+幹部診断）を見せる方が顧客体験として自然
   - 旧Blueprintコンテンツ時代は極短期間（260417-260420、3日間）で被リンクもほぼない
4. **GA4計測の連続性**：新URLは別計測になる → 棚卸しD対応で新イベント追加

---

## 📅 実施タイミング

### 最速実施シナリオ
- 今日（2026-04-20）～Sushitech前（4/26）：Step 1-6完了・本番稼働
- Sushitech（4/27-28）で新URL配布（名刺QR・口頭案内）

### 標準実施シナリオ（推奨）
- 5/7（水）：Step 1-4 完了（準備）
- 5/10（土）：Step 5-6 完了（デプロイ）
- 5/14（水）：Step 7 完了（ドキュメント同期）

### リスク回避
- Sushitechまでに完了できない場合：**旧URLで配布＆後日アナウンス**
- デプロイ失敗時の戻し手順：旧 `GravityScan/` ファイルは `_archive/` 経由で復元可能

---

## 🔗 関連

- 上書き対象：`260419_サービス改名ロードマップ_Blueprint_Scan.md`（URL維持案・廃止）
- 連動：`260420_gravity-scan参照箇所リスト.md`（全参照箇所）
- 連動：`260420_フォルダ改名影響範囲リスト.md`（棚卸しB）
- 連動：`260420_GA4_Blueprint改名チェックリスト.md`（棚卸しD）
- 連動：`260420_実装TODO網羅リスト.md`（Xグループ要書き換え）
- 影響：`memory/project_gravity_integrity_diagnosis.md`（Scan内部機能としての整合性）
