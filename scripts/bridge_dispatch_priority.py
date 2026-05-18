"""Bridge dispatch priority scoring - bridge scheduler Slice 6 (WI-3377).

Standalone, stdlib-only module. It computes a dispatch-priority score for a
bridge entry from the entry's age and an optional priority label, and orders a
set of entries by that score so the bridge scheduler's selector picks
anti-starvation-fairly instead of purely oldest-first.

The score is a linear effective-age model: a priority head-start measured in
hours plus the entry's real age in hours. Because the aging term is linear and
unbounded, an old low-priority entry always eventually outranks a fresh
high-priority one - the anti-starvation guarantee the owner's S350 throughput
directive asked for. The module is a pure function of its inputs: no
filesystem access, no runtime state, deterministic.

The module imports no dispatch code or sibling slice modules; wiring
select_next into the live dispatch selector is the deferred integration step,
so live dispatch behavior is unchanged by this module's existence.

Implements WI-3377 per bridge/gtkb-bridge-scheduler-lanes-leases-slice-6-001.md
(Loyal Opposition GO at -002).

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from datetime import datetime, timezone

# Priority head-start measured in hours: a higher-priority entry scores as if
# it were filed this many hours earlier than a P4 entry of the same real age.
DEFAULT_PRIORITY_HEADSTART_HOURS = {
    "P0": 96.0,
    "P1": 72.0,
    "P2": 48.0,
    "P3": 24.0,
    "P4": 0.0,
}

# The priority assigned to an entry that carries no priority field: a modest
# baseline head-start, neither emergency work nor bottom-of-queue.
DEFAULT_PRIORITY = "P3"

# The aging term contributes this many effective-hours of score per real-hour
# waited. Any positive rate preserves the anti-starvation guarantee.
DEFAULT_AGING_RATE_PER_HOUR = 1.0


def _to_utc(value: str | datetime) -> datetime:
    """Coerce a UTC ISO-8601 string or a datetime to an aware UTC datetime.

    A naive datetime, or an ISO-8601 string without an offset, is interpreted
    as UTC - the documented input contract - so a host-local timezone never
    influences a dispatch score. An aware datetime in another zone is
    converted to UTC.
    """
    if isinstance(value, str):
        dt = datetime.fromisoformat(value)
    elif isinstance(value, datetime):
        dt = value
    else:
        raise TypeError(
            f"filed_at/now must be a UTC ISO-8601 string or a datetime, "
            f"got {type(value).__name__}"
        )
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _normalize_priority(priority: object) -> str:
    """Normalize a priority label to a canonical key of
    DEFAULT_PRIORITY_HEADSTART_HOURS.

    Case-insensitive and whitespace-trimmed, so 'p2' and ' P2 ' both resolve
    to 'P2' rather than silently degrading to the default. A None, non-string,
    or unrecognized label resolves to DEFAULT_PRIORITY without raising.
    """
    if isinstance(priority, str):
        candidate = priority.strip().upper()
        if candidate in DEFAULT_PRIORITY_HEADSTART_HOURS:
            return candidate
    return DEFAULT_PRIORITY


def priority_headstart(priority: object) -> float:
    """Return the head-start hours for a priority label.

    Case-insensitive; an unknown or None priority maps to DEFAULT_PRIORITY's
    head-start. Never raises.
    """
    return DEFAULT_PRIORITY_HEADSTART_HOURS[_normalize_priority(priority)]


def dispatch_score(*, filed_at: str | datetime, priority: object = None,
                    now: str | datetime | None = None,
                    aging_rate: float = DEFAULT_AGING_RATE_PER_HOUR) -> float:
    """Compute the dispatch-priority score for one bridge entry.

    score = priority_headstart(priority) + aging_rate * age_hours, where
    age_hours = max(0.0, (now - filed_at) in hours). filed_at and now accept a
    UTC ISO-8601 string or a datetime; now defaults to the current UTC time.
    A filed_at in the future clamps age_hours to 0.0 - no negative score, no
    raise.
    """
    filed_dt = _to_utc(filed_at)
    now_dt = _to_utc(now) if now is not None else datetime.now(timezone.utc)
    age_hours = max(0.0, (now_dt - filed_dt).total_seconds() / 3600.0)
    return priority_headstart(priority) + aging_rate * age_hours


def sort_by_dispatch_priority(entries, *, now: str | datetime | None = None,
                              aging_rate: float = DEFAULT_AGING_RATE_PER_HOUR) -> list:
    """Return entries ordered by descending dispatch score.

    Each entry is a mapping carrying at least 'filed_at' and optionally
    'priority'. Score ties are broken by older filed_at first; entries with an
    identical score and an identical filed_at keep their input order (the sort
    is stable), so the ordering is total and deterministic. now is resolved
    once and applied to every entry.
    """
    now_dt = _to_utc(now) if now is not None else datetime.now(timezone.utc)
    materialized = list(entries)

    def _key(entry):
        filed_dt = _to_utc(entry["filed_at"])
        score = dispatch_score(filed_at=filed_dt, priority=entry.get("priority"),
                               now=now_dt, aging_rate=aging_rate)
        # Ascending sort on (-score, filed_dt): highest score first, then
        # oldest filed_at first. A stable sort keeps input order for entries
        # equal on both keys.
        return (-score, filed_dt)

    return sorted(materialized, key=_key)


def select_next(entries, *, now: str | datetime | None = None,
                aging_rate: float = DEFAULT_AGING_RATE_PER_HOUR):
    """Return the single highest-scoring entry, or None for empty input."""
    ordered = sort_by_dispatch_priority(entries, now=now, aging_rate=aging_rate)
    return ordered[0] if ordered else None
