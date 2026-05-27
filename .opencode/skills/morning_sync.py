#!/usr/bin/env python3
"""
morning_sync.py — 晨间唤醒技能（Morning Context Bootloader）

核心职责：
    每天首次对话时自动运行，扫描最近 N 天的 Digests，
    调用 DeepSeek 压缩生成 300 字以内的"思想快照"（Mind Snapshot），
    供 OpenCode 注入 System Prompt 顶部，实现 AI 的无缝记忆承接。

执行流程：
    1. 扫描 30_Daily_Stream/ 下最近 N 天（默认 5 天）的 _Digest.md 文件
    2. 拼接所有 Digest 正文，附上"请压缩"指令，调用 DeepSeek
    3. 返回 300 字以内的思想快照（纯文本）
    4. 外部调用方将此快照注入 System Prompt

缓存机制：
    快照同时写入 soul_profile.md 的「近期思想动态」区，
    由 soul_updater.py 在下一次周更新时正式归档。

输入：recent_days（默认 5）
输出：思想快照字符串（≤300 字）

依赖：config.json, paths.json
"""

import json
import os
import urllib.request
import urllib.error
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


def _resolve_api_key(raw_key: str) -> str:
    if raw_key.startswith("${") and raw_key.endswith("}"):
        env_var = raw_key[2:-1]
        return os.environ.get(env_var, raw_key)
    return raw_key


def call_deepseek(prompt: str, system_prompt: str = "") -> str:
    config = load_config()
    model_cfg = config["model"]
    api_key = _resolve_api_key(model_cfg["api_key"])
    base_url = model_cfg["base_url"].rstrip("/")
    url = f"{base_url}/chat/completions"

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    body = json.dumps({
        "model": model_cfg["model_id"],
        "messages": messages,
        "max_tokens": model_cfg["max_tokens"],
        "temperature": 0.3,  # 压缩任务用低温
    }).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        raise RuntimeError(f"DeepSeek API error {e.code}: {error_body}")


COMPRESS_PROMPT = """请阅读以下用户最近几天的思想纪要和深度知识文档。

然后，用 **300 字以内** 高度概括用户最近一周的以下四个方面：
1. 关注焦点 — 主要在思考和探索什么主题
2. 正在攻克的难题 — 卡点、障碍、未解决的问题
3. 思维活跃线程 — 反复出现的思想脉络、正在构建的认知框架
4. 近期情绪基调 — 精神状态的总体趋势

输出纯文本，不要带任何标记、标题或序号。
不要用"用户最近..."开头，直接用第一人称或第三人称自然叙述。

以下是最近的纪要内容：
---
"""


def get_recent_digests(recent_days: int = 5) -> list[str]:
    """
    扫描最近 N 天的所有 Digest 文件路径。
    """
    paths = load_paths()
    daily_root = os.path.join(VAULT_ROOT, paths["layers"]["daily_stream"]["root"])
    today = date.today()

    all_digests = glob_mod.glob(
        os.path.join(daily_root, "**/*_Digest.md"), recursive=True
    )

    recent = []
    cutoff = today - timedelta(days=recent_days)
    for d in all_digests:
        try:
            basename = os.path.basename(d)
            file_date = date.fromisoformat(basename[:10])
            if cutoff <= file_date <= today:
                recent.append(d)
        except (ValueError, IndexError):
            continue

    return sorted(recent)


def read_digests(digest_files: list[str]) -> str:
    """读取所有 Digest 文件的正文（跳过 Frontmatter）。"""
    contents = []
    for f in digest_files:
        with open(f, "r", encoding="utf-8") as fh:
            text = fh.read()
            body_match = re.search(r"---\n.*?\n---\n(.*)", text, re.DOTALL)
            if body_match:
                contents.append(body_match.group(1).strip())
            else:
                contents.append(text.strip())
    return "\n\n---\n\n".join(contents)


def generate_mind_snapshot(recent_days: int = 5) -> str:
    """
    主入口：生成思想快照。
    Returns: ≤300 字的思想状态摘要。
    """
    digest_files = get_recent_digests(recent_days)

    if not digest_files:
        return "（暂无近期思想纪要，这是用户在新周期中的第一次对话。）"

    print(f"Found {len(digest_files)} recent digest(s)")

    combined = read_digests(digest_files)
    full_prompt = COMPRESS_PROMPT + combined

    print("Compressing with DeepSeek...")
    snapshot = call_deepseek(full_prompt)

    # 强制截断到 350 字（给 DeepSeek 一点容差）
    if len(snapshot) > 350:
        snapshot = snapshot[:347] + "..."

    return snapshot.strip()


def morning_sync(recent_days: int = 5) -> dict:
    """
    完整的晨间同步流程。
    Returns: {
        "status": "ready" | "empty",
        "snapshot": "思想快照文本",
        "digest_count": N,
        "date_range": "YYYY-MM-DD ~ YYYY-MM-DD"
    }
    """
    digest_files = get_recent_digests(recent_days)

    if not digest_files:
        return {
            "status": "empty",
            "snapshot": "（暂无近期思想纪要）",
            "digest_count": 0,
            "date_range": "",
        }

    snapshot = generate_mind_snapshot(recent_days)

    # 确定日期范围
    dates = []
    for f in digest_files:
        try:
            dates.append(date.fromisoformat(os.path.basename(f)[:10]))
        except ValueError:
            pass

    date_range = ""
    if dates:
        date_range = f"{min(dates).isoformat()} ~ {max(dates).isoformat()}"

    return {
        "status": "ready",
        "snapshot": snapshot,
        "digest_count": len(digest_files),
        "date_range": date_range,
    }


if __name__ == "__main__":
    import sys
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    result = morning_sync(recent_days=days)
    print(json.dumps(result, ensure_ascii=False, indent=2))
