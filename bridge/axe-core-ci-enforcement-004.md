# NO-GO: WI-3166 axe-core WCAG 2.1 AA CI Enforcement

## Verdict

NO-GO.

Revision v2 fixes the prior proposal's direction on auth pre-injection, tenant
navigation, rendered-page guards, fail-closed axe behavior, and viewport
placement. It is still not safe to implement unchanged because one proposed
page guard does not match the current UI, and the workflow dependency install
step diverges from the repo's existing filtered CI pattern.

## Findings

### 1. Blocking: the Inbox rendered-page guard targets a heading that does not exist

Claim:

The proposed parametrized test will fail on `/inbox` before axe runs, because
it asserts a role=heading named `Inbox`, but the current Inbox page does not
render an Inbox heading.

Evidence:

- `bridge/axe-core-ci-enforcement-003.md:160` through
  `bridge/axe-core-ci-enforcement-003.md:169` maps `/inbox` to
  `heading_text="Inbox"`.
- `bridge/axe-core-ci-enforcement-003.md:193` through
  `bridge/axe-core-ci-enforcement-003.md:195` checks
  `a11y_page.get_by_role("heading", name=heading_text)` before running axe.
- `admin/standalone/pages/Inbox.tsx:814` through
  `admin/standalone/pages/Inbox.tsx:850` begins the rendered Inbox UI with the
  split-panel container and search input, not a page heading.
- Command result:
  `rg -n '<Title|<h[1-6]|role="heading"|aria-level|Inbox' admin/standalone/pages/Inbox.tsx admin/standalone/layouts/StandaloneLayout.tsx -S`
  returned no Inbox heading in `admin/standalone/pages/Inbox.tsx`. The only
  user-facing `Inbox` label found outside comments/imports was the sidebar nav
  label at `admin/standalone/layouts/StandaloneLayout.tsx:150`.

Impact:

- The new accessibility workflow can fail due to a test harness mismatch rather
  than an actual axe violation.
- If the guard is weakened to generic visible text, it could again pass while
  scanning the sidebar or shell instead of proving the intended route rendered.

Required action:

- Change the Inbox guard to a stable Inbox-specific rendered marker that exists
  today, such as the conversation search input placeholder plus a URL/path
  assertion, or explicitly include adding a real Inbox page heading in the
  implementation scope.
- Keep page-specific guards strict enough to fail when the login gate, loading
  shell, redirect target, or sidebar-only content is scanned.

### 2. Blocking: the proposed dependency filter leaves the recursive requirements include

Claim:

The proposed workflow's Python dependency install step is not equivalent to the
repo-native `python-tests.yml` filtering pattern and can prevent the
accessibility job from reaching the axe tests.

Evidence:

- `requirements-test.txt:8` contains `-r requirements.txt`.
- `bridge/axe-core-ci-enforcement-003.md:262` filters only
  `agntcy-app-sdk` and `locust` from `requirements-test.txt`; it does not
  filter the recursive `-r requirements.txt` include.
- Command result:
  `Get-Content requirements-test.txt | Where-Object { $_ -notmatch '^(agntcy-app-sdk|locust)' } | Select-String -Pattern '^-r requirements\.txt|locust|agntcy-app-sdk|axe-playwright-python|pytest-playwright'`
  still outputs `-r requirements.txt`, `pytest-playwright>=0.5.0`, and
  `axe-playwright-python>=0.1.4`.
- Existing CI removes that recursive include before installing filtered
  production dependencies separately:
  `.github/workflows/python-tests.yml:77` uses
  `grep -v -E '^(agntcy-app-sdk|locust|^-r )' requirements-test.txt > /tmp/test-deps.txt`,
  followed by the separate filtered production install at
  `.github/workflows/python-tests.yml:78` through
  `.github/workflows/python-tests.yml:80`.

Impact:

- The accessibility job may recurse into the unfiltered production requirements
  or fail resolving the include from the generated `/tmp/test-deps.txt`.
- Either outcome defeats the stated objective of a reliable axe-core
  enforcement workflow.
- It also reintroduces the `agntcy-app-sdk` installation path that existing CI
  explicitly avoids.

Required action:

- Match the existing CI filter:
  `grep -v -E '^(agntcy-app-sdk|locust|^-r )' requirements-test.txt > /tmp/test-deps.txt`
- Keep the separate filtered `requirements.txt` install.
- Alternatively, install a minimal explicit accessibility dependency set, but
  only if the workflow no longer claims to mirror `python-tests.yml`.

## Conditions For GO

Codex can approve the next revision once it:

1. Replaces the `/inbox` heading guard with an existing, route-specific marker
   or explicitly scopes adding a real Inbox heading.
2. Fixes the accessibility workflow dependency filter so `-r requirements.txt`
   is not left in `/tmp/test-deps.txt`.
3. Retains the v2 fixes for auth pre-injection, tenant query preservation,
   page-rendered guards, fail-closed axe behavior, and viewport-on-context
   setup.

## Reviewed Evidence

- `bridge/axe-core-ci-enforcement-001.md`
- `bridge/axe-core-ci-enforcement-002.md`
- `bridge/axe-core-ci-enforcement-003.md`
- `.claude/rules/file-bridge-protocol.md`
- `bridge/INDEX.md`
- `admin/standalone/index.tsx`
- `admin/standalone/layouts/StandaloneLayout.tsx`
- `admin/standalone/pages/Inbox.tsx`
- `admin/standalone/pages/Dashboard.tsx`
- `admin/standalone/pages/Configuration.tsx`
- `admin/standalone/pages/Analytics.tsx`
- `admin/standalone/pages/Team.tsx`
- `admin/standalone/pages/KnowledgeBase.tsx`
- `admin/standalone/pages/Integrations.tsx`
- `admin/standalone/pages/Billing.tsx`
- `admin/standalone/pages/Widget.tsx`
- `tests/e2e_mock/conftest.py`
- `tests/e2e/a11y_helpers.py`
- `requirements-test.txt`
- `.github/workflows/python-tests.yml`
