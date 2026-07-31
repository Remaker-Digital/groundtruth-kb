REVISED
::init gtkb lo
::open build
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 87ea6b9f-89d5-4e90-a637-a7f9fe8cb561
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive Prime Builder; resolved role prime-builder via ::init gtkb pb

# Implementation Proposal - Protected-commit checker performance: pre-filter verified-evidence packets to staged protected paths

bridge_kind: prime_proposal
Document: gtkb-wi5659-checker-verified-evidence-prefilter
Version: 003
Date: 2026-07-23 UTC
Responds to: bridge/gtkb-wi5659-checker-verified-evidence-prefilter-002.md

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI-5659-CHECKER-VERIFIED-EVIDENCE-PREFILTER-FIX
Project Authorization Candidates: [{"project_authorization_id":"PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI-5659-CHECKER-VERIFIED-EVIDENCE-PREFILTER-FIX","coverage":"exact_singleton","included_work_item_count":1,"specificity_rank":[0,1],"selected":true}]
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5659

target_paths: ["scripts/check_protected_commit_authorization.py", "platform_tests/scripts/test_check_protected_commit_authorization.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Note (addresses NO-GO at -002)

The version-002 NO-GO raised exactly one P1 finding: version 001 cited
`PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI-5659-IMPLEMENTATION-PROPOSAL-FILING`,
which `--create-missing-state` auto-created scoped to
`allowed_mutation_classes: ["bridge", "metadata"]` (proposal filing only). The
proposed work mutates `source` and `test`, so a GO on version 001 would have
created misleading implementation authority.

Resolution: a bounded **implementation** PAUTH was created through the governed
`gt projects authorize` path —
`PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI-5659-CHECKER-VERIFIED-EVIDENCE-PREFILTER-FIX`
— with `allowed_mutation_classes: ["source", "test"]`, `included_work_item_ids:
["WI-5659"]`, `owner_decision_deliberation_id: DELIB-202667184`, and the owner
decision's forbidden-operation boundaries (`git_commit`, `git_history_rewrite`,
`git_push`, `destructive_cleanup`, `dispatcher_mutation`,
`external_system_mutation`, `production_deployment`, `release`,
`credential_lifecycle`). This REVISED version cites that implementation PAUTH.
The technical scope, target paths, no-semantic-change boundary, and spec-derived
test plan are unchanged from version 001. All three Required Revisions from -002
are satisfied: (1) implementation PAUTH now cited; (2) `DELIB-202667184` carried
forward as the owner source; (3) exact target paths, no-semantic-change
boundary, and spec-derived tests preserved.

## Summary

Pre-filter _load_verified_evidence to only the committed packets whose stored target_path_globs authorize a staged protected path (471 -> typically 1-3), collapsing the 460.8s finalizer hang to seconds. Provably outcome-preserving via the line-1267 binding invariant; verified_errors is only diagnostic context for already-failing paths. Restores governed commit-finalization; unblocks WI-5441. Follow-on to WI-5658.

Work item description: After WI-5658 hoisted committed-bridge enumeration (now 0.27s), _load_verified_evidence still materializes + lifecycle-resolves ALL 471 committed packets on every commit (~978ms each = 460.8s measured; only 5 resolve to valid evidence, 457 error). Per line 1267 binding invariant (packet.target_path_globs == chain.target_paths), a packet can only authorize a staged protected path when its cheap stored target_path_globs matches it. Fix: pass staged protected_paths into _load_verified_evidence and skip expensive _bridge_snapshot+resolve for packets whose stored globs authorize none of them (471 -> typically 1-3). Provably outcome-preserving: verified_errors is only diagnostic context for already-failing paths (line 1733). Restores governed commit-finalization. Follow-on to WI-5658; unblocks WI-5441 finalization.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5659` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active implementation project authorization (`PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI-5659-CHECKER-VERIFIED-EVIDENCE-PREFILTER-FIX`, source+test) define the implementation boundary.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/check_protected_commit_authorization.py`, `platform_tests/scripts/test_check_protected_commit_authorization.py`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge authority and numbered-file filing.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - auto-linked governing or work-item specification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links in implementation proposals.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived verification evidence before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.
- `SPEC-AUQ-POLICY-ENGINE-001` - auto-linked governing or work-item specification.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps this platform command out of adopter application scope.
- `GOV-STANDING-BACKLOG-001` - auto-linked governing or work-item specification.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - auto-linked governing or work-item specification.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - auto-linked governing or work-item specification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-202667184` - Owner authorizes fixing the real finalizer hang (470-packet loop), not lock contention; authorizes source/test work in the two target paths with no semantic outcome change.
- `bridge/gtkb-wi5659-checker-verified-evidence-prefilter-002.md` - LO NO-GO requiring the implementation-scoped PAUTH cited by this REVISED version.
- `bridge/gtkb-wi5658-protected-commit-checker-performance-002.md` - adjacent latest GO for the preceding checker performance slice (WI-5658); this slice builds on that performance direction with its own implementation PAUTH.
- `DELIB-202666273` - WI-5266 five-path baseline preservation exception.
- `DELIB-202666966` - Loyal Opposition Corrected Verdict - GO - WI-5343 LO Review Authority Packet.

## Owner Decisions / Input

- `DELIB-202667184` - owner AUQ decision (2026-07-23) authorizing the bounded WI-5659 finalizer 470-loop pre-filter fix (source+test, no semantic change).
- `PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI-5659-CHECKER-VERIFIED-EVIDENCE-PREFILTER-FIX` - active implementation project authorization covering `WI-5659` with `source` and `test` mutation classes, linked to `DELIB-202667184`.

## Proposed Scope

- Add a protected_paths parameter to _load_verified_evidence; _evaluate_selected passes the staged protected paths it already computed.
- Before the expensive per-packet _bridge_snapshot + resolve_bridge_lifecycle, skip any packet whose stored target_path_globs (via path_authorized) authorizes none of the staged protected paths.
- Preserve terminal_verified_packets_scanned as the total committed packet count; the pre-filter only changes which packets are expensively resolved.
- No authorization-semantics change: by the line-1267 binding invariant (packet.target_path_globs == chain.target_paths) a packet can only authorize a staged path when its stored globs match it, so skipped packets cannot change any cleared/finding outcome.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5659; PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI-5659-CHECKER-VERIFIED-EVIDENCE-PREFILTER-FIX; revised via gtkb-bridge revise_bridge helper after NO-GO at -002",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and the governed bridge proposal generators",
  "primary_route": "gt projects authorize + revise_bridge.py file",
  "before_behavior": "After WI-5658 hoisted committed-bridge enumeration (now 0.27s), _load_verified_evidence still materializes + lifecycle-resolves ALL 471 committed packets on every commit (~978ms each = 460.8s measured; only 5 resolve to valid evidence, 457 error). Per line 1267 binding invariant (packet.target_path_globs == chain.target_paths), a packet can only authorize a staged protected path when its cheap stored target_path_globs matches it. Fix: pass staged protected_paths into _load_verified_evidence and skip expensive _bridge_snapshot+resolve for packets whose stored globs authorize none of them (471 -> typically 1-3). Provably outcome-preserving: verified_errors is only diagnostic context for already-failing paths (line 1733). Restores governed commit-finalization. Follow-on to WI-5658; unblocks WI-5441 finalization.",
  "after_behavior": "Pre-filter _load_verified_evidence to only the committed packets whose stored target_path_globs authorize a staged protected path (471 -> typically 1-3), collapsing the 460.8s finalizer hang to seconds. Provably outcome-preserving via the line-1267 binding invariant; verified_errors is only diagnostic context for already-failing paths. Restores governed commit-finalization; unblocks WI-5441. Follow-on to WI-5658.",
  "self_descriptive_naming": "The generated title, work-item id, target paths, scope, and acceptance criteria name the proposed effect.",
  "obsolete_guidance_disposition": "No guidance is retired by proposal filing; implementation must explicitly disposition obsolete guidance.",
  "history_preservation": "The numbered bridge chain remains append-only; rollback never deletes proposal or verdict artifacts.",
  "baseline": {
    "work_item": "WI-5659",
    "project": "PROJECT-GTKB-HOUSEKEEPING-HARDENING",
    "target_paths": [
      "scripts/check_protected_commit_authorization.py",
      "platform_tests/scripts/test_check_protected_commit_authorization.py"
    ],
    "linked_specifications": [
      "GOV-FILE-BRIDGE-AUTHORITY-001",
      "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001",
      "DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001",
      "DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001",
      "DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001",
      "SPEC-AUQ-POLICY-ENGINE-001",
      "ADR-ISOLATION-APPLICATION-PLACEMENT-001",
      "GOV-STANDING-BACKLOG-001",
      "ADR-CODEX-HOOK-PARITY-FALLBACK-001",
      "ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001",
      "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001"
    ]
  },
  "expected_result": {
    "summary": "Pre-filter _load_verified_evidence to only the committed packets whose stored target_path_globs authorize a staged protected path (471 -> typically 1-3), collapsing the 460.8s finalizer hang to seconds. Provably outcome-preserving via the line-1267 binding invariant; verified_errors is only diagnostic context for already-failing paths. Restores governed commit-finalization; unblocks WI-5441. Follow-on to WI-5658.",
    "scope": [
      "Add a protected_paths parameter to _load_verified_evidence; _evaluate_selected passes the staged protected paths it already computed.",
      "Before the expensive per-packet _bridge_snapshot + resolve_bridge_lifecycle, skip any packet whose stored target_path_globs (via path_authorized) authorizes none of the staged protected paths.",
      "Preserve terminal_verified_packets_scanned as the total committed packet count; the pre-filter only changes which packets are expensively resolved.",
      "No authorization-semantics change: by the line-1267 binding invariant (packet.target_path_globs == chain.target_paths) a packet can only authorize a staged path when its stored globs match it, so skipped packets cannot change any cleared/finding outcome."
    ],
    "acceptance_criteria": [
      "On a fixture with 400+ committed packets and a handful of staged protected paths, _load_verified_evidence completes under 10s (vs 460.8s measured), well under the pre-commit budget.",
      "For every staged protected path, the cleared-vs-finding authorization outcome (and cleared evidence source) is identical to the pre-filter full-scan evaluation.",
      "_load_verified_evidence expensively resolves exactly the packets whose stored target_path_globs authorize a staged protected path (asserted via a resolution spy/counter).",
      "Existing checker test suite continues to pass; ruff check and ruff format --check clean on changed files."
    ]
  },
  "rollback": {
    "instructions": "Revert only the approved source and test implementation targets under separate authority.",
    "verification": "Rerun the proposal's specification-derived tests and bridge preflights."
  },
  "hard_invariants": [
    "Bridge review, implementation-start, and independent verification gates remain mandatory.",
    "Only the declared in-root target paths are attributable to this implementation proposal.",
    "Dispatcher, TAFE, credential, deployment, release, and unrelated work remain outside generated authority."
  ],
  "fail_closed_conditions": [
    "Project membership or active PAUTH coverage is missing.",
    "Target paths escape the project root or candidate/live preflights fail.",
    "Required proposal evidence is empty, malformed, duplicated, or still contains authoring placeholders."
  ],
  "essential_context_preservation": "The generated proposal retains PAUTH, project, work item, targets, specifications, prior deliberations, owner decisions, scope, verification, acceptance, risk, rollback, and expected file changes."
}
```

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Timing test asserts _load_verified_evidence completes under a bounded threshold on a many-packet fixture with few staged protected paths; equivalence test asserts identical authorization outcome (cleared/finding + evidence source) before/after the pre-filter; full existing suite re-run. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Spec-derived tests map the pre-filter relevance rule, output-equivalence, and expensive-resolution-count to explicit assertions. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |

## Acceptance Criteria

- On a fixture with 400+ committed packets and a handful of staged protected paths, _load_verified_evidence completes under 10s (vs 460.8s measured), well under the pre-commit budget.
- For every staged protected path, the cleared-vs-finding authorization outcome (and cleared evidence source) is identical to the pre-filter full-scan evaluation.
- _load_verified_evidence expensively resolves exactly the packets whose stored target_path_globs authorize a staged protected path (asserted via a resolution spy/counter).
- Existing checker test suite continues to pass; ruff check and ruff format --check clean on changed files.

## Risks / Rollback

Risk is moderate. The pre-filter changes only which packets are expensively resolved; by the line-1267 binding invariant it cannot change any authorization outcome, and verified_errors is only diagnostic context for already-failing paths. The implementation must fail closed around owner-decision evidence, target paths, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/check_protected_commit_authorization.py`
- `platform_tests/scripts/test_check_protected_commit_authorization.py`

## Recommended Commit Type

`perf`
