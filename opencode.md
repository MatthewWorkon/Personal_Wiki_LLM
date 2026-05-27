# OpenCode System Constitution

> 本文档是整个 My_LLM_Wiki 知识库系统的 **最高行为准则**。
> 所有技能脚本、模板、检索路由、结晶逻辑均受本宪法约束。
> 随技术演进与认知升级进行低频微调。

---

## 1. 核心原则

### 1.1 单向数据流
```
Logs → Digests → Wiki_Grid → soul_profile.md → Archives
```
数据永远按此链路单向流动，严禁反向写入或循环引用。

### 1.2 最小干预写入
- 对 `00_Raw_Materials/`：**只读**，绝不修改原始素材。
- 对 `10_Wiki_Grid/`：拥有读写权，但修改必须通过 `ast_patcher.py` 精准局部修改。
- 对 `30_Daily_Stream/`：`Logs/` 只追加，`Digests/` 由日结晶脚本生成，人类不直接编辑。

### 1.3 模板契约
所有新产出（概念卡片、实体卡片、Digest）必须遵循 `20_Templates/` 中定义的 Frontmatter 规范。
不符合模板的产出将被 `eod_digest.py` 拒绝写入。

### 1.4 热冷分离
- **热数据**：当前年份（2026/），高频读写，向量索引权重最高。
- **温数据**：`10_Wiki_Grid/`，中频读取，权重中等。
- **冷数据**：`30_Daily_Stream/Archives/`，低频解冻，向量索引权重最低。

---

## 2. 技能脚本职责矩阵

| 脚本 | 环节 | 触发频率 | 输入 | 输出 |
|------|------|----------|------|------|
| `log_append.py` | 实时记录 | 每次对话 | 用户/AI 消息 | Logs/YYYY-MM-DD_Chat.md 追加 |
| `memory_router.py` | 检索路由 | On-demand | 用户查询 | 热/温/冷数据分流指令 |
| `hybrid_search.py` | 混合检索 | On-demand | 路由指令 + 查询 | 70/20/10 加权上下文 |
| `eod_digest.py` | 日结晶 | 每日/按需 | Logs/ 当日对话 | Digests/ 思想日刊 |
| `morning_sync.py` | 晨间唤醒 | 每日首次对话 | 近 5 天 Digests | 300 字思想快照 → System Prompt |
| `soul_updater.py` | 周更新 | 每周 | 本周 Digests | soul_profile.md 渐进重写 |
| `yearly_crystallize.py` | 年硬化 | 每年 | 全年 Digests | Wiki_Grid + Archives 冰封 |
| `graph_entropy.py` | 图谱熵控 | 定期 | Wiki_Grid 全量 | 合并重复概念、重写双链 |
| `conflict_resolver.py` | 冲突消解 | On-write | 新概念 vs 旧卡片 | 辩证区块 → 旧卡片追加 |
| `ripple_weave.py` | 涟漪联动 | On-write | 被修改的节点 | 全库双链更新 |
| `corpus_ingest.py` | 语料分析 | On-demand | 外部知识查询 | Raw_Materials + Wiki_Grid 多路分发 |
| `anchor_weekly.py` | 锚点结晶 | 每 2-4 周 | 近期 Digests | 00_Anchors/ 框架卡片 |
| `reminder_check.py` | 周期提醒 | 每次会话启动 / On-demand | 文件时间戳 | 6 项任务提醒清单 |
| `link_validator.py` | 链接修复 | On-demand | 全库双链扫描 | 破碎链接 + 空壳 → 自动创建最小卡片 |
| `health_check.py` | 健康自检 | 每次会话启动 / On-demand | 全项目 | 6 项自检 → 能自愈的无感修复 + 不能自愈的提醒 |
| `weekly_report.py` | 周报生成 | 每周 / On-demand | 本周 Digests + Wiki_Grid | 04_Weekly_Report/ 评论刊物风格周报 |
| `ast_patcher.py` | 精准修改 | On-write | 目标文件 + 操作 | Markdown AST 局部 patch |

---

## 3. 检索路由规则（70/20/10）

```
soul_profile.md + 近两周 Digests  →  权重 70%（感知当前精神状态）
10_Wiki_Grid/                      →  权重 20%（调取结构化常识）
30_Daily_Stream/Archives/          →  权重 10%（仅在明确提及历史时触发）
```

---

## 4. 文件路径约定

所有脚本通过 `.opencode/paths.json` 读取路径配置，严禁在脚本中硬编码路径。
路径发生变更时，仅修改 `paths.json` 一处即可。

---

## 5. 归档与保洁策略

- **每日**：`eod_digest.py` 生成 Digest 后，当日 Logs 标记为已处理（不改动内容）。
- **每周**：`soul_updater.py` 重写 `soul_profile.md` 顶部，旧状态追加到文件底部 `## 历史版本` 区。
- **每年**：`yearly_crystallize.py` 将全年 `30_Daily_Stream/YYYY/` 打包冰封至 `Archives/`，精华沉淀至 `10_Wiki_Grid/`。
- **每 2 年**：`soul_profile.md` 超过 2 年的历史版本迁移至 `soul_profile_archive/YYYY.md`。

---

## 6. 格式规范

- 所有 Markdown 文件使用 YAML Frontmatter 头部。
- 标签使用 `#tag` 而非 `[[tag]]`。
- 内部链接使用 `[[文件名]]` 双链语法（Obsidian 标准）。
- 辩证冲突区块使用 `> [!danger] 认知演进与范式转移` 标注。

---

---

## 7. 触发指令约定

### 日刊蒸馏（eod_digest.py）— 双通道模式

系统支持两种蒸馏通道，按优先级自动路由：

| 通道 | 触发方式 | 条件 | 工作原理 |
|------|----------|------|----------|
| **通道 B（推荐）** | 对话窗输入 `digest` | 无需配置 | 会话窗 AI 直接读取 Logs，执行三模块蒸馏，写入 Digests |
| **通道 A（自动化）** | `digest auto` | 需配置 `DEEPSEEK_API_KEY` | 脚本调用 DeepSeek API 完成全流程 |

### 主要指令

| 指令 | 行为 | 通道 |
|------|------|------|
| `digest` | 对今天已有对话生成思想日刊 | B（会话窗蒸馏） |
| `digest YYYY-MM-DD` | 补生成指定日期的日刊 | B（会话窗蒸馏） |
| `digest week` | 补生成本周 7 天内全部缺失日刊 | B（会话窗蒸馏） |
| `digest month` | 补生成本月 30 天内全部缺失日刊 | B（会话窗蒸馏） |
| `digest auto` | 强制走 API 通道 | A（需 API Key） |
| `ingest <查询>` | 研究外部知识并归档分析分发 | B（会话窗驱动） |
| `ingest raw <查询>` | 仅归档源材料到 Raw_Materials | B（会话窗驱动） |
| `anchor` | 扫描近 4 周 Digest，生成或更新 00_Anchors/ 思维框架 | B（会话窗驱动） |
| `remind` | 检查全部 6 项周期任务，输出待办提醒清单 | `reminder_check.py` |
| `fixlinks` | 扫描全库破损链接并自动创建最小占位卡片 | `link_validator.py` |
| `healthcheck` | 运行完整项目健康自检并自动修复 | `health_check.py` |
| `weekly` | 生成上周回顾分析与下阶段展望周报 | `weekly_report.py` |
| `sync` | 手动触发晨间唤醒，生成思想快照 | `morning_sync.py` |

### 通道 B 工作流详解（推荐方式）

当你在对话窗中直接输入 `digest` 时，AI 执行以下流程：
1. 读取当日 `Logs/YYYY-MM-DD_Chat.md` 全部内容
2. 按三模块 Prompt 进行蒸馏（核心灵感捕获 + 知识深度拓展 + 涟漪映射建议）
3. 将蒸馏结果渲染为完整的 Digest Markdown
4. 写入 `Digests/YYYY-MM-DD_Digest.md`
5. 在对话窗中汇报生成结果

**优势**：无需 API Key，蒸馏质量由会话上下文完整保证，
AI 在蒸馏时可以结合你们整个对话的记忆而不仅仅是 Logs 中的文字记录。

### 自动化触发时机
- **对话记录**：每次用户和 AI 对话，`log_append.py` 自动追加到当日 Chat 日志，无需手动指令。
- **主动提醒**：连续对话超过 10 轮时，AI 在回复末尾主动询问是否需要生成今日日刊。
- **晨间唤醒**：每天首次对话时自动触发 `morning_sync.py` 注入思想快照。

---

*本宪法最后更新：2026-05-26*
