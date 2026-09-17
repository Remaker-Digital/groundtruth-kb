"""Component checks for retired handoff storage and its former source consumers.

The linked TEST-12147 / WI-6952 contract additionally requires complete scoped
canonical harvest and fresh receiving contexts. These checks do not establish
that full contract. The legacy SQLite class is not the current authority service;
its removed prompt API is tested directly, and absence checks cover only the
named former files. No production database or generated projection is changed.
"""

from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest
from groundtruth_kb.db import KnowledgeDB

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
    "_next_session_prompt_version",
    "insert_session_prompt",
    "get_session_prompt",
    "get_session_prompt_by_idempotency_key",
    "get_next_session_prompt",
    "consume_session_prompt",
    "list_session_prompts",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_close_wrap_harvest_without_persisted_objects(tmp_path: Path) -> None:
    """Retire the real legacy store/API without treating this as full harvest proof."""
    path = tmp_path / "legacy.db"
    db = KnowledgeDB(path)
    try:
        with sqlite3.connect(path) as connection:
            tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            assert "session_prompts" not in tables
            indexes = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='index'")}
            assert "idx_session_prompts_session" not in indexes
        for name in PROMPT_STORE_API:
            with pytest.raises(AttributeError):
                getattr(db, name)

        # Emulate an old database solely in this disposable fixture. Removing
        # the API does not silently purge existing bytes or make them recovery
        # inputs; the ordinary native context workflow is qualified separately.
        with sqlite3.connect(path) as connection:
            connection.execute("CREATE TABLE session_prompts (rowid INTEGER PRIMARY KEY, prompt_text TEXT)")
            connection.execute("INSERT INTO session_prompts VALUES (1, 'OLD_PROMPT_SENTINEL')")
            connection.execute(
                "INSERT INTO assertion_runs (spec_id,spec_version,run_at,overall_passed,results,triggered_by) "
                "VALUES ('SPEC-FIXTURE',1,'2026-01-01T00:00:00Z',0,'{}','fixture')"
            )
        with sqlite3.connect(path) as connection:
            before = list(connection.iterdump())
        exported = tmp_path / "selected-legacy-tables.json"
        assert Path(db.export_json(exported)) == exported
        output = json.loads(exported.read_text(encoding="utf-8"))
        assert "session_prompts" not in output["tables"]
        assert "OLD_PROMPT_SENTINEL" not in exported.read_text(encoding="utf-8")
        assert output["tables"]["assertion_runs"][0]["spec_id"] == "SPEC-FIXTURE"
        with sqlite3.connect(path) as connection:
            assert list(connection.iterdump()) == before
    finally:
        db.close()


def test_wrap_produces_no_session_envelope_archive(tmp_path: Path) -> None:
    """Removed archive commands cannot recreate stores; this is not full wrap."""
    if WRAP.exists():
        assert "archive_path" not in _read(WRAP)
    marker = tmp_path / "unrelated.txt"
    marker.write_text("Preserve unrelated context bytes.\n", encoding="utf-8")
    before = {p.name: p.read_bytes() for p in tmp_path.iterdir() if p.is_file()}
    for name in (
        "harvest_session_deliberations.py",
        "deliberation_health.py",
        "inventory_lo_bridge_history_backfill.py",
    ):
        path = REPO_ROOT / "scripts" / name
        assert not path.exists(), f"Retired bridge-archive route remains: {path}"
        result = subprocess.run(
            [sys.executable, str(path)],
            cwd=tmp_path,
            capture_output=True,
            encoding="utf-8",
            timeout=10,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        assert result.returncode != 0 and not result.stdout
        assert {p.name: p.read_bytes() for p in tmp_path.iterdir() if p.is_file()} == before
        assert not any(p.is_dir() for p in tmp_path.iterdir())


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
