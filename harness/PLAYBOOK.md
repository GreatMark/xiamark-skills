# PLAYBOOK (Sisyphus-lite)

## 0) 先定义 Done
- 一句话：什么叫完成
- 验收：能否复制粘贴执行？能否拿去给团队/供应商？

## 1) 拆解
- 主任务 → 子任务 3~6 个
- 每个子任务：输入、输出、约束、截止

## 2) 并行执行（sessions_spawn）
- 每个子任务用一个角色模板
- 强制结构化输出（便于 merge）

## 3) 整合
- 去重
- 标注不确定性
- 给出推荐与 next actions

## 4) 产物落盘
- `reports/YYYY-MM-DD-<topic>.md`
- 如涉及脚本/配置：写入 `scripts/` 或 `configs/`

## 5) 防烂尾机制
- 输出末尾必须包含：
  - Next actions (1~5)
  - Open questions (0~3)
  - Owner（我/你/外部）
