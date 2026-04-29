# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for scripts/bridge_poller_runner.py.

Per ``bridge/gtkb-bridge-poller-p3-notify-2026-04-29-008.md`` GO conditions:

- AC #4-#7: --once / --interval / --max-iterations / bootstrap behavior
- AC #9: no-subprocess invariant — runner does NOT invoke subprocess.run
- AC #14, #15, #17 (+LC14, LC15): current-state lifecycle + bootstrap suppression
- AC #18 (+LC11-LC13): schema v2

Bridge imports are lazy per tests/test_bridge_import_hygiene rule.
The runner script itself is loaded via importlib because it lives under
scripts/, not the package proper.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest

_RUNNER_PATH = Path(__file__).resolve().parents[1] / "scripts" / "bridge_poller_runner.py"


def _load_runner() -> ModuleType:
    """Load scripts/bridge_poller_runner.py with sys.modules registration."""
    assert _RUNNER_PATH.is_file(), f"Expected runner at {_RUNNER_PATH}"
    module_name = "bridge_poller_runner"
    if module_name in sys.modules:
        return sys.modules[module_name]
    spec = importlib.util.spec_from_file_location(module_name, _RUNNER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _paths() -> SimpleNamespace:
    from groundtruth_kb.bridge.paths import GROUNDTRUTH_MARKER, PROJECT_ROOT_ENV_VAR

    return SimpleNamespace(
        GROUNDTRUTH_MARKER=GROUNDTRUTH_MARKER,
        PROJECT_ROOT_ENV_VAR=PROJECT_ROOT_ENV_VAR,
    )


def _notify_paths(state_dir: Path, recipient: str) -> tuple[Path, Path]:
    notif_dir = state_dir / "notifications"
    return (
        notif_dir / f"pending-bridge-action-{recipient}.json",
        notif_dir / f"pending-bridge-action-{recipient}.md",
    )


@pytest.fixture
def synthetic_gtkb_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    p = _paths()
    synth = tmp_path / "synth_gtkb"
    synth.mkdir()
    (synth / p.GROUNDTRUTH_MARKER).write_text("# synthetic\n", encoding="utf-8")
    (synth / "bridge").mkdir()
    monkeypatch.setenv(p.PROJECT_ROOT_ENV_VAR, str(synth))
    return synth


def _seed_bridge(synth: Path, doc_name: str, top_status: str, top_version: int = 2) -> None:
    bridge_dir = synth / "bridge"
    (bridge_dir / f"{doc_name}-{top_version:03d}.md").write_text("# stub\n", encoding="utf-8")
    if top_version != 1:
        (bridge_dir / f"{doc_name}-001.md").write_text("# stub\n", encoding="utf-8")
    index_path = bridge_dir / "INDEX.md"
    text = (
        f"# Bridge Index\n\n"
        f"Document: {doc_name}\n"
        f"{top_status}: bridge/{doc_name}-{top_version:03d}.md\n"
        f"NEW: bridge/{doc_name}-001.md\n"
    )
    index_path.write_text(text, encoding="utf-8")


# --- AC #9: no-subprocess invariant -----------------------------------------


def test_poller_loop_does_not_invoke_subprocess(synthetic_gtkb_root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """AC #9: poller must NOT invoke any subprocess (no spawning).

    Asserts via monkeypatch.setattr(subprocess, "run", ...) that the poller's
    full multi-iteration loop completes without calling subprocess.run.
    """
    runner = _load_runner()
    _seed_bridge(synthetic_gtkb_root, "foo", "REVISED")

    def _fail_unconditionally(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("Poller invoked subprocess.run; no-spawn invariant violated.")

    monkeypatch.setattr(subprocess, "run", _fail_unconditionally)
    iterations = runner.main_loop(interval_s=0, max_iterations=3, quiet=True)
    assert iterations == 3


# --- AC #4: --once mode -----------------------------------------------------


def test_main_invokes_once_and_exits(synthetic_gtkb_root: Path) -> None:
    runner = _load_runner()
    _seed_bridge(synthetic_gtkb_root, "foo", "GO")
    rc = runner.main(["--once", "--quiet"])
    assert rc == 0


# --- LC15: bootstrap iteration writes no notification files ---------------


def test_bootstrap_iteration_writes_no_notification_files(
    synthetic_gtkb_root: Path,
) -> None:
    """LC15: iteration 1 (bootstrap) does NOT create notification files."""
    runner = _load_runner()
    _seed_bridge(synthetic_gtkb_root, "foo", "REVISED")

    runner.main_loop(interval_s=0, max_iterations=1, quiet=True)

    state_dir = synthetic_gtkb_root / ".gtkb-state" / "bridge-poller"
    prime_json, prime_md = _notify_paths(state_dir, "prime")
    codex_json, codex_md = _notify_paths(state_dir, "codex")
    assert not prime_json.exists()
    assert not prime_md.exists()
    assert not codex_json.exists()
    assert not codex_md.exists()


# --- LC14: first post-bootstrap iteration notifies pre-existing entries ---


def test_first_post_bootstrap_iteration_notifies_pre_existing_actionable_entries(
    synthetic_gtkb_root: Path,
) -> None:
    """LC14 / Option A: iteration 2 on a populated INDEX writes notifications
    for ALL currently-actionable top statuses (including pre-existing entries)."""
    runner = _load_runner()
    _seed_bridge(synthetic_gtkb_root, "foo", "REVISED")

    runner.main_loop(interval_s=0, max_iterations=2, quiet=True)

    state_dir = synthetic_gtkb_root / ".gtkb-state" / "bridge-poller"
    codex_json, codex_md = _notify_paths(state_dir, "codex")
    assert codex_json.is_file()
    assert codex_md.is_file()
    payload = json.loads(codex_json.read_text(encoding="utf-8"))
    assert payload["schema_version"] == 2
    assert payload["pending_actions"][0]["top_status"] == "REVISED"


# --- LC1, LC2: persistence across unchanged scans -------------------------


def test_revised_persists_across_unchanged_scans(synthetic_gtkb_root: Path) -> None:
    """LC1 (integration): unchanged INDEX → REVISED stays in Codex notification."""
    runner = _load_runner()
    _seed_bridge(synthetic_gtkb_root, "foo", "REVISED")

    runner.main_loop(interval_s=0, max_iterations=4, quiet=True)

    state_dir = synthetic_gtkb_root / ".gtkb-state" / "bridge-poller"
    codex_json, _ = _notify_paths(state_dir, "codex")
    assert codex_json.is_file()
    payload = json.loads(codex_json.read_text(encoding="utf-8"))
    assert payload["pending_actions"][0]["top_status"] == "REVISED"


def test_go_persists_across_unchanged_scans(synthetic_gtkb_root: Path) -> None:
    """LC2 (integration): unchanged INDEX → GO stays in Prime notification."""
    runner = _load_runner()
    _seed_bridge(synthetic_gtkb_root, "foo", "GO")

    runner.main_loop(interval_s=0, max_iterations=4, quiet=True)

    state_dir = synthetic_gtkb_root / ".gtkb-state" / "bridge-poller"
    prime_json, _ = _notify_paths(state_dir, "prime")
    assert prime_json.is_file()
    payload = json.loads(prime_json.read_text(encoding="utf-8"))
    assert payload["pending_actions"][0]["top_status"] == "GO"


# --- LC3: REVISED → GO transition moves notification ----------------------


def test_revised_to_go_transition_moves_notification(synthetic_gtkb_root: Path) -> None:
    """LC3 (integration): top transitions REVISED → GO; notif moves Codex → Prime."""
    runner = _load_runner()
    _seed_bridge(synthetic_gtkb_root, "foo", "REVISED", top_version=2)

    # Bootstrap + first scan
    runner.main_loop(interval_s=0, max_iterations=2, quiet=True)
    state_dir = synthetic_gtkb_root / ".gtkb-state" / "bridge-poller"
    codex_json, _ = _notify_paths(state_dir, "codex")
    prime_json, _ = _notify_paths(state_dir, "prime")
    assert codex_json.is_file()
    assert not prime_json.is_file()

    # Promote top to GO
    bridge_dir = synthetic_gtkb_root / "bridge"
    (bridge_dir / "foo-003.md").write_text("# stub\n", encoding="utf-8")
    (bridge_dir / "INDEX.md").write_text(
        "# Bridge Index\n\nDocument: foo\nGO: bridge/foo-003.md\nREVISED: bridge/foo-002.md\nNEW: bridge/foo-001.md\n",
        encoding="utf-8",
    )
    runner.main_loop(interval_s=0, max_iterations=1, quiet=True)
    assert not codex_json.is_file()
    assert prime_json.is_file()
    payload = json.loads(prime_json.read_text(encoding="utf-8"))
    assert payload["pending_actions"][0]["top_status"] == "GO"


# --- LC4: VERIFIED clears notifications ----------------------------------


def test_revised_to_verified_clears_codex_notification(synthetic_gtkb_root: Path) -> None:
    """LC4 (integration): top transitions to VERIFIED; both notifs absent."""
    runner = _load_runner()
    _seed_bridge(synthetic_gtkb_root, "foo", "REVISED", top_version=2)

    runner.main_loop(interval_s=0, max_iterations=2, quiet=True)
    state_dir = synthetic_gtkb_root / ".gtkb-state" / "bridge-poller"
    codex_json, _ = _notify_paths(state_dir, "codex")
    assert codex_json.is_file()

    # Promote to VERIFIED
    bridge_dir = synthetic_gtkb_root / "bridge"
    (bridge_dir / "foo-004.md").write_text("# stub\n", encoding="utf-8")
    (bridge_dir / "INDEX.md").write_text(
        "# Bridge Index\n\n"
        "Document: foo\n"
        "VERIFIED: bridge/foo-004.md\n"
        "REVISED: bridge/foo-002.md\n"
        "NEW: bridge/foo-001.md\n",
        encoding="utf-8",
    )
    runner.main_loop(interval_s=0, max_iterations=1, quiet=True)

    prime_json, _ = _notify_paths(state_dir, "prime")
    assert not codex_json.is_file()
    assert not prime_json.is_file()


# --- Audit logging --------------------------------------------------------


def test_poller_writes_jsonl_audit_log(synthetic_gtkb_root: Path) -> None:
    runner = _load_runner()
    _seed_bridge(synthetic_gtkb_root, "foo", "GO")
    runner.main_loop(interval_s=0, max_iterations=2, quiet=True)
    state_dir = synthetic_gtkb_root / ".gtkb-state" / "bridge-poller"
    log_dir = state_dir / "poller-runs"
    assert log_dir.is_dir()
    log_files = list(log_dir.glob("*.jsonl"))
    assert len(log_files) == 1
    lines = log_files[0].read_text(encoding="utf-8").strip().splitlines()
    payloads = [json.loads(line) for line in lines]
    kinds = {p["kind"] for p in payloads}
    assert "bootstrap" in kinds
    assert "scan" in kinds
    assert "shutdown" in kinds


# --- run_one_iteration directly (white-box) ------------------------------


def test_run_one_iteration_returns_bootstrap_kind_on_first_call(
    synthetic_gtkb_root: Path,
) -> None:
    runner = _load_runner()
    _seed_bridge(synthetic_gtkb_root, "foo", "GO")
    state_dir = synthetic_gtkb_root / ".gtkb-state" / "bridge-poller"
    payload = runner.run_one_iteration(
        state_dir=state_dir,
        project_root=synthetic_gtkb_root,
        run_id="test-run-001",
        iteration=0,
    )
    assert payload["kind"] == "bootstrap"


def test_run_one_iteration_returns_scan_kind_on_second_call(
    synthetic_gtkb_root: Path,
) -> None:
    runner = _load_runner()
    _seed_bridge(synthetic_gtkb_root, "foo", "GO")
    state_dir = synthetic_gtkb_root / ".gtkb-state" / "bridge-poller"
    runner.run_one_iteration(
        state_dir=state_dir,
        project_root=synthetic_gtkb_root,
        run_id="test-run-002",
        iteration=0,
    )
    payload = runner.run_one_iteration(
        state_dir=state_dir,
        project_root=synthetic_gtkb_root,
        run_id="test-run-002",
        iteration=1,
    )
    assert payload["kind"] == "scan"
    assert payload["actionable_prime_count"] == 1
    assert payload["actionable_codex_count"] == 0


# --- max-iterations cap --------------------------------------------------


def test_main_loop_respects_max_iterations(synthetic_gtkb_root: Path) -> None:
    runner = _load_runner()
    _seed_bridge(synthetic_gtkb_root, "foo", "REVISED")
    completed = runner.main_loop(interval_s=0, max_iterations=5, quiet=True)
    assert completed == 5
