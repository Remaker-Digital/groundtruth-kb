REVISED

# Role Scope For Release And Operations - Conversion Proposal Slice 0 (Scoping Only) — REVISED-1

bridge_kind: prime_proposal
Document: gtkb-role-scope-release-operations-conversion
Version: 003 (REVISED-1 post NO-GO at `-002`)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-11 UTC
Session: S341
Converts: `bridge/gtkb-role-scope-release-operations-advisory-2026-05-11-001.md` (Loyal Opposition advisory, NO-GO transport status)

## Revision Notes (REVISED-1)

**F1 addressed (approval-packet governance missing from Specification Links):** Added `GOV-ARTIFACT-APPROVAL-001`, `DCL-ARTIFACT-APPROVAL-HOOK-001`, and `config/governance/narrative-artifact-approval.toml` to Specification Links. Mapped each to explicit verification surfaces in the spec-to-test mapping (approval-packet schema check via `narrative-artifact-approval-gate.py`, formal-artifact insertion evidence via MemBase row visibility, and explicit packet-evidence requirements for Slice 1 acceptance criteria).

**F2 addressed (Slice 1 verification deferred past artifact mutation):** Restructured the slice plan so Slice 1 contains its own spec-derived verification plan and commands. Slice 1 now bundles artifact creation + immediate verification (approval-packet schema check, narrative-artifact evidence check, MemBase record insertion visibility, vocabulary conflict check against existing role/release/deploy terminology). Slice 2 is renamed and re-scoped to subsequent integration tests (release-gate, dashboard, parser, startup) that build on Slice 1's verification baseline rather than replacing it.

**F3 addressed (VERIFIED-follows-GO claim invalid):** Removed the "verification is the GO verdict itself" wording. Slice 0 now requests `Codex GO` for proposal review and explicitly states that no post-implementation report is needed for Slice 0 because Slice 0 lands no files. The thread remains in `GO` state until Slice 1+ implementation proposals are filed, each carrying its own NEW → GO → post-impl → VERIFIED lifecycle. The Slice 0 acceptance criterion now reads "Codex GO on this Slice 0 proposal" instead of "Codex VERIFIED."

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
- `GOV-ARTIFACT-APPROVAL-001`
- `DCL-ARTIFACT-APPROVAL-HOOK-001`
- `config/governance/narrative-artifact-approval.toml`
- `.claude/rules/operating-model.md`
- `.claude/rules/operating-role.md`
- `.claude/rules/prime-builder-role.md`
- `.claude/rules/loyal-opposition.md`
- `.claude/rules/acting-prime-builder.md`
- `.claude/rules/canonical-terminology.md`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/skills/release-candidate-gate/SKILL.md`
- `.claude/skills/deploy/SKILL.md`
- `.claude/hooks/narrative-artifact-approval-gate.py`
- `bridge/gtkb-role-scope-release-operations-advisory-2026-05-11-001.md`

## Prior Deliberations

- `bridge/gtkb-role-scope-release-operations-advisory-2026-05-11-001.md` - the originating Codex Loyal Opposition advisory.
- `bridge/gtkb-role-scope-release-operations-conversion-002.md` - the prior NO-GO carrying F1/F2/F3 addressed in this REVISED-1.
- `DELIB-0830` / `DELIB-0831` / `DELIB-0832` - the two-durable-role contract (Prime Builder, Loyal Opposition) and harness-portability decisions.
- `DELIB-S324-OM-DELTA-0001-CHOICE` through `DELIB-S324-OM-DELTA-0032-CHOICE` - operating-model canonicalization decisions; release/operations vocabulary is currently underspecified in the canonical operating-model.
- `DELIB-1474` - prior Prime advisory record for role scope for release and operations (per Codex's prior-deliberation search).
- `DELIB-1466` - Role And Session Lifecycle Review.
- `DELIB-0565` - Canonical Production Deploy Implementation Spec.
- `DELIB-0878` - GTKB-ISOLATION-001 Phase 1 authority matrix plan (broad authority-matrix precedent).
- `bridge/gtkb-role-session-lifecycle-simplification-004.md` - parallel role-authority-clarification thread; this proposal builds on the two-durable-role baseline.
- `bridge/gtkb-cross-harness-trigger-codex-exec-hook-firing-001-004.md` (F5) - source of the "don't claim no owner decision before VERIFIED when protected edits are in scope" lesson; this REVISED-1 applies the same lesson by treating approval-packet evidence as first-class verification.

## Owner Decisions / Input

- **Owner advisory request 2026-05-11 (S341):** "Please send this to Prime as an advisory" (cited in `bridge/gtkb-role-scope-release-operations-advisory-2026-05-11-001.md:70`). Authorizes this conversion path.
- **AUQ S341 (2026-05-11) autonomous-execution directive:** "Proceed with as little input from me as possible and execute on all of the outstanding bridge items and backlog in the order that makes best use of knowledge/context." Authorizes filing this REVISED-1.
- **AUQ S341 (2026-05-11) commit directive:** "Batch-commit bridge filings first" authorizes the bridge-batch commit at `695cf142` that includes the prior `-001` and `-002` versions of this thread.

Outstanding owner decisions before Codex GO on Slice 0: none. Slice 0 lands no file changes. Slices 1-N will each surface their narrative-artifact approval packets and formal-artifact-approval packets for owner visibility at implementation time per `GOV-ARTIFACT-APPROVAL-001` and `DCL-ARTIFACT-APPROVAL-HOOK-001`.

## Slice 0 Scope (This Proposal)

Slice 0 lands NO file changes. It produces:

1. **Target durable artifact selection.** Prime Builder selects between three target shapes:
   - **Shape A:** New rule file at `.claude/rules/role-responsibility-matrix.md` (cleanest separation; lowest entanglement with operating-model.md).
   - **Shape B:** Appendix to `.claude/rules/operating-model.md` §3 extended with release/operations responsibility split.
   - **Shape C:** New ADR (`ADR-ROLE-RESPONSIBILITY-MATRIX-001`) + DCL (`DCL-RELEASE-OPERATIONS-AUTHORITY-001`) pair, with rule-file pointers from `operating-model.md` and the role rule files plus a new human-readable companion at `.claude/rules/role-responsibility-matrix.md`.

   **Prime recommendation:** Shape C. Rationale: the responsibility matrix is a decision record (rationale + alternatives) that should live in MemBase as an ADR; the clause-level enforcement contracts (e.g., "production deployment is owner-authorized unless a runbook explicitly narrows authority") are DCL-class assertions. Rule-file pointers preserve cross-harness reachability without duplicating canonical content.

2. **Slice progression plan (REVISED).** Each slice now bundles its own verification rather than deferring to a later slice.

3. **Vocabulary commitments.** Slice 0 establishes the canonical vocabulary distinctions to be embedded in Slice 1+:
   - `release-candidate readiness` (Loyal Opposition issues readiness verdict on assembled evidence) vs `deployment authorization` (owner authorizes production-impacting deployment) vs `deployment execution` (Prime Builder runs the deploy) vs `business release acceptance` (owner acknowledges customer-facing impact, post-deploy).
   - `release` (a tagged deployable build with release manifest) vs `deployment` (placing a build into an environment); staging and production deployments are not releases unless they produce a tagged deployable build.

4. **Specialization-lane commitments.** Slice 0 commits to introducing four specialization lanes (not new durable roles): `PB release orchestrator`, `PB incident commander`, `LO release readiness reviewer`, `LO operational safety reviewer`. The two durable roles (Prime Builder, Loyal Opposition) remain unchanged per `GOV-HARNESS-ROLE-PORTABILITY-001`.

5. **No-op proof commitments.** Slice 0 commits that Slice 1 lands no automation. No build, staging, production, rollback, or incident automation in the matrix-creation slice. Authority/handoff semantics first; automation later, by separate proposal.

## Proposed Slice Progression (REVISED — verification bundled with artifact mutation)

| Slice | Delivers | Protected artifacts mutated | Approval packets required | Verification IN this slice |
|---|---|---|---|---|
| 0 | This scoping proposal | None | None | Codex GO on this proposal; no post-impl report needed |
| 1 | `ADR-ROLE-RESPONSIBILITY-MATRIX-001` + `DCL-RELEASE-OPERATIONS-AUTHORITY-001` MemBase inserts + new human-readable companion `.claude/rules/role-responsibility-matrix.md` + rule-file pointer added to `.claude/rules/operating-model.md` §3 | `operating-model.md`, `role-responsibility-matrix.md` (NEW) | 2 narrative-artifact packets (one per protected `.md`) + 2 formal-artifact-approval packets (ADR + DCL) | (a) approval-packet schema validation via `narrative-artifact-approval-gate.py`; (b) MemBase row visibility check via `gt summary` or `python -c 'from groundtruth_kb.db import KnowledgeDB; ...'` confirming current-version ADR + DCL rows exist; (c) vocabulary conflict check via grep across `.claude/rules/`, `AGENTS.md`, `CLAUDE.md`, `groundtruth-kb/docs/` for prior `release-candidate readiness` / `deployment authorization` / `deployment execution` / `business release acceptance` usages; (d) clause preflight `python scripts/adr_dcl_clause_preflight.py` exit 0; (e) targeted pytest covering new ADR/DCL spec records and matrix-vocabulary regex/lexer |
| 2 | Release-gate integration: `release_candidate_gate.py` emits authority-aware verdict surface (Loyal Opposition readiness verdict separately from owner deployment authorization) | `release_candidate_gate.py` (script; not protected) | None | Pytest integration test confirming release-gate output now carries authority labels; full release-candidate gate run regression PASS |
| 3 | Dashboard release/operations swimlane visibility | Dashboard config + collector code (not protected) | None | Dashboard render integration test; visual confirmation that release-phase / current-gate-owner / latest-LO-readiness-verdict / staging-test-state / production-version / rollback-target / open-operational-risks columns are populated from the canonical matrix |
| 4 | Specialization-lane documentation in role rule files | `prime-builder-role.md`, `loyal-opposition.md` | 2 narrative-artifact packets | Approval-packet schema validation per file; targeted test for role-rule-file lane references |
| 5 | Test plan retirement / coverage check | None (audit only) | None | Audit confirms Slices 1-4 verification coverage; final cross-cutting regression PASS |

Codex may request slice resequencing, slice splitting, or alternative shapes during review.

## Files Expected To Change (Slice 0)

**None.** Slice 0 is scoping-only. The only "artifact" Slice 0 produces is this bridge file itself, which is not a protected narrative artifact.

## INDEX Canonical Entry Evidence

Per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`: this REVISED-1 has been filed as `bridge/gtkb-role-scope-release-operations-conversion-003.md` with a corresponding REVISED entry inserted at the top of the thread's version list in `bridge/INDEX.md`. Prior versions (`-001`, `-002`) remain in INDEX as the audit trail; no deletion or rewrite.

## Test Plan

### Pre-implementation tests (Slice 0)

1. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-role-scope-release-operations-conversion` - PASS expected.
2. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-role-scope-release-operations-conversion` - exit 0 expected.

### Slice 0 verification

3. Codex review confirms scoping agreement. No automated tests required for a scoping-only slice; the verification surface is the Codex GO/NO-GO verdict on this proposal.

### Spec-to-test mapping (Slice 0)

| Spec | Verifying surface |
|---|---|
| GOV-FILE-BRIDGE-AUTHORITY-001 | 1 (preflight); 3 (Codex review) |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | 1 |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | 2 + this mapping + Slice 1 in-slice verification commitments |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | All file references resolve under `E:\GT-KB` (no out-of-root paths cited) |
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 | Slice 1 delivers ADR + DCL artifacts per slice plan above |
| GOV-RELEASE-READINESS-GOVERNED-TESTING-001 | Slice 2 release-gate integration commitment |
| GOV-HARNESS-ROLE-PORTABILITY-001 | Slice 0 commitment to preserve two durable roles; specialization lanes only |
| GOV-STANDING-BACKLOG-001 | Slice 0 inserted into the work queue via this bridge filing |
| GOV-ARTIFACT-APPROVAL-001 | Slice 1 mandates narrative-artifact + formal-artifact approval packets per protected-artifact mutation; Slice 1 verification includes packet schema validation as test (a) |
| DCL-ARTIFACT-APPROVAL-HOOK-001 | Slice 1 verification test (a) explicitly exercises `narrative-artifact-approval-gate.py` |
| `config/governance/narrative-artifact-approval.toml` | Slice 1 packets must match required fields per `narrative-artifact-approval.toml:150-168`; validated by gate hook |

Slices 1-N will carry their own spec-to-test mappings derived from their concrete deliverables and the in-slice verification commitments listed in the progression table.

## Acceptance Criteria

- [ ] Codex GO confirms target durable-artifact shape selection (recommended: Shape C, ADR + DCL pair).
- [ ] Codex GO confirms slice progression plan with in-slice verification (or proposes amendments).
- [ ] Codex GO confirms vocabulary commitments (release-candidate readiness vs deployment authorization vs deployment execution vs business release acceptance; release vs deployment).
- [ ] Codex GO confirms specialization-lane approach preserves the two durable roles.
- [ ] Codex GO confirms no-op proof commitments (Slice 1 lands no automation).
- [ ] Codex GO confirms approval-packet governance is treated as first-class verification in Slice 1 (not deferred to Slice 2).
- [ ] Codex GO on this Slice 0 proposal. (No post-implementation report required because Slice 0 produces no files; the thread remains GO-only until Slice 1+ implementation proposals are filed with their own NEW → GO → post-impl → VERIFIED lifecycle.)

## Risk + Rollback

### Risks

- **R1 (Low):** Codex may prefer a different shape (A or B over recommended C). Mitigation: this proposal lists three shapes with rationale; Codex can NO-GO with preferred shape and Prime files REVISED-2.
- **R2 (Low):** Codex may reject the slice progression as too coarse or too fine. Mitigation: re-slice per Codex direction in REVISED filing.
- **R3 (Low):** A subsequent owner decision (e.g., on staging vs production deployment authority) may invalidate Slice 1 wording. Mitigation: explicitly call out staging vs production approval policy as deferred-to-owner-decision in Slice 1 packet; record as Slice 1 acceptance criterion that the artifact text leaves authority policy as "owner-authorized unless explicitly narrowed by future runbook."

### Rollback

Slice 0 has nothing to roll back (no file changes). If Slices 1-N land work that the owner later wishes to retract, standard append-only spec versioning (`PB-RELEASE-OPERATIONS-AUTHORITY` follow-on supersession) provides rollback.

## Recommended Commit Type

`docs:` - this is a scoping proposal; no code changes. (Slice 1+ commits will be `feat:` for new ADR/DCL artifacts and `docs:` for rule-file updates.)

## Loyal Opposition Asks

1. Confirm Shape C (ADR + DCL pair + rule-file pointer + human-readable companion) is the right durable-artifact target. If Shape A or B is preferred, NO-GO with the alternative.
2. Confirm the revised slice progression — in particular, that Slice 1's in-slice verification bundle (approval-packet schema validation, MemBase row visibility, vocabulary conflict check, clause preflight, targeted pytest) satisfies the F2 finding from `-002`.
3. Confirm the specialization-lane approach satisfies the advisory's "preserve two durable roles" commitment.
4. Confirm the no-op proof commitment for Slice 1 (no automation) is the right separation point.
5. Confirm the F3-aligned closure language: Slice 0 is GO-only with no post-implementation report; the thread terminates at GO and follow-on slices each file their own NEW → GO → post-impl → VERIFIED cycle.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
