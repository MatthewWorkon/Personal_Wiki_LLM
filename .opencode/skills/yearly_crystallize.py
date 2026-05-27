#!/usr/bin/env python3
"""
yearly_crystallize.py — 年度结晶与冰封技能

核心职责：
    每年底（或手动触发），扫描过去 12 个月的 Daily Stream，
    将反复出现的灵感和被验证过的框架抽离并沉淀到 10_Wiki_Grid，
    然后将整年的时间流文件夹移入 Archives 冰封区。

执行流程：
    1. 扫描目标年份所有月度文件夹下的 Digests
    2. 提取反复出现（出现次数 >= 3）的主题/概念/框架
    3. 对每个高频主题生成或更新 Wiki_Grid 中的对应卡片
    4. 将目标年份的 30_Daily_Stream/{year}/ 目录移入 Archives/
    5. 生成年度结晶报告

输入：目标年份（默认上一年）
输出：结晶报告 { concepts_created, concepts_updated, archived }

依赖：ast_patcher.py, conflict_resolver.py, graph_entropy.py, paths.json
"""

import json
import os
import shutil
import glob as glob_mod
from datetime import date
from typing import Optional
from collections import Counter


VAULT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def load_config() -> dict:
    with open(os.path.join(VAULT_ROOT, ".opencode", "config.json"), "r") as f:
        return json.load(f)


def load_paths() -> dict:
    with open(os.path.join(VAULT_ROOT, ".opencode", "paths.json"), "r") as f:
        return json.load(f)


def get_year_digests(year: int) -> list[str]:
    """
    获取指定年份所有 Digests 的文件路径。
    """
    paths = load_paths()
    daily_root = os.path.join(VAULT_ROOT, paths["layers"]["daily_stream"]["root"])
    year_dir = os.path.join(daily_root, str(year))

    if not os.path.isdir(year_dir):
        return []

    return sorted(glob_mod.glob(f"{year_dir}/**/*_Digest.md", recursive=True))


def extract_recurring_themes(digest_files: list[str], min_frequency: int = 3) -> list[dict]:
    """
    扫描所有 Digest，提取出现频率 >= min_frequency 的主题。
    返回 [{"theme": "...", "frequency": N, "source_digests": [...]}, ...]
    """
    # TODO: 解析 Digest Frontmatter 中的 key_insights 和 emerging_concepts，
    # 统计频率，调用 LLM 聚类
    return []


def crystallize_theme(theme: dict, target_year: int) -> str:
    """
    将一个高频主题沉淀到 Wiki_Grid。
    - 若 Wiki_Grid 中已有对应卡片 → 更新「历史演变」段落
    - 若无 → 按 Template_Concept.md 创建新卡片
    返回创建/更新的文件路径。
    """
    # TODO: 实现卡片创建/更新逻辑
    return ""


def archive_year(year: int) -> str:
    """
    将整年的 Daily Stream 文件夹移入 Archives/。
    如果 Archives/ 下已存在则追加后缀。
    返回归档后的路径。
    """
    paths = load_paths()
    daily_root = os.path.join(VAULT_ROOT, paths["layers"]["daily_stream"]["root"])
    archives_root = os.path.join(VAULT_ROOT, paths["layers"]["daily_stream"]["archives"])

    year_dir = os.path.join(daily_root, str(year))
    if not os.path.isdir(year_dir):
        raise FileNotFoundError(f"Year directory not found: {year_dir}")

    target = os.path.join(archives_root, str(year))
    if os.path.exists(target):
        target = os.path.join(archives_root, f"{year}_v2")

    shutil.move(year_dir, target)
    return target


def yearly_crystallize(year: Optional[int] = None) -> dict:
    """
    主入口：执行完整年度结晶流程。
    """
    if year is None:
        year = date.today().year - 1

    digests = get_year_digests(year)
    if not digests:
        return {"status": "skipped", "reason": f"No digests found for {year}"}

    themes = extract_recurring_themes(digests)

    crystallized = []
    for theme in themes:
        path = crystallize_theme(theme, year)
        if path:
            crystallized.append(path)

    archive_path = archive_year(year)

    return {
        "status": "completed",
        "year": year,
        "digests_analyzed": len(digests),
        "themes_found": len(themes),
        "concepts_crystallized": len(crystallized),
        "crystallized_paths": crystallized,
        "archived_to": archive_path,
    }


if __name__ == "__main__":
    import sys
    year = int(sys.argv[1]) if len(sys.argv) > 1 else None
    result = yearly_crystallize(year)
    print(json.dumps(result, ensure_ascii=False, indent=2))
