# 06_開発/scripts/ フォルダ構造（260513 Phase 2 C-1 整理）

## サブフォルダ（軽量再編・依存安全）

```
scripts/
├── _README.md          ← 本ファイル
├── config/             ← API キー設定（gitignore対象）4本
│   ├── config_claude.json
│   ├── config_fitbit.json
│   ├── config_meta.json
│   └── config_token_pricing.json
├── converters/         ← PDF/MD 変換ユーティリティ 2本
│   ├── convert_1on1_pdf.py
│   └── convert_pdf_to_md.py
├── extractors/         ← PDF 抽出ユーティリティ 3本
│   ├── extract_ocr_pages.py
│   ├── extract_pdf_text.py
│   └── extract_tables_from_pdf.py
├── hooks/              ← Claude Code hook（既存）
├── orbit_data/         ← Orbit 顧客データ（既存）
├── orbit_reports/      ← Orbit レポート出力（既存）
└── （直下に残った 30 本のスクリプト：audit / deploy / lint / note / gravity / fitbit / meta / orbit / token / wp / その他）
```

## 直下に残した理由（依存温存）

| スクリプト群 | 残した理由 |
|---|---|
| audit_*.py（3本） | `~/.claude/settings.local.json` の hook 経由で呼ばれる + CLAUDE.md 参照あり |
| orbit_*.py（2本） | `orbit_data/` `orbit_reports/` を SCRIPT_DIR 直下と仮定したコード |
| deploy*.sh + verify_deployment.sh | LP デプロイの主軸・パス変更は本番影響 |
| lint*.sh / lint*.py | hook 経由で呼ばれる |
| gravity_*.py / note_*.py | 多数の Vault SSOT を参照 |
| meta_ads_daily.py / fitbit_*.py | daily skill から呼ばれる |
| wp_decommission.py | 一度きりのスクリプトだが歴史的価値 |

## config_*.json 参照スクリプトのパス更新（260513）

- `fitbit_auth.py`：`config/config_fitbit.json`
- `fitbit_daily.py`：`config/config_fitbit.json`
- `meta_ads_daily.py`：`config/config_meta.json`
- `code_diagnosis_server.py`：`config/config_claude.json`
- `token_usage.py`：`config/config_token_pricing.json`
- `.gitignore`：`06_開発/scripts/config/config_*.json` に更新

## 動作確認

- `python3 06_開発/scripts/token_usage.py` で出力確認済（260513 Phase 2 完了時点）

## Phase 3 候補（高リスク・要慎重）

- audit/ deploy/ lint/ orbit/ への完全カテゴリ化は、hook と skill のパス参照を全て更新する必要があり Phase 3 扱い
- 現状で C-1 軽量版は完了
