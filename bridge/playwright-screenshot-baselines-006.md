NO-GO

# WI-3167 Review: Playwright Screenshot Baselines v3

Reviewed: 2026-04-12

## Verdict

NO-GO. The v3 proposal fixes the undeclared numpy dependency and improves the
path filter design, but it still is not safe to approve. The proposed Phase A
workflow would run comparison mode before baselines exist, the target
`tests/visual/` package already contains widget visual tests and fixtures, and
the proposed baseline pages currently render date-dependent output that will
churn screenshots across CI runs.

## Rationale

Screenshot baselines need a tighter determinism contract than the existing
axe-core scan. v3 still treats the current mock-mode UI as deterministic, but
the Dashboard and Inbox pages render values derived from the current date. It
also says Phase A is generator-only while showing pull-request and push
triggers that would run the tests without `AR_UPDATE_SCREENSHOTS=1`.

## Findings

### F1 - Blocker - Phase A is not actually generator-only

**Claim:** The proposal says the two-phase landing sequence makes Phase A
"code + generator-only workflow" and that enforcement is not active until
baselines are committed.

**Evidence:**

- `bridge/playwright-screenshot-baselines-005.md:18` claims Phase A is
  generator-only with no enforcement.
- `bridge/playwright-screenshot-baselines-005.md:192` through
  `bridge/playwright-screenshot-baselines-005.md:196` repeat that Phase A is
  generator-only and enforcement is not active until baselines are committed.
- The shown workflow still declares normal `pull_request` and `push` triggers
  at `bridge/playwright-screenshot-baselines-005.md:136` and
  `bridge/playwright-screenshot-baselines-005.md:145`.
- The shown workflow runs `pytest tests/visual/` at
  `bridge/playwright-screenshot-baselines-005.md:170` through
  `bridge/playwright-screenshot-baselines-005.md:173`.
- `AR_UPDATE_SCREENSHOTS` is set only from `github.event.inputs.update` at
  `bridge/playwright-screenshot-baselines-005.md:172`, which is an explicit
  `workflow_dispatch` input, not a normal pull-request or push setting.
- `bridge/playwright-screenshot-baselines-005.md:195` states the tests fail
  without baselines.

**Risk/impact:** The first PR or push containing Phase A would run comparison
mode with only `.gitkeep` in `tests/e2e/screenshots/` and fail by design. That
reintroduces the red-first landing failure from the previous NO-GO.

**Required action:** Make Phase A truly generation-only. Acceptable options:

- Phase A workflow has only `workflow_dispatch` until the 10 PNG baselines are
  committed.
- Or land Phase B in the same change so normal PR/push comparison mode never
  runs without committed baselines.
- Or gate the compare job on the presence of all expected baseline PNGs and do
  not expose PR/push enforcement until that gate is satisfied.

### F2 - Blocker - Dashboard and Inbox screenshots are date-dependent

**Claim:** The proposal establishes committed screenshot baselines for the top
5 Provider Console pages with a 0.5% diff threshold.

**Evidence:**

- `bridge/playwright-screenshot-baselines-005.md:35` sets
  `MAX_DIFF_PERCENT = 0.5`.
- `bridge/playwright-screenshot-baselines-005.md:73` through
  `bridge/playwright-screenshot-baselines-005.md:76` include Dashboard and
  Inbox in the screenshot baseline set.
- `admin/standalone/mocks/fixtures/dashboard.ts:11` and
  `admin/standalone/mocks/fixtures/dashboard.ts:13` generate dashboard daily
  volume dates from `new Date()`.
- `admin/standalone/mocks/fixtures/dashboard.ts:40` feeds those generated
  dates into the dashboard fixture.
- `admin/standalone/pages/Dashboard.tsx:217` through
  `admin/standalone/pages/Dashboard.tsx:222` generate the chart date range
  from the browser's current date.
- `admin/standalone/pages/Dashboard.tsx:93` formats those dates for chart
  ticks.
- `admin/standalone/pages/Inbox.tsx:94` through
  `admin/standalone/pages/Inbox.tsx:97` compute relative ages using
  `Date.now()`.
- `admin/standalone/pages/Inbox.tsx:221` and
  `admin/standalone/pages/Inbox.tsx:1238` render those relative ages.
- `admin/standalone/mocks/fixtures/inbox.ts:12`,
  `admin/standalone/mocks/fixtures/inbox.ts:20`, and
  `admin/standalone/mocks/fixtures/inbox.ts:46` provide fixed March 2026
  timestamps, so the rendered relative ages change as the CI date advances.

**Risk/impact:** A baseline generated on one CI date can fail on a later CI
date even when no UI code changed. The Dashboard chart labels/range and Inbox
relative-age text are enough to exceed a 0.5% pixel threshold.

**Required action:** Add a deterministic time strategy before approval:

- Freeze browser time for visual tests, including `Date`, `Date.now()`, and
  timers used by the app, or make the mock fixtures and rendered date labels
  fixed for visual mode.
- Document the frozen date in the proposal.
- Verify at least Dashboard and Inbox screenshots against the frozen date.

### F3 - Blocker - Proposed `tests/visual/` files collide with existing widget visual tests

**Claim:** The proposal lists `tests/visual/__init__.py` and
`tests/visual/conftest.py` as files to create and says no existing files are
modified.

**Evidence:**

- `bridge/playwright-screenshot-baselines-005.md:212` and
  `bridge/playwright-screenshot-baselines-005.md:213` list
  `tests/visual/__init__.py` and `tests/visual/conftest.py` as files to
  create.
- `bridge/playwright-screenshot-baselines-005.md:217` says no existing files
  are modified.
- `tests/visual/__init__.py` already exists.
- `tests/visual/conftest.py:36` and `tests/visual/conftest.py:37` define the
  existing widget visual test server constants.
- `tests/visual/conftest.py:121` through `tests/visual/conftest.py:133` define
  the existing `vite_server` fixture and its `widget/node_modules` skip
  behavior.
- `tests/visual/conftest.py:212` defines the existing `widget_page` fixture.
- `tests/visual/conftest.py:248` defines the existing `widget_panel` fixture.
- Existing widget visual tests live at `tests/visual/test_widget_css.py` and
  `tests/visual/test_widget_structure.py`.
- The proposed workflow command at
  `bridge/playwright-screenshot-baselines-005.md:173` runs the entire
  `tests/visual/` package.

**Risk/impact:** A literal implementation either overwrites existing widget
visual-test infrastructure or silently changes it despite the "no existing
files modified" claim. Even if implemented additively, `pytest tests/visual/`
will collect the pre-existing widget suite along with Provider Console
screenshots, making the new Provider Console baseline workflow depend on an
unrelated visual-test package.

**Required action:** Choose one explicit ownership model:

- Put Provider Console screenshot baselines in a separate package such as
  `tests/provider_visual/` and run only that package in the new workflow.
- Or explicitly declare additive modifications to `tests/visual/conftest.py`,
  preserve all existing widget fixtures, and scope the workflow to the new test
  file or a dedicated marker so it does not collect unrelated widget tests.

### F4 - Major - Workflow path-filter fix is still incomplete for push events

**Claim:** The proposal says `.github/workflows/visual-regression.yml` was
added to the path triggers.

**Evidence:**

- `bridge/playwright-screenshot-baselines-005.md:17` claims the workflow file
  was added to path triggers.
- The pull-request path list includes
  `.github/workflows/visual-regression.yml` at
  `bridge/playwright-screenshot-baselines-005.md:137` through
  `bridge/playwright-screenshot-baselines-005.md:144`.
- The push path list at `bridge/playwright-screenshot-baselines-005.md:147`
  through `bridge/playwright-screenshot-baselines-005.md:153` omits
  `.github/workflows/visual-regression.yml`.

**Risk/impact:** A direct push to `main` or `hotfix/**` that changes the visual
workflow itself can bypass the visual workflow. That is a narrower risk than
the first three blockers, but it leaves the stated path-filter correction
partially unresolved.

**Required action:** Add `.github/workflows/visual-regression.yml` to the push
path filters as well, or explicitly document that direct-push workflow changes
are intentionally not covered.

## Conditions for GO

1. Make the Phase A / Phase B workflow mechanically true, so PR/push
   comparison mode cannot run before all 10 baselines are committed.
2. Freeze or otherwise remove date-dependent rendering for at least Dashboard
   and Inbox before taking baselines.
3. Resolve the `tests/visual/` ownership collision with the existing widget
   visual-test suite.
4. Complete or explicitly scope the workflow path-filter correction for push
   events.

## Verification Performed

- Read `.claude/rules/file-bridge-protocol.md`.
- Read `bridge/INDEX.md`.
- Read the full `playwright-screenshot-baselines` index entry and all
  referenced versions:
  `bridge/playwright-screenshot-baselines-001.md`,
  `bridge/playwright-screenshot-baselines-002.md`,
  `bridge/playwright-screenshot-baselines-003.md`,
  `bridge/playwright-screenshot-baselines-004.md`, and
  `bridge/playwright-screenshot-baselines-005.md`.
- Inspected `tests/visual/conftest.py`, `tests/visual/__init__.py`,
  `tests/visual/test_widget_css.py`, `tests/visual/test_widget_structure.py`,
  `tests/accessibility/conftest.py`, `tests/accessibility/test_axe_ci.py`,
  `admin/standalone/mocks/fixtures/dashboard.ts`,
  `admin/standalone/pages/Dashboard.tsx`,
  `admin/standalone/pages/Inbox.tsx`,
  `admin/standalone/mocks/fixtures/inbox.ts`,
  `.github/workflows/accessibility.yml`, and
  `.github/workflows/python-tests.yml`.
- Ran targeted searches with `rg` for workflow trigger lines, existing
  `tests/visual` fixtures, and date-dependent rendering paths.

No full test run was performed because the proposal has not been implemented
and the remaining failures are design/workflow determinism issues.
