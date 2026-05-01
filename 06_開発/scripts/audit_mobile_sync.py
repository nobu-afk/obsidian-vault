#!/usr/bin/env python3
"""
audit_mobile_sync.py
19 LP の HTML と mobile.css の同期状態を監査し、AI 自動補完の素材を生成する。

実行:
  python3 06_開発/scripts/audit_mobile_sync.py                    # 人間用レポート
  python3 06_開発/scripts/audit_mobile_sync.py --json              # JSON 出力（Claude 用）
  python3 06_開発/scripts/audit_mobile_sync.py --severity high     # 高優先度のみ
  python3 06_開発/scripts/audit_mobile_sync.py --lp top_本番        # 特定 LP のみ
  python3 06_開発/scripts/audit_mobile_sync.py --apply             # mobile.css に提案を追記

機能:
  1. 各 LP の HTML から class / inline style を抽出
  2. mobile.css の @media (max-width:768px) でカバーされているセレクタと突合
  3. カバーされていない要素を検出（severity 別）
  4. ヒューリスティックに基づくモバイル対応案を自動生成
  5. JSON 出力で Claude が直接読み込んで Edit 提案できる形式

ワークフロー（Claude Code との連携）:
  1. ユーザーが LP の HTML を編集
  2. 本スクリプト実行 → JSON 出力
  3. Claude が JSON を読んで mobile.css への追加ルールを提案
  4. ユーザー承認後 Edit ツールで mobile.css 更新
  5. デプロイ

更新履歴:
  - 2026-04-29: 初版（Level 3 AI 自動補完の検出層）
"""

import re
import sys
import json
import argparse
from pathlib import Path
from collections import defaultdict

# ============================================================
# パス設定
# ============================================================
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
LP_DIR = PROJECT_ROOT / "05_プロダクト"
MOBILE_CSS = LP_DIR / "_共通" / "mobile.css"

# 19 LP（本番デプロイ対象）
TARGETS = [
    "top_本番/index.html",
    "Gravity/LP/index.html",
    "GravityCode/LP/index.html",
    "GravityCode/診断_executive_本番/index.html",
    "GravityBlueprint/LP/index.html",
    "GravityBlueprint/診断_本番/index.html",
    "GravityCoaching/LP/index.html",
    "GravityShift/LP/index.html",
    "GravityOrbit/LP/index.html",
    "service_本番/index.html",
    "profile_本番/index.html",
    "achievement_本番/index.html",
    "contact_本番/index.html",
    "privacy-policy_本番/index.html",
    "news_本番/index.html",
    "news_本番/site-renewal/index.html",
    "news_本番/gravity-release/index.html",
    "knowledge_本番/index.html",
    "whitepaper_optin_本番/index.html",
]

# 既に汎用ルールでカバー済の HTML タグ（mobile.css の汎用ルールが適用される）
GENERICALLY_COVERED_TAGS = {
    'h1', 'h2', 'h3', 'h4', 'p', 'li', 'dd', 'dt', 'td', 'th',
    'small', 'figcaption', 'a', 'button', 'input', 'textarea', 'select',
    'table', 'img', 'video', 'iframe', 'html', 'body',
}

# 汎用クラス（フィルタ対象）
GENERIC_CLASS_PATTERNS = {
    'container', 'inner', 'wrap', 'wrapper', 'main', 'body', 'header', 'footer',
    'section', 'block', 'box', 'item', 'list', 'group', 'row', 'col',
    'flex', 'grid', 'wow', 'fadeIn', 'fadeInUp', 'fadeInLeft', 'fadeInRight',
    # 既に components.css でカバー済
    'gf-hero', 'gf-btn', 'gf-card', 'gf-section', 'gf-grid',
    # トラッキング・A/Bテスト等のメタ属性的クラス
    'screen', 'active',
}

# ============================================================
# パーサ
# ============================================================
def extract_html_elements(html: str):
    """HTML から各タグの class / inline style を抽出"""
    elements = []
    # 簡易パーサ：<tag ... class="..." ... style="..."> を捕捉
    # 順序が逆でも対応
    for m in re.finditer(r'<(\w+)([^>]*)>', html):
        tag = m.group(1).lower()
        attrs = m.group(2)

        # class 属性
        class_match = re.search(r'\bclass="([^"]+)"', attrs)
        classes = class_match.group(1).split() if class_match else []

        # style 属性
        style_match = re.search(r'\bstyle="([^"]+)"', attrs)
        style = style_match.group(1).strip() if style_match else ''

        if classes or style:
            elements.append({
                'tag': tag,
                'classes': classes,
                'style': style,
            })
    return elements


def extract_mobile_covered_selectors(css: str):
    """mobile.css の @media (max-width:NNNpx) ブロックからカバー済セレクタを抽出
    バランス済 brace counter で堅牢に解析"""
    covered_selectors = set()
    covered_classes = set()
    covered_tags = set()

    # コメント除去（行コメント / ブロックコメント）
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.DOTALL)

    # @media ブロックを balance carry で抽出
    media_blocks = []
    i = 0
    while i < len(css):
        # @media の開始位置を探す
        m = re.search(r'@media[^{]*\(\s*max-width:\s*(\d+)\s*px\s*\)', css[i:])
        if not m:
            break
        max_width = int(m.group(1))
        # max-width >= 768px の @media ブロックのみ対象（モバイル想定）
        # （実は max-width:600px や 375px もモバイルに該当・全部含める）
        # → max-width: <=1024 を含めることでタブレットも捕捉
        if max_width > 1024:
            i += m.end()
            continue
        # `{` 位置を見つける
        brace_start = css.find('{', i + m.end())
        if brace_start < 0:
            break
        # balanced brace で終端を見つける
        depth = 1
        j = brace_start + 1
        while j < len(css) and depth > 0:
            if css[j] == '{':
                depth += 1
            elif css[j] == '}':
                depth -= 1
            j += 1
        if depth == 0:
            block_content = css[brace_start + 1:j - 1]
            media_blocks.append(block_content)
            i = j
        else:
            break

    for block in media_blocks:
        # ルール抽出：「selector { ... }」を非貪欲に拾う
        # ただしブロック内のネスト（@supports等）は無視・@-規則だけスキップ
        pos = 0
        while pos < len(block):
            # `{` を見つけてセレクタ部分を切り出す
            brace = block.find('{', pos)
            if brace < 0:
                break
            selector_text = block[pos:brace].strip()
            if selector_text.startswith('@'):
                # @supports 等のネストはスキップ
                # 対応する } まで進める
                d = 1
                k = brace + 1
                while k < len(block) and d > 0:
                    if block[k] == '{':
                        d += 1
                    elif block[k] == '}':
                        d -= 1
                    k += 1
                pos = k
                continue
            # 対応する } を見つける（非ネスト前提・宣言ブロック）
            d = 1
            k = brace + 1
            while k < len(block) and d > 0:
                if block[k] == '{':
                    d += 1
                elif block[k] == '}':
                    d -= 1
                k += 1
            # セレクタ登録
            for sel in selector_text.split(','):
                sel = sel.strip()
                if not sel:
                    continue
                covered_selectors.add(sel)
                for cls_m in re.finditer(r'\.([a-zA-Z_][a-zA-Z0-9_-]*)', sel):
                    covered_classes.add(cls_m.group(1))
                first_token = re.match(r'^(\w+)', sel)
                if first_token:
                    covered_tags.add(first_token.group(1).lower())
            pos = k

    return {
        'selectors': covered_selectors,
        'classes': covered_classes,
        'tags': covered_tags,
    }


# ============================================================
# 懸念事項検出（ヒューリスティック）
# ============================================================
def analyze_inline_style(style: str, tag: str):
    """インラインスタイルからモバイル懸念を検出＋提案を生成"""
    concerns = []

    # 1. 大きい font-size
    fs = re.search(r'font-size:\s*(\d+(?:\.\d+)?)\s*px', style)
    if fs:
        size = float(fs.group(1))
        if size >= 18:
            min_size = max(15, int(size * 0.85))
            vw = round(size * 0.27, 1)
            concerns.append({
                'severity': 'high' if size >= 24 else 'medium',
                'type': 'large_font_size',
                'detected': f'font-size: {fs.group(1)}px',
                'suggestion': f'font-size: clamp({min_size}px, {vw}vw, {fs.group(1)}px) !important;',
                'rationale': f'{fs.group(1)}px は SP で過大。clamp で 320-768px にスケール',
            })

    # 2. display: flex + flex-direction: row（横並び固定）
    if re.search(r'display:\s*flex', style):
        if re.search(r'flex-direction:\s*row', style):
            concerns.append({
                'severity': 'medium',
                'type': 'fixed_flex_row',
                'detected': 'display:flex + flex-direction:row',
                'suggestion': 'flex-direction: column !important;',
                'rationale': 'SP では縦積みが標準（既存 mobile.css の .d-flex.flex-row ルールと整合）',
            })

    # 3. white-space: nowrap
    if re.search(r'white-space:\s*nowrap', style):
        concerns.append({
            'severity': 'low',
            'type': 'nowrap',
            'detected': 'white-space: nowrap',
            'suggestion': 'white-space: normal !important;',
            'rationale': 'SP では折り返し許容（既存 mobile.css でカバー済の可能性大）',
        })

    # 4. 大きい padding
    pad_simple = re.search(r'padding:\s*(\d+)\s*px', style)
    if pad_simple:
        pad = int(pad_simple.group(1))
        if pad >= 40:
            concerns.append({
                'severity': 'medium',
                'type': 'large_padding',
                'detected': f'padding: {pad}px',
                'suggestion': f'padding: {int(pad * 0.6)}px !important;',
                'rationale': f'{pad}px は SP で過大。約 60% に圧縮推奨',
            })

    # 5. width 固定値（min-width も含む）
    width_fixed = re.search(r'(?<!max-)(?<!min-)width:\s*(\d+)\s*px', style)
    if width_fixed:
        w = int(width_fixed.group(1))
        if w > 320:
            concerns.append({
                'severity': 'high',
                'type': 'fixed_width',
                'detected': f'width: {w}px',
                'suggestion': f'max-width: 100% !important; width: auto !important;',
                'rationale': f'{w}px の固定幅は 320px 端末で破綻',
            })

    # 6. 大きい margin
    mar = re.search(r'margin:\s*(\d+)\s*px', style)
    if mar:
        m = int(mar.group(1))
        if m >= 50:
            concerns.append({
                'severity': 'low',
                'type': 'large_margin',
                'detected': f'margin: {m}px',
                'suggestion': f'margin: {int(m * 0.6)}px !important;',
                'rationale': '余白圧縮で情報密度向上',
            })

    return concerns


# ============================================================
# 監査本体
# ============================================================
def audit(severity_filter=None, lp_filter=None):
    if not MOBILE_CSS.exists():
        return {'error': f'mobile.css not found: {MOBILE_CSS}'}

    css = MOBILE_CSS.read_text(encoding='utf-8')
    covered = extract_mobile_covered_selectors(css)

    targets = TARGETS
    if lp_filter:
        targets = [t for t in TARGETS if lp_filter in t]
        if not targets:
            return {'error': f'No LP matches filter: {lp_filter}'}

    results = {
        'mobile_css_summary': {
            'total_selectors': len(covered['selectors']),
            'covered_classes': len(covered['classes']),
            'covered_tags': len(covered['tags']),
        },
        'lp_count': len(targets),
        'uncovered_classes': defaultdict(lambda: {'count': 0, 'lps': [], 'tags': set()}),
        'inline_concerns': [],
    }

    for rel_path in targets:
        lp_path = LP_DIR / rel_path
        if not lp_path.exists():
            continue

        html = lp_path.read_text(encoding='utf-8')
        elements = extract_html_elements(html)

        for el in elements:
            # クラス分析
            for cls in el['classes']:
                # 汎用クラス＋既に components.css 等でカバー済はスキップ
                if cls in GENERIC_CLASS_PATTERNS:
                    continue
                if cls.startswith('gf-'):
                    continue
                # 一文字クラス・wow 等のアニメ用クラスもスキップ
                if len(cls) <= 2 or cls.startswith('wow'):
                    continue
                # mobile.css でカバー済か？
                if cls not in covered['classes']:
                    info = results['uncovered_classes'][cls]
                    info['count'] += 1
                    if rel_path not in info['lps']:
                        info['lps'].append(rel_path)
                    info['tags'].add(el['tag'])

            # インラインスタイル分析
            if el['style']:
                concerns = analyze_inline_style(el['style'], el['tag'])
                for concern in concerns:
                    if severity_filter and concern['severity'] != severity_filter:
                        continue
                    results['inline_concerns'].append({
                        'lp': rel_path,
                        'tag': el['tag'],
                        'classes': el['classes'][:3],  # 上位 3 つ
                        'style_excerpt': el['style'][:120],
                        **concern,
                    })

    # set を list 化（JSON シリアライズ用）
    serialized_uncovered = []
    for cls, info in results['uncovered_classes'].items():
        if severity_filter and severity_filter != 'all':
            # severity_filter が 'low' なら未カバークラスは表示
            if severity_filter not in ('low', 'medium'):
                continue
        serialized_uncovered.append({
            'class': cls,
            'count': info['count'],
            'lps': info['lps'],
            'tags': sorted(list(info['tags'])),
            'severity': 'medium' if info['count'] >= 5 else 'low',
        })
    serialized_uncovered.sort(key=lambda x: -x['count'])
    results['uncovered_classes'] = serialized_uncovered

    return results


# ============================================================
# レポート出力
# ============================================================
def print_human_report(results):
    if 'error' in results:
        print(f"❌ {results['error']}")
        return

    print("=" * 60)
    print("📱 LP ↔ mobile.css 同期監査レポート")
    print("=" * 60)
    print()
    print(f"対象 LP: {results['lp_count']} ファイル")
    print(f"mobile.css カバー済セレクタ: {results['mobile_css_summary']['total_selectors']}")
    print(f"mobile.css カバー済クラス: {results['mobile_css_summary']['covered_classes']}")
    print()

    # 未カバークラス
    uncovered = results['uncovered_classes']
    print(f"⚠️  mobile.css 未カバーのクラス: {len(uncovered)} 件")
    print()
    if uncovered:
        print(f"{'Class':<35} {'出現':<8} {'タグ':<12} {'重要度':<8} {'LP数'}")
        print("-" * 75)
        for item in uncovered[:25]:
            tags_str = ','.join(item['tags'][:2])
            print(f".{item['class']:<34} {item['count']:<8} {tags_str:<12} {item['severity']:<8} {len(item['lps'])}")
        if len(uncovered) > 25:
            print(f"... +{len(uncovered) - 25} 件")
    print()

    # インラインスタイル懸念
    concerns = results['inline_concerns']
    print(f"⚠️  インラインスタイルのモバイル懸念: {len(concerns)} 件")
    print()

    by_severity = defaultdict(list)
    for c in concerns:
        by_severity[c['severity']].append(c)

    for sev in ('high', 'medium', 'low'):
        items = by_severity.get(sev, [])
        if not items:
            continue
        emoji = {'high': '🔴', 'medium': '🟡', 'low': '🔵'}[sev]
        print(f"{emoji} {sev.upper()}: {len(items)} 件")
        # type 別集計
        by_type = defaultdict(list)
        for it in items:
            by_type[it['type']].append(it)
        for t, ts in by_type.items():
            print(f"  [{t}] {len(ts)} 件 ── {ts[0]['rationale']}")
            print(f"     例: {ts[0]['lp']} ({ts[0]['tag']})")
            print(f"     検出: {ts[0]['detected']}")
            print(f"     提案: {ts[0]['suggestion']}")
        print()

    print("=" * 60)
    print("📋 推奨アクション")
    print("=" * 60)
    print("1. 高優先度（red）の懸念を mobile.css に追加")
    print("2. 出現件数が多い未カバークラスから対応")
    print("3. JSON 出力（--json）を Claude に渡して mobile.css 更新案を生成依頼")
    print("4. Claude 側で Edit ツールで mobile.css 更新→ デプロイ")
    print()


def main():
    parser = argparse.ArgumentParser(description='LP ↔ mobile.css 同期監査')
    parser.add_argument('--json', action='store_true', help='JSON 出力（Claude 用）')
    parser.add_argument('--severity', choices=['high', 'medium', 'low', 'all'], default='all')
    parser.add_argument('--lp', help='特定 LP のみ監査（部分一致）')
    parser.add_argument('--apply', action='store_true', help='提案を mobile.css にコメントで追記')

    args = parser.parse_args()

    severity = args.severity if args.severity != 'all' else None
    results = audit(severity_filter=severity, lp_filter=args.lp)

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2, default=str))
    else:
        print_human_report(results)

    if args.apply:
        apply_suggestions(results)


def apply_suggestions(results):
    """高優先度の懸念のみ mobile.css の末尾にコメントブロックで追記"""
    high_concerns = [c for c in results.get('inline_concerns', []) if c.get('severity') == 'high']
    if not high_concerns:
        print("\n✅ 高優先度の懸念なし。--apply スキップ")
        return

    block = ['', '/* ============================================================',
            f'   AUTO-SUGGESTED RULES（audit_mobile_sync.py が自動生成）',
            f'   検出: 高優先度 {len(high_concerns)} 件',
            f'   ※ 適用前に必ずレビュー！',
            '   ============================================================ */',
            '@media (max-width: 768px) {']
    seen = set()
    for c in high_concerns:
        key = (c.get('type'), c.get('detected'))
        if key in seen:
            continue
        seen.add(key)
        block.append(f'  /* {c["lp"]} ({c["tag"]}): {c.get("rationale","")} */')
        block.append(f'  /* TODO: 適切なセレクタを追加 */')
        block.append(f'  /* {c["suggestion"]} */')
        block.append('')
    block.append('}')

    appendage = '\n'.join(block) + '\n'
    with open(MOBILE_CSS, 'a', encoding='utf-8') as f:
        f.write(appendage)
    print(f"\n✅ mobile.css に {len(seen)} 件の提案ブロックを追記しました")
    print("   → エディタで開いて、適切なセレクタを埋めてからデプロイ")


if __name__ == '__main__':
    main()
