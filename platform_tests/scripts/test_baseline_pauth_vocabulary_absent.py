"""Regression coverage for retired authorization-carrier vocabulary (WI-7702)."""

from __future__ import annotations

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SCANNED_TARGETS = (
    ".harness-baseline-configuration/skills/gtkb-bridge-propose/SKILL.md",
    ".harness-baseline-configuration/skills/gtkb-bridge/SKILL.md",
    ".harness-baseline-configuration/skills/gtkb-lo-hygiene-assessment/SKILL.md",
    ".harness-baseline-configuration/skills/gtkb-managed-skill-adoption-review/SKILL.md",
    ".harness-baseline-configuration/skills/gtkb-projects/SKILL.md",
    ".harness-baseline-configuration/skills/gtkb-propose/SKILL.md",
    ".harness-baseline-configuration/rules/backlog-approval-state.md",
    "config/governance/hygiene-baseline-registry.toml",
    "config/governance/neutral-source-inventory.toml",
    "config/governance/protected-artifact-inventory-drift.toml",
    "config/membase-dump/dump-policy.toml",
    "config/registry/sot-artifacts.toml",
)

GENERATED_OUTPUT = "config/agent-control/gtkb-backlog-approval-state.md"
BASELINE_INPUT = ".harness-baseline-configuration/rules/backlog-approval-state.md"
COMMAND_SURFACE_EXCLUSIONS = (
    "config/agent-control/command-surface.toml",
    "config/agent-control/gtkb-command-surface.toml",
)

RETIRED_PATTERNS = {
    "pauth_identifier": re.compile(r"\bPAUTH(?:-[A-Z0-9][A-Z0-9-]*)?\b", re.IGNORECASE),
    "authorization_table": re.compile(r"\bproject_authorizations\b", re.IGNORECASE),
    "authorization_header": re.compile(r"^\s*Project Authorization\s*:", re.IGNORECASE | re.MULTILINE),
    "authorization_carrier": re.compile(
        r"\b(?:project\s+|implementation-start\s+)?authorization\s+"
        r"(?:packet|receipt|envelope|expiry|scope)s?\b",
        re.IGNORECASE,
    ),
    "approval_packet": re.compile(
        r"\b(?:formal[- ]artifact\s+|narrative[- ]artifact\s+)?approval[- ]packets?\b",
        re.IGNORECASE,
    ),
    "legacy_cli": re.compile(
        r"(?:--pauth\b|\bgt projects (?:authorize|revoke-authorization)\b)",
        re.IGNORECASE,
    ),
    "legacy_route": re.compile(r"\ballowed under PAUTH\b", re.IGNORECASE),
}


def _retired_hits(text: str) -> list[str]:
    return [name for name, pattern in RETIRED_PATTERNS.items() if pattern.search(text)]


def _scan_declared_targets() -> dict[str, list[str]]:
    scanned: dict[str, list[str]] = {}
    for relative_path in SCANNED_TARGETS:
        target = PROJECT_ROOT / relative_path
        assert target.is_file(), f"declared surviving target is missing: {relative_path}"
        scanned[relative_path] = _retired_hits(target.read_text(encoding="utf-8"))
    return scanned


def test_retired_authorization_carriers_are_absent() -> None:
    failures = {path: hits for path, hits in _scan_declared_targets().items() if hits}
    assert failures == {}


def test_scan_visits_every_declared_surviving_target() -> None:
    scanned = _scan_declared_targets()
    assert len(SCANNED_TARGETS) == 12
    assert set(scanned) == set(SCANNED_TARGETS)


def test_current_project_authorization_field_is_not_over_purged() -> None:
    fixture = "project.activation-status is authorized or not authorized"
    assert _retired_hits(fixture) == []


def test_generated_output_is_excluded_in_favor_of_baseline_input() -> None:
    assert GENERATED_OUTPUT not in SCANNED_TARGETS
    assert BASELINE_INPUT in SCANNED_TARGETS


def test_command_surface_copies_remain_explicitly_excluded() -> None:
    assert set(COMMAND_SURFACE_EXCLUSIONS).isdisjoint(SCANNED_TARGETS)
