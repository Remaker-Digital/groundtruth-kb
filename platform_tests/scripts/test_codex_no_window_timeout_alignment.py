# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for Codex no-window SessionStart timeout alignment."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
WRAPPER_PATH = REPO_ROOT / ".codex" / "gtkb-hooks" / "run_py_no_window.py"
SESSION_START_PATH = REPO_ROOT / ".codex" / "gtkb-hooks" / "session_start_dispatch.py"
ORDINARY_HOOK_PATH = REPO_ROOT / ".claude" / "hooks" / "spec-classifier.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("_codex_run_py_no_window_under_test", WRAPPER_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["_codex_run_py_no_window_under_test"] = module
    spec.loader.exec_module(module)
    return module


def test_session_start_child_uses_startup_service_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_module()
    monkeypatch.delenv("GTKB_CODEX_HOOK_CHILD_TIMEOUT_SECONDS", raising=False)
    monkeypatch.delenv(module.STARTUP_SERVICE_TIMEOUT_ENV, raising=False)

    assert module._child_timeout_seconds([sys.executable, str(SESSION_START_PATH)]) == pytest.approx(150.0)


def test_session_start_child_reads_startup_service_timeout_override(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_module()
    monkeypatch.delenv("GTKB_CODEX_HOOK_CHILD_TIMEOUT_SECONDS", raising=False)
    monkeypatch.setenv(module.STARTUP_SERVICE_TIMEOUT_ENV, "175.5")

    assert module._child_timeout_seconds([sys.executable, str(SESSION_START_PATH)]) == pytest.approx(175.5)


@pytest.mark.parametrize("value", ["not-a-number", "0", "-5"])
def test_session_start_child_rejects_invalid_startup_timeout_override(
    monkeypatch: pytest.MonkeyPatch, value: str
) -> None:
    module = _load_module()
    monkeypatch.delenv("GTKB_CODEX_HOOK_CHILD_TIMEOUT_SECONDS", raising=False)
    monkeypatch.setenv(module.STARTUP_SERVICE_TIMEOUT_ENV, value)

    assert module._child_timeout_seconds([sys.executable, str(SESSION_START_PATH)]) == pytest.approx(150.0)


def test_ordinary_child_keeps_short_default(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_module()
    monkeypatch.delenv("GTKB_CODEX_HOOK_CHILD_TIMEOUT_SECONDS", raising=False)
    monkeypatch.delenv(module.STARTUP_SERVICE_TIMEOUT_ENV, raising=False)

    assert module._child_timeout_seconds([sys.executable, str(ORDINARY_HOOK_PATH)]) == pytest.approx(10.0)


def test_explicit_wrapper_timeout_wins_for_session_start(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_module()
    monkeypatch.setenv("GTKB_CODEX_HOOK_CHILD_TIMEOUT_SECONDS", "22.25")
    monkeypatch.setenv(module.STARTUP_SERVICE_TIMEOUT_ENV, "175.5")

    assert module._child_timeout_seconds([sys.executable, str(SESSION_START_PATH)]) == pytest.approx(22.25)
