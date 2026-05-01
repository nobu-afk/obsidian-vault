#!/usr/bin/env bash
# bump_cache_buster.sh
# 全LP/HTMLの mobile.css?v=YYYYMMDD[a-z] を新しいバージョンに一括更新する
#
# 使い方:
#   bash 06_開発/scripts/bump_cache_buster.sh                        # 自動：今日の日付+suffix で bump
#   bash 06_開発/scripts/bump_cache_buster.sh 20260429b               # 明示的に指定
#   bash 06_開発/scripts/bump_cache_buster.sh --target style.css      # mobile.css 以外も対象に
#   bash 06_開発/scripts/bump_cache_buster.sh --dry-run               # 実行せず変更箇所を表示
#
# 動作:
#   - 05_プロダクト 配下の *.html を対象
#   - mobile.css?v=YYYYMMDD[a-z] のパターンを検出して新バージョンに置換
#   - 変更前のバージョンと変更件数を表示
#   - --target で他の CSS（style.css 等）も指定可

set -e

# プロジェクトルートに移動（任意の場所から実行できるように）
cd "$(dirname "$0")/../.." || exit 1

TARGET_FILE="mobile.css"
DRY_RUN=false
NEW_VERSION=""

# 引数解析
while [[ $# -gt 0 ]]; do
  case "$1" in
    --target)
      TARGET_FILE="$2"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    *)
      NEW_VERSION="$1"
      shift
      ;;
  esac
done

# JST で今日の日付を取得（システムが UTC でも JST 基準）
TODAY=$(date -u +%Y%m%d -d '+9 hours' 2>/dev/null || date -v+9H +%Y%m%d 2>/dev/null || date +%Y%m%d)

# 現在のバージョンを検出
CURRENT_VERSION=$(grep -hoE "${TARGET_FILE}\?v=[0-9]{8}[a-z]" 05_プロダクト -r 2>/dev/null \
  | sed "s|${TARGET_FILE}?v=||" \
  | sort -u \
  | head -1)

if [[ -z "$CURRENT_VERSION" ]]; then
  echo "❌ ${TARGET_FILE}?v=YYYYMMDD[a-z] のパターンが見つかりません"
  exit 1
fi

# 新バージョンの自動決定
if [[ -z "$NEW_VERSION" ]]; then
  CURRENT_DATE="${CURRENT_VERSION:0:8}"
  CURRENT_SUFFIX="${CURRENT_VERSION:8:1}"

  if [[ "$CURRENT_DATE" == "$TODAY" ]]; then
    # 同日なら suffix を 1 つ進める（a→b→c→...）
    NEXT_SUFFIX=$(echo "$CURRENT_SUFFIX" | tr 'a-y' 'b-z')
    NEW_VERSION="${TODAY}${NEXT_SUFFIX}"
  else
    # 別日なら suffix を a に戻す
    NEW_VERSION="${TODAY}a"
  fi
fi

# 同じバージョンへの bump は無意味
if [[ "$CURRENT_VERSION" == "$NEW_VERSION" ]]; then
  echo "⚠️  既に ${NEW_VERSION} です。bump 不要"
  exit 0
fi

echo "📦 ${TARGET_FILE}?v=${CURRENT_VERSION} → ${TARGET_FILE}?v=${NEW_VERSION}"

# 対象ファイル一覧
TARGET_FILES=$(grep -lE "${TARGET_FILE}\?v=${CURRENT_VERSION}" 05_プロダクト -r --include="*.html" 2>/dev/null || true)

if [[ -z "$TARGET_FILES" ]]; then
  echo "❌ 該当ファイルなし"
  exit 1
fi

FILE_COUNT=$(echo "$TARGET_FILES" | wc -l | tr -d ' ')
echo "🎯 対象: ${FILE_COUNT} ファイル"
echo ""

if [[ "$DRY_RUN" == true ]]; then
  echo "[DRY-RUN] 変更されるファイル:"
  echo "$TARGET_FILES"
  exit 0
fi

# 一括置換（macOS BSD sed と GNU sed 両対応）
echo "$TARGET_FILES" | while IFS= read -r f; do
  if [[ "$OSTYPE" == "darwin"* ]]; then
    sed -i '' "s|${TARGET_FILE}?v=${CURRENT_VERSION}|${TARGET_FILE}?v=${NEW_VERSION}|g" "$f"
  else
    sed -i "s|${TARGET_FILE}?v=${CURRENT_VERSION}|${TARGET_FILE}?v=${NEW_VERSION}|g" "$f"
  fi
done

# 検証
NEW_COUNT=$(grep -lE "${TARGET_FILE}\?v=${NEW_VERSION}" 05_プロダクト -r --include="*.html" 2>/dev/null | wc -l | tr -d ' ')

echo "✅ 完了: ${NEW_COUNT} ファイルに新バージョン反映"
echo ""
echo "次のステップ:"
echo "  1. mobile.css または対象 CSS をデプロイ"
echo "  2. 変更された HTML を再デプロイ"
echo "  3. ブラウザで動作確認"
