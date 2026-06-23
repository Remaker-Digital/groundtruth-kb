"""Tests for mode-switch bridge substrate pending-queue routing.

Covers SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from groundtruth_kb.mode_switch.bridge_substrate import defer_bridge_substrate_switch
from groundtruth_kb.mode_switch.pending import apply_pending, list_pending


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    _write(
        tmp_path / "harness-state" / "harness-registry.json",
        json.dumps(
            {
                "harnesses": [
                    {"id": "A", "role": ["loyal-opposition"], "status": "active"},
                    {"id": "B", "role": ["prime-builder"], "status": "active"},
                ]
            }
        ),
    )
    _write(
        tmp_path / "bridge" / "INDEX.md",
        "Document: foo\nNEW: bridge/foo-001.md\n",
    )
    _write(
        tmp_path / "bridge" / "foo-001.md",
        "NEW\n",
    )
    _write(
        tmp_path / "groundtruth.toml",
        '[groundtruth]\ndb_path = "./groundtruth.db"\nproject_root = "."\n',
    )
    # Seed hook registrations so cross_harness_trigger validates
    _write(
        tmp_path / ".claude" / "settings.json",
        json.dumps({"hooks": {"PostToolUse": [{"command": "python scripts/cross_harness_bridge_trigger.py"}]}}),
    )
    return tmp_path


def test_defer_writes_pending_file_with_axis_bridge_substrate(project_root: Path) -> None:
    path = defer_bridge_substrate_switch(project_root, "cross_harness_trigger", change_reason="defer test")
    assert path.exists()

    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["axis"] == "bridge_substrate"
    assert data["substrate"] == "cross_harness_trigger"
    assert data["change_reason"] == "defer test"


def test_apply_pending_drains_bridge_substrate_entries(project_root: Path) -> None:
    defer_bridge_substrate_switch(project_root, "cross_harness_trigger", change_reason="apply drain test")

    results = apply_pending(project_root)
    assert len(results) == 1
    assert results[0].applied is True
    assert results[0].error is None

    # Check updated state
    state_path = project_root / "harness-state" / "bridge-substrate.json"
    assert state_path.exists()
    state_data = json.loads(state_path.read_text(encoding="utf-8"))
    assert state_data["substrate"] == "cross_harness_trigger"


def test_apply_pending_preserves_legacy_role_pending_entries(project_root: Path) -> None:
    # Write legacy pending JSON file directly to pending dir
    pending_dir = project_root / ".gtkb-state" / "mode-switches" / "pending"
    pending_dir.mkdir(parents=True, exist_ok=True)
    legacy_file = pending_dir / "20260505T120000Z-legacy8.json"

    legacy_payload = {
        "schema_version": 1,
        "record_id": "legacy8",
        "harness_id_or_name": "B",
        "role": "prime-builder",
        "change_reason": "legacy file compatibility test",
        "scheduled_at": "2026-05-05T12:00:00Z",
    }
    legacy_file.write_text(json.dumps(legacy_payload, indent=2) + "\n", encoding="utf-8")

    # Verify legacy file is parsed with axis="role"
    pending = list_pending(project_root)
    assert len(pending) == 1
    assert pending[0].axis == "role"
    assert pending[0].role == "prime-builder"

    # Make sure apply runs role switch
    results = apply_pending(project_root)
    assert len(results) == 1
    assert results[0].applied is True


def test_apply_pending_records_failed_entries_with_error(project_root: Path) -> None:
    # Remove hook registrations to trigger validator failure
    (project_root / ".claude" / "settings.json").unlink()

    defer_bridge_substrate_switch(project_root, "cross_harness_trigger", change_reason="expect fail")

    results = apply_pending(project_root)
    assert len(results) == 1
    assert results[0].applied is False
    assert "cross_harness_trigger is not registered" in results[0].error

    # Check failed record
    failed_dir = project_root / ".gtkb-state" / "mode-switches" / "failed"
    assert failed_dir.exists()
    failed_files = list(failed_dir.glob("*.json"))
    assert len(failed_files) == 1
    failed_data = json.loads(failed_files[0].read_text(encoding="utf-8"))
    assert failed_data["axis"] == "bridge_substrate"
    assert "cross_harness_trigger is not registered" in failed_data["error"]
