"""Pure topology derivation from a role map.

Per ``SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001``. Mirrors the existing
applicability logic at
``scripts/single_harness_bridge_dispatcher._is_single_harness_topology_applicable``
so that dispatcher and startup compute identical results.

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights
reserved.
"""

from __future__ import annotations

from typing import Any

SINGLE_HARNESS = "single_harness"
MULTI_HARNESS = "multi_harness"

SHARED = "shared"

_PRIME = "prime-builder"
_LO = "loyal-opposition"


def _role_set(record: Any) -> frozenset[str]:
    """Normalize a role-map record into a role-set.

    Accepts both the canonical list form (``"role": ["prime-builder",
    "loyal-opposition"]``) and the legacy scalar form (``"role":
    "prime-builder"``). Legacy ``"acting-prime-builder"`` is READ-accepted
    and treated as ``"prime-builder"`` for topology purposes per
    ``GOV-ACTING-PRIME-BUILDER-001``.
    """
    if not isinstance(record, dict):
        return frozenset()
    role = record.get("role")
    if isinstance(role, list):
        tokens = {str(item).strip() for item in role if str(item).strip()}
    elif isinstance(role, str) and role.strip():
        tokens = {role.strip()}
    else:
        return frozenset()
    if "acting-prime-builder" in tokens:
        tokens.discard("acting-prime-builder")
        tokens.add(_PRIME)
    return frozenset(tokens)


def topology_from_role_map(role_map: dict[str, Any]) -> str:
    """Return ``single_harness`` or ``multi_harness`` for the given role map.

    Single-harness iff exactly one harness ID's role-set contains BOTH
    ``prime-builder`` AND ``loyal-opposition``. All other shapes return
    ``multi_harness`` (including empty/malformed maps; the dispatcher's
    fail-closed semantics for ambiguous input is preserved by returning the
    multi-harness default, which makes the cross-harness trigger the active
    substrate).
    """
    if not isinstance(role_map, dict):
        return MULTI_HARNESS
    harnesses = role_map.get("harnesses")
    if not isinstance(harnesses, dict):
        return MULTI_HARNESS
    if len(harnesses) != 1:
        return MULTI_HARNESS
    only_record = next(iter(harnesses.values()))
    roles = _role_set(only_record)
    if _PRIME in roles and _LO in roles:
        return SINGLE_HARNESS
    return MULTI_HARNESS


def role_slot_from_active_harness(
    role_map: dict[str, Any],
    active_harness_id: str | None,
) -> str:
    """Return the role-slot label for the active harness.

    Returns ``prime-builder`` or ``loyal-opposition`` for a singleton
    role-set, ``shared`` for a multi-element role-set, and ``shared``
    fail-safe for missing/malformed/unresolved input. Reuses
    ``_role_set`` so legacy scalar role values and the
    ``acting-prime-builder`` coercion are handled identically to the
    topology helper.
    """
    if not isinstance(role_map, dict) or not active_harness_id:
        return SHARED
    harnesses = role_map.get("harnesses")
    if not isinstance(harnesses, dict):
        return SHARED
    record = harnesses.get(active_harness_id)
    roles = _role_set(record)
    if not roles:
        return SHARED
    if len(roles) == 1:
        return next(iter(roles))
    return SHARED
