from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from scripts.sdk_bridge_bash_guard import (
    BridgeDeliveryIncomplete,
    NativeBindFailed,
    bind_native_context,
    bridge_bash_mutation_reason,
    bridge_completion_target,
    protected_bridge_paths,
)

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize(
    "command",
    [
        "Get-Content bridge/example-001.md",
        "Get-Content bridge/INDEX.md",
        "git diff -- bridge/example-001.md",
        "python -c \"from pathlib import Path; print(Path('bridge/example-001.md').read_text())\"",
    ],
)
def test_read_only_bridge_references_are_allowed(command: str) -> None:
    assert bridge_bash_mutation_reason(command) is None


@pytest.mark.parametrize(
    "command",
    [
        "echo GO > bridge/example-001.md",
        "echo GO > bridge/INDEX.md",
        "Set-Content bridge/example-001.md 'GO'",
        "Set-Content bridge/INDEX.md 'GO'",
        "Move-Item tmp.md bridge/example-001.md",
        "python -c \"from pathlib import Path; Path('bridge/example-001.md').write_text('GO')\"",
        "python -c \"import os; os.replace('tmp.md', r'E:\\GT-KB\\bridge\\example-001.md')\"",
        "git restore -- bridge/example-001.md",
    ],
)
def test_bridge_mutation_shapes_are_denied(command: str) -> None:
    reason = bridge_bash_mutation_reason(command)

    assert reason is not None
    assert "Bash bridge artifact mutation denied" in reason
    assert "gt bridge deliver" in reason
    assert "exact next-artifact claim" in reason


@pytest.mark.parametrize(
    "command",
    [
        'python scripts/ollama_harness.py -p "review"',
        'python scripts/alibaba_cloud_studio_harness.py -p "review"',
        'python scripts/qualification_harness.py -p "review"',
        'groundtruth-kb/.venv/Scripts/python.exe scripts/openrouter_harness.py -p "review"',
        r'& "E:\GT-KB\groundtruth-kb\.venv\Scripts\pythonw.exe" scripts\ollama_harness.py -p "review"',
    ],
)
def test_sdk_harness_self_invocation_is_denied(command: str) -> None:
    reason = bridge_bash_mutation_reason(command)

    assert reason is not None
    assert "Bash SDK harness self-invocation denied" in reason
    assert "scripts/" in reason


@pytest.mark.parametrize(
    "command",
    [
        "Get-Content scripts/ollama_harness.py",
        "python -c \"print('scripts/ollama_harness.py')\"",
        "rg ollama_harness scripts",
    ],
)
def test_sdk_harness_benign_references_are_allowed(command: str) -> None:
    assert bridge_bash_mutation_reason(command) is None


def test_protected_paths_are_deduplicated_and_preserve_first_spelling() -> None:
    paths = protected_bridge_paths("type bridge\\example-001.md; echo x > bridge/example-001.md")

    assert paths == ("bridge\\example-001.md",)


# c123 (batch design WP2 2.3): an assigned bridge target is the launcher's two arguments; a role skill no longer
# makes a run bridge work.


@pytest.mark.parametrize(
    ("document", "version", "expected"),
    [(None, None, None), ("assigned", 2, ("assigned", 2))],
)
def test_a_bridge_target_is_required_only_when_a_document_or_version_is_given(document, version, expected) -> None:
    assert bridge_completion_target(document, version) == expected


@pytest.mark.parametrize(
    ("document", "version"),
    [("assigned", None), (None, 2), ("", 2), ("  ", 2), ("assigned", 0), ("assigned", True), ("assigned", "2")],
)
def test_a_partial_or_invalid_bridge_target_is_refused_before_launch(document, version) -> None:
    with pytest.raises(BridgeDeliveryIncomplete, match="--bridge-document and --bridge-version") as refused:
        bridge_completion_target(document, version)
    assert refused.value.code == "bridge_delivery_incomplete"


def test_a_role_skill_is_no_longer_a_bridge_target_argument() -> None:
    with pytest.raises(TypeError):
        bridge_completion_target("bridge-review", None, None)


# c123 (batch design WP2 2.1): the API launchers bind their own context with the --init line before the first
# provider call, through gt session bind and the checks of the DeepSeek SDK launcher.
BINDING = {"session_context_id": "session-1", "role": "loyal-opposition", "native_context_id": "native-1"}


def _bind_runner(calls: list, *, returncode: int = 0, stdout: str = "", raises: BaseException | None = None):
    def runner(command, cwd, env, timeout):
        calls.append((command, cwd, dict(env), timeout))
        if raises is not None:
            raise raises
        return subprocess.CompletedProcess(command, returncode, stdout=stdout, stderr="")

    return runner


@pytest.mark.parametrize("status", ["init_requested", "already_initialized_idempotent"])
def test_bind_native_context_binds_through_the_native_cli_and_returns_the_binding(status, tmp_path, monkeypatch):
    monkeypatch.setenv("PGPASSWORD", "fixture-never-forwarded")
    monkeypatch.setenv("GT_POSTGRES_DSN", "fixture-never-forwarded")
    monkeypatch.setenv("GTKB_AUTHOR_SESSION_CONTEXT_ID", "parent-context")
    calls: list = []
    runner = _bind_runner(calls, stdout=json.dumps({"status": status, "binding": BINDING}))

    assert bind_native_context("native-1", "::init gtkb lo", tmp_path, runner=runner) == BINDING

    ((command, cwd, env, timeout),) = calls
    assert "-m groundtruth_kb session bind --native-context-id native-1 --init-keyword " in command
    assert "::init gtkb lo" in command and command.endswith(" --json")
    assert cwd == tmp_path and timeout is None
    assert not [key for key in env if key.startswith(("PG", "GT_POSTGRES_"))]
    assert "GTKB_AUTHOR_SESSION_CONTEXT_ID" not in env
    assert (env["GT_PROJECT_ROOT"], env["GTKB_NATIVE_CONTEXT_ID"], env["PYTHONIOENCODING"]) == (
        str(tmp_path),
        "native-1",
        "utf-8",
    )


@pytest.mark.parametrize(
    ("returncode", "response", "message"),
    [
        pytest.param(
            2, {"status": "init_requested", "binding": BINDING}, "gt session bind exited 2", id="nonzero_exit"
        ),
        pytest.param(0, "not JSON", "unavailable or returned no JSON", id="not_json"),
        pytest.param(
            0, {"status": "init_refused", "binding": BINDING}, "lacks a successful outcome and binding", id="status"
        ),
        pytest.param(0, {"status": "init_requested"}, "lacks a successful outcome and binding", id="no_binding"),
        pytest.param(0, ["init_requested", BINDING], "lacks a successful outcome and binding", id="not_an_object"),
        pytest.param(
            0,
            {"status": "init_requested", "binding": {**BINDING, "session_context_id": " "}},
            "lacks identity or role",
            id="empty_session_context",
        ),
        pytest.param(
            0,
            {"status": "init_requested", "binding": {**BINDING, "role": ""}},
            "lacks identity or role",
            id="empty_role",
        ),
        pytest.param(
            0,
            {"status": "init_requested", "binding": {**BINDING, "native_context_id": "native-2"}},
            "names a different native context",
            id="other_native_context",
        ),
    ],
)
def test_bind_native_context_refuses_what_is_not_a_bound_context(returncode, response, message, tmp_path):
    stdout = response if isinstance(response, str) else json.dumps(response)
    runner = _bind_runner([], returncode=returncode, stdout=stdout)

    with pytest.raises(NativeBindFailed, match=message) as refused:
        bind_native_context("native-1", "::init gtkb lo", tmp_path, runner=runner)

    assert refused.value.code == "native_bind_failed"
    assert str(refused.value).startswith("native_bind_failed: ")


@pytest.mark.parametrize("error", [OSError("interpreter unavailable"), subprocess.TimeoutExpired("gt session bind", 5)])
def test_bind_native_context_refuses_an_unavailable_native_cli(error, tmp_path):
    with pytest.raises(NativeBindFailed, match="unavailable or returned no JSON"):
        bind_native_context("native-1", "::init gtkb lo", tmp_path, runner=_bind_runner([], raises=error))


@pytest.mark.parametrize("stdout", [None, ""], ids=["no_stdout", "empty_stdout"])
def test_bind_native_context_refuses_a_response_without_output(stdout, tmp_path):
    """A runner that hands back no stdout is refused as "no JSON" (exit 4), never a TypeError traceback."""

    def runner(command, cwd, env, timeout):
        return subprocess.CompletedProcess(command, 0, stdout=stdout, stderr="")

    with pytest.raises(NativeBindFailed, match="unavailable or returned no JSON"):
        bind_native_context("native-1", "::init gtkb lo", tmp_path, runner=runner)
