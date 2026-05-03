# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Public-surface coverage for smart-poller bridge-poller doctor checks.

Per ``bridge/gtkb-bridge-poller-doctor-path-2026-05-02-003.md`` (REVISED-1
GO at -004) and ``GOV-19-A1`` (observable-surface coverage requirement),
the spec-counted tests here exercise ``run_doctor(target, profile="dual-agent")``
and inspect the resulting ``DoctorReport.checks`` list. Helper-level edge
cases that are awkward to reach via the public surface are kept as
explicitly-supplemental tests in the ``TestCheckBridgePollerHelperEdgeCases``
class below; per GOV-19-A1 they do not substitute for the public-surface
coverage.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

from groundtruth_kb.project.doctor import (
    ToolCheck,
    _check_bridge_poller,
    run_doctor,
)

_DISPATCH_STATE_REL = Path(".gtkb-state/bridge-poller/dispatch-state.json")


def _iso_seconds_ago(seconds: int) -> str:
    t = datetime.now(tz=UTC) - timedelta(seconds=seconds)
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def _write_dispatch_state(
    target: Path,
    *,
    prime_updated_at: str | None,
    codex_updated_at: str | None,
    prime_last_result: str = "no_pending",
    codex_last_result: str = "no_pending",
    prime_pending_count: int = 0,
    codex_pending_count: int = 0,
    bom_prefix: bool = False,
) -> Path:
    """Write a dispatch-state.json under *target* with the given recipient state.

    A ``None`` ``updated_at`` omits the field entirely. ``bom_prefix=True``
    prepends a UTF-8 BOM to the output, exercising defensive BOM tolerance.
    """
    state_path = target / _DISPATCH_STATE_REL
    state_path.parent.mkdir(parents=True, exist_ok=True)

    def _recipient(updated: str | None, last: str, pending: int) -> dict[str, object]:
        out: dict[str, object] = {
            "last_result": last,
            "pending_count": pending,
            "raw_pending_count": pending,
            "filtered_terminal_count": 0,
            "signature": "test-fixture",
        }
        if updated is not None:
            out["updated_at"] = updated
        return out

    payload = {
        "schema_version": 1,
        "updated_at": _iso_seconds_ago(0),
        "recipients": {
            "prime": _recipient(prime_updated_at, prime_last_result, prime_pending_count),
            "codex": _recipient(codex_updated_at, codex_last_result, codex_pending_count),
        },
    }
    text = json.dumps(payload)
    if bom_prefix:
        state_path.write_bytes(b"\xef\xbb\xbf" + text.encode("utf-8"))
    else:
        state_path.write_text(text, encoding="utf-8")
    return state_path


def _bridge_poller_checks(target: Path) -> dict[str, ToolCheck]:
    """Run ``run_doctor`` and return the per-agent bridge-poller checks by name."""
    report = run_doctor(target, "dual-agent")
    return {
        check.name: check
        for check in report.checks
        if check.name in ("Claude bridge poller", "Codex bridge poller")
    }


# ============================================================================
# Primary tests (public ``run_doctor`` surface — GOV-19-A1 spec coverage)
# ============================================================================


def test_run_doctor_reports_pass_for_both_agents_when_fresh(tmp_path: Path) -> None:
    """TP1: both per-agent bridge-poller checks PASS in DoctorReport when fresh.

    Spec/behavior: bridge-essential.md §"Poller Enablement Contract" condition 3.
    """
    _write_dispatch_state(
        tmp_path,
        prime_updated_at=_iso_seconds_ago(60),
        codex_updated_at=_iso_seconds_ago(60),
    )
    checks = _bridge_poller_checks(tmp_path)
    assert checks["Claude bridge poller"].status == "pass"
    assert checks["Codex bridge poller"].status == "pass"
    assert "OK" in checks["Claude bridge poller"].message
    assert "OK" in checks["Codex bridge poller"].message


def test_run_doctor_reports_warning_when_4_to_10_min_old(tmp_path: Path) -> None:
    """TP2: both per-agent bridge-poller checks WARN at 5 min stale via public surface."""
    _write_dispatch_state(
        tmp_path,
        prime_updated_at=_iso_seconds_ago(5 * 60 + 30),
        codex_updated_at=_iso_seconds_ago(5 * 60 + 30),
    )
    checks = _bridge_poller_checks(tmp_path)
    assert checks["Claude bridge poller"].status == "warning"
    assert checks["Codex bridge poller"].status == "warning"
    assert "WARN" in checks["Claude bridge poller"].message
    assert "WARN" in checks["Codex bridge poller"].message


def test_run_doctor_reports_fail_when_over_10_min_old(tmp_path: Path) -> None:
    """TP3: both per-agent bridge-poller checks FAIL at 15 min stale via public surface."""
    _write_dispatch_state(
        tmp_path,
        prime_updated_at=_iso_seconds_ago(15 * 60),
        codex_updated_at=_iso_seconds_ago(15 * 60),
    )
    checks = _bridge_poller_checks(tmp_path)
    assert checks["Claude bridge poller"].status == "fail"
    assert checks["Codex bridge poller"].status == "fail"
    assert "ALARM" in checks["Claude bridge poller"].message
    assert "ALARM" in checks["Codex bridge poller"].message


def test_run_doctor_reports_warning_when_state_file_absent(tmp_path: Path) -> None:
    """TP4: empty target dir → both per-agent checks WARN (not started) via public surface."""
    checks = _bridge_poller_checks(tmp_path)
    assert checks["Claude bridge poller"].status == "warning"
    assert checks["Codex bridge poller"].status == "warning"
    assert "not started" in checks["Claude bridge poller"].message.lower()
    assert "not started" in checks["Codex bridge poller"].message.lower()


def test_run_doctor_handles_utf8_bom_in_state_file_gracefully(tmp_path: Path) -> None:
    """TP5: BOM-prefixed valid JSON parses cleanly through public surface (defensive)."""
    _write_dispatch_state(
        tmp_path,
        prime_updated_at=_iso_seconds_ago(60),
        codex_updated_at=_iso_seconds_ago(60),
        bom_prefix=True,
    )
    checks = _bridge_poller_checks(tmp_path)
    assert checks["Claude bridge poller"].status == "pass"
    assert checks["Codex bridge poller"].status == "pass"


def test_run_doctor_message_includes_pending_count(tmp_path: Path) -> None:
    """TP6: public report message surfaces pending_count for operator visibility."""
    _write_dispatch_state(
        tmp_path,
        prime_updated_at=_iso_seconds_ago(60),
        codex_updated_at=_iso_seconds_ago(60),
        prime_pending_count=21,
        codex_pending_count=0,
    )
    checks = _bridge_poller_checks(tmp_path)
    assert "pending: 21" in checks["Claude bridge poller"].message
    assert "pending: 0" in checks["Codex bridge poller"].message


def test_run_doctor_distinguishes_claude_from_codex_recipients_in_report(tmp_path: Path) -> None:
    """TP7: agent mapping (claude→prime, codex→codex) visible in public report.

    Fresh prime, stale codex → Claude check PASS, Codex check FAIL.
    """
    _write_dispatch_state(
        tmp_path,
        prime_updated_at=_iso_seconds_ago(60),
        codex_updated_at=_iso_seconds_ago(15 * 60),
    )
    checks = _bridge_poller_checks(tmp_path)
    assert checks["Claude bridge poller"].status == "pass"
    assert checks["Codex bridge poller"].status == "fail"


# ============================================================================
# Supplemental helper-level coverage (NOT spec coverage per GOV-19-A1)
# ============================================================================


class TestCheckBridgePollerHelperEdgeCases:
    """Helper-level edge cases. Per ``GOV-19-A1`` these are supplemental and
    do NOT substitute for the public-surface tests (TP1-TP7) above."""

    def test_ts1_returns_fail_when_recipients_key_missing(self, tmp_path: Path) -> None:
        state_path = tmp_path / _DISPATCH_STATE_REL
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(json.dumps({"schema_version": 1}), encoding="utf-8")
        result = _check_bridge_poller(tmp_path, "claude")
        assert result.status == "fail"
        assert "recipients" in result.message

    def test_ts2_returns_fail_when_role_key_missing(self, tmp_path: Path) -> None:
        state_path = tmp_path / _DISPATCH_STATE_REL
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "recipients": {
                        "codex": {
                            "updated_at": _iso_seconds_ago(0),
                            "last_result": "no_pending",
                            "pending_count": 0,
                        }
                    },
                }
            ),
            encoding="utf-8",
        )
        result = _check_bridge_poller(tmp_path, "claude")
        assert result.status == "fail"
        assert "prime" in result.message

    def test_ts3_returns_fail_when_updated_at_unparseable(self, tmp_path: Path) -> None:
        state_path = tmp_path / _DISPATCH_STATE_REL
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "recipients": {
                        "prime": {
                            "updated_at": "not-an-iso-timestamp",
                            "last_result": "no_pending",
                            "pending_count": 0,
                        },
                        "codex": {
                            "updated_at": _iso_seconds_ago(0),
                            "last_result": "no_pending",
                            "pending_count": 0,
                        },
                    },
                }
            ),
            encoding="utf-8",
        )
        result = _check_bridge_poller(tmp_path, "claude")
        assert result.status == "fail"
        assert "unparseable" in result.message
