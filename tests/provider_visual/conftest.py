"""Provider Console visual regression test fixtures (SPEC-2104 / WI-3167).

Session-scoped Vite mock dev server with tenant-aware navigation.
Same pattern as tests/accessibility/conftest.py but for visual regression.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import os
import re
import subprocess
import time
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ADMIN_STANDALONE = PROJECT_ROOT / "admin" / "standalone"
MOCK_TENANT = "mock-tenant-001"
MOCK_API_KEY = "mock-api-key-for-testing"
VITE_STARTUP_TIMEOUT = 30  # seconds


@pytest.fixture(scope="session")
def vr_base_url():
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


def navigate_vr(page, base_url: str, path: str) -> None:
    """Navigate to an admin page with tenant param and wait for load."""
    separator = "&" if "?" in path else "?"
    url = f"{base_url}{path}{separator}tenant={MOCK_TENANT}"
    page.goto(url)
    page.wait_for_load_state("networkidle")
