from __future__ import annotations

import json
import shutil
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


def test_build_dispatch_command_uses_registry_template(tmp_path):
    _write_registry(tmp_path, _antigravity_record())
    command = build_dispatch_command(tmp_path, "C", "hello")
    assert command == ["gemini", "-p", "hello", "--approval-mode=yolo"]


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
        assert args[0] == ["gemini", "-p", "::init gtkb lo\nsentinel\n", "--approval-mode=yolo"]
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


def test_run_verification_treats_timeout_as_substrate_ok(tmp_path, monkeypatch):
    """TimeoutExpired means subprocess launched -- substrate is verified."""
    _write_registry(tmp_path, _antigravity_record())
    prompt = tmp_path / "prompt.txt"
    prompt.write_text("::init gtkb lo\nsentinel\n", encoding="utf-8")

    monkeypatch.setattr(
        "scripts.verify_antigravity_dispatch.shutil.which",
        lambda *args, **kwargs: "/fake/path/gemini.cmd",
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
