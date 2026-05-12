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

# 共通: 禁止語チェック関数
# 除外対象：
#   _archive / _archive_obsolete   — 廃止済み記録
#   *template*                       — テンプレート（コメント例OK）
#   growthfix-*-index.html           — 古いバックアップ（_本番/ が現行）
#   レポート/                        — サンプルレポート（歴史的内容OK）
# 第4引数 extra_exclude: 個別ファイルの除外パターン（任意・260430 セミナー LP 例外運用用）
check_forbidden() {
  local term="$1"
  local reason="$2"
  local replace="$3"
  local extra_exclude="$4"
  local found
  if [ -n "$extra_exclude" ]; then
    found=$(grep -rln "$term" "$ROOT" \
      --include="*.html" \
      --exclude-dir="_archive" \
      --exclude-dir="_archive_obsolete" \
      --exclude-dir="レポート" \
      --exclude="*template*" \
      --exclude="*_backup_*" \
      --exclude="growthfix-*-index.html" \
      --exclude="$extra_exclude" \
      2>/dev/null)
  else
    found=$(grep -rln "$term" "$ROOT" \
      --include="*.html" \
      --exclude-dir="_archive" \
      --exclude-dir="_archive_obsolete" \
      --exclude-dir="レポート" \
      --exclude="*template*" \
      --exclude="*_backup_*" \
      --exclude="growthfix-*-index.html" \
      2>/dev/null)
  fi
  if [ -n "$found" ]; then
    printf "${RED}❌ 禁止語「%s」発見${NC}（理由: %s → 代替: %s）\n" "$term" "$reason" "$replace"
    echo "$found" | sed "s|$ROOT/|     |"
    ERRORS=$((ERRORS + 1))
  fi
}

# 警告レベル禁止語チェック（移行期・大量ヒット予想・LP 修正タスク化想定）
check_forbidden_warning() {
  local term="$1"
  local reason="$2"
  local replace="$3"
  local found
  found=$(grep -rln "$term" "$ROOT" \
    --include="*.html" \
    --exclude-dir="_archive" \
    --exclude-dir="_archive_obsolete" \
    --exclude-dir="レポート" \
    --exclude="*template*" \
    --exclude="growthfix-*-index.html" \
    2>/dev/null)
  if [ -n "$found" ]; then
    local count
    count=$(echo "$found" | wc -l | tr -d ' ')
    printf "${YEL}⚠ 移行期警告「%s」（%s ファイル）${NC}（理由: %s → 代替: %s）\n" "$term" "$count" "$reason" "$replace"
    echo "$found" | sed "s|$ROOT/|     |"
    WARNINGS=$((WARNINGS + 1))
  fi
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
# ----------------------------------------------------------------------
echo ""
echo "[1] 廃止用語・禁止語チェック"

check_forbidden "ホームドクター" "旧Orbit positioning" "共鳴の参謀"
check_forbidden "セラピスト" "旧医療メタファー" "心の参謀"
check_forbidden "外科医" "旧医療メタファー" "変革の参謀"
check_forbidden "Gravity Light" "廃止サービス" "（言及不要）"
check_forbidden "Gravity Core" "廃止サービス" "（言及不要）"
# 「Gravity Scan」は 260430 夕にリブート（Pre-Shift 適合診断・組織の引力タイプ診断）。260422 廃止ルールは撤回。
# check_forbidden "Gravity Scan" "260422廃止・Shift統合" "Shift"
check_forbidden "月5-15万" "Coaching旧価格" "38万・6ヶ月"
check_forbidden "月15万・継続対話" "Coaching旧表記" "38万・6ヶ月"
check_forbidden "月15/25万" "Orbit旧表記（スラッシュ）" "月15-25万"
check_forbidden "13 ページ" "WP旧ページ数" "25 ページ"
check_forbidden "13ページ" "WP旧ページ数" "25 ページ"
check_forbidden "12 ページ" "WP旧ページ数" "25 ページ"
check_forbidden "12ページ" "WP旧ページ数" "25 ページ"
check_forbidden "5サービス体系" "260430で6サービス相当（Shift 2パッケージ化）" "6 サービス相当"
check_forbidden "6サービス体系" "260422→260430移行期の旧表記" "6 サービス相当"
# 260430 夕 Blueprint → Scan リブート
check_forbidden "Gravity Blueprint" "260430 夕 Scan リブート" "Gravity Scan"
check_forbidden "設計の参謀" "260430 夕 Blueprint→Scan リブート（Scan は引力の参謀（組織軸））" "引力の参謀（組織軸）"
check_forbidden "採用口説きブループリント" "260430 夕 主成果物移管" "面接ブループリント 5 要素（Shift R Week 1-2 納品物）"
check_forbidden "Shift 60万" "旧Shift価格" "Shift R/C 各 80 万"
# 260430 SSOT: タグライン階層（会社思想 vs プロダクト思想）
check_forbidden "採用に強い会社をつくる" "260430 タグライン進化" "優秀人材が躍動する会社をつくる(会社思想) or 組織に、引力を。(プロダクト思想)" "*seminar-acting*"
check_forbidden "人材磁場 × 躍動設計" "260430 夕 撤回" "(コピーから削除)"
# 260509 価格 SSOT 違反検出（M-9・LP/HTML での誤表記検出）
check_forbidden "Recruit 60万" "Recruit 価格 SSOT 違反（正：80 万）" "Gravity Recruit 80 万・3 ヶ月"
check_forbidden "Cultivate 60万" "Cultivate 価格 SSOT 違反（正：150 万・6 ヶ月）" "Gravity Cultivate 150 万・6 ヶ月"
check_forbidden "Cultivate 80万" "Cultivate 旧価格（260511 拡張・正：150 万・6 ヶ月）" "Gravity Cultivate 150 万・6 ヶ月"
check_forbidden "Cultivate・80 万・3 ヶ月" "Cultivate 旧価格・期間（260511 拡張・正：150 万・6 ヶ月）" "Gravity Cultivate 150 万・6 ヶ月"
check_forbidden "Coaching 月" "Coaching 旧 月額制（正：38 万・6 ヶ月一括）" "Gravity Coaching 38 万・6 ヶ月"
check_forbidden "Orbit 38万" "Orbit 価格混同（正：月 15 万・最低 6 ヶ月）" "Gravity Orbit 月 15 万・最低 6 ヶ月"
check_forbidden "Shift 100万" "旧 Shift 価格（260511 拡張・正：R+C 複合 220 万・9 ヶ月）" "Gravity Shift 220 万・9 ヶ月"
check_forbidden "Shift 150万・6 ヶ月" "Shift 旧価格・期間（260511 R+C 拡張・正：220 万・9 ヶ月）" "Gravity Shift 220 万・9 ヶ月"
check_forbidden "CODE 10万" "CODE 価格 SSOT 違反（正：5 万・60 分）" "Gravity CODE 5 万・60 分"
check_forbidden "Scan 5万" "Scan 価格 SSOT 違反（正：10 万・60 分）" "Gravity Scan 10 万・60 分"
# 260509 v0.4 旧用語検出（C-5 高/中/低 → A/B/C/D 4 象限）
check_forbidden "C-5 中判定" "v0.4 で覚悟確認 4 象限化（B 結論先送り型 / C 単線思考型）" "覚悟確認 B 型 / C 型"
check_forbidden "C-5 高判定" "v0.4 で覚悟確認 4 象限化（A 完全覚悟型）" "覚悟確認 A 型"
check_forbidden "C-5 低判定" "v0.4 で覚悟確認 4 象限化（D 完全 have to 型）" "覚悟確認 D 型"
# 260509 v0.4 引力項目数（7 → 8 に拡張）。260512 LP 5 ファイル 8 項目化完了 → 検出再有効化
check_forbidden "引力 7 項目" "v0.4 で 8 項目化（PO Fit 認識・心理的安全性 4 行動追加）" "引力 8 項目"
check_forbidden "引力7項目" "v0.4 で 8 項目化" "引力 8 項目"

# 260511 朝 SSOT §8 同期追加（廃止用語の機械検出強化）
check_forbidden "Why × 動詞 × 環境" "260430 公開語彙統一で廃止" "Why × 才能 × 偏愛"
check_forbidden "Why×動詞×環境" "260430 公開語彙統一で廃止" "Why × 才能 × 偏愛"
check_forbidden "環境ズレ型" "260430 4 型再設計で廃止" "才能ズレ型 / 偏愛ズレ型"
check_forbidden "動詞ズレ型" "260430 4 型再設計で廃止" "才能ズレ型 / 偏愛ズレ型"
check_forbidden "32 年" "経験年数の創作表記（幼稚園起点計算）禁止" "30 年以上"
check_forbidden "辞退理由の事前ブロック" "260501 改名（症状起点 → 構造起点）" "期待値ギャップの事前握り"
check_forbidden "辞退ブロック" "260501 改名" "期待値ギャップの事前握り"
check_forbidden "磁化する" "260501 一般語化（Shift R 動詞）" "吸い寄せられる"
check_forbidden "躍動する OS を実装する" "260501 OS 過多回避（Shift C 動詞）" "躍動する土壌を実装する"
check_forbidden "躍動するOSを実装する" "260501 OS 過多回避" "躍動する土壌を実装する"
check_forbidden "口説きフレーズ 3 種" "260430 BP 主成果物 5 種化" "口説きフレーズ 5 種"
check_forbidden "ハンバーガー型 1on1" "260509 JAFCO 反映時 業界一般用語化（カンリー固有語）" "謝罪 → 指摘 → 感謝の 1on1 構造"
check_forbidden "リレーションアセット" "260509 JAFCO 反映時 業界一般用語化（VC 用語寄り）" "採用接続資産"
check_forbidden "採用骨格" "260508 夜 業界一般用語化（人体メタファー禁則）" "採用基盤"
check_forbidden "動く採用骨格" "260508 夜 業界一般用語化" "動く採用基盤"
check_forbidden "引力場" "260508 夜 業界一般用語化（経営者認知負荷軽減）" "採用基盤／組織の魅力"
# 260511 朝 LP 修正完了（Recruit/Cultivate FAQ「採用基盤の引力場」→「採用基盤」）→ エラーレベル復活

# 260511 朝 SSOT 違反検出（Why × 才能 × 偏愛 は社長個人の引力源・会社/組織には適用禁止）
check_forbidden "会社の Why × 才能 × 偏愛" "Why × 才能 × 偏愛 は社長個人の引力源 → 会社には適用できない（SSOT §2 違反）" "社長の引力（Why × 才能 × 偏愛）に共鳴する人材 + 会社の Why と整合"
check_forbidden "会社のWhy × 才能 × 偏愛" "SSOT §2 違反（Why × 才能 × 偏愛 は個人軸専用）" "社長の引力（Why × 才能 × 偏愛）"
check_forbidden "組織の Why × 才能 × 偏愛" "SSOT §2 違反（個人軸専用）" "社長の引力（Why × 才能 × 偏愛）"
check_forbidden "組織のWhy × 才能 × 偏愛" "SSOT §2 違反（個人軸専用）" "社長の引力（Why × 才能 × 偏愛）"

[ "$ERRORS" -eq 0 ] && echo -e "${GRN}✓${NC} 禁止語なし"

# ----------------------------------------------------------------------
# 1.5 移行期警告（260430 SSOT 追加・LP 修正タスク待ち）
# ----------------------------------------------------------------------
echo ""
echo "[1.5] 移行期警告（260430 SSOT 追加・LP 修正タスク待ち）"

check_forbidden_warning "Why × 動詞 × 環境" "260430 公開語彙統一で廃止" "Why × 才能 × 偏愛"
check_forbidden_warning "環境ズレ型" "260430 4 型再設計" "才能ズレ型"
check_forbidden_warning "動詞ズレ型" "260430 4 型再設計" "偏愛ズレ型"

# 260503 二層命名運用（B 案）／260505 Activate→Cultivate：対外 HTML（05_プロダクト/ 配下）で内的呼称・旧外的命名が残っていたら警告
# - LP / WP / コーポレートでは外的呼称「Gravity Recruit / Gravity Cultivate / Gravity Shift」が正
# - 「Shift R」「Shift C」「Shift Full」「Gravity Shift R」「Gravity Shift C」は対外文脈で禁則
# - 「Gravity Activate」「Activate」「/gravity-activate/」は 260505 廃止・対外文脈で禁則
# - 09_会社OS / project memory / 仕様書（.md）は内的呼称継続のため対象外（--include="*.html" で限定）
check_forbidden_warning "Gravity Shift R" "260503 二層命名運用（対外）" "Gravity Recruit"
check_forbidden_warning "Gravity Shift C" "260503 二層命名運用（対外）" "Gravity Cultivate"
check_forbidden_warning "Shift R" "260503 二層命名運用（対外・社内呼称）" "Gravity Recruit"
check_forbidden_warning "Shift C" "260503 二層命名運用（対外・社内呼称）" "Gravity Cultivate"
check_forbidden_warning "Shift Full" "260503 二層命名運用（対外・社内呼称）" "Gravity Shift（R+A 複合）"
check_forbidden_warning "/gravity-shift-a/" "260503 β 並列型 URL 構造" "/gravity-cultivate/"
# 260505 Activate→Cultivate 外的命名変更（旧外的呼称・URL の対外残存検出）
check_forbidden_warning "Gravity Activate" "260505 外的命名変更（Activate→Cultivate）" "Gravity Cultivate"
check_forbidden_warning "/gravity-activate/" "260505 外的命名変更（URL 変更・旧 URL は 301 リダイレクト）" "/gravity-cultivate/"
check_forbidden_warning "Activate" "260505 外的命名変更（介入主義 Activate を撤廃・思想整合は Cultivate）" "Cultivate"

# 260506 P0-4 機能配分 v1.0 §6.2 追加：内的呼称 Shift A の対外残存検出（260505 Cultivate 命名変更で内的呼称も Shift C に統一済）
check_forbidden_warning "Shift A" "260505 内的呼称も Shift C に統一済（Cultivate 命名変更時）" "Shift C（社内）or Gravity Cultivate（対外）"
# Scan LP で発見した「Gravity Recruit／A（躍動組織）」型の残存（260506 修正済・再発防止）
check_forbidden "／A（躍動" "260506 Scan LP bug 再発防止（Cultivate 命名統一漏れ検出）" "／Gravity Cultivate（躍動組織）"
check_forbidden "／ A（躍動" "260506 Scan LP bug 再発防止（Cultivate 命名統一漏れ検出）" "／ Gravity Cultivate（躍動組織）"

# 260506 P0-3 ペルソナ v1.0 §「適合外（明示的に避けるペルソナ）」由来：
# 不適合ペルソナ語彙（ジャイアニズム × バキバキ × カリスマ採用型）の対外露出は禁則
check_forbidden_warning "ジャイアニズム" "P0-3 適合外ペルソナ語彙（対外 LP / WP に出すと不適合層を引き寄せる）" "（対外コピーから削除）"
check_forbidden_warning "カリスマ採用" "P0-3 適合外ペルソナ語彙（対外 LP / WP に出すと不適合層を引き寄せる）" "（対外コピーから削除）"

# 260506 P5 声トーンガイド v1.0 §2.2 由来：一人称ルール違反検知
# 「我々」「弊社」型は石井 ≠ GrowthFix の印象を作って権威希薄化
check_forbidden_warning "我々 GrowthFix" "P5 声トーンガイド §2.2 違反（複数形は石井 ≠ GrowthFix の印象を作る・権威希薄化）" "GrowthFix（私）は or GrowthFix の Gravity シリーズは"
check_forbidden_warning "弊社の Gravity" "P5 声トーンガイド §2.2 違反（同上）" "GrowthFix の Gravity"

# 260506 P5 声トーンガイド v1.0 §3 由来：主語チェック違反検知（堀田 #10）
# 経営者は「組織課題」「組織の問題」にお金を出さない。「事業の成長」「採用基盤」「優秀人材獲得」を主語にする
check_forbidden_warning "組織の問題を解決" "P5 声トーンガイド §3 主語チェック違反（堀田 #10・経営者は組織課題に金を出さない）" "事業の成長 / 採用基盤 / 優秀人材獲得"

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
# 2. 各サービスLPに参謀名タグラインがあるか
# ----------------------------------------------------------------------
echo ""
echo "[2] 5サービスLPの参謀名タグライン整合"

check_required "GravityCode/LP/index.html" "引力の参謀"
check_required "GravityScan/LP/index.html" "引力の参謀（組織軸）"
check_required "GravityCoaching/LP/index.html" "心の参謀"
check_required "GravityOrbit/LP/index.html" "共鳴の参謀"
# 260503 β 並列型・新設 LP（Gravity Recruit / Gravity Cultivate・260505 リネーム）
check_required "GravityRecruit/LP/index.html" "変革の参謀"
check_required "GravityCultivate/LP/index.html" "変革の参謀"
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
for lp in GravityCode GravityScan GravityRecruit GravityCultivate; do
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
for entry in "Gravity/LP/index.html|Hub /gravity/" "top_本番/index.html|コーポレート top" "service_本番/index.html|コーポレート service" "GravityCode/LP/index.html|GravityCode" "GravityScan/LP/index.html|GravityScan" "GravityCoaching/LP/index.html|GravityCoaching" "GravityOrbit/LP/index.html|GravityOrbit" "GravityRecruit/LP/index.html|GravityRecruit" "GravityCultivate/LP/index.html|GravityCultivate"; do
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
check_forbidden_warning "他人の組織のことしか考えていない" "P2 旧自己紹介文体（260506 B 版に統合済）" "30 年以上、組織の引力 ── 人が集まり、活きる力を追いかけてきた"
check_forbidden_warning "本音で生きられていない自分に絶望した。<br>その原体験" "P2 旧自己紹介文体（260506 B 版本文と原体験 1 行に統合済）" "B 版 + 原体験 1 行（260506 SSOT 整合形）"

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
check_intro_keywords "top_本番/index.html" "コーポレート（B 版）"
check_intro_keywords "GravityCode/LP/index.html" "CODE（B 版）"
check_intro_keywords "GravityScan/LP/index.html" "Scan（B 版）"
check_intro_keywords "GravityRecruit/LP/index.html" "Recruit（B 版）"
check_intro_keywords "GravityCultivate/LP/index.html" "Cultivate（B 版）"
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
