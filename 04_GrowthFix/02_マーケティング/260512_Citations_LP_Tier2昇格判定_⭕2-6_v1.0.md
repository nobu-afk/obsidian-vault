> **Citations LP Tier 2 昇格判定（⭕ #2-#6）v1.0**
> **判定日：** 2026-05-12（Task 59 実装）
> **判定対象：** 2605_pickup §推奨 ⭕#2-#6（5 件）
> **判定者：** 石井 伸幸（Claude Code 起票・user 承認後 W22 で LP 反映）
> **関連：** `08_情報収集/AI_papers_inbox/2605_pickup.md` ／ `05_プロダクト/Citations/LP/index.html`（1,369 行・本番稼働）

---

## §1 判定原則（再確認）

- **Tier 1（7 本柱）：** 累計 14,897 cites・引力経営の根幹 → 固定。新規昇格は原則しない
- **Tier 2（サービス別 主要論文・フィルター 41 件）：** 査読誌掲載 + サービス軸（Recruit/Cultivate/Coaching/Orbit/Scan/CODE/思想層）の主要論文
- **Tier 3（完全リスト 253 件）：** 査読論文 + 重要な業界一次ソース。網羅性重視
- **不適格：** HBR 記事 / 一般メディア / 業界レポート単体 = 営業資料 / Note 素材としては有用、Citations LP には載せない

---

## §2 判定マトリクス（⭕#2-#6）

| # | 論文 | 査読 | 直近性 | サービス軸接続 | 既存 SSOT 強度 | 判定 |
|---|---|---|---|---|---|---|
| #2 | arxiv Safety First（2026/2・n=2,257） | ❌ 未査読（arxiv preprint）| ✅ 2026/2 | ✅ Cultivate C-2 / 思想層（Edmondson 直系）| ✅ 強い（Edmondson 1999 既掲載）| **🟢 Tier 2 昇格適格**（"未査読・最新実証" 表示）|
| #3 | HBR Erodes Trust（2026/02）| ❌ HBR 記事 | ✅ 2026/02 | △ Coaching 参考 | — | **🔴 Citations LP 不適格** → Note Vol.10 素材 |
| #4 | Anthropic Labor Market（2026/3）| ❌ 企業リサーチ | ✅ 2026/3 | △ AI / 思想層 | — | **🟡 Tier 3 完全リスト追加候補**（"一次ソース・企業リサーチ" 注記）|
| #5 | Nature SR Attrition（2026）| ✅ Nature SR | ✅ 2026 | ✅ Orbit / Cultivate 離職予兆 | ✅ 強い（既存 Orbit SSOT 補強）| **🟢 Tier 2 昇格適格** |
| #6 | OECD SME（2024/12）| ❌ 国際機関統計 | △ 2024/12 | △ 営業資料統計 | — | **🔴 Citations LP 不適格** → 営業資料 §15 |

---

## §3 W22 反映タスク（5/16-5/30）

### Tier 2 昇格（2 件）

**🟢 T59-A：Citations LP Tier 2 に Cultivate カテゴリで追加（#2 arxiv Safety First）**
- **配置位置：** `05_プロダクト/Citations/LP/index.html` L745 付近（Frazier 2017 Psychological safety meta-analytic review の直下）
- **HTML 雛形：**
  ```html
  <div class="paper-item" data-service="cultivate">
    <p class="paper-item-title">Safety First: Psychological Safety as the Key to AI Transformation</p>
    <p class="paper-item-apa">Reich, T., Wolfe, M., Price, D., et al. (2026). <em>arXiv preprint</em>, 2602.23279. <a href="https://arxiv.org/abs/2602.23279" target="_blank" rel="noopener">arxiv.org/abs/2602.23279</a></p>
    <div class="paper-item-meta">
      <span class="cite-badge">n=2,257 / arxiv preprint</span>
      <span class="service-tag">Cultivate C-2</span>
      <span class="service-tag">思想層</span>
    </div>
  </div>
  ```
- **Tier 3 完全リスト（L1030 付近）にも 1 行追加：**
  ```html
  <tr><td class="td-num">254</td><td>Reich et al. (2026)</td><td>Safety First: Psychological Safety as the Key to AI Transformation</td><td>arXiv preprint 2602.23279</td><td class="td-cite">n=2,257</td><td class="td-doi"><a href="https://arxiv.org/abs/2602.23279" target="_blank" rel="noopener">link</a></td><td class="td-axis">C-2 / 思想層 / AI</td></tr>
  ```

**🟢 T59-B：Citations LP Tier 2 に Orbit カテゴリで追加（#5 Nature SR Attrition）**
- **配置位置：** Orbit カテゴリ末尾（Mitchell 2001 Job embeddedness 周辺）
- **HTML 雛形：**
  ```html
  <div class="paper-item" data-service="orbit">
    <p class="paper-item-title">Integrating machine learning and explainable AI for employee attrition prediction in HR analytics</p>
    <p class="paper-item-apa">Author et al. (2026). <em>Nature Scientific Reports</em>, 16, Article 36424. <a href="https://www.nature.com/articles/s41598-026-36424-2" target="_blank" rel="noopener">link</a></p>
    <div class="paper-item-meta">
      <span class="cite-badge">Nature SR 2026</span>
      <span class="service-tag">Orbit</span>
      <span class="service-tag">Cultivate</span>
    </div>
  </div>
  ```
- **Tier 3 完全リストにも 1 行追加（番号 255）**
- **注意：** 著者名は原本確認後に正式記入（現在は "Author et al." 仮）

### Tier 3 のみ追加候補（1 件）

**🟡 T59-C：Anthropic Labor Market 論文を Tier 3 完全リストに追加検討**
- 一次ソース価値は高いが査読論文ではない → Tier 3 末尾「業界一次ソース」セクションを新設するか、現状の Tier 3 末尾に注記付きで追加するかは LP 改修時に判断
- **判断保留：** 5/16 W22 着手時に再判定

### Citations LP 不適格（2 件・別反映先）

**🔴 T59-D：#3 HBR Erodes Trust → Note Vol.10 素材（Task 57 で既処理）**
- 反映先：`03_コンテンツ/note記事連載_事業の伸ばし方/260512_Vol10_..._素材ストック_v0.1.md` §2 補強候補

**🔴 T59-E：#6 OECD SME → 営業資料 §15 強化**
- 反映先：GravityRC 営業資料 v0.4 → v0.5 化時に §15 SMB ターゲット顧客理解パートに具体統計（日本 SME AI 採用率 16%・90% 期待 vs 41% 用途不明）を追記
- 担当タスク：W22 タスクに分離（Task 60 で統合タスクマスター反映）

---

## §4 検証メモ（user 承認後 LP 反映時の注意）

1. **本番 LP 編集後の必須実行：**
   - `python3 06_開発/scripts/audit_mobile_sync.py`
   - `bash 06_開発/scripts/verify_deployment.sh`（デプロイ後）
2. **Tier 2 件数表示更新：** 現在「サービスフィルター 41 件」→ +2 = 「43 件」に description / OG / 本文の数字を同期更新
3. **Tier 3 完全リスト 253 件 → 255 件**：meta description / og:description / h1 直下サブ / 累計 cites 表記（14,897 維持）の同期更新
4. **JS フィルター動作：** `data-service` を `recruit/cultivate/coaching/orbit/scan/thought` のいずれかに正確に揃える（typo すると "All" でしか表示されなくなる）

---

## §5 判定サマリー

- **Tier 2 昇格：2 件**（#2 arxiv Safety First / #5 Nature SR Attrition）
- **Tier 3 追加候補：1 件**（#4 Anthropic Labor Market・W22 で再判定）
- **Citations LP 不適格・別反映先：2 件**（#3 → Note Vol.10 / #6 → 営業資料）
- **次アクション：** W22（5/16-5/30）で T59-A / T59-B を実 LP 反映 → user 承認後デプロイ
