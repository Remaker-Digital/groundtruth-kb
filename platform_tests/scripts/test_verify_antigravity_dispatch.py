from __future__ import annotations

import importlib
import json
import os
import sqlite3
import subprocess
import sys
import textwrap
from pathlib import Path
from types import ModuleType

import pytest

from scripts.verify_antigravity_dispatch import (
    VerificationError,
    _resolve_executable_for_host,
    build_dispatch_command,
    evaluate_readiness,
    inspect_verdict_anchor_guard,
    resolve_loaded_project_module,
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
                "argv": [
                    "agy",
                    "--print",
                    "{{PROMPT}}",
                    "--add-dir",
                    "{{PROJECT_ROOT}}",
                    "--dangerously-skip-permissions",
                ],
                "stdin": True,
                "prompt_transport": "stdin",
            }
        },
        "role": ["loyal-opposition"],
        "status": "active",
        "can_receive_dispatch": False,
    }
    record.update(overrides)
    return record


def _write_conversation_db(conversations_dir: Path, *, step_type: int, payload: bytes) -> None:
    conversations_dir.mkdir(parents=True, exist_ok=True)
    db_path = conversations_dir / "fixture.db"
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            """
            CREATE TABLE steps (
                idx INTEGER PRIMARY KEY,
                step_type INTEGER NOT NULL DEFAULT 0,
                status INTEGER NOT NULL DEFAULT 0,
                has_subtrajectory numeric NOT NULL DEFAULT false,
                metadata BLOB,
                error_details BLOB,
                permissions BLOB,
                task_details BLOB,
                render_info BLOB,
                step_payload BLOB,
                step_format INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        connection.execute(
            """
            INSERT INTO steps (
                idx, step_type, status, has_subtrajectory, metadata, error_details,
                permissions, task_details, render_info, step_payload, step_format
            )
            VALUES (1, ?, 0, 0, NULL, NULL, NULL, NULL, NULL, ?, 0)
            """,
            (step_type, payload),
        )


def _fake_module(name: str, source_path: Path, **attributes: object) -> ModuleType:
    module = ModuleType(name)
    module.__file__ = str(source_path)
    for key, value in attributes.items():
        setattr(module, key, value)
    return module


def test_project_module_resolver_reuses_exact_loaded_object(tmp_path, monkeypatch):
    source_path = tmp_path / "runtime.py"
    source_path.write_text("# fixture\n", encoding="utf-8")
    sentinel = object()
    module = _fake_module("_private_runtime", source_path, sentinel=sentinel)
    monkeypatch.setitem(sys.modules, "_private_runtime", module)
    monkeypatch.setattr(
        importlib,
        "import_module",
        lambda _name: pytest.fail("package import must not run for an exact loaded module"),
    )

    resolved = resolve_loaded_project_module(
        project_root=tmp_path,
        expected_source_path=source_path,
        import_name="scripts.runtime",
        required_attributes=("sentinel",),
    )

    assert resolved is module
    assert resolved.sentinel is sentinel


def test_project_module_resolver_validates_package_fallback_source(tmp_path, monkeypatch):
    source_path = tmp_path / "runtime.py"
    source_path.write_text("# fixture\n", encoding="utf-8")
    module = _fake_module("scripts.runtime", source_path, sentinel=object())
    monkeypatch.setattr(importlib, "import_module", lambda name: module if name == "scripts.runtime" else None)

    resolved = resolve_loaded_project_module(
        project_root=tmp_path,
        expected_source_path=source_path,
        import_name="scripts.runtime",
        required_attributes=("sentinel",),
    )

    assert resolved is module


def test_project_module_resolver_rejects_duplicate_exact_source_objects(tmp_path, monkeypatch):
    source_path = tmp_path / "runtime.py"
    source_path.write_text("# fixture\n", encoding="utf-8")
    monkeypatch.setitem(sys.modules, "_runtime_one", _fake_module("_runtime_one", source_path, sentinel=1))
    monkeypatch.setitem(sys.modules, "_runtime_two", _fake_module("_runtime_two", source_path, sentinel=2))

    with pytest.raises(VerificationError, match="multiple loaded module objects"):
        resolve_loaded_project_module(
            project_root=tmp_path,
            expected_source_path=source_path,
            import_name="scripts.runtime",
            required_attributes=("sentinel",),
        )


def test_project_module_resolver_rejects_wrong_source_fallback(tmp_path, monkeypatch):
    source_path = tmp_path / "runtime.py"
    wrong_source = tmp_path / "shadow" / "runtime.py"
    source_path.write_text("# canonical\n", encoding="utf-8")
    wrong_source.parent.mkdir()
    wrong_source.write_text("# shadow\n", encoding="utf-8")
    monkeypatch.setattr(
        importlib,
        "import_module",
        lambda _name: _fake_module("scripts.runtime", wrong_source, sentinel=object()),
    )

    with pytest.raises(VerificationError, match="resolved to .* expected"):
        resolve_loaded_project_module(
            project_root=tmp_path,
            expected_source_path=source_path,
            import_name="scripts.runtime",
            required_attributes=("sentinel",),
        )


def test_project_module_resolver_rejects_missing_required_attributes(tmp_path, monkeypatch):
    source_path = tmp_path / "runtime.py"
    source_path.write_text("# fixture\n", encoding="utf-8")
    monkeypatch.setitem(
        sys.modules, "_runtime_without_contract", _fake_module("_runtime_without_contract", source_path)
    )

    with pytest.raises(VerificationError, match="missing required attributes: sentinel"):
        resolve_loaded_project_module(
            project_root=tmp_path,
            expected_source_path=source_path,
            import_name="scripts.runtime",
            required_attributes=("sentinel",),
        )


def test_project_module_resolver_rejects_source_outside_project_root(tmp_path):
    project_root = tmp_path / "project"
    source_path = tmp_path / "outside.py"
    project_root.mkdir()
    source_path.write_text("# outside\n", encoding="utf-8")

    with pytest.raises(VerificationError, match="outside the project root"):
        resolve_loaded_project_module(
            project_root=project_root,
            expected_source_path=source_path,
            import_name="scripts.runtime",
            required_attributes=(),
        )


def test_daemon_style_top_level_import_reuses_private_runtime_with_foreign_namespace(tmp_path):
    project_root = Path(__file__).resolve().parents[2]
    script = textwrap.dedent(
        """
        import importlib.util
        import json
        import sys
        import types
        from pathlib import Path

        project_root = Path(sys.argv[1]).resolve()
        scripts_dir = project_root / "scripts"
        source_dir = project_root / "groundtruth-kb" / "src"
        sys.path[:0] = [str(scripts_dir), str(source_dir)]

        runtime_spec = importlib.util.spec_from_file_location(
            "_dispatcher_runtime_for_daemon",
            scripts_dir / "dispatcher_runtime.py",
        )
        runtime = importlib.util.module_from_spec(runtime_spec)
        sys.modules[runtime_spec.name] = runtime
        runtime_spec.loader.exec_module(runtime)

        projection = sys.modules["harness_projection_reader"]

        foreign_scripts = types.ModuleType("scripts")
        foreign_scripts.__path__ = [str(project_root / "foreign-scripts")]
        sys.modules["scripts"] = foreign_scripts

        verifier_spec = importlib.util.spec_from_file_location(
            "verify_antigravity_dispatch",
            scripts_dir / "verify_antigravity_dispatch.py",
        )
        verifier = importlib.util.module_from_spec(verifier_spec)
        sys.modules[verifier_spec.name] = verifier
        verifier_spec.loader.exec_module(verifier)

        payload = {
            "dispatch_target_reused": verifier.DispatchTarget is runtime.DispatchTarget,
            "harness_command_reused": verifier._harness_command is runtime._harness_command,
            "projection_reader_reused": (
                verifier.load_harness_projection is projection.load_harness_projection
            ),
            "package_runtime_loaded": "scripts.dispatcher_runtime" in sys.modules,
        }
        print(json.dumps(payload, sort_keys=True))
        """
    )

    completed = subprocess.run(
        [sys.executable, "-I", "-c", script, str(project_root)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert json.loads(completed.stdout) == {
        "dispatch_target_reused": True,
        "harness_command_reused": True,
        "package_runtime_loaded": False,
        "projection_reader_reused": True,
    }


def test_build_dispatch_command_uses_registry_template(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "scripts.verify_antigravity_dispatch.shutil.which",
        lambda *args, **kwargs: None,
    )
    _write_registry(tmp_path, _antigravity_record())
    command = build_dispatch_command(tmp_path, "C", "hello")

    assert command == [
        "agy",
        "--print",
        "hello",
        "--add-dir",
        str(tmp_path),
        "--dangerously-skip-permissions",
    ]


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
    monkeypatch.delenv("LOCALAPPDATA", raising=False)

    # Force shutil.which to None so the host-resolution helper returns the
    # projected argv unchanged, keeping this test independent of whether
    # `agy` happens to be installed on the test host.
    monkeypatch.setattr(
        "scripts.verify_antigravity_dispatch.shutil.which",
        lambda *args, **kwargs: None,
    )

    def fake_run(*args, **kwargs):
        # Match new file-based capture: write to the file handles the script
        # passed in via stdout/stderr kwargs.
        if os.name == "nt":
            assert kwargs["creationflags"] & getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
        assert args[0] == [
            "agy",
            "--print",
            "::init gtkb lo\nsentinel\n",
            "--add-dir",
            str(tmp_path),
            "--dangerously-skip-permissions",
        ]
        if os.name != "nt":
            assert "creationflags" not in kwargs
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
    assert argv_payload["argv"][0] == "agy"
    assert argv_payload["resolved_argv"] == argv_payload["argv"]
    assert argv_payload["resolution_applied"] is False
    result_payload = json.loads((evidence_dir / "result.json").read_text(encoding="utf-8"))
    assert result_payload["returncode"] == 7
    assert result_payload["resolution_applied"] is False
    assert (evidence_dir / "stdout.txt").read_text(encoding="utf-8") == "ok"
    assert (evidence_dir / "stderr.txt").read_text(encoding="utf-8") == "warn"


def test_resolve_executable_for_host_returns_original_when_not_found(monkeypatch):
    monkeypatch.delenv("LOCALAPPDATA", raising=False)
    monkeypatch.setattr(
        "scripts.verify_antigravity_dispatch.shutil.which",
        lambda *args, **kwargs: None,
    )
    assert _resolve_executable_for_host(["agy", "--print", "x"]) == ["agy", "--print", "x"]


def test_resolve_executable_for_host_substitutes_resolved_path(monkeypatch):
    monkeypatch.setattr(
        "scripts.verify_antigravity_dispatch.shutil.which",
        lambda exe: "/fake/path/to/" + exe + ".cmd",
    )
    assert _resolve_executable_for_host(["agy", "--print", "x"]) == [
        "/fake/path/to/agy.cmd",
        "--print",
        "x",
    ]


def test_resolve_executable_for_host_handles_empty_command():
    assert _resolve_executable_for_host([]) == []


def test_resolver_uses_ambient_path_before_installer_fallback(monkeypatch):
    """Ambient PATH remains first; installer fallback is only for stale process PATH."""

    calls = []

    def spy_which(cmd, *args, **kwargs):
        calls.append((cmd, args, kwargs))
        return "/ambient/path/agy.cmd"

    monkeypatch.setattr("scripts.verify_antigravity_dispatch.shutil.which", spy_which)
    result = _resolve_executable_for_host(["agy", "--print", "x"])
    assert result == ["/ambient/path/agy.cmd", "--print", "x"]
    assert len(calls) == 1, "resolver should consult shutil.which exactly once"
    cmd, args, kwargs = calls[0]
    assert cmd == "agy"
    assert args == (), "no positional PATH override permitted (clause 2a: ambient only)"
    assert "path" not in kwargs


def test_resolver_documents_official_installer_fallback():
    assert _resolve_executable_for_host.__doc__ is not None
    assert "%LOCALAPPDATA%" in _resolve_executable_for_host.__doc__


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
        return "/fake/path/agy.cmd"

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


def _write_guarded_verdict_helper(root: Path, rel_path: str) -> None:
    helper = root / rel_path
    helper.parent.mkdir(parents=True, exist_ok=True)
    helper.write_text(
        "from scripts.verdict_evidence_anchor_preflight import validate_verdict_evidence_anchors\n"
        "\n"
        "def _assert_verdict_evidence_anchors():\n"
        "    return validate_verdict_evidence_anchors\n",
        encoding="utf-8",
    )


def test_inspect_verdict_anchor_guard_detects_helper_coverage(tmp_path):
    validator = tmp_path / "scripts" / "verdict_evidence_anchor_preflight.py"
    validator.parent.mkdir(parents=True, exist_ok=True)
    validator.write_text("# fixture\n", encoding="utf-8")
    _write_guarded_verdict_helper(tmp_path, ".codex/skills/gtkb-verify/helpers/write_verdict.py")

    result = inspect_verdict_anchor_guard(tmp_path)

    assert result["ok"] is True
    assert result["validator"]["exists"] is True
    assert ".codex/skills/gtkb-verify/helpers/write_verdict.py" in result["guarded_helpers"]


def test_evaluate_readiness_reports_verdict_anchor_guard(tmp_path, monkeypatch):
    _write_registry(tmp_path, _antigravity_record(can_receive_dispatch=True))
    monkeypatch.setattr(
        "scripts.verify_antigravity_dispatch.shutil.which",
        lambda exe: "/fake/path/agy.cmd" if exe == "agy" else None,
    )
    validator = tmp_path / "scripts" / "verdict_evidence_anchor_preflight.py"
    validator.parent.mkdir(parents=True, exist_ok=True)
    validator.write_text("# fixture\n", encoding="utf-8")
    _write_guarded_verdict_helper(tmp_path, ".claude/skills/gtkb-verify/helpers/write_verdict.py")

    result = evaluate_readiness(project_root=tmp_path, recipient="C")

    assert result["ready"] is True
    assert result["verdict_anchor_guard"]["ok"] is True
    assert ".claude/skills/gtkb-verify/helpers/write_verdict.py" in result["verdict_anchor_guard"]["guarded_helpers"]


def test_readiness_fails_closed_for_legacy_gemini_registry(tmp_path):
    _write_registry(
        tmp_path,
        _antigravity_record(
            invocation_surfaces={"headless": {"argv": ["gemini", "-p", "{{PROMPT}}"]}},
        ),
    )

    result = evaluate_readiness(project_root=tmp_path, recipient="C")

    assert result["ready"] is False
    assert result["first_failed_check"].startswith("registry agy headless argv")


def test_readiness_reports_dispatchable_when_agy_enabled(tmp_path, monkeypatch):
    _write_registry(tmp_path, _antigravity_record(can_receive_dispatch=True))
    monkeypatch.setattr(
        "scripts.verify_antigravity_dispatch.shutil.which",
        lambda exe: "/fake/path/agy.cmd" if exe == "agy" else None,
    )

    result = evaluate_readiness(project_root=tmp_path, recipient="C")

    assert result["ready"] is True
    assert result["dispatchable_now"] is True


def test_live_probe_requires_non_empty_output(tmp_path, monkeypatch):
    _write_registry(tmp_path, _antigravity_record(can_receive_dispatch=True))
    monkeypatch.setattr(
        "scripts.verify_antigravity_dispatch.shutil.which",
        lambda exe: "/fake/path/agy.cmd" if exe == "agy" else None,
    )

    def blank_runner(command, **kwargs):
        assert kwargs["stdin"] == subprocess.DEVNULL
        assert kwargs["capture_output"] is True
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    result = evaluate_readiness(
        project_root=tmp_path,
        recipient="C",
        require_live=True,
        live_runner=blank_runner,
    )

    assert result["ready"] is False
    assert result["dispatchable_now"] is False
    assert result["first_failed_check"].startswith("live agy prompt probe")


def test_live_probe_recovers_agy_response_from_conversation_db(tmp_path, monkeypatch):
    _write_registry(tmp_path, _antigravity_record(can_receive_dispatch=True))
    monkeypatch.setattr(
        "scripts.verify_antigravity_dispatch.shutil.which",
        lambda exe: "/fake/path/agy.cmd" if exe == "agy" else None,
    )
    conversations_dir = tmp_path / "conversations"
    _write_conversation_db(
        conversations_dir,
        step_type=15,
        payload=b"READY GTKB_AGY_READY_fixture",
    )
    monkeypatch.setattr(
        "scripts.verify_antigravity_dispatch._antigravity_conversations_dir",
        lambda: conversations_dir,
    )

    class FakeUuid:
        hex = "fixture"

    monkeypatch.setattr("scripts.verify_antigravity_dispatch.uuid.uuid4", lambda: FakeUuid())

    def blank_runner(command, **kwargs):
        assert "READY GTKB_AGY_READY_fixture" in " ".join(command)
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    result = evaluate_readiness(
        project_root=tmp_path,
        recipient="C",
        require_live=True,
        live_runner=blank_runner,
    )

    assert result["ready"] is True
    assert result["dispatchable_now"] is True
    assert result["live_probe"]["output_recovered"] is True
    assert result["live_probe"]["recovery"]["step_idx"] == 1


def test_live_probe_does_not_recover_prompt_only_conversation_row(tmp_path, monkeypatch):
    _write_registry(tmp_path, _antigravity_record(can_receive_dispatch=True))
    monkeypatch.setattr(
        "scripts.verify_antigravity_dispatch.shutil.which",
        lambda exe: "/fake/path/agy.cmd" if exe == "agy" else None,
    )
    conversations_dir = tmp_path / "conversations"
    _write_conversation_db(
        conversations_dir,
        step_type=14,
        payload=b"Reply with exactly: READY GTKB_AGY_READY_fixture",
    )
    monkeypatch.setattr(
        "scripts.verify_antigravity_dispatch._antigravity_conversations_dir",
        lambda: conversations_dir,
    )

    class FakeUuid:
        hex = "fixture"

    monkeypatch.setattr("scripts.verify_antigravity_dispatch.uuid.uuid4", lambda: FakeUuid())

    def blank_runner(command, **kwargs):
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    result = evaluate_readiness(
        project_root=tmp_path,
        recipient="C",
        require_live=True,
        live_runner=blank_runner,
    )

    assert result["ready"] is False
    assert result["live_probe"]["output_recovered"] is False
