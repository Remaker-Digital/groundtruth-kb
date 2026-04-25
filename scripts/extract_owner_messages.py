"""Extract all owner (human) messages from session transcripts for specification mining.

Reads all main JSONL session transcripts, extracts user-type messages,
and outputs a structured JSON file for granular specification extraction.

Claude Code JSONL format:
  type="user" records contain a "message" field with {role: "user", content: "..."}

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import json
import os
import sys
import glob
from pathlib import Path

# Per S307 hardcoded-path directive (no machine-local literals in active code):
# - Repo root is discovered from this script's location, not hardcoded.
# - Claude transcript dir is supplied via env var with a portable default
#   (`~/.claude/projects/`), letting any workstation point at its own location.
# Project hash subdirectory (e.g. "E--GT-KB") is itself derived by Claude from
# the project path; it can be overridden via env var if a project is moved.
_REPO_ROOT = Path(__file__).resolve().parent.parent
_TRANSCRIPT_BASE = Path(
    os.environ.get("CLAUDE_TRANSCRIPT_DIR", Path.home() / ".claude" / "projects")
)
_PROJECT_HASH = os.environ.get("CLAUDE_PROJECT_HASH", "E--GT-KB")
TRANSCRIPT_DIR = str(_TRANSCRIPT_BASE / _PROJECT_HASH)
OUTPUT_FILE = str(_REPO_ROOT / "docs" / "owner-messages-all.json")


def extract_text(content):
    """Extract plain text from various content formats."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict):
                if block.get("type") == "text":
                    parts.append(block.get("text", ""))
                elif "text" in block:
                    parts.append(block["text"])
            elif isinstance(block, str):
                parts.append(block)
        return "\n".join(parts)
    return str(content) if content else ""


def extract_human_messages(filepath):
    """Extract human role messages from a JSONL transcript."""
    messages = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue

                # Claude Code format: type="user" with message.content
                if record.get("type") == "user":
                    message = record.get("message", {})
                    if isinstance(message, dict):
                        content = message.get("content", "")
                    else:
                        content = str(message)

                    text = extract_text(content).strip()

                    # Skip empty, very short messages
                    if len(text) < 10:
                        continue
                    # Skip pure system reminders
                    if text.startswith("<system-reminder>") and not any(kw in text for kw in ["UserPromptSubmit", "SessionStart"]):
                        continue

                    messages.append({
                        "line": line_num,
                        "text": text[:8000],  # Cap at 8000 chars
                        "length": len(text)
                    })
    except Exception as e:
        print(f"  Error reading {filepath}: {e}", file=sys.stderr)

    return messages


def main():
    # Find all main transcript files (exclude subagent files)
    pattern = os.path.join(TRANSCRIPT_DIR, "*.jsonl")
    top_level = sorted(glob.glob(pattern))

    # Also check one level deep (session-id/session-id.jsonl)
    pattern2 = os.path.join(TRANSCRIPT_DIR, "*", "*.jsonl")
    nested = [f for f in sorted(glob.glob(pattern2))
              if "subagents" not in f]

    all_files = sorted(set(top_level + nested))
    print(f"Found {len(all_files)} transcript files")

    results = {}
    total_messages = 0
    total_chars = 0

    for filepath in all_files:
        basename = os.path.basename(filepath)
        session_id = basename.replace(".jsonl", "")

        messages = extract_human_messages(filepath)
        if messages:
            char_count = sum(m["length"] for m in messages)
            results[session_id] = {
                "file": filepath,
                "message_count": len(messages),
                "total_chars": char_count,
                "messages": messages
            }
            total_messages += len(messages)
            total_chars += char_count
            print(f"  {session_id}: {len(messages)} messages ({char_count:,} chars)")

    # Write output
    output = {
        "total_sessions": len(results),
        "total_messages": total_messages,
        "total_chars": total_chars,
        "sessions": results
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nDone: {len(results)} sessions, {total_messages} owner messages, {total_chars:,} total chars")
    print(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
