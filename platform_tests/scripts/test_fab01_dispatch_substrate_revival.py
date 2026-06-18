# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""FAB-01 dispatch-substrate-revival tests (WI-4413).

Covers ``bridge/gtkb-fab-01-dispatch-substrate-revival-001.md`` (Codex GO at
``-002``):

- **HYG-001 / step 1** — spawn-time argv normalization
  (``_normalize_argv_head`` + ``_harness_command``): a forward-slash-relative
  path or a bare ``PATHEXT`` command resolves to a launchable form instead of
  failing ``CreateProcess`` with ``WinError 2``.
- **step 2** — launchability doctor check (``_check_harness_launchability``):
  PASS when active dispatch targets resolve, FAIL on a ``WinError-2``-class
  unlaunchable argv head, WARN when no targets carry a headless argv.
- **HYG-004 / step 3** — capability-axis split projection: ``can_fire_events``
  vs ``can_receive_dispatch`` with the deprecated ``event_driven_hooks`` alias.
- **step 4** — gated scheduled wake (``_no_active_event_source_harness`` /
  ``_gated_wake_applicable`` / ``run_dispatcher(enforce_wake_gate=...)`` /
  automation activation): the wake activates in the degraded
  no-active-event-source topology and stays inert (mutually exclusive with the
  cross-harness trigger) when an event-source harness is active.

This module is skip-listed in ``platform_tests/scripts/conftest.py`` so the
autouse ``mock_harness_registry_for_tests`` fixture does not override the
synthetic per-test registries via ``GTKB_HARNESS_REGISTRY_PATH``.
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys
from pathlib import Path
from types import ModuleType

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
for _p in (PROJECT_ROOT / "groundtruth-kb" / "src", PROJECT_ROOT / "scripts"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

TRIGGER_PATH = PROJECT_ROOT / "scripts" / "cross_harness_bridge_trigger.py"
DISPATCHER_PATH = PROJECT_ROOT / "scripts" / "single_harness_bridge_dispatcher.py"
AUTOMATION_PATH = PROJECT_ROOT / "scripts" / "single_harness_bridge_automation.py"


def _load(name: str, path: Path) -> ModuleType:
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _trigger() -> ModuleType:
    return _load("cross_harness_bridge_trigger", TRIGGER_PATH)


def _dispatcher() -> ModuleType:
    return _load("single_harness_bridge_dispatcher", DISPATCHER_PATH)


def _automation() -> ModuleType:
    return _load("single_harness_bridge_automation", AUTOMATION_PATH)


# ---------------------------------------------------------------------------
# Topology fixtures
# ---------------------------------------------------------------------------

# All active harnesses are event-less (FAB-01 degraded topology): launchable
# dispatch targets exist but the cross-harness trigger has no active event
# source to fire it.
EVENTLESS_TOPOLOGY = [
    {
        "id": "C",
        "harness_name": "antigravity",
        "harness_type": "antigravity",
        "status": "active",
        "role": ["prime-builder"],
        "can_fire_events": False,
        "can_receive_dispatch": True,
        "event_driven_hooks": False,  # deprecated alias == can_fire_events
    },
    {
        "id": "D",
        "harness_name": "ollama",
        "harness_type": "ollama",
        "status": "active",
        "role": ["loyal-opposition"],
        "can_fire_events": False,
        "can_receive_dispatch": True,
        "event_driven_hooks": False,
    },
]

# Normal multi-harness topology: an event-source harness (claude B) is active,
# so the gated wake must stay inert and the cross-harness trigger is the sole
# substrate.
WITH_EVENT_SOURCE_TOPOLOGY = [
    {
        "id": "B",
        "harness_name": "claude",
        "harness_type": "claude",
        "status": "active",
        "role": ["prime-builder"],
        "can_fire_events": True,
        "can_receive_dispatch": True,
        "event_driven_hooks": True,
    },
    {
        "id": "D",
        "harness_name": "ollama",
        "harness_type": "ollama",
        "status": "active",
        "role": ["loyal-opposition"],
        "can_fire_events": False,
        "can_receive_dispatch": True,
        "event_driven_hooks": False,
    },
]

SINGLE_HARNESS_TOPOLOGY = [
    {
        "id": "B",
        "harness_name": "claude",
        "harness_type": "claude",
        "status": "active",
        "role": ["prime-builder", "loyal-opposition"],
        "can_fire_events": True,
        "can_receive_dispatch": True,
        "event_driven_hooks": True,
    },
]


def _make_topology_project(root: Path, harnesses: list[dict]) -> Path:
    (root / "groundtruth.toml").write_text(
        '[project]\nproject_name = "Fab01Fixture"\nprofile = "dual-agent"\n',
        encoding="utf-8",
    )
    (root / "bridge").mkdir()
    (root / "bridge" / "INDEX.md").write_text("# bridge index\n", encoding="utf-8")
    harness_state = root / "harness-state"
    harness_state.mkdir()
    (harness_state / "harness-identities.json").write_text(
        json.dumps({"schema_version": 1, "harnesses": {"claude": {"id": "B"}, "codex": {"id": "A"}}}),
        encoding="utf-8",
    )
    (harness_state / "harness-registry.json").write_text(
        json.dumps({"schema_version": 1, "source_of_truth": "test", "harnesses": harnesses}),
        encoding="utf-8",
    )
    return root


@pytest.fixture(autouse=True)
def _no_registry_env_override(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure synthetic per-test registries are read from project_root."""
    monkeypatch.delenv("GTKB_HARNESS_REGISTRY_PATH", raising=False)


# ---------------------------------------------------------------------------
# Step 1 — spawn-time argv normalization (HYG-001)
# ---------------------------------------------------------------------------


def test_normalize_argv_head_resolves_forward_slash_relative(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    trigger = _trigger()
    rooted = os.path.normpath(str(tmp_path / "groundtruth-kb/.venv/Scripts/python.exe"))
    seen: dict[str, str] = {}

    def fake_which(cmd: str) -> str | None:
        seen["arg"] = cmd
        return cmd if cmd == rooted else None

    monkeypatch.setattr(trigger.shutil, "which", fake_which)
    resolved = trigger._normalize_argv_head("groundtruth-kb/.venv/Scripts/python.exe", tmp_path)

    # The forward-slash-relative head is resolved against project_root with
    # native separators (the CreateProcess-launchable form).
    assert resolved == rooted
    assert seen["arg"] == rooted


def test_normalize_argv_head_resolves_bare_pathext_command(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    trigger = _trigger()

    def fake_which(cmd: str) -> str | None:
        return "C:/tools/gemini.cmd" if cmd == "gemini" else None

    monkeypatch.setattr(trigger.shutil, "which", fake_which)
    # A bare command (no separator) is PATHEXT-resolved by shutil.which.
    assert trigger._normalize_argv_head("gemini", tmp_path) == "C:/tools/gemini.cmd"


def test_normalize_argv_head_falls_back_when_unresolvable(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    trigger = _trigger()
    monkeypatch.setattr(trigger.shutil, "which", lambda cmd: None)
    # Fail-safe: an unresolvable head returns the normalized literal, never raises.
    assert trigger._normalize_argv_head("groundtruth-kb/.venv/Scripts/python.exe", tmp_path) == os.path.normpath(
        "groundtruth-kb/.venv/Scripts/python.exe"
    )


def test_normalize_argv_head_empty_passthrough(tmp_path: Path) -> None:
    assert _trigger()._normalize_argv_head("", tmp_path) == ""


def test_harness_command_normalizes_executable_head(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    trigger = _trigger()
    monkeypatch.setattr(trigger.shutil, "which", lambda cmd: "/resolved/python" if "python" in cmd else None)
    target = trigger.DispatchTarget(
        needed_role_label="loyal-opposition",
        harness_id="D",
        command_handle="ollama",
        canonical_mode="lo",
        invocation_surfaces={
            "headless": {
                "argv": [
                    "groundtruth-kb/.venv/Scripts/python.exe",
                    "scripts/ollama_harness.py",
                    "{{PROMPT}}",
                ]
            }
        },
    )
    command = trigger._harness_command(target, "PROMPT-BODY", tmp_path)
    assert command is not None
    # command[0] (the executable head) is normalized; later args are untouched.
    assert command[0] == "/resolved/python"
    assert command[1] == "scripts/ollama_harness.py"
    assert command[2] == "PROMPT-BODY"


def test_single_harness_worker_env_includes_package_src(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    trigger = _trigger()
    dispatcher = _dispatcher()
    target = trigger.DispatchTarget(
        needed_role_label="loyal-opposition",
        harness_id="D",
        command_handle="ollama",
        canonical_mode="lo",
        invocation_surfaces={"headless": {"argv": ["worker-cmd", "{{PROMPT}}"]}},
    )
    item = type(
        "FakeItem",
        (),
        {
            "document_name": "gtkb-headless-worker-venv-interpreter-pin",
            "top_status": "NEW",
            "top_file": "bridge/gtkb-headless-worker-venv-interpreter-pin-001.md",
        },
    )()
    captured: dict[str, object] = {}

    class FakeProcess:
        pid = 12345

    def fake_popen(*args, **kwargs):
        captured["args"] = args
        captured["kwargs"] = kwargs
        return FakeProcess()

    monkeypatch.setenv("PYTHONPATH", "C:/existing/pkg")
    monkeypatch.setattr(dispatcher.subprocess, "Popen", fake_popen)

    meta = dispatcher._spawn_worker(
        target=target,
        items=[item],
        project_root=tmp_path,
        state_dir=tmp_path / "state",
        max_items=1,
        dry_run=False,
        trigger=trigger,
        dispatch_id="single-dispatch-env-test",
    )

    assert meta["launched"] is True
    env = captured["kwargs"]["env"]
    pythonpath = env["PYTHONPATH"].split(os.pathsep)
    assert pythonpath[0] == trigger._PACKAGE_SRC
    assert "C:/existing/pkg" in pythonpath


# ---------------------------------------------------------------------------
# Step 2 — launchability doctor check
# ---------------------------------------------------------------------------


def _write_registry(root: Path, harnesses: list[dict]) -> None:
    (root / "harness-state").mkdir(parents=True, exist_ok=True)
    (root / "harness-state" / "harness-registry.json").write_text(
        json.dumps({"schema_version": 1, "source_of_truth": "test", "harnesses": harnesses}),
        encoding="utf-8",
    )


def test_launchability_passes_for_resolvable_target(tmp_path: Path) -> None:
    from groundtruth_kb.project.doctor import _check_harness_launchability

    _write_registry(
        tmp_path,
        [
            {
                "id": "B",
                "harness_name": "claude",
                "harness_type": "claude",
                "status": "active",
                "role": ["prime-builder"],
                "can_fire_events": True,
                "can_receive_dispatch": True,
                "invocation_surfaces": {"headless": {"argv": [sys.executable, "-p", "{{PROMPT}}"]}},
            }
        ],
    )
    check = _check_harness_launchability(tmp_path)
    assert check.status == "pass"


def test_launchability_fails_on_winerror2_class_head(tmp_path: Path) -> None:
    from groundtruth_kb.project.doctor import _check_harness_launchability

    _write_registry(
        tmp_path,
        [
            {
                "id": "D",
                "harness_name": "ollama",
                "harness_type": "ollama",
                "status": "active",
                "role": ["loyal-opposition"],
                "can_fire_events": False,
                "can_receive_dispatch": True,
                "invocation_surfaces": {"headless": {"argv": ["totally-not-a-real-binary-zzz999", "{{PROMPT}}"]}},
            }
        ],
    )
    check = _check_harness_launchability(tmp_path)
    assert check.status == "fail"
    assert "unlaunchable" in check.message.lower()


def test_launchability_warns_when_no_headless_targets(tmp_path: Path) -> None:
    from groundtruth_kb.project.doctor import _check_harness_launchability

    _write_registry(
        tmp_path,
        [
            {
                "id": "C",
                "harness_name": "antigravity",
                "harness_type": "antigravity",
                "status": "active",
                "role": ["prime-builder"],
                "can_fire_events": False,
                "can_receive_dispatch": True,
                "invocation_surfaces": {"interactive": {"kind": "ide", "name": "Antigravity IDE"}},
            }
        ],
    )
    check = _check_harness_launchability(tmp_path)
    assert check.status == "warning"


# ---------------------------------------------------------------------------
# Step 3 — capability-axis split projection (HYG-004)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("harness_type", "expected_fire", "expected_receive"),
    [
        ("claude", True, True),
        ("codex", True, True),
        ("ollama", False, True),
        ("openrouter", False, True),
        ("antigravity", False, True),
    ],
)
def test_capability_axes_split(harness_type: str, expected_fire: bool, expected_receive: bool) -> None:
    from groundtruth_kb.harness_projection import _project_harness_record

    record = _project_harness_record({"id": "X", "harness_name": harness_type, "harness_type": harness_type})
    assert record["can_fire_events"] is expected_fire
    assert record["can_receive_dispatch"] is expected_receive
    # Deprecated alias preserves the event-firing-axis value for legacy topology readers.
    assert record["event_driven_hooks"] == record["can_fire_events"]


def test_capability_axes_honor_explicit_dispatch_metadata() -> None:
    from groundtruth_kb.harness_projection import _project_harness_record

    record = _project_harness_record(
        {
            "id": "B",
            "harness_name": "claude",
            "harness_type": "claude",
            "invocation_surfaces": {
                "headless": {"argv": ["claude", "-p", "{{PROMPT}}"]},
                "dispatch": {
                    "can_fire_events": True,
                    "can_receive_dispatch": False,
                    "event_driven_hooks": False,
                },
            },
        }
    )

    assert record["can_fire_events"] is True
    assert record["can_receive_dispatch"] is False
    assert record["event_driven_hooks"] is False


# ---------------------------------------------------------------------------
# Step 4 — gated scheduled wake
# ---------------------------------------------------------------------------


def test_no_active_event_source_true_when_all_eventless(tmp_path: Path) -> None:
    dispatcher = _dispatcher()
    root = _make_topology_project(tmp_path, EVENTLESS_TOPOLOGY)
    assert dispatcher._no_active_event_source_harness(root) is True


def test_no_active_event_source_false_when_event_source_active(tmp_path: Path) -> None:
    dispatcher = _dispatcher()
    root = _make_topology_project(tmp_path, WITH_EVENT_SOURCE_TOPOLOGY)
    assert dispatcher._no_active_event_source_harness(root) is False


def test_no_active_event_source_false_when_no_active_harness(tmp_path: Path) -> None:
    dispatcher = _dispatcher()
    suspended = [
        {
            "id": "D",
            "harness_name": "ollama",
            "harness_type": "ollama",
            "status": "suspended",
            "role": ["loyal-opposition"],
            "can_fire_events": False,
            "can_receive_dispatch": True,
        }
    ]
    root = _make_topology_project(tmp_path, suspended)
    assert dispatcher._no_active_event_source_harness(root) is False


def test_record_is_active_event_source_legacy_fallback() -> None:
    dispatcher = _dispatcher()
    # Legacy record (no can_fire_events) falls back to harness_type membership.
    assert dispatcher._record_is_active_event_source({"status": "active", "harness_type": "codex"}) is True
    assert dispatcher._record_is_active_event_source({"status": "active", "harness_type": "ollama"}) is False
    # Explicit can_fire_events overrides the type fallback.
    assert (
        dispatcher._record_is_active_event_source(
            {"status": "active", "harness_type": "codex", "can_fire_events": False}
        )
        is False
    )


def test_gated_wake_applicable_no_event_source(tmp_path: Path) -> None:
    dispatcher = _dispatcher()
    root = _make_topology_project(tmp_path, EVENTLESS_TOPOLOGY)
    applicable, reason = dispatcher._gated_wake_applicable(root)
    assert applicable is True
    assert reason == "no_active_event_source_harness"


def test_gated_wake_not_applicable_with_event_source(tmp_path: Path) -> None:
    dispatcher = _dispatcher()
    root = _make_topology_project(tmp_path, WITH_EVENT_SOURCE_TOPOLOGY)
    applicable, reason = dispatcher._gated_wake_applicable(root)
    assert applicable is False
    assert reason is None


def test_gated_wake_applicable_single_harness(tmp_path: Path) -> None:
    dispatcher = _dispatcher()
    root = _make_topology_project(tmp_path, SINGLE_HARNESS_TOPOLOGY)
    applicable, reason = dispatcher._gated_wake_applicable(root)
    assert applicable is True
    assert reason == "single_harness_topology"


def test_run_dispatcher_wake_gate_blocks_when_event_source_active(tmp_path: Path) -> None:
    dispatcher = _dispatcher()
    root = _make_topology_project(tmp_path, WITH_EVENT_SOURCE_TOPOLOGY)
    result = dispatcher.run_dispatcher(
        project_root=root,
        state_dir=tmp_path / "state",
        dry_run=True,
        enforce_wake_gate=True,
    )
    assert result["skipped"] is True
    assert result["reason"] == "wake_gate_not_applicable"


def test_run_dispatcher_wake_gate_allows_no_event_source(tmp_path: Path) -> None:
    dispatcher = _dispatcher()
    root = _make_topology_project(tmp_path, EVENTLESS_TOPOLOGY)
    result = dispatcher.run_dispatcher(
        project_root=root,
        state_dir=tmp_path / "state",
        dry_run=True,
        enforce_wake_gate=True,
    )
    # The wake gate is open (no active event source) so the cycle proceeds.
    assert result.get("skipped") is False


def test_run_dispatcher_default_does_not_enforce_wake_gate(tmp_path: Path) -> None:
    dispatcher = _dispatcher()
    root = _make_topology_project(tmp_path, WITH_EVENT_SOURCE_TOPOLOGY)
    result = dispatcher.run_dispatcher(
        project_root=root,
        state_dir=tmp_path / "state",
        dry_run=True,
    )
    # Default enforce_wake_gate=False preserves prior behavior: no wake short-circuit.
    assert result.get("reason") != "wake_gate_not_applicable"


# ---------------------------------------------------------------------------
# Step 4 — automation activation broadening
# ---------------------------------------------------------------------------


def _patch_win_task_calls(monkeypatch: pytest.MonkeyPatch, module: ModuleType, calls: list[tuple[str, dict]]) -> None:
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


def test_automation_installs_for_no_event_source_topology(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = _automation()
    root = _make_topology_project(tmp_path, EVENTLESS_TOPOLOGY)
    calls: list[tuple[str, dict]] = []
    _patch_win_task_calls(monkeypatch, module, calls)

    payload = module.ensure_single_harness_automation(project_root=root, state_dir=tmp_path / "state", dry_run=True)

    assert payload["single_harness_applicable"] is False
    assert payload["gated_wake_applicable"] is True
    assert payload["wake_reason"] == "no_active_event_source_harness"
    assert payload["activated"] is True
    assert payload["action"] == "registered_or_updated"
    assert calls[0][0] == "install"


def test_automation_deactivates_when_event_source_active(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = _automation()
    root = _make_topology_project(tmp_path, WITH_EVENT_SOURCE_TOPOLOGY)
    calls: list[tuple[str, dict]] = []
    _patch_win_task_calls(monkeypatch, module, calls)

    payload = module.ensure_single_harness_automation(project_root=root, state_dir=tmp_path / "state", dry_run=True)

    assert payload["gated_wake_applicable"] is False
    assert payload["activated"] is False
    assert payload["action"] == "deactivated_no_wake_needed"
    assert calls and calls[0][0] == "uninstall"


def test_automation_dispatch_now_enforces_wake_gate(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = _automation()
    root = _make_topology_project(tmp_path, EVENTLESS_TOPOLOGY)
    calls: list[tuple[str, dict]] = []
    _patch_win_task_calls(monkeypatch, module, calls)

    captured: dict[str, object] = {}
    dispatcher = module._load_dispatcher_module()

    def _fake_run(**kwargs):
        captured.update(kwargs)
        return {"skipped": False, "enforced": kwargs.get("enforce_wake_gate")}

    monkeypatch.setattr(dispatcher, "run_dispatcher", _fake_run)

    payload = module.ensure_single_harness_automation(
        project_root=root,
        state_dir=tmp_path / "state",
        dispatch_now=True,
        dry_run=True,
    )

    # The dispatch_now path self-gates via enforce_wake_gate=True (defense in depth).
    assert captured.get("enforce_wake_gate") is True
    assert payload["dispatch_now"] == {"skipped": False, "enforced": True}
