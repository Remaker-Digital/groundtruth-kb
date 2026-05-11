# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
OpenTelemetry tenant-aware tracing and correlation ID propagation.

Implements Decisions #11-12 and Work Items #39-40. Ensures every span,
log record, and NATS message carries tenant_id + conversation_id +
trace_id, enabling per-tenant observability in Application Insights.

1. TenantSpanProcessor (Decision #11, WI #39):
   Injects tenant_id and conversation_id as span attributes on every
   span before export. Application Insights exposes these as custom
   dimensions for filtering, alerting, and per-tenant dashboards.

2. TenantLogProcessor (Decision #11, WI #39):
   Injects tenant_id into log records so Application Insights log
   queries can filter by tenant.

3. Correlation ID propagation (Decision #12, WI #40):
   - CorrelationContext: frozen dataclass carrying the correlation triple
     (tenant_id + conversation_id + trace_id) through the pipeline.
   - Context variable (_correlation_ctx) for async-safe propagation within
     a single request lifecycle.
   - NATS header injection/extraction (built on nats_isolation.py helpers).
   - FastAPI middleware integration to set correlation context on every
     authenticated request.

PII safety:
   Correlation IDs are PII-free by design. tenant_id is a UUID, not a
   customer identifier. conversation_id is an internal tracking ID.
   trace_id is an OpenTelemetry trace identifier. No customer names,
   emails, or other PII ever appears in telemetry attributes.

Architecture references:
    - Decision #11: tenant_id on all Application Insights telemetry
    - Decision #12: Correlation ID chain (conversation_id + tenant_id + trace_id)
    - Decision #7: PII scrubbing (telemetry must be PII-free)
    - NATS correlation headers: X-Tenant-Id, X-Conversation-Id, X-Trace-Id

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import contextvars
import logging
import os
from dataclasses import dataclass
from typing import Any

from opentelemetry import trace
from opentelemetry.context import Context
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import ReadableSpan, Span, SpanProcessor, TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
    SpanExporter,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Attribute keys for Application Insights custom dimensions
ATTR_TENANT_ID = "tenant.id"
ATTR_CONVERSATION_ID = "conversation.id"
ATTR_TRACE_ID = "correlation.trace_id"
ATTR_AUTH_METHOD = "tenant.auth_method"
ATTR_TIER = "tenant.tier"
ATTR_AGENT = "pipeline.agent"

# LLM token/cost attributes (SPEC-1540)
ATTR_LLM_PROMPT_TOKENS = "llm.prompt_tokens"
ATTR_LLM_COMPLETION_TOKENS = "llm.completion_tokens"
ATTR_LLM_TOTAL_TOKENS = "llm.total_tokens"
ATTR_LLM_MODEL = "llm.model"
ATTR_LLM_COST_USD = "llm.estimated_cost_usd"

# Service identification
SERVICE_NAME = "agent-red"
SERVICE_VERSION = "1.0.0"

# Environment
OTEL_EXPORTER_TYPE = os.environ.get("OTEL_EXPORTER_TYPE", "console")


# ---------------------------------------------------------------------------
# Correlation context (Decision #12)
# ---------------------------------------------------------------------------

# Async-safe context variable — set once per request, read by SpanProcessor
_correlation_ctx: contextvars.ContextVar[CorrelationContext | None] = (
    contextvars.ContextVar("_correlation_ctx", default=None)
)


@dataclass(frozen=True)
class CorrelationContext:
    """Carries the correlation ID triple through the request lifecycle.

    Set by middleware at the start of each request. Read by
    TenantSpanProcessor to inject attributes into every span
    created during that request.

    Fields:
        tenant_id: Tenant UUID (from TenantContext after auth).
        conversation_id: Conversation thread ID (from request body
            or NATS message headers). May be None for non-conversation
            requests (e.g., config updates, billing).
        trace_id: OpenTelemetry trace ID (hex string, auto-generated
            if not propagated from upstream).
        auth_method: How the tenant was authenticated (shopify_session, api_key).
        tier: Tenant subscription tier (starter, professional, enterprise).
    """

    tenant_id: str
    conversation_id: str | None = None
    trace_id: str | None = None
    auth_method: str | None = None
    tier: str | None = None


def set_correlation_context(ctx: CorrelationContext) -> None:
    """Set the correlation context for the current async task.

    Called by middleware after authentication resolves the tenant.
    """
    _correlation_ctx.set(ctx)


def get_correlation_context() -> CorrelationContext | None:
    """Get the correlation context for the current async task.

    Returns None if no context has been set (e.g., health check
    endpoints that skip authentication).
    """
    return _correlation_ctx.get()


def clear_correlation_context() -> None:
    """Clear the correlation context after request completion."""
    _correlation_ctx.set(None)


# ---------------------------------------------------------------------------
# TenantSpanProcessor (Decision #11, Work Item #39)
# ---------------------------------------------------------------------------


class TenantSpanProcessor(SpanProcessor):
    """OpenTelemetry SpanProcessor that injects tenant context into spans.

    Intercepts every span at start time and adds tenant_id,
    conversation_id, and trace metadata as span attributes. These
    attributes appear as custom dimensions in Application Insights,
    enabling per-tenant filtering, alerting, and dashboards.

    Processing order:
        1. Read CorrelationContext from the contextvars context.
        2. If present, set tenant attributes on the span.
        3. Delegate to the wrapped exporter for actual export.

    Usage:
        provider = TracerProvider()
        provider.add_span_processor(TenantSpanProcessor())
        provider.add_span_processor(BatchSpanProcessor(exporter))
        trace.set_tracer_provider(provider)

    Thread/async safety:
        CorrelationContext is stored in a contextvars.ContextVar, which
        is natively async-safe in Python's asyncio model. Each coroutine
        chain has its own context copy.
    """

    def on_start(self, span: Span, parent_context: Context | None = None) -> None:
        """Inject tenant context attributes when a span starts."""
        ctx = get_correlation_context()
        if ctx is None:
            return

        span.set_attribute(ATTR_TENANT_ID, ctx.tenant_id)

        if ctx.conversation_id:
            span.set_attribute(ATTR_CONVERSATION_ID, ctx.conversation_id)

        if ctx.trace_id:
            span.set_attribute(ATTR_TRACE_ID, ctx.trace_id)

        if ctx.auth_method:
            span.set_attribute(ATTR_AUTH_METHOD, ctx.auth_method)

        if ctx.tier:
            span.set_attribute(ATTR_TIER, ctx.tier)

    def on_end(self, span: ReadableSpan) -> None:
        """No-op — attribute injection happens at start time."""

    def shutdown(self) -> None:
        """No-op — no resources to release."""

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        """No-op — this processor doesn't buffer."""
        return True


# ---------------------------------------------------------------------------
# TenantLogProcessor (Decision #11, Work Item #39)
# ---------------------------------------------------------------------------


class TenantLogFilter(logging.Filter):
    """Python logging filter that injects tenant context into log records.

    Adds tenant_id, conversation_id, and trace_id to every log record
    as extra attributes. When Application Insights collects Python logs,
    these attributes appear as custom dimensions.

    Usage:
        handler = logging.StreamHandler()
        handler.addFilter(TenantLogFilter())
        logging.root.addHandler(handler)

    The filter also enriches the log format string. Use the formatter:
        "%(asctime)s [%(levelname)s] %(name)s [tenant=%(tenant_id)s] %(message)s"
    """

    def filter(self, record: logging.LogRecord) -> bool:
        """Inject tenant context into the log record. Always returns True."""
        ctx = get_correlation_context()

        if ctx is not None:
            record.tenant_id = ctx.tenant_id  # type: ignore[attr-defined]
            record.conversation_id = ctx.conversation_id or "-"  # type: ignore[attr-defined]
            record.trace_id = ctx.trace_id or "-"  # type: ignore[attr-defined]
        else:
            record.tenant_id = "-"  # type: ignore[attr-defined]
            record.conversation_id = "-"  # type: ignore[attr-defined]
            record.trace_id = "-"  # type: ignore[attr-defined]

        return True


# ---------------------------------------------------------------------------
# LLM Cost Attribution Model (SPEC-1540)
# ---------------------------------------------------------------------------

# Azure OpenAI pricing per 1K tokens (as of 2026-02, East US)
# These rates are updated periodically and should match the Azure pricing page.
LLM_COST_PER_1K_TOKENS: dict[str, dict[str, float]] = {
    "gpt-4o": {"prompt": 0.005, "completion": 0.015},
    "gpt-4o-mini": {"prompt": 0.00015, "completion": 0.0006},
    "gpt-4o-2024-11-20": {"prompt": 0.005, "completion": 0.015},
    "text-embedding-3-small": {"prompt": 0.00002, "completion": 0.0},
    "text-embedding-3-large": {"prompt": 0.00013, "completion": 0.0},
}


def calculate_llm_cost(
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
) -> float:
    """Calculate estimated USD cost for an LLM API call (SPEC-1540).

    Args:
        model: Model identifier (e.g., "gpt-4o", "gpt-4o-mini").
        prompt_tokens: Number of input tokens.
        completion_tokens: Number of output tokens.

    Returns:
        Estimated cost in USD. Returns 0.0 for unknown models.
    """
    rates = LLM_COST_PER_1K_TOKENS.get(model)
    if rates is None:
        return 0.0
    prompt_cost = (prompt_tokens / 1000) * rates["prompt"]
    completion_cost = (completion_tokens / 1000) * rates["completion"]
    return round(prompt_cost + completion_cost, 8)


def record_token_usage(
    span: trace.Span,
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
) -> float:
    """Record LLM token usage and cost on a span (SPEC-1540).

    Sets llm.prompt_tokens, llm.completion_tokens, llm.total_tokens,
    llm.model, and llm.estimated_cost_usd as span attributes.

    Args:
        span: The OpenTelemetry span to annotate.
        model: Model identifier.
        prompt_tokens: Number of input tokens.
        completion_tokens: Number of output tokens.

    Returns:
        Estimated cost in USD.
    """
    total = prompt_tokens + completion_tokens
    cost = calculate_llm_cost(model, prompt_tokens, completion_tokens)

    span.set_attribute(ATTR_LLM_MODEL, model)
    span.set_attribute(ATTR_LLM_PROMPT_TOKENS, prompt_tokens)
    span.set_attribute(ATTR_LLM_COMPLETION_TOKENS, completion_tokens)
    span.set_attribute(ATTR_LLM_TOTAL_TOKENS, total)
    span.set_attribute(ATTR_LLM_COST_USD, cost)

    return cost


# ---------------------------------------------------------------------------
# Agent-scoped tracing helper
# ---------------------------------------------------------------------------


def trace_agent_operation(
    agent: str,
    operation: str,
    conversation_id: str | None = None,
) -> trace.Span:
    """Create a span for an agent pipeline operation (SPEC-1539).

    Convenience function for instrumenting agent processing steps.
    Automatically includes the current correlation context. Used by
    pipeline dispatch methods to create parent-child span trees.

    Args:
        agent: Agent name (e.g., "intent-classifier", "response-generator").
        operation: Operation name (e.g., "classify", "generate", "validate").
        conversation_id: Override conversation_id for this span (optional).

    Returns:
        An OpenTelemetry Span (use as context manager).

    Usage:
        with trace_agent_operation("intent-classifier", "classify") as span:
            result = await classify_intent(message)
            span.set_attribute("intent.result", result.intent)
            record_token_usage(span, "gpt-4o-mini", result.prompt_tokens, result.completion_tokens)
    """
    tracer = trace.get_tracer(SERVICE_NAME, SERVICE_VERSION)
    span = tracer.start_span(
        name=f"{agent}.{operation}",
        attributes={ATTR_AGENT: agent},
    )

    # Inject correlation context
    ctx = get_correlation_context()
    if ctx is not None:
        span.set_attribute(ATTR_TENANT_ID, ctx.tenant_id)
        if conversation_id or ctx.conversation_id:
            span.set_attribute(
                ATTR_CONVERSATION_ID,
                conversation_id or ctx.conversation_id,
            )

    return span


def trace_pipeline_root(
    conversation_id: str | None = None,
) -> trace.Span:
    """Create the root span for a pipeline execution (SPEC-1541).

    This is the top-level span that all agent operation spans are
    children of. It represents the full pipeline.process lifecycle
    from intent classification through response delivery.

    Args:
        conversation_id: Conversation ID for the pipeline run.

    Returns:
        An OpenTelemetry Span (use as context manager).
    """
    tracer = trace.get_tracer(SERVICE_NAME, SERVICE_VERSION)
    span = tracer.start_span(
        name="pipeline.process",
        attributes={ATTR_AGENT: "orchestrator"},
    )

    ctx = get_correlation_context()
    if ctx is not None:
        span.set_attribute(ATTR_TENANT_ID, ctx.tenant_id)
        if conversation_id or ctx.conversation_id:
            span.set_attribute(
                ATTR_CONVERSATION_ID,
                conversation_id or ctx.conversation_id,
            )
        if ctx.trace_id:
            span.set_attribute(ATTR_TRACE_ID, ctx.trace_id)

    return span


# ---------------------------------------------------------------------------
# Correlation middleware for FastAPI (Decision #12)
# ---------------------------------------------------------------------------


class CorrelationMiddleware:
    """ASGI middleware that sets CorrelationContext on every request.

    Reads the TenantContext set by TenantAuthMiddleware and creates
    a CorrelationContext for the duration of the request. This context
    is then available to TenantSpanProcessor and TenantLogFilter.

    Also reads optional headers for conversation_id propagation from
    upstream services or NATS message processing.

    Install after TenantAuthMiddleware:
        app.add_middleware(TenantAuthMiddleware)
        app.add_middleware(CorrelationMiddleware)

    Note: Because Starlette middleware runs in reverse order of
    add_middleware calls, CorrelationMiddleware should be added AFTER
    TenantAuthMiddleware so it executes AFTER auth resolves.
    """

    def __init__(self, app: Any) -> None:
        self.app = app

    async def __call__(self, scope: dict, receive: Any, send: Any) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Extract tenant context (set by TenantAuthMiddleware)
        # At the ASGI level, we access state via the scope
        request_state = scope.get("state", {})
        tenant_ctx = request_state.get("tenant_context") if request_state else None

        if tenant_ctx is not None:
            # Get current trace ID from OpenTelemetry
            current_span = trace.get_current_span()
            span_ctx = current_span.get_span_context()
            otel_trace_id = (
                format(span_ctx.trace_id, "032x")
                if span_ctx and span_ctx.trace_id
                else None
            )

            # Check for conversation_id in headers (from NATS or upstream)
            headers = dict(scope.get("headers", []))
            conversation_id = (
                headers.get(b"x-conversation-id", b"").decode("utf-8", errors="ignore")
                or None
            )

            correlation = CorrelationContext(
                tenant_id=tenant_ctx.tenant_id,
                conversation_id=conversation_id,
                trace_id=otel_trace_id,
                auth_method=tenant_ctx.auth_method,
                tier=tenant_ctx.tier.value if tenant_ctx.tier else None,
            )
            set_correlation_context(correlation)

        try:
            await self.app(scope, receive, send)
        finally:
            # Clear context after request completes
            clear_correlation_context()


# ---------------------------------------------------------------------------
# Provider setup
# ---------------------------------------------------------------------------


def configure_tracing(
    service_name: str = SERVICE_NAME,
    service_version: str = SERVICE_VERSION,
    exporter: SpanExporter | None = None,
) -> TracerProvider:
    """Configure OpenTelemetry tracing with tenant-aware processors.

    Sets up:
        1. TracerProvider with service resource attributes.
        2. TenantSpanProcessor for tenant_id injection.
        3. BatchSpanProcessor with the configured exporter.

    Args:
        service_name: Service name for resource identification.
        service_version: Service version.
        exporter: SpanExporter to use. Defaults to ConsoleSpanExporter
            in development, or None (no export) if not specified.

    Returns:
        The configured TracerProvider.

    Usage (FastAPI startup):
        @app.on_event("startup")
        async def startup():
            provider = configure_tracing()
            # Provider is automatically set as global
    """
    resource = Resource.create(
        attributes={
            "service.name": service_name,
            "service.version": service_version,
        }
    )

    provider = TracerProvider(resource=resource)

    # 1. Tenant context injection (runs on every span start)
    provider.add_span_processor(TenantSpanProcessor())

    # 2. Export processor
    if exporter is None:
        if OTEL_EXPORTER_TYPE == "console":
            exporter = ConsoleSpanExporter()
        # For Azure Application Insights, the azure-monitor-opentelemetry
        # package provides AzureMonitorTraceExporter. It will be configured
        # via the APPLICATIONINSIGHTS_CONNECTION_STRING env var when deployed.
        # That integration is added in the Terraform/deployment layer, not here.

    if exporter is not None:
        # SPEC-1834 req 8: batch export interval 5 seconds (explicit, not default)
        provider.add_span_processor(
            BatchSpanProcessor(exporter, schedule_delay_millis=5000)
        )

    # Set as global provider
    trace.set_tracer_provider(provider)

    logger.info(
        "OpenTelemetry tracing configured: service=%s version=%s "
        "exporter=%s tenant_processor=enabled",
        service_name, service_version,
        type(exporter).__name__ if exporter else "none",
    )

    return provider


def configure_logging(
    log_format: str | None = None,
) -> None:
    """Configure Python logging with tenant context injection.

    Adds TenantLogFilter to the root logger so every log record
    includes tenant_id, conversation_id, and trace_id attributes.

    Args:
        log_format: Optional format string. Defaults to a tenant-aware
            format with structured fields.
    """
    if log_format is None:
        log_format = (
            "%(asctime)s [%(levelname)s] %(name)s "
            "[tenant=%(tenant_id)s conv=%(conversation_id)s trace=%(trace_id)s] "
            "%(message)s"
        )

    tenant_filter = TenantLogFilter()

    # Add filter to root logger
    root_logger = logging.getLogger()
    root_logger.addFilter(tenant_filter)

    # Update formatter on existing handlers
    formatter = logging.Formatter(log_format)
    for handler in root_logger.handlers:
        handler.addFilter(tenant_filter)
        handler.setFormatter(formatter)

    logger.info("Tenant-aware logging configured")


# ---------------------------------------------------------------------------
# NATS correlation helpers (extends nats_isolation.py)
# ---------------------------------------------------------------------------


def correlation_to_nats_headers(
    ctx: CorrelationContext | None = None,
) -> dict[str, str]:
    """Convert a CorrelationContext to NATS message headers.

    If no context is provided, reads from the current async context.
    Compatible with nats_isolation.TenantNATSManager.publish(headers=...).

    Args:
        ctx: Optional CorrelationContext. Defaults to current context.

    Returns:
        Dict of NATS headers (X-Tenant-Id, X-Conversation-Id, X-Trace-Id).
    """
    if ctx is None:
        ctx = get_correlation_context()

    if ctx is None:
        return {}

    headers: dict[str, str] = {"X-Tenant-Id": ctx.tenant_id}
    if ctx.conversation_id:
        headers["X-Conversation-Id"] = ctx.conversation_id
    if ctx.trace_id:
        headers["X-Trace-Id"] = ctx.trace_id
    return headers


def nats_headers_to_correlation(
    headers: dict[str, str] | None,
) -> CorrelationContext | None:
    """Create a CorrelationContext from NATS message headers.

    Used when an agent receives a message from NATS and needs to
    restore the correlation context for the processing pipeline.

    Args:
        headers: NATS message headers.

    Returns:
        CorrelationContext, or None if required headers are missing.
    """
    if not headers:
        return None

    tenant_id = headers.get("X-Tenant-Id")
    if not tenant_id:
        return None

    return CorrelationContext(
        tenant_id=tenant_id,
        conversation_id=headers.get("X-Conversation-Id"),
        trace_id=headers.get("X-Trace-Id"),
    )


def restore_correlation_from_nats(
    headers: dict[str, str] | None,
) -> CorrelationContext | None:
    """Restore correlation context from NATS headers into the current task.

    Combines nats_headers_to_correlation() + set_correlation_context().
    Call this at the start of a NATS message handler to propagate
    correlation through the agent's processing pipeline.

    Args:
        headers: NATS message headers from the received message.

    Returns:
        The restored CorrelationContext, or None if headers are insufficient.

    Usage:
        async def handle_message(msg: Msg):
            ctx = restore_correlation_from_nats(msg.headers)
            if ctx:
                # All spans and logs in this handler will carry tenant context
                result = await process_message(msg)
    """
    ctx = nats_headers_to_correlation(headers)
    if ctx is not None:
        set_correlation_context(ctx)
    return ctx
