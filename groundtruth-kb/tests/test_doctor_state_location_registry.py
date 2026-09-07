# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for the state-location default-deny doctor check (WI-6739).

Mirrors ``test_doctor_stale_test_slots.py``, the sibling test for the other
``@register_check`` module. All cases use ``tmp_path``; none touches the live
tree, so the tests do not depend on the repository's current registration state.
"""

from __future__ import annotations

from pathlib import Path

from groundtruth_kb.project.checks import get_registered_checks
from groundtruth_kb.project.checks.state_location_registry import (
    check_state_location_registry,
)

REGISTRY_REL = "config/registry/sot-artifacts.toml"


def _write_registry(root: Path, storage_paths: list[str]) -> None:
    root.joinpath("config", "registry").mkdir(parents=True, exist_ok=True)
    body = "\n\n".join(f'[[artifacts]]\nid = "a{i}"\nstorage_path = "{p}"' for i, p in enumerate(storage_paths))
    root.joinpath(REGISTRY_REL).write_text(body + "\n", encoding="utf-8")


def test_registered_directory_passes(tmp_path: Path) -> None:
    (tmp_path / ".gtkb-state" / "permitted").mkdir(parents=True)
    _write_registry(tmp_path, [".gtkb-state/permitted"])
    result = check_state_location_registry(tmp_path)
    assert result.status == "pass"
    assert result.required is True


def test_unregistered_directory_fails(tmp_path: Path) -> None:
    (tmp_path / ".gtkb-state" / "rogue").mkdir(parents=True)
    _write_registry(tmp_path, [".gtkb-state/permitted"])
    result = check_state_location_registry(tmp_path)
    assert result.status == "fail"
    assert result.required is True
    assert ".gtkb-state/rogue" in result.message


def test_unregistered_loose_file_fails(tmp_path: Path) -> None:
    """Files are violations too -- the decisive case.

    ``.claude/session`` holds zero directories and only loose files, and those
    files are the session-object population. A directories-only rule reports
    clean for a root that is entirely non-compliant.
    """
    session = tmp_path / ".claude" / "session"
    session.mkdir(parents=True)
    (session / "handoff-abc.md").write_text("x", encoding="utf-8")
    _write_registry(tmp_path, [".gtkb-state"])
    result = check_state_location_registry(tmp_path)
    assert result.status == "fail"
    assert ".claude/session/handoff-abc.md" in result.message


def test_discriminates_config_from_state_inside_one_parent(tmp_path: Path) -> None:
    """The core requirement: same parent, opposite classifications.

    ``harness-state/`` holds legitimate per-harness configuration and
    illegitimate per-harness session state side by side. Classification must be
    by longest-prefix match on the path, never by parent directory.
    """
    harness = tmp_path / "harness-state" / "claude"
    harness.mkdir(parents=True)
    (harness / "active-workspace.md").write_text("x", encoding="utf-8")
    (harness / "session-lifecycle-guard.json").write_text("{}", encoding="utf-8")
    (harness / "session-envelope-archive").mkdir()
    _write_registry(tmp_path, ["harness-state/claude/active-workspace.md"])

    result = check_state_location_registry(tmp_path)
    assert result.status == "fail"
    # Registered per-harness CONFIG is not reported.
    assert "active-workspace.md" not in result.message
    # Unregistered per-harness STATE is reported, both file and directory.
    assert "harness-state/claude/session-lifecycle-guard.json" in result.message
    assert "harness-state/claude/session-envelope-archive" in result.message


def test_descends_one_level_under_harness_state(tmp_path: Path) -> None:
    """Per-harness state is invisible at depth 1 and must be found at depth 2."""
    (tmp_path / "harness-state" / "codex" / "session-envelopes").mkdir(parents=True)
    # Only a sibling config file is registered, not the harness directory.
    _write_registry(tmp_path, ["harness-state/codex/session-startup-preferences.json"])
    result = check_state_location_registry(tmp_path)
    assert result.status == "fail"
    assert "harness-state/codex/session-envelopes" in result.message


def test_blanket_container_registration_defeats_the_check(tmp_path: Path) -> None:
    """Registering a container over a state tree permits everything inside it.

    This documents a hazard rather than a bug. Ancestor matching is required --
    a registered ``.groundtruth/formal-artifact-approvals/`` must permit the
    packets inside it -- but the same rule means a container registered over a
    state tree grants blanket permission and silently disables enforcement
    beneath it.

    This is precisely why WI-6739 narrows the existing ``opaque_container``
    registrations on ``.gtkb-state/`` and ``.claude/session/`` as part of the
    same work: without that narrowing, one registry row would grant blanket
    authority over the very tree the other rows enumerate, and this check would
    report ``pass`` over an entirely unregistered subtree.

    The test exists so that if someone later re-registers a broad container and
    the check goes quiet, the reason is discoverable rather than mysterious.
    """
    (tmp_path / "harness-state" / "codex" / "session-envelopes").mkdir(parents=True)
    (tmp_path / "harness-state" / "codex" / "session-lifecycle-guard.json").write_text("{}", encoding="utf-8")
    _write_registry(tmp_path, ["harness-state/codex"])
    result = check_state_location_registry(tmp_path)
    assert result.status == "pass", (
        "blanket container registration is expected to permit contents; "
        "if this now fails, ancestor matching changed and the narrowing "
        "requirement in WI-6739 should be revisited"
    )


def test_ancestor_registration_permits_contents(tmp_path: Path) -> None:
    """A registered container permits what is inside it."""
    approvals = tmp_path / ".groundtruth" / "formal-artifact-approvals"
    approvals.mkdir(parents=True)
    (approvals / "packet.json").write_text("{}", encoding="utf-8")
    _write_registry(tmp_path, [".groundtruth/formal-artifact-approvals"])
    assert check_state_location_registry(tmp_path).status == "pass"


def test_trailing_slash_in_registration_is_tolerated(tmp_path: Path) -> None:
    (tmp_path / ".gtkb-state" / "permitted").mkdir(parents=True)
    _write_registry(tmp_path, [".gtkb-state/permitted/"])
    assert check_state_location_registry(tmp_path).status == "pass"


def test_missing_registry_warns_rather_than_fails(tmp_path: Path) -> None:
    """A missing registry is a different defect from an unregistered location.

    Failing here would make the check fire loudly on a tree it cannot actually
    assess, which trains readers to ignore it.
    """
    (tmp_path / ".gtkb-state" / "rogue").mkdir(parents=True)
    result = check_state_location_registry(tmp_path)
    assert result.status == "warning"
    assert result.found is False


def test_absent_state_roots_pass(tmp_path: Path) -> None:
    _write_registry(tmp_path, [".gtkb-state/permitted"])
    assert check_state_location_registry(tmp_path).status == "pass"


def test_unscanned_roots_are_ignored(tmp_path: Path) -> None:
    """Only the closed set of state roots is scanned.

    A whole-tree walk would classify ordinary source directories as state.
    """
    (tmp_path / "scripts" / "whatever").mkdir(parents=True)
    (tmp_path / "applications" / "Agent_Red").mkdir(parents=True)
    _write_registry(tmp_path, [".gtkb-state/permitted"])
    assert check_state_location_registry(tmp_path).status == "pass"


def test_message_truncates_but_reports_full_count(tmp_path: Path) -> None:
    root = tmp_path / ".gtkb-state"
    root.mkdir(parents=True)
    for i in range(20):
        (root / f"rogue{i:02d}").mkdir()
    _write_registry(tmp_path, ["harness-state"])
    result = check_state_location_registry(tmp_path)
    assert result.status == "fail"
    assert "20 unregistered state location(s)" in result.message
    assert "..." in result.message


def test_registered_via_pkgutil_discovery(tmp_path: Path) -> None:
    """ADR-REGISTRY-DISCOVERY-001: discovered without editing doctor.py."""
    checks = get_registered_checks()
    assert "state_location_registry" in checks
    _write_registry(tmp_path, [".gtkb-state"])
    result = checks["state_location_registry"](tmp_path)
    assert result.required is True
