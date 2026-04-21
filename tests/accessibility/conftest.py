"""Accessibility CI test fixtures (SPEC-2103 / WI-3166).

Session-scoped Vite mock dev server + authenticated browser context.
Pattern mirrors tests/e2e_mock/conftest.py with accessibility-specific
focus: deterministic viewport, auth pre-injection, tenant param in every
navigation, and page-rendered guards before axe runs.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import os
import re
import subprocess
import time
from pathlib import Path

import pytest
from playwright.sync_api import BrowserContext, Page

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ADMIN_STANDALONE = PROJECT_ROOT / "admin" / "standalone"
MOCK_TENANT = "mock-tenant-001"
MOCK_API_KEY = "mock-api-key-for-testing"
VITE_STARTUP_TIMEOUT = 30  # seconds


# -- Session-scoped: Vite mock dev server ----------------------------------


@pytest.fixture(scope="session")
def a11y_base_url():
    """Start npm run dev:mock and yield the base URL."""
    env = {**os.environ, "BROWSER": "none", "NO_COLOR": "1"}
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


# -- Session-scoped: browser context with auth + viewport ------------------


@pytest.fixture(scope="session")
def a11y_context(browser, a11y_base_url) -> BrowserContext:
    """Browser context at 1280x800 with mock auth pre-injected."""
    context = browser.new_context(
        viewport={"width": 1280, "height": 800},
        base_url=a11y_base_url,
    )
    context.add_init_script(f"""
        try {{
            sessionStorage.setItem('agentred_api_key', '{MOCK_API_KEY}');
        }} catch (e) {{}}
    """)
    yield context
    context.close()


# -- Function-scoped: fresh page per test ----------------------------------


@pytest.fixture()
def a11y_page(a11y_context) -> Page:
    """Fresh page for each accessibility test."""
    page = a11y_context.new_page()
    yield page
    page.close()


# -- Navigation helper with tenant param -----------------------------------


def navigate_a11y(page: Page, base_url: str, path: str) -> None:
    """Navigate to an admin page with tenant param and wait for load."""
    separator = "&" if "?" in path else "?"
    url = f"{base_url}{path}{separator}tenant={MOCK_TENANT}"
    page.goto(url)
    page.wait_for_load_state("networkidle")
