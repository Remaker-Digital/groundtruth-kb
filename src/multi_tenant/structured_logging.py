"""Structured logging standardization (WI #149).

Provides a JSON-structured log formatter and configuration helper that
ensures all log output follows a consistent machine-parseable format.

Log format (JSON per line):
    {
        "timestamp": "2026-01-31T12:34:56.789Z",
        "level": "INFO",
        "logger": "src.multi_tenant.middleware",
        "message": "Rate limit exceeded",
        "tenant_id": "abc123",
        "conversation_id": "conv-456",
        "trace_id": "trace-789",
        "extra": { ... }
    }

Tenant context fields (tenant_id, conversation_id, trace_id) are injected
automatically by TenantLogFilter (from otel_tracing.py) when available.

Configuration:
    Call configure_structured_logging() at application startup to replace
    the default Python logging configuration with structured JSON output.
    The ENVIRONMENT variable controls format:
        - "development": human-readable colored output (default)
        - "production" / "staging": JSON structured output

Architecture references:
    - Decision #11: OpenTelemetry with tenant_id on all telemetry
    - Decision #12: Correlation ID chain (conversation_id + tenant_id + trace_id)
    - otel_tracing.py: TenantLogFilter injects context fields

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any


# ---------------------------------------------------------------------------
# JSON structured formatter
# ---------------------------------------------------------------------------


class StructuredJsonFormatter(logging.Formatter):
    """JSON log formatter that outputs one JSON object per log line.

    Includes standard fields (timestamp, level, logger, message) plus
    any tenant context injected by TenantLogFilter.
    """

    def format(self, record: logging.LogRecord) -> str:
        log_entry: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc,
            ).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Tenant context fields (injected by TenantLogFilter in otel_tracing.py)
        for field in ("tenant_id", "conversation_id", "trace_id"):
            value = getattr(record, field, None)
            if value:
                log_entry[field] = value

        # Include exception info if present
        if record.exc_info and record.exc_info[0] is not None:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Include any extra fields passed via logger.info("msg", extra={...})
        standard_attrs = {
            "name", "msg", "args", "created", "relativeCreated",
            "exc_info", "exc_text", "stack_info", "lineno", "funcName",
            "pathname", "filename", "module", "thread", "threadName",
            "process", "processName", "levelname", "levelno", "message",
            "msecs", "tenant_id", "conversation_id", "trace_id",
            "taskName",
        }
        extras = {
            k: v for k, v in record.__dict__.items()
            if k not in standard_attrs and not k.startswith("_")
        }
        if extras:
            log_entry["extra"] = extras

        return json.dumps(log_entry, default=str)


# ---------------------------------------------------------------------------
# Human-readable formatter for development
# ---------------------------------------------------------------------------


class DevelopmentFormatter(logging.Formatter):
    """Colored, human-readable log formatter for development use.

    Format: TIMESTAMP [LEVEL] logger: message [tenant=X conv=Y trace=Z]
    """

    COLORS = {
        "DEBUG": "\033[36m",      # Cyan
        "INFO": "\033[32m",       # Green
        "WARNING": "\033[33m",    # Yellow
        "ERROR": "\033[31m",      # Red
        "CRITICAL": "\033[41m",   # Red background
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, "")
        reset = self.RESET if color else ""

        # Base message
        msg = (
            f"{self.formatTime(record)} "
            f"{color}[{record.levelname}]{reset} "
            f"{record.name}: {record.getMessage()}"
        )

        # Append tenant context if available
        ctx_parts = []
        for field in ("tenant_id", "conversation_id", "trace_id"):
            value = getattr(record, field, None)
            if value:
                short = value[:8] if len(str(value)) > 8 else value
                ctx_parts.append(f"{field}={short}")

        if ctx_parts:
            msg += f" [{' '.join(ctx_parts)}]"

        if record.exc_info and record.exc_info[0] is not None:
            msg += "\n" + self.formatException(record.exc_info)

        return msg


# ---------------------------------------------------------------------------
# Configuration helper
# ---------------------------------------------------------------------------


def configure_structured_logging(
    level: str | None = None,
    force_json: bool = False,
) -> None:
    """Configure application-wide structured logging.

    Args:
        level: Log level override (DEBUG, INFO, WARNING, ERROR).
            Defaults to LOG_LEVEL env var or INFO.
        force_json: If True, always use JSON format regardless of
            ENVIRONMENT setting.

    In production/staging: JSON structured format (one JSON object per line).
    In development: colored human-readable format.
    """
    log_level = (level or os.environ.get("LOG_LEVEL", "INFO")).upper()
    environment = os.environ.get("ENVIRONMENT", "development").lower()

    # Choose formatter
    use_json = force_json or environment in ("production", "staging")

    if use_json:
        formatter = StructuredJsonFormatter()
    else:
        formatter = DevelopmentFormatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        )

    # Configure root logger
    root = logging.getLogger()
    root.setLevel(getattr(logging, log_level, logging.INFO))

    # Replace existing handlers
    for handler in root.handlers[:]:
        root.removeHandler(handler)

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    root.addHandler(handler)

    # Quiet noisy third-party loggers
    for noisy in ("httpx", "httpcore", "azure", "opentelemetry"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
