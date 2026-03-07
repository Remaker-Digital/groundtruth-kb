"""
S156 Wiki Update Script Part 2 — Defect-Log.md and Testing-Strategy.md.
© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
import os

wiki = r"C:\Users\micha\AppData\Local\Temp\agent-red-wiki"

# ===== DEFECT-LOG.md =====
fp = os.path.join(wiki, "Defect-Log.md")
with open(fp, "r", encoding="utf-8") as f:
    c = f.read()

c = c.replace(
    "| Total defects logged | 75 (D1-D68 + WI-1055..WI-1061) |",
    "| Total defects logged | 78 (D1-D68 + WI-1055..WI-1064) |",
)
c = c.replace("| Fixed | 74 |", "| Fixed | 77 |")

# Add S156 fixes before S153 section
old_s153 = "## Session 153 Fixes"
new_s156 = """## Session 156 Fixes (v1.76.0 staging)

3 defects identified and fixed:

| WI | Component | Fix |
|----|-----------|-----|
| WI-1062 | api_gateway | CORS middleware ordering -- moved CORSMiddleware to outermost position so 429 responses include CORS headers |
| WI-1063 | widget | CDN 404 -- switched from `shopify app dev` (temporary paths) to `shopify app deploy` (permanent versioned paths) |
| WI-1064 | widget | Issue report success screen Cancel button renamed to Done -- added `issueDone` locale key across 8 languages |

## Session 155 Fixes (v1.75.0 staging)

Async safety and code quality fixes:

| Fix | Component | Details |
|-----|-----------|---------|
| Fire-and-forget tasks | orchestrator.py | 3 `asyncio.create_task()` calls stored in `_background_tasks` set |
| HTTP client lock | middleware.py | Added `asyncio.Lock` to `_get_http_client()` |
| Bare except handlers | multiple | 4 bare `except` replaced with specific exception types |

"""
c = c.replace(old_s153, new_s156 + old_s153)
c = c.replace("*Last updated: 2026-03-06*", "*Last updated: 2026-03-07*")

with open(fp, "w", encoding="utf-8") as f:
    f.write(c)
print("Defect-Log.md updated")

# ===== TESTING-STRATEGY.md =====
fp = os.path.join(wiki, "Testing-Strategy.md")
with open(fp, "r", encoding="utf-8") as f:
    c = f.read()

c = c.replace(
    "> Last updated: 2026-03-06 (S154)",
    "> Last updated: 2026-03-07 (S156)",
)
c = c.replace(
    "| **Offline tests** | 5,526 (949 unit, 3,717 multi-tenant, 298 agents/chat, 272 integrations) |",
    "| **Offline tests** | 5,971 (967 unit, 4,423 multi-tenant, 309 agents/chat, 272 integrations) |",
)
c = c.replace(
    "| **Test failures** | 0 |",
    "| **Test failures** | 1 known fail (SPEC-1620) |",
)
c = c.replace(
    "| **KB test artifacts** | 8,761 |",
    "| **KB test artifacts** | 8,795 |",
)
c = c.replace(
    "| **Assertion coverage** | 99.7% (1,862/1,868 specs) |",
    "| **Assertion coverage** | 99.7% (1,862/1,869 specs) |",
)
c = c.replace(
    "| **Test traceability** | 100% (8,761/8,761) |",
    "| **Test traceability** | 100% (8,795/8,795) |",
)
c = c.replace(
    "python scripts/test_pipeline.py --env staging --version 1.74.0",
    "python scripts/test_pipeline.py --env staging --version 1.76.0",
)

# Update unit test count
c = c.replace("### Unit Tests (949)", "### Unit Tests (967)")
# Update multi-tenant count
c = c.replace("### Multi-Tenant Tests (3,717)", "### Multi-Tenant Tests (4,423)")
# Update agent count
c = c.replace("### Agent and Chat Tests (298)", "### Agent and Chat Tests (309)")

c = c.replace("*Last updated: 2026-03-06*", "*Last updated: 2026-03-07*")

with open(fp, "w", encoding="utf-8") as f:
    f.write(c)
print("Testing-Strategy.md updated")
