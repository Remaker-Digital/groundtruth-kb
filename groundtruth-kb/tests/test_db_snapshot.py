"""Tests for ``gt db snapshot`` support."""

from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from datetime import UTC, datetime
from pathlib import Path

import pytest
from click.testing import CliRunner

from groundtruth_kb.cli import main
from groundtruth_kb.config import GTConfig
from groundtruth_kb.db_snapshot import SnapshotError, create_snapshot, default_output_dir, rotate_snapshots


def _create_source_db(path: Path) -> None:
    with closing(sqlite3.connect(path)) as conn:
        conn.execute("CREATE TABLE sample (id INTEGER PRIMARY KEY, name TEXT)")
        conn.executemany("INSERT INTO sample (name) VALUES (?)", [("alpha",), ("beta",)])
        conn.commit()


def _config_for(tmp_path: Path) -> GTConfig:
    source = tmp_path / "project" / "groundtruth.db"
    source.parent.mkdir()
    _create_source_db(source)
    return GTConfig(db_path=source, project_root=source.parent)


def test_snapshot_default_output_dir_is_outside_project_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    project = tmp_path / "project"
    project.mkdir()
    local_data = tmp_path / "local-data"
    monkeypatch.setenv("LOCALAPPDATA", str(local_data))
    monkeypatch.setenv("XDG_DATA_HOME", str(local_data))

    output = default_output_dir(GTConfig(db_path=project / "groundtruth.db", project_root=project))

    assert not output.resolve().is_relative_to(project.resolve())
    assert local_data in output.parents


def test_snapshot_uses_staging_file_then_atomic_publish(tmp_path: Path) -> None:
    cfg = _config_for(tmp_path)
    output_dir = tmp_path / "snapshots"
    staging_dir = tmp_path / "staging"

    result = create_snapshot(cfg, output_dir=output_dir, staging_dir=staging_dir)

    assert result.final_path.exists()
    assert result.manifest_path.exists()
    assert not list(output_dir.glob("*.tmp"))
    assert not list(staging_dir.glob("*.tmp"))
    with closing(sqlite3.connect(result.final_path)) as conn:
        assert conn.execute("SELECT COUNT(*) FROM sample").fetchone()[0] == 2


def test_integrity_failure_quarantines_and_skips_publish(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    cfg = _config_for(tmp_path)
    output_dir = tmp_path / "snapshots"
    staging_dir = tmp_path / "staging"
    monkeypatch.setattr("groundtruth_kb.db_snapshot._integrity_check", lambda _path: "database malformed")

    with pytest.raises(SnapshotError) as exc_info:
        create_snapshot(cfg, output_dir=output_dir, staging_dir=staging_dir)

    assert exc_info.value.exit_code == 1
    assert not list(output_dir.glob("groundtruth-*.db"))
    assert list((staging_dir / "quarantine").glob("*.tmp"))
    assert list((staging_dir / "quarantine").glob("*.manifest.json"))


def test_cross_volume_staging_to_output_is_refused(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    cfg = _config_for(tmp_path)
    called = False

    def fail_if_called(*_args: object, **_kwargs: object) -> None:
        nonlocal called
        called = True

    monkeypatch.setattr("groundtruth_kb.db_snapshot._same_volume", lambda _left, _right: False)
    monkeypatch.setattr("groundtruth_kb.db_snapshot._create_snapshot_in_staging", fail_if_called)

    with pytest.raises(SnapshotError) as exc_info:
        create_snapshot(cfg, output_dir=tmp_path / "out", staging_dir=tmp_path / "stage")

    assert exc_info.value.exit_code == 2
    assert called is False


def test_synced_staging_dir_is_refused(tmp_path: Path) -> None:
    cfg = _config_for(tmp_path)

    with pytest.raises(SnapshotError) as exc_info:
        create_snapshot(cfg, output_dir=tmp_path / "out", staging_dir=tmp_path / "OneDrive" / "stage")

    assert exc_info.value.exit_code == 2
    assert "Refusing to stage" in str(exc_info.value)


def test_synced_output_dir_warns_and_succeeds(tmp_path: Path) -> None:
    cfg = _config_for(tmp_path)

    result = create_snapshot(cfg, output_dir=tmp_path / "OneDrive" / "snapshots", staging_dir=tmp_path / "stage")

    assert result.final_path.exists()
    assert result.warnings
    assert "sync-managed" in result.warnings[0]


def test_manifest_records_snapshot_metadata(tmp_path: Path) -> None:
    cfg = _config_for(tmp_path)

    result = create_snapshot(cfg, output_dir=tmp_path / "out", staging_dir=tmp_path / "stage")
    manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))

    assert manifest["source_db"] == str(cfg.db_path.resolve())
    assert manifest["final_path"] == str(result.final_path)
    assert manifest["integrity_check_result"] == "ok"
    assert manifest["method"] == "vacuum"
    assert manifest["schema_version"] >= 1
    assert manifest["table_counts"]["sample"] == 2
    assert manifest["snapshot_size"] > 0
    assert manifest["source_db_size"] > 0


def test_fast_mode_uses_backup_method_and_copies_data(tmp_path: Path) -> None:
    cfg = _config_for(tmp_path)

    result = create_snapshot(cfg, output_dir=tmp_path / "out", staging_dir=tmp_path / "stage", fast=True)
    manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))

    assert result.method == "backup"
    assert manifest["method"] == "backup"
    with closing(sqlite3.connect(result.final_path)) as conn:
        assert conn.execute("SELECT name FROM sample ORDER BY id").fetchall() == [("alpha",), ("beta",)]


def test_include_chroma_fails_closed_before_writing(tmp_path: Path) -> None:
    cfg = _config_for(tmp_path)
    output_dir = tmp_path / "out"

    with pytest.raises(SnapshotError) as exc_info:
        create_snapshot(cfg, output_dir=output_dir, staging_dir=tmp_path / "stage", include_chroma=True)

    assert exc_info.value.exit_code == 2
    assert "not implemented" in str(exc_info.value)
    assert not output_dir.exists()


def _write_fake_snapshot(output_dir: Path, stamp: str, *, schema_version: int) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"groundtruth-{stamp}.db"
    path.write_bytes(b"snapshot")
    path.with_suffix(".manifest.json").write_text(
        json.dumps({"schema_version": schema_version}),
        encoding="utf-8",
    )
    return path


def test_rotation_keeps_retain_recent(tmp_path: Path) -> None:
    output_dir = tmp_path / "out"
    stamps = ["20260501T000000Z", "20260502T000000Z", "20260503T000000Z", "20260504T000000Z"]
    for stamp in stamps:
        _write_fake_snapshot(output_dir, stamp, schema_version=1)

    result = rotate_snapshots(
        output_dir,
        retain_recent=2,
        retain_daily_days=0,
        now=datetime(2026, 5, 5, tzinfo=UTC),
    )

    assert result.deleted_count == 2
    assert sorted(path.name for path in output_dir.glob("groundtruth-*.db")) == [
        "groundtruth-20260503T000000Z.db",
        "groundtruth-20260504T000000Z.db",
    ]


def test_rotation_keeps_daily_survivors(tmp_path: Path) -> None:
    output_dir = tmp_path / "out"
    for stamp in [
        "20260501T000000Z",
        "20260503T000000Z",
        "20260503T120000Z",
        "20260504T000000Z",
        "20260504T120000Z",
        "20260505T000000Z",
    ]:
        _write_fake_snapshot(output_dir, stamp, schema_version=1)

    result = rotate_snapshots(
        output_dir,
        retain_recent=0,
        retain_daily_days=2,
        now=datetime(2026, 5, 6, tzinfo=UTC),
    )

    assert result.deleted_count == 4
    assert sorted(path.name for path in output_dir.glob("groundtruth-*.db")) == [
        "groundtruth-20260504T120000Z.db",
        "groundtruth-20260505T000000Z.db",
    ]
    assert sorted(path.name for path in output_dir.glob("groundtruth-*.manifest.json")) == [
        "groundtruth-20260504T120000Z.manifest.json",
        "groundtruth-20260505T000000Z.manifest.json",
    ]


def test_rotation_preserves_schema_versions(tmp_path: Path) -> None:
    output_dir = tmp_path / "out"
    _write_fake_snapshot(output_dir, "20260501T000000Z", schema_version=1)
    _write_fake_snapshot(output_dir, "20260502T000000Z", schema_version=2)
    _write_fake_snapshot(output_dir, "20260503T000000Z", schema_version=1)

    result = rotate_snapshots(
        output_dir,
        retain_recent=1,
        retain_daily_days=0,
        now=datetime(2026, 5, 4, tzinfo=UTC),
    )

    assert result.deleted_count == 1
    assert sorted(path.name for path in output_dir.glob("groundtruth-*.db")) == [
        "groundtruth-20260502T000000Z.db",
        "groundtruth-20260503T000000Z.db",
    ]


def test_gt_db_snapshot_cli_success_json(runner: CliRunner, project_dir: Path, tmp_path: Path) -> None:
    _create_source_db(project_dir / "groundtruth.db")

    result = runner.invoke(
        main,
        [
            "--config",
            str(project_dir / "groundtruth.toml"),
            "db",
            "snapshot",
            "--output-dir",
            str(tmp_path / "out"),
            "--staging-dir",
            str(tmp_path / "stage"),
            "--json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["status"] == "ok"
    assert Path(payload["final_path"]).exists()
    assert payload["integrity_result"] == "ok"


def test_gt_db_snapshot_cli_include_chroma_fails_closed(
    runner: CliRunner,
    project_dir: Path,
    tmp_path: Path,
) -> None:
    _create_source_db(project_dir / "groundtruth.db")

    result = runner.invoke(
        main,
        [
            "--config",
            str(project_dir / "groundtruth.toml"),
            "db",
            "snapshot",
            "--output-dir",
            str(tmp_path / "out"),
            "--staging-dir",
            str(tmp_path / "stage"),
            "--include-chroma",
            "--json",
        ],
    )

    assert result.exit_code == 2
    payload = json.loads(result.output)
    assert payload["status"] == "error"
    assert "not implemented" in payload["message"]
    assert not (tmp_path / "out").exists()
