# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for the state-location default-deny doctor check (WI-6739).

Mirrors ``test_doctor_stale_test_slots.py``, the sibling test for the other
``@register_check`` module. All cases use ``tmp_path``; none touches the live
tree, so the tests do not depend on the repository's current registration state.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from groundtruth_kb.project.checks import get_registered_checks
from groundtruth_kb.project.checks.state_location_registry import (
    FORBIDDEN_ROOTS,
    _is_permitted,
    check_state_location_registry,
)

REGISTRY_REL = "config/registry/sot-artifacts.toml"


def _write_registry(root: Path, storage_paths: list[str]) -> None:
    root.joinpath("config", "registry").mkdir(parents=True, exist_ok=True)
    body = "\n\n".join(f'[[artifacts]]\nid = "a{i}"\nstorage_path = "{p}"' for i, p in enumerate(storage_paths))
    root.joinpath(REGISTRY_REL).write_text(body + "\n", encoding="utf-8")


def test_registered_directory_passes(tmp_path: Path) -> None:
    (tmp_path / ".groundtruth" / "permitted").mkdir(parents=True)
    _write_registry(tmp_path, [".groundtruth/permitted"])
    result = check_state_location_registry(tmp_path)
    assert result.status == "pass"
    assert result.required is True


def test_unregistered_directory_fails(tmp_path: Path) -> None:
    (tmp_path / ".groundtruth" / "rogue").mkdir(parents=True)
    _write_registry(tmp_path, [".groundtruth/permitted"])
    result = check_state_location_registry(tmp_path)
    assert result.status == "fail"
    assert result.required is True
    assert ".groundtruth/rogue" in result.message


def test_unregistered_loose_file_fails(tmp_path: Path) -> None:
    """Files are violations too -- the decisive case.

    ``.claude/session`` holds zero directories and only loose files, and those
    files are the session-object population. A directories-only rule reports
    clean for a root that is entirely non-compliant.
    """
    session = tmp_path / ".claude" / "session"
    session.mkdir(parents=True)
    (session / "handoff-abc.md").write_text("x", encoding="utf-8")
    _write_registry(tmp_path, [".groundtruth/permitted"])
    result = check_state_location_registry(tmp_path)
    assert result.status == "fail"
    assert ".claude/session/handoff-abc.md" in result.message


def test_discriminates_config_from_state_inside_one_parent(tmp_path: Path) -> None:
    """Registered metadata and unregistered state under one ordinary parent differ."""
    state = tmp_path / ".groundtruth"
    state.mkdir()
    (state / "metadata.json").write_text("{}", encoding="utf-8")
    (state / "unregistered.json").write_text("{}", encoding="utf-8")
    (state / "unregistered-directory").mkdir()
    _write_registry(tmp_path, [".groundtruth/metadata.json"])
    result = check_state_location_registry(tmp_path)
    assert result.status == "fail"
    assert "metadata.json" not in result.message
    assert ".groundtruth/unregistered.json" in result.message
    assert ".groundtruth/unregistered-directory" in result.message


def test_rejects_nested_state_under_retired_harness_root(tmp_path: Path) -> None:
    """A retired root is rejected without interpreting files below it."""
    (tmp_path / "harness-state" / "codex" / "session-envelopes").mkdir(parents=True)
    # Only a sibling config file is registered, not the harness directory.
    _write_registry(tmp_path, ["harness-state/codex/session-startup-preferences.json"])
    result = check_state_location_registry(tmp_path)
    assert result.status == "fail"
    assert "harness-state" in result.message


@pytest.mark.parametrize("location", FORBIDDEN_ROOTS)
@pytest.mark.parametrize("kind", ["file", "directory"])
@pytest.mark.parametrize("registered", [False, True])
def test_forbidden_roots_cannot_be_permitted_by_registration(tmp_path, location, kind, registered):
    path = tmp_path / location
    path.parent.mkdir(parents=True, exist_ok=True)
    if kind == "file":
        path.write_text("inert forbidden state", encoding="utf-8")
    else:
        path.mkdir()
    if registered:
        _write_registry(tmp_path, [location, ".groundtruth"])
    result = check_state_location_registry(tmp_path)
    assert result.status == "fail" and result.required is True
    assert location in result.message
    assert "Register permitted" not in result.message
    assert not _is_permitted(location, {location, ".groundtruth"})
    assert not _is_permitted(location + "/nested.json", {location, ".groundtruth"})


def test_ancestor_registration_permits_contents(tmp_path: Path) -> None:
    """A registered container permits what is inside it."""
    approvals = tmp_path / ".groundtruth" / "metadata"
    approvals.mkdir(parents=True)
    (approvals / "packet.json").write_text("{}", encoding="utf-8")
    _write_registry(tmp_path, [".groundtruth/metadata"])
    assert check_state_location_registry(tmp_path).status == "pass"


def test_trailing_slash_in_registration_is_tolerated(tmp_path: Path) -> None:
    (tmp_path / ".groundtruth" / "permitted").mkdir(parents=True)
    _write_registry(tmp_path, [".groundtruth/permitted/"])
    assert check_state_location_registry(tmp_path).status == "pass"


def test_missing_registry_warns_rather_than_fails(tmp_path: Path) -> None:
    """A missing registry is a different defect from an unregistered location.

    Failing here would make the check fire loudly on a tree it cannot actually
    assess, which trains readers to ignore it.
    """
    (tmp_path / ".groundtruth" / "rogue").mkdir(parents=True)
    result = check_state_location_registry(tmp_path)
    assert result.status == "warning"
    assert result.found is False


def test_absent_state_roots_pass(tmp_path: Path) -> None:
    _write_registry(tmp_path, [".groundtruth/permitted"])
    assert check_state_location_registry(tmp_path).status == "pass"


def test_unscanned_roots_are_ignored(tmp_path: Path) -> None:
    """Only the closed set of state roots is scanned.

    A whole-tree walk would classify ordinary source directories as state.
    """
    (tmp_path / "scripts" / "whatever").mkdir(parents=True)
    (tmp_path / "applications" / "Agent_Red").mkdir(parents=True)
    _write_registry(tmp_path, [".groundtruth/permitted"])
    assert check_state_location_registry(tmp_path).status == "pass"


def test_message_truncates_but_reports_full_count(tmp_path: Path) -> None:
    root = tmp_path / ".groundtruth"
    root.mkdir(parents=True)
    for i in range(20):
        (root / f"rogue{i:02d}").mkdir()
    _write_registry(tmp_path, [".groundtruth/permitted"])
    result = check_state_location_registry(tmp_path)
    assert result.status == "fail"
    assert "20 unregistered state location(s)" in result.message
    assert "..." in result.message


def test_registered_via_pkgutil_discovery(tmp_path: Path) -> None:
    """ADR-REGISTRY-DISCOVERY-001: discovered without editing doctor.py."""
    checks = get_registered_checks()
    assert "state_location_registry" in checks
    _write_registry(tmp_path, [".groundtruth/permitted"])
    result = checks["state_location_registry"](tmp_path)
    assert result.required is True
