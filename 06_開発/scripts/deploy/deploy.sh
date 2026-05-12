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
  # Blueprint LP（新URL・260420追加）
  upload "$VAULT/05_プロダクト/GravityBlueprint/LP/index.html" "gravity-blueprint/index.html" "Blueprint LP"
  upload "$VAULT/05_プロダクト/GravityBlueprint/LP/script.js"  "gravity-blueprint/script.js"  "Blueprint script.js"
  upload "$VAULT/05_プロダクト/GravityBlueprint/LP/styles.css" "gravity-blueprint/styles.css" "Blueprint styles.css"
  # Scan LP（新Scan・旧DEEP統合版／styles.css は共通CSS使用）
  upload "$VAULT/05_プロダクト/GravityScan/LP/index.html"     "gravity-scan/index.html"      "Scan LP"
  upload "$VAULT/05_プロダクト/GravityScan/LP/script.js"      "gravity-scan/script.js"       "Scan script.js"
  # Shift LP（styles.css は共通CSS使用のため対象外）
  upload "$VAULT/05_プロダクト/GravityShift/LP/index.html"    "gravity-shift/index.html"     "Shift LP"
  upload "$VAULT/05_プロダクト/GravityShift/LP/script.js"     "gravity-shift/script.js"      "Shift script.js"
  # Orbit LP
  upload "$VAULT/05_プロダクト/GravityOrbit/LP/index.html"    "gravity-orbit/index.html"     "Orbit LP"
  upload "$VAULT/05_プロダクト/GravityOrbit/LP/styles.css"    "gravity-orbit/styles.css"     "Orbit CSS"
  upload "$VAULT/05_プロダクト/GravityOrbit/LP/script.js"     "gravity-orbit/script.js"      "Orbit script.js"
  # Coaching LP
  upload "$VAULT/05_プロダクト/GravityCoaching/LP/index.html" "gravity-coaching/index.html"  "Coaching LP"
  upload "$VAULT/05_プロダクト/GravityCoaching/LP/styles.css" "gravity-coaching/styles.css"  "Coaching CSS"
  upload "$VAULT/05_プロダクト/GravityCoaching/LP/script.js"  "gravity-coaching/script.js"   "Coaching script.js"
  # Code LP
  upload "$VAULT/05_プロダクト/GravityCode/LP/index.html"     "gravity-code/index.html"      "Code LP"
  upload "$VAULT/05_プロダクト/GravityCode/LP/styles.css"     "gravity-code/styles.css"      "Code CSS"
  upload "$VAULT/05_プロダクト/GravityCode/LP/script.js"      "gravity-code/script.js"       "Code script.js"
  wait
  echo "[LP完了]"
  echo ""
}

deploy_wp() {
  echo "[WhitePaper V9 アップロード]"
  upload "$VAULT/05_プロダクト/WhitePaper/V9/index.html"           "whitepaper/index.html"           "WP V9 index.html"
  upload "$VAULT/05_プロダクト/WhitePaper/V9/style.css"            "whitepaper/style.css"            "WP V9 style.css"
  upload "$VAULT/05_プロダクト/WhitePaper/V9/images/gravity_map.svg" "whitepaper/images/gravity_map.svg" "WP V9 gravity_map.svg"
  upload "$VAULT/05_プロダクト/WhitePaper/V9/images/loop_chart.svg"  "whitepaper/images/loop_chart.svg"  "WP V9 loop_chart.svg"
  wait
  echo "[WhitePaper V9 完了]"
  echo ""
}

deploy_diagnose() {
  echo "[診断ツール並列アップロード]"
  # === Blueprint 診断（個人CEO・60分単発／260420 URL配置換え） ===
  upload "$VAULT/05_プロダクト/GravityBlueprint/診断_本番/app.js"       "gravity-blueprint/diagnose/app.js"       "Blueprint diagnose app.js"
  upload "$VAULT/05_プロダクト/GravityBlueprint/診断_本番/generate.php" "gravity-blueprint/diagnose/generate.php" "Blueprint diagnose generate.php"
  upload "$VAULT/05_プロダクト/GravityBlueprint/診断_本番/index.html"   "gravity-blueprint/diagnose/index.html"   "Blueprint diagnose index.html"
  upload "$VAULT/05_プロダクト/GravityBlueprint/診断_本番/style.css"    "gravity-blueprint/diagnose/style.css"    "Blueprint diagnose style.css"

  # === Scan 診断（CEO+幹部・multi-step／260420 旧DEEP統合版） ===
  upload "$VAULT/05_プロダクト/GravityScan/診断_本番/index.html"        "gravity-scan/diagnose/index.html"        "Scan dashboard"
  upload "$VAULT/05_プロダクト/GravityScan/診断_本番/hearing-ceo.html"  "gravity-scan/diagnose/hearing-ceo.html"  "Scan CEO hearing"
  upload "$VAULT/05_プロダクト/GravityScan/診断_本番/hearing-exec.html" "gravity-scan/diagnose/hearing-exec.html" "Scan Exec hearing"
  upload "$VAULT/05_プロダクト/GravityScan/診断_本番/integrate.html"    "gravity-scan/diagnose/integrate.html"    "Scan integrate"
  upload "$VAULT/05_プロダクト/GravityScan/診断_本番/analyze.html"      "gravity-scan/diagnose/analyze.html"      "Scan analyze"
  upload "$VAULT/05_プロダクト/GravityScan/診断_本番/api/project.php"        "gravity-scan/diagnose/api/project.php"        "Scan api project"
  upload "$VAULT/05_プロダクト/GravityScan/診断_本番/api/hearing.php"        "gravity-scan/diagnose/api/hearing.php"        "Scan api hearing"
  upload "$VAULT/05_プロダクト/GravityScan/診断_本番/api/generate-gap.php"   "gravity-scan/diagnose/api/generate-gap.php"   "Scan api gap"
  upload "$VAULT/05_プロダクト/GravityScan/診断_本番/api/generate-report.php" "gravity-scan/diagnose/api/generate-report.php" "Scan api report"

  # === CODE 一般診断（ペンディング中）===
  upload "$VAULT/05_プロダクト/GravityCode/診断_本番/app.js"        "gravity-code/diagnose/app.js"        "Code app.js"
  upload "$VAULT/05_プロダクト/GravityCode/診断_本番/generate.php"  "gravity-code/diagnose/generate.php"  "Code generate.php"

  # === CODE Executive 診断（260420追加）===
  upload "$VAULT/05_プロダクト/GravityCode/診断_executive_本番/app.js"        "gravity-code/executive/app.js"        "Code Executive app.js"
  upload "$VAULT/05_プロダクト/GravityCode/診断_executive_本番/generate.php"  "gravity-code/executive/generate.php"  "Code Executive generate.php"
  upload "$VAULT/05_プロダクト/GravityCode/診断_executive_本番/index.html"    "gravity-code/executive/index.html"    "Code Executive index.html"

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
