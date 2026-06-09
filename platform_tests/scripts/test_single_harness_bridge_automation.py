# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for the single-harness bridge automation activation manager."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
AUTOMATION_PATH = PROJECT_ROOT / "scripts" / "single_harness_bridge_automation.py"
CLAUDE_SETTINGS = PROJECT_ROOT / ".claude" / "settings.json"
CODEX_HOOKS = PROJECT_ROOT / ".codex" / "hooks.json"


def _load_automation() -> ModuleType:
    name = "single_harness_bridge_automation_for_test"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, AUTOMATION_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _make_project(root: Path, *, topology: str) -> Path:
    (root / "groundtruth.toml").write_text(
        '[project]\nproject_name = "AutomationFixture"\nprofile = "dual-agent"\n',
        encoding="utf-8",
    )
    (root / "bridge").mkdir()
    (root / "bridge" / "INDEX.md").write_text(
        "# bridge index\n\nDocument: example\nNEW: bridge/example-001.md\n",
        encoding="utf-8",
    )
    (root / "bridge" / "example-001.md").write_text(
        "bridge_kind: implementation_proposal\n",
        encoding="utf-8",
    )
    harness_state = root / "harness-state"
    harness_state.mkdir()
    (harness_state / "harness-identities.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "harnesses": {
                    "claude": {"id": "B"},
                    "codex": {"id": "A"},
                },
            }
        ),
        encoding="utf-8",
    )
    if topology == "codex-single":
        harnesses = [
            {
                "id": "A",
                "harness_name": "codex",
                "harness_type": "codex",
                "status": "active",
                "role": ["prime-builder", "loyal-opposition"],
                "event_driven_hooks": True,
            }
        ]
    elif topology == "claude-single":
        harnesses = [
            {
                "id": "B",
                "harness_name": "claude",
                "harness_type": "claude",
                "status": "active",
                "role": ["prime-builder", "loyal-opposition"],
                "event_driven_hooks": True,
            }
        ]
    elif topology == "multi":
        harnesses = [
            {
                "id": "A",
                "harness_name": "codex",
                "harness_type": "codex",
                "status": "active",
                "role": ["loyal-opposition"],
                "event_driven_hooks": True,
            },
            {
                "id": "B",
                "harness_name": "claude",
                "harness_type": "claude",
                "status": "active",
                "role": ["prime-builder"],
                "event_driven_hooks": True,
            },
        ]
    else:
        raise AssertionError(f"unknown topology: {topology}")
    (harness_state / "harness-registry.json").write_text(
        json.dumps({"schema_version": 1, "harnesses": harnesses}),
        encoding="utf-8",
    )
    return root


def _patch_windows_task_calls(
    monkeypatch: pytest.MonkeyPatch,
    module: ModuleType,
    calls: list[tuple[str, dict]],
) -> None:
    monkeypatch.setattr(module.sys, "platform", "win32")
    monkeypatch.setattr(
        module,
        "_task_snapshot",
        lambda task_name: {"exists": False, "state": "Absent", "taskName": task_name},
    )

    def _install(**kwargs):
        calls.append(("install", kwargs))
        return {"returncode": 0, "stdout": "registered", "stderr": ""}

    def _uninstall(**kwargs):
        calls.append(("uninstall", kwargs))
        return {"returncode": 0, "stdout": "unregistered", "stderr": ""}

    monkeypatch.setattr(module, "_invoke_installer", _install)
    monkeypatch.setattr(module, "_invoke_uninstaller", _uninstall)


@pytest.mark.parametrize(
    ("topology", "expected_harness", "expected_handle"),
    [
        ("codex-single", "A", "codex"),
        ("claude-single", "B", "claude"),
    ],
)
def test_activation_installs_for_single_harness_topology(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    topology: str,
    expected_harness: str,
    expected_handle: str,
) -> None:
    module = _load_automation()
    root = _make_project(tmp_path, topology=topology)
    calls: list[tuple[str, dict]] = []
    _patch_windows_task_calls(monkeypatch, module, calls)

    payload = module.ensure_single_harness_automation(
        project_root=root,
        state_dir=tmp_path / "state",
        dry_run=True,
    )

    assert payload["single_harness_applicable"] is True
    assert payload["harness_id"] == expected_harness
    assert payload["command_handle"] == expected_handle
    assert payload["activated"] is True
    assert payload["action"] == "registered_or_updated"
    assert calls[0][0] == "install"
    assert calls[0][1]["max_items"] == 999


def test_activation_uninstalls_when_topology_is_not_single_harness(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_automation()
    root = _make_project(tmp_path, topology="multi")
    calls: list[tuple[str, dict]] = []
    _patch_windows_task_calls(monkeypatch, module, calls)

    payload = module.ensure_single_harness_automation(
        project_root=root,
        state_dir=tmp_path / "state",
        dry_run=True,
    )

    assert payload["single_harness_applicable"] is False
    assert payload["activated"] is False
    assert payload["action"] == "deactivated_not_single_harness"
    assert calls == [
        (
            "uninstall",
            {"project_root": root, "task_name": "GTKB-SingleHarnessBridgeDispatcher", "dry_run": True},
        )
    ]


def test_dispatch_now_uses_requested_full_queue_cap(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_automation()
    root = _make_project(tmp_path, topology="codex-single")
    calls: list[tuple[str, dict]] = []
    _patch_windows_task_calls(monkeypatch, module, calls)
    dispatcher = module._load_dispatcher_module()

    def _fake_dispatcher(**kwargs):
        return {
            "skipped": False,
            "max_items": kwargs["max_items"],
            "dry_run": kwargs["dry_run"],
        }

    monkeypatch.setattr(dispatcher, "run_dispatcher", _fake_dispatcher)

    payload = module.ensure_single_harness_automation(
        project_root=root,
        state_dir=tmp_path / "state",
        max_items=37,
        dispatch_now=True,
        dry_run=True,
    )

    assert payload["dispatch_now"] == {"skipped": False, "max_items": 37, "dry_run": True}


def _all_hook_commands(document: dict, event_name: str) -> list[str]:
    return [
        hook.get("command", "")
        for group in document.get("hooks", {}).get(event_name, [])
        for hook in group.get("hooks", [])
    ]


def test_codex_hooks_register_single_harness_activation_and_stop_dispatch() -> None:
    hooks = json.loads(CODEX_HOOKS.read_text(encoding="utf-8"))
    session_start = _all_hook_commands(hooks, "SessionStart")
    stop = _all_hook_commands(hooks, "Stop")

    assert any("single_harness_bridge_automation.py" in cmd and "--ensure" in cmd for cmd in session_start)
    assert any(
        "single_harness_bridge_automation.py" in cmd
        and "--ensure" in cmd
        and "--dispatch-now" in cmd
        and "--max-items 999" in cmd
        for cmd in stop
    )


def test_claude_settings_register_single_harness_activation_and_stop_dispatch() -> None:
    settings = json.loads(CLAUDE_SETTINGS.read_text(encoding="utf-8"))
    session_start = _all_hook_commands(settings, "SessionStart")
    stop = _all_hook_commands(settings, "Stop")

    assert any("single_harness_bridge_automation.py" in cmd and "--ensure" in cmd for cmd in session_start)
    assert any(
        "single_harness_bridge_automation.py" in cmd
        and "--ensure" in cmd
        and "--dispatch-now" in cmd
        and "--max-items 999" in cmd
        for cmd in stop
    )
