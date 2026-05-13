"""Project-scoped implementation authorization helpers."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

ACTIVE_PROJECT_AUTHORIZATION_STATUS = "active"
PROJECT_AUTHORIZATION_TERMINAL_STATUSES = frozenset({"revoked", "expired", "superseded"})


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
