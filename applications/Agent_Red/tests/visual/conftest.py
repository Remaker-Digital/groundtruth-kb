"""
Shared fixtures for visual regression tests.

Manages the Vite dev server lifecycle and provides pre-configured Playwright
pages with mocked API responses for deterministic widget testing.

Architecture:
  - vite_server (session): starts `npm run dev` in widget/, waits for port 3100
  - mock_config: the WidgetConfig dict returned by the mocked /api/config
  - widget_page: navigates to dev.html with API mocking, waits for SDK ready
  - widget_panel: opens the panel and returns a FrameLocator for the iframe

The widget uses a closed Shadow DOM for the launcher (inaccessible to
Playwright) and a same-origin iframe for the panel. All panel assertions
operate on the iframe via `page.frame_locator('iframe[title="Agent Red Chat"]')`.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import json
import os
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest
from playwright.sync_api import FrameLocator, Page, Route

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VITE_PORT = 3100
WIDGET_DIR = Path(__file__).resolve().parent.parent.parent / "widget"

# Minimal WidgetConfig that exercises all visual branches: light mode,
# standard panel, greeting enabled, default Agent Red branding.
MOCK_WIDGET_CONFIG: dict = {
    "widget_primary_color": "#ff3621",
    "widget_background_color": "#FFFFFF",
    "widget_position": "bottom-right",
    "widget_offset_x": 20,
    "widget_offset_y": 20,
    "widget_agent_avatar_url": None,
    "widget_agent_display_name": "Agent Red",
    "widget_agent_title": "AI Assistant",
    "widget_logo_url": None,
    "widget_show_branding": True,
    "widget_mobile_enabled": True,
    "widget_dark_mode": False,
    "widget_color_mode": "light",
    "widget_header_gradient_end": None,
    "widget_font_family": None,
    "widget_border_radius": None,
    "widget_launcher_size": None,
    "widget_launcher_icon": "chat",
    "widget_launcher_shape": "circle",
    "widget_header_title": None,
    "widget_header_subtitle": None,
    "widget_header_text": None,
    "widget_input_placeholder": None,
    "widget_agent_bubble_color": None,
    "widget_agent_bubble_text_color": None,
    "widget_customer_bubble_color": None,
    "widget_customer_bubble_text_color": None,
    "widget_offline_message": None,
    "widget_auto_open": False,
    "widget_auto_open_delay": None,
    "widget_operating_hours": None,
    "widget_offline_behavior": "ai_only",
    "widget_prechat_form": None,
    "widget_chat_rating_enabled": True,
    "widget_sound_enabled": False,  # disable sound for headless testing
    "widget_file_upload_enabled": False,
    "widget_greeting_enabled": True,
    "widget_greeting_message": "Hi there! How can I help you today?",
    "widget_pre_chat_form_enabled": False,
    "widget_pre_chat_fields": None,
    "widget_offline_form_enabled": False,
    "widget_page_rules": None,
    "widget_shadow_intensity": "standard",
    "widget_position_offset_x": None,
    "widget_position_offset_y": None,
    "widget_panel_width": "standard",
    "widget_quick_actions": None,
    "brand_name": "Test Brand",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _port_is_open(port: int, host: str = "localhost") -> bool:
    """Check if a TCP port is accepting connections.

    Checks both IPv4 (127.0.0.1) and IPv6 (::1) because Vite on Windows
    often binds to IPv6 only, while Python's 'localhost' may resolve to IPv4.
    """
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


# ---------------------------------------------------------------------------
# Session-scoped fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def vite_server():
    """Start the Vite dev server for the widget.

    Launches ``npm run dev`` in ``widget/`` and waits up to 30 s for port 3100
    to accept connections.  Tears down on session end.

    Skips the entire test session if ``widget/node_modules`` does not exist
    (prevents confusing failures on CI without frontend deps).
    """
    node_modules = WIDGET_DIR / "node_modules"
    if not node_modules.exists():
        pytest.skip("widget/node_modules not found — run `cd widget && npm install` first")

    # If a dev server is already running on the port, reuse it
    if _port_is_open(VITE_PORT):
        yield None  # external server — we don't manage it
        return

    # On Windows, use CREATE_NEW_PROCESS_GROUP so we can send CTRL_BREAK
    # to cleanly terminate the Vite + Node process tree.
    creation_flags = 0
    if sys.platform == "win32":
        creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP

    proc = subprocess.Popen(
        "npm run dev",
        cwd=str(WIDGET_DIR),
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=creation_flags,
    )

    # Wait for the dev server to be ready
    for _ in range(30):
        if _port_is_open(VITE_PORT):
            break
        if proc.poll() is not None:
            # Process exited prematurely
            stdout = proc.stdout.read().decode(errors="replace") if proc.stdout else ""
            stderr = proc.stderr.read().decode(errors="replace") if proc.stderr else ""
            raise RuntimeError(
                f"Vite dev server exited with code {proc.returncode}.\n"
                f"stdout: {stdout}\nstderr: {stderr}"
            )
        time.sleep(1)
    else:
        proc.kill()
        raise RuntimeError(f"Vite dev server did not start on port {VITE_PORT} within 30 s")

    yield proc

    # Teardown — kill the entire process tree on Windows
    if sys.platform == "win32":
        try:
            os.kill(proc.pid, signal.CTRL_BREAK_EVENT)
            proc.wait(timeout=5)
        except (OSError, subprocess.TimeoutExpired):
            # Force-kill via taskkill to get the whole tree
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
# Per-test fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def mock_config() -> dict:
    """Return a mutable copy of the default mock WidgetConfig.

    Tests can override specific fields before passing to ``widget_page``::

        def test_dark_mode(mock_config, page, vite_server):
            mock_config["widget_color_mode"] = "dark"
            # ... use make_widget_page(page, mock_config)
    """
    return {**MOCK_WIDGET_CONFIG}


@pytest.fixture()
def widget_page(page: Page, vite_server, mock_config: dict) -> Page:
    """Navigate to the widget dev page with a mocked /api/config.

    Returns the Playwright ``Page`` after the widget SDK is ready.
    The widget is still *closed* (launcher visible, panel not created yet).
    """
    # Intercept the config fetch — the widget calls GET <api-url>/api/config
    def _handle_config(route: Route) -> None:
        route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps({"config": mock_config}),
        )

    page.route("**/api/config*", _handle_config)

    # Also intercept conversation start (prevents network errors in console)
    def _handle_conversation(route: Route) -> None:
        route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps({"conversation_id": "test-conv-001"}),
        )

    page.route("**/api/conversations*", _handle_conversation)

    # Navigate to the dev harness
    page.goto(f"http://localhost:{VITE_PORT}/dev.html", wait_until="domcontentloaded")

    # Wait for the widget SDK to be available on window
    page.wait_for_function("!!window.AgentRed", timeout=10_000)

    return page


@pytest.fixture()
def widget_panel(widget_page: Page) -> FrameLocator:
    """Open the widget panel and return a FrameLocator for the panel iframe.

    The fixture:
      1. Calls ``window.AgentRed.open()`` to create the panel iframe
      2. Waits for the iframe to appear in the DOM
      3. Waits for the panel root element to render inside the iframe
      4. Returns a ``FrameLocator`` scoped to the panel iframe

    All assertions on panel content should use this locator::

        def test_header(widget_panel):
            expect(widget_panel.locator("text=Chat with us")).to_be_visible()
    """
    # Open the widget via its SDK (avoids closed Shadow DOM)
    widget_page.evaluate("window.AgentRed.open()")

    # Wait for the iframe to appear
    widget_page.wait_for_selector(
        'iframe[title="Agent Red Chat"]',
        state="attached",
        timeout=5_000,
    )

    # Wait for the open transition to settle (opacity 0→1, 200ms)
    widget_page.wait_for_timeout(400)

    # Return a FrameLocator for the panel iframe
    frame = widget_page.frame_locator('iframe[title="Agent Red Chat"]')

    # Verify the panel root rendered
    frame.locator("#ar-panel-root").wait_for(state="attached", timeout=5_000)

    return frame
