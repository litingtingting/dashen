#!/usr/bin/env python3
"""
Save conversation to a session file.
Usage: python3 save_session.py <session_id> <message>
"""
import sys
import os
from datetime import datetime

def save_message(session_id: str, message: str, role: str = "user"):
    """Append a message to the session file."""
    session_dir = os.path.expanduser("~/.openclaw/sessions")
    os.makedirs(session_dir, exist_ok=True)
    
    session_file = os.path.join(session_dir, f"{session_id}.txt")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(session_file, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {role}: {message}\n")
    
    return session_file

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: save_session.py <session_id> <message> [role]")
        sys.exit(1)
    
    session_id = sys.argv[1]
    message = sys.argv[2]
    role = sys.argv[3] if len(sys.argv) > 3 else "user"
    
    path = save_message(session_id, message, role)
    print(f"Saved to {path}")
