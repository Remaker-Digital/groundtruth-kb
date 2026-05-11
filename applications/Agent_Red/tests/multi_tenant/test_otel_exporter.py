"""Tests for SPEC-1834: OpenTelemetry Exporter to Application Insights.

Verifies exporter configuration, graceful no-op, tenant context in spans,
and sampling rate configuration.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import os
from unittest.mock import MagicMock, patch



class TestOTELExporterConfiguration:
    """SPEC-1834: Application Insights exporter wiring."""

    def test_exporter_configured_when_connection_string_present(self):
        """TEST-10441: AzureMonitorTraceExporter configured with connection string."""
        from src.multi_tenant.otel_application_insights import configure_exporter

        mock_exporter_instance = MagicMock()
        mock_exporter_cls = MagicMock(return_value=mock_exporter_instance)

        # Mock the azure.monitor package so the local import inside
        # configure_exporter() picks up our mock class.
        mock_azure_module = MagicMock(
            AzureMonitorTraceExporter=mock_exporter_cls,
        )

        with patch.dict(os.environ, {
            "APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=test-key;IngestionEndpoint=https://eastus.in.ai"
        }):
            with patch.dict("sys.modules", {
                "azure.monitor.opentelemetry.exporter": mock_azure_module,
            }):
                result = configure_exporter()

                assert result["configured"] is True
                assert result["exporter"] is mock_exporter_instance

    def test_graceful_noop_when_connection_string_absent(self):
        """TEST-10442: No exporter configured when env var absent, no errors."""
        from src.multi_tenant.otel_application_insights import configure_exporter

        env = {k: v for k, v in os.environ.items()
               if k != "APPLICATIONINSIGHTS_CONNECTION_STRING"}

        with patch.dict(os.environ, env, clear=True):
            result = configure_exporter()

            assert result["configured"] is False
            assert "error" not in result

    def test_graceful_noop_when_package_not_installed(self):
        """SPEC-1834: Graceful degradation when azure-monitor package missing."""
        from src.multi_tenant.otel_application_insights import configure_exporter

        with patch.dict(os.environ, {
            "APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=test-key"
        }):
            # Force ImportError by removing the module
            with patch.dict("sys.modules", {
                "azure.monitor.opentelemetry.exporter": None,
            }):
                result = configure_exporter()

                assert result["configured"] is False
                assert "error" in result
                assert "not installed" in result["error"]


class TestSamplingRate:
    """SPEC-1834: Sampling rate configuration."""

    def test_sampling_rate_default_10_percent(self):
        """SPEC-1834 req 7: Default sampling rate 0.1 (10%)."""
        from src.multi_tenant.otel_application_insights import get_sampling_rate

        env = {k: v for k, v in os.environ.items() if k != "OTEL_SAMPLING_RATE"}
        with patch.dict(os.environ, env, clear=True):
            rate = get_sampling_rate()
            assert rate == 0.1

    def test_sampling_rate_configurable(self):
        """SPEC-1834 req 7: Sampling rate configurable via env var."""
        from src.multi_tenant.otel_application_insights import get_sampling_rate

        with patch.dict(os.environ, {"OTEL_SAMPLING_RATE": "0.5"}):
            rate = get_sampling_rate()
            assert rate == 0.5

    def test_sampling_rate_clamped_high(self):
        """SPEC-1834: Sampling rate clamped to max 1.0."""
        from src.multi_tenant.otel_application_insights import get_sampling_rate

        with patch.dict(os.environ, {"OTEL_SAMPLING_RATE": "2.0"}):
            rate = get_sampling_rate()
            assert rate == 1.0

    def test_sampling_rate_clamped_low(self):
        """SPEC-1834: Sampling rate clamped to min 0.0."""
        from src.multi_tenant.otel_application_insights import get_sampling_rate

        with patch.dict(os.environ, {"OTEL_SAMPLING_RATE": "-0.5"}):
            rate = get_sampling_rate()
            assert rate == 0.0

    def test_sampling_rate_invalid_falls_back(self):
        """SPEC-1834: Invalid sampling rate string uses default."""
        from src.multi_tenant.otel_application_insights import get_sampling_rate

        with patch.dict(os.environ, {"OTEL_SAMPLING_RATE": "not-a-number"}):
            rate = get_sampling_rate()
            assert rate == 0.1


class TestOTELTenantContext:
    """SPEC-1834: Traces include tenant context."""

    def test_spans_include_tenant_id(self):
        """TEST-10443: Exported span includes tenant_id as custom dimension."""
        from src.multi_tenant.otel_tracing import (
            CorrelationContext,
            TenantSpanProcessor,
            set_correlation_context,
            clear_correlation_context,
        )

        processor = TenantSpanProcessor()
        mock_span = MagicMock()

        # Set correlation context (the proper API)
        set_correlation_context(CorrelationContext(
            tenant_id="tenant-001",
            conversation_id="conv-abc",
        ))

        try:
            processor.on_start(mock_span, parent_context=None)

            calls = {
                call[0][0]: call[0][1]
                for call in mock_span.set_attribute.call_args_list
            }
            assert "tenant.id" in calls
            assert calls["tenant.id"] == "tenant-001"
            assert "conversation.id" in calls
            assert calls["conversation.id"] == "conv-abc"
        finally:
            clear_correlation_context()

    def test_no_pii_in_telemetry_attributes(self):
        """SPEC-1834 req 10: No PII in exported telemetry."""
        from src.multi_tenant.otel_application_insights import OTEL_ATTRIBUTES

        pii_fields = {"email", "name", "phone", "address", "password", "api_key"}
        for attr in OTEL_ATTRIBUTES:
            parts = attr.split(".")
            for part in parts:
                assert part not in pii_fields, (
                    f"PII field '{part}' found in OTEL attribute '{attr}'"
                )

    def test_spans_without_context_are_clean(self):
        """SPEC-1834: Spans created without tenant context have no tenant attrs."""
        from src.multi_tenant.otel_tracing import (
            TenantSpanProcessor,
            clear_correlation_context,
        )

        clear_correlation_context()
        processor = TenantSpanProcessor()
        mock_span = MagicMock()

        processor.on_start(mock_span, parent_context=None)

        # No set_attribute calls when no correlation context
        mock_span.set_attribute.assert_not_called()


class TestCustomMetrics:
    """SPEC-1834 req 6: Custom metrics for Application Insights."""

    def test_configure_metrics_creates_four_instruments(self):
        """SPEC-1834 req 6: Four metric instruments are created."""
        from src.multi_tenant.otel_application_insights import configure_metrics

        env = {k: v for k, v in os.environ.items()
               if k != "APPLICATIONINSIGHTS_CONNECTION_STRING"}
        with patch.dict(os.environ, env, clear=True):
            result = configure_metrics()

        assert result["configured"] is False  # No connection string
        instruments = result["instruments"]
        assert "request_duration_ms" in instruments
        assert "llm_token_count" in instruments
        assert "cosmos_ru_consumed" in instruments
        assert "active_sse_connections" in instruments
        # All instruments should be non-None (created by meter)
        for name, inst in instruments.items():
            assert inst is not None, f"Instrument {name} is None"

    def test_record_request_duration(self):
        """SPEC-1834 req 6: request_duration_ms histogram records values."""
        from src.multi_tenant.otel_application_insights import (
            configure_metrics,
            record_request_duration,
        )

        env = {k: v for k, v in os.environ.items()
               if k != "APPLICATIONINSIGHTS_CONNECTION_STRING"}
        with patch.dict(os.environ, env, clear=True):
            configure_metrics()

        # Should not raise even without App Insights
        record_request_duration(42.5, tenant_id="t-001", method="GET")

    def test_record_llm_tokens(self):
        """SPEC-1834 req 6: llm_token_count counter records values."""
        from src.multi_tenant.otel_application_insights import (
            configure_metrics,
            record_llm_tokens,
        )

        env = {k: v for k, v in os.environ.items()
               if k != "APPLICATIONINSIGHTS_CONNECTION_STRING"}
        with patch.dict(os.environ, env, clear=True):
            configure_metrics()

        record_llm_tokens(1500, tenant_id="t-001", model="gpt-4o")

    def test_record_cosmos_ru(self):
        """SPEC-1834 req 6: cosmos_ru_consumed counter records values."""
        from src.multi_tenant.otel_application_insights import (
            configure_metrics,
            record_cosmos_ru,
        )

        env = {k: v for k, v in os.environ.items()
               if k != "APPLICATIONINSIGHTS_CONNECTION_STRING"}
        with patch.dict(os.environ, env, clear=True):
            configure_metrics()

        record_cosmos_ru(3.14, tenant_id="t-001", operation="query")

    def test_record_sse_connection(self):
        """SPEC-1834 req 6: active_sse_connections gauge tracks deltas."""
        from src.multi_tenant.otel_application_insights import (
            configure_metrics,
            record_sse_connection,
        )

        env = {k: v for k, v in os.environ.items()
               if k != "APPLICATIONINSIGHTS_CONNECTION_STRING"}
        with patch.dict(os.environ, env, clear=True):
            configure_metrics()

        # Connect
        record_sse_connection(+1, tenant_id="t-001")
        # Disconnect
        record_sse_connection(-1, tenant_id="t-001")

    def test_record_functions_safe_before_configure(self):
        """SPEC-1834: Record functions are no-ops when metrics not configured."""
        import src.multi_tenant.otel_application_insights as mod

        # Reset module-level instruments
        original = (
            mod._request_duration_histogram,
            mod._llm_token_counter,
            mod._cosmos_ru_counter,
            mod._active_sse_gauge,
        )
        mod._request_duration_histogram = None
        mod._llm_token_counter = None
        mod._cosmos_ru_counter = None
        mod._active_sse_gauge = None

        try:
            # Should not raise when instruments are None
            mod.record_request_duration(10.0)
            mod.record_llm_tokens(100)
            mod.record_cosmos_ru(2.0)
            mod.record_sse_connection(1)
        finally:
            (
                mod._request_duration_histogram,
                mod._llm_token_counter,
                mod._cosmos_ru_counter,
                mod._active_sse_gauge,
            ) = original


class TestBatchExportInterval:
    """SPEC-1834 req 8: Batch export interval 5 seconds."""

    def test_batch_processor_uses_5s_interval(self):
        """SPEC-1834 req 8: BatchSpanProcessor configured with 5000ms interval."""

        from src.multi_tenant.otel_tracing import configure_tracing

        mock_exporter = MagicMock()

        with patch(
            "src.multi_tenant.otel_tracing.BatchSpanProcessor"
        ) as mock_bsp_cls:
            mock_bsp_cls.return_value = MagicMock()
            configure_tracing(exporter=mock_exporter)

            mock_bsp_cls.assert_called_once_with(
                mock_exporter, schedule_delay_millis=5000
            )
