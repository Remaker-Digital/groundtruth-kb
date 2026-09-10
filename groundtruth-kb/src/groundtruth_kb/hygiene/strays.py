"""Read-only work-tree, stash, and worktree stray collection for WI-4356.

This module is the package-side adapter for the verified Slice A detector in
``scripts.hygiene.stray_detector``. It gathers fresh live state from git,
normalizes it into detector dataclasses, and emits dry-run recommendations only.
It does not execute cleanup actions or mutate MemBase, bridge, GOV, SPEC, ADR,
DCL, stash, commit, or workspace state.
"""

from __future__ import annotations

import fnmatch
import hashlib
import json
import os
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from scripts.hygiene.stray_detector import (
    STALE_THRESHOLD_HOURS,
    ActiveSessionContext,
    StashEntry,
    WorkspaceEntry,
    WorktreeEntry,
    detect_strays,
)

from groundtruth_kb.hygiene.auto_resolve import AutoResolveError, build_plan, summarize_plan
from groundtruth_kb.project.sot_registry import InvalidSoTRecord, UnknownDomain, default_registry_path, load_toml


class StraysError(RuntimeError):
    """Raised when live git state cannot be collected safely."""


def parse_now(value: str | None = None) -> datetime:
    """Return a timezone-aware UTC datetime from an ISO string or current time."""
    if value is None:
        return datetime.now(UTC)
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        raise StraysError("--now must include timezone information")
    return parsed.astimezone(UTC)


def _run_git(root: Path, args: list[str]) -> str:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=15,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise StraysError(f"git {args[0]} unavailable or exceeded the 15-second read bound") from error
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip()
        raise StraysError(f"git {' '.join(args)} failed: {detail}")
    return result.stdout


def _repo_relative(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def _path_mtime(root: Path, rel_path: str, *, fallback: datetime) -> datetime:
    candidate = root / rel_path
    try:
        stat = candidate.stat()
    except OSError:
        return fallback
    return datetime.fromtimestamp(stat.st_mtime, UTC)


def _latest_tree_mtime(path: Path) -> datetime:
    latest = path.stat().st_mtime
    for directory, dirnames, filenames in os.walk(path):
        for name in [*dirnames, *filenames]:
            candidate = Path(directory) / name
            try:
                latest = max(latest, candidate.stat().st_mtime)
            except OSError:
                continue
    return datetime.fromtimestamp(latest, UTC)


def _content_hash(path: Path) -> str | None:
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError:
        return None
    return "sha256:" + digest.hexdigest()


def _normalize_status_path(path: str) -> str:
    return path.replace("\\", "/")


def _glob_has_magic(pattern: str) -> bool:
    return any(ch in pattern for ch in "*?[")


def _load_active_registry_records(root: Path) -> tuple[Any, ...]:
    registry_path = default_registry_path(root)
    if not registry_path.is_file():
        return ()
    try:
        return tuple(record for record in load_toml(registry_path) if record.lifecycle == "active")
    except (InvalidSoTRecord, UnknownDomain, OSError) as exc:
        raise StraysError(f"SoT artifact registry could not be loaded: {exc}") from exc


def _registry_storage_path(record: Any) -> str:
    return str(record.storage_path).strip().replace("\\", "/")


def _registered_artifact_ids_for_path(rel_path: str, records: tuple[Any, ...]) -> tuple[str, ...]:
    ids: list[str] = []
    for record in records:
        storage = _registry_storage_path(record)
        if not storage or storage.startswith("membase:") or Path(storage).is_absolute():
            continue
        if _glob_has_magic(storage):
            matched = fnmatch.fnmatch(rel_path, storage)
        elif storage.endswith("/"):
            matched = rel_path.startswith(storage.rstrip("/") + "/")
        else:
            matched = rel_path == storage
        if matched:
            ids.append(str(record.id))
    return tuple(ids)


def _iter_hidden_owner_runtime_artifacts(root: Path, records: tuple[Any, ...]) -> list[tuple[str, tuple[str, ...]]]:
    hidden: list[tuple[str, tuple[str, ...]]] = []
    for record in records:
        storage = _registry_storage_path(record)
        if (
            not storage
            or storage.startswith("membase:")
            or Path(storage).is_absolute()
            or _glob_has_magic(storage)
            or storage.endswith("/")
            or record.backup_policy != "gitignored_runtime"
            or record.owner_role != "owner_only"
        ):
            continue
        candidate = root / storage
        if candidate.is_file():
            hidden.append((storage, _registered_artifact_ids_for_path(storage, records)))
    return hidden


def collect_workspace_entries(
    root: Path,
    *,
    now: datetime,
    registered_artifacts: tuple[Any, ...] = (),
) -> list[WorkspaceEntry]:
    """Collect dirty workspace paths from ``git status --porcelain``."""
    output = _run_git(root, ["status", "--porcelain=v1", "-z", "--untracked-files=all"])
    tokens = output.split("\0")
    entries: list[WorkspaceEntry] = []
    seen_paths: set[str] = set()
    index = 0
    while index < len(tokens):
        token = tokens[index]
        index += 1
        if not token:
            continue
        if len(token) < 4:
            continue
        status = token[:2]
        raw_path = token[3:]
        if not raw_path:
            continue
        rel_path = _normalize_status_path(raw_path)
        tracked = status != "??"
        file_path = root / rel_path
        registered_artifact_ids = _registered_artifact_ids_for_path(rel_path, registered_artifacts)
        seen_paths.add(rel_path)
        entries.append(
            WorkspaceEntry(
                path=rel_path,
                last_modified=_path_mtime(root, rel_path, fallback=now),
                tracked=tracked,
                content_hash=None if registered_artifact_ids else _content_hash(file_path),
                registered_artifact_ids=registered_artifact_ids,
            )
        )
        if "R" in status or "C" in status:
            index += 1
    for rel_path, registered_artifact_ids in _iter_hidden_owner_runtime_artifacts(root, registered_artifacts):
        if rel_path in seen_paths:
            continue
        entries.append(
            WorkspaceEntry(
                path=rel_path,
                last_modified=_path_mtime(root, rel_path, fallback=now),
                tracked=False,
                content_hash=None,
                registered_artifact_ids=registered_artifact_ids,
            )
        )
    return entries


def parse_stash_entries(output: str) -> list[StashEntry]:
    """Parse ``git stash list --format=%gd%x09%ct%x09%gs`` output."""
    entries: list[StashEntry] = []
    for line in output.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t", 2)
        if len(parts) < 2:
            continue
        stash_ref, epoch = parts[0], parts[1]
        subject = parts[2] if len(parts) > 2 else ""
        try:
            created_at = datetime.fromtimestamp(int(epoch), UTC)
        except ValueError:
            continue
        entries.append(StashEntry(stash_ref=stash_ref, created_at=created_at, subject=subject))
    return entries


def collect_stash_entries(root: Path) -> list[StashEntry]:
    output = _run_git(root, ["stash", "list", "--format=%gd%x09%ct%x09%gs"])
    return parse_stash_entries(output)


def _parse_worktree_paths(output: str) -> list[Path]:
    paths: list[Path] = []
    for line in output.splitlines():
        if line.startswith("worktree "):
            paths.append(Path(line.split(" ", 1)[1]))
    return paths


def collect_worktree_entries(root: Path) -> list[WorktreeEntry]:
    """Collect registered worktrees and orphaned ``.claude/worktrees`` dirs."""
    output = _run_git(root, ["worktree", "list", "--porcelain"])
    registered_paths = _parse_worktree_paths(output)
    root_resolved = root.resolve()
    registered_resolved = {path.resolve() for path in registered_paths}
    entries: list[WorktreeEntry] = []
    for path in registered_paths:
        resolved = path.resolve()
        if resolved == root_resolved:
            continue
        if not path.exists():
            continue
        entries.append(
            WorktreeEntry(
                path=_repo_relative(root, path),
                last_modified=_latest_tree_mtime(path),
                git_registered=True,
            )
        )

    harness_worktrees = root / ".claude" / "worktrees"
    if not harness_worktrees.is_dir():
        return entries
    for child in harness_worktrees.iterdir():
        if not child.is_dir():
            continue
        if child.resolve() in registered_resolved:
            continue
        entries.append(
            WorktreeEntry(
                path=_repo_relative(root, child),
                last_modified=_latest_tree_mtime(child),
                git_registered=False,
            )
        )
    return entries


def make_active_session(
    *,
    workspace_paths: tuple[str, ...] = (),
    stash_refs: tuple[str, ...] = (),
) -> ActiveSessionContext | None:
    if not workspace_paths and not stash_refs:
        return None
    normalized_paths = frozenset(_normalize_status_path(path) for path in workspace_paths)
    return ActiveSessionContext(workspace_paths=normalized_paths, stash_refs=frozenset(stash_refs))


def run_strays(
    root: Path,
    *,
    now: datetime | None = None,
    threshold_hours: int = STALE_THRESHOLD_HOURS,
    active_workspace_paths: tuple[str, ...] = (),
    active_stash_refs: tuple[str, ...] = (),
) -> dict[str, Any]:
    """Collect live state and return a JSON-serializable dry-run report."""
    root = root.resolve()
    if threshold_hours <= 0:
        raise StraysError("--threshold-hours must be greater than zero")
    # Git otherwise discovers an ancestor repository and can make an unrelated
    # nested directory trigger a scan of that repository and all its worktrees.
    top_level = Path(_run_git(root, ["rev-parse", "--show-toplevel"]).strip()).resolve()
    if top_level != root:
        raise StraysError("The scan target must be the exact Git checkout root; ancestor discovery is refused")
    now = (now or datetime.now(UTC)).astimezone(UTC)
    registered_artifacts = _load_active_registry_records(root)
    workspace_entries = collect_workspace_entries(root, now=now, registered_artifacts=registered_artifacts)
    stash_entries = collect_stash_entries(root)
    worktree_entries = collect_worktree_entries(root)
    active_session = make_active_session(
        workspace_paths=active_workspace_paths,
        stash_refs=active_stash_refs,
    )
    report = detect_strays(
        now=now,
        workspace_entries=workspace_entries,
        stash_entries=stash_entries,
        worktree_entries=worktree_entries,
        active_session=active_session,
        threshold_hours=threshold_hours,
    )
    try:
        auto_resolve_plan = build_plan(root)
    except AutoResolveError as exc:
        raise StraysError(f"auto-resolve plan could not be built: {exc}") from exc
    report["source"] = {
        "root": str(root),
        "workspace_command": "git status --porcelain=v1 -z --untracked-files=all",
        "stash_command": "git stash list --format=%gd%x09%ct%x09%gs",
        "worktree_command": "git worktree list --porcelain",
        "read_only": True,
        "active_workspace_paths": list(active_workspace_paths),
        "active_stash_refs": list(active_stash_refs),
    }
    report["candidate_actions_only"] = True
    report["auto_resolve_plan"] = auto_resolve_plan
    report["auto_resolve_summary"] = summarize_plan(auto_resolve_plan)
    return report


def stale_count(report: dict[str, Any]) -> int:
    counts = report.get("counts", {})
    return (
        int(counts.get("workspace_stale", 0)) + int(counts.get("stash_stale", 0)) + int(counts.get("worktree_stale", 0))
    )


def format_human(report: dict[str, Any]) -> str:
    counts = report["counts"]
    lines = [
        "work-tree stray scan",
        f"generated_at: {report['generated_at']}",
        f"root: {report['source']['root']}",
        f"threshold_hours: {report['threshold_hours']}",
        (
            "workspace: "
            f"{counts['workspace_total']} total, {counts['workspace_stale']} stale, "
            f"{counts['workspace_active_session']} active-session"
        ),
        (
            "stash: "
            f"{counts['stash_total']} total, {counts['stash_stale']} stale, "
            f"{counts['stash_active_session']} active-session"
        ),
        (
            "worktrees: "
            f"{counts['worktree_total']} total, {counts['worktree_stale']} stale, "
            f"{counts['worktree_registered']} registered, {counts['worktree_active_session']} active-session"
        ),
        "candidate_actions_only: true",
    ]
    auto_summary = report.get("auto_resolve_summary")
    if isinstance(auto_summary, dict):
        action_counts = auto_summary.get("actuator_actions", {})
        actions = "none"
        if isinstance(action_counts, dict) and action_counts:
            actions = ", ".join(f"{key}={value}" for key, value in sorted(action_counts.items()))
        lines.append(f"auto_resolve: dirty_paths={auto_summary.get('dirty_paths', 0)} actions={actions}")
    for key, label, identity in (
        ("workspace_findings", "workspace", "path"),
        ("stash_findings", "stash", "stash_ref"),
        ("worktree_findings", "worktree", "path"),
    ):
        stale = [finding for finding in report[key] if finding["classification"] == "stale"]
        if not stale:
            continue
        lines.append("")
        lines.append(f"stale {label}:")
        for finding in stale:
            lines.append(f"- {finding[identity]} age_hours={finding['age_hours']} action={finding['candidate_action']}")
    return "\n".join(lines) + "\n"


def emit_json(report: dict[str, Any], output_path: Path) -> None:
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def emit_human(report: dict[str, Any], output_path: Path) -> None:
    output_path.write_text(format_human(report), encoding="utf-8")


def write_outputs(report: dict[str, Any], output_dir: Path, fmt: str) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    if fmt in {"json", "both"}:
        path = output_dir / "strays.json"
        emit_json(report, path)
        written.append(path)
    if fmt in {"human", "both"}:
        path = output_dir / "summary.md"
        emit_human(report, path)
        written.append(path)
    return written
