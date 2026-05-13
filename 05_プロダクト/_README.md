# 05_プロダクト フォルダ構造（260513 Phase 3 B-1 親子2階層化）

## 親子構造

```
05_プロダクト/
├── _README.md              ← 本ファイル
├── Gravity/                ← Gravity サービス系（10 サブフォルダ）
│   ├── _ブランド/          ← Gravity 親ブランド LP + 成果物サンプル（旧 Gravity/ フォルダ）
│   ├── Code/               ← Gravity CODE LP + 診断 + executive（旧 GravityCode/）
│   ├── Scan/               ← Gravity Scan LP + 診断 + レポート（旧 GravityScan/）
│   ├── Shift/              ← Gravity Shift minimal LP（旧 GravityShift/）
│   ├── Recruit/            ← Gravity Recruit LP（旧 GravityRecruit/）
│   ├── Cultivate/          ← Gravity Cultivate LP（旧 GravityCultivate/）
│   ├── Orbit/              ← Gravity Orbit LP（旧 GravityOrbit/）
│   ├── Coaching/           ← Gravity Coaching minimal LP（旧 GravityCoaching/）
│   ├── Citations/          ← 引用ライブラリ公開ページ 253件（旧 Citations/）
│   └── WhitePaper/         ← WP V9 本番 + V10 開発版（旧 WhitePaper/）
├── コーポレート/           ← コーポレート HTML 12 フォルダ
│   ├── top_本番/           ← https://growthfix.jp/
│   ├── contact_本番/       ← /contact/
│   ├── news_本番/          ← /news/
│   ├── service_本番/       ← /service/
│   ├── profile_本番/       ← /profile/
│   ├── privacy-policy_本番/← /privacy-policy/
│   ├── knowledge_本番/     ← /knowledge/
│   ├── whitepaper_optin_本番/  ← /whitepaper/
│   ├── whitepaper-thanks_本番/ ← /whitepaper-thanks/
│   ├── achievement_本番/   ← /achievement/
│   ├── consultation-thanks_本番/← /consultation-thanks/
│   └── academy-wl_本番/    ← Academy ウェイトリスト
├── _共通/                  ← SSOT + デザインシステム + 共通PHP/CSS/JS（既存）
├── _assets/                ← LP共通アセット css/js（既存）
├── _archive/               ← 廃止フォルダ集約（既存）
├── _redirects/             ← .htaccess リダイレクト管理（既存）
└── assets_banners/         ← 広告バナー画像 31本（旧 banners_本番）
```

## 本番URL構造（変更なし）

```
https://growthfix.jp/                    ← コーポレート/top_本番/
https://growthfix.jp/contact/            ← コーポレート/contact_本番/
https://growthfix.jp/gravity/            ← Gravity/_ブランド/LP/
https://growthfix.jp/gravity-code/       ← Gravity/Code/LP/
https://growthfix.jp/gravity-code/executive/ ← Gravity/Code/診断_executive_本番/
https://growthfix.jp/gravity-scan/       ← Gravity/Scan/LP/
https://growthfix.jp/gravity-shift/      ← Gravity/Shift/LP/
https://growthfix.jp/gravity-orbit/      ← Gravity/Orbit/LP/
https://growthfix.jp/gravity-coaching/   ← Gravity/Coaching/LP/
https://growthfix.jp/whitepaper/         ← Gravity/WhitePaper/V9/（本体）+ コーポレート/whitepaper_optin_本番/（フォーム）
https://growthfix.jp/citations/          ← Gravity/Citations/LP/
```

## 整理履歴

### 260513 Phase 3 B-1
- ルート 28 フォルダ平置き状態 → 2階層親子化（Gravity/ + コーポレート/）
- GravityBlueprint 幽霊フォルダ問題解消（deploy.sh からBlueprint関連10行削除・260430 廃止済）
- banners_本番 → assets_banners/ にリネーム

### パス参照更新（260513 Phase 3 B-1）

| 更新ファイル | 更新内容 |
|---|---|
| `06_開発/scripts/deploy/deploy.sh` | GravityBlueprint 削除 + LP/diagnose/WP 全パス 14箇所更新 |
| `06_開発/scripts/deploy/deploy_whitepaper.sh` | 3パス（WhitePaper/V9 + whitepaper_optin） |
| `06_開発/scripts/lp/wp_decommission.py` | TOP_HTML + LOCAL_TO_REMOTE_HTMLS 11パス |
| `06_開発/scripts/gravity/gravity_scan_report.py` | TEMPLATE_PATH + REPORT_OUTPUT_DIR 3箇所 |
| `06_開発/scripts/lint/lint_consistency.sh` | check_required 等 6箇所 + entry loop 9パス |
| `~/.claude/skills/ai-paper-scan/SKILL.md` | Citations パス |
| `memory/*.md`（_archive 除く） | sed 一括置換 14パターン |

### 動作確認

- `audit_mobile_sync.py`：成功（mobile.css 同期チェック実行可）
- `lint_lp_internal_terms.py`：全 LP で社内用語ゼロ通過
- `audit_wp_refs.py`：WP 参照 0 件
- `lint_consistency.sh`：エラー 0 件・警告 19 件（既知の MD サイズ超過 + 孤児 memory 警告）

## FTP デプロイ実行時の注意

`bash 06_開発/scripts/deploy/deploy.sh` 実行時、本番 URL は変更なしで動作する。
ローカルパスが変わったが、`upload "source" "remote"` の `remote` 側は元のまま。
