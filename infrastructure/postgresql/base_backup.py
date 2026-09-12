#!/usr/bin/env python3
"""Unattended base backup and retention for the GT-KB PostgreSQL installation.

Operator tool, not an agent interface. It takes one physical base backup of the local server with
streamed WAL and a SHA-256 manifest, verifies it with pg_verifybackup, records the result, and applies
retention: the newest KEEP verified base backups stay in backups/, and archived WAL segments older than
the oldest retained base backup's start segment are pruned. WAL is never pruned by age alone, and a WAL
segment is never removed while a retained base backup could need it. Recovery material is only protected
against loss of this disk once the staging and archive directories have been copied to another volume;
this tool does not perform that copy.

    python infrastructure/postgresql/base_backup.py --root E:\\GT-KB [--keep 7] [--dry-run]

The server is reached through the protected libpq service file under credentials/ (service gtkb_admin);
no password is read or written by this tool.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

RELEASE = "release.json"
SEGMENT = re.compile(r"^[0-9A-F]{24}$")
BACKUP_HISTORY = re.compile(r"^([0-9A-F]{24})\.[0-9A-F]{8}\.backup$")


class BackupError(RuntimeError):
    pass


def resolve(root: Path) -> dict[str, Path]:
    installation = root / "infrastructure" / "postgresql"
    release = json.loads((installation / RELEASE).read_text(encoding="utf-8"))
    binaries = installation / "runtime" / release["build"] / "bin"
    for name in ("pg_basebackup.exe", "pg_verifybackup.exe"):
        if not (binaries / name).is_file():
            raise BackupError(f"PostgreSQL runtime is missing {name}")
    for directory in ("backups", "wal", "credentials"):
        if not (installation / directory).is_dir():
            raise BackupError(f"installation directory is missing: {directory}")
    return {
        "installation": installation,
        "binaries": binaries,
        "backups": installation / "backups",
        "wal": installation / "wal",
        "service_file": installation / "credentials" / "pg_service.conf",
    }


def take_backup(paths: dict[str, Path], stamp: str) -> Path:
    target = paths["backups"] / f"base-{stamp}"
    if target.exists():
        raise BackupError(f"backup directory already exists: {target}")
    env = dict(os.environ, PGSERVICEFILE=str(paths["service_file"]), PGCONNECT_TIMEOUT="10")
    env.pop("PGDATABASE", None)
    command = [
        str(paths["binaries"] / "pg_basebackup.exe"),
        "--dbname",
        "service=gtkb_admin",
        "-D",
        str(target),
        "-Fp",
        "-Xs",
        "-c",
        "fast",
        "--manifest-checksums=SHA256",
        "--no-password",
    ]
    completed = subprocess.run(
        command, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=3600
    )
    if completed.returncode != 0:
        raise BackupError(f"pg_basebackup failed: {completed.stderr.strip()[-800:]}")
    verify = subprocess.run(
        [str(paths["binaries"] / "pg_verifybackup.exe"), str(target)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=3600,
    )
    if verify.returncode != 0 or "successfully verified" not in verify.stdout:
        raise BackupError(f"pg_verifybackup failed: {verify.stdout.strip()[-400:]} {verify.stderr.strip()[-400:]}")
    return target


def start_segment(backup: Path) -> str:
    """The WAL segment a base backup starts in, from its backup_label; every later segment is needed for recovery."""
    label = (backup / "backup_label").read_text(encoding="utf-8")
    match = re.search(r"^START WAL LOCATION: .* \(file ([0-9A-F]{24})\)$", label, re.MULTILINE)
    if not match:
        raise BackupError(f"backup_label without START WAL LOCATION: {backup}")
    return match.group(1)


def verified_backups(paths: dict[str, Path], binaries: Path) -> list[Path]:
    result = []
    for candidate in sorted(paths["backups"].glob("base-*")):
        if not (candidate / "backup_manifest").is_file() or not (candidate / "backup_label").is_file():
            continue
        verify = subprocess.run(
            [str(binaries / "pg_verifybackup.exe"), str(candidate)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=3600,
        )
        if verify.returncode == 0 and "successfully verified" in verify.stdout:
            result.append(candidate)
    return result


def retention_plan(backups: list[Path], wal_entries: list[str], keep: int) -> dict[str, list[str]]:
    """Pure decision: which base backups and WAL files retention removes.

    ``backups`` are verified base backups ordered oldest to newest; ``wal_entries`` are file names in the
    archive. The newest ``keep`` backups stay. A WAL segment or backup-history file is pruned only when its
    segment sorts before the start segment of the oldest retained backup; nothing is pruned when no backup
    is retained.
    """
    if keep < 1:
        raise BackupError("keep must be at least 1")
    retained = backups[-keep:] if backups else []
    removed_backups = [str(path) for path in backups[: max(0, len(backups) - keep)]]
    if not retained:
        return {"retained_backups": [], "removed_backups": removed_backups, "removed_wal": []}
    floor = start_segment(retained[0])
    removed_wal = []
    for name in sorted(wal_entries):
        history = BACKUP_HISTORY.match(name)
        segment = history.group(1) if history else (name if SEGMENT.match(name) else None)
        if segment is not None and segment < floor:
            removed_wal.append(name)
    return {
        "retained_backups": [str(path) for path in retained],
        "removed_backups": removed_backups,
        "removed_wal": removed_wal,
    }


def apply_plan(paths: dict[str, Path], plan: dict[str, list[str]]) -> None:
    import shutil

    for backup in plan["removed_backups"]:
        target = Path(backup)
        if target.parent != paths["backups"] or not target.name.startswith("base-"):
            raise BackupError(f"refusing to remove a path outside backups/: {target}")
        shutil.rmtree(target)
    for name in plan["removed_wal"]:
        target = paths["wal"] / name
        if target.parent != paths["wal"]:
            raise BackupError(f"refusing to remove a path outside wal/: {target}")
        target.unlink()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--root", required=True, help="GT-KB root that contains infrastructure/postgresql")
    parser.add_argument("--keep", type=int, default=7, help="number of verified base backups to retain (default 7)")
    parser.add_argument(
        "--dry-run", action="store_true", help="take no backup and remove nothing; print the retention plan"
    )
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    try:
        paths = resolve(root)
        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        taken = None if args.dry_run else take_backup(paths, stamp)
        backups = verified_backups(paths, paths["binaries"])
        wal_entries = [entry.name for entry in paths["wal"].iterdir() if entry.is_file()]
        plan = retention_plan(backups, wal_entries, args.keep)
        if not args.dry_run:
            apply_plan(paths, plan)
        record = {
            "taken_at": stamp,
            "root": str(root),
            "backup": None if taken is None else str(taken),
            "verified": taken is not None,
            "keep": args.keep,
            "dry_run": args.dry_run,
            **plan,
        }
        if not args.dry_run:
            (paths["backups"] / f"base-{stamp}.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
        print(json.dumps(record))
        return 0
    except BackupError as error:
        print(json.dumps({"error": str(error)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
