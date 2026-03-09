from __future__ import annotations
import os
import pytest

PROJECT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def _read(rel_path: str) -> str:
    full = os.path.join(PROJECT, rel_path.replace("/", os.sep))
    with open(full, "r", encoding="utf-8") as fh:
        return fh.read()


class TestNavLabelRename:

    def test_sidebar_label(self):
        src = _read("admin/standalone/layouts/StandaloneLayout.tsx")
        assert "Account" in src

    def test_page_title(self):
        src = _read("admin/standalone/pages/Billing.tsx")
        assert "Account and billing" in src


class TestContactPreferencesSection:

    def test_has_contact_section(self):
        src = _read("admin/standalone/pages/Billing.tsx")
        assert "Contact and security preferences" in src

    def test_superadmin_guard(self):
        src = _read("admin/standalone/pages/Billing.tsx")
        assert "userRole" in src
        assert "superadmin" in src

    def test_email_change_handler(self):
        src = _read("admin/standalone/pages/Billing.tsx")
        assert "handleRequestEmailChange" in src
        assert "/api/admin/email/request" in src

    def test_user_email_in_context(self):
        src = _read("admin/standalone/layouts/StandaloneLayout.tsx")
        assert "userEmail" in src

    def test_whoami_sets_email(self):
        src = _read("admin/standalone/layouts/StandaloneLayout.tsx")
        assert "setUserEmail" in src

    def test_recovery_placeholder(self):
        src = _read("admin/standalone/pages/Billing.tsx")
        assert "Coming soon" in src



class TestBillingChartRemoval:
    """SPEC-1684: Verify recharts chart removed from Billing page."""

    def test_no_recharts_import(self):
        src = _read('admin/standalone/pages/Billing.tsx')
        assert 'recharts' not in src

    def test_no_use_daily_volume(self):
        src = _read('admin/standalone/pages/Billing.tsx')
        assert 'useDailyVolume' not in src

    def test_no_chart_data(self):
        src = _read('admin/standalone/pages/Billing.tsx')
        assert 'chartData' not in src

    def test_no_computed_color_scheme(self):
        src = _read('admin/standalone/pages/Billing.tsx')
        assert 'useComputedColorScheme' not in src

    def test_no_format_chart_date(self):
        src = _read('admin/standalone/pages/Billing.tsx')
        assert 'formatChartDate' not in src

    def test_no_area_chart(self):
        src = _read('admin/standalone/pages/Billing.tsx')
        assert 'AreaChart' not in src


class TestDashboardDualSeriesChart:
    """SPEC-1685: Dashboard has total + billable dual-series chart."""

    def test_daily_usage_title(self):
        src = _read('admin/standalone/pages/Dashboard.tsx')
        assert 'Daily usage' in src

    def test_billable_data_key(self):
        src = _read('admin/standalone/pages/Dashboard.tsx')
        assert 'billable' in src

    def test_gradient_billable_defined(self):
        src = _read('admin/standalone/pages/Dashboard.tsx')
        assert 'gradBillable' in src

    def test_recharts_still_used(self):
        src = _read('admin/standalone/pages/Dashboard.tsx')
        assert 'recharts' in src
        assert 'AreaChart' in src

    def test_total_and_billable_data(self):
        src = _read('admin/standalone/pages/Dashboard.tsx')
        assert 'total' in src
        assert 'billable' in src


class TestSmsVerificationModule:
    """SPEC-1686: SMS verification module exists with expected API."""

    def test_module_exists(self):
        from src.multi_tenant import sms_verification
        assert hasattr(sms_verification, 'SmsVerificationService')
        assert hasattr(sms_verification, 'generate_verification_code')

    def test_ttl_is_900(self):
        from src.multi_tenant.sms_verification import _CODE_TTL
        assert _CODE_TTL == 900


class TestCommunicationCaptureModule:
    """SPEC-1687: Communication capture module exists."""

    def test_emit_function_exists(self):
        from src.multi_tenant.communication_capture import emit_communication_event
        assert callable(emit_communication_event)

    def test_router_prefix(self):
        from src.multi_tenant.communication_capture import router
        route_paths = [r.path for r in router.routes]
        assert any('/api/test/email-capture' in p for p in route_paths)

    def test_capture_mode_default_off(self):
        from src.multi_tenant.communication_capture import CAPTURE_MODE
        assert CAPTURE_MODE is False


class TestEmailChangeModule:
    """SPEC-1682/1683: Email change module registered."""

    def test_router_exists(self):
        from src.multi_tenant.email_change import router
        assert router is not None

    def test_router_registered(self):
        from src.app.routers import email_change_router
        assert email_change_router is not None
