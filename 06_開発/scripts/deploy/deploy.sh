#!/bin/bash
# GrowthFix FTP並列デプロイスクリプト
#
# 使い方:
#   ./deploy.sh                # 全LP・診断ツール・共通アセット・WPを並列デプロイ
#   ./deploy.sh shared         # 共通アセットのみ
#   ./deploy.sh lp             # LPのみ
#   ./deploy.sh diagnose       # 診断ツールのみ
#   ./deploy.sh wp             # WhitePaper V9のみ
#
# 並列度: 8（curl & で並列実行）
# Xserver 制限：典型的に4-8並列まで安全
# ⚠️ 並列数が多すぎると FTP認証530エラーが出る（2026-04-20確認）。1スクリプトあたり8本前後に抑える
#
# 260513 Phase 3 B-1: 05_プロダクト 親子2階層化に対応
#   - 旧 05_プロダクト/Gravity{Code,Scan,Shift,...}/ → 新 05_プロダクト/Gravity/{Code,Scan,Shift,...}/
#   - GravityBlueprint 関連はすべて削除（260430 廃止済）
#   - 本番URL（gravity-code/ 等）は変更なし

set -e

# FTP設定（FTP情報_メインFTPアカウント.md より）
FTP_HOST="sv16489.xserver.jp"
FTP_USER="xs992119"
FTP_PASS="${FTP_PASS}"
FTP_BASE="ftp://${FTP_HOST}/growthfix.jp/public_html"
AUTH="${FTP_USER}:${FTP_PASS}"

# Vaultルート
VAULT="/Users/ishiinobuyuki/Documents/Obsidian Vault"

# === ヘルパー：FTPアップロード（バックグラウンド実行）===
upload() {
  local local_path="$1"
  local remote_path="$2"
  local label="$3"
  curl -T "$local_path" "${FTP_BASE}/${remote_path}" --user "$AUTH" --ftp-create-dirs -s -w "${label}: %{http_code}\n" &
}

# === グループ別デプロイ ===
deploy_shared() {
  echo "[共通アセット並列アップロード]"
  upload "$VAULT/_assets/js/tracking.js"           "assets/js/tracking.js"            "tracking.js"
  upload "$VAULT/_assets/css/tokens.css"           "assets/css/tokens.css"            "tokens.css"
  upload "$VAULT/_assets/css/lp-base.css"          "assets/css/lp-base.css"           "lp-base.css"
  upload "$VAULT/_assets/css/lp-scan-extras.css"   "assets/css/lp-scan-extras.css"    "lp-scan-extras.css"
  upload "$VAULT/05_プロダクト/_共通/question_block_styles.php" "shared/question_block_styles.php" "question_block_styles.php"
  wait
  echo "[共通アセット完了]"
  echo ""
}

deploy_lp() {
  echo "[LP並列アップロード]"
  # Scan LP（新Scan・旧DEEP統合版／styles.css は共通CSS使用）
  upload "$VAULT/05_プロダクト/Gravity/Scan/LP/index.html"     "gravity-scan/index.html"      "Scan LP"
  upload "$VAULT/05_プロダクト/Gravity/Scan/LP/script.js"      "gravity-scan/script.js"       "Scan script.js"
  # Shift LP（styles.css は共通CSS使用のため対象外）
  upload "$VAULT/05_プロダクト/Gravity/Shift/LP/index.html"    "gravity-shift/index.html"     "Shift LP"
  upload "$VAULT/05_プロダクト/Gravity/Shift/LP/script.js"     "gravity-shift/script.js"      "Shift script.js"
  # Orbit LP（260513 HR Team 仮説E採用でロールバック・Orbit 復元）
  upload "$VAULT/05_プロダクト/Gravity/Orbit/LP/index.html"    "gravity-orbit/index.html"     "Orbit LP"
  # Coaching LP
  upload "$VAULT/05_プロダクト/Gravity/Coaching/LP/index.html" "gravity-coaching/index.html"  "Coaching LP"
  upload "$VAULT/05_プロダクト/Gravity/Coaching/LP/styles.css" "gravity-coaching/styles.css"  "Coaching CSS"
  upload "$VAULT/05_プロダクト/Gravity/Coaching/LP/script.js"  "gravity-coaching/script.js"   "Coaching script.js"
  # Code LP
  upload "$VAULT/05_プロダクト/Gravity/Code/LP/index.html"     "gravity-code/index.html"      "Code LP"
  upload "$VAULT/05_プロダクト/Gravity/Code/LP/styles.css"     "gravity-code/styles.css"      "Code CSS"
  upload "$VAULT/05_プロダクト/Gravity/Code/LP/script.js"      "gravity-code/script.js"       "Code script.js"
  wait
  echo "[LP完了]"
  echo ""
}

deploy_wp() {
  echo "[WhitePaper V9 アップロード]"
  upload "$VAULT/05_プロダクト/Gravity/WhitePaper/V9/index.html"           "whitepaper/index.html"           "WP V9 index.html"
  upload "$VAULT/05_プロダクト/Gravity/WhitePaper/V9/style.css"            "whitepaper/style.css"            "WP V9 style.css"
  upload "$VAULT/05_プロダクト/Gravity/WhitePaper/V9/images/gravity_map.svg" "whitepaper/images/gravity_map.svg" "WP V9 gravity_map.svg"
  upload "$VAULT/05_プロダクト/Gravity/WhitePaper/V9/images/loop_chart.svg"  "whitepaper/images/loop_chart.svg"  "WP V9 loop_chart.svg"
  wait
  echo "[WhitePaper V9 完了]"
  echo ""
}

deploy_diagnose() {
  echo "[診断ツール並列アップロード]"
  # === Scan 診断（260508 Shift診断UI統合廃止後の単一ファイル構成・260513 deploy.sh 実態同期）===
  #   旧 multi-step UI（hearing-ceo / hearing-exec / integrate / analyze / api/*4本）は廃止
  #   現行：app.js + generate.php + index.html + style.css + web-diagnose.html + system_prompt.txt + jargon_map.json
  upload "$VAULT/05_プロダクト/Gravity/Scan/診断_本番/index.html"          "gravity-scan/diagnose/index.html"          "Scan index"
  upload "$VAULT/05_プロダクト/Gravity/Scan/診断_本番/app.js"              "gravity-scan/diagnose/app.js"              "Scan app.js"
  upload "$VAULT/05_プロダクト/Gravity/Scan/診断_本番/generate.php"        "gravity-scan/diagnose/generate.php"        "Scan generate.php"
  upload "$VAULT/05_プロダクト/Gravity/Scan/診断_本番/style.css"           "gravity-scan/diagnose/style.css"           "Scan style.css"
  upload "$VAULT/05_プロダクト/Gravity/Scan/診断_本番/web-diagnose.html"   "gravity-scan/diagnose/web-diagnose.html"   "Scan web-diagnose"
  upload "$VAULT/05_プロダクト/Gravity/Scan/診断_本番/system_prompt.txt"   "gravity-scan/diagnose/system_prompt.txt"   "Scan system prompt"
  upload "$VAULT/05_プロダクト/Gravity/Scan/診断_本番/jargon_map.json"     "gravity-scan/diagnose/jargon_map.json"     "Scan jargon map"

  # === CODE 一般診断（ペンディング中）===
  upload "$VAULT/05_プロダクト/Gravity/Code/診断_本番/app.js"        "gravity-code/diagnose/app.js"        "Code app.js"
  upload "$VAULT/05_プロダクト/Gravity/Code/診断_本番/generate.php"  "gravity-code/diagnose/generate.php"  "Code generate.php"

  # === CODE Executive 診断（260420追加）===
  upload "$VAULT/05_プロダクト/Gravity/Code/診断_executive_本番/app.js"        "gravity-code/executive/app.js"        "Code Executive app.js"
  upload "$VAULT/05_プロダクト/Gravity/Code/診断_executive_本番/generate.php"  "gravity-code/executive/generate.php"  "Code Executive generate.php"
  upload "$VAULT/05_プロダクト/Gravity/Code/診断_executive_本番/index.html"    "gravity-code/executive/index.html"    "Code Executive index.html"

  # ※ config.php（APIキー）は手動デプロイのみ（セキュリティのためスクリプト対象外）
  wait
  echo "[診断ツール完了]"
  echo ""
}

# === メイン ===
case "${1:-all}" in
  shared)   deploy_shared ;;
  lp)       deploy_lp ;;
  diagnose) deploy_diagnose ;;
  wp)       deploy_wp ;;
  all)
    deploy_shared
    deploy_lp
    deploy_diagnose
    deploy_wp
    ;;
  *)
    echo "Usage: $0 [shared|lp|diagnose|wp|all]"
    exit 1
    ;;
esac

echo "全デプロイ完了"
