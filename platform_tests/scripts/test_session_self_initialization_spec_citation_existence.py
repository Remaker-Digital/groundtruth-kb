# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Retained init sources cite existing formal contracts, never phantom IDs.

The retired startup generator and focus helper no longer participate in session
initialization. These assertions cover the surviving init helper and its tests.
Phantom IDs are split below so the scanner does not match its own patterns.
"""

from __future__ import annotations

from pathlib import Path

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
_SOURCE_FILES = (_ROOT / "scripts" / "_session_init_keyword.py",)

# Surviving authored sources and regression tests.
_ALL_TARGET_FILES = (
    _ROOT / "scripts" / "_session_init_keyword.py",
    _ROOT / "platform_tests" / "scripts" / "test_session_self_initialization_spec_citation_existence.py",
    _ROOT / "platform_tests" / "scripts" / "test_session_init_keyword_matching.py",
)


def _read(path: Path) -> str:
    assert path.is_file(), f"required file missing: {path}"
    return path.read_text(encoding="utf-8")


def test_phantoms_absent_from_all_target_files() -> None:
    """None of the three phantom IDs appear in any of the surviving approved target paths."""
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
