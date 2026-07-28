"""Typed, deterministic reconciliation for the platform artifact registry.

Registry declarations remain the only membership authority.  The observers in
this module establish that a present path is load-bearing; they never grant
membership themselves.  Reconciliation therefore reports candidate additions
separately from current membership and leaves registry mutation to the
journalled control plane.
"""

from __future__ import annotations

import fnmatch
import hashlib
import heapq
import json
import os
import re
import stat
import subprocess
import tomllib
from collections import defaultdict
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Literal

from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.inventory.string_scan import registered_artifact_inventory
from groundtruth_kb.project.registry_control_plane import (
    RegistryCoverageError,
    RegistrySnapshot,
    load_registry_snapshot,
    registry_currentness,
)
from groundtruth_kb.project.sot_registry import SoTArtifact

ObserverClass = Literal[
    "capability_inventory",
    "governed_knowledge",
    "package_and_entrypoint",
    "registered_dependency_closure",
    "physical_census",
]
MembershipClass = Literal[
    "registered",
    "unregistered_load_bearing",
    "unregistered_disposable",
    "invalid_unknown",
]
TraversalState = Literal[
    "inspected",
    "structural_ancestor",
    "pruned_uninspected_subtree",
    "owned_service_boundary",
    "hosted_application_boundary",
    "no_follow_boundary",
]

REQUIRED_OBSERVER_CLASSES: tuple[ObserverClass, ...] = (
    "capability_inventory",
    "governed_knowledge",
    "package_and_entrypoint",
    "registered_dependency_closure",
    "physical_census",
)

_TEXT_SUFFIXES = frozenset(
    {
        ".cmd",
        ".csv",
        ".ini",
        ".json",
        ".md",
        ".ps1",
        ".py",
        ".sh",
        ".toml",
        ".txt",
        ".yaml",
        ".yml",
    }
)
_NON_AUTHORITATIVE_PREFIXES = (
    ".git/",
    ".gtkb-state/",
    ".gtkb-tmp/",
    ".pytest_cache/",
    ".pytest-tmp/",
    ".ruff_cache/",
    ".tmp/",
    ".tmp-lo-verdict-drafts/",
    "__pycache__/",
    "memory/",
    "scratch/",
    "scratchpad/",
    "temp/",
    "tmp/",
    "work/",
    "work_area/",
)
_NON_AUTHORITATIVE_SEGMENTS = frozenset(
    {
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".tox",
        ".venv",
        "__pycache__",
        "node_modules",
        "venv",
    }
)
_NON_AUTHORITATIVE_RUNTIME_PREFIXES = (
    ".groundtruth/dashboard/",
    ".groundtruth/inventory/",
    ".groundtruth/session/",
    ".groundtruth/wrap-scan/",
    "independent-progress-assessments/",
    "scripts/upgrade-results/",
    "test-auth-root/",
)
_CANONICAL_UNTRACKED_REFERENCE_PREFIXES = (
    ".agent/skills/",
    ".api-harness/skills/",
    ".claude/commands/",
    ".claude/hooks/",
    ".claude/rules/",
    ".claude/skills/",
    ".codex/gtkb-hooks/",
    ".codex/skills/",
    ".cursor/gtkb-hooks/",
    ".cursor/rules/",
    ".cursor/skills/",
    ".githooks/",
    ".github/workflows/",
    ".goose/skills/",
    "config/",
    "docs/",
    "groundtruth-kb/",
    "infra/",
    "infrastructure/",
    "platform_tests/",
    "scripts/",
    "tools/",
)
_RECURSIVE_SERVICE_CONTAINER_ROOTS = frozenset({".groundtruth/formal-artifact-approvals"})
_SKIP_SOURCE_PREFIXES = (
    "bridge/",
    ".gtkb-state/",
    ".claude/session/",
    "memory/",
)
_PATH_TOKEN_RE = re.compile(
    r"(?<![A-Za-z0-9_])((?:\.?[A-Za-z0-9_$@{}()\[\]-]+[/\\])+"
    r"[A-Za-z0-9_.$@{}()\[\]*?\-]+)(?![A-Za-z0-9_])"
)
_BACKTICK_PATH_RE = re.compile(r"`([^`\r\n]+[/\\][^`\r\n]+)`")
_PATH_KEY_RE = re.compile(r"(?:path|file|source|target|surface|manifest|template|script|config)", re.IGNORECASE)
_TRACKED_INVENTORY_CACHE: dict[Path, frozenset[str]] = {}
_TRACKED_CANONICAL_CACHE: dict[Path, dict[str, str]] = {}
_GIT_MANAGED_INVENTORY_CACHE: dict[Path, frozenset[str] | None] = {}
_REFERENCE_RESOLUTION_CACHE: dict[tuple[Path, str], tuple[tuple[str, ...], str | None]] = {}


def _canonical_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(_canonical_json(value)).hexdigest()


def _sha256_bytes(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _tracked_inventory(project_root: Path) -> frozenset[str]:
    root = project_root.resolve()
    cached = _TRACKED_INVENTORY_CACHE.get(root)
    if cached is not None:
        return cached
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "ls-files", "-z"],
            check=False,
            capture_output=True,
            timeout=20,
        )
    except (OSError, subprocess.TimeoutExpired):
        inventory = frozenset()
    else:
        inventory = (
            frozenset(item for item in result.stdout.decode("utf-8").split("\0") if item)
            if result.returncode == 0
            else frozenset()
        )
    _TRACKED_INVENTORY_CACHE[root] = inventory
    return inventory


def _tracked_canonical_paths(project_root: Path) -> dict[str, str]:
    root = project_root.resolve()
    cached = _TRACKED_CANONICAL_CACHE.get(root)
    if cached is None:
        cached = {item.casefold(): item for item in _tracked_inventory(root)}
        _TRACKED_CANONICAL_CACHE[root] = cached
    return cached


def _git_managed_inventory(project_root: Path) -> frozenset[str] | None:
    """Return tracked plus untracked nonignored paths, or None when Git is unavailable."""

    root = project_root.resolve()
    if root in _GIT_MANAGED_INVENTORY_CACHE:
        return _GIT_MANAGED_INVENTORY_CACHE[root]
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
            check=False,
            capture_output=True,
            timeout=20,
        )
    except (OSError, subprocess.TimeoutExpired):
        inventory = None
    else:
        inventory = (
            frozenset(item for item in result.stdout.decode("utf-8").split("\0") if item)
            if result.returncode == 0
            else None
        )
    _GIT_MANAGED_INVENTORY_CACHE[root] = inventory
    return inventory


def _relative(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def _is_hosted_application_path(relative: str) -> bool:
    parts = PurePosixPath(relative).parts
    return len(parts) >= 2 and parts[0].casefold() == "applications"


def _is_non_authoritative_reference(relative: str) -> bool:
    folded = relative.casefold()
    if folded.startswith("./"):
        folded = folded[2:]
    parts = PurePosixPath(folded.rstrip("/")).parts
    basename = parts[-1] if parts else ""
    formal_approval = folded.startswith(".groundtruth/formal-artifact-approvals/")
    return (
        folded == "memory.md"
        or folded in {"groundtruth.db-shm", "groundtruth.db-wal", "groundtruth.db-journal"}
        or any(part in _NON_AUTHORITATIVE_SEGMENTS for part in parts)
        or any(folded.startswith(prefix.casefold()) for prefix in _NON_AUTHORITATIVE_RUNTIME_PREFIXES)
        or (folded.startswith(".groundtruth/") and not formal_approval)
        or basename.startswith(("last-session-", "last-user-visible-startup", "last-wrapup-"))
        or basename in {".session-lifecycle-guard.json", "scheduled_tasks.lock"}
        or any(folded.startswith(prefix.casefold()) for prefix in _NON_AUTHORITATIVE_PREFIXES)
    )


def _is_authoritative_dependency_target(
    project_root: Path,
    relative: str,
    *,
    typed_seed_paths: set[str],
) -> bool:
    """Require reference evidence plus a canonical target disposition.

    Git membership is corroborating evidence only.  A target still needs the
    registered-reference observation that called this helper.  Present
    untracked projections are accepted only inside known canonical surfaces or
    when another typed observer independently selected them.
    """

    folded = relative.casefold()
    if _is_non_authoritative_reference(relative):
        return False
    if folded == "groundtruth.db" or folded.startswith(".groundtruth/formal-artifact-approvals/"):
        return True
    tracked = folded in _tracked_canonical_paths(project_root)
    if folded in typed_seed_paths or tracked:
        return True
    if PurePosixPath(folded).suffix in {".db", ".err", ".lock", ".log", ".sqlite", ".sqlite3", ".tmp"}:
        return False
    return any(folded.startswith(prefix.casefold()) for prefix in _CANONICAL_UNTRACKED_REFERENCE_PREFIXES)


def _is_opaque_payload(snapshot: RegistrySnapshot, relative: str) -> bool:
    direct = snapshot.resolver.resolve(relative)
    if direct is not None:
        return False
    operation_record = snapshot.resolver.resolve_operation_path(relative)
    return operation_record is not None and operation_record.coverage_mode == "opaque_container"


def _is_prospective_service_payload(relative: str) -> bool:
    folded = relative.casefold()
    return any(folded.startswith(root.casefold().rstrip("/") + "/") for root in _RECURSIVE_SERVICE_CONTAINER_ROOTS)


def _is_prospective_service_boundary_or_payload(relative: str) -> bool:
    folded = relative.casefold().rstrip("/")
    return any(
        folded == root.casefold().rstrip("/") or folded.startswith(root.casefold().rstrip("/") + "/")
        for root in _RECURSIVE_SERVICE_CONTAINER_ROOTS
    )


def _is_skipped_dependency_source(relative: str) -> bool:
    return any(relative.casefold().startswith(prefix.casefold()) for prefix in _SKIP_SOURCE_PREFIXES)


def _ancestors(relative: str, *, include_self_for_directory: bool = False) -> tuple[str, ...]:
    path = PurePosixPath(relative.rstrip("/"))
    parents = list(path.parents)
    values = {parent.as_posix() for parent in parents if parent.as_posix() not in {"", "."}}
    if include_self_for_directory:
        values.add(path.as_posix())
    return tuple(sorted(values, key=str.casefold))


@dataclass(frozen=True)
class ArtifactObservation:
    relative_path: str
    observer_class: ObserverClass
    evidence_source: str
    reason: str

    def as_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class ObserverResult:
    observer_class: ObserverClass
    succeeded: bool
    input_digest: str
    observations: tuple[ArtifactObservation, ...] = ()
    ancestor_paths: tuple[str, ...] = ()
    diagnostics: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "observer_class": self.observer_class,
            "succeeded": self.succeeded,
            "input_digest": self.input_digest,
            "observation_count": len(self.observations),
            "ancestor_count": len(self.ancestor_paths),
            "observations": [item.as_dict() for item in self.observations],
            "diagnostics": list(self.diagnostics),
        }


@dataclass(frozen=True)
class MembershipEntry:
    relative_path: str
    object_kind: str
    membership_class: MembershipClass
    traversal_state: TraversalState
    descendants_inspected: bool
    registry_id: str | None = None
    observer_classes: tuple[str, ...] = ()
    evidence_sources: tuple[str, ...] = ()
    detail: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AdmissionCandidate:
    record: SoTArtifact
    observer_classes: tuple[str, ...]
    evidence_sources: tuple[str, ...]
    reasons: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        record = asdict(self.record)
        record["depends_on"] = list(self.record.depends_on)
        record["forbidden_substitutes"] = list(self.record.forbidden_substitutes)
        return {
            "record": record,
            "observer_classes": list(self.observer_classes),
            "evidence_sources": list(self.evidence_sources),
            "reasons": list(self.reasons),
        }


def _result(
    observer_class: ObserverClass,
    *,
    input_rows: Any,
    observations: Iterable[ArtifactObservation] = (),
    diagnostics: Iterable[str] = (),
    succeeded: bool = True,
) -> ObserverResult:
    unique = {(item.relative_path.casefold(), item.evidence_source, item.reason): item for item in observations}
    ordered = tuple(
        sorted(unique.values(), key=lambda item: (item.relative_path.casefold(), item.evidence_source, item.reason))
    )
    ancestor_paths: set[str] = set()
    for item in ordered:
        ancestor_paths.update(_ancestors(item.relative_path))
    return ObserverResult(
        observer_class=observer_class,
        succeeded=succeeded,
        input_digest=_digest(input_rows),
        observations=ordered,
        ancestor_paths=tuple(sorted(ancestor_paths, key=str.casefold)),
        diagnostics=tuple(sorted(set(diagnostics))),
    )


def _without_opaque_payload_observations(
    result: ObserverResult,
    snapshot: RegistrySnapshot,
) -> ObserverResult:
    """Keep opaque payloads owned by their registered service boundary."""

    kept = tuple(
        item
        for item in result.observations
        if not _is_opaque_payload(snapshot, item.relative_path)
        and not _is_prospective_service_payload(item.relative_path)
    )
    ancestor_paths = {ancestor for item in kept for ancestor in _ancestors(item.relative_path)}
    if not result.observations:
        ancestor_paths = {
            ancestor
            for ancestor in result.ancestor_paths
            if not _is_opaque_payload(snapshot, ancestor) and not _is_prospective_service_boundary_or_payload(ancestor)
        }
    if kept == result.observations and ancestor_paths == set(result.ancestor_paths):
        return result
    diagnostics = result.diagnostics
    if len(kept) != len(result.observations):
        diagnostics = (
            *diagnostics,
            f"service_payload_observations_suppressed:{len(result.observations) - len(kept)}",
        )
    return ObserverResult(
        observer_class=result.observer_class,
        succeeded=result.succeeded,
        input_digest=result.input_digest,
        observations=kept,
        ancestor_paths=tuple(sorted(ancestor_paths, key=str.casefold)),
        diagnostics=tuple(sorted(set(diagnostics))),
    )


def _clean_reference(raw: str) -> str:
    value = raw.strip().strip("`'\"")
    value = value.replace("\\", "/")
    value = re.sub(r"#L?\d+(?:-L?\d+)?$", "", value)
    value = re.sub(r":\d+(?::\d+)?$", "", value)
    return value.rstrip(".,;:)")


def _normalize_present_paths(root: Path, raw: str) -> tuple[tuple[str, ...], str | None]:
    cache_key = (root.resolve(), _clean_reference(raw))
    cached = _REFERENCE_RESOLUTION_CACHE.get(cache_key)
    if cached is not None:
        return cached
    result = _normalize_present_paths_uncached(root, raw)
    _REFERENCE_RESOLUTION_CACHE[cache_key] = result
    return result


def _normalize_present_paths_uncached(root: Path, raw: str) -> tuple[tuple[str, ...], str | None]:
    value = _clean_reference(raw)
    if value in {"", ".", "./", "/"}:
        return (), "project_root_reference"
    if not value or value.startswith(("membase:", "windows-scheduled-task:")):
        return (), "non_filesystem"
    value = re.sub(r"/{2,}", "/", value)
    candidate = Path(value)
    if candidate.is_absolute():
        try:
            relative = candidate.resolve(strict=False).relative_to(root).as_posix()
        except (OSError, ValueError):
            return (), "outside_project_root"
        value = relative
    if value.startswith("./"):
        value = value[2:]
    if value.rstrip("/") in {"", "."}:
        return (), "project_root_reference"
    if not value or any(part in {"", ".", ".."} for part in PurePosixPath(value.rstrip("/")).parts):
        return (), "unsafe_path"
    if _is_hosted_application_path(value):
        return (), "hosted_application_boundary"
    if _is_non_authoritative_reference(value):
        return (), "non_authoritative_surface"

    if any(char in value for char in "*?["):
        pattern = value.casefold()
        matches = [
            relative
            for relative in _tracked_inventory(root)
            if fnmatch.fnmatchcase(relative.casefold(), pattern)
            and not _is_hosted_application_path(relative)
            and not _is_non_authoritative_reference(relative)
        ]
        return tuple(sorted(set(matches), key=str.casefold)), None if matches else "missing"

    target = root / value.rstrip("/")
    try:
        exists = target.exists() or target.is_symlink()
    except OSError:
        return (), "unreadable"
    if not exists:
        return (), "missing"
    try:
        resolved = target.resolve(strict=False)
        resolved.relative_to(root)
    except (OSError, ValueError):
        return (), "path_escape"
    return (value.rstrip("/"),), None


def observe_capability_inventory(project_root: Path, _snapshot: RegistrySnapshot, _db_path: Path) -> ObserverResult:
    observer: ObserverClass = "capability_inventory"
    try:
        from scripts.check_harness_parity import capability_artifact_observations

        rows = capability_artifact_observations(project_root)
        observations: list[ArtifactObservation] = []
        diagnostics: list[str] = []
        for row in rows:
            paths, status = _normalize_present_paths(project_root, str(row["path"]))
            if status not in {None, "missing"}:
                diagnostics.append(f"{row['path']}: {status}")
            for relative in paths:
                observations.append(
                    ArtifactObservation(
                        relative_path=relative,
                        observer_class=observer,
                        evidence_source=str(row["source"]),
                        reason=str(row["reason"]),
                    )
                )
        return _result(observer, input_rows=rows, observations=observations, diagnostics=diagnostics)
    except Exception as exc:  # noqa: BLE001 - a failed required observer is explicit evidence.
        return _result(
            observer,
            input_rows={"error": type(exc).__name__, "detail": str(exc)},
            diagnostics=(f"{type(exc).__name__}: {exc}",),
            succeeded=False,
        )


def observe_governed_knowledge(project_root: Path, _snapshot: RegistrySnapshot, db_path: Path) -> ObserverResult:
    observer: ObserverClass = "governed_knowledge"
    try:
        db = KnowledgeDB(db_path=db_path)
        rows = db.list_registry_path_observations()
        observations: list[ArtifactObservation] = []
        diagnostics: list[str] = []
        for row in rows:
            paths, status = _normalize_present_paths(project_root, str(row["path"]))
            if status not in {None, "missing", "hosted_application_boundary", "non_authoritative_surface"}:
                diagnostics.append(f"{row['path']}: {status}")
            for relative in paths:
                observations.append(
                    ArtifactObservation(
                        relative_path=relative,
                        observer_class=observer,
                        evidence_source=f"{row['source_kind']}:{row['source_id']}:{row['field']}",
                        reason="current governed knowledge path field",
                    )
                )
        return _result(observer, input_rows=rows, observations=observations, diagnostics=diagnostics)
    except Exception as exc:  # noqa: BLE001
        return _result(
            observer,
            input_rows={"error": type(exc).__name__, "detail": str(exc)},
            diagnostics=(f"{type(exc).__name__}: {exc}",),
            succeeded=False,
        )


def _package_worktree_files(project_root: Path, roots: Sequence[str]) -> tuple[str, ...] | None:
    inventory = _git_managed_inventory(project_root)
    if inventory is None:
        return None
    prefixes = tuple(root.rstrip("/") + "/" for root in roots)
    exact = set(roots)
    return tuple(
        sorted(
            {item for item in inventory if item in exact or item.startswith(prefixes)},
            key=str.casefold,
        )
    )


def _package_selected_roots(project_root: Path) -> tuple[tuple[str, ...], list[dict[str, Any]]]:
    selected: set[str] = set()
    inputs: list[dict[str, Any]] = []
    pyprojects = (project_root / "pyproject.toml", project_root / "groundtruth-kb" / "pyproject.toml")
    for path in pyprojects:
        if not path.is_file():
            continue
        payload = path.read_bytes()
        data = tomllib.loads(payload.decode("utf-8"))
        base = path.parent
        base_relative = "" if base == project_root else _relative(project_root, base)
        inputs.append({"path": _relative(project_root, path), "sha256": _sha256_bytes(payload)})

        pytest_paths = (((data.get("tool") or {}).get("pytest") or {}).get("ini_options") or {}).get("testpaths") or []
        for item in pytest_paths:
            relative = "/".join(part for part in (base_relative, str(item).replace("\\", "/")) if part)
            selected.add(relative.rstrip("/"))

        hatch_targets = (((data.get("tool") or {}).get("hatch") or {}).get("build") or {}).get("targets") or {}
        hatch = hatch_targets.get("wheel") or {}
        for item in hatch.get("packages") or []:
            relative = "/".join(part for part in (base_relative, str(item).replace("\\", "/")) if part)
            selected.add(relative.rstrip("/"))
        for item in hatch.get("force-include") or {}:
            relative = "/".join(part for part in (base_relative, str(item).replace("\\", "/")) if part)
            selected.add(relative.rstrip("/"))

        scripts = (data.get("project") or {}).get("scripts") or {}
        source_roots = [item for item in selected if item.startswith(base_relative + "/src/")]
        for target in scripts.values():
            module = str(target).partition(":")[0]
            module_path = module.replace(".", "/") + ".py"
            for source_root in source_roots:
                package_parent = PurePosixPath(source_root).parent.as_posix()
                selected.add(f"{package_parent}/{module_path}")

    normalized = tuple(sorted((item for item in selected if item), key=str.casefold))
    return normalized, inputs


def observe_package_and_entrypoint(project_root: Path, _snapshot: RegistrySnapshot, _db_path: Path) -> ObserverResult:
    observer: ObserverClass = "package_and_entrypoint"
    try:
        _GIT_MANAGED_INVENTORY_CACHE.pop(project_root.resolve(), None)
        selected_roots, inputs = _package_selected_roots(project_root)
        files = _package_worktree_files(project_root, selected_roots)
        if files is None:
            return _result(
                observer,
                input_rows={"metadata": inputs, "selected_roots": list(selected_roots)},
                diagnostics=("Git-managed inventory unavailable; package admission is disabled",),
                succeeded=False,
            )
        source = "git_index_and_untracked_nonignored_enumeration"
        observations: list[ArtifactObservation] = []
        for relative in selected_roots:
            paths, _ = _normalize_present_paths(project_root, relative)
            for path in paths:
                observations.append(
                    ArtifactObservation(path, observer, f"package_metadata:{relative}", "selected package or test root")
                )
        for relative in files:
            paths, status = _normalize_present_paths(project_root, relative)
            if status is not None:
                continue
            for path in paths:
                observations.append(
                    ArtifactObservation(path, observer, source, "member of a build-selected source or test tree")
                )
        input_rows = {
            "metadata": inputs,
            "selected_roots": list(selected_roots),
            "files": list(files),
            "source": source,
        }
        return _result(observer, input_rows=input_rows, observations=observations)
    except Exception as exc:  # noqa: BLE001
        return _result(
            observer,
            input_rows={"error": type(exc).__name__, "detail": str(exc)},
            diagnostics=(f"{type(exc).__name__}: {exc}",),
            succeeded=False,
        )


def _iter_structured_path_values(value: Any, *, key: str = "") -> Iterable[tuple[str, str]]:
    if isinstance(value, Mapping):
        for child_key, child_value in value.items():
            yield from _iter_structured_path_values(child_value, key=str(child_key))
    elif isinstance(value, list):
        for child in value:
            yield from _iter_structured_path_values(child, key=key)
    elif isinstance(value, str) and _PATH_KEY_RE.search(key):
        yield key, value


def _text_path_references(text: str) -> Iterable[str]:
    for match in _BACKTICK_PATH_RE.finditer(text):
        yield _clean_reference(match.group(1))
    for match in _PATH_TOKEN_RE.finditer(text):
        candidate = _clean_reference(match.group(1))
        if "/" in candidate or "\\" in candidate:
            yield candidate


def observe_registered_dependency_closure(
    project_root: Path,
    snapshot: RegistrySnapshot,
    _db_path: Path,
    *,
    seed_paths: Iterable[str] = (),
) -> ObserverResult:
    observer: ObserverClass = "registered_dependency_closure"
    try:
        _artifacts, _by_path, _missing, expansions = registered_artifact_inventory(project_root, snapshot=snapshot)
        records_by_id = {record.id: record for record in snapshot.records}
        observations: list[ArtifactObservation] = []
        input_files: list[dict[str, str]] = []
        proposed_container_sources: dict[str, Path] = {}

        approval_root = project_root / ".groundtruth" / "formal-artifact-approvals"
        if approval_root.is_dir():
            observations.append(
                ArtifactObservation(
                    ".groundtruth/formal-artifact-approvals",
                    observer,
                    "managed_service_container:formal-artifact-approvals",
                    "immutable formal-approval audit service container",
                )
            )
            for path in sorted(approval_root.rglob("*"), key=lambda item: item.as_posix().casefold()):
                if path.is_file() and path.suffix.casefold() in _TEXT_SUFFIXES:
                    proposed_container_sources[_relative(project_root, path)] = path
        database = project_root / "groundtruth.db"
        if database.is_file():
            observations.append(
                ArtifactObservation(
                    "groundtruth.db",
                    observer,
                    "service_identity:groundtruth-kb-membase",
                    "load-bearing opaque MemBase service identity",
                )
            )

        for record in snapshot.records:
            for dependency in record.depends_on:
                target = records_by_id.get(dependency)
                raw = target.storage_path if target is not None else dependency
                paths, _ = _normalize_present_paths(project_root, raw)
                for relative in paths:
                    observations.append(
                        ArtifactObservation(
                            relative,
                            observer,
                            f"registry:{record.id}:depends_on",
                            "declared registry dependency",
                        )
                    )

        source_files: dict[str, Path] = dict(proposed_container_sources)
        for expansion in expansions:
            record = records_by_id.get(expansion.artifact.id)
            if (
                record is None
                or record.lifecycle != "active"
                or record.domain in {"runtime_state", "operational_notepad"}
            ):
                continue
            if _is_skipped_dependency_source(record.storage_path):
                continue
            for path in expansion.files:
                if path.suffix.casefold() in _TEXT_SUFFIXES:
                    source_files[_relative(project_root, path)] = path

        normalized_seeds = sorted(
            {relative for raw in seed_paths for relative in _normalize_present_paths(project_root, raw)[0]},
            key=str.casefold,
        )
        typed_seed_paths = {relative.casefold() for relative in normalized_seeds}
        for relative in normalized_seeds:
            path = project_root / relative
            if (
                not _is_skipped_dependency_source(relative)
                and path.is_file()
                and path.suffix.casefold() in _TEXT_SUFFIXES
            ):
                source_files.setdefault(relative, path)

        pending = [(relative.casefold(), relative) for relative in source_files]
        heapq.heapify(pending)
        processed: set[str] = set()
        while pending:
            _folded, relative = heapq.heappop(pending)
            if relative.casefold() in processed:
                continue
            processed.add(relative.casefold())
            path = source_files[relative]
            try:
                payload = path.read_bytes()
            except OSError:
                continue
            if len(payload) > 2_000_000:
                continue
            try:
                text = payload.decode("utf-8")
            except UnicodeDecodeError:
                continue
            input_files.append({"path": relative, "sha256": _sha256_bytes(payload)})
            raw_references = set(_text_path_references(text))
            if path.suffix.casefold() in {".json", ".toml"}:
                try:
                    structured = json.loads(text) if path.suffix.casefold() == ".json" else tomllib.loads(text)
                    raw_references.update(value for _key, value in _iter_structured_path_values(structured))
                except (json.JSONDecodeError, tomllib.TOMLDecodeError):
                    pass
            for raw in sorted(raw_references, key=str.casefold):
                # A wildcard in a registered policy describes that policy's
                # matching scope; it does not prove every current match is a
                # separate load-bearing dependency. Typed package/governed
                # observers own wildcard expansion where the field semantics
                # explicitly establish that relationship.
                if any(char in raw for char in "*?["):
                    continue
                paths, _ = _normalize_present_paths(project_root, raw)
                for target in paths:
                    if _is_opaque_payload(snapshot, target) or not _is_authoritative_dependency_target(
                        project_root,
                        target,
                        typed_seed_paths=typed_seed_paths,
                    ):
                        continue
                    observations.append(
                        ArtifactObservation(
                            target,
                            observer,
                            f"registered_text:{relative}",
                            "deterministic in-root reference from a typed load-bearing artifact",
                        )
                    )
                    target_path = project_root / target
                    if (
                        target.casefold() not in processed
                        and target not in source_files
                        and not _is_skipped_dependency_source(target)
                        and target_path.is_file()
                        and target_path.suffix.casefold() in _TEXT_SUFFIXES
                    ):
                        source_files[target] = target_path
                        heapq.heappush(pending, (target.casefold(), target))

        input_rows = {
            "registry_generation": snapshot.generation_digest,
            "seed_paths": normalized_seeds,
            "source_files": input_files,
            "dependency_rows": [
                {"id": record.id, "depends_on": list(record.depends_on)}
                for record in sorted(snapshot.records, key=lambda item: item.id)
                if record.depends_on
            ],
        }
        return _result(observer, input_rows=input_rows, observations=observations)
    except Exception as exc:  # noqa: BLE001
        return _result(
            observer,
            input_rows={"error": type(exc).__name__, "detail": str(exc)},
            diagnostics=(f"{type(exc).__name__}: {exc}",),
            succeeded=False,
        )


def _object_kind(mode: int, *, reparse: bool) -> str:
    if reparse:
        return "reparse_point"
    if stat.S_ISLNK(mode):
        return "symlink"
    if stat.S_ISDIR(mode):
        return "directory"
    if stat.S_ISREG(mode):
        return "file"
    return "other"


def _is_reparse(info: os.stat_result) -> bool:
    attributes = int(getattr(info, "st_file_attributes", 0))
    return bool(attributes & int(getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)))


def _physical_observer_result(project_root: Path, ancestor_paths: Iterable[str]) -> ObserverResult:
    observer: ObserverClass = "physical_census"
    try:
        rows: list[dict[str, Any]] = []
        with os.scandir(project_root) as iterator:
            for item in sorted(iterator, key=lambda entry: entry.name.casefold()):
                try:
                    info = item.stat(follow_symlinks=False)
                    rows.append(
                        {
                            "name": item.name,
                            "kind": _object_kind(info.st_mode, reparse=_is_reparse(info)),
                            "size": info.st_size if stat.S_ISREG(info.st_mode) else None,
                        }
                    )
                except OSError as exc:
                    rows.append({"name": item.name, "error": f"{type(exc).__name__}:{exc}"})
        return ObserverResult(
            observer_class=observer,
            succeeded=True,
            input_digest=_digest(rows),
            observations=(),
            ancestor_paths=tuple(sorted(set(ancestor_paths), key=str.casefold)),
        )
    except OSError as exc:
        return _result(
            observer,
            input_rows={"error": type(exc).__name__, "detail": str(exc)},
            diagnostics=(f"{type(exc).__name__}: {exc}",),
            succeeded=False,
        )


def _membership_census(
    project_root: Path,
    snapshot: RegistrySnapshot,
    observer_results: Sequence[ObserverResult],
    *,
    deep: bool,
) -> tuple[tuple[MembershipEntry, ...], set[str]]:
    observed: dict[str, list[ArtifactObservation]] = defaultdict(list)
    ancestor_maps: list[set[str]] = []
    for result in observer_results:
        ancestor_maps.append({path.casefold() for path in result.ancestor_paths})
        for item in result.observations:
            observed[item.relative_path.casefold()].append(item)

    if not all(result.succeeded for result in observer_results):
        failed = sorted(result.observer_class for result in observer_results if not result.succeeded)
        return (
            MembershipEntry(
                relative_path=".",
                object_kind="project_root",
                membership_class="invalid_unknown",
                traversal_state="pruned_uninspected_subtree",
                descendants_inspected=False,
                detail=f"required observers failed: {failed}",
            ),
        ), set()

    entries: list[MembershipEntry] = []
    seen: set[str] = set()

    def operative_descendant(relative: str) -> bool:
        folded = relative.casefold()
        return snapshot.resolver.is_structural_ancestor(relative) or any(
            folded in ancestors for ancestors in ancestor_maps
        )

    def classify(relative: str, kind: str) -> tuple[MembershipClass, str | None, tuple[str, ...], tuple[str, ...]]:
        try:
            record = snapshot.resolver.resolve(relative)
        except RegistryCoverageError as exc:
            return "invalid_unknown", None, (), (str(exc),)
        observations = observed.get(relative.casefold(), [])
        if record is not None:
            return (
                "registered",
                record.id,
                tuple(sorted({item.observer_class for item in observations})),
                tuple(sorted({item.evidence_source for item in observations})),
            )
        if observations and (kind != "directory" or relative in _RECURSIVE_SERVICE_CONTAINER_ROOTS):
            return (
                "unregistered_load_bearing",
                None,
                tuple(sorted({item.observer_class for item in observations})),
                tuple(sorted({item.evidence_source for item in observations})),
            )
        return "unregistered_disposable", None, (), ()

    def unreadable_entry(relative: str, exc: OSError) -> MembershipEntry:
        membership, registry_id, observer_classes, evidence_sources = classify(relative, "unreadable")
        if membership == "registered":
            membership = "invalid_unknown"
        return MembershipEntry(
            relative,
            "unreadable",
            membership,
            "inspected",
            False,
            registry_id,
            observer_classes,
            evidence_sources,
            detail=f"{type(exc).__name__}: {exc}",
        )

    def walk(directory: Path) -> None:
        try:
            iterator = os.scandir(directory)
            children = sorted(iterator, key=lambda item: item.name.casefold())
            iterator.close()
        except OSError as exc:
            relative = _relative(project_root, directory)
            entries.append(unreadable_entry(relative, exc))
            seen.add(relative.casefold())
            return
        for child in children:
            path = Path(child.path)
            relative = _relative(project_root, path)
            seen.add(relative.casefold())
            try:
                info = child.stat(follow_symlinks=False)
            except OSError as exc:
                entries.append(unreadable_entry(relative, exc))
                continue
            reparse = _is_reparse(info)
            kind = _object_kind(info.st_mode, reparse=reparse)
            membership, registry_id, observer_classes, evidence_sources = classify(relative, kind)

            if relative == ".git":
                entries.append(
                    MembershipEntry(
                        relative,
                        kind,
                        membership,
                        "owned_service_boundary",
                        False,
                        registry_id,
                        observer_classes,
                        evidence_sources,
                    )
                )
                continue
            parts = PurePosixPath(relative).parts
            if len(parts) == 2 and parts[0].casefold() == "applications" and kind == "directory":
                entries.append(
                    MembershipEntry(
                        relative,
                        "hosted_application_root",
                        membership,
                        "hosted_application_boundary",
                        False,
                        registry_id,
                        observer_classes,
                        evidence_sources,
                    )
                )
                continue
            if kind in {"symlink", "reparse_point", "other"}:
                entries.append(
                    MembershipEntry(
                        relative,
                        kind,
                        membership,
                        "no_follow_boundary",
                        False,
                        registry_id,
                        observer_classes,
                        evidence_sources,
                    )
                )
                continue

            record = snapshot.resolver.resolve(relative)
            if (
                kind == "directory"
                and record is not None
                and record.coverage_mode == "opaque_container"
                and not operative_descendant(relative)
            ):
                entries.append(
                    MembershipEntry(
                        relative,
                        kind,
                        membership,
                        "owned_service_boundary",
                        False,
                        registry_id,
                        observer_classes,
                        evidence_sources,
                    )
                )
                continue
            if kind == "directory":
                must_descend = (
                    deep
                    or operative_descendant(relative)
                    or (record is not None and record.coverage_mode == "recursive")
                )
                if not must_descend:
                    entries.append(
                        MembershipEntry(
                            relative,
                            kind,
                            membership,
                            "pruned_uninspected_subtree",
                            False,
                            registry_id,
                            observer_classes,
                            evidence_sources,
                        )
                    )
                    continue
                state: TraversalState = (
                    "structural_ancestor" if membership == "unregistered_disposable" else "inspected"
                )
                entries.append(
                    MembershipEntry(
                        relative,
                        kind,
                        membership,
                        state,
                        True,
                        registry_id,
                        observer_classes,
                        evidence_sources,
                    )
                )
                walk(path)
                continue
            entries.append(
                MembershipEntry(
                    relative,
                    kind,
                    membership,
                    "inspected",
                    True,
                    registry_id,
                    observer_classes,
                    evidence_sources,
                )
            )

    walk(project_root)

    for record in snapshot.records:
        if record.lifecycle != "active" or record.coverage_mode == "virtual":
            continue
        locator = record.storage_path.rstrip("/")
        if record.coverage_mode == "glob":
            try:
                present = any(project_root.glob(record.storage_path))
            except (OSError, ValueError):
                present = False
        else:
            target = project_root / locator
            present = target.exists() or target.is_symlink()
        if not present and locator.casefold() not in seen:
            entries.append(
                MembershipEntry(
                    locator,
                    "missing_registered_object",
                    "invalid_unknown",
                    "inspected",
                    False,
                    registry_id=record.id,
                    detail="active registry declaration does not resolve to a present object",
                )
            )

    for relative, observations in observed.items():
        if relative in seen:
            continue
        entries.append(
            MembershipEntry(
                observations[0].relative_path,
                "observer_path_not_reached",
                "invalid_unknown",
                "inspected",
                False,
                observer_classes=tuple(sorted({item.observer_class for item in observations})),
                evidence_sources=tuple(sorted({item.evidence_source for item in observations})),
                detail="present observer path was hidden by a traversal boundary",
            )
        )

    ordered = tuple(sorted(entries, key=lambda item: (item.relative_path.casefold(), item.object_kind)))
    return ordered, seen


def _git_managed_paths(project_root: Path) -> dict[str, str]:
    inventory = _git_managed_inventory(project_root)
    if inventory is None:
        return _tracked_canonical_paths(project_root)
    return {item.casefold(): item for item in inventory}


def _candidate_id(relative: str) -> str:
    stem = re.sub(r"[^a-z0-9]+", "-", relative.casefold()).strip("-")
    suffix = hashlib.sha256(relative.encode("utf-8")).hexdigest()[:10]
    return f"wi5441-member-{stem[:48]}-{suffix}"


def _candidate_domain(relative: str) -> str:
    folded = relative.casefold()
    if folded == "groundtruth.db":
        return "specifications"
    if folded.startswith("bridge/"):
        return "bridge_protocol"
    if folded.endswith(".md") and folded.startswith((".claude/rules/", "docs/")):
        return "narrative_authority"
    if "/test" in folded or folded.startswith("platform_tests/") or folded.startswith("tests/"):
        return "governance_policy"
    if folded.startswith(("harness-state/", ".claude/session/")):
        return "harness_state"
    return "control_surface"


def _candidate_record(relative: str, *, object_kind: str, git_managed: bool, observers: Sequence[str]) -> SoTArtifact:
    if relative == "groundtruth.db":
        return SoTArtifact(
            id=_candidate_id(relative),
            domain="specifications",
            lifecycle="active",
            storage_path=relative,
            authority_spec_id="GOV-PLATFORM-SOT-REGISTRY-001",
            mutation_api="groundtruth_kb.db.KnowledgeDB service ledger",
            versioning_policy="append_only_versioned",
            backup_policy="membase_export",
            health_check_function="_check_db_schema",
            owner_role="automated_only",
            restore_action="membase_export_restore",
            notes="WI-5441 service-owned opaque database identity; internal payload lifecycle remains in MemBase.",
            coverage_mode="opaque_container",
        )
    if relative in _RECURSIVE_SERVICE_CONTAINER_ROOTS:
        return SoTArtifact(
            id=_candidate_id(relative),
            domain="governance_policy",
            lifecycle="active",
            storage_path=relative + "/",
            authority_spec_id="GOV-ARTIFACT-APPROVAL-001",
            mutation_api="formal artifact approval packet writer",
            versioning_policy="immutable_archive",
            backup_policy="external_backup",
            health_check_function="",
            owner_role="automated_only",
            restore_action="manual",
            notes="WI-5441 narrow recursive service container for immutable formal-approval audit packets.",
            coverage_mode="recursive",
        )
    immutable_approval = relative.casefold().startswith(".groundtruth/formal-artifact-approvals/")
    versioning = (
        "git_tracked" if git_managed else "immutable_archive" if immutable_approval else "overwrite_single_writer"
    )
    backup = "git_tracked" if git_managed else "external_backup" if immutable_approval else "gitignored_runtime"
    restore = "git_restore" if git_managed else "manual" if immutable_approval else "regenerate_from_source"
    owner = "automated_only" if immutable_approval else "shared"
    mutation_api = (
        "formal artifact approval packet writer"
        if immutable_approval
        else "Governed bridge-authorized source edit; direct owner in-place content edit remains valid"
    )
    return SoTArtifact(
        id=_candidate_id(relative),
        domain=_candidate_domain(relative),
        lifecycle="active",
        storage_path=relative,
        authority_spec_id="GOV-PLATFORM-SOT-REGISTRY-001",
        mutation_api=mutation_api,
        versioning_policy=versioning,
        backup_policy=backup,
        health_check_function="",
        owner_role=owner,
        restore_action=restore,
        notes=f"Deterministically admitted by WI-5441 observers: {', '.join(sorted(observers))}.",
        coverage_mode="exact",
    )


def _admission_candidates(
    entries: Sequence[MembershipEntry],
    observations: Mapping[str, Sequence[ArtifactObservation]],
    *,
    project_root: Path,
) -> tuple[AdmissionCandidate, ...]:
    git_managed = _git_managed_paths(project_root)
    candidates: list[AdmissionCandidate] = []
    for entry in entries:
        if entry.membership_class != "unregistered_load_bearing":
            continue
        if entry.object_kind == "unreadable":
            continue
        evidence = observations.get(entry.relative_path.casefold(), ())
        observers = tuple(sorted({item.observer_class for item in evidence}))
        sources = tuple(sorted({item.evidence_source for item in evidence}))
        reasons = tuple(sorted({item.reason for item in evidence}))
        canonical_relative = git_managed.get(entry.relative_path.casefold(), entry.relative_path)
        candidates.append(
            AdmissionCandidate(
                record=_candidate_record(
                    canonical_relative,
                    object_kind=entry.object_kind,
                    git_managed=entry.relative_path.casefold() in git_managed,
                    observers=observers,
                ),
                observer_classes=observers,
                evidence_sources=sources,
                reasons=reasons,
            )
        )
    return tuple(sorted(candidates, key=lambda item: item.record.storage_path.casefold()))


DEFAULT_OBSERVERS: tuple[Callable[[Path, RegistrySnapshot, Path], ObserverResult], ...] = (
    observe_capability_inventory,
    observe_governed_knowledge,
    observe_package_and_entrypoint,
    observe_registered_dependency_closure,
)


def reconcile_artifact_membership(
    project_root: Path,
    *,
    snapshot: RegistrySnapshot | None = None,
    db_path: Path | None = None,
    observers: Sequence[Callable[[Path, RegistrySnapshot, Path], ObserverResult]] | None = None,
    observer_results: Sequence[ObserverResult] | None = None,
    deep: bool = False,
    audit: bool = False,
) -> dict[str, Any]:
    """Return one shared membership report without mutating registry state."""

    root = project_root.resolve()
    _TRACKED_INVENTORY_CACHE.pop(root, None)
    _TRACKED_CANONICAL_CACHE.pop(root, None)
    _GIT_MANAGED_INVENTORY_CACHE.pop(root, None)
    _REFERENCE_RESOLUTION_CACHE.clear()
    database = (db_path or root / "groundtruth.db").resolve()
    coherent = snapshot or load_registry_snapshot(project_root=root, db_path=database)
    if observer_results is None:
        if observers is None:
            capability = observe_capability_inventory(root, coherent, database)
            governed = observe_governed_knowledge(root, coherent, database)
            package = observe_package_and_entrypoint(root, coherent, database)
            seeds = {item.relative_path for result in (capability, governed, package) for item in result.observations}
            dependency = observe_registered_dependency_closure(
                root,
                coherent,
                database,
                seed_paths=seeds,
            )
            collected = [capability, governed, package, dependency]
        else:
            collected = [adapter(root, coherent, database) for adapter in observers]
        collected = [_without_opaque_payload_observations(result, coherent) for result in collected]
        all_ancestors = {path for result in collected for path in result.ancestor_paths}
        all_ancestors.update(
            ancestor
            for record in coherent.records
            if record.coverage_mode != "virtual"
            for ancestor in _ancestors(record.storage_path.rstrip("/"))
        )
        collected.append(_physical_observer_result(root, all_ancestors))
    else:
        collected = [_without_opaque_payload_observations(result, coherent) for result in observer_results]

    by_class = {result.observer_class: result for result in collected}
    for required in REQUIRED_OBSERVER_CLASSES:
        if required not in by_class:
            collected.append(
                _result(
                    required,
                    input_rows={"error": "observer_not_supplied"},
                    diagnostics=("required observer was not supplied",),
                    succeeded=False,
                )
            )
    collected = sorted(collected, key=lambda item: REQUIRED_OBSERVER_CLASSES.index(item.observer_class))

    observations: dict[str, list[ArtifactObservation]] = defaultdict(list)
    for result in collected:
        for item in result.observations:
            observations[item.relative_path.casefold()].append(item)
    entries, _seen = _membership_census(root, coherent, collected, deep=deep)
    all_succeeded = all(result.succeeded for result in collected)
    candidates = _admission_candidates(entries, observations, project_root=root) if all_succeeded else ()

    counts: dict[str, int] = {
        name: 0
        for name in (
            "registered",
            "unregistered_load_bearing",
            "unregistered_disposable",
            "invalid_unknown",
        )
    }
    traversal_counts: dict[str, int] = defaultdict(int)
    for entry in entries:
        counts[entry.membership_class] += 1
        traversal_counts[entry.traversal_state] += 1

    if audit:
        currentness = registry_currentness(coherent, project_root=root, db_path=database)
        audit_gaps = [
            *({"kind": "missing_revision", "registry_id": item} for item in currentness["missing_revisions"]),
            *({"kind": "stale_content_observation", **item} for item in currentness["stale"]),
        ]
    else:
        currentness = {"current": None, "missing_revisions": [], "stale": []}
        audit_gaps = [{"kind": "audit_not_performed"}]
    membership_complete = bool(
        all_succeeded and not candidates and counts["unregistered_load_bearing"] == 0 and counts["invalid_unknown"] == 0
    )
    pruned = traversal_counts.get("pruned_uninspected_subtree", 0)

    manifest_rows = [candidate.as_dict() for candidate in candidates]
    batch_records = [row["record"] for row in manifest_rows]
    evidence_rows = [entry.as_dict() for entry in entries]
    root_attribution: dict[str, int] = defaultdict(int)
    for entry in entries:
        if entry.membership_class == "invalid_unknown":
            top = PurePosixPath(entry.relative_path).parts[0] if entry.relative_path not in {"", "."} else "."
            root_attribution[top] += 1

    return {
        "schema_version": 1,
        "project_root": str(root),
        "deep_census": deep,
        "registry_generation_digest": coherent.generation_digest,
        "registry_record_count": len(coherent.records),
        "observers": [result.as_dict() for result in collected],
        "observer_input_digests": {result.observer_class: result.input_digest for result in collected},
        "counts": counts,
        "traversal_counts": dict(sorted(traversal_counts.items())),
        "entries": evidence_rows,
        "unknown_root_attribution": dict(sorted(root_attribution.items())),
        "admission_candidates": manifest_rows,
        "batch_records": batch_records,
        "candidate_manifest_sha256": _digest(manifest_rows),
        "reconciliation_evidence_digest": _digest(evidence_rows),
        "membership_complete": membership_complete,
        "audit_complete": not audit_gaps,
        "audit_performed": audit,
        "audit_gaps": audit_gaps,
        "operational_liveness": True,
        "pruned_envelope_count": pruned,
        "sweep_eligible": bool(membership_complete and currentness["current"] and pruned == 0),
        "release_eligible": bool(membership_complete and pruned == 0),
    }


def reconciliation_summary(report: Mapping[str, Any]) -> dict[str, Any]:
    """Return the bounded shared view embedded by inspect/doctor/gates."""

    return {
        key: report[key]
        for key in (
            "schema_version",
            "registry_generation_digest",
            "registry_record_count",
            "observer_input_digests",
            "counts",
            "traversal_counts",
            "unknown_root_attribution",
            "candidate_manifest_sha256",
            "reconciliation_evidence_digest",
            "membership_complete",
            "audit_complete",
            "audit_performed",
            "audit_gaps",
            "operational_liveness",
            "pruned_envelope_count",
            "sweep_eligible",
            "release_eligible",
        )
    }
