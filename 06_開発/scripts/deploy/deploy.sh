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

# === 並列度制限（260515 改修・race condition 対策）===
# 旧：無制限並列で FTP 530（Not logged in）が race condition で発生
# 新：MAX_PARALLEL（既定 5）でジョブ数制限 + wait_all で失敗自動リトライ
MAX_PARALLEL="${MAX_PARALLEL:-5}"

# === ヘルパー：FTPアップロード（バックグラウンド実行・PID と label を回収）===
declare -a PIDS=()
declare -a LABELS=()
declare -a LOCALS=()    # 260515 追加：リトライ用にローカルパス保存
declare -a REMOTES=()   # 260515 追加：リトライ用にリモートパス保存
FAILED=0

upload() {
  local local_path="$1"
  local remote_path="$2"
  local label="$3"

  # ====================================================================
  # Layer 4 ガード（260515 追加・WP 事故 4 件 構造防止）
  # 危険な local→remote 組み合わせを upload 前に検知して reject
  # 詳細：memory/feedback_wp_v9_v10_deploy_path_distinction_260515.md
  # ====================================================================

  # ガード 1: WP V9 本体を /whitepaper/ に送る → オプトイン LP 破壊（過去 3 回事故）
  if [[ "$local_path" == *"WhitePaper/V9"* && "$remote_path" == "whitepaper/"* ]]; then
    echo "🚨 [BLOCKED] WP V9 本体を /whitepaper/ に送ろうとしています。" >&2
    echo "   正しい送り先：/whitepaper-read/（オプトイン LP 保護）" >&2
    echo "   ローカル：$local_path" >&2
    echo "   リモート：$remote_path（拒否）" >&2
    FAILED=$((FAILED + 1))
    return 1
  fi

  # ガード 2: WP V10（草案）を本番に送る → 未完成 v 公開
  if [[ "$local_path" == *"WhitePaper/V10"* ]]; then
    echo "🚨 [BLOCKED] WP V10 は本番未投入の草案です。本来 04_GrowthFix/02_マーケティング/_WP_V10_草案_本番未投入/ に隔離されているはず。" >&2
    echo "   ローカル：$local_path" >&2
    echo "   再投入手順：04_GrowthFix/02_マーケティング/_WP_V10_草案_本番未投入/_README.md 参照" >&2
    FAILED=$((FAILED + 1))
    return 1
  fi

  # ガード 3: オプトイン LP を /whitepaper-read/ に送る → WP 本体上書き
  if [[ "$local_path" == *"whitepaper_optin"* && "$remote_path" == "whitepaper-read/"* ]]; then
    echo "🚨 [BLOCKED] オプトイン LP を /whitepaper-read/ に送ろうとしています。" >&2
    echo "   正しい送り先：/whitepaper/" >&2
    FAILED=$((FAILED + 1))
    return 1
  fi

  # ガード 4: アーカイブ・草案系の本番 upload を全面拒否
  if [[ "$local_path" == *"_archive"* || "$local_path" == *"_history"* || "$local_path" == *"_素材ストック"* || "$local_path" == *"_草案_本番未投入"* || "$local_path" == *"_DRAFT_DO_NOT_DEPLOY"* ]]; then
    echo "🚨 [BLOCKED] アーカイブ/草案ディレクトリからの upload は禁止されています。" >&2
    echo "   ローカル：$local_path" >&2
    FAILED=$((FAILED + 1))
    return 1
  fi

  # === 並列度制限（260515 改修）===
  # MAX_PARALLEL（既定 5）以上ジョブが走っていれば待機。FTP サーバーの同時接続制限回避。
  while [[ "$(jobs -rp | wc -l | tr -d ' ')" -ge "${MAX_PARALLEL}" ]]; do
    sleep 0.2
  done

  # -f: HTTP/FTP エラー時に non-zero exit（curl デフォルトは 4xx/5xx でも exit 0）
  curl -f -T "$local_path" "${FTP_BASE}/${remote_path}" --user "$AUTH" --ftp-create-dirs -s -w "${label}: %{http_code}\n" &
  PIDS+=("$!")
  LABELS+=("$label")
  LOCALS+=("$local_path")    # 260515 追加：リトライ用
  REMOTES+=("$remote_path")  # 260515 追加：リトライ用
}

# === ヘルパー：背景 upload の exit code を個別回収 + 自動リトライ ===
# 旧: 素の `wait` は集計しないため、認証失敗・転送失敗が握り潰されていた
# 260515 改修：失敗 upload を直列で最大 2 回リトライ（race condition による 530 対策）
wait_all() {
  local rc
  local -a failed_indices=()
  for i in "${!PIDS[@]}"; do
    if ! wait "${PIDS[$i]}"; then
      rc=$?
      echo "[FAIL] ${LABELS[$i]} (exit=$rc)" >&2
      failed_indices+=("$i")
    fi
  done

  # === 失敗 upload の自動リトライ（260515 追加・直列・最大 2 回）===
  if [[ ${#failed_indices[@]} -gt 0 ]]; then
    echo "🔁 失敗 ${#failed_indices[@]} 件を自動リトライ（直列・最大 2 回）" >&2
    for retry in 1 2; do
      local -a still_failed=()
      for i in "${failed_indices[@]}"; do
        if curl -f -T "${LOCALS[$i]}" "${FTP_BASE}/${REMOTES[$i]}" --user "$AUTH" --ftp-create-dirs -s -w "  [retry $retry] ${LABELS[$i]}: %{http_code}\n" 2>&1; then
          : # 成功
        else
          still_failed+=("$i")
        fi
        sleep 0.3  # FTP セッションクールダウン
      done
      failed_indices=("${still_failed[@]}")
      [[ ${#failed_indices[@]} -eq 0 ]] && break
    done

    # リトライ後も失敗したものを FAILED にカウント
    for i in "${failed_indices[@]}"; do
      echo "❌ リトライ後も失敗：${LABELS[$i]}" >&2
      FAILED=$((FAILED + 1))
    done
  fi

  # 配列クリア
  PIDS=()
  LABELS=()
  LOCALS=()
  REMOTES=()
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
  # Scan LP（260515 8 ページピボットで 301 リダイレクト先 = /gravity/。旧 LP は .htaccess が優先される）
  upload "$VAULT/05_プロダクト/Gravity/Scan/LP/index.html"     "gravity-scan/index.html"      "Scan LP"
  # Shift LP（260515 8 ページピボットで 301 リダイレクト先 = /gravity/。旧 LP は .htaccess が優先される）
  upload "$VAULT/05_プロダクト/Gravity/Shift/LP/index.html"    "gravity-shift/index.html"     "Shift LP"
  # Orbit LP（260515 8 ページピボットで 301 リダイレクト先 = /gravity/）
  upload "$VAULT/05_プロダクト/Gravity/Orbit/LP/index.html"    "gravity-orbit/index.html"     "Orbit LP"
  # Coaching LP（260515 8 ページピボット：/gravity-coaching/ → /gravity/coaching/ に物理移動）
  upload "$VAULT/05_プロダクト/Gravity/Coaching/LP/index.html" "gravity/coaching/index.html"  "Coaching LP (new)"
  upload "$VAULT/05_プロダクト/Gravity/Coaching/LP/.htaccess"  "gravity-coaching/.htaccess"   "Coaching 301"
  # Code LP（260515 8 ページピボット：/gravity-code/ → /gravity/code/ に物理移動）
  upload "$VAULT/05_プロダクト/Gravity/Code/LP/index.html"     "gravity/code/index.html"      "Code LP (new)"
  upload "$VAULT/05_プロダクト/Gravity/Code/LP/script.js"      "gravity/code/script.js"       "Code script.js (new)"
  upload "$VAULT/05_プロダクト/Gravity/Code/LP/.htaccess"      "gravity-code/.htaccess"       "Code 301"
  # Recruit LP（260513 仮説 E v0.2・集める軸・引力の参謀（採用）・月 35 万・260514 22-DH 追加）
  upload "$VAULT/05_プロダクト/Gravity/Recruit/LP/index.html"  "gravity-recruit/index.html"   "Recruit LP"
  # Cultivate LP（260513 仮説 E v0.2・躍動する軸・変革の参謀（躍動）・月 50 万・260514 22-DH 追加）
  upload "$VAULT/05_プロダクト/Gravity/Cultivate/LP/index.html" "gravity-cultivate/index.html" "Cultivate LP"
  # Hub LP（Gravity TOP・_ブランド/LP/・本番 URL: https://growthfix.jp/gravity/ ・260515 deploy.sh lp 漏れ修正で追加）
  upload "$VAULT/05_プロダクト/Gravity/_ブランド/LP/index.html"  "gravity/index.html"           "Hub LP"
  upload "$VAULT/05_プロダクト/Gravity/_ブランド/LP/styles.css"  "gravity/styles.css"           "Hub CSS"
  upload "$VAULT/05_プロダクト/Gravity/_ブランド/LP/script.js"   "gravity/script.js"            "Hub script.js"
  # コーポレート top + service + profile（本番 URL: https://growthfix.jp/ + /service/ + /profile/・260515 deploy.sh lp 漏れ修正で追加）
  upload "$VAULT/05_プロダクト/コーポレート/top_本番/index.html"     "index.html"          "コーポレート top"
  upload "$VAULT/05_プロダクト/コーポレート/service_本番/index.html" "service/index.html"  "コーポレート service"
  upload "$VAULT/05_プロダクト/コーポレート/profile_本番/index.html" "profile/index.html"  "コーポレート profile"
  # Scan web-diagnose（本番 URL: https://growthfix.jp/gravity-scan/web-diagnose/・260515 deploy.sh lp 漏れ修正で追加）
  upload "$VAULT/05_プロダクト/Gravity/Scan/web-diagnose_本番/index.html" "gravity-scan/web-diagnose/index.html" "Scan web-diagnose"
  # 8 ページピボット 301 リダイレクト（260515 追加・旧 5 LP → /gravity/ 統合）
  upload "$VAULT/05_プロダクト/Gravity/Recruit/LP/.htaccess"   "gravity-recruit/.htaccess"   "Recruit 301"
  upload "$VAULT/05_プロダクト/Gravity/Cultivate/LP/.htaccess" "gravity-cultivate/.htaccess" "Cultivate 301"
  upload "$VAULT/05_プロダクト/Gravity/Orbit/LP/.htaccess"     "gravity-orbit/.htaccess"     "Orbit 301"
  upload "$VAULT/05_プロダクト/Gravity/Shift/LP/.htaccess"     "gravity-shift/.htaccess"     "Shift 301"
  upload "$VAULT/05_プロダクト/Gravity/Scan/LP/.htaccess"      "gravity-scan/.htaccess"      "Scan 301"
  wait_all
  echo "[LP完了]"
  echo ""
}

deploy_wp() {
  echo "[WhitePaper V9 → /whitepaper-read/ アップロード（260515 オプトイン保護のためパス修正）]"
  # ⚠️ 不可侵：WP V9 本体は /whitepaper-read/ にのみ送る。/whitepaper/ はオプトイン LP の URL。
  # 詳細：memory/reference_whitepaper_url_structure.md / memory/feedback_wp_v9_v10_deploy_path_distinction_260515.md
  upload "$VAULT/05_プロダクト/Gravity/WhitePaper/V9/index.html"           "whitepaper-read/index.html"           "WP V9 index.html"
  upload "$VAULT/05_プロダクト/Gravity/WhitePaper/V9/style.css"            "whitepaper-read/style.css"            "WP V9 style.css"
  upload "$VAULT/05_プロダクト/Gravity/WhitePaper/V9/images/gravity_map.svg" "whitepaper-read/images/gravity_map.svg" "WP V9 gravity_map.svg"
  # loop_chart.svg はローカル不在のため除外（260515）
  wait_all
  echo "[WhitePaper V9 完了]"
  echo ""
}

deploy_optin() {
  echo "[WhitePaper オプトイン LP → /whitepaper/ アップロード]"
  # ⚠️ 不可侵：オプトイン LP は /whitepaper/ にのみ送る。WP V9 本体と混同禁止。
  upload "$VAULT/05_プロダクト/コーポレート/whitepaper_optin_本番/index.html" "whitepaper/index.html" "WP オプトイン LP"
  wait_all
  echo "[WhitePaper オプトイン LP 完了]"
  echo ""
}

deploy_diagnose() {
  echo "[診断ツール並列アップロード]"
  # === 旧有料版 Scan 診断（260515 完全廃止・アーカイブ化）===
  #   260514 22-DJ Scan 無料化決定 → 260515 サービスピボット最終締めで _archive_有料Scan_260515/ に移動
  #   現行運用は web-diagnose_本番/ → /gravity-scan/web-diagnose/（deploy.sh lp で deploy 済）
  #   旧 deploy 対象 7 ファイル（index.html / app.js / generate.php / style.css / web-diagnose.html / system_prompt.txt / jargon_map.json）は廃止
  #   本番サーバー側 /gravity-scan/diagnose/ は 301 リダイレクト → /gravity-scan/web-diagnose/ 統一が推奨（別途対応）

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
  optin)    deploy_optin ;;
  all)
    deploy_shared
    deploy_lp
    deploy_diagnose
    deploy_wp
    deploy_optin
    ;;
  *)
    echo "Usage: $0 [shared|lp|diagnose|wp|optin|all]"
    exit 1
    ;;
esac

if [ "$FAILED" -gt 0 ]; then
  echo "[WARNING] デプロイ完了（$FAILED 件失敗）── verify は継続実行" >&2
fi

# ====================================================================
# 自動 verify_deployment.sh 実行（260515 WP オプトイン破壊事故防止）
# 環境変数 SKIP_VERIFY=1 で抑制可能。upload FAIL があっても本番健全性検証は必ず実行
# ====================================================================
if [ "${SKIP_VERIFY:-0}" != "1" ]; then
  echo ""
  echo "🔒 verify_deployment.sh 自動実行（WP オプトイン保護等の本番健全性検証）"
  VERIFY_SCRIPT="$(dirname "${BASH_SOURCE[0]}")/verify_deployment.sh"
  if [ -f "$VERIFY_SCRIPT" ]; then
    if ! bash "$VERIFY_SCRIPT"; then
      echo "" >&2
      echo "🚨 [CRITICAL] verify_deployment.sh が異常を検知しました。本番事故の可能性。即時対応してください。" >&2
      exit 2
    fi
  else
    echo "⚠ verify_deployment.sh が見つかりません: $VERIFY_SCRIPT" >&2
  fi
fi

if [ "$FAILED" -gt 0 ]; then
  echo "[ERROR] アップロード $FAILED 件失敗（verify は通過）" >&2
  exit 1
fi
echo "全デプロイ完了"
