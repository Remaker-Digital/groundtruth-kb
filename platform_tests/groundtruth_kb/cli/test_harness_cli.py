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


def _register_active(config: Path, harness_id: str, harness_type: str) -> None:
    """Register a harness and activate it (status 'active' in the registry)."""
    reg = _invoke(
        config, "register", "--id", harness_id, "--name", harness_id.lower(),
        "--type", harness_type,
    )
    assert reg.exit_code == 0, reg.output
    act = _invoke(config, "activate", "--harness", harness_id)
    assert act.exit_code == 0, act.output


def _seed_role_workspace(root: Path, role_map: dict[str, list[str]]) -> None:
    """Seed harness-state/role-assignments.json and a minimal bridge/INDEX.md.

    ``apply_role_switch`` validates the role artifact, the bridge artifact, and
    (optionally) the session-state artifact before any write; this seeds the
    first two so the transaction's validator chain passes.
    """
    harnesses = {
        hid: {"role": roles, "name": hid.lower()} for hid, roles in role_map.items()
    }
    role_path = root / "harness-state" / "role-assignments.json"
    role_path.parent.mkdir(parents=True, exist_ok=True)
    role_path.write_text(json.dumps({"harnesses": harnesses}), encoding="utf-8")
    index_path = root / "bridge" / "INDEX.md"
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(
        "Document: seed\nVERIFIED: bridge/seed-001.md\n", encoding="utf-8"
    )


def _read_role_map(root: Path) -> dict:
    """Return the 'harnesses' object of the current role-assignments.json."""
    data = json.loads(
        (root / "harness-state" / "role-assignments.json").read_text(encoding="utf-8")
    )
    return data["harnesses"]


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
    _register_active(config, "A", "codex-cli")
    _register_active(config, "B", "claude-code")
    _seed_role_workspace(root, {"A": ["prime-builder"], "B": ["loyal-opposition"]})
    result = _invoke(config, "set-role", "--harness", "B")
    assert result.exit_code == 0, result.output
    role_map = _read_role_map(root)
    assert role_map["B"]["role"] == ["prime-builder"]
    assert role_map["A"]["role"] == ["loyal-opposition"]


def test_harness_set_role_reassigns_prime_builder(tmp_path: Path) -> None:
    """GOV-HARNESS-ROLE-PORTABILITY-001: the role moves by durable harness id
    irrespective of harness_type — A and B carry distinct types."""
    root, config = _project(tmp_path)
    _register_active(config, "A", "codex-cli")
    _register_active(config, "B", "claude-code")
    _seed_role_workspace(root, {"A": ["prime-builder"], "B": ["loyal-opposition"]})
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
    _register_active(config, "A", "codex-cli")
    _register_active(config, "B", "claude-code")
    _register_active(config, "C", "antigravity-cli")
    # C starts with an empty role set — the -006 F1 gap.
    _seed_role_workspace(
        root, {"A": ["prime-builder"], "B": ["loyal-opposition"], "C": []}
    )
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
    _register_active(config, "A", "codex-cli")
    # B is registered but never activated -> status 'registered'.
    assert _invoke(config, "register", "--id", "B", "--name", "b", "--type", "claude-code").exit_code == 0
    # D is registered, activated, then suspended -> status 'suspended'.
    _register_active(config, "D", "other-cli")
    assert _invoke(config, "suspend", "--harness", "D").exit_code == 0
    _seed_role_workspace(
        root,
        {"A": ["prime-builder"], "B": ["loyal-opposition"], "D": ["loyal-opposition"]},
    )
    role_path = root / "harness-state" / "role-assignments.json"
    before = role_path.read_text(encoding="utf-8")
    for non_active in ("B", "D"):
        result = _invoke(config, "set-role", "--harness", non_active)
        assert result.exit_code != 0, result.output
        assert "status" in result.output
    # The eligibility gate fails closed: no role-map write occurred.
    assert role_path.read_text(encoding="utf-8") == before


def test_harness_set_role_unknown_harness_rejected(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    _register_active(config, "A", "codex-cli")
    _seed_role_workspace(root, {"A": ["prime-builder"]})
    result = _invoke(config, "set-role", "--harness", "ZZ")
    assert result.exit_code != 0
    assert "ZZ" in result.output


def test_harness_set_role_emits_single_prime_builder(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    _register_active(config, "A", "codex-cli")
    _register_active(config, "B", "claude-code")
    _seed_role_workspace(root, {"A": ["prime-builder"], "B": ["loyal-opposition"]})
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
