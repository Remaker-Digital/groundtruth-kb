"""Coherent control plane for the platform SoT artifact registry.

The canonical TOML, packaged TOML mirror, and MemBase projection form one
logical generation. This module owns the cross-process read barrier,
journalled mutations, deterministic recovery, reverse-coverage census, and
single-use observation evidence for that generation.
"""

from __future__ import annotations

import fnmatch
import hashlib
import json
import os
import random
import re
import secrets
import sqlite3
import stat
import subprocess
import sys
import tempfile
import time
import uuid
from collections.abc import Iterator, Mapping, Sequence
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager, suppress
from dataclasses import asdict, dataclass, replace
from datetime import UTC, datetime, timedelta
from pathlib import Path, PurePosixPath
from typing import Any, Literal

from groundtruth_kb.project.sot_registry import (
    SoTArtifact,
    _load_projection_from_connection,
    _load_projection_unlocked,
    _load_toml_bytes,
    _load_toml_unlocked,
    validate_projection_parity,
)
from groundtruth_kb.project.timer_config import resolve_protected_commit_timers

CoverageClass = Literal[
    "registered_member",
    "registered_structural_ancestor",
    "opaque_container",
    "virtual_declaration",
    "unregistered",
    "invalid_unknown",
]
EvidenceView = Literal[
    "working_tree",
    "git_index",
    "governed_tool",
    "registry_transaction",
    "bridge_publication",
    "recovery",
]

TERMINAL_JOURNAL_STATES = frozenset({"committed", "aborted"})
APPROVED_VIRTUAL_SCHEMES = frozenset({"membase", "windows-scheduled-task"})
SUPPORTED_EVIDENCE_VIEWS: frozenset[str] = frozenset(
    {"working_tree", "git_index", "governed_tool", "registry_transaction", "bridge_publication", "recovery"}
)

# Reviewed explicitly in bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-007.md.
# Do not infer or expand this map from punctuation or filesystem object type.
LEGACY_COVERAGE_MODES: dict[str, str] = {
    "sot-registry-toml": "exact",
    "membase-specifications": "virtual",
    "membase-work-items": "virtual",
    "membase-tests": "virtual",
    "membase-deliberations": "virtual",
    "membase-projects": "virtual",
    "membase-pauths": "virtual",
    "membase-assertion-runs": "virtual",
    "owner-local-env": "exact",
    "claude-md": "exact",
    "agents-md": "exact",
    "rule-canonical-terminology": "exact",
    "rule-operating-model": "exact",
    "rule-file-bridge-protocol": "exact",
    "bridge-versioned-files": "glob",
    "bridge-dir": "opaque_container",
    "bridge-work-intent-claims": "virtual",
    "bridge-dispatch-state": "exact",
    "dispatcher-supervisor-task": "virtual",
    "dispatcher-storm-watchdog-task": "virtual",
    "harness-identities": "exact",
    "harness-registry": "exact",
    "harness-bridge-substrate": "exact",
    "harness-capability-registry": "exact",
    "session-startup-control-map": "exact",
    "managed-artifacts-registry": "exact",
    "generated-runtime-state-tree": "opaque_container",
    "generated-session-state-tree": "opaque_container",
    "scanner-safe-writer-log": "exact",
    "api-skill-adapter-manifest": "exact",
    "codex-skill-adapter-manifest": "exact",
    "api-harness-routing": "exact",
    "canonical-terminology-machine-registry": "exact",
    "project-resource-alias-registry": "exact",
    "project-resource-alias-pointer": "exact",
    "dependabot-configuration": "exact",
    "directive-registry": "exact",
    "agent-red-api-version-probe": "exact",
    "application-registry": "exact",
    "dispatcher-rules": "exact",
    "governance-config-tree": "recursive",
    "development-environment-inventory": "exact",
    "groundtruth-package-metadata": "exact",
    "groundtruth-version-source": "exact",
    "groundtruth-root-config": "exact",
    "pending-owner-decisions": "exact",
    "workspace-python-config": "exact",
    "cursor-harness-source": "exact",
    "sonar-project-config": "exact",
    "bridge-index": "exact",
}

IMPLEMENTATION_ARTIFACTS: tuple[SoTArtifact, ...] = (
    SoTArtifact(
        id="registry-control-plane-module",
        domain="control_surface",
        lifecycle="active",
        storage_path="groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py",
        authority_spec_id="GOV-PLATFORM-SOT-REGISTRY-001",
        mutation_api="gt registry register; gt registry amend",
        versioning_policy="git_tracked",
        backup_policy="git_tracked",
        health_check_function="_check_sot_registry_completeness",
        owner_role="shared",
        restore_action="git_restore",
        notes="Canonical registry transaction, snapshot, resolver, observation, and census service.",
        coverage_mode="exact",
    ),
    SoTArtifact(
        id="registry-control-plane-tests",
        domain="governance_policy",
        lifecycle="active",
        storage_path="groundtruth-kb/tests/test_registry_control_plane.py",
        authority_spec_id="GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001",
        mutation_api="governed source edit under bridge GO",
        versioning_policy="git_tracked",
        backup_policy="git_tracked",
        health_check_function="pytest groundtruth-kb/tests/test_registry_control_plane.py",
        owner_role="shared",
        restore_action="git_restore",
        notes="Specification-derived tests for the canonical registry control plane.",
        coverage_mode="exact",
    ),
    SoTArtifact(
        id="registry-observation-hook",
        domain="control_surface",
        lifecycle="active",
        storage_path="scripts/registry_observation_hook.py",
        authority_spec_id="DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001",
        mutation_api="governed source edit under bridge GO",
        versioning_policy="git_tracked",
        backup_policy="git_tracked",
        health_check_function="registry observation hook tests",
        owner_role="shared",
        restore_action="git_restore",
        notes="Capability-consuming post-tool observer for registered artifacts.",
        coverage_mode="exact",
    ),
    SoTArtifact(
        id="registry-observation-hook-tests",
        domain="governance_policy",
        lifecycle="active",
        storage_path="platform_tests/scripts/test_registry_observation_hook.py",
        authority_spec_id="GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001",
        mutation_api="governed source edit under bridge GO",
        versioning_policy="git_tracked",
        backup_policy="git_tracked",
        health_check_function="pytest platform_tests/scripts/test_registry_observation_hook.py",
        owner_role="shared",
        restore_action="git_restore",
        notes="Cross-harness negative and positive observation-authority tests.",
        coverage_mode="exact",
    ),
)


class RegistryControlPlaneError(RuntimeError):
    """Base error for coherent registry operations."""


class RegistryFileLockAcquisitionTimeout(RegistryControlPlaneError):
    """Typed caller-retryable transient for control-plane lock acquisition timeout.

    WI-5869: replaces the bare ``TimeoutError`` raised when the
    ``_RegistryFileLock`` acquisition deadline is exhausted. The typed subclass
    lets callers classify and retry the transient rather than treating it as a
    hard failure.
    """


class RegistryProjectionMismatch(RegistryControlPlaneError):
    """Raised when the declaration and MemBase projection are not coherent."""


class RegistryTransactionInProgress(RegistryControlPlaneError):
    """Raised when a nonterminal registry transaction blocks authority reads."""


class RegistryRecoveryRequired(RegistryControlPlaneError):
    """Raised when deterministic recovery cannot choose a safe state."""


class RegistryCoverageError(RegistryControlPlaneError):
    """Raised for unsafe, ambiguous, or incomplete registry coverage."""


class RegistryAuthorizationError(RegistryControlPlaneError):
    """Raised when mutation or observation authority is missing or mismatched."""


class RegistryGenerationConflict(RegistryAuthorizationError):
    """Raised when an amend snapshot is stale at the commit linearization point."""


@dataclass(frozen=True)
class RegistryPaths:
    project_root: Path
    registry_path: Path
    packaged_registry_path: Path
    db_path: Path
    lock_path: Path

    @classmethod
    def resolve(
        cls,
        *,
        project_root: Path | None = None,
        registry_path: Path | None = None,
        packaged_registry_path: Path | None = None,
        db_path: Path | None = None,
    ) -> RegistryPaths:
        if project_root is None:
            if registry_path is not None and registry_path.name == "sot-artifacts.toml":
                candidate = registry_path.resolve()
                project_root = candidate.parents[2] if candidate.parent.name == "registry" else candidate.parent
            elif db_path is not None:
                project_root = Path(db_path).resolve().parent
            else:
                project_root = Path(__file__).resolve().parents[4]
        root = Path(project_root).resolve()
        canonical = Path(registry_path or root / "config" / "registry" / "sot-artifacts.toml").resolve()
        packaged = Path(
            packaged_registry_path
            or root
            / "groundtruth-kb"
            / "src"
            / "groundtruth_kb"
            / "context"
            / "registries"
            / "v1"
            / "config"
            / "registry"
            / "sot-artifacts.toml"
        ).resolve()
        database = Path(db_path or root / "groundtruth.db").resolve()
        lock = root / ".gtkb-state" / "sot-registry" / "control-plane.lock"
        return cls(root, canonical, packaged, database, lock)


_DEFAULT_REGISTRY_LOCK_TIMEOUT_SECONDS = 300.0
_REGISTRY_LOCK_TIMEOUT_ENV = "GTKB_REGISTRY_LOCK_TIMEOUT_SECONDS"
# WI-5869: bounded exponential backoff + jitter for the acquisition polling
# loop. These are in-memory module constants (no timer/config TOML mutation);
# they are tuned per DELIB-202667722 and capped so a sleep never exceeds the
# remaining acquisition deadline.
_REGISTRY_LOCK_INITIAL_BACKOFF_SECONDS = 0.05
_REGISTRY_LOCK_MAX_BACKOFF_SECONDS = 1.0
_REGISTRY_LOCK_BACKOFF_FACTOR = 2.0


def _resolve_registry_lock_timeout(explicit: float | None) -> float:
    """Resolve the control-plane lock acquisition timeout in seconds.

    Precedence: an explicit caller value wins; otherwise the
    ``GTKB_REGISTRY_LOCK_TIMEOUT_SECONDS`` environment variable; otherwise a
    generous default. Per DELIB-202667722 (timer governance: relaxed-first,
    config-backed, no invisible hard-coded values) and WI-5788, the default is
    generous so sustained concurrent registry writers wait through
    control-plane.lock contention instead of hard-failing at the retired 30s
    deadline. Only the acquisition-wait deadline is resolved here; lock
    ordering, exclusivity, acquisition, and release semantics are unchanged. A
    lock timeout fails open to the generous default (never fail-closed): a
    registry operation that errored merely because the env var was unset or
    malformed would be worse than the contention it guards against.
    """
    if explicit is not None:
        return explicit
    raw = os.environ.get(_REGISTRY_LOCK_TIMEOUT_ENV)
    if raw is not None:
        try:
            value = float(raw)
        except ValueError:
            return _DEFAULT_REGISTRY_LOCK_TIMEOUT_SECONDS
        if value > 0:
            return value
    return _DEFAULT_REGISTRY_LOCK_TIMEOUT_SECONDS


class _RegistryFileLock:
    def __init__(self, path: Path, timeout: float | None = None) -> None:
        self.path = path
        self.timeout = _resolve_registry_lock_timeout(timeout)
        self._handle: Any = None

    def __enter__(self) -> _RegistryFileLock:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._handle = self.path.open("a+b")
        self._handle.seek(0, os.SEEK_END)
        if self._handle.tell() == 0:
            self._handle.write(b"0")
            self._handle.flush()
        deadline = time.monotonic() + self.timeout
        backoff = _REGISTRY_LOCK_INITIAL_BACKOFF_SECONDS
        attempt = 0
        while True:
            try:
                self._handle.seek(0)
                if os.name == "nt":
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
                backoff = min(backoff * _REGISTRY_LOCK_BACKOFF_FACTOR, _REGISTRY_LOCK_MAX_BACKOFF_SECONDS)
                jitter = backoff * random.uniform(0.5, 1.0)
                sleep_seconds = min(jitter, max(0.0, remaining))
                if sleep_seconds > 0:
                    time.sleep(sleep_seconds)

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> None:
        if self._handle is None:
            return
        try:
            self._handle.seek(0)
            if os.name == "nt":
                import msvcrt

                msvcrt.locking(self._handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl

                fcntl.flock(self._handle.fileno(), fcntl.LOCK_UN)
        finally:
            self._handle.close()


def _utc_now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sha256_bytes(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _json_digest(value: Any) -> str:
    return _sha256_bytes(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8"))


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
        "# The packaged mirror and MemBase projection are one journalled generation.",
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


def _record_from_payload(payload: Mapping[str, Any]) -> SoTArtifact:
    values = dict(payload)
    values["depends_on"] = tuple(values.get("depends_on") or ())
    values["forbidden_substitutes"] = tuple(values.get("forbidden_substitutes") or ())
    return SoTArtifact(**values)


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
    parts = PurePosixPath(locator.rstrip("/")).parts
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
            record for locator_folded, record in self._glob_records if fnmatch.fnmatchcase(folded, locator_folded)
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
            if record.coverage_mode == "opaque_container"
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
            record.coverage_mode != "virtual" and record.storage_path.rstrip("/").casefold().startswith(prefix)
            for record in self.records
        )


@dataclass(frozen=True)
class RegistrySnapshot:
    records: tuple[SoTArtifact, ...]
    declaration_digest: str
    packaged_digest: str
    projection_digest: str
    generation_digest: str
    resolver: RegistryResolver


@dataclass(frozen=True)
class RegistryTransactionReceipt:
    journal_id: str
    operation: str
    receipt_digest: str
    declaration_digest: str
    projection_digest: str
    record_count: int
    idempotent_retry: bool = False


@dataclass(frozen=True)
class RegistryRegistrationPreview:
    starting_generation_digest: str
    candidate_manifest_sha256: str
    observer_input_digests: dict[str, str]
    reconciliation_evidence_digest: str | None
    desired_declaration_digest: str
    desired_projection_digest: str
    desired_record_count: int
    candidate_count: int
    dry_run_receipt: str


@dataclass(frozen=True)
class BridgeAggregateRecoveryReceipt:
    receipt_id: str
    receipt_digest: str
    revision_id: str
    prior_digest: str
    observed_digest: str
    inventory_digest: str
    lifecycle_digest: str
    idempotent_retry: bool = False


@dataclass(frozen=True)
class BridgePublicationReceipt:
    capability_hash: str
    revision_id: str | None
    target_path: str
    aggregate_digest: str
    capability_state: str


@dataclass(frozen=True)
class CensusEntry:
    relative_path: str
    object_kind: str
    coverage_class: CoverageClass
    registry_id: str | None = None
    detail: str | None = None


def _projection_digest(records: Sequence[SoTArtifact]) -> str:
    return _json_digest([_record_payload(record) for record in sorted(records, key=lambda item: item.id)])


def _table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type IN ('table', 'view') AND name = ?",
        (table_name,),
    ).fetchone()
    return row is not None


def _ensure_column(conn: sqlite3.Connection, table: str, column: str, declaration: str) -> None:
    columns = {row[1] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()}
    if column not in columns:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {declaration}")


def ensure_control_plane_schema(conn: sqlite3.Connection) -> None:
    """Create or migrate the additive WI-5441 control-plane schema."""

    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS sot_artifact_revisions (
            rowid INTEGER PRIMARY KEY AUTOINCREMENT,
            revision_id TEXT NOT NULL,
            entry_id TEXT NOT NULL,
            canonical_relative_path TEXT NOT NULL,
            object_kind TEXT NOT NULL,
            content_digest TEXT NOT NULL,
            size_bytes INTEGER,
            observed_at TEXT NOT NULL,
            actor_session TEXT NOT NULL,
            operation TEXT NOT NULL,
            predecessor_revision_id TEXT,
            changed_by TEXT NOT NULL,
            changed_at TEXT NOT NULL,
            change_reason TEXT NOT NULL,
            capability_hash TEXT,
            bridge_id TEXT,
            start_packet_hash TEXT,
            pauth_decision TEXT,
            journal_id TEXT,
            evidence_view TEXT NOT NULL DEFAULT 'working_tree',
            evidence_source_reference TEXT,
            UNIQUE(revision_id)
        );
        CREATE INDEX IF NOT EXISTS idx_sot_artifact_revisions_entry
            ON sot_artifact_revisions(entry_id);
        CREATE TABLE IF NOT EXISTS sot_registry_transaction_journal (
            rowid INTEGER PRIMARY KEY AUTOINCREMENT,
            journal_id TEXT NOT NULL,
            operation TEXT NOT NULL,
            entry_id TEXT,
            intent_recorded_at TEXT NOT NULL,
            declaration_digest TEXT,
            prior_revision_id TEXT,
            current_revision_id TEXT,
            filesystem_result TEXT,
            projection_transaction TEXT,
            receipt_digest TEXT,
            journal_state TEXT NOT NULL,
            completed_at TEXT,
            actor_session TEXT NOT NULL,
            changed_by TEXT NOT NULL,
            changed_at TEXT NOT NULL,
            change_reason TEXT NOT NULL,
            old_canonical_digest TEXT,
            new_canonical_digest TEXT,
            old_packaged_digest TEXT,
            new_packaged_digest TEXT,
            old_projection_digest TEXT,
            new_projection_digest TEXT,
            request_digest TEXT,
            payload_json TEXT,
            expected_record_count INTEGER,
            start_packet_hash TEXT,
            pauth_id TEXT,
            bridge_id TEXT,
            receipt_seed TEXT,
            error_message TEXT,
            UNIQUE(journal_id)
        );
        CREATE INDEX IF NOT EXISTS idx_sot_registry_txn_journal_state
            ON sot_registry_transaction_journal(journal_state);
        CREATE TABLE IF NOT EXISTS sot_registry_observation_capabilities (
            rowid INTEGER PRIMARY KEY AUTOINCREMENT,
            capability_hash TEXT NOT NULL,
            session_id TEXT NOT NULL,
            tool_event_id TEXT NOT NULL,
            paths_json TEXT NOT NULL,
            preimage_digests_json TEXT NOT NULL,
            bridge_id TEXT NOT NULL,
            start_packet_hash TEXT NOT NULL,
            pauth_decision_json TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            operation TEXT NOT NULL,
            capability_state TEXT NOT NULL,
            created_at TEXT NOT NULL,
            consumed_at TEXT,
            result_digest TEXT,
            UNIQUE(capability_hash)
        );
        CREATE INDEX IF NOT EXISTS idx_sot_registry_observation_state
            ON sot_registry_observation_capabilities(capability_state, expires_at);
        CREATE TABLE IF NOT EXISTS sot_registry_bridge_recovery_receipts (
            rowid INTEGER PRIMARY KEY AUTOINCREMENT,
            receipt_id TEXT NOT NULL,
            request_digest TEXT NOT NULL,
            receipt_digest TEXT NOT NULL,
            revision_id TEXT NOT NULL,
            prior_digest TEXT NOT NULL,
            observed_digest TEXT NOT NULL,
            inventory_digest TEXT NOT NULL,
            lifecycle_digest TEXT NOT NULL,
            evidence_json TEXT NOT NULL,
            created_at TEXT NOT NULL,
            UNIQUE(receipt_id),
            UNIQUE(request_digest)
        );
        CREATE TABLE IF NOT EXISTS sot_registry_bridge_publication_capabilities (
            rowid INTEGER PRIMARY KEY AUTOINCREMENT,
            capability_hash TEXT NOT NULL,
            authority_kind TEXT NOT NULL,
            document_name TEXT NOT NULL,
            version INTEGER NOT NULL,
            status TEXT NOT NULL,
            target_path TEXT NOT NULL,
            content_digest TEXT NOT NULL,
            compliance_digest TEXT NOT NULL,
            transition_digest TEXT NOT NULL,
            claim_session TEXT NOT NULL,
            author_session_context_id TEXT NOT NULL,
            aggregate_entry_id TEXT NOT NULL,
            aggregate_preimage_digest TEXT NOT NULL,
            operation TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            capability_state TEXT NOT NULL,
            created_at TEXT NOT NULL,
            consumed_at TEXT,
            result_digest TEXT,
            revision_id TEXT,
            compensation_revision_id TEXT,
            compensation_digest TEXT,
            failure_reason TEXT,
            UNIQUE(capability_hash)
        );
        CREATE INDEX IF NOT EXISTS idx_sot_registry_bridge_publication_state
            ON sot_registry_bridge_publication_capabilities(capability_state, expires_at);
        CREATE TABLE IF NOT EXISTS sot_registry_transition_requests (
            rowid INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id TEXT NOT NULL,
            request_digest TEXT NOT NULL,
            entry_id TEXT NOT NULL,
            source_locator TEXT NOT NULL,
            current_revision_digest TEXT NOT NULL,
            operation TEXT NOT NULL,
            destination TEXT NOT NULL,
            owner_evidence TEXT NOT NULL,
            intended_membership_result TEXT NOT NULL,
            request_state TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            created_at TEXT NOT NULL,
            consumed_at TEXT,
            result_digest TEXT,
            actor_session TEXT NOT NULL,
            changed_by TEXT NOT NULL,
            changed_at TEXT NOT NULL,
            change_reason TEXT NOT NULL,
            bridge_id TEXT NOT NULL,
            pauth_id TEXT NOT NULL,
            start_packet_hash TEXT NOT NULL,
            UNIQUE(request_id)
        );
        CREATE INDEX IF NOT EXISTS idx_sot_registry_transition_request_state
            ON sot_registry_transition_requests(request_state, expires_at);
        """
    )
    journal_columns = {
        "old_canonical_digest": "TEXT",
        "new_canonical_digest": "TEXT",
        "old_packaged_digest": "TEXT",
        "new_packaged_digest": "TEXT",
        "old_projection_digest": "TEXT",
        "new_projection_digest": "TEXT",
        "request_digest": "TEXT",
        "payload_json": "TEXT",
        "expected_record_count": "INTEGER",
        "start_packet_hash": "TEXT",
        "pauth_id": "TEXT",
        "bridge_id": "TEXT",
        "receipt_seed": "TEXT",
        "error_message": "TEXT",
    }
    for name, declaration in journal_columns.items():
        _ensure_column(conn, "sot_registry_transaction_journal", name, declaration)
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_sot_registry_txn_journal_request "
        "ON sot_registry_transaction_journal(operation, request_digest)"
    )
    revision_columns = {
        "capability_hash": "TEXT",
        "bridge_id": "TEXT",
        "start_packet_hash": "TEXT",
        "pauth_decision": "TEXT",
        "journal_id": "TEXT",
        "evidence_view": "TEXT NOT NULL DEFAULT 'working_tree'",
        "evidence_source_reference": "TEXT",
    }
    for name, declaration in revision_columns.items():
        _ensure_column(conn, "sot_artifact_revisions", name, declaration)


def _nonterminal_journal(db_path: Path) -> sqlite3.Row | None:
    if not db_path.exists():
        return None
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        if not _table_exists(conn, "sot_registry_transaction_journal"):
            return None
        return conn.execute(
            "SELECT * FROM sot_registry_transaction_journal "
            "WHERE journal_state NOT IN ('committed', 'aborted') ORDER BY rowid DESC LIMIT 1"
        ).fetchone()
    finally:
        conn.close()


def _ensure_no_nonterminal_journal(db_path: Path) -> None:
    row = _nonterminal_journal(db_path)
    if row is not None:
        raise RegistryTransactionInProgress(
            f"registry journal {row['journal_id']} is {row['journal_state']}; run gt registry recover"
        )


class _RegistryOptimisticConflict(RuntimeError):
    """Signal that one optimistic read must replay under the exclusive lock."""


@dataclass(frozen=True)
class _TerminalRegistryGeneration:
    row_digest: str
    rowid: int
    journal_id: str
    journal_state: str
    canonical_digest: str
    packaged_digest: str
    projection_digest: str


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


def _read_terminal_generation_marker(db_path: Path) -> _TerminalRegistryGeneration | None:
    """Return one complete terminal journal head from a read-only snapshot."""

    if not db_path.exists():
        return None
    with _open_registry_read_only_connection(db_path) as conn:
        conn.row_factory = sqlite3.Row
        conn.execute("BEGIN")
        if not _table_exists(conn, "sot_registry_transaction_journal"):
            return None
        if conn.execute(
            "SELECT 1 FROM sot_registry_transaction_journal WHERE journal_state NOT IN ('committed', 'aborted') LIMIT 1"
        ).fetchone():
            return None
        row = conn.execute(
            "SELECT * FROM sot_registry_transaction_journal "
            "WHERE journal_state IN ('committed', 'aborted') ORDER BY rowid DESC LIMIT 1"
        ).fetchone()
        if row is None:
            return None
        state = str(row["journal_state"])
        prefix = "new" if state == "committed" else "old"
        canonical_digest = row[f"{prefix}_canonical_digest"]
        packaged_digest = row[f"{prefix}_packaged_digest"]
        projection_digest = row[f"{prefix}_projection_digest"]
        digest_values = (canonical_digest, packaged_digest, projection_digest)
        if not all(isinstance(value, str) and value for value in digest_values):
            return None
        row_payload = dict(row)
        return _TerminalRegistryGeneration(
            row_digest=_json_digest(row_payload),
            rowid=int(row["rowid"]),
            journal_id=str(row["journal_id"]),
            journal_state=state,
            canonical_digest=canonical_digest,
            packaged_digest=packaged_digest,
            projection_digest=projection_digest,
        )


class _RegistryReadLease:
    """Bind caller-returned data to one unchanged terminal generation."""

    def __init__(self, paths: RegistryPaths, marker: _TerminalRegistryGeneration | None) -> None:
        self.paths = paths
        self.marker = marker
        self._canonical_payload: bytes | None = None
        self._canonical_records: tuple[SoTArtifact, ...] | None = None
        self._projection_records: tuple[SoTArtifact, ...] | None = None

    @property
    def optimistic(self) -> bool:
        return self.marker is not None

    def bind_toml(self, payload: bytes, records: Sequence[SoTArtifact]) -> None:
        self._canonical_payload = payload
        self._canonical_records = tuple(records)

    def bind_projection(self, records: Sequence[SoTArtifact]) -> None:
        self._projection_records = tuple(records)

    def _prove_generation(self) -> None:
        marker = self.marker
        if marker is None:
            return
        canonical_payload = self._canonical_payload
        canonical_records = self._canonical_records
        if canonical_payload is None:
            try:
                canonical_payload = self.paths.registry_path.read_bytes()
            except OSError as exc:
                raise _RegistryOptimisticConflict("canonical registry bytes are not provable") from exc
        if canonical_records is None:
            canonical_records = tuple(_load_toml_bytes(canonical_payload))
        try:
            packaged_payload = self.paths.packaged_registry_path.read_bytes()
        except OSError as exc:
            raise _RegistryOptimisticConflict("packaged registry bytes are not provable") from exc
        if canonical_payload != packaged_payload:
            raise RegistryControlPlaneError("canonical and packaged registry declarations are not byte-identical")
        projection_records = self._projection_records
        if projection_records is None:
            with _open_registry_read_only_connection(self.paths.db_path) as conn:
                projection_records = tuple(_load_projection_from_connection(conn))
        parity = validate_projection_parity(list(canonical_records), list(projection_records))
        if not parity.in_sync:
            raise RegistryProjectionMismatch(
                "registry declaration/projection parity failure: "
                f"missing_projection={parity.missing_in_projection}, "
                f"missing_declaration={parity.missing_in_toml}, divergences={parity.field_divergences}"
            )
        RegistryResolver(canonical_records)
        observed = (
            _sha256_bytes(canonical_payload),
            _sha256_bytes(packaged_payload),
            _projection_digest(projection_records),
        )
        expected = (marker.canonical_digest, marker.packaged_digest, marker.projection_digest)
        if observed != expected:
            raise _RegistryOptimisticConflict("live registry bytes do not match the terminal journal generation")


def _is_canonical_registry_layout(paths: RegistryPaths) -> bool:
    """Return whether all three paths are the root's authoritative generation."""

    canonical = RegistryPaths.resolve(project_root=paths.project_root)
    return (
        paths.registry_path == canonical.registry_path
        and paths.packaged_registry_path == canonical.packaged_registry_path
        and paths.db_path == canonical.db_path
    )


@contextmanager
def _exclusive_registry_read_barrier(
    *,
    project_root: Path | None = None,
    registry_path: Path | None = None,
    packaged_registry_path: Path | None = None,
    db_path: Path | None = None,
) -> Iterator[RegistryPaths]:
    """Preserve the original exclusive reader as the sole fallback path."""

    paths = RegistryPaths.resolve(
        project_root=project_root,
        registry_path=registry_path,
        packaged_registry_path=packaged_registry_path,
        db_path=db_path,
    )
    with _RegistryFileLock(paths.lock_path):
        _ensure_no_nonterminal_journal(paths.db_path)
        yield paths


@contextmanager
def registry_read_barrier(
    *,
    project_root: Path | None = None,
    registry_path: Path | None = None,
    packaged_registry_path: Path | None = None,
    db_path: Path | None = None,
) -> Iterator[_RegistryReadLease]:
    """Prove one stable terminal generation or use the exclusive fallback."""

    paths = RegistryPaths.resolve(
        project_root=project_root,
        registry_path=registry_path,
        packaged_registry_path=packaged_registry_path,
        db_path=db_path,
    )
    if not _is_canonical_registry_layout(paths):
        with _exclusive_registry_read_barrier(
            project_root=paths.project_root,
            registry_path=paths.registry_path,
            packaged_registry_path=paths.packaged_registry_path,
            db_path=paths.db_path,
        ):
            yield _RegistryReadLease(paths, None)
        return
    try:
        marker = _read_terminal_generation_marker(paths.db_path)
    except Exception:
        marker = None
    if marker is None:
        with _exclusive_registry_read_barrier(
            project_root=paths.project_root,
            registry_path=paths.registry_path,
            packaged_registry_path=paths.packaged_registry_path,
            db_path=paths.db_path,
        ):
            yield _RegistryReadLease(paths, None)
        return

    lease = _RegistryReadLease(paths, marker)
    try:
        yield lease
        lease._prove_generation()
    except Exception:
        try:
            post_marker = _read_terminal_generation_marker(paths.db_path)
        except Exception as exc:
            raise _RegistryOptimisticConflict("registry generation became unreadable") from exc
        if post_marker != marker:
            raise _RegistryOptimisticConflict("registry generation changed during the read") from None
        raise
    try:
        post_marker = _read_terminal_generation_marker(paths.db_path)
    except Exception as exc:
        raise _RegistryOptimisticConflict("registry generation became unreadable") from exc
    if post_marker != marker:
        raise _RegistryOptimisticConflict("registry generation changed during the read")


def _load_snapshot_unlocked(paths: RegistryPaths) -> RegistrySnapshot:
    canonical_bytes = paths.registry_path.read_bytes()
    packaged_bytes = paths.packaged_registry_path.read_bytes()
    if canonical_bytes != packaged_bytes:
        raise RegistryControlPlaneError("canonical and packaged registry declarations are not byte-identical")
    records = _load_toml_bytes(canonical_bytes)
    projection = _load_projection_unlocked(paths.db_path)
    parity = validate_projection_parity(records, projection)
    if not parity.in_sync:
        raise RegistryProjectionMismatch(
            "registry declaration/projection parity failure: "
            f"missing_projection={parity.missing_in_projection}, "
            f"missing_declaration={parity.missing_in_toml}, divergences={parity.field_divergences}"
        )
    resolver = RegistryResolver(records)
    declaration_digest = _sha256_bytes(canonical_bytes)
    projection_digest = _projection_digest(projection)
    generation_digest = _json_digest(
        {
            "declaration": declaration_digest,
            "packaged": _sha256_bytes(packaged_bytes),
            "projection": projection_digest,
        }
    )
    return RegistrySnapshot(
        records=tuple(records),
        declaration_digest=declaration_digest,
        packaged_digest=_sha256_bytes(packaged_bytes),
        projection_digest=projection_digest,
        generation_digest=generation_digest,
        resolver=resolver,
    )


def _try_load_registry_snapshot_optimistically(paths: RegistryPaths) -> RegistrySnapshot:
    if not _is_canonical_registry_layout(paths):
        raise _RegistryOptimisticConflict("registry paths are outside the canonical generation layout")
    try:
        marker = _read_terminal_generation_marker(paths.db_path)
    except Exception as exc:
        raise _RegistryOptimisticConflict("registry generation is not optimistically readable") from exc
    if marker is None:
        raise _RegistryOptimisticConflict("registry generation has no complete terminal marker")
    try:
        canonical_bytes = paths.registry_path.read_bytes()
        packaged_bytes = paths.packaged_registry_path.read_bytes()
        if canonical_bytes != packaged_bytes:
            raise RegistryControlPlaneError("canonical and packaged registry declarations are not byte-identical")
        records = _load_toml_bytes(canonical_bytes)
        with _open_registry_read_only_connection(paths.db_path) as conn:
            projection = _load_projection_from_connection(conn)
        parity = validate_projection_parity(records, projection)
        if not parity.in_sync:
            raise RegistryProjectionMismatch(
                "registry declaration/projection parity failure: "
                f"missing_projection={parity.missing_in_projection}, "
                f"missing_declaration={parity.missing_in_toml}, divergences={parity.field_divergences}"
            )
        resolver = RegistryResolver(records)
        declaration_digest = _sha256_bytes(canonical_bytes)
        packaged_digest = _sha256_bytes(packaged_bytes)
        projection_digest = _projection_digest(projection)
        snapshot = RegistrySnapshot(
            records=tuple(records),
            declaration_digest=declaration_digest,
            packaged_digest=packaged_digest,
            projection_digest=projection_digest,
            generation_digest=_json_digest(
                {
                    "declaration": declaration_digest,
                    "packaged": packaged_digest,
                    "projection": projection_digest,
                }
            ),
            resolver=resolver,
        )
    except Exception:
        try:
            post_marker = _read_terminal_generation_marker(paths.db_path)
        except Exception as exc:
            raise _RegistryOptimisticConflict("registry generation became unreadable") from exc
        if post_marker != marker:
            raise _RegistryOptimisticConflict("registry generation changed during the snapshot") from None
        raise
    try:
        post_marker = _read_terminal_generation_marker(paths.db_path)
    except Exception as exc:
        raise _RegistryOptimisticConflict("registry generation became unreadable") from exc
    if post_marker != marker:
        raise _RegistryOptimisticConflict("registry generation changed during the snapshot")
    if (
        snapshot.declaration_digest,
        snapshot.packaged_digest,
        snapshot.projection_digest,
    ) != (marker.canonical_digest, marker.packaged_digest, marker.projection_digest):
        raise _RegistryOptimisticConflict("snapshot does not match the terminal journal generation")
    return snapshot


def _load_registry_snapshot_exclusive(paths: RegistryPaths) -> RegistrySnapshot:
    with _exclusive_registry_read_barrier(
        project_root=paths.project_root,
        registry_path=paths.registry_path,
        packaged_registry_path=paths.packaged_registry_path,
        db_path=paths.db_path,
    ):
        return _load_snapshot_unlocked(paths)


def load_registry_snapshot(
    *,
    project_root: Path | None = None,
    registry_path: Path | None = None,
    packaged_registry_path: Path | None = None,
    db_path: Path | None = None,
) -> RegistrySnapshot:
    paths = RegistryPaths.resolve(
        project_root=project_root,
        registry_path=registry_path,
        packaged_registry_path=packaged_registry_path,
        db_path=db_path,
    )
    try:
        return _try_load_registry_snapshot_optimistically(paths)
    except _RegistryOptimisticConflict:
        return _load_registry_snapshot_exclusive(paths)


def _projection_records_from_connection(conn: sqlite3.Connection) -> list[SoTArtifact]:
    rows = conn.execute(
        "SELECT id, domain, lifecycle, storage_path, authority_spec_id, mutation_api, "
        "versioning_policy, backup_policy, health_check_function, owner_role, restore_action, "
        "depends_on, forbidden_substitutes, notes, coverage_mode "
        "FROM current_sot_artifacts ORDER BY id"
    ).fetchall()
    records: list[SoTArtifact] = []
    for row in rows:
        records.append(
            SoTArtifact(
                id=row[0],
                domain=row[1],
                lifecycle=row[2],
                storage_path=row[3],
                authority_spec_id=row[4],
                mutation_api=row[5],
                versioning_policy=row[6],
                backup_policy=row[7],
                health_check_function=row[8],
                owner_role=row[9],
                restore_action=row[10] or "manual",
                depends_on=tuple(json.loads(row[11])) if row[11] else (),
                forbidden_substitutes=tuple(json.loads(row[12])) if row[12] else (),
                notes=row[13] or "",
                coverage_mode=row[14],
            )
        )
    return records


def _append_projection_versions(
    conn: sqlite3.Connection,
    records: Sequence[SoTArtifact],
    *,
    changed_by: str,
    changed_at: str,
    change_reason: str,
    allow_removal: bool = False,
) -> tuple[str, ...]:
    existing = {record.id: record for record in _projection_records_from_connection(conn)}
    changed: list[str] = []
    for record in records:
        current = existing.get(record.id)
        if current == record:
            continue
        version = conn.execute(
            "SELECT COALESCE(MAX(version), 0) + 1 FROM sot_artifacts WHERE id = ?",
            (record.id,),
        ).fetchone()[0]
        conn.execute(
            """
            INSERT INTO sot_artifacts (
                id, version, domain, lifecycle, storage_path, authority_spec_id,
                mutation_api, versioning_policy, backup_policy, health_check_function,
                owner_role, restore_action, depends_on, forbidden_substitutes, notes,
                coverage_mode, changed_by, changed_at, change_reason
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record.id,
                version,
                record.domain,
                record.lifecycle,
                record.storage_path,
                record.authority_spec_id,
                record.mutation_api,
                record.versioning_policy,
                record.backup_policy,
                record.health_check_function,
                record.owner_role,
                record.restore_action,
                json.dumps(list(record.depends_on)) if record.depends_on else None,
                json.dumps(list(record.forbidden_substitutes)) if record.forbidden_substitutes else None,
                record.notes or None,
                record.coverage_mode,
                changed_by,
                changed_at,
                change_reason,
            ),
        )
        changed.append(record.id)
    current_ids = set(existing)
    desired_ids = {record.id for record in records}
    removed_ids = current_ids - desired_ids
    if removed_ids and not allow_removal:
        raise RegistryAuthorizationError("ordinary registry transaction cannot remove declaration identities")
    # WI-5928 Slice 1: membership removal drops the record from the derived projection
    # mirror so `current_sot_artifacts` (MAX(version) per id, no tombstone filter) no
    # longer surfaces it, matching the post-transition declaration. The removal stays
    # audited by the transaction journal (old/new digests + full desired payload) and by
    # the git-tracked canonical TOML; only the derived current-state mirror rows are dropped.
    for removed_id in sorted(removed_ids):
        conn.execute("DELETE FROM sot_artifacts WHERE id = ?", (removed_id,))
    return tuple(changed)


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


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def _tree_digest(root: Path, *, pattern: str | None = None) -> tuple[str, int]:
    entries: list[tuple[str, str, str | None, int | None]] = []
    if not root.exists():
        return _json_digest({"missing": root.as_posix()}), 0
    candidates = root.glob(pattern) if pattern else root.rglob("*")
    for path in sorted(candidates, key=lambda item: item.as_posix().casefold()):
        kind = _path_object_kind(path)
        relative = path.relative_to(root).as_posix()
        if kind == "file":
            size = path.stat().st_size
            entries.append((relative, kind, _hash_file(path), size))
        else:
            entries.append((relative, kind, None, None))
    return _json_digest(entries), sum(item[3] or 0 for item in entries)


def artifact_content_state(project_root: Path, record: SoTArtifact) -> tuple[str, str, int | None]:
    """Return content digest, object kind, and logical size without following reparse nodes."""

    if record.coverage_mode == "virtual":
        return _json_digest({"virtual": record.storage_path}), "virtual", None
    if record.coverage_mode == "glob":
        locator = PurePosixPath(record.storage_path)
        wildcard_index = next(index for index, part in enumerate(locator.parts) if any(char in part for char in "*?["))
        base = project_root.joinpath(*locator.parts[:wildcard_index])
        pattern = "/".join(locator.parts[wildcard_index:])
        digest, size = _tree_digest(base, pattern=pattern)
        return digest, "glob", size
    target = project_root / record.storage_path.rstrip("/")
    if not target.exists() and not target.is_symlink():
        return _json_digest({"missing": record.storage_path}), "missing", None
    kind = _path_object_kind(target)
    if record.coverage_mode == "opaque_container":
        return _json_digest({"opaque": record.storage_path, "kind": kind}), kind, None
    if kind == "file":
        return _hash_file(target), kind, target.stat().st_size
    if kind == "directory" and record.coverage_mode == "recursive":
        digest, size = _tree_digest(target)
        return digest, kind, size
    return _json_digest({"path": record.storage_path, "kind": kind}), kind, None


def _append_revision(
    conn: sqlite3.Connection,
    *,
    project_root: Path,
    record: SoTArtifact,
    actor_session: str,
    operation: str,
    changed_by: str,
    changed_at: str,
    change_reason: str,
    capability_hash: str | None = None,
    bridge_id: str | None = None,
    start_packet_hash: str | None = None,
    pauth_decision: str | None = None,
    journal_id: str | None = None,
    evidence_view: EvidenceView,
    evidence_source_reference: str | None = None,
) -> str:
    if evidence_view not in SUPPORTED_EVIDENCE_VIEWS:
        raise RegistryCoverageError(f"unsupported revision evidence_view: {evidence_view!r}")
    digest, object_kind, size = artifact_content_state(project_root, record)
    predecessor = conn.execute(
        "SELECT revision_id FROM sot_artifact_revisions WHERE entry_id = ? ORDER BY rowid DESC LIMIT 1",
        (record.id,),
    ).fetchone()
    revision_id = f"SOTREV-{uuid.uuid4().hex.upper()}"
    conn.execute(
        """
        INSERT INTO sot_artifact_revisions (
            revision_id, entry_id, canonical_relative_path, object_kind, content_digest,
            size_bytes, observed_at, actor_session, operation, predecessor_revision_id,
            changed_by, changed_at, change_reason, capability_hash, bridge_id,
            start_packet_hash, pauth_decision, journal_id, evidence_view,
            evidence_source_reference
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            revision_id,
            record.id,
            record.storage_path,
            object_kind,
            digest,
            size,
            changed_at,
            actor_session,
            operation,
            predecessor[0] if predecessor else None,
            changed_by,
            changed_at,
            change_reason,
            capability_hash,
            bridge_id,
            start_packet_hash,
            pauth_decision,
            journal_id,
            evidence_view,
            evidence_source_reference,
        ),
    )
    return revision_id


def _latest_revision_rows(conn: sqlite3.Connection) -> dict[str, sqlite3.Row]:
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """
        SELECT revision.* FROM sot_artifact_revisions revision
        INNER JOIN (
            SELECT entry_id, MAX(rowid) AS max_rowid
            FROM sot_artifact_revisions GROUP BY entry_id
        ) latest ON revision.rowid = latest.max_rowid
        """
    ).fetchall()
    return {row["entry_id"]: row for row in rows}


def registry_currentness(
    snapshot: RegistrySnapshot,
    *,
    project_root: Path,
    db_path: Path,
    record_ids: set[str] | None = None,
) -> dict[str, Any]:
    """Deep content-observation audit for selected declarations.

    This is audit state, not membership authority. Hot mutation/publication
    paths should select the exact records they need or use
    :func:`registry_identity_state`.
    """

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        latest = _latest_revision_rows(conn) if _table_exists(conn, "sot_artifact_revisions") else {}
    finally:
        conn.close()
    selected_records = [record for record in snapshot.records if record_ids is None or record.id in record_ids]
    missing = [record.id for record in selected_records if record.id not in latest]
    selected = [record for record in selected_records if record.id in latest]

    def content_state(record: SoTArtifact) -> tuple[SoTArtifact, str]:
        digest, _, _ = artifact_content_state(project_root, record)
        return record, digest

    if len(selected) > 32:
        with ThreadPoolExecutor(max_workers=min(32, len(selected))) as executor:
            content_states = list(executor.map(content_state, selected))
    else:
        content_states = [content_state(record) for record in selected]

    stale: list[dict[str, str]] = []
    for record, current_digest in content_states:
        row = latest.get(record.id)
        assert row is not None
        if row["content_digest"] != current_digest:
            stale.append(
                {
                    "id": record.id,
                    "observed": row["content_digest"],
                    "current": current_digest,
                }
            )
    return {"current": not stale and not missing, "missing_revisions": missing, "stale": stale}


def registry_identity_state(snapshot: RegistrySnapshot, *, project_root: Path) -> dict[str, Any]:
    """Check declaration-backed filesystem identity without hashing content."""

    root = project_root.resolve()
    missing: list[dict[str, str]] = []
    object_kind_mismatches: list[dict[str, str]] = []
    for record in snapshot.records:
        if record.lifecycle != "active" or record.coverage_mode == "virtual":
            continue
        locator = record.storage_path.rstrip("/")
        if record.coverage_mode == "glob":
            try:
                present = any(root.glob(record.storage_path))
            except (NotImplementedError, OSError, ValueError):
                present = False
            if not present:
                missing.append({"id": record.id, "path": record.storage_path})
            continue
        target = root / locator
        if not target.exists() and not target.is_symlink():
            missing.append({"id": record.id, "path": record.storage_path})
            continue
        observed_kind = _path_object_kind(target)
        if record.coverage_mode == "recursive" and observed_kind != "directory":
            object_kind_mismatches.append(
                {"id": record.id, "path": record.storage_path, "expected": "directory", "observed": observed_kind}
            )
    return {
        "current": not missing and not object_kind_mismatches,
        "missing": missing,
        "object_kind_mismatches": object_kind_mismatches,
    }


def require_current_registry_receipt(snapshot: RegistrySnapshot, *, db_path: Path) -> str:
    """Return the committed receipt bound to this exact readable generation."""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        if not _table_exists(conn, "sot_registry_transaction_journal"):
            raise RegistryAuthorizationError("registry transaction journal is absent")
        row = conn.execute(
            "SELECT receipt_digest FROM sot_registry_transaction_journal "
            "WHERE journal_state = 'committed' AND new_canonical_digest = ? "
            "AND new_packaged_digest = ? AND new_projection_digest = ? "
            "AND receipt_digest IS NOT NULL ORDER BY rowid DESC LIMIT 1",
            (
                snapshot.declaration_digest,
                snapshot.packaged_digest,
                snapshot.projection_digest,
            ),
        ).fetchone()
    finally:
        conn.close()
    if row is None:
        raise RegistryAuthorizationError("current registry generation has no exact committed transaction receipt")
    return str(row["receipt_digest"])


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


def _receipt_from_row(row: sqlite3.Row, *, idempotent_retry: bool = False) -> RegistryTransactionReceipt:
    return RegistryTransactionReceipt(
        journal_id=row["journal_id"],
        operation=row["operation"],
        receipt_digest=row["receipt_digest"],
        declaration_digest=row["new_canonical_digest"],
        projection_digest=row["new_projection_digest"],
        record_count=row["expected_record_count"],
        idempotent_retry=idempotent_retry,
    )


def _commit_prepared_generation(
    conn: sqlite3.Connection,
    row: sqlite3.Row,
    records: Sequence[SoTArtifact],
    *,
    paths: RegistryPaths,
    failure_injector: Any = None,
) -> RegistryTransactionReceipt:
    now = _utc_now()
    conn.execute("BEGIN IMMEDIATE")
    try:
        changed_ids = _append_projection_versions(
            conn,
            records,
            changed_by=row["changed_by"],
            changed_at=now,
            change_reason=row["change_reason"],
            allow_removal=(row["operation"] == "transition"),
        )
        projection = _projection_records_from_connection(conn)
        projection_digest = _projection_digest(projection)
        if projection_digest != row["new_projection_digest"]:
            raise RegistryControlPlaneError(
                f"projection digest mismatch: expected {row['new_projection_digest']}, observed {projection_digest}"
            )
        seed_all = row["operation"] == "legacy_bootstrap"
        revision_ids = set(changed_ids)
        resolver = RegistryResolver(records)
        for declaration_path in (paths.registry_path, paths.packaged_registry_path):
            relative = declaration_path.relative_to(paths.project_root).as_posix()
            declaration_record = resolver.resolve(relative)
            if declaration_record is not None:
                revision_ids.add(declaration_record.id)
        if seed_all:
            revision_ids = {record.id for record in records}
        record_by_id = {record.id: record for record in records}
        for record_id in sorted(revision_ids):
            record = record_by_id.get(record_id)
            if record is not None:
                _append_revision(
                    conn,
                    project_root=paths.project_root,
                    record=record,
                    actor_session=row["actor_session"],
                    operation=row["operation"],
                    changed_by=row["changed_by"],
                    changed_at=now,
                    change_reason=row["change_reason"],
                    bridge_id=row["bridge_id"],
                    start_packet_hash=row["start_packet_hash"],
                    journal_id=row["journal_id"],
                    evidence_view="registry_transaction",
                    evidence_source_reference=row["journal_id"],
                )
        if failure_injector is not None:
            failure_injector("after_db_update")
        receipt = _json_digest(
            {
                "seed": row["receipt_seed"],
                "journal_id": row["journal_id"],
                "declaration": row["new_canonical_digest"],
                "projection": projection_digest,
                "record_count": len(records),
            }
        )
        transition = conn.execute(
            """
            UPDATE sot_registry_transaction_journal
            SET journal_state = 'committed', completed_at = ?, changed_at = ?,
                filesystem_result = 'canonical_and_packaged_replaced',
                projection_transaction = ?, receipt_digest = ?
            WHERE journal_id = ? AND journal_state = 'prepared'
            """,
            (now, now, json.dumps({"changed_ids": sorted(changed_ids)}), receipt, row["journal_id"]),
        )
        if transition.rowcount != 1:
            raise RegistryControlPlaneError(f"journal {row['journal_id']} was not prepared")
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    if failure_injector is not None:
        failure_injector("after_journal_commit")
    committed = conn.execute(
        "SELECT * FROM sot_registry_transaction_journal WHERE journal_id = ?",
        (row["journal_id"],),
    ).fetchone()
    return _receipt_from_row(committed)


def apply_registry_transaction(
    records: Sequence[SoTArtifact],
    *,
    operation: str,
    actor_session: str,
    changed_by: str,
    change_reason: str,
    start_packet_hash: str,
    pauth_id: str,
    bridge_id: str,
    project_root: Path | None = None,
    registry_path: Path | None = None,
    packaged_registry_path: Path | None = None,
    db_path: Path | None = None,
    allow_legacy_input: bool = False,
    expected_prior_generation_digest: str | None = None,
    failure_injector: Any = None,
) -> RegistryTransactionReceipt:
    """Commit one declaration/mirror/projection generation under a prepared journal."""

    if not actor_session or not start_packet_hash or not pauth_id or not bridge_id:
        raise RegistryAuthorizationError("actor session, bridge, start packet, and PAUTH evidence are required")
    desired = tuple(records)
    if len({record.id for record in desired}) != len(desired):
        raise RegistryCoverageError("duplicate registry IDs in requested generation")
    RegistryResolver(desired)
    new_payload = serialize_registry(desired)
    new_digest = _sha256_bytes(new_payload)
    new_projection_digest = _projection_digest(desired)
    request_digest = _json_digest({"operation": operation, "records": [_record_payload(item) for item in desired]})
    paths = RegistryPaths.resolve(
        project_root=project_root,
        registry_path=registry_path,
        packaged_registry_path=packaged_registry_path,
        db_path=db_path,
    )
    with _RegistryFileLock(paths.lock_path):
        conn = sqlite3.connect(str(paths.db_path))
        conn.row_factory = sqlite3.Row
        try:
            ensure_control_plane_schema(conn)
            conn.commit()
            incomplete = conn.execute(
                "SELECT * FROM sot_registry_transaction_journal "
                "WHERE journal_state NOT IN ('committed', 'aborted') ORDER BY rowid DESC LIMIT 1"
            ).fetchone()
            if incomplete is not None:
                raise RegistryTransactionInProgress(
                    f"registry journal {incomplete['journal_id']} is {incomplete['journal_state']}"
                )
            if operation in {"amend", "transition"} and expected_prior_generation_digest is not None:
                current_canonical = paths.registry_path.read_bytes()
                current_packaged = paths.packaged_registry_path.read_bytes()
                if current_canonical != current_packaged:
                    raise RegistryControlPlaneError("pre-transaction canonical and packaged declarations differ")
                current_records = _load_toml_unlocked(
                    paths.registry_path,
                    allow_missing_coverage=allow_legacy_input,
                )
                current_projection = _load_projection_unlocked(
                    paths.db_path,
                    allow_missing_coverage=allow_legacy_input,
                )
                current_parity = validate_projection_parity(current_records, current_projection)
                if not current_parity.in_sync:
                    raise RegistryControlPlaneError("pre-transaction declaration/projection parity failure")
                current_generation_digest = _json_digest(
                    {
                        "declaration": _sha256_bytes(current_canonical),
                        "packaged": _sha256_bytes(current_packaged),
                        "projection": _projection_digest(current_projection),
                    }
                )
                if current_generation_digest != expected_prior_generation_digest:
                    raise RegistryGenerationConflict(
                        "registry generation changed after amend snapshot: "
                        f"expected {expected_prior_generation_digest}, observed {current_generation_digest}"
                    )
            retry = conn.execute(
                "SELECT * FROM sot_registry_transaction_journal "
                "WHERE operation = ? AND request_digest = ? AND journal_state = 'committed' "
                "ORDER BY rowid DESC LIMIT 1",
                (operation, request_digest),
            ).fetchone()
            if retry is not None:
                if (
                    paths.registry_path.exists()
                    and _sha256_bytes(paths.registry_path.read_bytes()) == retry["new_canonical_digest"]
                ):
                    return _receipt_from_row(retry, idempotent_retry=True)
                raise RegistryRecoveryRequired("prior receipt exists but the live declaration does not match it")
            if operation == "legacy_bootstrap":
                prior_bootstrap = conn.execute(
                    "SELECT * FROM sot_registry_transaction_journal "
                    "WHERE operation = 'legacy_bootstrap' AND journal_state = 'committed' "
                    "ORDER BY rowid DESC LIMIT 1"
                ).fetchone()
                if prior_bootstrap is not None:
                    raise RegistryAuthorizationError("legacy bootstrap input differs from the receipt-bound generation")

            old_canonical = paths.registry_path.read_bytes()
            old_packaged = paths.packaged_registry_path.read_bytes()
            if old_canonical != old_packaged:
                raise RegistryControlPlaneError("pre-transaction canonical and packaged declarations differ")
            old_records = _load_toml_unlocked(
                paths.registry_path,
                allow_missing_coverage=allow_legacy_input,
            )
            old_projection = _load_projection_unlocked(
                paths.db_path,
                allow_missing_coverage=allow_legacy_input,
            )
            parity = validate_projection_parity(old_records, old_projection)
            if not parity.in_sync:
                raise RegistryControlPlaneError("pre-transaction declaration/projection parity failure")
            prior_generation_digest = _json_digest(
                {
                    "declaration": _sha256_bytes(old_canonical),
                    "packaged": _sha256_bytes(old_packaged),
                    "projection": _projection_digest(old_projection),
                }
            )
            if (
                expected_prior_generation_digest is not None
                and prior_generation_digest != expected_prior_generation_digest
            ):
                error_type = (
                    RegistryGenerationConflict if operation in {"amend", "transition"} else RegistryAuthorizationError
                )
                raise error_type(
                    "registry generation changed after dry-run: "
                    f"expected {expected_prior_generation_digest}, observed {prior_generation_digest}"
                )
            old_ids = {record.id for record in old_records}
            desired_ids = {record.id for record in desired}
            # WI-5928 Slice 1: the authorized `transition` operation is the sole lawful
            # path that may drop a registry identity (membership removal). register/amend/
            # legacy_bootstrap remain add-or-change-only.
            if operation != "transition" and (old_ids - desired_ids):
                raise RegistryAuthorizationError("register/amend cannot remove a registry identity")

            journal_id = f"SOTTXN-{uuid.uuid4().hex.upper()}"
            now = _utc_now()
            receipt_seed = _json_digest(
                {
                    "journal_id": journal_id,
                    "old": _sha256_bytes(old_canonical),
                    "new": new_digest,
                    "request": request_digest,
                }
            )
            journal_payload = json.dumps(
                {"records": [_record_payload(record) for record in desired]},
                sort_keys=True,
                separators=(",", ":"),
            )
            conn.execute(
                """
                INSERT INTO sot_registry_transaction_journal (
                    journal_id, operation, entry_id, intent_recorded_at, declaration_digest,
                    filesystem_result, projection_transaction, journal_state, actor_session,
                    changed_by, changed_at, change_reason, old_canonical_digest,
                    new_canonical_digest, old_packaged_digest, new_packaged_digest,
                    old_projection_digest, new_projection_digest, request_digest, payload_json,
                    expected_record_count, start_packet_hash, pauth_id, bridge_id, receipt_seed
                ) VALUES (
                    ?, ?, NULL, ?, ?, 'pending', 'pending', 'prepared', ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    journal_id,
                    operation,
                    now,
                    new_digest,
                    actor_session,
                    changed_by,
                    now,
                    change_reason,
                    _sha256_bytes(old_canonical),
                    new_digest,
                    _sha256_bytes(old_packaged),
                    new_digest,
                    _projection_digest(old_projection),
                    new_projection_digest,
                    request_digest,
                    journal_payload,
                    len(desired),
                    start_packet_hash,
                    pauth_id,
                    bridge_id,
                    receipt_seed,
                ),
            )
            conn.commit()
            if failure_injector is not None:
                failure_injector("after_prepare")
            _atomic_replace(paths.registry_path, new_payload)
            if failure_injector is not None:
                failure_injector("after_canonical_replace")
            _atomic_replace(paths.packaged_registry_path, new_payload)
            if failure_injector is not None:
                failure_injector("after_packaged_replace")
            row = conn.execute(
                "SELECT * FROM sot_registry_transaction_journal WHERE journal_id = ?",
                (journal_id,),
            ).fetchone()
            return _commit_prepared_generation(
                conn,
                row,
                desired,
                paths=paths,
                failure_injector=failure_injector,
            )
        finally:
            conn.close()


def recover_registry(
    *,
    project_root: Path | None = None,
    registry_path: Path | None = None,
    packaged_registry_path: Path | None = None,
    db_path: Path | None = None,
) -> RegistryTransactionReceipt | None:
    """Recover the latest incomplete transaction without guessing a mixed state."""

    paths = RegistryPaths.resolve(
        project_root=project_root,
        registry_path=registry_path,
        packaged_registry_path=packaged_registry_path,
        db_path=db_path,
    )
    with _RegistryFileLock(paths.lock_path):
        conn = sqlite3.connect(str(paths.db_path))
        conn.row_factory = sqlite3.Row
        try:
            ensure_control_plane_schema(conn)
            conn.commit()
            row = conn.execute(
                "SELECT * FROM sot_registry_transaction_journal "
                "WHERE journal_state NOT IN ('committed', 'aborted') ORDER BY rowid DESC LIMIT 1"
            ).fetchone()
            if row is None:
                latest = conn.execute(
                    "SELECT * FROM sot_registry_transaction_journal "
                    "WHERE journal_state = 'committed' ORDER BY rowid DESC LIMIT 1"
                ).fetchone()
                return _receipt_from_row(latest, idempotent_retry=True) if latest else None
            canonical_payload = paths.registry_path.read_bytes()
            packaged_payload = paths.packaged_registry_path.read_bytes()
            canonical_digest = _sha256_bytes(canonical_payload)
            packaged_digest = _sha256_bytes(packaged_payload)
            projection = _load_projection_unlocked(paths.db_path, allow_missing_coverage=True)
            projection_digest = _projection_digest(projection)
            old_files = (
                canonical_digest == row["old_canonical_digest"] and packaged_digest == row["old_packaged_digest"]
            )
            new_files = (
                canonical_digest == row["new_canonical_digest"] and packaged_digest == row["new_packaged_digest"]
            )
            if old_files and projection_digest == row["old_projection_digest"]:
                now = _utc_now()
                conn.execute(
                    "UPDATE sot_registry_transaction_journal SET journal_state = 'aborted', "
                    "completed_at = ?, changed_at = ?, filesystem_result = 'old_generation_intact' "
                    "WHERE journal_id = ?",
                    (now, now, row["journal_id"]),
                )
                conn.commit()
                return None
            canonical_new_packaged_old = (
                canonical_digest == row["new_canonical_digest"]
                and packaged_digest == row["old_packaged_digest"]
                and projection_digest == row["old_projection_digest"]
            )
            if canonical_new_packaged_old:
                payload = json.loads(row["payload_json"])
                records = tuple(_record_from_payload(item) for item in payload["records"])
                reviewed_payload = serialize_registry(records)
                payload_is_journal_bound = (
                    reviewed_payload == canonical_payload
                    and _sha256_bytes(reviewed_payload) == row["new_canonical_digest"]
                    and _sha256_bytes(reviewed_payload) == row["new_packaged_digest"]
                    and _projection_digest(records) == row["new_projection_digest"]
                    and len(records) == row["expected_record_count"]
                )
                if payload_is_journal_bound:
                    _atomic_replace(paths.packaged_registry_path, reviewed_payload)
                    return _commit_prepared_generation(conn, row, records, paths=paths)

            if new_files and projection_digest == row["old_projection_digest"]:
                payload = json.loads(row["payload_json"])
                records = tuple(_record_from_payload(item) for item in payload["records"])
                return _commit_prepared_generation(conn, row, records, paths=paths)
            if new_files and projection_digest == row["new_projection_digest"]:
                receipt = row["receipt_digest"] or _json_digest(
                    {
                        "seed": row["receipt_seed"],
                        "journal_id": row["journal_id"],
                        "declaration": row["new_canonical_digest"],
                        "projection": projection_digest,
                        "record_count": row["expected_record_count"],
                    }
                )
                now = _utc_now()
                conn.execute(
                    "UPDATE sot_registry_transaction_journal SET journal_state = 'committed', "
                    "completed_at = ?, changed_at = ?, receipt_digest = ? WHERE journal_id = ?",
                    (now, now, receipt, row["journal_id"]),
                )
                conn.commit()
                committed = conn.execute(
                    "SELECT * FROM sot_registry_transaction_journal WHERE journal_id = ?",
                    (row["journal_id"],),
                ).fetchone()
                return _receipt_from_row(committed)
            message = (
                "registry recovery found a mixed or unknown generation: "
                f"canonical={canonical_digest}, packaged={packaged_digest}, projection={projection_digest}"
            )
            conn.execute(
                "UPDATE sot_registry_transaction_journal SET journal_state = 'repair_required', "
                "error_message = ?, changed_at = ? WHERE journal_id = ?",
                (message, _utc_now(), row["journal_id"]),
            )
            conn.commit()
            raise RegistryRecoveryRequired(message)
        finally:
            conn.close()


def bootstrap_legacy_registry(
    *,
    actor_session: str,
    changed_by: str,
    change_reason: str,
    start_packet_hash: str,
    pauth_id: str,
    bridge_id: str,
    project_root: Path | None = None,
    registry_path: Path | None = None,
    packaged_registry_path: Path | None = None,
    db_path: Path | None = None,
    implementation_artifacts: Sequence[SoTArtifact] = IMPLEMENTATION_ARTIFACTS,
) -> RegistryTransactionReceipt:
    """Apply the exact reviewed 50-record coverage map and admit implementation artifacts."""

    paths = RegistryPaths.resolve(
        project_root=project_root,
        registry_path=registry_path,
        packaged_registry_path=packaged_registry_path,
        db_path=db_path,
    )
    with _RegistryFileLock(paths.lock_path):
        _ensure_no_nonterminal_journal(paths.db_path)
        existing = _load_toml_unlocked(paths.registry_path, allow_missing_coverage=True)
    existing_ids = {record.id for record in existing}
    legacy_ids = existing_ids & set(LEGACY_COVERAGE_MODES)
    if legacy_ids != set(LEGACY_COVERAGE_MODES):
        missing = sorted(set(LEGACY_COVERAGE_MODES) - legacy_ids)
        unexpected = sorted(legacy_ids - set(LEGACY_COVERAGE_MODES))
        raise RegistryCoverageError(f"legacy bootstrap set mismatch: missing={missing}, unexpected={unexpected}")
    extras = existing_ids - set(LEGACY_COVERAGE_MODES)
    approved_extra_ids = {record.id for record in implementation_artifacts}
    if extras - approved_extra_ids:
        raise RegistryCoverageError(f"unreviewed pre-bootstrap registry IDs: {sorted(extras - approved_extra_ids)}")
    mapped = [
        replace(record, coverage_mode=LEGACY_COVERAGE_MODES[record.id])
        if record.id in LEGACY_COVERAGE_MODES
        else record
        for record in existing
    ]
    by_id = {record.id: record for record in mapped}
    for artifact in implementation_artifacts:
        target = paths.project_root / artifact.storage_path
        if artifact.id not in by_id and not target.exists():
            raise RegistryCoverageError(f"implementation artifact does not exist: {artifact.storage_path}")
        by_id.setdefault(artifact.id, artifact)
    desired = [by_id[record.id] for record in mapped]
    desired.extend(artifact for artifact in implementation_artifacts if artifact.id not in existing_ids)
    return apply_registry_transaction(
        desired,
        operation="legacy_bootstrap",
        actor_session=actor_session,
        changed_by=changed_by,
        change_reason=change_reason,
        start_packet_hash=start_packet_hash,
        pauth_id=pauth_id,
        bridge_id=bridge_id,
        project_root=paths.project_root,
        registry_path=paths.registry_path,
        packaged_registry_path=paths.packaged_registry_path,
        db_path=paths.db_path,
        allow_legacy_input=True,
    )


def _registration_dry_run_receipt(
    *,
    starting_generation_digest: str,
    candidate_manifest_sha256: str,
    record_manifest_sha256: str,
    observer_input_digests: Mapping[str, str] | None,
    reconciliation_evidence_digest: str | None,
    desired_declaration_digest: str,
    desired_projection_digest: str,
    desired_record_count: int,
    candidate_count: int,
    actor_session: str,
    start_packet_hash: str,
    pauth_id: str,
    bridge_id: str,
) -> str:
    return _json_digest(
        {
            "operation": "register",
            "starting_generation_digest": starting_generation_digest,
            "candidate_manifest_sha256": candidate_manifest_sha256,
            "record_manifest_sha256": record_manifest_sha256,
            "observer_input_digests": dict(sorted((observer_input_digests or {}).items())),
            "reconciliation_evidence_digest": reconciliation_evidence_digest,
            "desired_declaration_digest": desired_declaration_digest,
            "desired_projection_digest": desired_projection_digest,
            "desired_record_count": desired_record_count,
            "candidate_count": candidate_count,
            "authorization": {
                "actor_session": actor_session,
                "start_packet_hash": start_packet_hash,
                "pauth_id": pauth_id,
                "bridge_id": bridge_id,
            },
        }
    )


def register_artifacts(
    records: Sequence[SoTArtifact],
    *,
    actor_session: str,
    changed_by: str,
    change_reason: str,
    start_packet_hash: str,
    pauth_id: str,
    bridge_id: str,
    project_root: Path | None = None,
    registry_path: Path | None = None,
    packaged_registry_path: Path | None = None,
    db_path: Path | None = None,
    expected_generation_digest: str | None = None,
    candidate_manifest_sha256: str | None = None,
    observer_input_digests: Mapping[str, str] | None = None,
    reconciliation_evidence_digest: str | None = None,
    dry_run_receipt: str | None = None,
) -> RegistryTransactionReceipt:
    if (expected_generation_digest is None) != (dry_run_receipt is None):
        raise RegistryAuthorizationError("expected generation and dry-run receipt must be supplied together")
    if (observer_input_digests is None) != (reconciliation_evidence_digest is None):
        raise RegistryAuthorizationError(
            "observer input digests and reconciliation evidence digest must be supplied together"
        )
    snapshot = load_registry_snapshot(
        project_root=project_root,
        registry_path=registry_path,
        packaged_registry_path=packaged_registry_path,
        db_path=db_path,
    )
    additions = tuple(records)
    existing = {record.id: record for record in snapshot.records}
    duplicate_ids = existing.keys() & {record.id for record in additions}
    if duplicate_ids:
        if duplicate_ids != {record.id for record in additions}:
            raise RegistryAuthorizationError(f"registration batch mixes existing and new IDs: {sorted(duplicate_ids)}")
        mismatched = [
            record.id for record in additions if _record_payload(existing[record.id]) != _record_payload(record)
        ]
        if mismatched:
            raise RegistryAuthorizationError(
                f"existing registry IDs differ from the requested retry: {sorted(mismatched)}"
            )
        if expected_generation_digest is not None:
            record_rows = [
                _record_payload(record) for record in sorted(additions, key=lambda item: item.storage_path.casefold())
            ]
            record_manifest_digest = _json_digest(record_rows)
            expected_retry_receipt = _registration_dry_run_receipt(
                starting_generation_digest=expected_generation_digest,
                candidate_manifest_sha256=candidate_manifest_sha256 or record_manifest_digest,
                record_manifest_sha256=record_manifest_digest,
                observer_input_digests=observer_input_digests,
                reconciliation_evidence_digest=reconciliation_evidence_digest,
                desired_declaration_digest=snapshot.declaration_digest,
                desired_projection_digest=snapshot.projection_digest,
                desired_record_count=len(snapshot.records),
                candidate_count=len(additions),
                actor_session=actor_session,
                start_packet_hash=start_packet_hash,
                pauth_id=pauth_id,
                bridge_id=bridge_id,
            )
            if dry_run_receipt != expected_retry_receipt:
                raise RegistryAuthorizationError("registration retry does not match the exact dry-run receipt")
        # The transaction layer recognizes the exact full-generation request
        # before checking the now-stale preimage digest, making an interrupted
        # caller retry deterministic and side-effect free.
        return apply_registry_transaction(
            snapshot.records,
            operation="register",
            actor_session=actor_session,
            changed_by=changed_by,
            change_reason=change_reason,
            start_packet_hash=start_packet_hash,
            pauth_id=pauth_id,
            bridge_id=bridge_id,
            project_root=project_root,
            registry_path=registry_path,
            packaged_registry_path=packaged_registry_path,
            db_path=db_path,
            expected_prior_generation_digest=expected_generation_digest,
        )
    preview = preview_registry_registration(
        additions,
        actor_session=actor_session,
        start_packet_hash=start_packet_hash,
        pauth_id=pauth_id,
        bridge_id=bridge_id,
        candidate_manifest_sha256=candidate_manifest_sha256,
        observer_input_digests=observer_input_digests,
        reconciliation_evidence_digest=reconciliation_evidence_digest,
        project_root=project_root,
        registry_path=registry_path,
        packaged_registry_path=packaged_registry_path,
        db_path=db_path,
    )
    if expected_generation_digest is not None:
        if expected_generation_digest != preview.starting_generation_digest:
            raise RegistryAuthorizationError("batch plan starting generation does not match the live registry")
        if dry_run_receipt != preview.dry_run_receipt:
            raise RegistryAuthorizationError("batch apply does not match the exact dry-run receipt")
    return apply_registry_transaction(
        (*snapshot.records, *additions),
        operation="register",
        actor_session=actor_session,
        changed_by=changed_by,
        change_reason=change_reason,
        start_packet_hash=start_packet_hash,
        pauth_id=pauth_id,
        bridge_id=bridge_id,
        project_root=project_root,
        registry_path=registry_path,
        packaged_registry_path=packaged_registry_path,
        db_path=db_path,
        expected_prior_generation_digest=expected_generation_digest,
    )


def preview_registry_registration(
    records: Sequence[SoTArtifact],
    *,
    actor_session: str,
    start_packet_hash: str,
    pauth_id: str,
    bridge_id: str,
    candidate_manifest_sha256: str | None = None,
    observer_input_digests: Mapping[str, str] | None = None,
    reconciliation_evidence_digest: str | None = None,
    project_root: Path | None = None,
    registry_path: Path | None = None,
    packaged_registry_path: Path | None = None,
    db_path: Path | None = None,
) -> RegistryRegistrationPreview:
    """Bind an additive batch and its authorization to one readable generation."""

    if (observer_input_digests is None) != (reconciliation_evidence_digest is None):
        raise RegistryAuthorizationError(
            "observer input digests and reconciliation evidence digest must be supplied together"
        )

    snapshot = load_registry_snapshot(
        project_root=project_root,
        registry_path=registry_path,
        packaged_registry_path=packaged_registry_path,
        db_path=db_path,
    )
    additions = tuple(records)
    existing_ids = {record.id for record in snapshot.records}
    duplicates = existing_ids & {record.id for record in additions}
    if duplicates:
        raise RegistryAuthorizationError(f"registry IDs already exist: {sorted(duplicates)}")
    desired = (*snapshot.records, *additions)
    RegistryResolver(desired)
    record_rows = [
        _record_payload(record) for record in sorted(additions, key=lambda item: item.storage_path.casefold())
    ]
    record_manifest_digest = _json_digest(record_rows)
    manifest_digest = candidate_manifest_sha256 or record_manifest_digest
    desired_declaration_digest = _sha256_bytes(serialize_registry(desired))
    desired_projection_digest = _projection_digest(desired)
    canonical_observer_digests = dict(sorted((observer_input_digests or {}).items()))
    receipt = _registration_dry_run_receipt(
        starting_generation_digest=snapshot.generation_digest,
        candidate_manifest_sha256=manifest_digest,
        record_manifest_sha256=record_manifest_digest,
        observer_input_digests=canonical_observer_digests,
        reconciliation_evidence_digest=reconciliation_evidence_digest,
        desired_declaration_digest=desired_declaration_digest,
        desired_projection_digest=desired_projection_digest,
        desired_record_count=len(desired),
        candidate_count=len(additions),
        actor_session=actor_session,
        start_packet_hash=start_packet_hash,
        pauth_id=pauth_id,
        bridge_id=bridge_id,
    )
    return RegistryRegistrationPreview(
        starting_generation_digest=snapshot.generation_digest,
        candidate_manifest_sha256=manifest_digest,
        observer_input_digests=canonical_observer_digests,
        reconciliation_evidence_digest=reconciliation_evidence_digest,
        desired_declaration_digest=desired_declaration_digest,
        desired_projection_digest=desired_projection_digest,
        desired_record_count=len(desired),
        candidate_count=len(additions),
        dry_run_receipt=receipt,
    )


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


def amend_artifact(
    artifact_id: str,
    changes: Mapping[str, Any],
    *,
    actor_session: str,
    changed_by: str,
    change_reason: str,
    start_packet_hash: str,
    pauth_id: str,
    bridge_id: str,
    project_root: Path | None = None,
    registry_path: Path | None = None,
    packaged_registry_path: Path | None = None,
    db_path: Path | None = None,
) -> RegistryTransactionReceipt:
    forbidden = set(changes) - _AMENDABLE_FIELDS
    if forbidden:
        raise RegistryAuthorizationError(
            "identity, locator, coverage, lifecycle, move, rename, and deletion changes require transition authority: "
            f"{sorted(forbidden)}"
        )
    normalized = dict(changes)
    for field_name in ("depends_on", "forbidden_substitutes"):
        if field_name in normalized:
            normalized[field_name] = tuple(normalized[field_name])

    for _attempt in range(8):
        snapshot = load_registry_snapshot(
            project_root=project_root,
            registry_path=registry_path,
            packaged_registry_path=packaged_registry_path,
            db_path=db_path,
        )
        found = False
        desired: list[SoTArtifact] = []
        for record in snapshot.records:
            if record.id != artifact_id:
                desired.append(record)
                continue
            found = True
            desired.append(replace(record, **normalized))
        if not found:
            raise RegistryCoverageError(f"registry ID not found: {artifact_id}")
        try:
            return apply_registry_transaction(
                desired,
                operation="amend",
                actor_session=actor_session,
                changed_by=changed_by,
                change_reason=change_reason,
                start_packet_hash=start_packet_hash,
                pauth_id=pauth_id,
                bridge_id=bridge_id,
                project_root=project_root,
                registry_path=registry_path,
                packaged_registry_path=packaged_registry_path,
                db_path=db_path,
                expected_prior_generation_digest=snapshot.generation_digest,
            )
        except RegistryGenerationConflict:
            if _attempt == 7:
                raise

    raise AssertionError("unreachable amend retry state")


# WI-5928 Slice 1: registry identity-transition surface
# (DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001). Slice 1 delivers the
# membership-set and in-place coverage-mode transition path only; move, rename,
# and delete-to-quarantine transitions are deferred to a later slice.
_SLICE1_TRANSITION_OPERATIONS: frozenset[str] = frozenset(
    {"membership_set", "coverage_mode", "coverage_and_membership"}
)
_DEFERRED_TRANSITION_OPERATIONS: frozenset[str] = frozenset({"move", "rename", "delete", "delete_to_quarantine"})
_VALID_TRANSITION_COVERAGE_MODES: frozenset[str] = frozenset({"exact", "recursive", "glob", "opaque_container"})
_TRANSITION_REQUEST_MAX_TTL_SECONDS = 86_400


def transition_request(
    *,
    entry_id: str,
    operation: str,
    owner_evidence: Mapping[str, Any],
    actor_session: str,
    changed_by: str,
    change_reason: str,
    start_packet_hash: str,
    pauth_id: str,
    bridge_id: str,
    coverage_changes: Mapping[str, str] | None = None,
    removals: Sequence[str] = (),
    destination: Mapping[str, Any] | None = None,
    expiry_seconds: int = 900,
    project_root: Path | None = None,
    registry_path: Path | None = None,
    packaged_registry_path: Path | None = None,
    db_path: Path | None = None,
) -> dict[str, Any]:
    """Record a digest-bound registry identity-transition request (Slice 1).

    Binds ``entry_id``, ``source_locator``, the current generation digest, the
    transition ``operation``, the ``destination`` summary, ``owner_evidence``,
    the ``intended_membership_result`` (coverage changes plus membership
    removals), and an expiry into the dedicated
    ``sot_registry_transition_requests`` capability table. That table (an
    active/consumed/expiry lifecycle mirroring the observation- and
    publication-capability tables) is used INSTEAD of the transaction journal so
    a pending request never leaves ``sot_registry_transaction_journal`` in a
    non-terminal state that would trip ``apply_registry_transaction``'s
    incomplete-journal gate.

    Slice 1 supports membership removals and in-place coverage-mode changes only;
    move/rename/delete-to-quarantine operations are rejected pending a later
    slice.
    """

    if operation in _DEFERRED_TRANSITION_OPERATIONS:
        raise RegistryAuthorizationError(
            f"transition operation {operation!r} (move/rename/delete) is deferred to a later slice"
        )
    if operation not in _SLICE1_TRANSITION_OPERATIONS:
        raise RegistryAuthorizationError(
            f"unsupported transition operation {operation!r}; expected one of {sorted(_SLICE1_TRANSITION_OPERATIONS)}"
        )
    if not all((actor_session, start_packet_hash, pauth_id, bridge_id)):
        raise RegistryAuthorizationError("actor session, bridge, start packet, and PAUTH evidence are required")
    if not owner_evidence:
        raise RegistryAuthorizationError("transition request requires non-empty owner evidence")
    if expiry_seconds <= 0 or expiry_seconds > _TRANSITION_REQUEST_MAX_TTL_SECONDS:
        raise RegistryAuthorizationError(
            f"transition request TTL must be between 1 and {_TRANSITION_REQUEST_MAX_TTL_SECONDS} seconds"
        )
    normalized_coverage_changes = dict(coverage_changes or {})
    removal_ids = tuple(dict.fromkeys(removals))
    if not normalized_coverage_changes and not removal_ids:
        raise RegistryAuthorizationError("transition request must change coverage or remove at least one member")
    for target_id, target_mode in normalized_coverage_changes.items():
        if target_mode not in _VALID_TRANSITION_COVERAGE_MODES:
            raise RegistryCoverageError(f"unsupported target coverage_mode {target_mode!r} for {target_id!r}")

    paths = RegistryPaths.resolve(
        project_root=project_root,
        registry_path=registry_path,
        packaged_registry_path=packaged_registry_path,
        db_path=db_path,
    )
    with _RegistryFileLock(paths.lock_path):
        _ensure_no_nonterminal_journal(paths.db_path)
        snapshot = _load_snapshot_unlocked(paths)
        by_id = {record.id: record for record in snapshot.records}
        if entry_id not in by_id:
            raise RegistryCoverageError(f"transition entry id not found in registry: {entry_id}")
        unknown = sorted(rid for rid in (*normalized_coverage_changes, *removal_ids) if rid not in by_id)
        if unknown:
            raise RegistryCoverageError(f"transition targets are not registered: {unknown}")
        source_locator = by_id[entry_id].storage_path
        intended_membership_result = {
            "coverage_changes": dict(sorted(normalized_coverage_changes.items())),
            "removals": sorted(removal_ids),
        }
        resolved_destination = dict(destination or {})
        if "coverage_mode" not in resolved_destination and entry_id in normalized_coverage_changes:
            resolved_destination["coverage_mode"] = normalized_coverage_changes[entry_id]
        current_revision_digest = snapshot.generation_digest
        request_digest = _json_digest(
            {
                "entry_id": entry_id,
                "operation": operation,
                "source_locator": source_locator,
                "current_revision_digest": current_revision_digest,
                "destination": resolved_destination,
                "intended_membership_result": intended_membership_result,
            }
        )
        request_id = f"REGTXNREQ-{uuid.uuid4().hex.upper()}"
        created = datetime.now(UTC)
        created_at = created.strftime("%Y-%m-%dT%H:%M:%SZ")
        expires_at = (created + timedelta(seconds=expiry_seconds)).strftime("%Y-%m-%dT%H:%M:%SZ")
        conn = sqlite3.connect(str(paths.db_path))
        try:
            ensure_control_plane_schema(conn)
            conn.execute(
                """
                INSERT INTO sot_registry_transition_requests (
                    request_id, request_digest, entry_id, source_locator,
                    current_revision_digest, operation, destination, owner_evidence,
                    intended_membership_result, request_state, expires_at, created_at,
                    actor_session, changed_by, changed_at, change_reason,
                    bridge_id, pauth_id, start_packet_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'active', ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    request_id,
                    request_digest,
                    entry_id,
                    source_locator,
                    current_revision_digest,
                    operation,
                    json.dumps(resolved_destination, sort_keys=True, separators=(",", ":")),
                    json.dumps(dict(owner_evidence), sort_keys=True, separators=(",", ":")),
                    json.dumps(intended_membership_result, sort_keys=True, separators=(",", ":")),
                    expires_at,
                    created_at,
                    actor_session,
                    changed_by,
                    created_at,
                    change_reason,
                    bridge_id,
                    pauth_id,
                    start_packet_hash,
                ),
            )
            conn.commit()
        finally:
            conn.close()
    return {
        "request_id": request_id,
        "request_digest": request_digest,
        "entry_id": entry_id,
        "operation": operation,
        "source_locator": source_locator,
        "current_revision_digest": current_revision_digest,
        "intended_membership_result": intended_membership_result,
        "destination": resolved_destination,
        "expires_at": expires_at,
        "request_state": "active",
    }


def transition_apply(
    *,
    request_id: str,
    ops_envelope: Mapping[str, Any],
    apply_authorization: Mapping[str, Any],
    actor_session: str,
    changed_by: str,
    change_reason: str,
    start_packet_hash: str,
    pauth_id: str,
    bridge_id: str,
    project_root: Path | None = None,
    registry_path: Path | None = None,
    packaged_registry_path: Path | None = None,
    db_path: Path | None = None,
) -> RegistryTransactionReceipt:
    """Consume an active transition request and commit the identity transition.

    Enforces the four DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001 apply
    gates and fails closed on any of them:

    1. OPS envelope -- ``ops_envelope`` must be present and declare an ops
       context (``envelope_id`` or ``activity == "ops"``).
    2. Matching active request -- ``request_id`` must resolve to an ``active``,
       unexpired row in ``sot_registry_transition_requests``.
    3. Matching independent bridge GO -- ``apply_authorization`` must carry
       ``status == "GO"`` from an ``author_session_context_id`` that differs
       from ``actor_session`` (self-review is invalid). This is a distinct
       authorization from the proposal GO that built the surface: each live
       apply requires its own independent GO.
    4. Fresh operation-time revalidation -- the live registry generation digest
       must still equal the digest bound at request time; otherwise the request
       is stale and the apply is rejected.

    The desired record set (membership removals plus coverage-mode changes) is
    then committed through the existing ``apply_registry_transaction`` with
    ``operation="transition"`` -- reusing the lock, journal, digest,
    projection-parity, and RegistryResolver overlap validation with no new
    transaction machinery. Runtime hook / shared identity-authorization wiring
    is deferred to a later slice; this function is the library surface those
    call sites will bind to.
    """

    if not all((actor_session, start_packet_hash, pauth_id, bridge_id)):
        raise RegistryAuthorizationError("actor session, bridge, start packet, and PAUTH evidence are required")
    # Gate 1: OPS envelope.
    if not ops_envelope or not (ops_envelope.get("envelope_id") or ops_envelope.get("activity") == "ops"):
        raise RegistryAuthorizationError("transition apply requires an ops envelope")
    # Gate 3: matching independent bridge GO (self-review is invalid).
    authorization = dict(apply_authorization or {})
    if str(authorization.get("status") or "") != "GO" or not str(authorization.get("bridge_id") or ""):
        raise RegistryAuthorizationError("transition apply requires a matching independent bridge GO")
    go_author_session = str(authorization.get("author_session_context_id") or "")
    if not go_author_session or go_author_session == actor_session:
        raise RegistryAuthorizationError(
            "transition apply GO must come from an independent session context (self-review is invalid)"
        )

    paths = RegistryPaths.resolve(
        project_root=project_root,
        registry_path=registry_path,
        packaged_registry_path=packaged_registry_path,
        db_path=db_path,
    )
    # Gate 2: matching active request.
    conn = sqlite3.connect(str(paths.db_path))
    conn.row_factory = sqlite3.Row
    try:
        ensure_control_plane_schema(conn)
        conn.commit()
        request_row = conn.execute(
            "SELECT * FROM sot_registry_transition_requests WHERE request_id = ?",
            (request_id,),
        ).fetchone()
    finally:
        conn.close()
    if request_row is None or request_row["request_state"] != "active":
        raise RegistryAuthorizationError(f"no matching active transition request: {request_id}")
    if _utc_now() > str(request_row["expires_at"]):
        raise RegistryAuthorizationError(f"transition request expired: {request_id}")

    bound_digest = str(request_row["current_revision_digest"])
    intended = json.loads(request_row["intended_membership_result"])
    coverage_changes = dict(intended.get("coverage_changes") or {})
    removal_ids = set(intended.get("removals") or ())

    # Gate 4: fresh operation-time revalidation of the source generation digest.
    snapshot = load_registry_snapshot(
        project_root=project_root,
        registry_path=registry_path,
        packaged_registry_path=packaged_registry_path,
        db_path=db_path,
    )
    if snapshot.generation_digest != bound_digest:
        raise RegistryGenerationConflict(
            "transition source revision digest is stale: "
            f"expected {bound_digest}, observed {snapshot.generation_digest}"
        )

    desired: list[SoTArtifact] = []
    for record in snapshot.records:
        if record.id in removal_ids:
            continue
        if record.id in coverage_changes:
            desired.append(replace(record, coverage_mode=coverage_changes[record.id]))
        else:
            desired.append(record)

    receipt = apply_registry_transaction(
        desired,
        operation="transition",
        actor_session=actor_session,
        changed_by=changed_by,
        change_reason=change_reason,
        start_packet_hash=start_packet_hash,
        pauth_id=pauth_id,
        bridge_id=bridge_id,
        project_root=project_root,
        registry_path=registry_path,
        packaged_registry_path=packaged_registry_path,
        db_path=db_path,
        expected_prior_generation_digest=bound_digest,
    )

    consumed_at = _utc_now()
    conn = sqlite3.connect(str(paths.db_path))
    try:
        ensure_control_plane_schema(conn)
        conn.execute(
            "UPDATE sot_registry_transition_requests "
            "SET request_state = 'consumed', consumed_at = ?, changed_at = ?, result_digest = ? "
            "WHERE request_id = ? AND request_state = 'active'",
            (consumed_at, consumed_at, receipt.receipt_digest, request_id),
        )
        conn.commit()
    finally:
        conn.close()
    return receipt


def _normalize_event_paths(project_root: Path, values: Sequence[str | Path]) -> tuple[str, ...]:
    normalized: set[str] = set()
    root = project_root.resolve()
    for value in values:
        candidate = Path(value)
        if candidate.is_absolute():
            resolved = candidate.resolve()
            try:
                relative = resolved.relative_to(root)
            except ValueError as exc:
                raise RegistryAuthorizationError(f"observation path escapes project root: {value}") from exc
        else:
            relative = candidate
        rendered = relative.as_posix().strip("/")
        if not rendered or any(part in {".", ".."} for part in PurePosixPath(rendered).parts):
            raise RegistryAuthorizationError(f"unsafe observation path: {value}")
        normalized.add(rendered)
    if not normalized:
        raise RegistryAuthorizationError("at least one exact observation path is required")
    return tuple(sorted(normalized, key=str.casefold))


def _event_preimages(project_root: Path, paths: Sequence[str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for relative in paths:
        target = project_root / relative
        if not target.exists() and not target.is_symlink():
            result[relative] = _json_digest({"missing": relative})
        elif _path_object_kind(target) == "file":
            result[relative] = _hash_file(target)
        else:
            result[relative] = _json_digest({"path": relative, "kind": _path_object_kind(target)})
    return result


def mint_observation_capability(
    *,
    target_paths: Sequence[str | Path],
    session_id: str,
    tool_event_id: str,
    bridge_id: str,
    start_packet_hash: str,
    pauth_decision: Mapping[str, Any],
    operation: str,
    authorized: bool,
    project_root: Path | None = None,
    registry_path: Path | None = None,
    packaged_registry_path: Path | None = None,
    db_path: Path | None = None,
    ttl_seconds: int = 300,
) -> dict[str, Any]:
    """Mint a short-lived capability only after the caller's pre-tool decision passed."""

    if not authorized:
        raise RegistryAuthorizationError("denied pre-tool decisions cannot mint observation capability")
    if not all((session_id, tool_event_id, bridge_id, start_packet_hash, operation)):
        raise RegistryAuthorizationError("observation capability bindings must be non-empty")
    if ttl_seconds <= 0 or ttl_seconds > 900:
        raise RegistryAuthorizationError("observation capability TTL must be between 1 and 900 seconds")
    paths = RegistryPaths.resolve(
        project_root=project_root,
        registry_path=registry_path,
        packaged_registry_path=packaged_registry_path,
        db_path=db_path,
    )
    with _RegistryFileLock(paths.lock_path):
        _ensure_no_nonterminal_journal(paths.db_path)
        snapshot = _load_snapshot_unlocked(paths)
        normalized = _normalize_event_paths(paths.project_root, target_paths)
        for relative in normalized:
            if snapshot.resolver.resolve(relative) is None:
                raise RegistryAuthorizationError(f"cannot mint observation for unregistered path: {relative}")
        preimages = _event_preimages(paths.project_root, normalized)
        raw_token = secrets.token_urlsafe(32)
        capability_hash = _sha256_bytes(raw_token.encode("utf-8"))
        created = datetime.now(UTC)
        expires = created + timedelta(seconds=ttl_seconds)
        conn = sqlite3.connect(str(paths.db_path))
        try:
            ensure_control_plane_schema(conn)
            conn.execute(
                """
                INSERT INTO sot_registry_observation_capabilities (
                    capability_hash, session_id, tool_event_id, paths_json,
                    preimage_digests_json, bridge_id, start_packet_hash,
                    pauth_decision_json, expires_at, operation, capability_state, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'minted', ?)
                """,
                (
                    capability_hash,
                    session_id,
                    tool_event_id,
                    json.dumps(normalized),
                    json.dumps(preimages, sort_keys=True),
                    bridge_id,
                    start_packet_hash,
                    json.dumps(dict(pauth_decision), sort_keys=True),
                    expires.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    operation,
                    created.strftime("%Y-%m-%dT%H:%M:%SZ"),
                ),
            )
            conn.commit()
        finally:
            conn.close()
    return {
        "capability": raw_token,
        "capability_hash": capability_hash,
        "paths": list(normalized),
        "preimage_digests": preimages,
        "expires_at": expires.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def consume_observation_capability(
    *,
    capability: str,
    target_paths: Sequence[str | Path],
    preimage_digests: Mapping[str, str],
    session_id: str,
    tool_event_id: str,
    bridge_id: str,
    start_packet_hash: str,
    operation: str,
    tool_succeeded: bool,
    tool_result: Any,
    changed_by: str,
    change_reason: str,
    project_root: Path | None = None,
    registry_path: Path | None = None,
    packaged_registry_path: Path | None = None,
    db_path: Path | None = None,
) -> tuple[str, ...]:
    """Atomically consume one exact capability and append current revision evidence."""

    if not capability:
        raise RegistryAuthorizationError("direct observation without a capability is denied")
    paths = RegistryPaths.resolve(
        project_root=project_root,
        registry_path=registry_path,
        packaged_registry_path=packaged_registry_path,
        db_path=db_path,
    )
    with _RegistryFileLock(paths.lock_path):
        _ensure_no_nonterminal_journal(paths.db_path)
        snapshot = _load_snapshot_unlocked(paths)
        normalized = _normalize_event_paths(paths.project_root, target_paths)
        normalized_preimages = {key.replace("\\", "/").strip("/"): value for key, value in preimage_digests.items()}
        capability_hash = _sha256_bytes(capability.encode("utf-8"))
        conn = sqlite3.connect(str(paths.db_path))
        conn.row_factory = sqlite3.Row
        try:
            ensure_control_plane_schema(conn)
            conn.commit()
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute(
                "SELECT * FROM sot_registry_observation_capabilities WHERE capability_hash = ?",
                (capability_hash,),
            ).fetchone()
            if row is None:
                raise RegistryAuthorizationError("unknown or fabricated observation capability")
            if row["capability_state"] != "minted":
                raise RegistryAuthorizationError("observation capability was already consumed or denied")
            expires = datetime.strptime(row["expires_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
            bindings = {
                "session_id": session_id,
                "tool_event_id": tool_event_id,
                "bridge_id": bridge_id,
                "start_packet_hash": start_packet_hash,
                "operation": operation,
            }
            for column, value in bindings.items():
                if row[column] != value:
                    raise RegistryAuthorizationError(f"observation capability {column} binding mismatch")
            if datetime.now(UTC) > expires:
                raise RegistryAuthorizationError("observation capability expired")
            if tuple(json.loads(row["paths_json"])) != normalized:
                raise RegistryAuthorizationError("observation capability path binding mismatch")
            if json.loads(row["preimage_digests_json"]) != normalized_preimages:
                raise RegistryAuthorizationError("observation capability preimage binding mismatch")
            if not tool_succeeded:
                conn.execute(
                    "UPDATE sot_registry_observation_capabilities SET capability_state = 'failed_tool', "
                    "consumed_at = ?, result_digest = ? WHERE capability_hash = ?",
                    (_utc_now(), _json_digest(tool_result), capability_hash),
                )
                conn.commit()
                raise RegistryAuthorizationError("failed tools do not create current revision evidence")
            records: dict[str, SoTArtifact] = {}
            for relative in normalized:
                record = snapshot.resolver.resolve(relative)
                if record is None:
                    raise RegistryAuthorizationError(f"observation target is no longer registered: {relative}")
                records[record.id] = record
            now = _utc_now()
            revision_ids: list[str] = []
            for record in sorted(records.values(), key=lambda item: item.id):
                revision_ids.append(
                    _append_revision(
                        conn,
                        project_root=paths.project_root,
                        record=record,
                        actor_session=session_id,
                        operation=operation,
                        changed_by=changed_by,
                        changed_at=now,
                        change_reason=change_reason,
                        capability_hash=capability_hash,
                        bridge_id=bridge_id,
                        start_packet_hash=start_packet_hash,
                        pauth_decision=row["pauth_decision_json"],
                        evidence_view="governed_tool",
                        evidence_source_reference=capability_hash,
                    )
                )
            conn.execute(
                "UPDATE sot_registry_observation_capabilities SET capability_state = 'consumed', "
                "consumed_at = ?, result_digest = ? WHERE capability_hash = ? AND capability_state = 'minted'",
                (now, _json_digest(tool_result), capability_hash),
            )
            conn.commit()
            return tuple(revision_ids)
        except Exception:
            if conn.in_transaction:
                conn.rollback()
            raise
        finally:
            conn.close()


def append_passive_observation(
    *,
    target_paths: Sequence[str | Path] = (),
    record_ids: Sequence[str] = (),
    evidence_view: Literal["working_tree", "git_index"] = "working_tree",
    evidence_source_reference: str | None = None,
    actor_session: str = "unattributed_external",
    changed_by: str = "registry-observer/unattributed",
    change_reason: str = "passive direct in-place content observation",
    project_root: Path | None = None,
    registry_path: Path | None = None,
    packaged_registry_path: Path | None = None,
    db_path: Path | None = None,
) -> tuple[str, ...]:
    """Append best-effort audit evidence without granting mutation authority.

    This API is intentionally capability-free because it is an after-the-fact
    observer. It can record only present content at an already-registered
    locator; identity transitions remain outside its authority. ``record_ids``
    selects declarations exactly and may be combined with path resolution. It
    exists for aggregate declarations whose locator is a glob rather than a
    concrete member path.
    """

    paths = RegistryPaths.resolve(
        project_root=project_root,
        registry_path=registry_path,
        packaged_registry_path=packaged_registry_path,
        db_path=db_path,
    )
    with _RegistryFileLock(paths.lock_path):
        _ensure_no_nonterminal_journal(paths.db_path)
        snapshot = _load_snapshot_unlocked(paths)
        if not target_paths and not record_ids:
            raise RegistryAuthorizationError("passive observation requires target_paths or exact record_ids")
        normalized = _normalize_event_paths(paths.project_root, target_paths) if target_paths else ()
        records: dict[str, SoTArtifact] = {}
        for relative in normalized:
            record = snapshot.resolver.resolve(relative)
            if record is None:
                raise RegistryAuthorizationError(f"passive observation target is unregistered: {relative}")
            target = paths.project_root / relative
            if not target.exists() and not target.is_symlink():
                raise RegistryAuthorizationError(
                    f"passive observation cannot record a missing identity transition: {relative}"
                )
            records[record.id] = record
        records_by_id = {record.id: record for record in snapshot.records}
        for raw_record_id in record_ids:
            record_id = str(raw_record_id).strip()
            record = records_by_id.get(record_id)
            if not record_id or record is None:
                raise RegistryAuthorizationError(
                    f"passive observation record is unregistered: {record_id or raw_record_id!s}"
                )
            if record.coverage_mode == "virtual":
                raise RegistryAuthorizationError(f"passive observation cannot record a virtual identity: {record_id}")
            if record.coverage_mode == "glob":
                try:
                    present = any(paths.project_root.glob(record.storage_path))
                except (NotImplementedError, OSError, ValueError):
                    present = False
            else:
                target = paths.project_root / record.storage_path.rstrip("/")
                present = target.exists() or target.is_symlink()
            if not present:
                raise RegistryAuthorizationError(
                    f"passive observation cannot record a missing identity transition: {record.storage_path}"
                )
            records[record.id] = record
        conn = sqlite3.connect(str(paths.db_path))
        try:
            ensure_control_plane_schema(conn)
            now = _utc_now()
            conn.execute("BEGIN IMMEDIATE")
            revision_ids = tuple(
                _append_revision(
                    conn,
                    project_root=paths.project_root,
                    record=record,
                    actor_session=actor_session or "unattributed_external",
                    operation="direct_in_place_content_change",
                    changed_by=changed_by or "registry-observer/unattributed",
                    changed_at=now,
                    change_reason=change_reason,
                    evidence_view=evidence_view,
                    evidence_source_reference=evidence_source_reference,
                )
                for record in sorted(records.values(), key=lambda item: item.id)
            )
            conn.commit()
            return revision_ids
        except Exception:
            if conn.in_transaction:
                conn.rollback()
            raise
        finally:
            conn.close()


_BRIDGE_PUBLICATION_AUTHORITY_KIND = "bridge_publication"
_BRIDGE_PUBLICATION_AGGREGATE_ID = "bridge-versioned-files"
_SAFE_BRIDGE_DOCUMENT_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def _bridge_publication_claim_holder(
    project_root: Path,
    document_name: str,
) -> Mapping[str, Any] | None:
    try:
        from scripts.bridge_work_intent_registry import current_holder

        return current_holder(document_name, project_root=project_root)
    except Exception as exc:
        raise RegistryAuthorizationError(f"bridge publication claim lookup failed: {exc}") from exc


def _bridge_publication_target(
    project_root: Path,
    *,
    document_name: str,
    version: int,
    target_path: str | Path,
) -> tuple[str, Path]:
    if _SAFE_BRIDGE_DOCUMENT_RE.fullmatch(document_name) is None:
        raise RegistryAuthorizationError(f"unsafe bridge document name: {document_name!r}")
    if version < 1:
        raise RegistryAuthorizationError("bridge publication version must be positive")
    normalized = _normalize_event_paths(project_root, [target_path])
    if len(normalized) != 1:
        raise RegistryAuthorizationError("bridge publication requires one exact target")
    relative = normalized[0]
    expected = f"bridge/{document_name}-{version:03d}.md"
    if relative != expected:
        raise RegistryAuthorizationError(
            f"bridge publication target mismatch: expected {expected}, observed {relative}"
        )
    resolved = (project_root / relative).resolve()
    try:
        resolved.relative_to(project_root.resolve())
    except ValueError as exc:
        raise RegistryAuthorizationError("bridge publication target escapes project root") from exc
    return relative, resolved


def _bridge_publication_author_session(content: bytes) -> str:
    try:
        text = content.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise RegistryAuthorizationError("bridge publication content must be strict UTF-8") from exc
    try:
        from scripts.bridge_author_metadata import extract_author_metadata
    except ImportError as exc:
        raise RegistryAuthorizationError("canonical bridge author-metadata parser is unavailable") from exc
    metadata = extract_author_metadata(text)
    session_id = str(metadata.get("author_session_context_id") or "").strip().strip("`")
    if not session_id:
        raise RegistryAuthorizationError("bridge publication lacks author_session_context_id")
    return session_id


def _bridge_publication_transition_digest(
    project_root: Path,
    *,
    document_name: str,
    version: int,
    status: str,
    content: bytes,
) -> str:
    try:
        from scripts.bridge_lifecycle_resolver import (
            BridgeLifecycleResolutionError,
            resolve_bridge_lifecycle,
        )
    except ImportError as exc:
        raise RegistryAuthorizationError("strict bridge lifecycle resolver is unavailable") from exc

    validation_parent = project_root / ".gtkb-state" / "bridge-candidate-validation"
    validation_parent.mkdir(parents=True, exist_ok=True)
    exact_name = re.compile(rf"^{re.escape(document_name)}-(?P<version>[0-9]{{3}})\.md$")
    candidate_name = f"{document_name}-{version:03d}.md"
    thread_files: list[dict[str, str | int]] = []
    try:
        with tempfile.TemporaryDirectory(
            prefix=f"{document_name}-{version:03d}-",
            dir=validation_parent,
        ) as temporary:
            candidate_root = Path(temporary)
            candidate_bridge = candidate_root / "bridge"
            candidate_bridge.mkdir()
            live_bridge = project_root / "bridge"
            if live_bridge.is_dir():
                for source in live_bridge.iterdir():
                    if not source.is_file() or exact_name.fullmatch(source.name) is None:
                        continue
                    # The transition digest is the publishing thread's preimage
                    # plus the exact candidate bytes.  Ignoring the live target
                    # slot makes the same derivation usable both before initial
                    # publication and while validating compensation of that
                    # publication.  Mint still rejects an existing target before
                    # reaching this helper.
                    if source.name == candidate_name:
                        continue
                    (candidate_bridge / source.name).write_bytes(source.read_bytes())
            candidate = candidate_bridge / candidate_name
            if candidate.exists():
                raise RegistryAuthorizationError("candidate bridge version already exists")
            candidate.write_bytes(content)
            try:
                resolution = resolve_bridge_lifecycle(candidate_root, document_name)
            except BridgeLifecycleResolutionError as exc:
                raise RegistryAuthorizationError(f"invalid candidate bridge lifecycle: {exc.code}: {exc}") from exc
            for path in sorted(candidate_bridge.iterdir(), key=lambda item: item.name.casefold()):
                if not path.is_file() or exact_name.fullmatch(path.name) is None:
                    continue
                payload = path.read_bytes()
                thread_files.append(
                    {
                        "path": f"bridge/{path.name}",
                        "size": len(payload),
                        "sha256": _sha256_bytes(payload),
                    }
                )
    finally:
        with suppress(OSError):
            validation_parent.rmdir()

    latest = resolution.latest_strict_state
    expected_path = f"bridge/{document_name}-{version:03d}.md"
    if (
        latest.version != version
        or latest.status != status
        or latest.path != expected_path
        or resolution.blocking_diagnostics
    ):
        raise RegistryAuthorizationError("candidate lifecycle did not resolve to the exact requested terminal state")
    evidence = {
        "evidence_schema_version": 2,
        "document_name": document_name,
        "version": version,
        "status": status,
        "thread_files": thread_files,
        "latest": asdict(latest),
        "audit_versions": [asdict(item) for item in resolution.audit_versions],
        "quarantined_paths": list(resolution.quarantined_paths),
        "blocking_diagnostics": [asdict(item) for item in resolution.blocking_diagnostics],
    }
    return _json_digest(evidence)


def _latest_artifact_revision(
    conn: sqlite3.Connection,
    entry_id: str,
) -> sqlite3.Row | None:
    return conn.execute(
        "SELECT * FROM sot_artifact_revisions WHERE entry_id = ? ORDER BY rowid DESC LIMIT 1",
        (entry_id,),
    ).fetchone()


def _bridge_aggregate_record(
    snapshot: RegistrySnapshot,
    target_path: str,
) -> SoTArtifact:
    record = snapshot.resolver.resolve(target_path)
    if record is None or record.id != _BRIDGE_PUBLICATION_AGGREGATE_ID:
        raise RegistryAuthorizationError(
            f"bridge publication target is not covered by {_BRIDGE_PUBLICATION_AGGREGATE_ID}: {target_path}"
        )
    return record


def _bridge_aggregate_digest_without_target(
    project_root: Path,
    record: SoTArtifact,
    target: Path,
) -> str:
    if record.coverage_mode != "glob":
        raise RegistryRecoveryRequired("bridge publication aggregate is not glob-backed")
    locator = PurePosixPath(record.storage_path)
    wildcard_index = next(index for index, part in enumerate(locator.parts) if any(char in part for char in "*?["))
    base = project_root.joinpath(*locator.parts[:wildcard_index])
    pattern = "/".join(locator.parts[wildcard_index:])
    entries: list[tuple[str, str, str | None, int | None]] = []
    target_resolved = target.resolve()
    if base.exists():
        for path in sorted(base.glob(pattern), key=lambda item: item.as_posix().casefold()):
            if path.resolve() == target_resolved:
                continue
            kind = _path_object_kind(path)
            relative = path.relative_to(base).as_posix()
            if kind == "file":
                size = path.stat().st_size
                entries.append((relative, kind, _hash_file(path), size))
            else:
                entries.append((relative, kind, None, None))
    return _json_digest(entries)


def _bridge_publication_quarantine_path(project_root: Path, capability_hash: str) -> Path:
    digest = capability_hash.removeprefix("sha256:")
    return project_root / ".gtkb-state" / "bridge-publication-recovery" / f"{digest}.rollback"


def _mark_bridge_publication_recovery_required(
    conn: sqlite3.Connection,
    capability_hash: str,
    reason: str,
) -> None:
    conn.execute(
        "UPDATE sot_registry_bridge_publication_capabilities "
        "SET capability_state = 'recovery_required', failure_reason = ? "
        "WHERE capability_hash = ?",
        (reason, capability_hash),
    )
    conn.commit()


def _mark_bridge_publication_recovery_required_with_observation(
    conn: sqlite3.Connection,
    *,
    project_root: Path,
    aggregate_record: SoTArtifact,
    capability_hash: str,
    document_name: str,
    session_id: str,
    changed_by: str,
    reason: str,
) -> str:
    """Preserve a recovery failure and truthfully observe the retained aggregate."""

    if conn.in_transaction:
        conn.rollback()
    try:
        conn.execute("BEGIN IMMEDIATE")
        updated = conn.execute(
            "UPDATE sot_registry_bridge_publication_capabilities "
            "SET capability_state = 'recovery_required', failure_reason = ? "
            "WHERE capability_hash = ?",
            (reason, capability_hash),
        )
        if updated.rowcount != 1:
            raise RegistryAuthorizationError("bridge publication recovery audit row disappeared")
        revision_id = _append_revision(
            conn,
            project_root=project_root,
            record=aggregate_record,
            actor_session=session_id,
            operation="direct_in_place_content_change",
            changed_by=changed_by,
            changed_at=_utc_now(),
            change_reason=reason,
            capability_hash=capability_hash,
            bridge_id=document_name,
            evidence_view="working_tree",
            evidence_source_reference=capability_hash,
        )
        conn.commit()
        return revision_id
    except Exception:
        if conn.in_transaction:
            conn.rollback()
        _mark_bridge_publication_recovery_required(conn, capability_hash, reason)
        raise


def mint_bridge_publication_capability(
    *,
    document_name: str,
    version: int,
    status: str,
    target_path: str | Path,
    content: bytes,
    session_id: str,
    compliance_digest: str,
    operation: str = _BRIDGE_PUBLICATION_AUTHORITY_KIND,
    project_root: Path | None = None,
    registry_path: Path | None = None,
    packaged_registry_path: Path | None = None,
    db_path: Path | None = None,
    ttl_seconds: int | None = None,
) -> dict[str, Any]:
    """Mint an exact, single-use capability before one bridge file is created."""

    if not all((document_name, status, session_id, compliance_digest, operation)):
        raise RegistryAuthorizationError("bridge publication bindings must be non-empty")
    if operation != _BRIDGE_PUBLICATION_AUTHORITY_KIND:
        raise RegistryAuthorizationError("bridge publication operation is not typed")
    if ttl_seconds is None:
        ttl_seconds = resolve_protected_commit_timers(
            project_root=project_root
        ).bridge_publication_capability_ttl_seconds
    if ttl_seconds <= 0 or ttl_seconds > 800:
        raise RegistryAuthorizationError("bridge publication capability TTL must be 1-800 seconds")
    if not isinstance(content, bytes) or not content:
        raise RegistryAuthorizationError("bridge publication content bytes are required")

    paths = RegistryPaths.resolve(
        project_root=project_root,
        registry_path=registry_path,
        packaged_registry_path=packaged_registry_path,
        db_path=db_path,
    )
    relative, target = _bridge_publication_target(
        paths.project_root,
        document_name=document_name,
        version=version,
        target_path=target_path,
    )
    with _RegistryFileLock(paths.lock_path):
        _ensure_no_nonterminal_journal(paths.db_path)
        snapshot = _load_snapshot_unlocked(paths)
        aggregate_record = _bridge_aggregate_record(snapshot, relative)
        # WI-5933 concurrency fix (emergency-bootstrap; DELIB-202668164): the prior
        # global-generation currentness gate (registry_currentness over the
        # bridge/*-NNN.md glob) is removed. registry_currentness is audit state, not
        # publication authority -- its own docstring says "Hot mutation/publication
        # paths should ... use registry_identity_state." Gating on it required a
        # caller-recorded observation (taken OUTSIDE this serialized lock) to equal
        # freshly-computed content; under concurrent governed publishers the recorded
        # observation always lagged actual content, so the check never converged
        # (optimistic-CAS livelock). The aggregate preimage is now established by a
        # self-observe under this lock + one-active-capability boundary (see below).
        if target.exists() or target.is_symlink():
            raise RegistryAuthorizationError(f"bridge publication target already exists: {relative}")
        author_session = _bridge_publication_author_session(content)
        if author_session != session_id:
            raise RegistryAuthorizationError("bridge author session and claim session differ")
        holder = _bridge_publication_claim_holder(paths.project_root, document_name)
        if holder is None or str(holder.get("session_id") or "") != session_id:
            raise RegistryAuthorizationError("bridge publication requires the exact live work-intent claim")
        transition_digest = _bridge_publication_transition_digest(
            paths.project_root,
            document_name=document_name,
            version=version,
            status=status,
            content=content,
        )
        content_digest = _sha256_bytes(content)
        created = datetime.now(UTC)
        expires = created + timedelta(seconds=ttl_seconds)
        capability = secrets.token_urlsafe(32)
        capability_hash = _sha256_bytes(capability.encode("utf-8"))
        conn = sqlite3.connect(str(paths.db_path))
        conn.row_factory = sqlite3.Row
        try:
            ensure_control_plane_schema(conn)
            conn.commit()
            conn.execute(
                "UPDATE sot_registry_bridge_publication_capabilities "
                "SET capability_state = 'expired', failure_reason = 'capability expired before use' "
                "WHERE capability_state = 'minted' AND expires_at < ?",
                (created.strftime("%Y-%m-%dT%H:%M:%SZ"),),
            )
            active = conn.execute(
                "SELECT target_path FROM sot_registry_bridge_publication_capabilities "
                "WHERE capability_state = 'minted' LIMIT 1"
            ).fetchone()
            if active is not None:
                raise RegistryAuthorizationError(
                    f"another bridge publication capability is active for {active['target_path']}"
                )
            # WI-5933 concurrency fix (emergency-bootstrap; DELIB-202668164): establish
            # the aggregate preimage by observing current content INSIDE this
            # publication's serialized boundary (the _RegistryFileLock held since the
            # top of this function + the one-active-capability guard above), rather than
            # requiring a pre-matched external observation. Recording a fresh observation
            # here makes `latest` == current content by construction, so concurrent
            # governed publishers serialize correctly instead of livelocking on a stale
            # preimage. The lock + one-active-capability guard guarantee no other governed
            # publisher mutates the bridge glob between this observation and the capability
            # consume, so the preimage stays valid through the transition. (Follow-on:
            # make the aggregate generation hash incremental so this serialized critical
            # section is cheap under high publication concurrency.)
            _append_revision(
                conn,
                project_root=paths.project_root,
                record=aggregate_record,
                actor_session=session_id,
                operation="direct_in_place_content_change",
                changed_by="bridge-publication-writer",
                changed_at=_utc_now(),
                change_reason=(
                    "self-observe bridge aggregate under publication serialization (WI-5933 concurrency fix)"
                ),
                evidence_view="working_tree",
            )
            latest = _latest_artifact_revision(conn, aggregate_record.id)
            if latest is None:
                raise RegistryAuthorizationError("bridge aggregate lacks current revision evidence")
            aggregate_digest, _, _ = artifact_content_state(paths.project_root, aggregate_record)
            if latest["content_digest"] != aggregate_digest:
                raise RegistryAuthorizationError("bridge aggregate preimage is not current")
            conn.execute(
                """
                INSERT INTO sot_registry_bridge_publication_capabilities (
                    capability_hash, authority_kind, document_name, version, status,
                    target_path, content_digest, compliance_digest, transition_digest,
                    claim_session, author_session_context_id, aggregate_entry_id,
                    aggregate_preimage_digest, operation, expires_at, capability_state,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'minted', ?)
                """,
                (
                    capability_hash,
                    _BRIDGE_PUBLICATION_AUTHORITY_KIND,
                    document_name,
                    version,
                    status,
                    relative,
                    content_digest,
                    compliance_digest,
                    transition_digest,
                    session_id,
                    author_session,
                    aggregate_record.id,
                    aggregate_digest,
                    operation,
                    expires.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    created.strftime("%Y-%m-%dT%H:%M:%SZ"),
                ),
            )
            conn.commit()
        except Exception:
            if conn.in_transaction:
                conn.rollback()
            raise
        finally:
            conn.close()
    return {
        "capability": capability,
        "capability_hash": capability_hash,
        "target_path": relative,
        "content_digest": content_digest,
        "compliance_digest": compliance_digest,
        "transition_digest": transition_digest,
        "aggregate_preimage_digest": aggregate_digest,
        "expires_at": expires.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def consume_bridge_publication_capability(
    *,
    capability: str,
    target_path: str | Path,
    content: bytes,
    session_id: str,
    changed_by: str,
    change_reason: str,
    project_root: Path | None = None,
    registry_path: Path | None = None,
    packaged_registry_path: Path | None = None,
    db_path: Path | None = None,
) -> BridgePublicationReceipt:
    """Consume one exact publication capability and append aggregate evidence."""

    if not capability:
        raise RegistryAuthorizationError("direct bridge publication observation is denied")
    paths = RegistryPaths.resolve(
        project_root=project_root,
        registry_path=registry_path,
        packaged_registry_path=packaged_registry_path,
        db_path=db_path,
    )
    capability_hash = _sha256_bytes(capability.encode("utf-8"))
    with _RegistryFileLock(paths.lock_path):
        _ensure_no_nonterminal_journal(paths.db_path)
        snapshot = _load_snapshot_unlocked(paths)
        conn = sqlite3.connect(str(paths.db_path))
        conn.row_factory = sqlite3.Row
        try:
            ensure_control_plane_schema(conn)
            conn.commit()
            row = conn.execute(
                "SELECT * FROM sot_registry_bridge_publication_capabilities WHERE capability_hash = ?",
                (capability_hash,),
            ).fetchone()
            if row is None:
                raise RegistryAuthorizationError("unknown or fabricated bridge publication capability")
            if row["capability_state"] != "minted":
                raise RegistryAuthorizationError("bridge publication capability was already consumed")
            expires = datetime.strptime(row["expires_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
            if datetime.now(UTC) > expires:
                raise RegistryAuthorizationError("bridge publication capability expired")
            relative, target = _bridge_publication_target(
                paths.project_root,
                document_name=row["document_name"],
                version=int(row["version"]),
                target_path=target_path,
            )
            if relative != row["target_path"] or row["claim_session"] != session_id:
                raise RegistryAuthorizationError("bridge publication capability binding mismatch")
            if _bridge_publication_author_session(content) != row["author_session_context_id"]:
                raise RegistryAuthorizationError("bridge publication author-session binding mismatch")
            content_digest = _sha256_bytes(content)
            if content_digest != row["content_digest"]:
                raise RegistryAuthorizationError("bridge publication content binding mismatch")
            if target.is_symlink() or not target.is_file() or _hash_file(target) != content_digest:
                raise RegistryAuthorizationError("bridge publication target bytes do not match capability")
            aggregate_record = _bridge_aggregate_record(snapshot, relative)
            latest = _latest_artifact_revision(conn, aggregate_record.id)
            if latest is None or latest["content_digest"] != row["aggregate_preimage_digest"]:
                raise RegistryRecoveryRequired("bridge aggregate preimage revision changed before consume")
            aggregate_digest, _, _ = artifact_content_state(paths.project_root, aggregate_record)
            currentness = registry_currentness(
                snapshot,
                project_root=paths.project_root,
                db_path=paths.db_path,
                record_ids={aggregate_record.id},
            )
            expected_stale = [
                {
                    "id": aggregate_record.id,
                    "observed": row["aggregate_preimage_digest"],
                    "current": aggregate_digest,
                }
            ]
            if currentness["missing_revisions"] or currentness["stale"] != expected_stale:
                raise RegistryRecoveryRequired(f"bridge publication produced unexpected registry drift: {currentness}")
            now = _utc_now()
            conn.execute("BEGIN IMMEDIATE")
            revision_id = _append_revision(
                conn,
                project_root=paths.project_root,
                record=aggregate_record,
                actor_session=session_id,
                operation=_BRIDGE_PUBLICATION_AUTHORITY_KIND,
                changed_by=changed_by,
                changed_at=now,
                change_reason=change_reason,
                capability_hash=capability_hash,
                bridge_id=row["document_name"],
                evidence_view="bridge_publication",
                evidence_source_reference=capability_hash,
            )
            revision = conn.execute(
                "SELECT content_digest FROM sot_artifact_revisions WHERE revision_id = ?",
                (revision_id,),
            ).fetchone()
            if revision is None or revision["content_digest"] != aggregate_digest:
                raise RegistryRecoveryRequired("bridge publication revision did not bind exact aggregate")
            result_digest = _json_digest(
                {
                    "target_path": relative,
                    "content_digest": content_digest,
                    "aggregate_digest": aggregate_digest,
                    "transition_digest": row["transition_digest"],
                    "compliance_digest": row["compliance_digest"],
                    "revision_id": revision_id,
                }
            )
            updated = conn.execute(
                "UPDATE sot_registry_bridge_publication_capabilities "
                "SET capability_state = 'consumed', consumed_at = ?, result_digest = ?, "
                "revision_id = ? WHERE capability_hash = ? AND capability_state = 'minted'",
                (now, result_digest, revision_id, capability_hash),
            )
            if updated.rowcount != 1:
                raise RegistryAuthorizationError("bridge publication capability lost single-use race")
            conn.commit()
        except Exception:
            if conn.in_transaction:
                conn.rollback()
            raise
        finally:
            conn.close()
        final_currentness = registry_currentness(
            snapshot,
            project_root=paths.project_root,
            db_path=paths.db_path,
            record_ids={aggregate_record.id},
        )
        if not final_currentness["current"]:
            raise RegistryRecoveryRequired(
                f"bridge publication was observed but registry remains stale: {final_currentness}"
            )
    return BridgePublicationReceipt(
        capability_hash=capability_hash,
        revision_id=revision_id,
        target_path=relative,
        aggregate_digest=aggregate_digest,
        capability_state="consumed",
    )


def recover_missing_bridge_publication_capability(
    *,
    document_name: str,
    version: int,
    target_path: str | Path,
    content: bytes,
    session_id: str,
    owner_authorization: str,
    project_root: Path | None = None,
    registry_path: Path | None = None,
    packaged_registry_path: Path | None = None,
    db_path: Path | None = None,
) -> BridgePublicationReceipt:
    """Back-fill one consumed receipt for an existing pre-capability bridge file.

    Unlike :func:`mint_bridge_publication_capability`, this recovery path never
    creates, changes, or removes a bridge file. It is available only to an
    explicit owner-authorized recovery and records that provenance in the
    resulting registry revision and receipt digest.
    """

    authorization = owner_authorization.strip() if isinstance(owner_authorization, str) else ""
    if not authorization:
        raise RegistryAuthorizationError("bridge publication recovery requires owner authorization")
    if not session_id:
        raise RegistryAuthorizationError("bridge publication recovery requires a session id")
    if not isinstance(content, bytes) or not content:
        raise RegistryAuthorizationError("bridge publication recovery content bytes are required")

    paths = RegistryPaths.resolve(
        project_root=project_root,
        registry_path=registry_path,
        packaged_registry_path=packaged_registry_path,
        db_path=db_path,
    )
    relative, target = _bridge_publication_target(
        paths.project_root,
        document_name=document_name,
        version=version,
        target_path=target_path,
    )
    # Fast-fail before taking the global registry lock. The target and bytes are
    # checked again inside the lock to preserve the exact binding.
    if target.is_symlink() or not target.is_file():
        raise RegistryRecoveryRequired("bridge publication recovery target is missing")
    if _hash_file(target) != _sha256_bytes(content):
        raise RegistryAuthorizationError("bridge publication recovery target bytes do not match content")

    try:
        from scripts.bridge_lifecycle_resolver import (
            BridgeLifecycleResolutionError,
            resolve_bridge_lifecycle,
        )
    except ImportError as exc:
        raise RegistryAuthorizationError("strict bridge lifecycle resolver is unavailable") from exc

    with _RegistryFileLock(paths.lock_path):
        _ensure_no_nonterminal_journal(paths.db_path)
        if target.is_symlink() or not target.is_file():
            raise RegistryRecoveryRequired("bridge publication recovery target is missing")
        content_digest = _sha256_bytes(content)
        if _hash_file(target) != content_digest:
            raise RegistryAuthorizationError("bridge publication recovery target bytes do not match content")

        try:
            resolution = resolve_bridge_lifecycle(paths.project_root, document_name)
        except BridgeLifecycleResolutionError as exc:
            raise RegistryRecoveryRequired(
                f"bridge publication recovery lifecycle is invalid: {exc.code}: {exc}"
            ) from exc
        matching_states = [
            state for state in resolution.audit_versions if state.version == version and state.path == relative
        ]
        if len(matching_states) != 1 or resolution.blocking_diagnostics:
            raise RegistryRecoveryRequired("bridge publication recovery cannot prove the exact bridge lifecycle")
        state = matching_states[0]
        status = state.status
        transition_digest = _json_digest(
            {
                "document_name": document_name,
                "version": version,
                "status": status,
                "target_path": relative,
                "state": asdict(state),
                "audit_versions": [asdict(item) for item in resolution.audit_versions],
                "quarantined_paths": list(resolution.quarantined_paths),
                "blocking_diagnostics": [asdict(item) for item in resolution.blocking_diagnostics],
            }
        )
        author_session = _bridge_publication_author_session(content)
        snapshot = _load_snapshot_unlocked(paths)
        aggregate_record = _bridge_aggregate_record(snapshot, relative)
        aggregate_digest, _, _ = artifact_content_state(paths.project_root, aggregate_record)
        now = _utc_now()
        capability_hash = _sha256_bytes(secrets.token_urlsafe(32).encode("utf-8"))
        compliance_digest = _json_digest(
            {
                "owner_authorization": authorization,
                "target_path": relative,
                "content_digest": content_digest,
            }
        )

        conn = sqlite3.connect(str(paths.db_path))
        conn.row_factory = sqlite3.Row
        try:
            ensure_control_plane_schema(conn)
            conn.commit()
            existing = conn.execute(
                """
                SELECT capability_state FROM sot_registry_bridge_publication_capabilities
                WHERE document_name = ? AND version = ? AND target_path = ?
                ORDER BY rowid DESC LIMIT 1
                """,
                (document_name, version, relative),
            ).fetchone()
            if existing is not None:
                raise RegistryAuthorizationError(
                    "bridge publication recovery target already holds a publication capability receipt"
                )

            conn.execute("BEGIN IMMEDIATE")
            conn.execute(
                """
                INSERT INTO sot_registry_bridge_publication_capabilities (
                    capability_hash, authority_kind, document_name, version, status,
                    target_path, content_digest, compliance_digest, transition_digest,
                    claim_session, author_session_context_id, aggregate_entry_id,
                    aggregate_preimage_digest, operation, expires_at, capability_state,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'minted', ?)
                """,
                (
                    capability_hash,
                    _BRIDGE_PUBLICATION_AUTHORITY_KIND,
                    document_name,
                    version,
                    status,
                    relative,
                    content_digest,
                    compliance_digest,
                    transition_digest,
                    session_id,
                    author_session,
                    aggregate_record.id,
                    aggregate_digest,
                    _BRIDGE_PUBLICATION_AUTHORITY_KIND,
                    now,
                    now,
                ),
            )
            revision_id = _append_revision(
                conn,
                project_root=paths.project_root,
                record=aggregate_record,
                actor_session=session_id,
                operation=_BRIDGE_PUBLICATION_AUTHORITY_KIND,
                changed_by="bridge-publication-recovery",
                changed_at=now,
                change_reason=f"owner-authorized bridge publication receipt backfill: {authorization}",
                capability_hash=capability_hash,
                bridge_id=document_name,
                evidence_view="recovery",
                evidence_source_reference=capability_hash,
            )
            revision = conn.execute(
                "SELECT content_digest FROM sot_artifact_revisions WHERE revision_id = ?",
                (revision_id,),
            ).fetchone()
            if revision is None or revision["content_digest"] != aggregate_digest:
                raise RegistryRecoveryRequired("bridge publication recovery revision did not bind exact aggregate")
            result_digest = _json_digest(
                {
                    "recovered": True,
                    "owner_authorization": authorization,
                    "target_path": relative,
                    "content_digest": content_digest,
                    "aggregate_digest": aggregate_digest,
                    "transition_digest": transition_digest,
                    "revision_id": revision_id,
                }
            )
            updated = conn.execute(
                """
                UPDATE sot_registry_bridge_publication_capabilities
                SET capability_state = 'consumed', consumed_at = ?, result_digest = ?, revision_id = ?
                WHERE capability_hash = ? AND capability_state = 'minted'
                """,
                (now, result_digest, revision_id, capability_hash),
            )
            if updated.rowcount != 1:
                raise RegistryAuthorizationError("bridge publication recovery lost its single-use receipt")
            conn.commit()
        except Exception:
            if conn.in_transaction:
                conn.rollback()
            raise
        finally:
            conn.close()

        final_currentness = registry_currentness(
            snapshot,
            project_root=paths.project_root,
            db_path=paths.db_path,
            record_ids={aggregate_record.id},
        )
        if not final_currentness["current"]:
            raise RegistryRecoveryRequired(f"bridge publication recovery receipt remains stale: {final_currentness}")

    return BridgePublicationReceipt(
        capability_hash=capability_hash,
        revision_id=revision_id,
        target_path=relative,
        aggregate_digest=aggregate_digest,
        capability_state="consumed",
    )


def recover_bridge_publication(
    *,
    target_path: str | Path,
    session_id: str,
    mode: Literal["finalize", "rollback"],
    changed_by: str,
    change_reason: str,
    expected_capability_hash: str | None = None,
    expected_content_digest: str | None = None,
    expected_document_name: str | None = None,
    expected_version: int | None = None,
    expected_status: str | None = None,
    project_root: Path | None = None,
    registry_path: Path | None = None,
    packaged_registry_path: Path | None = None,
    db_path: Path | None = None,
) -> BridgePublicationReceipt:
    """Recover an exact crashed bridge publication without exposing its secret."""

    if mode not in {"finalize", "rollback"}:
        raise RegistryAuthorizationError("bridge publication recovery mode must be finalize or rollback")
    if not session_id or not changed_by or not change_reason:
        raise RegistryAuthorizationError("bridge publication recovery bindings must be non-empty")
    paths = RegistryPaths.resolve(
        project_root=project_root,
        registry_path=registry_path,
        packaged_registry_path=packaged_registry_path,
        db_path=db_path,
    )
    normalized = _normalize_event_paths(paths.project_root, [target_path])
    if len(normalized) != 1:
        raise RegistryAuthorizationError("bridge publication recovery requires one exact target")
    requested_target = normalized[0]

    with _RegistryFileLock(paths.lock_path):
        _ensure_no_nonterminal_journal(paths.db_path)
        snapshot = _load_snapshot_unlocked(paths)
        conn = sqlite3.connect(str(paths.db_path))
        conn.row_factory = sqlite3.Row
        target: Path | None = None
        quarantine: Path | None = None
        quarantine_moved = False
        rollback_committed = False
        try:
            ensure_control_plane_schema(conn)
            conn.commit()
            if expected_capability_hash:
                row = conn.execute(
                    "SELECT * FROM sot_registry_bridge_publication_capabilities "
                    "WHERE capability_hash = ? AND target_path = ? AND claim_session = ?",
                    (expected_capability_hash, requested_target, session_id),
                ).fetchone()
            else:
                row = conn.execute(
                    "SELECT * FROM sot_registry_bridge_publication_capabilities "
                    "WHERE target_path = ? AND claim_session = ? ORDER BY rowid DESC LIMIT 1",
                    (requested_target, session_id),
                ).fetchone()
            if row is None:
                raise RegistryAuthorizationError("exact bridge publication recovery row was not found")
            expected_bindings = {
                "capability_hash": expected_capability_hash,
                "content_digest": expected_content_digest,
                "document_name": expected_document_name,
                "version": expected_version,
                "status": expected_status,
            }
            mismatched = [
                name
                for name, expected in expected_bindings.items()
                if expected is not None and str(row[name]) != str(expected)
            ]
            if mismatched:
                raise RegistryAuthorizationError(
                    "bridge publication recovery sidecar binding mismatch: " + ", ".join(sorted(mismatched))
                )
            relative, target = _bridge_publication_target(
                paths.project_root,
                document_name=row["document_name"],
                version=int(row["version"]),
                target_path=target_path,
            )
            if relative != row["target_path"]:
                raise RegistryAuthorizationError("bridge publication recovery target binding mismatch")
            capability_hash = row["capability_hash"]
            state = row["capability_state"]
            quarantine = _bridge_publication_quarantine_path(paths.project_root, capability_hash)
            aggregate_record = _bridge_aggregate_record(snapshot, relative)
            latest = _latest_artifact_revision(conn, aggregate_record.id)
            if latest is None:
                raise RegistryRecoveryRequired("bridge aggregate has no recovery revision")

            target_present = target.exists() or target.is_symlink()
            quarantine_present = quarantine.exists() or quarantine.is_symlink()
            if quarantine_present:
                if quarantine.is_symlink() or not quarantine.is_file():
                    raise RegistryRecoveryRequired("bridge publication rollback quarantine is not a regular file")
                if _hash_file(quarantine) != row["content_digest"]:
                    raise RegistryRecoveryRequired("bridge publication rollback quarantine bytes are not exact")
                if target_present:
                    raise RegistryRecoveryRequired(
                        "bridge publication recovery found both target and rollback quarantine"
                    )
                if mode == "finalize":
                    raise RegistryRecoveryRequired(
                        "bridge publication finalize found an interrupted rollback quarantine"
                    )
            if target_present:
                if target.is_symlink() or not target.is_file():
                    failure = "bridge publication recovery target is not a regular file"
                    if mode == "rollback":
                        _mark_bridge_publication_recovery_required_with_observation(
                            conn,
                            project_root=paths.project_root,
                            aggregate_record=aggregate_record,
                            capability_hash=capability_hash,
                            document_name=row["document_name"],
                            session_id=session_id,
                            changed_by=changed_by,
                            reason=failure,
                        )
                        raise RegistryRecoveryRequired(failure)
                    raise RegistryAuthorizationError(failure)
                if _hash_file(target) != row["content_digest"]:
                    failure = "bridge publication recovery target bytes do not match the exact row"
                    if mode == "rollback":
                        _mark_bridge_publication_recovery_required_with_observation(
                            conn,
                            project_root=paths.project_root,
                            aggregate_record=aggregate_record,
                            capability_hash=capability_hash,
                            document_name=row["document_name"],
                            session_id=session_id,
                            changed_by=changed_by,
                            reason=failure,
                        )
                        raise RegistryRecoveryRequired(failure)
                    raise RegistryAuthorizationError(failure)

            if mode == "finalize":
                if state == "consumed":
                    if not target_present:
                        raise RegistryAuthorizationError("consumed bridge publication recovery target is missing")
                    revision = conn.execute(
                        "SELECT content_digest FROM sot_artifact_revisions WHERE revision_id = ?",
                        (row["revision_id"],),
                    ).fetchone()
                    if revision is None:
                        raise RegistryRecoveryRequired("consumed bridge publication recovery revision is missing")
                    aggregate_digest, _, _ = artifact_content_state(
                        paths.project_root,
                        aggregate_record,
                    )
                    final_currentness = registry_currentness(
                        snapshot,
                        project_root=paths.project_root,
                        db_path=paths.db_path,
                        record_ids={aggregate_record.id},
                    )
                    if not final_currentness["current"]:
                        raise RegistryRecoveryRequired(
                            f"idempotent bridge publication finalize found stale aggregate: {final_currentness}"
                        )
                    return BridgePublicationReceipt(
                        capability_hash=capability_hash,
                        revision_id=row["revision_id"],
                        target_path=relative,
                        aggregate_digest=aggregate_digest,
                        capability_state="consumed",
                    )
                if state not in {"minted", "expired"}:
                    raise RegistryAuthorizationError(f"bridge publication cannot be finalized from {state}")
                if not target_present:
                    raise RegistryAuthorizationError("bridge publication recovery target is missing")
                predicted = _bridge_aggregate_digest_without_target(
                    paths.project_root,
                    aggregate_record,
                    target,
                )
                if predicted != row["aggregate_preimage_digest"]:
                    raise RegistryRecoveryRequired(
                        "bridge publication finalize cannot prove its exact aggregate preimage"
                    )
                if latest["content_digest"] != row["aggregate_preimage_digest"]:
                    raise RegistryRecoveryRequired(
                        "bridge publication finalize no longer has its aggregate preimage revision"
                    )
                aggregate_digest, _, _ = artifact_content_state(paths.project_root, aggregate_record)
                if _hash_file(target) != row["content_digest"]:
                    raise RegistryRecoveryRequired(
                        "bridge publication finalize target changed during aggregate observation"
                    )
                confirmed_aggregate_digest, _, _ = artifact_content_state(
                    paths.project_root,
                    aggregate_record,
                )
                if confirmed_aggregate_digest != aggregate_digest or _hash_file(target) != row["content_digest"]:
                    raise RegistryRecoveryRequired(
                        "bridge publication finalize aggregate changed during stable observation"
                    )
                now = _utc_now()
                conn.execute("BEGIN IMMEDIATE")
                revision_id = _append_revision(
                    conn,
                    project_root=paths.project_root,
                    record=aggregate_record,
                    actor_session=session_id,
                    operation=_BRIDGE_PUBLICATION_AUTHORITY_KIND,
                    changed_by=changed_by,
                    changed_at=now,
                    change_reason=change_reason,
                    capability_hash=capability_hash,
                    bridge_id=row["document_name"],
                    evidence_view="recovery",
                    evidence_source_reference=capability_hash,
                )
                result_digest = _json_digest(
                    {
                        "target_path": relative,
                        "content_digest": row["content_digest"],
                        "aggregate_digest": aggregate_digest,
                        "transition_digest": row["transition_digest"],
                        "compliance_digest": row["compliance_digest"],
                        "revision_id": revision_id,
                    }
                )
                updated = conn.execute(
                    "UPDATE sot_registry_bridge_publication_capabilities "
                    "SET capability_state = 'consumed', consumed_at = ?, result_digest = ?, "
                    "revision_id = ?, failure_reason = NULL "
                    "WHERE capability_hash = ? AND capability_state = ?",
                    (now, result_digest, revision_id, capability_hash, state),
                )
                if updated.rowcount != 1:
                    raise RegistryAuthorizationError("bridge publication recovery lost its finalize single-use race")
                conn.commit()
                final_currentness = registry_currentness(
                    snapshot,
                    project_root=paths.project_root,
                    db_path=paths.db_path,
                    record_ids={aggregate_record.id},
                )
                if not final_currentness["current"]:
                    raise RegistryRecoveryRequired(f"recovered bridge publication remains stale: {final_currentness}")
                return BridgePublicationReceipt(
                    capability_hash=capability_hash,
                    revision_id=revision_id,
                    target_path=relative,
                    aggregate_digest=aggregate_digest,
                    capability_state="consumed",
                )

            if state == "compensated":
                if target_present:
                    raise RegistryRecoveryRequired("compensated bridge publication recovery target unexpectedly exists")
                observed, _, _ = artifact_content_state(paths.project_root, aggregate_record)
                if observed != row["aggregate_preimage_digest"] or latest["content_digest"] != observed:
                    raise RegistryRecoveryRequired(
                        "idempotent bridge publication rollback no longer matches its aggregate preimage"
                    )
                final_currentness = registry_currentness(
                    snapshot,
                    project_root=paths.project_root,
                    db_path=paths.db_path,
                    record_ids={aggregate_record.id},
                )
                if not final_currentness["current"]:
                    raise RegistryRecoveryRequired(
                        f"idempotent bridge publication rollback found stale aggregate: {final_currentness}"
                    )
                if quarantine_present:
                    quarantine.unlink()
                return BridgePublicationReceipt(
                    capability_hash=capability_hash,
                    revision_id=row["compensation_revision_id"],
                    target_path=relative,
                    aggregate_digest=observed,
                    capability_state="compensated",
                )
            if state not in {"minted", "expired", "consumed"}:
                raise RegistryAuthorizationError(f"bridge publication cannot be rolled back from {state}")
            predicted = _bridge_aggregate_digest_without_target(
                paths.project_root,
                aggregate_record,
                target,
            )
            if predicted != row["aggregate_preimage_digest"]:
                failure = "bridge publication rollback cannot restore its exact aggregate preimage"
                _mark_bridge_publication_recovery_required_with_observation(
                    conn,
                    project_root=paths.project_root,
                    aggregate_record=aggregate_record,
                    capability_hash=capability_hash,
                    document_name=row["document_name"],
                    session_id=session_id,
                    changed_by=changed_by,
                    reason=failure,
                )
                raise RegistryRecoveryRequired(failure)
            if state in {"minted", "expired"}:
                if latest["content_digest"] != row["aggregate_preimage_digest"]:
                    failure = "unconsumed bridge publication no longer has its aggregate preimage"
                    _mark_bridge_publication_recovery_required_with_observation(
                        conn,
                        project_root=paths.project_root,
                        aggregate_record=aggregate_record,
                        capability_hash=capability_hash,
                        document_name=row["document_name"],
                        session_id=session_id,
                        changed_by=changed_by,
                        reason=failure,
                    )
                    raise RegistryRecoveryRequired(failure)
            elif latest["revision_id"] != row["revision_id"]:
                failure = "another bridge aggregate revision followed the publication"
                _mark_bridge_publication_recovery_required_with_observation(
                    conn,
                    project_root=paths.project_root,
                    aggregate_record=aggregate_record,
                    capability_hash=capability_hash,
                    document_name=row["document_name"],
                    session_id=session_id,
                    changed_by=changed_by,
                    reason=failure,
                )
                raise RegistryRecoveryRequired(failure)

            quarantine_moved = quarantine_present
            if target_present:
                quarantine.parent.mkdir(parents=True, exist_ok=True)
                os.replace(target, quarantine)
                quarantine_moved = True
                if _hash_file(quarantine) != row["content_digest"]:
                    if not target.exists() and not target.is_symlink():
                        os.replace(quarantine, target)
                        quarantine_moved = False
                    failure = "bridge publication rollback target changed before atomic quarantine"
                    _mark_bridge_publication_recovery_required_with_observation(
                        conn,
                        project_root=paths.project_root,
                        aggregate_record=aggregate_record,
                        capability_hash=capability_hash,
                        document_name=row["document_name"],
                        session_id=session_id,
                        changed_by=changed_by,
                        reason=failure,
                    )
                    raise RegistryRecoveryRequired(failure)
            now = _utc_now()
            conn.execute("BEGIN IMMEDIATE")
            observed, _, _ = artifact_content_state(paths.project_root, aggregate_record)
            if observed != row["aggregate_preimage_digest"]:
                raise RegistryRecoveryRequired("bridge aggregate changed during recovery rollback")
            compensation_revision_id: str | None = None
            if latest["content_digest"] != observed:
                compensation_revision_id = _append_revision(
                    conn,
                    project_root=paths.project_root,
                    record=aggregate_record,
                    actor_session=session_id,
                    operation="bridge_publication_compensation",
                    changed_by=changed_by,
                    changed_at=now,
                    change_reason=change_reason,
                    capability_hash=capability_hash,
                    bridge_id=row["document_name"],
                    evidence_view="recovery",
                    evidence_source_reference=capability_hash,
                )
            compensation_digest = _json_digest(
                {
                    "target_path": relative,
                    "restored_aggregate_digest": observed,
                    "reason": change_reason,
                    "compensation_revision_id": compensation_revision_id,
                }
            )
            updated = conn.execute(
                "UPDATE sot_registry_bridge_publication_capabilities "
                "SET capability_state = 'compensated', consumed_at = COALESCE(consumed_at, ?), "
                "compensation_revision_id = ?, compensation_digest = ?, failure_reason = ? "
                "WHERE capability_hash = ? AND capability_state = ?",
                (
                    now,
                    compensation_revision_id,
                    compensation_digest,
                    change_reason,
                    capability_hash,
                    state,
                ),
            )
            if updated.rowcount != 1:
                raise RegistryAuthorizationError("bridge publication recovery lost its rollback single-use race")
            conn.commit()
            rollback_committed = True
            if quarantine_moved:
                quarantine.unlink()
                quarantine_moved = False
        except Exception as exc:
            if conn.in_transaction:
                conn.rollback()
            if rollback_committed:
                raise
            if quarantine_moved and quarantine is not None and target is not None and not target.exists():
                try:
                    os.replace(quarantine, target)
                    quarantine_moved = False
                    if _hash_file(target) != row["content_digest"]:
                        raise OSError("restored bytes differ")
                except OSError as restore_exc:
                    try:
                        _mark_bridge_publication_recovery_required(
                            conn,
                            capability_hash,
                            f"recovery rollback restoration failed: {restore_exc}",
                        )
                    finally:
                        raise RegistryRecoveryRequired(
                            "bridge publication recovery failed and exact file restoration failed"
                        ) from exc
                _mark_bridge_publication_recovery_required_with_observation(
                    conn,
                    project_root=paths.project_root,
                    aggregate_record=aggregate_record,
                    capability_hash=capability_hash,
                    document_name=row["document_name"],
                    session_id=session_id,
                    changed_by=changed_by,
                    reason=f"recovery rollback failed after exact file restoration: {exc}",
                )
            elif quarantine_moved and quarantine is not None and target is not None:
                _mark_bridge_publication_recovery_required_with_observation(
                    conn,
                    project_root=paths.project_root,
                    aggregate_record=aggregate_record,
                    capability_hash=capability_hash,
                    document_name=row["document_name"],
                    session_id=session_id,
                    changed_by=changed_by,
                    reason=f"recovery rollback failed with exact file retained: {exc}",
                )
            raise
        finally:
            conn.close()

        final_currentness = registry_currentness(
            snapshot,
            project_root=paths.project_root,
            db_path=paths.db_path,
            record_ids={aggregate_record.id},
        )
        if not final_currentness["current"]:
            raise RegistryRecoveryRequired(f"bridge publication recovery rollback remains stale: {final_currentness}")
    return BridgePublicationReceipt(
        capability_hash=capability_hash,
        revision_id=compensation_revision_id,
        target_path=relative,
        aggregate_digest=observed,
        capability_state="compensated",
    )


def compensate_bridge_publication(
    *,
    capability: str,
    target_path: str | Path,
    session_id: str,
    reason: str,
    changed_by: str,
    project_root: Path | None = None,
    registry_path: Path | None = None,
    packaged_registry_path: Path | None = None,
    db_path: Path | None = None,
) -> BridgePublicationReceipt:
    """Remove only the exact new file and restore aggregate preimage evidence."""

    if not capability or not reason:
        raise RegistryAuthorizationError("bridge publication compensation requires capability and reason")
    paths = RegistryPaths.resolve(
        project_root=project_root,
        registry_path=registry_path,
        packaged_registry_path=packaged_registry_path,
        db_path=db_path,
    )
    capability_hash = _sha256_bytes(capability.encode("utf-8"))
    with _RegistryFileLock(paths.lock_path):
        _ensure_no_nonterminal_journal(paths.db_path)
        snapshot = _load_snapshot_unlocked(paths)
        conn = sqlite3.connect(str(paths.db_path))
        conn.row_factory = sqlite3.Row
        deleted_bytes: bytes | None = None
        candidate_bytes: bytes | None = None
        target: Path | None = None
        try:
            ensure_control_plane_schema(conn)
            conn.commit()
            row = conn.execute(
                "SELECT * FROM sot_registry_bridge_publication_capabilities WHERE capability_hash = ?",
                (capability_hash,),
            ).fetchone()
            if row is None:
                raise RegistryAuthorizationError("unknown bridge publication compensation capability")
            if row["capability_state"] not in {"minted", "consumed"}:
                raise RegistryAuthorizationError(
                    f"bridge publication cannot be compensated from {row['capability_state']}"
                )
            if row["claim_session"] != session_id:
                raise RegistryAuthorizationError("bridge publication compensation session mismatch")
            relative, target = _bridge_publication_target(
                paths.project_root,
                document_name=row["document_name"],
                version=int(row["version"]),
                target_path=target_path,
            )
            if relative != row["target_path"]:
                raise RegistryAuthorizationError("bridge publication compensation target mismatch")
            aggregate_record = _bridge_aggregate_record(snapshot, relative)
            latest = _latest_artifact_revision(conn, aggregate_record.id)
            if latest is None:
                raise RegistryRecoveryRequired("bridge aggregate has no revision to compensate")
            if target.exists() or target.is_symlink():
                if target.is_symlink() or not target.is_file():
                    failure = "bridge publication compensation target is not a regular file"
                    _mark_bridge_publication_recovery_required_with_observation(
                        conn,
                        project_root=paths.project_root,
                        aggregate_record=aggregate_record,
                        capability_hash=capability_hash,
                        document_name=row["document_name"],
                        session_id=session_id,
                        changed_by=changed_by,
                        reason=failure,
                    )
                    raise RegistryRecoveryRequired(failure)
                candidate_bytes = target.read_bytes()
                if _sha256_bytes(candidate_bytes) != row["content_digest"]:
                    failure = "bridge publication compensation target bytes changed"
                    _mark_bridge_publication_recovery_required_with_observation(
                        conn,
                        project_root=paths.project_root,
                        aggregate_record=aggregate_record,
                        capability_hash=capability_hash,
                        document_name=row["document_name"],
                        session_id=session_id,
                        changed_by=changed_by,
                        reason=failure,
                    )
                    raise RegistryRecoveryRequired(failure)
            elif row["capability_state"] == "consumed":
                failure = "consumed bridge publication compensation target is missing"
                _mark_bridge_publication_recovery_required_with_observation(
                    conn,
                    project_root=paths.project_root,
                    aggregate_record=aggregate_record,
                    capability_hash=capability_hash,
                    document_name=row["document_name"],
                    session_id=session_id,
                    changed_by=changed_by,
                    reason=failure,
                )
                raise RegistryRecoveryRequired(failure)

            validated_transition_digest: str | None = None
            if candidate_bytes is not None:
                try:
                    validated_transition_digest = _bridge_publication_transition_digest(
                        paths.project_root,
                        document_name=row["document_name"],
                        version=int(row["version"]),
                        status=row["status"],
                        content=candidate_bytes,
                    )
                except Exception as exc:
                    failure = f"bridge publication thread preimage cannot be derived: {exc}"
                    _mark_bridge_publication_recovery_required_with_observation(
                        conn,
                        project_root=paths.project_root,
                        aggregate_record=aggregate_record,
                        capability_hash=capability_hash,
                        document_name=row["document_name"],
                        session_id=session_id,
                        changed_by=changed_by,
                        reason=failure,
                    )
                    raise RegistryRecoveryRequired(failure) from exc
                if validated_transition_digest != row["transition_digest"]:
                    failure = "bridge publication thread preimage changed before compensation"
                    _mark_bridge_publication_recovery_required_with_observation(
                        conn,
                        project_root=paths.project_root,
                        aggregate_record=aggregate_record,
                        capability_hash=capability_hash,
                        document_name=row["document_name"],
                        session_id=session_id,
                        changed_by=changed_by,
                        reason=failure,
                    )
                    raise RegistryRecoveryRequired(failure)
            else:
                # A minted capability may legitimately be compensated before
                # its target file is created.  No candidate bytes exist from
                # which to reconstruct the thread transition, and the global
                # one-active-capability boundary prevents another governed
                # publication in that interval.  Preserve the existing exact
                # aggregate preimage check for this no-file case only.
                predicted = _bridge_aggregate_digest_without_target(
                    paths.project_root,
                    aggregate_record,
                    target,
                )
                if (
                    predicted != row["aggregate_preimage_digest"]
                    or latest["content_digest"] != row["aggregate_preimage_digest"]
                ):
                    failure = "minted bridge publication no longer has its aggregate preimage"
                    _mark_bridge_publication_recovery_required_with_observation(
                        conn,
                        project_root=paths.project_root,
                        aggregate_record=aggregate_record,
                        capability_hash=capability_hash,
                        document_name=row["document_name"],
                        session_id=session_id,
                        changed_by=changed_by,
                        reason=failure,
                    )
                    raise RegistryRecoveryRequired(failure)

            deleted_bytes = candidate_bytes
            now = _utc_now()
            conn.execute("BEGIN IMMEDIATE")
            if deleted_bytes is not None:
                target.unlink()
                try:
                    observed_transition_digest = _bridge_publication_transition_digest(
                        paths.project_root,
                        document_name=row["document_name"],
                        version=int(row["version"]),
                        status=row["status"],
                        content=deleted_bytes,
                    )
                except Exception as exc:
                    raise RegistryRecoveryRequired(
                        f"bridge publication thread changed during compensation: {exc}"
                    ) from exc
                if observed_transition_digest != row["transition_digest"]:
                    raise RegistryRecoveryRequired("bridge publication thread changed during compensation")
            observed, _, _ = artifact_content_state(paths.project_root, aggregate_record)
            if deleted_bytes is None and observed != row["aggregate_preimage_digest"]:
                raise RegistryRecoveryRequired("bridge aggregate changed during compensation")
            compensation_revision_id: str | None = None
            if latest["content_digest"] != observed:
                compensation_revision_id = _append_revision(
                    conn,
                    project_root=paths.project_root,
                    record=aggregate_record,
                    actor_session=session_id,
                    operation="bridge_publication_compensation",
                    changed_by=changed_by,
                    changed_at=now,
                    change_reason=reason,
                    capability_hash=capability_hash,
                    bridge_id=row["document_name"],
                    evidence_view="recovery",
                    evidence_source_reference=capability_hash,
                )
            compensation_digest = _json_digest(
                {
                    "target_path": relative,
                    "aggregate_preimage_digest": row["aggregate_preimage_digest"],
                    "observed_aggregate_digest": observed,
                    "thread_transition_digest": (validated_transition_digest or row["transition_digest"]),
                    "reason": reason,
                    "compensation_revision_id": compensation_revision_id,
                }
            )
            conn.execute(
                "UPDATE sot_registry_bridge_publication_capabilities "
                "SET capability_state = 'compensated', consumed_at = COALESCE(consumed_at, ?), "
                "compensation_revision_id = ?, compensation_digest = ?, failure_reason = ? "
                "WHERE capability_hash = ?",
                (now, compensation_revision_id, compensation_digest, reason, capability_hash),
            )
            conn.commit()
        except Exception as exc:
            if conn.in_transaction:
                conn.rollback()
            if deleted_bytes is not None and target is not None and not target.exists():
                try:
                    with target.open("xb") as handle:
                        handle.write(deleted_bytes)
                    if _sha256_bytes(target.read_bytes()) != _sha256_bytes(deleted_bytes):
                        raise OSError("restored bytes differ")
                except OSError as restore_exc:
                    try:
                        _mark_bridge_publication_recovery_required(
                            conn,
                            capability_hash,
                            f"compensation rollback failed: {restore_exc}",
                        )
                    finally:
                        raise RegistryRecoveryRequired(
                            "bridge publication compensation failed and exact file restoration failed"
                        ) from exc
                _mark_bridge_publication_recovery_required_with_observation(
                    conn,
                    project_root=paths.project_root,
                    aggregate_record=aggregate_record,
                    capability_hash=capability_hash,
                    document_name=row["document_name"],
                    session_id=session_id,
                    changed_by=changed_by,
                    reason=f"compensation failed after exact file restoration: {exc}",
                )
            elif deleted_bytes is not None and target is not None:
                _mark_bridge_publication_recovery_required_with_observation(
                    conn,
                    project_root=paths.project_root,
                    aggregate_record=aggregate_record,
                    capability_hash=capability_hash,
                    document_name=row["document_name"],
                    session_id=session_id,
                    changed_by=changed_by,
                    reason=f"compensation failed with exact file retained: {exc}",
                )
            raise
        finally:
            conn.close()
        final_currentness = registry_currentness(
            snapshot,
            project_root=paths.project_root,
            db_path=paths.db_path,
            record_ids={aggregate_record.id},
        )
        if not final_currentness["current"]:
            raise RegistryRecoveryRequired(
                f"bridge publication compensation did not restore currentness: {final_currentness}"
            )
    return BridgePublicationReceipt(
        capability_hash=capability_hash,
        revision_id=compensation_revision_id,
        target_path=relative,
        aggregate_digest=observed,
        capability_state="compensated",
    )


_WI5441_V4_RECOVERY_BRIDGE_ID = "gtkb-wi5441-registry-control-plane-reverse-coverage-v4"
_WI5441_V4_RECOVERY_PAUTH_ID = "PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5441-REGISTRY-CONTROL-PLANE-20260724"
_WI5441_V4_RECOVERY_SESSION_ID = "019f863a-acd3-7320-80c0-1831f0936cc0"
_WI5441_V4_RECOVERY_PACKET_HASH = "sha256:8404611f0df4cc7b8576dfb471d434b30ac2cb42f94cc09f485492007d162a62"
_WI5441_V4_RECOVERY_PRIOR_DIGEST = "sha256:f6c3b3f4b8d89829da9b0b11cc7d308c13c267bf05e98aeb9ab9d6e19bec7267"
_WI5441_V4_RECOVERY_CURRENT_DIGEST = "sha256:61c6e3e2cab2b5376e70e7e0b4911e86b853a801e1aaa9515e6780242ea921ea"
_WI5441_V4_RECOVERY_INVENTORY_DIGEST = "sha256:ef89330284fc3ba1de493f77010b8f37a9c93ceafa8e410f0df973b7061cdfae"


def _wi5441_bridge_recovery_evidence(project_root: Path) -> tuple[dict[str, str], dict[str, Any]]:
    status = subprocess.run(
        ["git", "status", "--porcelain=v1", "--untracked-files=all", "--", "bridge"],
        cwd=project_root,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        timeout=30,
        check=False,
    )
    if status.returncode != 0:
        raise RegistryRecoveryRequired(
            "WI-5441 bridge recovery could not inspect the dirty bridge inventory: "
            + (status.stderr or status.stdout or "git status failed").strip()
        )
    inventory: dict[str, str] = {}
    for line in status.stdout.splitlines():
        if line[:2] != "??":
            raise RegistryRecoveryRequired(
                f"WI-5441 bridge recovery requires additive-only bridge evidence; observed {line[:2]!r}"
            )
        relative = line[3:].replace("\\", "/")
        candidate = project_root / relative
        if not candidate.is_file():
            raise RegistryRecoveryRequired(f"WI-5441 bridge recovery path is not a file: {relative}")
        inventory[relative] = _sha256_bytes(candidate.read_bytes())
    inventory_digest = _json_digest(inventory)
    if inventory_digest != _WI5441_V4_RECOVERY_INVENTORY_DIGEST:
        raise RegistryRecoveryRequired(
            "WI-5441 bridge recovery inventory drifted: "
            f"expected {_WI5441_V4_RECOVERY_INVENTORY_DIGEST}, observed {inventory_digest}"
        )

    scripts_path = str(project_root / "scripts")
    if scripts_path not in sys.path:
        sys.path.insert(0, scripts_path)
    try:
        from bridge_lifecycle_resolver import (
            BridgeLifecycleResolutionError,
            resolve_bridge_lifecycle,
        )
    except ImportError as exc:
        raise RegistryRecoveryRequired("strict bridge lifecycle resolver is unavailable") from exc

    lifecycle: dict[str, Any] = {"valid": {}, "quarantined": {}}
    expected_valid = {
        "gtkb-file-move-rename-canonicalization-repair-forward": (4, "NO-GO", "strict"),
        "gtkb-wi5441-registry-control-plane-reverse-coverage-v3": (2, "WITHDRAWN", "legacy"),
        _WI5441_V4_RECOVERY_BRIDGE_ID: (4, "GO", "strict"),
        "gtkb-wi5279-strict-lifecycle-fixture-recovery-v2": (6, "NO-GO", "strict"),
    }
    for slug, expected in expected_valid.items():
        try:
            resolved = resolve_bridge_lifecycle(project_root, slug)
        except BridgeLifecycleResolutionError as exc:
            raise RegistryRecoveryRequired(f"expected valid bridge chain is malformed: {slug}: {exc}") from exc
        latest = resolved.latest_strict_state
        actual = None if latest is None else (latest.version, latest.status, latest.classification)
        if actual != expected or resolved.blocking_diagnostics:
            raise RegistryRecoveryRequired(
                f"WI-5441 bridge recovery lifecycle drift for {slug}: expected={expected}, actual={actual}"
            )
        lifecycle["valid"][slug] = {
            "version": latest.version,
            "status": latest.status,
            "classification": latest.classification,
        }

    expected_invalid = {
        "gtkb-wi5441-registry-control-plane-reverse-coverage": (
            "WRONG_BRIDGE_VERSION_METADATA",
            "bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-009.md",
            9,
        ),
        "gtkb-wi5441-registry-control-plane-reverse-coverage-v2": (
            "DUPLICATE_BRIDGE_METADATA",
            "bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-v2-001.md",
            1,
        ),
        "gtkb-wi5279-strict-lifecycle-fixture-recovery": (
            "WRONG_STATUS_AUTHOR_ROLE",
            "bridge/gtkb-wi5279-strict-lifecycle-fixture-recovery-002.md",
            2,
        ),
    }
    for slug, expected in expected_invalid.items():
        try:
            resolve_bridge_lifecycle(project_root, slug)
        except BridgeLifecycleResolutionError as exc:
            actual = (exc.code, exc.path, exc.version)
            if actual != expected:
                raise RegistryRecoveryRequired(
                    f"WI-5441 quarantine diagnostic drift for {slug}: expected={expected}, actual={actual}"
                ) from exc
            lifecycle["quarantined"][slug] = {
                "code": exc.code,
                "path": exc.path,
                "version": exc.version,
            }
        else:
            raise RegistryRecoveryRequired(f"WI-5441 quarantined chain unexpectedly became valid: {slug}")
    return inventory, lifecycle


def recover_wi5441_bridge_aggregate(
    *,
    actor_session: str,
    bridge_id: str,
    start_packet_hash: str,
    pauth_id: str,
    changed_by: str,
    change_reason: str,
    project_root: Path | None = None,
    registry_path: Path | None = None,
    packaged_registry_path: Path | None = None,
    db_path: Path | None = None,
) -> BridgeAggregateRecoveryReceipt:
    """Reject the retired, one-time WI-5441 bridge-aggregate recovery path."""

    raise RegistryAuthorizationError("recover_wi5441_bridge_aggregate is retired; use typed publication capabilities")

    bindings = (
        actor_session,
        bridge_id,
        start_packet_hash,
        pauth_id,
    )
    expected = (
        _WI5441_V4_RECOVERY_SESSION_ID,
        _WI5441_V4_RECOVERY_BRIDGE_ID,
        _WI5441_V4_RECOVERY_PACKET_HASH,
        _WI5441_V4_RECOVERY_PAUTH_ID,
    )
    if bindings != expected:
        raise RegistryAuthorizationError("WI-5441 bridge recovery authority binding mismatch")
    paths = RegistryPaths.resolve(
        project_root=project_root,
        registry_path=registry_path,
        packaged_registry_path=packaged_registry_path,
        db_path=db_path,
    )
    with _RegistryFileLock(paths.lock_path):
        _ensure_no_nonterminal_journal(paths.db_path)
        snapshot = _load_snapshot_unlocked(paths)
        currentness = registry_currentness(snapshot, project_root=paths.project_root, db_path=paths.db_path)
        inventory, lifecycle = _wi5441_bridge_recovery_evidence(paths.project_root)
        lifecycle_digest = _json_digest(lifecycle)
        request = {
            "actor_session": actor_session,
            "bridge_id": bridge_id,
            "start_packet_hash": start_packet_hash,
            "pauth_id": pauth_id,
            "prior_digest": _WI5441_V4_RECOVERY_PRIOR_DIGEST,
            "current_digest": _WI5441_V4_RECOVERY_CURRENT_DIGEST,
            "inventory_digest": _json_digest(inventory),
            "lifecycle_digest": lifecycle_digest,
        }
        request_digest = _json_digest(request)
        conn = sqlite3.connect(str(paths.db_path))
        conn.row_factory = sqlite3.Row
        try:
            ensure_control_plane_schema(conn)
            conn.commit()
            existing = conn.execute(
                "SELECT * FROM sot_registry_bridge_recovery_receipts WHERE request_digest = ?",
                (request_digest,),
            ).fetchone()
            if existing is not None:
                if not currentness["current"]:
                    raise RegistryRecoveryRequired("recorded WI-5441 recovery receipt is not registry-current")
                return BridgeAggregateRecoveryReceipt(
                    receipt_id=existing["receipt_id"],
                    receipt_digest=existing["receipt_digest"],
                    revision_id=existing["revision_id"],
                    prior_digest=existing["prior_digest"],
                    observed_digest=existing["observed_digest"],
                    inventory_digest=existing["inventory_digest"],
                    lifecycle_digest=existing["lifecycle_digest"],
                    idempotent_retry=True,
                )
            stale = currentness.get("stale")
            expected_stale = [
                {
                    "id": "bridge-versioned-files",
                    "observed": _WI5441_V4_RECOVERY_PRIOR_DIGEST,
                    "current": _WI5441_V4_RECOVERY_CURRENT_DIGEST,
                }
            ]
            if currentness.get("missing_revisions") != [] or stale != expected_stale:
                raise RegistryRecoveryRequired(
                    f"WI-5441 recovery requires the exact sole-stale bridge aggregate: {currentness}"
                )
            record = next((item for item in snapshot.records if item.id == "bridge-versioned-files"), None)
            if record is None:
                raise RegistryRecoveryRequired("bridge-versioned-files is absent from the coherent registry")
            now = _utc_now()
            conn.execute("BEGIN IMMEDIATE")
            revision_id = _append_revision(
                conn,
                project_root=paths.project_root,
                record=record,
                actor_session=actor_session,
                operation="wi5441_bridge_aggregate_recovery",
                changed_by=changed_by,
                changed_at=now,
                change_reason=change_reason,
                bridge_id=bridge_id,
                start_packet_hash=start_packet_hash,
                pauth_decision=json.dumps(
                    {"authorization_id": pauth_id, "operation": "wi5441_bridge_aggregate_recovery"},
                    sort_keys=True,
                ),
                evidence_view="recovery",
                evidence_source_reference=bridge_id,
            )
            revision = conn.execute(
                "SELECT content_digest FROM sot_artifact_revisions WHERE revision_id = ?",
                (revision_id,),
            ).fetchone()
            if revision is None or revision["content_digest"] != _WI5441_V4_RECOVERY_CURRENT_DIGEST:
                raise RegistryRecoveryRequired("bridge aggregate revision did not bind the reviewed current digest")
            receipt_id = f"bridge-recovery-{uuid.uuid4()}"
            evidence = {
                "request": request,
                "inventory": inventory,
                "lifecycle": lifecycle,
                "revision_id": revision_id,
            }
            receipt_digest = _json_digest(evidence)
            conn.execute(
                """
                INSERT INTO sot_registry_bridge_recovery_receipts (
                    receipt_id, request_digest, receipt_digest, revision_id,
                    prior_digest, observed_digest, inventory_digest,
                    lifecycle_digest, evidence_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    receipt_id,
                    request_digest,
                    receipt_digest,
                    revision_id,
                    _WI5441_V4_RECOVERY_PRIOR_DIGEST,
                    _WI5441_V4_RECOVERY_CURRENT_DIGEST,
                    _json_digest(inventory),
                    lifecycle_digest,
                    json.dumps(evidence, sort_keys=True),
                    now,
                ),
            )
            conn.commit()
        except Exception:
            if conn.in_transaction:
                conn.rollback()
            raise
        finally:
            conn.close()
        final_snapshot = _load_snapshot_unlocked(paths)
        final_currentness = registry_currentness(
            final_snapshot,
            project_root=paths.project_root,
            db_path=paths.db_path,
        )
        if not final_currentness["current"]:
            raise RegistryRecoveryRequired(
                f"WI-5441 bridge recovery committed but registry remains stale: {final_currentness}"
            )
        return BridgeAggregateRecoveryReceipt(
            receipt_id=receipt_id,
            receipt_digest=receipt_digest,
            revision_id=revision_id,
            prior_digest=_WI5441_V4_RECOVERY_PRIOR_DIGEST,
            observed_digest=_WI5441_V4_RECOVERY_CURRENT_DIGEST,
            inventory_digest=_json_digest(inventory),
            lifecycle_digest=lifecycle_digest,
        )


def inspect_registry(
    *,
    project_root: Path | None = None,
    registry_path: Path | None = None,
    packaged_registry_path: Path | None = None,
    db_path: Path | None = None,
    include_census: bool = True,
) -> dict[str, Any]:
    paths = RegistryPaths.resolve(
        project_root=project_root,
        registry_path=registry_path,
        packaged_registry_path=packaged_registry_path,
        db_path=db_path,
    )
    journal = _nonterminal_journal(paths.db_path)
    if journal is not None:
        return {
            "coherent": False,
            "error": "registry_transaction_in_progress",
            "journal_id": journal["journal_id"],
            "journal_state": journal["journal_state"],
        }
    try:
        snapshot = load_registry_snapshot(
            project_root=paths.project_root,
            registry_path=paths.registry_path,
            packaged_registry_path=paths.packaged_registry_path,
            db_path=paths.db_path,
        )
    except Exception as exc:  # noqa: BLE001 - inspect must report typed authority failures.
        return {"coherent": False, "error": type(exc).__name__, "detail": str(exc)}
    identity_state = registry_identity_state(snapshot, project_root=paths.project_root)
    report: dict[str, Any] = {
        "coherent": True,
        "record_count": len(snapshot.records),
        "declaration_digest": snapshot.declaration_digest,
        "packaged_digest": snapshot.packaged_digest,
        "projection_digest": snapshot.projection_digest,
        "generation_digest": snapshot.generation_digest,
        "identity_state": identity_state,
    }
    if include_census:
        from groundtruth_kb.project.artifact_membership_reconciliation import (
            reconcile_artifact_membership,
            reconciliation_summary,
        )

        reconciliation = reconcile_artifact_membership(
            paths.project_root,
            snapshot=snapshot,
            db_path=paths.db_path,
        )
        summary = reconciliation_summary(reconciliation)
        report["membership_reconciliation"] = summary
        report["currentness"] = {
            "current": summary["audit_complete"],
            "audit_only": True,
            "missing_revisions": [
                gap["registry_id"] for gap in summary["audit_gaps"] if gap["kind"] == "missing_revision"
            ],
            "stale": [
                {key: value for key, value in gap.items() if key != "kind"}
                for gap in summary["audit_gaps"]
                if gap["kind"] == "stale_content_observation"
            ],
        }
        report["reverse_coverage"] = {
            "object_count": sum(summary["counts"].values()),
            "counts": summary["counts"],
            "gaps": [
                entry
                for entry in reconciliation["entries"]
                if entry["membership_class"] in {"unregistered_load_bearing", "invalid_unknown"}
            ],
        }
    else:
        report["currentness"] = {
            "current": None,
            "audit_only": True,
            "audit_performed": False,
            "missing_revisions": [],
            "stale": [],
        }
    return report


def validate_registry(
    *,
    project_root: Path | None = None,
    registry_path: Path | None = None,
    packaged_registry_path: Path | None = None,
    db_path: Path | None = None,
    require_reverse_closure: bool = True,
) -> dict[str, Any]:
    report = inspect_registry(
        project_root=project_root,
        registry_path=registry_path,
        packaged_registry_path=packaged_registry_path,
        db_path=db_path,
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
