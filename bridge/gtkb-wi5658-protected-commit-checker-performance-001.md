NEW
::init gtkb lo
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 87ea6b9f-89d5-4e90-a637-a7f9fe8cb561
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive Prime Builder; resolved role prime-builder via ::init gtkb pb

# Implementation Proposal - Protected-commit checker performance: hoist committed-bridge enumeration out of per-packet loop

bridge_kind: prime_proposal
Document: gtkb-wi5658-protected-commit-checker-performance
Version: 001
Date: 2026-07-23 UTC

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

Fix the protected-commit checker's O(packets x committed-bridge-files) hang (470 packets x 13425 files ~= 6.3M parses/commit) by enumerating the committed bridge tree once and reusing it, plus a bounded _run_git timeout. Restores commit-finalization speed; unblocks WI-5657, WI-5441, and all future phase finalizations. Performance-only, no semantics change.

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
- `GOV-WORK-TREE-HYGIENE-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-202666549` - Loyal Opposition Corrected Verdict (review_no_action) - GO - WI-5344 Bound Git-Lifecycle Wrapper Process Tree
- `DELIB-202667024` - LO Review - WI-5370 WI-5361 Invalid Terminal Verdict Reissue (REVISED-007 Byte-Identity/Race Concern)
- `DELIB-20265407` - Loyal Opposition Review - WI-4678 git-write finalization blocker report
- `DELIB-202666061` - Verdict: VERIFIED
- `DELIB-202666969` - NO-GO — WI-5344 Bounded Git-Lifecycle Wrapper Process Tree (finalization-mechanics blocker)

## Owner Decisions / Input

- `DELIB-202667183` - owner-decision evidence supplied to this command.
- `PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI-5658-PROTECTED-COMMIT-CHECKER-PERFORMANCE-FIX` - active project authorization covering `WI-5658`.

## Proposed Scope

- In _load_verified_evidence, enumerate the committed bridge tree ONCE (git ls-tree -r -z HEAD -- bridge, parsed into a bridge-id->entries map) before the per-packet loop, instead of _bridge_snapshot re-running ls-tree + parsing 1.5MB for each of 470 packets.
- Add an optional pre-enumerated head-entries argument to _bridge_snapshot's committed-history path so it reuses the once-computed listing: O(packets + bridge-files) instead of O(packets x bridge-files).
- Add a bounded subprocess timeout to _run_git so a blocked git call fails closed instead of grinding unbounded (honors the git-subprocesses-must-be-timeout-bounded invariant).
- No change to authorization semantics, verdict outcomes, or single-candidate validation; purely a performance optimization.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5658; PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI-5658-PROTECTED-COMMIT-CHECKER-PERFORMANCE-FIX; generated by gt bridge file-implementation-proposal",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and the governed bridge proposal generators",
  "primary_route": "gt bridge file-implementation-proposal",
  "before_behavior": "scripts/check_protected_commit_authorization.py _load_verified_evidence loops over 470 committed named packets, each calling _bridge_snapshot which re-runs git ls-tree over all 13425 committed bridge files (~6.3M tree entries parsed per commit) + materialize + resolve. O(packets x bridge-files); _run_git has no timeout. Pre-commit hook exceeds 2 min, failing all finalizer commits (file-only VERIFIED, WI-5648/WI-5113 class). Fix: enumerate committed bridge tree once, index by bridge-id, reuse per packet (O(packets + bridge-files)); add bounded _run_git timeout. Performance-only, no authorization-semantics change.",
  "after_behavior": "Fix the protected-commit checker's O(packets x committed-bridge-files) hang (470 packets x 13425 files ~= 6.3M parses/commit) by enumerating the committed bridge tree once and reusing it, plus a bounded _run_git timeout. Restores commit-finalization speed; unblocks WI-5657, WI-5441, and all future phase finalizations. Performance-only, no semantics change.",
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
      "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001",
      "GOV-WORK-TREE-HYGIENE-001"
    ]
  },
  "expected_result": {
    "summary": "Fix the protected-commit checker's O(packets x committed-bridge-files) hang (470 packets x 13425 files ~= 6.3M parses/commit) by enumerating the committed bridge tree once and reusing it, plus a bounded _run_git timeout. Restores commit-finalization speed; unblocks WI-5657, WI-5441, and all future phase finalizations. Performance-only, no semantics change.",
    "scope": [
      "In _load_verified_evidence, enumerate the committed bridge tree ONCE (git ls-tree -r -z HEAD -- bridge, parsed into a bridge-id->entries map) before the per-packet loop, instead of _bridge_snapshot re-running ls-tree + parsing 1.5MB for each of 470 packets.",
      "Add an optional pre-enumerated head-entries argument to _bridge_snapshot's committed-history path so it reuses the once-computed listing: O(packets + bridge-files) instead of O(packets x bridge-files).",
      "Add a bounded subprocess timeout to _run_git so a blocked git call fails closed instead of grinding unbounded (honors the git-subprocesses-must-be-timeout-bounded invariant).",
      "No change to authorization semantics, verdict outcomes, or single-candidate validation; purely a performance optimization."
    ],
    "acceptance_criteria": [
      "The checker completes well under the pre-commit budget (target <10s) on a representative VERIFIED finalization set with 470 committed packets, vs >120s before.",
      "Committed-VERIFIED evidence output (evidence tuples + errors) is identical before/after the change.",
      "A blocked/slow git subprocess in _run_git times out and fails closed rather than hanging.",
      "Existing checker test suite continues to pass."
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
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Timing test asserts evaluate/_load_verified_evidence completes under a bounded threshold on a many-packet fixture; equivalence test asserts identical committed-VERIFIED evidence before/after; full existing suite re-run. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Spec-derived tests map the perf bound, output-equivalence, and timeout-fail-closed behaviors to explicit assertions. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-WORK-TREE-HYGIENE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |

## Acceptance Criteria

- The checker completes well under the pre-commit budget (target <10s) on a representative VERIFIED finalization set with 470 committed packets, vs >120s before.
- Committed-VERIFIED evidence output (evidence tuples + errors) is identical before/after the change.
- A blocked/slow git subprocess in _run_git times out and fails closed rather than hanging.
- Existing checker test suite continues to pass.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/check_protected_commit_authorization.py`
- `platform_tests/scripts/test_check_protected_commit_authorization.py`

## Recommended Commit Type

`feat`
