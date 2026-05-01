#!/bin/bash
# PostToolUseFailure hook: Edit 失敗時に全角半角混在警告
# 260501 5/1 セッションで Edit 失敗 5+ 回（全角コロン「:」/ 全角括弧「(」「)」混在）の手戻り対策
# stdin: hook input JSON / stdout: additionalContext 注入で Claude に対処法を提示

PAYLOAD=$(cat)
ERROR=$(echo "$PAYLOAD" | jq -r '.tool_response.error // .tool_response.error_message // (.tool_response | tostring) // ""')

if echo "$ERROR" | grep -q "String to replace not found"; then
  jq -nc '{hookSpecificOutput: {hookEventName: "PostToolUseFailure", additionalContext: "💡 Edit 失敗（String to replace not found）→ 全角・半角混在の可能性大。\n\n対処法（260501 標準パターン）：\n1. Bash grep -n で実ファイルの該当行を確認（全角コロン「:」 vs 半角「:」／全角括弧「(」「)」 vs 半角「(」「)」）\n2. 確認した実ファイル文字をそのまま old_string にコピー\n3. 長い文字列は短い文字列単位で分割 Edit に切替え\n4. 同セッション内で同 MD を編集中なら、すでに変更済の箇所を二重編集していないか確認"}}'
fi
