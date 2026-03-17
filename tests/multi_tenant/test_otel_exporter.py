"""Tests for SPEC-1834: OpenTelemetry Exporter to Application Insights.

Verifies exporter configuration, graceful no-op, tenant context in spans,
and sampling rate configuration.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

import pytest


class TestOTELExporterConfiguration:
    """SPEC-1834: Application Insights exporter wiring."""

    def test_exporter_configured_when_connection_string_present(self):
        """TEST-10441: AzureMonitorTraceExporter configured with connection string."""
        from src.multi_tenant.otel_application_insights import configure_exporter

        with patch.dict(os.environ, {
            "APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=test-key;IngestionEndpoint=https://eastus.in.ai"
        }):
            with patch("src.multi_tenant.otel_application_insights.AzureMonitorTraceExporter") as mock_cls:
                result = configure_exporter()

                mock_cls.assert_called_once()
                assert result["configured"] is True

    def test_graceful_noop_when_connection_string_absent(self):
        """TEST-10442: No exporter configured when env var absent, no errors."""
        from src.multi_tenant.otel_application_insights import configure_exporter

        with patch.dict(os.environ, {}, clear=True):
            # Remove the env var if present
            os.environ.pop("APPLICATIONINSIGHTS_CONNECTION_STRING", None)

            result = configure_exporter()

            assert result["configured"] is False
            assert "error" not in result

    def test_sampling_rate_default_10_percent(self):
        """SPEC-1834 req 7: Default sampling rate 0.1 (10%)."""
        from src.multi_tenant.otel_application_insights import get_sampling_rate

        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("OTEL_SAMPLING_RATE", None)
            rate = get_sampling_rate()
            assert rate == 0.1

    def test_sampling_rate_configurable(self):
        """SPEC-1834 req 7: Sampling rate configurable via env var."""
        from src.multi_tenant.otel_application_insights import get_sampling_rate

        with patch.dict(os.environ, {"OTEL_SAMPLING_RATE": "0.5"}):
            rate = get_sampling_rate()
            assert rate == 0.5


class TestOTELTenantContext:
    """SPEC-1834: Traces include tenant context."""

    def test_spans_include_tenant_id(self):
        """TEST-10443: Exported span includes tenant_id as custom dimension."""
        from src.multi_tenant.otel_tracing import TenantSpanProcessor

        processor = TenantSpanProcessor()
        mock_span = MagicMock()
        mock_span.set_attribute = MagicMock()

        # Simulate span with tenant context
        processor._current_tenant_id = "tenant-001"
        processor._current_conversation_id = "conv-abc"
        processor.on_start(mock_span, parent_context=None)

        # Verify tenant_id set as attribute
        calls = {call[0][0]: call[0][1] for call in mock_span.set_attribute.call_args_list}
        assert "tenant_id" in calls or "tenant.id" in calls

    def test_no_pii_in_telemetry(self):
        """SPEC-1834 req 10: No PII in exported telemetry."""
        # tenant_id is acceptable, email/name is not
        from src.multi_tenant.otel_tracing import OTEL_ATTRIBUTES

        pii_fields = {"email", "name", "phone", "address", "password", "api_key"}
        for attr in OTEL_ATTRIBUTES:
            assert attr not in pii_fields, f"PII field {attr} found in OTEL attributes"
