NEW

# gtkb-wi5406-artifact-lifecycle-timeout-reliability (Slice 1) - Bound the intentional two-scan determinism test

bridge_kind: prime_proposal
Document: gtkb-wi5406-artifact-lifecycle-timeout-reliability
Version: 001
Author: Prime Builder Codex A
Date: 2026-07-17 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: codex-desktop-019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: interactive desktop Prime Builder A

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ARTIFACT-DECONTAMINATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ARTIFACT-DECONTAMINATION
Work Item: WI-5406

target_paths: ["platform_tests/scripts/test_modernization_artifact_decontamination.py"]

implementation_scope: test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Restore the narrow test-local timeout that terminal predecessor WI-5335
specified but that is absent from the current file. Add
`@pytest.mark.timeout(600)` only to
`test_effective_loading_graph_is_repeatable`. The test continues to perform two
complete repository loading-graph scans, compare canonical bytes, and execute
every existing graph assertion.

The repository-wide timeout remains 30 seconds. The exact frozen
AT-ARTIFACT-LIFECYCLE lane passed in the current worktree on 2026-07-17
(`24 passed` in 35.13 seconds), but the same unchanged test has repeatedly
exceeded the per-test bound under load. The local 600-second ceiling matches
WI-5335's measured proposal and the frozen acceptance runner's outer
`timeout_seconds: 600`; it removes load-sensitive false failures without
weakening behavior or permitting an unbounded scan.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires independent GO before the
  protected test file changes and independent VERIFIED before completion.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires this
  proposal to link the implementation and verification plan to live
  specifications.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires explicit
  project, work-item, PAUTH, target-path, and slice linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires independent
  verification against the cited specification-derived commands.
- `GOV-STANDING-BACKLOG-001` - governs WI-5406 as the successor hygiene item
  rather than rewriting terminal WI-5335 history.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - requires the reliability fix to
  preserve behavior, bounded execution, and every existing assertion.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - requires current,
  reproducible evidence for this change-controlled acceptance test.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - requires the observed reliability
  defect and its disposition to remain visible as durable governed artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - requires traceability from WI-5406
  through proposal, test evidence, implementation report, and verification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - requires explicit lifecycle states
  rather than treating a transient green run as proof that the known defect is
  complete.

## Prior Deliberations

- WI-5335 established the measured design: preserve both scans and all
  assertions, prefer optimization when it provides reliable margin, otherwise
  use a narrow 600-second test-local ceiling. Its terminal history is not
  reopened or rewritten.
- WI-5406 records the current-state omission and is the sole successor work
  item for restoring the missing hunk.
- `INTAKE-e0d49108` is respected by appending this successor proposal and
  leaving the prior work-item and bridge lifecycle history intact.

## Owner Decisions / Input

No new owner decision is required. The owner authorized the full modernization
program and directed discovered flaws to be recorded as hygiene work items and
continued where possible. The active project authorization is
`PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ARTIFACT-DECONTAMINATION-20260715-PROJECT-SCOPE`.
Implementation still requires an independent bridge GO plus matching
work-intent and implementation-start authority.

## Requirement Sufficiency

Existing requirements sufficient. The non-impairment, evaluability, bridge
authority, project-linkage, and specification-derived verification
requirements cited above fully determine the one-line test-only repair. No new
runtime behavior, policy, dependency, interface, or authority is introduced.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5406 successor evidence and terminal predecessor WI-5335 measured timeout design",
  "canonical_authority": "config/governance/modernization-release-candidate.json AT-ARTIFACT-LIFECYCLE plus GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "the existing frozen pytest acceptance command",
  "before_behavior": "the intentional second full repository scan inherits the global 30-second per-test timeout and can fail solely because of workstation load",
  "after_behavior": "the same two complete scans and assertions run under a test-local 600-second ceiling while every other test retains the global 30-second timeout",
  "self_descriptive_naming": "the existing repeatability test name remains accurate; no new public name is introduced",
  "obsolete_guidance_disposition": "none; terminal WI-5335 history is preserved and WI-5406 supplies the missing successor hunk",
  "history_preservation": "append-only proposal and work-item linkage; no prior artifact is rewritten",
  "baseline": "24 passed in 35.13 seconds on 2026-07-17, with prior reproducible per-test timeout failures under load",
  "expected_result": "two consecutive exact frozen-lane runs pass with all 24 tests and no global-timeout change",
  "rollback": "remove the single test-local pytest timeout decorator",
  "hard_invariants": [
    "perform both complete loading-graph scans",
    "compare canonical report bytes",
    "preserve every existing graph assertion",
    "retain the repository-wide 30-second timeout",
    "retain a finite outer bound aligned with the frozen 600-second acceptance timeout"
  ],
  "fail_closed_conditions": [
    "any scan is skipped or narrowed",
    "any assertion is removed or weakened",
    "the global timeout changes",
    "the exact frozen lane fails",
    "the target diff contains anything beyond the local marker and required import compatibility"
  ],
  "essential_context_preservation": "the test remains in the frozen AT-ARTIFACT-LIFECYCLE file and exercises the production loading-graph discovery surface twice"
}
```

## Spec-Derived Verification Plan

1. `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` and
   `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_modernization_artifact_decontamination.py -q --tb=short
```

Run the exact frozen lane twice. Each run must report `24 passed`; the
repeatability test must still execute both full scans and all existing
assertions.

2. `GOV-FILE-BRIDGE-AUTHORITY-001`,
   `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`,
   `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, and
   `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, together with the
   artifact-oriented governance and lifecycle specifications:

```text
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5406-artifact-lifecycle-timeout-reliability --json
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5406-artifact-lifecycle-timeout-reliability
```

Both preflights must pass, and independent Loyal Opposition must verify the
exact hunk and test evidence before completion.

3. Static scope and style:

```text
groundtruth-kb/.venv/Scripts/python.exe -m ruff check platform_tests/scripts/test_modernization_artifact_decontamination.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check platform_tests/scripts/test_modernization_artifact_decontamination.py
git diff --check -- platform_tests/scripts/test_modernization_artifact_decontamination.py
git diff -- platform_tests/scripts/test_modernization_artifact_decontamination.py
```

The checks must be clean. The semantic diff must be limited to the single local
timeout decorator; `pytest` is already imported by the file.

## Risk / Rollback

Risk is low and test-only. A 600-second marker could delay detection of a true
hang in this one expensive test, but it remains finite, matches the frozen
runner's outer ceiling, and leaves the global 30-second policy intact. Rollback
is removal of the one decorator in the same scoped finalization transaction.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5406-artifact-lifecycle-timeout-reliability`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`test` - the entire implementation is a reliability bound on one existing
acceptance test, with no production behavior change.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
