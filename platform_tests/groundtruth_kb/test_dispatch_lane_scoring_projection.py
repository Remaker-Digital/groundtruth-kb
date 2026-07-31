"""Tests for WI-4958 dispatch lane-scoring registry/projection foundation."""

from __future__ import annotations

import json
import sys
from dataclasses import replace
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_PACKAGE_SRC = _REPO_ROOT / "groundtruth-kb" / "src"
if str(_PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(_PACKAGE_SRC))

from groundtruth_kb.db import KnowledgeDB  # noqa: E402
from groundtruth_kb.dispatcher.lane_scoring import (  # noqa: E402
    DEFAULT_ACTIVITY_TYPES,
    DispatchLane,
    EvidenceRef,
    build_compact_projection,
    lanes_from_harness_projection,
    projection_is_compact,
)

from scripts.benchmarks import fixture_corpus, harness_quality_runner, harness_quality_scoring  # noqa: E402


def _projection() -> dict[str, object]:
    return {
        "schema_version": 1,
        "harnesses": [
            {
                "id": "A",
                "harness_name": "codex",
                "harness_type": "codex",
                "status": "active",
                "role": ["prime-builder"],
                "can_receive_dispatch": True,
                "dispatch_quality": 90,
                "dispatch_availability": 80,
                "dispatch_cost": 10,
            },
            {
                "id": "B",
                "harness_name": "claude",
                "harness_type": "claude",
                "status": "registered",
                "role": ["loyal-opposition", "prime-builder"],
                "can_receive_dispatch": False,
            },
            {
                "id": "C",
                "harness_name": "antigravity",
                "harness_type": "antigravity",
                "status": "retired",
                "role": ["loyal-opposition"],
                "can_receive_dispatch": True,
            },
        ],
    }


def _quality_snapshot(*, generated_at: str, ttl_seconds: int = 86_400) -> tuple[dict[str, object], dict[str, object]]:
    fixture = fixture_corpus.require_valid_fixture_corpus()[0]
    target = harness_quality_runner.BenchmarkHarnessTarget(
        harness_id="A",
        provider="codex",
        model="gpt-5-codex",
        author_model_configuration="codex desktop synthetic benchmark",
    )
    record = dict(
        harness_quality_runner.build_dry_run_evidence_records(
            run_id="run-quality-input",
            harness_targets=(target,),
            benchmark_mode="prime_builder",
            started_at=generated_at,
            ended_at=generated_at,
            fixtures=(fixture,),
        )[0]
    )
    record["failure_class"] = fixture.failure_classes[0]
    snapshot = harness_quality_scoring.build_dispatch_quality_snapshot(
        (record,),
        fixtures=(fixture,),
        generated_at=generated_at,
        ttl_seconds=ttl_seconds,
    )
    return snapshot, record


def test_schema_creates_lane_scoring_tables_and_current_views(tmp_path: Path) -> None:
    db = KnowledgeDB(tmp_path / "groundtruth.db")
    try:
        names = {
            row[0]
            for row in db._get_conn().execute(  # noqa: SLF001 - schema assertion
                "SELECT name FROM sqlite_master WHERE type IN ('table', 'view')"
            )
        }
    finally:
        db.close()

    expected = {
        "dispatch_lanes",
        "dispatch_lane_score_dimensions",
        "dispatch_lane_scoring_evidence",
        "dispatch_lane_score_snapshots",
        "dispatch_lane_projection_snapshots",
        "current_dispatch_lanes",
        "current_dispatch_lane_projection_snapshots",
    }
    assert expected <= names


def test_seed_lane_matrix_from_non_retired_harness_roles_and_activities() -> None:
    lanes = lanes_from_harness_projection(_projection())

    # A has 1 role, B has 2 roles, retired C is excluded.
    assert len(lanes) == 3 * len(DEFAULT_ACTIVITY_TYPES)
    assert {lane.harness_id for lane in lanes} == {"A", "B"}
    assert all(lane.route_selectable is False for lane in lanes)
    assert all(lane.model_route.endswith("-fixed") for lane in lanes)
    assert {"prime-builder", "loyal-opposition"} == {lane.role for lane in lanes}
    assert all(lane.dispatch_enabled is False for lane in lanes)
    assert any(lane.shadow_enabled for lane in lanes if lane.harness_id == "A")


def test_benchmark_quality_snapshot_overrides_lane_quality_without_raw_evidence() -> None:
    snapshot, record = _quality_snapshot(generated_at="2026-07-07T00:00:00Z")

    lane = next(
        lane
        for lane in lanes_from_harness_projection(_projection(), quality_snapshot=snapshot)
        if lane.harness_id == "A" and lane.role == "prime-builder" and lane.activity_type == "build"
    )
    projection = build_compact_projection([lane], as_of="2026-07-02T00:00:01+00:00")

    compact_lane = projection["effective_ranked_lanes"]["prime-builder"]["build"][0]
    assert compact_lane["utility_components"]["quality"] == 100.0
    assert compact_lane["evidence_ref_count"] == 1
    assert projection_is_compact(projection)
    rendered = json.dumps(projection, sort_keys=True)
    assert str(record["fixture_id"]) not in rendered
    assert "artifact_links" not in rendered


def test_stale_benchmark_quality_snapshot_blocks_production_lane() -> None:
    snapshot, _record = _quality_snapshot(generated_at="2020-01-01T00:00:00Z", ttl_seconds=1)
    lane = next(
        lane
        for lane in lanes_from_harness_projection(_projection(), quality_snapshot=snapshot)
        if lane.harness_id == "A" and lane.role == "prime-builder" and lane.activity_type == "build"
    )
    lane = replace(lane, lifecycle="approved", dispatch_enabled=True)

    projection = build_compact_projection(
        [lane],
        production=True,
        as_of="2026-07-02T00:00:00+00:00",
        required_evidence=("benchmark",),
    )

    assert projection["effective_ranked_lanes"] == {}
    assert "stale_benchmark_quality" in projection["blocked_lanes"][0]["reasons"]


def test_compact_projection_keeps_lifecycle_first_metadata_without_raw_evidence() -> None:
    lane = DispatchLane(
        lane_id="a:codex:codex-fixed:prime-builder:build",
        harness_id="A",
        provider="codex",
        model_route="codex-fixed",
        role="prime-builder",
        activity_type="build",
        lifecycle="shadow",
        shadow_enabled=True,
        score_components={"quality": 90.0, "availability": 80.0, "cost": 10.0},
        evidence_refs={
            "parity": EvidenceRef(
                "parity",
                "fresh",
                ref="bridge/example-verified.md",
                captured_at="2026-07-02T00:00:00+00:00",
            )
        },
    )

    projection = build_compact_projection([lane], as_of="2026-07-02T00:00:00+00:00")

    compact_lane = projection["effective_ranked_lanes"]["prime-builder"]["build"][0]
    assert compact_lane["lifecycle"] == "shadow"
    assert compact_lane["utility_components"] == {"quality": 90.0, "availability": 80.0, "cost": 10.0}
    assert compact_lane["evidence_ref_count"] == 1
    assert projection["runtime_suppression"]["raw_evidence_omitted"] is True
    assert projection_is_compact(projection)
    assert "bridge/example-verified.md" not in json.dumps(projection, sort_keys=True)


def test_production_projection_fails_closed_without_required_evidence() -> None:
    lane = DispatchLane(
        lane_id="a:codex:codex-fixed:prime-builder:build",
        harness_id="A",
        provider="codex",
        model_route="codex-fixed",
        role="prime-builder",
        activity_type="build",
        lifecycle="approved",
        dispatch_enabled=True,
        shadow_enabled=True,
    )

    projection = build_compact_projection(
        [lane],
        production=True,
        as_of="2026-07-02T00:00:00+00:00",
    )

    assert projection["effective_ranked_lanes"] == {}
    assert projection["runtime_suppression"]["production_fail_closed"] is True
    blocked = projection["blocked_lanes"][0]
    assert blocked["lane_id"] == lane.lane_id
    assert "missing_required_evidence:parity" in blocked["reasons"]
    assert "missing_required_evidence:readiness" in blocked["reasons"]
    assert "missing_required_evidence:benchmark" in blocked["reasons"]


def test_projection_snapshots_are_append_only_versions(tmp_path: Path) -> None:
    db = KnowledgeDB(tmp_path / "groundtruth.db")
    try:
        lane = lanes_from_harness_projection(_projection())[0]
        first = build_compact_projection([lane], source_snapshot_id="candidate-1")
        second = build_compact_projection([lane], source_snapshot_id="candidate-2")

        db.insert_dispatch_lane_projection_snapshot(
            "projection-shadow",
            "shadow_advisory",
            first,
            "test",
            "initial projection",
            source_snapshot_id="candidate-1",
        )
        current = db.insert_dispatch_lane_projection_snapshot(
            "projection-shadow",
            "shadow_advisory",
            second,
            "test",
            "updated projection",
            source_snapshot_id="candidate-2",
        )
        history = db.get_dispatch_lane_projection_snapshot_history("projection-shadow")
    finally:
        db.close()

    assert current is not None
    assert current["version"] == 2
    assert current["projection_payload_parsed"]["source_snapshot_id"] == "candidate-2"
    assert [row["version"] for row in history] == [2, 1]


def test_helper_reads_but_does_not_write_harness_registry(tmp_path: Path) -> None:
    registry = tmp_path / "harness-state" / "harness-registry.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(json.dumps(_projection(), indent=2), encoding="utf-8")
    before = registry.read_bytes()

    lanes = lanes_from_harness_projection(json.loads(registry.read_text(encoding="utf-8")))

    assert lanes
    assert registry.read_bytes() == before
