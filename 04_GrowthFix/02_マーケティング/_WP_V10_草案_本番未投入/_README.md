# WP V10 草案・本番未投入（260515 隔離）

## 目的

WhitePaper V10 系（V10 / V10_第6章草案）を **本番デプロイ対象ディレクトリ（05_プロダクト）から物理的に外す** ことで、誤って `/whitepaper/` `/whitepaper-read/` に上げる事故を構造的に防ぐ。

## 移動経緯

2026-05-15 CODE 3 軸 B 案（強み × 想い × 偏愛）全件波及デプロイ作業中、メインスレッドが「WP V10 を本番にデプロイすべき」と誤認して `/whitepaper/` に upload → オプトインフォーム消失事故。30 秒以内に修復したが、以下の構造的根本原因が判明：

1. `deploy.sh deploy_wp` 関数が `WhitePaper/V9/index.html → /whitepaper/index.html` という誤設計で、毎回 WP デプロイがオプトイン破壊を引き起こす罠だった（既に Layer 1 で修正済）
2. V10 が本番デプロイ対象ディレクトリ（05_プロダクト）に同居していたため、agent が「未デプロイ = 本番投入候補」と誤判断
3. 過去 4 件の WP 関連事故（260425 / 260507 / 260511 / 260515）の連鎖

→ 物理隔離（本ディレクトリ）+ deploy.sh 修正 + verify_deployment.sh 自動実行で **構造的事故ゼロ化**。

## 配置内容

- `V10/` ── WhitePaper V10 草案（PhaseA 完了・PhaseB 開発中）
- `V10_第6章草案/` ── V10 第 6 章 / 6.5 章 / 第 8 章「庭教師」/ Bandura 3 層 / 複数領域統合 等の草案 .md

## 本番投入の判断タイミング

V10 を本番に投入する判断が出たら、以下を **必ずセット実施**：

1. user 明示判断（「V10 を本番化する」と明示的決定）
2. memory `feedback_wp_v9_v10_deploy_path_distinction_260515.md` 更新
3. `deploy.sh` に `deploy_wp_v10` 関数追加（`/whitepaper-read/` への upload 設計）
4. `verify_deployment.sh` の WP 検証で V10 特徴語を確認するチェックを追加
5. 移動：`04_GrowthFix/02_マーケティング/_WP_V10_草案_本番未投入/V10/` → `05_プロダクト/Gravity/WhitePaper/V10/`（プロダクト層に戻す）
6. CLAUDE.md / MEMORY.md デプロイ情報セクション更新

## 草案編集時の参照

V10 を編集する場合は、本ディレクトリ内のファイルを直接編集する。本番反映なし。SSOT lint [1.7c] CODE 3 軸 B 案チェックは本ディレクトリも対象（草案であってもマスター整合維持）。
