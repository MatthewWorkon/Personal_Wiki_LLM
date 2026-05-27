#!/usr/bin/env python3
"""
reminder_check.py — 周期提醒引擎

核心职责：
    在每次会话启动时（或手动触发）检查所有周期性任务的完成状态，
    向用户输出友好的提醒清单，防止遗忘日刊蒸馏、锚点结晶、灵魂更新等任务。

触发方式：
    自动：每天首次会话，morning-sync 执行之后自动运行
    手动：随时输入 remind

检测项目（6 项）：
    1. 日刊蒸馏 — 今天有 Chat Log 但无匹配 Digest？
    2. 锚点结晶 — 距上次更新 00_Anchors/ 是否超过 14 天？
    3. 灵魂更新 — soul_profile.md 超过 7 天未修改？
    4. 年度结晶 — 是否 12 月且去年未归档？
    5. 图谱熵控 — Wiki_Grid 卡片增长是否超过阈值？
    6. 日志归档 — 上月 Logs 是否未清理标记？

依赖：config.json、paths.json
"""

import json
import os
import glob as glob_mod
from datetime import date, datetime, timedelta
from typing import Optional


VAULT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def load_config() -> dict:
    with open(os.path.join(VAULT_ROOT, ".opencode", "config.json"), "r") as f:
        return json.load(f)


def load_paths() -> dict:
    with open(os.path.join(VAULT_ROOT, ".opencode", "paths.json"), "r") as f:
        return json.load(f)


def get_intervals() -> dict:
    """从 config 读取提醒间隔（天），缺失用默认值。"""
    config = load_config()
    defaults = {
        "digest_daily": 1,
        "anchor_weekly": 14,
        "soul_updater_weekly": 7,
        "yearly_crystallize_yearly": 365,
        "graph_entropy_monthly": 30,
    }
    return config.get("reminder", {}).get("intervals", defaults)


def days_since(filepath: str) -> Optional[int]:
    """文件距今天多少天。文件不存在返回 None。"""
    if not os.path.exists(filepath):
        return None
    mtime = datetime.fromtimestamp(os.path.getmtime(filepath)).date()
    return (date.today() - mtime).days


def latest_mod(directory: str, pattern: str = "*.md") -> Optional[int]:
    """目录下最新匹配文件的距今天数。目录为空返回 None。"""
    if not os.path.isdir(directory):
        return None
    files = glob_mod.glob(os.path.join(directory, pattern))
    if not files:
        return None
    latest = max(datetime.fromtimestamp(os.path.getmtime(f)).date() for f in files)
    return (date.today() - latest).days


def count_files(directory: str, pattern: str = "*.md") -> int:
    if not os.path.isdir(directory):
        return 0
    return len(glob_mod.glob(os.path.join(directory, pattern)))


# ── 6 项检测 ──────────────────────────────────────────────────

def check_digest() -> dict:
    """检查今天有没有生成 Digest。"""
    today = date.today()
    paths = load_paths()
    daily = paths["layers"]["daily_stream"]
    year = str(today.year)
    month = today.strftime("%m_%b")
    log_dir = os.path.join(VAULT_ROOT, daily["logs_pattern"].format(year=year, month=month))
    digest_dir = os.path.join(VAULT_ROOT, daily["digests_pattern"].format(year=year, month=month))
    digest_file = os.path.join(digest_dir, f"{today.isoformat()}_Digest.md")

    has_logs = count_files(log_dir, f"{today.isoformat()}_Chat.md") > 0
    has_digest = os.path.exists(digest_file)

    if not has_logs:
        return {"task": "日刊蒸馏", "status": "quiet", "message": "今天没有对话记录"}
    if has_digest:
        return {"task": "日刊蒸馏", "status": "ok", "message": "今日日刊已生成"}
    return {"task": "日刊蒸馏", "status": "warn", "message": "今天有对话但还没生成日刊 → 输入 digest"}


def check_anchor() -> dict:
    """检查距上次锚点更新是否超过阈值。"""
    interval = get_intervals().get("anchor_weekly", 14)
    d = latest_mod(os.path.join(VAULT_ROOT, "10_Wiki_Grid", "00_Anchors"))
    if d is None:
        return {"task": "锚点结晶", "status": "warn", "message": "00_Anchors/ 为空，建议运行一次 → 输入 anchor"}
    if d > interval:
        return {"task": "锚点结晶", "status": "warn", "message": f"距上次更新 {d} 天（阈值 {interval} 天）→ 输入 anchor"}
    return {"task": "锚点结晶", "status": "ok", "message": f"距上次更新 {d} 天，下次提醒在 {interval - d} 天后"}


def check_soul_updater() -> dict:
    """检查 soul_profile.md 是否过期。"""
    interval = get_intervals().get("soul_updater_weekly", 7)
    d = days_since(os.path.join(VAULT_ROOT, "soul_profile.md"))
    if d is None:
        return {"task": "灵魂更新", "status": "warn", "message": "soul_profile.md 不存在"}
    if d > interval:
        return {"task": "灵魂更新", "status": "warn", "message": f"soul_profile.md 距上次更新 {d} 天（阈值 {interval} 天）"}
    return {"task": "灵魂更新", "status": "ok", "message": f"距上次更新 {d} 天"}


def check_yearly_crystallize() -> dict:
    """检查年底是否需要归档。"""
    today = date.today()
    if today.month != 12:
        return {"task": "年度结晶", "status": "ok", "message": "非年底，无需操作"}

    last_year = today.year - 1
    archives_dir = os.path.join(VAULT_ROOT, "30_Daily_Stream", "Archives", str(last_year))
    if os.path.isdir(archives_dir):
        return {"task": "年度结晶", "status": "ok", "message": f"{last_year} 年已归档"}
    return {"task": "年度结晶", "status": "warn", "message": f"{last_year} 年尚未归档 → 需要运行 yearly_crystallize"}


def check_graph_entropy() -> dict:
    """检查 Wiki_Grid 卡片增长是否需要熵控扫描。"""
    interval = get_intervals().get("graph_entropy_monthly", 30)
    concept_count = count_files(os.path.join(VAULT_ROOT, "10_Wiki_Grid", "Concepts"))
    entity_count = count_files(os.path.join(VAULT_ROOT, "10_Wiki_Grid", "Entities"))
    total = concept_count + entity_count

    if total < 10:
        return {"task": "图谱熵控", "status": "quiet", "message": f"仅 {total} 张卡片，无需扫描"}

    d = latest_mod(os.path.join(VAULT_ROOT, "10_Wiki_Grid", "Concepts"))
    if d is None:
        d = 0
    if d > interval:
        return {"task": "图谱熵控", "status": "warn", "message": f"{total} 张卡片，距上次更新 {d} 天（阈值 {interval} 天）→ 考虑运行 graph_entropy.py"}
    return {"task": "图谱熵控", "status": "ok", "message": f"{total} 张卡片，距上次扫描 {d} 天"}


def check_log_cleanup() -> dict:
    """检查上月 Logs 是否需要标记。"""
    today = date.today()
    if today.day > 7:
        return {"task": "日志归档", "status": "quiet", "message": "非月初，无需检查"}

    last_month = today.replace(day=1) - timedelta(days=1)
    log_dir = os.path.join(
        VAULT_ROOT, "30_Daily_Stream",
        str(last_month.year), last_month.strftime("%m_%b"), "Logs",
    )
    log_count = count_files(log_dir)
    if log_count == 0:
        return {"task": "日志归档", "status": "ok", "message": "上月无日志"}
    return {"task": "日志归档", "status": "info", "message": f"上月 {log_count} 个日志文件完好，暂不归档（年底统一处理）"}


def check_weekly_report() -> dict:
    """检查上周周报是否已生成。仅在周一提醒。"""
    today = date.today()
    if today.weekday() != 0:
        return {"task": "周报生成", "status": "quiet", "message": "非周一，无需检查"}

    last_monday = today - timedelta(days=7)
    last_sunday = today - timedelta(days=1)
    iso = last_monday.isocalendar()
    week_label = f"{iso[0]}-W{iso[1]:02d}"
    report_file = os.path.join(VAULT_ROOT, "04_Weekly_Report", str(iso[0]), f"{week_label}_Weekly.md")

    if os.path.exists(report_file) and os.path.getsize(report_file) > 500:
        return {"task": "周报生成", "status": "ok", "message": f"上周周报 {week_label} 已生成"}

    return {"task": "周报生成", "status": "warn", "message": f"上周周报 {week_label} 未生成 → 输入 weekly last"}


# ── 输出渲染 ──────────────────────────────────────────────────

def render(checks: list[dict]) -> str:
    """将检测结果渲染为可读的提醒清单。"""
    lines = []
    warn_count = 0

    lines.append("📋 周期提醒 " + date.today().isoformat())
    lines.append("─" * 37)

    icons = {"ok": "✓", "warn": "⚠️", "info": "ℹ", "quiet": "·"}
    for c in checks:
        icon = icons.get(c["status"], "?")
        lines.append(f"  {icon}  {c['task']} — {c['message']}")
        if c["status"] == "warn":
            warn_count += 1

    lines.append("─" * 37)
    if warn_count == 0:
        lines.append("全部就绪。输入 remind 随时查看。")
    else:
        lines.append(f"需要处理: {warn_count} 项。输入 remind 随时查看。")

    return "\n".join(lines)


# ── 主入口 ────────────────────────────────────────────────────

def run_reminder() -> str:
    """执行全部 6 项周期检测，返回渲染后的提醒文本。"""
    checks = [
        check_digest(),
        check_anchor(),
        check_soul_updater(),
        check_yearly_crystallize(),
        check_graph_entropy(),
        check_log_cleanup(),
        check_weekly_report(),
    ]
    return render(checks)


if __name__ == "__main__":
    print(run_reminder())
