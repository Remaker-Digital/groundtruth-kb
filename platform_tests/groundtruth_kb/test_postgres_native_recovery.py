"""Opt-in physical backup/PITR drill against an installed disposable native server."""

from __future__ import annotations

import os
import shutil
import socket
import subprocess
import time
import uuid
from pathlib import Path

import psycopg
import pytest
from psycopg import sql

pytestmark = [pytest.mark.integration, pytest.mark.timeout(120)]
ROOT = Path(__file__).resolve().parents[2]


def _run(command, env):
    result = subprocess.run(command, env=env, capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, f"{Path(command[0]).name} failed: {result.stderr}"
    return result.stdout.strip()


def test_native_physical_backup_and_wal_recovery(tmp_path, monkeypatch):
    configured = os.environ.get("GTKB_NATIVE_POSTGRES_HOME")
    if not configured:
        pytest.skip("set GTKB_NATIVE_POSTGRES_HOME to a disposable native installation outside GT-KB")
    home = Path(configured).resolve(strict=True)
    common = Path(_run(["git", "-C", str(ROOT), "rev-parse", "--path-format=absolute", "--git-common-dir"], os.environ))
    assert not home.is_relative_to(common.parent), "Recovery drills must not target the permanent installation"
    runtimes = list((home / "runtime").iterdir())
    assert len(runtimes) == 1
    binary = runtimes[0] / "bin"
    environment = {key: value for key, value in os.environ.items() if not key.startswith("PG")}
    environment.update(
        PGSERVICEFILE=str(home / "credentials" / "pg_service.conf"), PGSERVICE="gtkb_admin", PGDATABASE="postgres"
    )
    for key in tuple(os.environ):
        if key.startswith("PG"):
            monkeypatch.delenv(key)
    for key, value in environment.items():
        if key.startswith("PG"):
            monkeypatch.setenv(key, value)
    started_at = time.monotonic()
    schema = "recovery_" + uuid.uuid4().hex
    restore_point = schema + "_complete"
    restored = tmp_path / "restored"
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        restore_port = probe.getsockname()[1]
    running = False
    with psycopg.connect(service="gtkb_admin", autocommit=True) as source:
        assert Path(source.execute("SHOW data_directory").fetchone()[0]).resolve() == home / "data"
        assert source.execute("SHOW archive_mode").fetchone()[0] == "on"
        source.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(schema)))
        table = sql.Identifier(schema, "probe")
        try:
            source.execute(sql.SQL("CREATE TABLE {} (event INTEGER PRIMARY KEY)").format(table))
            source.execute(sql.SQL("INSERT INTO {} VALUES (1)").format(table))
            backup = tmp_path / "base"
            _run(
                [
                    str(binary / "pg_basebackup.exe"),
                    "-D",
                    str(backup),
                    "-Fp",
                    "-X",
                    "stream",
                    "--checkpoint=fast",
                    "--no-password",
                    "-d",
                    "service=gtkb_admin",
                ],
                environment,
            )
            _run([str(binary / "pg_verifybackup.exe"), str(backup)], environment)
            # This row can only appear in the restored server through archived
            # WAL: the verified physical base backup predates it.
            source.execute(sql.SQL("INSERT INTO {} VALUES (2)").format(table))
            source.execute("SELECT pg_create_restore_point(%s)", (restore_point,))
            wal = source.execute("SELECT pg_walfile_name(pg_current_wal_lsn())").fetchone()[0]
            source.execute("SELECT pg_switch_wal()")
            archive_deadline = time.monotonic() + 30
            while not (home / "wal" / wal).exists() and time.monotonic() < archive_deadline:
                time.sleep(0.2)
            assert (home / "wal" / wal).exists(), "WAL did not archive within 30 seconds"
            assert not list((home / "wal").glob("*.partial"))
            shutil.copytree(backup, restored)
            archive = str(home / "wal")
            assert not any(char in archive for char in "'\"%&|<>^\r\n")
            # COPY needs native separators, escaped for the configuration parser.
            archive = archive.replace("\\", "\\\\")
            with (restored / "postgresql.auto.conf").open("a", encoding="utf-8") as config:
                config.write(
                    f"\nport = {restore_port}\narchive_mode = off\n"
                    "log_directory = 'log'\n"
                    f'restore_command = \'copy /y "{archive}\\\\%f" "%p"\'\n'
                    f"recovery_target_name = '{restore_point}'\nrecovery_target_action = 'promote'\n"
                )
            (restored / "recovery.signal").touch()
            # Do not capture pipes that the Windows background server inherits.
            result = subprocess.run(
                [
                    str(binary / "pg_ctl.exe"),
                    "start",
                    "-D",
                    str(restored),
                    "-w",
                    "-t",
                    "30",
                    "-l",
                    str(tmp_path / "restore-startup.log"),
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                env=environment,
                timeout=40,
            )
            running = (restored / "postmaster.pid").exists()
            assert result.returncode == 0, "Restored server failed to reach the named recovery target"
            # The original pgpass has an exact production port. Use the same
            # protected credential for this one isolated connection in memory.
            password = (home / "credentials" / "admin.pgpass").read_text().strip().rsplit(":", 1)[1]
            with psycopg.connect(
                host="127.0.0.1",
                port=restore_port,
                user="postgres",
                password=password,
                dbname="postgres",
                autocommit=True,
            ) as recovery:
                assert Path(recovery.execute("SHOW data_directory").fetchone()[0]).resolve() == restored.resolve()
                deadline = time.monotonic() + 20
                while recovery.execute("SELECT pg_is_in_recovery()").fetchone()[0] and time.monotonic() < deadline:
                    time.sleep(0.1)
                assert not recovery.execute("SELECT pg_is_in_recovery()").fetchone()[0]
                assert recovery.execute(sql.SQL("SELECT event FROM {} ORDER BY event").format(table)).fetchall() == [
                    (1,),
                    (2,),
                ]
            assert source.execute(sql.SQL("SELECT count(*) FROM {}").format(table)).fetchone()[0] == 2
            assert time.monotonic() - started_at < 120
        finally:
            try:
                if running and (restored / "postmaster.pid").exists():
                    _run([str(binary / "pg_ctl.exe"), "stop", "-D", str(restored), "-m", "fast", "-w"], environment)
            finally:
                source.execute(sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(schema)))
