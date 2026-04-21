# NO-GO: WI-3166 axe-core WCAG 2.1 AA CI Enforcement

## Verdict

NO-GO.

The direction is sound: a separate accessibility workflow and a small axe-focused
test module are appropriate for CI. The proposal is not yet safe to implement
because the proposed tests will not reliably exercise the 9 named Provider
Console pages. As written, they navigate directly to SPA routes without the
auth and tenant context that the standalone admin requires before rendering
admin content.

## Findings

### 1. Blocking: proposed navigation will scan the auth gate, not the target pages

The proposal's test shape is:

```python
page.goto(f"{base_url}{path}")
page.wait_for_load_state("networkidle")
assert_no_critical_a11y_violations(page)
```

and the proposed CI command sets:

```bash
--base-url=http://localhost:3300/admin/standalone
```

That URL plan supplies neither `sessionStorage.agentred_api_key` nor a
`?tenant=` query parameter.

Evidence:

- `admin/standalone/index.tsx:71` through `admin/standalone/index.tsx:80`
  reads auth only from `sessionStorage.agentred_api_key` or
  `sessionStorage.agentred_session_token`.
- `admin/standalone/index.tsx:232` through `admin/standalone/index.tsx:241`
  renders `ApiKeyLogin` and never mounts the routed admin layout when auth is
  missing.
- `admin/standalone/layouts/StandaloneLayout.tsx:272` through
  `admin/standalone/layouts/StandaloneLayout.tsx:289` requires `?tenant=` for
  authenticated standalone admin sessions and calls `onLogout()` when it is
  absent.
- Existing mock E2E infrastructure documents and implements the required setup:
  `tests/e2e_mock/conftest.py:92` through `tests/e2e_mock/conftest.py:113`
  injects `agentred_api_key` before page JavaScript runs, and
  `tests/e2e_mock/conftest.py:150` through `tests/e2e_mock/conftest.py:155`
  appends `?tenant=mock-tenant-001` during navigation.

Impact:

- Best case: all 9 tests run axe against the login page, producing a false
  sense of WCAG coverage while the Provider Console pages remain unscanned.
- If auth is later added without tenant-aware navigation, the layout will log
  the session out before scanning protected admin content.

Required action:

- Add an accessibility test fixture equivalent to the mock E2E auth setup:
  inject `sessionStorage.agentred_api_key` via `context.add_init_script()` or
  `page.add_init_script()` before the first navigation.
- Navigate with a tenant query parameter, for example
  `?tenant=mock-tenant-001`, preserving it for every route under test.
- Before each axe assertion, assert a page-specific heading or landmark from
  the intended route so CI fails if it is scanning the login page, loading
  shell, or redirect target.

### 2. High: CI enforcement must not silently skip when axe is unavailable

The proposal says the new CI module should "Skip gracefully if
`axe_playwright_python` not installed." That is acceptable for optional local
E2E coverage, but it is not acceptable for a CI enforcement workflow whose
objective is to fail builds on critical or serious violations.

Evidence:

- The current optional E2E module uses `pytest.importorskip` at
  `tests/e2e/test_accessibility.py:15` through
  `tests/e2e/test_accessibility.py:16`.
- The dependency is already declared for test environments at
  `requirements-test.txt:31` through `requirements-test.txt:32`.
- The shared helper raises `ImportError` if the package is absent at
  `tests/e2e/a11y_helpers.py:30` through `tests/e2e/a11y_helpers.py:35`.

Impact:

- If the CI dependency install changes or the package import breaks, the
  accessibility workflow can pass with skipped tests instead of failing closed.

Required action:

- In the CI-enforced `tests/accessibility/` module, do not use unconditional
  `pytest.importorskip`.
- Let the helper's `ImportError` fail the job, or only allow local skips behind
  an explicit non-CI condition.

### 3. Medium: the proposed viewport fixture target is the wrong Playwright layer

The proposal places the 1280 x 800 viewport in `browser_type_launch_args`.
Viewport belongs to the browser context, not the browser launch arguments.

Evidence:

- Existing mock E2E tests set viewport on `browser.new_context(...)` at
  `tests/e2e_mock/conftest.py:101` through `tests/e2e_mock/conftest.py:104`.
- The proposal instead assigns viewport responsibility to
  `browser_type_launch_args`.

Impact:

- If implemented literally, the viewport may be ignored or passed to the wrong
  API, leading to startup errors or inconsistent axe scan surfaces.

Required action:

- Use `browser_context_args` or a custom `browser.new_context(viewport=...)`
  fixture for viewport and base URL.
- Keep browser launch arguments limited to browser process settings.

## Conditions For GO

Codex can approve a revision once it:

1. Authenticates the SPA before first navigation.
2. Includes and preserves a tenant query parameter for every route.
3. Asserts the intended page rendered before running axe.
4. Fails closed in CI if axe cannot be imported.
5. Configures viewport at the browser context layer.

## Reviewed Evidence

- `bridge/axe-core-ci-enforcement-001.md`
- `admin/standalone/index.tsx`
- `admin/standalone/layouts/StandaloneLayout.tsx`
- `tests/e2e_mock/conftest.py`
- `tests/e2e/test_accessibility.py`
- `tests/e2e/a11y_helpers.py`
- `requirements-test.txt`
- `admin/standalone/package.json`
- `admin/standalone/vite.config.ts`
- `.github/workflows/python-tests.yml`
