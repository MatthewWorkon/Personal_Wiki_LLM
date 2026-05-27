#!/usr/bin/env python3
"""
log_append.py — 实时流式聊天记录追加技能

核心职责：
    每次用户与 AI 交互时，将消息实时追加到当天的 Chat 日志文件中。

追加格式：
    ## 问：HH:MM:SS
    用户输入内容

    ### 答：HH:MM:SS
    AI 回复内容

写入路径：
    30_Daily_Stream/{year}/{month}/Logs/YYYY-MM-DD_Chat.md
    （严格遵循 paths.json 的 logs_pattern 约定）

设计约束：
    - 纯追加（append），绝不修改已有内容
    - 路径从 paths.json 动态读取，杜绝硬编码
    - 月份目录按需自动创建
"""

import json
import os
from datetime import datetime


VAULT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def load_paths() -> dict:
    with open(os.path.join(VAULT_ROOT, ".opencode", "paths.json"), "r") as f:
        return json.load(f)


def _build_log_path(target_date: datetime) -> str:
    paths = load_paths()
    daily = paths["layers"]["daily_stream"]
    year = target_date.strftime("%Y")
    month = target_date.strftime("%m_%b")
    logs_dir = os.path.join(
        VAULT_ROOT, daily["logs_pattern"].format(year=year, month=month)
    )
    os.makedirs(logs_dir, exist_ok=True)

    filename = f"{target_date.strftime('%Y-%m-%d')}_Chat.md"
    return os.path.join(logs_dir, filename)


def log_message(role: str, content: str, target_date: datetime = None) -> str:
    """
    向当日 Chat 日志文件追加一条消息。

    Args:
        role: "user" 或 "assistant"
        content: 消息正文
        target_date: 目标日期（默认当前时间）

    Returns:
        写入的日志文件路径
    """
    if target_date is None:
        target_date = datetime.now()

    filepath = _build_log_path(target_date)
    timestamp = target_date.strftime("%H:%M:%S")

    if role == "user":
        prefix = f"## 问：{timestamp}\n"
    elif role == "assistant":
        prefix = f"### 答：{timestamp}\n"
    else:
        raise ValueError(f"Unknown role: {role}. Use 'user' or 'assistant'.")

    entry = f"\n{prefix}{content.strip()}\n"
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(entry)

    return filepath


def log_conversation_turn(user_msg: str, assistant_msg: str) -> tuple[str, str]:
    """
    一次性追加一轮完整对话（用户消息 + AI 回复）。

    Returns:
        (user_entry_path, assistant_entry_path) — 指向同一文件
    """
    now = datetime.now()
    fp = log_message("user", user_msg, target_date=now)
    fp = log_message("assistant", assistant_msg, target_date=now)
    return fp, fp


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: log_append.py <user|assistant> <content>")
        print("       log_append.py turn '<user_msg>' '<assistant_msg>'")
        sys.exit(1)

    if sys.argv[1] == "turn":
        u, a = sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else ""
        log_conversation_turn(u, a)
        print("Conversation turn logged.")
    else:
        role = sys.argv[1]
        content = sys.argv[2]
        path = log_message(role, content)
        print(f"Logged to: {path}")
