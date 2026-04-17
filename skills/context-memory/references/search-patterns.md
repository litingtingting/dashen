# Search Patterns for Context

Use these grep commands to search historical sessions.

## Basic Search

```bash
# Search all sessions for a keyword
grep -r "keyword" ~/.openclaw/sessions/

# Search with line numbers (for reference)
grep -rn "keyword" ~/.openclaw/sessions/

# Case-insensitive search
grep -ri "keyword" ~/.openclaw/sessions/
```

## Session Discovery

```bash
# List all session files
ls -la ~/.openclaw/sessions/

# Read a specific session
cat ~/.openclaw/sessions/<session_id>.txt

# Get line count per session
wc -l ~/.openclaw/sessions/*.txt
```

## Advanced Search

```bash
# Find sessions with both terms (AND)
grep -l "term1" ~/.openclaw/sessions/*.txt | xargs grep -l "term2"

# Find sessions with either term (OR)
grep -E "term1|term2" ~/.openclaw/sessions/*.txt

# Show context around match (3 lines before and after)
grep -C 3 "keyword" ~/.openclaw/sessions/*.txt

# Search in specific session
grep "keyword" ~/.openclaw/sessions/<session_id>.txt
```

## Summary Generation

```bash
# Generate summary for a session
python3 <skill-path>/scripts/summarize.py <session_id>
```

## Session Management

```bash
# Save a message to session
python3 <skill-path>/scripts/save_session.py <session_id> "<message>" [role]

# roles: user, assistant, system
```
