#!/usr/bin/env python3
"""Batch archive-preserve non-finalizable terminal bridge verdicts.

WI-5370 Slice 2 implements the archive-preserve path for terminal bridge
verdict files that are untracked, terminal in their thread, and not eligible
for normal VERIFIED finalization. The service is intentionally conservative:
it copies bytes to a tracked archive path, verifies identity, commits only the
archive paths through a pathspec-limited commit, then removes the untracked
source files after the commit succeeds.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = _SCRIPTS_DIR.parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
_VERIFY_HELPERS = PROJECT_ROOT / ".claude" / "skills" / "verify" / "helpers"
if str(_VERIFY_HELPERS) not in sys.path:
    sys.path.insert(0, str(_VERIFY_HELPERS))

from bridge_thread_files import (  # noqa: E402
    latest_bridge_status_for_thread,
    parse_versioned_bridge_filename,
    status_from_bridge_file,
)
from windows_subprocess import no_window_subprocess_kwargs  # noqa: E402

ARCHIVE_DIR = Path("archive") / "bridge-terminal-verdicts"
AUDIT_DIR = Path(".gtkb-state") / "batch-archive"
TERMINAL_STATUSES = frozenset({"VERIFIED", "WITHDRAWN", "DEFERRED", "ADVISORY"})
DEFAULT_LIMIT = 20
GIT_TIMEOUT_SECONDS = int(os.environ.get("GTKB_BATCH_ARCHIVE_GIT_TIMEOUT_SECONDS", "60"))


@dataclass(frozen=True)
class Candidate:
    source: str
    archive: str
    slug: str
    status: str
    sha256: str
    size: int
    reason: str


@dataclass(frozen=True)
class Skip:
    source: str
    reason: str


@dataclass(frozen=True)
class ArchiveResult:
    source: str
    archive: str
    sha256: str
    size: int


def _now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _rel(path: Path, project_root: Path) -> str:
    return path.resolve().relative_to(project_root.resolve()).as_posix()


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _first_status(path: Path) -> str | None:
    return status_from_bridge_file(path)


def _git(project_root: Path, args: list[str], *, timeout: int | None = None) -> subprocess.CompletedProcess:
    command = ["git", "-C", str(project_root), *args]
    try:
        return subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout if timeout is not None else GIT_TIMEOUT_SECONDS,
            **no_window_subprocess_kwargs(),
        )
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout if isinstance(exc.stdout, str) else ""
        stderr = exc.stderr if isinstance(exc.stderr, str) else ""
        detail = f"git subprocess timed out after {exc.timeout} seconds: {' '.join(command)}"
        return subprocess.CompletedProcess(command, 124, stdout, (stderr + "\n" + detail).strip())


def _untracked_bridge_markdown(project_root: Path) -> list[str]:
    result = _git(project_root, ["ls-files", "--others", "--exclude-standard", "bridge"])
    if result.returncode != 0:
        raise RuntimeError((result.stderr or result.stdout or "git ls-files failed").strip())
    return sorted(
        line.strip().replace("\\", "/") for line in result.stdout.splitlines() if line.strip().endswith(".md")
    )


def _git_blob_hash(project_root: Path, rel_path: str) -> str:
    result = _git(project_root, ["hash-object", "--", rel_path])
    if result.returncode != 0:
        raise RuntimeError((result.stderr or result.stdout or f"git hash-object failed for {rel_path}").strip())
    return result.stdout.strip()


def _validate_verified_body(content: str, project_root: Path) -> tuple[bool, str]:
    try:
        from write_verdict import VerifiedFinalizationError, validate_verified_body  # type: ignore[import-not-found]
    except Exception as exc:  # pragma: no cover - import-environment guard
        return False, f"canonical finalizer validation unavailable: {exc}"
    try:
        validate_verified_body(content, project_root=project_root)
    except VerifiedFinalizationError as exc:
        return False, f"canonical finalizer rejects body: {exc}"
    return True, "valid-bodied VERIFIED is finalizable elsewhere"


def _is_non_finalizable_terminal(path: Path, status: str, project_root: Path) -> tuple[bool, str]:
    if status != "VERIFIED":
        return True, f"{status} is terminal but not a normal VERIFIED finalization candidate"
    content = path.read_text(encoding="utf-8", errors="replace")
    finalizable, reason = _validate_verified_body(content, project_root)
    return (not finalizable), reason


def discover_candidates(
    project_root: Path = PROJECT_ROOT, *, limit: int | None = DEFAULT_LIMIT
) -> tuple[list[Candidate], list[Skip]]:
    bridge_dir = project_root / "bridge"
    candidates: list[Candidate] = []
    skipped: list[Skip] = []
    for rel in _untracked_bridge_markdown(project_root):
        path = project_root / rel
        parsed = parse_versioned_bridge_filename(path.name)
        if parsed is None:
            skipped.append(Skip(rel, "not an exact versioned bridge filename"))
            continue
        slug, _version = parsed
        status = _first_status(path)
        if status not in TERMINAL_STATUSES:
            skipped.append(Skip(rel, f"first status is {status or 'missing'}, not terminal"))
            continue
        latest = latest_bridge_status_for_thread(project_root, slug)
        if latest not in TERMINAL_STATUSES:
            skipped.append(Skip(rel, f"thread latest status is {latest or 'missing'}, not terminal"))
            continue
        non_finalizable, reason = _is_non_finalizable_terminal(path, status, project_root)
        if not non_finalizable:
            skipped.append(Skip(rel, reason))
            continue
        archive_rel = (ARCHIVE_DIR / path.name).as_posix()
        archive_abs = project_root / archive_rel
        if archive_abs.exists():
            skipped.append(Skip(rel, f"archive target already exists: {archive_rel}"))
            continue
        if path.parent != bridge_dir:
            skipped.append(Skip(rel, "candidate is not directly under bridge/"))
            continue
        candidates.append(
            Candidate(
                source=rel,
                archive=archive_rel,
                slug=slug,
                status=status,
                sha256=_sha256(path),
                size=path.stat().st_size,
                reason=reason,
            )
        )
        if limit is not None and len(candidates) >= limit:
            break
    return candidates, skipped


def _copy_bytes(source: Path, archive: Path) -> None:
    archive.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, archive)


def copy_and_verify(candidate: Candidate, project_root: Path = PROJECT_ROOT) -> ArchiveResult:
    source = project_root / candidate.source
    archive = project_root / candidate.archive
    if not candidate.source.startswith("bridge/"):
        raise RuntimeError(f"refusing to archive non-bridge source: {candidate.source}")
    if not candidate.archive.startswith(f"{ARCHIVE_DIR.as_posix()}/"):
        raise RuntimeError(f"refusing archive path outside archive directory: {candidate.archive}")
    if archive.exists():
        raise RuntimeError(f"archive target already exists: {candidate.archive}")
    _copy_bytes(source, archive)
    try:
        if archive.stat().st_size != candidate.size:
            raise RuntimeError("byte length mismatch after archive copy")
        if _sha256(archive) != candidate.sha256:
            raise RuntimeError("sha256 mismatch after archive copy")
        if _git_blob_hash(project_root, candidate.source) != _git_blob_hash(project_root, candidate.archive):
            raise RuntimeError("git blob hash mismatch after archive copy")
    except Exception:
        try:
            archive.unlink()
        except OSError:
            pass
        raise
    return ArchiveResult(candidate.source, candidate.archive, candidate.sha256, candidate.size)


def _index_lock_present(project_root: Path) -> bool:
    return (project_root / ".git" / "index.lock").exists()


def _commit_archives(project_root: Path, archive_paths: list[str]) -> tuple[bool, str]:
    if not archive_paths:
        return True, "nothing to commit"
    if _index_lock_present(project_root):
        return False, ".git/index.lock present"
    if any(not path.startswith(f"{ARCHIVE_DIR.as_posix()}/") for path in archive_paths):
        return False, "refusing to stage non-archive path"
    add = _git(project_root, ["add", "--", *archive_paths])
    if add.returncode != 0:
        return False, f"git add failed: {(add.stderr or add.stdout).strip()}"
    commit = _git(
        project_root,
        ["commit", "-m", "chore(bridge): archive non-finalizable terminal verdicts", "--", *archive_paths],
    )
    if commit.returncode != 0:
        _git(project_root, ["reset", "-q", "HEAD", "--", *archive_paths])
        return False, f"git commit failed: {(commit.stderr or commit.stdout).strip()}"
    show = _git(project_root, ["show", "--name-only", "--format=", "HEAD"])
    if show.returncode != 0:
        return False, f"git show failed after commit: {(show.stderr or show.stdout).strip()}"
    committed = [line.strip().replace("\\", "/") for line in show.stdout.splitlines() if line.strip()]
    unexpected = [path for path in committed if path not in set(archive_paths)]
    if unexpected:
        return False, f"pathspec commit captured unexpected paths: {unexpected}"
    return True, "committed"


def _staged_archive_paths(project_root: Path, archive_paths: list[str]) -> tuple[list[str], str | None]:
    result = _git(project_root, ["diff", "--cached", "--name-only", "--", *archive_paths])
    if result.returncode != 0:
        return [], f"could not inspect staged archive paths: {(result.stderr or result.stdout).strip()}"
    staged = [line.strip().replace("\\", "/") for line in result.stdout.splitlines() if line.strip()]
    return staged, None


def _cleanup_failed_archive_copies(
    project_root: Path,
    copied: list[ArchiveResult],
) -> tuple[list[str], list[str]]:
    archive_prefix = f"{ARCHIVE_DIR.as_posix()}/"
    archive_paths = [result.archive for result in copied]
    errors: list[str] = []
    removed: list[str] = []

    unsafe = [path for path in archive_paths if not path.startswith(archive_prefix)]
    if unsafe:
        return removed, [f"refusing cleanup outside archive directory: {unsafe}"]

    staged, inspect_error = _staged_archive_paths(project_root, archive_paths)
    if inspect_error:
        return removed, [inspect_error]
    if staged:
        reset = _git(project_root, ["reset", "-q", "HEAD", "--", *archive_paths])
        if reset.returncode != 0:
            return removed, [f"could not unstage failed archive paths: {(reset.stderr or reset.stdout).strip()}"]
        staged, inspect_error = _staged_archive_paths(project_root, archive_paths)
        if inspect_error:
            return removed, [inspect_error]
        if staged:
            return removed, [f"failed archive paths remain staged after reset: {staged}"]

    archive_root = (project_root / ARCHIVE_DIR).resolve()
    for result in copied:
        archive = (project_root / result.archive).resolve()
        try:
            archive.relative_to(archive_root)
        except ValueError:
            errors.append(f"refusing cleanup outside archive directory: {result.archive}")
            continue
        if not archive.exists():
            continue
        try:
            if archive.stat().st_size != result.size or _sha256(archive) != result.sha256:
                errors.append(f"preserved changed failed archive copy: {result.archive}")
                continue
            archive.unlink()
            removed.append(result.archive)
        except OSError as exc:
            errors.append(f"could not remove failed archive copy {result.archive}: {exc}")
    return removed, errors


def _write_audit(project_root: Path, event: dict) -> None:
    audit_dir = project_root / AUDIT_DIR
    audit_dir.mkdir(parents=True, exist_ok=True)
    audit_path = audit_dir / f"{datetime.now(UTC).strftime('%Y%m%d')}.jsonl"
    with audit_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"ts": _now(), **event}, ensure_ascii=True, sort_keys=True) + "\n")


def run_batch(
    project_root: Path = PROJECT_ROOT,
    *,
    limit: int | None = DEFAULT_LIMIT,
    dry_run: bool = False,
) -> dict:
    candidates, skipped = discover_candidates(project_root, limit=limit)
    summary: dict = {
        "dry_run": dry_run,
        "limit": limit,
        "candidates": [asdict(candidate) for candidate in candidates],
        "skipped": [asdict(skip) for skip in skipped],
        "archived": [],
        "errors": [],
        "commit": None,
        "cleanup": {"removed": [], "errors": []},
    }
    if dry_run or not candidates:
        if not dry_run and not candidates:
            _write_audit(project_root, {"action": "noop", "summary": summary})
        return summary

    copied: list[ArchiveResult] = []
    try:
        for candidate in candidates:
            copied.append(copy_and_verify(candidate, project_root))
    except Exception as exc:  # noqa: BLE001 - fail closed with sources intact
        summary["errors"].append({"stage": "copy", "reason": str(exc)})
        _write_audit(project_root, {"action": "error", "stage": "copy", "summary": summary})
        return summary

    archive_paths = [result.archive for result in copied]
    ok, reason = _commit_archives(project_root, archive_paths)
    summary["commit"] = {"ok": ok, "reason": reason, "paths": archive_paths}
    if not ok:
        summary["errors"].append({"stage": "commit", "reason": reason})
        removed, cleanup_errors = _cleanup_failed_archive_copies(project_root, copied)
        summary["cleanup"] = {"removed": removed, "errors": cleanup_errors}
        summary["errors"].extend({"stage": "cleanup", "reason": error} for error in cleanup_errors)
        _write_audit(project_root, {"action": "error", "stage": "commit", "summary": summary})
        return summary

    for result in copied:
        source = project_root / result.source
        source.unlink()
        summary["archived"].append(asdict(result))
    _write_audit(project_root, {"action": "archive", "summary": summary})
    return summary


def _limit_from_args(args: argparse.Namespace) -> int | None:
    if args.all:
        return None
    if args.limit < 1:
        raise SystemExit("--limit must be positive")
    return args.limit


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    parser.add_argument("--all", action="store_true", help="Process every eligible candidate.")
    parser.add_argument(
        "--dry-run", action="store_true", help="Enumerate candidates without copying, deleting, or committing."
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    root = args.project_root.resolve()
    summary = run_batch(root, limit=_limit_from_args(args), dry_run=args.dry_run)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(
            "Batch archive terminal verdicts: "
            f"{len(summary['candidates'])} candidate(s), "
            f"{len(summary['archived'])} archived, "
            f"{len(summary['errors'])} error(s)"
        )
    return 1 if summary["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
