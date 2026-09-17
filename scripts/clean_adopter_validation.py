#!/usr/bin/env python3
"""Validate that an initialized application is consumable without platform leakage.

The application must already exist under the selected host's ``applications/``
slot, registered in the catalog and initialized with ``gt project init`` for an
execution project. Validation reads the application's files and the configured
native authority; the optional smoke step writes the application's own canonical
records through the ordinary CLI and is intended for disposable authorities.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

from groundtruth_kb.authority_client import AuthorityClient, AuthorityClientError
from groundtruth_kb.config import GTConfig, GTConfigError
from groundtruth_kb.project.doctor import inspect_native_application
from groundtruth_kb.project.scaffold import validate_scaffold_minimum_and_no_leakage


@dataclass(frozen=True)
class StepResult:
    """Single validation step outcome."""

    name: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class ValidationRun:
    """Complete clean-application validation outcome."""

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


def _run_cli(target: Path, args: list[str]) -> StepResult:
    env = {key: value for key, value in os.environ.items() if not key.upper().startswith(("GT_", "GTKB_", "PG"))}
    env.update(PYTHONIOENCODING="utf-8", PYTHONDONTWRITEBYTECODE="1")
    command = [sys.executable, "-P", "-m", "groundtruth_kb", "--config", str(target / "groundtruth.toml"), *args]
    result = subprocess.run(command, cwd=target, env=env, text=True, capture_output=True, timeout=60, encoding="utf-8")
    detail = " ".join(args[:3])
    if result.returncode == 0:
        return StepResult(detail, True, (result.stdout.strip() or "ok")[:500])
    output = (result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}")[:500]
    return StepResult(detail, False, output)


def _doctor_step(target: Path, host_root: Path, project_id: str) -> StepResult:
    try:
        config = GTConfig.load(config_path=target / "groundtruth.toml", discover=False)
        if not config.authority_url:
            return StepResult("gt project doctor", False, "groundtruth.toml selects no authority_url")
        report = inspect_native_application(AuthorityClient(config.authority_url), project_id, host_root)
    except (AuthorityClientError, GTConfigError, OSError, ValueError) as error:
        return StepResult("gt project doctor", False, f"{getattr(error, 'code', 'invalid_application')}: {error}")
    failures = [row for row in report["checks"] if row["status"] == "fail"]
    if not failures:
        return StepResult("gt project doctor", True, f"status={report['status']}; failing checks=0")
    return StepResult("gt project doctor", False, "; ".join(f"{row['name']}: {row['message']}" for row in failures[:5]))


def _packaging_step(target: Path, profile: str, cloud_provider: str) -> StepResult:
    result = validate_scaffold_minimum_and_no_leakage(target, profile, cloud_provider=cloud_provider)
    return StepResult("scaffold packaging", result.passed, result.summary())


def run_smoke_ops(target: Path, *, project_id: str, suffix: str = "SMOKE") -> tuple[StepResult, ...]:
    """Create and read the application's own canonical work through the ordinary CLI.

    This writes a specification, an executable test, a test plan phase and a
    work item under the selected project. Use it against disposable authorities.
    """
    scope = None
    marker = target / "application.toml"
    if marker.is_file():
        import tomllib

        payload = tomllib.loads(marker.read_text(encoding="utf-8"))
        name = payload.get("application", {}).get("name")
        scope = f"application:{name}" if isinstance(name, str) and name else None
    tag = f"{project_id}-{suffix}".upper().replace("_", "-")
    ids = {
        "spec": f"SPEC-{tag}",
        "test": f"TEST-{tag}",
        "plan": f"PLAN-{tag}",
        "phase": f"PHASE-{tag}",
        "work": "WI-" + tag.removeprefix("PROJECT-"),
    }
    records = [
        ("spec", ids["spec"], {"title": "Smoke behavior", "description": "Smoke", "application_scope": scope}, []),
        (
            "tests",
            ids["test"],
            {
                "title": "Smoke test",
                "test_type": "integration",
                "expected_outcome": "Smoke observed",
                "spec_id": ids["spec"],
                "test_file": "tests/test_smoke.py",
                "test_function": "test_smoke",
                "application_scope": scope,
            },
            [],
        ),
        ("test-plans", ids["plan"], {"title": "Smoke plan"}, []),
        (
            "test-phases",
            ids["phase"],
            {
                "title": "Smoke phase",
                "plan_id": ids["plan"],
                "phase_order": 10,
                "gate_criteria": "Smoke",
                "test_ids": [ids["test"]],
            },
            [],
        ),
        (
            "backlog",
            ids["work"],
            {
                "title": "Clean application validation smoke",
                "source_spec_id": ids["spec"],
                "source_test_id": ids["test"],
            },
            ["--project-id", project_id],
        ),
    ]
    results: list[StepResult] = []
    with tempfile.TemporaryDirectory(prefix="gtkb-smoke-") as temporary:
        for group, record_id, fields, extra in records:
            fields = {key: value for key, value in fields.items() if value is not None}
            fields_file = Path(temporary) / f"{record_id}.json"
            fields_file.write_text(json.dumps(fields), encoding="utf-8")
            results.append(
                _run_cli(
                    target,
                    [
                        group,
                        "record",
                        "--id",
                        record_id,
                        "--fields-file",
                        str(fields_file),
                        "--expected-version",
                        "0",
                        "--actor",
                        "clean-adopter-validation",
                        "--change-reason",
                        "clean application validation smoke",
                        *extra,
                        "--json",
                    ],
                )
            )
    results.append(_run_cli(target, ["backlog", "show", ids["work"], "--json"]))
    results.append(_run_cli(target, ["projects", "show", project_id, "--json"]))
    return tuple(results)


def validate_existing_adopter(
    target: Path,
    *,
    host_root: Path,
    project_id: str,
    profile: str = "dual-agent",
    cloud_provider: str = "none",
    run_doctor_check: bool = True,
    run_smoke_checks: bool = False,
) -> ValidationRun:
    """Validate an already-initialized application tree."""
    steps: list[StepResult] = [_packaging_step(target, profile, cloud_provider)]
    if run_doctor_check:
        steps.append(_doctor_step(target, host_root, project_id))
    if run_smoke_checks:
        steps.extend(run_smoke_ops(target, project_id=project_id))
    return ValidationRun(target=target, steps=tuple(steps))


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", type=Path, required=True, help="Initialized application root.")
    parser.add_argument("--host-root", type=Path, required=True, help="Platform host that registers the application.")
    parser.add_argument("--project-id", required=True, help="Execution project associated with the application.")
    parser.add_argument("--profile", default="dual-agent", help="Scaffold profile to validate.")
    parser.add_argument("--cloud-provider", default="none", help="Cloud provider the application was created with.")
    parser.add_argument("--no-doctor", action="store_true", help="Skip the native project doctor step.")
    parser.add_argument(
        "--smoke-writes",
        action="store_true",
        help="Also create and read smoke canonical records through the CLI (disposable authorities only).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        result = validate_existing_adopter(
            args.target.resolve(),
            host_root=args.host_root.resolve(),
            project_id=args.project_id,
            profile=args.profile,
            cloud_provider=args.cloud_provider,
            run_doctor_check=not args.no_doctor,
            run_smoke_checks=args.smoke_writes,
        )
    except Exception as exc:  # intentional-catch: CLI boundary, report and return non-zero
        print(f"clean_adopter_validation failed before validation: {exc}", file=sys.stderr)
        return 2
    print(result.render())
    return result.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
