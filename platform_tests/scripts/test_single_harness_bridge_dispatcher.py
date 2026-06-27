# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Script-level tests for scripts/single_harness_bridge_dispatcher.py.

Authority: bridge/gtkb-single-harness-bridge-dispatcher-slice-2-005.md
(Codex GO at -006). IP-5 test surface for IP-1 (dispatcher script).

Specs:
- SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001 v1 (behavior contract).
- DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001 v1 (wake substrate).
- ADR-SINGLE-HARNESS-OPERATING-MODE-001 v1 (operating-mode topology).
- SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001 v1 (keyword emitted).
- PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001 v2 (audit-log discipline).
"""

from __future__ import annotations

import datetime as dt
import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DISPATCHER_PATH = PROJECT_ROOT / "scripts" / "single_harness_bridge_dispatcher.py"


def _load_dispatcher() -> ModuleType:
    name = "single_harness_bridge_dispatcher_for_test"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, DISPATCHER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _make_synthetic_project(root: Path, single_harness: bool = False) -> Path:
    """Create a minimal in-root synthetic GT-KB project.

    If ``single_harness=True``, the role map records one harness ID with a
    multi-element role-set. Otherwise it records two harnesses with singleton
    role-sets (the default multi-harness topology).
    """
    (root / "groundtruth.toml").write_text(
        '[project]\nproject_name = "TestSynthetic"\nprofile = "dual-agent"\n',
        encoding="utf-8",
    )
    (root / "bridge").mkdir(exist_ok=True)
    harness_state = root / "harness-state"
    harness_state.mkdir(exist_ok=True)
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

    claude_surfaces = {
        "headless": {"argv": ["claude", "-p", "{{PROMPT}}", "--add-dir", "{{PROJECT_ROOT}}", "--output-format", "json"]}
    }
    codex_surfaces = {"headless": {"argv": ["codex", "exec", "{{PROMPT}}", "--cd", "{{PROJECT_ROOT}}"]}}

    if single_harness:
        (harness_state / "role-assignments.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "harnesses": {
                        "B": {
                            "role": ["prime-builder", "loyal-opposition"],
                            "harness_type": "claude",
                        }
                    },
                }
            ),
            encoding="utf-8",
        )
        registry_harnesses = [
            {
                "id": "B",
                "harness_name": "claude",
                "harness_type": "claude",
                "status": "active",
                "event_driven_hooks": True,
                "role": ["prime-builder", "loyal-opposition"],
                "invocation_surfaces": claude_surfaces,
            }
        ]
    else:
        (harness_state / "role-assignments.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "harnesses": {
                        "B": {"role": ["prime-builder"], "harness_type": "claude"},
                        "A": {"role": ["loyal-opposition"], "harness_type": "codex"},
                    },
                }
            ),
            encoding="utf-8",
        )
        registry_harnesses = [
            {
                "id": "B",
                "harness_name": "claude",
                "harness_type": "claude",
                "status": "active",
                "event_driven_hooks": True,
                "role": ["prime-builder"],
                "invocation_surfaces": claude_surfaces,
            },
            {
                "id": "A",
                "harness_name": "codex",
                "harness_type": "codex",
                "status": "active",
                "event_driven_hooks": True,
                "role": ["loyal-opposition"],
                "invocation_surfaces": codex_surfaces,
            },
        ]
    (harness_state / "harness-registry.json").write_text(
        json.dumps({"schema_version": 1, "harnesses": registry_harnesses}),
        encoding="utf-8",
    )
    return root


def _write_index(root: Path, body: str) -> None:
    (root / "bridge" / "INDEX.md").write_text(body, encoding="utf-8")


def _write_work_subject(root: Path, subject: str) -> None:
    state_path = root / ".claude" / "session" / "work-subject.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "current_subject": subject,
                "source": "test fixture",
                "updated_by": "pytest",
            }
        ),
        encoding="utf-8",
    )


def _suppression_records(state_dir: Path) -> list[dict]:
    path = state_dir / "dispatch-suppressions.jsonl"
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _write_bridge_file(root: Path, name: str) -> None:
    (root / "bridge" / name).write_text("bridge_kind: implementation_proposal\n", encoding="utf-8")


def _write_authorized_go_thread(
    root: Path,
    doc: str,
    target_paths: list[str] | None = None,
    project_id: str | None = None,
) -> str:
    if target_paths is None:
        target_paths = ["scripts/single_harness_bridge_dispatcher.py"]
    proposal = "\n".join(
        [
            "NEW",
            "",
            f"# Fixture proposal {doc}",
            "",
            f"target_paths: {json.dumps(target_paths)}",
            "",
            *(["Project: " + project_id, ""] if project_id else []),
            "## Specification Links",
            "",
            "- GOV-FILE-BRIDGE-AUTHORITY-001 - bridge authority.",
            "- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - spec linkage.",
            "",
            "## Requirement Sufficiency",
            "",
            "Existing requirements are sufficient.",
            "",
            "## Verification Plan",
            "",
            "Run focused dispatch packet tests.",
            "",
        ]
    )
    (root / "bridge" / f"{doc}.md").write_text(proposal, encoding="utf-8")
    (root / "bridge" / f"{doc}-002.md").write_text("GO\n\nFixture GO.\n", encoding="utf-8")
    return f"# bridge index\n\nDocument: {doc}\nGO: bridge/{doc}-002.md\nNEW: bridge/{doc}.md\n"


def _index_with_one_new(root: Path) -> str:
    (root / "bridge" / "example-thread-001.md").write_text(
        "NEW\n\nauthor_session_context_id: fixture-author-session\n",
        encoding="utf-8",
    )
    return "# bridge index\n\nDocument: example-thread\nNEW: bridge/example-thread-001.md\n"


# ──────────────────────────────────────────────────────────────────────────
# T-SHD-S2-multi-harness-noop
# ──────────────────────────────────────────────────────────────────────────


def test_dispatcher_runs_in_multi_harness_topology(tmp_path: Path) -> None:
    """ADR-SINGLE-HARNESS-OPERATING-MODE-001: unified poller runs in both topologies."""
    root = _make_synthetic_project(tmp_path, single_harness=False)
    _write_index(root, _index_with_one_new(root))
    state_dir = tmp_path / "state"

    dispatcher = _load_dispatcher()
    summary = dispatcher.run_dispatcher(project_root=root, state_dir=state_dir, dry_run=True)
    assert summary["skipped"] is False
    assert summary["results"]["loyal-opposition"]["reason"] == "dry_run"


def test_single_harness_dispatcher_honors_prime_work_intent_filter_project_guard(tmp_path: Path) -> None:
    root = _make_synthetic_project(tmp_path, single_harness=True)
    dispatcher = _load_dispatcher()
    dispatcher._load_trigger_module()
    registry = sys.modules["bridge_work_intent_registry"]
    state_dir = tmp_path / "state"
    project_id = "PROJECT-GUARD"
    holder_session = "2026-06-22T00-00-00Z-prime-builder-B-abc123"

    _write_authorized_go_thread(root, "held-thread", project_id=project_id)
    _write_index(root, _write_authorized_go_thread(root, "selected-thread", project_id=project_id))
    assert registry.acquire("held-thread", holder_session, project_root=root)

    summary = dispatcher.run_dispatcher(project_root=root, state_dir=state_dir, dry_run=True)

    assert summary["skipped"] is False
    assert summary["results"]["prime-builder"]["reason"] == "work_intent_already_held"
    suppressions_path = state_dir / "dispatch-suppressions.jsonl"
    records = [json.loads(line) for line in suppressions_path.read_text(encoding="utf-8").splitlines() if line]
    project_guard_records = [record for record in records if record["reason"] == "same_role_project_claim_active"]
    assert len(project_guard_records) == 1
    assert project_guard_records[0]["document_name"] == "selected-thread"
    assert project_guard_records[0]["project_id"] == project_id
    assert project_guard_records[0]["holder_thread_slug"] == "held-thread"


# ──────────────────────────────────────────────────────────────────────────
# T-SHD-S2-spawn-on-signature-change
# ──────────────────────────────────────────────────────────────────────────


def test_dispatcher_spawns_in_single_harness_topology_on_signature_change(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001 § Wake Mechanism step 3."""
    root = _make_synthetic_project(tmp_path, single_harness=True)
    _write_index(root, _index_with_one_new(root))
    state_dir = tmp_path / "state"

    dispatcher = _load_dispatcher()
    summary = dispatcher.run_dispatcher(project_root=root, state_dir=state_dir, dry_run=True)
    assert summary["skipped"] is False
    assert summary["harness_id"] == "B"
    assert summary["command_handle"] == "claude"
    # In dry_run mode at least one role had pending work (NEW entry triggers LO).
    lo_result = summary["results"].get("loyal-opposition", {})
    assert lo_result.get("reason") == "dry_run"


def test_dispatcher_resolves_codex_single_harness_command_handle(tmp_path: Path) -> None:
    """Single-harness operation must work when Codex is the only active harness."""
    root = _make_synthetic_project(tmp_path, single_harness=False)
    (root / "harness-state" / "role-assignments.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "harnesses": {
                    "A": {
                        "role": ["prime-builder", "loyal-opposition"],
                        "harness_type": "codex",
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    (root / "harness-state" / "harness-registry.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "harnesses": [
                    {
                        "id": "A",
                        "harness_name": "codex",
                        "harness_type": "codex",
                        "status": "active",
                        "event_driven_hooks": True,
                        "role": ["prime-builder", "loyal-opposition"],
                        "invocation_surfaces": {
                            "headless": {"argv": ["codex", "exec", "{{PROMPT}}", "--cd", "{{PROJECT_ROOT}}"]}
                        },
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    _write_index(root, _index_with_one_new(root))
    state_dir = tmp_path / "state"

    dispatcher = _load_dispatcher()
    summary = dispatcher.run_dispatcher(project_root=root, state_dir=state_dir, dry_run=True)

    assert summary["skipped"] is False
    assert summary["harness_id"] == "A"
    assert summary["command_handle"] == "codex"
    assert summary["results"]["loyal-opposition"]["reason"] == "dry_run"


# ──────────────────────────────────────────────────────────────────────────
# T-SHD-S2-canonical-keyword
# ──────────────────────────────────────────────────────────────────────────


def test_dispatcher_emits_canonical_keyword_first_line(tmp_path: Path) -> None:
    """SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001 (first-line activator)."""
    dispatcher = _load_dispatcher()
    trigger = dispatcher._load_trigger_module()
    items = [
        SimpleNamespace(
            document_name="example",
            top_status="NEW",
            top_file="bridge/example-001.md",
            dispatchable=True,
        )
    ]
    prompt = dispatcher._build_prompt("lo", items, 2, trigger)
    first_line = prompt.splitlines()[0]
    assert first_line == "::init gtkb lo"


def test_dispatcher_keyword_pb_mode(tmp_path: Path) -> None:
    dispatcher = _load_dispatcher()
    trigger = dispatcher._load_trigger_module()
    prompt = dispatcher._build_prompt("pb", [], 2, trigger)
    first_line = prompt.splitlines()[0]
    assert first_line == "::init gtkb pb"


def test_dispatcher_suppresses_on_document_lease(tmp_path: Path) -> None:
    """Verify that if a document has a lease held, it is not dispatched by the dispatcher."""
    from bridge_lease_registry import acquire_lease, release_lease

    root = _make_synthetic_project(tmp_path, single_harness=True)
    _write_index(root, _index_with_one_new(root))
    state_dir = tmp_path / "state"
    state_dir.mkdir(parents=True, exist_ok=True)

    # Acquire lease on example-thread
    lease = acquire_lease("example-thread", action="test", state_dir=state_dir)
    assert lease is not None

    dispatcher = _load_dispatcher()
    summary = dispatcher.run_dispatcher(project_root=root, state_dir=state_dir, dry_run=True)
    # Loyal opposition results should be no_pending_after_filter because example-thread is leased!
    assert summary["skipped"] is False
    assert summary["results"]["loyal-opposition"]["reason"] == "no_pending_after_filter"

    release_lease(lease)


def test_application_subject_suppresses_single_harness_prime_dispatch_before_acquire_or_spawn(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _make_synthetic_project(tmp_path, single_harness=True)
    state_dir = tmp_path / "state"
    _write_index(root, _write_authorized_go_thread(root, "selected-thread"))
    _write_work_subject(root, "application")

    dispatcher = _load_dispatcher()
    trigger = dispatcher._load_trigger_module()

    def _forbidden_filter(*_args: object, **_kwargs: object) -> dict[str, object]:
        pytest.fail("application subject must suppress before prime work-intent filtering")

    def _forbidden_acquire(*_args: object, **_kwargs: object) -> dict[str, object]:
        pytest.fail("application subject must suppress before prime work-intent acquisition")

    def _forbidden_spawn(**_kwargs: object) -> dict[str, object]:
        pytest.fail("application subject must suppress before worker spawn")

    def _forbidden_release(*_args: object, **_kwargs: object) -> None:
        pytest.fail("application subject must not release in-flight prime work intent")

    monkeypatch.setattr(trigger, "_filter_prime_selected_by_work_intent", _forbidden_filter)
    monkeypatch.setattr(trigger, "_acquire_prime_work_intent_batch", _forbidden_acquire)
    monkeypatch.setattr(trigger, "_release_prime_work_intents", _forbidden_release)
    monkeypatch.setattr(dispatcher, "_spawn_worker", _forbidden_spawn)

    summary = dispatcher.run_dispatcher(project_root=root, state_dir=state_dir, dry_run=False)

    result = summary["results"]["prime-builder"]
    assert result["reason"] == trigger.WORK_SUBJECT_APPLICATION_SUSPENDED_REASON
    assert result["current_subject"] == "application"

    recipient_state = summary["dispatch_state"]["recipients"]["prime-builder"]
    assert recipient_state["last_result"] == trigger.WORK_SUBJECT_APPLICATION_SUSPENDED_REASON
    assert recipient_state["last_suppressed_signature"]
    assert recipient_state["last_dispatched_signature"] is None
    assert recipient_state["signature"] is None

    records = _suppression_records(state_dir)
    assert [record["reason"] for record in records] == [trigger.WORK_SUBJECT_APPLICATION_SUSPENDED_REASON]
    assert records[0]["document_names"] == ["selected-thread"]


def test_gtkb_subject_allows_single_harness_prime_dispatch_negative_control(tmp_path: Path) -> None:
    root = _make_synthetic_project(tmp_path, single_harness=True)
    state_dir = tmp_path / "state"
    _write_index(root, _write_authorized_go_thread(root, "selected-thread"))
    _write_work_subject(root, "gtkb_infrastructure")

    dispatcher = _load_dispatcher()
    summary = dispatcher.run_dispatcher(project_root=root, state_dir=state_dir, dry_run=True)

    assert summary["results"]["prime-builder"]["reason"] == "dry_run"
    recipient_state = summary["dispatch_state"]["recipients"]["prime-builder"]
    assert recipient_state["last_result"] == "launch_failed"
    assert recipient_state["last_dispatched_signature"] == recipient_state["signature"]
    assert recipient_state.get("last_suppressed_signature") is None
    assert _suppression_records(state_dir) == []


# ──────────────────────────────────────────────────────────────────────────
# T-SHD-S2-signature-dedup-loop-prevention
# ──────────────────────────────────────────────────────────────────────────


def test_dispatcher_loop_prevention_via_signature_dedup(tmp_path: Path) -> None:
    """DCL-SMART-POLLER-AUTO-TRIGGER-001 v2: actionable-only spawn invariant.

    Repeated invocation against same INDEX -> second invocation reports
    `unchanged`; no second spawn.
    """
    root = _make_synthetic_project(tmp_path, single_harness=True)
    _write_index(root, _index_with_one_new(root))
    state_dir = tmp_path / "state"

    dispatcher = _load_dispatcher()
    first = dispatcher.run_dispatcher(project_root=root, state_dir=state_dir, dry_run=True)
    assert first["results"]["loyal-opposition"]["reason"] == "dry_run"

    second = dispatcher.run_dispatcher(project_root=root, state_dir=state_dir, dry_run=True)
    assert second["results"]["loyal-opposition"]["reason"] == "unchanged"


# ──────────────────────────────────────────────────────────────────────────
# T-SHD-S2-signature-byte-identical (parity with cross-harness trigger)
# ──────────────────────────────────────────────────────────────────────────


def test_signature_byte_identical_to_trigger(tmp_path: Path) -> None:
    """SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001 § Wake Mechanism step 2:
    signature scheme byte-identical to cross-harness trigger so state-path
    sharing is safe across substrate transitions."""
    root = _make_synthetic_project(tmp_path, single_harness=True)
    _write_index(root, _index_with_one_new(root))
    state_dir_a = tmp_path / "state-dispatcher"

    dispatcher = _load_dispatcher()
    trigger = dispatcher._load_trigger_module()

    # Dispatcher run: produces signature for loyal-opposition.
    summary = dispatcher.run_dispatcher(project_root=root, state_dir=state_dir_a, dry_run=True)
    dispatch_sig = summary["dispatch_state"]["recipients"]["loyal-opposition"]["signature"]

    # Compute the same signature via trigger module helpers directly.
    index_text = trigger._read_index_live(root)
    _, codex_items = trigger._compute_actionable(index_text, root)
    filtered = [it for it in codex_items if getattr(it, "dispatchable", True)]
    selected = trigger._selected_oldest_first(filtered, dispatcher.DEFAULT_MAX_ITEMS)
    expected_sig = trigger._signature(selected)

    assert dispatch_sig == expected_sig


# ──────────────────────────────────────────────────────────────────────────
# T-SHD-S2-audit-log-failures
# ──────────────────────────────────────────────────────────────────────────


def test_dispatcher_records_dispatch_failures_jsonl(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001 v2: audit-log on failure."""
    root = _make_synthetic_project(tmp_path, single_harness=True)
    _write_index(root, _index_with_one_new(root))
    state_dir = tmp_path / "state"

    dispatcher = _load_dispatcher()

    def _boom_popen(*_args, **_kwargs):
        raise OSError("simulated spawn failure")

    import subprocess as _subprocess

    monkeypatch.setattr(_subprocess, "Popen", _boom_popen)

    dispatcher.run_dispatcher(project_root=root, state_dir=state_dir, dry_run=False)

    failures_path = state_dir / "dispatch-failures.jsonl"
    assert failures_path.is_file(), "dispatch-failures.jsonl not written on spawn failure"
    lines = [line for line in failures_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert lines, "dispatch-failures.jsonl was empty"
    # At least one line should reference the simulated failure.
    parsed = [json.loads(line) for line in lines]
    assert any(rec.get("launched") is False and "simulated" in str(rec.get("error_message", "")) for rec in parsed)


def test_prime_worker_spawn_creates_dispatch_authorization_packet_and_env(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _make_synthetic_project(tmp_path, single_harness=True)
    doc = "prime-implementation"
    _write_index(root, _write_authorized_go_thread(root, doc))
    state_dir = tmp_path / "state"
    dispatcher = _load_dispatcher()
    trigger = dispatcher._load_trigger_module()
    captured_envs: list[dict[str, str]] = []

    class _FakeProcess:
        pid = 12345

    def _fake_popen(*_args, **kwargs):
        captured_envs.append(kwargs.get("env", {}))
        return _FakeProcess()

    import subprocess as _subprocess

    monkeypatch.setattr(_subprocess, "Popen", _fake_popen)
    fake_item = SimpleNamespace(
        document_name=doc,
        top_status="GO",
        top_file=f"bridge/{doc}-002.md",
        dispatchable=True,
    )

    target = trigger.DispatchTarget(
        needed_role_label="prime-builder",
        harness_id="B",
        command_handle="claude",
        canonical_mode="pb",
        invocation_surfaces={
            "headless": {
                "argv": ["claude", "-p", "{{PROMPT}}", "--add-dir", "{{PROJECT_ROOT}}", "--output-format", "json"]
            }
        },
    )
    meta = dispatcher._spawn_worker(
        target=target,
        items=[fake_item],
        project_root=root,
        state_dir=state_dir,
        max_items=2,
        dry_run=False,
        trigger=trigger,
    )

    assert meta["launched"] is True
    current = json.loads(
        (root / ".gtkb-state" / "implementation-authorizations" / "current.json").read_text(encoding="utf-8")
    )
    assert current["bridge_id"] == doc
    assert current["target_path_globs"] == ["scripts/single_harness_bridge_dispatcher.py"]
    assert (root / ".gtkb-state" / "implementation-authorizations" / "by-bridge" / f"{doc}.json").is_file()
    child_env = captured_envs[0]
    assert child_env["GTKB_IMPLEMENTATION_AUTH_BRIDGE_IDS"] == doc
    assert child_env["GTKB_IMPLEMENTATION_AUTH_CURRENT_BRIDGE_ID"] == doc
    assert child_env["GTKB_IMPLEMENTATION_AUTH_PACKET_HASHES"] == current["packet_hash"]


# ──────────────────────────────────────────────────────────────────────────
# T-SHD-S2-diagnose-no-mutation
# ──────────────────────────────────────────────────────────────────────────


def test_dispatcher_diagnose_emits_liveness_summary(tmp_path: Path) -> None:
    """IP-1 CLI: --diagnose emits a structured liveness summary WITHOUT
    performing dispatch or mutating state."""
    root = _make_synthetic_project(tmp_path, single_harness=True)
    _write_index(root, _index_with_one_new(root))
    state_dir = tmp_path / "state"

    dispatcher = _load_dispatcher()
    output = dispatcher._emit_diagnose_summary(state_dir, root)

    # Required sections (always present).
    assert "Trigger infrastructure" in output
    assert "Dispatch state" in output
    assert "Overall" in output
    # Applicability reported.
    assert "Applicability:" in output
    # Cold-start path returns early without per-recipient section; rich path
    # includes all the sections. Verify whichever path applies.
    if "ABSENT" in output:
        assert "DEGRADED" in output  # cold-start branch
    else:
        assert "Per-recipient state" in output
        assert "Recent failures" in output

    # No dispatch-state file created by diagnose alone.
    state_path = state_dir / "dispatch-state.json"
    assert not state_path.exists(), "diagnose mode wrote dispatch-state.json (it must be read-only)"


# ──────────────────────────────────────────────────────────────────────────
# T-SHD-S2-loop-prevention-env-var
# ──────────────────────────────────────────────────────────────────────────


def test_dispatcher_respects_manual_disable_env_var(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Operator opt-out: GTKB_NO_SINGLE_HARNESS_DISPATCHER=1 -> short-circuit."""
    root = _make_synthetic_project(tmp_path, single_harness=True)
    _write_index(root, _index_with_one_new(root))
    state_dir = tmp_path / "state"

    monkeypatch.setenv("GTKB_NO_SINGLE_HARNESS_DISPATCHER", "1")

    dispatcher = _load_dispatcher()
    summary = dispatcher.run_dispatcher(project_root=root, state_dir=state_dir, dry_run=True)
    assert summary == {"skipped": True, "reason": "loop_prevention_env_var"}
    assert not (state_dir / "dispatch-state.json").exists()


# ──────────────────────────────────────────────────────────────────────────
# T-SHD-heartbeat — _parse_storm_watchdog_heartbeat
# Authority: bridge/gtkb-wi4742-autonomous-dispatch-loop-health-002.md GO
# ──────────────────────────────────────────────────────────────────────────


def _write_heartbeat(project_root: Path, content: str) -> Path:
    """Write a heartbeat file to the storm-watchdog path under project_root."""
    hb_path = project_root / ".gtkb-state" / "ops" / "storm-watchdog-heartbeat.txt"
    hb_path.parent.mkdir(parents=True, exist_ok=True)
    hb_path.write_text(content, encoding="utf-8")
    return hb_path


def _write_dispatch_state(
    state_dir: Path, pb_result: str = "no_actionable_change", lo_result: str = "no_actionable_change"
) -> None:
    """Write a minimal dispatch-state.json so _emit_diagnose_summary takes the rich path."""
    state_dir.mkdir(parents=True, exist_ok=True)
    state = {
        "updated_at": "2026-06-23T00:00:00+00:00",
        "recipients": {
            "prime-builder": {
                "last_result": pb_result,
                "pending_count": 0,
                "selected_count": 0,
                "signature": "a" * 64,
                "last_dispatched_signature": None,
            },
            "loyal-opposition": {
                "last_result": lo_result,
                "pending_count": 0,
                "selected_count": 0,
                "signature": "b" * 64,
                "last_dispatched_signature": None,
            },
        },
    }
    (state_dir / "dispatch-state.json").write_text(json.dumps(state), encoding="utf-8")


def test_parse_heartbeat_absent(tmp_path: Path) -> None:
    """Heartbeat file not present → absent=True, no error."""
    dispatcher = _load_dispatcher()
    result = dispatcher._parse_storm_watchdog_heartbeat(tmp_path)
    assert result["absent"] is True
    assert result["parse_error"] is None
    assert result["timestamp"] is None


def test_parse_heartbeat_modern_format(tmp_path: Path) -> None:
    """Modern format with noncodex field."""
    fresh_ts = dt.datetime.now(dt.UTC).isoformat()
    _write_heartbeat(tmp_path, f"{fresh_ts} codex=3 family=7 threshold=15 noncodex=4 noncodexThreshold=10\n")
    dispatcher = _load_dispatcher()
    result = dispatcher._parse_storm_watchdog_heartbeat(tmp_path)
    assert result["absent"] is False
    assert result["parse_error"] is None
    assert result["codex"] == 3
    assert result["family"] == 7
    assert result["threshold"] == 15
    assert result["noncodex"] == 4
    assert result["noncodex_threshold"] == 10
    assert result["age_seconds"] is not None
    assert result["stale"] is False  # fresh timestamp


def test_parse_heartbeat_older_format_without_noncodex(tmp_path: Path) -> None:
    """Older format without noncodex."""
    _write_heartbeat(tmp_path, "2026-06-23T00:00:00+00:00 codex=10 family=22 threshold=15\n")
    dispatcher = _load_dispatcher()
    result = dispatcher._parse_storm_watchdog_heartbeat(tmp_path)
    assert result["codex"] == 10
    assert result["family"] == 22
    assert result["noncodex"] is None
    assert result["noncodex_threshold"] is None


def test_parse_heartbeat_stale(tmp_path: Path) -> None:
    """Timestamp more than _HEARTBEAT_STALE_SECONDS old → stale=True."""
    # Use a timestamp well in the past (year 2000).
    _write_heartbeat(tmp_path, "2000-01-01T00:00:00+00:00 codex=1 family=2 threshold=15\n")
    dispatcher = _load_dispatcher()
    result = dispatcher._parse_storm_watchdog_heartbeat(tmp_path)
    assert result["stale"] is True
    assert result["age_seconds"] is not None and result["age_seconds"] > 300


def test_parse_heartbeat_empty_file(tmp_path: Path) -> None:
    """Empty heartbeat file → parse_error set."""
    _write_heartbeat(tmp_path, "")
    dispatcher = _load_dispatcher()
    result = dispatcher._parse_storm_watchdog_heartbeat(tmp_path)
    assert result["absent"] is False
    assert result["parse_error"] is not None


def test_parse_heartbeat_unparsable_timestamp(tmp_path: Path) -> None:
    """Unparsable timestamp → parse_error mentions the bad timestamp."""
    _write_heartbeat(tmp_path, "NOT-A-DATE codex=5 family=10 threshold=15\n")
    dispatcher = _load_dispatcher()
    result = dispatcher._parse_storm_watchdog_heartbeat(tmp_path)
    assert result["parse_error"] is not None
    assert "NOT-A-DATE" in result["parse_error"]


# ──────────────────────────────────────────────────────────────────────────
# T-SHD-heartbeat — _emit_diagnose_summary liveness section
# ──────────────────────────────────────────────────────────────────────────


def test_diagnose_summary_liveness_section_when_absent(tmp_path: Path) -> None:
    """When heartbeat file is absent, diagnose reports ABSENT."""
    root = _make_synthetic_project(tmp_path)
    state_dir = tmp_path / "state"
    _write_dispatch_state(state_dir)
    dispatcher = _load_dispatcher()
    output = dispatcher._emit_diagnose_summary(state_dir, root)
    assert "Worker process-family liveness" in output
    assert "ABSENT" in output


def test_diagnose_summary_liveness_section_shows_counters(tmp_path: Path) -> None:
    """When heartbeat present, diagnose shows codex/family/threshold counters."""
    root = _make_synthetic_project(tmp_path)
    _write_heartbeat(root, "2026-06-23T00:00:00+00:00 codex=3 family=7 threshold=15\n")
    state_dir = tmp_path / "state"
    _write_dispatch_state(state_dir)
    dispatcher = _load_dispatcher()
    output = dispatcher._emit_diagnose_summary(state_dir, root)
    assert "Worker process-family liveness" in output
    assert "codex=3" in output
    assert "family=7" in output
    assert "threshold=15" in output


def test_diagnose_summary_false_idle_warning_emitted(tmp_path: Path) -> None:
    """WARNING emitted when dispatch shows no change but family>1 (processes active)."""
    root = _make_synthetic_project(tmp_path)
    # family=5 means worker processes are running despite idle dispatch state
    _write_heartbeat(root, "2026-06-23T00:00:00+00:00 codex=0 family=5 threshold=15\n")
    state_dir = tmp_path / "state"
    _write_dispatch_state(state_dir, pb_result="no_actionable_change", lo_result="no_actionable_change")
    dispatcher = _load_dispatcher()
    output = dispatcher._emit_diagnose_summary(state_dir, root)
    assert "WARNING" in output
    assert "processes appear active" in output


def test_diagnose_summary_no_false_idle_warning_when_truly_idle(tmp_path: Path) -> None:
    """No WARNING when processes are idle (family<=1, codex=0)."""
    root = _make_synthetic_project(tmp_path)
    _write_heartbeat(root, "2026-06-23T00:00:00+00:00 codex=0 family=1 threshold=15\n")
    state_dir = tmp_path / "state"
    _write_dispatch_state(state_dir, pb_result="no_actionable_change", lo_result="no_actionable_change")
    dispatcher = _load_dispatcher()
    output = dispatcher._emit_diagnose_summary(state_dir, root)
    # Section present but no warning
    assert "Worker process-family liveness" in output
    assert "WARNING" not in output


def _go_fake_item(doc: str) -> object:
    return type(
        "FakeItem",
        (),
        {
            "document_name": doc,
            "top_status": "GO",
            "top_file": f"bridge/{doc}-002.md",
            "dispatchable": True,
        },
    )()


def test_single_harness_issue_dispatch_auth_quarantines_bad_go_and_continues_healthy(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """WI-4770: single-harness dispatcher quarantines one bad GO and continues healthy GO."""
    root = _make_synthetic_project(tmp_path, single_harness=True)
    dispatcher = _load_dispatcher()
    trigger = dispatcher._load_trigger_module()
    state_dir = tmp_path / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
    recorded: list[dict[str, object]] = []

    def _fake_create(_root, bridge_id):
        if bridge_id == "bad-go-thread":
            raise dispatcher.AuthorizationError("missing approved proposal")
        return {
            "bridge_id": bridge_id,
            "packet_hash": f"hash-{bridge_id}",
            "target_path_globs": ["scripts/*.py"],
        }

    def _record_failure(_state_dir, payload):
        recorded.append(payload)

    monkeypatch.setattr(dispatcher, "create_authorization_packet", _fake_create)
    monkeypatch.setattr(dispatcher, "write_named_packet", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(dispatcher, "write_packet", lambda *_args, **_kwargs: root / "auth-current.json")
    monkeypatch.setattr(trigger, "_record_dispatch_failure", _record_failure)

    result = dispatcher._issue_dispatch_authorization_for_selected(
        [_go_fake_item("bad-go-thread"), _go_fake_item("good-go-thread")],
        project_root=root,
        state_dir=state_dir,
        recipient="prime-builder",
        dispatch_id="dispatch-single-harness-auth",
        trigger=trigger,
    )

    assert result["ok"] is True
    assert result["context"]["bridge_ids"] == ["good-go-thread"]
    assert result["quarantined_slugs"] == [{"slug": "bad-go-thread", "error_message": "missing approved proposal"}]
    assert recorded[-1]["document_name"] == "bad-go-thread"
    assert recorded[-1]["reason"] == "impl_auth_quarantined"
