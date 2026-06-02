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
            },
            {
                "id": "A",
                "harness_name": "codex",
                "harness_type": "codex",
                "status": "active",
                "event_driven_hooks": True,
                "role": ["loyal-opposition"],
            },
        ]
    (harness_state / "harness-registry.json").write_text(
        json.dumps({"schema_version": 1, "harnesses": registry_harnesses}),
        encoding="utf-8",
    )
    return root


def _write_index(root: Path, body: str) -> None:
    (root / "bridge" / "INDEX.md").write_text(body, encoding="utf-8")


def _write_bridge_file(root: Path, name: str) -> None:
    (root / "bridge" / name).write_text("bridge_kind: implementation_proposal\n", encoding="utf-8")


def _write_authorized_go_thread(root: Path, doc: str, target_paths: list[str] | None = None) -> str:
    if target_paths is None:
        target_paths = ["scripts/single_harness_bridge_dispatcher.py"]
    proposal = "\n".join(
        [
            f"# Fixture proposal {doc}",
            "",
            f"target_paths: {json.dumps(target_paths)}",
            "",
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
    _write_bridge_file(root, "example-thread-001.md")
    return "# bridge index\n\nDocument: example-thread\nNEW: bridge/example-thread-001.md\n"


# ──────────────────────────────────────────────────────────────────────────
# T-SHD-S2-multi-harness-noop
# ──────────────────────────────────────────────────────────────────────────


def test_dispatcher_no_op_in_multi_harness_topology(tmp_path: Path) -> None:
    """ADR-SINGLE-HARNESS-OPERATING-MODE-001: substrates mutually exclusive."""
    root = _make_synthetic_project(tmp_path, single_harness=False)
    _write_index(root, _index_with_one_new(root))
    state_dir = tmp_path / "state"

    dispatcher = _load_dispatcher()
    summary = dispatcher.run_dispatcher(project_root=root, state_dir=state_dir, dry_run=True)
    assert summary["skipped"] is True
    assert summary["reason"] == "not_applicable_multi_harness_topology"


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


# ──────────────────────────────────────────────────────────────────────────
# T-SHD-S2-active-session-suppression
# ──────────────────────────────────────────────────────────────────────────


def test_dispatcher_suppresses_on_active_session_lock(tmp_path: Path) -> None:
    """SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001 § Idle Suppression.

    Single-harness topology + fresh active-session lock for the active harness
    -> dispatcher no-ops with reason `foreground_session_active`.
    """
    root = _make_synthetic_project(tmp_path, single_harness=True)
    _write_index(root, _index_with_one_new(root))
    state_dir = tmp_path / "state"
    state_dir.mkdir(parents=True, exist_ok=True)

    # Write a fresh active-session lock for Claude (the harness holding both roles).
    lock_path = state_dir / "active-claude-session.lock"
    lock_path.write_text(json.dumps({"role": "claude"}), encoding="utf-8")

    dispatcher = _load_dispatcher()
    summary = dispatcher.run_dispatcher(project_root=root, state_dir=state_dir, dry_run=True)
    assert summary["skipped"] is True
    assert summary["reason"] == "foreground_session_active"


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
    lines = [l for l in failures_path.read_text(encoding="utf-8").splitlines() if l.strip()]
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

    meta = dispatcher._spawn_worker(
        command_handle="claude",
        needed_role_label="prime-builder",
        target_mode="pb",
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
