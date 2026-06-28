# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Public-surface coverage for bridge dispatch liveness doctor checks.

Per ``bridge/gtkb-bridge-poller-doctor-path-2026-05-02-003.md`` (REVISED-1
GO at -004) and ``GOV-19-A1`` (observable-surface coverage requirement),
the spec-counted tests here exercise ``run_doctor(target, profile="dual-agent")``
and inspect the resulting ``DoctorReport.checks`` list. Helper-level edge
cases that are awkward to reach via the public surface are kept as
explicitly-supplemental tests in the ``TestCheckBridgeDispatchHelperEdgeCases``
class below; per GOV-19-A1 they do not substitute for the public-surface
coverage.

Slice 4 (2026-05-09): the function under test was renamed from
``_check_bridge_poller`` to ``_check_bridge_dispatch_liveness`` after the
smart-poller mechanism was retired in favor of the cross-harness
event-driven trigger. The check is mechanism-agnostic — it surfaces
dispatch freshness regardless of which mechanism updates the state file.
The check name is now ``Claude bridge dispatch`` / ``Codex bridge dispatch``.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

from groundtruth_kb.project.doctor import (
    _BRIDGE_DISPATCH_DOC,
    ToolCheck,
    _check_bridge_dispatch_liveness,
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
            "prime-builder": _recipient(prime_updated_at, prime_last_result, prime_pending_count),
            "loyal-opposition": _recipient(codex_updated_at, codex_last_result, codex_pending_count),
        },
    }
    text = json.dumps(payload)
    if bom_prefix:
        state_path.write_bytes(b"\xef\xbb\xbf" + text.encode("utf-8"))
    else:
        state_path.write_text(text, encoding="utf-8")
    return state_path


def _bridge_dispatch_checks(target: Path) -> dict[str, ToolCheck]:
    """Run ``run_doctor`` and return the per-agent bridge-dispatch checks by name."""
    report = run_doctor(target, "dual-agent")
    return {
        check.name: check
        for check in report.checks
        if check.name in ("Claude bridge dispatch", "Codex bridge dispatch")
    }


# ============================================================================
# Primary tests (public ``run_doctor`` surface — GOV-19-A1 spec coverage)
# ============================================================================


def test_run_doctor_reports_pass_for_both_agents_when_fresh(tmp_path: Path) -> None:
    """TP1: both per-agent bridge-dispatch checks PASS in DoctorReport when fresh.

    Spec/behavior: bridge-essential.md §"Poller Enablement Contract" condition 3.
    """
    _write_dispatch_state(
        tmp_path,
        prime_updated_at=_iso_seconds_ago(60),
        codex_updated_at=_iso_seconds_ago(60),
    )
    checks = _bridge_dispatch_checks(tmp_path)
    assert checks["Claude bridge dispatch"].status == "pass"
    assert checks["Codex bridge dispatch"].status == "pass"
    assert "OK" in checks["Claude bridge dispatch"].message
    assert "OK" in checks["Codex bridge dispatch"].message


def test_run_doctor_reports_warning_when_4_to_10_min_old(tmp_path: Path) -> None:
    """TP2: pending work in both per-agent bridge-dispatch checks WARNs at 5 min stale."""
    _write_dispatch_state(
        tmp_path,
        prime_updated_at=_iso_seconds_ago(5 * 60 + 30),
        codex_updated_at=_iso_seconds_ago(5 * 60 + 30),
        prime_pending_count=1,
        codex_pending_count=1,
    )
    checks = _bridge_dispatch_checks(tmp_path)
    assert checks["Claude bridge dispatch"].status == "warning"
    assert checks["Codex bridge dispatch"].status == "warning"
    assert "WARN" in checks["Claude bridge dispatch"].message
    assert "WARN" in checks["Codex bridge dispatch"].message


def test_run_doctor_reports_fail_when_over_10_min_old(tmp_path: Path) -> None:
    """TP3: pending work in both per-agent bridge-dispatch checks FAILs at 15 min stale."""
    _write_dispatch_state(
        tmp_path,
        prime_updated_at=_iso_seconds_ago(15 * 60),
        codex_updated_at=_iso_seconds_ago(15 * 60),
        prime_pending_count=1,
        codex_pending_count=1,
    )
    checks = _bridge_dispatch_checks(tmp_path)
    assert checks["Claude bridge dispatch"].status == "fail"
    assert checks["Codex bridge dispatch"].status == "fail"
    assert "ALARM" in checks["Claude bridge dispatch"].message
    assert "ALARM" in checks["Codex bridge dispatch"].message


def test_run_doctor_reports_warning_when_state_file_absent(tmp_path: Path) -> None:
    """TP4: empty target dir → both per-agent checks WARN (not started) via public surface."""
    checks = _bridge_dispatch_checks(tmp_path)
    assert checks["Claude bridge dispatch"].status == "warning"
    assert checks["Codex bridge dispatch"].status == "warning"
    assert "not started" in checks["Claude bridge dispatch"].message.lower()
    assert "not started" in checks["Codex bridge dispatch"].message.lower()


def test_run_doctor_passes_stale_empty_queue_when_top_level_dispatch_state_is_fresh(tmp_path: Path) -> None:
    """TP4b: stale empty recipient rows are non-failing when the dispatch-state heartbeat is fresh."""
    _write_dispatch_state(
        tmp_path,
        prime_updated_at=_iso_seconds_ago(15 * 60),
        codex_updated_at=_iso_seconds_ago(15 * 60),
        prime_pending_count=0,
        codex_pending_count=0,
    )
    checks = _bridge_dispatch_checks(tmp_path)
    assert checks["Claude bridge dispatch"].status == "pass"
    assert checks["Codex bridge dispatch"].status == "pass"
    assert "empty queue idle" in checks["Claude bridge dispatch"].message
    assert "empty queue idle" in checks["Codex bridge dispatch"].message


def test_run_doctor_handles_utf8_bom_in_state_file_gracefully(tmp_path: Path) -> None:
    """TP5: BOM-prefixed valid JSON parses cleanly through public surface (defensive)."""
    _write_dispatch_state(
        tmp_path,
        prime_updated_at=_iso_seconds_ago(60),
        codex_updated_at=_iso_seconds_ago(60),
        bom_prefix=True,
    )
    checks = _bridge_dispatch_checks(tmp_path)
    assert checks["Claude bridge dispatch"].status == "pass"
    assert checks["Codex bridge dispatch"].status == "pass"


def test_run_doctor_message_includes_pending_count(tmp_path: Path) -> None:
    """TP6: public report message surfaces pending_count for operator visibility."""
    _write_dispatch_state(
        tmp_path,
        prime_updated_at=_iso_seconds_ago(60),
        codex_updated_at=_iso_seconds_ago(60),
        prime_pending_count=21,
        codex_pending_count=0,
    )
    checks = _bridge_dispatch_checks(tmp_path)
    assert "pending: 21" in checks["Claude bridge dispatch"].message
    assert "pending: 0" in checks["Codex bridge dispatch"].message


def test_run_doctor_distinguishes_claude_from_codex_recipients_in_report(tmp_path: Path) -> None:
    """TP7: agent mapping (claude→prime-builder, codex→loyal-opposition) visible in public report.

    Fresh prime-builder, stale loyal-opposition → Claude check PASS, Codex check FAIL.
    """
    _write_dispatch_state(
        tmp_path,
        prime_updated_at=_iso_seconds_ago(60),
        codex_updated_at=_iso_seconds_ago(15 * 60),
        codex_pending_count=1,
    )
    checks = _bridge_dispatch_checks(tmp_path)
    assert checks["Claude bridge dispatch"].status == "pass"
    assert checks["Codex bridge dispatch"].status == "fail"


def test_dispatch_doc_path_exists() -> None:
    """T-4-doctor-dispatch-doc-path-exists (Slice 4 REVISED-7 F1 fix): the
    path referenced by ``_BRIDGE_DISPATCH_DOC`` must resolve to a file in
    the ``groundtruth-kb`` package tree.

    Background: ``-014`` F1 found that ``_BRIDGE_DISPATCH_DOC`` was
    pointing at a non-existent tutorial. REVISED-7 retargeted it to
    ``docs/tutorials/dual-agent-setup.md``, which D5d already brings
    into the slice. This regression test catches future drift where the
    constant points at a path that no longer exists.
    """
    package_root = Path(__file__).resolve().parents[1]
    dispatch_doc = package_root / _BRIDGE_DISPATCH_DOC
    assert dispatch_doc.is_file(), (
        f"_BRIDGE_DISPATCH_DOC points at {_BRIDGE_DISPATCH_DOC!r} which does not "
        f"resolve to an existing file in the groundtruth-kb package tree. "
        f"Resolved path: {dispatch_doc}"
    )


# ============================================================================
# Supplemental helper-level coverage (NOT spec coverage per GOV-19-A1)
# ============================================================================


class TestCheckBridgeDispatchHelperEdgeCases:
    """Helper-level edge cases. Per ``GOV-19-A1`` these are supplemental and
    do NOT substitute for the public-surface tests (TP1-TP7) above."""

    def test_ts1_returns_fail_when_recipients_key_missing(self, tmp_path: Path) -> None:
        state_path = tmp_path / _DISPATCH_STATE_REL
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(json.dumps({"schema_version": 1}), encoding="utf-8")
        result = _check_bridge_dispatch_liveness(tmp_path, "claude")
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
                        "loyal-opposition": {
                            "updated_at": _iso_seconds_ago(0),
                            "last_result": "no_pending",
                            "pending_count": 0,
                        }
                    },
                }
            ),
            encoding="utf-8",
        )
        result = _check_bridge_dispatch_liveness(tmp_path, "claude")
        assert result.status == "fail"
        assert "prime-builder" in result.message

    def test_ts3_returns_fail_when_updated_at_unparseable(self, tmp_path: Path) -> None:
        state_path = tmp_path / _DISPATCH_STATE_REL
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "recipients": {
                        "prime-builder": {
                            "updated_at": "not-an-iso-timestamp",
                            "last_result": "no_pending",
                            "pending_count": 0,
                        },
                        "loyal-opposition": {
                            "updated_at": _iso_seconds_ago(0),
                            "last_result": "no_pending",
                            "pending_count": 0,
                        },
                    },
                }
            ),
            encoding="utf-8",
        )
        result = _check_bridge_dispatch_liveness(tmp_path, "claude")
        assert result.status == "fail"
        assert "unparseable" in result.message


def test_run_doctor_recipient_keys_match_cross_harness_trigger_canonical_labels() -> None:
    """TP8: ensure doctor mapping targets the cross-harness trigger's ROLE_STATE_KEYS."""
    import sys
    from pathlib import Path

    repo_root = Path(__file__).resolve().parents[2]
    scripts_dir = repo_root / "scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))

    import cross_harness_bridge_trigger

    from groundtruth_kb.bridge import role_state
    from groundtruth_kb.project.doctor import _BRIDGE_AGENT_TO_RECIPIENT

    trigger_keys = set(cross_harness_bridge_trigger.ROLE_STATE_KEYS)
    doctor_keys = set(_BRIDGE_AGENT_TO_RECIPIENT.values())

    assert doctor_keys == trigger_keys, f"Doctor keys {doctor_keys} do not match trigger keys {trigger_keys}"
    assert "prime" not in doctor_keys
    assert "codex" not in doctor_keys
    assert cross_harness_bridge_trigger.ROLE_STATE_KEYS is role_state.ROLE_STATE_KEYS
    assert _BRIDGE_AGENT_TO_RECIPIENT is role_state.BRIDGE_AGENT_TO_RECIPIENT


def test_no_duplicate_role_state_literals_in_dispatch_sources() -> None:
    """Role-state ownership stays in ``groundtruth_kb.bridge.role_state``."""
    repo_root = Path(__file__).resolve().parents[2]
    trigger_source = (repo_root / "scripts" / "cross_harness_bridge_trigger.py").read_text(encoding="utf-8")
    doctor_source = (repo_root / "groundtruth-kb/src/groundtruth_kb/project/doctor.py").read_text(encoding="utf-8")

    assert 'ROLE_STATE_KEYS = ("prime-builder", "loyal-opposition")' not in trigger_source
    assert '_BRIDGE_AGENT_TO_RECIPIENT = {"claude": "prime-builder", "codex": "loyal-opposition"}' not in doctor_source
