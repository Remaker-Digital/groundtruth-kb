"""Bridge dispatch rule helpers."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

OPEN_ACTIVITY_RE = re.compile(r"^\s*::open\s+(?P<activity>[^\s#]+)", re.IGNORECASE | re.MULTILINE)
SESSION_SUBJECT_RE = re.compile(
    r"^\s*(?:session_subject|subject):\s*(?P<subject>.+?)\s*$", re.IGNORECASE | re.MULTILINE
)


@dataclass(frozen=True)
class DispatchContext:
    """Context used when matching a bridge work item to dispatch rules."""

    required_role: str
    status: str | None = None
    session_subject: str | None = None
    activity: str | None = None

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "required_role": self.required_role,
            "status": self.status,
            "session_subject": self.session_subject,
            "activity": self.activity,
        }


@dataclass(frozen=True)
class DispatchRule:
    """A declarative eligibility/ranking rule from ``config/dispatcher/rules.toml``."""

    id: str
    required_roles: tuple[str, ...] = ()
    blocked_roles: tuple[str, ...] = ()
    statuses: tuple[str, ...] = ()
    session_subjects: tuple[str, ...] = ()
    activities: tuple[str, ...] = ()
    prefer: tuple[str, ...] = field(default_factory=tuple)

    @classmethod
    def from_mapping(cls, raw: dict[str, Any]) -> DispatchRule:
        return cls(
            id=str(raw.get("id") or "unnamed-rule").strip(),
            required_roles=_string_tuple(raw.get("required_roles")),
            blocked_roles=_string_tuple(raw.get("blocked_roles")),
            statuses=_string_tuple(raw.get("statuses")),
            session_subjects=_string_tuple(raw.get("session_subjects")),
            activities=_string_tuple(raw.get("activities")),
            prefer=_string_tuple(raw.get("prefer")),
        )

    def matches(self, context: DispatchContext) -> bool:
        role = context.required_role.strip().lower()
        if self.required_roles and role not in {r.lower() for r in self.required_roles}:
            return False
        if role in {r.lower() for r in self.blocked_roles}:
            return False
        if self.statuses and (context.status or "").upper() not in {s.upper() for s in self.statuses}:
            return False
        if self.session_subjects and not _matches_optional(context.session_subject, self.session_subjects):
            return False
        return not (self.activities and not _matches_optional(context.activity, self.activities))

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "required_roles": list(self.required_roles),
            "blocked_roles": list(self.blocked_roles),
            "statuses": list(self.statuses),
            "session_subjects": list(self.session_subjects),
            "activities": list(self.activities),
            "prefer": list(self.prefer),
        }


def extract_open_activity(text: str) -> str | None:
    """Return the first ``::open <activity>`` declaration in ``text``."""
    match = OPEN_ACTIVITY_RE.search(text)
    if match is None:
        return None
    return match.group("activity").strip() or None


def extract_session_subject(text: str) -> str | None:
    """Return the first simple ``subject:`` / ``session_subject:`` value."""
    match = SESSION_SUBJECT_RE.search(text)
    if match is None:
        return None
    return match.group("subject").strip() or None


def context_from_bridge_text(required_role: str, text: str, *, status: str | None = None) -> DispatchContext:
    """Build a dispatch context from a bridge/session envelope text body."""
    return DispatchContext(
        required_role=required_role,
        status=status,
        session_subject=extract_session_subject(text),
        activity=extract_open_activity(text),
    )


def _string_tuple(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, (list, tuple, set, frozenset)):
        return ()
    return tuple(str(item).strip() for item in value if str(item).strip())


def _matches_optional(actual: str | None, allowed: tuple[str, ...]) -> bool:
    if actual is None:
        return False
    folded = actual.strip().lower()
    return folded in {item.strip().lower() for item in allowed}
