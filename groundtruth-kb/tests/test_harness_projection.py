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

from groundtruth_kb.harness_projection import (
    PROJECTION_SCHEMA_VERSION,
    build_projection,
    generate_harness_projection,
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
        _insert_harness(
            db, id="A", harness_name="codex", harness_type="codex", role=["loyal-opposition"]
        )
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
            db, id="C", harness_name="antigravity", harness_type="antigravity",
            role=["loyal-opposition"],
        )
        _insert_harness(
            db, id="C", harness_name="antigravity", harness_type="antigravity",
            role=["loyal-opposition"], status="active",
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
            db, id="B", harness_name="claude", harness_type="claude",
            role=["prime-builder"], invocation_surfaces={"headless": "claude -p"},
        )
        proj_path = tmp_path / "harness-state" / "harness-registry.json"
        generate_harness_projection(db, tmp_path, projection_path=proj_path)
        reader = _load_reader_module()
        loaded = reader.load_harness_projection(tmp_path, projection_path=proj_path)
        assert len(loaded["harnesses"]) == 1
        assert loaded["harnesses"][0]["id"] == "B"
        assert loaded["harnesses"][0]["role"] == ["prime-builder"]
        assert loaded["harnesses"][0]["invocation_surfaces"] == {"headless": "claude -p"}
