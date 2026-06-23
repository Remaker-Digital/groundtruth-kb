# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""WI-4396: expected lease-contention suppressions are routed out of
``dispatch-failures.jsonl`` into the sibling ``dispatch-suppressions.jsonl``
audit log.

A last-24h analysis found 1,997 ``work_intent_already_held`` rows polluting the
failure log versus 233 real ``implementation_authorization_packet_failed`` rows,
burying actionable failures in the dispatch ``diagnose`` "Recent failures" view.
The fix routes expected, non-actionable lease/contention suppressions by
``reason`` at the single shared writer ``_record_dispatch_failure`` so both
dispatch substrates (the cross-harness trigger and the single-harness
dispatcher, which reuses the same writer) are covered with no call-site changes.

Authority: bridge ``gtkb-wi4396-dispatch-suppression-routing`` GO at ``-004``.

Specs:
- GOV-STANDING-BACKLOG-001 (WI-4396 backlog authority)
- .claude/rules/bridge-essential.md § "Dual-Substrate Coexistence"
  (fire-and-forget audit-log discipline preserved for both files)
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import cross_harness_bridge_trigger as cht  # noqa: E402

FAILURES = "dispatch-failures.jsonl"
SUPPRESSIONS = "dispatch-suppressions.jsonl"


def _records(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_work_intent_held_routed_to_suppressions(tmp_path: Path) -> None:
    """Acceptance criterion #1 (WI-4396 root): a ``work_intent_already_held``
    record routed through the shared writer lands in dispatch-suppressions.jsonl
    and is ABSENT from dispatch-failures.jsonl."""
    state_dir = tmp_path / "state"
    cht._record_dispatch_failure(
        state_dir,
        {"ts": "2026-06-14T10:00:00+00:00", "reason": "work_intent_already_held", "launched": False},
    )

    suppressions = _records(state_dir / SUPPRESSIONS)
    assert len(suppressions) == 1
    assert suppressions[0]["reason"] == "work_intent_already_held"
    assert _records(state_dir / FAILURES) == []


def test_real_failure_stays_in_failures(tmp_path: Path) -> None:
    """Acceptance criterion #2: real, actionable failure reasons still go to
    dispatch-failures.jsonl (no false routing). Covers both a hook/packet
    failure and a work-intent registry error (a ``launched: False`` record that
    is NOT an expected suppression — routing is by reason, not by ``launched``)."""
    state_dir = tmp_path / "state"
    cht._record_dispatch_failure(
        state_dir,
        {
            "ts": "2026-06-14T10:00:00+00:00",
            "reason": "implementation_authorization_packet_failed",
            "launched": False,
        },
    )
    cht._record_dispatch_failure(
        state_dir,
        {
            "ts": "2026-06-14T10:01:00+00:00",
            "reason": "work_intent_registry_error",
            "launched": False,
        },
    )

    failures = _records(state_dir / FAILURES)
    failure_reasons = {rec.get("reason") for rec in failures}
    assert failure_reasons == {"implementation_authorization_packet_failed", "work_intent_registry_error"}
    assert _records(state_dir / SUPPRESSIONS) == []


def test_single_harness_dispatcher_uses_shared_chokepoint() -> None:
    """Acceptance criterion #3: the single-harness dispatcher REUSES
    ``trigger._record_dispatch_failure`` (no independent failure/suppression
    writer of its own), so the reason-based routing applies to both substrates.

    Verified by source inspection: the dispatcher calls
    ``trigger._record_dispatch_failure(`` and defines neither
    ``_record_dispatch_failure`` nor ``_record_dispatch_suppression``."""
    dispatcher_src = (REPO_ROOT / "scripts" / "single_harness_bridge_dispatcher.py").read_text(encoding="utf-8")
    assert "trigger._record_dispatch_failure(" in dispatcher_src
    assert "def _record_dispatch_failure(" not in dispatcher_src
    assert "def _record_dispatch_suppression(" not in dispatcher_src

    # The shared writer is the canonical routing point; confirm the routing
    # constant + helper it depends on exist on the trigger module the dispatcher
    # imports.
    assert "work_intent_already_held" in cht.EXPECTED_SUPPRESSION_REASONS
    assert hasattr(cht, "_record_dispatch_suppression")


def test_suppressions_file_rotates(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Acceptance criterion #4: dispatch-suppressions.jsonl honors the same
    rotation discipline as the failures log."""
    state_dir = tmp_path / "state"
    monkeypatch.setenv(cht.DISPATCH_SUPPRESSIONS_MAX_BYTES_ENV_VAR, "1")

    for i in range(3):
        cht._record_dispatch_failure(
            state_dir,
            {"ts": f"2026-06-14T10:0{i}:00+00:00", "reason": "work_intent_already_held", "launched": False},
        )

    # With a 1-byte threshold, each subsequent write rotates the current file to
    # ``.1`` before appending — so a rollover file must exist.
    assert (state_dir / f"{SUPPRESSIONS}.1").is_file()
    assert (state_dir / SUPPRESSIONS).is_file()
    # The failures log must not have been touched.
    assert not (state_dir / FAILURES).is_file()


def test_suppression_write_failsafe(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Acceptance criterion #6: fire-and-forget — a suppressions-write error
    never propagates out of the shared writer (dispatch must not break on an
    instrumentation I/O failure)."""
    state_dir = tmp_path / "state"

    def _boom(*args: object, **kwargs: object) -> None:
        raise OSError("simulated unwritable state-dir")

    # Force the suppressions write path to fail at mkdir; the writer must swallow it.
    monkeypatch.setattr(cht.Path, "mkdir", _boom)
    # Must not raise.
    cht._record_dispatch_failure(
        state_dir,
        {"ts": "2026-06-14T10:00:00+00:00", "reason": "work_intent_already_held", "launched": False},
    )
    assert not (state_dir / SUPPRESSIONS).is_file()
    # A tiny touch to ensure the file is considered dirty for finalization.
