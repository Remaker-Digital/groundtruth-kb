"""Tests for session start pending queue drains (Test 11).

Covers SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from groundtruth_kb.mode_switch.bridge_substrate import defer_bridge_substrate_switch

from scripts.cross_harness_bridge_trigger import run_trigger


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
                    {"id": "A", "role": ["prime-builder"], "status": "active"},
                    {"id": "B", "role": ["loyal-opposition"], "status": "active"},
                ]
            }
        ),
    )
    _write(
        tmp_path / "harness-state" / "harness-identities.json",
        json.dumps({"codex": "A", "claude": "B"}),
    )
    _write(
        tmp_path / "bridge" / "INDEX.md",
        "Document: foo\nNEW: bridge/foo-001.md\n",
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


def test_session_start_drains_pending_before_role_resolution(
    project_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Ensure no environment variable overrides skip execution in test
    monkeypatch.delenv("GTKB_NO_CROSS_HARNESS_TRIGGER", raising=False)

    # Set a pending transaction
    defer_bridge_substrate_switch(project_root, "cross_harness_trigger", change_reason="session start drain test")

    # Run trigger simulation
    state_dir = project_root / ".gtkb-state" / "bridge-poller"
    run_trigger(project_root=project_root, state_dir=state_dir)

    # Check that substrate updated durably
    state_path = project_root / "harness-state" / "bridge-substrate.json"
    assert state_path.exists()
    state_data = json.loads(state_path.read_text(encoding="utf-8"))
    assert state_data["substrate"] == "cross_harness_trigger"
