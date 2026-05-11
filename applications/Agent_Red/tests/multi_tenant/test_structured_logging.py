"""Tests for structured logging — JSON formatter, dev formatter, configuration.

Covers:
    - StructuredJsonFormatter: JSON output, tenant context fields, exception info, extras
    - DevelopmentFormatter: colored output, context truncation
    - configure_structured_logging: env-aware formatter selection, noisy logger quieting

Run:
    pytest tests/multi_tenant/test_structured_logging.py -v

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
import logging
import os
from unittest.mock import patch


from src.multi_tenant.structured_logging import (
    DevelopmentFormatter,
    StructuredJsonFormatter,
    configure_structured_logging,
)


# ---------------------------------------------------------------------------
# SL-01 to SL-04: StructuredJsonFormatter
# ---------------------------------------------------------------------------


class TestStructuredJsonFormatter:
    """JSON log formatter output validation."""

    def _make_record(
        self,
        message: str = "test message",
        level: int = logging.INFO,
        **extras: object,
    ) -> logging.LogRecord:
        """Create a log record with optional tenant context."""
        record = logging.LogRecord(
            name="test.logger",
            level=level,
            pathname="test.py",
            lineno=1,
            msg=message,
            args=(),
            exc_info=None,
        )
        for k, v in extras.items():
            setattr(record, k, v)
        return record

    def test_sl_01_basic_json_output(self):
        """Formatter outputs valid JSON with standard fields."""
        formatter = StructuredJsonFormatter()
        record = self._make_record("Hello world")
        output = formatter.format(record)

        parsed = json.loads(output)
        assert parsed["level"] == "INFO"
        assert parsed["logger"] == "test.logger"
        assert parsed["message"] == "Hello world"
        assert "timestamp" in parsed

    def test_sl_02_tenant_context_included(self):
        """Tenant context fields are included when present."""
        formatter = StructuredJsonFormatter()
        record = self._make_record(
            "request",
            tenant_id="tenant-abc",
            conversation_id="conv-123",
            trace_id="trace-xyz",
        )
        output = formatter.format(record)
        parsed = json.loads(output)

        assert parsed["tenant_id"] == "tenant-abc"
        assert parsed["conversation_id"] == "conv-123"
        assert parsed["trace_id"] == "trace-xyz"

    def test_sl_03_tenant_context_absent_when_not_set(self):
        """Tenant context fields are omitted when not on the record."""
        formatter = StructuredJsonFormatter()
        record = self._make_record("no context")
        output = formatter.format(record)
        parsed = json.loads(output)

        assert "tenant_id" not in parsed
        assert "conversation_id" not in parsed
        assert "trace_id" not in parsed

    def test_sl_04_exception_info_formatted(self):
        """Exception info is included in the JSON output."""
        formatter = StructuredJsonFormatter()
        try:
            raise ValueError("test error")
        except ValueError:
            import sys
            record = self._make_record("error occurred", level=logging.ERROR)
            record.exc_info = sys.exc_info()

        output = formatter.format(record)
        parsed = json.loads(output)

        assert "exception" in parsed
        assert "ValueError" in parsed["exception"]
        assert "test error" in parsed["exception"]

    def test_sl_05_extras_captured(self):
        """Extra fields passed via logger are captured."""
        formatter = StructuredJsonFormatter()
        record = self._make_record("with extras", custom_field="custom_value")
        output = formatter.format(record)
        parsed = json.loads(output)

        assert "extra" in parsed
        assert parsed["extra"]["custom_field"] == "custom_value"


# ---------------------------------------------------------------------------
# SL-06 to SL-07: DevelopmentFormatter
# ---------------------------------------------------------------------------


class TestDevelopmentFormatter:
    """Development (colored) formatter output."""

    def _make_record(self, message: str = "dev test", **extras: object) -> logging.LogRecord:
        record = logging.LogRecord(
            name="test.dev",
            level=logging.WARNING,
            pathname="test.py",
            lineno=1,
            msg=message,
            args=(),
            exc_info=None,
        )
        for k, v in extras.items():
            setattr(record, k, v)
        return record

    def test_sl_06_includes_level_and_message(self):
        """Dev formatter includes level and message in output."""
        formatter = DevelopmentFormatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        )
        record = self._make_record("warning msg")
        output = formatter.format(record)

        assert "WARNING" in output
        assert "warning msg" in output
        assert "test.dev" in output

    def test_sl_07_tenant_context_truncated(self):
        """Tenant context fields are truncated to 8 chars."""
        formatter = DevelopmentFormatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        )
        record = self._make_record(
            "ctx test",
            tenant_id="remaker-digital-001",
        )
        output = formatter.format(record)

        # Should contain truncated tenant_id (first 8 chars)
        assert "tenant_id=remaker-" in output
        # Should NOT contain the full ID
        assert "remaker-digital-001" not in output


# ---------------------------------------------------------------------------
# SL-08 to SL-10: configure_structured_logging
# ---------------------------------------------------------------------------


class TestConfigureLogging:
    """Logging configuration helper."""

    def test_sl_08_production_uses_json_formatter(self):
        """Production environment selects JSON formatter."""
        with patch.dict(os.environ, {"ENVIRONMENT": "production", "LOG_LEVEL": "INFO"}):
            configure_structured_logging()

        root = logging.getLogger()
        assert len(root.handlers) == 1
        assert isinstance(root.handlers[0].formatter, StructuredJsonFormatter)

    def test_sl_09_development_uses_colored_formatter(self):
        """Development environment selects colored formatter."""
        with patch.dict(os.environ, {"ENVIRONMENT": "development", "LOG_LEVEL": "DEBUG"}):
            configure_structured_logging()

        root = logging.getLogger()
        assert len(root.handlers) == 1
        assert isinstance(root.handlers[0].formatter, DevelopmentFormatter)

    def test_sl_10_force_json_overrides_environment(self):
        """force_json=True uses JSON even in development."""
        with patch.dict(os.environ, {"ENVIRONMENT": "development"}):
            configure_structured_logging(force_json=True)

        root = logging.getLogger()
        assert len(root.handlers) == 1
        assert isinstance(root.handlers[0].formatter, StructuredJsonFormatter)

    def test_sl_11_noisy_loggers_quieted(self):
        """Third-party loggers are set to WARNING level."""
        with patch.dict(os.environ, {"ENVIRONMENT": "development"}):
            configure_structured_logging()

        for name in ("httpx", "httpcore", "azure", "opentelemetry"):
            assert logging.getLogger(name).level == logging.WARNING
