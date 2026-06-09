"""S131 — Record spec, WI, and test artifacts for widget config pipeline defect.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools" / "knowledge-db"))
import db  # noqa: E402

kdb = db.KnowledgeDB()
BY = "S131"

# ---------------------------------------------------------------------------
# Specification (GOV-09)
# ---------------------------------------------------------------------------

kdb.insert_spec(
    id="SPEC-1612",
    title="Widget Panel uses reactive store config for appearance",
    description=(
        "The widget Panel component must resolve design tokens and derived "
        "state (agent name, title, avatar, colors, gradient, branding, etc.) "
        "from the store's config rather than the initial config prop. The "
        "config prop is frozen at iframe creation time; the store's config "
        "is updated by setConfigPartial() (called by the admin UI preview "
        "and the SDK). Without this, draft-mode appearance changes and "
        "post-activation config updates have no effect until a full page "
        "reload. The pattern: `const activeConfig = state.config || config;` "
        "ensures the store value takes precedence when available, falling "
        "back to the initial prop on first render."
    ),
    status="implemented",
    changed_by=BY,
    change_reason="Owner defect: saved widget config did not take effect in draft or active mode",
    priority="P1",
    scope="widget_ui",
    section="WIDGET_UI",
    assertions=[
        {
            "description": "Panel.tsx resolves activeConfig from state.config with prop fallback",
            "type": "grep",
            "pattern": "state\\.config \\|\\| config",
            "path": "widget/src/components/Panel.tsx",
        },
        {
            "description": "Panel.tsx uses activeConfig for resolveTokens (not stale config prop)",
            "type": "grep",
            "pattern": "resolveTokens\\(activeConfig\\)",
            "path": "widget/src/components/Panel.tsx",
        },
    ],
)
print("SPEC-1612 recorded")

# ---------------------------------------------------------------------------
# Work Item
# ---------------------------------------------------------------------------

kdb.insert_work_item(
    id="WI-0934",
    title="Widget config not taking effect in draft mode or after activation",
    description=(
        "Panel.tsx resolved design tokens and derived state (agent name, "
        "title, avatar, colors, gradients, branding, pre-chat, offline, "
        "consent, placeholder) from the `config` prop passed at iframe "
        "creation time. This prop is frozen — it never updates when "
        "setConfigPartial() is called by the admin UI or SDK. The store's "
        "`state.config` IS updated but Panel ignored it for token resolution "
        "and all config-derived rendering. Fix: introduce `activeConfig = "
        "state.config || config` and replace all config.widget_* references "
        "with activeConfig.widget_* throughout Panel.tsx."
    ),
    origin="defect",
    component="customer_interface",
    source_spec_id="SPEC-1612",
    resolution_status="open",
    priority="P1",
    changed_by=BY,
    change_reason="Owner defect: saved widget appearance config had no effect",
    stage="created",
)
print("WI-0934 recorded")

# ---------------------------------------------------------------------------
# Test Artifacts (GOV-12)
# ---------------------------------------------------------------------------

kdb.insert_test(
    id="TEST-2928",
    title="Panel.tsx resolves activeConfig from store with prop fallback",
    spec_id="SPEC-1612",
    test_type="unit",
    expected_outcome="Panel.tsx contains `state.config || config` pattern for activeConfig resolution",
    changed_by=BY,
    change_reason="GOV-12: test for WI-0934",
    test_file="tests/widget/test_widget_config_reactivity.py",
    test_class="TestWidgetConfigReactivity",
    test_function="test_panel_uses_store_config_with_prop_fallback",
)
print("TEST-2928 recorded")

kdb.insert_test(
    id="TEST-2929",
    title="Panel.tsx uses activeConfig for resolveTokens",
    spec_id="SPEC-1612",
    test_type="unit",
    expected_outcome="Panel.tsx calls resolveTokens(activeConfig) not resolveTokens(config)",
    changed_by=BY,
    change_reason="GOV-12: test for WI-0934",
    test_file="tests/widget/test_widget_config_reactivity.py",
    test_class="TestWidgetConfigReactivity",
    test_function="test_panel_resolve_tokens_uses_active_config",
)
print("TEST-2929 recorded")

kdb.insert_test(
    id="TEST-2930",
    title="Panel.tsx has no stale config.widget_ references",
    spec_id="SPEC-1612",
    test_type="unit",
    expected_outcome="No config.widget_ references in Panel.tsx (all replaced with activeConfig.widget_)",
    changed_by=BY,
    change_reason="GOV-12: test for WI-0934",
    test_file="tests/widget/test_widget_config_reactivity.py",
    test_class="TestWidgetConfigReactivity",
    test_function="test_no_stale_config_widget_references",
)
print("TEST-2930 recorded")

kdb.insert_test(
    id="TEST-2931",
    title="Panel.tsx uses activeConfig for all derived state",
    spec_id="SPEC-1612",
    test_type="unit",
    expected_outcome="Agent name, title, avatar, gradient, branding all derive from activeConfig",
    changed_by=BY,
    change_reason="GOV-12: test for WI-0934",
    test_file="tests/widget/test_widget_config_reactivity.py",
    test_class="TestWidgetConfigReactivity",
    test_function="test_derived_state_uses_active_config",
)
print("TEST-2931 recorded")

# ---------------------------------------------------------------------------
# GOV-13: Assign tests to PLAN-001 Phase 3 (widget tests)
# ---------------------------------------------------------------------------

conn = sqlite3.connect(str(Path(__file__).resolve().parent.parent / "tools" / "knowledge-db" / "knowledge.db"))
row = conn.execute("SELECT test_ids FROM current_test_plan_phases WHERE id = 'PHASE-003'").fetchone()

if row and row[0]:
    existing_ids = json.loads(row[0])
else:
    existing_ids = []

new_test_ids = ["TEST-2928", "TEST-2929", "TEST-2930", "TEST-2931"]
updated_ids = existing_ids + [tid for tid in new_test_ids if tid not in existing_ids]

kdb.update_test_plan_phase(
    id="PHASE-003",
    changed_by=BY,
    change_reason="GOV-13: assign S131 config pipeline defect tests to Phase 3",
    test_ids=updated_ids,
)
print(f"PHASE-003 updated: {len(updated_ids)} tests (added {len(new_test_ids)})")

conn.close()
print("\nAll S131 config pipeline defect artifacts recorded successfully.")
