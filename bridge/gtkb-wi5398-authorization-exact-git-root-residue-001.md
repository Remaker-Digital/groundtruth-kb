NEW

# WI-5398 - Close the missing exact-root authorization repair

bridge_kind: prime_proposal
Document: gtkb-wi5398-authorization-exact-git-root-residue
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-17 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop Prime Builder; current worktree authoritative; no direct harness contact

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5398

target_paths: ["scripts/implementation_authorization.py", "platform_tests/scripts/test_implementation_authorization.py"]

implementation_scope: exact-root and bounded dirty-path discovery only
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Implement the physical repair that WI-5371 described but did not leave in the
current source. WI-5371 was reconciled as resolved from terminal workflow
metadata, yet `_dirty_worktree_paths()` still launches an unbounded full status
from any supplied directory and never proves that the directory is the exact
Git top-level. An isolated pytest root below GT-KB therefore borrows the dirty
ancestor repository, can exceed the default test timeout, and can leave Git
work after the test has already failed.

Reject non-exact roots before full status, use bounded hidden Git probes with
complete descendant cleanup, and preserve the existing fail-soft authorization
contract: only positive dirty evidence from the exact named project may block a
claim. This proposal is a strict successor to WI-5178 because both target files
contain WI-5178 work; no WI-5398 mutation may begin until WI-5178 is
independently VERIFIED and mechanically finalized.

## Specification Links

- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - collision evidence must be
  attributable to the exact named project.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - operation-time
  authority checks must remain deterministic and bounded.
- `DCL-PROJECT-DEPENDENCY-ORDERING-001` - WI-5178 finalization is a hard
  predecessor for both shared files.
- `GOV-WORK-TREE-HYGIENE-001` - foreign ancestor dirt must not be absorbed into
  an isolated claim decision.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - root mismatch, timeout,
  failure, and malformed output require explicit testable behavior.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - real-root commingle protection
  remains active and no harness is impaired.
- `ADR-GOVERNED-TWO-TIER-GIT-LIFECYCLE-001` - Git evidence is valid only for
  its bound project/worktree identity.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all targets and evidence remain
  in-root under `E:/GT-KB`.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` - the frozen authority activity
  must complete under its declared bounds.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - independent GO and VERIFIED are mandatory.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the exact shared
  targets, predecessor, and requirements are linked.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - PAUTH, project, work
  item, and targets are explicit.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - nested-root, exact-root,
  timeout, cleanup, no-window, and frozen acceptance cases are executed.
- `GOV-STANDING-BACKLOG-001` - WI-5398 owns the remaining physical residue.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - WI-5371 history, live source,
  successor tests, verdict, and finalization remain traceable.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - terminal metadata contradicted by
  current source and acceptance creates a successor lifecycle.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the contradiction is preserved as
  hygiene work rather than hidden.

## Prior Deliberations

- `DELIB-202666274` - authorizes modernization at project scope while retaining
  review, predecessor, and mechanical gates.
- `DELIB-WI5066-INDEP-ROOTCAUSE-COMMINGLE-HAZARD-20260709` - dirty-path
  attribution must be exact and must preserve unrelated work.
- Owner directive, 2026-07-16 - repair Git/process defects without disabling,
  deprioritizing, or making any harness ineligible.
- WI-5178 - owns the current shared source/test baseline.
- WI-5371 - preserves the original design and terminal history but is not
  evidence that the physical repair exists.
- WI-5386 - separately owns the general metadata-only reconciliation defect.

## Owner Decisions / Input

No new owner decision is required. The implementation is source/test only and
does not mutate dispatcher, TAFE, routing, harness roles or eligibility,
credentials, Git state, deployment, release, or cleanup.

## Requirement Sufficiency

Existing requirements are sufficient. Exact authorization attribution,
bounded operation-time evaluation, fail-soft behavior, and nonimpairment fully
define the repair.

## Proposed Scope

1. Fail closed unless WI-5178 is independently VERIFIED and mechanically
   finalized as the exact two-file parent baseline.
2. Before full status, require a local Git marker and resolve canonical
   top-level with a short bounded hidden probe.
3. If the supplied root and canonical top-level differ after normalized Windows
   path comparison, return no attributable dirty evidence and do not run status.
4. Run exact-root porcelain status through the existing bounded no-window
   subprocess convention with complete descendant cleanup.
5. Preserve the current parser, rename/copy handling, and fail-soft return of no
   evidence for missing Git, non-zero exit, malformed output, or timeout.
6. Add focused tests for nested non-repository roots, exact directory and
   worktree roots, timeout cleanup, hidden launch settings, output parsing, and
   real-root collision preservation.
7. Rerun the unchanged frozen authority-operation activity after WI-5178; do
   not increase pytest timeouts or weaken its assertions.

## Specification-Derived Verification Plan

| Requirement | Verification | Expected result |
|---|---|---|
| WI-5178 ordering | Confirm exact shared-file hashes are committed before claim/start. | WI-5398 owns only later bounded-root hunks. |
| Exact project attribution | Exercise nested non-repository, exact repository, and linked-worktree fixtures. | Nested roots launch no full status; exact roots report only their own dirt. |
| Bounded process behavior | Simulate top-level and status timeouts, failures, and malformed output on Windows. | Return is fail-soft, hidden, bounded, and leaves no descendant. |
| Commingle protection | Run existing positive collision and rename/copy parsing tests. | Exact-root dirty paths still block unauthorized overlap. |
| Frozen activity | Run the exact authority-operation command unchanged. | WI-5398 timeout class is absent; WI-5178 semantic assertions remain intact. |
| Scope and review | Inspect two-target hunk diff and require independent review. | No unrelated bytes change; VERIFIED precedes finalization. |

## Intuitiveness/Non-Impairment Disposition

```json
{"schema_version":1,"applicability":"applicable","provenance":"WI-5398; current source inspection after WI-5371 metadata-only reconciliation; frozen authority-operation evidence","canonical_authority":"GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001; GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001","primary_route":"exact normalized Git top-level identity followed by bounded hidden status","before_behavior":"Any nested directory can inherit the ancestor GT-KB repository, scan foreign dirt without a timeout, and outlive the failing test.","after_behavior":"Only the exact project root supplies dirty-path evidence; every probe is hidden, bounded, fail-soft, and completely cleaned up.","self_descriptive_naming":"Exact-root and bounded-probe helpers state repository authority and failure semantics directly.","obsolete_guidance_disposition":"WI-5371 terminal history remains; WI-5398 supplies the missing physical implementation without changing acceptance bounds or harness availability.","history_preservation":"WI-5178 baseline, WI-5371 design/verdict history, WI-5386 reconciler repair, WI-5398 patch, tests, and independent verdict remain separate.","baseline":{"exact_root_check":false,"internal_timeout":false,"frozen_authority":"18 failed, 388 passed after approximately 41 minutes"},"expected_result":{"nested_ancestor_scans":0,"leaked_descendants":0,"real_root_collision_preserved":true,"frozen_timeout_class":0},"rollback":{"instructions":"Revert only WI-5398 hunks through a governed successor after preserving WI-5178.","verification":"focused authorization tests plus unchanged frozen activity"},"hard_invariants":["WI-5178 committed predecessor","real exact-root collision protection preserved","fail-soft unavailable behavior preserved","no visible console","no leaked descendants","no harness, dispatcher, TAFE, routing, role, eligibility, credential, deployment, or unrelated Git mutation"],"fail_closed_conditions":["supplied root differs from canonical top-level","probe timeout or error","porcelain cannot be normalized","frozen assertions are weakened","GO, claim, start, or independent verification is absent"],"essential_context_preservation":"Retain exact project attribution, fail-soft collision semantics, real-root protection, bounded no-window cleanup, WI-5178 sequencing, and WI-5371 historical contradiction."}
```

## Acceptance Criteria

1. WI-5178 is independently VERIFIED and mechanically finalized first.
2. Nested non-repository fixture roots never scan the ancestor GT-KB worktree.
3. Exact repositories and linked worktrees retain collision evidence.
4. Every Git probe is hidden, bounded, fail-soft, and leaves no descendant.
5. Existing parsing and commingle-protection tests remain green.
6. The unchanged frozen authority activity has no WI-5398 timeout failure.
7. No harness or dispatcher/TAFE/routing/eligibility state changes.
8. Independent VERIFIED precedes exact hunk finalization.

## Risk / Rollback

The under-enforcement risk is incorrectly rejecting a legitimate linked
worktree. Tests cover both directory and file Git markers and compare the
canonical worktree top-level, not the shared common directory. The availability
risk is a timeout too short for supported load; use a bounded margin below the
outer test limit while retaining fail-soft semantics. Rollback is the exact
WI-5398 hunk set through a governed successor.

## Bridge Filing

File through the governed Codex non-bypass helper as the next numbered bridge
file. The numbered bridge file chain is append-only; no prior version is
deleted or rewritten. Deterministic TAFE routing remains external.

## Recommended Commit Type

`fix` - restore exact, bounded authorization evidence discovery.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
