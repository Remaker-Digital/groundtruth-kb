"""Read-only push readiness diagnostic."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

from groundtruth_kb.governance.preflight_evidence import CheckSeverity, PreflightCheck, PreflightEvidence


def run_push_readiness(
    project_root: Path,
    *,
    remote: str = "origin",
    hostname: str = "github.com",
    timeout_seconds: int = 15,
    evidence_path: str | Path | None = None,
) -> PreflightEvidence:
    """Inspect non-interactive push readiness without mutating credentials or remotes."""
    root = project_root.resolve()
    checks = [
        _credential_helper_check(root, timeout_seconds=timeout_seconds),
        _gh_auth_check(root, hostname=hostname, timeout_seconds=timeout_seconds),
        _remote_reachability_check(root, remote=remote, timeout_seconds=timeout_seconds),
        _prompt_risk_check(root, timeout_seconds=timeout_seconds),
    ]
    return PreflightEvidence.from_checks(checks, evidence_path=evidence_path)


def readiness_exit_code(evidence: PreflightEvidence) -> int:
    """Return process exit code for a readiness packet."""
    return 1 if evidence.summary_counts["hard_failures"] or evidence.summary_counts["hard_inconclusive"] else 0


def _credential_helper_check(project_root: Path, *, timeout_seconds: int) -> PreflightCheck:
    result = _run_command(project_root, ("git", "config", "--get-all", "credential.helper"), timeout_seconds)
    helpers = [line.strip() for line in result.stdout.splitlines() if line.strip()] if result is not None else []
    evidence = _result_evidence(result, ["git", "config", "--get-all", "credential.helper"])
    evidence["helpers"] = helpers
    if result is None:
        return PreflightCheck.inconclusive(
            "credential-helper",
            severity=CheckSeverity.HARD,
            summary="credential helper check could not run",
            evidence=evidence,
        )
    if result.returncode not in (0, 1):
        return PreflightCheck.failed(
            "credential-helper",
            severity=CheckSeverity.HARD,
            summary="credential helper check failed",
            detail=_combined_output(result),
            evidence=evidence,
        )
    if not helpers:
        return PreflightCheck.failed(
            "credential-helper",
            severity=CheckSeverity.HARD,
            summary="no Git credential helper configured",
            evidence=evidence,
        )
    if len(helpers) > 1:
        return PreflightCheck.failed(
            "credential-helper",
            severity=CheckSeverity.ADVISORY,
            summary="multiple Git credential helpers configured",
            evidence=evidence,
        )
    return PreflightCheck.passed(
        "credential-helper",
        summary=f"Git credential helper configured: {helpers[0]}",
        evidence=evidence,
    )


def _gh_auth_check(project_root: Path, *, hostname: str, timeout_seconds: int) -> PreflightCheck:
    gh_path = shutil.which("gh")
    command = ["gh", "auth", "status", "--hostname", hostname]
    if gh_path is None:
        return PreflightCheck.failed(
            "github-cli-auth",
            severity=CheckSeverity.HARD,
            summary="GitHub CLI is unavailable",
            evidence={"command": command, "hostname": hostname},
        )
    result = _run_command(project_root, tuple(command), timeout_seconds)
    evidence = _result_evidence(result, command)
    evidence["hostname"] = hostname
    evidence["gh_path"] = gh_path
    if result is not None and result.returncode == 0:
        return PreflightCheck.passed(
            "github-cli-auth",
            summary=f"GitHub CLI auth reports ready for {hostname}",
            evidence=evidence,
        )
    return PreflightCheck.failed(
        "github-cli-auth",
        severity=CheckSeverity.HARD,
        summary=f"GitHub CLI auth is not ready for {hostname}",
        detail=_combined_output(result) if result is not None else "command could not run",
        evidence=evidence,
    )


def _remote_reachability_check(project_root: Path, *, remote: str, timeout_seconds: int) -> PreflightCheck:
    remote_url_result = _run_command(project_root, ("git", "remote", "get-url", remote), timeout_seconds)
    remote_url = remote_url_result.stdout.strip() if remote_url_result is not None else ""
    if remote_url_result is None or remote_url_result.returncode != 0 or not remote_url:
        return PreflightCheck.failed(
            "remote-reachability",
            severity=CheckSeverity.HARD,
            summary=f"remote {remote!r} is not configured",
            detail=_combined_output(remote_url_result) if remote_url_result is not None else "command could not run",
            evidence=_result_evidence(remote_url_result, ["git", "remote", "get-url", remote]),
        )

    command = ["git", "ls-remote", "--exit-code", remote, "HEAD"]
    result = _run_command(
        project_root,
        tuple(command),
        timeout_seconds,
        extra_env={"GIT_TERMINAL_PROMPT": "0", "GCM_INTERACTIVE": "never"},
    )
    evidence = _result_evidence(result, command)
    evidence["remote"] = remote
    evidence["remote_url"] = remote_url
    evidence["non_interactive_env"] = {"GIT_TERMINAL_PROMPT": "0", "GCM_INTERACTIVE": "never"}
    if result is not None and result.returncode == 0:
        return PreflightCheck.passed(
            "remote-reachability",
            summary=f"remote {remote!r} is reachable without interactive prompts",
            evidence=evidence,
        )
    return PreflightCheck.failed(
        "remote-reachability",
        severity=CheckSeverity.HARD,
        summary=f"remote {remote!r} is not reachable non-interactively",
        detail=_combined_output(result) if result is not None else "command could not run",
        evidence=evidence,
    )


def _prompt_risk_check(project_root: Path, *, timeout_seconds: int) -> PreflightCheck:
    result = _run_command(project_root, ("git", "config", "--get-all", "credential.helper"), timeout_seconds)
    helpers = (
        [line.strip().lower() for line in result.stdout.splitlines() if line.strip()] if result is not None else []
    )
    gui_helpers = [
        helper for helper in helpers if "manager" in helper or "wincred" in helper or "osxkeychain" in helper
    ]
    evidence = _result_evidence(result, ["git", "config", "--get-all", "credential.helper"])
    evidence["helpers"] = helpers
    evidence["gui_capable_helpers"] = gui_helpers
    if gui_helpers:
        return PreflightCheck.failed(
            "interactive-prompt-risk",
            severity=CheckSeverity.ADVISORY,
            summary="credential helper may open a GUI prompt if auth is stale",
            evidence=evidence,
        )
    return PreflightCheck.passed(
        "interactive-prompt-risk",
        severity=CheckSeverity.ADVISORY,
        summary="no GUI credential helper detected",
        evidence=evidence,
    )


def _run_command(
    project_root: Path,
    command: tuple[str, ...],
    timeout_seconds: int,
    *,
    extra_env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str] | None:
    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)
    try:
        return subprocess.run(
            list(command),
            cwd=project_root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_seconds,
            check=False,
            env=env,
        )
    except (OSError, subprocess.SubprocessError):
        return None


def _result_evidence(result: subprocess.CompletedProcess[str] | None, command: list[str]) -> dict[str, object]:
    if result is None:
        return {"command": command, "returncode": None, "stdout": "", "stderr": ""}
    return {
        "command": command,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def _combined_output(result: subprocess.CompletedProcess[str] | None) -> str:
    if result is None:
        return ""
    return "\n".join(part for part in (result.stdout.strip(), result.stderr.strip()) if part)
