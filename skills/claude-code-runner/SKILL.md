---
name: claude-code-runner
description: 快速调用 Claude Code 执行编程任务。支持一键运行、进度监控、结果获取。用于代码生成、项目构建、PR 审查、重构等任务。触发词：claude code、cc、让 claude 写、让 claude 做。
metadata:
  author: greatmark
  version: "2.0"
  requires:
    bins: ["claude"]
---

# Claude Code Runner v2.0 — 零轮询模式

## 🔥 核心原则：零轮询，Hook 回调

**永远不要轮询 Claude Code！** 用 dispatch + Stop Hook 模式：
1. OpenClaw 派发任务（一次 exec）
2. Claude Code 后台独立运行
3. 完成后 Stop Hook 自动写 latest.json + wake OpenClaw
4. OpenClaw 读结果、推飞书

Token 消耗：从暴涨 → 几乎忽略不计。

## 快速使用

### 方式一：dispatch 脚本（推荐）

```bash
# 基础任务
exec command:"bash ~/.openclaw/workspace/scripts/claude-dispatch/dispatch-claude.sh \
  -p '实现一个 Python 爬虫' \
  -n 'my-scraper' \
  -w /path/to/project"

# Agent Teams 多智能体协作
exec command:"bash ~/.openclaw/workspace/scripts/claude-dispatch/dispatch-claude.sh \
  -p '重构整个项目的测试框架' \
  -n 'test-refactor' \
  -w /path/to/project \
  --agent-teams"
```

dispatch 后立即返回，不阻塞。Claude Code 完成后 Hook 自动 wake OpenClaw。

### 方式二：直接 exec（简单任务）

```bash
# 后台启动，输出重定向
exec background:true workdir:/path/to/project \
  command:"claude --permission-mode bypassPermissions -p '任务描述' > /tmp/cc-output.txt 2>&1"
```

注意：这种方式需要手动 poll，不推荐长任务。

## Hook 架构

```
dispatch-claude.sh
  │
  ├─ 写入 task-meta.json（任务名、时间戳）
  ├─ nohup 启动 Claude Code（后台运行）
  │   └─ 输出写入 task-output.txt
  │
  └─ Claude Code 完成 → Stop Hook 自动触发
      │
      ├─ notify-openclaw.sh 执行：
      │   ├─ 读取 task-meta.json + 输出
      │   ├─ 写入 latest.json（完整结果）
      │   └─ curl wake API → OpenClaw 秒级响应
      │
      └─ OpenClaw 读取 latest.json → 推飞书
```

## 文件位置

| 文件 | 路径 | 作用 |
|------|------|------|
| dispatch 脚本 | `~/.openclaw/workspace/scripts/claude-dispatch/dispatch-claude.sh` | 一键派发 |
| Hook 脚本 | `~/.openclaw/workspace/scripts/claude-dispatch/notify-openclaw.sh` | Stop 回调 |
| 任务元数据 | `~/.openclaw/workspace/data/claude-code-results/task-meta.json` | 任务信息 |
| 任务输出 | `~/.openclaw/workspace/data/claude-code-results/task-output.txt` | 完整输出 |
| 结果 JSON | `~/.openclaw/workspace/data/claude-code-results/latest.json` | Hook 写入 |

## dispatch 参数

| 参数 | 说明 |
|------|------|
| `-p, --prompt` | 任务提示（必需）|
| `-n, --name` | 任务名称（用于跟踪）|
| `-w, --workdir` | 工作目录 |
| `--agent-teams` | 启用 Agent Teams 多智能体 |
| `--permission-mode` | 权限模式（默认 bypassPermissions）|
| `--model` | 指定模型 |

## 处理 Wake Event

当收到 wake event（"Claude Code 任务 [xxx] 已完成"），执行：

```bash
# 读取结果
cat ~/.openclaw/workspace/data/claude-code-results/latest.json

# 读取详细输出
cat ~/.openclaw/workspace/data/claude-code-results/task-output.txt
```

然后将结果摘要推送到飞书。

## 注意事项

1. **不要在 ~/.openclaw/workspace 目录运行 Claude Code** — 会干扰
2. **Stop Hook 有 30 秒去重** — 避免 Stop + SessionEnd 双触发
3. **串行执行** — 不要并行跑多个 Claude Code（会 SIGKILL）
4. **Agent Teams 需要 Opus 4.6** — 确保有模型访问权限
