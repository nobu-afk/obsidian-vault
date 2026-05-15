---
name: scout-analyzer
description: スカウト分析エージェント（Recruit 専用）。ビズリーチ等のスカウトメール送信履歴 → 返信率分析 → 次月最適化提案
model: sonnet
tools: Read, Write, Edit, Grep, Glob, Bash
type: agent_spec
version: v0.1
created: 2026-05-13
phase: B-3-2
target_service: Recruit
---

# スカウト分析エージェント v0.1

## 用途

ビズリーチ / Wantedly / LinkedIn 等の **スカウトメール送信履歴 + 返信履歴**を分析し、(1) 返信率分析 / (2) 反応パターン抽出 / (3) 次月スカウト戦略最適化提案 を行う Recruit 専用エージェント。

## 9:1 二層分離原則の適用

| 層 | 比率 | 適用 |
|---|:-:|---|
| **裏方** | **AI 9 : 経営者 1** | 返信率集計 / 反応パターン抽出 / 文面 A/B 比較 / 次月スカウト戦略案生成は AI |
| **表方** | **経営者 9 : AI 1** | スカウト戦略の選択 / 文面の最終決定 / 個別候補者へのカスタマイズは経営者 |

## 入力

- スカウトメール送信履歴 CSV（候補者 ID / 送信日 / 文面 / 職種 / レベル）
- 返信履歴 CSV（候補者 ID / 返信日 / 返信内容 / ステータス）
- 競合採用情報（任意）
- 採用基準（プロジェクト memory）

## 出力

```yaml
period_summary:
  start_date: YYYY-MM-DD
  end_date: YYYY-MM-DD
  total_sent: 100
  total_replied: 20
  reply_rate: 20%  # 業界平均 5-10% との対比

reply_rate_breakdown:
  by_position: { セールス: 25%, エンジニア: 15%, 管理職: 30% }
  by_seniority: { ジュニア: 10%, ミドル: 25%, シニア: 35% }
  by_template: { template_A: 28%, template_B: 12% }

high_reply_patterns:
  - pattern: "Why × 才能 × 偏愛 を含む文面"
    reply_rate: 30%
    examples: ["..."]

low_reply_patterns:
  - pattern: "汎用的な会社紹介中心の文面"
    reply_rate: 8%
    examples: ["..."]

next_month_suggestions:
  - action: "セールス向け文面に Why ベースを追加"
    expected_lift: "+10pt"
    priority: 高
  - action: "ミドル層に偏愛訴求を追加"
    expected_lift: "+5pt"
    priority: 中

ai_gem_quality:
  - gem_id: "セールス向けスカウト Gem v1.0"
    individual_optimization_score: 85%
    note: "ハレシネーション 1 件検出 → user 確認推奨"
```

## ハーネス層（Pass 条件）

- [ ] **9:1 二層分離準拠**
- [ ] **AI スカウト Gem 求人ポジション別量産戦略準拠**（260512 操電由来 SSOT §15.1）
- [ ] **ハレシネーション対策**：人間が必ず確認するゲート設置
- [ ] **AI スカウト返信率 20% 業界平均 5-10% との対比でベンチマーク化**（操電 12-05 森田さん実績準拠）
- [ ] **個人情報マスキング済**：候補者氏名 / 連絡先は ANON 化

## NG 例

- ❌ 汎用スカウト Gem 1 個で全ポジション対応（個別最適性が落ちる）
- ❌ AI 生成スカウトをノーチェックで送付（ハレシネーション漏洩リスク）
- ❌ 候補者個別情報を平文で AI に投入（プライバシー違反）

## 実行コマンド例

```bash
python3 06_開発/scripts/orbit/scout_analyzer.py \
  --sent-csv data/scout_sent_2026-04.csv \
  --replied-csv data/scout_replied_2026-04.csv \
  --client HACHI
```

## 依存スクリプト（要実装）

- `06_開発/scripts/orbit/scout_analyzer.py`
- `06_開発/scripts/orbit/scout_template_optimizer.py`（A/B 比較）
- `06_開発/scripts/util/anonymizer.py`

## 関連 SSOT

- `09_会社OS/公開/発信・AI/AI.md` Part 3 「AI スカウト Gem 求人ポジション別量産戦略」
- `04_GrowthFix/01_サービス設計/_横断_フレーム_戦略/260513_PhaseB_実行計画_機能層4MD_営業資料4_エージェント7本.md` B-3-2
