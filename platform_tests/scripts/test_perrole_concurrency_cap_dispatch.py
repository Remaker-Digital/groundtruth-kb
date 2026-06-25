# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for the CA9165 (SPEC-INTAKE-ca9165) per-role dispatch concurrency cap.

Covers the spec-derived behaviors from
``bridge/gtkb-perrole-concurrency-cap-dispatch-001.md`` (GO at -002):

- ``_max_live_dispatched_per_role`` env parsing + fail-safe default.
- ``_count_live_dispatched_processes_for_role`` role-scoped count semantics.
- The ``_spawn_harness`` per-role gate: at/over the per-role cap it skips the
  dispatch (no ``Popen``) with ``reason="per_role_concurrency_cap_reached"``;
  below the cap a same-role spawn still proceeds (no binary suppression).
- Global-cap precedence: a global-cap hit returns ``concurrency_cap_reached``
  before the per-role gate is reached.
"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest

_SCRIPT_PATH = Path(__file__).resolve().parents[2] / "scripts" / "cross_harness_bridge_trigger.py"
_CODEX_INVOCATION_SURFACES = {"headless": {"argv": ["codex", "exec", "{{PROMPT}}", "--cd", "{{PROJECT_ROOT}}"]}}


def _load_trigger() -> ModuleType:
    module_name = "cross_harness_bridge_trigger"
    if module_name in sys.modules:
        return sys.modules[module_name]
    spec = importlib.util.spec_from_file_location(module_name, _SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _lo_target(trigger: ModuleType) -> object:
    return trigger.DispatchTarget(
        needed_role_label="loyal-opposition",
        harness_id="A",
        command_handle="codex",
        canonical_mode="lo",
        invocation_surfaces=_CODEX_INVOCATION_SURFACES,
    )


def _fake_item() -> SimpleNamespace:
    return SimpleNamespace(
        document_name="cap-test",
        top_status="NEW",
        top_file="bridge/cap-test-001.md",
        index_line_number=1,
        dispatchable=True,
        classification="dispatchable",
    )


@pytest.fixture
def trigger_module() -> ModuleType:
    return _load_trigger()


@pytest.fixture(autouse=True)
def _isolate_host_dispatch_cap_env(trigger_module: ModuleType, monkeypatch: pytest.MonkeyPatch) -> None:
    """Host env can override GTKB cap defaults; spawn-gate tests assume defaults."""
    monkeypatch.delenv(trigger_module.MAX_LIVE_DISPATCHED_PROCESSES_ENV_VAR, raising=False)
    monkeypatch.delenv(trigger_module.MAX_LIVE_DISPATCHED_PER_ROLE_ENV_VAR, raising=False)


# --------------------------------------------------------------------------- #
# _max_live_dispatched_per_role — env parsing + fail-safe default
# --------------------------------------------------------------------------- #


def test_per_role_cap_default_when_unset(monkeypatch: pytest.MonkeyPatch) -> None:
    trigger = _load_trigger()
    monkeypatch.delenv(trigger.MAX_LIVE_DISPATCHED_PER_ROLE_ENV_VAR, raising=False)
    assert trigger._max_live_dispatched_per_role() == trigger.DEFAULT_MAX_LIVE_DISPATCHED_PER_ROLE


def test_per_role_cap_env_override(monkeypatch: pytest.MonkeyPatch) -> None:
    trigger = _load_trigger()
    monkeypatch.setenv(trigger.MAX_LIVE_DISPATCHED_PER_ROLE_ENV_VAR, "5")
    assert trigger._max_live_dispatched_per_role() == 5


@pytest.mark.parametrize("value", ["0", "-2", "notanint", "  "])
def test_per_role_cap_invalid_or_nonpositive_falls_back(value: str, monkeypatch: pytest.MonkeyPatch) -> None:
    trigger = _load_trigger()
    monkeypatch.setenv(trigger.MAX_LIVE_DISPATCHED_PER_ROLE_ENV_VAR, value)
    assert trigger._max_live_dispatched_per_role() == trigger.DEFAULT_MAX_LIVE_DISPATCHED_PER_ROLE


# --------------------------------------------------------------------------- #
# _count_live_dispatched_processes_for_role — role-scoped count
# --------------------------------------------------------------------------- #


def test_per_role_count_is_role_scoped(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    trigger = _load_trigger()
    runs_dir = tmp_path / "dispatch-runs"
    runs_dir.mkdir()
    me = os.getpid()
    # dispatch_id format from _new_dispatch_id: {ts}-{role_label}-{harness_id}-{uuid6}
    (runs_dir / "2026-06-21T05-00-00Z-loyal-opposition-A-aaaaaa.pid").write_text(str(me), encoding="utf-8")
    (runs_dir / "2026-06-21T05-00-00Z-loyal-opposition-A-bbbbbb.pid").write_text(str(me), encoding="utf-8")
    (runs_dir / "2026-06-21T05-00-00Z-prime-builder-B-cccccc.pid").write_text(str(me), encoding="utf-8")
    monkeypatch.setattr(trigger, "_pid_alive", lambda pid: str(pid) == str(me))

    assert trigger._count_live_dispatched_processes_for_role(runs_dir, "loyal-opposition") == 2
    assert trigger._count_live_dispatched_processes_for_role(runs_dir, "prime-builder") == 1
    # The global counter still sees all three.
    assert trigger._count_live_dispatched_processes(runs_dir) == 3


def test_per_role_count_zero_for_missing_runs_dir(tmp_path: Path) -> None:
    trigger = _load_trigger()
    assert trigger._count_live_dispatched_processes_for_role(tmp_path / "nope", "loyal-opposition") == 0


# --------------------------------------------------------------------------- #
# _spawn_harness per-role gate
# --------------------------------------------------------------------------- #


def test_per_role_cap_suppresses_at_limit(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    trigger = _load_trigger()
    state_dir = tmp_path / "state"

    def _sentinel_popen(*args, **kwargs):  # noqa: ANN002, ANN003
        raise AssertionError("Popen must not be called when the per-role cap is reached")

    monkeypatch.setattr(subprocess, "Popen", _sentinel_popen)
    monkeypatch.setattr(trigger, "_dispatch_prompt", lambda *a, **k: "prompt")
    monkeypatch.setattr(trigger, "_harness_command", lambda *a, **k: ["codex", "exec", "prompt"])
    # Global pool has headroom; the per-role count is at the cap.
    monkeypatch.setattr(trigger, "_count_live_dispatched_processes", lambda runs_dir: 0)
    monkeypatch.setattr(
        trigger,
        "_count_live_dispatched_processes_for_role",
        lambda runs_dir, role: trigger.DEFAULT_MAX_LIVE_DISPATCHED_PER_ROLE,
    )

    meta = trigger._spawn_harness(
        target=_lo_target(trigger),
        items=[_fake_item()],
        project_root=tmp_path,
        state_dir=state_dir,
        max_items=2,
        dry_run=False,
    )

    assert meta["launched"] is False
    assert meta["reason"] == "per_role_concurrency_cap_reached"
    assert meta["role"] == "loyal-opposition"
    assert meta["per_role_live"] == trigger.DEFAULT_MAX_LIVE_DISPATCHED_PER_ROLE
    assert meta["per_role_cap"] == trigger.DEFAULT_MAX_LIVE_DISPATCHED_PER_ROLE

    failures = state_dir / trigger.DISPATCH_FAILURES_FILENAME
    assert failures.is_file()
    records = [json.loads(line) for line in failures.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert any(r.get("reason") == "per_role_concurrency_cap_reached" for r in records)


def test_per_role_below_cap_allows_same_role_spawn(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    trigger = _load_trigger()
    state_dir = tmp_path / "state"

    class _FakeProcess:
        pid = 4242

    monkeypatch.setattr(subprocess, "Popen", lambda *a, **k: _FakeProcess())
    monkeypatch.setattr(trigger, "_dispatch_prompt", lambda *a, **k: "prompt")
    monkeypatch.setattr(trigger, "_harness_command", lambda *a, **k: ["codex", "exec", "prompt"])
    monkeypatch.setattr(trigger, "_count_live_dispatched_processes", lambda runs_dir: 0)
    # One same-role worker already live, but below the per-role cap (default 3):
    monkeypatch.setattr(trigger, "_count_live_dispatched_processes_for_role", lambda runs_dir, role: 1)

    meta = trigger._spawn_harness(
        target=_lo_target(trigger),
        items=[_fake_item()],
        project_root=tmp_path,
        state_dir=state_dir,
        max_items=2,
        dry_run=False,
    )

    assert meta["launched"] is True
    assert meta.get("reason") != "per_role_concurrency_cap_reached"


def test_global_cap_keeps_precedence_over_per_role(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    trigger = _load_trigger()
    state_dir = tmp_path / "state"

    def _sentinel_popen(*args, **kwargs):  # noqa: ANN002, ANN003
        raise AssertionError("Popen must not be called when the global cap is reached")

    monkeypatch.setattr(subprocess, "Popen", _sentinel_popen)
    monkeypatch.setattr(trigger, "_dispatch_prompt", lambda *a, **k: "prompt")
    monkeypatch.setattr(trigger, "_harness_command", lambda *a, **k: ["codex", "exec", "prompt"])
    # Global pool is at the cap; even though per-role would also be over, the
    # global gate must fire first and own the reason.
    monkeypatch.setattr(trigger, "_count_live_dispatched_processes", lambda runs_dir: 8)
    monkeypatch.setattr(trigger, "_count_live_dispatched_processes_for_role", lambda runs_dir, role: 99)

    meta = trigger._spawn_harness(
        target=_lo_target(trigger),
        items=[_fake_item()],
        project_root=tmp_path,
        state_dir=state_dir,
        max_items=2,
        dry_run=False,
    )

    assert meta["launched"] is False
    assert meta["reason"] == "concurrency_cap_reached"
