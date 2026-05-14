# `/gravity-scan/` LP 完全変更 引き継ぎ書 v1.0

> **作成日：** 2026-05-14 夕（260514 W22 SCAN 廃止 PJ 当日全完走の続き）
> **対象：** 別 Node（推奨：lp-implementer agent / Sonnet）
> **想定工数：** 2-3h（Sonnet 速度想定）
> **目的：** ローカル LP `05_プロダクト/Gravity/Scan/LP/index.html`（585 行）から **「60 分有料 Scan」前提の残骸 30+ 箇所**を一掃し、**「無料 Web 診断 v2 + 30 分解説セッション + R/C/Orbit 月額」軸**に統一する

---

## 1. 主軸戦略（260514 朝 スパーリング Q1-Q5 確定済・絶対遵守）

| 軸 | 確定内容 |
|---|---|
| **方針** | SCAN 10 万 → **廃止**。組織横断ヒアリングは R/C/Orbit 月額契約の Week 1 オンボに内包 |
| **新仕様** | **無料 Web 診断 v2**（18 問 3 軸 3 分・自動 PDF + 30 分解説セッション同梱）|
| **3 軸** | 集まる × 躍動 × **留まる**（Phase 13 学術 BB 準拠：Mitchell JE / Meyer-Allen / Rousseau / Phase 12 Continuous EC）|
| **LP h1** | 「組織の引力タイプ診断」**前面化**（「無料」は副次）|
| **解説セッション** | 既存 utage URL を流用 → `https://utage-system.com/event/gcfmTRLg7lAq/register` |
| **R/C/Orbit 月額** | Recruit 月 35 万・Cultivate 月 50 万・Orbit 月 15 万・段階移行型 |
| **既存購入者** | そのまま完了扱い（補填なし）|

詳細：`memory/project_scan_abolish_260514.md`

---

## 2. 既に修正済（22-DJ で本番反映済・触らない）

| 箇所 | 修正内容 |
|---|---|
| L6 title | `Gravity Scan ── 組織の引力タイプ診断` |
| L7-14 meta description / og | 18 問 3 分 / 無料 PDF + 30 分 Zoom |
| L37-66 Schema.org | price: "0" / serviceType: 無料 Web 診断 |
| L104-123 Hero | h1「組織の引力タイプ診断」/ 18 問 3 軸 3 分 / 無料 + 30 分 Zoom / CTA `/web-diagnose/` |
| L380-388 bp-price-next 周辺 | CTA「無料診断をはじめる」/ 3 分で月額の方角確定 |
| L414 lp-route-sub--muted | 「10 万割」削除 |
| L549 form-note | 入力 30 秒｜無料 |
| L562-563 lp-consult-lead | Web 診断より深く壁打ち / R/C/Orbit 動線 |

---

## 3. 残存箇所マップ（30+ 箇所・以下を全て修正）

### 3.1 Nav（L77-95・「60 分の流れ」）

- **L79 / L92** `60分の流れ` → `診断の流れ`
- **L83 / L95** `申し込む` → `無料診断を始める`（CTA リンク先は `/web-diagnose/` に変更）

### 3.2 Section 2 Paradox（L150-170・CODE × Scan 対比）

- **L155** `CODE（個人軸・60 分）` → **CODE 60 分は維持**（個人軸対比のため）
- **L162** `Scan（組織軸・60 分・本サービス）` → `Scan（組織軸・無料 Web 診断 v2・18 問 3 軸 3 分 + 30 分解説 Zoom 同梱）`
- **L164** `組織の引力タイプを診断する 60 分。` → `組織の引力タイプを診断する 18 問 3 軸 3 分。詳細解説は 30 分 Zoom で。`

### 3.3 Section 3 イントロ（L180-220・「60 分で診る」 / 8 項目）

- **L184** `組織の引力タイプを 60 分で診る診断セッション。` → `組織の引力タイプを 18 問 3 軸 3 分で診る無料 Web 診断（自動 PDF + 30 分解説 Zoom 同梱）。`
- **L187** `Gravity Recruit（採用基盤）／Gravity Cultivate（躍動組織）／Gravity Shift（両軸）のどれが効くかを示します。` → `Gravity Recruit（集まる・月 35 万）／Gravity Cultivate（躍動・月 50 万）／Gravity Orbit（留まる・月 15 万）の月額契約のどれが効くかを示します。`
- **L215** `組織の現状ペイン 8 項目（採用パイプライン・最終面接辞退率・...・採用コスト対効果）から客観的に判定されます` → `組織の現状を 18 問 3 軸（集まる × 躍動 × 留まる）で測定し、各軸 6 問の Likert 5 段階で客観判定されます`

### 3.4 Section 4 「60 分の 3 パート」（L235-275・PART 1-2-3）

- **L239** `60 分は、3 つのパートで構成される。` → `Web 診断 18 問 + 30 分解説セッションは、2 段で構成される。`
- **L241** `組織現状ヒアリング → 引力タイプ判定 → Shift 適合ロードマップ` → `Web 診断 18 問 3 軸 → 自動 PDF + 4 型判定 → 30 分解説 Zoom（推奨サービスの方角共有）`
- **L247** `8 項目を、過去 2 年の具体エピソードと数値で深掘り` → `集まる軸 6 問 + 躍動軸 6 問 + 留まる軸 6 問の 3 軸 18 問を 5 段階で回答（所要 3 分）`
- **L259** `推奨 Shift パッケージ（Gravity Recruit／Gravity Cultivate／Gravity Shift）と、3 ヶ月の着手順序を共同制作` → `推奨月額契約（Gravity Recruit／Cultivate／Orbit）と、Week 1 で行う組織横断ヒアリング + Pre-Shift 適合判定の方角を 30 分対話で共有`
- **L267** `引力 8 項目スコア` → `3 軸スコア（集まる × 躍動 × 留まる）`

### 3.5 Section 5「60 分の流れ」プロセス（L276-310）

- **L276 / L281 / L283 / L296 / L303 / L304** すべて「60 分」「Zoom 60 分」「PART 1-2-3」「Shift 適合ロードマップ」を新フロー（18 問 3 分 + 30 分解説 Zoom）に統一
- ただし PART 3 案：このセクション全体を **「Web 診断 (3 分) → 自動 PDF → 30 分解説 Zoom」の 3 ステップ**に書き換える（process-step 構造は維持）

### 3.6 Section 6 石井プロフィール（L315-340・「60 分で診るのは石井本人」）

- **L315** `60 分で組織の引力タイプを診るのは、石井本人です。` → `Web 診断（3 分）は AI 自動診断・30 分解説 Zoom セッションは石井本人が直接対応します。`
- **L331** 引用「Scan は、その診断を 60 分で行うセッションです。」→ `Scan は、その診断を 18 問 3 軸の無料 Web 診断 + 30 分解説 Zoom で行います。`

### 3.7 Section 7 Pricing（L370-388・「Zoom 60 分セッション 10 万」）

- **L375** `Zoom 60分セッション・1名` → `無料 Web 診断 v2 + 30 分解説 Zoom セッション同梱・経営者 1 名`
- **L378** `Zoom 60分対話（3パート構成）＋レポート生成＋読み合わせ` → `Web 診断 18 問 3 軸（所要 3 分）＋ 自動 PDF レポート生成 ＋ 30 分解説 Zoom セッション`
- 注：価格は既に Schema.org / 22-DJ で「無料」に修正済。Pricing 周辺の **「10 万円（税抜）」が他に残っていないか grep で再確認**

### 3.8 Section 8 4 型ルート（L390-415・旧価格）

- **L399** `Gravity Orbit` ルート → そのまま OK（月 15 万）
- **L404** `躍動組織実装・月 25 万（6 ヶ月総額 150 万）` → `躍動組織実装・月 50 万（最低 6 ヶ月）`
- **L409** `採用基盤実装・月 26.7 万（3 ヶ月総額 80 万）` → `採用基盤実装・月 35 万（最低 6 ヶ月）`
- **L414** `商談時に R+C 複合パッケージ Gravity Shift（220 万・9 ヶ月）もご案内` → `商談時に R+C 複合（月 85 万・段階移行型）と Orbit 並走もご案内`

### 3.9 Section 9 FAQ（L420-510・60 分 / 8 項目言及）

- **L460** `Recruit / Cultivate / Shift のどれを処方すべきか` → `Recruit / Cultivate / Orbit のどれを処方すべきか`
- **L495-496** `60 分で本当に組織の引力タイプが分かりますか？` / `引力 8 項目（採用パイプライン・...・採用コスト対効果）の客観データから、過去 2 年の具体エピソードと照合して 60 分で判定` → 新仕様（18 問 3 軸 3 分）に書換
- **L492** `事前入力フォーム` 周辺：CODE 未受講者向けの旧フォーム言及 → 新仕様（無料 Web 診断完了後に経営者が回答内容を共有 / または CODE 結果を任意添付）に書換
- FAQ 全体を「無料 Web 診断 + 30 分解説」軸で再点検：他の質問項目（Q1 30 分で何が分かる / Q2 営業されないか / Q3 押し売り / Q4 経営者 1 名 / Q5-Q10）にも残骸あれば修正

### 3.10 Section 10 最終 CTA（L510-540・「60 分で診る」）

- **L516** `組織の引力を、60 分で診る。` → `組織の引力タイプを、18 問 3 軸 3 分で診る。`
- **L519** `Gravity Recruit／Cultivate／Shift のどれが効くかを構造的に判定する` → `Gravity Recruit／Cultivate／Orbit のどれが効くかを構造的に判定する`
- **L524** `Zoom 60分` バッジ → `無料 18 問 3 分` バッジ
- **L531** `60 分で、組織の引力タイプが判定されます。` → `18 問 3 軸 3 分で、組織の引力タイプが判定されます。詳細解説は 30 分 Zoom で。`

### 3.11 残骸の再点検（必須）

LP 全文（585 行）を以下のキーワードで grep し、漏れがないか確認：

```bash
grep -n -E "10\s*万|60\s*分|8 項目|引力 7 項目|Pre-Shift|Shift パッケージ|Shift 適合|R/C/Full|3 ヶ月.*ロードマップ|Zoom 60|Scan 60|事業の伸びしろ|丸裸|Recruit／Cultivate／Shift|Recruit/Cultivate/Shift" "/Users/ishiinobuyuki/Documents/Obsidian Vault/05_プロダクト/Gravity/Scan/LP/index.html"
```

検出 0 件になったら完了。

---

## 4. 実装手順（推奨フェーズ分割）

| Phase | 範囲 | 工数 | 確認 |
|:-:|---|:-:|---|
| **A** | Nav + Section 2 Paradox + Section 3 イントロ | 30 分 | grep で 60 分 / 8 項目 / Shift 残存数確認 |
| **B** | Section 4 + Section 5（PART 1-2-3 → Web 診断 + 30 分解説）| 60 分 | 同上 |
| **C** | Section 6 石井プロフィール + Section 7 Pricing + Section 8 4 型ルート | 45 分 | 旧価格（80 万 / 150 万 / 220 万 / 月 25 万 / 月 26.7 万）残存ゼロ確認 |
| **D** | Section 9 FAQ + Section 10 最終 CTA | 45 分 | 60 分言及ゼロ確認 |
| **E** | 機械チェック + 本番デプロイ + 反映確認 | 15 分 | mobile audit / lint / lint_consistency.sh / FTP デプロイ |

合計 **約 3h**（Sonnet 速度・user 確認の往復含めず）。

---

## 5. 機械チェック手順（各 Edit 後・自動実行）

LP 編集後は post_lp_edit_audit.sh hook が以下を自動実行：

1. `audit_mobile_sync.py`（mobile.css 同期）
2. `lint_lp_internal_terms.py`（LP 社内用語ゼロ原則）

加えて、全 Phase 完了後に：

```bash
cd "/Users/ishiinobuyuki/Documents/Obsidian Vault" && bash 06_開発/scripts/lint/lint_consistency.sh
```

を実行し、`gravity/Scan/LP/index.html` が「Scan 10万」等のエラーリストに**入っていないこと**を確認。

---

## 6. 本番デプロイ手順

```bash
curl -T "/Users/ishiinobuyuki/Documents/Obsidian Vault/05_プロダクト/Gravity/Scan/LP/index.html" \
  "ftp://sv16489.xserver.jp/growthfix.jp/public_html/gravity-scan/index.html" \
  --user "xs992119:cgq1fv99" \
  -w "DJ_LP_v2: %{http_code}\n"
```

FTP パスワード詳細：`06_開発/開発ツール/FTP情報_メインFTPアカウント.md`

デプロイ後の反映確認：

```bash
curl -s "https://growthfix.jp/gravity-scan/" | grep -E "60\s*分|10\s*万|8 項目|Shift パッケージ" | head -10
```

検出 0 件になったら **本タスク完了**。

---

## 7. 完走後の作業

1. **memory 更新**：`memory/project_scan_abolish_260514.md` の §完走サマリーに「`/gravity-scan/` LP 完全変更（DJ-v2）」を追記
2. **MEMORY.md 更新**：トップエントリ（260514 朝〜夕完走宣言）に「DJ-v2 LP 完全変更も完走」追記
3. **統合タスクマスター更新**：`04_GrowthFix/00_統合タスクマスター_v1.1.md` §3.5 完走実績に追記
4. **デイリーログ更新**：`04_GrowthFix/04_デイリーログ/2605/260514_daily.md` 振り返りに反映
5. **user 報告**：完走報告 + 本番 URL 体験 URL（`https://growthfix.jp/gravity-scan/`）共有

---

## 8. 別 Node 起動プロンプト（user がコピペで使う用）

以下を別 Node のメインスレッドに貼り付け：

```
このセッションで以下のタスクを完走してほしい：

「/gravity-scan/ LP 完全変更」を実施する。

詳細は以下の引き継ぎ書を Read してから着手：
`04_GrowthFix/01_サービス設計/_Gravity_診断_CODE_Scan/260514_gravity-scan_LP完全変更_引き継ぎ書_v1.0.md`

着手手順：
1. 引き継ぎ書を Read（§1 主軸戦略・§2 既修正・§3 残存箇所マップ・§4 実装手順・§5 機械チェック・§6 デプロイ手順を把握）
2. Phase A → B → C → D の順で 5-7 セクションを大ブロック置換
3. 各 Phase 完了後に grep で残存箇所を確認
4. 全 Phase 完了後に lint_consistency.sh を実行 → エラー 0 件確認
5. FTP デプロイ → 本番反映確認 → user 報告

主軸戦略：
- 「60 分有料 Scan」前提の残骸を一掃し、「無料 Web 診断 v2 + 30 分解説 Zoom + R/C/Orbit 月額」軸に統一
- R/C/Orbit 月額制：Recruit 月 35 万 / Cultivate 月 50 万 / Orbit 月 15 万
- 30 分解説 Zoom は既存 utage URL（https://utage-system.com/event/gcfmTRLg7lAq/register）流用
- Q1-Q5 確定済・SSOT 整合・本番ファネル稼働中（22-DJ Hero / 22-DK Web 診断 / 22-DL PDF / 22-DM メール / 22-DO lint すべて完了済）

モデル指定（推奨）：
- Sonnet または lp-implementer agent でコスト最適化（Opus 不要・大規模 LP 書換に最適）

引き継ぎ書の §3 残存箇所マップを参照しながら、Edit ツールでセクション単位置換を進めてください。
```

---

## 9. ブロッカー想定 / トラブルシュート

| ブロッカー | 対処 |
|---|---|
| `mobile.css 未カバークラス` 警告 | 新規 class を導入していなければ無視可（既存 class のみ使用）|
| FTP 226 以外のエラー | パスワード / パス確認（`06_開発/開発ツール/FTP情報_メインFTPアカウント.md`）|
| lint で予期せぬエラー | 引き継ぎ書 §5 機械チェック手順に従う |
| 文章構造で迷う | §1 主軸戦略に立ち戻る・user に確認 |
| Edit で「String not found」 | Read で正確な文字列を再取得・全角スペース / 改行に注意 |

---

## 10. 関連参照

- `memory/project_scan_abolish_260514.md`（Q1-Q5 確定 + W22 全完走実績）
- `MEMORY.md`（トップ：260514 朝〜夕完走宣言）
- `04_GrowthFix/00_統合タスクマスター_v1.1.md` v2.9（§3.5）
- `05_プロダクト/_共通/SSOT_用語と定義.md` v5.1（廃止注記原則）
- `05_プロダクト/_共通/SSOT_Gravity_3軸.md` v1.2
- `09_会社OS/公開/ガイドライン/商品.md`（読み替え原則）
- `09_会社OS/公開/ガイドライン/商品_5サービス詳細.md`（旧 Scan 仕様の履歴温存）
- `06_開発/scripts/lint/lint_consistency.sh`（「Scan 10万」検出ルール）
- `04_GrowthFix/04_デイリーログ/2605/260514_daily.md`（本日振り返り）
