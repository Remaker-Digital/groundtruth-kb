#!/usr/bin/env python3
"""Resolve active work items whose linked bridge threads are all VERIFIED."""

from __future__ import annotations

# ruff: noqa: E402,I001

import argparse
import fnmatch
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    from windows_subprocess import no_window_subprocess_kwargs
except ModuleNotFoundError:  # pragma: no cover - package-style test import
    from scripts.windows_subprocess import no_window_subprocess_kwargs

PROJECT_ROOT = Path(__file__).resolve().parent.parent
GROUNDTRUTH_SRC = PROJECT_ROOT / "groundtruth-kb" / "src"
if str(GROUNDTRUTH_SRC) not in sys.path:
    sys.path.insert(0, str(GROUNDTRUTH_SRC))

from groundtruth_kb.db import (  # noqa: E402
    KnowledgeDB,
    WORK_ITEM_BACKLOG_FIELDS,
    WORK_ITEM_TERMINAL_RESOLUTION_STATUSES,
)

BRIDGE_FILE_STATUS_RE = re.compile(
    r"^[#>*\-\s`]*(NEW|REVISED|NO-ACTION|GO|NO-GO|VERIFIED|ADVISORY|DEFERRED|WITHDRAWN)\b"
)
BRIDGE_PATH_RE = re.compile(r"(?:^|\b)bridge/([A-Za-z0-9_.-]+?)-\d{3}\.md(?:\b|$)")
VERSIONED_MD_RE = re.compile(r"^([A-Za-z0-9_.-]+?)-\d{3}\.md$")
TOKEN_SPLIT_RE = re.compile(r"[,;\r\n]+")
# Canonical bridge-file metadata line declaring the thread's parent work item.
# Anchored and MULTILINE so only the metadata declaration matches, never a prose
# WI mention. The captured ID is upper-cased to key the reverse index against the
# canonical uppercase work_items.id form.
_WORK_ITEM_METADATA_RE = re.compile(
    r"^Work Item:\s*(WI-[A-Za-z0-9-]+)\s*$", re.MULTILINE | re.IGNORECASE
)
_BRIDGE_KIND_RE = re.compile(
    r"^bridge_kind:\s*([A-Za-z0-9_.-]+)\s*$", re.MULTILINE | re.IGNORECASE
)
_TARGET_PATHS_METADATA_RE = re.compile(
    r"^\s*target_paths\s*:\s*(.*?)\s*$", re.MULTILINE | re.IGNORECASE
)
_BRIDGE_VERSION_REFERENCE_RE = re.compile(
    r"(?:bridge[/\\])?(?P<slug>[A-Za-z0-9_.-]+?)-(?P<version>\d{3})(?:\.md)?"
)
_IMPLEMENTATION_PROPOSAL_RE = re.compile(
    r"^#\s+.*implementation proposal", re.MULTILINE | re.IGNORECASE
)
_WAIVER_HEADING_RE = re.compile(
    r"^##\s+By-Reference Finalization Waiver\s*$",
    re.MULTILINE,
)
_AFFIRMATIVE_WAIVER_RE = re.compile(
    r"^Owner-approved by-reference waiver:\s*(DELIB-[A-Z0-9-]+)\.\s*$",
    re.MULTILINE,
)
_NEGATED_WAIVER_RE = re.compile(
    r"(?i)\b(?:do not|don't|does not|did not|not|never|no)\b.{0,80}by-reference waiver",
)
_ADVISORY_GO_TEXT_RE = re.compile(
    r"\b(?:constrained to advisory(?: and planning)?|advisory and planning direction only|planning direction only)\b",
    re.IGNORECASE,
)

_CLOSURE_REASON_PRIORITY = (
    "no_action_verified",
    "malformed_target_metadata",
    "missing_implementation_commit_coverage",
)

CHANGED_BY = "bridge-verified-backlog-reconciler"
CHANGE_REASON = "Resolved by bridge VERIFIED backlog reconciler per DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM."
REPAIR_CHANGED_BY = "bridge-verified-backlog-reconciler-repair"
REPAIR_CHANGE_REASON = (
    "Reopened by bridge VERIFIED backlog reconciler repair after "
    "bridge/gtkb-bridge-verified-backlog-retirement-006.md NO-GO identified "
    "an overbroad related_bridge_threads closure predicate."
)


def _status_from_bridge_file(path: Path) -> str | None:
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return None
    for raw in lines:
        stripped = raw.strip()
        if not stripped:
            continue
        match = BRIDGE_FILE_STATUS_RE.match(stripped)
        return match.group(1).upper() if match else None
    return None


def collect_latest_bridge_statuses(project_root: Path) -> dict[str, dict[str, str]]:
    """Return the latest status row for each numbered bridge-file thread."""

    latest: dict[str, tuple[int, str, str]] = {}
    bridge_dir = project_root / "bridge"
    if not bridge_dir.is_dir():
        return {}
    for path in bridge_dir.glob("*.md"):
        match = VERSIONED_MD_RE.match(path.name)
        if match is None:
            continue
        slug = match.group(1)
        version_match = re.search(r"-(\d{3})\.md$", path.name)
        if version_match is None:
            continue
        status = _status_from_bridge_file(path)
        if status is None:
            continue
        rel_path = path.relative_to(project_root).as_posix()
        version = int(version_match.group(1))
        prior = latest.get(slug)
        if prior is None or version > prior[0]:
            latest[slug] = (version, status, rel_path)
    return {
        slug: {"status": status, "path": rel_path}
        for slug, (_version, status, rel_path) in sorted(latest.items())
    }


def _flatten_related_value(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return []
        try:
            decoded = json.loads(stripped)
        except json.JSONDecodeError:
            decoded = None
        if isinstance(decoded, (list, tuple)):
            return _flatten_related_value(decoded)
        if isinstance(decoded, str) and decoded != value:
            return _flatten_related_value(decoded)
        paths = [match.group(0).strip() for match in BRIDGE_PATH_RE.finditer(stripped)]
        if paths:
            remainder = BRIDGE_PATH_RE.sub(" ", stripped)
            return paths + [token for token in TOKEN_SPLIT_RE.split(remainder) if token]
        return [token for token in TOKEN_SPLIT_RE.split(stripped) if token]
    if isinstance(value, (list, tuple, set)):
        tokens: list[str] = []
        for item in value:
            tokens.extend(_flatten_related_value(item))
        return tokens
    return []


def normalize_bridge_reference(token: str) -> str | None:
    """Normalize a related_bridge_threads token to a bridge document slug."""

    cleaned = token.strip().strip("`'\"")
    if not cleaned:
        return None
    path_match = BRIDGE_PATH_RE.search(cleaned)
    if path_match:
        return path_match.group(1)
    if cleaned.startswith("bridge/"):
        cleaned = cleaned.removeprefix("bridge/")
    versioned_match = VERSIONED_MD_RE.match(cleaned)
    if versioned_match:
        return versioned_match.group(1)
    if cleaned.endswith(".md"):
        return None
    if "/" in cleaned or "\\" in cleaned:
        return None
    if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", cleaned):
        return cleaned
    return None


def parse_related_bridge_threads(value: Any) -> list[str]:
    """Parse related_bridge_threads values without inferring from prose."""

    slugs: list[str] = []
    seen: set[str] = set()
    for token in _flatten_related_value(value):
        slug = normalize_bridge_reference(token)
        if slug and slug not in seen:
            slugs.append(slug)
            seen.add(slug)
    return slugs


def _index_bridge_thread_files(project_root: Path) -> dict[str, list[Path]]:
    """One-pass index of slug -> sorted exact-versioned files (``<slug>-NNN.md``).

    Built with a single ``bridge/*.md`` scan so callers needing files for many
    slugs (reverse-link construction, per-candidate evidence) avoid an
    O(slugs x dir) per-slug ``glob`` that does not scale at live bridge volume
    (~1099 docs; WI-4704 verification F1). Grouping by ``VERSIONED_MD_RE``
    preserves the exact-version rule (WI-4704 GO Condition 1): a child file such
    as ``<slug>-child-001.md`` indexes under ``<slug>-child``, never ``<slug>``.
    """

    index: dict[str, list[Path]] = {}
    bridge_dir = project_root / "bridge"
    if not bridge_dir.is_dir():
        return index
    for path in bridge_dir.glob("*.md"):
        match = VERSIONED_MD_RE.match(path.name)
        if match is None:
            continue
        index.setdefault(match.group(1), []).append(path)
    for files in index.values():
        files.sort()
    return index


def _bridge_thread_files(
    project_root: Path, slug: str, *, file_index: dict[str, list[Path]] | None = None
) -> list[Path]:
    """Return only the exact versioned chain for ``slug`` (``<slug>-NNN.md``).

    Batch callers pass ``file_index`` (from ``_index_bridge_thread_files``) to
    reuse a single directory scan; without it a one-pass index is built and the
    slug selected (correct for standalone callers and tests). The exact-version
    rule (WI-4704 GO Condition 1) is enforced by ``VERSIONED_MD_RE`` grouping, so
    a child file such as ``<slug>-child-001.md`` never counts as a file of
    ``<slug>``.
    """

    if file_index is None:
        file_index = _index_bridge_thread_files(project_root)
    return file_index.get(slug, [])


def _read_bridge_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def _bridge_rel_path(project_root: Path, path: Path) -> str:
    return path.relative_to(project_root).as_posix()


def _metadata_reference(markdown: str, label: str) -> str | None:
    match = re.search(
        rf"^{re.escape(label)}:\s*(.+?)\s*$", markdown, re.MULTILINE | re.IGNORECASE
    )
    if match is None:
        return None
    reference = _BRIDGE_VERSION_REFERENCE_RE.search(match.group(1))
    if reference is None:
        return ""
    return f"bridge/{reference.group('slug')}-{reference.group('version')}.md"


def _thread_file_by_rel_path(
    project_root: Path, files: list[Path], rel_path: str
) -> Path | None:
    return next(
        (path for path in files if _bridge_rel_path(project_root, path) == rel_path),
        None,
    )


def _approved_proposal_file(
    project_root: Path, slug: str, verdict_path: Path, files: list[Path]
) -> Path | None:
    """Resolve the proposal approved by the latest GO preceding ``verdict_path``."""

    try:
        verdict_index = files.index(verdict_path)
    except ValueError:
        return None
    prior_files = files[:verdict_index]
    go_path = next(
        (
            path
            for path in reversed(prior_files)
            if _status_from_bridge_file(path) == "GO"
        ),
        None,
    )
    if go_path is None:
        return None
    go_index = files.index(go_path)
    go_text = _read_bridge_text(go_path)
    for label in ("Approved proposal", "Responds to"):
        reference = _metadata_reference(go_text, label)
        if not reference:
            continue
        candidate = _thread_file_by_rel_path(project_root, files, reference)
        if candidate is not None and files.index(candidate) < go_index:
            if _status_from_bridge_file(candidate) in {"NEW", "REVISED"}:
                return candidate

    candidates = [
        path
        for path in files[:go_index]
        if _status_from_bridge_file(path) in {"NEW", "REVISED"}
    ]
    for candidate in reversed(candidates):
        text = _read_bridge_text(candidate)
        kind = _BRIDGE_KIND_RE.search(text)
        if (
            kind and kind.group(1).lower() == "prime_proposal"
        ) or _IMPLEMENTATION_PROPOSAL_RE.search(text):
            return candidate
    return candidates[-1] if candidates else None


def _parse_target_path_metadata(
    markdown: str,
) -> tuple[tuple[str, ...] | None, str | None]:
    """Parse strict inline-JSON target metadata.

    Missing metadata preserves legacy and bridge-only behavior. Once a
    ``target_paths`` declaration exists, malformed or unsafe values fail closed.
    """

    matches = list(_TARGET_PATHS_METADATA_RE.finditer(markdown))
    if not matches:
        return None, None
    if len(matches) != 1:
        return None, "multiple_target_paths_declarations"
    try:
        parsed = json.loads(matches[0].group(1))
    except json.JSONDecodeError:
        return None, "target_paths_not_json"
    if not isinstance(parsed, list) or not all(
        isinstance(item, str) and item.strip() for item in parsed
    ):
        return None, "target_paths_not_string_list"

    normalized: list[str] = []
    for raw in parsed:
        path = raw.strip().replace("\\", "/")
        while path.startswith("./"):
            path = path[2:]
        parts = path.split("/")
        if (
            not path
            or path.startswith("/")
            or re.match(r"^[A-Za-z]:", path)
            or any(part in {"", ".", ".."} for part in parts)
        ):
            return None, f"unsafe_target_path:{raw}"
        if path not in normalized:
            normalized.append(path)
    return tuple(normalized), None


def _run_git(project_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=project_root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
        **no_window_subprocess_kwargs(),
    )


def _parse_git_status_paths(stdout: str) -> set[str]:
    paths: set[str] = set()
    entries = [entry for entry in stdout.split("\0") if entry]
    index = 0
    while index < len(entries):
        entry = entries[index]
        code = entry[:2]
        path = entry[3:] if len(entry) > 3 and entry[2] == " " else entry[2:].strip()
        if path:
            paths.add(path.replace("\\", "/"))
        if code.strip().startswith(("R", "C")) and index + 1 < len(entries):
            index += 1
            old_path = entries[index].strip()
            if old_path:
                paths.add(old_path.replace("\\", "/"))
        index += 1
    return paths


def _git_log_name_index(stdout: str) -> tuple[dict[str, str], dict[str, set[str]]]:
    latest_commit_by_path: dict[str, str] = {}
    changed_paths_by_commit: dict[str, set[str]] = {}
    current_commit: str | None = None
    for raw_line in stdout.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("commit:"):
            current_commit = line.removeprefix("commit:").strip()
            changed_paths_by_commit.setdefault(current_commit, set())
            continue
        if current_commit is None:
            continue
        path = line.replace("\\", "/")
        changed_paths_by_commit[current_commit].add(path)
        latest_commit_by_path.setdefault(path, current_commit)
    return latest_commit_by_path, changed_paths_by_commit


def _target_covered_by_commit(target: str, changed_paths: set[str]) -> bool:
    """Return whether an approved target is present in a commit path set."""

    if any(char in target for char in "*?["):
        return any(fnmatch.fnmatchcase(path, target) for path in changed_paths)
    return target in changed_paths


def _target_is_uncommittable(
    project_root: Path,
    target: str,
    cache: dict[str, bool],
) -> bool:
    """Return whether a declared target can never appear in any commit (WI-6280).

    A gitignored path cannot be committed, so requiring it in the verdict's commit
    makes closure permanently unsatisfiable: the work item can never auto-resolve
    no matter what the implementer does. 46 items were blocked this way, 9 of them
    on ``groundtruth.db`` alone. Such a path is excluded from the coverage
    requirement rather than counted missing.

    Deliberately narrow. Only IGNORED paths qualify. An untracked-but-not-ignored
    path is a genuine "forgot to commit it" and MUST still count as missing, so the
    check must not be widened to untracked. Glob targets are not tested: check-ignore
    has no meaningful answer for a pattern, and a glob matching only ignored files is
    a scope defect to surface, not to hide.
    """

    if any(char in target for char in "*?["):
        return False
    cached = cache.get(target)
    if cached is not None:
        return cached
    result = _run_git(project_root, "check-ignore", "-q", target)
    ignored = result.returncode == 0
    cache[target] = ignored
    return ignored


def _commit_is_ancestor(
    project_root: Path,
    candidate: str,
    descendant: str,
    cache: dict[tuple[str, str], bool],
) -> bool:
    """Return whether ``candidate`` is an ancestor of, or equal to, ``descendant``."""

    if not candidate or not descendant:
        return False
    if candidate == descendant:
        return True
    key = (candidate, descendant)
    cached = cache.get(key)
    if cached is not None:
        return cached
    result = _run_git(
        project_root, "merge-base", "--is-ancestor", candidate, descendant
    )
    ancestor = result.returncode == 0
    cache[key] = ancestor
    return ancestor


def _target_covered_by_ancestor_commit(
    project_root: Path,
    target: str,
    verdict_commit: str,
    provenance: dict[str, Any],
    cache: dict[tuple[str, str], bool],
) -> bool:
    """Return whether an approved target was committed at or before the verdict.

    Ancestry, not mere presence (WI-6280). A path committed AFTER verification,
    or on a branch unrelated to the verdict commit, is not work the verdict
    verified, so it must not satisfy closure. Only the commit boundary moves;
    the requirement that the path BE committed does not.
    """

    latest_commit_by_path = provenance["latest_commit_by_path"]
    if any(char in target for char in "*?["):
        # Mirrors _target_covered_by_commit's ANY-match glob semantics.
        return any(
            _commit_is_ancestor(
                project_root, latest_commit_by_path[path], verdict_commit, cache
            )
            for path in provenance["tracked_paths"]
            if fnmatch.fnmatchcase(path, target) and latest_commit_by_path.get(path)
        )
    commit = latest_commit_by_path.get(target)
    if not commit:
        return False
    return _commit_is_ancestor(project_root, commit, verdict_commit, cache)


def build_git_provenance_index(project_root: Path) -> dict[str, Any]:
    """Build one repository-wide Git provenance index for VERIFIED closure checks."""

    status = _run_git(
        project_root, "status", "--porcelain=v1", "-z", "--untracked-files=all", "--"
    )
    tracked = _run_git(project_root, "ls-files", "-z", "--")
    history = _run_git(project_root, "log", "--format=commit:%H", "--name-only", "--")
    latest_commit_by_path: dict[str, str] = {}
    changed_paths_by_commit: dict[str, set[str]] = {}
    if history.returncode == 0:
        latest_commit_by_path, changed_paths_by_commit = _git_log_name_index(
            history.stdout
        )
    tracked_paths = (
        {path.replace("\\", "/") for path in tracked.stdout.split("\0") if path}
        if tracked.returncode == 0
        else set()
    )
    return {
        "status_ok": status.returncode == 0,
        "tracked_ok": tracked.returncode == 0,
        "history_ok": history.returncode == 0,
        "dirty_paths": _parse_git_status_paths(status.stdout)
        if status.returncode == 0
        else set(),
        "tracked_paths": tracked_paths,
        "latest_commit_by_path": latest_commit_by_path,
        "changed_paths_by_commit": changed_paths_by_commit,
    }


def _terminal_verdict_commit_coverage(
    project_root: Path,
    verdict_rel_path: str,
    target_paths: tuple[str, ...],
    *,
    git_provenance_index: dict[str, Any] | None = None,
) -> dict[str, Any]:
    provenance = git_provenance_index or build_git_provenance_index(project_root)
    dirty_paths = provenance["dirty_paths"]
    tracked_paths = provenance["tracked_paths"]
    if (
        not provenance["status_ok"]
        or not provenance["tracked_ok"]
        or verdict_rel_path in dirty_paths
    ):
        return {
            "covered": False,
            "commit": None,
            "changed_paths": [],
            "missing_paths": [verdict_rel_path, *target_paths],
            "verdict_state": "uncommitted_or_untracked",
        }
    if verdict_rel_path not in tracked_paths:
        return {
            "covered": False,
            "commit": None,
            "changed_paths": [],
            "missing_paths": [verdict_rel_path, *target_paths],
            "verdict_state": "uncommitted_or_untracked",
        }

    commit = provenance["latest_commit_by_path"].get(verdict_rel_path, "")
    if not commit:
        return {
            "covered": False,
            "commit": None,
            "changed_paths": [],
            "missing_paths": [verdict_rel_path, *target_paths],
            "verdict_state": "no_containing_commit",
        }

    changed_paths = provenance["changed_paths_by_commit"].get(commit)
    if changed_paths is None:
        return {
            "covered": False,
            "commit": commit,
            "changed_paths": [],
            "missing_paths": [verdict_rel_path, *target_paths],
            "verdict_state": "commit_inspection_failed",
        }
    # The verdict artifact must still appear in its OWN commit; only
    # implementation targets may be satisfied by an ancestor commit (WI-6280).
    # This keeps GOV-FILE-BRIDGE-AUTHORITY-001's "a verdict exists and is
    # committed" invariant exactly where it was.
    ancestor_cache: dict[tuple[str, str], bool] = {}
    ignore_cache: dict[str, bool] = {}
    missing = []
    uncommittable = []
    for path in (verdict_rel_path, *target_paths):
        if _target_covered_by_commit(path, changed_paths):
            continue
        if path != verdict_rel_path and _target_covered_by_ancestor_commit(
            project_root, path, commit, provenance, ancestor_cache
        ):
            continue
        # WI-6280: a gitignored implementation target can never be committed, so
        # counting it missing makes closure permanently unsatisfiable. Exclude it
        # and report it separately. The verdict artifact itself is NOT exempt --
        # GOV-FILE-BRIDGE-AUTHORITY-001's "a verdict exists and is committed"
        # invariant stays exactly where it was.
        if path != verdict_rel_path and _target_is_uncommittable(
            project_root, path, ignore_cache
        ):
            uncommittable.append(path)
            continue
        missing.append(path)
    return {
        "covered": not missing,
        "commit": commit,
        "changed_paths": sorted(changed_paths),
        "missing_paths": missing,
        "uncommittable_paths": uncommittable,
        "verdict_state": "committed"
        if verdict_rel_path in changed_paths
        else "commit_omits_verdict",
    }


def _report_has_by_reference_waiver(report_path: Path | None) -> bool:
    """Accept only one dedicated affirmative DELIB-backed by-reference waiver."""

    if report_path is None:
        return False
    text = _read_bridge_text(report_path)
    headings = list(_WAIVER_HEADING_RE.finditer(text))
    if len(headings) != 1:
        return False
    heading = headings[0]
    next_heading = re.search(r"^##\s+", text[heading.end() :], re.MULTILINE)
    end = heading.end() + next_heading.start() if next_heading else len(text)
    body = text[heading.end() : end]
    if _NEGATED_WAIVER_RE.search(body):
        return False
    return len(_AFFIRMATIVE_WAIVER_RE.findall(body)) == 1


def verified_thread_closure_evidence(
    project_root: Path,
    slug: str,
    *,
    file_index: dict[str, list[Path]] | None = None,
    git_provenance_index: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Classify whether a latest VERIFIED thread proves implementation closure."""

    files = _bridge_thread_files(project_root, slug, file_index=file_index)
    if not files:
        return {
            "satisfied": False,
            "reason": "malformed_target_metadata",
            "detail": "missing_thread_files",
        }
    verdict_path = files[-1]
    verdict_rel_path = _bridge_rel_path(project_root, verdict_path)
    verdict_text = _read_bridge_text(verdict_path)
    response_reference = _metadata_reference(verdict_text, "Responds to")
    if response_reference == "":
        return {
            "satisfied": False,
            "reason": "malformed_target_metadata",
            "detail": "malformed_responds_to",
        }
    response_path = (
        _thread_file_by_rel_path(project_root, files, response_reference)
        if response_reference is not None
        else None
    )
    if response_reference is not None and response_path is None:
        return {
            "satisfied": False,
            "reason": "malformed_target_metadata",
            "detail": "cross_thread_responds_to",
        }
    if response_path is None:
        verdict_index = files.index(verdict_path)
        response_path = files[verdict_index - 1] if verdict_index > 0 else None
    if (
        response_path is not None
        and _status_from_bridge_file(response_path) == "NO-ACTION"
    ):
        return {
            "satisfied": False,
            "reason": "no_action_verified",
            "detail": _bridge_rel_path(project_root, response_path),
        }

    proposal_path = _approved_proposal_file(project_root, slug, verdict_path, files)
    if proposal_path is None:
        return {
            "satisfied": True,
            "reason": "genuinely_closable",
            "mode": "legacy_or_bridge_only",
        }
    target_paths, error = _parse_target_path_metadata(_read_bridge_text(proposal_path))
    if error:
        return {
            "satisfied": False,
            "reason": "malformed_target_metadata",
            "detail": error,
            "proposal_path": _bridge_rel_path(project_root, proposal_path),
        }
    if (
        target_paths is None
        or not target_paths
        or all(path.startswith("bridge/") for path in target_paths)
    ):
        return {
            "satisfied": True,
            "reason": "genuinely_closable",
            "mode": "legacy_or_bridge_only",
        }

    non_bridge_targets = tuple(
        path for path in target_paths if not path.startswith("bridge/")
    )
    coverage = _terminal_verdict_commit_coverage(
        project_root,
        verdict_rel_path,
        non_bridge_targets,
        git_provenance_index=git_provenance_index,
    )
    if (
        _report_has_by_reference_waiver(response_path)
        and verdict_rel_path not in coverage["missing_paths"]
    ):
        return {
            "satisfied": True,
            "reason": "genuinely_closable",
            "mode": "by_reference_waiver",
            "commit_coverage": coverage,
        }
    if not coverage["covered"]:
        return {
            "satisfied": False,
            "reason": "missing_implementation_commit_coverage",
            "detail": coverage["verdict_state"],
            "commit_coverage": coverage,
        }
    return {
        "satisfied": True,
        "reason": "genuinely_closable",
        "mode": "focused_commit",
        "commit_coverage": coverage,
    }


def _child_thread_slugs(
    slug: str, bridge_statuses: dict[str, dict[str, str]]
) -> list[str]:
    """Return indexed thread slugs that are children of ``slug`` (``<slug>-*``).

    Child enumeration is a DISTINCT operation from parent-thread file
    enumeration (WI-4704 GO Condition 1): a child slug shares the parent slug as
    a prefix but is its own thread with its own versioned chain. A satisfied
    umbrella never rewrites the parent thread's own status to ``VERIFIED``.
    """

    prefix = f"{slug}-"
    return sorted(
        candidate
        for candidate in bridge_statuses
        if candidate != slug and candidate.startswith(prefix)
    )


def build_work_item_bridge_links(
    project_root: Path,
    bridge_statuses: dict[str, dict[str, str]],
    *,
    file_index: dict[str, list[Path]] | None = None,
) -> dict[str, list[str]]:
    """Derive the reverse work-item -> [bridge slug] index from bridge files.

    Bridge files carry a canonical ``Work Item: WI-XXXX`` metadata line that
    declares the thread's parent work item (file -> WI). MemBase work items do
    not always carry the inverse ``related_bridge_threads`` link, so a VERIFIED
    bridge can never reach an unlinked WI through ``related_bridge_threads``
    alone. This builds the inverse map by scanning each indexed slug's files for
    the metadata line only (never prose WI mentions), so the reconciler can
    supplement a WI's links with the slugs that explicitly declare it.

    ``file_index`` (from ``_index_bridge_thread_files``) is reused when provided
    so the bridge directory is scanned once for the whole batch rather than once
    per slug (WI-4704 verification F1 scale fix).
    """

    if file_index is None:
        file_index = _index_bridge_thread_files(project_root)
    index: dict[str, set[str]] = {}
    for slug in bridge_statuses:
        for path in _bridge_thread_files(project_root, slug, file_index=file_index):
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                text = path.read_text(encoding="utf-8", errors="replace")
            for match in _WORK_ITEM_METADATA_RE.finditer(text):
                work_item_id = match.group(1).upper()
                index.setdefault(work_item_id, set()).add(slug)
    return {work_item_id: sorted(slugs) for work_item_id, slugs in index.items()}


def _contains_work_item_id(text: str, work_item_id: str) -> bool:
    escaped = re.escape(work_item_id)
    return bool(re.search(rf"(?<![A-Za-z0-9_.-]){escaped}(?![A-Za-z0-9_.-])", text))


def bridge_thread_has_parent_evidence(
    project_root: Path,
    slug: str,
    work_item_id: str,
    *,
    file_index: dict[str, list[Path]] | None = None,
) -> dict[str, Any]:
    """Return explicit evidence that a bridge thread covers the work item.

    related_bridge_threads is a broad linkage field. For mechanical closure we
    require the bridge thread chain itself to carry the exact work item ID.
    ``file_index`` is reused when provided to avoid a per-call directory scan.
    """

    files = _bridge_thread_files(project_root, slug, file_index=file_index)
    matched_files: list[str] = []
    for path in files:
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = path.read_text(encoding="utf-8", errors="replace")
        if _contains_work_item_id(text, work_item_id):
            matched_files.append(str(path.relative_to(project_root)).replace("\\", "/"))
    return {
        "has_parent_evidence": bool(matched_files),
        "files_checked": [
            str(path.relative_to(project_root)).replace("\\", "/") for path in files
        ],
        "matched_files": matched_files,
    }


def bridge_thread_declares_work_item(
    project_root: Path,
    slug: str,
    work_item_id: str,
    *,
    file_index: dict[str, list[Path]] | None = None,
) -> bool:
    """Return True if the thread's exact versioned chain canonically declares the WI.

    Canonical evidence is the ``Work Item: WI-XXXX`` metadata line only (WI-4704
    GO Condition 2). A prose mention, a bare ``related_bridge_threads``
    membership, or a prefix-sibling file never counts. This is the only evidence
    form the WI-4704 parent-evidence relaxation and umbrella-closure paths accept.
    ``file_index`` is reused when provided to avoid a per-call directory scan.
    """

    target = work_item_id.upper()
    for path in _bridge_thread_files(project_root, slug, file_index=file_index):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = path.read_text(encoding="utf-8", errors="replace")
        for match in _WORK_ITEM_METADATA_RE.finditer(text):
            if match.group(1).upper() == target:
                return True
    return False


def bridge_thread_is_advisory_kind(
    project_root: Path, slug: str, *, file_index: dict[str, list[Path]] | None = None
) -> bool:
    """Return True only for threads explicitly marked as advisory/planning work."""

    for path in _bridge_thread_files(project_root, slug, file_index=file_index):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = path.read_text(encoding="utf-8", errors="replace")
        for match in _BRIDGE_KIND_RE.finditer(text):
            if "advisory" in match.group(1).lower():
                return True
        if _ADVISORY_GO_TEXT_RE.search(text):
            return True
    return False


def bridge_thread_is_non_implementation_link(
    project_root: Path,
    slug: str,
    status: str,
    *,
    file_index: dict[str, list[Path]] | None = None,
) -> bool:
    """Return True for terminal/advisory links that should not block closure."""

    if status in {"ADVISORY", "WITHDRAWN"}:
        return True
    return status == "GO" and bridge_thread_is_advisory_kind(
        project_root, slug, file_index=file_index
    )


def umbrella_satisfaction(
    project_root: Path,
    slug: str,
    work_item_id: str,
    bridge_statuses: dict[str, dict[str, str]],
    *,
    file_index: dict[str, list[Path]] | None = None,
    verified_closure_cache: dict[str, dict[str, Any]] | None = None,
    git_provenance_index: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Evaluate whether non-VERIFIED ``slug`` is a satisfied umbrella for the WI.

    A non-VERIFIED parent thread is a satisfied umbrella only when it has at
    least one child thread, EVERY child is latest ``VERIFIED``, and at least one
    child canonically declares this work item (WI-4704 GO Conditions 1 and 2).
    The parent thread's own status is never rewritten to ``VERIFIED``; child
    evidence supports the umbrella resolution path only. An umbrella child set
    where only unrelated children are VERIFIED, or where no child declares the
    WI, is not satisfied.
    """

    children = _child_thread_slugs(slug, bridge_statuses)
    all_children_verified = bool(children) and all(
        bridge_statuses[child]["status"] == "VERIFIED" for child in children
    )
    if verified_closure_cache is None:
        verified_closure_cache = {}
    child_closure_evidence: dict[str, dict[str, Any]] = {}
    if all_children_verified:
        for child in children:
            if child not in verified_closure_cache:
                verified_closure_cache[child] = verified_thread_closure_evidence(
                    project_root,
                    child,
                    file_index=file_index,
                    git_provenance_index=git_provenance_index,
                )
            child_closure_evidence[child] = verified_closure_cache[child]
    all_children_closable = all_children_verified and all(
        evidence["satisfied"] for evidence in child_closure_evidence.values()
    )
    declaring_children = (
        [
            child
            for child in children
            if bridge_thread_declares_work_item(
                project_root, child, work_item_id, file_index=file_index
            )
        ]
        if all_children_closable
        else []
    )
    return {
        "satisfied": all_children_closable and bool(declaring_children),
        "children": children,
        "all_children_verified": all_children_verified,
        "all_children_closable": all_children_closable,
        "child_closure_evidence": child_closure_evidence,
        "declaring_children": declaring_children,
    }


def _completion_evidence(current: dict[str, Any], row: dict[str, Any]) -> str:
    slugs = row["recognized_bridge_threads"]
    reason = row.get("reason")
    if reason == "umbrella_children_all_verified":
        evidence = (
            "Bridge VERIFIED backlog reconciler resolved this work item because the "
            "recognized parent bridge threads are all satisfied: any GO umbrella thread "
            "has every child thread latest VERIFIED with at least one child canonically "
            "declaring this work item, and any directly-VERIFIED thread carries work-item "
            f"evidence: {', '.join(slugs)}. Source: "
            "DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM (WI-4704 umbrella auto-closure)."
        )
    elif reason == "parent_evidence_canonical_relaxed":
        evidence = (
            "Bridge VERIFIED backlog reconciler resolved this work item because all "
            "recognized parent bridge threads are latest VERIFIED and at least one "
            "canonically declares this work item via its Work Item metadata line: "
            f"{', '.join(slugs)}. Source: "
            "DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM (WI-4704 parent-evidence relaxation)."
        )
    elif reason == "non_implementation_links_ignored":
        implementation = ", ".join(
            row.get("satisfied_implementation_bridge_threads", [])
        )
        non_implementation = ", ".join(row.get("non_blocking_bridge_threads", []))
        evidence = (
            "Bridge VERIFIED backlog reconciler resolved this work item because at least one "
            "recognized implementation bridge thread is satisfied by VERIFIED evidence "
            f"({implementation}) and the remaining linked non-implementation bridge threads "
            f"are terminal/advisory traceability links that do not block closure ({non_implementation}). "
            "Source: DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM and WI-4535 "
            "advisory-link resolution."
        )
    else:
        evidence = (
            "Bridge VERIFIED backlog reconciler resolved this work item because "
            "all recognized parent implementation bridge threads are latest VERIFIED "
            "and carry explicit work-item evidence: "
            f"{', '.join(slugs)}. Source: "
            "DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM."
        )
    existing = current.get("completion_evidence")
    if isinstance(existing, str) and existing.strip():
        return f"{existing.rstrip()}\n{evidence}"
    return evidence


def classify_work_item(
    item: dict[str, Any],
    bridge_statuses: dict[str, dict[str, str]],
    *,
    project_root: Path = PROJECT_ROOT,
    ignore_terminal: bool = False,
    derived_links: dict[str, list[str]] | None = None,
    file_index: dict[str, list[Path]] | None = None,
    verified_closure_cache: dict[str, dict[str, Any]] | None = None,
    git_provenance_index: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if file_index is None:
        file_index = _index_bridge_thread_files(project_root)
    if verified_closure_cache is None:
        verified_closure_cache = {}
    raw_links = item.get(
        "related_bridge_threads_parsed", item.get("related_bridge_threads")
    )
    parsed_links = parse_related_bridge_threads(raw_links)
    if derived_links:
        for slug in derived_links.get(item["id"], []):
            if slug not in parsed_links:
                parsed_links.append(slug)
    recognized = [slug for slug in parsed_links if slug in bridge_statuses]
    missing = [slug for slug in parsed_links if slug not in bridge_statuses]
    statuses = {slug: bridge_statuses[slug]["status"] for slug in recognized}
    parent_evidence = {
        slug: bridge_thread_has_parent_evidence(
            project_root, slug, item["id"], file_index=file_index
        )
        for slug in recognized
        if statuses.get(slug) == "VERIFIED"
    }
    missing_parent_evidence = [
        slug
        for slug in recognized
        if statuses.get(slug) == "VERIFIED"
        and not parent_evidence[slug]["has_parent_evidence"]
    ]
    verified_closure_evidence: dict[str, dict[str, Any]] = {}
    for slug in recognized:
        if statuses.get(slug) != "VERIFIED":
            continue
        if slug not in verified_closure_cache:
            verified_closure_cache[slug] = verified_thread_closure_evidence(
                project_root,
                slug,
                file_index=file_index,
                git_provenance_index=git_provenance_index,
            )
        verified_closure_evidence[slug] = verified_closure_cache[slug]
    # Class 1 (WI-4704): a non-VERIFIED recognized link may still be satisfied
    # when it is an umbrella whose children are ALL VERIFIED and at least one
    # child canonically declares this work item. The parent's own status is
    # never rewritten to VERIFIED.
    umbrella_evidence = {
        slug: umbrella_satisfaction(
            project_root,
            slug,
            item["id"],
            bridge_statuses,
            file_index=file_index,
            verified_closure_cache=verified_closure_cache,
            git_provenance_index=git_provenance_index,
        )
        for slug in recognized
        if statuses.get(slug) != "VERIFIED"
    }
    umbrella_satisfied_slugs = [
        slug for slug, ev in umbrella_evidence.items() if ev["satisfied"]
    ]
    non_blocking_bridge_threads = [
        slug
        for slug in recognized
        if statuses.get(slug) != "VERIFIED"
        and slug not in umbrella_satisfied_slugs
        and bridge_thread_is_non_implementation_link(
            project_root, slug, statuses[slug], file_index=file_index
        )
    ]
    unsatisfied_non_verified = [
        slug
        for slug in recognized
        if statuses.get(slug) != "VERIFIED"
        and slug not in umbrella_satisfied_slugs
        and slug not in non_blocking_bridge_threads
    ]
    # Class 2 (WI-4704): canonical parent-evidence relaxation. When all links are
    # otherwise satisfied but some VERIFIED link lacks the broad WI-id evidence,
    # the work item still resolves if at least one VERIFIED link canonically
    # declares it via the ``Work Item: WI-XXXX`` metadata line. Prose mentions and
    # bare related_bridge_threads membership never satisfy this floor.
    canonical_evidence_threads = [
        slug
        for slug in recognized
        if statuses.get(slug) == "VERIFIED"
        and bridge_thread_declares_work_item(
            project_root, slug, item["id"], file_index=file_index
        )
    ]
    satisfied_verified_threads = [
        slug
        for slug in recognized
        if statuses.get(slug) == "VERIFIED"
        and verified_closure_evidence[slug]["satisfied"]
        and (slug not in missing_parent_evidence or slug in canonical_evidence_threads)
    ]
    satisfied_implementation_threads = sorted(
        set(satisfied_verified_threads + umbrella_satisfied_slugs)
    )
    blocking_closure_reasons = [
        evidence["reason"]
        for evidence in verified_closure_evidence.values()
        if not evidence["satisfied"]
    ]
    for evidence in umbrella_evidence.values():
        blocking_closure_reasons.extend(
            child_evidence["reason"]
            for child_evidence in evidence.get("child_closure_evidence", {}).values()
            if not child_evidence["satisfied"]
        )
    closure_reason = next(
        (
            reason
            for reason in _CLOSURE_REASON_PRIORITY
            if reason in blocking_closure_reasons
        ),
        "genuinely_closable" if satisfied_implementation_threads else None,
    )

    if (
        not ignore_terminal
        and item.get("resolution_status") in WORK_ITEM_TERMINAL_RESOLUTION_STATUSES
    ):
        action = "skip"
        reason = "terminal_work_item"
    elif not parsed_links:
        action = "skip"
        reason = "no_related_bridge_threads"
    elif missing:
        action = "skip"
        reason = "missing_bridge_document"
    elif not recognized:
        action = "skip"
        reason = "unrecognized_only"
    elif closure_reason in _CLOSURE_REASON_PRIORITY:
        action = "skip"
        reason = closure_reason
    elif (
        unsatisfied_non_verified
        or non_blocking_bridge_threads
        and not satisfied_implementation_threads
    ):
        action = "skip"
        reason = "linked_bridge_not_verified"
    elif missing_parent_evidence and not canonical_evidence_threads:
        action = "skip"
        reason = "missing_parent_evidence"
    else:
        action = "resolve"
        if non_blocking_bridge_threads:
            reason = "non_implementation_links_ignored"
        elif umbrella_satisfied_slugs:
            reason = "umbrella_children_all_verified"
        elif missing_parent_evidence:
            reason = "parent_evidence_canonical_relaxed"
        else:
            reason = "all_parent_links_verified"

    return {
        "id": item["id"],
        "title": item.get("title"),
        "resolution_status": item.get("resolution_status"),
        "stage": item.get("stage"),
        "related_bridge_threads": parsed_links,
        "recognized_bridge_threads": recognized,
        "missing_bridge_threads": missing,
        "bridge_statuses": statuses,
        "parent_evidence": parent_evidence,
        "verified_closure_evidence": verified_closure_evidence,
        "closure_reason": closure_reason,
        "missing_parent_evidence": missing_parent_evidence,
        "umbrella_evidence": umbrella_evidence,
        "umbrella_satisfied": umbrella_satisfied_slugs,
        "non_blocking_bridge_threads": non_blocking_bridge_threads,
        "canonical_evidence_threads": canonical_evidence_threads,
        "satisfied_implementation_bridge_threads": satisfied_implementation_threads,
        "action": action,
        "reason": reason,
    }


def classify_reconciler_resolution(
    item: dict[str, Any],
    bridge_statuses: dict[str, dict[str, str]],
    *,
    project_root: Path = PROJECT_ROOT,
    derived_links: dict[str, list[str]] | None = None,
    file_index: dict[str, list[Path]] | None = None,
    verified_closure_cache: dict[str, dict[str, Any]] | None = None,
    git_provenance_index: dict[str, Any] | None = None,
) -> dict[str, Any]:
    strict = classify_work_item(
        item,
        bridge_statuses,
        project_root=project_root,
        ignore_terminal=True,
        derived_links=derived_links,
        file_index=file_index,
        verified_closure_cache=verified_closure_cache,
        git_provenance_index=git_provenance_index,
    )
    if strict["action"] == "resolve":
        action = "keep_resolved"
        reason = "strict_parent_evidence_satisfied"
    else:
        action = "reopen"
        reason = f"overbroad_resolution_{strict['reason']}"
    return {**strict, "action": action, "reason": reason}


def _copy_work_item_version(
    db: KnowledgeDB,
    source: dict[str, Any],
    *,
    changed_by: str,
    change_reason: str,
) -> dict[str, Any] | None:
    kwargs = {field: source.get(field) for field in WORK_ITEM_BACKLOG_FIELDS}
    return db.insert_work_item(
        source["id"],
        source["title"],
        source["origin"],
        source["component"],
        source["resolution_status"],
        changed_by,
        change_reason,
        description=source.get("description"),
        source_spec_id=source.get("source_spec_id"),
        source_test_id=source.get("source_test_id"),
        failure_description=source.get("failure_description"),
        priority=source.get("priority"),
        stage=source.get("stage", "backlogged"),
        **kwargs,
    )


def _previous_nonterminal_version(
    db: KnowledgeDB, item_id: str
) -> dict[str, Any] | None:
    for row in db.get_work_item_history(item_id)[1:]:
        if row.get("resolution_status") not in WORK_ITEM_TERMINAL_RESOLUTION_STATUSES:
            return row
    return None


def _revalidate_work_item_for_resolution(
    project_root: Path,
    item: dict[str, Any],
    *,
    git_provenance_index: dict[str, Any] | None = None,
) -> dict[str, Any]:
    fresh_bridge_statuses = collect_latest_bridge_statuses(project_root)
    fresh_file_index = _index_bridge_thread_files(project_root)
    fresh_derived_links = build_work_item_bridge_links(
        project_root,
        fresh_bridge_statuses,
        file_index=fresh_file_index,
    )
    return classify_work_item(
        item,
        fresh_bridge_statuses,
        project_root=project_root,
        derived_links=fresh_derived_links,
        file_index=fresh_file_index,
        git_provenance_index=git_provenance_index,
    )


def reconcile(
    *,
    project_root: Path = PROJECT_ROOT,
    db_path: Path | None = None,
    apply: bool = False,
    repair_overbroad: bool = False,
) -> dict[str, Any]:
    root = project_root.resolve()
    database_path = db_path or root / "groundtruth.db"

    bridge_statuses = collect_latest_bridge_statuses(root)
    file_index = _index_bridge_thread_files(root)
    derived_links = build_work_item_bridge_links(
        root, bridge_statuses, file_index=file_index
    )
    git_provenance_index = build_git_provenance_index(root)
    verified_closure_cache: dict[str, dict[str, Any]] = {}
    db = KnowledgeDB(database_path)
    resolved_ids: list[str] = []
    reopened_ids: list[str] = []
    errors: list[dict[str, str]] = []
    repair_inventory: list[dict[str, Any]] = []
    try:
        candidates = [
            item
            for item in db.get_open_work_items()
            if item.get("related_bridge_threads")
            or item.get("related_bridge_threads_parsed")
            or derived_links.get(item["id"])
        ]
        inventory = [
            classify_work_item(
                item,
                bridge_statuses,
                project_root=root,
                derived_links=derived_links,
                file_index=file_index,
                verified_closure_cache=verified_closure_cache,
                git_provenance_index=git_provenance_index,
            )
            for item in candidates
        ]
        items_by_id = {item["id"]: item for item in candidates}
        if apply:
            for index, row in enumerate(inventory):
                if row["action"] != "resolve":
                    continue
                try:
                    current = db.get_work_item(row["id"]) or items_by_id[row["id"]]
                    row = _revalidate_work_item_for_resolution(
                        root,
                        current,
                        git_provenance_index=git_provenance_index,
                    )
                    inventory[index] = row
                    if row["action"] != "resolve":
                        continue
                    db.update_work_item(
                        row["id"],
                        CHANGED_BY,
                        CHANGE_REASON,
                        owner_approved=True,
                        resolution_status="resolved",
                        stage="resolved",
                        completion_evidence=_completion_evidence(current, row),
                    )
                    resolved_ids.append(row["id"])
                except (
                    Exception
                ) as exc:  # pragma: no cover - defensive runtime reporting
                    errors.append({"id": row["id"], "error": str(exc)})
        if repair_overbroad:
            reconciler_resolutions = [
                item
                for item in db.list_work_items(resolution_status="resolved")
                if item.get("changed_by") == CHANGED_BY
            ]
            repair_inventory = [
                classify_reconciler_resolution(
                    item,
                    bridge_statuses,
                    project_root=root,
                    derived_links=derived_links,
                    file_index=file_index,
                    verified_closure_cache=verified_closure_cache,
                    git_provenance_index=git_provenance_index,
                )
                for item in reconciler_resolutions
            ]
            if apply:
                for row in repair_inventory:
                    if row["action"] != "reopen":
                        continue
                    try:
                        previous = _previous_nonterminal_version(db, row["id"])
                        if previous is None:
                            errors.append(
                                {
                                    "id": row["id"],
                                    "error": "no_previous_nonterminal_version",
                                }
                            )
                            continue
                        _copy_work_item_version(
                            db,
                            previous,
                            changed_by=REPAIR_CHANGED_BY,
                            change_reason=REPAIR_CHANGE_REASON,
                        )
                        reopened_ids.append(row["id"])
                    except (
                        Exception
                    ) as exc:  # pragma: no cover - defensive runtime reporting
                        errors.append({"id": row["id"], "error": str(exc)})
    finally:
        db.close()

    mode = "apply" if apply else "dry-run"
    if repair_overbroad:
        mode = f"{mode}+repair-overbroad"
    return {
        "project_root": str(root),
        "db_path": str(database_path),
        "bridge_state": str(root / "bridge"),
        "mode": mode,
        "bridge_document_count": len(bridge_statuses),
        "candidate_count": len(inventory),
        "would_resolve_ids": [
            row["id"] for row in inventory if row["action"] == "resolve"
        ],
        "resolved_ids": resolved_ids,
        "repair_candidate_count": len(repair_inventory),
        "would_reopen_ids": [
            row["id"] for row in repair_inventory if row["action"] == "reopen"
        ],
        "reopened_ids": reopened_ids,
        "errors": errors,
        "candidates": inventory,
        "repair_candidates": repair_inventory,
    }


def render_text(summary: dict[str, Any]) -> str:
    lines = [
        "Bridge VERIFIED backlog reconciler",
        f"mode: {summary['mode']}",
        f"candidates: {summary['candidate_count']}",
        f"would_resolve_ids: {summary['would_resolve_ids']}",
        f"resolved_ids: {summary['resolved_ids']}",
        f"repair_candidates: {summary['repair_candidate_count']}",
        f"would_reopen_ids: {summary['would_reopen_ids']}",
        f"reopened_ids: {summary['reopened_ids']}",
    ]
    if summary["errors"]:
        lines.append(f"errors: {summary['errors']}")
    for row in summary["candidates"]:
        lines.append(
            "- {id}: {action} ({reason}); closure_reason={closure_reason}; status={resolution_status}; "
            "stage={stage}; links={recognized_bridge_threads}; "
            "bridge_statuses={bridge_statuses}".format(**row)
        )
    for row in summary["repair_candidates"]:
        lines.append(
            "- repair {id}: {action} ({reason}); closure_reason={closure_reason}; status={resolution_status}; "
            "stage={stage}; links={recognized_bridge_threads}; "
            "missing_parent_evidence={missing_parent_evidence}".format(**row)
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--dry-run",
        action="store_true",
        help="Report candidates without mutating MemBase.",
    )
    mode.add_argument(
        "--apply", action="store_true", help="Resolve eligible work items."
    )
    parser.add_argument(
        "--repair-overbroad",
        action="store_true",
        help="Audit reconciler-resolved rows and reopen ones without strict parent evidence.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress normal output unless errors occur.",
    )
    parser.add_argument(
        "--json", action="store_true", help="Emit machine-readable JSON."
    )
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--db-path", type=Path)
    args = parser.parse_args(argv)

    summary = reconcile(
        project_root=args.project_root,
        db_path=args.db_path,
        apply=args.apply,
        repair_overbroad=args.repair_overbroad,
    )
    if not args.quiet or summary["errors"]:
        if args.json:
            print(json.dumps(summary, indent=2, sort_keys=True))
        else:
            print(render_text(summary))
    return 1 if summary["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
