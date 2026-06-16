"""Tests for scripts/protected_mutation_guard.py.

Covers:
- unprotected targets are allowed without bridge evidence;
- protected targets deny when bridge GO is missing;
- protected targets deny when the implementation packet is missing, stale, or target paths do not match;
- protected targets deny when no current work-intent claim exists;
- protected targets allow only when GO, packet, claim, and target scope align;
- outside-root target paths deny deterministically;
- reason codes remain stable for later hook integrations.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from scripts import bridge_work_intent_registry
from scripts.protected_mutation_guard import evaluate_mutation


@pytest.fixture()
def root(tmp_path: Path, monkeypatch) -> Path:
    """Fixture that initializes a temporary project root with harness-registry."""
    monkeypatch.delenv("GTKB_HARNESS_REGISTRY_PATH", raising=False)

    registry_dir = tmp_path / "harness-state"
    registry_dir.mkdir(parents=True, exist_ok=True)
    registry_file = registry_dir / "harness-registry.json"

    registry_content = {
        "schema_version": 1,
        "source_of_truth": "MemBase harnesses table (groundtruth.db)",
        "harnesses": [
            {"id": "A", "harness_name": "Antigravity", "role": ["prime-builder"]},
            {"id": "B", "harness_name": "Codex", "role": ["loyal-opposition"]},
        ],
    }
    registry_file.write_text(json.dumps(registry_content), encoding="utf-8")

    # Write interactive session marker fallback so that we are prime-eligible
    marker_dir = tmp_path / ".claude" / "session"
    marker_dir.mkdir(parents=True, exist_ok=True)
    marker_file = marker_dir / "active-session-role.json"
    marker_file.write_text(json.dumps({"role": "prime-builder"}), encoding="utf-8")

    return tmp_path


def _write_bridge_files(project_root: Path, bridge_id: str, status: str = "GO") -> None:
    bridge_dir = project_root / "bridge"
    bridge_dir.mkdir(parents=True, exist_ok=True)

    proposal = bridge_dir / f"{bridge_id}.md"
    proposal.write_text('NEW\n\nFixture proposal\n\ntarget_paths: ["scripts/dummy.py"]\n', encoding="utf-8")

    verdict = bridge_dir / f"{bridge_id}-002.md"
    verdict.write_text(f"{status}\n\nFixture verdict\n", encoding="utf-8")


def _write_packet(
    project_root: Path,
    bridge_id: str,
    target_globs: list[str],
    expires_at_str: str,
    latest_status: str = "GO",
) -> Path:
    packet = {
        "bridge_id": bridge_id,
        "created_at": "2026-06-16T20:00:00Z",
        "expires_at": expires_at_str,
        "go_file": f"bridge/{bridge_id}-002.md",
        "latest_status": latest_status,
        "spec_links": [],
        "target_path_globs": target_globs,
    }
    # Compute packet_hash
    material = {key: value for key, value in packet.items() if key != "packet_hash"}
    encoded = json.dumps(material, sort_keys=True, separators=(",", ":")).encode("utf-8")
    packet["packet_hash"] = "sha256:" + hashlib.sha256(encoded).hexdigest()

    packet_dir = project_root / ".gtkb-state" / "implementation-authorizations" / "by-bridge"
    packet_dir.mkdir(parents=True, exist_ok=True)
    packet_file = packet_dir / f"{bridge_id}.json"
    packet_file.write_text(json.dumps(packet), encoding="utf-8")
    return packet_file


def test_unprotected_targets_allowed(root: Path) -> None:
    res = evaluate_mutation(
        root,
        ["bridge/some-doc.md", "independent-progress-assessments/report.md"],
        harness_id="A",
        session_id="session-1",
    )
    assert res.allowed is True
    assert res.reason_code == "not_protected"


def test_target_outside_project_root_denied(root: Path) -> None:
    res = evaluate_mutation(root, ["../escaped.py"], harness_id="A", session_id="session-1")
    assert res.allowed is False
    assert res.reason_code == "target_outside_project_root"


def test_forbidden_operation_bridge_index_denied(root: Path) -> None:
    res = evaluate_mutation(root, ["bridge/INDEX.md"], harness_id="A", session_id="session-1")
    assert res.allowed is False
    assert res.reason_code == "forbidden_operation"
    assert "bridge/INDEX.md" in res.details


def test_forbidden_operation_command_denied(root: Path) -> None:
    res = evaluate_mutation(
        root, ["scripts/dummy.py"], harness_id="A", session_id="session-1", command="git push origin main --force"
    )
    assert res.allowed is False
    assert res.reason_code == "forbidden_operation"
    assert "Command contains forbidden" in res.details


def test_forbidden_operation_tool_denied(root: Path) -> None:
    res = evaluate_mutation(
        root, ["scripts/dummy.py"], harness_id="A", session_id="session-1", tool_name="production_deployment"
    )
    assert res.allowed is False
    assert res.reason_code == "forbidden_operation"
    assert "Tool name contains forbidden" in res.details


def test_role_validation_unauthorized_harness_denied(root: Path) -> None:
    res = evaluate_mutation(
        root,
        ["scripts/dummy.py"],
        harness_id="B",  # loyal-opposition
        session_id="session-1",
    )
    assert res.allowed is False
    assert res.reason_code == "forbidden_operation"
    assert "not authorized as a Prime Builder" in res.details


def test_role_validation_unknown_harness_denied(root: Path) -> None:
    res = evaluate_mutation(root, ["scripts/dummy.py"], harness_id=None, harness_name=None, session_id="session-1")
    assert res.allowed is False
    assert res.reason_code == "forbidden_operation"
    assert "identity could not be resolved" in res.details


def test_role_validation_unregistered_harness_denied(root: Path) -> None:
    res = evaluate_mutation(
        root,
        ["scripts/dummy.py"],
        harness_id="X",  # Unregistered ID
        session_id="session-1",
    )
    assert res.allowed is False
    assert res.reason_code == "forbidden_operation"
    assert "not authorized as a Prime Builder" in res.details


def test_missing_work_intent_claim_denied(root: Path) -> None:
    res = evaluate_mutation(root, ["scripts/dummy.py"], harness_id="A", session_id="session-1")
    assert res.allowed is False
    assert res.reason_code == "missing_or_stale_claim"
    assert "No active work-intent claim found" in res.details


def test_missing_implementation_packet_denied(root: Path) -> None:
    bridge_id = "test-bridge"
    session_id = "session-1"
    _write_bridge_files(root, bridge_id, status="GO")

    # Acquire claim in DB
    bridge_work_intent_registry.acquire(bridge_id, session_id, project_root=root)

    res = evaluate_mutation(root, ["scripts/dummy.py"], harness_id="A", session_id=session_id)
    assert res.allowed is False
    assert res.reason_code == "missing_implementation_packet"
    assert "packet for bridge test-bridge not found" in res.details.lower()


def test_stale_implementation_packet_denied(root: Path) -> None:
    bridge_id = "test-bridge"
    session_id = "session-1"
    _write_bridge_files(root, bridge_id, status="GO")
    _write_packet(root, bridge_id, ["scripts/dummy.py"], "2026-06-16T19:00:00Z")  # Expired

    # Acquire claim in DB
    bridge_work_intent_registry.acquire(bridge_id, session_id, project_root=root)

    res = evaluate_mutation(root, ["scripts/dummy.py"], harness_id="A", session_id=session_id)
    assert res.allowed is False
    assert res.reason_code == "stale_implementation_packet"
    assert "has expired" in res.details


def test_missing_bridge_go_denied(root: Path) -> None:
    bridge_id = "test-bridge"
    session_id = "session-1"
    _write_bridge_files(root, bridge_id, status="VERIFIED")  # live status shifted to VERIFIED
    _write_packet(root, bridge_id, ["scripts/dummy.py"], "2026-06-16T23:59:59Z")

    # Acquire claim in DB
    bridge_work_intent_registry.acquire(bridge_id, session_id, project_root=root)

    res = evaluate_mutation(root, ["scripts/dummy.py"], harness_id="A", session_id=session_id)
    assert res.allowed is False
    assert res.reason_code == "missing_bridge_go"


def test_target_out_of_scope_denied(root: Path) -> None:
    bridge_id = "test-bridge"
    session_id = "session-1"
    _write_bridge_files(root, bridge_id, status="GO")
    _write_packet(root, bridge_id, ["scripts/dummy.py"], "2026-06-16T23:59:59Z")

    # Acquire claim in DB
    bridge_work_intent_registry.acquire(bridge_id, session_id, project_root=root)

    res = evaluate_mutation(
        root,
        ["scripts/other.py"],  # scripts/other.py is protected but not matching "scripts/dummy.py"
        harness_id="A",
        session_id=session_id,
    )
    assert res.allowed is False
    assert res.reason_code == "target_out_of_scope"
    assert "outside packet scope" in res.details


def test_fully_authorized_mutation_allowed(root: Path) -> None:
    bridge_id = "test-bridge"
    session_id = "session-1"
    _write_bridge_files(root, bridge_id, status="GO")
    _write_packet(root, bridge_id, ["scripts/dummy.py"], "2026-06-16T23:59:59Z")

    # Acquire claim in DB
    bridge_work_intent_registry.acquire(bridge_id, session_id, project_root=root)

    res = evaluate_mutation(root, ["scripts/dummy.py"], harness_id="A", session_id=session_id)
    assert res.allowed is True
    assert res.reason_code == "authorized"
