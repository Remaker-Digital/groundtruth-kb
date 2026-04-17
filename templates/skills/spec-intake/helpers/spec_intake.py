# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Helper for the /gtkb-spec-intake skill.

Wraps :mod:`groundtruth_kb.intake` with three helper functions so
skill callers get the confirm-before-mutate contract and audit-trail
differentiation for free. The helper never owns the business logic;
it delegates to the library pipeline and passes
``changed_by="prime-builder/spec-intake-skill"`` on every call.
"""

from __future__ import annotations

from typing import Any

from groundtruth_kb import intake as _intake
from groundtruth_kb.db import KnowledgeDB


class SpecIntakeCaptureFailed(RuntimeError):
    """Raised when ``intake.capture_requirement`` returns a malformed result."""


class SpecIntakeConfirmFailed(RuntimeError):
    """Raised when ``intake.confirm_intake`` returns an error dict."""


class SpecIntakeRejectFailed(RuntimeError):
    """Raised when ``intake.reject_intake`` returns an error dict.

    Also raised at the helper boundary when the ``reason`` argument is
    empty or whitespace-only — reject-without-reason is refused before
    any library call is made.
    """


_CHANGED_BY = "prime-builder/spec-intake-skill"
_CAPTURE_CHANGE_REASON = "Requirement captured via /gtkb-spec-intake skill"


def capture_candidate(
    db: KnowledgeDB,
    text: str,
    *,
    proposed_title: str,
    proposed_section: str,
    proposed_scope: str | None = None,
    proposed_type: str = "requirement",
    proposed_authority: str = "stated",
) -> dict[str, Any]:
    """Capture a requirement candidate at ``outcome='deferred'``.

    Delegates to :func:`groundtruth_kb.intake.capture_requirement`
    with ``changed_by=_CHANGED_BY`` and
    ``change_reason=_CAPTURE_CHANGE_REASON`` so the persisted
    deliberation records the skill actor. Audit-trail differentiation
    matches the ``gtkb-decision-capture`` and ``gtkb-bridge-propose``
    precedent.

    Args:
        db: Open :class:`KnowledgeDB` instance to write against.
        text: The owner's raw requirement text.
        proposed_title: Short headline for list / detail views.
        proposed_section: KB section (e.g., ``"auth"``,
            ``"observability"``) the candidate belongs to.
        proposed_scope: Optional scope string (free-form).
        proposed_type: KB spec ``type`` the candidate should use if
            confirmed (default ``"requirement"``).
        proposed_authority: KB spec ``authority`` level (default
            ``"stated"``).

    Returns:
        A dict with ``deliberation_id`` and the full captured
        ``content`` payload (same shape as
        :func:`intake.capture_requirement`'s return value).

    Raises:
        SpecIntakeCaptureFailed: If the library returns a value that
            is not a dict, or is a dict without a ``deliberation_id``
            key. This is a defensive guard against library
            regressions — not a recoverable user state.
    """
    result = _intake.capture_requirement(
        db,
        text,
        proposed_title=proposed_title,
        proposed_section=proposed_section,
        proposed_scope=proposed_scope,
        proposed_type=proposed_type,
        proposed_authority=proposed_authority,
        changed_by=_CHANGED_BY,
        change_reason=_CAPTURE_CHANGE_REASON,
    )
    if not isinstance(result, dict) or "deliberation_id" not in result:
        raise SpecIntakeCaptureFailed(f"capture_requirement returned malformed result: {result!r}")
    return result


def confirm_candidate(
    db: KnowledgeDB,
    deliberation_id: str,
) -> dict[str, Any]:
    """Confirm a captured candidate — creates a KB spec.

    Delegates to :func:`groundtruth_kb.intake.confirm_intake` with
    ``changed_by=_CHANGED_BY`` so both the new spec AND the
    confirmation-version deliberation record the skill actor.

    Args:
        db: Open :class:`KnowledgeDB` instance to write against.
        deliberation_id: The DELIB-ID returned by
            :func:`capture_candidate`.

    Returns:
        A dict with ``spec``, ``quality``, ``impact``,
        ``constraints``, and ``confirmed_spec_id`` keys (same shape
        as :func:`intake.confirm_intake`'s success-path return value).

    Raises:
        SpecIntakeConfirmFailed: If the library returns an error dict
            (unknown deliberation ID, non-intake deliberation, or
            ``insert_spec`` failure).
    """
    result = _intake.confirm_intake(
        db,
        deliberation_id,
        changed_by=_CHANGED_BY,
    )
    if "error" in result:
        raise SpecIntakeConfirmFailed(f"confirm_intake failed for {deliberation_id!r}: {result['error']}")
    return result


def reject_candidate(
    db: KnowledgeDB,
    deliberation_id: str,
    reason: str,
) -> dict[str, Any]:
    """Reject a captured candidate.

    Fails fast at the helper boundary when ``reason`` is empty or
    whitespace-only. Otherwise delegates to
    :func:`groundtruth_kb.intake.reject_intake` with
    ``changed_by=_CHANGED_BY``.

    Args:
        db: Open :class:`KnowledgeDB` instance to write against.
        deliberation_id: The DELIB-ID returned by
            :func:`capture_candidate`.
        reason: Non-empty owner-supplied rejection reason.

    Returns:
        A dict with ``deliberation_id``, ``rejected``, and ``reason``
        keys (same shape as :func:`intake.reject_intake`'s
        success-path return value).

    Raises:
        SpecIntakeRejectFailed: If ``reason`` is empty or
            whitespace-only (helper-boundary guard), or if the
            library returns an error dict (unknown deliberation ID,
            non-intake deliberation).
    """
    if not reason or not reason.strip():
        raise SpecIntakeRejectFailed("Rejection reason is required")
    result = _intake.reject_intake(
        db,
        deliberation_id,
        reason,
        changed_by=_CHANGED_BY,
    )
    if "error" in result:
        raise SpecIntakeRejectFailed(f"reject_intake failed for {deliberation_id!r}: {result['error']}")
    return result
