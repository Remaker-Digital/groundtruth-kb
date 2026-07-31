"""Tests for the modernization source-of-truth freshness evaluator."""

from __future__ import annotations

import importlib.util
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "check_source_of_truth_freshness.py"


@pytest.fixture
def freshness():
    spec = importlib.util.spec_from_file_location("check_source_of_truth_freshness", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _valid_record(now: datetime) -> dict:
    return {
        "source_id": "GOV-1",
        "source_path": "groundtruth.db:current_specifications",
        "authority_class": "stated",
        "source_version_or_hash": "v1",
        "churn_class": "low",
        "generated_at": now.isoformat(),
        "ttl_seconds": 120,
        "bounded_usage_context": "session_start",
        "live_query_route": "gt spec show GOV-1",
        "recovery_route": "gt spec show GOV-1",
        "embedded_content": {"status": "specified"},
    }


def test_complete_low_churn_extract_is_current(freshness):
    now = datetime(2026, 7, 13, tzinfo=UTC)

    result = freshness.evaluate_extract(_valid_record(now), now=now)

    assert result["eligible_as_current"] is True
    assert result["status"] == "current"


@pytest.mark.parametrize(
    "field",
    sorted(
        {
            "source_id",
            "authority_class",
            "source_version_or_hash",
            "churn_class",
            "generated_at",
            "ttl_seconds",
            "bounded_usage_context",
            "live_query_route",
            "recovery_route",
        }
    ),
)
def test_low_churn_extract_requires_every_metadata_field(freshness, field):
    now = datetime(2026, 7, 13, tzinfo=UTC)
    record = _valid_record(now)
    record.pop(field)

    result = freshness.evaluate_extract(record, now=now)

    assert result["eligible_as_current"] is False
    assert f"missing:{field}" in result["reasons"]


@pytest.mark.parametrize("churn_class", ["bridge_queue", "dispatcher_workers", "active_claims", "runtime_health"])
def test_high_churn_embedded_state_is_live_query_only(freshness, churn_class):
    result = freshness.evaluate_extract(
        {
            "source_id": churn_class,
            "churn_class": churn_class,
            "embedded_content": {"state": "active"},
            "live_query_route": "gt status",
            "recovery_route": "gt status",
        }
    )

    assert result["eligible_as_current"] is False
    assert {"high-churn", "live-query-only"} <= set(result["reasons"])


def test_expired_or_conflicting_extract_routes_to_recovery(freshness):
    now = datetime(2026, 7, 13, tzinfo=UTC)
    expired = _valid_record(now)
    expired["generated_at"] = (now - timedelta(seconds=121)).isoformat()
    conflict = {**_valid_record(now), "conflict": True}

    expired_result = freshness.evaluate_extract(expired, now=now)
    conflict_result = freshness.evaluate_extract(conflict, now=now)

    assert expired_result["status"] == "recovery_required"
    assert "expired" in expired_result["reasons"]
    assert conflict_result["status"] == "recovery_required"
    assert "conflict" in conflict_result["reasons"]
    assert expired_result["recovery_route"] == conflict_result["recovery_route"] == "gt spec show GOV-1"


def test_retired_bridge_and_role_authority_are_rejected(freshness):
    now = datetime(2026, 7, 13, tzinfo=UTC)
    for retired_path in ("bridge/INDEX.md", "harness-state/role-assignments.json"):
        result = freshness.evaluate_extract({**_valid_record(now), "source_path": retired_path}, now=now)
        assert result["eligible_as_current"] is False
        assert "retired-authority" in result["reasons"]


def test_contract_fixture_report_executes_all_four_required_assertions(freshness):
    report = freshness.run_contract_fixtures(now=datetime(2026, 7, 13, tzinfo=UTC))

    assert report["status"] == "PASS"
    assert {item["id"] for item in report["assertions"]} == {
        "FRESH-V4-A1",
        "FRESH-V4-A2",
        "FRESH-V4-A3",
        "FRESH-V4-A4",
    }
    assert all(item["status"] == "PASS" and item["evidence"] for item in report["assertions"])
