# LP 変更時 モバイル確認チェックリスト

> **目的：** LP/HTML を変更する際にモバイル最適化を忘れる事故を防ぐ単一の手順書
> **作成：** 2026-04-28（260428 LIVE WEBINAR バー追加時にモバイル最適化忘れが発生した事故を契機に整備）
> **発火条件：** `05_プロダクト/` 配下の HTML を編集する全てのケース。Claude は LP/HTML 変更後にこのチェックリストを必ず実行する（memory `feedback_lp_mobile_audit_required.md` 参照）

---

## Step 1：変更前の確認（編集着手前）

- [ ] 変更対象の HTML ファイルを把握した
- [ ] 同じ変更を**他の LP にも展開する必要があるか**判定した（例：共通ヘッダー / バー / 帯）
- [ ] `05_プロダクト/_共通/mobile.css` の現状を確認した

## Step 2：変更時の確認（HTML 編集中）

- [ ] **新規クラス名**を追加したか確認（`class="..."` の新規値）
- [ ] **新規インラインスタイル要素**を追加したか確認（`style="..."` で構造的なもの）
- [ ] **新規構造**を追加したか確認（新しい section / div / 表 / グリッド / フレックス）

→ いずれか YES なら **必ず Step 3 に進む**

## Step 3：mobile.css の対応ルール作成

新規クラス／インラインスタイル要素／構造に対して mobile.css に以下を追加する：

### チェック項目

- [ ] **font-size**：PC 値 → `clamp(min, vw, max) !important` で再定義
- [ ] **padding / margin**：mobile では詰める
- [ ] **horizontal layout（display:flex flex-row）**：縦積みに反転（`flex-direction: column !important`）
- [ ] **width 固定値**：`max-width: 100% !important`
- [ ] **white-space: nowrap**：解除（折り返し許容）
- [ ] **fixed width tables / grids**：`grid-template-columns: 1fr !important`
- [ ] **小さすぎる文字（< 14px）**：mobile では下限 14px 程度に引き上げ
- [ ] **タッチ要素（ボタン・リンク）**：`min-height: 44px !important`（タップ領域確保）
- [ ] **装飾画像／装飾テキスト**：本文と被るリスクがあれば `display: none !important` を検討
- [ ] **横並びの「／」「・」等の区切り**：mobile で改行する場合は非表示
- [ ] **背景画像 / position: absolute**：mobile での重なり確認

### 追加位置の決め方

- 全 LP 共通の要素 → `@media (max-width: 768px)` のメインブロック
- 特定セクション専用（例：`.fv` `.service`）→ WP テーマ固有ブロック
- 極小画面専用 → `@media (max-width: 375px)` ブロック

## Step 4：キャッシュバスター更新

- [ ] mobile.css 変更後は cache buster を新しい値に bump（例：`?v=20260428a` → `?v=20260428b`）
- [ ] 全 LP（19 ファイル）の `mobile.css?v=...` を一括更新（sed）

## Step 5：デプロイ

- [ ] mobile.css を `/assets/css/mobile.css` にデプロイ
- [ ] 変更した HTML を該当パスにデプロイ（19 LP の場合は順次）
- [ ] HTTP 226（FTP 成功）を全件確認

## Step 6：検証（必須）

- [ ] スマホ実機 or DevTools モバイルビュー（375px / 414px）で確認
- [ ] **ファーストビュー**：装飾と本文が被っていないか
- [ ] **横スクロール発生**していないか
- [ ] **新規追加要素**が読める文字サイズか（タップしやすいか）
- [ ] **nowrap**で画面外にはみ出ていないか
- [ ] 320px（iPhone SE 縦）と 768px（タブレット）の境界も軽く確認

## Step 7：完了報告

完了報告には以下を含める：

```
- 変更内容：
- mobile.css 追加ルール：
- cache buster：
- デプロイ結果：
- 検証結果：（実機 or DevTools）
```

---

## 過去の事故記録（再発防止用）

| 日付 | 何が起きたか | 教訓 |
|---|---|---|
| 2026-04-28 | LIVE WEBINAR バーを 19 LP に追加したが mobile 最適化忘れ → 後追い 2 回修正 | 新規セクション追加時は **mobile.css ルールを HTML と同時にセットで追加**する |
| 2026-04-28 | `.fv_en`（cursive 装飾テキスト）が SP で画面占拠 → 別要素の `.fv_bg1/.fv_bg2` を疑って初手を外した | 装飾系要素は **クラス名と実際のスタイルを WP テーマ CSS で確認**してから対処する |

---

## 関連ファイル

- mobile.css 本体：`05_プロダクト/_共通/mobile.css`
- mobile 戦略 memory：`reference_mobile_css_strategy.md`
- lint スクリプト：`06_開発/scripts/lint_consistency.sh`
- 自動リマインド memory：`feedback_lp_mobile_audit_required.md`
