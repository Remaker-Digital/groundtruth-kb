"""Tests for superadmin_api package split (S161 Group 4).

Validates SPEC-1694: superadmin_api.py MUST be split into domain sub-modules.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
import importlib
import pathlib

import pytest


class TestSuperadminApiIsPackage:
    """SPEC-1694: superadmin_api MUST be a package with sub-modules."""

    def test_superadmin_api_is_directory(self):
        p = pathlib.Path('src/multi_tenant/superadmin_api')
        assert p.is_dir(), 'superadmin_api must be a package (directory)'

    def test_superadmin_api_has_init(self):
        p = pathlib.Path('src/multi_tenant/superadmin_api/__init__.py')
        assert p.exists(), '__init__.py must exist'

    def test_superadmin_api_has_sub_modules(self):
        pkg = pathlib.Path('src/multi_tenant/superadmin_api')
        modules = [f.stem for f in pkg.glob('*.py')
                   if f.stem != '__init__' and not f.stem.startswith('__')]
        assert len(modules) >= 5, f'Expected >= 5 sub-modules, found {len(modules)}: {modules}'

    def test_no_monolith_file(self):
        p = pathlib.Path('src/multi_tenant/superadmin_api.py')
        assert not p.exists(), 'Old monolith file should not exist'


class TestBackwardCompatibility:
    """All existing imports MUST still work after the split."""

    def test_import_router(self):
        from src.multi_tenant.superadmin_api import router
        assert router is not None

    def test_import_configure_superadmin_services(self):
        from src.multi_tenant.superadmin_api import configure_superadmin_services
        assert callable(configure_superadmin_services)

    def test_import_configure_copilot(self):
        from src.multi_tenant.superadmin_api import configure_copilot_knowledge_service
        assert callable(configure_copilot_knowledge_service)

    def test_import_configure_pipeline(self):
        from src.multi_tenant.superadmin_api import configure_pipeline_observatory
        assert callable(configure_pipeline_observatory)

    def test_import_tenant_models(self):
        from src.multi_tenant.superadmin_api import (
            TenantSummaryItem,
            TenantDirectoryResponse,
            CreateTenantRequest,
            CreateTenantResponse,
            TierOverrideResponse,
            SetExpiryRequest,
            SetExpiryResponse,
        )

    def test_import_dashboard_models(self):
        from src.multi_tenant.superadmin_api import (
            DashboardHealthResponse,
            BillingHealthResponse,
            SLATrendsResponse,
            QueueDepthResponse,
            ComplianceSummaryResponse,
            SecretPostureResponse,
            IntegrationHealthResponse,
        )

    def test_import_incident_models(self):
        from src.multi_tenant.superadmin_api import (
            IncidentModel,
            IncidentListResponse,
            CreateIncidentRequest,
        )

    def test_import_alert_models(self):
        from src.multi_tenant.superadmin_api import (
            AlertRuleModel,
            AlertRuleListResponse,
            CreateAlertRuleRequest,
            AlertHistoryResponse,
        )

    def test_import_mfa_models(self):
        from src.multi_tenant.superadmin_api import (
            MfaStatusResponse,
            MfaEnrollResponse,
        )

    def test_import_cost_abuse_models(self):
        from src.multi_tenant.superadmin_api import (
            CostOverviewResponse,
            CostBreakdownModel,
            AbuseOverviewResponse,
            AbuseSignalModel,
            FlagTenantRequest,
        )

    def test_import_copilot_models(self):
        from src.multi_tenant.superadmin_api import (
            CopilotDocumentResponse,
            CopilotDocumentListResponse,
        )

    def test_import_pipeline_models(self):
        from src.multi_tenant.superadmin_api import (
            PipelineTopologyResponse,
            PipelineNodeMetrics,
        )

    def test_import_service_message_models(self):
        from src.multi_tenant.superadmin_api import (
            ServiceMessageRequest,
            ServiceMessageSendResponse,
        )

    def test_import_platform_admin_models(self):
        from src.multi_tenant.superadmin_api import (
            RegenerateKeyResponse,
            PlatformAdminUserResponse,
            CreateOperatorRequest,
        )

    def test_import_endpoint_functions(self):
        from src.multi_tenant.superadmin_api import (
            list_all_tenants,
            tenant_summary,
            provider_dashboard,
            billing_health,
            sla_trends,
            queue_depth,
            compliance_summary,
            secret_posture,
            integration_health,
        )

    def test_router_has_all_endpoints(self):
        from src.multi_tenant.superadmin_api import router
        paths = [r.path for r in router.routes if hasattr(r, 'path')]
        assert len(paths) >= 55, f'Expected >= 55 routes, got {len(paths)}'


class TestSubModuleDomains:
    """Each sub-module should cover a coherent domain with real endpoints."""

    def test_tenants_module_has_endpoints(self):
        import src.multi_tenant.superadmin_api._tenants as m
        assert hasattr(m, 'list_all_tenants')
        assert hasattr(m, 'create_tenant')
        assert hasattr(m, 'set_tenant_expiry')

    def test_dashboard_module_has_endpoints(self):
        import src.multi_tenant.superadmin_api._dashboard as m
        assert hasattr(m, 'provider_dashboard')
        assert hasattr(m, 'billing_health')
        assert hasattr(m, 'integration_health')

    def test_operations_module_has_endpoints(self):
        import src.multi_tenant.superadmin_api._operations as m
        assert hasattr(m, 'list_incidents')
        assert hasattr(m, 'list_alert_rules')
        assert hasattr(m, 'mfa_status')

    def test_copilot_module_has_endpoints(self):
        import src.multi_tenant.superadmin_api._copilot as m
        assert hasattr(m, 'list_copilot_documents')
        assert hasattr(m, 'copilot_stats')
        assert hasattr(m, 'test_copilot_query')

    def test_platform_module_has_endpoints(self):
        import src.multi_tenant.superadmin_api._platform as m
        assert hasattr(m, 'get_pipeline_topology')
        assert hasattr(m, 'regenerate_platform_admin_key')
        assert hasattr(m, 'list_platform_admin_users')

    def test_monolith_only_has_state_and_config(self):
        """After split, _monolith.py should only contain state, router, and configure_*."""
        import src.multi_tenant.superadmin_api._monolith as m
        # Should have state + config
        assert hasattr(m, 'router')
        assert hasattr(m, 'configure_superadmin_services')
        assert hasattr(m, '_tenant_repo')
        # Should NOT have endpoint functions
        assert not hasattr(m, 'list_all_tenants')
        assert not hasattr(m, 'provider_dashboard')
        assert not hasattr(m, 'list_incidents')
