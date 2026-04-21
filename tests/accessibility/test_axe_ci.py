"""axe-core WCAG 2.1 AA enforcement for Provider Console (SPEC-2103 / WI-3166).

Scans 9 Provider Console pages via axe-core in CI. Fails on NEW critical/serious
violations not in the known-violations baseline. Pre-existing violations are
baselined and tracked for remediation. Minor/moderate are logged as warnings.

This module does NOT use importorskip — axe-playwright-python MUST be
available in CI. ImportError = hard fail (fail-closed design).

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging

import pytest
from axe_playwright_python.sync_playwright import Axe
from playwright.sync_api import Page, expect

from .conftest import navigate_a11y
from .known_violations import KNOWN_VIOLATIONS

logger = logging.getLogger(__name__)

# -- 9 Provider Console pages (SPEC-2103 requirement 2) --------------------
# Each tuple: (route, page_name, guard_type, guard_value)
# guard_type: "heading" uses get_by_role("heading"), "placeholder" uses get_by_placeholder
# Guard values verified against source — see bridge/axe-core-ci-enforcement-005.md

PROVIDER_CONSOLE_PAGES = [
    ("/", "Dashboard", "heading", "Dashboard"),
    ("/configuration", "Configuration", "heading", "Agent configuration"),
    ("/inbox", "Inbox", "placeholder", "Search conversations..."),
    ("/analytics", "Analytics", "heading", "Analytics"),
    ("/team", "Team", "heading", "Team members"),
    ("/knowledge-base", "Knowledge Base", "heading", "Knowledge base"),
    ("/integrations", "Integrations", "heading", "Integrations"),
    ("/billing", "Billing", "heading", "Account and billing"),
    ("/widget", "Widget", "heading", "Widget configuration"),
]


class TestProviderConsoleAccessibility:
    """WCAG 2.1 AA compliance for 9 Provider Console pages."""

    @pytest.mark.parametrize(
        "path,page_name,guard_type,guard_value",
        PROVIDER_CONSOLE_PAGES,
        ids=[p[1] for p in PROVIDER_CONSOLE_PAGES],
    )
    def test_page_a11y(
        self,
        a11y_page: Page,
        a11y_base_url: str,
        path: str,
        page_name: str,
        guard_type: str,
        guard_value: str,
    ) -> None:
        """Provider Console page must have no critical/serious a11y violations."""
        # Navigate with auth + tenant param
        navigate_a11y(a11y_page, a11y_base_url, path)

        # Guard: verify the intended page rendered, not the login page
        if guard_type == "heading":
            marker = a11y_page.get_by_role("heading", name=guard_value)
        elif guard_type == "placeholder":
            marker = a11y_page.get_by_placeholder(guard_value)
        else:
            raise ValueError(f"Unknown guard_type: {guard_type}")
        expect(marker.first).to_be_visible(timeout=10_000)

        # Run axe-core with count-based known-violations baseline
        known = KNOWN_VIOLATIONS.get(page_name, {})
        results = Axe().run(a11y_page)

        errors = []
        known_seen = set()
        for violation in results.response.get("violations", []):
            impact = violation.get("impact", "minor")
            rule_id = violation.get("id", "unknown")
            node_count = len(violation.get("nodes", []))

            if impact not in ("critical", "serious"):
                logger.info("a11y [%s] minor/moderate: %s", page_name, rule_id)
                continue

            if rule_id not in known:
                # NEW violation not in baseline — always fail
                errors.append(f"  NEW [{impact}] {rule_id}: {violation.get('description', '')} ({node_count} elements)")
            else:
                known_seen.add(rule_id)
                max_count = known[rule_id]
                if node_count > max_count:
                    # Count increased — new instances of baselined rule
                    errors.append(
                        f"  REGRESSION [{impact}] {rule_id}: {node_count} elements (baseline max: {max_count})"
                    )
                else:
                    logger.warning(
                        "a11y [%s] BASELINED %s: %s (%d/%d elements)",
                        page_name,
                        impact,
                        rule_id,
                        node_count,
                        max_count,
                    )

        # Enforce baseline cleanup: fail if a baselined rule was fixed
        stale = set(known.keys()) - known_seen
        for rule_id in sorted(stale):
            errors.append(
                f"  STALE BASELINE {rule_id}: no longer fires on {page_name}. Remove from known_violations.py."
            )

        if errors:
            raise AssertionError(f"{len(errors)} a11y issue(s) on {page_name}:\n" + "\n".join(errors))
