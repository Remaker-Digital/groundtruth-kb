"""Release-gate test: in-root MEMORY.md must stay below the
documented harness loading ceiling.

Per CLAUDE.md ("MEMORY.md is always loaded into your conversation
context -- lines after 200 will be truncated, so keep the index
concise"), the file is silently truncated when it exceeds the harness
load budget. The owner has observed this at session start with a
banner: "WARNING: MEMORY.md is 58.2KB (limit: 24.4KB) -- index entries
are too long." This test fails when the file exceeds 25,000 bytes
(24.4 KiB rounded up) so growth is caught at release time, not at
session start as silent truncation.

The test enforces the ceiling on the in-root memory file. Active GT-KB memory
must not be sourced from a home-directory mirror.

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


def _memory_path(project_root: Path) -> Path:
    """Return the in-root active memory path."""
    return project_root / "memory" / "MEMORY.md"


def test_memory_md_under_ceiling() -> None:
    """Fail when MEMORY.md exceeds the 25,000-byte ceiling."""
    project_root = Path(__file__).resolve().parents[2]
    memory_path = _memory_path(project_root)
    if not memory_path.exists():
        pytest.skip(f"In-root memory not present at {memory_path}; skip ceiling check.")
    size = memory_path.stat().st_size
    assert size <= MEMORY_MD_CEILING_BYTES, (
        f"MEMORY.md is {size} bytes (~{size / 1024:.1f} KiB), exceeds the "
        f"documented {MEMORY_MD_CEILING_BYTES}-byte (~24.4 KiB) ceiling. "
        "Trim multi-line entries to one line each per the format documented "
        "in CLAUDE.md (`- [Title](file.md) -- one-line hook`)."
    )
