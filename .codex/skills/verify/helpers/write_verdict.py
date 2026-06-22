# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Helper utilities for Loyal Opposition verdict authoring."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _discover_project_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "scripts" / "bridge_author_metadata.py").is_file():
            return parent
    return Path(__file__).resolve().parents[4]


PROJECT_ROOT = _discover_project_root()
GROUNDTRUTH_SRC = PROJECT_ROOT / "groundtruth-kb" / "src"
if GROUNDTRUTH_SRC.is_dir() and str(GROUNDTRUTH_SRC) not in sys.path:
    sys.path.insert(0, str(GROUNDTRUTH_SRC))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from groundtruth_kb.bridge.prior_deliberations import (  # noqa: E402
    pre_populate_prior_deliberations,
)

DEFAULT_VERDICT_PREPOPULATION_LOG = Path(".gtkb-state/bridge-verify-helper/last-prepopulation.json")
STATUS_RE = re.compile(r"^(NEW|REVISED|GO|NO-GO|VERIFIED|DEFERRED|WITHDRAWN|ADVISORY|IMPLEMENTED)$")
VERSIONED_BRIDGE_RE_TEMPLATE = r"^{slug}-(?P<version>\d{{3}})\.md$"
RECOMMENDED_COMMIT_TYPE_RE = re.compile(r"Recommended commit type\s*:", re.IGNORECASE)


class VerifiedFinalizationError(RuntimeError):
    """Raised when a VERIFIED verdict cannot be atomically committed."""


@dataclass(frozen=True)
class BridgeVersion:
    status: str
    rel_path: str
    version: int


@dataclass(frozen=True)
class VerifiedFinalizationResult:
    """Result for a successful VERIFIED finalization transaction."""

    commit_sha: str
    verdict_path: str
    committed_paths: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "commit_sha": self.commit_sha,
            "verdict_path": self.verdict_path,
            "committed_paths": list(self.committed_paths),
        }


def seed_prior_deliberations(
    slug: str,
    body: str,
    *,
    db: Any | bool | None = None,
    glossary_path: Path | None = None,
    log_path: Path | bool | None = DEFAULT_VERDICT_PREPOPULATION_LOG,
    pre_populate: bool = True,
) -> str:
    """Seed a verdict body's ``## Prior Deliberations`` section."""
    if not pre_populate:
        return body
    return pre_populate_prior_deliberations(
        slug,
        body,
        db=db,
        glossary_path=glossary_path,
        log_path=log_path,
    )


def _project_root_from_arg(value: Path | None) -> Path:
    return (value or PROJECT_ROOT).resolve()


def _bridge_versions(slug: str, project_root: Path) -> list[BridgeVersion]:
    bridge_dir = project_root / "bridge"
    pattern = re.compile(VERSIONED_BRIDGE_RE_TEMPLATE.format(slug=re.escape(slug)))
    versions: list[BridgeVersion] = []
    for path in bridge_dir.glob(f"{slug}-*.md"):
        match = pattern.match(path.name)
        if match is None:
            continue
        try:
            lines = path.read_text(encoding="utf-8-sig", errors="replace").splitlines()
        except OSError as exc:
            raise VerifiedFinalizationError(f"Bridge file is unreadable: {path}") from exc
        status = next((line.strip() for line in lines if line.strip()), "")
        if not STATUS_RE.fullmatch(status):
            raise VerifiedFinalizationError(f"Bridge file has invalid status token: {path}: {status!r}")
        versions.append(
            BridgeVersion(
                status=status,
                rel_path=f"bridge/{path.name}",
                version=int(match.group("version")),
            )
        )
    if not versions:
        raise VerifiedFinalizationError(f"No versioned bridge files found for {slug!r}")
    return sorted(versions, key=lambda item: item.version, reverse=True)


def _assert_verification_ready(slug: str, project_root: Path) -> tuple[int, str]:
    versions = _bridge_versions(slug, project_root)
    latest = versions[0]
    if latest.status not in {"NEW", "REVISED"}:
        raise VerifiedFinalizationError(
            "VERIFIED finalization requires a post-implementation report latest "
            f"status of NEW or REVISED; got {latest.status} at {latest.rel_path}."
        )
    if not any(version.status == "GO" for version in versions[1:]):
        raise VerifiedFinalizationError(f"VERIFIED finalization requires a prior GO in the bridge chain for {slug!r}.")
    return max(version.version for version in versions) + 1, latest.rel_path


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


def validate_verified_body(body: str) -> None:
    """Validate the evidence floor before a VERIFIED verdict can be committed."""
    if _first_nonblank_line(body) != "VERIFIED":
        raise VerifiedFinalizationError(
            "Atomic finalization only applies to verdict bodies whose first token is VERIFIED."
        )
    if not RECOMMENDED_COMMIT_TYPE_RE.search(body):
        raise VerifiedFinalizationError("VERIFIED verdict body must include Recommended commit type evidence.")
    mapping = _section_body(body, "Spec-to-Test Mapping")
    if not mapping:
        raise VerifiedFinalizationError("VERIFIED verdict body must include a ## Spec-to-Test Mapping section.")
    if not re.search(r"\|\s*[^|\n]+\s*\|\s*[^|\n]+\s*\|\s*yes\s*\|\s*[^|\n]+\s*\|", mapping, re.IGNORECASE):
        raise VerifiedFinalizationError(
            "VERIFIED verdict body must include at least one executed Spec-to-Test Mapping row with Executed=yes."
        )
    if not _section_body(body, "Commands Executed"):
        raise VerifiedFinalizationError("VERIFIED verdict body must include a ## Commands Executed section.")


def _normalize_repo_path(project_root: Path, path_text: str) -> str:
    raw = path_text.strip().strip("'\"")
    if not raw:
        raise VerifiedFinalizationError("Committed path list contains an empty path.")
    path = Path(raw)
    if path.is_absolute():
        try:
            return path.resolve().relative_to(project_root.resolve()).as_posix()
        except ValueError as exc:
            raise VerifiedFinalizationError(f"Committed path escapes project root: {path_text}") from exc
    normalized = raw.replace("\\", "/")
    if normalized.startswith("./"):
        normalized = normalized[2:]
    if normalized.startswith("../") or normalized == ".." or "/../" in normalized:
        raise VerifiedFinalizationError(f"Committed path escapes project root: {path_text}")
    if normalized.startswith(".git/") or normalized == ".git":
        raise VerifiedFinalizationError("Committed path list must not target .git internals.")
    return normalized


def _unique_paths(project_root: Path, paths: list[str]) -> tuple[str, ...]:
    unique: list[str] = []
    seen: set[str] = set()
    for path in paths:
        normalized = _normalize_repo_path(project_root, path)
        if normalized not in seen:
            unique.append(normalized)
            seen.add(normalized)
    return tuple(unique)


def _run_git(args: list[str], *, cwd: Path, check: bool = False) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if check and result.returncode != 0:
        raise VerifiedFinalizationError(
            f"git {' '.join(args)} failed with exit {result.returncode}: {(result.stderr or result.stdout).strip()}"
        )
    return result


_INDEX_LOCK_SIGNATURES = (
    "index.lock",
    "unable to create",
    "permission denied",
    "another git process",
)


def _env_int(name: str, default: int) -> int:
    try:
        value = int(os.environ.get(name, ""))
    except ValueError:
        return default
    return value if value > 0 else default


def _env_float(name: str, default: float) -> float:
    try:
        value = float(os.environ.get(name, ""))
    except ValueError:
        return default
    return value if value > 0 else default


def _is_index_lock_failure(result: subprocess.CompletedProcess[str]) -> bool:
    blob = f"{result.stderr or ''}\n{result.stdout or ''}".lower()
    return "index.lock" in blob or (
        "another git process" in blob and any(signature in blob for signature in _INDEX_LOCK_SIGNATURES)
    )


def _run_git_with_lock_retry(
    args: list[str],
    *,
    cwd: Path,
    attempts: int | None = None,
    base_delay: float | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    attempts = attempts if attempts is not None else _env_int("GTKB_VERIFIED_COMMIT_LOCK_RETRIES", 5)
    base_delay = base_delay if base_delay is not None else _env_float("GTKB_VERIFIED_COMMIT_LOCK_BASE_DELAY", 0.5)
    attempts = max(1, attempts)
    base_delay = max(0.0, base_delay)
    last: subprocess.CompletedProcess[str] | None = None
    for attempt in range(attempts):
        result = _run_git(args, cwd=cwd, check=False)
        if result.returncode == 0:
            return result
        last = result
        if not _is_index_lock_failure(result):
            break
        if attempt < attempts - 1:
            time.sleep(base_delay * (2**attempt))

    if last is None:
        raise VerifiedFinalizationError(f"git {' '.join(args)} did not run.")
    if check:
        raise VerifiedFinalizationError(
            f"git {' '.join(args)} failed (attempt {attempt + 1}/{attempts}) with exit {last.returncode}: {(last.stderr or last.stdout).strip()}"
        )
    return last


def _git_lines(args: list[str], *, cwd: Path) -> tuple[str, ...]:
    result = _run_git(args, cwd=cwd, check=True)
    return tuple(line.strip().replace("\\", "/") for line in result.stdout.splitlines() if line.strip())


def _staged_paths(project_root: Path) -> tuple[str, ...]:
    return _git_lines(["diff", "--name-only", "--cached", "--"], cwd=project_root)


def _cleanup_failed_verdict(project_root: Path, verdict_rel_path: str, staged_paths: tuple[str, ...]) -> None:
    if staged_paths:
        _run_git(["restore", "--staged", "--", *staged_paths], cwd=project_root)
    verdict_path = project_root / verdict_rel_path
    try:
        verdict_path.unlink()
    except FileNotFoundError:
        pass


def _append_commit_finalization_evidence(body: str, *, commit_message: str, paths: tuple[str, ...]) -> str:
    if _section_body(body, "Commit Finalization Evidence"):
        return body
    path_lines = "\n".join(f"- `{path}`" for path in paths)
    subject = commit_message.splitlines()[0].strip()
    return (
        body.rstrip() + "\n\n## Commit Finalization Evidence\n\n"
        "- Finalization helper: `.claude/skills/verify/helpers/write_verdict.py --finalize-verified`\n"
        f"- Intended commit subject: `{subject}`\n"
        "- Same-transaction path set:\n"
        f"{path_lines}\n"
        "- Final commit SHA is emitted by the helper after commit creation; it is intentionally not self-embedded in this verdict file.\n"
    )


def finalize_verified_commit(
    slug: str,
    body: str,
    *,
    include_paths: list[str],
    commit_message: str,
    project_root: Path | None = None,
    pre_populate: bool = False,
    db: Any | bool | None = None,
    glossary_path: Path | None = None,
    log_path: Path | bool | None = DEFAULT_VERDICT_PREPOPULATION_LOG,
) -> VerifiedFinalizationResult:
    """Write a VERIFIED verdict and create the final local commit as one transaction.

    The helper writes the next versioned bridge verdict, stages the verified
    path set plus that verdict, and commits ONLY that path set via an explicit
    pathspec. Unrelated paths already staged in the shared index by other
    sessions are tolerated and left untouched (never folded into this commit).
    If any step after the verdict write fails, the verdict file is removed and
    the staged paths added by this helper are unstaged.
    """
    root = _project_root_from_arg(project_root)
    if not include_paths:
        raise VerifiedFinalizationError(
            "VERIFIED finalization requires at least one verified implementation/report path."
        )
    if not commit_message.strip():
        raise VerifiedFinalizationError("VERIFIED finalization requires a non-empty commit message.")

    next_version, _latest_report = _assert_verification_ready(slug, root)
    verdict_rel_path = f"bridge/{slug}-{next_version:03d}.md"
    expected_paths = _unique_paths(root, [*include_paths, verdict_rel_path])
    if len(expected_paths) != len(include_paths) + 1:
        raise VerifiedFinalizationError("VERIFIED finalization include paths must not duplicate the verdict path.")

    # Pre-existing staged paths from other sessions in the shared index are
    # tolerated: the final commit below uses an explicit pathspec, so only the
    # verified path set is committed regardless of unrelated staged work. We
    # capture them to scope the post-`git add` staged-set assertion to this
    # helper's own paths; unrelated staged entries are left untouched.
    staged_before = set(_staged_paths(root))

    body_to_write = seed_prior_deliberations(
        slug,
        body,
        db=db,
        glossary_path=glossary_path,
        log_path=log_path,
        pre_populate=pre_populate,
    )
    validate_verified_body(body_to_write)
    body_to_write = _append_commit_finalization_evidence(
        body_to_write,
        commit_message=commit_message,
        paths=expected_paths,
    )

    # Determine which expected paths are actually dirty/modified/untracked
    # so we only expect those to be staged after `git add`.
    dirty_expected_paths = [verdict_rel_path]
    for path in expected_paths:
        if path == verdict_rel_path:
            continue
        res = _run_git(["status", "--porcelain", "--ignored", "--", path], cwd=root)
        if res.stdout.strip():
            dirty_expected_paths.append(path)

    from scripts.gtkb_bridge_writer import write_bridge_file

    write_bridge_file(slug, next_version, body_to_write, root)
    try:
        _run_git_with_lock_retry(["add", "-f", "--", *expected_paths], cwd=root)
        staged_after = set(_staged_paths(root))
        missing = set(dirty_expected_paths) - staged_after
        # Anything staged beyond the helper's own expected paths must be a
        # pre-existing unrelated entry (tolerated); the helper must never have
        # introduced new staging of its own beyond `dirty_expected_paths`.
        unexpected_new = (staged_after - set(dirty_expected_paths)) - staged_before
        if missing or unexpected_new:
            raise VerifiedFinalizationError(
                "VERIFIED finalization staged-set mismatch. "
                f"missing={sorted(missing)}; unexpected_new={sorted(unexpected_new)}; "
                f"expected_dirty={list(dirty_expected_paths)}; pre_existing_staged={sorted(staged_before)}"
            )
        # Commit ONLY the verified path set via explicit pathspec so unrelated
        # pre-existing staged files are never folded into this VERIFIED commit.
        commit = _run_git_with_lock_retry(
            ["commit", "-m", commit_message, "--", *expected_paths], cwd=root, check=False
        )
        if commit.returncode != 0:
            raise VerifiedFinalizationError(
                f"git commit failed with exit {commit.returncode}: {(commit.stderr or commit.stdout).strip()}"
            )
    except Exception:
        _cleanup_failed_verdict(root, verdict_rel_path, expected_paths)
        raise

    commit_sha = _git_lines(["rev-parse", "HEAD"], cwd=root)[0]
    return VerifiedFinalizationResult(
        commit_sha=commit_sha,
        verdict_path=verdict_rel_path,
        committed_paths=expected_paths,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Seed a verdict body's Prior Deliberations section.",
    )
    parser.add_argument("--slug", required=True, help="Bridge thread slug shared by the verdict.")
    parser.add_argument(
        "--body-file",
        type=Path,
        help="Read the verdict body from this UTF-8 file. Defaults to stdin.",
    )
    parser.add_argument(
        "--no-semantic-search",
        action="store_true",
        help="Disable KnowledgeDB semantic search and use glossary seeds only.",
    )
    parser.add_argument(
        "--no-log",
        action="store_true",
        help="Disable the verify-side prepopulation audit log.",
    )
    parser.add_argument(
        "--no-prepopulate",
        action="store_true",
        help="Return the body unchanged for explicit opt-out workflows.",
    )
    parser.add_argument(
        "--finalize-verified",
        action="store_true",
        help="Atomically write a VERIFIED verdict and create the final local commit.",
    )
    parser.add_argument(
        "--include",
        action="append",
        default=[],
        help="Verified implementation/report path to include in the final commit. Repeat as needed.",
    )
    parser.add_argument("--commit-message", help="Commit message for --finalize-verified.")
    parser.add_argument("--project-root", type=Path, help="Project root for --finalize-verified.")
    args = parser.parse_args(argv)

    if args.body_file is not None:
        body = args.body_file.read_text(encoding="utf-8")
    else:
        body = sys.stdin.read()

    log_path = False if args.no_log else DEFAULT_VERDICT_PREPOPULATION_LOG
    if args.finalize_verified:
        result = finalize_verified_commit(
            args.slug,
            body,
            include_paths=args.include,
            commit_message=args.commit_message or "",
            project_root=args.project_root,
            pre_populate=not args.no_prepopulate,
            db=False if args.no_semantic_search else None,
            log_path=log_path,
        )
        sys.stdout.write(json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n")
        return 0

    seeded = seed_prior_deliberations(
        args.slug,
        body,
        db=False if args.no_semantic_search else None,
        log_path=log_path,
        pre_populate=not args.no_prepopulate,
    )
    sys.stdout.write(seeded)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
