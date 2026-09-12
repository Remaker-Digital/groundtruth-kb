"""End-to-end regression for infrastructure/postgresql/restore_from_copy.py (observer findings 1 and 2, 2026-09-11).

A disposable PostgreSQL cluster archives its WAL into a copy-shaped directory. Rows committed AFTER the first record
of the last archived segment must survive the restore (finding 1: a recovery target at that first record discarded
them), and a restore on the copy's ORIGINAL port must authenticate with credentials derived from the copy while the
copied service file names an unreachable original volume (finding 2).

Opt-in like the kernel integration tests: set ``GTKB_RUN_POSTGRES_INTEGRATION=1`` and ``GTKB_TEST_POSTGRES_BIN`` to
the ``bin`` directory of a PostgreSQL 18 build (a disposable one, never the production service's data). Missing
prerequisites are failures, never skips, for the approved invocation. Credential values are generated per run and
never printed.
"""

from __future__ import annotations

import importlib.util
import json
import os
import secrets
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SEGMENT_BYTES = 16 * 1024 * 1024


def _load_tool():
    spec = importlib.util.spec_from_file_location(
        "restore_from_copy_under_test", ROOT / "infrastructure" / "postgresql" / "restore_from_copy.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules["restore_from_copy_under_test"] = module
    spec.loader.exec_module(module)
    return module


def _required_binaries() -> Path:
    if os.environ.get("GTKB_RUN_POSTGRES_INTEGRATION") != "1":
        pytest.fail("set GTKB_RUN_POSTGRES_INTEGRATION=1 for the reviewed disposable-PostgreSQL operation")
    value = os.environ.get("GTKB_TEST_POSTGRES_BIN")
    if not value:
        pytest.fail("GTKB_TEST_POSTGRES_BIN must name the bin directory of a disposable PostgreSQL 18 build")
    binaries = Path(value)
    for name in ("initdb.exe", "pg_ctl.exe", "pg_basebackup.exe", "psql.exe", "pg_verifybackup.exe", "pg_isready.exe"):
        if not (binaries / name).is_file():
            pytest.fail(f"{name} is missing under GTKB_TEST_POSTGRES_BIN={binaries}")
    return binaries


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _run(argv: list[str | Path], env: dict[str, str], timeout: int = 300) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        [str(a) for a in argv],
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )
    if completed.returncode != 0:
        raise AssertionError(f"{argv[0]} failed ({completed.returncode}): {completed.stderr.strip()[-800:]}")
    return completed


def _wait_for(predicate, timeout: float, what: str) -> None:
    deadline = time.monotonic() + timeout
    while not predicate():
        if time.monotonic() > deadline:
            pytest.fail(f"timed out waiting for {what}")
        time.sleep(0.5)


def test_restore_replays_rows_committed_late_in_the_last_archived_segment_on_the_original_port(tmp_path: Path) -> None:
    binaries = _required_binaries()
    tool = _load_tool()
    port = _free_port()
    password = secrets.token_urlsafe(18)
    pwfile = tmp_path / "pw.txt"
    pwfile.write_text(password + "\n", encoding="utf-8")
    pgpass = tmp_path / "client.pgpass"
    pgpass.write_text(f"127.0.0.1:{port}:*:gtkb_admin:{password}\n", encoding="utf-8")
    client_env = dict(os.environ, PGPASSFILE=str(pgpass), PGCONNECT_TIMEOUT="5")
    client_env.pop("PGSERVICEFILE", None)
    client_env.pop("PGSERVICE", None)

    copy = tmp_path / "copy"
    installation = copy / "infrastructure" / "postgresql"
    for name in ("backups", "wal", "credentials"):
        (installation / name).mkdir(parents=True)
    (installation / "release.json").write_text(json.dumps({"build": "18.6-3"}), encoding="utf-8")
    (installation / "runtime").mkdir()
    junction = installation / "runtime" / "18.6-3"
    cluster = tmp_path / "cluster"
    restored = tmp_path / "restored" / "data"
    restored.parent.mkdir()
    report_dir = tmp_path / "report"

    def psql(database: str, sql_text: str) -> str:
        return _run(
            [
                binaries / "psql.exe",
                "-h",
                "127.0.0.1",
                "-p",
                str(port),
                "-U",
                "gtkb_admin",
                "-d",
                database,
                "-X",
                "-At",
                "-v",
                "ON_ERROR_STOP=1",
                "-c",
                sql_text,
            ],
            client_env,
            timeout=120,
        ).stdout.strip()

    def stop(data: Path) -> None:
        subprocess.run(
            [str(binaries / "pg_ctl.exe"), "stop", "-D", str(data), "-m", "fast", "-w"],
            capture_output=True,
            timeout=120,
        )

    junction_made = False
    try:
        # the copy's runtime is a directory junction to the disposable build (binaries, lib and share travel together)
        _run(["cmd", "/c", "mklink", "/J", str(junction), str(binaries.parent)], client_env, timeout=60)
        junction_made = True
        _run(
            [
                binaries / "initdb.exe",
                "-D",
                cluster,
                "-U",
                "gtkb_admin",
                f"--pwfile={pwfile}",
                "-A",
                "scram-sha-256",
                "-E",
                "UTF8",
                "--no-instructions",
            ],
            client_env,
            timeout=300,
        )
        archive_dir = str(installation / "wal").replace("/", "\\")
        with (cluster / "postgresql.conf").open("a", encoding="utf-8") as conf:
            conf.write(
                "\n# disposable end-to-end restore regression\n"
                f"port = {port}\nlisten_addresses = '127.0.0.1'\nwal_level = replica\nmax_wal_senders = 3\n"
                f"archive_mode = on\narchive_command = {tool.conf_quote(f'copy "%p" "{archive_dir}\\%f"')}\n"
            )
        with open(os.devnull, "rb") as null_in, open(os.devnull, "ab") as null_out:
            started = subprocess.run(
                [
                    str(binaries / "pg_ctl.exe"),
                    "start",
                    "-D",
                    str(cluster),
                    "-l",
                    str(tmp_path / "cluster.log"),
                    "-w",
                    "-t",
                    "120",
                    "-o",
                    f"-p {port}",
                ],
                stdin=null_in,
                stdout=null_out,
                stderr=null_out,
                timeout=180,
            )
        assert started.returncode == 0, (tmp_path / "cluster.log").read_text(encoding="utf-8", errors="replace")[-1500:]
        psql("postgres", "create database gtkb")
        psql("gtkb", "create table public.notes (id int primary key, body text not null)")
        for i in range(1, 11):
            psql("gtkb", f"insert into public.notes values ({i}, 'before the base backup')")

        base = installation / "backups" / "base-20260911T120000Z"
        _run(
            [
                binaries / "pg_basebackup.exe",
                "-h",
                "127.0.0.1",
                "-p",
                str(port),
                "-U",
                "gtkb_admin",
                "-D",
                base,
                "-Fp",
                "-Xs",
                "-c",
                "fast",
                "--manifest-checksums=SHA256",
                "--no-password",
            ],
            client_env,
            timeout=600,
        )
        assert (base / "backup_manifest").is_file() and (base / "backup_label").is_file()

        for i in range(11, 21):
            psql("gtkb", f"insert into public.notes values ({i}, 'first archived segment after the base')")
        psql("postgres", "select pg_switch_wal()")
        # commits well past the first record of what becomes the LAST archived segment
        for i in range(21, 41):
            psql("gtkb", f"insert into public.notes values ({i}, 'late in the last archived segment')")
        psql("postgres", "select pg_switch_wal()")

        def archived_complete_segments() -> list[str]:
            return sorted(
                p.name
                for p in (installation / "wal").iterdir()
                if tool.SEGMENT_NAME.match(p.name) and p.stat().st_size == SEGMENT_BYTES
            )

        _wait_for(
            lambda: (
                len(archived_complete_segments()) >= 3
                and any(p.suffix == ".backup" for p in (installation / "wal").iterdir())
            ),
            120,
            "the archiver to copy the base history file and three complete segments",
        )
        stop(cluster)

        (installation / "credentials" / "admin.pgpass").write_text(
            f"127.0.0.1:{port}:*:gtkb_admin:{password}\n", encoding="utf-8"
        )
        (installation / "credentials" / "pg_service.conf").write_text(
            f"[gtkb_admin]\nhost=127.0.0.1\nport={port}\nuser=gtkb_admin\ndbname=gtkb\n"
            "passfile=E:/original-volume-that-is-not-here/infrastructure/postgresql/credentials/admin.pgpass\n",
            encoding="utf-8",
        )
        for key in ("PGPASSFILE", "PGSERVICEFILE", "PGSERVICE", "PGPASSWORD"):
            os.environ.pop(key, None)
        # same port as the original cluster: the copied service file must NOT be used (its passfile is unreachable)
        code = tool.main(
            [
                "--copy",
                str(copy),
                "--data",
                str(restored),
                "--port",
                str(port),
                "--report-dir",
                str(report_dir),
                "--stop",
            ]
        )
        report = json.loads((report_dir / "restore-report.json").read_text(encoding="utf-8"))
        assert code == 0, report.get("error")
        assert report["archive_recovery_complete"] is True
        chain = report["archived_after_base"]
        assert len(chain) >= 2 and report["missing_archived_segments"] == []
        assert set(chain) <= set(report["restored_from_archive"])
        assert report["replay_reached_last_archived_segment"] is True
        # finding 1: rows committed after the first record of the last archived segment are present
        assert report["row_counts"]["notes"] == 40
        assert "recovery_target" not in (restored / "postgresql.auto.conf").read_text(encoding="utf-8")
        assert not (report_dir / "credentials").exists()  # --stop removed the derived credentials
    finally:
        stop(restored)
        stop(cluster)
        if junction_made:
            try:
                junction.rmdir()  # removes the junction only; the disposable build stays
            except OSError:
                pass
