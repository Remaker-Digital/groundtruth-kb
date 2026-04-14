# Active Work List

**Owner pre-approval:** Proceed through this list autonomously. For each item:
propose via bridge → wait for Codex GO → implement → post-impl report → wait for Codex VERIFIED → commit → drop from list.

Do not wait for owner approval between items. Continue unsupervised.

## Items

### GT-KB Spec Pipeline (DOC-GTKB-SPEC-PIPELINE)

**Phase 1-3 COMPLETE + VERIFIED (S287, S288).**

Implementation status as of end of S288:
- [x] F1: Spec Schema Enrichment — committed 1e1e965, VERIFIED (S287)
- [x] F3 + F4-A: Spec Quality Gate + Constraint Lookup — committed a21fa19 (S287)
- [x] F2-A: Change Impact Analysis Phase A — committed 35514fe + 85440db + 77c0310, VERIFIED (S288)
- [x] F4-B + F2-B: Constraint Writes + Dependents Traversal — committed 7d166e4, VERIFIED (S288)
- [x] F7: Session Health Dashboard — committed 61b278a, VERIFIED (S288)
- [x] F5: Requirement Intake Pipeline — committed 63ea9c2, VERIFIED (S288)
- [x] Phase 3 NO-GO fixes (snapshot ordering, trends deltas, reject discriminator) — committed b2d425c, VERIFIED (S288)

### Phase 4 — COMPLETE + VERIFIED (S289) ✓

All GT-KB Spec Pipeline phases are now implemented, verified, and on main.

## Owner Actions Pending

- [x] Create Chromatic project at chromatic.com + set CHROMATIC_PROJECT_TOKEN GitHub secret (WI-3165) — DONE S285

## Completed (S289)

- [x] **GT-KB Phase 4: F6 Spec Scaffold + F8 Provenance Reconciliation + assertions depth guard** — committed `87e7bd7` on `groundtruth-kb` main, VERIFIED at `bridge/gtkb-phase4-implementation-012.md`
  - F6: new `spec_scaffold.py` (scaffold_specs, SpecScaffoldConfig, ScaffoldReport); `ScaffoldOptions.spec_scaffold` optional integration into `scaffold_project()`; `gt scaffold specs` CLI; 10 tests
  - F8: new `reconciliation.py` (ReconciliationReport + 5 detectors: orphaned_assertions, stale_specs, authority_conflicts, duplicate_specs, expired_provisionals); `gt kb reconcile` CLI with per-detector flags + `--all`; 28 tests (27 detector + 1 CLI smoke)
  - Shared: `_extract_assertion_targets()` gained `depth: int = 0` kwarg with `_MAX_COMPOSITION_DEPTH` guard; 1 regression test in `test_impact.py`
  - Totals: 561 → 600 tests pass, ruff clean, docs CLI coverage clean
  - Review cycle: 5 Prime revisions (v1-v5), 4 Codex NO-GOs, GO at -010, NEW post-impl at -011, VERIFIED at -012
  - Phase 4 completes the entire 8-feature GT-KB Spec Pipeline (F1-F8) started in S286 — the spec pipeline is now fully functional
- [x] **INDEX.md retirement patch (S289 mid-session)** — retired 9 stale/subsumed GT-KB spec-pipeline entries (gtkb-f1f8-cross-check, gtkb-spec-pipeline-f1..f8) from `bridge/INDEX.md` to stop the Prime Builder OS poller from re-firing headless `claude.exe` every 3 minutes on already-completed GO entries. Bridge files remain on disk.
- [x] **Poller autonomy memory** — saved `feedback_poller_autonomy.md` capturing owner directive: "If the poller is working, leave it alone" — mitigate race concerns with fast writes, not shutdown.

## Completed (S285)

- [x] WI-3168 — Migrate knowledge.db to groundtruth.db at repo root (8b9a1def, 11 Codex review rounds, VERIFIED -026)
- [x] WI-3142 — Credential scan narrowing — KB resolved (committed S281)
- [x] WI-3165 — Chromatic CI activation — KB resolved, CI green, 14 snapshots (committed S281 + cb3f2af5)
- [x] WI-3166 — Axe-core CI — KB resolved (committed S282)
- [x] WI-3167 — Playwright baselines — KB resolved (committed S282)
- [x] WI-3169 — Wiki path audit, 6 pages updated (wiki ce2cde8)
- [x] WI-3170 — Transport governance import fix (ae6a6f02)

## Completed (S284)

- [x] GT-kb docs completion — ALL PHASES COMPLETE, Codex VERIFIED (016), committed (0fe21c9), tagged v0.3.0

## Completed (S283)

- [x] Deliberation Archive C3 — Session-wrap harvest script (705 deliberations, 55 bridge threads created)
- [x] Deliberation Archive C4 — Health metrics script + /check-deliberations skill (5 metrics, PASS/WARN/FAIL)
- [x] Deliberation Archive C5 — WI-3159 collision repair + WI-3169 + DOC-DELIB-COMPLETION
- [x] NO-GO fix: test_deliberation_search.py (16 tests, 10/10 known-answer, 100% top-3)
- [x] NO-GO fix: GT-kb v0.2.1 text_match contract test (69/69 pass)
- [x] Requirements updated to GT-kb v0.2.1
