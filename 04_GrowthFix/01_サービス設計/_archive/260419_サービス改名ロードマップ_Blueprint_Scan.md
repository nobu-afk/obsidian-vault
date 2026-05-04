# 🗄️【部分上書き】サービス改名ロードマップ — Blueprint／Scan

> **260419（土）確定 → 260420（月）A案で上書き**
>
> **⚠️ 260420更新：** 本ロードマップは「URL維持・表示名のみ変更」のB案だったが、260420に **A案（URL配置換え）** が採用され、本ロードマップは部分的に上書きされた。
>
> **最新版：** `260420_URL配置換え計画_Blueprint新URL_Scan差替.md`
>
> **変更差分：**
> - 旧 B案：URL `/gravity-scan/` 維持で「Blueprint」表示／URL `/gravity-scan-deep/` 維持で「Scan」表示
> - 新 A案：URL `/gravity-blueprint/` を新規作成・Blueprint配置／URL `/gravity-scan/` に新Scan配置／`/gravity-scan-deep/` → 301リダイレクト廃止
>
> **本ファイルの扱い：** 改名の思想・命名のロジックは有効。URL配置の具体策のみ A案で上書き。
>
> **起点:** 現Gravity ScanのLP実態（4ステップで設計図を描くレポート）と名称「Scan」が不整合。コンセプトと名前を一致させる。

---

## 改名内容

| 現行 | 新名称 | 実態 | 価格 |
|---|---|---|---|
| Gravity Scan | **Gravity Blueprint** | 事業の現在地から、グラビティ型成長への道筋を描くレポート | LP 20万円アンカー／体験セッション経由 10万円（実売） |
| Gravity Scan DEEP | **Gravity Scan** | CEO＋幹部を多視点でスキャンし盲点を丸裸にする診断 | CEO 20万 + 幹部1名 10万、最低2名・推奨2-3名 |

---

## サービス階段（改名後）

```
CODE         → 自分の才能を知る
Blueprint    → 事業の引力設計図を描く（個人CEO向け・10万）
Scan         → 組織の盲点をスキャンする（CEO＋幹部・40-60万）
Coaching     → 自分軸を整える
Shift        → 引力を実装する（3ヶ月・60万）
Orbit        → 軌道に乗せる（月15-25万継続）
```

**論理：自己→事業→組織→自己軸→組織変革→継続**

---

## Phase 0: 今日（4/19土）— 方針確定のみ ✅

- [x] 名称確定：Scan→Blueprint、DEEP→Scan
- [x] 1行定義確定
- [x] 価格構造確認
- [x] リダイレクト方針：**なし**（未受注・外部認知薄のため直接切り替え）
- [x] ロードマップ文書化

---

## Phase 1: 月曜（4/20）— 壁打ちで2論点＋4棚卸し

### 壁打ちで詰める2論点
- **Q35（追加）**：Blueprintの訴求対象は「社長1人」か「社長＋右腕（CFO/COO）」か？10万の価値最大化の対象設定
- **Q36（追加）**：Scan（旧DEEP）の対象幹部数の推奨（2名／3名／制限なし）と総額レンジ

### 棚卸し4項目（月曜確認）
- [ ] 広告運用中のMeta広告リンク先URL（要書き換え）
- [ ] 既存ヒアリングテンプレート `診断_本番/` `DEEP_本番/` `ヒアリング_本番/` のフォルダ名
- [ ] Orbit/Coaching等、他LPから旧Scanへのリンク
- [ ] Google Analyticsの旧URLトラッキング設定

---

## Phase 2: 火〜金（4/21-24）— ドキュメント・LP改修

### 火（21日）：ファイルリネーム
- `05_プロダクト/GravityScan/` → `GravityBlueprint/`
- `05_プロダクト/GravityScanDeep/` → `GravityScan/`
- 各サブフォルダ（`診断_本番/`等）内の命名確認

### 水（22日）：LP本体改修
**Blueprint LP（新規パス `/gravity-blueprint/`）**
- 現`/gravity-scan/` のHTMLを複製→文言差し替え（Scan→Blueprint）
- タイトル・H1・CTA・診断フォームURL変更
- FTPアップロード

**Scan LP（新規パス `/gravity-scan/`）**
- 現`/gravity-scan/deep/` のHTMLを複製→文言差し替え（DEEP→Scan）
- タイトル・H1・CTA更新
- FTPアップロード

**旧LP削除：**
- `/gravity-scan/` の旧内容を削除（新Scan LPに上書き）
- `/gravity-scan/deep/` ディレクトリ削除

### 木（23日）：共通部・診断フォーム
- `05_プロダクト/_共通/` header/footer 雛形更新（ナビのBlueprint／Scan表記）
- 7LPへ雛形展開
- 診断フォーム2本のtitle/パス書き換え：
  - `/gravity-scan/diagnose/` → `/gravity-blueprint/diagnose/`
  - `/gravity-scan/deep/diagnose/` → `/gravity-scan/diagnose/`

### 金（24日）：スキル・メモリ・資料
- `scan-prep`スキル → `blueprint-prep` にリネーム＋内容見直し
- Scan（旧DEEP）用の事前情報生成スキルが別途必要か判断
- メモリ更新：
  - `project_scan_pricing.md` → `project_blueprint_pricing.md`
  - `project_deep_pricing.md` → `project_scan_pricing.md`（旧ファイル退避＝_archive_obsolete/260419/へ）
  - `project_scan_repositioning.md` 内容更新
  - MEMORY.md のリンク・記述更新
- 事業加速アクションプラン・既存RECODE分析ファイル内の「Scan」言及を文脈に応じて書き換え

---

## Phase 3: 来週〜来々週 — 認知づくり

- Note記事「Scanという名前をBlueprintに変えた理由」（改名宣言＝設計→診断→変革の階段思想の発表）
- FB投稿で新呼称に統一
- セミナー・営業資料内の用語更新

---

## 関連ファイル
- `project_scan_pricing.md`（改修対象）
- `project_scan_repositioning.md`（改修対象）
- `project_deep_pricing.md`（改修対象）
- `260419_RECODE全チャンネル分析_143本完成版.md`（Scan言及の書き換え対象）
- `~/.claude/skills/scan-prep/SKILL.md`（改名＋内容見直し対象）
