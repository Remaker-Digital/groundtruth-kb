"""SPEC-1740 setup-guide documentation coverage.

These tests keep the authoritative Docusaurus source and shipped static HTML
aligned on the first-login magic-link flow.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
"""

from html.parser import HTMLParser
from pathlib import Path

import pytest

pytestmark = pytest.mark.local_env

ROOT = Path(__file__).resolve().parents[2]
SETUP_MD = ROOT / "docs-site" / "docs" / "getting-started" / "setup.md"
SETUP_HTML = ROOT / "docs" / "getting-started" / "setup.html"


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        stripped = data.strip()
        if stripped:
            self.parts.append(stripped)


def _html_text(markup: str) -> str:
    parser = _TextExtractor()
    parser.feed(markup)
    return " ".join(parser.parts)


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


def _html_section(markup: str, start_id: str, end_id: str) -> str:
    start = markup.index(f'id="{start_id}"')
    end = markup.index(f'id="{end_id}"', start)
    return markup[start:end]


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


def test_setup_html_first_login_matches_shipped_static_page() -> None:
    markup = SETUP_HTML.read_text(encoding="utf-8")
    text = _html_text(markup)

    _assert_in_order(
        markup,
        'id="1-account-provisioning"',
        'id="first-login"',
        'id="2-api-key-configuration"',
    )
    _assert_in_order(
        text,
        "1. Account provisioning",
        "First login",
        "2. API key configuration",
    )

    first_login_markup = _html_section(markup, "first-login", "2-api-key-configuration")
    first_login_text = _html_text(first_login_markup)

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
        assert required_text in first_login_text

    assert "First login magic link sequence diagram" in first_login_markup
    assert "sequenceDiagram" in first_login_markup
    assert 'href="/docs/admin-guide/mfa-security"' in first_login_markup


def test_setup_html_no_longer_claims_api_keys_arrive_by_email() -> None:
    markup = SETUP_HTML.read_text(encoding="utf-8")
    text = _html_text(markup)

    assert "API key is delivered in your welcome email" not in text
    assert "Authorization: Bearer YOUR_API_KEY" not in markup
    assert "X-API-Key: YOUR_API_KEY" in markup
    assert "X-Widget-Key: YOUR_WIDGET_KEY" in markup
