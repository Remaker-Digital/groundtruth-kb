GO

# WI-3167 Review: Playwright Screenshot Baselines v7

Reviewed: 2026-04-12

## Verdict

GO. The v7 revision resolves the remaining date-alignment blocker from
`bridge/playwright-screenshot-baselines-012.md` and preserves the prior approved
shape: provider screenshots live in a separate test package, Phase A is
manual/generator-only, browser time is frozen with `page.clock.set_fixed_time`,
Dashboard server-side dates are deterministic, and Recharts is allowed to settle
before capture.

## Rationale

The previous NO-GO was narrowly about the Dashboard chart validating the wrong
state: the mock API daily range ended on 2026-03-10 while the proposed browser
clock ended the chart range on 2026-04-01. v7 changes the visual frozen time to
`2026-03-10T12:00:00Z`, so the API daily range and browser chart range align
for the default 30-day Dashboard view. I also reproduced the narrow Dashboard
stability check in this checkout without writing screenshot files into the repo.

## Findings

### F1 - Resolved - Dashboard API range and browser chart range now align

**Claim:** v7 changes the browser frozen time to
`2026-03-10T12:00:00Z` so the Dashboard fixture and browser chart ranges both
cover February 9 through March 10, 2026.

**Evidence:**

- `bridge/playwright-screenshot-baselines-013.md:14` through
  `bridge/playwright-screenshot-baselines-013.md:16` state that the browser
  frozen time is now `2026-03-10T12:00:00Z` to match the Dashboard fixture end
  date.
- `bridge/playwright-screenshot-baselines-013.md:22` through
  `bridge/playwright-screenshot-baselines-013.md:24` state the intended
  30/30-day overlap.
- `admin/standalone/mocks/fixtures/dashboard.ts:8` through
  `admin/standalone/mocks/fixtures/dashboard.ts:23` generate 30 daily records
  ending at the fixed reference date `2026-03-10T12:00:00Z`.
- `admin/standalone/mocks/fixtures/dashboard.ts:41` assigns that generated
  range to the Dashboard daily fixture.
- `admin/standalone/pages/Dashboard.tsx:211` through
  `admin/standalone/pages/Dashboard.tsx:223` build the rendered chart range
  from browser `new Date()` and merge by date with API data.
- Command result:
  `node -e "...calculate fixed API range and frozen browser chart range..."`
  returned `apiStart: "2026-02-09"`, `apiEnd: "2026-03-10"`,
  `chartStart: "2026-02-09"`, `chartEnd: "2026-03-10"`,
  `overlapCount: 30`, and `missingCount: 0`.

**Risk/impact:** The prior risk that the Dashboard baseline would mostly
validate fallback zero-filled chart days is addressed.

**Required action:** Implement the visual test `FROZEN_TIME` as
`2026-03-10T12:00:00Z` and keep the Dashboard fixture reference date aligned
with it.

### F2 - Resolved - Aligned Dashboard stability proof reproduced

**Claim:** v7 reports a two-capture Dashboard desktop stability proof with
0 differing pixels after date alignment.

**Evidence:**

- `bridge/playwright-screenshot-baselines-013.md:26` through
  `bridge/playwright-screenshot-baselines-013.md:37` report the aligned
  Dashboard stability proof using Chromium headless, the 2026-03-10 frozen
  time, a 2500 ms settle, and fixed mock data.
- Current checkout command result:
  in-memory Playwright capture of Dashboard twice at 1280x800 with
  `page.clock.set_fixed_time("2026-03-10T12:00:00Z")`, mock auth, tenant
  parameter, `networkidle`, heading guard, and 2500 ms settle returned
  `diff_pixels=0` and `diff_percent=0.0000`.
- `admin/standalone/pages/Dashboard.tsx:325` through
  `admin/standalone/pages/Dashboard.tsx:379` render the target Dashboard chart
  with Recharts `AreaChart` and two `Area` series.
- `admin/standalone/node_modules/recharts/lib/cartesian/Area.js:415` through
  `admin/standalone/node_modules/recharts/lib/cartesian/Area.js:418` show the
  browser default animation is active with `animationDuration: 1500`, so the
  proposed 2500 ms wait clears the default animation duration.

**Risk/impact:** The prior stability proof was for the mismatched chart range.
The repeated capture now covers the aligned Dashboard state.

**Required action:** Keep the 2500 ms settle or replace it only with a stronger
explicit animation-disable strategy that is proven against the Dashboard chart.

## Approval Conditions

1. Phase A remains `workflow_dispatch` only and unconditionally sets
   `AR_UPDATE_SCREENSHOTS=1`; do not enable PR/push comparison until all 10
   Ubuntu/Chromium baseline PNGs are committed.
2. Provider Console screenshot tests stay isolated under `tests/provider_visual/`
   and do not collect the existing widget tests under `tests/visual/`.
3. Phase B must add PR/push triggers only in the follow-up commit that includes
   the generated baseline PNGs in `tests/e2e/screenshots/`.
4. Post-implementation verification should run the full provider visual suite
   across both desktop and tablet viewports and review the generated artifacts.

## Verification Performed

- Read `.claude/rules/file-bridge-protocol.md`.
- Read `bridge/INDEX.md`.
- Read the full `playwright-screenshot-baselines` index entry and all
  referenced versions:
  `bridge/playwright-screenshot-baselines-001.md` through
  `bridge/playwright-screenshot-baselines-013.md`.
- Inspected `admin/standalone/mocks/fixtures/dashboard.ts`,
  `admin/standalone/pages/Dashboard.tsx`,
  `admin/standalone/mocks/fixtures/inbox.ts`,
  `admin/standalone/pages/Inbox.tsx`,
  `tests/accessibility/conftest.py`, `admin/standalone/package.json`,
  `admin/standalone/vite.config.ts`, and installed Recharts files under
  `admin/standalone/node_modules/`.
- Ran targeted commands:
  `git status --short`,
  `git diff -- admin/standalone/mocks/fixtures/dashboard.ts`,
  `rg` checks for Dashboard, Inbox, Vite, and Recharts evidence,
  a Node date-range overlap calculation, and an in-memory Playwright two-capture
  Dashboard stability check.

No full provider visual suite was run because the proposed `tests/provider_visual/`
test package and `.github/workflows/visual-regression.yml` are not present in
the checkout yet.
