---
name: ingest
description: Use when user asks about external knowledge sources—speeches, papers, books, articles, news. Triggered by queries like '乔布斯2009年的演讲是什么' or '帮我分析《思考，快与慢》' or 'ingest <query>'. Researches source material, archives it to 00_Raw_Materials/{Books|Papers|WebClips}/, extracts concepts to 10_Wiki_Grid/Concepts/ (following Template_Concept.md), extracts entities to 10_Wiki_Grid/Entities/ (following Template_Entity.md), and writes cross-domain syntheses to 10_Wiki_Grid/Syntheses/. No API key required.
---

# Ingest — 语料分析入库技能

## Trigger
Natural language queries about external knowledge sources:
- "乔布斯2009年的演讲是什么？"
- "帮我分析《思考，快与慢》的核心框架"
- "这篇关于LLM记忆机制的文章，整理入库"
- Explicit: `ingest <query>` or `ingest raw <query>`

## Content Type Routing

Determine the content type and route to the correct Raw_Materials subdirectory:

| Content Type | Keywords | Target Directory |
|---|---|---|
| Speech/Talk/Keynote | 演讲, speech, talk, keynote, commencement | `00_Raw_Materials/Papers/` |
| Academic Paper | 论文, paper, journal, 学术 | `00_Raw_Materials/Papers/` |
| Book/Chapter | 书, book, chapter, 章节 | `00_Raw_Materials/Books/` |
| News/Article/Blog | 新闻, news, 报道, article, blog | `00_Raw_Materials/WebClips/` |
| Interview | 访谈, interview, 对话 | `00_Raw_Materials/Papers/` |
| Default | (anything else) | `00_Raw_Materials/WebClips/` |

## Workflow

### Step 1: Research & Write Raw Material
- Retrieve/find the source material content
- Write complete content to `00_Raw_Materials/{subdir}/{title}.md`
- Use descriptive Chinese filenames for Chinese content, English for English content
- If exact source material is unavailable, write a comprehensive knowledge-base synthesis labeled as such

### Step 2: Extract Concepts
For each distinct concept/idea/theory found in the source material:
- Read template: `20_Templates/Template_Concept.md`
- Create a concept card following exactly the Frontmatter structure:
  ```yaml
  title, file_type: concept, created, updated, tags, aliases,
  parent_concepts, child_concepts, related_entities,
  maturity: seedling, confidence: 0.0-1.0
  ```
- Required sections: `## 一句话定义`, `## 核心阐述`, `## 关键论据与案例`, `## 反面观点与边界`, `## 与其他概念的关联`, `## 参考来源`
- Write to `10_Wiki_Grid/Concepts/{title}.md`
- Use `[[double bracket links]]` for cross-references to other concepts and entities

### Step 3: Extract Entities
For each person, company, place, product, or disease entity:
- Read template: `20_Templates/Template_Entity.md`
- Required fields: `title, file_type: entity, entity_type, created, updated`
- Required sections: `## 基本信息`, `## 背景与简介`, `## 关键事件时间线`, `## 与我的知识体系的关联`, `## 参考来源`
- Write to `10_Wiki_Grid/Entities/{title}.md`

### Step 4: Cross-Domain Synthesis (optional)
If the source material connects multiple concepts in a non-obvious way:
- Write a synthesis report to `10_Wiki_Grid/Syntheses/{title}.md`
- Include: summary, cross-domain connections, source nodes list

### Step 5: Report
Output a structured report showing all created files:
```
## 语料入库报告
### 原始素材 (00_Raw_Materials/Papers) — 1
- [[filename]]
### 概念卡片 (10_Wiki_Grid/Concepts) — N
- [[concept1]], [[concept2]], ...
### 实体卡片 (10_Wiki_Grid/Entities) — N
- [[entity1]], ...
### 合成报告 (10_Wiki_Grid/Syntheses) — N
- [[synthesis1]], ...
```

## Content Quality Standards
- Concepts must be atomic (one idea per card, Zettelkasten style)
- Definitions must be precise, 1-2 sentences, standalone
- Elaborations should be 300-500 words of substantive explanation
- Always include counterpoints/limitations for every concept
- Always cross-link to other existing concepts and entities using `[[links]]`
- Mark confidence level (0.0-1.0) to indicate how well-verified the concept is

## The `ingest raw` Variant
If user explicitly says `ingest raw <query>`, ONLY write to Raw_Materials without extracting concepts/entities. Useful for quick archival without analysis.

## Helper Script
`.opencode/skills/corpus_ingest.py` provides utility functions:
- `python3 .opencode/skills/corpus_ingest.py route <type>` — prints target directory
- `python3 .opencode/skills/corpus_ingest.py render concept <json>` — renders concept card from JSON
- `python3 .opencode/skills/corpus_ingest.py write concept <json>` — writes concept card to disk

However, for most ingest tasks, the AI should write files directly (like the digest workflow) rather than relying on the script.
