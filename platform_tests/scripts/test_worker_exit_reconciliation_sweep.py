# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Focused tests for WI-6037 Slice 1: worker-exit reconciliation sweep.

Every test runs against a ``tmp_path`` fixture root; none reads or mutates live
repository state, and none depends on an ambient harness session-id env var.
"""

from __future__ import annotations

import json
import subprocess
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from scripts.worker_exit_reconciliation_sweep import (
    collect_candidates,
    render_summary,
    run_sweep,
)

NOW = datetime(2026, 8, 8, 12, 0, 0, tzinfo=UTC)
EXPIRED = (NOW - timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
LIVE = (NOW + timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%SZ")


def _write(path: Path, payload: dict[str, object]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _seed(root: Path) -> dict[str, Path]:
    """Seed one expired and one live record of each expiry-bearing class."""

    return {
        "expired_claim": _write(
            root / ".gtkb-state" / "work-intent" / "gtkb-dead-thread.json",
            {"session_id": "dead", "ttl_expires_at": EXPIRED},
        ),
        "live_claim": _write(
            root / ".gtkb-state" / "work-intent" / "gtkb-live-thread.json",
            {"session_id": "live", "ttl_expires_at": LIVE},
        ),
        "expired_packet": _write(
            root / ".gtkb-state" / "implementation-authorizations" / "gtkb-dead-packet.json",
            {"bridge_id": "gtkb-dead", "expires_at": EXPIRED},
        ),
        "live_packet": _write(
            root / ".gtkb-state" / "implementation-authorizations" / "gtkb-live-packet.json",
            {"bridge_id": "gtkb-live", "expires_at": LIVE},
        ),
        "pointer": _write(
            root / ".gtkb-state" / "implementation-authorizations" / "current.json",
            {"bridge_id": "gtkb-live", "expires_at": EXPIRED},
        ),
    }


def _seed_bridge(root: Path) -> Path:
    target = root / "bridge" / "gtkb-some-thread-001.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("NEW\n\n# proposal\n", encoding="utf-8")
    return target


# --- GOV-SOURCE-OF-TRUTH-FRESHNESS-001 -------------------------------------------------


def test_expired_claim_and_packet_are_enumerated(tmp_path: Path) -> None:
    """Expired records of both expiry-bearing classes are reported as reclaimable."""

    _seed(tmp_path)
    expired = {c.path for c in collect_candidates(tmp_path, now=NOW) if c.expired}
    assert ".gtkb-state/work-intent/gtkb-dead-thread.json" in expired
    assert ".gtkb-state/implementation-authorizations/gtkb-dead-packet.json" in expired


# --- PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001 -------------------------------------


def test_live_records_are_never_reclaimed(tmp_path: Path) -> None:
    """Invariant 2: a record still live by its own recorded TTL is never touched."""

    seeded = _seed(tmp_path)
    result = run_sweep(tmp_path, apply=True, now=NOW)
    assert seeded["live_claim"].exists()
    assert seeded["live_packet"].exists()
    assert ".gtkb-state/work-intent/gtkb-live-thread.json" not in result.reclaimed
    assert ".gtkb-state/implementation-authorizations/gtkb-live-packet.json" not in result.reclaimed


def test_reclaim_never_creates_or_edits_a_packet(tmp_path: Path) -> None:
    """Reclamation only removes; it never mints or rewrites authorization evidence."""

    seeded = _seed(tmp_path)
    live_before = seeded["live_packet"].read_bytes()
    packets_before = {p.name for p in (tmp_path / ".gtkb-state" / "implementation-authorizations").iterdir()}

    run_sweep(tmp_path, apply=True, now=NOW)

    packets_after = {p.name for p in (tmp_path / ".gtkb-state" / "implementation-authorizations").iterdir()}
    assert packets_after <= packets_before, "reclamation must never create a packet"
    assert seeded["live_packet"].read_bytes() == live_before, "reclamation must never edit a packet"


def test_pointer_file_is_never_reclaimed(tmp_path: Path) -> None:
    """current.json is state rewritten by the next begin, not a reclaimable record."""

    seeded = _seed(tmp_path)
    run_sweep(tmp_path, apply=True, now=NOW)
    assert seeded["pointer"].exists()


# --- GOV-FILE-BRIDGE-AUTHORITY-001 -----------------------------------------------------


def test_bridge_audit_trail_is_untouched(tmp_path: Path) -> None:
    """Invariant 3: no bridge file is deleted, rewritten, or moved."""

    _seed(tmp_path)
    bridge_file = _seed_bridge(tmp_path)
    before_bytes = bridge_file.read_bytes()
    before_mtime = bridge_file.stat().st_mtime

    run_sweep(tmp_path, apply=True, now=NOW)

    assert bridge_file.exists()
    assert bridge_file.read_bytes() == before_bytes
    assert bridge_file.stat().st_mtime == before_mtime


def test_no_git_subprocess_is_invoked(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Invariant 4: the sweep performs no git operation."""

    _seed(tmp_path)
    _seed_bridge(tmp_path)

    def _explode(*args: object, **kwargs: object) -> None:
        raise AssertionError("sweep must not invoke any subprocess")

    monkeypatch.setattr(subprocess, "run", _explode)
    monkeypatch.setattr(subprocess, "Popen", _explode)
    monkeypatch.setattr(subprocess, "check_output", _explode)

    run_sweep(tmp_path, apply=True, now=NOW)


# --- Invariant 1: report-only by default -----------------------------------------------


def test_bare_run_mutates_nothing(tmp_path: Path) -> None:
    """A bare invocation with expired residue present is side-effect free."""

    seeded = _seed(tmp_path)
    result = run_sweep(tmp_path, now=NOW)

    assert result.applied is False
    assert result.reclaimed == []
    assert seeded["expired_claim"].exists()
    assert seeded["expired_packet"].exists()
    assert any(c.expired for c in result.candidates), "fixture must contain reclaimable residue"


# --- Invariant 5: idempotence ----------------------------------------------------------


def test_second_apply_reclaims_nothing(tmp_path: Path) -> None:
    _seed(tmp_path)
    first = run_sweep(tmp_path, apply=True, now=NOW)
    second = run_sweep(tmp_path, apply=True, now=NOW)

    assert first.reclaimed, "first apply must reclaim the seeded expired records"
    assert second.reclaimed == []


# --- Invariant 6: audit log ------------------------------------------------------------


def test_reclaims_and_skips_are_audit_logged_with_reasons(tmp_path: Path) -> None:
    _seed(tmp_path)
    run_sweep(tmp_path, apply=True, now=NOW)

    log = tmp_path / ".gtkb-state" / "worker-exit-reconciliation" / "sweep.jsonl"
    assert log.is_file()
    entries = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines() if line.strip()]
    actions = {e["action"] for e in entries}
    assert "reclaim" in actions
    assert "skip" in actions
    assert all(e.get("reason") for e in entries), "every audit entry carries a reason"


# --- Invariant 7: fail-soft ------------------------------------------------------------


def test_corrupt_record_is_skipped_not_raised(tmp_path: Path) -> None:
    _seed(tmp_path)
    corrupt = tmp_path / ".gtkb-state" / "implementation-authorizations" / "corrupt.json"
    corrupt.write_text("{ this is not json", encoding="utf-8")

    result = run_sweep(tmp_path, apply=True, now=NOW)

    assert corrupt.exists(), "an unreadable record is not known to be dead; leave it"
    skipped = {c.path for c in result.skipped}
    assert ".gtkb-state/implementation-authorizations/corrupt.json" in skipped


def test_unparseable_expiry_is_not_treated_as_expired(tmp_path: Path) -> None:
    """A record whose expiry cannot be read is not known to be dead (invariant 2)."""

    target = _write(
        tmp_path / ".gtkb-state" / "implementation-authorizations" / "bad-stamp.json",
        {"bridge_id": "gtkb-x", "expires_at": "not-a-timestamp"},
    )
    run_sweep(tmp_path, apply=True, now=NOW)
    assert target.exists()


# --- Surface ---------------------------------------------------------------------------


def test_empty_root_is_clean_and_reports_nothing(tmp_path: Path) -> None:
    result = run_sweep(tmp_path, apply=True, now=NOW)
    assert result.candidates == []
    assert result.reclaimed == []
    assert result.errors == []


def test_render_summary_flags_report_only_mode(tmp_path: Path) -> None:
    _seed(tmp_path)
    summary = render_summary(run_sweep(tmp_path, now=NOW))
    assert "REPORT-ONLY" in summary
    assert "--apply" in summary
