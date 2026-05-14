#!/usr/bin/env python3
"""Phase 4 統合 JSON DB v2.0 生成スクリプト（ミナジン + 人事の大学 拡張版）

v1.0 (DMM + MOON-X + プレイド) を継承し、companies.ミナジン と companies.人事の大学 を追加。
横断パターンに「SMB 適用 / 中小コンサル方法論軸」3-5 件を追加。
"""
from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime

import sys
sys.path.insert(0, str(Path(__file__).parent))
from build_json_db import (
    load_structure,
    normalize_for_match,
    subfolder_of,
    PHASE_12_MAP,
    PHASE_3_FILE_TO_MD,
    collect_dmm,
    collect_moonx,
    collect_plaid,
    build_cross_insights as build_cross_insights_v1,
)

CACHE = Path("/Users/ishiinobuyuki/Documents/Obsidian Vault/06_開発/scripts/dropbox/_structure_cache")
OUT = Path("/Users/ishiinobuyuki/Documents/Obsidian Vault/04_GrowthFix/01_サービス設計/_DMM資産_AI武装連携/260514_Dropbox網羅DB_v2.0_ミナジン拡張.json")


# Phase 4 個別分析 MD マッピング（ファイル毎・複数ファイル束ねは同一 MD で重複参照）
PHASE_4_FILE_TO_MD = {
    # 007 道具箱 - 商品開発系（軽量分割版）
    "/02_MINAGINE/01_人事制度検討資料/007_オーダーコンサル/3_道具箱（参考資料）/02_商品開発系/scouty_スタートアップ組織開発勉強会.pdf": "260514_ミナジン_007道具箱_scouty_1ファイル_分析_v0.1.md",
    "/02_MINAGINE/01_人事制度検討資料/007_オーダーコンサル/3_道具箱（参考資料）/02_商品開発系/採用系資料/【送付用】白潟総研_採用で組織を伸ばす３５の採用のしかけ.pdf": "260514_ミナジン_007道具箱_白潟採用35_強み発見_2ファイル_分析_v0.1.md",
    "/02_MINAGINE/01_人事制度検討資料/007_オーダーコンサル/3_道具箱（参考資料）/02_商品開発系/自分の強みの見つけ方.pptx": "260514_ミナジン_007道具箱_白潟採用35_強み発見_2ファイル_分析_v0.1.md",
    # 007 道具箱 - HiManager + 職務評価系
    "/02_MINAGINE/01_人事制度検討資料/007_オーダーコンサル/3_道具箱（参考資料）/07_ハイマネージャー/ピアリー営業検討/提案書_ピアリー/(仮)HiManager提案書.pptx": "260514_ミナジン_007道具箱_HiManager_職務評価_2ファイル_分析_v0.1.md",
    "/02_MINAGINE/01_人事制度検討資料/007_オーダーコンサル/3_道具箱（参考資料）/パート社員職務評価（ツール）/職務評価.pdf": "260514_ミナジン_007道具箱_HiManager_職務評価_2ファイル_分析_v0.1.md",
    # 007 制度事例 + 他社人事制度
    "/02_MINAGINE/01_人事制度検討資料/007_オーダーコンサル/3_道具箱（参考資料）/08_平川資料/他社人事制度/光通信/光通信 コンシューマー事業部 2013年人事制度.pdf": "260514_ミナジン_007制度事例_他社人事制度_3ファイル_分析_v0.1.md",
    "/02_MINAGINE/01_人事制度検討資料/007_オーダーコンサル/1_制度事例/02_評価制度素材（みらいの人事他）/07人事制度（あしたのチーム）/あしたのチーム/あしたのチーム様資料.pdf": "260514_ミナジン_007制度事例_他社人事制度_3ファイル_分析_v0.1.md",
    "/02_MINAGINE/01_人事制度検討資料/007_オーダーコンサル/1_制度事例/02_評価制度素材（みらいの人事他）/職業能力評価基準検索データ.xlsx": "260514_ミナジン_007制度事例_他社人事制度_3ファイル_分析_v0.1.md",
    # 007 制度事例 - 評価者教育
    "/02_MINAGINE/01_人事制度検討資料/007_オーダーコンサル/1_制度事例/02_評価制度素材（みらいの人事他）/みらいの人事/170604セミナー資料/0604菅野パート完成テキスト/Ⅱ人事評価者のトレーニング.pdf": "260514_ミナジン_007制度事例_評価者教育_1ファイル_分析_v0.1.md",
    # 008 セールス用 セミナー（軽量分割版）
    "/02_MINAGINE/01_人事制度検討資料/008_みんなの人事評価（共有フォルダ）/01_セールス用ファイル/002_セミナー用資料/20200305@Web（令和人事&運用）/Webセミナースライド用_令和構築&運用セミナー（投影用）.pptx": "260514_ミナジン_008セミナーWeb版_1ファイル_分析_v0.1.md",
    "/02_MINAGINE/01_人事制度検討資料/008_みんなの人事評価（共有フォルダ）/01_セールス用ファイル/002_セミナー用資料/20200227@東京（令和人事&運用）/セミナースライド用_令和構築&運用セミナー（投影用）.pptx": "260514_ミナジン_008セミナー東京版_1ファイル_分析_v0.1.md",
    # 008 コンサル - 平川メソッド
    "/02_MINAGINE/01_人事制度検討資料/008_みんなの人事評価（共有フォルダ）/03_コンサル用ファイル/0_道具箱（コンサル）/平川コンサルメソッド/第1回/【Sc】1_理念ビジョン戦略の調和_20140130.pptx": "260514_ミナジン_008コンサル_平川メソッド_3ファイル_分析_v0.1.md",
    "/02_MINAGINE/01_人事制度検討資料/008_みんなの人事評価（共有フォルダ）/03_コンサル用ファイル/0_道具箱（コンサル）/平川コンサルメソッド/第6回/【Sc】6_報酬設計_20140418 (1).pptx": "260514_ミナジン_008コンサル_平川メソッド_3ファイル_分析_v0.1.md",
    "/02_MINAGINE/01_人事制度検討資料/008_みんなの人事評価（共有フォルダ）/03_コンサル用ファイル/0_道具箱（コンサル）/平川コンサルメソッド/第7回/【Sc】7_評価設計_20140430.pptx": "260514_ミナジン_008コンサル_平川メソッド_3ファイル_分析_v0.1.md",
    # 008 コンサル - クライアント別事例
    "/02_MINAGINE/01_人事制度検討資料/008_みんなの人事評価（共有フォルダ）/03_コンサル用ファイル/001_OZソフト/運用サポート/2020年4月/人事制度（等級・報酬・評価）説明資料20204改定_OZsoft御中.pdf": "260514_ミナジン_008コンサル_クライアント別事例_4ファイル_分析_v0.1.md",
    "/02_MINAGINE/01_人事制度検討資料/008_みんなの人事評価（共有フォルダ）/03_コンサル用ファイル/002_ジャパンアーツ/議事録/人事制度構築MTG①議事録　ジャパン・アーツ御中.pdf": "260514_ミナジン_008コンサル_クライアント別事例_4ファイル_分析_v0.1.md",
    "/02_MINAGINE/01_人事制度検討資料/008_みんなの人事評価（共有フォルダ）/03_コンサル用ファイル/フロント商材開発用/エムシードゥコー/【MC様】現行分析・確認事項_1907.pptx": "260514_ミナジン_008コンサル_クライアント別事例_4ファイル_分析_v0.1.md",
    "/02_MINAGINE/01_人事制度検討資料/008_みんなの人事評価（共有フォルダ）/03_コンサル用ファイル/005_フュディアルクリエーション/【株式会社フュディアルクリエーション御中】操作説明資料Ver1.pptx": "260514_ミナジン_008コンサル_クライアント別事例_4ファイル_分析_v0.1.md",
    # 人事の大学 - 講演セミナー 2006-2010
    "/人事の大学_人事コンサルタント養成講座/講演・セミナー資料/20061201_eラーニングカンファレンスWinter/061201_eラーニングカンファレンスWinter_draft_061130_15.ppt": "260514_人事の大学_2006_2010セミナー_4ファイル_分析_v0.1.md",
    "/人事の大学_人事コンサルタント養成講座/講演・セミナー資料/20091129_ケース面接セミナー&プレゼンテーションセミナー/ESP_学生向けプレゼン講座_091205.pptx": "260514_人事の大学_2006_2010セミナー_4ファイル_分析_v0.1.md",
    "/人事の大学_人事コンサルタント養成講座/講演・セミナー資料/20100803_グローバルタレントマネジメントセミナー/ESP_グローバルタレントマネジメントセミナー投影版_100802.pptx": "260514_人事の大学_2006_2010セミナー_4ファイル_分析_v0.1.md",
    "/人事の大学_人事コンサルタント養成講座/講演・セミナー資料/201010～_人事コンサルタント養成講座/ESP_人事コンサルタント養成講座スライド_101028.pptx": "260514_人事の大学_2006_2010セミナー_4ファイル_分析_v0.1.md",
    # 人事の大学 - 講演セミナー 2014-2015
    "/人事の大学_人事コンサルタント養成講座/講演・セミナー資料/20140605_HRSumit_JSHRM（HRサミット）/JSHRM_Presentation_140605.pdf": "260514_人事の大学_2014成熟期セミナー_PM研修_4ファイル_分析_v0.1.md",
    "/人事の大学_人事コンサルタント養成講座/講演・セミナー資料/20141023_WinnningWomen/JIN-G_Seminar_141023.pptx": "260514_人事の大学_2014成熟期セミナー_PM研修_4ファイル_分析_v0.1.md",
    "/人事の大学_人事コンサルタント養成講座/講演・セミナー資料/20080717_プロフェッショナルセミナー/プロフェッショナルを惹きつけ魅了するタレントマネジメント.ppt": "260514_人事の大学_2014成熟期セミナー_PM研修_4ファイル_分析_v0.1.md",
    "/人事の大学_人事コンサルタント養成講座/研修テキスト/スキル系/プロジェクトマネジメント.pdf": "260514_人事の大学_2014成熟期セミナー_PM研修_4ファイル_分析_v0.1.md",
    # 人事の大学 - コンサル事例
    "/人事の大学_人事コンサルタント養成講座/コンサルティング事例/人事制度の提案資料/人事考課制度ご提案書.pdf": "260514_人事の大学_コンサル事例_4ファイル_分析_v0.1.md",
    "/人事の大学_人事コンサルタント養成講座/コンサルティング事例/評価者研修の資料/JIN-G_ManagementTraining_140902.pptx": "260514_人事の大学_コンサル事例_4ファイル_分析_v0.1.md",
    "/人事の大学_人事コンサルタント養成講座/コンサルティング事例/ダイバーシティ/TI_20150831.pptx": "260514_人事の大学_コンサル事例_4ファイル_分析_v0.1.md",
    "/人事の大学_人事コンサルタント養成講座/コンサルティング事例/海外研修の事前研修/MC_KUFS_PreTraining_140903.pptx": "260514_人事の大学_コンサル事例_4ファイル_分析_v0.1.md",
    # 003 運用支援パック
    "/02_MINAGINE/01_人事制度検討資料/003_運用支援パック/運用サポート/運用サポート概要_20180124.pdf": "260514_ミナジン_003運用支援パック_5ファイル_分析_v0.1.md",
    "/02_MINAGINE/01_人事制度検討資料/003_運用支援パック/運用サポート/運用フォロー提案/【標準提案書】運用フォローサービス.pdf": "260514_ミナジン_003運用支援パック_5ファイル_分析_v0.1.md",
    "/02_MINAGINE/01_人事制度検討資料/003_運用支援パック/賞与パック/①【賞与】評価会議運営ガイド.xlsx": "260514_ミナジン_003運用支援パック_5ファイル_分析_v0.1.md",
    "/02_MINAGINE/01_人事制度検討資料/003_運用支援パック/賞与パック/②【賞与】評定決定・賞与額計算シート（点数固定版）.xlsx": "260514_ミナジン_003運用支援パック_5ファイル_分析_v0.1.md",
    "/02_MINAGINE/01_人事制度検討資料/003_運用支援パック/運用サポート/運用フォロー提案/【標準提案書】運用フォローサービス.pptx": "260514_ミナジン_003運用支援パック_5ファイル_分析_v0.1.md",
}


def lookup_analysis_v2(path: str) -> dict | None:
    """v1.0 + Phase 4 マッピングを横断検索"""
    # v1.0
    if path in PHASE_12_MAP:
        return {"phase": PHASE_12_MAP[path]["phase"], "analysis_md": PHASE_12_MAP[path]["analysis_md"]}
    if path in PHASE_3_FILE_TO_MD:
        return {"phase": "Phase 3", "analysis_md": PHASE_3_FILE_TO_MD[path]}
    # Phase 4
    if path in PHASE_4_FILE_TO_MD:
        return {"phase": "Phase 4", "analysis_md": PHASE_4_FILE_TO_MD[path]}
    # Normalized comparison
    np = normalize_for_match(path)
    for k, v in PHASE_12_MAP.items():
        if normalize_for_match(k) == np:
            return {"phase": v["phase"], "analysis_md": v["analysis_md"]}
    for k, v in PHASE_3_FILE_TO_MD.items():
        if normalize_for_match(k) == np:
            return {"phase": "Phase 3", "analysis_md": v}
    for k, v in PHASE_4_FILE_TO_MD.items():
        if normalize_for_match(k) == np:
            return {"phase": "Phase 4", "analysis_md": v}
    return None


def collect_minagine() -> dict:
    """ミナジン 02_MINAGINE 配下を収集（複数 JSON マージ）"""
    all_entries: list[dict] = []
    seen = set()
    for fn in [
        "minagine_007_order.json",
        "minagine_008_hyouka.json",
        "minagine_007_道具箱.json",
        "minagine_008_コンサル用.json",
        "minagine_003_運用.json",
        "minagine_009_運用.json",
        "minagine_001_営業.json",
    ]:
        for e in load_structure(fn):
            p = e.get("path", "")
            if p in seen:
                continue
            seen.add(p)
            all_entries.append(e)
    root = "/02_MINAGINE/01_人事制度検討資料"
    subfolders: dict[str, dict] = {}
    for e in all_entries:
        if e.get("type") != "file":
            continue
        sub = subfolder_of(e["path"], root, depth=1)
        if sub not in subfolders:
            subfolders[sub] = {"files": []}
        rec = {
            "name": e["name"],
            "path": e["path"],
            "size_kb": e.get("size_kb", 0),
            "extension": e.get("extension", ""),
        }
        ana = lookup_analysis_v2(e["path"])
        if ana:
            rec["phase_analyzed"] = ana["phase"]
            rec["analysis_md"] = ana["analysis_md"]
        else:
            rec["phase_analyzed"] = "未分析"
            rec["analysis_md"] = None
        subfolders[sub]["files"].append(rec)
    return subfolders


def collect_jinji_univ() -> dict:
    """人事の大学 全件収集"""
    all_entries: list[dict] = []
    seen = set()
    for fn in ["jinji_univ_full.json", "jinji_univ_consulting.json"]:
        for e in load_structure(fn):
            p = e.get("path", "")
            if p in seen:
                continue
            seen.add(p)
            all_entries.append(e)
    root = "/人事の大学_人事コンサルタント養成講座"
    subfolders: dict[str, dict] = {}
    for e in all_entries:
        if e.get("type") != "file":
            continue
        sub = subfolder_of(e["path"], root, depth=1)
        if sub not in subfolders:
            subfolders[sub] = {"files": []}
        rec = {
            "name": e["name"],
            "path": e["path"],
            "size_kb": e.get("size_kb", 0),
            "extension": e.get("extension", ""),
        }
        ana = lookup_analysis_v2(e["path"])
        if ana:
            rec["phase_analyzed"] = ana["phase"]
            rec["analysis_md"] = ana["analysis_md"]
        else:
            rec["phase_analyzed"] = "未分析"
            rec["analysis_md"] = None
        subfolders[sub]["files"].append(rec)
    return subfolders


def build_cross_insights_v2() -> list[dict]:
    """v1.0 既存 + Phase 4 ミナジン由来の新規 SMB 適用 / 中小コンサル方法論軸を追加"""
    base = build_cross_insights_v1()
    phase4_additions = [
        {
            "theme": "SMB 中小コンサル方法論（外部から中小企業を変える）= 7 ステップ × 道具箱型方法論",
            "companies": ["ミナジン"],
            "common_patterns": [
                "理念ビジョン戦略の調和 → 職務役割 → 機能役割 → 仕事ステップ → キャリアビジョン → 報酬設計 → 評価設計の 7 段順序",
                "ベテランコンサル A（社内ロール）が体系化した道具箱型メソッドで属人化を解体",
                "クライアント企業に「自社で完結できる」状態を残す",
            ],
            "divergence": [
                "DMM/プレイドは大手伴走（深さ重視）",
                "ミナジンは中小コンサル外部支援（再現性重視・横展開可能なメソッド）",
            ],
            "ai_agent_target": "smb-consult-methodology / 7step-walkthrough-engine",
        },
        {
            "theme": "中小企業向け人事制度設計プロセス = 評価/等級/給与の三位一体パッケージ",
            "companies": ["ミナジン"],
            "common_patterns": [
                "中小 SaaS（みんなの人事評価）+ コンサル（007 オーダー）+ 運用サポート（003/009）の 3 階層",
                "制度設計 → 構築 → 運用定着までワンストップで提供",
                "クライアント別カスタマイズ（OZsoft / ジャパンアーツ / MC / フュディアル等）",
            ],
            "divergence": [
                "MOON-X は内製人事チームで設計（30-60 名規模）",
                "ミナジンは外部コンサル（30-300 名規模 SMB）",
            ],
            "ai_agent_target": "smb-system-design-walker / triad-package-builder",
        },
        {
            "theme": "セミナー集客 → 営業フローの 10 年蓄積（人事の大学 2006-2014）",
            "companies": ["ミナジン", "人事の大学"],
            "common_patterns": [
                "業界横断テーマ（タレントマネジメント / ダイバーシティ / グローバル）の 10 年トレンド変化",
                "プレゼン → 提案 → コンサル受注の典型 3 段ファネル",
                "オンライン版 vs 対面版の章立て差分（令和構築&運用セミナー Web/東京）",
            ],
            "divergence": [
                "プレイド Nobu セミナーは 1 回完結",
                "人事の大学は 10 年連続シリーズで累積資産化",
            ],
            "ai_agent_target": "seminar-archive-curator / online-offline-adapter",
        },
        {
            "theme": "運用サポートサービスの SMB 標準提案書 = Orbit 直結テンプレ",
            "companies": ["ミナジン"],
            "common_patterns": [
                "標準提案書（pdf / pptx）+ 賞与運営ガイド + 評定計算シート の 4 点セット",
                "月次運用 KPI（評価会議運営 / 賞与額計算 / 中間面談 / フィードバック）",
                "クライアント別カスタマイズ前提のテンプレ化",
            ],
            "divergence": [
                "プレイド Orbit 月次運用は大手向け",
                "ミナジン運用サポートは SMB 向け定型パッケージ",
            ],
            "ai_agent_target": "orbit-template-engine / smb-operations-walker",
        },
        {
            "theme": "強み発見 × Authentic Self（CODE 個人引力）= Phase 11 補強素材",
            "companies": ["ミナジン", "人事の大学"],
            "common_patterns": [
                "自分の強みの見つけ方ワーク（pptx）= Wrzesniewski 1997 Calling + Bandura SE 自覚化プロセス",
                "白潟総研 採用 35 のしかけ = SMB 採用ペインの構造化",
                "個人引力（CODE）の言語化に必要な 3 つの問い（What/Why/How）",
            ],
            "divergence": [
                "Phase 11 SSOT で学術的バックボーン確立済",
                "ミナジン素材は SMB 適用層での実装事例",
            ],
            "ai_agent_target": "code-strengths-extractor / authentic-self-mapper",
        },
    ]
    return base + phase4_additions


def main():
    companies = {
        "DMM": {"subfolders": collect_dmm()},
        "MOON-X": {"subfolders": collect_moonx()},
        "プレイド": {"subfolders": collect_plaid()},
        "ミナジン": {"subfolders": collect_minagine()},
        "人事の大学": {"subfolders": collect_jinji_univ()},
    }
    # Summary
    summary = {}
    for company, data in companies.items():
        total_files = 0
        analyzed_files = 0
        for sub, sub_data in data["subfolders"].items():
            for f in sub_data["files"]:
                total_files += 1
                if f.get("phase_analyzed") != "未分析":
                    analyzed_files += 1
        summary[company] = {
            "total_files": total_files,
            "analyzed_files": analyzed_files,
            "coverage_pct": round(analyzed_files / total_files * 100, 2) if total_files > 0 else 0,
            "subfolder_count": len(data["subfolders"]),
        }

    db = {
        "version": "v2.0",
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M JST"),
        "scope": [
            "DMM HRBP 14 サブフォルダ",
            "MOON-X 全件",
            "プレイド全件",
            "ミナジン 02_MINAGINE/01_人事制度検討資料 全件",
            "人事の大学 全件 + コンサル事例",
        ],
        "summary": summary,
        "phase_completion": {
            "Phase 1": "DMM HRBP 3 大ファイル深掘り（スカウト/面接官研修/Wevox）",
            "Phase 2": "DMM HRBP 残 6 サブフォルダ深掘り",
            "Phase 3": "DMM 残補強 + MOON-X 全件 + プレイド全件 (36 ファイル 13 MD)",
            "Phase 4": "ミナジン + 人事の大学 (37 ファイル / 11 MD)",
        },
        "companies": companies,
        "cross_company_insights": build_cross_insights_v2(),
        "analysis_md_inventory": {
            "Phase 1 (3 MD)": [
                "260513_DMM_スカウト文章分析_v0.1.md",
                "260513_DMM_面接官研修分析_v0.1.md",
                "260513_DMM_Wevoxコメント分析_v0.1.md",
            ],
            "Phase 2 (6 MD)": [
                "260514_DMM_02_オンボーディング_入社後面談_分析_v0.1.md",
                "260514_DMM_04_制度面_バリュー策定ワークショップ_分析_v0.1.md",
                "260514_DMM_05_労務対応_退職アンケート_分析_v0.1.md",
                "260514_DMM_07_組織体制_リファラル50運用_分析_v0.1.md",
                "260514_DMM_08_PMI_新規事業バックオフィスサポート_分析_v0.1.md",
                "260514_DMM_09_リーダー業務_人事分科会_分析_v0.1.md",
            ],
            "Phase 3 (13 MD)": [
                "260514_DMM_04_制度面_3ファイル_分析_v0.1.md",
                "260514_DMM_採用_HRBPオンボ_面接官研修基礎_3ファイル_分析_v0.1.md",
                "260514_DMM_05_労務対応_3ファイル_分析_v0.1.md",
                "260514_DMM_07_異動_08_PMI_3ファイル_分析_v0.1.md",
                "260514_MOONX_制度設計_3ファイル_分析_v0.1.md",
                "260514_MOONX_採用_オンボ業務フロー_3ファイル_分析_v0.1.md",
                "260514_MOONX_投資_市場_4ファイル_分析_v0.1.md",
                "260514_MOONX_労務テンプレ_2ファイル_分析_v0.1.md",
                "260514_プレイド_オンボ_PM_2ファイル_分析_v0.1.md",
                "260514_プレイド_プロサービス_3ファイル_分析_v0.1.md",
                "260514_プレイド_顧客伴走_3ファイル_分析_v0.1.md",
                "260514_プレイド_ナレッジ顧客_3ファイル_分析_v0.1.md",
                "260514_プレイド_マーケ組織セミナー_スタイル開発_分析_v0.1.md",
            ],
            "Phase 4 (11 MD)": [
                "260514_ミナジン_007道具箱_scouty_1ファイル_分析_v0.1.md",
                "260514_ミナジン_007道具箱_白潟採用35_強み発見_2ファイル_分析_v0.1.md",
                "260514_ミナジン_007道具箱_HiManager_職務評価_2ファイル_分析_v0.1.md",
                "260514_ミナジン_007制度事例_他社人事制度_3ファイル_分析_v0.1.md",
                "260514_ミナジン_007制度事例_評価者教育_1ファイル_分析_v0.1.md",
                "260514_ミナジン_008セミナーWeb版_1ファイル_分析_v0.1.md",
                "260514_ミナジン_008セミナー東京版_1ファイル_分析_v0.1.md",
                "260514_ミナジン_008コンサル_平川メソッド_3ファイル_分析_v0.1.md",
                "260514_ミナジン_008コンサル_クライアント別事例_4ファイル_分析_v0.1.md",
                "260514_人事の大学_2006_2010セミナー_4ファイル_分析_v0.1.md",
                "260514_人事の大学_2014成熟期セミナー_PM研修_4ファイル_分析_v0.1.md",
                "260514_人事の大学_コンサル事例_4ファイル_分析_v0.1.md",
                "260514_ミナジン_003運用支援パック_5ファイル_分析_v0.1.md",
            ],
        },
        "failed_downloads": [
            {"path": "/04_MOON-X/Moon-X案件_投資メモ (1).docx", "reason": "Dropbox 上で 0 byte"},
            {"path": "/01_DMM.com/01_HRビジネスパートナー/05_労務対応/01_労務対応/220819_ネクストキャリア制度 （仮称）.xlsx", "reason": "Dropbox 上で 0 byte"},
            {"path": "/02_MINAGINE/01_人事制度検討資料/007_オーダーコンサル/3_道具箱（参考資料）/07_ハイマネージャー/ピアリーセミナー資料/マネジメント能力を飛躍させる1on1の方法_ver1.5.pdf", "reason": "Phase 4 DL 失敗（11.5MB pdf・再 DL 未実施・代替 1on1 知見は HiManager 提案書で補完）"},
        ],
        "masking_policy": {
            "absolute_excluded": ["個人氏名", "メールアドレス", "電話番号", "給与・退職金・賞与金額", "住所・生年月日", "顧客社名・取引先名", "売上数字", "内部URL", "パスワード"],
            "abstracted": {"事業部名": "事業部A/B/C", "顧客社名": "事業領域C/D/E社", "子会社名": "子会社A/B/C/D社", "ミナジン社内関係者": "ベテランコンサル A / 社内ロール A"},
            "phase4_special": "ミナジンは user 在籍 10 年の会社のため特別配慮：個人エピソード・社内政治情報・窪さん打ち合わせフォルダは完全除外。クライアント実名（OZsoft / ジャパンアーツ / MC / フュディアル等）は A 社 / B 社 / C 社 / D 社 に番号統一抽象化",
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    print(f"=== JSON DB v2.0 生成完了 ===")
    print(f"出力先: {OUT}")
    print(f"サイズ: {OUT.stat().st_size / 1024:.1f} KB")
    print()
    print("=== サマリー ===")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
