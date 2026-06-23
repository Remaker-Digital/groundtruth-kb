"""SPEC-1744 changelog deployed-version entry coverage.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
"""

import re
from pathlib import Path

import pytest

pytestmark = pytest.mark.local_env

ROOT = Path(__file__).resolve().parents[2]
CHANGELOG = ROOT / "docs-site" / "docs" / "changelog.md"


def _changelog_markdown() -> str:
    return CHANGELOG.read_text(encoding="utf-8")


def _version_section(version: str) -> str:
    markdown = _changelog_markdown()
    pattern = re.compile(r"^## (?P<version>v\d+\.\d+\.\d+)\b.*$", re.MULTILINE)
    matches = list(pattern.finditer(markdown))

    for index, match in enumerate(matches):
        if match.group("version") != version:
            continue
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
        return markdown[match.start() : end]

    raise AssertionError(f"Changelog must include {version}")


def _assert_terms(section: str, terms: list[str]) -> None:
    for term in terms:
        assert term in section


def test_v182_staging_entry_documents_mock_dev_and_admin_ui_polish() -> None:
    section = _version_section("v1.82.0")

    _assert_terms(
        section,
        [
            "Mock Dev Environment and Admin UI Polish",
            "Staging, 2026-03-11",
            "Mock development environment",
            "Zero-backend UI development",
            "npm run dev:mock",
            "mock API handlers",
            "mock E2E tests",
            "Admin UI improvements",
            "Auto-save on focus out",
            "focus leaves a field",
            "Agent identity",
            "Policy overrides",
            "Integrations mock data",
        ],
    )


def test_v181_production_entry_documents_auth_rate_limit_and_ci() -> None:
    section = _version_section("v1.81.0")

    _assert_terms(
        section,
        [
            "Auth Hardening, Rate Limit Backend, and CI/CD",
            "Production, 2026-03-10",
            "Authentication hardening",
            "Inactivity auto-logout",
            "Cross-tab token protection",
            "Clickjacking protection",
            "Rate limit backend",
            "RateLimitBackend",
            "CI/CD pipeline",
            "GitHub Actions workflow",
            "ruff",
            "pyright",
            "pytest",
            "bandit + safety",
            "Makefile targets",
            "Superadmin API split",
        ],
    )


def test_deployed_version_entries_are_newest_first() -> None:
    markdown = _changelog_markdown()
    v182_position = markdown.find("## v1.82.0")
    v181_position = markdown.find("## v1.81.0")

    assert v182_position != -1
    assert v181_position != -1
    assert v182_position < v181_position
