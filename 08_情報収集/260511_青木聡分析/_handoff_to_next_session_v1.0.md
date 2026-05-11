# 青木仁志ベンチマーク分析 Tier 2 抽出 引き継ぎ書 v1.0

**作成：** 2026-05-11
**前セッション：** 5/11 メインセッション（TOP 20 のうち 10 件壁打ち完了・残 10 件は Shift C/Cultivate 系）
**今セッション目的：** 残り 360 件から **Tier 2 = 30-50 件**を再厳選 → 6 軸抽出 → マスタープラン v1.1 補完 → **Tier 1 残 10 件 + Tier 2 新規を合わせて統合スパーリングまで実施**
**最終ゴール：** Tier 1/2 合わせた全件スパーリング完了（実装 / 反映なし / 統合 判断確定 + LP/memory 反映）
**ユーザー：** 石井伸幸（GrowthFix）

---

## 0. このセッションのミッション（6 行で）

1. 残り 360 件（除外判定済）を再スキャンして **Tier 2 = 30-50 件**を抽出
2. 既存 6 軸（採用 / 組織 / 躍動 / SMB / 思想 / 対談）で並列抽出
3. **TOP 20（既処理済）と重複しない** Tier 2 候補を発見
4. マスタープラン v1.1 として補完（v1.0 を上書きせず）= **TOP 30-40 統合マスター**
5. **Tier 1 残 10 件 + Tier 2 新規 = 統合スパーリング実施**（石井さん × Claude Code 往復で 1 件ずつ判断）
6. 確定した実装は LP / memory に反映・反映なし判断は memory 補完で記録

---

## 1. 既存資産（必ず最初に Read）

### memory（自動継承済）

- `memory/project_aoki_satoshi_benchmark_260511.md` — プロジェクト全体・5/11 壁打ち結果・残 10 件リスト
- `memory/reference_aoki_frameworks_consolidated.md` — 採用 16 / 組織 10 / 躍動 10 / SMB 11 / 思想 8 / 対談 6 のフレーム集約・GrowthFix 翻訳対応表
- `memory/MEMORY.md` — Vault 全体メモリ（5/11 セッションで青木分析を筆頭追加済）

### マスタープラン v1.0（既存）

- `04_GrowthFix/02_マーケティング/260511_青木仁志ベンチマーク分析_GrowthFix経営OS反映マスタープラン_v1.0.md`
- → §1-B 統合 TOP 20 / §6 差別化軸 / §7 ユーザー判断ポイント 6 件 / 重要動画 5 本リスト

### 分析データ（既存）

`/Users/ishiinobuyuki/Documents/Obsidian Vault/08_情報収集/260511_青木聡分析/` 配下：

| ファイル | 内容 | 流用度 |
|---|---|---|
| `_channel_videos_raw.txt` | 415 動画リスト（video_id\|title\|duration） | ★★★ 必須 |
| `_selected_55_ids.txt` | TOP 55 厳選 ID | ★★★ 除外用 |
| `_theme_classification_v1.md` | 12 カテゴリ分類 + 戦略厳選 55 + 除外 360 リスト | ★★★ 必須 |
| `_extraction_1_recruitment.md` 〜 `_extraction_6_dialogues.md` | 6 軸抽出（TOP 55 ベース） | ★★ 参照 |
| `_videos_chunk_aa/ab/ac` | 415 タイトルを 140 件 × 3 チャンク分割 | ★★ 流用可 |
| `transcripts/` | 55 動画の vtt 110 ファイル | ✗ 不要（TOP 55 のみ） |
| `transcripts_clean/` | 55 動画のテキスト 89 万字 | ✗ 不要（TOP 55 のみ） |
| `_download_transcripts.sh` | yt-dlp 並列 DL スクリプト | ★★★ **流用必須** |
| `_vtt_to_text.py` | vtt → テキスト変換 | ★★★ **流用必須** |

---

## 2. 実行プラン（推奨フロー）

### Step 1：除外グループの再厳選（30-60 分・analysis-runner Sonnet 1 本）

**目的：** 残り 360 件から Tier 2 候補 30-50 件を抽出

**Agent プロンプト概要：**

```
入力：
- _channel_videos_raw.txt（全 415 件）
- _selected_55_ids.txt（除外用 = TOP 55）
- _theme_classification_v1.md（テーマ分類 + 除外グループ理由）
- memory/reference_aoki_frameworks_consolidated.md（既抽出フレーム）

タスク：
1. 415 - 55 = 360 件の除外動画を再スキャン
2. **TOP 55 で取りこぼした Tier 2 候補**を 30-50 件選定
3. 選定基準：
   - 既抽出フレーム（reference）と被らない新規フレームを含む可能性
   - 経営戦略・採用・組織・思想領域に寄与する内容
   - Q&A シリーズの中で経営戦略寄り（採用 Q / 組織 Q / 財務 Q）
   - 対談・コラボ動画（Tier 1 で 4 本抽出済の残り）
   - 自伝的動画（人物理解深化）
   - Season1/2/3 のうち経営寄りの未抽出
4. アウトプット：`_tier2_selection_v1.md`
   - 30-50 件の video_id + title + duration + 選定理由（1 行）
   - 既 TOP 20 / Tier 1 フレームとの差別化ポイント明示

出力先：08_情報収集/260511_青木聡分析/_tier2_selection_v1.md
```

### Step 2：字幕一括 DL（30 分・並列）

```bash
# Tier 2 リストから ID 抽出して既存スクリプト流用
cd "/Users/ishiinobuyuki/Documents/Obsidian Vault/08_情報収集/260511_青木聡分析"

# _tier2_selection_v1.md から video_id 抽出 → _selected_tier2_ids.txt
# 既存 _download_transcripts.sh の IDS_FILE を _selected_tier2_ids.txt に変更
# OUT_DIR を transcripts_tier2 / transcripts_tier2_clean に変更
```

### Step 3：vtt → テキスト変換（5 分）

```bash
# _vtt_to_text.py の IN_DIR / OUT_DIR を tier2 用に変更して実行
```

### Step 4：6 軸並列抽出（30-60 分・analysis-runner Sonnet × 6 並列）

**前回と同じ 6 軸を Tier 2 でも回す：**
1. 採用・入り口管理（軸1）
2. 組織設計・幹部育成（軸2）
3. 躍動組織・エンプロイヤーシップ（軸3）
4. SMB 経営の壁・財務・経営者覚悟（軸4）
5. 経営思想圧縮（軸5）
6. 対談・育成実務（軸6）

**ただし重要な指示変更：**
- 「**TOP 55 で抽出済フレームと重複しない新規発見**を最優先」と明示
- memory `reference_aoki_frameworks_consolidated.md` を**最初に Read させて既抽出フレームを把握**
- 重複フレームは Tier 3（記録レベル）落としで OK

**アウトプット：**
- `_extraction_1_recruitment_tier2.md` 〜 `_extraction_6_dialogues_tier2.md`

### Step 5：マスタープラン v1.1 補完作成（60-90 分・Opus メインスレッド統合）

- v1.0 を **上書きせず**に v1.1 として補完版作成
- v1.0 の TOP 20 + 今回の Tier 2 を統合して **TOP 30-40 マスター**を提示
- **5/11 壁打ちで処理済の 10 件は「処理済」マーク**を付ける（重複スパーリング回避）
- **残スパーリング候補（Tier 1 残 10 件 + Tier 2 新規）を一覧化**
- 反映ロードマップ v1.0 を補完（5/16 以降のスパーリング候補追加）
- 重要動画リスト v1.0（5 本）に Tier 2 重要動画 5-10 本追加

**保存先：** `04_GrowthFix/02_マーケティング/260511_青木仁志ベンチマーク分析_GrowthFix経営OS反映マスタープラン_v1.1.md`

### Step 6：統合スパーリング実施（最終ゴール・60-120 分以上・石井さん × Claude Code 往復）

**目的：** Tier 1 残 10 件 + Tier 2 新規 = 計 30-50 件のスパーリングを 1 件ずつ判断

**フロー（前セッション踏襲）：**
1. 各項目について以下を提示：
   - 青木の生フレーム（出典動画・発言の文脈）
   - GrowthFix への翻訳案（複数パターン）
   - 反映先候補（LP / 09_会社OS / memory）
   - リスク・差別化軸チェック（独自軸を希釈しないか）
   - 推奨案
2. 石井さんの判断：採用 / 却下 / 修正
3. 採用の場合：Edit → モバイル監査 → FTP デプロイ → 本番反映確認
4. 反映なしの場合：理由を記録

**LP 改修対象（前セッション踏襲）：**
- Scan LP（`/gravity-scan/`）
- Recruit LP（`/gravity-recruit/`）
- Cultivate LP（`/gravity-cultivate/`）
- 必要に応じて Coaching / Orbit / Gravity TOP / 5/15 セミナー LP

**FTP デプロイ情報：**
- ホスト：sv16489.xserver.jp
- ユーザー：xs992119
- パスワード：cgq1fv99
- パス：growthfix.jp/public_html/PATH/

**機械チェック（CLAUDE.md ルール）：**
- LP 編集後：自動 mobile audit（hook で自動実行）
- 必要に応じて：`bash 06_開発/scripts/lint_consistency.sh`

### Step 7：最終サマリ + memory 更新（30 分）

- 統合スパーリング全件の結果サマリ（実装 N 件 / 反映なし N 件 / 統合 N 件）
- memory `project_aoki_satoshi_benchmark_260511.md` を**統合スパーリング完了版に更新**（または `_v2.0` 新規作成）
- `/work-log` スキル実行（タスク追記 + 月次サマリ更新 + デイリーログ振り返り）

---

## 3. 注意事項（前セッションの学び）

### 3-A. 字幕分析の限界

- YouTube 自動生成字幕を使うため**逐語引用は誤認識を含む**
- LP / 発信物に転用前に**原動画確認必須**
- 誤認識例：「散方よし」→ 三方よし / 「異人責任」→ 委任責任

### 3-B. 独自軸希釈回避（最重要）

- GrowthFix は **複数領域編集型**（識学・アチーブメント単一権威担ぎ型と差別化）
- Tier 2 抽出時も **GrowthFix 独自軸（4 型診断 × CODE × Scan × Authentic Self × AI ネイティブ）を希釈しない**判断を Tier 3 に落とせる
- 5/11 壁打ちで **16 件中 6 件を「反映なし」判断**した実績あり（独自軸を守る）

### 3-C. 第 1 フェーズ集中軸との整合

- 5/15 セミナー直前・第 1 フェーズ = Shift R 売り集中軸
- Tier 2 のうち Shift R / Scan 寄与度高いものを優先
- Shift C / Cultivate 関連は第 2 フェーズ（2026 Q3 以降）向けとして v1.1 に保持

### 3-D. AI コスト管理

- 6 軸並列 Sonnet（Tier 1 で 約 150 万 tokens 消費）
- Tier 2 は 30-50 件 × 平均字数（小さめの動画含む）で **約 100-200 万 tokens 想定**
- 1 軸あたり 10-20 動画なので 1 Agent の負荷は前回より軽い

---

## 4. 期待アウトプット

| ファイル | 内容 |
|---|---|
| `_tier2_selection_v1.md`（新規） | 残 360 件から再厳選した Tier 2 = 30-50 件 |
| `_selected_tier2_ids.txt`（新規） | video_id リスト |
| `transcripts_tier2/`（新規） | vtt 60-100 ファイル |
| `transcripts_tier2_clean/`（新規） | テキスト 30-50 ファイル |
| `_extraction_1〜6_*_tier2.md`（新規） | 6 軸抽出（Tier 2） |
| `260511_青木仁志ベンチマーク分析_GrowthFix経営OS反映マスタープラン_v1.1.md`（新規） | v1.0 を補完するマスタープラン v1.1（TOP 30-40） |

---

## 5. 完了報告フォーマット（石井さん向け）

### 中間報告（Step 5 完了時 = v1.1 マスタープラン完成）

```
Tier 2 抽出完了 / マスタープラン v1.1 完成。
- 再厳選：[N] 件・6 軸抽出新規フレーム [M] 件
- TOP 30-40 統合マスター完成（処理済 10 件マーク付き）
- 残スパーリング候補：[Tier 1 残 10] + [Tier 2 新規 N] = 計 [N] 件
- Step 6 統合スパーリングへ進む（石井さん判断要請）
```

### 最終報告（Step 7 完了時 = 統合スパーリング完了）

```
青木仁志ベンチマーク Tier 1/2 統合スパーリング完了。
- 全件処理：[N] 件（実装 [A] / 反映なし [B] / 統合 [C]）
- LP 改修：Scan [a] / Recruit [b] / Cultivate [c] / 他 [d] 箇所
- memory 更新：project_aoki_satoshi_benchmark_260511.md 統合スパーリング完了版
- 反映なし判断 [B] 件 = GrowthFix 独自軸の希釈回避
- 09_会社OS 直接反映なし（マスタープラン §7 引用ルール準拠）
- AI コスト：約 [tokens] 万トークン
```

---

## 6. 既存セッション（5/11 メイン）との分業

| 役割 | 内容 |
|---|---|
| **5/11 メインセッション**（既終了） | TOP 20 のうち 10 件壁打ち（実装 9 件・反映なし 6 件・統合 1 件）= Tier 1 半完走 |
| **今セッション**（このファイル） | **Step 1-5 抽出系 + Step 6-7 統合スパーリング全部実施** |
| **5/12 以降** | 第 2 フェーズ準備（Shift C 立ち上げ時期のスパーリング再開判断） |

---

## 7. 起動手順（このファイルを Read した直後）

1. memory `project_aoki_satoshi_benchmark_260511.md` + `reference_aoki_frameworks_consolidated.md` を Read
2. マスタープラン v1.0 §1-B（TOP 20）と §6（差別化軸）を確認
3. `_theme_classification_v1.md`（除外グループ）を Read
4. **Step 1：再厳選 Agent 起動**（analysis-runner Sonnet）
5. Step 2-5 を順次実行 → マスタープラン v1.1 完成
6. **Step 6：石井さん × Claude Code で統合スパーリング**（最終ゴール）
7. Step 7：最終サマリ + memory 更新 + /work-log

**所要時間目安：** 抽出 3-5 時間 + 統合スパーリング 5-8 時間 = 計 8-13 時間（1 セッションでは長いので適宜区切る）
**石井さんの介入ポイント：**
- Step 1 完了時（Tier 2 リスト 30-50 件の方向確認）
- Step 5 完了時（v1.1 マスタープラン受領 → Step 6 へ進む合意）
- **Step 6 全件**（1 件ずつ A/B/C/D/E 等の判断・推奨案採否）

---

**この引き継ぎ書 v1.0 は 5/11 メインセッション最終時点のもの。新セッションで追加発見があれば v1.1 として更新可。**

## 8. 新セッション起動時のユーザー第一声テンプレート

新 Claude Code セッションを起動したら、最初のプロンプトとして以下を入力：

```
青木仁志ベンチマーク Tier 2 抽出 + 統合スパーリングを開始します。

引き継ぎ書を最初に Read してください：
/Users/ishiinobuyuki/Documents/Obsidian Vault/08_情報収集/260511_青木聡分析/_handoff_to_next_session_v1.0.md

引き継ぎ書の Step 1 から順次実行してください。
Step 1 完了時に Tier 2 リスト 30-50 件を確認させてください。
最終ゴールは Tier 1 残 10 件 + Tier 2 新規の統合スパーリング完了です。
```
