"""
OpenTelemetry Application Insights exporter integration (SPEC-1834).

Provides AzureMonitorTraceExporter wiring for shipping telemetry to
Application Insights. Graceful no-op when APPLICATIONINSIGHTS_CONNECTION_STRING
is absent — allows local/staging environments to run without App Insights.

Configuration:
    APPLICATIONINSIGHTS_CONNECTION_STRING — Azure Monitor ingestion endpoint.
    OTEL_SAMPLING_RATE — Float 0.0-1.0, default 0.1 (10%). Controls trace
        sampling to manage telemetry volume and cost.

Custom dimensions included on every span (via TenantSpanProcessor in
otel_tracing.py): tenant_id, conversation_id, trace_id.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

# Default sampling rate: 10% of traces
_DEFAULT_SAMPLING_RATE = 0.1

# Attribute names exported to App Insights (PII-free by design)
OTEL_ATTRIBUTES = [
    "tenant.id",
    "conversation.id",
    "correlation.trace_id",
    "tenant.auth_method",
    "tenant.tier",
    "pipeline.agent",
    "llm.prompt_tokens",
    "llm.completion_tokens",
    "llm.total_tokens",
    "llm.model",
    "llm.estimated_cost_usd",
]


def get_sampling_rate() -> float:
    """Return the configured OTEL sampling rate (SPEC-1834).

    Reads OTEL_SAMPLING_RATE from environment. Defaults to 0.1 (10%).
    Clamps to [0.0, 1.0] range for safety.

    Returns:
        Sampling rate as a float between 0.0 and 1.0.
    """
    raw = os.environ.get("OTEL_SAMPLING_RATE")
    if raw is None:
        return _DEFAULT_SAMPLING_RATE
    try:
        rate = float(raw)
        return max(0.0, min(1.0, rate))
    except (ValueError, TypeError):
        logger.warning(
            "Invalid OTEL_SAMPLING_RATE='%s', using default %s",
            raw,
            _DEFAULT_SAMPLING_RATE,
        )
        return _DEFAULT_SAMPLING_RATE


def configure_exporter() -> dict[str, Any]:
    """Configure the Azure Monitor trace exporter (SPEC-1834, WI-1453).

    Reads APPLICATIONINSIGHTS_CONNECTION_STRING from environment. If present,
    creates an AzureMonitorTraceExporter and returns configuration details.
    If absent, returns a no-op result with no errors.

    Returns:
        Dict with keys:
            configured (bool): Whether the exporter was successfully created.
            exporter: The AzureMonitorTraceExporter instance, or None.
            sampling_rate (float): The configured sampling rate.
            error (str): Only present if configuration failed due to an error.
    """
    connection_string = os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING")
    sampling_rate = get_sampling_rate()

    if not connection_string:
        logger.info(
            "APPLICATIONINSIGHTS_CONNECTION_STRING not set — "
            "Application Insights exporter disabled (no-op)"
        )
        return {
            "configured": False,
            "exporter": None,
            "sampling_rate": sampling_rate,
        }

    try:
        from azure.monitor.opentelemetry.exporter import (
            AzureMonitorTraceExporter,
        )

        exporter = AzureMonitorTraceExporter(
            connection_string=connection_string,
        )

        logger.info(
            "Application Insights exporter configured: "
            "sampling_rate=%.2f batch_interval=5s",
            sampling_rate,
        )

        return {
            "configured": True,
            "exporter": exporter,
            "sampling_rate": sampling_rate,
        }

    except ImportError:
        logger.warning(
            "azure-monitor-opentelemetry-exporter not installed — "
            "Application Insights exporter disabled"
        )
        return {
            "configured": False,
            "exporter": None,
            "sampling_rate": sampling_rate,
            "error": "azure-monitor-opentelemetry-exporter not installed",
        }
    except Exception as exc:
        logger.error(
            "Failed to configure Application Insights exporter: %s",
            exc,
        )
        return {
            "configured": False,
            "exporter": None,
            "sampling_rate": sampling_rate,
            "error": str(exc),
        }


# ---------------------------------------------------------------------------
# Custom metrics (SPEC-1834 req 6)
# ---------------------------------------------------------------------------

# Lazy-initialized metric instruments — created by configure_metrics().
_request_duration_histogram: Any = None
_llm_token_counter: Any = None
_cosmos_ru_counter: Any = None
_active_sse_gauge: Any = None


def configure_metrics() -> dict[str, Any]:
    """Configure OpenTelemetry custom metrics for Application Insights (SPEC-1834 req 6).

    Creates four metric instruments:
        - request_duration_ms: Histogram of HTTP request durations.
        - llm_token_count: Counter of LLM tokens consumed (prompt + completion).
        - cosmos_ru_consumed: Counter of Cosmos DB request units consumed.
        - active_sse_connections: UpDownCounter of active SSE connections.

    When APPLICATIONINSIGHTS_CONNECTION_STRING is set, exports metrics to
    Application Insights via AzureMonitorMetricExporter. Otherwise, metrics
    are collected in-memory only (useful for testing).

    Returns:
        Dict with keys: configured (bool), instruments (dict of metric names).
    """
    global _request_duration_histogram, _llm_token_counter
    global _cosmos_ru_counter, _active_sse_gauge

    from opentelemetry import metrics

    meter = metrics.get_meter("agent-red", "1.0.0")

    _request_duration_histogram = meter.create_histogram(
        name="request_duration_ms",
        description="HTTP request duration in milliseconds",
        unit="ms",
    )

    _llm_token_counter = meter.create_counter(
        name="llm_token_count",
        description="Total LLM tokens consumed (prompt + completion)",
        unit="tokens",
    )

    _cosmos_ru_counter = meter.create_counter(
        name="cosmos_ru_consumed",
        description="Cosmos DB request units consumed",
        unit="RU",
    )

    _active_sse_gauge = meter.create_up_down_counter(
        name="active_sse_connections",
        description="Current number of active SSE connections",
        unit="connections",
    )

    # Wire metrics exporter for App Insights if connection string present
    connection_string = os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING")
    configured = False
    if connection_string:
        try:
            from azure.monitor.opentelemetry.exporter import (
                AzureMonitorMetricExporter,
            )
            from opentelemetry.sdk.metrics import MeterProvider
            from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

            metric_reader = PeriodicExportingMetricReader(
                AzureMonitorMetricExporter(connection_string=connection_string),
                export_interval_millis=5000,
            )
            provider = MeterProvider(metric_readers=[metric_reader])
            metrics.set_meter_provider(provider)
            configured = True
            logger.info("Application Insights metrics exporter configured")
        except ImportError:
            logger.warning(
                "azure-monitor-opentelemetry-exporter not installed — "
                "metrics collected in-memory only"
            )
        except Exception as exc:
            logger.warning("Failed to configure metrics exporter: %s", exc)

    return {
        "configured": configured,
        "instruments": {
            "request_duration_ms": _request_duration_histogram,
            "llm_token_count": _llm_token_counter,
            "cosmos_ru_consumed": _cosmos_ru_counter,
            "active_sse_connections": _active_sse_gauge,
        },
    }


def record_request_duration(duration_ms: float, **attributes: Any) -> None:
    """Record an HTTP request duration (SPEC-1834 req 6)."""
    if _request_duration_histogram is not None:
        _request_duration_histogram.record(duration_ms, attributes=attributes)


def record_llm_tokens(token_count: int, **attributes: Any) -> None:
    """Record LLM tokens consumed (SPEC-1834 req 6)."""
    if _llm_token_counter is not None:
        _llm_token_counter.add(token_count, attributes=attributes)


def record_cosmos_ru(ru_consumed: float, **attributes: Any) -> None:
    """Record Cosmos DB request units consumed (SPEC-1834 req 6)."""
    if _cosmos_ru_counter is not None:
        _cosmos_ru_counter.add(ru_consumed, attributes=attributes)


def record_sse_connection(delta: int, **attributes: Any) -> None:
    """Record SSE connection change (+1 on connect, -1 on disconnect) (SPEC-1834 req 6)."""
    if _active_sse_gauge is not None:
        _active_sse_gauge.add(delta, attributes=attributes)


def configure_tracing_with_app_insights() -> dict[str, Any]:
    """Configure OpenTelemetry tracing with Application Insights export.

    Integrates with the existing configure_tracing() from otel_tracing.py.
    When App Insights is configured, passes the AzureMonitorTraceExporter
    as the exporter. When not configured, falls back to the default
    (console exporter in dev, no-op otherwise).

    Returns:
        Configuration result dict from configure_exporter().
    """
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    from src.multi_tenant.otel_tracing import configure_tracing

    result = configure_exporter()

    if result["configured"] and result["exporter"] is not None:
        # Configure tracing with App Insights exporter
        provider = configure_tracing(exporter=result["exporter"])

        # Apply sampling rate via TraceIdRatioBased sampler
        sampling_rate = result["sampling_rate"]
        if sampling_rate < 1.0:
            try:
                from opentelemetry.sdk.trace.sampling import (
                    TraceIdRatioBased,
                )

                # Re-create provider with sampler
                from opentelemetry import trace
                from opentelemetry.sdk.resources import Resource

                resource = provider.resource
                sampled_provider = TracerProvider(
                    resource=resource,
                    sampler=TraceIdRatioBased(sampling_rate),
                )
                # Re-add processors from original provider
                for processor in provider._active_span_processor._span_processors:
                    sampled_provider.add_span_processor(processor)
                trace.set_tracer_provider(sampled_provider)

                logger.info(
                    "Trace sampling configured: rate=%.2f",
                    sampling_rate,
                )
            except Exception as exc:
                logger.warning(
                    "Failed to configure trace sampling: %s — "
                    "all traces will be exported",
                    exc,
                )
    else:
        # No App Insights — use default tracing config
        configure_tracing()

    # Configure custom metrics (SPEC-1834 req 6) regardless of exporter
    metrics_result = configure_metrics()
    result["metrics_configured"] = metrics_result["configured"]

    return result
