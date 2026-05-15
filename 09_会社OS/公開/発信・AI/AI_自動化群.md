# AI_自動化群.md（子 SSOT・260507 Phase 9.1 分割）

> **親 SSOT：** `09_会社OS/公開/発信・AI/AI.md`
> **位置付け：** AI.md Part 2 の自動化スクリプト群・Skill 群・実装パターン詳細（370 行）を分離。
> **親 MD に残置：** Part 1 思想層（四春期戦略 / 速度非対称性 / ハーネスエンジニアリング核）+ Part 2 中核（実績 / AI 戦略的 3 役割 / Obsidian Vault 構造 / Claude memory システム / モデル選択経済）+ Part 3 ハーネス層。
> **本書の範囲：** Skill 自動化群（GrowthFix 専用）/ 自動化スクリプト群 / LP 共通基盤アセット / サブエージェント分離パターン / RECODE Agent 並列実行パターン / ウニ丼理論の進化 / 09_会社OS/ 自体の実装証拠。

---

### Skill 自動化群（GrowthFix 専用）

| Skill | 用途 |
|---|---|
| `/daily` | 今日のデイリーログ作成（事業加速アクションプラン連携・Meta 広告数値・Fitbit ヘルスデータ付き） |
| `/weekly-close` | 週次クローズ（バランスホイール週次レビュー＋ポジションチェック＋来週の設計） |
| `/work-log` | 今回の Claude Code 作業をログに記録 |
| `/iran-tweet` | イラン戦争デイリーアップデート FB 投稿文（堀田5原則・1000文字・朝1回） |
| `/japan-market` | マクロ経済ポジションチェック（日本市場＋中国＋米国 PC＋INPEX 定点） |
| `/yoshida-analysis` `/nakajima-analysis` | メルマガ投資判断分析 |
| `/youtube-analysis` | YouTube 動画字幕自動取得→指定観点で分析 |
| `/sales-prep` | 見込み客の事前情報から商談仮説を生成 |
| `/note-growth` `/note-article` | Note 連載執筆（堀田5原則ベース・セルフレビュー付き） |
| `/session-prep` | 次回コーチングセッションの事前レポート生成 |
| `/unidon` | サービス設計をウニ丼モデルで再設計（堀田フレーム） |

**設計原則：** 1 タスク 1 Skill。Skill 同士は連携を強制せず、独立に動かせる。

### 自動化スクリプト群

#### データ取得・分析系
| スクリプト | 用途 |
|---|---|
| `06_開発/scripts/meta_ads_daily.py` | Meta 広告 API から日次数値取得→デイリーログ自動更新 |
| `06_開発/scripts/fitbit_daily.py` | Fitbit ヘルスデータ取得 |

#### 整合性・検証系
| スクリプト | 用途 |
|---|---|
| `06_開発/scripts/lint_consistency.sh` | SSOT に基づく LP / コーポレート / WP の整合性チェック（週次推奨） |
| `06_開発/scripts/verify_deployment.sh` | 19 LP デプロイ後の HTTP 200 + 共通アセット稼働 + バージョン整合性検証（23 項目） |

#### LP 一括運用系（260429 整備）
| スクリプト | 用途 |
|---|---|
| `06_開発/scripts/bump_cache_buster.sh` | mobile.css?v=YYYYMMDD[a-z] を全 HTML で一括 bump（10 分→ 30 秒） |
| `06_開発/scripts/migrate_seminar_bar_to_js.py` | 19 LP のインライン LIVE WEBINAR バー HTML を削除→ JS 化（実行済・実行履歴用） |
| `06_開発/scripts/inject_ab_test_script.py` | 19 LP に ab-test.js script タグを seminar-bar.js より先に挿入（実行済） |
| `06_開発/scripts/add_service_schema.py` | 5 サービス LP に Schema.org Service JSON-LD を追加（実行済） |

#### デプロイ系
| スクリプト | 用途 |
|---|---|
| LP 一括 FTP デプロイ（`deploy.sh`・curl ベース）| 43 ファイルを 8 並列で本番反映 |
| WhitePaper PDF 再生成（Chrome ヘッドレス） | HTML 更新 → PDF 再生成 → デプロイの 1 コマンド手順 |

**全て自社ドメイン内で完結。** 外部 SaaS への依存を最小化。

### LP 共通基盤アセット（260429 整備・5 本稼働）

「経営×AI で会社を回す」の Web 運用版。**19 LP の重複を共通アセット側に集約**し、LP 個別 HTML/CSS の保守工数を最小化する基盤。

| アセット | 役割 | 更新頻度 |
|---|---|---|
| **`/assets/css/mobile.css`** | 全 LP のモバイル最適化（768px / 600px / 375px ブレイクポイント） | 中（要 cache buster bump） |
| **`/assets/css/components.css`**（260429 新規）| 新規 LP 用 Hero/CTA/Card/Section コンポーネント。`gf-` prefix で命名統一 | 低 |
| **`/assets/js/tracking.js`**（260429 拡張）| GA4 + GTM + Meta Pixel 初期化＋ `window.GrowthFixEvents` 名前空間（7 イベント API）＋ `data-event-cta` 自動 click 計測 | 中 |
| **`/assets/js/seminar-bar.js`**（260429 新規）| LIVE WEBINAR バー動的注入。`SEMINAR` 定数 1 箇所変更で全 LP 反映＋日付ベース自動撤去 | 高（キャンペーン都度） |
| **`/assets/js/ab-test.js`**（260429 新規）| UTM 駆動式 A/B テスト（`?variant=A\|B\|C`）＋ `data-ab-test` 宣言式＋ JS API＋ GA4 `ab_test_view` イベント | 中（テスト都度） |

#### 設計原則（LP 共通基盤）

1. **HTML 側はインラインスタイルで装飾を完結**（CSS 依存を最小化＝サードパーティ CDN 落ちでも崩れない）
2. **共通アセットは defer 読み込み**（render-blocking なし）
3. **アセット間の依存は明示**（例：seminar-bar.js は ABTest があれば使う・なければデフォルト）
4. **19 LP に script タグを挿入する Python マイグレーションスクリプトを残す**（再実行・新規 LP 統合に再利用可能）
5. **本番動作検証は `verify_deployment.sh` で機械化**（HTTP 200・script 参照・インライン残留・バージョン整合の 4 観点）

#### LP 共通基盤の運用効果

| 項目 | Before | After |
|---|---|---|
| LIVE WEBINAR バー文言変更 | 19 LP 編集（60 分） | seminar-bar.js 1 箇所（5 分） |
| キャンペーン期日後の撤去 | 手動で 19 LP 編集 | 自動非表示（日付ベース） |
| A/B テスト導入 | 各 LP 個別 JS 実装 | UTM パラメータのみ |
| 計測イベント追加 | 19 LP 個別実装 | tracking.js 1 行 |
| デプロイ後検証 | 目視 15 分 | スクリプト 2 分 |

**含意：** 「19 LP × N 種類の運用変更」が「1 アセット × N」に圧縮された。**保守工数が線形ではなく対数で増える基盤**。

### モデル選択経済（Opus / Sonnet 使い分け）

| 用途 | モデル | Why |
|---|---|---|
| 戦略判断・壁打ち | **Opus** | 「思想を伴う深い思考」が必要。出力差がコスト差に見合う |
| レポート生成・プロンプトテスト | **Sonnet** | 「思想 6 割：ロジック 4 割」の表現タスクは Sonnet で十分。コスト差大 |
| プロダクト実装（CODE / Scan 生成API） | **Sonnet** | 大量呼び出しでコスト最適化 |
| **大量ファイル並列分析（Agent 並列実行・260501 確立）** | **Sonnet × 6 並列** | **6 Agent に各 5-6 ファイル分担で 6,571 行を約 4-15 分で抽出。Opus 単独より圧倒的に高速・低コスト** |
| **LP HTML / CSS 編集（260503 サブエージェント分離）** | **Sonnet（lp-implementer 経由）** | メイン Opus は議論専念・実装は Sonnet サブエージェント委譲でコスト圧縮 + メイン context 汚染防止 |
| **`06_開発/scripts/` 改修（260503 サブエージェント分離）** | **Sonnet（script-writer 経由）** | 純粋コード作業に思想層判断不要・Sonnet で品質十分 |
| **YouTube 動画分析（思想・対話・コーチング系・260503 ユーザー feedback 確定）** | **Opus（analysis-runner 既定）** | 偏愛・えげつない具体・人格・翻訳構造の抽出には Opus 級の意味理解が必須。Sonnet では学者モード化で「綺麗にまとめた抽象論」になり Note 素材として死ぬ |

**判断軸：** 「この出力に思想の濃さが必要か？」YES なら Opus、NO なら Sonnet。

**追加判断軸（260503）：** 「この分析の出力は壁打ち入力（戦略素材）になるか？」YES なら Opus（出力の質が後続戦略判断の質を決める）、NO（量と速度の構造化抽出のみ）なら Sonnet。RECODE 系並列抽出は後者・YouTube 思想分析は前者。

### ★ サブエージェント分離パターン（260503 確立・実行エージェント層の物理ファイル化）

**ルール：「議論=Opus / コード=Sonnet」をネイティブ機能では自動切替できない（settings.json は単一 model のみ）。**`~/.claude/agents/*.md`** に「モデル + system prompt + tools + ハーネス装置」を 1 ファイルでパッケージ化し、メイン Opus スレッドから Agent tool で物理委譲する分業構造を採用する。**

**Why：** メインスレッドを毎回 Opus にしておくと議論・思想・戦略は最高品質を確保できるが、LP HTML 編集や Python script 改修まで Opus で実行するとコストが膨らみ、context window もコード差分で汚染される。サブエージェントに委譲すると以下が同時に解決する：

- **コスト圧縮**：実装フェーズだけ Sonnet 単価で動く
- **context 汚染防止**：サブエージェントは独立 context・メイン Opus の議論履歴を汚さない（長セッションで効く）
- **ハーネス内蔵**：Vault 固有プロトコル（mobile audit / SSOT lint / 秘匿情報ガード）を system prompt に転記することで feedback メモリ依存から脱却
- **思想層と実装層の分離強制**：「サブエージェントには思想判断させない」を system prompt に書くことで、コア層（メイン Opus）の責務範囲を物理的に守る

#### GrowthFix での実装（260503 開始・2 ファイル）

| エージェント | パス | 担当 | model | 内蔵ハーネス |
|---|---|---|:-:|---|
| **lp-implementer** | `~/.claude/agents/lp-implementer.md` | LP HTML / CSS / 診断 UI 編集 | sonnet | LP 編集後に `audit_mobile_sync.py` 自動実行 / SSOT 用語触れたら `lint_consistency.sh` 自動実行 / SSOT 用語チェック / header/footer 雛形先行更新ルール / スクショ先行ルール |
| **script-writer** | `~/.claude/agents/script-writer.md` | `06_開発/scripts/` Python・bash 改修 | sonnet | `python3 -m py_compile` 構文チェック / `--dry-run` フラグ実装規定 / 秘匿情報ガード / FTP/API 本番書込はユーザー承認必須 |

**メイン Opus スレッドからの呼び出し方：**
```
「lp-implementer に投げて」「Sonnet で実装して」等の自然言語
→ メイン Opus が Agent tool 経由で自動委譲
```

#### 委譲しないもの（メイン Opus に残す）

- 思想・コピー・タグライン・サービス名の意思決定
- 価格・期間・参謀名の変更（SSOT 変更を伴うもの）
- 新規サービス設計・LP 構成の根本変更
- Note 記事・思想 MD（09_会社OS 配下）の執筆
- 仕様が曖昧なスクリプト新規作成（仕様確定後に script-writer に投げる）

→ サブエージェントの system prompt に「以下に該当したらメインスレッドに差し戻す」と明記してある。これがコア層保護のハーネス。

#### 判断軸（新規エージェント追加時）

1. **頻度**：「同じ作業を週 1 回以上やるか？」YES → エージェント化候補
2. **思想性**：「思想層判断が伴うか？」YES → コア（メイン Opus）に残す・エージェント化しない
3. **Vault 固有性**：「Vault 固有のハーネス（lint / audit / SSOT）が必要か？」YES → system prompt に内蔵
4. **モデル経済**：「Sonnet で品質が十分か？」YES → サブエージェント化でコスト圧縮効く

#### 警戒事項

- ❌ 思想層判断をエージェントに委譲する → メインスレッドに差し戻す規定を system prompt に必ず書く
- ❌ `tools: *` で全許可 → 最小権限原則（必要な tools だけ列挙）
- ❌ 同じハーネスを複数エージェントで重複実装 → 共通スクリプト（`lint_consistency.sh` 等）を呼ぶ参照型に統一
- ❌ Codex / 他 IDE で代替しようとする → Vault 固有のハーネス層（CLAUDE.md / MEMORY.md / Part 3 プロトコル）が効かなくなる。**Vault 内編集は Claude Code 固定**

#### 将来拡張候補（260503 夜・全 3 件作成完了）

- ✅ `note-writer`（Note 連載執筆エージェント・Sonnet・堀田 5 原則 + culture.md Part 3 内蔵）
- ✅ `analysis-runner`（YouTube/参考資料分析エージェント・Sonnet 並列・RECODE パターン適用）
- ✅ `deploy-runner`（FTP デプロイ + verify_deployment.sh 自動実行・Haiku モデル）

新規追加時は本セクションに行追加 + harness.md Part 2 既存ハーネス資産表に同期反映。

### ★ 11 新規エージェント群（260513 R7・堀田セッション反映）

> **起点：** 260513 堀田セッション R7 オペレーション設計確定 → Phase B-3 で 7 本仕様 v0.1 完成 / 残 5 本は Phase C 22-CT/CU で実装予定
> **配置：** 仕様 v0.1 = `06_開発/scripts/agents_specs/`（Vault 内）／ 本番運用 = `~/.claude/agents/*.md`（推敲後展開）
> **実装パターン：** 1 ファイルパッケージ化（model + system prompt + tools + ハーネス装置を 1 MD に集約）

**通底原則：Gravity Coaching = 思想の主軸（不変）／ R・C・Orbit = マネタイズ装置（最適化対象）**
全 11 エージェントは 9:1 二層分離原則（裏方=AI 9 / 表方=経営者 9）に準拠。

#### エージェント一覧

| # | エージェント | 対象 | 状態 | 仕様パス |
|:-:|---|:-:|:-:|---|
| 1 | minutes-analyzer（議事録分析・共通基盤）| R/C/O | v0.1 仕様完成 | `06_開発/scripts/agents_specs/01_minutes-analyzer_v0.1.md` |
| 2 | scout-analyzer（スカウト分析）| R | v0.1 仕様完成 | `06_開発/scripts/agents_specs/02_scout-analyzer_v0.1.md` |
| 3 | jd-hypothesis（JD 仮説）| R | v0.1 仕様完成 | `06_開発/scripts/agents_specs/03_jd-hypothesis_v0.1.md` |
| 4 | recruit-layer-audit（レイヤー 1-5 監査）| R | v0.1 仕様完成 | `06_開発/scripts/agents_specs/04_recruit-layer-audit_v0.1.md` |
| 5 | recruit-weekly-report（週次レポート生成）| R | v0.1 仕様完成 | `06_開発/scripts/agents_specs/05_recruit-weekly-report_v0.1.md` |
| 6 | cultivate-goal-engine（個人別目標設計）| C | v0.1 仕様完成 | `06_開発/scripts/agents_specs/06_cultivate-goal-engine_v0.1.md` |
| 7 | cultivate-1on1-support（1on1 サポート・個別最適 20% 集中）| C | v0.1 仕様完成 | `06_開発/scripts/agents_specs/07_cultivate-1on1-support_v0.1.md` |
| 8 | cultivate-survey-followup（個別フォロー提案エンジン）| C | 22-CT 実装予定（Phase C）| - |
| 9 | cultivate-meeting-facilitator（AI 会議体ファシリテーター）| C | 22-CT 実装予定（Phase C）| - |
| 10 | cultivate-manager-copilot（AI マネージャー副操縦士）| C | 22-CT 実装予定（Phase C）| - |
| 11 | orbit-zoom-pipeline（Zoom → 月次レポート自動化パイプ）| O | 22-CU 実装予定（Phase C）| - |
| 12 | orbit-15axis-gate（軸 15 個ゲート判定エンジン）| O | 22-CU 実装予定（Phase C）| - |

合計：12 エージェント（minutes-analyzer は共通基盤・残 11 = R 4 / C 5 / O 2）

> **🔴 260514 v3.0 命名再編注記（22-EH 連動）：** 上記 12 エージェント命名（scout-analyzer / cultivate-goal-engine / orbit-zoom-pipeline 等）は **260514 夜 v3.0 で全廃止 → RT-1〜RT-6 / CT-1〜CT-6 / OT-1〜OT-6 に統一**。サービス別 6 本ずつ計 18 本のスロットに再編成。22-EH（260514）で **OT-1/2/3 + RT-4/5 + CT-1/2/3 = 8 本を MVP 実装完了**（詳細は本書末尾「22-EH 8 AI エージェント MVP 全実装」セクション）。残 10 本（RT-1/2/3/6 + CT-4/5/6 + OT-4/5/6）は 6 月以降順次実装。**🔴 260515 v3.0 Cultivate 命名再編注記：** CT-1〜CT-3 の磁場名称を v3.0 3 設計に更新（CT-1 既存 SaaS データ統合エンジン / CT-2 論文 × AI 介入提案エンジン / CT-3 半期物語化エンジン）。スクリプトファイル名（cultivate_vision_engine.py 等）は実装整合のため温存。

#### 9:1 二層分離原則の全エージェント適用

| 層 | 比率 | 全エージェント共通の適用 |
|---|:-:|---|
| **裏方**（実務エージェント側）| AI 9 : 経営者 1 | データ収集 / 議事録文字起こし / パターン抽出 / 仮説生成 / レポート自動生成 |
| **表方**（経営者 / マネージャーの意思決定側）| 経営者 9 : AI 1 | 最終選択 / 判断 / カスタマイズ / 顧客への伝達 |

#### Phase 別実装ロードマップ

| Phase | 期間 | 実装内容 |
|---|---|---|
| **B-3**（5/14 完了済）| 1 日 | 7 本仕様 v0.1（Vault 内）|
| **C 22-CT**（5/28-6/3）| 1 週間 | Cultivate 残 3 本実装（個別フォロー / 会議体 / マネージャー副操縦士）|
| **C 22-CU**（6/4-6/17）| 2 週間 | Orbit 2 本実装（Zoom 自動化 / 軸 15 個ゲート判定）|
| **D 統合**（6/18-6/30）| 2 週間 | 全 11 本統合テスト + 1 件目顧客試験運用 |

#### 各エージェントの共通ハーネス

- **9:1 二層分離準拠**：「経営者の意思決定を奪う最終答え」になっていない
- **個人情報マスキング済**：候補者氏名 / 給与等は ANON 化
- **学術武装併記**（該当時）：Locke-Latham / Edmondson / Theeboom 等の参照
- **「足すコーチではなく抜く翻訳者」原則準拠**：本人の言葉を引き出す（AI 創作で埋めない）

#### 関連 SSOT

- 仕様 v0.1：`06_開発/scripts/agents_specs/01-07_*.md`（7 本完成）
- 統合 SSOT 反映プラン：`04_GrowthFix/01_サービス設計/_横断_フレーム_戦略/260513_堀田セッション_統合SSOT反映プラン_v0.1.md`
- Phase B 実行計画：`04_GrowthFix/01_サービス設計/_横断_フレーム_戦略/260513_PhaseB_実行計画_機能層4MD_営業資料4_エージェント7本.md`
- AI.md Part 3 二層分離原則 / harness.md（更新中）

#### 試運転の知見（260503 夜・lp-implementer 初回起動で確立）

**知見 1：mid-session で作成したサブエージェントは Agent tool から見えない**
- `~/.claude/agents/*.md` を作成しても、その**セッション内**では Agent tool の subagent_type で参照できない
- 次回セッション起動時に自動 discovery される
- 暫定対応：当該セッション中は `general-purpose` に当該エージェントの system prompt を内包する形でプロンプト渡しで機能等価運用
- **運用ルール：** 新規エージェント作成は「次セッションで使う」前提。当日中に試運転したい場合は general-purpose 経由で system prompt を渡す

**知見 2：エージェント間の scope crossover が発生しうる**
- lp-implementer 初回試運転で `audit_mobile_sync.py` のロジックバグを発見し、エージェントが**自発的にスクリプトも修正した**（script-writer 領域に越境）
- 修正自体は正解（audit が `[style*="..."]` で覆われたインラインスタイルを「未対応」と誤判定していた）
- ただし暗黙の scope creep は将来的に責任境界が曖昧になる
- **対応：** lp-implementer の system prompt に「`06_開発/scripts/` への直接編集禁止・発見した bug は『スクリプト修正提案』として報告のみ」を追記済（260503 夜）

**実運用上の含意：**
- サブエージェントは「自分のスコープを越えて発見した問題」を**実装ではなく報告で返す**設計が正しい
- メインスレッドが報告を受けて適切なエージェント（script-writer）に再委譲する
- これにより 3 層構造の責任境界（コア層が判断・各エージェントが実行）が機械的に維持される

**詳細：** `harness.md` Part 1「実行エージェント層の物理ファイル化」 ／ `feedback_model_selection_sonnet.md`

### ★ RECODE Agent 並列実行パターン（260501 朝確立・AI ネイティブ経営者の知的資産活用）

**事例：5/1 朝の参考資料 33 ファイル分析**
- 対象：Desktop/参考資料 33 ファイル / 6,571 行（過去のクライアント壁打ちセッションログ）
- 方法：6 Agent 並列実行（各 5-6 ファイル × Sonnet）
- 抽出軸：6 軸（採用ペイン / 躍動組織課題 / 経営者生発話 / C-5 判定実例 / サービス検証材料 / ★ サービスアップデート発見）
- 結果：**278 発見（うち軸 6 サービスアップデート 49 件）を約 10-15 分で抽出**
- 後工程：6 中間ファイル統合 → Tier 1/2/3 優先度分類レポート → memory 起こし

**他社が真似できない理由：**
- 100 本超の Claude memory + Obsidian Vault 構造化資産が存在しない
- 過去のクライアント壁打ち音声書き起こし＝**自分の知的資産**が蓄積されていない
- AI Agent 並列実行のオーケストレーション運用文化がない
- 過去資産から「サービスアップデート発見」に直結させるフレームがない

**運用パターン：**
1. **対象資産の特定**（過去の壁打ち / セッション録画 / Note 連載 / セミナー音声 等）
2. **抽出軸の事前定義**（6 軸 × ★/⚪/△ マーク等）
3. **Agent への分担分配**（行数バランスで 5-7 Agent に分割）
4. **共通プロンプトテンプレ**（プロジェクト背景 + 重複検出用 SSOT + 抽出軸 + 出力フォーマット）
5. **Sonnet 並列実行**（並列数 = ファイル数 ÷ 5-6）
6. **コーディネーター（Opus or 自分）が統合**

**詳細：** `04_GrowthFix/01_サービス設計/260501_参考資料分析_Shift_RA_検証アップデート_統合.md` ／ `memory/project_shift_rc_field_validation_260501.md`

### ★ ウニ丼理論の進化（260501 確立・標準化 = AI / トレーニング = 人間の時系列実装）

**従来のウニ丼理論：** 高価値時間（ウニ）と低コスト労働（ご飯）を**サービス内で同時に**配分

**260501 の進化：** ウニ丼を**時系列で実装**する設計パターン

| フェーズ | 比率 | 担い手 | 内容 |
|---|---|---|---|
| **標準化フェーズ**（Month 1）| AI 70-75% + 石井 25-30% | AI が起草・石井が引力翻訳の対面セッション | アウトプット物（採用 3 点セット / 躍動 3 点セット）の生成 |
| **実装フェーズ**（Month 2-3）| 石井 35-40% + AI+業務委託 60-65% | 業務委託パートナー + 石井監修 | 幹部 OJT・実機運用・同席フィードバック |

**Shift R/C 別 AI 比率：**
- Shift R 標準化：AI 70%（採用台本生成）
- Shift C 標準化：**AI 75%**（得意技 ② AI × 人事データ × エンゲージメント設計を活用 → 既存サーベイ/1on1 メモ/人事データ分析を AI が回せる強み）

**判断軸：** 「アウトプット物の生成は AI で再現可能か？」YES → AI 比率最大化／「人間の対面でしか引き出せない引力源・暗黙知か？」YES → 石井対面セッションに集中

**他社が真似できない理由：**
- AI に標準化を任せられる前提として「**SSOT 整備 + 過去資産の Claude memory 化**」が必要
- 業務委託パートナー組成（Shift R 採用基盤 OPS / Shift C 人事データ × エンゲージメント設計）が機能する必要
- 経営者の引力源を翻訳できるのは経営者自身の対面セッション 4-5h のみで他者代替不可

**詳細：** `09_会社OS/公開/ガイドライン/商品.md` Shift R/C セクション ／ `memory/project_unidon_service_ratios_260424.md`

### 実装証拠：本「09_会社OS/」フォルダ自体

**メタ事例として最強：**

- このフォルダの設計（4カテゴリ × 公開非公開 × T3 思想-運用2層）は、Claude との壁打ちで Q1〜Q5 の選択肢設計＋推奨提示を経て確定
- Phase 1 の思想層 6 本（合計約1,000行）は、既存 Claude memory を抽出ベースに 1 セッションで完成
- 17 ファイル全部の生成は約 30 分

**他社が真似できない理由：**
- 100本超の Claude memory が存在しない
- Obsidian Vault 構造が用途別に切れていない
- 主軸先行ルール・思想 6 割：ロジック 4 割の運用文化がない
- 自社ドッグフードの覚悟がない

→ 「経営×AI で会社を回す」は、ツールを買えば真似できるものではない。**強み × 想い × 偏愛 × 運用文化のセット**で初めて成立する。

### クライアント展開モデル（Shift / Coaching への組み込み）

GrowthFix が自社で完成させた「会社OS化」を、クライアント企業に展開する設計：

| Phase | 内容 |
|---|---|
| Week 1-2（Shift Phase 1） | 経営者の引力源（強み × 想い × 偏愛）の言語化＝CODE / Scan 拡張 |
| Week 3-6 | クライアント版「会社OS」テンプレ（本フォルダの公開部分）を提供 |
| Week 7-12 | 4カテゴリ × T3 形式で各MDを埋める伴走。クライアント企業の Obsidian / Notion 構築支援 |
| Orbit 移行後 | 月次で OS 更新・整合性レビュー |

これは「コンサルが資料を作る」のではなく、**経営者が AI と一緒に自社 OS を組み上げる伴走**。

### ★ 6 セッション連続稼働の前倒し成功パターン（260501 実証・122 時間相当を 13 時間で完遂）

**5/1 実績：** 1 日で 50 タスク完遂（手作業換算 135.3h → AI 実績 13.1h ／ **削減率 90%**）

**6 セッション構造：**
1. 朝〜夕（13 タスク）：Scan 診断 UI 全面書き換え + CODE フルテスト + Orbit minimal LP 化 + RECODE 39 要素抽出 + 7 論点確定
2. 夜（11 タスク）：5/2 詰め論点 7 件確定 + 商品.md SSOT 反映 + Shift LP / Scan / Orbit / 営業.md / 接続装置.md 全更新 + 並列デプロイ
3. 15 時セッション後（12 タスク）：Scan 完全同期 + 参考資料 33 ファイル分析（6 Agent 並列）+ 統合分析 + memory 起こし
4. Shift R/C シャープ化（5 タスク）：A4 1 枚サマリー + Shift R 49 質問下書き + シャープ版議論 + 5 論点詰め
5. Shift R/C 49 質問下書き × 2（5 タスク）：5/8 モニター用 6 VP 統合資料 + Shift C 1 文 + 5 論点 + 49 質問
6. LP 構成判断 + work-log + company-os 反映（4 タスク）

**前倒し成功の根本要因：**
- **引き継ぎ MD + memory 永続化プロトコル**で「次の Node が即着手できる」状態を作る
- 5/2 朝予定だった Step 1-6 を**5/1 夜 Node に前倒し完遂**（5/1 引き継ぎ詳細化が直接生産性圧縮）
- **AI が下書き → ユーザー赤入れ**の二段プロセスで疲労を最小化
- Sonnet × 並列実行で大量分析を 4-15 分に圧縮

**真似できない構造：**
- Claude Code Max + Opus 4.7 + Sonnet 4.6 並列の運用環境
- Obsidian Vault 構造 + 100 本超 memory + SSOT 整備済の前提資産
- 主軸先行ルール + シャープ化哲学 + 9:1 アウトプット原則の運用文化
- 健康優先（HRV モニタリング・23 時就寝 7h 確保）の自己管理規律

**詳細：** `04_GrowthFix/04_デイリーログ/260501_daily.md` ／ `2605_work_log.md`

### ★ secrets 防御パターン（260502 GitHub Push Protection 事故対応で確立）

**事故事実：** 5 ヶ月分 commit を push しようとして **GitHub Push Protection が Anthropic API Key 5 箇所を検出してブロック**。包括スキャンで合計 **8 ファイル**に Anthropic API Key、**10 ファイル**に FTP パスワードが残存していた。

**3 層防御パターン：**

| 層 | 防御装置 | 対象 |
|:-:|---|---|
| **① 入口防御** | `.gitignore` 拡張パターン | `**/config.php` ／ `_archive/` ／ `06_開発/scripts/config_*.json` ／ `.env` 系 |
| **② commit 直前防御** | `auto_commit.sh` の secrets 検出ガード | 既知 secrets パターン（`{FTP_PASSWORD}` / `sk-ant-` / `api_key.*[a-zA-Z0-9]{20,}` 等）検出時に commit 中止 |
| **③ push 直前防御** | GitHub Push Protection（保険） | 既知 secrets フォーマット（Anthropic / OpenAI / GitHub PAT 等）を自動検出してブロック |

**運用ルール：**
- API キー / パスワードは **必ず環境変数 or .env / config 系ファイル**で管理
- これらファイルは `.gitignore` で git から除外（local only）
- 既存ファイルに secrets が残っている場合は `${ENV_VAR_NAME}` プレースホルダに置換
- 単一情報源を 1 ファイルに集約（例：`06_開発/開発ツール/FTP情報_メインFTPアカウント.md` を local only で SSOT 化）

**事故時の復旧手順：**
1. GitHub Push Protection のエラーメッセージから検出箇所を特定
2. 包括スキャン（`grep -rl "sk-ant-" --include="*.php" ...`）で他に残存ないか確認
3. `.gitignore` 拡張 + 必要に応じて sanitize（プレースホルダ化）
4. `git reset --soft HEAD~N` で commit を取消 → 再 stage → 再 commit
5. 再 push（GitHub Push Protection が通れば成功）

**詳細：** `09_会社OS/公開/文化/判断基準.md` Part 2「★ git 履歴運用」 ／ `06_開発/scripts/hooks/auto_commit.sh`

### ★ auto_commit hook（5 ヶ月放置事故 → ハーネスエンジニアリング実装事例・260502 確立）

**事故事実：** 2025-12-26 〜 2026-05-02 の 5 ヶ月間 git commit が一度も実行されず、WhitePaper LP の「昨日のブラッシュアップを巻き戻したい」要望に対して git からのロールバックが不可能だった。

**ハーネスエンジニアリング 3 層構造での実装：**

| 層 | 役割 | 実装 |
|:-:|---|---|
| **コア層** | 「すべての編集に履歴を残す」原則 | git の commit 概念 |
| **ハーネス層** | 自動 commit 装置（人間が忘れても動作）| `auto_commit.sh`（Stop event hook）|
| **実行エージェント** | Claude Code セッション | Stop event 発火時に hook 自動起動 |

**設計上の判断（trade-off・260503 更新）：**

- ✅ **自動 commit on Stop**：セッション終了時に変更があれば必ず commit
- ✅ **secrets 検出ガード**：誤って secrets を commit しないよう事前ブロック
- ✅ **自動 push する**（260503 更新・5/2 設計の "手動のみ" から転換）：Stop hook は単発発火のため認証 loop しない／GitHub Push Protection が secrets 二重防御として機能／push 失敗時は warning のみ・hook を exit 0 で終了させ次回阻害しない
- 旧設計（5/2）：手動 push のみ ── 5/2 当時は GitHub Push Protection で secrets ブロックされた直後だったため慎重設計だったが、secrets ガード強化と placeholder 化で混入リスクが大幅低減・自動化で操作摩擦ゼロ化を優先

**TDD 経営原則との整合：**
- 事故 → 原因分析 → ハーネス装置の実装 → 「同じ事故が二度と起きない構造」を確立
- 5 ヶ月放置事故は 1 回限りの教訓 → auto_commit hook で永続的に防御
- 「人間の規律」に頼らず「装置の自動化」で防御 ── ハーネスエンジニアリングの中核思想

**詳細：** `06_開発/scripts/hooks/auto_commit.sh` ／ `09_会社OS/公開/文化/判断基準.md` Part 2「★ git 履歴運用」

### 言葉・語彙

- **AI ネイティブ経営**（カテゴリ宣言用語）
- **AI 主権**（自己主権の延長語彙）
- **L3 領域**（対内戦略言語・対外では「AI に代替されない領域」に翻訳）
- **学者モード化**（避けるべき AI ブレストの希薄化症状）
- **主軸先行**（AI に投げる前のプロトコル）
- **「抜く AI 活用」**（「足す AI」との対比）
- **記憶層 / OS 層 / プロダクト層**（3階層アーキテクチャ）
- **895 タスク・84% 削減**（権威構築の数値・260427 時点）
- **自社ドッグフード**（GrowthFix 自身が最大の事例）
- **ハーネスエンジニアリング**（260429 統合フレーム・対外発信可）
- **コア／ハーネス／実行エージェント**（3層構造）
- **TDD 経営**（テスト駆動経営・あるべき状態を事前定義）
- **クローズドループ**（ハーネス自己更新ループ・対内）
- **トークンあたり利益**（経営指標）
- **「組織を最小化して引力を最大化する」**（AIネイティブ組織の翻訳語）
- **サブエージェント分離**（260503・モデル経済 × ハーネス装置内蔵の実装パターン）
- **実行エージェント物理ファイル化**（260503・3 層構造 [3] の `~/.claude/agents/*.md` 実装）
- **lp-implementer / script-writer**（GrowthFix サブエージェント名・対内用語）

### 危険信号（運用時のセルフチェック）

AI 活用で個性が希薄化していないか：

- [ ] AI に「最初にブレストして」と投げている → 主軸先行に切り替え
- [ ] 「3 つの原則」「4 パターン」がきれいに並んでいる → 学者モード化警戒
- [ ] 出力に偏愛・極論・否定形が入っていない → 「Gravity 思想が滲んでいるか」で判定
- [ ] 自社で出来ないものをクライアントに売ろうとしている → 自社ドッグフード違反
- [ ] AI で「足している」だけ → 「抜く」観点で再設計

ハーネス品質のセルフチェック（260429 追加）：

- [ ] ハーネス（実行ルール）とコンテクスト（参照情報）が混在していないか → MD内で分離する
- [ ] 「良いアウトプット定義」が事前に書かれているか → 書かれていなければハーネス未成立
- [ ] 失敗パターンが `feedback_*` メモリに蓄積されているか → 蓄積なし＝ループが回っていない
- [ ] ハーネス通りに動かすのが人間でなくAIで実装可能になっているか → 人間依存はハーネス未完成
- [ ] ハーネスを書くこと自体が目的化していないか → 規定の塊化警戒・思想層の魅力が殺されていないか確認

---

### ★ 22-EH 8 AI エージェント MVP 全実装（260514 夜・3 並列 script-writer / 計 3,412 行）

> **起点：** 260514 夜 v3.0 命名再編（CU- → OT- 等）+ 8 本 MVP 実装決定 → 3 並列 script-writer agent（Sonnet）で同時実装完走
> **配置：** 本番運用スクリプト = `06_開発/scripts/orbit/` / `06_開発/scripts/recruit/` / `06_開発/scripts/cultivate/`
> **学習基盤：** v3.0 マンスリー施策レポート装置（Orbit）+ AI 武装人事業務（Recruit/Cultivate）の運用骨格 v0.1

#### 実装サマリー（8 エージェント / 9 ファイル / 3,412 行）

| カテゴリ | エージェント | ファイル | 行数 | 主機能 |
|:-:|---|---|:-:|---|
| **Orbit** | OT-1 既存タレマネデータ取得 | `orbit/orbit_data_fetcher.py` | 405 | Wevox / カオナビ mock + SmartHR CSV + 氏名 SHA-256 ハッシュ |
| Orbit | OT-2 論文 × AI 突合分析 | `orbit/orbit_paper_matcher.py` | 563 | 埋込論文 DB 15 本 × タレマネ → Claude API 施策生成・prompt caching |
| Orbit | OT-3 月次レポート自動生成 | `orbit/orbit_monthly_report_v3.py` | 903 | A4 5-7p PDF/MD（p.1-7 心理的契約 + 軸 15 個ゲート）|
| **Recruit** | RT-4 Bizreach 全件分析 | `recruit/recruit_bizreach_analyzer.py` | 206 | 業界 × 件名 × 本文長 クロス + Claude API 文面最適化 |
| Recruit | RT-5 週次採用 KPI レポート | `recruit/recruit_weekly_kpi.py` | 262 | ファネル 8 KPI + ベンチマーク Δ-15% ボトルネック自動検出 |
| **Cultivate** | CT-1 既存 SaaS データ統合エンジン（Vision Engine）| `cultivate/cultivate_vision_engine.py` | 282 | 経営者 Why/才能/偏愛 → 文化 3 層 + 8 類型 |
| Cultivate | CT-2 論文 × AI 介入提案エンジン（Values × Policy）| `cultivate/cultivate_values_policy.py` | 266 | バリュー 10 × ポリシー 50 自動生成 |
| Cultivate | CT-3 半期物語化エンジン（Manager Copilot）| `cultivate/cultivate_manager_copilot.py` | 362 | コンプレックス補完 + 4 マネジメント軸マトリクス |
| 共通基盤 | claude_client.py | `scripts/_common/claude_client.py` | 200 | Claude API / config / MD 整形 / mask（260514 _cultivate_common.py から昇格・recruit/orbit 共有化）|

**合計：3,412 行 / 9 ファイル**（8 エージェント + 1 共通モジュール）

#### --mask フラグ統一仕様（OT-1 + RT-4 共通実装パターン）

> **位置付け：** 個人情報マスキング（氏名 / 候補者 ID 等）の標準実装パターン。v3.0 以降の全 AI エージェントは本パターンに準拠。

```python
# argparse 標準実装（OT-1 / RT-4 採用）
parser.add_argument('--mask', action=argparse.BooleanOptionalAction, default=True,
                    help='個人情報マスキング有効化（default: True / --no-mask で素通し可）')
```

**実装ルール：**
- `default=True`（マスキング ON が安全側）/ `--no-mask` で明示的に解除可（デモ・検証時のみ）
- 氏名は **SHA-256 ハッシュの先頭 8 文字** + プレフィックス（"M-" 等）でユニーク ID 化
- mask 引数は全関数に propagation（`_mask_name` / `_mask_email` / `_parse_csv_members` / `fetch_from_csv` / `fetch_from_demo` / `fetch_from_wevox_mock` / `fetch_from_kaonavi_mock` 等 7+ 関数で一貫渡し）
- Cultivate 系 3 本（CT-1/2/3）は経営者層対象データのため既存 --mask 維持（opt-in 設計尊重）

**動作検証パターン：**
- ✅ OT-1：mask=True で "M-6b0e1c" / mask=False で "山田太郎" 素通し
- ✅ RT-4：60 件母数で業界別 9-20% 算出 + 候補者 ID マスキング切替
- ✅ デモデータ規模可変オプション（`--demo-size N`）で実運用前のサンプル検証可能

#### mock 連携基盤（既存タレマネ × 採用ツール）

| ツール | mock 実装 | 本番接続 |
|---|---|---|
| Wevox | `fetch_from_wevox_mock`（OT-1）| API 連携準備（v0.2 で本実装）|
| カオナビ | `fetch_from_kaonavi_mock`（OT-1）| API 連携準備（v0.2 で本実装）|
| SmartHR | CSV インポート（OT-1）| 既存 CSV エクスポート機能流用 |
| Bizreach | デモデータ 60 件（RT-4）| API 連携準備（v0.2 で本実装）|
| モチベクラウド | 設計済 / 未実装（OT-1 v0.2 候補）| - |

#### 9:1 二層分離原則の 8 MVP への適用（裏方 AI 9 × 表方経営者 9）

| エージェント | 裏方（AI 9 / 100x）| 表方（経営者 9 / 1x）|
|---|---|---|
| OT-1 データ取得 | タレマネ DB 自動取得 + SHA-256 ハッシュ化 + 個人別配列構造化 | 取得ソース選定 / マスキング ON/OFF 判断 |
| OT-2 論文突合 | 論文 DB 15 本マッチング + Claude API 個別施策案生成 | 施策案の採否決定 / クライアント文脈への翻訳 |
| OT-3 月次レポート | A4 5-7p PDF/MD 自動生成 | 経営者対面 60 分で本人の言葉で意思決定 |
| RT-4 Bizreach 分析 | 業界 × 件名 × 本文長 クロス分析 + 文面最適化提案 | スカウト送信判断 / 個別カスタマイズ |
| RT-5 週次 KPI | ファネル 8 KPI 集計 + ボトルネック自動検出 | 採用基準調整 / 人事責任者との戦略 MTG |
| CT-1〜3 | 文化 3 層 / バリュー 50 / マネージャー副操縦士の AI 草稿生成 | 経営者本人の言葉で言語化 / 文化定着判断 |

#### 学び・運用ルール（260514 確立）

1. **3 並列 script-writer Sonnet パターン**：大規模スクリプト群（8 ファイル / 3,412 行）を **1.5 時間で同時実装可能**。今後の MVP 一括実装の標準フロー
2. **--mask フラグ統一は OT-1 / RT-4 両方で同パターン採用**：v0.2 以降の全エージェントで同パターン踏襲（コピペ可能な argparse.BooleanOptionalAction）
3. **「scope crossover を防ぐ」=「実装ではなく報告で返す」原則**は 260503 lp-implementer 知見を継承（agent A/B/C が各カテゴリのみに集中）
4. **共通モジュール（scripts/_common/claude_client.py）の分離パターン**：Claude API 呼び出し + config 読込 + MD 整形 + mask 関数を 1 ファイルに集約 → Cultivate / Recruit / Orbit 系 8 ファイルの重複コード削減（260514 夜 `_cultivate_common.py` から昇格・5 ファイル合計 150+ 行削減・prompt caching 新形式 `cache_control: ephemeral` に統一）
5. **prompt caching の積極活用**：OT-2 で論文 DB 15 本 × タレマネを Claude API に渡す際、`cache_control: ephemeral` でコスト 60% 削減
6. **デモデータの母数戦略**：RT-4 で 20 件 → 60 件に拡充して業界別クロス分析の統計的安定性確保（1 件サンプル 100% の異常値解消）

#### 残実装ロードマップ（260514 → 2026 Q3）

| Phase | 期間 | 実装内容 |
|---|---|---|
| **v0.2**（5/15-5/31）| 2 週間 | RT-1/2/3/6 + OT-4/5/6 実装 + Wevox/Bizreach API 本連携 |
| **v0.3**（6/1-6/30）| 1 ヶ月 | CT-4/5/6 実装 + 1 件目顧客（Orbit 月 5 万）試験運用 |
| **v0.4**（7/1-9/30）| 3 ヶ月 | 全 18 本統合テスト + Mac mini ローカル運用基盤切替（22-DB 連動）|

#### 関連 SSOT

- 実装仕様：`04_GrowthFix/01_サービス設計/_Gravity_R/260514_GravityRecruit_標準サービス設計_v2.0.md` §2.2 + `_Gravity_C/260514_GravityCultivate_標準サービス設計_v2.0.md` §2.2 + `_Gravity_その他_Orbit_Coaching_ShiftS/260514_GravityOrbit_標準サービス設計_v3.0.md` §2.4
- v3.0 引き継ぎ書：`04_GrowthFix/01_サービス設計/_横断_フレーム_戦略/260514_3サービスv2.0_v3.0_確定要素+SSOT反映引き継ぎ書_v1.0.md`
- 実装 mtime 記録：`04_GrowthFix/04_デイリーログ/2605/2605_work_log.md` 第 19 ラウンド（22-EH）

---

### 改訂履歴

| バージョン | 日付 | 内容 |
|---|---|---|
| v260514 | 2026-05-14 | 22-EH 8 AI エージェント MVP 全実装（OT-1/2/3 + RT-4/5 + CT-1/2/3 + _cultivate_common.py・3,412 行）+ --mask フラグ統一仕様 + mock 連携基盤（Wevox/カオナビ/SmartHR/Bizreach）+ 9:1 二層分離原則の 8 MVP 適用 + 残実装ロードマップ v0.2-v0.4。260513 R7 の 12 エージェント命名（scout-analyzer 等）は v3.0 で RT/CT/OT 統一に再編・廃止注記済 |
| v260513 R7 | 2026-05-13 | 11 新規エージェント群セクション追加（260513 堀田セッション R7 反映・Phase B-3 で 7 本仕様 v0.1 完成 / 残 5 本は 22-CT/CU 予定）|
| v260507 | 2026-05-07 | AI.md Phase 9.1 分割により AI_自動化群.md として独立 |
