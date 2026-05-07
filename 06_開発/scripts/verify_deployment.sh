#!/usr/bin/env bash
# verify_deployment.sh
# 20 LP の本番デプロイ後の HTTP 検証＋整合性チェック（260502 /gravity-shift-a/ 追加）
#
# 使い方:
#   bash 06_開発/scripts/verify_deployment.sh
#
# チェック項目:
#   1. 全 20 LP が HTTP 200
#   2. mobile.css が HTTP 200 + 同一バージョン
#   3. seminar-bar.js が HTTP 200
#   4. tracking.js が HTTP 200
#   5. 各 LP に seminar-bar.js が参照されている
#   6. 各 LP に古いインライン .next-seminar-bar が残っていない（JS 化検証）

set -e
cd "$(dirname "$0")/../.." || exit 1

PASS=0
FAIL=0
WARN=0

# 20 LP の URL（260502 /gravity-shift-a/ 追加で 19 → 20）
LPS=(
  "https://growthfix.jp/"
  "https://growthfix.jp/gravity/"
  "https://growthfix.jp/gravity-code/"
  "https://growthfix.jp/gravity-code/executive/"
  "https://growthfix.jp/gravity-blueprint/"
  "https://growthfix.jp/gravity-blueprint/diagnose/"
  "https://growthfix.jp/gravity-coaching/"
  "https://growthfix.jp/gravity-shift/"
  "https://growthfix.jp/gravity-shift-a/"
  "https://growthfix.jp/gravity-orbit/"
  "https://growthfix.jp/service/"
  "https://growthfix.jp/profile/"
  "https://growthfix.jp/achievement/"
  "https://growthfix.jp/contact/"
  "https://growthfix.jp/privacy-policy/"
  "https://growthfix.jp/news/"
  "https://growthfix.jp/news/site-renewal/"
  "https://growthfix.jp/news/gravity-release/"
  "https://growthfix.jp/knowledge/"
  "https://growthfix.jp/whitepaper/"
)

# 共通アセット
ASSETS=(
  "https://growthfix.jp/assets/css/mobile.css"
  "https://growthfix.jp/assets/js/seminar-bar.js"
  "https://growthfix.jp/assets/js/tracking.js"
)

echo "🌐 GrowthFix 20 LP デプロイ検証"
echo ""

# 1. 共通アセット
echo "📦 共通アセット"
for url in "${ASSETS[@]}"; do
  code=$(curl -s -o /dev/null -w "%{http_code}" -I "$url")
  if [[ "$code" == "200" ]]; then
    echo "  ✅ $code: $url"
    PASS=$((PASS+1))
  else
    echo "  ❌ $code: $url"
    FAIL=$((FAIL+1))
  fi
done
echo ""

# 2. 19 LP
echo "🎯 20 LP"
for url in "${LPS[@]}"; do
  # HTTP コード取得
  code=$(curl -s -o /tmp/_lp_body.html -w "%{http_code}" -L "$url")

  if [[ "$code" != "200" ]]; then
    echo "  ❌ HTTP $code: $url"
    FAIL=$((FAIL+1))
    continue
  fi

  # 各種コンテンツチェック（grep -c 結果のみ・空白除去で算術比較を安全化）
  has_seminar_script=$(grep -c "seminar-bar.js" /tmp/_lp_body.html 2>/dev/null | tr -d '[:space:]' || echo "0")
  has_inline_bar=$(grep -c "next-seminar-bar" /tmp/_lp_body.html 2>/dev/null | tr -d '[:space:]' || echo "0")
  has_mobile_css=$(grep -c "mobile.css" /tmp/_lp_body.html 2>/dev/null | tr -d '[:space:]' || echo "0")
  : "${has_seminar_script:=0}"
  : "${has_inline_bar:=0}"
  : "${has_mobile_css:=0}"

  issues=()

  if [[ "$has_seminar_script" == "0" ]]; then
    issues+=("seminar-bar.js 未参照")
  fi

  # JS 化したので、HTML に next-seminar-bar が残っていたら異常
  if [[ "$has_inline_bar" -gt 0 ]]; then
    issues+=("インラインバー残留($has_inline_bar)")
  fi

  if [[ "$has_mobile_css" == "0" ]]; then
    issues+=("mobile.css 未参照")
  fi

  if [[ ${#issues[@]} -eq 0 ]]; then
    echo "  ✅ 200: $url"
    PASS=$((PASS+1))
  else
    echo "  ⚠️  200 (要確認): $url"
    for issue in "${issues[@]}"; do
      echo "       └ $issue"
    done
    WARN=$((WARN+1))
  fi
done
echo ""

# 3. mobile.css バージョン整合性
echo "🔢 mobile.css バージョン整合性"
versions=$(for url in "${LPS[@]}"; do
  curl -s "$url" 2>/dev/null | grep -oE "mobile\.css\?v=[0-9a-z]+" | head -1
done | sort -u | wc -l | tr -d ' ')

if [[ "$versions" == "1" ]]; then
  one_version=$(curl -s "${LPS[0]}" 2>/dev/null | grep -oE "mobile\.css\?v=[0-9a-z]+" | head -1)
  echo "  ✅ 全 20 LP で同一バージョン ($one_version)"
  PASS=$((PASS+1))
else
  echo "  ⚠️  $versions 種類のバージョンが混在（要 bump 統一）"
  WARN=$((WARN+1))
fi
echo ""

# 集計
TOTAL=$((PASS+FAIL+WARN))
echo "📊 検証結果"
echo "  ✅ PASS: $PASS"
echo "  ⚠️  WARN: $WARN"
echo "  ❌ FAIL: $FAIL"
echo "  合計: $TOTAL"

if [[ "$FAIL" -gt 0 ]]; then
  echo ""
  echo "❌ FAIL があります。再デプロイ要"
  exit 1
elif [[ "$WARN" -gt 0 ]]; then
  echo ""
  echo "⚠️  WARN があります。確認推奨"
  exit 0
else
  echo ""
  echo "🎉 全項目クリア"
  exit 0
fi
