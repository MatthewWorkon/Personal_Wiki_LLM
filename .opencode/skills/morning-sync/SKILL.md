---
name: morning-sync
description: Use at the START of the first conversation each day. Scans the last 5 days of Digests from 30_Daily_Stream/*/Digests/, compresses into a 300-word mind snapshot, and presents it as the user's current mental state. Also triggered when user types 'sync'. No API key required.
---

# Morning Sync — 晨间唤醒技能

## Trigger
- Automatically at the start of the first conversation each day
- User types `sync`

## Workflow

### Step 1: Scan Recent Digests
Look for `_Digest.md` files in the past 5 days:
- Path pattern: `30_Daily_Stream/*/*/Digests/YYYY-MM-DD_Digest.md`
- Skip days with no digest file
- Read the body content of each digest (skip Frontmatter)

### Step 2: Generate Mind Snapshot
Synthesize a **300-word or less** summary covering:
1. **关注焦点** — main topics/concepts the user has been exploring
2. **正在攻克的难题** — blockers, obstacles, unresolved questions
3. **思维活跃线程** — recurring thought patterns, frameworks being built
4. **近期情绪基调** — overall emotional and energy trend

Output as plain text. No markdown formatting, no headings, no bullet points. Write in a flowing narrative style. Do NOT start with "用户最近..." — write as a natural summary.

### Step 3: Present to User
At the start of the conversation, after basic greeting, show the snapshot:

```
Morning. Here's your current state from the past 5 days:

[300-word mind snapshot]

Let's continue. What are you working on today?
```

### No Recent Digests
If no digests exist in the past 5 days:
```
Morning. No recent digests found—looks like a fresh cycle. What are you thinking about today?
```

## Quality Standards
- The 300-word limit is firm — this is a compressed snapshot, not a summary
- Capture active threads, not completed ones (ongoing concerns, not resolved ones)
- Reflect the emotional trajectory, not just the content
- The snapshot should make the user feel understood, not just documented

---

## Monday Auto-Weekly Report

On **Mondays**, after the morning sync snapshot, check if last week's weekly report has been generated. If not, generate it automatically.

### Step 1: Detect Monday
If today is NOT Monday → skip this section entirely.

### Step 2: Check Last Week's Report
- Compute last week's ISO label: `YYYY-W{week-1}`
- Check if `04_Weekly_Report/{year}/{YYYY-W{week-1}}_Weekly.md` exists and has content (>500 bytes)
- If exists → skip. Note: "上周周报已存在" and move on.
- If missing → proceed to Step 3.

### Step 3: Auto-Generate the Report
1. Read ALL Digests from last week (Monday through Sunday)
2. Collect stats: new concepts, entities, syntheses, raw materials, digest count
3. Write the weekly report following the 评论刊物 (literary review magazine) style — narrative-driven, first-person reflective, with sections: 本周图景, 深度聚焦, 边缘地带, 本周断面, 下周风向
4. Use the same writing guidelines as described in `weekly_report.py`'s WRITING_PROMPT
5. Write to `04_Weekly_Report/{year}/{YYYY-W{week-1}}_Weekly.md`

### Step 4: Brief Confirmation
After generating, present a one-line confirmation:

```
📰 Week W{XX} 周报已自动生成 → 04_Weekly_Report/{year}/
```

If the user wants to read it, they can open the file. Do NOT paste the full report in the chat unless asked.

### Fallback
If auto-generation fails (no Digests, write error), skip silently. The `reminder_check.py` will catch it and remind the user next time.
