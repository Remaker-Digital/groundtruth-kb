"""AUQ -> Deliberation Archive auto-archive helper.

Reuses the Slice 1 ``record_deliberation`` in-process service when the
owner-decision-tracker hook detects a resolved AskUserQuestion that crosses
the deliberation-protocol capture threshold. Classification is deterministic
per ``SPEC-AUQ-NO-LLM-CLASSIFIER-001``; the helper itself imports no LLM or
embedding library, and the heavy imports (``cli_deliberations_record`` +
``config``) are deferred to ``archive_decision()`` so default-off tracker
invocations pay zero additional import cost.
"""

from __future__ import annotations

import contextlib
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Acknowledgement-only or short-noise answer patterns. Deterministic
# frozenset; no LLM. Conservative: when in doubt, classifier returns
# (True, ...) so the risk is over-archive rather than under-archive.
_OUT_OF_SCOPE_ANSWERS: frozenset[str] = frozenset(
    {
        "",
        "ok",
        "okay",
        "ack",
        "acknowledged",
        "thanks",
        "thank you",
        "ty",
        "tool loaded",
        "tool loaded.",
        "noted",
        "got it",
        "y",
        "n",
    }
)


@dataclass(frozen=True)
class DecisionForArchive:
    """Subset of tracker ``DecisionEntry`` fields needed for archival.

    Mirrors the tracker's data shape so the hook integration can construct
    this from a resolved ``DecisionEntry`` with simple field copies.
    """

    decision_id: str
    question: str
    options: tuple[str, ...] = field(default_factory=tuple)
    answer: str = ""
    resolved_at: str = ""
    session_id: str = ""
    detected_via: str = "ask_user_question"


def should_auto_archive(decision: DecisionForArchive) -> tuple[bool, str]:
    """Deterministic classifier: should this decision auto-archive?

    Returns ``(False, reason)`` for non-AUQ-detected, unresolved, empty-answer,
    or out-of-scope-content decisions. Returns ``(True, "in-scope owner
    decision")`` otherwise.
    """
    if decision.detected_via != "ask_user_question":
        return False, "not an AUQ"
    if not decision.resolved_at:
        return False, "unresolved"
    if not decision.answer:
        return False, "empty answer"
    if decision.answer.strip().lower() in _OUT_OF_SCOPE_ANSWERS:
        return False, "out-of-scope content"
    return True, "in-scope owner decision"


def _render_body(decision: DecisionForArchive) -> str:
    """Render the decision content body as markdown for the DA record."""
    parts: list[str] = []
    parts.append(f"# {decision.decision_id}")
    parts.append("")
    if decision.resolved_at:
        parts.append(f"Resolved: {decision.resolved_at}")
    if decision.session_id:
        parts.append(f"Session: {decision.session_id}")
    parts.append("")
    parts.append("## Question")
    parts.append(decision.question)
    parts.append("")
    if decision.options:
        parts.append("## Options")
        for opt in decision.options:
            parts.append(f"- {opt}")
        parts.append("")
    parts.append("## Answer")
    parts.append(decision.answer)
    parts.append("")
    return "\n".join(parts)


def archive_decision(
    decision: DecisionForArchive,
    *,
    project_root: Path | None = None,
    config: Any = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Archive a resolved AUQ as a deliberation via the governed service.

    Calls ``record_deliberation`` in-process with
    ``source_type="owner_conversation"``, ``outcome="owner_decision"``,
    and the decision ID as ``source_ref`` so the Slice 1 service's
    source_ref+content_hash idempotency naturally deduplicates repeat
    archives of the same decision.
    """
    # Lazy imports to keep default-off tracker invocations cost-free.
    from groundtruth_kb.cli_deliberations_record import (
        DeliberationRecordRequest,
        record_deliberation,
    )
    from groundtruth_kb.config import GTConfig

    if project_root is None:
        raise ValueError(
            "archive_decision requires an explicit project_root anchor; "
            "implicit Path.cwd() resolution can leak writes into a live "
            "GT-KB checkout when the caller runs from the project root "
            "(Slice 4 NO-GO -007 F1 root cause)."
        )
    root = project_root.resolve()
    tmp_dir = root / ".tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    body = _render_body(decision)

    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".md",
        prefix=f"auq-archive-{decision.decision_id}-",
        delete=False,
        dir=str(tmp_dir),
        encoding="utf-8",
    ) as handle:
        handle.write(body)
        content_file = Path(handle.name)

    try:
        request = DeliberationRecordRequest(
            source_type="owner_conversation",
            source_ref=decision.decision_id,
            title=decision.question[:120] if decision.question else decision.decision_id,
            summary=(f"Owner answered: {decision.answer[:120]}" if decision.answer else "Owner decision recorded"),
            content_file=content_file,
            change_reason=(
                "Auto-archive via owner-decision-tracker "
                "(Slice 4; deterministic classification per SPEC-AUQ-NO-LLM-CLASSIFIER-001)"
            ),
            auq_id=decision.decision_id,
            auq_answer=decision.answer,
            owner_presented=True,
            approved_by=None,
            spec_id=None,
            work_item_id=None,
            participants=None,
            outcome="owner_decision",
            session_id=decision.session_id or None,
            dry_run=dry_run,
        )
        active_config = config or GTConfig(
            db_path=root / "groundtruth.db",
            project_root=root,
        )
        return record_deliberation(active_config, request)
    finally:
        with contextlib.suppress(OSError):
            content_file.unlink()
