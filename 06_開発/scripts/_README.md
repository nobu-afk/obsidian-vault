# 06_開発/scripts/ フォルダ構造（260513 Phase 3 C-1拡張 完全カテゴリ化）

## 親子構造（14 サブフォルダ）

```
scripts/
├── _README.md          ← 本ファイル
├── audit/              ← 3本：audit_mobile_sync / audit_knowledge_sync / audit_wp_refs
├── lint/               ← 2本：lint_consistency.sh / lint_lp_internal_terms.py
├── deploy/             ← 4本：deploy.sh / deploy_whitepaper.sh / verify_deployment.sh / bump_cache_buster.sh
├── orbit/              ← 2本 + データ：orbit_monthly_report / orbit_quarterly_review + orbit_data/ + orbit_reports/
├── daily/              ← 5本：meta_ads_daily / fitbit_daily / fitbit_auth / token_usage / stock_watch
├── note/               ← 2本：note_editor / note_batch_editor
├── gravity/            ← 3本：gravity_code_report / gravity_scan_report / code_diagnosis_server
├── lp/                 ← 4本：add_service_schema / inject_ab_test_script / migrate_seminar_bar_to_js / wp_decommission
├── util/               ← 7本：audio_transcript_simple / transcribe_mp3 / format_markdown / merge_tables / split_markdown / config.py / md_to_pdf.sh
├── config/             ← 4本：config_claude / config_fitbit / config_meta / config_token_pricing.json（gitignore対象）
├── converters/         ← 2本：convert_1on1_pdf / convert_pdf_to_md
├── extractors/         ← 3本：extract_ocr_pages / extract_pdf_text / extract_tables_from_pdf
├── hooks/              ← 4本：Claude Code hook（既存）
└── __pycache__/        ← Pythonキャッシュ
```

## 役割

| サブフォルダ | 用途 |
|---|---|
| `audit/` | Vault 整合性監査・mobile.css 同期・WP 参照チェック |
| `lint/` | SSOT 用語チェック・LP 社内用語ゼロチェック |
| `deploy/` | LP / WP の FTP デプロイ・キャッシュバスター更新・デプロイ後検証 |
| `orbit/` | Orbit 月次レポート・四半期レビュー生成（orbit_data + orbit_reports 含む） |
| `daily/` | デイリーログ補助（Meta 広告 / Fitbit / トークン使用量 / 株価） |
| `note/` | Note 連載編集ツール |
| `gravity/` | Gravity CODE / Scan のレポート生成・診断 API サーバ |
| `lp/` | LP 改修系（schema 注入 / AB テスト / セミナーバー移行 / WP 廃止処理） |
| `util/` | 汎用ユーティリティ（音声・PDF・MD 操作） |
| `config/` | API キー設定（gitignore） |
| `converters/` `extractors/` | PDF 変換・抽出 |
| `hooks/` | PostToolUse / Stop hook |

## 直近の整理履歴

### Phase 3 C-1拡張（260513）
- 直下に散在していた 35 スクリプトを 9 テーマ別サブフォルダに完全分類
- パス参照を一括更新（5 SKILL.md + 1 hook + CLAUDE.md 4箇所 + lint_consistency.sh 1箇所 + verify_deployment.sh 1箇所 + 5 Python scripts の config 相対パス）
- 動作確認：token_usage.py / lint_consistency.sh 実行 OK

### Phase 2 C-1（260513・前段）
- config/ converters/ extractors/ の3軽量サブフォルダを先行新設

## パス参照更新一覧（C-1拡張完了時点）

### Hook
- `hooks/post_lp_edit_audit.sh`：audit/ + lint/ パス

### CLAUDE.md
- `bash 06_開発/scripts/lint/lint_consistency.sh`
- `python3 06_開発/scripts/audit/audit_mobile_sync.py`
- `bash 06_開発/scripts/deploy/verify_deployment.sh`
- `06_開発/scripts/daily/token_usage.py`

### Skill SKILL.md
- daily/: 3箇所（meta_ads_daily / fitbit_daily / token_usage / stock_watch 含む）
- weekly-close/: 2箇所
- sync-knowledge/: 4箇所
- company-os/: 2箇所
- company-os-review/: 2箇所
- japan-market/: 1箇所

### Script内自参照
- `lint/lint_consistency.sh` line 528 → `audit/audit_knowledge_sync.py`
- `deploy/verify_deployment.sh` line 130 → `deploy/deploy_whitepaper.sh`

### Python config 相対パス（5本）
- `daily/token_usage.py`: `SCRIPT_DIR.parent / "config" / "config_token_pricing.json"`
- `daily/fitbit_auth.py`：`"..", "config", "config_fitbit.json"`
- `daily/fitbit_daily.py`：同上
- `daily/meta_ads_daily.py`：`"..", "config", "config_meta.json"`
- `gravity/code_diagnosis_server.py`：`"..", "config", "config_claude.json"`
