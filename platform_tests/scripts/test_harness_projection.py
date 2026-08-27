"""Verification tests for the harness projection framework.

Landed by bridge/gtkb-baseline-correction-and-goose-projector-slice-1 (GO at
-004). Maps to GOV-HARNESS-NEUTRAL-BASELINE-001:

- obligation 3 via ``test_baseline_token_census`` (ratchet: seeded at the
  measured value, may only decrease);
- obligation 2/verification bullet 2 via ``test_projection_idempotent``
  (byte-reproducible plan);
- obligation 5 via ``test_projected_markdown_stamped_after_frontmatter``;
- fail-closed token handling via ``test_unresolved_token_is_projector_gap``.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENGINE_DIR = PROJECT_ROOT / "scripts" / "harness_projection"
if str(ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(ENGINE_DIR))

import project_harness  # noqa: E402

BASELINE = PROJECT_ROOT / ".harness-baseline-configuration"

HARNESS_TOKENS = [
    "codex",
    "claude",
    "cursor",
    "goose",
    "antigravity",
    "ollama",
    "openrouter",
    "alibaba",
    "api-harness",
]

# Ratchet cap seeded from the census measured at landing time (Phase A
# increment 3 state; method: case-insensitive matched lines per token over
# *.md,*.py,*.toml,*.json,*.yaml,*.txt). The number may ONLY decrease as
# Phase A relocations and Phase D formal-artifact edits land. Raising it
# requires an owner-approved bridge revision.
CENSUS_CAP = 210


def measure_census() -> int:
    total = 0
    for token in HARNESS_TOKENS:
        pattern = re.compile(re.escape(token), re.I)
        for path in BASELINE.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in {
                ".md",
                ".py",
                ".toml",
                ".json",
                ".yaml",
                ".txt",
            }:
                continue
            text = path.read_text(encoding="utf-8", errors="surrogateescape")
            total += sum(1 for line in text.splitlines() if pattern.search(line))
    return total


def test_baseline_token_census():
    measured = measure_census()
    assert measured <= CENSUS_CAP, (
        f"baseline harness-token census regressed: {measured} > cap {CENSUS_CAP}. "
        "New harness references entered the neutral baseline "
        "(GOV-HARNESS-NEUTRAL-BASELINE-001 obligation 3). Remove them or, if a "
        "legitimate decrease landed, lower the cap - never raise it without an "
        "owner-approved bridge revision."
    )


def test_projection_idempotent():
    plan_a = project_harness.build_plan("goose")
    plan_b = project_harness.build_plan("goose")
    assert plan_a.writes == plan_b.writes
    assert not plan_a.gaps, f"projector gaps present: {plan_a.gaps}"


def test_antigravity_projection_idempotent_and_clean() -> None:
    plan_a = project_harness.build_plan("antigravity")
    plan_b = project_harness.build_plan("antigravity")
    assert plan_a.writes, "antigravity plan rendered no files"
    assert not plan_a.gaps, f"projector gaps present: {plan_a.gaps}"
    assert plan_a.writes == plan_b.writes, "antigravity projection is not byte-idempotent"

    bridge_rule = plan_a.writes.get(".agent/rules/bridge-essential.md")
    assert bridge_rule is not None, "antigravity bridge rule not rendered"
    for token in ("{{HARNESS_RULES_DIR}}", "{{HARNESS_CONFIG_DIR}}"):
        assert token not in bridge_rule, (
            f"{token} survived substitution in the antigravity bridge rule "
            "(ADR-RULE-PROJECTION-FLOW-INVERSION-001: the projection carries no "
            "unsubstituted harness tokens)"
        )
    assert ".agent/rules/" in bridge_rule, (
        "antigravity bridge rule is not self-referential; it must point at its own "
        "projection root (ADR-ISOLATION-APPLICATION-PLACEMENT-001)"
    )
    assert ".claude/" not in bridge_rule, (
        "antigravity bridge rule emits a foreign harness root; each projection "
        "references only its own config surface (ADR-CROSS-HARNESS-PARITY-001)"
    )


def test_projected_markdown_stamped_after_frontmatter():
    plan = project_harness.build_plan("goose")
    skill_paths = [p for p in plan.writes if p.endswith("SKILL.md")]
    assert skill_paths, "no SKILL.md files in the goose plan"
    for rel in skill_paths:
        content = plan.writes[rel]
        assert "THIS FILE IS A PROJECTION, NOT CANONICAL." in content, rel
        if content.startswith("---"):
            close = content.index("\n---", 3)
            frontmatter = content[: close + 4]
            assert "PROJECTION" not in frontmatter, (
                f"{rel}: stamp landed inside YAML frontmatter, which breaks "
                "skill discovery (obligation 5 placement rule)"
            )


def test_projected_hooks_registration_is_native():
    plan = project_harness.build_plan("goose")
    hooks_json = plan.writes.get(".goose/plugins/gtkb/hooks/hooks.json")
    assert hooks_json is not None, "goose plugin hooks.json not rendered"
    assert "PreToolUse" in hooks_json and "Stop" in hooks_json
    assert "$CLAUDE_PROJECT_DIR" not in hooks_json


def test_unresolved_token_is_projector_gap(tmp_path, monkeypatch):
    plan = project_harness.Plan()
    result = project_harness.substitute("path is {{HARNESS_UNKNOWN_TOKEN}}", {"HARNESS_NAME": "x"}, "f.md", plan.gaps)
    assert "{{HARNESS_UNKNOWN_TOKEN}}" in result
    assert plan.gaps and "unresolved token" in plan.gaps[0]


def test_pending_profile_fails_closed():
    with pytest.raises(project_harness.ProjectionError):
        project_harness.build_plan("codex")


def test_normalize_planned_rel_strips_dot_slash_without_lstripping_baseline_dot():
    assert (
        project_harness.normalize_planned_rel("./.harness-baseline-configuration/skills/x.md")
        == ".harness-baseline-configuration/skills/x.md"
    )
    assert (
        project_harness.normalize_planned_rel(".harness-baseline-configuration\\skills\\x.md")
        == ".harness-baseline-configuration/skills/x.md"
    )
    assert not project_harness.is_baseline_destination("scripts/harness_projection/project_harness.py")


def test_write_mode_rejects_baseline_destination_and_writes_nothing(tmp_path, monkeypatch):
    plan = project_harness.Plan()
    dest = ".harness-baseline-configuration/skills/wi6539-injected.md"
    plan.writes[dest] = "should-not-land\n"
    monkeypatch.setattr(project_harness, "build_plan", lambda harness: plan)
    monkeypatch.setattr(project_harness, "PROJECT_ROOT", tmp_path)
    with pytest.raises(project_harness.ProjectionError, match="harness-baseline-configuration"):
        project_harness.run("goose", "write")
    assert not (tmp_path / dest).exists()


def test_write_mode_rejects_dot_slash_and_backslash_baseline_destinations(tmp_path, monkeypatch):
    monkeypatch.setattr(project_harness, "PROJECT_ROOT", tmp_path)
    for dest in (
        "./.harness-baseline-configuration/skills/wi6539-dot-slash.md",
        ".harness-baseline-configuration\\skills\\wi6539-backslash.md",
    ):
        plan = project_harness.Plan()
        plan.writes[dest] = "should-not-land\n"
        monkeypatch.setattr(project_harness, "build_plan", lambda harness, _plan=plan: _plan)
        with pytest.raises(project_harness.ProjectionError, match="harness-baseline-configuration"):
            project_harness.run("goose", "write")
        assert not (tmp_path / project_harness.normalize_planned_rel(dest)).exists()
