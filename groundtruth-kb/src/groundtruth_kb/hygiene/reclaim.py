"""Deterministic, reversible hygiene reclaim planning and actuation.

Planning is metadata-only apart from its durable run ledger. Reclaim first
moves selected files into same-volume reversible trash. A separate, governed
purge actuator can then permanently delete exact receipted payloads to reclaim
physical disk space while retaining the hash-chained audit trail.
"""

from __future__ import annotations

import fnmatch
import hashlib
import json
import os
import re
import stat
import subprocess
from collections.abc import Iterator
from contextlib import contextmanager, suppress
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from groundtruth_kb.inventory import InventoryScanError, build_refresh_report
from groundtruth_kb.project.registry_control_plane import (
    RegistryControlPlaneError,
    RegistryProjectionMismatch,
    load_registry_snapshot,
)
from groundtruth_kb.project.sot_registry import SoTArtifact, default_registry_path

_SCHEMA_VERSION = 1
_GENESIS_HASH = "GENESIS"
_HEX_FANOUT_RE = re.compile(r"^[0-9a-f]{2}$")
_LOOSE_NAME_RE = re.compile(r"^[0-9a-f]{38}$")
_GIT_TMP_OBJECT_RE = re.compile(r"^tmp_obj_[A-Za-z0-9]+$")
_OID_RE = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
_EXTERNAL_STORAGE_SCHEMES = ("membase:", "windows-scheduled-task:")
_SCRATCH_COMPONENTS = frozenset({".harness-tmp", ".loyal-opposition"})
_SCRATCH_NAME_PREFIXES = (
    ".temp_verdict_body",
    "_temp_draft",
    "_draft_verdict_body_",
)
_DETRITUS_CLASSES = frozenset(
    {
        "stale_workspace_detritus",
        "stale_runtime_detritus",
    }
)
# Standing delete authorization is bounded to these two dispositions only, per
# .harness-baseline-configuration/rules/prime-builder.md (WI-6743, Route B).
# `unregistered` routes to receipted quarantine and `owner_gated` is the
# fail-closed default; neither may be added here without a fresh owner decision.
_STANDING_DELETE_AUTHORIZED = frozenset({"derived", "cached"})

# WI-6743 F1. The governing rule states that code, tests, features and
# specifications cannot satisfy the DERIVED or CACHED evidence conditions. The
# classifier therefore hard-denies these classes on ``rel_path`` BEFORE any
# evidence is weighed, so no combination of caller-supplied strings can
# authorize deletion of a protected artifact. A false deny costs an owner
# prompt; a false allow deletes protected source. The asymmetry is the reason
# this list is deliberately broad.
# Extensions that are unambiguously authored source in this repository. The
# JS/TS family is deliberately ABSENT: bundlers legitimately emit ".js"/".ts"
# as build output, which is the canonical DERIVED case this feature exists to
# authorize. Denying by extension there would break the feature rather than
# secure it, so JS/TS source is covered by the protected-tree rule below
# instead of by suffix.
_STANDING_DELETE_DENIED_SUFFIXES = frozenset(
    {
        ".bash",
        ".c",
        ".cc",
        ".cfg",
        ".cpp",
        ".cs",
        ".go",
        ".h",
        ".hpp",
        ".ini",
        ".java",
        ".ps1",
        ".psm1",
        ".py",
        ".pyi",
        ".rb",
        ".rs",
        ".sh",
        ".sql",
        ".toml",
    }
)
_STANDING_DELETE_DENIED_PARTS = frozenset(
    {
        ".harness-baseline-configuration",
        "migrations",
        "platform_tests",
        "spec",
        "specifications",
        "specs",
        "src",
        "test",
        "tests",
    }
)
_STANDING_DELETE_DENIED_NAME_PREFIXES = (
    "ADR-",
    "DCL-",
    "DELIB-",
    "GOV-",
    "PAUTH-",
    "PB-",
    "REQ-",
    "SPEC-",
    "WI-",
)
# Evidence is only trustworthy when a governed verifier issued it. Caller-
# asserted generator/source-of-truth strings are inputs, not proof.
_STANDING_DELETE_TRUSTED_EVIDENCE_SOURCES = frozenset(
    {
        "governed_regeneration_verifier",
        "governed_sot_verifier",
    }
)


def _standing_delete_protected_class(rel_path: str) -> str | None:
    """Return the protected artifact class of ``rel_path``, or ``None``.

    A non-``None`` result means the object may never receive an authorized
    standing-delete disposition, regardless of the evidence supplied.
    """
    # ``removeprefix`` and not ``lstrip("./")``: lstrip strips any leading "."
    # or "/" character, which silently converts ".claude/hooks/x" into
    # "claude/hooks/x" and defeats every dot-prefixed protected path.
    normalized = str(rel_path).replace("\\", "/").strip().removeprefix("./")
    if not normalized:
        return "unresolvable_path"
    path = Path(normalized)
    name = path.name

    if name in _PROTECTED_EXACT:
        return "protected_exact_artifact"
    if normalized.startswith(_PROTECTED_PREFIXES):
        return "protected_path_prefix"
    if any(part in _STANDING_DELETE_DENIED_PARTS for part in path.parts):
        return "protected_source_or_test_tree"
    if path.suffix.lower() in _STANDING_DELETE_DENIED_SUFFIXES:
        return "protected_code_or_config"
    if name.startswith(_STANDING_DELETE_DENIED_NAME_PREFIXES):
        return "protected_specification_or_governance"
    if name.startswith("test_") or name.endswith(("_test.py", "_test.ts", "_test.go")):
        return "protected_test"
    return None


_DIRECTORY_SOURCE_KINDS = frozenset({"worktree_directory"})
_ROOT_DETRITUS_EXACT = frozenset(
    {
        "__pycache__",
        ".harness-tmp",
        ".hypothesis",
        ".loyal-opposition",
        ".pytest_cache",
        ".ruff_cache",
        ".test-tmp",
        ".tmp",
        ".gtkb-tmp",
    }
)
_ROOT_DETRITUS_PREFIXES = (
    "__tmp_",
    ".harness-tmp-",
    ".pytest",
    ".tmp-",
    "GT-KB.gtkb-statepytest-",
    "GT-KB.gtkb-statemodernization-release-candidatesemantic-evidencepytest-temp",
)
_STATE_DETRITUS_EXACT = frozenset(
    {
        "__pycache__",
        "bridge-revisions",
        "database-carrier-restoration",
        "headless-temp",
        "release-worktrees",
        "tmp",
        "uv-cache",
        "verification-temp",
    }
)
_STATE_DETRITUS_PREFIXES = (
    "antigravity-wi",
    "codex-pytest",
    "codex-wi",
    "lo-wi",
    "modernization-db-reconstruction",
    "pytest",
    "tmp",
)
_STATE_DETRITUS_SUFFIXES = (
    ".tar",
    ".patch",
    ".index",
    ".out",
    ".err",
)
_STATE_WORK_ITEM_DETRITUS_RE = re.compile(r"^(?:antigravity-wi|codex-wi|lo-wi|wi)\d")
_PROTECTED_PREFIXES = (
    ".claude/hooks/",
    ".claude/rules/",
    ".claude/session/",
    ".codex/gtkb-hooks/",
    ".github/workflows/",
    "bridge/",
    "config/",
    "groundtruth-kb/src/",
    "groundtruth-kb/tests/",
    "independent-progress-assessments/",
    "memory/",
    "platform_tests/",
    "scripts/",
    "tests/",
)
_PROTECTED_EXACT = frozenset(
    {
        ".dockerignore",
        ".env",
        ".env.local",
        "AGENTS.md",
        "CLAUDE.md",
        "Dockerfile",
        "Dockerfile.test",
        "Dockerfile.ui",
        "docker-compose.yml",
        "env.local",
        "env.staging",
        "shopify.app.toml",
    }
)
_ALLOWED_EVENTS = frozenset(
    {
        "plan_created",
        "planned",
        "trash_started",
        "trashed",
        "purge_started",
        "purged",
        "restore_started",
        "restored",
        "refused",
    }
)


class ReclaimError(RuntimeError):
    """Raised when reclaim evidence is incomplete or a mutation is unsafe."""


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def _stable_hash(value: Any) -> str:
    return "sha256:" + hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _digest_strings(values: set[str] | list[str] | tuple[str, ...]) -> str:
    digest = hashlib.sha256()
    for value in sorted(values):
        digest.update(value.encode("utf-8", errors="surrogateescape"))
        digest.update(b"\0")
    return "sha256:" + digest.hexdigest()


def _as_utc(value: datetime | None) -> datetime:
    current = value or datetime.now(UTC)
    if current.tzinfo is None:
        raise ReclaimError("now must include timezone information")
    return current.astimezone(UTC)


def _iso(value: datetime) -> str:
    return value.astimezone(UTC).isoformat(timespec="microseconds").replace("+00:00", "Z")


def _root_path(root: Path) -> Path:
    try:
        resolved = Path(root).expanduser().resolve(strict=True)
    except OSError as exc:
        raise ReclaimError(f"repository root cannot be resolved: {exc}") from exc
    if not resolved.is_dir():
        raise ReclaimError(f"repository root is not a directory: {resolved}")
    top_level = _git_text(resolved, ["rev-parse", "--show-toplevel"]).strip()
    try:
        git_root = Path(top_level).resolve(strict=True)
    except OSError as exc:
        raise ReclaimError(f"Git top-level path cannot be resolved: {exc}") from exc
    if git_root != resolved:
        raise ReclaimError(f"root must be the Git top-level directory: {git_root}")
    return resolved


def _is_within(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def _state_path(root: Path, state_root: Path | None) -> Path:
    requested = root / ".gtkb-state" / "hygiene-reclaim" if state_root is None else Path(state_root)
    if not requested.is_absolute():
        requested = root / requested
    resolved = requested.expanduser().resolve(strict=False)
    if resolved == root or not _is_within(resolved, root):
        raise ReclaimError("state_root must resolve to a dedicated directory inside the repository root")
    return resolved


def _git_process(
    root: Path,
    args: list[str],
    *,
    cwd: Path | None = None,
    input_bytes: bytes | None = None,
) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", *args],
        cwd=cwd or root,
        input=input_bytes,
        capture_output=True,
        check=False,
    )


def _git_bytes(
    root: Path,
    args: list[str],
    *,
    cwd: Path | None = None,
    input_bytes: bytes | None = None,
) -> bytes:
    result = _git_process(root, args, cwd=cwd, input_bytes=input_bytes)
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).decode("utf-8", errors="replace").strip()
        raise ReclaimError(f"git {' '.join(args)} failed: {detail}")
    return result.stdout


def _git_text(root: Path, args: list[str], *, cwd: Path | None = None) -> str:
    return _git_bytes(root, args, cwd=cwd).decode("utf-8", errors="surrogateescape")


def _decode_z(output: bytes) -> set[str]:
    return {
        token.decode("utf-8", errors="surrogateescape").replace("\\", "/") for token in output.split(b"\0") if token
    }


def _safe_relative_path(value: str) -> bool:
    path = Path(value)
    return bool(value) and not path.is_absolute() and ".." not in path.parts


def _common_git_dir(root: Path) -> Path:
    raw = _git_text(root, ["rev-parse", "--git-common-dir"]).strip()
    path = Path(raw)
    if not path.is_absolute():
        path = root / path
    return path.resolve(strict=True)


def _parse_worktrees(root: Path, defects: list[dict[str, str]]) -> list[dict[str, str | None]]:
    output = _git_text(root, ["worktree", "list", "--porcelain"])
    records: list[dict[str, str | None]] = []
    for block in output.strip().split("\n\n") if output.strip() else []:
        record: dict[str, str | None] = {"path": None, "head": None, "branch": None}
        for line in block.splitlines():
            key, _, value = line.partition(" ")
            if key == "worktree":
                record["path"] = value
            elif key == "HEAD":
                record["head"] = value
            elif key == "branch":
                record["branch"] = value
        if not record["path"] or not record["head"]:
            defects.append({"code": "git_worktree_record_incomplete", "detail": block})
        records.append(record)
    return records


def _parse_index_oids(output: bytes, label: str, defects: list[dict[str, str]]) -> set[str]:
    oids: set[str] = set()
    for token in output.split(b"\0"):
        if not token:
            continue
        metadata, separator, _path = token.partition(b"\t")
        fields = metadata.split()
        if not separator or len(fields) != 3:
            defects.append({"code": "git_index_record_malformed", "detail": label})
            continue
        oid = fields[1].decode("ascii", errors="replace")
        if not _OID_RE.fullmatch(oid):
            defects.append({"code": "git_index_oid_malformed", "detail": f"{label}:{oid}"})
            continue
        oids.add(oid)
    return oids


def _reflog_oids(common_dir: Path, defects: list[dict[str, str]]) -> set[str]:
    logs = common_dir / "logs"
    if not logs.exists():
        return set()
    if not logs.is_dir():
        defects.append({"code": "git_reflog_root_invalid", "detail": str(logs)})
        return set()
    oids: set[str] = set()
    for directory, dirnames, filenames in os.walk(logs, followlinks=False):
        dirnames.sort()
        filenames.sort()
        for name in filenames:
            path = Path(directory) / name
            try:
                if path.is_symlink() or not path.is_file():
                    defects.append({"code": "git_reflog_artifact_unsupported", "detail": str(path)})
                    continue
                with path.open("r", encoding="utf-8", errors="replace") as handle:
                    for line_number, line in enumerate(handle, start=1):
                        fields = line.split(maxsplit=2)
                        if len(fields) < 2:
                            defects.append(
                                {
                                    "code": "git_reflog_record_malformed",
                                    "detail": f"{path}:{line_number}",
                                }
                            )
                            continue
                        for oid in fields[:2]:
                            if set(oid) == {"0"}:
                                continue
                            if not _OID_RE.fullmatch(oid):
                                defects.append(
                                    {
                                        "code": "git_reflog_oid_malformed",
                                        "detail": f"{path}:{line_number}",
                                    }
                                )
                                continue
                            oids.add(oid)
            except OSError as exc:
                defects.append({"code": "git_reflog_unreadable", "detail": f"{path}: {exc}"})
    return oids


def _batch_object_info(root: Path, oids: set[str]) -> dict[str, tuple[str, int] | None]:
    if not oids:
        return {}
    payload = "".join(f"{oid}\n" for oid in sorted(oids)).encode("ascii")
    output = _git_bytes(
        root,
        ["cat-file", "--batch-check=%(objectname) %(objecttype) %(objectsize)"],
        input_bytes=payload,
    ).decode("ascii", errors="replace")
    info: dict[str, tuple[str, int] | None] = {}
    for requested, line in zip(sorted(oids), output.splitlines(), strict=False):
        fields = line.split()
        if len(fields) == 2 and fields[1] in {"missing", "ambiguous"}:
            info[requested] = None
        elif len(fields) == 3 and fields[0] == requested:
            try:
                info[requested] = (fields[1], int(fields[2]))
            except ValueError:
                info[requested] = None
        else:
            info[requested] = None
    for oid in oids:
        info.setdefault(oid, None)
    return info


def _collect_git_evidence(root: Path) -> dict[str, Any]:
    defects: list[dict[str, str]] = []
    common_dir = _common_git_dir(root)
    if not _is_within(common_dir, root):
        defects.append({"code": "git_common_dir_outside_root", "detail": str(common_dir)})

    tracked = _decode_z(_git_bytes(root, ["ls-files", "-z"]))
    untracked = _decode_z(_git_bytes(root, ["ls-files", "--others", "--exclude-standard", "-z"]))
    ignored = _decode_z(_git_bytes(root, ["ls-files", "--others", "--ignored", "--exclude-standard", "-z"]))

    root_sources: dict[str, set[str]] = {}

    def add_root(oid: str, source: str) -> None:
        if not _OID_RE.fullmatch(oid):
            defects.append({"code": "git_root_oid_malformed", "detail": f"{source}:{oid}"})
            return
        root_sources.setdefault(oid, set()).add(source)

    for line in _git_text(root, ["for-each-ref", "--format=%(objectname)"]).splitlines():
        if line:
            add_root(line.strip(), "ref")
    for line in _git_text(root, ["stash", "list", "--format=%H"]).splitlines():
        if line:
            add_root(line.strip(), "stash")

    worktrees = _parse_worktrees(root, defects)
    worktree_summary: list[dict[str, str | bool | None]] = []
    outside_worktrees: list[str] = []
    for record in worktrees:
        raw_path = record["path"]
        head = record["head"]
        if head:
            add_root(head, f"worktree_head:{raw_path}")
        if not raw_path:
            continue
        try:
            worktree_path = Path(raw_path).resolve(strict=True)
        except OSError as exc:
            defects.append({"code": "git_worktree_unreadable", "detail": f"{raw_path}: {exc}"})
            continue
        try:
            index_output = _git_bytes(root, ["ls-files", "--stage", "-z"], cwd=worktree_path)
        except ReclaimError as exc:
            defects.append({"code": "git_worktree_index_unreadable", "detail": str(exc)})
            continue
        for oid in _parse_index_oids(index_output, str(worktree_path), defects):
            add_root(oid, f"index:{worktree_path}")
        outside_root = not _is_within(worktree_path, root)
        if outside_root:
            outside_worktrees.append(str(worktree_path))
        worktree_summary.append(
            {
                "path": worktree_path.relative_to(root).as_posix()
                if not outside_root and worktree_path != root
                else "."
                if worktree_path == root
                else str(worktree_path),
                "head": head,
                "branch": record["branch"],
                "outside_root": outside_root,
            }
        )

    if _is_within(common_dir, root):
        for oid in _reflog_oids(common_dir, defects):
            add_root(oid, "reflog")

    root_info = _batch_object_info(root, set(root_sources))
    valid_roots: set[str] = set()
    missing_index_roots: list[dict[str, str]] = []
    missing_reflog_roots: list[dict[str, str]] = []
    for oid, sources in sorted(root_sources.items()):
        if root_info.get(oid) is None:
            sorted_sources = sorted(sources)
            if all(source.startswith("index:") for source in sorted_sources):
                missing_index_roots.append({"oid": oid, "sources": ",".join(sorted_sources)})
            elif sorted_sources == ["reflog"]:
                missing_reflog_roots.append({"oid": oid, "sources": "reflog"})
            else:
                defects.append(
                    {
                        "code": "git_root_object_missing",
                        "detail": f"{oid}:{','.join(sorted_sources)}",
                    }
                )
        else:
            valid_roots.add(oid)

    reachable: set[str] = set()
    if valid_roots:
        payload = "".join(f"{oid}\n" for oid in sorted(valid_roots)).encode("ascii")
        output = _git_bytes(
            root,
            ["rev-list", "--objects", "--no-object-names", "--stdin"],
            input_bytes=payload,
        )
        for line in output.decode("ascii", errors="replace").splitlines():
            oid = line.split(maxsplit=1)[0]
            if _OID_RE.fullmatch(oid):
                reachable.add(oid)
            else:
                defects.append({"code": "git_reachability_record_malformed", "detail": line})
    reachable.update(valid_roots)

    head_result = _git_process(root, ["rev-parse", "--verify", "HEAD"])
    head = head_result.stdout.decode("ascii", errors="replace").strip() if head_result.returncode == 0 else None
    public = {
        "common_dir": common_dir.relative_to(root).as_posix() if _is_within(common_dir, root) else str(common_dir),
        "head": head,
        "tracked_count": len(tracked),
        "tracked_digest": _digest_strings(tracked),
        "root_count": len(valid_roots),
        "root_digest": _digest_strings(valid_roots),
        "reachable_count": len(reachable),
        "reachable_digest": _digest_strings(reachable),
        "worktrees": sorted(worktree_summary, key=lambda item: str(item["path"])),
        "outside_worktrees": sorted(outside_worktrees),
        "missing_index_roots": missing_index_roots,
        "missing_index_root_count": len(missing_index_roots),
        "missing_reflog_roots": missing_reflog_roots,
        "missing_reflog_root_count": len(missing_reflog_roots),
        "defects": sorted(defects, key=lambda item: (item["code"], item["detail"])),
        "complete": not defects,
    }
    return {
        "public": public,
        "common_dir": common_dir,
        "tracked": tracked,
        "untracked": untracked,
        "ignored": ignored,
        "reachable": reachable,
    }


def _registry_local_path(storage_path: str) -> str | None:
    normalized = storage_path.strip().replace("\\", "/")
    if not normalized or normalized.startswith(_EXTERNAL_STORAGE_SCHEMES):
        return None
    return normalized


def _has_glob(value: str) -> bool:
    return any(character in value for character in "*?[")


def _collect_registry(root: Path) -> dict[str, Any]:
    path = default_registry_path(root)
    defects: list[dict[str, str]] = []
    records: list[SoTArtifact] = []
    reality: dict[str, Any] = {
        "blocking": True,
        "findings": [],
        "summary": {},
    }
    parity: dict[str, Any] = {
        "checked": False,
        "in_sync": False,
        "projection_count": 0,
        "toml_count": 0,
    }
    try:
        snapshot = load_registry_snapshot(project_root=root)
        records = list(snapshot.records)
    except RegistryProjectionMismatch as exc:
        defects.append({"code": "registry_projection_out_of_sync", "detail": str(exc)})
    except (FileNotFoundError, RegistryControlPlaneError, OSError) as exc:
        defects.append({"code": "registry_load_failed", "detail": str(exc)})
    else:
        parity = {
            "checked": True,
            "in_sync": True,
            "projection_count": len(records),
            "toml_count": len(records),
        }
        unsafe_records = False
        for record in records:
            storage = _registry_local_path(record.storage_path)
            if storage is None:
                continue
            candidate = Path(storage)
            if candidate.is_absolute() or ".." in candidate.parts:
                unsafe_records = True
                defects.append(
                    {
                        "code": "registry_storage_path_unsafe",
                        "detail": f"{record.id}:{record.storage_path}",
                    }
                )
            elif ":" in storage:
                unsafe_records = True
                defects.append(
                    {
                        "code": "registry_storage_scheme_unsupported",
                        "detail": f"{record.id}:{record.storage_path}",
                    }
                )
        if not unsafe_records:
            try:
                refresh = build_refresh_report(root, registry_path=path)
            except InventoryScanError as exc:
                defects.append({"code": "registry_reality_check_failed", "detail": str(exc)})
            else:
                blocking_findings = [
                    finding for finding in refresh["registry_findings"] if finding["severity"] == "blocking"
                ]
                reality = {
                    "blocking": bool(refresh["blocking"]),
                    "findings": blocking_findings,
                    "summary": refresh["summary"],
                }
                defects.extend(
                    {
                        "code": f"registry_reality_{finding['code']}",
                        "detail": f"{finding['artifact_id']}:{finding['storage_path']}",
                    }
                    for finding in blocking_findings
                )

    serialized = [asdict(record) for record in sorted(records, key=lambda item: item.id)]
    public = {
        "path": path.relative_to(root).as_posix() if _is_within(path, root) else str(path),
        "loaded": not any(item["code"] == "registry_load_failed" for item in defects),
        "record_count": len(records),
        "records_digest": _stable_hash(serialized),
        "parity": parity,
        "reality": reality,
        "defects": sorted(defects, key=lambda item: (item["code"], item["detail"])),
        "reality_valid": not defects,
    }
    return {"public": public, "records": tuple(records)}


def _registry_matches(rel_path: str, records: tuple[SoTArtifact, ...]) -> list[str]:
    matches: list[str] = []
    for record in records:
        storage = _registry_local_path(record.storage_path)
        if storage is None or Path(storage).is_absolute() or ".." in Path(storage).parts:
            continue
        if storage.endswith("/"):
            matched = rel_path == storage.rstrip("/") or rel_path.startswith(storage)
        elif _has_glob(storage):
            matched = fnmatch.fnmatchcase(rel_path, storage)
        else:
            matched = rel_path == storage
        if matched:
            matches.append(record.id)
    return sorted(matches)


def _registry_preservation_ids(
    rel_path: str,
    records: tuple[SoTArtifact, ...],
    *,
    candidate_class: str | None = None,
) -> list[str]:
    matches: list[str] = []
    for record in records:
        storage = _registry_local_path(record.storage_path)
        if storage is None or Path(storage).is_absolute() or ".." in Path(storage).parts:
            continue
        if storage.endswith("/"):
            matched = rel_path == storage.rstrip("/") or rel_path.startswith(storage)
        elif _has_glob(storage):
            matched = fnmatch.fnmatchcase(rel_path, storage)
        else:
            matched = rel_path == storage
        if not matched:
            continue
        if (
            candidate_class in _DETRITUS_CLASSES
            and record.lifecycle == "generated"
            and record.backup_policy in {"gitignored_runtime", "regenerable_from_source"}
        ):
            continue
        matches.append(record.id)
    return sorted(matches)


def _state_relative(root: Path, state: Path) -> str:
    return state.relative_to(root).as_posix().rstrip("/") + "/"


def _is_protected(rel_path: str, state_prefix: str, candidate_class: str | None = None) -> bool:
    if rel_path in _PROTECTED_EXACT or rel_path.startswith(_PROTECTED_PREFIXES):
        return True
    if rel_path == state_prefix.rstrip("/") or rel_path.startswith(state_prefix):
        return candidate_class not in _DETRITUS_CLASSES
    return rel_path.startswith(".git/") and candidate_class not in {
        "unreachable_loose_object",
        "malformed_git_object_garbage",
    }


def _is_root_detritus_name(name: str) -> bool:
    return name in _ROOT_DETRITUS_EXACT or name.startswith(_ROOT_DETRITUS_PREFIXES)


def _is_state_detritus_name(name: str) -> bool:
    return (
        name in _STATE_DETRITUS_EXACT
        or name.startswith(_STATE_DETRITUS_PREFIXES)
        or name.endswith(_STATE_DETRITUS_SUFFIXES)
        or _STATE_WORK_ITEM_DETRITUS_RE.match(name) is not None
    )


def _direct_detritus_class(rel_path: str, _state_prefix: str) -> str | None:
    path = Path(rel_path)
    parts = path.parts
    if len(parts) == 1 and _is_root_detritus_name(parts[0]):
        return "stale_workspace_detritus"
    if len(parts) == 2 and parts[0] == ".gtkb-state" and _is_state_detritus_name(parts[1]):
        return "stale_runtime_detritus"
    return None


def classify_standing_delete(
    *,
    rel_path: str,
    observed_digest: str | None = None,
    generator: str | None = None,
    regenerated_digest: str | None = None,
    source_of_truth: str | None = None,
    sot_digest: str | None = None,
    registry_matches: list[str] | None = None,
    evidence_source: str | None = None,
) -> dict[str, Any]:
    """Classify one object for standing delete authorization.

    Implements the bounded relaxation in ``.harness-baseline-configuration/rules/
    prime-builder.md`` section "Standing Delete Authorization - DERIVED and CACHED
    Only" (WI-6743, Route B, ``DELIB-20260825183500``).

    Returns a disposition dict carrying the class and the evidence that
    established it. Dispositions:

    ``derived``
        A named generator exists AND regeneration reproduced the observed bytes.
        Standing delete authorized.
    ``cached``
        A named source of truth exists AND the object corresponds to it at
        digest level. Standing delete authorized.
    ``unregistered``
        Absent from the SoT registry. Routes to receipted quarantine; never a
        direct delete.
    ``owner_gated``
        Everything else, including every case where class cannot be established
        from evidence. The default.

    Precedence: ``derived`` and ``cached`` are evaluated before ``unregistered``
    because both require positive proof that the bytes are reproducible, which is
    strictly stronger evidence than registry absence. An object that is both
    registry-absent and demonstrably regenerable is ``derived``; registry absence
    alone never upgrades a disposition.

    The function performs no I/O and no deletion. It is a pure decision over
    supplied evidence, so the decision is reproducible and testable independently
    of the filesystem.
    """
    # WI-6743 F1, gate 1 of 2: protected artifact classes are denied on path
    # alone, before any evidence is weighed. No supplied digest, generator or
    # source-of-truth string can reach an authorized disposition from here.
    protected_class = _standing_delete_protected_class(rel_path)
    if protected_class is not None:
        return _standing_delete_disposition(
            rel_path,
            "owner_gated",
            "protected artifact class cannot satisfy the DERIVED or CACHED evidence conditions",
            protected_class=protected_class,
        )

    # WI-6743 F1, gate 2 of 2: evidence must be attributed to a governed
    # verifier. Caller-asserted strings are inputs, not proof, so an absent or
    # unrecognized issuer can never establish a regenerable class.
    evidence_trusted = evidence_source in _STANDING_DELETE_TRUSTED_EVIDENCE_SOURCES

    if (
        evidence_trusted
        and generator
        and regenerated_digest
        and observed_digest
        and regenerated_digest == observed_digest
    ):
        return _standing_delete_disposition(
            rel_path,
            "derived",
            "named generator reproduced the observed bytes under governed verification",
            generator=generator,
            observed_digest=observed_digest,
            regenerated_digest=regenerated_digest,
            evidence_source=evidence_source,
        )
    if evidence_trusted and source_of_truth and sot_digest and observed_digest and sot_digest == observed_digest:
        return _standing_delete_disposition(
            rel_path,
            "cached",
            "object corresponds to a named source of truth at digest level under governed verification",
            source_of_truth=source_of_truth,
            observed_digest=observed_digest,
            sot_digest=sot_digest,
            evidence_source=evidence_source,
        )
    if not evidence_trusted and (generator or source_of_truth):
        return _standing_delete_disposition(
            rel_path,
            "owner_gated",
            "regenerability evidence was not issued by a governed verifier",
            evidence_source=evidence_source,
            registry_matches=list(registry_matches or []),
        )
    if not registry_matches:
        return _standing_delete_disposition(
            rel_path,
            "unregistered",
            "absent from the SoT registry; routes to receipted quarantine",
        )
    return _standing_delete_disposition(
        rel_path,
        "owner_gated",
        "class could not be established from evidence",
        registry_matches=list(registry_matches),
    )


def _standing_delete_disposition(
    rel_path: str,
    disposition: str,
    reason: str,
    **evidence: Any,
) -> dict[str, Any]:
    return {
        "path": rel_path,
        "disposition": disposition,
        "standing_delete_authorized": disposition in _STANDING_DELETE_AUTHORIZED,
        "reason": reason,
        "evidence": dict(evidence),
    }


def standing_delete_audit_record(
    disposition: dict[str, Any],
    *,
    action: str,
    actor: str,
    performed_at: datetime,
) -> dict[str, Any]:
    """Build the mandatory post-hoc audit record for a standing-delete action.

    The governing rule makes this record mandatory: an action taken under the
    standing authorization without a record naming the object and the evidence
    for its class is a defect, not a permitted shortcut. The record therefore
    carries the evidence verbatim rather than only the resulting class.
    """
    return {
        "schema_version": _SCHEMA_VERSION,
        "record_kind": "standing_delete_action",
        "path": disposition["path"],
        "disposition": disposition["disposition"],
        "standing_delete_authorized": disposition["standing_delete_authorized"],
        "reason": disposition["reason"],
        "evidence": dict(disposition.get("evidence") or {}),
        "action": action,
        "actor": actor,
        "performed_at": _iso(_as_utc(performed_at)),
        "authority": "DELIB-20260825183500",
    }


def _scratch_class(rel_path: str) -> str | None:
    path = Path(rel_path)
    if any(part in _SCRATCH_COMPONENTS for part in path.parts):
        return "stale_harness_scratch"
    if path.name.startswith(_SCRATCH_NAME_PREFIXES):
        return "stale_draft_scratch"
    return None


def _path_is_covered_by_prefix(rel_path: str, prefixes: set[str]) -> bool:
    rel_dir = rel_path.rstrip("/") + "/"
    return any(rel_path == prefix.rstrip("/") or rel_dir.startswith(prefix) for prefix in prefixes)


def _prune_scratch_walk_path(rel_path: str, state_prefix: str, covered_prefixes: set[str]) -> bool:
    return _path_is_covered_by_prefix(rel_path, covered_prefixes) or _is_protected(rel_path, state_prefix)


def _stat_evidence(value: os.stat_result) -> dict[str, int]:
    return {
        "device": int(value.st_dev),
        "inode": int(value.st_ino),
        "mode": int(value.st_mode),
        "size": int(value.st_size),
        "mtime_ns": int(value.st_mtime_ns),
        "ctime_ns": int(value.st_ctime_ns),
    }


def _tree_fingerprint(path: Path) -> dict[str, Any]:
    root_stat = path.lstat()
    if path.is_symlink():
        raise ReclaimError(f"tree_root_symlink:{path}")
    if stat.S_ISREG(root_stat.st_mode):
        return {
            "kind": "file",
            "digest": _stable_hash({"path": "", "stat": _stat_evidence(root_stat)}),
            "logical_bytes": int(root_stat.st_size),
            "file_count": 1,
            "directory_count": 0,
        }
    if not stat.S_ISDIR(root_stat.st_mode):
        raise ReclaimError(f"tree_root_unsupported:{path}")

    digest = hashlib.sha256()
    logical_bytes = 0
    file_count = 0
    directory_count = 1

    def update(rel: str, entry_stat: os.stat_result, kind: str) -> None:
        digest.update(
            _canonical_bytes(
                {
                    "path": rel,
                    "kind": kind,
                    "stat": _stat_evidence(entry_stat),
                }
            )
        )

    update("", root_stat, "directory")
    for current, dir_names, file_names in os.walk(path, topdown=True, followlinks=False):
        current_path = Path(current)
        dir_names.sort()
        file_names.sort()
        for dir_name in list(dir_names):
            child = current_path / dir_name
            rel = child.relative_to(path).as_posix()
            try:
                child_stat = child.lstat()
            except OSError as exc:
                raise ReclaimError(f"tree_stat_failed:{child}:{exc}") from exc
            if child.is_symlink():
                update(rel, child_stat, "symlink")
                dir_names.remove(dir_name)
                continue
            if not stat.S_ISDIR(child_stat.st_mode):
                raise ReclaimError(f"tree_directory_entry_unsupported:{child}")
            directory_count += 1
            update(rel, child_stat, "directory")
        for file_name in file_names:
            child = current_path / file_name
            rel = child.relative_to(path).as_posix()
            try:
                child_stat = child.lstat()
            except OSError as exc:
                raise ReclaimError(f"tree_stat_failed:{child}:{exc}") from exc
            if child.is_symlink():
                update(rel, child_stat, "symlink")
                continue
            if not stat.S_ISREG(child_stat.st_mode):
                raise ReclaimError(f"tree_file_entry_unsupported:{child}")
            file_count += 1
            logical_bytes += int(child_stat.st_size)
            update(rel, child_stat, "file")
    return {
        "kind": "directory",
        "digest": "sha256:" + digest.hexdigest(),
        "logical_bytes": int(logical_bytes),
        "file_count": int(file_count),
        "directory_count": int(directory_count),
    }


def _shallow_directory_fingerprint(path: Path, file_stat: os.stat_result | None = None) -> dict[str, Any]:
    current_stat = file_stat or path.lstat()
    if path.is_symlink() or not stat.S_ISDIR(current_stat.st_mode):
        raise ReclaimError(f"directory_root_unsupported:{path}")
    return {
        "kind": "directory",
        "digest": _stable_hash({"kind": "directory", "stat": _stat_evidence(current_stat)}),
        "logical_bytes": int(current_stat.st_size),
        "file_count": 0,
        "directory_count": 1,
    }


def _age_hours(value: os.stat_result, now: datetime) -> float:
    return (now.timestamp() - value.st_mtime) / 3600


def _observation(path: str, classification: str, reason: str, **extra: Any) -> dict[str, Any]:
    result: dict[str, Any] = {"path": path, "classification": classification, "reason": reason}
    result.update(extra)
    return result


def _make_item(
    *,
    rel_path: str,
    candidate_class: str,
    source_kind: str,
    file_stat: os.stat_result,
    logical_bytes: int | None = None,
    tree_digest: str | None = None,
    file_count: int | None = None,
    directory_count: int | None = None,
    ignored: bool = False,
    git_oid: str | None = None,
    git_object_type: str | None = None,
) -> dict[str, Any]:
    identity = {
        "path": rel_path,
        "candidate_class": candidate_class,
        "source_kind": source_kind,
        "stat": _stat_evidence(file_stat),
        "tree_digest": tree_digest,
        "git_oid": git_oid,
        "git_object_type": git_object_type,
    }
    item_id = "item-" + hashlib.sha256(_canonical_bytes(identity)).hexdigest()[:24]
    item = {
        "item_id": item_id,
        **identity,
        "ignored": ignored,
        "logical_bytes": int(logical_bytes if logical_bytes is not None else file_stat.st_size),
        "file_count": file_count,
        "directory_count": directory_count,
    }
    item["item_hash"] = _stable_hash(item)
    return item


def _candidate_source(root: Path, rel_path: str) -> Path | None:
    if not _safe_relative_path(rel_path):
        return None
    source = root / rel_path
    try:
        resolved = source.resolve(strict=True)
    except OSError:
        return None
    if resolved != source.resolve(strict=False) or not _is_within(resolved, root):
        return None
    return source


def _collect_direct_detritus_candidates(
    root: Path,
    state: Path,
    registry: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], set[str]]:
    items: list[dict[str, Any]] = []
    observations: list[dict[str, Any]] = []
    covered_prefixes: set[str] = set()
    state_prefix = _state_relative(root, state)
    runtime_state = root / ".gtkb-state"
    scan_roots = [root]
    if runtime_state.is_dir():
        scan_roots.append(runtime_state)

    for scan_root in scan_roots:
        try:
            entries = sorted(scan_root.iterdir(), key=lambda entry: entry.name)
        except OSError as exc:
            rel_root = scan_root.relative_to(root).as_posix() if scan_root != root else "."
            observations.append(_observation(rel_root, "detritus_scan_failed", str(exc)))
            continue
        for entry in entries:
            try:
                rel_path = entry.relative_to(root).as_posix()
            except ValueError:
                continue
            candidate_class = _direct_detritus_class(rel_path, state_prefix)
            if candidate_class is None:
                continue
            source = _candidate_source(root, rel_path)
            if source is None:
                observations.append(_observation(rel_path, "ambiguous_detritus", "path_escape_or_unreadable"))
                continue
            try:
                file_stat = source.lstat()
            except OSError as exc:
                observations.append(_observation(rel_path, "ambiguous_detritus", f"stat_failed:{exc}"))
                continue
            if source.is_symlink() or not (stat.S_ISREG(file_stat.st_mode) or stat.S_ISDIR(file_stat.st_mode)):
                observations.append(_observation(rel_path, "ambiguous_detritus", "unsupported_file_type"))
                continue
            registry_ids = _registry_preservation_ids(
                rel_path,
                registry["records"],
                candidate_class=candidate_class,
            )
            if registry_ids:
                observations.append(
                    _observation(
                        rel_path,
                        "registered_veto",
                        "registry_match_preserves_path",
                        registry_ids=registry_ids,
                    )
                )
                continue
            if _is_protected(rel_path, state_prefix, candidate_class):
                observations.append(_observation(rel_path, "protected_veto", "protected path"))
                continue
            try:
                if stat.S_ISDIR(file_stat.st_mode):
                    fingerprint = _shallow_directory_fingerprint(source, file_stat)
                else:
                    fingerprint = _tree_fingerprint(source)
            except ReclaimError as exc:
                observations.append(_observation(rel_path, "ambiguous_detritus", str(exc)))
                continue
            source_kind = "worktree_directory" if fingerprint["kind"] == "directory" else "worktree_file"
            items.append(
                _make_item(
                    rel_path=rel_path,
                    candidate_class=candidate_class,
                    source_kind=source_kind,
                    file_stat=file_stat,
                    logical_bytes=int(fingerprint["logical_bytes"]),
                    tree_digest=str(fingerprint["digest"]),
                    file_count=int(fingerprint["file_count"]),
                    directory_count=int(fingerprint["directory_count"]),
                )
            )
            if source_kind in _DIRECTORY_SOURCE_KINDS:
                covered_prefixes.add(rel_path.rstrip("/") + "/")
    return items, observations, covered_prefixes


def _collect_scratch_candidates(
    root: Path,
    state: Path,
    git: dict[str, Any],
    registry: dict[str, Any],
    *,
    now: datetime,
    min_age_hours: int,
    covered_prefixes: set[str] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    items: list[dict[str, Any]] = []
    observations: list[dict[str, Any]] = []
    state_prefix = _state_relative(root, state)
    covered = covered_prefixes or set()
    for current, dir_names, file_names in os.walk(root, topdown=True, followlinks=False):
        current_path = Path(current)
        try:
            rel_current = current_path.relative_to(root).as_posix()
        except ValueError:
            dir_names[:] = []
            continue
        rel_current = "" if rel_current == "." else rel_current
        dir_names.sort()
        file_names.sort()

        for dir_name in list(dir_names):
            child = current_path / dir_name
            rel_path = child.relative_to(root).as_posix()
            if _prune_scratch_walk_path(rel_path, state_prefix, covered):
                dir_names.remove(dir_name)
                continue

        if rel_current and _prune_scratch_walk_path(rel_current, state_prefix, covered):
            dir_names[:] = []
            continue

        for file_name in file_names:
            source = current_path / file_name
            rel_path = source.relative_to(root).as_posix()
            candidate_class = _scratch_class(rel_path)
            if candidate_class is None or _prune_scratch_walk_path(rel_path, state_prefix, covered):
                continue
            try:
                file_stat = source.lstat()
            except OSError as exc:
                observations.append(_observation(rel_path, "ambiguous_scratch", f"stat_failed:{exc}"))
                continue
            if source.is_symlink() or not stat.S_ISREG(file_stat.st_mode):
                observations.append(_observation(rel_path, "ambiguous_scratch", "unsupported_file_type"))
                continue
            registry_ids = _registry_preservation_ids(
                rel_path,
                registry["records"],
                candidate_class=candidate_class,
            )
            if registry_ids:
                observations.append(
                    _observation(
                        rel_path,
                        "registered_veto",
                        "registry_match_preserves_path",
                        registry_ids=registry_ids,
                    )
                )
                continue
            if _is_protected(rel_path, state_prefix, candidate_class):
                observations.append(_observation(rel_path, "protected_veto", "protected path"))
                continue
            if _age_hours(file_stat, now) < min_age_hours:
                observations.append(_observation(rel_path, "age_veto", "candidate is too recent"))
                continue
            items.append(
                _make_item(
                    rel_path=rel_path,
                    candidate_class=candidate_class,
                    source_kind="worktree_file",
                    file_stat=file_stat,
                    ignored=rel_path in git["ignored"],
                )
            )
    return items, observations


def _collect_loose_object_candidates(
    root: Path,
    state: Path,
    git: dict[str, Any],
    *,
    now: datetime,
    min_age_hours: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    items: list[dict[str, Any]] = []
    observations: list[dict[str, Any]] = []
    common_dir: Path = git["common_dir"]
    if not _is_within(common_dir, root):
        return items, observations
    objects_dir = common_dir / "objects"
    if not objects_dir.is_dir():
        return items, observations

    valid_names: dict[str, tuple[Path, os.stat_result]] = {}
    state_prefix = _state_relative(root, state)
    for fanout in sorted(objects_dir.iterdir(), key=lambda path: path.name):
        if not fanout.is_dir() or fanout.is_symlink() or not _HEX_FANOUT_RE.fullmatch(fanout.name):
            continue
        for artifact in sorted(fanout.iterdir(), key=lambda path: path.name):
            rel_path = artifact.relative_to(root).as_posix()
            try:
                file_stat = artifact.lstat()
            except OSError as exc:
                observations.append(_observation(rel_path, "ambiguous_git_object", f"stat_failed:{exc}"))
                continue
            if artifact.is_symlink() or not stat.S_ISREG(file_stat.st_mode):
                observations.append(_observation(rel_path, "ambiguous_git_object", "unsupported_file_type"))
                continue
            if _GIT_TMP_OBJECT_RE.fullmatch(artifact.name):
                if _is_protected(rel_path, state_prefix, "malformed_git_object_garbage"):
                    observations.append(_observation(rel_path, "protected_veto", "protected path"))
                    continue
                items.append(
                    _make_item(
                        rel_path=rel_path,
                        candidate_class="malformed_git_object_garbage",
                        source_kind="git_garbage_file",
                        file_stat=file_stat,
                    )
                )
                continue
            if not _LOOSE_NAME_RE.fullmatch(artifact.name):
                observations.append(
                    _observation(
                        rel_path,
                        "malformed_loose_object",
                        "non-canonical object artifact is preserved",
                    )
                )
                continue
            valid_names[fanout.name + artifact.name] = (artifact, file_stat)

    object_info = _batch_object_info(root, set(valid_names))
    for oid, (artifact, file_stat) in sorted(valid_names.items()):
        rel_path = artifact.relative_to(root).as_posix()
        info = object_info.get(oid)
        if info is None:
            observations.append(_observation(rel_path, "ambiguous_invalid_loose_object", "cat-file validation failed"))
            continue
        if oid in git["reachable"]:
            continue
        if _is_protected(rel_path, state_prefix, "unreachable_loose_object"):
            observations.append(_observation(rel_path, "protected_veto", "protected path"))
            continue
        if _age_hours(file_stat, now) < min_age_hours:
            observations.append(_observation(rel_path, "age_veto", "candidate is too recent"))
            continue
        items.append(
            _make_item(
                rel_path=rel_path,
                candidate_class="unreachable_loose_object",
                source_kind="git_loose_object",
                file_stat=file_stat,
                git_oid=oid,
                git_object_type=info[0],
            )
        )
    return items, observations


def _plan_material(manifest: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": manifest["schema_version"],
        "root_identity": manifest["root_identity"],
        "observed_at": manifest["observed_at"],
        "min_age_hours": manifest["min_age_hours"],
        "registry": manifest["registry"],
        "git": manifest["git"],
        "blockers": manifest["blockers"],
        "executable": manifest["executable"],
        "items": manifest["items"],
        "preserved": manifest["preserved"],
    }


def _manifest_hash(manifest: dict[str, Any]) -> str:
    return _stable_hash({key: value for key, value in manifest.items() if key != "manifest_hash"})


def _event_hash(event: dict[str, Any]) -> str:
    return _stable_hash({key: value for key, value in event.items() if key != "event_hash"})


def _new_event(
    sequence: int,
    prev_hash: str,
    *,
    timestamp: str,
    action: str,
    item_id: str | None,
    details: dict[str, Any],
) -> dict[str, Any]:
    event = {
        "schema_version": _SCHEMA_VERSION,
        "sequence": sequence,
        "timestamp": timestamp,
        "action": action,
        "item_id": item_id,
        "details": details,
        "prev_hash": prev_hash,
    }
    event["event_hash"] = _event_hash(event)
    return event


def _write_json(path: Path, value: Any) -> None:
    payload = json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True) + "\n"
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())


def _write_events(path: Path, events: list[dict[str, Any]]) -> None:
    with path.open("xb") as handle:
        for event in events:
            handle.write(_canonical_bytes(event) + b"\n")
        handle.flush()
        os.fsync(handle.fileno())


def _run_dir(state: Path, run_id: str) -> Path:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", run_id):
        raise ReclaimError("run_id contains unsupported characters")
    path = (state / "runs" / run_id).resolve(strict=False)
    if not _is_within(path, state):
        raise ReclaimError("run_id escapes state_root")
    return path


def _compact_plan(manifest: dict[str, Any], run_dir: Path) -> dict[str, Any]:
    class_counts: dict[str, int] = {}
    class_bytes: dict[str, int] = {}
    for item in manifest["items"]:
        candidate_class = str(item["candidate_class"])
        class_counts[candidate_class] = class_counts.get(candidate_class, 0) + 1
        class_bytes[candidate_class] = class_bytes.get(candidate_class, 0) + int(item["logical_bytes"])
    preview = sorted(
        manifest["items"],
        key=lambda item: (-int(item["logical_bytes"]), str(item["path"]), str(item["item_id"])),
    )[:10]
    return {
        "run_id": manifest["run_id"],
        "plan_hash": manifest["plan_hash"],
        "executable": manifest["executable"],
        "candidate_count": len(manifest["items"]),
        "logical_bytes": sum(int(item["logical_bytes"]) for item in manifest["items"]),
        "blockers": [item["code"] for item in manifest["blockers"]],
        "registry_ready": not manifest["registry"]["defects"],
        "git_ready": not manifest["git"]["defects"],
        "candidate_classes": {
            key: {"count": class_counts[key], "logical_bytes": class_bytes[key]} for key in sorted(class_counts)
        },
        "item_preview": [
            {
                "item_id": item["item_id"],
                "path": item["path"],
                "candidate_class": item["candidate_class"],
                "logical_bytes": item["logical_bytes"],
            }
            for item in preview
        ],
        "items_omitted": max(0, len(manifest["items"]) - len(preview)),
        "manifest_path": str(run_dir / "manifest.json"),
        "summary_path": str(run_dir / "summary.json"),
        "events_path": str(run_dir / "events.jsonl"),
    }


def plan_reclaim(
    root: Path,
    *,
    state_root: Path | None = None,
    min_age_hours: int = 168,
    now: datetime | None = None,
    actor: str | None = None,
    session_id: str | None = None,
) -> dict[str, Any]:
    """Plan conservative reclaim candidates and persist an immutable run ledger."""
    if isinstance(min_age_hours, bool) or min_age_hours <= 0:
        raise ReclaimError("min_age_hours must be a positive integer")
    root = _root_path(Path(root))
    state = _state_path(root, state_root)
    observed_at = _as_utc(now)
    git = _collect_git_evidence(root)
    registry = _collect_registry(root)

    detritus_items, detritus_observations, covered_prefixes = _collect_direct_detritus_candidates(
        root,
        state,
        registry,
    )
    scratch_items, scratch_observations = _collect_scratch_candidates(
        root,
        state,
        git,
        registry,
        now=observed_at,
        min_age_hours=min_age_hours,
        covered_prefixes=covered_prefixes,
    )
    object_items, object_observations = _collect_loose_object_candidates(
        root,
        state,
        git,
        now=observed_at,
        min_age_hours=min_age_hours,
    )
    items = sorted([*detritus_items, *scratch_items, *object_items], key=lambda item: (item["path"], item["item_id"]))
    observations = sorted(
        [*detritus_observations, *scratch_observations, *object_observations],
        key=lambda item: (item["path"], item["classification"]),
    )
    blockers = [
        *(
            {"code": item["code"], "detail": item["detail"], "source": "registry"}
            for item in registry["public"]["defects"]
        ),
        *({"code": item["code"], "detail": item["detail"], "source": "git"} for item in git["public"]["defects"]),
    ]
    blockers = sorted(blockers, key=lambda item: (item["source"], item["code"], item["detail"]))
    root_stat = root.stat()
    manifest: dict[str, Any] = {
        "schema_version": _SCHEMA_VERSION,
        "run_id": "",
        "root": str(root),
        "state_root": str(state),
        "root_identity": {
            "resolved_path": str(root),
            "device": int(root_stat.st_dev),
            "inode": int(root_stat.st_ino),
        },
        "observed_at": _iso(observed_at),
        "min_age_hours": int(min_age_hours),
        "actor": actor,
        "session_id": session_id,
        "registry": registry["public"],
        "git": git["public"],
        "blockers": blockers,
        "executable": not blockers,
        "items": items,
        "preserved": observations,
    }
    manifest["plan_hash"] = _stable_hash(_plan_material(manifest))
    run_stamp = observed_at.strftime("%Y%m%dT%H%M%S%fZ")
    manifest["run_id"] = f"{run_stamp}-{manifest['plan_hash'].split(':', 1)[1][:12]}"
    manifest["manifest_hash"] = _manifest_hash(manifest)

    run_dir = _run_dir(state, manifest["run_id"])
    if run_dir.exists():
        existing = _load_manifest(run_dir)
        if existing.get("manifest_hash") != manifest["manifest_hash"]:
            raise ReclaimError(f"deterministic run collision at {run_dir}")
        existing_history = _history_one(run_dir)
        if not existing_history["integrity"]["valid"]:
            raise ReclaimError(f"existing deterministic run is corrupt or partial: {run_dir}")
        return _compact_plan(existing, run_dir)

    state.mkdir(parents=True, exist_ok=True)
    (state / "runs").mkdir(exist_ok=True)
    run_dir.mkdir()
    _write_json(run_dir / "manifest.json", manifest)
    summary = {
        "schema_version": _SCHEMA_VERSION,
        "run_id": manifest["run_id"],
        "plan_hash": manifest["plan_hash"],
        "executable": manifest["executable"],
        "candidate_count": len(items),
        "logical_bytes": sum(int(item["logical_bytes"]) for item in items),
        "blocker_count": len(blockers),
        "preserved_count": len(observations),
        "physical_bytes_reclaimed": 0,
    }
    summary["summary_hash"] = _stable_hash(summary)
    _write_json(run_dir / "summary.json", summary)

    timestamp = manifest["observed_at"]
    events: list[dict[str, Any]] = []
    previous = _GENESIS_HASH
    created = _new_event(
        1,
        previous,
        timestamp=timestamp,
        action="plan_created",
        item_id=None,
        details={"plan_hash": manifest["plan_hash"], "executable": manifest["executable"]},
    )
    events.append(created)
    previous = created["event_hash"]
    for item in items:
        event = _new_event(
            len(events) + 1,
            previous,
            timestamp=timestamp,
            action="planned",
            item_id=item["item_id"],
            details={"item_hash": item["item_hash"], "path": item["path"]},
        )
        events.append(event)
        previous = event["event_hash"]
    _write_events(run_dir / "events.jsonl", events)
    return _compact_plan(manifest, run_dir)


def _load_manifest(run_dir: Path) -> dict[str, Any]:
    manifest_path = run_dir / "manifest.json"
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise ReclaimError("manifest is missing or is not a regular file")
    try:
        value = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ReclaimError(f"manifest cannot be read: {exc}") from exc
    if not isinstance(value, dict):
        raise ReclaimError("manifest is not a JSON object")
    return value


def _validate_manifest(manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {
        "schema_version",
        "run_id",
        "root",
        "state_root",
        "root_identity",
        "observed_at",
        "min_age_hours",
        "registry",
        "git",
        "blockers",
        "executable",
        "items",
        "preserved",
        "plan_hash",
        "manifest_hash",
    }
    missing = sorted(required - set(manifest))
    if missing:
        return [f"manifest_missing_fields:{','.join(missing)}"]
    try:
        if manifest["schema_version"] != _SCHEMA_VERSION:
            errors.append("manifest_schema_unsupported")
        if manifest["plan_hash"] != _stable_hash(_plan_material(manifest)):
            errors.append("plan_hash_mismatch")
        if manifest["manifest_hash"] != _manifest_hash(manifest):
            errors.append("manifest_hash_mismatch")
        item_ids = [item["item_id"] for item in manifest["items"]]
        if len(item_ids) != len(set(item_ids)):
            errors.append("manifest_duplicate_item_id")
        for item in manifest["items"]:
            if item["item_hash"] != _stable_hash({key: value for key, value in item.items() if key != "item_hash"}):
                errors.append(f"item_hash_mismatch:{item.get('item_id', '<missing>')}")
    except (KeyError, TypeError, ValueError):
        errors.append("manifest_structure_invalid")
    return errors


def _validate_summary(run_dir: Path, manifest: dict[str, Any]) -> list[str]:
    path = run_dir / "summary.json"
    if path.is_symlink() or not path.is_file():
        return ["summary_missing_or_unsupported"]
    try:
        summary = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"summary_unreadable:{exc}"]
    if not isinstance(summary, dict):
        return ["summary_not_object"]
    errors: list[str] = []
    expected = {
        "schema_version": _SCHEMA_VERSION,
        "run_id": manifest.get("run_id"),
        "plan_hash": manifest.get("plan_hash"),
        "executable": manifest.get("executable"),
        "candidate_count": len(manifest.get("items", [])),
        "logical_bytes": sum(int(item.get("logical_bytes", 0)) for item in manifest.get("items", [])),
        "blocker_count": len(manifest.get("blockers", [])),
        "preserved_count": len(manifest.get("preserved", [])),
        "physical_bytes_reclaimed": 0,
    }
    for key, value in expected.items():
        if summary.get(key) != value:
            errors.append(f"summary_field_mismatch:{key}")
    material = {key: value for key, value in summary.items() if key != "summary_hash"}
    if summary.get("summary_hash") != _stable_hash(material):
        errors.append("summary_hash_mismatch")
    return errors


def _load_and_validate_events(
    run_dir: Path,
    manifest: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[str], bool]:
    errors: list[str] = []
    partial = False
    path = run_dir / "events.jsonl"
    if path.is_symlink() or not path.is_file():
        return [], ["events_missing_or_unsupported"], True
    try:
        payload = path.read_bytes()
    except OSError as exc:
        return [], [f"events_unreadable:{exc}"], True
    if payload and not payload.endswith(b"\n"):
        errors.append("events_truncated_final_line")
        partial = True
    events: list[dict[str, Any]] = []
    previous = _GENESIS_HASH
    for expected_sequence, raw_line in enumerate(payload.splitlines(), start=1):
        try:
            event = json.loads(raw_line)
        except json.JSONDecodeError:
            errors.append(f"event_json_invalid:{expected_sequence}")
            partial = True
            continue
        if not isinstance(event, dict):
            errors.append(f"event_not_object:{expected_sequence}")
            continue
        if event.get("sequence") != expected_sequence:
            errors.append(f"event_sequence_gap:{expected_sequence}")
        if event.get("prev_hash") != previous:
            errors.append(f"event_prev_hash_mismatch:{expected_sequence}")
        if event.get("event_hash") != _event_hash(event):
            errors.append(f"event_hash_mismatch:{expected_sequence}")
        if event.get("action") not in _ALLOWED_EVENTS:
            errors.append(f"event_action_unsupported:{expected_sequence}")
        previous = str(event.get("event_hash", ""))
        events.append(event)

    item_ids = {item["item_id"] for item in manifest.get("items", []) if isinstance(item, dict) and "item_id" in item}
    planned_ids = [event.get("item_id") for event in events if event.get("action") == "planned"]
    if not events or events[0].get("action") != "plan_created":
        errors.append("plan_created_event_missing")
        partial = True
    if set(planned_ids) != item_ids or len(planned_ids) != len(item_ids):
        errors.append("planned_event_set_mismatch")
        partial = True
    for event in events:
        item_id = event.get("item_id")
        if item_id is not None and item_id not in item_ids:
            errors.append(f"event_unknown_item:{event.get('sequence')}")
    return events, errors, partial


def _reconstruct_states(
    manifest: dict[str, Any], events: list[dict[str, Any]]
) -> tuple[dict[str, dict[str, Any]], list[str], bool]:
    states = {
        item["item_id"]: {
            "item_id": item["item_id"],
            "path": item["path"],
            "candidate_class": item["candidate_class"],
            "payload_state": "planned",
            "status": "planned",
            "pending": None,
            "receipt": None,
            "last_refusal": None,
        }
        for item in manifest.get("items", [])
    }
    errors: list[str] = []
    for event in events:
        item_id = event.get("item_id")
        if item_id not in states:
            continue
        state = states[item_id]
        action = event.get("action")
        if action == "planned":
            continue
        if action == "trash_started":
            if state["payload_state"] not in {"planned", "restored"} or state["pending"] is not None:
                errors.append(f"invalid_trash_transition:{event.get('sequence')}")
            state["pending"] = "trash"
            state["status"] = "partial"
        elif action == "trashed":
            if state["pending"] != "trash":
                errors.append(f"trash_receipt_without_start:{event.get('sequence')}")
            state["payload_state"] = "trashed"
            state["status"] = "trashed"
            state["pending"] = None
            state["receipt"] = event.get("details")
            state["last_refusal"] = None
        elif action == "purge_started":
            if state["payload_state"] != "trashed" or state["pending"] is not None:
                errors.append(f"invalid_purge_transition:{event.get('sequence')}")
            state["pending"] = "purge"
            state["status"] = "partial"
        elif action == "purged":
            if state["pending"] != "purge":
                errors.append(f"purge_receipt_without_start:{event.get('sequence')}")
            state["payload_state"] = "purged"
            state["status"] = "purged"
            state["pending"] = None
            state["receipt"] = event.get("details")
            state["last_refusal"] = None
        elif action == "restore_started":
            if state["payload_state"] != "trashed" or state["pending"] is not None:
                errors.append(f"invalid_restore_transition:{event.get('sequence')}")
            state["pending"] = "restore"
            state["status"] = "partial"
        elif action == "restored":
            if state["pending"] != "restore":
                errors.append(f"restore_receipt_without_start:{event.get('sequence')}")
            state["payload_state"] = "restored"
            state["status"] = "restored"
            state["pending"] = None
            state["receipt"] = event.get("details")
            state["last_refusal"] = None
        elif action == "refused":
            state["status"] = "refused"
            state["pending"] = None
            state["last_refusal"] = event.get("details")
    partial = any(state["pending"] is not None for state in states.values())
    return states, errors, partial


def _history_one(run_dir: Path, *, item_id: str | None = None) -> dict[str, Any]:
    try:
        manifest = _load_manifest(run_dir)
    except ReclaimError as exc:
        return {
            "run_id": run_dir.name,
            "status": "corrupt",
            "integrity": {"valid": False, "partial": True, "errors": [str(exc)]},
            "items": [],
            "counts": {},
        }
    manifest_errors = _validate_manifest(manifest)
    summary_errors = _validate_summary(run_dir, manifest)
    events, event_errors, event_partial = _load_and_validate_events(run_dir, manifest)
    states, transition_errors, state_partial = _reconstruct_states(manifest, events)
    if item_id is not None and item_id not in states:
        raise ReclaimError(f"item_id is not present in run {manifest.get('run_id', run_dir.name)}: {item_id}")
    all_states = [states[key] for key in sorted(states)]
    selected = [states[item_id]] if item_id is not None else []
    errors = [*manifest_errors, *summary_errors, *event_errors, *transition_errors]
    partial = event_partial or state_partial
    run_refusals = [
        event.get("details") for event in events if event.get("action") == "refused" and event.get("item_id") is None
    ]
    counts: dict[str, int] = {}
    for state in all_states:
        counts[state["status"]] = counts.get(state["status"], 0) + 1
    if errors:
        status = "corrupt"
    elif partial:
        status = "partial"
    elif counts.get("refused") or run_refusals:
        status = "refused"
    elif len(counts) == 1:
        status = next(iter(counts), "planned")
    elif counts:
        status = "mixed"
    else:
        status = "planned"
    return {
        "run_id": manifest.get("run_id", run_dir.name),
        "plan_hash": manifest.get("plan_hash"),
        "executable": bool(manifest.get("executable", False)),
        "status": status,
        "integrity": {"valid": not errors and not partial, "partial": partial, "errors": errors},
        "counts": dict(sorted(counts.items())),
        "items": selected,
        "item_count": len(all_states),
        "items_omitted": len(all_states) if item_id is None else max(0, len(all_states) - 1),
        "run_refusals": run_refusals,
    }


def history_reclaim(
    root: Path,
    *,
    run_id: str | None = None,
    item_id: str | None = None,
    state_root: Path | None = None,
) -> dict[str, Any]:
    """Validate immutable manifests and reconstruct state from event chains."""
    root = _root_path(Path(root))
    state = _state_path(root, state_root)
    if item_id is not None and run_id is None:
        raise ReclaimError("item_id requires run_id")
    if run_id is not None:
        run_dir = _run_dir(state, run_id)
        if not run_dir.is_dir():
            raise ReclaimError(f"reclaim run does not exist: {run_id}")
        return _history_one(run_dir, item_id=item_id)
    runs_dir = state / "runs"
    if not runs_dir.is_dir():
        return {"count": 0, "runs": []}
    runs = [
        _history_one(path)
        for path in sorted(runs_dir.iterdir(), key=lambda candidate: candidate.name, reverse=True)
        if path.is_dir() and not path.is_symlink()
    ]
    return {"count": len(runs), "runs": runs}


def _validated_run(root: Path, state: Path, run_id: str) -> tuple[Path, dict[str, Any], list[dict[str, Any]]]:
    run_dir = _run_dir(state, run_id)
    if not run_dir.is_dir() or run_dir.is_symlink():
        raise ReclaimError(f"reclaim run does not exist or is unsupported: {run_id}")
    manifest = _load_manifest(run_dir)
    errors = _validate_manifest(manifest)
    errors.extend(_validate_summary(run_dir, manifest))
    events, event_errors, partial = _load_and_validate_events(run_dir, manifest)
    _states, transition_errors, state_partial = _reconstruct_states(manifest, events)
    errors.extend(event_errors)
    errors.extend(transition_errors)
    if partial or state_partial:
        errors.append("event_history_partial")
    if errors:
        raise ReclaimError("run integrity validation failed: " + "; ".join(errors))
    if manifest["run_id"] != run_id:
        raise ReclaimError("run_id does not match immutable manifest")
    if Path(manifest["root"]).resolve(strict=False) != root:
        raise ReclaimError("run root does not match requested repository root")
    if Path(manifest["state_root"]).resolve(strict=False) != state:
        raise ReclaimError("run state_root does not match requested state_root")
    root_stat = root.stat()
    identity = manifest["root_identity"]
    if (
        identity.get("resolved_path") != str(root)
        or identity.get("device") != int(root_stat.st_dev)
        or identity.get("inode") != int(root_stat.st_ino)
    ):
        raise ReclaimError("repository root identity changed")
    return run_dir, manifest, events


def _append_event(
    run_dir: Path,
    events: list[dict[str, Any]],
    *,
    action: str,
    item_id: str | None,
    details: dict[str, Any],
) -> dict[str, Any]:
    if action not in _ALLOWED_EVENTS:
        raise ReclaimError(f"unsupported event action: {action}")
    previous = events[-1]["event_hash"] if events else _GENESIS_HASH
    event = _new_event(
        len(events) + 1,
        previous,
        timestamp=_iso(datetime.now(UTC)),
        action=action,
        item_id=item_id,
        details=details,
    )
    with (run_dir / "events.jsonl").open("ab") as handle:
        handle.write(_canonical_bytes(event) + b"\n")
        handle.flush()
        os.fsync(handle.fileno())
    events.append(event)
    return event


def _normalize_nonempty(values: tuple[str, ...] | list[str], label: str) -> list[str]:
    if isinstance(values, (str, bytes)):
        raise ReclaimError(f"{label} must be a tuple or list of non-empty strings")
    normalized = [str(value).strip() for value in values]
    if not normalized or any(not value for value in normalized):
        raise ReclaimError(f"{label} must contain at least one non-empty exact reference")
    return normalized


def _normalize_item_ids(values: tuple[str, ...] | list[str]) -> list[str]:
    normalized = _normalize_nonempty(values, "item_ids")
    if len(normalized) != len(set(normalized)):
        raise ReclaimError("item_ids must be unique")
    return normalized


@contextmanager
def _operation_lock(run_dir: Path, operation: str) -> Iterator[None]:
    if not run_dir.is_dir() or run_dir.is_symlink():
        raise ReclaimError(f"reclaim run does not exist or is unsupported: {run_dir.name}")
    lock_path = run_dir / "operation.lock"
    try:
        descriptor = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise ReclaimError(f"operation_in_progress: {run_dir.name}") from exc
    except OSError as exc:
        raise ReclaimError(f"operation_lock_failed: {exc}") from exc
    try:
        payload = (
            _canonical_bytes(
                {
                    "operation": operation,
                    "pid": os.getpid(),
                    "started_at": _iso(datetime.now(UTC)),
                }
            )
            + b"\n"
        )
        os.write(descriptor, payload)
        os.fsync(descriptor)
        yield
    finally:
        os.close(descriptor)
        with suppress(FileNotFoundError):
            lock_path.unlink()


def _prepare_payload_paths(run_dir: Path, state: Path, item_ids: list[str]) -> dict[str, Path]:
    trash_root = run_dir / "trash"
    try:
        if trash_root.exists() or trash_root.is_symlink():
            if trash_root.is_symlink() or not trash_root.is_dir():
                raise ReclaimError(f"trash_root_unsupported:{trash_root}")
        else:
            trash_root.mkdir()
        resolved_trash = trash_root.resolve(strict=True)
        if not _is_within(resolved_trash, run_dir) or _has_symlink_parent(run_dir, trash_root):
            raise ReclaimError(f"trash_root_escape:{trash_root}")
        if int(resolved_trash.stat().st_dev) != int(state.stat().st_dev):
            raise ReclaimError(f"trash_root_cross_device:{trash_root}")

        payloads: dict[str, Path] = {}
        for item_id in item_ids:
            item_dir = trash_root / item_id
            if item_dir.exists() or item_dir.is_symlink():
                if item_dir.is_symlink() or not item_dir.is_dir():
                    raise ReclaimError(f"trash_collision:{item_dir}")
                contents = list(item_dir.iterdir())
                if contents:
                    if len(contents) != 1 or contents[0].name != "payload":
                        raise ReclaimError(f"trash_collision:{item_dir}")
                    if contents[0].is_symlink() or not (contents[0].is_file() or contents[0].is_dir()):
                        raise ReclaimError(f"trash_collision:{contents[0]}")
            else:
                item_dir.mkdir()
            resolved_item_dir = item_dir.resolve(strict=True)
            if not _is_within(resolved_item_dir, run_dir) or _has_symlink_parent(run_dir, item_dir):
                raise ReclaimError(f"trash_item_escape:{item_dir}")
            if int(resolved_item_dir.stat().st_dev) != int(state.stat().st_dev):
                raise ReclaimError(f"trash_item_cross_device:{item_dir}")
            payloads[item_id] = item_dir / "payload"
        return payloads
    except (OSError, ReclaimError) as exc:
        raise ReclaimError(f"trash_destination_failed:{exc}") from exc


def _append_refusal(
    run_dir: Path,
    events: list[dict[str, Any]],
    item_ids: list[str],
    *,
    code: str,
    detail: str,
) -> None:
    targets: list[str | None] = item_ids or [None]
    for item_id in targets:
        _append_event(
            run_dir,
            events,
            action="refused",
            item_id=item_id,
            details={"operation": "reclaim", "code": code, "detail": detail},
        )


def _refuse(
    run_dir: Path,
    events: list[dict[str, Any]],
    item_ids: list[str],
    *,
    code: str,
    detail: str,
) -> None:
    _append_refusal(run_dir, events, item_ids, code=code, detail=detail)
    raise ReclaimError(f"{code}: {detail}")


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as exc:
        raise ReclaimError(f"payload cannot be hashed: {path}: {exc}") from exc
    return "sha256:" + digest.hexdigest()


def _payload_fingerprint(path: Path, item: dict[str, Any]) -> str:
    if item.get("source_kind") in _DIRECTORY_SOURCE_KINDS:
        return str(_shallow_directory_fingerprint(path)["digest"])
    return _file_sha256(path)


def _add_write_permission(path: Path) -> int:
    """Make a regular file unlinkable on Windows and return its prior permission bits."""
    current = path.lstat()
    if path.is_symlink() or not stat.S_ISREG(current.st_mode):
        raise ReclaimError(f"unlink_target_unsupported:{path}")
    previous_mode = stat.S_IMODE(current.st_mode)
    os.chmod(path, previous_mode | stat.S_IWRITE)
    return previous_mode


def _restore_permission_bits(path: Path, mode: int) -> None:
    with suppress(OSError):
        os.chmod(path, stat.S_IMODE(mode))


def _unlink_regular_with_write_retry(path: Path) -> None:
    try:
        path.unlink()
        return
    except PermissionError:
        _add_write_permission(path)
        path.unlink()


def _repair_windows_directory_acl(path: Path) -> None:
    if os.name != "nt":
        return
    username = os.environ.get("USERNAME")
    if not username:
        return
    grant = f"{username}:(OI)(CI)F"
    subprocess.run(["takeown", "/F", str(path), "/R", "/D", "Y"], capture_output=True, text=True, check=False)
    subprocess.run(["icacls", str(path), "/reset", "/T", "/C"], capture_output=True, text=True, check=False)
    subprocess.run(["icacls", str(path), "/grant", grant, "/T", "/C"], capture_output=True, text=True, check=False)


def _rmtree_bottom_up_once(path: Path) -> None:
    for current, dir_names, file_names in os.walk(path, topdown=False, followlinks=False):
        current_path = Path(current)
        for file_name in file_names:
            child = current_path / file_name
            if not child.exists() and not child.is_symlink():
                continue
            with suppress(OSError):
                os.chmod(child, stat.S_IWRITE | stat.S_IREAD)
            with suppress(FileNotFoundError):
                _unlink_regular_with_write_retry(child)
        for dir_name in dir_names:
            child = current_path / dir_name
            if not child.exists() and not child.is_symlink():
                continue
            with suppress(OSError):
                os.chmod(child, stat.S_IWRITE | stat.S_IREAD | stat.S_IEXEC)
            try:
                if child.is_symlink():
                    child.unlink()
                else:
                    child.rmdir()
            except PermissionError:
                os.chmod(child, stat.S_IWRITE | stat.S_IREAD | stat.S_IEXEC)
                child.rmdir()
            except FileNotFoundError:
                pass
    with suppress(OSError):
        os.chmod(path, stat.S_IWRITE | stat.S_IREAD | stat.S_IEXEC)
    with suppress(FileNotFoundError):
        path.rmdir()


def _rmtree_with_write_retry(path: Path) -> None:
    last_error: OSError | None = None
    for _attempt in range(3):
        try:
            _rmtree_bottom_up_once(path)
            return
        except OSError as exc:
            last_error = exc
    escaped = str(path).replace("'", "''")
    script = f"Remove-Item -LiteralPath '{escaped}' -Recurse -Force -ErrorAction Stop"
    for executable in ("pwsh", "powershell"):
        try:
            result = subprocess.run(
                [executable, "-NoProfile", "-Command", script],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
        except FileNotFoundError:
            continue
        if result.returncode == 0 or not path.exists():
            return
        last_error = OSError(result.stderr.strip() or result.stdout.strip() or f"{executable} Remove-Item failed")
    if os.name == "nt" and os.environ.get("USERNAME"):
        _repair_windows_directory_acl(path)
        for _attempt in range(2):
            try:
                _rmtree_bottom_up_once(path)
                return
            except OSError as exc:
                last_error = exc
        for executable in ("pwsh", "powershell"):
            try:
                result = subprocess.run(
                    [executable, "-NoProfile", "-Command", script],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    check=False,
                )
            except FileNotFoundError:
                continue
            if result.returncode == 0 or not path.exists():
                return
            last_error = OSError(result.stderr.strip() or result.stdout.strip() or f"{executable} Remove-Item failed")
    raise ReclaimError(f"recursive_remove_failed:{path}:{last_error}")


def _move_no_replace(source: Path, destination: Path, *, expected_stat: dict[str, int]) -> None:
    """Move a regular file without ever replacing an existing destination."""
    if destination.exists() or destination.is_symlink():
        raise ReclaimError(f"destination_exists:{destination}")
    try:
        source_stat = source.lstat()
    except OSError as exc:
        raise ReclaimError(f"source_missing:{source}:{exc}") from exc
    if source.is_symlink() or not stat.S_ISREG(source_stat.st_mode):
        raise ReclaimError(f"source_unsupported:{source}")
    if _stat_evidence(source_stat) != expected_stat:
        raise ReclaimError(f"source_changed:{source}")
    original_mode = stat.S_IMODE(source_stat.st_mode)
    try:
        os.link(source, destination, follow_symlinks=False)
        linked_stat = destination.lstat()
        current_stat = source.lstat()
        identity_fields = ("device", "inode", "mode", "size")
        linked = _stat_evidence(linked_stat)
        current = _stat_evidence(current_stat)
        if any(linked[key] != current[key] for key in identity_fields):
            raise ReclaimError(f"linked_identity_mismatch:{source}")
        _unlink_regular_with_write_retry(source)
        _restore_permission_bits(destination, original_mode)
    except (OSError, ReclaimError) as exc:
        try:
            if destination.exists() and source.exists():
                _unlink_regular_with_write_retry(destination)
                _restore_permission_bits(source, original_mode)
        except OSError:
            pass
        raise ReclaimError(f"no_replace_move_failed:{source}:{destination}:{exc}") from exc


def _move_directory_no_replace(source: Path, destination: Path, *, expected_stat: dict[str, int]) -> None:
    """Move a directory tree without replacing an existing destination."""
    if destination.exists() or destination.is_symlink():
        raise ReclaimError(f"destination_exists:{destination}")
    try:
        source_stat = source.lstat()
    except OSError as exc:
        raise ReclaimError(f"source_missing:{source}:{exc}") from exc
    if source.is_symlink() or not stat.S_ISDIR(source_stat.st_mode):
        raise ReclaimError(f"source_unsupported:{source}")
    if _stat_evidence(source_stat) != expected_stat:
        raise ReclaimError(f"source_changed:{source}")
    try:
        source.rename(destination)
    except PermissionError:
        _repair_windows_directory_acl(source)
        try:
            source.rename(destination)
        except OSError as retry_exc:
            raise ReclaimError(f"directory_move_failed:{source}:{destination}:{retry_exc}") from retry_exc
        try:
            moved_stat = destination.lstat()
        except OSError as stat_exc:
            raise ReclaimError(f"destination_unreadable:{destination}:{stat_exc}") from stat_exc
        if _stat_evidence(moved_stat) != expected_stat:
            raise ReclaimError(f"destination_changed:{destination}") from None
    except OSError as exc:
        raise ReclaimError(f"directory_move_failed:{source}:{destination}:{exc}") from exc


def _move_payload_no_replace(
    source: Path,
    destination: Path,
    item: dict[str, Any],
    *,
    expected_stat: dict[str, int],
) -> None:
    if item.get("source_kind") in _DIRECTORY_SOURCE_KINDS:
        _move_directory_no_replace(source, destination, expected_stat=expected_stat)
        return
    _move_no_replace(source, destination, expected_stat=expected_stat)


def _state_allows_existing_payload_recovery(state: dict[str, Any]) -> bool:
    refusal = state.get("last_refusal")
    return (
        state.get("status") == "refused"
        and isinstance(refusal, dict)
        and refusal.get("operation") == "trash"
        and refusal.get("code") == "atomic_move_failed"
    )


def _complete_existing_payload_move(
    source: Path,
    payload: Path,
    *,
    expected_stat: dict[str, int],
    expected_sha256: str,
) -> None:
    """Complete a previous link-then-unlink move that left source and payload present."""
    if payload.is_symlink() or source.is_symlink():
        raise ReclaimError(f"retry_payload_unsupported:{payload}")
    try:
        source_stat = source.lstat()
        payload_stat = payload.lstat()
    except OSError as exc:
        raise ReclaimError(f"retry_payload_state_unreadable:{exc}") from exc
    if not stat.S_ISREG(source_stat.st_mode) or not stat.S_ISREG(payload_stat.st_mode):
        raise ReclaimError(f"retry_payload_unsupported:{payload}")
    if _stat_evidence(source_stat) != expected_stat:
        raise ReclaimError(f"source_changed:{source}")
    if int(payload_stat.st_dev) != int(source_stat.st_dev):
        raise ReclaimError(f"retry_payload_cross_device:{payload}")
    if int(payload_stat.st_size) != int(source_stat.st_size):
        raise ReclaimError(f"retry_payload_size_mismatch:{payload}")
    if _file_sha256(payload) != expected_sha256:
        raise ReclaimError(f"retry_payload_hash_mismatch:{payload}")
    original_mode = stat.S_IMODE(source_stat.st_mode)
    _unlink_regular_with_write_retry(source)
    _restore_permission_bits(payload, original_mode)


def _has_symlink_parent(root: Path, path: Path) -> bool:
    try:
        relative = path.relative_to(root)
    except ValueError:
        return True
    current = root
    for part in relative.parts[:-1]:
        current = current / part
        try:
            if current.is_symlink():
                return True
        except OSError:
            return True
    return False


def _fresh_registry_and_git(root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    git = _collect_git_evidence(root)
    registry = _collect_registry(root)
    return git, registry


def _prevalidate_trash_item(
    root: Path,
    state: Path,
    item: dict[str, Any],
    git: dict[str, Any],
    registry: dict[str, Any],
    run_dir: Path,
    payload: Path,
) -> Path:
    rel_path = str(item["path"])
    source = _candidate_source(root, rel_path)
    if source is None:
        raise ReclaimError(f"path_escape_or_missing:{rel_path}")
    if _has_symlink_parent(root, source) or source.is_symlink():
        raise ReclaimError(f"path_escape_or_symlink:{rel_path}")
    try:
        current_stat = source.lstat()
    except OSError as exc:
        raise ReclaimError(f"candidate_missing:{rel_path}:{exc}") from exc
    source_kind = str(item.get("source_kind", "worktree_file"))
    if source_kind in {"worktree_file", "git_loose_object", "git_garbage_file"} and not stat.S_ISREG(
        current_stat.st_mode
    ):
        raise ReclaimError(f"unsupported_file_type:{rel_path}")
    if source_kind == "worktree_directory" and not stat.S_ISDIR(current_stat.st_mode):
        raise ReclaimError(f"unsupported_file_type:{rel_path}")
    if source_kind not in {"worktree_file", "worktree_directory", "git_loose_object", "git_garbage_file"}:
        raise ReclaimError(f"unsupported_source_kind:{rel_path}:{source_kind}")
    if _stat_evidence(current_stat) != item["stat"]:
        raise ReclaimError(f"candidate_changed:{rel_path}")
    registry_ids = _registry_preservation_ids(
        rel_path,
        registry["records"],
        candidate_class=str(item["candidate_class"]),
    )
    if registry_ids:
        raise ReclaimError(f"candidate_became_registered:{rel_path}:{','.join(registry_ids)}")
    state_prefix = _state_relative(root, state)
    if _is_protected(rel_path, state_prefix, item["candidate_class"]):
        raise ReclaimError(f"candidate_is_protected:{rel_path}")
    if item["candidate_class"] in _DETRITUS_CLASSES:
        if _direct_detritus_class(rel_path, state_prefix) != item["candidate_class"]:
            raise ReclaimError(f"candidate_class_changed:{rel_path}")
    elif item["candidate_class"] in {"stale_harness_scratch", "stale_draft_scratch"}:
        if _scratch_class(rel_path) != item["candidate_class"]:
            raise ReclaimError(f"candidate_class_changed:{rel_path}")
    elif item["candidate_class"] == "unreachable_loose_object":
        common_dir: Path = git["common_dir"]
        expected = common_dir / "objects" / str(item["git_oid"])[:2] / str(item["git_oid"])[2:]
        if expected.resolve(strict=False) != source.resolve(strict=False):
            raise ReclaimError(f"loose_object_path_changed:{rel_path}")
        info = _batch_object_info(root, {str(item["git_oid"])}).get(str(item["git_oid"]))
        if info is None or info[0] != item["git_object_type"]:
            raise ReclaimError(f"loose_object_invalid:{rel_path}")
        if item["git_oid"] in git["reachable"]:
            raise ReclaimError(f"loose_object_newly_reachable:{rel_path}")
    elif item["candidate_class"] == "malformed_git_object_garbage":
        common_dir = git["common_dir"]
        objects_dir = common_dir / "objects"
        try:
            relative_object = source.relative_to(objects_dir)
        except ValueError as exc:
            raise ReclaimError(f"git_garbage_path_changed:{rel_path}") from exc
        if (
            len(relative_object.parts) != 2
            or not _HEX_FANOUT_RE.fullmatch(relative_object.parts[0])
            or not _GIT_TMP_OBJECT_RE.fullmatch(relative_object.parts[1])
        ):
            raise ReclaimError(f"git_garbage_path_changed:{rel_path}")
    else:
        raise ReclaimError(f"candidate_class_unsupported:{item['candidate_class']}")
    if int(current_stat.st_dev) != int(state.stat().st_dev):
        raise ReclaimError(f"cross_device_candidate:{rel_path}")
    try:
        payload_parent = payload.parent.resolve(strict=True)
    except OSError as exc:
        raise ReclaimError(f"trash_parent_missing:{payload.parent}:{exc}") from exc
    if (
        not _is_within(payload_parent, run_dir)
        or _has_symlink_parent(run_dir, payload)
        or int(payload_parent.stat().st_dev) != int(current_stat.st_dev)
    ):
        raise ReclaimError(f"trash_parent_unsafe:{payload.parent}")
    if payload.is_symlink():
        raise ReclaimError(f"trash_collision:{payload}")
    if payload.exists():
        try:
            payload_stat = payload.lstat()
        except OSError as exc:
            raise ReclaimError(f"trash_collision:{payload}:{exc}") from exc
        payload_kind_ok = (
            source_kind == "worktree_directory"
            and stat.S_ISDIR(payload_stat.st_mode)
            or source_kind != "worktree_directory"
            and stat.S_ISREG(payload_stat.st_mode)
        )
        if not payload_kind_ok or int(payload_stat.st_dev) != int(current_stat.st_dev):
            raise ReclaimError(f"trash_collision:{payload}")
    return source


def _prevalidate_existing_payload_recovery(
    source: Path,
    payload: Path,
    *,
    item_state: dict[str, Any],
    expected_source_stat: dict[str, int],
    expected_sha256: str,
) -> None:
    if not _state_allows_existing_payload_recovery(item_state):
        raise ReclaimError(f"unexpected_existing_payload:{payload}")
    if payload.is_symlink() or not payload.exists():
        raise ReclaimError(f"trash_collision:{payload}")
    try:
        payload_stat = payload.lstat()
        source_stat = source.lstat()
    except OSError as exc:
        raise ReclaimError(f"existing_payload_unreadable:{payload}:{exc}") from exc
    if not stat.S_ISREG(payload_stat.st_mode):
        raise ReclaimError(f"trash_collision:{payload}")
    if _stat_evidence(source_stat) != expected_source_stat:
        raise ReclaimError(f"candidate_changed:{source}")
    if int(payload_stat.st_dev) != int(source_stat.st_dev):
        raise ReclaimError(f"existing_payload_cross_device:{payload}")
    if int(payload_stat.st_size) != int(source_stat.st_size):
        raise ReclaimError(f"existing_payload_size_mismatch:{payload}")
    if _file_sha256(payload) != expected_sha256:
        raise ReclaimError(f"existing_payload_hash_mismatch:{payload}")


def _trash_reclaim_locked(
    root: Path,
    *,
    run_id: str,
    plan_hash: str,
    item_ids: tuple[str, ...] | list[str],
    owner_evidence: tuple[str, ...] | list[str],
    quiescence_evidence: tuple[str, ...] | list[str],
    state_root: Path | None = None,
) -> dict[str, Any]:
    """Atomically move an exact, revalidated batch into reversible trash."""
    root = _root_path(Path(root))
    state = _state_path(root, state_root)
    run_dir, manifest, events = _validated_run(root, state, run_id)
    requested = _normalize_item_ids(item_ids)
    item_by_id = {item["item_id"]: item for item in manifest["items"]}
    unknown = [item_id for item_id in requested if item_id not in item_by_id]
    if unknown:
        _refuse(run_dir, events, [], code="unknown_item_id", detail=",".join(unknown))
    if plan_hash != manifest["plan_hash"]:
        _refuse(run_dir, events, requested, code="plan_hash_mismatch", detail="exact plan hash is required")
    if not manifest["executable"]:
        _refuse(run_dir, events, requested, code="plan_not_executable", detail="planning evidence has blockers")
    try:
        owner_refs = _normalize_nonempty(owner_evidence, "owner_evidence")
        quiescence_refs = _normalize_nonempty(quiescence_evidence, "quiescence_evidence")
    except ReclaimError as exc:
        _refuse(run_dir, events, requested, code="evidence_missing", detail=str(exc))

    states, transition_errors, partial = _reconstruct_states(manifest, events)
    if transition_errors or partial:
        raise ReclaimError("event state is corrupt or partial")
    invalid_states = [
        item_id for item_id in requested if states[item_id]["payload_state"] not in {"planned", "restored"}
    ]
    if invalid_states:
        _refuse(
            run_dir,
            events,
            invalid_states,
            code="item_state_not_trashable",
            detail=",".join(invalid_states),
        )

    git, registry = _fresh_registry_and_git(root)
    if git["public"]["defects"]:
        _refuse(run_dir, events, requested, code="git_evidence_incomplete", detail="fresh Git roots are incomplete")
    if registry["public"]["defects"]:
        _refuse(
            run_dir,
            events,
            requested,
            code="registry_reality_invalid",
            detail="fresh registry evidence has defects",
        )
    if registry["public"]["records_digest"] != manifest["registry"]["records_digest"]:
        _refuse(run_dir, events, requested, code="registry_changed", detail="registry changed after planning")

    try:
        payloads = _prepare_payload_paths(run_dir, state, requested)
    except ReclaimError as exc:
        _refuse(run_dir, events, requested, code="trash_destination_failed", detail=str(exc))
    sources: dict[str, Path] = {}
    try:
        for item_id in requested:
            sources[item_id] = _prevalidate_trash_item(
                root,
                state,
                item_by_id[item_id],
                git,
                registry,
                run_dir,
                payloads[item_id],
            )
    except ReclaimError as exc:
        _refuse(run_dir, events, requested, code="candidate_revalidation_failed", detail=str(exc))

    content_hashes: dict[str, str] = {}
    try:
        for item_id in requested:
            source = sources[item_id]
            content_hashes[item_id] = _payload_fingerprint(source, item_by_id[item_id])
            if _stat_evidence(source.lstat()) != item_by_id[item_id]["stat"]:
                raise ReclaimError(f"candidate_changed_while_hashing:{item_by_id[item_id]['path']}")
    except (OSError, ReclaimError) as exc:
        _refuse(run_dir, events, requested, code="candidate_hash_failed", detail=str(exc))

    fresh_git, fresh_registry = _fresh_registry_and_git(root)
    if fresh_git["public"]["defects"]:
        _refuse(run_dir, events, requested, code="git_evidence_incomplete", detail="pre-move Git roots are incomplete")
    if fresh_registry["public"]["defects"]:
        _refuse(
            run_dir,
            events,
            requested,
            code="registry_reality_invalid",
            detail="pre-move registry evidence has defects",
        )
    if fresh_registry["public"]["records_digest"] != manifest["registry"]["records_digest"]:
        _refuse(run_dir, events, requested, code="registry_changed", detail="registry changed before move")
    try:
        for item_id in requested:
            sources[item_id] = _prevalidate_trash_item(
                root,
                state,
                item_by_id[item_id],
                fresh_git,
                fresh_registry,
                run_dir,
                payloads[item_id],
            )
    except ReclaimError as exc:
        _refuse(run_dir, events, requested, code="candidate_revalidation_failed", detail=str(exc))

    trashed: list[dict[str, Any]] = []
    for item_id in requested:
        item = item_by_id[item_id]
        source = sources[item_id]
        payload = payloads[item_id]
        existing_payload = False
        try:
            if _stat_evidence(source.lstat()) != item["stat"]:
                raise ReclaimError(f"candidate_changed_immediately_before_move:{item['path']}")
            payload_parent = payload.parent.resolve(strict=True)
            if not _is_within(payload_parent, run_dir) or _has_symlink_parent(run_dir, payload) or payload.is_symlink():
                raise ReclaimError(f"trash_destination_changed:{payload}")
            existing_payload = payload.exists()
            if existing_payload:
                _prevalidate_existing_payload_recovery(
                    source,
                    payload,
                    item_state=states[item_id],
                    expected_source_stat=item["stat"],
                    expected_sha256=content_hashes[item_id],
                )
        except (OSError, ReclaimError) as exc:
            _refuse(run_dir, events, [item_id], code="immediate_revalidation_failed", detail=str(exc))
        started_details: dict[str, Any] = {
            "path": item["path"],
            "payload_path": payload.relative_to(run_dir).as_posix(),
        }
        if existing_payload:
            started_details["existing_payload_recovery"] = True
        _append_event(
            run_dir,
            events,
            action="trash_started",
            item_id=item_id,
            details=started_details,
        )
        try:
            if existing_payload:
                _complete_existing_payload_move(
                    source,
                    payload,
                    expected_stat=item["stat"],
                    expected_sha256=content_hashes[item_id],
                )
            else:
                _move_payload_no_replace(source, payload, item, expected_stat=item["stat"])
            if _payload_fingerprint(payload, item) != content_hashes[item_id]:
                if not source.exists():
                    _move_payload_no_replace(payload, source, item, expected_stat=_stat_evidence(payload.lstat()))
                raise ReclaimError(f"payload_changed_during_move:{item['path']}")
        except (OSError, ReclaimError) as exc:
            _append_event(
                run_dir,
                events,
                action="refused",
                item_id=item_id,
                details={"operation": "trash", "code": "atomic_move_failed", "detail": str(exc)},
            )
            raise ReclaimError(f"atomic_move_failed: {item['path']}: {exc}") from exc
        receipt = {
            "operation": "trash",
            "source_path": item["path"],
            "payload_path": payload.relative_to(run_dir).as_posix(),
            "payload_sha256": content_hashes[item_id],
            "item_hash": item["item_hash"],
            "logical_bytes_removed": int(item["logical_bytes"]),
            "physical_bytes_reclaimed": 0,
            "owner_evidence": owner_refs,
            "quiescence_evidence": quiescence_refs,
        }
        _append_event(run_dir, events, action="trashed", item_id=item_id, details=receipt)
        trashed.append({"item_id": item_id, **receipt})
    return {
        "run_id": run_id,
        "plan_hash": manifest["plan_hash"],
        "status": "trashed",
        "requested_item_ids": requested,
        "trashed": trashed,
        "logical_bytes_removed": sum(item["logical_bytes_removed"] for item in trashed),
        "physical_bytes_reclaimed": 0,
    }


def trash_reclaim(
    root: Path,
    *,
    run_id: str,
    plan_hash: str,
    item_ids: tuple[str, ...] | list[str],
    owner_evidence: tuple[str, ...] | list[str],
    quiescence_evidence: tuple[str, ...] | list[str],
    state_root: Path | None = None,
) -> dict[str, Any]:
    """Lock and atomically move an exact, revalidated batch into reversible trash."""
    resolved_root = _root_path(Path(root))
    resolved_state = _state_path(resolved_root, state_root)
    run_dir = _run_dir(resolved_state, run_id)
    with _operation_lock(run_dir, "trash"):
        return _trash_reclaim_locked(
            resolved_root,
            run_id=run_id,
            plan_hash=plan_hash,
            item_ids=item_ids,
            owner_evidence=owner_evidence,
            quiescence_evidence=quiescence_evidence,
            state_root=resolved_state,
        )


def _prevalidate_restore_item(
    root: Path,
    run_dir: Path,
    item: dict[str, Any],
    state_info: dict[str, Any],
) -> tuple[Path, Path, dict[str, Any]]:
    if state_info["payload_state"] != "trashed":
        raise ReclaimError(f"item_state_not_restorable:{item['item_id']}")
    receipt = state_info.get("receipt")
    if not isinstance(receipt, dict) or receipt.get("operation") != "trash":
        raise ReclaimError(f"trash_receipt_missing:{item['item_id']}")
    payload_rel = receipt.get("payload_path")
    if not isinstance(payload_rel, str) or not _safe_relative_path(payload_rel):
        raise ReclaimError(f"payload_path_invalid:{item['item_id']}")
    payload = run_dir / payload_rel
    try:
        resolved_payload = payload.resolve(strict=True)
    except OSError as exc:
        raise ReclaimError(f"payload_missing:{item['item_id']}:{exc}") from exc
    if not _is_within(resolved_payload, run_dir) or _has_symlink_parent(run_dir, payload) or payload.is_symlink():
        raise ReclaimError(f"payload_path_escape_or_unsupported:{item['item_id']}")
    if item.get("source_kind") in _DIRECTORY_SOURCE_KINDS:
        if not payload.is_dir():
            raise ReclaimError(f"payload_path_escape_or_unsupported:{item['item_id']}")
    elif not payload.is_file():
        raise ReclaimError(f"payload_path_escape_or_unsupported:{item['item_id']}")
    destination = root / item["path"]
    if not _safe_relative_path(item["path"]):
        raise ReclaimError(f"destination_path_invalid:{item['item_id']}")
    if destination.exists() or destination.is_symlink():
        raise ReclaimError(f"restore_would_overwrite:{item['path']}")
    if _has_symlink_parent(root, destination):
        raise ReclaimError(f"restore_parent_symlink:{item['path']}")
    try:
        parent = destination.parent.resolve(strict=True)
    except OSError as exc:
        raise ReclaimError(f"restore_parent_missing:{item['path']}:{exc}") from exc
    if not _is_within(parent, root):
        raise ReclaimError(f"restore_path_escape:{item['path']}")
    payload_stat = payload.stat()
    if int(payload_stat.st_dev) != int(root.stat().st_dev):
        raise ReclaimError(f"restore_cross_device:{item['path']}")
    if item.get("source_kind") not in _DIRECTORY_SOURCE_KINDS and int(payload_stat.st_size) != int(
        item["logical_bytes"]
    ):
        raise ReclaimError(f"payload_size_changed:{item['path']}")
    if _payload_fingerprint(payload, item) != receipt.get("payload_sha256"):
        raise ReclaimError(f"payload_hash_changed:{item['path']}")
    return payload, destination, receipt


def _prevalidate_purge_item(
    root: Path,
    run_dir: Path,
    item: dict[str, Any],
    state_info: dict[str, Any],
) -> tuple[Path, dict[str, Any], os.stat_result]:
    if state_info["payload_state"] != "trashed":
        raise ReclaimError(f"item_state_not_purgeable:{item['item_id']}")
    receipt = state_info.get("receipt")
    if not isinstance(receipt, dict) or receipt.get("operation") != "trash":
        raise ReclaimError(f"trash_receipt_missing:{item['item_id']}")
    payload_rel = receipt.get("payload_path")
    if not isinstance(payload_rel, str) or not _safe_relative_path(payload_rel):
        raise ReclaimError(f"payload_path_invalid:{item['item_id']}")
    payload = run_dir / payload_rel
    try:
        resolved_payload = payload.resolve(strict=True)
    except OSError as exc:
        raise ReclaimError(f"payload_missing:{item['item_id']}:{exc}") from exc
    if not _is_within(resolved_payload, run_dir) or _has_symlink_parent(run_dir, payload) or payload.is_symlink():
        raise ReclaimError(f"payload_path_escape_or_unsupported:{item['item_id']}")
    if item.get("source_kind") in _DIRECTORY_SOURCE_KINDS:
        if not payload.is_dir():
            raise ReclaimError(f"payload_path_escape_or_unsupported:{item['item_id']}")
    elif not payload.is_file():
        raise ReclaimError(f"payload_path_escape_or_unsupported:{item['item_id']}")
    if not _safe_relative_path(item["path"]):
        raise ReclaimError(f"source_path_invalid:{item['item_id']}")
    payload_stat = payload.stat()
    if item.get("source_kind") not in _DIRECTORY_SOURCE_KINDS and int(payload_stat.st_size) != int(
        item["logical_bytes"]
    ):
        raise ReclaimError(f"payload_size_changed:{item['path']}")
    if _payload_fingerprint(payload, item) != receipt.get("payload_sha256"):
        raise ReclaimError(f"payload_hash_changed:{item['path']}")
    return payload, receipt, payload_stat


def _restore_reclaim_locked(
    root: Path,
    *,
    run_id: str,
    item_ids: tuple[str, ...] | list[str],
    state_root: Path | None = None,
) -> dict[str, Any]:
    """Atomically restore exact trashed items without overwriting any path."""
    root = _root_path(Path(root))
    state = _state_path(root, state_root)
    run_dir, manifest, events = _validated_run(root, state, run_id)
    requested = _normalize_item_ids(item_ids)
    item_by_id = {item["item_id"]: item for item in manifest["items"]}
    unknown = [item_id for item_id in requested if item_id not in item_by_id]
    if unknown:
        _refuse(run_dir, events, [], code="unknown_item_id", detail=",".join(unknown))
    states, transition_errors, partial = _reconstruct_states(manifest, events)
    if transition_errors or partial:
        raise ReclaimError("event state is corrupt or partial")

    prepared: dict[str, tuple[Path, Path, dict[str, Any]]] = {}
    try:
        for item_id in requested:
            prepared[item_id] = _prevalidate_restore_item(
                root,
                run_dir,
                item_by_id[item_id],
                states[item_id],
            )
    except ReclaimError as exc:
        _refuse(run_dir, events, requested, code="restore_revalidation_failed", detail=str(exc))

    restored: list[dict[str, Any]] = []
    for item_id in requested:
        item = item_by_id[item_id]
        payload, destination, trash_receipt = prepared[item_id]
        try:
            payload_stat = payload.lstat()
            if (
                _payload_fingerprint(payload, item) != trash_receipt["payload_sha256"]
                or destination.exists()
                or destination.is_symlink()
                or _has_symlink_parent(root, destination)
                or not _is_within(destination.parent.resolve(strict=True), root)
            ):
                raise ReclaimError(f"restore_state_changed_immediately_before_move:{item['path']}")
        except (OSError, ReclaimError) as exc:
            _refuse(run_dir, events, [item_id], code="immediate_restore_revalidation_failed", detail=str(exc))
        _append_event(
            run_dir,
            events,
            action="restore_started",
            item_id=item_id,
            details={"path": item["path"], "payload_path": payload.relative_to(run_dir).as_posix()},
        )
        try:
            _move_payload_no_replace(payload, destination, item, expected_stat=_stat_evidence(payload_stat))
            if _payload_fingerprint(destination, item) != trash_receipt["payload_sha256"]:
                if not payload.exists():
                    _move_payload_no_replace(
                        destination,
                        payload,
                        item,
                        expected_stat=_stat_evidence(destination.lstat()),
                    )
                raise ReclaimError(f"restored_payload_changed:{item['path']}")
        except (OSError, ReclaimError) as exc:
            _append_event(
                run_dir,
                events,
                action="refused",
                item_id=item_id,
                details={"operation": "restore", "code": "atomic_restore_failed", "detail": str(exc)},
            )
            raise ReclaimError(f"atomic_restore_failed: {item['path']}: {exc}") from exc
        receipt = {
            "operation": "restore",
            "destination_path": item["path"],
            "payload_sha256": trash_receipt["payload_sha256"],
            "logical_bytes_restored": int(item["logical_bytes"]),
            "physical_bytes_reclaimed": 0,
        }
        _append_event(run_dir, events, action="restored", item_id=item_id, details=receipt)
        restored.append({"item_id": item_id, **receipt})
    return {
        "run_id": run_id,
        "status": "restored",
        "requested_item_ids": requested,
        "restored": restored,
        "logical_bytes_restored": sum(item["logical_bytes_restored"] for item in restored),
        "physical_bytes_reclaimed": 0,
    }


def _purge_reclaim_locked(
    root: Path,
    *,
    run_id: str,
    plan_hash: str,
    item_ids: tuple[str, ...] | list[str],
    owner_evidence: tuple[str, ...] | list[str],
    quiescence_evidence: tuple[str, ...] | list[str],
    state_root: Path | None = None,
) -> dict[str, Any]:
    """Permanently delete exact, receipted trash payloads and retain receipts."""
    root = _root_path(Path(root))
    state = _state_path(root, state_root)
    run_dir, manifest, events = _validated_run(root, state, run_id)
    requested = _normalize_item_ids(item_ids)
    owner_refs = _normalize_nonempty(owner_evidence, "owner_evidence")
    quiescence_refs = _normalize_nonempty(quiescence_evidence, "quiescence_evidence")
    if manifest["plan_hash"] != plan_hash:
        _refuse(run_dir, events, requested, code="plan_hash_mismatch", detail="requested plan hash does not match run")
    item_by_id = {item["item_id"]: item for item in manifest["items"]}
    unknown = [item_id for item_id in requested if item_id not in item_by_id]
    if unknown:
        _refuse(run_dir, events, [], code="unknown_item_id", detail=",".join(unknown))
    states, transition_errors, partial = _reconstruct_states(manifest, events)
    if transition_errors or partial:
        raise ReclaimError("event state is corrupt or partial")

    prepared: dict[str, tuple[Path, dict[str, Any], os.stat_result]] = {}
    try:
        for item_id in requested:
            prepared[item_id] = _prevalidate_purge_item(
                root,
                run_dir,
                item_by_id[item_id],
                states[item_id],
            )
    except ReclaimError as exc:
        _refuse(run_dir, events, requested, code="purge_revalidation_failed", detail=str(exc))

    purged: list[dict[str, Any]] = []
    for item_id in requested:
        item = item_by_id[item_id]
        payload, trash_receipt, payload_stat = prepared[item_id]
        try:
            if payload.is_symlink():
                raise ReclaimError(f"purge_payload_changed:{item['path']}")
            if item.get("source_kind") in _DIRECTORY_SOURCE_KINDS:
                if not payload.is_dir():
                    raise ReclaimError(f"purge_payload_changed:{item['path']}")
            elif not payload.is_file():
                raise ReclaimError(f"purge_payload_changed:{item['path']}")
            current_stat = payload.lstat()
            if _stat_evidence(current_stat) != _stat_evidence(payload_stat):
                raise ReclaimError(f"purge_payload_changed:{item['path']}")
        except (OSError, ReclaimError) as exc:
            _refuse(run_dir, events, [item_id], code="immediate_purge_revalidation_failed", detail=str(exc))
        payload_rel = payload.relative_to(run_dir).as_posix()
        _append_event(
            run_dir,
            events,
            action="purge_started",
            item_id=item_id,
            details={"path": item["path"], "payload_path": payload_rel},
        )
        try:
            if item.get("source_kind") in _DIRECTORY_SOURCE_KINDS:
                _rmtree_with_write_retry(payload)
            else:
                _unlink_regular_with_write_retry(payload)
            with suppress(OSError):
                payload.parent.rmdir()
        except (OSError, ReclaimError) as exc:
            _append_event(
                run_dir,
                events,
                action="refused",
                item_id=item_id,
                details={"operation": "purge", "code": "atomic_purge_failed", "detail": str(exc)},
            )
            raise ReclaimError(f"atomic_purge_failed: {item['path']}: {exc}") from exc
        receipt = {
            "operation": "purge",
            "source_path": item["path"],
            "payload_path": payload_rel,
            "payload_sha256": trash_receipt["payload_sha256"],
            "item_hash": item["item_hash"],
            "logical_bytes_purged": int(item["logical_bytes"]),
            "physical_bytes_reclaimed": int(
                item["logical_bytes"] if item.get("source_kind") in _DIRECTORY_SOURCE_KINDS else payload_stat.st_size
            ),
            "owner_evidence": owner_refs,
            "quiescence_evidence": quiescence_refs,
        }
        _append_event(run_dir, events, action="purged", item_id=item_id, details=receipt)
        purged.append({"item_id": item_id, **receipt})
    return {
        "run_id": run_id,
        "plan_hash": manifest["plan_hash"],
        "status": "purged",
        "requested_item_ids": requested,
        "purged": purged,
        "logical_bytes_purged": sum(item["logical_bytes_purged"] for item in purged),
        "physical_bytes_reclaimed": sum(item["physical_bytes_reclaimed"] for item in purged),
    }


def purge_reclaim(
    root: Path,
    *,
    run_id: str,
    plan_hash: str,
    item_ids: tuple[str, ...] | list[str],
    owner_evidence: tuple[str, ...] | list[str],
    quiescence_evidence: tuple[str, ...] | list[str],
    state_root: Path | None = None,
) -> dict[str, Any]:
    """Lock and permanently delete exact, receipted trash payloads."""
    resolved_root = _root_path(Path(root))
    resolved_state = _state_path(resolved_root, state_root)
    run_dir = _run_dir(resolved_state, run_id)
    with _operation_lock(run_dir, "purge"):
        return _purge_reclaim_locked(
            resolved_root,
            run_id=run_id,
            plan_hash=plan_hash,
            item_ids=item_ids,
            owner_evidence=owner_evidence,
            quiescence_evidence=quiescence_evidence,
            state_root=resolved_state,
        )


def _chunks(values: list[str], size: int) -> Iterator[list[str]]:
    if isinstance(size, bool) or size <= 0:
        raise ReclaimError("batch_size must be a positive integer")
    for offset in range(0, len(values), size):
        yield values[offset : offset + size]


def deep_clean_reclaim(
    root: Path,
    *,
    owner_evidence: tuple[str, ...] | list[str],
    quiescence_evidence: tuple[str, ...] | list[str],
    state_root: Path | None = None,
    min_age_hours: int = 168,
    max_cycles: int = 25,
    batch_size: int = 250,
    now: datetime | None = None,
    actor: str | None = None,
    session_id: str | None = None,
) -> dict[str, Any]:
    """Plan, trash, and purge until the production reclaim planner is clean."""
    resolved_root = _root_path(Path(root))
    resolved_state = _state_path(resolved_root, state_root)
    owner_refs = _normalize_nonempty(owner_evidence, "owner_evidence")
    quiescence_refs = _normalize_nonempty(quiescence_evidence, "quiescence_evidence")
    if isinstance(max_cycles, bool) or max_cycles <= 0:
        raise ReclaimError("max_cycles must be a positive integer")
    if isinstance(batch_size, bool) or batch_size <= 0:
        raise ReclaimError("batch_size must be a positive integer")

    cycles: list[dict[str, Any]] = []
    total_trashed = 0
    total_purged = 0
    total_logical_bytes_removed = 0
    total_physical_bytes_reclaimed = 0
    blocked_purges: list[dict[str, str]] = []
    final_plan: dict[str, Any] | None = None

    for cycle_index in range(1, max_cycles + 1):
        plan = plan_reclaim(
            resolved_root,
            state_root=resolved_state,
            min_age_hours=min_age_hours,
            now=now,
            actor=actor,
            session_id=session_id,
        )
        final_plan = plan
        candidate_count = int(plan["candidate_count"])
        cycle: dict[str, Any] = {
            "cycle": cycle_index,
            "run_id": plan["run_id"],
            "plan_hash": plan["plan_hash"],
            "candidate_count": candidate_count,
            "logical_bytes": int(plan["logical_bytes"]),
            "trashed": 0,
            "purged": 0,
            "blocked_purges": [],
            "physical_bytes_reclaimed": 0,
        }
        if candidate_count == 0:
            cycles.append(cycle)
            status = "clean" if not blocked_purges else "blocked_purges"
            return {
                "status": status,
                "cycles": cycles,
                "cycle_count": len(cycles),
                "final_run_id": plan["run_id"],
                "final_plan_hash": plan["plan_hash"],
                "final_candidate_count": 0,
                "total_trashed": total_trashed,
                "total_purged": total_purged,
                "blocked_purge_count": len(blocked_purges),
                "blocked_purges": blocked_purges,
                "logical_bytes_removed": total_logical_bytes_removed,
                "physical_bytes_reclaimed": total_physical_bytes_reclaimed,
            }
        if not bool(plan["executable"]):
            raise ReclaimError(f"deep_clean_plan_not_executable:{plan['run_id']}:{plan['blockers']}")

        manifest = _load_manifest(Path(str(plan["manifest_path"])).parent)
        item_ids = sorted(str(item["item_id"]) for item in manifest["items"])
        for chunk in _chunks(item_ids, batch_size):
            trashed = trash_reclaim(
                resolved_root,
                run_id=str(plan["run_id"]),
                plan_hash=str(plan["plan_hash"]),
                item_ids=chunk,
                owner_evidence=owner_refs,
                quiescence_evidence=quiescence_refs,
                state_root=resolved_state,
            )
            trashed_count = len(trashed.get("trashed", []))
            cycle["trashed"] += trashed_count
            total_trashed += trashed_count
            total_logical_bytes_removed += int(trashed.get("logical_bytes_removed", 0))
            for item_id in chunk:
                try:
                    purged = purge_reclaim(
                        resolved_root,
                        run_id=str(plan["run_id"]),
                        plan_hash=str(plan["plan_hash"]),
                        item_ids=[item_id],
                        owner_evidence=owner_refs,
                        quiescence_evidence=quiescence_refs,
                        state_root=resolved_state,
                    )
                except ReclaimError as exc:
                    blocked = {"run_id": str(plan["run_id"]), "item_id": item_id, "detail": str(exc)}
                    blocked_purges.append(blocked)
                    cycle["blocked_purges"].append(blocked)
                    continue
                purged_count = len(purged.get("purged", []))
                reclaimed = int(purged.get("physical_bytes_reclaimed", 0))
                cycle["purged"] += purged_count
                cycle["physical_bytes_reclaimed"] += reclaimed
                total_purged += purged_count
                total_physical_bytes_reclaimed += reclaimed
        cycles.append(cycle)

    raise ReclaimError(
        "deep_clean_max_cycles_reached:"
        f"{max_cycles}:final_run_id={final_plan.get('run_id') if final_plan else '<none>'}"
    )


def restore_reclaim(
    root: Path,
    *,
    run_id: str,
    item_ids: tuple[str, ...] | list[str],
    state_root: Path | None = None,
) -> dict[str, Any]:
    """Lock and restore exact trashed items without overwriting any path."""
    resolved_root = _root_path(Path(root))
    resolved_state = _state_path(resolved_root, state_root)
    run_dir = _run_dir(resolved_state, run_id)
    with _operation_lock(run_dir, "restore"):
        return _restore_reclaim_locked(
            resolved_root,
            run_id=run_id,
            item_ids=item_ids,
            state_root=resolved_state,
        )


__all__ = [
    "deep_clean_reclaim",
    "ReclaimError",
    "history_reclaim",
    "plan_reclaim",
    "purge_reclaim",
    "restore_reclaim",
    "trash_reclaim",
]
