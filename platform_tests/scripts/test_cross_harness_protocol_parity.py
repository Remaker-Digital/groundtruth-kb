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


def test_owner_action_visibility_contract_is_present_for_blocking_decisions() -> None:
    ag_contract = _read_text("AGENTS.md")
    prime_role = _read_text(".claude/rules/prime-builder-role.md")
    claude_settings = _read_text(".claude/settings.json")

    assert "OWNER ACTION REQUIRED" in ag_contract
    assert "AskUserQuestion as the Only Valid Owner-Decision Channel" in prime_role
    assert "owner-decision-tracker.py" in claude_settings


def test_harness_parity_skill_separates_catalog_operational_and_hook_scope() -> None:
    skill_text = _read_text(".claude/skills/gtkb-harness-parity-review/SKILL.md")

    assert "phase-1 catalog parity" in skill_text
    assert "phase-2 operational readiness" in skill_text
    assert "Discovery-diff applies only where a" in skill_text
    assert "API/provider harness readiness must" in skill_text
    assert "python scripts/parity_discovery_diff.py --project-root . --markdown" in skill_text
