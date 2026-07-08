from __future__ import annotations

import importlib.util
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "dispatch_sandbox_plan.py"
CONFIG_PATH = PROJECT_ROOT / "config" / "dispatcher" / "sandbox-execution.toml"


def _load_module():
    spec = importlib.util.spec_from_file_location("dispatch_sandbox_plan", SCRIPT_PATH)
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
    assert plan["runtime_launch_allowed"] is False
    assert plan["credential_access_allowed"] is False
    assert plan["dispatcher_replacement_allowed"] is False


def test_providers_require_future_owner_approval_and_never_launch() -> None:
    module = _load_module()
    config = module._read_toml(CONFIG_PATH)
    plan = module.build_plan(config, project_root=PROJECT_ROOT)

    assert {provider["name"] for provider in plan["providers"]} == {"modal", "daytona"}
    for provider in plan["providers"]:
        assert provider["enabled"] is False
        assert provider["launch_permitted"] is False
        assert provider["credential_source"] == "future_owner_approval"
        assert provider["required_artifacts"]


def test_approval_gates_are_owner_decision_bound() -> None:
    module = _load_module()
    config = module._read_toml(CONFIG_PATH)
    plan = module.build_plan(config, project_root=PROJECT_ROOT)

    gate_names = {gate["name"] for gate in plan["approval_gates"]}
    assert {"provider_selection", "credential_use", "dispatcher_activation"}.issubset(gate_names)
    assert all(gate["owner_decision_required"] is True for gate in plan["approval_gates"])


def test_markdown_report_names_constraints_without_runtime_activation() -> None:
    module = _load_module()
    config = module._read_toml(CONFIG_PATH)
    markdown = module.render_markdown(module.build_plan(config, project_root=PROJECT_ROOT))

    assert "Runtime launch allowed: `false`" in markdown
    assert "Credential access allowed: `false`" in markdown
    assert "dispatcher daemon remains the control plane" in markdown
