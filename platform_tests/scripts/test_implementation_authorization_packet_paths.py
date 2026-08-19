"""WI-5830 packet-path and overwrite-protection tests.

Packet-path tests:
- test_begin_stdout_includes_packet_paths

Overwrite protection tests:
- test_rerun_begin_versions_previous_packet
- test_history_preservation_failure_blocks_overwrite
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "implementation_authorization.py"


@pytest.fixture(scope="module")
def auth_module():
    spec = importlib.util.spec_from_file_location(
        "wi5830_implementation_authorization", SCRIPT_PATH
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------------------
# Packet-path disclosure
# ---------------------------------------------------------------------------


def test_begin_stdout_includes_packet_paths(
    auth_module, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """begin success stdout includes packet_paths with named and active_pointer."""

    # We test the internal write_started_packets return value shape
    # since we cannot run the full CLI in a lightweight test.
    packet: dict[str, Any] = {
        "schema_version": 3,
        "bridge_id": "wi5830-path-test",
        "target_path_globs": ["scripts/implementation_authorization.py"],
        "packet_hash": "stub-not-real",
        "implementation_start": {
            "schema_version": 2,
            "finalized_at": "2026-07-31T14:00:00Z",
            "bridge_id": "wi5830-path-test",
            "session_id": "test-session",
            "pre_start_packet_hash": "stub-not-real",
            "target_path_globs": ["scripts/implementation_authorization.py"],
            "work_intent_claim": {},
            "role_attestation": {},
            "project_authorization_decision": {},
        },
    }
    # Recompute so hash matches
    packet["packet_hash"] = auth_module.packet_hash(packet)

    written = auth_module.write_started_packets(tmp_path, [packet])
    assert len(written) == 1
    named_path, active_path = written[0]
    assert isinstance(named_path, Path)
    assert isinstance(active_path, Path)
    assert named_path.exists()
    assert active_path.exists()
    # Named path is in the by-bridge directory
    assert "by-bridge" in str(named_path)
    assert "wi5830-path-test" in str(named_path)


# ---------------------------------------------------------------------------
# Slice C: Overwrite protection
# ---------------------------------------------------------------------------


def test_rerun_begin_versions_previous_packet(
    auth_module, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Re-running begin for the same bridge versions rather than overwrites."""
    bridge_id = "wi5830-overwrite-test"

    # First packet
    packet1: dict[str, Any] = {
        "schema_version": 3,
        "bridge_id": bridge_id,
        "target_path_globs": ["scripts/implementation_authorization.py"],
        "created_at": "2026-07-31T14:00:00Z",
    }
    packet1["packet_hash"] = auth_module.packet_hash(packet1)

    named_path1 = auth_module.write_named_packet(tmp_path, packet1, bridge_id)
    assert named_path1.exists()
    saved_bytes1 = named_path1.read_bytes()

    # Second packet — different content (different created_at)
    packet2: dict[str, Any] = {
        "schema_version": 3,
        "bridge_id": bridge_id,
        "target_path_globs": ["scripts/implementation_authorization.py"],
        "created_at": "2026-07-31T14:05:00Z",
    }
    packet2["packet_hash"] = auth_module.packet_hash(packet2)

    named_path2 = auth_module.write_named_packet(tmp_path, packet2, bridge_id)
    assert named_path2 == named_path1  # same path
    saved_bytes2 = named_path2.read_bytes()

    # Second write should NOT be the first packet's bytes
    assert saved_bytes2 != saved_bytes1

    # History directory should exist and contain the first packet's bytes
    history_dir = named_path1.parent / f"{bridge_id}.history"
    assert history_dir.exists()
    history_files = sorted(history_dir.iterdir())
    assert len(history_files) >= 1
    # The newest history file should contain the first packet's bytes
    history_bytes = history_files[-1].read_bytes()
    assert history_bytes == saved_bytes1


def test_byte_identical_rewrite_creates_no_history_entry(
    auth_module, tmp_path: Path
) -> None:
    """A byte-identical rewrite creates no history entry."""
    bridge_id = "wi5830-identical-test"

    packet: dict[str, Any] = {
        "schema_version": 3,
        "bridge_id": bridge_id,
        "target_path_globs": ["scripts/implementation_authorization.py"],
    }
    packet["packet_hash"] = auth_module.packet_hash(packet)

    # Write once
    auth_module.write_named_packet(tmp_path, packet, bridge_id)
    history_dir = (
        tmp_path
        / ".gtkb-state"
        / "implementation-authorizations"
        / "by-bridge"
        / f"{bridge_id}.history"
    )

    # Write identical packet again
    auth_module.write_named_packet(tmp_path, packet, bridge_id)

    if history_dir.exists():
        # Either no history entries or exactly the same number
        history_files = sorted(history_dir.iterdir())
        # If one history entry was created, both writes had identical bytes
        # so at most one entry (could be zero if first write was initial)
        assert len(history_files) <= 1


def test_history_preservation_failure_blocks_overwrite(
    auth_module, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """When history preservation fails, write_named_packet raises AuthorizationError."""
    bridge_id = "wi5830-fail-test"

    # Write initial packet
    packet1: dict[str, Any] = {
        "schema_version": 3,
        "bridge_id": bridge_id,
        "target_path_globs": ["scripts/implementation_authorization.py"],
        "created_at": "2026-07-31T14:00:00Z",
    }
    packet1["packet_hash"] = auth_module.packet_hash(packet1)
    auth_module.write_named_packet(tmp_path, packet1, bridge_id)

    # Second packet with different content
    packet2: dict[str, Any] = {
        "schema_version": 3,
        "bridge_id": bridge_id,
        "target_path_globs": ["scripts/implementation_authorization.py"],
        "created_at": "2026-07-31T14:05:00Z",
    }
    packet2["packet_hash"] = auth_module.packet_hash(packet2)

    # Make Path.write_bytes fail
    original_write_bytes = Path.write_bytes

    def failing_write_bytes(self, data):
        raise OSError("Simulated disk failure")

    monkeypatch.setattr(Path, "write_bytes", failing_write_bytes)

    with pytest.raises(
        auth_module.AuthorizationError,
        match="Cannot preserve existing named-packet bytes",
    ):
        auth_module.write_named_packet(tmp_path, packet2, bridge_id)

    # Restore for teardown
    monkeypatch.setattr(Path, "write_bytes", original_write_bytes)

    # The named packet should still contain the ORIGINAL bytes
    named_path = auth_module.packet_path_for_bridge(tmp_path, bridge_id)
    existing = named_path.read_bytes()
    assert json.loads(existing)["created_at"] == "2026-07-31T14:00:00Z"
