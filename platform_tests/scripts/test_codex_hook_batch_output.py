"""Regression tests for Codex hook batch stdout normalization."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
WRAPPER_PATH = REPO_ROOT / ".codex" / "gtkb-hooks" / "run_py_no_window.py"


def _load_wrapper():
    spec = importlib.util.spec_from_file_location("codex_run_py_no_window_for_tests", WRAPPER_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture()
def wrapper(monkeypatch: pytest.MonkeyPatch):
    module = _load_wrapper()
    monkeypatch.setitem(module.BATCHES, "fixture", (("py", "one.py"), ("py", "two.py")))
    monkeypatch.setattr(module, "_batch_command", lambda entry: [entry[1]])
    return module


def _run_with_stdout(wrapper, monkeypatch: pytest.MonkeyPatch, outputs: list[bytes]):
    calls = iter(outputs)

    def fake_run_child(command: list[str], payload: bytes) -> tuple[int, bytes, bytes]:
        return 0, next(calls), b""

    monkeypatch.setattr(wrapper, "_run_child", fake_run_child)
    return wrapper._run_batch("fixture", b'{"tool_name":"Bash"}')


def test_batch_collapses_multiple_noop_outputs_to_single_json(
    wrapper,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    returncode, stdout, stderr = _run_with_stdout(wrapper, monkeypatch, [b"{}", b"{}\n"])

    assert returncode == 0
    assert stderr == b""
    assert json.loads(stdout.decode()) == {}


def test_batch_preserves_deny_decision_as_single_json(wrapper, monkeypatch: pytest.MonkeyPatch) -> None:
    deny = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": "blocked by fixture",
        }
    }

    returncode, stdout, stderr = _run_with_stdout(wrapper, monkeypatch, [b"{}", json.dumps(deny).encode()])

    assert returncode == 0
    assert stderr == b""
    parsed = json.loads(stdout.decode())
    assert parsed["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert parsed["hookSpecificOutput"]["permissionDecisionReason"] == "blocked by fixture"


def test_batch_converts_legacy_block_decision_to_codex_deny(
    wrapper,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    returncode, stdout, stderr = _run_with_stdout(
        wrapper,
        monkeypatch,
        [b"{}", b'{"decision":"block","reason":"legacy block"}'],
    )

    assert returncode == 0
    assert stderr == b""
    parsed = json.loads(stdout.decode())
    assert parsed["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert parsed["hookSpecificOutput"]["permissionDecisionReason"] == "legacy block"


def test_batch_fails_closed_on_malformed_child_stdout(wrapper, monkeypatch: pytest.MonkeyPatch) -> None:
    returncode, stdout, stderr = _run_with_stdout(wrapper, monkeypatch, [b"{}", b"not-json"])

    assert returncode == 0
    assert b"emitted invalid hook JSON" in stderr
    parsed = json.loads(stdout.decode())
    assert parsed["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert "two.py emitted invalid hook JSON" in parsed["hookSpecificOutput"]["permissionDecisionReason"]


def test_batch_merges_context_payloads(wrapper, monkeypatch: pytest.MonkeyPatch) -> None:
    returncode, stdout, stderr = _run_with_stdout(
        wrapper,
        monkeypatch,
        [b'{"additionalContext":"one"}', b'{"additionalContext":"two"}'],
    )

    assert returncode == 0
    assert stderr == b""
    assert json.loads(stdout.decode()) == {"additionalContext": "one\n\ntwo"}
