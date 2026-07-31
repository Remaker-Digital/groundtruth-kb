# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Direct disable-guard lifecycle tests for WI-5304."""

from __future__ import annotations

import datetime as dt
import json

import pytest
from groundtruth_kb import dispatcher_disable_guard as guard

NOW = dt.datetime(2026, 7, 16, 8, 0, tzinfo=dt.UTC)


def test_explicit_ttl_expiry_overrides_owner_evidence(tmp_path) -> None:
    guard.record_guarded_disable(
        tmp_path,
        task_names=["task"],
        component="dispatcher",
        ttl_seconds=60,
        owner_quiesce_record="DELIB-owner",
        reason="bounded",
        now=NOW - dt.timedelta(seconds=61),
    )

    status = guard.disable_guard_status(tmp_path, task_name="task", now=NOW)

    assert status["active"] is False
    assert status["expired"] is True
    assert status["status"] == "expired"


def test_owner_only_guard_remains_indefinitely_active(tmp_path) -> None:
    guard.record_guarded_disable(
        tmp_path,
        task_names=["task"],
        component="dispatcher",
        owner_quiesce_record="DELIB-owner",
        reason="owner hold",
        now=NOW - dt.timedelta(days=30),
    )

    status = guard.disable_guard_status(tmp_path, task_name="task", now=NOW)

    assert status["active"] is True
    assert status["expired"] is False
    assert status["status"] == "active"


def test_supersession_preserves_original_evidence_and_is_idempotent(tmp_path) -> None:
    guard.record_guarded_disable(
        tmp_path,
        task_names=["task", "other"],
        component="dispatcher",
        ttl_seconds=600,
        owner_quiesce_record="DELIB-owner",
        reason="original reason",
        actor="original actor",
        now=NOW,
    )
    path = guard.default_guard_path(tmp_path)
    original = json.loads(path.read_text(encoding="utf-8"))["records"]["task"].copy()

    first = guard.supersede_guarded_disable(
        tmp_path,
        task_names=["task", "absent"],
        actor="enable actor",
        reason="successful governed enable",
        now=NOW + dt.timedelta(seconds=1),
    )
    second = guard.supersede_guarded_disable(
        tmp_path,
        task_names=["task"],
        actor="different actor",
        reason="different reason",
        now=NOW + dt.timedelta(seconds=2),
    )
    payload = json.loads(path.read_text(encoding="utf-8"))
    record = payload["records"]["task"]

    for field, value in original.items():
        assert record[field] == value
    assert record["superseded_at"] == "2026-07-16T08:00:01Z"
    assert record["superseded_by"] == "enable actor"
    assert record["supersession_reason"] == "successful governed enable"
    assert payload["records"]["other"].get("superseded_at") is None
    assert first["changed"] is True
    assert first["records"][0]["status"] == "superseded"
    assert first["records"][0]["active"] is False
    assert first["records"][1]["status"] == "absent"
    assert second["changed"] is False


def test_supersession_refuses_unreadable_document(tmp_path) -> None:
    path = guard.default_guard_path(tmp_path)
    path.parent.mkdir(parents=True)
    path.write_text("not json", encoding="utf-8")

    with pytest.raises(guard.DispatcherDisableGuardError, match="unreadable"):
        guard.supersede_guarded_disable(tmp_path, task_names=["task"], actor="actor", reason="reason")

    assert path.read_text(encoding="utf-8") == "not json"


def test_supersession_write_failure_preserves_original_document(tmp_path, monkeypatch) -> None:
    guard.record_guarded_disable(
        tmp_path,
        task_names=["task"],
        component="dispatcher",
        ttl_seconds=600,
        reason="bounded",
        now=NOW,
    )
    path = guard.default_guard_path(tmp_path)
    original = path.read_bytes()
    monkeypatch.setattr(
        guard,
        "_atomic_write_json",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(guard.DispatcherDisableGuardError("write failed")),
    )

    with pytest.raises(guard.DispatcherDisableGuardError, match="write failed"):
        guard.supersede_guarded_disable(tmp_path, task_names=["task"], actor="actor", reason="reason")

    assert path.read_bytes() == original
