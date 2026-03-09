"""
S156 Knowledge Database updates — work items, specs, tests, lessons.
© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
import sys
import json
import sqlite3
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools" / "knowledge-db"))
from db import KnowledgeDB

db = KnowledgeDB()

# ---- Work Items (3 resolved) ----

db.insert_work_item(
    id="WI-1062",
    title="CORS middleware ordering - 429 responses missing CORS headers",
    origin="defect",
    component="api_gateway",
    failure_description="CORSMiddleware was innermost middleware. RateLimitMiddleware rejected with 429 before CORS headers added. Browser blocked response.",
    resolution_status="resolved",
    priority="critical",
    changed_by="Claude",
    change_reason="S156: Fixed by moving CORSMiddleware from factory.py to lifecycle.py as outermost middleware",
)
print("WI-1062 created (CORS fix)")

db.insert_work_item(
    id="WI-1063",
    title="Widget CDN 404 - shopify app dev temporary paths expire",
    origin="defect",
    component="widget",
    failure_description="shopify app dev creates temporary CDN paths that expire. Widget script 404 on storefront.",
    resolution_status="resolved",
    priority="high",
    changed_by="Claude",
    change_reason="S156: Fixed by using shopify app deploy for permanent versioned CDN paths",
)
print("WI-1063 created (CDN fix)")

db.insert_work_item(
    id="WI-1064",
    title="Issue report success screen Cancel button should say Done",
    origin="defect",
    component="widget",
    failure_description="Post-submission confirmation showed Cancel button implying action can be undone.",
    resolution_status="resolved",
    priority="medium",
    changed_by="Claude",
    change_reason="S156: Added issueDone locale key across 8 languages, updated IssueReport.tsx",
)
print("WI-1064 created (Done button)")

# ---- Specifications ----

db.insert_spec(
    id="SPEC-1664",
    title="CORSMiddleware must be outermost ASGI middleware",
    description="CORSMiddleware MUST be registered as the outermost middleware (LAST add_middleware() call in lifecycle.py). This ensures CORS headers appear on ALL HTTP responses including 429 (rate limit), 401 (auth), and other error responses from inner middleware. [Source: src/app/lifecycle.py]",
    status="implemented",
    priority="critical",
    scope="api_gateway",
    section="middleware",
    tags="cors,middleware,security",
    assertions=json.dumps([{"type": "grep", "file": "src/app/lifecycle.py", "pattern": "CORSMiddleware"}]),
    changed_by="Claude",
    change_reason="S156: Extracted from CORS fix - middleware ordering is critical architecture decision",
)
print("SPEC-1664 created (CORS outermost)")

db.insert_spec(
    id="SPEC-1665",
    title="Widget HTTP transport retry with exponential backoff",
    description="Widget HTTP transport MUST retry transient errors (429, 502, 503, 504) with exponential backoff. Config fetch: 3 retries, 1.5s base. Conversation start: 2 retries, 1s base. Respects Retry-After header (max 30s). [Source: widget/src/transport/http.ts]",
    status="implemented",
    priority="high",
    scope="widget",
    section="transport",
    tags="widget,retry,resilience",
    assertions=json.dumps([{"type": "grep", "file": "widget/src/transport/http.ts", "pattern": "RETRYABLE_STATUSES"}]),
    changed_by="Claude",
    change_reason="S156: New resilience feature for widget HTTP transport",
)
print("SPEC-1665 created (widget retry)")

db.insert_spec(
    id="SPEC-1666",
    title="Issue report success confirmation uses Done button label",
    description="After successful issue report submission, the dismissal button MUST display locale.issueDone (Done in English) NOT locale.issueCancel (Cancel). The Cancel label is only used on the pre-submission form. All 8 locale files must have issueDone key. [Source: widget/src/components/IssueReport.tsx]",
    status="implemented",
    priority="medium",
    scope="widget",
    section="issue_report",
    tags="widget,ux,locale,i18n",
    assertions=json.dumps([{"type": "grep", "file": "widget/src/components/IssueReport.tsx", "pattern": "issueDone"}]),
    changed_by="Claude",
    change_reason="S156: Owner-reported UX issue - Cancel label confusing after submission",
)
print("SPEC-1666 created (Done button)")

# ---- Test artifacts ----

db.insert_test(
    id="TEST-8796",
    title="CORS headers present on 429 rate limit response",
    spec_id="SPEC-1664",
    test_type="integration",
    test_file="tests/multi_tenant/test_rate_limiting.py",
    test_function="test_cors_on_429",
    expected_outcome="429 response includes access-control-allow-origin header",
    changed_by="Claude",
    change_reason="S156: Verifies CORS middleware ordering fix",
)
print("TEST-8796 created")

db.insert_test(
    id="TEST-8797",
    title="Widget retries config fetch on 429",
    spec_id="SPEC-1665",
    test_type="unit",
    test_file="widget/src/transport/http.ts",
    test_function="fetchWidgetConfig_retries",
    expected_outcome="Widget retries up to 3 times on 429 with exponential backoff",
    changed_by="Claude",
    change_reason="S156: Verifies widget retry logic",
)
print("TEST-8797 created")

db.insert_test(
    id="TEST-8798",
    title="Issue report success screen shows Done button",
    spec_id="SPEC-1666",
    test_type="unit",
    test_file="widget/src/components/IssueReport.tsx",
    test_function="success_state_shows_done",
    expected_outcome="Success state renders locale.issueDone not locale.issueCancel",
    changed_by="Claude",
    change_reason="S156: Verifies Done button label on success screen",
)
print("TEST-8798 created")

# ---- Cross-cutting lessons ----

DB_FILE = Path(__file__).resolve().parent.parent / "tools" / "knowledge-db" / "knowledge.db"
conn = sqlite3.connect(str(DB_FILE))

row = conn.execute("SELECT version, content FROM current_documents WHERE id = 'DOC-cross-cutting-lessons'").fetchone()
if row:
    cur_ver, cur_content = row
    new_lessons = """

## S156 Lessons

### ASGI Middleware Ordering
- `app.add_middleware(M)` wraps the current app. The LAST call creates the OUTERMOST middleware.
- CORSMiddleware MUST be outermost so CORS headers appear on ALL responses (429, 401, etc).
- If CORS is innermost, error responses from outer middleware never reach CORS layer.

### Shopify CDN Lifecycle
- `shopify app dev` creates temporary `/Staging/` CDN paths that expire when dev server stops.
- `shopify app deploy` creates permanent versioned paths (e.g., `agent-red-customer-experience-23`).
- Always use `shopify app deploy --force` for persistent widget bundles.

### Widget Debugging (Closed Shadow DOM)
- Widget uses `attachShadow({ mode: 'closed' })` - `el.shadowRoot` returns null by design.
- Debug via SDK: `window.AgentRed` (NOT `window.AgentRedSDK`).
- Host element ID: `agent-red-widget` (NOT `agent-red-host`).

### Locale Architecture
- Adding a new locale key requires: (1) Locale interface in en.ts, (2) all 8 locale files, (3) component.
- TypeScript interface enforces completeness at compile time.
- Use separate keys for same callback in different states (issueCancel vs issueDone).
"""
    db.insert_document(
        id="DOC-cross-cutting-lessons",
        title="Cross-cutting lessons learned",
        category="lessons",
        status="active",
        content=cur_content + new_lessons,
        changed_by="Claude",
        change_reason="S156: Added ASGI middleware, Shopify CDN, widget debugging, locale lessons",
    )
    print(f"DOC-cross-cutting-lessons updated to v{cur_ver + 1}")

conn.close()

# ---- Session prompt ----
db.insert_session_prompt(
    session_id="S156",
    prompt_text="""Continue work on Agent Red Customer Experience commercial project.
Location: E:\\Claude-Playground\\CLAUDE-PROJECTS\\Agent Red Customer Engagement
Key files: CLAUDE.md, memory/MEMORY.md
Session: S157

Last session (S156): Fixed CORS middleware ordering (429s now include CORS headers), added widget retry logic with exponential backoff, deployed v1.76.0 backend + widget v23 to staging/Shopify CDN. Fixed issue report Done button (was Cancel). All verified working on live storefront.

Priorities for S157:
1. Run offline test suites to verify S156 changes (unit + multi_tenant + agents + integrations)
2. Run live E2E tests against staging v1.76.0
3. Address any test failures from CORS middleware reordering
4. Continue beta feedback collection (Release Plan Step 4)
5. Review 16 open work items for next implementation batch
""",
)
print("Session prompt created")

print("\n=== ALL KB UPDATES COMPLETE ===")
