NEW
::init gtkb pb
::open build
author_identity: codex
author_harness_id: A
author_session_context_id: A-2026-07-24T14-24-57Z
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=default; thread_source=codex-desktop
author_metadata_source: x-codex-turn-metadata

# Implementation Proposal - Protected-commit checker performance: hoist committed-bridge enumeration out of per-packet loop

bridge_kind: prime_proposal
Document: gtkb-wi5658-terminal-verdict-recovery
Version: 001
Date: 2026-07-24 UTC

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI-5658-PROTECTED-COMMIT-CHECKER-PERFORMANCE-FIX
Project Authorization Candidates: [{"project_authorization_id":"PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI-5658-PROTECTED-COMMIT-CHECKER-PERFORMANCE-FIX","coverage":"exact_singleton","included_work_item_count":1,"specificity_rank":[0,1],"selected":true}]
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5658

target_paths: ["scripts/check_protected_commit_authorization.py", "platform_tests/scripts/test_check_protected_commit_authorization.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Recover WI-5658 from an untracked file-only VERIFIED verdict using committed by-reference audit finalization, not a second source implementation.

Work item description: scripts/check_protected_commit_authorization.py _load_verified_evidence loops over 470 committed named packets, each calling _bridge_snapshot which re-runs git ls-tree over all 13425 committed bridge files (~6.3M tree entries parsed per commit) + materialize + resolve. O(packets x bridge-files); _run_git has no timeout. Pre-commit hook exceeds 2 min, failing all finalizer commits (file-only VERIFIED, WI-5648/WI-5113 class). Fix: enumerate committed bridge tree once, index by bridge-id, reuse per packet (O(packets + bridge-files)); add bounded _run_git timeout. Performance-only, no authorization-semantics change.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5658` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

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

- `DELIB-202666549` - Loyal Opposition Corrected Verdict (review_no_action) - GO - WI-5344 Bound Git-Lifecycle Wrapper Process Tree
- `DELIB-202667024` - LO Review - WI-5370 WI-5361 Invalid Terminal Verdict Reissue (REVISED-007 Byte-Identity/Race Concern)
- `DELIB-20265407` - Loyal Opposition Review - WI-4678 git-write finalization blocker report
- `DELIB-202666969` - NO-GO — WI-5344 Bounded Git-Lifecycle Wrapper Process Tree (finalization-mechanics blocker)
- `DELIB-202666061` - Verdict: VERIFIED

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI-5658-PROTECTED-COMMIT-CHECKER-PERFORMANCE-FIX` - active project authorization covering `WI-5658`.

## Proposed Scope

- Quarantine the untracked WI-5658 report and file-only VERIFIED verdict; they must not be used as completion evidence or staged as ordinary source work.
- Establish a new append-only recovery chain that proves the exact already-committed implementation at 93f7764662853b3f86a714d34555303a62c2321d and requires governed by-reference bridge-audit finalization.
- Do not modify, restage, or attribute later WI-5657/WI-5659 overlapping hunks; do not create a new source implementation.

## Cross-Harness Disposition

- **Protected-commit checker**: Preserve the committed WI-5658 implementation; repair only its audit/finalization provenance without new harness behavior.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5658; PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI-5658-PROTECTED-COMMIT-CHECKER-PERFORMANCE-FIX; generated by gt bridge file-implementation-proposal",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and the governed bridge proposal generators",
  "primary_route": "gt bridge file-implementation-proposal",
  "before_behavior": "scripts/check_protected_commit_authorization.py _load_verified_evidence loops over 470 committed named packets, each calling _bridge_snapshot which re-runs git ls-tree over all 13425 committed bridge files (~6.3M tree entries parsed per commit) + materialize + resolve. O(packets x bridge-files); _run_git has no timeout. Pre-commit hook exceeds 2 min, failing all finalizer commits (file-only VERIFIED, WI-5648/WI-5113 class). Fix: enumerate committed bridge tree once, index by bridge-id, reuse per packet (O(packets + bridge-files)); add bounded _run_git timeout. Performance-only, no authorization-semantics change.",
  "after_behavior": "Recover WI-5658 from an untracked file-only VERIFIED verdict using committed by-reference audit finalization, not a second source implementation.",
  "self_descriptive_naming": "The generated title, work-item id, target paths, scope, and acceptance criteria name the proposed effect.",
  "obsolete_guidance_disposition": "No guidance is retired by proposal filing; implementation must explicitly disposition obsolete guidance.",
  "history_preservation": "The numbered bridge chain remains append-only; rollback never deletes proposal or verdict artifacts.",
  "baseline": {
    "work_item": "WI-5658",
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
    "summary": "Recover WI-5658 from an untracked file-only VERIFIED verdict using committed by-reference audit finalization, not a second source implementation.",
    "scope": [
      "Quarantine the untracked WI-5658 report and file-only VERIFIED verdict; they must not be used as completion evidence or staged as ordinary source work.",
      "Establish a new append-only recovery chain that proves the exact already-committed implementation at 93f7764662853b3f86a714d34555303a62c2321d and requires governed by-reference bridge-audit finalization.",
      "Do not modify, restage, or attribute later WI-5657/WI-5659 overlapping hunks; do not create a new source implementation."
    ],
    "acceptance_criteria": [
      "The recovery evidence identifies the exact two-file implementation commit, its bounded diff, and focused test/lint/format results.",
      "The terminal bridge audit transaction carries a helper-recognized by-reference waiver and contains complete finalization evidence; a file-only VERIFIED is rejected.",
      "The untracked predecessor report/verdict remain quarantined and a fresh independent LO verdict closes only the recovery thread."
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
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Verify 93f776466 path scope and tests; then run the governed finalization helper on the bridge-only by-reference transaction. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |

## Acceptance Criteria

- The recovery evidence identifies the exact two-file implementation commit, its bounded diff, and focused test/lint/format results.
- The terminal bridge audit transaction carries a helper-recognized by-reference waiver and contains complete finalization evidence; a file-only VERIFIED is rejected.
- The untracked predecessor report/verdict remain quarantined and a fresh independent LO verdict closes only the recovery thread.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/check_protected_commit_authorization.py`
- `platform_tests/scripts/test_check_protected_commit_authorization.py`

## Recommended Commit Type

`feat`
