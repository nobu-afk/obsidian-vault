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

# Vaultルート
VAULT="/Users/ishiinobuyuki/Documents/Obsidian Vault"

# FTP設定（FTP情報_メインFTPアカウント.md より）
FTP_HOST="sv16489.xserver.jp"
FTP_USER="xs992119"

# FTP_PASS 自動取得（260515 改修）：
# 環境変数 FTP_PASS が未設定 or 空の場合、FTP情報ファイルから自動読込
# - フォーマット：「- FTPパスワード：`実パスワード`」を期待
# - stdout 流出防止：grep + sed のみで変数代入・echo しない
# - 260514 第 16 ラウンド「FTP パスワード stdout 流出」事故対策として set -x なしを維持
if [ -z "${FTP_PASS}" ]; then
  FTP_INFO_FILE="${VAULT}/06_開発/開発ツール/FTP情報_メインFTPアカウント.md"
  if [ -f "${FTP_INFO_FILE}" ]; then
    FTP_PASS=$(grep "^- FTPパスワード" "${FTP_INFO_FILE}" | sed 's/.*`\([^`]*\)`.*/\1/' | head -1)
  fi
fi

# FTP_PASS が依然未設定なら早期エラー
if [ -z "${FTP_PASS}" ]; then
  echo "[ERROR] FTP_PASS が未設定です。環境変数で渡すか、${FTP_INFO_FILE} にパスワードを記載してください" >&2
  exit 1
fi

FTP_BASE="ftp://${FTP_HOST}/growthfix.jp/public_html"
AUTH="${FTP_USER}:${FTP_PASS}"

# === ヘルパー：FTPアップロード（バックグラウンド実行・PID と label を回収）===
declare -a PIDS=()
declare -a LABELS=()
FAILED=0

upload() {
  local local_path="$1"
  local remote_path="$2"
  local label="$3"
  # -f: HTTP/FTP エラー時に non-zero exit（curl デフォルトは 4xx/5xx でも exit 0）
  curl -f -T "$local_path" "${FTP_BASE}/${remote_path}" --user "$AUTH" --ftp-create-dirs -s -w "${label}: %{http_code}\n" &
  PIDS+=("$!")
  LABELS+=("$label")
}

# === ヘルパー：背景 upload の exit code を個別回収 ===
# 旧: 素の `wait` は集計しないため、認証失敗・転送失敗が握り潰されていた
wait_all() {
  local rc
  for i in "${!PIDS[@]}"; do
    if ! wait "${PIDS[$i]}"; then
      rc=$?
      echo "[FAIL] ${LABELS[$i]} (exit=$rc)" >&2
      FAILED=$((FAILED + 1))
    fi
  done
  PIDS=()
  LABELS=()
}

# === グループ別デプロイ ===
deploy_shared() {
  echo "[共通アセット並列アップロード]"
  upload "$VAULT/_assets/js/tracking.js"           "assets/js/tracking.js"            "tracking.js"
  upload "$VAULT/_assets/css/tokens.css"           "assets/css/tokens.css"            "tokens.css"
  upload "$VAULT/_assets/css/lp-base.css"          "assets/css/lp-base.css"           "lp-base.css"
  upload "$VAULT/_assets/css/lp-scan-extras.css"   "assets/css/lp-scan-extras.css"    "lp-scan-extras.css"
  upload "$VAULT/05_プロダクト/_共通/question_block_styles.php" "shared/question_block_styles.php" "question_block_styles.php"
  wait_all
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
  # Recruit LP（260513 仮説 E v0.2・集める軸・引力の参謀（採用）・月 35 万・260514 22-DH 追加）
  upload "$VAULT/05_プロダクト/Gravity/Recruit/LP/index.html"  "gravity-recruit/index.html"   "Recruit LP"
  # Cultivate LP（260513 仮説 E v0.2・躍動する軸・変革の参謀（躍動）・月 50 万・260514 22-DH 追加）
  upload "$VAULT/05_プロダクト/Gravity/Cultivate/LP/index.html" "gravity-cultivate/index.html" "Cultivate LP"
  # Hub LP（Gravity TOP・_ブランド/LP/・本番 URL: https://growthfix.jp/gravity/ ・260515 deploy.sh lp 漏れ修正で追加）
  upload "$VAULT/05_プロダクト/Gravity/_ブランド/LP/index.html"  "gravity/index.html"           "Hub LP"
  upload "$VAULT/05_プロダクト/Gravity/_ブランド/LP/styles.css"  "gravity/styles.css"           "Hub CSS"
  upload "$VAULT/05_プロダクト/Gravity/_ブランド/LP/script.js"   "gravity/script.js"            "Hub script.js"
  wait_all
  echo "[LP完了]"
  echo ""
}

deploy_wp() {
  echo "[WhitePaper V9 アップロード]"
  upload "$VAULT/05_プロダクト/Gravity/WhitePaper/V9/index.html"           "whitepaper/index.html"           "WP V9 index.html"
  upload "$VAULT/05_プロダクト/Gravity/WhitePaper/V9/style.css"            "whitepaper/style.css"            "WP V9 style.css"
  upload "$VAULT/05_プロダクト/Gravity/WhitePaper/V9/images/gravity_map.svg" "whitepaper/images/gravity_map.svg" "WP V9 gravity_map.svg"
  upload "$VAULT/05_プロダクト/Gravity/WhitePaper/V9/images/loop_chart.svg"  "whitepaper/images/loop_chart.svg"  "WP V9 loop_chart.svg"
  wait_all
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
  wait_all
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

if [ "$FAILED" -gt 0 ]; then
  echo "[ERROR] デプロイ完了（$FAILED 件失敗）" >&2
  exit 1
fi
echo "全デプロイ完了"
