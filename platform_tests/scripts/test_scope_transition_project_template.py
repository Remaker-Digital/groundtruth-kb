"""Spec-derived tests for the Scope-Transition project template (WI-4688 Slice B).

Covers GOV-SCOPE-TRANSITION-PROCEDURE-001 (template instantiates the 5 steps +
cites the procedure), SPEC-1830 (deterministic instantiation, not hand-built),
and GOV-STANDING-BACKLOG-001 (governed project/WI creation). The dry-run path
must not mutate MemBase.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_PATH = REPO_ROOT / "config" / "project-templates" / "scope-transition.toml"
HELPER_PATH = REPO_ROOT / "scripts" / "scope_transition_project.py"
PROCEDURE_SPEC = "GOV-SCOPE-TRANSITION-PROCEDURE-001"


def _load_helper():
    spec = importlib.util.spec_from_file_location("scope_transition_project", HELPER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


helper = _load_helper()


def test_template_is_well_formed() -> None:
    template = helper.load_template(TEMPLATE_PATH)
    assert "template" in template and "work_items" in template
    assert template["template"]["id"] == "scope-transition"


def test_template_cites_procedure_spec() -> None:
    template = helper.load_template(TEMPLATE_PATH)
    assert template["template"]["procedure_spec"] == PROCEDURE_SPEC


def test_template_defines_five_procedure_steps() -> None:
    template = helper.load_template(TEMPLATE_PATH)
    steps = sorted(int(wi["step"]) for wi in template["work_items"])
    assert steps == [1, 2, 3, 4, 5]


def test_plan_project_substitutes_application() -> None:
    template = helper.load_template(TEMPLATE_PATH)
    plan = helper.plan_project(template, "Agent Red")
    assert plan["project_id"] == "PROJECT-SCOPE-TRANSITION-AGENT-RED"
    assert "Agent Red" in plan["name"]
    assert "Agent Red" in plan["purpose"]
    assert len(plan["work_items"]) == 5
    assert all("Agent Red" in wi["title"] for wi in plan["work_items"])
    assert "{application}" not in plan["scope_note"]


def test_render_commands_are_governed_gt_calls() -> None:
    template = helper.load_template(TEMPLATE_PATH)
    plan = helper.plan_project(template, "Agent Red")
    commands = helper.render_commands(plan)
    assert commands[0][:3] == ["gt", "projects", "create"]
    assert sum(1 for c in commands if c[:3] == ["gt", "backlog", "add"]) == 5
    assert all(c[0] == "gt" for c in commands)


def test_instantiate_dry_run_produces_project_skeleton() -> None:
    with mock.patch.object(helper.subprocess, "run") as run:
        result = helper.instantiate(TEMPLATE_PATH, "Agent Red", dry_run=True)
    run.assert_not_called()  # SPEC-1830 / GOV-STANDING-BACKLOG-001: dry-run mutates nothing.
    assert result["applied"] is False
    assert len(result["plan"]["work_items"]) == 5
    assert result["plan"]["procedure_spec"] == PROCEDURE_SPEC
