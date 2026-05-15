# 旧有料版 Scan アーカイブ（260515 完全廃止）

## 廃止経緯

| 日付 | 経緯 |
|---|---|
| 260422 | 旧 `/gravity-scan/` 廃止 → Shift 統合 |
| 260430 | リブート（10 万円有料 Scan として復活）|
| **260514** | **22-DJ Scan 無料化決定**（無料 Web 診断 v2 化・18 問 3 軸 + 30 分説明セッション同梱）|
| **260515** | **本フォルダアーカイブ化**（有料版完全廃止・サービスピボット最終締め）|

## アーカイブ内容

| フォルダ | 内容 | 旧本番 URL |
|---|---|---|
| `診断_本番/` | 旧有料版 10 万円 Scan の本番ファイル群（index.html / app.js / generate.php / style.css / system_prompt.txt / jargon_map.json / web-diagnose.html / api/ / .htaccess / CHANGELOG.md）| `https://growthfix.jp/gravity-scan/diagnose/` |
| `診断_設計/` | 旧有料版 Scan 設計資料・素材ストック | - |

## 廃止理由

1. **戦略ピボット**（260514）：プロジェクト型 → 月額継続型への転換に伴う Scan 無料化
2. **新動線**：無料 Web 診断 v2（`web-diagnose_本番/` → `/gravity-scan/web-diagnose/`）が稼働中
3. **3 サービス対称構造の入口**：CODE 5 万 → Scan 無料 → R/C/Orbit 月額（260515 v3.0/v3.2 確定）

## 現行運用（260515 確定）

| URL | 役割 |
|---|---|
| `https://growthfix.jp/gravity-scan/` | Scan メイン LP（無料化済）|
| `https://growthfix.jp/gravity-scan/web-diagnose/` | 無料 Web 診断 v2（18 問 3 軸 + 自動 PDF + utage 30 分予約）|

## 後続作業（次回サーバー側対応）

- 本番サーバー側 `/gravity-scan/diagnose/` の処理：
  - (a) ファイル削除 → 404
  - (b) **301 リダイレクト → `/gravity-scan/web-diagnose/` 統一**（推奨）

## 関連

- 260514 22-DJ Scan 無料化決定の memory：MEMORY.md「W22 SCAN 廃止 PJ」
- Cultivate v3.0 + R v2.1.4 + Orbit v3.2 ピボット 全完走（260515）
- 関連 PR：deploy.sh deploy_diagnose 関数修正（診断_本番 deploy 対象除外）

## 復元可否

旧有料版に戻す場合は本フォルダから `診断_本番/` `診断_設計/` を `Scan/` 直下に戻し、deploy.sh deploy_diagnose を復活させる。ただし戦略ピボット完了済のため復元想定なし。
