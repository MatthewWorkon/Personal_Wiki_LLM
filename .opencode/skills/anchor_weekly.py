#!/usr/bin/env python3
"""
anchor_weekly.py — 周度锚点生成技能

核心职责：
    每 2-4 周自动运行（或手动触发），扫描近期 Digests 中的持续性思维模式，
    识别已稳定反复出现的底层框架，结晶为 10_Wiki_Grid/00_Anchors/ 中的锚点卡片。

触发方式（会话窗驱动，类 digest 模式）：
    anchor              → 扫描近 4 周 Digest，准备分析上下文
    anchor write <json> → 写入锚点卡片

锚点 vs 概念的区别：
    概念 (Concepts/)   → 原子化的具体知识（如 "Memory Consolidation"）
    锚点 (00_Anchors/) → 跨越多个领域的底层思维范式/人生框架
                         （如 "信息热力学思维模型"、"多因素终末通路分析框架"）

锚点的特征（满足 2+ 条即为候选）：
    1. 在 3 周以上的 Digest 中反复出现
    2. 跨越至少 2 个不同领域/主题
    3. 是"看问题的方式"而非"问题的答案"
    4. 用户明确表达过 "这是一种底层框架/思维模型"

输出：00_Anchors/{title}.md

依赖：paths.json
"""

import json
import os
import glob as glob_mod
import re
from datetime import date, timedelta
from typing import Optional


VAULT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def load_config() -> dict:
    with open(os.path.join(VAULT_ROOT, ".opencode", "config.json"), "r") as f:
        return json.load(f)


def load_paths() -> dict:
    with open(os.path.join(VAULT_ROOT, ".opencode", "paths.json"), "r") as f:
        return json.load(f)


# ── 文件扫描 ──────────────────────────────────────────────────

def get_digests_in_range(start_date: date, end_date: date) -> list[str]:
    """获取指定日期范围内的所有 Digest 文件。"""
    all_digests = glob_mod.glob(
        os.path.join(VAULT_ROOT, "30_Daily_Stream", "**", "*_Digest.md"),
        recursive=True,
    )
    in_range = []
    for d in all_digests:
        try:
            basename = os.path.basename(d)
            file_date = date.fromisoformat(basename[:10])
            if start_date <= file_date <= end_date:
                in_range.append(d)
        except (ValueError, IndexError):
            continue
    return sorted(in_range)


def list_anchors() -> list[dict]:
    """列出 00_Anchors/ 下所有已有锚点卡片。"""
    anchors_dir = os.path.join(VAULT_ROOT, "10_Wiki_Grid", "00_Anchors")
    if not os.path.isdir(anchors_dir):
        return []

    anchors = []
    for f in sorted(os.listdir(anchors_dir)):
        if f.endswith(".md"):
            filepath = os.path.join(anchors_dir, f)
            with open(filepath, "r", encoding="utf-8") as fh:
                content = fh.read()
            title = os.path.splitext(f)[0]
            anchors.append({
                "title": title,
                "filepath": filepath,
                "preview": content[:300],
            })
    return anchors


def read_digest_body(filepath: str) -> str:
    """读取 Digest 正文（跳过 Frontmatter）。"""
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()
    body_match = re.search(r"---\n.*?\n---\n(.*)", text, re.DOTALL)
    if body_match:
        return body_match.group(1).strip()
    return text.strip()


# ── 锚点卡片渲染 ──────────────────────────────────────────────

ANCHOR_TEMPLATE = """---
title: "{title}"
file_type: anchor
created: {created}
updated: {updated}
tags: {tags}
source_weeks: {source_weeks}
related_concepts: {related_concepts}
confidence: {confidence}
---

# {title}

## 一句话定义
{definition}

## 核心框架
{framework}

## 来源与演化
{evolution}

## 适用边界
{boundaries}

## 关联概念
{concept_links}

## 本周更新
{weekly_update}
"""


def render_anchor(data: dict) -> str:
    """
    渲染锚点卡片 Markdown。
    所需字段：title, definition, framework, evolution, boundaries
    """
    today = date.today().isoformat()
    return ANCHOR_TEMPLATE.format(
        title=data.get("title", "未命名锚点"),
        created=data.get("created", today),
        updated=today,
        tags=json.dumps(data.get("tags", []), ensure_ascii=False),
        source_weeks=json.dumps(data.get("source_weeks", []), ensure_ascii=False),
        related_concepts=json.dumps(data.get("related_concepts", []), ensure_ascii=False),
        confidence=data.get("confidence", 0.5),
        definition=data.get("definition", "（待补充）"),
        framework=data.get("framework", "（待补充）"),
        evolution=data.get("evolution", "（待补充）"),
        boundaries=data.get("boundaries", "（待补充）"),
        concept_links="\n".join(
            f"- [[{c}]]" for c in data.get("related_concepts", [])
        ) or "- ",
        weekly_update=data.get("weekly_update", "（本周无新增内容）"),
    )


def write_anchor(data: dict) -> str:
    """渲染并写入锚点卡片。返回文件路径。"""
    content = render_anchor(data)
    anchors_dir = os.path.join(VAULT_ROOT, "10_Wiki_Grid", "00_Anchors")
    os.makedirs(anchors_dir, exist_ok=True)

    safe_name = data.get("title", "unnamed").replace("/", "-").replace(":", "-")
    if not safe_name.endswith(".md"):
        safe_name += ".md"
    filepath = os.path.join(anchors_dir, safe_name)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"  [anchor] Written: {filepath}")
    return filepath


def update_anchor(filepath: str, weekly_update: str) -> str:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    today = date.today().isoformat()
    weekly_section = f"\n\n### {today}\n{weekly_update}"

    # 更新 frontmatter 中的 updated 字段
    content = re.sub(r"updated: .*", f"updated: {today}", content)

    # 替换空占位符 或 在已有更新区顶部追加
    if "（本周无新增内容）" in content:
        content = content.replace(
            "（本周无新增内容）",
            weekly_section.strip(),
        )
    elif "## 本周更新" in content:
        content = content.replace(
            "## 本周更新\n",
            f"## 本周更新\n{weekly_section}\n",
        )
    else:
        content += f"\n\n## 本周更新\n{weekly_section}\n"

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"  [anchor] Updated: {filepath}")
    return filepath


# ── 会话窗准备（类 digest prepare 模式） ─────────────────────

ANCHOR_ANALYSIS_PROMPT = """你是本地 Wiki 的首席知识架构师。请阅读以下近期思想纪要和已有锚点清单，
识别是否有正在稳定形成的"底层思维框架"可以结晶为锚点。

锚点的定义：
    不是具体的知识点（那属于 Concepts/），而是跨越多个领域的"看问题的视角"。
    是一个可重用的分析框架、一种思维习惯、一条底层人生原则。

锚点的判断标准（满足 2+ 条即为候选）：
    1. 在 3 周以上的 Digest 中反复出现
    2. 跨越至少 2 个不同领域/主题
    3. 是"如何思考"的框架，而非"思考的结果"
    4. 用户明确表达过 "这是一种底层框架/思维模型"

对每个候选锚点，请输出 JSON：
{
  "anchors": [
    {
      "action": "create",
      "title": "锚点标题",
      "definition": "一句话定义这个框架",
      "framework": "框架的完整描述（300-500字）",
      "evolution": "这个框架在Digest中的演化轨迹",
      "boundaries": "这个框架不适用于哪些场景",
      "tags": ["tag1", "tag2"],
      "related_concepts": ["概念1", "概念2"],
      "confidence": 0.8
    }
  ]
}"""


def prepare_anchor_context(weeks: int = 4) -> str:
    """
    准备锚点分析上下文：近期 Digest 正文 + 已有锚点清单。
    供会话窗 AI 读取后执行分析。
    """
    today = date.today()
    start_date = today - timedelta(weeks=weeks)
    digests = get_digests_in_range(start_date, today)
    anchors = list_anchors()

    if not digests:
        print(f"[anchor] No digests found in the past {weeks} weeks.", end="")
        return ""

    lines = [
        "<!-- ANCHOR_PREPARE_BEGIN -->",
        f"<!-- date_range: {start_date.isoformat()} ~ {today.isoformat()} -->",
        f"<!-- digest_count: {len(digests)} -->",
        f"<!-- existing_anchors: {len(anchors)} -->",
        "",
        ANCHOR_ANALYSIS_PROMPT,
        "",
    ]

    # 已有锚点清单
    if anchors:
        lines.append("## 已有锚点")
        for a in anchors:
            lines.append(f"- [[{a['title']}]]")
        lines.append("")

    # 近期 Digest 正文
    lines.append("## 近期思想纪要")
    for d in digests:
        date_str = os.path.basename(d)[:10]
        body = read_digest_body(d)
        lines.append(f"### {date_str}")
        lines.append(body[:1500])  # 每个 Digest 最多取 1500 字
        lines.append("")

    lines.append("<!-- ANCHOR_PREPARE_END -->")
    output = "\n".join(lines)
    print(output)
    return output


# ── CLI ────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: anchor_weekly.py <command> [args]")
        print()
        print("Commands:")
        print("  anchor              Prepare analysis context (past 4 weeks)")
        print("  anchor N            Prepare context (past N weeks)")
        print("  list                List existing anchors")
        print("  write <json_file>   Create a new anchor from JSON")
        print("  update <title> <text>  Append weekly update to existing anchor")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "list":
        anchors = list_anchors()
        if anchors:
            for a in anchors:
                print(f"  [[{a['title']}]]")
        else:
            print("  (No anchors yet)")

    elif cmd == "write":
        if len(sys.argv) < 3:
            print("Usage: anchor_weekly.py write <json_file>", file=sys.stderr)
            sys.exit(1)
        with open(sys.argv[2], "r", encoding="utf-8") as f:
            data = json.load(f)
        write_anchor(data)

    elif cmd == "update":
        if len(sys.argv) < 4:
            print("Usage: anchor_weekly.py update <title> <update_text>", file=sys.stderr)
            sys.exit(1)
        title = sys.argv[2]
        text = sys.argv[3]
        anchors_dir = os.path.join(VAULT_ROOT, "10_Wiki_Grid", "00_Anchors")
        filepath = os.path.join(anchors_dir, f"{title}.md")
        if not os.path.exists(filepath):
            filepath = os.path.join(anchors_dir, f"{title}")  # try without .md
            if not os.path.exists(filepath):
                print(f"[anchor] Anchor not found: {title}", file=sys.stderr)
                sys.exit(1)
        update_anchor(filepath, text)

    else:
        # 数字 = weeks 参数
        try:
            weeks = int(cmd)
            prepare_anchor_context(weeks=weeks)
        except ValueError:
            # 默认为 anchor 指令
            prepare_anchor_context(weeks=4)
