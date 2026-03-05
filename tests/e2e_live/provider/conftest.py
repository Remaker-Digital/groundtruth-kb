"""
Live E2E test fixtures for the Provider Admin Console (SPA console) against staging.

The Provider Console is the platform-wide operator interface at /admin/provider.
It requires a SUPERADMIN API key and accesses /api/superadmin/* endpoints.
Unlike the standalone admin (per-tenant), this console manages ALL tenants.

Architecture:
  - Auth: sessionStorage key ``agentred_provider_key`` (three-state:
    login → optional MFA → authenticated)
  - Navigation: Grouped sidebar with 19 pages in 4 groups
  - API context: ProviderContext.apiFetch injects X-API-Key header

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import os
import re
import time

import pytest
from playwright.sync_api import Page

# ---------------------------------------------------------------------------
# Auto-load .env.local
# ---------------------------------------------------------------------------
from scripts._env import load_env_local

load_env_local()

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

STAGING_FQDN = "https://agent-red-staging.orangeglacier-f566a4e7.eastus.azurecontainerapps.io"

PROVIDER_BASE_URL = os.environ.get(
    "PROVIDER_BASE_URL",
    f"{STAGING_FQDN}/admin/provider",
)

PROD_URL = os.environ.get("PROD_URL", STAGING_FQDN)

# SPA Console API key — SUPERADMIN role, used for the provider console.
# Priority: env override > .env.local keys.
PROVIDER_API_KEY = (
    os.environ.get("SPA_CONSOLE_API_KEY")
    or os.environ.get("SUPERADMIN_PREVIEW_API_KEY")
    or os.environ.get("STAGING_REMAKER_DIGITAL_001_SUPERADMIN_KEY")
    or os.environ.get("AGENTRED_API_KEY")
    or ""
)

# Navigation groups and items (must match ProviderLayout.tsx NAV_GROUPS)
NAV_GROUPS = {
    "Overview": [
        ("Dashboard", "/"),
        ("Tenants", "/tenants"),
    ],
    "Operations": [
        ("Deployments", "/deployments"),
        ("Queue Health", "/queues"),
        ("Integrations", "/integrations"),
        ("Status Page", "/status"),
        ("Alerts", "/alerts"),
        ("Diagnostics", "/diagnostics"),
        ("Co-Pilot Knowledge", "/copilot-knowledge"),
        ("Pipeline Observatory", "/pipeline"),
        ("Contact Messages", "/contact-messages"),
        ("Service Messages", "/service-messages"),
    ],
    "Compliance & Security": [
        ("Compliance", "/compliance"),
        ("Secrets", "/secrets"),
        ("Billing", "/billing"),
        ("Cost Analytics", "/costs"),
        ("SLA Trends", "/sla"),
        ("Abuse Detection", "/abuse"),
    ],
    "Account": [
        ("MFA Settings", "/mfa"),
    ],
}

ALL_NAV_ITEMS = [item for group in NAV_GROUPS.values() for item in group]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _check_staging_reachable() -> bool:
    """Quick connectivity check against the staging health endpoint."""
    try:
        import httpx
        with httpx.Client(timeout=5.0) as c:
            resp = c.get(f"{PROD_URL}/health")
            return resp.status_code == 200
    except Exception:
        return False


def _main_text(page: Page) -> str:
    """Extract visible text from the main content area."""
    try:
        main = page.locator("main").first
        if main.count() > 0:
            return main.inner_text(timeout=5_000)
    except Exception:
        pass
    return page.locator("body").inner_text(timeout=5_000)


def _is_rate_limited(page: Page) -> bool:
    """Check if the page is showing rate limit errors."""
    text = _main_text(page).lower()
    if "failed to load" in text and ("429" in text or "rate" in text):
        return True
    if "too many" in text and "request" in text:
        return True
    return False


def _navigate_provider_to(page: Page, nav_label: str, wait_text: str | None = None) -> Page:
    """Click a sidebar nav link in the provider console and wait for load."""
    nav_link = page.locator(f"nav >> text=\"{nav_label}\"").first
    if not nav_link.is_visible():
        nav_link = page.get_by_text(nav_label, exact=True).first
    nav_link.click()

    if wait_text:
        page.wait_for_selector(f"text={wait_text}", timeout=15_000)

    page.wait_for_timeout(1000)
    return page


# ---------------------------------------------------------------------------
# Session-scoped fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def provider_api_key() -> str:
    """Load the SUPERADMIN API key for the provider console."""
    if not PROVIDER_API_KEY:
        pytest.skip(
            "No SPA console API key found — set SPA_CONSOLE_API_KEY or "
            "SUPERADMIN_PREVIEW_API_KEY in .env.local"
        )
    return PROVIDER_API_KEY


@pytest.fixture(scope="session")
def staging_reachable() -> None:
    """Verify staging is reachable before running provider console tests."""
    if not _check_staging_reachable():
        pytest.skip(f"Staging unreachable at {PROD_URL} — skipping provider E2E tests")


# ---------------------------------------------------------------------------
# Class-scoped rate limit cooldown
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True, scope="class")
def _rate_limit_cooldown():
    """2 s cooldown between test classes to avoid burst clustering."""
    yield
    time.sleep(2)


# ---------------------------------------------------------------------------
# Per-test page fixture
# ---------------------------------------------------------------------------

@pytest.fixture()
def live_provider_page(
    page: Page,
    staging_reachable,
    provider_api_key: str,
) -> Page:
    """Navigate to the Provider Console with real SUPERADMIN auth.

    Injects the API key into sessionStorage (matching the provider console's
    getStoredApiKey() which reads ``agentred_provider_key``), then navigates
    to the deployed provider SPA.
    """
    page.add_init_script(f"""
        sessionStorage.setItem('agentred_provider_key', '{provider_api_key}');
    """)
    page.goto(f"{PROVIDER_BASE_URL}/", wait_until="load")

    # Wait for the console to load — either dashboard content or login form
    # (if the key is rejected, login form reappears)
    try:
        page.wait_for_selector(
            "text=/Platform Dashboard|Service Provider Console|Dashboard/i",
            timeout=20_000,
        )
    except Exception:
        pass  # Let individual tests assert on content

    page.wait_for_timeout(1000)
    return page


# ---------------------------------------------------------------------------
# Page-specific fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def live_health_dashboard_page(live_provider_page: Page) -> Page:
    """Provider console — Health Dashboard (landing page)."""
    return live_provider_page


@pytest.fixture()
def live_tenant_directory_page(live_provider_page: Page) -> Page:
    """Provider console — Tenant Directory."""
    return _navigate_provider_to(live_provider_page, "Tenants", "Tenant")


@pytest.fixture()
def live_deployment_history_page(live_provider_page: Page) -> Page:
    """Provider console — Deployment History."""
    return _navigate_provider_to(live_provider_page, "Deployments", "Deployment")


@pytest.fixture()
def live_queue_health_page(live_provider_page: Page) -> Page:
    """Provider console — Queue Health."""
    return _navigate_provider_to(live_provider_page, "Queue Health", "Queue")


@pytest.fixture()
def live_integration_health_page(live_provider_page: Page) -> Page:
    """Provider console — Integration Health."""
    return _navigate_provider_to(live_provider_page, "Integrations", "Integration")


@pytest.fixture()
def live_status_page_page(live_provider_page: Page) -> Page:
    """Provider console — Status Page Management."""
    return _navigate_provider_to(live_provider_page, "Status Page", "Status")


@pytest.fixture()
def live_alert_config_page(live_provider_page: Page) -> Page:
    """Provider console — Alert Configuration."""
    return _navigate_provider_to(live_provider_page, "Alerts", "Alert")


@pytest.fixture()
def live_diagnostics_page(live_provider_page: Page) -> Page:
    """Provider console — Support Diagnostics."""
    return _navigate_provider_to(live_provider_page, "Diagnostics", "Diagnostic")


@pytest.fixture()
def live_copilot_knowledge_page(live_provider_page: Page) -> Page:
    """Provider console — Co-Pilot Knowledge."""
    return _navigate_provider_to(live_provider_page, "Co-Pilot Knowledge", "Knowledge")


@pytest.fixture()
def live_pipeline_page(live_provider_page: Page) -> Page:
    """Provider console — Pipeline Observatory."""
    return _navigate_provider_to(live_provider_page, "Pipeline Observatory", "Pipeline")


@pytest.fixture()
def live_contact_messages_page(live_provider_page: Page) -> Page:
    """Provider console — Contact Messages."""
    return _navigate_provider_to(live_provider_page, "Contact Messages", "Contact")


@pytest.fixture()
def live_service_messages_page(live_provider_page: Page) -> Page:
    """Provider console — Service Messages."""
    return _navigate_provider_to(live_provider_page, "Service Messages", "Service")


@pytest.fixture()
def live_compliance_page(live_provider_page: Page) -> Page:
    """Provider console — Compliance Dashboard."""
    return _navigate_provider_to(live_provider_page, "Compliance", "Compliance")


@pytest.fixture()
def live_secrets_page(live_provider_page: Page) -> Page:
    """Provider console — Secret Posture."""
    return _navigate_provider_to(live_provider_page, "Secrets", "Secret")


@pytest.fixture()
def live_billing_health_page(live_provider_page: Page) -> Page:
    """Provider console — Billing Health."""
    return _navigate_provider_to(live_provider_page, "Billing", "Billing")


@pytest.fixture()
def live_cost_analytics_page(live_provider_page: Page) -> Page:
    """Provider console — Cost Analytics."""
    return _navigate_provider_to(live_provider_page, "Cost Analytics", "Cost")


@pytest.fixture()
def live_sla_trends_page(live_provider_page: Page) -> Page:
    """Provider console — SLA Trends."""
    return _navigate_provider_to(live_provider_page, "SLA Trends", "SLA")


@pytest.fixture()
def live_abuse_detection_page(live_provider_page: Page) -> Page:
    """Provider console — Abuse Detection."""
    return _navigate_provider_to(live_provider_page, "Abuse Detection", "Abuse")


@pytest.fixture()
def live_mfa_settings_page(live_provider_page: Page) -> Page:
    """Provider console — MFA Settings."""
    return _navigate_provider_to(live_provider_page, "MFA Settings", "MFA")
