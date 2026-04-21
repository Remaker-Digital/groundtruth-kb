NO-GO

# WI-3167 Review: Playwright Screenshot Baselines v4

Reviewed: 2026-04-12

## Verdict

NO-GO. The v4 proposal fixes the Phase A trigger shape and avoids the existing
`tests/visual/` ownership collision, but the visual determinism contract is
still not sound enough to approve. The proposed clock call does not freeze
`Date` / `Date.now()` as claimed, and the Dashboard screenshot path still has
an animated chart with no settle or animation-disable strategy.

## Rationale

The remaining problems are not cosmetic. Screenshot baselines are only useful
if the captured frame represents a deterministic final UI state. v4 correctly
switches to a separate `tests/provider_visual/` package and keeps Phase A off
normal PR/push enforcement, but it relies on inaccurate Playwright clock
semantics and captures immediately after page guards. That leaves time-sensitive
and animation-sensitive pixels under-specified.

## Findings

### F1 - Blocker - `page.clock.install(time=...)` does not freeze time as claimed

**Claim:** v4 says `page.clock.install(time=...)` freezes JavaScript `Date`,
`Date.now()`, and timers to `2026-04-01T12:00:00Z`.

**Evidence:**

- `bridge/playwright-screenshot-baselines-007.md:17` claims
  `page.clock.install(time=...)` freezes Dashboard and Inbox time.
- `bridge/playwright-screenshot-baselines-007.md:41` through
  `bridge/playwright-screenshot-baselines-007.md:49` show the proposed freeze
  implementation using `page.clock.install(time=FROZEN_TIME)`.
- `bridge/playwright-screenshot-baselines-007.md:51` through
  `bridge/playwright-screenshot-baselines-007.md:54` depend on that call to
  prevent date drift.
- Local Playwright API inspection reported:
  `Clock.install: (self, *, time: float | str | datetime.datetime | None = None) -> None`
  and
  `Clock.set_fixed_time: (self, time: float | str | datetime.datetime) -> None`.
- Local Playwright API docs for `Clock.set_fixed_time` state that it makes
  `Date.now` and `new Date()` return fixed fake time while keeping timers
  running.
- Runtime check result:
  `install_delta_ms= 252` after a 250 ms wall-clock sleep, while
  `set_fixed_time_delta_ms= 0`.
- Runtime check result for `set_fixed_time`:
  `{'start': 1775044800000, 'end': 1775044800000, 'fired': True}` for a
  `setTimeout(..., 50)` promise, proving timers can still fire while `Date`
  remains fixed.
- The target pages still rely on current time:
  `admin/standalone/pages/Dashboard.tsx:217` through
  `admin/standalone/pages/Dashboard.tsx:222`,
  `admin/standalone/mocks/fixtures/dashboard.ts:11` through
  `admin/standalone/mocks/fixtures/dashboard.ts:17`, and
  `admin/standalone/pages/Inbox.tsx:94` through
  `admin/standalone/pages/Inbox.tsx:107`.

**Risk/impact:** The proposal's stated freeze guarantee is false. `install()`
sets an initial fake time, then time advances. That may be enough for some
day-level labels today, but it is not the deterministic clock contract the
proposal claims, and it leaves minute/second-sensitive UI vulnerable to
run-duration jitter.

**Required action:** Use `page.clock.set_fixed_time(FROZEN_TIME)` before
navigation when the goal is fixed `Date` / `Date.now()` with normal timer
behavior. If Prime intentionally wants full fake-timer control instead, the
proposal must define the explicit `install()` plus `run_for()` / `pause_at()`
sequence and verify the final captured UI state.

### F2 - Blocker - Dashboard chart animation is captured without a deterministic settle strategy

**Claim:** v4 captures screenshots after navigation and page guard checks.

**Evidence:**

- `bridge/playwright-screenshot-baselines-007.md:76` through
  `bridge/playwright-screenshot-baselines-007.md:83` list the test flow:
  create context, create page, install clock, navigate, assert guard, capture,
  update or compare. No animation-disable or settle step is specified.
- `admin/standalone/pages/Dashboard.tsx:325` through
  `admin/standalone/pages/Dashboard.tsx:379` render the Dashboard daily usage
  chart using Recharts `ResponsiveContainer`, `AreaChart`, and two `Area`
  components.
- `admin/standalone/package.json:28` declares `recharts`.
- Installed Recharts code shows `Area` animation is active in the browser by
  default: `admin/standalone/node_modules/recharts/lib/cartesian/Area.js:415`
  sets `isAnimationActive: !_Global.Global.isSsr`.
- Installed Recharts code shows the default animation lasts 1500 ms:
  `admin/standalone/node_modules/recharts/lib/cartesian/Area.js:416` through
  `admin/standalone/node_modules/recharts/lib/cartesian/Area.js:418`.
- Installed Recharts code renders an animated path when animation is active:
  `admin/standalone/node_modules/recharts/lib/cartesian/Area.js:316` through
  `admin/standalone/node_modules/recharts/lib/cartesian/Area.js:318`.
- Installed Recharts code passes that animation through `react-smooth`:
  `admin/standalone/node_modules/recharts/lib/cartesian/Area.js:242` through
  `admin/standalone/node_modules/recharts/lib/cartesian/Area.js:246`.
- Targeted search found `requestAnimationFrame` usage in
  `admin/standalone/node_modules/react-smooth/src/configUpdate.js` and
  `admin/standalone/node_modules/react-smooth/src/setRafTimeout.js`.

**Risk/impact:** A custom `page.screenshot()` immediately after the heading
guard can capture an arbitrary Recharts animation frame. Baseline generation
and later comparison can differ based on CI timing, and the committed baseline
may represent a partially drawn chart rather than the final Dashboard UI.

**Required action:** Add an explicit animation strategy before capture. Acceptable
directions include disabling Recharts animation for visual-test mode, waiting
for a verified final chart state, or using fake-timer control to advance past
the 1500 ms animation before the screenshot. The proposal should include command
evidence that Dashboard captures are stable under the chosen strategy.

### F3 - Major - Phase A is manual-only, but still defaults to non-update comparison mode

**Claim:** v4 says Phase A is generator-only and baselines do not exist yet.

**Evidence:**

- `bridge/playwright-screenshot-baselines-007.md:25` and
  `bridge/playwright-screenshot-baselines-007.md:26` say Phase A is
  generator-only and has no baselines.
- `bridge/playwright-screenshot-baselines-007.md:90` through
  `bridge/playwright-screenshot-baselines-007.md:95` define a
  `workflow_dispatch` input named `update` with `default: false`.
- `bridge/playwright-screenshot-baselines-007.md:127` through
  `bridge/playwright-screenshot-baselines-007.md:134` run the visual tests with
  `AR_UPDATE_SCREENSHOTS` derived from that input.
- Earlier proposal versions establish that missing baselines are a hard
  comparison failure when not in update mode, and v4 still says baselines do not
  exist in Phase A.

**Risk/impact:** A default manual Phase A run is not a generator run; it is a
comparison run against absent baselines. This is not as severe as PR/push
enforcement, but it makes the intended Phase A path easy to run red by default.

**Required action:** Make Phase A mechanically generator-only. Either remove the
input and force `AR_UPDATE_SCREENSHOTS=1`, default `update` to true during
Phase A, or add an early guard that refuses non-update Phase A runs with a clear
message before pytest starts.

## Conditions for GO

1. Replace `page.clock.install(time=FROZEN_TIME)` with a clock strategy that
   truly fixes `Date` / `Date.now()` while preserving or explicitly controlling
   timers.
2. Add a deterministic animation-settle or animation-disable strategy for the
   Dashboard Recharts chart before screenshot capture.
3. Make the Phase A workflow default behavior match the generator-only claim.
4. Keep the v4 improvements: `tests/provider_visual/` remains separate from
   existing `tests/visual/`, Phase A remains off PR/push enforcement, and Phase
   B enables PR/push only after all 10 Ubuntu/Chromium baselines are committed.

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
  `bridge/playwright-screenshot-baselines-006.md`, and
  `bridge/playwright-screenshot-baselines-007.md`.
- Inspected `requirements.txt`, `requirements-test.txt`, `pyproject.toml`,
  `.github/workflows/accessibility.yml`, `tests/accessibility/conftest.py`,
  `tests/visual/`, `admin/standalone/package.json`,
  `admin/standalone/pages/Dashboard.tsx`,
  `admin/standalone/pages/Inbox.tsx`,
  `admin/standalone/mocks/fixtures/dashboard.ts`,
  `admin/standalone/mocks/fixtures/inbox.ts`, and installed Recharts /
  react-smooth files under `admin/standalone/node_modules/`.
- Ran targeted API checks for Playwright clock signatures and docs.
- Ran a headless Chromium runtime check comparing `page.clock.install()` with
  `page.clock.set_fixed_time()`.

No full visual test run was performed because the proposal has not been
implemented and the remaining issues are design/API determinism blockers.
