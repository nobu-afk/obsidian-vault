# 新セッション引継ぎ：Gravity LP デザイン刷新・残タスク6件

> **作成日：** 2026-04-16
> **引継ぎ理由：** 現セッションがトークン消費過多（24時間連続対話・戦略レベル思考多数保持）。メカニカルな実装作業は新セッションでクリーンに進める
> **次セッションでの最初の指示：**「`/Users/ishiinobuyuki/Documents/Obsidian Vault/06_開発/260416_新セッション引継ぎ_Gravity_LP_デザイン刷新.md` を読んで、記載された6タスクを順次進めてください」

---

## 📋 実施する6タスク

### 軽作業（各5-15分）

#### タスク1：Shift LP にScanリンク追加
- **ファイル**：`/Users/ishiinobuyuki/Documents/Obsidian Vault/05_プロダクト/GravityShift/LP/index.html`
- **現状**：footer-links に Scan リンクが未掲載
- **やること**：footer-links に `<a href="https://growthfix.jp/gravity-scan/">Scan</a>` を他のサービスリンクと並べて追加
- **デプロイ**：FTPで `/gravity-shift/index.html` に上書き

#### タスク2：`/gravity/sample/` フォルダの本番削除判断
- **背景**：LP本体からリンクは既に削除済み。本番サーバーにファイルは残っている
- **選択肢**：
  - (a) 本番から削除してアクセス不能化
  - (b) 維持（URL直打ちでのみアクセス可）
- **判断材料**：サンプル成果物としての情報価値 vs 古いサービス情報（旧Gravity 210万時代のもの）の混乱リスク
- **推奨**：(a) 削除（第2世代と整合しない古いサンプルは誤解を生む）
- **削除方法**：curl の DELE コマンド or FTPクライアントで削除（削除前にローカルバックアップ確認）

#### タスク3：CODE LP「5万円」表示の最終チェック
- **ファイル**：`/Users/ishiinobuyuki/Documents/Obsidian Vault/05_プロダクト/GravityCode/LP/index.html`
- **やること**：全箇所grepして価格表記が「5万円」or「¥50,000」に統一されているか確認
- **関連**：名刺裏も「5万円」、サンプルレポートも一致必要
- **不整合あれば**：「10万円」→「5万円」に修正＋デプロイ

### 中作業（各30-60分）

#### タスク4：Gravity LPのインラインCSS切り出し
- **ファイル**：
  - `/Users/ishiinobuyuki/Documents/Obsidian Vault/05_プロダクト/Gravity/LP/index.html`
  - `/Users/ishiinobuyuki/Documents/Obsidian Vault/05_プロダクト/Gravity/LP/styles.css`
- **対象インラインstyle**：
  - 5サービスカード（CODE/Scan/Coaching/Shift/Orbit）
  - 診断2択CTA（CODE/Scan の分岐ボタン）
- **やること**：
  1. index.html から `style="..."` 属性を抽出
  2. `styles.css` に意味のあるクラス名（例：`.service-card`, `.service-card-title`, `.diagnosis-cta` 等）で追加
  3. index.html から style 属性を削除し、クラスに置換
- **検証**：シークレットウィンドウで本番確認・レイアウト崩れないこと
- **デプロイ**：index.html と styles.css 両方を FTP

#### タスク5：4象限ビジュアル図の追加（Gravityマップをリッチ化）
- **ファイル**：Gravity LP（上記）
- **現状**：service-connect-band は横並びテキスト（`❶社長独走／❷人力拡大／❸施策先行／❹グラビティ型成長`）
- **目標**：4象限のマトリクス図を視覚的に表示
  - 縦軸：人で回す ↔ 仕組みで回す
  - 横軸：今のステージ ↔ 次のステージ
  - ❹だけ特別扱い（濃いネイビー・ハイライト・思想セリフ「重力が全てを引き寄せるかのように」添える）
- **実装方針**：
  - 純CSS Grid で 2×2 配置
  - SVG or CSS で矢印軸
  - ❹セルだけ背景色強化・説明テキスト少し多め
- **参考**：V8.1 PDF の P5 Gravityマップ図（文字版マトリクス）を視覚化

### 重作業（2-4時間）

#### タスク6：共通ヘッダー/フッターの部品化（7LPのDRY化）
- **対象**：Gravity / CODE / Scan / Scan DEEP / Coaching / Shift / Orbit の7LP
- **現状の問題**：各LPにheader/footerのHTMLがハードコード。タグライン変更時に7ファイル修正が必要
- **実装方針候補**：
  - (A) **SSI (Server Side Include)**：`.shtml` 化して `<!--#include virtual="..." -->`。ただしxserverがSSI対応か要確認
  - (B) **JavaScript fetch**：`<div id="header"></div>` + `fetch('/assets/html/header.html')` で注入。SEO的に微妙
  - (C) **雛形ファイル＋手動コピー**：`/assets/html/header-template.html` を作り、LP更新時に参照する運用ルール化
- **推奨**：**(C) 雛形ファイル方式**が運用安定
  - 更新時の手順を memory 化：「7LP全てで一貫するよう雛形を参照」
  - 雛形：`/Users/ishiinobuyuki/Documents/Obsidian Vault/05_プロダクト/_共通/` フォルダ新設
- **やること**：
  1. `_共通/header-template.html`・`_共通/footer-template.html` 作成（現在の最新版を固定）
  2. 各LPの現在のheader/footerを雛形と一致させる
  3. 差分リストを作成（各LPで意図的に違う箇所・ハイライト箇所等）
  4. 運用ルール memory 化

---

## 🎯 各タスク共通の制約・原則

### 自己ラベル禁則（絶対遵守）
- ❌「変人」「偏愛者」「Gravity信者」等の自己ラベル
- ✅「人間」で統一
- 詳細：`memory/feedback_embrace_criticism_and_exaggeration.md` 鉄則3

### V9 思想との整合
- メインタグ「自分を取り戻すと、組織が動き出す。」
- サブタグ「組織を変えるな。引力を作れ。」
- V9書籍タイトル「組織を変えるな。経営者を取り戻せ。」は**書籍専用**（LPでは不使用）

### サービス第2世代（重要）
- 5サービス：CODE / Scan / Scan DEEP / Coaching / Shift / Orbit
- **Gravity本体 6ヶ月・210万は廃止済み**
- Shift 主力（3ヶ月・60万・❷人力拡大 主戦場）
- ❸施策先行 も Shift で吸収
- 詳細：`memory/project_gravity_series_gen2_260415.md`

### 禁則表記（本文）
- ❌ グラビティ象限 → ✅ グラビティ型成長
- ❌ Gravity本体 6ヶ月プログラム（廃止済）
- ❌ ソースコード / ハック（ITメタファー）
- 詳細：`04_GrowthFix/02_マーケティング/260416_WP_V9構成仕様書.md` の禁則ワード節

---

## 🔗 関連ファイル・リソース

### サーバー情報
- FTP情報：`/Users/ishiinobuyuki/Documents/Obsidian Vault/06_開発/開発ツール/FTP情報_メインFTPアカウント.md`
- デプロイ先：`growthfix.jp/public_html/` 配下
- デプロイコマンド：
  ```
  curl -T LOCAL_FILE "ftp://sv16489.xserver.jp/growthfix.jp/public_html/PATH/REMOTE_FILE" --user "xs992119:PASS"
  ```

### memory参照（重要）
- サービス第2世代：`memory/project_gravity_series_gen2_260415.md`
- Gravity思想マスター：`memory/project_gravity_identity_gravitational.md`
- 自己ラベル禁則：`memory/feedback_embrace_criticism_and_exaggeration.md`
- タイムゾーン・デプロイ手順：`memory/MEMORY.md`

### 今日の決定・成果物
- V9 WP構成仕様書：`04_GrowthFix/02_マーケティング/260416_WP_V9構成仕様書.md`
- V9 Manusプロンプト：`04_GrowthFix/02_マーケティング/260416_Manus投入プロンプト_WP_V9.md`
- セミナー設計仕様書：`04_GrowthFix/02_マーケティング/260416_セミナー設計仕様書_V9.md`
- 名刺入稿指示書：`04_GrowthFix/00_営業/260415_名刺入稿指示書_Sushitech.md`

### 7LPの物理位置
| LP | ローカル | 本番URL |
|---|---|---|
| Gravity（シリーズハブ） | `05_プロダクト/Gravity/LP/index.html` | `/gravity/` |
| CODE | `05_プロダクト/GravityCode/LP/index.html` | `/gravity-code/` |
| Scan | `05_プロダクト/GravityScan/LP/index.html` | `/gravity-scan/` |
| Scan DEEP | `05_プロダクト/GravityScan/DEEP_LP/index.html` | `/gravity-scan-deep/` |
| Coaching | `05_プロダクト/GravityCoaching/LP/index.html` | `/gravity-coaching/` |
| Shift | `05_プロダクト/GravityShift/LP/index.html` | `/gravity-shift/` |
| Orbit | `05_プロダクト/GravityOrbit/LP/index.html` | `/gravity-orbit/` |

---

## 🏁 完了条件

### 全タスク共通
- [ ] シークレットウィンドウで本番の最終確認
- [ ] レイアウト崩れ・リンク切れなし
- [ ] モバイル表示確認
- [ ] 実施内容を新セッションで簡潔にサマリ出力

### 各タスク別
- タスク1：Shift LP footer に Scan リンク表示・リンク動作確認
- タスク2：`/gravity/sample/` アクセス不能化 (404) or 維持判断の記録
- タスク3：CODE LP の価格表記が5万円で統一
- タスク4：Gravity LP のインラインstyle が削除され、CSSクラスで動作
- タスク5：Gravityマップ4象限が視覚的に表示され、❹がハイライトされている
- タスク6：雛形ファイル作成＋7LPの差分リスト＋運用ルール memory 化

---

## 💬 新セッションでの最初の指示（コピペ用）

```
/Users/ishiinobuyuki/Documents/Obsidian Vault/06_開発/260416_新セッション引継ぎ_Gravity_LP_デザイン刷新.md を読んで、記載された6タスクを軽作業→中作業→重作業の順で進めてください。各タスク完了時に実施内容を報告してから次に進んでください。全て完了したらサマリを出力してください。
```

### 進め方の注意
- タスク1/2/3（軽）は1回のメッセージで3件まとめて実施可
- タスク4（中）は単独で実施・完了後に報告
- タスク5（中）は単独で実施・完了後に報告
- タスク6（重）は段階的に実施：(a)雛形作成 → (b)差分リスト → (c)運用ルール化 の3段階で報告

---

## 🗓 実施タイミング推奨

- **今日（4/16 夜 or 4/17朝）**：タスク1/2/3（軽作業・15-20分）
- **4/17-18**：タスク4/5（中作業・各30-60分）
- **4/19-20**：タスク6（重作業・2-4時間）
- **Sushitech前 4/26まで**：全タスク完了し本番検証

---

## 📝 現セッションからの追加注意

1. **名刺入稿指示書は4/19締切**：別作業で進行中。今回のLP作業とは独立
2. **Manus V9 WP投入は本日 or 明日朝推奨**：プロンプト・仕様書完成済み
3. **セミナーLP実装**（5/8 本番用）は別タスクとして後日

---

## 🧠 新セッションへのメタ指示

- 戦略レベルの判断（V9思想・パーパス・ビジネスモデル）は**本セッション外では変更しない**
- 実装レベルの判断（CSS命名・ファイル構造）は新セッションで自由に決定してよい
- 迷ったら関連memoryを参照し、それでも不明なら石井に質問する
- 作業中に「この決定は戦略レベルでは？」と感じたら、そこで止めて石井に確認
