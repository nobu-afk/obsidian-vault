# gravity-scan 全参照箇所リスト（Blueprint改名対応用）

> **⚠️ 260420夕方更新：本リストは部分的に古くなっている**
>
> **事由：** 260419 B案（URL維持・表示名変更）から260420 A案（URL配置換え）に方針変更。本リストは「URLを維持する前提」で作成されたため、新A案では以下の調整が必要：
> - `/gravity-scan/` 参照の多くは **新Scan（CEO+幹部）に誘導**する参照としてOK
> - ただし**Blueprint（個人CEO）誘導を意図した参照**は `/gravity-blueprint/` に変更すべき（Step 5完了）
>
> **本リストの有効部分：** ファイル一覧・影響範囲のマッピング（構造情報）は引き続き有効。
> **本リストの無効部分：** 「URL維持前提の対応方針」は A案で上書き。最新は `260420_URL配置換え計画_Blueprint新URL_Scan差替.md` 参照。
>
> ---
>
> **作成日：** 2026-04-20
> **目的：** `/gravity-scan/` を Blueprint 命名に変更する際の影響範囲の事前把握
> **前提（260419改名ロードマップ）：** URLは `/gravity-scan/` のまま維持、ページタイトル／表示名のみ Blueprint に変更（リダイレクトなし）
> **総件数：** 46ファイル・240参照

---

## 📊 カテゴリ別サマリ

| カテゴリ | ファイル数 | 優先度 |
|---|---|---|
| 🔴 本番LP／HTML（表示名更新必須） | 15 | 高 |
| 🔴 PHP／JS（機能連携） | 7 | 高 |
| 🟡 共通テンプレート／スクリプト | 4 | 中 |
| 🟡 設定ファイル | 2 | 中 |
| 🟡 現行ドキュメント | 10 | 中 |
| 🟢 履歴ログ・過去素材 | 8 | 低（変更不要） |

---

## 🔴 Category A：本番LP／HTML（15ファイル）

### A1：Blueprint本体（旧Scan・URLは/gravity-scan/のまま）

| ファイル | 現参照箇所 | 対応 |
|---|---|---|
| `05_プロダクト/GravityScan/gravity-scan-index.html` | Hero／metadata等5箇所 | **ページタイトル・Heroを "Gravity Blueprint" に更新** |
| `05_プロダクト/GravityScan/LP/index.html` | 5箇所 | 同上（別バージョン・要統合確認） |

### A2：他LPからのBlueprintリンク（6ファイル）

| ファイル | 参照意図 | 対応 |
|---|---|---|
| `05_プロダクト/Gravity/LP/growthfix-top-index.html` | シリーズTOPからBlueprintへの導線 | 表示文言を Blueprint に変更・URL `/gravity-scan/` 維持 |
| `05_プロダクト/Gravity/LP/growthfix-service-index.html` | サービス一覧からの導線 | 同上 |
| `05_プロダクト/Gravity/LP/index.html` | Gravity Hub LP | 同上 |
| `05_プロダクト/GravityCode/gravity-code-index.html` | CODE→Blueprint誘導 | 同上 |
| `05_プロダクト/GravityCode/LP/index.html` | CODE LP 別バージョン | 同上 |
| `05_プロダクト/GravityCoaching/LP/index.html` | Coaching→Blueprint誘導 | 同上 |

### A3：他サービスLP内の参照（4ファイル）

| ファイル | 参照意図 | 対応 |
|---|---|---|
| `05_プロダクト/GravityScan/gravity-coaching-index.html` | Coaching系統 | Blueprint 表示 |
| `05_プロダクト/GravityScan/gravity-shift-index.html` | Shift系統 | 同上 |
| `05_プロダクト/GravityScan/gravity-orbit-index.html` | Orbit系統 | 同上 |
| `05_プロダクト/GravityShift/LP/index.html` | Shift→Blueprint | 同上 |
| `05_プロダクト/GravityOrbit/LP/index.html` | Orbit→Blueprint | 同上 |

### A4：Scan DEEP関連（改名後は "Scan"）（2ファイル）

| ファイル | 参照意図 | 対応 |
|---|---|---|
| `05_プロダクト/GravityScan/DEEP_本番/lp.html` | DEEP LP | **"Gravity Scan"（改名後）** に更新 |
| `05_プロダクト/GravityScan/DEEP_LP/index.html` | 別バージョン | 同上 |

### A5：WhitePaper V9（1ファイル）

| ファイル | 参照意図 | 対応 |
|---|---|---|
| `05_プロダクト/WhitePaper/V9/index.html` | WP本体からのリンク | Blueprint 更新 |

---

## 🔴 Category B：PHP／JS／診断システム（7ファイル）

| ファイル | 役割 | 対応 |
|---|---|---|
| `05_プロダクト/GravityScan/diagnose-app.js` | 診断アプリJS | 表示文言／内部名称 Blueprint に更新 |
| `05_プロダクト/GravityScan/diagnose-index.html` | 診断フォーム | 同上 |
| `05_プロダクト/GravityScan/診断_本番/app.js` | 本番用JS | 同上（フォルダ名も改名予定） |
| `05_プロダクト/GravityScan/診断_本番/index.html` | 本番フォーム | 同上 |
| `05_プロダクト/GravityScan/ヒアリング_本番/generate_report.php` | ヒアリング→レポート生成 | Blueprint／Scan の命名整理要 |
| `05_プロダクト/Gravity/LP/gf-footer.php` | 共通フッターPHP | Blueprint リンク更新 |
| `05_プロダクト/Gravity/LP/gf-footer-contact.php` | 共通フッター（お問い合わせ） | 同上 |

---

## 🟡 Category C：共通テンプレート／スクリプト（4ファイル）

| ファイル | 状態 | 対応 |
|---|---|---|
| `05_プロダクト/_共通/site-footer_template.html` | ✅ 260420更新済（Blueprint表記） | 追加変更不要 |
| `05_プロダクト/_共通/b-footer_template.html` | ✅ 260420更新済 | 追加変更不要 |
| `05_プロダクト/_共通/260416_差分リスト.md` | 参照記録 | 改名反映済 |
| `deploy.sh`（ルート） | FTPデプロイスクリプト | **パス確認要**（スクリプト内でgravity-scanを使っているか／フォルダ改名時の影響） |

---

## 🟡 Category D：設定・トラッキング（2ファイル）

| ファイル | 役割 | 対応 |
|---|---|---|
| `_assets/js/tracking.js` | GAトラッキング | **Blueprint イベント名・CV名更新**（棚卸しD関連） |
| `.claude/settings.local.json` | Claude Code settings | 参照が残っている可能性・確認要 |

---

## 🟡 Category E：現行ドキュメント（10ファイル）

### 改名ロードマップ関連

| ファイル | 対応 |
|---|---|
| `04_GrowthFix/01_サービス設計/260419_サービス改名ロードマップ_Blueprint_Scan.md` | 参照元（変更不要） |
| `04_GrowthFix/01_サービス設計/260420_戦略アップデート_RECODE1日消化版.md` | 参照記録（変更不要） |
| `04_GrowthFix/01_サービス設計/260420_実装TODO網羅リスト.md` | 参照記録（変更不要） |
| `04_GrowthFix/01_サービス設計/260401_経営アドバイザー壁打ち資料.md` | 過去資料・履歴 |
| `04_GrowthFix/00_営業/260420_Scan日程確定依頼文_ハイマネージャー_インステイト.md` | 現行営業文書 |
| `04_GrowthFix/02_マーケティング/260415_WP本文_事業の勝ち筋ループの作り方_V8_思想注入版.md` | WP素材 |
| `04_GrowthFix/02_マーケティング/LP_WP配布/index.html` | WP配布LP | **表示変更検討要** |

### 開発系ドキュメント

| ファイル | 対応 |
|---|---|
| `06_開発/260416_新セッション引継ぎ_Gravity_LP_デザイン刷新.md` | 作業記録 |
| `06_開発/260416_新セッション引継ぎ_V9_HTML編集.md` | V9編集メモ |

### Scanヒアリング関連

| ファイル | 対応 |
|---|---|
| `05_プロダクト/GravityScan/260401_Scanヒアリングガイド.md` | 現行ヒアリング素材（要更新） |
| `05_プロダクト/GravityScan/レポート/テンプレート_停滞構造レポート.md` | レポートテンプレ（旧版） |
| `05_プロダクト/GravityScan/レポート/260311_サンプル_停滞構造レポート.md` | サンプル（旧版） |
| `05_プロダクト/GravityScan/オプトイン/260316_UTAGE設定ガイド_ABテスト統合版.md` | UTAGE設定 |
| `05_プロダクト/GravityScan/オプトイン/判断グセ診断/260313_UTAGEステップメール設定ガイド.md` | ステップメール設定 |
| `05_プロダクト/GravityScan/オプトイン/盲点チェック/260313_UTAGEステップメール設定ガイド.md` | ステップメール設定 |

---

## 🟢 Category F：履歴ログ（8ファイル・変更不要）

履歴として残すべきファイル（当時の表記を保持）：

- `04_GrowthFix/04_デイリーログ/260313_daily.md`
- `04_GrowthFix/04_デイリーログ/2604_work_log.md`
- その他過去 daily ログ

---

## 🛠 実装フェーズの手順（推奨）

### Step 1: 事前準備（30分）

- [ ] 本ドキュメントで全影響範囲を再確認
- [ ] `05_プロダクト/GravityScan/LP/index.html` と `gravity-scan-index.html` の関係性を確認（本番デプロイ元はどちらか）
- [ ] `diagnose-app.js` vs `診断_本番/app.js` の関係を確認

### Step 2: 共通テンプレート（30分・完了済）

- [x] `site-footer_template.html` Blueprint化（260420済）
- [x] `b-footer_template.html` Blueprint化（260420済）

### Step 3: Blueprint本体LP（60分）

- [ ] `gravity-scan-index.html` の Hero／metadata／本文を Blueprint 刷新
- [ ] `GravityScan/LP/index.html` 同期（本番フォーカスならこちらを先）

### Step 4: 他LPからの参照更新（90分・7ファイル）

- [ ] growthfix-top / growthfix-service / Gravity Hub LP
- [ ] CODE LP 2バージョン
- [ ] Coaching LP
- [ ] Shift LP
- [ ] Orbit LP

### Step 5: PHP／JS／診断システム（60分）

- [ ] diagnose-app.js／diagnose-index.html
- [ ] 診断_本番/ 配下
- [ ] ヒアリング_本番/generate_report.php
- [ ] gf-footer.php／gf-footer-contact.php

### Step 6: DEEP 系＝改名後"Scan"（30分）

- [ ] DEEP_本番/lp.html → "Gravity Scan"（改名後）に更新
- [ ] DEEP_LP/index.html 同期

### Step 7: 設定・トラッキング（30分・棚卸しD連動）

- [ ] tracking.js のイベント名・CV名更新
- [ ] settings.local.json 参照確認

### Step 8: FTPデプロイ（30分）

- [ ] 全ファイルのサーバー同期
- [ ] 本番で表示確認（シークレットウィンドウ）

### Step 9: フォルダ改名（棚卸しB連動・60分）

- [ ] `診断_本番/` → `Blueprint_本番/`
- [ ] `DEEP_本番/` → `Scan_本番/`
- [ ] `ヒアリング_本番/` 用途確認→改名or削除判断
- [ ] `git mv` でリネーム
- [ ] 参照パス一括置換

**総所要時間：** 約6時間

---

## ⚠️ 注意事項

1. **URLは変わらない**：`/gravity-scan/` のまま維持（260419ロードマップ）
2. **表示名のみ変更**：「Gravity Scan」→「Gravity Blueprint」
3. **DEEPは「Scan」に改名**：旧DEEPファイルの表示名は「Gravity Scan」へ
4. **過去の履歴ログは変更不要**：当時の表記を保持
5. **一括実装が原則**：部分更新するとブランド混在期間が発生する

---

## 🔗 関連

- `04_GrowthFix/01_サービス設計/260419_サービス改名ロードマップ_Blueprint_Scan.md`
- `04_GrowthFix/01_サービス設計/260420_戦略アップデート_RECODE1日消化版.md`
- `04_GrowthFix/01_サービス設計/260420_実装TODO網羅リスト.md`（M-1〜M-4, O-1〜O-5 参照）
- `05_プロダクト/_共通/260416_差分リスト.md`（雛形差分・260420更新）
