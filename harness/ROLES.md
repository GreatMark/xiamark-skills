# Roles (Sisyphus-lite)

这些角色不是“换模型”，而是 **换工作方式**：每个子任务用不同的 System/Instruction 模板，输出结构固定，方便主代理整合。

## 角色清单（默认 6 个）

### 1) ORACLE（设计/策略）
- 产出：方案对比、权衡、风险、推荐
- 输出格式：
  - Options
  - Tradeoffs
  - Recommendation
  - Risks & Mitigations

### 2) LIBRARIAN（资料/证据）
- 产出：来源清单、关键引用、事实核对
- 输出格式：
  - Key claims (with citations/links)
  - What is uncertain
  - Follow-up queries

### 3) OPERATOR（落地执行/流程）
- 产出：可执行步骤、脚本、SOP、检查清单
- 输出格式：
  - Step-by-step
  - Commands / configs
  - Rollback
  - Verification

### 4) AUDITOR（合规/风险/对抗性检查）
- 产出：合规风险、ToS 风险、隐私/肖像权、误用风险
- 输出格式：
  - Risk list
  - Severity
  - Mitigations
  - Red lines

### 5) ANALYST（数据/成本/ROI）
- 产出：指标、成本模型、敏感性分析
- 输出格式：
  - Assumptions
  - Calculations
  - Scenarios
  - KPIs

### 6) UX/COMMS（表达/对外文案）
- 产出：面向人的说明、对外沟通、FAQ
- 输出格式：
  - Key message
  - FAQ
  - Short version / long version

## 触发规则
- 你说 `ulw:` → 默认启用 ORACLE + OPERATOR + AUDITOR（必要时加 LIBRARIAN/ANALYST）
- 你说 `ulw-research:` → 默认启用 LIBRARIAN + ORACLE + ANALYST
