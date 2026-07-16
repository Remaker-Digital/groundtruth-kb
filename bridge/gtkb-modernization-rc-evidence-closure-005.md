REVISED

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6610-1bc5-7781-88bf-900dccbc6010
author_model: GPT-5
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript override ::init gtkb pb; governed bridge drain

# Revised Implementation Proposal - Modernization RC Evidence Closure

bridge_kind: prime_proposal
Document: gtkb-modernization-rc-evidence-closure
Version: 005
Responds to: bridge/gtkb-modernization-rc-evidence-closure-004.md
Supersedes authority from: bridge/gtkb-modernization-rc-evidence-closure-001.md and bridge/gtkb-modernization-rc-evidence-closure-002.md

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-WI-5165-RC-BLOCKER-REPAIR-20260715
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5165

target_paths: [".gtkb-state/modernization-release-candidate/semantic-evidence/issues/predecessor-reconciliation", ".gtkb-state/modernization-release-candidate/semantic-evidence/issues/program-closure", ".gtkb-state/modernization-release-candidate/semantic-evidence/issues/authority-carrier-classification", ".gtkb-state/modernization-release-candidate/semantic-evidence/issues/artifact-cleanup-batches", ".gtkb-state/modernization-release-candidate/semantic-evidence/issues/semantic-guidance-cleanup", ".gtkb-state/modernization-release-candidate/semantic-evidence/issues/lifecycle-state-reconciliation", ".gtkb-state/modernization-release-candidate/semantic-evidence/issues/work-item-advisory-deduplication", ".gtkb-state/modernization-release-candidate/semantic-evidence/issues/runtime-interface-inventory", ".gtkb-state/modernization-release-candidate/semantic-evidence/issues/harness-claude-live", ".gtkb-state/modernization-release-candidate/semantic-evidence/issues/harness-codex-live", ".gtkb-state/modernization-release-candidate/semantic-evidence/issues/harness-cursor-live", ".gtkb-state/modernization-release-candidate/semantic-evidence/issues/harness-antigravity-optimized-startup", ".gtkb-state/modernization-release-candidate/semantic-evidence/issues/headless-provider-conformance", ".gtkb-state/modernization-release-candidate/semantic-evidence/issues/cross-harness-confusion-corpus", ".gtkb-state/modernization-release-candidate/semantic-evidence/issues/pre-modernization-baseline", ".gtkb-state/modernization-release-candidate/semantic-evidence/issues/seven-category-scenario-matrix", ".gtkb-state/modernization-release-candidate/semantic-evidence/issues/six-activity-behavior-matrix", ".gtkb-state/modernization-release-candidate/semantic-evidence/issues/role-harness-session-branch-scenarios", ".gtkb-state/modernization-release-candidate/semantic-evidence/issues/confusion-regression-fixtures", ".gtkb-state/modernization-release-candidate/semantic-evidence/issues/nonimpairment-orchestrator", ".gtkb-state/modernization-release-candidate/semantic-evidence/issues/modernization-measurements", ".gtkb-state/modernization-release-candidate/semantic-evidence/issues/shadow-six-activities-primary-harnesses", ".gtkb-state/modernization-release-candidate/semantic-evidence/issues/activation-thresholds", ".gtkb-state/modernization-release-candidate/semantic-evidence/issues/reversible-activation-slices", ".gtkb-state/modernization-release-candidate/semantic-evidence/issues/operational-observation", ".gtkb-state/modernization-release-candidate/semantic-evidence/issues/independent-verification", ".gtkb-state/modernization-release-candidate/semantic-evidence/command-runs", ".gtkb-state/mrc-pytest"]

implementation_scope: governance_evidence
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Claim

This proposal replaces the stale version-001 baseline and incomplete target inventory. It authorizes one bounded invocation of the existing read/measure/append collector over its fixed 26-plan registry, with the exact 26 potential receipt roots plus the two bounded runtime-output roots used by collector subprocesses.

The collector may append a receipt only after an objective-specific measurement succeeds. Missing live sessions, clean runs, independent audits, activation evidence, or pilot observations remain `BLOCKED`; they are not written as passing evidence. Existing receipt history is never rewritten or deleted.

## Current Baseline

- Git HEAD observed by the collector: `ea8dad56fb0df842825bbe73bbc16e30e91026e5`.
- Scope digest: `AD70C6D61C01500DBDF11BA8AFD5C1A42AD8C00D4EB63BDBF0EEC2423D1EB240`.
- Current semantic counts: `BLOCKED=12`, `INVALID=14`, `COLLECTED=0` at this HEAD.
- Current session provenance: Prime Builder, harness A, session `019f6610-1bc5-7781-88bf-900dccbc6010`, source `transcript_init_keyword`.

If committed HEAD or scope digest changes before implementation-start authorization, Prime Builder must perform no receipt mutation and file another current-baseline revision. The implementation report must record the pre-run and post-run HEAD/digest/counts.

## Complete Collector Plan And Potential Write Set

The fixed plan contains 26 objectives:

| Group | Receipt names | Current mix |
| --- | --- | --- |
| foundations | `predecessor-reconciliation`, `authority-carrier-classification`, `work-item-advisory-deduplication` | 3 INVALID |
| repository | `artifact-cleanup-batches`, `semantic-guidance-cleanup`, `lifecycle-state-reconciliation`, `runtime-interface-inventory` | 4 INVALID |
| harness-live | `harness-claude-live`, `harness-codex-live`, `harness-cursor-live`, `harness-antigravity-optimized-startup`, `headless-provider-conformance`, `cross-harness-confusion-corpus` | 5 BLOCKED, 1 INVALID |
| assurance | `pre-modernization-baseline`, `seven-category-scenario-matrix`, `six-activity-behavior-matrix`, `role-harness-session-branch-scenarios`, `confusion-regression-fixtures`, `nonimpairment-orchestrator`, `modernization-measurements`, `shadow-six-activities-primary-harnesses`, `activation-thresholds`, `reversible-activation-slices`, `operational-observation` | 5 BLOCKED, 6 INVALID |
| final | `program-closure`, `independent-verification` | 2 BLOCKED |

Successful objectives append `measurement.json`, `receipt.json`, and `issuance.json` beneath their named issue root and invocation ID. Executed measurement commands may append `output.log` beneath `semantic-evidence/command-runs`; pytest may use `.gtkb-state/mrc-pytest`. No other path is authorized.

The earlier `git-lifecycle-modernization-pilot.json` target is removed. This collector does not write that file; it only reads existing pilot evidence when evaluating `operational-observation`.

## Proposed Operation

1. Re-run `--json status` immediately before claim/start and verify exact HEAD, scope digest, session provenance, and counts.
2. Acquire a matching GO-implementation work-intent claim and implementation-start packet under the cited PAUTH.
3. Run the existing collector once with `--json all`.
4. Preserve honest `BLOCKED`/`FAIL` results; do not retry by synthesizing state, changing harness routing, opening/closing session envelopes, editing runtime JSON, or fabricating external evidence.
5. Re-run collector status, the clean-suite semantic checker, and Git-lifecycle checker read-only.
6. File an implementation report listing every newly appended path, every command result, exact before/after counts, and any remaining blockers.

## Requirement Sufficiency

Existing requirements sufficient. The linked modernization non-impairment, Git-binding, project-authorization, bridge-authority, and spec-derived verification requirements already govern this append-only evidence collection. This revision corrects stale scope and baseline metadata; it does not introduce a new product or governance requirement.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5165 RC blocker-repair PAUTH and the corrected version-004 Loyal Opposition NO-GO",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001; PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-WI-5165-RC-BLOCKER-REPAIR-20260715; WI-5165",
  "primary_route": "Run the existing fixed-plan modernization semantic-evidence collector once after exact HEAD, scope, GO, claim, and implementation-start checks.",
  "before_behavior": "At HEAD ea8dad56fb0df842825bbe73bbc16e30e91026e5 the semantic status is BLOCKED=12 and INVALID=14; the prior bridge authority names only nine receipt roots and a file the collector does not write.",
  "after_behavior": "Only objective-specific current receipts may be appended beneath the complete fixed plan; missing prerequisites remain BLOCKED and all command evidence stays bounded to declared roots.",
  "self_descriptive_naming": "All 26 issue roots retain the collector plan receipt_name values and each append uses one invocation ID.",
  "obsolete_guidance_disposition": "The stale version-001 baseline, incomplete nine-root list, superseded version-002 GO, and non-writer pilot target are not used for implementation authority.",
  "history_preservation": "Existing receipts, bridge files, Git history, release evidence, and session provenance remain append-only and are not rewritten or deleted.",
  "baseline": {
    "head": "ea8dad56fb0df842825bbe73bbc16e30e91026e5",
    "scope_digest": "AD70C6D61C01500DBDF11BA8AFD5C1A42AD8C00D4EB63BDBF0EEC2423D1EB240",
    "semantic_status": "BLOCKED=12 INVALID=14 COLLECTED=0",
    "potential_receipt_roots": 26,
    "runtime_output_roots": 2
  },
  "expected_result": {
    "receipt_policy": "Counts improve only when a current objective-specific measurement passes and issuance validates.",
    "blocked_policy": "Unobtainable evidence remains BLOCKED with its current reason.",
    "failure_policy": "Measurement failures and collector failures remain visible and are reported without synthetic retry state."
  },
  "rollback": {
    "instructions": "Do not delete append-only evidence under this authority; file a separately governed correction if a collector defect creates invalid output.",
    "test": "Re-run collector status, clean-suite semantics, Git-lifecycle checks, and exact pre/post inventory comparison."
  },
  "hard_invariants": [
    "No synthesized live harness, activation, pilot, operational, clean-run, or independent-verification evidence.",
    "No collection after HEAD or scope-digest drift.",
    "No mutation outside the 28 declared roots.",
    "No source, test, database, dispatcher, harness, credential, deployment, release, or Git-state mutation.",
    "No rewrite or deletion of existing receipt history."
  ],
  "fail_closed_conditions": [
    "HEAD or scope digest differs from the reviewed baseline.",
    "Missing GO, matching work-intent claim, or implementation-start packet.",
    "Missing or ambiguous canonical session provenance.",
    "Objective measurement is missing, blocked, timed out, or failing.",
    "A planned write resolves outside the declared target roots."
  ],
  "essential_context_preservation": "The 26-plan registry, current semantic status, non-impairment authority, stale-history distinction, and independent review requirement remain visible in the numbered bridge chain."
}
```

## Explicit Exclusions

- No source, test, manifest, specification, MemBase, database, bridge-history, dispatcher, TAFE, harness, routing, role, eligibility, lease, lock, credential, deployment, release, Git index, commit, branch, remote, or GitHub mutation.
- No deletion, rewrite, backdating, copying-forward, or status promotion of existing receipts.
- No synthetic live-harness, clean-run, pilot, activation, operational-observation, or independent-verification evidence.
- No write beneath a receipt name absent from the fixed 26-plan registry.
- No run if HEAD or scope digest differs from the baseline reviewed by Loyal Opposition.

## Specification Links

- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - requires current, non-synthetic evidence and fail-closed blocker handling.
- `DCL-GIT-BRANCH-BINDING-PROMOTION-001` - prevents synthetic or stale Git-lifecycle promotion evidence.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` - requires executable checks for the cross-cutting RC assertions.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this revision is the next numbered Prime Builder response to the corrected NO-GO.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - concrete governing links and mapped verification are present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - exact commands and result evidence are required before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - PAUTH, project, WI, and inline-JSON targets are explicit.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`, and `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - GO, claim, start packet, exact targets, and operation-time state remain mandatory.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - receipts and reports remain linked append-only lifecycle artifacts.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all potential writes are in-root GT-KB runtime evidence paths.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - the revised proposal is filed through the governed helper.

## Prior Deliberations

- `DELIB-20260710-GTKB-MODERNIZATION-NONIMPAIRMENT-GOV-FORMALIZATION-RESULT` - modernization non-impairment authority.
- `DELIB-20260710-GTKB-MODERNIZATION-GATE-1-READINESS-AUTHORIZATION` - Gate 1 readiness authorization.
- `DELIB-20260710-FIRST-STABILIZATION-BATCH-APPROVAL` - approved stabilization direction.
- `bridge/gtkb-modernization-rc-evidence-closure-001.md` - stale original proposal.
- `bridge/gtkb-modernization-rc-evidence-closure-002.md` - superseded GO.
- `bridge/gtkb-modernization-rc-evidence-closure-003.md` - correct Prime Builder NO-ACTION on stale scope.
- `bridge/gtkb-modernization-rc-evidence-closure-004.md` - corrected NO-GO requiring this current inventory.

## Owner Decisions / Input

No new owner decision is required. The active WI-5165 PAUTH and prior owner modernization decisions remain the authority; this revision narrows execution to the collector's actual append-only behavior and expands only the declared potential path inventory to match the fixed plan.

## Findings Addressed

### P1 - Collector writes exceeded the GO-approved targets

Corrected. The inline target inventory now contains every fixed receipt root plus the only two runtime-output roots written by collector subprocess handling. The stale pilot-file target was removed because the collector does not write it.

### P1 - Approved baseline was no longer current

Corrected to HEAD `ea8dad56fb0df842825bbe73bbc16e30e91026e5`, scope digest `AD70C6D61C01500DBDF11BA8AFD5C1A42AD8C00D4EB63BDBF0EEC2423D1EB240`, and `BLOCKED=12` / `INVALID=14`. Operation is fail-closed on any subsequent HEAD or digest change.

### Clause evidence gap for spec-derived testing

Corrected through the mapped verification matrix below and the requirement that the report record exact command outputs and before/after counts.

## Scope Changes

The proposal now covers the collector's complete fixed write envelope instead of nine selected receipts and a non-writer pilot path. It still authorizes no product/source change, no external-state mutation, and no evidence synthesis.

## Pre-Filing Preflight Subsection

The governed revision helper must pass applicability and mandatory-clause preflights on this exact content before publication. A missing required spec, target-class denial, credential hit, stale bridge version, or clause gap blocks filing.

## Specification-Derived Verification Plan

| Governing requirement | Deterministic command/evidence | Required result |
| --- | --- | --- |
| Current baseline and exact receipt validity | `python scripts/collect_modernization_semantic_evidence.py --json status` before and after collection | Exact HEAD/digest; counts and per-receipt statuses recorded |
| Mechanical clean-suite semantics | `python scripts/check_modernization_scope_semantics.py run --phase clean-suite --json` | No newly impaired assertion; exact remaining failures reported |
| Git binding and non-synthesis | `python scripts/check_modernization_git_lifecycle.py --json` | Existing real evidence only; no collector-created pilot artifact |
| Fixed-plan coverage | `python -m pytest platform_tests/scripts/test_collect_modernization_semantic_evidence.py -q --tb=short` | Plan count, append-only issuance, blocked behavior, and path contracts pass |
| Collector source quality without mutation | `python -m ruff check scripts/collect_modernization_semantic_evidence.py` and `python -m ruff format --check scripts/collect_modernization_semantic_evidence.py` | PASS |
| Exact writes | Compare pre/post filesystem inventory beneath the 28 declared roots | Every new file belongs to one invocation and declared root |
| Governance | Applicability, clause, claim, target, and implementation-start preflights | PASS before collection |

## Acceptance Criteria

- The implementation starts only when HEAD and scope digest equal the reviewed baseline.
- Every collected receipt has current Git HEAD, current scope digest, canonical open-session provenance, objective-specific passing measurement, and append-only issuance.
- Unobtainable objectives remain explicitly BLOCKED; failures remain visible.
- No file is created or changed outside the 28 declared roots.
- The report records all new files and exact before/after semantic status.

## Risk And Rollback

The primary risk is concurrent HEAD drift or a newly obtainable objective writing a path omitted from review. Exact baseline recheck and the complete fixed plan inventory address both. Rollback of an incorrectly generated runtime receipt requires a separately governed correction; this proposal does not authorize deletion. Bridge and receipt history remain append-only.

## Recommended Commit Type

No source commit is expected. If a later governed evidence-carrier commit is required, use `chore(governance):` and include only independently reviewed evidence paths.
