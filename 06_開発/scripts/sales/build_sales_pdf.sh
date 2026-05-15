#!/bin/bash
# build_sales_pdf.sh — 営業資料マスター HTML → PDF 変換（260515 8 ページピボット §7）
#
# SSOT:
#   - 仕様書：04_GrowthFix/02_マーケティング/260515_8pages_pivot_v1.0_仕様書.md §7
#   - 入力：05_プロダクト/コーポレート/sales_本番/master/index.html
#   - 出力：05_プロダクト/コーポレート/sales_本番/pdf/YYMMDD_営業資料_v{VERSION}.pdf
#
# 変換ツール優先順位（先に見つかったものを使用）:
#   1. Google Chrome (--headless --print-to-pdf) ← Mac デフォルト想定
#   2. wkhtmltopdf (Homebrew install)
#   3. weasyprint (pip install weasyprint)
#
# Usage:
#   bash 06_開発/scripts/sales/build_sales_pdf.sh                  # v0.1 で生成
#   bash 06_開発/scripts/sales/build_sales_pdf.sh 1.0              # v1.0 で生成
#   bash 06_開発/scripts/sales/build_sales_pdf.sh 1.0 --open       # 生成後 PDF を開く
#
# Exit code:
#   0: 成功
#   1: 入力 HTML 不在
#   2: 変換ツール不在
#   3: PDF 生成失敗

set -e

# ─────────────────────────────────────────────────────────────
# 引数解析
# ─────────────────────────────────────────────────────────────
VERSION="${1:-0.1}"
OPEN_AFTER="${2:-}"

# ─────────────────────────────────────────────────────────────
# パス定義
# ─────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VAULT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
SALES_ROOT="$VAULT_ROOT/05_プロダクト/コーポレート/sales_本番"
INPUT_HTML="$SALES_ROOT/master/index.html"
OUTPUT_DIR="$SALES_ROOT/pdf"
TIMESTAMP=$(TZ='Asia/Tokyo' date +%y%m%d)
OUTPUT_PDF="$OUTPUT_DIR/${TIMESTAMP}_営業資料_v${VERSION}.pdf"

# 色付き出力
RED='\033[0;31m'
YEL='\033[0;33m'
GRN='\033[0;32m'
BLU='\033[0;34m'
NC='\033[0m'

# ─────────────────────────────────────────────────────────────
# 入力検証
# ─────────────────────────────────────────────────────────────
echo "================================================"
echo "GrowthFix 営業資料 PDF ビルド v${VERSION}"
echo "================================================"

if [ ! -f "$INPUT_HTML" ]; then
  printf "${RED}❌ 入力 HTML が見つかりません: %s${NC}\n" "$INPUT_HTML"
  exit 1
fi

mkdir -p "$OUTPUT_DIR"
printf "${BLU}入力:${NC} %s\n" "$INPUT_HTML"
printf "${BLU}出力:${NC} %s\n" "$OUTPUT_PDF"
echo ""

# ─────────────────────────────────────────────────────────────
# 変換ツール検出
# ─────────────────────────────────────────────────────────────
CHROME_BIN=""
if [ -f "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" ]; then
  CHROME_BIN="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
elif command -v google-chrome >/dev/null 2>&1; then
  CHROME_BIN="google-chrome"
elif command -v chromium >/dev/null 2>&1; then
  CHROME_BIN="chromium"
fi

WKHTMLTOPDF_BIN=""
if command -v wkhtmltopdf >/dev/null 2>&1; then
  WKHTMLTOPDF_BIN="wkhtmltopdf"
fi

WEASYPRINT_AVAILABLE=0
if python3 -c "import weasyprint" 2>/dev/null; then
  WEASYPRINT_AVAILABLE=1
fi

# ─────────────────────────────────────────────────────────────
# PDF 生成
# ─────────────────────────────────────────────────────────────
if [ -n "$CHROME_BIN" ]; then
  printf "${GRN}✓ 変換ツール: Google Chrome ヘッドレス${NC}\n"
  echo "実行中..."
  # Chrome は file:// URL で日本語パスを扱う際にパーセントエンコード推奨
  # absolute path → file:// URL（簡易・スペース対応）
  INPUT_URL="file://${INPUT_HTML// /%20}"

  "$CHROME_BIN" \
    --headless=new \
    --disable-gpu \
    --no-sandbox \
    --no-pdf-header-footer \
    --print-to-pdf-no-header \
    --print-to-pdf="$OUTPUT_PDF" \
    --virtual-time-budget=10000 \
    "$INPUT_URL" 2>&1 | grep -v "DevTools\|GPU\|Warning" || true

elif [ -n "$WKHTMLTOPDF_BIN" ]; then
  printf "${GRN}✓ 変換ツール: wkhtmltopdf${NC}\n"
  echo "実行中..."
  wkhtmltopdf \
    --enable-local-file-access \
    --print-media-type \
    --page-size A4 \
    --margin-top 15mm \
    --margin-bottom 15mm \
    --margin-left 15mm \
    --margin-right 15mm \
    "$INPUT_HTML" "$OUTPUT_PDF"

elif [ "$WEASYPRINT_AVAILABLE" -eq 1 ]; then
  printf "${GRN}✓ 変換ツール: weasyprint${NC}\n"
  echo "実行中..."
  python3 -c "
from weasyprint import HTML
HTML('$INPUT_HTML').write_pdf('$OUTPUT_PDF')
"

else
  printf "${RED}❌ PDF 変換ツールが見つかりません${NC}\n"
  echo "以下のいずれかをインストールしてください："
  echo "  1. Google Chrome（推奨・既定で利用可）→ /Applications/ に配置"
  echo "  2. wkhtmltopdf → brew install wkhtmltopdf"
  echo "  3. weasyprint  → pip3 install weasyprint"
  exit 2
fi

# ─────────────────────────────────────────────────────────────
# 出力検証
# ─────────────────────────────────────────────────────────────
if [ ! -f "$OUTPUT_PDF" ]; then
  printf "${RED}❌ PDF 生成失敗${NC}\n"
  exit 3
fi

PDF_SIZE=$(du -h "$OUTPUT_PDF" | cut -f1)
PDF_BYTES=$(stat -f%z "$OUTPUT_PDF" 2>/dev/null || stat -c%s "$OUTPUT_PDF")

if [ "$PDF_BYTES" -lt 10000 ]; then
  printf "${YEL}⚠ PDF サイズが小さすぎます（%s）─ 生成エラーの可能性${NC}\n" "$PDF_SIZE"
fi

echo ""
echo "================================================"
printf "${GRN}✅ PDF 生成完了${NC}\n"
echo "================================================"
printf "${BLU}ファイル:${NC} %s\n" "$OUTPUT_PDF"
printf "${BLU}サイズ:${NC}   %s（%s bytes）\n" "$PDF_SIZE" "$PDF_BYTES"
echo ""

# ─────────────────────────────────────────────────────────────
# 後処理（オプション）
# ─────────────────────────────────────────────────────────────
if [ "$OPEN_AFTER" = "--open" ]; then
  echo "PDF を開きます..."
  open "$OUTPUT_PDF"
fi

# ─────────────────────────────────────────────────────────────
# 運用メモ
# ─────────────────────────────────────────────────────────────
cat <<EOF

────────────────────────────────────────
📋 次の運用ステップ
────────────────────────────────────────
1. 商談配布：上記 PDF を直接送付（限定公開・商談相手のみ）
2. オンライン共有（限定公開）：
   bash 06_開発/scripts/deploy/deploy.sh sales
   → https://growthfix.jp/sales/master-{HASH}/ で閲覧可
3. v1.0 化：本資料 v0.1 骨格 → 個社事例・実証数値追加で v1.0 完成版に
4. ハッシュ rotation：半年 1 回程度（仕様書 §7.2）
EOF
