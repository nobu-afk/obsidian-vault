#!/bin/bash
# lint_consistency.sh — GrowthFix LP/コーポレート/WP の整合性チェック
# SSOT: 05_プロダクト/_共通/SSOT_用語と定義.md
# 使い方: bash "06_開発/scripts/lint_consistency.sh"
# 終了コード: 0=全通過 / 1=エラーあり

ROOT="/Users/ishiinobuyuki/Documents/Obsidian Vault/05_プロダクト"
ERRORS=0
WARNINGS=0

# 色付き出力
RED='\033[0;31m'
YEL='\033[0;33m'
GRN='\033[0;32m'
NC='\033[0m'

echo "========================================"
echo "GrowthFix 整合性チェック ($(date +%Y-%m-%d_%H:%M))"
echo "SSOT: 05_プロダクト/_共通/SSOT_用語と定義.md"
echo "========================================"

# ----------------------------------------------------------------------
# 禁止語スキャン基盤（260514 夜・TSV 外出し + 1 パス grep に refactor）
#   旧: check_forbidden / check_forbidden_warning を 100+ 回呼び出し
#       → 毎回 grep -rln フルスキャン（数十秒 worst case）
#   新: forbidden_terms.tsv を読み込み、1 度の find + 1 度の grep -F -f で
#       ヒットファイルを絞り込んだ後、ヒット時のみ term 別に micro-grep
# ----------------------------------------------------------------------
LINT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TSV="$LINT_DIR/forbidden_terms.tsv"

# 全 HTML ファイルキャッシュ（exclude ルール込み）
HTML_LIST=$(mktemp)
trap 'rm -f "$HTML_LIST" "$PATTERNS_FILE" 2>/dev/null' EXIT
find "$ROOT" -type f -name "*.html" \
  -not -path "*/_archive/*" \
  -not -path "*/_archive_obsolete/*" \
  -not -path "*/レポート/*" \
  ! -name "*template*" \
  ! -name "growthfix-*-index.html" \
  -print > "$HTML_LIST"

# 1 パス grep でヒットファイルを絞り込み
PATTERNS_FILE=$(mktemp)
awk -F'\t' 'NF >= 3 && $1 !~ /^#/ && $1 != "" { print $3 }' "$TSV" | sort -u > "$PATTERNS_FILE"

if [ -s "$HTML_LIST" ] && [ -s "$PATTERNS_FILE" ]; then
  HIT_FILES=$(tr '\n' '\0' < "$HTML_LIST" | xargs -0 grep -F -l -f "$PATTERNS_FILE" 2>/dev/null)
else
  HIT_FILES=""
fi
# error レベル用：*_backup_* を追加除外（旧 check_forbidden の挙動）
HIT_FILES_NO_BACKUP=$(echo "$HIT_FILES" | grep -v "_backup_")

# TSV 1 行に対する判定・出力
scan_one_term() {
  local section="$1"
  local level="$2"
  local term="$3"
  local reason="$4"
  local replace="$5"
  local extra_exclude="$6"

  local search_pool
  if [ "$level" = "error" ]; then
    search_pool="$HIT_FILES_NO_BACKUP"
  else
    search_pool="$HIT_FILES"
  fi

  # extra_exclude（glob 形式・*seminar-acting* 等）→ パスフィルタに変換
  if [ -n "$extra_exclude" ]; then
    local exc_substr
    exc_substr=$(echo "$extra_exclude" | sed 's/\*//g')
    search_pool=$(echo "$search_pool" | grep -v -- "$exc_substr")
  fi

  [ -z "$search_pool" ] && return

  local found
  found=$(echo "$search_pool" | tr '\n' '\0' | xargs -0 grep -F -l "$term" 2>/dev/null)
  [ -z "$found" ] && return

  if [ "$level" = "error" ]; then
    printf "${RED}❌ 禁止語「%s」発見${NC}（理由: %s → 代替: %s）\n" "$term" "$reason" "$replace"
    echo "$found" | sed "s|$ROOT/|     |"
    ERRORS=$((ERRORS + 1))
  else
    local count
    count=$(echo "$found" | wc -l | tr -d ' ')
    printf "${YEL}⚠ 移行期警告「%s」（%s ファイル）${NC}（理由: %s → 代替: %s）\n" "$term" "$count" "$reason" "$replace"
    echo "$found" | sed "s|$ROOT/|     |"
    WARNINGS=$((WARNINGS + 1))
  fi
}

# 指定 section の TSV エントリを順に scan
scan_forbidden_section() {
  local target_section="$1"
  while IFS=$'\t' read -r section level term reason replace extra_exclude; do
    [[ -z "$section" ]] && continue
    [[ "$section" =~ ^# ]] && continue
    [[ "$section" != "$target_section" ]] && continue
    scan_one_term "$section" "$level" "$term" "$reason" "$replace" "$extra_exclude"
  done < "$TSV"
}

# 共通: 必須語チェック関数（特定ファイルに含まれているべき）
check_required() {
  local file="$1"
  local term="$2"
  local count
  count=$(grep -c "$term" "$ROOT/$file" 2>/dev/null)
  count=${count:-0}
  if [ "$count" -eq 0 ]; then
    printf "${RED}❌ %s に「%s」なし${NC}\n" "$file" "$term"
    ERRORS=$((ERRORS + 1))
    return 1
  else
    printf "${GRN}✓${NC} %s ── 「%s」 %s 件\n" "$file" "$term" "$count"
    return 0
  fi
}

# ----------------------------------------------------------------------
# 1. 廃止用語・禁止語チェック（High）
# 　 禁止語リストは forbidden_terms.tsv 外出し（260514 夜 refactor）
# ----------------------------------------------------------------------
echo ""
echo "[1] 廃止用語・禁止語チェック"

scan_forbidden_section "1"

[ "$ERRORS" -eq 0 ] && echo -e "${GRN}✓${NC} 禁止語なし"

# ----------------------------------------------------------------------
# 1.5 移行期警告（260430 SSOT 追加・LP 修正タスク待ち）
# 　 警告語リストは forbidden_terms.tsv 外出し（260514 夜 refactor）
# ----------------------------------------------------------------------
echo ""
echo "[1.5] 移行期警告（260430 SSOT 追加・LP 修正タスク待ち）"

scan_forbidden_section "1.5"

[ "$WARNINGS" -eq 0 ] && echo -e "${GRN}✓${NC} 移行期警告なし"

# ----------------------------------------------------------------------
# 1.6 雛形（_共通/ template）警告（260430 SSOT 追加・雛形運用ルール）
# CLAUDE.md「共通部変更は雛形を先に更新してから各LPに展開」のため雛形をチェック
# ----------------------------------------------------------------------
echo ""
echo "[1.6] 雛形（_共通/ template）の禁止語チェック"

check_template_warning() {
  local term="$1"
  local replace="$2"
  local found
  found=$(grep -rln "$term" "$ROOT/_共通" --include="*.html" 2>/dev/null)
  if [ -n "$found" ]; then
    local count
    count=$(echo "$found" | wc -l | tr -d ' ')
    printf "${YEL}⚠ 雛形に旧表記「%s」（%s ファイル）${NC} → 代替: %s\n" "$term" "$count" "$replace"
    echo "$found" | sed "s|$ROOT/|     |"
    WARNINGS=$((WARNINGS + 1))
  fi
}

template_warnings_before=$WARNINGS
check_template_warning "組織の引力研究の人" "引力経営提唱者 ／ 引力の参謀"
check_template_warning "採用に強い会社をつくる" "優秀人材が躍動する会社をつくる"
[ "$WARNINGS" -eq "$template_warnings_before" ] && echo -e "${GRN}✓${NC} 雛形 OK"

# ----------------------------------------------------------------------
# [1.7] 月額表記必須語チェック（v5.4・260514 夜 v3.0 反映・月額制 + 最低 6 ヶ月）
# v5.4 確定価格マップ:
#   - Recruit (集まる):     月 35 万・最低 6 ヶ月（RT-1〜RT-6）
#   - Cultivate (躍動する): 月 50 万・最低 6 ヶ月（CT-1〜CT-6）
#   - Orbit (留まる):       月 5 万・最低 6 ヶ月 + 5 年継続装置（OT-1〜OT-6・260514 v3.0 で月 15 万 → 月 5 万）
#   - Shift (R+C 複合):     月 85 万・段階移行型（R 6 ヶ月 → C 6 ヶ月）
# Coaching = 38 万 6 ヶ月一括維持（月額化しない）
# 検出方針：各 LP に v5.0 月額表記が含まれているかを必須語的にチェック
# ----------------------------------------------------------------------
echo ""
echo "[1.7] 月額表記必須語チェック（v5.0・260514 月額制）"

check_monthly_pricing() {
  local lp_path="$1"
  local label="$2"
  local pattern="$3"  # 「月 X 万」の検出パターン（egrep 形式）
  local f="$ROOT/$lp_path"
  if [ ! -f "$f" ]; then
    printf "${YEL}⚠${NC} %s ── LP ファイル不在（%s）\n" "$label" "$lp_path"
    WARNINGS=$((WARNINGS + 1))
    return
  fi
  local monthly_count
  monthly_count=$(grep -cE "$pattern" "$f" 2>/dev/null)
  monthly_count=${monthly_count:-0}
  if [ "$monthly_count" -eq 0 ]; then
    printf "${YEL}⚠ %s 月額表記なし${NC}（v5.0 SSOT: 月額制 + 最低 6 ヶ月）\n" "$label"
    WARNINGS=$((WARNINGS + 1))
  else
    printf "${GRN}✓${NC} %s 月額表記あり（%s 件）\n" "$label" "$monthly_count"
  fi
}

check_monthly_pricing "Gravity/Recruit/LP/index.html" "Recruit（月 35 万・最低 6 ヶ月）" "月 ?35 *万"
check_monthly_pricing "Gravity/Cultivate/LP/index.html" "Cultivate（月 50 万・最低 6 ヶ月）" "月 ?50 *万"
check_monthly_pricing "Gravity/Orbit/LP/index.html" "Orbit（月 5 万・最低 6 ヶ月）" "月 ?5 *万"
check_monthly_pricing "Gravity/Shift/LP/index.html" "Shift（R+C 月 85 万・段階移行型）" "月 ?85 *万|段階移行"

# ----------------------------------------------------------------------
# 2. 各サービスLPに参謀名タグラインがあるか
# ----------------------------------------------------------------------
echo ""
echo "[2] 5サービスLPの参謀名タグライン整合"

check_required "Gravity/Code/LP/index.html" "引力の参謀"
check_required "Gravity/Scan/LP/index.html" "引力の参謀（組織軸）"
check_required "Gravity/Coaching/LP/index.html" "心の参謀"
check_required "Gravity/Orbit/LP/index.html" "共鳴の参謀"
# 260503 β 並列型・新設 LP（Gravity Recruit / Gravity Cultivate・260505 リネーム・260514 SSOT v5.0 整合：参謀名（軸）形式に統一）
check_required "Gravity/Recruit/LP/index.html" "引力の参謀（採用）"
check_required "Gravity/Cultivate/LP/index.html" "変革の参謀（躍動）"
# 260503 minimal LP（Push 型：GravityShift = R+A 複合 / Pull 型：GravityCoaching = 心の参謀・記載あり/リンクなし）：他ページからのリンクチェックは [5.5]/[5.6] で対応

# ----------------------------------------------------------------------
# 3. Coaching 価格の正解表記が存在するか
# ----------------------------------------------------------------------
echo ""
echo "[3] Coaching 価格 38万 表記"
correct_count=$(grep -rln "Coaching（38万・6ヶ月" "$ROOT" --include="*.html" --exclude-dir="_archive" 2>/dev/null | wc -l | tr -d ' ')
printf "${GRN}✓${NC} 「Coaching（38万・6ヶ月）」表記 ── %s ファイル\n" "$correct_count"

# ----------------------------------------------------------------------
# 4. WP V9 ページ数表記
# ----------------------------------------------------------------------
echo ""
echo "[4] WhitePaper ページ数表記"
wp_25=$(grep -rln "25 *ページ" "$ROOT" --include="*.html" --exclude-dir="_archive" 2>/dev/null | wc -l | tr -d ' ')
printf "${GRN}✓${NC} 「25 ページ」表記 ── %s ファイル\n" "$wp_25"

# ----------------------------------------------------------------------
# 5. サービスLPに「TOPのFAQ」導線があるか（minimal LP は除外）
# 260503: GravityShift は minimal LP 化により対象外（Orbit パターン同様）
# ----------------------------------------------------------------------
echo ""
echo "[5] サービスLPの「TOP のFAQ」導線（minimal LP 除外）"
top_link_missing=0
for lp in Gravity/Code Gravity/Scan Gravity/Recruit Gravity/Cultivate; do
  count=$(grep -c "Gravity シリーズ TOP のよくある質問" "$ROOT/$lp/LP/index.html" 2>/dev/null)
  count=${count:-0}
  if [ "$count" -eq 0 ]; then
    printf "${YEL}⚠${NC} %s/LP に「Gravity シリーズ TOP のよくある質問」リンクなし\n" "$lp"
    WARNINGS=$((WARNINGS + 1))
    top_link_missing=$((top_link_missing + 1))
  fi
done
[ "$top_link_missing" -eq 0 ] && echo -e "${GRN}✓${NC} 全 LP（CODE/Scan/Recruit/Cultivate）に TOP 導線あり ／ GravityShift/Orbit/Coaching は minimal LP 運用のため対象外"

# ----------------------------------------------------------------------
# 5.5 Gravity Shift minimal LP 運用チェック（260503 確定・Orbit パターン）
# Hub / コーポレート / 各 LP フッターに Gravity Shift カード/リンクが載っていたら警告
# ----------------------------------------------------------------------
echo ""
echo "[5.5] Gravity Shift minimal LP 運用（Hub/コーポレート/Footer に展開禁止）"

check_shift_minimal() {
  local file="$1"
  local label="$2"
  # Footer の Gravity Shift（R+A 複合）リンク or Hub/コーポレートの Shift カード言及を検出
  local count
  count=$(grep -cE 'href="https://growthfix\.jp/gravity-shift/"[^>]*>Gravity Shift' "$ROOT/$file" 2>/dev/null)
  count=${count:-0}
  if [ "$count" -gt 0 ]; then
    printf "${YEL}⚠${NC} %s に Gravity Shift リンク／カードが %s 件残存（minimal LP 運用違反）\n" "$label" "$count"
    WARNINGS=$((WARNINGS + 1))
    return 1
  fi
  return 0
}

shift_minimal_clean=1
for entry in "Gravity/_ブランド/LP/index.html|Hub /gravity/" "コーポレート/top_本番/index.html|コーポレート top" "コーポレート/service_本番/index.html|コーポレート service" "Gravity/Code/LP/index.html|GravityCode" "Gravity/Scan/LP/index.html|GravityScan" "Gravity/Coaching/LP/index.html|GravityCoaching" "Gravity/Orbit/LP/index.html|GravityOrbit" "Gravity/Recruit/LP/index.html|GravityRecruit" "Gravity/Cultivate/LP/index.html|GravityCultivate"; do
  IFS='|' read -r f label <<< "$entry"
  check_shift_minimal "$f" "$label" || shift_minimal_clean=0
done
[ "$shift_minimal_clean" -eq 1 ] && echo -e "${GRN}✓${NC} Gravity Shift は全 LP / コーポレートで minimal LP 運用整合"

# ----------------------------------------------------------------------
# 5.6 廃止（260503 夜・Pull 型 minimal → funnel 内側型 minimal に統合）
# Coaching は R/A と同じ funnel 内側型 minimal（記載あり/リンクあり）に統合
# Push 営業防止は LP 内容（Hero + 「商談時にご案内」明記）で担保
# 詳細：判断基準.md § minimal LP 戦略選択原則（260503 夜 アップデート）
# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
# 6. コーポレート（top/service/news）参謀名展開チェック
# ----------------------------------------------------------------------
echo ""
echo "[6] コーポレートページの参謀名展開"
corporate_missing=0
# 「共鳴の参謀」(Orbit) は意図的に除外：継続運用サービスで入口商材ではないため
# 詳細：memory/feedback_corporate_lp_sambou_orbit_excluded.md
for term in "引力の参謀" "心の参謀" "変革の参謀"; do
  count_top=$(grep -c "$term" "$ROOT/top_本番/index.html" 2>/dev/null)
  count_top=${count_top:-0}
  count_svc=$(grep -c "$term" "$ROOT/service_本番/index.html" 2>/dev/null)
  count_svc=${count_svc:-0}
  count_news=$(grep -c "$term" "$ROOT/news_本番/gravity-release/index.html" 2>/dev/null)
  count_news=${count_news:-0}
  if [ "$count_top" -eq 0 ] || [ "$count_svc" -eq 0 ] || [ "$count_news" -eq 0 ]; then
    printf "${YEL}⚠${NC} 「%s」 top=%s svc=%s news=%s\n" "$term" "$count_top" "$count_svc" "$count_news"
    WARNINGS=$((WARNINGS + 1))
    corporate_missing=$((corporate_missing + 1))
  fi
done
[ "$corporate_missing" -eq 0 ] && echo -e "${GRN}✓${NC} 3 参謀名（CODE/Scan の『引力の参謀』・心・変革）が top / service / news に展開済み（Orbit『共鳴の参謀』は継続運用サービスのため意図的に除外）"

# ----------------------------------------------------------------------
# 7. 自己紹介ストーリー SSOT 整合（260506 P2 物語アーク統一）
# ----------------------------------------------------------------------
# SSOT: memory/user_self_intro_attractor_designer_260430.md（260504 進化版）
# - 核心の一行：「30 年以上、組織の引力 ── 人が集まり、活きる力を [追いかけてきた|設計してきた]」
# - 役割肩書き：「引力経営提唱者」「引力の参謀」
echo ""
echo "[7] 自己紹介ストーリー SSOT 整合（260506 P2 物語アーク統一）"

# 7.1 旧自虐軸文体検出（260506 P2 で B 版に統合済・コーポレート Profile セクション）
# 　 警告語リストは forbidden_terms.tsv 外出し（260514 夜 refactor）
scan_forbidden_section "7.1"

# 7.2 自己紹介核心キーワード密度（profile / 6 サービス LP / WP）
check_intro_keywords() {
  local lp_path="$1"
  local lp_name="$2"
  local f="$ROOT/$lp_path"
  if [ ! -f "$f" ]; then
    return
  fi
  local kw_30years
  kw_30years=$(grep -cE "30 ?年以上" "$f" 2>/dev/null)
  local kw_gravity
  kw_gravity=$(grep -c "組織の引力" "$f" 2>/dev/null)
  local kw_lifeforce
  kw_lifeforce=$(grep -c "人が集まり" "$f" 2>/dev/null)
  local kw_role
  kw_role=$(grep -cE "引力経営提唱者|引力の参謀" "$f" 2>/dev/null)
  local total=$((kw_30years + kw_gravity + kw_lifeforce + kw_role))
  if [ "$total" -lt 3 ]; then
    printf "${YEL}⚠ %s 自己紹介核心キーワード不足${NC}（30年以上 %d / 組織の引力 %d / 人が集まり %d / 役割肩書き %d ＝計 %d ／ 推奨: 3+ 件）\n" \
      "$lp_name" "$kw_30years" "$kw_gravity" "$kw_lifeforce" "$kw_role" "$total"
    WARNINGS=$((WARNINGS + 1))
  else
    printf "${GRN}✓${NC} %s 自己紹介 SSOT 整合（30年以上 %d / 組織の引力 %d / 人が集まり %d / 肩書き %d ＝計 %d）\n" \
      "$lp_name" "$kw_30years" "$kw_gravity" "$kw_lifeforce" "$kw_role" "$total"
  fi
}

check_intro_keywords "profile_本番/index.html" "profile（A 版）"
check_intro_keywords "コーポレート/top_本番/index.html" "コーポレート（B 版）"
check_intro_keywords "Gravity/Code/LP/index.html" "CODE（B 版）"
check_intro_keywords "Gravity/Scan/LP/index.html" "Scan（B 版）"
check_intro_keywords "Gravity/Recruit/LP/index.html" "Recruit（B 版）"
check_intro_keywords "Gravity/Cultivate/LP/index.html" "Cultivate（B 版）"
check_intro_keywords "WhitePaper/V9/index.html" "WP V9（A 版）"
# minimal LP（Shift / Coaching / Orbit）は SPEAKER セクション無のため対象外（仕様通り）

echo ""
echo "[8] 正本パターン違反検出（260507 追加・本番事故再発防止）"

# 8.1 Gravity/LP/ 許可ファイル外 HTML 検出
GRAVITY_LP_DIR="$ROOT/Gravity/LP"
if [ -d "$GRAVITY_LP_DIR" ]; then
  for f in "$GRAVITY_LP_DIR"/*.html; do
    [ -f "$f" ] || continue
    basename=$(basename "$f")
    case "$basename" in
      index.html|seminar-acting.html) ;;  # 正本（許可）
      *)
        printf "${YEL}⚠${NC} 正本外 HTML: %s（_archive/ 移動推奨）\n" "$f"
        WARNINGS=$((WARNINGS + 1))
        ;;
    esac
  done
fi

# 8.2 各 Gravity{Service}/ 直下の古い設計メモ MD 検出（YYMMDD_ パターン）
for dir in "$ROOT"/Gravity*/; do
  [ -d "$dir" ] || continue
  for md in "$dir"*.md; do
    [ -f "$md" ] || continue
    basename=$(basename "$md")
    if echo "$basename" | grep -qE "^26[0-9]{4}_"; then
      printf "${YEL}⚠${NC} 古い設計メモ残置: %s（archive 化推奨）\n" "$md"
      WARNINGS=$((WARNINGS + 1))
    fi
  done
done

# 8.3 廃止/ペンディングサービスディレクトリ検出（archive 必須）
SUSPICIOUS_DIRS=("$ROOT/TrueFit" "$ROOT/GravityFit" "$ROOT/GravityBlueprint")
for d in "${SUSPICIOUS_DIRS[@]}"; do
  if [ -d "$d" ]; then
    printf "${RED}❌${NC} 廃止/ペンディングサービス残置: %s（_archive/ 移動必須）\n" "$d"
    ERRORS=$((ERRORS + 1))
  fi
done

if [ "$WARNINGS" -eq 0 ] && [ "$ERRORS" -eq 0 ]; then
  printf "${GRN}✓${NC} 正本パターン違反なし\n"
fi

echo ""
echo "[9] 09_会社OS 膨張抑制ルール B 違反検知（260507 追加・Phase 9 計画化）"

# 思想層 MD（300 行ルール）：Why.md / 引力.md / 会社.md / 参謀.md / 接続装置.md / culture.md
# 機能系 MD（500 行ルール）：商品.md / 営業.md / 採用.md / カスタマー.md / 法務.md / 社長.md /
#   バランスホイール.md / AI.md / 発信.md / harness.md / 判断基準.md / design.md / 翻訳.md / 00_README.md

OS_ROOT="/Users/ishiinobuyuki/Documents/Obsidian Vault/09_会社OS"
SIZE_VIOLATIONS=0

# 9.1 思想層 MD（300 行ルール）
THOUGHT_MDS=(
  "公開/経営思想/Why.md"
  "公開/経営思想/引力.md"
  "公開/経営思想/会社.md"
  "公開/経営思想/参謀.md"
  "公開/経営思想/接続装置.md"
  "公開/文化/culture.md"
)
for md_rel in "${THOUGHT_MDS[@]}"; do
  md="$OS_ROOT/$md_rel"
  [ -f "$md" ] || continue
  lines=$(wc -l < "$md" | tr -d ' ')
  if [ "$lines" -gt 300 ]; then
    over=$((lines - 300))
    printf "${YEL}⚠${NC} 思想層 MD サイズ超過: %s（%d 行・300 行ルール +%d）\n" "$md_rel" "$lines" "$over"
    WARNINGS=$((WARNINGS + 1))
    SIZE_VIOLATIONS=$((SIZE_VIOLATIONS + 1))
  fi
done

# 9.2 機能系 MD（500 行ルール）
FUNC_MDS=(
  "公開/ガイドライン/商品.md"
  "公開/ガイドライン/design.md"
  "公開/ガイドライン/翻訳.md"
  "公開/文化/判断基準.md"
  "公開/発信・AI/AI.md"
  "公開/発信・AI/発信.md"
  "公開/発信・AI/harness.md"
  "非公開/機能/営業.md"
  "非公開/機能/採用.md"
  "非公開/機能/法務.md"
  "非公開/ガイド/カスタマー.md"
  "非公開/経営層/社長.md"
  "非公開/経営層/バランスホイール.md"
  "00_README.md"
)
for md_rel in "${FUNC_MDS[@]}"; do
  md="$OS_ROOT/$md_rel"
  [ -f "$md" ] || continue
  lines=$(wc -l < "$md" | tr -d ' ')
  if [ "$lines" -gt 500 ]; then
    over=$((lines - 500))
    printf "${YEL}⚠${NC} 機能系 MD サイズ超過: %s（%d 行・500 行ルール +%d）\n" "$md_rel" "$lines" "$over"
    WARNINGS=$((WARNINGS + 1))
    SIZE_VIOLATIONS=$((SIZE_VIOLATIONS + 1))
  fi
done

if [ "$SIZE_VIOLATIONS" -eq 0 ]; then
  printf "${GRN}✓${NC} 09_会社OS サイズ違反なし\n"
else
  printf "  → 詳細・分割計画：04_GrowthFix/02_マーケティング/260508_Phase9_09会社OS分割計画.md\n"
fi

# ----------------------------------------------------------------------
# [10] 知識連動 audit（260509 Phase 1・memory + SSOT + 会社OS 参照リンク整合）
# ----------------------------------------------------------------------
echo ""
echo "[10] 知識連動 audit（memory ↔ SSOT ↔ 会社OS）"
VAULT_ROOT="/Users/ishiinobuyuki/Documents/Obsidian Vault"
audit_output=$(python3 "$VAULT_ROOT/06_開発/scripts/audit/audit_knowledge_sync.py" 2>&1)
audit_exit=$?
if echo "$audit_output" | grep -qE "🔴 HIGH"; then
  high_count=$(echo "$audit_output" | grep -oE "HIGH: [0-9]+" | grep -oE "[0-9]+" | head -1)
  printf "${RED}❌${NC} 死リンク %s 件（audit_knowledge_sync.py で詳細確認）\n" "$high_count"
  ERRORS=$((ERRORS + high_count))
elif echo "$audit_output" | grep -qE "🟡 MEDIUM"; then
  med_count=$(echo "$audit_output" | grep -oE "MEDIUM: [0-9]+" | grep -oE "[0-9]+" | head -1)
  printf "${YEL}⚠${NC} 警告 %s 件（孤児 memory / frontmatter 欠損 — audit_knowledge_sync.py で詳細確認）\n" "$med_count"
  WARNINGS=$((WARNINGS + med_count))
else
  printf "${GRN}✓${NC} memory ↔ SSOT ↔ 会社OS 参照リンク整合 OK\n"
fi

# ----------------------------------------------------------------------
# 結果サマリー
# ----------------------------------------------------------------------
echo ""
echo "========================================"
if [ "$ERRORS" -eq 0 ] && [ "$WARNINGS" -eq 0 ]; then
  echo -e "${GRN}✅ 全チェック通過${NC}"
  exit 0
elif [ "$ERRORS" -eq 0 ]; then
  printf "${YEL}⚠ 警告 %s 件（エラーなし）${NC}\n" "$WARNINGS"
  exit 0
else
  printf "${RED}❌ エラー %s 件 / 警告 %s 件${NC}\n" "$ERRORS" "$WARNINGS"
  exit 1
fi
