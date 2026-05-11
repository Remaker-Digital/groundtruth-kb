"""CQ-7: Merchant quality configuration tests (SPEC-0186 / WI-1517).

Tests for MerchantQualityConfig, get_merchant_quality_config(), and
update_merchant_quality_config().

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from src.chat.quality_config import (
    DEFAULT_QUALITY_CONFIG,
    MerchantQualityConfig,
    get_merchant_quality_config,
    update_merchant_quality_config,
)


# ---------------------------------------------------------------------------
# Model validation
# ---------------------------------------------------------------------------


class TestMerchantQualityConfigModel:
    """MerchantQualityConfig model validates ranges."""

    def test_default_values(self):
        cfg = MerchantQualityConfig()
        assert cfg.quality_threshold == 3.5
        assert cfg.escalation_threshold == 2.5
        assert cfg.consecutive_low_turns == 3
        assert cfg.enable_quality_feedback is True
        assert cfg.enable_quality_escalation is True

    def test_custom_values(self):
        cfg = MerchantQualityConfig(
            quality_threshold=4.0,
            escalation_threshold=3.0,
            consecutive_low_turns=5,
            enable_quality_feedback=False,
            enable_quality_escalation=False,
        )
        assert cfg.quality_threshold == 4.0
        assert cfg.enable_quality_feedback is False

    def test_threshold_below_minimum_rejected(self):
        with pytest.raises(ValidationError):
            MerchantQualityConfig(quality_threshold=0.5)

    def test_threshold_above_maximum_rejected(self):
        with pytest.raises(ValidationError):
            MerchantQualityConfig(quality_threshold=6.0)

    def test_consecutive_turns_below_minimum_rejected(self):
        with pytest.raises(ValidationError):
            MerchantQualityConfig(consecutive_low_turns=0)

    def test_consecutive_turns_above_maximum_rejected(self):
        with pytest.raises(ValidationError):
            MerchantQualityConfig(consecutive_low_turns=11)


# ---------------------------------------------------------------------------
# get_merchant_quality_config
# ---------------------------------------------------------------------------


class TestGetConfig:
    """get_merchant_quality_config reads from tenant doc or returns defaults."""

    def test_none_tenant_doc_returns_defaults(self):
        result = get_merchant_quality_config(None)
        assert result == DEFAULT_QUALITY_CONFIG

    def test_empty_dict_returns_defaults(self):
        result = get_merchant_quality_config({})
        assert result == DEFAULT_QUALITY_CONFIG

    def test_no_quality_config_key_returns_defaults(self):
        result = get_merchant_quality_config({"name": "test-tenant"})
        assert result == DEFAULT_QUALITY_CONFIG

    def test_valid_quality_config_parsed(self):
        doc = {
            "quality_config": {
                "quality_threshold": 4.0,
                "escalation_threshold": 3.0,
                "consecutive_low_turns": 5,
            }
        }
        result = get_merchant_quality_config(doc)
        assert result.quality_threshold == 4.0
        assert result.escalation_threshold == 3.0
        assert result.consecutive_low_turns == 5
        # Defaults for unset fields
        assert result.enable_quality_feedback is True

    def test_invalid_quality_config_returns_defaults(self):
        doc = {"quality_config": {"quality_threshold": "invalid"}}
        result = get_merchant_quality_config(doc)
        assert result == DEFAULT_QUALITY_CONFIG

    def test_non_dict_quality_config_returns_defaults(self):
        doc = {"quality_config": "not a dict"}
        result = get_merchant_quality_config(doc)
        assert result == DEFAULT_QUALITY_CONFIG


# ---------------------------------------------------------------------------
# update_merchant_quality_config
# ---------------------------------------------------------------------------


class TestUpdateConfig:
    """update_merchant_quality_config merges config into tenant doc."""

    def test_update_adds_quality_config(self):
        doc = {"name": "test-tenant"}
        cfg = MerchantQualityConfig(quality_threshold=4.0)
        result = update_merchant_quality_config(doc, cfg)
        assert "quality_config" in result
        assert result["quality_config"]["quality_threshold"] == 4.0

    def test_update_overwrites_existing(self):
        doc = {"quality_config": {"quality_threshold": 3.0}}
        cfg = MerchantQualityConfig(quality_threshold=4.5)
        result = update_merchant_quality_config(doc, cfg)
        assert result["quality_config"]["quality_threshold"] == 4.5

    def test_update_preserves_other_keys(self):
        doc = {"name": "test-tenant", "tier": "professional"}
        cfg = MerchantQualityConfig()
        result = update_merchant_quality_config(doc, cfg)
        assert result["name"] == "test-tenant"
        assert result["tier"] == "professional"
        assert "quality_config" in result

    def test_roundtrip_serialization(self):
        cfg = MerchantQualityConfig(
            quality_threshold=4.2,
            enable_quality_feedback=False,
        )
        doc = update_merchant_quality_config({}, cfg)
        recovered = get_merchant_quality_config(doc)
        assert recovered.quality_threshold == 4.2
        assert recovered.enable_quality_feedback is False
