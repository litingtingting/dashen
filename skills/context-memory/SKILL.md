---
name: context-memory
description: Automatic conversation context management. Replaces built-in session history. Workflow: (1) When user sends a message, extract keywords and grep search ~/.openclaw/sessions/ for relevant context BEFORE answering. (2) After responding, auto-save the exchange to session file. This forces AI to search for answers instead of hallucinating. Activate for ALL conversations.
---

# Context Memory Skill

**Purpose:** Replace system session with file-based context that AI actively searches.

## Core Workflow

### 1. User Sends Message → SEARCH FIRST
**Before answering anything**, extract keywords from user's message and search:

```bash
# Extract keywords and search (example: user asks about "服务器")
grep -rn "服务器" ~/.openclaw/sessions/

# Or search multiple keywords
grep -E "服务器|CPU|内存" ~/.openclaw/sessions/
```

### 2. AI Processes with Context
- Read relevant session lines from grep output
- Incorporate context into response
- Never answer from memory alone

### 3. Auto-Save After Responding
```bash
# Save user's message
python3 scripts/save_session.py <session_id> "<user_message>" user

# Save AI's response  
python3 scripts/save_session.py <session_id> "<ai_response>" assistant
```

## Session Format

File: `~/.openclaw/sessions/<session_id>.txt`
```
[YYYY-MM-DD HH:MM:SS] user: message
[YYYY-MM-DD HH:MM:SS] assistant: response
[YYYY-MM-DD HH:MM:SS] user: next message
...
```

## Keyword Extraction Examples

| User Says | Keywords to Search |
|-----------|-------------------|
| "服务器怎么样？" | 服务器, server, CPU, 内存 |
| "上次那个项目" | 项目, project, name |
| "帮我看看代码" | 代码, code, bug, error |

## Search Commands Reference

```bash
# Basic search
grep -rn "keyword" ~/.openclaw/sessions/

# Case insensitive
grep -ri "keyword" ~/.openclaw/sessions/

# Multiple keywords (OR)
grep -E "word1|word2|word3" ~/.openclaw/sessions/

# With context (3 lines around match)
grep -C 3 "keyword" ~/.openclaw/sessions/

# List all sessions
ls ~/.openclaw/sessions/

# Read specific session
cat ~/.openclaw/sessions/<session_id>.txt
```

## Session ID Strategy

Use a consistent session ID per user/conversation thread:
- `user_<sender_id>` for personal chats
- `group_<chat_id>` for group chats
- `project_<name>` for project-specific threads

## CRITICAL RULES

1. **ALWAYS search before answering** — never skip this step
2. **Extract 2-5 keywords** from user message for search
3. **Save every exchange** after AI responds
4. **Use grep -rn** for line references when citing context
5. **If no context found**, tell user "我在历史记录中没找到相关信息"

## Scripts

```bash
# Save message (call after AI responds)
python3 scripts/save_session.py <session_id> "<message>" [user|assistant]

# Get session summary
python3 scripts/summarize.py <session_id>
```
