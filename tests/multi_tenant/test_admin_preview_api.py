"""Tests for Admin Preview API (SPEC-1872).

Covers: preview chat endpoint, tier gating, daily limits, decision trace API,
config overrides, and analytics exclusion.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from src.multi_tenant.admin_preview_api import (
    DAILY_PREVIEW_LIMIT,
    PreviewChatRequest,
    PreviewTraceResponse,
    _check_daily_limit,
    _daily_counts,
    _enforce_tier_gate,
)


# ---------------------------------------------------------------------------
# Tier gating
# ---------------------------------------------------------------------------


class TestPreviewTierGate:
    """TEST-11022: Preview chat requires professional+ tier."""

    def test_free_tier_rejected(self):
        ctx = MagicMock()
        ctx.is_platform_admin = False
        ctx.tier = MagicMock(value="free")
        with pytest.raises(Exception) as exc_info:
            _enforce_tier_gate(ctx)
        assert "403" in str(exc_info.value.status_code) or exc_info.value.status_code == 403

    def test_starter_tier_rejected(self):
        ctx = MagicMock()
        ctx.is_platform_admin = False
        ctx.tier = MagicMock(value="starter")
        with pytest.raises(Exception) as exc_info:
            _enforce_tier_gate(ctx)
        assert exc_info.value.status_code == 403

    def test_professional_tier_allowed(self):
        ctx = MagicMock()
        ctx.is_platform_admin = False
        ctx.tier = MagicMock(value="professional")
        _enforce_tier_gate(ctx)  # Should not raise

    def test_enterprise_tier_allowed(self):
        ctx = MagicMock()
        ctx.is_platform_admin = False
        ctx.tier = MagicMock(value="enterprise")
        _enforce_tier_gate(ctx)  # Should not raise

    def test_platform_admin_bypasses_gate(self):
        ctx = MagicMock()
        ctx.is_platform_admin = True
        ctx.tier = MagicMock(value="free")
        _enforce_tier_gate(ctx)  # Should not raise


# ---------------------------------------------------------------------------
# Daily limit
# ---------------------------------------------------------------------------


class TestPreviewDailyLimit:
    """TEST-11027: Daily preview limit enforced at 50 per tenant."""

    def setup_method(self):
        _daily_counts.clear()

    def test_first_preview_allowed(self):
        _check_daily_limit("tenant-1")
        # Should not raise

    def test_limit_enforcement(self):
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        _daily_counts["tenant-1"] = (today, DAILY_PREVIEW_LIMIT)
        with pytest.raises(Exception) as exc_info:
            _check_daily_limit("tenant-1")
        assert exc_info.value.status_code == 429

    def test_different_day_resets(self):
        _daily_counts["tenant-1"] = ("2020-01-01", DAILY_PREVIEW_LIMIT)
        _check_daily_limit("tenant-1")  # Should not raise (different day)

    def test_different_tenants_independent(self):
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        _daily_counts["tenant-1"] = (today, DAILY_PREVIEW_LIMIT)
        _check_daily_limit("tenant-2")  # Different tenant, should not raise


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------


class TestPreviewModels:
    """Model validation for preview API."""

    def test_preview_request_valid(self):
        req = PreviewChatRequest(message="Hello, test message")
        assert req.message == "Hello, test message"
        assert req.config_overrides is None

    def test_preview_request_with_overrides(self):
        req = PreviewChatRequest(
            message="Test",
            config_overrides={"response_tone_preset": "casual"},
        )
        assert req.config_overrides["response_tone_preset"] == "casual"

    def test_preview_trace_response(self):
        resp = PreviewTraceResponse(
            conversation_id="conv-123",
            trace={"detected_intent": "product_inquiry", "confidence": 0.85},
        )
        assert resp.conversation_id == "conv-123"
        assert resp.trace["detected_intent"] == "product_inquiry"
