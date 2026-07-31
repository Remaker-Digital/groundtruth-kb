"""Spec-derived tests for WI-5298 Codex snapshot-window containment."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "scripts" / "ops" / "codex_snapshot_window_hider.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("codex_snapshot_window_hider_under_test", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class _Process:
    def __init__(self, name: str, commandline: list[str] | None = None, parent=None):
        self._name = name
        self._commandline = commandline or []
        self._parent = parent

    def name(self) -> str:
        return self._name

    def cmdline(self) -> list[str]:
        return self._commandline

    def parent(self):
        return self._parent


def _qualifying_process_factory(module):
    chatgpt = _Process("ChatGPT.exe")
    git = _Process(
        "git.exe",
        ["C:\\Program Files\\Git\\cmd\\git.exe", *module.SNAPSHOT_GIT_ARGUMENTS],
        chatgpt,
    )
    conhost = _Process("conhost.exe", parent=git)
    return lambda pid: conhost if pid == 30 else None


def test_exact_codex_snapshot_console_is_hidden_once() -> None:
    module = _load_module()
    hidden: list[int] = []

    result = module.hide_qualifying_window(
        9001,
        pid_resolver=lambda hwnd: 30,
        hide_window=lambda hwnd: hidden.append(hwnd) or True,
        process_factory=_qualifying_process_factory(module),
    )

    assert result is True
    assert hidden == [9001]


@pytest.mark.parametrize(
    ("console_name", "git_args", "ancestor_name"),
    [
        ("cmd.exe", ["git.exe", "-c", "core.hooksPath=NUL", "-c", "core.fsmonitor=", "add", "-u"], "ChatGPT.exe"),
        ("conhost.exe", ["git.exe", "status"], "ChatGPT.exe"),
        (
            "conhost.exe",
            ["git.exe", "-c", "core.hooksPath=NUL", "-c", "core.fsmonitor=", "add", "-u", "--porcelain"],
            "ChatGPT.exe",
        ),
        ("conhost.exe", ["git.exe", "-c", "core.hooksPath=NUL", "-c", "core.fsmonitor=", "add", "-u"], "explorer.exe"),
    ],
)
def test_near_miss_process_topologies_remain_untouched(console_name, git_args, ancestor_name) -> None:
    module = _load_module()
    ancestor = _Process(ancestor_name)
    git = _Process("git.exe", git_args, ancestor)
    console = _Process(console_name, parent=git)
    hidden: list[int] = []

    result = module.hide_qualifying_window(
        9002,
        pid_resolver=lambda hwnd: 31,
        hide_window=lambda hwnd: hidden.append(hwnd) or True,
        process_factory=lambda pid: console,
    )

    assert result is False
    assert hidden == []


def test_process_inspection_failure_leaves_window_visible() -> None:
    module = _load_module()
    hidden: list[int] = []

    result = module.hide_qualifying_window(
        9003,
        pid_resolver=lambda hwnd: 32,
        hide_window=lambda hwnd: hidden.append(hwnd) or True,
        process_factory=lambda pid: (_ for _ in ()).throw(OSError("access denied")),
    )

    assert result is False
    assert hidden == []


def test_missing_process_metadata_leaves_window_visible() -> None:
    module = _load_module()
    hidden: list[int] = []

    result = module.hide_qualifying_window(
        9004,
        pid_resolver=lambda hwnd: 33,
        hide_window=lambda hwnd: hidden.append(hwnd) or True,
        process_factory=lambda pid: None,
    )

    assert result is False
    assert hidden == []


@pytest.mark.parametrize(
    ("event", "hwnd", "object_id", "child_id"),
    [
        (0x8001, 9005, 0, 0),
        (0x8002, 0, 0, 0),
        (0x8002, 9005, 1, 0),
        (0x8002, 9005, 0, 1),
    ],
)
def test_non_target_window_events_are_rejected(event, hwnd, object_id, child_id) -> None:
    module = _load_module()

    assert module.is_target_window_show_event(event, hwnd, object_id, child_id) is False


def test_top_level_window_show_event_is_accepted() -> None:
    module = _load_module()

    assert module.is_target_window_show_event(module.EVENT_OBJECT_SHOW, 9006, module.OBJID_WINDOW, 0)


def test_source_contains_only_hide_side_effect_and_no_dispatch_controls() -> None:
    body = MODULE_PATH.read_text(encoding="utf-8")

    assert "ShowWindowAsync" in body
    assert "SW_HIDE" in body
    assert "CreateMutexW" in body
    assert "ERROR_ALREADY_EXISTS" in body
    assert module_mutex_name_is_stable(body)
    for forbidden in (
        ".kill(",
        ".terminate(",
        "taskkill",
        "TerminateProcess",
        "SuspendThread",
        "can_receive_dispatch",
        "dispatch_quality",
        "harness-registry",
        "git add",
    ):
        assert forbidden not in body


def module_mutex_name_is_stable(body: str) -> bool:
    return 'MUTEX_NAME = "Local\\\\GTKB-CodexSnapshotWindowHider-v1"' in body
