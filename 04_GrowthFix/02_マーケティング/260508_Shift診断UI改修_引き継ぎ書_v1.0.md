# Shift 診断 UI 改修 引き継ぎ書 v1.0

> **ミッション：** Gravity Shift 診断 UI（`/gravity-shift/diagnose/`）を、260430 Scan リブート + 採用基盤実装書 12 要素 SSOT に整合させる。
> **発生経緯：** 2026-05-07 夜の LP SSOT 整合チェック（13 LP 並列実装）で、診断 UI のみ機械的修正不可レベル（構造変更）と判定されエスカレーション。本セッションで Step A/B（軽微 + リライト）は処理済み、本書は Step C 専用。
> **位置付け：** 引き継ぎ書 v1.0（既存・19 タスク）の **TASK-2 R/C 営業資料 v0.2** の関連タスク。診断 UI は Shift R/C/Full 受講前提のオペレーション基盤で、Phase 1 採用市場集中軸の根幹。
> **作成：** 2026-05-07 夜（Opus メインスレッド）
> **実行者：** 次セッション Opus（思想判断）+ lp-implementer 別 Node（実装）

---

## 0. 必読 SSOT（実行前に Read 必須）

| # | ファイル | 用途 |
|:-:|---|---|
| 1 | `09_会社OS/公開/ガイドライン/商品.md` | 5 サービス・採用 4 軸・面接ブループリント 5 要素 vs 採用基盤実装書 12 要素 |
| 2 | `05_プロダクト/_共通/SSOT_用語と定義.md` | 廃止用語・公開語彙 |
| 3 | `memory/project_scan_reboot_260430.md` | Scan リブート（Pre-Shift 適合診断・組織引力 4 型）|
| 4 | `memory/project_shift_rc_specs_260501.md` | Shift R/C 仕様（Week 1-2 12 要素・3 ヶ月予言の書）|
| 5 | `memory/project_shift_rc_field_validation_260501.md` | フィールド検証 33 ファイル分析 |

---

## 1. 改修対象ファイル

| # | ファイル | 行数 | 主な BP/旧構造言及 |
|:-:|---|:-:|---|
| 1 | `05_プロダクト/GravityShift/診断_本番/index.html` | 742 | line 242-275（BP受講確認 UI）／line 311（STEP_NAMES）／line 563（toast）|
| 2 | `05_プロダクト/GravityShift/診断_本番/hearing-ceo.html` | 528 | line 155, 254-261, 311（BP翻訳マップの組織文脈化 STEP）|
| 3 | `05_プロダクト/GravityShift/診断_本番/hearing-exec.html` | 528 | line 152, 261-272, 325（翻訳マップ実装確認 + BP意見 STEP）|
| 4 | `05_プロダクト/GravityShift/診断_本番/api/generate-gap.php` | (要調査) | line 4, 88-136（BP参照データ取得）／line 163, 235, 255, 266-323（プロンプト全体）|

---

## 2. SSOT 違反パターン（2 大論点）

### 2.1 論点 A：BP → Scan/CODE 全体リネーム（260430 リブート反映）

**経緯：**
- 旧設計：「BP（採用口説きブループリント v6.0）」が Shift Week 1-2 の参照データ
- 260430 夕：Blueprint v6.0 廃止 → Gravity Scan（組織引力タイプ診断・Pre-Shift 適合診断）にリブート
- 個人引力タイプ解読は Gravity CODE（既存）が担う
- 現行参照は「**CODE 翻訳マップ + Scan 組織引力診断**」の 2 層

**リネームマップ：**

| 旧表記 | 新表記 |
|---|---|
| BP / Blueprint | Scan + CODE（文脈で使い分け）|
| BP受講済み | Scan 受講済み |
| BP翻訳マップ | CODE 翻訳マップ（個人引力タイプ）／ Scan 組織診断結果 |
| BP v6.0 レポート | Scan レポート + CODE レポート |
| BP結果URL | Scan 結果URL（または CODE 結果URL）|
| BP組織文脈化 | CODE翻訳マップの組織文脈化 ＋ Scan 組織診断との突合 |
| BPで取得済み | CODE/Scan で取得済み |
| BP再診推奨 | CODE 再診推奨（個人引力タイプ）／ Scan 再診推奨（組織診断）|
| BPセッション実施日 | Scan セッション実施日 |
| Whyズレ型（BP再診推奨）| Whyズレ型（CODE 再診推奨）|

**思想判断ポイント（Opus 必須）：**
- CEO 側の参照データソースを「CODE」「Scan」のどちらに割り付けるか
- 個人引力タイプ → CODE（既存）／組織引力 4 型 → Scan（260430 新規）
- generate-gap.php のプロンプト構造を「個人軸（CODE）×組織軸（Scan）×幹部証言」の 3 角形に再設計するか、「Scan 結果＋幹部証言」の 2 軸に簡素化するか

### 2.2 論点 B：面接ブループリント 5 要素 → 採用基盤実装書 12 要素

**経緯：**
- 旧設計：BP v6.0 で「面接ブループリント 5 要素」（採用基準・口説きフレーズ 5 種・期待値ギャップの事前握り・入社後 3 ヶ月評価・幹部同席設計）
- 260501 確定：Shift R Week 1-2 で「**採用基盤実装書 12 要素**（思想 3 / 設計 4 / 運用 5）」に拡張

**12 要素構成（project_shift_rc_specs_260501.md より）：**
- 思想 3：① 採用 Why ／ ② AI 時代採用論 ／ ③ 採用ペルソナ整合
- 設計 4：④ 採用 4 軸 ／ ⑤ 採用基準 ／ ⑥ 面接プロセス ／ ⑦ 採用後評価軸
- 運用 5：⑧ 幹部役割分担 ／ ⑨ 口説きフレーズ ／ ⑩ 期待値ギャップ事前握り ／ ⑪ 入社後 3 ヶ月評価 ／ ⑫ Week 0 体験設計

**リネームマップ：**

| 旧表記 | 新表記 |
|---|---|
| 面接ブループリント 5 要素 | 採用基盤実装書 12 要素 |
| 採用基準・口説きフレーズ 5 種・期待値ギャップの事前握り・入社後 3 ヶ月評価・幹部同席設計の 5 要素 | 採用基盤実装書 12 要素（思想 3 / 設計 4 / 運用 5）|
| 5 要素を共同制作 | 12 要素を共同制作 |
| BP翻訳マップ＋面接ブループリント 5 要素 | CODE 翻訳マップ＋ Scan 組織診断＋採用基盤実装書 12 要素 |

**思想判断ポイント（Opus 必須）：**
- 12 要素を全て診断 UI で問うと工数膨張 → 重点 5 要素に絞るか、全 12 要素を網羅するか
- 幹部 hearing 質問の数を増やすか（現行 Q10-Q12 の 3 問）
- AI プロンプト（generate-gap.php）の参照軸を 12 要素に拡張すると出力長が膨張するため、レポート構造の見直しが必要

---

## 3. 改修ステップ（Opus + lp-implementer 連携）

### Phase 1：Opus 思想判断（次セッション冒頭・60-90 分想定）

**論点 A：CEO 側参照データソース割り付け**
- 選択肢 1：CODE = 個人軸 ／ Scan = 組織軸（2 軸並立・推奨）
- 選択肢 2：Scan のみ参照（CODE は前提扱い・簡素化）
- 選択肢 3：3 角形（CODE × Scan × 幹部証言）

**論点 B：12 要素網羅 vs 重点絞り込み**
- 選択肢 1：全 12 要素を診断 UI で網羅（工数膨張）
- 選択肢 2：重点 5 要素に絞る（採用 4 軸＋ Week 0 体験設計など）
- 選択肢 3：CEO hearing は思想 3 ＋設計 4 の 7 要素／幹部 hearing は運用 5 要素

**論点 C：generate-gap.php プロンプト構造**
- 旧：BP翻訳マップ vs 組織実態（2 軸）
- 新案：CODE 翻訳マップ × Scan 組織診断 × 幹部証言（3 軸）／レポート構造の影響範囲

**論点 D：Whyズレ型判定の再診推奨先**
- 旧：「Whyズレ型 → BP再診推奨」
- 新案：「Whyズレ型 → CODE 再診推奨 ＋ Coaching 並行推奨」（Why 揺らぎは Coaching の領域）

### Phase 2：lp-implementer 実装（別 Node・3-5 時間想定）

Opus が論点 A-D を確定したら、以下のプロンプトで lp-implementer に投げる：

```
GravityShift 診断 UI の 260430 Scan リブート + 採用基盤実装書 12 要素対応リネーム。
Opus メインスレッドで方針確定済み（引き継ぎ書 §3 Phase 1）。実装のみ。

## 対象ファイル
1. /Users/ishiinobuyuki/Documents/Obsidian Vault/05_プロダクト/GravityShift/診断_本番/index.html
2. /Users/ishiinobuyuki/Documents/Obsidian Vault/05_プロダクト/GravityShift/診断_本番/hearing-ceo.html
3. /Users/ishiinobuyuki/Documents/Obsidian Vault/05_プロダクト/GravityShift/診断_本番/hearing-exec.html
4. /Users/ishiinobuyuki/Documents/Obsidian Vault/05_プロダクト/GravityShift/診断_本番/api/generate-gap.php

## 確定方針（引き継ぎ書 §3 Phase 1 で確定）
- 論点 A：[Opus が選択した割り付け方針を記載]
- 論点 B：[Opus が選択した要素絞り込み方針を記載]
- 論点 C：[Opus が選択したプロンプト構造を記載]
- 論点 D：[Opus が選択した Whyズレ型再診推奨先を記載]

## リネームマップ（引き継ぎ書 §2.1 / §2.2 のマップに従う）
[省略・引き継ぎ書を参照]

## 実行手順
1. 4 ファイル全て一気通貫リネーム（grep で BP/Blueprint 残存ゼロまで反復）
2. STEP_NAMES 配列・section-label・q-text 全更新
3. generate-gap.php のプロンプト構造を論点 C 方針通りに再設計
4. FTP デプロイ：4 ファイル全て /growthfix.jp/public_html/gravity-shift/diagnose/ 配下
5. ローカル動作確認は不可（PHP 環境）→ 本番デプロイ後にブラウザで動作確認
6. worklog 追記
```

### Phase 3：本番動作確認（Opus + ユーザー）

- ブラウザで `https://growthfix.jp/gravity-shift/diagnose/` を開いて全 STEP 通し確認
- CEO hearing → Exec hearing → analyze → レポート生成の一連フローを 1 ケース通す
- generate-gap.php の AI プロンプト出力をサンプルで検証
- 不整合発見時は Opus 直接 Edit で軽微修正

---

## 4. エスカレーション基準（Phase 2 中）

lp-implementer が以下に該当した場合は Phase 1 に戻して Opus 再判断：

- リネームによって診断ロジックが破綻する箇所（CEO/Exec の参照データ突合ロジック）
- 12 要素導入で診断 UI の STEP 数が大幅増加し、UX 破綻
- generate-gap.php のプロンプト長が token 上限に到達
- レポート構造（generate-report.php / generate-report_v2.php）にも変更が及ぶ場合

---

## 5. 完了基準

- [ ] 4 ファイルから「BP」「Blueprint」「面接ブループリント 5 要素」が完全消失（grep で残存ゼロ）
- [ ] STEP_NAMES 配列が CODE/Scan ベースに更新済
- [ ] generate-gap.php のプロンプトが論点 A-D 方針通りに再設計済
- [ ] 本番ブラウザで全 STEP 通し動作確認 PASS
- [ ] 1 サンプルケースで AI プロンプト → レポート生成が完走
- [ ] worklog 完了記録
- [ ] `bash 06_開発/scripts/lint_consistency.sh` 全 PASS

---

## 6. FTP 認証情報

```
USER:   xs992119
PASS:   cgq1fv99
SERVER: ftp://sv16489.xserver.jp
BASE:   /growthfix.jp/public_html/gravity-shift/diagnose/
```

---

## 7. 関連ファイル

- LP SSOT 整合チェック引き継ぎ書（13 LP 並列実装の元）：`260507_LP_SSOT整合チェック_引き継ぎ書_v1.0.md`
- 既存引き継ぎ書 v1.0（19 タスク）：`260507以降_タスク引き継ぎ書_v1.0.md`
- worklog：`04_GrowthFix/04_デイリーログ/2605_work_log.md`
- Shift R/C 仕様 SSOT：`memory/project_shift_rc_specs_260501.md`
- Scan リブート SSOT：`memory/project_scan_reboot_260430.md`

---

## 8. コピペ用プロンプト（次セッション冒頭で使用）

### Phase 1（Opus 思想判断）開始用：

```
260508_Shift診断UI改修_引き継ぎ書_v1.0.md を Read して、
§3 Phase 1 の論点 A-D（4 つの思想判断）を順番に提示してください。
私（石井）と対話で 1 論点ずつ確定します。
全 4 論点が確定したら、§3 Phase 2 のコピペ用プロンプトに方針を埋め込んで、
lp-implementer 別 Node で実装フェーズに移ります。
```

### Phase 2（lp-implementer 実装）起動用テンプレ：

```
Agent({
  subagent_type: "lp-implementer",
  description: "Shift 診断 UI 全面リネーム",
  prompt: "
    260508_Shift診断UI改修_引き継ぎ書_v1.0.md §3 Phase 2 の確定方針に従って、
    4 ファイル（index.html / hearing-ceo.html / hearing-exec.html / api/generate-gap.php）の
    全面リネームを実施してください。
    
    確定方針：
    - 論点 A：[Phase 1 で確定した割り付け方針]
    - 論点 B：[Phase 1 で確定した要素絞り込み方針]
    - 論点 C：[Phase 1 で確定したプロンプト構造]
    - 論点 D：[Phase 1 で確定した Whyズレ型再診推奨先]
    
    リネームマップは引き継ぎ書 §2.1 / §2.2 を参照。
    実行手順は引き継ぎ書 §3 Phase 2 を参照。
    エスカレーション基準は §4 を参照。
  "
})
```

### Phase 3（動作確認）開始用：

```
260508_Shift診断UI改修_引き継ぎ書_v1.0.md §3 Phase 3 に従って、
本番ブラウザで動作確認します。
私が https://growthfix.jp/gravity-shift/diagnose/ を開いて
1 ケース通すので、不整合発見時に修正提案してください。
```
