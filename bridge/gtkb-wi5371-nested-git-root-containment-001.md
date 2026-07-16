NEW

# Contain authorization dirty-path discovery to the exact Git root

bridge_kind: prime_proposal
Document: gtkb-wi5371-nested-git-root-containment
Version: 001
Author: Prime Builder (Codex A)
Date: 2026-07-16T22:20:00Z

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive; role=prime-builder; approval_policy=never; sandbox=danger-full-access

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5371

target_paths: ["scripts/implementation_authorization.py", "platform_tests/scripts/test_implementation_authorization.py"]

implementation_scope: source_and_tests
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Prevent authorization-packet collision checks from treating an arbitrary
nested directory as authority for its ancestor Git repository. The repository
pytest configuration intentionally creates isolated fixture roots below an
ignored in-root temporary parent. `_dirty_worktree_paths()` currently launches
`git status` from the supplied root without proving that the supplied root is
the exact Git top-level. Git walks upward to the live GT-KB repository, scans
all current dirt, and turns an isolated fixture into a full-worktree operation.

The frozen authority-operation acceptance activity now reproduces a default
30-second timeout in that scan. A direct live-root status took 4.788 seconds,
the worktree had 1,736 entries at diagnosis time, and concurrent samples showed
multiple Desktop snapshot scans. When pytest interrupts the unbounded call,
Git descendants can outlive the test process.

Repair the boundary in two stages. First, reject a supplied project root as a
dirty-path authority root unless it has its own Git marker and the canonical
top-level resolves exactly to that normalized root. A nested non-repository
fixture must return no attributable dirty evidence before a full status scan.
Second, execute the exact-root probe and status under the committed no-window
subprocess convention with a finite internal timeout and complete process-tree
termination. Preserve the existing fail-soft contract: missing Git, malformed
output, non-zero exit, boundary mismatch, or timeout returns no evidence rather
than denying otherwise valid implementation.

Both target files contain current foreign WI-5178 integration work. This
proposal is a strict successor to WI-5178: do not implement, review, or finalize
its hunks until WI-5178 is independently VERIFIED and mechanically established
as the baseline. The observed pre-proposal hashes were
`5FCE7F62131B8F601607D349B38BD962EC623FBE9E89DF536AA5EA92C33E6EEC` and
`13280D1E5F6A8D568DF2FE99D4926CC77140128FBD01FCCBDD1686603E1D8278` in target
order; they are concurrency snapshots, not ownership claims.

## Specification Links

- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation authority must use evidence attributable to the named project, not an ancestor repository reached by Git discovery.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - operation-time checks must remain deterministic and bounded immediately before effect.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - the repair must preserve real-root collision detection and must not disable or reduce harness dispatchability.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - root selection, timeout, and failure behavior must be mechanically testable.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected changes still require independent GO, a matching claim/start packet, implementation reporting, and independent VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal is bound to WI-5371 and the active Assurance PAUTH.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the complete governing specification set is explicit here.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - independent verification must execute the focused and frozen acceptance evidence.
- `DCL-PROJECT-DEPENDENCY-ORDERING-001` - WI-5178 must become the exact baseline before these two shared-file hunks begin.
- `GOV-STANDING-BACKLOG-001` - the reproducible acceptance blocker remains visible until verified and finalized.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all runtime state and verification evidence remain within the GT-KB root.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the defect, linked test, proposal, implementation evidence, and verdict remain durably connected.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - WI-5371 remains open through implementation, independent verification, and mechanical finalization.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the newly discovered acceptance defect is represented as an origin=hygiene work item and linked test.

## Prior Deliberations

- `DELIB-202666274` - authorizes required modernization blocker work at project scope while preserving bridge, independent review, and mechanical-operation gates.
- `DELIB-WI5066-INDEP-ROOTCAUSE-COMMINGLE-HAZARD-20260709` - confirms that concurrent dirty-path attribution must be exact and may not commingle unrelated work.
- `INTAKE-c5792b0c` - establishes bounded Git lifecycle behavior and deterministic process containment as project expectations.

## Owner Decisions / Input

No new owner decision is required. The modernization program and active
project-scoped Assurance PAUTH cover the proposal, while independent GO,
matching claim/start authority, independent VERIFIED, and exact mechanical Git
authority remain mandatory. This proposal does not request dispatcher, TAFE,
harness eligibility, role, credential, staging, commit, push, deployment,
release, or destructive-cleanup mutation.

## Requirement Sufficiency

Existing requirements sufficient. The implementation-authorization,
operation-time enforcement, evaluability, non-impairment, dependency-ordering,
and spec-derived verification requirements fully define the repair. No new or
revised requirement is needed.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5371 authoritative-worktree diagnosis under DELIB-202666274",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "frozen AT-AUTHORITY-OPERATION-TIME activity",
  "before_behavior": "A nested non-repository fixture root inherits its ancestor repository through Git discovery, performs an unbounded full-worktree status, and may leak Git descendants when pytest times out.",
  "after_behavior": "Only the exact normalized Git top-level can supply dirty-path evidence; nested roots return no evidence before status; exact-root probes are hidden, bounded, fail-soft, and terminate their complete process tree.",
  "self_descriptive_naming": "Exact-root and bounded-probe helpers make repository authority and failure behavior explicit rather than relying on Git's upward discovery.",
  "obsolete_guidance_disposition": "No governance rule is retired; only the implicit assumption that every supplied directory is its own Git root is removed.",
  "history_preservation": "All WI-5178 and other pre-start hunks remain byte-identical outside the later WI-5371 patch and retain independent ownership.",
  "baseline": {
    "worktree_entries_at_diagnosis": 1736,
    "direct_live_root_status_milliseconds": 4788,
    "isolated_reproductions_at_default_timeout": 2,
    "default_pytest_timeout_seconds": 30
  },
  "expected_result": {
    "ancestor_repository_status_scans_from_nested_fixture": 0,
    "focused_default_timeout_failures": 0,
    "leaked_probe_descendants": 0,
    "real_root_dirty_path_detection_preserved": true
  },
  "rollback": "Revert only the independently attributed WI-5371 source and test hunks through a separately governed transaction after preserving the WI-5178 baseline and all concurrent bytes.",
  "hard_invariants": [
    "real exact-root dirty paths still participate in commingle protection",
    "a failed or timed-out Git probe cannot become positive collision evidence",
    "no subprocess launched by this repair may create a visible console window",
    "no timed-out probe may leave a descendant process running",
    "no harness is disabled, deprioritized, rerouted, or made ineligible",
    "no dispatcher, TAFE, harness registry, role, or bridge-routing configuration is mutated",
    "no unrelated shared-file hunk is changed or finalized"
  ],
  "fail_closed_conditions": [
    "the supplied project root is not the exact canonical Git top-level",
    "the probe exceeds its internal timeout",
    "Git is missing or returns a non-zero result",
    "porcelain output cannot be normalized safely",
    "focused isolation, real-root, timeout-cleanup, no-window, or frozen acceptance evidence fails"
  ],
  "essential_context_preservation": "Exact repository authority, fail-soft collision semantics, real-root protection, timeout containment, no-window execution, WI-5178 sequencing, and shared-file ownership remain explicit in code, tests, and review evidence."
}
```

## Spec-Derived Verification Plan

| Governing specification | Verification evidence | Expected result |
|---|---|---|
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`; `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`; `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | Focused authorization integration tests for nested non-repository roots, exact initialized roots, Git-unavailable/non-zero behavior, and bounded timeout cleanup | Nested roots launch no full status; exact roots report only their own dirt; every unavailable or timeout path returns no evidence and leaves no descendant. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Windows-focused subprocess argument assertion plus three repeated executions of the previously timing-out packet test under the repository default bound | All probes use hidden process settings; all repetitions pass; no harness or routing state changes. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | The complete focused test file and the frozen AT-AUTHORITY-OPERATION-TIME manifest activity | Focused tests pass and the frozen activity completes without the WI-5371 timeout while retaining every WI-5178 semantic assertion. |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001`; `GOV-FILE-BRIDGE-AUTHORITY-001` | Pre-start hashes, hunk-level diff review, matching claim/start packet, implementation report, and independent verdict | WI-5178 is already VERIFIED/finalized; only two attributable WI-5371 hunks are reviewed and finalized. |
| `GOV-STANDING-BACKLOG-001`; `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`; `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | WI-5371, TEST-11487, and the numbered proposal/report/verdict lifecycle | The item remains open until executable evidence is independently VERIFIED and mechanically finalized. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | In-root path inventory from the implementation report | All changed files and evidence remain inside the GT-KB root. |

## Risk / Rollback

The principal under-enforcement risk is incorrectly treating a legitimate Git
worktree as a nested non-repository root and silently skipping attributable
dirt. Tests must cover both a `.git` directory and worktree-style `.git` file,
normalize case and separators on Windows, and prove that the canonical
top-level equals the supplied root before status. The principal availability
risk is an internal timeout that is too short for a legitimate dirty root;
measure supported-load status duration, leave margin below pytest's outer
bound, and preserve the fail-soft contract.

Implementation begins only after WI-5178 finalization and a fresh two-target
hash inventory. Rollback is the exact later WI-5371 hunk set, never a whole-file
replacement. No database, dispatcher, TAFE, harness, bridge-routing, staging,
commit, push, deployment, release, credential, or cleanup action is part of
implementation.

## Bridge Filing

This proposal is filed through the governed numbered bridge namespace as the
next status-bearing file for `gtkb-wi5371-nested-git-root-containment`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` - corrects an authorization evidence-boundary and subprocess containment
defect that blocks a frozen release-candidate acceptance activity.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
