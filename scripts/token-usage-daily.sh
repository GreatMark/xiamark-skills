#!/bin/bash
# 每日 Token 使用统计脚本 (v2 - 统计所有 sessions)

SESSIONS_DIR="$HOME/.openclaw/agents/main/sessions"
USAGE_LOG="$HOME/clawd/memory/token-usage-log.json"
TODAY=$(date +%Y-%m-%d)

# 从 sessions.json 获取所有 session 的 token 总和
CURRENT=$(cat "$SESSIONS_DIR/sessions.json" 2>/dev/null | jq '[to_entries | .[].value.totalTokens // 0] | add // 0')

# 初始化或读取历史记录
if [ ! -f "$USAGE_LOG" ]; then
    echo '{"history":[]}' > "$USAGE_LOG"
fi

# 添加今天的记录
jq --arg date "$TODAY" --argjson tokens "$CURRENT" \
   '.history += [{"date": $date, "totalTokens": $tokens, "timestamp": now}] | .history = (.history | unique_by(.date) | sort_by(.date) | .[-30:])' \
   "$USAGE_LOG" > "${USAGE_LOG}.tmp" && mv "${USAGE_LOG}.tmp" "$USAGE_LOG"

# 格式化数字（加逗号）
format_num() {
    printf "%'d" $1
}

# 输出汇总
echo "📊 OpenClaw Token 使用统计 - $TODAY"
echo "---"
echo "今日累计: $(format_num $CURRENT) tokens"
echo ""

# 按 session 明细
echo "Session 明细:"
cat "$SESSIONS_DIR/sessions.json" 2>/dev/null | jq -r 'to_entries | .[] | select(.value.totalTokens != null) | "  \(.key | split(":") | .[-1]): \(.value.totalTokens) tokens (\(.value.model // "unknown"))"'
echo ""

echo "最近7天记录:"
jq -r '.history[-7:] | .[] | "  \(.date): \(.totalTokens) tokens"' "$USAGE_LOG" 2>/dev/null
