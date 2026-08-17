"""Project-scoped implementation authorization helpers."""

from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import Any

ACTIVE_PROJECT_AUTHORIZATION_STATUS = "active"
PROJECT_AUTHORIZATION_TERMINAL_STATUSES = frozenset({"revoked", "expired", "superseded"})

# WI-6617 / DCL-PROJECT-AUTHORIZATION-EVENT-TRANSACTION-001 C2: a new
# authorization identity must not resolve to an individual work item.
_WORK_ITEM_SCOPED_AUTH_ID_RE = re.compile(r"(?i)(?:^|[-_])WI-\d+(?:[-_]|$)")
_BARE_WORK_ITEM_ID_RE = re.compile(r"^WI-\d+$")
_PAUTH_WI_IDENTITY_RE = re.compile(r"(?i)PAUTH-WI-\d+")


def _normalized_id_list(values: list[str] | None) -> list[str]:
    if not values:
        return []
    return [str(item).strip() for item in values if str(item).strip()]


def work_item_scoped_authorization_identity(
    authorization_id: str | None,
    scope_summary: str | None = None,
) -> str | None:
    """Return a C2 reason when identity or declared scope names a work item."""
    auth_id = str(authorization_id or "").strip()
    if auth_id and (_PAUTH_WI_IDENTITY_RE.search(auth_id) or _WORK_ITEM_SCOPED_AUTH_ID_RE.search(auth_id)):
        return (
            "Authorization identity "
            f"{auth_id!r} designates an individual work item "
            "(DCL-PROJECT-AUTHORIZATION-EVENT-TRANSACTION-001 C2)."
        )
    scope = str(scope_summary or "").strip()
    if scope and _BARE_WORK_ITEM_ID_RE.fullmatch(scope):
        return (
            "Authorization scope "
            f"{scope!r} designates an individual work item "
            "(DCL-PROJECT-AUTHORIZATION-EVENT-TRANSACTION-001 C2)."
        )
    return None


def reject_authorization_creation_c2_c4(
    *,
    authorization_id: str | None,
    scope_summary: str | None,
    included_work_item_ids: list[str] | None,
    excluded_work_item_ids: list[str] | None,
    new_identity: bool,
) -> None:
    """Reject C2 (new identity only) and C4 (any version) before a row is appended.

    Existing PAUTH-WI-* identities remain appendable until WI-6618's
    supersession pass; C2 fail-closed on that population is out of this slice.
    """
    included = _normalized_id_list(included_work_item_ids)
    excluded = _normalized_id_list(excluded_work_item_ids)
    if included or excluded:
        raise ValueError(
            "Project authorization envelope must not enumerate included or "
            "excluded work-item IDs (GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 "
            "v3 / DCL-PROJECT-AUTHORIZATION-EVENT-TRANSACTION-001 C4)."
        )
    if new_identity:
        reason = work_item_scoped_authorization_identity(authorization_id, scope_summary)
        if reason:
            raise ValueError(reason)


def parse_expires_at(value: str | None) -> datetime | None:
    if not value:
        return None
    text = value[:-1] + "+00:00" if value.endswith("Z") else value
    parsed = datetime.fromisoformat(text)
    return parsed.astimezone(UTC) if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def is_project_authorization_active(row: dict[str, Any], *, now: datetime | None = None) -> bool:
    if row.get("status") != ACTIVE_PROJECT_AUTHORIZATION_STATUS:
        return False
    expiry = parse_expires_at(row.get("expires_at"))
    if expiry is None:
        return True
    return expiry >= (now or datetime.now(UTC))
