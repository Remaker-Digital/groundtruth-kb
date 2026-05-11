# (C) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Shared fixtures for SPEC-1706 mock-based frontend E2E tests.

Manages a session-scoped Vite dev server running in mock mode, plus
class-scoped and function-scoped Playwright page fixtures with store
reset between mutation tests.
"""
import os
import re
import subprocess
import time
from pathlib import Path
from urllib.parse import urlparse

import pytest
from playwright.sync_api import Page

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ADMIN_STANDALONE = PROJECT_ROOT / "admin" / "standalone"
MOCK_TENANT = "mock-tenant-001"
MOCK_API_KEY = "mock-api-key-for-testing"
VITE_STARTUP_TIMEOUT = 30  # seconds

# Cache the API origin (extracted once from mock_base_url)
_api_origin_cache = None


def api_origin(mock_base_url: str) -> str:
    """Extract origin (scheme://host:port) from a Vite base URL.

    Vite serves the SPA at /admin/standalone/ but mock API middleware
    intercepts at /api/* (root path). This helper strips the base path.
    """
    global _api_origin_cache
    if _api_origin_cache is None:
        parsed = urlparse(mock_base_url)
        _api_origin_cache = f"{parsed.scheme}://{parsed.netloc}"
    return _api_origin_cache


# ---------------------------------------------------------------------------
# Session-scoped: start Vite dev server once for the entire test run
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def mock_base_url():
    """Start npm run dev:mock and yield the base URL (e.g. http://localhost:5173/admin/standalone)."""
    env = {**os.environ, "BROWSER": "none", "NO_COLOR": "1"}  # prevent auto-open + disable ANSI
    # shell=True needed on Windows where npm is a .cmd script
    proc = subprocess.Popen(
        "npm run dev:mock",
        cwd=str(ADMIN_STANDALONE),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=env,
        shell=True,
    )

    base_url = None
    deadline = time.time() + VITE_STARTUP_TIMEOUT

    while time.time() < deadline:
        line = proc.stdout.readline()
        if not line:
            if proc.poll() is not None:
                break
            continue
        # Vite prints "Local:   http://localhost:5173/admin/standalone/" when ready
        m = re.search(r"Local:\s*(https?://\S+)", line)
        if m:
            base_url = m.group(1).rstrip("/")
            break

    if not base_url:
        proc.terminate()
        pytest.fail("Vite dev server did not start within timeout")

    yield base_url

    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()


# ---------------------------------------------------------------------------
# Browser context
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def browser_context(browser, mock_base_url):
    """Session-scoped browser context with mock auth pre-injected.

    The SPA checks sessionStorage for 'agentred_api_key' on mount.
    Without it, all pages render the login form instead of the admin UI.
    We inject a mock key via add_init_script so every new page is
    automatically authenticated before the React app mounts.
    """
    context = browser.new_context(
        viewport={"width": 1280, "height": 800},
        base_url=mock_base_url,
    )
    # Inject mock API key into sessionStorage BEFORE any page JS runs.
    # This bypasses the ApiKeyLogin gate in admin/standalone/index.tsx.
    context.add_init_script(f"""
        try {{
            sessionStorage.setItem('agentred_api_key', '{MOCK_API_KEY}');
        }} catch (e) {{
            // sessionStorage unavailable — tests will see login page
        }}
    """)
    yield context
    context.close()


# ---------------------------------------------------------------------------
# Class-scoped: shared page for read-only tests (faster)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="class")
def shared_page(browser_context, mock_base_url) -> Page:
    """One browser page per test class -- for read-only assertions only."""
    page = browser_context.new_page()
    yield page
    page.close()


# ---------------------------------------------------------------------------
# Function-scoped: fresh page with store reset for mutation tests
# ---------------------------------------------------------------------------

@pytest.fixture(scope="function")
def page(browser_context, mock_base_url) -> Page:
    """Fresh page with store reset -- for CRUD/mutation tests."""
    page = browser_context.new_page()
    # Reset mock store to initial fixture state (API at origin, not base path)
    origin = api_origin(mock_base_url)
    resp = page.request.post(f"{origin}/api/__test__/reset")
    assert resp.status == 200, f"Store reset failed: {resp.status}"
    yield page
    page.close()


# ---------------------------------------------------------------------------
# Navigation helpers
# ---------------------------------------------------------------------------

def navigate_to(page: Page, path: str, mock_base_url: str, wait: str = "networkidle"):
    """Navigate to an admin page with tenant param and wait for load."""
    separator = "&" if "?" in path else "?"
    url = f"{mock_base_url}{path}{separator}tenant={MOCK_TENANT}"
    page.goto(url)
    page.wait_for_load_state(wait)


def navigate_and_settle(page: Page, path: str, mock_base_url: str):
    """Navigate and wait for both network idle and DOM settle."""
    navigate_to(page, path, mock_base_url)
    page.wait_for_timeout(500)


def dismiss_onboarding_if_present(page: Page):
    """Dismiss the onboarding wizard modal if it appears."""
    try:
        close_btn = page.locator("[data-testid=\"close-wizard\"], .mantine-Modal-close").first
        if close_btn.is_visible(timeout=2000):
            close_btn.click()
            page.wait_for_timeout(300)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Assertion helpers — API calls use origin (not Vite base path)
# ---------------------------------------------------------------------------

def assert_mock_active(page: Page, mock_base_url: str):
    """Verify the mock API is active by checking X-Mock header."""
    origin = api_origin(mock_base_url)
    resp = page.request.get(f"{origin}/api/health")
    assert resp.status == 200
    assert resp.headers.get("x-mock") == "true", "Mock API not active"


def get_api_json(page: Page, mock_base_url: str, path: str) -> dict:
    """Fetch a mock API endpoint and return parsed JSON."""
    origin = api_origin(mock_base_url)
    resp = page.request.get(f"{origin}{path}")
    assert resp.status == 200, f"API {path} returned {resp.status}"
    return resp.json()


def post_api_json(page: Page, mock_base_url: str, path: str, data: dict = None) -> dict:
    """POST to a mock API endpoint and return parsed JSON.

    Uses ``data`` for JSON-serialised body so the mock plugin's
    ``readBody → JSON.parse()`` can parse it correctly.
    """
    origin = api_origin(mock_base_url)
    if data is not None:
        import json as _json
        resp = page.request.post(
            f"{origin}{path}",
            data=_json.dumps(data),
            headers={"Content-Type": "application/json"},
        )
    else:
        resp = page.request.post(f"{origin}{path}")
    return resp.json()


def main_text(page: Page) -> str:
    """Get visible text from main content area."""
    main = page.locator("main, [role=\"main\"], .mantine-AppShell-main").first
    return main.inner_text() if main.count() > 0 else page.locator("body").inner_text()
