# 溯源契约（Traceability Contract）

本文件定义所有交付文档必须遵守的 ID 体系、引用格式与校验规则。`scripts/validate_docs.py` 按此规则自动校验。

## 1. ID 体系

| 前缀 | 含义 | 定义位置 | 必须引用 |
| --- | --- | --- | --- |
| `SRC-XXX-NNN` | 来源条目 | `01-spec/sources.md`、JSON `source_registry` | URL + 抓取时间 + 级别 |
| `OBS-XXX` | 调研观察/结论 | `00-research/analysis.md` | ≥1 个 SRC |
| `REQ-XXX` | spec 中的需求 | `01-spec/spec.md` | ≥1 个 SRC 或 OBS |
| `MOD-XXX` | 板块/模块 | `01-spec/spec.md` 的板块划分章节 | ≥1 个 REQ |
| `DEC-XXX` | 技术栈/架构决策 | `02-plan/decisions.md` | ≥1 个 SRC 或 OBS，且含备选方案 |
| `TASK-XXX` | 执行任务 | `02-plan/plan.md` | ≥1 个 MOD 或 REQ |
| `TEST-XXX` | 测试用例 | `03-tests/test_suite.md` 与 `test_cases.csv` | ≥1 个 REQ |

编号建议：`REQ-001`、`MOD-01`、`TEST-FUNC-001`。脚本识别 `前缀-字母数字` 形式。

## 2. 定义与引用的写法（供校验器识别）

**定义**（三种形式之一，行首）：

```markdown
| REQ-001 | 用户可创建任务 | ... | [SRC-GH-001] |
- **REQ-001**: 用户可创建任务 ... [SRC-GH-001]
### REQ-001 用户可创建任务
```

**引用**：方括号形式 `[SRC-GH-001]`、`[REQ-001, MOD-02]`，或表格「来源 / 依据 / 关联」列中的裸 ID。

每个定义块的正文从其定义行延续到下一个定义行或二级标题；校验器在该块内查找引用。因此**不要把需求定义和它的来源放在不同章节**。

## 3. `sources.md` 必需结构

```markdown
# 来源台账

## 来源级别
A = GitHub API / 官方页面；B = 仓库原始文件；C = 搜索片段（仅线索）

## 假设与口径
- 时间窗口口径：created（近 6 个月新建），理由：...
- 关键词：...
- 未验证推断：...（若无写「无」）

## 来源清单
| ID | 级别 | URL | 抓取时间 | 用途 |  Supports |
| --- | --- | --- | --- | --- | --- |
| SRC-GH-001 | A | https://api.github.com/repos/... | 2026-11-21T...Z | stars/created_at | REQ-001, REQ-002 |
```

反向列 `Supports` 记录该来源支撑的下游 ID，便于双向审计。

## 4. 需求卡片格式

```markdown
| ID | 需求描述 | 优先级 | 来源 | 验收标准 | 关联测试 |
| --- | --- | --- | --- | --- | --- |
| REQ-001 | 用户可创建带标题的任务 | P0 | [SRC-GH-001, OBS-003] | 给定标题，创建后列表中可见 | TEST-FUNC-001 |
```

- 需求描述必须是可验证的陈述句，避免「友好的」「高性能的」这类无验收标准的表述。
- 非功能性需求同样要有来源与量化指标（如 `p95 < 300ms`，来源为竞品 benchmark 或用户约束）。
- 由推断产生的需求写 `[假设]`，并指向 `sources.md` 中的假设条目。

## 5. 决策记录格式（ADR-lite）

```markdown
### DEC-001 前端框架选型
- 决策：React 19 + Vite
- 依据：[SRC-GH-002, OBS-011]（Top 5 中 3 个采用 React，社区规模最大）
- 备选方案：Vue 3（[SRC-GH-004]，生态规模较小）、Svelte（[SRC-GH-005]，团队经验不足）
- 代价：需要额外状态管理库
- 影响任务：TASK-002, TASK-005
```

## 6. 测试用例格式

Markdown 矩阵与 CSV 必须一一对应。CSV 表头固定为：

```
test_id, dimension, related_req, preconditions, steps, expected, source_ids, priority, automated
```

- `dimension` 取值见 `testing_guide.md`。
- `related_req` 至少填一个 REQ ID；`source_ids` 至少填一个 SRC/OBS ID。
- `steps` 用 `；` 分隔多个步骤；`expected` 必须为可判定结果。
- `automated` 为 `yes` / `no`。

## 7. 校验命令

```bash
python3 scripts/validate_docs.py --docs-dir docs --report docs/validation_report.md
python3 scripts/validate_docs.py --docs-dir docs --check-links   # 追加链接可达性检查
```

失败项必须修复后重跑；`--check-links` 的网络类失败可记录为已知风险，但需在报告说明。

## 8. 「可复用」要求

- 输出目录结构与文件名保持固定，便于跨项目对比与工具复用。
- JSON 保留 `schema_version` 与 `reproduce_command`。
- 所有文档保留生成日期与所用关键词/口径。
- 模板从 `assets/` 复制，不凭记忆重写字段。
