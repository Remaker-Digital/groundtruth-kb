"""Tests for the DB-independent harness registry projection reader (WI-3338).

Spec-derived tests for ``REQ-HARNESS-REGISTRY-001`` FR5: the SessionStart
hot-path reader must load the projection without a DB connection and degrade
gracefully when the projection is absent or malformed.

This test module imports only ``scripts.harness_projection_reader`` and the
standard library — it does NOT import ``groundtruth_kb``, which is itself part
of the FR5 DB-independence evidence.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import json
from pathlib import Path

from scripts.harness_projection_reader import (
    harness_registry_path,
    load_harness_projection,
)

_VALID_PROJECTION = {
    "schema_version": 1,
    "source_of_truth": "MemBase harnesses table (groundtruth.db)",
    "description": "test fixture",
    "generated_at": "2026-05-16T00:00:00Z",
    "harnesses": [
        {
            "id": "B",
            "version": 1,
            "harness_name": "claude",
            "harness_type": "claude",
            "status": "active",
            "role": ["prime-builder"],
            "reviewer_precedence": None,
            "invocation_surfaces": {"headless": "claude -p"},
            "capabilities_ref": "config/agent-control/harness-capability-registry.toml",
        }
    ],
}


def _write(path: Path, payload: object) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_load_valid_projection(tmp_path: Path) -> None:
    proj = _write(tmp_path / "harness-state" / "harness-registry.json", _VALID_PROJECTION)
    loaded = load_harness_projection(tmp_path, projection_path=proj)
    assert loaded["schema_version"] == 1
    assert len(loaded["harnesses"]) == 1
    assert loaded["harnesses"][0]["id"] == "B"
    assert loaded["harnesses"][0]["role"] == ["prime-builder"]


def test_load_default_path(tmp_path: Path) -> None:
    _write(tmp_path / "harness-state" / "harness-registry.json", _VALID_PROJECTION)
    loaded = load_harness_projection(tmp_path)
    assert loaded["harnesses"][0]["id"] == "B"


def test_load_missing_file_returns_empty(tmp_path: Path) -> None:
    loaded = load_harness_projection(tmp_path)
    assert loaded["harnesses"] == []
    assert loaded["schema_version"] == 1


def test_load_malformed_file_returns_empty(tmp_path: Path) -> None:
    proj = tmp_path / "harness-state" / "harness-registry.json"
    proj.parent.mkdir(parents=True, exist_ok=True)
    proj.write_text("{not valid json", encoding="utf-8")
    loaded = load_harness_projection(tmp_path, projection_path=proj)
    assert loaded["harnesses"] == []


def test_load_non_dict_payload_returns_empty(tmp_path: Path) -> None:
    proj = _write(tmp_path / "registry.json", ["not", "a", "dict"])
    loaded = load_harness_projection(tmp_path, projection_path=proj)
    assert loaded["harnesses"] == []


def test_normalize_drops_non_dict_harness_entries(tmp_path: Path) -> None:
    payload = {"schema_version": 1, "harnesses": [{"id": "B"}, "junk", 42, {"id": "A"}]}
    proj = _write(tmp_path / "registry.json", payload)
    loaded = load_harness_projection(tmp_path, projection_path=proj)
    assert [h["id"] for h in loaded["harnesses"]] == ["B", "A"]


def test_env_override_path(tmp_path: Path, monkeypatch) -> None:
    target = _write(tmp_path / "elsewhere" / "reg.json", _VALID_PROJECTION)
    monkeypatch.setenv("GTKB_HARNESS_REGISTRY_PATH", str(target))
    loaded = load_harness_projection(tmp_path)
    assert loaded["harnesses"][0]["id"] == "B"
    assert harness_registry_path(tmp_path) == target.resolve()


def test_reader_module_is_db_independent() -> None:
    """FR5: the reader module must not import groundtruth_kb or open a DB."""
    reader_source = Path(__file__).resolve().parents[2] / "scripts" / "harness_projection_reader.py"
    source = reader_source.read_text(encoding="utf-8")
    assert "import groundtruth_kb" not in source
    assert "from groundtruth_kb" not in source
    assert "import sqlite3" not in source
    assert "from sqlite3" not in source
