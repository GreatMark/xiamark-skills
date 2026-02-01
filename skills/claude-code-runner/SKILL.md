---
name: claude-code-runner
description: 快速调用 Claude Code 执行编程任务。支持一键运行、进度监控、结果获取。用于代码生成、项目构建、PR 审查、重构等任务。触发词：claude code、cc、让 claude 写、让 claude 做。
metadata:
  author: greatmark
  version: "1.0"
  requires:
    bins: ["claude"]
---

# Claude Code Runner

快速调用 Claude Code 的 OpenClaw 技能。

## 快速使用

### 1. 一键执行任务

```bash
# 基础模式（需要确认）
claude "你的任务描述"

# 全自动模式（sandbox 内自动确认）
claude --dangerously-auto-accept-permissions "你的任务描述"

# YOLO 模式（无 sandbox，无确认，最快最危险）
claude --dangerously-auto-accept-permissions --no-sandbox "你的任务描述"
```

### 2. 在后台运行（推荐）

```bash
# 后台启动，返回 sessionId
exec background:true workdir:/path/to/project command:"claude --dangerously-auto-accept-permissions '任务描述'"

# 查看进度
process action:log sessionId:xxx

# 检查是否完成
process action:poll sessionId:xxx
```

### 3. 指定工作目录

```bash
# 在特定项目目录执行
exec workdir:~/Projects/my-project command:"claude '在这个项目里添加登录功能'"
```

## 常用场景

### 代码生成
```bash
claude "写一个 Python 脚本，读取 CSV 文件并生成统计报告"
```

### 项目构建
```bash
claude --dangerously-auto-accept-permissions "创建一个 React + TypeScript 项目，包含用户登录功能"
```

### Bug 修复
```bash
claude "修复 src/utils.py 中的空指针异常"
```

### 代码审查
```bash
claude "Review 这个项目的代码质量，给出改进建议"
```

### PR 审查
```bash
claude "Review PR #123，分析代码变更并给出评审意见"
```

## 高级用法

### 并行执行多个任务
```bash
# 同时启动多个 Claude Code 实例
exec background:true workdir:~/project1 command:"claude '任务1'"
exec background:true workdir:~/project2 command:"claude '任务2'"

# 查看所有运行中的任务
process action:list
```

### 交互式会话（需要 tmux）
```bash
# 创建 tmux 会话
tmux new-session -d -s claude-session

# 在 tmux 中启动 Claude Code
tmux send-keys -t claude-session "cd ~/project && claude" Enter

# 发送任务
tmux send-keys -t claude-session "帮我重构这个模块" Enter

# 查看输出
tmux capture-pane -t claude-session -p
```

## 注意事项

1. **工作目录很重要** - 始终指定正确的 workdir，避免 Claude Code 读取无关文件
2. **不要在 ~/clawd 目录运行** - 这是 OpenClaw 的工作目录，会干扰
3. **后台模式更安全** - 可以随时查看进度和终止
4. **YOLO 模式谨慎使用** - 它会直接执行命令，没有任何确认

## 模式对比

| 模式 | 命令 | 安全性 | 速度 | 适用场景 |
|------|------|--------|------|----------|
| 普通 | `claude "..."` | ✅ 高 | 慢 | 敏感操作 |
| 全自动 | `claude --dangerously-auto-accept-permissions "..."` | ⚠️ 中 | 快 | 日常开发 |
| YOLO | `claude --dangerously-auto-accept-permissions --no-sandbox "..."` | ❌ 低 | 最快 | 信任的环境 |

## 检查 Claude Code 是否可用

```bash
which claude && claude --version
```

## 常见问题

### Q: Claude Code 没响应？
```bash
# 检查进程状态
process action:poll sessionId:xxx

# 查看最近输出
process action:log sessionId:xxx limit:50
```

### Q: 如何终止任务？
```bash
process action:kill sessionId:xxx
```

### Q: 如何查看所有运行中的任务？
```bash
process action:list
```
