"""Current authored setup-guide instructions after stale HTML retirement.

The historical SPEC-1740 record is retired. The maintained Docusaurus Markdown
source retains the first-login and key-handling checks; this module does not
claim that a generated or remotely deployed site was built or exercised.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
"""

from pathlib import Path

import pytest

pytestmark = pytest.mark.local_env

ROOT = Path(__file__).resolve().parents[2]
SETUP_MD = ROOT / "docs-site" / "docs" / "getting-started" / "setup.md"


def _assert_in_order(haystack: str, *needles: str) -> None:
    cursor = -1
    for needle in needles:
        next_index = haystack.find(needle, cursor + 1)
        assert next_index != -1, f"Missing {needle!r}"
        assert next_index > cursor, f"{needle!r} appeared out of order"
        cursor = next_index


def _markdown_section(markdown: str, start_heading: str, end_heading: str) -> str:
    start = markdown.index(start_heading)
    end = markdown.index(end_heading, start)
    return markdown[start:end]


def test_setup_markdown_first_login_meets_spec_1740() -> None:
    markdown = SETUP_MD.read_text(encoding="utf-8")

    _assert_in_order(
        markdown,
        "## 1. Account provisioning",
        "## First login",
        "## 2. API key configuration",
    )
    first_login = _markdown_section(
        markdown,
        "## First login",
        "## 2. API key configuration",
    )

    for required_text in [
        "Sign in to Dashboard",
        "does not contain your API key",
        "Keys are never sent via email",
        "magic link",
        "one-time login link (expires in 15 minutes)",
        "8-hour session",
        "Account & billing",
        "API key and widget key",
        "Copy your API key to a password manager immediately",
    ]:
        assert required_text in first_login

    assert "```mermaid\nsequenceDiagram" in first_login
    assert "[Securing Agent Red](/docs/admin-guide/mfa-security)" in first_login


def test_setup_source_preserves_key_headers_and_never_promises_email_delivery() -> None:
    markdown = SETUP_MD.read_text(encoding="utf-8")
    assert "API key is delivered in your welcome email" not in markdown
    assert "Authorization: Bearer YOUR_API_KEY" not in markdown
    assert "X-API-Key: YOUR_API_KEY" in markdown
    assert "X-Widget-Key: YOUR_WIDGET_KEY" in markdown
