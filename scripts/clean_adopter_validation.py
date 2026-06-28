#!/usr/bin/env python3
"""Validate that a clean adopter scaffold is consumable without platform leakage."""

from __future__ import annotations

import argparse
import gc
import os
import shutil
import subprocess
import sys
import time
import uuid
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "groundtruth-kb" / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from groundtruth_kb.project.doctor import run_doctor  # noqa: E402
from groundtruth_kb.project.scaffold import (  # noqa: E402
    ScaffoldOptions,
    scaffold_project,
    validate_scaffold_minimum_and_no_leakage,
)


@dataclass(frozen=True)
class StepResult:
    """Single validation step outcome."""

    name: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class ValidationRun:
    """Complete clean-adopter validation outcome."""

    target: Path
    steps: tuple[StepResult, ...]

    @property
    def passed(self) -> bool:
        return all(step.passed for step in self.steps)

    @property
    def exit_code(self) -> int:
        return 0 if self.passed else 1

    def render(self) -> str:
        lines = [f"clean_adopter_validation target={self.target}", ""]
        for step in self.steps:
            status = "PASS" if step.passed else "FAIL"
            lines.append(f"{status} {step.name}: {step.detail}")
        lines.append("")
        lines.append("Overall: " + ("PASS" if self.passed else "FAIL"))
        return "\n".join(lines)


def _validate_in_root_application_target(target: Path) -> Path:
    resolved = target.resolve()
    applications_root = (PROJECT_ROOT / "applications").resolve()
    if resolved.parent != applications_root:
        raise ValueError(f"target must live directly under {applications_root}; got {resolved}")
    return resolved


def _run_cli(target: Path, args: list[str]) -> StepResult:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(SRC_ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    command = [
        sys.executable,
        "-m",
        "groundtruth_kb",
        "--config",
        str(target / "groundtruth.toml"),
        *args,
    ]
    result = subprocess.run(command, cwd=target, env=env, text=True, capture_output=True, timeout=30)
    detail = " ".join(args)
    if result.returncode == 0:
        return StepResult(detail, True, result.stdout.strip() or "ok")
    output = (result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}")[:500]
    return StepResult(detail, False, output)


def _doctor_step(target: Path, profile: str) -> StepResult:
    report = run_doctor(target, profile)
    failures = [check for check in report.checks if check.required and check.status == "fail"]
    if not failures:
        return StepResult("gt project doctor", True, f"overall={report.overall}; actionable required failures=0")
    detail = "; ".join(f"{check.name}: {check.message}" for check in failures[:5])
    return StepResult("gt project doctor", False, detail)


def _packaging_step(target: Path, profile: str, cloud_provider: str) -> StepResult:
    result = validate_scaffold_minimum_and_no_leakage(target, profile, cloud_provider=cloud_provider)
    return StepResult("scaffold packaging", result.passed, result.summary())


def run_smoke_ops(target: Path) -> tuple[StepResult, ...]:
    """Run read-only or dry-run CLI smoke operations against the adopter."""
    return (
        _run_cli(target, ["summary"]),
        _run_cli(
            target,
            [
                "backlog",
                "add",
                "--title",
                "Clean adopter validation smoke",
                "--origin",
                "hygiene",
                "--component",
                "adoption",
                "--change-reason",
                "clean adopter validation dry-run smoke",
                "--dry-run",
            ],
        ),
    )


def validate_existing_adopter(
    target: Path,
    *,
    profile: str = "dual-agent",
    cloud_provider: str = "none",
    run_doctor_check: bool = True,
    run_smoke_checks: bool = True,
) -> ValidationRun:
    """Validate an already-scaffolded adopter tree."""
    steps: list[StepResult] = [_packaging_step(target, profile, cloud_provider)]
    if run_doctor_check:
        steps.append(_doctor_step(target, profile))
    if run_smoke_checks:
        steps.extend(run_smoke_ops(target))
    return ValidationRun(target=target, steps=tuple(steps))


def scaffold_clean_adopter(target: Path, *, profile: str, cloud_provider: str) -> Path:
    """Create a clean adopter using the live scaffold_project path."""
    options = ScaffoldOptions(
        project_name=target.name,
        profile=profile,
        owner="CleanAdopterValidation",
        target_dir=target,
        copyright_notice="Test (c) 2026 Remaker Digital",
        cloud_provider=cloud_provider,
        init_git=False,
        include_ci=False,
        seed_example=False,
        gt_kb_root=PROJECT_ROOT,
    )
    return scaffold_project(options)


def _cleanup_tree(target: Path) -> None:
    """Remove a temporary adopter tree, retrying briefly for Windows file locks."""
    for attempt in range(5):
        try:
            gc.collect()
            shutil.rmtree(target)
            return
        except FileNotFoundError:
            return
        except OSError:
            if attempt == 4:
                raise
            time.sleep(0.2)


def run_clean_adopter_validation(
    *,
    adopter_name: str | None = None,
    temp_dir: Path | None = None,
    profile: str = "dual-agent",
    cloud_provider: str = "none",
    keep: bool = False,
) -> ValidationRun:
    """Scaffold a temporary adopter, validate it, and clean it up by default."""
    name = adopter_name or f"_clean_adopter_{uuid.uuid4().hex[:8]}"
    target = _validate_in_root_application_target(temp_dir or (PROJECT_ROOT / "applications" / name))
    if target.exists():
        raise FileExistsError(f"target already exists: {target}")
    created = False
    try:
        scaffold_clean_adopter(target, profile=profile, cloud_provider=cloud_provider)
        created = True
        return validate_existing_adopter(target, profile=profile, cloud_provider=cloud_provider)
    finally:
        if created and not keep and target.exists():
            _cleanup_tree(target)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--adopter-name", default=None, help="Temporary adopter directory name under applications/.")
    parser.add_argument("--temp-dir", type=Path, default=None, help="Explicit in-root applications/<name> target.")
    parser.add_argument("--profile", default="dual-agent", help="Scaffold profile to validate.")
    parser.add_argument("--cloud-provider", default="none", help="Cloud provider passed to the scaffold.")
    parser.add_argument("--keep", action="store_true", help="Keep the temporary adopter directory after validation.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        result = run_clean_adopter_validation(
            adopter_name=args.adopter_name,
            temp_dir=args.temp_dir,
            profile=args.profile,
            cloud_provider=args.cloud_provider,
            keep=args.keep,
        )
    except Exception as exc:  # intentional-catch: CLI boundary, report and return non-zero
        print(f"clean_adopter_validation failed before validation: {exc}", file=sys.stderr)
        return 2
    print(result.render())
    return result.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
