#!/usr/bin/env python3
"""Restore the GT-KB PostgreSQL installation from an off-volume copy, using only that copy.

Operator tool for storage-loss recovery. Given a copy of the GT-KB root (for example D:\\GT-KB-LocalBackup, written
by the nightly SyncBackSE job), it restores the newest verified base backup into a fresh data directory, replays
every complete archived WAL segment that follows it from the copy's archive, promotes the server, and reports
what was recovered. Everything it needs is inside the copy: the PostgreSQL binaries under
infrastructure/postgresql/runtime/<build>/bin, the base backups and WAL archive, and the credential files.
No file from the original volume is read.

    python restore_from_copy.py --copy D:\\GT-KB-LocalBackup --data E:\\GT-KB\\infrastructure\\postgresql\\data --port 5432

Use --port 5440 (any free port) and --stop to rehearse a recovery beside a running installation. For every port,
the original one included, the libpq service file and password file are derived inside --report-dir from the
copy's own admin credential file (values are never printed; removed with --stop): the copied pg_service.conf is
never used because its passfile entries name the original volume. Recovery runs through the ENTIRE complete
archived WAL: no recovery target is set (a target at the first record of the last segment would discard later
committed records in that segment); PostgreSQL replays every archived segment until the archive ends and then
promotes, and the tool proves afterwards that every complete archived segment after the base was restored from
the archive and that replay reached the last archived segment. The report lists every segment restored from the
archive, the final redo and replay positions and the row count of every table, so a restore that only replayed
the base backup cannot pass as a full recovery.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

SEGMENT_BYTES = 16 * 1024 * 1024
SEGMENT_NAME = re.compile(r"^[0-9A-F]{24}$")


class RestoreError(RuntimeError):
    pass


def segment_number(name: str) -> int:
    return int(name[8:16], 16) * 256 + int(name[16:24], 16)


def segment_name(timeline_hex: str, number: int) -> str:
    return f"{timeline_hex}{number // 256:08X}{number % 256:08X}"


def segment_lsn(number: int, offset: int = 0) -> str:
    value = number * SEGMENT_BYTES + offset
    return f"{value >> 32:X}/{value & 0xFFFFFFFF:08X}"


def lsn_value(text: str) -> int:
    high, low = text.split("/")
    return (int(high, 16) << 32) + int(low, 16)


def conf_quote(value: str) -> str:
    """Single-quoted postgresql.conf value: backslashes and quotes must be escaped."""
    return "'" + value.replace("\\", "\\\\").replace("'", "''") + "'"


def resolve_copy(copy_root: Path) -> dict[str, Path]:
    installation = copy_root / "infrastructure" / "postgresql"
    release = json.loads((installation / "release.json").read_text(encoding="utf-8"))
    binaries = installation / "runtime" / release["build"] / "bin"
    for name in ("pg_ctl.exe", "psql.exe", "pg_verifybackup.exe", "pg_isready.exe"):
        if not (binaries / name).is_file():
            raise RestoreError(f"the copy lacks {name} under {binaries}")
    for directory in ("backups", "wal", "credentials"):
        if not (installation / directory).is_dir():
            raise RestoreError(f"the copy lacks infrastructure/postgresql/{directory}")
    return {
        "installation": installation,
        "binaries": binaries,
        "backups": installation / "backups",
        "wal": installation / "wal",
        "credentials": installation / "credentials",
    }


def newest_verified_base(paths: dict[str, Path]) -> Path:
    candidates = sorted(
        p
        for p in paths["backups"].glob("base-*")
        if (p / "backup_manifest").is_file() and (p / "backup_label").is_file()
    )
    if not candidates:
        raise RestoreError("the copy holds no base backup with a manifest")
    base = candidates[-1]
    verify = subprocess.run(
        [str(paths["binaries"] / "pg_verifybackup.exe"), str(base)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=3600,
    )
    if verify.returncode != 0 or "successfully verified" not in verify.stdout:
        raise RestoreError(
            f"pg_verifybackup failed for {base.name}: {verify.stdout.strip()[-300:]} {verify.stderr.strip()[-300:]}"
        )
    return base


def archive_chain(paths: dict[str, Path], base: Path) -> dict[str, object]:
    label = (base / "backup_label").read_text(encoding="utf-8")
    start = re.search(r"\(file ([0-9A-F]{24})\)", label)
    if not start:
        raise RestoreError("backup_label without a START WAL LOCATION file")
    start_segment = start.group(1)
    history = sorted(paths["wal"].glob(f"{start_segment}.*.backup"))
    if not history:
        raise RestoreError(f"the archive copy lacks the backup history file for {start_segment}")
    stop = re.search(
        r"^STOP WAL LOCATION: ([0-9A-F]+/[0-9A-F]+) \(file ([0-9A-F]{24})\)$",
        history[-1].read_text(encoding="utf-8"),
        re.M,
    )
    if not stop:
        raise RestoreError("backup history file without a STOP WAL LOCATION")
    base_end_lsn, base_end_segment = stop.group(1), stop.group(2)
    complete = sorted(
        p.name
        for p in paths["wal"].iterdir()
        if p.is_file() and SEGMENT_NAME.match(p.name) and p.stat().st_size == SEGMENT_BYTES
    )
    after = [name for name in complete if segment_number(name) > segment_number(base_end_segment)]
    expected = [segment_name(base_end_segment[:8], segment_number(base_end_segment) + 1 + i) for i in range(len(after))]
    if after != expected:
        raise RestoreError(f"archived segments after the base backup are not contiguous: {after}")
    last = after[-1] if after else base_end_segment
    return {
        "start_segment": start_segment,
        "base_end_lsn": base_end_lsn,
        "base_end_segment": base_end_segment,
        "archived_after_base": after,
        "last_archived_segment": last,
        "last_segment_start_lsn": segment_lsn(segment_number(last)),
    }


def replay_evidence(
    chain: dict[str, object], logs: str, replay_lsn: str, redo_done_at: str | None
) -> dict[str, object]:
    """Prove that recovery ran through the whole archive: every complete archived segment after the base appears as
    restored from the archive in the server log, and the replay position lies in or beyond the last archived segment
    (when nothing was archived after the base, replay must reach the base backup's end). A segment beyond the
    contiguous chain that was nevertheless restored is reported so a stale or partial archive cannot pass silently."""
    restored = set(re.findall(r'restored log file "([0-9A-F]{24})" from archive', logs))
    after = [str(name) for name in chain["archived_after_base"]]
    last = str(chain["last_archived_segment"])
    beyond = segment_name(last[:8], segment_number(last) + 1)
    floor = str(chain["last_segment_start_lsn"]) if after else str(chain["base_end_lsn"])
    reached = lsn_value(replay_lsn) >= lsn_value(floor)
    return {
        "restored_from_archive": sorted(restored),
        "missing_archived_segments": [name for name in after if name not in restored],
        "segment_beyond_chain_restored": beyond in restored,
        "redo_done_at": redo_done_at,
        "replay_floor_lsn": floor,
        "replay_reached_last_archived_segment": bool(reached) and beyond not in restored,
    }


def prepare_data(paths: dict[str, Path], base: Path, data: Path, port: int, chain: dict[str, object]) -> str:
    if data.exists() and any(data.iterdir()):
        raise RestoreError(f"target data directory is not empty: {data}")
    shutil.copytree(base, data, dirs_exist_ok=True)
    for stale in ("postmaster.pid", "postmaster.opts"):
        (data / stale).unlink(missing_ok=True)
    (data / "recovery.signal").write_text("", encoding="utf-8")
    wal_dir = str(paths["wal"]).replace("/", "\\")
    restore_command = f'copy /Y "{wal_dir}\\%f" "%p"'
    lines = [
        "",
        "# restore_from_copy overrides",
        f"restore_command = {conf_quote(restore_command)}",
        f"port = {port}",
        "archive_mode = off",
    ]
    # No recovery target: recovery.signal without a target replays every archived segment the restore_command can
    # fetch and promotes at the end of the archive; replay_evidence() proves afterwards that the archive was consumed.
    with (data / "postgresql.auto.conf").open("a", encoding="utf-8") as conf:
        conf.write("\n".join(lines) + "\n")
    return restore_command


def service_environment(paths: dict[str, Path], port: int, report_dir: Path) -> tuple[dict[str, str], str]:
    """libpq environment for the restored server: a service file and password file derived inside report_dir from
    the copy's own admin credential file, for the requested port whatever it is. The copied pg_service.conf is never
    used because its passfile entries name the original volume; credential values are never printed."""
    lines = [
        entry
        for entry in (paths["credentials"] / "admin.pgpass").read_text(encoding="utf-8").splitlines()
        if entry.strip() and not entry.startswith("#")
    ]
    if len(lines) != 1 or lines[0].count(":") != 4:
        raise RestoreError("unexpected admin.pgpass shape in the copy")
    fields = lines[0].split(":")
    fields[0] = "127.0.0.1"
    fields[1] = str(port)
    derived = report_dir / "credentials"
    derived.mkdir(parents=True, exist_ok=True)
    pgpass = derived / "admin.pgpass"
    pgpass.write_text(":".join(fields) + "\n", encoding="utf-8")
    derived_service = derived / "pg_service.conf"
    derived_service.write_text(
        f"[restore_admin]\nhost=127.0.0.1\nport={port}\nuser={fields[3]}\ndbname=gtkb\nconnect_timeout=5\npassfile={pgpass}\n",
        encoding="utf-8",
    )
    return dict(os.environ, PGSERVICEFILE=str(derived_service), PGCONNECT_TIMEOUT="5"), "restore_admin"


def psql(paths: dict[str, Path], env: dict[str, str], service: str, sql_text: str) -> str:
    completed = subprocess.run(
        [
            str(paths["binaries"] / "psql.exe"),
            f"service={service} dbname=gtkb",
            "-X",
            "-v",
            "ON_ERROR_STOP=1",
            "-At",
            "-c",
            sql_text,
        ],
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=600,
    )
    if completed.returncode != 0:
        raise RestoreError(f"psql failed: {completed.stderr.strip()[-400:]}")
    return completed.stdout.strip()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument(
        "--copy",
        required=True,
        help="root of the GT-KB copy (for example D:\\GT-KB-LocalBackup)",
    )
    parser.add_argument("--data", required=True, help="empty data directory to restore into")
    parser.add_argument("--port", type=int, default=5432)
    parser.add_argument(
        "--report-dir",
        default=None,
        help="where restore-report.json and any derived service file go (default: beside --data)",
    )
    parser.add_argument(
        "--stop",
        action="store_true",
        help="stop the restored server after the report (rehearsal)",
    )
    args = parser.parse_args(argv)
    copy_root = Path(args.copy).resolve()
    data = Path(args.data).resolve()
    report_dir = Path(args.report_dir).resolve() if args.report_dir else data.parent
    report_dir.mkdir(parents=True, exist_ok=True)
    report: dict[str, object] = {
        "started_at": datetime.now(UTC).isoformat(),
        "copy": str(copy_root),
        "data": str(data),
        "port": args.port,
    }
    try:
        paths = resolve_copy(copy_root)
        base = newest_verified_base(paths)
        chain = archive_chain(paths, base)
        report.update(base_backup=str(base), **chain)
        report["restore_command"] = prepare_data(paths, base, data, args.port, chain)
        env, service = service_environment(paths, args.port, report_dir)
        server_log = report_dir / "restore-server.log"
        with open(os.devnull, "rb") as null_in, open(os.devnull, "ab") as null_out:
            started = subprocess.run(
                [
                    str(paths["binaries"] / "pg_ctl.exe"),
                    "start",
                    "-D",
                    str(data),
                    "-l",
                    str(server_log),
                    "-w",
                    "-t",
                    "900",
                    "-o",
                    f"-p {args.port}",
                ],
                stdin=null_in,
                stdout=null_out,
                stderr=null_out,
                timeout=1000,
            )
        if started.returncode != 0:
            raise RestoreError(f"the restored server did not start (restore failure); see {server_log}")
        deadline = time.monotonic() + 1800
        while psql(paths, env, service, "select pg_is_in_recovery()") != "f":
            if time.monotonic() > deadline:
                raise RestoreError("recovery did not finish within 1800 s")
            time.sleep(5)
        logs = server_log.read_text(encoding="utf-8", errors="replace")
        for extra in sorted((data / "log").glob("*.log")) + sorted((data.parent / "logs").glob("*.log")):
            logs += "\n" + extra.read_text(encoding="utf-8", errors="replace")
        redo_done = re.search(r"redo done at ([0-9A-F]+/[0-9A-F]+)", logs)
        replay_lsn = psql(paths, env, service, "select pg_last_wal_replay_lsn()")
        evidence = replay_evidence(chain, logs, replay_lsn, redo_done.group(1) if redo_done else None)
        report.update(
            evidence,
            replay_lsn=replay_lsn,
            timeline=int(
                psql(
                    paths,
                    env,
                    service,
                    "select timeline_id from pg_control_checkpoint()",
                )
            ),
            restore_command_effective=psql(paths, env, service, "select current_setting('restore_command')"),
            schema_comment=psql(
                paths,
                env,
                service,
                "select obj_description('public'::regnamespace, 'pg_namespace')",
            ),
        )
        names = psql(
            paths,
            env,
            service,
            "select table_name from information_schema.tables where table_schema='public' and table_type='BASE TABLE' order by 1",
        ).split()
        report["row_counts"] = {
            name: int(psql(paths, env, service, f'select count(*) from public."{name}"')) for name in names
        }
        report["total_rows"] = sum(report["row_counts"].values())
        if evidence["missing_archived_segments"]:
            raise RestoreError(f"archived segments not restored: {evidence['missing_archived_segments']}")
        if evidence["segment_beyond_chain_restored"]:
            raise RestoreError("the archive holds a segment beyond the contiguous complete chain; inspect the copy")
        if not evidence["replay_reached_last_archived_segment"]:
            raise RestoreError(
                f"replay ended at {replay_lsn} before the last archived segment {chain['last_archived_segment']}"
            )
        report["archive_recovery_complete"] = True
        report["finished_at"] = datetime.now(UTC).isoformat()
        (report_dir / "restore-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(json.dumps({k: v for k, v in report.items() if k != "row_counts"}))
        if args.stop:
            subprocess.run(
                [
                    str(paths["binaries"] / "pg_ctl.exe"),
                    "stop",
                    "-D",
                    str(data),
                    "-m",
                    "fast",
                    "-w",
                ],
                capture_output=True,
                timeout=300,
            )
            shutil.rmtree(report_dir / "credentials", ignore_errors=True)
        return 0
    except RestoreError as error:
        report["error"] = str(error)
        report["archive_recovery_complete"] = False
        (report_dir / "restore-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(json.dumps({"error": str(error)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
