#!/usr/bin/env python3
"""
add_service_schema.py
5 サービス LP に Schema.org Service の JSON-LD を </head> 直前に追加する。

実行:
  python3 06_開発/scripts/add_service_schema.py [--dry-run]

対象:
  - Gravity CODE LP（5 万円）
  - Gravity Blueprint LP（10 万円）
  - Gravity Coaching LP（38 万円・6 ヶ月）
  - Gravity Shift LP（80 万円・3 ヶ月）
  - Gravity Orbit LP（月 15 万〜25 万円・サブスク）

特徴:
  - 既に "schema.org" を含む LP はスキップ（重複防止）
  - JSON-LD は SSOT に基づく価格・期間
  - <script type="application/ld+json"> として 1 ブロックで挿入
"""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
LP_DIR = PROJECT_ROOT / "05_プロダクト"

DRY_RUN = "--dry-run" in sys.argv

# 共通の provider オブジェクト
PROVIDER = {
    "@type": "Organization",
    "name": "GrowthFix",
    "url": "https://growthfix.jp/",
    "sameAs": [
        "https://www.facebook.com/profile.php?id=61573530374008",
        "https://x.com/growthfix87",
    ],
}

AREA = {"@type": "Country", "name": "Japan"}

# 5 サービスの設定
SERVICES = [
    {
        "file": "GravityCode/LP/index.html",
        "schema": {
            "@context": "https://schema.org",
            "@type": "Service",
            "name": "Gravity CODE",
            "alternateName": "引力の参謀",
            "description": "60 分の対話から経営者の引力タイプ・源泉・死角を解読し「YOUR GRAVITY CODE」を生成する診断サービス。",
            "url": "https://growthfix.jp/gravity-code/",
            "provider": PROVIDER,
            "areaServed": AREA,
            "serviceType": "経営者向け引力診断",
            "offers": {
                "@type": "Offer",
                "price": "50000",
                "priceCurrency": "JPY",
                "description": "60 分・税抜き 5 万円",
                "availability": "https://schema.org/InStock",
            },
        },
    },
    {
        "file": "GravityBlueprint/LP/index.html",
        "schema": {
            "@context": "https://schema.org",
            "@type": "Service",
            "name": "Gravity Blueprint",
            "alternateName": "設計の参謀",
            "description": "60 分の対話で個人引力を組織の 4 軸（制度・会議・評価軸・役割分担）への翻訳設計図に落とし込む。Shift／Orbit の必須入口。",
            "url": "https://growthfix.jp/gravity-blueprint/",
            "provider": PROVIDER,
            "areaServed": AREA,
            "serviceType": "経営者向け組織設計図セッション",
            "offers": {
                "@type": "Offer",
                "price": "100000",
                "priceCurrency": "JPY",
                "description": "60 分・税抜き 10 万円",
                "availability": "https://schema.org/InStock",
            },
        },
    },
    {
        "file": "GravityCoaching/LP/index.html",
        "schema": {
            "@context": "https://schema.org",
            "@type": "Service",
            "name": "Gravity Coaching",
            "alternateName": "心の参謀",
            "description": "経営者が本来の自分を取り戻す 6 ヶ月の継続対話。社会から埋め込まれたものを抜き、本来の判断軸を取り戻す。",
            "url": "https://growthfix.jp/gravity-coaching/",
            "provider": PROVIDER,
            "areaServed": AREA,
            "serviceType": "エグゼクティブコーチング",
            "offers": {
                "@type": "Offer",
                "price": "380000",
                "priceCurrency": "JPY",
                "description": "6 ヶ月一括・税抜き 38 万円（CODE 付属）。7 ヶ月目以降 月 5 万円で継続伴走可能。",
                "availability": "https://schema.org/InStock",
            },
        },
    },
    {
        "file": "GravityShift/LP/index.html",
        "schema": {
            "@context": "https://schema.org",
            "@type": "Service",
            "name": "Gravity Shift",
            "alternateName": "変革の参謀",
            "description": "Week 1-2 で組織実装整合診断、Week 3-12 で実装伴走を行う 3 ヶ月の組織実装プログラム。経営者と幹部の繋がり方を変える。Blueprint 受講必須。",
            "url": "https://growthfix.jp/gravity-shift/",
            "provider": PROVIDER,
            "areaServed": AREA,
            "serviceType": "組織実装伴走プログラム",
            "offers": {
                "@type": "Offer",
                "price": "800000",
                "priceCurrency": "JPY",
                "description": "3 ヶ月・税抜き 80 万円（幹部 2 名標準）。3 名 90 万／4 名以上 100 万〜。",
                "availability": "https://schema.org/InStock",
            },
        },
    },
    {
        "file": "GravityOrbit/LP/index.html",
        "schema": {
            "@context": "https://schema.org",
            "@type": "Service",
            "name": "Gravity Orbit",
            "alternateName": "共鳴の参謀",
            "description": "経営者の引力を幹部複数人の引力に複製する月次伴走。Shift の次の幹部育成フェーズ。",
            "url": "https://growthfix.jp/gravity-orbit/",
            "provider": PROVIDER,
            "areaServed": AREA,
            "serviceType": "幹部育成月次伴走",
            "offers": [
                {
                    "@type": "Offer",
                    "name": "Standard",
                    "price": "150000",
                    "priceCurrency": "JPY",
                    "description": "Standard 月 15 万円（幹部 1 名）",
                    "availability": "https://schema.org/InStock",
                },
                {
                    "@type": "Offer",
                    "name": "Pro",
                    "price": "250000",
                    "priceCurrency": "JPY",
                    "description": "Pro 月 25 万円（幹部 3 名＋戦略納品）",
                    "availability": "https://schema.org/InStock",
                },
            ],
        },
    },
]

added = 0
skipped = 0
errors = 0

print(f"📋 Service スキーマ追加（{'DRY-RUN' if DRY_RUN else '本番実行'}）")
print(f"   対象: {len(SERVICES)} サービス LP")
print()

for svc in SERVICES:
    file_path = LP_DIR / svc["file"]
    name = svc["schema"]["name"]

    if not file_path.exists():
        print(f"  ❌ NOT FOUND: {svc['file']}")
        errors += 1
        continue

    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"  ❌ READ FAIL ({svc['file']}): {e}")
        errors += 1
        continue

    # 既に schema.org JSON-LD があればスキップ
    if 'application/ld+json' in content and 'schema.org' in content:
        print(f"  ⏭  SKIP（既存 JSON-LD あり）: {name}")
        skipped += 1
        continue

    # JSON-LD ブロックを生成
    json_str = json.dumps(svc["schema"], ensure_ascii=False, indent=2)
    block = (
        '\n  <!-- Service Schema (Schema.org) -->\n'
        '  <script type="application/ld+json">\n'
        f'{json_str}\n'
        '  </script>\n'
    )

    # </head> 直前に挿入
    if '</head>' not in content:
        print(f"  ❌ </head> not found: {svc['file']}")
        errors += 1
        continue

    new_content = content.replace('</head>', f'{block}</head>', 1)

    if DRY_RUN:
        print(f"  📋 [dry] {name} ({svc['file']}) ── 追加するブロックサイズ: {len(block)} bytes")
    else:
        try:
            file_path.write_text(new_content, encoding="utf-8")
            print(f"  ✅ {name}: 追加完了")
            added += 1
        except Exception as e:
            print(f"  ❌ WRITE FAIL ({svc['file']}): {e}")
            errors += 1

print()
print("📊 集計")
print(f"  追加: {added}")
print(f"  スキップ: {skipped}")
print(f"  エラー: {errors}")
