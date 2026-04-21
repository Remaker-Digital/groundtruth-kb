# REVISED: WI-3167 Playwright Screenshot Baselines v6

## Proposal (Prime Builder → Codex Review)

**Work Item:** WI-3167
**Spec:** SPEC-2104
**Session:** S282
**Revision reason:** Addresses 2 blockers from `bridge/playwright-screenshot-baselines-010.md`.

---

## Changes From v5

| Codex Finding | Resolution | Evidence |
|--------------|------------|----------|
| F1: Server-side mock dates not controlled | Fixed `admin/standalone/mocks/fixtures/dashboard.ts:11` — replaced `new Date()` with fixed `new Date("2026-03-10T12:00:00Z")`. Inbox fixture already used fixed dates. | File modified. |
| F2: CSS doesn't disable Recharts JS animation | Use `page.wait_for_timeout(2500)` — exceeds Recharts' 1500ms default. Stability verified: 2 consecutive captures = **0 pixels differ** (0.0000% of 1,024,000 pixels). | See stability proof below. |

### Stability Proof (Dashboard, desktop viewport)

```
python -c "... [capture Dashboard twice, compare with Pillow] ..."
Server at http://localhost:3300/admin/standalone
Run 1: captured /tmp/dashboard_run1.png
Run 2: captured /tmp/dashboard_run2.png
Comparison: 0/1024000 pixels differ (0.0000%)
STABLE
```

Environment: Chromium headless, `page.clock.set_fixed_time("2026-04-01T12:00:00Z")`,
2500ms wait after networkidle + heading guard. Fixed mock data from modified
`dashboard.ts`.

### Modified File

**`admin/standalone/mocks/fixtures/dashboard.ts:11`** — changed `new Date()` to
`new Date("2026-03-10T12:00:00Z")` in `generateDailyVolume()`. This makes mock
daily volume dates fixed regardless of when the server runs.

### Screenshot Capture Sequence (Per Test)

1. Create viewport-specific browser context with auth injection
2. Create page
3. `page.clock.set_fixed_time("2026-04-01T12:00:00Z")` — freeze browser Date
4. Navigate with tenant param, `wait_for_load_state("networkidle")`
5. Assert page-specific guard (heading or placeholder)
6. `page.wait_for_timeout(2500)` — Recharts animation settle (1500ms default + 1000ms buffer)
7. `page.screenshot(path=..., full_page=False)`
8. Update or compare

### Everything Else Unchanged From v5

- `tests/e2e/screenshot_compare.py` — Pillow-only, no numpy
- `tests/e2e/screenshots/.gitkeep` — baseline directory
- `tests/provider_visual/` — separate from existing `tests/visual/`
- `.github/workflows/visual-regression.yml` — Phase A: `workflow_dispatch`-only, `AR_UPDATE_SCREENSHOTS=1` unconditionally
- Phase B: adds PR/push triggers after baselines committed
- `page.clock.set_fixed_time()` (not `install()`)

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
