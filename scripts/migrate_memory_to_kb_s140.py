#!/usr/bin/env python3
"""
S140 Migration: Move project knowledge from MEMORY.md to Knowledge Database.

Inserts:
  - DOC-cross-cutting-lessons: 48 development lessons organized by category
  - DOC-owner-preferences: 6 owner behavioral directives

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools" / "knowledge-db"))

import db

LESSONS_CONTENT = r"""# Cross-Cutting Development Lessons

Verified patterns and gotchas discovered across 140+ sessions of development. These are hard-won lessons that prevent recurring mistakes.

## Python / Backend

- **Lazy import patching:** `patch("source_module.symbol")`, NOT `patch("consumer_module.symbol")`
- **TenantScopedRepository.read():** requires TWO args (partition_key, document_id)
- **Cascading async:** grep ALL callers when making functions async — unawaited coroutines → 502
- **Python method name shadowing (S114):** When a class defines two methods with the same name, the second silently replaces the first. No error raised. Always use unique helper names per table (e.g., `_next_test_proc_version` vs `_next_test_version`).
- **Windows cp1252 in scripts:** Always add `sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")` to Python scripts that print API responses or Unicode characters. Without this, special chars crash on Windows.
- **Subprocess output parsing:** Never use `"FAIL" not in output` — the string "0 FAIL" contains "FAIL". Use regex `r"(\d+)\s+FAIL"` and check count == 0. Similarly for pytest: `r"(\d+)\s+passed"`.
- **CORS middleware ordering in FastAPI (S120):** In Starlette, `add_middleware()` builds an onion — LAST added = OUTERMOST. If auth middleware is added after CORS middleware, auth is outer and its error responses bypass CORS entirely.
- **Windows .cmd wrappers in subprocess (S131):** `az`, `node`, `npm` are .cmd batch wrappers on Windows. `subprocess.run(["az", ...], shell=False)` raises FileNotFoundError. Fix: use `shell=True` on Windows with `subprocess.list2cmdline(cmd)`.

## API Conventions

- **API response convention (camelCase):** All API responses use camelCase field names. Verification scripts must match.
- **Superadmin auth (S92 correction):** `SUPERADMIN_PREVIEW_API_KEY` env var is NOT referenced in `src/` code. Superadmin endpoints authenticate via Cosmos DB `team_members` lookup using the tenant admin key with superadmin role.
- **Widget auth endpoint topology (S134):** Widget runtime uses `/api/config` with `X-Widget-Key` header. Admin tools use `/api/tenants/lookup` with `X-API-Key` header. These are distinct endpoints.
- **Widget keys are secret credentials (S132):** Widget keys (`pk_live_*`) are stored in Cosmos but NOT exposed through any API response. Obtain from `seed_tenant.py` stdout or Cosmos directly.
- **Tenant URL param is an authorization gate (S139, SPEC-1657):** `?tenant=xx` determines which tenancy the user is accessing. API key authenticates identity only. Each key is globally unique. Implementation gap (WI-1045): Backend derives tenant from API key, never reads `?tenant=`.
- **Uniform 500 rpm rate limits (S137):** All tiers share the same 500 rpm rate limit.

## Cosmos DB

- **Cosmos DB database separation (S132):** Staging uses `COSMOS_DB_DATABASE=agentred-staging`, production uses `agentred` — same Cosmos account, different databases. Any subprocess targeting staging MUST pass `COSMOS_DB_DATABASE` env var explicitly.
- **Cosmos persisted values override code defaults (S139):** Per-tenant `rate_limit_rpm` from Cosmos takes precedence over `TIER_DEFAULTS`. Changing code defaults does NOT affect existing tenants with persisted values. Fix: patch Cosmos docs to `null` or re-seed.

## Build / Deploy

- **Admin dist build:** `npm run build` all 3 dists before ACR build
- **ACR Windows:** `az acr build --no-logs` to avoid charmap crash
- **Upgrade verification multi-a/multi-c ordering (S131):** `multi-a` MUST run BEFORE deployment, not after.
- **Pipeline env-aware config tests (S132):** The pipeline MUST explicitly set `PROD_URL`, `SUPERADMIN_PREVIEW_API_KEY`, and `PREVIEW_WIDGET_KEY` from `ENVIRONMENTS[args.env]`.
- **Pipeline multi-tenant test credentials (S134):** The pipeline passes `TENANT_B_API_KEY` and `TENANT_B_WIDGET_KEY` env vars from the first non-primary tenant in `TENANTS` dict.

## Testing

- **Thermal-safe testing:** `run-tests-thermal-safe.ps1 -Workers 4 -CoolDown 30`
- **Test drift:** Count/set assertions must update when adding fields/enums
- **xdist parallel safety:** `tests/integration/` CANNOT run under xdist (TestClient race)
- **Provider Console null-safety:** `Object.entries(field ?? {})` on all API response fields
- **KB test_coverage.spec_id references specifications.id (NOT handle)**
- **Widget source inspection tests:** Use `Path.read_text()` to read .ts/.tsx files and verify patterns.
- **Widget field pipeline rule:** Every new widget_* field must exist in 4 places: `fields.yaml` → `field_mapping.py` → `cosmos_schema.py` → widget TypeScript type.
- **KB insert_spec() assertions parameter (S116):** Pass `assertions` as `list[dict]`, NOT `json.dumps(list)`.

## Playwright / E2E

- **Playwright route interception vs Vite proxy (S116):** Don't register route handlers for URL patterns that share paths with safe GET endpoints.
- **Live E2E rate limiting (S116):** 3s inter-class cooldown + progressive backoff retry (5s/10s/15s) with page reload.
- **Playwright timeout layering (S134):** Later `--timeout=` flags win. Live API tests need 120s+ per test.
- **Playwright wait_until="networkidle" vs live SPAs (S134):** Use `wait_until="load"` and explicit `wait_for_selector()` instead.
- **Playwright text_content() vs inner_text() (S135):** Use `page.inner_text("body")` — returns only visible rendered text, unlike `text_content()` which includes style tags.
- **Mantine NavLink DOM structure (S135):** Icons are siblings, not ancestors. Walk UP to `ancestor::a[1]` then search DOWN for `svg`.
- **CSS class selectors match ALL sharing elements (S138):** Use text content matching instead of CSS class selectors when multiple same-component instances exist.
- **Before/after comparison for search/filter on live data (S138):** Capture state before action → compare after. Skip if no observable change.
- **DOM ancestry disambiguation in Playwright (S138):** Use `el.closest('tbody')` to determine which context an element is in.
- **Rate limit false positives in live E2E (S137):** Never search for HTTP status codes as bare substrings in page text.
- **NEVER capture/restore original values in E2E tests (S139, SPEC-1655):** Just mutate, assert, move on. Re-seed handles state reset.
- **Staging mutations are safe and expected (S138):** ALL data-mutating actions MUST be executed in tests. Disposable member pattern.

## Frontend / Widget

- **React Router navigate() drops query params (S135):** Wrap `useNavigate()` in `useQueryPreservingNavigate` for persistent query params.
- **Closed Shadow DOM inspection (S120):** Widget uses `attachShadow({ mode: 'closed' })`. Use `window.AgentRed` API or screenshots to verify.
- **Shopify Theme App Extension widget key sync (S120):** Re-seeding widget keys does NOT auto-update Theme App Extension. Update via Shopify Admin API PUT.

## Infrastructure

- **Rate limiting in verification scripts:** Insert 65s cooldowns between pipeline phases. Accept 429 as valid.
- **Pre-flight checklist:** `scripts/pre_flight_checklist.py` — run for every deployment.
- **Live config pipeline tests:** `tests/security/test_config_pipeline_live.py` — 26 tests. Run after every deployment.
- **Staging remaker-digital-001 key (S137):** Re-seeded credentials. Owner-created `STAGING_REMAKER_DIGITAL_001_SUPERADMIN_KEY` in .env.local also works.
"""

OWNER_PREFS_CONTENT = """# Owner Preferences

Behavioral directives from the project owner (Mike) that apply across all sessions.

## Quality & Process
- **No effort estimates** — focus on quality (correctness, completeness, absence of defects)
- **Technical work > creative/content work** — technical work has elevated priority
- **Manual test → automated test rule** — every bug fix MUST include a regression test
- **Honest feedback** — never exaggerate quality or impact of Mike's input

## Product
- **MANDATORY P0: Customer identification for every conversation** — See SPEC-1489 (intent taxonomy) and related customer identity specs
- **E-commerce identity assumed** — warning is deliberate friction to discourage anonymity
"""


def main():
    kdb = db.KnowledgeDB()

    # 1. Insert cross-cutting lessons
    try:
        kdb.insert_document(
            id="DOC-cross-cutting-lessons",
            title="Cross-Cutting Development Lessons",
            category="reference",
            status="current",
            changed_by="S140",
            change_reason="S140 audit: migrated 48 cross-cutting lessons from MEMORY.md to KB per GOV-08",
            content=LESSONS_CONTENT,
            tags=["lessons", "patterns", "gotchas", "testing", "deployment", "playwright", "cosmos-db"],
        )
        print("✓ DOC-cross-cutting-lessons inserted")
    except Exception as e:
        print(f"✗ DOC-cross-cutting-lessons: {e}")

    # 2. Insert owner preferences
    try:
        kdb.insert_document(
            id="DOC-owner-preferences",
            title="Owner Preferences and Behavioral Directives",
            category="governance",
            status="current",
            changed_by="S140",
            change_reason="S140 audit: migrated 6 owner preference directives from MEMORY.md to KB per GOV-08",
            content=OWNER_PREFS_CONTENT,
            tags=["owner", "preferences", "governance", "quality", "process"],
        )
        print("✓ DOC-owner-preferences inserted")
    except Exception as e:
        print(f"✗ DOC-owner-preferences: {e}")

    # Verify
    d1 = kdb.get_document("DOC-cross-cutting-lessons")
    d2 = kdb.get_document("DOC-owner-preferences")
    print(f"\nVerification:")
    print(
        f"  DOC-cross-cutting-lessons: {len(d1['content'])} chars" if d1 else "  DOC-cross-cutting-lessons: NOT FOUND"
    )
    print(f"  DOC-owner-preferences: {len(d2['content'])} chars" if d2 else "  DOC-owner-preferences: NOT FOUND")

    docs = kdb.list_documents()
    print(f"  Total documents: {len(docs)}")

    kdb.close()


if __name__ == "__main__":
    main()
