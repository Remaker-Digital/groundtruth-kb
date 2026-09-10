"""The remaining startup renderer neither consults nor mutates old ledgers."""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts import session_self_initialization as startup


@pytest.mark.parametrize("history", [b"## Pending\nDECISION-001: Grant permission\n", b"\xff malformed history\r\n"])
def test_startup_does_not_read_or_mutate_historical_owner_ledger(tmp_path, monkeypatch, history):
    ledger = tmp_path / "memory/pending-owner-decisions.md"
    ledger.parent.mkdir()
    ledger.write_bytes(history)
    original_open = Path.open

    def guarded_open(path, *args, **kwargs):
        assert path != ledger, "startup consulted historical owner decisions"
        return original_open(path, *args, **kwargs)

    model = {
        "generated_at": "test",
        "role": dict.fromkeys(
            ("assumed_role", "role_assignment", "bridge", "bridge_operation_instructions", "role_mapping_source"),
            "not supplied",
        ),
        "metrics": {"tokens": {"tokens_consumed_before_user_input": None, "measurement_status": "unavailable"}},
        "dashboard_requirements": {"scope_note": "fixture"},
        "governance_stance": [],
    }
    # These render unrelated domain sections; ledger loading was in render_report.
    for name in (
        "_render_current_project_state",
        "_render_session_startup_briefing",
        "_render_top_priority_actions_section",
        "render_active_work_subject",
        "render_session_context_review_independence_disclosure",
    ):
        monkeypatch.setattr(startup, name, lambda *args, **kwargs: "")
    monkeypatch.setattr(startup, "_render_dashboard_reachability_lines", lambda *args: [])
    with monkeypatch.context() as guard:
        guard.setattr(Path, "open", guarded_open)
        report = startup.render_report(model, "fixture", tmp_path)
    assert report.startswith("# GroundTruth-KB Fresh Session Startup")
    assert "Pending Owner Decisions" not in report
    assert "DECISION-001" not in report
    assert ledger.read_bytes() == history
    assert sorted(p.relative_to(tmp_path).as_posix() for p in tmp_path.rglob("*") if p.is_file()) == [
        "memory/pending-owner-decisions.md"
    ]
