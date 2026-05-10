# GrowthFix 会社OS

会社全体の判断軸・思想・運用基準を Markdown で覆い、組織のあらゆる暗黙知をファイル化する。MOONSHOT 流「会社のOS化」フレームを GrowthFix 仕様に翻訳した実装。

---

## 目的（C+D 併用）

| 目的 | 内容 |
|---|---|
| **C：対外発信の素材化** | 公開MDを WhitePaper / Note / LP / 書籍の素材に直転用。AIネイティブ経営の実践者ポジション証明 |
| **D：クライアントへの展開モデル** | 自社で完成させた後、Shift / Coaching の一部として顧客企業に「会社OS化」を導入 |

---

## 構造（4カテゴリ × 2層 = 18ファイル・260502 バランスホイール SSOT 昇格）

```
09_会社OS/
├── 00_README.md           ← このファイル
├── 公開/                  （対外発信・クライアント展開時のテンプレ）
│   ├── 経営思想/          【思想層 ★260430 サブ層分割】
│   │   ├── 会社.md        【経営思想サブ】GrowthFix=引力経営を広める会社
│   │   ├── Why.md         【経営思想サブ】使命=才能解放・自己主権
│   │   ├── 引力.md        【経営思想サブ】中核思想・タグライン実装
│   │   ├── 参謀.md        【経営思想サブ】社長の翻訳者・5サービス参謀体系
│   │   └── 接続装置.md    【接続装置サブ★260430 新規】内的⇔外的橋渡し・5層モデル・「引力＝集客力」言い換え・GrowthFix の最大の知的資産
│   ├── 文化/
│   │   ├── culture.md     尖り路線4.3・批判覚悟・主軸先行
│   │   └── 判断基準.md    堀田フレーム・ウニ丼・5原則・構造逆算
│   ├── ガイドライン/
│   │   ├── design.md      ブランドガイド・引力ブランディング3層
│   │   ├── 商品.md        5サービス一貫性ガイド
│   │   └── 翻訳.md        コアコンピタンス=翻訳力
│   └── 発信・AI/
│       ├── AI.md          AIネイティブ経営の実装ノウハウ
│       └── 発信.md        広報5軸・Note連載・SNS方針
└── 非公開/                （内部運用専用）
    ├── 経営層/
    │   ├── 社長.md            石井さんの判断軸の生情報
    │   └── バランスホイール.md  【★260502 新規】個人軸 8 領域ゴール SSOT（仕事/ファイナンス/健康/知性/趣味/人間関係/家族/社会貢献）× 2026年末 / 2028年 / 2033年
    ├── 機能/
    │   ├── 法務.md        契約パターン
    │   ├── 採用.md        業務委託パートナー基準
    │   └── 営業.md        商談・見積・契約標準
    └── ガイド/
        └── カスタマー.md   顧客対応・コミュニケーション基準
```

---

## MD 内部フォーマット（T4：思想-運用-ハーネス3層構造／260429 拡張）

全MDで共通：

```markdown
# {タイトル}

## Part 1: 思想層（対外発信可・コンテクスト）

### Why（なぜ重要か）
### 定義
### 中核原則

## Part 2: 実装層（内部運用・コンテクスト）

### 具体運用ルール
### ケース・例
### 言葉・語彙

## Part 3: ハーネス層（実行時ガード・260429 追加）

### 良いアウトプットの合格基準（Pass条件）
### 悪いアウトプット例（NG例）
### 実行時テスト（チェックフック）
### 機械チェック対応（lint等への反映）

### 関連MD
### 参考メモリ
```

- **Part 1 の活用**：そのまま WhitePaper / Note / LP に切り出せる対外発信素材
- **Part 2 の活用**：内部運用の指針＋クライアント展開時のテンプレート骨格
- **Part 3 の活用**：AI による業務実行時のテスト基準＝ハーネスエンジニアリングの実装層。森謙吾／AINative 動画の「ハーネス」概念に対応（260429 採用）
- **思想層 4MD（会社／Why／引力／参謀）の Part 3** は「ハーネス展開先への接続」のみ記述。規定の塊化を避ける
- **「参考メモリ」欄**：既存 Obsidian Vault `memory/` フォルダ内のメモリファイル名を明記し、根拠の透明性を担保

## ハーネスエンジニアリング 3 層構造（260429 採用）

```
[1] コア層（経営の核）= 思想層 MD（経営思想 4 MD ＋ 接続装置 1 MD）+ 社長.md
[2] ハーネス層（実行時ガード）= 各 MD の Part 3
[3] 実行エージェント = 人間 / AI（Claude Code・skill 群・Sonnet/Opus）
```

詳細：`公開/発信・AI/harness.md`（260501 SSOT 分離）

## 09_会社OS と SSOT の分業構造（260509 明示化）

> **会社OS は「コア + ハーネス」2 層を担当する場所。SSOT は字面の辞書。実行エージェント層は別物（LP / generate.php / 商談 / セッション）。**

### 4 レイヤー役割分担

| レイヤー | 役割 | 担当 |
|---|---|---|
| **What（字面）** | 価格・期間・サービス名・タグライン・廃止語 | **SSOT**（05_プロダクト/_共通/）|
| **Why（思想・原則）** | なぜそう設計したか・経営思想・北極星 | **会社OS** 公開/経営思想 + 非公開/経営層 |
| **How（運用・ハーネス）** | 業務時の合格基準・NG 例・チェックリスト | **会社OS** 公開/文化 + ガイドライン + 非公開/機能 の Part 3 |
| **Who（人物・判断軸）** | 石井さん固有の判断軸・バランスホイール | **会社OS** 非公開/経営層/ |

→ **SSOT は「What」のみ。残り 3 レイヤーは会社OS が担当。SSOT 単独では運用できない。**

### 実例：Coaching 38 万のケース

| レイヤー | 出所 | 内容 |
|---|---|---|
| What | SSOT_用語と定義 §1 | `Coaching = 38 万・6 ヶ月一括／7 ヶ月目以降 月 5 万` |
| Why | 経営思想/会社.md | 経営者の覚悟は売り物ではなく信用装置 |
| How | 公開/文化/カスタマー.md Part 3 | コーチは判定しない・素材引き出しに徹する・読み合わせフェーズで合意取得 |
| Who | 非公開/経営層/社長.md | 石井さん個人の覚悟確認・コーチング哲学・李英俊師匠との関係 |

4 レイヤー全部揃って初めて Coaching が運用可能。SSOT 単独では「38 万」の字面しか分からない。

### SSOT 索引（260509 追加・物理位置 + 役割）

#### プロダクト編集の現場 SSOT（05_プロダクト/_共通/）

| ファイル | サイズ | 役割 | 主な参照元 |
|---|---|---|---|
| **SSOT_用語と定義.md** | 68KB | 5 サービス・参謀名・価格・期間・タグライン・廃止語・v0.4 新語彙 | LP 全般 / 09_会社OS 営業.md・商品.md・カスタマー.md / lint |
| **SSOT_対話設計_CODE_SCAN.md** | 36KB | CODE 5 観点 + SCAN 8 項目構造化対話の共通フレーム | 進行マニュアル（長谷さん版・将来クライアント版）|
| **SSOT_Gravity_コア主張.md** | 36KB | Gravity 10 コア主張 + 学術領域マッピング + 配置戦略 | WhitePaper V10 / 書籍 2027 Q1 / 認定コーチ研修教材 / 09_会社OS AI.md |
| **SSOT_LPコピー言語ガイドライン.md** | 20KB | LP コピー語彙 / 社内用語 → 業界一般用語の置換ルール | LP 全般 / セミナー LP / Note |

#### 経営戦略 SSOT（04_GrowthFix/02_マーケティング/・260507 7 軸 100% 完走）

| ファイル | 役割 | 参照元 |
|---|---|---|
| 競合分析_SSOT | 識学・アチーブメント等の比較 SSOT | 09_会社OS 商品.md・営業.md |
| 商談スライド_提案書_契約書_要件SSOT | 商談 / 提案書 / 契約書の要件 | 09_会社OS 営業.md |
| LP_SSOT整合チェック_引き継ぎ書 | LP 全件の SSOT 整合状況 | LP 全般 |
| ブランドアセット_一発芸スライド_要件SSOT | 認知装置の要件 | 発信.md |
| アライアンス_ステークホルダー戦略_SSOT | パートナー戦略 | 採用.md |
| プライシング戦略_SSOT | 価格決定の根拠 | 商品.md |
| リスク管理_SSOT | 22 リスク評価 | 判断基準.md |
| 事業KPI_計測指標_SSOT | KPI 体系 | 営業.md |
| データ分析基盤_SSOT | データ収集・分析 | AI.md |
| 顧客成功_CS設計_SSOT | カスタマーサクセス設計 | カスタマー.md |

### SSOT との連動の仕組み

1. **CLAUDE.md（Vault ルート）が SSOT 整合を規定**：「語彙レイヤー SSOT＝ `05_プロダクト/_共通/SSOT_用語と定義.md`」「設計レイヤー SSOT＝堀田フレームワーク体系」
2. **09_会社OS の各 MD が SSOT を参照する DRY 構造**：営業.md / 商品.md / カスタマー.md / 接続装置.md / 発信.md / AI.md / design.md / 判断基準.md など 11 MD が SSOT を参照
3. **lint_consistency.sh が両者の整合を機械検証**：廃止語・禁止語・価格 SSOT 違反を自動検出（260509 で 7 ルール追加）

### なぜ SSOT は会社OS 配下ではなく 05_プロダクト 配下にあるか

**歴史的経緯：**
- 260426：SSOT_用語と定義.md 確立（LP / 提案書編集の現場ニーズが先行）
- 260427：09_会社OS 着手（MOONSHOT 翻訳） ← SSOT が 1 日先行

**設計判断：**
- LP / コピー編集時に SSOT を頻繁参照 → プロダクト傘下が物理近接で便利
- 会社OS は「思想・運用・判断軸」レイヤー・SSOT は「字面の辞書」レイヤーで役割分担
- 物理移動より参照リンク + lint で連動確保するほうが保守コスト低い

## 思想層内サブ層構造（260430 確定）

T4 構造の思想層は 2 つのサブ層で構成される：

```
T4 思想層
   ├ 経営思想サブ層：会社 / Why / 引力 / 参謀（4 MD）── 何を売るか・なぜ存在するか
   └ 接続装置サブ層：接続装置（1 MD）── 内的⇔外的をどう橋渡しするか・どう市場に届けるか
T4 運用層（11 MD）
T4 ハーネス層（各 MD の Part 3）
```

**経営思想 vs 接続装置の役割分離：**

- **経営思想**：内的コンセプトの定義（引力経営・社長の翻訳者・5 サービス）
- **接続装置**：内的コンセプトと外的コンセプト（経営者のコンプレックス）を橋渡しする思想・言語・運用の型

接続装置は GrowthFix の **最大の知的資産・参入障壁**（260430 確定）。詳細：`公開/経営思想/接続装置.md` Part 1。

---

## 進行ステータス（2026-04-27 起点）

### Phase 1（既存メモリ抽出ベース・即書ける思想層）

すべて260427に完成。同日中にセルフレビュー → 思想注入版に書き換え済み（5本：会社/引力/culture/判断基準/参謀。Why.md はレビューで合格）。

| MD | ステータス | 主参照メモリ |
|---|:-:|---|
| 会社.md | ✅ 完成（思想注入版） | `project_growthfix_company_positioning` |
| Why.md | ✅ 完成 | `user_core_mission_talent_liberation` `user_why_glossary_core_concepts` `user_why_grayscale_vs_colorful` |
| 引力.md | ✅ 完成（思想注入版） | `project_gravity_identity_gravitational` `user_life_theme_gravity` |
| culture.md | ✅ 完成（思想注入版） | `feedback_edge_path_43` `feedback_embrace_criticism_and_exaggeration` `feedback_ai_brainstorm_individuality` |
| 判断基準.md | ✅ 完成（思想注入版） | `reference_horita_framework` `project_unidon_service_ratios_260424` 他多数 |
| 参謀.md | ✅ 完成（思想注入版） | `project_3saiyaku_naming_260425` `project_gravity_identity_triple_layer` `project_gravity_l3_positioning` |

### Phase 2（260427 完成）

| MD | ステータス | 主参照メモリ |
|---|:-:|---|
| AI.md | ✅ 完成 | `project_ai_native_strategy` `feedback_ai_brainstorm_individuality` `feedback_model_selection_sonnet` |
| 商品.md | ✅ 完成 | `project_gravity_series_gen2_260415` `project_shift_v2_260422` `project_unidon_service_ratios_260424` ＋ SSOT |
| 発信.md | ✅ 完成 | `project_gravity_strategy_260403` `project_note_knowledge_3themes` `project_q4_2026_triggers` `project_seminar_acting_260424` |
| 翻訳.md | ✅ 完成 | `project_gravity_strategy_260403` `project_gravity_l3_positioning` `user_core_mission_talent_liberation` |
| design.md | ✅ 完成 | `project_gravity_identity_triple_layer` `feedback_lp_header_footer_template` `reference_mobile_css_strategy` |

### Phase 3（260427 完成・法務のみテンプレ維持）

| MD | ステータス | 主参照メモリ |
|---|:-:|---|
| 社長.md | ✅ 完成（260427・生情報フル版・273行） | `user_profile_basics` `user_core_mission_talent_liberation` `user_why_grayscale_vs_colorful` `user_circle_of_competence` `user_financial_context` |
| 採用.md | ✅ 完成（260427・218行） | `project_unidon_service_ratios_260424` `project_gravity_academy_roadmap` `project_q4_2026_triggers` `user_circle_of_competence` |
| 営業.md | ✅ 完成（260427・218行） | `project_coaching_clients` `project_seminar_acting_260424` `feedback_coach_credibility_business_pair` `user_why_grayscale_vs_colorful` |
| カスタマー.md | ✅ 完成（260427・237行） | `project_coaching_clients` `project_orbit_direct` `feedback_coach_credibility_business_pair` `project_gravity_strategy_260403` |
| 法務.md | 📝 テンプレ維持 | （実案件発生時に蓄積。契約・NDA・知財登記の素材が現状不足のため机上の雛形化を回避） |

### Phase 4（260429 完成・Part 3 ハーネス層拡張）

森謙吾／AINative 動画「ハーネスエンジニアリング」を統合フレームとして採用。**法務.md 以外の 14 MD すべてに Part 3 ハーネス層を追加**。

### Phase 5（260430 完成・接続装置サブ層追加）

5 層モデル戦略確定（GrowthFix が売れない真因＝接続装置未整備）に伴い、**思想層内に独立サブ層「接続装置」を追加**。

| MD | ステータス | 主参照メモリ |
|---|:-:|---|
| **接続装置.md** | ✅ 完成（260430・新規・思想層内サブ層）| `project_internal_external_concept_260430` `user_self_intro_attractor_designer_260430` `feedback_recruitment_pain_first` `feedback_egetsunai_specific_over_abstract` |

### Phase 6（260430 午後完成・戦略大改訂反映：会社.md / 商品.md）

**260430 午後の戦略確定（タグライン進化・6 サービス体系・得意技 2 軸・個人引力単一統一・4 型 A' 案）**を会社.md / 商品.md に反映。最重要 SSOT として `project_strategy_lock_260430.md` を memory 永続化。

### Phase 7（260430 夕完成・Scan リブート＋タグライン階層構造）

**260430 夕の戦略再整理：**
1. Blueprint v6.0「採用口説きブループリント」廃止 → **Gravity Scan「組織の引力タイプ診断・Pre-Shift 適合診断」リブート**
2. **タグライン階層構造**：会社思想「優秀人材が躍動する会社をつくる」（コーポレート）／プロダクト思想「組織に、引力を。」（Gravity TOP）
3. **CODE × Scan 対比構造**：個人軸の引力診断 × 組織軸の引力診断・両方「引力の参謀」
4. 採用 4 軸＋面接ブループリント 5 要素は **Shift R Week 1-2 納品物に移管**

| MD | ステータス | 主参照メモリ |
|---|:-:|---|
| 商品.md | ✅ Scan リブート反映完了（260430 夕） | `project_scan_reboot_260430` `project_session_learnings_260430_pivot` |
| 引力.md | ✅ CODE × Scan 対比＋タグライン階層追記（260430 夕） | `project_session_learnings_260430_pivot` |
| 参謀.md | ✅ 6 サービス参謀体系（Scan 反映）（260430 夕） | `project_3saiyaku_naming_260425`（更新済み） |
| 判断基準.md | ✅ Part 3 に 5 つの気づき追記（260430 夕） | `project_session_learnings_260430_pivot` |
| その他 7 MD（Why／会社／culture／design／翻訳／発信／AI）| ✅ Blueprint → Scan 機械置換完了 | （sed 一括）|

**新規メモリ：** `project_session_learnings_260430_pivot.md`（5 つの判断軸学び：戦略撤回スピード／タグライン階層／CODE × Scan 対比／LP 単一化／顕在ニーズゼロ運用検証）

### Phase 8（260501 夜・シャープ化哲学 + Lean MVP コンセプトテスト + AI Agent 並列実行 + ウニ丼進化反映）

**260501 夜の戦略確定：**
1. **シャープ化哲学**（モリモリ → 1 文）：49 質問テンプレ運用 + ★/⚪/△ 削ぎ落としマークで Shift R/C を「1 文で説明できる状態」まで研ぎ澄ます（Shift R = 「採用コスト悪循環を断つ」/ Shift C = 「制度疲弊からの解放」）
2. **Lean MVP コンセプトテスト原則**：1 サービスのモニターを「実証 → 3 案 × N サービス = N×3 VP コンセプトテスト」に転換（5/8 長谷さんモニターで R/C 6 VP テスト実施予定）
3. **LP 構成判断の見直し**（260430 LP 単一化原則 → 260501 実運用検証で見直し）：Gravity マップで R/C が別象限ターゲット（人力拡大 vs 施策先行）の場合は 2 枚分割を優先（Shift R 専用化 + Shift C 専用 LP 新規・5/2-5/14 段階移行）
4. **RECODE Agent 並列実行パターン**：Sonnet × 6 並列で 33 ファイル / 6,571 行を約 10-15 分で 278 発見抽出
5. **ウニ丼理論の進化**：標準化 = AI（70-75%）/ トレーニング = 人間（35-40%）の時系列実装

| MD | ステータス | 主参照メモリ |
|---|:-:|---|
| 判断基準.md | ✅ シャープ化哲学 + Lean MVP コンセプトテスト + LP 構成判断見直し追記（260501 夜）| `project_shift_rc_specs_260501` `project_shift_rc_field_validation_260501` |
| AI.md | ✅ RECODE Agent 並列実行パターン + ウニ丼理論進化 + 6 セッション連続稼働パターン追記（260501 夜）| `project_shift_rc_field_validation_260501` `project_harness_engineering_260429` |

**主参照ファイル：**
- 1 文 SSOT（Shift R）：`04_GrowthFix/01_サービス設計/260501_Shift_R_49質問_削ぎ落とし版.md`
- 1 文 SSOT（Shift C）：`04_GrowthFix/01_サービス設計/260501_Shift_A_シャープ版_1文_5論点確定.md` ／ `260501_Shift_A_49質問_削ぎ落とし版.md`
- 5/8 R/C 統合 6 VP 資料：`04_GrowthFix/01_サービス設計/260508_長谷さんモニター_R_A統合_6VPテスト資料一式.md`
- A4 1 枚サマリー：`04_GrowthFix/01_サービス設計/260501_Shift全体像_A4一枚_本日確定版.md`

**Phase 8 で持ち越し（5/8 モニター後の最終仕様で反映）：**
- 商品.md：Shift C シャープ版（躍動 3 点セット 27p + 1 文 + 標準化+OJT 構造）反映 → 5/9-5/15 計画
- 発信.md：Meta 広告 R/C 分離戦略 + 5/15 セミナータイトル整合性 → 5/4-5/16 段階反映

### Phase 9（260502 朝・/sharpen × 5 サービス完遂 + Shift R/C 2 LP 物理分割 + 廃止用語完全消滅 + git 履歴復活 + auto_commit hook）

**260502 朝〜午後の戦略確定：**

1. **/sharpen × 5 サービス全完遂**：CODE / Scan / Coaching / Shift R / Shift C の 1 文 SSOT 確定 + 49 質問削ぎ落とし版作成 + LP/SSOT/商品.md/営業.md 整合
2. **Shift R/C 2 LP 物理分割**：既存 /gravity-shift/ → Shift R 専用化 + /gravity-shift-a/ 新規作成（260501 Phase 8 確定の運用実装）
3. **20 LP 横断監査 + 廃止用語完全消滅**：採用 4 軸（5 件）／面接ブループリント（2 件）／ブループリント（2 件）が gravity-hub と service の 2 ページに集中残存していたのを完全クリーン化
4. **サービス軸性質判定（Push vs Pull）原則確立**：CODE/Scan/Shift R/C は Push 型（採用接地統一）／Coaching は唯一 Pull 型（「売り言葉にしない」原則）
5. **ハイブリッド配置パターン標準化**：軸 B（市場接地）Hero 主軸 + 軸 A（既存軸）Sub Hero + 軸 C（構造起点）Pricing 補強の 3 軸ハイブリッド
6. **funnel 全体採用接地統一**：CODE → Scan → Shift R 連続 Hero が採用接地で言語的に統一 → 経営者の「自分の話」感を全段階で維持
7. **ブラッシュアップの境界線確立（WhitePaper LP 事故教訓）**：思想書 vs 採用ペイン具体起点・LP の役割別に軸を分ける判定ルール
8. **git 履歴復活 + auto_commit hook 実装**：5 ヶ月放置事故対策。Stop event hook で自動 commit + secrets 検出ガード + GitHub Push Protection 三層防御

| MD | ステータス | 主参照 |
|---|:-:|---|
| 商品.md | ✅ CODE / Scan / Coaching セクション 1 文 SSOT + 配分 15-25-20 + ハイブリッド配置追記 | `260502_*_シャープ版_1文_5論点確定.md` |
| SSOT_用語と定義.md | ✅ CODE / Scan / Coaching スコープ詳細セクション新規 | 同上 |
| 営業.md | ✅ funnel diagram [2][3][4] 全更新（CODE/Scan 60 分配分 + Coaching Pull 性質）| 同上 |
| Scan generate.php / CODE generate.php | ✅ PART タイミング 15-25-20 化 + LP 分離 URL 振り分けルール | 同上 |
| **判断基準.md** | ✅ サービス軸性質判定（Push vs Pull）+ ブラッシュアップ境界線 + git 履歴運用追記（260502 朝）| `260502_Coaching_シャープ版_1文_5論点確定.md` ／ `feedback_coaching_not_frontline_word.md` |
| **AI.md** | ✅ secrets 防御パターン + auto_commit hook（ハーネスエンジニアリング実装事例）追記（260502 朝）| 本セッション・GitHub Push Protection 事故対応 |
| **接続装置.md** | ✅ ハイブリッド配置パターン標準化 + funnel 全体軸統一原則追記（260502 朝）| `260502_*_シャープ版_1文_5論点確定.md` |

**主参照ファイル：**
- 1 文 SSOT × 5：`04_GrowthFix/01_サービス設計/260502_{CODE,Scan,Coaching}_シャープ版_1文_5論点確定.md` ／ `260501_Shift_{R,A}_*`
- 49 質問削ぎ落とし版 × 5：上記同フォルダ `260502_*_49質問_削ぎ落とし版.md` ／ `260501_Shift_*_49質問_削ぎ落とし版.md`
- 20 LP 監査結果：`04_GrowthFix/04_デイリーログ/260502_daily.md`
- auto_commit hook：`06_開発/scripts/hooks/auto_commit.sh`

### Phase 10（260503・二層命名運用 B 案 + Gravity Shift minimal LP 化（Orbit パターン汎用化）+ Gravity Succession 骨子確定）

**260503 朝〜夜の戦略確定：**

1. **B 案二層命名運用確定**：内的 Shift R/C/Full ／ 外的 Gravity Recruit/Cultivate/Shift。接続装置 5 層モデル「内的→外的」原則と完全整合。CODE/Scan の既存パターンと同じ二層構造で運用負荷増ゼロ
2. **β 並列型 URL 構造確定**：`/gravity-recruit/` `/gravity-cultivate/` `/gravity-shift/` の 3 並列・既存 Code/Scan/Coaching/Orbit と完全対称
3. **Gravity Shift minimal LP 化（Orbit パターン汎用化）**：5/1 で Orbit を minimal LP 化した運用が、5/3 で Shift にも適用 → 2 例で汎用パターン化。Hub/コーポレート/各 LP フッターから Shift カード/リンク撤去・Recruit/Cultivate の pricing 欄では言及保持
4. **Scan 4 型推奨フロー更新**：「不毛型 → Shift Full」→「不毛型 → Recruit + Cultivate 順次（商談時に Shift 提案）」に統一
5. **Gravity Succession 骨子確定（構想段階）**：引力経営 3 軸目（採用×躍動×承継）。S-3 PMI 統合実装が主軸候補・3 点セット 78p（Shift R/C 完全対称）・6 ヶ月伴走・規模別 1,000-3,000 万 + 成功報酬。本格化は 2027〜・第 1 フェーズ Shift R 集中軸を侵食しない制約遵守
6. **lint_consistency.sh [5.5] 機械チェック新設**：minimal LP 運用違反（Hub/コーポレート/Footer に Shift カード/リンク残存）を自動検出
7. **18 ファイル本番デプロイ完遂**：Phase 1（新規 LP + .htaccess redirect）+ Phase 2（既存 9 LP cross-link 一斉更新）+ minimal LP 化再デプロイの 3 段階を 1 セッションで完遂

| MD | ステータス | 主参照 |
|---|:-:|---|
| **SSOT_用語と定義.md** | ✅ §0.5 命名二層運用ルール新設 + Gravity Shift minimal LP 運用ルール + 7 項目最終整合（動線/Scan 4 型/組織の引力 4 型表/Shift Full スコープ詳細/Coaching 並走表記/Section 8 廃止用語/関連メモリ） | `project_naming_two_layer_260503.md` |
| **商品.md** | ✅ 二層命名運用バナー追加 + 4 型 → URL β 並列型化 + 営業時パッケージ外的呼称化 + Part 3 NG 例に二層命名違反追加 | 同上 |
| **接続装置.md** | ✅ 商品名・サービス名の二段運用拡張（260503 サービス名にも拡張）+ funnel 連続 Hero 例外的呼称化 | 同上 |
| **営業.md** | ✅ 二層命名運用バナー + 4 型 → 推奨 URL β 並列型化 | 同上 |
| **カスタマー.md / 採用.md / 発信.md** | ✅ 二層命名運用バナー追加 | 同上 |
| **判断基準.md** | ✅ ★ minimal LP 戦略選択原則（Orbit パターン汎用化・260503 確立）追加 + Part 3 ハーネス層 NG 例 1 件・合格基準 1 件追加 | `project_naming_two_layer_260503.md` |
| **AI.md**（260503 夜追記） | ✅ サブエージェント分離パターン新設（モデル選択経済表に lp-implementer / script-writer 行追加 + 専用 ★ セクション「サブエージェント分離パターン」+ 言葉・語彙 3 件追加 + Part 3 機械チェック対応に `~/.claude/agents/*.md` 追加） | `feedback_model_selection_sonnet.md` |
| **harness.md**（260503 夜追記） | ✅ 3 層構造 [3] 実行エージェント層に「物理ファイル化（260503 確立）」サブセクション新設 + Part 2 既存ハーネス資産表にサブエージェント定義 + auto_commit hook 行追加 | 同上 |

**主参照ファイル：**
- B 案二層命名運用 SSOT：`memory/project_naming_two_layer_260503.md`
- Succession 骨子：`04_GrowthFix/01_サービス設計/260503_GravitySuccession_シャープ版_1文_5論点確定_概念フェーズ.md`
- minimal LP 実装：`05_プロダクト/GravityShift/LP/index.html`（130 行・1 ページ完結）
- W18 週次クローズ：`04_GrowthFix/04_デイリーログ/260501_weekly_close.md`
- サブエージェント定義：`~/.claude/agents/lp-implementer.md` ／ `~/.claude/agents/script-writer.md`（260503 夜・実行エージェント層の物理ファイル化第 1 弾）

**Phase 10 で持ち越し（W19 / 5/4-5/10）：**
- 発信.md 反映：命名運用変更の対外発信物への影響・Note Vol.2 接続
- WhitePaper PDF 再生成（HTML 更新済・PDF 古いまま）
- 5/8 長谷さんモニター実施 → Gravity 受注 1 件目判断
- アウトバウンド母数復活（朝のリーチルーティン毎日実行・W19 月から再開）

**Phase 9 で持ち越し（5/8 モニター後 or 余力時）：**
- 5 サービス × 5 層整合の最終確認（5/8 モニター反応反映）
- 価格見直し（Lean MVP 原則・モニター後判断）：CODE 5 万 → 7-10 万 ／ Scan 10 万 → 12-15 万
- gravity-code-executive LP の Footer 組織軸列に Shift R/C 追加（5/8 後別ペルソナ判断）
- design.md Part 3 に「20 LP 横断監査ハーネス」セクション追加（時間あれば）

**新規メモリ候補（5/2 で永続化された SSOT・コード）：**
- `auto_commit.sh`（hook ハーネス装置）
- `.gitignore` 拡張パターン（secrets 防御）
- 判断基準.md「サービス軸性質判定（Push vs Pull）」原則
- 接続装置.md「ハイブリッド配置パターン」標準化
- 接続装置.md：言語マップ R/C 別ペインカテゴリ分離 → 5/16 以降
- 採用.md：業務委託パートナー組成 Phase 1 採用基準詳細化 → 次の weekly-close でまとめて

| MD | 更新内容 | 主参照メモリ |
|---|---|---|
| **会社.md（260430 戦略反映版）**| アンブレラタグライン「優秀人材が躍動する会社をつくる」追加・6 サービス体系（Shift R/C/Full）・識学対比に「野心商材 vs コンプレックス商材」軸追加・進化軌跡第 5 期追加・得意技 2 軸の戦略判断基準追加 | **🔥 `project_strategy_lock_260430.md`**（最重要 SSOT）|
| **商品.md（260430 戦略反映版）**| 6 サービス体系・組織の引力タイプ診断化・Shift R/C/Full 詳細スコープ・公開語彙 Why × 才能 × 偏愛 統一・4 型 A' 案・廃止用語 8 件追加・営業時パッケージ Shift R/C 対応 | **🔥 `project_strategy_lock_260430.md`** ＋ SSOT |



| MD | Part 3 内容 |
|---|---|
| AI.md | AI 生成物（発信物・分析メモ・LP）の合格基準＋ TDD 経営の業務適用マッピング |
| 判断基準.md | コンバージョン 3 条件＋ 5 原則＋ウニ丼比率の Pass 条件・意思決定タイミング別チェック |
| culture.md | 尖り路線 4.3 の合格基準・4 点取り型 NG・音読セルフレビュー |
| 営業.md | 適合判定 Pass 条件＋ **チェンジマネジメント 3 層判定表（Shift / Coaching 差別化）** |
| 商品.md | 5 サービス品質＋ **Shift Week 1-2 ハーネス成立度診断（Shift 80→90 万正当化材料）** |
| 採用.md | 業務委託パートナー「**ハーネスを書ける人 5 項目評価**」 |
| 発信.md | 発信物の品質・採用ペイン接地・スピーカー偏差値 |
| design.md | LP / WP / コーポレートのビジュアル品質・19 LP 一括運用 |
| 翻訳.md | 経営者言語 → 組織言語の翻訳出力品質 |
| カスタマー.md | 磁化の継続 vs 業務処理の判定 |
| 社長.md | **コア層としての石井さんの責務 5 項目** |
| 会社.md | 思想層・ハーネス展開先への接続のみ |
| Why.md | 思想層・Why が各ハーネスに与える駆動 |
| 引力.md | 思想層・引力思想 → ハーネス派生関係 |
| 参謀.md | 思想層・参謀名 → ハーネス派生関係 |

---

### Phase 8（260430 夜完成・情報圧縮＋膨張抑制ルール整備）

**目的：** 19 MD・6,212 行に膨らんだ 09_会社OS の重複・冗長を圧縮し、今後の膨張抑制ルールを整備する。

**実施内容：**

1. **履歴ファイルの `_archive/` 移動**：`260429_AINative森_ハーネスエンジニアリング_会社OS運用アップデート提案.md`（179 行）を `_archive/` 配下へ移動。OS ルートが現役 MD のみで構成される状態に。
2. **関連MD/参考メモリ簡素化（12 MD）**：各 MD の「関連MD」「参考メモリ」欄を 5 件以内に縮小。冗長参照を削除し、必須参照のみ残す。
3. **タグライン階層構造の SSOT 一元化**：旧 3 層タグライン構造（メイン／サブ／アイデンティティ）を廃止し、260430 確定の 3 層階層構造（会社思想／プロダクト思想／識学アンチテーゼ）に刷新。詳細は `引力.md` Part 2、アンブレラタグラインは `会社.md` Part 1 が SSOT。
4. **6 サービス体系サマリーのポインタ化**：`会社.md` の 6 サービス価格表を `商品.md` Part 2 へのポインタ化。
5. **ハーネスエンジニアリング SSOT 確認**：`AI.md` Part 1 が SSOT として機能していることを再確認。他 MD は既にポインタ化済み。**※260501 追加：AI.md から `harness.md` へ独立分離（B ルール 500 行以内達成）**。
6. **Why × 才能 × 偏愛 SSOT 確認**：`引力.md` Part 1 中核原則が SSOT として機能。他 MD の引用は短文参照に留まることを確認。

**削減目安：約 250-350 行**（全体の 4-6%）

| 項目 | 状態 |
|---|:-:|
| `_archive/` 移動 | ✅ 完了（260430 夕）|
| 関連MD/参考メモリ簡素化 | ✅ 完了（260430 夜・12 MD 全件）|
| タグライン階層構造一元化 | ✅ 完了（260430 夜・引力.md 刷新）|
| 6 サービス体系ポインタ化 | ✅ 完了（260430 夜・会社.md ポインタ化）|
| ハーネス／Why × 才能 × 偏愛 一元化 | ✅ 確認のみ（既に SSOT 確立済み）|

---

## 文書管理ルール（260430 確定・今後の膨張抑制）

### A. 1 MD = 1 コンセプトの SSOT 化

- 各 MD は「1 つの中核コンセプト」の SSOT として機能
- 他 MD で参照する場合は**ポインタリンク**のみ・内容コピーペースト禁止
- 例：「Why × 才能 × 偏愛」の詳細定義は **引力.md** にのみ記載・他は「詳細：引力.md Part 1」

### B. ファイルサイズ上限（目安）

- 思想層 MD（Why.md / 引力.md / 会社.md / 参謀.md / 接続装置.md）は **300 行以内**が理想
- 機能系 MD（商品.md / 営業.md / AI.md 等）は **500 行以内**
- 500 行を超えた MD は分割・SSOT 参照ポインタ化を検討

### C. 履歴記録は `_archive/` へ

- Phase 完成後の履歴ファイルは `_archive/` に物理移動
- 09_会社OS ルート・Phase ディレクトリは現役 MD のみで構成

### D. 関連MD/参考メモリは 5 件以内

- 各 MD の Part 3 末尾の「関連MD」「参考メモリ」は必須参照のみ残す（5 件以内）
- 「関連 SSOT」セクションは廃止し、ヘッダーの SSOT 注記で代替

### E. 重複検出の定期実行

- 四半期 1 回 `/company-os-review` で重複検出
- `grep -rln "重複候補キーワード"` で出現 MD 数 4 以上は SSOT 化検討

### F. 「参考保持」「履歴記録」「過去版」マーク付きセクションは 30 日経過で削除候補化（260511 確立）

> **背景：** 260511 朝の SSOT 整理セッションで「常に情報は膨大化していく」課題が浮上。明示的に「参考保持」「v0.x 履歴」「盛り盛り化の経緯記録として保管」とマークされたセクションが上書き済の現役版に対して累積していることを発見。

**運用ルール：**

1. **マーカー語彙の統一**：削除候補化したいセクションには以下のいずれかを明記
   - 「（YYMMDD 版・参考保持）」
   - 「v0.x 履歴」
   - 「過去パターン記録」
   - 「○○ シャープ化前の参考記録」

2. **30 日経過判定**：マーク付与から 30 日経過 + 現役版が SSOT として確立済の場合、以下のいずれかを実行
   - **削除**（コア概念が他 SSOT で再構成済の場合）
   - **`_archive/` 物理移動**（マッピング情報・反映理由など参照価値が残る場合）

3. **lint で機械検出**：`lint_consistency.sh [11]`（将来追加）で `grep -n "参考保持\|v0\.x 履歴\|過去パターン記録"` ヒットを月次レポート

4. **削除前確認チェックリスト：**
   - [ ] 現役版（v1.0 / 最新 SSOT）が存在し SSOT 化済
   - [ ] 削除対象内のコア概念が他 MD（SSOT / 09_会社OS）で再構成済
   - [ ] 削除対象内の固有情報（論文 ID マッピング・特定の数値）が _archive/ で参照可能か

5. **例外運用：**
   - **改訂履歴セクション**は MD 末尾に 50 行以内なら残す（v1.0 → v1.x の進化軌跡）
   - **判断ログ**（260430 戦略ピボット等）は memory に project_*.md として保管・MD には残さない

**運用根拠：** 260511 朝の実例 = 商品_5サービス詳細.md L.292-333「旧 Shift R 実装フロー（260501 版・参考保持）」42 行を削除（現役 v1.0 で上書き済・JAFCO 反映要素は SSOT_用語と定義.md §10-11 に SSOT 化済）。同パターンが Phase 7 反映本体 / v0.x 履歴に複数残存。

---

## 既存 Obsidian Vault との関係

| フォルダ | 役割 |
|---|---|
| `01_石井伸幸/` | 個人プロファイリング・バランスホイール（人格データ層） |
| `02_セッション記録/` | コーチング書き起こし（生データ層） |
| `04_GrowthFix/` | 営業・サービス設計・マーケ・採用・デイリーログ（実務運用層） |
| `05_プロダクト/` | 各LP・診断UI・WP（プロダクト層） |
| `09_会社OS/` ★本フォルダ | **判断軸・思想・運用基準の単一情報源**（OS層） |
| `memory/`（Claude） | Claude が参照する事実・フィードバック・プロジェクト状態（記憶層） |

**接続関係：** OS層（09）が memory（記憶層）から要点を抽出して構造化し、対外発信・クライアント展開・自社運用の3用途に分配する。

---

## 更新ルール

1. **MDの追加・大幅編集時は MEMORY.md（Claude記憶インデックス）にも反映**：将来のClaude会話でも参照可能にする
2. **Part 1 思想層の編集は慎重に**：対外発信物（WP/LP/Note）と整合を取る必要がある
3. **「言葉・語彙」欄は SSOT**（`05_プロダクト/_共通/SSOT_用語と定義.md`）と整合させる
4. **公開/非公開の物理分離を維持**：「公開」フォルダに非公開情報（顧客名・金額・契約詳細）を絶対に書かない
5. **新規MDを作る前に既存MDで吸収できないか検討**：ファイル肥大化を防ぐ

---

## 関連参照

- MOONSHOT 元ネタ：「会社全体をMDで覆う」（暗黙知を10MDに分解／個別の暗黙知 → 会社のOS化）
- 既存 SSOT：`05_プロダクト/_共通/SSOT_用語と定義.md`（5サービス・参謀名・価格・期間・3要素）
- Claude memory インデックス：`memory/MEMORY.md`
