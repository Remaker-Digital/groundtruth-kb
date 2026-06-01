"""Tests for mode-switch bridge substrate transactions.

Covers SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from groundtruth_kb.mode_switch.bridge_substrate import apply_bridge_substrate_switch
from groundtruth_kb.mode_switch.transaction import TransactionValidationError


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    # Seed required files for validator all-pass
    _write(
        tmp_path / "harness-state" / "harness-registry.json",
        json.dumps({"harnesses": [{"id": "A", "role": ["prime-builder"], "status": "active"}]}),
    )
    _write(
        tmp_path / "bridge" / "INDEX.md",
        "Document: foo\nNEW: bridge/foo-001.md\n",
    )
    _write(
        tmp_path / "groundtruth.toml",
        '[groundtruth]\ndb_path = "./groundtruth.db"\nproject_root = "."\n',
    )
    return tmp_path


def test_apply_writes_harness_state_atomically(project_root: Path) -> None:
    # Seed trigger in .claude/settings.json
    _write(
        project_root / ".claude" / "settings.json",
        json.dumps({"hooks": {"PostToolUse": [{"command": "python scripts/cross_harness_bridge_trigger.py"}]}}),
    )

    audit_path = apply_bridge_substrate_switch(
        project_root,
        "cross_harness_trigger",
        change_reason="test immediate apply",
    )

    assert audit_path.exists()
    state_path = project_root / "harness-state" / "bridge-substrate.json"
    assert state_path.exists()
    data = json.loads(state_path.read_text(encoding="utf-8"))
    assert data["substrate"] == "cross_harness_trigger"
    assert data["applied_by"] == "A"


def test_apply_emits_audit_record_with_axis_field(project_root: Path) -> None:
    _write(
        project_root / ".claude" / "settings.json",
        json.dumps({"hooks": {"PostToolUse": [{"command": "python scripts/cross_harness_bridge_trigger.py"}]}}),
    )

    audit_path = apply_bridge_substrate_switch(
        project_root,
        "cross_harness_trigger",
        change_reason="test audit log axis",
    )

    assert audit_path.exists()
    data = json.loads(audit_path.read_text(encoding="utf-8"))
    assert data["axis"] == "bridge_substrate"
    assert data["new_substrate"] == "cross_harness_trigger"
    assert data["change_reason"] == "test audit log axis"


def test_apply_rejects_substrate_topology_mismatch(project_root: Path) -> None:
    # multi_harness topology (seed harnesses A and B active)
    _write(
        project_root / "harness-state" / "harness-registry.json",
        json.dumps(
            {
                "harnesses": [
                    {"id": "A", "role": ["prime-builder"], "status": "active"},
                    {"id": "B", "role": ["loyal-opposition"], "status": "active"},
                ]
            }
        ),
    )

    # single_harness_dispatcher is invalid for multi_harness topology
    with pytest.raises(TransactionValidationError) as exc:
        apply_bridge_substrate_switch(
            project_root,
            "single_harness_dispatcher",
            change_reason="invalid substrate",
        )
    assert "bridge substrate validation failed" in str(exc.value)


def test_apply_is_idempotent_when_substrate_unchanged(project_root: Path) -> None:
    _write(
        project_root / ".claude" / "settings.json",
        json.dumps({"hooks": {"PostToolUse": [{"command": "python scripts/cross_harness_bridge_trigger.py"}]}}),
    )

    audit1 = apply_bridge_substrate_switch(
        project_root,
        "cross_harness_trigger",
        change_reason="apply 1",
    )
    audit2 = apply_bridge_substrate_switch(
        project_root,
        "cross_harness_trigger",
        change_reason="apply 2",
    )

    assert audit1.exists()
    assert audit2.exists()
    assert audit1 != audit2


def test_cli_set_bridge_substrate_invokes_apply_switch(project_root: Path) -> None:
    from click.testing import CliRunner
    from groundtruth_kb.cli import main

    _write(
        project_root / ".claude" / "settings.json",
        json.dumps({"hooks": {"PostToolUse": [{"command": "python scripts/cross_harness_bridge_trigger.py"}]}}),
    )

    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "--config",
            str(project_root / "groundtruth.toml"),
            "mode",
            "set-bridge-substrate",
            "--substrate",
            "cross_harness_trigger",
            "--reason",
            "cli set-bridge-substrate",
        ],
        obj={"project_root": str(project_root), "db_path": str(project_root / "groundtruth.db")},
    )

    assert result.exit_code == 0
    assert "applied" in result.output
    assert "cross_harness_trigger" in result.output


def test_cli_set_bridge_substrate_defer_flag_queues_pending(project_root: Path) -> None:
    from click.testing import CliRunner
    from groundtruth_kb.cli import main

    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "--config",
            str(project_root / "groundtruth.toml"),
            "mode",
            "set-bridge-substrate",
            "--substrate",
            "cross_harness_trigger",
            "--reason",
            "cli defer substrate",
            "--defer-to-next-session",
        ],
        obj={"project_root": str(project_root), "db_path": str(project_root / "groundtruth.db")},
    )

    assert result.exit_code == 0
    assert "deferred" in result.output
    pending_dir = project_root / ".gtkb-state" / "mode-switches" / "pending"
    assert len(list(pending_dir.glob("*.json"))) == 1


def test_substrate_inert_path_when_disagrees_with_durable_selection(project_root: Path) -> None:
    from scripts.cross_harness_bridge_trigger import run_trigger

    # Setup trigger
    state_dir = project_root / ".gtkb-state" / "bridge-poller"

    # Set substrate to 'none' in bridge-substrate.json
    _write(
        project_root / "harness-state" / "bridge-substrate.json",
        json.dumps({"substrate": "none"}),
    )

    res = run_trigger(project_root=project_root, state_dir=state_dir)
    assert res["skipped"] is True
    assert res["reason"] == "substrate_mismatch_inert"
