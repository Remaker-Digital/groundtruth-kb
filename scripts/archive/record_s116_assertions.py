#!/usr/bin/env python3
"""Record S116 specification assertions in the Knowledge Database.

Updates SPEC-1500..1503 and GOV-09 with machine-verifiable assertions
that ensure the live E2E test specifications are retained.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools" / "knowledge-db"))

from db import KnowledgeDB

kdb = KnowledgeDB()


# ── SPEC-1500: Real API integration ──
kdb.insert_spec(
    id="SPEC-1500",
    title="Live E2E tests must use real API integration (not mocked responses)",
    status="implemented",
    changed_by="Claude (S116)",
    change_reason="Add assertions to verify spec retention",
    description=(
        "The live end-to-end test suite (tests/e2e_live/) must connect to the production API "
        "gateway through the Vite dev server proxy. Tests must NOT use mocked API responses; "
        "all data displayed in the admin SPA must come from real Cosmos DB queries via the "
        "production backend. The Vite proxy forwards /api/* to the production FQDN. "
        "Safety guards block dangerous mutations (activate, delete, rotate) but allow all reads."
    ),
    priority="P1",
    scope="testing",
    section="TESTING",
    tags="live-e2e,api-integration,testing",
    type="requirement",
    assertions=[
        {
            "type": "glob",
            "pattern": "tests/e2e_live/conftest.py",
            "description": "Live E2E conftest.py exists (test infrastructure for real API integration)",
        },
        {
            "type": "grep",
            "pattern": "VITE_API_URL|production_reachable|live_api_key",
            "file": "tests/e2e_live/conftest.py",
            "description": "conftest.py connects to production API (VITE_API_URL or production reachability check)",
            "min_count": 1,
        },
        {
            "type": "grep_absent",
            "pattern": "AdminApiMocker|mock_api|MOCK_CONFIG.*=.*{",
            "file": "tests/e2e_live/conftest.py",
            "description": "Live E2E conftest does NOT use mocked API responses (no AdminApiMocker)",
        },
    ],
)
print("SPEC-1500 updated with 3 assertions")


# ── SPEC-1501: Real data ──
kdb.insert_spec(
    id="SPEC-1501",
    title="Live E2E tests must validate real production data (not fixtures or mocks)",
    status="implemented",
    changed_by="Claude (S116)",
    change_reason="Add assertions to verify spec retention",
    description=(
        "All assertions in the live E2E test suite must validate against real data from the "
        "production tenant (remaker-digital-001). Tests verify that form fields are populated "
        "with actual values (brand name, widget key, team members, conversation history), "
        "stat cards display real metrics, and configuration sections show live config data. "
        "Tests must NOT rely on hardcoded expected values; they assert structural properties "
        "(non-empty, valid format, expected element count) against whatever the production API returns."
    ),
    priority="P1",
    scope="testing",
    section="TESTING",
    tags="live-e2e,real-data,testing",
    type="requirement",
    assertions=[
        {
            "type": "glob",
            "pattern": "tests/e2e_live/test_dashboard_live.py",
            "description": "Dashboard live test file exists (validates real stat card data)",
        },
        {
            "type": "glob",
            "pattern": "tests/e2e_live/test_team_live.py",
            "description": "Team live test file exists (validates real team member data)",
        },
        {
            "type": "grep",
            "pattern": "pk_live_|widget.key|real.key",
            "file": "tests/e2e_live/test_widget_live.py",
            "description": "Widget tests check for real widget key prefix (pk_live_)",
            "min_count": 1,
        },
    ],
)
print("SPEC-1501 updated with 3 assertions")


# ── SPEC-1502: Visual + responsive ──
kdb.insert_spec(
    id="SPEC-1502",
    title="Live E2E tests must verify visual CSS properties and responsive layout at 3 viewport sizes",
    status="implemented",
    changed_by="Claude (S116)",
    change_reason="Add assertions to verify spec retention",
    description=(
        "The live E2E test suite must include visual CSS tests (test_visual_live.py) that use "
        "page.evaluate() + getComputedStyle() to verify computed CSS properties: sidebar width, "
        "background colors, font sizes, border-radius, padding, brand color usage, and monospace "
        "fonts. Responsive layout tests (test_responsive_live.py) must validate at 3 viewport sizes: "
        "desktop (1440x900), tablet (768x1024), and mobile (375x812). Tests verify sidebar collapse, "
        "content reflow, stat card stacking, burger menu functionality, and form width adaptation."
    ),
    priority="P1",
    scope="testing",
    section="TESTING",
    tags="live-e2e,visual,responsive,css,testing",
    type="requirement",
    assertions=[
        {
            "type": "glob",
            "pattern": "tests/e2e_live/test_visual_live.py",
            "description": "Visual CSS live test file exists",
        },
        {
            "type": "glob",
            "pattern": "tests/e2e_live/test_responsive_live.py",
            "description": "Responsive layout live test file exists",
        },
        {
            "type": "grep",
            "pattern": "getComputedStyle|computed.style|background.color|border.radius",
            "file": "tests/e2e_live/test_visual_live.py",
            "description": "Visual tests use getComputedStyle to verify CSS properties",
            "min_count": 3,
        },
        {
            "type": "grep",
            "pattern": "set_viewport_size.*1440|set_viewport_size.*768|set_viewport_size.*375",
            "file": "tests/e2e_live/test_responsive_live.py",
            "description": "Responsive tests cover all 3 viewport sizes (1440, 768, 375)",
            "min_count": 3,
        },
    ],
)
print("SPEC-1502 updated with 4 assertions")


# ── SPEC-1503: End-to-end flows ──
kdb.insert_spec(
    id="SPEC-1503",
    title="Live E2E tests must exercise end-to-end user flows against the live backend",
    status="implemented",
    changed_by="Claude (S116)",
    change_reason="Add assertions to verify spec retention",
    description=(
        "The live E2E test suite must include end-to-end flow tests that exercise multi-step user "
        "interactions against the production backend: navigation between all admin pages, "
        "draft config save round-trip (edit field, save, reload, verify persistence, cleanup), "
        "inbox conversation click-through, search filtering, and widget configuration inspection. "
        "The save round-trip test (test_configuration_live.py::TestDraftSaveRoundTrip) modifies a "
        "draft field, saves via PUT /api/config?state=draft, reloads, and verifies the change "
        "persisted, then restores the original value as cleanup."
    ),
    priority="P1",
    scope="testing",
    section="TESTING",
    tags="live-e2e,end-to-end,flows,testing",
    type="requirement",
    assertions=[
        {
            "type": "glob",
            "pattern": "tests/e2e_live/test_navigation_live.py",
            "description": "Navigation live test file exists (page loading flows)",
        },
        {
            "type": "glob",
            "pattern": "tests/e2e_live/test_configuration_live.py",
            "description": "Configuration live test file exists (draft save round-trip)",
        },
        {
            "type": "grep",
            "pattern": "TestDraftSaveRoundTrip|test_edit_draft_and_save",
            "file": "tests/e2e_live/test_configuration_live.py",
            "description": "Configuration tests include draft save round-trip flow",
            "min_count": 1,
        },
        {
            "type": "glob",
            "pattern": "tests/e2e_live/test_inbox_live.py",
            "description": "Inbox live test file exists (conversation interaction flows)",
        },
    ],
)
print("SPEC-1503 updated with 4 assertions")


# ── GOV-09: Owner Input Classification Rule ──
kdb.insert_spec(
    id="GOV-09",
    title="Owner Input Classification Rule: detect specification language before implementation",
    status="implemented",
    changed_by="Claude (S116)",
    change_reason="Add assertions to verify spec retention and mechanical enforcement",
    description=(
        "When the owner describes what the system must do, should do, must include, or states "
        "numbered criteria, Claude must classify the input as specification language. Before writing "
        "any code: (1) record or verify specifications in KB, (2) identify work items for any gaps, "
        "(3) add work items to the backlog, (4) present the backlog for prioritization. Only proceed "
        "to implementation after explicit prioritization approval. A UserPromptSubmit hook "
        "(.claude/hooks/spec-classifier.py) mechanically enforces this, but Claude must also "
        "self-enforce when the hook does not trigger."
    ),
    priority="P0",
    scope="governance",
    section="GOVERNANCE",
    tags="governance,specification-discipline,classification,hook",
    type="governance",
    assertions=[
        {
            "type": "glob",
            "pattern": ".claude/hooks/spec-classifier.py",
            "description": "Specification classifier hook exists",
        },
        {
            "type": "grep",
            "pattern": "GOV-09|Owner Input Classification",
            "file": "CLAUDE.md",
            "description": "GOV-09 Owner Input Classification Rule is documented in CLAUDE.md",
            "min_count": 1,
        },
        {
            "type": "grep",
            "pattern": "spec-classifier",
            "file": ".claude/settings.local.json",
            "description": "spec-classifier hook is registered in settings.local.json",
            "min_count": 1,
        },
    ],
)
print("GOV-09 updated with 3 assertions")


print()
print("All 5 specs updated with assertions (17 total assertions).")
