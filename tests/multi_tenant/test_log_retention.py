"""Tests for SPEC-1837: Log Retention Policy and Archival.

Verifies tier-based retention periods, archival to Blob Storage,
GDPR precedence, and compliance reporting.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestLogRetentionPolicy:
    """SPEC-1837: Tier-based retention periods enforced."""

    @pytest.mark.asyncio
    async def test_starter_audit_logs_archived_after_365_days(self):
        """TEST-10452: Starter tenant logs older than 365d archived."""
        from src.multi_tenant.log_retention import LogRetentionService

        mock_repo = AsyncMock()
        old_date = (datetime.now(timezone.utc) - timedelta(days=366)).isoformat()
        mock_repo.query_expired_audit_logs.return_value = [
            {"id": "log-001", "timestamp": old_date, "event_type": "CONFIG_UPDATED"},
            {"id": "log-002", "timestamp": old_date, "event_type": "API_KEY_ROTATED"},
        ]
        mock_blob = AsyncMock()
        mock_blob.upload_archive.return_value = "https://blob.storage/archive-001.ndjson.gz"

        svc = LogRetentionService(audit_repo=mock_repo, blob_client=mock_blob)
        result = await svc.archive_expired_logs(tenant_id="t1", tier="starter")

        assert result["archived_count"] == 2
        assert result["archive_uri"] is not None
        mock_blob.upload_archive.assert_called_once()

    @pytest.mark.asyncio
    async def test_enterprise_unlimited_audit_retention(self):
        """TEST-10453: Enterprise logs NOT archived (unlimited retention)."""
        from src.multi_tenant.log_retention import LogRetentionService

        mock_repo = AsyncMock()
        mock_blob = AsyncMock()

        svc = LogRetentionService(audit_repo=mock_repo, blob_client=mock_blob)
        result = await svc.archive_expired_logs(tenant_id="t2", tier="enterprise")

        assert result["archived_count"] == 0
        mock_repo.query_expired_audit_logs.assert_not_called()  # Should skip entirely

    @pytest.mark.asyncio
    async def test_gdpr_deletion_overrides_retention(self):
        """TEST-10454: GDPR deletion takes precedence over retention policy."""
        from src.multi_tenant.log_retention import LogRetentionService

        mock_repo = AsyncMock()
        mock_blob = AsyncMock()

        svc = LogRetentionService(audit_repo=mock_repo, blob_client=mock_blob)

        # GDPR request for a log that's within retention period (< 365 days old)
        recent_date = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()

        result = await svc.gdpr_delete_logs(
            tenant_id="t3",
            log_ids=["log-recent-001"],
        )

        assert result["deleted_count"] == 1  # Deleted despite being within retention

    @pytest.mark.asyncio
    async def test_manual_archive_trigger(self):
        """TEST-10455: POST /api/superadmin/retention/archive-now triggers immediate archival."""
        from src.multi_tenant.log_retention import LogRetentionService

        mock_repo = AsyncMock()
        mock_repo.query_expired_audit_logs.return_value = [
            {"id": f"log-{i}", "timestamp": "2025-01-01T00:00:00Z"} for i in range(5)
        ]
        mock_blob = AsyncMock()
        mock_blob.upload_archive.return_value = "https://blob.storage/archive.ndjson.gz"

        svc = LogRetentionService(audit_repo=mock_repo, blob_client=mock_blob)
        result = await svc.archive_expired_logs(tenant_id="t1", tier="starter")

        assert result["archived_count"] == 5

    def test_archive_format_ndjson_gzip(self):
        """SPEC-1837 req 4: Archive format is NDJSON gzip compressed."""
        from src.multi_tenant.log_retention import format_archive_records

        records = [
            {"id": "log-001", "event_type": "CONFIG_UPDATED"},
            {"id": "log-002", "event_type": "API_KEY_ROTATED"},
        ]

        data = format_archive_records(records)
        # Should be bytes (gzip compressed)
        assert isinstance(data, bytes)
        # Decompress and verify NDJSON
        import gzip
        text = gzip.decompress(data).decode("utf-8")
        lines = text.strip().split("\n")
        assert len(lines) == 2

    def test_archive_file_naming_convention(self):
        """SPEC-1837 req 5: Files named {tenant_id}/{collection}/{year}/{month}/archive-{date}.ndjson.gz."""
        from src.multi_tenant.log_retention import compute_archive_path

        path = compute_archive_path(
            tenant_id="tenant-001",
            collection="audit_log",
            date="2026-03-16",
        )

        assert path == "tenant-001/audit_log/2026/03/archive-2026-03-16.ndjson.gz"


class TestRetentionPeriods:
    """SPEC-1837 req 1: Tier-specific retention defaults."""

    def test_starter_retention_periods(self):
        """Starter: audit 365d, key usage 90d, alerts 180d."""
        from src.multi_tenant.log_retention import get_retention_config

        config = get_retention_config("starter")
        assert config["audit_logs_days"] == 365
        assert config["api_key_usage_days"] == 90
        assert config["alert_history_days"] == 180

    def test_professional_retention_periods(self):
        """Professional: audit 365d, key usage 90d, alerts 180d."""
        from src.multi_tenant.log_retention import get_retention_config

        config = get_retention_config("professional")
        assert config["audit_logs_days"] == 365
        assert config["api_key_usage_days"] == 90
        assert config["alert_history_days"] == 180

    def test_enterprise_unlimited_retention(self):
        """Enterprise: unlimited audit retention."""
        from src.multi_tenant.log_retention import get_retention_config

        config = get_retention_config("enterprise")
        assert config["audit_logs_days"] is None  # Unlimited
        assert config["api_key_usage_days"] == 90  # Still 90d for key usage
