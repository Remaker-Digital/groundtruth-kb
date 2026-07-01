"""No-index bridge file writer used by governed bridge helpers.

The current bridge model uses dispatcher/TAFE state plus status-bearing
numbered files under ``bridge/``. This module only writes a new numbered file
after caller-side validation has passed; it never mutates aggregate queue state.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

from scripts.bridge_author_metadata import (
    ensure_author_metadata,
    extract_author_metadata,
    is_synthetic_session_context_id,
)

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


def _synthetic_session_context_id_for_content(content: str) -> str | None:
    session_context_id = extract_author_metadata(content).get("author_session_context_id")
    if is_synthetic_session_context_id(session_context_id):
        return str(session_context_id).strip().strip("`")
    return None


def _reject_synthetic_session_context_id(content: str) -> None:
    synthetic_session_context_id = _synthetic_session_context_id_for_content(content)
    if synthetic_session_context_id:
        raise BridgeTransitionError(
            "bridge artifact author_session_context_id must be a real session context id; "
            f"got synthetic harness placeholder {synthetic_session_context_id!r}. "
            "The authoring session or dispatcher must provide concrete metadata before write."
        )


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
    content_to_write = (
        ensure_author_metadata(content, project_root=project_root, explicit=author_metadata)
        if require_author_metadata
        else content
    )
    _reject_synthetic_session_context_id(content_to_write)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content_to_write, encoding="utf-8")
    written = target.read_text(encoding="utf-8")
    if written != content_to_write:
        raise BridgeConflictError(f"post-write verification failed for {target}: content on disk differs")
    return target
