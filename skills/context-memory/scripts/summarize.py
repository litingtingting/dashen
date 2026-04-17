#!/usr/bin/env python3
"""
Generate a summary for a session.
Usage: python3 summarize.py <session_id>
"""
import sys
import os

def generate_summary(session_id: str) -> str:
    """Read session file and generate a summary."""
    session_dir = os.path.expanduser("~/.openclaw/sessions")
    session_file = os.path.join(session_dir, f"{session_id}.txt")
    
    if not os.path.exists(session_file):
        return f"Session {session_id} not found"
    
    with open(session_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    if not lines:
        return f"Session {session_id} is empty"
    
    # Extract key info
    first_msg = ""
    last_msg = ""
    msg_count = len(lines)
    
    if lines:
        # First message (skip timestamp part)
        first_line = lines[0]
        if "] " in first_line:
            first_msg = first_line.split("] ", 1)[1].strip()
        
        # Last message
        last_line = lines[-1]
        if "] " in last_line:
            last_msg = last_line.split("] ", 1)[1].strip()
    
    summary = f"""Session: {session_id}
Messages: {msg_count}
Started: {first_msg[:100] if first_msg else 'N/A'}...
Last: {last_msg[:100] if last_msg else 'N/A'}..."""
    
    return summary

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: summarize.py <session_id>")
        sys.exit(1)
    
    session_id = sys.argv[1]
    print(generate_summary(session_id))
