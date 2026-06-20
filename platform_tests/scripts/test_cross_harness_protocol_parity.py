"""Read-only cross-harness protocol parity checks.

These tests inspect durable GT-KB harness, dispatcher, hook, and capability
surfaces. They do not execute hooks, spawn harnesses, mutate bridge state, or
touch external services.
"""

from __future__ import annotations

import json
import tomllib
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXPECTED_IDENTITIES = {
    "codex": "A",
    "claude": "B",
    "antigravity": "C",
    "ollama": "D",
    "openrouter": "F",
}
VALID_ROLES = {"prime-builder", "loyal-opposition"}
VALID_STATUSES = {"active", "suspended"}


def _read_json(relative_path: str) -> dict[str, Any]:
    return json.loads((PROJECT_ROOT / relative_path).read_text(encoding="utf-8"))


def _read_toml(relative_path: str) -> dict[str, Any]:
    return tomllib.loads((PROJECT_ROOT / relative_path).read_text(encoding="utf-8"))


def _read_text(relative_path: str) -> str:
    return (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")


def test_durable_harness_identity_and_role_surfaces_cover_expected_harnesses() -> None:
    identities = _read_json("harness-state/harness-identities.json")
    registry = _read_json("harness-state/harness-registry.json")

    identity_rows = identities["harnesses"]
    assert {name: identity_rows[name]["id"] for name in EXPECTED_IDENTITIES} == EXPECTED_IDENTITIES

    registry_by_id = {row["id"]: row for row in registry["harnesses"]}
    assert set(EXPECTED_IDENTITIES.values()).issubset(registry_by_id)

    active_rows = []
    suspended_rows = []
    for harness_name, harness_id in EXPECTED_IDENTITIES.items():
        row = registry_by_id[harness_id]
        assert row["harness_name"] == harness_name
        assert row["status"] in VALID_STATUSES
        assert set(row["role"]).issubset(VALID_ROLES)
        assert row["can_receive_dispatch"] is True
        assert row["dispatch_tags"]
        assert "headless" in row["invocation_surfaces"]

        if row["status"] == "active":
            active_rows.append(row)
            assert row["role"]
        else:
            suspended_rows.append(row)
            assert row["can_fire_events"] is False

    assert any("prime-builder" in row["role"] for row in active_rows)
    assert any("loyal-opposition" in row["role"] for row in active_rows)
    assert all(row["status"] == "suspended" for row in suspended_rows)

    assert registry_by_id["A"]["event_driven_hooks"] is True
    assert registry_by_id["B"]["event_driven_hooks"] is True
    assert registry_by_id["C"]["event_driven_hooks"] is False
    assert registry_by_id["D"]["event_driven_hooks"] is False
    assert registry_by_id["F"]["event_driven_hooks"] is False


def test_dispatcher_status_rules_match_prime_and_lo_bridge_boundaries() -> None:
    rules_config = _read_toml("config/dispatcher/rules.toml")

    harness_ids = set(rules_config["harnesses"])
    assert set(EXPECTED_IDENTITIES.values()).issubset(harness_ids)

    rule_by_id = {rule["id"]: rule for rule in rules_config["rules"]}
    prime_rule = rule_by_id["bridge-prime-builder-default"]
    lo_rule = rule_by_id["bridge-loyal-opposition-cheap-fast-default"]

    assert prime_rule["required_roles"] == ["prime-builder"]
    assert prime_rule["statuses"] == ["GO", "NO-GO"]
    assert lo_rule["required_roles"] == ["loyal-opposition"]
    assert lo_rule["statuses"] == ["NEW", "REVISED"]

    protocol = _read_text(".claude/rules/file-bridge-protocol.md")
    assert "GO, NO-GO, or ADVISORY" in protocol
    assert "NEW or REVISED entries" in protocol
    assert (
        "ADVISORY entries are Prime-actionable for interactive sessions and non-dispatchable for headless runs"
        in protocol
    )


def test_protected_mutation_surfaces_expose_go_packet_and_claim_requirements() -> None:
    review_gate = _read_text(".claude/rules/codex-review-gate.md")
    bridge_protocol = _read_text(".claude/rules/file-bridge-protocol.md")
    protected_guard = _read_text("scripts/protected_mutation_guard.py")
    codex_hooks = _read_text(".codex/hooks.json")
    claude_settings = _read_text(".claude/settings.json")

    for needle in (
        "current local authorization packet",
        "implementation_authorization.py begin",
        "Loyal Opposition GO status",
    ):
        assert needle in review_gate

    assert "work-intent claim" in bridge_protocol
    assert "bridge_claim_cli.py claim" in bridge_protocol

    for needle in ("missing_bridge_go", "missing_implementation_packet", "missing_or_stale_claim"):
        assert needle in protected_guard

    assert "implementation-start-gate" in codex_hooks
    assert "bridge-compliance-gate" in codex_hooks
    assert "implementation-start-gate.py" in claude_settings
    assert "bridge-compliance-gate.py" in claude_settings


def test_owner_action_visibility_contract_is_present_for_blocking_decisions() -> None:
    ag_contract = _read_text("AGENTS.md")
    prime_role = _read_text(".claude/rules/prime-builder-role.md")
    claude_settings = _read_text(".claude/settings.json")

    assert "OWNER ACTION REQUIRED" in ag_contract
    assert "AskUserQuestion as the Only Valid Owner-Decision Channel" in prime_role
    assert "owner-decision-tracker.py" in claude_settings


def test_capability_registry_tracks_shared_skill_and_low_cost_harness_floors() -> None:
    capability_registry = _read_toml("config/agent-control/harness-capability-registry.toml")

    capability_by_name = {row["canonical_name"]: row for row in capability_registry["capabilities"]}
    for skill_name in ("gtkb-bridge", "gtkb-bridge-propose", "harness-parity-review", "gtkb-verify"):
        row = capability_by_name[skill_name]
        assert row["claude"]["status"] == "native"
        assert row["codex"]["status"] == "adapter"
        assert row["antigravity"]["status"] == "adapter"

    for harness_name in ("ollama", "openrouter"):
        harness_floor = capability_registry["harnesses"][harness_name]
        assert harness_floor["bridge_compliance_gate_respect"] is True
        assert harness_floor["root_boundary_respect"] is True
        assert harness_floor["author_metadata_env_var_setting"] is True
        assert harness_floor["tool_guard_adapter_fail_closed"] is True
        assert set(harness_floor["advertised_tool_subset"]) == {"Read", "Write", "Edit", "Grep", "Glob", "Bash"}


def test_hook_fallback_surfaces_distinguish_event_sources_from_dispatch_targets() -> None:
    registry = _read_json("harness-state/harness-registry.json")
    codex_hooks = _read_text(".codex/hooks.json")
    claude_settings = _read_text(".claude/settings.json")

    by_id = {row["id"]: row for row in registry["harnesses"]}
    event_sources = {row["id"] for row in registry["harnesses"] if row["can_fire_events"]}
    dispatch_only = {row["id"] for row in registry["harnesses"] if not row["can_fire_events"]}

    assert event_sources == {"A", "B"}
    assert dispatch_only == {"C", "D", "F"}
    assert all(by_id[harness_id]["can_receive_dispatch"] for harness_id in EXPECTED_IDENTITIES.values())

    assert "cross_harness_bridge_trigger.py" in codex_hooks
    assert "single_harness_bridge_automation.py" in codex_hooks
    assert "cross_harness_bridge_trigger.py" in claude_settings
    assert "single_harness_bridge_automation.py" in claude_settings
