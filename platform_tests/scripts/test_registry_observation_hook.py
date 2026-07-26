# Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Cross-harness tests for capability-bound registry observation."""

from __future__ import annotations

import importlib.util
import json
import sqlite3
from pathlib import Path

import pytest
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.project.registry_control_plane import (
    RegistryAuthorizationError,
    mint_observation_capability,
    serialize_registry,
)
from groundtruth_kb.project.sot_registry import SoTArtifact, sync_projection

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "registry_observation_hook.py"


def _load_hook():
    spec = importlib.util.spec_from_file_location("registry_observation_hook_test", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _record() -> SoTArtifact:
    return SoTArtifact(
        id="member",
        domain="control_surface",
        lifecycle="active",
        storage_path="member.txt",
        authority_spec_id="GOV-PLATFORM-SOT-REGISTRY-001",
        mutation_api="governed edit",
        versioning_policy="git_tracked",
        backup_policy="git_tracked",
        health_check_function="",
        owner_role="shared",
        restore_action="git_restore",
        coverage_mode="exact",
    )


def _fixture(tmp_path: Path) -> tuple[Path, Path, Path]:
    registry = tmp_path / "config" / "registry" / "sot-artifacts.toml"
    packaged = (
        tmp_path
        / "groundtruth-kb"
        / "src"
        / "groundtruth_kb"
        / "context"
        / "registries"
        / "v1"
        / "config"
        / "registry"
        / "sot-artifacts.toml"
    )
    registry.parent.mkdir(parents=True)
    packaged.parent.mkdir(parents=True)
    payload = serialize_registry([_record()])
    registry.write_bytes(payload)
    packaged.write_bytes(payload)
    (tmp_path / "member.txt").write_text("before", encoding="utf-8")
    db_path = tmp_path / "groundtruth.db"
    KnowledgeDB(db_path=db_path)
    sync_projection([_record()], db_path, changed_by="test", change_reason="fixture")
    return registry, packaged, db_path


def _mint(tmp_path: Path, registry: Path, packaged: Path, db_path: Path) -> dict[str, object]:
    return mint_observation_capability(
        target_paths=["member.txt"],
        session_id="session",
        tool_event_id="event",
        bridge_id="bridge",
        start_packet_hash="packet",
        pauth_decision={"allowed": True},
        operation="Edit",
        authorized=True,
        project_root=tmp_path,
        registry_path=registry,
        packaged_registry_path=packaged,
        db_path=db_path,
    )


def _write_intent(hook, tmp_path: Path, minted: dict[str, object], **overrides: object) -> Path:
    payload: dict[str, object] = {
        "capability": minted["capability"],
        "target_paths": minted["paths"],
        "preimage_digests": minted["preimage_digests"],
        "session_id": "session",
        "tool_event_id": "event",
        "bridge_id": "bridge",
        "start_packet_hash": "packet",
        "operation": "Edit",
        "change_reason": "test",
    }
    payload.update(overrides)
    path = hook.intent_path(tmp_path, "session", "event")
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _post_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "session_id": "session",
        "tool_use_id": "event",
        "tool_name": "Edit",
        "tool_input": {"file_path": "member.txt"},
        "tool_response": {"success": True},
    }
    payload.update(overrides)
    return payload


def test_positive_event_consumes_exactly_once(tmp_path: Path) -> None:
    hook = _load_hook()
    registry, packaged, db_path = _fixture(tmp_path)
    capability = _mint(tmp_path, registry, packaged, db_path)
    intent = _write_intent(hook, tmp_path, capability)
    (tmp_path / "member.txt").write_text("after", encoding="utf-8")
    revisions = hook.consume_payload(_post_payload(), project_root=tmp_path)
    assert len(revisions) == 1
    assert not intent.exists()
    with pytest.raises(RegistryAuthorizationError, match="no authorized observation intent"):
        hook.consume_payload(_post_payload(), project_root=tmp_path)


@pytest.mark.parametrize(
    ("intent_override", "payload_override", "message"),
    [
        ({"session_id": "other"}, {}, "binding mismatch"),
        ({"tool_event_id": "other"}, {}, "binding mismatch"),
        ({"bridge_id": "other"}, {}, "bridge_id binding mismatch"),
        ({"start_packet_hash": "other"}, {}, "start_packet_hash binding mismatch"),
        ({}, {"tool_response": {"success": False}}, "failed tools"),
    ],
)
def test_mismatch_and_failed_tool_events_are_denied(
    tmp_path: Path,
    intent_override: dict[str, object],
    payload_override: dict[str, object],
    message: str,
) -> None:
    hook = _load_hook()
    registry, packaged, db_path = _fixture(tmp_path)
    capability = _mint(tmp_path, registry, packaged, db_path)
    _write_intent(hook, tmp_path, capability, **intent_override)
    (tmp_path / "member.txt").write_text("after", encoding="utf-8")
    with pytest.raises(RegistryAuthorizationError, match=message):
        hook.consume_payload(_post_payload(**payload_override), project_root=tmp_path)


def test_fabricated_capability_is_denied_without_revision(tmp_path: Path) -> None:
    hook = _load_hook()
    registry, packaged, db_path = _fixture(tmp_path)
    capability = _mint(tmp_path, registry, packaged, db_path)
    _write_intent(hook, tmp_path, capability, capability="fabricated")
    with pytest.raises(RegistryAuthorizationError, match="fabricated"):
        hook.consume_payload(_post_payload(), project_root=tmp_path)
    with sqlite3.connect(db_path) as conn:
        assert conn.execute("SELECT COUNT(*) FROM sot_artifact_revisions").fetchone()[0] == 0
