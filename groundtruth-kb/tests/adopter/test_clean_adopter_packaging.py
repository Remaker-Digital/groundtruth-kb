"""Clean application packaging: minimum files, no platform leakage, native diagnostics and backlog smoke."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

from groundtruth_kb.project.doctor import inspect_native_application
from groundtruth_kb.project.scaffold import validate_scaffold_minimum_and_no_leakage


def _load_validation_script() -> ModuleType:
    script = Path(__file__).resolve().parents[3] / "scripts" / "clean_adopter_validation.py"
    spec = importlib.util.spec_from_file_location("clean_adopter_validation", script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_clean_adopter_validation_passes(clean_adopter, native_application) -> None:
    adopter, host = clean_adopter
    module = _load_validation_script()
    result = module.validate_existing_adopter(
        adopter, host_root=host, project_id="PROJECT-Alpha", profile="dual-agent", run_smoke_checks=False
    )
    assert result.exit_code == 0, result.render()
    assert result.steps[0].passed and result.steps[1].name == "gt project doctor"


def test_clean_adopter_missing_piece_fails(clean_adopter) -> None:
    adopter, host = clean_adopter
    (adopter / "README.md").unlink()
    module = _load_validation_script()
    result = module.validate_existing_adopter(
        adopter,
        host_root=host,
        project_id="PROJECT-Alpha",
        profile="dual-agent",
        run_doctor_check=False,
        run_smoke_checks=False,
    )
    assert result.exit_code == 1
    assert not result.steps[0].passed and "README.md" in result.steps[0].detail


def test_doctor_reports_platform_state_inside_the_application(clean_adopter, native_application) -> None:
    """Platform state or a local authority store inside an application is a required failure."""
    adopter, host = clean_adopter
    leaked = adopter / ".gtkb-state" / "current.json"
    leaked.parent.mkdir(parents=True)
    leaked.write_text("{}", encoding="utf-8")
    (adopter / "groundtruth.db").write_bytes(b"")
    report = inspect_native_application(native_application.client, "PROJECT-Alpha", host)
    finding = next(row for row in report["checks"] if row["name"] == "Platform leakage")
    assert finding["status"] == "fail" and ".gtkb-state/current.json" in finding["message"]
    assert "groundtruth.db" in finding["message"] and report["status"] == "fail"
    result = native_application.invoke(
        "project", "doctor", "--project-id", "PROJECT-Alpha", "--host-root", str(host), "--json"
    )
    assert result.exit_code == 1 and json.loads(result.output)["status"] == "fail"


def test_scaffold_leakage_check_detects_internal(clean_adopter) -> None:
    adopter, _host = clean_adopter
    leaked = adopter / ".gtkb-state" / "current.json"
    leaked.parent.mkdir(parents=True)
    leaked.write_text("{}", encoding="utf-8")
    result = validate_scaffold_minimum_and_no_leakage(adopter, "dual-agent")
    assert not result.passed and ".gtkb-state/current.json" in result.leaked_paths


def test_live_gt_project_init_clean_of_leakage(clean_adopter) -> None:
    adopter, _host = clean_adopter
    result = validate_scaffold_minimum_and_no_leakage(adopter, "dual-agent")
    assert result.passed, result.summary()
    assert "groundtruth.toml" in result.expected_paths and "README.md" in result.expected_paths
    assert "groundtruth.db" not in result.expected_paths
    assert not result.missing_paths and not result.leaked_paths


def test_smoke_backlog_ops_in_temp_adopter(clean_adopter, native_application) -> None:
    """A registered application creates and reads its own canonical work through the native backlog."""
    adopter, _host = clean_adopter
    module = _load_validation_script()
    results = module.run_smoke_ops(adopter, project_id="PROJECT-Alpha")
    assert all(result.passed for result in results), "\n".join(f"{r.name}: {r.detail}" for r in results)
    listed = native_application.invoke("backlog", "list", "--json", config=adopter / "groundtruth.toml")
    assert listed.exit_code == 0, listed.output
    rows = json.loads(listed.output)
    assert [row["id"] for row in rows] == ["WI-ALPHA-SMOKE"]
    shown = native_application.client.request("GET", "/v1/projects/PROJECT-Alpha")
    assert [row["work_item_id"] for row in shown["memberships"]] == ["WI-ALPHA-SMOKE"]
    assert native_application.client.request("GET", "/v1/projects/PROJECT-Beta")["memberships"] == []
