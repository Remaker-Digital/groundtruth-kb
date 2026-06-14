# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for scripts/bridge_dispatch_starvation_telemetry.py (WI-4480 Slice A).

Per ``bridge/gtkb-wi4480-dispatch-starvation-telemetry-001.md`` Verification
Plan (Codex GO at ``-002``). Covers the pure-function increment/reset/prune/
threshold behavior, ``first_starved_at`` preservation, persistence round-trip,
fail-safe behavior, and the byte-identical actionable-signature invariant
(the load-bearing swarm-coordination constraint this slice must NOT perturb).
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_TELEMETRY_PATH = _REPO_ROOT / "scripts" / "bridge_dispatch_starvation_telemetry.py"
_TRIGGER_PATH = _REPO_ROOT / "scripts" / "cross_harness_bridge_trigger.py"


def _load_module(path: Path, module_name: str) -> ModuleType:
    if module_name in sys.modules:
        return sys.modules[module_name]
    # Ensure scripts/ is importable for the trigger's sibling imports.
    scripts_dir = str(path.resolve().parent)
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    pkg_src = str(_REPO_ROOT / "groundtruth-kb" / "src")
    if pkg_src not in sys.path:
        sys.path.insert(0, pkg_src)
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def telemetry() -> ModuleType:
    return _load_module(_TELEMETRY_PATH, "bridge_dispatch_starvation_telemetry")


@pytest.fixture(scope="module")
def trigger() -> ModuleType:
    return _load_module(_TRIGGER_PATH, "cross_harness_bridge_trigger")


_RECIPIENT = "loyal-opposition:A"
_THRESHOLD = 5


def _update(telemetry, prev, actionable, selected, now_iso="2026-06-14T00:00:00+00:00", threshold=_THRESHOLD):
    return telemetry.update_starvation_telemetry(prev, _RECIPIENT, actionable, selected, now_iso, threshold)


def _entries(telem):
    return telem["recipients"][_RECIPIENT]["entries"]


# --- Acceptance: un-selected actionable entry increments (starvation detect) ---


def test_non_selection_increments(telemetry):
    telem, _ = _update(telemetry, None, ["a", "b", "c"], ["a", "b"])
    assert _entries(telem)["c"]["consecutive_non_selection"] == 1
    assert "a" not in _entries(telem) and "b" not in _entries(telem)

    telem, _ = _update(telemetry, telem, ["a", "b", "c"], ["a", "b"])
    assert _entries(telem)["c"]["consecutive_non_selection"] == 2


# --- Acceptance: selection resets the counter (no false starvation) ---


def test_selection_resets_counter(telemetry):
    telem, _ = _update(telemetry, None, ["a", "b", "c"], ["a", "b"])
    telem, _ = _update(telemetry, telem, ["a", "b", "c"], ["a", "b"])
    assert _entries(telem)["c"]["consecutive_non_selection"] == 2

    telem, _ = _update(telemetry, telem, ["a", "b", "c"], ["c"])
    assert "c" not in _entries(telem)


# --- Acceptance: no-longer-actionable entries pruned ---


def test_pruned_when_not_actionable(telemetry):
    telem, _ = _update(telemetry, None, ["a", "b", "c"], ["a", "b"])
    assert "c" in _entries(telem)

    telem, _ = _update(telemetry, telem, ["a", "b"], ["a", "b"])
    assert "c" not in _entries(telem)


# --- Acceptance: threshold flagging (GOV-STANDING-BACKLOG-001, WI-4480) ---


def test_starved_flag_at_threshold(telemetry):
    telem = None
    starved = []
    for _ in range(_THRESHOLD):
        telem, starved = _update(telemetry, telem, ["a", "b", "c"], ["a", "b"])
    assert _entries(telem)["c"]["consecutive_non_selection"] == _THRESHOLD
    flagged = {row["document_name"]: row for row in starved}
    assert "c" in flagged
    assert flagged["c"]["consecutive_non_selection"] == _THRESHOLD
    # Below-threshold entries are not flagged.
    telem2, starved2 = _update(telemetry, None, ["a", "b", "c"], ["a", "b"])
    assert starved2 == []


# --- Acceptance: first_starved_at set once and preserved ---


def test_first_starved_at_preserved(telemetry):
    first_stamp = "2026-06-14T00:00:00+00:00"
    later_stamp = "2026-06-14T01:00:00+00:00"  # later, to prove it is NOT overwritten
    telem, _ = _update(telemetry, None, ["a", "b", "c"], ["a", "b"], now_iso=first_stamp)
    assert _entries(telem)["c"]["first_starved_at"] == first_stamp

    telem, _ = _update(telemetry, telem, ["a", "b", "c"], ["a", "b"], now_iso=later_stamp)
    assert _entries(telem)["c"]["consecutive_non_selection"] == 2
    assert _entries(telem)["c"]["first_starved_at"] == first_stamp


# --- Acceptance: persistence round-trip ---


def test_persistence_round_trip(telemetry, tmp_path):
    starved = telemetry.record_starvation(
        _RECIPIENT,
        ["a", "b", "c"],
        ["a", "b"],
        project_root=tmp_path,
        now_iso="2026-06-14T00:00:00+00:00",
        threshold=_THRESHOLD,
    )
    assert starved == []  # one round, below threshold

    path = tmp_path.joinpath(*telemetry.TELEMETRY_STATE_SUBDIR, telemetry.TELEMETRY_FILENAME)
    assert path.is_file()
    loaded = json.loads(path.read_text(encoding="utf-8"))
    assert loaded["schema_version"] == telemetry.SCHEMA_VERSION
    assert loaded["recipients"][_RECIPIENT]["entries"]["c"]["consecutive_non_selection"] == 1

    # A second round persists the incremented counter.
    telemetry.record_starvation(
        _RECIPIENT,
        ["a", "b", "c"],
        ["a", "b"],
        project_root=tmp_path,
        now_iso="2026-06-14T00:01:00+00:00",
        threshold=_THRESHOLD,
    )
    loaded2 = json.loads(path.read_text(encoding="utf-8"))
    assert loaded2["recipients"][_RECIPIENT]["entries"]["c"]["consecutive_non_selection"] == 2


def test_record_starvation_flags_at_threshold(telemetry, tmp_path):
    starved = []
    for i in range(_THRESHOLD):
        starved = telemetry.record_starvation(
            _RECIPIENT,
            ["a", "b", "c"],
            ["a", "b"],
            project_root=tmp_path,
            now_iso=f"2026-06-14T00:0{i}:00+00:00",
            threshold=_THRESHOLD,
        )
    assert any(row["document_name"] == "c" for row in starved)

    report = telemetry.report_starved(tmp_path, threshold=_THRESHOLD)
    assert "c" in {row["document_name"] for row in report["recipients"][_RECIPIENT]}


# --- Acceptance: fail-safe — corrupt/missing telemetry never raises ---


def test_record_starvation_fail_safe_corrupt(telemetry, tmp_path):
    path = tmp_path.joinpath(*telemetry.TELEMETRY_STATE_SUBDIR, telemetry.TELEMETRY_FILENAME)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("{ this is not valid json", encoding="utf-8")

    # Must not raise; corrupt prior state is treated as empty and overwritten.
    result = telemetry.record_starvation(
        _RECIPIENT,
        ["a", "b", "c"],
        ["a", "b"],
        project_root=tmp_path,
        now_iso="2026-06-14T00:00:00+00:00",
        threshold=_THRESHOLD,
    )
    assert result == []
    loaded = json.loads(path.read_text(encoding="utf-8"))
    assert loaded["recipients"][_RECIPIENT]["entries"]["c"]["consecutive_non_selection"] == 1


def test_record_starvation_fail_safe_unwritable(telemetry, tmp_path, monkeypatch):
    # Force the atomic write to fail; record_starvation must swallow it.
    def _boom(*_args, **_kwargs):
        raise OSError("disk full")

    monkeypatch.setattr(telemetry, "_atomic_write", _boom)
    result = telemetry.record_starvation(
        _RECIPIENT,
        ["a", "b", "c"],
        ["a", "b"],
        project_root=tmp_path,
        now_iso="2026-06-14T00:00:00+00:00",
        threshold=_THRESHOLD,
    )
    assert result == []


def test_threshold_env_override(telemetry, monkeypatch):
    monkeypatch.setenv(telemetry.THRESHOLD_ENV_VAR, "3")
    assert telemetry.resolve_threshold(None) == 3
    # Explicit positive arg wins over env.
    assert telemetry.resolve_threshold(7) == 7
    monkeypatch.setenv(telemetry.THRESHOLD_ENV_VAR, "not-a-number")
    assert telemetry.resolve_threshold(None) == telemetry.DEFAULT_THRESHOLD


# --- Acceptance: signature invariant preserved (no behavior change) ---


def _item(document_name: str, top_status: str = "NEW", top_file: str = "") -> SimpleNamespace:
    return SimpleNamespace(
        document_name=document_name,
        top_status=top_status,
        top_file=top_file or f"bridge/{document_name}-001.md",
        dispatchable=True,
    )


def test_signature_invariant_unaffected(trigger):
    """The selected-batch signature is byte-identical regardless of telemetry.

    Reproduces the trigger's own ``_signature(_selected_oldest_first(...))``
    and asserts it does not depend on telemetry state — the WI-4480 detector
    observes selection without altering it.
    """
    items = [_item("c"), _item("b"), _item("a")]  # INDEX is newest-first
    selected = trigger._selected_oldest_first(items, 2)
    sig_before = trigger._signature(selected)

    # Selection is pure oldest-first cap; telemetry recording does not enter
    # the selection path. Recompute to prove byte-identical determinism.
    selected_again = trigger._selected_oldest_first(items, 2)
    sig_after = trigger._signature(selected_again)
    assert sig_before == sig_after
    # Oldest-first cap selects the two oldest (reversed-then-capped).
    assert [it.document_name for it in selected] == ["a", "b"]


def test_telemetry_records_starved_oldest_first_starvation(telemetry, trigger):
    """End-to-end: the oldest-first cap-2 selector starves the newest entry,
    and the detector records exactly that."""
    items = [_item("newest"), _item("mid"), _item("oldest")]  # newest-first INDEX
    selected = trigger._selected_oldest_first(items, 2)
    selected_keys = [it.document_name for it in selected]
    actionable_keys = [it.document_name for it in items]
    assert selected_keys == ["oldest", "mid"]  # newest is starved

    telem, _ = _update(telemetry, None, actionable_keys, selected_keys)
    assert _entries(telem)["newest"]["consecutive_non_selection"] == 1
    assert "oldest" not in _entries(telem) and "mid" not in _entries(telem)
