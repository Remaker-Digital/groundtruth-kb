# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Helper for the /gtkb-decision-capture skill.

Records an owner decision as an append-only Deliberation Archive
record with fixed governance metadata. The helper never mutates
specs, work items, or any other artifact — its only write path is
``KnowledgeDB.insert_deliberation``.
"""

from __future__ import annotations

from typing import Any

from groundtruth_kb.db import KnowledgeDB


class DeliberationIDCollisionError(RuntimeError):
    """Raised when a caller-supplied DELIB-ID already exists in the archive."""


class DeliberationInsertFailed(RuntimeError):
    """Raised when ``insert_deliberation`` returns ``None`` unexpectedly."""


_CHANGED_BY = "prime-builder/decision-capture-skill"
_CHANGE_REASON = "owner decision captured via /gtkb-decision-capture"


def record_decision(
    db: KnowledgeDB,
    delib_id: str,
    title: str,
    summary: str,
    content: str,
    *,
    spec_id: str | None = None,
    work_item_id: str | None = None,
    participants: list[str] | None = None,
    session_id: str | None = None,
) -> dict[str, Any]:
    """Capture an owner decision as an append-only deliberation.

    Contract:

    - ``source_type='owner_conversation'`` (fixed — not exposed to caller).
    - ``outcome='owner_decision'`` (fixed — not exposed to caller).
    - ``changed_by='prime-builder/decision-capture-skill'`` (fixed).
    - ``change_reason='owner decision captured via /gtkb-decision-capture'``
      (fixed).
    - Redaction is performed inside
      :meth:`KnowledgeDB.insert_deliberation`; the helper does not
      duplicate that pass.
    - Raises :class:`DeliberationIDCollisionError` when ``delib_id``
      already exists in the archive. The helper never silently
      version-bumps an unrelated owner decision.
    - Raises :class:`DeliberationInsertFailed` when
      ``insert_deliberation`` returns ``None`` (defensive guard — should
      not happen for a valid non-colliding insert).

    Args:
        db: Open :class:`KnowledgeDB` instance to write against.
        delib_id: Caller-generated ``DELIB-NNNN`` identifier. Must not
            already exist in the archive.
        title: Short headline for list views.
        summary: Short prose summary for detail views.
        content: Full decision body. May include considered
            alternatives, rationale, and owner quotes.
        spec_id: Optional spec reference for traceability.
        work_item_id: Optional work-item reference for traceability.
        participants: Optional list of participant identifiers.
        session_id: Optional session identifier (e.g., ``"S298"``).

    Returns:
        The persisted deliberation row as a dict. Includes the
        auto-assigned ``version``, the fixed ``changed_by`` /
        ``change_reason`` / ``source_type`` / ``outcome`` values, and
        any redaction markers applied to the content.
    """
    existing = db.get_deliberation(delib_id)
    if existing is not None:
        raise DeliberationIDCollisionError(
            f"DELIB-ID {delib_id!r} already exists (version {existing.get('version', '?')}). Generate a fresh ID."
        )

    row = db.insert_deliberation(
        id=delib_id,
        source_type="owner_conversation",
        title=title,
        summary=summary,
        content=content,
        changed_by=_CHANGED_BY,
        change_reason=_CHANGE_REASON,
        outcome="owner_decision",
        spec_id=spec_id,
        work_item_id=work_item_id,
        participants=participants,
        session_id=session_id,
    )
    if row is None:
        raise DeliberationInsertFailed(f"insert_deliberation returned None for {delib_id!r} — no row was persisted.")
    return row
