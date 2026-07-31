from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from click.testing import CliRunner
from groundtruth_kb.cli import main
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.project.registry_control_plane import (
    load_registry_snapshot,
    registry_currentness,
    serialize_registry,
)
from groundtruth_kb.project.sot_registry import SoTArtifact, sync_projection


def _record(record_id: str, storage_path: str, coverage_mode: str = "exact") -> SoTArtifact:
    return SoTArtifact(
        id=record_id,
        domain="control_surface",
        lifecycle="active",
        storage_path=storage_path,
        authority_spec_id="GOV-PLATFORM-SOT-REGISTRY-001",
        mutation_api="gt registry observe",
        versioning_policy="git_tracked",
        backup_policy="git_tracked",
        health_check_function="",
        owner_role="shared",
        restore_action="git_restore",
        coverage_mode=coverage_mode,
    )


def _project(tmp_path: Path) -> tuple[Path, Path]:
    root = tmp_path / "project"
    root.mkdir()
    config = root / "groundtruth.toml"
    config.write_text('[groundtruth]\ndb_path = "./groundtruth.db"\nproject_root = "."\n', encoding="utf-8")
    member = root / "member.txt"
    member.write_text("current member bytes", encoding="utf-8")
    bridge = root / "bridge"
    bridge.mkdir()
    (bridge / "example-001.md").write_text("NEW\n", encoding="utf-8")
    records = [
        _record("member", "member.txt"),
        _record("bridge-versioned-files", "bridge/*-[0-9][0-9][0-9].md", "glob"),
    ]
    registry = root / "config" / "registry" / "sot-artifacts.toml"
    packaged = (
        root
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
    payload = serialize_registry(records)
    registry.write_bytes(payload)
    packaged.write_bytes(payload)
    db_path = root / "groundtruth.db"
    KnowledgeDB(db_path=db_path)
    sync_projection(records, db_path, changed_by="test", change_reason="fixture")
    return config, db_path


def test_registry_observe_accepts_artifact_and_path_with_operator_provenance(
    tmp_path: Path,
    monkeypatch,
) -> None:
    config, db_path = _project(tmp_path)
    monkeypatch.setenv("CODEX_SESSION_ID", "session-observer")

    result = CliRunner().invoke(
        main,
        [
            "--config",
            str(config),
            "registry",
            "observe",
            "--artifact",
            "bridge-versioned-files",
            "--path",
            "member.txt",
            "--change-reason",
            "Record current fixture bytes",
            "--json",
        ],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["mode"] == "operator"
    assert payload["actor_session"] == "session-observer"
    assert len(payload["revision_ids"]) == 2
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            "SELECT entry_id, actor_session, operation, changed_by FROM sot_artifact_revisions ORDER BY entry_id"
        ).fetchall()
    assert rows == [
        ("bridge-versioned-files", "session-observer", "direct_in_place_content_change", "registry-observer/cli"),
        ("member", "session-observer", "direct_in_place_content_change", "registry-observer/cli"),
    ]
    snapshot = load_registry_snapshot(project_root=config.parent)
    assert registry_currentness(
        snapshot,
        project_root=config.parent,
        db_path=db_path,
        record_ids={"bridge-versioned-files", "member"},
    )["current"]


def test_registry_observe_fails_closed_for_unknown_identity_and_missing_reason(tmp_path: Path) -> None:
    config, db_path = _project(tmp_path)
    runner = CliRunner()
    registry = config.parent / "config" / "registry" / "sot-artifacts.toml"
    registry_before = registry.read_bytes()
    with sqlite3.connect(db_path) as conn:
        declarations_before = conn.execute(
            "SELECT id, storage_path, lifecycle FROM sot_artifacts ORDER BY id"
        ).fetchall()

    missing_reason = runner.invoke(
        main,
        ["--config", str(config), "registry", "observe", "--artifact", "bridge-versioned-files"],
    )
    unknown = runner.invoke(
        main,
        [
            "--config",
            str(config),
            "registry",
            "observe",
            "--artifact",
            "unknown",
            "--change-reason",
            "must fail",
        ],
    )
    missing_path = runner.invoke(
        main,
        [
            "--config",
            str(config),
            "registry",
            "observe",
            "--path",
            "missing.txt",
            "--change-reason",
            "must fail",
        ],
    )

    assert missing_reason.exit_code != 0
    assert "--change-reason is required" in missing_reason.output
    assert unknown.exit_code != 0
    assert "passive observation record is unregistered: unknown" in unknown.output
    assert missing_path.exit_code != 0
    assert "passive observation target is unregistered: missing.txt" in missing_path.output
    assert registry.read_bytes() == registry_before
    with sqlite3.connect(db_path) as conn:
        declarations_after = conn.execute(
            "SELECT id, storage_path, lifecycle FROM sot_artifacts ORDER BY id"
        ).fetchall()
    assert declarations_after == declarations_before
