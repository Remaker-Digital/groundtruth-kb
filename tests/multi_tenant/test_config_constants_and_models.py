"""Tests for CONFIG specs — TTL constants, Pydantic config models, and tier gate ranking.

Covers 11 specs:
  - 7 TTL constants in cosmos_schema.py
  - 3 Pydantic models in config/models.py (ConfigReadResult, ConfigVersionInfo, ConfigRollbackResult)
  - 1 internal dict _GATE_RANK in schema/validation.py

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations


# ---------------------------------------------------------------------------
# TTL Constants (cosmos_schema.py)
# ---------------------------------------------------------------------------


class TestTTLConstants:
    """Verify TTL constants have the correct values in seconds."""

    def test_ttl_usage_period_is_35_days(self):
        from src.multi_tenant.cosmos_schema import TTL_USAGE_PERIOD

        assert TTL_USAGE_PERIOD == 35 * 24 * 60 * 60
        assert TTL_USAGE_PERIOD == 3_024_000

    def test_ttl_pack_balance_is_90_days(self):
        from src.multi_tenant.cosmos_schema import TTL_PACK_BALANCE

        assert TTL_PACK_BALANCE == 90 * 24 * 60 * 60
        assert TTL_PACK_BALANCE == 7_776_000

    def test_ttl_sla_snapshots_is_90_days(self):
        from src.multi_tenant.cosmos_schema import TTL_SLA_SNAPSHOTS

        assert TTL_SLA_SNAPSHOTS == 90 * 24 * 60 * 60
        assert TTL_SLA_SNAPSHOTS == 7_776_000

    def test_ttl_verification_token_is_10_minutes(self):
        from src.multi_tenant.cosmos_schema import TTL_VERIFICATION_TOKEN

        assert TTL_VERIFICATION_TOKEN == 10 * 60
        assert TTL_VERIFICATION_TOKEN == 600

    def test_ttl_incidents_is_1_year(self):
        from src.multi_tenant.cosmos_schema import TTL_INCIDENTS

        assert TTL_INCIDENTS == 365 * 24 * 60 * 60
        assert TTL_INCIDENTS == 31_536_000

    def test_ttl_alert_history_is_90_days(self):
        from src.multi_tenant.cosmos_schema import TTL_ALERT_HISTORY

        assert TTL_ALERT_HISTORY == 90 * 24 * 60 * 60
        assert TTL_ALERT_HISTORY == 7_776_000

    def test_ttl_ingestion_jobs_is_30_days(self):
        from src.multi_tenant.cosmos_schema import TTL_INGESTION_JOBS

        assert TTL_INGESTION_JOBS == 30 * 24 * 60 * 60
        assert TTL_INGESTION_JOBS == 2_592_000


# ---------------------------------------------------------------------------
# Pydantic Config Models (config/models.py)
# ---------------------------------------------------------------------------


class TestConfigReadResult:
    """Verify ConfigReadResult instantiation and fields."""

    def test_instantiation_with_required_fields(self):
        from src.multi_tenant.config.models import ConfigReadResult

        result = ConfigReadResult(
            tenant_id="t-test-001",
            tier="starter",
            version=1,
            config={"brand_name": "Test Brand"},
        )
        assert result.tenant_id == "t-test-001"
        assert result.tier == "starter"
        assert result.version == 1
        assert result.config == {"brand_name": "Test Brand"}

    def test_from_cache_defaults_to_false(self):
        from src.multi_tenant.config.models import ConfigReadResult

        result = ConfigReadResult(
            tenant_id="t1", tier="starter", version=1, config={},
        )
        assert result.from_cache is False

    def test_from_cache_can_be_set_true(self):
        from src.multi_tenant.config.models import ConfigReadResult

        result = ConfigReadResult(
            tenant_id="t1", tier="starter", version=1, config={}, from_cache=True,
        )
        assert result.from_cache is True


class TestConfigVersionInfo:
    """Verify ConfigVersionInfo instantiation and fields."""

    def test_instantiation_with_required_fields(self):
        from src.multi_tenant.config.models import ConfigVersionInfo

        info = ConfigVersionInfo(
            version=3,
            is_current=True,
            created_at="2026-01-15T10:00:00Z",
        )
        assert info.version == 3
        assert info.is_current is True
        assert info.created_at == "2026-01-15T10:00:00Z"

    def test_optional_fields_default_to_none_or_zero(self):
        from src.multi_tenant.config.models import ConfigVersionInfo

        info = ConfigVersionInfo(
            version=1, is_current=False, created_at="2026-01-01T00:00:00Z",
        )
        assert info.created_by is None
        assert info.field_count == 0
        assert info.config_name is None

    def test_all_fields_populated(self):
        from src.multi_tenant.config.models import ConfigVersionInfo

        info = ConfigVersionInfo(
            version=5,
            is_current=False,
            created_at="2026-02-01T12:00:00Z",
            created_by="admin@test.com",
            field_count=42,
            config_name="Holiday Config",
        )
        assert info.created_by == "admin@test.com"
        assert info.field_count == 42
        assert info.config_name == "Holiday Config"


class TestConfigRollbackResult:
    """Verify ConfigRollbackResult instantiation and fields."""

    def test_instantiation_with_required_fields(self):
        from src.multi_tenant.config.models import ConfigRollbackResult

        result = ConfigRollbackResult(
            success=True,
            from_version=5,
            to_version=3,
            new_version=6,
        )
        assert result.success is True
        assert result.from_version == 5
        assert result.to_version == 3
        assert result.new_version == 6

    def test_message_defaults_to_empty(self):
        from src.multi_tenant.config.models import ConfigRollbackResult

        result = ConfigRollbackResult(
            success=True, from_version=2, to_version=1, new_version=3,
        )
        assert result.message == ""

    def test_message_can_be_set(self):
        from src.multi_tenant.config.models import ConfigRollbackResult

        result = ConfigRollbackResult(
            success=False,
            from_version=2,
            to_version=1,
            new_version=3,
            message="Rollback failed: version not found",
        )
        assert result.message == "Rollback failed: version not found"


# ---------------------------------------------------------------------------
# Tier Gate Ranking (schema/validation.py)
# ---------------------------------------------------------------------------


class TestGateRank:
    """Verify _GATE_RANK maps TierGate enum values to correct rank ordering."""

    def test_gate_rank_has_four_entries(self):
        from src.multi_tenant.schema.validation import _GATE_RANK

        assert len(_GATE_RANK) == 4

    def test_gate_rank_ordering(self):
        """ALL < PROFESSIONAL_PLUS < ENTERPRISE_ONLY."""
        from src.multi_tenant.schema.models import TierGate
        from src.multi_tenant.schema.validation import _GATE_RANK

        assert _GATE_RANK[TierGate.ALL] == 0
        assert _GATE_RANK[TierGate.PROFESSIONAL_PLUS] == 1
        assert _GATE_RANK[TierGate.ENTERPRISE_ONLY] == 2

    def test_gate_rank_all_is_lowest(self):
        from src.multi_tenant.schema.models import TierGate
        from src.multi_tenant.schema.validation import _GATE_RANK

        all_rank = _GATE_RANK[TierGate.ALL]
        for gate, rank in _GATE_RANK.items():
            assert rank >= all_rank
