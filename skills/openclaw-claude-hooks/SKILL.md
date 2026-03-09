---
name: openclaw-claude-hooks
description: 用 Claude Code Hooks + 结果持久化 + wake event，把 OpenClaw 对 Claude Code 的长任务派发改成零轮询异步回调。适用于后台编码、长任务、Agent Teams、多任务异步收敛。触发词：claude hooks、Stop Hook、SessionEnd、零轮询、Agent Teams、dispatch Claude Code、回调、wake event。
metadata:
  author: greatmark
  version: "1.0"
  sources:
    - https://github.com/win4r/claude-code-hooks
    - https://www.aivi.fyi/aiagents/OpenClaw-Agent-Teams
  requires:
    bins: ["claude", "openclaw", "python3"]
---

# OpenClaw Claude Code Hooks

## 核心结论

**不要用 OpenClaw 高频轮询 Claude Code 长任务。**

更省 token、更稳的方式是：

1. OpenClaw 只负责一次派发
2. Claude Code 在后台独立执行
3. Claude Hook 在 `Stop` / `SessionEnd` 时写结果文件
4. Hook 再发一个短 wake signal 把 OpenClaw 叫醒
5. OpenClaw 醒来后读结果文件并总结给用户

一句话：

> **signal 和 data 分离：wake event 只负责“叫醒”，结果文件负责“存全量数据”。**

---

## 什么时候激活

当用户要你：

- 用 OpenClaw 派发 **Claude Code 长任务**
- 做 **后台异步编码**，不想堵主会话
- 做 **零轮询 / 少 token** 的 Claude Code 集成
- 使用 **Claude Code Hooks**、`Stop Hook`、`SessionEnd Hook`
- 用 **Agent Teams** 做并行协作开发
- 让 Claude Code 完成后 **自动通知 / 自动唤醒 OpenClaw**

如果只是一次性小修小补，直接用常规 `claude --permission-mode bypassPermissions --print` 即可，不需要上 hooks 架构。

---

## 默认工作流

### 1）派发前判断

如果任务满足下面任一条件，优先用 hooks 模式：

- 预计运行 > 1~2 分钟
- 可能要跑测试 / 构建 / 多文件改动
- 任务完成后才需要回收结果
- 用户不想看持续日志
- 想启用 Agent Teams

### 2）一次派发，不做紧轮询

优先把 prompt 整理完整后，一次交给 Claude Code：

```bash
claude --permission-mode bypassPermissions --print '你的任务'
```

要点：

- **Claude Code 默认优先用 `--print` + `--permission-mode bypassPermissions`**
- 不要靠高频 `process log/poll` 盯进度
- 真要监控，也只做低频、按需查看，不做秒级轮询

### 3）结果持久化

Hook 触发后，把结果写到文件，而不是只发消息。

推荐目录：

```text
~/.openclaw/claude-hooks/
  runs/
    <task-id>/
      meta.json
      output.txt
      result.json
      hook.log
```

其中：

- `meta.json`：任务名、工作目录、开始时间、模型、session 信息
- `output.txt`：Claude Code 原始输出
- `result.json`：给 OpenClaw 回收用的结构化结果
- `hook.log`：hook 运行记录

### 4）wake 只发短消息

Hook 完成后，发送一个短 wake signal：

```bash
openclaw system event --text "Claude Code 任务完成：<task-name>。请读取 <result.json>" --mode now
```

或者调 gateway wake API。原则不变：

- **wake text 只负责通知，不承载大段结果**
- **完整输出始终放文件**

### 5）OpenClaw 醒来后再读结果

收到 wake 后：

1. 读取 `result.json`
2. 必要时补读 `output.txt`
3. 给用户发简报：
   - 已完成什么
   - 结果路径
   - 关键改动 / 测试情况
   - 是否还有阻塞

---

## 与来源方案对齐后的最佳实践

`win4r/claude-code-hooks` 和文章里的核心思路是对的：

- Claude Code 后台跑
- Hook 回调
- latest.json 持久化
- wake event 秒级唤醒
- 可配 Agent Teams

但在真正长期使用时，建议做这几个升级：

### A. 不要只用单个 `latest.json`

Demo 用单文件很直观，但 **并发任务会互相覆盖**。

更稳做法：

- 每个任务一个目录
- 用 `task-id` / `session-id` 作为主键
- `latest.json` 只当“最近一次索引”，不要当唯一结果存储

### B. Stop / SessionEnd 要做去重

Claude Hook 可能在 `Stop` 和 `SessionEnd` 都触发一次。

必须做：

- 锁文件去重
- 或按 `session_id + 最近 N 秒` 去重

### C. signal / data 双通道

这是这套架构最关键的点：

- `result.json` = **数据通道**
- wake event = **信号通道**

不要把它们混成一个东西。

### D. 不要在 OpenClaw 工作区里直接跑 Claude Code

避免 Claude Code 误读 agent 自身的工作区文件、心智文件、配置文件。

### E. Agent Teams 只在重任务启用

适用场景：

- 大功能开发
- 大范围重构
- 多模块并行改造
- 需要 lead + sub-agents 协作

不要对普通小修滥用 Agent Teams。

---

## 推荐执行模板

### 模板 1：后台单任务（无 Teams）

```bash
TASK_ID="cc-$(date +%Y%m%d-%H%M%S)"
TASK_ROOT="$HOME/.openclaw/claude-hooks/runs/$TASK_ID"
mkdir -p "$TASK_ROOT"

claude --permission-mode bypassPermissions --print "$PROMPT" \
  > "$TASK_ROOT/output.txt" 2>&1
```

Hook 写入：

```json
{
  "task_id": "cc-20260309-153000",
  "task_name": "fix-auth-bug",
  "status": "done",
  "cwd": "/path/to/project",
  "output_file": "/Users/you/.openclaw/claude-hooks/runs/cc-20260309-153000/output.txt",
  "completed_at": "2026-03-09T15:30:00+08:00"
}
```

### 模板 2：Agent Teams 重任务

当任务明显适合并行拆解时：

- 开启 Agent Teams 环境变量
- 仍然坚持“后台运行 + 文件持久化 + wake 回调”
- 不因为 Teams 就回到高频轮询

---

## Hook 配置要点

Claude Code 侧通常需要在 `~/.claude/settings.json` 注册：

```json
{
  "hooks": {
    "Stop": [{"hooks": [{"type": "command", "command": "~/.claude/hooks/notify-openclaw.sh", "timeout": 10}]}],
    "SessionEnd": [{"hooks": [{"type": "command", "command": "~/.claude/hooks/notify-openclaw.sh", "timeout": 10}]}]
  }
}
```

Hook 脚本职责：

1. 读 stdin 里的 hook payload
2. 找到对应任务目录
3. 读取输出文件
4. 写 `result.json`
5. 发 wake
6. 做去重

---

## 回收结果时的汇报格式

默认用这种简报：

1. 已接收/已派发什么任务
2. 当前状态（进行中 / 已完成 / 失败）
3. 结果文件路径
4. 关键产物 / 测试 / 阻塞

例如：

- 已派发 Claude Code 后台执行 `fix-auth-bug`
- 当前状态：已完成
- 结果路径：`~/.openclaw/claude-hooks/runs/cc-xxx/result.json`
- 测试：`pnpm test` 通过
- 产物：修改 `src/auth.ts`、`src/session.ts`

---

## 禁忌

### 不要这样做

- 不要每几秒轮询 Claude Code 输出
- 不要把完整结果塞进 wake text
- 不要只发 wake、不写结果文件
- 不要只写文件、不发 wake（除非接受 heartbeat 延迟）
- 不要把多个任务都写进同一个固定文件而不做隔离
- 不要在 `~/.openclaw/` 或 agent 自身工作区里直接跑 Claude Code 任务

---

## 适用判断

### 用这个 skill

- 用户说：
  - “让 Claude Code 后台跑”
  - “别轮询，省 token”
  - “任务完成自动通知我”
  - “用 hooks 回调”
  - “用 Agent Teams 异步开发”

### 不用这个 skill

- 只是查看文件
- 只是一次性小改
- 只是短命令执行
- 用户明确要实时前台流式输出

---

## 来源学习摘要

### `win4r/claude-code-hooks`
给了一个很清晰的最小闭环：

- dispatch 脚本
- Claude Code 运行器
- Stop/SessionEnd hook
- `latest.json`
- `pending-wake.json` / 通知

### `OpenClaw-Agent-Teams` 文章
把这个模式讲清楚了：

- 轮询浪费 token
- latest.json 负责“存全量结果”
- wake event 负责“即时叫醒”
- Agent Teams 可以把复杂任务并行化

这两个来源组合起来，形成了一个实用原则：

> **OpenClaw 负责调度与回收，Claude Code 负责长时间自主执行，Hooks 负责低成本回调。**
