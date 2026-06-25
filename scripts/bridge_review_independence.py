# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Shared bridge review-independence comparator (WI-4829).

Single-sources the self-review refusal semantics that were previously inlined only
in the headless dispatch path (``scripts/cross_harness_bridge_trigger.py``
``_self_review_refusal_reason``; ``groundtruth_kb/tafe_dispatch_policy.py``
``_review_independence_gate``). The same semantics now also gate verdict-write
time (the bridge-compliance hook + the ``write_verdict`` finalization helper) and
implementation-start authorization, per ``DELIB-20266105`` (owner defense-in-depth
authorization) and ``GOV-DOCUMENT-AUTHOR-PROVENANCE-001``.

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

import fnmatch
import re
from pathlib import Path

AUTHOR_MEETS_REVIEWER_REFUSED = "author_meets_reviewer_refused"
AUTHOR_SESSION_CONTEXT_MISSING = "author_session_context_missing"
AUTHOR_SESSION_CONTEXT_UNREADABLE = "author_session_context_unreadable"

#: Header lines a verdict uses to name the artifact it reviews, most specific first.
_REVIEWED_REFERENCE_RE = re.compile(
    r"^(?:Responds to|Reviewed report|Reviewed file|Approved proposal):\s*`?([^\s`]+)`?\s*$",
    re.IGNORECASE | re.MULTILINE,
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
    patterns = (f"{bridge_id}-*.md", f"gtkb-{bridge_id}-*.md")
    files = [
        candidate
        for candidate in bridge_dir.glob("*.md")
        if any(fnmatch.fnmatch(candidate.name, pattern) for pattern in patterns)
    ]
    files.sort(key=lambda candidate: candidate.name)
    return files


def reviewed_artifact_path(
    verdict_content: str,
    bridge_id: str,
    project_root: Path,
) -> Path | None:
    """Resolve the artifact a verdict reviews.

    Prefers the verdict's explicit ``Responds to:`` / ``Reviewed report:`` /
    ``Approved proposal:`` reference, because the latest prior versioned file is
    *not* reliable for ``VERIFIED``: an intervening ``GO`` can be the newest file
    while the verified artifact is the earlier implementation report (e.g. ``-005``
    verifies report ``-003`` even though ``GO -004`` is newer). Falls back to the
    latest prior versioned file only when no explicit reference is present.
    """
    match = _REVIEWED_REFERENCE_RE.search(verdict_content or "")
    if match:
        candidate = (Path(project_root) / match.group(1).strip().strip("`")).resolve()
        if candidate.is_file():
            return candidate
    files = _versioned_bridge_files(bridge_id, project_root)
    return files[-1] if files else None


def verdict_self_review_reason(
    verdict_content: str,
    bridge_id: str,
    project_root: Path,
) -> str | None:
    """Return a refusal reason if ``verdict_content`` is a self-review, else ``None``.

    Fails closed when the reviewed artifact cannot be resolved or read, or when
    either session id is missing.
    """
    reviewer = parse_author_session_context_id(verdict_content)
    target_path = reviewed_artifact_path(verdict_content, bridge_id, project_root)
    if target_path is None:
        return AUTHOR_SESSION_CONTEXT_MISSING
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
    "parse_author_session_context_id",
    "reviewed_artifact_path",
    "self_review_reason",
    "verdict_self_review_reason",
]
