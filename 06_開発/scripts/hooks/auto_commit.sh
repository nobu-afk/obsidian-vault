#!/usr/bin/env bash
# auto_commit.sh
# Stop hook：Claude セッション終了時に未コミット変更があれば自動 commit
#
# 設計（260502 確立）：
#   - 5 ヶ月放置を二度と起こさない装置
#   - Stop イベントで起動・変更件数 ≥ 1 で自動 commit
#   - 自動 push はしない（認証エラーで loop 化防止・手動 push が安全）
#   - commit message は変更ファイル数 + 主要編集ディレクトリで自動生成
#
# 関連：
#   - feedback_lp_mobile_audit_required.md（hook 設計パターン）
#   - 5/2 09:00 git 履歴 5 ヶ月放置事故対策

set -e
cd "/Users/ishiinobuyuki/Documents/Obsidian Vault" || exit 0

# git リポジトリでない場合は何もしない
git rev-parse --git-dir >/dev/null 2>&1 || exit 0

# 変更件数カウント（gitignored は対象外）
CHANGES=$(git status --short 2>/dev/null | wc -l | tr -d ' ')
[[ "$CHANGES" == "0" ]] && exit 0

# パスワード等の secrets が含まれていないかガード
if git diff --cached --no-color 2>/dev/null | grep -qE "cgq1fv99|api_key.*[a-zA-Z0-9]{20,}|password.*=.*[a-zA-Z0-9]{8,}"; then
    echo "⚠️  auto_commit: secrets 検出のため commit 中止。手動確認してください。" >&2
    exit 0
fi
if git diff --no-color 2>/dev/null | grep -qE "cgq1fv99|api_key.*[a-zA-Z0-9]{20,}"; then
    echo "⚠️  auto_commit: 未ステージ diff に secrets 検出。git add 前に確認してください。" >&2
    exit 0
fi

# stage all
git add . 2>/dev/null

# stage 後の変更件数再カウント
STAGED=$(git diff --cached --name-only 2>/dev/null | wc -l | tr -d ' ')
[[ "$STAGED" == "0" ]] && exit 0

# 主要編集ディレクトリの推定（top 3）
TOP_DIRS=$(git diff --cached --name-only 2>/dev/null | awk -F/ '{print $1}' | sort | uniq -c | sort -rn | head -3 | awk '{print $2}' | tr '\n' ' ')

# JST タイムスタンプ
TS=$(TZ=Asia/Tokyo date +"%Y-%m-%d %H:%M JST")

# commit message
MSG="auto: ${TS} (${STAGED} files: ${TOP_DIRS})"

git commit -m "$MSG" 2>&1 | tail -1

# 自動 push（260503 追加・Stop hook は単発発火のため loop 化しない）
# 失敗時は警告のみ（exit 0 で hook を阻害しない・GitHub Push Protection が secrets 二重防御）
if git push origin main 2>&1 | tail -3; then
    echo "✅ auto_commit + push 成功: ${STAGED} files (${MSG})" >&2
else
    echo "⚠️  push 失敗（手動実行: cd Vault && git push origin main）: ${STAGED} files は commit 済" >&2
fi
exit 0
