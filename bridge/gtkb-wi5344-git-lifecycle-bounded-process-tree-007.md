REVISED

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: A-2026-07-16T12-17-36Z
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined ::init gtkb pb

# WI-5344 revised proposal: baseline dependency closed

bridge_kind: prime_proposal
Document: gtkb-wi5344-git-lifecycle-bounded-process-tree
Version: 007
Responds to: bridge/gtkb-wi5344-git-lifecycle-bounded-process-tree-006.md
Approved design: bridge/gtkb-wi5344-git-lifecycle-bounded-process-tree-001.md
Date: 2026-07-16 UTC
Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-GIT-LIFECYCLE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-GIT-LIFECYCLE
Work Item: WI-5344

target_paths: ["platform_tests/scripts/test_modernization_git_lifecycle.py"]

implementation_scope: frozen acceptance test runtime
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Re-submit the unchanged one-file bounded-process-tree repair after satisfying
the sole version-006 blocker. WI-5354 is now independently VERIFIED at
`bridge/gtkb-wi5354-git-lifecycle-acceptance-baseline-004.md`, and both frozen
baseline paths are clean and tracked in current HEAD `42a252ab` with the exact
approved hashes:

- `scripts/check_modernization_git_lifecycle.py`:
  `FFB2ED61FA8D71496202B1A80BB7C7831233E10240C62FE7FC4EE7194ECC73C4`
- `platform_tests/scripts/test_modernization_git_lifecycle.py`:
  `AD497F681853B0661DA2A63ECF5D4BED668129E04D43C68D84E75EA63F0A7536`

No implementation byte is changed by this revision. After a fresh independent
GO, Prime may modify only the wrapper target to implement the original
600-second child, 750-second wrapper, and 900-second activity ordering with
hidden process launch and complete process-tree termination on timeout.

## Requirement Sufficiency

Existing requirements remain sufficient. Version 001's measured runtime,
timeout ordering, helper selection, failure semantics, and one-file scope are
unchanged; only the prerequisite state has advanced.

## Specification Links

- `ADR-GOVERNED-TWO-TIER-GIT-LIFECYCLE-001`
- `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001`
- `DCL-GIT-BRANCH-BINDING-PROMOTION-001`
- `GOV-GTKB-PUBLISHED-STATE-SOT-DEFERENCE-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Prior Deliberations

- `INTAKE-c5792b0c`
- `DELIB-20260710-GTKB-MODERNIZATION-GIT-LIFECYCLE-CHARTER`
- `DELIB-202666274`
- WI-5354 versions 001-004 establish and independently verify the exact
  prerequisite baseline.

## Owner Decisions / Input

No new owner decision is required. The active project PAUTH covers this exact
test repair while retaining GO, claim, start, verification, and Git gates.

## Proposed Scope

1. Preserve the checker and all 26 assertions byte-for-byte.
2. Change only the pytest wrapper target.
3. Replace the 180-second test marker with 750 seconds.
4. Replace `subprocess.run(..., timeout=900)` with hidden/new-group `Popen`
   and `communicate(timeout=600)`.
5. On timeout, invoke the existing `_terminate_process_tree`, retain bounded
   diagnostics, and fail.
6. Add one fast monkeypatched regression proving timeout calls tree termination
   and cannot report PASS.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5354 VERIFIED -004; WI-5344 NO-GO -006; DELIB-202666274",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "one frozen-wrapper repair using existing hidden-process and tree-termination helpers",
  "before_behavior": "A 180-second wrapper interrupts a valid checker while its child timeout cannot govern first.",
  "after_behavior": "Nested 600/750/900 bounds preserve complete execution and terminate the child tree on timeout.",
  "self_descriptive_naming": "child and wrapper timeout constants state the envelope directly.",
  "obsolete_guidance_disposition": "The inconsistent 180/900 ordering is replaced; all checker assertions remain current.",
  "history_preservation": "WI-5354 owns baseline bytes, WI-5344 owns this wrapper hunk, and WI-5261 retains broader wrapper work.",
  "baseline": {"checker_assertions": 26, "checker_sha256": "FFB2ED61FA8D71496202B1A80BB7C7831233E10240C62FE7FC4EE7194ECC73C4"},
  "expected_result": {"child_timeout_seconds": 600, "wrapper_timeout_seconds": 750, "activity_timeout_seconds": 900},
  "rollback": {"instructions": "Revert only the wrapper hunk through a governed successor.", "verification": "Rerun timeout regression and exact frozen activity."},
  "hard_invariants": ["all 26 assertions remain", "timeout remains failure", "complete child tree is terminated", "no console or harness change"],
  "fail_closed_conditions": ["baseline hash changes", "checker/shared helper edit", "child bound is not lowest", "timeout passes or leaks descendants"],
  "essential_context_preservation": "Retain the full checker payload, diagnostics, frozen activity ceiling, and cross-platform process-tree behavior."
}
```

## Specification-Derived Verification Plan

| Requirement | Command | Expected result |
| --- | --- | --- |
| Frozen lifecycle contract | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_modernization_git_lifecycle.py -q --tb=short` | Wrapper passes; checker reports CAP-GIT-LIFECYCLE and A1-A26 PASS. |
| Timeout failure and cleanup | Focused `-k timeout` plus `test_terminate_process_tree_reaps_grandchild_on_windows` | Forced timeout calls tree termination, fails, and leaves no child/grandchild. |
| Nonimpairment | Run exact frozen activity three times under current workstation load | Three bounded passes; no console, leaked process, dispatcher, role, or eligibility change. |
| Scope | Ruff check/format and `git diff --check` on sole target | Only the approved wrapper/test hunk exists. |

## Acceptance Criteria

- WI-5354 baseline hashes remain exact at implementation start.
- All 26 checker assertions remain mandatory and pass.
- Timeout always fails after complete process-tree termination.
- Child, wrapper, and activity bounds remain strictly ordered 600/750/900.
- Independent VERIFIED precedes finalization.

## Risk And Rollback

The original risks and rollback remain unchanged. An undersized child bound
causes false failures; a bare child kill leaks descendants. Rollback is limited
to the one wrapper hunk through a governed successor.

## Recommended Commit Type

`test`

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
