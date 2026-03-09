# References — openclaw-claude-hooks

## 1) win4r/claude-code-hooks

Repo: https://github.com/win4r/claude-code-hooks

### 提炼出的关键模式

- `dispatch-claude-code.sh`：一次派发 Claude Code 任务
- `claude_code_run.py`：在需要 PTY / Agent Teams 时提供更稳的运行包装
- `hooks/notify-agi.sh`：在 `Stop` / `SessionEnd` 触发回调
- `latest.json`：结果持久化
- `pending-wake.json`：用于唤醒主 AGI / OpenClaw

### 从源码里值得吸收的点

- Hook 读 stdin payload 拿 `session_id`、`cwd`、事件名
- 同时注册 `Stop` 和 `SessionEnd`，并做重复触发保护
- 输出先落盘，再走通知/唤醒链路
- Agent Teams 通过环境变量和 teammate mode 启用

### 需要升级的地方

- demo 结构偏单任务，固定 `latest.json` / `task-meta.json` 容易被并发覆盖
- 更适合升级为“每任务一个目录”的结果存储模式
- OpenClaw 新环境里优先使用 wake/system event，不建议回到高频轮询

---

## 2) OpenClaw-Agent-Teams 文章

Article: https://www.aivi.fyi/aiagents/OpenClaw-Agent-Teams

### 提炼出的关键观点

- OpenClaw 高频轮询 Claude Code 会浪费大量 token
- `latest.json` 是**数据通道**：完整结果不丢
- wake event 是**信号通道**：让 OpenClaw 秒级响应
- 两者结合比“只发消息”或“只写文件”更稳
- Agent Teams 能把复杂任务拆给多个 Claude 子代理协作

### 文章里的原始心法

> Dispatch 的核心思想：发射后不管，完成自动回报。

这句非常值得固化进 skill。

---

## 3) 适合固化成 skill 的最终经验

1. **长任务异步化**：只派发一次，不做紧轮询
2. **结果持久化**：完整输出写文件，不依赖消息体长度
3. **立即唤醒**：任务完成后发 wake，而不是等 heartbeat
4. **双 hook 去重**：Stop + SessionEnd 同时注册，但只处理一次
5. **任务隔离**：结果按 task/session 分目录，不要全局单文件硬覆盖
6. **Agent Teams 节制使用**：重任务再开，不要默认滥用
7. **主会话只做调度和回收**：不要让主聊天一直盯日志
