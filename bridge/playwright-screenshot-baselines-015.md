# Post-Implementation Report: WI-3167 Playwright Screenshot Baselines

## Summary

Implemented per approved v7 proposal. Phase A: generator-only workflow + test
code + 10 baseline PNGs committed. All tests pass in both update and comparison
modes.

## Test Results

- Update mode: `10 skipped in 41.16s` (baselines generated)
- Comparison mode: `10 passed in 43.08s` (0% diff on all pages)
- Stability proof: Dashboard desktop 0/1,024,000 pixels differ across 2 captures

## Files Created

| File | Purpose |
|------|---------|
| `tests/e2e/screenshot_compare.py` | Pillow-only pixel comparison (no numpy) |
| `tests/e2e/screenshots/*.png` | 10 baseline PNGs (5 pages × 2 viewports) |
| `tests/e2e/screenshots/.gitkeep` | Directory marker |
| `tests/provider_visual/__init__.py` | Package marker |
| `tests/provider_visual/conftest.py` | Mock server + navigation fixtures |
| `tests/provider_visual/test_screenshots.py` | 10 parametrized tests |
| `.github/workflows/visual-regression.yml` | Phase A: workflow_dispatch-only, AR_UPDATE_SCREENSHOTS=1 |

## Files Modified

| File | Change |
|------|--------|
| `admin/standalone/mocks/fixtures/dashboard.ts:11` | `new Date()` → `new Date("2026-03-10T12:00:00Z")` for deterministic mock data |

## Verification

- `ruff check` — all pass
- `ruff format --check` — all formatted
- Tests pass in both modes (update + comparison)
- Dashboard stability: 0 pixel difference across captures
- Clock: `page.clock.set_fixed_time("2026-03-10T12:00:00Z")` (not `install()`)
- Date alignment: server fixture range (Feb 9 → Mar 10) = browser chart range
- Animation settle: 2500ms wait (> Recharts 1500ms default)

## Phase B Note

Phase B (PR/push enforcement) requires updating the workflow to add
pull_request/push triggers with full path filters. This is a follow-up
commit after baselines are confirmed stable on CI.

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
