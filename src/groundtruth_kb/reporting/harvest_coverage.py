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

_DOC_LINE_RE = re.compile(r"^Document:\s+(.+)$")
_STATUS_LINE_RE = re.compile(r"^(NEW|REVISED|GO|NO-GO|VERIFIED):\s+bridge/(.+\.md)$")


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


def _active_verified_threads(index_path: Path) -> list[str]:
    """Parse bridge INDEX and return active thread names whose latest status is VERIFIED.

    The INDEX format per `.claude/rules/file-bridge-protocol.md`:

        Document: <thread-name>
        <STATUS>: bridge/<thread-name>-NNN.md   (newest first within the entry)
        <STATUS>: bridge/<thread-name>-NNN.md
        ...
    """
    if not index_path.exists():
        return []

    active_verified: list[str] = []
    current_name: str | None = None
    first_status: str | None = None

    def _flush() -> None:
        nonlocal current_name, first_status
        if current_name is not None and first_status == "VERIFIED":
            active_verified.append(current_name)
        current_name = None
        first_status = None

    for raw_line in index_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("<!--") or line.startswith("#"):
            continue

        doc_match = _DOC_LINE_RE.match(line)
        if doc_match:
            _flush()
            current_name = doc_match.group(1).strip()
            first_status = None
            continue

        status_match = _STATUS_LINE_RE.match(line)
        if status_match and current_name is not None and first_status is None:
            # First status line within an entry = latest status (newest-first ordering)
            first_status = status_match.group(1)

    _flush()
    return active_verified


def compute_active_bridge_thread_coverage(
    index_path: Path,
    db: _DeliberationLister,
) -> dict[str, object]:
    """Return DA harvest coverage metrics for active VERIFIED bridge threads.

    Args:
        index_path: Path to ``bridge/INDEX.md`` in the consumer project.
        db: Knowledge DB handle exposing ``list_deliberations``.

    Returns:
        dict with keys ``denominator_threads`` (int), ``numerator_threads`` (int),
        ``coverage_pct`` (float, 2 decimal places), ``uncovered_thread_names``
        (sorted list[str]), and ``covered_thread_names`` (sorted list[str]).

        Empty index returns 100.0% coverage with denominator 0 — there are no
        threads whose coverage can be missed. This matches the convention used
        by the Agent Red retroactive sweep script.
    """
    active_verified = set(_active_verified_threads(index_path))

    covered: set[str] = set()
    for name in active_verified:
        hits = db.list_deliberations(
            source_type="bridge_thread",
            source_ref=f"bridge/{name}-*.md",
        )
        if hits:
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
