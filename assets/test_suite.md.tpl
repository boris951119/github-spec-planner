# 多维度交付测试集

> 版本：{{VERSION}}
> 生成日期：{{GENERATED_AT}}
> 对应 spec：{{SPEC_VERSION}}；对应 plan：{{PLAN_VERSION}}
> 机器可读版本：`03-tests/test_cases.csv`

## 1. 覆盖统计

- 功能需求总数：{{REQ_TOTAL}}
- 已覆盖需求：{{REQ_COVERED}}
- 未覆盖需求及理由：{{REQ_UNCOVERED}}

## 2. 维度覆盖矩阵

| 需求 | 功能 | 边界 | 异常 | 性能 | 安全 | 兼容 | 数据一致性 | 可访问性 | 回归 | 验收 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| REQ-001 | TEST-FUNC-001 | TEST-BND-001 | TEST-ERR-001 | N/A(无量化指标) | TEST-SEC-001 | TEST-COMP-001 | TEST-DATA-001 | N/A(无界面) | N/A | TEST-ACC-001 |
| REQ-002 | TEST-FUNC-002 | N/A(理由) | TEST-ERR-002 | TEST-PERF-001 | N/A(理由) | N/A(理由) | N/A(理由) | N/A(理由) | N/A(理由) | TEST-ACC-002 |

## 3. 用例明细

| ID | 维度 | 关联需求 | 前置条件 | 步骤 | 预期结果 | 来源 | 优先级 | 自动化 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TEST-FUNC-001 | 功能 | REQ-001 | {{PRECOND_1}} | {{STEPS_1}} | {{EXPECTED_1}} | {{SOURCE_IDS_1}} | P0 | yes |
| TEST-BND-001 | 边界 | REQ-001 | {{PRECOND_2}} | {{STEPS_2}} | {{EXPECTED_2}} | {{SOURCE_IDS_2}} | P1 | yes |

## 4. 执行策略

- 框架：{{TEST_FRAMEWORK}}（依据 DEC-005）
- 环境：{{ENVIRONMENT}}
- 测试数据：{{FIXTURES}}
- 执行顺序：{{ORDER}}

## 5. 发布门禁

- P0 用例通过率：100%
- P1 用例通过率：≥95%
- 未通过项必须登记风险接受记录：{{RISK_ACCEPTANCE}}

## 6. 可复用资产与来源

{{REUSABLE_ASSETS}}
