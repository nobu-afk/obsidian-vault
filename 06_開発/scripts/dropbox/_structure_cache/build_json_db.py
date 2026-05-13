#!/usr/bin/env python3
"""Phase 3 統合 JSON DB 生成スクリプト

3 社のフォルダ構造 + 選定済ファイル + 分析 MD 紐付けを 1 つの JSON DB に統合。
引き継ぎ書 §4.1 のスキーマに準拠。
"""
from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime

CACHE = Path("/Users/ishiinobuyuki/Documents/Obsidian Vault/06_開発/scripts/dropbox/_structure_cache")
OUT = Path("/Users/ishiinobuyuki/Documents/Obsidian Vault/04_GrowthFix/01_サービス設計/_DMM資産_AI武装連携/260514_Dropbox網羅DB_v1.0.json")

# Phase 1+2 既深掘り 9 ファイル（マッピング）
PHASE_12_MAP = {
    "/01_DMM.com/01_HRビジネスパートナー/01_採用関連/06_ダイレクト管理資料/220630_【admin】スカウト文章等について.xlsx": {
        "analysis_md": "260513_DMM_スカウト文章分析_v0.1.md",
        "phase": "Phase 1",
    },
    "/01_DMM.com/01_HRビジネスパートナー/03_人材開発（育成）/04_マネジメント育成/面接官研修.pptx": {
        "analysis_md": "260513_DMM_面接官研修分析_v0.1.md",
        "phase": "Phase 1",
    },
    "/01_DMM.com/01_HRビジネスパートナー/06_組織開発（データ）/02_Wevox全体/220701_wevoxコメント精査SS.xlsx": {
        "analysis_md": "260513_DMM_Wevoxコメント分析_v0.1.md",
        "phase": "Phase 1",
    },
    "/01_DMM.com/01_HRビジネスパートナー/02_オンボーディング/04_入社後面談/入社後面談【中途】.xlsx": {
        "analysis_md": "260514_DMM_02_オンボーディング_入社後面談_分析_v0.1.md",
        "phase": "Phase 2",
    },
    "/01_DMM.com/01_HRビジネスパートナー/04_制度面/04_バリュー検討/220701_バリュー策定ワークショップ.pptx": {
        "analysis_md": "260514_DMM_04_制度面_バリュー策定ワークショップ_分析_v0.1.md",
        "phase": "Phase 2",
    },
    "/01_DMM.com/01_HRビジネスパートナー/05_労務対応/04_退職関連資料/220822_退職・社員アンケート（回答）.xlsx": {
        "analysis_md": "260514_DMM_05_労務対応_退職アンケート_分析_v0.1.md",
        "phase": "Phase 2",
    },
    "/01_DMM.com/01_HRビジネスパートナー/07_組織体制/02_リファラル50運用/220901_リファラル50（運用フロー）.pdf": {
        "analysis_md": "260514_DMM_07_組織体制_リファラル50運用_分析_v0.1.md",
        "phase": "Phase 2",
    },
    "/01_DMM.com/01_HRビジネスパートナー/08_PMI/220912_prj-bo改善16-新規事業バックオフィスサポート.pptx": {
        "analysis_md": "260514_DMM_08_PMI_新規事業バックオフィスサポート_分析_v0.1.md",
        "phase": "Phase 2",
    },
    "/01_DMM.com/01_HRビジネスパートナー/09_リーダー業務/01_課業の洗い出し/220912_20211102_人事分科会用.pptx": {
        "analysis_md": "260514_DMM_09_リーダー業務_人事分科会_分析_v0.1.md",
        "phase": "Phase 2",
    },
}

# Phase 3 個別分析 MD と対象ファイル（複数ファイル束ねた MD はファイル毎にマッピング）
PHASE_3_FILE_TO_MD = {
    # DMM 04_制度面 3 ファイル
    "/01_DMM.com/01_HRビジネスパートナー/04_制度面/01_COM/02_COM人事制度/02_スキル評価/スキル評価 - 職能集計（2020_03_04時点）_作業用.xlsx": "260514_DMM_04_制度面_3ファイル_分析_v0.1.md",
    "/01_DMM.com/01_HRビジネスパートナー/04_制度面/01_COM/08_手当類の整理/マスタデータ/手当出力.xlsx": "260514_DMM_04_制度面_3ファイル_分析_v0.1.md",
    "/01_DMM.com/01_HRビジネスパートナー/04_制度面/01_COM/01_子会社関連/05_DMMチャットブースト/HSD他2107-004【HSD】就業規則.pdf": "260514_DMM_04_制度面_3ファイル_分析_v0.1.md",
    # DMM 採用 + HRBP オンボ + 面接官研修基礎 3 ファイル
    "/01_DMM.com/01_HRビジネスパートナー/01_採用関連/02_プロジェクト管理/220630_中途採用分科会data.xlsx": "260514_DMM_採用_HRBPオンボ_面接官研修基礎_3ファイル_分析_v0.1.md",
    "/01_DMM.com/01_HRビジネスパートナー/02_オンボーディング/03_HRBPオンボーディング/03_社内営業資料/HRBP社内営業用資料_final.pptx": "260514_DMM_採用_HRBPオンボ_面接官研修基礎_3ファイル_分析_v0.1.md",
    "/01_DMM.com/01_HRビジネスパートナー/03_人材開発（育成）/02_研修一覧/01_初級TL/面接官研修（基礎）/220819_面接官研修.pptx": "260514_DMM_採用_HRBPオンボ_面接官研修基礎_3ファイル_分析_v0.1.md",
    # DMM 05_労務対応 3 ファイル
    "/01_DMM.com/01_HRビジネスパートナー/05_労務対応/01_労務対応/220701_労務対応素材.pptx": "260514_DMM_05_労務対応_3ファイル_分析_v0.1.md",
    "/01_DMM.com/01_HRビジネスパートナー/05_労務対応/01_労務対応/220819_ネクストキャリア制度 （仮称）.xlsx": "260514_DMM_05_労務対応_3ファイル_分析_v0.1.md",
    "/01_DMM.com/01_HRビジネスパートナー/05_労務対応/04_退職関連資料/220822_入社・社員アンケート（回答）.xlsx": "260514_DMM_05_労務対応_3ファイル_分析_v0.1.md",
    "/01_DMM.com/01_HRビジネスパートナー/05_労務対応/04_退職関連資料/220824_【com】2021年度退職者分析.xlsx": "260514_DMM_05_労務対応_3ファイル_分析_v0.1.md",
    # DMM 07_組織体制 + 08_PMI 3 ファイル
    "/01_DMM.com/01_HRビジネスパートナー/07_組織体制/00_異動関連資料/02_異動関連ナレッジ/220901_異動関連ナレッジ.pdf": "260514_DMM_07_異動_08_PMI_3ファイル_分析_v0.1.md",
    "/01_DMM.com/01_HRビジネスパートナー/08_PMI/02_PMI対応企業/01_comidia/07_PMI/220824_オンボーディング.pptx": "260514_DMM_07_異動_08_PMI_3ファイル_分析_v0.1.md",
    "/01_DMM.com/01_HRビジネスパートナー/08_PMI/01_PMIナレッジ/02_ナレッジ（参照ボックス）/220908_【DMMオンクレ】 人事労務管理マニュアル.pptx": "260514_DMM_07_異動_08_PMI_3ファイル_分析_v0.1.md",
    # MOON-X 制度設計 3 ファイル
    "/04_MOON-X/02_制度設計/人事制度素案.xlsx": "260514_MOONX_制度設計_3ファイル_分析_v0.1.md",
    "/04_MOON-X/02_制度設計/グレードマッピング2023.xlsx": "260514_MOONX_制度設計_3ファイル_分析_v0.1.md",
    "/04_MOON-X/Peopleに関する課題.pdf": "260514_MOONX_制度設計_3ファイル_分析_v0.1.md",
    # MOON-X 採用・オンボ業務フロー 3 ファイル
    "/04_MOON-X/01_業務フロー/221106_業務フロー（採用広報〜採用）.pdf": "260514_MOONX_採用_オンボ業務フロー_3ファイル_分析_v0.1.md",
    "/04_MOON-X/01_業務フロー/221106_オンボーディング.pdf": "260514_MOONX_採用_オンボ業務フロー_3ファイル_分析_v0.1.md",
    "/04_MOON-X/採用広報(ケラッタ).pptx": "260514_MOONX_採用_オンボ業務フロー_3ファイル_分析_v0.1.md",
    "/04_MOON-X/採用広報（ケラッタ）.pptx": "260514_MOONX_採用_オンボ業務フロー_3ファイル_分析_v0.1.md",
    # MOON-X 投資・市場 4 ファイル
    "/04_MOON-X/投資情報共有会20230207.pptx": "260514_MOONX_投資_市場_4ファイル_分析_v0.1.md",
    "/04_MOON-X/05_参考資料/220822スタートアップ・ベンチャー企業向け人事・組織領域の取り組みに関する調査.pdf": "260514_MOONX_投資_市場_4ファイル_分析_v0.1.md",
    "/04_MOON-X/05_参考資料/00_LayerX/221006_公開用_LayerX羅針盤_2022010_ver_1.1__2_.pdf": "260514_MOONX_投資_市場_4ファイル_分析_v0.1.md",
    "/04_MOON-X/05_参考資料/221007_MoonX-EarnOut-Slide-211202.pdf": "260514_MOONX_投資_市場_4ファイル_分析_v0.1.md",
    # MOON-X 労務テンプレ 2 ファイル
    "/04_MOON-X/03_労務/産業医活動テンプレート/産業衛生活動お役立ちテンプレート一覧 Ver1.2.pdf": "260514_MOONX_労務テンプレ_2ファイル_分析_v0.1.md",
    "/04_MOON-X/03_労務/産業医活動テンプレート/1.衛生委員会/18衛生委員会の立ち上げと運用手引き Ver1.2.pdf": "260514_MOONX_労務テンプレ_2ファイル_分析_v0.1.md",
    # プレイド オンボ・PM 2 ファイル
    "/00_プレイド/オンボーディング/2404_オンボーディングチーム・アップデート.pptx": "260514_プレイド_オンボ_PM_2ファイル_分析_v0.1.md",
    "/00_プレイド/オンボーディング/PMプロセスについて.pptx": "260514_プレイド_オンボ_PM_2ファイル_分析_v0.1.md",
    # プレイド プロサービス 3 ファイル
    "/00_プレイド/アルファー/プロフェッショナルサービス｢PLAID ALPHA｣のご紹介.pptx": "260514_プレイド_プロサービス_3ファイル_分析_v0.1.md",
    "/00_プレイド/ナレッジ/提案書類/STUDIO ZERO_whitepaper.pptx": "260514_プレイド_プロサービス_3ファイル_分析_v0.1.md",
    "/00_プレイド/ナレッジ/STUDIO ZERO_Proposal (1).pptx": "260514_プレイド_プロサービス_3ファイル_分析_v0.1.md",
    # プレイド 顧客伴走 3 ファイル
    "/00_プレイド/01_顧客デリバリー/東京建物/20230731_東京建物_CXアプリ構想_最終報告資料_保存版.pptx": "260514_プレイド_顧客伴走_3ファイル_分析_v0.1.md",
    "/00_プレイド/01_顧客デリバリー/関西電力/202404_新規事業伴走支援_関西電力様.pptx": "260514_プレイド_顧客伴走_3ファイル_分析_v0.1.md",
    "/00_プレイド/その他/エモーションテック/応募図書.pptx": "260514_プレイド_顧客伴走_3ファイル_分析_v0.1.md",
    # プレイド ナレッジ顧客 3 ファイル
    "/00_プレイド/01_顧客デリバリー/JTB/240523_JTB_コーポマーケ戦略策定_v2.pptx": "260514_プレイド_ナレッジ顧客_3ファイル_分析_v0.1.md",
    "/00_プレイド/01_顧客デリバリー/Accel 3/20_ノウハウ共有/新規事業開発の心得.pptx": "260514_プレイド_ナレッジ顧客_3ファイル_分析_v0.1.md",
    "/00_プレイド/ナレッジ/ワークショップ/ユーザー体験の設計とは？：マリオの話（UEPON）.pptx": "260514_プレイド_ナレッジ顧客_3ファイル_分析_v0.1.md",
    # プレイド マーケ組織セミナー 1 ファイル
    "/00_プレイド/その他/Nobuセミナー/マーケ組織セミナー第二弾  組織成長を加速させる秘訣は「スタイル開発」.pptx": "260514_プレイド_マーケ組織セミナー_スタイル開発_分析_v0.1.md",
}


def load_structure(filename: str) -> list[dict]:
    p = CACHE / filename
    if not p.exists():
        return []
    with p.open() as f:
        return json.load(f)


def normalize_for_match(p: str) -> str:
    """Normalize path for comparison (handle full-width vs half-width parens, slash differences)."""
    # Note: Dropbox returns paths with both half-width and full-width characters
    # We compare loosely by removing some variations
    return p.replace("（", "(").replace("）", ")").replace("．", ".").replace("　", " ")


def lookup_analysis(path: str) -> dict | None:
    """Look up phase-1/2/3 analysis assignment for a Dropbox path."""
    # Direct match first
    if path in PHASE_12_MAP:
        return {
            "phase": PHASE_12_MAP[path]["phase"],
            "analysis_md": PHASE_12_MAP[path]["analysis_md"],
        }
    if path in PHASE_3_FILE_TO_MD:
        return {"phase": "Phase 3", "analysis_md": PHASE_3_FILE_TO_MD[path]}
    # Normalized comparison
    np = normalize_for_match(path)
    for k, v in PHASE_12_MAP.items():
        if normalize_for_match(k) == np:
            return {"phase": v["phase"], "analysis_md": v["analysis_md"]}
    for k, v in PHASE_3_FILE_TO_MD.items():
        if normalize_for_match(k) == np:
            return {"phase": "Phase 3", "analysis_md": v}
    return None


def subfolder_of(path: str, root: str, depth: int = 1) -> str:
    """Get the n-th subfolder name from root."""
    if not path.startswith(root):
        return "(その他)"
    rest = path[len(root):].lstrip("/")
    parts = rest.split("/")
    if len(parts) <= depth:
        return "(直下)"
    return parts[depth - 1] if depth >= 1 else "(直下)"


def collect_dmm() -> dict:
    """Collect DMM HRBP structure into subfolders."""
    all_entries: list[dict] = []
    seen = set()
    for fn in ["dmm_hrbp_full_structure.json", "dmm_01_recruit.json",
                "dmm_03_dev.json", "dmm_06_data.json"]:
        for e in load_structure(fn):
            p = e.get("path", "")
            if p in seen:
                continue
            seen.add(p)
            all_entries.append(e)
    root = "/01_DMM.com/01_HRビジネスパートナー"
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
        ana = lookup_analysis(e["path"])
        if ana:
            rec["phase_analyzed"] = ana["phase"]
            rec["analysis_md"] = ana["analysis_md"]
        else:
            rec["phase_analyzed"] = "未分析"
            rec["analysis_md"] = None
        subfolders[sub]["files"].append(rec)
    return subfolders


def collect_moonx() -> dict:
    entries = load_structure("moonx_structure.json")
    root = "/04_MOON-X"
    subfolders: dict[str, dict] = {}
    for e in entries:
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
        ana = lookup_analysis(e["path"])
        if ana:
            rec["phase_analyzed"] = ana["phase"]
            rec["analysis_md"] = ana["analysis_md"]
        else:
            rec["phase_analyzed"] = "未分析"
            rec["analysis_md"] = None
        subfolders[sub]["files"].append(rec)
    return subfolders


def collect_plaid() -> dict:
    entries = load_structure("plaid_structure.json")
    root = "/00_プレイド"
    subfolders: dict[str, dict] = {}
    for e in entries:
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
        ana = lookup_analysis(e["path"])
        if ana:
            rec["phase_analyzed"] = ana["phase"]
            rec["analysis_md"] = ana["analysis_md"]
        else:
            rec["phase_analyzed"] = "未分析"
            rec["analysis_md"] = None
        subfolders[sub]["files"].append(rec)
    return subfolders


def build_cross_insights() -> list[dict]:
    """Cross-company insights from individual MD findings. Populated based on hand-aggregated 横断パターン."""
    return [
        {
            "theme": "在籍 5-7 年層の「ゴールデン離反」現象",
            "companies": ["DMM"],
            "common_patterns": [
                "Wevox 在籍中ヒアリングと退職アンケートで 3 大認識ズレ",
                "退職主因が年数別に変化（1-3年=キャリア形成不安、5-7年=やりたい仕事不在、7年以上=やりがい喪失）",
            ],
            "divergence": [
                "DMM では NPS -12.4 → -61.9 の 49.5 ポイント期待剥落を定量化（v0.3 + 新発見）",
                "上長 69% が退職予見、引き止め行動 31% という構造問題",
            ],
            "ai_agent_target": "retention-analyzer / expectation-mapper",
        },
        {
            "theme": "顧客伴走 PM プロセスの 8 フェーズ × ゲート設計",
            "companies": ["プレイド"],
            "common_patterns": [
                "アウトプット定義（ゴール状態言語化）でフェーズを区切る",
                "Impact × Reach マトリクスでの施策優先度スコアリング",
                "NG チェックリスト（フェーズ毎の落とし穴 3-5 件）の明示",
            ],
            "divergence": [
                "プレイドは大手顧客向け（C 社規模 100名+）",
                "Gravity Orbit は中小経営者直伴走（30-100名）",
            ],
            "ai_agent_target": "orbit-monthly-engine / delivery-pm-mapper",
        },
        {
            "theme": "スタートアップ「50 名の壁」と労務基盤義務化",
            "companies": ["MOON-X"],
            "common_patterns": [
                "産業医選任・衛生委員会・健診管理・ストレスチェック・長時間労働管理の 5 義務同時発動",
                "21 種類の産業衛生テンプレートで法令対応一気通貫",
            ],
            "divergence": [
                "MOON-X は事前設計済（カーブアウト時点で）",
                "通常 SMB は壁到達後に右往左往",
            ],
            "ai_agent_target": "labor-template-library / 50名の壁-checker",
        },
        {
            "theme": "Layer-3 育成不在は規模拡大時の組織崩壊トリガー",
            "companies": ["DMM", "MOON-X"],
            "common_patterns": [
                "MOON-X 経営幹部が課題自己申告で「Layer-3 不在」を明示",
                "DMM HRBP の組織課題でもマネージャー育成は最大課題",
            ],
            "divergence": [
                "MOON-X は 30-60 名規模で既に課題顕在化",
                "DMM は 1,000+ 名規模で構造的常態化",
            ],
            "ai_agent_target": "cultivate-manager-copilot",
        },
        {
            "theme": "MVV / バリュー策定 → 浸透の構造的ギャップ",
            "companies": ["DMM", "MOON-X"],
            "common_patterns": [
                "DMM はバリュー策定 WS で「鉄の掟」言語化（v0.3 既収録）",
                "MOON-X People 課題 PDF で MVV 浸透の順序が経営陣で議論",
                "Mercer 調査：MVV 策定 93% / 評価組込 30% という業界 gap",
            ],
            "divergence": [
                "DMM は策定済・浸透途上",
                "MOON-X は浸透順序を設計段階で議論",
            ],
            "ai_agent_target": "vision-codifier / mvv-permeation-tracker",
        },
        {
            "theme": "リファラル/社内公募 = 内部流動性 8 フェーズ設計",
            "companies": ["DMM"],
            "common_patterns": [
                "リファラル50（外部採用）4 フェーズ運用設計",
                "社内公募（内部異動）8 フェーズ × HRMOS + 社内掲示板二層管理",
                "二段階インセンティブ・紹介者/被紹介者分離コミュニケーション",
            ],
            "divergence": [
                "SMB ではほぼ未整備（Shift R スコープ拡張根拠）",
            ],
            "ai_agent_target": "referral-engine / internal-mobility-designer",
        },
        {
            "theme": "プロフェッショナルサービスの差別化軸「実行力 / 内製化 / 半歩リード」",
            "companies": ["プレイド"],
            "common_patterns": [
                "PLAID ALPHA = SaaS × プロサービス ハイブリッドモデル",
                "STUDIO ZERO 「戦略と実行の認識ズレ」訴求 → 実行まで伴走",
                "「クライアントが主体、当社は半歩リード」の役割設計",
            ],
            "divergence": [
                "プレイドは Sentinel プロダクトを持つ",
                "GrowthFix は診断プロダクト（Gravity Scan）+ プロサービス（Shift / Orbit / Coaching）",
            ],
            "ai_agent_target": "proposal-builder / engagement-flow-mapper",
        },
        {
            "theme": "セミナー設計：文脈→積み上げ→感情フック→クイズ→事例→クロージング",
            "companies": ["プレイド"],
            "common_patterns": [
                "Nobu セミナー第二弾「スタイル開発」での 7 段階流れ",
                "感情フック（生の不満 4 つ）→ クイズ（メタファー）",
            ],
            "divergence": [
                "プレイド：ビジネスは闘争型（機能論）",
                "GrowthFix：組織引力（存在論）= 上位概念",
            ],
            "ai_agent_target": "seminar-designer / hook-generator",
        },
        {
            "theme": "「Want to × アイデンティティ更新」のコーチング設計（共通語彙）",
            "companies": ["プレイド"],
            "common_patterns": [
                "プレイドの組織変容コーチング 4 ステップが GrowthFix Coaching と同語彙",
                "Step1 動機（Want to）特定 → Step4 アイデンティティ更新で完了",
            ],
            "divergence": [
                "市場での概念的妥当性の傍証（競合に同フレーム）",
            ],
            "ai_agent_target": "coaching-session-designer",
        },
    ]


def build_summary(companies: dict) -> dict:
    s = {}
    for company, data in companies.items():
        total_files = 0
        analyzed_files = 0
        for sub, sub_data in data["subfolders"].items():
            for f in sub_data["files"]:
                total_files += 1
                if f.get("phase_analyzed") != "未分析":
                    analyzed_files += 1
        s[company] = {
            "total_files": total_files,
            "analyzed_files": analyzed_files,
            "coverage_pct": round(analyzed_files / total_files * 100, 1) if total_files > 0 else 0,
            "subfolder_count": len(data["subfolders"]),
        }
    return s


def main():
    companies = {
        "DMM": {"subfolders": collect_dmm()},
        "MOON-X": {"subfolders": collect_moonx()},
        "プレイド": {"subfolders": collect_plaid()},
    }
    summary = build_summary(companies)
    db = {
        "version": "v1.0",
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M JST"),
        "scope": ["DMM HRBP 14 サブフォルダ", "MOON-X 全件", "プレイド全件"],
        "summary": summary,
        "phase_completion": {
            "Phase 1": "DMM HRBP 3 大ファイル深掘り（スカウト/面接官研修/Wevox）",
            "Phase 2": "DMM HRBP 残 6 サブフォルダ深掘り（オンボ/バリュー/退職/リファラル50/PMI/分科会）",
            "Phase 3": "DMM 残補強 4 サブフォルダ + MOON-X 全件 + プレイド全件 (36 ファイル 13 MD)",
        },
        "companies": companies,
        "cross_company_insights": build_cross_insights(),
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
        },
        "failed_downloads": [
            {"path": "/04_MOON-X/Moon-X案件_投資メモ (1).docx", "reason": "Dropbox 上で 0 byte"},
            {"path": "/01_DMM.com/01_HRビジネスパートナー/05_労務対応/01_労務対応/220819_ネクストキャリア制度 （仮称）.xlsx", "reason": "Dropbox 上で 0 byte"},
        ],
        "masking_policy": {
            "absolute_excluded": ["個人氏名", "メールアドレス", "電話番号", "給与・退職金・賞与金額", "住所・生年月日", "顧客社名・取引先名", "売上数字", "内部URL", "パスワード"],
            "abstracted": {"事業部名": "事業部A/B/C", "顧客社名": "事業領域C/D/E社", "子会社名": "子会社A/B/C/D社"},
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    print(f"=== JSON DB 生成完了 ===")
    print(f"出力先: {OUT}")
    print(f"サイズ: {OUT.stat().st_size / 1024:.1f} KB")
    print()
    print("=== サマリー ===")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
