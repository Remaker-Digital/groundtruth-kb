REVISED

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: A-2026-07-16T12-17-36Z
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined ::init gtkb pb

# WI-5350 revised proposal: location-robust fresh-worker source isolation

bridge_kind: prime_proposal
Document: gtkb-wi5350-wi5155-fresh-worker-acceptance-baseline
Version: 007
Responds to: bridge/gtkb-wi5350-wi5155-fresh-worker-acceptance-baseline-006.md
Date: 2026-07-16 UTC
Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5350

target_paths: ["platform_tests/scripts/test_modernization_fresh_worker.py"]

implementation_scope: one assertion correction in one acceptance test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Correct the single stale environmental assertion identified by version 006.
The test already proves the imported module is inside the newly created venv.
Its additional assertion that the module path must not be relative to
`REPO_ROOT` is invalid when governed pytest temporary storage itself lives
under `E:/GT-KB/.pytest-tmp`.

Replace only that redundant root-relative assertion with a direct comparison
against the repository source module path. This preserves the actual contract:
the wheel-installed worker must import from its venv and must not import
`groundtruth-kb/src/groundtruth_kb/__init__.py`, regardless of where the venv
directory is physically rooted.

## Requirement Sufficiency

Existing requirements are sufficient. This changes no product behavior or
fresh-worker authority contract; it makes the acceptance assertion accurately
measure source-tree isolation in every governed temporary-directory layout.

## Specification Links

- `DCL-ACTIVITY-CONTEXT-MANIFEST-001`
- `ADR-ACTIVITY-ENVELOPE-DISPOSITION-001`
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001`
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`

## Prior Deliberations

- `DELIB-20260710-GTKB-MODERNIZATION-GATE-1-READINESS-AUTHORIZATION`
- `DELIB-202666274`
- Versions 001 through 006 preserve the original exact baseline, prior GO,
  implementation reports, and the independently reproduced location failure.

## Owner Decisions / Input

No new owner decision is required. The active Assurance PAUTH covers bounded
acceptance-test corrections while preserving GO, claim, start, independent
verification, and Git-finalization gates.

## Proposed Scope

1. In `test_built_wheel_assembles_context_without_source_tree_or_root_config`,
   resolve the reported module path once.
2. Preserve the assertion that the module path is inside the fresh venv.
3. Replace `not module_path.is_relative_to(REPO_ROOT)` with exact inequality
   against the resolved repository source module
   `BUILD_PROJECT/src/groundtruth_kb/__init__.py`.
4. Change no fixture placement, wheel builder, production source, timeout,
   package resource, or other test.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5350 version 006 independent failure evidence; DELIB-202666274",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001; DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001",
  "primary_route": "directly prove venv containment and inequality from the repository source module",
  "before_behavior": "A valid wheel import fails when its governed temporary venv is physically under the repository root.",
  "after_behavior": "The test rejects the repository source module while accepting the wheel-installed module regardless of temporary-root placement.",
  "self_descriptive_naming": "module_path and source_module_path name the two compared authorities.",
  "obsolete_guidance_disposition": "Remove only the stale implication that every venv must live outside E:/GT-KB; retain the source-tree isolation requirement.",
  "history_preservation": "Versions 001-006, the exact pre-change hash, independent failure, one-hunk revision, report, and verdict remain append-only.",
  "baseline": {
    "target_sha256": "8A3C32384031A272070C304FCA99634C0E5360C16841475E88FF7A5756C1751A",
    "focused_result": "3 passed, 1 failed because .pytest-tmp is in-root"
  },
  "expected_result": {
    "focused": "4 passed",
    "production_changes": 0
  },
  "rollback": {
    "instructions": "Revert only the assertion hunk through a governed successor.",
    "verification": "Rerun the four-test module and Ruff checks."
  },
  "hard_invariants": [
    "module remains inside the fresh venv",
    "module differs from the repository source module",
    "all scratch evidence remains under E:/GT-KB",
    "production source and package resources remain unchanged"
  ],
  "fail_closed_conditions": [
    "venv-containment assertion removed",
    "source module accepted",
    "fixture moved outside the project root",
    "unrelated test or production byte changes"
  ],
  "essential_context_preservation": "Retain the wheel build, source-free subprocess, root-config absence, packaged-default origin, and exact module provenance checks."
}
```

## Specification-Derived Verification Plan

| Requirement | Command | Expected result |
| --- | --- | --- |
| Fresh-worker source isolation | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_modernization_fresh_worker.py -q --tb=short --timeout=600` | All four tests pass with governed in-root pytest temporary storage. |
| Evaluability and hygiene | `groundtruth-kb/.venv/Scripts/python.exe -m ruff check platform_tests/scripts/test_modernization_fresh_worker.py` and `python -m ruff format --check` | Both gates pass on the sole target. |
| Exact scope | `git diff --check -- platform_tests/scripts/test_modernization_fresh_worker.py` plus hunk inspection | Only the module-path assertion hunk changes. |
| Nonimpairment | Run the focused test once with the repository-managed temp root and inspect the subprocess payload | Module remains under the venv, differs from the source module, and packaged defaults remain authoritative. |

## Acceptance Criteria

- The complete four-test module passes under `E:/GT-KB/.pytest-tmp`.
- The imported module is proven inside the fresh venv.
- The imported module is proven unequal to the repository source module.
- Production code and every other test byte remain unchanged.
- Independent VERIFIED precedes any finalization.

## Risk And Rollback

The risk is weakening source-tree isolation into a tautology. Retaining the
venv-containment assertion and adding exact source-module inequality preserves
two independent checks. Rollback is the one assertion hunk through a governed
successor.

## Recommended Commit Type

`test`

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
