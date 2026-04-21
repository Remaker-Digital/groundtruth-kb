"""One-shot script: insert S136 handoff prompt into Knowledge DB."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools', 'knowledge-db'))
from db import KnowledgeDB

db_path = os.path.join(os.path.dirname(__file__), '..', 'groundtruth.db')
db = KnowledgeDB(db_path)

prompt = r"""Continue work on Agent Red Customer Experience commercial project.
Location: E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement
Key files: CLAUDE.md, memory/MEMORY.md
Session: S136 (increment from S135)

## Context
S135 completed two tracks:
1. **SPEC-1652/1653 element inventory + live E2E tests** for Dashboard (129 elements, 61 tests), Navbar (16 elements, 41 tests), Sidebar (26 elements, 66 tests) = 168 new tests, 0 product defects.
2. **SPEC-1654 tenant param persistence** -- useQueryPreservingNavigate hook + NavigateWithQuery component. Standalone dist rebuilt. NOT YET DEPLOYED to staging.

## Task: Continue SPEC-1652 element inventory -- Inbox page
Resume the closed-loop quality cycle on the **Inbox page**:
1. **Inventory testable elements** -- Use Playwright against staging to record all Inbox page elements into KB testable_elements table (pattern: record_inbox_elements.py).
2. **Write comprehensive live E2E tests** -- Create tests/e2e_live/test_inbox_live.py covering all inventoried elements across SPEC-1653 dimensions (A: Presence/Visibility, B: Text Content, C: Layout, D: Navigation, E: Data Loading, etc.).
3. **Run tests** -- Execute against staging and record results.

## Pre-existing Inbox test file
tests/e2e_live/test_inbox_live.py already exists from S116 (5 basic tests). The new tests should significantly expand it following the SPEC-1652 pattern established for Dashboard/Navbar/Sidebar.

## Test environment
SUPERADMIN_PREVIEW_API_KEY=(set from environment, SPEC-1845)
PROD_URL=https://agent-red-staging.orangeglacier-f566a4e7.eastus.azurecontainerapps.io
LIVE_TENANT_ID=staging-001

## Staging deployment note
SPEC-1654 standalone dist was rebuilt locally but NOT deployed to staging. The current staging (v1.66.0, revision 0000015) does NOT have the tenant param fix. This does not block Inbox testing (tests use direct API + Playwright navigation, not bookmarks). Consider deploying if time permits.

## Pattern reference
- Element recording scripts: scripts/record_dashboard_elements.py, record_navbar_elements.py, record_sidebar_elements.py
- Test files: tests/e2e_live/test_dashboard_live.py (61 tests), test_navbar_live.py (41), test_sidebar_live.py (66)
- KB table: testable_elements (columns: id, subsystem, element_name, dimensions JSON, locator_strategy, version, created_at)
- SPEC-1653 dimensions: A-N (14 categories, 68 dimensions)
"""

context = {
    "continuing": "SPEC-1652 quality cycle",
    "completed_subsystems": ["Dashboard", "Navbar", "Sidebar"],
    "next_subsystem": "Inbox",
    "remaining_subsystems": ["Configuration", "Widget", "Knowledge Base", "Quick Actions", "Billing", "Team", "Integrations", "Memory/Privacy"],
    "pending_deployment": "SPEC-1654 standalone dist rebuilt, not yet deployed to staging",
}

result = db.insert_session_prompt(
    session_id="S136",
    prompt_text=prompt,
    context=context,
)
print(f"Session prompt inserted: session_id={result['session_id']}, version={result['version']}")
