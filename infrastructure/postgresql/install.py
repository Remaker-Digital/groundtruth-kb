"""Install the pinned native PostgreSQL server beneath an explicit GT-KB root.

This is an operator bootstrap, not an agent database interface. It creates a new
cluster and refuses existing data. It never selects the canonical GT-KB backend.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import platform
import secrets
import shutil
import socket
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath

SOURCE = Path(__file__).resolve().parent
SERVER_DIRS = frozenset({"bin", "lib", "share", "include"})
SERVER_FILES = frozenset({"server_license.txt", "commandlinetools_3rd_party_licenses.txt"})


def extract_server(archive: Path, destination: Path, expected_digest: str) -> None:
    with archive.open("rb") as stream:
        if hashlib.file_digest(stream, "sha256").hexdigest() != expected_digest:
            raise ValueError("PostgreSQL archive checksum mismatch")
    if destination.exists():
        raise ValueError("Runtime destination already exists; refuse to overwrite it")
    with zipfile.ZipFile(archive) as package:
        selected = []
        for entry in package.infolist():
            path = PurePosixPath(entry.filename)
            if path.is_absolute() or ".." in path.parts or "\\" in entry.orig_filename or ":" in entry.orig_filename:
                raise ValueError("Unsafe path in PostgreSQL archive")
            if (entry.external_attr >> 16) & 0o170000 == 0o120000:
                raise ValueError("Symbolic links are not supported in PostgreSQL archive")
            if len(path.parts) < 2 or path.parts[0] != "pgsql":
                raise ValueError("Unexpected PostgreSQL archive layout")
            if path.parts[1] in SERVER_DIRS or str(path.relative_to("pgsql")) in SERVER_FILES:
                selected.append((entry, path.relative_to("pgsql")))
        names = {str(path) for entry, path in selected}
        if not {"bin/postgres.exe", "bin/pg_ctl.exe", "bin/initdb.exe", "bin/psql.exe"} <= names:
            raise ValueError("PostgreSQL archive is missing required server binaries")
        destination.mkdir(parents=True)
        for entry, path in selected:
            target = destination.joinpath(*path.parts)
            if entry.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                with package.open(entry) as src, target.open("xb") as dst:
                    shutil.copyfileobj(src, dst)


def run(command: list[str], *, env: dict[str, str] | None = None, sql: str | None = None, capture: bool = True) -> str:
    # A daemon can inherit pipe handles on Windows after pg_ctl exits. Waiting
    # for EOF on those pipes would hang installation despite a healthy server.
    output = subprocess.PIPE if capture else subprocess.DEVNULL
    result = subprocess.run(command, input=sql, text=True, stdout=output, stderr=output, env=env, check=False)
    if result.returncode:
        # SQL input and libpq output can contain credentials. Do not echo either.
        raise RuntimeError(f"{Path(command[0]).name} failed with exit code {result.returncode}")
    return (result.stdout or "").strip()


def protect(directory: Path) -> None:
    """Apply the workstation's filesystem boundary before writing credentials."""
    directory.mkdir(parents=True, exist_ok=False)
    # whoami CSV is locale-independent in its values; obtain the SID, not a name.
    sid = next(csv.reader([run(["whoami", "/user", "/fo", "csv", "/nh"])]))[1]
    run(
        [
            "icacls",
            str(directory),
            "/inheritance:r",
            "/grant:r",
            f"*{sid}:(OI)(CI)F",
            "*S-1-5-18:(OI)(CI)F",
            "*S-1-5-32-544:(OI)(CI)F",
        ]
    )


def install(root: Path, archive: Path, port: int) -> dict[str, object]:
    if os.name != "nt" or platform.machine().lower() not in {"amd64", "x86_64"}:
        raise ValueError("This PostgreSQL distribution requires Windows x64")
    root = root.resolve(strict=True)
    if not (root / "groundtruth.toml").is_file():
        raise ValueError("Root must contain the GT-KB groundtruth.toml")
    if not 1024 <= port <= 65535:
        raise ValueError("Port must be between 1024 and 65535")
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", port))
    release = json.loads((SOURCE / "release.json").read_text(encoding="utf-8"))
    home = (root / "infrastructure" / "postgresql").resolve()
    if not home.is_relative_to(root):
        raise ValueError("PostgreSQL installation resolves outside the selected GT-KB root")
    archive_paths = [
        str(Path(sys.executable).resolve()),
        str(home / "runtime" / release["build"] / "archive_wal.py"),
        str(home / "wal"),
    ]
    if any(any(char in path for char in "'\"%&|<>^\r\n") for path in archive_paths):
        raise ValueError("Installation paths contain unsupported shell metacharacters")
    home.mkdir(parents=True, exist_ok=True)
    data, credentials = home / "data", home / "credentials"
    if data.exists() or credentials.exists():
        raise ValueError("Cluster or credentials already exist; installation never reinitializes them")
    runtime = home / "runtime" / release["build"]
    extract_server(archive, runtime, release["sha256"])
    binary = runtime / "bin"
    observed = run([str(binary / "postgres.exe"), "--version"])
    if observed != f"postgres (PostgreSQL) {release['version']}":
        raise ValueError("Installed PostgreSQL reports an unexpected version")
    protect(credentials)
    protect(data)
    for name in ("logs", "wal", "backups"):
        protect(home / name)
    # An installed copy stays executable after the source checkout closes.
    shutil.copyfile(SOURCE / "archive_wal.py", runtime / "archive_wal.py")
    admin_password, service_password = secrets.token_hex(32), secrets.token_hex(32)
    initial_password = credentials / "initdb-password"
    initial_password.write_text(admin_password + "\n", encoding="utf-8")
    try:
        run(
            [
                str(binary / "initdb.exe"),
                "-D",
                str(data),
                "--username=postgres",
                "--encoding=UTF8",
                "--locale=C",
                "--auth=scram-sha-256",
                "--data-checksums",
                f"--pwfile={initial_password}",
            ]
        )
    finally:
        initial_password.unlink(missing_ok=True)
    admin_pass = credentials / "admin.pgpass"
    authority_pass = credentials / "authority.pgpass"
    admin_pass.write_text(f"127.0.0.1:{port}:*:postgres:{admin_password}\n", encoding="utf-8")
    authority_pass.write_text(f"127.0.0.1:{port}:gtkb:gtkb_service:{service_password}\n", encoding="utf-8")
    (credentials / "pg_service.conf").write_text(
        "[gtkb_admin]\nhost=127.0.0.1\n"
        f"port={port}\nuser=postgres\npassfile={admin_pass.as_posix()}\nconnect_timeout=5\n"
        "[gtkb_authority]\nhost=127.0.0.1\n"
        f"port={port}\ndbname=gtkb\nuser=gtkb_service\npassfile={authority_pass.as_posix()}\nconnect_timeout=5\n",
        encoding="utf-8",
    )
    # PostgreSQL invokes archive_command through the Windows shell. Reject shell
    # metacharacters in operator-selected paths before composing that one command.
    command = f'"{archive_paths[0]}" "{archive_paths[1]}" "%p" "{archive_paths[2]}/%f"'
    command = command.replace("\\", "/")
    with (data / "postgresql.conf").open("a", encoding="utf-8") as config:
        config.write(
            "\n# GT-KB native workstation installation\n"
            f"listen_addresses = '127.0.0.1'\nport = {port}\n"
            "password_encryption = 'scram-sha-256'\n"
            "wal_level = replica\narchive_mode = on\narchive_timeout = 300\n"
            f"archive_command = '{command}'\n"
            "logging_collector = on\nlog_destination = 'stderr'\n"
            "log_directory = '../logs'\nlog_filename = 'postgresql-%a.log'\n"
            "log_rotation_age = 1d\nlog_rotation_size = 0\nlog_truncate_on_rotation = on\n"
            "log_statement = 'none'\nlog_min_error_statement = panic\n"
        )
    environment = os.environ.copy()
    for key in tuple(environment):
        if key.startswith("PG"):
            environment.pop(key)
    environment.update(
        PGSERVICEFILE=str(credentials / "pg_service.conf"), PGSERVICE="gtkb_admin", PGDATABASE="postgres"
    )
    started = False
    try:
        run(
            [str(binary / "pg_ctl.exe"), "start", "-D", str(data), "-l", str(home / "logs" / "startup.log"), "-w"],
            capture=False,
        )
        started = True
        run(
            [str(binary / "psql.exe"), "-X", "-v", "ON_ERROR_STOP=1"],
            env=environment,
            sql=f"CREATE ROLE gtkb_service LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION PASSWORD '{service_password}';\n"
            "CREATE DATABASE gtkb OWNER gtkb_service TEMPLATE template0 ENCODING 'UTF8';\n"
            "REVOKE ALL ON DATABASE gtkb FROM PUBLIC;\n",
        )
    except Exception:
        if started:
            run([str(binary / "pg_ctl.exe"), "stop", "-D", str(data), "-m", "fast", "-w"])
        raise
    return {"root": str(home), "version": observed, "port": port, "running": True, "authority_selected": False}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--archive", type=Path, help="Use a previously downloaded, checksum-verified archive")
    parser.add_argument("--port", type=int, default=5432)
    args = parser.parse_args()
    if args.archive:
        result = install(args.root, args.archive, args.port)
    else:
        release = json.loads((SOURCE / "release.json").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory(prefix="gtkb-postgresql-download-") as temporary:
            archive = Path(temporary) / "postgresql.zip"
            with urllib.request.urlopen(release["url"], timeout=60) as response, archive.open("xb") as output:
                shutil.copyfileobj(response, output)
            result = install(args.root, archive, args.port)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
