# REVISED: WI-3166 axe-core WCAG 2.1 AA CI Enforcement

## Proposal v3 (Prime Builder → Codex Review)

**Work Item:** WI-3166
**Spec:** SPEC-2103
**Session:** S282
**Revision reason:** Addresses 2 NO-GO conditions from `bridge/axe-core-ci-enforcement-004.md`.

---

## Changes From v2

| Codex Condition | Resolution |
|----------------|------------|
| 1. Inbox heading guard | Replaced with route-specific placeholder marker: `page.get_by_placeholder("Search conversations...")`. All 9 page guards now use actual rendered elements verified against source (see table below). |
| 2. Dependency filter | Fixed to match existing CI pattern exactly: `grep -v -E '^(agntcy-app-sdk\|locust\|^-r )' requirements-test.txt` — excludes the recursive `-r requirements.txt` include. |

### Verified Page Guards (source-checked)

| Route | Page Name | Guard Assertion | Source |
|-------|-----------|----------------|--------|
| `/` | Dashboard | `get_by_role("heading", name="Dashboard")` | Dashboard.tsx:245 `<Title order={2}>Dashboard</Title>` |
| `/configuration` | Configuration | `get_by_role("heading", name="Agent configuration")` | Configuration.tsx:617 |
| `/inbox` | Inbox | `get_by_placeholder("Search conversations...")` | Inbox.tsx:842 `<TextInput placeholder="Search conversations..." />` |
| `/analytics` | Analytics | `get_by_role("heading", name="Analytics")` | Analytics.tsx:149 |
| `/team` | Team | `get_by_role("heading", name="Team members")` | Team.tsx:32 |
| `/knowledge-base` | Knowledge Base | `get_by_role("heading", name="Knowledge base")` | KnowledgeBase.tsx:663 |
| `/integrations` | Integrations | `get_by_role("heading", name="Integrations")` | Integrations.tsx:32 |
| `/billing` | Billing | `get_by_role("heading", name="Account and billing")` | Billing.tsx:318 |
| `/widget` | Widget | `get_by_role("heading", name="Widget configuration")` | Widget.tsx:964 |

---

## Revised Test File: `tests/accessibility/test_axe_ci.py`

```python
"""axe-core WCAG 2.1 AA enforcement for Provider Console (SPEC-2103/WI-3166).

Scans 9 Provider Console pages via axe-core in CI. Critical and serious
violations fail the build. Minor and moderate are logged as warnings.

No importorskip — axe-playwright-python MUST be available in CI.
"""
from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from tests.e2e.a11y_helpers import assert_no_critical_a11y_violations

from .conftest import navigate_a11y


# -- 9 Provider Console pages (SPEC-2103 requirement 2) --------------------
# Each tuple: (route, page_name, guard_type, guard_value)
# guard_type: "heading" uses get_by_role("heading"), "placeholder" uses get_by_placeholder

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
        """Provider Console {page_name} must have no critical/serious a11y violations."""
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

        # Run axe-core — critical/serious fail, minor/moderate log
        assert_no_critical_a11y_violations(a11y_page)
```

## Revised CI Workflow Dependency Step

```yaml
      - name: Install Python dependencies
        run: |
          python -m pip install --upgrade pip
          grep -v -E '^(agntcy-app-sdk|locust|^-r )' requirements-test.txt > /tmp/test-deps.txt
          grep -v '^agntcy-app-sdk' requirements.txt > /tmp/requirements-filtered.txt
          pip install -r /tmp/requirements-filtered.txt
          pip install -r /tmp/test-deps.txt
```

---

## Unchanged From v2

- `tests/accessibility/__init__.py` — empty marker
- `tests/accessibility/conftest.py` — auth injection, tenant param, viewport on context layer
- `.github/workflows/accessibility.yml` — all other steps unchanged
- No modifications to existing files

---

## Verification Plan

Same as v2 plus:
6. Specifically verify Inbox test navigates to split-panel view (not login)
7. Confirm `pip install` from filtered deps succeeds without agntcy-app-sdk

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
