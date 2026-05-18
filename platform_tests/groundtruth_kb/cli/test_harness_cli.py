"""Tests for the ``gt harness`` CLI command group.

Spec-derived tests for ``REQ-HARNESS-REGISTRY-001`` FR3 (the unified
``gt harness`` command group) and FR9 (the operational ``set-role`` verb).
``set-role`` promotes a harness to ``prime-builder``, atomically demoting
every other harness to ``loyal-opposition`` (WI-3341 Slice A).

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

import pytest
from click.testing import CliRunner

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "groundtruth-kb" / "src"))

from groundtruth_kb.cli import main  # noqa: E402


@pytest.fixture(autouse=True)
def _clean_registry_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure the projection lands at the default in-project path."""
    monkeypatch.delenv("GTKB_HARNESS_REGISTRY_PATH", raising=False)


def _project(tmp_path: Path) -> tuple[Path, Path]:
    """Create a temporary GT-KB project with config; return (root, config)."""
    root = tmp_path / "project"
    root.mkdir()
    config = root / "groundtruth.toml"
    config.write_text(
        '[groundtruth]\ndb_path = "./groundtruth.db"\nproject_root = "."\n',
        encoding="utf-8",
    )
    return root, config


def _harness_current(db_path: Path, harness_id: str) -> sqlite3.Row | None:
    """Return the current-version harness row, or None."""
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        return conn.execute(
            "SELECT * FROM current_harnesses WHERE id = ?", (harness_id,)
        ).fetchone()


def _invoke(config: Path, *args: str) -> object:
    """Invoke the gt CLI under the given config."""
    return CliRunner().invoke(main, ["--config", str(config), "harness", *args])


def _register_active(
    config: Path, harness_id: str, harness_type: str, *, role: list[str] | None = None
) -> None:
    """Register a harness with an initial role set and activate it.

    WI-3342 IP-6: the harness role map is the DB-backed registry projection
    (``harness-state/harness-registry.json``), not the retired
    ``role-assignments.json``. The initial role set is therefore written into
    the DB at registration via repeatable ``--role`` options so the projection
    ``apply_role_switch`` reads carries the intended starting roles.
    """
    register_args = [
        "register", "--id", harness_id, "--name", harness_id.lower(),
        "--type", harness_type,
    ]
    for token in role or []:
        register_args += ["--role", token]
    reg = _invoke(config, *register_args)
    assert reg.exit_code == 0, reg.output
    act = _invoke(config, "activate", "--harness", harness_id)
    assert act.exit_code == 0, act.output


def _seed_role_workspace(root: Path) -> None:
    """Seed the minimal ``bridge/INDEX.md`` the transaction validator needs.

    WI-3342 IP-6: ``apply_role_switch`` validates the role artifact (the
    DB-backed registry projection — already produced by ``gt harness register``
    / ``activate``), the bridge artifact, and (optionally) the session-state
    artifact before any write. The starting role map now comes from the DB via
    ``_register_active(..., role=[...])``, so this helper only seeds the bridge
    artifact.
    """
    index_path = root / "bridge" / "INDEX.md"
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(
        "Document: seed\nVERIFIED: bridge/seed-001.md\n", encoding="utf-8"
    )


def _read_role_map(root: Path) -> dict:
    """Return ``{harness_id: record}`` from the registry projection (WI-3342 IP-6).

    The post-switch role surface is the DB-backed registry projection
    ``harness-state/harness-registry.json`` (``harnesses`` is a LIST of unified
    records), not the retired ``role-assignments.json``.
    """
    data = json.loads(
        (root / "harness-state" / "harness-registry.json").read_text(encoding="utf-8")
    )
    return {
        str(record["id"]): record
        for record in data.get("harnesses", [])
        if isinstance(record, dict) and record.get("id")
    }


# --- T-HC-1: register -------------------------------------------------------


def test_harness_register_cli(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    result = _invoke(config, "register", "--id", "B", "--name", "claude", "--type", "claude-code")
    assert result.exit_code == 0, result.output
    row = _harness_current(root / "groundtruth.db", "B")
    assert row is not None
    assert row["status"] == "registered"
    # FR5 hot-path projection refreshed after the mutation.
    assert (root / "harness-state" / "harness-registry.json").exists()


# --- T-HC-2: full lifecycle -------------------------------------------------


def test_harness_lifecycle_cli(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    db_path = root / "groundtruth.db"
    assert _invoke(config, "register", "--id", "B", "--name", "claude", "--type", "claude-code").exit_code == 0
    assert _invoke(config, "activate", "--harness", "B").exit_code == 0
    assert _harness_current(db_path, "B")["status"] == "active"
    assert _invoke(config, "suspend", "--harness", "B").exit_code == 0
    assert _harness_current(db_path, "B")["status"] == "suspended"
    assert _invoke(config, "resume", "--harness", "B").exit_code == 0
    assert _harness_current(db_path, "B")["status"] == "active"
    show = _invoke(config, "show", "--harness", "B")
    assert show.exit_code == 0
    assert json.loads(show.output)["status"] == "active"


# --- T-HC-3: retire of an active harness auto-suspends ----------------------


def test_harness_retire_active_cli(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    db_path = root / "groundtruth.db"
    _invoke(config, "register", "--id", "B", "--name", "claude", "--type", "claude-code")
    _invoke(config, "activate", "--harness", "B")
    result = _invoke(config, "retire", "--harness", "B")
    assert result.exit_code == 0, result.output
    row = _harness_current(db_path, "B")
    assert row["status"] == "retired"
    # registered -> active -> suspended -> retired => version 4 (owner AUQ).
    assert row["version"] == 4


# --- T-HC-4: an invalid verb use fails closed with a hint -------------------


def test_harness_invalid_transition_cli(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    db_path = root / "groundtruth.db"
    _invoke(config, "register", "--id", "B", "--name", "claude", "--type", "claude-code")
    # B is 'registered'; suspend expects an 'active' harness.
    result = _invoke(config, "suspend", "--harness", "B")
    assert result.exit_code != 0
    assert "activate" in result.output  # the hint names the correct verb
    row = _harness_current(db_path, "B")
    assert row["status"] == "registered"  # no transition applied
    assert row["version"] == 1


# --- T-HC-5: list and show --------------------------------------------------


def test_harness_list_and_show_cli(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    _invoke(config, "register", "--id", "B", "--name", "claude", "--type", "claude-code")
    _invoke(config, "register", "--id", "A", "--name", "codex", "--type", "codex-cli")
    listing = _invoke(config, "list")
    assert listing.exit_code == 0
    assert {h["id"] for h in json.loads(listing.output)} == {"A", "B"}
    show = _invoke(config, "show", "--harness", "A")
    assert show.exit_code == 0
    assert json.loads(show.output)["id"] == "A"
    missing = _invoke(config, "show", "--harness", "Z")
    assert missing.exit_code != 0


# --- T-HC-6: set-precedence -------------------------------------------------


def test_harness_set_precedence_cli(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    db_path = root / "groundtruth.db"
    _invoke(config, "register", "--id", "B", "--name", "claude", "--type", "claude-code")
    result = _invoke(config, "set-precedence", "--harness", "B", "--precedence", "7")
    assert result.exit_code == 0, result.output
    assert _harness_current(db_path, "B")["reviewer_precedence"] == 7


# --- T-HC-7: set-role promotes the target and demotes every other harness ---


def test_harness_set_role_promotes_and_demotes(tmp_path: Path) -> None:
    """FR9: set-role sets the target to prime-builder and the other harness to
    loyal-opposition; the role map is a valid partition after."""
    root, config = _project(tmp_path)
    _register_active(config, "A", "codex-cli", role=["prime-builder"])
    _register_active(config, "B", "claude-code", role=["loyal-opposition"])
    _seed_role_workspace(root)
    result = _invoke(config, "set-role", "--harness", "B")
    assert result.exit_code == 0, result.output
    role_map = _read_role_map(root)
    assert role_map["B"]["role"] == ["prime-builder"]
    assert role_map["A"]["role"] == ["loyal-opposition"]


def test_harness_set_role_reassigns_prime_builder(tmp_path: Path) -> None:
    """GOV-HARNESS-ROLE-PORTABILITY-001: the role moves by durable harness id
    irrespective of harness_type — A and B carry distinct types."""
    root, config = _project(tmp_path)
    _register_active(config, "A", "codex-cli", role=["prime-builder"])
    _register_active(config, "B", "claude-code", role=["loyal-opposition"])
    _seed_role_workspace(root)
    # Promote B (currently loyal-opposition) — prime-builder must move to it.
    assert _invoke(config, "set-role", "--harness", "B").exit_code == 0
    role_map = _read_role_map(root)
    assert role_map["B"]["role"] == ["prime-builder"]
    assert role_map["A"]["role"] == ["loyal-opposition"]
    # And back to A — portability is symmetric and harness-type-independent.
    assert _invoke(config, "set-role", "--harness", "A").exit_code == 0
    role_map = _read_role_map(root)
    assert role_map["A"]["role"] == ["prime-builder"]
    assert role_map["B"]["role"] == ["loyal-opposition"]


def test_harness_set_role_three_harness_demotes_all_non_targets(tmp_path: Path) -> None:
    """FR9 + FR6: with three distinctly-typed harnesses, promoting one makes it
    the sole prime-builder and demotes BOTH others — including a non-target
    whose prior role set was empty — to loyal-opposition."""
    root, config = _project(tmp_path)
    _register_active(config, "A", "codex-cli", role=["prime-builder"])
    _register_active(config, "B", "claude-code", role=["loyal-opposition"])
    # C starts with an empty role set — the -006 F1 gap.
    _register_active(config, "C", "antigravity-cli", role=[])
    _seed_role_workspace(root)
    result = _invoke(config, "set-role", "--harness", "C")
    assert result.exit_code == 0, result.output
    role_map = _read_role_map(root)
    assert role_map["C"]["role"] == ["prime-builder"]
    assert role_map["A"]["role"] == ["loyal-opposition"]
    assert role_map["B"]["role"] == ["loyal-opposition"]


def test_harness_set_role_rejects_non_active_harness(tmp_path: Path) -> None:
    """FR9 active-harness eligibility gate: a registered or suspended harness is
    rejected, and the role map is not mutated (fail closed before any write)."""
    root, config = _project(tmp_path)
    _register_active(config, "A", "codex-cli", role=["prime-builder"])
    # B is registered but never activated -> status 'registered'.
    assert _invoke(
        config, "register", "--id", "B", "--name", "b", "--type", "claude-code",
        "--role", "loyal-opposition",
    ).exit_code == 0
    # D is registered, activated, then suspended -> status 'suspended'.
    _register_active(config, "D", "other-cli", role=["loyal-opposition"])
    assert _invoke(config, "suspend", "--harness", "D").exit_code == 0
    _seed_role_workspace(root)
    # WI-3342 IP-6: the role map is the DB-backed registry projection; the
    # eligibility gate failing closed means the projection's role records are
    # unchanged by the rejected set-role.
    roles_before = {hid: rec.get("role") for hid, rec in _read_role_map(root).items()}
    for non_active in ("B", "D"):
        result = _invoke(config, "set-role", "--harness", non_active)
        assert result.exit_code != 0, result.output
        assert "status" in result.output
    # The eligibility gate fails closed: no role-map write occurred.
    assert {hid: rec.get("role") for hid, rec in _read_role_map(root).items()} == roles_before


def test_harness_set_role_unknown_harness_rejected(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    _register_active(config, "A", "codex-cli", role=["prime-builder"])
    _seed_role_workspace(root)
    result = _invoke(config, "set-role", "--harness", "ZZ")
    assert result.exit_code != 0
    assert "ZZ" in result.output


def test_harness_set_role_emits_single_prime_builder(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    _register_active(config, "A", "codex-cli", role=["prime-builder"])
    _register_active(config, "B", "claude-code", role=["loyal-opposition"])
    _seed_role_workspace(root)
    result = _invoke(config, "set-role", "--harness", "B")
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["verified_prime_builder"] == "B"
    assert payload["new_role_set"] == ["prime-builder"]


# --- T-HC-8: the gt mode set-role command is unaffected ---------------------


def test_gt_mode_set_role_command_unaffected(tmp_path: Path) -> None:
    _, config = _project(tmp_path)
    result = CliRunner().invoke(main, ["--config", str(config), "mode", "set-role", "--help"])
    assert result.exit_code == 0
    assert "set-role" in result.output
