"""Tests for the ``gt harness`` CLI command group (WI-3340).

Spec-derived tests for ``REQ-HARNESS-REGISTRY-001`` FR3 — the unified
``gt harness`` command group. Eight verbs are operational against the
DB-backed registry; the ninth (``set-role``) is a guarded command whose
operational behavior is FR9 / WI-3341.

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


def _harness_row_count(db_path: Path) -> int:
    """Total rows in the append-only harnesses table (0 if the db is absent)."""
    if not db_path.exists():
        return 0
    with sqlite3.connect(db_path) as conn:
        return int(conn.execute("SELECT COUNT(*) FROM harnesses").fetchone()[0])


def _invoke(config: Path, *args: str) -> object:
    """Invoke the gt CLI under the given config."""
    return CliRunner().invoke(main, ["--config", str(config), "harness", *args])


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


# --- T-HC-7: set-role is guarded and mutates nothing (answers -002 F1) ------


def test_harness_set_role_is_guarded_and_mutates_nothing(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    result = _invoke(config, "set-role", "--harness", "B", "--role", "prime-builder")
    assert result.exit_code != 0
    assert "not yet available" in result.output
    assert "gt mode set-role" in result.output
    # The guarded verb performs no DB write, no role-map write, and no
    # projection write — it cannot leave the registry or projection stale.
    assert _harness_row_count(root / "groundtruth.db") == 0
    assert not (root / "harness-state" / "harness-registry.json").exists()
    assert not (root / "harness-state" / "role-assignments.json").exists()


# --- T-HC-8: the gt mode set-role command is unaffected ---------------------


def test_gt_mode_set_role_command_unaffected(tmp_path: Path) -> None:
    _, config = _project(tmp_path)
    result = CliRunner().invoke(main, ["--config", str(config), "mode", "set-role", "--help"])
    assert result.exit_code == 0
    assert "set-role" in result.output
