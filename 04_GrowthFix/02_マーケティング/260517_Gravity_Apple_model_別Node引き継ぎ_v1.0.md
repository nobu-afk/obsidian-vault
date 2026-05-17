# Gravity ブランド Apple モデル化 別 Node 引き継ぎ書 v1.0

**作成日**: 2026-05-17 / **作成者**: GrowthFix・石井伸幸（メインスレッド）/ **想定**: 別 Node で本書を最初に Read してから実行

---

## 1. このタスクの位置づけ

260517 メイン thread での議論結果：**Gravity ブランドを Apple モデルで再構造化**することが確定。

### 新構造（確定済）

```
GrowthFix（会社）
└ Gravity ブランド
   ├ Gravity（組織軸メイン商品 = 組織の引力設計プログラム）
   ├ Gravity CODE（個人軸サブ・40 分診断・入口）
   └ Gravity Coaching（個人軸サブ・6 ヶ月伴走）
```

**ポイント**：
- 「**Gravity**」単体 = **組織軸メインプログラム**（デフォルト）= 旧「組織の引力設計プログラム」
- 「**Gravity CODE**」「**Gravity Coaching**」 = 個人軸サブ（必ずフルネーム）
- 「**Gravity シリーズ**」表記は廃止 →「**Gravity**」or「**Gravity ブランド**」

### 堀田フレームでの根拠

| 堀田フレーム | 評価 |
|---|---|
| #21 コンバージョン 3 条件 | ◎ 一語で覚えられる |
| #16 メタファー先行 | ◎ Gravity（引力）自体がメタファー |
| #2 ウニ丼モデル | ◎ Apple / iPhone 型のブランド = 商品構造 |
| #41 直接訴求の禁則 | ◎ Gravity はメタファー（内的直打ちでない）|
| #29 認知価格設計 | ◎ 一語の認知価格は最強 |

→ 5 つ全部 ◎。これまでの命名規則ズレを完全解消。

## 2. 実装範囲（推定 50-80 ファイル）

| 領域 | 推定ファイル数 | 主要内容 |
|---|---:|---|
| 4 LP（CODE / 引力設計 / Coaching / 無料 Web 診断）| 10-15 | 「Gravity シリーズ」→「Gravity」/ Hero メイン表記 |
| コーポレート系 LP（top / profile / achievement / news / knowledge）| 5-10 | フッター・ナビ・本文の表記統一 |
| 共通アセット（site-chrome.js / mobile.css / footer 系）| 3-5 | フッターブランド表記の動的生成 |
| SSOT MD（SSOT_用語と定義 / 商品 / 接続装置 / Why / 引力 / culture / 発信 / design）| 10-15 | 「Gravity = 組織軸メイン商品」明文化 |
| 09_会社OS 機能 MD（営業 / 採用 / カスタマー / 判断基準 / 翻訳）| 5-10 | 商品定義の数値・表記訂正 |
| memory MD（project_gravity_* / project_8pages_pivot_* など）| 10-15 | 新構造の SSOT 記録 |
| WP V9（hero / chapter / bio） | 5-10 | 「Gravity シリーズ」廃止・新構造反映 |
| **合計** | **約 50-80** | |

## 3. 実装手順（8 フェーズ）

### Phase 1：影響範囲調査（10 分）

```bash
# 「Gravity シリーズ」表記の grep
grep -rln "Gravity シリーズ" "/Users/ishiinobuyuki/Documents/Obsidian Vault" --include="*.md" --include="*.html" --include="*.js" 2>/dev/null | grep -v "_archive\|_history\|.git"

# 「組織の引力設計プログラム」表記の grep
grep -rln "組織の引力設計プログラム" "/Users/ishiinobuyuki/Documents/Obsidian Vault" --include="*.md" --include="*.html" 2>/dev/null | grep -v "_archive\|_history\|.git"
```

→ 結果をパターン分類（4-5 パターン）

### Phase 2：核心 SSOT 訂正（30 分・最優先）

対象：
- `05_プロダクト/_共通/SSOT_用語と定義.md` ── Gravity 定義を「組織軸メイン商品」明文化
- `09_会社OS/公開/ガイドライン/商品.md` ── 商品体系の Apple モデル化
- `09_会社OS/公開/経営思想/接続装置.md` ── サービス体験ストーリーの更新
- `09_会社OS/公開/経営思想/Why.md` / `引力.md` ── 必要に応じて
- `09_会社OS/公開/文化/culture.md` ── ブランド運用ルール

訂正パターン：
```bash
# パターン 1: 「Gravity シリーズ」→ 「Gravity」or 「Gravity ブランド」
sed -i '' 's/Gravity シリーズ/Gravity ブランド/g' [file]

# パターン 2: 「組織の引力設計プログラム」を「Gravity」に置換（商品名として）
# 注意：コンセプト記述で残す箇所と、商品名として置換する箇所の判別が必要
```

### Phase 3：機能 MD 訂正（30 分）

- 09_会社OS/非公開/機能/営業.md
- 09_会社OS/非公開/機能/採用.md
- 09_会社OS/非公開/ガイド/カスタマー.md
- 09_会社OS/公開/ガイドライン/翻訳.md
- 09_会社OS/公開/文化/判断基準.md

### Phase 4：LP 訂正（45 分）

#### 4 LP（CODE / 引力設計 / Coaching / 無料 Web 診断）

**Hero / メインコピー**：
- 引力設計 LP `/gravity/`：「Gravity ── 組織の引力設計プログラム」型に Hero h1 構造化
- 個人軸 LP（CODE / Coaching）：「Gravity の入口」型ラベル追加

**フッター / ナビ / リンクテキスト**：
- 「Gravity シリーズ」→「Gravity」or「Gravity ブランド」

#### コーポレート系（top / profile / achievement / news / knowledge）

- 「Gravity シリーズ」表記の置換
- top の Hero タグライン整合性確認

#### 共通アセット

- `06_開発/site-chrome/site-chrome.js`：フッターブランド表記
- 動的生成テンプレート（gf-footer.php / site-footer_template.html / b-footer_template.html）

### Phase 5：WP V9 訂正（15 分）

- `05_プロダクト/Gravity/WhitePaper/V9/index.html`
- hero eyebrow / 本文 / wp-author-bio
- 「Gravity シリーズ」表記の置換

### Phase 6：memory 更新（20 分）

**新規作成**：
- `memory/project_gravity_brand_apple_model_260517.md`
  - Apple モデル構造の確定記録
  - 「Gravity」単独 = 組織軸メイン商品の運用ルール
  - 「Gravity CODE」「Gravity Coaching」必ずフルネーム
  - 堀田フレームでの根拠 5 件

**MEMORY.md 索引追加**：
- 🍎 2026-05-17 Gravity ブランド Apple モデル化（「Gravity シリーズ」廃止）

**既存 memory MD で「Gravity シリーズ」表記の訂正**：
- project_gravity_strategy_260403.md / project_gravity_series_gen2_260415.md など

### Phase 7：本番デプロイ + lint 検証（20 分）

```bash
# 全部一括
bash 06_開発/scripts/deploy/deploy.sh all

# lint 検証
bash 06_開発/scripts/lint/lint_consistency.sh
```

**user 明示承認が必要**（自動 deploy 禁止）。

**本番反映確認**：
```bash
for url in "/" "/gravity/" "/gravity/code/" "/gravity/coaching/" "/gravity/diagnose/" "/profile/" "/achievement/" "/news/" "/knowledge/" "/whitepaper-read/"; do
  cnt=$(curl -s "https://growthfix.jp${url}" | grep -c "Gravity シリーズ")
  echo "  ${url} : ${cnt} 件残存"
done
```

→ 全 LP で「Gravity シリーズ」残存 0 件を確認。

### Phase 8：work-log 統合（15 分）

- `04_GrowthFix/04_デイリーログ/2605/2605_work_log.md` に 5/18（または完了日）の新ラウンド追記
- デイリー集計再計算
- 5/18 daily.md 作成 + 振り返り記載
- 会社OS 更新候補リスト

## 4. 必須運用ルール

### a. 「足す＋消す」ペア運用

- 表記置換でも「ペア」感を意識：旧表記を消す & 新表記を入れる
- 単に置換するだけでなく、文脈上の整合性チェック必須

### b. Gravity 用語隔離原則

- 天プロ用語（執着・象徴エピソード・落とし込み 等）を持ち込まない
- Gravity 用語（偏愛性・想い・強み・引力）に統一

### c. 自動反映禁止・都度承認制

- 各 Phase の deploy は必ず user 明示承認
- 大規模置換は user に「これで置換します・OK？」確認

### d. 「Gravity」単独使用 vs 「Gravity CODE / Coaching」の判別

- 文脈で組織軸メイン商品を指している箇所：**「Gravity」単独**
- 個人軸サブを指している箇所：**「Gravity CODE」「Gravity Coaching」フルネーム**
- ブランド全体を指す箇所：**「Gravity」or「Gravity ブランド」**
- 旧「Gravity シリーズ」表記は廃止

## 5. 注意点（誤訂正ガード）

### 誤訂正リスク 1：「組織の引力設計プログラム」をすべて削除しない

- LP メインヘッダー（`/gravity/`）：「**Gravity ── 組織の引力設計プログラム**」型で **コンセプト名として温存**
- 商品名としては「Gravity」に統一
- 説明文中の「組織の引力設計プログラム」は文脈次第で温存可

### 誤訂正リスク 2：個人軸 LP の hero-eyebrow

- 既存：「引力の参謀（個人軸）── Coaching 体験版・40 分」（CODE）
- 「Gravity」単独で個人軸を指さないので、CODE は「Gravity CODE」明示維持

### 誤訂正リスク 3：履歴ファイル

- _archive / _history / _素材ストック 配下は **温存**（歴史記録として温存）

## 6. 主要 SSOT パス（先に Read）

- `04_GrowthFix/02_マーケティング/260517_天プロR3_別エージェント引き継ぎ_v1.0.md` ── R3 タスクの引き継ぎ書（B/A/C タスクは別ジョブ）
- `memory/MEMORY.md` ── プロジェクト全体の索引
- `memory/project_8pages_pivot_implementation_260515.md` ── 8 ページピボット履歴
- `memory/project_gravity_identity_triple_layer.md` ── 肩書き 3 層構造
- `memory/feedback_lp_improvement_add_remove_pair_260517.md` ── 足す＋消す運用
- `memory/feedback_gravity_terminology_isolation_260517.md` ── Gravity 用語隔離原則

## 7. 期待 ROI

| 項目 | 効果 |
|---|---|
| 認知価格設計 | 一語ブランドで覚えやすさ最大化 |
| ブランド一貫性 | Apple モデルで個人軸 / 組織軸の階層が明確 |
| LP メインキャッチ | 「Gravity ── 組織の引力設計プログラム」型でシンプル |
| 商談 / 営業 | 「Gravity 受講したい」と一言で表現可能 |
| Note / FB / 対外発信 | 一語のハッシュタグ #Gravity でブランディング統一 |

## 8. やってはいけないこと

- ❌ 「組織の引力設計プログラム」完全削除（コンセプト名として温存）
- ❌ 個人軸 LP のフルネーム表記を「Gravity」だけに省略
- ❌ 履歴ファイル（_archive / _history）の置換
- ❌ 自動 deploy / user 明示承認なしの本番反映
- ❌ 天プロ用語の持ち込み（Gravity 用語隔離原則違反）

## 9. R3 タスクとの関係

- R3（B コーポレート LP / A WP V9 / C Note 素材化）は別ジョブとして並行進行可
- ただし **R3 B（コーポレート LP）と本タスク（Apple モデル化）は同一 LP に影響**
- 推奨：本タスクを先に完了 → R3 B はその後（または同時進行で user 取捨選択を綿密に）

## 10. 完了後の最終アウトプット

- ✅ memory 新規（project_gravity_brand_apple_model_260517.md）+ MEMORY.md 索引追加
- ✅ 全 LP 本番反映（curl 検証で「Gravity シリーズ」残存 0 件）
- ✅ lint 通過（lint_consistency.sh）
- ✅ work-log 新ラウンド追加 + デイリー集計再計算
- ✅ 本書末尾に「完了サマリ」追記

---

**最後に**：このタスクは Vault 全体の構造変更を伴う **大規模リブランド**。慎重さと網羅性が両立必要。「**Gravity シリーズ → Gravity**」の表記変更は機械的だが、文脈整合性（個人軸 vs 組織軸の判別）は人間判断が必要。

成功条件：**完了後、全 LP・SSOT・memory で「Gravity = 組織軸メイン商品」「Gravity CODE / Coaching = 個人軸サブ」の階層が完全に統一**されていること。

---

## 11. 完了サマリ（2026-05-17 別 Node 実装完了）

### 11.1 実施 Phase 概要

| Phase | 内容 | 結果 |
|---|---|---|
| 1 | 影響範囲調査・パターン分類 | 「Gravity シリーズ」53 ファイル / 「組織の引力設計プログラム」78 ファイル → 5 パターン（A 核心 SSOT / B 公開 LP / C WP V9 系 / D 履歴系 / E 共通アセット）に分類 |
| 2 | 核心 SSOT 6 件訂正 | SSOT_用語と定義 + 商品.md + SSOT_Gravity_コア主張 + 引力.md + 接続装置.md + culture.md ── 全件に🍎 Apple モデル注記追加 |
| 3 | 機能 MD 6 件訂正 | 法務.md（L49 + 注記）+ 営業 / 採用 / カスタマー / 翻訳 / 判断基準（注記） |
| 4 | LP 13 件訂正 | 7 サービス LP（Citations/Coaching/Code/Cultivate/Orbit/Recruit/Scan）+ コーポレート 5（top/profile/privacy-policy/news 2）+ tracking.js。post_lp_edit hook（audit_mobile_sync + lint_lp_internal_terms）全 PASS |
| 5 | WP V9 整合性確認 | 本体 index.html は既に「Gravity シリーズ」ゼロ件 + Apple モデル整合構造（Gravity 全体像 / 2 階層構造 / Gravity CODE + Gravity Coaching フルネーム）→ 追加修正不要 |
| 6 | memory 更新 | 新規 `project_gravity_brand_apple_model_260517.md` 作成 + MEMORY.md 先頭索引（🍎）+ 既存 memory 8 件の表記訂正 |
| 7 | 本番デプロイ + 検証 | `deploy.sh all` user 明示承認後実行 → verify PASS 18 / WARN 9（既知）/ FAIL 0 → privacy-policy のみ deploy.sh 対象外で個別 curl 補完 → **全 14 公開 LP で「Gravity シリーズ」残存 0 件達成** |
| 8 | work-log 統合 + 引き継ぎ書末尾追記 | 2605_work_log.md 第 7 ラウンド追記（8 タスク・削減 456 分・削減率 89.4%）+ 本書 §11 完了サマリ追記 |

### 11.2 成功条件達成確認

- ✅ memory 新規（`project_gravity_brand_apple_model_260517.md`）+ MEMORY.md 索引追加完了
- ✅ 全 14 公開 LP 本番反映で「Gravity シリーズ」残存 **0 件**（curl 検証済）
- ✅ lint_consistency.sh 通過（警告 20 / エラー 0）
- ✅ work-log 第 7 ラウンド追加 + デイリー集計再計算
- ✅ 本書末尾に完了サマリ（§11）追記

### 11.3 本番反映確認結果（curl 検証）

| URL | Gravity シリーズ残存 |
|---|---:|
| `/` | 0 |
| `/profile/` | 0 |
| `/achievement/` | 0 |
| `/news/` | 0 |
| `/news/gravity-release/` | 0 |
| `/news/site-renewal/` | 0 |
| `/knowledge/` | 0 |
| `/privacy-policy/` | 0（個別 curl 補完後）|
| `/gravity/` | 0 |
| `/gravity/code/` | 0 |
| `/gravity/coaching/` | 0 |
| `/gravity/diagnose/` | 0 |
| `/whitepaper-read/` | 0 |
| `/whitepaper/` | 0 |
| `/assets/js/tracking.js` | 0 |

### 11.4 温存対象（履歴・草稿・戦略 MD）

引き継ぎ書 §5 誤訂正リスク 3 ルールに従い、以下は **温存**：
- `_archive` / `_history` / `_素材ストック` 配下
- `.bak` ファイル（pre-upgrade / pre-zerobased / index_backup）
- 04_デイリーログ系（時系列記録）
- 02_セッション記録（堀田壁打ち履歴）
- 03_コンテンツ Note 草稿（連載 Vol3 / Vol5）
- 戦略 MD（260424 / 260429 / 260506 / 260508 / 260509 / 260511 / 260512）
- WP V10 草案（`_WP_V10_草案_本番未投入/`）
- 営業 LP 詳細アーカイブ（`_LP詳細アーカイブ_260508/`）
- 引き継ぎ書類（本書 + `260517_Gravity_Apple_model_貼り付けプロンプト.md`）

### 11.5 関連 SSOT（更新済）

- `05_プロダクト/_共通/SSOT_用語と定義.md`（Apple モデル注記新規追加）
- `09_会社OS/公開/ガイドライン/商品.md`（Apple モデル注記 + L3 サブタイトル更新）
- `05_プロダクト/_共通/SSOT_Gravity_コア主張.md`（Apple モデル注記 + L6 訂正）
- `09_会社OS/公開/経営思想/引力.md`（注記 + L119 訂正）
- `09_会社OS/公開/経営思想/接続装置.md`（注記）
- `09_会社OS/公開/文化/culture.md`（注記）
- `09_会社OS/公開/文化/判断基準.md`（注記）
- `09_会社OS/公開/ガイドライン/翻訳.md`（注記）
- `09_会社OS/非公開/機能/営業.md` / `採用.md` / `法務.md`（注記 + 法務 L49 訂正）
- `09_会社OS/非公開/ガイド/カスタマー.md`（注記）
- `memory/project_gravity_brand_apple_model_260517.md`（新規・Apple モデル SSOT）
- `memory/MEMORY.md`（🍎 索引先頭追加）

### 11.6 ROI（11.6 期待 ROI セクション §7 への実証）

| 項目 | 実現状況 |
|---|---|
| 認知価格設計 | 一語ブランド「Gravity」が組織軸メイン商品として全公開 LP で統一・覚えやすさ最大化 ✓ |
| ブランド一貫性 | Apple モデル明示で個人軸 / 組織軸の階層が SSOT レベルで確定 ✓ |
| LP メインキャッチ | 「Gravity ── 組織の引力設計プログラム」型を top tagline + profile + news で実装 ✓ |
| 商談 / 営業 | 営業.md / 採用.md / カスタマー.md に Apple モデル注記反映で運用準備完了 ✓ |
| Note / FB / 対外発信 | culture.md / 翻訳.md / 発信系 MD に注記反映 ✓ |

---

**本タスク完走時刻：** 2026-05-17 23:00 頃 JST（別 Node 実装）
**実装者：** Claude Opus 4.7（1M context）
**承認者：** GrowthFix・石井伸幸（Phase 7 デプロイ承認・明示テキスト承認）
