# Phase 10B/C：サービス反映方針書 + シャープ化 v1.0（Phase 9 Bandura 系列・260510 夜）

> **位置づけ：** Phase 9 採用 21 件（Bandura 系列）を Phase 7-8 と同パターンでサービス別に反映 + Phase 8 シャープ化基準（コア 3 + 補強 2 = 5 件上限）を維持しつつ「**思想層補強引用**」として別枠追加。
> **元データ：** Phase 9 引用ライブラリ v4.0（164 件）+ Phase 10A スパーリング結果（採用 21 / 除外 2）

---

## 0. シャープ化戦略（260510 確定）

### 0.1 Phase 8 シャープ化基準を維持
- 各サービスの Phase 7 採用論文は **コア 3 + 補強 2 = 5 件上限**を厳守
- アーカイブ 12 件の保管構造も維持

### 0.2 Phase 9 Bandura 系列は「思想層補強引用」として別枠
- 各サービスに **1-2 件の Bandura 系列引用**を「思想層バックボーン」として追加
- 既存コア 3 + 補強 2 とは別ラインで管理（混同回避）
- 配置：LP の理論背景セクションに **「思想層バックボーン」** 小セクション新設

### 0.3 戦略的意義
> **Phase 7-8 = 実装層の補助線（HOW 軸）**
> **Phase 9 = 思想層のバックボーン（WHY 軸）**

両者を「実装 × 思想」の二層構造で並列運用することで、識学差別化を：
- HOW 軸 = OD 業界 5 系列の最新統合実装版
- **WHY 軸 = Bandura 効力感理論を直接実装する企業向けサービス**

の 2 軸で完成させる。

---

## 1. サービス別 Phase 9 反映マッピング

### 1.1 CODE（個人引力診断・既存温存方針 → Phase 9 で初の追加）

**Phase 6/7/8 まで：論文反映ゼロ（既存 v2.0 SDT 系列で十分）**

**Phase 9 追加（思想層バックボーン 1 件）：**
- **D-1 Bandura 1977 PR**（49,507 cites）── 「経営者の引力 = Self-Efficacy の高さ」の理論基盤

**反映先：**
- CODE LP `/gravity-code/` 末尾「思想層バックボーン」小セクション新設
- CODE generate.php theory-background-box に **「Bandura Self-Efficacy 理論」**項目追加

**ブラッシュアップ案：**
> **「経営者個人の引力 = Bandura（Stanford）が 1977 年に確立した Self-Efficacy（自己効力感）の高さ。CODE はこの理論を実装する個人軸診断サービス」**

### 1.2 Scan（組織引力 4 型診断）

**Phase 8 シャープ化済（既存）：**
- コア：A-20 Saks 2006 Engagement / A-17 Peltokorpi 2017
- 補強：A-3 Bauer 2007 / A-9 Saks-Gruman 2018

**Phase 9 追加（思想層バックボーン 2 件）：**
- **E-1 Bandura 2000 Current Directions**（1,721 cites）── 「組織の引力 4 型 = 集合的効力感パターン」の理論基盤
- **E-2 Goddard-Hoy 2000 AERJ**（839 cites）── 学校組織の集合的効力感研究

**反映先：**
- Scan LP `/gravity-scan/` の理論背景セクションに「思想層バックボーン」小セクション新設
- Scan generate.php theory-background-box に Bandura 2000 / Goddard 2000 追加（基盤理論ブロック内）

**ブラッシュアップ案：**
> **「Scan 4 型診断は、Bandura（Stanford）2000 年の Collective Efficacy 理論と Goddard-Hoy（Ohio State）の組織応用研究に基づく」**

### 1.3 Shift R（採用基盤）

**Phase 8 シャープ化済（既存）：**
- コア：A-3 Bauer 2007 / A-18 Cooper-Thomas/Anderson 2006 / A-6 Ellis-Bauer 2017
- 補強：A-8 Saks-Gruman 2011 / A-13 Saks-Gruman 2014

**Phase 9 追加（思想層バックボーン 1 件）：**
- **D-2 Stajkovic-Luthans 1998 PsycBull**（2,210 cites）── 「採用後 Self-Efficacy 構築 → 業績向上」の理論基盤

**反映先：**
- Shift R LP `/gravity-recruit/` の理論背景セクションに「思想層バックボーン」小セクション新設

**ブラッシュアップ案：**
> **「採用後 90 日定着の理論的根拠 = Stajkovic-Luthans 1998（114 研究 21,616 サンプル メタ分析）の Self-Efficacy → 業績効果。Shift R Week 7-12 は Self-Efficacy を制度的に構築する設計」**

### 1.4 Shift C / Cultivate（躍動軸）

**Phase 8 シャープ化済（既存・最重要）：**
- コア：B-1 Bushe-Marshak 2009（Dialogic OD）/ B-9 Kotter 2011（8 ステップ）/ B-16 Beer-Nohria 2009（E+O 統合）
- 補強：A-9 Saks-Gruman 2018（17 資源）/ B-19 Raelin 2011（中間管理職 4 条件）

**Phase 9 追加（思想層バックボーン 3 件）：**
- **E-1 Bandura 2000**（1,721 cites）── Collective Efficacy 構築の理論基盤
- **E-3 Tasa-Taggar-Seijts 2007 JAP**（232 cites）── **チーム CE の縦断構築モデル → 12 週設計の直接根拠**
- **E-4 Stajkovic-Lee-Nyberg 2009 JAP**（333 cites）── CE × 業績メタ分析

**反映先：**
- Cultivate LP `/gravity-cultivate/` の理論背景セクションに「思想層バックボーン」小セクション新設
- Shift C 商談資料 v0.5 化（Phase 9 反映）

**ブラッシュアップ案：**
> **「Shift C 12 週は、Bandura 2000 / Tasa-Taggar-Seijts 2007（McMaster）/ Stajkovic-Lee-Nyberg 2009（96 研究 6,128 グループ メタ分析）に基づく Collective Efficacy 構築の縦断プロセス。OD 5 系列（実装層）+ Bandura 効力感理論（思想層）の二層統合」**

### 1.5 Coaching（経営者個人）

**Phase 8 シャープ化済（既存）：**
- コア：B-1 Bushe-Marshak 2009 / B-12 Cooperrider 2017
- 補強：A-20 Saks 2006 / A-9 Saks-Gruman 2018

**Phase 9 追加（思想層バックボーン 2 件）：**
- **D-1 Bandura 1977 PR**（49,507 cites）── Self-Efficacy の 4 源泉（成功体験 / 代理経験 / 言語的説得 / 情動的覚醒）
- **E-6 Taggar-Seijts 2003**（53 cites）── 個人 SE → Collective CE 翻訳の媒介モデル

**反映先：**
- Coaching LP `/gravity-coaching/` の理論背景セクションに「思想層バックボーン」小セクション新設

**ブラッシュアップ案：**
> **「Coaching 6 ヶ月伴走は、Bandura（Stanford）の Self-Efficacy 4 源泉（成功体験 / 代理経験 / 言語的説得 / 情動的覚醒）を経営者個人に適用する設計。経営者の Self-Efficacy → 組織の Collective Efficacy への翻訳機構（Taggar-Seijts 2003）」**

### 1.6 Orbit（留まる軸・月次強化）

**Phase 8 シャープ化済（既存）：**
- コア：A-3 Bauer 2007 / A-9 Saks-Gruman 2018 / A-2 Van Maanen 1975
- 補強：A-19 Cooper-Thomas/Anderson 2005 / A-20 Saks 2006

**Phase 9 追加（思想層バックボーン 1 件）：**
- **E-1 Bandura 2000**（1,721 cites）── Collective Efficacy 月次維持の理論基盤

**反映先：**
- Orbit LP `/gravity-orbit/` の理論背景セクションに「思想層バックボーン」小セクション新設

**ブラッシュアップ案：**
> **「Orbit 月次強化は、Bandura 2000 の Collective Efficacy を時間軸で維持・強化する設計。月次引力レポートは『集合的効力感の月次測定 → 改善』の継続装置」**

---

## 2. Gravity TOP 信用層 数字更新（141 → 164 本）

**現状（260510 朝反映済）：**
> 「16 年の実務経験 ＋ 約 600 本の学術論文を精査・141 本を引用統合」

**Phase 9 反映後（260510 夜更新）：**
> **「16 年の実務経験 ＋ 約 670 本の学術論文を精査・164 本を引用統合」**

または以下の進化版：
> **「16 年の実務経験 ＋ Bandura 効力感理論を中核に約 670 本の学術論文を精査・164 本を引用統合した独自フレーム」**

**追加すべき OD 5 系列リストへの **Bandura 系列 3 大古典**追加：**
- 既存：Kotter / Bushe-Marshak / NTL / Cooperrider / Beer-Nohria
- 追加：**Bandura（Stanford）**── Self-Efficacy 1977（49,507 cites）+ Collective Efficacy 2000

**追加すべき主要引用 4 件 → 6 件：**
- 既存：Bauer 2007 / Saks 2006 / Saks-Gruman 2018 / Cooper-Thomas/Anderson 2006
- 追加：**Bandura 1977**（49,507 cites）/ **Sampson 1997 Science**（8,583 cites）

---

## 3. 自己紹介 SSOT 修正（Sampson 1997 追加）

**反映先：** `memory/user_self_intro_attractor_designer_260430.md`

**追加内容：**
> **「30 年以上、組織の引力 ── 人が集まり、活きる力を設計してきた」軸の学術的バックボーン：**
> **Sampson, Raudenbush & Earls (1997) Science**（被引用 8,583）が示した **コミュニティ Collective Efficacy 理論** = 街・地域の「人が集まる力」「離れない力」「活きる力」を多層的に説明する理論。**和歌山（45 年連続人口流出）vs 流山（6 年連続流入 1 位）の対比** = コミュニティ Collective Efficacy の差として学術的に説明可能。

---

## 4. WhitePaper V10 第 6.5 章 新規執筆（Phase 9 主軸）

**章タイトル：** 自己効力感 → 集合的効力感への翻訳機構 ── Gravity 引力経営の最終目標

**構成案（5 セクション）：**

### §6.5.1 Bandura Self-Efficacy 理論（1977 起点）
- D-1 Bandura 1977 / D-2 Stajkovic-Luthans 1998 / D-3 OD 版

### §6.5.2 Bandura Collective Efficacy 理論（2000 展開）
- E-1 Bandura 2000 / E-2 Goddard-Hoy 2000 / E-4 Stajkovic-Lee-Nyberg 2009

### §6.5.3 個人 → 集合的への翻訳機構
- E-3 Tasa-Taggar-Seijts 2007 / E-5 Mathieu 2008 / E-6 Taggar-Seijts 2003

### §6.5.4 コミュニティ Collective Efficacy（街・地域）
- F-1 Sampson 1997 Science / F-2 PHDCN / F-3 Norris 2008 / F-4 Sharkey-Faber 2014

### §6.5.5 反論章（誠実な学術姿勢）
- D-7 Vancouver / E-8 文脈依存 / G-1 Vancouver / G-2 測定批判 / G-3 文化横断

### §6.5.6 Gravity の最終目標 = 集合的効力感に満ちた会社
- 章末まとめ：個人 → 組織 → コミュニティの 3 層 Collective Efficacy 階層構造
- 引力経営の究極形を Bandura 理論で言語化

---

## 5. 商談資料 v0.4 → v0.5 化（Phase 9 反映）

**追加セクション：**

### §Bandura 効力感理論バックボーン（権威性訴求）

**商談時の主軸メッセージ：**
> 「Gravity の理論的バックボーンは Bandura（Stanford・心理学界の不朽の古典）の Self-Efficacy 理論（1977・49,507 cites）+ Collective Efficacy 理論（2000）です。識学さんは『管理の科学』ですが、Gravity は『**Bandura 効力感理論を企業向けに直接実装する唯一のサービス**』として位置付けられます」

### §識学差別化の最終形（Phase 8 → Phase 9 で決定的進化）

| 軸 | Gravity | 識学 |
|---|---|---|
| 変革理論 | Beer-Nohria E+O 統合 | E 単独 |
| 中間管理職 | Raelin エンパワメント 4 条件 | 実行者扱い |
| 失敗回避 | Jones-Schenk + Kotter 5+8 失敗回避 | 失敗放置 |
| OD 実装 | 5 系列統合 | 単一権威担ぎ |
| **🔥 理論的バックボーン** | **Bandura 効力感理論直接実装**（個人 → 集合的への翻訳機構）| 管理の科学（Self-Efficacy 概念なし） |

---

## 6. アーカイブ運用（Phase 9 採用 21 件のうち）

**全件「思想層補強引用」として採用済 → アーカイブなし。**

ただし以下は「補注レベル」として WhitePaper 第 6.5 章のみ活用：
- D-3 Stajkovic-Luthans 1998 OD（実務翻訳補強）
- D-4 Bandura 1978 ABRT 続編
- D-5 Bandura-Adams 1977 CTR
- F-2 PHDCN データセット
- F-4 Sharkey-Faber 2014（経済成果）

---

## 7. 反映スケジュール（本日中継続）

| 優先 | タスク | タイミング | 状態 |
|---|---|---|:-:|
| 🔥 P0 | Gravity TOP 信用層数字更新（141→164 + Bandura 追加）| 本日（5/10）| ⏳ |
| 🔥 P0 | /service/ 軽量サマリ数字更新 | 本日 | ⏳ |
| 🔥 P1 | LP 4 件「思想層バックボーン」セクション追加（CODE / Cultivate / Coaching / Orbit）| 本日 | ⏳ |
| 🔥 P1 | Scan LP「思想層バックボーン」セクション追加 + generate.php に Bandura 2000 追加 | 本日 | ⏳ |
| P2 | Shift R LP「思想層バックボーン」追加 | 本日 | ⏳ |
| P2 | 商談資料 v0.4 → v0.5 化（§Bandura 効力感理論バックボーン追加）| 本日 | ⏳ |
| P3 | 自己紹介 SSOT 修正（Sampson 1997 追加）| 本日 | ⏳ |
| P3 | WhitePaper V10 第 6.5 章草案 v0.1 新規執筆 | 本日 | ⏳ |
| P3 | 09_会社OS 商品_5サービス詳細.md「Phase 9 反映」セクション追加 | 本日 | ⏳ |

---

## 8. 関連ファイル

- 引用ライブラリ v4.0：`04_GrowthFix/02_マーケティング/260510_Gravity_論文引用ライブラリ_v4.0_Phase9追加.md`
- Phase 9.1 マッピング：`02_セッション記録/論文リサーチ/260510_Phase9_学術領域マッピング_自己集合的効力感_v0.1.md`
- Phase 9.2 候補論文：`02_セッション記録/論文リサーチ/260510_Phase9_候補論文リスト_v0.1.md`
- Phase 7-8 統合方針書：`04_GrowthFix/01_サービス設計/260510_Phase7_L2サービスブラッシュアップ_統合方針書_v1.0.md`
- 関連 SSOT：`05_プロダクト/_共通/260510_Gravity_3軸_集まる躍動留まる_SSOT_v1.0.md`
- 関連 SSOT：`05_プロダクト/_共通/SSOT_Engagement指標定義.md`
