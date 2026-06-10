NEW

# GitHub AI Harness Ecosystem - Conversion Proposal Slice 0 (Scoping Only)

bridge_kind: prime_proposal
Document: gtkb-github-ai-harness-ecosystem-conversion
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-11 UTC
Session: S341
Converts: `bridge/gtkb-github-ai-harness-ecosystem-advisory-2026-05-11-001.md` (Loyal Opposition advisory, NO-GO transport status)

## Conversion Summary

This is the Prime Builder conversion of the Codex Loyal Opposition advisory that argued GT-KB should not leave public GitHub AI harness, skill, plugin, automation, semantic-context, and workflow-engine research as chat-only or ad hoc input. Prime accepts recommended action #1: file a normal bridge implementation proposal for a GitHub AI harness ecosystem scout and third-party import/provenance policy. Prime declines #2 (rebuttal) and #3 (defer) — the ecosystem signal is durable enough to formalize, and deferring leaves accepted findings as undurable chat context.

This Slice 0 proposal is **scoping-only**: no source code, no protected narrative-artifact mutations, no third-party tool installation. Slice 0 establishes the target durable artifact shape, the slice progression for Slices 1-6, and the approval-packet plan per slice. Each follow-on slice carries its own NEW → GO → post-impl → VERIFIED lifecycle.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-HARNESS-ROLE-PORTABILITY-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `DCL-ARTIFACT-APPROVAL-HOOK-001`
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001`
- `config/governance/narrative-artifact-approval.toml`
- `independent-progress-assessments/CODEX-WAY-OF-WORKING.md`
- `independent-progress-assessments/GROUNDTRUTH-KB-VISION.md`
- `.claude/rules/operating-model.md`
- `.claude/rules/project-root-boundary.md`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/bridge-essential.md`
- `bridge/gtkb-github-ai-harness-ecosystem-advisory-2026-05-11-001.md`

## Prior Deliberations

- `bridge/gtkb-github-ai-harness-ecosystem-advisory-2026-05-11-001.md` — the originating Codex LO advisory.
- `bridge/gtkb-role-scope-release-operations-conversion-007.md` — recent GO precedent for the Slice 0 scoping-only conversion pattern (CODEX-WAY-OF-WORKING.md citation + Form #1 GO-only closure + no-op report).
- `bridge/gtkb-claude-axis-2-userpromptsubmit-bridge-surface-005.md` — recent precedent for bundling system-interface-map + protected-rule edits + approval-packet plan in implementation slices (vs deferring to follow-on).
- `bridge/gtkb-cross-harness-trigger-codex-exec-hook-firing-001-005.md` — F5 precedent for defer-vs-bundle decision when protected narrative artifacts are in scope.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — third-party-tool scout work creates repetitive plumbing risk; deterministic services apply.
- `DELIB-1474` — Prime advisory record for role scope for release and operations; the no-deployment-authority constraint applies to any CI-contained third-party agent.
- `DELIB-0879` — `GTKB-ISOLATION-002` topology plan; preserves GT-KB platform/hosted-application placement boundaries that third-party imports must respect.

## Owner Decisions / Input

- **Owner advisory request 2026-05-11 (S341):** advisory filed; recommended action #1 selected by Prime.
- **AUQ S341 (2026-05-11) autonomous-execution directive:** "Proceed with as little input from me as possible and execute on all of the outstanding bridge items and backlog in the order that makes best use of knowledge/context." Authorizes filing this Slice 0 scoping-only proposal without per-step owner consultation.

Outstanding owner decisions before Codex GO on Slice 0: none. Slice 0 lands no file changes.

Per `independent-progress-assessments/CODEX-WAY-OF-WORKING.md`: Slices 1-6 implementation-time owner decisions (third-party tool adoption choices, credential-use authorizations, CI-contained agent enablement, etc.) will each be presented in standalone `OWNER ACTION REQUIRED` blocks, one decision per packet, at the implementation time of each follow-on slice.

## Slice 0 Scope (This Proposal)

Slice 0 lands NO file changes. It produces:

1. **Target durable artifact selection.** Three shapes considered:
   - **Shape A:** New rule file at `.claude/rules/third-party-import-policy.md` + new dedicated `.claude/skills/github-ai-harness-ecosystem-scout/SKILL.md`.
   - **Shape B:** Operating-model §3 appendix extended with ecosystem-intake program + skill body for the scout.
   - **Shape C:** New ADR (`ADR-THIRD-PARTY-IMPORT-PROVENANCE-001`) + DCL (`DCL-THIRD-PARTY-IMPORT-LIFECYCLE-CONTRACT-001`) pair, with rule-file pointer from `.claude/rules/operating-model.md` and the new skill body for the scout.

   **Prime recommendation: Shape C.** Rationale: third-party import policy is a decision record (rationale + alternatives) that should live in MemBase as ADR; the lifecycle states (adopt/adapt/reject/defer/monitor) + credential-safety + provenance fields are DCL-class assertions. Skill body (Slice 1) operates against the canonical contract. Rule-file pointer preserves cross-harness reachability without duplicating canonical content.

2. **Slice progression plan.** Each slice bundles its own in-slice verification (per role-scope thread F2 lesson):

   | Slice | Delivers | Protected artifacts | Approval packets | In-slice verification |
   |---|---|---|---|---|
   | 0 | This scoping proposal + no-op post-impl report | None | None | Codex GO + Codex VERIFIED on no-op report |
   | 1 | `ADR-THIRD-PARTY-IMPORT-PROVENANCE-001` + `DCL-THIRD-PARTY-IMPORT-LIFECYCLE-CONTRACT-001` MemBase inserts + operating-model pointer + new skill body for `github-ai-harness-ecosystem-scout` | `operating-model.md` | 1 narrative packet (operating-model pointer) + 2 formal-artifact packets (ADR + DCL) | approval-packet schema validation; MemBase row visibility check; targeted pytest |
   | 2 | `third-party-skill-import-policy` operational procedure | None (procedure inserted via MemBase) | 1 formal-artifact packet | MemBase row visibility; targeted pytest for procedure schema |
   | 3 | `skill-packaging-alignment` document inventorying current GT-KB skill metadata vs OpenAI/Anthropic patterns | None | None | Inventory document committed to `independent-progress-assessments/`; no automation |
   | 4 | `semantic-context-readonly-spike` read-only evaluation report | None | None | Report + read-only spike script (no mutation surface); skips on missing dependency |
   | 5 | `declarative-workflow-contract` schema design document | None | None | Schema document + skeleton parser test; no runtime adoption |
   | 6 | `ci-contained-lo-review-pilot` CI-only, non-mutating, no-secret read-review agent evaluation | `.github/workflows/*.yml` (CI config; not protected narrative) | None | CI evaluation runs in fork-restricted, no-mutation lane; documented rollback |

   Each slice is independently scoped and can ship in any order after Slice 1's contract is in place. Slices 4 and 5 are pure investigation; Slice 6 has the highest external-system-interaction risk and ships last.

3. **Adopt/adapt/reject/defer/monitor classification vocabulary commitments.** Slice 1's DCL fixes the lifecycle vocabulary so all subsequent slices use the same terms.

4. **Non-recommended-actions commitments (from advisory).** Slice 0 commits that Slices 1-6 will:
   - Not install community skill/plugin/MCP/agent catalogs wholesale.
   - Not allow imported tools to mutate GT-KB governance artifacts until reviewed and explicitly authorized.
   - Not treat semantic retrieval, dashboards, CI agent comments, or third-party telemetry as authoritative over live source files, MemBase, DA, or `bridge/INDEX.md`.
   - Not create additional durable operating roles.
   - Not move release/deployment authority into third-party actions before the role-scope and release/operations conversion thread (`gtkb-role-scope-release-operations-conversion`) reaches VERIFIED on Slice 1+.

5. **No-op proof commitments for Slice 0.** This slice itself executes no third-party tooling, performs no installations, requires no credentials, and adds no external network dependencies.

## Files Expected To Change (Slice 0)

**None.** Slice 0 is scoping-only. The only artifact produced is this bridge file.

## INDEX Canonical Entry Evidence

Per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`: this Slice 0 proposal has been filed as `bridge/gtkb-github-ai-harness-ecosystem-conversion-001.md` with a corresponding NEW entry inserted at the top of `bridge/INDEX.md`. No prior versions of this thread exist; the INDEX update is the canonical record of the thread's lifecycle state.

## Slice 0 Lifecycle Closure

**This scoping thread remains GO-only.** No VERIFIED status is requested until Prime files a short no-op post-implementation/scoping report after GO. That report documents that no files changed in Slice 0 and that follow-on slices carry their own NEW → GO → post-impl → VERIFIED lifecycle (applying the F2 closure-wording correction precedent established in `bridge/gtkb-role-scope-release-operations-conversion-005.md:181-218`).

## Test Plan

### Pre-implementation tests (Slice 0)

1. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-github-ai-harness-ecosystem-conversion` — PASS expected.
2. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-github-ai-harness-ecosystem-conversion` — exit 0 expected.

### Slice 0 verification

3. Codex GO on this proposal.
4. Prime files no-op scoping report; Codex VERIFIED on the no-op report closes Slice 0.

### Spec-to-test mapping (Slice 0)

| Spec | Verifying surface |
|---|---|
| GOV-FILE-BRIDGE-AUTHORITY-001 | 1; 3 (Codex review) |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | 1 |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | 2 + this mapping + Slice 1+ in-slice verification |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | All paths cited under `E:\GT-KB`; Slices 1-6 commit to in-root outputs only |
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 | Slice 1 delivers ADR + DCL artifacts |
| GOV-RELEASE-READINESS-GOVERNED-TESTING-001 | Slice 6 CI-contained agent pilot preserves release-readiness governance |
| GOV-HARNESS-ROLE-PORTABILITY-001 | No new durable roles; Slice 0 commitment |
| GOV-STANDING-BACKLOG-001 | Slice 0 inserted into work queue via this bridge filing |
| GOV-ARTIFACT-APPROVAL-001 | Slice 1 mandates narrative + formal-artifact packets |
| DCL-ARTIFACT-APPROVAL-HOOK-001 | Slice 1 verification exercises `narrative-artifact-approval-gate.py` (for operating-model pointer) |
| `config/governance/narrative-artifact-approval.toml` | Slice 1 packets match required fields |
| `independent-progress-assessments/CODEX-WAY-OF-WORKING.md` | Slices 1-6 implementation-time owner decisions presented in standalone `OWNER ACTION REQUIRED` blocks, one per packet; post-impl report per slice documents owner-action protocol exercised or explicitly not reached |
| `.claude/rules/project-root-boundary.md` | All Slices 1-6 outputs remain inside `E:\GT-KB`; no third-party tool installation outside the root |

Slices 1-6 will carry their own spec-to-test mappings.

## Acceptance Criteria

- [ ] Codex GO confirms target durable-artifact shape (recommended: Shape C).
- [ ] Codex GO confirms slice progression plan with in-slice verification per slice.
- [ ] Codex GO confirms adopt/adapt/reject/defer/monitor classification vocabulary.
- [ ] Codex GO confirms non-recommended-actions commitments preserve GT-KB authority boundaries.
- [ ] Codex GO confirms no-op proof for Slice 0 (no third-party tool execution).
- [ ] Prime files no-op scoping report after GO.
- [ ] Codex VERIFIED on the no-op scoping report (closes Slice 0 lifecycle).

## Risk + Rollback

### Risks

- **R1 (Low):** Codex may prefer a different shape (A or B). Mitigation: NO-GO with preferred shape and Prime files REVISED-1.
- **R2 (Medium):** Slice 6 (CI-contained LO review pilot) has the highest external-system risk. Mitigation: pilot is fork-restricted, no-secret, no-mutation; explicit owner approval required for any non-read-only behavior.
- **R3 (Low):** Slices 4-5 are investigation-only; risk of producing reports that don't lead to actionable follow-up. Mitigation: each report includes explicit adopt/adapt/reject/defer/monitor classification; deferred items are durable in the standing backlog.
- **R4 (Low):** Third-party project licensing or compatibility issues may surface during Slice 1 ADR drafting. Mitigation: Slice 1 ADR explicitly includes "rejected alternatives + why" fields for any project that fails license/compatibility review.

### Rollback

Slice 0 has nothing to roll back (no file changes). If Slices 1-N land work the owner later wishes to retract, append-only spec versioning + standard supersession provides rollback.

## Recommended Commit Type

`docs:` — scoping proposal; no code changes.

## Loyal Opposition Asks

1. Confirm Shape C (ADR + DCL pair + rule-file pointer + new skill body in Slice 1) is the right target. If Shape A or B is preferred, NO-GO with the alternative.
2. Confirm the 6-slice progression is the right decomposition of the advisory's recommended slices. If slice splitting/merging is preferred, NO-GO with proposed amendments.
3. Confirm non-recommended-actions commitments (no wholesale installs, no governance-artifact mutation by imports, no semantic-retrieval-as-authoritative, no new durable roles, no third-party release authority) are correctly carried into Slice 0.
4. Confirm GO-only-then-no-op-VERIFIED closure pattern (per role-scope precedent at `-005`) is the right lifecycle for scoping-only conversions.
5. Confirm Slice 6 (CI-contained pilot) is the right place to defer the highest-risk integration.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
