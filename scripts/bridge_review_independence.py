# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Shared bridge review-independence comparator (WI-4829).

The remaining file-bridge readers compare the actual context attribution of
an author and reviewer. Native delivery enforces independence through canonical
session bindings and current work state. Neither a harness name, file creator
nor a retained owner-permission record establishes review independence.

A bridge verdict (``GO`` / ``NO-GO`` / ``VERIFIED``) is a **self-review** when its
``author_session_context_id`` equals the ``author_session_context_id`` of the
artifact it reviews. The rule **fails closed** when either session id is missing or
the reviewed artifact cannot be read — review independence cannot be *established*,
so it must not be *assumed*.

Refusal-reason vocabulary (kept byte-identical to the dispatch path so audit
classification is stable):

- ``author_meets_reviewer_refused`` — reviewer session == reviewed-artifact author.
- ``author_session_context_missing`` — a required session id is absent/blank.
- ``author_session_context_unreadable`` — the reviewed artifact could not be read.

This module imports nothing outside the standard library so it is safe to import
from the activated hook, the verify skill helper, and the implementation-start
authorizer alike.
"""

from __future__ import annotations

import re
from pathlib import Path, PurePosixPath, PureWindowsPath

AUTHOR_MEETS_REVIEWER_REFUSED = "author_meets_reviewer_refused"
AUTHOR_SESSION_CONTEXT_MISSING = "author_session_context_missing"
AUTHOR_SESSION_CONTEXT_UNREADABLE = "author_session_context_unreadable"
REVIEWED_ARTIFACT_REFERENCE_INVALID = "reviewed_artifact_reference_invalid"

#: Header lines a verdict uses to name the artifact it reviews, most specific first.
_REVIEWED_REFERENCE_RE = re.compile(
    r"^(?:Responds to|Reviewed report|Reviewed file|Approved proposal):\s*`?([^\s`]+\.md)`?(?:\s+.*)?$",
    re.IGNORECASE,
)
_AUTHOR_LINE_RE = re.compile(r"^author_session_context_id:\s*(\S+)\s*$", re.IGNORECASE)


def parse_author_session_context_id(content: str) -> str | None:
    """Return the ``author_session_context_id`` header value, or ``None`` if absent.

    Only the metadata header region (first 50 lines) is scanned, matching the
    dispatch-path parser. A blank value resolves to ``None`` (treated as missing).
    """
    for line in (content or "").splitlines()[:50]:
        match = _AUTHOR_LINE_RE.match(line.strip())
        if match:
            value = match.group(1).strip().strip('"').strip("'")
            return value or None
    return None


def self_review_reason(
    reviewer_session_context_id: str | None,
    target_author_session_context_id: str | None,
) -> str | None:
    """Pure comparator. Return a refusal-reason string, or ``None`` when independent.

    Fails closed (``author_session_context_missing``) when either id is blank, so a
    caller can never read "no reason" as "independence confirmed" off missing data.
    """
    reviewer = (reviewer_session_context_id or "").strip()
    target = (target_author_session_context_id or "").strip()
    if not reviewer or not target:
        return AUTHOR_SESSION_CONTEXT_MISSING
    if reviewer == target:
        return AUTHOR_MEETS_REVIEWER_REFUSED
    return None


def _versioned_bridge_files(bridge_id: str, project_root: Path) -> list[Path]:
    """Return the versioned bridge files for ``bridge_id``, sorted by name."""
    bridge_dir = Path(project_root) / "bridge"
    if not bridge_dir.is_dir():
        return []
    slugs = {bridge_id}
    if not bridge_id.startswith("gtkb-"):
        slugs.add(f"gtkb-{bridge_id}")
    bridge_file_re = re.compile(rf"^(?:{'|'.join(re.escape(slug) for slug in sorted(slugs))})-\d{{3}}\.md$")
    files = [candidate for candidate in bridge_dir.glob("*.md") if bridge_file_re.match(candidate.name)]
    files.sort(key=lambda candidate: candidate.name)
    return files


def _reviewed_reference(verdict_content: str) -> str | None:
    """Return one explicit reviewed-artifact reference from the metadata region."""
    for line in (verdict_content or "").splitlines()[:50]:
        normalized = line.strip().replace("**", "")
        match = _REVIEWED_REFERENCE_RE.fullmatch(normalized)
        if match:
            return match.group(1).strip().strip("`")
    return None


def _thread_relative_path(path_text: str | Path, bridge_id: str) -> Path | None:
    """Return a normalized path only when it names this exact bridge thread."""
    raw = str(path_text).strip().strip("`")
    if not raw or Path(raw).is_absolute() or PureWindowsPath(raw).is_absolute():
        return None
    normalized = raw.replace("\\", "/")
    segments = normalized.split("/")
    if len(segments) != 2 or segments[0] != "bridge" or any(part in {"", ".", ".."} for part in segments):
        return None
    name = PurePosixPath(normalized).name
    slugs = {bridge_id}
    if not bridge_id.startswith("gtkb-"):
        slugs.add(f"gtkb-{bridge_id}")
    if not any(re.fullmatch(rf"{re.escape(slug)}-\d{{3}}\.md", name) for slug in slugs):
        return None
    return Path("bridge") / name


def _contained_bridge_path(path_text: str | Path, bridge_id: str, project_root: Path) -> Path | None:
    """Resolve one same-thread path and reject traversal, symlinks, and root escape."""
    relative = _thread_relative_path(path_text, bridge_id)
    if relative is None:
        return None
    root = Path(project_root).resolve()
    bridge_root = (root / "bridge").resolve()
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(bridge_root)
    except ValueError:
        return None
    return candidate


def reviewed_artifact_path(
    verdict_content: str,
    bridge_id: str,
    project_root: Path,
    *,
    expected_artifact_path: str | Path | None = None,
) -> Path | None:
    """Resolve the artifact a verdict reviews.

    Prefers the verdict's explicit ``Responds to:`` / ``Reviewed report:`` /
    ``Approved proposal:`` reference, because the latest prior versioned file is
    *not* reliable for ``VERIFIED``: an intervening ``GO`` can be the newest file
    while the verified artifact is the earlier implementation report (e.g. ``-005``
    verifies report ``-003`` even though ``GO -004`` is newer). Falls back to the
    latest prior versioned file only when no explicit reference is present.
    """
    reference = _reviewed_reference(verdict_content)
    if reference is not None:
        candidate = _contained_bridge_path(reference, bridge_id, project_root)
        if candidate is None or not candidate.is_file():
            return None
        if expected_artifact_path is not None:
            expected = _contained_bridge_path(expected_artifact_path, bridge_id, project_root)
            if expected is None or candidate != expected:
                return None
        return candidate
    if expected_artifact_path is not None:
        # Exact report binding is explicit: a verdict cannot silently fall back
        # to another version when the finalizer has identified the report.
        return None
    files = _versioned_bridge_files(bridge_id, project_root)
    if not files:
        return None
    candidate = _contained_bridge_path(files[-1].relative_to(project_root), bridge_id, project_root)
    return candidate if candidate is not None and candidate.is_file() else None


def verdict_self_review_reason(
    verdict_content: str,
    bridge_id: str,
    project_root: Path,
    *,
    expected_artifact_path: str | Path | None = None,
) -> str | None:
    """Return a refusal reason if ``verdict_content`` is a self-review, else ``None``.

    Fails closed when the reviewed artifact cannot be resolved or read, or when
    either session id is missing.
    """
    reviewer = parse_author_session_context_id(verdict_content)
    target_path = reviewed_artifact_path(
        verdict_content,
        bridge_id,
        project_root,
        expected_artifact_path=expected_artifact_path,
    )

    if target_path is None:
        return REVIEWED_ARTIFACT_REFERENCE_INVALID
    try:
        target_content = target_path.read_text(encoding="utf-8")
    except OSError:
        return AUTHOR_SESSION_CONTEXT_UNREADABLE
    target_author = parse_author_session_context_id(target_content)

    return self_review_reason(reviewer, target_author)


__all__ = [
    "AUTHOR_MEETS_REVIEWER_REFUSED",
    "AUTHOR_SESSION_CONTEXT_MISSING",
    "AUTHOR_SESSION_CONTEXT_UNREADABLE",
    "REVIEWED_ARTIFACT_REFERENCE_INVALID",
    "parse_author_session_context_id",
    "reviewed_artifact_path",
    "self_review_reason",
    "verdict_self_review_reason",
]
