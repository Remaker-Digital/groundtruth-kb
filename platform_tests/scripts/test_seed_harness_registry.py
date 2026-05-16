"""Tests for the harness-registry seed migration (WI-3342 Slice A).

Spec-derived tests for ``REQ-HARNESS-REGISTRY-001`` FR1 (the ``harnesses``
table is populated from the legacy harness-state JSON) and FR5 (the hot-path
projection is regenerated after seeding), plus the migration's idempotence.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_PACKAGE_SRC = _REPO_ROOT / "groundtruth-kb" / "src"
if str(_PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(_PACKAGE_SRC))

from groundtruth_kb.db import KnowledgeDB  # noqa: E402

_SEED_SCRIPT = _REPO_ROOT / "scripts" / "seed_harness_registry.py"


def _load_seed_module() -> Any:
    """Load scripts/seed_harness_registry.py by file path."""
    spec = importlib.util.spec_from_file_location("seed_harness_registry", _SEED_SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_seed = _load_seed_module()


@pytest.fixture(autouse=True)
def _clean_registry_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep the projection at the default in-project path."""
    monkeypatch.delenv("GTKB_HARNESS_REGISTRY_PATH", raising=False)


def _project(tmp_path: Path, role_map: dict[str, Any] | None = None) -> Path:
    """Create a temp project with harness-state identity + role-assignment JSON."""
    state = tmp_path / "harness-state"
    state.mkdir()
    identities = {"harnesses": {"claude": {"id": "B"}, "codex": {"id": "A"}}}
    roles = role_map if role_map is not None else {
        "harnesses": {
            "A": {"role": ["loyal-opposition"], "harness_type": "codex"},
            "B": {"role": ["prime-builder"], "harness_type": "claude"},
        }
    }
    (state / "harness-identities.json").write_text(json.dumps(identities), encoding="utf-8")
    (state / "role-assignments.json").write_text(json.dumps(roles), encoding="utf-8")
    return tmp_path


def _db(tmp_path: Path) -> KnowledgeDB:
    return KnowledgeDB(db_path=tmp_path / "seed-test.db")


def _decode(value: Any) -> Any:
    """Decode a possibly-JSON-text harness field to a native value."""
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    return value


def test_seed_inserts_live_harnesses_at_active(tmp_path: Path) -> None:
    root = _project(tmp_path)
    db = _db(tmp_path)
    _seed.seed_harness_registry(db, root)
    harnesses = {h["id"]: h for h in db.list_harnesses()}
    assert set(harnesses) == {"A", "B"}
    assert harnesses["A"]["status"] == "active"
    assert harnesses["B"]["status"] == "active"


def test_seed_carries_role_and_identity_from_legacy_json(tmp_path: Path) -> None:
    root = _project(tmp_path)
    db = _db(tmp_path)
    _seed.seed_harness_registry(db, root)
    a = db.get_harness("A")
    b = db.get_harness("B")
    assert a["harness_name"] == "codex"
    assert a["harness_type"] == "codex"
    assert _decode(a["role"]) == ["loyal-opposition"]
    assert b["harness_name"] == "claude"
    assert b["harness_type"] == "claude"
    assert _decode(b["role"]) == ["prime-builder"]


def test_seed_is_idempotent(tmp_path: Path) -> None:
    root = _project(tmp_path)
    db = _db(tmp_path)
    first = _seed.seed_harness_registry(db, root)
    second = _seed.seed_harness_registry(db, root)
    assert first["seeded"] == ["A", "B"]
    assert second["seeded"] == []
    assert second["skipped"] == ["A", "B"]
    for hid in ("A", "B"):
        count = db._get_conn().execute(
            "SELECT COUNT(*) FROM harnesses WHERE id = ?", (hid,)
        ).fetchone()[0]
        assert count == 1


def test_seed_skips_harness_already_in_table(tmp_path: Path) -> None:
    root = _project(tmp_path)
    db = _db(tmp_path)
    db.insert_harness(
        id="A",
        harness_name="codex",
        harness_type="codex",
        role=["loyal-opposition"],
        changed_by="test",
        change_reason="pre-seed insert",
        status="active",
    )
    summary = _seed.seed_harness_registry(db, root)
    assert "A" in summary["skipped"]
    assert summary["seeded"] == ["B"]


def test_seed_regenerates_projection(tmp_path: Path) -> None:
    root = _project(tmp_path)
    db = _db(tmp_path)
    summary = _seed.seed_harness_registry(db, root)
    projection = Path(summary["projection_path"])
    assert projection.exists()
    doc = json.loads(projection.read_text(encoding="utf-8"))
    assert {h["id"] for h in doc["harnesses"]} == {"A", "B"}


def test_seed_summary_reports_seeded_and_skipped(tmp_path: Path) -> None:
    root = _project(tmp_path)
    db = _db(tmp_path)
    summary = _seed.seed_harness_registry(db, root)
    assert summary["seeded"] == ["A", "B"]
    assert summary["skipped"] == []
    assert summary["projection_path"].endswith("harness-registry.json")
