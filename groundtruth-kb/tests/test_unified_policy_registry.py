"""Tests for the WI-4551 unified policy-registry inventory layer."""

from __future__ import annotations

import inspect
from pathlib import Path

import pytest

import groundtruth_kb.policy.registry as unified_registry
from groundtruth_kb.policy.engine import load_policy_registry
from groundtruth_kb.policy.registry import load_unified_policy_registry


def test_unified_policy_registry_parses_inventory() -> None:
    registry = load_unified_policy_registry()

    assert registry.schema_version == 1
    assert registry.registry_id == "gtkb-unified-policy-registry"
    assert registry.registry_hash.startswith("sha256:")
    assert set(registry.actions_by_class) >= {
        "status",
        "test",
        "build",
        "deploy-staging",
        "deploy-production",
        "requirements-update",
        "commit",
        "push",
        "platform-write",
        "bridge-compliance-write",
        "implementation-start",
        "scanner-safe-write",
        "narrative-artifact-write",
        "sot-read-discipline",
        "owner-decision-tracking",
    }
    assert registry.actions_by_class["status"].enforcement_status == "engine_backed"
    assert registry.actions_by_class["bridge-compliance-write"].enforcement_status == "external_gate"
    assert registry.actions_by_class["bridge-compliance-write"].adapter_installed is True


def test_unified_registry_can_feed_policy_engine_action_metadata() -> None:
    auq_registry = load_policy_registry()
    unified = load_unified_policy_registry()

    for action_class in auq_registry.actions:
        action = unified.actions_by_class[action_class]
        assert action.enforcement_status == "engine_backed"
        assert action.decision_source == "groundtruth_kb.policy.engine"
        assert action.outcome == auq_registry.actions[action_class].outcome


def test_unified_registry_rejects_duplicate_action_classes(tmp_path: Path) -> None:
    registry = tmp_path / "registry.toml"
    registry.write_text(
        """
schema_version = 1
registry_id = "duplicate"

[actions.one]
action_class = "same"
outcome = "ALLOW"
message = "one"
enforcement_status = "inventory_only"
decision_source = "fixture"
adapter_installed = false
adapter_surfaces = ["fixture"]
harnesses = ["all"]

[actions.two]
action_class = "same"
outcome = "WARN"
message = "two"
enforcement_status = "inventory_only"
decision_source = "fixture"
adapter_installed = false
adapter_surfaces = ["fixture"]
harnesses = ["all"]
""",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="duplicate action_class"):
        load_unified_policy_registry(registry)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("outcome", "MAYBE", "invalid outcome"),
        ("enforcement_status", "migrated-ish", "invalid enforcement_status"),
    ],
)
def test_unified_registry_rejects_invalid_tokens(
    tmp_path: Path,
    field: str,
    value: str,
    message: str,
) -> None:
    registry = tmp_path / "registry.toml"
    registry_text = """
schema_version = 1
registry_id = "bad-token"

[actions.one]
action_class = "one"
outcome = "ALLOW"
message = "one"
enforcement_status = "inventory_only"
decision_source = "fixture"
adapter_installed = false
adapter_surfaces = ["fixture"]
harnesses = ["all"]
"""
    original_line = f'{field} = "ALLOW"' if field == "outcome" else f'{field} = "inventory_only"'
    registry.write_text(
        registry_text.replace(original_line, f'{field} = "{value}"'),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match=message):
        load_unified_policy_registry(registry)


def test_registry_inventory_includes_codex_and_claude_governance_surfaces() -> None:
    registry = load_unified_policy_registry()

    bridge = registry.actions_by_class["bridge-compliance-write"]
    assert "claude" in bridge.harnesses
    assert "codex-helper-audit" in bridge.harnesses
    assert any("bridge-compliance-gate.py" in surface for surface in bridge.adapter_surfaces)


def test_registry_allows_per_harness_adapter_availability() -> None:
    registry = load_unified_policy_registry()

    narrative = registry.actions_by_class["narrative-artifact-write"]
    assert narrative.harnesses == ("claude", "pre-commit-floor")
    assert narrative.enforcement_status == "external_gate"


def test_unified_policy_registry_has_no_llm_network_or_subprocess_dependency() -> None:
    source = inspect.getsource(unified_registry).lower()

    for forbidden in ("openai", "anthropic", "requests", "urllib", "socket", "subprocess", "api_key"):
        assert forbidden not in source


def test_unified_policy_registry_rejects_archive_path(tmp_path: Path) -> None:
    archive_dir = tmp_path / "Claude-Playground"
    archive_dir.mkdir()
    registry = archive_dir / "registry.toml"
    registry.write_text('schema_version = 1\nregistry_id = "archive"\n', encoding="utf-8")

    with pytest.raises(ValueError, match="archive path"):
        load_unified_policy_registry(registry)
