# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Regression guard for WI-3326 phantom-spec-citation re-point in SessionStart payload.

Authority: bridge/gtkb-wi3326-sessionstart-phantom-spec-citation-repoint-006.md (GO).
Specs: DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001,
SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001,
DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001.

WI-3326 defect: session_self_initialization.py, workstream_focus.py, and
_session_init_keyword.py cited three planned-but-never-created spec IDs in the
SessionStart payload. This guard asserts:
  (a) None of the phantom IDs appear in any of the eight approved target paths.
  (b) Each real replacement ID is present in the appropriate source file.
  (c) The three real replacement IDs exist in live current_specifications (ensuring
      the re-point targets are real specs, not future phantoms themselves).

Phantom IDs are split across concatenations to avoid triggering the no-phantom
rg scan that targets this file itself as one of the eight approved paths.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]

# Phantom IDs expressed as concatenations so this file does not contain the
# literal strings and thereby appear in its own no-phantom scan result.
_PHANTOM_1 = "ADR-SESSION-START-INIT-KEYWORD-" + "CONTRACT-001"
_PHANTOM_2 = "DCL-SESSION-START-INIT-KEYWORD-" + "MATCHING-001"
_PHANTOM_3 = "DCL-SESSION-START-APP-SCOPE-" + "BINDING-001"
_PHANTOMS = (_PHANTOM_1, _PHANTOM_2, _PHANTOM_3)

_REAL_IDS = (
    "DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001",
    "SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001",
    "DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001",
)

# Source files whose SessionStart payload citation strings are guarded.
_SOURCE_FILES = (
    _ROOT / "scripts" / "session_self_initialization.py",
    _ROOT / "scripts" / "workstream_focus.py",
    _ROOT / "scripts" / "_session_init_keyword.py",
)

# All eight approved target paths from the GO'd bridge proposal.
_ALL_TARGET_FILES = (
    _ROOT / "scripts" / "session_self_initialization.py",
    _ROOT / "scripts" / "workstream_focus.py",
    _ROOT / "scripts" / "_session_init_keyword.py",
    _ROOT / "platform_tests" / "scripts" / "test_session_self_initialization_spec_citation_existence.py",
    _ROOT / "platform_tests" / "hooks" / "test_workstream_focus.py",
    _ROOT / "platform_tests" / "scripts" / "test_session_self_initialization.py",
    _ROOT / "platform_tests" / "scripts" / "test_workstream_focus_hook_parity.py",
    _ROOT / "platform_tests" / "scripts" / "test_session_init_keyword_matching.py",
)

_DB_PATH = _ROOT / "groundtruth.db"


def _read(path: Path) -> str:
    assert path.is_file(), f"required file missing: {path}"
    return path.read_text(encoding="utf-8")


def test_phantoms_absent_from_all_target_files() -> None:
    """None of the three phantom IDs appear in any of the eight approved target paths."""
    offenders: list[str] = []
    for path in _ALL_TARGET_FILES:
        text = _read(path)
        for phantom in _PHANTOMS:
            if phantom in text:
                offenders.append(f"{path.name}: contains {phantom}")
    assert not offenders, "phantom citation(s) found:\n" + "\n".join(offenders)


def test_real_ids_present_in_source_files() -> None:
    """Each real replacement spec ID appears in at least one SessionStart source file."""
    source_text = "\n".join(_read(p) for p in _SOURCE_FILES)
    missing = [rid for rid in _REAL_IDS if rid not in source_text]
    assert not missing, f"replacement IDs missing from SessionStart source files: {missing}"


def test_replacement_ids_exist_in_membase() -> None:
    """The three real replacement IDs governing init-keyword behavior exist in MemBase."""
    if not _DB_PATH.is_file():
        pytest.skip(f"groundtruth.db not found at {_DB_PATH}")
    conn = sqlite3.connect(_DB_PATH)
    try:
        rows = conn.execute(
            "SELECT id FROM current_specifications WHERE id IN (?, ?, ?)",
            list(_REAL_IDS),
        ).fetchall()
    finally:
        conn.close()
    found = {row[0] for row in rows}
    missing = [rid for rid in _REAL_IDS if rid not in found]
    assert not missing, f"replacement IDs absent from MemBase current_specifications: {missing}"
