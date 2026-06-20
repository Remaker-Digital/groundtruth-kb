"""Tests for groundtruth_kb.mode_switch.validation.

Covers SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001 acceptance criterion #2:
validation against authoritative role, bridge, and session-state artifacts
before writing durable state.

The bridge-axis cases exercise the numbered-bridge-file model (``*-NNN.md``):
the validator's fatal floor is structural coherence (directory present, at
least one numbered file, all readable), while a non-canonical leading status
token in an existing numbered file is grandfathered legacy observability per
the file-bridge-protocol Body Status-Token Rule (WI-4696; GO -002). The earlier
``bridge/INDEX.md``-based cases were retired with WI-4696 because the validator
no longer reads ``bridge/INDEX.md``.

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
    # WI-3342 IP-5: validate_role_artifact reads the DB-backed registry
    # projection (harness-state/harness-registry.json), whose ``harnesses`` is a
    # LIST of unified records, not the retired role-assignments.json dict.
    _write(
        project_root / "harness-state" / "harness-registry.json",
        json.dumps({"harnesses": [{"id": "A", "role": ["prime-builder"]}]}),
    )
    result = validate_role_artifact(project_root)
    assert result.is_valid


def test_validate_role_artifact_unknown_token_fails(project_root: Path) -> None:
    # WI-3342 IP-5: validate_role_artifact reads the registry projection LIST.
    _write(
        project_root / "harness-state" / "harness-registry.json",
        json.dumps({"harnesses": [{"id": "A", "role": ["mystery-role"]}]}),
    )
    result = validate_role_artifact(project_root)
    assert not result.is_valid


def test_validate_bridge_artifact_missing_fails(project_root: Path) -> None:
    """Fatal floor (GO -002 condition 1): no ``bridge/`` directory fails."""
    result = validate_bridge_artifact(project_root)
    assert not result.is_valid
    assert result.axis == "bridge"


def test_validate_bridge_artifact_no_numbered_files_fails(project_root: Path) -> None:
    """Fatal floor (condition 1): a ``bridge/`` dir with no numbered files fails.

    Only ``*-NNN.md`` files are bridge-axis input; a bare ``INDEX.md`` (or any
    non-numbered file) is not a numbered bridge file, so the corpus is empty.
    """
    _write(project_root / "bridge" / "INDEX.md", "# Bridge Index\n\n<!-- empty -->\n")
    result = validate_bridge_artifact(project_root)
    assert not result.is_valid


def test_validate_bridge_artifact_ignores_non_numbered_files(project_root: Path) -> None:
    """Non-numbered files (e.g. ``INDEX.md``) are ignored; numbered files drive validity."""
    _write(project_root / "bridge" / "INDEX.md", "Document: foo\nFROBNICATED: x\n")
    _write(project_root / "bridge" / "foo-001.md", "NEW\n\n# proposal\n")
    result = validate_bridge_artifact(project_root)
    assert result.is_valid


def test_validate_bridge_artifact_grandfathers_unknown_token_in_numbered_file(
    project_root: Path,
) -> None:
    """GO -002 condition 2: a numbered file with a non-canonical first line is
    grandfathered legacy, not a fatal blocker."""
    _write(project_root / "bridge" / "legacy-001.md", "Document: foo\nbody\n")
    result = validate_bridge_artifact(project_root)
    assert result.is_valid


def test_validate_bridge_artifact_accepts_canonical_withdrawn(project_root: Path) -> None:
    """WITHDRAWN is part of the canonical vocabulary; canonical numbered files validate."""
    _write(project_root / "bridge" / "foo-001.md", "NEW\n")
    _write(project_root / "bridge" / "foo-002.md", "WITHDRAWN\n")
    result = validate_bridge_artifact(project_root)
    assert result.is_valid


def test_validate_bridge_artifact_grandfathers_legacy_with_canonical(
    project_root: Path,
) -> None:
    """GO -002 condition 5: a mixed corpus of a legacy (non-canonical first line)
    numbered file plus a canonical numbered file is accepted, and the legacy file
    is surfaced as non-fatal observability (condition 3)."""
    _write(project_root / "bridge" / "legacy-001.md", "Document: legacy\nbody\n")
    _write(project_root / "bridge" / "fresh-001.md", "NEW\n\n# fresh proposal\n")
    result = validate_bridge_artifact(project_root)
    assert result.is_valid
    assert any("grandfathered legacy" in note for note in result.notes)


def test_validate_bridge_artifact_accepted_blocked_are_legacy_not_canonical(
    project_root: Path,
) -> None:
    """GO -002 condition 3: ``ACCEPTED`` / ``BLOCKED`` are NOT canonical tokens;
    historical files using them are grandfathered legacy observability, never fatal."""
    _write(project_root / "bridge" / "hist-001.md", "ACCEPTED\n")
    _write(project_root / "bridge" / "hist-002.md", "BLOCKED\n")
    _write(project_root / "bridge" / "hist-003.md", "NEW\n")
    result = validate_bridge_artifact(project_root)
    assert result.is_valid
    # 2 of the 3 numbered files use non-canonical legacy tokens.
    assert any("2 grandfathered legacy/unknown" in note for note in result.notes)


def test_validate_session_state_artifact_missing_is_ok(project_root: Path) -> None:
    """Missing session-state file is acceptable (single-harness installs may lack one)."""
    result = validate_session_state_artifact(project_root)
    assert result.is_valid


def test_validate_session_state_artifact_unparseable_fails(project_root: Path) -> None:
    _write(project_root / ".claude" / "session" / "work-subject.json", "{not json")
    result = validate_session_state_artifact(project_root)
    assert not result.is_valid
