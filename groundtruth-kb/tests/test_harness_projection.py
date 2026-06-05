"""Tests for the harness registry hot-path projection generator (WI-3338).

Spec-derived tests for ``REQ-HARNESS-REGISTRY-001`` FR5 (a generated flat
projection serving the DB-independent SessionStart hot path) and FR1 (the
projected harness-record column set).

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

import pytest  # noqa: E402

from groundtruth_kb.harness_projection import (
    HARNESS_CAPABILITIES_RELATIVE_PATH,
    HARNESS_IDENTITIES_RELATIVE_PATH,
    HARNESS_REGISTRY_RELATIVE_PATH,
    PROJECTION_SCHEMA_VERSION,
    HarnessStateError,
    build_projection,
    generate_harness_projection,
    read_capabilities,
    read_identity,
    read_roles,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_READER_PATH = _REPO_ROOT / "scripts" / "harness_projection_reader.py"


def _load_reader_module() -> Any:
    """Load scripts/harness_projection_reader.py by file path.

    The reader is intentionally outside the ``groundtruth_kb`` package; loading
    it by path keeps this round-trip test independent of sys.path setup.
    """
    spec = importlib.util.spec_from_file_location("harness_projection_reader", _READER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _insert_harness(db: Any, **overrides: Any) -> dict[str, Any]:
    """Insert a harness row with sensible defaults; overrides win."""
    fields: dict[str, Any] = dict(
        id="B",
        harness_name="claude",
        harness_type="claude",
        role=["prime-builder"],
        changed_by="test",
        change_reason="test insert",
    )
    fields.update(overrides)
    return db.insert_harness(**fields)


class TestBuildProjection:
    """build_projection() — the pure projection-document builder (FR5/FR1)."""

    def test_build_projection_empty(self) -> None:
        doc = build_projection([])
        assert doc["schema_version"] == PROJECTION_SCHEMA_VERSION
        assert doc["harnesses"] == []
        assert doc["source_of_truth"]
        assert doc["generated_at"].endswith("Z")

    def test_build_projection_carries_fr1_columns(self, db: Any) -> None:
        _insert_harness(
            db,
            id="B",
            harness_name="claude",
            harness_type="claude",
            role=["prime-builder"],
            reviewer_precedence=1,
            invocation_surfaces={"interactive": "claude", "headless": "claude -p"},
            capabilities_ref="config/agent-control/harness-capability-registry.toml",
        )
        doc = build_projection(db.list_harnesses())
        assert len(doc["harnesses"]) == 1
        record = doc["harnesses"][0]
        assert record["id"] == "B"
        assert record["version"] == 1
        assert record["harness_name"] == "claude"
        assert record["harness_type"] == "claude"
        assert record["status"] == "registered"
        assert record["reviewer_precedence"] == 1
        assert record["capabilities_ref"].endswith("harness-capability-registry.toml")
        # role + invocation_surfaces are decoded from JSON text to native types
        assert record["role"] == ["prime-builder"]
        assert record["invocation_surfaces"] == {
            "interactive": "claude",
            "headless": "claude -p",
        }

    def test_build_projection_null_invocation_surfaces(self, db: Any) -> None:
        _insert_harness(db, id="A", harness_name="codex", harness_type="codex", role=["loyal-opposition"])
        record = build_projection(db.list_harnesses())["harnesses"][0]
        assert record["invocation_surfaces"] is None
        assert record["reviewer_precedence"] is None

    def test_build_projection_omits_topology_fr4(self, db: Any) -> None:
        """FR4: topology is a derived pure function, never a persisted field."""
        _insert_harness(db, id="B", role=["prime-builder"])
        doc = build_projection(db.list_harnesses())
        assert "topology" not in doc
        for record in doc["harnesses"]:
            assert "topology" not in record


class TestGenerateHarnessProjection:
    """generate_harness_projection() — the DB-to-file writer."""

    def test_generate_writes_projection_file(self, db: Any, tmp_path: Path) -> None:
        _insert_harness(db, id="B", role=["prime-builder"])
        proj_path = tmp_path / "harness-state" / "harness-registry.json"
        written = generate_harness_projection(db, tmp_path, projection_path=proj_path)
        assert written.exists()
        on_disk = json.loads(written.read_text(encoding="utf-8"))
        assert on_disk["schema_version"] == PROJECTION_SCHEMA_VERSION
        assert on_disk["harnesses"][0]["id"] == "B"

    def test_generate_reflects_current_versions(self, db: Any, tmp_path: Path) -> None:
        _insert_harness(
            db,
            id="C",
            harness_name="antigravity",
            harness_type="antigravity",
            role=["loyal-opposition"],
        )
        _insert_harness(
            db,
            id="C",
            harness_name="antigravity",
            harness_type="antigravity",
            role=["loyal-opposition"],
            status="active",
        )
        proj_path = tmp_path / "harness-registry.json"
        generate_harness_projection(db, tmp_path, projection_path=proj_path)
        on_disk = json.loads(proj_path.read_text(encoding="utf-8"))
        assert len(on_disk["harnesses"]) == 1
        assert on_disk["harnesses"][0]["version"] == 2
        assert on_disk["harnesses"][0]["status"] == "active"

    def test_generate_empty_table_yields_empty_projection(self, db: Any, tmp_path: Path) -> None:
        proj_path = tmp_path / "harness-registry.json"
        generate_harness_projection(db, tmp_path, projection_path=proj_path)
        on_disk = json.loads(proj_path.read_text(encoding="utf-8"))
        assert on_disk["harnesses"] == []
        assert on_disk["schema_version"] == PROJECTION_SCHEMA_VERSION

    def test_env_override_path(self, db: Any, tmp_path: Path, monkeypatch: Any) -> None:
        target = tmp_path / "override" / "registry.json"
        monkeypatch.setenv("GTKB_HARNESS_REGISTRY_PATH", str(target))
        written = generate_harness_projection(db, tmp_path)
        assert written == target.resolve()
        assert target.exists()


class TestGeneratorReaderRoundTrip:
    """A generated projection loads through the DB-free reader (FR5)."""

    def test_generate_then_load_roundtrip(self, db: Any, tmp_path: Path) -> None:
        _insert_harness(
            db,
            id="B",
            harness_name="claude",
            harness_type="claude",
            role=["prime-builder"],
            invocation_surfaces={"headless": "claude -p"},
        )
        proj_path = tmp_path / "harness-state" / "harness-registry.json"
        generate_harness_projection(db, tmp_path, projection_path=proj_path)
        reader = _load_reader_module()
        loaded = reader.load_harness_projection(tmp_path, projection_path=proj_path)
        assert len(loaded["harnesses"]) == 1
        assert loaded["harnesses"][0]["id"] == "B"
        assert loaded["harnesses"][0]["role"] == ["prime-builder"]
        assert loaded["harnesses"][0]["invocation_surfaces"] == {"headless": "claude -p"}


# ──────────────────────────────────────────────────────────────────────────
# WI-4327 / WI-4328: canonical reader entrypoint tests
#
# Verifies that read_roles(), read_identity(), and read_capabilities() are
# the canonical reader entrypoints for the 3 harness-state SoT surfaces and
# that they raise HarnessStateError on missing / malformed inputs.
# ──────────────────────────────────────────────────────────────────────────


def _write_harness_state_fixtures(root: Path) -> None:
    """Create canonical 3-SoT-file fixture set under ``root``."""
    (root / HARNESS_REGISTRY_RELATIVE_PATH).parent.mkdir(parents=True, exist_ok=True)
    (root / HARNESS_REGISTRY_RELATIVE_PATH).write_text(
        json.dumps({"schema_version": 1, "harnesses": [{"id": "B", "harness_name": "claude"}]}),
        encoding="utf-8",
    )
    (root / HARNESS_IDENTITIES_RELATIVE_PATH).write_text(
        json.dumps({"schema_version": 1, "harnesses": {"claude": {"id": "B"}}}),
        encoding="utf-8",
    )
    (root / HARNESS_CAPABILITIES_RELATIVE_PATH).parent.mkdir(parents=True, exist_ok=True)
    (root / HARNESS_CAPABILITIES_RELATIVE_PATH).write_text(
        '[[harness]]\nname = "claude"\ntype = "claude"\n',
        encoding="utf-8",
    )


def test_read_roles_returns_parsed_registry(tmp_path: Path) -> None:
    """read_roles() reads the canonical harness-registry.json SoT."""
    _write_harness_state_fixtures(tmp_path)
    data = read_roles(project_root=tmp_path)
    assert isinstance(data, dict)
    assert data["schema_version"] == 1
    assert data["harnesses"][0]["id"] == "B"


def test_read_identity_returns_parsed_identities(tmp_path: Path) -> None:
    """read_identity() reads the canonical harness-identities.json SoT."""
    _write_harness_state_fixtures(tmp_path)
    data = read_identity(project_root=tmp_path)
    assert isinstance(data, dict)
    assert data["harnesses"]["claude"]["id"] == "B"


def test_read_capabilities_returns_parsed_toml(tmp_path: Path) -> None:
    """read_capabilities() reads the canonical harness-capability-registry.toml SoT."""
    _write_harness_state_fixtures(tmp_path)
    data = read_capabilities(project_root=tmp_path)
    assert isinstance(data, dict)
    assert data["harness"][0]["name"] == "claude"


def test_read_roles_missing_file_raises_harness_state_error(tmp_path: Path) -> None:
    """Missing harness-registry.json raises HarnessStateError, not FileNotFoundError."""
    # No fixtures written; SoT file absent.
    with pytest.raises(HarnessStateError, match="missing"):
        read_roles(project_root=tmp_path)


def test_read_identity_malformed_json_raises_harness_state_error(tmp_path: Path) -> None:
    """Malformed JSON in identities file raises HarnessStateError."""
    (tmp_path / HARNESS_IDENTITIES_RELATIVE_PATH).parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / HARNESS_IDENTITIES_RELATIVE_PATH).write_text("{not valid json", encoding="utf-8")
    with pytest.raises(HarnessStateError, match="malformed JSON"):
        read_identity(project_root=tmp_path)


def test_read_capabilities_malformed_toml_raises_harness_state_error(tmp_path: Path) -> None:
    """Malformed TOML in capabilities file raises HarnessStateError."""
    cap_path = tmp_path / HARNESS_CAPABILITIES_RELATIVE_PATH
    cap_path.parent.mkdir(parents=True, exist_ok=True)
    cap_path.write_text("[[harness\nname = oops missing-bracket", encoding="utf-8")
    with pytest.raises(HarnessStateError, match="malformed TOML"):
        read_capabilities(project_root=tmp_path)


def test_read_roles_non_object_top_level_raises_harness_state_error(tmp_path: Path) -> None:
    """Top-level non-object (e.g. JSON array) raises HarnessStateError."""
    registry_path = tmp_path / HARNESS_REGISTRY_RELATIVE_PATH
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    registry_path.write_text("[1, 2, 3]", encoding="utf-8")
    with pytest.raises(HarnessStateError, match="expected a JSON object"):
        read_roles(project_root=tmp_path)
