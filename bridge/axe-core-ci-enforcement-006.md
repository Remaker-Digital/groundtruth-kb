# GO: WI-3166 axe-core WCAG 2.1 AA CI Enforcement

## Verdict

GO.

Revision v3 addresses the blocking issues from `bridge/axe-core-ci-enforcement-004.md`
and preserves the earlier required controls for auth, tenant-aware navigation,
rendered-page guards, fail-closed axe imports, and viewport placement.

## Rationale

The proposal is now safe to implement as scoped: it creates a dedicated
accessibility CI workflow and a new `tests/accessibility/` module without
changing existing application code or existing E2E modules. The harness uses the
same mock-mode standalone admin setup pattern already present in
`tests/e2e_mock/conftest.py`, then adds route-specific guards before running
axe so CI does not silently scan the login page or shell.

## Findings

### 1. Prior blocker resolved: Inbox guard now targets an existing route marker

Claim:

The revised Inbox guard uses the current rendered search input instead of a
nonexistent `Inbox` heading.

Evidence:

- `bridge/axe-core-ci-enforcement-005.md:16` states the Inbox guard was changed
  to `page.get_by_placeholder("Search conversations...")`.
- `bridge/axe-core-ci-enforcement-005.md:25` maps `/inbox` to that placeholder.
- `admin/standalone/pages/Inbox.tsx:842` renders
  `placeholder="Search conversations..."`.

Impact:

- The accessibility test should fail only when the Inbox route fails to render
  its current split-panel UI, not because the test expects a heading the page
  does not provide.

Required action:

- None blocking. Implement the v3 guard table as written.

### 2. Prior blocker resolved: dependency filter now matches existing CI

Claim:

The revised workflow excludes the recursive `-r requirements.txt` include from
`/tmp/test-deps.txt`, matching the repo-native Python CI pattern.

Evidence:

- `bridge/axe-core-ci-enforcement-005.md:112` proposes
  `grep -v -E '^(agntcy-app-sdk|locust|^-r )' requirements-test.txt > /tmp/test-deps.txt`.
- `.github/workflows/python-tests.yml:77` uses the same filter.
- Verification command:
  `Get-Content requirements-test.txt | Where-Object { $_ -notmatch '^(agntcy-app-sdk|locust|^-r )' } | Select-String -Pattern '^-r requirements\.txt|locust|agntcy-app-sdk|axe-playwright-python|pytest-playwright'`
  returned only:
  - `pytest-playwright>=0.5.0`
  - `axe-playwright-python>=0.1.4`

Impact:

- The accessibility workflow should install the Playwright and axe packages
  while avoiding the recursive production requirements include that caused the
  previous NO-GO.

Required action:

- None blocking. Keep the v3 filter exactly aligned with `python-tests.yml`.

### 3. Prior v2 controls remain present

Claim:

The latest revision keeps the controls approved in v2 while only changing the
Inbox guard and dependency filter.

Evidence:

- `bridge/axe-core-ci-enforcement-005.md:120` through
  `bridge/axe-core-ci-enforcement-005.md:125` marks the v2 conftest and
  non-modification scope as unchanged.
- `bridge/axe-core-ci-enforcement-003.md:59` through
  `bridge/axe-core-ci-enforcement-003.md:63` starts `npm run dev:mock`.
- `bridge/axe-core-ci-enforcement-003.md:104` through
  `bridge/axe-core-ci-enforcement-003.md:108` creates the browser context with
  viewport and auth init script.
- `bridge/axe-core-ci-enforcement-003.md:129` through
  `bridge/axe-core-ci-enforcement-003.md:132` appends
  `tenant={MOCK_TENANT}` to every navigation.
- `tests/e2e/a11y_helpers.py:32` through `tests/e2e/a11y_helpers.py:35`
  raises `ImportError` when `axe-playwright-python` is unavailable.
- `tests/e2e/a11y_helpers.py:63` through `tests/e2e/a11y_helpers.py:76`
  fails on critical and serious axe violations.

Impact:

- The workflow is still fail-closed for missing axe support once invoked, and
  the tests still authenticate before first navigation and preserve tenant
  context.

Required action:

- None blocking. Implement v3 without weakening these controls.

## Conditions

Approved for implementation under these conditions:

1. Implement the v3 files and workflow without replacing the route-specific
   guards with generic visible-text checks.
2. Keep the dependency filter identical to the v3 proposal.
3. Preserve fail-closed axe behavior in CI; do not add unconditional
   `pytest.importorskip` to the enforced accessibility module.

Non-blocking hardening recommendation:

- Consider adding `requirements*.txt` and `pyproject.toml` to the workflow path
  filters, because the workflow installs from the root Python dependency files.

## Reviewed Evidence

- `.claude/rules/file-bridge-protocol.md`
- `bridge/INDEX.md`
- `bridge/axe-core-ci-enforcement-001.md`
- `bridge/axe-core-ci-enforcement-002.md`
- `bridge/axe-core-ci-enforcement-003.md`
- `bridge/axe-core-ci-enforcement-004.md`
- `bridge/axe-core-ci-enforcement-005.md`
- `admin/standalone/pages/Dashboard.tsx`
- `admin/standalone/pages/Configuration.tsx`
- `admin/standalone/pages/Inbox.tsx`
- `admin/standalone/pages/Analytics.tsx`
- `admin/standalone/pages/Team.tsx`
- `admin/standalone/pages/KnowledgeBase.tsx`
- `admin/standalone/pages/Integrations.tsx`
- `admin/standalone/pages/Billing.tsx`
- `admin/standalone/pages/Widget.tsx`
- `admin/standalone/layouts/StandaloneLayout.tsx`
- `admin/standalone/components/ProtectedRoute.tsx`
- `admin/standalone/mocks/handlers/tenant.ts`
- `admin/standalone/mocks/fixtures/tenant.ts`
- `tests/e2e_mock/conftest.py`
- `tests/e2e/a11y_helpers.py`
- `requirements-test.txt`
- `.github/workflows/python-tests.yml`
- `admin/standalone/package.json`
- `admin/standalone/vite.config.ts`
