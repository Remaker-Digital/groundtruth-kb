"""Tests for dashboard work-subject selector + writer/snapshot field contract.

Slice 2.1 of GTKB-DASHBOARD-002 — see
``bridge/gtkb-dashboard-industry-alignment-slice2a-visibility-005.md``.

The contract under test:

* The model object returned by ``build_startup_model()`` carries
  ``current_work_subject`` at the top level (paired with the structured
  ``model["metrics"]["work_subject"]`` source-of-truth record).
* ``_snapshot_from_model()`` projects ``current_work_subject`` onto every
  history-row snapshot.
* ``write_dashboard_and_report()`` is the page-facing
  ``dashboard-data.json`` writer; ``refresh_dashboard_db.py`` is not.
* The landing page IIFE reads ``latest.current_work_subject`` (uniform
  writer-side contract — no page-side branch on payload shape).
* Both ``selectLatest()`` branches expose the field, so the empty-history
  fallback still renders the canonical subject.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts import session_self_initialization as ssi  # noqa: E402
from scripts.gtkb_dashboard import refresh_dashboard_db as rdb  # noqa: E402

INDEX_HTML = REPO_ROOT / "docs" / "gtkb-dashboard" / "index.html"

EXPECTED_SCOPE_KEYS = {
    "regression_release_blocker_count",
    "backlog_active_items",
    "membase_open_work_items",
    "deliberation_archive_current_total",
    "specification_current_total",
    "drift_changed_path_count",
    "pytest_file_count",
    "contention_actionable_bridge_count",
    "skill_template_count",
}


def _fake_model(*, subject: str | None, present: bool) -> dict[str, Any]:
    """Build the minimal ``model`` shape ``_snapshot_from_model`` needs."""
    return {
        "generated_at": "2026-04-24T10:00:00+00:00",
        "metrics": {
            "backlog": {"active_item_count": 5},
            "membase": {"open_work_items": 0},
            "deliberation_archive": {"current_total": 700},
            "tests": {"pytest_file_count": 100},
            "templates": {"skill_template_count": 30},
            "specifications": {"current_total": 2100},
            "drift": {"changed_path_count": 4},
            "regression": {"release_blocker_count": 0},
            "contention": {"actionable_count": 1},
            "tokens": {"tokens_consumed_before_user_input": None, "measurement_status": "n/a"},
            "work_subject": {
                "current_subject": subject,
                "source_path": ".claude/session/work-subject.json",
                "present": present,
            },
        },
        "current_work_subject": subject,
    }


def _seed_canonical_state(project_root: Path, subject: str) -> Path:
    target = project_root / ".claude" / "session" / "work-subject.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": 1,
        "current_subject": subject,
        "updated_at": "2026-04-24T09:00:00+00:00",
        "updated_by": "test-fixture",
        "source": "pytest seeded",
        "project_root": str(project_root),
        "gtkb_root": None,
        "role_slot": "shared",
        "topology_mode": "single_harness",
    }
    target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return target


# ----------------------------- 1-3: unit ---------------------------------


def test_snapshot_row_carries_current_work_subject() -> None:
    model = _fake_model(subject="application", present=True)
    snapshot = ssi._snapshot_from_model(model)
    assert snapshot["current_work_subject"] == "application"


def test_snapshot_row_subject_none_when_absent() -> None:
    model = _fake_model(subject=None, present=False)
    snapshot = ssi._snapshot_from_model(model)
    assert snapshot["current_work_subject"] is None


def test_model_object_carries_current_work_subject(tmp_path: Path) -> None:
    """Pin writer-side parity that the page-fallback branch depends on (-004 F1)."""
    _seed_canonical_state(tmp_path, "gtkb_infrastructure")
    record = ssi._collect_work_subject(tmp_path)
    assert record["current_subject"] == "gtkb_infrastructure"
    assert record["present"] is True
    # And the fake-model parity matches.
    model = _fake_model(subject=record["current_subject"], present=record["present"])
    assert model["current_work_subject"] == model["metrics"]["work_subject"]["current_subject"]


# --------------------- 4: end-to-end writer integration -------------------


def test_dashboard_data_json_carries_work_subject(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``write_dashboard_and_report()`` writes the field at all three locations."""
    monkeypatch.setattr(
        ssi,
        "_collect_work_subject",
        lambda _root: {
            "current_subject": "application",
            "source_path": ".claude/session/work-subject.json",
            "present": True,
        },
    )
    dashboard_dir = tmp_path / "dashboard"
    history_path = tmp_path / "history.json"
    result = ssi.write_dashboard_and_report(
        REPO_ROOT,
        dashboard_dir,
        history_path,
        generate_pdf=False,
        role_profile="prime-builder",
    )
    payload = json.loads(Path(result["data_path"]).read_text(encoding="utf-8"))
    # Three locations (uniform top-level key on snapshot row + model;
    # structured source-of-truth on metrics).
    assert payload["model"]["current_work_subject"] == "application"
    assert payload["model"]["metrics"]["work_subject"]["current_subject"] == "application"
    assert payload["history"][-1]["current_work_subject"] == "application"


# ---------- 5: producer boundary (refresh_dashboard_db.py is NOT writer) -


def test_refresh_dashboard_db_does_not_write_subject(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``refresh_database()`` must not write ``dashboard-data.json`` at all."""
    # Force the swimlane out_path away from the real docs/ tree to keep this
    # test hermetic — refresh_database now writes the swimlane, but it is not
    # the page-data writer.
    monkeypatch.setattr(rdb, "_write_bridge_swimlane_safe", lambda _root: None)

    db_path = tmp_path / "gtkb-dashboard.sqlite"
    docs_dir = tmp_path / "docs" / "gtkb-dashboard"
    docs_dir.mkdir(parents=True, exist_ok=True)
    sentinel_data_json = docs_dir / "dashboard-data.json"
    sentinel_data_json.write_text('{"sentinel":"untouched"}', encoding="utf-8")

    fake_model = _fake_model(subject="application", present=True)
    fake_history = [ssi._snapshot_from_model(fake_model)]
    rdb.refresh_database(db_path=db_path, project_root=REPO_ROOT, model=fake_model, history=fake_history)

    # The sentinel was never overwritten by refresh_database.
    assert json.loads(sentinel_data_json.read_text(encoding="utf-8")) == {"sentinel": "untouched"}


# ---------- 6-9: static asserts on landing page ---------------------------


def test_landing_page_has_subject_toolbar() -> None:
    text = INDEX_HTML.read_text(encoding="utf-8")
    assert 'id="subject-toolbar"' in text
    assert text.count('class="filter-btn') >= 3
    for filter_value in ("all", "application", "gtkb_infrastructure"):
        assert f'data-filter="{filter_value}"' in text


def test_landing_page_reads_latest_current_work_subject() -> None:
    text = INDEX_HTML.read_text(encoding="utf-8")
    assert "latest.current_work_subject" in text
    # Explicit guardrail against the rejected page-side branch.
    assert "payload.current_work_subject" not in text
    assert "payload.model.current_work_subject" not in text


def test_landing_page_kpi_scope_constants() -> None:
    text = INDEX_HTML.read_text(encoding="utf-8")
    assert "SCOPE_BY_METRIC" in text
    for key in EXPECTED_SCOPE_KEYS:
        # Each key must appear as a property of SCOPE_BY_METRIC.
        assert re.search(rf"\b{re.escape(key)}\s*:", text), f"missing scope mapping for {key}"


def test_landing_page_swimlane_section() -> None:
    text = INDEX_HTML.read_text(encoding="utf-8")
    assert 'id="swimlane-heading"' in text
    assert 'id="swimlane-table"' in text


# ---------- 10-11: branch coverage via Python re-implementation -----------


def _select_latest(payload: dict[str, Any] | list[Any] | None) -> Any:
    """Mirror the four-branch ``selectLatest`` rule in ``index.html``."""
    if not payload:
        return None
    if isinstance(payload, list):
        return payload[-1] if payload else None
    history = payload.get("history") if isinstance(payload, dict) else None
    if isinstance(history, list) and history:
        return history[-1]
    if isinstance(payload, dict) and payload.get("model"):
        return payload["model"]
    return payload


def _read_subject(latest: Any) -> str:
    if isinstance(latest, dict):
        value = latest.get("current_work_subject")
        if value:
            return value
    return "all"


def test_landing_page_fallback_to_model_branch_carries_subject() -> None:
    """Empty-history fallback: page reads ``model.current_work_subject``.

    Pinned via Python re-implementation of ``selectLatest`` mirroring the
    four-branch rule in ``index.html``. Avoids a hard ``js2py`` test
    dependency while pinning the contract end-to-end (-004 F1).
    """
    payload = {
        "model": {
            "current_work_subject": "gtkb_infrastructure",
            "metrics": {"work_subject": {"current_subject": "gtkb_infrastructure"}},
        },
        "history": [],
    }
    latest = _select_latest(payload)
    assert latest is payload["model"]
    assert _read_subject(latest) == "gtkb_infrastructure"
    # And the literal access path the IIFE uses is in the file.
    assert "latest.current_work_subject" in INDEX_HTML.read_text(encoding="utf-8")


def test_older_history_row_without_subject_defaults_to_all() -> None:
    payload = {
        "model": {"current_work_subject": "application"},
        "history": [{"generated_at": "2026-04-23T00:00:00+00:00"}],  # no subject field
    }
    latest = _select_latest(payload)
    assert latest is payload["history"][-1]
    assert _read_subject(latest) == "all"
