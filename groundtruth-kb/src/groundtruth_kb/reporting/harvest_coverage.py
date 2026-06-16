# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""DA bridge-thread harvest coverage helper.

Coverage formula (per bridge/gtkb-da-harvest-coverage-implementation-004.md,
REVISED-1): distinct active VERIFIED thread names (denominator) vs distinct
thread names covered by at least one canonical wildcard deliberation row
(numerator). Set-based — cannot exceed 100%.

Ownership: GT-KB provides the helper + the doctor check; the retroactive
sweep itself and the ongoing harvest script live in Agent Red (the consumer
project) per the F5 ownership split.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Protocol

_BRIDGE_VERSION_FILE_RE = re.compile(r"^(.+)-(\d{3,})\.md$")
_BRIDGE_FILE_STATUS_RE = re.compile(
    r"^[#>*\-\s`]*(NEW|REVISED|GO|NO-GO|VERIFIED|ADVISORY|DEFERRED|WITHDRAWN|ACCEPTED|BLOCKED)\b",
    re.IGNORECASE,
)


class _DeliberationLister(Protocol):
    """Structural protocol for the DB dependency used by this helper.

    Only `list_deliberations` is needed; accepting this protocol (instead of
    importing `KnowledgeDB` directly) keeps the helper easy to fake in tests
    without spinning up a real SQLite database.
    """

    def list_deliberations(
        self,
        *,
        source_type: str | None = ...,
        source_ref: str | None = ...,
    ) -> list[dict[str, object]]: ...


def _status_from_bridge_file(path: Path) -> str | None:
    try:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            match = _BRIDGE_FILE_STATUS_RE.match(stripped)
            return match.group(1).upper() if match else None
    except OSError:
        return None
    return None


def _resolve_bridge_dir(path: Path) -> Path:
    if path.is_dir():
        return path
    if path.name.endswith(".md"):
        return path.parent
    return path / "bridge"


def _active_verified_threads(bridge_state_path: Path) -> list[str]:
    """Return thread names whose latest numbered bridge file is VERIFIED."""
    bridge_dir = _resolve_bridge_dir(bridge_state_path)
    if not bridge_dir.exists():
        return []

    grouped: dict[str, list[tuple[int, str]]] = {}
    for path in bridge_dir.glob("*.md"):
        match = _BRIDGE_VERSION_FILE_RE.match(path.name)
        if match is None:
            continue
        status = _status_from_bridge_file(path)
        if status is None:
            continue
        grouped.setdefault(match.group(1), []).append((int(match.group(2)), status))

    active_verified: list[str] = []
    for name, versions in grouped.items():
        _version, latest_status = max(versions, key=lambda item: item[0])
        if latest_status == "VERIFIED":
            active_verified.append(name)
    return sorted(active_verified)


def compute_active_bridge_thread_coverage(
    bridge_state_path: Path,
    db: _DeliberationLister,
) -> dict[str, object]:
    """Return DA harvest coverage metrics for active VERIFIED bridge threads.

    Args:
        bridge_state_path: Project root, bridge directory, or status-bearing
            bridge-file directory locator.
        db: Knowledge DB handle exposing ``list_deliberations``.

    Returns:
        dict with keys ``denominator_threads`` (int), ``numerator_threads`` (int),
        ``coverage_pct`` (float, 2 decimal places), ``uncovered_thread_names``
        (sorted list[str]), and ``covered_thread_names`` (sorted list[str]).

        Empty bridge state returns 100.0% coverage with denominator 0 — there
        are no threads whose coverage can be missed. This matches the convention
        used by the Agent Red retroactive sweep script.
    """
    active_verified = set(_active_verified_threads(bridge_state_path))

    all_bridge = db.list_deliberations(source_type="bridge_thread")
    covered: set[str] = set()
    for name in active_verified:
        prefix = f"bridge/{name}-"
        if any(str(d.get("source_ref", "")).startswith(prefix) for d in all_bridge):
            covered.add(name)

    denom = len(active_verified)
    num = len(covered)
    coverage_pct = round(100.0 * num / denom, 2) if denom else 100.0

    return {
        "denominator_threads": denom,
        "numerator_threads": num,
        "coverage_pct": coverage_pct,
        "uncovered_thread_names": sorted(active_verified - covered),
        "covered_thread_names": sorted(covered),
    }
