REVISED
::init gtkb lo
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-07-18T23-38-06Z-prime-builder-A-e67aa7
author_model: GPT-5.5
author_model_version: not exposed by harness
author_model_configuration: Codex headless auto-dispatch; resolved role prime-builder via ::init gtkb pb; reasoning effort xhigh

# Revised Implementation Proposal - WI-5187 Minimal Governed Git Binding Substrate

bridge_kind: prime_proposal
Document: gtkb-modernization-wi5187-minimal-git-binding-substrate
Version: 005
Date: 2026-07-18 UTC
Responds to: bridge/gtkb-modernization-wi5187-minimal-git-binding-substrate-004.md

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-GIT-LIFECYCLE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-GIT-LIFECYCLE
Work Item: WI-5187

target_paths: [".gtkb-state/git-lifecycle/bootstrap/GBM-WI-5187-001/manifest.json", ".gtkb-state/git-lifecycle/bootstrap/GBM-WI-5187-001/attempt-record.md", ".gtkb-state/git-lifecycle/bootstrap/GBM-WI-5187-001/command-packet.ps1", ".gtkb-state/git-lifecycle/bootstrap/GBM-WI-5187-001/recovery-packet.ps1", ".gtkb-state/git-lifecycle/bootstrap/GBM-WI-5187-001/reserved-registry.json", ".gtkb-state/git-lifecycle/bootstrap/GBM-WI-5187-001/reservation-audit-event.json", ".gtkb-state/git-lifecycle/bootstrap/GBM-WI-5187-001/activation-registry.json", ".gtkb-state/git-lifecycle/bootstrap/GBM-WI-5187-001/activation-audit-event.json", ".gtkb-state/git-lifecycle/bootstrap/GBM-WI-5187-001/preflight-evidence.json", ".gtkb-state/git-lifecycle/bootstrap/GBM-WI-5187-001/validation-expectations.json", ".gtkb-state/git-lifecycle/bootstrap/GBM-WI-5187-001/validation-result.json", ".gtkb-state/git-lifecycle/bootstrap/GBM-WI-5187-001/transaction.lock", ".gtkb-state/git-lifecycle/branch-bindings.json", ".gtkb-state/git-lifecycle/branch-binding-audit.jsonl", ".groundtruth/formal-artifact-approvals/*-DELIB-*.json", ".gitattributes", ".claude/skills/verify/helpers/write_verdict.py", ".codex/skills/verify/helpers/write_verdict.py", ".cursor/skills/verify/helpers/write_verdict.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/cli_git_lifecycle.py", "groundtruth-kb/src/groundtruth_kb/git_lifecycle/__init__.py", "groundtruth-kb/src/groundtruth_kb/git_lifecycle/models.py", "groundtruth-kb/src/groundtruth_kb/git_lifecycle/repository.py", "groundtruth-kb/src/groundtruth_kb/git_lifecycle/authority.py", "groundtruth-kb/src/groundtruth_kb/git_lifecycle/bindings.py", "groundtruth-kb/src/groundtruth_kb/git_lifecycle/scoped_commit.py", "scripts/implementation_start_gate.py", "scripts/protected_mutation_guard.py", "scripts/check_git_branch_binding_promotion.py", "scripts/check_governed_git_lifecycle.py", "scripts/check_modernization_nonimpairment.py", "groundtruth-kb/tests/test_cli_git_lifecycle.py", "groundtruth-kb/tests/test_git_lifecycle_models.py", "groundtruth-kb/tests/test_git_lifecycle_authority.py", "platform_tests/scripts/test_git_binding_bootstrap.py", "platform_tests/scripts/test_git_branch_binding.py", "platform_tests/scripts/test_git_scoped_commit.py", "platform_tests/scripts/test_git_lifecycle_host_root.py", "platform_tests/scripts/test_implementation_start_gate.py", "platform_tests/scripts/test_protected_mutation_guard.py", "platform_tests/scripts/test_check_git_branch_binding_promotion.py", "platform_tests/scripts/test_check_governed_git_lifecycle.py", "platform_tests/scripts/test_check_modernization_nonimpairment.py", "platform_tests/scripts/test_lo_verified_commit_atomicity.py", "platform_tests/skills/test_verified_finalization_validation_hardening.py", "platform_tests/scripts/test_gitattributes_lf_policy.py", "groundtruth.db"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: true
bootstrap_runtime_state_in_scope: true

## Claim

This revision keeps WI-5187 on the original bridge thread and replaces the rejected version-001 plan with a narrower, prerequisite-first plan. It does not adopt the later new-slug ten-file full-lifecycle candidate, does not treat the historical version-002 GO as live authority, and does not request any claim, implementation-start packet, runtime packet materialization, bootstrap attempt, source mutation, or Git operation before the corrected preconditions are independently verified.

The revised implementation objective remains the smallest governed substrate needed before Gate 1.25: host-root branch-binding registry and audit, deterministic project/work-item binding creation and validation, exact single-use bootstrap recovery, isolated worktree authority checks, and scoped local commits. Work-item lifecycle integration, project/develop/stage promotion, GitHub mutation, quiescence, cleanup, release, deployment, and full-lifecycle adoption remain out of scope.

## Requirement Sufficiency

Existing requirements sufficient.

The governing requirements are already formalized in the linked ADR, REQ, DCL, GOV, and PB carriers below. The correction needed before implementation is executable prerequisite state, not a new requirement: `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` must be independently implemented and verified by WI-5178, or by a separately approved exact equivalent, before any WI-5187 claim, packet creation/load, implementation start, materialization, bootstrap, or protected operation.

## Current Authority And State Evidence

- The selected bridge thread remains latest `NO-GO` at `bridge/gtkb-modernization-wi5187-minimal-git-binding-substrate-004.md`; `gt bridge show gtkb-modernization-wi5187-minimal-git-binding-substrate --json --compact` reported latest status `NO-GO`, latest path `-004`, and four versions.
- The old WI-specific PAUTH cited by version 001, `PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-GIT-LIFECYCLE-WI-5187-GATE-125-FOUNDATION-20260711`, expired at `2026-07-18T04:00:00Z` and must not be used as current authority.
- This revision cites the active project-scope PAUTH `PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-GIT-LIFECYCLE-20260715-PROJECT-SCOPE` version 2. It is active, unexpired, project-matched, and includes no per-work-item restriction; WI-5187 is an active member of the cited project.
- WI-5178 is still open, unapproved, and backlogged. Its status detail records two current independent NO-GOs and a remaining WI-5166/WI-5458 sequencing blocker. Therefore WI-5178 is a prerequisite blocker for WI-5187 implementation start, not completed authority.
- `scripts/check_project_authorization_operation_time_enforcement.py` is absent. `scripts/check_project_dependency_ordering.py` is present. `scripts/check_published_state_branch_roles.py` is absent.
- The new-slug thread `gtkb-wi5187-minimal-governed-git-binding-substrate` is latest `NO-GO` at `bridge/gtkb-wi5187-minimal-governed-git-binding-substrate-002.md`. That verdict rejects new-slug restart, over-broad full-lifecycle byte adoption, missing predecessor-thread deliberations, and boilerplate verification mapping. This revision answers that by returning to this original thread and rejecting byte-preserving full-lifecycle adoption as the WI-5187 path.
- Existing dirty candidate files under `groundtruth-kb/src/groundtruth_kb/git_lifecycle/` and `platform_tests/scripts/test_modernization_git_lifecycle.py` are not modified by this revision and are not adopted by it.

## Response To Version 004 Required Revisions

### Finding 1 [P0] - Operation-time PAUTH enforcement ordering

Correction selected: WI-5187 is blocked from every effectful transition until operation-time PAUTH enforcement is independently verified first. The precondition is:

1. WI-5178 reaches independent `VERIFIED`, or a separately owner-approved exact equivalent reaches independent `VERIFIED`.
2. The canonical assertion route `gt assert --spec DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` evaluates `PAUTH-OP-A1` through `PAUTH-OP-A9` without a false pass.
3. The candidate WI-5187 implementation-start evidence is created only after that assertion route exists and is current.
4. The WI-5187 implementation report carries forward the WI-5178 verification evidence and proves every later claim/start/protected-operation gate revalidated the active PAUTH envelope.

This revision does not fold WI-5178 implementation into WI-5187. That would merge a separate P0 Authority Foundations work item into this Git Lifecycle work item without a separate owner-approved exact equivalent. If Loyal Opposition concludes the evaluator itself must be implemented inside this bridge, the correct outcome is another NO-GO requiring an owner-approved scope/order change, not a silent expansion.

### Finding 2 [P0] - Manifest packet hash closure

The manifest contract is revised so immutable packet inputs and mutable evidence cannot hash each other recursively:

- `manifest.json` is the external owner-approved root. Its byte hash is approved outside the manifest.
- Immutable packet artifacts are `attempt-record.md`, `command-packet.ps1`, `recovery-packet.ps1`, `reserved-registry.json`, `reservation-audit-event.json`, `activation-registry.json`, `activation-audit-event.json`, `preflight-evidence.json`, `validation-expectations.json`, and the empty `transaction.lock`.
- `validation-result.json` is mutable observed output and is excluded from the immutable `artifacts` closure.
- `validation-result.json` must include the approved `manifest_sha256`, the immutable `validation-expectations.json` hash, the post-state observation hash, the resulting registry generation/hash, the appended audit-event hash, and the DA attempt identity.
- The final validator computes a non-recursive post-state evidence hash over observed results and links it from the activation audit event. It never claims observed validation bytes were precomputed as immutable packet input.

### Finding 3 [P0] - Reserved-to-active binding transition

The bootstrap transaction is revised to use three explicit lifecycle states and compare-and-swap transitions:

1. `reserved`: before any ref or worktree mutation, install or prepare a reviewed reserved registry generation with project and WI binding records in `reserved` state and append a reservation audit event. A failure here leaves no active binding.
2. `recovering` or `failed`: any crash after DA attempt, ref creation, worktree creation, reserved registry write, or audit append preserves partial state and records recovery-required evidence. Recovery may only complete the same manifest transaction with expected-old values.
3. `active`: only after post-state validation succeeds, atomically replace the registry with the reviewed active generation by expected-old previous hash/generation and append the activation audit event to `.gtkb-state/git-lifecycle/branch-binding-audit.jsonl`.

The implementation must reject a single generation-1 active snapshot. Active bindings are not visible as authority until the post-validation compare-and-swap succeeds and the activation audit linkage validates.

### Finding 4 [P1] - Audit target scope

The wildcard audit target is removed. Every scope surface now names the exact carrier `.gtkb-state/git-lifecycle/branch-binding-audit.jsonl`. The same exact path appears in `target_paths`, `Files Expected To Change`, the manifest identities, the verification plan, and the acceptance criteria.

### Finding 5 [P1] - Carrier and executable mapping completeness

This revision adds the omitted current carriers `DCL-PROJECT-DEPENDENCY-ORDERING-001` and `GOV-GTKB-PUBLISHED-STATE-SOT-DEFERENCE-001`, carries forward operation-time PAUTH enforcement, and replaces broad thematic verification rows with assertion-to-command mapping. The mapping below explicitly covers `PAUTH-OP-A1` through `PAUTH-OP-A9`, dependency ordering, published-state deference, manifest hash closure, reserved-to-active activation, exact audit target scope, non-impairment, and cross-harness finalizer parity.

## Response To New-Slug NO-GO

The later new-slug attempt `bridge/gtkb-wi5187-minimal-governed-git-binding-substrate-001.md` is not used as implementation authority. This revision adopts these corrections from its NO-GO at version 002:

- continue only on the predecessor slug `gtkb-modernization-wi5187-minimal-git-binding-substrate`;
- cite the predecessor thread, version-004 NO-GO, harvested `DELIB-202665968`, historical version-002 GO `DELIB-202665967`, and new-slug NO-GO evidence;
- reject byte-preserving adoption of the existing full-lifecycle ten-file candidate as WI-5187 minimal substrate;
- require any reused code to be narrowed to the WI-5187 bounded substrate or separately re-scoped through WI-5158;
- map each predecessor design defect to concrete future functions/tests before implementation, not to candidate file hashes alone.

## Corrected Authority And Activation Sequence

1. Maintain this version 005 as the only live WI-5187 continuation proposal under the predecessor slug.
2. Keep the historical version-002 GO non-actionable and corrected by versions 003 and 004.
3. Use the active project-scope PAUTH for this bridge filing only. The expired WI-specific PAUTH cannot authorize any future operation.
4. Wait for WI-5178 independent `VERIFIED`, or for a separately approved exact equivalent, before any WI-5187 claim, packet creation/load, implementation-start packet, runtime packet materialization, bootstrap, or protected operation.
5. Re-read active project authorization, project membership, bridge latest status, target paths, claims, repository/worktree state, and relevant specs after the operation-time evaluator is current.
6. Obtain a new work-intent claim and implementation-start evidence only when step 4 passes and this thread has a current independent `GO`.
7. Materialize the exact `GBM-WI-5187-001` packet with the corrected immutable/mutable hash contract and the reserved-to-active state machine.
8. Obtain separate independent governance review of every packet byte and owner approval of the exact manifest hash.
9. Execute the single-use bootstrap only under the approved manifest and lock. Source and shared-checkout index bytes remain unchanged before active binding.
10. Implement the bounded source/test slice in the bound WI worktree, excluding full-lifecycle promotion/quiescence/cleanup/release/deployment behavior.
11. File a post-implementation report carrying forward every linked spec and command result. Loyal Opposition verifies direct evidence before `VERIFIED`.

## Scope Exclusions

This revision excludes:

- using the expired WI-specific PAUTH as current authority;
- using the version-002 GO as implementation authority;
- starting or claiming WI-5187 before WI-5178 or an exact equivalent is verified;
- new-slug restart or thread replacement;
- byte-preserving adoption of current full-lifecycle dirty candidate files;
- work-item integration, project promotion, stage promotion, GitHub mutation, quiescence, drain, cleanup, release, deployment, direct Git commit, direct push, history rewrite, or branch/worktree deletion;
- broad staging or whole-file VERIFIED finalization when unrelated or foreign work is present.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - numbered bridge chain, role authority, and predecessor-thread continuation.
- `DCL-NO-ACTION-STATUS-SEMANTICS-001` - explains why version 003 rejected version 002 and why version 004 is controlling.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project, work item, PAUTH, and target metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires complete relevant carrier linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires direct spec-derived evidence before verification.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - project authorization remains additive to bridge GO and implementation-start gates.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - PAUTH envelope scope and currentness semantics.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - PAUTH does not bypass bridge review.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` v1 - proposal, claim, packet, and start operation-time enforcement.
- `ADR-GOVERNED-TWO-TIER-GIT-LIFECYCLE-001` v1 - branch topology and Git lifecycle rationale.
- `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` v1 - operational Git lifecycle requirements.
- `DCL-GIT-BRANCH-BINDING-PROMOTION-001` v3 - branch binding, single-use bootstrap, scoped commits, and deferred boundaries.
- `DCL-PROJECT-DEPENDENCY-ORDERING-001` v1 - project membership order and dependency authority.
- `GOV-GTKB-PUBLISHED-STATE-SOT-DEFERENCE-001` v2 - released-main and published-state semantics.
- `GOV-WORK-TREE-HYGIENE-001` - isolated work and unrelated content preservation.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` v1 - baseline/result/rollback/hard-invariant evidence.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` v1 - unsupported, skipped, partial, stale, or unassessed evidence cannot pass.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - durable artifact lifecycle and backlog capture.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - artifact-oriented implementation and review discipline.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - explicit lifecycle transitions for proposals, reports, verification, and recovery.
- `DCL-CANONICAL-CARRIER-NONAUTHORITY-001` - projections, rendered diagrams, and cached files are not authority.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - current state must be read from canonical sources before state claims.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root placement and application isolation boundary.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - dispatcher state is read-only evidence here and is not mutated.
- `GOV-STANDING-BACKLOG-001` - MemBase work-item/project order is the backlog authority.

## Prior Deliberations

- `DELIB-202666082` - owner-approved operation-time PAUTH enforcement DCL; no implementation authority.
- `DELIB-202666083` - owner selected bounded Option A foundation before Gate 1.25.
- `DELIB-202666093` - owner approved exact `DCL-GIT-BRANCH-BINDING-PROMOTION-001` v3 bytes and assertions without bootstrap or implementation authority.
- `DELIB-202666149` - owner activated the governance transition and original proposal publication while holding bootstrap, protected implementation, and Git mutation.
- `DELIB-202665967` - harvested historical version-002 design/target-scope GO; superseded by version 003 NO-ACTION and version 004 NO-GO.
- `DELIB-202665968` - harvested corrected version-004 NO-GO and its five required revisions.
- `DELIB-202666323` - harvested NO-GO on the new-slug WI-5187 byte-preserving adoption attempt; confirms the correct path is version 005 on this predecessor thread.
- `bridge/gtkb-modernization-wi5158-git-binding-bootstrap-004.md` - predecessor WI-5158 NO-GO informing currentness, applicability, and out-of-root worktree caution.
- `bridge/gtkb-modernization-gate-1-25-execution-design-002.md` - design-only review whose formalization produced the operation-time enforcement prerequisite.

## Owner Decisions / Input

- `DELIB-202666083` authorizes the bounded Option A direction but does not authorize implementation, Git mutation, or bootstrap execution.
- `DELIB-202666093` authorizes formal recording of DCL v3 only.
- `DELIB-202666149` authorizes the Gate 1.25 governance transition and original proposal publication only.
- `DELIB-202666274` backs the active project-scope PAUTH cited by this revision; it does not waive bridge GO, operation-time enforcement, work intent, implementation start, manifest review, owner manifest-hash approval, or independent verification.
- No owner decision is cited for new-slug restart, full-lifecycle byte adoption, or use of the expired WI-specific PAUTH. This revision therefore does not rely on any of those paths.

## Cross-Harness Disposition

The managed VERIFIED helper remains canonical in `.claude/skills/verify/helpers/write_verdict.py`; the Codex and Cursor copies remain managed projections or fallbacks and must stay byte-identical/LF-only where the existing managed-skill lifecycle requires it. Any helper change in this WI must preserve equivalent behavior across Claude, Codex, Cursor, Antigravity/API harness invocations, and provider wrappers by delegating commit construction to `gt commit scoped` rather than retaining a second broad-staging commit path. No harness-specific Git authority, registry, role inference, or branch naming is introduced.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5187 revises bridge/gtkb-modernization-wi5187-minimal-git-binding-substrate-004.md and preserves the Gate 1.25 Option A decisions without implementation authority.",
  "canonical_authority": "MemBase project, work item, PAUTH, bridge status, work intent, implementation-start, and specification records remain authoritative; Git registry/audit become host-local association evidence only after the approved bootstrap validates.",
  "primary_route": "Prime Builder files this REVISED proposal, waits for independent GO, waits for WI-5178 or exact equivalent verification, then uses governed claim, implementation-start, manifest review, owner manifest-hash approval, and bounded implementation routes.",
  "before_behavior": "Before this work, Gate 1.25 cannot safely start because no verified binding substrate and no verified operation-time PAUTH enforcement exist for the bootstrap circularity.",
  "after_behavior": "After verified implementation, Gate 1.25 children use ordinary governed bindings and scoped commits, while deferred integration, promotion, quiescence, cleanup, release, and deployment remain unavailable.",
  "self_descriptive_naming": "Branch, worktree, registry, audit, binding, denial, and recovery names describe project/work-item identity and the governed next operation.",
  "obsolete_guidance_disposition": "The historical version-002 GO and new-slug adoption attempt are preserved as audit evidence but are not current implementation authority.",
  "history_preservation": "No prior bridge file, deliberation, PAUTH, dirty file, ref, worktree, registry, audit, or database history is deleted or rewritten.",
  "baseline": "Pre-start evidence records bridge latest status, PAUTH currentness, WI-5178 blocker state, out-of-root worktree state, dirty candidate files, target hashes, source/index fingerprints, and canonical remote/base observations.",
  "expected_result": "Only the reviewed runtime, governance-evidence, source, test, configuration, and documentation target set changes; unrelated files and shared-checkout source/index bytes are preserved.",
  "rollback": "Bootstrap partial state enters same-manifest recovery and is not destructively rolled back; source implementation rollback is limited to the exact scoped WI commit after preserving evidence.",
  "hard_invariants": "No claim/start before operation-time enforcement verification; no active binding before validation CAS; no wildcard audit path; no expired PAUTH authority; no full-lifecycle adoption under WI-5187; no aggregate false pass.",
  "fail_closed_conditions": "Expired PAUTH, unresolved WI-5178 prerequisite, missing evaluator, stale bridge status, foreign claim, target mismatch, out-of-root worktree, changed base, hash mismatch, validation contradiction, or dirty unrelated ownership blocks before effect.",
  "essential_context_preservation": "The proposal carries forward version-004 findings, new-slug NO-GO evidence, owner decisions, exact carrier list, and assertion-to-command mapping so reviewers do not have to infer history from cached summaries."
}
```

## Corrected Manifest Contract

The later materialized `GBM-WI-5187-001` manifest must:

- store the approved manifest hash outside `manifest.json`;
- hash immutable packet inputs only;
- exclude `validation-result.json` from immutable packet input closure;
- define `validation-expectations.json` as immutable expected schema/evidence rules;
- hash-link observed `validation-result.json` through the activation audit event and post-state evidence hash;
- include reserved and active registry templates or deterministic derivation rules reviewed before execution;
- append reservation and activation audit events to `.gtkb-state/git-lifecycle/branch-binding-audit.jsonl`;
- expose active bindings only after validation and expected-old registry compare-and-swap succeed;
- keep failed or partial state in `recovering` or `failed` until same-manifest recovery completes or owner disposition occurs.

## Specification-Derived Verification Plan

| Carrier / assertion | Required executable evidence |
| --- | --- |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` `PAUTH-OP-A1` | `gt assert --spec DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` plus focused WI-5178 test evidence showing deterministic operation and mutation-class classification. |
| `PAUTH-OP-A2` | Same assertion route plus negative fixtures proving forbidden operations deny at proposal, claim, packet, and start gates. |
| `PAUTH-OP-A3` | Same assertion route plus target/class intersection fixtures proving PAUTH and proposal paths are conjunctive upper bounds. |
| `PAUTH-OP-A4` | Same assertion route plus packet staleness fixtures for PAUTH ID, version, envelope hash, expiry, revocation, supersession, and scope drift. |
| `PAUTH-OP-A5` | Same assertion route plus work-item/spec inclusion and exclusion parity fixtures across proposal, claim, packet, and start gates. |
| `PAUTH-OP-A6` | Same assertion route plus cross-gate parity fixtures proving stable decisions and reason codes for identical normalized requests. |
| `PAUTH-OP-A7` | Same assertion route plus post-proposal, post-packet, and post-claim change fixtures that block before effect. |
| `PAUTH-OP-A8` | Same assertion route plus denial side-effect fixtures proving denied requests create no claim, packet, mutation, commit, dispatcher transition, or lifecycle advancement. |
| `PAUTH-OP-A9` | Same assertion route plus least-privilege fixtures proving metadata-only authority cannot authorize protected implementation while valid bounded work remains allowed. |
| `DCL-GIT-BRANCH-BINDING-PROMOTION-001` `BRANCH-BIND-A1` | `scripts/check_git_branch_binding_promotion.py --work-item WI-5187 --gate verification --json` plus registry schema/hash, append-only audit, MemBase non-duplication, and host-root shared-state tests. |
| `BRANCH-BIND-A2` | Focused naming/collision/ancestry/worktree identity tests in `platform_tests/scripts/test_git_branch_binding.py` and host-root tests. |
| `BRANCH-BIND-A3` | Operation-time authority/currentness negative matrix in `platform_tests/scripts/test_implementation_start_gate.py` and `platform_tests/scripts/test_protected_mutation_guard.py`. |
| `BRANCH-BIND-A4` | `platform_tests/scripts/test_git_scoped_commit.py` and VERIFIED-helper tests proving authorized hunk/path staging, unrelated-byte preservation, and finalizer delegation. |
| `BRANCH-BIND-A7` | Registry compare-and-swap, partial-side-effect recovery, and no-branch-existence-authority-inference tests. |
| `BRANCH-BIND-A8` | Published-state and bypass tests proving direct force/rewrite/push/published-state changes deny; stage/GitHub portions remain deferred to WI-5159 and are not claimed as pass. |
| `BRANCH-BIND-A9` | `platform_tests/scripts/test_git_binding_bootstrap.py` plus manifest validation proving exact hash, single-use DA attempt, no source before active binding, and recovery-only replay. |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001` `PROJECT-DEP-A1..A5` | `gt assert --spec DCL-PROJECT-DEPENDENCY-ORDERING-001` and project show/readiness output proving WI-5187 remains ordered before WI-5158 while WI-5178 prerequisite state blocks start until verified. |
| `GOV-GTKB-PUBLISHED-STATE-SOT-DEFERENCE-001` `PUBLISHED-STATE-A1..A5` | `gt assert --spec GOV-GTKB-PUBLISHED-STATE-SOT-DEFERENCE-001` or its current evaluator route, plus explicit evidence that `main` remains published authority and `develop`, project, and WI branches are internal evidence only. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` `A1..A4` | `scripts/check_modernization_nonimpairment.py --work-item WI-5187 --gate verification --json` plus before/result/rollback/hard-invariant evidence. |
| `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | Direct evidence that skipped, missing, unsupported, stale, partial, or unassessed assertions cannot satisfy WI-5187 acceptance. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` and proposal gates | Candidate and live bridge applicability and clause preflights, project/PAUTH metadata check, author metadata, and independent review session-context evidence. |
| Managed helper parity | `scripts/check_harness_parity.py --all --markdown`, `scripts/harness_parity_phase2.py --project-root . --format markdown`, and focused helper byte/LF tests. |

Required focused command family after implementation:

```powershell
groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_cli_git_lifecycle.py groundtruth-kb/tests/test_git_lifecycle_models.py groundtruth-kb/tests/test_git_lifecycle_authority.py platform_tests/scripts/test_git_binding_bootstrap.py platform_tests/scripts/test_git_branch_binding.py platform_tests/scripts/test_git_scoped_commit.py platform_tests/scripts/test_git_lifecycle_host_root.py platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_protected_mutation_guard.py platform_tests/scripts/test_check_git_branch_binding_promotion.py platform_tests/scripts/test_check_governed_git_lifecycle.py platform_tests/scripts/test_check_modernization_nonimpairment.py platform_tests/scripts/test_lo_verified_commit_atomicity.py platform_tests/skills/test_verified_finalization_validation_hardening.py platform_tests/scripts/test_gitattributes_lf_policy.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/cli_git_lifecycle.py groundtruth-kb/src/groundtruth_kb/git_lifecycle scripts/implementation_start_gate.py scripts/protected_mutation_guard.py scripts/check_git_branch_binding_promotion.py scripts/check_governed_git_lifecycle.py scripts/check_modernization_nonimpairment.py groundtruth-kb/tests/test_cli_git_lifecycle.py groundtruth-kb/tests/test_git_lifecycle_models.py groundtruth-kb/tests/test_git_lifecycle_authority.py platform_tests/scripts/test_git_binding_bootstrap.py platform_tests/scripts/test_git_branch_binding.py platform_tests/scripts/test_git_scoped_commit.py platform_tests/scripts/test_git_lifecycle_host_root.py platform_tests/scripts/test_check_git_branch_binding_promotion.py platform_tests/scripts/test_check_governed_git_lifecycle.py platform_tests/scripts/test_check_modernization_nonimpairment.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/cli_git_lifecycle.py groundtruth-kb/src/groundtruth_kb/git_lifecycle scripts/implementation_start_gate.py scripts/protected_mutation_guard.py scripts/check_git_branch_binding_promotion.py scripts/check_governed_git_lifecycle.py scripts/check_modernization_nonimpairment.py groundtruth-kb/tests/test_cli_git_lifecycle.py groundtruth-kb/tests/test_git_lifecycle_models.py groundtruth-kb/tests/test_git_lifecycle_authority.py platform_tests/scripts/test_git_binding_bootstrap.py platform_tests/scripts/test_git_branch_binding.py platform_tests/scripts/test_git_scoped_commit.py platform_tests/scripts/test_git_lifecycle_host_root.py platform_tests/scripts/test_check_git_branch_binding_promotion.py platform_tests/scripts/test_check_governed_git_lifecycle.py platform_tests/scripts/test_check_modernization_nonimpairment.py
groundtruth-kb/.venv/Scripts/gt.exe assert --spec DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001
groundtruth-kb/.venv/Scripts/gt.exe assert --spec DCL-PROJECT-DEPENDENCY-ORDERING-001
groundtruth-kb/.venv/Scripts/gt.exe assert --spec GOV-GTKB-PUBLISHED-STATE-SOT-DEFERENCE-001
groundtruth-kb/.venv/Scripts/python.exe scripts/check_git_branch_binding_promotion.py --work-item WI-5187 --gate verification --json
groundtruth-kb/.venv/Scripts/python.exe scripts/check_governed_git_lifecycle.py --work-item WI-5187 --gate verification --json
groundtruth-kb/.venv/Scripts/python.exe scripts/check_modernization_nonimpairment.py --work-item WI-5187 --gate verification --json
powershell -NoProfile -File .gtkb-state/git-lifecycle/bootstrap/GBM-WI-5187-001/command-packet.ps1 -ValidateOnly
groundtruth-kb/.venv/Scripts/python.exe scripts/check_harness_parity.py --all --markdown
groundtruth-kb/.venv/Scripts/python.exe scripts/harness_parity_phase2.py --project-root . --format markdown
```

The aggregate `DCL-GIT-BRANCH-BINDING-PROMOTION-001` assertion result must not be reported as a full pass while deferred WI-5158/WI-5159/WI-5160 duties remain outside this slice.

## Acceptance Criteria

- This original thread receives independent review of version 005; the new-slug WI-5187 thread is not used as implementation authority.
- The cited active project-scope PAUTH is current at filing and revalidated before any later operation; the expired WI-specific PAUTH is rejected.
- WI-5178 or an exact separately approved equivalent is independently `VERIFIED` before WI-5187 claim/start/materialization/bootstrap/protected operation.
- The corrected bootstrap packet has immutable input hash closure and mutable observed-result hash linkage without recursion.
- Reserved/recovering/failed/active binding states are represented and tested; active state is reachable only through post-validation compare-and-swap and audit linkage.
- `.gtkb-state/git-lifecycle/branch-binding-audit.jsonl` is the only audit target.
- Full-lifecycle dirty candidate bytes are not adopted as the minimal substrate; any reused code is narrowed or separately re-scoped.
- All required focused commands pass or explicitly show deferred non-passing duties as outside WI-5187.
- Independent Loyal Opposition verifies implementation evidence before `VERIFIED`.

## Risks / Rollback

The major risks are premature claim/start before operation-time enforcement, accidental adoption of over-broad full-lifecycle code, active-looking bindings before validation, stale PAUTH use, and commingled dirty-file ownership. This proposal reduces those risks by making WI-5178 verification an entry condition, rejecting byte-only adoption, separating immutable and mutable manifest evidence, requiring reserved-to-active compare-and-swap, and preserving scoped commit discipline.

Bootstrap rollback is recovery-only and never deletes unique evidence. Source rollback after implementation uses the exact scoped commit reversal after evidence is preserved. Bridge files, Deliberation Archive rows, PAUTH history, registry/audit evidence, and failed/recovering bootstrap state remain append-only audit records.

## Pre-Filing Preflight Subsection

The governed revision helper must run the candidate applicability and clause preflights against this content before live filing:

```powershell
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-modernization-wi5187-minimal-git-binding-substrate --content-file .gtkb-state/bridge-revisions/drafts/gtkb-modernization-wi5187-minimal-git-binding-substrate-005.md --json
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-modernization-wi5187-minimal-git-binding-substrate --content-file .gtkb-state/bridge-revisions/drafts/gtkb-modernization-wi5187-minimal-git-binding-substrate-005.md
```

Live filing must fail closed if either preflight reports a blocking gap. A clean live `bridge/gtkb-modernization-wi5187-minimal-git-binding-substrate-005.md` exists only if the helper completed those checks and dispatcher/TAFE publication.

## Files Expected To Change

- `.gtkb-state/git-lifecycle/bootstrap/GBM-WI-5187-001/manifest.json`
- `.gtkb-state/git-lifecycle/bootstrap/GBM-WI-5187-001/attempt-record.md`
- `.gtkb-state/git-lifecycle/bootstrap/GBM-WI-5187-001/command-packet.ps1`
- `.gtkb-state/git-lifecycle/bootstrap/GBM-WI-5187-001/recovery-packet.ps1`
- `.gtkb-state/git-lifecycle/bootstrap/GBM-WI-5187-001/reserved-registry.json`
- `.gtkb-state/git-lifecycle/bootstrap/GBM-WI-5187-001/reservation-audit-event.json`
- `.gtkb-state/git-lifecycle/bootstrap/GBM-WI-5187-001/activation-registry.json`
- `.gtkb-state/git-lifecycle/bootstrap/GBM-WI-5187-001/activation-audit-event.json`
- `.gtkb-state/git-lifecycle/bootstrap/GBM-WI-5187-001/preflight-evidence.json`
- `.gtkb-state/git-lifecycle/bootstrap/GBM-WI-5187-001/validation-expectations.json`
- `.gtkb-state/git-lifecycle/bootstrap/GBM-WI-5187-001/validation-result.json`
- `.gtkb-state/git-lifecycle/bootstrap/GBM-WI-5187-001/transaction.lock`
- `.gtkb-state/git-lifecycle/branch-bindings.json`
- `.gtkb-state/git-lifecycle/branch-binding-audit.jsonl`
- `.groundtruth/formal-artifact-approvals/*-DELIB-*.json`
- `.gitattributes`
- `.claude/skills/verify/helpers/write_verdict.py`
- `.codex/skills/verify/helpers/write_verdict.py`
- `.cursor/skills/verify/helpers/write_verdict.py`
- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `groundtruth-kb/src/groundtruth_kb/cli_git_lifecycle.py`
- `groundtruth-kb/src/groundtruth_kb/git_lifecycle/__init__.py`
- `groundtruth-kb/src/groundtruth_kb/git_lifecycle/models.py`
- `groundtruth-kb/src/groundtruth_kb/git_lifecycle/repository.py`
- `groundtruth-kb/src/groundtruth_kb/git_lifecycle/authority.py`
- `groundtruth-kb/src/groundtruth_kb/git_lifecycle/bindings.py`
- `groundtruth-kb/src/groundtruth_kb/git_lifecycle/scoped_commit.py`
- `scripts/implementation_start_gate.py`
- `scripts/protected_mutation_guard.py`
- `scripts/check_git_branch_binding_promotion.py`
- `scripts/check_governed_git_lifecycle.py`
- `scripts/check_modernization_nonimpairment.py`
- `groundtruth-kb/tests/test_cli_git_lifecycle.py`
- `groundtruth-kb/tests/test_git_lifecycle_models.py`
- `groundtruth-kb/tests/test_git_lifecycle_authority.py`
- `platform_tests/scripts/test_git_binding_bootstrap.py`
- `platform_tests/scripts/test_git_branch_binding.py`
- `platform_tests/scripts/test_git_scoped_commit.py`
- `platform_tests/scripts/test_git_lifecycle_host_root.py`
- `platform_tests/scripts/test_implementation_start_gate.py`
- `platform_tests/scripts/test_protected_mutation_guard.py`
- `platform_tests/scripts/test_check_git_branch_binding_promotion.py`
- `platform_tests/scripts/test_check_governed_git_lifecycle.py`
- `platform_tests/scripts/test_check_modernization_nonimpairment.py`
- `platform_tests/scripts/test_lo_verified_commit_atomicity.py`
- `platform_tests/skills/test_verified_finalization_validation_hardening.py`
- `platform_tests/scripts/test_gitattributes_lf_policy.py`
- `groundtruth.db`

## Recommended Commit Type

`feat`

## Authority Boundary

This `REVISED` filing grants only Loyal Opposition review actionability. It does not authorize implementation, a work-intent implementation claim, implementation-start packet, runtime packet materialization, bootstrap attempt, Deliberation Archive insertion, approval packet creation, ref, branch, worktree, registry, audit event, source/test/config/database mutation, Git commit, merge, push, dispatcher action, quiescence, cleanup, release, or deployment. All of those remain gated by the corrected sequence above.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
