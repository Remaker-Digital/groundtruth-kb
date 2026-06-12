from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from scripts.verify_antigravity_dispatch import (
    VerificationError,
    _resolve_executable_for_host,
    build_dispatch_command,
    run_verification,
    sanitize_capture,
)


@pytest.fixture(autouse=True)
def clear_registry_env(monkeypatch):
    monkeypatch.delenv("GTKB_HARNESS_REGISTRY_PATH", raising=False)


def _write_registry(root: Path, record: dict) -> None:
    state = root / "harness-state"
    state.mkdir()
    (state / "harness-registry.json").write_text(
        json.dumps({"harnesses": [record], "schema_version": 1}),
        encoding="utf-8",
    )


def _antigravity_record(**overrides):
    record = {
        "harness_name": "antigravity",
        "harness_type": "antigravity",
        "id": "C",
        "invocation_surfaces": {
            "headless": {
                "argv": ["gemini", "-p", "{{PROMPT}}", "--approval-mode=yolo"],
            }
        },
        "role": [],
        "status": "registered",
    }
    record.update(overrides)
    return record


def test_build_dispatch_command_uses_registry_template(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "scripts.verify_antigravity_dispatch.shutil.which",
        lambda *args, **kwargs: None,
    )
    _write_registry(tmp_path, _antigravity_record())
    command = build_dispatch_command(tmp_path, "C", "hello")
    import os

    if os.name == "nt":
        assert command == ["gemini", "--prompt=", "--approval-mode=yolo"]
    else:
        assert command == ["gemini", "-p", "", "--approval-mode=yolo"]


def test_build_dispatch_command_errors_for_missing_recipient(tmp_path):
    _write_registry(tmp_path, _antigravity_record(id="A"))
    with pytest.raises(VerificationError, match="recipient harness not found"):
        build_dispatch_command(tmp_path, "C", "hello")


def test_build_dispatch_command_errors_for_malformed_template(tmp_path):
    _write_registry(tmp_path, _antigravity_record(invocation_surfaces={"headless": {"argv": []}}))
    with pytest.raises(VerificationError, match="no valid headless argv"):
        build_dispatch_command(tmp_path, "C", "hello")


def test_run_verification_writes_evidence_files(tmp_path, monkeypatch):
    _write_registry(tmp_path, _antigravity_record())
    prompt = tmp_path / "prompt.txt"
    prompt.write_text("::init gtkb lo\nsentinel\n", encoding="utf-8")

    # Force shutil.which to None so the host-resolution helper returns the
    # projected argv unchanged, keeping this test independent of whether
    # `gemini` happens to be installed on the test host.
    monkeypatch.setattr(
        "scripts.verify_antigravity_dispatch.shutil.which",
        lambda *args, **kwargs: None,
    )

    def fake_run(*args, **kwargs):
        # Match new file-based capture: write to the file handles the script
        # passed in via stdout/stderr kwargs.
        import os

        if os.name == "nt":
            assert args[0] == ["gemini", "--prompt=", "--approval-mode=yolo"]
        else:
            assert args[0] == ["gemini", "-p", "", "--approval-mode=yolo"]
        if "stdout" in kwargs and hasattr(kwargs["stdout"], "write"):
            kwargs["stdout"].write("ok")
        if "stderr" in kwargs and hasattr(kwargs["stderr"], "write"):
            kwargs["stderr"].write("warn")
        return subprocess.CompletedProcess(args=args[0], returncode=7)

    monkeypatch.setattr(subprocess, "run", fake_run)
    result = run_verification(
        project_root=tmp_path,
        recipient="C",
        prompt_fixture=prompt,
        timeout=1,
        evidence_root=tmp_path / "evidence",
    )
    evidence_dir = Path(result["evidence_dir"])
    assert result["substrate_ok"] is True
    argv_payload = json.loads((evidence_dir / "argv.json").read_text(encoding="utf-8"))
    assert argv_payload["argv"][0] == "gemini"
    assert argv_payload["resolved_argv"] == argv_payload["argv"]
    assert argv_payload["resolution_applied"] is False
    result_payload = json.loads((evidence_dir / "result.json").read_text(encoding="utf-8"))
    assert result_payload["returncode"] == 7
    assert result_payload["resolution_applied"] is False
    assert (evidence_dir / "stdout.txt").read_text(encoding="utf-8") == "ok"
    assert (evidence_dir / "stderr.txt").read_text(encoding="utf-8") == "warn"


def test_resolve_executable_for_host_returns_original_when_not_found(monkeypatch):
    monkeypatch.setattr(
        "scripts.verify_antigravity_dispatch.shutil.which",
        lambda *args, **kwargs: None,
    )
    assert _resolve_executable_for_host(["gemini", "-p", "x"]) == ["gemini", "-p", "x"]


def test_resolve_executable_for_host_substitutes_resolved_path(monkeypatch):
    monkeypatch.setattr(
        "scripts.verify_antigravity_dispatch.shutil.which",
        lambda exe: "/fake/path/to/" + exe + ".cmd",
    )
    assert _resolve_executable_for_host(["gemini", "-p", "x"]) == [
        "/fake/path/to/gemini.cmd",
        "-p",
        "x",
    ]


def test_resolve_executable_for_host_handles_empty_command():
    assert _resolve_executable_for_host([]) == []


def test_resolver_source_contains_no_home_dir_derivation():
    """Clause 2a lock: the resolver must not derive user-profile exec dirs.

    Structural assertion against re-introducing the REVISED-11 home-directory
    PATH enrichment design (NO-GO'd at -012). The resolver relies only on the
    launching context's ambient PATH per the External Harness Executable
    Resolution Exception clause 2a; it must not compute candidate directories
    from the user home.
    """
    import inspect

    src = inspect.getsource(_resolve_executable_for_host)
    forbidden = ("expanduser", "AppData", "WindowsApps", "npm-global", "_candidate_path_dirs")
    for token in forbidden:
        assert token not in src, f"home-directory derivation token {token!r} reintroduced into resolver"


def test_resolver_uses_only_ambient_path(monkeypatch):
    """Clause 2a contract: resolution consults ambient PATH with no enrichment.

    ``shutil.which`` must be called with only the command name -- no ``path=``
    override and no positional path argument that would inject computed
    directories. This asserts the resolver does not enrich PATH.
    """
    calls = []

    def spy_which(cmd, *args, **kwargs):
        calls.append((cmd, args, kwargs))
        return "/ambient/path/gemini.cmd"

    monkeypatch.setattr("scripts.verify_antigravity_dispatch.shutil.which", spy_which)
    result = _resolve_executable_for_host(["gemini", "-p", "x"])
    assert result == ["/ambient/path/gemini.cmd", "-p", "x"]
    assert len(calls) == 1, "resolver should consult shutil.which exactly once"
    cmd, args, kwargs = calls[0]
    assert cmd == "gemini"
    assert args == (), "no positional PATH override permitted (clause 2a: ambient only)"
    assert "path" not in kwargs, "no enriched path= kwarg permitted (clause 2a: ambient only)"


def test_resolver_clause_2a_contract_documented():
    """The resolver docstring must cite the clause-2a ambient-PATH contract.

    Locks the documentation to the governing rule so the boundary contract is
    discoverable at the call site, not only in the bridge audit trail.
    """
    assert _resolve_executable_for_host.__doc__ is not None
    assert "clause 2a" in _resolve_executable_for_host.__doc__


def test_run_verification_treats_timeout_as_substrate_ok(tmp_path, monkeypatch):
    """TimeoutExpired means subprocess launched -- substrate is verified."""
    _write_registry(tmp_path, _antigravity_record())
    prompt = tmp_path / "prompt.txt"
    prompt.write_text("::init gtkb lo\nsentinel\n", encoding="utf-8")

    calls = []

    def mock_which(cmd, *args, **kwargs):
        calls.append(cmd)
        if len(calls) == 1:
            return None
        return "/fake/path/gemini.cmd"

    monkeypatch.setattr(
        "scripts.verify_antigravity_dispatch.shutil.which",
        mock_which,
    )

    def raise_timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired(
            cmd=args[0],
            timeout=kwargs.get("timeout", 1),
            output=b"partial stdout",
            stderr=b"partial stderr",
        )

    monkeypatch.setattr(subprocess, "run", raise_timeout)
    result = run_verification(
        project_root=tmp_path,
        recipient="C",
        prompt_fixture=prompt,
        timeout=1,
        evidence_root=tmp_path / "evidence",
    )
    assert result["substrate_ok"] is True
    assert result["error"]["type"] == "TimeoutExpired"
    assert "substrate verified" in result["error"]["note"]
    assert result["returncode"] is None
    evidence_dir = Path(result["evidence_dir"])
    result_payload = json.loads((evidence_dir / "result.json").read_text(encoding="utf-8"))
    assert result_payload["substrate_ok"] is True
    assert result_payload["resolution_applied"] is True


def test_run_verification_treats_filenotfound_as_substrate_failure(tmp_path, monkeypatch):
    """FileNotFoundError (WinError 2) means subprocess could NOT launch -- substrate failed."""
    _write_registry(tmp_path, _antigravity_record())
    prompt = tmp_path / "prompt.txt"
    prompt.write_text("::init gtkb lo\nsentinel\n", encoding="utf-8")

    monkeypatch.setattr(
        "scripts.verify_antigravity_dispatch.shutil.which",
        lambda *args, **kwargs: None,
    )

    def raise_filenotfound(*args, **kwargs):
        raise FileNotFoundError("[WinError 2] The system cannot find the file specified")

    monkeypatch.setattr(subprocess, "run", raise_filenotfound)
    result = run_verification(
        project_root=tmp_path,
        recipient="C",
        prompt_fixture=prompt,
        timeout=1,
        evidence_root=tmp_path / "evidence",
    )
    assert result["substrate_ok"] is False
    assert result["error"]["type"] == "FileNotFoundError"


def test_sanitize_capture_redacts_credential_shapes():
    text = "token=abc123456789xyz and api_key: AIza123456789012345678901234567890"
    sanitized = sanitize_capture(text)
    assert "abc123456789xyz" not in sanitized
    assert "AIza123456789012345678901234567890" not in sanitized
    assert "[REDACTED]" in sanitized
