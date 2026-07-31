"""Tests for the read-only push readiness diagnostic."""

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
from groundtruth_kb.governance import push_readiness  # noqa: E402
from groundtruth_kb.governance.preflight_evidence import PreflightCheck, PreflightEvidence  # noqa: E402


def _completed(command: list[str], returncode: int = 0, stdout: str = "", stderr: str = ""):
    return subprocess.CompletedProcess(command, returncode, stdout=stdout, stderr=stderr)


def _fake_success(command, **kwargs):  # noqa: ANN001
    command = list(command)
    if command[:3] == ["git", "config", "--get-all"]:
        return _completed(command, stdout="cache\n")
    if command[:3] == ["git", "remote", "get-url"]:
        return _completed(command, stdout="git@github.com:example/repo.git\n")
    return _completed(command, stdout="ok\n")


def test_push_readiness_passes_when_helpers_auth_and_remote_are_ready(monkeypatch, tmp_path: Path) -> None:
    calls: list[tuple[list[str], dict[str, str] | None]] = []

    def fake_run(command, **kwargs):  # noqa: ANN001
        calls.append((list(command), kwargs.get("env")))
        return _fake_success(command, **kwargs)

    monkeypatch.setattr(push_readiness.shutil, "which", lambda name: "gh" if name == "gh" else None)
    monkeypatch.setattr(push_readiness.subprocess, "run", fake_run)

    evidence = push_readiness.run_push_readiness(tmp_path)

    assert evidence.summary_counts["hard_failures"] == 0
    assert any(call[0][:3] == ["git", "ls-remote", "--exit-code"] for call in calls)
    ls_remote_env = next(env for command, env in calls if command[:3] == ["git", "ls-remote", "--exit-code"])
    assert ls_remote_env["GIT_TERMINAL_PROMPT"] == "0"
    assert ls_remote_env["GCM_INTERACTIVE"] == "never"


def test_push_readiness_fails_when_gh_auth_is_invalid(monkeypatch, tmp_path: Path) -> None:
    def fake_run(command, **kwargs):  # noqa: ANN001
        command = list(command)
        if command[:3] == ["gh", "auth", "status"]:
            return _completed(command, returncode=1, stderr="not logged in\n")
        return _fake_success(command, **kwargs)

    monkeypatch.setattr(push_readiness.shutil, "which", lambda name: "gh" if name == "gh" else None)
    monkeypatch.setattr(push_readiness.subprocess, "run", fake_run)

    evidence = push_readiness.run_push_readiness(tmp_path)

    failed = next(check for check in evidence.checks if check.name == "github-cli-auth")
    assert failed.outcome.value == "failed"
    assert failed.blocks_release is True
    assert push_readiness.readiness_exit_code(evidence) == 1


def test_push_readiness_reports_multiple_helpers_as_advisory(monkeypatch, tmp_path: Path) -> None:
    def fake_run(command, **kwargs):  # noqa: ANN001
        command = list(command)
        if command[:3] == ["git", "config", "--get-all"]:
            return _completed(command, stdout="manager-core\ncache\n")
        return _fake_success(command, **kwargs)

    monkeypatch.setattr(push_readiness.shutil, "which", lambda name: "gh" if name == "gh" else None)
    monkeypatch.setattr(push_readiness.subprocess, "run", fake_run)

    evidence = push_readiness.run_push_readiness(tmp_path)

    helper = next(check for check in evidence.checks if check.name == "credential-helper")
    assert helper.outcome.value == "failed"
    assert helper.severity.value == "advisory"
    assert helper.blocks_release is False


def test_push_readiness_fails_when_remote_is_inaccessible(monkeypatch, tmp_path: Path) -> None:
    def fake_run(command, **kwargs):  # noqa: ANN001
        command = list(command)
        if command[:3] == ["git", "ls-remote", "--exit-code"]:
            return _completed(command, returncode=128, stderr="permission denied\n")
        return _fake_success(command, **kwargs)

    monkeypatch.setattr(push_readiness.shutil, "which", lambda name: "gh" if name == "gh" else None)
    monkeypatch.setattr(push_readiness.subprocess, "run", fake_run)

    evidence = push_readiness.run_push_readiness(tmp_path)

    remote = next(check for check in evidence.checks if check.name == "remote-reachability")
    assert remote.outcome.value == "failed"
    assert remote.blocks_release is True


def test_push_readiness_cli_emits_json_and_exit_code(monkeypatch, tmp_path: Path) -> None:
    evidence = PreflightEvidence.from_checks(
        [PreflightCheck.passed("remote-reachability", summary="ok")],
        evidence_path=tmp_path / "push-readiness.json",
        generated_at="2026-06-30T00:00:00Z",
    )

    def fake_run(project_root, **kwargs):  # noqa: ANN001
        assert project_root == tmp_path
        assert kwargs["remote"] == "upstream"
        return evidence

    monkeypatch.setattr(cli, "_resolve_config", lambda ctx: SimpleNamespace(project_root=tmp_path))
    monkeypatch.setattr(push_readiness, "run_push_readiness", fake_run)

    result = CliRunner().invoke(
        cli.main,
        [
            "push",
            "readiness",
            "--remote",
            "upstream",
            "--json",
            "--evidence-out",
            str(tmp_path / "push-readiness.json"),
        ],
    )

    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["status"] == "passed"
    assert (tmp_path / "push-readiness.json").exists()
