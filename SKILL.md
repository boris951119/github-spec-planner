---
name: evidence-driven-project-planner
description: This skill should be used before starting a new software project, or when a user asks for a spec, an execution plan with justified tech-stack choices, a competitive open-source scan, or a delivery test suite. It researches the top 5 starred GitHub projects created within the last six months that match the idea, derives a source-traceable spec.md, splits it into modules, writes plan.md with technology decision records, and generates a multi-dimensional test suite. Every claim must be backed by a cited, verifiable, reusable source.
display_name: GitHub 开源调研项目规划
display_name_en: GitHub Spec Planner
description_zh: 项目开工前自动调研 GitHub 近半年 star 前 5 的同类开源项目，产出可溯源、可验证、可复用的 spec.md、plan.md 与多维度交付测试集。
description_en: Researches top-starred GitHub projects from the last six months and produces source-traceable spec, plan and multi-dimensional delivery test suite.
version: 1.2.0
author: WorkBuddy User
examples_zh:
  - 我要做一个【一句话描述】；给谁用：【】；解决什么问题：【】；核心功能：【2-3个】；典型场景：【】；不想要的：【可留空】；已定约束：【可留空】
  - 帮我规划一个任务管理应用，先调研同类开源项目再写 spec
  - 根据这个需求生成项目板块划分和执行计划
examples_en:
  - I want to build [one-line idea]; for [target users]; to solve [pain point]; core features [2-3]; a typical scenario []; exclusions [optional]; fixed constraints [optional]
  - Plan a task manager with GitHub open-source research first
  - Generate module breakdown and execution plan for this requirement
agent_created: true
---

# GitHub Spec Planner

## Overview

Turn a one-line project idea into a complete, auditable planning package: GitHub competitive research → `spec.md` → module breakdown → `plan.md` with justified tech stack → multi-dimensional delivery test suite. Every factual claim carries a source ID, URL and retrieval timestamp; every downstream artifact traces back to an upstream requirement or observation.

## When to Use

Trigger on requests such as: "before building this, find similar open-source projects and write the spec", "帮我做项目规划 / 写 spec.md / 写 plan.md / 生成测试集", "调研半年内 star 最高的同类项目", "确定技术栈并说明依据". Also use when a user supplies a rough idea and expects a ready-to-execute planning package rather than code.

Do not use for isolated bug fixes, code reviews, or purely conversational questions about an existing project.

## Input Template — 把模糊想法变清晰

When the user's request is a single vague sentence and lacks target users, core features, or a concrete scenario, present the fill-in template below and wait for it to be completed before entering Stage 0. Do not start research on an under-specified idea.

```
我要做一个【一句话描述，模糊也行】
给谁用：【目标用户，如「独立开发者」「小团队运营」】
它要解决什么问题：【现在的痛点或低效之处】
核心功能：【2-3 个最重要的能力】
一个典型场景：【谁在什么情况下用它做什么】
我明确不想要的：【排除项，可留空】
已确定的约束：【技术/平台/时间/预算，可留空】
```

**模板是引导，不是门槛**：填不出来的字段允许留空或写「不知道」，按 `[假设]` 登记后继续，不反复追问。用户若直接给出完整描述，不必强制套用，直接进入 Stage 0。

模板的每个答案都是后续 spec 的第一手输入：用户填写的约束与排除项记为 `OBS-USR-xxx`，作为需求的来源之一，与 GitHub 调研证据并列。

## Non-Negotiable Rules

1. **无来源不落笔**：spec、plan、测试集中的每条事实、需求、选型、指标都必须挂接 `SRC-`/`OBS-` ID。无法验证的推断写 `[假设]` 并在 `sources.md` 登记，不得伪装成事实。
2. **可验证**：所有来源必须在 `source_registry` 与 `sources.md` 中有可访问的 URL 和抓取时间；`github_top5.json` 保留 `schema_version` 与 `reproduce_command`。
3. **可复用**：固定输出目录与文件名，从 `assets/` 复制模板，不凭记忆重写字段；ID 一经发布不复用、不重命名。
4. **不编造**：API 失败、项目不足 5 个、指标无来源时，按真实情况输出并说明限制，绝不补足虚构条目或用「知名项目通常…」填补空白。
5. **先锁口径**：「半年内」按 `created`（近半年新建）为默认；采用其他口径必须在 `sources.md` 显式声明理由。

## Workflow at a Glance

| 阶段 | 核心动作 | 产出 | 门禁 |
| --- | --- | --- | --- |
| 0 对齐 | 抽取关键词、锁定口径与输出目录 | 参数清单 | 口径已声明 |
| 1 调研 | 运行 GitHub Top5 脚本 | `00-research/*` | 来源 ID ≥ 项目数 |
| 2 分析 | 逐项目分析 + 来源台账 | `analysis.md`、`sources.md` | 每条结论有来源 |
| 3 规格 | 写需求与板块划分 | `spec.md` | 每个 REQ/MOD 可追溯 |
| 4 计划 | 写技术栈决策与任务 | `decisions.md`、`plan.md` | 每个 DEC 有备选、TASK 有 DoD |
| 5 测试 | 生成多维度用例 | `test_suite.md`、`test_cases.csv` | 每个 TEST 映射 REQ |
| 6 校验 | 运行校验器并修复 | `validation_report.md` | 0 失败项 |

## Stage 0 — 对齐需求与口径

从用户描述中抽取 2–5 个关键词（领域词 + 功能词），确认项目约束与「半年内」口径。设定工作目录 `DOCS` 为用户项目下的 `docs/`（若用户指定其他路径则以其为准）。建立固定结构：

```
docs/
├── 00-research/  github_top5.json, github_top5.md, analysis.md
├── 01-spec/      spec.md, sources.md
├── 02-plan/      plan.md, decisions.md
├── 03-tests/     test_suite.md, test_cases.csv
└── validation_report.md
```

读取 `references/research_method.md` 的第 1 节，确认口径后进入调研。

## Stage 1 — GitHub Top 5 调研

设置 `SKILL_DIR=~/.workbuddy/skills/github-spec-planner`，执行：

```bash
python3 "$SKILL_DIR/scripts/github_top5.py" \
  --keywords "关键词1,关键词2,关键词3" \
  --topics "可选topic" \
  --months 6 --window-basis created --top 5 \
  --output "$DOCS/00-research/github_top5.json" \
  --report "$DOCS/00-research/github_top5.md"
```

- 关键词超过 5 个时分批运行；未登录 GitHub API 的 search 限额为 10 次/分钟，脚本已内置限速与重试。建议用户设置 `GITHUB_TOKEN` 以提高限额，但不强制。
- 解读 `source_registry`、`similarity`、`warnings`。高 star 但关键词覆盖低的项目标为「背景参考」，不强行纳入需求推导。
- 若脚本退出码为 2 或返回不足 5 个项目：遵循 `references/research_method.md` 第 7 节的降级路径，用 WebSearch + WebFetch 人工核验，按真实数量输出；禁止编造补足。

## Stage 2 — 逐项目分析与来源台账

1. 复制 `assets/analysis.md.tpl` → `analysis.md`，`assets/sources.md.tpl` → `sources.md`。
2. 按 `references/research_method.md` 第 5 节逐项目填写：定位、核心功能、技术栈、架构、活跃度、可借鉴点、不适用点、纳入结论。每条结论附来源 ID。
3. 为跨项目的归纳结论分配 `OBS-001…` 并填入 analysis.md 的观察表；用户原始约束记为 `OBS-USR-001…`。
4. 在 `sources.md` 完整登记 JSON 中每个 `SRC-` 条目（URL、抓取时间、级别、用途、Supports），并写明假设与口径。
5. 门禁：任一条结论找不到来源 ID 时，回到 Stage 1 补证据或删除该结论。

## Stage 3 — 撰写 spec.md

1. 复制 `assets/spec.md.tpl` → `spec.md`，严格遵循 `references/spec_guide.md`。
2. 从 analysis.md 的「可借鉴点」与用户约束生成 `REQ-` 需求：每条含描述、优先级、来源、可判定验收标准、关联 TEST ID。竞品共有能力是强证据；用户独有的差异化需求以 `OBS-USR-` 为来源并登记风险。
3. 按 `references/spec_guide.md` 第 4 节的判据划分 `MOD-` 板块（4–9 个），写明职责、覆盖需求、输入输出、依赖、不含范围、来源；依赖必须无环。
4. 非功能需求必须量化并注明来源；无来源的指标标 `[假设]` 并写验证方法。
5. 门禁：每个 REQ 有来源与验收标准，每个 MOD 覆盖至少一个 REQ，Out of scope 与假设均已写明。此阶段不写框架与库选型。

## Stage 4 — 技术栈决策与 plan.md

1. 复制 `assets/decisions.md.tpl` → `decisions.md`，`assets/plan.md.tpl` → `plan.md`，遵循 `references/plan_guide.md`。
2. 对前端、后端、数据、基础设施、质量、可观测、安全合规逐层给出 `DEC-` 记录：决策、依据（`SRC-`/`OBS-`）、至少两个备选方案及取舍、代价、影响板块与任务。竞品未提供证据的维度必须说明真实依据，不得伪造竞品技术栈。
3. 按 5 个阶段（验证骨架 → 核心闭环 → 支撑能力 → 质量交付 → 发布回滚）拆分 `TASK-`：每个任务含覆盖的 MOD/REQ、产出、可验证的 DoD、依赖、带依据的估算、验证用 TEST ID。
4. 填写阶段出口条件、关键路径、里程碑门禁、风险与「需求 → 测试 → 阶段」对应表。
5. 门禁：每个 DEC 有备选与来源，每个 TASK 可追溯到 MOD/REQ 且有 DoD，估算均标注依据。

## Stage 5 — 生成多维度测试集

1. 复制 `assets/test_suite.md.tpl` → `test_suite.md`，`assets/test_cases.csv.tpl` → `test_cases.csv`，遵循 `references/testing_guide.md`。
2. 对每个 REQ 按验收标准生成用例，至少覆盖功能、边界、异常三类；有量化指标补性能，有写操作补数据一致性，有安全约束补安全；再按 spec 情况补兼容、可访问性、回归、验收维度。不适用的维度写 `N/A(理由)`，不留空。
3. CSV 保持固定表头 `test_id,dimension,related_req,preconditions,steps,expected,source_ids,priority,automated`；`related_req` 与 `source_ids` 均不得为空。测试预期来自 REQ 验收标准，来源可间接指向该 REQ 的来源；假设指标必须在 sources.md 登记。
4. 在 `test_suite.md` 写覆盖统计、维度矩阵、用例明细、执行策略、发布门禁（P0 100% 通过，P1 ≥95%）、可复用资产。
5. 门禁：Markdown 与 CSV 的用例一一对应，每条 TEST 映射到至少一个 REQ。

## Stage 6 — 一致性校验与交付

```bash
python3 "$SKILL_DIR/scripts/validate_docs.py" \
  --docs-dir "$DOCS" --report "$DOCS/validation_report.md"
# 可选：追加链接可达性检查
python3 "$SKILL_DIR/scripts/validate_docs.py" --docs-dir "$DOCS" --check-links
```

修复所有 FAIL 项后重跑，直到 0 失败。不可修复的链接失败需在报告中记录为已知风险。最后用 present_files 交付 `spec.md`、`plan.md`、`test_suite.md`、`test_cases.csv`、`validation_report.md` 与调研报告，并在回复中给出：找到的项目数量、板块数量、用例数量、遗留风险。

## Resources

### scripts/
- `scripts/github_top5.py`：GitHub Top5 检索与证据采集。检索式构造、证据分级、降级路径见 `references/research_method.md`。
- `scripts/validate_docs.py`：溯源一致性校验器。规则详解见 `references/traceability_spec.md`。

### references/（按需读取，避免一次性全部加载）
- `references/traceability_spec.md`：ID 体系、引用格式、sources.md 结构、校验规则。**Stage 2 前先读**。
- `references/research_method.md`：时间窗口口径、GitHub 检索式、证据分级、API 失败降级。**Stage 0–2 读**。
- `references/spec_guide.md`：需求推导、验收标准写法、板块划分判据。**Stage 3 读**。
- `references/plan_guide.md`：技术栈决策记录、阶段与任务拆分、估算依据。**Stage 4 读**。
- `references/testing_guide.md`：测试维度、CSV 字段、发布门禁。**Stage 5 读**。

### assets/（复制到输出目录后替换全部 `{{...}}` 占位符）
- `sources.md.tpl`、`analysis.md.tpl`、`spec.md.tpl`、`plan.md.tpl`、`decisions.md.tpl`、`test_suite.md.tpl`、`test_cases.csv.tpl`。

## Common Pitfalls

- 把竞品「高 star」直接等同于「适合借鉴」：必须同时检查相关性与许可证。
- 技术栈凭个人偏好写：没有 DEC 依据与备选方案的选型一律补证据或标假设。
- 需求只写形容词没有验收标准：会导致测试集无法生成，必须先回到 spec 修补。
- 测试来源列留空：校验器会判 FAIL，改为指向 REQ 的来源或已登记的假设。
- 交付前未运行校验器：任何 FAIL 项都意味着「可验证」承诺未达成。
