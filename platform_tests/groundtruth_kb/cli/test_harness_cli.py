"""Tests for the ``gt harness`` CLI command group.

Spec-derived tests for ``REQ-HARNESS-REGISTRY-001`` FR3 (the unified
``gt harness`` command group) and FR9 (the operational ``set-role`` verb).
``set-role`` updates one harness's default role metadata while preserving the
active PB/LO invariant across the whole candidate configuration.

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
from groundtruth_kb.db import KnowledgeDB  # noqa: E402
from groundtruth_kb.harness_projection import generate_harness_projection  # noqa: E402


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
        return conn.execute("SELECT * FROM current_harnesses WHERE id = ?", (harness_id,)).fetchone()


def _invoke(config: Path, *args: str) -> object:
    """Invoke the gt CLI under the given config."""
    return CliRunner().invoke(main, ["--config", str(config), "harness", *args])


def _seed_harness_roles(root: Path, roles: dict[str, list[str]]) -> None:
    db_path = root / "groundtruth.db"
    db = KnowledgeDB(db_path=db_path)
    for harness_id, role in roles.items():
        current = _harness_current(db_path, harness_id)
        assert current is not None
        invocation_surfaces = json.loads(current["invocation_surfaces"]) if current["invocation_surfaces"] else None
        db.insert_harness(
            id=harness_id,
            harness_name=current["harness_name"],
            harness_type=current["harness_type"],
            role=list(role),
            changed_by="test",
            change_reason="seed harness role metadata for CLI test",
            status=current["status"],
            reviewer_precedence=current["reviewer_precedence"],
            invocation_surfaces=invocation_surfaces,
            capabilities_ref=current["capabilities_ref"],
        )
    generate_harness_projection(db, root)


def _register_active(config: Path, harness_id: str, harness_type: str, *, role: list[str] | None = None) -> None:
    """Register a harness, activate it, and optionally seed role metadata."""
    register_args = [
        "register",
        "--id",
        harness_id,
        "--name",
        harness_id.lower(),
        "--type",
        harness_type,
    ]
    reg = _invoke(config, *register_args)
    assert reg.exit_code == 0, reg.output
    act = _invoke(config, "activate", "--harness", harness_id)
    assert act.exit_code == 0, act.output
    if role is not None:
        _seed_harness_roles(config.parent, {harness_id: role})


def _seed_role_workspace(root: Path) -> None:
    """Seed the minimal ``bridge/INDEX.md`` the transaction validator needs.

    WI-3342 IP-6: ``apply_role_switch`` validates the role artifact (the
    DB-backed registry projection â€” already produced by ``gt harness register``
    / ``activate``), the bridge artifact, and (optionally) the session-state
    artifact before any write. The starting role map now comes from the DB via
    ``_register_active(..., role=[...])``, so this helper only seeds the bridge
    artifact.
    """
    index_path = root / "bridge" / "INDEX.md"
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text("Document: seed\nVERIFIED: bridge/seed-001.md\n", encoding="utf-8")


def _read_role_map(root: Path) -> dict:
    """Return ``{harness_id: record}`` from the registry projection (WI-3342 IP-6).

    The post-switch role surface is the DB-backed registry projection
    ``harness-state/harness-registry.json`` (``harnesses`` is a LIST of unified
    records), not the retired ``role-assignments.json``.
    """
    data = json.loads((root / "harness-state" / "harness-registry.json").read_text(encoding="utf-8"))
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
    assert json.loads(row["role"]) == []
    # FR5 hot-path projection refreshed after the mutation.
    assert (root / "harness-state" / "harness-registry.json").exists()


def test_harness_register_rejects_initial_role(tmp_path: Path) -> None:
    _, config = _project(tmp_path)
    result = _invoke(
        config,
        "register",
        "--id",
        "B",
        "--name",
        "claude",
        "--type",
        "claude-code",
        "--role",
        "prime-builder",
    )
    assert result.exit_code != 0
    assert "registration is separate" in result.output


# --- T-HC-2: full lifecycle -------------------------------------------------


def test_harness_lifecycle_cli(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    db_path = root / "groundtruth.db"
    assert _invoke(config, "register", "--id", "A", "--name", "codex", "--type", "codex-cli").exit_code == 0
    assert _invoke(config, "activate", "--harness", "A").exit_code == 0
    assert _invoke(config, "register", "--id", "B", "--name", "claude", "--type", "claude-code").exit_code == 0
    assert _invoke(config, "activate", "--harness", "B").exit_code == 0
    assert _harness_current(db_path, "B")["status"] == "active"
    assert _invoke(config, "suspend", "--harness", "B").exit_code == 0
    assert _harness_current(db_path, "B")["status"] == "suspended"
    assert _invoke(config, "activate", "--harness", "B").exit_code == 0
    assert _harness_current(db_path, "B")["status"] == "active"
    show = _invoke(config, "show", "--harness", "B")
    assert show.exit_code == 0
    assert json.loads(show.output)["status"] == "active"


def test_harness_suspend_last_active_rejected(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    db_path = root / "groundtruth.db"
    _register_active(config, "A", "codex-cli")
    result = _invoke(config, "suspend", "--harness", "A")
    assert result.exit_code != 0
    assert "last active harness" in result.output
    assert _harness_current(db_path, "A")["status"] == "active"


def test_harness_suspend_preserves_role_metadata(tmp_path: Path) -> None:
    """WI-4213: suspended harnesses may retain role metadata."""
    root, config = _project(tmp_path)
    db_path = root / "groundtruth.db"
    _register_active(config, "A", "codex-cli", role=["loyal-opposition"])
    _register_active(config, "B", "claude-code", role=["loyal-opposition"])
    _seed_role_workspace(root)
    _seed_harness_roles(root, {"A": ["loyal-opposition"], "B": ["loyal-opposition"]})
    result = _invoke(config, "set-role", "--harness", "B", "--role", "prime-builder")
    assert result.exit_code == 0, result.output
    assert json.loads(_harness_current(db_path, "B")["role"]) == ["prime-builder"]

    assert _invoke(config, "suspend", "--harness", "B").exit_code == 0
    row = _harness_current(db_path, "B")
    assert row["status"] == "suspended"
    assert json.loads(row["role"]) == ["prime-builder"]


# --- T-HC-3: retire of an active harness auto-suspends ----------------------


def test_harness_retire_active_cli(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    db_path = root / "groundtruth.db"
    _invoke(config, "register", "--id", "A", "--name", "codex", "--type", "codex-cli")
    _invoke(config, "activate", "--harness", "A")
    _invoke(config, "register", "--id", "B", "--name", "claude", "--type", "claude-code")
    _invoke(config, "activate", "--harness", "B")
    result = _invoke(config, "retire", "--harness", "B")
    assert result.exit_code == 0, result.output
    row = _harness_current(db_path, "B")
    assert row["status"] == "retired"
    # registered -> active -> role reconciliation -> suspended -> retired.
    assert row["version"] == 5


def test_harness_retire_preserves_role_metadata(tmp_path: Path) -> None:
    """WI-4213: retired harnesses keep their role-set history for orthogonality."""
    root, config = _project(tmp_path)
    db_path = root / "groundtruth.db"
    _register_active(config, "A", "codex-cli", role=["loyal-opposition"])
    _register_active(config, "B", "claude-code", role=["loyal-opposition"])
    _seed_role_workspace(root)
    _seed_harness_roles(root, {"A": ["loyal-opposition"], "B": ["loyal-opposition"]})
    assert _invoke(config, "set-role", "--harness", "B", "--role", "prime-builder").exit_code == 0

    assert _invoke(config, "retire", "--harness", "B").exit_code == 0
    row = _harness_current(db_path, "B")
    assert row["status"] == "retired"
    assert json.loads(row["role"]) == ["prime-builder"]


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


# --- T-HC-7: set-role assigns one role and preserves active PB/LO invariant ---


def test_harness_set_role_updates_only_target_when_candidate_valid(tmp_path: Path) -> None:
    """FR9: assigning B to prime-builder leaves A unchanged as loyal-opposition."""
    root, config = _project(tmp_path)
    _register_active(config, "A", "codex-cli", role=["loyal-opposition"])
    _register_active(config, "B", "claude-code", role=["loyal-opposition"])
    _seed_role_workspace(root)
    _seed_harness_roles(root, {"A": ["loyal-opposition"], "B": ["loyal-opposition"]})
    result = _invoke(config, "set-role", "--harness", "B", "--role", "prime-builder")
    assert result.exit_code == 0, result.output
    role_map = _read_role_map(root)
    assert role_map["A"]["role"] == ["loyal-opposition"]
    assert role_map["B"]["role"] == ["prime-builder"]


def test_harness_set_role_rejects_invalid_active_candidate(tmp_path: Path) -> None:
    """A one-target update cannot synthesize the complementary holder."""
    root, config = _project(tmp_path)
    _register_active(config, "A", "codex-cli", role=["prime-builder"])
    _register_active(config, "B", "claude-code", role=["loyal-opposition"])
    _seed_role_workspace(root)
    _seed_harness_roles(root, {"A": ["prime-builder"], "B": ["loyal-opposition"]})
    result = _invoke(config, "set-role", "--harness", "B", "--role", "prime-builder")
    assert result.exit_code != 0, result.output
    assert "at least one loyal-opposition" in result.output
    role_map = _read_role_map(root)
    assert role_map["A"]["role"] == ["prime-builder"]
    assert role_map["B"]["role"] == ["loyal-opposition"]


def test_harness_set_role_three_harness_allows_multiple_prime_builders(tmp_path: Path) -> None:
    """Active candidates can have multiple prime-builders and loyal-oppositions."""
    root, config = _project(tmp_path)
    _register_active(config, "A", "codex-cli", role=["prime-builder"])
    _register_active(config, "B", "claude-code", role=["loyal-opposition"])
    _register_active(config, "C", "antigravity-cli", role=["loyal-opposition"])
    _seed_role_workspace(root)
    _seed_harness_roles(
        root,
        {"A": ["prime-builder"], "B": ["loyal-opposition"], "C": ["loyal-opposition"]},
    )
    result = _invoke(config, "set-role", "--harness", "C", "--role", "prime-builder")
    assert result.exit_code == 0, result.output
    role_map = _read_role_map(root)
    assert role_map["A"]["role"] == ["prime-builder"]
    assert role_map["B"]["role"] == ["loyal-opposition"]
    assert role_map["C"]["role"] == ["prime-builder"]


def test_harness_set_role_allows_non_active_metadata_and_rejects_retired(tmp_path: Path) -> None:
    """Registered/suspended metadata can change; retired remains terminal."""
    root, config = _project(tmp_path)
    _register_active(config, "A", "codex-cli", role=["prime-builder"])
    _register_active(config, "C", "other-active-cli", role=["loyal-opposition"])
    # B is registered but never activated -> status 'registered'.
    assert (
        _invoke(
            config,
            "register",
            "--id",
            "B",
            "--name",
            "b",
            "--type",
            "claude-code",
        ).exit_code
        == 0
    )
    # D is registered, activated, then suspended -> status 'suspended'.
    _register_active(config, "D", "other-cli", role=["loyal-opposition"])
    assert _invoke(config, "suspend", "--harness", "D").exit_code == 0
    _register_active(config, "E", "retired-cli", role=["loyal-opposition"])
    assert _invoke(config, "retire", "--harness", "E").exit_code == 0
    _seed_role_workspace(root)
    _seed_harness_roles(
        root,
        {
            "A": ["prime-builder"],
            "C": ["loyal-opposition"],
            "D": ["loyal-opposition"],
            "E": ["loyal-opposition"],
        },
    )
    for non_active in ("B", "D"):
        result = _invoke(config, "set-role", "--harness", non_active, "--role", "prime-builder")
        assert result.exit_code == 0, result.output
    result = _invoke(config, "set-role", "--harness", "E", "--role", "prime-builder")
    assert result.exit_code != 0
    assert "retired" in result.output
    role_map = _read_role_map(root)
    assert role_map["B"]["role"] == ["prime-builder"]
    assert role_map["B"]["status"] == "registered"
    assert role_map["D"]["role"] == ["prime-builder"]
    assert role_map["D"]["status"] == "suspended"
    assert role_map["E"]["role"] == ["loyal-opposition"]
    assert role_map["E"]["status"] == "retired"


def test_harness_set_role_unknown_harness_rejected(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    _register_active(config, "A", "codex-cli", role=["prime-builder"])
    _seed_role_workspace(root)
    result = _invoke(config, "set-role", "--harness", "ZZ", "--role", "prime-builder")
    assert result.exit_code != 0
    assert "ZZ" in result.output


def test_harness_set_role_emits_role_holder_sets(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    _register_active(config, "A", "codex-cli", role=["loyal-opposition"])
    _register_active(config, "B", "claude-code", role=["loyal-opposition"])
    _seed_role_workspace(root)
    _seed_harness_roles(root, {"A": ["loyal-opposition"], "B": ["loyal-opposition"]})
    result = _invoke(config, "set-role", "--harness", "B", "--role", "prime-builder")
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["verified_prime_builder"] == "B"
    assert payload["verified_prime_builders"] == ["B"]
    assert payload["verified_loyal_opposition"] == "A"
    assert payload["verified_loyal_oppositions"] == ["A"]
    assert payload["new_role_set"] == ["prime-builder"]


# --- T-HC-8: the gt mode set-role command is unaffected ---------------------


def test_gt_mode_set_role_command_unaffected(tmp_path: Path) -> None:
    _, config = _project(tmp_path)
    result = CliRunner().invoke(main, ["--config", str(config), "mode", "set-role", "--help"])
    assert result.exit_code == 0
    assert "set-role" in result.output
