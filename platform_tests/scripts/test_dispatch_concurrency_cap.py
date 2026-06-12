# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for the WI-4472 hard global dispatch concurrency cap.

Covers the spec-derived behaviors from
``bridge/gtkb-cross-harness-dispatch-concurrency-cap-003.md`` (GO at -004):

- ``_max_live_dispatched_processes`` env parsing + default-fallback.
- ``_pid_alive`` liveness + fail-closed parse guard.
- ``_count_live_dispatched_processes`` count semantics + stale-sidecar prune.
- The ``_spawn_harness`` cap gate: at/over the cap it skips the dispatch
  (no ``Popen``), returns ``reason="concurrency_cap_reached"``, and records a
  durable ``dispatch-failures.jsonl`` audit entry; below the cap it launches
  and writes the ``.pid`` accounting sidecar.
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
    """Load scripts/cross_harness_bridge_trigger.py with sys.modules registration."""
    assert _SCRIPT_PATH.is_file(), f"Expected trigger at {_SCRIPT_PATH}"
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


# --------------------------------------------------------------------------- #
# _max_live_dispatched_processes — env parsing + fail-safe default
# --------------------------------------------------------------------------- #


def test_cap_default_when_unset(monkeypatch: pytest.MonkeyPatch) -> None:
    trigger = _load_trigger()
    monkeypatch.delenv(trigger.MAX_LIVE_DISPATCHED_PROCESSES_ENV_VAR, raising=False)
    assert trigger._max_live_dispatched_processes() == trigger.DEFAULT_MAX_LIVE_DISPATCHED_PROCESSES


def test_cap_env_override(monkeypatch: pytest.MonkeyPatch) -> None:
    trigger = _load_trigger()
    monkeypatch.setenv(trigger.MAX_LIVE_DISPATCHED_PROCESSES_ENV_VAR, "3")
    assert trigger._max_live_dispatched_processes() == 3


@pytest.mark.parametrize("value", ["0", "-5", "notanint", "  "])
def test_cap_invalid_or_nonpositive_falls_back_to_default(value: str, monkeypatch: pytest.MonkeyPatch) -> None:
    trigger = _load_trigger()
    monkeypatch.setenv(trigger.MAX_LIVE_DISPATCHED_PROCESSES_ENV_VAR, value)
    assert trigger._max_live_dispatched_processes() == trigger.DEFAULT_MAX_LIVE_DISPATCHED_PROCESSES


# --------------------------------------------------------------------------- #
# _pid_alive — liveness + fail-closed parse guard
# --------------------------------------------------------------------------- #


def test_pid_alive_for_current_process() -> None:
    trigger = _load_trigger()
    assert trigger._pid_alive(os.getpid()) is True


@pytest.mark.parametrize("bad", [-1, 0, "notanint", None])
def test_pid_alive_fail_closed_for_invalid(bad: object) -> None:
    trigger = _load_trigger()
    assert trigger._pid_alive(bad) is False


# --------------------------------------------------------------------------- #
# _count_live_dispatched_processes — count semantics + prune
# --------------------------------------------------------------------------- #


def test_count_excludes_exited_and_dead_and_prunes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    trigger = _load_trigger()
    runs_dir = tmp_path / "dispatch-runs"
    runs_dir.mkdir()
    me = os.getpid()

    # id1: pending sidecar, alive pid -> LIVE.
    (runs_dir / "id1.pid").write_text(str(me), encoding="utf-8")
    # id2: alive pid but exit_code written (exited) -> not live, pruned.
    (runs_dir / "id2.pid").write_text(str(me), encoding="utf-8")
    (runs_dir / "id2.exit_code").write_text("0", encoding="utf-8")
    # id3: dead pid -> not live, pruned.
    (runs_dir / "id3.pid").write_text("424242", encoding="utf-8")
    # id4: malformed sidecar -> not live, pruned.
    (runs_dir / "id4.pid").write_text("not-a-pid", encoding="utf-8")

    # Deterministic liveness: only the current pid is alive.
    monkeypatch.setattr(trigger, "_pid_alive", lambda pid: str(pid) == str(me))

    assert trigger._count_live_dispatched_processes(runs_dir) == 1
    assert (runs_dir / "id1.pid").exists()
    assert not (runs_dir / "id2.pid").exists()
    assert not (runs_dir / "id3.pid").exists()
    assert not (runs_dir / "id4.pid").exists()


def test_count_zero_for_missing_runs_dir(tmp_path: Path) -> None:
    trigger = _load_trigger()
    assert trigger._count_live_dispatched_processes(tmp_path / "does-not-exist") == 0


# --------------------------------------------------------------------------- #
# _spawn_harness cap gate
# --------------------------------------------------------------------------- #


def test_cap_gate_blocks_dispatch_at_or_over_limit(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    trigger = _load_trigger()
    state_dir = tmp_path / "state"

    popen_calls: list[object] = []

    def _sentinel_popen(*args, **kwargs):  # noqa: ANN002, ANN003
        popen_calls.append((args, kwargs))
        raise AssertionError("Popen must not be called when the concurrency cap is reached")

    monkeypatch.setattr(subprocess, "Popen", _sentinel_popen)
    monkeypatch.setattr(trigger, "_dispatch_prompt", lambda *a, **k: "prompt")
    monkeypatch.setattr(trigger, "_harness_command", lambda *a, **k: ["codex", "exec", "prompt"])
    # Force the live count to the default cap (8) so live >= cap.
    monkeypatch.setattr(trigger, "_count_live_dispatched_processes", lambda runs_dir: 8)

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
    assert meta["live_count"] == 8
    assert meta["cap"] == trigger.DEFAULT_MAX_LIVE_DISPATCHED_PROCESSES
    assert popen_calls == []

    failures = state_dir / trigger.DISPATCH_FAILURES_FILENAME
    assert failures.is_file()
    records = [json.loads(line) for line in failures.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert any(r.get("reason") == "concurrency_cap_reached" for r in records)


def test_below_cap_launches_and_writes_pid_sidecar(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    trigger = _load_trigger()
    state_dir = tmp_path / "state"

    class _FakeProcess:
        pid = 4242

    monkeypatch.setattr(subprocess, "Popen", lambda *a, **k: _FakeProcess())
    monkeypatch.setattr(trigger, "_dispatch_prompt", lambda *a, **k: "prompt")
    monkeypatch.setattr(trigger, "_harness_command", lambda *a, **k: ["codex", "exec", "prompt"])
    monkeypatch.setattr(trigger, "_count_live_dispatched_processes", lambda runs_dir: 0)

    meta = trigger._spawn_harness(
        target=_lo_target(trigger),
        items=[_fake_item()],
        project_root=tmp_path,
        state_dir=state_dir,
        max_items=2,
        dry_run=False,
    )

    assert meta["launched"] is True
    assert meta.get("reason") != "concurrency_cap_reached"
    sidecar = state_dir / trigger.DISPATCH_RUNS_SUBDIR / f"{meta['dispatch_id']}.pid"
    assert sidecar.is_file()
    assert sidecar.read_text(encoding="utf-8").strip() == "4242"
