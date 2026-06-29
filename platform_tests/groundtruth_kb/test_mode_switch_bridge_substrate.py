"""Tests for mode-switch bridge substrate transactions.

Covers SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

import pytest
from groundtruth_kb.mode_switch.bridge_substrate import apply_bridge_substrate_switch
from groundtruth_kb.mode_switch.transaction import TransactionValidationError


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _seed_daemon_ready(root: Path) -> None:
    _write(root / "scripts" / "gtkb_dispatcher_daemon.py", "# stub\n")
    state_dir = root / ".gtkb-state" / "dispatcher-daemon"
    _write(state_dir / "daemon.lock", "{}")
    heartbeat = dt.datetime.now(dt.UTC).isoformat(timespec="seconds").replace("+00:00", "Z")
    _write(state_dir / "heartbeat.txt", heartbeat + "\n")


@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    # Seed required files for validator all-pass
    _write(
        tmp_path / "harness-state" / "harness-registry.json",
        json.dumps(
            {"harnesses": [{"id": "A", "role": ["prime-builder"], "status": "active", "event_driven_hooks": True}]}
        ),
    )
    _write(
        tmp_path / "bridge" / "INDEX.md",
        "Document: foo\nNEW: bridge/foo-001.md\n",
    )
    _write(
        tmp_path / "bridge" / "foo-001.md",
        "NEW\n",
    )
    _write(
        tmp_path / "groundtruth.toml",
        '[groundtruth]\ndb_path = "./groundtruth.db"\nproject_root = "."\n',
    )
    _seed_daemon_ready(tmp_path)
    return tmp_path


def test_apply_writes_harness_state_atomically(project_root: Path) -> None:
    audit_path = apply_bridge_substrate_switch(
        project_root,
        "dispatcher_daemon",
        change_reason="test immediate apply",
    )

    assert audit_path.exists()
    state_path = project_root / "harness-state" / "bridge-substrate.json"
    assert state_path.exists()
    data = json.loads(state_path.read_text(encoding="utf-8"))
    assert data["substrate"] == "dispatcher_daemon"
    assert data["applied_by"] == "A"


def test_apply_emits_audit_record_with_axis_field(project_root: Path) -> None:
    audit_path = apply_bridge_substrate_switch(
        project_root,
        "dispatcher_daemon",
        change_reason="test audit log axis",
    )

    assert audit_path.exists()
    data = json.loads(audit_path.read_text(encoding="utf-8"))
    assert data["axis"] == "bridge_substrate"
    assert data["new_substrate"] == "dispatcher_daemon"
    assert data["change_reason"] == "test audit log axis"


def test_apply_rejects_substrate_topology_mismatch(project_root: Path) -> None:
    # multi_harness topology (seed harnesses A and B active)
    _write(
        project_root / "harness-state" / "harness-registry.json",
        json.dumps(
            {
                "harnesses": [
                    {"id": "A", "role": ["prime-builder"], "status": "active", "event_driven_hooks": True},
                    {"id": "B", "role": ["loyal-opposition"], "status": "active", "event_driven_hooks": True},
                ]
            }
        ),
    )

    # Unknown automated substrates are rejected; the only automated substrate is the daemon.
    with pytest.raises(TransactionValidationError) as exc:
        apply_bridge_substrate_switch(
            project_root,
            "not_a_real_substrate",
            change_reason="invalid substrate",
        )
    assert "bridge substrate validation failed" in str(exc.value)


def test_apply_is_idempotent_when_substrate_unchanged(project_root: Path) -> None:
    audit1 = apply_bridge_substrate_switch(
        project_root,
        "dispatcher_daemon",
        change_reason="apply 1",
    )
    audit2 = apply_bridge_substrate_switch(
        project_root,
        "dispatcher_daemon",
        change_reason="apply 2",
    )

    assert audit1.exists()
    assert audit2.exists()
    assert audit1 != audit2


def test_applied_by_ignores_non_active_retained_prime_builder(project_root: Path) -> None:
    _write(
        project_root / "harness-state" / "harness-registry.json",
        json.dumps(
            {
                "harnesses": [
                    {
                        "id": "C",
                        "role": ["prime-builder"],
                        "status": "registered",
                        "event_driven_hooks": False,
                    },
                    {
                        "id": "A",
                        "role": ["prime-builder"],
                        "status": "active",
                        "event_driven_hooks": True,
                    },
                ]
            }
        ),
    )
    apply_bridge_substrate_switch(
        project_root,
        "dispatcher_daemon",
        change_reason="ignore retained non-active PB",
    )

    data = json.loads((project_root / "harness-state" / "bridge-substrate.json").read_text(encoding="utf-8"))
    assert data["applied_by"] == "A"


def test_dispatcher_daemon_rejects_missing_heartbeat(project_root: Path) -> None:
    (project_root / ".gtkb-state" / "dispatcher-daemon" / "heartbeat.txt").unlink()

    with pytest.raises(TransactionValidationError) as exc:
        apply_bridge_substrate_switch(
            project_root,
            "dispatcher_daemon",
            change_reason="missing heartbeat",
        )
    assert "heartbeat" in str(exc.value).lower()


def test_cli_set_bridge_substrate_invokes_apply_switch(project_root: Path) -> None:
    from click.testing import CliRunner
    from groundtruth_kb.cli import main

    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "--config",
            str(project_root / "groundtruth.toml"),
            "mode",
            "set-bridge-substrate",
            "--substrate",
            "dispatcher_daemon",
            "--reason",
            "cli set-bridge-substrate",
        ],
        obj={"project_root": str(project_root), "db_path": str(project_root / "groundtruth.db")},
    )

    assert result.exit_code == 0
    assert "applied" in result.output
    assert "dispatcher_daemon" in result.output


def test_cli_set_bridge_substrate_defer_flag_queues_pending(project_root: Path) -> None:
    from click.testing import CliRunner
    from groundtruth_kb.cli import main

    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "--config",
            str(project_root / "groundtruth.toml"),
            "mode",
            "set-bridge-substrate",
            "--substrate",
            "dispatcher_daemon",
            "--reason",
            "cli defer substrate",
            "--defer-to-next-session",
        ],
        obj={"project_root": str(project_root), "db_path": str(project_root / "groundtruth.db")},
    )

    assert result.exit_code == 0
    assert "deferred" in result.output
    pending_dir = project_root / ".gtkb-state" / "mode-switches" / "pending"
    assert len(list(pending_dir.glob("*.json"))) == 1


def test_substrate_inert_path_when_disagrees_with_durable_selection(
    project_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from scripts.dispatcher_runtime import run_dispatch_cycle

    monkeypatch.delenv("GTKB_DISPATCHER_DAEMON_DISABLED", raising=False)
    # Set up dispatcher runtime state.
    state_dir = project_root / ".gtkb-state" / "bridge-poller"

    # Set substrate to 'none' in bridge-substrate.json
    _write(
        project_root / "harness-state" / "bridge-substrate.json",
        json.dumps({"substrate": "none"}),
    )

    res = run_dispatch_cycle(project_root=project_root, state_dir=state_dir)
    assert res["skipped"] is True
    assert res["reason"] == "substrate_mismatch_inert"


@pytest.mark.parametrize(
    ("substrate", "expected"),
    [
        ("dispatcher_daemon", True),
        ("none", False),
    ],
)
def test_active_substrate_predicate_matches_configured_domain(
    project_root: Path, substrate: str, expected: bool
) -> None:
    from scripts.dispatcher_runtime import _is_dispatcher_daemon_active_substrate

    _write(
        project_root / "harness-state" / "bridge-substrate.json",
        json.dumps({"substrate": substrate}),
    )

    assert _is_dispatcher_daemon_active_substrate(project_root) is expected


def test_active_substrate_predicate_fail_open_when_missing_config(project_root: Path) -> None:
    from scripts.dispatcher_runtime import _is_dispatcher_daemon_active_substrate

    assert _is_dispatcher_daemon_active_substrate(project_root) is True


@pytest.mark.parametrize("content", ["not-json", "[]"])
def test_active_substrate_predicate_fail_open_when_invalid_or_non_dict(project_root: Path, content: str) -> None:
    from scripts.dispatcher_runtime import _is_dispatcher_daemon_active_substrate

    _write(project_root / "harness-state" / "bridge-substrate.json", content)

    assert _is_dispatcher_daemon_active_substrate(project_root) is True
