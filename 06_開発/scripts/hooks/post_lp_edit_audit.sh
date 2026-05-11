#!/bin/bash
# PostToolUse hook: 05_プロダクト/*.html 編集後に
#   ① audit_mobile_sync.py（mobile.css 同期監査）
#   ② lint_lp_internal_terms.py（LP 社内用語ゼロ原則・260511 追加）
# を並列実行し、結果を additionalContext で Claude に注入。
#
# stdin: hook input JSON / stdout: hook output JSON
# 関連 SSOT:
#   - CLAUDE.md「LP 編集時の自動機械チェック」（260501 確立）
#   - 09_会社OS/公開/ガイドライン/design.md §LP 社内用語ゼロ原則（260511 追加）

PAYLOAD=$(cat)
FILE_PATH=$(echo "$PAYLOAD" | jq -r '.tool_input.file_path // .tool_response.filePath // ""')

# 05_プロダクト/ 配下の .html ファイル編集の場合のみ実行
if echo "$FILE_PATH" | grep -qE '05_プロダクト/.+\.html$'; then
  VAULT_DIR="/Users/ishiinobuyuki/Documents/Obsidian Vault"
  AUDIT_OUT="$(mktemp)"
  LINT_OUT="$(mktemp)"

  # ① と ② を並列実行
  (cd "$VAULT_DIR" && python3 06_開発/scripts/audit_mobile_sync.py 2>&1 | tail -15) > "$AUDIT_OUT" &
  AUDIT_PID=$!
  (cd "$VAULT_DIR" && python3 06_開発/scripts/lint_lp_internal_terms.py 2>&1 | tail -30) > "$LINT_OUT" &
  LINT_PID=$!

  wait $AUDIT_PID
  wait $LINT_PID

  AUDIT_OUTPUT=$(cat "$AUDIT_OUT")
  LINT_OUTPUT=$(cat "$LINT_OUT")
  rm -f "$AUDIT_OUT" "$LINT_OUT"

  jq -nc --arg ctx "🔍 LP 編集検出（${FILE_PATH}）→ 機械チェック自動実行：

═══════════════════════════════════════════════
① audit_mobile_sync.py（mobile.css 同期）
═══════════════════════════════════════════════
${AUDIT_OUTPUT}

═══════════════════════════════════════════════
② lint_lp_internal_terms.py（LP 社内用語ゼロ原則）
═══════════════════════════════════════════════
${LINT_OUTPUT}

⚠️ HIGH/MEDIUM 指摘あれば mobile.css 更新 / LP 社内用語の定性化を検討してください。
SSOT: 09_会社OS/公開/ガイドライン/design.md §LP 社内用語ゼロ原則" \
    '{hookSpecificOutput: {hookEventName: "PostToolUse", additionalContext: $ctx}}'
fi
