# 04_デイリーログ フォルダ構造（260513 Phase 2 月別分割化）

## 親子構造

```
04_デイリーログ/
├── _README.md           ← 本ファイル
├── 2603/                ← 3月（daily 12本 + work_log 1本 = 13本）
├── 2604/                ← 4月（daily 24本 + weekly_close 3本 + work_log 1本 = 28本）
└── 2605/                ← 5月（daily 12本 + weekly_close 3本 + work_log 1本 + その他 5本 = 21本）
```

## 命名規則

- daily：`YYMMDD_daily.md`
- weekly_close：`YYMMDD_weekly_close.md`（金曜の日付）
- work_log：`YYMM_work_log.md`（月次ファイル）

## 配置ルール

- 各ファイルは `YYMM = YYMMDD の最初4文字` のフォルダに配置
- YYMM フォルダが存在しない場合は `mkdir -p` で先に作成

## 関連 skill / script（260513 月別分割化対応済）

- **daily skill**：`~/.claude/skills/daily/SKILL.md` line 11, 86 更新済
- **weekly-close skill**：`~/.claude/skills/weekly-close/SKILL.md` line 17, 258 更新済
- **hotta-prep skill**：`~/.claude/skills/hotta-prep/SKILL.md` line 48-49 更新済
- **work-log skill**：`~/.claude/skills/work-log/SKILL.md` line 27, 170 更新済
- **sync-knowledge skill**：`~/.claude/skills/sync-knowledge/SKILL.md` line 49 更新済
- **meta_ads_daily.py**：`06_開発/scripts/meta_ads_daily.py` get_daily_log_path() 更新済

## 整理履歴

- 260513 Phase 2 A-3: 直下62本ベタ置き → 月別フォルダ化（A-3 実施）
  - 3月: 2603/（13本）
  - 4月: 2604/（28本）
  - 5月: 2605/（21本）
  - 関連skill 5本 + meta_ads_daily.py のパス参照を月別フォルダ対応に更新
