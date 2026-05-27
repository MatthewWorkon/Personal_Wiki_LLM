#!/usr/bin/env python3
"""
hybrid_search.py — 混合向量检索技能

核心职责：
    响应用户查询时，按 70/20/10 权重从热/温/冷三层数据中检索上下文。

检索策略（由 config.json 的 retrieval.default_weights 控制）：
    - 热层 (70%)：soul_profile.md + 近 14 天 Digests
    - 温层 (20%)：10_Wiki_Grid/ 全量结构化知识
    - 冷层 (10%)：30_Daily_Stream/Archives/（仅当用户明确提及历史时间时触发）

输入：用户查询字符串
输出：合并后的加权上下文片段列表

依赖：memory_router.py（数据分流）、paths.json（路径配置）
"""

import json
import os
from datetime import datetime, timedelta
from typing import Optional


VAULT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def load_paths() -> dict:
    with open(os.path.join(VAULT_ROOT, ".opencode", "paths.json"), "r") as f:
        return json.load(f)


def load_config() -> dict:
    with open(os.path.join(VAULT_ROOT, ".opencode", "config.json"), "r") as f:
        return json.load(f)


def search_hot(query: str, days: int = 14) -> list[str]:
    """
    检索热层数据：soul_profile.md + 近 N 天 Digests。
    返回匹配的上下文片段列表。
    """
    # TODO: 实现向量/关键词检索逻辑
    return []


def search_warm(query: str) -> list[str]:
    """
    检索温层数据：10_Wiki_Grid/ 全量。
    返回匹配的上下文片段列表。
    """
    # TODO: 实现向量/关键词检索逻辑
    return []


def search_cold(query: str, year_filter: Optional[int] = None) -> list[str]:
    """
    检索冷层数据：30_Daily_Stream/Archives/。
    仅在 year_filter 非空时触发。
    返回匹配的上下文片段列表。
    """
    if year_filter is None:
        return []
    # TODO: 实现向量/关键词检索逻辑
    return []


def merge_and_rank(
    hot_results: list[str],
    warm_results: list[str],
    cold_results: list[str],
    weights: dict,
) -> str:
    """
    按权重合并三层检索结果，拼接为最终上下文。
    """
    # TODO: 实现加权排序、去重、拼接逻辑
    return ""


def hybrid_search(query: str, year_filter: Optional[int] = None) -> str:
    """
    主入口：执行混合检索，返回拼接后的上下文。
    """
    config = load_config()
    weights = config["retrieval"]["default_weights"]
    hot_days = config["retrieval"]["hot_window_days"]

    hot = search_hot(query, days=hot_days)
    warm = search_warm(query)
    cold = search_cold(query, year_filter=year_filter)

    return merge_and_rank(hot, warm, cold, weights)


if __name__ == "__main__":
    import sys
    query = sys.argv[1] if len(sys.argv) > 1 else ""
    result = hybrid_search(query)
    print(result)
