"""
S156 Wiki Update Script — updates 5 wiki pages with S155-S156 changes.
© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
import os

wiki = r"C:\Users\micha\AppData\Local\Temp\agent-red-wiki"

# ===== HOME.md =====
fp = os.path.join(wiki, "Home.md")
with open(fp, "r", encoding="utf-8") as f:
    c = f.read()

c = c.replace(
    "v1.74.0 (ACR ca4b, revision 0000023, 3 tenants, `agent-red-staging`)",
    "v1.76.0 (ACR ca4g, revision 0000025, 3 tenants, `agent-red-staging`)",
)
c = c.replace(
    "All 19 cycles DEPLOYED. v1.62.0 PRODUCTION. Quality hardening IN PROGRESS.",
    "All 19 cycles DEPLOYED. v1.62.0 PRODUCTION. v1.76.0 STAGING. Quality hardening IN PROGRESS.",
)
c = c.replace(
    "[[Changelog]] -- Release history from v1.0.0 through v1.74.0",
    "[[Changelog]] -- Release history from v1.0.0 through v1.76.0",
)
c = c.replace(
    "[[Testing Strategy]] -- 5,526 offline + 936 live E2E tests",
    "[[Testing Strategy]] -- 5,971 offline + 936 live E2E tests",
)
c = c.replace(
    "| Offline tests | 5,526 passed, 0 failures |",
    "| Offline tests | 5,971 passed, 1 known fail |",
)
c = c.replace(
    "| Specifications | 1,868 (1,335 implemented, 313 verified, 60 specified, 159 retired) |",
    "| Specifications | 1,869 (1,336 implemented, 313 verified, 60 specified, 159 retired) |",
)
c = c.replace("| Test artifacts | 8,761 |", "| Test artifacts | 8,795 |")
c = c.replace(
    "1,868 specs, 8,761 tests, 1,061 WIs",
    "1,869 specs, 8,795 tests, 1,064 WIs",
)
c = c.replace(
    "Staging validated at v1.74.0 with Shopify embedded admin fixes.",
    "Staging validated at v1.76.0 with CORS middleware fix, widget retry logic, and Done button UX improvement.",
)

old_m = (
    "**Recent milestones (S140-S153):**\n"
    "- SPEC-1652 Quality Cycle COMPLETE -- 520 elements inventoried, 576 standalone + 264 provider + 96 Shopify live E2E tests\n"
    "- Quality metrics at ceiling -- assertion coverage 99.7%, pass rate 100%, traceability 100%\n"
    "- Shopify embedded admin fixed (5 bugs) and validated via Chrome MCP (S143-S144)\n"
    "- S153 mega session -- 7 code defects fixed, 400 specs promoted, 148 retired, GOV-18 governance spec\n"
    "- Production readiness assessment (DOC-142) and beta onboarding checklist (DOC-143)"
)
new_m = (
    "**Recent milestones (S140-S156):**\n"
    "- **S156**: CORS middleware ordering fix (429s include CORS headers), widget HTTP retry with exponential backoff, widget CDN fix (permanent paths), issue report Done button UX fix, deployed v1.76.0 backend + widget v23\n"
    "- **S155**: Audit session -- async safety (3 fire-and-forget fixes), GitHub Actions CI, Redis rate limiting (SPEC-1626), Cloudflare proxy middleware (SPEC-1663), v1.75.0 staging deploy, mid-flight seed script\n"
    "- SPEC-1652 Quality Cycle COMPLETE -- 520 elements inventoried, 576 standalone + 264 provider + 96 Shopify live E2E tests\n"
    "- Quality metrics at ceiling -- assertion coverage 99.7%, pass rate 100%, traceability 100%\n"
    "- Production readiness assessment (DOC-142) and beta onboarding checklist (DOC-143)"
)
c = c.replace(old_m, new_m)
c = c.replace("*Last updated: 2026-03-06*", "*Last updated: 2026-03-07*")
c = c.replace("## Project Metrics (2026-03-06)", "## Project Metrics (2026-03-07)")

with open(fp, "w", encoding="utf-8") as f:
    f.write(c)
print("Home.md updated")


# ===== PROJECT-STATUS.md =====
fp = os.path.join(wiki, "Project-Status.md")
with open(fp, "r", encoding="utf-8") as f:
    c = f.read()

c = c.replace(
    "> Last updated: 2026-03-06 (S154)",
    "> Last updated: 2026-03-07 (S156)",
)
c = c.replace(
    "| **Staging** | v1.74.0 (ACR ca4b, revision 0000023, 3 tenants, scales to zero) |",
    "| **Staging** | v1.76.0 (ACR ca4g, revision 0000025, 3 tenants, scales to zero) |",
)
c = c.replace(
    "| **Offline Tests** | 5,526 passed, 0 failed (949 unit, 3,717 multi-tenant, 298 agents/chat, 272 integrations) |",
    "| **Offline Tests** | 5,971 passed, 1 known fail (967 unit, 4,423 multi-tenant, 309 agents/chat, 272 integrations) |",
)
c = c.replace(
    "| **Knowledge DB** | 1,868 specs, 8,761 test artifacts, 1,061 work items, 143 documents, 13 procedures |",
    "| **Knowledge DB** | 1,869 specs, 8,795 test artifacts, 1,064 work items, 143 documents, 13 procedures |",
)
c = c.replace(
    "| Offline tests | **5,526** passed, 0 failures |",
    "| Offline tests | **5,971** passed, 1 known fail |",
)
c = c.replace(
    "| Specifications | **1,868** (1,335 implemented, 313 verified, 60 specified, 159 retired) |",
    "| Specifications | **1,869** (1,336 implemented, 313 verified, 60 specified, 159 retired) |",
)
c = c.replace(
    "| Work items | **1,061** (16 open, 950 resolved, 35 verified, 56 wont_fix) |",
    "| Work items | **1,064** (16 open, 953 resolved, 35 verified, 56 wont_fix) |",
)
c = c.replace(
    "| Test artifacts (KB) | **8,761** |",
    "| Test artifacts (KB) | **8,795** |",
)
c = c.replace(
    "| Staging Environment | v1.74.0, 3 tenants (staging-001, staging-002, remaker-digital-001), scales to zero |",
    "| Staging Environment | v1.76.0, 3 tenants (staging-001, staging-002, remaker-digital-001), scales to zero |",
)

old_s = "| **S153** | Mega session -- 7 code defects fixed, 400 specs promoted, 148 retired, GOV-18, 84 new tests |"
new_s = (
    "| **S156** | CORS middleware fix, widget retry logic, CDN fix, Done button UX, v1.76.0 staging + widget v23 |\n"
    "| **S155** | Audit -- async safety, GitHub CI, Redis rate limiting, Cloudflare proxy, v1.75.0 staging, mid-flight seed |\n"
    "| **S154** | Documentation + GitHub hygiene -- wiki sync, repo topics, stale issue cleanup |\n"
    "| **S153** | Mega session -- 7 code defects fixed, 400 specs promoted, 148 retired, GOV-18, 84 new tests |"
)
c = c.replace(old_s, new_s)
c = c.replace("*Last updated: 2026-03-06*", "*Last updated: 2026-03-07*")

with open(fp, "w", encoding="utf-8") as f:
    f.write(c)
print("Project-Status.md updated")


# ===== CHANGELOG.md =====
fp = os.path.join(wiki, "Changelog.md")
with open(fp, "r", encoding="utf-8") as f:
    c = f.read()

v176 = """## v1.76.0 STAGING (2026-03-07, Sessions 155-156) -- CORS FIX + WIDGET RESILIENCE + UX

**ACR Image:** ca4g, revision 0000025. Staging only. Widget v23 on Shopify CDN.

### CORS Middleware Ordering Fix (S156)
- **WI-1062** -- CORSMiddleware was innermost middleware; RateLimitMiddleware rejected with 429 before CORS headers added, causing browser to block response
- **Fix:** Moved CORSMiddleware from factory.py to lifecycle.py as outermost middleware (LAST `add_middleware()` call)
- **SPEC-1664:** CORSMiddleware MUST be outermost ASGI middleware -- ensures CORS headers on ALL responses (429, 401, etc.)

### Widget HTTP Retry with Exponential Backoff (S156)
- **SPEC-1665:** Widget HTTP transport retries transient errors (429, 502, 503, 504) with exponential backoff
- Config fetch: 3 retries, 1.5s base delay. Conversation start: 2 retries, 1s base delay
- Respects `Retry-After` header (max 30s cap)

### Widget CDN Fix (S156)
- **WI-1063** -- `shopify app dev` creates temporary `/Staging/` CDN paths that expire when dev server stops
- **Fix:** Use `shopify app deploy --force` for permanent versioned paths (e.g., `agent-red-customer-experience-23`)

### Issue Report Done Button (S156)
- **WI-1064** -- Post-submission confirmation showed "Cancel" button implying action can be undone
- **Fix:** Added `issueDone` locale key across all 8 languages, updated IssueReport.tsx success state
- **SPEC-1666:** Success confirmation uses `locale.issueDone` (Done), not `locale.issueCancel` (Cancel)

### Infrastructure (S155)
- **Async safety:** Fixed 3 fire-and-forget `asyncio.create_task()` calls -- stored in `_background_tasks` set. Added `asyncio.Lock` to `_get_http_client()`. Fixed 4 bare `except` handlers
- **GitHub Actions CI:** Added `unit` shard + `lint.yml` + ruff config
- **Redis rate limiting (SPEC-1626):** `RedisRateLimitBackend` with sorted sets, auto-configure from `REDIS_URL`, fallback to in-memory. 18 tests
- **Cloudflare proxy middleware (SPEC-1663):** `TrustedProxyMiddleware` extracts real IP from `CF-Connecting-IP`/`X-Forwarded-For`, rewrites `scope["client"]`. 34 tests

### Metrics
- 5,971 offline tests, 1 known fail (SPEC-1620 manual test elimination)
- 1,869 specs (1,336 implemented, 313 verified, 60 specified, 159 retired)
- 8,795 test artifacts in KB
- All quality gates at ceiling
- Widget bundle: 102.96 KB

---

"""
marker = "## v1.74.0 STAGING"
c = c.replace(marker, v176 + marker)

with open(fp, "w", encoding="utf-8") as f:
    f.write(c)
print("Changelog.md updated")


# ===== TEST-COVERAGE.md =====
fp = os.path.join(wiki, "Test-Coverage.md")
with open(fp, "r", encoding="utf-8") as f:
    c = f.read()

c = c.replace(
    "> Last updated: 2026-03-06 (S154)",
    "> Last updated: 2026-03-07 (S156)",
)
c = c.replace(
    "| **Offline Tests** | 5,526 (949 unit, 3,717 multi-tenant, 298 agents/chat, 272 integrations) |",
    "| **Offline Tests** | 5,971 (967 unit, 4,423 multi-tenant, 309 agents/chat, 272 integrations) |",
)
c = c.replace(
    "| **KB Test Artifacts** | 8,761 |",
    "| **KB Test Artifacts** | 8,795 |",
)
c = c.replace(
    "| **Failures** | 0 |",
    '| **Failures** | 1 known fail (SPEC-1620) |',
)
c = c.replace("### Unit Tests (949 tests)", "### Unit Tests (967 tests)")
c = c.replace("### Multi-Tenant Tests (3,717 tests)", "### Multi-Tenant Tests (4,423 tests)")
c = c.replace("### Agent and Chat Tests (298 tests)", "### Agent and Chat Tests (309 tests)")
c = c.replace(
    "| Assertion Coverage | 99.7% (1,862/1,868 specs) | >= 60% | PASS |",
    "| Assertion Coverage | 99.7% (1,862/1,869 specs) | >= 60% | PASS |",
)
c = c.replace(
    "| Test Traceability | 100% (8,761/8,761 traced) | >= 80% | PASS |",
    "| Test Traceability | 100% (8,795/8,795 traced) | >= 80% | PASS |",
)
c = c.replace(
    "python scripts/test_pipeline.py --env staging --version 1.74.0",
    "python scripts/test_pipeline.py --env staging --version 1.76.0",
)
c = c.replace("*Last updated: 2026-03-06*", "*Last updated: 2026-03-07*")

with open(fp, "w", encoding="utf-8") as f:
    f.write(c)
print("Test-Coverage.md updated")


# ===== CHAT-WIDGET-SPECIFICATION.md =====
fp = os.path.join(wiki, "Chat-Widget-Specification.md")
with open(fp, "r", encoding="utf-8") as f:
    c = f.read()

c = c.replace("34 strings, i18n-ready", "35 strings, i18n-ready")

# Add IssueReport to component tree
old_tree = (
    '    PANEL --> RATING["ChatRating.tsx<br/>Thumbs up/down<br/>Optional comment<br/>Thank-you state"]\n'
    "\n"
    '    PANEL --> OFFLINE["OfflineForm.tsx'
)
new_tree = (
    '    PANEL --> RATING["ChatRating.tsx<br/>Thumbs up/down<br/>Optional comment<br/>Thank-you state"]\n'
    "\n"
    '    PANEL --> ISSUE["IssueReport.tsx<br/>Issue type selector<br/>Details textarea<br/>Submit + Done states"]\n'
    "\n"
    '    PANEL --> OFFLINE["OfflineForm.tsx'
)
c = c.replace(old_tree, new_tree)

# Add style
c = c.replace(
    "    style INPUT fill:#2A2A2A,stroke:#3A3A3A,color:#F0F0F0",
    "    style INPUT fill:#2A2A2A,stroke:#3A3A3A,color:#F0F0F0\n    style ISSUE fill:#2A2A2A,stroke:#3A3A3A,color:#F0F0F0",
)

# Add resilience section
old_design = "---\n\n## Design Token System"
new_design = (
    "---\n\n"
    "## HTTP Transport Resilience\n\n"
    "The widget implements automatic retry logic for transient HTTP errors (SPEC-1665).\n\n"
    "### Retry Configuration\n\n"
    "| Operation | Max Retries | Base Delay | Backoff |\n"
    "|-----------|-------------|------------|----------|\n"
    "| Config fetch | 3 | 1.5s | Exponential |\n"
    "| Conversation start | 2 | 1.0s | Exponential |\n\n"
    "### Retryable Status Codes\n\n"
    "| Code | Description |\n"
    "|------|-------------|\n"
    "| 429 | Too Many Requests (rate limited) |\n"
    "| 502 | Bad Gateway |\n"
    "| 503 | Service Unavailable |\n"
    "| 504 | Gateway Timeout |\n\n"
    "The retry logic respects the `Retry-After` header when present, with a 30-second maximum cap. "
    "Non-retryable errors (4xx except 429) fail immediately.\n\n"
    "---\n\n## Design Token System"
)
c = c.replace(old_design, new_design)

with open(fp, "w", encoding="utf-8") as f:
    f.write(c)
print("Chat-Widget-Specification.md updated")
