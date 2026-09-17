"""Tests for Windows-native push governance preflight."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from click.testing import CliRunner

REPO_ROOT = Path(__file__).resolve().parents[3]

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


@pytest.mark.parametrize(
    "scan_result,status,exit_code", [(0, "passed", 0), (5, "failed", 1), ("timeout", "inconclusive", 1)]
)
@pytest.mark.parametrize("json_output", [False, True])
@pytest.mark.parametrize("evidence_flag", ["--evidence-out", "--evidence-file"])
@pytest.mark.parametrize("with_authority", [False, True])
def test_preflight_route_preserves_scan_boundary_and_evidence(
    monkeypatch, tmp_path, scan_result, status, exit_code, json_output, evidence_flag, with_authority
):
    from groundtruth_kb.authority_client import AuthorityClient

    selected = tmp_path / "selected"
    caller = tmp_path / "caller"
    selected.mkdir()
    caller.mkdir()
    config = selected / "groundtruth.toml"
    config.write_text(
        '[groundtruth]\nproject_root="."\n' + ('authority_url="http://127.0.0.1:1"\n' if with_authority else ""),
        encoding="utf-8",
    )
    sentinel = caller / "groundtruth.db"
    sentinel.write_bytes(b"foreign database sentinel")
    monkeypatch.chdir(caller)
    for key in ["GT_PROJECT_ROOT", "GT_DB_PATH", "GT_AUTHORITY_URL"]:
        monkeypatch.delenv(key, raising=False)

    def forbidden(*args, **kwargs):
        pytest.fail("A local push diagnostic must not access an authority or database")

    monkeypatch.setattr(AuthorityClient, "request", forbidden)
    monkeypatch.setattr("sqlite3.connect", forbidden)
    monkeypatch.setattr("groundtruth_kb.postgres_kernel.PostgresKernel._connect", forbidden)
    calls = []

    def scan(command, **kwargs):
        calls.append((list(command), kwargs))
        if scan_result == "timeout":
            raise subprocess.TimeoutExpired(command, kwargs["timeout"])
        return _completed(list(command), returncode=scan_result, stdout="redacted fixture result\n")

    monkeypatch.setattr(push_preflight.subprocess, "run", scan)
    destination = caller / "evidence" / "result.json"
    args = [
        "--config",
        str(config),
        "push",
        "preflight",
        "--python-bin",
        "selected-python",
        evidence_flag,
        str(destination),
    ]
    if json_output:
        args.append("--json")
    result = CliRunner().invoke(cli.main, args, input="refs/heads/main new-sha refs/heads/main old-sha\n")
    assert result.exit_code == exit_code, result.output
    assert len(calls) == 1
    command, kwargs = calls[0]
    assert command == [
        "selected-python",
        "-m",
        "groundtruth_kb",
        "secrets",
        "scan",
        "--range",
        "old-sha..new-sha",
        "--redacted",
        "--fail-on",
        "verified-provider",
    ]
    assert kwargs["cwd"] == selected and kwargs["check"] is False
    packet = json.loads(destination.read_text(encoding="utf-8"))
    assert packet["status"] == status
    assert packet["checks"][0]["evidence"]["range"] == "old-sha..new-sha"
    if json_output:
        assert json.loads(result.output) == packet
    else:
        assert status in result.output.lower()
        assert "pre-push-ref-1" in result.output
    assert sentinel.read_bytes() == b"foreign database sentinel"
    assert not (selected / "groundtruth.db").exists()


@pytest.mark.parametrize("module", ["groundtruth_kb", "groundtruth_kb.cli"])
@pytest.mark.parametrize(
    "stdin,status,exit_code",
    [
        ("", "passed", 0),
        ("refs/heads/old " + "0" * 40 + " refs/heads/old " + "b" * 40 + "\n", "passed", 0),
        ("malformed ref tuple\n", "failed", 1),
    ],
)
def test_preflight_cold_cli_entry_preserves_foreign_caller(tmp_path, module, stdin, status, exit_code):
    import groundtruth_kb

    selected = tmp_path / "selected"
    caller = tmp_path / "caller"
    selected.mkdir()
    caller.mkdir()
    config = selected / "groundtruth.toml"
    config.write_text('[groundtruth]\nproject_root="."\nauthority_url="http://127.0.0.1:1"\n', encoding="utf-8")
    sentinel = caller / "groundtruth.db"
    sentinel.write_bytes(b"untouched foreign bytes")
    before = {p.relative_to(tmp_path).as_posix(): p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONDONTWRITEBYTECODE="1")
    for key in list(env):
        if key.startswith(("GT_", "GTKB_", "PG", "GIT_")):
            env.pop(key)
    env["PYTHONPATH"] = str(Path(groundtruth_kb.__file__).resolve().parent.parent)
    result = subprocess.run(
        [sys.executable, "-P", "-m", module, "--config", str(config), "push", "preflight", "--json"],
        cwd=caller,
        env=env,
        input=stdin,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
        check=False,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    assert result.returncode == exit_code, result.stdout + result.stderr
    assert json.loads(result.stdout)["status"] == status
    after = {p.relative_to(tmp_path).as_posix(): p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
    assert after == before
