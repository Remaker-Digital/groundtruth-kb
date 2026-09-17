# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Helper for the /gtkb-spec-intake skill: direct native intake with skill attribution.

Wraps :mod:`groundtruth_kb.spec_intake`. A candidate is temporary and grants nothing; confirmation writes one
specification through the native authority with ``changed_by="prime-builder/spec-intake-skill"``; rejection
discards the candidate and writes nothing. The persisted deliberation queue is retired (O-7 R24).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from groundtruth_kb import spec_intake as _intake
from groundtruth_kb.authority_client import AuthorityClient, AuthorityClientError


class SpecIntakeCaptureFailed(RuntimeError):
    """Raised when the candidate cannot be extracted (empty text, title or section, or an unknown authority)."""


class SpecIntakeConfirmFailed(RuntimeError):
    """Raised when confirmation is refused before or by the authority (wrong target, taken identity, readback)."""


class SpecIntakeRejectFailed(RuntimeError):
    """Raised at the helper boundary when the reason is empty or the object is not a candidate."""


_CHANGED_BY = "prime-builder/spec-intake-skill"


def capture_candidate(
    text: str,
    *,
    proposed_title: str,
    proposed_section: str,
    proposed_scope: str | None = None,
    proposed_type: str = "requirement",
    proposed_authority: str = "stated",
    candidate_dir: Path | None = None,
) -> dict[str, Any]:
    """Extract a temporary candidate (optionally saved under ``candidate_dir``); nothing canonical changes."""
    try:
        return _intake.capture_candidate(
            text,
            proposed_title=proposed_title,
            proposed_section=proposed_section,
            proposed_scope=proposed_scope,
            proposed_type=proposed_type,
            proposed_authority=proposed_authority,
            candidate_dir=candidate_dir,
        )
    except _intake.IntakeError as error:
        raise SpecIntakeCaptureFailed(str(error)) from error


def confirm_candidate(
    client: AuthorityClient, candidate: dict[str, Any], *, spec_id: str | None = None
) -> dict[str, Any]:
    """Write the confirmed specification with skill attribution and exact readback."""
    try:
        return _intake.confirm_candidate(
            client,
            candidate,
            actor=_CHANGED_BY,
            spec_id=spec_id,
            reason="Requirement confirmed via /gtkb-spec-intake skill",
        )
    except (_intake.IntakeError, AuthorityClientError) as error:
        raise SpecIntakeConfirmFailed(str(error)) from error


def reject_candidate(candidate: dict[str, Any], reason: str) -> dict[str, Any]:
    """Discard the candidate with the owner's reason; no canonical record is written."""
    if not reason or not reason.strip():
        raise SpecIntakeRejectFailed("reject_candidate requires a non-empty reason")
    try:
        return _intake.reject_candidate(candidate, reason)
    except _intake.IntakeError as error:
        raise SpecIntakeRejectFailed(str(error)) from error
