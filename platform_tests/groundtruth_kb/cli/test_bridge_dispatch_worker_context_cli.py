"""Tests for the worker-safe dispatch context facade."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from click.testing import CliRunner
from groundtruth_kb.cli import main

DISPATCH_ID = "2026-07-17T08-00-00Z-prime-builder-A-abc123"


def test_worker_context_packet_includes_assigned_content_and_omits_internals(tmp_path: Path) -> None:
    config = _write_project(tmp_path)
    state_path = _write_dispatch_state(tmp_path)
    _write_bridge_thread(tmp_path)
    before_state = state_path.read_bytes()

    result = CliRunner().invoke(
        main,
        [
            "--config",
            str(config),
            "bridge",
            "dispatch",
            "worker-context",
            "--self",
            "--dispatch-id",
            DISPATCH_ID,
            "--json",
        ],
    )

    assert result.exit_code == 0, result.output
    assert state_path.read_bytes() == before_state
    packet = json.loads(result.output)
    assert packet["schema_version"] == "gtkb.dispatch.worker_context_packet.v1"
    assert packet["dispatch_id"] == DISPATCH_ID
    assert packet["target_paths"] == ["groundtruth-kb/src/groundtruth_kb/example.py"]
    assert "DCL-DISPATCHER-WORKER-SAFE-PACKET-CONTRACT-001" in packet["governing_specs"]
    assert "implement_approved_target_paths" in packet["allowed_actions"]
    assert packet["blockers"] == []
    assert packet["preflight_state"]["status"] == "PASS"
    assert packet["provenance"]["role"] == "prime-builder"
    assert packet["provenance"]["harness_id"] == "A"

    assigned = packet["assigned_content"]
    assert [item["document_name"] for item in assigned] == ["gtkb-demo-worker-context"]
    assert [item["status"] for item in assigned[0]["bridge_files"]] == ["NEW", "GO"]
    contents = "\n".join(item["content"] for item in assigned[0]["bridge_files"])
    assert "Prime proposal body for worker context." in contents
    assert "Loyal Opposition GO body." in contents

    serialized = json.dumps(packet, sort_keys=True)
    for forbidden in (
        "raw_queue_marker",
        "ranking_score",
        "tafe_secret",
        "harness-state/harness-registry.json",
        "gtkb-demo-worker-context.lock",
        "command.exe",
        "stdout.log",
        "dispatch-state.json",
        "other-harness:B",
    ):
        assert forbidden not in serialized
    _assert_absent_keys(packet, {"pid", "command_head", "stdout_path", "lock_path", "launch_ledger", "last_launch"})


def test_worker_context_self_resolves_dispatch_id_from_environment(tmp_path: Path) -> None:
    config = _write_project(tmp_path)
    _write_dispatch_state(tmp_path)
    _write_bridge_thread(tmp_path)

    result = CliRunner().invoke(
        main,
        ["--config", str(config), "bridge", "dispatch", "worker-context", "--self", "--json"],
        env={"GTKB_DISPATCH_ID": DISPATCH_ID},
    )

    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["dispatch_id"] == DISPATCH_ID


def _write_project(root: Path) -> Path:
    (root / "bridge").mkdir(parents=True)
    config = root / "groundtruth.toml"
    config.write_text(f'[groundtruth]\nproject_root = "{root.as_posix()}"\n', encoding="utf-8")
    return config


def _write_bridge_thread(root: Path) -> None:
    proposal = """NEW
Project Authorization: PAUTH-DEMO
Project: PROJECT-DEMO
Work Item: WI-5270
target_paths: ["groundtruth-kb/src/groundtruth_kb/example.py"]

## Specification Links

- `DCL-DISPATCHER-WORKER-SAFE-PACKET-CONTRACT-001`
- `DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001`
- `ADR-DISPATCHER-WORKER-CONTEXT-FACADE-001`

Prime proposal body for worker context.
"""
    verdict = """GO
Reviewed Proposal: bridge/gtkb-demo-worker-context-001.md

Loyal Opposition GO body.
"""
    (root / "bridge" / "gtkb-demo-worker-context-001.md").write_text(proposal, encoding="utf-8")
    (root / "bridge" / "gtkb-demo-worker-context-002.md").write_text(verdict, encoding="utf-8")


def _write_dispatch_state(root: Path) -> Path:
    state_dir = root / ".gtkb-state" / "bridge-poller"
    state_dir.mkdir(parents=True)
    state = {
        "recipients": {
            "prime-builder:A": {
                "last_launch": {
                    "dispatch_id": DISPATCH_ID,
                    "recipient": "prime-builder:A",
                    "needed_role_label": "prime-builder",
                    "primary_bridge_id": "gtkb-demo-worker-context",
                    "selected_documents": ["gtkb-demo-worker-context"],
                    "selected_top_files": ["bridge/gtkb-demo-worker-context-002.md"],
                    "work_intent_session_id": DISPATCH_ID,
                    "work_intent_slugs": ["gtkb-demo-worker-context"],
                    "trusted_worker_context": {
                        "dispatch_id": DISPATCH_ID,
                        "harness_id": "A",
                        "role": "prime-builder",
                        "session_id": DISPATCH_ID,
                    },
                    "pid": 1234,
                    "command_head": ["command.exe"],
                    "stdout_path": "E:/GT-KB/.gtkb-state/bridge-poller/dispatch-runs/stdout.log",
                    "lock_path": "E:/GT-KB/.gtkb-state/bridge-poller/leases/gtkb-demo-worker-context.lock",
                    "raw_queue_marker": "raw queue should not leak",
                    "ranking_score": 99,
                    "tafe_secret": "tafe_secret",
                    "harness_registry_path": "harness-state/harness-registry.json",
                    "other_harness_state": "other-harness:B",
                },
                "launch_ledger": {},
            }
        }
    }
    path = state_dir / "dispatch-state.json"
    path.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")
    return path


def _assert_absent_keys(value: Any, forbidden: set[str]) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            assert key not in forbidden
            _assert_absent_keys(item, forbidden)
    elif isinstance(value, list):
        for item in value:
            _assert_absent_keys(item, forbidden)
