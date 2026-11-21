# GitHub Spec Planner

[![Skill Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](SKILL.md)
[![Python](https://img.shields.io/badge/python-3.10%2B-green.svg)](scripts/)

**项目开工前，先让证据说话。**

一个给 AI Agent 用的技能（Skill）：把一句模糊的项目想法，变成一套**可溯源、可验证、可复用**的立项文档——自动调研 GitHub 近半年 star 排名前 5 的同类开源项目，据此写出 `spec.md`、划分项目板块、生成带技术栈决策依据的 `plan.md`，以及覆盖多维度的交付测试集。

每一条需求、每一个技术选型、每一条测试用例，都能追溯到真实的来源 URL 和抓取时间，而不是 AI 凭空编出来的。

---

## 它解决什么问题

| 痛点 | 这个技能的做法 |
| --- | --- |
| 立项靠拍脑袋，没有同类项目参照 | 自动检索 GitHub 近半年 star Top 5 同类项目，逐项分析功能/技术栈/活跃度/许可证 |
| spec 写得含糊，无法验收 | 每条需求带来源 ID 和可判定的验收标准，禁止「体验好」这类形容词 |
| 技术栈选型没有依据 | 每个选型是一条决策记录，含来源、至少两个备选方案和取舍代价 |
| 测试和需求对不上 | 每条测试用例映射到至少一个需求 ID，Markdown 矩阵和 CSV 双份交付 |
| 文档信息不可信、不可复用 | 统一 ID 体系 + 自动校验器，悬空引用、缺失来源、占位符一律拦截 |

---

## 工作流

```
一句话想法
   │
   ▼
① GitHub 调研      近半年 created / pushed 口径，Top 5 开源项目，生成来源台账
   │
   ▼
② 竞品分析         功能 / 技术栈 / 架构 / 活跃度 / 许可证 / 可借鉴点与风险
   │
   ▼
③ spec.md          功能需求 + 非功能需求，每条带来源；划分 MOD 板块
   │
   ▼
④ plan.md          技术栈决策记录 DEC + 阶段任务 TASK，任务含 DoD 与验证用例
   │
   ▼
⑤ 测试集           功能 / 边界 / 异常 / 性能 / 安全 / 兼容 / 一致性 / 回归 / 验收
   │
   ▼
⑥ 一致性校验       自动检查 9 份交付物、追溯链、悬空引用、占位符
```

---

## 溯源体系

所有文档共用一套 ID，形成双向可审计的链路：

| 前缀 | 含义 | 必须引用 |
| --- | --- | --- |
| `SRC-` | 来源条目（URL + 抓取时间 + 证据级别） | — |
| `OBS-` | 调研观察与结论 | ≥1 个 `SRC-` |
| `REQ-` | spec 中的需求 | ≥1 个 `SRC-`/`OBS-` |
| `MOD-` | 项目板块 | ≥1 个 `REQ-` |
| `DEC-` | 技术栈/架构决策 | ≥1 个 `SRC-`/`OBS-`，且含备选方案 |
| `TASK-` | 执行任务 | ≥1 个 `MOD-`/`REQ-` |
| `TEST-` | 测试用例 | ≥1 个 `REQ-` |

无来源支撑的推断必须标 `[假设]` 并在 `sources.md` 登记，不得伪装成事实。API 失败或可验证项目不足 5 个时按真实数量输出，绝不编造补足。

---

## 安装

### 方式一：导入到 WorkBuddy（推荐）

1. 下载本仓库的 Release zip，或点 `Code → Download ZIP`
2. 在 WorkBuddy 左侧栏点击 **专家·技能·连接器 → 技能**
3. 点 **添加技能 → 上传技能**，选择 zip 文件
4. 导入后在「已安装」里启用即可

### 方式二：手动安装

```bash
unzip github-spec-planner.zip -d ~/.workbuddy/skills/
```

重载 WorkBuddy 会话后生效。

---

## 使用

在 WorkBuddy 对话里直接描述需求即可触发：

- `帮我规划一个任务管理应用，先调研同类开源项目再写 spec`
- `根据这个需求生成项目板块划分和执行计划`
- `为我的项目生成带来源依据的多维度测试集`
- `先找近半年 star 最高的看板类开源项目，然后产出 spec 和 plan`

默认口径是「近 6 个月新建（created）的项目按 star 排序」。如果你要的是「近半年仍在活跃维护」或「star 增长最快」，在需求里说明，技能会在来源台账里声明所用口径。

---

## 产物结构

```
docs/
├── 00-research/
│   ├── github_top5.json     # 证据台账：来源 ID、URL、抓取时间、复现命令
│   ├── github_top5.md       # Top 5 调研报告
│   └── analysis.md          # 逐项目深度分析 + OBS 观察
├── 01-spec/
│   ├── spec.md              # 需求 + 验收标准 + MOD 板块划分
│   └── sources.md           # 来源清单 + 假设与口径
├── 02-plan/
│   ├── decisions.md         # 技术栈决策记录（依据 + 备选 + 代价）
│   └── plan.md              # 阶段 / 任务 / DoD / 关键路径 / 门禁
├── 03-tests/
│   ├── test_suite.md        # 维度矩阵 + 用例明细 + 发布门禁
│   └── test_cases.csv       # 机器可读用例，可导入测试管理平台
└── validation_report.md     # 溯源一致性校验结果
```

---

## 目录结构

```
github-spec-planner/
├── SKILL.md                  # 技能定义与完整工作流
├── README.md
├── scripts/
│   ├── github_top5.py        # GitHub Top 5 调研与证据采集
│   └── validate_docs.py      # 文档溯源一致性校验
├── references/               # 按需加载的方法论文档
│   ├── research_method.md    # 检索式、证据分级、API 失败降级
│   ├── traceability_spec.md  # ID 体系与引用格式
│   ├── spec_guide.md         # 需求推导与板块划分
│   ├── plan_guide.md         # 技术栈决策与任务拆分
│   └── testing_guide.md      # 测试维度与用例设计
└── assets/                   # 7 份文档模板
    ├── sources.md.tpl
    ├── analysis.md.tpl
    ├── spec.md.tpl
    ├── plan.md.tpl
    ├── decisions.md.tpl
    ├── test_suite.md.tpl
    └── test_cases.csv.tpl
```

---

## 独立运行脚本

两个核心脚本也可以脱离 WorkBuddy 单独使用。

### GitHub 调研

```bash
python3 scripts/github_top5.py \
  --keywords "task,manager,kanban" \
  --topics productivity \
  --months 6 --window-basis created --top 5 \
  --output docs/00-research/github_top5.json \
  --report docs/00-research/github_top5.md
```

未登录 GitHub 时 search API 限额为 10 次/分钟、core API 为 60 次/小时，脚本内置限速与重试。建议设置 `GITHUB_TOKEN` 提高限额：

```bash
export GITHUB_TOKEN=ghp_xxx
```

脚本只使用 Python 标准库，无需安装依赖。

### 一致性校验

```bash
python3 scripts/validate_docs.py --docs-dir docs \
  --report docs/validation_report.md
# 追加来源链接可达性检查
python3 scripts/validate_docs.py --docs-dir docs --check-links
```

退出码 0 表示全部通过，1 表示存在失败项。

---

## 设计原则

1. **无来源不落笔** — 事实、需求、选型、指标都必须挂接来源 ID
2. **可验证** — 所有来源有可访问 URL 和抓取时间，保留复现命令
3. **可复用** — 固定输出目录与文件名，模板化交付，ID 稳定
4. **不编造** — 数据不足时如实说明，不用「知名项目通常…」填补空白
5. **先锁口径** — 「半年内」默认按新建时间判定，改用其他口径必须显式声明

---

## 限制

- star 数是抓取时的快照，不是半年内的 star 增长量；对比时以 `generated_at` 为准
- 关键词相关性是词面匹配，不是语义判断；高 star 弱相关的项目只作背景参考
- GitHub API 未登录时限流较紧，大批量关键词调研建议配置 token
- 适用于产品/项目立项阶段；不适合单点 bug 修复或已有代码库的重构规划

---

## License

MIT
