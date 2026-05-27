#!/usr/bin/env python3
"""
ripple_weave.py — 多文件联动"涟漪效应"调度

核心职责：
    当 Wiki_Grid 中某个概念卡片被修改后，自动识别所有引用该概念的文件，
    并按需触发相应的更新操作（双链更新、内容同步、关联节点提醒）。

触发场景：
    - 概念合并（graph_entropy.py 触发）
    - 概念重命名
    - 概念卡片重大改写
    - 实体卡片关键属性变更

输入：被修改的节点 ID（文件名）+ 修改类型
输出：受影响的文件列表 + 自动执行的更新操作日志

依赖：ast_patcher.py（执行具体文件修改）
"""

import json
import os
import glob as glob_mod
from typing import Optional


VAULT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def find_backlinks(target_file: str) -> list[str]:
    """
    扫描全库，找到所有包含 [[target_file]] 双链引用的文件。
    """
    backlinks = []
    wiki_root = os.path.join(VAULT_ROOT, "10_Wiki_Grid")
    all_files = glob_mod.glob(f"{wiki_root}/**/*.md", recursive=True)

    target_name = os.path.splitext(os.path.basename(target_file))[0]
    pattern = f"[[{target_name}]]"

    for fpath in all_files:
        if fpath == target_file:
            continue
        with open(fpath, "r", encoding="utf-8") as f:
            if pattern in f.read():
                backlinks.append(fpath)

    return backlinks


def on_concept_merged(old_name: str, new_name: str) -> dict:
    """
    概念合并后的涟漪处理：
    1. 找到所有引用旧概念的文件
    2. 将 [[旧概念]] 替换为 [[新概念]]
    """
    # TODO: 实现全库双链替换
    return {"updated_files": [], "failed_files": []}


def on_concept_renamed(old_name: str, new_name: str) -> dict:
    """概念重命名时的涟漪处理。"""
    return on_concept_merged(old_name, new_name)


def on_major_rewrite(concept_file: str) -> list[str]:
    """
    重大改写后，找出所有关联文件，标记为"可能需要复审"。
    """
    # TODO: 实现关联分析、标记逻辑
    return []


def ripple(trigger_file: str, change_type: str) -> dict:
    """
    主入口：根据修改类型调度对应的涟漪操作。
    """
    # TODO: 实现分发逻辑
    return {"status": "not_implemented"}


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: ripple_weave.py <trigger_file> <change_type>")
        sys.exit(1)
    result = ripple(sys.argv[1], sys.argv[2])
    print(json.dumps(result, ensure_ascii=False, indent=2))
