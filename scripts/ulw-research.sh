#!/bin/bash
set -euo pipefail

# ulw-research.sh
# 用法：bash scripts/ulw-research.sh "你的主题" [outdir]

TOPIC="${1:-}"
OUTDIR="${2:-/tmp/ulw-research-$(date +%Y%m%d%H%M%S)}"

if [[ -z "$TOPIC" ]]; then
  echo "Usage: $0 <topic> [outdir]" >&2
  exit 1
fi

SERPER_KEY="${SERPER_API_KEY:-d06b3a1ff63d5d18d1b828e49743a75b26e3795d}"
mkdir -p "$OUTDIR"

# 一个轻量 query 生成器：中英各 12 条 = 24 轮（你要 50 轮时可以扩展）
QUERIES=(
  "$TOPIC 2026 对比"
  "$TOPIC 开源 商用 授权"
  "$TOPIC 批量处理 自动化"
  "$TOPIC 中国可用性"
  "$TOPIC 价格 订阅 API"
  "$TOPIC 最佳实践 工作流"
  "best $TOPIC tools 2026"
  "$TOPIC commercial license terms"
  "$TOPIC batch processing automation"
  "$TOPIC pricing API"
  "$TOPIC China availability"
  "$TOPIC workflow best practices"
)

ALL="$OUTDIR/all_snippets.txt"
: > "$ALL"

i=0
for q in "${QUERIES[@]}"; do
  i=$((i+1))
  echo "[$i/${#QUERIES[@]}] $q" >&2

  if [[ "$q" =~ [一-龥] ]]; then
    body=$(jq -nc --arg q "$q" '{q:$q, gl:"cn", hl:"zh-cn", num:10}')
  else
    body=$(jq -nc --arg q "$q" '{q:$q, num:10}')
  fi

  curl -s -X POST 'https://google.serper.dev/search' \
    -H "X-API-KEY: $SERPER_KEY" \
    -H 'Content-Type: application/json' \
    -d "$body" > "$OUTDIR/search_$i.json"

  jq -r '.organic[:5] | .[] | "- \(.title)\n  \(.link)\n  \(.snippet)\n"' "$OUTDIR/search_$i.json" >> "$ALL"
  echo "" >> "$ALL"
  sleep 0.3

done

echo "DONE: $OUTDIR" >&2
echo "$ALL"
