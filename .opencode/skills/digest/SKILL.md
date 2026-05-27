---
name: digest
description: Use when user types 'digest', 'digest week', 'digest month', or 'digest YYYY-MM-DD'. Reads today's chat log from 30_Daily_Stream/{year}/{month}/Logs/YYYY-MM-DD_Chat.md, performs 3-module distillation (core insights, deep knowledge expansion, ripple mapping), and writes the resulting Digest to 30_Daily_Stream/{year}/{month}/Digests/YYYY-MM-DD_Digest.md. No API key required—the AI performs distillation directly in the session window.
---

# Digest — 日刊蒸馏技能

## Trigger
User types any of:
- `digest` — generate today's digest
- `digest YYYY-MM-DD` — generate for a specific date
- `digest week` — fill all missing digests in the past 7 days
- `digest month` — fill all missing digests in the past 30 days

## Workflow

### Step 1: Read Chat Log
Read `30_Daily_Stream/{year}/{month}/Logs/YYYY-MM-DD_Chat.md`. The path follows `paths.json` convention: `30_Daily_Stream/{year}/{MM_Mon}/Logs/`.

If no chat log exists for the date, tell the user: "No chat logs found for YYYY-MM-DD. Have you chatted today?"

### Step 2: Perform 3-Module Distillation
Read the template at `20_Templates/Template_Digest.md` for the output structure, then distill the chat log into three modules:

**Module 1 — 核心灵感捕获 (Core Insights)**
Condense the most inspiring points from today's conversation into 1-3 one-sentence insights. Each should be a standalone, reusable insight.

**Module 2 — 知识深度拓展 (Deep Knowledge Expansion)**
For the core technical/design/framework topics discussed, DO NOT just summarize. Perform academic-level or engineering-level deep analysis from fundamentals to advanced. Include:
- Theoretical foundations (cite relevant concepts, frameworks, or papers)
- Practical implications and engineering tradeoffs
- Step-by-step reasoning that makes the insight transferable

**Module 3 — 涟漪映射建议 (Ripple Mapping Suggestions)**
Analyze connections between today's insights and existing Wiki nodes. For each connection, specify:
- Which Wiki node it relates to (use `[[node name]]` format)
- The nature of the relationship (strengthens, questions, new connection)
- Concrete edit suggestions

### Step 3: Write Digest
Write to `30_Daily_Stream/{year}/{month}/Digests/YYYY-MM-DD_Digest.md`.

The file MUST follow the Frontmatter structure from `20_Templates/Template_Digest.md`:
```yaml
---
title: "YYYY-MM-DD 思想日刊"
file_type: digest
digest_type: daily
created: YYYY-MM-DD
period_start: YYYY-MM-DD
period_end: YYYY-MM-DD
source_logs: ["filename.md"]
key_insights: ["insight1", "insight2", "insight3"]
emerging_concepts: ["concept1", "concept2"]
mood_summary: "summary"
---
```

Required sections: `## 核心灵感捕获`, `## 知识深度拓展`, `## 涟漪映射建议`, `## 精神状态摘要`, `## 待办与后续`, `## 原始对话索引`.

### Step 4: Report
Tell the user what was generated and where it was written. List the key insights for a quick preview.

### Batch Mode (digest week / digest month)
For each missing date in the range:
1. Check if digest already exists (skip if so)
2. Check if chat log exists (skip if not)
3. Generate digest
4. Report: `Generated N missing digests.`

The helper script `.opencode/skills/eod_digest.py` has `prepare` and `write` subcommands that can assist with reading logs and writing output, but the distillation itself should be done by the AI in-session.

## Output Quality Standards
- Insights must be standalone and reusable — a person reading 6 months later should understand the insight without context
- Deep dives must go beyond summarization — add analytical value not present in the raw chat
- Ripple suggestions must be actionable — specify exactly what card to create/update and why
- Mood summary should be 1 sentence, capturing emotional tone + focus area + energy level
