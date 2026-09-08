#!/usr/bin/env python3
"""Pre-commit gate for protected-surface GO or VERIFIED evidence."""

from __future__ import annotations

import argparse
import concurrent.futures
import functools
import hashlib
import json
import os
import re
import sqlite3
import stat
import subprocess
import sys
import tempfile
import time
import unicodedata
from collections.abc import Iterator
from contextlib import contextmanager, nullcontext
from dataclasses import dataclass, replace
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
PACKAGE_SRC = PROJECT_ROOT / "groundtruth-kb" / "src"
if str(PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC))

from scripts.bridge_author_metadata import (  # noqa: E402
    author_metadata_gaps,
    extract_author_metadata,
    is_synthetic_session_context_id,
)
from scripts.bridge_lifecycle_resolver import (  # noqa: E402
    BridgeLifecycleResolutionError,
    resolve_bridge_lifecycle,
)
from scripts.bridge_review_independence import verdict_self_review_reason  # noqa: E402
from scripts.controlled_artifact_paths import (  # noqa: E402
    classify_controlled_artifact,
    is_versioned_bridge_status_file,
    registry_snapshot_cache_scope,
)
from scripts.gtkb_bridge_writer import BridgeComplianceError  # noqa: E402
from scripts.gtkb_session_id import resolve_session_id  # noqa: E402
from scripts.implementation_authorization import (  # noqa: E402
    PROJECT_AUTHORIZATION_KEYS,
    AuthorizationError,
    canonical_go_authorizations,
    extract_metadata_value,
    extract_target_paths,
    groundtruth_db_path,
    list_named_packets,
    load_named_packet,
    packet_hash,
    packet_path_for_bridge,
    parse_iso,
    path_authorized,
    validate_packet_project_authorization_operation,
)
from scripts.verdict_evidence_anchor_preflight import validate_verdict_evidence_anchors  # noqa: E402

BY_BRIDGE_PACKETS_REL = Path(".gtkb-state/implementation-authorizations/by-bridge")
BATCH_FINALIZATION_ENV = "GTKB_BATCH_VERIFIED_FINALIZATION_MANIFEST"
BATCH_FINALIZATION_REL = Path(".gtkb-state/batch-verified-finalization")
BATCH_FINALIZATION_AUTHORITY = "gtkb-wi6073-batch-verified-finalization"
BATCH_FINALIZATION_OWNER_DECISION = "DELIB-20260808-GOVERNED-BATCH-FINALIZATION-PATH"
BATCH_FINALIZATION_PAUTH = "PAUTH-PROJECT-GTKB-SESSION-ENVELOPE-WHOLE-PROJECT-20260808"
BATCH_FINALIZATION_MAX_BYTES = 64 * 1024
VERSIONED_BRIDGE_RE = re.compile(r"^bridge/.+-\d{3}\.md$")
VERSIONED_BRIDGE_CAPTURE_RE = re.compile(r"^bridge/(?P<bridge_id>[A-Za-z0-9][A-Za-z0-9_.-]*)-(?P<version>\d{3})\.md$")
TRANSIENT_INDEX_PATH_RE = re.compile(r"\.gtkb-index-[a-z0-9_]{8}/index")
STATUS_RE = re.compile(r"^(NEW|REVISED|GO|NO-GO|NO-ACTION|VERIFIED|DEFERRED|WITHDRAWN|ADVISORY)$")
IMPLEMENTATION_REPORT_RE = re.compile(r"(?mi)^bridge_kind:\s*implementation_report\s*$")
CONTROLLING_GO_RE = re.compile(r"(?mi)^Controlling GO:\s*`?(bridge/[A-Za-z0-9][A-Za-z0-9_.-]*-\d{3}\.md)`?\s*$")
MANIFEST_PATH_RE = re.compile(r"^-\s+`([^`]+)`\s*$")
GLOB_META_RE = re.compile(r"[*?\[\]]")
AUTHOR_SESSION_RE = re.compile(r"(?mi)^author_session_context_id:\s*(\S+)\s*$")
GIT_OBJECT_FORMATS = {"sha1": 40, "sha256": 64}
MAX_BLOB_BYTES = 64 * 1024 * 1024
MAX_TREE_BYTES = 512 * 1024 * 1024
PAUTH_READ_SNAPSHOT_REL = "groundtruth.db"
PAUTH_READ_SNAPSHOT_VERSION = 1
PAUTH_READ_SNAPSHOT_APPLICATION_ID = 0x47544B42
PAUTH_READ_SNAPSHOT_STATUSES = {"GO", "NO-GO", "VERIFIED"}
PAUTH_READ_SNAPSHOT_SIDECAR_SUFFIXES = ("-journal", "-wal", "-shm")
PAUTH_READ_SNAPSHOT_RELATIONS: tuple[tuple[str, tuple[tuple[str, str], ...]], ...] = (
    (
        "current_specifications",
        (
            ("id", "TEXT"),
            ("version", "INTEGER"),
            ("title", "TEXT"),
            ("status", "TEXT"),
            ("type", "TEXT"),
        ),
    ),
    (
        "current_projects",
        (
            ("id", "TEXT"),
            ("version", "INTEGER"),
            ("status", "TEXT"),
            ("parent_project_id", "TEXT"),
        ),
    ),
    (
        "current_project_work_item_memberships",
        (
            ("id", "TEXT"),
            ("version", "INTEGER"),
            ("project_id", "TEXT"),
            ("work_item_id", "TEXT"),
            ("status", "TEXT"),
        ),
    ),
)
PAUTH_READ_SNAPSHOT_RELATION_NAMES = tuple(name for name, _columns in PAUTH_READ_SNAPSHOT_RELATIONS)
WINDOWS_RESERVED_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{number}" for number in range(1, 10)),
    *(f"LPT{number}" for number in range(1, 10)),
}

EXTRA_PROTECTED_PREFIXES = (".githooks/",)


class GateError(RuntimeError):
    """Raised when the commit gate cannot evaluate safely."""


# WI-5742 Layer A: fail-closed wall-clock bound on the full staged evaluation.
#
# Before this bound existed the gate had a per-subprocess Git timeout but no
# outer budget, so one evaluation could run for minutes while the parent
# ``git commit`` waited. Measured on the live repository at 241.7s wall against
# a 120s bridge-publication capability TTL, the gate routinely outlived the
# capability minted for the publication it was gating -- which is the mechanism
# that stranded terminal VERIFIED verdicts with no backing commit.
#
# The budget denies on exhaustion. It never passes on timeout and never hangs.
_EVALUATION_PHASES = (
    "index_snapshot",
    "classification",
    "registry_assessment",
    "live_go_evidence",
    "verified_evidence",
    "transaction_evidence",
    "per_path",
)


# Share of elapsed wall-clock spent blocked that classifies a denial as
# contention-dominant. This is a ratio, not a timer literal (WI-5867 AC9).
_BLOCKED_SHARE_CONTENTION_DOMINANT = 0.5


class EvaluationBoundExceeded(GateError):
    """Raised when a staged evaluation exhausts its configured wall-clock budget."""

    def __init__(
        self,
        *,
        phase: str,
        elapsed: float,
        bound: float,
        source: str,
        work_seconds: float | None = None,
        blocked_seconds: float = 0.0,
        dominant_blocking_reason: str | None = None,
        blocked_share: float = 0.0,
    ) -> None:
        self.phase = phase
        self.elapsed = elapsed
        self.bound = bound
        self.source = source
        self.blocked_seconds = float(blocked_seconds)
        self.work_seconds = float(elapsed if work_seconds is None else work_seconds)
        self.dominant_blocking_reason = dominant_blocking_reason
        self.blocked_share = float(blocked_share)
        self.contention_dominant = self.blocked_share >= _BLOCKED_SHARE_CONTENTION_DOMINANT
        super().__init__(
            f"protected-commit evaluation exceeded its {bound:g}s budget while executing phase "
            f"{phase!r} (elapsed {elapsed:.1f}s; bound resolved from {source})"
        )

    def as_result(self) -> dict[str, Any]:
        """Render the exhaustion as a deterministic deny verdict with phase evidence."""
        if self.contention_dominant:
            reason_text = self.dominant_blocking_reason or "unspecified wait"
            remediation = (
                "remediation: evaluation spent most of its budget blocked "
                f"({self.blocked_share:.0%} on {reason_text}). Raising "
                "evaluation_bound_seconds is not the indicated remedy under starvation. "
                "Retry under quiescence. Contention reduction is tracked by WI-5784 "
                "(claim-registry locks), not by enlarging this bound."
            )
        else:
            remediation = (
                "remediation: re-run the commit; if this recurs, the phase named above is the "
                "slow phase to investigate. Raise evaluation_bound_seconds in "
                "config/governance/protected-commit-timers.toml only up to (not including) the "
                "paired bridge_publication_capability_ttl_seconds -- a bound at or above that TTL "
                "re-creates the publication-stranding precondition and is rejected by the accessor."
            )
        return {
            "status": "fail",
            "findings": [
                {
                    "path": "<evaluation-bound>",
                    "reason": (
                        f"protected-commit evaluation exceeded its configured {self.bound:g}s wall-clock "
                        f"bound while executing phase {self.phase!r}"
                    ),
                    "evidence_errors": [
                        f"executing phase: {self.phase}",
                        f"elapsed: {self.elapsed:.1f}s",
                        f"configured bound: {self.bound:g}s",
                        f"bound source: {self.source}",
                        f"work_seconds: {self.work_seconds:.1f}s",
                        f"blocked_seconds: {self.blocked_seconds:.1f}s",
                        f"dominant_blocking_reason: {self.dominant_blocking_reason or 'none'}",
                        remediation,
                    ],
                }
            ],
            "cleared": [],
            "skipped_unprotected": [],
            "protected_paths": [],
            "audit_gaps": [],
            "evaluation_bound": {
                "exhausted": True,
                "phase": self.phase,
                "elapsed_seconds": round(self.elapsed, 3),
                "bound_seconds": self.bound,
                "source": self.source,
                "work_seconds": round(self.work_seconds, 3),
                "blocked_seconds": round(self.blocked_seconds, 3),
                "dominant_blocking_reason": self.dominant_blocking_reason,
                "blocked_share": round(self.blocked_share, 4),
                "contention_dominant": self.contention_dominant,
            },
            "evidence_summary": {
                "live_go_packets_scanned": 0,
                "live_go_packets_valid": 0,
                "terminal_verified_packets_scanned": 0,
                "terminal_verified_threads_loaded": 0,
            },
        }


class _EvaluationBudget:
    """Monotonic wall-clock budget with phase tracking for one staged evaluation."""

    def __init__(self, bound_seconds: float, *, source: str, clock: Any = None) -> None:
        self._bound = float(bound_seconds)
        self._source = source
        self._clock = clock or time.monotonic
        self._start = self._clock()
        self._phase = "startup"
        self._blocked_seconds = 0.0
        self._blocked_by_reason: dict[str, float] = {}
        self._blocked_by_phase: dict[str, float] = {}
        self._block_depth = 0

    @property
    def phase(self) -> str:
        return self._phase

    @property
    def bound_seconds(self) -> float:
        return self._bound

    @property
    def blocked_seconds(self) -> float:
        return float(self._blocked_seconds)

    @property
    def work_seconds(self) -> float:
        return max(0.0, self.elapsed() - self._blocked_seconds)

    @property
    def blocked_by_reason(self) -> dict[str, float]:
        return dict(self._blocked_by_reason)

    @property
    def blocked_by_phase(self) -> dict[str, float]:
        return dict(self._blocked_by_phase)

    @property
    def dominant_blocking_reason(self) -> str | None:
        if not self._blocked_by_reason:
            return None
        return max(self._blocked_by_reason.items(), key=lambda item: item[1])[0]

    @property
    def blocked_share(self) -> float:
        elapsed = self.elapsed()
        if elapsed <= 0:
            return 0.0
        return min(1.0, self._blocked_seconds / elapsed)

    @property
    def is_contention_dominant(self) -> bool:
        return self.blocked_share >= _BLOCKED_SHARE_CONTENTION_DOMINANT

    def elapsed(self) -> float:
        return float(self._clock() - self._start)

    @contextmanager
    def blocked(self, reason: str) -> Iterator[None]:
        """Record wall-clock spent waiting on an external resource (measurement only)."""
        start = self._clock()
        self._block_depth += 1
        try:
            yield
        finally:
            duration = max(0.0, float(self._clock() - start))
            self._block_depth -= 1
            self._blocked_by_reason[reason] = self._blocked_by_reason.get(reason, 0.0) + duration
            self._blocked_by_phase[self._phase] = self._blocked_by_phase.get(self._phase, 0.0) + duration
            if self._block_depth == 0:
                self._blocked_seconds += duration

    def enter(self, phase: str) -> None:
        """Mark the phase now executing, then check the budget before doing its work."""
        self._phase = phase
        self.check()

    def check(self) -> None:
        elapsed = self.elapsed()
        if elapsed > self._bound:
            raise EvaluationBoundExceeded(
                phase=self._phase,
                elapsed=elapsed,
                bound=self._bound,
                source=self._source,
                work_seconds=self.work_seconds,
                blocked_seconds=self.blocked_seconds,
                dominant_blocking_reason=self.dominant_blocking_reason,
                blocked_share=self.blocked_share,
            )


def _resolve_evaluation_budget(root: Path) -> _EvaluationBudget:
    """Resolve the configured bound through the single timer-config path.

    Fails closed: an unreadable or invariant-violating timer configuration is a
    gate error, never an unbounded evaluation.
    """
    package_src = root / "groundtruth-kb" / "src"
    if str(package_src) not in sys.path:
        sys.path.insert(0, str(package_src))
    try:
        from groundtruth_kb.project.timer_config import resolve_protected_commit_timers

        timers = resolve_protected_commit_timers(root)
    except Exception as exc:  # noqa: BLE001 - commit authority fails closed
        raise GateError(f"protected-commit timer configuration is unusable: {exc}") from exc
    return _EvaluationBudget(timers.evaluation_bound_seconds, source=timers.source)


@dataclass(frozen=True, slots=True)
class _IndexSnapshot:
    env: dict[str, str]
    head_oid: str
    object_format: str
    selected_paths: tuple[str, ...]
    status_by_path: dict[str, str]
    index_file: Path
    index_file_identity: _PathIdentity
    index_root_identity: _PathIdentity

    @property
    def added_paths(self) -> set[str]:
        return {path for path, status in self.status_by_path.items() if status == "A"}


@dataclass(frozen=True, slots=True)
class _ApprovedChain:
    proposal_path: str
    go_path: str
    report_path: str
    target_paths: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class _IndexEntry:
    mode: str
    oid: str
    rel_path: str


@dataclass(frozen=True, slots=True)
class _PAuthSourceIdentity:
    resolved_path: str
    device: int
    inode: int
    link_count: int
    mode: int


@dataclass(frozen=True, slots=True)
class _PAuthProjectionIdentity:
    resolved_path: str
    device: int
    inode: int
    link_count: int


@dataclass(frozen=True, slots=True)
class _PAuthRelationObservation:
    name: str
    schema_sha256: str
    row_count: int
    rows_sha256: str


@dataclass(frozen=True, slots=True)
class _PAuthAuthorityObservation:
    data_version: int
    schema_version: int
    relations: tuple[_PAuthRelationObservation, ...]


@dataclass(frozen=True, slots=True)
class _PAuthReadSnapshotEvidence:
    construction_version: int
    source_identity: _PAuthSourceIdentity
    relations: tuple[_PAuthRelationObservation, ...]


@dataclass(frozen=True, slots=True)
class _LedgerEntry:
    mode: str
    sha256: str
    size: int
    device: int
    inode: int
    link_count: int
    # WI-5659 mechanism 3 (in-ledger; DELIB-202667186 / DELIB-202667188): an index
    # entry whose blob exceeded MAX_BLOB_BYTES is recorded IN the ledger with
    # content_exempt=True, carrying its mode, index object id (`oid`), and declared
    # `size`, but is NOT copied to disk. Keeping every index entry in the one
    # verifier-recognised structure (per the owner decision) instead of a parallel
    # map lets _verify_snapshot_ledger prove enumeration completeness and enforce
    # that no content file exists at an exempt path. For exempt entries
    # device/inode/link_count are 0 (no on-disk file) and sha256 is the streamed
    # content hash.
    content_exempt: bool = False
    oid: str = ""
    pauth_read_snapshot: _PAuthReadSnapshotEvidence | None = None


@dataclass(frozen=True, slots=True)
class _PathIdentity:
    resolved_path: str
    device: int
    inode: int
    link_count: int
    size: int
    mode: int
    sha256: str | None = None


@dataclass(frozen=True, slots=True)
class _BridgeSnapshot:
    root: Path
    ledger: dict[str, _LedgerEntry]
    pauth_source_identity: _PAuthSourceIdentity | None = None


def _normalize_rel(path_text: str) -> str:
    rel = path_text.strip().replace("\\", "/")
    while rel.startswith("./"):
        rel = rel[2:]
    return rel


def _is_narrative_artifact(rel_path: str) -> bool:
    name = Path(rel_path).name
    if rel_path == "AGENTS.md":
        return True
    if name.startswith("CLAUDE") and name.endswith(".md"):
        return rel_path == name or rel_path.startswith("applications/")
    return rel_path.startswith(".claude/rules/") and rel_path.endswith(".md")


def is_protected_path(rel_path: str, *, project_root: Path | None = None) -> bool:
    rel = _normalize_rel(rel_path)
    if _is_narrative_artifact(rel):
        return False
    if rel.startswith(EXTRA_PROTECTED_PREFIXES):
        return True
    if is_versioned_bridge_status_file(rel):
        return False
    return classify_controlled_artifact(rel, project_root=project_root).is_controlled


def _windows_authority_git_candidates() -> tuple[Path, ...]:
    candidates: list[Path] = [
        Path(r"C:\Program Files\Git\cmd\git.exe"),
        Path(r"C:\Program Files\Git\bin\git.exe"),
    ]
    try:
        import winreg

        access_modes = (winreg.KEY_READ | winreg.KEY_WOW64_64KEY, winreg.KEY_READ | winreg.KEY_WOW64_32KEY)
        for access in access_modes:
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\GitForWindows", 0, access) as key:
                    install_path, _ = winreg.QueryValueEx(key, "InstallPath")
            except OSError:
                continue
            if isinstance(install_path, str) and Path(install_path).is_absolute():
                candidates.extend(
                    (
                        Path(install_path) / "cmd" / "git.exe",
                        Path(install_path) / "bin" / "git.exe",
                    )
                )
    except (ImportError, AttributeError):
        pass
    return tuple(dict.fromkeys(candidates))


def _authority_git_candidates() -> tuple[Path, ...]:
    if os.name == "nt":
        return _windows_authority_git_candidates()
    return (Path("/usr/bin/git"), Path("/usr/local/bin/git"))


def _authority_bound_executable(candidate: Path) -> str | None:
    try:
        resolved = candidate.resolve(strict=True)
        if not resolved.is_file() or _path_is_linklike(candidate) or _path_is_linklike(resolved):
            return None
        if os.name != "nt":
            for path in (resolved, *resolved.parents):
                info = path.stat()
                if info.st_uid != 0 or info.st_mode & (stat.S_IWGRP | stat.S_IWOTH):
                    return None
                if path == Path("/"):
                    break
    except OSError:
        return None
    return str(resolved)


@functools.lru_cache(maxsize=1)
def _trusted_git_executable() -> str:
    for candidate in _authority_git_candidates():
        executable = _authority_bound_executable(candidate)
        if executable is not None:
            return executable
    raise GateError("authority-bound Git executable is unavailable")


def _sanitized_subprocess_env(
    *,
    index_file: Path | None = None,
    isolate_python: bool = False,
) -> dict[str, str]:
    env: dict[str, str] = {}
    for key in ("SYSTEMROOT", "WINDIR", "COMSPEC", "PATHEXT", "TEMP", "TMP", "TMPDIR"):
        value = os.environ.get(key)
        if value:
            env[key] = value
    path_entries = [str(Path(_trusted_git_executable()).parent)]
    system_root = env.get("SYSTEMROOT") or env.get("WINDIR")
    if system_root:
        path_entries.append(str(Path(system_root) / "System32"))
    env.update(
        {
            "PATH": os.pathsep.join(dict.fromkeys(path_entries)),
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_NO_REPLACE_OBJECTS": "1",
            "GIT_OPTIONAL_LOCKS": "0",
            "LC_ALL": "C",
            "LANG": "C",
        }
    )
    if index_file is not None:
        env["GIT_INDEX_FILE"] = str(index_file.resolve())
    if isolate_python:
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["PYTHONNOUSERSITE"] = "1"
    return env


def _git_command(*args: str) -> list[str]:
    return [
        _trusted_git_executable(),
        "--no-replace-objects",
        "-c",
        "core.fsmonitor=false",
        "-c",
        f"core.hooksPath={os.devnull}",
        *args,
    ]


# WI-5658: bound every checker git subprocess so a blocked/slow git call fails
# closed instead of grinding unbounded (honors the git-subprocess timeout-bound
# invariant relied on by the finalizer / pre-commit gate).
_GIT_SUBPROCESS_TIMEOUT_SECONDS = 120


def _run_git(
    root: Path,
    *args: str,
    env: dict[str, str] | None = None,
    text: bool = False,
    timeout: float | None = _GIT_SUBPROCESS_TIMEOUT_SECONDS,
) -> subprocess.CompletedProcess[Any]:
    try:
        return subprocess.run(
            _git_command(*args),
            cwd=root,
            capture_output=True,
            text=text,
            encoding="utf-8" if text else None,
            errors="replace" if text else None,
            check=False,
            env=env or _sanitized_subprocess_env(),
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        message = f"git subprocess timed out after {timeout}s: {' '.join(str(a) for a in args)}"
        return subprocess.CompletedProcess(
            exc.cmd,
            returncode=124,
            stdout=exc.stdout if exc.stdout is not None else ("" if text else b""),
            stderr=message if text else message.encode("utf-8"),
        )


def _git_object_text(root: Path, object_spec: str, *, env: dict[str, str] | None = None) -> str:
    result = _run_git(root, "show", object_spec, env=env, text=True)
    if result.returncode != 0:
        raise GateError(f"could not read Git object {object_spec}: {result.stderr.strip()}")
    return result.stdout


def _resolve_head_oid(root: Path, budget: _EvaluationBudget | None = None) -> str | None:
    result = _run_git(root, "rev-parse", "--verify", "HEAD^{commit}", text=True)
    if result.returncode != 0:
        return None
    oid = result.stdout.strip()
    return oid or None


def _resolve_head_ref(root: Path, head_oid: str | None = None) -> str | None:
    result = _run_git(root, "symbolic-ref", "-q", "HEAD", text=True)
    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip()
    oid = head_oid or _resolve_head_oid(root)
    return f"DETACHED:{oid}" if oid else None


def _resolve_object_format(root: Path) -> str:
    result = _run_git(root, "rev-parse", "--show-object-format", text=True)
    value = result.stdout.strip().lower() if result.returncode == 0 else ""
    if value not in GIT_OBJECT_FORMATS:
        raise GateError(f"unsupported or unreadable Git object format {value!r}")
    return value


def _decode_git_path(raw: bytes) -> str:
    return _validated_index_path(raw)


def _parse_staged_name_status(raw: bytes) -> tuple[tuple[str, ...], dict[str, str]]:
    tokens = raw.split(b"\0")
    if tokens and tokens[-1] == b"":
        tokens.pop()
    selected: list[str] = []
    statuses: dict[str, str] = {}
    index = 0
    while index < len(tokens):
        status_text = tokens[index].decode("ascii", errors="strict")
        index += 1
        code = status_text[:1]
        if code in {"R", "C"}:
            if index + 1 >= len(tokens):
                raise GateError(f"truncated staged {code} record")
            old_path = _decode_git_path(tokens[index])
            new_path = _decode_git_path(tokens[index + 1])
            index += 2
            records = ((old_path, f"{code}-source"), (new_path, f"{code}-destination"))
        elif code in {"A", "M", "D"}:
            if index >= len(tokens):
                raise GateError(f"truncated staged {code} record")
            records = ((_decode_git_path(tokens[index]), code),)
            index += 1
        else:
            raise GateError(f"unsupported staged Git status {status_text!r}")

        for rel_path, path_status in records:
            if not rel_path or Path(rel_path).is_absolute() or ".." in Path(rel_path).parts:
                raise GateError(f"invalid staged path {rel_path!r}")
            if rel_path in statuses:
                raise GateError(f"duplicate staged path record {rel_path!r}")
            statuses[rel_path] = path_status
            selected.append(rel_path)
    return tuple(selected), statuses


def _validated_index_path(raw_path: bytes) -> str:
    try:
        decoded = raw_path.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise GateError("index contains a path that is not valid UTF-8") from exc
    if decoded != decoded.strip() or "\\" in decoded or any(ord(character) < 32 for character in decoded):
        raise GateError(f"index contains non-canonical path bytes {decoded!r}")
    rel_path = decoded
    raw_parts = rel_path.split("/")
    parts = Path(rel_path).parts
    if (
        not rel_path
        or Path(rel_path).is_absolute()
        or any(part in {"", ".", ".."} for part in raw_parts)
        or ".." in parts
        or parts[0].lower() == ".git"
        or any(":" in part for part in parts)
        or any(part.endswith((".", " ")) for part in raw_parts)
    ):
        raise GateError(f"index contains unsafe path {rel_path!r}")
    for part in raw_parts:
        stem = part.split(".", 1)[0].rstrip(" .").upper()
        if stem in WINDOWS_RESERVED_NAMES:
            raise GateError(f"index contains platform-reserved path component {part!r}")
    return rel_path


def _parse_index_inventory(raw: bytes) -> tuple[_IndexEntry, ...]:
    records = raw.split(b"\0")
    if records and records[-1] == b"":
        records.pop()
    entries: list[_IndexEntry] = []
    seen: set[str] = set()
    collision_keys: dict[str, str] = {}
    for record in records:
        try:
            metadata, raw_path = record.split(b"\t", 1)
            mode_raw, oid_raw, stage_raw = metadata.split(b" ", 2)
            mode = mode_raw.decode("ascii", errors="strict")
            oid = oid_raw.decode("ascii", errors="strict")
            stage = stage_raw.decode("ascii", errors="strict")
        except (UnicodeDecodeError, ValueError) as exc:
            raise GateError("malformed stage-0 index inventory record") from exc
        if stage != "0":
            raise GateError(f"unmerged index entry is not eligible for authorization materialization: stage {stage}")
        if mode not in {"100644", "100755"}:
            raise GateError(f"unsupported index mode {mode}; only regular files are eligible")
        if not re.fullmatch(r"[0-9a-fA-F]{40,64}", oid):
            raise GateError(f"invalid index object id {oid!r}")
        rel_path = _validated_index_path(raw_path)
        if rel_path in seen:
            raise GateError(f"duplicate stage-0 index path {rel_path!r}")
        collision_key = unicodedata.normalize("NFC", rel_path).casefold()
        collision = collision_keys.get(collision_key)
        if collision is not None and collision != rel_path:
            raise GateError(f"casefold or Unicode-normalized index path collision: {collision!r}, {rel_path!r}")
        seen.add(rel_path)
        collision_keys[collision_key] = rel_path
        entries.append(_IndexEntry(mode=mode, oid=oid, rel_path=rel_path))
    return tuple(entries)


def _path_is_linklike(path: Path) -> bool:
    try:
        info = path.lstat()
    except OSError:
        return False
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    file_attributes = getattr(info, "st_file_attributes", 0)
    return path.is_symlink() or bool(reparse_flag and file_attributes & reparse_flag)


def _path_identity(path: Path, *, hash_bytes: bool = False) -> _PathIdentity:
    if _path_is_linklike(path):
        raise GateError(f"guarded authority path is symlink, junction, or reparse point: {path}")
    try:
        info = path.stat()
        resolved = path.resolve(strict=True)
    except OSError as exc:
        raise GateError(f"could not bind guarded authority path {path}: {exc}") from exc
    digest = hashlib.sha256(path.read_bytes()).hexdigest() if hash_bytes else None
    return _PathIdentity(
        resolved_path=str(resolved),
        device=info.st_dev,
        inode=info.st_ino,
        link_count=info.st_nlink,
        size=info.st_size,
        mode=stat.S_IMODE(info.st_mode),
        sha256=digest,
    )


def _verify_path_identity(path: Path, expected: _PathIdentity) -> None:
    actual = _path_identity(path, hash_bytes=expected.sha256 is not None)
    if actual != expected:
        raise GateError(f"guarded authority path identity or bytes drifted during evaluation: {path}")


def _pauth_source_identity(root: Path, path: Path) -> _PAuthSourceIdentity:
    """Bind the canonical PAUTH source without hashing unrelated database bytes."""

    try:
        canonical_root = root.resolve(strict=True)
    except OSError as exc:
        raise GateError(f"canonical PAUTH read snapshot root is unavailable: {exc}") from exc
    expected = canonical_root / PAUTH_READ_SNAPSHOT_REL
    if path != expected or path.parent != canonical_root:
        raise GateError("PAUTH read snapshot source is not the canonical live-root groundtruth.db")
    if _path_is_linklike(canonical_root) or _path_is_linklike(path):
        raise GateError("PAUTH read snapshot source is symlinked, junctioned, or reparse-point redirected")
    try:
        info = path.stat()
        resolved = path.resolve(strict=True)
    except OSError as exc:
        raise GateError(f"canonical PAUTH read snapshot source is unavailable: {exc}") from exc
    if not path.is_file() or resolved != expected:
        raise GateError("PAUTH read snapshot source is not the canonical regular database file")
    return _PAuthSourceIdentity(
        resolved_path=str(resolved),
        device=info.st_dev,
        inode=info.st_ino,
        link_count=info.st_nlink,
        mode=stat.S_IMODE(info.st_mode),
    )


def _verify_pauth_source_identity(root: Path, path: Path, expected: _PAuthSourceIdentity) -> None:
    if _pauth_source_identity(root, path) != expected:
        raise GateError("canonical PAUTH read snapshot source identity changed during evaluation")


def _pauth_projection_identity(path: Path) -> _PAuthProjectionIdentity:
    if _path_is_linklike(path):
        raise GateError("PAUTH read snapshot destination is symlinked, junctioned, or reparse-point redirected")
    try:
        info = path.lstat()
        resolved = path.resolve(strict=True)
    except OSError as exc:
        raise GateError(f"PAUTH read snapshot destination is unavailable: {exc}") from exc
    if not stat.S_ISREG(info.st_mode) or resolved.parent != path.parent.resolve(strict=True):
        raise GateError("PAUTH read snapshot destination is not a direct regular file")
    return _PAuthProjectionIdentity(
        resolved_path=str(resolved),
        device=info.st_dev,
        inode=info.st_ino,
        link_count=info.st_nlink,
    )


def _verify_pauth_projection_identity(path: Path, expected: _PAuthProjectionIdentity) -> None:
    if _pauth_projection_identity(path) != expected:
        raise GateError("PAUTH read snapshot destination identity changed during evaluation")


def _pauth_projection_sidecar_paths(destination: Path) -> tuple[Path, ...]:
    return tuple(Path(str(destination) + suffix) for suffix in PAUTH_READ_SNAPSHOT_SIDECAR_SUFFIXES)


def _create_pauth_projection_sidecar_guards(destination: Path) -> dict[Path, _PathIdentity]:
    """Occupy every SQLite sidecar name with one retained, empty directory."""

    identities: dict[Path, _PathIdentity] = {}
    created: list[Path] = []
    try:
        for sidecar in _pauth_projection_sidecar_paths(destination):
            if _path_is_linklike(sidecar) or sidecar.exists():
                raise GateError(f"PAUTH read snapshot sidecar path is already occupied or redirected: {sidecar.name}")
            sidecar.mkdir(mode=0o755)
            created.append(sidecar)
            identity = _path_identity(sidecar)
            if not sidecar.is_dir():
                raise GateError(f"PAUTH read snapshot sidecar guard is not a directory: {sidecar.name}")
            identities[sidecar] = identity
        return identities
    except (GateError, OSError) as exc:
        for sidecar in reversed(created):
            try:
                if _path_is_linklike(sidecar) or sidecar.is_file():
                    sidecar.unlink()
                elif sidecar.is_dir():
                    sidecar.rmdir()
            except OSError:
                pass
        if isinstance(exc, GateError):
            raise
        raise GateError(f"could not create PAUTH read snapshot sidecar guards: {exc}") from exc


def _verify_pauth_projection_sidecar_guards(identities: dict[Path, _PathIdentity]) -> None:
    for path, expected in identities.items():
        if not path.is_dir() or _path_identity(path) != expected:
            raise GateError(f"PAUTH read snapshot sidecar guard changed during evaluation: {path.name}")


def _create_exclusive_pauth_projection_placeholder(destination: Path) -> tuple[int, _PAuthProjectionIdentity]:
    """Create the projection path exactly once and retain its no-follow descriptor."""

    if _path_is_linklike(destination):
        raise GateError("PAUTH read snapshot destination is redirected")
    flags = os.O_CREAT | os.O_EXCL | os.O_RDWR | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(destination, flags, 0o600)
    except OSError as exc:
        raise GateError(f"could not exclusively create PAUTH read snapshot destination: {exc}") from exc
    try:
        descriptor_info = os.fstat(descriptor)
        identity = _pauth_projection_identity(destination)
        if (
            not stat.S_ISREG(descriptor_info.st_mode)
            or descriptor_info.st_dev != identity.device
            or descriptor_info.st_ino != identity.inode
        ):
            raise GateError("PAUTH read snapshot exclusive destination binding is inconsistent")
        return descriptor, identity
    except (GateError, OSError) as exc:
        os.close(descriptor)
        try:
            destination.unlink()
        except OSError:
            pass
        if isinstance(exc, GateError):
            raise
        raise GateError(f"could not bind PAUTH read snapshot destination: {exc}") from exc


def _typed_sqlite_value(value: object, *, declared_type: str, relation: str, column: str) -> list[object]:
    if value is None:
        return ["null", None]
    if declared_type == "INTEGER" and isinstance(value, int) and not isinstance(value, bool):
        return ["integer", str(value)]
    if declared_type == "TEXT" and isinstance(value, str):
        return ["text", value]
    raise GateError(
        f"PAUTH read snapshot relation {relation}.{column} has unsupported value type "
        f"{type(value).__name__!r} for declared type {declared_type}"
    )


def _pauth_relation_schema(
    conn: sqlite3.Connection,
    relation: str,
    columns: tuple[tuple[str, str], ...],
    *,
    projection: bool,
) -> str:
    object_row = conn.execute("SELECT type FROM sqlite_master WHERE name = ?", (relation,)).fetchone()
    allowed_types = {"table"} if projection else {"table", "view"}
    if object_row is None or object_row[0] not in allowed_types:
        kind = "physical table" if projection else "table or view"
        raise GateError(f"PAUTH read snapshot relation {relation} is not a readable {kind}")
    schema_rows = conn.execute(f'PRAGMA table_info("{relation}")').fetchall()
    by_name = {str(row[1]): row for row in schema_rows}
    normalized: list[tuple[str, str, int, int]] = []
    for column, declared_type in columns:
        row = by_name.get(column)
        if row is None:
            raise GateError(f"PAUTH read snapshot relation {relation} is missing required column {column}")
        actual_type = str(row[2] or "").upper()
        not_null = int(row[3])
        primary_key_position = int(row[5])
        if actual_type != declared_type or not_null != 0 or primary_key_position != 0:
            raise GateError(
                f"PAUTH read snapshot relation {relation}.{column} has incompatible schema "
                f"({actual_type}, notnull={not_null}, pk={primary_key_position})"
            )
        normalized.append((column, declared_type, not_null, primary_key_position))
    encoded = json.dumps(normalized, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _observe_pauth_authority(
    conn: sqlite3.Connection,
    *,
    projection: bool,
    include_rows: bool = False,
) -> tuple[_PAuthAuthorityObservation, dict[str, tuple[tuple[object, ...], ...]]]:
    """Observe the exact four logical relations in one coherent read transaction."""

    rows_by_relation: dict[str, tuple[tuple[object, ...], ...]] = {}
    observations: list[_PAuthRelationObservation] = []
    try:
        conn.execute("BEGIN")
        data_version = int(conn.execute("PRAGMA data_version").fetchone()[0])
        schema_version = int(conn.execute("PRAGMA schema_version").fetchone()[0])
        for relation, columns in PAUTH_READ_SNAPSHOT_RELATIONS:
            schema_sha256 = _pauth_relation_schema(conn, relation, columns, projection=projection)
            column_sql = ", ".join(f'"{column}"' for column, _declared_type in columns)
            raw_rows = [tuple(row) for row in conn.execute(f'SELECT {column_sql} FROM "{relation}"').fetchall()]
            encoded_rows: list[tuple[bytes, tuple[object, ...]]] = []
            seen_ids: set[str] = set()
            for raw_row in raw_rows:
                identity = raw_row[0]
                if not isinstance(identity, str) or not identity:
                    raise GateError(f"PAUTH read snapshot relation {relation} has a missing or non-text id")
                if identity in seen_ids:
                    raise GateError(f"PAUTH read snapshot relation {relation} has duplicate id {identity!r}")
                seen_ids.add(identity)
                typed = [
                    _typed_sqlite_value(value, declared_type=declared_type, relation=relation, column=column)
                    for value, (column, declared_type) in zip(raw_row, columns, strict=True)
                ]
                encoded = json.dumps(typed, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
                encoded_rows.append((encoded, raw_row))
            encoded_rows.sort(key=lambda item: item[0])
            rows_payload = b"\n".join(encoded for encoded, _row in encoded_rows)
            observations.append(
                _PAuthRelationObservation(
                    name=relation,
                    schema_sha256=schema_sha256,
                    row_count=len(encoded_rows),
                    rows_sha256=hashlib.sha256(rows_payload).hexdigest(),
                )
            )
            if include_rows:
                rows_by_relation[relation] = tuple(row for _encoded, row in encoded_rows)
        conn.execute("COMMIT")
    except (GateError, sqlite3.Error) as exc:
        if conn.in_transaction:
            conn.execute("ROLLBACK")
        if isinstance(exc, GateError):
            raise
        raise GateError(f"PAUTH read snapshot authority relations are unreadable: {exc}") from exc
    return (
        _PAuthAuthorityObservation(
            data_version=data_version,
            schema_version=schema_version,
            relations=tuple(observations),
        ),
        rows_by_relation,
    )


def _verify_pauth_projection(path: Path, evidence: _PAuthReadSnapshotEvidence) -> None:
    if evidence.construction_version != PAUTH_READ_SNAPSHOT_VERSION:
        raise GateError("PAUTH read snapshot ledger construction version is unsupported")
    try:
        conn = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True, timeout=5)
        conn.execute("PRAGMA query_only=ON")
        if int(conn.execute("PRAGMA query_only").fetchone()[0]) != 1:
            raise GateError("PAUTH read snapshot projection connection is not query-only")
        database_path = Path(str(conn.execute("PRAGMA database_list").fetchone()[2])).resolve(strict=True)
        if database_path != path.resolve(strict=True):
            raise GateError("PAUTH read snapshot consumer opened a different database path")
        application_id = int(conn.execute("PRAGMA application_id").fetchone()[0])
        user_version = int(conn.execute("PRAGMA user_version").fetchone()[0])
        if application_id != PAUTH_READ_SNAPSHOT_APPLICATION_ID or user_version != PAUTH_READ_SNAPSHOT_VERSION:
            raise GateError("PAUTH read snapshot producer/consumer construction identity mismatch")
        tables = tuple(
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
            ).fetchall()
        )
        if tables != tuple(sorted(PAUTH_READ_SNAPSHOT_RELATION_NAMES)):
            raise GateError(f"PAUTH read snapshot relation allowlist mismatch: {tables!r}")
        observation, _rows = _observe_pauth_authority(conn, projection=True)
    except (OSError, sqlite3.Error) as exc:
        raise GateError(f"PAUTH read snapshot projection is unreadable: {exc}") from exc
    finally:
        if "conn" in locals():
            conn.close()
    if observation.relations != evidence.relations:
        raise GateError("PAUTH read snapshot projection logical contents differ from its derived ledger")


def _create_pauth_projection(
    destination: Path,
    destination_identity: _PAuthProjectionIdentity,
    rows_by_relation: dict[str, tuple[tuple[object, ...], ...]],
) -> None:
    _verify_pauth_projection_identity(destination, destination_identity)
    try:
        conn = sqlite3.connect(destination.as_uri() + "?mode=rw", uri=True)
        opened_path = Path(str(conn.execute("PRAGMA database_list").fetchone()[2])).resolve(strict=True)
        if opened_path != Path(destination_identity.resolved_path):
            raise GateError("PAUTH read snapshot projection connection was redirected")
        conn.execute("PRAGMA journal_mode=OFF")
        conn.execute("PRAGMA synchronous=OFF")
        conn.execute(f"PRAGMA application_id={PAUTH_READ_SNAPSHOT_APPLICATION_ID}")
        conn.execute(f"PRAGMA user_version={PAUTH_READ_SNAPSHOT_VERSION}")
        for relation, columns in PAUTH_READ_SNAPSHOT_RELATIONS:
            schema_sql = ", ".join(f'"{column}" {declared_type}' for column, declared_type in columns)
            conn.execute(f'CREATE TABLE "{relation}" ({schema_sql})')
            rows = rows_by_relation.get(relation)
            if rows is None:
                raise GateError(f"PAUTH read snapshot source rows are missing for {relation}")
            placeholders = ", ".join("?" for _column in columns)
            conn.executemany(f'INSERT INTO "{relation}" VALUES ({placeholders})', rows)
        conn.commit()
        _verify_pauth_projection_identity(destination, destination_identity)
    except (GateError, OSError, sqlite3.Error) as exc:
        if "conn" in locals() and conn.in_transaction:
            conn.rollback()
        if isinstance(exc, GateError):
            raise
        raise GateError(f"could not construct PAUTH read snapshot projection: {exc}") from exc
    finally:
        if "conn" in locals():
            conn.close()


def _remove_pauth_projection(
    destination: Path,
    destination_identity: _PAuthProjectionIdentity | None = None,
    sidecar_identities: dict[Path, _PathIdentity] | None = None,
) -> None:
    failures: list[str] = []
    expected_sidecars = sidecar_identities or {}
    for suffix in ("", *PAUTH_READ_SNAPSHOT_SIDECAR_SUFFIXES):
        candidate = Path(str(destination) + suffix)
        try:
            if _path_is_linklike(candidate):
                failures.append(f"{candidate.name}: redirected cleanup artifact")
                candidate.unlink()
            elif candidate.exists():
                if suffix == "" and destination_identity is not None:
                    try:
                        current_identity = _pauth_projection_identity(candidate)
                    except GateError as exc:
                        failures.append(f"{candidate.name}: {exc}")
                        candidate.unlink()
                    else:
                        if current_identity != destination_identity:
                            failures.append(f"{candidate.name}: destination identity changed before cleanup")
                            candidate.unlink()
                        else:
                            candidate.unlink()
                elif suffix == "":
                    failures.append(f"{candidate.name}: cleanup artifact lacks an exclusive identity binding")
                    candidate.unlink()
                else:
                    expected = expected_sidecars.get(candidate)
                    if expected is not None:
                        try:
                            current_identity = _path_identity(candidate)
                        except GateError as exc:
                            failures.append(f"{candidate.name}: {exc}")
                            if _path_is_linklike(candidate) or candidate.is_file():
                                candidate.unlink()
                            elif candidate.is_dir():
                                candidate.rmdir()
                        else:
                            if current_identity != expected or not candidate.is_dir():
                                failures.append(f"{candidate.name}: sidecar guard identity changed before cleanup")
                                if candidate.is_dir():
                                    candidate.rmdir()
                                else:
                                    candidate.unlink()
                            else:
                                candidate.rmdir()
                    elif candidate.is_dir():
                        failures.append(f"{candidate.name}: unexpected sidecar directory lacks an identity binding")
                        candidate.rmdir()
                    else:
                        candidate.unlink()
        except OSError as exc:
            failures.append(f"{candidate.name}: {exc}")
        if candidate.exists() or _path_is_linklike(candidate):
            failures.append(f"{candidate.name}: still exists")
    if failures:
        raise GateError("PAUTH read snapshot cleanup failed: " + "; ".join(failures))


@contextmanager
def _pauth_read_snapshot(live_root: Path, snapshot: _BridgeSnapshot) -> Iterator[_BridgeSnapshot]:
    """Add a four-relation invocation-local PAUTH projection to one copied root."""

    try:
        _verify_snapshot_ledger(snapshot)
        resolved_live_root = live_root.resolve(strict=True)
    except GateError:
        raise
    except OSError as exc:
        raise GateError(f"could not verify the base copied-root ledger for PAUTH projection: {exc}") from exc
    source = resolved_live_root / PAUTH_READ_SNAPSHOT_REL
    source_identity = _pauth_source_identity(live_root, source)
    destination = snapshot.root / PAUTH_READ_SNAPSHOT_REL
    existing = snapshot.ledger.get(PAUTH_READ_SNAPSHOT_REL)
    if existing is not None and not existing.content_exempt:
        raise GateError("copied audit root already contains non-exempt groundtruth.db authority")

    source_conn: sqlite3.Connection | None = None
    projection_descriptor: int | None = None
    projection_identity: _PAuthProjectionIdentity | None = None
    sidecar_identities: dict[Path, _PathIdentity] = {}
    cleanup_error: GateError | None = None
    try:
        source_conn = sqlite3.connect(source.as_uri() + "?mode=ro", uri=True, timeout=5)
        source_conn.execute("PRAGMA query_only=ON")
        if int(source_conn.execute("PRAGMA query_only").fetchone()[0]) != 1:
            raise GateError("canonical PAUTH read snapshot source connection is not query-only")
        opened_path = Path(str(source_conn.execute("PRAGMA database_list").fetchone()[2])).resolve(strict=True)
        if opened_path != source:
            raise GateError("PAUTH read snapshot source connection was redirected")
        before, rows_by_relation = _observe_pauth_authority(source_conn, projection=False, include_rows=True)
        sidecar_identities = _create_pauth_projection_sidecar_guards(destination)
        projection_descriptor, projection_identity = _create_exclusive_pauth_projection_placeholder(destination)
        _create_pauth_projection(destination, projection_identity, rows_by_relation)
        if destination.stat().st_size > MAX_BLOB_BYTES:
            raise GateError("compact PAUTH read snapshot exceeds the ordinary copied-blob limit")
        projection_observation, _rows = _observe_projection_path(destination)
        if projection_observation.relations != before.relations:
            raise GateError("PAUTH read snapshot projection differs from canonical source relations")
        _verify_pauth_projection_identity(destination, projection_identity)
        if os.name == "nt":
            destination.chmod(0o644)
        else:
            os.fchmod(projection_descriptor, 0o644)
        _verify_pauth_projection_identity(destination, projection_identity)
        _verify_pauth_projection_sidecar_guards(sidecar_identities)
        info = destination.stat()
        evidence = _PAuthReadSnapshotEvidence(
            construction_version=PAUTH_READ_SNAPSHOT_VERSION,
            source_identity=source_identity,
            relations=before.relations,
        )
        derived_entry = _LedgerEntry(
            mode="100644",
            sha256=hashlib.sha256(destination.read_bytes()).hexdigest(),
            size=info.st_size,
            device=info.st_dev,
            inode=info.st_ino,
            link_count=info.st_nlink,
            pauth_read_snapshot=evidence,
        )
        effective_ledger = {**snapshot.ledger, PAUTH_READ_SNAPSHOT_REL: derived_entry}
        effective_size = sum(entry.size for entry in effective_ledger.values() if not entry.content_exempt)
        if effective_size > MAX_TREE_BYTES:
            raise GateError(f"prospective tree exceeds {MAX_TREE_BYTES}-byte materialization limit")
        effective = _BridgeSnapshot(
            root=snapshot.root,
            ledger=effective_ledger,
            pauth_source_identity=source_identity,
        )
        try:
            configured_path = groundtruth_db_path(effective.root)
        except (OSError, ValueError) as exc:
            raise GateError(f"copied-root PAUTH consumer configuration is unreadable: {exc}") from exc
        if configured_path.resolve(strict=True) != destination.resolve(strict=True):
            raise GateError("copied-root PAUTH consumer configuration resolves outside the derived projection")
        _verify_snapshot_ledger(effective)
        _verify_pauth_source_identity(live_root, source, source_identity)
        after_copy, _rows = _observe_pauth_authority(source_conn, projection=False)
        if after_copy.relations != before.relations:
            raise GateError("canonical PAUTH authority changed while constructing the read snapshot")
        # Construction retained the exclusive no-follow descriptor. Replace that
        # construction handle with the normal read-only no-replace guard before
        # any consumer opens the finished projection; identity is rechecked after
        # the handoff and before consumer execution.
        os.close(projection_descriptor)
        projection_descriptor = None
        guarded_paths = (destination, *sidecar_identities)
        with _hold_paths_no_replace(guarded_paths):
            _verify_pauth_projection_identity(destination, projection_identity)
            _verify_pauth_projection_sidecar_guards(sidecar_identities)
            yield effective
            _verify_snapshot_ledger(effective)
            _verify_pauth_projection_identity(destination, projection_identity)
            _verify_pauth_projection_sidecar_guards(sidecar_identities)
            _verify_pauth_source_identity(live_root, source, source_identity)
            after_evaluation, _rows = _observe_pauth_authority(source_conn, projection=False)
            if after_evaluation.relations != before.relations:
                raise GateError("canonical PAUTH authority changed during protected-commit evaluation")
    except (OSError, sqlite3.Error) as exc:
        raise GateError(f"canonical PAUTH read snapshot source is unreadable: {exc}") from exc
    finally:
        if source_conn is not None:
            try:
                source_conn.close()
            except sqlite3.Error as exc:
                cleanup_error = GateError(f"canonical PAUTH source connection cleanup failed: {exc}")
        if projection_descriptor is not None:
            try:
                os.close(projection_descriptor)
            except OSError as exc:
                cleanup_error = cleanup_error or GateError(f"PAUTH projection descriptor cleanup failed: {exc}")
        try:
            _remove_pauth_projection(destination, projection_identity, sidecar_identities)
        except GateError as exc:
            cleanup_error = exc
        try:
            _verify_snapshot_ledger(snapshot)
        except GateError as exc:
            cleanup_error = cleanup_error or exc
        except OSError as exc:
            cleanup_error = cleanup_error or GateError(
                f"base copied-root ledger re-verification failed after PAUTH cleanup: {exc}"
            )
        if cleanup_error is not None:
            raise cleanup_error


def _observe_projection_path(
    path: Path,
) -> tuple[_PAuthAuthorityObservation, dict[str, tuple[tuple[object, ...], ...]]]:
    try:
        conn = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True, timeout=5)
        conn.execute("PRAGMA query_only=ON")
        if int(conn.execute("PRAGMA query_only").fetchone()[0]) != 1:
            raise GateError("PAUTH read snapshot projection connection is not query-only")
        return _observe_pauth_authority(conn, projection=True)
    except (OSError, sqlite3.Error) as exc:
        raise GateError(f"PAUTH read snapshot projection is unreadable: {exc}") from exc
    finally:
        if "conn" in locals():
            conn.close()


def _requires_pauth_read_snapshot(status: str, *contents: str | None) -> bool:
    return status in PAUTH_READ_SNAPSHOT_STATUSES and any(
        extract_metadata_value(content, PROJECT_AUTHORIZATION_KEYS) is not None
        for content in contents
        if content is not None
    )


@contextmanager
def _hold_paths_no_replace(paths: tuple[Path, ...]) -> Iterator[None]:
    handles: list[Any] = []
    try:
        if os.name == "nt":
            import ctypes
            from ctypes import wintypes

            create_file = ctypes.WinDLL("kernel32", use_last_error=True).CreateFileW
            create_file.argtypes = (
                wintypes.LPCWSTR,
                wintypes.DWORD,
                wintypes.DWORD,
                wintypes.LPVOID,
                wintypes.DWORD,
                wintypes.DWORD,
                wintypes.HANDLE,
            )
            create_file.restype = wintypes.HANDLE
            invalid_handle = wintypes.HANDLE(-1).value
            for path in paths:
                desired_access = 0x0080 | (0x80000000 if path.is_file() else 0)
                flags = 0x02000000 if path.is_dir() else 0x00000080
                handle = create_file(
                    str(path),
                    desired_access,
                    0x00000001,
                    None,
                    3,
                    flags,
                    None,
                )
                if handle == invalid_handle:
                    error = ctypes.get_last_error()
                    raise GateError(f"could not lock guarded authority path {path}: Windows error {error}")
                handles.append(handle)
            yield
        else:
            for path in paths:
                flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
                if path.is_dir():
                    flags |= getattr(os, "O_DIRECTORY", 0)
                handles.append(os.open(path, flags))
            yield
    finally:
        if os.name == "nt":
            if handles:
                import ctypes

                close_handle = ctypes.WinDLL("kernel32", use_last_error=True).CloseHandle
                close_handle.argtypes = (ctypes.c_void_p,)
                close_handle.restype = ctypes.c_int
                for handle in reversed(handles):
                    close_handle(handle)
        else:
            for handle in reversed(handles):
                os.close(handle)


def _verify_index_snapshot(snapshot: _IndexSnapshot) -> None:
    _verify_path_identity(snapshot.index_file.parent, snapshot.index_root_identity)
    _verify_path_identity(snapshot.index_file, snapshot.index_file_identity)


@contextmanager
def _immutable_index_snapshot(snapshot: _IndexSnapshot) -> Iterator[None]:
    snapshot.index_file.chmod(0o444)
    snapshot.index_file.parent.chmod(0o555)
    guarded = (snapshot.index_file.parent, snapshot.index_file)
    try:
        _verify_index_snapshot(snapshot)
        with _hold_paths_no_replace(guarded):
            _verify_index_snapshot(snapshot)
            try:
                yield
            finally:
                _verify_index_snapshot(snapshot)
    finally:
        snapshot.index_file.parent.chmod(0o755)
        snapshot.index_file.chmod(0o644)


def _run_index_git(
    root: Path,
    snapshot: _IndexSnapshot,
    *args: str,
    text: bool = False,
) -> subprocess.CompletedProcess[Any]:
    _verify_index_snapshot(snapshot)
    result = _run_git(root, *args, env=snapshot.env, text=text)
    _verify_index_snapshot(snapshot)
    return result


def _scratch_root(root: Path) -> Path:
    root_resolved = root.resolve()
    if _path_is_linklike(root):
        raise GateError(f"project root is a symlink, junction, or reparse point: {root}")
    scratch = root / ".gtkb-state"
    if scratch.exists() and _path_is_linklike(scratch):
        raise GateError(f"scratch root is a symlink, junction, or reparse point: {scratch}")
    scratch.mkdir(parents=True, exist_ok=True)
    scratch_resolved = scratch.resolve()
    try:
        scratch_resolved.relative_to(root_resolved)
    except ValueError as exc:
        raise GateError(f"scratch root resolves outside the project root: {scratch_resolved}") from exc
    for ancestor in (scratch, *scratch.parents):
        if ancestor == root.parent:
            break
        if _path_is_linklike(ancestor):
            raise GateError(f"scratch ancestor is a symlink, junction, or reparse point: {ancestor}")
        if ancestor == root:
            break
    return scratch


def _index_entries(root: Path, snapshot: _IndexSnapshot) -> tuple[_IndexEntry, ...]:
    result = _run_index_git(root, snapshot, "ls-files", "--stage", "-z")
    if result.returncode != 0:
        raise GateError(f"could not enumerate copied index entries: {result.stderr!r}")
    return _parse_index_inventory(result.stdout)


def _parse_tree_inventory(raw: bytes) -> tuple[_IndexEntry, ...]:
    records = raw.split(b"\0")
    if records and records[-1] == b"":
        records.pop()
    index_records: list[bytes] = []
    for record in records:
        try:
            metadata, raw_path = record.split(b"\t", 1)
            mode, object_type, oid = metadata.split(b" ", 2)
        except ValueError as exc:
            raise GateError("malformed committed tree inventory record") from exc
        if object_type != b"blob":
            raise GateError(f"unsupported committed tree object type {object_type!r}")
        index_records.append(mode + b" " + oid + b" 0\t" + raw_path)
    return _parse_index_inventory(b"\0".join(index_records) + (b"\0" if index_records else b""))


def _blob_ledger_entry(
    root: Path,
    destination: Path,
    entry: _IndexEntry,
    *,
    env: dict[str, str],
    object_format: str,
) -> _LedgerEntry:
    expected_oid_length = GIT_OBJECT_FORMATS[object_format]
    if len(entry.oid) != expected_oid_length:
        raise GateError(f"index object id length does not match repository {object_format} format for {entry.rel_path}")
    size_result = _run_git(root, "cat-file", "-s", entry.oid, env=env, text=True)
    try:
        expected_size = int(size_result.stdout.strip())
    except ValueError as exc:
        raise GateError(f"could not read raw blob size for {entry.rel_path}") from exc
    if size_result.returncode != 0 or expected_size < 0:
        raise GateError(f"could not read raw blob size for {entry.rel_path}: {size_result.stderr!r}")
    if expected_size > MAX_BLOB_BYTES:
        raise GateError(f"raw blob exceeds {MAX_BLOB_BYTES}-byte materialization limit: {entry.rel_path}")

    object_hasher = hashlib.new(object_format)
    object_hasher.update(f"blob {expected_size}\0".encode("ascii"))
    content_hasher = hashlib.sha256()
    actual_size = 0
    process = subprocess.Popen(
        _git_command("cat-file", "blob", entry.oid),
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )
    try:
        with destination.open("xb") as output:
            assert process.stdout is not None
            while chunk := process.stdout.read(1024 * 1024):
                actual_size += len(chunk)
                if actual_size > expected_size or actual_size > MAX_BLOB_BYTES:
                    process.kill()
                    raise GateError(f"raw blob exceeded declared or configured size for {entry.rel_path}")
                object_hasher.update(chunk)
                content_hasher.update(chunk)
                output.write(chunk)
        stderr = process.communicate(timeout=30)[1]
    except BaseException:
        if process.poll() is None:
            process.kill()
            process.communicate()
        raise
    if process.returncode != 0:
        raise GateError(f"could not read raw index blob {entry.oid} for {entry.rel_path}: {stderr!r}")
    if actual_size != expected_size:
        raise GateError(f"raw blob size mismatch for {entry.rel_path}: expected {expected_size}, got {actual_size}")
    if object_hasher.hexdigest().lower() != entry.oid.lower():
        raise GateError(f"raw blob bytes do not hash to indexed object id for {entry.rel_path}")
    if os.name != "nt":
        destination.chmod(0o755 if entry.mode == "100755" else 0o644)
    info = destination.stat()
    return _LedgerEntry(
        mode=entry.mode,
        sha256=content_hasher.hexdigest(),
        size=actual_size,
        device=info.st_dev,
        inode=info.st_ino,
        link_count=info.st_nlink,
    )


def _materialize_entries(
    root: Path,
    snapshot_root: Path,
    entries: tuple[_IndexEntry, ...],
    *,
    env: dict[str, str],
    object_format: str,
) -> dict[str, _LedgerEntry]:
    # WI-5659: stream every blob through ONE `git cat-file --batch` process
    # instead of two subprocess spawns per entry (`cat-file -s` + `cat-file
    # blob`). Measured on this 19,090-entry index: 159.4 ms/entry (50.7 min)
    # -> ~1 ms/entry, with 86% of the old cost being process spawn alone. This
    # changes only HOW blobs are fetched, never WHAT is materialized: the tree
    # stays index-complete, and per-blob declared-size checks, per-blob
    # object-hash verification, MAX_BLOB_BYTES / MAX_TREE_BYTES limits,
    # destination path/link-safety checks, exclusive-create writes, and ledger
    # contents are all preserved. `_blob_ledger_entry` is retained as the
    # reference single-entry implementation the ledger-equivalence test
    # compares against.
    #
    # Requests are interleaved one-at-a-time rather than written up front: git
    # would otherwise block writing a full stdout pipe while this process is
    # still writing stdin, deadlocking on a large index.
    ledger: dict[str, _LedgerEntry] = {}
    if not entries:
        return ledger

    expected_oid_length = GIT_OBJECT_FORMATS[object_format]
    for entry in entries:
        if len(entry.oid) != expected_oid_length:
            raise GateError(
                f"index object id length does not match repository {object_format} format for {entry.rel_path}"
            )

    total_size = 0
    snapshot_root_resolved = snapshot_root.resolve()
    process = subprocess.Popen(
        _git_command("cat-file", "--batch"),
        cwd=root,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )
    try:
        assert process.stdin is not None
        assert process.stdout is not None
        for entry in entries:
            destination = snapshot_root / entry.rel_path
            destination.parent.mkdir(parents=True, exist_ok=True)
            if _path_is_linklike(destination.parent):
                raise GateError(f"snapshot destination parent is link-like: {destination.parent}")
            resolved_parent = destination.parent.resolve()
            try:
                resolved_parent.relative_to(snapshot_root_resolved)
            except ValueError as exc:
                raise GateError(f"snapshot destination escapes materialization root: {entry.rel_path}") from exc

            process.stdin.write(f"{entry.oid}\n".encode("ascii"))
            process.stdin.flush()

            header = process.stdout.readline()
            if not header:
                raise GateError(f"could not read raw index blob {entry.oid} for {entry.rel_path}: batch stream closed")
            fields = header.decode("utf-8", "replace").strip().split(" ")
            if len(fields) != 3:
                # `<oid> missing` / `<oid> ambiguous` and any malformed header.
                raise GateError(f"could not read raw index blob {entry.oid} for {entry.rel_path}: {header!r}")
            batch_oid, object_type, raw_size = fields
            if object_type != "blob":
                raise GateError(f"unsupported committed tree object type {object_type!r}")
            if batch_oid.lower() != entry.oid.lower():
                raise GateError(f"batch stream returned object id {batch_oid!r} for {entry.rel_path}")
            try:
                expected_size = int(raw_size)
            except ValueError as exc:
                raise GateError(f"could not read raw blob size for {entry.rel_path}") from exc
            if expected_size < 0:
                raise GateError(f"could not read raw blob size for {entry.rel_path}")
            if expected_size > MAX_BLOB_BYTES:
                # WI-5659 mechanism 3 (in-ledger; DELIB-202667186 / DELIB-202667188):
                # exempt oversized blobs from CONTENT COPY only. The bytes are still
                # streamed from the batch and hash-verified against the index object
                # id (a substituted blob still fails closed), but are NOT written to
                # the tree and do NOT consume MAX_TREE_BYTES. The entry is recorded IN
                # the ledger with content_exempt=True and its mode/oid/declared size.
                # Required because tracked groundtruth.db (762720256 bytes) otherwise
                # makes every governed VERIFIED finalization fail closed. Size-triggered
                # only, never path- or content-targeted.
                exempt_object_hasher = hashlib.new(object_format)
                exempt_object_hasher.update(f"blob {expected_size}\0".encode("ascii"))
                exempt_content_hasher = hashlib.sha256()
                remaining = expected_size
                while remaining > 0:
                    chunk = process.stdout.read(min(remaining, 1024 * 1024))
                    if not chunk:
                        raise GateError(
                            f"raw blob size mismatch for {entry.rel_path}: "
                            f"expected {expected_size}, got {expected_size - remaining}"
                        )
                    remaining -= len(chunk)
                    exempt_object_hasher.update(chunk)
                    exempt_content_hasher.update(chunk)
                if process.stdout.read(1) != b"\n":
                    raise GateError(f"malformed batch record terminator for {entry.rel_path}")
                if exempt_object_hasher.hexdigest().lower() != entry.oid.lower():
                    raise GateError(f"raw blob bytes do not hash to indexed object id for {entry.rel_path}")
                ledger[entry.rel_path] = _LedgerEntry(
                    mode=entry.mode,
                    sha256=exempt_content_hasher.hexdigest(),
                    size=expected_size,
                    device=0,
                    inode=0,
                    link_count=0,
                    content_exempt=True,
                    oid=entry.oid,
                )
                continue

            object_hasher = hashlib.new(object_format)
            object_hasher.update(f"blob {expected_size}\0".encode("ascii"))
            content_hasher = hashlib.sha256()
            actual_size = 0
            with destination.open("xb") as output:
                remaining = expected_size
                while remaining > 0:
                    chunk = process.stdout.read(min(remaining, 1024 * 1024))
                    if not chunk:
                        raise GateError(
                            f"raw blob size mismatch for {entry.rel_path}: expected {expected_size}, got {actual_size}"
                        )
                    remaining -= len(chunk)
                    actual_size += len(chunk)
                    object_hasher.update(chunk)
                    content_hasher.update(chunk)
                    output.write(chunk)
            if process.stdout.read(1) != b"\n":
                raise GateError(f"malformed batch record terminator for {entry.rel_path}")
            if actual_size != expected_size:
                raise GateError(
                    f"raw blob size mismatch for {entry.rel_path}: expected {expected_size}, got {actual_size}"
                )
            if object_hasher.hexdigest().lower() != entry.oid.lower():
                raise GateError(f"raw blob bytes do not hash to indexed object id for {entry.rel_path}")
            if os.name != "nt":
                destination.chmod(0o755 if entry.mode == "100755" else 0o644)
            info = destination.stat()

            total_size += actual_size
            if total_size > MAX_TREE_BYTES:
                raise GateError(f"prospective tree exceeds {MAX_TREE_BYTES}-byte materialization limit")
            ledger[entry.rel_path] = _LedgerEntry(
                mode=entry.mode,
                sha256=content_hasher.hexdigest(),
                size=actual_size,
                device=info.st_dev,
                inode=info.st_ino,
                link_count=info.st_nlink,
            )
    finally:
        try:
            if process.stdin is not None and not process.stdin.closed:
                process.stdin.close()
        except OSError:
            pass
        if process.poll() is None:
            process.kill()
        process.communicate()
    return ledger


def _materialize_index_tree(
    root: Path,
    snapshot_root: Path,
    snapshot: _IndexSnapshot,
) -> dict[str, _LedgerEntry]:
    _verify_index_snapshot(snapshot)
    try:
        return _materialize_entries(
            root,
            snapshot_root,
            _index_entries(root, snapshot),
            env=snapshot.env,
            object_format=snapshot.object_format,
        )
    finally:
        _verify_index_snapshot(snapshot)


@contextmanager
def _index_snapshot(root: Path, head_oid: str | None = None) -> Iterator[_IndexSnapshot]:
    pinned_head = head_oid or _resolve_head_oid(root)
    if pinned_head is None:
        raise GateError("could not resolve HEAD^{commit} for staged authorization evaluation")
    object_format = _resolve_object_format(root)
    source_text = os.environ.get("GIT_INDEX_FILE")
    if source_text:
        source_index = Path(source_text)
        if not source_index.is_absolute():
            source_index = root / source_index
    else:
        resolved = _run_git(root, "rev-parse", "--git-path", "index", text=True)
        if resolved.returncode != 0:
            raise GateError(f"could not resolve Git index path: {resolved.stderr.strip()}")
        source_index = Path(resolved.stdout.strip())
        if not source_index.is_absolute():
            source_index = root / source_index
    try:
        index_bytes = source_index.read_bytes()
    except OSError as exc:
        raise GateError(f"could not snapshot Git index {source_index}: {exc}") from exc

    with tempfile.TemporaryDirectory(prefix=".gtkb-index-", dir=_scratch_root(root)) as tmp:
        snapshot_index = Path(tmp) / "index"
        snapshot_index.write_bytes(index_bytes)
        snapshot_index.chmod(0o444)
        snapshot_index.parent.chmod(0o555)
        env = _sanitized_subprocess_env(index_file=snapshot_index)
        snapshot = _IndexSnapshot(
            env=env,
            head_oid=pinned_head,
            object_format=object_format,
            selected_paths=(),
            status_by_path={},
            index_file=snapshot_index,
            index_file_identity=_path_identity(snapshot_index, hash_bytes=True),
            index_root_identity=_path_identity(snapshot_index.parent),
        )
        with _immutable_index_snapshot(snapshot):
            result = _run_index_git(
                root,
                snapshot,
                "diff",
                "--cached",
                "--name-status",
                "-z",
                "--find-renames",
                pinned_head,
            )
            if result.returncode != 0:
                raise GateError(f"could not enumerate staged paths from index snapshot: {result.stderr!r}")
            selected_paths, status_by_path = _parse_staged_name_status(result.stdout)
            snapshot = replace(
                snapshot,
                selected_paths=selected_paths,
                status_by_path=status_by_path,
            )
            _index_entries(root, snapshot)
            yield snapshot


def _staged_text(root: Path, rel_path: str, snapshot: _IndexSnapshot) -> str:
    result = _run_index_git(root, snapshot, "show", f":{rel_path}", text=True)
    if result.returncode != 0:
        raise GateError(f"could not read copied index path {rel_path}: {result.stderr.strip()}")
    return result.stdout


def _staged_or_worktree_text(root: Path, rel_path: str) -> str:
    staged = _run_git(root, "show", f":{rel_path}", text=True)
    if staged.returncode == 0:
        return staged.stdout
    try:
        return (root / rel_path).read_text(encoding="utf-8")
    except OSError as exc:
        raise GateError(f"could not read {rel_path}: {exc}") from exc


def _disk_bridge_entries(root: Path, bridge_id: str) -> tuple[_IndexEntry, ...]:
    """WI-6726 Surface B: the commit-gate counterpart of the b39db7a31 repair.

    WI-6530 reclassified ``bridge/`` as ephemeral runtime state and git-ignored it,
    but this gate still sourced bridge lifecycle evidence from the committed tree,
    so the tree yields no entries, the snapshot has no ``bridge`` directory, and
    every terminal VERIFIED thread is unreadable -- the commit-side half of the
    deadlock ``b39db7a31`` fixed on the verdict-writing side. An IGNORED bridge file
    present on disk satisfies chain integrity for the reason accepted there:
    tracked-ness is not a meaningful signal for a path class governance declared
    ephemeral.

    Fails closed. A matching bridge file that is NOT ignored is a real gap, and any
    such file collapses the fallback to an empty tuple so the caller keeps its
    existing missing-evidence error. Content is hashed into the object store so the
    unchanged ``_materialize_entries`` path, the ledger, and every snapshot
    immutability guard continue to apply verbatim.
    """
    bridge_dir = root / "bridge"
    if not bridge_dir.is_dir():
        return ()
    exact_re = re.compile(rf"^{re.escape(bridge_id)}-\d{{3}}\.md$")
    entries: list[_IndexEntry] = []
    for path in sorted(bridge_dir.iterdir()):
        if not path.is_file() or not exact_re.fullmatch(path.name):
            continue
        rel_path = f"bridge/{path.name}"
        ignored = _run_git(root, "check-ignore", "-q", "--", rel_path)
        if ignored.returncode != 0:
            return ()
        hashed = _run_git(root, "hash-object", "-w", "--", rel_path, text=True)
        if hashed.returncode != 0:
            return ()
        oid = (hashed.stdout or "").strip()
        if not oid:
            return ()
        entries.append(_IndexEntry(mode="100644", oid=oid, rel_path=rel_path))
    return tuple(entries)


@contextmanager
def _bridge_snapshot(
    root: Path,
    bridge_id: str,
    index_snapshot: _IndexSnapshot | None = None,
    head_oid: str | None = None,
    precomputed_head_entries: tuple[_IndexEntry, ...] | None = None,
) -> Iterator[_BridgeSnapshot]:
    pinned_head = index_snapshot.head_oid if index_snapshot is not None else head_oid
    if pinned_head is None:
        raise GateError("could not resolve pinned HEAD commit for bridge lifecycle evidence")
    scratch_root = _scratch_root(root)
    with tempfile.TemporaryDirectory(prefix=".gtkb-lifecycle-", dir=scratch_root) as tmp:
        snapshot_root = Path(tmp)
        if index_snapshot is not None:
            ledger = _materialize_index_tree(root, snapshot_root, index_snapshot)
            yield _BridgeSnapshot(root=snapshot_root, ledger=ledger)
            return

    if precomputed_head_entries is not None:
        # WI-5658: reuse the once-enumerated committed bridge inventory instead of
        # re-running ls-tree + re-parsing the full ~13k-file tree for every caller.
        head_entries = precomputed_head_entries
    else:
        head_listing = _run_git(root, "ls-tree", "-r", "-z", pinned_head, "--", "bridge")
        if head_listing.returncode != 0:
            raise GateError(f"could not enumerate committed bridge history: {head_listing.stderr!r}")

        exact_re = re.compile(rf"^bridge/{re.escape(bridge_id)}-\d{{3}}\.md$")
        head_entries = tuple(
            entry for entry in _parse_tree_inventory(head_listing.stdout) if exact_re.fullmatch(entry.rel_path)
        )
    if not head_entries:
        # WI-6726 Surface B: fall back to ignored-but-present on-disk chain evidence.
        head_entries = _disk_bridge_entries(root, bridge_id)
    with tempfile.TemporaryDirectory(prefix=".gtkb-lifecycle-", dir=scratch_root) as tmp:
        snapshot_root = Path(tmp)
        ledger = _materialize_entries(
            root,
            snapshot_root,
            head_entries,
            env=_sanitized_subprocess_env(),
            object_format=_resolve_object_format(root),
        )
        yield _BridgeSnapshot(root=snapshot_root, ledger=ledger)


# Upper bound on ledger-verification concurrency. Sized above typical core
# counts because the work is I/O-bound, and capped so a large host does not
# spawn an unbounded pool (WI-5998).
_LEDGER_VERIFY_WORKER_CAP = 32


def _ledger_verify_worker_count(entry_count: int, max_workers: int | None = None) -> int:
    """Worker count for ledger verification: CPU-derived, capped, never below 1.

    Verification is I/O-bound (stat plus full-file read per entry), so the pool
    is sized above core count to hide disk latency, then capped so a large
    machine does not spawn an unbounded pool. ``max_workers`` is honoured
    verbatim when supplied so tests can pin a count, including 1 to reproduce
    serial ordering (WI-5998).
    """
    if max_workers is not None:
        return max(1, max_workers)
    if entry_count <= 1:
        return 1
    derived = (os.cpu_count() or 1) * 2
    return max(1, min(_LEDGER_VERIFY_WORKER_CAP, derived, entry_count))


def _verify_ledger_entry(snapshot: _BridgeSnapshot, rel_path: str, expected: Any) -> None:
    """Verify one ledger entry. Body preserved verbatim from the serial loop.

    Raises ``GateError`` on any mismatch; returns None on success. Every check
    and its order is unchanged from the pre-WI-5998 serial implementation --
    only the dispatch around it changed.
    """
    if expected.content_exempt:
        if expected.pauth_read_snapshot is not None:
            raise GateError(f"content-exempt ledger entry cannot carry PAUTH authority: {rel_path}")
        if not expected.oid or expected.size < 0 or not expected.mode:
            raise GateError(f"content-exempt ledger entry has incomplete metadata: {rel_path}")
        return
    candidate = snapshot.root / rel_path
    if not candidate.is_file() or _path_is_linklike(candidate):
        raise GateError(f"prospective audit authority path is no longer a regular file: {rel_path}")
    info = candidate.stat()
    if (
        info.st_size != expected.size
        or info.st_dev != expected.device
        or info.st_ino != expected.inode
        or info.st_nlink != expected.link_count
    ):
        raise GateError(f"prospective audit authority file identity drifted during audit: {rel_path}")
    actual_hash = hashlib.sha256(candidate.read_bytes()).hexdigest()
    if actual_hash != expected.sha256:
        raise GateError(f"prospective audit authority bytes drifted during audit: {rel_path}")
    if os.name != "nt":
        actual_executable = bool(info.st_mode & stat.S_IXUSR)
        if actual_executable != (expected.mode == "100755"):
            raise GateError(f"prospective audit authority mode drifted during audit: {rel_path}")
    if expected.pauth_read_snapshot is not None:
        if rel_path != PAUTH_READ_SNAPSHOT_REL:
            raise GateError(f"PAUTH read snapshot ledger entry uses an unexpected path: {rel_path}")
        if expected.pauth_read_snapshot.source_identity != snapshot.pauth_source_identity:
            raise GateError("PAUTH read snapshot ledger source identity changed from canonical source binding")
        _verify_pauth_projection(candidate, expected.pauth_read_snapshot)


def _verify_ledger_entries(snapshot: _BridgeSnapshot, *, max_workers: int | None = None) -> None:
    """Verify every ledger entry, dispatching in parallel and failing closed.

    Fail-closed contract (WI-5998): every future is drained, so no worker
    exception can be swallowed. When several entries drift at once, the failure
    re-raised is the one earliest in ledger order -- not the first to complete --
    so the reported entry and message are identical across repeated runs and
    across worker counts.
    """
    entries = list(snapshot.ledger.items())
    if not entries:
        return
    workers = _ledger_verify_worker_count(len(entries), max_workers)
    if workers == 1:
        for rel_path, expected in entries:
            _verify_ledger_entry(snapshot, rel_path, expected)
        return
    failures: dict[int, GateError] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {
            pool.submit(_verify_ledger_entry, snapshot, rel_path, expected): index
            for index, (rel_path, expected) in enumerate(entries)
        }
        for future in concurrent.futures.as_completed(futures):
            index = futures[future]
            try:
                future.result()
            except GateError as exc:
                failures[index] = exc
    if failures:
        raise failures[min(failures)]


def _verify_snapshot_ledger(snapshot: _BridgeSnapshot, *, max_workers: int | None = None) -> None:
    # WI-5659 mechanism 4 (DELIB-202667187): skip ONLY the owner-authorized audit
    # scratch boundary `.gtkb-state/compliance-audit/` (both _isolated_compliance_audit
    # and the audit-candidate quarantine live under it), NOT every non-ledger path.
    # Tracked `.gtkb-state/*` files are in the ledger and verified normally; any
    # UNEXPECTED untracked file elsewhere under `.gtkb-state/` is caught as file-set
    # drift, preserving the narrow exclusion the owner selected (LO verdict -021 P1).
    # Mechanism 3 (in-ledger; DELIB-202667186 / DELIB-202667188): content-exempt
    # entries are recorded in the ledger but must be ABSENT from disk.
    exempt_paths = {rel for rel, entry in snapshot.ledger.items() if entry.content_exempt}
    non_exempt_paths = {rel for rel, entry in snapshot.ledger.items() if not entry.content_exempt}
    pauth_evidence_paths = {rel for rel, entry in snapshot.ledger.items() if entry.pauth_read_snapshot is not None}
    if snapshot.pauth_source_identity is None and pauth_evidence_paths:
        raise GateError("PAUTH read snapshot ledger is missing its canonical source identity binding")
    if snapshot.pauth_source_identity is not None and pauth_evidence_paths != {PAUTH_READ_SNAPSHOT_REL}:
        raise GateError("PAUTH read snapshot source identity binding lacks canonical ledger evidence")
    actual_paths: set[str] = set()
    for candidate in snapshot.root.rglob("*"):
        rel_path = candidate.relative_to(snapshot.root).as_posix()
        if rel_path == ".gtkb-state" or rel_path.startswith(".gtkb-state/compliance-audit/"):
            continue
        if _path_is_linklike(candidate):
            raise GateError(f"prospective audit tree contains a link-like path after audit: {rel_path}")
        if candidate.is_file():
            actual_paths.add(rel_path)
    if actual_paths != non_exempt_paths:
        raise GateError(
            "prospective audit tree file set drifted during audit"
            f"; missing={sorted(non_exempt_paths - actual_paths)}"
            f"; extra={sorted(actual_paths - non_exempt_paths)}"
        )
    exempt_on_disk = sorted(rel for rel in exempt_paths if (snapshot.root / rel).exists())
    if exempt_on_disk:
        raise GateError(f"content-exempt ledger paths must not exist on disk: {exempt_on_disk}")
    _verify_ledger_entries(snapshot, max_workers=max_workers)


def _set_snapshot_read_only(snapshot: _BridgeSnapshot, read_only: bool) -> None:
    paths = sorted(
        (
            candidate
            for candidate in (snapshot.root, *snapshot.root.rglob("*"))
            if ".gtkb-state" not in candidate.relative_to(snapshot.root).parts
        ),
        key=lambda candidate: len(candidate.parts),
        reverse=read_only,
    )
    for candidate in paths:
        if _path_is_linklike(candidate):
            raise GateError(f"prospective audit tree contains a link-like path: {candidate}")
        if candidate.is_file():
            rel_path = candidate.relative_to(snapshot.root).as_posix()
            expected = snapshot.ledger.get(rel_path)
            if expected is None:
                raise GateError(f"prospective audit tree contains an untracked file: {rel_path}")
            mode = 0o444 if read_only else (0o755 if expected.mode == "100755" else 0o644)
            candidate.chmod(mode)
        elif candidate.is_dir():
            candidate.chmod(0o555 if read_only else 0o755)


def _snapshot_guard_paths(snapshot: _BridgeSnapshot) -> tuple[Path, ...]:
    descendants = tuple(
        candidate
        for candidate in snapshot.root.rglob("*")
        if ".gtkb-state" not in candidate.relative_to(snapshot.root).parts
    )
    return (snapshot.root.parent, snapshot.root, *sorted(descendants))


def _snapshot_guard_identities(snapshot: _BridgeSnapshot) -> dict[Path, _PathIdentity]:
    return {path: _path_identity(path, hash_bytes=path.is_file()) for path in _snapshot_guard_paths(snapshot)}


def _verify_snapshot_guard_identities(identities: dict[Path, _PathIdentity]) -> None:
    for path, expected in identities.items():
        _verify_path_identity(path, expected)


@contextmanager
def _immutable_snapshot(snapshot: _BridgeSnapshot) -> Iterator[None]:
    _verify_snapshot_ledger(snapshot)
    _set_snapshot_read_only(snapshot, True)
    identities = _snapshot_guard_identities(snapshot)
    try:
        with _hold_paths_no_replace(tuple(identities)):
            _verify_snapshot_guard_identities(identities)
            try:
                yield
            finally:
                _verify_snapshot_ledger(snapshot)
                _verify_snapshot_guard_identities(identities)
    finally:
        _set_snapshot_read_only(snapshot, False)
        _verify_snapshot_ledger(snapshot)


def _isolated_compliance_audit(
    *,
    snapshot_root: Path,
    candidate: Path,
    content: str,
) -> dict[str, object]:
    gate_path = snapshot_root / ".claude" / "hooks" / "bridge-compliance-gate.py"
    if not gate_path.is_file() or _path_is_linklike(gate_path):
        raise BridgeComplianceError(f"bridge-compliance gate is unavailable in prospective tree: {gate_path}")
    try:
        candidate_rel = candidate.relative_to(snapshot_root).as_posix()
    except ValueError as exc:
        raise BridgeComplianceError("bridge-compliance candidate escapes prospective tree") from exc
    payload = {
        "cwd": str(snapshot_root.resolve()),
        "tool_input": {"file_path": candidate_rel, "content": content},
    }
    audit_dir = snapshot_root / ".gtkb-state" / "compliance-audit"
    audit_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="audit-", dir=audit_dir) as tmp:
        audit_output = Path(tmp) / "audit.json"
        audit_env = _sanitized_subprocess_env(isolate_python=True)
        audit_env["HOME"] = str(snapshot_root)
        audit_env["USERPROFILE"] = str(snapshot_root)
        result = subprocess.run(
            [
                str(Path(sys.executable).resolve()),
                "-I",
                "-B",
                "-S",
                str(gate_path),
                "--audit-only",
                "--audit-output",
                str(audit_output),
            ],
            cwd=snapshot_root,
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            check=False,
            env=audit_env,
        )
        if result.returncode != 0:
            raise BridgeComplianceError(
                "bridge-compliance audit failed to execute: "
                f"returncode={result.returncode} stdout={result.stdout!r} stderr={result.stderr!r}"
            )
        try:
            audit = json.loads(audit_output.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise BridgeComplianceError("bridge-compliance audit did not produce readable JSON") from exc
    if not isinstance(audit, dict):
        raise BridgeComplianceError("bridge-compliance audit JSON root must be an object")
    if audit.get("decision") != "pass":
        reason = audit.get("reason") or "bridge-compliance audit denied the candidate bridge file"
        raise BridgeComplianceError(str(reason))
    return audit


def run_bridge_compliance_audit(
    *,
    file_path: Path,
    content: str,
    project_root: Path,
) -> dict[str, object]:
    """Run the project gate directly under the checker's isolated subprocess contract."""
    return _isolated_compliance_audit(
        snapshot_root=project_root,
        candidate=file_path,
        content=content,
    )


def _run_snapshot_compliance_audit(
    *,
    snapshot: _BridgeSnapshot,
    candidate_path: str,
    content: str,
) -> dict[str, object]:
    snapshot_root = snapshot.root
    candidate = snapshot_root / candidate_path
    _verify_snapshot_ledger(snapshot)
    quarantine_dir = snapshot_root / ".gtkb-state" / "compliance-audit" / "audit-candidate"
    quarantine_dir.mkdir(parents=True, exist_ok=True)
    hidden_candidate = quarantine_dir / candidate.name
    try:
        candidate.replace(hidden_candidate)
    except OSError as exc:
        raise GateError(f"could not isolate compliance candidate {candidate_path}: {exc}") from exc
    _verify_snapshot_ledger(
        replace(
            snapshot,
            ledger={path: entry for path, entry in snapshot.ledger.items() if path != candidate_path},
        )
    )
    _set_snapshot_read_only(
        replace(
            snapshot,
            ledger={path: entry for path, entry in snapshot.ledger.items() if path != candidate_path},
        ),
        True,
    )
    try:
        audit = run_bridge_compliance_audit(
            file_path=candidate,
            content=content,
            project_root=snapshot_root,
        )
    finally:
        _set_snapshot_read_only(
            replace(
                snapshot,
                ledger={path: entry for path, entry in snapshot.ledger.items() if path != candidate_path},
            ),
            False,
        )
        hidden_candidate.replace(candidate)
    _verify_snapshot_ledger(snapshot)
    return audit


def _first_nonblank_line(text: str) -> str:
    return next((line.strip() for line in text.splitlines() if line.strip()), "")


def _section_body(text: str, heading: str) -> str:
    pattern = re.compile(rf"^##\s+{re.escape(heading)}\s*$", re.IGNORECASE | re.MULTILINE)
    match = pattern.search(text)
    if match is None:
        return ""
    start = match.end()
    next_heading = re.search(r"^##\s+", text[start:], re.MULTILINE)
    end = start + next_heading.start() if next_heading else len(text)
    return text[start:end].strip()


def _has_commit_finalization_evidence(text: str) -> bool:
    section = _section_body(text, "Commit Finalization Evidence")
    if not section:
        return False
    return "Same-transaction path set" in section and bool(re.search(r"(?m)^\s*-\s+`[^`]+`\s*$", section))


def _superseded_versioned_bridge(
    rel_path: str,
    snapshot: _IndexSnapshot | None,
) -> bool:
    """Return True when ``rel_path`` is a superseded predecessor within its numbered
    bridge chain in THIS commit transaction: a higher-numbered version of the same
    slug is staged in the current transaction (``snapshot.selected_paths``).

    Supersession is scoped to the staged transaction, never the ambient worktree,
    so an untracked or parked higher-numbered draft cannot false-positively mark a
    genuine latest terminal VERIFIED as superseded (which would both break a
    legitimate commit and suppress the terminal-VERIFIED finalization-evidence
    finding). A superseded predecessor is non-authoritative history: excluded from
    the VERIFIED-candidate count and from the finalization-evidence finding.
    Excluding it grants no authority: with zero live VERIFIED candidates a protected
    commit is simply not authorized (fail-closed), so only the single latest
    VERIFIED candidate ever carries authorization, and that candidate still receives
    full validation (including the resolver latest-strict-state check).
    """
    if snapshot is None:
        return False
    match = VERSIONED_BRIDGE_CAPTURE_RE.fullmatch(rel_path)
    if match is None:
        return False
    slug = match.group("bridge_id")
    version = int(match.group("version"))

    def _is_higher_sibling(candidate: str) -> bool:
        sibling = VERSIONED_BRIDGE_CAPTURE_RE.fullmatch(candidate)
        return sibling is not None and sibling.group("bridge_id") == slug and int(sibling.group("version")) > version

    return any(_is_higher_sibling(p) for p in snapshot.selected_paths)


def _verified_bridge_finalization_finding(
    root: Path,
    rel_path: str,
    snapshot: _IndexSnapshot | None,
) -> dict[str, Any] | None:
    if not VERSIONED_BRIDGE_RE.fullmatch(rel_path):
        return None
    if snapshot is not None and rel_path in snapshot.status_by_path:
        path_status = snapshot.status_by_path[rel_path]
        if path_status == "D" or path_status.endswith("-source"):
            return None
        content = _staged_text(root, rel_path, snapshot)
    else:
        if not (root / rel_path).exists():
            return None
        content = _staged_or_worktree_text(root, rel_path)
    status = _first_nonblank_line(content)
    if status and not STATUS_RE.fullmatch(status):
        return {
            "path": rel_path,
            "reason": f"versioned bridge file has invalid status token {status!r}",
        }
    if status != "VERIFIED":
        return None
    if _superseded_versioned_bridge(rel_path, snapshot):
        # A superseded predecessor VERIFIED is committed as inert history; it is
        # not the live terminal state and needs no Commit Finalization Evidence.
        return None
    if _has_commit_finalization_evidence(content):
        return None
    return {
        "path": rel_path,
        "reason": "terminal VERIFIED bridge file lacks Commit Finalization Evidence with a same-transaction path set",
    }


def _load_live_go_evidence(
    root: Path, candidate_paths: list[str] | None = None
) -> tuple[list[dict[str, Any]], list[str], int]:
    """Load live GO packet evidence.

    WI-5742 Layer B2: ``candidate_paths`` is the protected-path set actually
    being evaluated. Passing it lets the packet enumerator skip full bridge-chain
    validation for packets that provably cannot authorize any of those paths.
    The returned ``valid_packets`` -- the only field that decides clearance -- is
    unchanged, because every skipped packet fails a necessary condition for
    clearance. Skipped packets still produce a row and a populated error, so the
    fail-closed reporting surface stays populated.
    """
    # WI-7129: canonical evidence is the primary authorization source. The named
    # packet cache lives under the forbidden runtime state directory, so a route
    # that can only clear from there fails once that surface is purged -- which
    # is exactly what blocked WI-5183 after it passed every review and test.
    #
    # The canonical route derives the same facts from the approved bridge chain
    # and the approved proposal's declared target_paths, so when it clears a path
    # the forbidden directory is never read. The packet cache is consulted only
    # when canonical evidence clears nothing, which keeps transitional flows that
    # still depend on a minted packet working without making clearance require it.
    # An unauthorized cohort is denied by both routes: neither invents a row.
    canonical_rows, canonical_errors = canonical_go_authorizations(root, candidate_paths=candidate_paths)
    if canonical_rows and (
        candidate_paths is None
        or any(path_authorized(row, candidate) for row in canonical_rows for candidate in candidate_paths)
    ):
        return canonical_rows, canonical_errors, len(canonical_rows)

    errors: list[str] = list(canonical_errors)
    try:
        if candidate_paths is None:
            packets = list_named_packets(root)
        else:
            try:
                packets = list_named_packets(root, candidate_paths=candidate_paths)
            except TypeError:
                # A caller or test double still bound to the pre-WI-5742
                # single-argument signature. Degrade to the exhaustive
                # enumeration -- slower, but identical evidence. Without this
                # the arity mismatch would be swallowed by the fail-closed
                # handler below and silently DENY a path that a live GO packet
                # should have cleared, which is an authorization regression
                # rather than a performance one.
                packets = list_named_packets(root)
    except Exception as exc:  # noqa: BLE001 - fail closed on authorization subsystem errors.
        return [], [f"could not list implementation authorization packets: {exc}"], 0

    valid_packets: list[dict[str, Any]] = []
    for packet in packets:
        if packet.get("error"):
            errors.append(f"{packet.get('path', '<unknown-packet>')}: {packet['error']}")
            continue
        if packet.get("valid") is True:
            valid_packets.append(packet)
    return valid_packets, errors, len(packets)


def _live_go_authorization(
    packets: list[dict[str, Any]], errors: list[str], rel_path: str
) -> tuple[bool, str | None, list[str]]:
    for packet in packets:
        if path_authorized(packet, rel_path):
            return True, str(packet.get("bridge_id") or packet.get("path") or "<unknown-packet>"), errors
    return False, None, errors


def _version_by_path(resolution: Any, rel_path: str | None) -> Any | None:
    if not rel_path:
        return None
    return next((version for version in resolution.audit_versions if version.path == rel_path), None)


def _controlling_go_path(report_text: str) -> str | None:
    matches = CONTROLLING_GO_RE.findall(report_text)
    if len(matches) > 1:
        raise GateError("implementation report declares more than one Controlling GO")
    return matches[0] if matches else None


def _approved_chain(snapshot_root: Path, resolution: Any) -> _ApprovedChain:
    latest = resolution.latest_strict_state
    if latest.status != "VERIFIED" or not latest.responds_to:
        raise GateError("latest lifecycle state is not a report-linked VERIFIED verdict")
    report = _version_by_path(resolution, latest.responds_to)
    # WI-6726 Surface B follow-on: canon section 6 replaced the retired post-GO
    # NEW with READY as the implementation-report status, so a compliant
    # NEW -> GO -> READY -> VERIFIED chain was rejected here as "not linked to a
    # Prime implementation report". NEW and REVISED are retained because canon
    # section 6 keeps historical GO -> NEW chains readable via
    # HISTORICAL_TRANSITIONS, and this gate reads committed history.
    if report is None or report.status not in {"NEW", "REVISED", "READY"} or report.author_role != "prime-builder":
        raise GateError("VERIFIED verdict is not linked to a Prime implementation report")
    try:
        report_text = (snapshot_root / report.path).read_text(encoding="utf-8")
    except OSError as exc:
        raise GateError(f"could not read linked implementation report {report.path}: {exc}") from exc
    if IMPLEMENTATION_REPORT_RE.search(report_text) is None:
        raise GateError("linked Prime artifact is not an implementation report")

    direct_go = _version_by_path(resolution, report.responds_to)
    explicit_go_path = _controlling_go_path(report_text)
    if direct_go is not None and direct_go.status == "GO" and direct_go.author_role == "loyal-opposition":
        if explicit_go_path is not None and explicit_go_path != direct_go.path:
            raise GateError("implementation report's Controlling GO conflicts with its Responds to GO")
        go = direct_go
    else:
        go = _version_by_path(resolution, explicit_go_path)
    if go is None or go.status != "GO" or go.author_role != "loyal-opposition":
        raise GateError("implementation report is not linked to its approving GO")
    proposal = _version_by_path(resolution, go.responds_to)
    if proposal is None or proposal.status not in {"NEW", "REVISED"} or proposal.author_role != "prime-builder":
        raise GateError("approving GO is not linked to a Prime proposal")
    try:
        proposal_text = (snapshot_root / proposal.path).read_text(encoding="utf-8")
        target_paths = tuple(_normalize_rel(path) for path in extract_target_paths(proposal_text))
    except (OSError, AuthorizationError) as exc:
        raise GateError(f"could not resolve approved proposal target scope: {exc}") from exc
    if not target_paths or len(target_paths) != len(set(target_paths)):
        raise GateError("approved proposal target scope is empty or duplicated")
    return _ApprovedChain(
        proposal_path=proposal.path,
        go_path=go.path,
        report_path=report.path,
        target_paths=target_paths,
    )


def _packet_target_paths(packet: dict[str, Any]) -> list[str] | None:
    raw_targets = packet.get("target_path_globs")
    if not isinstance(raw_targets, list) or not raw_targets:
        return None
    if any(not isinstance(target, str) or not target.strip() for target in raw_targets):
        return None
    return [_normalize_rel(target) for target in raw_targets]


def _packet_binding_errors(
    packet_path: Path,
    packet: dict[str, Any],
    bridge_id: str,
    chain: _ApprovedChain,
    *,
    require_schema_v3: bool,
) -> list[str]:
    errors: list[str] = []
    if packet_path.stem != bridge_id:
        errors.append(f"{bridge_id}: named packet filename does not match bridge id")
    if packet.get("bridge_id") != bridge_id:
        errors.append(f"{bridge_id}: named packet object names another bridge")
    allowed_schemas = {3} if require_schema_v3 else {2, 3}
    if packet.get("schema_version") not in allowed_schemas:
        errors.append(f"{bridge_id}: named packet has an unsupported schema")
    if packet.get("packet_hash") != packet_hash(packet):
        errors.append(f"{bridge_id}: named packet hash mismatch")
    if packet.get("proposal_file") != chain.proposal_path:
        errors.append(f"{bridge_id}: named packet is not bound to the resolver-approved proposal")
    if packet.get("go_file") != chain.go_path:
        errors.append(f"{bridge_id}: named packet is not bound to the resolver-approved GO")
    packet_targets = _packet_target_paths(packet)
    if packet_targets is None or tuple(packet_targets) != chain.target_paths:
        errors.append(f"{bridge_id}: named packet target scope differs from the resolver-approved proposal")
    return errors


def _committed_bridge_entries_by_id(root: Path, head_oid: str) -> dict[str, tuple[_IndexEntry, ...]]:
    """Enumerate the committed ``bridge/`` tree ONCE and group versioned entries by
    bridge slug, so callers can look up a chain's committed entries without
    re-running ``git ls-tree`` (and re-parsing the full ~13k-file inventory) per
    packet. This turns ``_load_verified_evidence`` from
    O(packets x committed-bridge-files) into O(packets + committed-bridge-files).
    Grouping by ``VERSIONED_BRIDGE_CAPTURE_RE`` bridge_id is equivalent to the
    prior per-bridge exact-slug filter.
    """
    listing = _run_git(root, "ls-tree", "-r", "-z", head_oid, "--", "bridge")
    if listing.returncode != 0:
        raise GateError(f"could not enumerate committed bridge history: {listing.stderr!r}")
    by_id: dict[str, list[_IndexEntry]] = {}
    for entry in _parse_tree_inventory(listing.stdout):
        match = VERSIONED_BRIDGE_CAPTURE_RE.fullmatch(entry.rel_path)
        if match is not None:
            by_id.setdefault(match.group("bridge_id"), []).append(entry)
    return {bridge_id: tuple(entries) for bridge_id, entries in by_id.items()}


def _load_verified_evidence(
    root: Path,
    head_oid: str | None = None,
    protected_paths: list[str] | None = None,
) -> tuple[list[tuple[str, list[str]]], list[str], int]:
    errors: list[str] = []
    evidence: list[tuple[str, list[str]]] = []
    by_bridge_dir = root / BY_BRIDGE_PACKETS_REL
    if not by_bridge_dir.is_dir():
        return evidence, errors, 0

    packet_paths = sorted(by_bridge_dir.glob("*.json"))
    if packet_paths and head_oid is None:
        return evidence, ["terminal VERIFIED evidence cannot be read without a pinned HEAD commit"], len(packet_paths)
    # WI-5658: enumerate committed bridge history ONCE and group by bridge-id, so the
    # per-packet loop below is O(packets + committed-bridge-files) instead of
    # re-running ls-tree over all committed bridge files for each packet.
    head_entries_by_bridge = (
        _committed_bridge_entries_by_id(root, head_oid) if (packet_paths and head_oid is not None) else {}
    )
    for packet_path in packet_paths:
        try:
            packet = json.loads(packet_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{packet_path.relative_to(root).as_posix()}: corrupt or unreadable: {exc}")
            continue
        if not isinstance(packet, dict):
            errors.append(f"{packet_path.relative_to(root).as_posix()}: decoded packet root is not an object")
            continue
        bridge_id = packet.get("bridge_id")
        if not isinstance(bridge_id, str) or not bridge_id.strip():
            continue
        # WI-5659: pre-filter to packets that could authorize a staged protected
        # path before the expensive _bridge_snapshot + resolve_bridge_lifecycle.
        # By the _packet_binding_errors invariant a packet contributes to evidence
        # only when its stored target_path_globs == the resolver-approved
        # chain.target_paths, and _verified_authorization matches those exact
        # globs. So a packet whose stored globs authorize none of the staged
        # protected paths cannot change any cleared/finding outcome, and
        # verified_errors are only diagnostic context on already-failing paths;
        # skip its resolution. The scanned-packet count below stays total, so
        # evidence_summary's terminal_verified_packets_scanned remains honest.
        # protected_paths=None preserves legacy full-scan behavior for callers
        # that do not pass it.
        if protected_paths is not None:
            packet_globs = _packet_target_paths(packet)
            if packet_globs is None or not any(
                path_authorized({"target_path_globs": packet_globs}, rel_path) for rel_path in protected_paths
            ):
                continue
        try:
            with _bridge_snapshot(
                root,
                bridge_id,
                head_oid=head_oid,
                precomputed_head_entries=head_entries_by_bridge.get(bridge_id, ()),
            ) as bridge_snapshot:
                snapshot_root = bridge_snapshot.root
                with _immutable_snapshot(bridge_snapshot):
                    resolution = resolve_bridge_lifecycle(snapshot_root, bridge_id)
                    latest = resolution.latest_strict_state
                    if latest.status != "VERIFIED":
                        continue
                    if resolution.blocking_diagnostics:
                        errors.append(f"{bridge_id}: terminal VERIFIED thread has blocking lifecycle diagnostics")
                        continue
                    chain = _approved_chain(snapshot_root, resolution)
        except (BridgeLifecycleResolutionError, GateError, OSError, ValueError) as exc:
            errors.append(f"{bridge_id}: could not read bridge thread: {exc}")
            continue
        binding_errors = _packet_binding_errors(packet_path, packet, bridge_id, chain, require_schema_v3=False)
        if binding_errors:
            errors.extend(binding_errors)
            continue
        evidence.append((bridge_id, list(chain.target_paths)))
    return evidence, errors, len(packet_paths)


def _verified_authorization(
    evidence: list[tuple[str, list[str]]], errors: list[str], rel_path: str
) -> tuple[bool, str | None, list[str]]:
    for bridge_id, target_paths in evidence:
        if path_authorized({"target_path_globs": target_paths}, rel_path):
            return True, bridge_id, errors
    return False, None, errors


def _manifest_path_error(root: Path, raw_path: str) -> str | None:
    if not raw_path:
        return "same-transaction manifest contains an empty path"
    if Path(raw_path).is_absolute() or re.match(r"^[A-Za-z]:", raw_path):
        return f"same-transaction manifest contains absolute path {raw_path!r}"
    if ".." in Path(raw_path).parts:
        return f"same-transaction manifest contains path escape {raw_path!r}"
    if raw_path == ".git" or raw_path.startswith(".git/"):
        return f"same-transaction manifest contains forbidden Git path {raw_path!r}"
    if GLOB_META_RE.search(raw_path):
        return f"same-transaction manifest contains glob path {raw_path!r}"
    if raw_path.endswith("/") or (root / raw_path).is_dir():
        return f"same-transaction manifest contains directory shorthand {raw_path!r}"
    try:
        _validated_index_path(raw_path.encode("utf-8"))
    except GateError:
        return f"same-transaction manifest contains non-canonical or unsafe path {raw_path!r}"
    return None


def _parse_transaction_manifest(root: Path, content: str) -> tuple[list[str], list[str]]:
    section = _section_body(content, "Commit Finalization Evidence")
    if not section:
        return [], ["VERIFIED candidate lacks Commit Finalization Evidence"]

    lines = [line.strip() for line in section.splitlines()]
    markers = [index for index, line in enumerate(lines) if line == "- Same-transaction path set:"]
    if len(markers) != 1:
        return [], ["VERIFIED candidate must contain exactly one Same-transaction path set marker"]

    paths: list[str] = []
    errors: list[str] = []
    for line in lines[markers[0] + 1 :]:
        if not line:
            if paths:
                break
            continue
        match = MANIFEST_PATH_RE.fullmatch(line)
        if match is None:
            break
        raw_path = match.group(1)
        path_error = _manifest_path_error(root, raw_path)
        if path_error:
            errors.append(path_error)
        paths.append(raw_path)

    if not paths:
        errors.append("VERIFIED candidate same-transaction path set is empty")
    duplicates = sorted({path for path in paths if paths.count(path) > 1})
    if duplicates:
        errors.append("same-transaction manifest contains duplicate path(s): " + ", ".join(duplicates))
    collision_keys: dict[str, str] = {}
    for path in paths:
        collision_key = unicodedata.normalize("NFC", path).casefold()
        prior = collision_keys.get(collision_key)
        if prior is not None and prior != path:
            errors.append(f"same-transaction manifest contains casefold or Unicode collision: {prior!r}, {path!r}")
        collision_keys[collision_key] = path
    return paths, errors


def _transaction_manifest_relation_errors(manifest_paths: list[str], selected_paths: list[str]) -> list[str]:
    """Reject only staged paths that the reviewer-authored manifest did not declare.

    A declared path may legitimately be unchanged.  The inverse is never true:
    staging an undeclared path would expand the transaction beyond the verdict.
    """

    undeclared = sorted(set(selected_paths) - set(manifest_paths))
    if not undeclared:
        return []
    return [f"same-transaction manifest does not equal the staged path set; missing={undeclared}"]


def _batch_manifest_hash(payload: dict[str, Any]) -> str:
    canonical = dict(payload)
    canonical.pop("manifest_hash", None)
    encoded = json.dumps(canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def _batch_candidate_plan_hash(payload: dict[str, Any]) -> str:
    fields = (
        "authority_bridge_id",
        "authority_packet_hash",
        "authority_session_id",
        "owner_decision_id",
        "project_authorization_id",
        "head_oid",
        "head_ref",
        "candidate_bridge_id",
        "candidate_path",
        "candidate_content_digest",
        "selected_paths",
        "declared_paths",
    )
    encoded = json.dumps(
        {field: payload.get(field) for field in fields},
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def _batch_foreign_claim_errors(root: Path, candidate_bridge_id: str, selected_paths: list[str]) -> list[str]:
    from scripts import bridge_work_intent_registry

    db_path = (root / "groundtruth.db").resolve()
    try:
        conn = sqlite3.connect(db_path.as_uri() + "?mode=ro", uri=True)
        rows = conn.execute("SELECT thread_slug FROM work_intent_claims ORDER BY thread_slug").fetchall()
    except sqlite3.Error as exc:
        return [f"batch-finalization active claim inventory is unreadable: {exc}"]
    finally:
        if "conn" in locals():
            conn.close()

    errors: list[str] = []
    for (slug,) in rows:
        if slug in {candidate_bridge_id, BATCH_FINALIZATION_AUTHORITY}:
            continue
        try:
            holder = bridge_work_intent_registry.current_holder(slug, project_root=root)
        except bridge_work_intent_registry.WorkIntentRegistryError as exc:
            errors.append(f"batch-finalization foreign claim {slug!r} is unreadable: {exc}")
            continue
        if not holder or holder.get("claim_kind") != "go_implementation":
            continue
        try:
            packet = load_named_packet(root, slug)
        except AuthorizationError as exc:
            errors.append(f"batch-finalization foreign claim {slug!r} has unreadable target scope: {exc}")
            continue
        overlap = sorted(path for path in selected_paths if path_authorized(packet, path))
        if overlap:
            errors.append(f"batch-finalization staged paths overlap active foreign claim {slug!r}: {overlap}")
    return errors


def _load_batch_finalization_authority(
    root: Path,
    *,
    snapshot: _IndexSnapshot,
    candidate_path: str,
    bridge_id: str,
    manifest_paths: list[str],
    protected_paths: list[str],
) -> tuple[dict[str, Any] | None, list[str]]:
    """Load a fail-closed WI-6073 transaction manifest, when explicitly supplied.

    The manifest is evidence, not a bypass flag.  It binds the copied index,
    candidate blob, pinned HEAD, live carrier packet, and active Prime claim.
    """

    from scripts import bridge_work_intent_registry

    raw_rel = os.environ.get(BATCH_FINALIZATION_ENV)
    if raw_rel is None:
        return None, []
    errors: list[str] = []
    rel = _normalize_rel(raw_rel)
    rel_path = Path(rel)
    if (
        not rel
        or rel_path.is_absolute()
        or re.match(r"^[A-Za-z]:", rel)
        or ".." in rel_path.parts
        or rel_path.suffix.lower() != ".json"
        or rel_path.parent.as_posix() != BATCH_FINALIZATION_REL.as_posix()
    ):
        return None, ["batch-finalization manifest path is not a direct governed runtime manifest"]
    path = root / rel_path
    try:
        resolved = path.resolve(strict=True)
        resolved_root = root.resolve(strict=True)
        expected_parent = (root / BATCH_FINALIZATION_REL).resolve(strict=True)
        try:
            resolved.relative_to(resolved_root)
        except ValueError:
            return None, ["batch-finalization manifest resolves outside the project root"]
        lexical_ancestors = (path, *path.parents)
        linked_ancestor = any(
            _path_is_linklike(ancestor)
            for ancestor in lexical_ancestors
            if ancestor != root.parent and (ancestor == root or root in ancestor.parents)
        )
        if resolved.parent != expected_parent or linked_ancestor:
            return None, ["batch-finalization manifest path is linked or escapes its governed runtime directory"]
        if resolved.stat().st_size > BATCH_FINALIZATION_MAX_BYTES:
            return None, ["batch-finalization manifest exceeds its size limit"]
        payload = json.loads(resolved.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, [f"batch-finalization manifest is unreadable or invalid: {exc}"]
    if not isinstance(payload, dict):
        return None, ["batch-finalization manifest root is not an object"]

    required = {
        "schema_version",
        "operation",
        "authority_bridge_id",
        "authority_packet_hash",
        "authority_session_id",
        "owner_decision_id",
        "project_authorization_id",
        "head_oid",
        "head_ref",
        "candidate_bridge_id",
        "candidate_path",
        "candidate_content_digest",
        "selected_paths",
        "declared_paths",
        "plan_digest",
        "candidate_plan_digest",
        "created_at",
        "expires_at",
        "nonce",
        "manifest_hash",
    }
    if set(payload) != required:
        errors.append("batch-finalization manifest fields do not match schema version 1")
    if payload.get("schema_version") != 1 or payload.get("operation") != "verified_batch_finalize":
        errors.append("batch-finalization manifest has the wrong schema or operation")
    if payload.get("authority_bridge_id") != BATCH_FINALIZATION_AUTHORITY:
        errors.append("batch-finalization manifest names the wrong authority bridge")
    if payload.get("owner_decision_id") != BATCH_FINALIZATION_OWNER_DECISION:
        errors.append("batch-finalization manifest names the wrong owner decision")
    if payload.get("project_authorization_id") != BATCH_FINALIZATION_PAUTH:
        errors.append("batch-finalization manifest names the wrong project authorization")
    if payload.get("manifest_hash") != _batch_manifest_hash(payload):
        errors.append("batch-finalization manifest hash mismatch")
    if payload.get("candidate_plan_digest") != _batch_candidate_plan_hash(payload):
        errors.append("batch-finalization candidate plan digest mismatch")
    try:
        created_at = parse_iso(str(payload.get("created_at") or ""))
        expires_at = parse_iso(str(payload.get("expires_at") or ""))
    except (TypeError, ValueError):
        created_at = None
        expires_at = None
        errors.append("batch-finalization manifest timestamps are invalid")
    if created_at is not None and expires_at is not None:
        now = datetime.now(UTC)
        if (
            created_at > now + timedelta(seconds=30)
            or expires_at <= now
            or expires_at <= created_at
            or expires_at - created_at > timedelta(minutes=5)
        ):
            errors.append("batch-finalization manifest is outside its live transaction window")
    if not isinstance(payload.get("nonce"), str) or re.fullmatch(r"[0-9a-f]{32}", payload["nonce"]) is None:
        errors.append("batch-finalization manifest nonce is invalid")
    if payload.get("head_oid") != snapshot.head_oid:
        errors.append("batch-finalization manifest is not bound to the copied index HEAD")
    if payload.get("head_ref") != _resolve_head_ref(root, snapshot.head_oid):
        errors.append("batch-finalization manifest is not bound to the active symbolic HEAD ref")
    if payload.get("candidate_bridge_id") != bridge_id or payload.get("candidate_path") != candidate_path:
        errors.append("batch-finalization manifest is not bound to the VERIFIED candidate")
    selected_manifest_paths = payload.get("selected_paths")
    if (
        not isinstance(selected_manifest_paths, list)
        or any(not isinstance(path, str) for path in selected_manifest_paths)
        or len(selected_manifest_paths) != len(set(selected_manifest_paths))
        or set(selected_manifest_paths) != set(snapshot.selected_paths)
    ):
        errors.append("batch-finalization manifest selected path set differs from the copied index")
    else:
        errors.extend(_batch_foreign_claim_errors(root, bridge_id, selected_manifest_paths))
    if payload.get("declared_paths") != manifest_paths:
        errors.append("batch-finalization manifest declared path set differs from the VERIFIED candidate")
    staged_digest, staged_error = _staged_index_content_digest(root, candidate_path, snapshot)
    if staged_error is not None:
        errors.append(staged_error)
    elif payload.get("candidate_content_digest") != staged_digest:
        errors.append("batch-finalization manifest candidate content digest mismatch")
    plan_digest = payload.get("plan_digest")
    if not isinstance(plan_digest, str) or not re.fullmatch(r"sha256:[0-9a-f]{64}", plan_digest):
        errors.append("batch-finalization manifest plan digest is invalid")

    authority_packet: dict[str, Any] | None = None
    try:
        authority_packet = load_named_packet(root, BATCH_FINALIZATION_AUTHORITY)
    except AuthorizationError as exc:
        errors.append(f"batch-finalization authority packet is invalid: {exc}")
    if authority_packet is not None:
        if payload.get("authority_packet_hash") != authority_packet.get("packet_hash"):
            errors.append("batch-finalization manifest authority packet hash mismatch")
        start = authority_packet.get("implementation_start")
        start_session = start.get("session_id") if isinstance(start, dict) else None
        if payload.get("authority_session_id") != start_session:
            errors.append("batch-finalization manifest authority session differs from implementation start")
        if resolve_session_id() != payload.get("authority_session_id"):
            errors.append("batch-finalization invoking session does not own the authority claim")
        project_authorization = authority_packet.get("project_authorization")
        if not isinstance(project_authorization, dict) or project_authorization.get("id") != BATCH_FINALIZATION_PAUTH:
            errors.append("batch-finalization authority packet is not bound to the approved PAUTH")
        try:
            holder = bridge_work_intent_registry.current_holder(BATCH_FINALIZATION_AUTHORITY, project_root=root)
        except bridge_work_intent_registry.WorkIntentRegistryError as exc:
            holder = None
            errors.append(f"batch-finalization work-intent claim is unreadable: {exc}")
        if not isinstance(holder, dict):
            errors.append("batch-finalization authority has no active work-intent claim")
        elif not (
            holder.get("session_id") == payload.get("authority_session_id")
            and holder.get("claim_kind") == "go_implementation"
            and holder.get("acting_role") == "prime-builder"
        ):
            errors.append("batch-finalization work-intent claim does not match the Prime implementation session")
        try:
            validate_packet_project_authorization_operation(
                root,
                authority_packet,
                requested_operations=["protected_mutation"],
                target_paths=protected_paths,
            )
        except AuthorizationError as exc:
            errors.append(f"batch-finalization current PAUTH validation failed: {exc}")
    return (authority_packet if not errors else None), errors


def _load_finalized_packet(
    root: Path,
    bridge_id: str,
    chain: _ApprovedChain,
    protected_paths: list[str],
    *,
    batch_authority_packet: dict[str, Any] | None = None,
    pauth_root: Path | None = None,
) -> tuple[dict[str, Any] | None, list[str]]:
    errors: list[str] = []
    try:
        named_path = packet_path_for_bridge(root, bridge_id)
        packet = json.loads(named_path.read_text(encoding="utf-8"))
    except AuthorizationError as exc:
        return None, [f"{bridge_id}: implementation-start packet path is invalid: {exc}"]
    except FileNotFoundError:
        return None, [f"{bridge_id}: implementation-start packet is absent"]
    except json.JSONDecodeError as exc:
        return None, [f"{bridge_id}: implementation-start packet is not valid JSON: {exc}"]
    except OSError as exc:
        return None, [f"{bridge_id}: implementation-start packet is unreadable: {exc}"]

    if not isinstance(packet, dict):
        return None, [f"{bridge_id}: implementation-start packet root is not an object"]
    errors.extend(_packet_binding_errors(named_path, packet, bridge_id, chain, require_schema_v3=True))
    target_paths = _packet_target_paths(packet)
    # WI-5824 Fix B (DELIB-202667723): the finalized implementation-start packet
    # is evidence of implementation-time authority. Transaction-local terminal
    # evidence is judged by the time of the act -- the implementation start must
    # fall inside the packet's live window -- not by ambient wall-clock time, so
    # an atomic finalize-verified transaction is not denied merely because the
    # packet expired between implementation start and verification.
    try:
        packet_expires = parse_iso(str(packet["expires_at"]))
    except (KeyError, TypeError, ValueError):
        packet_expires = None
        errors.append(f"{bridge_id}: implementation-start packet has invalid expiry")

    implementation_start = packet.get("implementation_start")
    if not isinstance(implementation_start, dict):
        errors.append(f"{bridge_id}: implementation-start packet is not finalized")
    else:
        if implementation_start.get("schema_version") != 2:
            errors.append(f"{bridge_id}: implementation-start evidence has an unsupported schema")
        if implementation_start.get("bridge_id") != bridge_id:
            errors.append(f"{bridge_id}: finalized implementation-start names another bridge")
        if (
            not isinstance(implementation_start.get("finalized_at"), str)
            or not implementation_start["finalized_at"].strip()
        ):
            errors.append(f"{bridge_id}: implementation-start packet is not finalized")
        else:
            try:
                finalized_at = parse_iso(implementation_start["finalized_at"])
            except (TypeError, ValueError):
                finalized_at = None
                errors.append(f"{bridge_id}: implementation-start finalized_at is unparseable")
            if finalized_at is not None and packet_expires is not None and finalized_at > packet_expires:
                errors.append(f"{bridge_id}: implementation-start packet was not live at implementation")
        start_targets = implementation_start.get("target_path_globs")
        normalized_start_targets = (
            [_normalize_rel(target) for target in start_targets]
            if isinstance(start_targets, list)
            and all(isinstance(target, str) and target.strip() for target in start_targets)
            else None
        )
        if normalized_start_targets is None or target_paths is None or normalized_start_targets != target_paths:
            errors.append(f"{bridge_id}: finalized implementation-start target scope does not match packet scope")
        claim = implementation_start.get("work_intent_claim")
        role_attestation = implementation_start.get("role_attestation")
        start_session = str(implementation_start.get("session_id") or "")
        if not start_session:
            errors.append(f"{bridge_id}: finalized implementation-start lacks a session id")
        if not isinstance(claim, dict):
            errors.append(f"{bridge_id}: finalized implementation-start lacks a work-intent claim")
        elif claim.get("thread_slug") != bridge_id:
            errors.append(f"{bridge_id}: finalized implementation-start claim does not match the bridge")
        else:
            if claim.get("session_id") != start_session:
                errors.append(f"{bridge_id}: finalized implementation-start claim session differs from start session")
            report_resume = claim.get("claim_kind") == "draft" and isinstance(
                implementation_start.get("resumption_authority"), dict
            )
            if claim.get("claim_kind") != "go_implementation" and not report_resume:
                errors.append(f"{bridge_id}: finalized implementation-start claim kind is not go_implementation")
            if not report_resume:
                if claim.get("acting_role") != "prime-builder":
                    errors.append(f"{bridge_id}: finalized implementation-start claim acting role is not prime-builder")
                claim_envelope_id = claim.get("session_envelope_id")
                if not isinstance(claim_envelope_id, str) or not claim_envelope_id:
                    errors.append(f"{bridge_id}: finalized implementation-start claim lacks a session envelope id")
                claim_attestation = claim.get("acting_role_attestation")
                if not isinstance(claim_attestation, str) or not claim_attestation:
                    errors.append(
                        f"{bridge_id}: finalized implementation-start claim lacks a role-attestation reference"
                    )
        if not isinstance(role_attestation, dict):
            errors.append(f"{bridge_id}: finalized implementation-start lacks exact-init role-attestation evidence")
        else:
            if role_attestation.get("schema_version") != 1:
                errors.append(f"{bridge_id}: finalized implementation-start role-attestation schema is unsupported")
            if role_attestation.get("invoking_context") != start_session:
                errors.append(
                    f"{bridge_id}: finalized implementation-start attested context differs from start session"
                )
            if role_attestation.get("role") != "prime-builder":
                errors.append(f"{bridge_id}: finalized implementation-start attested role is not prime-builder")
            if role_attestation.get("source_event") != "exact_init":
                errors.append(f"{bridge_id}: finalized implementation-start role authority is not exact-init")
            envelope_id = role_attestation.get("session_envelope_id")
            if not isinstance(envelope_id, str) or not envelope_id:
                errors.append(
                    f"{bridge_id}: finalized implementation-start role attestation lacks a session envelope id"
                )
            evidence_reference = role_attestation.get("evidence_reference")
            if not isinstance(evidence_reference, str) or not evidence_reference:
                errors.append(
                    f"{bridge_id}: finalized implementation-start role attestation lacks an evidence reference"
                )
            if isinstance(claim, dict) and claim.get("claim_kind") == "go_implementation":
                if claim.get("session_envelope_id") != envelope_id:
                    errors.append(
                        f"{bridge_id}: finalized implementation-start claim envelope differs from role attestation"
                    )
                if claim.get("acting_role_attestation") != evidence_reference:
                    errors.append(
                        f"{bridge_id}: finalized implementation-start claim reference differs from role attestation"
                    )
        decision = implementation_start.get("project_authorization_decision")
        if not isinstance(decision, dict) or decision.get("allowed") is not True:
            errors.append(f"{bridge_id}: finalized implementation-start lacks an allowed project decision")
        pre_start_hash = implementation_start.get("pre_start_packet_hash")
        if not isinstance(pre_start_hash, str) or not pre_start_hash:
            errors.append(f"{bridge_id}: finalized implementation-start lacks a pre-start packet hash")
        else:
            pre_start = dict(packet)
            pre_start.pop("implementation_start", None)
            pre_start["schema_version"] = 2
            pre_start["packet_hash"] = pre_start_hash
            if packet_hash(pre_start) != pre_start_hash:
                errors.append(f"{bridge_id}: finalized implementation-start pre-start packet hash mismatch")

    project_authorization = packet.get("project_authorization")
    if not isinstance(project_authorization, dict):
        errors.append(f"{bridge_id}: finalized implementation-start lacks project authorization")
    elif isinstance(implementation_start, dict):
        claim = implementation_start.get("work_intent_claim")
        if isinstance(claim, dict) and claim.get("project_id") != project_authorization.get("project_id"):
            errors.append(f"{bridge_id}: implementation-start claim project differs from packet PAUTH")
        try:
            validate_packet_project_authorization_operation(
                pauth_root or root,
                packet,
                requested_operations=["protected_mutation"],
                target_paths=list(chain.target_paths),
            )
        except AuthorizationError as exc:
            # Ordinary current-PAUTH validation remains the first route. The
            # WI-6073 carrier substitutes only for immutable snapshot drift on
            # the same PAUTH identity; every other failure remains a denial.
            drift_error = "drifted since packet creation" in str(exc)
            carrier_pauth = (
                batch_authority_packet.get("project_authorization")
                if isinstance(batch_authority_packet, dict)
                else None
            )
            if not (
                drift_error
                and isinstance(carrier_pauth, dict)
                and carrier_pauth.get("id") == project_authorization.get("id")
                and carrier_pauth.get("project_id") == project_authorization.get("project_id")
            ):
                errors.append(f"{bridge_id}: protected-mutation PAUTH validation failed: {exc}")

    if target_paths is not None:
        unauthorized_paths = [path for path in protected_paths if not path_authorized(packet, path)]
        if unauthorized_paths:
            errors.append(
                f"{bridge_id}: finalized implementation-start packet does not authorize protected staged path(s): "
                + ", ".join(unauthorized_paths)
            )
    return (packet if not errors else None), errors


def _single_author_session(content: str, label: str, errors: list[str]) -> str | None:
    session_ids = AUTHOR_SESSION_RE.findall(content)
    if len(session_ids) != 1:
        errors.append(f"{label} must contain exactly one author_session_context_id header")
        return None
    return session_ids[0]


def _load_transaction_verified_evidence(
    root: Path,
    protected_paths: list[str],
    snapshot: _IndexSnapshot,
) -> tuple[tuple[str, dict[str, Any]] | None, list[str], str | None]:
    selected_paths = list(snapshot.selected_paths)
    candidates: list[tuple[str, str]] = []
    for rel_path in selected_paths:
        if not VERSIONED_BRIDGE_RE.fullmatch(rel_path):
            continue
        status = snapshot.status_by_path[rel_path]
        if status == "D" or status.endswith("-source"):
            continue
        try:
            content = _staged_text(root, rel_path, snapshot)
        except GateError as exc:
            return None, [str(exc)], rel_path
        if _first_nonblank_line(content) == "VERIFIED":
            if _superseded_versioned_bridge(rel_path, snapshot):
                # Superseded predecessor VERIFIED is non-authoritative history,
                # not a live terminal candidate; only the latest-per-chain
                # VERIFIED counts toward the exactly-one-candidate clearance.
                continue
            candidates.append((rel_path, content))

    if not candidates:
        return None, [], None
    if len(candidates) != 1:
        paths = ", ".join(path for path, _ in candidates)
        return (
            None,
            [f"same-transaction clearance requires exactly one VERIFIED candidate; found {len(candidates)}: {paths}"],
            candidates[0][0],
        )

    candidate_path, content = candidates[0]
    errors: list[str] = []
    identity_match = VERSIONED_BRIDGE_CAPTURE_RE.fullmatch(candidate_path)
    if identity_match is None:
        return None, [f"VERIFIED candidate has invalid numbered bridge path: {candidate_path}"], candidate_path
    bridge_id = identity_match.group("bridge_id")

    if snapshot.status_by_path.get(candidate_path) != "A":
        errors.append("transaction-local VERIFIED candidate is not a Git-added staged file")

    manifest_paths, manifest_errors = _parse_transaction_manifest(root, content)
    errors.extend(manifest_errors)
    if len(selected_paths) != len(set(selected_paths)):
        errors.append("staged path set contains duplicate normalized paths")
    errors.extend(_transaction_manifest_relation_errors(manifest_paths, selected_paths))

    batch_authority_packet, batch_errors = _load_batch_finalization_authority(
        root,
        snapshot=snapshot,
        candidate_path=candidate_path,
        bridge_id=bridge_id,
        manifest_paths=manifest_paths,
        protected_paths=protected_paths,
    )
    errors.extend(batch_errors)

    chain: _ApprovedChain | None = None
    report_text: str | None = None
    proposal_text: str | None = None
    packet: dict[str, Any] | None = None
    try:
        with _bridge_snapshot(root, bridge_id, snapshot) as bridge_snapshot:
            snapshot_root = bridge_snapshot.root
            _verify_snapshot_ledger(bridge_snapshot)
            with _immutable_snapshot(bridge_snapshot):
                try:
                    resolution = resolve_bridge_lifecycle(snapshot_root, bridge_id)
                except (BridgeLifecycleResolutionError, OSError, ValueError) as exc:
                    resolution = None
                    errors.append(f"{bridge_id}: VERIFIED candidate lifecycle is invalid: {exc}")
            _verify_snapshot_ledger(bridge_snapshot)

            if resolution is not None:
                latest = resolution.latest_strict_state
                if resolution.blocking_diagnostics:
                    errors.append(f"{bridge_id}: VERIFIED candidate lifecycle has blocking diagnostics")
                if latest.path != candidate_path or latest.status != "VERIFIED":
                    errors.append(f"{bridge_id}: VERIFIED candidate is not the exact latest strict lifecycle state")
                with _immutable_snapshot(bridge_snapshot):
                    try:
                        chain = _approved_chain(snapshot_root, resolution)
                        proposal_text = (snapshot_root / chain.proposal_path).read_text(encoding="utf-8")
                        report_text = (snapshot_root / chain.report_path).read_text(encoding="utf-8")
                    except (GateError, OSError) as exc:
                        errors.append(f"{bridge_id}: VERIFIED candidate approved-chain validation failed: {exc}")
            _verify_snapshot_ledger(bridge_snapshot)

            with _immutable_snapshot(bridge_snapshot):
                anchor_violations = validate_verdict_evidence_anchors(content, project_root=snapshot_root)
            if anchor_violations:
                errors.append(f"{bridge_id}: VERIFIED candidate has invalid evidence anchors: {anchor_violations}")
            _verify_snapshot_ledger(bridge_snapshot)
            candidate_session = _single_author_session(content, f"{bridge_id} VERIFIED candidate", errors)
            report_session = (
                _single_author_session(report_text, f"{bridge_id} implementation report", errors)
                if report_text is not None
                else None
            )
            if candidate_session is not None and report_session is not None and candidate_session == report_session:
                errors.append(f"{bridge_id}: VERIFIED candidate is a same-session self-review")

            if chain is not None:
                with _immutable_snapshot(bridge_snapshot):
                    self_review_reason = verdict_self_review_reason(
                        content,
                        bridge_id,
                        snapshot_root,
                        expected_artifact_path=chain.report_path,
                    )
                if self_review_reason is not None:
                    errors.append(f"{bridge_id}: VERIFIED candidate review independence failed: {self_review_reason}")
            _verify_snapshot_ledger(bridge_snapshot)

            requires_pauth_snapshot = _requires_pauth_read_snapshot(
                _first_nonblank_line(content),
                proposal_text,
                report_text,
                content,
            )
            effective_context = (
                _pauth_read_snapshot(root, bridge_snapshot) if requires_pauth_snapshot else nullcontext(bridge_snapshot)
            )
            with effective_context as effective_snapshot:
                try:
                    _run_snapshot_compliance_audit(
                        snapshot=effective_snapshot,
                        candidate_path=candidate_path,
                        content=content,
                    )
                except (BridgeComplianceError, OSError, subprocess.SubprocessError) as exc:
                    errors.append(f"{bridge_id}: VERIFIED candidate bridge-compliance audit failed: {exc}")
                _verify_snapshot_ledger(effective_snapshot)
                if chain is not None:
                    with _immutable_snapshot(effective_snapshot):
                        packet, packet_errors = _load_finalized_packet(
                            root,
                            bridge_id,
                            chain,
                            protected_paths,
                            batch_authority_packet=batch_authority_packet,
                            pauth_root=effective_snapshot.root if requires_pauth_snapshot else root,
                        )
                    errors.extend(packet_errors)
                _verify_snapshot_ledger(effective_snapshot)
    except GateError as exc:
        errors.append(str(exc))

    metadata = extract_author_metadata(content)
    gaps = author_metadata_gaps(metadata)
    if gaps:
        errors.append(f"{bridge_id}: VERIFIED candidate author metadata is incomplete: {', '.join(gaps)}")
    elif is_synthetic_session_context_id(metadata.get("author_session_context_id")):
        errors.append(f"{bridge_id}: VERIFIED candidate author session context is synthetic")

    if chain is None:
        errors.append(f"{bridge_id}: no resolver-approved chain exists for packet validation")

    if errors or packet is None:
        return None, errors, candidate_path
    return (bridge_id, packet), [], candidate_path


def _evaluate_protected_path(
    rel_path: str,
    *,
    live_go_packets: list[dict[str, Any]],
    live_go_errors: list[str],
    verified_evidence: list[tuple[str, list[str]]],
    verified_errors: list[str],
    transaction_evidence: tuple[str, dict[str, Any]] | None,
    transaction_errors: list[str],
    transaction_available: bool,
) -> dict[str, Any]:
    go_allowed, go_source, go_errors = _live_go_authorization(live_go_packets, live_go_errors, rel_path)
    if go_allowed:
        return {"path": rel_path, "status": "cleared", "evidence": "live_go_packet", "source": go_source}

    terminal_allowed, verified_source, terminal_errors = _verified_authorization(
        verified_evidence, verified_errors, rel_path
    )
    if terminal_allowed:
        return {
            "path": rel_path,
            "status": "cleared",
            "evidence": "terminal_verified_bridge_thread",
            "source": verified_source,
        }

    if transaction_evidence is not None:
        transaction_source, transaction_packet = transaction_evidence
        if path_authorized(transaction_packet, rel_path):
            return {
                "path": rel_path,
                "status": "cleared",
                "evidence": "transaction_local_verified_manifest",
                "source": transaction_source,
            }

    errors = go_errors + terminal_errors + transaction_errors
    evidence_routes = "live GO authorization packet or committed terminal VERIFIED bridge evidence"
    if transaction_available:
        evidence_routes += " or valid transaction-local VERIFIED evidence"
    finding: dict[str, Any] = {
        "path": rel_path,
        "reason": f"protected path lacks {evidence_routes}",
    }
    if errors:
        finding["evidence_errors"] = errors
    return finding


def _staged_index_content_digest(
    root: Path,
    rel_path: str,
    index_snapshot: _IndexSnapshot | None,
) -> tuple[str | None, str | None]:
    """Return the SHA-256 digest of one exact blob from the copied Git index."""
    if index_snapshot is None:
        return None, "bridge publication evidence requires an immutable staged-index snapshot"

    inventory = _run_index_git(
        root,
        index_snapshot,
        "ls-files",
        "--stage",
        "-z",
        "--",
        f":(literal){rel_path}",
    )
    if inventory.returncode != 0:
        return None, f"could not resolve staged bridge path from copied index: {inventory.stderr!r}"
    try:
        entries = _parse_index_inventory(inventory.stdout)
    except GateError as exc:
        return None, str(exc)
    if len(entries) != 1 or entries[0].rel_path != rel_path:
        return None, "staged bridge path does not resolve to one exact regular index blob"

    entry = entries[0]
    blob = _run_index_git(root, index_snapshot, "cat-file", "blob", entry.oid)
    if blob.returncode != 0:
        return None, f"could not read staged bridge blob from copied index: {blob.stderr!r}"
    if len(blob.stdout) > MAX_BLOB_BYTES:
        return None, f"staged bridge blob exceeds {MAX_BLOB_BYTES}-byte authorization limit"

    object_hasher = hashlib.new(index_snapshot.object_format)
    object_hasher.update(f"blob {len(blob.stdout)}\0".encode("ascii"))
    object_hasher.update(blob.stdout)
    if object_hasher.hexdigest().lower() != entry.oid.lower():
        return None, "staged bridge blob does not hash to its copied-index object id"
    return "sha256:" + hashlib.sha256(blob.stdout).hexdigest(), None


def _is_valid_iso_timestamp(value: object) -> bool:
    """Null-safe timestamp validity: a non-empty string that ``parse_iso`` accepts.

    WI-5824 Fix A: ``parse_iso`` requires a string (``None.endswith`` raises
    ``AttributeError``), so capability timestamp checks route through this
    guard instead of parsing raw row values directly.
    """
    if not isinstance(value, str) or not value:
        return False
    try:
        parse_iso(value)
    except (TypeError, ValueError):
        return False
    return True


def _newest_exact_bridge_publication_capability(
    conn: sqlite3.Connection,
    *,
    record_id: str,
    rel_path: str,
) -> sqlite3.Row | None:
    return conn.execute(
        "SELECT * FROM sot_registry_bridge_publication_capabilities "
        "WHERE aggregate_entry_id = ? AND target_path = ? ORDER BY rowid DESC LIMIT 1",
        (record_id, rel_path),
    ).fetchone()


def _bridge_publication_capability_clearance(
    conn: sqlite3.Connection,
    *,
    root: Path,
    record_id: str,
    rel_path: str,
    index_snapshot: _IndexSnapshot | None,
    capability: sqlite3.Row | None = None,
) -> tuple[bool, str]:
    """Evaluate the newest exact publication attempt for one staged bridge path."""
    if capability is None:
        capability = _newest_exact_bridge_publication_capability(
            conn,
            record_id=record_id,
            rel_path=rel_path,
        )
    if capability is None:
        return False, "registered bridge path lacks exact publication capability evidence"

    target = VERSIONED_BRIDGE_CAPTURE_RE.fullmatch(rel_path)
    try:
        version = int(capability["version"])
    except (TypeError, ValueError):
        version = -1
    if (
        target is None
        or capability["document_name"] != target.group("bridge_id")
        or version != int(target.group("version"))
        or capability["target_path"] != rel_path
        or capability["aggregate_entry_id"] != record_id
    ):
        return False, "bridge publication capability target identity mismatch"
    if capability["authority_kind"] != "bridge_publication" or capability["operation"] != "bridge_publication":
        return False, "bridge publication capability has the wrong authority type"

    # WI-5824 Fix A: capability_state is evaluated before any consumed_at
    # handling, and every timestamp check is null-safe, so no capability row
    # shape can escape this function as an uncaught exception. consumed_at is
    # null by design on minted/recovery_required rows, which deny precisely on
    # state below without ever reaching consumed_at parsing.
    # expires_at bounds mint-to-consume use. Once consumed, the immutable row is
    # archival commit evidence and remains valid after that short publication TTL.
    if not _is_valid_iso_timestamp(capability["expires_at"]):
        return False, "bridge publication capability has incomplete or invalid timestamps"
    if (
        capability["capability_state"] == "compensated"
        or capability["compensation_revision_id"]
        or capability["compensation_digest"]
    ):
        return False, "bridge publication capability was compensated or failed"
    if capability["capability_state"] != "consumed":
        return False, f"bridge publication capability is not consumed ({capability['capability_state']!r})"
    # Defense in depth for rows on the consumed path: consumed_at must be a
    # non-null string that parses; any other shape is the clean deny below.
    if not _is_valid_iso_timestamp(capability["consumed_at"]):
        return False, "bridge publication capability has incomplete or invalid timestamps"
    if not capability["result_digest"] or not capability["revision_id"]:
        return False, "bridge publication capability lacks consumed result or revision evidence"
    if capability["failure_reason"]:
        return False, "bridge publication capability was compensated or failed"

    revision = conn.execute(
        "SELECT * FROM sot_artifact_revisions WHERE revision_id = ?",
        (capability["revision_id"],),
    ).fetchone()
    if revision is None:
        return False, "bridge publication capability linked revision is missing"
    if not (
        revision["entry_id"] == record_id
        and revision["operation"] == "bridge_publication"
        and revision["capability_hash"] == capability["capability_hash"]
        and revision["bridge_id"] == capability["document_name"]
    ):
        return False, "bridge publication capability revision linkage mismatch"

    staged_digest, staged_error = _staged_index_content_digest(root, rel_path, index_snapshot)
    if staged_error is not None:
        return False, staged_error
    if capability["content_digest"] != staged_digest:
        return False, "bridge publication staged content digest mismatch"
    return True, ""


def _registry_commit_assessment(
    root: Path,
    selected_paths: list[str],
    index_snapshot: _IndexSnapshot | None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Enforce identity controls and report content-observation gaps separately."""
    package_src = root / "groundtruth-kb" / "src"
    if str(package_src) not in sys.path:
        sys.path.insert(0, str(package_src))
    registry_path = root / "config" / "registry" / "sot-artifacts.toml"
    transient_paths = [path for path in selected_paths if TRANSIENT_INDEX_PATH_RE.fullmatch(path)]
    if not registry_path.is_file():
        if transient_paths:
            return (
                [
                    {
                        "path": path,
                        "reason": "transient Git index deletion requires coherent registry authority",
                    }
                    for path in transient_paths
                ],
                [],
            )
        return [], []
    try:
        # WI-5742 Layer B1: inside an active cache scope this reuses the single
        # snapshot already loaded for path classification instead of taking the
        # exclusive control-plane lock a second time.
        from scripts.controlled_artifact_paths import load_registry_snapshot_cached

        registry = load_registry_snapshot_cached(project_root=root)
    except Exception as exc:  # noqa: BLE001 - commit authority fails closed
        return (
            [
                {
                    "path": "config/registry/sot-artifacts.toml",
                    "reason": f"coherent registry authority unavailable: {exc}",
                }
            ],
            [],
        )

    conn = sqlite3.connect(str(root / "groundtruth.db"))
    conn.row_factory = sqlite3.Row
    findings: list[dict[str, Any]] = []
    audit_gaps: list[dict[str, Any]] = []
    try:
        for rel_path in selected_paths:
            record = registry.resolver.resolve(rel_path)
            staged_status = index_snapshot.status_by_path.get(rel_path, "") if index_snapshot is not None else ""
            if TRANSIENT_INDEX_PATH_RE.fullmatch(rel_path):
                if staged_status != "D":
                    findings.append(
                        {
                            "path": rel_path,
                            "reason": "transient Git index recurrence is forbidden; only an unregistered deletion is allowed",
                        }
                    )
                    continue
                if record is None:
                    continue
            if record is None:
                continue
            if staged_status == "D" or staged_status.endswith("-source"):
                findings.append(
                    {
                        "path": rel_path,
                        "reason": "registered identity delete/move/rename requires separately authorized transition",
                    }
                )
                continue
            publication_capability = _newest_exact_bridge_publication_capability(
                conn,
                record_id=record.id,
                rel_path=rel_path,
            )
            if VERSIONED_BRIDGE_CAPTURE_RE.fullmatch(rel_path):
                publication_bound, publication_reason = _bridge_publication_capability_clearance(
                    conn,
                    root=root,
                    record_id=record.id,
                    rel_path=rel_path,
                    index_snapshot=index_snapshot,
                    capability=publication_capability,
                )
                if not publication_bound:
                    findings.append({"path": rel_path, "reason": publication_reason})
                continue
            revision = conn.execute(
                "SELECT * FROM sot_artifact_revisions WHERE entry_id = ? ORDER BY rowid DESC LIMIT 1",
                (record.id,),
            ).fetchone()
            if revision is None:
                audit_gaps.append(
                    {
                        "path": rel_path,
                        "registry_id": record.id,
                        "reason": "registered artifact lacks content-observation revision evidence",
                    }
                )
                continue
            if record.coverage_mode == "exact":
                staged_digest, staged_error = _staged_index_content_digest(root, rel_path, index_snapshot)
                if staged_error is not None:
                    audit_gaps.append(
                        {
                            "path": rel_path,
                            "registry_id": record.id,
                            "reason": staged_error,
                        }
                    )
                elif revision["content_digest"] != staged_digest:
                    audit_gaps.append(
                        {
                            "path": rel_path,
                            "registry_id": record.id,
                            "reason": "staged bytes are newer than the latest registry observation",
                        }
                    )
            capability_bound = False
            if revision["capability_hash"]:
                capability = conn.execute(
                    "SELECT * FROM sot_registry_observation_capabilities WHERE capability_hash = ?",
                    (revision["capability_hash"],),
                ).fetchone()
                if capability is not None:
                    try:
                        capability_paths = {_normalize_rel(path) for path in json.loads(capability["paths_json"])}
                    except (TypeError, ValueError, json.JSONDecodeError):
                        capability_paths = set()
                    capability_bound = bool(
                        capability["capability_state"] == "consumed"
                        and capability["consumed_at"]
                        and capability["result_digest"]
                        and rel_path in capability_paths
                        and capability["bridge_id"] == revision["bridge_id"]
                        and capability["start_packet_hash"] == revision["start_packet_hash"]
                        and capability["pauth_decision_json"] == revision["pauth_decision"]
                    )
            journal_bound = False
            if revision["journal_id"]:
                journal = conn.execute(
                    "SELECT journal_state, start_packet_hash, pauth_id, bridge_id, receipt_digest "
                    "FROM sot_registry_transaction_journal WHERE journal_id = ?",
                    (revision["journal_id"],),
                ).fetchone()
                journal_bound = bool(
                    journal
                    and journal["journal_state"] == "committed"
                    and journal["start_packet_hash"]
                    and journal["pauth_id"]
                    and journal["bridge_id"]
                    and journal["receipt_digest"]
                    and journal["bridge_id"] == revision["bridge_id"]
                    and journal["start_packet_hash"] == revision["start_packet_hash"]
                )
            if not capability_bound and not journal_bound:
                audit_gaps.append(
                    {
                        "path": rel_path,
                        "registry_id": record.id,
                        "reason": "registered artifact lacks automatic observation or transaction evidence",
                    }
                )
    except sqlite3.Error as exc:
        findings.append(
            {
                "path": "groundtruth.db",
                "reason": f"registry evidence store is unavailable: {exc}",
            }
        )
    finally:
        conn.close()
    unique_gaps = {(gap["path"], gap["registry_id"], gap["reason"]): gap for gap in audit_gaps}
    return findings, list(unique_gaps.values())


def _registry_commit_findings(
    root: Path,
    selected_paths: list[str],
    index_snapshot: _IndexSnapshot | None,
) -> list[dict[str, Any]]:
    """Compatibility view containing only commit-blocking registry findings."""

    findings, _audit_gaps = _registry_commit_assessment(root, selected_paths, index_snapshot)
    return findings


def _evaluate_selected(
    root: Path,
    selected_paths: list[str],
    snapshot: _IndexSnapshot | None,
    head_oid: str | None,
    budget: _EvaluationBudget | None = None,
) -> dict[str, Any]:
    # WI-5742 Layer B3: classify each selected path exactly once and derive both
    # partitions from that single pass. The previous form evaluated
    # ``is_protected_path`` once per path and then re-scanned the protected list
    # with an O(n) membership test per path to build the complement.
    if budget is not None:
        budget.enter("classification")
    protected_paths: list[str] = []
    skipped_unprotected: list[str] = []
    for path in selected_paths:
        if is_protected_path(path, project_root=root):
            protected_paths.append(path)
        else:
            skipped_unprotected.append(path)
        if budget is not None:
            budget.check()

    bridge_findings = [
        finding
        for path in selected_paths
        if (finding := _verified_bridge_finalization_finding(root, path, snapshot)) is not None
    ]
    if budget is not None:
        budget.enter("registry_assessment")
    registry_findings, registry_audit_gaps = _registry_commit_assessment(root, selected_paths, snapshot)
    bridge_findings.extend(registry_findings)

    batch_transaction_requested = bool(os.environ.get(BATCH_FINALIZATION_ENV))
    if not protected_paths and not bridge_findings and not batch_transaction_requested:
        return {
            "status": "pass",
            "findings": [],
            "cleared": [],
            "skipped_unprotected": skipped_unprotected,
            "protected_paths": [],
            "audit_gaps": registry_audit_gaps,
            "evidence_summary": {
                "live_go_packets_scanned": 0,
                "live_go_packets_valid": 0,
                "terminal_verified_packets_scanned": 0,
                "terminal_verified_threads_loaded": 0,
            },
        }

    live_go_packets: list[dict[str, Any]] = []
    live_go_errors: list[str] = []
    live_go_count = 0
    verified_evidence: list[tuple[str, list[str]]] = []
    verified_errors: list[str] = []
    verified_packet_count = 0
    transaction_evidence: tuple[str, dict[str, Any]] | None = None
    transaction_errors: list[str] = []
    transaction_candidate_path: str | None = None
    if protected_paths:
        if budget is not None:
            budget.enter("live_go_evidence")
        # WI-5742 Layer B2: only protected paths can be cleared by a live GO
        # packet, so they are the exact candidate set for the pre-filter.
        live_go_packets, live_go_errors, live_go_count = _load_live_go_evidence(root, candidate_paths=protected_paths)
        if budget is not None:
            budget.enter("verified_evidence")
        verified_evidence, verified_errors, verified_packet_count = _load_verified_evidence(
            root, head_oid=head_oid, protected_paths=protected_paths
        )
    if snapshot is not None and (protected_paths or batch_transaction_requested):
        if budget is not None:
            budget.enter("transaction_evidence")
        transaction_evidence, transaction_errors, transaction_candidate_path = _load_transaction_verified_evidence(
            root,
            protected_paths,
            snapshot,
        )

    findings: list[dict[str, Any]] = list(bridge_findings)
    if transaction_errors and transaction_candidate_path is not None:
        findings.append(
            {
                "path": transaction_candidate_path,
                "reason": "transaction-local VERIFIED candidate validation failed",
                "evidence_errors": transaction_errors,
            }
        )
    cleared: list[dict[str, Any]] = []
    if budget is not None:
        budget.enter("per_path")
    for rel_path in protected_paths:
        if budget is not None:
            budget.check()
        result = _evaluate_protected_path(
            rel_path,
            live_go_packets=live_go_packets,
            live_go_errors=live_go_errors,
            verified_evidence=verified_evidence,
            verified_errors=verified_errors,
            transaction_evidence=transaction_evidence,
            transaction_errors=transaction_errors,
            transaction_available=snapshot is not None,
        )
        if result.get("status") == "cleared":
            cleared.append(result)
        else:
            findings.append(result)

    return {
        "status": "fail" if findings else "pass",
        "findings": findings,
        "cleared": cleared,
        "skipped_unprotected": skipped_unprotected,
        "protected_paths": protected_paths,
        "audit_gaps": registry_audit_gaps,
        "evidence_summary": {
            "live_go_packets_scanned": live_go_count,
            "live_go_packets_valid": len(live_go_packets),
            "terminal_verified_packets_scanned": verified_packet_count,
            "terminal_verified_threads_loaded": len(verified_evidence),
        },
    }


def evaluate(
    root: Path,
    *,
    paths: list[str] | None = None,
    budget: _EvaluationBudget | None = None,
) -> dict[str, Any]:
    """Evaluate protected-commit authorization for a staged or explicit path set.

    WI-5742: the whole evaluation runs inside a fail-closed wall-clock budget
    (Layer A) and one invocation-scoped registry snapshot cache (Layer B1). On
    budget exhaustion this returns a deterministic deny verdict carrying phase
    evidence -- it never passes on timeout and never hangs.

    ``budget`` is injectable so tests can drive the bound with a fake clock
    without depending on real elapsed time.
    """
    root = root.resolve()
    if budget is None:
        budget = _resolve_evaluation_budget(root)
    try:
        # The cache scope is strictly this invocation: it collapses the N+1
        # exclusive-lock snapshot loads to 1 and is discarded on exit, so no
        # stale-authority window is created for any mutating caller.
        with registry_snapshot_cache_scope():
            head_oid = _resolve_head_oid(root)
            if paths is not None:
                selected_paths = [_normalize_rel(path) for path in paths]
                return _evaluate_selected(root, selected_paths, None, head_oid, budget=budget)
            budget.enter("index_snapshot")
            with _index_snapshot(root, head_oid) as snapshot:
                return _evaluate_selected(root, list(snapshot.selected_paths), snapshot, head_oid, budget=budget)
    except EvaluationBoundExceeded as exc:
        return exc.as_result()


def _format_human(result: dict[str, Any], *, transaction_available: bool = False) -> str:
    if result["status"] == "pass":
        audit_suffix = (
            f"; {len(result.get('audit_gaps', []))} registry audit gap(s) recorded" if result.get("audit_gaps") else ""
        )
        if result["cleared"]:
            return (
                f"PASS protected-commit authorization ({len(result['cleared'])} protected path(s) cleared"
                f"{audit_suffix})"
            )
        return f"PASS protected-commit authorization (no protected paths in staged set{audit_suffix})"

    lines = ["FAIL protected-commit authorization"]
    for finding in result["findings"]:
        lines.append(f"  - {finding['path']}: {finding['reason']}")
        for error in finding.get("evidence_errors", []):
            lines.append(f"    evidence error: {error}")
    lines.append("")
    if transaction_available:
        lines.append(
            "Protected staged files require a live GO implementation packet, committed terminal VERIFIED bridge "
            "evidence, or transaction-local VERIFIED manifest evidence."
        )
    else:
        lines.append(
            "Protected files require either a live GO implementation packet or committed terminal VERIFIED evidence."
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--staged", action="store_true", help="Read staged paths from git diff --cached.")
    selection.add_argument("--paths", nargs="*", help="Explicit paths to check.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    args = parser.parse_args(argv)

    try:
        result = evaluate(args.project_root, paths=list(args.paths) if args.paths is not None else None)
    except GateError as exc:
        sys.stderr.write(f"protected-commit authorization gate error: {exc}\n")
        return 2

    if args.json:
        sys.stdout.write(json.dumps(result, indent=2, sort_keys=True))
        sys.stdout.write("\n")
    else:
        sys.stdout.write(_format_human(result, transaction_available=args.staged))
        sys.stdout.write("\n")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
