# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Normalize a malformed test-plan-phase membership representation to canonical JSON.

WI-5615: the canonical PLAN-001 PHASE-003 current ``test_ids`` value is
comma-delimited plain text instead of the required JSON list. Strict governed
writers reject that row as malformed. This service appends one governed phase
version that preserves the exact ordered test-id membership while encoding it
as a canonical JSON array, fail-closed on drift.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from typing import Any

from groundtruth_kb.db import KnowledgeDB

_CANONICAL_TEST_ID_RE = re.compile(r"^TEST-\d+$")


class PhaseMembershipNormalizeError(Exception):
    """Raised when phase-membership normalization cannot safely proceed."""


@dataclass(frozen=True)
class PhaseMembershipNormalizeRequest:
    phase_id: str
    expected_version: int
    expected_raw_sha256: str
    dry_run: bool = False
    changed_by: str = "prime-builder"
    change_reason: str = "WI-5615: normalize comma-delimited test_ids to canonical JSON"


@dataclass(frozen=True)
class PhaseMembershipNormalizeResult:
    phase_id: str
    source_version: int
    source_raw_sha256: str
    member_count: int
    member_list: list[str] = field(default_factory=list)
    proposed_json_sha256: str | None = None
    applied: bool = False
    new_version: int | None = None
    new_test_ids: str | None = None
    new_raw_sha256: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "phase_id": self.phase_id,
            "source_version": self.source_version,
            "source_raw_sha256": self.source_raw_sha256,
            "member_count": self.member_count,
            "proposed_json_sha256": self.proposed_json_sha256,
            "applied": self.applied,
            "new_version": self.new_version,
            "new_raw_sha256": self.new_raw_sha256,
        }


def _require_version(raw: Any, *, name: str) -> int:
    if isinstance(raw, bool):
        raise PhaseMembershipNormalizeError(f"{name} must be an integer")
    try:
        value = int(raw)  # type: ignore[arg-type]
    except (TypeError, ValueError) as exc:
        raise PhaseMembershipNormalizeError(f"{name} must be an integer") from exc
    if value <= 0:
        raise PhaseMembershipNormalizeError(f"{name} must be positive")
    return value


def _require_sha256(raw: Any, *, name: str) -> str:
    value = str(raw or "").strip().lower()
    if not re.fullmatch(r"[0-9a-f]{64}", value):
        raise PhaseMembershipNormalizeError(f"{name} must be a 64-char lowercase hex SHA-256")
    return value


def _parse_legacy_members(raw_test_ids: Any, *, phase_id: str) -> list[str]:
    """Parse the exact legacy comma-list representation into an ordered unique list."""
    if raw_test_ids is None:
        raise PhaseMembershipNormalizeError(f"{phase_id} has no test_ids to normalize")
    if not isinstance(raw_test_ids, str):
        raise PhaseMembershipNormalizeError(
            f"{phase_id} test_ids is already structured ({type(raw_test_ids).__name__}); not a legacy comma list"
        )
    raw = raw_test_ids.strip()
    if not raw:
        raise PhaseMembershipNormalizeError(f"{phase_id} test_ids is empty")
    # The legacy form is comma-delimited with no JSON brackets.
    if raw.lstrip().startswith("["):
        raise PhaseMembershipNormalizeError(f"{phase_id} test_ids is already a JSON array")
    members = [part.strip() for part in raw.split(",") if part.strip()]
    if not members:
        raise PhaseMembershipNormalizeError(f"{phase_id} test_ids parses to no members")
    bad = [m for m in members if not _CANONICAL_TEST_ID_RE.match(m)]
    if bad:
        raise PhaseMembershipNormalizeError(f"{phase_id} contains non-canonical TEST-* member(s): {bad[:5]}")
    if len(set(members)) != len(members):
        raise PhaseMembershipNormalizeError(f"{phase_id} contains duplicate members")
    return members


def _phase_raw_test_ids(db: KnowledgeDB, phase_id: str) -> str | None:
    """Return the raw ``test_ids`` column of the current phase row (unparsed)."""
    conn = db._get_conn()
    row = conn.execute("SELECT test_ids FROM current_test_plan_phases WHERE id = ?", (phase_id,)).fetchone()
    return row["test_ids"] if row is not None else None  # type: ignore[index]


def _phase_version(db: KnowledgeDB, phase_id: str) -> int | None:
    conn = db._get_conn()
    row = conn.execute("SELECT version FROM current_test_plan_phases WHERE id = ?", (phase_id,)).fetchone()
    return row["version"] if row is not None else None  # type: ignore[index]


def normalize_phase_membership(
    db: KnowledgeDB,
    request: PhaseMembershipNormalizeRequest,
) -> PhaseMembershipNormalizeResult:
    """Validate and, unless dry-run, append a canonical JSON membership version."""
    phase_id = request.phase_id.strip()
    if not phase_id:
        raise PhaseMembershipNormalizeError("phase_id must be non-empty")

    current_version = _phase_version(db, phase_id)
    if current_version is None:
        raise PhaseMembershipNormalizeError(f"Test plan phase {phase_id} not found")

    expected_version = _require_version(request.expected_version, name="expected_version")
    if current_version != expected_version:
        raise PhaseMembershipNormalizeError(
            f"version drift: current {phase_id} is version {current_version}, expected {expected_version}"
        )

    raw_test_ids = _phase_raw_test_ids(db, phase_id)
    raw_sha256 = hashlib.sha256((raw_test_ids or "").encode("utf-8")).hexdigest()
    expected_sha = _require_sha256(request.expected_raw_sha256, name="expected_raw_sha256")
    if raw_sha256 != expected_sha:
        raise PhaseMembershipNormalizeError(
            f"hash drift: current {phase_id} raw test_ids SHA-256 {raw_sha256}, expected {expected_sha}"
        )

    members = _parse_legacy_members(raw_test_ids, phase_id=phase_id)
    canonical = json.dumps(members, separators=(",", ":"))
    proposed_sha = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    result = PhaseMembershipNormalizeResult(
        phase_id=phase_id,
        source_version=current_version,
        source_raw_sha256=raw_sha256,
        member_count=len(members),
        member_list=members,
        proposed_json_sha256=proposed_sha,
        applied=False,
    )

    if request.dry_run:
        return result

    updated = db.update_test_plan_phase(
        phase_id,
        changed_by=request.changed_by,
        change_reason=request.change_reason,
        test_ids=members,
    )
    if updated is None:
        raise PhaseMembershipNormalizeError(f"update_test_plan_phase returned no current row for {phase_id}")

    new_raw = _phase_raw_test_ids(db, phase_id)
    new_sha = hashlib.sha256((new_raw or "").encode("utf-8")).hexdigest()
    return PhaseMembershipNormalizeResult(
        phase_id=phase_id,
        source_version=current_version,
        source_raw_sha256=raw_sha256,
        member_count=len(members),
        member_list=members,
        proposed_json_sha256=proposed_sha,
        applied=True,
        new_version=_phase_version(db, phase_id),
        new_test_ids=new_raw,
        new_raw_sha256=new_sha,
    )
