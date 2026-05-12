# Gravity Scan v1.0 レポート 品質課題整理 v0.1

> **発端：** 2026-05-08 朝、長谷さんダミー（CODE 受講者・才能ズレ型・任せられない建築家）で本番 Sonnet 4.5 生成 PDF をレビューした際、5 つの構造的フィードバックを発見。CODE v5.2 → v5.3.4 改修と同型のプロセスで段階的に改修。
> **位置付け：** SCAN レポート単体価値検証 + R/C 接続設計検証（ユーザー要請：「レポート単体で価値を出しているか」「R/C に繋がる設計になっているか」）
> **作成：** 2026-05-08 朝
> **改修達成：** v1.0 → v1.4（同日内・本番デプロイ済）

---

## 🎯 v1.4 改修達成サマリー

### 全 5 論点完全解消 + 8 ページ最適化

| 項目 | v1.0 | v1.4 | 改善 |
|---|:-:|:-:|:-:|
| **ページ数** | 11 | **8** | 🟢 27% 削減（CODE v5.3.4 と同水準） |
| **「Shift A」表記露出** | 🔴 露出 | ✅ Gravity Cultivate 統一 | 🟢 完全 |
| **「組織の引力」定義不在** | 🔴 不在 | ✅ Page 1 開示（gravity-definition-box）| 🟢 完全 |
| **テーブル縦書き縮退** | 🔴 縮退 | ✅ 水平表示（table-layout: fixed） | 🟢 完全 |
| **動詞3連鎖（CODE 公開語彙不整合）** | 🟡 SSOT 違反 | ✅ 才能統一 | 🟢 完全 |
| **footer 二重出力** | 🔴 重複 | ✅ 解消 | 🟢 完全 |
| **Block A 集約** | 3 ページ分散 | ✅ Page 1 主要要素集約 | 🟢 完全 |

---

## 5 論点サマリー

| # | 論点 | レベル | v1.0 影響 | 解消版 |
|:-:|---|:-:|:-:|:-:|
| 1 | **「Shift A」表記露出（公開向け SSOT 違反）** | 戦略 | 大・本番不可 | v1.1 |
| 2 | **「組織の引力」定義不在（CODE 同型欠陥）** | 戦略 | 大 | v1.1 |
| 3 | **テーブル縦書き縮退（CSS 不備）** | 戦術 | 大・読めない | v1.1 |
| 4 | **動詞3連鎖（CODE v5.3.4 公開語彙違反）** | 戦術 | 中 | v1.1 |
| 5 | **ページ膨張（11 ページ・footer 二重含む）** | 戦術 | 中 | v1.4 |

---

## 🔴 論点 1：「Shift A」表記露出（最重要・本番運用不可レベル）

### 現状（v1.0 PDF）

公開向けレポートに以下が露出：
- shift-fit-box：「Shift A + Coaching 並走パッケージ」
- path-cards：「Gravity Shift A + Coaching 並走パッケージ」
- **CTA ボタン：「Shift A 体験セッション 30 分無料 →」**（最重大）
- closing-note：「Shift A で躍動組織を 3 ヶ月実装」

### SSOT 違反

260503 B 案二層命名 + 260505 Cultivate 化の SSOT に対して：
- 公開向け正式表記：**Gravity Cultivate**（旧 Activate からも変更済）
- 内的呼称（Shift C）は社内設計用・顧客接点では出さない

generate.php SYSTEM プロンプト全般で「Shift A／Shift R／Shift Full」表記が残存していた。

### v1.1 修正

generate.php の以下を全面修正：
- role_guidance（line 367）：公開語彙ルール追加
- 推奨サービス決定ロジック表（line 487-494）
- Block C テンプレ（shift-fit-box / roadmap-box / path-cards / final-question / closing-note）
- URL 振り分けルール：`/gravity-shift-a/` → `/gravity-cultivate/`、`/gravity-shift/`（渇望型）→ `/gravity-recruit/`
- サービス記載の正確ルール表

### 修正後（v1.4 PDF Page 8 CTA）

```
Gravity Cultivate + Coaching 並走パッケージ 体験セッション 30 分無料 →
```

→ 公開向け表記化完了。260503 B 案二層命名 + 260505 Cultivate 化に整合。

---

## 🔴 論点 2：「組織の引力」定義不在（CODE 同型欠陥）

### 現状（v1.0 PDF）

レポート全体で「組織の引力」「集まる軸」「躍動軸」の定義が一切開示されていない。経営者は前提理解なく「拡散型」を受け入れる構造。

### CODE 改修との同型性

CODE v5.2 でも同型欠陥を発見（260507 v0.1）：
- 「引力」を経営者が知らないまま読み進める
- v5.3 で gravity-definition-box（Cover Page）を追加して解決

SCAN は Cover Page がないため、Block A 冒頭に独立ボックスを追加するパターンを採用。

### v1.1 追加実装

#### SYSTEM プロンプト指示追加（Block A コア要素 0 番目）

```
0. ★ NEW（v1.1）「組織の引力とは何か」定義ボックス（gravity-definition-box）
   ← core-quote の前、Block A の最初に配置
   - 3-5 行で組織の引力定義を開示
```

#### HTML テンプレ追加

```html
<div class="gravity-definition-box">
  <h4>組織の引力とは</h4>
  <p>組織の引力＝人が離れない・自発的に集まり躍動する「場の力」。
     経営者個人の引力（CODE = Why × 才能 × 偏愛）が、組織への翻訳を経て立ち上がる。</p>
  <p><strong>集まる軸</strong>×<strong>躍動軸</strong>の 2 マトリクスで 4 型に分類される。</p>
  <p><strong>事業の天井は、組織の引力の天井である。</strong></p>
</div>
```

#### CSS 追加（青グラデーション）

```css
.gravity-definition-box {
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border: 2px solid #0284c7;
  border-radius: 10px;
  padding: 14px 20px;
  margin: 0 0 14px;
  page-break-inside: avoid;
}
```

### v1.4 PDF Page 1 確認済

組織の引力定義 + core-quote + type-matrix-box（4 象限+判定根拠）が 1 ページに集約された。

---

## 🔴 論点 3：テーブル縦書き縮退（CSS 不備）

### 現状（v1.0 PDF Page 2, 5）

- type-matrix-box の 4 象限テキスト：「【渇望型】既存活きるが採用詰まり → Shift R」が**縦書き**で表示
- pulse-7-table の項目名（採用パイプライン・最終面接辞退率…）が**縦書き**で表示
- セル幅が狭すぎてテキストが折り返されず縦に縮退

### 原因

CSS で `table-layout: auto`（デフォルト）+ 各列の `width` 未指定。テーブル幅 100% に対してセルが等分配されず、コンテンツが多いセルが縦に押し出される。

### v1.1 修正（CSS）

```css
.gi-table {
  width: 100%;
  table-layout: fixed;        /* ← 追加 */
  word-wrap: break-word;      /* ← 追加 */
}

/* type-matrix-box の 3 列：第 1 列ヘッダー + 第 2 列 △ + 第 3 列 ◎ */
.type-matrix-box .gi-table th:nth-child(1) { width: 18%; }
.type-matrix-box .gi-table th:nth-child(2),
.type-matrix-box .gi-table th:nth-child(3) { width: 41%; text-align: center; }

/* pulse-7-table の 5 列：# / 項目 / 軸 / スコア / 根拠 */
.pulse-7-table .gi-table th:nth-child(1) { width: 5%; }
.pulse-7-table .gi-table th:nth-child(2) { width: 18%; }
.pulse-7-table .gi-table th:nth-child(3) { width: 8%; }
.pulse-7-table .gi-table th:nth-child(4) { width: 9%; }
.pulse-7-table .gi-table th:nth-child(5) { width: 60%; }
```

### v1.4 PDF Page 1, 3 確認済

- type-matrix-box（Page 1）：4 象限すべて水平表示
- pulse-7-table（Page 3）：7 項目すべて水平表示

---

## 🟡 論点 4：動詞3連鎖 → 才能 統一（CODE v5.3.4 公開語彙整合）

### 現状（v1.0 PDF Page 3）

ギャップ図に「Why × **動詞3連鎖** × 偏愛の 3 要素のうち『動詞3連鎖』が欠損」と表記。

### CODE v5.3.4 SSOT との不整合

CODE v5.3.4 では公開語彙を「Why × **才能** × 偏愛」に統一。動詞は内部分析用語として残すが、レポート出力では「才能」のみ。

### v1.1 修正

generate.php parse_code_result_for_prompt() の出力フォーマット：

```php
// 旧
$lines[] = "- 動詞3連鎖：" . implode(' / ', $d['verbs']);
// 新
$lines[] = "- 才能（動詞3連鎖）：" . implode(' / ', $d['verbs']);
```

加えて、user_prompt 内の生成ルールに以下を追加：

> CODE 公開語彙「Why × 才能 × 偏愛」で表記（旧「動詞 3 連鎖」「環境」は内部分析用語のためレポート出力では使わない）

### v1.4 PDF Page 2 確認済

「経営者個人の引力タイプ：才能ズレ型『任せられない建築家』（Why：能力があるのに指示待ちで死んでいる人の才能を解放するために構造を作り続ける × **才能**：先回りして答えを準備する × **偏愛**：構造から逆算する設計）」

---

## 🟡 論点 5：ページ膨張（11 → 8 ページ・段階的最適化）

### v1.0 → v1.4 の段階改修プロセス

| Version | ページ数 | 主要変更 | 結果 |
|:-:|:-:|---|:-:|
| v1.0 | 11 | （初版・上記 4 論点露出）| 基準 |
| v1.1 | **8** | 5 論点まとめ修正（Shift A・引力定義・縦書き・動詞3連鎖）| ★ 大改善（footer 二重残） |
| v1.2 | 9 | footer 二重解消 + Block A 集約のため CSS 全体圧縮 | 🔴 退行（Block B 膨張） |
| v1.3 | 9 | v1.2 の core-quote/gi-summary 等の圧縮を撤回（gravity-definition-box のみ保持） | 🟡 横ばい（Block A 退行） |
| v1.4 | **8** | type-matrix-box + gravity-gap-box にスコープ限定でピンポイント圧縮 | ✅ 完全達成 |

### 重要学び：CSS 圧縮の trade-off

**広範圧縮（v1.2）の失敗：**
- core-quote / type-matrix-box / gravity-gap-box / gi-summary / gi-rationale を一律で `!important` 圧縮
- Page 1 への type-matrix-box 集約は成功
- しかし他セクション（Block B 副次 issue）の page-break 計算が乱れて 9 ページに膨張

**ピンポイント圧縮（v1.4）の成功：**
- スコープ限定セレクタ（`.type-matrix-box .gi-summary` 等）で対象セクションのみ圧縮
- 他セクションの page-break 計算に影響を与えない
- 結果：Block A 集約 + Block B 安定 = 8 ページ達成

→ **詳細：`memory/feedback_pdf_report_pinpoint_css_compression.md`** に汎用パターンとして記録

---

## 13+1 軸セルフチェック結果（v1.4 最終）

### CODE 共通 8 軸

| # | 軸 | 評価 |
|:-:|---|:-:|
| 1 | レポート単体の価値 | ✅ 高（質的内容深い・8 ページ完結）|
| 2 | キャラ命名（4 型ラベル）の鋭さ | ✅ 「拡散型 = 応募はあるが定着しない・優秀幹部離脱」が一刀で切れている |
| 3 | 矛盾検出の精度 | ✅ 「個人の才能が採用面接で発火するが、組織内では毒に転じる」 |
| 4 | core-quote / 主軸メッセージ品質 | ✅ 日本語破綻なし |
| 5 | テーブル / 図化形式 | ✅ 縦書き解消・適切な width 配分 |
| 6 | 引力定義の明示 | ✅ Page 1 gravity-definition-box で開示 |
| 7 | 経営インパクトの紐付け | ✅ Block C 推奨ロジック + 3 ヶ月後組織像で具体化 |
| 8 | PDF レイアウトの収まり | ✅ 8 ページ・各 Block セクション完結 |

### SCAN 固有 5 軸

| # | 軸 | 評価 |
|:-:|---|:-:|
| 9 | R/C/Full への接続精度 | ✅ Cultivate + Coaching 並走 128 万への接続が論理的に機能 |
| 10 | 4 型判定の根拠の明確さ | ✅ 7 項目数値根拠 + 集まる軸/躍動軸サマリで説得力高 |
| 11 | CODE × Scan ギャップ図の機能性 | ✅ 「個人引力が採用面接で発火 vs 組織運営で躍動を殺す」構造的因果が言語化 |
| 12 | 採用コスト試算の説得力 | ✅ 1.85 倍（年間採用費 1,000 万 / 昇給原資 540 万）= 悪循環閾値 2 倍に近接 |
| 13 | C-5 ネガティブ・ケイパビリティ判定の有効性 | ✅ 「答えを出さないモードは苦手」発言から中判定 → Coaching 並走 128 万標準推奨 |

### 整合性チェック軸

| # | 軸 | 評価 |
|:-:|---|:-:|
| 14 | SSOT 整合性（B 案二層命名・260505 Cultivate 化）| ✅ 公開向け表記すべて整合 |

---

## 残った高品質要素（CODE 改修と同水準）

| 要素 | 内容 |
|---|---|
| **Page 1 集約** | 「組織の引力とは」青グラデ定義 → core-quote → 4 象限図 + 判定根拠 が 1 画面で完結（レポート最初の 5 秒で全体像把握可能） |
| **Page 2 ギャップ言語化** | 「個人引力が採用面接だけで終わり、組織への躍動設計に翻訳されていない構造が露呈している」 |
| **Page 4 引力欠損構造** | 「1on1・OKR・識学・人事制度・サーベイを全部入れても躍動が立ち上がらないのは、これらの仕組みを『あなたが設計して幹部に渡す』構造だからだ」 |
| **Page 5 推奨理由 3 軸** | 4 型判定 + 引力欠損ポイント + C-5 判定で 128 万推奨を論理化 |
| **Page 7 最大リスク** | 「次の四半期で離脱予兆の幹部 1 名が実際に離脱し、優秀層の離脱が 2 名 → 3 名 → 4 名と連鎖する」 |
| **Page 8 closing-note 署名** | Sonnet が「── 石井伸幸」署名を自発的に追加（v1.4 で初登場・権威構造として効果的） |

---

## 5/9 以降の検証計画

### Phase A：5/9 朝 ── 長谷さん本番データで再生成

- 昨夜のモニターで実生成された CODE 結果（v5.3.4）+ 既知の組織情報 7 項目で再生成
- 石井さんが PDF を読み「長谷さんレポート」として違和感検出
- 必要に応じて v1.5 微調整

### Phase B：5/16 次回 Coaching セッション ── 長谷さん本人反応取得

- レポートを長谷さん本人に提示
- 「拡散型」「Gravity Cultivate + Coaching 並走 128 万推奨」への本人反応取得
- 受注クロージングへ接続するか、別タイミングで検討するか判断

### Phase C：5/15 セミナー以降 ── ケース #001 言語化に SCAN 結果を組み込む

- TASK-2 v0.2 § ROI ケースエリアに長谷さん SCAN 結果を反映
- TASK-3 ケース #001 言語化に「Pre-Shift 適合診断 → Cultivate 推奨」フローを組み込む

---

## 関連ファイル

- ダミーペルソナ：`260508_Scan_長谷さんダミー_検証用ペルソナ_v1.0.md`（13+1 軸検証フレーム）
- payload：`05_プロダクト/GravityScan/レポート/260508_長谷さんダミー_payload.json`
- 生成 PDF（4 バージョン）：`05_プロダクト/GravityScan/レポート/260508_長谷さんダミー_生成レポート_v1.{0,1,2,3,4}_本番.pdf`
- generate.php（v1.4）：`05_プロダクト/GravityScan/診断_本番/generate.php`（1305 行）
- CODE 改修プロセス参考：`260507_GravityCODE_v5.2_品質課題整理_v0.1.md`
- SCAN リブート memory：`memory/project_scan_reboot_260430.md`
- SCAN シャープ版 SSOT：`260502_Scan_シャープ版_1文_5論点確定.md`
- SSOT_用語と定義：`05_プロダクト/_共通/SSOT_用語と定義.md`（260505 Cultivate 化記録）
- ★ 学び memory：`memory/feedback_pdf_report_pinpoint_css_compression.md`（CSS 圧縮 trade-off パターン・本日新規）

---

## まとめ

**5 時間の段階改修で SCAN レポート v1.0（11 ページ・本番運用不可）→ v1.4（8 ページ・本番運用可）達成。**

CODE v5.2 → v5.3.4 改修と同型のプロセスを踏襲：
1. ダミーペルソナ + トランスクリプト設計
2. 本番 API で生成 + PDF 化
3. 13+1 軸セルフチェック → 5 論点抽出
4. 段階改修（v1.1 → v1.2 → v1.3 → v1.4）
5. 各段階で本番デプロイ + 再生成 + Read PDF で検証

**得られた汎用パターン：CSS ピンポイント圧縮（スコープ限定セレクタ）が、PDF ページ最適化での trade-off 解消に有効。**
