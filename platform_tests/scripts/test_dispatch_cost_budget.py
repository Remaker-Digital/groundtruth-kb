from __future__ import annotations

import datetime as dt
import importlib.util
import json
import os
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
TRIGGER_PATH = REPO_ROOT / "scripts" / "cross_harness_bridge_trigger.py"


def _load_trigger() -> ModuleType:
    name = "cross_harness_bridge_trigger_budget_test"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, TRIGGER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _write_config(root: Path, budget: str = "") -> None:
    (root / "config" / "dispatcher").mkdir(parents=True)
    (root / "config" / "dispatcher" / "rules.toml").write_text(
        (
            """
schema_version = 1

[[rules]]
id = "lo-default"
required_roles = ["loyal-opposition"]
statuses = ["NEW", "REVISED"]
prefer = ["harness_id"]
"""
            + budget
        ).lstrip(),
        encoding="utf-8",
    )


def _target(trigger: ModuleType, harness_id: str = "D"):
    return trigger.DispatchTarget(
        needed_role_label="loyal-opposition",
        harness_id=harness_id,
        command_handle="test",
        canonical_mode="lo",
        invocation_surfaces={"headless": {"argv": [sys.executable, "-c", "pass"]}},
    )


def _item() -> SimpleNamespace:
    return SimpleNamespace(
        document_name="sample-budget-thread",
        top_status="NEW",
        top_file="bridge/sample-budget-thread-001.md",
    )


def _spawn(trigger: ModuleType, root: Path, state_dir: Path, *, harness_id: str = "D") -> dict:
    return trigger._spawn_harness(
        target=_target(trigger, harness_id),
        items=[_item()],
        project_root=root,
        state_dir=state_dir,
        max_items=1,
        dry_run=False,
        dispatch_id=f"2026-06-28T00-00-00Z-loyal-opposition-{harness_id}-budget",
    )


def _failure_rows(state_dir: Path) -> list[dict]:
    path = state_dir / "dispatch-failures.jsonl"
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


@pytest.fixture()
def trigger(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    module = _load_trigger()
    monkeypatch.setattr(module, "_pid_create_time_epoch", lambda _pid: None)
    return module


def test_default_budget_config_preserves_spawn(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, trigger: ModuleType
) -> None:
    _write_config(tmp_path)
    calls: list[dict] = []

    class _FakeProcess:
        pid = os.getpid()

    def _fake_popen(*_args, **kwargs):
        calls.append(kwargs)
        return _FakeProcess()

    monkeypatch.setattr(trigger.subprocess, "Popen", _fake_popen)

    meta = _spawn(trigger, tmp_path, tmp_path / "state")

    assert meta["launched"] is True
    assert len(calls) == 1
    assert _failure_rows(tmp_path / "state") == []


def test_session_hard_cap_suppresses_before_popen(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, trigger: ModuleType
) -> None:
    _write_config(
        tmp_path,
        """

[budget]
enabled = true
per_session_usd = 0.05
unknown_model_policy = "fail_closed"
unpriced_model_policy = "fail_open"

[budget.harnesses.D]
model = "priced-model"
pricing = "priced"
estimated_usd_per_dispatch = 0.10
""",
    )
    monkeypatch.setattr(trigger.subprocess, "Popen", lambda *_a, **_k: pytest.fail("Popen must not run"))

    meta = _spawn(trigger, tmp_path, tmp_path / "state")

    assert meta["launched"] is False
    assert meta["reason"] == "dispatch_budget_session_cap_reached"
    rows = _failure_rows(tmp_path / "state")
    assert rows[-1]["reason"] == "dispatch_budget_session_cap_reached"
    assert rows[-1]["projected_usd"] == 0.10


def test_unknown_priced_model_fails_closed_before_popen(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, trigger: ModuleType
) -> None:
    _write_config(
        tmp_path,
        """

[budget]
enabled = true
unknown_model_policy = "fail_closed"

[budget.harnesses.D]
model = "priced-without-estimate"
pricing = "priced"
""",
    )
    monkeypatch.setattr(trigger.subprocess, "Popen", lambda *_a, **_k: pytest.fail("Popen must not run"))

    meta = _spawn(trigger, tmp_path, tmp_path / "state")

    assert meta["launched"] is False
    assert meta["reason"] == "dispatch_budget_unknown_priced_model"
    assert _failure_rows(tmp_path / "state")[-1]["model"] == "priced-without-estimate"


def test_unpriced_model_fails_open_even_with_zero_caps(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, trigger: ModuleType
) -> None:
    _write_config(
        tmp_path,
        """

[budget]
enabled = true
per_session_usd = 0.0
per_user_daily_usd = 0.0
unknown_model_policy = "fail_closed"
unpriced_model_policy = "fail_open"

[budget.harnesses.D]
model = "local-unpriced"
pricing = "unpriced"
""",
    )
    calls: list[dict] = []

    class _FakeProcess:
        pid = os.getpid()

    def _fake_popen(*_args, **kwargs):
        calls.append(kwargs)
        return _FakeProcess()

    monkeypatch.setattr(trigger.subprocess, "Popen", _fake_popen)

    meta = _spawn(trigger, tmp_path, tmp_path / "state")

    assert meta["launched"] is True
    assert len(calls) == 1


def test_daily_cap_uses_budget_ledger_before_popen(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, trigger: ModuleType
) -> None:
    _write_config(
        tmp_path,
        """

[budget]
enabled = true
per_user_daily_usd = 0.10
unknown_model_policy = "fail_closed"
unpriced_model_policy = "fail_open"

[budget.harnesses.D]
model = "priced-model"
pricing = "priced"
estimated_usd_per_dispatch = 0.02
""",
    )
    monkeypatch.setenv("GTKB_DISPATCH_BUDGET_USER", "budget-user")
    state_dir = tmp_path / "state"
    state_dir.mkdir()
    today = dt.datetime.now(dt.UTC).date().isoformat()
    (state_dir / "dispatch-budget-ledger.jsonl").write_text(
        json.dumps({"user": "budget-user", "day": today, "estimated_usd": 0.09}) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(trigger.subprocess, "Popen", lambda *_a, **_k: pytest.fail("Popen must not run"))

    meta = _spawn(trigger, tmp_path, state_dir)

    assert meta["launched"] is False
    assert meta["reason"] == "dispatch_budget_daily_cap_reached"
    assert meta["daily_used_usd"] == 0.09
    assert meta["projected_usd"] == 0.11
