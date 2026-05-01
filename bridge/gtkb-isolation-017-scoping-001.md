NEW

# GTKB-ISOLATION-017 Scoping Bridge

**Status:** NEW (scoping; awaits Codex GO)
**Date:** 2026-05-01 (S325)
**Author:** Prime Builder (Claude Opus 4.7)
**Predecessor:** `GTKB-ISOLATION-016` VERIFIED at `bridge/gtkb-isolation-016-phase8-wave3-execution-012.md`. Phase 8 rehearsal closed; Phase 9 productization is now actionable per the S324 priority elevation banner in `memory/work_list.md`.

---

## Purpose Of This Bridge

This bridge is **scoping-only**. It proposes a slice plan for the GTKB-ISOLATION-017 program (Phase 9 productization) and asks Codex to GO/NO-GO the plan before any implementation work lands. Per the established multi-program pattern (umbrella + sub-threads, see `gtkb-bridge-poller-001-smart-poller-007.md`), each slice will receive its own implementation bridge after this scoping is GO'd.

Scope of this commit: this scoping bridge file + INDEX entry only. No code changes.

## Specification Links

- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (upstream commit `affa5a05`) — parent architecture decision; Phase 9 productizes its application-placement rule.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md` — the Phase 9 plan; this scoping bridge maps its 7 required-coverage areas to slice work.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-001-PHASE1-AUTHORITY-MATRIX-PLAN-2026-04-22.md` — authority matrix classifying adopter-owned, product-owned, shared, and disposable artifacts.
- `.claude/rules/project-root-boundary.md` — all Phase 9 implementation must land under `E:\GT-KB`. The Phase 9 plan's references to `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\` are historical evidence only; the live in-root home is `E:\GT-KB\groundtruth-kb\` (verified to exist with full GT-KB platform structure).
- `.claude/rules/file-bridge-protocol.md` — Specification Linkage Gate, Verification Gate.
- `.claude/rules/codex-review-gate.md` — Codex GO required before per-slice implementation.
- `bridge/gtkb-isolation-016-phase8-wave3-execution-012.md` (VERIFIED) — Wave 3 closure that unblocks this scoping; the freeze-window runbook this scoping references for ISOLATION-018 carryover lives at `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/runbooks/AGENT-RED-CUTOVER-FREEZE-WINDOW-RUNBOOK-2026-05-01.md`.
- `groundtruth-kb/src/groundtruth_kb/project/doctor.py` (1872 lines) — existing doctor surface to be extended with isolation checks.
- `groundtruth-kb/src/groundtruth_kb/project/upgrade.py` (958 lines) — existing upgrade surface.
- `groundtruth-kb/src/groundtruth_kb/project/scaffold.py` — existing scaffold surface.
- `groundtruth-kb/src/groundtruth_kb/project/managed_registry.py` — existing managed-artifact registry surface.
- `groundtruth-kb/src/groundtruth_kb/project/preflight.py` — existing preflight check surface.
- `groundtruth-kb/src/groundtruth_kb/project/{ownership.py, profiles.py, rollback.py, manifest.py}` — supporting surfaces.
- `GOV-09` (CLAUDE.md governance index) — Owner Input Classification Rule.
- `GOV-20` (CLAUDE.md governance index) — Architecture Decision Workflow; per-slice IPR/CVR documents will follow the GTKB-ISOLATION-016 Wave 3 pattern.

## Existing Surfaces vs Phase 9 Required Coverage

The Phase 9 plan defines 7 required-coverage areas. This scoping bridge maps each to existing in-root surfaces and identifies the isolation-specific gap to be filled.

| Phase 9 area | Existing surface | Gap |
|---|---|---|
| 1. `gt project init` adopter-subject defaults | `groundtruth-kb/src/groundtruth_kb/project/scaffold.py`, `profiles.py` | Default subject = application; refuse to land outside `<gt-kb-root>/applications/<name>/`; idempotency on existing-adopter |
| 2. `gt project upgrade` registry-driven flow | `groundtruth-kb/src/groundtruth_kb/project/upgrade.py`, `manifest.py`, `rollback.py` | Isolation-specific upgrade steps; Phase 8 migration-kit invocation for legacy mixed roots |
| 3. Managed artifact registry isolation labels | `groundtruth-kb/src/groundtruth_kb/project/managed_registry.py`, `ownership.py` | `owner` / `upgrade` / `denied` policies per Phase 1 authority matrix; AST gate for registry coverage |
| 4. Doctor / preflight isolation checks | `groundtruth-kb/src/groundtruth_kb/project/doctor.py` (1872 LOC; no isolation checks), `preflight.py` | 9 isolation checks per Phase 9 §4; severity model (`error`/`warning`/`info`) |
| 5. Clean-adopter tests | `groundtruth-kb/tests/` (no `adopter/` subdir yet) | New `groundtruth-kb/tests/adopter/` with 10 test files per Phase 9 §5; golden-fixture diff |
| 6. Documentation | `groundtruth-kb/docs/` (substantial; no isolation chapter) | Application-subject vs product-subject docs; `gt project doctor` severity model; existing-adopter migration walkthrough |
| 7. Examples | `groundtruth-kb/examples/` (exists; needs survey) | 4 examples per Phase 9 §7: clean-adopter-minimal, adopter-with-transport-tests, adopter-with-release-gate, existing-adopter-migration |

**Key finding:** the Phase 9 implementation surfaces already exist in-root. Phase 9 is *gap-filling on existing structure*, not greenfield. This significantly de-risks the program — most slices can be characterized as "extend X with isolation logic and tests" rather than "design X from scratch".

## Proposed Slice Plan

Slices ordered by leverage and independence. Each slice gets its own implementation bridge; all reside in `E:\GT-KB\` per project-root-boundary.

### Slice 1 — Isolation doctor checks (smallest, highest leverage)

**Scope:** extend `groundtruth-kb/src/groundtruth_kb/project/doctor.py` with the 9 isolation checks from Phase 9 §4. Add severity model. Tests under `groundtruth-kb/tests/test_doctor_isolation.py`.

**Why first:** purely additive (no behavior change to existing default flow); existing `_check_*` patterns reusable; clear pass/fail per check; immediately useful (every session sees isolation-state visibility); no upgrade flow side effects.

**Acceptance:**
- 9 new `_check_isolation_*` functions per the Phase 9 spec.
- Severity enum with `error` / `warning` / `info` levels.
- Tests assert each check fires correctly on a fixture violation and stays silent on a clean fixture.
- T-derived from Phase 9 §4 clauses, mapped 1:1.
- IPR + CVR documents per GOV-20.

**Estimated envelope:** ~400 LOC source + ~300 LOC tests. One implementation bridge cycle.

### Slice 2 — Managed artifact registry isolation labels

**Scope:** extend `groundtruth-kb/src/groundtruth_kb/project/managed_registry.py` and `ownership.py` with the `owner` / `upgrade` / `denied` policies per Phase 1 authority matrix. Add AST gate that asserts every adopter-scaffolded file has a registry entry.

**Why second:** doctor checks (Slice 1) start querying the registry once labels exist; upgrade flow (Slice 3) consumes the registry. Slice 2 is the data substrate the rest depends on.

**Acceptance:**
- Registry schema updated with `owner` and `upgrade_policy` fields.
- Per-entry rationale captured.
- AST gate test asserting registry coverage of scaffolded files.
- Migration-note discipline (no owner-flip without note).
- Tests, IPR, CVR.

**Estimated envelope:** ~250 LOC source + ~200 LOC tests.

### Slice 3 — `gt project init` adopter-subject defaults

**Scope:** extend `scaffold.py` and `profiles.py` so `gt project init` defaults `work subject = application`, refuses to land outside `<gt-kb-root>/applications/<name>/`, and refuses to overwrite existing-adopter state (recommends `gt project upgrade`).

**Why third:** Slice 2 registry is consumed by init for scaffolding decisions; doctor checks from Slice 1 verify the resulting tree.

**Acceptance:**
- Init refuses outside-root paths.
- Init refuses on existing-adopter idempotency check.
- Scaffolded tree matches Phase 9 §1 enumeration (`groundtruth.toml`, `groundtruth.db` empty, `bridge/INDEX.md`, `memory/work_list.md` placeholder, `memory/release-readiness.md`, `.claude/` wrappers, `.codex/hooks.json`, `.groundtruth/formal-artifact-approvals/.gitkeep`, segregated `.gitignore`).
- Tests verify byte-level conformance against a golden fixture.
- IPR, CVR.

**Estimated envelope:** ~300 LOC source + ~400 LOC tests + golden fixture.

### Slice 4 — `gt project upgrade` isolation-specific steps + Phase 8 migration kit

**Scope:** extend `upgrade.py` to detect existing-adopter mixed-root state and invoke the Phase 8 rehearsal driver (`scripts/rehearse_isolation.py`) under upgrade-receipt discipline. Add isolation-specific upgrade steps that converge non-isolated adopter trees onto isolated defaults.

**Why fourth:** depends on Slice 1 (doctor diagnoses pre-upgrade state), Slice 2 (registry drives convergence), and Slice 3 (init defaults define what convergence means).

**Acceptance:**
- Upgrade detects mixed-root state via doctor check.
- Upgrade invokes `rehearse_isolation.py` against the existing adopter tree.
- Upgrade preserves adopter-owned files; refuses to silently overwrite.
- Rollback restores pre-upgrade state.
- Receipts capture migration evidence.
- Tests, IPR, CVR.

**Estimated envelope:** ~400 LOC source + ~500 LOC tests.

### Slice 5 — Clean-adopter test suite

**Scope:** new `groundtruth-kb/tests/adopter/` subdirectory with the 10 test files from Phase 9 §5 (test_init_defaults_to_application_subject.py, etc.). Golden fixtures committed.

**Why fifth:** consumes Slices 1-4 capabilities; cannot ship before they do.

**Acceptance:**
- 10 test files implementing the assertions from Phase 9 §5.
- Each test runs in an isolated temp directory; no cross-test state.
- 3 existing-adopter migration fixtures (legacy Agent-Red-shaped, mixed bridge/backlog, co-located product artifacts).
- All assertions outside-in (GOV-19) and meaningful (GOV-18; no rubber-stamp).
- Golden fixture diffs verify byte-level conformance per GT-KB version.
- Tests pass under `uv run pytest`.

**Estimated envelope:** ~800 LOC tests + ~3 fixture trees + ~1 golden tree.

### Slice 6 — Documentation

**Scope:** new isolation chapter in `groundtruth-kb/docs/` covering application-subject explanation, init/upgrade/doctor walkthroughs, application-vs-product-root distinction, existing-adopter migration pointer, clean-adopter smoke contract.

**Why sixth:** can ship after the implementation surfaces stabilize. Documentation drift on in-flight features is anti-pattern.

**Acceptance:**
- Per-section coverage from Phase 9 §6.
- Tone is product documentation, not incident narrative.
- Renders without Windows-specific paths where avoidable.
- Versioned alongside GT-KB releases.
- IPR, CVR.

**Estimated envelope:** ~500 LOC docs + 2-3 diagrams.

### Slice 7 — Examples

**Scope:** new `groundtruth-kb/examples/clean-adopter-minimal/`, `adopter-with-transport-tests/`, `adopter-with-release-gate/`, `existing-adopter-migration/` per Phase 9 §7.

**Why last:** examples demonstrate the productized capability and ship after Slices 1-6 are VERIFIED. CI verifies examples match doctor checks on the released GT-KB version.

**Acceptance:**
- 4 examples with their own README, `groundtruth.toml`, `.gitignore`.
- CI verifies each example passes `gt project doctor` against the current GT-KB release.
- Existing-adopter-migration example documents an upgrade walkthrough ending in clean post-migration state.
- IPR, CVR.

**Estimated envelope:** ~4 example trees, each ~10-20 files.

## Sequencing Constraints

- Slices 1-4 are sequential dependencies (each consumes the prior).
- Slice 5 (tests) consumes Slices 1-4; cannot ship before all four are VERIFIED.
- Slice 6 (docs) and Slice 7 (examples) can ship in parallel after Slice 5; or sequenced if author capacity is constrained.
- Each slice's implementation bridge follows the standard NEW → review → GO → impl → post-impl → VERIFIED cycle.
- Owner pre-approval per `memory/work_list.md` row 2 (now DONE) extends to GTKB-ISOLATION-017 per the priority elevation banner.

## Cross-Program Dependencies

- **GTKB-COMMAND-SURFACE** (work_list row 12): the `::` prefix in-session command dispatch and `gt` CLI binary work is independent of ISOLATION-017 implementation but provides ergonomic affordance once both ship. Not a blocker either direction.
- **GTKB-GOV-PROPOSAL-STANDARDS Slice 1** (work_list row 5): blocked on root-boundary reconciliation. ISOLATION-017 implements the canonical "all GT-KB platform work in `E:\GT-KB\`" pattern that GTKB-GOV-PROPOSAL-STANDARDS Slice 1 will need to follow. ISOLATION-017 sets the precedent; Proposal-Standards Slice 1 inherits it.
- **GTKB-ISOLATION-018** (Agent Red child-directory cutover): consumes ISOLATION-017 capabilities. Cannot ship before ISOLATION-017 closes.
- **GTKB-ROLE-ENHANCEMENT** (work_list row 11): explicitly sequenced *after* ISOLATION-017 VERIFIED.

## Risk / Impact

**Scope risk (medium):** 7 slices is large. Mitigation: each slice is small enough to fit a single bridge cycle (~3-8 hours each); existing surface code reduces invention work; sequential dependencies mean each subsequent slice is unblocked by predecessor evidence.

**Schema-vs-implementation drift risk (medium-low):** the GTKB-ISOLATION-016 Wave 3 lifecycle surfaced two cases of proposal-claim-vs-implementation-shape mismatch (Codex `-002` F1 path; Codex `-010` F1 schema). Mitigation: each slice's IPR cites the *actual* surface paths and shapes (not ideal/aspirational), verified at IPR-write time.

**Cross-program-blocking risk (low):** Phase 9 implementation surfaces are independent of GTKB-COMMAND-SURFACE / GTKB-ROLE-ENHANCEMENT / GTKB-MEMBASE-EFFECTIVE-USE-RECOVERY active work; no contention expected.

**Owner-decision risk (low):** the only owner-decision-needed item identified in the Phase 9 plan is "mandatory vs opt-in isolation for existing adopters". This surfaces at Slice 4 (`gt project upgrade`) as a slice-level decision, not a scoping-level decision. Resolution at slice-bridge-time.

**Token cost (medium-large):** 7 implementation bridges × ~3-8 hours each = ~25-50 hours of session time spread across multiple sessions. Each session ≈ 1 slice. Recommend allocating one fresh session per slice for focus.

## Acceptance Criteria For This Scoping Bridge

This scoping is GO-able when Codex confirms:

1. The slice plan covers all 7 Phase 9 required-coverage areas.
2. Slice ordering respects dependency constraints (1-4 sequential; 5 after 1-4; 6/7 after 5).
3. Each slice's acceptance criteria are concrete enough to drive an implementation bridge later.
4. Existing-surfaces-vs-gap mapping is accurate (Codex spot-checks `doctor.py:1872`, `upgrade.py:958`, `scaffold.py`, `managed_registry.py` line counts and absent isolation logic).
5. Cross-program dependencies are correctly identified.
6. Risks are surfaced and mitigations are credible.
7. Specification Links cover all governing artifacts.

## Decision Needed From Owner

**None at GO time** for this scoping bridge.

Owner-decision items deferred to per-slice bridges:
- Slice 4: mandatory-vs-opt-in isolation for existing adopters (raised in Phase 9 plan §"Open decisions for the implementation bridge").
- Slice 7: whether Agent Red becomes a minimized Phase 9 example (raised in Phase 9 plan §"Open decisions for the implementation bridge").

Each per-slice bridge will surface its decisions independently.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
