"""Windows-native push governance preflight orchestration."""

from __future__ import annotations

import subprocess
import sys
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from groundtruth_kb.governance.preflight_evidence import CheckSeverity, PreflightCheck, PreflightEvidence

ZERO_SHA = "0" * 40
DEFAULT_BASE_CANDIDATES = (
    "refs/remotes/origin/HEAD",
    "refs/remotes/origin/main",
    "refs/remotes/origin/develop",
    "main",
    "develop",
)


@dataclass(frozen=True)
class RefUpdate:
    """One Git pre-push stdin tuple."""

    local_ref: str
    local_sha: str
    remote_ref: str
    remote_sha: str


def parse_pre_push_stdin(text: str) -> tuple[RefUpdate, ...]:
    """Parse Git pre-push stdin into ref update records."""
    updates: list[RefUpdate] = []
    for line_no, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) != 4:
            raise ValueError(f"pre-push stdin line {line_no} has {len(parts)} fields; expected 4")
        updates.append(RefUpdate(*parts))
    return tuple(updates)


def run_push_preflight(
    project_root: Path,
    stdin_text: str,
    *,
    python_bin: str | None = None,
    evidence_path: str | Path | None = None,
) -> PreflightEvidence:
    """Run redacted secret scans for Git pre-push ref updates."""
    root = project_root.resolve()
    try:
        updates = parse_pre_push_stdin(stdin_text)
    except ValueError as exc:
        return PreflightEvidence.from_checks(
            [
                PreflightCheck.failed(
                    "pre-push-stdin",
                    severity=CheckSeverity.HARD,
                    summary="invalid Git pre-push stdin",
                    detail=str(exc),
                )
            ],
            evidence_path=evidence_path,
        )

    python_cmd = python_bin or sys.executable
    checks: list[PreflightCheck] = []
    if not updates:
        checks.append(
            PreflightCheck.passed(
                "pre-push-stdin",
                summary="no refs supplied on stdin",
                evidence={"updates": []},
            )
        )
        return PreflightEvidence.from_checks(checks, evidence_path=evidence_path)

    for index, update in enumerate(updates, start=1):
        checks.extend(_checks_for_update(root, update, python_cmd=python_cmd, index=index))
    return PreflightEvidence.from_checks(checks, evidence_path=evidence_path)


def preflight_exit_code(evidence: PreflightEvidence) -> int:
    """Return process exit code for an evidence packet."""
    return 1 if evidence.summary_counts["hard_failures"] or evidence.summary_counts["hard_inconclusive"] else 0


def _checks_for_update(project_root: Path, update: RefUpdate, *, python_cmd: str, index: int) -> list[PreflightCheck]:
    check_name = f"pre-push-ref-{index}"
    update_evidence = {
        "local_ref": update.local_ref,
        "local_sha": update.local_sha,
        "remote_ref": update.remote_ref,
        "remote_sha": update.remote_sha,
    }
    if _is_zero_sha(update.local_sha):
        return [
            PreflightCheck.passed(
                check_name,
                summary=f"skipped deleted ref {update.remote_ref}",
                evidence=update_evidence,
            )
        ]

    if _is_zero_sha(update.remote_sha):
        base_sha, base_evidence = _merge_base_for_new_ref(project_root, update.local_ref, update.local_sha)
        evidence = {**update_evidence, **base_evidence}
        if not base_sha:
            return [
                PreflightCheck.failed(
                    check_name,
                    severity=CheckSeverity.HARD,
                    summary="cannot determine safe base for new ref",
                    detail=(
                        f"Could not determine a safe base for {update.local_ref} -> {update.remote_ref}. "
                        "Run a reviewed redacted tracked scan before pushing."
                    ),
                    evidence=evidence,
                )
            ]
        range_spec = f"{base_sha}..{update.local_sha}"
    else:
        range_spec = f"{update.remote_sha}..{update.local_sha}"

    return [_run_secret_scan(project_root, python_cmd, range_spec, check_name, update_evidence)]


def _merge_base_for_new_ref(project_root: Path, local_ref: str, local_sha: str) -> tuple[str | None, dict[str, object]]:
    candidates = (f"{local_ref}@{{upstream}}", *DEFAULT_BASE_CANDIDATES)
    attempted: list[dict[str, object]] = []
    for candidate in candidates:
        resolved = _resolve_candidate(project_root, candidate)
        attempted.append({"candidate": candidate, "resolved": resolved})
        if resolved is None:
            continue
        result = _run_git(project_root, ("merge-base", resolved, local_sha))
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip().splitlines()[0], {"base_candidate": candidate, "attempted_bases": attempted}
        attempted[-1]["merge_base_returncode"] = result.returncode
        attempted[-1]["merge_base_output"] = _combined_output(result)
    return None, {"attempted_bases": attempted}


def _resolve_candidate(project_root: Path, candidate: str) -> str | None:
    result = _run_git(project_root, ("rev-parse", "--verify", "--quiet", candidate))
    if result.returncode != 0:
        return None
    resolved = result.stdout.strip().splitlines()
    return resolved[0] if resolved else candidate


def _run_secret_scan(
    project_root: Path,
    python_cmd: str,
    range_spec: str,
    check_name: str,
    update_evidence: dict[str, str],
) -> PreflightCheck:
    command = (
        python_cmd,
        "-m",
        "groundtruth_kb",
        "secrets",
        "scan",
        "--range",
        range_spec,
        "--redacted",
        "--fail-on",
        "verified-provider",
    )
    try:
        result = subprocess.run(
            list(command),
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
            check_name,
            severity=CheckSeverity.HARD,
            summary="secret scan could not run",
            detail=str(exc),
            evidence={**update_evidence, "command": list(command), "range": range_spec},
        )
    evidence = {
        **update_evidence,
        "command": list(command),
        "range": range_spec,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }
    if result.returncode == 0:
        return PreflightCheck.passed(
            check_name,
            summary=f"redacted secret scan passed for {range_spec}",
            evidence=evidence,
        )
    return PreflightCheck.failed(
        check_name,
        severity=CheckSeverity.HARD,
        summary=f"redacted secret scan failed for {range_spec}",
        detail=_combined_output(result),
        evidence=evidence,
    )


def _run_git(project_root: Path, args: Iterable[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=project_root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
        check=False,
    )


def _is_zero_sha(value: str) -> bool:
    return value == ZERO_SHA


def _combined_output(result: subprocess.CompletedProcess[str]) -> str:
    return "\n".join(part for part in (result.stdout.strip(), result.stderr.strip()) if part)
