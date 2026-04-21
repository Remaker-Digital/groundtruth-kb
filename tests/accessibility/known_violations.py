"""Known pre-existing axe violations baselined at WI-3166 introduction.

Baseline semantics:
  - Maps page name → {axe_rule_id: max_affected_node_count}
  - Tests FAIL on any NEW critical/serious rule not in the baseline
  - Tests FAIL if an existing rule's node count EXCEEDS the baseline
  - Tests FAIL if a baselined rule NO LONGER fires (forces cleanup)
  - Remove entries as violations are fixed

Owner acceptance: Mike accepted count-based baseline 2026-04-12 (S282).
Decision cited in bridge/axe-core-ci-enforcement-013.md.
Remediation tracked as follow-up work.

Expiry: All entries must be eliminated before next production release.
Remediation priority: critical rules first, then serious.

Source: Local axe scan run S282 against admin/standalone dev:mock.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

# Maps page name → {axe_rule_id: max_affected_element_count}.
# When a violation is fixed, remove it. The test will fail on stale entries.
KNOWN_VIOLATIONS: dict[str, dict[str, int]] = {
    "Dashboard": {
        "aria-progressbar-name": 5,  # Mantine Progress/LoadingOverlay
    },
    "Configuration": {
        "aria-input-field-name": 1,  # Mantine input without field name
        "button-name": 6,  # Icon-only buttons missing aria-label
        "color-contrast": 3,  # Mantine theme color contrast
        "label": 6,  # Form inputs without associated labels
    },
    "Inbox": {
        "button-name": 2,  # Icon-only action buttons
        "scrollable-region-focusable": 1,  # Split-panel scroll area
    },
    "Analytics": {
        "aria-progressbar-name": 5,  # Mantine Progress/LoadingOverlay
    },
    "Team": {
        "color-contrast": 14,  # Mantine theme color contrast
        "select-name": 4,  # Mantine Select without accessible name
    },
    "Knowledge Base": {
        "button-name": 18,  # Icon-only action buttons on KB entries
        "color-contrast": 1,  # Mantine theme color contrast
    },
    "Integrations": {
        "color-contrast": 13,  # Mantine theme color contrast
    },
    "Billing": {
        "color-contrast": 11,  # Mantine theme color contrast
    },
    "Widget": {
        "aria-input-field-name": 2,  # Mantine input without field name
        "color-contrast": 7,  # Mantine theme color contrast
        "label": 3,  # Form inputs without associated labels
    },
}
