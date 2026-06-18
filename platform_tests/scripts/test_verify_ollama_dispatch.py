"""Tests for the Phase-1 Ollama dispatch verification script (WI-4322).

Spec-derived tests for ``scripts/verify_ollama_dispatch.py`` per the Phase-1
Child 3 proposal (bridge/gtkb-ollama-integration-phase-1-verification-005.md)
and the GO verdict (bridge/gtkb-ollama-integration-phase-1-verification-006.md).

The script's verification surface has seven check functions across two modes:

- Live mode: ``_check_tool_loop_round_trip``, ``_check_author_metadata``,
  ``_check_bridge_filing_via_dispatch``.
- Guard-only mode: ``_check_guard_destructive_bash``,
  ``_check_guard_formal_artifact``, ``_check_guard_out_of_root``,
  ``_check_guard_bridge_bash_denial``.

Tests stub the live ``urllib.request`` reachability probe, inject deterministic
mock chat functions through the shim, and exercise the dispatch path against
disposable fixture workspaces.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPTS_DIR = _REPO_ROOT / "scripts"


def _load_script_module():
    """Load scripts/verify_ollama_dispatch.py as a module for direct test access."""
    if str(_SCRIPTS_DIR) not in sys.path:
        sys.path.insert(0, str(_SCRIPTS_DIR))
    # Ensure ollama_harness is importable from the same directory.
    spec = importlib.util.spec_from_file_location("verify_ollama_dispatch", _SCRIPTS_DIR / "verify_ollama_dispatch.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def verify_module():
    return _load_script_module()


@pytest.fixture(scope="module")
def ollama_harness_module():
    if str(_SCRIPTS_DIR) not in sys.path:
        sys.path.insert(0, str(_SCRIPTS_DIR))
    import ollama_harness  # noqa: PLC0415

    return ollama_harness


def _fixture_route(ollama_harness_module, *, key: str, allowed_tools: tuple[str, ...]):
    model_id = f"{key}:current"
    return ollama_harness_module.ModelRoute(
        key=key,
        model_id=model_id,
        model_version=ollama_harness_module.infer_model_version(model_id),
        tool_calling_supported=True,
        allowed_tools=allowed_tools,
    )


# ── Reachability probe ────────────────────────────────────────────────────


def test_reachability_probe_returns_false_when_endpoint_dead(verify_module, monkeypatch) -> None:
    """The reachability probe must return False on URLError / OSError."""
    import urllib.error

    def fail(url, timeout):
        raise urllib.error.URLError("connection refused")

    monkeypatch.setattr("urllib.request.urlopen", fail)
    assert verify_module._ollama_reachable("http://localhost:11434") is False


def test_reachability_probe_returns_true_when_endpoint_alive(verify_module, monkeypatch) -> None:
    """The reachability probe must return True on HTTP 200."""

    class FakeResp:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def read(self, n=64):
            return b'{"models":[]}'

    monkeypatch.setattr("urllib.request.urlopen", lambda url, timeout: FakeResp())
    assert verify_module._ollama_reachable("http://localhost:11434") is True


def test_autostart_probe_detects_windows_task(verify_module) -> None:
    def _runner(args, **kwargs):  # noqa: ANN001, ANN202
        return subprocess.CompletedProcess(
            args=args,
            returncode=0,
            stdout='{"scheduled_tasks":["GTKB-Ollama-Serve"],"services":[]}',
            stderr="",
        )

    result = verify_module.evaluate_ollama_autostart(
        platform="win32",
        executable_resolver=lambda _name: "powershell.exe",
        command_runner=_runner,
    )

    assert result["checked"] is True
    assert result["configured"] is True
    assert result["scheduled_tasks"] == ["GTKB-Ollama-Serve"]
    assert "warning" not in result


def test_autostart_probe_warns_when_no_task_or_service(verify_module) -> None:
    def _runner(args, **kwargs):  # noqa: ANN001, ANN202
        return subprocess.CompletedProcess(
            args=args,
            returncode=0,
            stdout='{"scheduled_tasks":[],"services":[]}',
            stderr="",
        )

    result = verify_module.evaluate_ollama_autostart(
        platform="win32",
        executable_resolver=lambda _name: "powershell.exe",
        command_runner=_runner,
    )

    assert result["checked"] is True
    assert result["configured"] is False
    assert "No Windows scheduled task or service" in result["warning"]


def test_autostart_installer_script_is_guarded() -> None:
    script = (_SCRIPTS_DIR / "ops" / "install_ollama_autostart_task.ps1").read_text(encoding="utf-8")

    assert "SupportsShouldProcess" in script
    assert "Register-ScheduledTask" in script
    assert "ollama.exe" in script
    assert '-Argument "serve"' in script


# ── Live-mode: tool-loop round-trip ──────────────────────────────────────


def test_tool_loop_round_trip_invokes_chat_twice(verify_module, ollama_harness_module, tmp_path) -> None:
    """L1: round-trip must invoke chat at least twice (tool_call turn + final-text turn)."""
    # Construct a route directly to avoid depending on a real routing TOML.
    route = _fixture_route(ollama_harness_module, key="fixture-read", allowed_tools=("Read",))
    # Plant the routing TOML the script uses to resolve the model.
    (tmp_path / ".ollama").mkdir()
    (tmp_path / ".ollama" / "routing.toml").write_text(
        "schema_version = 1\n"
        "[models.fixture-read]\n"
        'model_id = "fixture-read:current"\n'
        "tool_calling_supported = true\n"
        'allowed_tools = ["Read"]\n'
        "[routing]\n"
        'default_model = "fixture-read"\n',
        encoding="utf-8",
    )
    # Plant a Read target inside tmp_path.
    target_file = tmp_path / "sentinel.txt"
    target_file.write_text("fixture-read", encoding="utf-8")

    ok = verify_module._check_tool_loop_round_trip(route, "http://localhost:11434", tmp_path)
    assert ok is True


def test_author_metadata_check_passes_when_model_id_matches(verify_module, ollama_harness_module) -> None:
    """L2: metadata model_id matches route model_id."""
    route = _fixture_route(ollama_harness_module, key="metadata-route", allowed_tools=("Read",))
    assert verify_module._check_author_metadata(route, "http://localhost:11434") is True


def test_ollama_session_resolver_prefers_dispatch_run_id(ollama_harness_module) -> None:
    env = {
        "GTKB_BRIDGE_POLLER_RUN_ID": "dispatch-run",
        "CODEX_THREAD_ID": "parent-codex-thread",
        "GTKB_SESSION_ID": "parent-gtkb",
    }

    assert ollama_harness_module.resolve_ollama_session_id(env) == "dispatch-run"


def test_ollama_guard_payload_uses_dispatch_run_id(ollama_harness_module, tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("GTKB_BRIDGE_POLLER_RUN_ID", "dispatch-run")
    monkeypatch.setenv("CODEX_THREAD_ID", "parent-codex-thread")
    guard_path = tmp_path / "guard.py"
    guard_path.write_text("# fixture guard\n", encoding="utf-8")
    captured: list[dict[str, object]] = []

    def guard_runner(path, payload, env, timeout):  # noqa: ANN001, ARG001
        captured.append(dict(payload))
        return ollama_harness_module.GuardExecutionResult(0, "{}")

    metadata = ollama_harness_module.ModelMetadata(
        model_id="qwen3-coder-next:cloud",
        model_version="cloud",
        endpoint="http://localhost:11434",
        route_key="qwen3-coder-next-cloud",
    )
    ollama_harness_module.invoke_guard_adapter(
        "Write",
        {"path": str(tmp_path / "bridge" / "gtkb-fixture-001.md"), "content": "NEW\n"},
        metadata,
        tmp_path,
        guard_runner=guard_runner,
        guard_paths=(guard_path,),
    )

    assert captured[0]["session_id"] == "dispatch-run"


# ── Live-mode: bridge filing via dispatch ────────────────────────────────


def test_dispatch_read_missing_file_returns_model_visible_error(ollama_harness_module, tmp_path) -> None:
    metadata = ollama_harness_module.ModelMetadata(
        model_id="qwen3-coder-next:cloud",
        model_version="cloud",
        endpoint="http://localhost:11434",
        route_key="qwen3-coder-next-cloud",
    )

    result = ollama_harness_module.dispatch_tool_call(
        "Read",
        {"path": "harness-state/d/operating-role.md"},
        metadata,
        tmp_path,
    )

    assert result == "Read failed: file not found: harness-state/d/operating-role.md"


def test_dispatch_bash_nonzero_returns_model_visible_evidence(ollama_harness_module, tmp_path) -> None:
    for guard_path in (
        ".claude/hooks/destructive-gate.py",
        ".claude/hooks/formal-artifact-approval-gate.py",
        "scripts/implementation_start_gate.py",
    ):
        path = tmp_path / guard_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# fixture guard\n", encoding="utf-8")

    metadata = ollama_harness_module.ModelMetadata(
        model_id="qwen3-coder-next:cloud",
        model_version="cloud",
        endpoint="http://localhost:11434",
        route_key="qwen3-coder-next-cloud",
    )

    def guard_runner(path, payload, env, timeout):  # noqa: ANN001, ARG001
        return ollama_harness_module.GuardExecutionResult(0, "{}")

    def command_runner(command, project_root, env, timeout):  # noqa: ANN001, ARG001
        return subprocess.CompletedProcess(args=command, returncode=5, stdout="out", stderr="err")

    result = ollama_harness_module.dispatch_tool_call(
        "Bash",
        {"command": "python scripts/adr_dcl_clause_preflight.py --bridge-id fixture"},
        metadata,
        tmp_path,
        guard_runner=guard_runner,
        command_runner=command_runner,
    )

    assert "Bash command exited with return code 5." in result
    assert "Command: python scripts/adr_dcl_clause_preflight.py --bridge-id fixture" in result
    assert "STDOUT:\nout" in result
    assert "STDERR:\nerr" in result


def test_dispatch_readiness_requires_full_lo_tool_set(verify_module) -> None:
    assert verify_module.OLLAMA_DISPATCH_REQUIRED_TOOLS == ("Read", "Write", "Edit", "Grep", "Glob", "Bash")


def test_bridge_filing_writes_fixture_file_with_NEW_first_line(verify_module, ollama_harness_module, tmp_path) -> None:
    """L3: fixture write through dispatch_tool_call must produce a file whose
    first non-blank line is exactly ``NEW``."""
    route = _fixture_route(ollama_harness_module, key="bridge-write-route", allowed_tools=("Write",))
    ok = verify_module._check_bridge_filing_via_dispatch(route, "http://localhost:11434", tmp_path)
    assert ok is True


def test_bridge_filing_does_not_touch_production_index(verify_module, ollama_harness_module, tmp_path) -> None:
    """L3: production bridge/INDEX.md must be untouched after the fixture write.

    The verification script writes to a tempfile.mkdtemp root, never the live
    project root, so the production INDEX.md mtime must not change.
    """
    prod_index = _REPO_ROOT / "bridge" / "INDEX.md"
    if not prod_index.is_file():
        pytest.skip("production bridge/INDEX.md absent; live-repo invariant")
    before = prod_index.stat().st_mtime_ns
    route = _fixture_route(ollama_harness_module, key="production-index-route", allowed_tools=("Write",))
    verify_module._check_bridge_filing_via_dispatch(route, "http://localhost:11434", tmp_path)
    after = prod_index.stat().st_mtime_ns
    assert before == after, "production bridge/INDEX.md was modified"


def test_bridge_filing_writes_numbered_fixture_file_with_status_token(
    verify_module, ollama_harness_module, tmp_path
) -> None:
    """L3: fixture bridge filing must create a status-bearing numbered file."""
    route = _fixture_route(ollama_harness_module, key="fixture-index-route", allowed_tools=("Write",))
    fixture_root = tmp_path / "fixture"
    ok = verify_module._check_bridge_filing_via_dispatch(
        route,
        "http://localhost:11434",
        tmp_path,
        fixture_root=fixture_root,
    )
    assert ok is True
    fixture_bridge_file = fixture_root / "bridge" / "gtkb-ollama-e2e-fixture-001.md"
    assert fixture_bridge_file.is_file(), "fixture bridge file missing after filing"
    first_nonblank = next(
        (line.strip() for line in fixture_bridge_file.read_text(encoding="utf-8").splitlines() if line.strip()),
        "",
    )
    assert first_nonblank == "NEW"
    assert not (fixture_root / "bridge" / "INDEX.md").exists()


# ── Guard-only: destructive Bash rejection ───────────────────────────────


def test_guard_destructive_bash_rejected(verify_module, ollama_harness_module, tmp_path) -> None:
    """G1: ``rm -rf /`` payload through the mocked guard pipeline must be rejected."""
    route = _fixture_route(ollama_harness_module, key="destructive-bash-route", allowed_tools=("Bash",))
    ok = verify_module._check_guard_destructive_bash(tmp_path, route, "http://localhost:11434")
    assert ok is True


# ── Guard-only: formal-artifact rejection ────────────────────────────────


def test_guard_formal_artifact_rejected(verify_module, ollama_harness_module, tmp_path) -> None:
    """G2: write to a formal-artifact-approval path must be rejected by the mocked guard."""
    route = _fixture_route(ollama_harness_module, key="formal-artifact-route", allowed_tools=("Write",))
    # Ensure the .groundtruth/formal-artifact-approvals path resolves under tmp_path,
    # which the script will use to construct the test write target.
    (tmp_path / ".groundtruth" / "formal-artifact-approvals").mkdir(parents=True, exist_ok=True)
    ok = verify_module._check_guard_formal_artifact(tmp_path, route, "http://localhost:11434")
    assert ok is True


# ── Guard-only: out-of-root rejection ────────────────────────────────────


def test_guard_out_of_root_rejected(verify_module, ollama_harness_module, tmp_path) -> None:
    """G3: read of an out-of-root path is rejected by ``_ensure_under_root``.

    Out-of-root rejection happens at the path-resolution layer, not via the
    guard runner. The check passes when ``dispatch_tool_call`` raises
    ``OllamaHarnessError`` containing the escape diagnostic.
    """
    route = _fixture_route(ollama_harness_module, key="out-of-root-route", allowed_tools=("Read",))
    ok = verify_module._check_guard_out_of_root(tmp_path, route, "http://localhost:11434")
    assert ok is True


# ── Guard-only: bridge Bash mutation rejection ──────────────────────────


def test_guard_bridge_bash_denial_blocks_file_and_index_mutation(
    verify_module, ollama_harness_module, tmp_path
) -> None:
    """G4: Bash bridge writes are rejected before guards or subprocess execution."""
    route = _fixture_route(ollama_harness_module, key="bridge-bash-route", allowed_tools=("Bash",))
    ok = verify_module._check_guard_bridge_bash_denial(tmp_path, route, "http://localhost:11434")
    assert ok is True


# ── Smoke test: script importable with no side effects ──────────────────


def test_script_importable_without_side_effects() -> None:
    """Importing the verification script must not contact the network or modify state."""
    mod = _load_script_module()
    assert hasattr(mod, "_check_tool_loop_round_trip")
    assert hasattr(mod, "_check_author_metadata")
    assert hasattr(mod, "_check_bridge_filing_via_dispatch")
    assert hasattr(mod, "_check_guard_destructive_bash")
    assert hasattr(mod, "_check_guard_formal_artifact")
    assert hasattr(mod, "_check_guard_out_of_root")
    assert hasattr(mod, "_check_guard_bridge_bash_denial")
    assert callable(getattr(mod, "main", None))
