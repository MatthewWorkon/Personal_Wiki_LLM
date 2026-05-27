#!/usr/bin/env python3
"""
corpus_ingest.py — 语料分析引擎

核心职责：
    当用户查询外部知识源（演讲、论文、书籍、文章等）时，
    执行「研究 → 归档 → 分析 → 分发」全流程：
    1. 源材料写入 00_Raw_Materials/{Books|Papers|WebClips}/
    2. 提取概念 → 10_Wiki_Grid/Concepts/（按 Template_Concept.md）
    3. 提取实体 → 10_Wiki_Grid/Entities/  （按 Template_Entity.md）
    4. 跨领域合成 → 10_Wiki_Grid/Syntheses/
    5. 底层框架 → 10_Wiki_Grid/00_Anchors/

触发方式（会话窗驱动，无需 API）：
    自然语言：
        "乔布斯2009年的演讲是什么？"
        "帮我分析《思考，快与慢》的核心框架"
        "这篇关于 LLM 记忆机制的文章，整理入库"
    显式指令：
        ingest <查询>      → 研究归档 + 分析分发
        ingest raw <查询>   → 仅归档到 Raw_Materials

输出路由规则（语料类型 → 目录映射）：
    演讲/论文/学术      → Papers/
    书籍/著作            → Books/
    网页/新闻/博客       → WebClips/
    提取的概念           → Concepts/   (Template_Concept.md)
    提取的实体           → Entities/   (Template_Entity.md)
    跨领域洞察           → Syntheses/
    底层思维范式         → 00_Anchors/

依赖：paths.json、20_Templates/、ast_patcher.py（写入时校验）
"""

import json
import os
import re
from datetime import date
from typing import Optional


VAULT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def load_config() -> dict:
    with open(os.path.join(VAULT_ROOT, ".opencode", "config.json"), "r") as f:
        return json.load(f)


def load_paths() -> dict:
    with open(os.path.join(VAULT_ROOT, ".opencode", "paths.json"), "r") as f:
        return json.load(f)


def load_template(template_name: str) -> str:
    path = os.path.join(VAULT_ROOT, "20_Templates", template_name)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


# ── 语料类型路由 ──────────────────────────────────────────────

CONTENT_TYPE_ROUTES = {
    "speech":     "Papers",
    "paper":      "Papers",
    "academic":   "Papers",
    "talk":       "Papers",
    "book":       "Books",
    "chapter":    "Books",
    "article":    "WebClips",
    "news":       "WebClips",
    "blog":       "WebClips",
    "webpage":    "WebClips",
    "interview":  "Papers",
    "documentation": "Books",
}


def route_raw_material(content_type: str) -> str:
    """
    根据内容类型返回 Raw_Materials 下的目标子目录名。

    Args:
        content_type: 内容类型关键词（speech, book, article, paper...）

    Returns:
        "Books" | "Papers" | "WebClips"
    """
    key = content_type.lower().strip()
    subdir = CONTENT_TYPE_ROUTES.get(key, "WebClips")
    raw_root = os.path.join(VAULT_ROOT, "00_Raw_Materials", subdir)
    os.makedirs(raw_root, exist_ok=True)
    return raw_root


def classify_content_type(query: str) -> str:
    """
    根据查询内容自动推断语料类型。
    规则：关键词匹配 → 返回类型标签。
    """
    q = query.lower()
    if any(w in q for w in ["演讲", "speech", "talk", "keynote", "commencement"]):
        return "speech"
    if any(w in q for w in ["论文", "paper", "journal", "学术"]):
        return "paper"
    if any(w in q for w in ["书", "book", "chapter", "章节", "第.*章"]):
        return "book"
    if any(w in q for w in ["新闻", "news", "报道"]):
        return "news"
    if any(w in q for w in ["访谈", "interview", "对话"]):
        return "interview"
    return "article"


# ── 卡片渲染（模板驱动） ──────────────────────────────────────

def render_concept_card(data: dict) -> str:
    """
    按 Template_Concept.md 渲染概念卡片 Markdown。

    Required data keys:
        title, definition, elaboration, cases, counterpoints,
        relations, source

    Optional:
        tags, aliases, maturity, confidence
    """
    title = data.get("title", "未命名概念")
    today = date.today().isoformat()

    yaml_tags = json.dumps(data.get("tags", []), ensure_ascii=False)
    yaml_aliases = json.dumps(data.get("aliases", []), ensure_ascii=False)
    yaml_parents = json.dumps(data.get("parent_concepts", []), ensure_ascii=False)
    yaml_children = json.dumps(data.get("child_concepts", []), ensure_ascii=False)
    yaml_entities = json.dumps(data.get("related_entities", []), ensure_ascii=False)

    relations_md = "\n".join(
        f"- {r}" for r in data.get("relations", [])
    ) or "- "

    source_md = "\n".join(
        f"- {s}" for s in data.get("sources", [])
    ) or "- "

    return f"""---
title: "{title}"
file_type: concept
created: {today}
updated: {today}
tags: {yaml_tags}
aliases: {yaml_aliases}
parent_concepts: {yaml_parents}
child_concepts: {yaml_children}
related_entities: {yaml_entities}
maturity: {data.get("maturity", "seedling")}
confidence: {data.get("confidence", 0.5)}
---

# {title}

## 一句话定义
{data.get("definition", "（待补充）")}

## 核心阐述
{data.get("elaboration", "（待补充）")}

## 关键论据与案例
{data.get("cases", "（待补充）")}

## 反面观点与边界
{data.get("counterpoints", "（待补充）")}

## 与其他概念的关联
{relations_md}

## 历史演变
<!-- 由 conflict_resolver.py 维护 -->

## 参考来源
{source_md}
"""


def render_entity_card(data: dict) -> str:
    """
    按 Template_Entity.md 渲染实体卡片 Markdown。

    Required data keys:
        title, entity_type, background, timeline, relevance, source
    """
    title = data.get("title", "未命名实体")
    today = date.today().isoformat()

    yaml_tags = json.dumps(data.get("tags", []), ensure_ascii=False)
    yaml_aliases = json.dumps(data.get("aliases", []), ensure_ascii=False)
    yaml_concepts = json.dumps(data.get("related_concepts", []), ensure_ascii=False)
    yaml_entities = json.dumps(data.get("related_entities", []), ensure_ascii=False)

    timeline_md = "\n".join(
        f"| {t.get('date', '')} | {t.get('event', '')} | {t.get('notes', '')} |"
        for t in data.get("timeline", [])
    ) or "| | | |"

    related_md = "\n".join(
        f"- {e}" for e in data.get("related_entities", [])
    ) or "- "

    source_md = "\n".join(
        f"- {s}" for s in data.get("sources", [])
    ) or "- "

    entity_type = data.get("entity_type", "person")

    return f"""---
title: "{title}"
file_type: entity
entity_type: {entity_type}
created: {today}
updated: {today}
tags: {yaml_tags}
aliases: {yaml_aliases}
related_concepts: {yaml_concepts}
related_entities: {yaml_entities}
---

# {title}

## 基本信息
| 属性 | 值 |
|------|-----|
| 类型 | {entity_type} |
| 首次记录 | {today} |
| 最后一次更新 | {today} |

## 背景与简介
{data.get("background", "（待补充）")}

## 关键事件时间线
| 日期 | 事件 | 备注 |
|------|------|------|
{timeline_md}

## 与我的知识体系的关联
{data.get("relevance", "（待补充）")}

## 相关实体
{related_md}

## 参考来源
{source_md}
"""


def render_synthesis(data: dict) -> str:
    """
    渲染跨领域合成报告。
    """
    title = data.get("title", "未命名合成")
    today = date.today().isoformat()

    sources_md = "\n".join(
        f"- [[{s}]]" for s in data.get("source_nodes", [])
    ) or "- "

    return f"""---
title: "{title}"
file_type: synthesis
created: {today}
updated: {today}
tags: {json.dumps(data.get("tags", []), ensure_ascii=False)}
source_nodes: {json.dumps(data.get("source_nodes", []), ensure_ascii=False)}
---

# {title}

## 合成摘要
{data.get("summary", "（待补充）")}

## 跨领域连接
{data.get("connections", "（待补充）")}

## 源节点
{sources_md}
"""


# ── 卡片写入 ──────────────────────────────────────────────────

def validate_card(content: str, card_type: str) -> list[str]:
    """返回缺失项列表，为空表示通过。"""
    missing = []

    if card_type == "concept":
        required_fields = ["title", "file_type", "created"]
        required_headings = ["一句话定义", "核心阐述"]
    elif card_type == "entity":
        required_fields = ["title", "file_type", "entity_type", "created"]
        required_headings = ["基本信息", "背景与简介"]
    else:
        return []

    for field in required_fields:
        if not re.search(rf"{field}:", content[:500]):
            missing.append(f"frontmatter.{field}")

    for heading in required_headings:
        if f"## {heading}" not in content and f"# {heading}" not in content:
            missing.append(f"heading.{heading}")

    return missing


def write_card(content: str, directory: str, filename: str) -> str:
    """
    写入卡片到指定目录。自动创建目录。
    Returns: 写入的文件完整路径。
    """
    os.makedirs(directory, exist_ok=True)
    safe_name = filename.replace("/", "-").replace(":", "-")
    if not safe_name.endswith(".md"):
        safe_name += ".md"
    filepath = os.path.join(directory, safe_name)

    if os.path.exists(filepath):
        base = safe_name.replace(".md", "")
        i = 1
        while os.path.exists(filepath):
            filepath = os.path.join(directory, f"{base}_{i}.md")
            i += 1

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"  [written] {filepath}")
    return filepath


def write_concept(data: dict) -> str:
    """渲染概念卡片并写入 Concepts/ 目录。"""
    content = render_concept_card(data)
    missing = validate_card(content, "concept")
    if missing:
        print(f"  [warn] Concept card missing: {', '.join(missing)}")

    grid_root = os.path.join(VAULT_ROOT, "10_Wiki_Grid", "Concepts")
    filename = data.get("title", "unnamed").replace(" ", "_")
    return write_card(content, grid_root, filename)


def write_entity(data: dict) -> str:
    """渲染实体卡片并写入 Entities/ 目录。"""
    content = render_entity_card(data)
    missing = validate_card(content, "entity")
    if missing:
        print(f"  [warn] Entity card missing: {', '.join(missing)}")

    grid_root = os.path.join(VAULT_ROOT, "10_Wiki_Grid", "Entities")
    filename = data.get("title", "unnamed").replace(" ", "_")
    return write_card(content, grid_root, filename)


def write_synthesis(data: dict) -> str:
    """渲染合成报告并写入 Syntheses/ 目录。"""
    content = render_synthesis(data)
    grid_root = os.path.join(VAULT_ROOT, "10_Wiki_Grid", "Syntheses")
    filename = data.get("title", "unnamed").replace(" ", "_")
    return write_card(content, grid_root, filename)


def write_anchor(data: dict) -> str:
    """写入 00_Anchors/ 目录（直接写入内容，不经过模板渲染）。"""
    grid_root = os.path.join(VAULT_ROOT, "10_Wiki_Grid", "00_Anchors")
    filename = data.get("title", "unnamed").replace(" ", "_")
    return write_card(data.get("content", ""), grid_root, filename)


def write_raw_material(content: str, content_type: str, filename: str) -> str:
    """写入原始素材到 Raw_Materials 对应子目录。"""
    subdir = route_raw_material(content_type)
    return write_card(content, subdir, filename)


# ── 产出报告 ──────────────────────────────────────────────────

def ingest_report(files: dict) -> str:
    """
    生成可读的语料入库报告。
    files = { "raw": [path], "concepts": [path], "entities": [path], ... }
    """
    lines = ["## 语料入库报告\n"]
    labels = {
        "raw": "原始素材 (00_Raw_Materials)",
        "concepts": "概念卡片 (10_Wiki_Grid/Concepts)",
        "entities": "实体卡片 (10_Wiki_Grid/Entities)",
        "syntheses": "合成报告 (10_Wiki_Grid/Syntheses)",
        "anchors": "思维锚点 (10_Wiki_Grid/00_Anchors)",
    }

    for key, label in labels.items():
        items = files.get(key, [])
        if items:
            lines.append(f"### {label} ({len(items)})")
            for p in items:
                name = os.path.basename(p).replace(".md", "")
                lines.append(f"- [[{name}]]")
        else:
            lines.append(f"### {label} — 无")
        lines.append("")

    return "\n".join(lines)


# ── CLI ────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: corpus_ingest.py <command> [args]")
        print()
        print("Commands:")
        print("  route <content_type>         → Print target Raw_Materials subdir")
        print("  render concept <json_file>   → Render concept card to stdout")
        print("  render entity <json_file>    → Render entity card to stdout")
        print("  write concept <json_file>    → Write concept card to Wiki_Grid")
        print("  write entity <json_file>     → Write entity card to Wiki_Grid")
        print("  write raw <json_file>        → Write raw material")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "route":
        ct = sys.argv[2] if len(sys.argv) > 2 else "article"
        print(route_raw_material(ct))

    elif cmd == "render":
        if len(sys.argv) < 3:
            print("Usage: corpus_ingest.py render <concept|entity> [json_file]", file=sys.stderr)
            sys.exit(1)
        card_type = sys.argv[2]
        json_path = sys.argv[3] if len(sys.argv) > 3 else None
        if json_path:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = {"title": "测试卡片"}

        if card_type == "concept":
            print(render_concept_card(data))
        elif card_type == "entity":
            print(render_entity_card(data))
        else:
            print(f"Unknown type: {card_type}", file=sys.stderr)
            sys.exit(1)

    elif cmd == "write":
        if len(sys.argv) < 3:
            print("Usage: corpus_ingest.py write <concept|entity|raw> <json_file>", file=sys.stderr)
            sys.exit(1)
        card_type = sys.argv[2]
        json_path = sys.argv[3]
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if card_type == "concept":
            write_concept(data)
        elif card_type == "entity":
            write_entity(data)
        elif card_type == "raw":
            write_raw_material(
                data.get("content", ""),
                data.get("content_type", "article"),
                data.get("filename", "untitled.md"),
            )
        else:
            print(f"Unknown type: {card_type}", file=sys.stderr)
            sys.exit(1)

    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        sys.exit(1)
