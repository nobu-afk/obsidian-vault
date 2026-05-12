# Simplify Refactor TODO（2026-04-14 レビュー結果）

> **背景：** 2026-04-14 の実装（CODE/Scan改修、Orbit/Coaching/Shift/WP配布LP）に対して3エージェントで reuse/quality/efficiency レビューを実施
> **即時修正済み：** ①WP配布LPのプレースホルダー警告コメント追加、②CODE generate.php の `$role_guidance` を連想配列ルックアップにリファクタ、デプロイ済み
> **以下は大型 refactor で優先度中〜高、次期改修で対応**

---

## 🔴 優先度：高（次の改修サイクルで対応）

### 1. Scan generate.php の分岐ロジックをPHP事前判定化
**現状：** STEP1-7の判定ロジック（CEO関与度、L0-L3、4象限、Q7ギャップ等）が `system_prompt` のヒアドキュメント内にテキストで埋め込まれており、AIが解釈して判定している。

**問題：**
- 入力トークン消費量が大きい（推定30-40%削減可能）
- レスポンス時間が長い（180秒→120秒程度に短縮期待）
- AIのゆらぎによる誤判定リスク

**対応：**
- `$choices` から決定的ルール（Q2/Q3/Q7/Q9/Q10a/Q10b）を PHP で事前判定
- 判定結果（「この経営者は ❷ 人力拡大、L2、幹部ギャップあり」）だけをプロンプトに渡す
- プロンプトは「判定結果を基に文章化してください」という指示に縮小

**実装概算：** 8-12時間

### 2. Shift LP と Scan LP の styles.css 共通化
**現状：** Shift LPの styles.css は Scan LP のコピー（約820行中、差分は103行のみ）

**問題：**
- 片方を修正すると片方が陳腐化するリスク
- ブランドカラー統一時に複数箇所変更が必要

**対応：**
- `/05_プロダクト/_shared/lp-base.css` として共通部分を切り出し
- 各LPは `<link rel="stylesheet" href="/shared/lp-base.css">` ＋差分のみ自LPに記述
- FTP運用のため、シンボリックリンクではなく実体ファイル分離方式を採用

**実装概算：** 4-6時間

### 3. Meta Pixel / GA4 初期化コードの共通化
**現状：** 複数LP（Shift/Scan/Code/Orbit/Coaching/Gravity/WP配布）で同じinit処理がインラインコピペ。WP配布LPでは GA4 に加えて GTM (`GT-5D48K35Z`) も読み込まれており既に差分が発生。

**問題：**
- Pixel ID 変更時の同期漏れリスク
- ブラウザキャッシュヒット率が低い
- 既に差分発生中（技術的負債の兆候）

**対応：**
- `/assets/js/tracking.js` として共通化
- 各LPは `<script src="/assets/js/tracking.js"></script>` で読み込み
- SRI (Subresource Integrity) 付きで参照

**実装概算：** 2-3時間

---

## ⚠️ 優先度：中

### 4. 問い直し装置（analyst-question-block / final-question）CSSの共通化
**現状：** CODE の `final-question` と Scan の `analyst-question-block` はデザイントークンが完全一致。クラス名だけ違う同一コンポーネント。

**対応：**
- `/05_プロダクト/_shared/question_block.css.php` に切り出し
- 両 generate.php から `include` する
- クラス名を `.cta-question-block` に統一

**実装概算：** 2時間

### 5. CODE/Scan app.js の section番号 enum化
**現状：** `SECTIONS` 配列の index と `QUESTIONS` の `section: N` が整数で紐づいており、セクション追加時に全Qを一斉変更する必要がある（今日実施した Q0追加時の8箇所変更が証左）

**対応：**
- `SECTION_ID.SCENE0`, `SECTION_ID.SCENE1` 形式の定数/enumに統一
- `section: SECTION_ID.SCENE0` と書けるようにする

**実装概算：** 1.5時間

### 6. CSS変数（ブランドトークン）の共通化
**現状：** 各LPの `:root` に `--accent`, `--radius`, `--text` 等が個別定義。Orbit `--accent: #1e40af`, Shift も同じだが、Gravity/Coaching は未確認で不統一の可能性。

**対応：**
- `/05_プロダクト/_shared/tokens.css` に統一定義
- 全LPが `<link>` で読み込み

**実装概算：** 3時間

---

## 🟢 優先度：低（Nice to have）

### 7. FTP並列デプロイスクリプト
**現状：** `curl -T` を単発実行で各ファイルを順次アップロード

**対応：**
- `deploy.sh` として並列化（`curl -T ... &` で 4-8並列）
- xserver側の接続数制限は事前確認

**実装概算：** 1時間

### 8. CODE `$client_role` 抽出の O(1) 化
**現状：** `foreach` で全choice走査（Q0が先頭固定なら `$choices[0]` 直接参照可）

**対応：** マイクロ最適化。N≒10-20なので実害は軽微。現状維持でOK

---

## 対応スケジュール案

### 5月前半（WP配布開始前）
- [ ] #1 Scan分岐ロジックのPHP事前判定化 ← **最大インパクト**
- [ ] #3 Meta Pixel / GA4 共通化 ← **技術的負債の早期解消**

### 5月後半〜6月
- [ ] #2 Shift/Scan styles.css 共通化
- [ ] #4 問い直し装置CSS共通化
- [ ] #6 CSS変数共通化

### 機会があれば
- [ ] #5 section番号enum化
- [ ] #7 FTP並列化

---

## 今日修正済みの項目

✅ **WP配布LPのUtageプレースホルダー警告コメント追加**
→ `YOUR_UTAGE_ID_HERE` 直上に `<!-- ⚠️ DEPLOY BLOCKER ... -->` コメント追加。本番デプロイ前の grep チェックで発見できるように

✅ **CODE generate.php の `$role_guidance` を連想配列ルックアップにリファクタ**
→ if/elseif 5分岐を `$ROLE_GUIDANCE_MAP` とループで置換。将来の立場追加時の差分が1行に
→ デプロイ済み（本番反映）

---

## レビューサマリー（3エージェント集約）

| 項目 | 指摘数 | 修正済 | 残TODO |
|-----|------|------|------|
| 🔴 重大 | 4 | 1 (WP placeholder) | 3 |
| ⚠️ 改善余地 | 10 | 1 (role_guidance) | 9 |
| ✅ 問題なし | 6 | - | - |

**次の改修サイクルで最優先：** Scan generate.phpの分岐ロジックPHP化（#1）＋Meta Pixel/GA4共通化（#3）
