# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""WI-5552 mixed D/F exited-worker lease reconciliation fixture.

The fixture is a deterministic synthetic integration test exercising the
canonical reconciliation seam (``_process_pending_exit_codes``) with two
concurrent launch-ledger entries:

1. one launch carries an authoritative parseable exit sidecar and recorded
   document leases (becomes terminal exactly once; only its leases are
   released exactly once); and
2. one separate launch remains live with a matching live PID and its own
   leases (preserved, never processed as exited).

The exited launch's PID is non-authoritative for live classification because a
status sidecar exists. The fixture uses isolated temporary state and a
monkeypatched lease-release seam; it never starts, stops, configures, or
mutates TAFE, the dispatcher daemon, live workers, live leases, live run
state, or provider state. WI-5208 baseline behavior (committed) already passes
focused tests; this fixture supplies the missing exact WI-5552 mixed-exit
reproducer without authorizing any source modification.
"""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path
from types import ModuleType

import pytest

_SCRIPT_PATH = Path(__file__).resolve().parents[2] / "scripts" / "dispatcher_runtime.py"


def _load_trigger() -> ModuleType:
    """Load scripts/dispatcher_runtime.py with sys.modules registration."""
    assert _SCRIPT_PATH.is_file(), f"Expected trigger at {_SCRIPT_PATH}"
    module_name = "dispatcher_runtime"
    if module_name in sys.modules:
        return sys.modules[module_name]
    spec = importlib.util.spec_from_file_location(module_name, _SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _prime_launch(dispatch_id: str, launched_at: str, document: str) -> dict:
    return {
        "dispatch_id": dispatch_id,
        "recipient": "prime-builder:A",
        "launched": True,
        "launched_at": launched_at,
        "signature": f"signature-{document}",
        "needed_role_label": "prime-builder",
        "selected_documents": [document],
        "document_lease_handles": [{"doc_slug": document}],
    }


def _current_pid_create_time() -> float | None:
    import psutil  # noqa: PLC0415

    try:
        return float(psutil.Process().create_time())
    except Exception:  # pragma: no cover - psutil unavailable
        return None


def test_wi5552_mixed_exit_preserves_live_launch_and_releases_exited_exactly_once(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Two concurrent launches: one exited (terminal, leases released), one live (preserved)."""
    trigger = _load_trigger()
    state_dir = tmp_path / "state"
    runs_dir = state_dir / trigger.DISPATCH_RUNS_SUBDIR
    runs_dir.mkdir(parents=True)

    live_pid = os.getpid()  # alive for the duration of the test
    exited = _prime_launch("exited-launch", "2026-07-12T08:00:00+00:00", "exited-thread")
    live = _prime_launch("live-launch", "2026-07-12T08:01:00+00:00", "live-thread")
    live["pid"] = live_pid
    live["pid_create_time_epoch"] = _current_pid_create_time()
    launches = {
        "exited-launch": exited,
        "live-launch": live,
    }
    # Exited launch carries an authoritative parseable exit sidecar.
    (runs_dir / "exited-launch.exit_code").write_text("0", encoding="utf-8")
    # Live launch has no exit sidecar; its PID is alive, so it is not terminal.
    assert not (runs_dir / "live-launch.exit_code").exists()

    release_calls: list[list[str]] = []

    def _release(records):
        slugs = [record["doc_slug"] for record in records]
        release_calls.append(slugs)
        return slugs

    monkeypatch.setattr(trigger, "_release_document_lease_records", _release)
    recipients = {
        "prime-builder:A": {
            trigger.LAUNCH_LEDGER_KEY: launches,
            "failure_count": 0,
        }
    }

    # Canonical reconciliation seam; run twice to prove idempotence.
    trigger._process_pending_exit_codes(recipients, state_dir, tmp_path)
    trigger._process_pending_exit_codes(recipients, state_dir, tmp_path)

    state = recipients["prime-builder:A"]
    ledger = state[trigger.LAUNCH_LEDGER_KEY]
    # Exited launch becomes terminal exactly once and its leases released once.
    assert ledger["exited-launch"]["exit_code_processed"] is True
    assert ledger["exited-launch"]["document_leases_released_on_exit"] == ["exited-thread"]
    # Live launch is preserved: still active, leases intact.
    assert ledger["live-launch"].get("exit_code_processed") is not True
    assert "document_leases_released_on_exit" not in ledger["live-launch"]
    # Counts converge.
    assert state["launch_ledger_active_count"] == 1
    assert state["launch_ledger_completed_count"] == 1
    # Only the exited launch's leases are released, exactly once.
    assert release_calls == [["exited-thread"]]
