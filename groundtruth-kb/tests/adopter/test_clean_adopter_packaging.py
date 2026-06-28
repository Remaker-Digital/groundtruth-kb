# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Clean-adopter packaging validation for GTKB-ISOLATION-017."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

from groundtruth_kb.project.doctor import run_doctor
from groundtruth_kb.project.scaffold import validate_scaffold_minimum_and_no_leakage


def _load_validation_script() -> ModuleType:
    script = Path(__file__).resolve().parents[3] / "scripts" / "clean_adopter_validation.py"
    spec = importlib.util.spec_from_file_location("clean_adopter_validation", script)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_clean_adopter_validation_passes(clean_adopter: tuple[Path, Path]) -> None:
    """Validation script helper passes on a freshly scaffolded clean adopter."""
    adopter, _ = clean_adopter
    module = _load_validation_script()

    result = module.validate_existing_adopter(
        adopter,
        profile="dual-agent",
        run_doctor_check=False,
        run_smoke_checks=False,
    )

    assert result.exit_code == 0
    assert result.steps[0].passed


def test_clean_adopter_missing_piece_fails(clean_adopter: tuple[Path, Path]) -> None:
    """A missing minimum scaffold file produces a non-zero validation result."""
    adopter, _ = clean_adopter
    (adopter / "README.md").unlink()
    module = _load_validation_script()

    result = module.validate_existing_adopter(
        adopter,
        profile="dual-agent",
        run_doctor_check=False,
        run_smoke_checks=False,
    )

    assert result.exit_code == 1
    assert not result.steps[0].passed
    assert "README.md" in result.steps[0].detail


def test_doctor_exposes_no_writable_product_paths_in_temp_adopter(clean_adopter: tuple[Path, Path]) -> None:
    """Fresh clean adopter surfaces same-user product writability instead of suppressing it."""
    adopter, _ = clean_adopter

    report = run_doctor(adopter, "dual-agent")
    failures = [check for check in report.checks if check.required and check.status == "fail"]
    failure_names = {check.name for check in failures}
    unexpected = [check for check in failures if check.name != "isolation:no-writable-product-paths"]

    assert "isolation:no-writable-product-paths" in failure_names
    assert not unexpected, "Unexpected doctor required failures:\n" + "\n".join(
        f"  {check.name}: {check.message}" for check in failures
    )


def test_clean_adopter_doctor_step_reports_no_writable_product_paths_failure(monkeypatch, tmp_path: Path) -> None:
    """The validator must not suppress the no-writable-product-paths required check."""
    module = _load_validation_script()
    failure = SimpleNamespace(
        required=True,
        status="fail",
        name="isolation:no-writable-product-paths",
        message="product-scope paths writable from app session",
    )
    monkeypatch.setattr(
        module,
        "run_doctor",
        lambda _target, _profile: SimpleNamespace(overall="fail", checks=[failure]),
    )

    result = module._doctor_step(tmp_path, "dual-agent")

    assert result.passed is False
    assert "isolation:no-writable-product-paths" in result.detail


def test_scaffold_leakage_check_detects_internal(clean_adopter: tuple[Path, Path]) -> None:
    """Internal GT-KB platform state paths are reported as leakage."""
    adopter, _ = clean_adopter
    leaked = adopter / ".gtkb-state" / "current.json"
    leaked.parent.mkdir(parents=True)
    leaked.write_text("{}", encoding="utf-8")

    result = validate_scaffold_minimum_and_no_leakage(adopter, "dual-agent")

    assert not result.passed
    assert ".gtkb-state/current.json" in result.leaked_paths


def test_live_gt_project_init_clean_of_leakage(clean_adopter: tuple[Path, Path]) -> None:
    """The live scaffold_project path satisfies the minimum-file/leakage check."""
    adopter, _ = clean_adopter

    result = validate_scaffold_minimum_and_no_leakage(adopter, "dual-agent")

    assert result.passed
    assert "groundtruth.toml" in result.expected_paths
    assert "MEMORY.md" in result.expected_paths
    assert not result.missing_paths
    assert not result.leaked_paths


def test_smoke_backlog_ops_in_temp_adopter(clean_adopter: tuple[Path, Path]) -> None:
    """Basic summary and dry-run backlog CLI operations work in the adopter."""
    adopter, _ = clean_adopter
    module = _load_validation_script()

    results = module.run_smoke_ops(adopter)

    assert all(result.passed for result in results), "\n".join(f"{result.name}: {result.detail}" for result in results)
