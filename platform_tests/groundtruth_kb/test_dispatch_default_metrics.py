from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "groundtruth-kb" / "src"))

from groundtruth_kb import dispatch_default_metrics as metrics  # noqa: E402
from groundtruth_kb.db import KnowledgeDB  # noqa: E402


def _event(event_id: str, event_at: str, **overrides: object) -> dict[str, object]:
    value: dict[str, object] = {
        "id": event_id,
        "event_at": event_at,
        "dispatch_id": event_id,
        "bridge_document_id": "dispatch-thread",
        "work_item_id": "WI-5173",
        "harness_session_id": f"session-{event_id}",
        "harness_id": "F",
        "harness_name": "openrouter",
        "provider": "openrouter",
        "model_profile": "provider/model-v1",
        "role": "loyal-opposition",
        "role_source": "document",
        "intended_role": "loyal-opposition",
        "actual_role": "loyal-opposition",
        "queue_outcome": "reviewed",
        "selection_outcome": "selected",
        "started_at": event_at,
        "ended_at": event_at,
        "elapsed_ms": 2500,
        "exit_status": 0,
        "stop_reason": "completed",
        "turns_used": 4,
        "tool_calls_total": 2,
        "tool_counts": {"Read": 1, "Bash": 1},
        "input_tokens": 10,
        "output_tokens": 20,
        "cached_tokens": 0,
        "total_tokens": 30,
        "provider_cost": 0.0,
        "benchmark_estimated_cost": 0.25,
        "quality_score": 0.9,
        "quality_source": "benchmark-1",
        "adaptation_score": 0.8,
        "adaptation_source": "adaptation-1",
        "source_refs": {"telemetry": f"telemetry/{event_id}", "benchmark": "benchmark-1"},
    }
    value.update(overrides)
    return value


def test_normalize_is_allowlisted_private_and_nullable() -> None:
    event = metrics.normalize_metric_event(
        _event(
            "event-private",
            "2026-07-11T00:00:00Z",
            input_tokens=None,
            total_tokens=None,
            provider_cost=None,
            tool_calls_total=0,
            prompt_content="owner prompt must not persist",
            tool_arguments={"secret": "must not persist"},
            provider_body={"api_key": "must not persist"},
            environment_value="must not persist",
        )
    )

    serialized = json.dumps(event, sort_keys=True)
    assert metrics.EVENT_SCHEMA_ID == "gtkb.dispatch_default_metric_event.v1"
    assert event["input_tokens"] is None
    assert event["provider_cost"] is None
    assert event["tool_calls_total"] == 0
    assert "owner prompt" not in serialized
    assert "api_key" not in serialized
    assert "tool_arguments" not in serialized
    assert "environment_value" not in serialized
    assert event["coverage"]["usage"]["status"] == "unavailable"


def test_event_persistence_is_canonical_and_idempotent(tmp_path: Path) -> None:
    db = KnowledgeDB(tmp_path / "groundtruth.db")
    raw = _event("event-one", "2026-07-11T00:00:00Z", input_tokens=None)

    first = metrics.persist_metric_event(db, raw, "test", "WI-5180 test event")
    second = metrics.persist_metric_event(db, raw, "test", "retry should be idempotent")

    assert first["id"] == second["id"] == "event-one"
    assert len(db.list_dispatch_default_metric_events()) == 1
    assert first["input_tokens"] is None
    assert first["tool_counts_parsed"] == {"Bash": 1, "Read": 1}
    table_count = (
        db._get_conn()
        .execute(
            "SELECT COUNT(*) FROM dispatch_events WHERE rule_id = ?",
            (metrics.EVENT_SCHEMA_ID,),
        )
        .fetchone()[0]
    )
    assert table_count == 1


def test_snapshot_is_bounded_deterministic_and_cost_separated() -> None:
    events = [
        _event("event-a", "2026-07-11T00:00:00Z", provider_cost=None, benchmark_estimated_cost=1.0),
        _event("event-b", "2026-07-11T00:01:00Z", turns_used=None, total_tokens=None),
        _event("event-c", "2026-07-11T00:02:00Z", harness_name="claude", provider_cost=None),
    ]
    first = metrics.build_metrics_snapshot(events, max_records=2, generated_at="2026-07-11T00:03:00Z")
    second = metrics.build_metrics_snapshot(list(reversed(events)), max_records=2, generated_at="2026-07-11T00:03:00Z")

    assert first == second
    assert first["snapshot_schema_id"] == "gtkb.dispatch_default_metrics_snapshot.v1"
    assert first["source_record_count"] == 2
    assert first["source_event_ids"] == ["event-b", "event-c"]
    assert first["cost_coverage"]["provider_reported"]["observed_count"] == 1
    assert first["cost_coverage"]["benchmark_estimated"]["observed_count"] == 2
    assert first["usage_coverage"]["usage"]["missing_count"] == 1


def test_snapshot_persistence_has_one_authority_and_explicit_freshness(tmp_path: Path) -> None:
    db = KnowledgeDB(tmp_path / "groundtruth.db")
    raw_events = [_event("event-one", "2026-07-11T00:00:00Z")]
    metrics.persist_metric_event(db, raw_events[0], "test", "seed event")

    snapshot = metrics.persist_metrics_snapshot(
        db,
        db.list_dispatch_default_metric_events(),
        "test",
        "WI-5180 snapshot",
        generated_at="2026-07-11T00:01:00Z",
    )
    retry = metrics.persist_metrics_snapshot(
        db,
        db.list_dispatch_default_metric_events(),
        "test",
        "retry should be idempotent",
        generated_at="2026-07-11T00:01:00Z",
    )

    assert snapshot["id"] == retry["id"]
    assert snapshot["freshness_parsed"]["status"] == "fresh"
    assert snapshot["provenance_parsed"]["source_schema_id"] == metrics.EVENT_SCHEMA_ID
    assert len(db.list_dispatch_default_metrics_snapshots()) == 1
