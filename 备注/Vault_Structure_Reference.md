# My_LLM_Wiki 完整目录结构与归类说明

> 本文件是全库所有文件夹的分类指南。当你不知道一段内容该放到哪个文件夹时，查阅此文。
>
> 最后更新：2026-05-26

---

## 一、系统控制层（根目录文件）

| 文件 | 英文 | 用途 | 谁在写 | 多久改一次 |
|------|------|------|--------|-----------|
| `opencode.md` | System Constitution | AI 行为总律：约束所有脚本的检索路由、写入权限、归档策略 | 你手动微调 | 技术演进时低频更新 |
| `soul_profile.md` | Soul Anchor | 你的当前精神镜像：人生目标、焦虑卡点、思维模型、价值观。AI 的全局引导盘 | `soul_updater.py` 每周自动重写顶部 | 每周 |
| `.opencode/` | System Config | 配置中心：模型参数、路径映射、技能脚本 | 见下表 | — |
| `.obsidian/` | Obsidian Config | Obsidian 前端渲染设置（插件、外观、图谱），与 OpenCode 无关 | Obsidian 自身 | — |

### .opencode/ 子目录

| 文件/目录 | 用途 |
|-----------|------|
| `config.json` | 模型配置（API Key、BaseURL、MaxTokens）、技能启用列表、检索权重参数 |
| `paths.json` | **全系统路径配置中心**。所有脚本从此读取路径，修改目录名只需改这一处 |
| `config_schema.json` | 健康检查锚点：定义 config.json 的合法结构，用于年度兼容性巡检 |
| `skills/` | 17 个 Python 技能脚本，覆盖收集→记录→输出→记忆→更新→存储全链路 |

---

## 二、原始素材层 `00_Raw_Materials/`

> **权限：只读（OpenCode 绝不修改此层任何内容）**
>
> 这一层是"外部世界流入的内容"。已经定型的东西——书、论文、演讲稿、新闻报道。
> 放进来之后只追加索引，不改动原文。

| 子目录 | 英文 | 归类条件 | 示例 |
|--------|------|----------|------|
| `Books/` | 经典书籍 | 书籍全文或章节节选。长篇幅，有作者、出版年份 | 《思考，快与慢》第1章.md |
| `Papers/` | 论文/演讲 | 学术论文、公开演讲听写稿、访谈记录、Keynote 文字稿 | 乔布斯2009斯坦福演讲.md |
| `WebClips/` | 网页剪藏 | 博客文章、新闻报道、公众号深度文章、产品文档 | 2026-05_Karpathy_LLM_Memory.md |

### 归类决策

```
这段内容来自哪里？
├── 一本书的章节/全文         → Books/
├── 一场演讲/论文/访谈记录     → Papers/
└── 一个网页/博客/新闻文章     → WebClips/
```

### 命名规范

`{来源}_{标题关键词}.md`

---

## 三、知识晶格层 `10_Wiki_Grid/`

> **权限：读写（OpenCode 有完全的读写权，但修改必须通过 ast_patcher.py 精准局部修改）**
>
> 这一层是"你一生的结构化知识"。经过蒸馏、验证、网状的晶体智识。
> 一切从这里出发做检索和推理。

| 子目录           | 英文    | 归类条件                              | 模板                    | 示例                        |
| ------------- | ----- | --------------------------------- | --------------------- | ------------------------- |
| `00_Anchors/` | 思维锚点  | 底层人生观、核心决策框架、终身不变的思维范式            | 自由格式                  | "向死而生决策框架.md"             |
| `Concepts/`   | 概念卡片  | 原子化的核心概念（Zettelkasten 风格）。一个概念一张卡 | `Template_Concept.md` | "Memory Consolidation.md" |
| `Entities/`   | 实体卡片  | 人、地点、公司、品牌、产品。有实体属性的东西            | `Template_Entity.md`  | "Steve Jobs.md"           |
| `Syntheses/`  | 跨领域合成 | AI 自动发现的"你没意识到的跨领域联系"。暂时不属于任何单一概念 | 自由格式                  | "乔布斯哲学与禅宗美学.md"           |

### 归类决策

```
这段知识是什么性质？
├── 一个概念/理论/方法   → Concepts/
├── 一个人/公司/地点/产品 → Entities/
├── 多个领域的交叉洞察    → Syntheses/
└── 底层人生观/决策框架   → 00_Anchors/
```

---

## 四、时间流层 `30_Daily_Stream/`

> **权限：Logs 只追加，Digests 由脚本生成**
>
> 这一层是"你和 AI 对话的时间轴"。每天的生肉对话在这里，每晚的蒸馏日刊也在这里。

| 路径 | 英文 | 用途 | 谁在写 | 何时写入 |
|------|------|------|--------|----------|
| `2026/05_May/Logs/` | Daily Chat Logs | 每天和 AI 的原始对话，一问一答格式 | `log_append.py` | 每次对话实时追加 |
| `2026/05_May/Digests/` | Daily Digests | 每晚生成的"思想纪要与深度知识册" | `eod_digest.py` 或你输入 `digest` | 每日一次 |
| `Archives/` | Frozen Archives | 往年所有已完成的年份数据 | `yearly_crystallize.py` | 每年底 |

### 文件命名规范

- **Logs**：`YYYY-MM-DD_Chat.md`
- **Digests**：`YYYY-MM-DD_Digest.md`

### 归类决策

```
是今天的？
├── 对话记录        → Logs/YYYY-MM-DD_Chat.md
└── 蒸馏总结        → Digests/YYYY-MM-DD_Digest.md

是往年的？
└── 全部            → Archives/YYYY/
```

---

## 五、模板层 `20_Templates/`

> **权限：只读参考（写入时由脚本引用，不修改模板本身）**
>
> 所有概念卡片、实体卡片、日刊都必须遵循这些模板的 Frontmatter 规范。

| 文件 | 约束对象 | 核心必填字段 |
|------|----------|-------------|
| `Template_Concept.md` | 概念卡片 | title, file_type, created, maturity, confidence |
| `Template_Entity.md` | 实体卡片 | title, file_type, entity_type, created |
| `Template_Digest.md` | 日刊 | title, file_type, created, source_logs, key_insights |

### 模板的使用方式

- **你不需要手动填模板**。当你输入 `digest` 或 `ingest` 时，我自动按模板渲染。
- 如果想自定义格式约束，修改这三个模板文件后，所有脚本的下次产出自动生效。

---

## 六、归档与辅助目录

| 路径 | 用途 | 写入时机 |
|------|------|----------|
| `soul_profile_archive/` | `soul_profile.md` 超过 2 年的历史版本迁移至此 | 每年由 `soul_updater.py` 触发 |
| `备注/` | 本文件所在目录。存放系统自身的说明文档（非知识内容） | 手动 |

---

## 七、快速归类决策树

准备放入一段内容时，按以下顺序判断：

```
① 这是外部源材料（书、论文、网页），不是我自己的思考？
   └─ 是 → 00_Raw_Materials/{Books|Papers|WebClips}/
   └─ 不是 → 继续 ②

② 这是我和 AI 的对话记录？
   └─ 是 → 30_Daily_Stream/YYYY/MM_Mon/Logs/
   └─ 不是 → 继续 ③

③ 这是从对话中蒸馏出的思考总结？
   └─ 是 → 30_Daily_Stream/YYYY/MM_Mon/Digests/
   └─ 不是 → 继续 ④

④ 这是一个独立的结构化知识单元？
   └─ 是 → 继续判断：
       ├─ 抽象概念/方法论 → 10_Wiki_Grid/Concepts/
       ├─ 具体的人/公司/地点 → 10_Wiki_Grid/Entities/
       ├─ 跨领域洞察 → 10_Wiki_Grid/Syntheses/
       └─ 底层人生观/决策框架 → 10_Wiki_Grid/00_Anchors/
   └─ 不是 → 继续 ⑤

⑤ 这是系统配置或说明文档？
   └─ 是 → 根目录（opencode.md / soul_profile.md）或 .opencode/ 或 备注/
   └─ 不是 → 和我聊聊，我帮你决定。
```

---

## 八、禁止事项

| ❌ 不要做 | ✅ 应该做 |
|----------|---------|
| 手动修改 `00_Raw_Materials/` 中的文件 | 用 `ingest` 指令让 AI 重新写入更正版本 |
| 直接把灵感写到 `10_Wiki_Grid/` 里（不按模板） | 先和 AI 讨论，然后用 `digest` 蒸馏后再沉淀 |
| 手动移动 `30_Daily_Stream/` 中的年份文件夹 | 等 `yearly_crystallize.py` 或告诉 AI 帮你移 |
| 删除旧对话日志 | 它们会被自动冰封到 Archives 中，不占检索权重 |
| 在脚本里硬编码路径 | 改 `paths.json`，所有脚本自动生效 |

---

*本备忘由 AI 维护。如果你发现分类规则需要调整，直接告诉我。*
