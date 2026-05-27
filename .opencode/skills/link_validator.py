#!/usr/bin/env python3
"""
link_validator.py — 破损链接扫描与自动修复引擎

核心职责：
    扫描全库所有 .md 文件中的 [[双链]] 引用，交叉对比文件系统，
    识别破损链接和空壳链接，自动按模板创建最小占位卡片到正确的目录。

问题场景：
    1. 破碎链接：[[引用]] 存在但目标文件不存在
    2. 空壳链接：目标文件存在但内容完全空白（无 Frontmatter、无正文）
    3. 根目录空壳：Obsidian 默认在根目录生成了无归属的空白文件

自动修复：
    - 破碎/空壳 → 按名称推断类型 → 在正确的子目录创建最小模板卡片
    - 根目录空壳 → 移到正确子目录并注入最小模板
    - 已有内容的文件 → 跳过，绝不覆写

路径推断规则：
    名称包含 "Steve Jobs" "Tim Cook" 等人名 → Entities/
    名称包含 "Apple" "Google" 等公司 → Entities/
    名称包含 "北京" "斯坦福" 等地名 → Entities/
    名称以大写缩写为主 "BI-RADS" "HELLP" → Concepts/
    继承引用来源所在目录 → 源在 Entities/ → 目标→ Entities/
    默认 → Concepts/

触发方式：
    fixlinks            扫描 + 自动修复
    fixlinks dry        仅扫描，输出报告不修复

依赖：paths.json、20_Templates/
"""

import json
import os
import re
import glob as glob_mod
import shutil
from datetime import date
from typing import Optional


VAULT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def load_paths() -> dict:
    with open(os.path.join(VAULT_ROOT, ".opencode", "paths.json"), "r") as f:
        return json.load(f)


# ── 文件扫描 ──────────────────────────────────────────────────

def all_md_files() -> list[str]:
    """返回 vault 中所有 .md 文件的绝对路径（排除系统目录和说明文档）。"""
    exclude_dirs = {".obsidian", "GitHub同步", "Templates", ".opencode", ".git"}
    result = []
    for root, dirs, files in os.walk(VAULT_ROOT, topdown=True):
        # 跳过排除目录及其子目录
        rel = os.path.relpath(root, VAULT_ROOT)
        parts = rel.split(os.sep)
        if any(p in exclude_dirs for p in parts):
            continue
        for f in files:
            if f.endswith(".md"):
                result.append(os.path.join(root, f))
    return result


def should_scan(filepath: str) -> bool:
    """判断文件是否应该被扫描 wikilinks。
    排除系统配置、说明文档、模板文件（它们的 [[链接]] 是示例，不是真正的知识引用）。"""
    rel = os.path.relpath(filepath, VAULT_ROOT)
    parts = rel.split(os.sep)

    exclude_prefixes = (
        ".opencode", "20_Templates", "备注", "soul_profile_archive",
    )
    for p in parts:
        if p in exclude_prefixes:
            return False

    # 排除根目录的系统文件
    basename = os.path.basename(filepath)
    if basename in ("opencode.md", "soul_profile.md"):
        return False

    return True


def file_exists_by_name(name: str) -> Optional[str]:
    """搜索 vault 中是否存在名为 <name>.md 的文件。返回路径或 None。"""
    name_clean = name.strip()
    for f in all_md_files():
        basename = os.path.splitext(os.path.basename(f))[0]
        if basename == name_clean:
            return f
    return None


def extract_wikilinks(filepath: str) -> list[str]:
    """提取文件中所有 [[链接名]]（不含前缀路径部分）。"""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    links = re.findall(r"\[\[([^\]|#]+)(?:[|#][^\]]+)?\]\]", content)
    # 过滤：去掉文件路径引用（含 .md .py .json 后缀的）
    return [l.strip() for l in links
            if not any(l.strip().endswith(ext) for ext in (".md", ".py", ".json", ".js"))]


def is_file_empty(filepath: str) -> bool:
    """判断 .md 文件是否几乎为空（无实质性内容）。"""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    stripped = content.strip()
    if not stripped:
        return True
    # 去掉 frontmatter 后再判断
    body = re.sub(r"^---\n.*?\n---\n", "", stripped, flags=re.DOTALL).strip()
    return len(body) < 20  # 少于 20 字符视为空壳


def is_in_root(filepath: str) -> bool:
    """判断文件是否在 vault 根目录下。"""
    return os.path.dirname(os.path.abspath(filepath)) == VAULT_ROOT


# ── 路径推断 ──────────────────────────────────────────────────

ENTITY_PERSON_KEYWORDS = [
    "jobs", "cook", "musk", "gates", "bezos", "obama", "trump", "乔布斯",
    "马斯克", "盖茨", "奥巴马",
]

ENTITY_COMPANY_KEYWORDS = [
    "apple", "google", "microsoft", "amazon", "meta", "tesla", "openai",
    "苹果", "谷歌", "微软",
]

ENTITY_PLACE_KEYWORDS = [
    "斯坦福", "硅谷", "北京", "上海", "纽约", "酒吧",
    "stanford", "silicon valley",
]


def infer_card_type(link_name: str, source_path: str = "") -> str:
    """
    根据链接名称和引用来源推断目标卡片类型。
    Returns: "concept" | "entity" | "anchor"
    """
    name_lower = link_name.lower()

    # 已知实体模式
    if any(kw in name_lower for kw in ENTITY_PERSON_KEYWORDS):
        return "entity"
    if any(kw in name_lower for kw in ENTITY_COMPANY_KEYWORDS):
        return "entity"
    if any(kw in name_lower for kw in ENTITY_PLACE_KEYWORDS):
        return "entity"

    # 继承来源路径
    if "Entities" in source_path:
        return "entity"
    if "Anchors" in source_path or "00_Anchors" in source_path:
        return "anchor"

    return "concept"


def get_target_dir(card_type: str) -> str:
    """根据卡片类型返回目标目录。"""
    mapping = {
        "concept": os.path.join(VAULT_ROOT, "10_Wiki_Grid", "Concepts"),
        "entity": os.path.join(VAULT_ROOT, "10_Wiki_Grid", "Entities"),
        "anchor": os.path.join(VAULT_ROOT, "10_Wiki_Grid", "00_Anchors"),
    }
    d = mapping.get(card_type, mapping["concept"])
    os.makedirs(d, exist_ok=True)
    return d


# ── 最小模板 ──────────────────────────────────────────────────

def render_minimal_concept(title: str) -> str:
    today = date.today().isoformat()
    return f"""---
title: "{title}"
file_type: concept
created: {today}
updated: {today}
tags: []
aliases: []
parent_concepts: []
child_concepts: []
related_entities: []
maturity: seedling
confidence: 0.5
---

# {title}

## 一句话定义
（待补充 — 由 link_validator.py 自动生成的最小占位卡片）

## 核心阐述
（待补充）

## 关键论据与案例
（待补充）

## 反面观点与边界
（待补充）

## 与其他概念的关联
<!-- 已有以下页面引用此概念： -->
（待补充）

## 参考来源
（待补充）
"""


def render_minimal_entity(title: str) -> str:
    today = date.today().isoformat()
    return f"""---
title: "{title}"
file_type: entity
entity_type: person
created: {today}
updated: {today}
tags: []
aliases: []
related_concepts: []
related_entities: []
---

# {title}

## 基本信息
| 属性 | 值 |
|------|-----|
| 首次记录 | {today} |

## 背景与简介
（待补充 — 由 link_validator.py 自动生成的最小占位卡片）

## 关键事件时间线
| 日期 | 事件 | 备注 |
|------|------|------|
| | | |

## 与我的知识体系的关联
<!-- 已有以下页面引用此实体： -->
（待补充）

## 相关实体
（待补充）

## 参考来源
（待补充）
"""


def render_minimal_anchor(title: str) -> str:
    today = date.today().isoformat()
    return f"""---
title: "{title}"
file_type: anchor
created: {today}
updated: {today}
tags: []
source_weeks: []
related_concepts: []
confidence: 0.3
---

# {title}

## 一句话定义
（待补充 — 由 link_validator.py 自动生成的最小占位卡片）

## 核心框架
（待补充）

## 来源与演化
（待补充）

## 适用边界
（待补充）

## 关联概念
（待补充）

## 本周更新
（待补充）
"""


RENDERERS = {
    "concept": render_minimal_concept,
    "entity": render_minimal_entity,
    "anchor": render_minimal_anchor,
}


# ── 扫描与修复 ────────────────────────────────────────────────

def scan_broken_links() -> list[dict]:
    """
    扫描全库，找出所有破损链接和空壳链接。
    返回 [{"link_name": ..., "source_file": ..., "source_path": ..., "issue": "broken"|"empty"|"empty_in_root", "existing_file": ...|None}]
    """
    all_files = all_md_files()
    issues = []

    for src in all_files:
        if not should_scan(src):
            continue
        links = extract_wikilinks(src)
        for link in links:
            # 跳过自引用和特殊链接
            src_name = os.path.splitext(os.path.basename(src))[0]
            if link == src_name:
                continue

            existing = file_exists_by_name(link)
            if existing is None:
                # 破碎链接 — 文件不存在
                issues.append({
                    "link_name": link,
                    "source_file": os.path.basename(src),
                    "source_path": src,
                    "issue": "broken",
                    "existing_file": None,
                })
            elif is_file_empty(existing):
                issue_type = "empty_in_root" if is_in_root(existing) else "empty"
                issues.append({
                    "link_name": link,
                    "source_file": os.path.basename(src),
                    "source_path": src,
                    "issue": issue_type,
                    "existing_file": existing,
                })

    # 按 link_name 去重（保留第一个出现的 source）
    seen = set()
    unique = []
    for item in issues:
        if item["link_name"] not in seen:
            seen.add(item["link_name"])
            unique.append(item)
    return unique


def fix_link(item: dict, dry_run: bool = False) -> dict:
    """
    修复单个破损/空壳链接。
    返回 {"action": "created"|"moved"|"skipped", "path": ...}
    """
    name = item["link_name"]
    card_type = infer_card_type(name, item["source_path"])
    target_dir = get_target_dir(card_type)
    target_path = os.path.join(target_dir, f"{name}.md")

    # 如果目标路径已存在且有内容，跳过
    if os.path.exists(target_path) and not is_file_empty(target_path):
        return {"action": "skipped", "path": target_path,
                "reason": "target already exists with content"}

    if dry_run:
        return {"action": "would_create", "path": target_path, "type": card_type}

    # 如果有空壳文件，先删除（或内容不足 20 字的也视为空壳）
    if item["existing_file"]:
        if is_file_empty(item["existing_file"]):
            os.remove(item["existing_file"])

    # 渲染并写入
    renderer = RENDERERS.get(card_type, RENDERERS["concept"])
    content = renderer(name)
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(content)

    return {"action": "created", "path": target_path, "type": card_type}


def run_fixlinks(dry_run: bool = False) -> dict:
    """主入口：扫描并修复全部破损链接。"""
    issues = scan_broken_links()

    if not issues:
        return {"status": "clean", "issues": 0, "fixed": 0, "details": []}

    details = []
    for item in issues:
        result = fix_link(item, dry_run=dry_run)
        details.append({
            "link": item["link_name"],
            "source": item["source_file"],
            "issue": item["issue"],
            **result,
        })

    return {
        "status": "dry_run" if dry_run else "fixed",
        "issues": len(issues),
        "fixed": sum(1 for d in details if d["action"] in ("created", "moved")),
        "skipped": sum(1 for d in details if d["action"] == "skipped"),
        "details": details,
    }


def format_report(result: dict) -> str:
    """将修复结果格式化为可读报告。"""
    if result["status"] == "clean":
        return "✓ 全库链接完整，无需修复。"

    lines = [
        f"{'[DRY RUN] ' if result['status'] == 'dry_run' else ''}破损链接扫描结果",
        f"发现问题: {result['issues']} 个",
        f"可修复: {result['fixed']} 个",
        f"已跳过: {result['skipped']} 个（目标已有内容）",
        "",
    ]

    type_map = {"concept": "概念卡片", "entity": "实体卡片", "anchor": "思维锚点"}

    for d in result["details"]:
        action = d["action"]
        if action == "created":
            lines.append(f"  ✓ 创建 {type_map.get(d.get('type', ''), '')}: [[{d['link']}]]")
            lines.append(f"      来源: {d['source']}  →  {d['path']}")
        elif action == "would_create":
            lines.append(f"  ○ 将创建: [[{d['link']}]] ({d.get('type', '')})")
            lines.append(f"      来源: {d['source']}")
        elif action == "skipped":
            lines.append(f"  — 跳过: [[{d['link']}]] (已有内容)")
        elif action == "moved":
            lines.append(f"  → 移动: [[{d['link']}]] → {d['path']}")
        lines.append("")

    return "\n".join(lines)


# ── CLI ────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    dry = len(sys.argv) > 1 and sys.argv[1] == "dry"
    result = run_fixlinks(dry_run=dry)
    print(format_report(result))
