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


# ---------------------------------------------------------------------------
# Success ledger tests (WI-5549)
# ---------------------------------------------------------------------------

_SUCCESS_HARNESSES = (
    {"harness_id": "A", "harness_name": "codex", "role": "prime-builder"},
    {"harness_id": "D", "harness_name": "ollama", "role": "loyal-opposition"},
    {"harness_id": "F", "harness_name": "openrouter", "role": "loyal-opposition"},
)


def _success_event(
    event_id: str,
    event_at: str,
    dispatch_id: str,
    harness_id: str,
    role: str,
    bridge_document_id: str,
    **overrides: object,
) -> dict[str, object]:
    """Build a minimal terminal-success metric event."""
    base: dict[str, object] = {
        "id": event_id,
        "event_at": event_at,
        "dispatch_id": dispatch_id,
        "bridge_document_id": bridge_document_id,
        "work_item_id": "WI-7001",
        "harness_session_id": f"session-{event_id}",
        "harness_id": harness_id,
        "harness_name": harness_id,
        "role": role,
        "queue_outcome": "reviewed",
        "selection_outcome": "selected",
        "started_at": event_at,
        "ended_at": event_at,
        "elapsed_ms": 1000,
        "exit_status": 0,
        "stop_reason": "completed",
        "turns_used": 5,
        "tool_calls_total": 3,
        "input_tokens": 50,
        "output_tokens": 25,
        "total_tokens": 75,
    }
    base.update(overrides)
    return base


def _seed_events(db: KnowledgeDB, events: list[dict[str, object]]) -> None:
    for event in events:
        metrics.persist_metric_event(db, event, "test", "WI-5549 ledger test")


class TestSuccessLedger:
    def test_empty_event_store_returns_zero_streak(self, tmp_path: Path) -> None:
        db = KnowledgeDB(tmp_path / "groundtruth.db")
        ledger = metrics.build_success_ledger(db)
        assert ledger["schema_id"] == metrics.LEDGER_SCHEMA_ID
        assert ledger["streak"] == 0
        assert ledger["threshold_met"] is False

    def test_60_clean_events_across_A_D_F_produces_streak_60(self, tmp_path: Path) -> None:
        db = KnowledgeDB(tmp_path / "groundtruth.db")
        events: list[dict[str, object]] = []
        harnesses = list(_SUCCESS_HARNESSES)
        for i in range(60):
            h = harnesses[i % len(harnesses)]
            events.append(
                _success_event(
                    event_id=f"ev-{i:04d}",
                    event_at=f"2026-07-11T{i // 3600:02d}:{i % 3600 // 60:02d}:{i % 60:02d}Z",
                    dispatch_id=f"dispatch-{i:04d}",
                    harness_id=h["harness_id"],
                    role=h["role"],
                    bridge_document_id=f"doc-{i:04d}",
                )
            )
        _seed_events(db, events)

        ledger = metrics.build_success_ledger(db, threshold=60)
        assert ledger["streak"] == 60
        assert ledger["threshold_met"] is True
        seq = ledger["sequence"]
        assert seq["start"] is not None
        assert seq["end"] is not None
        assert seq["start"]["dispatch_id"] == "dispatch-0000"
        assert seq["end"]["dispatch_id"] == "dispatch-0059"
        dist = ledger["distribution"]
        assert dist["by_harness"]["A"] == 20
        assert dist["by_harness"]["D"] == 20
        assert dist["by_harness"]["F"] == 20
        assert dist["by_role"]["prime-builder"] == 20
        assert dist["by_role"]["loyal-opposition"] == 40
        assert ledger["first_reset_reason"] is None

    def test_failure_class_resets_streak_and_records_reason(self, tmp_path: Path) -> None:
        db = KnowledgeDB(tmp_path / "groundtruth.db")
        harnesses = list(_SUCCESS_HARNESSES)
        events: list[dict[str, object]] = []
        # 30 clean successes
        for i in range(30):
            h = harnesses[i % len(harnesses)]
            events.append(
                _success_event(
                    event_id=f"ev-{i:04d}",
                    event_at=f"2026-07-11T{i // 60:02d}:{i % 60:02d}:00Z",
                    dispatch_id=f"dispatch-{i:04d}",
                    harness_id=h["harness_id"],
                    role=h["role"],
                    bridge_document_id=f"doc-{i:04d}",
                )
            )
        # 1 failure at its own unambiguous timestamp between the two runs
        events.append(
            _success_event(
                event_id="ev-fail-0001",
                event_at="2026-07-11T00:30:00Z",
                dispatch_id="dispatch-fail-0001",
                harness_id="F",
                role="loyal-opposition",
                bridge_document_id="doc-fail-0001",
                queue_outcome="failed",
                failure_class="provider_failure",
                exit_status=1,
                stop_reason="error",
            )
        )
        # 30 more clean successes after failure (i=30..59)
        for i in range(30, 60):
            h = harnesses[i % len(harnesses)]
            events.append(
                _success_event(
                    event_id=f"ev-{i:04d}",
                    event_at=f"2026-07-11T{(i + 31) // 60:02d}:{(i + 31) % 60:02d}:00Z",
                    dispatch_id=f"dispatch-{i:04d}",
                    harness_id=h["harness_id"],
                    role=h["role"],
                    bridge_document_id=f"doc-{i:04d}",
                )
            )
        _seed_events(db, events)

        ledger = metrics.build_success_ledger(db, threshold=60)
        assert ledger["streak"] == 30
        assert ledger["threshold_met"] is False
        assert ledger["first_reset_reason"] == "failure_class:provider_failure"

    def test_non_success_outcome_resets_streak(self, tmp_path: Path) -> None:
        db = KnowledgeDB(tmp_path / "groundtruth.db")
        events: list[dict[str, object]] = []
        # 10 good — unique timestamps 00:00 through 00:09
        for i in range(10):
            events.append(
                _success_event(
                    event_id=f"ev-{i:04d}",
                    event_at=f"2026-07-11T00:{i:02d}:00Z",
                    dispatch_id=f"dispatch-{i:04d}",
                    harness_id="A",
                    role="prime-builder",
                    bridge_document_id=f"doc-{i:04d}",
                )
            )
        # Reset with non-success queue_outcome at 00:10
        events.append(
            _success_event(
                event_id="ev-bad-outcome",
                event_at="2026-07-11T00:10:00Z",
                dispatch_id="dispatch-bad-outcome",
                harness_id="A",
                role="prime-builder",
                bridge_document_id="doc-bad",
                queue_outcome="abandoned",
            )
        )
        # 5 more good at times 00:11 through 00:15
        for i in range(5):
            events.append(
                _success_event(
                    event_id=f"ev-r{i:04d}",
                    event_at=f"2026-07-11T00:{11 + i:02d}:00Z",
                    dispatch_id=f"dispatch-r{i:04d}",
                    harness_id="A",
                    role="prime-builder",
                    bridge_document_id=f"doc-r{i:04d}",
                )
            )
        _seed_events(db, events)

        ledger = metrics.build_success_ledger(db)
        assert ledger["streak"] == 5
        assert "non_success_outcome" in ledger["first_reset_reason"]

    def test_missing_provenance_binding_never_counts_as_success(self, tmp_path: Path) -> None:
        db = KnowledgeDB(tmp_path / "groundtruth.db")
        events: list[dict[str, object]] = [
            _success_event(
                event_id="ev-good-01",
                event_at="2026-07-11T00:01:00Z",
                dispatch_id="dispatch-good-01",
                harness_id="A",
                role="prime-builder",
                bridge_document_id="doc-good-01",
            ),
            _success_event(
                event_id="ev-no-harness",
                event_at="2026-07-11T00:02:00Z",
                dispatch_id="ev-no-harness",
                harness_id="A",
                role="prime-builder",
                bridge_document_id="",
            ),
            _success_event(
                event_id="ev-good-03",
                event_at="2026-07-11T00:03:00Z",
                dispatch_id="dispatch-good-03",
                harness_id="A",
                role="prime-builder",
                bridge_document_id="doc-good-03",
            ),
        ]
        _seed_events(db, events)

        ledger = metrics.build_success_ledger(db)
        # The empty bridge_document_id should reset the streak
        assert ledger["streak"] == 1
        assert ledger["first_reset_reason"] == "missing_provenance_binding"

    def test_duplicate_event_ids_do_not_inflate_streak(self, tmp_path: Path) -> None:
        db = KnowledgeDB(tmp_path / "groundtruth.db")
        events: list[dict[str, object]] = []
        for i in range(20):
            events.append(
                _success_event(
                    event_id="ev-dup",
                    event_at=f"2026-07-11T00:{i:02d}:00Z",
                    dispatch_id="dispatch-dup",
                    harness_id="A",
                    role="prime-builder",
                    bridge_document_id="doc-dup",
                )
            )
        _seed_events(db, events)

        ledger = metrics.build_success_ledger(db)
        assert ledger["streak"] == 1

    def test_events_ordered_by_event_at_then_id(self, tmp_path: Path) -> None:
        db = KnowledgeDB(tmp_path / "groundtruth.db")
        # Out-of-order insertion
        events: list[dict[str, object]] = [
            _success_event(
                event_id="ev-C",
                event_at="2026-07-11T00:03:00Z",
                dispatch_id="dispatch-C",
                harness_id="A",
                role="prime-builder",
                bridge_document_id="doc-C",
            ),
            _success_event(
                event_id="ev-A",
                event_at="2026-07-11T00:01:00Z",
                dispatch_id="dispatch-A",
                harness_id="A",
                role="prime-builder",
                bridge_document_id="doc-A",
            ),
            _success_event(
                event_id="ev-B",
                event_at="2026-07-11T00:02:00Z",
                dispatch_id="dispatch-B",
                harness_id="A",
                role="prime-builder",
                bridge_document_id="doc-B",
            ),
        ]
        _seed_events(db, events)

        ledger = metrics.build_success_ledger(db)
        assert ledger["streak"] == 3
        assert ledger["sequence"]["start"]["dispatch_id"] == "dispatch-A"
        assert ledger["sequence"]["end"]["dispatch_id"] == "dispatch-C"

    def test_ledger_from_root_unavailable_when_no_db(self, tmp_path: Path) -> None:
        root = str(tmp_path)
        ledger = metrics.build_success_ledger_from_root(root)
        assert ledger["streak"] == 0
        assert ledger["threshold_met"] is False
        assert ledger["first_reset_reason"] == "canonical_event_store_unavailable"

    def test_build_success_ledger_rejects_negative_threshold(self) -> None:
        import pytest

        with pytest.raises(ValueError, match="threshold must be positive"):
            metrics.build_success_ledger(None, threshold=0)  # type: ignore[arg-type]
