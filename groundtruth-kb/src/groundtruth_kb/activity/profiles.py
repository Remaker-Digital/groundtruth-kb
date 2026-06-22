"""Activity disposition profile loader — DCL-ACTIVITY-DISPOSITION-PROFILE-001.

Provides the canonical reader entrypoint ``load_activity_profiles`` for the
TOML config at ``config/agent-control/activity-disposition-profiles.toml``.
The loader validates against the DCL schema (assertions A1–A3) and raises
``ActivityProfileError`` fail-closed on any violation.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved. Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Six canonical activities per DELIB-20265287 D4 / DELIB-20260621 DEC-4.
CANONICAL_ACTIVITIES: frozenset[str] = frozenset({"ops", "deliberation", "build", "test", "spec", "project"})

# Valid headless_eligibility tokens.
_VALID_ELIGIBILITY: frozenset[str] = frozenset({"headless_eligible", "interactive_only", "interactive_primary"})

# Required per-profile D4 headless_eligibility mapping (DELIB-20265287 D4).
_D4_ELIGIBILITY: dict[str, str] = {
    "spec": "headless_eligible",
    "build": "headless_eligible",
    "test": "headless_eligible",
    "deliberation": "interactive_only",
    "project": "interactive_only",
    "ops": "interactive_primary",
}

# Four payload classes required by DCL-ACTIVITY-DISPOSITION-PROFILE-001 A2.
_REQUIRED_CLASSES: tuple[str, ...] = ("skills", "terminology", "history_state", "direction")

# Path from this file (activity/profiles.py) up to the project root.
_PROJECT_ROOT = Path(__file__).resolve().parents[4]
_DEFAULT_CONFIG_PATH = _PROJECT_ROOT / "config" / "agent-control" / "activity-disposition-profiles.toml"


class ActivityProfileError(ValueError):
    """Raised when the activity disposition profile config is missing or invalid."""


@dataclass(frozen=True)
class ActivityProfile:
    """Validated activity disposition profile entry."""

    name: str
    version: int
    headless_eligibility: str
    skills: list[str]
    terminology: list[str]
    history_state: dict[str, Any]
    direction: dict[str, Any]


def load_activity_profiles(path: Path | None = None) -> dict[str, ActivityProfile]:
    """Load and validate the activity disposition profiles from *path*.

    Uses the shipped ``config/agent-control/activity-disposition-profiles.toml``
    when *path* is ``None``.  Returns a mapping from activity name to
    :class:`ActivityProfile`.  Raises :class:`ActivityProfileError` fail-closed
    when any DCL A1–A3 assertion is violated.
    """
    resolved = path if path is not None else _DEFAULT_CONFIG_PATH

    try:
        raw = tomllib.loads(resolved.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ActivityProfileError(f"Activity profiles config not found: {resolved}") from exc
    except tomllib.TOMLDecodeError as exc:
        raise ActivityProfileError(f"Invalid TOML in {resolved}: {exc}") from exc

    activities_raw: dict[str, Any] = raw.get("activities", {})

    # A1: all six canonical activities must be present.
    missing = CANONICAL_ACTIVITIES - set(activities_raw)
    if missing:
        raise ActivityProfileError(
            f"DCL-ACTIVITY-DISPOSITION-PROFILE-001 A1 violation: missing activity profiles: {sorted(missing)}"
        )

    profiles: dict[str, ActivityProfile] = {}
    for name in CANONICAL_ACTIVITIES:
        entry: dict[str, Any] = activities_raw[name]

        # A2: each profile must define all four payload classes.
        missing_classes = [cls for cls in _REQUIRED_CLASSES if cls not in entry]
        if missing_classes:
            raise ActivityProfileError(
                f"DCL-ACTIVITY-DISPOSITION-PROFILE-001 A2 violation: "
                f"activity '{name}' missing class(es): {missing_classes}"
            )

        # A3: headless_eligibility must be a valid token and D4-consistent.
        eligibility = entry.get("headless_eligibility", "")
        if eligibility not in _VALID_ELIGIBILITY:
            raise ActivityProfileError(
                f"DCL-ACTIVITY-DISPOSITION-PROFILE-001 A3 violation: "
                f"activity '{name}' has invalid headless_eligibility {eligibility!r}; "
                f"must be one of {sorted(_VALID_ELIGIBILITY)}"
            )
        expected = _D4_ELIGIBILITY[name]
        if eligibility != expected:
            raise ActivityProfileError(
                f"DCL-ACTIVITY-DISPOSITION-PROFILE-001 A3 violation: "
                f"activity '{name}' headless_eligibility is {eligibility!r} "
                f"but DELIB-20265287 D4 requires {expected!r}"
            )

        profiles[name] = ActivityProfile(
            name=name,
            version=int(entry.get("version", 1)),
            headless_eligibility=eligibility,
            skills=list(entry.get("skills", [])),
            terminology=list(entry.get("terminology", [])),
            history_state=dict(entry.get("history_state", {})),
            direction=dict(entry.get("direction", {})),
        )

    return profiles
