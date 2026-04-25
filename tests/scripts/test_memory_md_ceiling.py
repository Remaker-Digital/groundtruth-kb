"""Release-gate test: user-auto-memory MEMORY.md must stay below the
documented harness loading ceiling.

Per CLAUDE.md ("MEMORY.md is always loaded into your conversation
context -- lines after 200 will be truncated, so keep the index
concise"), the file is silently truncated when it exceeds the harness
load budget. The owner has observed this at session start with a
banner: "WARNING: MEMORY.md is 58.2KB (limit: 24.4KB) -- index entries
are too long." This test fails when the file exceeds 25,000 bytes
(24.4 KiB rounded up) so growth is caught at release time, not at
session start as silent truncation.

The test is skipped when the file is not present on the running
machine (clean checkout, fresh dev environment). It does not enforce
that user-auto-memory exists; it only enforces a ceiling when it does.

Authority:
- bridge/gtkb-startup-enhancements-p1-003.md REVISED §2.3
- bridge/gtkb-startup-enhancements-p1-004.md GO

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from pathlib import Path

import pytest

# 24.4 KiB rounded up. Banner and CLAUDE.md document 24.4KB; binary
# KiB matches the observed banner format (the same file at 59,913 bytes
# displays as "58.2KB" which is a binary-KiB rendering of 58.5 KiB
# rounded one-decimal-place down). 25,000 bytes gives us a small
# safety margin above the 24.4 KiB ceiling without bumping into it.
MEMORY_MD_CEILING_BYTES = 25_000


def _user_auto_memory_path(project_root: Path) -> Path:
    """Reverse-engineer Claude Code's project-hash path encoding.

    Claude Code stores user auto-memory under
    ``~/.claude/projects/<encoded-cwd>/memory/MEMORY.md`` where
    ``<encoded-cwd>`` replaces path separators with ``-`` and prefixes
    the drive letter on Windows. For ``E:\\GT-KB`` the encoding is
    ``E--GT-KB``.

    This helper derives the path from project_root rather than reading
    a harness internal so the test stays evergreen against project
    moves. On non-Windows platforms or non-standard layouts the
    derivation may not match; the test pytest-skips when the file
    is not present.
    """
    parts = project_root.resolve().parts
    drive = parts[0].rstrip(":\\/")
    rest = "-".join(p for p in parts[1:] if p)
    encoded = f"{drive}--{rest}" if drive and rest else (drive or rest)
    return Path.home() / ".claude" / "projects" / encoded / "memory" / "MEMORY.md"


def test_memory_md_under_ceiling() -> None:
    """Fail when MEMORY.md exceeds the 25,000-byte ceiling."""
    project_root = Path(__file__).resolve().parents[2]
    memory_path = _user_auto_memory_path(project_root)
    if not memory_path.exists():
        pytest.skip(
            f"User-auto-memory not present at {memory_path}; "
            "skip ceiling check (clean checkout or non-standard harness path)."
        )
    size = memory_path.stat().st_size
    assert size <= MEMORY_MD_CEILING_BYTES, (
        f"MEMORY.md is {size} bytes (~{size / 1024:.1f} KiB), exceeds the "
        f"documented {MEMORY_MD_CEILING_BYTES}-byte (~24.4 KiB) ceiling. "
        "Trim multi-line entries to one line each per the format documented "
        "in CLAUDE.md (`- [Title](file.md) -- one-line hook`)."
    )
