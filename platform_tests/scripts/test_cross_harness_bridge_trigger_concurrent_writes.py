# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Concurrent _write_dispatch_state correctness against a shared state dir.

Authority: bridge `gtkb-cross-harness-trigger-windows-rename-race-001` GO at
`-004` (REVISED-1). Codex F1 of -002: tests must cover concurrent calls to
`_write_dispatch_state`, not only direct calls to `_rename_with_retry`.

Specs:
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 v2 (state-write reliability under
  concurrency is foundational to dispatch correctness).
"""
from __future__ import annotations

import json
import sys
import threading
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import cross_harness_bridge_trigger as cht  # noqa: E402


def test_concurrent_write_dispatch_state_no_exceptions(tmp_path: Path) -> None:
    """8 threads × 50 writes against shared state dir → all succeed; final JSON valid."""
    state_dir = tmp_path / "state"
    state_dir.mkdir()

    THREADS = 8
    WRITES_PER_THREAD = 50
    exceptions: list[BaseException] = []

    def worker(thread_id: int) -> None:
        try:
            for i in range(WRITES_PER_THREAD):
                cht._write_dispatch_state(state_dir, {"thread": thread_id, "i": i})
        except BaseException as exc:  # noqa: BLE001 — capture all to assert none
            exceptions.append(exc)

    threads = [threading.Thread(target=worker, args=(t,)) for t in range(THREADS)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert exceptions == [], f"Expected no exceptions, got: {exceptions[:3]}"

    # Final JSON must be valid and one of the written payloads (last writer wins).
    final = json.loads((state_dir / "dispatch-state.json").read_text(encoding="utf-8"))
    assert isinstance(final, dict)
    assert "thread" in final and "i" in final
    assert 0 <= final["thread"] < THREADS
    assert 0 <= final["i"] < WRITES_PER_THREAD


def test_concurrent_write_dispatch_state_no_orphan_temps(tmp_path: Path) -> None:
    """After concurrent writes complete, no `*.tmp` orphans remain in state_dir."""
    state_dir = tmp_path / "state"
    state_dir.mkdir()

    THREADS = 4
    WRITES_PER_THREAD = 25

    def worker(thread_id: int) -> None:
        for i in range(WRITES_PER_THREAD):
            cht._write_dispatch_state(state_dir, {"thread": thread_id, "i": i})

    threads = [threading.Thread(target=worker, args=(t,)) for t in range(THREADS)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    orphans = list(state_dir.glob("*.tmp"))
    assert orphans == [], f"Orphan temps remain: {orphans}"
