# AI Agent 使用说明

> **面向对象**：OpenCode 会话中的 AI Agent
> **语言**：全中文操作指令。本文档不是给人类看的指南，是给 AI 的任务执行协议。
> **最后更新**：2026-05-27

---

## 1. 系统概览

本知识库是一个**模拟人类记忆代谢的终身个人 Wiki 系统**。核心理念：你的知识库不是仓库，是会新陈代谢的生物体。

### 四层地质架构

```
00_Raw_Materials/    原始素材层    只读不修改    外部世界流入的定型内容
10_Wiki_Grid/        知识晶格层    读写（精准修改）  一生存下来的结构化晶体智识
20_Templates/        模板契约层    只读引用       所有产出物的 Frontmatter 格式约束
30_Daily_Stream/     时间流层      追加/生成      时间轴上的流动记忆（热→冷→冰封）
```

### 记忆代谢闭环

```
聊天对话 ──→ Logs ──→ Digest ──→ Wiki_Grid ──→ soul_profile.md ──→ Archives
(秒-分)     (日)      (日-周)     (月-年)       (周-月)            (年+)
```

---

## 2. 会话启动流程

每次新会话开始时，按以下顺序执行：

### 2.1 晨间唤醒（morning-sync）

扫描 `30_Daily_Stream/**/Digests/` 下最近 5 天的 `*_Digest.md`，压缩为 **≤300 字**的思想快照。

输出格式（纯文本，无 Markdown）：
```
Morning. Here's your current state from the past 5 days:

[300字以内的快照：关注焦点 + 卡点 + 思维线程 + 情绪趋势]

Let's continue.
```

若无 Digest，输出：
```
Morning. No recent digests found—looks like a fresh cycle. What are you thinking about today?
```

### 2.2 周一自动周报（集成于 morning-sync）

仅在**周一**执行。morning-sync 完成后检测：

```
today = Monday?
  ├─ 否 → 跳过
  └─ 是 →
      04_Weekly_Report/{year}/LastWeek_Weekly.md 存在且 >500 字节？
        ├─ 是 → 跳过（上周周报已存在）
        └─ 否 →
            ① 读取上周所有 Digest
            ② 按评论刊物文风生成周报（本周图景 + 深度聚焦 + 边缘地带 + 断面 + 风向）
            ③ 写入文件
            ④ 一行确认：📰 Week W{XX} 周报已自动生成
```

失败降级：静默跳过，`reminder_check` 会在下一步捕获。

### 2.3 周期提醒（reminder_check）

运行后检查 6 项任务的"距上次执行"间隔。只在有待办项时输出提醒；全绿时静默。

检测逻辑：
- **日刊蒸馏**：今天有 Chat Log 但无 Digest → ⚠️
- **锚点结晶**：`00_Anchors/` 为空 或 最新文件超过 14 天 → ⚠️
- **灵魂更新**：`soul_profile.md` 修改时间超过 7 天 → ⚠️
- **年度结晶**：当前是 12 月且去年未归档 → ⚠️
- **图谱熵控**：`Concepts/ + Entities/` 卡片 > 10 且超过 30 天未扫描 → ⚠️
- **日志归档**：月初且上月有残留 → ℹ 提醒

---

## 3. 目录结构与归类决策树

### 3.1 完整目录清单

| 路径 | 权限 | 用途 |
|------|------|------|
| `opencode.md` | 读 | 系统宪法，所有行为准则的来源 |
| `soul_profile.md` | 读写 | 当前精神镜像，顶部最新/底部历史 |
| `opencode.json` | 读 | OpenCode 启动配置（instructions 字段注入宪法和灵魂） |
| `.opencode/config.json` | 读 | 模型参数、技能启用列表、检索权重、提醒间隔 |
| `.opencode/paths.json` | 读 | **全系统唯一路径配置中心**，修改目录名只需改此处 |
| `.opencode/skills/` | 读+执行 | 17 个 Python 脚本 + 4 个 SKILL.md 原生技能 |
| `00_Raw_Materials/Books/` | 只写（追加） | 书籍全文/章节 |
| `00_Raw_Materials/Papers/` | 只写（追加） | 论文、演讲稿、访谈记录 |
| `00_Raw_Materials/WebClips/` | 只写（追加） | 网页文章、新闻、博客 |
| `10_Wiki_Grid/00_Anchors/` | 读写 | 底层思维范式、人生决策框架 |
| `10_Wiki_Grid/Concepts/` | 读写 | 原子概念卡片（Zettelkasten） |
| `10_Wiki_Grid/Entities/` | 读写 | 人、公司、地点、疾病实体 |
| `10_Wiki_Grid/Syntheses/` | 读写 | 跨领域合成报告 |
| `20_Templates/` | 只读 | 三种卡片的 Frontmatter 格式规范 |
| `30_Daily_Stream/{year}/{MM_Mon}/Logs/` | 只追加 | 当日对话流水 |
| `30_Daily_Stream/{year}/{MM_Mon}/Digests/` | 写入 | 当日思想日刊 |
| `30_Daily_Stream/Archives/` | 写入 | 往年冰封数据 |
| `soul_profile_archive/` | 写入 | 超过 2 年的 soul 历史版本 |
| `备注/` | 读写 | 系统说明文档 |

### 3.2 快速归类决策树

按以下顺序判断一段内容的目标目录：

```
① 这是外部源材料（书、演讲、论文、新闻）？
   └─ 是 → 00_Raw_Materials/{Books|Papers|WebClips}/
         路由规则：演讲/论文→Papers | 书籍→Books | 网页/新闻→WebClips

② 这是 AI 对话的原始记录？
   └─ 是 → 30_Daily_Stream/{year}/{MM_Mon}/Logs/YYYY-MM-DD_Chat.md

③ 这是从对话中蒸馏出的思考总结？
   └─ 是 → 30_Daily_Stream/{year}/{MM_Mon}/Digests/YYYY-MM-DD_Digest.md

④ 这是独立的结构化知识单元？
   └─ 是 →
       ├─ 抽象概念/方法论 → 10_Wiki_Grid/Concepts/
       ├─ 具体的人/公司/地点 → 10_Wiki_Grid/Entities/
       ├─ 跨领域洞察 → 10_Wiki_Grid/Syntheses/
       └─ 底层人生观/决策框架 → 10_Wiki_Grid/00_Anchors/

⑤ 这是系统配置或说明文档？
   └─ 是 → 根目录 或 .opencode/ 或 备注/
```

### 3.3 月份目录命名规范

日志和日刊按 `{year}/{MM_Mon}` 模式组织：
- `01_Jan`, `02_Feb`, `03_Mar`, `04_Apr`, `05_May`, `06_Jun`
- `07_Jul`, `08_Aug`, `09_Sep`, `10_Oct`, `11_Nov`, `12_Dec`

英文缩写必须与 `paths.json` 中的 `month_format: "MM_Mon"` 一致。

---

## 4. 模板规范

所有卡片产出必须严格遵循 `20_Templates/` 中的模板。不符合模板的产出应拒绝写入。

### 4.1 Template_Concept.md

```yaml
---
title: "概念名称"
file_type: concept          # 固定值
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: []
aliases: []
parent_concepts: []
child_concepts: []
related_entities: []
maturity: seedling          # seedling | sapling | evergreen
confidence: 0.0-1.0         # 置信度
---
```

必需章节：`## 一句话定义`、`## 核心阐述`、`## 关键论据与案例`、`## 反面观点与边界`、`## 与其他概念的关联`、`## 参考来源`

### 4.2 Template_Entity.md

```yaml
---
title: "实体名称"
file_type: entity           # 固定值
entity_type: person         # person | company | place | disease | product
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: []
aliases: []
related_concepts: []
related_entities: []
---
```

必需章节：`## 基本信息`、`## 背景与简介`、`## 关键事件时间线`、`## 与我的知识体系的关联`、`## 相关实体`、`## 参考来源`

### 4.3 Template_Digest.md

```yaml
---
title: "YYYY-MM-DD 思想日刊"
file_type: digest            # 固定值
digest_type: daily           # daily | weekly
created: YYYY-MM-DD
period_start: YYYY-MM-DD
period_end: YYYY-MM-DD
source_logs: ["filename.md"]
key_insights: ["insight1", "insight2"]
emerging_concepts: ["concept1"]
mood_summary: "short summary"
---
```

必需章节：`## 核心灵感捕获`、`## 知识深度拓展`、`## 涟漪映射建议`、`## 精神状态摘要`、`## 待办与后续`、`## 原始对话索引`

---

## 5. 自动行为

### 5.1 对话记录（log-append）

**每轮对话后自动执行。静默，不提示用户。**

格式规范（追加到 `30_Daily_Stream/{year}/{MM_Mon}/Logs/YYYY-MM-DD_Chat.md`）：

```markdown
## 问：HH:MM:SS
用户完整消息

### 答：HH:MM:SS
AI 完整回复

```

规则：
- 用户消息用 `##`（二级标题），AI 回复用 `###`（三级标题）
- 时间戳精确到秒
- 每次追加前有一个空行
- 文件名日期格式：`YYYY-MM-DD_Chat.md`
- 如果目录或文件不存在，自动创建

### 5.2 主动蒸馏提醒

**当连续对话超过 10 轮时**，在当前回复末尾追加：

> 今日对话已自动记录。需要生成今日思想日刊吗？（回复 digest 即可）

### 5.3 晨间唤醒（morning-sync）

每天首次对话自动执行。详见 §2.1。

---

## 6. 用户指令响应表

以下所有指令均在会话窗中直接执行，**无需 API Key**。

### 6.1 digest — 日刊蒸馏

| 指令 | 行为 |
|------|------|
| `digest` | 对今天生成日刊 |
| `digest YYYY-MM-DD` | 对指定日期生成日刊 |
| `digest week` | 补生成本周 7 天全部缺失日刊 |
| `digest month` | 补生成本月 30 天全部缺失日刊 |

响应步骤：
1. 读取 `30_Daily_Stream/{year}/{MM_Mon}/Logs/YYYY-MM-DD_Chat.md`
2. 执行三模块蒸馏（详见 §7.1）
3. 按 `Template_Digest.md` 格式写入 `30_Daily_Stream/{year}/{MM_Mon}/Digests/YYYY-MM-DD_Digest.md`
4. 在对话窗汇报核心洞察预览

若是 `digest week` 或 `digest month`，对每一天循环执行：检查 Digest 是否存在 → 检查 Chat Log 是否存在 → 生成。

### 6.2 ingest — 语料分析入库

| 指令 | 行为 |
|------|------|
| `ingest <查询>` | 研究外部知识 → 归档源材料 → 提取概念/实体 → 写入合成报告 |
| `ingest raw <查询>` | 仅归档源材料到 Raw_Materials，不做分析提取 |
| 自然语言问题 | "乔布斯2009年的演讲是什么？" 等同 `ingest` |

响应步骤（详见 §7.2）：
1. 研究/检索源材料内容
2. 路由写入 `00_Raw_Materials/{Books|Papers|WebClips}/`
3. 提取概念 → `10_Wiki_Grid/Concepts/`（按 Template_Concept.md）
4. 提取实体 → `10_Wiki_Grid/Entities/`（按 Template_Entity.md）
5. 如有跨领域关联 → `10_Wiki_Grid/Syntheses/`
6. 汇报产出清单

### 6.3 anchor — 锚点结晶

响应步骤（详见 §7.3）：
1. 扫描近 4 周所有 `_Digest.md`
2. 列出 `00_Anchors/` 中已有锚点
3. 识别满足 2+ 条标准的候选框架（反复出现/跨领域/是思维框架/用户明确认可）
4. 对每个候选：创建新锚点 或 更新已有锚点的"本周更新"区

### 6.4 remind — 周期提醒

运行 `reminder_check.py`，输出 6 项任务的友好提醒清单。

### 6.5 fixlinks — 链接修复

运行 `link_validator.py`，扫描全库破损双链并自动创建最小占位卡片。已在写入新卡片后自动执行。

### 6.6 sync — 手动晨间唤醒

立即执行 morning-sync 流程。

### 6.7 digest auto — API 强制模式

执行 `python3 .opencode/skills/eod_digest.py auto`。需要配置 `DEEPSEEK_API_KEY` 环境变量。

---

## 7. 核心工作流详解

### 7.1 digest 三模块蒸馏

从 Chat Log 中蒸馏三类内容：

**模块 1 — 核心灵感捕获**
1-3 条一句话洞察。独立、可复用。6 个月后阅读仍能理解。

**模块 2 — 知识深度拓展**
对讨论的核心技术/设计/框架进行学术级或工程级深度解析。不是摘要，是增值分析。包括：
- 理论基础（引用概念、框架、论文）
- 实践含义和工程权衡
- 可迁移的推理步骤

**模块 3 — 涟漪映射建议**
分析灵感与现有 Wiki 节点的关联。每条建议：
- 用 `[[节点名]]` 双链格式
- 说明关系性质（强化/质疑/新关联）
- 给出具体的修改建议

**蒸馏质量要求**：
- 洞察必须是对话中没有明说的深层含义，不是复述对话
- 深度拓展必须增加对话中没有的学术/工程内容
- 涟漪建议必须是可操作的（"创建 XX 卡片"而非"也许有关联"）

### 7.2 ingest 五步分发

**Step 1：源材料路由**

| 内容类型 | 关键词 | 目标目录 |
|----------|--------|----------|
| 演讲/Keynote | 演讲, speech, talk, commencement | `Papers/` |
| 论文/学术 | 论文, paper, journal | `Papers/` |
| 书籍/章节 | 书, book, chapter | `Books/` |
| 新闻/文章 | 新闻, news, article, blog | `WebClips/` |
| 访谈 | 访谈, interview | `Papers/` |
| 其他 | — | `WebClips/` |

**Step 2-5**：写入 Raw_Materials → 提取概念 → 提取实体 → 合成报告

### 7.3 anchor 框架识别

锚点判断标准（满足 2+ 条即为候选）：
1. 在 3 周以上的 Digest 中反复出现
2. 跨越至少 2 个不同领域/主题
3. 是"如何思考"的框架，而非"思考的答案"
4. 用户明确表达过"这是一种底层框架/思维模型"

锚点卡片格式：
```yaml
file_type: anchor
created: YYYY-MM-DD
updated: YYYY-MM-DD
confidence: 0.0-1.0
```
必需章节：`## 一句话定义`、`## 核心框架`、`## 来源与演化`、`## 适用边界`、`## 关联概念`、`## 本周更新`

更新策略：锚点是保守更新的——已有锚点只在新证据出现时追加到"本周更新"区，不修改框架正文。

---

## 8. 文件写入规则

### 8.1 分层权限

| 层级 | 权限 | 规则 |
|------|------|------|
| `00_Raw_Materials/` | 只追加写入 | 绝不修改已有文件。如需更正，写入新文件并标注版本 |
| `10_Wiki_Grid/` | 读写 | 修改必须精准局部，不全文重写。使用 `ast_patcher.py` 或追加 block |
| `20_Templates/` | 只读 | 绝不修改模板 |
| `30_Daily_Stream/Logs/` | 只追加 | 日志是流水账，不修改历史内容 |
| `30_Daily_Stream/Digests/` | 写入 | 由 `eod_digest.py` 或 AI 生成 |

### 8.2 命名规范

- 中文内容用中文文件名，英文内容用英文文件名
- 用下划线替代空格（`Steve_Jobs_2009_Speech.md`）
- 日期文件严格 `YYYY-MM-DD` 格式

### 8.3 路径解析

所有路径从 Vault 根目录（`/Users/matthew/Desktop/AI Dock/LLM Wiki/AI Vault`）开始。
日志和日刊路径使用 `paths.json` 的 `logs_pattern` 和 `digests_pattern`：
```
30_Daily_Stream/{year}/{MM_Mon}/Logs/
30_Daily_Stream/{year}/{MM_Mon}/Digests/
```

---

## 9. 双链与格式规范

### 9.1 双链语法
- 内部链接：`[[文件名]]`（Obsidian 标准，不含 `.md` 扩展名）
- 跨目录链接同样使用 `[[文件名]]`，Obsidian 自动解析
- 标签：`#tag` 格式（不是 `[[tag]]`）

### 9.2 辩证冲突区块
当新观点与旧卡片冲突时，不覆盖旧卡片，而是追加：
```markdown
> [!danger] 认知演进与范式转移
> * **2024-03 历史观点**：旧结论
> * **2026-05 最新修正**：新结论
```

### 9.3 Frontmatter
所有 Markdown 文件使用 YAML Frontmatter（`---` 包裹）。不是 TOML，不是 JSON。

---

## 10. 脚本调用参考

### 10.1 日常高频脚本（会话窗直接调用，不需要 bash）

| 脚本 | 用途 | 示例 |
|------|------|------|
| `eod_digest.py` | 准备蒸馏上下文 | `python3 .opencode/skills/eod_digest.py prepare [date]` |
| `eod_digest.py` | 写入蒸馏结果 | `python3 .opencode/skills/eod_digest.py write <json> [date]` |
| `corpus_ingest.py` | 内容类型路由 | `python3 .opencode/skills/corpus_ingest.py route speech` |
| `corpus_ingest.py` | 渲染概念卡片 | `python3 .opencode/skills/corpus_ingest.py render concept <json>` |
| `corpus_ingest.py` | 写入概念卡片 | `python3 .opencode/skills/corpus_ingest.py write concept <json>` |
| `corpus_ingest.py` | 写入实体卡片 | `python3 .opencode/skills/corpus_ingest.py write entity <json>` |
| `anchor_weekly.py` | 列出已有锚点 | `python3 .opencode/skills/anchor_weekly.py list` |
| `anchor_weekly.py` | 写入锚点 | `python3 .opencode/skills/anchor_weekly.py write <json>` |
| `anchor_weekly.py` | 更新锚点 | `python3 .opencode/skills/anchor_weekly.py update <title> <text>` |
| `reminder_check.py` | 运行周期检测 | `python3 .opencode/skills/reminder_check.py` |
| `link_validator.py` | 扫描修复链接 | `python3 .opencode/skills/link_validator.py` |
| `log_append.py` | 手动追加消息 | `python3 .opencode/skills/log_append.py user "消息"` |

### 10.2 低频维护脚本

| 脚本 | 用途 | 触发时机 |
|------|------|----------|
| `soul_updater.py` | 周更新 soul_profile | 每周由 AI 手动调用 |
| `yearly_crystallize.py` | 年硬化 + 冰封 | 每年底 |
| `graph_entropy.py` | 扫描重复概念 | 卡片 > 50 时手动触发 |
| `conflict_resolver.py` | 新概念冲突检测 | 写入概念时自动触发 |
| `ripple_weave.py` | 全库双链更新 | 重命名/合并概念时触发 |
| `ast_patcher.py` | Markdown 精准修改 | 按需调用 |
| `hybrid_search.py` | 70/20/10 检索 | 用户查询时触发 |
| `memory_router.py` | 数据层分流 | 检索前路由 |

### 10.3 不使用脚本的场景

以下操作直接写入文件，不通过脚本：
- digest 的蒸馏和 Markdown 渲染（AI 在会话窗直接完成）
- ingest 的源材料归档（AI 直接写入）
- log-append 的实时追加（AI 直接追加，比脚本调用更快）

---

## 11. 生命周期与归档

### 11.1 时间维度上的代谢节奏

| 周期 | 触发 | 操作 | 输入 → 输出 |
|------|------|------|-------------|
| 每轮对话 | 自动 | log-append | 消息对 → Chat Log |
| 每日 | `digest` | eod_digest | Chat Log → Digest |
| 每日首次 | 自动 | morning-sync | 近5天 Digest → 300字快照 |
| 每周 | AI 手动 | soul_updater | 本周 Digest → soul_profile.md 重写 |
| 每2-4周 | `anchor` | anchor_weekly | Digest → 00_Anchors/ 框架卡片 |
| 每30天 | `remind` 提醒 | graph_entropy | Wiki_Grid → 重复检测 |
| 每年底 | AI 手动 | yearly_crystallize | 全年 Digest → Wiki_Grid + Archives 冰封 |
| 每2年 | soul_updater | 旧版本迁移 | soul_profile 历史 → soul_profile_archive/ |

### 11.2 冷热分离权重

```
热数据（70%）：soul_profile.md + 近两周 Digests
温数据（20%）：10_Wiki_Grid/ 全量
冷数据（10%）：30_Daily_Stream/Archives/（仅显式查询时激活）
```

---

## 12. 错误处理

### 12.1 API Key 缺失

**触发场景**：用户输入 `digest auto` 但 `DEEPSEEK_API_KEY` 未设置。

**降级策略**：自动切换到会话窗蒸馏模式（通道 B）。回复用户：
> API Key 未配置。已在会话窗中执行蒸馏，质量一致。

### 12.2 当日无 Chat Log

**触发场景**：用户输入 `digest` 但今天没有对话记录。

**降级策略**：回复：
> 今天还没有对话记录。等我们聊完后再输入 digest 生成日刊。

### 12.3 模板文件缺失

**触发场景**：`20_Templates/Template_Concept.md` 等不存在。

**降级策略**：使用内置的 Frontmatter 规范（本文档 §4 中的字段和章节要求）。同时提醒用户模板文件缺失。

### 12.4 目标目录不存在

**触发场景**：月份目录尚未创建。

**降级策略**：先 `mkdir -p` 创建目录，再写入文件。目录路径从 `paths.json` 读取。

### 12.5 多日志文件冲突

**触发场景**：当天目录下存在多个匹配日期的 Chat Log。

**降级策略**：全部读取，合并蒸馏。不做去重（蒸馏 Prompt 中的重复内容通常不影响质量）。

---

## 13. 配置参考

### 13.1 config.json 关键字段

```json
{
  "model": { "provider": "deepseek", "model_id": "deepseek-v4-pro" },
  "retrieval": {
    "default_weights": { "hot": 0.70, "warm": 0.20, "cold": 0.10 },
    "hot_window_days": 14
  },
  "digest": { "auto_remind_after_rounds": 10, "morning_sync_days": 5 },
  "archive": { "soul_profile_history_years": 2 },
  "reminder": {
    "intervals": {
      "digest_daily": 1, "anchor_weekly": 14,
      "soul_updater_weekly": 7, "graph_entropy_monthly": 30
    }
  }
}
```

### 13.2 paths.json 关键字段

日志和日刊的路径模板：
```json
{
  "daily_stream": {
    "logs_pattern": "30_Daily_Stream/{year}/{month}/Logs/",
    "digests_pattern": "30_Daily_Stream/{year}/{month}/Digests/",
    "month_format": "MM_Mon"
  }
}
```

`{month}` 替换示例：`strftime("%m_%b")` → `05_May`。

### 13.3 opencode.json

在 `instructions` 数组中指定的文件会在每个新会话启动时注入 System Prompt。当前配置：
```json
{ "instructions": ["opencode.md", "soul_profile.md"] }
```

---

## 14. 当前知识库清单

> 以下为自动统计的快照。运行 `healthcheck` 可自动更新本文档中的过期数字。

### 14.1 Concepts（概念卡片）— 111 张

### 14.2 Entities（实体卡片）— 12 张

### 14.3 Syntheses（合成报告）— 11 篇

### 14.4 00_Anchors（思维锚点）— 4 个

### 14.5 Raw_Materials（原始素材）— 62 篇

| 目录 | 数量 |
|------|------|
| Books/ | 2 |
| Papers/ | 2 |
| WebClips/ | 58 |

### 14.6 Digests（日刊）— 2 篇

| 文件 | 日期 |
|------|------|
| 2026-05-26_Digest.md | 2026-05-26 |
| 2026-05-27_Digest.md | 2026-05-27 |

### 14.7 Weekly_Report（周报）— 1 篇

| 文件 | 周 |
|------|-----|
| 2026-W22_Weekly.md | W22 |

---

*本文档由 AI 维护。系统结构变更时自动更新。*
