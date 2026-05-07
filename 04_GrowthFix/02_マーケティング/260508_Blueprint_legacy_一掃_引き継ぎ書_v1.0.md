# Blueprint Legacy 一掃 引き継ぎ書 v1.0

> **ミッション：** 旧 Blueprint v6.0「採用口説きブループリント」（260430 廃止）の **語彙残骸を全 Vault から一掃**する。Scan リブート（260430）+ Shift R/C 分割（260501）+ Shift 診断 UI 廃止（260508）と並ぶ「廃止サービスの語彙的尾鰭」始末。
> **発生経緯：** 2026-05-07 夜、user 指摘「コーポレート / と /gravity/ TOP の CTA『組織の"引力"の設計図を描く』は SCAN にリンクされているが、これは Blueprint legacy では？」 → SSOT 突合で確定 → 全 Vault grep で 39+ ファイル汚染が判明
> **作成：** 2026-05-07 夜（Opus メインスレッド）
> **実行者：** 次セッション lp-implementer 別 Node（Tier 1-3）+ Opus メインスレッド（Tier 4-5 思想層判断）

---

## 0. 必読 SSOT（実行前に Read 必須）

| # | ファイル | 用途 |
|:-:|---|---|
| 1 | `05_プロダクト/_共通/SSOT_用語と定義.md` | B2 Scan Hero「自社の引力タイプを、60 分で丸裸にする」+ Scan 動詞「診る」確定 |
| 2 | `memory/project_scan_reboot_260430.md` | 「Scan = 組織の引力タイプ診断・Pre-Shift 適合診断」確定の経緯 |
| 3 | `09_会社OS/公開/ガイドライン/商品.md` | Scan 納品物 = 組織の引力タイプ判定書（4 型 + 7 項目スコア）／旧 Blueprint v6.0 廃止経緯 line 89 |
| 4 | `09_会社OS/公開/文化/判断基準.md` line 825 | 「顕在ニーズゼロのまま売り出す」NG 例として Blueprint 廃止が記録 |
| 5 | `memory/project_shift_diagnose_ui_abolished_260508.md` | Shift 診断 UI 廃止の判断（同じ系譜の語彙整理）|

---

## 1. 修正方針（Type 区別が最重要）

### Type A：旧 Blueprint v6.0 商品名・コピー残骸（**必ず修正**）

旧 Blueprint v6.0 が Scan に置き換わったが、コピーが Blueprint 時代のまま残っている箇所。

**典型例：**
- LP の Scan CTA「組織の"引力"の設計図を描く」← user 指摘
- "GRAVITY BLUEPRINT" 直接表記
- "Blueprint（10 万・60 分）" 商品名表記
- Scan 納品物が「設計図」と書かれている

### Type A2：URL `/gravity-blueprint/` 直接参照（**必ず修正**）

`/gravity-blueprint/` は 260430 で `/gravity-scan/` に 301 リダイレクトされているが、生 URL を直接書いている箇所がある。

### Type B：思想層の「設計図」概念（**原則維持・要再判断**）

Blueprint 商品名とは別レイヤーで、経営思想・翻訳概念として「設計図」を使っている箇所。

**典型例：**
- 09_会社OS/翻訳.md「個人引力 → 組織設計図」（翻訳概念図）
- 09_会社OS/Why.md「鎖を外す設計図」
- 09_会社OS/design.md「変革の参謀 = 引力の設計図を組織に実装する」
- 09_会社OS/接続装置.md「統合実装設計図」（マーケ設計概念）

**判断：** これらは **「人が動く構造を可視化したもの」**という一般語としての設計図で、Blueprint 商品名ではない。**Tier 5 で個別に Opus が判断**（Scan 商品コピー文脈で使われていたら修正、思想語ならば維持）。

### Type C：廃止注記・歴史記録（**触らない**）

- `_archive/` 配下
- worklog / daily / セッション記録
- 引き継ぎ書のクローズ注記
- 廃止経緯 memory（廃止記録として残すべき）

### Type D：System ファイル（**別判断**）

- `_共通/tracking.js`
- `GravityScan/config.php`
- `_共通/_OGP画像_運用ルール.md`

→ 機能的に Blueprint URL を参照している可能性。Tier 3 で個別確認。

---

## 2. 影響範囲インベントリ（39+ ファイル・5 Tier）

### 🔴 Tier 1：本番 LP TOP CTA（user-visible 最優先・即時修正）

| # | ファイル | 行 | 内容 |
|:-:|---|:-:|---|
| 1 | `05_プロダクト/top_本番/index.html` | 119 | コーポレート / TOP CTA「組織の"引力"の設計図を描く」 |
| 2 | `05_プロダクト/top_本番/index.html` | 226 | サービスカード文「経営者の引力が…60 分で設計図にする」 |
| 3 | `05_プロダクト/Gravity/LP/index.html` | 65 | /gravity/ TOP CTA「組織の"引力"の設計図を描く」 |
| 4 | `05_プロダクト/Gravity/LP/index.html` | 387 | Trial branch desc「一枚の設計図に落とし込む 60 分」 |
| 5 | `05_プロダクト/Gravity/LP/index.html` | 407 | FAQ「設計図を組織に実装したい場合は…」 |
| 6 | `05_プロダクト/Gravity/LP/index.html` | 415 | FAQ「設計図を組織に実装する集中期間」 |

### 🟡 Tier 2：LP 本体（28 ファイル中の Scan 商品コピー文脈）

| # | ファイル | 主な箇所 |
|:-:|---|---|
| 7 | `05_プロダクト/GravityScan/LP/index.html` | Scan 自身の LP に「設計図」「BLUEPRINT」混在 |
| 8 | `05_プロダクト/GravityCode/LP/sample-report.html` | line 447-448「設計図として返す」（CODE の出力文脈・別判断）|
| 9 | `05_プロダクト/GravityCode/LP/index.html` | CODE LP の言及 |
| 10 | `05_プロダクト/GravityRecruit/LP/index.html` | Recruit LP の言及 |
| 11 | `05_プロダクト/GravityCultivate/LP/index.html` | Cultivate LP の言及 |
| 12 | `05_プロダクト/TrueFit/LP/coaching/index.html` | Coaching LP の言及 |
| 13 | `05_プロダクト/WhitePaper/V9/index.html` | WP V9 内の言及 |
| 14 | `05_プロダクト/Gravity/LP/seminar-acting.html` | 5/15 セミナー LP の言及 |
| 15 | `05_プロダクト/Gravity/LP/seminar-ceiling.html` | 旧セミナー LP「GRAVITY BLUEPRINT」直接表記 |
| 16 | `05_プロダクト/Gravity/LP/growthfix-top-index.html` | 古いトップコピー（本番不在の確認必要）|
| 17 | `05_プロダクト/Gravity/LP/growthfix-service-index.html` | 古いサービス一覧（本番不在の確認必要）|
| 18 | `05_プロダクト/Gravity/LP/gf-footer.php` | フッター PHP に `/gravity-blueprint/` URL 残存 |
| 19 | `05_プロダクト/Gravity/LP/gf-footer-contact.php` | 同上 |

### 🟠 Tier 3：診断 UI / Sample Report / System（Scan AI 生成プロンプト含む）

| # | ファイル | 主な箇所 |
|:-:|---|---|
| 20 | `05_プロダクト/GravityScan/診断_本番/generate.php` | line 370, 399, 455, 846, 906「組織の引力を強める設計図」AI プロンプト |
| 21 | `05_プロダクト/GravityScan/診断_本番/style.css` | CSS class 名に Blueprint 残存可能性 |
| 22 | `05_プロダクト/GravityScan/config.php` | Scan 設定で Blueprint 参照可能性 |
| 23 | `05_プロダクト/GravityCode/診断_本番/generate.php` | CODE プロンプトに「設計図」混入可能性 |
| 24 | `05_プロダクト/GravityCode/診断_executive_本番/generate.php` | Executive プロンプト |
| 25 | `05_プロダクト/GravityCode/レポート/260507_長谷さんダミー_生成レポート_v5.3.3b_本番.html` | 5/8 モニター用ダミー（要 Blueprint 残存確認）|
| 26 | `05_プロダクト/_共通/tracking.js` | UTM/イベント tracking で blueprint URL 参照 |
| 27 | `05_プロダクト/_共通/_OGP画像_運用ルール.md` | OGP 画像の旧 URL 参照 |

### 🟢 Tier 4：マーケ・営業文書（4_GrowthFix 配下・現役 vs 履歴の判別必要）

| # | ファイル | 判定 |
|:-:|---|---|
| 28 | `04_GrowthFix/02_マーケティング/260507_LP_SSOT整合チェック_引き継ぎ書_v1.0.md` | 現役・要修正 |
| 29 | `04_GrowthFix/02_マーケティング/260507_本日反映チェックリスト_v1.0.md` | 現役・要修正 |
| 30 | `04_GrowthFix/02_マーケティング/260505_ブランディングロードマップ_7軸.md` | 現役・要修正 |
| 31 | `04_GrowthFix/02_マーケティング/260506_チャネル機能配分_v1.0.md` | 現役・要修正 |
| 32 | `04_GrowthFix/02_マーケティング/260430_外的コンセプト言語マップ.md` | 現役・要修正 |
| 33 | `04_GrowthFix/02_マーケティング/260430_育成メール5通_v2_5層モデル準拠版.md` | 配信前なら修正・配信済なら触らない |
| 34 | `04_GrowthFix/02_マーケティング/260423_情報発信_*` | 履歴 or 現役要確認 |
| 35 | `04_GrowthFix/00_営業/*Sushitech*` 9 ファイル | **送信済み履歴 → 触らない**（Type C）|

### 🟣 Tier 5：09_会社OS 思想層（11 MD・Type B 区別が肝）

| # | ファイル | 判断方針 |
|:-:|---|---|
| 36 | `09_会社OS/公開/ガイドライン/商品.md` line 533-534 | Scan 納品物文脈の「設計図」→ 「引力タイプ判定」に置換 |
| 37 | `09_会社OS/公開/ガイドライン/翻訳.md` line 108-111 | 翻訳概念図「個人引力 → 組織設計図」→ 思想語として保留・要再判断 |
| 38 | `09_会社OS/公開/ガイドライン/design.md` line 99 | 「変革の参謀 = 引力の設計図を組織に実装」→ 思想語として維持可能 |
| 39 | `09_会社OS/公開/経営思想/Why.md` line 209 | Scan「鎖を外す設計図」→ 「引力タイプを丸裸にする」に置換 |
| 40 | `09_会社OS/公開/経営思想/引力.md` line 137 | Scan「引力源 → 組織設計図への翻訳」→ 表現再検討 |
| 41 | `09_会社OS/公開/経営思想/接続装置.md` 複数箇所 | 「統合実装設計図」「5 層モデル実装設計図」→ 思想語として維持可能 |
| 42 | `09_会社OS/公開/文化/判断基準.md` line 825 | **触らない**（廃止経緯記録・Type C）|
| 43 | `09_会社OS/00_README.md` line 184 | 「Blueprint → Scan 機械置換完了」（履歴記録・Type C・触らない）|

---

## 3. 置換マップ

### 3.1 Scan CTA / Hero 系（user 確定済 = 「組織の"引力タイプ"を診断する」）

| 旧表記 | 新表記 |
|---|---|
| 組織の"引力"の設計図を描く | **組織の"引力タイプ"を診断する** |
| 60 分で設計図にする | **60 分で引力タイプを診る** |
| 組織の引力を強める設計図 | **組織の引力タイプ判定（4 型 + 7 項目スコア）** |
| GRAVITY BLUEPRINT | **GRAVITY SCAN**（Scan レポート名）|
| 引力の設計図 | **引力タイプ判定書** |
| 一枚の設計図に落とし込む 60 分 | **一枚の引力タイプ判定書に落とし込む 60 分** |
| 設計図を組織に実装したい | **引力タイプの方角に合わせて組織に実装したい** |
| 設計図を組織に実装する集中期間 | **引力タイプを組織に実装する集中期間** |

### 3.2 URL 系

| 旧 URL | 新 URL |
|---|---|
| `/gravity-blueprint/` | `/gravity-scan/`（既に 301 稼働中だが直接書き換え推奨）|

### 3.3 商品名系

| 旧表記 | 新表記 |
|---|---|
| Blueprint（10 万・60 分） | **Scan（10 万・60 分）** |
| 採用口説きブループリント | **組織の引力タイプ診断**（Pre-Shift 適合診断）|
| 面接ブループリント 5 要素 | **採用基盤実装書 12 要素**（Shift R Week 1-2 納品物）|

### 3.4 思想層（Tier 5・要再判断）

| 文脈 | 判断方針 |
|---|---|
| 翻訳概念図「個人引力 → 組織設計図」| Scan の出力名と同期するなら「組織の引力タイプ判定」に置換／思想語として残すなら維持 |
| 「変革の参謀 = 引力の設計図を組織に実装」| Shift R/C の役割定義。「引力の設計図」= Scan 出力 = 引力タイプ判定。表現変更検討 |
| 「鎖を外す設計図」（Why.md）| Scan の効能。「引力タイプを丸裸にして鎖を見える化する」に書き換え推奨 |
| 「統合実装設計図」（接続装置.md）| 内部設計概念・思想語として維持可能 |
| 「5 層モデル実装設計図」| 内部設計概念・思想語として維持可能 |

---

## 4. 実行プロトコル

### Phase 1：Tier 1 即時修正（lp-implementer 別 Node・1-2h）

最優先 6 箇所（top_本番 + Gravity/LP/index.html）を一気に修正 → FTP デプロイ → mobile audit → lint。

**実行：lp-implementer**

### Phase 2：Tier 2-3 LP / 診断 UI 棚卸し（lp-implementer 別 Node・3-4h）

LP 12 ファイル + 診断 UI 6 ファイル + System 3 ファイル = 21 ファイルを Tier 1 と同じ置換マップで一括処理。

**判定：** 各ファイル開いて Scan 商品コピー文脈の「設計図」「Blueprint」を §3 マップで置換。Type B 思想層は触らない。

**実行：lp-implementer**

### Phase 3：Tier 4 マーケ文書整理（Opus メインスレッド・30 分）

引き継ぎ書 v1.0（260507）/ ロードマップ /チェックリスト等の現役マーケ文書を Tier 1 結果反映 + Type B 残置で整理。送信済み営業文書は触らない。

**実行：Opus**

### Phase 4：Tier 5 思想層 09_会社OS 個別判断（Opus メインスレッド・1-2h）

11 MD を 1 件ずつ：
- Scan 商品コピー文脈 → 置換
- 思想層・翻訳概念 → 維持
- 廃止経緯記録 → 維持

**実行：Opus**

### Phase 5：lint + 検証 + worklog（lp-implementer or Opus・15 分）

- `bash 06_開発/scripts/lint_consistency.sh` で SSOT 整合確認
- 本番 HTTP 検証：/, /gravity/ で「設計図」grep してゼロ確認
- worklog 追記

---

## 5. lp-implementer 起動プロンプトテンプレ

### Phase 1（即時 6 箇所）

```
260508_Blueprint_legacy_一掃_引き継ぎ書_v1.0.md §2 Tier 1 + §3.1 置換マップに従って、
以下 6 箇所を一気に修正してください。

## 対象（6 箇所）
- /Users/ishiinobuyuki/Documents/Obsidian Vault/05_プロダクト/top_本番/index.html line 119, 226
- /Users/ishiinobuyuki/Documents/Obsidian Vault/05_プロダクト/Gravity/LP/index.html line 65, 387, 407, 415

## 置換ルール（§3.1 マップ）
- 「組織の"引力"の設計図を描く」→「組織の"引力タイプ"を診断する」
- 「60 分で設計図にする」→「60 分で引力タイプを診る」
- 「一枚の設計図に落とし込む 60 分」→「一枚の引力タイプ判定書に落とし込む 60 分」
- 「設計図を組織に実装したい」→「引力タイプの方角に合わせて組織に実装したい」
- 「設計図を組織に実装する集中期間」→「引力タイプを組織に実装する集中期間」

## 実行手順
1. Edit ツールで 6 箇所修正
2. FTP デプロイ：
   - /growthfix.jp/public_html/index.html ← top_本番/index.html
   - /growthfix.jp/public_html/gravity/index.html ← Gravity/LP/index.html
3. 本番反映確認：curl で / と /gravity/ を fetch して「設計図」grep ゼロ確認
4. mobile audit：python3 06_開発/scripts/audit_mobile_sync.py
5. lint：bash 06_開発/scripts/lint_consistency.sh
6. worklog 追記

## エスカレーション基準
- §3.1 マップで該当しない「設計図」表記を発見 → §1 Type B 思想層判断のため Opus に戻す
- LP 構造が壊れる（CSS class / data-wow-delay 等）→ Opus 判断
```

### Phase 2（Tier 2-3 全件）

Phase 1 完了後・別プロンプトで起動。

---

## 6. 完了基準

### Phase 1 完了基準

- [ ] top_本番/index.html + Gravity/LP/index.html から `設計図` grep でゼロ
- [ ] 本番 / と /gravity/ で `設計図を描く` grep ゼロ
- [ ] mobile audit clean
- [ ] lint 全 PASS
- [ ] worklog 追記

### 全 Phase 完了基準

- [ ] 39+ ファイルから Type A/A2 残存ゼロ（grep `BLUEPRINT\|設計図を描く\|gravity-blueprint`）
- [ ] Type B 思想層の判断記録（残置 / 置換）が 09_会社OS Part 3 に明記
- [ ] 本番 LP 全 20 ページで `設計図` grep ゼロ
- [ ] Scan 診断 UI の AI プロンプトが「組織の引力タイプ判定」ベースに統一
- [ ] memory/project_blueprint_legacy_cleanup_260508.md（廃止経緯）作成
- [ ] MEMORY.md にポインタ追加

---

## 7. FTP 認証情報

```
USER:   xs992119
PASS:   cgq1fv99
SERVER: ftp://sv16489.xserver.jp
BASE:   /growthfix.jp/public_html/
```

---

## 8. 関連ファイル

- 上位 SSOT：`memory/project_scan_reboot_260430.md`
- 廃止経緯（同系譜）：`memory/project_shift_diagnose_ui_abolished_260508.md`
- LP SSOT 整合チェック引き継ぎ書（260507）：`260507_LP_SSOT整合チェック_引き継ぎ書_v1.0.md`
- worklog：`04_GrowthFix/04_デイリーログ/2605_work_log.md`

---

## 9. コピペ用プロンプト

### Phase 1 開始（lp-implementer 別 Node）

```
260508_Blueprint_legacy_一掃_引き継ぎ書_v1.0.md §5 Phase 1 のプロンプトテンプレに従って、
Tier 1 の 6 箇所を一気に修正 + FTP デプロイ + 検証してください。
```

### Phase 2 開始（Phase 1 完了後）

```
260508_Blueprint_legacy_一掃_引き継ぎ書_v1.0.md §2 Tier 2-3 (21 ファイル) を
§3.1 / §3.2 / §3.3 置換マップで一括処理してください。
Type B 思想層に該当する箇所を発見したら Opus に戻す。
```
