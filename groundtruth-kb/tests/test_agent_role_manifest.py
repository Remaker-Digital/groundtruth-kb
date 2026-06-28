"""Tests for the WI-4552 declarative agent/role manifest inventory."""

from __future__ import annotations

import inspect
from pathlib import Path
from typing import Any

import pytest
import yaml

import groundtruth_kb.agent_role_manifest as manifest_module
from groundtruth_kb.agent_role_manifest import load_agent_role_manifest


def _manifest_fixture() -> dict[str, Any]:
    manifest_path = Path("config") / "agent-control" / "declarative-agent-role-manifest.yaml"
    data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def _write_manifest(tmp_path: Path, data: dict[str, Any]) -> Path:
    manifest = tmp_path / "manifest.yaml"
    manifest.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return manifest


def test_agent_role_manifest_parses_inventory() -> None:
    manifest = load_agent_role_manifest()

    assert manifest.schema_version == 1
    assert manifest.manifest_id == "gtkb-declarative-agent-role-manifest"
    assert manifest.authority_status == "inventory_only"
    assert manifest.manifest_hash.startswith("sha256:")
    assert set(manifest.roles) == {"prime-builder", "loyal-opposition"}
    assert manifest.roles["prime-builder"].counterpart_role == "loyal-opposition"
    assert manifest.roles["loyal-opposition"].counterpart_role == "prime-builder"
    assert "A" in manifest.harnesses
    assert manifest.harnesses["A"].harness_name == "codex"
    assert any(harness.roles == ("loyal-opposition",) for harness in manifest.dispatch_targets.values())
    assert set(manifest.event_sources) >= {"A", "E"}


def test_manifest_declares_canonical_reader_entrypoints() -> None:
    manifest = load_agent_role_manifest()

    assert set(manifest.canonical_reader_refs) >= {
        "groundtruth_kb.harness_projection.read_roles",
        "groundtruth_kb.harness_projection.read_identity",
        "groundtruth_kb.harness_projection.read_capabilities",
    }
    assert "GOV-HARNESS-ONBOARDING-CONTRACT-001" in manifest.role_schema_anchors
    assert "DCL-HARNESS-STATE-SOT-READER-CONTRACT-001" in manifest.role_schema_anchors


def test_manifest_to_json_dict_is_stable_and_serializable() -> None:
    manifest = load_agent_role_manifest()
    document = manifest.to_json_dict()

    assert document["manifest_id"] == manifest.manifest_id
    assert document["roles"]["prime-builder"]["counterpart_role"] == "loyal-opposition"
    assert document["harnesses"]["D"]["can_receive_dispatch"] is True


def test_manifest_rejects_duplicate_role_ids(tmp_path: Path) -> None:
    data = _manifest_fixture()
    data["roles"].append(dict(data["roles"][0]))

    with pytest.raises(ValueError, match="duplicate role_id"):
        load_agent_role_manifest(_write_manifest(tmp_path, data))


def test_manifest_rejects_duplicate_harness_ids(tmp_path: Path) -> None:
    data = _manifest_fixture()
    data["harnesses"].append(dict(data["harnesses"][0]))

    with pytest.raises(ValueError, match="duplicate harness_id"):
        load_agent_role_manifest(_write_manifest(tmp_path, data))


def test_manifest_rejects_unknown_role_id(tmp_path: Path) -> None:
    data = _manifest_fixture()
    data["roles"][0]["role_id"] = "observer"

    with pytest.raises(ValueError, match="unknown role_id"):
        load_agent_role_manifest(_write_manifest(tmp_path, data))


def test_manifest_rejects_unknown_harness_role_token(tmp_path: Path) -> None:
    data = _manifest_fixture()
    data["harnesses"][0]["roles"] = ["observer"]

    with pytest.raises(ValueError, match="unknown role token"):
        load_agent_role_manifest(_write_manifest(tmp_path, data))


def test_manifest_rejects_invalid_authority_status(tmp_path: Path) -> None:
    data = _manifest_fixture()
    data["authority_status"] = "authoritative"

    with pytest.raises(ValueError, match="invalid authority_status"):
        load_agent_role_manifest(_write_manifest(tmp_path, data))


def test_manifest_rejects_invalid_dispatch_mode(tmp_path: Path) -> None:
    data = _manifest_fixture()
    data["harnesses"][0]["dispatch_mode"] = "maybe"

    with pytest.raises(ValueError, match="invalid dispatch_mode"):
        load_agent_role_manifest(_write_manifest(tmp_path, data))


def test_manifest_requires_boolean_dispatch_capabilities(tmp_path: Path) -> None:
    data = _manifest_fixture()
    data["harnesses"][0]["can_fire_events"] = "yes"

    with pytest.raises(ValueError, match="requires boolean can_fire_events"):
        load_agent_role_manifest(_write_manifest(tmp_path, data))


def test_agent_role_manifest_has_no_direct_harness_state_or_network_dependency() -> None:
    source = inspect.getsource(manifest_module).lower()

    for forbidden in (
        "harness-state/harness-registry.json",
        "harness-state/harness-identities.json",
        "harness-capability-registry.toml",
        "openai",
        "anthropic",
        "requests",
        "urllib",
        "socket",
        "subprocess",
        "api_key",
    ):
        assert forbidden not in source


def test_manifest_rejects_archive_path(tmp_path: Path) -> None:
    archive_dir = tmp_path / "Claude-Playground"
    archive_dir.mkdir()
    manifest = archive_dir / "manifest.yaml"
    manifest.write_text("schema_version: 1\nmanifest_id: archive\n", encoding="utf-8")

    with pytest.raises(ValueError, match="archive path"):
        load_agent_role_manifest(manifest)
