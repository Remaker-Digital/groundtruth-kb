# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for scripts/bridge_poller_runner.py.

Per ``bridge/gtkb-bridge-poller-p3-notify-2026-04-29-008.md`` GO conditions:

- AC #4-#7: --once / --interval / --max-iterations / bootstrap behavior
- Dispatch contract: automatic harness launch occurs only when work is pending
  and the pending-action signature has not already been dispatched.
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


# --- Dispatch contract -------------------------------------------------------


def test_poller_loop_does_not_launch_harness_when_no_work_waits(
    synthetic_gtkb_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """No actionable work means no harness launch and no token spend."""
    runner = _load_runner()
    _seed_bridge(synthetic_gtkb_root, "foo", "VERIFIED")

    def _fail_unconditionally(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("Poller launched a harness despite no actionable work.")

    monkeypatch.setattr(subprocess, "Popen", _fail_unconditionally)
    iterations = runner.main_loop(interval_s=0, max_iterations=3, quiet=True, dispatch_enabled=True)
    assert iterations == 3


def test_poller_loop_launches_harness_once_for_pending_signature(
    synthetic_gtkb_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Actionable work triggers the recipient harness once; unchanged work does not relaunch."""
    runner = _load_runner()
    _seed_bridge(synthetic_gtkb_root, "foo", "REVISED")
    calls: list[list[str]] = []

    class _FakeProcess:
        pid = 12345

    def _fake_popen(command: list[str], **_kwargs: object) -> _FakeProcess:
        calls.append(command)
        return _FakeProcess()

    monkeypatch.setattr(subprocess, "Popen", _fake_popen)
    iterations = runner.main_loop(interval_s=0, max_iterations=3, quiet=True, dispatch_enabled=True)

    assert iterations == 3
    assert len(calls) == 1
    assert calls[0][0:2] == ["codex", "exec"]
    assert "--cd" in calls[0]
    state_path = synthetic_gtkb_root / ".gtkb-state" / "bridge-poller" / "dispatch-state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert state["recipients"]["codex"]["pending_count"] == 1
    assert state["recipients"]["codex"]["last_result"] == "unchanged"


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
    # Schema v3 per smart-poller-kind-aware-routing-2026-04-30-009 REVISED-4.
    assert payload["schema_version"] == 3
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


# --- audit-only transitions_count (per -005 §1.2 / -007 §3 / -010 NO-GO) ---


def test_post_bootstrap_records_transitions_count_audit_only(synthetic_gtkb_root: Path) -> None:
    """Per `-005 §1.2` preserved in `-007 §3` and required by `-010` NO-GO:
    post-bootstrap iterations must compute `transitions = diff_against_checkpoint(...)`
    for audit-only observability, emit `transitions_count` in the scan audit
    payload + per-iteration JSONL log, and keep notification contents sourced
    only from `compute_actionable_pending()` (current-state semantics)."""
    runner = _load_runner()
    _seed_bridge(synthetic_gtkb_root, "foo", "REVISED", top_version=2)
    state_dir = synthetic_gtkb_root / ".gtkb-state" / "bridge-poller"

    # Iteration 0: bootstrap — writes checkpoint, no notification, no scan event.
    bootstrap_payload = runner.run_one_iteration(
        state_dir=state_dir,
        project_root=synthetic_gtkb_root,
        run_id="test-run-trans",
        iteration=0,
    )
    assert bootstrap_payload["kind"] == "bootstrap"
    # Bootstrap reports `transitions_routable`, not transitions_count.
    assert "transitions_count" not in bootstrap_payload

    # Iteration 1: first post-bootstrap with unchanged INDEX → 0 transitions
    # but notification still surfaces REVISED for codex (Option A current-state).
    unchanged_payload = runner.run_one_iteration(
        state_dir=state_dir,
        project_root=synthetic_gtkb_root,
        run_id="test-run-trans",
        iteration=1,
    )
    assert unchanged_payload["kind"] == "scan"
    assert unchanged_payload["transitions_count"] == 0
    assert unchanged_payload["actionable_codex_count"] == 1
    assert unchanged_payload["actionable_prime_count"] == 0

    codex_json, _ = _notify_paths(state_dir, "codex")
    assert codex_json.is_file()
    payload_after_unchanged = json.loads(codex_json.read_text(encoding="utf-8"))
    assert payload_after_unchanged["pending_actions"][0]["top_status"] == "REVISED"

    # Promote top to GO so the diff produces exactly one transition.
    bridge_dir = synthetic_gtkb_root / "bridge"
    (bridge_dir / "foo-003.md").write_text("# stub\n", encoding="utf-8")
    (bridge_dir / "INDEX.md").write_text(
        "# Bridge Index\n\nDocument: foo\nGO: bridge/foo-003.md\nREVISED: bridge/foo-002.md\nNEW: bridge/foo-001.md\n",
        encoding="utf-8",
    )

    # Iteration 2: REVISED → GO transition.
    transition_payload = runner.run_one_iteration(
        state_dir=state_dir,
        project_root=synthetic_gtkb_root,
        run_id="test-run-trans",
        iteration=2,
    )
    assert transition_payload["kind"] == "scan"
    assert transition_payload["transitions_count"] == 1
    # Notification routing follows current-state, NOT the diff: GO routes to prime.
    assert transition_payload["actionable_prime_count"] == 1
    assert transition_payload["actionable_codex_count"] == 0

    prime_json, _ = _notify_paths(state_dir, "prime")
    assert prime_json.is_file()
    assert not codex_json.is_file()  # codex notification cleared by current-state recompute.
    payload_after_transition = json.loads(prime_json.read_text(encoding="utf-8"))
    assert payload_after_transition["pending_actions"][0]["top_status"] == "GO"


def test_main_loop_writes_transitions_count_to_jsonl_audit_log(synthetic_gtkb_root: Path) -> None:
    """Companion to test_post_bootstrap_records_transitions_count_audit_only:
    confirm `transitions_count` lands in the per-run JSONL log written by
    `_log_iteration` (which records the run_one_iteration return payload)."""
    runner = _load_runner()
    _seed_bridge(synthetic_gtkb_root, "foo", "GO")
    runner.main_loop(interval_s=0, max_iterations=2, quiet=True)
    state_dir = synthetic_gtkb_root / ".gtkb-state" / "bridge-poller"
    log_files = list((state_dir / "poller-runs").glob("*.jsonl"))
    assert len(log_files) == 1
    payloads = [json.loads(line) for line in log_files[0].read_text(encoding="utf-8").strip().splitlines()]
    scan_payloads = [p for p in payloads if p["kind"] == "scan"]
    assert len(scan_payloads) == 1
    assert "transitions_count" in scan_payloads[0]
    # Single-doc seed; first post-bootstrap scan against unchanged checkpoint → 0 transitions.
    assert scan_payloads[0]["transitions_count"] == 0


# ===========================================================================
# Smart-poller kind-aware routing dispatch filter — per smart-poller-kind-
# aware-routing-2026-04-30 thread (GO at -010). The runner's _dispatch_if_
# needed filters items on dispatchable BEFORE signature/spawn so terminal-kind
# GO entries don't spawn redundant harnesses.
# ===========================================================================


def _seed_kind_bridge(
    synth: Path,
    doc_name: str,
    top_status: str,
    operative_kind: str | None,
    operative_status: str = "REVISED",
    operative_version: int = 3,
    top_version: int = 4,
) -> None:
    """Seed an INDEX with a Codex-verdict top file (no bridge_kind) plus an
    operative Prime version that carries bridge_kind."""
    bridge_dir = synth / "bridge"
    bridge_dir.mkdir(exist_ok=True)
    # Top file (verdict)
    top_path = bridge_dir / f"{doc_name}-{top_version:03d}.md"
    top_path.write_text(f"# {top_status} verdict\n", encoding="utf-8")
    # Operative Prime version
    op_path = bridge_dir / f"{doc_name}-{operative_version:03d}.md"
    op_content = f"# Prime {operative_status}\n"
    if operative_kind is not None:
        op_content += f"bridge_kind: {operative_kind}\n"
    op_path.write_text(op_content, encoding="utf-8")
    # INDEX
    index_path = bridge_dir / "INDEX.md"
    text = (
        f"# Bridge Index\n\n"
        f"Document: {doc_name}\n"
        f"{top_status}: bridge/{doc_name}-{top_version:03d}.md\n"
        f"{operative_status}: bridge/{doc_name}-{operative_version:03d}.md\n"
    )
    index_path.write_text(text, encoding="utf-8")


def test_dispatch_consumer_skips_terminal_prime_GO_entries(
    synthetic_gtkb_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The core token-cost-reduction case: a terminal-kind GO does NOT launch
    a Prime harness."""
    runner = _load_runner()
    _seed_kind_bridge(synthetic_gtkb_root, "scoping_thread", "GO", "scoping_proposal")

    def _fail_unconditionally(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("Dispatch consumer launched harness for terminal-kind GO entry.")

    monkeypatch.setattr(subprocess, "Popen", _fail_unconditionally)
    runner.main_loop(interval_s=0, max_iterations=3, quiet=True, dispatch_enabled=True)

    state_path = synthetic_gtkb_root / ".gtkb-state" / "bridge-poller" / "dispatch-state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    # Filtered terminal count is recorded and the result is no_pending_after_filter.
    assert state["recipients"]["prime"]["filtered_terminal_count"] == 1
    assert state["recipients"]["prime"]["last_result"] == "no_pending_after_filter"
    assert state["recipients"]["prime"]["pending_count"] == 0  # filtered to zero


def test_dispatch_consumer_includes_terminal_prime_NO_GO_entries(
    synthetic_gtkb_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """F1 fix from -008 NO-GO: terminal-kind NO-GO must dispatch Prime."""
    runner = _load_runner()
    _seed_kind_bridge(synthetic_gtkb_root, "intake_thread", "NO-GO", "candidate_spec_intake")
    calls: list[list[str]] = []

    class _FakeProcess:
        pid = 12345

    def _fake_popen(command: list[str], **_kwargs: object) -> _FakeProcess:
        calls.append(command)
        return _FakeProcess()

    monkeypatch.setattr(subprocess, "Popen", _fake_popen)
    runner.main_loop(interval_s=0, max_iterations=3, quiet=True, dispatch_enabled=True)

    # Prime harness launched once for the NO-GO entry (terminal-kind didn't filter it).
    assert len(calls) == 1


def test_dispatch_consumer_includes_terminal_codex_entries(
    synthetic_gtkb_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """F1 fix from -006 NO-GO: terminal-kind NEW must dispatch Codex review."""
    runner = _load_runner()
    _seed_kind_bridge(
        synthetic_gtkb_root, "scoping_thread", "NEW", "scoping_proposal",
        operative_status="NEW", operative_version=4, top_version=4,
    )
    calls: list[list[str]] = []

    class _FakeProcess:
        pid = 12345

    def _fake_popen(command: list[str], **_kwargs: object) -> _FakeProcess:
        calls.append(command)
        return _FakeProcess()

    monkeypatch.setattr(subprocess, "Popen", _fake_popen)
    runner.main_loop(interval_s=0, max_iterations=3, quiet=True, dispatch_enabled=True)

    # Codex harness launched once for the NEW entry.
    assert len(calls) == 1


def test_dispatch_consumer_includes_dispatchable_prime_GO(
    synthetic_gtkb_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Implementation-kind GO entries still dispatch Prime."""
    runner = _load_runner()
    _seed_kind_bridge(synthetic_gtkb_root, "impl_thread", "GO", "implementation_proposal")
    calls: list[list[str]] = []

    class _FakeProcess:
        pid = 12345

    def _fake_popen(command: list[str], **_kwargs: object) -> _FakeProcess:
        calls.append(command)
        return _FakeProcess()

    monkeypatch.setattr(subprocess, "Popen", _fake_popen)
    runner.main_loop(interval_s=0, max_iterations=3, quiet=True, dispatch_enabled=True)

    assert len(calls) == 1


def test_dispatch_consumer_includes_ambiguous_legacy_GO(
    synthetic_gtkb_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Legacy bridges with no bridge_kind: still dispatch (preserves current behavior)."""
    runner = _load_runner()
    _seed_kind_bridge(synthetic_gtkb_root, "legacy_thread", "GO", None)
    calls: list[list[str]] = []

    class _FakeProcess:
        pid = 12345

    def _fake_popen(command: list[str], **_kwargs: object) -> _FakeProcess:
        calls.append(command)
        return _FakeProcess()

    monkeypatch.setattr(subprocess, "Popen", _fake_popen)
    runner.main_loop(interval_s=0, max_iterations=3, quiet=True, dispatch_enabled=True)

    assert len(calls) == 1


def test_dispatch_consumer_disabled_via_env_var_bypasses_filter(
    synthetic_gtkb_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """GTKB_NOTIFY_KIND_AWARE_ROUTING=0 reverts to pre-refinement spawn behavior:
    even a terminal-kind GO triggers Prime harness launch."""
    runner = _load_runner()
    _seed_kind_bridge(synthetic_gtkb_root, "scoping_thread", "GO", "scoping_proposal")
    monkeypatch.setenv("GTKB_NOTIFY_KIND_AWARE_ROUTING", "0")
    calls: list[list[str]] = []

    class _FakeProcess:
        pid = 12345

    def _fake_popen(command: list[str], **_kwargs: object) -> _FakeProcess:
        calls.append(command)
        return _FakeProcess()

    monkeypatch.setattr(subprocess, "Popen", _fake_popen)
    runner.main_loop(interval_s=0, max_iterations=3, quiet=True, dispatch_enabled=True)

    # With kind-aware filtering disabled, the terminal-kind GO still spawns.
    assert len(calls) == 1
