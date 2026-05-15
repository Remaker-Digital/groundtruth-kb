"""Tests for ``groundtruth_kb.mode_switch.derive.role_slot_from_active_harness``.

Per the GO of ``bridge/gtkb-startup-payload-canonical-state-drift-004.md`` IP-2 +
IP-3 scope. Each test maps to a Specification Link cited in
``bridge/gtkb-startup-payload-canonical-state-drift-003.md`` Specification-Derived
Verification Plan.

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from groundtruth_kb.mode_switch.derive import role_slot_from_active_harness


def test_role_slot_singleton_prime() -> None:
    """Singleton ``["prime-builder"]`` role-set returns ``prime-builder``."""
    role_map = {
        "harnesses": {
            "B": {"role": ["prime-builder"]},
        }
    }
    assert role_slot_from_active_harness(role_map, "B") == "prime-builder"


def test_role_slot_singleton_lo() -> None:
    """Singleton ``["loyal-opposition"]`` role-set returns ``loyal-opposition``."""
    role_map = {
        "harnesses": {
            "A": {"role": ["loyal-opposition"]},
        }
    }
    assert role_slot_from_active_harness(role_map, "A") == "loyal-opposition"


def test_role_slot_multi_element_returns_shared() -> None:
    """Multi-element role-set (single-harness operating mode) returns ``shared``."""
    role_map = {
        "harnesses": {
            "A": {"role": ["prime-builder", "loyal-opposition"]},
        }
    }
    assert role_slot_from_active_harness(role_map, "A") == "shared"


def test_role_slot_missing_harness_returns_shared() -> None:
    """Active harness ID not present in the map fail-safes to ``shared``."""
    role_map = {
        "harnesses": {
            "A": {"role": ["loyal-opposition"]},
        }
    }
    assert role_slot_from_active_harness(role_map, "C") == "shared"


def test_role_slot_legacy_scalar_role() -> None:
    """Legacy scalar ``"role": "prime-builder"`` is coerced via ``_role_set``."""
    role_map = {"harnesses": {"B": {"role": "prime-builder"}}}
    assert role_slot_from_active_harness(role_map, "B") == "prime-builder"


def test_role_slot_acting_prime_builder_coercion() -> None:
    """``acting-prime-builder`` is READ-coerced to ``prime-builder`` per GOV-ACTING-PRIME-BUILDER-001."""
    role_map = {
        "harnesses": {
            "B": {"role": ["acting-prime-builder"]},
        }
    }
    assert role_slot_from_active_harness(role_map, "B") == "prime-builder"


def test_role_slot_empty_role_map_returns_shared() -> None:
    """Empty / malformed role map fail-safes to ``shared``."""
    assert role_slot_from_active_harness({}, "B") == "shared"
    assert role_slot_from_active_harness({"harnesses": {}}, "B") == "shared"
    assert role_slot_from_active_harness({"harnesses": None}, "B") == "shared"  # type: ignore[arg-type]


def test_role_slot_none_active_harness_returns_shared() -> None:
    """``active_harness_id=None`` fail-safes to ``shared``."""
    role_map = {
        "harnesses": {
            "B": {"role": ["prime-builder"]},
        }
    }
    assert role_slot_from_active_harness(role_map, None) == "shared"
