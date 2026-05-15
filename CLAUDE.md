# GrowthFix Vault — Claude 指示書

GrowthFix（石井伸幸・引力経営の会社）の Obsidian Vault。詳細プロファイル・プロジェクト状態・フィードバックは `memory/MEMORY.md` 経由で自動参照される。本ファイルは **Vault 全体に常時効く実行ルール**のみを記述する。

---

## 業務系タスク実行時：09_会社OS Part 3 を参照（260429 採用・260501 効率化）

各 MD の **Part 3 ハーネス層**には合格基準／NG 例／実行時テストが記載。**プロトコル：** タスク前に該当 Part 3 を Read → アウトプット → セルフチェック報告。

### Part 3 マッピング（タスク種別 → 参照 MD）

| タスク | Part 3 参照（パスは `09_会社OS/...` 配下）|
|---|---|
| Note／FB／WP／対外コピー | culture.md ＋ 発信.md ＋ **接続装置.md** |
| LP／コーポレート HTML | design.md ＋ **接続装置.md** |
| 営業・商談・見積 | 営業.md ＋ 商品.md |
| 採用・業務委託 | 採用.md |
| 顧客対応・コーチング | カスタマー.md |
| AI 生成物全般 | AI.md |
| 投資・大型支出・撤退判断 | 判断基準.md ＋ 社長.md |
| 翻訳の出力 | 翻訳.md |
| 接続装置整備 | **接続装置.md** Part 1-3 |

### 設計フレーム参照（堀田フレーム・260502 確立）

対外発信物・LP・セミナー設計・サービス設計などの **設計タスク**では、Part 3（ハーネス層）に加えて **堀田フレームワーク体系（42 選・260514 第 11 セッション反映版）** を必須参照する：

- **本体**：`02_セッション記録/堀田さんコーチング/260429_堀田フレームワーク体系_最新版.md`（260514 第 11 セッション反映で 42 選に拡張）
- **メモリポインタ**：`memory/reference_horita_framework.md`

| タスク | 堀田フレーム参照 |
|---|---|
| Note／FB／WP／対外コピー | **必須** |
| LP／コーポレート HTML | **必須** |
| セミナータイトル／セッション設計 | **必須** |
| 営業トーク・商談スクリプト | 推奨 |
| trivial 修正（誤字・1 行差し替え等）| 不要 |

**位置づけ**：堀田フレームは「設計レイヤーの SSOT」。`SSOT_用語と定義.md`（語彙レイヤーの SSOT）とは別軸で運用。`lint_consistency.sh` の対象外（語彙ではないため機械チェック不可）。**更新時は本体ファイルを単一の更新点として扱い、reference_horita_framework.md の項目数も同期更新**。

### Read 効率化ルール（260501 確立・260512 Phase 9 完走後改訂）

> **260512 Phase 9 完走後の状態**：09_会社OS 全 MD が思想層 300 行 / 機能系 500 行ルール通過済（lint §9 警告ゼロ）。全文 Read してもトークン肥大化は限定的だが、**子 MD 階層を踏まえた段階 Read** で更に効率化可能。

1. **ピンポイント Read**：Part 3 のみ必要な時は `Read offset=<Part3行> limit=<必要行数>` で読む。**Phase 9 完走後の各 MD サイズ**：思想層 235-298 行 / 機能系 295-499 行（全件 500 以下）。それでも Part 3 が末尾にある MD（商品.md / 営業.md / 判断基準.md 等）はピンポイント Read 推奨
2. **子 MD 階層 Read（260512 Phase 9 完走で確立）**：親 MD → 詳細が必要な時のみ子 MD → 孫 MD（Phase 反映系のみ）。最初から子・孫を読まない
   - 例：商品設計タスク = 商品.md（親）のみ → 詳細が必要なら商品_5サービス詳細.md（子・260515 8 ページピボット後は履歴ファイル化・現役 SSOT は商品.md）→ 論文反映の細部が必要なら 商品_5サービス_論文反映_Phase{8_9, 10_10軸補完}.md（孫）
   - 階層構造マップ：`09_会社OS/00_README.md` §「親 ↔ 子 ↔ 孫 構造マップ」
3. **_素材ストック は履歴参照時のみ Read**：通常運用では参照不要。`09_会社OS/_素材ストック/` 配下（商品_進化記録 / 営業_260512反映_HACHI操電_スイートスポット）は将来復活可能性のための温存・現役 SSOT は親 MD 側にある
4. **同セッション再 Read 不要**：1 セッション内で同 MD の Part 3 を一度読んだら、追加の業務タスクで再 Read しない（context に既存）
5. **trivial 免除**：以下は Part 3 Read 免除
   - 誤字・変数名・スペル修正
   - 単純な 1 行差し替え（思想に触れない）
   - 機械的な lint 修正・SSOT 用語置換
   - 既存ファイルのフォーマット整形のみ
6. **疑わしきは読む**：「軽微っぽいが思想・対外発信に影響しそう」と感じた時は Read する（省略癖はハーネスを腐らせる）

### 業務系タスクの認識基準（Read 必要）

- 対外発信物の作成・編集（思想変更を伴う）
- 営業・商談・見積・契約・適合判定
- 採用・業務委託・顧客対応
- 投資・大型支出・撤退・新サービス検討
- サービスの設計・改訂（260515 8 ページピボット後：「組織の引力設計プログラム」1 商品 + 個人軸 2 サービス・旧 5 サービス並列構造は内部参考値として温存）

### 補助フレーム

- **ハーネスエンジニアリング 3 層**（コア／ハーネス／実行エージェント）：詳細は `harness.md`（260501 分離）／ `memory/project_harness_engineering_260429.md`
- **思想層 2 サブ層**：経営思想（会社／Why／引力／参謀）＋接続装置。詳細：`09_会社OS/00_README.md`
- **5 層モデル**（接続装置）：内的コンセプト直接打ち禁則／外的で集めて内的で磁化。詳細：`接続装置.md` Part 1

---

## SSOT 整合（LP / コピー / 提案書 / 見積書）

- **語彙レイヤー SSOT**：`05_プロダクト/_共通/SSOT_用語と定義.md`（260515 8 ページピボット後：「組織の引力設計プログラム」+ 個人軸 2・参謀名・期間・3 要素。価格は内部参考値として温存）
- **設計レイヤー SSOT**：堀田フレームワーク体系（35 選・最新版）→ 上記「設計フレーム参照」セクション
- 編集後の検証：`bash 06_開発/scripts/lint/lint_consistency.sh` を実行（語彙レイヤーのみ機械チェック対象）

## LP 編集時の自動機械チェック

`05_プロダクト/` 配下 HTML を編集したら、**ユーザーに言われなくても以下を実行する**：
- `python3 06_開発/scripts/audit/audit_mobile_sync.py`
- 必要に応じて `bash 06_開発/scripts/deploy/verify_deployment.sh`（デプロイ後）

詳細：`memory/feedback_lp_mobile_audit_required.md` ／ `memory/reference_audit_mobile_sync_workflow.md`

## FTP デプロイ運用ルール（260515 確立・WP 事故 4 連発の構造防止）

**個別 curl による FTP upload は原則禁止**。本番への FTP upload は `bash 06_開発/scripts/deploy/deploy.sh [shared|lp|diagnose|wp|optin|all]` 経由のみ使用する。

### 理由

過去 4 件の WP 関連事故（260425 / 260507 / 260511 / 260515）は、いずれも **「ローカルパス → 本番 URL」のマッピング誤判定** が直接原因。個別 curl は SSOT 照合をバイパスするため事故を量産する。`deploy.sh upload()` 関数内に Layer 4 ガードを実装済（危険な local→remote 組み合わせは BLOCK）。

### 主要 SSOT マッピング（不可侵）

| URL | ローカル | 内容 |
|---|---|---|
| `/whitepaper/` | `05_プロダクト/コーポレート/whitepaper_optin_本番/index.html` | **オプトイン LP**（メール入力 → PDF DL）|
| `/whitepaper-read/` | `05_プロダクト/Gravity/WhitePaper/V9/index.html` | **WP V9 本体**（PDF 生成元）|
| `/whitepaper.pdf` | `05_プロダクト/Gravity/WhitePaper/V9/gravity-whitepaper-v9.pdf` | PDF 本体 |
| `/gravity/coaching/` | `05_プロダクト/Gravity/Coaching/LP/index.html` | 260515 8 ページピボット後：旧 `/gravity-coaching/` から物理移動済 |
| `/gravity/code/` | `05_プロダクト/Gravity/Code/LP/index.html` | 260515 物理移動済（旧 `/gravity-code/`）|
| `/gravity/` | `05_プロダクト/Gravity/_ブランド/LP/index.html` | **法人メイン LP**（組織の引力設計プログラム・260515 1 枚化）|

詳細マッピング：`memory/feedback_lp_deployment_path_ssot_check.md` ／ `memory/feedback_wp_v9_v10_deploy_path_distinction_260515.md` ／ `memory/reference_whitepaper_url_structure.md`

### deploy.sh の Layer 4 ガード（260515 実装）

以下の組み合わせは upload() 関数で自動 BLOCK：
1. **WP V9 本体 → /whitepaper/**：オプトイン LP 破壊（過去 3 回事故）
2. **WP V10（草案）→ 本番**：未完成版公開（隔離済 → `04_GrowthFix/02_マーケティング/_WP_V10_草案_本番未投入/`）
3. **オプトイン LP → /whitepaper-read/**：WP 本体上書き
4. **`_archive` / `_history` / `_素材ストック` / `_草案_本番未投入` / `_DRAFT_DO_NOT_DEPLOY` 配下 → 本番**：意図しない過去版公開

### deploy.sh 自動 verify 連鎖（260515 実装）

`bash deploy.sh [...]` 実行時、最後に `verify_deployment.sh` が自動実行され、本番健全性を検証（オプトイン特徴語必須・WP 本体特徴語必須・PDF 200 OK・mobile.css バージョン整合 等）。FAIL 時は exit 2 で即停止。`SKIP_VERIFY=1` で抑制可能（非常時のみ）。

### 例外的に個別 curl が必要な場合

deploy.sh が未対応のファイル（profile / knowledge / academy-wl / sample-report / seminar-acting 等）への upload は、以下を必ず実施：

1. memory `feedback_wp_v9_v10_deploy_path_distinction_260515.md` の URL マッピング表を Read
2. ローカルパスとリモートパスをユーザーに共有して確認
3. upload 後に `bash 06_開発/scripts/deploy/verify_deployment.sh` を手動実行
4. 本番 grep で意図したコンテンツが反映されているか確認

将来的には deploy.sh に対応関数を追加して個別 curl を排除するのが望ましい。

## 「変わっていない／おかしい」報告時の原則

ビジュアル系不具合の報告は、**仮説修正を走らせる前にスクショを依頼する**。仕様認識違いと実装違いを区別するため。詳細：`memory/feedback_screenshot_first_before_fix.md`

---

## トークン経済（経営指標）

AI 費用は経営戦略指標として扱う。月次 retail 換算コストは `06_開発/scripts/daily/token_usage.py` で集計。`/daily` skill が STEP 4.7 で自動取得する。詳細：`memory/reference_token_usage_script.md`

## 主要原則（Vault 全体）

- **主軸先行**：AI に「ブレストして」と先に投げない。主軸 → AI 相談 → 検証 の順序（`memory/feedback_ai_brainstorm_individuality.md`）
- **時間制約タスク**：目的 1 行 → 問い 3-5 / 決定 3-5 / 指標 3-5 で止める。網羅報告は禁則（`memory/feedback_session_purpose_first.md`）
- **Skill 実行後は Diff 提示**：iran-update / daily 等は前日との差分箇条書きを必ず出す（`memory/feedback_post_skill_diff_summary.md`）
- **モデル選択**：戦略判断・壁打ちは Opus、レポート生成・実装は Sonnet（`memory/feedback_model_selection_sonnet.md`）

---

## 260513 Phase 1-3 フォルダ整理（全完走・適用済）

### Phase 1（260513・即時整理）
- **03_コンテンツ**：直下40本ベタ置き → サブフォルダ化（`_連載管理/` `連載_Vol0-14/` `連載_卒業生シリーズS1-S8/` `_素材ストック/` `_archive/`）。詳細：`03_コンテンツ/_README.md`
- **04_GrowthFix/03_採用**：新設（求人設計 / 面接プロセス / オファー設計 / 採用_横断知見 / Shift_R_Week1-2納品物）。詳細：`04_GrowthFix/03_採用/_README.md`
- **01_石井伸幸**：親版本 = `260514_最新統合プロファイル_v3.0反映_18日間進化版.md`（260514 切替・260427 親版本は §7 のみ v3.0 更新で歴史記録化）。詳細：`01_石井伸幸/_README.md`
- **_shared 廃止**：`question_block_styles.php` を `05_プロダクト/_共通/` に統合（deploy.sh 同期更新済）
- **08_情報収集 56M→4M**：青木聡 VTT 原本（42M）・Tier2 VTT（9.9M）・260501 Shift検証素材（152K）削除。クリーン版とフレーム集約 SSOT は温存

### Phase 2（260513・中規模整理）
- **04_デイリーログ 月別分割**：直下62本ベタ置き → `2603/`（13本）`2604/`（28本）`2605/`（21本）の月別フォルダ化。**ファイルパス：`04_デイリーログ/YYMM/YYMMDD_daily.md`**（YYMM = YYMMDD の最初4文字）。daily / weekly-close / hotta-prep / work-log / sync-knowledge skill のパス参照と `meta_ads_daily.py` の `get_daily_log_path()` 更新済。詳細：`04_GrowthFix/04_デイリーログ/_README.md`
- **01_サービス設計 テーマ別分類**：直下119本 → 11テーマ別フォルダ化（_Gravity_R / _Gravity_C / _Gravity_診断_CODE_Scan / _Gravity_その他_Orbit_Coaching_ShiftS / _書籍_WhitePaper / _Phase論文反映 / _外部分析_対談 / _セミナー_WS_モニター / _横断_フレーム_戦略 / _堀田壁打ち）。詳細：`04_GrowthFix/01_サービス設計/_README.md`
- **06_開発/scripts/ 軽量サブフォルダ化**：`config/`（4本）`converters/`（2本）`extractors/`（3本）新設・5スクリプトの CONFIG_PATH 更新・`.gitignore` 更新。詳細：`06_開発/scripts/_README.md`

### Phase 3（260513・高リスク整理 全完走）
- **05_プロダクト 親子2階層化**：ルート28フォルダ平置き → `Gravity/`（10本）+ `コーポレート/`（12本）+ `assets_banners/`（旧 banners_本番）+ 既存インフラ系。**本番URLは変更なし**（ローカルパスのみ）。GravityBlueprint 幽霊フォルダ問題（260430 廃止済）も deploy.sh から完全削除。詳細：`05_プロダクト/_README.md`
- **06_開発/scripts/ 完全カテゴリ化**：軽量3サブフォルダ → 14サブフォルダ（audit/lint/deploy/orbit/daily/note/gravity/lp/util + 既存 config/converters/extractors/hooks）。**ファイルパス例：`06_開発/scripts/lint/lint_consistency.sh`, `06_開発/scripts/audit/audit_mobile_sync.py`, `06_開発/scripts/daily/token_usage.py`**。post_lp_edit_audit.sh hook + CLAUDE.md 4箇所 + 5 skill のパス参照を一括更新。
- **04_GrowthFix/00_営業 サブフォルダ化**：直下27本 → 6テーマ別（_Sushitech/_Scan商談/_Gravity営業基盤/_Coaching営業/_業務委託営業/_営業プレイブック）。詳細：`04_GrowthFix/00_営業/_README.md`
- **02_セッション記録 クライアント別分離**：直下32本 → 堀田18本+クライアント別（長島寛12+長谷2）+横断分析2本。詳細：`02_セッション記録/_README.md`
- **06_開発 直下 MD 6本**：旧セッション引継ぎ・MVP仕様書 → `04_GrowthFix/02_マーケティング/_archive/06_開発_由来_旧引継ぎ/`
