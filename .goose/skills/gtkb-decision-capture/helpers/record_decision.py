# THIS FILE IS A PROJECTION, NOT CANONICAL.
# Projected from the neutral harness baseline by the GT-KB projection engine.
# Do not edit here: change the baseline (.harness-baseline-configuration) and re-project with
# `gt harness project goose`. If a needed change cannot be made through
# the baseline and re-projection, file a work item against the projector
# (GOV-HARNESS-NEUTRAL-BASELINE-001 obligation 6).
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Helper for the /gtkb-decision-capture skill.

Records an owner decision as an append-only Deliberation Archive
record with fixed governance metadata. The helper never mutates
specs, work items, or any other artifact — its only write path is
``KnowledgeDB.insert_deliberation``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from groundtruth_kb.db import KnowledgeDB


class DeliberationIDCollisionError(RuntimeError):
    """Raised when a caller-supplied DELIB-ID already exists in the archive."""


class DeliberationInsertFailed(RuntimeError):
    """Raised when ``insert_deliberation`` returns ``None`` unexpectedly."""


class CompositeCompositionError(ValueError):
    """Raised when composite-decision inputs cannot form a coherent record."""


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


@dataclass(frozen=True)
class CompositeDecision:
    """One AskUserQuestion answer inside a composite owner-decision record.

    Attributes:
        source_ref: Where the answer came from, kept stable within one
            composite record. Use the AUQ-id form ``AUQ-<n>`` (or an
            owner-supplied question label) for AskUserQuestion answers, or a
            predecessor-deliberation section anchor such as ``§9.1`` when the
            answer resolves a numbered open question (the ``DELIB-2234``
            exemplar shape).
        decision: The decision the owner made for this answer.
        rationale: The rationale anchor or short reason for the decision.
    """

    source_ref: str
    decision: str
    rationale: str


def _escape_cell(value: str) -> str:
    """Escape a value so it is safe inside a single markdown table cell."""
    return value.replace("\\", "\\\\").replace("|", "\\|").replace("\n", " ").strip()


def compose_composite_content(
    heading: str,
    intro: str,
    decisions: list[CompositeDecision],
    *,
    composed_implications: list[str] | None = None,
    linked_artifacts: list[str] | None = None,
    first_concrete_actions: list[str] | None = None,
) -> str:
    """Compose several AUQ answers into one composite deliberation body.

    This is a **pure** string composer — it performs no database access and
    no redaction. The returned markdown body is intended to be passed as the
    ``content`` argument to :func:`record_decision`, so composite records
    flow through the same append-only, fixed-metadata write path as atomic
    records (``source_type='owner_conversation'``,
    ``outcome='owner_decision'``, fixed ``changed_by`` / ``change_reason``,
    and the DELIB-ID collision guard).

    The body carries the four canonical composite sections used by
    ``DELIB-2234`` and ``DELIB-2238``:

    - ``## Decisions`` — a markdown table with one row per
      :class:`CompositeDecision`, keyed by ``source_ref``.
    - ``## Composed Implications`` — cross-answer consequences.
    - ``## Linked Artifacts`` — specs, ADRs/DCLs, bridge threads, memory
      snapshots, and sibling deliberations, named by canonical source-ref.
    - ``## First Concrete Actions Authorized`` — the numbered next steps the
      composite decision authorizes.

    Later optional sections are omitted from the body when their list is
    empty, so a minimal composite record is just heading + intro + the
    Decisions table.

    Args:
        heading: Level-1 markdown heading for the composite record.
        intro: Prose that introduces the composite decision (what exchange
            it resolves and what triggered it).
        decisions: The per-answer decisions. At least one is required; a
            genuine composite normally carries two or more.
        composed_implications: Cross-answer implications (optional).
        linked_artifacts: Referenced artifacts named by source-ref
            (optional).
        first_concrete_actions: Numbered authorized next steps (optional).

    Returns:
        The composed markdown body.

    Raises:
        CompositeCompositionError: When ``decisions`` is empty or a
            required text field is blank.
    """
    if not decisions:
        raise CompositeCompositionError("a composite record requires at least one CompositeDecision")
    if not heading.strip():
        raise CompositeCompositionError("composite heading must not be blank")
    if not intro.strip():
        raise CompositeCompositionError("composite intro must not be blank")

    lines: list[str] = [f"# {heading.strip()}", "", intro.strip(), ""]

    lines.append("## Decisions")
    lines.append("")
    lines.append("| Source | Decision | Rationale |")
    lines.append("| --- | --- | --- |")
    for entry in decisions:
        if not entry.source_ref.strip():
            raise CompositeCompositionError("each CompositeDecision must carry a non-empty source_ref")
        if not entry.decision.strip():
            raise CompositeCompositionError(f"decision for source_ref {entry.source_ref!r} must not be blank")
        lines.append(
            f"| {_escape_cell(entry.source_ref)} | {_escape_cell(entry.decision)} | {_escape_cell(entry.rationale)} |"
        )
    lines.append("")

    if composed_implications:
        lines.append("## Composed Implications")
        lines.append("")
        lines.extend(f"- {item.strip()}" for item in composed_implications)
        lines.append("")

    if linked_artifacts:
        lines.append("## Linked Artifacts")
        lines.append("")
        lines.extend(f"- {item.strip()}" for item in linked_artifacts)
        lines.append("")

    if first_concrete_actions:
        lines.append("## First Concrete Actions Authorized")
        lines.append("")
        lines.extend(f"{index}. {item.strip()}" for index, item in enumerate(first_concrete_actions, start=1))
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"
