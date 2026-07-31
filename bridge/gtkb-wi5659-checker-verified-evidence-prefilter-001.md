NEW
::init gtkb lo
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 87ea6b9f-89d5-4e90-a637-a7f9fe8cb561
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive Prime Builder; resolved role prime-builder via ::init gtkb pb

# Implementation Proposal - Protected-commit checker performance: pre-filter verified-evidence packets to staged protected paths

bridge_kind: prime_proposal
Document: gtkb-wi5659-checker-verified-evidence-prefilter
Version: 001
Date: 2026-07-23 UTC

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI-5659-IMPLEMENTATION-PROPOSAL-FILING
Project Authorization Candidates: [{"project_authorization_id":"PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI-5659-IMPLEMENTATION-PROPOSAL-FILING","coverage":"exact_singleton","included_work_item_count":1,"specificity_rank":[0,1],"selected":true}]
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5659

target_paths: ["scripts/check_protected_commit_authorization.py", "platform_tests/scripts/test_check_protected_commit_authorization.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Pre-filter _load_verified_evidence to only the committed packets whose stored target_path_globs authorize a staged protected path (471 -> typically 1-3), collapsing the 460.8s finalizer hang to seconds. Provably outcome-preserving via the line-1267 binding invariant; verified_errors is only diagnostic context for already-failing paths. Restores governed commit-finalization; unblocks WI-5441. Follow-on to WI-5658.

Work item description: After WI-5658 hoisted committed-bridge enumeration (now 0.27s), _load_verified_evidence still materializes + lifecycle-resolves ALL 471 committed packets on every commit (~978ms each = 460.8s measured; only 5 resolve to valid evidence, 457 error). Per line 1267 binding invariant (packet.target_path_globs == chain.target_paths), a packet can only authorize a staged protected path when its cheap stored target_path_globs matches it. Fix: pass staged protected_paths into _load_verified_evidence and skip expensive _bridge_snapshot+resolve for packets whose stored globs authorize none of them (471 -> typically 1-3). Provably outcome-preserving: verified_errors is only diagnostic context for already-failing paths (line 1733). Restores governed commit-finalization. Follow-on to WI-5658; unblocks WI-5441 finalization.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5659` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

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

- `DELIB-202666273` - WI-5266 five-path baseline preservation exception
- `DELIB-20260722-WI5652-IMPL-START-GATE-MULTIPATH-DRIFT-FIX` - WI-5652 single-path fix for impl-start gate multi-path drift; independent of WI-5178
- `DELIB-202667184` - Owner authorizes fixing the real finalizer hang (470-packet loop), not lock contention
- `DELIB-202666774` - WI-5370 Sprawl Reconciliation - Owner Decisions and Findings
- `DELIB-202666966` - Loyal Opposition Corrected Verdict - GO - WI-5343 LO Review Authority Packet

## Owner Decisions / Input

- `DELIB-202667184` - owner-decision evidence supplied to this command.
- `PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI-5659-IMPLEMENTATION-PROPOSAL-FILING` - active project authorization covering `WI-5659`.

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
  "provenance": "WI-5659; PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI-5659-IMPLEMENTATION-PROPOSAL-FILING; generated by gt bridge file-implementation-proposal",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and the governed bridge proposal generators",
  "primary_route": "gt bridge file-implementation-proposal",
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

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/check_protected_commit_authorization.py`
- `platform_tests/scripts/test_check_protected_commit_authorization.py`

## Recommended Commit Type

`feat`
