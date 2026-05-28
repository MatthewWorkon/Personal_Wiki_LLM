# My_LLM_Wiki

**全生命周期个人 LLM Wiki 知识库系统**

一个模拟人类记忆代谢机制的终身知识管理框架。不是仓库，是会新陈代谢的生物体。

---

## 核心概念

传统知识库在 5-10 年尺度上遭遇两大灾难：

1. **信息熵爆表** — 海量旧数据污染检索空间，信噪比雪崩
2. **知识库硬化** — 旧思想钢印无法修正，失去自我迭代能力

My_LLM_Wiki 通过**记忆分级与结晶机制**解决这个问题：

```
聊天对话 ──→ Logs ──→ Digest ──→ Wiki_Grid ──→ soul_profile ──→ Archives
(秒-分)      (日)      (日-周)     (月-年)        (周-月)         (年+)

短时记忆 → 工作记忆 → 长时记忆 → 灵魂锚点 → 历史冰封
```

---

## 架构概览

```
My_LLM_Wiki/                       ← Obsidian Vault & OpenCode 工作区
│
├── opencode.md                    ← 系统宪法（AI 行为总律）
├── soul_profile.md                ← 灵魂锚点（自我意识压缩表征）
├── opencode.json                  ← OpenCode 启动配置
│
├── .opencode/                     ← 系统配置与技能库
│   ├── config.json                ← 模型/检索/提醒参数
│   ├── paths.json                 ← 全系统唯一路径配置中心
│   ├── skills/                    ← 14 个 Python 脚本 + 4 个 SKILL.md
│
├── 00_Raw_Materials/              ← 【原始素材层】只读不修改
│   ├── Books/                     ← 书籍/章节
│   ├── Papers/                    ← 论文/演讲/访谈
│   └── WebClips/                  ← 网页剪藏/新闻
│
├── 10_Wiki_Grid/                  ← 【知识晶格层】读写（精准修改）
│   ├── 00_Anchors/                ← 底层思维范式
│   ├── Concepts/                  ← 原子概念卡片（Zettelkasten）
│   ├── Entities/                  ← 实体卡片（人/公司/地点）
│   └── Syntheses/                 ← 跨领域合成报告
│
├── 20_Templates/                  ← 【模板契约层】格式规范
│   ├── Template_Concept.md
│   ├── Template_Entity.md
│   └── Template_Digest.md
│
└── 30_Daily_Stream/               ← 【时间流层】流动记忆
    ├── {year}/{MM_Mon}/Logs/      ← 每日对话流水（热数据）
    ├── {year}/{MM_Mon}/Digests/   ← 每日蒸馏日刊（温数据）
    └── Archives/                  ← 往年冰封（冷数据）
```

---

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/yourname/My_LLM_Wiki.git
cd My_LLM_Wiki
```

### 2. 用 Obsidian 打开

```
Obsidian → Open folder as vault → 选择 My_LLM_Wiki 文件夹
```

### 3. 在终端中启动 OpenCode

```bash
opencode
```

### 4. 首次对话

新会话启动时，系统自动执行：
- **晨间唤醒** — 扫描近期 Digest 生成思想快照
- **周期提醒** — 检查待办任务（日刊、锚点、灵魂更新）

---

## 技能系统

### OpenCode 原生技能（4 项，自动加载）

| 技能 | 指令 | 功能 |
|------|------|------|
| `digest` | `digest` / `digest week` | 从当日对话蒸馏思想日刊 |
| `ingest` | `ingest <查询>` | 研究外部知识 → 归档 → 提取概念/实体 |
| `morning-sync` | 自动 / `sync` | 晨间扫描近期 Digest → 300 字快照 |
| `log-append` | 自动 | 每轮对话静默追加到 Chat Log |

### 手动指令（8 条）

| 指令 | 行为 |
|------|------|
| `digest` | 生成今天的思想日刊 |
| `digest YYYY-MM-DD` | 补生成指定日期日刊 |
| `digest week` | 补生成本周全量缺失日刊 |
| `digest month` | 补生成本月全量缺失日刊 |
| `ingest <查询>` | 研究外部知识并归档分析分发 |
| `ingest raw <查询>` | 仅归档源材料到 Raw_Materials |
| `anchor` | 扫描近 4 周 Digest，生成思维锚点框架 |
| `remind` | 检查全部 6 项周期任务 |
| `fixlinks` | 扫描全库破损链接并自动创建最小占位卡片 |
| `healthcheck` | 运行完整项目健康自检并自动修复 |
| `weekly` | 生成上周回顾分析与下阶段展望周报 |
| `sync` | 手动触发晨间唤醒 |

### 典型一天

```
早上打开终端，启动 OpenCode
  ├─→ 系统自动执行 morning-sync（读取昨晚的 Digest）
  └─→ 系统自动执行 reminder_check（提醒今天该蒸馏了）

白天对话
  └─→ 每句话自动记入 Logs/

晚上结束时输入 digest
  └─→ AI 读取今日 Chat Log → 三模块蒸馏 → 写入 Digest

周末输入 anchor
  └─→ 扫描近 4 周 Digest → 提取底层思维框架 → 写入 Anchors/
```

### 临时查询

```
"乔布斯2009年的演讲是什么？"
  └─→ AI 研究源材料 → 写入 Raw_Materials → 提取概念/实体 → 汇报
```

---

## 17 个 Python 脚本

| 脚本 | 环节 | 触发 |
|------|------|------|
| `log_append.py` | 实时记录 | 每次对话 |
| `memory_router.py` | 检索路由 | 按需 |
| `hybrid_search.py` | 混合检索 | 按需 |
| `eod_digest.py` | 日结晶 | 每日 |
| `morning_sync.py` | 晨间唤醒 | 每日首次 |
| `soul_updater.py` | 周更新 | 每周 |
| `yearly_crystallize.py` | 年硬化 | 每年 |
| `graph_entropy.py` | 图谱熵控 | 定期 |
| `conflict_resolver.py` | 冲突消解 | 写入时 |
| `ripple_weave.py` | 涟漪联动 | 写入时 |
| `corpus_ingest.py` | 语料分析 | 按需 |
| `anchor_weekly.py` | 锚点结晶 | 每 2-4 周 |
| `reminder_check.py` | 周期提醒 | 会话启动 / 手动 |
| `link_validator.py` | 链接修复 | 手动 / 写入后 |
| `health_check.py` | 健康自检 | 会话启动 / 手动 |
| `ast_patcher.py` | 精准修改 | 写入时 |

---

## 配置

所有参数在 `.opencode/config.json` 中集中管理：

```json
{
  "model": { "provider": "deepseek", "model_id": "deepseek-v4-pro" },
  "retrieval": {
    "default_weights": { "hot": 0.70, "warm": 0.20, "cold": 0.10 }
  },
  "reminder": {
    "intervals": { "anchor_weekly": 14, "soul_updater_weekly": 7 }
  }
}
```

路径映射在 `.opencode/paths.json` 中统一维护。修改目录名只需改一处。

---

## 模板规范

所有产出物遵循 `20_Templates/` 中的 Frontmatter 规范：

- **概念卡片**：`file_type: concept`，必需 `title + definition + elaboration`
- **实体卡片**：`file_type: entity`，必需 `entity_type + background + timeline`
- **日刊**：`file_type: digest`，必需 `key_insights + deep_dive + ripple_suggestions`

---

## 扩展

在 `.opencode/skills/` 下添加新脚本，在 `config.json` 的 `skills.enabled` 中注册。

如需新的 OpenCode 原生技能，创建 `.opencode/skills/<name>/SKILL.md`，OpenCode 启动时自动加载。

---

## 归档与保洁

| 周期 | 操作 |
|------|------|
| 每日 | `eod_digest.py` 生成 Digest |
| 每周 | `soul_updater.py` 重写 soul_profile.md |
| 每年 | `yearly_crystallize.py` 全年归档 + 结晶沉淀 |
| 每 2 年 | soul_profile 旧版本迁移至 `soul_profile_archive/` |

---

## 备注文档

| 文档 | 内容 |
|------|------|
| `备注/Vault_Structure_Reference.md` | 全库目录结构与归类说明 |
| `备注/技能触发说明.md` | 所有技能触发方式速查 |
| `备注/AI_Agent_使用说明.md` | 面向 AI Agent 的完整操作手册 |

---

## License

MIT
