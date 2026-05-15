# 8 ページピボット SSOT 反映 引き継ぎ書 v1.0（260515）

> **目的**：260515 確定の「25 LP → 8 ページピボット」を SSOT / 09_会社OS / memory / lint に網羅的に反映する。本書は別エージェント（別 Node）で実行可能な自己完結ドキュメントとして設計されている。
>
> **本書ステータス**：v1.0 ドラフト・調査完了。実装は別エージェントが §7 のプロンプトで実行可能。
>
> **基盤資料**：
> - 仕様書：`04_GrowthFix/02_マーケティング/260515_8pages_pivot_v1.0_仕様書.md`
> - 段階 1 完了記録：`memory/project_8pages_pivot_implementation_260515.md`
> - PeopleX 調査：`08_情報収集/260515_PeopleX_網羅調査_v1.0.md`

---

## §0. 目的・背景

### 0.1 8 ページピボットとは（260515 確定）

GrowthFix が PeopleX 網羅調査 + 堀田 hajime.institute 分析を経て決断した、構造的な事業整理：

1. **法人 5 サービス並列 → 統合プログラム 1 + 個人軸 2 へ集約**
   - 旧：Shift R（採用・月 35 万）/ Cultivate（躍動・月 50 万）/ Orbit（留まる・月 5 万）/ Coaching（38 万）/ CODE（5 万）の 5 サービス並列展開
   - 新：「**組織の引力設計プログラム**」1 商品（集まる × 躍動 × 留まる 統合）+ **Gravity CODE**（個人軸）+ **Gravity Coaching**（個人軸）の 2 階層構造

2. **LP 料金完全非公開化**（堀田流・問い合わせベース）
   - LP 側：料金記述ゼロ（「ご相談ください」型）
   - 社内資料（SSOT / 09_会社OS / 営業提案書 / プレイブック）：**内部参考値**として温存

3. **公開 LP を 25 本 → 8 ページに圧縮**
   ```
   /                       TOP
   /profile/              代表プロフィール
   /achievement/          実績
   /knowledge/            ナレッジ
   /news/                 お知らせ
   /gravity/              組織の引力設計（法人メイン・1 枚化）
   /gravity/code/         CODE（個人軸サブページ）
   /gravity/coaching/     Coaching（個人軸サブページ）
   ```
   + リード獲得：`/whitepaper/` `/whitepaper-read/`
   + 補助残置：`/gravity/diagnose/`（無料 Web 診断 UI）/ `/gravity-citations/`（学術引用 LP）

4. **301 リダイレクト稼働中**（260515 .htaccess 配置済）
   - /gravity-recruit/ /gravity-cultivate/ /gravity-orbit/ /gravity-shift/ /gravity-scan/ /gravity-code/ /gravity-coaching/ /gravity-scan/web-diagnose/ /academy-wl/ → 全て /gravity/ 系へ転送済

5. **4 型修飾語追加**（260515 確定）
   - CODE 個人 4 型：「個人整合型 / 個人想いズレ型 / 個人強みズレ型 / 個人偏愛ズレ型」
   - 無料 Web 診断 組織 4 型：「組織整合型 / 組織拡散型 / 組織渇望型 / 組織不毛型」

### 0.2 段階 1-3 で既に完了している項目

- /gravity/ LP v2.0 微修正完了（料金完全削除・3 サービスカード統合・FAQ 削除・trinity-grid 削除・学術背景リッチ化・自己紹介 2/3 短縮・3 軸よだれブロック追加・Gravity マップ Scan 4 型化・診断 iframe 埋め込み）
- 8 LP 物理移動完了（CODE / Coaching / 無料 Web 診断）
- 301 リダイレクト 9 件配置済（.htaccess）
- SSOT 2 ファイルにピボット注記追加済（`05_プロダクト/_共通/SSOT_用語と定義.md` line 14・`09_会社OS/公開/ガイドライン/商品.md` line 12）
- memory トップに新項目追加 + 本番 LP マッピング更新
- 新規 project memory：`project_8pages_pivot_implementation_260515.md`
- deploy.sh 改修（並列度制限 5 + 自動リトライ・死蔵参照削除）

### 0.3 本書で扱う未完了タスク

- **方針 A 完全置換**：対外発信 LP 経由ファイル（料金・旧 URL を新構造に置換）
- **方針 B 注記追加**：内部 SSOT / 09_会社OS / プレイブック（料金温存・トップ注記）
- **方針 C 温存**：日付付き設計史・WP V10 草案・過去 Phase 記録（変更不要）
- lint_consistency.sh / lint_lp_internal_terms.py のルール追加
- memory MEMORY.md / 個別 memory（旧 5/6 サービス記載）の整合化
- CLAUDE.md の Read 効率化ルール・本番 LP マッピング更新
- 4 型修飾語の SSOT 反映（`05_プロダクト/_共通/SSOT_対話設計_CODE_SCAN.md` 等）

---

## §1. 8 ページピボット 確定事項サマリ

### 1.1 確定意思決定（260515 9 項目）

| # | 論点 | 決定 |
|---|---|---|
| 1 | URL 設計 | A 案：CODE / Coaching を `/gravity/` 配下に統合 |
| 2 | WhitePaper LP | 残置（リード獲得装置）|
| 3 | TOP メッセージ | 「組織に、引力を。」継続 |
| 4 | サービス料金 LP 表記 | **完全非公開化**（堀田流・問い合わせベース・内部参考値は温存）|
| 5 | 個人サブスク 3 階級 | 見送り（2027 年以降の伏線）|
| 6 | 営業資料 HTML 編集権限 | 石井のみ |
| 7 | Gravity マップ 4 象限 | Scan 4 型（整合 / 拡散 / 渇望 / 不毛）に変換 |
| 8 | FAQ 処遇 | 全削除（堀田流・シンプル化）|
| 9 | trinity-grid（AI × 内省 × 引力翻訳）| 削除 |

### 1.2 完了済（段階 1）

- /gravity/ LP v2.0 完成・本番反映
- 301 リダイレクト 5 件配置（旧 LP → /gravity/）
- SSOT 2 ファイルにピボット注記追加
- /gravity/code/ /gravity/coaching/ /gravity/diagnose/ 物理ファイル作成
- deploy.sh 改修

### 1.3 完了済（段階 2-3）

- 4 型修飾語 LP 反映（CODE 個人軸 / 無料 Web 診断 組織軸）
- 個人軸 LP（CODE / Coaching）の料金記述・他 LP リンク削除
- 301 .htaccess 9 件配置（追加 4 件）

### 1.4 未完了（本タスクで実施）

- SSOT 本文の料金温存 + 注記方式適用（17 ファイル）
- 09_会社OS Part 3 / 思想層の旧 URL・料金記述整理（20 ファイル）
- memory 個別ファイルの旧構造記述更新（5+ ファイル）
- lint_consistency.sh / lint_lp_internal_terms.py 拡張
- CLAUDE.md の Read 効率化ルール / 本番 LP マッピング更新

---

## §2. 影響範囲調査結果

> **調査方法**：全件 grep（除外＝`_archive` `_history` `_素材ストック` 配下）。
> **集計範囲**：09_会社OS / 04_GrowthFix（00_営業 / 01_サービス設計 / 02_マーケティング / 04_デイリーログ）/ 05_プロダクト/_共通 / memory / CLAUDE.md / lint。

### §2.1 料金記述の残存（パターン 1：「月 35 万」「月 50 万」「月 5 万」「月 85 万」「38 万」「5 万円」）

**総ヒット件数**：1,043 件（09=113 / 04=786 / memory=74 / SSOT 用語=70）
**影響ファイル数**：約 165 件

#### §2.1.1 09_会社OS（20 ファイル / 113 件）

| ファイル | 件数 | 該当行（先頭 3-5 件）|
|---|---|---|
| `09_会社OS/公開/ガイドライン/商品_5サービス詳細.md` | 11 | L184 集まる月 35 万・L195 月 35 万円・L315 月 25 万 6 ヶ月総額 150 万・L477 月 15 万 → 月 5 万・L527 38 万 6 ヶ月 |
| `09_会社OS/公開/ガイドライン/商品.md` | 約 25 | L36 38 万 6 ヶ月一括・L55 38 万・L56 集まる 月 35 万・L57 躍動 月 50 万・L58 留まる 月 5 万・L107-109 価格根拠 |
| `09_会社OS/非公開/ガイド/カスタマー.md` | 10 | （Coaching 38 万 / R 月 35 万 / C 月 50 万 / Orbit 月 5 万 多数）|
| `09_会社OS/非公開/機能/営業.md` | 6 | （価格根拠・反論処理・パッケージ）|
| `09_会社OS/非公開/機能/採用.md` | 4 | （業務委託採用根拠：人件費 vs 月 35 万）|
| `09_会社OS/非公開/経営層/社長.md` | 2 | （CF 試算・LTV）|
| `09_会社OS/公開/経営思想/接続装置.md` | 3 | L94 月 5 万 × 2 ヶ月・L151 Orbit v3.2 月 5 万・L161 月 5 万 × 2 ヶ月 = 10 万 |
| `09_会社OS/公開/経営思想/会社.md` | 1 | L118 Coaching 38 万 |
| `09_会社OS/公開/経営思想/引力.md` | 1 | （Coaching 38 万）|
| `09_会社OS/公開/発信・AI/発信.md` | 1 | L266 Gravity Code 5 万 / Coaching 38 万 |
| `09_会社OS/公開/発信・AI/発信_チャネル別運用.md` | 多数 | （Vol.2 案内・Note 文例）|
| `09_会社OS/公開/発信・AI/AI_自動化群.md` | 数件 | （RT/CT/OT 月 35/50/5 万）|
| `09_会社OS/公開/発信・AI/発信_学術濃度ルール.md` | 数件 |  |
| `09_会社OS/公開/ガイドライン/design.md` | 2 | L368 Orbit 月 5 万・L369 Orbit 月 5 万 v3.2 |
| `09_会社OS/公開/ガイドライン/商品_5サービス_論文反映_Phase8_Phase9.md` | 1 |  |
| `09_会社OS/公開/ガイドライン/商品_5サービス_論文反映_Phase10_10軸補完.md` | 1 |  |
| `09_会社OS/公開/文化/判断基準_運用レイヤー.md` | 2 |  |
| `09_会社OS/00_README.md` | 3 | L148 Coaching 38 万・L152 38 万 SSOT 例・L157 38 万・L237 月 15 万 → 月 5 万 |
| `09_会社OS/公開/経営思想/接続装置_実装パターン.md` | 数件 |  |

#### §2.1.2 04_GrowthFix（約 130 ファイル / 786 件）

膨大なため、ファイル群サマリーで提示（個別ファイルは §3 マトリクスで方針判定）：

| 配下 | 主要ファイル | 件数概算 |
|---|---|---|
| `00_営業/_営業プレイブック/` | 260512_営業プレイブック_v1.0.md（8 件）/ 260512_反論処理50問_v0.1.md / 260512_顧客事例V1_A社_匿名版_v0.1.md | 30+ |
| `00_営業/_Gravity営業基盤/` | 260514_22-BE_商談ログ運用フォーマット / 260514_22-BF_パイプライン管理装置 / 260514_P1_競合比較表 等 | 20+ |
| `00_営業/_Scan商談/` `_Sushitech/` | FAQ 想定問答集 / 核心の1枚 等 | 10+ |
| `01_サービス設計/_Gravity_R/` | 260514_GravityRecruit_標準サービス設計_v2.0.md / v2.0_叩き台 | 20+ |
| `01_サービス設計/_Gravity_C/` | 260515_GravityCultivate_標準サービス設計_v3.0.md / v2.0_叩き台 | 20+ |
| `01_サービス設計/_Gravity_その他_Orbit_Coaching_ShiftS/` | 260514_GravityOrbit_標準サービス設計_v3.0.md / 260513_R9_プロコーチ束ね運用設計 | 30+ |
| `01_サービス設計/_横断_フレーム_戦略/` | 260514_3サービスv2.0_v3.0_確定要素+SSOT反映引き継ぎ書_v1.0.md / 260515_R_v2.1.4_Cultivate_v3.0_Orbit_v3.2_全反映漏れ調査_引き継ぎ書_v1.0.md 等 | 50+ |
| `01_サービス設計/_書籍_WhitePaper/` | WP V10 v0.5-v0.7 / 書籍_引力経営_第6-12章 / 終章 / 付録A-D | 80+ |
| `01_サービス設計/_DMM資産_AI武装連携/` | 統合業務マスター v1.0 / v2.0 / Phase5 ミナジン引き継ぎ書 v3.0 | 30+ |
| `01_サービス設計/_Phase論文反映/` | 260514_3軸マッピング棚卸しレポート_v0.1.md 等 | 10+ |
| `01_サービス設計/_セミナー_WS_モニター/` | 260508_Gravity_モニター標準フロー_SOP_v1.0.md 等 | 10+ |
| `01_サービス設計/_堀田壁打ち/` `_外部分析_対談/` | 260429_堀田ディスカッション / 260417_RECODE33本_Gravity活用統合分析 等 | 30+ |
| `02_マーケティング/` | 260514_営業資料_v0.4（50 件）/ 260512_GravityRC_営業提案_サービス資料_v1.0（18 件）/ 260507_プライシング戦略_SSOT_v0.2（12 件）/ 260511_競合分析_v1.0 / 260511_セミナーリブランディング素材 等 | 200+ |
| `02_マーケティング/競合分析/` | 識学 / リーダーの仮面 / 数値化の鬼 等 | 20+ |
| `02_マーケティング/_WP_V10_草案_本番未投入/` | WP V10 PhaseB ch01/ch05/ch08/エピローグ / 第6章 v0.2 | 20+ |
| `04_デイリーログ/2603-2605/` | 26 日次 + 月次 work_log | 100+ |

#### §2.1.3 memory（27 ファイル / 74 件）

| ファイル | 件数 | 該当行サンプル |
|---|---|---|
| `memory/MEMORY.md` | 7 | L29 月 50 万 / 月 5 万・L33 月 35 万 / 月 50 万 / 月 5 万・L117 Shift R 月35万 / Shift C 月50万 / Coaching 38万 / Orbit 月5万 |
| `memory/project_3services_v2_v3_definition_260514.md` | 7 |  |
| `memory/project_cultivate_v3.0_definition_260515.md` | 6 |  |
| `memory/project_orbit_direct.md` | 4 |  |
| `memory/project_strategy_lock_260430.md` | 1 |  |
| `memory/project_hachi_field_validation_260511.md` | 数件 |  |
| `memory/project_soden_field_validation_260512.md` | 数件 |  |
| `memory/feedback_lp_deployment_path_ssot_check.md` | 数件 |  |
| `memory/feedback_coaching_not_frontline_word.md` | 数件 |  |
| `memory/project_horita_14sessions_longitudinal_260428.md` | 数件 |  |
| `memory/project_growthfix_company_positioning.md` | 1-2 |  |
| `memory/project_phase6_research_260510.md` | 数件 |  |
| `memory/project_pending_meta_macmini_260514.md` | 1-2 |  |
| `memory/reference_recode_frameworks_consolidated.md` `reference_takagi_frameworks_consolidated.md` | 数件 |  |
| `memory/user_conviction_260418_executive_coaching.md` | 1-2 |  |
| `memory/project_scan_abolish_260514.md` | 数件 |  |
| `memory/user_financial_context.md` | 1-2 |  |
| `memory/project_shift_orbit_business_model.md` | 1-2 |  |
| `memory/_archive_*` | （調査対象外）|  |

#### §2.1.4 05_プロダクト/_共通 SSOT（7 ファイル / 79 件）

| ファイル | 件数 | 備考 |
|---|---|---|
| `SSOT_用語と定義.md` | 70 | **L14 で 8 ページピボット注記済**（料金は内部参考値として温存）|
| `SSOT_Gravity_3軸.md` | 4 |  |
| `SSOT_対話設計_CODE_SCAN.md` | 3 |  |
| `SSOT_Gravity_コア主張.md` | 2 |  |
| `SSOT_用語_JAFCO_HACHI_操電反映.md` | 2 |  |
| `SSOT_LPコピー言語ガイドライン.md` | 1 |  |
| `SSOT_Engagement指標定義.md` | 0 |  |

### §2.2 5 サービス並列構造（パターン 2：「5 サービス」「Recruit / Cultivate / Orbit」並列・「Shift R/C/Full」）

**影響ファイル数**：535 件（5サービス 171 + Shift R/C/Full 364）

主要ファイル（方針判定対象）：

| ファイル | 該当パターン |
|---|---|
| `CLAUDE.md` | L48「5 サービス詳細が必要なら商品_5サービス詳細.md」/ L65「5 サービスの設計・改訂」/ L77「（5 サービス・参謀名・価格・期間・3 要素）」 |
| `09_会社OS/00_README.md` | 商品 子 MD 階層マップで「商品_5サービス詳細」言及 |
| `09_会社OS/公開/ガイドライン/商品.md` | 多数（外的命名 vs 内的命名 二層運用 / Shift R / Shift C / Shift Full）|
| `09_会社OS/公開/ガイドライン/商品_5サービス詳細.md` | ファイル名自体が「5サービス」言及 |
| `09_会社OS/公開/ガイドライン/商品_5サービス_論文反映_Phase8_Phase9.md` | 同上 |
| `09_会社OS/公開/ガイドライン/商品_5サービス_論文反映_Phase10_10軸補完.md` | 同上 |
| `05_プロダクト/_共通/SSOT_用語と定義.md` | L14 注記内に「旧 5 サービス（Recruit / Cultivate / Orbit / Coaching / CODE）」/ B3-B5 行に Shift R/C 表記 |
| `memory/MEMORY.md` | L117「6 サービス相当（260514 SCAN 無料化 + Orbit v3.0 値下げ反映）」 |
| `04_GrowthFix/00_統合タスクマスター_v1.1.md` | 5 サービス並列記述 |

### §2.3 旧 LP URL 参照（パターン 3：`/gravity-{recruit/cultivate/orbit/shift/scan/code/coaching}/` `/academy-wl/`）

**影響ファイル数**：128 件（vault 内 101 + memory 27）

#### §2.3.1 09_会社OS / SSOT / CLAUDE.md（高優先）

| ファイル | 件数 | 該当行サンプル |
|---|---|---|
| `09_会社OS/公開/ガイドライン/design.md` | 11 | （URL 言及・LP マッピング表）|
| `09_会社OS/非公開/機能/営業.md` | 8 | （URL 共有テンプレ）|
| `09_会社OS/公開/ガイドライン/商品_5サービス詳細.md` | 6 |  |
| `09_会社OS/公開/ガイドライン/商品.md` | 5 |  |
| `09_会社OS/公開/発信・AI/発信.md` | 1 | L266 Gravity Code/Coaching 言及 |
| `CLAUDE.md` | 1 | L104「/gravity-coaching/」LP マッピング |
| `05_プロダクト/_共通/SSOT_用語と定義.md` | 多数 | L103-105 B3-B5 行で `/gravity-recruit/` `/gravity-cultivate/` `/gravity-orbit/` 表記（LP 再構成予定注記済）|

#### §2.3.2 memory（27 ファイル）

主要：MEMORY.md（4 件）/ project_3services_v2_v3_definition_260514.md / project_strategy_lock_260430.md / project_orbit_direct.md / project_scan_abolish_260514.md / project_hachi_field_validation_260511.md / project_soden_field_validation_260512.md / feedback_lp_deployment_path_ssot_check.md 等。

#### §2.3.3 04_GrowthFix（約 70 ファイル）

00_営業 / 01_サービス設計 / 02_マーケティング / 04_デイリーログ 全般。

### §2.4 4 型修飾語なし表記（パターン 4：「整合型」「拡散型」「渇望型」「不毛型」「想いズレ型」「強みズレ型」「偏愛ズレ型」が修飾語なしで残存）

**影響ファイル数**：153 件

#### §2.4.1 SSOT / 09_会社OS（高優先）

| ファイル | 該当パターン |
|---|---|
| `05_プロダクト/_共通/SSOT_用語と定義.md` | 4 型表記あり（修飾語なし）|
| `05_プロダクト/_共通/SSOT_Gravity_コア主張.md` | 同上 |
| `05_プロダクト/_共通/SSOT_Gravity_3軸.md` | 同上 |
| `05_プロダクト/_共通/SSOT_対話設計_CODE_SCAN.md` | 同上 |
| `05_プロダクト/_共通/SSOT_Engagement指標定義.md` | 同上 |
| `09_会社OS/公開/経営思想/引力.md` | L103「整合／想いズレ／強みズレ／偏愛ズレ」「整合／拡散／渇望／不毛」（CODE/Scan 文脈で区別記載済）|
| `09_会社OS/公開/ガイドライン/翻訳.md` | 同上 |
| `09_会社OS/公開/ガイドライン/商品.md` | L223 整合型・L224-226 想いズレ型 / 強みズレ型 / 偏愛ズレ型・L230 整合型 → Scan / 3 ズレ型 → Coaching・L480「CODE 4 型（整合型／想いズレ型／強みズレ型／偏愛ズレ型）／ Scan 4 型（整合／拡散／渇望／不毛）」 |
| `09_会社OS/公開/ガイドライン/商品_5サービス詳細.md` | 4 型関連 |

> **注意**：09_会社OS/引力.md L103 と 商品.md L480 は **「CODE 4 型 / Scan 4 型」と並列文脈で書かれており、混同リスクは低い**。修飾語追加は「個人」「組織」を冠する方針なので、文脈上両方が並ぶ箇所は **判定保留**（混在文脈なら明示推奨だが、対称性表現の場合は温存も可）。

---

## §3. 更新方針マトリクス

### §3.1 方針判定基準

| 方針 | 内容 | 適用基準 |
|---|---|---|
| **A. 完全置換** | 料金・旧 URL・5 サービス並列を新構造に全置換 | 対外発信物（LP / WP / Note / セミナー資料 / 公開コピー）|
| **B. 注記追加** | トップに「8 ページピボット注記」を追加し、本文の料金は **内部参考値**として温存 | 内部 SSOT / 09_会社OS（公開ガイドライン）/ 営業.md / 商品.md / 営業プレイブック / 提案書 |
| **C. 温存** | 変更不要 | 過去履歴・日付付き設計史・草案（_WP_V10_草案）/ デイリーログ / RECODE/高木フレーム集約 |

### §3.2 ファイル別判定マトリクス（主要 80 件・全 165 件中）

#### §3.2.1 方針 B（注記追加・本文温存）：内部 SSOT 系

| ファイル | 方針 | 理由 | 注記テンプレ |
|---|---|---|---|
| `05_プロダクト/_共通/SSOT_用語と定義.md` | **B**（注記済）| L14 で注記済・本文 70 件は内部参考値として温存運用中 | （既済）|
| `05_プロダクト/_共通/SSOT_Gravity_3軸.md` | **B** | 軸定義の社内 SSOT・LP は別 SSOT | トップ注記追加（§4 参照）|
| `05_プロダクト/_共通/SSOT_Gravity_コア主張.md` | **B** | 主張定義の社内 SSOT | トップ注記追加 |
| `05_プロダクト/_共通/SSOT_LPコピー言語ガイドライン.md` | **A** | LP コピー直接ガイド・LP 側は料金非公開 → ガイド側も非公開へ修正 | 「料金記述例」セクションを削除 or 「内部資料用」と明示 |
| `05_プロダクト/_共通/SSOT_用語_JAFCO_HACHI_操電反映.md` | **B** | フィールド検証履歴 + 用語反映 | トップ注記追加 |
| `05_プロダクト/_共通/SSOT_対話設計_CODE_SCAN.md` | **B（4 型修飾語追加）** | 4 型 SSOT・「個人」「組織」修飾語追加 | 注記＋本文修飾語追加 |
| `05_プロダクト/_共通/SSOT_Engagement指標定義.md` | **B**（軽）| 4 型言及あり・修飾語確認 | 必要に応じ注記 |

#### §3.2.2 方針 B（注記追加・本文温存）：09_会社OS

| ファイル | 方針 | 理由 |
|---|---|---|
| `09_会社OS/公開/ガイドライン/商品.md` | **B**（注記済）| L12 で注記済 |
| `09_会社OS/公開/ガイドライン/商品_5サービス詳細.md` | **B** | 内部参考値・ファイル名「5 サービス詳細」は履歴温存 |
| `09_会社OS/公開/ガイドライン/商品_5サービス_論文反映_Phase8_Phase9.md` | **B** | Phase 反映史・参考用 |
| `09_会社OS/公開/ガイドライン/商品_5サービス_論文反映_Phase10_10軸補完.md` | **B** | Phase 反映史・参考用 |
| `09_会社OS/公開/ガイドライン/design.md` | **B** | LP マッピング表に旧 URL 11 件・8 ページ構造に書き換え or 旧マッピングは履歴注記 |
| `09_会社OS/公開/ガイドライン/翻訳.md` | **B**（軽）| 4 型修飾語確認 |
| `09_会社OS/公開/経営思想/接続装置.md` | **B** | 月 5 万 × 2 ヶ月 = 10 万 等の経営思想表現・内部参考値温存 |
| `09_会社OS/公開/経営思想/接続装置_実装パターン.md` | **B** | 同上 |
| `09_会社OS/公開/経営思想/会社.md` | **B**（軽）| Coaching 38 万 1 件・思想層 |
| `09_会社OS/公開/経営思想/引力.md` | **B**（軽）| 4 型対称構造の説明（修飾語明示推奨）|
| `09_会社OS/公開/発信・AI/発信.md` | **B**（軽）| Vol.2 案内 1 件 |
| `09_会社OS/公開/発信・AI/発信_チャネル別運用.md` | **B** | Note 文例多数・内部参考値温存 |
| `09_会社OS/公開/発信・AI/発信_学術濃度ルール.md` | **B**（軽）|  |
| `09_会社OS/公開/発信・AI/AI_自動化群.md` | **B** | RT/CT/OT 月 35/50/5 万・内部運用基準 |
| `09_会社OS/公開/文化/判断基準_運用レイヤー.md` | **B**（軽）| 投資判断基準 |
| `09_会社OS/非公開/機能/営業.md` | **B** | 営業ガイド・内部運用 SSOT |
| `09_会社OS/非公開/機能/営業_運用詳細.md` | **B** | 同上 |
| `09_会社OS/非公開/機能/採用.md` | **B**（軽）| 業務委託採用根拠 |
| `09_会社OS/非公開/ガイド/カスタマー.md` | **B** | カスタマー対応 SSOT・10 件 |
| `09_会社OS/非公開/経営層/社長.md` | **B**（軽）| CF 試算 |
| `09_会社OS/00_README.md` | **B**（軽）| Coaching 38 万 SSOT 実例・教育用 |

#### §3.2.3 方針 A（完全置換）：対外発信物

| ファイル | 方針 | 理由 |
|---|---|---|
| `04_GrowthFix/02_マーケティング/260514_営業資料_v0.4_3サービスv2.0_v3.0統合_NotebookLM入稿版.md` | **A** | 営業資料（半対外）・新構造 1 プログラム + 個人軸 2 へ書き換え |
| `04_GrowthFix/02_マーケティング/260512_GravityRC_営業提案_サービス資料_v1.0.md` | **A** | 営業提案書・新構造へ |
| `04_GrowthFix/02_マーケティング/260512_無料30分相談装置_設計書_v1.0.md` | **A** | 相談動線設計 |
| `04_GrowthFix/02_マーケティング/260513_FB投稿候補_AI論文反映_v1.0.md` | **A** | FB 投稿候補 |
| `04_GrowthFix/02_マーケティング/260507_LP_SSOT整合チェック_引き継ぎ書_v1.0.md` | **A** | LP 整合チェック（25 LP 前提を 8 ページに）|
| `04_GrowthFix/02_マーケティング/260511_セミナーリブランディング素材_v1.0.md` | **A** | セミナー素材 |
| `04_GrowthFix/00_営業/_営業プレイブック/260512_営業プレイブック_v1.0.md` | **B**（注記）| プレイブック内は内部参考値・現場で参照 |
| `04_GrowthFix/00_営業/_営業プレイブック/260512_反論処理50問_v0.1.md` | **B**（注記）| 同上 |
| `04_GrowthFix/00_営業/_営業プレイブック/260512_顧客事例V1_A社_匿名版_v0.1.md` | **B**（注記）| 同上 |
| `04_GrowthFix/00_営業/_業務委託営業/260512_業務委託営業認定プロトコル_v0.1.md` | **B**（注記）| 業務委託向け教育資料・内部参考値温存 |
| `04_GrowthFix/00_営業/_Sushitech/260415_FAQ_想定問答集_Sushitech.md` `260420_FAQ_想定問答集_Sushitech_v2.md` | **A** | 対外 FAQ |
| `04_GrowthFix/02_マーケティング/260512_対談動画_打診メール草稿_v0.1.md` | **A** | 対外メール |
| `04_GrowthFix/02_マーケティング/260511_競合分析_v1.0.md` | **A** | 競合分析・新構造に |

#### §3.2.4 方針 A（完全置換）：戦略・サービス設計の現役 v0.1 系

| ファイル | 方針 | 理由 |
|---|---|---|
| `04_GrowthFix/01_サービス設計/_横断_フレーム_戦略/260514_3サービスv2.0_v3.0_確定要素+SSOT反映引き継ぎ書_v1.0.md` | **A**（または B+8ページ追記）| 旧 3 サービス並列前提の引き継ぎ書 → 8 ページピボット注記必須 |
| `04_GrowthFix/01_サービス設計/_横断_フレーム_戦略/260515_R_v2.1.4_Cultivate_v3.0_Orbit_v3.2_全反映漏れ調査_引き継ぎ書_v1.0.md` | **A** | 同上・260515 同日資料 |
| `04_GrowthFix/01_サービス設計/_横断_フレーム_戦略/260514_3軸完成設計書_v0.1.md` | **B** | 3 軸思想構造（軸定義は新構造でも維持）|
| `04_GrowthFix/01_サービス設計/_Gravity_R/260514_GravityRecruit_標準サービス設計_v2.0.md` | **B** | サービス内部仕様・営業資料参照元 |
| `04_GrowthFix/01_サービス設計/_Gravity_C/260515_GravityCultivate_標準サービス設計_v3.0.md` | **B** | 同上 |
| `04_GrowthFix/01_サービス設計/_Gravity_その他_Orbit_Coaching_ShiftS/260514_GravityOrbit_標準サービス設計_v3.0.md` | **B** | 同上 |
| `04_GrowthFix/02_マーケティング/260507_プライシング戦略_SSOT_v0.2.md` | **B** | 内部プライシング SSOT・参考値温存 |
| `04_GrowthFix/02_マーケティング/260507_メソッド体系_一元管理_v0.2.md` | **B** | 内部メソッド体系 |
| `04_GrowthFix/02_マーケティング/260507_競合分析_SSOT_v0.2.md` | **B** | 内部競合分析 |
| `04_GrowthFix/00_統合タスクマスター_v1.1.md` | **B**（注記）| タスクマスター（履歴含む）|
| `04_GrowthFix/00_W22-W26_週次実行プラン_v1.0.md` | **A** | 週次実行プラン（現役）|

#### §3.2.5 方針 C（温存）：日付付き設計史・草案

| ファイル | 方針 | 理由 |
|---|---|---|
| `04_GrowthFix/01_サービス設計/_書籍_WhitePaper/` 配下全般 | **C** | 書籍草案・WP V10 草案・付録 v0.x（草案前提・刊行時に一括更新）|
| `04_GrowthFix/02_マーケティング/_WP_V10_草案_本番未投入/` 配下全般 | **C** | 草案・本番未投入（隔離済）|
| `04_GrowthFix/02_マーケティング/競合分析/` 配下（識学 / 数値化の鬼 / 事業人 等）| **C** | 過去分析・履歴 |
| `04_GrowthFix/01_サービス設計/_外部分析_対談/` 配下（RECODE / 高木新平 等）| **C** | 過去分析・履歴 |
| `04_GrowthFix/01_サービス設計/_堀田壁打ち/` 配下 | **C** | 過去セッション記録 |
| `04_GrowthFix/04_デイリーログ/2603-2605/` 配下全般 | **C** | デイリーログ（履歴）|
| `04_GrowthFix/00_営業/_Scan商談/260415_核心の1枚_Scan分岐×Orbitストック_堀田4_15.md` | **C** | 4-15 堀田壁打ち履歴 |
| `04_GrowthFix/00_統合タスクマスター_完了履歴アーカイブ_260513.md` | **C** | 完了履歴 |
| `04_GrowthFix/01_サービス設計/_Phase論文反映/260514_3軸マッピング棚卸しレポート_v0.1.md` | **C** | Phase 棚卸し・履歴性 |
| `04_GrowthFix/01_サービス設計/_横断_フレーム_戦略/260513_サービスv2.0_仮説E_統合設計書_v0.1.md` | **C** | 仮説検討段階の設計書 |
| `04_GrowthFix/01_サービス設計/_DMM資産_AI武装連携/260514_統合業務マスター_v1.0.md` `v2.0_ミナジン拡張.md` | **C** | DMM 資産分析（履歴性）|
| `04_GrowthFix/01_サービス設計/260511_Gravity示唆抽出/` `260512_操電示唆抽出/` 配下 | **C** | フィールド検証履歴 |

#### §3.2.6 memory（個別判定）

| ファイル | 方針 | 理由 |
|---|---|---|
| `memory/MEMORY.md` | **A**（部分更新）| L117 「6 サービス相当」セクション + L103-104 本番 LP マッピング → 8 ページ構造へ更新 |
| `memory/project_3services_v2_v3_definition_260514.md` | **B**（注記）| 履歴 project memory・本文温存 + トップに 260515 ピボット注記 |
| `memory/project_cultivate_v3.0_definition_260515.md` | **B**（注記）| 同上 |
| `memory/project_strategy_lock_260430.md` | **B**（注記）| 戦略 SSOT memory・トップ注記で 8 ページピボット反映 |
| `memory/project_orbit_direct.md` | **B**（注記）| 設計履歴 |
| `memory/project_scan_abolish_260514.md` | **B**（注記）| 履歴 |
| `memory/project_hachi_field_validation_260511.md` | **C** | フィールド検証履歴 |
| `memory/project_soden_field_validation_260512.md` | **C** | 同上 |
| `memory/feedback_lp_deployment_path_ssot_check.md` | **A** | LP デプロイ運用 SSOT・現役・新構造へ更新 |
| `memory/feedback_coaching_not_frontline_word.md` | **B**（注記）| Coaching 売り言葉禁則の運用ルール |
| `memory/project_horita_14sessions_longitudinal_260428.md` | **C** | 縦断分析・履歴 |
| `memory/project_growthfix_company_positioning.md` | **B**（注記）| 会社定位 SSOT |
| `memory/project_phase6_research_260510.md` | **C** | Phase 履歴 |
| `memory/project_pending_meta_macmini_260514.md` | **C** | ペンディング履歴 |
| `memory/user_conviction_260418_executive_coaching.md` | **B**（軽・注記）| 覚悟日記録（思想層）|
| `memory/user_financial_context.md` | **A**（軽）| 財務状況更新（CF 試算が旧構造前提）|
| `memory/reference_recode_frameworks_consolidated.md` `reference_takagi_frameworks_consolidated.md` | **C** | フレーム集約（外部参照）|
| `memory/project_shift_orbit_business_model.md` | **C** | Shift Orbit ビジネスモデル履歴 |
| `memory/_archive/` `_archive_obsolete/` `_archive_260513_HRTeam_案検討/` 配下 | **C** | アーカイブ（変更不要）|

#### §3.2.7 CLAUDE.md（Vault ルート）

| 該当箇所 | 方針 | 修正内容 |
|---|---|---|
| L48「5 サービス詳細が必要なら商品_5サービス詳細.md」| **A** | 「商品_5サービス詳細.md（履歴）」と注記追加 or 「商品.md のみ（8 ページピボット後）」と書き換え |
| L65「5 サービスの設計・改訂」 | **A** | 「1 プログラム + 個人軸 2 サービスの設計・改訂」へ |
| L77「（5 サービス・参謀名・価格・期間・3 要素）」 | **A** | 「（1 プログラム + 個人軸 2 サービス・参謀名・期間・3 要素）」 |
| L104「/gravity-coaching/ → `05_プロダクト/Gravity/Coaching/LP/index.html`」| **A** | 段階 2 で物理移動済 → `/gravity/coaching/` へ更新 |

---

## §4. 実行プラン（優先順位付き）

### Step 1（即時実施）：方針 A・完全置換

#### Step 1.1 CLAUDE.md（Vault ルート）

```
旧：L48「5 サービス詳細が必要なら商品_5サービス詳細.md」
新：「5 サービス詳細が必要なら商品_5サービス詳細.md（260515 8 ページピボット後は履歴ファイル化・現役は商品.md のみ）」

旧：L65「5 サービスの設計・改訂」
新：「1 プログラム + 個人軸 2 サービスの設計・改訂」

旧：L77「（5 サービス・参謀名・価格・期間・3 要素）」
新：「（組織の引力設計プログラム + CODE + Coaching の用語/参謀名/期間/3 要素・料金は内部参考値）」

旧：L104「/gravity-coaching/ | 05_プロダクト/Gravity/Coaching/LP/index.html」
新：「/gravity/coaching/ | 05_プロダクト/Gravity/Coaching/LP/index.html（260515 物理移動済）」

追加（FTP デプロイ運用ルールセクション内）：旧 LP URL の SSOT マッピング表を「8 ページ構造」に更新
```

#### Step 1.2 memory/MEMORY.md

```
旧 L117「サービスラインナップ（260430 戦略 + 260514 SCAN 無料化）」
   「6 サービス相当（260514 SCAN 無料化 + Orbit v3.0 値下げ反映）」
新：「サービスラインナップ（260515 8 ページピボット確定）」
   「**LP 公開構造（260515）**：『組織の引力設計プログラム』1 商品（集まる × 躍動 × 留まる 統合）+ 個人軸 2（CODE / Coaching）。LP 側は料金完全非公開・社内資料に内部参考値温存。」
   「**内部参考値（旧 5 サービス）**：CODE 5万 / Scan 無料 / Recruit 月 35 万 / Cultivate 月 50 万 / Coaching 38 万 / Orbit 月 5 万」

L103-104 の本番 LP マッピング → 8 ページ構造へ更新（/gravity/code/ /gravity/coaching/ /gravity/diagnose/）
```

#### Step 1.3 対外発信物 LP 経由ファイル

- `04_GrowthFix/02_マーケティング/260514_営業資料_v0.4_3サービスv2.0_v3.0統合_NotebookLM入稿版.md`
  - 「組織の引力設計プログラム」1 商品 + 個人軸 2 構造へ全体書き換え
  - 料金は「ご相談ください」型 or 内部参考値注記
- `04_GrowthFix/02_マーケティング/260512_GravityRC_営業提案_サービス資料_v1.0.md`
  - 同上
- `04_GrowthFix/02_マーケティング/260512_対談動画_打診メール草稿_v0.1.md`
  - 旧 URL・料金記述を新構造で更新
- `04_GrowthFix/02_マーケティング/260512_無料30分相談装置_設計書_v1.0.md`
  - 動線を 8 ページ構造へ更新（/gravity/ → ご相談）
- `04_GrowthFix/02_マーケティング/260511_セミナーリブランディング素材_v1.0.md`
  - LP 動線を 8 ページ構造へ
- `04_GrowthFix/02_マーケティング/260511_競合分析_v1.0.md`
  - GrowthFix サービス記述を新構造へ
- `04_GrowthFix/02_マーケティング/260513_FB投稿候補_AI論文反映_v1.0.md`
  - 旧 URL 削除・8 ページ動線へ
- `04_GrowthFix/02_マーケティング/260507_LP_SSOT整合チェック_引き継ぎ書_v1.0.md`
  - 25 LP 前提を 8 ページ前提に
- `04_GrowthFix/00_営業/_Sushitech/260415_FAQ_想定問答集_Sushitech.md` `260420_FAQ_想定問答集_Sushitech_v2.md`
  - 対外 FAQ・新構造へ
- `04_GrowthFix/00_W22-W26_週次実行プラン_v1.0.md`
  - 週次プラン現役・新構造へ

#### Step 1.4 lint / memory（運用 SSOT 系）

- `memory/feedback_lp_deployment_path_ssot_check.md`：8 ページ構造の LP マッピングへ更新
- `06_開発/scripts/lint/lint_consistency.sh`：L176-177 / L246-247 / L255 / L312 の Gravity LP 各種 URL チェックを 8 ページ構造に再設計（§4.3）

### Step 2（並列実施可）：方針 B・注記追加

#### Step 2.1 SSOT トップ注記テンプレ（260515 8 ページピボット）

各方針 B ファイルのトップ（h1 直後）に以下を追加：

```markdown
> **★ 8 ページピボット反映注記（260515 確定）：**
> 旧 5 サービス（Recruit / Cultivate / Orbit / Coaching / CODE）→ **「組織の引力設計プログラム」1 商品**（集まる × 躍動する × 留まる 統合）+ **個人軸 2**（CODE / Coaching）の 2 階層構造に統合。**LP 側は料金完全非公開化**（堀田流・問い合わせベース）。本ファイル内の料金記述（月 35 万 / 月 50 万 / 月 5 万 / 38 万 等）および旧 LP URL（`/gravity-recruit/` `/gravity-cultivate/` `/gravity-orbit/` `/gravity-shift/` `/gravity-scan/`）は **内部参考値**（営業資料 / 提案書 / 商談スクリプト作成時の参照用）として温存。本番 LP マッピングは 8 ページ構造（`/` `/profile/` `/achievement/` `/knowledge/` `/news/` `/gravity/` `/gravity/code/` `/gravity/coaching/`）。詳細：`04_GrowthFix/02_マーケティング/260515_8pages_pivot_v1.0_仕様書.md` / `memory/project_8pages_pivot_implementation_260515.md`。
```

#### Step 2.2 対象 SSOT（注記追加）

- `05_プロダクト/_共通/SSOT_Gravity_3軸.md`
- `05_プロダクト/_共通/SSOT_Gravity_コア主張.md`
- `05_プロダクト/_共通/SSOT_用語_JAFCO_HACHI_操電反映.md`
- `05_プロダクト/_共通/SSOT_対話設計_CODE_SCAN.md`（+ 4 型修飾語追加）

#### Step 2.3 09_会社OS（注記追加）

- `09_会社OS/公開/ガイドライン/商品_5サービス詳細.md`
- `09_会社OS/公開/ガイドライン/商品_5サービス_論文反映_Phase8_Phase9.md`
- `09_会社OS/公開/ガイドライン/商品_5サービス_論文反映_Phase10_10軸補完.md`
- `09_会社OS/公開/ガイドライン/design.md`（LP マッピング部分は §11 で更新）
- `09_会社OS/公開/経営思想/接続装置.md` `接続装置_実装パターン.md`
- `09_会社OS/公開/発信・AI/発信.md` `発信_チャネル別運用.md` `発信_学術濃度ルール.md` `AI_自動化群.md`
- `09_会社OS/公開/文化/判断基準_運用レイヤー.md`
- `09_会社OS/非公開/機能/営業.md` `営業_運用詳細.md`
- `09_会社OS/非公開/機能/採用.md`
- `09_会社OS/非公開/ガイド/カスタマー.md`
- `09_会社OS/非公開/経営層/社長.md`

> **既に注記済（再注記不要）**：`09_会社OS/公開/ガイドライン/商品.md` L12

#### Step 2.4 04_GrowthFix（営業プレイブック・サービス設計）

- `04_GrowthFix/00_営業/_営業プレイブック/260512_営業プレイブック_v1.0.md`
- `04_GrowthFix/00_営業/_営業プレイブック/260512_反論処理50問_v0.1.md`
- `04_GrowthFix/00_営業/_営業プレイブック/260512_顧客事例V1_A社_匿名版_v0.1.md`
- `04_GrowthFix/00_営業/_業務委託営業/260512_業務委託営業認定プロトコル_v0.1.md`
- `04_GrowthFix/00_営業/_Gravity営業基盤/*.md`（パイプライン管理・競合比較表 等）
- `04_GrowthFix/00_統合タスクマスター_v1.1.md`
- `04_GrowthFix/01_サービス設計/_Gravity_R/260514_GravityRecruit_標準サービス設計_v2.0.md`
- `04_GrowthFix/01_サービス設計/_Gravity_C/260515_GravityCultivate_標準サービス設計_v3.0.md`
- `04_GrowthFix/01_サービス設計/_Gravity_その他_Orbit_Coaching_ShiftS/260514_GravityOrbit_標準サービス設計_v3.0.md`
- `04_GrowthFix/02_マーケティング/260507_プライシング戦略_SSOT_v0.2.md` `260507_メソッド体系_一元管理_v0.2.md` `260507_競合分析_SSOT_v0.2.md` `260507_アライアンス_ステークホルダー戦略_SSOT_v0.2.md` `260507_顧客成功_CS設計_SSOT_v0.2.md` `260507_データ分析基盤_SSOT_v0.2.md` `260507_商談スライド_提案書_契約書_要件SSOT_v0.2.md`
- `04_GrowthFix/01_サービス設計/_横断_フレーム_戦略/260514_3サービスv2.0_v3.0_確定要素+SSOT反映引き継ぎ書_v1.0.md`
- `04_GrowthFix/01_サービス設計/_横断_フレーム_戦略/260515_R_v2.1.4_Cultivate_v3.0_Orbit_v3.2_全反映漏れ調査_引き継ぎ書_v1.0.md`

#### Step 2.5 memory（注記追加）

- `memory/project_3services_v2_v3_definition_260514.md`
- `memory/project_cultivate_v3.0_definition_260515.md`
- `memory/project_strategy_lock_260430.md`
- `memory/project_orbit_direct.md`
- `memory/project_scan_abolish_260514.md`
- `memory/feedback_coaching_not_frontline_word.md`
- `memory/project_growthfix_company_positioning.md`

### Step 3（最終確認）：lint / 機械チェック更新

#### Step 3.1 lint_consistency.sh 拡張

`06_開発/scripts/lint/lint_consistency.sh` に新ルール追加：

```bash
# [N] 8 ページピボット：LP 公開構造の旧 URL 残存検出（260515 確定）
echo "[N] 8 ページピボット：LP HTML 内の旧 URL 残存検出"

OLD_URLS="gravity-recruit\|gravity-cultivate\|gravity-orbit\|gravity-shift\|gravity-scan\|gravity-code\|gravity-coaching\|academy-wl"

# LP HTML 側で旧 URL が残存していないか確認（_archive 除外・.htaccess 除外）
hits=$(grep -rEn "$OLD_URLS" 05_プロダクト/ --include="*.html" 2>/dev/null \
  | grep -v "_archive" | grep -v "/.htaccess" | wc -l | tr -d ' ')

if [ "$hits" -gt 0 ]; then
  printf "${YEL}⚠ 旧 LP URL の残存：%s 件${NC}（8 ページ構造へ更新要・/gravity/ /gravity/code/ /gravity/coaching/ /gravity/diagnose/）\n" "$hits"
fi

# [N.5] LP HTML 内の料金記述検出（堀田流・LP 完全非公開化）
echo "[N.5] LP 料金完全非公開化チェック"

PRICE_PATTERNS="月 ?35 ?万|月 ?50 ?万|月 ?5 ?万|月 ?85 ?万|38 ?万|5 ?万円"

price_hits=$(grep -rEn "$PRICE_PATTERNS" 05_プロダクト/Gravity/ 05_プロダクト/コーポレート/ --include="*.html" 2>/dev/null \
  | grep -v "_archive" | grep -v "_history" | wc -l | tr -d ' ')

if [ "$price_hits" -gt 0 ]; then
  printf "${RED}✗ LP HTML 内に料金記述：%s 件${NC}（堀田流・完全非公開ルール違反）\n" "$price_hits"
fi
```

既存の以下のセクションは **削除 or リネーム**：
- L246-247：`check_monthly_pricing "Gravity/Recruit/LP/index.html"` `check_monthly_pricing "Gravity/Cultivate/LP/index.html"`（LP に料金記述する前提のチェック → 削除）
- L255：`echo "[2] 5サービスLPの参謀名タグライン整合"` → `[2] 統合プログラム + 個人軸 2 LP の参謀名タグライン整合` にリネーム
- L312：`href="https://growthfix.jp/gravity-shift/"` chk → 削除（旧 URL）

#### Step 3.2 lint_lp_internal_terms.py 拡張

4 型修飾語チェック追加：

```python
# 4 型修飾語必須チェック（260515 8 ページピボット確定）
# CODE 個人 4 型 / 無料 Web 診断 組織 4 型を区別表記

CODE_4TYPES_INDIVIDUAL = ["個人整合型", "個人想いズレ型", "個人強みズレ型", "個人偏愛ズレ型"]
SCAN_4TYPES_ORGANIZATIONAL = ["組織整合型", "組織拡散型", "組織渇望型", "組織不毛型"]

# /gravity/code/ LP では「個人」修飾必須
# /gravity/diagnose/ LP では「組織」修飾必須
# 修飾なし「整合型」「拡散型」「渇望型」「不毛型」が単独で出てくる場合は警告
```

> **注意**：09_会社OS/引力.md L103 や 商品.md L480 等「CODE 4 型 / Scan 4 型」と並列で書かれている対称構造表現は除外。LP HTML のみ厳密チェック。

### Step 4（任意）：tarball + git commit

全置換 + 注記追加完了後：

```bash
cd "/Users/ishiinobuyuki/Documents/Obsidian Vault"
bash 06_開発/scripts/lint/lint_consistency.sh  # 警告 → 0 件想定
python3 06_開発/scripts/lint/lint_lp_internal_terms.py  # HIT 0 件想定

# 全置換完了後 lint 通過確認
git add ...
git commit -m "8 ページピボット SSOT 全反映完走（A 完全置換 + B 注記追加・260515）"
```

---

## §5. 注意事項

### 5.1 Part 3 ハーネス層遵守

LP / コピー編集を伴う場合は以下の Part 3 をタスク前に Read：
- `09_会社OS/公開/ガイドライン/design.md` Part 3（LP / HTML）
- `09_会社OS/公開/経営思想/接続装置.md` Part 3（接続装置整備）
- `09_会社OS/公開/文化/culture.md` Part 3（Note / FB / WP）
- `09_会社OS/公開/発信・AI/発信.md` Part 3（対外発信）

### 5.2 Layer 4 ガード（deploy.sh）の確認

8 ページピボットで旧 LP は本番側に存在するが 301 リダイレクト稼働中。`deploy.sh upload()` の Layer 4 ガードで以下を確認：
- 旧 LP HTML（`05_プロダクト/Gravity/{Recruit,Cultivate,Orbit,Shift,Scan}/LP/`）を本番 `/gravity-recruit/` 等へ再 upload しない
- 段階 1-3 で配置済の .htaccess を上書きしない

### 5.3 既存 memory / SSOT 注記の整合維持

既に注記済の以下は再注記不要：
- `05_プロダクト/_共通/SSOT_用語と定義.md` L14
- `09_会社OS/公開/ガイドライン/商品.md` L12
- `memory/MEMORY.md` の 260515 8 ページピボット項目（新項目として既に追加済）

### 5.4 契約期間サービス特性の整合

3 サービス契約期間が分かれる現状を新「組織の引力設計プログラム」1 商品でどう吸収するかは **本タスクのスコープ外**：
- R v2.1.4 = 最低 3 ヶ月 + 月次更新
- C v3.0 = 最低 6 ヶ月コミット
- Orbit v3.2 = 最低 1 ヶ月 + 月次更新

→ プログラム 1 本化 LP では「期間はご相談（個社状況に合わせて設計）」と表記。社内 SSOT には旧 3 軸契約期間を内部参考値として温存（既に商品.md / SSOT_用語と定義.md にあり）。

### 5.5 4 型修飾語の例外（並列文脈での温存）

「CODE 4 型（整合 / 想いズレ / 強みズレ / 偏愛ズレ）／ Scan 4 型（整合 / 拡散 / 渇望 / 不毛）」のように **CODE と Scan を並列で対称構造表現する文脈** では修飾語追加は **不要**（対称性が読み手に伝わる）。LP 単独 / 1 軸での記述時のみ修飾語必須。

---

## §6. 完了基準

- [ ] **Step 1 完了**：方針 A 全ファイルの完全置換完了（CLAUDE.md / MEMORY.md / 対外発信物 10 ファイル / 戦略 v0.1 系 + 運用 SSOT memory 1 件）
- [ ] **Step 2 完了**：方針 B 全ファイルの注記追加完了（SSOT 4 件 + 09_会社OS 16 件 + 04_GrowthFix 営業/サービス系 15 件 + memory 7 件 = 計 42 件）
- [ ] **Step 3 完了**：lint_consistency.sh / lint_lp_internal_terms.py の拡張完了
- [ ] **lint 全通過**：旧 LP URL 検出 0 件（LP HTML 側）・LP 社内用語 HIT 0 件・LP 料金記述 0 件
- [ ] **本番健全性**：`bash 06_開発/scripts/deploy/verify_deployment.sh` PASS 21 / FAIL 0 維持
- [ ] **memory MEMORY.md 更新済**：本番 LP マッピング（L103-104）+ サービスラインナップ（L117）の 8 ページ構造化
- [ ] **新規 project memory 作成**：`project_8pages_pivot_ssot_reflection_260515.md`（Step 1-3 完了記録）

---

## §7. 別エージェント実行用プロンプト（自己完結）

> **このプロンプトをそのまま別エージェント（別 Node）に渡せばタスク完遂可能**。背景説明・実行手順・完了基準・成果物形式を全て含む。メインスレッドの conversation context を参照させない。
> **推奨モデル**：Sonnet（並列度高い機械的置換 + 注記追加が中心。思想層は触らない）
> **推奨 subagent_type**：general-purpose

```
あなたは GrowthFix Vault（/Users/ishiinobuyuki/Documents/Obsidian Vault）の SSOT 反映実行エージェントです。

## タスク

「8 ページピボット（260515 確定）」を SSOT / 09_会社OS / 04_GrowthFix / memory / lint / CLAUDE.md に網羅反映する。

## 必読ドキュメント（順に Read）

1. /Users/ishiinobuyuki/Documents/Obsidian Vault/04_GrowthFix/02_マーケティング/260515_8pages_pivot_引き継ぎ書_v1.0.md  ← 本書（マスター）
2. /Users/ishiinobuyuki/Documents/Obsidian Vault/04_GrowthFix/02_マーケティング/260515_8pages_pivot_v1.0_仕様書.md
3. /Users/ishiinobuyuki/.claude/projects/-Users-ishiinobuyuki-Documents-Obsidian-Vault/memory/project_8pages_pivot_implementation_260515.md
4. /Users/ishiinobuyuki/Documents/Obsidian Vault/CLAUDE.md（Vault ルート）

## 背景（要点）

- 旧 5 サービス並列（Recruit 月 35 万 / Cultivate 月 50 万 / Orbit 月 5 万 / Coaching 38 万 / CODE 5 万）→ 新「組織の引力設計プログラム」1 商品（集まる × 躍動 × 留まる 統合）+ 個人軸 2（CODE / Coaching）の 2 階層構造に統合
- LP 側は料金完全非公開化（堀田 hajime.institute 流・問い合わせベース）
- LP 公開構造を 25 本 → 8 ページ（/ /profile/ /achievement/ /knowledge/ /news/ /gravity/ /gravity/code/ /gravity/coaching/）に圧縮
- 301 リダイレクト稼働中：/gravity-{recruit,cultivate,orbit,shift,scan,code,coaching}/ /gravity-scan/web-diagnose/ /academy-wl/ → /gravity/ 系
- 4 型修飾語追加：CODE 個人 4 型「個人整合型 / 個人想いズレ型 / 個人強みズレ型 / 個人偏愛ズレ型」/ 無料 Web 診断 組織 4 型「組織整合型 / 組織拡散型 / 組織渇望型 / 組織不毛型」
- 段階 1-3 完了済：/gravity/ LP v2.0 修正・物理移動・301 配置・SSOT 2 件にトップ注記追加

## 実行手順（必読の §4 をそのまま実行）

### Step 1：方針 A・完全置換（即時実施）

引き継ぎ書 §4 Step 1.1-1.4 を実行。
- CLAUDE.md L48/L65/L77/L104 を新構造へ書き換え
- memory/MEMORY.md L103-104（本番 LP マッピング）+ L117（サービスラインナップ）を 8 ページ構造へ更新
- 対外発信物 10 ファイル：260514_営業資料_v0.4_NotebookLM入稿版 / 260512_GravityRC_営業提案 / 260512_対談動画_打診メール / 260512_無料30分相談装置 / 260511_セミナーリブランディング / 260511_競合分析 / 260513_FB投稿候補 / 260507_LP_SSOT整合チェック / Sushitech FAQ ×2 / 260514_3サービス引き継ぎ書 / 260515_全反映漏れ調査 / 00_W22-W26_週次実行プラン
- memory/feedback_lp_deployment_path_ssot_check.md（運用 SSOT・現役）

### Step 2：方針 B・注記追加（並列実施可）

引き継ぎ書 §4 Step 2.1 のトップ注記テンプレを §4 Step 2.2-2.5 の全 42 ファイルに追加。

注記テンプレ：

> **★ 8 ページピボット反映注記（260515 確定）：**
> 旧 5 サービス（Recruit / Cultivate / Orbit / Coaching / CODE）→ **「組織の引力設計プログラム」1 商品**（集まる × 躍動する × 留まる 統合）+ **個人軸 2**（CODE / Coaching）の 2 階層構造に統合。**LP 側は料金完全非公開化**（堀田流・問い合わせベース）。本ファイル内の料金記述（月 35 万 / 月 50 万 / 月 5 万 / 38 万 等）および旧 LP URL（`/gravity-recruit/` `/gravity-cultivate/` `/gravity-orbit/` `/gravity-shift/` `/gravity-scan/`）は **内部参考値**（営業資料 / 提案書 / 商談スクリプト作成時の参照用）として温存。本番 LP マッピングは 8 ページ構造（`/` `/profile/` `/achievement/` `/knowledge/` `/news/` `/gravity/` `/gravity/code/` `/gravity/coaching/`）。詳細：`04_GrowthFix/02_マーケティング/260515_8pages_pivot_v1.0_仕様書.md` / `memory/project_8pages_pivot_implementation_260515.md`。

挿入位置：各ファイル h1（# タイトル）の直後の空行を1つ挟んだ次の行。既に「最終更新」「v X.X」等のメタ行がある場合はその下。

注記対象（再注記不要）：
- 05_プロダクト/_共通/SSOT_用語と定義.md L14（既済）
- 09_会社OS/公開/ガイドライン/商品.md L12（既済）

並列実行で 7-8 ファイルずつのバッチで Edit ツールにより一気に注記追加すること。

### Step 3：lint / 機械チェック更新

引き継ぎ書 §4 Step 3.1-3.2 に従って：
- 06_開発/scripts/lint/lint_consistency.sh：
  - L246-247 を削除（LP に料金記述する前提のチェック）
  - L255「[2] 5サービスLP」をリネーム
  - L312 の `gravity-shift` href チェックを削除（旧 URL）
  - 新ルール [N] 8 ページピボット URL チェック + [N.5] LP 料金完全非公開チェックを追加
- 06_開発/scripts/lint/lint_lp_internal_terms.py：
  - 4 型修飾語チェック関数を追加（/gravity/code/ LP は「個人」修飾必須、/gravity/diagnose/ LP は「組織」修飾必須）

### Step 4：完了確認

```bash
cd "/Users/ishiinobuyuki/Documents/Obsidian Vault"
bash 06_開発/scripts/lint/lint_consistency.sh
python3 06_開発/scripts/lint/lint_lp_internal_terms.py
bash 06_開発/scripts/deploy/verify_deployment.sh   # FAIL 0 維持確認
```

### Step 5：新規 project memory 作成

/Users/ishiinobuyuki/.claude/projects/-Users-ishiinobuyuki-Documents-Obsidian-Vault/memory/project_8pages_pivot_ssot_reflection_260515.md を新規作成。Step 1-3 で実施した内容のサマリーを記録。frontmatter は他の project memory（例：project_8pages_pivot_implementation_260515.md）のフォーマットに従う。

## 制約事項（厳守）

1. **方針 A / B / C の判定根拠を逸脱しない**：引き継ぎ書 §3 で「方針 C 温存」とされたファイルは絶対に変更しないこと（_書籍_WhitePaper / _WP_V10_草案 / 競合分析の過去資料 / _外部分析_対談 / _堀田壁打ち / デイリーログ / Phase 棚卸し / 仮説検討 / DMM 資産 / フィールド検証履歴）
2. **既に注記済の SSOT には再注記しない**：SSOT_用語と定義.md L14・商品.md L12
3. **本番 HTML（05_プロダクト/Gravity/_ブランド/LP/index.html 等）は触らない**：段階 1-3 で確定済
4. **301 .htaccess は触らない**：05_プロダクト/Gravity/{Recruit,Cultivate,Orbit,Shift,Scan,Code,Coaching}/LP/.htaccess は配置済
5. **deploy.sh は触らない**：260515 改修済（並列度 5 + Layer 4 ガード）
6. **Layer 4 ガード違反禁止**：individual curl 個別 upload は禁止。bash 06_開発/scripts/deploy/deploy.sh 経由のみ
7. **memory/_archive*/ 配下は触らない**：アーカイブ
8. **CLAUDE.md は最小限変更**：L48/L65/L77/L104 のみ。FTP デプロイ運用ルールセクションは触らない
9. **時間制約**：本タスクの所要は 2-4 時間想定。Step 1（30 分）→ Step 2（1.5 時間・並列 6-8 batch）→ Step 3（30 分）→ Step 4（5 分）→ Step 5（10 分）
10. **失敗時は中断して報告**：lint FAIL 時・verify_deployment FAIL 時・予想外のエラー発生時はメインスレッドに差し戻し

## 完了報告フォーマット

メインスレッドに以下を 500 字以内で報告：
1. 完了した Step 1-5 のチェックリスト
2. lint / verify 結果サマリー
3. 新規 project memory のパス
4. 想定外の発見・判断保留事項（あれば 1-3 件）
5. 次タスク推奨（残課題があれば）
```

---

## §8. 引き継ぎ書 完了後の最終確認手順

### 8.1 動作確認コマンド

```bash
cd "/Users/ishiinobuyuki/Documents/Obsidian Vault"

# 1. lint 通過確認
bash 06_開発/scripts/lint/lint_consistency.sh
python3 06_開発/scripts/lint/lint_lp_internal_terms.py

# 2. 本番健全性
bash 06_開発/scripts/deploy/verify_deployment.sh

# 3. 残存パターン件数確認（注記追加後でも本文には残存する想定）
echo "=== LP HTML 内の料金記述（0 件想定）==="
grep -rEn "月 ?35 ?万|月 ?50 ?万|月 ?5 ?万|月 ?85 ?万|38 ?万|5 ?万円" \
  05_プロダクト/Gravity/ 05_プロダクト/コーポレート/ --include="*.html" 2>/dev/null \
  | grep -v "_archive" | grep -v "_history" | wc -l

echo "=== LP HTML 内の旧 URL（0 件想定）==="
grep -rEn "/gravity-recruit/|/gravity-cultivate/|/gravity-orbit/|/gravity-shift/|/gravity-scan/|/gravity-code/|/gravity-coaching/|/academy-wl/" \
  05_プロダクト/Gravity/ 05_プロダクト/コーポレート/ --include="*.html" 2>/dev/null \
  | grep -v "_archive" | grep -v "/.htaccess" | wc -l

echo "=== SSOT/09_会社OS/memory の方針 B 注記反映確認（注記文字列を含むファイル数）==="
grep -rl "8 ページピボット反映注記" 05_プロダクト/_共通/ 09_会社OS/ 04_GrowthFix/ "/Users/ishiinobuyuki/.claude/projects/-Users-ishiinobuyuki-Documents-Obsidian-Vault/memory/" --include="*.md" 2>/dev/null | wc -l
```

### 8.2 メインスレッドへの完了報告フォーマット

```
8 ページピボット SSOT 反映完走（260515）

## 実施内容
- Step 1（方針 A 完全置換）：N 件完了
- Step 2（方針 B 注記追加）：N 件完了（既済 2 件除く）
- Step 3（lint 拡張）：lint_consistency.sh + lint_lp_internal_terms.py 完了
- Step 4（lint 通過確認）：旧 LP URL 0 件 / LP 料金記述 0 件 / verify_deployment FAIL 0
- Step 5（新規 project memory）：project_8pages_pivot_ssot_reflection_260515.md 作成済

## 残課題
（残課題があれば箇条書き）

## 次タスク推奨
（次フェーズ提案）
```

---

## 付録 A：調査基盤統計

### A.1 パターン別総ヒット件数（grep ベース）

| パターン | 09_会社OS | 04_GrowthFix | memory | SSOT 用語 | 合計 |
|---|---:|---:|---:|---:|---:|
| 料金記述 | 113 | 786 | 74 | 70 | **1,043** |
| 5 サービス並列 |  |  |  |  | **約 535** |
| 旧 LP URL（HTML 除く） |  |  |  |  | **約 128** |
| 4 型修飾語なし |  |  |  |  | **約 153** |

### A.2 影響ファイル数（重複除く）

- **方針 A（完全置換）**：約 18 ファイル
- **方針 B（注記追加）**：約 42 ファイル
- **方針 C（温存）**：約 105 ファイル
- **合計影響**：約 165 ファイル

### A.3 既に措置済（再対応不要）

- LP HTML：段階 1-3 で完了
- 301 .htaccess：段階 1-3 で配置
- deploy.sh：260515 改修済
- SSOT_用語と定義.md L14 / 商品.md L12：注記済
- memory/MEMORY.md トップ：8 ページピボット新項目追加済
- memory/project_8pages_pivot_implementation_260515.md：新規作成済

---

**本書ステータス**：v1.0 完成・調査完了。実装は §7 のプロンプトで別エージェント（Sonnet × general-purpose）が実行可能。
