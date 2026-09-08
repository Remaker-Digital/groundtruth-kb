"""Windows-native commit governance preflight orchestration."""

from __future__ import annotations

import shutil
import subprocess
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from groundtruth_kb.governance.preflight_evidence import (
    CheckSeverity,
    PreflightCheck,
    PreflightEvidence,
)


@dataclass(frozen=True)
class CommandSpec:
    """One staged governance command mirrored from ``.githooks/pre-commit``."""

    name: str
    command: tuple[str, ...]


def commit_preflight_commands(python_bin: str) -> tuple[CommandSpec, ...]:
    """Return the Python checks in the same order as the Bash pre-commit hook."""
    return (
        CommandSpec("secret-scan", (python_bin, "scripts/scan_secrets.py", "--staged")),
        CommandSpec(
            "dev-environment-inventory-drift",
            (
                python_bin,
                "scripts/check_dev_environment_inventory_drift.py",
                "--staged",
                "--allow-review-evidence",
            ),
        ),
        CommandSpec(
            "narrative-artifact-evidence",
            (python_bin, "scripts/check_narrative_artifact_evidence.py", "--staged"),
        ),
        CommandSpec("ruff-format", (python_bin, "scripts/check_ruff_format.py", "--staged")),
    )


def run_commit_preflight(
    project_root: Path,
    *,
    python_bin: str | None = None,
    powershell_bin: str | None = None,
    evidence_path: str | Path | None = None,
) -> PreflightEvidence:
    """Run staged commit governance checks and return structured evidence."""
    root = project_root.resolve()
    python_cmd = python_bin or sys.executable
    checks = [_run_command(root, spec) for spec in commit_preflight_commands(python_cmd)]
    checks.append(_run_powershell_syntax_check(root, powershell_bin=powershell_bin))
    return PreflightEvidence.from_checks(checks, evidence_path=evidence_path)


def preflight_exit_code(evidence: PreflightEvidence) -> int:
    """Return process exit code for an evidence packet."""
    return 1 if evidence.summary_counts["hard_failures"] or evidence.summary_counts["hard_inconclusive"] else 0


def _run_command(project_root: Path, spec: CommandSpec) -> PreflightCheck:
    try:
        result = subprocess.run(
            list(spec.command),
            cwd=project_root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=300,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return PreflightCheck.inconclusive(
            spec.name,
            severity=CheckSeverity.HARD,
            summary="command could not run",
            detail=str(exc),
            evidence={"command": list(spec.command)},
        )
    return _check_from_result(spec.name, spec.command, result)


def _check_from_result(
    name: str,
    command: Sequence[str],
    result: subprocess.CompletedProcess[str],
) -> PreflightCheck:
    evidence = {
        "command": list(command),
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }
    if result.returncode == 0:
        return PreflightCheck.passed(
            name,
            summary=_first_output_line(result) or "passed",
            evidence=evidence,
        )
    return PreflightCheck.failed(
        name,
        summary=f"command exited {result.returncode}",
        detail=_combined_output(result),
        evidence=evidence,
    )


def _run_powershell_syntax_check(project_root: Path, *, powershell_bin: str | None) -> PreflightCheck:
    ps1_files, error = _staged_ps1_files(project_root)
    if error is not None:
        return PreflightCheck.inconclusive(
            "powershell-syntax",
            severity=CheckSeverity.HARD,
            summary="could not list staged PowerShell files",
            detail=error,
            evidence={"command": ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"]},
        )
    if not ps1_files:
        return PreflightCheck.passed(
            "powershell-syntax",
            summary="no staged PowerShell files",
            evidence={"staged_ps1_files": []},
        )
    shell = powershell_bin or _find_powershell()
    if shell is None:
        return PreflightCheck.passed(
            "powershell-syntax",
            summary="PowerShell unavailable; skipped per existing hook behavior",
            evidence={"staged_ps1_files": ps1_files},
        )
    command = (
        shell,
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(project_root / ".githooks" / "pre-commit-ps1-parse.ps1"),
    )
    return _run_command(project_root, CommandSpec("powershell-syntax", command))


def _staged_ps1_files(project_root: Path) -> tuple[list[str], str | None]:
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
            cwd=project_root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return [], str(exc)
    if result.returncode != 0:
        return [], _combined_output(result) or f"git diff exited {result.returncode}"
    return [line.strip() for line in result.stdout.splitlines() if line.strip().lower().endswith(".ps1")], None


def _find_powershell() -> str | None:
    for candidate in ("pwsh", "powershell.exe", "powershell"):
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    return None


def _combined_output(result: subprocess.CompletedProcess[str]) -> str:
    return "\n".join(part for part in (result.stdout.strip(), result.stderr.strip()) if part)


def _first_output_line(result: subprocess.CompletedProcess[str]) -> str:
    for line in _combined_output(result).splitlines():
        if line.strip():
            return line.strip()
    return ""
