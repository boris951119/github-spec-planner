# 执行计划（plan.md）

> 版本：{{VERSION}}
> 生成日期：{{GENERATED_AT}}
> 输入：`01-spec/spec.md`（版本 {{SPEC_VERSION}}）、`02-plan/decisions.md`
> 规则：任务必须追溯到 MOD/REQ；估算标依据；不得留占位符。

## 1. 输入与依据

{{INPUTS}}

## 2. 技术栈总览

| 层级 | 选型 | 决策 ID | 依据来源 |
| --- | --- | --- | --- |
| 前端 | {{FRONTEND}} | DEC-001 | {{SOURCE_IDS_1}} |
| 后端 | {{BACKEND}} | DEC-002 | {{SOURCE_IDS_2}} |
| 数据存储 | {{STORAGE}} | DEC-003 | {{SOURCE_IDS_3}} |
| 基础设施 | {{INFRA}} | DEC-004 | {{SOURCE_IDS_4}} |
| 测试 | {{TEST_STACK}} | DEC-005 | {{SOURCE_IDS_5}} |

## 3. 阶段划分

| 阶段 | 目标 | 覆盖板块 | 任务 | 出口条件 | 人日 | 主要风险 |
| --- | --- | --- | --- | --- | --- | --- |
| P0 验证与骨架 | {{GOAL_0}} | {{MODS_0}} | TASK-001 | {{EXIT_0}} | {{DAYS_0}} | {{RISK_0}} |
| P1 核心闭环 | {{GOAL_1}} | {{MODS_1}} | TASK-002 | {{EXIT_1}} | {{DAYS_1}} | {{RISK_1}} |
| P2 支撑能力 | {{GOAL_2}} | {{MODS_2}} | TASK-003 | {{EXIT_2}} | {{DAYS_2}} | {{RISK_2}} |
| P3 质量与交付 | {{GOAL_3}} | 全部 | TASK-004 | {{EXIT_3}} | {{DAYS_3}} | {{RISK_3}} |

## 4. 任务明细

### TASK-001 {{TASK_NAME_1}}

- 覆盖：[MOD-01, REQ-001]
- 阶段：P0
- 产出：{{DELIVERABLE_1}}
- 完成定义（DoD）：{{DOD_1}}
- 依赖任务：无
- 估算：{{ESTIMATE_1}}（{{ESTIMATE_BASIS_1}}）
- 验证方式：TEST-FUNC-001；TEST-BND-001

### TASK-002 {{TASK_NAME_2}}

- 覆盖：[MOD-02, REQ-002]
- 阶段：P1
- 产出：{{DELIVERABLE_2}}
- 完成定义（DoD）：{{DOD_2}}
- 依赖任务：TASK-001
- 估算：{{ESTIMATE_2}}（{{ESTIMATE_BASIS_2}}）
- 验证方式：TEST-FUNC-002

## 5. 依赖关系与关键路径

{{CRITICAL_PATH}}

## 6. 里程碑与验收门禁

{{MILESTONES}}

## 7. 风险与缓解

{{RISKS}}

## 8. 需求 → 测试 → 阶段对应表

| 需求 | 测试用例 | 执行阶段 |
| --- | --- | --- |
| REQ-001 | TEST-FUNC-001, TEST-BND-001 | P1 |
| REQ-002 | TEST-FUNC-002 | P1 |

## 9. 复现与审计

- 调研命令：`{{REPRODUCE_COMMAND}}`
- 校验命令：`python3 scripts/validate_docs.py --docs-dir docs --report docs/validation_report.md`
