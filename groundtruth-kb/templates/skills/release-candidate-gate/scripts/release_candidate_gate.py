#!/usr/bin/env python3
"""Non-deploying release-candidate gate template for GT-KB adopters."""

from __future__ import annotations

import argparse
import os
import shlex
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

ADOPTER_PYTHON_SCAN_TARGETS = "{{adopter_python_scan_targets}}"
ADOPTER_SECURITY_SCAN_TARGET = "{{adopter_security_scan_target}}"
ADOPTER_TARGETED_TESTS = "{{adopter_targeted_tests}}"
ADOPTER_FRONTEND_PROJECTS = "{{adopter_frontend_projects}}"
ADOPTER_GOVERNANCE_CHECKS = "{{adopter_governance_checks}}"
ADOPTER_REQUIREMENTS_FILE = "{{adopter_requirements_file}}"


class GateFailure(RuntimeError):
    """Raised when one or more release gates fail."""


@dataclass(frozen=True)
class GateConfig:
    python_scan_targets: list[str]
    security_scan_target: str
    targeted_tests: list[str]
    frontend_projects: list[str]
    governance_commands: list[list[str]]
    requirements_file: str


def _template_value(value: str, default: str) -> str:
    stripped = value.strip()
    if not stripped or (stripped.startswith("{{") and stripped.endswith("}}")):
        return default
    return stripped


def _words(value: str, default: str) -> list[str]:
    return shlex.split(_template_value(value, default))


def _semicolon_items(value: str, default: str = "") -> list[str]:
    raw = _template_value(value, default)
    return [item.strip() for item in raw.split(";") if item.strip()]


def _governance_commands() -> list[list[str]]:
    items = _semicolon_items(
        ADOPTER_GOVERNANCE_CHECKS,
        "python -m groundtruth_kb project doctor .",
    )
    return [shlex.split(item) for item in items]


def _config_from_templates() -> GateConfig:
    return GateConfig(
        python_scan_targets=_words(ADOPTER_PYTHON_SCAN_TARGETS, "src tests"),
        security_scan_target=_template_value(ADOPTER_SECURITY_SCAN_TARGET, "src"),
        targeted_tests=_words(ADOPTER_TARGETED_TESTS, "tests"),
        frontend_projects=_semicolon_items(ADOPTER_FRONTEND_PROJECTS),
        governance_commands=_governance_commands(),
        requirements_file=_template_value(ADOPTER_REQUIREMENTS_FILE, "requirements.txt"),
    )


def _run(command: list[str], *, timeout: int = 300, env: dict[str, str] | None = None) -> None:
    started = time.time()
    print(f"\n$ {' '.join(command)}", flush=True)
    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        env=env,
    )
    elapsed = time.time() - started
    if result.returncode != 0:
        raise GateFailure(f"Command failed after {elapsed:.1f}s: {' '.join(command)}")
    print(f"PASS ({elapsed:.1f}s)")


def _check_python_version(required: str | None) -> None:
    if not required:
        return
    actual = f"{sys.version_info.major}.{sys.version_info.minor}"
    if actual != required:
        raise GateFailure(f"Python {required} required for release gate; running {actual}")
    print(f"PASS Python version: {actual}")


def _secret_scan() -> None:
    _run(
        [
            sys.executable,
            "-m",
            "groundtruth_kb",
            "secrets",
            "scan",
            "--tracked",
            "--redacted",
            "--fail-on",
            "verified-provider",
        ],
        timeout=180,
    )


def _dependency_audit(config: GateConfig) -> None:
    requirements = PROJECT_ROOT / config.requirements_file
    if not requirements.is_file():
        raise GateFailure(f"Requirements file is missing: {config.requirements_file}")
    _run([sys.executable, "-m", "pip_audit", "-r", config.requirements_file], timeout=180)


def _security_scan(config: GateConfig) -> None:
    _run([sys.executable, "-m", "bandit", "-r", config.security_scan_target, "-ll"], timeout=180)


def _python_quality(config: GateConfig) -> None:
    _run([sys.executable, "-m", "ruff", "check", *config.python_scan_targets, "--select", "E,F"], timeout=120)


def _targeted_regressions(config: GateConfig) -> None:
    _run([sys.executable, "-m", "pytest", *config.targeted_tests, "-q", "--tb=short"], timeout=300)


def _governance_adoption(config: GateConfig) -> None:
    for command in config.governance_commands:
        _run(command, timeout=180)


def _python_gates(config: GateConfig) -> None:
    _secret_scan()
    _dependency_audit(config)
    _security_scan(config)
    _python_quality(config)
    _targeted_regressions(config)
    _governance_adoption(config)


def _frontend_gates(config: GateConfig) -> None:
    if not config.frontend_projects:
        print("PASS frontend builds (no frontend projects configured)")
        return
    npm = shutil.which("npm.cmd" if sys.platform == "win32" else "npm") or shutil.which("npm")
    if not npm:
        raise GateFailure("npm executable not found on PATH")
    frontend_env = os.environ.copy()
    frontend_env["npm_config_ignore_scripts"] = "true"
    for project in config.frontend_projects:
        _run([npm, "--prefix", project, "test"], timeout=180)
        _run([npm, "--prefix", project, "run", "build"], timeout=240, env=frontend_env)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run non-deploying release-candidate gates.")
    parser.add_argument("--require-python", default="", help="Require a Python major.minor, for example 3.12.")
    parser.add_argument("--skip-python", action="store_true", help="Skip Python/security/governance gates.")
    parser.add_argument("--skip-frontend", action="store_true", help="Skip frontend gates.")
    parser.add_argument("--include-frontend", action="store_true", help="Run configured frontend gates.")
    args = parser.parse_args()

    config = _config_from_templates()
    try:
        _check_python_version(args.require_python or None)
        if not args.skip_python:
            _python_gates(config)
        if args.include_frontend and not args.skip_frontend:
            _frontend_gates(config)
    except (GateFailure, subprocess.TimeoutExpired) as exc:
        print(f"\nRELEASE GATE: FAIL - {exc}", file=sys.stderr)
        return 1

    print("\nRELEASE GATE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
