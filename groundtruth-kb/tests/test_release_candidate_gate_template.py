"""Tests for the release-candidate-gate managed skill template."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

TEMPLATE_ROOT = Path(__file__).resolve().parent.parent / "templates" / "skills" / "release-candidate-gate"
SKILL_PATH = TEMPLATE_ROOT / "SKILL.md"
SCRIPT_PATH = TEMPLATE_ROOT / "scripts" / "release_candidate_gate.py"


def _load_template_module():
    spec = importlib.util.spec_from_file_location("release_candidate_gate_template", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["release_candidate_gate_template"] = module
    spec.loader.exec_module(module)
    return module


def _render(text: str, **values: str) -> str:
    rendered = text
    for key, value in values.items():
        rendered = rendered.replace("{{" + key + "}}", value)
    return rendered


def test_template_includes_all_readiness_check_sections() -> None:
    skill = SKILL_PATH.read_text(encoding="utf-8")

    for phrase in (
        "Security scans",
        "Dependency audit",
        "Targeted regression tests",
        "Frontend builds",
        "GroundTruth governance adoption",
    ):
        assert phrase in skill


def test_template_renders_with_adopter_parameters() -> None:
    script = SCRIPT_PATH.read_text(encoding="utf-8")

    rendered = _render(
        script,
        adopter_python_scan_targets="src tests",
        adopter_security_scan_target="src",
        adopter_targeted_tests="tests/unit tests/security",
        adopter_frontend_projects="widget;admin",
        adopter_governance_checks="python -m groundtruth_kb project doctor .;python -m groundtruth_kb release status",
        adopter_requirements_file="requirements.lock",
    )

    assert "src tests" in rendered
    assert "tests/unit tests/security" in rendered
    assert "widget;admin" in rendered
    assert "requirements.lock" in rendered
    assert "{{adopter_" not in rendered


def test_template_defaults_applied_when_adopter_omits_parameters() -> None:
    module = _load_template_module()

    config = module._config_from_templates()

    assert config.python_scan_targets == ["src", "tests"]
    assert config.security_scan_target == "src"
    assert config.targeted_tests == ["tests"]
    assert config.frontend_projects == []
    assert config.requirements_file == "requirements.txt"
    assert config.governance_commands == [["python", "-m", "groundtruth_kb", "project", "doctor", "."]]


def test_template_script_command_order(monkeypatch) -> None:
    module = _load_template_module()
    commands: list[list[str]] = []
    config = module.GateConfig(
        python_scan_targets=["src", "tests"],
        security_scan_target="src",
        targeted_tests=["tests/unit"],
        frontend_projects=[],
        governance_commands=[["python", "-m", "groundtruth_kb", "project", "doctor", "."]],
        requirements_file="requirements.txt",
    )

    monkeypatch.setattr(module, "PROJECT_ROOT", Path.cwd())
    monkeypatch.setattr(module, "_run", lambda command, **_kwargs: commands.append(command))
    monkeypatch.setattr(Path, "is_file", lambda self: True if self.name == "requirements.txt" else Path.exists(self))

    module._python_gates(config)

    assert commands[0][1:5] == ["-m", "groundtruth_kb", "secrets", "scan"]
    assert commands[1][1:4] == ["-m", "pip_audit", "-r"]
    assert commands[2][1:4] == ["-m", "bandit", "-r"]
    assert commands[3][1:4] == ["-m", "ruff", "check"]
    assert commands[4][1:4] == ["-m", "pytest", "tests/unit"]
    assert commands[5] == ["python", "-m", "groundtruth_kb", "project", "doctor", "."]


def test_render_does_not_leak_internal_or_adopter_specific_paths() -> None:
    combined = SKILL_PATH.read_text(encoding="utf-8") + "\n" + SCRIPT_PATH.read_text(encoding="utf-8")

    forbidden = (
        "E:\\GT-KB",
        "applications/Agent_Red",
        "applications\\Agent_Red",
        "Agent Red",
        ".claude/skills/release-candidate-gate",
    )
    for token in forbidden:
        assert token not in combined


def test_registry_binding_remains_deferred_in_template_only_slice() -> None:
    skill = SKILL_PATH.read_text(encoding="utf-8")
    script = SCRIPT_PATH.read_text(encoding="utf-8")

    assert "managed-artifacts.toml" not in skill
    assert "managed-artifacts.toml" not in script
