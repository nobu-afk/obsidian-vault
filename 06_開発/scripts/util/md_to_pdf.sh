#!/usr/bin/env bash
# md_to_pdf.sh ── MD → HTML → PDF 変換（Chrome ヘッドレス + pandoc）
# 図表 ASCII art を保護するため pre/code を monospace + 小さめフォントで CSS 指定
#
# 使い方：
#   bash md_to_pdf.sh <input.md> [output.pdf]
#
# 出力：
#   入力 MD と同フォルダに同名 .pdf を生成（output 指定なき場合）

set -e

INPUT="${1:?Usage: md_to_pdf.sh <input.md> [output.pdf]}"
OUTPUT="${2:-${INPUT%.md}.pdf}"
TITLE="$(basename "${INPUT%.md}")"
TMP_HTML="/tmp/md_to_pdf_$$.html"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# CSS 内蔵（図表 ASCII 保護のため pre/code は monospace + 9pt 厳密指定）
cat > "/tmp/md_to_pdf_style_$$.html" <<'HTML_HEAD'
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>__TITLE__</title>
<style>
  @page { size: A4; margin: 18mm 16mm; }
  body {
    font-family: -apple-system, "Hiragino Kaku Gothic ProN", "Noto Sans CJK JP", sans-serif;
    font-size: 10.5pt;
    line-height: 1.7;
    color: #1b1b1b;
    max-width: 100%;
  }
  h1 { font-size: 22pt; font-weight: 900; color: #0f172a; margin: 0 0 14pt; padding-bottom: 8pt; border-bottom: 3px solid #b8a88a; page-break-before: avoid; }
  h2 { font-size: 16pt; font-weight: 800; color: #0f172a; margin: 24pt 0 10pt; padding-left: 10pt; border-left: 5px solid #b8a88a; page-break-after: avoid; }
  h3 { font-size: 13pt; font-weight: 700; color: #0f172a; margin: 18pt 0 8pt; page-break-after: avoid; }
  h4 { font-size: 11pt; font-weight: 700; color: #334155; margin: 12pt 0 6pt; page-break-after: avoid; }
  p { margin: 0 0 8pt; }
  strong { color: #0f172a; font-weight: 700; }
  em { color: #b8a88a; font-style: normal; font-weight: 700; }
  blockquote { margin: 10pt 0; padding: 10pt 14pt; background: #f8f5ee; border-left: 3px solid #b8a88a; font-size: 10pt; line-height: 1.65; }
  ul, ol { margin: 4pt 0 8pt 18pt; padding: 0; }
  li { margin: 2pt 0; }
  hr { border: none; border-top: 1px dashed #cbd5e1; margin: 18pt 0; }

  /* ★ 図表（ASCII art）保護：monospace + 8pt + 行間 1.2 で alignment 維持 */
  pre {
    font-family: "SF Mono", "Menlo", "Consolas", "Courier New", monospace;
    font-size: 8pt;
    line-height: 1.2;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 4px;
    padding: 10pt 12pt;
    overflow-x: auto;
    white-space: pre;
    margin: 10pt 0;
    page-break-inside: avoid;
  }
  code {
    font-family: "SF Mono", "Menlo", "Consolas", "Courier New", monospace;
    font-size: 9pt;
    background: #f8fafc;
    padding: 1pt 4pt;
    border-radius: 3px;
    color: #0f172a;
  }
  pre code { background: transparent; padding: 0; font-size: inherit; }

  table { border-collapse: collapse; width: 100%; margin: 10pt 0; font-size: 9.5pt; page-break-inside: avoid; }
  th { background: #0f172a; color: #fff; font-weight: 700; padding: 6pt 8pt; text-align: left; border: 1px solid #0f172a; }
  td { padding: 6pt 8pt; border: 1px solid #e2e8f0; vertical-align: top; }
  tbody tr:nth-child(even) { background: #f8fafc; }

  a { color: #1e40af; text-decoration: underline; }

  /* 印刷時のページ送り制御 */
  h2, h3 { page-break-after: avoid; }
  pre, table, blockquote { page-break-inside: avoid; }
</style>
</head>
<body>
HTML_HEAD

# pandoc で MD → HTML（body 部分のみ）
pandoc --from=gfm --to=html5 --no-highlight "$INPUT" > "/tmp/md_to_pdf_body_$$.html"

# title 置換 + body 結合 + 閉じタグ
sed "s/__TITLE__/$TITLE/g" "/tmp/md_to_pdf_style_$$.html" > "$TMP_HTML"
cat "/tmp/md_to_pdf_body_$$.html" >> "$TMP_HTML"
echo "</body></html>" >> "$TMP_HTML"

echo "📄 HTML 中間ファイル: $TMP_HTML ($(wc -l < "$TMP_HTML") lines)"

# Chrome ヘッドレスで PDF 生成
"$CHROME" \
  --headless --disable-gpu --no-pdf-header-footer \
  --print-to-pdf="$OUTPUT" \
  --print-to-pdf-no-header \
  "file://$TMP_HTML" 2>&1 | grep -v "DevTools\|Fontconfig\|ContextResult" || true

# クリーンアップ
rm -f "/tmp/md_to_pdf_style_$$.html" "/tmp/md_to_pdf_body_$$.html" "$TMP_HTML"

if [[ -f "$OUTPUT" ]]; then
  SIZE=$(du -h "$OUTPUT" | awk '{print $1}')
  echo "✅ PDF 生成完了: $OUTPUT ($SIZE)"
else
  echo "❌ PDF 生成失敗"
  exit 1
fi
