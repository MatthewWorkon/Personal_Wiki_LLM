#!/usr/bin/env python3
"""
eod_digest.py — 日结晶技能（End of Day Digest）

核心职责：
    每晚自动抓取当日 Logs/ 中的原始对话，利用 DeepSeek 蒸馏为核心洞察、
    深度知识讲解、涟漪映射建议，按 Template_Digest.md 格式写入 Digests/。

双通道蒸馏模式：
    通道 A（API 模式）：配置了 DEEPSEEK_API_KEY 时，脚本直接调用 API 完成全流程。
    通道 B（会话窗模式）：无 API Key 时，脚本输出「Prompt + 日志原文」，
        由会话窗中的 AI 执行蒸馏，结果通过 write 子命令写入。
    通道 B 是优先推荐的工作流——无需外部 API 依赖，蒸馏质量由会话上下文保证。

触发指令：
    digest              → 会话窗 AI 执行蒸馏（推荐）
    digest week         → 补生成本周全量缺失日刊（会话窗模式）
    digest month        → 补生成本月全量缺失日刊（会话窗模式）
    digest auto         → 强制 API 模式（需配置 DEEPSEEK_API_KEY）

蒸馏三模块：
    1. 核心灵感捕获 — 一句话提炼今天最具有启发性的点
    2. 知识深度拓展 — 学术级/工程级原理解析，由浅入深
    3. 涟漪映射建议 — 分析灵感与现有 Wiki 节点的关联

依赖：config.json、paths.json、Template_Digest.md
"""

import json
import os
import urllib.request
import urllib.error
import re
import sys
from datetime import datetime, date, timedelta
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
        return os.environ.get(env_var, "")
    return raw_key


def has_api_key() -> bool:
    """检查是否已配置有效的 API Key（非空且非占位符）。"""
    config = load_config()
    raw_key = config["model"]["api_key"]
    resolved = _resolve_api_key(raw_key)
    if not resolved:
        return False
    if resolved.startswith("${"):
        return False
    return True


# ── 蒸馏 Prompt（三模块） ──────────────────────────────────────

DISTILL_PROMPT = """你现在是本地 Wiki 的首席知识官。请阅读今天用户与 AI 的全部对话，生成一份《每日思想纪要与深度知识册》。

必须包含以下三个模块：

1. # 核心灵感捕获
   用一句话提炼今天最具有启发性的点。

2. # 知识深度拓展
   针对今天讨论的核心技术/设计/框架，不要只做总结，
   请利用你的长上下文和深度推理能力（Reasoning），
   进行由浅入深的学术级/工程级原理解析。

3. # 涟漪映射建议
   分析今天的灵感与现有的哪些 Wiki 节点（如 [[概念A]] 或 [[实体B]]）
   可能存在关联，并给出具体修改建议。

严格按以下 JSON 结构返回，不要包含任何其他文字：

{
  "insights": ["洞察1（一句话）", "洞察2", "洞察3"],
  "deep_dive": "知识深度拓展的完整 Markdown 正文（可多段，含小标题）",
  "ripple_suggestions": ["建议1：关联 [[节点名]]，原因...", "建议2"],
  "mood": "简短的情绪/状态总结",
  "todo": ["待办项1", "待办项2"],
  "emerging_concepts": ["新概念名1", "新概念名2"]
}"""


# ── 日志读取 ──────────────────────────────────────────────────

def get_log_files(target_date: date) -> list[str]:
    paths = load_paths()
    daily = paths["layers"]["daily_stream"]
    year = str(target_date.year)
    month = target_date.strftime("%m_%b")
    logs_dir = os.path.join(
        VAULT_ROOT, daily["logs_pattern"].format(year=year, month=month)
    )
    if not os.path.isdir(logs_dir):
        return []
    date_prefix = target_date.isoformat()
    return sorted([
        os.path.join(logs_dir, f) for f in os.listdir(logs_dir)
        if f.startswith(date_prefix) and f.endswith(".md") and not f.endswith("_Digest.md")
    ])


def read_logs(log_files: list[str]) -> str:
    contents = []
    for f in log_files:
        with open(f, "r", encoding="utf-8") as fh:
            contents.append(fh.read())
    return "\n\n---\n\n".join(contents)


# ── 通道 A：API 蒸馏 ──────────────────────────────────────────

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
        "temperature": model_cfg["temperature"],
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


def distill(log_content: str) -> dict:
    full_prompt = DISTILL_PROMPT + "\n\n以下是今天的全部对话：\n\n" + log_content
    response = call_deepseek(full_prompt)

    try:
        json_match = re.search(r"\{.*\}", response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
        return json.loads(response)
    except json.JSONDecodeError:
        return {
            "insights": ["（蒸馏解析失败，请检查 API 返回格式）"],
            "deep_dive": response,
            "ripple_suggestions": [],
            "mood": "",
            "todo": [],
            "emerging_concepts": [],
        }


# ── 通道 B：会话窗准备 ────────────────────────────────────────

def prepare_context(target_date: date) -> str:
    """
    通道 B 入口：输出「蒸馏 Prompt + 当日日志原文」的联合文本块。
    供会话窗中的 AI 读取后执行蒸馏。

    输出包含清晰的分隔标记，方便 AI 解析和处理。
    """
    log_files = get_log_files(target_date)
    if not log_files:
        print(f"[eod_digest] No chat logs found for {target_date}.", file=sys.stderr)
        return ""

    log_content = read_logs(log_files)
    date_str = target_date.isoformat()

    output = f"""<!-- EOD_DIGEST_PREPARE_BEGIN -->
<!-- target_date: {date_str} -->
<!-- log_file_count: {len(log_files)} -->
<!-- mode: session_window -->

## 蒸馏任务

{DISTILL_PROMPT}

## 当日对话日志

{log_content}

<!-- EOD_DIGEST_PREPARE_END -->"""

    print(output)
    return output


# ── Digest 渲染与写入 ─────────────────────────────────────────

def render_digest(distilled: dict, target_date: date, source_logs: list[str]) -> str:
    date_str = target_date.isoformat()
    insights_md = "\n\n".join(
        f"### 洞察 {i+1}：\n{insight}"
        for i, insight in enumerate(distilled.get("insights", []))
    ) or "### 洞察 1：\n（今日无核心洞察）"

    concepts_list = "\n".join(
        f"- [[{c}]]" for c in distilled.get("emerging_concepts", [])
    ) or "- （无新概念）"

    ripple_list = "\n".join(
        f"- {s}" for s in distilled.get("ripple_suggestions", [])
    ) or "- （无涟漪映射建议）"

    todo_list = "\n".join(
        f"- [ ] {t}" for t in distilled.get("todo", [])
    ) or "- [ ] "

    source_list = "\n".join(
        f"- [[{os.path.splitext(os.path.basename(f))[0]}]]"
        for f in source_logs
    )

    return f"""---
title: "{date_str} 思想日刊"
file_type: digest
digest_type: daily
created: {date_str}
period_start: {date_str}
period_end: {date_str}
source_logs: {json.dumps([os.path.basename(f) for f in source_logs], ensure_ascii=False)}
key_insights: {json.dumps(distilled.get("insights", []), ensure_ascii=False)}
emerging_concepts: {json.dumps(distilled.get("emerging_concepts", []), ensure_ascii=False)}
mood_summary: "{distilled.get("mood", "")}"
---

# {date_str} 思想日刊

## 核心灵感捕获

{insights_md}

## 知识深度拓展

{distilled.get("deep_dive", "（暂无深度拓展内容）")}

## 涟漪映射建议

{ripple_list}

## 精神状态摘要

{distilled.get("mood", "（未记录）")}

## 新涌现的概念

{concepts_list}

## 待办与后续

{todo_list}

## 原始对话索引

{source_list}
"""


def validate_digest(digest_content: str) -> list[str]:
    """返回缺失项列表，为空则表示通过。"""
    required_frontmatter = ["title", "file_type", "created"]
    required_headings = [
        "核心灵感捕获",
        "知识深度拓展",
        "涟漪映射建议",
        "精神状态摘要",
        "待办与后续",
    ]
    missing = []

    for key in required_frontmatter:
        if not re.search(rf"{key}:", digest_content[:500]):
            missing.append(f"frontmatter.{key}")

    for heading in required_headings:
        if f"## {heading}" not in digest_content and f"# {heading}" not in digest_content:
            missing.append(f"heading.{heading}")

    return missing


def get_digest_path(target_date: date) -> str:
    paths = load_paths()
    daily = paths["layers"]["daily_stream"]
    year = str(target_date.year)
    month = target_date.strftime("%m_%b")
    digest_dir = os.path.join(
        VAULT_ROOT, daily["digests_pattern"].format(year=year, month=month)
    )
    os.makedirs(digest_dir, exist_ok=True)
    filename = f"{target_date.isoformat()}_Digest.md"
    return os.path.join(digest_dir, filename)


def write_digest_file(distilled: dict, target_date: date) -> str:
    """
    将已蒸馏的数据渲染为 Markdown 并写入文件。
    由会话窗 AI 在蒸馏完成后调用。
    """
    log_files = get_log_files(target_date)
    digest_content = render_digest(distilled, target_date, log_files)

    missing = validate_digest(digest_content)
    if missing:
        raise ValueError(f"Digest validation failed: {', '.join(missing)}")

    filepath = get_digest_path(target_date)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(digest_content)

    print(f"[eod_digest] Written: {filepath}")
    return filepath


# ── 主流程：双通道自动路由 ────────────────────────────────────

def generate_digest(target_date: Optional[date] = None,
                    force_api: bool = False) -> str:
    """
    主入口。自动检测 API Key 可用性选择通道。
    force_api=True 时强制走 API 通道（失败不降级）。
    """
    if target_date is None:
        target_date = date.today()

    log_files = get_log_files(target_date)
    if not log_files:
        raise FileNotFoundError(
            f"No chat log files found for {target_date}. Have you chatted today?"
        )

    log_content = read_logs(log_files)

    if force_api or has_api_key():
        # 通道 A：API 蒸馏
        print(f"[eod_digest] Mode: API (channel A) — {len(log_files)} log(s)")
        distilled = distill(log_content)
        print("[eod_digest] Distillation complete.")
        return write_digest_file(distilled, target_date)
    else:
        # 通道 B：输出上下文供会话窗 AI 蒸馏
        print(f"[eod_digest] Mode: SESSION WINDOW (channel B) — {len(log_files)} log(s)")
        print("[eod_digest] No API key configured.")
        print("[eod_digest] Outputting prompt + logs for in-session distillation...\n")
        prepare_context(target_date)
        print("\n[eod_digest] ▲ Paste the above into your AI session for distillation.")
        print("[eod_digest] After AI distills, call: eod_digest.py write <json_file> [date]")
        return ""


def generate_missing_digests(days: int) -> list[str]:
    """
    补生成最近 N 天内缺失的日刊。
    每个缺失日期输出 prepare context，由会话窗 AI 逐个处理。
    """
    today = date.today()
    prepared = []
    for i in range(days, 0, -1):
        d = today - timedelta(days=i)
        digest_file = get_digest_path(d)
        if os.path.exists(digest_file):
            continue

        log_files = get_log_files(d)
        if not log_files:
            continue

        print(f"\n{'='*60}")
        print(f"[eod_digest] Preparing {d.isoformat()}...")
        print(f"{'='*60}\n")
        prepare_context(d)
        prepared.append(d.isoformat())

    return prepared


# ── CLI ────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: eod_digest.py <command> [args]")
        print()
        print("Session window commands (recommended, no API key needed):")
        print("  prepare              Output prompt + today's logs for AI distillation")
        print("  prepare YYYY-MM-DD   Output prompt + logs for specific date")
        print("  week                 Prepare all missing digests this week")
        print("  month                Prepare all missing digests this month")
        print("  write <json> [date]  Write AI-distilled JSON to digest file")
        print()
        print("API mode commands (requires DEEPSEEK_API_KEY):")
        print("  auto                 Full API pipeline for today")
        print("  auto YYYY-MM-DD      Full API pipeline for specific date")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "prepare":
        target = date.fromisoformat(sys.argv[2]) if len(sys.argv) > 2 else date.today()
        prepare_context(target)

    elif cmd == "write":
        if len(sys.argv) < 3:
            print("Usage: eod_digest.py write <json_file> [YYYY-MM-DD]", file=sys.stderr)
            sys.exit(1)
        json_path = sys.argv[2]
        target = date.fromisoformat(sys.argv[3]) if len(sys.argv) > 3 else date.today()
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        write_digest_file(data, target)

    elif cmd == "week":
        results = generate_missing_digests(days=7)
        if results:
            print(f"\n[eod_digest] Prepared {len(results)} missing dates: {', '.join(results)}")
        else:
            print("[eod_digest] All digests up to date for the past week.")

    elif cmd == "month":
        results = generate_missing_digests(days=30)
        if results:
            print(f"\n[eod_digest] Prepared {len(results)} missing dates: {', '.join(results)}")
        else:
            print("[eod_digest] All digests up to date for the past month.")

    elif cmd == "auto":
        target = date.fromisoformat(sys.argv[2]) if len(sys.argv) > 2 else None
        try:
            result = generate_digest(target, force_api=True)
            print(f"[eod_digest] Done: {result}")
        except Exception as e:
            print(f"[eod_digest] Error: {e}", file=sys.stderr)
            sys.exit(1)

    else:
        target = date.fromisoformat(cmd)
        generate_digest(target, force_api=True)
