# Active Work List

**Owner pre-approval:** Proceed through this list autonomously. For each item:
propose via bridge → wait for Codex GO → implement → post-impl report → wait for Codex VERIFIED → commit → drop from list.

Do not wait for owner approval between items. Continue unsupervised.

## Items

- [ ] WI-3142 — Narrow conftest.py exclusion in credential-scan
  - Status: IMPLEMENTED. Post-impl report submitted (bridge/credential-scan-narrowing-013.md), awaiting Codex VERIFIED
  - Changes: credential-scan.py rewritten, 24/24 tests pass, eval/archive/deploy files remediated
  - Next: wait for Codex VERIFIED, then commit
- [ ] WI-3162 — Backfill existing LO reports into deliberation archive
  - Status: REVISED v013 submitted, awaiting Codex review
  - v013 fixes: multi-signal section extraction (mixed GO/NO-GO → informational + warning), narrowed unparsed-signal scan to structured locations only
  - Next: wait for Codex review of v013
- [ ] UI-EVAL — Evaluate visual/UX testing tools for Agent Red pipeline
  - Goal: Add UI testing tools that improve appearance, usability, consistency with minimal owner work
  - Scope: Research Applitools vs Percy vs Chromatic pricing/fit for our TypeScript + Playwright stack
  - Next: tool evaluation research
- [ ] UI-SPEC — Create specifications for UI quality testing track (GOV-01)
  - Depends on: UI-EVAL (tool selection informs spec scope)
  - Scope: Spec the testing layers (Playwright workflows, axe-core a11y, visual regression, AI UX critique)
  - Next: after UI-EVAL
- [ ] UI-PILOT — Implement Playwright + axe-core for top user journeys
  - Depends on: UI-SPEC (specs before code, GOV-01)
  - Scope: Add axe-core to existing Playwright suite, cover top 5 user journeys
  - Next: after UI-SPEC

## Completed (S280)

- [x] WI-0929 — wont_fix (pre-existing)
- [x] WI-0970 — wont_fix (pre-existing)
- [x] WI-0971 — wont_fix (pre-existing)
- [x] WI-0972 — wont_fix (pre-existing)
- [x] WI-0973 — wont_fix (pre-existing)
- [x] WI-0974 — wont_fix (pre-existing)
- [x] WI-3141 — Resolved: already fixed (shell=True probe + _skip_no_az)
- [x] WI-3160 — Resolved: SPEC-2101 pipeline dashboard (commit 5a38838)
- [x] WI-3163 — Resolved: 52 deliberation tests (commit c72cb25)
- [x] WI-3164 — Resolved: ruff lint/format both clean after S280 work
