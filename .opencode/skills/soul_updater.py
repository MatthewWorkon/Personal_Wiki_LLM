#!/usr/bin/env python3
"""
soul_updater.py — 灵魂锚点周更新技能

核心职责：
    每周日晚上自动运行，读取本周所有 Digests，对 soul_profile.md 进行
    非破坏性、渐进式的覆盖重写。

更新策略：
    1. 读取本周（过去 7 天）所有 Digests
    2. 提炼出本周核心思想动态，写入「近期思想动态」区
    3. 评估当前状态是否需要更新：目标、焦虑、思维模型、价值观
    4. 若需更新 → 重写「当前状态」顶部，旧版本追加到「历史版本」区
    5. 检查 soul_profile.md 的历史版本深度，超过 2 年的迁移至归档文件

输入：无（自动读取 config 配置）
输出：更新后的 soul_profile.md 路径 + 变更摘要

依赖：config.json, ast_patcher.py, paths.json
"""

import json
import os
import glob as glob_mod
from datetime import date, timedelta
from typing import Optional


VAULT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def load_config() -> dict:
    with open(os.path.join(VAULT_ROOT, ".opencode", "config.json"), "r") as f:
        return json.load(f)


def load_paths() -> dict:
    with open(os.path.join(VAULT_ROOT, ".opencode", "paths.json"), "r") as f:
        return json.load(f)


def get_weekly_digests(end_date: Optional[date] = None) -> list[str]:
    """
    获取过去 7 天的所有 Digest 文件路径。
    """
    if end_date is None:
        end_date = date.today()
    start_date = end_date - timedelta(days=7)

    paths = load_paths()
    digest_pattern = os.path.join(
        VAULT_ROOT,
        paths["layers"]["daily_stream"]["digests_pattern"].format(
            year="*", month="*"
        ),
    )
    digest_pattern = os.path.join(digest_pattern, "*_Digest.md")
    all_digests = glob_mod.glob(digest_pattern, recursive=False)

    weekly = []
    for d in all_digests:
        try:
            basename = os.path.basename(d)
            file_date = date.fromisoformat(basename[:10])
            if start_date <= file_date <= end_date:
                weekly.append(d)
        except (ValueError, IndexError):
            continue

    return sorted(weekly)


def analyze_weekly_digests(digest_files: list[str]) -> dict:
    """
    分析本周 Digests，提取：
    - 核心思想动态摘要
    - 是否需要更新当前状态（目标、焦虑、思维模型等）
    - 新涌现的持续主题
    """
    # TODO: 读取 Digest 内容，调用 LLM 分析
    return {
        "weekly_summary": "",
        "state_updates": {},
        "emerging_themes": [],
    }


def update_soul_profile(analysis: dict) -> str:
    """
    将分析结果写入 soul_profile.md：
    1. 更新「近期思想动态」段落
    2. 如有状态变化，重写「当前状态」并追加旧版本
    """
    # TODO: 使用 ast_patcher.py 实现精确写入
    return os.path.join(VAULT_ROOT, "soul_profile.md")


def archive_old_versions(soul_profile_path: str) -> int:
    """
    检查 soul_profile.md 底部历史版本数量。
    将超过 2 年的旧版本迁移至 soul_profile_archive/YYYY.md。
    返回迁移的版本数量。
    """
    # TODO: 实现历史版本分割与归档
    return 0


def run_weekly_update(end_date: Optional[date] = None) -> dict:
    """
    主入口：执行完整的周更新流程。
    """
    if end_date is None:
        end_date = date.today()

    digests = get_weekly_digests(end_date)
    if not digests:
        return {"status": "skipped", "reason": "No digests found in the past 7 days"}

    analysis = analyze_weekly_digests(digests)
    updated_path = update_soul_profile(analysis)
    archived_count = archive_old_versions(updated_path)

    return {
        "status": "updated",
        "soul_profile": updated_path,
        "digests_analyzed": len(digests),
        "state_changes": bool(analysis["state_updates"]),
        "archived_versions": archived_count,
    }


if __name__ == "__main__":
    result = run_weekly_update()
    print(json.dumps(result, ensure_ascii=False, indent=2))
