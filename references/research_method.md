# GitHub 开源项目调研方法

本文件供 `scripts/github_top5.py` 的使用与人工补充调研时参考。目标：让「半年内 star 排名前 5 的类似开源项目」这一结论**可复核、可重跑、无编造**。

## 1. 「半年内」的三种口径（必须先锁定并在文档中声明）

| 口径 | 含义 | 实现方式 | 适用场景 |
| --- | --- | --- | --- |
| `created`（默认） | 近半年内**新建**的项目，按 star 排序 | `created:>=YYYY-MM-DD` | 用户字面意思「半年内 star 排名前 5」；看新兴项目 |
| `pushed` | 近半年内**仍在活跃维护**的项目（不限创建时间） | `pushed:>=YYYY-MM-DD` | 关注活跃度而非新鲜度 |
| star 增长 | 半年内新增 star 最多 | GitHub API 无原生字段，需 star-history 类外部服务或用户提供快照 | 仅在用户提供数据源时使用，否则不得推断 |

脚本默认 `created`。若用户口径不明，在 `sources.md` 的「假设与口径」段落写明所采用口径及理由，不要静默替换。窗口按 `months * 30 天` 近似，脚本会在输出的 `methodology.window_approximation` 中记录 `since` 日期。

## 2. 检索式构造

```
"<keyword>" created:>=2026-05-21 archived:false fork:false [topic:<topic>] [stars:>=N]
```

- 每个关键词单独发起一次 `search/repositories`，`sort=stars&order=desc`，再按 `full_name` 合并去重。
- 关键词应从用户的一句话需求中抽取 2–5 个，兼顾**领域词**与**功能词**。例：「一个带标签和看板视图的团队任务管理器」→ `task manager, kanban, issue tracking, team collaboration`。
- 可加 `topic:<name>` 缩小范围，但 topic 覆盖不全，勿作为唯一条件。
- 未登录状态下 search API 为 10 次/分钟，core API 为 60 次/小时。脚本内置 1 秒间隔与 `Retry-After` 处理；关键词超过 5 个时应分批执行而非提高并发。

## 3. 每个项目必须采集的证据

| 字段 | 来源级别 | 用途 |
| --- | --- | --- |
| `stargazers_count` / `forks_count` | A：GitHub API | 排名与流行度结论 |
| `created_at` / `pushed_at` | A：GitHub API | 验证「半年内」与活跃度 |
| `description` / `topics` / `homepage` | A：GitHub API | 判断相关性 |
| `languages` / `license` | A：GitHub API | 技术栈与合规性判断 |
| `open_issues_count` / `contributors` | A：GitHub API | 维护健康度 |
| README 全文/摘录 | B：仓库原始文件 | 功能特性、架构、安装方式的直接证据 |
| 搜索结果片段 | C：仅作线索 | 不得作为结论依据，必须回溯到 A/B 级来源 |

脚本为每个来源生成 `SRC-XXX-NNN` 形式的 ID，并写入 `source_registry`（含 URL、抓取时间、用途、级别）。**任何写进 spec/plan/test 的事实必须能指向其中一个 ID。**

## 4. 相关性判定（避免「star 高但不相似」）

脚本给出词面覆盖率 `matched_keywords / total_keywords`，仅作初筛。人工/代理分析阶段还需逐项判断：

1. 核心功能是否重合（不是「都是 Web 应用」这种泛化相似）。
2. 目标用户是否一致（个人工具 vs 企业协作 vs 开发者 SDK）。
3. 架构约束是否可借鉴（单体 / 插件化 / 边缘计算等）。
4. 明确记录**不相似之处**，避免把竞品结论错误迁移到本项目。

覆盖率低但 star 极高的项目，应在 `analysis.md` 中标注「高 star 弱相关，仅作背景参考」，不得强行纳入需求推导。

## 5. 逐项目分析模板（`00-research/analysis.md`）

对每个 Top 5 项目写：

```markdown
### 1. owner/repo  [SRC-GH-001, SRC-GH-002]
- 一句话定位：... [SRC-GH-001]
- 核心功能：（3–6 条，每条带来源 ID）
- 技术栈：语言/框架/存储/部署，逐条带来源 ID [SRC-GH-00X]
- 架构与扩展点：... [README 来源 ID]
- 活跃度证据：stars=..., pushed_at=..., contributors=... [SRC-GH-001]
- 可借鉴点：...（对应到候选需求 REQ-XXX）
- 不适用点/风险：...（许可证、规模、技术栈冲突）
- 结论：纳入 / 仅作背景（附理由）
```

## 6. 交叉验证规则

- 同一结论若被多个来源支持，列出全部来源 ID。
- 若来源之间冲突（例如 README 说支持某功能但 issue 显示已移除），在 `analysis.md` 中显式记录冲突并以更新时间更近的 A 级来源为准。
- 无法验证的推断写入 `sources.md` 的「假设」段落，并在 spec 中标注 `[假设]`，不得伪装成事实。

## 7. API 失败时的降级路径（严禁编造）

1. 脚本返回退出码 2 且无候选数据 → 不要写「Top 5」报告。
2. 改用 WebSearch 搜索 `site:github.com <keywords> created:>=<since> stars`，再用 WebFetch 打开仓库页核对 star/创建时间。
3. 每条替代来源仍需给出 URL、抓取时间，并在 `sources.md` 中标注级别 C→B（页面可见信息）。
4. 若仍无法获得 5 个可验证项目，按实际数量输出，并在报告首行写明「仅找到 N 个可验证项目」，不得补足虚构条目。

## 8. 复现性

- 保留脚本输出的 `reproduce_command`，原样复制到 `github_top5.md` 第 7 节。
- star 数是快照，报告必须带 `generated_at`；后续复核时重新运行脚本对比差异。
