# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Helper utilities for Loyal Opposition verdict authoring."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
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
from groundtruth_kb.bridge.vocabulary import (  # noqa: E402
    LOYAL_OPPOSITION_ACTIONABLE_STATUSES,
)

from scripts.bridge_author_metadata import (  # noqa: E402
    extract_author_metadata,
    is_synthetic_session_context_id,
)
from scripts.gtkb_session_id import (  # noqa: E402
    resolve_session_id,
    sanitize_session_id,
)
from scripts.verdict_evidence_anchor_preflight import (  # noqa: E402
    validate_verdict_evidence_anchors,
    violation_summary,
)
from scripts.windows_subprocess import no_window_subprocess_kwargs  # noqa: E402

# Canon s17: helper scratch is session-scoped under the canonical scratchpad
# root, never `.gtkb-state`. Session id resolution reuses the single membership
# authority in `scripts.gtkb_session_id` rather than re-listing the env vars.
DEFAULT_VERDICT_PREPOPULATION_LOG = (
    Path("scratchpad") / sanitize_session_id(resolve_session_id()) / "bridge-verify-helper" / "last-prepopulation.json"
)
STATUS_RE = re.compile(
    r"^(NEW|REVISED|GO|NO-GO|NO-ACTION|VERDICT-REJECTED|VERIFIED|WITHDRAWN|ADVISORY|IMPLEMENTED|READY|NOT-READY|SUPERSEDED|BLOCKED)$"
)
VERSIONED_BRIDGE_RE_TEMPLATE = r"^{slug}-(?P<version>\d{{3}})\.md$"
RECOMMENDED_COMMIT_TYPE_RE = re.compile(r"Recommended commit type\s*:", re.IGNORECASE)
UNRESOLVED_PLACEHOLDER_RE = re.compile(
    r"\bPLACEHOLDER(?:_[A-Z0-9]+)+\b|<fill in [^>\n]+>",
    re.IGNORECASE,
)
FAILED_PREFLIGHT_RE = re.compile(r"(?im)^\s*(?:[-*]\s*)?[`\"']?preflight_passed[`\"']?\s*[:=]\s*[`\"']?false[`\"']?\b")
MISSING_REQUIRED_SPECS_RE = re.compile(
    r"(?im)^\s*(?:[-*]\s*)?[`\"']?missing_required_specs[`\"']?\s*[:=]\s*(?P<value>[^\n]*)$"
)
WINDOWS_ABSOLUTE_PATH_RE = re.compile(r"(?<![\w`])(?P<path>[A-Za-z]:[\\/][^\s`|<>'\"]+)")
FENCED_CODE_BLOCK_RE = re.compile(r"```[^\n]*\n(?P<body>.*?)(?:\n```|$)", re.DOTALL)
TARGET_PATHS_DECL_RE = re.compile(r"(?im)^\s*(?:[-*]\s*)?`?target_paths`?\s*[:=]\s*(?P<value>\[[^\n]+\])")
PATCH_SHA256_DECL_RE = re.compile(r"(?i)\b(?:patch\s+)?sha-?256\b[^0-9a-f]*(?P<value>[0-9a-f]{64})")
PATCH_SIZE_DECL_RE = re.compile(r"(?i)\b(?:patch\s+)?size\b[^0-9]*(?P<value>\d+)\s*(?:bytes?)?")
REPORT_PATH_TOKEN_RE = re.compile(
    r"`(?P<code>[^`\n]+)`|(?P<plain>(?<![\w./-])(?:\.?/?(?:scripts|groundtruth-kb|platform_tests|tests|config|"
    r"\.claude|\.codex|\.cursor|\.github|\.githooks|bridge|applications)/[^\s`|<>'\"]+|"
    r"pyproject\.toml|groundtruth\.toml|groundtruth\.db))"
)
EVIDENCE_SECTION_HEADINGS = (
    "Applicability Preflight",
    "Clause Applicability",
    "Preflight Evidence",
    "Verification Evidence",
    "Command Output",
    "Commands Executed",
    "Commit Finalization Evidence",
)


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


@dataclass(frozen=True)
class HunkPatch:
    """A reviewed patch file plus the repo paths it touches."""

    path: Path
    touched_paths: tuple[str, ...]
    sha256: str
    size_bytes: int


@dataclass(frozen=True)
class IndexEntry:
    """One stage entry from a Git index."""

    mode: str
    object_id: str
    stage: int


@dataclass(frozen=True)
class RealIndexRealignmentPlan:
    """Exact real-index state required after a disposable-index commit."""

    committed_paths: tuple[str, ...]
    entries_before: dict[str, tuple[IndexEntry, ...]]
    expected_entries: dict[str, tuple[IndexEntry, ...]]
    preserved_overlap: tuple[str, ...]


def append_skills_applied_disclosure(body: str, skills: list[str] | None) -> str:
    """Append the canonical Skills applied line when *skills* is not None (report-only)."""
    if skills is None:
        return body
    from scripts.skill_disclosure import format_skills_applied

    return body.rstrip() + "\n\n" + format_skills_applied(skills) + "\n"


def seed_prior_deliberations(
    slug: str,
    body: str,
    *,
    db: Any | bool | None = None,
    glossary_path: Path | None = None,
    log_path: Path | bool | None = DEFAULT_VERDICT_PREPOPULATION_LOG,
    pre_populate: bool = True,
    project_root: Path | None = None,
) -> str:
    """Seed a verdict body's ``## Prior Deliberations`` section."""
    seeded = (
        pre_populate_prior_deliberations(
            slug,
            body,
            db=db,
            glossary_path=glossary_path,
            log_path=log_path,
        )
        if pre_populate
        else body
    )
    _assert_verdict_evidence_anchors(seeded, project_root=project_root)
    return seeded


def _project_root_from_arg(value: Path | None) -> Path:
    return (value or PROJECT_ROOT).resolve()


def _assert_verdict_evidence_anchors(body: str, *, project_root: Path | None = None) -> None:
    """Fail closed when a gated verdict carries fabricated operative anchors."""
    root = _project_root_from_arg(project_root)
    violations = validate_verdict_evidence_anchors(body, project_root=root)
    if violations:
        raise VerifiedFinalizationError(
            "verdict evidence anchors are invalid: "
            + violation_summary(violations)
            + ". Fix the citation, or mark the finding [inference] / [no exact anchor] / [absent]."
        )


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
        head = [line.strip() for line in lines if line.strip()][:3]
        status = next((line for line in head if STATUS_RE.fullmatch(line)), "")
        if not status:
            raise VerifiedFinalizationError(
                f"Bridge file has no status token in its first three lines: {path}: {head!r}"
            )
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
    if latest.status not in LOYAL_OPPOSITION_ACTIONABLE_STATUSES:
        raise VerifiedFinalizationError(
            "VERIFIED finalization requires a post-implementation report latest "
            f"status in {sorted(LOYAL_OPPOSITION_ACTIONABLE_STATUSES)}; "
            f"got {latest.status} at {latest.rel_path}."
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


def _reject_unresolved_placeholders(body: str) -> None:
    match = UNRESOLVED_PLACEHOLDER_RE.search(body)
    if match is not None:
        raise VerifiedFinalizationError(
            f"VERIFIED verdict body contains unresolved placeholder evidence: {match.group(0)!r}."
        )


def _reject_failed_preflight_evidence(body: str) -> None:
    match = FAILED_PREFLIGHT_RE.search(body)
    if match is not None:
        raise VerifiedFinalizationError("VERIFIED verdict body embeds failed preflight evidence.")
    for match in MISSING_REQUIRED_SPECS_RE.finditer(body):
        value = match.group("value").strip().strip("`").rstrip(",")
        if value != "[]":
            raise VerifiedFinalizationError(
                "VERIFIED verdict body embeds preflight evidence with non-empty missing_required_specs."
            )


def _evidence_spans(body: str) -> tuple[str, ...]:
    spans: list[str] = []
    for match in FENCED_CODE_BLOCK_RE.finditer(body):
        spans.append(match.group("body"))
    for heading in EVIDENCE_SECTION_HEADINGS:
        section = _section_body(body, heading)
        if section:
            spans.append(section)
    return tuple(spans)


def _path_within_project_root(path_text: str, project_root: Path) -> bool:
    try:
        path = Path(path_text).resolve()
        path.relative_to(project_root.resolve())
    except (OSError, ValueError):
        return False
    return True


def _reject_out_of_root_evidence_paths(body: str, project_root: Path) -> None:
    for span in _evidence_spans(body):
        for match in WINDOWS_ABSOLUTE_PATH_RE.finditer(span):
            path_text = match.group("path").rstrip(".,;:)]}")
            if not _path_within_project_root(path_text, project_root):
                raise VerifiedFinalizationError(
                    f"VERIFIED verdict body embeds out-of-root path evidence: {path_text!r} is outside {project_root}."
                )


def validate_verified_body(body: str, *, project_root: Path | None = None) -> None:
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
    root = _project_root_from_arg(project_root)
    _reject_unresolved_placeholders(body)
    _reject_failed_preflight_evidence(body)
    _reject_out_of_root_evidence_paths(body, root)
    _assert_verdict_evidence_anchors(body, project_root=root)


def _normalize_repo_path(project_root: Path, path_text: str) -> str:
    raw = path_text.strip().strip("'\"").rstrip(".,;:)]}")
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


def _looks_like_claimed_repo_path(path_text: str) -> bool:
    raw = path_text.strip().rstrip(".,;:)]}")
    if not raw or " " in raw:
        return False
    return bool(
        raw.startswith(
            (
                "./scripts/",
                "scripts/",
                "./groundtruth-kb/",
                "groundtruth-kb/",
                "./platform_tests/",
                "platform_tests/",
                "./tests/",
                "tests/",
                "./config/",
                "config/",
                "./.claude/",
                ".claude/",
                "./.codex/",
                ".codex/",
                "./.cursor/",
                ".cursor/",
                "./.github/",
                ".github/",
                "./.githooks/",
                ".githooks/",
                "./bridge/",
                "bridge/",
                "./applications/",
                "applications/",
            )
        )
        or raw in {"pyproject.toml", "groundtruth.toml", "groundtruth.db"}
    )


def _claimed_paths_from_report(report_text: str, project_root: Path) -> tuple[str, ...]:
    paths: list[str] = []
    for heading in (
        "Files Changed",
        "Changed Files",
        "Implementation Files",
        "Implementation Path Set",
        "Implementation Report Path Set",
    ):
        section = _section_body(report_text, heading)
        if not section:
            continue
        for match in REPORT_PATH_TOKEN_RE.finditer(section):
            candidate = match.group("code") or match.group("plain") or ""
            if _looks_like_claimed_repo_path(candidate):
                if "*" not in candidate and not candidate.strip().endswith("/"):
                    paths.append(candidate)
    return _unique_paths(project_root, paths)


def _report_has_by_reference_finalization_waiver(report_text: str) -> bool:
    waiver_sections = [
        _section_body(report_text, "By-Reference Finalization Waiver"),
        _section_body(report_text, "Finalization Waiver"),
        _section_body(report_text, "Owner Decisions / Input"),
    ]
    text = "\n".join(section for section in waiver_sections if section).lower()
    if not text:
        return False
    return "by-reference" in text and "waiver" in text and ("owner" in text or "delib-" in text)


def _assert_include_set_covers_report_claims(
    *,
    slug: str,
    project_root: Path,
    latest_report_rel_path: str,
    include_paths: list[str],
) -> None:
    report_path = project_root / latest_report_rel_path
    try:
        report_text = report_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise VerifiedFinalizationError(
            f"Could not read latest implementation report: {latest_report_rel_path}"
        ) from exc
    if _report_has_by_reference_finalization_waiver(report_text):
        return
    claimed = set(_claimed_paths_from_report(report_text, project_root))
    if not claimed:
        return
    include_set = set(_unique_paths(project_root, include_paths))
    missing = sorted(claimed - include_set)
    if missing:
        joined = ", ".join(missing)
        raise VerifiedFinalizationError(
            "VERIFIED finalization include set omits path(s) claimed by latest implementation report "
            f"for {slug!r}: {joined}"
        )


def _assert_predecessor_chain_committed(
    slug: str,
    project_root: Path,
    next_version: int,
    transaction_paths: tuple[str, ...],
) -> None:
    transaction_set = set(transaction_paths)
    problems: list[str] = []
    for version in range(1, next_version):
        rel_path = f"bridge/{slug}-{version:03d}.md"
        abs_path = project_root / rel_path
        if not abs_path.is_file():
            history = _run_git(["log", "--format=%H", "--max-count=1", "--", rel_path], cwd=project_root, check=False)
            if history.returncode != 0:
                problems.append(
                    f"{rel_path} is missing and git history could not be inspected: "
                    f"{(history.stderr or history.stdout).strip()}"
                )
            elif history.stdout.strip():
                problems.append(f"{rel_path} is missing but exists in git history")
            continue
        if rel_path in transaction_set:
            continue
        tracked = _run_git(["ls-files", "--error-unmatch", "--", rel_path], cwd=project_root, check=False)
        if tracked.returncode != 0:
            # WI-6530 reclassified `bridge/` as ephemeral runtime state and added the
            # matching `git add -f` staging below, but left this check asserting the
            # pre-WI-6530 tracked-artifact model -- making VERIFIED unreachable for
            # every multi-version thread. An IGNORED predecessor present on disk
            # satisfies chain integrity: the chain is complete, and tracked-ness is
            # not a meaningful signal for a path class governance declared ephemeral.
            # An untracked predecessor that is NOT ignored remains a real gap and
            # still fails closed.
            ignored = _run_git(["check-ignore", "-q", "--", rel_path], cwd=project_root, check=False)
            if ignored.returncode == 0:
                continue
            problems.append(f"{rel_path} is not git-tracked and is not included in the VERIFIED transaction")
            continue
        status = _run_git(["status", "--porcelain", "--", rel_path], cwd=project_root, check=True).stdout.strip()
        if status:
            problems.append(f"{rel_path} has uncommitted changes and is not included in the VERIFIED transaction")
    if problems:
        raise VerifiedFinalizationError(
            "VERIFIED finalization requires a committed predecessor bridge chain; " + "; ".join(problems)
        )


def _run_git(
    args: list[str],
    *,
    cwd: Path,
    check: bool = False,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    run_env = None
    if env:
        run_env = os.environ.copy()
        run_env.update(env)
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        env=run_env,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        check=False,
        **no_window_subprocess_kwargs(),
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
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    attempts = attempts if attempts is not None else _env_int("GTKB_VERIFIED_COMMIT_LOCK_RETRIES", 5)
    base_delay = base_delay if base_delay is not None else _env_float("GTKB_VERIFIED_COMMIT_LOCK_BASE_DELAY", 0.5)
    attempts = max(1, attempts)
    base_delay = max(0.0, base_delay)
    last: subprocess.CompletedProcess[str] | None = None
    for attempt in range(attempts):
        result = _run_git(args, cwd=cwd, check=False, env=env)
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


def _git_lines(args: list[str], *, cwd: Path, env: dict[str, str] | None = None) -> tuple[str, ...]:
    result = _run_git(args, cwd=cwd, check=True, env=env)
    return tuple(line.strip().replace("\\", "/") for line in result.stdout.splitlines() if line.strip())


def _staged_paths(project_root: Path, *, env: dict[str, str] | None = None) -> tuple[str, ...]:
    return _git_lines(["diff", "--name-only", "--cached", "--"], cwd=project_root, env=env)


def _git_absolute_dir(project_root: Path) -> Path:
    return Path(_git_lines(["rev-parse", "--absolute-git-dir"], cwd=project_root)[0])


def _create_temporary_index(project_root: Path) -> tuple[dict[str, str], Path]:
    git_dir = _git_absolute_dir(project_root)
    handle, index_name = tempfile.mkstemp(prefix="gtkb-verified-index-", dir=git_dir)
    os.close(handle)
    index_path = Path(index_name)
    index_path.unlink(missing_ok=True)
    return {"GIT_INDEX_FILE": str(index_path)}, index_path


def _patch_path_token(path_text: str) -> str | None:
    path_text = path_text.split("\t", 1)[0].strip()
    if path_text == "/dev/null":
        return None
    if path_text.startswith(("a/", "b/")):
        path_text = path_text[2:]
    return path_text


def _patch_header_text(raw_line: bytes, patch_arg: str) -> str:
    try:
        return raw_line.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise VerifiedFinalizationError(f"Hunk patch has a non-UTF-8 path header: {patch_arg}") from exc


def _patch_paths_from_bytes(patch_bytes: bytes, project_root: Path, patch_arg: str) -> tuple[str, ...]:
    raw_paths: list[str] = []
    for raw_line in patch_bytes.splitlines():
        is_diff_header = raw_line.startswith(b"diff --git ")
        if not is_diff_header and not raw_line.startswith((b"--- ", b"+++ ")):
            continue
        line = _patch_header_text(raw_line, patch_arg)
        diff_match = re.match(r"^diff --git a/(?P<old>.*?) b/(?P<new>.*)$", line)
        if is_diff_header:
            if diff_match:
                for group_name in ("old", "new"):
                    path_text = _patch_path_token(diff_match.group(group_name))
                    if path_text is not None:
                        raw_paths.append(path_text)
            continue
        path_text = _patch_path_token(line[4:])
        if path_text is not None:
            raw_paths.append(path_text)
    return _unique_paths(project_root, raw_paths)


def _declared_hunk_path(line: str) -> str | None:
    if not re.match(r"(?i)^\s*[-*]?\s*hunk patch\s*:", line):
        return None
    value = line.split(":", 1)[1].strip()
    code_match = re.search(r"`([^`]+)`", value)
    if code_match:
        return code_match.group(1)
    return value.split()[0] if value.split() else None


def _hunk_patch_metadata_from_report(report_text: str, project_root: Path) -> dict[str, dict[str, object]]:
    section = _section_body(report_text, "Hunk Patch Evidence")
    if not section:
        return {}
    metadata: dict[str, dict[str, object]] = {}
    current_path: str | None = None
    for line in section.splitlines():
        declared_path = _declared_hunk_path(line)
        if declared_path:
            current_path = _normalize_repo_path(project_root, declared_path)
            metadata.setdefault(current_path, {})
            continue
        if current_path is None:
            continue
        sha_match = PATCH_SHA256_DECL_RE.search(line)
        if sha_match:
            metadata[current_path]["sha256"] = sha_match.group("value").lower()
            continue
        size_match = PATCH_SIZE_DECL_RE.search(line)
        if size_match:
            metadata[current_path]["size_bytes"] = int(size_match.group("value"))
    return metadata


def _load_hunk_patch_metadata(
    project_root: Path,
    latest_report_rel_path: str | None,
) -> dict[str, dict[str, object]]:
    if not latest_report_rel_path:
        return {}
    try:
        report_text = (project_root / latest_report_rel_path).read_text(encoding="utf-8")
    except OSError as exc:
        raise VerifiedFinalizationError(
            f"Could not read latest implementation report for hunk metadata: {latest_report_rel_path}"
        ) from exc
    return _hunk_patch_metadata_from_report(report_text, project_root)


def _validate_hunk_patch_metadata(
    *,
    patch_arg: str,
    patch_rel_path: str,
    patch_bytes: bytes,
    report_metadata: dict[str, dict[str, object]],
) -> tuple[str, int]:
    actual_sha = hashlib.sha256(patch_bytes).hexdigest()
    actual_size = len(patch_bytes)
    declared = report_metadata.get(patch_rel_path, {})
    declared_sha = declared.get("sha256")
    if declared_sha is not None and str(declared_sha).lower() != actual_sha:
        raise VerifiedFinalizationError(
            f"Hunk patch SHA-256 mismatch for {patch_arg}: declared {declared_sha}, actual {actual_sha}"
        )
    declared_size = declared.get("size_bytes")
    if declared_size is not None and int(declared_size) != actual_size:
        raise VerifiedFinalizationError(
            f"Hunk patch size mismatch for {patch_arg}: declared {declared_size}, actual {actual_size}"
        )
    return actual_sha, actual_size


def _resolve_hunk_patches(
    project_root: Path,
    *,
    hunk_patch_paths: list[str],
    include_paths: tuple[str, ...],
    latest_report_rel_path: str | None = None,
) -> tuple[HunkPatch, ...]:
    include_set = set(include_paths)
    report_metadata = _load_hunk_patch_metadata(project_root, latest_report_rel_path)
    patches: list[HunkPatch] = []
    for patch_arg in hunk_patch_paths:
        patch_path = Path(patch_arg)
        if not patch_path.is_absolute():
            patch_path = project_root / patch_path
        patch_path = patch_path.resolve()
        try:
            patch_rel_path = patch_path.relative_to(project_root.resolve()).as_posix()
        except ValueError as exc:
            raise VerifiedFinalizationError(f"Hunk patch path escapes project root: {patch_arg}") from exc
        try:
            patch_bytes = patch_path.read_bytes()
        except OSError as exc:
            raise VerifiedFinalizationError(f"Hunk patch is unreadable: {patch_arg}") from exc
        patch_sha, patch_size = _validate_hunk_patch_metadata(
            patch_arg=patch_arg,
            patch_rel_path=patch_rel_path,
            patch_bytes=patch_bytes,
            report_metadata=report_metadata,
        )
        touched = _patch_paths_from_bytes(patch_bytes, project_root, patch_arg)
        if not touched:
            raise VerifiedFinalizationError(f"Hunk patch does not identify any repository path: {patch_arg}")
        outside = sorted(set(touched) - include_set)
        if outside:
            raise VerifiedFinalizationError(
                "Hunk patch touches path(s) outside the VERIFIED include set: " + ", ".join(outside)
            )
        patches.append(HunkPatch(path=patch_path, touched_paths=touched, sha256=patch_sha, size_bytes=patch_size))
    return tuple(patches)


def _allowed_staged_paths(
    project_root: Path,
    *,
    expected_paths: tuple[str, ...],
    staged_paths: set[str],
) -> set[str]:
    allowed: set[str] = set()
    for path in expected_paths:
        path_obj = project_root / path
        if path_obj.is_dir():
            prefix = path.rstrip("/") + "/"
            children = {staged for staged in staged_paths if staged.startswith(prefix)}
            allowed.update(children or {path})
        else:
            allowed.add(path)
    return allowed


def _index_entries(
    project_root: Path,
    *,
    paths: tuple[str, ...] = (),
    env: dict[str, str] | None = None,
) -> dict[str, tuple[IndexEntry, ...]]:
    args = ["ls-files", "--stage", "-z"]
    if paths:
        args.extend(["--", *paths])
    output = _run_git(args, cwd=project_root, check=True, env=env).stdout
    entries: dict[str, list[IndexEntry]] = {}
    for record in output.split("\0"):
        if not record:
            continue
        try:
            metadata, path = record.split("\t", 1)
            mode, object_id, stage_text = metadata.split()
            entry = IndexEntry(mode=mode, object_id=object_id, stage=int(stage_text))
        except (ValueError, TypeError) as exc:
            raise VerifiedFinalizationError(f"Could not parse git index entry: {record!r}") from exc
        entries.setdefault(path.replace("\\", "/"), []).append(entry)
    return {path: tuple(path_entries) for path, path_entries in entries.items()}


def _set_real_index_entries(
    project_root: Path,
    paths: tuple[str, ...],
    entries: dict[str, tuple[IndexEntry, ...]],
) -> None:
    for path in paths:
        path_entries = entries.get(path, ())
        if not path_entries:
            _run_git_with_lock_retry(["update-index", "--force-remove", "--", path], cwd=project_root)
            continue
        if len(path_entries) != 1 or path_entries[0].stage != 0:
            raise VerifiedFinalizationError(
                f"VERIFIED real-index realignment requires one stage-0 entry for {path!r}; observed={path_entries!r}"
            )
        entry = path_entries[0]
        _run_git_with_lock_retry(
            ["update-index", "--add", "--cacheinfo", entry.mode, entry.object_id, path],
            cwd=project_root,
        )


def _apply_preserved_overlap_patch(
    project_root: Path,
    patch_path: Path,
    *,
    env: dict[str, str],
) -> None:
    exact_check = _run_git(
        ["apply", "--binary", "--cached", "--check", str(patch_path)],
        cwd=project_root,
        check=False,
        env=env,
    )
    if exact_check.returncode == 0:
        _run_git_with_lock_retry(
            ["apply", "--binary", "--cached", str(patch_path)],
            cwd=project_root,
            env=env,
        )
        return

    three_way = _run_git_with_lock_retry(
        ["apply", "--binary", "--cached", "--3way", str(patch_path)],
        cwd=project_root,
        check=False,
        env=env,
    )
    if three_way.returncode != 0:
        failure = (three_way.stderr or three_way.stdout or exact_check.stderr or exact_check.stdout).strip()
        raise VerifiedFinalizationError(
            "A pre-existing staged hunk on a VERIFIED path could not be rebased onto the reviewed candidate; "
            f"finalization stopped before commit: {failure}"
        )


def _prepare_real_index_realign(
    project_root: Path,
    committed_paths: set[str],
    *,
    candidate_env: dict[str, str],
) -> RealIndexRealignmentPlan:
    ordered_paths = tuple(sorted(committed_paths))
    entries_before = _index_entries(project_root)
    candidate_entries = _index_entries(project_root, paths=ordered_paths, env=candidate_env)
    staged_before = set(_staged_paths(project_root))
    overlap = sorted(committed_paths & staged_before)
    preserved_overlap = tuple(
        path for path in overlap if entries_before.get(path, ()) != candidate_entries.get(path, ())
    )
    expected_entries = {path: candidate_entries.get(path, ()) for path in ordered_paths}
    if not preserved_overlap:
        return RealIndexRealignmentPlan(
            committed_paths=ordered_paths,
            entries_before=entries_before,
            expected_entries=expected_entries,
            preserved_overlap=(),
        )

    patch_handle, patch_name = tempfile.mkstemp(
        prefix="gtkb-verified-overlap-", suffix=".patch", dir=_git_absolute_dir(project_root)
    )
    os.close(patch_handle)
    patch_path = Path(patch_name)
    preserve_env: dict[str, str] | None = None
    preserve_index: Path | None = None
    try:
        patch_result = _run_git(
            ["diff", "--cached", "--binary", "--full-index", "HEAD", "--", *preserved_overlap],
            cwd=project_root,
            check=False,
        )
        if patch_result.returncode != 0 or not patch_result.stdout.strip():
            failure = (patch_result.stderr or patch_result.stdout).strip()
            raise VerifiedFinalizationError(
                "Could not capture the pre-existing staged hunk for VERIFIED real-index preservation: "
                + (failure or "empty staged patch")
            )
        patch_path.write_text(patch_result.stdout, encoding="utf-8", newline="\n")

        candidate_tree = _git_lines(["write-tree"], cwd=project_root, env=candidate_env)[0]
        preserve_env, preserve_index = _create_temporary_index(project_root)
        _run_git(["read-tree", candidate_tree], cwd=project_root, check=True, env=preserve_env)
        _apply_preserved_overlap_patch(project_root, patch_path, env=preserve_env)
        unmerged = _git_lines(["ls-files", "--unmerged"], cwd=project_root, env=preserve_env)
        if unmerged:
            raise VerifiedFinalizationError(
                "A pre-existing staged hunk produced unmerged entries in the VERIFIED preservation preflight."
            )
        merged_entries = _index_entries(project_root, paths=preserved_overlap, env=preserve_env)
        for path in preserved_overlap:
            expected_entries[path] = merged_entries.get(path, ())
    finally:
        patch_path.unlink(missing_ok=True)
        if preserve_index is not None:
            preserve_index.unlink(missing_ok=True)

    return RealIndexRealignmentPlan(
        committed_paths=ordered_paths,
        entries_before=entries_before,
        expected_entries=expected_entries,
        preserved_overlap=preserved_overlap,
    )


def _realign_real_index_after_temp_commit(project_root: Path, plan: RealIndexRealignmentPlan) -> None:
    try:
        _set_real_index_entries(project_root, plan.committed_paths, plan.expected_entries)
        entries_after = _index_entries(project_root)
        non_committed_before = {
            path: entries for path, entries in plan.entries_before.items() if path not in plan.committed_paths
        }
        non_committed_after = {
            path: entries for path, entries in entries_after.items() if path not in plan.committed_paths
        }
        if non_committed_after != non_committed_before:
            raise VerifiedFinalizationError("VERIFIED real-index realignment changed a non-committed index entry.")
        actual_committed = {path: entries_after.get(path, ()) for path in plan.committed_paths}
        if actual_committed != plan.expected_entries:
            raise VerifiedFinalizationError(
                "VERIFIED real-index realignment did not reproduce the preservation-preflight entries."
            )
    except Exception:
        _set_real_index_entries(project_root, plan.committed_paths, plan.entries_before)
        raise


def _apply_hunk_patch_to_index(project_root: Path, patch: HunkPatch, *, env: dict[str, str]) -> None:
    check = _run_git(
        ["apply", "--binary", "--cached", "--check", str(patch.path)],
        cwd=project_root,
        check=False,
        env=env,
    )
    if check.returncode == 0:
        _run_git_with_lock_retry(["apply", "--binary", "--cached", str(patch.path)], cwd=project_root, env=env)
        return

    whitespace_check = _run_git(
        ["apply", "--binary", "--cached", "--check", "--ignore-space-change", str(patch.path)],
        cwd=project_root,
        check=False,
        env=env,
    )
    if whitespace_check.returncode == 0:
        _run_git_with_lock_retry(
            ["apply", "--binary", "--cached", "--ignore-space-change", str(patch.path)],
            cwd=project_root,
            env=env,
        )
        return

    reverse_check = _run_git(
        ["apply", "--binary", "--cached", "--reverse", "--check", str(patch.path)],
        cwd=project_root,
        check=False,
        env=env,
    )
    if reverse_check.returncode == 0:
        raise VerifiedFinalizationError(
            f"hunk patch is reverse-applyable but not forward-applyable to the disposable index: {patch.path}"
        )

    whitespace_reverse_check = _run_git(
        ["apply", "--binary", "--cached", "--reverse", "--check", "--ignore-space-change", str(patch.path)],
        cwd=project_root,
        check=False,
        env=env,
    )
    if whitespace_reverse_check.returncode == 0:
        raise VerifiedFinalizationError(
            f"hunk patch is reverse-applyable but not forward-applyable to the disposable index: {patch.path}"
        )

    failure = (
        check.stderr
        or check.stdout
        or whitespace_check.stderr
        or whitespace_check.stdout
        or reverse_check.stderr
        or reverse_check.stdout
        or whitespace_reverse_check.stderr
        or whitespace_reverse_check.stdout
    ).strip()
    raise VerifiedFinalizationError(
        f"hunk patch is not Git-applyable against the disposable index: {patch.path}: {failure}"
    )


def _cleanup_failed_staging(project_root: Path, staged_paths: tuple[str, ...]) -> None:
    if staged_paths:
        _run_git(["restore", "--staged", "--", *staged_paths], cwd=project_root)


def _append_commit_finalization_evidence(body: str, *, commit_message: str, paths: tuple[str, ...]) -> str:
    if _section_body(body, "Commit Finalization Evidence"):
        return body
    path_lines = "\n".join(f"- `{path}`" for path in paths)
    subject = commit_message.splitlines()[0].strip()
    return (
        body.rstrip() + "\n\n## Commit Finalization Evidence\n\n"
        "- Finalization helper: `.harness-baseline-configuration/skills/gtkb-verify/helpers/write_verdict.py --finalize-verified`\n"
        f"- Intended commit subject: `{subject}`\n"
        "- Same-transaction path set:\n"
        f"{path_lines}\n"
        "- Final commit SHA is emitted by the helper after commit creation; it is intentionally not self-embedded in this verdict file.\n"
    )


def _assert_verdict_review_independence(
    slug: str,
    body: str,
    project_root: Path,
    *,
    latest_report_rel_path: str,
) -> None:
    """Fail closed if a verdict body is a self-review (WI-4829 write-time helper guard).

    The verify helper writes verdicts via ``write_bridge_file`` (``write_bytes``),
    which bypasses the bridge-compliance PreToolUse Write hook, so the same
    self-review check is enforced here. A verdict whose ``author_session_context_id``
    equals the exact latest implementation report's author session is invalid under
    the session-context review-independence rule. The report path comes from
    ``_assert_verification_ready`` and must match the verdict's explicit reference.
    Comparator loading is itself fail-closed because no independent verdict may be
    finalized when the enforcement helper is unavailable.
    """
    try:
        from scripts.bridge_review_independence import verdict_self_review_reason
    except (ImportError, AttributeError) as exc:
        raise VerifiedFinalizationError(
            "Review-independence enforcement helper could not load; VERIFIED finalization is denied."
        ) from exc
    reason = verdict_self_review_reason(
        body,
        slug,
        project_root,
        expected_artifact_path=latest_report_rel_path,
    )
    if reason is not None:
        raise VerifiedFinalizationError(
            f"Self-review verdict refused ({reason}): the verdict author session must be present "
            f"and distinct from the reviewed artifact's author session for {slug!r}. Review "
            "independence is session-context based; file the verdict from a different session "
            "context (WI-4829; GOV-DOCUMENT-AUTHOR-PROVENANCE-001)."
        )


def _assert_verdict_author_session_context_is_real(body: str) -> None:
    session_context_id = extract_author_metadata(body).get("author_session_context_id")
    if is_synthetic_session_context_id(session_context_id):
        raise VerifiedFinalizationError(
            "VERIFIED verdict body uses a synthetic author_session_context_id "
            f"{session_context_id!r}. The finalization helper requires a concrete "
            "author session context id before writing the bridge verdict (WI-4940; "
            "GOV-DOCUMENT-AUTHOR-PROVENANCE-001)."
        )


_BRIDGE_COMPLIANCE_GATE_MODULES: dict[str, Any] = {}


def _load_bridge_compliance_gate(project_root: Path) -> Any:
    """Load the bridge-compliance gate module that will audit this write.

    The gate owns the single definition of the self-referential
    ``candidate_evidence_hash`` algorithm, so the helper never re-implements it
    and the stamped value cannot drift from the audited value. Resolution reuses
    the writer's own gate lookup, which guarantees the module loaded here is the
    same file ``run_bridge_compliance_audit`` executes for this ``project_root``.

    Loading is fail-closed, matching the review-independence comparator: no
    terminal VERIFIED verdict may be finalized when the enforcement definition
    is unavailable.
    """
    try:
        from scripts.gtkb_bridge_writer import _bridge_compliance_gate_path

        gate_path = _bridge_compliance_gate_path(project_root)
        key = str(gate_path.resolve())
        cached = _BRIDGE_COMPLIANCE_GATE_MODULES.get(key)
        if cached is not None:
            return cached
        suffix = hashlib.sha256(key.encode("utf-8")).hexdigest()[:12]
        spec = importlib.util.spec_from_file_location(f"gtkb_bridge_compliance_gate_{suffix}", gate_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"could not build a module spec for {gate_path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except Exception as exc:  # noqa: BLE001 - any gate-load failure must deny finalization.
        raise VerifiedFinalizationError(
            "Bridge-compliance gate could not be loaded; VERIFIED finalization is denied. The gate "
            "owns the candidate_evidence_hash definition and the verdict cannot be stamped without "
            f"it ({exc})."
        ) from exc
    _BRIDGE_COMPLIANCE_GATE_MODULES[key] = module
    return module


def _restamp_candidate_evidence_hash(
    body: str,
    *,
    verdict_rel_path: str,
    project_root: Path,
) -> str:
    """Return the verdict body with ``candidate_evidence_hash`` stamped over final bytes.

    ``candidate_evidence_hash`` is self-referential: the gate recomputes it over
    the fully normalized candidate bytes it is about to audit. Every body
    mutation performed after the reviewer stamped the field therefore
    invalidates it. This step runs last, after the finalizer's own mutations and
    after pre-applying the writer's pre-audit normalization, so the bytes stamped
    here are the bytes the audit hashes.

    Deterministic: no clock, no network, no retry. Fail-closed on every branch
    where the gate could not validate the result.
    """
    from scripts.gtkb_bridge_writer import ensure_author_metadata, normalize_bridge_envelope_head

    gate = _load_bridge_compliance_gate(project_root)

    # Pre-apply the writer's pre-audit normalization so the stamped bytes and the
    # audited bytes are identical. Both are idempotent for a finalizer-shaped body.
    normalized = ensure_author_metadata(body, project_root=project_root, explicit=None)
    normalized = normalize_bridge_envelope_head(normalized)

    occurrences = list(gate.CANDIDATE_EVIDENCE_HASH_LINE_RE.finditer(normalized))
    if len(occurrences) > 1:
        raise VerifiedFinalizationError(
            f"VERIFIED verdict body declares {len(occurrences)} `candidate_evidence_hash` fields; the "
            "bridge-compliance gate requires exactly one and denies the write otherwise. Remove the "
            "duplicate field(s) from the Applicability Preflight section."
        )
    if not occurrences:
        # Mirror the gate's own activation condition: it only checks the hash when
        # an Applicability Preflight section is present. Absent that section the
        # field is not required, so there is nothing to stamp.
        if gate._applicability_preflight_section(normalized) is not None:
            raise VerifiedFinalizationError(
                "VERIFIED verdict body has an `## Applicability Preflight` section but no "
                "`candidate_evidence_hash` field, so the bridge-compliance gate will deny the write. "
                f"Add `- candidate_evidence_hash: `{gate.CANDIDATE_EVIDENCE_HASH_SENTINEL}`` to that "
                "section; the finalizer stamps the real value."
            )
        return normalized

    expected = gate._candidate_evidence_hash(verdict_rel_path, normalized, project_root)
    if expected is None:
        raise VerifiedFinalizationError(
            "VERIFIED finalization could not compute `candidate_evidence_hash` for "
            f"{verdict_rel_path!r}; the verdict path must be root-contained and the field must carry "
            "either the sentinel placeholder or a well-formed sha256 value."
        )

    stamped = gate.CANDIDATE_EVIDENCE_HASH_LINE_RE.sub(
        lambda match: match.group("prefix") + expected + match.group("suffix"),
        normalized,
        count=1,
    )

    # The writer re-applies its normalization before auditing. Assert that
    # re-application is a no-op here, so a future non-idempotent normalization
    # change fails closed instead of silently reintroducing a stale stamp.
    reapplied = normalize_bridge_envelope_head(
        ensure_author_metadata(stamped, project_root=project_root, explicit=None)
    )
    if reapplied != stamped:
        raise VerifiedFinalizationError(
            "VERIFIED finalization detected non-idempotent bridge-writer normalization; the stamped "
            "bytes would differ from the audited bytes. Refusing to write a verdict whose "
            "`candidate_evidence_hash` cannot be guaranteed fresh."
        )
    recomputed = gate._candidate_evidence_hash(verdict_rel_path, stamped, project_root)
    if recomputed != expected:
        raise VerifiedFinalizationError(
            "VERIFIED finalization could not reach a stable `candidate_evidence_hash` fixpoint for "
            f"{verdict_rel_path!r} (expected {expected!r}, recomputed {recomputed!r})."
        )
    return stamped


def finalize_verified_commit(
    slug: str,
    body: str,
    *,
    include_paths: list[str],
    hunk_patch_paths: list[str] | None = None,
    commit_message: str,
    project_root: Path | None = None,
    pre_populate: bool = False,
    db: Any | bool | None = None,
    glossary_path: Path | None = None,
    log_path: Path | bool | None = DEFAULT_VERDICT_PREPOPULATION_LOG,
) -> VerifiedFinalizationResult:
    """Write a VERIFIED verdict and create the final local commit as one transaction.

    The helper writes the next versioned bridge verdict, builds a disposable
    index from HEAD, stages the verified path set plus that verdict in the
    disposable index, and commits that reviewed index with no pathspec.
    Unrelated paths already staged in the shared real index by other sessions
    are tolerated and never folded into this commit. If any step after the
    verdict write fails, the verdict file is removed. Project auto-retirement
    remains enabled by default; callers with separately governed keep-open
    authority may explicitly suppress that post-commit actuation for this
    invocation.
    """
    root = _project_root_from_arg(project_root)
    hunk_patch_paths = hunk_patch_paths or []
    if not include_paths:
        raise VerifiedFinalizationError(
            "VERIFIED finalization requires at least one verified implementation/report path."
        )
    if not commit_message.strip():
        raise VerifiedFinalizationError("VERIFIED finalization requires a non-empty commit message.")

    next_version, latest_report = _assert_verification_ready(slug, root)
    _assert_include_set_covers_report_claims(
        slug=slug,
        project_root=root,
        latest_report_rel_path=latest_report,
        include_paths=include_paths,
    )
    verdict_rel_path = f"bridge/{slug}-{next_version:03d}.md"
    expected_paths = _unique_paths(root, [*include_paths, verdict_rel_path])
    if len(expected_paths) != len(include_paths) + 1:
        raise VerifiedFinalizationError("VERIFIED finalization include paths must not duplicate the verdict path.")
    _assert_predecessor_chain_committed(slug, root, next_version, expected_paths)
    hunk_patches = _resolve_hunk_patches(
        root,
        hunk_patch_paths=hunk_patch_paths,
        include_paths=tuple(_unique_paths(root, include_paths)),
        latest_report_rel_path=latest_report,
    )
    hunk_patch_touched_paths = {path for patch in hunk_patches for path in patch.touched_paths}

    body_to_write = seed_prior_deliberations(
        slug,
        body,
        db=db,
        glossary_path=glossary_path,
        log_path=log_path,
        pre_populate=pre_populate,
        project_root=root,
    )
    validate_verified_body(body_to_write, project_root=root)
    body_to_write = _append_commit_finalization_evidence(
        body_to_write,
        commit_message=commit_message,
        paths=expected_paths,
    )

    _assert_verdict_review_independence(
        slug,
        body_to_write,
        root,
        latest_report_rel_path=latest_report,
    )
    _assert_verdict_author_session_context_is_real(body_to_write)

    # Must run last: every preceding step may mutate the body, and the gate hashes
    # the final normalized bytes. Fail-closed, so no partial terminal artifact and
    # no commit can result from a stale stamp.
    body_to_write = _restamp_candidate_evidence_hash(
        body_to_write,
        verdict_rel_path=verdict_rel_path,
        project_root=root,
    )

    from scripts.gtkb_bridge_writer import (
        finalize_pending_bridge_publication,
        rollback_pending_bridge_publication,
        write_bridge_file,
    )

    publication_path = write_bridge_file(
        slug,
        next_version,
        body_to_write,
        root,
        release_claim=False,
    )
    temp_env: dict[str, str] | None = None
    temp_index: Path | None = None
    old_head = _git_lines(["rev-parse", "HEAD"], cwd=root)[0]
    created_commit: str | None = None
    try:
        temp_env, temp_index = _create_temporary_index(root)
        _run_git(["read-tree", "HEAD"], cwd=root, check=True, env=temp_env)

        full_stage_paths = [path for path in expected_paths if path not in hunk_patch_touched_paths]
        if full_stage_paths:
            _run_git_with_lock_retry(["add", "-f", "--", *full_stage_paths], cwd=root, env=temp_env)

        for patch in hunk_patches:
            _apply_hunk_patch_to_index(root, patch, env=temp_env)

        temp_staged = set(_staged_paths(root, env=temp_env))
        allowed_staged = _allowed_staged_paths(root, expected_paths=expected_paths, staged_paths=temp_staged)
        missing = {verdict_rel_path} - temp_staged
        unexpected = temp_staged - allowed_staged
        if missing or unexpected:
            raise VerifiedFinalizationError(
                "VERIFIED finalization staged-set mismatch. "
                f"missing={sorted(missing)}; unexpected_new={sorted(unexpected)}; "
                f"expected_paths={list(expected_paths)}; temp_staged={sorted(temp_staged)}"
            )
        realignment_plan = _prepare_real_index_realign(root, temp_staged, candidate_env=temp_env)
        commit = _run_git_with_lock_retry(["commit", "-m", commit_message], cwd=root, check=False, env=temp_env)
        if commit.returncode != 0:
            raise VerifiedFinalizationError(
                f"git commit failed with exit {commit.returncode}: {(commit.stderr or commit.stdout).strip()}"
            )
        created_commit = _git_lines(["rev-parse", "HEAD"], cwd=root)[0]
        committed = set(_git_lines(["diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"], cwd=root))
        if committed != temp_staged:
            raise VerifiedFinalizationError(
                "VERIFIED finalization committed-path mismatch. "
                f"committed={sorted(committed)}; expected={sorted(temp_staged)}"
            )
        _realign_real_index_after_temp_commit(root, realignment_plan)
        finalize_pending_bridge_publication(publication_path, root)
    except Exception as exc:
        if created_commit is not None:
            rollback = _run_git_with_lock_retry(
                ["update-ref", "HEAD", old_head, created_commit],
                cwd=root,
                check=False,
            )
            if rollback.returncode != 0:
                raise VerifiedFinalizationError(
                    "VERIFIED finalization created a commit but could not atomically roll HEAD back after "
                    f"realignment failure; verdict retained for diagnosis: {(rollback.stderr or rollback.stdout).strip()}"
                ) from exc
        _cleanup_failed_staging(root, ())
        rollback_pending_bridge_publication(
            publication_path,
            root,
            reason=f"VERIFIED finalization failed before durable commit: {exc}",
        )
        raise
    finally:
        if temp_index is not None:
            temp_index.unlink(missing_ok=True)

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
    parser.add_argument(
        "--hunk-patch",
        action="append",
        default=[],
        help=(
            "Unified patch containing reviewed hunks to apply to the disposable index. "
            "All patch paths must be in the --include set. Repeat as needed."
        ),
    )
    parser.add_argument("--commit-message", help="Commit message for --finalize-verified.")
    parser.add_argument("--project-root", type=Path, help="Project root for --finalize-verified.")
    parser.add_argument(
        "--skills-applied",
        action="append",
        default=[],
        help="Skill name for the Skills applied disclosure line (repeatable; report-only).",
    )
    args = parser.parse_args(argv)

    if args.body_file is not None:
        body = args.body_file.read_text(encoding="utf-8")
    else:
        body = sys.stdin.read()

    if args.skills_applied:
        body = append_skills_applied_disclosure(body, args.skills_applied)

    log_path = False if args.no_log else DEFAULT_VERDICT_PREPOPULATION_LOG
    if args.finalize_verified:
        result = finalize_verified_commit(
            args.slug,
            body,
            include_paths=args.include,
            hunk_patch_paths=args.hunk_patch,
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
        project_root=args.project_root,
    )
    sys.stdout.write(seeded)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
