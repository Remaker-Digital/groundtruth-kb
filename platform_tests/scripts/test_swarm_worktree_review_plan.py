from __future__ import annotations

import importlib.util
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "swarm_worktree_review_plan.py"
CONFIG_PATH = PROJECT_ROOT / "config" / "dispatcher" / "swarm-worktree-review.toml"


def _load_module():
    spec = importlib.util.spec_from_file_location("swarm_worktree_review_plan", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_default_config_is_planning_only_and_disabled() -> None:
    module = _load_module()
    config = module._read_toml(CONFIG_PATH)
    plan = module.build_plan(config, project_root=PROJECT_ROOT)

    assert plan["enabled"] is False
    assert plan["planning_only"] is True
    assert plan["worktree_creation_allowed"] is False
    assert plan["agent_spawn_allowed"] is False
    assert plan["harness_invocation_allowed"] is False
    assert plan["git_mutation_allowed"] is False


def test_lanes_describe_isolation_without_creating_worktrees() -> None:
    module = _load_module()
    config = module._read_toml(CONFIG_PATH)
    plan = module.build_plan(config, project_root=PROJECT_ROOT)

    assert {lane["name"] for lane in plan["lanes"]} == {"implementation", "review"}
    for lane in plan["lanes"]:
        assert lane["enabled"] is False
        assert lane["isolated_worktree_required"] is True
        assert lane["worktree_creation_permitted"] is False
        assert lane["agent_spawn_permitted"] is False
        assert lane["artifact_outputs"]


def test_review_routes_preserve_cross_vendor_or_typed_waiver_constraints() -> None:
    module = _load_module()
    config = module._read_toml(CONFIG_PATH)
    plan = module.build_plan(config, project_root=PROJECT_ROOT)

    assert plan["bridge_bypass_allowed"] is False
    assert plan["required_bridge_sequence"] == ["NEW", "GO", "implementation_report", "VERIFIED"]
    for route in plan["review_routes"]:
        assert route["bridge_bypass_permitted"] is False
        assert route["typed_waiver_required"] is True
    assert any(route["cross_vendor_required"] is True for route in plan["review_routes"])


def test_approval_gates_are_owner_decision_bound() -> None:
    module = _load_module()
    config = module._read_toml(CONFIG_PATH)
    plan = module.build_plan(config, project_root=PROJECT_ROOT)

    gate_names = {gate["name"] for gate in plan["approval_gates"]}
    assert {"worktree_orchestration", "agent_spawn", "finalization_route"}.issubset(gate_names)
    assert all(gate["owner_decision_required"] is True for gate in plan["approval_gates"])


def test_markdown_report_names_constraints_without_runtime_activation() -> None:
    module = _load_module()
    config = module._read_toml(CONFIG_PATH)
    markdown = module.render_markdown(module.build_plan(config, project_root=PROJECT_ROOT))

    assert "Worktree creation allowed: `false`" in markdown
    assert "Harness invocation allowed: `false`" in markdown
    assert "cross-vendor reviewer assignment or typed waiver" in markdown
    assert "NEW -> GO -> implementation_report -> VERIFIED" in markdown
