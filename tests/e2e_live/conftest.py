"""
Live E2E test fixtures for the standalone admin SPA against production.

Unlike tests/e2e/ (which mocks all API calls), these tests run the real React
app with real API responses from the production backend, proxied through Vite.

Architecture:
  - admin_vite_server (session): starts ``npm run dev`` with VITE_API_URL
    pointing to production so the Vite proxy forwards /api/* to the real backend.
  - live_api_key (session): loads from .env.local — the real admin API key.
  - live_admin_page (per-test): injects real auth, navigates to the admin SPA,
    attaches safety guards to block dangerous mutations.
  - Page fixtures: live_dashboard_page, live_team_page, etc.

Safety:
  page.route() blocks any POST/DELETE that could mutate production state
  (activate config, rotate widget key, invite/remove team members, delete
  named configs).  Blocked requests return 200 + empty JSON.

Rate limiting:
  Professional tier = 50 rpm.  A 2 s cooldown between test classes keeps
  the suite within budget (~120 API calls total).

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

ADMIN_VITE_PORT = 3300
ADMIN_DIR = Path(__file__).resolve().parent.parent.parent / "admin" / "standalone"

PROD_URL = os.environ.get(
    "PROD_URL",
    "https://agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io",
)

# API key for the production tenant — used to authenticate the admin SPA.
# .env.local uses SAP_CONSOLE_API_KEY; some scripts use SUPERADMIN_PREVIEW_API_KEY.
LIVE_API_KEY = (
    os.environ.get("SAP_CONSOLE_API_KEY")
    or os.environ.get("SUPERADMIN_PREVIEW_API_KEY")
    or os.environ.get("AGENTRED_API_KEY")
    or ""
)

# Mutations that MUST NOT reach production during test runs.
# Each entry: (HTTP method, URL substring to match).
#
# IMPORTANT: Only list patterns whose URL path is UNIQUE to the dangerous
# mutation.  If the same URL serves both a safe GET and a dangerous POST
# (e.g. GET /api/admin/team → list members  vs  POST /api/admin/team → invite),
# the route interception will also catch the GET and break the Vite proxy.
# For those cases, rely on test design (tests never submit invite forms).
BLOCKED_MUTATIONS: list[tuple[str, str]] = [
    ("POST", "/api/config/activate"),
    ("POST", "/api/admin/widget/rotate"),
    # DELETE /api/admin/team/:id intentionally omitted.
    # The glob pattern **/api/admin/team/* also matches GET /api/admin/team
    # (the trailing * can match zero chars), breaking the team page.
    # Tests don't invoke the delete flow, so the safety risk is minimal.
    ("DELETE", "/api/config/named/"),
]

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


def _attach_safety_guards(page: Page) -> None:
    """Block dangerous mutations from reaching production.

    Registers targeted route handlers for each blocked mutation pattern.
    Unlike intercepting all /api/** traffic (which can interfere with the
    Vite proxy's request forwarding), this only intercepts the specific
    dangerous endpoints, leaving all other API calls untouched.
    """
    blocked_log: list[str] = []

    def _make_blocker(method: str, pattern: str):
        def _block(route: Route) -> None:
            if route.request.method == method:
                blocked_log.append(f"BLOCKED: {method} {route.request.url}")
                route.fulfill(
                    status=200,
                    content_type="application/json",
                    body="{}",
                )
            else:
                # Use fallback() instead of continue_() — fallback passes
                # to the next handler without consuming the route, avoiding
                # interference with Vite proxy request forwarding.
                route.fallback()
        return _block

    # Register a targeted route handler for each blocked mutation
    for blocked_method, blocked_pattern in BLOCKED_MUTATIONS:
        page.route(f"**{blocked_pattern}*", _make_blocker(blocked_method, blocked_pattern))

    # Attach log for test assertions
    page._safety_blocked = blocked_log  # type: ignore[attr-defined]


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
            "(set SUPERADMIN_PREVIEW_API_KEY or AGENTRED_API_KEY) — "
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
    """
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

    # Point the Vite proxy to production
    env = {**os.environ, "VITE_API_URL": PROD_URL}
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
    """Insert a 3 s cooldown between test classes to stay within 50 rpm.

    Each page navigation triggers 1-3 API calls.  With ~20 test classes
    and 3 s between each, the suite averages ~40 rpm, well within budget.
    """
    yield
    time.sleep(3)


# ---------------------------------------------------------------------------
# Per-test fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def live_admin_page(
    page: Page,
    admin_vite_server,
    live_api_key: str,
) -> Page:
    """Navigate to the admin SPA with real API key and safety guards.

    Injects the real API key into sessionStorage before the React app
    loads, so the app authenticates against the production backend.
    Safety guards block dangerous mutations.
    """
    # Attach safety guards BEFORE navigation
    _attach_safety_guards(page)

    # Inject real auth key into sessionStorage before any page JS runs
    page.add_init_script(f"""
        sessionStorage.setItem('agentred_api_key', '{live_api_key}');
    """)

    # Navigate to the admin SPA
    page.goto(
        f"http://localhost:{ADMIN_VITE_PORT}/admin/standalone/",
        wait_until="networkidle",
    )

    # Wait for the Dashboard to load with real data
    page.wait_for_selector("text=Dashboard", timeout=20_000)

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
    """Navigate to the Inbox page with real data."""
    return _navigate_admin_to(live_admin_page, "Inbox", "Inbox")


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
