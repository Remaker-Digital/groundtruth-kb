"""Partial Slice 1 deployability preservation checks for adopter roots.

This module intentionally implements only the Slice 1 coverage approved by the
bridge thread. A PASS report from this module is not full deployability
clearance for irreversible adopter migration, cutover, extraction, deletion, or
restructuring work. Full clearance requires the deferred proofs named in
``deferred_specs`` to exist and pass in later slices.
"""

from __future__ import annotations

import configparser
import json
import os
import subprocess
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, cast

Status = Literal["PASS", "FAIL", "SKIP", "WARN"]

COVERAGE = "partial"
COVERED_SPECS = [
    "SPEC-DEPLOY-RC-GATE-PYTHON-3-12-001",
    "SPEC-DEPLOY-FRONTEND-BUNDLES-001",
    "SPEC-DEPLOY-EVIDENCE-FRESHNESS-001",
]
DEFERRED_SPECS = [
    "SPEC-DEPLOY-SOURCE-BUILD-001",
    "SPEC-DEPLOY-CONTAINER-BUILD-001",
    "SPEC-DEPLOY-WORKFLOW-INPUTS-001",
    "SPEC-DEPLOY-MAINTAIN-ENHANCE-PATH-001",
]
DEFERRED_PROOFS = {
    "SPEC-DEPLOY-SOURCE-BUILD-001": "gtkb-agent-red-deployability-preservation-gate-slice-2-source-container",
    "SPEC-DEPLOY-CONTAINER-BUILD-001": "gtkb-agent-red-deployability-preservation-gate-slice-2-source-container",
    "SPEC-DEPLOY-WORKFLOW-INPUTS-001": "gtkb-agent-red-deployability-preservation-gate-slice-3-workflow-maintain",
    "SPEC-DEPLOY-MAINTAIN-ENHANCE-PATH-001": "gtkb-agent-red-deployability-preservation-gate-slice-3-workflow-maintain",
}
PARTIAL_CLEARANCE_WARNING = (
    "Slice 1 coverage is partial. PASS means only the RC-gate, Python gate, "
    "frontend bundle metadata, and test-collection signal passed; it is not "
    "full deployability clearance."
)


@dataclass(frozen=True)
class DeployabilityCheckResult:
    name: str
    status: Status
    detail: str

    def as_dict(self) -> dict[str, str]:
        return {"name": self.name, "status": self.status, "detail": self.detail}


@dataclass(frozen=True)
class DeployabilityReport:
    coverage: str
    covered_specs: list[str]
    deferred_specs: list[str]
    results: list[DeployabilityCheckResult]

    @property
    def summary_status(self) -> Status:
        if any(result.status == "FAIL" for result in self.results):
            return "FAIL"
        if any(result.status == "WARN" for result in self.results):
            return "WARN"
        return "PASS"

    def has_failures(self) -> bool:
        return self.summary_status == "FAIL"

    def as_dict(self) -> dict[str, Any]:
        return {
            "coverage": self.coverage,
            "full_clearance": False,
            "summary_status": self.summary_status,
            "covered_specs": list(self.covered_specs),
            "deferred_specs": list(self.deferred_specs),
            "deferred_proofs": dict(DEFERRED_PROOFS),
            "partial_clearance_warning": PARTIAL_CLEARANCE_WARNING,
            "results": [result.as_dict() for result in self.results],
        }


def check_adopter_deployability(adopter_root: Path | str) -> DeployabilityReport:
    root = Path(adopter_root).resolve()
    return DeployabilityReport(
        coverage=COVERAGE,
        covered_specs=list(COVERED_SPECS),
        deferred_specs=list(DEFERRED_SPECS),
        results=[
            check_rc_gate(root),
            check_python_gate(root),
            check_frontend_build_path(root),
            check_test_suite_collects(root),
        ],
    )


def check_rc_gate(adopter_root: Path) -> DeployabilityCheckResult:
    if not adopter_root.exists() or not adopter_root.is_dir():
        return DeployabilityCheckResult("rc_gate", "FAIL", f"adopter root does not exist: {adopter_root}")

    skill = _first_existing(
        adopter_root,
        [
            ".codex/skills/release-candidate-gate/SKILL.md",
            ".claude/skills/release-candidate-gate/SKILL.md",
            ".agents/skills/release-candidate-gate/SKILL.md",
        ],
    )
    if skill is None:
        return DeployabilityCheckResult("rc_gate", "FAIL", "release-candidate-gate skill file not found")

    script = _first_existing(
        adopter_root,
        [
            "scripts/release_candidate_gate.py",
            "scripts/agent_red_release_candidate_gate.py",
        ],
    )
    if script is None:
        return DeployabilityCheckResult("rc_gate", "FAIL", "release-candidate gate script not found")

    completed = _run(
        [sys.executable, str(script), "--dry-run"],
        cwd=adopter_root,
        timeout_seconds=30,
    )
    if completed.returncode != 0:
        return DeployabilityCheckResult(
            "rc_gate",
            "FAIL",
            f"dry-run failed with exit {completed.returncode}: {_combined_output(completed)}",
        )
    return DeployabilityCheckResult(
        "rc_gate",
        "PASS",
        "release-candidate skill "
        f"{skill.relative_to(adopter_root)} and dry-run script {script.relative_to(adopter_root)} passed",
    )


def check_python_gate(adopter_root: Path) -> DeployabilityCheckResult:
    requirement = _python_requirement(adopter_root)
    if requirement is None:
        return DeployabilityCheckResult(
            "python_gate",
            "FAIL",
            "no Python version declaration found in pyproject.toml, setup.cfg, or .python-version",
        )
    if _requirement_allows_python_312(requirement):
        return DeployabilityCheckResult("python_gate", "PASS", f"Python declaration allows 3.12: {requirement}")
    return DeployabilityCheckResult("python_gate", "FAIL", f"Python declaration does not allow 3.12: {requirement}")


def check_frontend_build_path(adopter_root: Path) -> DeployabilityCheckResult:
    package_files = _frontend_package_files(adopter_root)
    if not package_files:
        return DeployabilityCheckResult("frontend_build", "SKIP", "no frontend package metadata found")

    missing_build: list[str] = []
    invalid_json: list[str] = []
    for package_file in package_files:
        try:
            data = json.loads(package_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            invalid_json.append(f"{package_file.relative_to(adopter_root)} ({exc.msg})")
            continue
        scripts = data.get("scripts")
        if not isinstance(scripts, dict) or not str(scripts.get("build") or "").strip():
            missing_build.append(str(package_file.relative_to(adopter_root)))

    if invalid_json:
        return DeployabilityCheckResult("frontend_build", "FAIL", f"invalid package.json: {', '.join(invalid_json)}")
    if missing_build:
        return DeployabilityCheckResult(
            "frontend_build",
            "FAIL",
            f"frontend package metadata missing build scripts: {', '.join(missing_build)}",
        )
    paths = ", ".join(str(path.relative_to(adopter_root)) for path in package_files)
    return DeployabilityCheckResult("frontend_build", "PASS", f"frontend build scripts present: {paths}")


def check_test_suite_collects(adopter_root: Path) -> DeployabilityCheckResult:
    if not adopter_root.exists() or not adopter_root.is_dir():
        return DeployabilityCheckResult("test_collection", "FAIL", f"adopter root does not exist: {adopter_root}")

    completed = _run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q"],
        cwd=adopter_root,
        timeout_seconds=45,
    )
    if completed.returncode != 0:
        return DeployabilityCheckResult(
            "test_collection",
            "FAIL",
            f"pytest collection failed with exit {completed.returncode}: {_combined_output(completed)}",
        )
    return DeployabilityCheckResult("test_collection", "PASS", "pytest collection completed without errors")


def _first_existing(root: Path, relative_paths: list[str]) -> Path | None:
    for relative_path in relative_paths:
        candidate = root / relative_path
        if candidate.is_file():
            return candidate
    return None


def _python_requirement(root: Path) -> str | None:
    pyproject = root / "pyproject.toml"
    if pyproject.is_file():
        try:
            data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
        except tomllib.TOMLDecodeError:
            return None
        project = data.get("project")
        if isinstance(project, dict) and isinstance(project.get("requires-python"), str):
            return str(project["requires-python"])
        poetry = data.get("tool", {}).get("poetry", {}) if isinstance(data.get("tool"), dict) else {}
        dependencies = poetry.get("dependencies") if isinstance(poetry, dict) else None
        if isinstance(dependencies, dict) and isinstance(dependencies.get("python"), str):
            return str(dependencies["python"])

    setup_cfg = root / "setup.cfg"
    if setup_cfg.is_file():
        parser = configparser.ConfigParser()
        parser.read(setup_cfg, encoding="utf-8")
        if parser.has_option("options", "python_requires"):
            return parser.get("options", "python_requires")

    python_version = root / ".python-version"
    if python_version.is_file():
        value = python_version.read_text(encoding="utf-8").strip()
        return value or None
    return None


def _requirement_allows_python_312(requirement: str) -> bool:
    normalized = requirement.strip()
    if not normalized:
        return False
    if "3.12" in normalized:
        return True
    try:
        from packaging.specifiers import SpecifierSet
        from packaging.version import Version
    except ImportError:
        return normalized in {">=3.11", ">=3.10", ">=3.9"} or normalized.startswith(">=3.11")
    try:
        return Version("3.12.0") in SpecifierSet(normalized)
    except Exception:  # intentional-catch: quality gate waiver
        return False


def _frontend_package_files(root: Path) -> list[Path]:
    candidates = [
        root / "package.json",
        root / "frontend" / "package.json",
        root / "admin" / "package.json",
        root / "widget" / "package.json",
        root / "website" / "package.json",
        root / "web" / "package.json",
    ]
    return [path for path in candidates if path.is_file()]


def _run(command: list[str], *, cwd: Path, timeout_seconds: int) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.setdefault("PYTHONIOENCODING", "utf-8")
    try:
        return subprocess.run(
            command,
            cwd=cwd,
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        stdout_str = (
            exc.stdout.decode("utf-8", errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        )
        stderr_str = (
            exc.stderr.decode("utf-8", errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "timeout")
        )
        return subprocess.CompletedProcess(command, 124, stdout=stdout_str, stderr=stderr_str)


def _combined_output(completed: subprocess.CompletedProcess[str]) -> str:
    combined = "\n".join(part.strip() for part in (completed.stdout, completed.stderr) if part and part.strip())
    if not combined:
        return "no output"
    return combined[:1000]
