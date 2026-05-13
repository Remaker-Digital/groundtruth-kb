"""Consistent SQLite snapshot support for ``gt db snapshot``.

Snapshots are written to a staging directory first, verified with
``PRAGMA integrity_check``, then atomically published into the output
directory with ``os.replace``.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved. Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import json
import os
import re
import sqlite3
import time
from contextlib import closing
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from groundtruth_kb.config import GTConfig

_SYNC_PATH_MARKERS = {
    "box",
    "dropbox",
    "google drive",
    "icloud",
    "icloud drive",
    "mega",
    "onedrive",
    "pcloud",
    "sync",
}
_SNAPSHOT_PREFIX = "groundtruth-"
_SNAPSHOT_SUFFIX = ".db"


class SnapshotError(Exception):
    """Raised for snapshot failures that should map to a CLI exit code."""

    def __init__(self, message: str, *, exit_code: int = 2) -> None:
        super().__init__(message)
        self.exit_code = exit_code


@dataclass(frozen=True)
class SnapshotPaths:
    """Resolved source, staging, and output paths for a snapshot run."""

    source_db: Path
    output_dir: Path
    staging_dir: Path


@dataclass(frozen=True)
class RetentionResult:
    """Snapshot retention result."""

    retained_count: int
    deleted_count: int
    deleted_paths: tuple[Path, ...] = ()


@dataclass(frozen=True)
class SnapshotResult:
    """Successful snapshot result."""

    final_path: Path
    manifest_path: Path
    method: str
    integrity_result: str
    warnings: tuple[str, ...]
    retained_count: int
    deleted_count: int

    def to_json_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation."""
        return {
            "status": "ok",
            "final_path": str(self.final_path),
            "manifest_path": str(self.manifest_path),
            "method": self.method,
            "integrity_result": self.integrity_result,
            "warnings": list(self.warnings),
            "retained_count": self.retained_count,
            "deleted_count": self.deleted_count,
        }


def create_snapshot(
    config: GTConfig,
    *,
    output_dir: Path | None = None,
    staging_dir: Path | None = None,
    retain_recent: int | None = None,
    retain_daily_days: int | None = None,
    fast: bool = False,
    include_chroma: bool | None = None,
) -> SnapshotResult:
    """Create a consistent, integrity-checked SQLite snapshot."""
    use_chroma = config.backup.include_chroma if include_chroma is None else include_chroma
    if use_chroma:
        raise SnapshotError("--include-chroma is not implemented in this slice; no snapshot was written.", exit_code=2)

    paths = resolve_snapshot_paths(config, output_dir=output_dir, staging_dir=staging_dir)
    retention_recent = config.backup.retain_recent if retain_recent is None else retain_recent
    retention_daily = config.backup.retain_daily_days if retain_daily_days is None else retain_daily_days
    if retention_recent < 0 or retention_daily < 0:
        raise SnapshotError("Retention values must be zero or greater.", exit_code=2)

    warnings = _validate_snapshot_paths(paths, sync_paths=config.backup.sync_paths)
    paths.output_dir.mkdir(parents=True, exist_ok=True)
    paths.staging_dir.mkdir(parents=True, exist_ok=True)

    stem = _snapshot_stem()
    staging_path = _unique_staging_path(paths.staging_dir, stem)
    final_path = _final_path(paths.output_dir, stem)
    staging_manifest_path = Path(str(staging_path) + ".manifest.json")
    final_manifest_path = final_path.with_suffix(".manifest.json")

    method = "backup" if fast else "vacuum"
    started = time.perf_counter()
    _create_snapshot_in_staging(paths.source_db, staging_path, fast=fast)
    duration = time.perf_counter() - started
    integrity_result = _integrity_check(staging_path)
    if integrity_result.lower() != "ok":
        quarantined = _quarantine_staged_snapshot(staging_path, paths.staging_dir)
        failure_manifest = Path(str(quarantined) + ".manifest.json")
        _write_json(
            failure_manifest,
            {
                "status": "integrity_failed",
                "source_db": str(paths.source_db),
                "quarantined_path": str(quarantined),
                "integrity_check_result": integrity_result,
                "created_at": _utc_now().isoformat(),
            },
        )
        raise SnapshotError(
            f"Snapshot integrity_check failed ({integrity_result}); staged file moved to {quarantined}.",
            exit_code=1,
        )

    manifest = _build_manifest(
        source_db=paths.source_db,
        final_path=final_path,
        staging_path=staging_path,
        method=method,
        duration=duration,
        integrity_result=integrity_result,
        warnings=warnings,
    )
    _write_json(staging_manifest_path, manifest)
    os.replace(staging_path, final_path)
    os.replace(staging_manifest_path, final_manifest_path)

    retention = rotate_snapshots(
        paths.output_dir,
        retain_recent=retention_recent,
        retain_daily_days=retention_daily,
        always_keep={final_path},
    )
    return SnapshotResult(
        final_path=final_path,
        manifest_path=final_manifest_path,
        method=method,
        integrity_result=integrity_result,
        warnings=tuple(warnings),
        retained_count=retention.retained_count,
        deleted_count=retention.deleted_count,
    )


def resolve_snapshot_paths(
    config: GTConfig,
    *,
    output_dir: Path | None = None,
    staging_dir: Path | None = None,
) -> SnapshotPaths:
    """Resolve snapshot source, output, and staging paths."""
    resolved_output = output_dir or config.backup.snapshot_output_dir or default_output_dir(config)
    resolved_staging = staging_dir or config.backup.snapshot_staging_dir or default_staging_dir()
    return SnapshotPaths(
        source_db=_absolute_path(config.db_path),
        output_dir=_absolute_path(resolved_output),
        staging_dir=_absolute_path(resolved_staging),
    )


def default_output_dir(config: GTConfig) -> Path:
    """Return the platform default snapshot output directory."""
    project_name = _safe_name(_absolute_path(config.project_root).name or "project")
    return _user_data_dir() / "gtkb-snapshots" / project_name


def default_staging_dir() -> Path:
    """Return the platform default non-synced staging directory."""
    return _user_data_dir() / "gtkb-snapshots" / "staging"


def rotate_snapshots(
    output_dir: Path,
    *,
    retain_recent: int,
    retain_daily_days: int,
    always_keep: set[Path] | None = None,
    now: datetime | None = None,
) -> RetentionResult:
    """Rotate snapshot files in ``output_dir`` according to retention rules."""
    records = _snapshot_records(output_dir)
    if not records:
        return RetentionResult(retained_count=0, deleted_count=0)

    keep: set[Path] = {path.resolve() for path in (always_keep or set())}
    sorted_records = sorted(records, key=lambda item: item["created_at"], reverse=True)
    keep.update(record["path"].resolve() for record in sorted_records[:retain_recent])

    cutoff = (now or _utc_now()).date() - timedelta(days=retain_daily_days)
    daily: dict[datetime.date, dict[str, Any]] = {}
    if retain_daily_days > 0:
        for record in sorted_records:
            created_date = record["created_at"].date()
            if created_date >= cutoff and created_date not in daily:
                daily[created_date] = record
        keep.update(record["path"].resolve() for record in daily.values())

    schema_versions: dict[int, dict[str, Any]] = {}
    for record in sorted_records:
        schema_version = record.get("schema_version")
        if isinstance(schema_version, int) and schema_version not in schema_versions:
            schema_versions[schema_version] = record
    keep.update(record["path"].resolve() for record in schema_versions.values())

    deleted: list[Path] = []
    for record in records:
        path = record["path"]
        if path.resolve() in keep:
            continue
        manifest = path.with_suffix(".manifest.json")
        path.unlink(missing_ok=True)
        manifest.unlink(missing_ok=True)
        deleted.append(path)

    return RetentionResult(
        retained_count=len(records) - len(deleted),
        deleted_count=len(deleted),
        deleted_paths=tuple(deleted),
    )


def _validate_snapshot_paths(paths: SnapshotPaths, *, sync_paths: tuple[Path, ...]) -> list[str]:
    if not paths.source_db.exists():
        raise SnapshotError(f"Source database does not exist: {paths.source_db}", exit_code=2)
    if _is_synced_path(paths.staging_dir, sync_paths=sync_paths):
        raise SnapshotError(f"Refusing to stage snapshots in a known synced path: {paths.staging_dir}", exit_code=2)
    if not _same_volume(paths.staging_dir, paths.output_dir):
        raise SnapshotError(
            "Snapshot staging and output directories must be on the same volume for atomic publish.",
            exit_code=2,
        )
    warnings: list[str] = []
    if _is_synced_path(paths.output_dir, sync_paths=sync_paths):
        warnings.append(f"Output directory appears to be sync-managed: {paths.output_dir}")
    return warnings


def _create_snapshot_in_staging(source_db: Path, staging_path: Path, *, fast: bool) -> None:
    staging_path.unlink(missing_ok=True)
    if fast:
        _write_fast_backup(source_db, staging_path)
    else:
        _write_vacuum_snapshot(source_db, staging_path)


def _write_vacuum_snapshot(source_db: Path, staging_path: Path) -> None:
    with closing(sqlite3.connect(source_db)) as source:
        source.execute("VACUUM INTO ?", (str(staging_path),))


def _write_fast_backup(source_db: Path, staging_path: Path) -> None:
    with closing(sqlite3.connect(source_db)) as source, closing(sqlite3.connect(staging_path)) as target:
        source.backup(target)


def _integrity_check(db_path: Path) -> str:
    with closing(sqlite3.connect(db_path)) as conn:
        row = conn.execute("PRAGMA integrity_check").fetchone()
    return str(row[0] if row else "missing integrity_check result")


def _quarantine_staged_snapshot(staging_path: Path, staging_dir: Path) -> Path:
    quarantine_dir = staging_dir / "quarantine"
    quarantine_dir.mkdir(parents=True, exist_ok=True)
    target = quarantine_dir / staging_path.name
    os.replace(staging_path, target)
    return target


def _build_manifest(
    *,
    source_db: Path,
    final_path: Path,
    staging_path: Path,
    method: str,
    duration: float,
    integrity_result: str,
    warnings: list[str],
) -> dict[str, Any]:
    source_stat = source_db.stat()
    staging_stat = staging_path.stat()
    with closing(sqlite3.connect(staging_path)) as conn:
        schema_version = int(conn.execute("PRAGMA schema_version").fetchone()[0])
        table_counts = _table_counts(conn)
    return {
        "created_at": _utc_now().isoformat(),
        "source_db": str(source_db),
        "final_path": str(final_path),
        "snapshot_size": staging_stat.st_size,
        "source_db_size": source_stat.st_size,
        "source_db_mtime": datetime.fromtimestamp(source_stat.st_mtime, UTC).isoformat(),
        "duration_seconds": round(duration, 6),
        "method": method,
        "integrity_check_result": integrity_result,
        "schema_version": schema_version,
        "table_counts": table_counts,
        "warnings": warnings,
    }


def _table_counts(conn: sqlite3.Connection) -> dict[str, int]:
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
    ).fetchall()
    counts: dict[str, int] = {}
    for (name,) in rows:
        counts[name] = int(conn.execute(f"SELECT COUNT(*) FROM {_quote_identifier(name)}").fetchone()[0])
    return counts


def _snapshot_records(output_dir: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    if not output_dir.exists():
        return records
    for path in output_dir.glob(f"{_SNAPSHOT_PREFIX}*{_SNAPSHOT_SUFFIX}"):
        created_at = _parse_snapshot_timestamp(path)
        if created_at is None:
            continue
        manifest = _read_manifest(path.with_suffix(".manifest.json"))
        records.append(
            {
                "path": path,
                "created_at": created_at,
                "schema_version": manifest.get("schema_version"),
            }
        )
    return records


def _read_manifest(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _parse_snapshot_timestamp(path: Path) -> datetime | None:
    stem = path.name.removeprefix(_SNAPSHOT_PREFIX).removesuffix(_SNAPSHOT_SUFFIX)
    try:
        return datetime.strptime(stem, "%Y%m%dT%H%M%SZ").replace(tzinfo=UTC)
    except ValueError:
        return None


def _final_path(output_dir: Path, stem: str) -> Path:
    return output_dir / f"{_SNAPSHOT_PREFIX}{stem}{_SNAPSHOT_SUFFIX}"


def _unique_staging_path(staging_dir: Path, stem: str) -> Path:
    return staging_dir / f".gtkb-snapshot-staging-{stem}.db.tmp"


def _snapshot_stem() -> str:
    return _utc_now().strftime("%Y%m%dT%H%M%SZ")


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _user_data_dir() -> Path:
    if os.name == "nt":
        base = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA")
        if base:
            return Path(base)
    if os.name == "posix" and os.environ.get("XDG_DATA_HOME"):
        return Path(os.environ["XDG_DATA_HOME"])
    if os.name == "posix" and os.uname().sysname == "Darwin":
        return Path.home() / "Library" / "Application Support"
    return Path.home() / ".local" / "share"


def _safe_name(value: str) -> str:
    safe = re.sub(r'[<>:"/\\|?*\x00-\x1f]+', "-", value).strip(" .-")
    return safe or "project"


def _is_synced_path(path: Path, *, sync_paths: tuple[Path, ...]) -> bool:
    resolved = _absolute_path(path)
    parts = {part.lower() for part in resolved.parts}
    if parts & _SYNC_PATH_MARKERS:
        return True
    lowered = str(resolved).lower()
    if "google drive" in lowered or "icloud drive" in lowered:
        return True
    return any(_is_relative_to(resolved, _absolute_path(sync_path)) for sync_path in sync_paths)


def _same_volume(left: Path, right: Path) -> bool:
    return _volume_id(left) == _volume_id(right)


def _volume_id(path: Path) -> str:
    absolute = _absolute_path(path)
    return (absolute.drive or absolute.anchor or str(absolute.anchor)).lower()


def _absolute_path(path: Path | str) -> Path:
    return Path(path).expanduser().resolve(strict=False)


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _quote_identifier(value: str) -> str:
    return '"' + value.replace('"', '""') + '"'
