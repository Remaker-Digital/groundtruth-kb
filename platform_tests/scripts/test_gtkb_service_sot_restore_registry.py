"""Spec-derived tests for WI-5044 restore-action registry metadata."""

from __future__ import annotations

import sys
import textwrap
import tomllib
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT / "groundtruth-kb" / "src") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "groundtruth-kb" / "src"))

from groundtruth_kb.project.registry_control_plane import load_registry_snapshot  # noqa: E402
from groundtruth_kb.project.sot_registry import (  # noqa: E402
    InvalidSoTRecord,
    load_toml,
)

_REGISTRY = _REPO_ROOT / "config" / "registry" / "sot-artifacts.toml"
_VALID_ACTIONS = {
    "manual",
    "visibility_only",
    "git_restore",
    "membase_export_restore",
    "regenerate_from_source",
    "ensure_alive",
    "noop",
}


def _write_registry(tmp_path: Path, *, restore_action: str = "ensure_alive") -> Path:
    path = tmp_path / "config" / "registry" / "sot-artifacts.toml"
    path.parent.mkdir(parents=True)
    path.write_text(
        textwrap.dedent(
            f"""
            [[artifacts]]
            id = "fixture-artifact"
            domain = "control_surface"
            lifecycle = "active"
            storage_path = "config/fixture.toml"
            coverage_mode = "exact"
            authority_spec_id = "GOV-FILE-BRIDGE-AUTHORITY-001"
            mutation_api = "fixture writer"
            versioning_policy = "git_tracked"
            backup_policy = "git_tracked"
            restore_action = "{restore_action}"
            health_check_function = ""
            owner_role = "shared"
            """
        ),
        encoding="utf-8",
    )
    return path


def test_shipped_registry_declares_restore_action_for_every_record() -> None:
    raw_records = tomllib.loads(_REGISTRY.read_text(encoding="utf-8"))["artifacts"]

    assert raw_records
    assert all("restore_action" in record for record in raw_records)
    assert {record["restore_action"] for record in raw_records} <= _VALID_ACTIONS
    assert {
        "manual",
        "visibility_only",
        "git_restore",
        "membase_export_restore",
        "regenerate_from_source",
        "ensure_alive",
        "noop",
    } <= {record["restore_action"] for record in raw_records}


def test_loader_rejects_invalid_restore_action(tmp_path: Path) -> None:
    path = _write_registry(tmp_path, restore_action="run-anything")

    with pytest.raises(InvalidSoTRecord, match="restore_action"):
        load_toml(path)


@pytest.mark.parametrize("restore_action", sorted(_VALID_ACTIONS))
def test_canonical_declaration_preserves_restore_action_without_mirrors(tmp_path: Path, restore_action: str) -> None:
    registry_path = _write_registry(tmp_path, restore_action=restore_action)
    database = tmp_path / "groundtruth.db"
    database.write_bytes(b"unreadable historical SQLite sentinel")
    packaged = tmp_path / "groundtruth-kb" / "src" / "groundtruth_kb" / "context" / "registries"
    before = registry_path.read_bytes()

    snapshot = load_registry_snapshot(project_root=tmp_path)

    assert len(snapshot.records) == 1
    assert snapshot.records[0].id == "fixture-artifact"
    assert snapshot.records[0].restore_action == restore_action
    assert registry_path.read_bytes() == before
    assert database.read_bytes() == b"unreadable historical SQLite sentinel"
    assert not packaged.exists()
