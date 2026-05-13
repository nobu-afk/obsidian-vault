#!/bin/bash
# WhitePaper 安全デプロイスクリプト（260511 障害再発防止）
#
# 用途: WP V9 HTML 更新後の本番反映 + PDF 再生成 + デプロイを安全に行う
# 設計原則:
#   - WP V9 本体は /whitepaper-read/ のみにアップロード（/whitepaper/ には絶対に触らない）
#   - /whitepaper/ はオプトインフォーム専用
#   - オプトイン更新が必要な場合は明示的に --optin フラグを指定
#
# 使い方:
#   bash 06_開発/scripts/deploy_whitepaper.sh             # WP V9 本体のみ更新 + PDF 再生成
#   bash 06_開発/scripts/deploy_whitepaper.sh --optin     # オプトインフォームも同時更新
#   bash 06_開発/scripts/deploy_whitepaper.sh --skip-pdf  # PDF 再生成スキップ（HTML のみ）

set -e

VAULT="/Users/ishiinobuyuki/Documents/Obsidian Vault"
WP_BODY="$VAULT/05_プロダクト/Gravity/WhitePaper/V9/index.html"
WP_PDF="$VAULT/05_プロダクト/Gravity/WhitePaper/V9/gravity-whitepaper-v9.pdf"
OPTIN_HTML="$VAULT/05_プロダクト/コーポレート/whitepaper_optin_本番/index.html"

CONFIG_FTP="$VAULT/06_開発/scripts/config/config_ftp.json"
if [ ! -f "$CONFIG_FTP" ]; then
  echo "❌ FTP config が見つかりません: $CONFIG_FTP"
  echo "   既存スクリプトの値で再作成: { \"host\": \"sv16489.xserver.jp\", \"user\": \"xs992119\", \"pass\": \"...\" }"
  exit 1
fi
FTP_HOST=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['host'])" "$CONFIG_FTP")
FTP_USER=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['user'])" "$CONFIG_FTP")
FTP_PASS=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['pass'])" "$CONFIG_FTP")
FTP_BASE="ftp://${FTP_HOST}/growthfix.jp/public_html"

UPDATE_OPTIN=false
SKIP_PDF=false

for arg in "$@"; do
  case $arg in
    --optin) UPDATE_OPTIN=true ;;
    --skip-pdf) SKIP_PDF=true ;;
  esac
done

echo "🔒 WhitePaper 安全デプロイ開始"
echo ""

# ========================================
# Step 1: WP V9 本体を /whitepaper-read/ にアップロード
# ========================================
echo "📤 Step 1: WP V9 本体 → /whitepaper-read/ にアップロード"
if [ ! -f "$WP_BODY" ]; then
  echo "❌ WP V9 本体が見つかりません: $WP_BODY"
  exit 1
fi

CODE=$(curl -s -T "$WP_BODY" "$FTP_BASE/whitepaper-read/index.html" --user "$FTP_USER:$FTP_PASS" -w "%{http_code}" -o /dev/null)
if [[ "$CODE" == "226" ]]; then
  echo "  ✅ /whitepaper-read/: HTTP $CODE"
else
  echo "  ❌ /whitepaper-read/: HTTP $CODE"
  exit 1
fi
sleep 2

# ========================================
# Step 2: オプトインフォーム更新（明示指定時のみ）
# ========================================
if [ "$UPDATE_OPTIN" = true ]; then
  echo ""
  echo "📤 Step 2: オプトインフォーム → /whitepaper/ にアップロード（--optin 指定）"
  if [ ! -f "$OPTIN_HTML" ]; then
    echo "❌ オプトインフォーム HTML が見つかりません: $OPTIN_HTML"
    exit 1
  fi
  CODE=$(curl -s -T "$OPTIN_HTML" "$FTP_BASE/whitepaper/index.html" --user "$FTP_USER:$FTP_PASS" -w "%{http_code}" -o /dev/null)
  if [[ "$CODE" == "226" ]]; then
    echo "  ✅ /whitepaper/: HTTP $CODE（オプトインフォーム更新）"
  else
    echo "  ❌ /whitepaper/: HTTP $CODE"
    exit 1
  fi
  sleep 2
else
  echo ""
  echo "🛡️  Step 2 スキップ: /whitepaper/ には触りません（オプトインフォーム保護）"
  echo "    オプトイン更新が必要な場合は --optin フラグを指定してください"
fi

# ========================================
# Step 3: PDF 再生成（オプション）
# ========================================
if [ "$SKIP_PDF" = false ]; then
  echo ""
  echo "🖨️  Step 3: PDF 再生成"
  TMP_PDF="/tmp/gravity-whitepaper-v9.pdf"
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
    --headless --disable-gpu --no-pdf-header-footer \
    --print-to-pdf="$TMP_PDF" \
    "https://growthfix.jp/whitepaper-read/?v=$(date +%s)" 2>&1 | grep -E "bytes written|error" | tail -3

  if [ ! -f "$TMP_PDF" ]; then
    echo "  ❌ PDF 生成失敗"
    exit 1
  fi

  cp "$TMP_PDF" "$WP_PDF"
  echo "  ✅ ローカル PDF 更新: $WP_PDF"

  echo ""
  echo "📤 Step 4: PDF → /whitepaper.pdf にアップロード"
  CODE=$(curl -s -T "$WP_PDF" "$FTP_BASE/whitepaper.pdf" --user "$FTP_USER:$FTP_PASS" -w "%{http_code}" -o /dev/null)
  if [[ "$CODE" == "226" ]]; then
    echo "  ✅ /whitepaper.pdf: HTTP $CODE（$(ls -la "$WP_PDF" | awk '{print $5}') bytes）"
  else
    echo "  ❌ /whitepaper.pdf: HTTP $CODE"
    exit 1
  fi
fi

# ========================================
# Step 5: 安全性検証
# ========================================
echo ""
echo "🔍 Step 5: 安全性検証"
sleep 3

# /whitepaper/ にオプトインフォームが残っているか確認
OPTIN_BODY=$(curl -s "https://growthfix.jp/whitepaper/")
if echo "$OPTIN_BODY" | grep -q 'name="email"\|type="email"'; then
  echo "  ✅ /whitepaper/ にオプトインフォーム（email 入力欄）が存在"
else
  echo "  ❌ /whitepaper/ にオプトインフォームが見つからない（事故の可能性）"
  echo "     復旧コマンド: bash 06_開発/scripts/deploy_whitepaper.sh --optin --skip-pdf"
  exit 1
fi

# /whitepaper-read/ に WP V9 本体があるか確認
WP_READ_BODY=$(curl -s "https://growthfix.jp/whitepaper-read/")
if echo "$WP_READ_BODY" | grep -q 'hero-title\|chapter-title\|引力経営'; then
  echo "  ✅ /whitepaper-read/ に WP V9 本体（hero-title / chapter-title 等）が存在"
else
  echo "  ❌ /whitepaper-read/ に WP V9 本体が見つからない"
  exit 1
fi

echo ""
echo "🎉 WhitePaper 安全デプロイ完了"
