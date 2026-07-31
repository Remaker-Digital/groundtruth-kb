NEW

# WI-5425: Isolate non-impairment tests from live membership state

bridge_kind: prime_proposal
Document: gtkb-wi5425-nonimpairment-test-membership-isolation
Version: 001
Author: Prime Builder Codex A
Date: 2026-07-17T03:53:08Z

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: codex-desktop-019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: OpenAI Codex
author_model_version: GPT-5.5
author_model_configuration: desktop interactive Prime Builder A

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5425

target_paths: ["platform_tests/hooks/test_modernization_nonimpairment_proposal_gate.py"]

implementation_scope: test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Adopt the current one-file test-isolation hunk in
`platform_tests/hooks/test_modernization_nonimpairment_proposal_gate.py`.
The local `_deny` helper temporarily replaces the live
`_wi_project_membership_gap` check while exercising the independent structured
non-impairment disposition gate, then restores the original callable in a
`finally` block. This keeps one gate's unit tests from being preempted by
unrelated live MemBase membership state.

The production bridge-compliance gate remains byte-for-byte unchanged. The
candidate file is 5,066 bytes with SHA-256
`4BE626AFC4CD417E84E119527DE082D46215646113D9478D793B240A35BF018E`.
The LF-rendered exact `git diff` has SHA-256
`59E6528A0CA8B9FAF05B9C7946581CA48E21E2EEEACC3248F05217788593D979`.
Any additional path or byte drift invalidates this review.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires independent GO and VERIFIED before the protected test hunk can be finalized.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires complete applicable requirement linkage.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - binds this repair to WI-5425 and the active Tree Stabilization PAUTH.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires executed spec-to-test evidence for terminal verification.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - prevents project authorization from replacing GO, claim, or implementation-start authority.
- `GOV-STANDING-BACKLOG-001` - governs WI-5425 and linked TEST-11536.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - requires the gate under test to remain independently evaluable without weakening any hard invariant.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - requires the focused test to evaluate the declared control rather than fail on unrelated live state.
- `GOV-WORK-TREE-HYGIENE-001` - requires exact one-hunk ownership without absorbing adjacent or unrelated dirt.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - requires this discovered residue to remain linked across work-item, test, proposal, and verification artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - preserves the one-hunk change as part of the durable artifact graph rather than an unexplained tree edit.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - keeps candidate, approved, verified, and finalized states distinct.

## Prior Deliberations

- `DELIB-20260710-GTKB-MODERNIZATION-NONIMPAIRMENT-GOV-APPROVAL` - approved the structured non-impairment control whose focused test is being isolated.
- `DELIB-202666274` - authorized the Tree Stabilization project scope while retaining exact bridge, start, verification, and Git-mechanic gates.

## Owner Decisions / Input

No new owner decision is required. The owner authorized the full modernization
program, directed every discovered orphaned residue into an `origin=hygiene`
work item, and requires exact independently reviewed clearing of all worktree
dirt. This proposal performs no implementation or Git mechanic.

## Requirement Sufficiency

Existing requirements sufficient - the non-impairment, artifact-evaluability,
worktree-hygiene, bridge-authority, and spec-derived-verification requirements
already define the required isolated and fail-closed behavior.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5425 exact ownership audit at HEAD 42a252ab57b5a203e9406b626c741d897e8fb196",
  "canonical_authority": "Production bridge-compliance behavior plus the focused non-impairment gate test contract",
  "primary_route": "Temporarily isolate only the unrelated membership predicate inside the local test helper and restore it in finally",
  "before_behavior": "A structured non-impairment test can be preempted by live project-membership state and fail for a control outside its asserted subject",
  "after_behavior": "The focused test deterministically evaluates only the non-impairment disposition while the production membership gate remains unchanged",
  "self_descriptive_naming": "_deny, membership_check, and _wi_project_membership_gap expose the bounded test seam",
  "obsolete_guidance_disposition": "No guidance becomes obsolete; the test keeps both production controls distinct",
  "history_preservation": "The committed WI-5166 baseline and all gate history remain unchanged; this is one additive test-harness correction",
  "baseline": "One dirty test hunk; 12 focused tests pass in the current candidate",
  "expected_result": "All 12 focused tests pass, exception restoration is proven, and no production gate path changes",
  "rollback": "A separately authorized exact rollback removes only this test hunk",
  "hard_invariants": "No production membership weakening, no bridge or dispatcher mutation, no harness interaction, no groundtruth.db finalization, no Git mechanic, and no unrelated path capture",
  "fail_closed_conditions": "File or diff hash drift, failed restoration proof, production gate diff, extra target, missing authority, or failed focused test blocks finalization",
  "essential_context_preservation": "The distinction between live project-membership enforcement and structured non-impairment disposition enforcement remains explicit"
}
```

## Spec-Derived Verification Plan

| Requirement | Verification | Expected result |
|---|---|---|
| Exact scope; `GOV-WORK-TREE-HYGIENE-001` | Recompute the sole file and LF diff hashes; run `git diff --check` | Both hashes match this proposal, no whitespace errors, and no second path is present. |
| Isolated non-impairment evaluability | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/hooks/test_modernization_nonimpairment_proposal_gate.py -q --tb=short --timeout=300` | 12 tests pass. |
| Exception-safe restoration | Invoke `_deny` with a fixture whose `_deny_reason_for_content` raises, then assert the original `_wi_project_membership_gap` object is restored | The exception propagates and the original callable identity is restored. |
| Production control preservation | `git diff --quiet -- .claude/hooks/bridge-compliance-gate.py` | Exit 0; production gate bytes are unchanged. |
| Test quality | Run Ruff check and format-check on the sole test path | Both exit 0. |
| Bridge/project authority | Validate active PAUTH, independent GO, matching claim/start, WI-5425/TEST-11536 linkage, and independent post-implementation verdict through governed CLI surfaces | Every transition is current and exact; no project scope substitutes for a bridge/start gate. |

## Risk / Rollback

The main risk is that a broad monkeypatch could hide a real integration defect or
leak into later tests. The hunk limits replacement to one helper call and
restores the original object in `finally`; independent review must exercise the
raising path as well as the ordinary 12-test suite.

Rollback is an exact one-hunk reversal. It must not touch the production gate,
WI-5166 source, live MemBase state, bridge chains, or unrelated worktree paths.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5425-nonimpairment-test-membership-isolation`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`test` - the sole behavior change is deterministic isolation of one focused
test helper.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
