#!/bin/bash
# Stop hook: セッション終了時に work-log 提案メッセージを UI に表示
# 260501 確立・work-log 更新忘れ防止

echo '{"systemMessage": "📝 セッション終了。本日の作業を記録するなら /work-log を実行してください"}'
