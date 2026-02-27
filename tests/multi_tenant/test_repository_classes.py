"""Tests for repository class existence, method signatures, and constants.

Covers infrastructure specs for repository layer:
    SPEC-1344: AlertRuleRepository.get_rule() returns dict | None
    SPEC-1357: CustomerProfileRepository class exists
    SPEC-1358: IncidentRepository.get_incident() returns dict | None
    SPEC-1361: IncidentRepository.list_all() returns list[dict]
    SPEC-1362: KnowledgeBaseRepository class exists
    SPEC-1365: AuditLogRepository class exists
    SPEC-1367: PreferencesRepository class exists
    SPEC-1368: PreferencesRepository.get_active() returns dict | None
    SPEC-1369: PreferencesRepository.get_draft() returns dict | None
    SPEC-1370: PreferencesRepository.get_previous() returns dict | None
    SPEC-1371: PreferencesRepository.get_current() returns dict | None
    SPEC-1372: PreferencesRepository.get_quick_actions() returns list[dict]
    SPEC-1373: PreferencesRepository.get_quick_actions_active() returns list[dict]
    SPEC-1375: SNAPSHOT_TYPE_DAILY = "daily"
    SPEC-1377: TenantRepository class exists
    SPEC-1380: TenantRepository.list_expiring_trials() returns list[dict]
    SPEC-1382: TenantRepository.list_expiring_tenants() returns list[dict]
    SPEC-1383: UsageRepository class exists

Total: 18 tests

These tests verify structural contracts (class existence, method presence,
async nature) without requiring Cosmos DB connectivity.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import inspect

import pytest


# ===================================================================
# SPEC-1344: AlertRuleRepository.get_rule() returns dict | None
# ===================================================================


class TestAlertRuleRepositoryGetRule:
    """SPEC-1344: alerts.get_rule() returns dict | None."""

    def test_alert_rule_repository_class_exists(self):
        """AlertRuleRepository is importable and is a class."""
        from src.multi_tenant.repositories.alerts import AlertRuleRepository
        assert isinstance(AlertRuleRepository, type)

    def test_get_rule_method_exists(self):
        """AlertRuleRepository has a get_rule method."""
        from src.multi_tenant.repositories.alerts import AlertRuleRepository
        assert hasattr(AlertRuleRepository, "get_rule")

    def test_get_rule_is_async(self):
        """AlertRuleRepository.get_rule is an async method."""
        from src.multi_tenant.repositories.alerts import AlertRuleRepository
        assert inspect.iscoroutinefunction(AlertRuleRepository.get_rule)

    def test_get_rule_signature_has_rule_id_and_rule_type(self):
        """get_rule accepts rule_id and rule_type parameters."""
        from src.multi_tenant.repositories.alerts import AlertRuleRepository
        sig = inspect.signature(AlertRuleRepository.get_rule)
        param_names = list(sig.parameters.keys())
        assert "rule_id" in param_names
        assert "rule_type" in param_names


# ===================================================================
# SPEC-1357: CustomerProfileRepository class exists
# ===================================================================


class TestCustomerProfileRepositoryExists:
    """SPEC-1357: CustomerProfileRepository class exists in customer.py."""

    def test_customer_profile_repository_class_exists(self):
        """CustomerProfileRepository is importable and is a class."""
        from src.multi_tenant.repositories.customer import CustomerProfileRepository
        assert isinstance(CustomerProfileRepository, type)

    def test_customer_profile_repository_is_tenant_scoped(self):
        """CustomerProfileRepository extends TenantScopedRepository."""
        from src.multi_tenant.repositories.customer import CustomerProfileRepository
        from src.multi_tenant.repositories.base import TenantScopedRepository
        assert issubclass(CustomerProfileRepository, TenantScopedRepository)


# ===================================================================
# SPEC-1358: IncidentRepository.get_incident() returns dict | None
# ===================================================================


class TestIncidentRepositoryGetIncident:
    """SPEC-1358: incidents.get_incident() returns dict | None."""

    def test_incident_repository_class_exists(self):
        """IncidentRepository is importable and is a class."""
        from src.multi_tenant.repositories.incidents import IncidentRepository
        assert isinstance(IncidentRepository, type)

    def test_get_incident_method_exists(self):
        """IncidentRepository has a get_incident method."""
        from src.multi_tenant.repositories.incidents import IncidentRepository
        assert hasattr(IncidentRepository, "get_incident")

    def test_get_incident_is_async(self):
        """IncidentRepository.get_incident is an async method."""
        from src.multi_tenant.repositories.incidents import IncidentRepository
        assert inspect.iscoroutinefunction(IncidentRepository.get_incident)

    def test_get_incident_signature_has_incident_id_and_status(self):
        """get_incident accepts incident_id and status parameters."""
        from src.multi_tenant.repositories.incidents import IncidentRepository
        sig = inspect.signature(IncidentRepository.get_incident)
        param_names = list(sig.parameters.keys())
        assert "incident_id" in param_names
        assert "status" in param_names


# ===================================================================
# SPEC-1361: IncidentRepository.list_all() returns list[dict]
# ===================================================================


class TestIncidentRepositoryListAll:
    """SPEC-1361: incidents.list_all() returns list[dict]."""

    def test_list_all_method_exists(self):
        """IncidentRepository has a list_all method."""
        from src.multi_tenant.repositories.incidents import IncidentRepository
        assert hasattr(IncidentRepository, "list_all")

    def test_list_all_is_async(self):
        """IncidentRepository.list_all is an async method."""
        from src.multi_tenant.repositories.incidents import IncidentRepository
        assert inspect.iscoroutinefunction(IncidentRepository.list_all)

    def test_list_all_has_limit_parameter(self):
        """list_all accepts a limit parameter with default 50."""
        from src.multi_tenant.repositories.incidents import IncidentRepository
        sig = inspect.signature(IncidentRepository.list_all)
        assert "limit" in sig.parameters
        assert sig.parameters["limit"].default == 50


# ===================================================================
# SPEC-1362: KnowledgeBaseRepository class exists
# ===================================================================


class TestKnowledgeBaseRepositoryExists:
    """SPEC-1362: KnowledgeBaseRepository class exists in knowledge.py."""

    def test_knowledge_base_repository_class_exists(self):
        """KnowledgeBaseRepository is importable and is a class."""
        from src.multi_tenant.repositories.knowledge import KnowledgeBaseRepository
        assert isinstance(KnowledgeBaseRepository, type)

    def test_knowledge_base_repository_is_tenant_scoped(self):
        """KnowledgeBaseRepository extends TenantScopedRepository."""
        from src.multi_tenant.repositories.knowledge import KnowledgeBaseRepository
        from src.multi_tenant.repositories.base import TenantScopedRepository
        assert issubclass(KnowledgeBaseRepository, TenantScopedRepository)


# ===================================================================
# SPEC-1365: AuditLogRepository class exists
# ===================================================================


class TestAuditLogRepositoryExists:
    """SPEC-1365: AuditLogRepository class exists in platform.py."""

    def test_audit_log_repository_class_exists(self):
        """AuditLogRepository is importable and is a class."""
        from src.multi_tenant.repositories.platform import AuditLogRepository
        assert isinstance(AuditLogRepository, type)

    def test_audit_log_repository_has_log_event(self):
        """AuditLogRepository has a log_event async method."""
        from src.multi_tenant.repositories.platform import AuditLogRepository
        assert hasattr(AuditLogRepository, "log_event")
        assert inspect.iscoroutinefunction(AuditLogRepository.log_event)


# ===================================================================
# SPEC-1367: PreferencesRepository class exists
# ===================================================================


class TestPreferencesRepositoryExists:
    """SPEC-1367: PreferencesRepository class exists in preferences.py."""

    def test_preferences_repository_class_exists(self):
        """PreferencesRepository is importable and is a class."""
        from src.multi_tenant.repositories.preferences import PreferencesRepository
        assert isinstance(PreferencesRepository, type)

    def test_preferences_repository_is_tenant_scoped(self):
        """PreferencesRepository extends TenantScopedRepository."""
        from src.multi_tenant.repositories.preferences import PreferencesRepository
        from src.multi_tenant.repositories.base import TenantScopedRepository
        assert issubclass(PreferencesRepository, TenantScopedRepository)


# ===================================================================
# SPEC-1368: PreferencesRepository.get_active() returns dict | None
# ===================================================================


class TestPreferencesGetActive:
    """SPEC-1368: preferences.get_active() returns dict | None."""

    def test_get_active_method_exists(self):
        """PreferencesRepository has a get_active method."""
        from src.multi_tenant.repositories.preferences import PreferencesRepository
        assert hasattr(PreferencesRepository, "get_active")

    def test_get_active_is_async(self):
        """PreferencesRepository.get_active is an async method."""
        from src.multi_tenant.repositories.preferences import PreferencesRepository
        assert inspect.iscoroutinefunction(PreferencesRepository.get_active)

    def test_get_active_accepts_tenant_id(self):
        """get_active accepts a tenant_id parameter."""
        from src.multi_tenant.repositories.preferences import PreferencesRepository
        sig = inspect.signature(PreferencesRepository.get_active)
        assert "tenant_id" in sig.parameters


# ===================================================================
# SPEC-1369: PreferencesRepository.get_draft() returns dict | None
# ===================================================================


class TestPreferencesGetDraft:
    """SPEC-1369: preferences.get_draft() returns dict | None."""

    def test_get_draft_method_exists(self):
        """PreferencesRepository has a get_draft method."""
        from src.multi_tenant.repositories.preferences import PreferencesRepository
        assert hasattr(PreferencesRepository, "get_draft")

    def test_get_draft_is_async(self):
        """PreferencesRepository.get_draft is an async method."""
        from src.multi_tenant.repositories.preferences import PreferencesRepository
        assert inspect.iscoroutinefunction(PreferencesRepository.get_draft)


# ===================================================================
# SPEC-1370: PreferencesRepository.get_previous() returns dict | None
# ===================================================================


class TestPreferencesGetPrevious:
    """SPEC-1370: preferences.get_previous() returns dict | None."""

    def test_get_previous_method_exists(self):
        """PreferencesRepository has a get_previous method."""
        from src.multi_tenant.repositories.preferences import PreferencesRepository
        assert hasattr(PreferencesRepository, "get_previous")

    def test_get_previous_is_async(self):
        """PreferencesRepository.get_previous is an async method."""
        from src.multi_tenant.repositories.preferences import PreferencesRepository
        assert inspect.iscoroutinefunction(PreferencesRepository.get_previous)


# ===================================================================
# SPEC-1371: PreferencesRepository.get_current() returns dict | None
# ===================================================================


class TestPreferencesGetCurrent:
    """SPEC-1371: preferences.get_current() returns dict | None."""

    def test_get_current_method_exists(self):
        """PreferencesRepository has a get_current method."""
        from src.multi_tenant.repositories.preferences import PreferencesRepository
        assert hasattr(PreferencesRepository, "get_current")

    def test_get_current_is_async(self):
        """PreferencesRepository.get_current is an async method."""
        from src.multi_tenant.repositories.preferences import PreferencesRepository
        assert inspect.iscoroutinefunction(PreferencesRepository.get_current)


# ===================================================================
# SPEC-1372: PreferencesRepository.get_quick_actions() returns list[dict]
# ===================================================================


class TestPreferencesGetQuickActions:
    """SPEC-1372: preferences.get_quick_actions() returns list[dict]."""

    def test_get_quick_actions_method_exists(self):
        """PreferencesRepository has a get_quick_actions method."""
        from src.multi_tenant.repositories.preferences import PreferencesRepository
        assert hasattr(PreferencesRepository, "get_quick_actions")

    def test_get_quick_actions_is_async(self):
        """PreferencesRepository.get_quick_actions is an async method."""
        from src.multi_tenant.repositories.preferences import PreferencesRepository
        assert inspect.iscoroutinefunction(PreferencesRepository.get_quick_actions)

    def test_get_quick_actions_accepts_tenant_id(self):
        """get_quick_actions accepts a tenant_id parameter."""
        from src.multi_tenant.repositories.preferences import PreferencesRepository
        sig = inspect.signature(PreferencesRepository.get_quick_actions)
        assert "tenant_id" in sig.parameters


# ===================================================================
# SPEC-1373: PreferencesRepository.get_quick_actions_active()
# ===================================================================


class TestPreferencesGetQuickActionsActive:
    """SPEC-1373: preferences.get_quick_actions_active() returns list[dict]."""

    def test_get_quick_actions_active_method_exists(self):
        """PreferencesRepository has a get_quick_actions_active method."""
        from src.multi_tenant.repositories.preferences import PreferencesRepository
        assert hasattr(PreferencesRepository, "get_quick_actions_active")

    def test_get_quick_actions_active_is_async(self):
        """PreferencesRepository.get_quick_actions_active is an async method."""
        from src.multi_tenant.repositories.preferences import PreferencesRepository
        assert inspect.iscoroutinefunction(
            PreferencesRepository.get_quick_actions_active,
        )


# ===================================================================
# SPEC-1375: SNAPSHOT_TYPE_DAILY = "daily"
# ===================================================================


class TestSnapshotTypeDailyConstant:
    """SPEC-1375: SNAPSHOT_TYPE_DAILY = 'daily'."""

    def test_snapshot_type_daily_value(self):
        """SNAPSHOT_TYPE_DAILY constant equals 'daily'."""
        from src.multi_tenant.repositories.sla_snapshots import SNAPSHOT_TYPE_DAILY
        assert SNAPSHOT_TYPE_DAILY == "daily"

    def test_snapshot_type_daily_is_string(self):
        """SNAPSHOT_TYPE_DAILY is a string."""
        from src.multi_tenant.repositories.sla_snapshots import SNAPSHOT_TYPE_DAILY
        assert isinstance(SNAPSHOT_TYPE_DAILY, str)


# ===================================================================
# SPEC-1377: TenantRepository class exists
# ===================================================================


class TestTenantRepositoryExists:
    """SPEC-1377: TenantRepository class exists in tenant.py."""

    def test_tenant_repository_class_exists(self):
        """TenantRepository is importable and is a class."""
        from src.multi_tenant.repositories.tenant import TenantRepository
        assert isinstance(TenantRepository, type)

    def test_tenant_repository_is_tenant_scoped(self):
        """TenantRepository extends TenantScopedRepository."""
        from src.multi_tenant.repositories.tenant import TenantRepository
        from src.multi_tenant.repositories.base import TenantScopedRepository
        assert issubclass(TenantRepository, TenantScopedRepository)


# ===================================================================
# SPEC-1380: TenantRepository.list_expiring_trials() returns list[dict]
# ===================================================================


class TestTenantListExpiringTrials:
    """SPEC-1380: tenant.list_expiring_trials() returns list[dict]."""

    def test_list_expiring_trials_method_exists(self):
        """TenantRepository has a list_expiring_trials method."""
        from src.multi_tenant.repositories.tenant import TenantRepository
        assert hasattr(TenantRepository, "list_expiring_trials")

    def test_list_expiring_trials_is_async(self):
        """TenantRepository.list_expiring_trials is an async method."""
        from src.multi_tenant.repositories.tenant import TenantRepository
        assert inspect.iscoroutinefunction(TenantRepository.list_expiring_trials)

    def test_list_expiring_trials_accepts_within_iso(self):
        """list_expiring_trials accepts a within_iso parameter."""
        from src.multi_tenant.repositories.tenant import TenantRepository
        sig = inspect.signature(TenantRepository.list_expiring_trials)
        assert "within_iso" in sig.parameters


# ===================================================================
# SPEC-1382: TenantRepository.list_expiring_tenants() returns list[dict]
# ===================================================================


class TestTenantListExpiringTenants:
    """SPEC-1382: tenant.list_expiring_tenants() returns list[dict]."""

    def test_list_expiring_tenants_method_exists(self):
        """TenantRepository has a list_expiring_tenants method."""
        from src.multi_tenant.repositories.tenant import TenantRepository
        assert hasattr(TenantRepository, "list_expiring_tenants")

    def test_list_expiring_tenants_is_async(self):
        """TenantRepository.list_expiring_tenants is an async method."""
        from src.multi_tenant.repositories.tenant import TenantRepository
        assert inspect.iscoroutinefunction(TenantRepository.list_expiring_tenants)

    def test_list_expiring_tenants_accepts_within_iso(self):
        """list_expiring_tenants accepts a within_iso parameter."""
        from src.multi_tenant.repositories.tenant import TenantRepository
        sig = inspect.signature(TenantRepository.list_expiring_tenants)
        assert "within_iso" in sig.parameters


# ===================================================================
# SPEC-1383: UsageRepository class exists
# ===================================================================


class TestUsageRepositoryExists:
    """SPEC-1383: UsageRepository class exists in usage.py."""

    def test_usage_repository_class_exists(self):
        """UsageRepository is importable and is a class."""
        from src.multi_tenant.repositories.usage import UsageRepository
        assert isinstance(UsageRepository, type)

    def test_usage_repository_is_tenant_scoped(self):
        """UsageRepository extends TenantScopedRepository."""
        from src.multi_tenant.repositories.usage import UsageRepository
        from src.multi_tenant.repositories.base import TenantScopedRepository
        assert issubclass(UsageRepository, TenantScopedRepository)
