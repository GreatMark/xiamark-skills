# OpenClaw Harness (Sisyphus-lite)

目标：把 greatmark 变成“经理 + 专家团队”的协作框架，不仅写代码，也覆盖研究、决策、运营、电商自动化。

## 核心概念
- **主代理（greatmark / TL）**：负责澄清目标、拆解任务、分配子任务、整合输出、把关风险。
- **子代理（临时会话 / sessions_spawn）**：按角色提示词运行，产出结构化结果回传给主代理。
- **ulw 模式（ultrawork）**：一句触发词，自动进入“并行探索 + 强制完成”的工作方式。

> 注：当前 allowlist 仅允许 `agentId=main`，所以子代理用同一个 agent，但通过“角色系统提示词”模拟不同专家。

## 使用方式（建议）
### 1) 普通模式
直接问我。

### 2) ulw 模式（推荐）
你发：
- `ulw: <目标>`
我会自动：
1. 定义 Done
2. 并行派发 3~6 个角色子任务
3. 汇总成一份可执行交付物（并写入 reports/）

### 3) 深度研究（50轮搜索）
你发：
- `ulw-research: <主题>`
我会跑 `scripts/deep-research.sh`（或按主题生成 queries），再汇总。

## 文件
- `harness/ROLES.md`：角色说明与提示词模板
- `harness/PLAYBOOK.md`：工作流与输出标准
- `scripts/ulw-research.sh`：一键研究脚本（基于 Serper）
