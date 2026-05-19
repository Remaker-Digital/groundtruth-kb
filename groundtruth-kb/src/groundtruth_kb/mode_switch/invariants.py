"""Role-map partition checks for the operating-mode subsystem.

``REQ-HARNESS-REGISTRY-001`` FR9 requires that ``gt harness set-role`` leave
the active harness set with exactly one ``prime-builder`` assignment and exactly
one ``loyal-opposition`` assignment. When more than one harness is active, those
roles must be assigned to different active harnesses. Inactive harnesses remain
registered but carry no operating role.

It reads the harness registry projection
(``harness-state/harness-registry.json``) and computes over the role-set wire
form — a list of role tokens, or a legacy scalar string per
``ADR-SINGLE-HARNESS-OPERATING-MODE-001``.

Authority: ``REQ-HARNESS-REGISTRY-001`` FR9; ``DELIB-2080`` (the
single-prime-builder amendment); ``GOV-HARNESS-ROLE-PORTABILITY-001`` (Prime
Builder and Loyal Opposition are portable harness-assigned roles).

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights
reserved.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Role tokens that count as holding the prime-builder role. The legacy
# ``acting-prime-builder`` provenance token is READ-accepted per
# ``GOV-ACTING-PRIME-BUILDER-001``; it counts toward the single-prime-builder
# invariant so a stale provenance value cannot mask a second prime-class
# harness.
_PRIME_BUILDER_TOKENS = frozenset({"prime-builder", "acting-prime-builder"})


class RolePartitionViolation(RuntimeError):
    """Raised when the active role map is not a valid registrar partition."""


@dataclass(frozen=True)
class RolePartitionSummary:
    prime_builder_id: str
    loyal_opposition_id: str
    active_harness_ids: tuple[str, ...]


def _role_tokens(role_field: Any) -> set[str]:
    """Normalize a harness record's ``role`` field to a set of role tokens.

    Accepts the list wire form (``["prime-builder"]``) and the legacy scalar
    wire form (``"prime-builder"``); any other value yields an empty set.
    """
    if isinstance(role_field, list):
        return {str(token).strip() for token in role_field if str(token).strip()}
    if isinstance(role_field, str) and role_field.strip():
        return {role_field.strip()}
    return set()


def prime_builder_ids(role_document: dict[str, Any]) -> list[str]:
    """Return the sorted harness ids holding a prime-builder-class role.

    A harness counts when its role set contains ``prime-builder`` or the
    READ-compatible ``acting-prime-builder`` provenance token.
    """
    harnesses = role_document.get("harnesses", {})
    if not isinstance(harnesses, dict):
        return []
    return sorted(
        harness_id
        for harness_id, record in harnesses.items()
        if isinstance(record, dict)
        and record.get("status") == "active"
        and _PRIME_BUILDER_TOKENS & _role_tokens(record.get("role"))
    )


def loyal_opposition_ids(role_document: dict[str, Any]) -> list[str]:
    """Return the sorted active harness ids holding loyal-opposition."""
    harnesses = role_document.get("harnesses", {})
    if not isinstance(harnesses, dict):
        return []
    return sorted(
        harness_id
        for harness_id, record in harnesses.items()
        if isinstance(record, dict)
        and record.get("status") == "active"
        and "loyal-opposition" in _role_tokens(record.get("role"))
    )


def verify_active_role_partition(project_root: Path, *, role_path: Path | None = None) -> RolePartitionSummary:
    """Verify the role map satisfies the active-harness PB/LO invariant.

    Loads the harness registry projection under ``project_root`` (or the
    explicit ``role_path`` override) and raises ``RolePartitionViolation``
    unless exactly one active harness holds a prime-builder-class role and
    exactly one active harness holds loyal-opposition. With multiple active
    harnesses, the two role holders must be different. Registered, suspended,
    and retired harnesses must carry no operating role.

    WI-3342 IP-5: migrated from the retired
    ``harness-state/role-assignments.json`` to the DB-backed registry
    projection ``harness-state/harness-registry.json``. The projection stores
    ``harnesses`` as a LIST of unified records; it is converted here to the
    ``{harness_id: record}`` document shape that ``prime_builder_ids`` and the
    partition check consume.
    """
    from groundtruth_kb.harness_projection import harness_registry_path

    path = role_path if role_path is not None else harness_registry_path(project_root)
    projection = json.loads(Path(path).read_text(encoding="utf-8"))
    projection_harnesses = projection.get("harnesses", []) if isinstance(projection, dict) else None
    if not isinstance(projection_harnesses, list):
        raise RolePartitionViolation(f"harness registry projection at {path} has no 'harnesses' list")
    harnesses = {str(rec["id"]): rec for rec in projection_harnesses if isinstance(rec, dict) and rec.get("id")}
    role_document = {"harnesses": harnesses}
    active_ids = tuple(
        sorted(
            harness_id
            for harness_id, record in harnesses.items()
            if isinstance(record, dict) and record.get("status") == "active"
        )
    )
    if not active_ids:
        raise RolePartitionViolation("role map must include at least one active harness")

    inactive_with_roles: list[str] = []
    for harness_id, record in sorted(harnesses.items()):
        if not isinstance(record, dict) or record.get("status") == "active":
            continue
        tokens = _role_tokens(record.get("role"))
        if tokens:
            inactive_with_roles.append(f"{harness_id}={sorted(tokens)}")
    if inactive_with_roles:
        raise RolePartitionViolation(
            "inactive harnesses must not carry operating roles; violations: " + ", ".join(inactive_with_roles)
        )

    primes = prime_builder_ids(role_document)
    if len(primes) != 1:
        raise RolePartitionViolation(
            f"active role map must hold exactly one prime-builder; found {len(primes)}: {primes if primes else '[]'}"
        )
    prime_id = primes[0]

    los = loyal_opposition_ids(role_document)
    if len(los) != 1:
        raise RolePartitionViolation(
            f"active role map must hold exactly one loyal-opposition; found {len(los)}: {los if los else '[]'}"
        )
    lo_id = los[0]
    if len(active_ids) > 1 and lo_id == prime_id:
        raise RolePartitionViolation(
            "prime-builder and loyal-opposition must be assigned to different "
            "active harnesses when more than one active harness exists"
        )
    return RolePartitionSummary(
        prime_builder_id=prime_id,
        loyal_opposition_id=lo_id,
        active_harness_ids=active_ids,
    )


def verify_role_partition(project_root: Path, *, role_path: Path | None = None) -> str:
    """Backward-compatible wrapper returning the verified Prime Builder id."""
    return verify_active_role_partition(project_root, role_path=role_path).prime_builder_id
