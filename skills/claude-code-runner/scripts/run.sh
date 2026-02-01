#!/bin/bash
# Claude Code 快速运行脚本
# 用法: ./run.sh "任务描述" [工作目录] [模式]
# 模式: normal, auto, yolo

TASK="$1"
WORKDIR="${2:-$(pwd)}"
MODE="${3:-auto}"

if [ -z "$TASK" ]; then
    echo "用法: ./run.sh \"任务描述\" [工作目录] [模式]"
    echo "模式: normal, auto, yolo"
    exit 1
fi

cd "$WORKDIR" || exit 1

case "$MODE" in
    normal)
        claude "$TASK"
        ;;
    auto)
        claude --dangerously-auto-accept-permissions "$TASK"
        ;;
    yolo)
        claude --dangerously-auto-accept-permissions --no-sandbox "$TASK"
        ;;
    *)
        echo "未知模式: $MODE (可选: normal, auto, yolo)"
        exit 1
        ;;
esac
