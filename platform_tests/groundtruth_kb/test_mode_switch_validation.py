"""Tests for groundtruth_kb.mode_switch.validation.

Covers SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001 acceptance criterion #2:
validation against authoritative role, bridge, and session-state artifacts
before writing durable state. Includes the live-INDEX compatibility
regression cases Codex required at bridge -011 F1 (WITHDRAWN rows accepted;
missing referenced files tolerated).

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from groundtruth_kb.mode_switch.validation import (
    validate_bridge_artifact,
    validate_role_artifact,
    validate_session_state_artifact,
)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    return tmp_path


def test_validate_role_artifact_missing_file_fails(project_root: Path) -> None:
    result = validate_role_artifact(project_root)
    assert not result.is_valid
    assert result.axis == "role"


def test_validate_role_artifact_parseable_passes(project_root: Path) -> None:
    _write(
        project_root / "harness-state" / "role-assignments.json",
        json.dumps({"harnesses": {"A": {"role": ["prime-builder"]}}}),
    )
    result = validate_role_artifact(project_root)
    assert result.is_valid


def test_validate_role_artifact_unknown_token_fails(project_root: Path) -> None:
    _write(
        project_root / "harness-state" / "role-assignments.json",
        json.dumps({"harnesses": {"A": {"role": ["mystery-role"]}}}),
    )
    result = validate_role_artifact(project_root)
    assert not result.is_valid


def test_validate_bridge_artifact_missing_fails(project_root: Path) -> None:
    result = validate_bridge_artifact(project_root)
    assert not result.is_valid
    assert result.axis == "bridge"


def test_validate_bridge_artifact_unknown_status_token_fails(project_root: Path) -> None:
    _write(
        project_root / "bridge" / "INDEX.md",
        "Document: foo\nFROBNICATED: bridge/foo-001.md\n",
    )
    result = validate_bridge_artifact(project_root)
    assert not result.is_valid


def test_validate_bridge_artifact_accepts_withdrawn_status_rows(project_root: Path) -> None:
    """REVISED-3 regression: WITHDRAWN is part of the canonical vocabulary."""
    _write(
        project_root / "bridge" / "INDEX.md",
        "Document: foo\nWITHDRAWN: bridge/foo-002.md\nNEW: bridge/foo-001.md\n",
    )
    result = validate_bridge_artifact(project_root)
    assert result.is_valid


def test_validate_bridge_artifact_tolerates_missing_referenced_bridge_files(
    project_root: Path,
) -> None:
    """REVISED-3 regression: historical INDEX entries may reference removed files.

    The validator MUST NOT make file-existence of referenced bridge files
    a precondition for mode-switch safety.
    """
    _write(
        project_root / "bridge" / "INDEX.md",
        "Document: ghost\nNEW: bridge/ghost-thread-001.md\n",
    )
    # The referenced file is intentionally not on disk.
    assert not (project_root / "bridge" / "ghost-thread-001.md").exists()
    result = validate_bridge_artifact(project_root)
    assert result.is_valid


def test_validate_bridge_artifact_no_document_entry_fails(project_root: Path) -> None:
    _write(project_root / "bridge" / "INDEX.md", "# Bridge Index\n\n<!-- empty -->\n")
    result = validate_bridge_artifact(project_root)
    assert not result.is_valid


def test_validate_session_state_artifact_missing_is_ok(project_root: Path) -> None:
    """Missing session-state file is acceptable (single-harness installs may lack one)."""
    result = validate_session_state_artifact(project_root)
    assert result.is_valid


def test_validate_session_state_artifact_unparseable_fails(project_root: Path) -> None:
    _write(project_root / ".claude" / "session" / "work-subject.json", "{not json")
    result = validate_session_state_artifact(project_root)
    assert not result.is_valid
