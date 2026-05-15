# GrowthFix 8 ページ統合計画書 v1.0（260515）

> **目的**：現状 25 本に膨張した公開 LP を **8 ページ + WP 装置 2 ページ + 営業資料（限定公開）** に圧縮する。堀田 hajime.institute モデルを参考にした「シンプル × 高密度 × 内部編集型営業資料」構造への根本ピボット。

---

## §0. 意思決定サマリー（260515 確定）

| # | 論点 | 決定 |
|---|---|---|
| 1 | URL 設計（CODE/Coaching の位置） | **A 案：/gravity/ 配下に統合**（Gravity Coaching ブランド整合）|
| 2 | WhitePaper LP | **残す**（リード獲得装置・/whitepaper/ オプトイン + /whitepaper-read/ 本体）|
| 3 | TOP のメインメッセージ | **「組織に、引力を。」継続** |
| 4 | サービス料金の LP 表記 | **非公開化**（堀田流・問い合わせベース・参考レンジは社内資料のみ）|
| 5 | 個人サブスク 3 階級 | **見送り**（書籍刊行とコミュニティ蓄積まで凍結・2027 年以降の伏線）|
| 6 | 移行順序 | Step 1 仕様書 → Step 2 /gravity/ LP v1.0 → Step 3 アーカイブ実装 |
| 7 | 営業資料 HTML 編集権限 | **石井のみ**（業務委託編集不可）|

---

## §1. 背景：なぜ 25 → 8 ピボットか

### 1.1 PeopleX 調査（260515）からの学び

PeopleX = 累計調達 23.7 億円・社員 140 → 240 名・大手 20 社（セブン/イオン/SUBARU 等）の AgenticHR プラットフォーム。**SaaS スケール戦略**で AI 面接領域を制圧中。GrowthFix（石井 1 名 + AI + 業務委託数名）が同じ土俵で戦うのは無謀。**ニッチ路線で「経営者翻訳レイヤー」に振り切る** ことが構造的必然。

### 1.2 堀田 hajime.institute 分析（260515）からの学び

堀田さんは年商 1 億超を **約 7-8 LP** で達成している：
- 法人案件 4 種（Coaching/AIUX/AIDev/StartupAdvisory）= **全部価格非公開**
- 個人向けは 3 階級メンバーシップ（年 12-66 万・前払い）
- クライアント事例ゼロ・本人実績（AI 研究 20 年 × 2 回エグジット × 100+ メンタリング）+ 学術武装で勝負
- デザイン極度にミニマル・1 セクション 1 概念・装飾ゼロ

### 1.3 GrowthFix の構造的問題（現状）

- 公開 LP 25 本（コーポレート 12 + Gravity 13）= **過剰な保守負荷**
- 5 サービス（CODE/Scan/Shift R/Shift C/Coaching/Orbit）の **顧客接点での分かりにくさ**
- 料金 LP 明記（月 35/50/5 万）= **値切り材料を与えている**
- 業務代行性が弱い（思想層は厚いが実行層がスカスカ）

### 1.4 採用すべき構造

ユーザー意思決定：
- **法人プログラム集中**（個人サブスクは凍結）
- **「組織の引力設計」1 商品**（月 50 万 × 3 ヶ月 + 月 15 万継続）に統合
- **LP 8 ページ + WP 装置 + 営業資料**で運用負荷を激減

---

## §2. 新 8 ページ構成（公開 LP）

```
1. /                       TOP
2. /profile/              代表プロフィール
3. /achievement/          実績
4. /knowledge/            ナレッジ
5. /news/                 お知らせ
6. /gravity/              組織の引力設計（法人メイン）
7. /gravity/code/         CODE（個人軸サブページ）
8. /gravity/coaching/     Coaching（個人軸サブページ）
```

**+ リード獲得装置 2 ページ**（残置）：
```
/whitepaper/              WP V9 オプトイン LP
/whitepaper-read/         WP V9 本体（PDF 生成元）
```

**+ ユーティリティページ**（残置・必須）：
```
/contact/                 お問い合わせ
/consultation-thanks/     相談 thanks
/whitepaper-thanks/       WP thanks
/privacy-policy/          プライバシーポリシー
```

**+ 営業資料（限定公開）**：
```
/sales/master-{hash}/     営業資料マスター HTML（noindex・URL ハッシュ）
```

**実カウント**：公開メイン 8 + WP 2 + ユーティリティ 4 + 営業資料 1 = **15 リソース**（実質公開メイン LP は 8 + WP オプトイン 1 = 9 枚）

---

## §3. 各ページの内容仕様

### §3.1 `/` TOP

- **既存ファイル**：`05_プロダクト/コーポレート/top_本番/index.html`
- **メインメッセージ**：「組織に、引力を。」（継続）
- **構成**：
  1. ヒーロー（h1 = 組織に、引力を。 + サブコピー）
  2. 会社思想（引力経営とは・3 軸：集まる × 躍動する × 留まる）
  3. サービス導線（`/gravity/` への 1 メイン CTA + `/gravity/code/` `/gravity/coaching/` への 2 サブ CTA）
  4. 実績ハイライト（数値 3-5 個 + `/achievement/` 詳細導線）
  5. ナレッジハイライト（最新 Note 3 本 + `/knowledge/` 詳細導線）
  6. お問い合わせ CTA
- **料金表記**：なし（堀田流）

### §3.2 `/profile/` 代表プロフィール

- **既存ファイル**：`05_プロダクト/コーポレート/profile_本番/index.html`
- **構成**：
  1. 石井伸幸の経歴（組織人事 16 年 / MCA 16 年 / 組織の引力設計者）
  2. 思想層（Why × 才能 × 偏愛 → 強み × 想い × 偏愛・260515 確定）
  3. 学術武装（Bandura / Edmondson / Mitchell JE 等 350,000+ cites）
  4. メディア露出・登壇歴
  5. お問い合わせ CTA

### §3.3 `/achievement/` 実績

- **既存ファイル**：`05_プロダクト/コーポレート/achievement_本番/index.html`
- **構成**：
  1. 数値実績（クライアント数 / 経験年数 / 採用累計 等）
  2. クライアント事例（守秘範囲で・匿名化可）
  3. 引用論文（`/gravity-citations/` を `/achievement/citations/` 配下に統合 or 別ページ残置）
- **判断保留**：citations 統合 or 残置 → §11 で決定

### §3.4 `/knowledge/` ナレッジ

- **既存ファイル**：`05_プロダクト/コーポレート/knowledge_本番/index.html`
- **新規統合**：
  1. Note 連載インデックス（Vol 0-14 + 卒業生 S1-S8）
  2. メルマガアーカイブ
  3. WhitePaper DL（`/whitepaper/` への導線）
  4. 書籍『引力経営』情報（刊行後 = 26-27 年）
  5. メディア掲載

### §3.5 `/news/` お知らせ

- **既存ファイル**：`05_プロダクト/コーポレート/news_本番/index.html` + サブページ 2 本
- **構成**：
  1. プレスリリース時系列
  2. 登壇・セミナー告知
  3. サービスアップデート
- **既存サブページ残置**：`/news/site-renewal/` `/news/gravity-release/`

### §3.6 `/gravity/` 組織の引力設計（法人メイン）★最重要

- **既存ファイル統合元**：
  - `05_プロダクト/Gravity/_ブランド/LP/index.html`（現 /gravity/ TOP）
  - `05_プロダクト/Gravity/Recruit/LP/index.html`（現 /gravity-recruit/）
  - `05_プロダクト/Gravity/Cultivate/LP/index.html`（現 /gravity-cultivate/）
  - `05_プロダクト/Gravity/Shift/LP/index.html`（現 /gravity-shift/）
  - `05_プロダクト/Gravity/Orbit/LP/index.html`（現 /gravity-orbit/）
  - `05_プロダクト/Gravity/Scan/LP/index.html`（現 /gravity-scan/）
  - `05_プロダクト/コーポレート/service_本番/index.html`（現 /service/）
- **新コンセプト**：「組織の引力設計プログラム」1 商品
- **二段構造**（堀田 japanese.html 流）：
  - **上段（ファーストビュー）**：1 メッセージ + 3 軸（集まる × 躍動 × 留まる）+ 「3 ヶ月で組織の引力を AI 武装する」+ **価格非公開**（「ご相談ください」CTA）
  - **中段**：WBS 概要（3 ヶ月）/ 提供物リスト / 学術武装 / FAQ（タブ or アコーディオン）
  - **下段**：石井プロフィール短縮版 + 詳細プロフィール導線 + CTA 再掲
- **無料診断導線**：`/gravity-scan/web-diagnose/` を `/gravity/diagnose/` に移動 or `/gravity/` 内に埋め込み
- **詳細営業資料**：「より詳しい資料をご希望の方は問い合わせください」→ 商談時に営業資料 URL 共有

### §3.7 `/gravity/code/` CODE（個人軸サブページ）

- **既存ファイル統合元**：
  - `05_プロダクト/Gravity/Code/LP/index.html`（現 /gravity-code/）
  - `05_プロダクト/Gravity/Code/診断_本番/index.html`（現 /gravity-code/diagnose/）
  - `05_プロダクト/Gravity/Code/診断_executive_本番/index.html`（現 /gravity-code/executive/）
- **位置付け**：経営者個人引力タイプ診断（強み × 想い × 偏愛）
- **構成**：
  1. CODE とは（個人引力の 3 要素）
  2. 4 型紹介（整合 / 拡散 / 渇望 / 不毛 → ※ 4 型は SCAN だった・要再整理）
  3. 診断 CTA（無料診断 → `/gravity/code/diagnose/`）
  4. CODE → /gravity/（組織引力設計）導線

### §3.8 `/gravity/coaching/` Coaching（個人軸サブページ）

- **既存ファイル統合元**：
  - `05_プロダクト/Gravity/Coaching/LP/index.html`（現 /gravity-coaching/）
- **位置付け**：Gravity Coaching（個人軸エグゼクティブコーチング）
- **構成**：
  1. Gravity Coaching とは
  2. 提供内容・期間・回数
  3. **料金非公開**（260515 確定方針に従う）
  4. CTA：お問い合わせ
  5. CODE 診断 → Coaching 動線

---

## §4. WhitePaper 装置（追加リード獲得）

| URL | ファイル | 位置付け | 処置 |
|---|---|---|---|
| `/whitepaper/` | `05_プロダクト/コーポレート/whitepaper_optin_本番/index.html` | **オプトイン LP**（メール → PDF DL）| 残置 |
| `/whitepaper-read/` | `05_プロダクト/Gravity/WhitePaper/V9/index.html` | **WP V9 本体** | 残置 |
| `/whitepaper-thanks/` | `05_プロダクト/コーポレート/whitepaper-thanks_本番/index.html` | thanks ページ | 残置 |
| `/whitepaper.pdf` | `05_プロダクト/Gravity/WhitePaper/V9/gravity-whitepaper-v9.pdf` | PDF 本体 | 残置 |

**deploy.sh ルール（260515 確定済）**：deploy_optin / deploy_wp 関数経由のみ。upload() の Layer 4 ガード継続。

---

## §5. 統合元マップ（25 LP → 8 ページ）

### §5.1 そのまま残置（既存活用）

| 新 URL | 既存ファイル | 処置 |
|---|---|---|
| `/` | `top_本番/` | 既存活用 + 新サービス導線追加 |
| `/profile/` | `profile_本番/` | 既存活用 + 思想層強化 |
| `/achievement/` | `achievement_本番/` | 既存活用 + citations 統合判断 |
| `/knowledge/` | `knowledge_本番/` | 既存活用 + コンテンツ装置強化 |
| `/news/` | `news_本番/` | 既存活用 |
| `/contact/` | `contact_本番/` | 既存活用 |
| `/consultation-thanks/` | `consultation-thanks_本番/` | 既存活用 |
| `/privacy-policy/` | `privacy-policy_本番/` | 既存活用 |
| `/whitepaper/` | `whitepaper_optin_本番/` | 既存活用 |
| `/whitepaper-read/` | `Gravity/WhitePaper/V9/` | 既存活用 |
| `/whitepaper-thanks/` | `whitepaper-thanks_本番/` | 既存活用 |

### §5.2 統合・再構築（/gravity/ 1 枚化）

| 既存 URL | 既存ファイル | 処置 |
|---|---|---|
| `/gravity/` | `Gravity/_ブランド/LP/` | **/gravity/ メイン LP に再設計**（v2.0）|
| `/gravity-recruit/` | `Gravity/Recruit/LP/` | → `/gravity/` 内セクションに統合・301 |
| `/gravity-cultivate/` | `Gravity/Cultivate/LP/` | → `/gravity/` 内セクションに統合・301 |
| `/gravity-shift/` | `Gravity/Shift/LP/` | → `/gravity/` に統合・301 |
| `/gravity-orbit/` | `Gravity/Orbit/LP/` | → `/gravity/` 内「継続フェーズ」セクションに統合・301 |
| `/gravity-scan/` | `Gravity/Scan/LP/` | → `/gravity/` 内「無料診断」セクションに統合・301 |
| `/gravity-scan/web-diagnose/` | `Gravity/Scan/web-diagnose_本番/` | → `/gravity/diagnose/` に移動（診断 UI のみ残す）|
| `/service/` | `コーポレート/service_本番/` | → `/gravity/` に統合・301 |

### §5.3 サブページに圧縮

| 既存 URL | 既存ファイル | 処置 |
|---|---|---|
| `/gravity-code/` | `Gravity/Code/LP/` | → `/gravity/code/` に移動・301 |
| `/gravity-code/diagnose/` | `Gravity/Code/診断_本番/` | → `/gravity/code/diagnose/` に移動・301 |
| `/gravity-code/executive/` | `Gravity/Code/診断_executive_本番/` | → `/gravity/code/executive/` に移動・301 |
| `/gravity-coaching/` | `Gravity/Coaching/LP/` | → `/gravity/coaching/` に移動・301 |

### §5.4 判断保留

| 既存 URL | 候補処置 |
|---|---|
| `/gravity-citations/` | A) `/achievement/citations/` に統合 / B) `/gravity/citations/` で残置 / C) そのまま残置 |
| `/academy-wl/` | A) 残置（Academy 想起装置）/ B) アーカイブ |

---

## §6. 301 リダイレクト一覧

`.htaccess` または Apache config 設定：

```apache
# Gravity サービス LP 統合（→ /gravity/）
Redirect 301 /gravity-recruit/ /gravity/
Redirect 301 /gravity-cultivate/ /gravity/
Redirect 301 /gravity-shift/ /gravity/
Redirect 301 /gravity-orbit/ /gravity/
Redirect 301 /gravity-scan/ /gravity/
Redirect 301 /service/ /gravity/

# Scan 診断 UI（→ /gravity/diagnose/）
Redirect 301 /gravity-scan/web-diagnose/ /gravity/diagnose/

# CODE（→ /gravity/code/）
Redirect 301 /gravity-code/ /gravity/code/
Redirect 301 /gravity-code/diagnose/ /gravity/code/diagnose/
Redirect 301 /gravity-code/executive/ /gravity/code/executive/

# Coaching（→ /gravity/coaching/）
Redirect 301 /gravity-coaching/ /gravity/coaching/
```

**SEO 影響対策**：Search Console で検索流入の多いページを事前確認。リダイレクト先のページ内に元 URL のメインキーワードを含むセクションを必ず配置。

---

## §7. 営業資料 HTML 限定公開設計

### §7.1 ディレクトリ構造

```
05_プロダクト/コーポレート/sales_本番/        ← 編集場所（石井のみアクセス）
  master/
    index.html                                ← 営業資料マスター（SSOT）
    assets/                                    ← 画像・CSS
  pdf/
    260515_営業資料_v1.0.pdf                  ← ビルド成果物
```

### §7.2 限定公開機構：URL ハッシュ方式

- **本番 URL**：`/sales/master-a8f3k2x9/`（推測不能ハッシュ）
- **noindex 設定**：`<meta name="robots" content="noindex,nofollow">`
- **sitemap.xml に含めない**
- **`.htaccess` でディレクトリリスト禁止**：`Options -Indexes`

ハッシュは商談ごとに変更可（運用負荷下げるなら半年 1 回 rotation）。

### §7.3 HTML → PDF 変換

新規スクリプト：`06_開発/scripts/sales/build_sales_pdf.sh`

```bash
#!/bin/bash
# 営業資料 HTML → PDF 変換
INPUT="05_プロダクト/コーポレート/sales_本番/master/index.html"
OUTPUT="05_プロダクト/コーポレート/sales_本番/pdf/$(date +%y%m%d)_営業資料_v$1.pdf"

# wkhtmltopdf or puppeteer
wkhtmltopdf --enable-local-file-access "$INPUT" "$OUTPUT"
```

または puppeteer 版（推奨・レンダリング精度高）：

```javascript
// 06_開発/scripts/sales/build_sales_pdf.js
const puppeteer = require('puppeteer');
// ... HTML → PDF 変換
```

### §7.4 deploy.sh への新関数追加

```bash
deploy_sales() {
  # /sales/ 配下を本番にアップロード
  # Layer 4 ガード対応（sales 配下は本番アップロード可）
}
```

### §7.5 営業資料の構造（v1.0 案）

| ページ | 内容 |
|---|---|
| 1 表紙 | 「組織の引力設計プログラム」+ 提案日 |
| 2 課題提起 | SME 経営者の人事ペイン 5 つ |
| 3 GrowthFix のポジション | PeopleX / 識学 / マルゴト人事との差別化マトリクス |
| 4 3 軸（集まる × 躍動 × 留まる） | 各軸の学術武装と提供物 |
| 5 WBS（3 ヶ月） | Week 1-12 の詳細ガントチャート |
| 6 提供物リスト | 12 要素 + 3 設計 + 月次レポート + AI Bot 3 体 |
| 7 投資レンジ | 複数プラン（最小構成 / 標準 / フルパッケージ）|
| 8 継続フェーズ | 月 15 万の中身（壁打ち + 保守 + 月次レポート）|
| 9 石井経歴 | 組織人事 16 年 / MCA 16 年 / 組織の引力設計者 |
| 10 ご相談の流れ | 初回相談 → 診断 → 提案 → 契約 |

### §7.6 編集権限

- **石井のみ編集可**（業務委託は閲覧のみ）
- 物理パス `05_プロダクト/コーポレート/sales_本番/master/index.html` は石井 Mac のみ
- Git 管理対象（バージョン履歴保持）

---

## §8. アーカイブ手順

### §8.1 物理アーカイブ先

新規作成：`05_プロダクト/_archive_8pages_pivot_260515/`

```
_archive_8pages_pivot_260515/
  Gravity_Recruit_LP/
  Gravity_Cultivate_LP/
  Gravity_Shift_LP/
  Gravity_Orbit_LP/
  Gravity_Scan_LP/
  service_本番/
```

### §8.2 本番サーバー側

- 本番削除しない（即時切り戻し可能性のため）
- `/_archive_260515/` ディレクトリに移動
- 301 リダイレクトで `/gravity/` に転送

### §8.3 deploy.sh 更新

- `deploy_lp` 関数から旧 LP（Recruit/Cultivate/Shift/Orbit/Scan/service）を **コメントアウト**（削除ではなく）
- Layer 4 ガードに `_archive_8pages_pivot_260515/` 配下からの本番アップロード BLOCK 追加

---

## §9. SSOT 反映項目

### §9.1 必須更新

| ファイル | 更新内容 |
|---|---|
| `05_プロダクト/_共通/SSOT_用語と定義.md` | 「5 サービス」→「1 メインプログラム + 個人軸 2 サブサービス」に変更。料金記述削除（or 内部参考値として注記）|
| `09_会社OS/商品.md` | 商品構造再定義。R/C/Orbit の独立記載 → 統合プログラムとして再構成 |
| `09_会社OS/接続装置.md` | 5 層モデルとの整合性確認・LP マッピング表更新 |
| `09_会社OS/design.md` | 8 ページ構造を Part 3 ハーネス層に明記 |
| `09_会社OS/発信.md` | LP 統合に伴う発信動線変更 |
| `06_開発/scripts/lint/lint_consistency.sh` | 旧 URL（/gravity-recruit/ 等）の参照を検出する lint 追加 |
| `CLAUDE.md` | 本番 LP マッピング 6 サービス → 8 ページ構造に書き換え |

### §9.2 memory 反映

新規 project memory：`project_8pages_pivot_260515.md`

---

## §10. lint / verify 対応

### §10.1 lint 拡張

`06_開発/scripts/lint/lint_consistency.sh` に追加チェック：

```bash
# 旧 Gravity サービス LP URL の検出
grep -r "gravity-recruit\|gravity-cultivate\|gravity-shift\|gravity-orbit\|gravity-scan" \
  05_プロダクト/ --include="*.html" --include="*.md" \
  | grep -v "_archive" | grep -v "301"
# 検出時は警告
```

### §10.2 verify_deployment.sh 拡張

- `/gravity/` の特徴語（「組織の引力設計」「集まる × 躍動 × 留まる」）必須
- `/gravity-recruit/` 等への直接アクセスが 301 で `/gravity/` にリダイレクトされることを確認

---

## §11. 実装スケジュール

| Step | 内容 | 目安 |
|---|---|---|
| **Step 1**（本書）| 8 ページ統合計画書 v1.0 確定 | 260515 |
| Step 2 | `/gravity/` 1 枚 LP v1.0 構成案 + ワイヤフレーム | 260516-518 |
| Step 3 | 営業資料 HTML テンプレ v1.0 | 260519-521 |
| Step 4 | `/gravity/code/` `/gravity/coaching/` 移動 + 301 設定 | 260522-524 |
| Step 5 | `/gravity/` 1 枚 LP 実装・本番デプロイ | 260525-528 |
| Step 6 | 旧 LP アーカイブ移動 + deploy.sh 更新 | 260529-531 |
| Step 7 | SSOT 反映（商品.md / 接続装置.md / design.md / CLAUDE.md）| 260601-603 |
| Step 8 | lint / verify 拡張 + memory 反映 | 260604-605 |

**全体所要**：約 3 週間（Step 2-8）

---

## §12. オープン論点（ユーザー判断要）

### §12.1 残置 LP の処遇（5 件）

1. **`/gravity-citations/`** → 候補 A: `/achievement/citations/` 統合 / B: 残置 / C: `/gravity/citations/`
2. **`/academy-wl/`**（Academy 想起装置）→ 残置 or アーカイブ
3. **`/whitepaper-read/`** → 残置（既定）/ `/knowledge/whitepaper/` に移動も可
4. **CODE 4 型表記**：CODE LP の「4 型（整合/拡散/渇望/不毛）」は SCAN の組織引力 4 型と混同していないか確認要
5. **`/gravity/diagnose/`**（旧 Scan web-diagnose）→ `/gravity/` 内埋め込み / 独立サブページ

### §12.2 営業資料の中身決定

§7.5 の 10 ページ構造を v1.0 として進めるか、追加・削除・順序変更があるか。

### §12.3 個人軸サービス（CODE / Coaching）のサブページ深度

`/gravity/code/` のみ or `/gravity/code/diagnose/` `/gravity/code/executive/` まで残すか。

---

## 付録 A：参照ドキュメント

- PeopleX 網羅調査：`08_情報収集/260515_PeopleX_網羅調査_v1.0.md`
- 堀田 hajime.institute 分析：本書 §1.2 に集約（独立ファイル化候補）
- 既存 SSOT 用語と定義：`05_プロダクト/_共通/SSOT_用語と定義.md`
- 既存 deploy.sh：`06_開発/scripts/deploy/deploy.sh`
- LP デプロイマッピング SSOT：`memory/feedback_wp_v9_v10_deploy_path_distinction_260515.md`

---

**本書ステータス**：v1.0 ドラフト・ユーザーレビュー待ち。承認後 Step 2 に着手。
