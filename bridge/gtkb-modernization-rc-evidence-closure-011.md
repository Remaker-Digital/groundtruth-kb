REVISED

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6610-1bc5-7781-88bf-900dccbc6010
author_model: GPT-5
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript override ::init gtkb pb; owner-authorized bounded WI-5165 closure correction

# Revised Implementation Proposal - Modernization RC Evidence Closure Correction

bridge_kind: prime_proposal
Document: gtkb-modernization-rc-evidence-closure
Version: 011
Responds to: bridge/gtkb-modernization-rc-evidence-closure-010.md

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-WI-5165-RC-BLOCKER-REPAIR-20260715
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5165

target_paths: ["scripts/collect_modernization_semantic_evidence.py", "independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-MODERNIZATION-RC-EVIDENCE-CLOSURE-2026-07-15.md"]

implementation_scope: source_format_and_governance_evidence
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Claim

This revision addresses both P1 findings in version 010 without rerunning, deleting, rewriting, or promoting the append-only collector invocation. It proposes one format-only source correction and one durable in-root evidence carrier. Owner-authorized PAUTH version 2 permits the exact local atomic VERIFIED-finalizer commit while continuing to forbid push, deployment, release, history rewrite, unrelated mutation, and external-system action.

No protected target mutation may begin until this exact revision receives a fresh independent GO, the Prime Builder holds the matching work-intent claim, and `scripts/implementation_authorization.py begin` authorizes these exact two paths.

## Findings Addressed

### P1 - Required source-format verification failed

Addressed by adding only `scripts/collect_modernization_semantic_evidence.py` to the correction scope. After GO, Prime Builder will record the pre-format source SHA-256 and normalized Python AST digest, run Ruff formatter once on this file, and require the post-format normalized AST digest to be identical. The collector operation will not be rerun. Ruff check and Ruff format-check must then pass, and the existing focused collector test suite must pass.

### P1 - Current PAUTH forbids mandatory VERIFIED finalization

Addressed by owner decision `DELIB-20260715-WI5165-BOUNDED-CLOSURE-CORRECTION-AUTHORIZATION` and PAUTH version 2, rowid 706. Version 2 removes `git_commit` from the forbidden-operation list only for the exact local finalizer transaction defined in its scope; `git_push`, `git_history_rewrite`, deployment, release, external-system mutation, destructive cleanup, and credential lifecycle remain forbidden.

The durable evidence carrier is exactly `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-MODERNIZATION-RC-EVIDENCE-CLOSURE-2026-07-15.md`. It will identify invocation `20260715163526-76461cb465c3`, list and hash the 13 current receipt files, record the 944 collector-output and 83 focused-test-output counts, preserve the `COLLECTED=13 BLOCKED=12 INVALID=1` result, enumerate all 13 residual assertions, and cite the exact verification commands. Transient `.gtkb-state/mrc-pytest` content will not be committed.

If version 012 is an independent GO, the exact prospective same-transaction finalizer include set is:

- `scripts/collect_modernization_semantic_evidence.py`
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-MODERNIZATION-RC-EVIDENCE-CLOSURE-2026-07-15.md`
- `bridge/gtkb-modernization-rc-evidence-closure-013.md` (the post-implementation report)
- `bridge/gtkb-modernization-rc-evidence-closure-014.md` (the finalizer-created VERIFIED verdict)

Any intervening version, different verdict, different path, staged foreign path, or finalizer failure invalidates that include set and fails closed. Prime Builder will not author the VERIFIED verdict or create the final commit.

## Requirement Sufficiency

Existing requirements plus the new owner decision are sufficient. The revision changes no modernization acceptance requirement and grants no waiver. It corrects the failed formatting gate and makes the completed runtime collection durably reviewable under the mandatory atomic VERIFIED contract.

## Owner Decisions / Input

- `DELIB-20260715-WI5165-BOUNDED-CLOSURE-CORRECTION-AUTHORIZATION` - Mike authorizes the format-only collector correction, one durable evidence carrier, and one exact local atomic VERIFIED-finalizer commit. It explicitly excludes collector rerun or deletion, unrelated mutation, broad staging, push, deployment, release, credentials, dispatcher/harness/routing changes, database changes, and external-system action.
- PAUTH `PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-WI-5165-RC-BLOCKER-REPAIR-20260715` version 2, rowid 706 - operation-time authority implementing that bounded decision.

## Proposed Operation

1. Require latest bridge status GO on version 012, exact approved revision 011, matching claim, PAUTH version 2, and an implementation-start packet for the two declared targets.
2. Record source SHA-256 and normalized AST digest, format the collector source once with Ruff, and require AST-digest identity.
3. Build the durable evidence carrier from the existing invocation and current read-only verification results. Do not rerun the collector.
4. Run the complete specification-derived verification matrix below.
5. File the governed post-implementation report at version 013 only if the expected version sequence remains exact.
6. Leave positive terminal finalization to independent Loyal Opposition through `write_verdict.py --finalize-verified` with the exact four-path include set above.

## Hard Invariants And Exclusions

- No collector `all` run, receipt issuance, deletion, rewrite, copy-forward, backdating, or status promotion.
- No semantic source change; normalized AST digest must remain identical across Ruff formatting.
- No mutation outside the two target paths before the implementation report is filed.
- No source/test/config/database/MemBase mutation beyond the one format-only source target.
- No dispatcher, TAFE, harness, routing, role, eligibility, lease, lock, credential, deployment, release, external-system, Git-history, push, or broad-staging mutation.
- Preserve every unrelated dirty and untracked worktree path.
- No synthetic live-harness, activation, pilot, operational, clean-run, or independent-verification evidence.
- The 13 unavailable assertions remain explicit blockers; this correction does not claim modernization program closure.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "DELIB-20260715-WI5165-BOUNDED-CLOSURE-CORRECTION-AUTHORIZATION and PAUTH version 2",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001; DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001; WI-5165",
  "primary_route": "Apply Ruff formatting without AST change and commit a durable summary of the already-completed collection through the atomic VERIFIED finalizer.",
  "before_behavior": "The completed collection is represented by ignored runtime outputs and report 009; the collector source fails Ruff format-check and PAUTH version 1 forbids the finalizer commit.",
  "after_behavior": "Collector behavior is unchanged, Ruff format-check passes, a durable evidence carrier represents the collection, and PAUTH version 2 permits only the exact local finalizer transaction.",
  "self_descriptive_naming": "The durable carrier name identifies GT-KB modernization RC evidence closure and its collection date; the collector source retains its canonical command name.",
  "obsolete_guidance_disposition": "Version 010's two findings remain authoritative until this correction is independently verified; PAUTH version 1 and report 009 are preserved as superseded history, not reused as closure authority.",
  "history_preservation": "Existing receipt, bridge, Git, and deliberation history remains append-only.",
  "baseline": {
    "collector_invocation": "20260715163526-76461cb465c3",
    "semantic_status": "COLLECTED=13 BLOCKED=12 INVALID=1",
    "collector_output_files": 944,
    "focused_test_output_files": 83,
    "ruff_format_check": "FAIL: one unmodified source file would be reformatted",
    "pauth_version": 2
  },
  "expected_result": {
    "source": "Ruff-formatted with identical normalized AST digest",
    "carrier": "One durable report containing exact receipt hashes, counts, status, blockers, and verification commands",
    "finalization": "One independent exact-path local VERIFIED-finalizer commit, with no push, deployment, or release"
  },
  "hard_invariants": [
    "Do not rerun or delete the append-only collector invocation.",
    "Do not change the collector's normalized Python AST.",
    "Do not mutate outside the two declared target paths before the implementation report.",
    "Do not synthesize evidence or conceal the 13 residual assertion failures.",
    "Do not stage or commit any path outside the exact four-path finalizer set."
  ],
  "rollback": {
    "instructions": "Before terminal commit, revert only the format-only source delta and remove only the newly created evidence carrier under separately governed correction authority; never delete runtime receipts or bridge history.",
    "test": "Recompute normalized AST identity, collector status, focused tests, Ruff gates, clean-suite semantics, and Git-lifecycle checks."
  },
  "fail_closed_conditions": [
    "Missing fresh GO, claim, or implementation-start packet.",
    "Target-path or PAUTH-version drift.",
    "Normalized AST digest changes.",
    "Ruff or focused tests fail.",
    "Receipt hashes, invocation counts, semantic status, or residual blocker set differ from the carrier.",
    "Expected bridge version sequence or finalizer include set changes.",
    "Any foreign staged path or finalizer failure."
  ],
  "essential_context_preservation": "The carrier preserves invocation identity, receipt integrity, objective results, unresolved assertions, source-format correction evidence, PAUTH authority, and independent finalization requirements without treating transient test output as a durable artifact."
}
```

## Specification Links

- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - format-only non-impairment and honest residual blockers.
- `DCL-GIT-BRANCH-BINDING-PROMOTION-001` - no synthetic Git evidence and exact local finalization scope.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` - executable verification gates.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - role-correct numbered revision and independent verdict authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - concrete requirement linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - every carried requirement receives executed evidence before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - PAUTH, project, work item, and exact target paths.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - bounded PAUTH version 2.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - fresh operation-time authorization.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - owner decision and exact authority envelope.
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` - unchanged linked specification membership.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - GO, claim, packet, and exact path bounds.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - durable, reviewable evidence carrier.
- `DCL-PROJECT-DEPENDENCY-ORDERING-001` - correction remains subordinate to WI-5165 and does not claim program closure.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - append-only decision, proposal, report, and evidence lifecycle.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - both targets are in `E:\GT-KB` and outside adopter scope.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - helper-mediated Codex bridge filing.
- `DCL-NO-ACTION-STATUS-SEMANTICS-001` - prior stale GO history remains preserved and non-operative.

## Prior Deliberations

- `DELIB-20260715-WI5165-BOUNDED-CLOSURE-CORRECTION-AUTHORIZATION` - exact owner authorization for this correction and finalizer scope.
- `DELIB-20260710-GTKB-MODERNIZATION-NONIMPAIRMENT-GOV-FORMALIZATION-RESULT` - modernization non-impairment authority.
- `DELIB-20260710-GTKB-MODERNIZATION-GATE-1-READINESS-AUTHORIZATION` - Gate 1 readiness authorization.
- `DELIB-20260619-VERIFIED-COMMIT-FINALIZATION-OWNER-DIRECTIVE` - atomic VERIFIED finalization authority.
- `DELIB-20260712-WI5210-HUNK-SCOPED-FINALIZATION-WAIVER` - precedent for exact-path local finalization while preserving unrelated worktree content.
- `bridge/gtkb-modernization-rc-evidence-closure-007.md` through `-010.md` - approved collection scope, GO, implementation report, and current NO-GO findings.

## Pre-Filing Preflight Subsection

- Candidate applicability preflight: PASS; `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`, and `blocking_errors: []`.
- Candidate mandatory clause preflight: PASS; 5 clauses evaluated, 4 `must_apply`, 1 `may_apply`, 0 evidence gaps in `must_apply`, and 0 blocking gaps.
- Live filing must use `revise_bridge.py file`, which reruns both candidate preflights and rejects placeholders, stale version state, credential findings, and target collisions.

## Specification-Derived Verification Plan

| Governing requirement | Deterministic command or evidence | Required result |
| --- | --- | --- |
| Format-only non-impairment | Record SHA-256 and normalized `ast.dump(..., include_attributes=False)` digest before formatting; run `python -m ruff format scripts/collect_modernization_semantic_evidence.py`; recompute AST digest | Source bytes may change only by formatting; normalized AST digest identical |
| Source quality | `python -m ruff check scripts/collect_modernization_semantic_evidence.py` and `python -m ruff format --check scripts/collect_modernization_semantic_evidence.py` | PASS |
| Fixed-plan collector coverage | `python -m pytest platform_tests/scripts/test_collect_modernization_semantic_evidence.py -q --tb=short --basetemp .gtkb-state/mrc-pytest/closure-correction-20260715` | PASS; runtime output only |
| Current receipt validity | `python scripts/collect_modernization_semantic_evidence.py --json status` | Expected nonzero status with `COLLECTED=13 BLOCKED=12 INVALID=1`, exact invocation receipts, reviewed HEAD and scope digest |
| Honest clean-suite blockers | `python scripts/check_modernization_scope_semantics.py run --phase clean-suite --json` | No new impairment; exact 13 residual assertion failures reported |
| Git-lifecycle non-synthesis | `python scripts/check_modernization_git_lifecycle.py --json` | All existing Git lifecycle assertions pass; no pilot artifact created |
| Durable carrier integrity | Hash all 13 invocation receipt files, count all invocation files and focused-test files, then compare the carrier to live runtime state | 13 receipt hashes, 944 collector files, 83 original focused-test files, and residual statuses agree |
| Exact source delta | `git diff --no-index` against a pre-format in-memory or runtime-state snapshot plus `git diff --check -- scripts/collect_modernization_semantic_evidence.py` | Formatting-only delta; no whitespace errors |
| Governance | Candidate and live applicability/clause preflights; claim status; implementation-start packet; PAUTH v2 readback | PASS |
| Atomic finalization | Loyal Opposition `write_verdict.py --finalize-verified` with only the four declared include paths | One local commit; no foreign staged path, push, deployment, or release |

## Acceptance Criteria

- Fresh GO, matching claim, PAUTH version 2, and exact implementation-start packet precede both target mutations.
- Collector normalized AST digest is unchanged and both Ruff gates pass.
- Focused collector tests pass without source/test mutation outside scope.
- The durable carrier exactly represents the existing invocation, receipt hashes, counts, status, and residual blockers.
- The collector is not rerun and no existing receipt or test output is deleted or rewritten.
- The post-implementation report names every target change and the exact finalizer include set.
- Terminal VERIFIED, if warranted, is authored independently and created only by the atomic finalizer in the exact four-path local commit.

## Risk And Rollback

Risk is low for runtime behavior because Ruff formatting must preserve normalized AST identity, but governance risk is high if the atomic commit captures foreign work. The exact include set, clean staging precondition, and fail-closed finalizer contain that risk. No rollback may delete append-only evidence or bridge history; a failed correction requires another governed numbered response.

## Recommended Commit Type

`chore(governance): verify modernization RC evidence closure correction`
