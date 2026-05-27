#!/usr/bin/env python3
"""
health_check.py — 项目健康自检与自愈引擎

核心职责：
    每次会话启动时静默运行 6 项自检，能自愈的无感修复，
    不能自愈的交给 reminder_check.py 提醒用户。

自愈能力：
    1. 文档脚本计数过期 → 自动更新数字
    2. 破损链接 → 自动调用 link_validator
    3. 目录缺失 → 自动 mkdir
    4. .gitkeep 缺失 → 自动 touch
    5. GitHub 同步差异 → 仅报告
    6. 今日 Digest 缺失 → 仅报告

触发方式：
    自动：每次会话启动（静默）
    手动：healthcheck → 输出完整自检报告

依赖：paths.json, config.json, link_validator.py
"""

import json
import os
import re
import glob as glob_mod
import subprocess
from datetime import date, datetime


VAULT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def load_config() -> dict:
    with open(os.path.join(VAULT_ROOT, ".opencode", "config.json"), "r") as f:
        return json.load(f)


def load_paths() -> dict:
    with open(os.path.join(VAULT_ROOT, ".opencode", "paths.json"), "r") as f:
        return json.load(f)


# ── 工具函数 ──────────────────────────────────────────────────

def count_py_scripts() -> int:
    d = os.path.join(VAULT_ROOT, ".opencode", "skills")
    return len([f for f in os.listdir(d) if f.endswith(".py")])


def count_files(directory: str, pattern: str = "*.md") -> int:
    if not os.path.isdir(directory):
        return 0
    return len(glob_mod.glob(os.path.join(directory, pattern)))


# ── 检测 1：文档计数一致性 ──────────────────────────────────

def check_doc_counts() -> list[str]:
    """检查 Vault_Structure_Reference.md 和 AI_Agent_使用说明.md 中的脚本计数是否正确。"""
    actual = count_py_scripts()
    fixed = []

    targets = [
        os.path.join(VAULT_ROOT, "备注", "Vault_Structure_Reference.md"),
        os.path.join(VAULT_ROOT, "备注", "AI_Agent_使用说明.md"),
    ]

    for filepath in targets:
        if not os.path.exists(filepath):
            continue
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        modified = False

        # 修复 "X 个 Python 技能脚本" 或 "X 个 Python 脚本"
        patterns = [
            (r"(\d+) 个 Python 技能脚本", f"{actual} 个 Python 技能脚本"),
            (r"(\d+) 个 Python 脚本", f"{actual} 个 Python 脚本"),
            (r"(\d+) 个 .+? 脚本骨", f"{actual} 个 Python 脚本骨"),
        ]
        for pat, repl in patterns:
            match = re.search(pat, content)
            if match and int(match.group(1)) != actual:
                content = re.sub(pat, repl, content)
                modified = True

        if modified:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            fixed.append(os.path.basename(filepath))

    return fixed


# ── 检测 2：破损链接 ──────────────────────────────────────────

def check_broken_links() -> bool:
    """调用 link_validator.py 修复破损链接。返回是否修复了链接。"""
    script = os.path.join(VAULT_ROOT, ".opencode", "skills", "link_validator.py")
    result = subprocess.run(
        ["python3", script],
        capture_output=True, text=True,
    )
    return "全库链接完整" not in result.stdout


# ── 检测 3：目录完整性 ────────────────────────────────────────

def check_directories() -> list[str]:
    """检查 paths.json 中引用的目录是否存在，不存在则创建。"""
    paths = load_paths()
    expected = []

    # Raw_Materials
    raw = os.path.join(VAULT_ROOT, paths["layers"]["raw_materials"]["root"])
    for sub in paths["layers"]["raw_materials"]["subdirs"]:
        expected.append(os.path.join(raw, sub))

    # Wiki_Grid
    grid = os.path.join(VAULT_ROOT, paths["layers"]["wiki_grid"]["root"])
    for sub in paths["layers"]["wiki_grid"]["subdirs"]:
        expected.append(os.path.join(grid, sub))

    # Archives
    archives = os.path.join(VAULT_ROOT, paths["layers"]["daily_stream"]["archives"])
    expected.append(archives)

    # Soul archive
    sa = os.path.join(VAULT_ROOT, paths["layers"]["soul_archive"])
    expected.append(sa)

    # Weekly report
    today = date.today()
    weekly_dir = os.path.join(VAULT_ROOT, "04_Weekly_Report", str(today.year))
    expected.append(weekly_dir)

    # 当前月份日志目录
    year = str(today.year)
    month = today.strftime("%m_%b")
    logs_dir = os.path.join(
        VAULT_ROOT,
        paths["layers"]["daily_stream"]["logs_pattern"].format(year=year, month=month),
    )
    digests_dir = os.path.join(
        VAULT_ROOT,
        paths["layers"]["daily_stream"]["digests_pattern"].format(year=year, month=month),
    )
    expected.extend([logs_dir, digests_dir])

    created = []
    for d in expected:
        if not os.path.isdir(d):
            os.makedirs(d, exist_ok=True)
            created.append(os.path.relpath(d, VAULT_ROOT))

    return created


# ── 检测 4：.gitkeep 完整性 ──────────────────────────────────

def check_gitkeeps() -> list[str]:
    """检查空目录是否有 .gitkeep，缺失则创建。"""
    dirs_to_check = [
        "00_Raw_Materials/Books",
        "00_Raw_Materials/Papers",
        "00_Raw_Materials/WebClips",
        "10_Wiki_Grid/00_Anchors",
        "10_Wiki_Grid/Concepts",
        "10_Wiki_Grid/Entities",
        "10_Wiki_Grid/Syntheses",
        "30_Daily_Stream/Archives",
        "soul_profile_archive",
        "04_Weekly_Report",
    ]

    today = date.today()
    year = str(today.year)
    month = today.strftime("%m_%b")
    next_month = (today.replace(day=28) + __import__("datetime").timedelta(days=4)).replace(day=1)
    next_month_str = next_month.strftime("%m_%b")

    dirs_to_check.extend([
        f"30_Daily_Stream/{year}/{month}/Logs",
        f"30_Daily_Stream/{year}/{month}/Digests",
        f"30_Daily_Stream/{year}/{next_month_str}/Logs",
        f"30_Daily_Stream/{year}/{next_month_str}/Digests",
    ])

    created = []
    for d in dirs_to_check:
        full = os.path.join(VAULT_ROOT, d)
        if not os.path.isdir(full):
            continue
        gitkeep = os.path.join(full, ".gitkeep")
        if not os.path.exists(gitkeep):
            with open(gitkeep, "w") as f:
                pass
            created.append(d)

    return created


# ── 检测 5：GitHub 同步时效 ──────────────────────────────────

def check_github_sync() -> dict:
    """检查 GitHub 同步文件夹是否过期。"""
    sync_root = os.path.join(VAULT_ROOT, "备注", "GitHub同步")
    if not os.path.isdir(sync_root):
        return {"status": "missing", "message": "GitHub同步 文件夹不存在"}

    # 检查脚本数是否一致
    vault_scripts = count_py_scripts()
    sync_scripts = len([f for f in os.listdir(os.path.join(sync_root, ".opencode", "skills"))
                        if f.endswith(".py")]) if os.path.isdir(os.path.join(sync_root, ".opencode", "skills")) else 0

    if vault_scripts != sync_scripts:
        return {"status": "stale", "message": f"脚本数不一致：vault {vault_scripts} vs sync {sync_scripts}"}

    # 检查 .gitignore
    if not os.path.exists(os.path.join(sync_root, ".opencode", ".gitignore")):
        src = os.path.join(VAULT_ROOT, ".opencode", ".gitignore")
        if os.path.exists(src):
            import shutil
            dst = os.path.join(sync_root, ".opencode", ".gitignore")
            shutil.copy2(src, dst)
            return {"status": "fixed", "message": "已复制 .opencode/.gitignore 到 GitHub 同步"}

    return {"status": "ok", "message": "GitHub 同步脚本层一致"}


# ── 检测 6：今日 Digest ───────────────────────────────────────

def check_today_digest() -> dict:
    today = date.today()
    paths = load_paths()
    daily = paths["layers"]["daily_stream"]
    year = str(today.year)
    month = today.strftime("%m_%b")

    log_dir = os.path.join(VAULT_ROOT, daily["logs_pattern"].format(year=year, month=month))
    digest_dir = os.path.join(VAULT_ROOT, daily["digests_pattern"].format(year=year, month=month))
    log_file = os.path.join(log_dir, f"{today.isoformat()}_Chat.md")
    digest_file = os.path.join(digest_dir, f"{today.isoformat()}_Digest.md")

    has_log = os.path.exists(log_file) and os.path.getsize(log_file) > 100
    has_digest = os.path.exists(digest_file)

    if not has_log:
        return {"status": "quiet", "message": "今日无对话"}
    if has_digest:
        return {"status": "ok", "message": "今日 Digest 已存在"}
    return {"status": "missing", "message": "今日有对话但无 Digest — 输入 digest 生成"}


# ── 主入口 ────────────────────────────────────────────────────

def run_healthcheck(verbose: bool = False) -> dict:
    report = {
        "doc_counts_fixed": [],
        "broken_links_fixed": False,
        "directories_created": [],
        "gitkeeps_created": [],
        "github_sync": {},
        "today_digest": {},
    }

    report["doc_counts_fixed"] = check_doc_counts()
    report["broken_links_fixed"] = check_broken_links()
    report["directories_created"] = check_directories()
    report["gitkeeps_created"] = check_gitkeeps()
    report["github_sync"] = check_github_sync()
    report["today_digest"] = check_today_digest()

    return report


def format_report(report: dict, verbose: bool = False) -> str:
    lines = ["🔍 项目健康检查 " + date.today().isoformat(), "═" * 37]
    issue_count = 0

    # 文档计数
    if report["doc_counts_fixed"]:
        for f in report["doc_counts_fixed"]:
            lines.append(f"  ✓ 已更新 {f} 中的脚本计数")
            issue_count += 1
    elif verbose:
        lines.append("  · 文档计数一致")

    # 破损链接
    if report["broken_links_fixed"]:
        lines.append("  ✓ 已修复破损链接")
        issue_count += 1
    elif verbose:
        lines.append("  · 无破损链接")

    # 目录
    if report["directories_created"]:
        for d in report["directories_created"]:
            lines.append(f"  ✓ 已创建目录 {d}")
            issue_count += 1
    elif verbose:
        lines.append("  · 目录结构完整")

    # gitkeep
    if report["gitkeeps_created"]:
        for g in report["gitkeeps_created"]:
            lines.append(f"  ✓ 已补全 .gitkeep ({g})")
            issue_count += 1
    elif verbose:
        lines.append("  · .gitkeep 完整")

    # GitHub 同步
    gs = report["github_sync"]
    if gs.get("status") in ("stale", "missing"):
        lines.append(f"  ⚠ GitHub 同步: {gs.get('message', '')}")
        issue_count += 1
    elif gs.get("status") == "fixed":
        lines.append(f"  ✓ {gs.get('message', '')}")
        issue_count += 1
    elif verbose:
        lines.append("  · " + gs.get("message", "GitHub 同步 OK"))

    # 今日 Digest
    td = report["today_digest"]
    if td.get("status") == "missing":
        lines.append(f"  ⚠ {td['message']}")
        issue_count += 1
    elif verbose or td.get("status") != "quiet":
        lines.append(f"  · {td.get('message', '')}")

    lines.append("═" * 37)
    if issue_count == 0:
        lines.append("全部健康。")
    else:
        lines.append(f"已处理 {issue_count} 项。")

    return "\n".join(lines)


if __name__ == "__main__":
    import sys
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    report = run_healthcheck(verbose=verbose)
    print(format_report(report, verbose=verbose))
