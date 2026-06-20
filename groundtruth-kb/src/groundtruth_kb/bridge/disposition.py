# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Shared bridge status disposition matrix.

This module centralizes the role/actionability/dispatchability rules used by
the bridge notification path and the manual bridge scan helper. It is intentionally
free of filesystem access so callers can apply document-kind classification
separately, then pass the resulting classification into the status matrix.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

PRIME_BUILDER_ROLE: Final[str] = "prime-builder"
LOYAL_OPPOSITION_ROLE: Final[str] = "loyal-opposition"

STATUS_NEW: Final[str] = "NEW"
STATUS_REVISED: Final[str] = "REVISED"
STATUS_GO: Final[str] = "GO"
STATUS_NO_GO: Final[str] = "NO-GO"
STATUS_VERIFIED: Final[str] = "VERIFIED"
STATUS_ADVISORY: Final[str] = "ADVISORY"
STATUS_DEFERRED: Final[str] = "DEFERRED"
STATUS_WITHDRAWN: Final[str] = "WITHDRAWN"

PRIME_ACTIONABLE_STATUSES: Final[frozenset[str]] = frozenset({STATUS_GO, STATUS_NO_GO, STATUS_ADVISORY})
LOYAL_OPPOSITION_ACTIONABLE_STATUSES: Final[frozenset[str]] = frozenset({STATUS_NEW, STATUS_REVISED})
OWNER_VISIBLE_STATUSES: Final[frozenset[str]] = frozenset({STATUS_ADVISORY})
TERMINAL_OR_CLOSED_STATUSES: Final[frozenset[str]] = frozenset({STATUS_VERIFIED, STATUS_DEFERRED, STATUS_WITHDRAWN})
VERIFIED_CONTEXT_STATUSES: Final[frozenset[str]] = frozenset({STATUS_VERIFIED})

CLASSIFICATION_TERMINAL: Final[str] = "terminal"

# Bridge-kind substring tokens. Matched against the lowercased + kebab-to-snake
# normalized bridge_kind value. Order matters: terminal is checked first so the
# more-specific tokens win before broader matches.
BRIDGE_KIND_TERMINAL_TOKENS: Final[tuple[str, ...]] = (
    "scoping",
    "closure",
    "parking",
    "index_reconciliation",
    "thread_reconciliation",
    "operational_state_change",
    "candidate_spec_intake",
    "governance_review",
    "spec_intake",
    "loyal_opposition_advisory",
    "governance_advisory",
    "post_implementation",
    "post_impl",
    "implementation_report",
)

BRIDGE_KIND_DISPATCHABLE_TOKENS: Final[tuple[str, ...]] = (
    "implementation_proposal",
    "implementation_slice",
    "multiphase_implementation",
    "fix",
    "governance_proposal",
    "architecture_proposal",
    "prime_proposal",
)


@dataclass(frozen=True)
class BridgeDisposition:
    """Status disposition for one recipient role."""

    status: str
    role: str
    actionable: bool
    dispatchable: bool
    owner_visible: bool
    terminal: bool
    reason_code: str
    next_action: str


def normalize_status(status: str) -> str:
    """Return bridge status in canonical uppercase form."""
    return str(status).strip().upper()


def normalize_role(role: str) -> str:
    """Return the canonical bridge recipient role for common legacy aliases."""
    role_key = str(role).strip().lower().replace("_", "-")
    if role_key in {"prime", "prime-builder"}:
        return PRIME_BUILDER_ROLE
    if role_key in {"codex", "lo", "loyal-opposition"}:
        return LOYAL_OPPOSITION_ROLE
    return role_key


def dispatchable_for_status(status: str, classification: str = "ambiguous") -> bool:
    """Return whether a status should trigger headless dispatch."""
    status_key = normalize_status(status)
    if status_key in LOYAL_OPPOSITION_ACTIONABLE_STATUSES:
        return True
    if status_key == STATUS_NO_GO:
        return True
    if status_key == STATUS_GO:
        return classification != CLASSIFICATION_TERMINAL
    return False


def _action_role_for_status(status: str) -> str | None:
    if status in LOYAL_OPPOSITION_ACTIONABLE_STATUSES:
        return LOYAL_OPPOSITION_ROLE
    if status in PRIME_ACTIONABLE_STATUSES:
        return PRIME_BUILDER_ROLE
    return None


def _reason_for_actionable(status: str) -> tuple[str, str]:
    if status in {STATUS_NEW, STATUS_REVISED}:
        return "lo_review_required", "review"
    if status == STATUS_GO:
        return "prime_go_continuation", "implement_or_continue"
    if status == STATUS_NO_GO:
        return "prime_revision_required", "revise"
    if status == STATUS_ADVISORY:
        return "prime_advisory_disposition", "owner_disposition"
    return "unknown_status", "none"


def _reason_for_non_actionable(status: str, expected_role: str | None) -> tuple[str, str]:
    if status in {STATUS_NEW, STATUS_REVISED} and expected_role == LOYAL_OPPOSITION_ROLE:
        return "wrong_role_lo_review", "loyal_opposition_review"
    if status in {STATUS_GO, STATUS_NO_GO} and expected_role == PRIME_BUILDER_ROLE:
        return "wrong_role_prime_continuation", "prime_builder_continuation"
    if status == STATUS_ADVISORY and expected_role == PRIME_BUILDER_ROLE:
        return "wrong_role_prime_advisory", "prime_builder_advisory_disposition"
    if status == STATUS_VERIFIED:
        return "terminal_verified", "none"
    if status == STATUS_DEFERRED:
        return "non_actionable_deferred", "none"
    if status == STATUS_WITHDRAWN:
        return "terminal_withdrawn", "none"
    return "unknown_status", "none"


def disposition_for_status(
    status: str,
    role: str,
    *,
    classification: str = "ambiguous",
) -> BridgeDisposition:
    """Return the bridge disposition for ``status`` from ``role``'s viewpoint."""
    status_key = normalize_status(status)
    role_key = normalize_role(role)
    expected_role = _action_role_for_status(status_key)
    actionable = expected_role == role_key
    reason_code, next_action = (
        _reason_for_actionable(status_key) if actionable else _reason_for_non_actionable(status_key, expected_role)
    )
    return BridgeDisposition(
        status=status_key,
        role=role_key,
        actionable=actionable,
        dispatchable=dispatchable_for_status(status_key, classification),
        owner_visible=status_key in OWNER_VISIBLE_STATUSES,
        terminal=status_key in TERMINAL_OR_CLOSED_STATUSES,
        reason_code=reason_code,
        next_action=next_action,
    )


def is_actionable_status_for_role(status: str, role: str) -> bool:
    """Return whether ``role`` should act on the given latest bridge status."""
    return disposition_for_status(status, role).actionable
