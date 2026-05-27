---
name: log-append
description: Use automatically during EVERY conversation turn. After the AI responds to the user, append the user message and AI response to 30_Daily_Stream/{year}/{month}/Logs/YYYY-MM-DD_Chat.md in the format '## 问：HH:MM:SS\n<user message>\n\n### 答：HH:MM:SS\n<AI response>'. This runs silently—do not tell the user it's logging unless they ask.
---

# Log Append — 实时对话记录技能

## Trigger
- **Automatically** after every conversation turn (user message + AI response)
- Runs silently — do NOT mention logging in your reply unless user asks
- Keeps running in the background for every exchange

## Workflow

### Step 1: Determine Log Path
The chat log for today goes to:
```
30_Daily_Stream/{year}/{MM_Mon}/Logs/YYYY-MM-DD_Chat.md
```

Example: `30_Daily_Stream/2026/05_May/Logs/2026-05-27_Chat.md`

- `{year}` = current year (4 digits)
- `{MM_Mon}` = month as two-digit number + abbreviated English name (e.g., `05_May`, `06_Jun`)
- `YYYY-MM-DD` = current date in ISO format

Create parent directories if they don't exist.

### Step 2: Append Conversation Turn
Append the full exchange to the file in this EXACT format:

```markdown
## 问：HH:MM:SS
<user's complete message>

### 答：HH:MM:SS
<AI's complete response>

```

Rules:
- `HH:MM:SS` = current time
- Blank line between `## 问：timestamp` and the user message
- Blank line between `### 答：timestamp` and the AI response
- Blank line after the AI response before next section
- Use `##` for user messages, `###` for AI responses
- Append ONLY, never modify existing content
- Log the full text of both messages without truncation

### Step 3: Remain Silent
Do NOT say things like "I've logged our conversation" or "This has been saved." The logging is transparent and silent.

## Edge Cases
- If the directory doesn't exist, create it
- If the file doesn't exist, create it
- If this is the first turn of the day, the file starts fresh
- Multiple conversation turns append sequentially to the same file

## Helper Script
The Python script at `.opencode/skills/log_append.py` provides:
```
python3 .opencode/skills/log_append.py user "<message>"
python3 .opencode/skills/log_append.py assistant "<message>"
```
But in practice, the AI should write directly using the Write tool rather than calling the script, since the AI has full file access.
