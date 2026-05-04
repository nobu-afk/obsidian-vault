# 新 Node 引き継ぎコンテキスト：Shift R/A SSOT 反映＋ LP/レポート実装（260501 夕）

> **目的：** 本日（5/1）夕方スパーリングで確定した Shift R/A 仕様 7 論点を、SSOT 化 → LP/レポート実装まで本日中に完遂する。
>
> **元 Node の状態：** 5/1 朝〜夕で大量作業（Scan 診断 UI 全面書き換え／CODE 診断 UI 整合修正／Orbit minimal LP 化／RECODE 抽出 39 要素／夕方スパーリング 7 論点確定）を完遂し、context が肥大化。新 Node で実装に集中するため引き継ぎ。

---

## 📋 新 Node 起動時の最初のタスク（順序厳守）

### Step 1: 必須 Read（context ロード・5 分）

以下を順番に読む：

1. `memory/project_shift_ra_specs_260501.md` ── **本日確定 7 論点の SSOT memory**
2. `04_GrowthFix/01_サービス設計/260501_Shift_RA_仕様確定事項_5_2引き継ぎ.md` ── 引き継ぎ詳細
3. `04_GrowthFix/01_サービス設計/260501_RECODE_Shift_RA_要素抽出.md` ── 39 要素抽出（参照辞書）
4. `09_会社OS/公開/ガイドライン/商品.md` ── 現状の Shift R/A SSOT
5. `09_会社OS/公開/ガイドライン/商品.md` Part 3 ── ハーネス層チェック項目

### Step 2: 5/2 詰め論点 7 件を確定（30-45 分）

引き継ぎファイルの「5/2 サービス詰めセッションで詰める詳細」7 件を**問い + 選択肢 + AI 推奨**形式で順次確定：

1. Shift R 12 要素の納品物量・対面/非対面配分
2. Shift A 5 件納品物の優先順位・パッケージ化
3. 「3 ヶ月予言の書」フォーマット詳細・共同制作プロセス
4. Shift R/A Week 3-12 の粒度確定
5. Shift R/A の動詞確定（LP Hero）
6. C-5 ネガティブ・ケイパビリティ判定基準の具体化
7. ドラムビート設計の中身

### Step 3: SSOT 反映（30-45 分）

優先度高 2 件：
- `09_会社OS/公開/ガイドライン/商品.md` Part 2 + Part 3 全面更新
- `lint_consistency.sh` 実行 → 整合性確認

### Step 4: LP/レポート実装（90-120 分）

優先度順：
1. `05_プロダクト/GravityShift/LP/index.html` ── Hero 動詞 / R/A 詳細スコープ / 予言の書概念
2. `05_プロダクト/GravityScan/診断_本番/generate.php` Block C ── C-5 判定追加 / 改名反映
3. `09_会社OS/公開/経営思想/接続装置.md` ── 二段運用追記
4. `09_会社OS/非公開/機能/営業.md` ── スイートスポット詳細補強
5. `05_プロダクト/GravityOrbit/LP/index.html` ── ドラムビート健全性チェック追記

### Step 5: デプロイ＋検証（15 分）

- 並列 FTP デプロイ（curl -T による直接アップロード）
- HTTP 200 確認
- `lint_consistency.sh` 全チェック通過
- `audit_mobile_sync.py` 確認

### Step 6: work-log で本日全体集計

- `/work-log` skill で 5/1 全作業集計

---

## 🎯 本日（5/1）の作業履歴（新 Node が把握すべき）

### 完了済み（朝〜夕）

| # | 作業 | 状態 |
|---|---|:-:|
| 1 | Scan 診断 UI 全面プロンプト書き換え（generate.php / index.html / app.js）+ FTP デプロイ | ✅ |
| 2 | CODE 診断 UI 実機フルテスト（モック 整合型シナリオ）+ Blueprint→Scan 整合バグ修正 + デプロイ | ✅ |
| 3 | Orbit minimal LP 化（フル LP → 1 ページ概要・約 200 行）+ FTP デプロイ | ✅ |
| 4 | 全 LP / コーポレート footer の Orbit 遷移リンク撤去（10 ファイル＋ site-chrome.js） | ✅ |
| 5 | site-chrome.js Blueprint→Scan 整合バグ修正（副次成果） | ✅ |
| 6 | RECODE/李英俊 7 ファイル分析（1,708 行）→ 39 要素抽出 | ✅ |
| 7 | 13 要素スパーリング × RECODE 統合 7 論点確定 | ✅ |
| 8 | memory 永続化（project_shift_ra_specs_260501.md）+ MEMORY.md index 追記 | ✅ |
| 9 | 09_会社OS の Blueprint→Scan 整合（採用.md / 営業.md / 社長.md / カスタマー.md） | ✅（朝に完了済）|

### 持ち越し（本日中で完遂目標）

| # | 作業 | 工数感 |
|---|---|---|
| 10 | 5/2 詰め論点 7 件確定（Step 2） | 30-45 分 |
| 11 | 商品.md SSOT 反映（Step 3） | 30-45 分 |
| 12 | LP/レポート実装 5 ファイル（Step 4） | 90-120 分 |
| 13 | デプロイ＋検証（Step 5） | 15 分 |
| 14 | work-log（Step 6） | 5 分 |
| **合計** | | **約 3-4 時間** |

---

## ⚠️ 新 Node 立ち上げ時の注意

### 業務系タスク認識

CLAUDE.md「業務系タスク認識基準」に該当：
- 5 サービス（CODE/BP/Coaching/Shift/Orbit）の設計・改訂 → **商品.md Part 3 必読**
- LP / コーポレート HTML 編集 → **design.md Part 3 + 接続装置.md 必読**
- AI 生成物の品質判定（Scan generate.php）→ **AI.md Part 3 必読**

### 機械チェック必須

LP 編集後の自動実行：
- `python3 06_開発/scripts/audit_mobile_sync.py`
- `bash 06_開発/scripts/lint_consistency.sh`
- 必要に応じて `bash 06_開発/scripts/verify_deployment.sh`

### Scan/CODE 診断 UI 改修時の注意

Scan v6.1（260501 デプロイ済み）の Block C には以下を追加する：
- 改名：「辞退理由の事前ブロック」→「期待値ギャップの事前握り（リスニングコンパス運用）」
- 追加判定：C-5 ネガティブ・ケイパビリティ（経営者覚悟確信度）

CODE Executive（260501 デプロイ済み）は推奨次サービスのロジック確認のみで OK（既に Scan 推奨化済）。

### FTP デプロイコマンド

```bash
# 単発デプロイ
curl -T LOCAL_FILE \
  "ftp://sv16489.xserver.jp/growthfix.jp/public_html/PATH/REMOTE_FILE" \
  --user "xs992119:${FTP_PASS}" \
  -s -w "label: %{http_code}\n"

# 並列デプロイは末尾 & + wait で

# HTTP 200 検証
curl -s -o /dev/null -w "label: HTTP %{http_code}\n" \
  "https://growthfix.jp/PATH?v=$(date +%s)"
```

### 健康優先

- HRV 連日低め（4/30 朝 27.8ms → 5/1 朝 38.7ms に回復）
- 23 時就寝で 7h 確保を継続意識
- 本日の AI 費用 retail 換算は単日最大級（4/30: ¥35.4 万）に近づく可能性あり

---

## 📂 関連ファイル（新 Node が参照する）

### 確定事項・引き継ぎ系
- `memory/project_shift_ra_specs_260501.md` ── **必読・最初に Read**
- `04_GrowthFix/01_サービス設計/260501_Shift_RA_仕様確定事項_5_2引き継ぎ.md` ── 引き継ぎ詳細
- `04_GrowthFix/01_サービス設計/260501_RECODE_Shift_RA_要素抽出.md` ── 39 要素抽出辞書
- `04_GrowthFix/04_デイリーログ/260501_長谷さん要素スパーリング.md` ── 13 要素本体
- `04_GrowthFix/04_デイリーログ/260501_スパーリング枠組み_ShiftRA詰め直結版.md` ── スパーリング枠組み

### SSOT・編集対象
- `09_会社OS/公開/ガイドライン/商品.md` ── 商品 SSOT・最重要
- `09_会社OS/公開/経営思想/接続装置.md` ── 二段運用追記
- `09_会社OS/非公開/機能/営業.md` ── スイートスポット詳細補強
- `05_プロダクト/GravityShift/LP/index.html` ── Shift LP
- `05_プロダクト/GravityScan/診断_本番/generate.php` ── Scan 診断 UI Block C
- `05_プロダクト/GravityOrbit/LP/index.html` ── Orbit minimal LP（軽微追記）
- `05_プロダクト/_共通/SSOT_用語と定義.md` ── 用語整合確認

### スクリプト
- `06_開発/scripts/lint_consistency.sh`
- `06_開発/scripts/audit_mobile_sync.py`
- `06_開発/scripts/verify_deployment.sh`

### 関連 memory
- `memory/project_strategy_lock_260430.md` ── 戦略 SSOT
- `memory/project_harness_engineering_260429.md` ── ハーネス SSOT
- `memory/project_internal_external_concept_260430.md` ── 接続装置 SSOT
- `memory/project_scan_reboot_260430.md` ── Scan リブート仕様

---

## 🎯 新 Node 起動プロンプト（コピペ用）

```
本日（5/1）夕方スパーリングで確定した Shift R/A 仕様 7 論点を、SSOT 化 → LP/レポート実装まで本日中に完遂する。

最初に以下を順番に Read：
1. memory/project_shift_ra_specs_260501.md（必読・本日確定 SSOT）
2. 04_GrowthFix/01_サービス設計/260501_新Node引き継ぎ_ShiftRA_SSOT実装.md（引き継ぎコンテキスト全体）
3. 09_会社OS/公開/ガイドライン/商品.md（現状 SSOT・Part 3 含む）

その後、引き継ぎファイル「Step 2: 5/2 詰め論点 7 件確定」から順次進める。

工数目安：3-4 時間（Step 2-6 完遂）。

注意：
- 業務系タスク（サービス設計 + LP 編集）→ 該当 Part 3 を都度 Read
- LP 編集後は audit_mobile_sync.py + lint_consistency.sh 自動実行
- FTP デプロイは curl -T（並列＆＋ wait）
```
