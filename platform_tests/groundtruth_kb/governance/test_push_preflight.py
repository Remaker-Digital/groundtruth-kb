"""Tests for Windows-native push governance preflight."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

from click.testing import CliRunner

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "groundtruth-kb" / "src"))

from groundtruth_kb import cli  # noqa: E402
from groundtruth_kb.governance import push_preflight  # noqa: E402
from groundtruth_kb.governance.preflight_evidence import PreflightCheck, PreflightEvidence  # noqa: E402


def _completed(command: list[str], returncode: int = 0, stdout: str = "", stderr: str = ""):
    return subprocess.CompletedProcess(command, returncode, stdout=stdout, stderr=stderr)


def test_existing_branch_update_runs_redacted_range_scan(monkeypatch, tmp_path: Path) -> None:
    calls: list[list[str]] = []

    def fake_run(command, **kwargs):  # noqa: ANN001
        calls.append(list(command))
        return _completed(list(command), stdout="clean\n")

    monkeypatch.setattr(push_preflight.subprocess, "run", fake_run)

    evidence = push_preflight.run_push_preflight(
        tmp_path,
        "refs/heads/main aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa "
        "refs/heads/main bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb\n",
        python_bin="python",
    )

    assert evidence.status.value == "passed"
    assert calls == [
        [
            "python",
            "-m",
            "groundtruth_kb",
            "secrets",
            "scan",
            "--range",
            "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb..aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "--redacted",
            "--fail-on",
            "verified-provider",
        ]
    ]


def test_new_branch_uses_safe_merge_base_before_scan(monkeypatch, tmp_path: Path) -> None:
    calls: list[list[str]] = []

    def fake_run(command, **kwargs):  # noqa: ANN001
        calls.append(list(command))
        if command[:3] == ["git", "rev-parse", "--verify"]:
            return _completed(list(command), stdout="cccccccccccccccccccccccccccccccccccccccc\n")
        if command[:2] == ["git", "merge-base"]:
            return _completed(list(command), stdout="dddddddddddddddddddddddddddddddddddddddd\n")
        return _completed(list(command), stdout="clean\n")

    monkeypatch.setattr(push_preflight.subprocess, "run", fake_run)

    evidence = push_preflight.run_push_preflight(
        tmp_path,
        "refs/heads/feature aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa refs/heads/feature "
        "0000000000000000000000000000000000000000\n",
        python_bin="python",
    )

    assert evidence.status.value == "passed"
    assert calls[-1][6] == "dddddddddddddddddddddddddddddddddddddddd..aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"


def test_new_branch_without_safe_base_fails_closed(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        push_preflight.subprocess,
        "run",
        lambda command, **kwargs: _completed(list(command), returncode=1, stderr="missing\n"),
    )

    evidence = push_preflight.run_push_preflight(
        tmp_path,
        "refs/heads/feature aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa refs/heads/feature "
        "0000000000000000000000000000000000000000\n",
    )

    assert evidence.status.value == "failed"
    assert evidence.checks[0].summary == "cannot determine safe base for new ref"
    assert push_preflight.preflight_exit_code(evidence) == 1


def test_deleted_ref_is_skipped_without_scan(monkeypatch, tmp_path: Path) -> None:
    calls: list[list[str]] = []
    monkeypatch.setattr(push_preflight.subprocess, "run", lambda command, **kwargs: calls.append(list(command)))

    evidence = push_preflight.run_push_preflight(
        tmp_path,
        "refs/heads/old 0000000000000000000000000000000000000000 refs/heads/old "
        "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb\n",
    )

    assert evidence.status.value == "passed"
    assert evidence.checks[0].summary == "skipped deleted ref refs/heads/old"
    assert calls == []


def test_push_preflight_cli_emits_json_and_exit_code(monkeypatch, tmp_path: Path) -> None:
    evidence = PreflightEvidence.from_checks(
        [PreflightCheck.passed("pre-push-ref-1", summary="ok")],
        evidence_path=tmp_path / "push-preflight.json",
        generated_at="2026-06-30T00:00:00Z",
    )

    def fake_run(project_root, stdin_text, **kwargs):  # noqa: ANN001
        assert project_root == tmp_path
        assert "refs/heads/main" in stdin_text
        return evidence

    monkeypatch.setattr(cli, "_resolve_config", lambda ctx: SimpleNamespace(project_root=tmp_path))
    monkeypatch.setattr(push_preflight, "run_push_preflight", fake_run)

    result = CliRunner().invoke(
        cli.main,
        ["push", "preflight", "--json", "--evidence-out", str(tmp_path / "push-preflight.json")],
        input="refs/heads/main a refs/heads/main b\n",
    )

    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["status"] == "passed"
    assert (tmp_path / "push-preflight.json").exists()


def test_windows_pre_push_wrappers_delegate_to_push_preflight_and_prefer_project_venv() -> None:
    cmd_wrapper = (REPO_ROOT / ".githooks" / "pre-push.cmd").read_text(encoding="utf-8")
    ps1_wrapper = (REPO_ROOT / ".githooks" / "pre-push.ps1").read_text(encoding="utf-8")

    assert "-m groundtruth_kb.cli push preflight" in cmd_wrapper
    assert "-m groundtruth_kb.cli push preflight" in ps1_wrapper
    assert cmd_wrapper.index("groundtruth-kb\\.venv\\Scripts\\python.exe") < cmd_wrapper.index("%PYTHON%")
    assert ps1_wrapper.index("groundtruth-kb/.venv/Scripts/python.exe") < ps1_wrapper.index("$env:PYTHON")
    for direct_script in ("scan_secrets.py", "groundtruth_kb secrets scan"):
        assert direct_script not in cmd_wrapper
        assert direct_script not in ps1_wrapper
