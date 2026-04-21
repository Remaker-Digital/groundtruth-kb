NO-GO

# WI-3167 Review: Playwright Screenshot Baselines v5

Reviewed: 2026-04-12

## Verdict

NO-GO. v5 fixes the Playwright clock API choice and makes Phase A
generator-only by default, but the screenshot determinism contract is still not
sound enough to approve. The frozen browser clock does not control the
server-side Vite mock data that drives the Dashboard chart, and the proposed CSS
injection does not disable Recharts' JavaScript animation path.

## Rationale

The remaining blockers are both in the critical path for stable Dashboard
baselines. Screenshot comparison can only be useful if the captured pixels are
repeatable across CI runs. v5 still leaves date-dependent mock API data outside
the browser clock and relies on CSS rules for an animation implementation that
uses `requestAnimationFrame` and a JavaScript duration prop.

## Findings

### F1 - Blocker - Browser clock freeze does not control server-side Dashboard mock dates

**Claim:** v5 says `page.clock.set_fixed_time("2026-04-01T12:00:00Z")`
makes time-derived Dashboard and Inbox screenshot content constant.

**Evidence:**

- `bridge/playwright-screenshot-baselines-009.md:16` claims
  `page.clock.set_fixed_time(FROZEN_TIME)` fixes `Date` and `Date.now()`.
- `bridge/playwright-screenshot-baselines-009.md:24` through
  `bridge/playwright-screenshot-baselines-009.md:30` define the time-freeze
  determinism guarantee.
- `bridge/playwright-screenshot-baselines-009.md:35` and
  `bridge/playwright-screenshot-baselines-009.md:144` apply the browser clock
  freeze before navigation.
- `tests/accessibility/conftest.py:32` through
  `tests/accessibility/conftest.py:44` show the reused pattern starts
  `npm run dev:mock` as a separate Vite server process.
- `admin/standalone/mocks/plugin.ts:73` through
  `admin/standalone/mocks/plugin.ts:89` register server middleware that
  intercepts `/api/*` requests.
- `admin/standalone/mocks/plugin.ts:145` through
  `admin/standalone/mocks/plugin.ts:166` execute the matched mock handler and
  serialize its response from the Vite process.
- `admin/standalone/mocks/store.ts:41` through
  `admin/standalone/mocks/store.ts:47` initialize the mock store and create the
  Dashboard fixture server-side.
- `admin/standalone/mocks/fixtures/dashboard.ts:8` through
  `admin/standalone/mocks/fixtures/dashboard.ts:17` generate daily volume dates
  from `new Date()`.
- `admin/standalone/pages/Dashboard.tsx:211` through
  `admin/standalone/pages/Dashboard.tsx:223` build the chart range from the
  browser's current date and merge in the mock API's daily data.
- Command result:
  a Playwright runtime check confirmed `page.clock.set_fixed_time(...)` fixes
  browser-page `Date.now()` values (`a`, `b`, and `now` all returned
  `1775044800000`), but that clock is scoped to the browser page, not the
  separate `npm run dev:mock` process that generates `/api/dashboard/usage/daily`.

**Risk/impact:** A baseline generated on one CI date can differ from a later CI
run even when UI code has not changed. The browser chart range is frozen to
April 1, 2026, but the server-side daily fixture still ends on the actual Vite
process date, so the overlap between API data and the chart range can shift
over time.

**Required action:** Add a server-side mock-data time strategy before approval.
Acceptable directions include:

- Make `admin/standalone/mocks/fixtures/dashboard.ts` use fixed daily dates in
  mock/visual mode.
- Or pass a visual-test frozen time into the Vite mock server process and have
  server-side fixtures use it.
- Or provide a deterministic mock reset/seed path that pins the Dashboard daily
  range before screenshots are generated.

The revised proposal should verify that `/api/dashboard/usage/daily` returns
the same date range across visual-test runs and that the range matches the
frozen browser date used by the Dashboard page.

### F2 - Blocker - CSS injection does not disable the Recharts JavaScript animation

**Claim:** v5 says injecting CSS with `animation-duration: 0s` and
`transition-duration: 0s` eliminates Recharts' `requestAnimationFrame`-based
animation.

**Evidence:**

- `bridge/playwright-screenshot-baselines-009.md:17` claims the CSS injection
  eliminates CSS and `requestAnimationFrame`-based animation.
- `bridge/playwright-screenshot-baselines-009.md:38` through
  `bridge/playwright-screenshot-baselines-009.md:48` define the CSS rule and
  a 500 ms settle.
- `bridge/playwright-screenshot-baselines-009.md:155` and
  `bridge/playwright-screenshot-baselines-009.md:156` apply the CSS after
  navigation/page guard and wait 500 ms.
- `admin/standalone/pages/Dashboard.tsx:325` through
  `admin/standalone/pages/Dashboard.tsx:379` render the Dashboard chart with
  Recharts `ResponsiveContainer`, `AreaChart`, and two `Area` components.
- `admin/standalone/node_modules/recharts/lib/cartesian/Area.js:415` through
  `admin/standalone/node_modules/recharts/lib/cartesian/Area.js:418` set
  browser animation active by default with a 1500 ms duration.
- `admin/standalone/node_modules/recharts/lib/cartesian/Area.js:242` through
  `admin/standalone/node_modules/recharts/lib/cartesian/Area.js:246` pass
  `animationDuration` and `isAnimationActive` into `react-smooth`.
- `admin/standalone/node_modules/recharts/lib/cartesian/Area.js:256` through
  `admin/standalone/node_modules/recharts/lib/cartesian/Area.js:302` use a
  child function receiving `t` to render the animated chart state.
- `admin/standalone/node_modules/recharts/lib/cartesian/Area.js:316` through
  `admin/standalone/node_modules/recharts/lib/cartesian/Area.js:318` select
  `renderAreaWithAnimation(...)` when animation is active.
- `admin/standalone/node_modules/react-smooth/src/Animate.js:222` through
  `admin/standalone/node_modules/react-smooth/src/Animate.js:224` route
  function-child animations to `runJSAnimation`.
- `admin/standalone/node_modules/react-smooth/src/Animate.js:147` through
  `admin/standalone/node_modules/react-smooth/src/Animate.js:155` pass the
  JavaScript `duration` into `configUpdate(...)`.
- `admin/standalone/node_modules/react-smooth/src/configUpdate.js:95` through
  `admin/standalone/node_modules/react-smooth/src/configUpdate.js:111` compute
  animation progress from elapsed time and schedule additional frames with
  `requestAnimationFrame`.
- `admin/standalone/node_modules/react-smooth/src/configUpdate.js:126` through
  `admin/standalone/node_modules/react-smooth/src/configUpdate.js:127` start
  the animation with `requestAnimationFrame(update)`.

**Risk/impact:** The screenshot can capture an arbitrary partial Dashboard chart
frame. A 500 ms wait is shorter than Recharts' default 1500 ms animation, and
the CSS rule does not change the JavaScript `duration` prop or the
`requestAnimationFrame` progress calculation used by this chart path.

**Required action:** Replace the CSS-only animation claim with a deterministic
Recharts strategy. Acceptable directions include:

- Disable Recharts animation in visual-test mode, for example by rendering the
  Dashboard `Area` components with `isAnimationActive={false}` under an explicit
  visual-test flag.
- Or wait/drive the actual JavaScript animation to a verified final state before
  capture, then prove repeated Dashboard captures are stable.

The revised proposal should include command evidence from this repo that two
Dashboard captures taken under the chosen strategy produce identical pixels.

## Conditions for GO

1. Freeze or seed the Vite mock server's Dashboard daily data, not just the
   browser page clock.
2. Replace CSS-only animation disabling with a strategy that actually controls
   the Recharts/react-smooth JavaScript animation path.
3. Verify Dashboard stability with repeated captures after the server-date and
   animation fixes.
4. Keep the v5 improvements: `page.clock.set_fixed_time(...)` for browser
   time, `tests/provider_visual/` separation, and Phase A as
   `workflow_dispatch`-only with `AR_UPDATE_SCREENSHOTS=1`.

## Verification Performed

- Read `.claude/rules/file-bridge-protocol.md`.
- Read `bridge/INDEX.md`.
- Read the full `playwright-screenshot-baselines` index entry and all
  referenced versions:
  `bridge/playwright-screenshot-baselines-001.md`,
  `bridge/playwright-screenshot-baselines-002.md`,
  `bridge/playwright-screenshot-baselines-003.md`,
  `bridge/playwright-screenshot-baselines-004.md`,
  `bridge/playwright-screenshot-baselines-005.md`,
  `bridge/playwright-screenshot-baselines-006.md`,
  `bridge/playwright-screenshot-baselines-007.md`,
  `bridge/playwright-screenshot-baselines-008.md`, and
  `bridge/playwright-screenshot-baselines-009.md`.
- Inspected `tests/accessibility/conftest.py`,
  `admin/standalone/mocks/plugin.ts`,
  `admin/standalone/mocks/store.ts`,
  `admin/standalone/mocks/fixtures/dashboard.ts`,
  `admin/standalone/mocks/fixtures/inbox.ts`,
  `admin/standalone/pages/Dashboard.tsx`,
  `admin/standalone/pages/Inbox.tsx`, and installed Recharts/react-smooth files
  under `admin/standalone/node_modules/`.
- Ran targeted searches with `rg` for the proposed v5 mechanics, mock-server
  paths, Recharts animation defaults, and react-smooth animation internals.
- Ran a Playwright runtime check confirming `page.clock.set_fixed_time(...)`
  fixes browser `Date.now()` while timers still fire.

No full visual test run was performed because the proposal has not been
implemented and the remaining failures are proposal-level determinism blockers.
