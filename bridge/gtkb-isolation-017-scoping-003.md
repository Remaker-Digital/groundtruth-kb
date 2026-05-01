REVISED

# GTKB-ISOLATION-017 Scoping Bridge (Revision 1)

**Status:** REVISED (scoping; awaits Codex GO)
**Date:** 2026-05-01 (S325)
**Author:** Prime Builder (Claude Opus 4.7)
**Supersedes:** `bridge/gtkb-isolation-017-scoping-001.md` (NO-GO at `-002`)
**Addresses:** Codex `-002` findings F1 (5 of 7 Phase 9 decisions dropped) and F2 (deliverables and exit criteria not mapped to slices).

---

## NO-GO Acknowledgement

Codex `-002` identified two blocking scope-mapping defects in `-001`. Both accepted in full.

### F1 (P1) - Phase 9 owner decisions partially dropped

**Acknowledged.** The `-001` proposal claimed only mandatory-vs-opt-in (decision 1) and Agent Red example (decision 6) were owner-decision items. The Phase 9 plan §"Open Decisions For The Implementation Bridge" lines 369-396 enumerates **seven** decisions. The five I dropped: release version (2), backward-compatibility policy (3), publicity/transition channels (4), post-Phase-9 acceptance gate (5), Phase 8 rehearsal-evidence integration (7). Fix: full Decision Map below assigning each to an owning slice with blocking point, expected owner input shape, and implementation consequence.

### F2 (P1) - Deliverables and exit criteria not mapped to slices

**Acknowledged.** The Phase 9 plan §"Deliverables From The Implementation Bridge" (lines 415-430) and §"Exit Criteria" §4 (Service/Overlay, lines 341-352) and §"Regression Visibility" (lines 398-413) name several artifacts and acceptance gates I did not assign to slices. Specifically: adopter README quickstart block scaffolded into init, release notes, release-version gating, Phase 4 service endpoints in scaffolded `groundtruth.toml` + scaffolded test, Phase 6 overlay refresh/stale tests, example dashboard rendering verification, service-down / overlay fallback documentation, AST gate CI wiring, registry-drift detection in CI. Fix: expanded slice acceptance criteria below + added Slice 8 (release ops + program closeout).

## Specification Links

All Specification Links from `-001` carry forward unchanged. Re-cited briefly here for compliance-gate verification.

- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (upstream commit `affa5a05`)
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md` — full Phase 9 plan (the deliverables, exit criteria, decisions, regression-visibility list are all carried forward into the slice plan in this revision)
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-001-PHASE1-AUTHORITY-MATRIX-PLAN-2026-04-22.md`
- `.claude/rules/project-root-boundary.md`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `bridge/gtkb-isolation-016-phase8-wave3-execution-012.md` (VERIFIED) — Phase 8 closure including the freeze-window runbook that decision 7 (Phase 8 rehearsal-evidence integration) maps to
- `groundtruth-kb/src/groundtruth_kb/project/{doctor.py, upgrade.py, scaffold.py, managed_registry.py, preflight.py, ownership.py, profiles.py, rollback.py, manifest.py}` — existing in-root surfaces extended by slices
- `GOV-09`, `GOV-20`

## Decision Map (per F1 fix)

The Phase 9 plan §"Open Decisions" enumerates 7 decisions. Each owned by a slice. Each row describes blocking point (when in the slice the decision must resolve), expected owner input shape, and implementation consequence.

| # | Decision | Owning slice | Blocking point | Expected owner input | Implementation consequence |
|---|---|---|---|---|---|
| 1 | Mandatory vs opt-in isolation for existing adopters | Slice 4 (`gt project upgrade`) | Slice 4 implementation bridge §"Decision Needed From Owner" | One of {`mandatory_at_upgrade`, `opt_in_with_deprecation_window`, `version_gated`} | Mandatory: upgrade refuses pre-isolation roots without `--accept-migration`. Opt-in: upgrade emits warning, defers migration. Version-gated: upgrade requires `--target-version >= X.Y.Z` |
| 2 | GT-KB release version that ships adopter tooling | Slice 8 (release ops) | Slice 8 implementation bridge §"Decision Needed From Owner" | One of {`next_minor`, `dedicated_release`, `tagged_with_migration_guide`} or explicit version (e.g., `0.7.0`) | Release notes header version; CHANGELOG section; release-readiness gate version-pin |
| 3 | Backward-compatibility policy | Slice 4 (sequenced after decision 1) | Same Slice 4 bridge as decision 1 (paired) | One of {`deprecation_warning_N_releases` + N value, `one_shot_migration_at_upgrade`, `version_gating`} | Doctor warning text; upgrade-flow branching; release-notes migration-guide structure |
| 4 | Publicity and transition channels | Slice 8 (release ops) | Slice 8 bridge §"Decision Needed From Owner" | Pick subset from {release_notes, standalone_announcement, docs_chapter, example_repos, blog_post, customer_email}; pick scheduling (together vs staggered) | Slice 8 deliverable scope: which artifacts ship; slice 8 acceptance: which gates each artifact passes |
| 5 | Post-Phase-9 acceptance gate | Slice 8 closeout (program-level) | Slice 8 post-implementation report §"Acceptance Criteria" | One of {`adopter_fixture_count >= N`, `doctor_pass_rate_on_sampled_adopters >= P%`, `release_readiness_field`, custom criterion} | What evidence declares ISOLATION-017 program complete and unblocks ISOLATION-018 |
| 6 | Agent Red as Phase 9 example | Slice 7 (examples) | Slice 7 bridge §"Decision Needed From Owner" | Y/N + (if Y) "minimized fixture only — no production paths/secrets" affirmation | Slice 7 produces a 4th or 5th example tree under `examples/agent-red-minimized-fixture/` |
| 7 | Phase 8 rehearsal-evidence integration into upgrade | Slice 4 (paired with decisions 1+3) | Same Slice 4 bridge | One of {`rehearsal_evidence_required_input`, `out_of_band_recipe_only`, `optional_attachment`} | Slice 4 upgrade flow: invokes `scripts/rehearse_isolation.py` automatically, or expects pre-run evidence files, or treats rehearsal as documentation only |

Decisions 1, 3, 7 cluster on Slice 4 (upgrade flow); 2, 4 on Slice 8 (release); 5 on Slice 8 closeout; 6 on Slice 7. **No decision is needed at this scoping-bridge GO time;** each will surface in its owning slice's bridge.

If the owner pre-decides any of these now, the corresponding slice bridge cites the decision DELIB; otherwise the slice bridge surfaces it via AskUserQuestion at filing time.

## Existing Surfaces vs Phase 9 Required Coverage (carried forward from -001)

[Section unchanged from `-001`. Survey of `groundtruth-kb/src/groundtruth_kb/project/{doctor.py,upgrade.py,scaffold.py,managed_registry.py,preflight.py,ownership.py,profiles.py,rollback.py,manifest.py}` confirms all in-root surfaces exist; isolation-specific gap is what this scoping addresses.]

## Revised Slice Plan (per F2 fix)

8 slices. Slices 1-7 expanded with previously-missed deliverables; Slice 8 added for release ops + program closeout. Each slice ships as its own implementation bridge.

### Slice 1 — Isolation doctor checks

**Scope (unchanged from `-001`):** extend `groundtruth-kb/src/groundtruth_kb/project/doctor.py` with the 9 isolation checks from Phase 9 §4. Severity model. Tests under `groundtruth-kb/tests/test_doctor_isolation.py`.

**Acceptance (expanded):**
- 9 new `_check_isolation_*` functions per Phase 9 spec.
- Severity enum with `error` / `warning` / `info` levels.
- Tests assert each check fires correctly on a fixture violation and stays silent on a clean fixture.
- **Doctor output is deterministic** (per Phase 9 §"Regression Visibility": "non-deterministic doctor check is a defect, not a feature"). Test asserts repeated runs on identical input produce identical output.
- IPR + CVR documents per GOV-20.

**Estimated envelope:** ~400 LOC source + ~350 LOC tests.

### Slice 2 — Managed artifact registry isolation labels + AST gate CI wiring

**Scope (expanded):** extend `managed_registry.py` and `ownership.py` with `owner` / `upgrade` / `denied` policies per Phase 1 authority matrix. Add AST gate that asserts every adopter-scaffolded file has a registry entry. **Wire AST gate into CI** (per Phase 9 §"Regression Visibility": "AST gate ... must run in CI and fail on unregistered files or unmatched globs").

**Acceptance (expanded):**
- Registry schema updated with `owner` and `upgrade_policy` fields.
- Per-entry rationale captured.
- AST gate test asserting registry coverage of scaffolded files.
- **AST gate wired into `groundtruth-kb` CI** (existing pyproject.toml / tox / Makefile path; lane fails CI on unregistered file).
- Migration-note discipline (no owner-flip without note).
- **Registry-drift detection in CI** (per Phase 9 §"Regression Visibility": "Registry drift must be detectable").
- Tests, IPR, CVR.

**Estimated envelope:** ~250 LOC source + ~200 LOC tests + ~30 LOC CI config.

### Slice 3 — `gt project init` adopter-subject defaults + scaffold deliverables

**Scope (expanded):** extend `scaffold.py` and `profiles.py` so `gt project init` defaults `work subject = application`, refuses to land outside `<gt-kb-root>/applications/<name>/`, and refuses to overwrite existing-adopter state. **Scaffold all artifacts enumerated in Phase 9 §1**, including:
- `groundtruth.toml` with **Phase 4 service-endpoint template** populated.
- `groundtruth.db` initialized empty with app-scope tables only.
- `bridge/INDEX.md` empty + bridge-essential rule header in scaffolded README.
- `memory/work_list.md` placeholder + comments.
- `memory/release-readiness.md` with application-subject header banner.
- `.claude/rules/`, `.claude/hooks/`, `.claude/settings.json` wrappers (no embedded policy).
- `.codex/hooks.json` forward-compat intent.
- `.groundtruth/formal-artifact-approvals/.gitkeep`.
- Segregated `.gitignore` (product-maintained block + adopter-owned block).
- **Adopter-facing README quickstart block** baked into `gt project init` output (per Phase 9 §6 lines 261-262 + Deliverables line 425-426 + F2).

**Acceptance (expanded):**
- Init refuses outside-root paths.
- Init refuses on existing-adopter idempotency check; recommends `gt project upgrade`.
- Scaffolded tree matches Phase 9 §1 enumeration **including service endpoint and README quickstart block**.
- Tests verify byte-level conformance against a golden fixture.
- **Phase 4 service endpoints scaffolded in `groundtruth.toml` are documented in the scaffolded adopter README** (per Phase 9 Exit Criterion 4 line 343-345).
- IPR, CVR.

**Estimated envelope:** ~350 LOC source + ~450 LOC tests + golden fixture + scaffolded README template.

### Slice 4 — `gt project upgrade` isolation steps + Phase 8 migration kit invocation

**Scope (unchanged structurally; resolves decisions 1, 3, 7):** extend `upgrade.py` with isolation-specific upgrade steps; integrate Phase 8 rehearsal driver per decision 7.

**Acceptance (expanded):**
- Upgrade detects mixed-root state via doctor checks (Slice 1 dependency).
- Upgrade behavior under decision 1: implements selected mode (mandatory/opt-in/version-gated).
- Upgrade behavior under decision 3: emits selected warning policy (deprecation window of N releases, or one-shot, or version-gated).
- Upgrade behavior under decision 7: invokes `scripts/rehearse_isolation.py` per selected integration mode (required input / out-of-band / optional).
- Upgrade preserves adopter-owned files; refuses silent overwrite.
- Rollback restores pre-upgrade state via receipts.
- Receipts capture migration evidence per `docs/reference/upgrade-receipts.md` conventions.
- Tests, IPR, CVR.

**Estimated envelope:** ~450 LOC source + ~550 LOC tests.

### Slice 5 — Clean-adopter test suite + CI wiring + overlay tests

**Scope (expanded):** new `groundtruth-kb/tests/adopter/` with the 10 test files from Phase 9 §5 + **3 existing-adopter migration fixtures** + **golden fixture diff** + **Phase 6 overlay refresh/stale tests** (per Phase 9 Exit Criterion 4 line 346-348). **Wire test suite into `groundtruth-kb` CI** (per Phase 9 §"Regression Visibility": "CI must run the clean-adopter test suite on every GT-KB commit").

**Acceptance (expanded):**
- 10 test files implementing Phase 9 §5 assertions.
- Each test in isolated temp directory; no cross-test state.
- 3 existing-adopter migration fixtures.
- All assertions outside-in (GOV-19) and meaningful (GOV-18).
- Golden-fixture diff per GT-KB version.
- **Phase 6 overlay refresh test:** overlays refresh on demand on clean adopter.
- **Phase 6 overlay stale-detection test:** stale overlays emit warnings.
- **Phase 6 overlay disposability test:** overlays are disposable; rebuild from authoritative records produces equivalent state.
- **CI wiring** (existing `groundtruth-kb` CI path, e.g., `tox.ini` or `.github/workflows/`); test failure halts release per Phase 9 §"Regression Visibility".
- Tests pass under `uv run pytest`.

**Estimated envelope:** ~900 LOC tests + 3 fixture trees + 1 golden tree + ~30 LOC CI config.

### Slice 6 — Documentation chapter + service-down/overlay fallback docs

**Scope (expanded):** new isolation chapter in `groundtruth-kb/docs/` covering:
- Application-subject explanation (plain-language).
- `gt project init` walkthrough (referencing Slice 3 adopter README block).
- `gt project upgrade` walkthrough with receipt explanation.
- `gt project doctor` severity model and remediation paths.
- Application root vs GT-KB product root.
- Existing-adopter migration walkthrough (pointer to Phase 8 rehearsal kit).
- Clean-adopter smoke contract.
- **Service-down behavior documentation** (per Phase 9 Exit Criterion 4 line 351).
- **Overlay fallback semantics documentation** (per Phase 9 Exit Criterion 4 line 352).

**Acceptance (expanded):**
- All sections from Phase 9 §6 covered.
- Tone is product documentation, not incident narrative.
- Renders without Windows-specific paths where avoidable.
- Versioned alongside GT-KB releases.
- IPR, CVR.

**Estimated envelope:** ~600 LOC docs + 2-3 diagrams.

### Slice 7 — Examples + dashboard rendering verification

**Scope (expanded; resolves decision 6):** 4 examples per Phase 9 §7, **plus dashboard-rendering step in each that exercises overlay + service paths together** (per Phase 9 Exit Criterion 4 line 349-350). If decision 6 = Yes, add 5th example: `examples/agent-red-minimized-fixture/`.

**Acceptance (expanded):**
- 4 examples (or 5 if decision 6=Yes) with own README, `groundtruth.toml`, `.gitignore`.
- **Each example contains a dashboard rendering step** that exercises the Phase 6 overlay and Phase 4 service paths together.
- CI verifies each example passes `gt project doctor` against the current GT-KB release.
- Existing-adopter-migration example documents an upgrade walkthrough ending in clean post-migration state.
- IPR, CVR.

**Estimated envelope:** 4-5 example trees, each ~10-20 files; ~80 LOC CI verification logic.

### Slice 8 — Release notes + program closeout (NEW per F2)

**Scope (NEW; resolves decisions 2, 4, 5):**
- **Release notes** covering every isolation-related change across Slices 1-7, written under selected publicity strategy from decision 4.
- **Release-version gating**: tag the GT-KB release that ships the adopter tooling per decision 2; pin in `release-readiness.md`.
- **Post-Phase-9 acceptance gate evaluation** per decision 5 criteria; final post-implementation umbrella report summarizing all 7 prior slices + decisions taken/deferred.
- Per Phase 9 §"Deliverables" line 428-430.

**Acceptance (NEW):**
- Release notes structured per decision 4 publicity strategy (release_notes / standalone_announcement / docs_chapter / example_repos / etc.).
- Release version (decision 2) tagged in `groundtruth-kb/CHANGELOG.md` + release-notes file.
- `release-readiness.md` updated with Phase 9 closure evidence.
- Acceptance gate evaluation (decision 5): evidence assembled and posted per criterion (e.g., adopter fixture count, doctor pass rate on sample, etc.).
- Final post-implementation umbrella report cites all Slice 1-7 IPRs and CVRs.
- IPR, CVR for Slice 8 itself.

**Estimated envelope:** ~300 LOC docs + 1 release-notes file + closeout report.

## Sequencing Constraints (updated)

- Slices 1-4 sequential (each consumes the prior).
- Slice 5 (tests + overlay tests + CI wiring) after Slices 1-4 VERIFIED.
- Slices 6 (docs) and 7 (examples) parallel after Slice 5.
- Slice 8 (release ops + closeout) after Slices 1-7 VERIFIED.
- Each slice's implementation bridge follows standard NEW → review → GO → impl → post-impl → VERIFIED cycle.
- Owner pre-approval per work_list extends to GTKB-ISOLATION-017.

## Cross-Program Dependencies (carried forward)

[Same as `-001`: ISOLATION-018 consumes ISOLATION-017; GTKB-ROLE-ENHANCEMENT sequenced after; GTKB-COMMAND-SURFACE independent.]

## Risk / Impact (updated)

**Scope risk (medium-large; up from medium in `-001`):** 8 slices is larger than `-001`'s 7. Mitigation: each slice is bounded; Slices 1-4 sequential dependencies known; Slices 5-8 well-defined.

**Decision-cluster risk (medium):** Slice 4 owns 3 decisions (1, 3, 7); Slice 8 owns 3 decisions (2, 4, 5). Mitigation: each slice's bridge surfaces its decisions via AskUserQuestion; owner-decision packets archived per `.claude/rules/deliberation-protocol.md`.

**Schema-vs-implementation drift risk (medium-low; unchanged):** GTKB-ISOLATION-016 Wave 3 lifecycle surfaced two cases. Mitigation: each slice's IPR cites *actual* surface paths and shapes verified at IPR-write time.

**CI integration risk (low; new in this revision):** Slices 2 and 5 wire AST gate and clean-adopter suite into CI. Mitigation: existing `groundtruth-kb` CI path is established; AST gate and test suite are additive.

**Cross-program-blocking risk (low; unchanged):** Phase 9 implementation surfaces are independent of GTKB-COMMAND-SURFACE / GTKB-ROLE-ENHANCEMENT / GTKB-MEMBASE-EFFECTIVE-USE-RECOVERY active work.

**Token cost (medium-large; updated):** 8 implementation bridges × ~3-8 hours each ≈ 25-60 hours of session time spread across multiple sessions. Recommend one fresh session per slice.

## Acceptance Criteria For This Scoping Bridge

This REVISED-1 is GO-able when Codex confirms:

1. Decision Map covers all 7 Phase 9 decisions (per F1 fix).
2. Each decision has owning slice, blocking point, expected owner input shape, and implementation consequence.
3. Slice plan covers all 7 Phase 9 required-coverage areas + previously-missed deliverables (adopter README block, release notes, version gating, service endpoint scaffold, overlay tests, dashboard rendering example, service-down/overlay fallback docs, AST gate CI, clean-adopter CI) (per F2 fix).
4. Each slice's acceptance criteria are concrete enough to drive an implementation bridge later.
5. Existing-surfaces-vs-gap mapping is accurate.
6. Cross-program dependencies are correctly identified.
7. Risks are surfaced and mitigations are credible.
8. Specification Links cover all governing artifacts.

## Decision Needed From Owner

**None at GO time** for this scoping bridge. All 7 Phase 9 owner decisions are deferred to their owning slices per the Decision Map.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
