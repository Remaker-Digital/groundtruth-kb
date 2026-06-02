# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for per-document leasing in cross-harness bridge trigger.

Verifies SPEC-INTAKE-57a736 Clauses 1, 2, 3, and 4.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# Ensure repo root scripts/ and platform_tests/scripts/ are on sys.path
_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPTS_DIR = str(_REPO_ROOT / "scripts")
_TESTS_DIR = str(_REPO_ROOT / "platform_tests" / "scripts")
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)
if _TESTS_DIR not in sys.path:
    sys.path.insert(0, _TESTS_DIR)

from bridge_lease_registry import (  # noqa: E402
    acquire_lease,
    is_lease_held,
    release_lease,
)
from test_cross_harness_bridge_trigger import (  # noqa: E402
    _CLAUDE_INVOCATION_SURFACES,
    _load_trigger,
    _make_synthetic_project,
    _write_bridge_file,
    _write_index,
)


def test_active_lease_on_x_does_not_suppress_y(tmp_path: Path) -> None:
    """T-LEASE-active-lease-on-x-does-not-suppress-y: lease on document X does NOT suppress dispatch of document Y."""
    root = _make_synthetic_project(tmp_path)
    state_dir = tmp_path / "state"
    state_dir.mkdir(parents=True, exist_ok=True)

    # 1. Setup INDEX.md with two NEW items (actionable for Codex / loyal-opposition)
    _write_bridge_file(root, "example-x-001.md", "bridge_kind: implementation_proposal\n")
    _write_bridge_file(root, "example-y-001.md", "bridge_kind: implementation_proposal\n")

    index_body = (
        "# bridge index\n\n"
        "Document: example-x\n"
        "NEW: bridge/example-x-001.md\n\n"
        "Document: example-y\n"
        "NEW: bridge/example-y-001.md\n"
    )
    _write_index(root, index_body)

    # 2. Acquire a lease on X
    lease_handle = acquire_lease("example-x", action="test-harness", state_dir=state_dir)
    assert lease_handle is not None
    assert is_lease_held("example-x", state_dir=state_dir)
    assert not is_lease_held("example-y", state_dir=state_dir)

    # 3. Run trigger - should dispatch only Y
    trigger = _load_trigger()
    summary = trigger.run_trigger(project_root=root, state_dir=state_dir, max_items=2, dry_run=True)

    # Since example-y is unleased, it must be dispatched (which in dry_run returns "dry_run" reason)
    results = summary["results"]
    assert results["loyal-opposition"]["reason"] == "dry_run"

    # Verify that only example-y was selected and signed
    rec = summary["dispatch_state"]["recipients"]["loyal-opposition"]
    assert rec["selected_count"] == 1

    # The signature must correspond to only example-y
    from groundtruth_kb.bridge.detector import parse_index
    from groundtruth_kb.bridge.notify import compute_actionable_pending

    parse_result = parse_index(index_body, project_root=root)
    _, codex_items = compute_actionable_pending(parse_result, project_root=root)
    # Filter to only example-y
    unleased_items = [it for it in codex_items if it.document_name == "example-y"]
    expected_sig = trigger._signature(trigger._selected_oldest_first(unleased_items, 2))

    assert rec["signature"] == expected_sig

    # Release the lease
    release_lease(lease_handle)


def test_second_worker_refused_lease_on_same_document(tmp_path: Path) -> None:
    """T-LEASE-second-worker-refused-lease: a second worker is refused a lease on the same document while held."""
    state_dir = tmp_path / "state"
    state_dir.mkdir(parents=True, exist_ok=True)

    # 1. First worker acquires lease
    handle1 = acquire_lease("example-x", action="worker1", state_dir=state_dir)
    assert handle1 is not None

    # 2. Second worker attempts to acquire same lease - should be refused
    handle2 = acquire_lease("example-x", action="worker2", state_dir=state_dir)
    assert handle2 is None

    # Clean up
    release_lease(handle1)


def test_stale_lease_is_reclaimed(tmp_path: Path) -> None:
    """T-LEASE-stale-lease-reclaimed: a stale lease is reclaimable and retried successfully."""
    state_dir = tmp_path / "state"
    state_dir.mkdir(parents=True, exist_ok=True)

    # 1. Manually write a stale lease file
    leases_dir = state_dir / "leases"
    leases_dir.mkdir(parents=True, exist_ok=True)
    lease_file = leases_dir / "example-x.lock"

    stale_payload = {
        "schema_version": 1,
        "doc_slug": "example-x",
        "lease_token": "stale-token-123",
        "pid": 9999,
        "acquired_at": "2026-05-30T00:00:00Z",
        "heartbeat_at": "2026-05-30T00:00:00Z",
        "action": "stale-worker",
        "ttl_seconds": 10,
    }
    lease_file.write_text(json.dumps(stale_payload), encoding="utf-8")

    # Verify that the lease is currently reported as not held (since it's stale)
    assert not is_lease_held("example-x", state_dir=state_dir)

    # 2. Try to acquire lease - should successfully reclaim and return a new handle
    handle = acquire_lease("example-x", action="new-worker", state_dir=state_dir)
    assert handle is not None
    assert handle.lease_token != "stale-token-123"
    assert is_lease_held("example-x", state_dir=state_dir)

    # Clean up
    release_lease(handle)


def test_dispatch_uses_lease_not_harness_lock(tmp_path: Path) -> None:
    """T-LEASE-dispatch-uses-lease-not-harness-lock: trigger dispatch does not consult check_target_active lock."""
    root = _make_synthetic_project(tmp_path)
    state_dir = tmp_path / "state"
    state_dir.mkdir(parents=True, exist_ok=True)

    # 1. Setup INDEX.md with one NEW item
    _write_bridge_file(root, "example-x-001.md", "bridge_kind: implementation_proposal\n")
    _write_index(root, "# bridge index\n\nDocument: example-x\nNEW: bridge/example-x-001.md\n")

    # 2. Write a fresh target active-session lock file.
    # This would normally trigger target-active suppression.
    lock_path = state_dir / "active-claude-session.lock"
    lock_payload = {"opened_at": "2026-06-01T00:00:00Z", "last_refreshed": "2026-06-01T00:00:00Z"}
    lock_path.write_text(json.dumps(lock_payload), encoding="utf-8")
    os.utime(lock_path, None)  # Set mtime to now so it is fresh

    # Verify that the target-active logic reports True (if called).
    trigger = _load_trigger()
    lo_target = trigger.DispatchTarget(
        needed_role_label="loyal-opposition",
        harness_id="A",
        command_handle="claude",
        canonical_mode="lo",
        invocation_surfaces=_CLAUDE_INVOCATION_SURFACES,
    )
    assert trigger.check_target_active(lo_target, state_dir) is True

    # 3. Run trigger - should dispatch normally since no lease file exists for example-x
    summary = trigger.run_trigger(project_root=root, state_dir=state_dir, max_items=2, dry_run=True)
    assert summary["results"]["loyal-opposition"]["reason"] == "dry_run"
