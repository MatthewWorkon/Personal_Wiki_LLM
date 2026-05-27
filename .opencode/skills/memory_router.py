#!/usr/bin/env python3
"""
memory_router.py — 记忆路由门闸

核心职责：
    在 hybrid_search.py 检索之前，根据用户查询内容判断应触发哪些数据层。
    防止大模型在数十年的海量数据中迷失。

路由逻辑：
    - 常规查询 → 仅热 + 温层（不触发冷层）
    - 包含年份/历史引用 → 热 + 温 + 指定年份的冷层
    - 系统维护查询 → 全量扫描

输入：用户查询字符串
输出：{ "hot": bool, "warm": bool, "cold": bool, "cold_years": [int] }
"""

import json
import os
import re
from typing import Optional


VAULT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def extract_year_references(query: str) -> list[int]:
    """
    从查询中提取显式的年份引用。
    匹配模式：20XX 年、"2024"、"我 2024 年" 等。
    """
    years = re.findall(r"(20\d{2})\s*年", query)
    return [int(y) for y in years]


def route(query: str) -> dict:
    """
    根据查询内容返回数据层激活指令。
    """
    result = {
        "hot": True,
        "warm": True,
        "cold": False,
        "cold_years": [],
    }

    years = extract_year_references(query)
    if years:
        result["cold"] = True
        result["cold_years"] = years

    # 维护类指令：如 "reindex"、"healthcheck"
    maintain_triggers = ["healthcheck", "reindex", "全量重建", "索引重建"]
    if any(t in query.lower() for t in maintain_triggers):
        result["cold"] = True
        # 不指定年份 = 全量

    return result


if __name__ == "__main__":
    import sys
    q = sys.argv[1] if len(sys.argv) > 1 else ""
    print(json.dumps(route(q), ensure_ascii=False, indent=2))
