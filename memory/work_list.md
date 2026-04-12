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
- [x] UI-EVAL — Evaluate visual/UX testing tools (S281, complete)
- [x] UI-SPEC — Specs created: SPEC-2102 (Chromatic CI), SPEC-2103 (axe-core CI), SPEC-2104 (visual baselines)
- [ ] WI-3165 — Activate Chromatic visual regression CI (SPEC-2102, P2)
  - Status: specified, ready to implement
  - Scope: GitHub Actions workflow + CHROMATIC_PROJECT_TOKEN + baseline capture
  - Next: propose via bridge → implement
- [ ] WI-3166 — Add axe-core WCAG 2.1 AA to CI (SPEC-2103, P2)
  - Status: specified, ready to implement
  - Scope: Include test_accessibility.py in CI or create lighter integration
  - Next: after WI-3165
- [ ] WI-3167 — Playwright screenshot baselines (SPEC-2104, P3)
  - Status: specified, ready to implement
  - Scope: toHaveScreenshot() for top 5 Provider Console pages
  - Next: after WI-3166

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
