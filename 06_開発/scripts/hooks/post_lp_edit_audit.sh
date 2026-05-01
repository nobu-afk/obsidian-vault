#!/bin/bash
# PostToolUse hook: 05_プロダクト/*.html 編集後に audit_mobile_sync.py 自動実行
# stdin: hook input JSON / stdout: hook output JSON（hookSpecificOutput.additionalContext で Claude に注入）
# CLAUDE.md「LP 編集時の自動機械チェック」ルールの hooks 化（260501 確立）

PAYLOAD=$(cat)
FILE_PATH=$(echo "$PAYLOAD" | jq -r '.tool_input.file_path // .tool_response.filePath // ""')

# 05_プロダクト/ 配下の .html ファイル編集の場合のみ実行
if echo "$FILE_PATH" | grep -qE '05_プロダクト/.+\.html$'; then
  AUDIT_OUTPUT=$(cd "/Users/ishiinobuyuki/Documents/Obsidian Vault" && python3 06_開発/scripts/audit_mobile_sync.py 2>&1 | tail -15)
  jq -nc --arg ctx "🔍 LP 編集検出（${FILE_PATH}）→ audit_mobile_sync.py 自動実行：

${AUDIT_OUTPUT}

⚠️ HIGH/MEDIUM 指摘あれば mobile.css 更新を検討してください。" \
    '{hookSpecificOutput: {hookEventName: "PostToolUse", additionalContext: $ctx}}'
fi
