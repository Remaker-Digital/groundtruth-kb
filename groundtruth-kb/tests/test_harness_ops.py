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
        reviewer_precedence=2,
        invocation_surfaces={"interactive": "antigravity", "headless": "gemini -p"},
        capabilities_ref="infrastructure/antigravity/installed.json",
    )
    assert record["harness_name"] == "antigravity"
    assert record["harness_type"] == "antigravity"
    assert record["reviewer_precedence"] == 2
    assert record["capabilities_ref"] == "infrastructure/antigravity/installed.json"
    assert _decode(record["role"]) == []
    assert _decode(record["invocation_surfaces"]) == {
        "interactive": "antigravity",
        "headless": "gemini -p",
    }


def test_register_rejects_role_assignment(db: Any) -> None:
    with pytest.raises(harness_ops.HarnessOperationError, match="operating-role assignment"):
        _register(db, "B", role=["prime-builder"])


# --- lifecycle transitions --------------------------------------------------


def test_activate_registered_to_active(db: Any) -> None:
    _register(db, "B")
    record = _transition(db, "B", "active", "registered")
    assert record["status"] == "active"
    assert record["version"] == 3


def test_activate_rejects_non_registered(db: Any) -> None:
    _register(db, "B")
    _transition(db, "B", "active", "registered")
    _register(db, "C")
    _transition(db, "C", "active", "registered")
    _transition(db, "B", "suspended", "active")
    # B is suspended; the activate verb expects a registered harness.
    with pytest.raises(harness_ops.HarnessOperationError, match="resume"):
        _transition(db, "B", "active", "registered")


def test_suspend_active_to_suspended(db: Any) -> None:
    _register(db, "B")
    _transition(db, "B", "active", "registered")
    _register(db, "C")
    _transition(db, "C", "active", "registered")
    record = _transition(db, "B", "suspended", "active")
    assert record["status"] == "suspended"


def test_resume_suspended_to_active(db: Any) -> None:
    _register(db, "B")
    _transition(db, "B", "active", "registered")
    _register(db, "C")
    _transition(db, "C", "active", "registered")
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
    _register(db, "C")
    _transition(db, "C", "active", "registered")
    _transition(db, "B", "suspended", "active")
    record = _transition(db, "B", "retired", None)
    assert record["status"] == "retired"


def test_retire_active_auto_suspends_then_retires(db: Any) -> None:
    _register(db, "B")
    _transition(db, "B", "active", "registered")
    _register(db, "C")
    _transition(db, "C", "active", "registered")
    record = _transition(db, "B", "retired", None)
    assert record["status"] == "retired"
    statuses = [x[1] for x in _version_chain(db, "B")]
    assert "registered" in statuses
    assert "active" in statuses
    assert "suspended" in statuses
    assert "retired" in statuses


def test_retire_registered_rejected(db: Any) -> None:
    _register(db, "B")  # registered: the FSM has no retire path from registered
    with pytest.raises(harness_ops.HarnessOperationError):
        _transition(db, "B", "retired", None)


def test_transition_unknown_harness_rejected(db: Any) -> None:
    with pytest.raises(harness_ops.HarnessOperationError, match="unknown harness"):
        _transition(db, "Z", "active", "registered")


def test_transition_carries_forward_fr1_fields(db: Any) -> None:
    _register(db, "B")
    _transition(db, "B", "active", "registered")
    _register(
        db,
        "C",
        harness_name="antigravity",
        harness_type="antigravity",
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
    record = harness_ops.set_harness_precedence(db, "B", 5, changed_by="test", change_reason="bump precedence")
    assert record["reviewer_precedence"] == 5
    assert record["status"] == "active"  # status carries forward unchanged
    assert record["version"] == 4  # v1 register, v2 activate, v3 role reconcile, v4 set-precedence


def test_set_precedence_unknown_harness_rejected(db: Any) -> None:
    with pytest.raises(harness_ops.HarnessOperationError, match="unknown harness"):
        harness_ops.set_harness_precedence(db, "Z", 1, changed_by="test", change_reason="x")


# --- set-invocation-surface -------------------------------------------------


def test_set_invocation_surface_replaces_named_surface_only(db: Any) -> None:
    _register(
        db,
        "A",
        harness_name="codex",
        harness_type="codex-cli",
        reviewer_precedence=4,
        invocation_surfaces={
            "interactive": {"command": "codex"},
            "headless": {"argv": ["codex", "exec", "{{PROMPT}}"]},
        },
    )
    record = harness_ops.set_invocation_surface(
        db,
        "A",
        "headless",
        {"argv": ["codex", "exec", "--model", "gpt-5.5", "{{PROMPT}}"]},
        changed_by="test",
        change_reason="pin headless model",
    )

    surfaces = _decode(record["invocation_surfaces"])
    assert record["status"] == "registered"
    assert record["reviewer_precedence"] == 4
    assert surfaces["interactive"] == {"command": "codex"}
    assert surfaces["headless"]["argv"] == ["codex", "exec", "--model", "gpt-5.5", "{{PROMPT}}"]


def test_set_invocation_surface_unknown_harness_rejected(db: Any) -> None:
    with pytest.raises(harness_ops.HarnessOperationError, match="unknown harness"):
        harness_ops.set_invocation_surface(db, "Z", "headless", {}, changed_by="test", change_reason="x")


# --- set-dispatch-metadata --------------------------------------------------


def test_set_dispatch_metadata_updates_dispatch_surface_only(db: Any) -> None:
    _register(
        db,
        "A",
        harness_name="codex",
        harness_type="codex-cli",
        invocation_surfaces={
            "interactive": {"command": "codex"},
            "headless": {"argv": ["codex", "exec", "{{PROMPT}}"]},
        },
    )

    record = harness_ops.set_dispatch_metadata(
        db,
        "A",
        can_receive_dispatch=True,
        can_fire_events=True,
        dispatch_quality=90,
        dispatch_cost=60,
        dispatch_availability=85.5,
        dispatch_max_items=2,
        dispatch_tags=["prime-builder", "event-source", "prime-builder"],
        changed_by="test",
        change_reason="set dispatch metadata",
    )

    surfaces = _decode(record["invocation_surfaces"])
    assert record["version"] == 2
    assert surfaces["interactive"] == {"command": "codex"}
    assert surfaces["headless"] == {"argv": ["codex", "exec", "{{PROMPT}}"]}
    assert surfaces["dispatch"] == {
        "can_receive_dispatch": True,
        "can_fire_events": True,
        "event_driven_hooks": True,
        "dispatch_quality": 90,
        "dispatch_cost": 60,
        "dispatch_availability": 85.5,
        "dispatch_max_items": 2,
        "dispatch_tags": ["event-source", "prime-builder"],
    }


def test_set_dispatch_metadata_preserves_existing_dispatch_fields(db: Any) -> None:
    _register(
        db,
        "D",
        harness_name="ollama",
        harness_type="ollama",
        invocation_surfaces={
            "dispatch": {
                "can_receive_dispatch": True,
                "dispatch_quality": 92,
                "dispatch_cost": 25,
            }
        },
    )

    record = harness_ops.set_dispatch_metadata(
        db,
        "D",
        can_receive_dispatch=False,
        changed_by="test",
        change_reason="disable dispatch target",
    )

    dispatch = _decode(record["invocation_surfaces"])["dispatch"]
    assert dispatch["can_receive_dispatch"] is False
    assert dispatch["dispatch_quality"] == 92
    assert dispatch["dispatch_cost"] == 25


def test_set_dispatch_metadata_unknown_harness_rejected(db: Any) -> None:
    with pytest.raises(harness_ops.HarnessOperationError, match="unknown harness"):
        harness_ops.set_dispatch_metadata(
            db,
            "Z",
            can_receive_dispatch=True,
            changed_by="test",
            change_reason="x",
        )


def test_set_dispatch_metadata_rejects_invalid_score(db: Any) -> None:
    _register(db, "A", harness_name="codex", harness_type="codex-cli")

    with pytest.raises(harness_ops.HarnessOperationError, match="between 0 and 100"):
        harness_ops.set_dispatch_metadata(
            db,
            "A",
            dispatch_quality=101,
            changed_by="test",
            change_reason="x",
        )
