# Orbit 月次引力レポート — 入力 JSON スキーマ定義

**対象スクリプト：** `06_開発/scripts/orbit_monthly_report.py` / `orbit_quarterly_review.py`
**バージョン：** v1.0（Phase 1）
**最終更新：** 260512

---

## ファイル命名規則

```
orbit_data/<CLIENT_ID>_<YYYY-MM>.json
```

例:
- `orbit_data/sample_orbit_client_2026-05.json`（当月）
- `orbit_data/sample_orbit_client_2026-04.json`（前月）

---

## スキーマ全体

```json
{
  "client_id": "sample_orbit_client",
  "month": "2026-05",
  "previous_month": "2026-04",
  "gravity_scores": {
    "current": {
      "recruitment_pipeline":  "○",
      "final_decline_rate":    "△",
      "talent_retention":      "○",
      "executive_voice":       "△",
      "engagement":            "○",
      "departure_signal":      "△",
      "recruitment_wall_pof":  "○",
      "psych_safety_cost":     "△"
    },
    "previous": {
      "recruitment_pipeline":  "△",
      "final_decline_rate":    "△",
      "talent_retention":      "△",
      "executive_voice":       "×",
      "engagement":            "△",
      "departure_signal":      "×",
      "recruitment_wall_pof":  "△",
      "psych_safety_cost":     "×"
    }
  },
  "alpha_beta_gamma_delta_actions": [
    {"axis": "R-α", "action": "採用メッセージの Why 軸を経営者の言語で再設計", "priority": "high"},
    {"axis": "C-β", "action": "1on1 頻度を隔週→毎週に引き上げ・アジェンダ標準化", "priority": "high"},
    {"axis": "C-γ", "action": "エンゲージメントサーベイ設問を引力 8 項目に対応させる", "priority": "medium"},
    {"axis": "R-δ", "action": "最終面接フォローアップ連絡を 24h 以内に統一", "priority": "medium"}
  ],
  "departure_signals": {
    "physical":      "△",
    "facial":        "○",
    "overload":      "△",
    "meaning":       "○",
    "relationships": "○"
  },
  "memo": "自由記述（月次コメント・共有事項等）"
}
```

---

## フィールド定義

### トップレベル

| フィールド | 型 | 説明 |
|---|---|---|
| `client_id` | string | クライアント識別子（英数字・アンダースコア）|
| `month` | string | 当月（YYYY-MM 形式）|
| `previous_month` | string | 前月（YYYY-MM 形式）|
| `gravity_scores` | object | 引力 8 項目スコア（current / previous）|
| `alpha_beta_gamma_delta_actions` | array | 改善提案リスト（α/β/γ/δ マッピング）|
| `departure_signals` | object | 離職予兆 5 シグナルスコア |
| `memo` | string | 自由記述（省略可）|

---

### gravity_scores.current / previous — 引力 8 項目

SSOT `05_プロダクト/_共通/SSOT_用語と定義.md` §13.1 準拠（v0.4・7→8 項目化済）

| キー | 対応項目（SSOT §13.1）| 軸 |
|---|---|---|
| `recruitment_pipeline` | ① 採用パイプライン | 集まる |
| `final_decline_rate` | ② 最終面接辞退率 | 集まる |
| `talent_retention` | ③ 優秀人材定着率 | 躍動 |
| `executive_voice` | ④ 幹部発話量 | 躍動 |
| `engagement` | ⑤ エンゲージメント | 躍動 |
| `departure_signal` | ⑥ 離脱予兆 | 躍動 |
| `recruitment_wall_pof` | ⑦ 採用最大壁の自覚度 + PO Fit 認識 | 集まる |
| `psych_safety_cost` | ⑧ 心理的安全性 4 行動 + 採用コスト対効果 | 躍動 |

**集まる軸（①②⑦）= 3 項目 / 躍動軸（③④⑤⑥⑧）= 5 項目**

**スコア値（4 段階）：**

| 記号 | 数値 | 意味 |
|---|---|---|
| `◎` | 4 | 良好・課題なし |
| `○` | 3 | 概ね良好・軽微な課題あり |
| `△` | 2 | 要改善・具体的な課題あり |
| `×` | 1 | 要緊急対応・リスク水準 |

---

### alpha_beta_gamma_delta_actions — 改善提案リスト

| フィールド | 型 | 説明 |
|---|---|---|
| `axis` | string | α/β/γ/δ マッピング軸（例: `R-α`, `C-β`）|
| `action` | string | 改善提案の具体的な行動 |
| `priority` | string | `high` / `medium` / `low` |

**Phase 0 運用:** JSON 入力テキストをそのままレポートに貼り付け。自動マッピングロジックは Phase 1 実装予定。

---

### departure_signals — 離職予兆 5 シグナル

SSOT `09_会社OS/商品.md`「離職予兆 5 シグナル KPI」準拠

| キー | シグナル | 観察ポイント |
|---|---|---|
| `physical` | 身体シグナル | 遅刻・欠勤・体調不良の頻度変化 |
| `facial` | 表情シグナル | 会議・1on1 での表情・発話量変化 |
| `overload` | 過負荷シグナル | 残業・週末対応・タスク滞留 |
| `meaning` | 意味付けシグナル | 仕事への意義言語化・質問の変化 |
| `relationships` | 人間関係シグナル | チーム間コミュニケーション密度変化 |

スコア値は gravity_scores と同じ 4 段階（◎/○/△/×）を使用。

---

## Phase 1 実装済（260512）

1. **Score IntEnum 化**（`orbit_monthly_report.py` — M-1 解消。`◎/○/△/×` の定義は `Score` クラスに集約）
2. **α/β/γ/δ 自動マッピング**（`orbit_actions_map.json` の 16 ルールでスコアパターン → 提案を自動生成）
   - `alpha_beta_gamma_delta_actions` が JSON に存在すれば手動入力を優先（下位互換維持）
3. **過去 6 ヶ月時系列グラフ**（`--trend` フラグで `_trend.png` を出力）
4. **PDF 出力サポート**（`--pdf` フラグ + `reportlab` がある場合に A4 3p PDF を出力）
5. **orbit_quarterly_review.py 新設**（四半期 4 型再判定書 A4 5p を自動生成）

## Phase 2 残課題（本番顧客投入時）

1. `gravity_scores.current` の数値直接入力サポート（定量データ連携）
2. 顧客別ベンチマーク比較（同業他社匿名平均との差分）
3. `orbit_actions_map.json` ルールの実顧客フィードバックによる精緻化（ルール増設・優先度調整）
