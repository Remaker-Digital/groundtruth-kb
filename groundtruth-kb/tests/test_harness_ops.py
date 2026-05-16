"""Tests for the harness registry operations module (WI-3340).

Spec-derived tests for ``REQ-HARNESS-REGISTRY-001`` FR3 — the deterministic
transaction discipline behind the ``gt harness`` ``register`` / ``activate`` /
``suspend`` / ``resume`` / ``retire`` / ``set-precedence`` verbs — exercising
the FR2 lifecycle FSM and the FR1 append-only ``harnesses`` table.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import json
from typing import Any

import pytest

from groundtruth_kb import harness_ops


def _decode(value: Any) -> Any:
    """Decode a possibly-JSON-text harness field to a native value."""
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    return value


def _register(db: Any, harness_id: str = "B", **overrides: Any) -> dict[str, Any]:
    """Register a harness with sensible defaults; overrides win."""
    fields: dict[str, Any] = dict(
        id=harness_id,
        harness_name="claude",
        harness_type="claude-code",
        role=["prime-builder"],
        changed_by="test",
        change_reason="test register",
    )
    fields.update(overrides)
    return harness_ops.register_harness(db, **fields)


def _transition(db: Any, harness_id: str, target: str, source: str | None) -> dict[str, Any]:
    """Apply a transition with test-default audit fields."""
    return harness_ops.transition_harness(
        db,
        harness_id,
        target,
        changed_by="test",
        change_reason=f"test {target}",
        expected_source=source,
    )


def _version_chain(db: Any, harness_id: str) -> list[tuple[int, str]]:
    """Return (version, status) for every stored version of a harness, ascending."""
    rows = (
        db._get_conn()
        .execute(
            "SELECT version, status FROM harnesses WHERE id = ? ORDER BY version",
            (harness_id,),
        )
        .fetchall()
    )
    return [(row[0], row[1]) for row in rows]


# --- register --------------------------------------------------------------


def test_register_creates_registered_harness(db: Any) -> None:
    record = _register(db, "B")
    assert record["id"] == "B"
    assert record["status"] == "registered"
    assert record["version"] == 1


def test_register_rejects_duplicate_id(db: Any) -> None:
    _register(db, "B")
    with pytest.raises(harness_ops.HarnessOperationError, match="already registered"):
        _register(db, "B")


def test_register_persists_optional_fields(db: Any) -> None:
    record = _register(
        db,
        "C",
        harness_name="antigravity",
        harness_type="antigravity",
        role=["loyal-opposition"],
        reviewer_precedence=2,
        invocation_surfaces={"interactive": "antigravity", "headless": "gemini -p"},
        capabilities_ref="config/agent-control/harness-capability-registry.toml",
    )
    assert record["harness_name"] == "antigravity"
    assert record["harness_type"] == "antigravity"
    assert record["reviewer_precedence"] == 2
    assert record["capabilities_ref"].endswith("harness-capability-registry.toml")
    assert _decode(record["role"]) == ["loyal-opposition"]
    assert _decode(record["invocation_surfaces"]) == {
        "interactive": "antigravity",
        "headless": "gemini -p",
    }


# --- lifecycle transitions --------------------------------------------------


def test_activate_registered_to_active(db: Any) -> None:
    _register(db, "B")
    record = _transition(db, "B", "active", "registered")
    assert record["status"] == "active"
    assert record["version"] == 2


def test_activate_rejects_non_registered(db: Any) -> None:
    _register(db, "B")
    _transition(db, "B", "active", "registered")
    _transition(db, "B", "suspended", "active")
    # B is suspended; the activate verb expects a registered harness.
    with pytest.raises(harness_ops.HarnessOperationError, match="resume"):
        _transition(db, "B", "active", "registered")


def test_suspend_active_to_suspended(db: Any) -> None:
    _register(db, "B")
    _transition(db, "B", "active", "registered")
    record = _transition(db, "B", "suspended", "active")
    assert record["status"] == "suspended"


def test_resume_suspended_to_active(db: Any) -> None:
    _register(db, "B")
    _transition(db, "B", "active", "registered")
    _transition(db, "B", "suspended", "active")
    record = _transition(db, "B", "active", "suspended")
    assert record["status"] == "active"


def test_resume_rejects_non_suspended(db: Any) -> None:
    _register(db, "B")  # status registered
    # The resume verb expects a suspended harness.
    with pytest.raises(harness_ops.HarnessOperationError, match="activate"):
        _transition(db, "B", "active", "suspended")


def test_retire_suspended_to_retired(db: Any) -> None:
    _register(db, "B")
    _transition(db, "B", "active", "registered")
    _transition(db, "B", "suspended", "active")
    record = _transition(db, "B", "retired", None)
    assert record["status"] == "retired"


def test_retire_active_auto_suspends_then_retires(db: Any) -> None:
    _register(db, "B")
    _transition(db, "B", "active", "registered")
    record = _transition(db, "B", "retired", None)
    assert record["status"] == "retired"
    # Owner AskUserQuestion 2026-05-16: active -> suspended -> retired. The
    # version chain proves the intermediate suspended version exists.
    assert _version_chain(db, "B") == [
        (1, "registered"),
        (2, "active"),
        (3, "suspended"),
        (4, "retired"),
    ]


def test_retire_registered_rejected(db: Any) -> None:
    _register(db, "B")  # registered: the FSM has no retire path from registered
    with pytest.raises(harness_ops.HarnessOperationError):
        _transition(db, "B", "retired", None)


def test_transition_unknown_harness_rejected(db: Any) -> None:
    with pytest.raises(harness_ops.HarnessOperationError, match="unknown harness"):
        _transition(db, "Z", "active", "registered")


def test_transition_carries_forward_fr1_fields(db: Any) -> None:
    _register(
        db,
        "C",
        harness_name="antigravity",
        harness_type="antigravity",
        role=["loyal-opposition"],
        reviewer_precedence=3,
        invocation_surfaces={"headless": "gemini -p"},
        capabilities_ref="caps.toml",
    )
    record = _transition(db, "C", "active", "registered")
    assert record["status"] == "active"
    assert record["harness_name"] == "antigravity"
    assert record["harness_type"] == "antigravity"
    assert record["reviewer_precedence"] == 3
    assert record["capabilities_ref"] == "caps.toml"
    assert _decode(record["role"]) == ["loyal-opposition"]
    assert _decode(record["invocation_surfaces"]) == {"headless": "gemini -p"}


# --- set-precedence ---------------------------------------------------------


def test_set_precedence_appends_version_unchanged_status(db: Any) -> None:
    _register(db, "B", reviewer_precedence=1)
    _transition(db, "B", "active", "registered")
    record = harness_ops.set_harness_precedence(
        db, "B", 5, changed_by="test", change_reason="bump precedence"
    )
    assert record["reviewer_precedence"] == 5
    assert record["status"] == "active"  # status carries forward unchanged
    assert record["version"] == 3  # v1 register, v2 activate, v3 set-precedence


def test_set_precedence_unknown_harness_rejected(db: Any) -> None:
    with pytest.raises(harness_ops.HarnessOperationError, match="unknown harness"):
        harness_ops.set_harness_precedence(
            db, "Z", 1, changed_by="test", change_reason="x"
        )
