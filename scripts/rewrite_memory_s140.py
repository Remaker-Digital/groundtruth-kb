#!/usr/bin/env python3
"""
S140: Rewrite MEMORY.md — archive old sessions, remove migrated knowledge.

Operations:
  1. Append S134-S92 session logs to CLAUDE_ARCHIVE.md
  2. Rewrite MEMORY.md: keep Current Status + last 6 sessions + Quick Reference (trimmed)
     Remove: Owner Preferences (→ KB DOC-owner-preferences),
             Cross-Cutting Lessons (→ KB DOC-cross-cutting-lessons),
             Topic Files index (can ls memory/ instead)

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import io
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MEMORY_DIR = Path(r"C:\Users\micha\.claude\projects\E--Claude-Playground-CLAUDE-PROJECTS-Agent-Red-Customer-Engagement\memory")
MEMORY_FILE = MEMORY_DIR / "MEMORY.md"
ARCHIVE_FILE = PROJECT_ROOT / "CLAUDE_ARCHIVE.md"


def main():
    # Read current MEMORY.md
    lines = MEMORY_FILE.read_text(encoding="utf-8").splitlines(keepends=True)
    print(f"Read MEMORY.md: {len(lines)} lines")

    # Find section boundaries by line number (0-indexed)
    # Structure: Current Status (lines 0-9), Recent Sessions header (line 10),
    # S140-S135 (lines 11-16), S134-S92 (lines 17-57), archive refs (58-60),
    # Protected Files (62-64), Quick Reference (66-95), Owner Preferences (97-103),
    # Key Patterns & Lessons (105-172)

    # Extract sessions to archive (S134 through S92) — lines 18-58 (1-indexed)
    # In 0-indexed: lines 17-57
    archived_sessions = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        # S134 is at 1-indexed line 18 (0-indexed 17)
        # S92 is at 1-indexed line 58 (0-indexed 57)
        if i >= 17 and i <= 57:
            archived_sessions.append(line)

    print(f"Archiving {len(archived_sessions)} lines (S134-S92)")

    # 1. Append archived sessions to CLAUDE_ARCHIVE.md
    archive_content = ARCHIVE_FILE.read_text(encoding="utf-8")
    archive_addition = "\n\n---\n\n## Archived Session Logs (S134-S92)\n\n"
    archive_addition += "Archived from MEMORY.md during S140 knowledge migration.\n\n"
    for line in archived_sessions:
        archive_addition += line if line.endswith("\n") else line + "\n"

    ARCHIVE_FILE.write_text(archive_content + archive_addition, encoding="utf-8")
    print(f"✓ Appended {len(archived_sessions)} session lines to CLAUDE_ARCHIVE.md")

    # 2. Build new MEMORY.md
    new_memory = """# Agent Red Memory

## Current Status
"""
    # Keep Current Status bullets (lines 3-8, 0-indexed)
    for i in range(3, 9):
        new_memory += lines[i]
    # Keep blank + Recent Sessions header
    new_memory += "\n## Recent Sessions\n"
    # Keep S140-S135 (lines 11-16, 0-indexed)
    for i in range(11, 17):
        new_memory += lines[i]
    # Archive references
    new_memory += "- S134-S92: Archived to CLAUDE_ARCHIVE.md (S140 migration).\n"
    new_memory += "- S80-91: See CLAUDE_ARCHIVE.md.\n"
    new_memory += "- S38-79: See CLAUDE_ARCHIVE.md.\n"
    new_memory += "- S7-37: See CLAUDE_ARCHIVE.md.\n"

    # Protected Files
    new_memory += """
## Protected Files (DO NOT MODIFY)
- `branding/logo/SVG/icon-master.svg`, `branding/logo/SVG/primary-logo-no-wordmark.svg`
- `branding/logo/PNG/icon-master.png`, `branding/logo/PNG/primary-logo-no-wordmark.png`

## Quick Reference
"""
    # Keep Quick Reference lines 67-96 (1-indexed) = 66-95 (0-indexed)
    # But trim: remove Knowledge DB detailed description (line 95, 0-indexed 94)
    # and Codex deferred (line 96, 0-indexed 95)
    for i in range(67, 96):  # 1-indexed 68-96 = 0-indexed 67-95
        line_stripped = lines[i].strip()
        # Skip the long Knowledge DB self-description
        if line_stripped.startswith("- **Knowledge DB:**"):
            # Replace with compact version
            new_memory += "- **Knowledge DB:** `tools/knowledge-db/` — append-only SQLite, web UI at localhost:8090, Python API: `db.py`. Use `db.get_summary()` for current counts.\n"
        elif line_stripped.startswith("- **Codex deferred"):
            continue  # Skip — deferred items don't need session bootstrap
        else:
            new_memory += lines[i]

    # Add KB references (replacing removed sections)
    new_memory += """
## Project Knowledge (in Knowledge Database)
- **Cross-cutting lessons (48):** `DOC-cross-cutting-lessons` — Python, API, Cosmos, build, testing, Playwright, frontend, infrastructure patterns
- **Owner preferences (6):** `DOC-owner-preferences` — quality, process, product directives
- **Topic files (14):** `memory/*.md` — operational patterns (testing, deployment, cosmos-db, admin-ui, etc.)
- **Protected behaviors:** PB-* specs in KB — machine-verifiable assertions checked at session start
"""

    MEMORY_FILE.write_text(new_memory, encoding="utf-8")
    new_lines = new_memory.count("\n")
    print(f"✓ Rewrote MEMORY.md: {len(lines)} → {new_lines} lines")
    print(f"  Removed: Owner Preferences (→ DOC-owner-preferences)")
    print(f"  Removed: Cross-Cutting Lessons (→ DOC-cross-cutting-lessons)")
    print(f"  Removed: Topic Files index (→ ls memory/)")
    print(f"  Removed: S134-S92 session logs (→ CLAUDE_ARCHIVE.md)")
    print(f"  Trimmed: Knowledge DB self-description")


if __name__ == "__main__":
    main()
