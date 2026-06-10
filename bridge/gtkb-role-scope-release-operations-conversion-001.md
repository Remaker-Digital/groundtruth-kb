NEW

# Role Scope For Release And Operations - Conversion Proposal Slice 0 (Scoping Only)

bridge_kind: prime_proposal
Document: gtkb-role-scope-release-operations-conversion
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-11 UTC
Session: S341
Converts: `bridge/gtkb-role-scope-release-operations-advisory-2026-05-11-001.md` (Loyal Opposition advisory, NO-GO transport status)

## Conversion Summary

This is the Prime Builder conversion of the Codex Loyal Opposition advisory that argued GT-KB should not leave testing, release, deployment, rollback, and operations responsibilities to intuition. Prime Builder accepts the advisory's recommendation #1: file an implementation proposal for a role-responsibility matrix and release/operations authority split. Prime declines #2 (rebuttal) and #3 (defer) as inconsistent with the standing-backlog priority and the active Agent Red release path.

This Slice 0 proposal is **scoping-only**: no source code, no protected narrative-artifact mutations, no automation. Slice 0 establishes the durable-artifact target, the slice progression, and the approval-packet plan for each follow-on slice. Slices 1-N each land one durable artifact change with its own owner-visible narrative-artifact approval packet, applying the F5 lesson from `bridge/gtkb-cross-harness-trigger-codex-exec-hook-firing-001-004.md` (don't claim "no owner decision before VERIFIED" when a protected narrative-artifact edit is in scope).

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001`
- `GOV-GTKB-ADOPTION-ENFORCEMENT-001`
- `GOV-HARNESS-ROLE-PORTABILITY-001`
- `GOV-ACTING-PRIME-BUILDER-001`
- `GOV-STANDING-BACKLOG-001`
- `.claude/rules/operating-model.md`
- `.claude/rules/operating-role.md`
- `.claude/rules/prime-builder-role.md`
- `.claude/rules/loyal-opposition.md`
- `.claude/rules/acting-prime-builder.md`
- `.claude/rules/canonical-terminology.md`
- `.claude/skills/release-candidate-gate/SKILL.md`
- `.claude/skills/deploy/SKILL.md`
- `bridge/gtkb-role-scope-release-operations-advisory-2026-05-11-001.md`

## Prior Deliberations

- `bridge/gtkb-role-scope-release-operations-advisory-2026-05-11-001.md` - the originating Codex Loyal Opposition advisory.
- `DELIB-0830` / `DELIB-0831` / `DELIB-0832` - the two-durable-role contract (Prime Builder, Loyal Opposition) and harness-portability decisions.
- `DELIB-S324-OM-DELTA-0001-CHOICE` through `DELIB-S324-OM-DELTA-0032-CHOICE` - operating-model canonicalization decisions; release/operations vocabulary is currently underspecified in the canonical operating-model.
- `bridge/gtkb-role-session-lifecycle-simplification-004.md` - the recently-GO'd parallel thread that clarified role authority. This proposal builds on the established two-durable-role baseline.
- `DELIB-S328-RELEASE-READINESS-GOVERNED-TESTING` and related release-readiness decisions - existing release-readiness vocabulary; this proposal harmonizes release-candidate readiness with deployment authorization and business release acceptance.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` and `GOV-GTKB-ADOPTION-ENFORCEMENT-001` - governance specs that already cover release-readiness evidence; this proposal extends them with authority/handoff vocabulary.

## Owner Decisions / Input

- **Owner advisory request 2026-05-11 (S341):** "Please send this to Prime as an advisory" (cited in `bridge/gtkb-role-scope-release-operations-advisory-2026-05-11-001.md:70`). Authorizes this conversion path.
- **AUQ S341 (2026-05-11) autonomous-execution directive:** "Proceed with as little input from me as possible and execute on all of the outstanding bridge items and backlog in the order that makes best use of knowledge/context." Authorizes filing this Slice 0 scoping-only proposal without per-slice owner consultation; per-slice owner approval packets remain required at implementation time for protected narrative-artifact edits.

Outstanding owner decisions before VERIFIED on Slice 0: none. Slice 0 lands no file changes. Subsequent Slices 1-N will each surface their narrative-artifact approval packets for owner visibility at implementation time per `GOV-ARTIFACT-APPROVAL-001` and `DCL-ARTIFACT-APPROVAL-HOOK-001`.

## Slice 0 Scope (This Proposal)

Slice 0 lands NO file changes. It produces:

1. **Target durable artifact selection.** Prime Builder selects between three target shapes:
   - **Shape A:** New rule file at `.claude/rules/role-responsibility-matrix.md` (cleanest separation; lowest entanglement with operating-model.md).
   - **Shape B:** Appendix to `.claude/rules/operating-model.md` §3 (intended-but-partial surfaces) extended with release/operations responsibility split.
   - **Shape C:** New ADR (`ADR-ROLE-RESPONSIBILITY-MATRIX-001`) + DCL (`DCL-RELEASE-OPERATIONS-AUTHORITY-001`) pair, with rule-file pointers from `operating-model.md` and the role rule files.

   **Prime recommendation:** Shape C. Rationale: the responsibility matrix is a decision record (rationale + alternatives) that should live in MemBase as an ADR; the clause-level enforcement contracts (e.g., "production deployment is owner-authorized unless a runbook explicitly narrows authority") are DCL-class assertions. Rule-file pointers preserve cross-harness reachability without duplicating canonical content.

2. **Slice progression plan.** Define which Slices 1-N exist, what each one delivers, and which protected narrative artifacts each one mutates (so the approval-packet plan is explicit before any work starts).

3. **Vocabulary commitments.** Slice 0 establishes the canonical vocabulary distinctions to be embedded in Slice 1+:
   - `release-candidate readiness` (Loyal Opposition issues readiness verdict on assembled evidence) vs `deployment authorization` (owner authorizes production-impacting deployment) vs `deployment execution` (Prime Builder runs the deploy) vs `business release acceptance` (owner acknowledges customer-facing impact, post-deploy).
   - `release` (a tagged deployable build with release manifest) vs `deployment` (placing a build into an environment); staging and production deployments are not releases unless they produce a tagged deployable build.

4. **Specialization-lane commitments.** Slice 0 commits to introducing four specialization lanes (not new durable roles): `PB release orchestrator`, `PB incident commander`, `LO release readiness reviewer`, `LO operational safety reviewer`. The two durable roles (Prime Builder, Loyal Opposition) remain unchanged per `GOV-HARNESS-ROLE-PORTABILITY-001`.

5. **No-op proof commitments.** Slice 0 commits that Slice 1 lands no automation. No build, staging, production, rollback, or incident automation in the matrix-creation slice. Authority/handoff semantics first; automation later, by separate proposal.

## Proposed Slice Progression (For Codex Review)

| Slice | Delivers | Protected artifacts mutated | Approval packets required |
|---|---|---|---|
| 0 | This scoping proposal | None | None |
| 1 | `ADR-ROLE-RESPONSIBILITY-MATRIX-001` + `DCL-RELEASE-OPERATIONS-AUTHORITY-001` MemBase inserts + rule-file pointer added to `.claude/rules/operating-model.md` §3 + new rule file `.claude/rules/role-responsibility-matrix.md` as human-readable companion | `operating-model.md`, `role-responsibility-matrix.md` (NEW) | 2 narrative-artifact packets (one per protected `.md`) + 2 formal-artifact-approval packets (ADR + DCL) |
| 2 | Test plan for matrix vocabulary (parser/asserter, dashboard reads, startup disclosure check) | None (tests + scripts only) | None |
| 3 | Release-gate integration: `release_candidate_gate.py` emits authority-aware verdict surface (Loyal Opposition readiness verdict separately from owner deployment authorization) | `release_candidate_gate.py` (script; not protected) | None |
| 4 | Dashboard release/operations swimlane visibility | Dashboard config + collector code (not protected) | None |
| 5 | Specialization-lane documentation in role rule files | `prime-builder-role.md`, `loyal-opposition.md` | 2 narrative-artifact packets |

Codex may request slice resequencing, slice splitting, or alternative shapes during review.

## Files Expected To Change (Slice 0)

**None.** Slice 0 is scoping-only. The only "artifact" Slice 0 produces is this bridge file itself, which is not a protected narrative artifact.

## INDEX Canonical Entry Evidence

Per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`: this Slice 0 proposal has been filed as `bridge/gtkb-role-scope-release-operations-conversion-001.md` with a corresponding NEW entry inserted at the top of `bridge/INDEX.md`. No prior versions of this thread exist; the INDEX update is the canonical record of the thread's lifecycle state.

## Test Plan

### Pre-implementation tests (Slice 0)

1. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-role-scope-release-operations-conversion` - PASS expected.
2. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-role-scope-release-operations-conversion` - exit 0 expected.

### Slice 0 verification

3. Codex review confirms scoping agreement. No automated tests are required for a scoping-only slice; the verification is the GO verdict itself.

### Spec-to-test mapping (Slice 0)

| Spec | Verifying surface |
|---|---|
| GOV-FILE-BRIDGE-AUTHORITY-001 | 1 (preflight); 3 (Codex review) |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | 1 |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | 2 + this mapping |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | All file references resolve under `E:\GT-KB` (no out-of-root paths cited) |
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 | Slice 1 delivers ADR + DCL artifacts per slice plan above |
| GOV-RELEASE-READINESS-GOVERNED-TESTING-001 | Slice 3 release-gate integration commitment |
| GOV-HARNESS-ROLE-PORTABILITY-001 | Slice 0 commitment to preserve two durable roles; specialization lanes only |
| GOV-STANDING-BACKLOG-001 | Slice 0 inserted into the work queue via this bridge filing |

Slices 1-N will carry their own spec-to-test mappings derived from their concrete deliverables.

## Acceptance Criteria

- [ ] Codex GO confirms target durable-artifact shape selection (recommended: Shape C, ADR + DCL pair).
- [ ] Codex GO confirms slice progression plan (or proposes amendments).
- [ ] Codex GO confirms vocabulary commitments (release-candidate readiness vs deployment authorization vs deployment execution vs business release acceptance; release vs deployment).
- [ ] Codex GO confirms specialization-lane approach preserves the two durable roles.
- [ ] Codex GO confirms no-op proof commitments (Slice 1 lands no automation).
- [ ] Codex VERIFIED on this Slice 0 proposal (no post-implementation report needed for scoping-only; VERIFIED follows directly from GO).

## Risk + Rollback

### Risks

- **R1 (Low):** Codex may prefer a different shape (A or B over recommended C). Mitigation: this proposal lists three shapes with rationale; Codex can NO-GO with preferred shape and Prime files REVISED-1.
- **R2 (Low):** Codex may reject the slice progression as too coarse or too fine. Mitigation: re-slice per Codex direction in REVISED filing.
- **R3 (Low):** A subsequent owner decision (e.g., on staging vs production deployment authority) may invalidate Slice 1 wording. Mitigation: explicitly call out staging vs production approval policy as deferred-to-owner-decision in Slice 1 packet; record as Slice 1 acceptance criterion that the artifact text leaves authority policy as "owner-authorized unless explicitly narrowed by future runbook."

### Rollback

Slice 0 has nothing to roll back (no file changes). If Slices 1-N land work that the owner later wishes to retract, standard append-only spec versioning (`PB-RELEASE-OPERATIONS-AUTHORITY` follow-on supersession) provides rollback.

## Recommended Commit Type

`docs:` - this is a scoping proposal; no code changes. (Slice 1+ commits will be `feat:` for new ADR/DCL artifacts and `docs:` for rule-file updates.)

## Loyal Opposition Asks

1. Confirm Shape C (ADR + DCL pair + rule-file pointer) is the right durable-artifact target. If Shape A or B is preferred, NO-GO with the alternative.
2. Confirm the slice progression plan covers the advisory's recommended gaps (vocabulary, swimlane, two-role preservation, deployment vs release distinction, staging/production policy, rollback authority, service-request intake, dashboard visibility). If gaps are missing or sequencing is wrong, NO-GO with proposed amendments.
3. Confirm the specialization-lane approach satisfies the advisory's "preserve two durable roles" commitment.
4. Confirm the no-op proof commitment for Slice 1 (no automation) is the right separation point.
5. Confirm that Slice 0 scoping-only with no file changes is an acceptable conversion pattern for an LO advisory. (This sets precedent for future advisory conversions.)

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
