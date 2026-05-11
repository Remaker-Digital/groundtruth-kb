"""Accessibility testing helpers (SPEC-1846/WI-1504).

Provides axe-core integration for WCAG 2.1 AA compliance testing via
axe-playwright-python. Fails on critical and serious violations; logs
minor and moderate.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def assert_no_critical_a11y_violations(page: Any) -> dict[str, Any]:
    """Run axe-core on the page and assert no critical/serious violations.

    Args:
        page: Playwright Page object with loaded content.

    Returns:
        Full axe results dict for further inspection if needed.

    Raises:
        AssertionError: If any critical or serious violations are found.
        ImportError: If axe-playwright-python is not installed.
    """
    try:
        from axe_playwright_python.sync_playwright import Axe
    except ImportError:
        raise ImportError(
            "axe-playwright-python is required for accessibility testing. "
            "Install it with: pip install axe-playwright-python"
        )

    axe = Axe()
    results = axe.run(page)

    # Separate violations by impact level
    critical_violations = []
    serious_violations = []
    minor_violations = []

    for violation in results.response.get("violations", []):
        impact = violation.get("impact", "minor")
        if impact == "critical":
            critical_violations.append(violation)
        elif impact == "serious":
            serious_violations.append(violation)
        else:
            minor_violations.append(violation)

    # Log minor/moderate violations (informational, do not fail)
    if minor_violations:
        logger.info(
            "a11y: %d minor/moderate violations (non-blocking): %s",
            len(minor_violations),
            [v.get("id") for v in minor_violations],
        )

    # Fail on critical and serious violations
    blocking = critical_violations + serious_violations
    if blocking:
        details = []
        for v in blocking:
            nodes = v.get("nodes", [])
            targets = [n.get("target", []) for n in nodes[:3]]
            details.append(
                f"  [{v.get('impact')}] {v.get('id')}: {v.get('description')} "
                f"(affects {len(nodes)} element(s), e.g. {targets})"
            )
        detail_str = "\n".join(details)
        raise AssertionError(
            f"{len(blocking)} critical/serious accessibility violation(s) found:\n{detail_str}"
        )

    return results.response
