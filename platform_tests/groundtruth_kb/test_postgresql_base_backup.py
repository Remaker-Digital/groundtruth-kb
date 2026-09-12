"""Retention decisions of the unattended base-backup tool, without a server."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def _module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "infrastructure" / "postgresql" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


tool = _module("base_backup")


def _base(tmp_path: Path, stamp: str, start: str) -> Path:
    backup = tmp_path / "backups" / f"base-{stamp}"
    backup.mkdir(parents=True)
    (backup / "backup_label").write_text(
        f"START WAL LOCATION: 0/{start[-8:]}000028 (file {start})\nCHECKPOINT LOCATION: 0/{start[-8:]}000080\n"
        "BACKUP METHOD: streamed\nSTART TIMELINE: 1\n",
        encoding="utf-8",
    )
    (backup / "backup_manifest").write_text("{}", encoding="utf-8")
    return backup


def _wal(*segments: str) -> list[str]:
    return list(segments)


def test_start_segment_reads_the_backup_label(tmp_path):
    backup = _base(tmp_path, "one", "000000010000000000000008")
    assert tool.start_segment(backup) == "000000010000000000000008"


def test_retention_keeps_newest_backups_and_prunes_only_wal_before_the_oldest_retained_start(tmp_path):
    older = _base(tmp_path, "20260901T000000Z", "000000010000000000000003")
    middle = _base(tmp_path, "20260905T000000Z", "000000010000000000000008")
    newest = _base(tmp_path, "20260910T000000Z", "00000001000000000000000B")
    wal = _wal(
        "000000010000000000000001",
        "000000010000000000000002",
        "000000010000000000000003",
        "000000010000000000000003.00000028.backup",
        "000000010000000000000007",
        "000000010000000000000008",
        "000000010000000000000008.00000028.backup",
        "00000001000000000000000B",
        "00000001000000000000000C",
        "unrelated.txt",
    )
    plan = tool.retention_plan([older, middle, newest], wal, keep=2)
    assert plan["retained_backups"] == [str(middle), str(newest)]
    assert plan["removed_backups"] == [str(older)]
    # Segment 08 starts the oldest retained backup: everything before it goes; nothing at or after it,
    # and nothing unrecognized, is touched.
    assert plan["removed_wal"] == [
        "000000010000000000000001",
        "000000010000000000000002",
        "000000010000000000000003",
        "000000010000000000000003.00000028.backup",
        "000000010000000000000007",
    ]


def test_retention_never_prunes_wal_by_age_when_no_backup_is_retained():
    plan = tool.retention_plan([], _wal("000000010000000000000001", "000000010000000000000002"), keep=7)
    assert plan == {"retained_backups": [], "removed_backups": [], "removed_wal": []}


def test_retention_keeps_every_backup_when_fewer_than_keep_exist(tmp_path):
    only = _base(tmp_path, "20260910T000000Z", "000000010000000000000005")
    plan = tool.retention_plan([only], _wal("000000010000000000000004", "000000010000000000000005"), keep=7)
    assert plan["retained_backups"] == [str(only)] and plan["removed_backups"] == []
    assert plan["removed_wal"] == ["000000010000000000000004"]


def test_keep_must_be_positive():
    with pytest.raises(tool.BackupError):
        tool.retention_plan([], [], keep=0)


def test_apply_plan_refuses_paths_outside_the_installation_directories(tmp_path):
    paths = {"backups": tmp_path / "backups", "wal": tmp_path / "wal"}
    paths["backups"].mkdir()
    paths["wal"].mkdir()
    outside = tmp_path / "elsewhere" / "base-x"
    outside.mkdir(parents=True)
    with pytest.raises(tool.BackupError):
        tool.apply_plan(paths, {"retained_backups": [], "removed_backups": [str(outside)], "removed_wal": []})
    assert outside.exists()
    with pytest.raises(tool.BackupError):
        tool.apply_plan(paths, {"retained_backups": [], "removed_backups": [], "removed_wal": ["..\\elsewhere\\file"]})


def test_apply_plan_removes_exactly_the_planned_entries(tmp_path):
    paths = {"backups": tmp_path / "backups", "wal": tmp_path / "wal"}
    paths["wal"].mkdir()
    doomed = _base(tmp_path, "old", "000000010000000000000001")
    kept = _base(tmp_path, "new", "000000010000000000000004")
    for name in ("000000010000000000000001", "000000010000000000000004"):
        (paths["wal"] / name).write_bytes(b"x")
    tool.apply_plan(
        paths,
        {
            "retained_backups": [str(kept)],
            "removed_backups": [str(doomed)],
            "removed_wal": ["000000010000000000000001"],
        },
    )
    assert not doomed.exists() and kept.exists()
    assert sorted(entry.name for entry in paths["wal"].iterdir()) == ["000000010000000000000004"]
