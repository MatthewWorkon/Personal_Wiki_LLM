#!/usr/bin/env python3
"""
weekly_report.py — 周刊风格周报引擎

核心职责：
    每周自动（或手动触发）读取本周所有日刊，生成具有评论刊物风格的
    周报：叙事驱动的回顾分析 + 趋势预测的下阶段展望。

文风参照：
    美国评论刊物（The New Yorker / The Atlantic）的叙事传统——
    有观点、有温度、有叙事弧线。不是行政周报，是思想周刊。

周报位置：
    04_Weekly_Report/{year}/{year}-W{week}_Weekly.md
    与 30_Daily_Stream 平级，时间流之外独立的时间分析层。

触发方式：
    weekly           → 生成本周周一至今天的周报
    weekly last      → 生成上周完整周报
    weekly W21       → 补生成指定 ISO 周的周报
    自动             → 周一 reminded 检测上周周报缺失时提醒

依赖：paths.json、config.json
"""

import json
import os
import re
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


# ── ISO 周计算 ────────────────────────────────────────────────

def get_week_dates(iso_week: Optional[str] = None, mode: str = "current") -> tuple[date, date, str]:
    """
    返回 (period_start, period_end, week_label)。

    mode:
        "current" — 本周周一至今天
        "last"    — 上周周一至周日
        "specific" — iso_week 指定的完整周一至周日
    """
    today = date.today()

    if mode == "last":
        today = today - timedelta(days=7)

    if mode == "specific" and iso_week:
        year = int(iso_week[:4]) if len(iso_week) >= 7 else today.year
        week = int(iso_week[-2:]) if len(iso_week) >= 5 else int(iso_week)
        jan4 = date(year, 1, 4)
        first_monday = jan4 - timedelta(days=jan4.weekday())
        target_monday = first_monday + timedelta(weeks=week - 1)
        target_sunday = target_monday + timedelta(days=6)
        label = f"{year}-W{week:02d}"
        return target_monday, target_sunday, label

    monday = today - timedelta(days=today.weekday())
    if mode == "last":
        sunday = monday + timedelta(days=6)
    else:
        sunday = today  # 本周到今天

    iso = today.isocalendar()
    label = f"{iso[0]}-W{iso[1]:02d}"
    return monday, sunday, label


def get_week_filepath(week_label: str) -> str:
    year = week_label[:4]
    folder = os.path.join(VAULT_ROOT, "04_Weekly_Report", year)
    os.makedirs(folder, exist_ok=True)
    return os.path.join(folder, f"{week_label}_Weekly.md")


def digests_exist_in_range(start: date, end: date) -> list[str]:
    """获取范围内所有 Digest 文件。"""
    digests = glob_mod.glob(os.path.join(VAULT_ROOT, "30_Daily_Stream", "**", "*_Digest.md"), recursive=True)
    result = []
    for d in digests:
        try:
            basename = os.path.basename(d)
            d_date = date.fromisoformat(basename[:10])
            if start <= d_date <= end:
                result.append(d)
        except (ValueError, IndexError):
            continue
    return sorted(result)


# ── 本周数据收集 ──────────────────────────────────────────────

def collect_week_stats(start: date, end: date) -> dict:
    """收集本周的统计数据。"""
    digests = digests_exist_in_range(start, end)

    # 读取所有日刊的 insights
    all_insights = []
    for d in digests:
        with open(d, "r", encoding="utf-8") as f:
            content = f.read()
            match = re.search(r"key_insights:\s*\[(.*?)\]", content, re.DOTALL)
            if match:
                for line in match.group(1).splitlines():
                    insight = line.strip().strip('",').strip('"')
                    if insight and len(insight) > 10:
                        all_insights.append(insight)

    # 统计新增卡片（本周修改的文件）
    concepts_new = []
    entities_new = []
    syntheses_new = []
    raw_new = []

    for subdir, target in [("Concepts", concepts_new), ("Entities", entities_new),
                            ("Syntheses", syntheses_new)]:
        d = os.path.join(VAULT_ROOT, "10_Wiki_Grid", subdir)
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            if f.endswith(".md"):
                fpath = os.path.join(d, f)
                mtime = date.fromtimestamp(os.path.getmtime(fpath))
                if start <= mtime <= end:
                    target.append(f.replace(".md", ""))

    for raw_sub in ["Books", "Papers", "WebClips"]:
        d = os.path.join(VAULT_ROOT, "00_Raw_Materials", raw_sub)
        if not os.path.isdir(d):
            continue
        for f in os.listdir(d):
            if f.endswith(".md"):
                fpath = os.path.join(d, f)
                mtime = date.fromtimestamp(os.path.getmtime(fpath))
                if start <= mtime <= end:
                    raw_new.append(f"{raw_sub}/{f.replace('.md', '')}")

    return {
        "digest_count": len(digests),
        "insights": all_insights,
        "concepts_added": concepts_new,
        "entities_added": entities_new,
        "syntheses_added": syntheses_new,
        "raw_added": raw_new,
        "total_cards": len(concepts_new) + len(entities_new) + len(syntheses_new),
    }


# ── AI Prompt（会话窗用） ─────────────────────────────────────

WRITING_PROMPT = """你是 My_LLM_Wiki 的首席思想编辑。请根据本周全部日刊内容和统计数据，
撰写一份具有美国评论刊物风格的周报。

评论刊物参照：
    叙事驱动的深度专栏（The New Yorker / The Atlantic 的周刊传统），
    中文参照：财新/端传媒的深度叙事节奏、《读库》的个人化知识书写。

写作准则：
1. 不要用 bullet points 组织主要叙事——用段落。标题是一个判断句，不是一个标签。
2. 开篇要有一个钩子：本周最关键的发现、最意外的转折、或一个让你停下来思考的瞬间。
3. "深度聚焦"要展示推理过程，而不只是结论。读者想看到你是怎么从 A 走到 B 的。
4. "边缘地带"要坦诚——记录不完美的想法、未成形的灵感、标记了但还没开挖的地点。
5. 结尾的展望要用推测语气（"可能会、也许应该"），不要写成待办清单。
6. 使用第一人称反思口吻——这是周刊的思想日记，不是公司报告。"我"可以出现。
7. 数据统计独立成段，不嵌入叙事。保持叙事的流畅感。
8. 语言：有观点的、精确的中文。不要翻译腔。可以有偶尔的比喻，但不要泛滥。

输出格式：直接输出完整的周报 Markdown（含 Frontmatter），不要 JSON 包装。"""


def prepare_context(iso_week: Optional[str] = None, mode: str = "current") -> str:
    """准备周报写作上下文：Prompt + 日刊摘要 + 统计数据。"""
    start, end, label = get_week_dates(iso_week, mode)
    filepath = get_week_filepath(label)

    if os.path.exists(filepath) and os.path.getsize(filepath) > 500:
        print(f"[weekly] Report already exists: {filepath}")
        return ""

    digests = digests_exist_in_range(start, end)
    if not digests:
        print(f"[weekly] No digests found in {start} ~ {end}")
        return ""

    stats = collect_week_stats(start, end)

    lines = [
        "<!-- WEEKLY_PREPARE_BEGIN -->",
        f"<!-- week: {label} -->",
        f"<!-- period: {start.isoformat()} ~ {end.isoformat()} -->",
        f"<!-- digest_count: {stats['digest_count']} -->",
        "",
        WRITING_PROMPT,
        "",
        f"本周日期范围：{start.isoformat()} 至 {end.isoformat()}",
        f"周标签：{label}",
        "",
        "## 关键洞察（从本周日刊中提取）",
    ]

    for i, insight in enumerate(stats["insights"][:10]):
        lines.append(f"{i+1}. {insight}")

    lines.extend([
        "",
        "## 本周新增知识单元",
        "",
        f"概念卡片 ({len(stats['concepts_added'])}): {', '.join(stats['concepts_added'][:20]) or '无'}",
        f"实体卡片 ({len(stats['entities_added'])}): {', '.join(stats['entities_added'][:10]) or '无'}",
        f"合成报告 ({len(stats['syntheses_added'])}): {', '.join(stats['syntheses_added'][:5]) or '无'}",
        f"源材料 ({len(stats['raw_added'])}): {', '.join(stats['raw_added'][:5]) or '无'}",
        f"日刊数: {stats['digest_count']}",
        "",
        "## 本周全部日刊正文",
    ])

    for d in digests:
        with open(d, "r", encoding="utf-8") as f:
            content = f.read()
        body = re.sub(r"^---\n.*?\n---\n", "", content, flags=re.DOTALL).strip()
        date_str = os.path.basename(d)[:10]
        lines.append(f"### {date_str}")
        lines.append(body[:2000])  # 每篇日刊最多取 2000 字
        lines.append("")

    lines.append("<!-- WEEKLY_PREPARE_END -->")
    output = "\n".join(lines)
    print(output)
    return output


def write_weekly_report(content: str, week_label: str) -> str:
    """将渲染好的周报写入文件。"""
    filepath = get_week_filepath(week_label)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[weekly] Written: {filepath}")
    return filepath


# ── CLI ────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        mode = "current"
    else:
        arg = sys.argv[1]
        if arg == "last":
            mode = "last"
        elif arg.startswith("W") or arg.startswith("w"):
            prepare_context(iso_week=arg.upper(), mode="specific")
            sys.exit(0)
        else:
            mode = "current"

    prepare_context(mode=mode)
