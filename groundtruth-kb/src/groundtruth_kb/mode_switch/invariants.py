"""Role-map partition checks for the operating-mode subsystem.

``REQ-HARNESS-REGISTRY-001`` FR9 requires that ``gt harness set-role`` leave
the role map as a full role partition: exactly one harness holds
``prime-builder`` and every other harness holds ``loyal-opposition``. This
module is the postcondition check for that property. ``apply_role_switch``
(``mode_switch/transaction.py``) produces the partition inside the transaction;
``verify_role_partition`` confirms it afterward.

It is pure standard-library logic: it reads
``harness-state/role-assignments.json`` and computes over the role-set wire
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
from pathlib import Path
from typing import Any

# Role tokens that count as holding the prime-builder role. The legacy
# ``acting-prime-builder`` provenance token is READ-accepted per
# ``GOV-ACTING-PRIME-BUILDER-001``; it counts toward the single-prime-builder
# invariant so a stale provenance value cannot mask a second prime-class
# harness.
_PRIME_BUILDER_TOKENS = frozenset({"prime-builder", "acting-prime-builder"})


class RolePartitionViolation(RuntimeError):
    """Raised when the role map is not a valid FR9 role partition.

    A valid partition has exactly one harness in a prime-builder-class role and
    every other harness in exactly ``["loyal-opposition"]``. The message names
    the offending condition and the harness ids involved.
    """


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
        and _PRIME_BUILDER_TOKENS & _role_tokens(record.get("role"))
    )


def verify_role_partition(project_root: Path, *, role_path: Path | None = None) -> str:
    """Verify the role map is a valid ``REQ-HARNESS-REGISTRY-001`` FR9 partition.

    Loads ``harness-state/role-assignments.json`` under ``project_root`` (or
    ``role_path`` when given) and raises ``RolePartitionViolation`` unless
    exactly one harness holds a prime-builder-class role and every other
    harness's role set is exactly ``{"loyal-opposition"}``. Returns the single
    ``prime-builder`` harness id on success.
    """
    path = (
        role_path
        if role_path is not None
        else Path(project_root) / "harness-state" / "role-assignments.json"
    )
    role_document = json.loads(Path(path).read_text(encoding="utf-8"))
    harnesses = role_document.get("harnesses", {})
    if not isinstance(harnesses, dict):
        raise RolePartitionViolation(f"role map at {path} has no 'harnesses' object")
    primes = prime_builder_ids(role_document)
    if len(primes) != 1:
        raise RolePartitionViolation(
            f"role map must hold exactly one prime-builder; found "
            f"{len(primes)}: {primes if primes else '[]'}"
        )
    prime_id = primes[0]
    violations: list[str] = []
    for harness_id, record in sorted(harnesses.items()):
        if harness_id == prime_id or not isinstance(record, dict):
            continue
        tokens = _role_tokens(record.get("role"))
        if tokens != {"loyal-opposition"}:
            violations.append(f"{harness_id}={sorted(tokens)}")
    if violations:
        raise RolePartitionViolation(
            "every non-prime-builder harness must hold exactly "
            "['loyal-opposition']; violations: " + ", ".join(violations)
        )
    return prime_id
