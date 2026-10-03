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


def test_harness_parity_skill_separates_derivation_installed_output_and_execution() -> None:
    skill_text = " ".join(
        _read_text(".harness-baseline-configuration/skills/gtkb-harness-parity-review/SKILL.md").split()
    )

    assert "The reviewed sources can produce the required configuration" in skill_text
    assert "The selected installed configuration agrees with those sources" in skill_text
    assert "Real fresh-context execution invokes the required hooks and native CLI paths" in skill_text
    assert "A clean render does not prove invocation, delivery or effect containment" in skill_text
    assert "gt harness diagnostic --harness-id <ID> --json" in skill_text
