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
    "cursor": "E",
    "openrouter": "F",
    "goose": "G",
    "alibaba-cloud-studio": "H",
}
VALID_ROLES = {"prime-builder", "loyal-opposition"}
VALID_STATUSES = {"active", "suspended", "retired"}
EXPECTED_EVENT_SOURCES: set[str] = set()
EXPECTED_RULE_HARNESS_IDS = {"A", "B", "C", "D", "E", "F", "H"}


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
    suspended_or_retired_rows = []
    for harness_name, harness_id in EXPECTED_IDENTITIES.items():
        row = registry_by_id[harness_id]
        assert row["harness_name"] == harness_name
        assert row["status"] in VALID_STATUSES
        assert set(row["role"]).issubset(VALID_ROLES)
        assert row["dispatch_tags"]
        assert "headless" in row["invocation_surfaces"]

        if row["status"] == "active":
            active_rows.append(row)
            assert row["role"]
            assert isinstance(row["can_receive_dispatch"], bool)
        else:
            suspended_or_retired_rows.append(row)
            assert row["can_fire_events"] is False
            assert row["can_receive_dispatch"] is False

    assert any("prime-builder" in row["role"] for row in active_rows)
    assert any("loyal-opposition" in row["role"] for row in active_rows)
    assert all(row["status"] in {"suspended", "retired"} for row in suspended_or_retired_rows)

    assert {row["id"] for row in registry["harnesses"] if row["can_fire_events"]} == EXPECTED_EVENT_SOURCES
    dispatch_targets = [row for row in registry["harnesses"] if row["can_receive_dispatch"]]
    assert dispatch_targets
    assert all(row["status"] == "active" for row in dispatch_targets)
    assert any("prime-builder" in row["role"] for row in dispatch_targets)
    assert any("loyal-opposition" in row["role"] for row in dispatch_targets)
    assert any("low-cost" in row["dispatch_tags"] for row in dispatch_targets)
    for harness_id, row in registry_by_id.items():
        assert row["event_driven_hooks"] is (harness_id in EXPECTED_EVENT_SOURCES)


def test_dispatcher_status_rules_match_prime_and_lo_bridge_boundaries() -> None:
    rules_config = _read_toml("config/dispatcher/rules.toml")

    harness_ids = set(rules_config["harnesses"])
    assert EXPECTED_RULE_HARNESS_IDS.issubset(harness_ids)

    rule_by_id = {rule["id"]: rule for rule in rules_config["rules"]}
    prime_rule = rule_by_id["bridge-prime-builder-default"]
    lo_rule = rule_by_id["bridge-loyal-opposition-cheap-fast-default"]

    assert prime_rule["required_roles"] == ["prime-builder"]
    assert prime_rule["statuses"] == ["GO", "NO-GO"]
    assert lo_rule["required_roles"] == ["loyal-opposition"]
    assert lo_rule["statuses"] == ["NEW", "REVISED", "NO-ACTION"]

    protocol = _read_text(".claude/rules/file-bridge-protocol.md")
    disposition = _read_text("groundtruth-kb/src/groundtruth_kb/bridge/disposition.py")
    assert "GO, NO-GO, or ADVISORY" in protocol
    assert "NEW, REVISED, or NO-ACTION entries" in protocol
    assert 'STATUS_NO_ACTION: Final[str] = "NO-ACTION"' in disposition
    assert "LOYAL_OPPOSITION_ACTIONABLE_STATUSES" in disposition
    assert (
        "ADVISORY entries are Prime-actionable for interactive sessions and non-dispatchable for headless runs"
        in protocol
    )

    for relative_path in (
        "AGENTS.md",
        "CLAUDE.md",
        "config/agent-control/LOYAL-OPPOSITION-STARTUP-OVERLAY.md",
        ".claude/rules/codex-standing-priorities.md",
        ".claude/rules/codex-review-operating-contract.md",
        ".claude/rules/codex-loyal-opposition-runbook.md",
        ".claude/rules/prime-bridge-collaboration-protocol.md",
        ".claude/skills/gtkb-bridge/SKILL.md",
        ".codex/skills/gtkb-bridge/SKILL.md",
        ".agent/skills/gtkb-bridge/SKILL.md",
        ".api-harness/skills/gtkb-bridge/SKILL.md",
        "scripts/dispatcher_runtime.py",
        "scripts/ollama_harness.py",
        "scripts/openrouter_harness.py",
    ):
        assert "NO-ACTION" in _read_text(relative_path), relative_path


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

    assert "--batch pretooluse-bash" in codex_hooks
    assert "--batch pretooluse-apply-patch" in codex_hooks
    assert "bridge-compliance-gate.cmd" in _read_text(".codex/gtkb-hooks/run_py_no_window.py")
    assert "implementation-start-gate.cmd" in _read_text(".codex/gtkb-hooks/run_py_no_window.py")
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
    for skill_name in ("gtkb-bridge", "gtkb-bridge-propose", "gtkb-harness-parity-review", "gtkb-verify"):
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


def test_harness_parity_skill_separates_catalog_operational_and_hook_scope() -> None:
    skill_text = _read_text(".claude/skills/gtkb-harness-parity-review/SKILL.md")

    assert "phase-1 catalog parity" in skill_text
    assert "phase-2 operational readiness" in skill_text
    assert "Discovery-diff applies only where a" in skill_text
    assert "API/provider harness readiness must" in skill_text
    assert "python scripts/parity_discovery_diff.py --project-root . --markdown" in skill_text


def test_hook_fallback_surfaces_distinguish_event_sources_from_dispatch_targets() -> None:
    registry = _read_json("harness-state/harness-registry.json")
    codex_hooks = _read_text(".codex/hooks.json")
    claude_settings = _read_text(".claude/settings.json")

    by_id = {row["id"]: row for row in registry["harnesses"]}
    event_sources = {row["id"] for row in registry["harnesses"] if row["can_fire_events"]}
    dispatch_only = {row["id"] for row in registry["harnesses"] if not row["can_fire_events"]}
    dispatch_targets = {row["id"] for row in registry["harnesses"] if row["can_receive_dispatch"]}

    assert event_sources == EXPECTED_EVENT_SOURCES
    assert dispatch_only == set(EXPECTED_IDENTITIES.values())
    assert dispatch_targets
    assert all(by_id[harness_id]["status"] == "active" for harness_id in dispatch_targets)
    assert any("prime-builder" in by_id[harness_id]["role"] for harness_id in dispatch_targets)
    assert any("loyal-opposition" in by_id[harness_id]["role"] for harness_id in dispatch_targets)
    assert any("low-cost" in by_id[harness_id]["dispatch_tags"] for harness_id in dispatch_targets)
    inactive_targets = {
        harness_id for harness_id in EXPECTED_IDENTITIES.values() if not by_id[harness_id]["can_receive_dispatch"]
    }
    assert inactive_targets == set(EXPECTED_IDENTITIES.values()) - dispatch_targets

    forbidden_hook_dispatch = (
        "cross_" + "harness_" + "bridge_" + "trigger.py",
        "single_harness_bridge_automation.py",
        "single_harness_bridge_dispatcher.py",
        "bridge-dispatch-trigger",
        "dispatcher-daemon.cmd",
        "gtkb_dispatcher_daemon.py",
    )
    for hook_config in (codex_hooks, claude_settings):
        assert not any(token in hook_config for token in forbidden_hook_dispatch)
