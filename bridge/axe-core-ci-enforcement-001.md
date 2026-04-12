# WI-3166: axe-core WCAG 2.1 AA CI Enforcement

## Proposal (Prime Builder → Codex Review)

**Work Item:** WI-3166
**Spec:** SPEC-2103 (axe-core WCAG 2.1 AA enforcement in CI)
**Priority:** P2
**Session:** S282

---

## Objective

Add axe-core accessibility scanning to the CI pipeline so critical and serious
WCAG 2.1 AA violations fail the build. Covers the 9 Provider Console pages
specified in SPEC-2103.

## Current State

- `tests/e2e/test_accessibility.py` exists but uses route paths (`/provider/dashboard`)
  that don't match the actual standalone SPA routes. Requires a full dev server and is
  excluded from all CI test shards.
- `tests/e2e/a11y_helpers.py` provides `assert_no_critical_a11y_violations()` — wraps
  `axe-playwright-python` with impact-level filtering. Critical/serious = fail,
  minor/moderate = log.
- `axe-playwright-python` and `pytest-playwright` are already in `requirements-test.txt`.
- `admin/standalone/` is the tenant-facing SPA ("Provider Console") with `dev:mock` mode
  (Vite `--mode mock`) that intercepts `/api/*` with in-memory fixtures. Zero backend
  dependency. Port 3300, basename `/admin/standalone`.

## Approach: New CI Workflow + Dedicated Test Module

### Rationale

1. **Separate workflow** (`accessibility.yml`) rather than adding to existing test shards
   because this requires Node.js + Vite dev server — a fundamentally different runtime
   from pure Python unit tests.
2. **New test module** (`tests/accessibility/`) rather than patching `tests/e2e/` because
   the e2e tests are designed for full integration environments. CI needs a self-contained
   module with correct SPA routes and no external dependencies.
3. **Mock dev server** (`npm run dev:mock`) provides the full React component tree with
   fixture data. Accessibility testing primarily needs structural HTML (ARIA attributes,
   heading hierarchy, form labels, landmark regions, color contrast), all of which render
   correctly in mock mode.

### Files to Create

1. **`.github/workflows/accessibility.yml`** — CI workflow
   - Triggers: PRs affecting `admin/**`, `tests/accessibility/**`, `tests/e2e/a11y_helpers.py`
   - Pushes to `main`/`hotfix/**` affecting same paths
   - Steps:
     a. Checkout
     b. Setup Node 20 + cache npm (`admin/standalone/package-lock.json`)
     c. Setup Python 3.12 + cache pip
     d. `npm ci` in `admin/standalone/` (installs shared deps via `@shared` alias)
     e. Start mock dev server: `npx vite --mode mock --port 3300` (background)
     f. Wait for server ready: `curl --retry 10 --retry-delay 2 http://localhost:3300/admin/standalone/`
     g. Install Python test deps (filtered, same as python-tests.yml)
     h. `playwright install chromium --with-deps`
     i. `pytest tests/accessibility/ --base-url=http://localhost:3300/admin/standalone -v --tb=short --junitxml=a11y-results.xml`
     j. Upload JUnit XML + step summary
   - Concurrency group: `a11y-${{ github.ref }}`, cancel-in-progress

2. **`tests/accessibility/__init__.py`** — empty marker

3. **`tests/accessibility/conftest.py`** — minimal conftest
   - Imports shared pytest-playwright fixtures
   - Sets `@pytest.fixture(scope="session")` for `browser_type_launch_args` to use
     `--headless` mode with reasonable viewport (1280×800)

4. **`tests/accessibility/test_axe_ci.py`** — 9 parametrized tests
   - Reuses `assert_no_critical_a11y_violations()` from `tests/e2e/a11y_helpers.py`
   - Route mapping (SPA route → page name):
     | Route | Page Name |
     |-------|-----------|
     | `/` | Dashboard |
     | `/configuration` | Configuration |
     | `/inbox` | Inbox |
     | `/analytics` | Analytics |
     | `/team` | Team |
     | `/knowledge-base` | Knowledge Base |
     | `/integrations` | Integrations |
     | `/billing` | Billing |
     | `/widget` | Widget |
   - Each test: navigate to route, `wait_for_load_state("networkidle")`, run axe
   - Skip gracefully if `axe_playwright_python` not installed (same `importorskip` pattern)

### Files NOT Modified

- `tests/e2e/test_accessibility.py` — unchanged (remains for full integration testing)
- `tests/e2e/a11y_helpers.py` — unchanged (shared helper, imported by new tests)
- `.github/workflows/python-tests.yml` — unchanged (no new shard)

### Verification Plan

1. All 9 page tests pass locally against `npm run dev:mock` in `admin/standalone/`
2. Workflow YAML validates with `actionlint` (if available)
3. No regressions in existing CI shards

### Risk Assessment

- **Low risk:** New workflow and test module only. No changes to existing code.
- **Mock mode dependency:** If mock fixtures don't cover a page's initial render,
  the page may show a loading state. axe-core still catches structural violations
  (missing labels, ARIA roles, heading hierarchy) on loading states.
- **False positives:** Third-party components (Mantine) may have minor a11y issues
  outside our control. Only critical/serious violations fail; minor/moderate are warnings.

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
