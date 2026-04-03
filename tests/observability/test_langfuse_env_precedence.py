"""Slice 0c: S248 Langfuse environment variable precedence tests.

Verifies LANGFUSE_HOST vs LANGFUSE_BASE_URL fallback behavior at line 194
of src/observability/langfuse_exporter.py:
    host = os.getenv("LANGFUSE_HOST") or os.getenv("LANGFUSE_BASE_URL", "http://localhost:3000")

Test plan ref: COMPREHENSIVE-TEST-PLAN-S245-S255.md Slice 0c

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import os
import pytest
from unittest.mock import patch


def _resolve_host(env: dict[str, str]) -> str:
    """Replicate the inline host resolution logic from langfuse_exporter.py:194."""
    return env.get("LANGFUSE_HOST") or env.get("LANGFUSE_BASE_URL", "http://localhost:3000")


class TestLangfuseEnvPrecedence:
    """Env var precedence for Langfuse base URL resolution."""

    def test_langfuse_host_only(self):
        """LANGFUSE_HOST is used as base URL when set alone."""
        env = {"LANGFUSE_HOST": "https://custom.langfuse.com"}
        assert _resolve_host(env) == "https://custom.langfuse.com"

    def test_langfuse_base_url_only(self):
        """LANGFUSE_BASE_URL used as fallback when LANGFUSE_HOST not set."""
        env = {"LANGFUSE_BASE_URL": "https://fallback.langfuse.com"}
        assert _resolve_host(env) == "https://fallback.langfuse.com"

    def test_langfuse_host_wins_over_base_url(self):
        """When both set, LANGFUSE_HOST takes precedence."""
        env = {
            "LANGFUSE_HOST": "https://primary.langfuse.com",
            "LANGFUSE_BASE_URL": "https://fallback.langfuse.com",
        }
        assert _resolve_host(env) == "https://primary.langfuse.com"

    def test_neither_set_uses_default(self):
        """When neither is set, falls back to http://localhost:3000."""
        env: dict[str, str] = {}
        assert _resolve_host(env) == "http://localhost:3000"

    def test_empty_host_falls_through(self):
        """Empty LANGFUSE_HOST (falsy) falls through to BASE_URL."""
        env = {
            "LANGFUSE_HOST": "",
            "LANGFUSE_BASE_URL": "https://fallback.langfuse.com",
        }
        assert _resolve_host(env) == "https://fallback.langfuse.com"

    def test_source_code_matches_test_logic(self):
        """Verify the actual source line matches our replicated logic."""
        import inspect
        from src.observability import langfuse_exporter
        source = inspect.getsource(langfuse_exporter)
        # The canonical line we're testing
        assert 'os.getenv("LANGFUSE_HOST") or os.getenv("LANGFUSE_BASE_URL"' in source
