"""Tests for the Windows-native commit governance preflight."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from types import SimpleNamespace

from click.testing import CliRunner

REPO_ROOT = Path(__file__).resolve().parents[3]

from groundtruth_kb import cli  # noqa: E402
from groundtruth_kb.governance import commit_preflight  # noqa: E402
from groundtruth_kb.governance.preflight_evidence import PreflightCheck, PreflightEvidence  # noqa: E402


def _completed(command: list[str], returncode: int = 0, stdout: str = "[PASS] ok\n", stderr: str = ""):
    return subprocess.CompletedProcess(command, returncode, stdout=stdout, stderr=stderr)


def test_commit_preflight_runs_bash_hook_checks_in_order_without_ps1(monkeypatch, tmp_path: Path) -> None:
    calls: list[list[str]] = []

    def fake_run(command, **kwargs):  # noqa: ANN001
        calls.append(list(command))
        if command[:3] == ["git", "diff", "--cached"]:
            return _completed(list(command), stdout="")
        return _completed(list(command))

    monkeypatch.setattr(commit_preflight.subprocess, "run", fake_run)

    evidence = commit_preflight.run_commit_preflight(tmp_path, python_bin="python")

    assert evidence.status.value == "passed"
    assert [check.name for check in evidence.checks] == [
        "secret-scan",
        "ruff-format",
        "commit-pathspec-safety",
        "projection-drift",
        "powershell-syntax",
    ]
    assert calls[:4] == [
        ["python", "scripts/scan_secrets.py", "--staged"],
        ["python", "scripts/check_ruff_format.py", "--staged"],
        [
            "python",
            "scripts/check_commit_pathspec_safety.py",
            "--staged",
        ],
        ["python", "scripts/check_projection_drift.py", "--staged"],
    ]
    assert evidence.checks[-1].summary == "no staged PowerShell files"


def test_commit_preflight_records_hard_failure(monkeypatch, tmp_path: Path) -> None:
    def fake_run(command, **kwargs):  # noqa: ANN001
        if command[1:2] == ["scripts/check_ruff_format.py"]:
            return _completed(list(command), returncode=1, stdout="[FAIL] ruff format\n")
        if command[:3] == ["git", "diff", "--cached"]:
            return _completed(list(command), stdout="")
        return _completed(list(command))

    monkeypatch.setattr(commit_preflight.subprocess, "run", fake_run)

    evidence = commit_preflight.run_commit_preflight(tmp_path, python_bin="python")

    assert evidence.status.value == "failed"
    assert commit_preflight.preflight_exit_code(evidence) == 1
    failed = next(check for check in evidence.checks if check.name == "ruff-format")
    assert failed.blocks_release is True
    assert failed.evidence["returncode"] == 1


def test_commit_preflight_runs_powershell_parser_for_staged_ps1(monkeypatch, tmp_path: Path) -> None:
    calls: list[list[str]] = []

    def fake_run(command, **kwargs):  # noqa: ANN001
        calls.append(list(command))
        if command[:3] == ["git", "diff", "--cached"]:
            return _completed(list(command), stdout=".githooks/pre-commit.ps1\n")
        return _completed(list(command))

    monkeypatch.setattr(commit_preflight.subprocess, "run", fake_run)

    evidence = commit_preflight.run_commit_preflight(tmp_path, python_bin="python", powershell_bin="pwsh")

    assert evidence.status.value == "passed"
    assert calls[-1][:4] == ["pwsh", "-NoProfile", "-ExecutionPolicy", "Bypass"]
    assert calls[-1][-1].replace("\\", "/").endswith(".githooks/pre-commit-ps1-parse.ps1")


def test_commit_preflight_cli_emits_json_and_exit_code(monkeypatch, tmp_path: Path) -> None:
    evidence = PreflightEvidence.from_checks(
        [PreflightCheck.passed("secret-scan", summary="ok")],
        evidence_path=tmp_path / "commit-preflight.json",
        generated_at="2026-06-29T00:00:00Z",
    )

    def fake_run(project_root, **kwargs):  # noqa: ANN001
        assert project_root == tmp_path
        return evidence

    monkeypatch.setattr(cli, "_resolve_config", lambda ctx: SimpleNamespace(project_root=tmp_path))
    monkeypatch.setattr(commit_preflight, "run_commit_preflight", fake_run)

    result = CliRunner().invoke(
        cli.main,
        ["commit", "preflight", "--json", "--evidence-out", str(tmp_path / "commit-preflight.json")],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["status"] == "passed"
    assert (tmp_path / "commit-preflight.json").exists()


def test_windows_wrappers_delegate_to_commit_preflight_and_prefer_project_venv() -> None:
    cmd_text = (REPO_ROOT / ".githooks" / "pre-commit.cmd").read_text(encoding="utf-8")
    ps1_text = (REPO_ROOT / ".githooks" / "pre-commit.ps1").read_text(encoding="utf-8")

    assert "-m groundtruth_kb.cli commit preflight" in cmd_text
    assert "-m groundtruth_kb.cli commit preflight" in ps1_text
    assert cmd_text.index("groundtruth-kb\\.venv\\Scripts\\python.exe") < cmd_text.index("%PYTHON%")
    assert ps1_text.index("groundtruth-kb/.venv/Scripts/python.exe") < ps1_text.index("$env:PYTHON")


def test_windows_wrappers_delegate_to_commit_preflight_command() -> None:
    cmd_wrapper = (REPO_ROOT / ".githooks" / "pre-commit.cmd").read_text(encoding="utf-8")
    ps1_wrapper = (REPO_ROOT / ".githooks" / "pre-commit.ps1").read_text(encoding="utf-8")

    assert "commit preflight" in cmd_wrapper
    assert "commit preflight" in ps1_wrapper
    for direct_script in (
        "scan_secrets.py",
        "check_ruff_format.py",
        "check_protected_commit_authorization.py",
        "pre-commit-ps1-parse.ps1",
    ):
        assert direct_script not in cmd_wrapper
        assert direct_script not in ps1_wrapper
