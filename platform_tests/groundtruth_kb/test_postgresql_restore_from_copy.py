"""Offline restore tool: configuration escaping, WAL-segment arithmetic and archive-chain decisions, without a server."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def _module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "infrastructure" / "postgresql" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


tool = _module("restore_from_copy")
SEGMENT = tool.SEGMENT_BYTES


def test_conf_quote_doubles_backslashes_so_windows_paths_survive_the_config_parser():
    # postgresql.conf single-quoted values interpret backslash escapes; a Windows path written with single
    # backslashes reaches the server with its separators removed (the defect found in the second drill run).
    quoted = tool.conf_quote('copy /Y "D:\\copy\\wal\\%f" "%p"')
    assert quoted == '\'copy /Y "D:\\\\copy\\\\wal\\\\%f" "%p"\''
    assert tool.conf_quote("it's") == "'it''s'"


@pytest.mark.parametrize(
    ("name", "number"),
    [
        ("000000010000000000000025", 0x25),
        ("0000000100000000000000FF", 0xFF),
        ("000000010000000100000000", 0x100),
    ],
)
def test_segment_arithmetic_keeps_the_timeline_and_carries_into_the_log_number(name, number):
    assert tool.segment_number(name) == number
    assert tool.segment_name(name[:8], number) == name
    assert tool.segment_name("00000002", number + 1) == tool.segment_name("00000002", number + 1)


def test_segment_lsn_and_lsn_value_round_trip():
    assert tool.segment_lsn(0x27, 0x28) == "0/27000028"
    assert tool.segment_lsn(0x100) == "1/00000000"
    assert tool.lsn_value("0/27000060") > tool.lsn_value("0/27000028") > tool.lsn_value("0/25000158")


def _copy_layout(
    tmp_path,
    *,
    base_end="000000010000000000000025",
    complete_after=("26", "27"),
    partial=(),
):
    installation = tmp_path / "infrastructure" / "postgresql"
    (installation / "runtime" / "18.6-3" / "bin").mkdir(parents=True)
    for name in ("pg_ctl.exe", "psql.exe", "pg_verifybackup.exe", "pg_isready.exe"):
        (installation / "runtime" / "18.6-3" / "bin" / name).write_bytes(b"")
    (installation / "release.json").write_text(json.dumps({"build": "18.6-3"}), encoding="utf-8")
    for directory in ("backups", "wal", "credentials"):
        (installation / directory).mkdir()
    base = installation / "backups" / "base-20260911T055333Z"
    base.mkdir()
    (base / "backup_manifest").write_text("{}", encoding="utf-8")
    (base / "backup_label").write_text(
        f"START WAL LOCATION: 0/25000028 (file {base_end})\nCHECKPOINT LOCATION: 0/25000080\n",
        encoding="utf-8",
    )
    (installation / "wal" / f"{base_end}.00000028.backup").write_text(
        f"START WAL LOCATION: 0/25000028 (file {base_end})\nSTOP WAL LOCATION: 0/25000158 (file {base_end})\n",
        encoding="utf-8",
    )
    for suffix in ("25", *complete_after):
        segment = installation / "wal" / f"0000000100000000000000{suffix}"
        with segment.open("wb") as handle:
            handle.truncate(SEGMENT)
    for suffix in partial:
        (installation / "wal" / f"0000000100000000000000{suffix}").write_bytes(b"partial")
    return tmp_path, base


def test_archive_chain_records_the_last_complete_segment_after_the_base_and_ignores_partial_files(
    tmp_path,
):
    copy_root, base = _copy_layout(tmp_path, partial=("28",))
    paths = tool.resolve_copy(copy_root)
    chain = tool.archive_chain(paths, base)
    assert chain["base_end_lsn"] == "0/25000158"
    assert chain["archived_after_base"] == [
        "000000010000000000000026",
        "000000010000000000000027",
    ]
    assert chain["last_archived_segment"] == "000000010000000000000027"
    assert chain["last_segment_start_lsn"] == "0/27000000"
    assert "recovery_target_lsn" not in chain


def test_archive_chain_refuses_a_gap_in_the_archived_segments(tmp_path):
    copy_root, base = _copy_layout(tmp_path, complete_after=("27",))
    paths = tool.resolve_copy(copy_root)
    with pytest.raises(tool.RestoreError, match="not contiguous"):
        tool.archive_chain(paths, base)


def test_archive_chain_without_segments_after_the_base_records_the_base_end_segment_as_last(tmp_path):
    copy_root, base = _copy_layout(tmp_path, complete_after=())
    paths = tool.resolve_copy(copy_root)
    chain = tool.archive_chain(paths, base)
    assert chain["archived_after_base"] == [] and chain["last_archived_segment"] == "000000010000000000000025"


def test_prepare_data_writes_an_escaped_restore_command_and_no_recovery_target(
    tmp_path,
):
    copy_root, base = _copy_layout(tmp_path)
    paths = tool.resolve_copy(copy_root)
    chain = tool.archive_chain(paths, base)
    data = tmp_path / "restored" / "data"
    data.parent.mkdir()
    (base / "PG_VERSION").write_text("18\n", encoding="utf-8")
    command = tool.prepare_data(paths, base, data, 5440, chain)
    conf = (data / "postgresql.auto.conf").read_text(encoding="utf-8")
    wal = str(paths["wal"]).replace("/", "\\")
    assert command == f'copy /Y "{wal}\\%f" "%p"'
    assert f"restore_command = {tool.conf_quote(command)}" in conf
    assert "recovery_target" not in conf  # observer finding 1: a target would discard later records of the last segment
    assert (data / "recovery.signal").is_file() and "port = 5440" in conf and "archive_mode = off" in conf
    with pytest.raises(tool.RestoreError, match="not empty"):
        tool.prepare_data(paths, base, data, 5440, chain)


def test_replay_evidence_requires_every_segment_restored_and_replay_into_the_last_segment(tmp_path):
    copy_root, base = _copy_layout(tmp_path)
    chain = tool.archive_chain(tool.resolve_copy(copy_root), base)
    logs = (
        'restored log file "000000010000000000000025" from archive\n'
        'restored log file "000000010000000000000026" from archive\n'
        'restored log file "000000010000000000000027" from archive\n'
        "redo done at 0/27ABCDE0\n"
    )
    complete = tool.replay_evidence(chain, logs, "0/27ABCE10", "0/27ABCDE0")
    assert complete["missing_archived_segments"] == [] and complete["replay_reached_last_archived_segment"]
    assert complete["replay_floor_lsn"] == "0/27000000" and not complete["segment_beyond_chain_restored"]
    # replay that stopped inside segment 26 (the last segment never applied) is not complete
    short = tool.replay_evidence(chain, logs, "0/26FFFFF0", "0/26FFFFF0")
    assert not short["replay_reached_last_archived_segment"]
    # a segment missing from the archive log is reported by name
    partial = tool.replay_evidence(
        chain, logs.replace('"000000010000000000000027"', '"000000010000000000000029"'), "0/27ABCE10", None
    )
    assert partial["missing_archived_segments"] == ["000000010000000000000027"]
    # without segments after the base, replay must reach the base backup's end
    copy_root2, base2 = _copy_layout(tmp_path / "second", complete_after=())
    chain2 = tool.archive_chain(tool.resolve_copy(copy_root2), base2)
    assert tool.replay_evidence(chain2, "", "0/25000158", None)["replay_reached_last_archived_segment"]
    assert not tool.replay_evidence(chain2, "", "0/25000100", None)["replay_reached_last_archived_segment"]


def test_service_environment_derives_credentials_from_the_copy_for_the_original_port_too(tmp_path):
    copy_root, _base = _copy_layout(tmp_path)
    credentials = copy_root / "infrastructure" / "postgresql" / "credentials"
    (credentials / "admin.pgpass").write_text("localhost:5432:*:gtkb_admin:not-a-real-value\n", encoding="utf-8")
    (credentials / "pg_service.conf").write_text(
        "[gtkb_admin]\nhost=localhost\nport=5432\nuser=gtkb_admin\ndbname=gtkb\n"
        "passfile=E:/original-volume-that-does-not-exist/credentials/admin.pgpass\n",
        encoding="utf-8",
    )
    report_dir = tmp_path / "report"
    env, service = tool.service_environment(tool.resolve_copy(copy_root), 5432, report_dir)
    assert service == "restore_admin"
    service_file = Path(env["PGSERVICEFILE"])
    assert service_file.is_relative_to(report_dir)  # observer finding 2: never the copied service file
    body = service_file.read_text(encoding="utf-8")
    assert "original-volume-that-does-not-exist" not in body and "port=5432" in body
    passfile = Path(body.split("passfile=", 1)[1].strip())
    assert passfile.is_relative_to(report_dir)
    assert passfile.read_text(encoding="utf-8") == "127.0.0.1:5432:*:gtkb_admin:not-a-real-value\n"
