# Active Work List

**Owner pre-approval:** Proceed through this list autonomously. For each item:
propose via bridge → wait for Codex GO → implement → post-impl report → wait for Codex VERIFIED → commit → drop from list.

Do not wait for owner approval between items. Continue unsupervised.

## Items

- [x] WI-3166 — axe-core WCAG 2.1 AA CI enforcement (commit cff9f102, 9 tests, 7 review rounds)
- [ ] WI-3167 — Add Playwright screenshot baselines for top 5 Provider Console journeys (SPEC-2104, P3)
  - Status: specified, ready to propose
  - Scope: toHaveScreenshot() for Dashboard, Configuration, Inbox, Widget, Team
  - Next: after WI-3166

## Owner Actions Pending

- [ ] Create Chromatic project at chromatic.com + set CHROMATIC_PROJECT_TOKEN GitHub secret (WI-3165)

## Completed (S281)

- [x] WI-3142 — credential-scan narrowing (commit 1e3107ea, 33 tests, 9 proposal + 3 verification rounds)
- [x] WI-3162 — LO report backfill (commit fb0e5d7e, 53 tests, 9 proposal + 4 verification rounds)
- [x] WI-3165 — Chromatic CI activation (commit 1979d06a, 2 proposal + 2 verification rounds)
- [x] UI-EVAL — Tool research complete (Chromatic already installed)
- [x] UI-SPEC — 3 specs (SPEC-2102/2103/2104) + 3 WIs (WI-3165/3166/3167)

## Completed (S280)

- [x] WI-0929..0974 — wont_fix (pre-existing)
- [x] WI-3141 — already fixed
- [x] WI-3160 — pipeline dashboard
- [x] WI-3163 — deliberation tests
- [x] WI-3164 — ruff lint/format
