"""Spec-derived tests for WI-4810 skill-usage router (SPEC-SKILL-USAGE-ROUTER-001)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
TABLE_PATH = REPO_ROOT / "config" / "agent-control" / "skill-scenarios.toml"
STARTUP_SCRIPT = REPO_ROOT / "scripts" / "session_self_initialization.py"
GT_EXE = REPO_ROOT / "groundtruth-kb" / ".venv" / "Scripts" / "gt.exe"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import scripts.skill_usage_router as router  # noqa: E402


@pytest.fixture(scope="module")
def router_module():
    return router


def test_ac1_lo_bridge_review_explicit_scenario(router_module) -> None:
    result = router_module.suggest(scenario="lo_bridge_review")
    assert result.scenario == "lo_bridge_review"
    assert {"gtkb-bridge", "proposal-review"} <= set(result.required)
    assert {"check-deliberations", "lo-opportunity-radar"} <= set(result.recommended)


@pytest.mark.parametrize(
    "scenario",
    [
        "lo_bridge_review",
        "lo_verify_report",
        "advisory_report",
        "harness_surface_change",
        "session_wrap",
        "release_readiness",
    ],
)
def test_ac2_each_scenario_returns_table_content(router_module, scenario: str) -> None:
    result = router_module.suggest(scenario=scenario)
    assert result.scenario == scenario
    assert isinstance(result.required, list)
    assert isinstance(result.recommended, list)
    assert result.rationale.strip()


def test_ac3_unknown_inputs_yield_empty_advisory(router_module) -> None:
    assert router_module.suggest(scenario="not-a-real-scenario").is_empty
    assert router_module.suggest(bridge_status="WITHDRAWN").is_empty


def test_ac4_table_edit_changes_output_without_router_code_change(router_module, tmp_path: Path) -> None:
    custom = tmp_path / "skill-scenarios.toml"
    custom.write_text(
        """
schema_version = 1
[scenarios.lo_bridge_review]
title = "custom"
required = ["custom-required"]
recommended = ["custom-recommended"]
rationale = "custom rationale"
""".strip()
        + "\n",
        encoding="utf-8",
    )
    result = router_module.suggest(scenario="lo_bridge_review", table=router_module.load_table(custom))
    assert result.required == ["custom-required"]
    assert result.recommended == ["custom-recommended"]


def test_ac6_deterministic_no_network(router_module, monkeypatch: pytest.MonkeyPatch) -> None:
    def _forbid_network(*_args, **_kwargs):
        raise AssertionError("router must not perform network/LLM calls")

    monkeypatch.setattr("urllib.request.urlopen", _forbid_network)
    first = router_module.suggest(scenario="session_wrap")
    second = router_module.suggest(scenario="session_wrap")
    assert first.as_dict() == second.as_dict()


def test_ac7_router_does_not_mutate_skill_content(router_module, tmp_path: Path) -> None:
    skill_dir = tmp_path / ".claude" / "skills" / "sample"
    skill_dir.mkdir(parents=True)
    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text("before\n", encoding="utf-8")
    before_mtime = skill_file.stat().st_mtime_ns
    router_module.suggest(scenario="lo_bridge_review")
    assert skill_file.read_text(encoding="utf-8") == "before\n"
    assert skill_file.stat().st_mtime_ns == before_mtime


def test_cli_suggest_json_exits_zero() -> None:
    if not GT_EXE.is_file():
        pytest.skip("gt executable not present")
    completed = subprocess.run(
        [str(GT_EXE), "skills", "suggest", "--scenario", "lo_bridge_review", "--json"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["scenario"] == "lo_bridge_review"
    assert payload["required"]


def test_ac5_startup_includes_advisory_for_lo_role(tmp_path: Path) -> None:
    dashboard_dir = tmp_path / "dashboard"
    dashboard_dir.mkdir()
    env = os.environ.copy()
    env["GTKB_STARTUP_REQUESTED_AT"] = "2026-06-25T08:00:00Z"
    env["GTKB_BRIDGE_DISPATCH_KEYWORD"] = "::init gtkb lo"
    completed = subprocess.run(
        [
            sys.executable,
            str(STARTUP_SCRIPT),
            "--emit-startup-service-payload",
            "--fast-hook",
            "--dashboard-dir",
            str(dashboard_dir),
            "--project-root",
            str(REPO_ROOT),
        ],
        capture_output=True,
        text=True,
        env=env,
        timeout=120,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    disclosure = payload["hookSpecificOutput"]["startupDisclosure"]
    assert "Suggested Skills (report-only)" in disclosure
    assert "gtkb-bridge" in disclosure


def test_ac5_startup_omits_advisory_when_router_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    import scripts.session_self_initialization as startup

    def _boom(*_args, **_kwargs):
        raise RuntimeError("simulated router failure")

    monkeypatch.setattr("scripts.skill_usage_router.suggest", _boom)
    model = startup.build_startup_model(REPO_ROOT, role_profile="loyal-opposition", fast_hook=True)
    assert startup._suggested_skills_lines(model) == []
    disclosure = startup._minimized_startup_disclosure(
        {
            "model": model,
            "project_root": str(REPO_ROOT),
            "dashboard_url": "http://localhost:8090",
            "report_path": "dashboard/startup-report.md",
        }
    )
    assert "Suggested Skills (report-only)" not in disclosure
