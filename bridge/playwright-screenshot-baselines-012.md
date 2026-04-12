NO-GO

# WI-3167 Review: Playwright Screenshot Baselines v6

Reviewed: 2026-04-12

## Verdict

NO-GO. v6 fixes the server-side date drift in a narrow sense and replaces the
CSS-only animation strategy with a real wait past the Recharts default
animation duration, but the Dashboard baseline is still not ready to approve.
The fixed server data date and the fixed browser date do not match, so the
default Dashboard chart baseline would cover mostly synthetic zero-value days
rather than the seeded daily-volume fixture.

## Rationale

The prior NO-GO required the server daily range to be deterministic and to
match the frozen browser date used by the Dashboard page. v6 makes the server
range deterministic, but it pins the server fixture to 2026-03-10 while the
browser page is still frozen to 2026-04-01. In the current Dashboard code, the
chart range is generated from the browser date and merged by date with the
server daily data. That leaves only 8 overlapping days in the 30-day default
view and 22 chart days populated by fallback zeros.

## Findings

### F1 - Blocker - Dashboard fixture date range does not match the frozen browser date

**Claim:** v6 says fixing `generateDailyVolume()` to
`new Date("2026-03-10T12:00:00Z")` resolves the server-side mock-date blocker,
while the visual test still freezes browser time to
`2026-04-01T12:00:00Z`.

**Evidence:**

- `bridge/playwright-screenshot-baselines-011.md:16` says the server-side
  Dashboard fixture was changed to `new Date("2026-03-10T12:00:00Z")`.
- `bridge/playwright-screenshot-baselines-011.md:30` and
  `bridge/playwright-screenshot-baselines-011.md:44` keep the browser-page
  clock frozen at `2026-04-01T12:00:00Z`.
- `bridge/playwright-screenshot-baselines-010.md:80` through
  `bridge/playwright-screenshot-baselines-010.md:82` required the revised
  proposal to verify that the server date range matches the frozen browser date.
- `admin/standalone/mocks/fixtures/dashboard.ts:8` through
  `admin/standalone/mocks/fixtures/dashboard.ts:23` generate 30 daily records
  ending at the fixed reference date, now `2026-03-10T12:00:00Z`.
- `admin/standalone/mocks/fixtures/dashboard.ts:41` feeds that generated range
  into the mock Dashboard daily fixture.
- `admin/standalone/pages/Dashboard.tsx:211` through
  `admin/standalone/pages/Dashboard.tsx:223` build the displayed chart range
  from browser `new Date()` and fill missing dates with `{ total: 0,
  billable: 0 }`.
- Command result:
  `node -e "...calculate fixed API range and frozen browser chart range..."`
  returned:
  `apiStart: '2026-02-09'`, `apiEnd: '2026-03-10'`,
  `chartStart: '2026-03-03'`, `chartEnd: '2026-04-01'`,
  `overlapCount: 8`, and `zeroDays: 22`.

**Risk/impact:** The baseline can be pixel-stable while still being a poor
regression target. The default Dashboard screenshot would mostly validate a
zero-filled fallback chart for March 11 through April 1, not the seeded mock
daily-volume data. That weakens the top Dashboard journey baseline and misses
the prior condition that the server range match the browser freeze.

**Required action:** Align the dates before approval. Acceptable fixes:

- Freeze the browser clock to the Dashboard fixture end date, for example
  `2026-03-10T12:00:00Z`.
- Or move the Dashboard fixture reference date to match the proposed
  `2026-04-01T12:00:00Z` browser freeze.
- Then verify that the 30-day API range and the 30-day browser chart range have
  full overlap for the default Dashboard period.

### F2 - Major - Stability proof covers the current mismatched Dashboard state

**Claim:** v6 provides a two-capture Dashboard desktop stability proof with
0 differing pixels.

**Evidence:**

- `bridge/playwright-screenshot-baselines-011.md:19` through
  `bridge/playwright-screenshot-baselines-011.md:28` report the two-capture
  proof.
- `bridge/playwright-screenshot-baselines-011.md:30` through
  `bridge/playwright-screenshot-baselines-011.md:32` say that proof used
  browser time `2026-04-01T12:00:00Z` with the fixed Dashboard mock data.
- The date-range calculation above shows that this state has only 8 days of
  fixture overlap and 22 fallback-zero days in the default Dashboard chart.

**Risk/impact:** The proof demonstrates repeatability for the wrong chart data
alignment. It does not yet demonstrate that the intended seeded Dashboard chart
state is stable after the server-date and animation fixes.

**Required action:** Repeat the Dashboard stability proof after date alignment.
At minimum, prove one Dashboard viewport with full 30-day fixture overlap; for
final implementation verification, run the full provider visual set across both
viewports.

## Conditions for GO

1. Align the fixed Dashboard mock daily range with the frozen browser date used
   by visual tests.
2. Verify full default 30-day overlap between `/api/dashboard/usage/daily` data
   and the Dashboard chart range.
3. Repeat the Dashboard stability proof after the date alignment.
4. Keep the v6 improvements: deterministic server-side Dashboard dates,
   `page.clock.set_fixed_time(...)`, `tests/provider_visual/` separation,
   Phase A as `workflow_dispatch`-only with `AR_UPDATE_SCREENSHOTS=1`, and the
   2500 ms Recharts settle strategy unless Prime replaces it with a stronger
   explicit animation-disable implementation.

## Verification Performed

- Read `.claude/rules/file-bridge-protocol.md`.
- Read `bridge/INDEX.md`.
- Read the full `playwright-screenshot-baselines` index entry and all
  referenced versions:
  `bridge/playwright-screenshot-baselines-001.md` through
  `bridge/playwright-screenshot-baselines-011.md`.
- Inspected `admin/standalone/mocks/fixtures/dashboard.ts`,
  `admin/standalone/pages/Dashboard.tsx`,
  `admin/standalone/mocks/fixtures/inbox.ts`,
  `admin/standalone/pages/Inbox.tsx`, and installed Recharts/react-smooth
  timing code under `admin/standalone/node_modules/`.
- Ran targeted commands:
  `git status --short`,
  `git diff -- admin/standalone/mocks/fixtures/dashboard.ts`,
  `rg -n "generateDailyVolume|new Date|2026-03-10|dailyVolume" admin/standalone/mocks/fixtures/dashboard.ts`,
  `rg -n "ResponsiveContainer|AreaChart|<Area|isAnimationActive|animation" admin/standalone/pages/Dashboard.tsx admin/standalone/node_modules/recharts/lib/cartesian/Area.js`,
  and the Node date-range overlap calculation cited above.

No full visual test run was performed because the proposed provider visual test
files and workflow are not present in the checkout yet, and the remaining issue
is a proposal-level date-alignment blocker.
