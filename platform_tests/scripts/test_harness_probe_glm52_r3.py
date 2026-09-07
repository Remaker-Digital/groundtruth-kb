# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Focused unit tests for the WI-5808 GLM-5.2 Run 3 harness capability probe.

Each test exercises one of the six probe checks including failure paths, the
snake_case key convention, the no-hardcoded-timer discipline, and the
missing-timeout configuration-error path.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

# Ensure scripts/ is importable so the probe module can be loaded.
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

import harness_probe_glm52_r3 as probe  # noqa: E402

PROJECT_ROOT = Path(__file__).resolve().parents[2]


# --- Check 1: project-root containment ------------------------------------


def test_project_root_containment_pass(monkeypatch) -> None:
    monkeypatch.chdir(PROJECT_ROOT)
    result = probe._check_project_root_containment(PROJECT_ROOT)
    assert result["project_root_containment"]["passed"] is True
    assert "cwd" in result["project_root_containment"]


def test_project_root_containment_fail(monkeypatch) -> None:
    # Patch Path.cwd() to return a path that is NOT inside the project root.
    outside = Path("Z:/definitely/outside/the/gtkb/root")
    monkeypatch.setattr(Path, "cwd", classmethod(lambda cls: outside))
    result = probe._check_project_root_containment(PROJECT_ROOT)
    assert result["project_root_containment"]["passed"] is False


# --- Check 2: venv resolution ---------------------------------------------


def test_project_venv_resolution_pass(monkeypatch) -> None:
    monkeypatch.setattr(probe, "_VENV_PYTHON_PARTS", ("groundtruth-kb", ".venv", "Scripts", "python.exe"))
    result = probe._check_venv_resolution(PROJECT_ROOT, timeout=30.0)
    assert result["project_venv_resolution"]["passed"] is True
    assert result["project_venv_resolution"]["import_succeeded"] is True


def test_project_venv_resolution_fail_missing_venv(monkeypatch, tmp_path) -> None:
    # Point venv parts at a path that does not exist.
    monkeypatch.setattr(probe, "_VENV_PYTHON_PARTS", ("__does_not_exist__", "python.exe"))
    result = probe._check_venv_resolution(PROJECT_ROOT, timeout=30.0)
    assert result["project_venv_resolution"]["passed"] is False
    assert result["project_venv_resolution"]["import_succeeded"] is False


def test_project_venv_resolution_fail_import_error(monkeypatch) -> None:
    class _FakeResult:
        returncode = 1
        stderr = "ModuleNotFoundError: No module named 'groundtruth_kb'"
        stdout = ""

    def _fake_run(*args, **kwargs):
        return _FakeResult()

    monkeypatch.setattr(subprocess, "run", _fake_run)
    result = probe._check_venv_resolution(PROJECT_ROOT, timeout=30.0)
    assert result["project_venv_resolution"]["passed"] is False
    assert "groundtruth_kb" in (result["project_venv_resolution"]["import_error"] or "")


# --- Check 3: git read health ---------------------------------------------


def test_git_read_health_pass(monkeypatch) -> None:
    class _FakeResult:
        def __init__(self, returncode, stdout, stderr=""):
            self.returncode = returncode
            self.stdout = stdout
            self.stderr = stderr

    def _fake_run(*args, **kwargs):
        cmd = args[0]
        if "rev-parse" in cmd:
            return _FakeResult(0, "abc1234\n")
        if "status" in cmd:
            return _FakeResult(0, " M file1.py\n?? file2.py\n")
        return _FakeResult(0, "")

    monkeypatch.setattr(subprocess, "run", _fake_run)
    result = probe._check_git_read_health(PROJECT_ROOT, timeout=30.0)
    assert result["git_read_health"]["passed"] is True
    assert result["git_read_health"]["head_sha"] == "abc1234"
    assert result["git_read_health"]["dirty_count"] == 2


def test_git_read_health_fail_not_a_repo(monkeypatch) -> None:
    class _FakeResult:
        def __init__(self, returncode, stdout="", stderr=""):
            self.returncode = returncode
            self.stdout = stdout
            self.stderr = stderr

    def _fake_run(*args, **kwargs):
        return _FakeResult(128, stderr="fatal: not a git repository")

    monkeypatch.setattr(subprocess, "run", _fake_run)
    result = probe._check_git_read_health(PROJECT_ROOT, timeout=30.0)
    assert result["git_read_health"]["passed"] is False
    assert result["git_read_health"]["head_sha"] is None


# --- Check 4: gt CLI reachability -----------------------------------------


def test_gt_cli_reachability_pass(monkeypatch) -> None:
    class _FakeResult:
        returncode = 0
        stdout = "help"
        stderr = ""

    monkeypatch.setattr(subprocess, "run", lambda *a, **k: _FakeResult())
    result = probe._check_gt_cli_reachability(PROJECT_ROOT, timeout=30.0)
    assert result["gt_cli_reachability"]["passed"] is True
    assert result["gt_cli_reachability"]["exit_code"] == 0


def test_gt_cli_reachability_fail_nonzero_exit(monkeypatch) -> None:
    class _FakeResult:
        returncode = 2
        stdout = ""
        stderr = "error"

    monkeypatch.setattr(subprocess, "run", lambda *a, **k: _FakeResult())
    result = probe._check_gt_cli_reachability(PROJECT_ROOT, timeout=30.0)
    assert result["gt_cli_reachability"]["passed"] is False
    assert result["gt_cli_reachability"]["exit_code"] == 2


# --- Check 5: session-envelope presence -----------------------------------


def _write_session_envelope(tmp_path: Path, session_id: str, payload: object) -> Path:
    envelope_path = tmp_path / ".gtkb-state" / "session-envelopes" / f"{session_id}.json"
    envelope_path.parent.mkdir(parents=True, exist_ok=True)
    envelope_path.write_text(json.dumps(payload), encoding="utf-8")
    return envelope_path


def test_session_envelope_presence_passes_exact_context_document(tmp_path) -> None:
    session_id = "session-exact-1"
    envelope_path = _write_session_envelope(tmp_path, session_id, {"session_id": session_id})

    result = probe._check_session_envelope_presence(tmp_path, session_id)["session_envelope_presence"]

    assert result == {
        "passed": True,
        "path": str(envelope_path),
        "session_id": session_id,
        "detail": "exact context-keyed session envelope is present and identity-bound",
    }


def test_explicit_session_id_wins_over_marker_environment(monkeypatch, tmp_path) -> None:
    explicit_id = "explicit-session"
    _write_session_envelope(tmp_path, explicit_id, {"session_id": explicit_id})
    monkeypatch.setenv("GTKB_SESSION_ID", "ambient-session")

    result = probe._check_session_envelope_presence(tmp_path, explicit_id)["session_envelope_presence"]

    assert result["passed"] is True
    assert result["session_id"] == explicit_id


def test_marker_continuity_resolver_supplies_context(monkeypatch, tmp_path) -> None:
    session_id = "marker-session"
    _write_session_envelope(tmp_path, session_id, {"session_id": session_id})
    for env_name in probe.MARKER_CONTINUITY_ORDER:
        monkeypatch.delenv(env_name, raising=False)
    monkeypatch.setenv("GTKB_SESSION_ID", session_id)

    result = probe._check_session_envelope_presence(tmp_path)["session_envelope_presence"]

    assert result["passed"] is True
    assert result["session_id"] == session_id


def test_session_envelope_presence_fails_without_session_id(monkeypatch, tmp_path) -> None:
    for env_name in probe.MARKER_CONTINUITY_ORDER:
        monkeypatch.delenv(env_name, raising=False)

    result = probe._check_session_envelope_presence(tmp_path)["session_envelope_presence"]

    assert result["passed"] is False
    assert result["path"] is None
    assert result["session_id"] is None


def test_session_envelope_presence_rejects_unsafe_identity(tmp_path) -> None:
    result = probe._check_session_envelope_presence(tmp_path, "../foreign")["session_envelope_presence"]

    assert result["passed"] is False
    assert result["path"] is None
    assert "filesystem-safe" in result["detail"]


def test_session_envelope_presence_fails_when_exact_document_is_absent(tmp_path) -> None:
    result = probe._check_session_envelope_presence(tmp_path, "missing-session")["session_envelope_presence"]

    assert result["passed"] is False
    assert result["session_id"] == "missing-session"
    assert "absent" in result["detail"]


def test_session_envelope_presence_rejects_malformed_json(tmp_path) -> None:
    session_id = "malformed-session"
    envelope_path = _write_session_envelope(tmp_path, session_id, {})
    envelope_path.write_text("{not-json", encoding="utf-8")

    result = probe._check_session_envelope_presence(tmp_path, session_id)["session_envelope_presence"]

    assert result["passed"] is False
    assert "malformed" in result["detail"]


def test_session_envelope_presence_rejects_non_mapping_json(tmp_path) -> None:
    session_id = "list-session"
    _write_session_envelope(tmp_path, session_id, [session_id])

    result = probe._check_session_envelope_presence(tmp_path, session_id)["session_envelope_presence"]

    assert result["passed"] is False
    assert "not a mapping" in result["detail"]


def test_session_envelope_presence_rejects_root_identity_mismatch(tmp_path) -> None:
    session_id = "expected-session"
    _write_session_envelope(tmp_path, session_id, {"session_id": "foreign-session"})

    result = probe._check_session_envelope_presence(tmp_path, session_id)["session_envelope_presence"]

    assert result["passed"] is False
    assert "does not match" in result["detail"]


def test_session_envelope_presence_never_selects_another_session(tmp_path) -> None:
    _write_session_envelope(tmp_path, "other-session", {"session_id": "other-session"})

    result = probe._check_session_envelope_presence(tmp_path, "invoking-session")["session_envelope_presence"]

    assert result["passed"] is False
    assert result["path"].endswith("invoking-session.json")


def test_source_and_tests_do_not_reference_shared_envelope_projection() -> None:
    source_text = Path(probe.__file__).read_text(encoding="utf-8")
    test_text = Path(__file__).read_text(encoding="utf-8")
    forbidden_literal = "/".join((".claude", "session", "envelope.json"))

    assert forbidden_literal not in source_text
    assert forbidden_literal not in test_text


# --- Check 6: report determinism ------------------------------------------


def test_report_determinism() -> None:
    report1 = probe.build_report(PROJECT_ROOT, timeout=30.0)
    report2 = probe.build_report(PROJECT_ROOT, timeout=30.0)
    r1 = {k: v for k, v in report1.items() if k != "generated_at"}
    r2 = {k: v for k, v in report2.items() if k != "generated_at"}
    assert r1 == r2


# --- Owner decision: snake_case keys --------------------------------------


def test_report_json_keys_are_snake_case() -> None:
    report = probe.build_report(PROJECT_ROOT, timeout=30.0)
    for key in report:
        assert "_" not in key or key.islower(), f"report key {key!r} is not snake_case"
        assert " " not in key, f"report key {key!r} contains a space"


# --- DELIB-202667722: no hardcoded timeout literals ------------------------


def test_no_hardcoded_timeout_literals() -> None:
    source = Path(probe.__file__).read_text(encoding="utf-8")
    # No numeric literal passed to subprocess.run timeout= directly.
    assert "timeout=" not in source.replace("timeout=timeout", "").replace("timeout=args.timeout", ""), (
        "probe must not pass a numeric literal to subprocess timeout="
    )
    # The module must reference the env var and the --timeout CLI source.
    assert "HARNESS_PROBE_SUBPROCESS_TIMEOUT" in source


# --- F2 (v002): missing timeout returns config error -----------------------


def test_missing_timeout_returns_config_error(monkeypatch) -> None:
    monkeypatch.delenv("HARNESS_PROBE_SUBPROCESS_TIMEOUT", raising=False)
    timeout, error = probe._resolve_timeout(None)
    assert timeout is None
    assert error is not None
    assert "--timeout" in error
    assert "HARNESS_PROBE_SUBPROCESS_TIMEOUT" in error


def test_timeout_from_env_var(monkeypatch) -> None:
    monkeypatch.setenv("HARNESS_PROBE_SUBPROCESS_TIMEOUT", "45")
    timeout, error = probe._resolve_timeout(None)
    assert timeout == 45.0
    assert error is None


def test_timeout_from_cli_arg_precedes_env(monkeypatch) -> None:
    monkeypatch.setenv("HARNESS_PROBE_SUBPROCESS_TIMEOUT", "999")
    timeout, error = probe._resolve_timeout(15.0)
    assert timeout == 15.0
    assert error is None
