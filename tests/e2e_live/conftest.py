"""
Live E2E test fixtures for the standalone admin SPA against staging.

Unlike tests/e2e/ (which mocks all API calls), these tests run the real React
app with real API responses from the deployed staging environment.

Architecture:
  - admin_vite_server (session): starts ``npm run dev`` with VITE_API_URL
    pointing to staging so the Vite proxy forwards /api/* to the real backend.
  - live_api_key (session): loads from .env.local — the real admin API key.
  - live_admin_page (per-test): injects real auth, navigates to the admin SPA.
  - Page fixtures: live_dashboard_page, live_team_page, etc.

Mutation policy (SPEC-1655):
  Staging is NOT a safe environment.  ALL data-mutating operations (POST,
  PUT, DELETE) MUST be executed — destructive testing is a required part of
  the test plan.  Tests that create data must clean up after themselves
  (disposable member pattern).

Rate limiting:
  All tiers = 500 rpm.  A 2 s cooldown between test classes prevents
  burst clustering.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import os
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest
from playwright.sync_api import Page, Route

# ---------------------------------------------------------------------------
# Auto-load .env.local (transient credentials — R7 refactoring)
# ---------------------------------------------------------------------------
from scripts._env import load_env_local

load_env_local()

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# S137: All live E2E tests target the DEPLOYED staging environment directly.
# The SPA and API share the same origin — no Vite dev server, no CORS proxy.
# Override via env vars if targeting a different environment.
STAGING_FQDN = "https://agent-red-staging.orangeglacier-f566a4e7.eastus.azurecontainerapps.io"

LIVE_SPA_BASE_URL = os.environ.get(
    "LIVE_SPA_BASE_URL",
    f"{STAGING_FQDN}/admin/standalone",
)

# The ACTUAL API target — used for reachability checks and direct API calls.
PROD_URL = os.environ.get("PROD_URL", STAGING_FQDN)

# Legacy: SPA_API_URL used by the Vite proxy rewrite.  Still needed if
# someone opts into local Vite mode by clearing LIVE_SPA_BASE_URL.
SPA_API_URL = PROD_URL

# API key for the target tenant — used to authenticate the admin SPA.
# Priority: env override > .env.local keys.
LIVE_API_KEY = (
    os.environ.get("SUPERADMIN_PREVIEW_API_KEY")
    or os.environ.get("STAGING_REMAKER_DIGITAL_001_SUPERADMIN_KEY")
    or os.environ.get("SPA_CONSOLE_API_KEY")
    or os.environ.get("AGENTRED_API_KEY")
    or ""
)

# Tenant slug for URL ?tenant= parameter.
LIVE_TENANT_ID = os.environ.get("LIVE_TENANT_ID", "blanco-9939")

# Legacy Vite support — only used when LIVE_SPA_BASE_URL is empty.
ADMIN_VITE_PORT = 3300
ADMIN_DIR = Path(__file__).resolve().parent.parent.parent / "admin" / "standalone"

# SPEC-1655: No mutations are blocked.  Staging is a testing environment
# where ALL operations (POST, PUT, DELETE) must be exercised.
# Legacy BLOCKED_MUTATIONS list removed per owner directive S139.
# Tests that create/modify data must clean up after themselves.

# Navigation items and their expected page headings
NAV_ITEMS: dict[str, str | None] = {
    "Dashboard": "Dashboard",
    "Inbox": "Inbox",
    "Team members": "Team members",
    "Agent configuration": "Configuration",
    "Knowledge base": "Knowledge",
    "Quick actions": "Quick actions",
    "Widget configuration": "Widget",
    "Integrations": None,  # no specific heading
    "Memory & privacy": "Memory",
    "Billing": "Billing",
}


# ---------------------------------------------------------------------------
# Helpers (reused from tests/e2e/conftest.py)
# ---------------------------------------------------------------------------

def _port_is_open(port: int, host: str = "localhost") -> bool:
    """Check if a TCP port is accepting connections."""
    for family, addr in [
        (socket.AF_INET, "127.0.0.1"),
        (socket.AF_INET6, "::1"),
    ]:
        try:
            with socket.socket(family, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                s.connect((addr, port))
                return True
        except (ConnectionRefusedError, OSError):
            continue
    return False


def _check_production_reachable() -> bool:
    """Quick connectivity check against the production health endpoint."""
    try:
        import httpx

        with httpx.Client(timeout=5.0) as c:
            resp = c.get(f"{PROD_URL}/health")
            return resp.status_code == 200
    except Exception:
        return False


def _dismiss_onboarding_modal(page: Page) -> None:
    """Dismiss the OnboardingWizard modal if it is visible.

    The OnboardingWizard auto-opens on every fresh page load when
    ``sessionStorage`` lacks ``agentred-onboarding-dismissed``.  Since each
    test gets a fresh browser context, the wizard always appears.

    - Freshly-seeded tenants (active_version=0): Step 1 shows a "Skip for
      now" button.  Click it.
    - Activated tenants (active_version >= 1): The wizard shows template
      selection with NO "Skip for now" button.  Press Escape to dismiss.

    **Race condition (WI-CP3):** For version-0 tenants the StandaloneLayout
    ``useEffect`` fires *after* the activation-status API returns, forcibly
    removing the ``agentred-onboarding-dismissed`` flag and re-opening the
    wizard — even if we already dismissed it.  We must retry dismissal up
    to 3 times and verify the overlay is fully removed before returning.

    The modal uses ``closeOnClickOutside={false}`` so backdrop clicks don't
    work, but Escape triggers the ``onClose`` callback on Step 1 only.
    """
    overlay_sel = ".mantine-Modal-overlay"

    for attempt in range(3):
        # Try clicking "Skip for now" (freshly-seeded Step 1)
        try:
            skip_btn = page.get_by_text("Skip for now", exact=True)
            skip_btn.wait_for(state="visible", timeout=3_000)
            skip_btn.click()
            page.wait_for_timeout(500)
        except Exception:
            # No "Skip for now" visible — try Escape on any open dialog
            try:
                dialog = page.locator("[role='dialog']")
                if dialog.count() > 0:
                    page.keyboard.press("Escape")
                    page.wait_for_timeout(500)
            except Exception:
                pass

        # Verify the overlay is actually gone
        try:
            page.locator(overlay_sel).wait_for(state="hidden", timeout=2_000)
            return  # ✅ Overlay removed — safe to proceed
        except Exception:
            # Overlay still present — the useEffect may have re-opened the
            # wizard after our dismiss.  Wait a beat and retry.
            page.wait_for_timeout(1_000)

    # Final safety net: force-remove overlay via JS so tests aren't blocked.
    # This doesn't "fix" the wizard state but prevents the overlay from
    # intercepting pointer events on the page underneath.
    page.evaluate("""
        document.querySelectorAll('.mantine-Modal-overlay, .mantine-Modal-root')
            .forEach(el => el.remove());
    """)


def _navigate_admin_to(page: Page, nav_text: str, wait_for_text: str | None = None) -> Page:
    """Click a sidebar nav link and wait for the page to load."""
    nav_link = page.locator(f'nav >> text="{nav_text}"').first
    if not nav_link.is_visible():
        nav_link = page.get_by_text(nav_text, exact=True).first
    nav_link.click()

    if wait_for_text:
        page.wait_for_selector(f"text={wait_for_text}", timeout=10_000)

    # Settle time for React state + real API response
    page.wait_for_timeout(500)
    return page


def _attach_api_proxy_rewrite(page: Page) -> None:
    """Rewrite cross-origin API calls to go through the local Vite proxy.

    When VITE_API_URL is set (via admin/.env.local), the React SPA makes
    direct cross-origin requests to the gateway URL stored there.  This
    causes CORS preflight failures for custom headers like X-API-Key.

    This handler intercepts those cross-origin requests at the Playwright
    network level (before CORS checks) and proxies them through the
    localhost Vite dev server instead — making them same-origin.

    Key distinction: SPA_API_URL is what the browser requests (from
    admin/.env.local); PROD_URL is the actual API target (may differ for
    staging pipeline runs).  The Vite proxy (API_PROXY_TARGET) routes
    /api/* to PROD_URL, so the full chain is:

        SPA → SPA_API_URL → Playwright intercepts → localhost:3300
                → Vite proxy → API_PROXY_TARGET (=PROD_URL)

    Uses httpx to manually fetch from localhost because Playwright's
    route.continue_() does not allow protocol changes (https → http).

    MUST be registered BEFORE safety guards so guards take priority via
    Playwright's LIFO route matching + fallback() chain.
    """
    if not SPA_API_URL:
        return

    import httpx

    def _proxy_via_localhost(route: Route) -> None:
        local_url = route.request.url.replace(
            SPA_API_URL, f"http://localhost:{ADMIN_VITE_PORT}"
        )
        # Forward the request headers, stripping host (will be set by httpx)
        headers = {
            k: v
            for k, v in route.request.headers.items()
            if k.lower() not in ("host", "content-length")
        }
        try:
            with httpx.Client(timeout=30.0) as client:
                resp = client.request(
                    method=route.request.method,
                    url=local_url,
                    headers=headers,
                    content=route.request.post_data_buffer,
                    follow_redirects=True,
                )
            # Convert httpx headers to dict (Playwright needs simple dict)
            resp_headers = {k: v for k, v in resp.headers.items()}
            # Remove transfer-encoding since we're passing the full body
            resp_headers.pop("transfer-encoding", None)
            route.fulfill(
                status=resp.status_code,
                headers=resp_headers,
                body=resp.content,
            )
        except Exception:
            # If local proxy fails, let the original request through
            route.fallback()

    page.route(f"{SPA_API_URL}/**", _proxy_via_localhost)


# ---------------------------------------------------------------------------
# Session-scoped fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def live_api_key() -> str:
    """Load the real API key from .env.local.

    Skips the entire test session if no API key is available.
    """
    if not LIVE_API_KEY:
        pytest.skip(
            "No API key found in .env.local "
            "(set SUPERADMIN_PREVIEW_API_KEY or SPA_CONSOLE_API_KEY) — "
            "skipping live E2E tests"
        )
    return LIVE_API_KEY


@pytest.fixture(scope="session")
def production_reachable() -> None:
    """Verify production is reachable before running any tests.

    Skips the entire session if the production endpoint is down.
    """
    if not _check_production_reachable():
        pytest.skip(
            f"Production endpoint unreachable at {PROD_URL} — "
            "skipping live E2E tests"
        )


@pytest.fixture(scope="session")
def admin_vite_server(production_reachable) -> subprocess.Popen | None:
    """Start the Vite dev server with API proxy to production.

    Sets VITE_API_URL so the Vite proxy in vite.config.ts forwards
    /api/* to the real production backend.

    When LIVE_SPA_BASE_URL is set (deployed SPA mode), the Vite server
    is not needed — the SPA is served directly from the deployed container.
    """
    if LIVE_SPA_BASE_URL:
        yield None
        return

    node_modules = ADMIN_DIR / "node_modules"
    if not node_modules.exists():
        pytest.skip(
            "admin/standalone/node_modules not found — "
            "run `cd admin/standalone && npm install`"
        )

    # Reuse existing server if already running
    if _port_is_open(ADMIN_VITE_PORT):
        yield None
        return

    creation_flags = 0
    if sys.platform == "win32":
        creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP

    # Point the Vite proxy to the target environment.
    # API_PROXY_TARGET is a server-only env var (not exposed to browser via
    # import.meta.env) that vite.config.ts reads for the proxy target.
    # VITE_API_URL is also set so the proxy works even without the config change.
    env = {**os.environ, "API_PROXY_TARGET": PROD_URL, "VITE_API_URL": PROD_URL}
    proc = subprocess.Popen(
        "npm run dev",
        cwd=str(ADMIN_DIR),
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=creation_flags,
        env=env,
    )

    for _ in range(30):
        if _port_is_open(ADMIN_VITE_PORT):
            break
        if proc.poll() is not None:
            stdout = proc.stdout.read().decode(errors="replace") if proc.stdout else ""
            stderr = proc.stderr.read().decode(errors="replace") if proc.stderr else ""
            raise RuntimeError(
                f"Admin Vite dev server exited with code {proc.returncode}.\n"
                f"stdout: {stdout}\nstderr: {stderr}"
            )
        time.sleep(1)
    else:
        proc.kill()
        raise RuntimeError(
            f"Admin Vite server did not start on port {ADMIN_VITE_PORT} within 30 s"
        )

    yield proc

    # Teardown
    if sys.platform == "win32":
        try:
            os.kill(proc.pid, signal.CTRL_BREAK_EVENT)
            proc.wait(timeout=5)
        except (OSError, subprocess.TimeoutExpired):
            subprocess.run(
                f"taskkill /F /T /PID {proc.pid}",
                shell=True,
                capture_output=True,
            )
    else:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()


# ---------------------------------------------------------------------------
# Class-scoped rate limit cooldown
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True, scope="class")
def _rate_limit_cooldown():
    """Insert a 2 s cooldown between test classes.

    With class-scoped page fixtures (one page load per class), API usage
    is modest (~3-5 calls per class).  A 2 s gap prevents burst clustering.
    """
    yield
    time.sleep(2)


# ---------------------------------------------------------------------------
# Per-test fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def live_admin_page(
    page: Page,
    admin_vite_server,
    live_api_key: str,
) -> Page:
    """Navigate to the admin SPA with real API key — all mutations allowed.

    Two modes:
      1. **Local Vite** (default): starts a Vite dev server on localhost:3300,
         rewrites cross-origin API calls through the Vite proxy.
      2. **Deployed SPA** (LIVE_SPA_BASE_URL set): navigates directly to the
         deployed admin SPA.  No Vite, no proxy rewriting.  SPA and API share
         the same origin, so no CORS issues.

    SPEC-1655: No mutation guards — staging is a testing environment where
    ALL operations (POST, PUT, DELETE) must be exercised.
    """
    if LIVE_SPA_BASE_URL:
        # --- Deployed SPA mode ---
        page.add_init_script(f"""
            sessionStorage.setItem('agentred_api_key', '{live_api_key}');
            sessionStorage.setItem('agentred-onboarding-dismissed', 'true');
        """)
        page.goto(
            f"{LIVE_SPA_BASE_URL}/?tenant={LIVE_TENANT_ID}",
            wait_until="load",
        )
    else:
        # --- Local Vite mode ---
        # Rewrite cross-origin API calls to go through local Vite proxy.
        _attach_api_proxy_rewrite(page)

        # Inject real auth key + suppress auto-opening OnboardingWizard
        # into sessionStorage before any page JS runs.
        # The wizard checks this flag in a useEffect; setting it via
        # addInitScript ensures it's present BEFORE React hydrates,
        # eliminating the race condition where the wizard opens after
        # _dismiss_onboarding_modal() has already run.
        page.add_init_script(f"""
            sessionStorage.setItem('agentred_api_key', '{live_api_key}');
            sessionStorage.setItem('agentred-onboarding-dismissed', 'true');
        """)

        # Navigate to the admin SPA with tenant identification (SPEC-1644/SPEC-1645)
        # S134: Use "load" instead of "networkidle" — live SPAs have persistent
        # API connections (SSE, polling) that prevent networkidle from resolving.
        # The explicit wait_for_selector("Dashboard") below ensures content is ready.
        page.goto(
            f"http://localhost:{ADMIN_VITE_PORT}/admin/standalone/?tenant={LIVE_TENANT_ID}",
            wait_until="load",
        )

    # Wait for the Dashboard to load with real data
    page.wait_for_selector("text=Dashboard", timeout=20_000)

    # Dismiss the OnboardingWizard if it appears (freshly-seeded tenants)
    _dismiss_onboarding_modal(page)

    return page


@pytest.fixture()
def live_dashboard_page(live_admin_page: Page) -> Page:
    """Return the admin page already on the Dashboard."""
    return live_admin_page


@pytest.fixture()
def live_team_page(live_admin_page: Page) -> Page:
    """Navigate to the Team members page with real data."""
    return _navigate_admin_to(live_admin_page, "Team members", "Team members")


@pytest.fixture()
def live_config_page(live_admin_page: Page) -> Page:
    """Navigate to the Agent configuration page with real data."""
    return _navigate_admin_to(live_admin_page, "Agent configuration", "Configuration")


@pytest.fixture()
def live_widget_page(live_admin_page: Page) -> Page:
    """Navigate to the Widget configuration page with real data."""
    return _navigate_admin_to(live_admin_page, "Widget configuration", "Widget")


@pytest.fixture()
def live_inbox_page(live_admin_page: Page) -> Page:
    """Navigate to the Inbox page with real data.

    After clicking Inbox in the sidebar, waits for conversation data to
    load from the API — either conversation items (containing 'messages')
    or the 'No conversations' empty state.
    """
    _navigate_admin_to(live_admin_page, "Inbox", "Inbox")

    # Wait for conversation data to load: either "N messages" text from
    # conversation items, or "No conversations" empty state, or filter
    # tab counts like "All (N)".
    try:
        live_admin_page.wait_for_selector(
            "text=/messages|No conversations|All \\(\\d/i",
            timeout=15_000,
        )
    except Exception:
        # If neither appears within 15 s, proceed anyway — individual
        # tests will assert and fail with a clear error message.
        pass

    # Extra settle time for remaining React renders
    live_admin_page.wait_for_timeout(1000)
    return live_admin_page


@pytest.fixture()
def live_kb_page(live_admin_page: Page) -> Page:
    """Navigate to the Knowledge base page with real data."""
    return _navigate_admin_to(live_admin_page, "Knowledge base", "Knowledge")


@pytest.fixture()
def live_billing_page(live_admin_page: Page) -> Page:
    """Navigate to the Billing page with real data."""
    return _navigate_admin_to(live_admin_page, "Billing", "Billing")


@pytest.fixture()
def live_integrations_page(live_admin_page: Page) -> Page:
    """Navigate to the Integrations page with real data."""
    return _navigate_admin_to(live_admin_page, "Integrations", None)


@pytest.fixture()
def live_memory_page(live_admin_page: Page) -> Page:
    """Navigate to the Memory & privacy page with real data.

    Skips if the page heading doesn't appear (non-Professional tier).
    """
    _navigate_admin_to(live_admin_page, "Memory & privacy", None)
    try:
        live_admin_page.wait_for_selector("text=Memory", timeout=5_000)
    except Exception:
        pytest.skip("Memory & privacy page not available (tier restriction)")
    return live_admin_page


@pytest.fixture()
def live_quick_actions_page(live_admin_page: Page) -> Page:
    """Navigate to the Quick actions page with real data."""
    return _navigate_admin_to(live_admin_page, "Quick actions", "Quick actions")
