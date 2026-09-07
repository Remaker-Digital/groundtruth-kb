"""TEST-12147 — close and wrap harvest without persisted handoff objects.

Linked acceptance test for WI-6952 (PROJECT-GTKB-WI6952-EPHEMERAL-HANDOFF).

Canon s5 holds that a handoff is ephemeral owner-copyable text and "never an on-disk
or database authority object", that "no fact required for continuation may exist only
in the handoff", and that the receiving context re-queries canonical state. Canon s17
and s24 additionally forbid the ``harness-state`` root.

WI-6952 requires retiring the persisted carriers and every consumer that treats them as
recovery or authority. Measured, those carriers are TWO, not one:

1. the MemBase ``session_prompts`` store; and
2. the on-disk session-envelope archive at
   ``harness-state/<harness>/session-envelope-archive/<closed_at>-session-envelope.json``,
   which ``session/wrap.py`` writes through ``close_session`` and which
   ``session/handoff.py`` reads to compose a handoff.

SCOPE. ``session_snapshots`` and ``session_role_attestations`` are NOT asserted here.
WI-6940 owns their removal, and WI-6952 declares a ``terminal_published`` dependency on
it; asserting them here would duplicate predecessor-owned scope. The live purge of
existing ``session_prompts`` rows is likewise out of scope: this module asserts that no
code path creates, reads, or consumes the carriers, not that historical rows are gone.

All tests are expected to FAIL at proposal time; that red preimage is the point.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

SRC = REPO_ROOT / "groundtruth-kb" / "src" / "groundtruth_kb"
DB = SRC / "db.py"
CLI_HANDOFF = SRC / "cli_session_handoff.py"
WRAP = SRC / "session" / "wrap.py"
HANDOFF = SRC / "session" / "handoff.py"
GLOSSARY = REPO_ROOT / ".harness-baseline-configuration" / "rules" / "canonical-terminology.md"

SESSION_START_HOOKS = (
    REPO_ROOT / ".harness-baseline-configuration" / "hooks" / "assertion-check.py",
    REPO_ROOT / "config" / "hooks" / "gtkb-assertion-check.py",
    REPO_ROOT / "groundtruth-kb" / "templates" / "hooks" / "assertion-check.py",
)

PROMPT_STORE_API = (
    "insert_session_prompt",
    "get_next_session_prompt",
    "consume_session_prompt",
    "list_session_prompts",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_close_wrap_harvest_without_persisted_objects() -> None:
    """No persisted prompt-record store or accessor survives in the canonical DB layer."""
    source = _read(DB)
    survivors = [name for name in PROMPT_STORE_API if f"def {name}(" in source]
    assert survivors == [], (
        f"session_prompts store accessors still defined in db.py: {survivors}; "
        "canon s5 forbids a database authority object for a handoff"
    )
    assert "CREATE TABLE IF NOT EXISTS session_prompts" not in source, (
        "the session_prompts table is still created by the canonical schema"
    )


def test_wrap_produces_no_session_envelope_archive() -> None:
    """``::wrap`` harvests without writing a persisted envelope archive."""
    if not WRAP.exists():
        return
    source = _read(WRAP)
    assert "archive_path" not in source, (
        "session/wrap.py still produces an archive path; canon s5 forbids wrap persisting a session object"
    )


def test_handoff_reads_no_archived_envelope() -> None:
    """Handoff composition re-queries canonical state, not an on-disk archive."""
    if not HANDOFF.exists():
        return
    source = _read(HANDOFF)
    assert "session-envelope-archive" not in source, (
        "session/handoff.py still reads the on-disk session-envelope archive"
    )
    assert "harness-state" not in source, (
        "session/handoff.py still resolves a path under the forbidden harness-state root"
    )


def test_handoff_creates_no_persisted_prompt_row() -> None:
    """Handoff generation writes no durable prompt record."""
    if not HANDOFF.exists():
        return
    assert "session_prompts" not in _read(HANDOFF), (
        "session/handoff.py still creates a session_prompts row for the next session"
    )


def test_no_session_start_hook_consumes_a_handoff_prompt() -> None:
    """No SessionStart hook injects a prior session's handoff into a new context."""
    offenders = [
        path.relative_to(REPO_ROOT).as_posix()
        for path in SESSION_START_HOOKS
        if path.exists() and "consume_session_prompt" in _read(path)
    ]
    assert offenders == [], f"SessionStart hooks still consume a stored handoff prompt: {offenders}"


def test_no_cli_read_surface_for_stored_handoff_prompts() -> None:
    """The handoff CLI exposes no read-back of a persisted prompt row."""
    if not CLI_HANDOFF.exists():
        return
    assert "session_prompts" not in _read(CLI_HANDOFF), (
        "cli_session_handoff.py still reads or writes the session_prompts store"
    )


def test_glossary_defines_no_persisted_prompt_record() -> None:
    """The canonical glossary no longer names a persisted handoff-prompt record."""
    assert "session_prompts" not in _read(GLOSSARY), (
        "canonical-terminology.md still defines session_prompts as a supporting record"
    )
