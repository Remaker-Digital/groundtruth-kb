"""Current SoT declarations, scope resolution and atomic declaration updates.

The canonical TOML supplies current declarations. Readers inspect that source;
mutations validate current formal sources and actual artifact effects before
atomically replacing it. Native bridge services own claims and delivery.
"""

from __future__ import annotations

import fnmatch
import hashlib
import json
import os
import random
import sqlite3
import stat
import subprocess
import sys
import time
import uuid
from collections.abc import Callable, Iterator, Mapping, Sequence
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Literal

from groundtruth_kb.config import GTConfig
from groundtruth_kb.project.operational_control_config import (
    REGISTRY_CONTROL_UNITS,
    OperationalControlConfigError,
    ResolvedOperationalControl,
    control_value,
    load_operational_control_catalog,
    resolve_operational_controls,
)
from groundtruth_kb.project.sot_registry import (
    SoTArtifact,
    _load_toml_bytes,
    _parse_record,
)

CoverageClass = Literal[
    "registered_member",
    "registered_structural_ancestor",
    "opaque_container",
    "virtual_declaration",
    "unregistered",
    "invalid_unknown",
]

APPROVED_VIRTUAL_SCHEMES = frozenset({"membase", "windows-scheduled-task"})


class RegistryControlPlaneError(RuntimeError):
    """Base error for coherent registry operations."""


class RegistryFileLockAcquisitionTimeout(RegistryControlPlaneError):
    """Typed caller-retryable transient for control-plane lock acquisition timeout.

    WI-5869: replaces the bare ``TimeoutError`` raised when the
    ``_RegistryFileLock`` acquisition deadline is exhausted. The typed subclass
    lets callers classify and retry the transient rather than treating it as a
    hard failure.
    """


class RegistryRecoveryRequired(RegistryControlPlaneError):
    """Raised when deterministic recovery cannot choose a safe state."""


class RegistryCoverageError(RegistryControlPlaneError):
    """Raised for unsafe, ambiguous, or incomplete registry coverage."""


class RegistryGenerationConflict(RegistryControlPlaneError):
    """Raised when an amend snapshot is stale at the commit linearization point."""


@dataclass(frozen=True)
class RegistryPaths:
    project_root: Path
    registry_path: Path

    @classmethod
    def resolve(
        cls,
        *,
        project_root: Path | None = None,
        registry_path: Path | None = None,
    ) -> RegistryPaths:
        if project_root is None:
            if registry_path is not None:
                candidate = registry_path.resolve()
                project_root = candidate.parents[2] if candidate.parent.name == "registry" else candidate.parent
            else:
                raise RegistryControlPlaneError(
                    "project_root or registry_path is required; the installed package location is not project authority"
                )
        root = Path(project_root).resolve()
        canonical = Path(registry_path or root / "config" / "registry" / "sot-artifacts.toml").resolve()
        return cls(root, canonical)


def _registry_controls(project_root: Path) -> Mapping[str, ResolvedOperationalControl]:
    """Retain one validated control snapshot for the entire registry write."""
    try:
        controls = resolve_operational_controls(
            load_operational_control_catalog(project_root), list(REGISTRY_CONTROL_UNITS)
        )
        for key, unit in REGISTRY_CONTROL_UNITS.items():
            control_value(controls, key, unit=unit)
        return controls
    except OperationalControlConfigError as exc:
        raise RegistryControlPlaneError(f"operational_controls: {exc}") from exc


class _RegistryFileLock:
    def __init__(self, path: Path, *, controls: Mapping[str, ResolvedOperationalControl]) -> None:
        self.path = path
        if len({value.catalog_sha256 for value in controls.values()}) != 1:
            raise RegistryControlPlaneError("Registry lock requires one control snapshot")
        self.catalog_sha256 = next(iter(controls.values())).catalog_sha256
        self.timeout = float(control_value(controls, "registry.lock.acquire_seconds", unit="seconds"))
        self.initial_backoff = float(control_value(controls, "registry.lock.initial_backoff_seconds", unit="seconds"))
        self.max_backoff = float(control_value(controls, "registry.lock.max_backoff_seconds", unit="seconds"))
        self.backoff_factor = float(control_value(controls, "registry.lock.backoff_factor", unit="ratio"))
        self.jitter_min = float(control_value(controls, "registry.lock.jitter_min_ratio", unit="ratio"))
        self.jitter_max = float(control_value(controls, "registry.lock.jitter_max_ratio", unit="ratio"))
        self._handle: Any = None

    def __enter__(self) -> _RegistryFileLock:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._handle = self.path.open("a+b")
        # Byte-range locks may extend beyond EOF. Seeding a byte before
        # acquisition races another holder and is itself denied on Windows.
        deadline = time.monotonic() + self.timeout
        backoff = self.initial_backoff
        attempt = 0
        while True:
            try:
                self._handle.seek(0)
                if sys.platform == "win32":
                    import msvcrt

                    msvcrt.locking(self._handle.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl

                    fcntl.flock(self._handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                return self
            except OSError:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    self._handle.close()
                    raise RegistryFileLockAcquisitionTimeout(f"timed out acquiring registry lock {self.path}") from None
                attempt += 1
                # Bounded exponential backoff with jitter so contending waiters
                # stagger instead of hammering the lock at a fixed rate
                # (WI-5869). The sleep never exceeds the remaining budget.
                backoff = min(backoff * self.backoff_factor, self.max_backoff)
                jitter = backoff * random.uniform(self.jitter_min, self.jitter_max)
                sleep_seconds = min(jitter, max(0.0, remaining))
                if sleep_seconds > 0:
                    time.sleep(sleep_seconds)

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> None:
        if self._handle is None:
            return
        try:
            self._handle.seek(0)
            if sys.platform == "win32":
                import msvcrt

                msvcrt.locking(self._handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl

                fcntl.flock(self._handle.fileno(), fcntl.LOCK_UN)
        finally:
            self._handle.close()


def _sha256_bytes(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _toml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=True)


_SERIALIZED_FIELDS = (
    "id",
    "domain",
    "lifecycle",
    "storage_path",
    "coverage_mode",
    "authority_spec_id",
    "mutation_api",
    "versioning_policy",
    "backup_policy",
    "restore_action",
    "health_check_function",
    "owner_role",
    "depends_on",
    "forbidden_substitutes",
    "notes",
)


def serialize_registry(records: Sequence[SoTArtifact]) -> bytes:
    """Serialize one deterministic, human-readable registry generation."""

    lines = [
        "# Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.",
        "#",
        "# Platform SoT Artifact Registry - canonical human-edit declaration.",
        "# Mutate only through `gt registry register` or `gt registry amend`.",
        "# Lifecycle and locator reconciliation use `gt registry transition`.",
        "",
    ]
    for record in records:
        if record.coverage_mode is None:
            raise RegistryCoverageError(f"record {record.id!r} has no explicit coverage_mode")
        lines.append("[[artifacts]]")
        payload = asdict(record)
        for field_name in _SERIALIZED_FIELDS:
            value = payload[field_name]
            if field_name in {"depends_on", "forbidden_substitutes"}:
                encoded = ", ".join(_toml_string(str(item)) for item in value)
                lines.append(f"{field_name} = [{encoded}]")
            else:
                lines.append(f"{field_name} = {_toml_string('' if value is None else str(value))}")
        lines.append("")
    return ("\n".join(lines).rstrip() + "\n").encode("utf-8")


def _record_payload(record: SoTArtifact) -> dict[str, Any]:
    payload = asdict(record)
    payload["depends_on"] = list(record.depends_on)
    payload["forbidden_substitutes"] = list(record.forbidden_substitutes)
    return payload


def _normalized_locator(record: SoTArtifact) -> str:
    locator = record.storage_path.replace("\\", "/")
    if not locator or locator != record.storage_path:
        raise RegistryCoverageError(f"record {record.id!r}: locator must be normalized with forward slashes")
    if record.coverage_mode == "virtual":
        scheme, separator, suffix = locator.partition(":")
        if separator != ":" or scheme not in APPROVED_VIRTUAL_SCHEMES or not suffix:
            raise RegistryCoverageError(f"record {record.id!r}: unsupported virtual locator {locator!r}")
        return locator
    if ":" in locator or locator.startswith("/") or locator.startswith("//"):
        raise RegistryCoverageError(f"record {record.id!r}: locator must be project-relative")
    parts = (locator[:-1] if locator.endswith("/") else locator).split("/")
    if not parts or any(part in {"", ".", ".."} for part in parts):
        raise RegistryCoverageError(f"record {record.id!r}: unsafe project-relative locator {locator!r}")
    has_magic = any(char in locator for char in "*?[")
    if record.coverage_mode == "glob" and not has_magic:
        raise RegistryCoverageError(f"record {record.id!r}: glob coverage requires a glob locator")
    if record.coverage_mode != "glob" and has_magic:
        raise RegistryCoverageError(f"record {record.id!r}: glob syntax requires coverage_mode='glob'")
    if record.coverage_mode == "recursive" and not locator.endswith("/"):
        raise RegistryCoverageError(f"record {record.id!r}: directory coverage locator must end in '/'")
    if record.coverage_mode == "exact" and locator.endswith("/"):
        raise RegistryCoverageError(f"record {record.id!r}: exact locator cannot end in '/'")
    return locator


def _glob_path_matches(relative_path: str, pattern: str) -> bool:
    """Match complete path components; only ** can span directories."""

    parts = relative_path.casefold().split("/")
    patterns = pattern.casefold().rstrip("/").split("/")

    def matches(path_index: int, pattern_index: int) -> bool:
        if pattern_index == len(patterns):
            return path_index == len(parts)
        component = patterns[pattern_index]
        if component == "**":
            return matches(path_index, pattern_index + 1) or (
                path_index < len(parts) and matches(path_index + 1, pattern_index)
            )
        return (
            path_index < len(parts)
            and fnmatch.fnmatchcase(parts[path_index], component)
            and matches(path_index + 1, pattern_index + 1)
        )

    return matches(0, 0)


class RegistryResolver:
    """Resolve project-relative objects against explicit registry coverage."""

    def __init__(self, records: Sequence[SoTArtifact]) -> None:
        self.records = tuple(records)
        self._locators: dict[str, str] = {}
        self._exact_records: dict[str, list[SoTArtifact]] = {}
        self._recursive_records: list[tuple[str, SoTArtifact]] = []
        self._glob_records: list[tuple[str, SoTArtifact]] = []
        for record in self.records:
            if record.coverage_mode is None:
                raise RegistryCoverageError(f"record {record.id!r}: coverage_mode is required")
            locator = _normalized_locator(record)
            if record.lifecycle == "archive":
                continue
            folded = locator.casefold()
            prior = self._locators.get(folded)
            if prior is not None and prior != locator:
                raise RegistryCoverageError(f"Windows case-fold locator collision: {prior!r} and {locator!r}")
            self._locators[folded] = locator
            if record.coverage_mode in {"exact", "opaque_container"}:
                self._exact_records.setdefault(folded.rstrip("/"), []).append(record)
            elif record.coverage_mode == "recursive":
                self._recursive_records.append((folded.rstrip("/"), record))
            elif record.coverage_mode == "glob":
                self._glob_records.append((folded, record))
        self._validate_overlaps()

    def _validate_overlaps(self) -> None:
        concrete = [record for record in self.records if record.coverage_mode != "virtual"]
        probes: set[str] = set()
        for record in concrete:
            locator = record.storage_path.rstrip("/")
            if record.coverage_mode == "glob":
                locator = locator.replace("*", "probe").replace("?", "x")
                locator = locator.replace("[0-9]", "0")
            probes.add(locator)
        for probe in probes:
            matches = self._matches(probe)
            if len(matches) > 1:
                ids = ", ".join(sorted(record.id for record in matches))
                raise RegistryCoverageError(f"ambiguous registry overlap for {probe!r}: {ids}")

    def _matches(self, relative_path: str) -> list[SoTArtifact]:
        normalized = relative_path.replace("\\", "/").strip("/")
        folded = normalized.casefold()
        matches = list(self._exact_records.get(folded, ()))
        matches.extend(
            record
            for locator_folded, record in self._recursive_records
            if folded == locator_folded or folded.startswith(locator_folded + "/")
        )
        matches.extend(
            record for locator_folded, record in self._glob_records if _glob_path_matches(folded, locator_folded)
        )
        return matches

    def resolve(self, relative_path: str | Path) -> SoTArtifact | None:
        normalized = str(relative_path).replace("\\", "/").strip("/")
        if not normalized or any(part in {".", ".."} for part in PurePosixPath(normalized).parts):
            raise RegistryCoverageError(f"unsafe project-relative path {relative_path!r}")
        matches = self._matches(normalized)
        if len(matches) > 1:
            ids = ", ".join(sorted(record.id for record in matches))
            raise RegistryCoverageError(f"ambiguous registry membership for {normalized!r}: {ids}")
        return matches[0] if matches else None

    def resolve_operation_path(self, relative_path: str | Path) -> SoTArtifact | None:
        """Resolve a member or a disposable child of one opaque container.

        Opaque payloads do not become registry identities or census members,
        but the registered container authorizes runtime operations beneath it.
        """

        normalized = str(relative_path).replace("\\", "/").strip("/")
        direct = self.resolve(normalized)
        if direct is not None:
            return direct
        containers = [
            record
            for record in self.records
            if record.lifecycle != "archive"
            and record.coverage_mode == "opaque_container"
            and normalized.casefold().startswith(record.storage_path.rstrip("/").casefold() + "/")
        ]
        if len(containers) > 1:
            ids = ", ".join(sorted(record.id for record in containers))
            raise RegistryCoverageError(f"ambiguous opaque operation authority for {normalized!r}: {ids}")
        return containers[0] if containers else None

    def is_structural_ancestor(self, relative_path: str | Path) -> bool:
        normalized = str(relative_path).replace("\\", "/").strip("/").casefold()
        prefix = normalized + "/"
        return any(
            record.lifecycle != "archive"
            and record.coverage_mode != "virtual"
            and record.storage_path.rstrip("/").casefold().startswith(prefix)
            for record in self.records
        )


@dataclass(frozen=True)
class RegistrySnapshot:
    records: tuple[SoTArtifact, ...]
    declaration_digest: str
    resolver: RegistryResolver


@dataclass(frozen=True)
class CensusEntry:
    relative_path: str
    object_kind: str
    coverage_class: CoverageClass
    registry_id: str | None = None
    detail: str | None = None


@contextmanager
def _open_registry_read_only_connection(db_path: Path) -> Iterator[sqlite3.Connection]:
    """Open an existing registry database without write or create authority."""

    uri = db_path.resolve().as_uri() + "?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    try:
        conn.execute("PRAGMA query_only=ON")
        if conn.execute("PRAGMA query_only").fetchone()[0] != 1:
            raise RegistryControlPlaneError(f"registry read connection is not query-only: {db_path}")
        yield conn
    finally:
        conn.close()


def load_registry_snapshot(*, project_root: Path | None = None, registry_path: Path | None = None) -> RegistrySnapshot:
    """Read and validate one current canonical declaration, without side effects."""
    path = RegistryPaths.resolve(project_root=project_root, registry_path=registry_path).registry_path
    try:
        payload = path.read_bytes()
    except OSError as exc:
        raise RegistryControlPlaneError(f"Cannot read canonical registry declaration at {path}: {exc}") from exc
    records = _load_toml_bytes(payload)
    return RegistrySnapshot(
        records=tuple(records), declaration_digest=_sha256_bytes(payload), resolver=RegistryResolver(records)
    )


def _atomic_replace(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        with temporary.open("wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        if os.name != "nt":
            directory_fd = os.open(path.parent, os.O_RDONLY)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
    finally:
        if temporary.exists():
            temporary.unlink()


def _path_object_kind(path: Path) -> str:
    metadata = path.lstat()
    attributes = getattr(metadata, "st_file_attributes", 0)
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    if attributes & reparse_flag:
        tag = getattr(metadata, "st_reparse_tag", None)
        if tag == getattr(stat, "IO_REPARSE_TAG_SYMLINK", object()):
            return "symlink"
        if tag == getattr(stat, "IO_REPARSE_TAG_MOUNT_POINT", object()):
            return "junction"
        return "reparse"
    if path.is_symlink():
        return "symlink"
    if stat.S_ISDIR(metadata.st_mode):
        return "directory"
    if stat.S_ISREG(metadata.st_mode):
        return "file"
    return "other"


def registry_identity_state(snapshot: RegistrySnapshot, *, project_root: Path) -> dict[str, Any]:
    """Check declared lifecycle and filesystem identity without hashing content."""

    root = project_root.resolve()
    missing: list[dict[str, str]] = []
    archived_present: list[dict[str, str]] = []
    object_kind_mismatches: list[dict[str, str]] = []
    invalid_paths: list[dict[str, str]] = []
    for record in snapshot.records:
        if record.coverage_mode == "virtual":
            continue
        try:
            objects = _record_objects(root, record)
            present = [target for target in objects if target.exists() or target.is_symlink()]
            if record.lifecycle == "archive":
                if present:
                    archived_present.append({"id": record.id, "path": record.storage_path})
            elif not present:
                missing.append({"id": record.id, "path": record.storage_path})
            elif record.coverage_mode == "recursive":
                observed_kind = _path_object_kind(present[0])
                if observed_kind != "directory":
                    object_kind_mismatches.append(
                        {
                            "id": record.id,
                            "path": record.storage_path,
                            "expected": "directory",
                            "observed": observed_kind,
                        }
                    )
        except (OSError, ValueError, RegistryCoverageError) as exc:
            invalid_paths.append({"id": record.id, "path": record.storage_path, "detail": str(exc)})
    return {
        "current": not missing and not archived_present and not object_kind_mismatches and not invalid_paths,
        "missing": missing,
        "archived_present": archived_present,
        "object_kind_mismatches": object_kind_mismatches,
        "invalid_paths": invalid_paths,
    }


def census_registry(
    snapshot: RegistrySnapshot,
    *,
    project_root: Path,
) -> tuple[CensusEntry, ...]:
    """Walk the whole platform root with only the two approved traversal boundaries."""

    root = project_root.resolve()
    entries: list[CensusEntry] = []

    def classify(path: Path, relative: str, object_kind: str) -> tuple[CensusEntry, bool]:
        if relative == ".git":
            return CensusEntry(relative, "vcs_service_state", "unregistered"), False
        parts = PurePosixPath(relative).parts
        if len(parts) == 2 and parts[0].casefold() == "applications" and object_kind == "directory":
            try:
                record = snapshot.resolver.resolve(relative)
            except RegistryCoverageError as exc:
                return CensusEntry(relative, "hosted_application_root", "invalid_unknown", detail=str(exc)), False
            coverage: CoverageClass = "registered_member" if record else "unregistered"
            return CensusEntry(relative, "hosted_application_root", coverage, record.id if record else None), False
        try:
            record = snapshot.resolver.resolve(relative)
        except RegistryCoverageError as exc:
            return CensusEntry(relative, object_kind, "invalid_unknown", detail=str(exc)), False
        if record is not None:
            coverage = "opaque_container" if record.coverage_mode == "opaque_container" else "registered_member"
            return CensusEntry(relative, object_kind, coverage, record.id), record.coverage_mode != "opaque_container"
        if snapshot.resolver.is_structural_ancestor(relative):
            return CensusEntry(relative, object_kind, "registered_structural_ancestor"), True
        return CensusEntry(relative, object_kind, "unregistered"), True

    def walk(directory: Path) -> None:
        try:
            children = sorted(directory.iterdir(), key=lambda item: item.name.casefold())
        except OSError as exc:
            relative = directory.relative_to(root).as_posix()
            entries.append(CensusEntry(relative, "unreadable", "invalid_unknown", detail=str(exc)))
            return
        for child in children:
            relative = child.relative_to(root).as_posix()
            try:
                object_kind = _path_object_kind(child)
                entry, descend = classify(child, relative, object_kind)
            except OSError as exc:
                entries.append(CensusEntry(relative, "unreadable", "invalid_unknown", detail=str(exc)))
                continue
            entries.append(entry)
            if descend and object_kind == "directory":
                walk(child)

    walk(root)
    for record in snapshot.records:
        if record.coverage_mode == "virtual":
            entries.append(CensusEntry(record.storage_path, "virtual", "virtual_declaration", record.id))
    return tuple(entries)


def _declaration_lock_path(
    project_root: Path, controls: Mapping[str, ResolvedOperationalControl] | None = None
) -> Path:
    """Reuse the OS writer mutex in this checkout's Git metadata directory."""
    controls = _registry_controls(project_root) if controls is None else controls
    result = subprocess.run(
        ["git", "-C", str(project_root), "rev-parse", "--absolute-git-dir", "--show-toplevel"],
        env={key: value for key, value in os.environ.items() if not key.upper().startswith("GIT_")},
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=float(control_value(controls, "registry.git_probe_seconds", unit="seconds")),
    )
    lines = result.stdout.splitlines()
    if result.returncode or len(lines) != 2 or Path(lines[1]).resolve() != project_root.resolve():
        raise RegistryCoverageError("Registry writes require the selected Git checkout root")
    return Path(lines[0]) / "gtkb-sot-registry.lock"


def _registry_config(root: Path, config: GTConfig | None) -> GTConfig:
    if config is not None:
        return config
    config_path = root / "groundtruth.toml"
    return GTConfig.load(
        config_path if config_path.is_file() else None,
        discover=False,
        project_root=root,
        **({} if config_path.is_file() else {"db_path": root / "groundtruth.db"}),
    )


def _validate_record_fields(record: SoTArtifact) -> SoTArtifact:
    payload = _record_payload(record)
    for field, value in payload.items():
        if field in {"depends_on", "forbidden_substitutes"}:
            continue
        if field == "health_check_function" and value is None:
            payload[field] = ""
        elif not isinstance(value, str):
            raise RegistryCoverageError(f"record {record.id!r}: {field} must be a string")
    for field in ("id", "storage_path", "authority_spec_id", "mutation_api"):
        if not payload[field].strip():
            raise RegistryCoverageError(f"record {record.id!r}: {field} must not be empty")
    return _parse_record(payload)


def _record_objects(root: Path, record: SoTArtifact) -> list[Path]:
    if record.coverage_mode == "virtual":
        return []
    if record.storage_path.split("/", 1)[0].casefold() == "applications":
        raise RegistryCoverageError("Hosted application artifacts are outside the platform registry")

    def expand(directory: Path, patterns: Sequence[str]) -> Iterator[Path]:
        if not patterns:
            yield directory
            return
        if _path_object_kind(directory) != "directory":
            return
        component, *remaining = patterns
        if component == "**":
            yield from expand(directory, remaining)
        for child in sorted(directory.iterdir(), key=lambda path: path.name.casefold()):
            if component == "**":
                if _path_object_kind(child) == "directory":
                    yield from expand(child, patterns)
                elif not remaining:
                    yield child
            elif fnmatch.fnmatchcase(child.name.casefold(), component.casefold()):
                yield from expand(child, remaining)

    if record.coverage_mode == "glob":
        objects = sorted(
            set(expand(root, record.storage_path.rstrip("/").split("/"))),
            key=lambda path: path.as_posix().casefold(),
        )
        if record.storage_path.endswith("/"):
            objects = [path for path in objects if _path_object_kind(path) == "directory"]
    else:
        objects = [root / record.storage_path.rstrip("/")]
    for target in objects:
        try:
            target.resolve().relative_to(root)
        except ValueError as exc:
            raise RegistryCoverageError(f"record {record.id!r}: locator escapes the selected root") from exc
    return objects


def _validate_relinquished_coverage(root: Path, old: SoTArtifact, resolver: RegistryResolver) -> None:
    """A declaration change cannot silently leave existing content uncovered."""

    def check(path: Path) -> None:
        relative = path.relative_to(root).as_posix()
        if resolver.resolve_operation_path(relative) is None and not (
            path.is_dir() and resolver.is_structural_ancestor(relative)
        ):
            raise RegistryCoverageError(f"record {old.id!r}: existing object would lose coverage: {relative}")

    def unreadable(error: OSError) -> None:
        raise RegistryCoverageError(f"Cannot inspect coverage being relinquished: {error}") from error

    for target in _record_objects(root, old):
        if not target.exists() and not target.is_symlink():
            continue
        check(target)
        if _path_object_kind(target) == "directory" and old.coverage_mode in {"recursive", "opaque_container"}:
            for parent, directories, files in os.walk(target, followlinks=False, onerror=unreadable):
                for name in [*directories, *files]:
                    check(Path(parent) / name)
                directories[:] = [name for name in directories if _path_object_kind(Path(parent) / name) == "directory"]


def _validate_registry_effects(
    paths: RegistryPaths,
    before: Sequence[SoTArtifact],
    after: Sequence[SoTArtifact],
    changed_ids: set[str],
    checked_ids: set[str],
    config: GTConfig,
) -> None:
    resolver = RegistryResolver(after)
    relative = paths.registry_path.relative_to(paths.project_root).as_posix()
    self_record = resolver.resolve(relative)
    if self_record is None:
        raise RegistryCoverageError("The canonical registry declaration must retain its own coverage")
    old_by_id = {record.id: record for record in before}
    new_by_id = {record.id: record for record in after}
    affected = [record for record in after if record.id in changed_ids | checked_ids]
    for record in affected:
        _record_objects(paths.project_root, record)
    identity = registry_identity_state(
        RegistrySnapshot(tuple(affected), "", resolver),
        project_root=paths.project_root,
    )
    if not identity["current"]:
        raise RegistryCoverageError(
            "Registry effect contradicts actual lifecycle, containment or object kind: "
            + json.dumps(identity, sort_keys=True)
        )
    for ident in changed_ids & old_by_id.keys():
        old, new = old_by_id[ident], new_by_id.get(ident)
        if new is None or (old.storage_path, old.coverage_mode, old.lifecycle) != (
            new.storage_path,
            new.coverage_mode,
            new.lifecycle,
        ):
            _validate_relinquished_coverage(paths.project_root, old, resolver)
    required = {self_record.authority_spec_id, *(record.authority_spec_id for record in affected)}
    if not config.authority_url:
        raise RegistryControlPlaneError("No authority_url is configured for the selected project")
    from urllib.parse import quote

    from groundtruth_kb.authority_client import AuthorityClient, AuthorityClientError

    client = AuthorityClient(config.authority_url)
    try:
        formals = {
            ident: client.request("GET", f"/v1/specifications/{quote(ident, safe='')}") for ident in sorted(required)
        }
    except AuthorityClientError as exc:
        raise RegistryControlPlaneError(f"{exc.code}: {exc}") from exc
    invalid = sorted(
        ident for ident, formal in formals.items() if not isinstance(formal, dict) or formal.get("status") != "active"
    )
    if invalid:
        raise RegistryCoverageError(f"Registry changes require current active formal sources: {invalid}")


def _render_registry_update(payload: bytes, records: Sequence[SoTArtifact]) -> bytes:
    """Change only selected tables/fields, retaining unrelated authored formatting."""
    import tomlkit

    document = tomlkit.parse(payload.decode("utf-8"))
    entries = document["artifacts"]
    wanted = {record.id: _record_payload(record) for record in records}
    for index in range(len(entries) - 1, -1, -1):
        if entries[index]["id"] not in wanted:
            del entries[index]
    present = set()
    for entry in entries:
        present.add(entry["id"])
        current = _record_payload(_parse_record(dict(entry)))
        for field, value in wanted[entry["id"]].items():
            if current[field] != value:
                entry[field] = value
    for record in records:
        if record.id not in present:
            entry = tomlkit.inline_table() if isinstance(entries, tomlkit.items.Array) else tomlkit.table()
            for field, value in wanted[record.id].items():
                entry[field] = value
            entries.append(entry)
    rendered = tomlkit.dumps(document).encode("utf-8")
    if tuple(_load_toml_bytes(rendered)) != tuple(records):
        raise RegistryControlPlaneError("Rendered declaration does not match the intended records")
    return rendered


def _update_registry(
    build: Callable[[tuple[SoTArtifact, ...]], tuple[SoTArtifact, ...]],
    *,
    checked_ids: set[str],
    project_root: Path | None = None,
    registry_path: Path | None = None,
    config: GTConfig | None = None,
    expected_declaration_digest: str | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    paths = RegistryPaths.resolve(project_root=project_root, registry_path=registry_path)
    try:
        paths.registry_path.relative_to(paths.project_root)
    except ValueError as exc:
        raise RegistryCoverageError("The declaration must be inside the selected project root") from exc
    selected = _registry_config(paths.project_root, config)
    controls = _registry_controls(paths.project_root)

    def prepare() -> tuple[bytes, bytes, dict[str, Any]]:
        before_bytes = paths.registry_path.read_bytes()
        before = tuple(_load_toml_bytes(before_bytes))
        before_digest = _sha256_bytes(before_bytes)
        if expected_declaration_digest is not None and expected_declaration_digest != before_digest:
            raise RegistryGenerationConflict("The canonical declaration changed; read current state before retrying")
        after = tuple(build(before))
        if len({record.id for record in after}) != len(after):
            raise RegistryCoverageError("Duplicate registry IDs in the requested declaration")
        old_by_id = {record.id: record for record in before}
        new_by_id = {record.id: record for record in after}
        changed_ids = {
            ident for ident in old_by_id.keys() | new_by_id.keys() if old_by_id.get(ident) != new_by_id.get(ident)
        }
        # Validate requested postimages without turning unrelated historical
        # metadata into a prerequisite for a current declaration change.
        # Resolver, identity and affected-coverage checks still run below.
        for record in after:
            if record.id in changed_ids | checked_ids:
                _validate_record_fields(record)
        _validate_registry_effects(paths, before, after, changed_ids, checked_ids, selected)
        rendered = _render_registry_update(before_bytes, after) if changed_ids else before_bytes
        return (
            before_bytes,
            rendered,
            {
                "changed": bool(changed_ids),
                "dry_run": dry_run,
                "control_catalog_sha256": next(iter(controls.values())).catalog_sha256,
                "before_digest": before_digest,
                "declaration_digest": _sha256_bytes(rendered),
                "record_count": len(after),
                "changed_ids": sorted(changed_ids),
            },
        )

    if dry_run:
        return prepare()[2]
    with _RegistryFileLock(_declaration_lock_path(paths.project_root, controls), controls=controls):
        before, after, result = prepare()
        # Direct owner edits do not take this cooperative writer mutex.
        if paths.registry_path.read_bytes() != before:
            raise RegistryGenerationConflict("The canonical declaration changed during validation; read current state")
        if result["changed"]:
            _atomic_replace(paths.registry_path, after)
        if paths.registry_path.read_bytes() != after:
            raise RegistryRecoveryRequired(
                "The declaration changed after replacement; inspect current source before retrying"
            )
        return result


def register_artifacts(records: Sequence[SoTArtifact], **options: Any) -> dict[str, Any]:
    additions = tuple(_validate_record_fields(record) for record in records)
    if not additions or len({record.id for record in additions}) != len(additions):
        raise RegistryCoverageError("Registration requires a nonempty set of unique IDs")

    def build(current: tuple[SoTArtifact, ...]) -> tuple[SoTArtifact, ...]:
        existing = {record.id: record for record in current}
        replacements = {
            record.id: record
            for record in additions
            if record.id in existing and existing[record.id].lifecycle == "archive" and record.lifecycle != "archive"
        }
        mismatched = [
            record.id
            for record in additions
            if record.id in existing and existing[record.id] != record and record.id not in replacements
        ]
        if mismatched:
            raise RegistryCoverageError(f"Existing IDs differ from the requested registration: {sorted(mismatched)}")
        return (
            *(replacements.get(record.id, record) for record in current),
            *(record for record in additions if record.id not in existing),
        )

    return _update_registry(build, checked_ids={record.id for record in additions}, **options)


_AMENDABLE_FIELDS = frozenset(
    {
        "domain",
        "authority_spec_id",
        "mutation_api",
        "versioning_policy",
        "backup_policy",
        "restore_action",
        "health_check_function",
        "owner_role",
        "depends_on",
        "forbidden_substitutes",
        "notes",
    }
)


def amend_artifact(artifact_id: str, changes: Mapping[str, Any], **options: Any) -> dict[str, Any]:
    if not changes or set(changes) - _AMENDABLE_FIELDS:
        raise RegistryCoverageError(
            "Metadata amendment requires non-identity fields; "
            "use registry transition for locator, coverage or lifecycle changes"
        )
    return transition_artifact(artifact_id, changes, **options)


def transition_artifact(
    artifact_id: str,
    changes: Mapping[str, Any] | None = None,
    *,
    remove: bool = False,
    removals: Sequence[str] = (),
    **options: Any,
) -> dict[str, Any]:
    changes = dict(changes or {})
    if remove == bool(changes) or set(changes) - (_AMENDABLE_FIELDS | {"storage_path", "coverage_mode", "lifecycle"}):
        raise RegistryCoverageError("Supply field changes or one explicit membership removal")
    if (
        not isinstance(removals, (list, tuple))
        or any(not isinstance(ident, str) or not ident.strip() for ident in removals)
        or len(set(removals)) != len(removals)
        or artifact_id in removals
    ):
        raise RegistryCoverageError("Related removals must be unique nonempty IDs distinct from the primary ID")
    selected_ids = {artifact_id, *removals}
    removed_ids = set(removals) | ({artifact_id} if remove else set())

    def build(current: tuple[SoTArtifact, ...]) -> tuple[SoTArtifact, ...]:
        missing = selected_ids - {record.id for record in current}
        if missing:
            raise RegistryCoverageError(f"Registry ID not found: {', '.join(sorted(missing))}")
        selected = next(record for record in current if record.id == artifact_id)
        if "lifecycle" in changes:
            legal = {
                "active": {"generated", "deprecated", "archive"},
                "generated": {"active", "archive"},
                "deprecated": {"active", "archive"},
                "archive": set(),
            }
            if not isinstance(changes["lifecycle"], str) or changes["lifecycle"] not in legal[selected.lifecycle]:
                raise RegistryCoverageError(
                    f"Invalid lifecycle transition: {selected.lifecycle} -> {changes['lifecycle']!r}; "
                    "archived surfaces re-enter through register"
                )
        if selected.lifecycle == "archive" and {"storage_path", "coverage_mode"} & changes.keys():
            raise RegistryCoverageError("Archived lifecycle identity cannot change through transition; use register")
        return tuple(
            _parse_record({**_record_payload(record), **changes}) if record.id == artifact_id else record
            for record in current
            if record.id not in removed_ids
        )

    return _update_registry(build, checked_ids=selected_ids, **options)


def inspect_registry(
    *,
    project_root: Path | None = None,
    registry_path: Path | None = None,
    db_path: Path | None = None,
    include_census: bool = True,
    config: GTConfig | None = None,
) -> dict[str, Any]:
    """Inspect the current declaration and actual objects, without observation debt."""
    paths = RegistryPaths.resolve(project_root=project_root, registry_path=registry_path)
    try:
        snapshot = load_registry_snapshot(project_root=paths.project_root, registry_path=paths.registry_path)
    except (OSError, ValueError, RegistryControlPlaneError) as exc:
        return {"coherent": False, "error": type(exc).__name__, "detail": str(exc)}
    report = {
        "coherent": True,
        "record_count": len(snapshot.records),
        "declaration_digest": snapshot.declaration_digest,
        "identity_state": registry_identity_state(snapshot, project_root=paths.project_root),
    }
    if include_census:
        from groundtruth_kb.project.artifact_membership_reconciliation import (
            reconcile_artifact_membership,
            reconciliation_summary,
        )

        reconciliation = reconcile_artifact_membership(
            paths.project_root, snapshot=snapshot, db_path=db_path, config=config
        )
        summary = reconciliation_summary(reconciliation)
        report["membership_reconciliation"] = summary
        report["reverse_coverage"] = {
            "object_count": sum(summary["counts"].values()),
            "counts": summary["counts"],
            "gaps": [
                entry
                for entry in reconciliation["entries"]
                if entry["membership_class"] in {"unregistered_load_bearing", "invalid_unknown"}
            ],
        }
    return report


def validate_registry(
    *,
    project_root: Path | None = None,
    registry_path: Path | None = None,
    db_path: Path | None = None,
    config: GTConfig | None = None,
    require_reverse_closure: bool = True,
) -> dict[str, Any]:
    report = inspect_registry(
        project_root=project_root,
        registry_path=registry_path,
        db_path=db_path,
        config=config,
        include_census=require_reverse_closure,
    )
    errors: list[str] = []
    if not report.get("coherent"):
        errors.append(str(report.get("error", "registry_not_coherent")))
    else:
        if not report["identity_state"]["current"]:
            errors.append("registry_identity_failure")
        if require_reverse_closure and not report["membership_reconciliation"]["membership_complete"]:
            errors.append("registry_membership_incomplete")
    return {**report, "valid": not errors, "errors": errors}
