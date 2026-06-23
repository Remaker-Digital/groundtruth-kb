"""No-index bridge file writer used by governed bridge helpers.

The current bridge model uses dispatcher/TAFE state plus status-bearing
numbered files under ``bridge/``. This module only writes a new numbered file
after caller-side validation has passed; it never mutates aggregate queue state.
"""

from __future__ import annotations

import subprocess
from collections.abc import Mapping
from pathlib import Path

from scripts.bridge_author_metadata import ensure_author_metadata
from scripts.verdict_evidence_anchor_preflight import (
    validate_verdict_evidence_anchors,
    violation_summary,
)


def _bridge_file_committed_in_git(target: Path, project_root: Path) -> bool:
    """Return True when *target* appears in git history, even if absent on disk.

    Prevents recreating a numbered bridge file at the same version as a
    previously committed but now-deleted file.  Fail-open: returns False on
    any subprocess / git error so a missing git installation or repository
    does not create a spurious hard-block.
    """
    try:
        rel = target.relative_to(project_root).as_posix()
    except ValueError:
        return False
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "-1", "--", rel],
            cwd=str(project_root),
            capture_output=True,
            timeout=5,
        )
        return bool(result.stdout.strip())
    except Exception:
        return False


VALID_STATUSES: frozenset[str] = frozenset({"NEW", "REVISED", "GO", "NO-GO", "VERIFIED", "ADVISORY", "DEFERRED"})
PRIME_STATUSES: frozenset[str] = frozenset({"NEW", "REVISED"})
LOYAL_OPPOSITION_STATUSES: frozenset[str] = frozenset({"GO", "NO-GO", "VERIFIED", "ADVISORY"})

PRIME_ROLE_SLOT = "prime-builder"
LOYAL_OPPOSITION_ROLE_SLOT = "loyal-opposition"


class BridgeError(Exception):
    """Base class for bridge writer errors."""


class BridgeConflictError(BridgeError):
    """Live disk state conflicts with the proposed bridge file write."""


class BridgeTransitionError(BridgeError):
    """Proposed status transition is illegal for the calling workflow."""


class BridgeEvidenceAnchorError(BridgeError):
    """A gated verdict (NO-GO/VERIFIED) cites evidence anchors that do not exist.

    Raised by ``write_bridge_file`` per WI-4520 so the helper-routed verdict
    chokepoint (post-implementation VERIFIED finalize, impl-report, revise)
    cannot persist a verdict whose cited line/string anchors are fabricated.
    """


def _bridge_dir(project_root: Path) -> Path:
    return project_root / "bridge"


def write_bridge_file(
    document_name: str,
    version: int,
    content: str,
    project_root: Path,
    *,
    author_metadata: Mapping[str, object] | None = None,
    require_author_metadata: bool = True,
) -> Path:
    """Write ``bridge/<document>-<NNN>.md`` and re-read to verify.

    Raises ``BridgeConflictError`` if the file already exists. Status transition
    validation is owned by the caller's latest-status scan because dispatcher
    state, not this low-level writer, decides queue actionability.
    """

    if version < 1:
        raise BridgeTransitionError(f"bridge version must be positive; got {version}")
    target = _bridge_dir(project_root) / f"{document_name}-{version:03d}.md"
    if target.exists():
        raise BridgeConflictError(f"{target} already exists; refusing to overwrite")
    if _bridge_file_committed_in_git(target, project_root):
        raise BridgeConflictError(
            f"{target} exists in git history; refusing to recreate at the same version. "
            "Use the next version number to append a new bridge entry."
        )
    anchor_violations = validate_verdict_evidence_anchors(content, project_root=project_root)
    if anchor_violations:
        raise BridgeEvidenceAnchorError(
            "refusing to write verdict with fabricated evidence anchors (WI-4520): "
            + violation_summary(anchor_violations)
            + ". Fix the citation, or mark the finding [inference] / [no exact anchor] / [absent]."
        )
    content_to_write = (
        ensure_author_metadata(content, project_root=project_root, explicit=author_metadata)
        if require_author_metadata
        else content
    )
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content_to_write, encoding="utf-8")
    written = target.read_text(encoding="utf-8")
    if written != content_to_write:
        raise BridgeConflictError(f"post-write verification failed for {target}: content on disk differs")
    return target
