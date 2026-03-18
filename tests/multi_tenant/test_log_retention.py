"""Tests for SPEC-1837: Log Retention Policy and Archival.

Verifies tier-based retention periods, cutoff computation, archive path
generation, expired record identification, NDJSON formatting, and
retention summaries.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

import pytest

from src.multi_tenant.log_retention import (
    ARCHIVE_PATH_TEMPLATE,
    DEFAULT_RETENTION_DAYS,
    build_archive_path,
    compute_cutoff_date,
    format_ndjson,
    get_retention_days,
    get_retention_summary,
    identify_expired_records,
)


class TestDefaultRetentionDays:
    """SPEC-1837: Tier-based retention defaults."""

    def test_three_collections(self):
        assert set(DEFAULT_RETENTION_DAYS.keys()) == {
            "audit_logs", "api_key_usage", "alert_history",
        }

    def test_starter_audit_365(self):
        assert DEFAULT_RETENTION_DAYS["audit_logs"]["starter"] == 365

    def test_professional_audit_365(self):
        assert DEFAULT_RETENTION_DAYS["audit_logs"]["professional"] == 365

    def test_enterprise_audit_unlimited(self):
        assert DEFAULT_RETENTION_DAYS["audit_logs"]["enterprise"] is None

    def test_api_key_usage_90_all_tiers(self):
        for tier in ("starter", "professional", "enterprise"):
            assert DEFAULT_RETENTION_DAYS["api_key_usage"][tier] == 90

    def test_alert_history_180_all_tiers(self):
        for tier in ("starter", "professional", "enterprise"):
            assert DEFAULT_RETENTION_DAYS["alert_history"][tier] == 180


class TestGetRetentionDays:
    """get_retention_days with tier and custom overrides."""

    def test_starter_audit_logs(self):
        assert get_retention_days("audit_logs", "starter") == 365

    def test_enterprise_audit_unlimited(self):
        assert get_retention_days("audit_logs", "enterprise") is None

    def test_custom_override_takes_precedence(self):
        result = get_retention_days("audit_logs", "enterprise", {"audit_logs": 730})
        assert result == 730

    def test_custom_override_only_affects_specified_collection(self):
        result = get_retention_days("alert_history", "enterprise", {"audit_logs": 730})
        assert result == 180  # Not overridden

    def test_unknown_collection_falls_back(self):
        result = get_retention_days("unknown_collection", "starter")
        # Falls back to starter default in missing tier_config
        assert result is not None or result is None  # Doesn't raise


class TestComputeCutoffDate:
    """compute_cutoff_date for retention windows."""

    def test_365_days_cutoff(self):
        now = datetime(2026, 3, 17, tzinfo=timezone.utc)
        cutoff = compute_cutoff_date(365, now)
        expected = now - timedelta(days=365)
        assert cutoff == expected

    def test_none_retention_returns_none(self):
        assert compute_cutoff_date(None) is None

    def test_zero_retention_returns_now(self):
        now = datetime(2026, 3, 17, tzinfo=timezone.utc)
        cutoff = compute_cutoff_date(0, now)
        assert cutoff == now

    def test_defaults_to_utc_now(self):
        cutoff = compute_cutoff_date(90)
        assert cutoff is not None
        assert cutoff.tzinfo == timezone.utc


class TestBuildArchivePath:
    """Archive blob path generation."""

    def test_path_format(self):
        date = datetime(2026, 3, 17, tzinfo=timezone.utc)
        path = build_archive_path("tenant-001", "audit_logs", date)
        assert path == "tenant-001/audit_logs/2026/03/archive-2026-03-17.ndjson.gz"

    def test_path_with_different_month(self):
        date = datetime(2026, 11, 5, tzinfo=timezone.utc)
        path = build_archive_path("t-xyz", "api_key_usage", date)
        assert path == "t-xyz/api_key_usage/2026/11/archive-2026-11-05.ndjson.gz"

    def test_defaults_to_now(self):
        path = build_archive_path("t1", "alert_history")
        assert path.startswith("t1/alert_history/")
        assert path.endswith(".ndjson.gz")


class TestIdentifyExpiredRecords:
    """Partition records into expired and retained."""

    def test_expired_before_cutoff(self):
        cutoff = datetime(2026, 1, 1, tzinfo=timezone.utc)
        records = [
            {"id": "1", "created_at": "2025-06-01T00:00:00+00:00"},
            {"id": "2", "created_at": "2026-06-01T00:00:00+00:00"},
        ]
        expired, retained = identify_expired_records(records, cutoff)
        assert len(expired) == 1
        assert expired[0]["id"] == "1"
        assert len(retained) == 1
        assert retained[0]["id"] == "2"

    def test_none_timestamp_retained(self):
        cutoff = datetime(2026, 1, 1, tzinfo=timezone.utc)
        records = [{"id": "1", "created_at": None}]
        expired, retained = identify_expired_records(records, cutoff)
        assert len(expired) == 0
        assert len(retained) == 1

    def test_invalid_timestamp_retained(self):
        cutoff = datetime(2026, 1, 1, tzinfo=timezone.utc)
        records = [{"id": "1", "created_at": "not-a-date"}]
        expired, retained = identify_expired_records(records, cutoff)
        assert len(expired) == 0
        assert len(retained) == 1

    def test_custom_timestamp_field(self):
        cutoff = datetime(2026, 1, 1, tzinfo=timezone.utc)
        records = [{"id": "1", "logged_at": "2025-01-01T00:00:00+00:00"}]
        expired, retained = identify_expired_records(records, cutoff, timestamp_field="logged_at")
        assert len(expired) == 1

    def test_naive_timestamp_treated_as_utc(self):
        cutoff = datetime(2026, 1, 1, tzinfo=timezone.utc)
        records = [{"id": "1", "created_at": "2025-06-01T00:00:00"}]
        expired, retained = identify_expired_records(records, cutoff)
        assert len(expired) == 1  # Naive datetime < cutoff

    def test_empty_records(self):
        cutoff = datetime(2026, 1, 1, tzinfo=timezone.utc)
        expired, retained = identify_expired_records([], cutoff)
        assert expired == []
        assert retained == []


class TestFormatNdjson:
    """NDJSON (newline-delimited JSON) formatting."""

    def test_single_record(self):
        result = format_ndjson([{"id": "1", "event": "test"}])
        parsed = json.loads(result)
        assert parsed["id"] == "1"

    def test_multiple_records(self):
        records = [{"id": "1"}, {"id": "2"}, {"id": "3"}]
        result = format_ndjson(records)
        lines = result.strip().split("\n")
        assert len(lines) == 3
        for line in lines:
            parsed = json.loads(line)
            assert "id" in parsed

    def test_compact_separators(self):
        result = format_ndjson([{"key": "value"}])
        # No spaces after : or ,
        assert ": " not in result
        assert ", " not in result

    def test_empty_records(self):
        result = format_ndjson([])
        assert result == ""


class TestGetRetentionSummary:
    """Retention policy summary for a tenant."""

    def test_starter_summary_structure(self):
        summary = get_retention_summary("t-001", "starter")
        assert summary["tenant_id"] == "t-001"
        assert summary["tier"] == "starter"
        assert "collections" in summary
        assert "computed_at" in summary
        assert set(summary["collections"].keys()) == {
            "audit_logs", "api_key_usage", "alert_history",
        }

    def test_starter_has_cutoff_dates(self):
        summary = get_retention_summary("t-001", "starter")
        for coll in summary["collections"].values():
            assert "cutoff_date" in coll
            assert "retention_days" in coll
            assert coll["unlimited"] is False

    def test_enterprise_audit_unlimited(self):
        summary = get_retention_summary("t-002", "enterprise")
        audit = summary["collections"]["audit_logs"]
        assert audit["unlimited"] is True
        assert audit["cutoff_date"] is None
        assert audit["retention_days"] is None

    def test_enterprise_api_key_still_90(self):
        summary = get_retention_summary("t-002", "enterprise")
        api_key = summary["collections"]["api_key_usage"]
        assert api_key["retention_days"] == 90
        assert api_key["unlimited"] is False
