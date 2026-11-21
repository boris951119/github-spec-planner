# 项目规格说明书（spec.md）

> 版本：{{VERSION}}
> 生成日期：{{GENERATED_AT}}
> 输入：`00-research/analysis.md`、`01-spec/sources.md`
> 调研口径：{{WINDOW_BASIS}}；关键词：{{KEYWORDS}}
> 规则：每条需求/板块必须有来源 ID；推断标 `[假设]` 并指向 sources.md。

## 1. 项目目标与背景

{{GOAL}}
- 目标用户：{{TARGET_USERS}} [{{SOURCE_IDS}}]
- 问题陈述：{{PROBLEM}} [{{SOURCE_IDS}}]

## 2. 竞品洞察摘要

| 项目 | 关键结论 | 来源 |
| --- | --- | --- |
| {{REPO_1}} | {{INSIGHT_1}} | {{SOURCE_IDS_1}} |

## 3. 范围

### In scope
{{IN_SCOPE}}

### Out of scope
| 不做的事 | 理由 | 来源/依据 |
| --- | --- | --- |
| {{OUT_1}} | {{REASON_1}} | {{SOURCE_IDS_1}} |

## 4. 功能需求

| ID | 需求描述 | 优先级 | 来源 | 验收标准 | 关联测试 |
| --- | --- | --- | --- | --- | --- |
| REQ-001 | {{REQ_TEXT_1}} | P0 | {{SOURCE_IDS_1}} | {{ACCEPTANCE_1}} | TEST-FUNC-001 |
| REQ-002 | {{REQ_TEXT_2}} | P1 | {{SOURCE_IDS_2}} | {{ACCEPTANCE_2}} | TEST-BND-001 |

## 5. 非功能需求

| ID | 类别 | 指标 | 来源 | 验收方式 | 关联测试 |
| --- | --- | --- | --- | --- | --- |
| REQ-NFR-001 | 性能 | {{METRIC_1}} | {{SOURCE_IDS_1}} | {{MEASURE_1}} | TEST-PERF-001 |
| REQ-NFR-002 | 安全 | {{METRIC_2}} | {{SOURCE_IDS_2}} | {{MEASURE_2}} | TEST-SEC-001 |

## 6. 用户与关键场景

{{SCENARIOS}}

## 7. 领域模型与术语

{{DOMAIN_MODEL}}

## 8. 板块划分

| ID | 板块名称 | 职责 | 覆盖需求 | 依赖板块 | 来源 |
| --- | --- | --- | --- | --- | --- |
| MOD-01 | {{MOD_NAME_1}} | {{MOD_DUTY_1}} | REQ-001 | 无 | {{SOURCE_IDS_1}} |
| MOD-02 | {{MOD_NAME_2}} | {{MOD_DUTY_2}} | REQ-002 | MOD-01 | {{SOURCE_IDS_2}} |

### MOD-01 {{MOD_NAME_1}}

- 职责：{{MOD_DUTY_1}}
- 覆盖需求：[REQ-001]
- 输入：{{MOD_INPUT_1}}；输出：{{MOD_OUTPUT_1}}
- 依赖：{{MOD_DEPS_1}}
- 不含：{{MOD_EXCLUDES_1}}
- 来源：{{SOURCE_IDS_1}}

## 9. 约束与依赖

{{CONSTRAINTS}}

## 10. 风险与开放问题

{{RISKS}}

## 11. 来源索引

{{SOURCE_INDEX}}
