NEW
::init gtkb lo
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: OpenAI Codex
author_model_version: gpt-5.5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role; build activity envelope; approval_policy=never
author_metadata_source: explicit_interactive_session_metadata

# Implementation Proposal - Populate Cursor E dispatcher telemetry worker provenance on successful and failed runs

bridge_kind: prime_proposal
Document: gtkb-wi5369-cursor-dispatch-telemetry-provenance
Version: 001
Date: 2026-07-17 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5369-CURSOR-TELEMETRY-PROVENANCE-20260717
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5369

target_paths: ["platform_tests/scripts/test_cursor_dispatch_telemetry_provenance.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Add one isolated production-path integration test proving that the existing role-neutral dispatch telemetry reconciliation records Cursor E worker, model, status, and error provenance on successful and failed runs without changing production source.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5369; TEST-11485; PAUTH-DISPATCHER-BLACK-BOX-WI5369-CURSOR-TELEMETRY-PROVENANCE-20260717",
  "canonical_authority": "SPEC-SHIM-HARNESS-DISPATCH-TELEMETRY-001; GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001; GOV-HARNESS-ONBOARDING-CONTRACT-001",
  "primary_route": "platform_tests/scripts/test_cursor_dispatch_telemetry_provenance.py exercising the existing dispatcher exit-reconciliation and shim telemetry APIs",
  "before_behavior": "Generic telemetry unit coverage passes, but no isolated installed production-path regression proves Cursor E provenance on both successful and failed dispatch completion.",
  "after_behavior": "The new integration test proves Cursor E dispatch id, harness id, provider, model, completion status, exit code, and failure diagnostic provenance through the existing role-neutral production path.",
  "self_descriptive_naming": "The test module and cases name Cursor dispatch telemetry provenance and success or failure behavior explicitly.",
  "obsolete_guidance_disposition": "No guidance is replaced; the test converts an unproven parity assumption into executable evidence while preserving existing generic tests.",
  "history_preservation": "Existing bridge, telemetry, dispatch, and test history remain unchanged; this slice adds one new test file only.",
  "baseline": {"shim_telemetry_suite": "23 tests passed", "runtime_reconciliation_subset": "3 tests passed", "cursor_specific_production_path": "missing"},
  "expected_result": {"success_case": "Cursor E provenance is persisted with completed status and no fabricated failure.", "failure_case": "Cursor E provenance is persisted with failed status, nonzero exit code, and the actual diagnostic.", "production_source": "unchanged"},
  "rollback": "Remove only the new governed test file after an independently approved revert; no production or historical artifact requires rollback.",
  "hard_invariants": ["No production source mutation.", "No dispatcher, TAFE, harness registry, eligibility, lease, worker, credential, Git staging, push, deployment, or release mutation.", "Existing A, B, C, D, F, and H telemetry behavior remains governed by the same role-neutral implementation."],
  "fail_closed_conditions": ["The test cannot exercise the real production reconciliation API.", "Cursor E identity, model, success status, failure status, exit code, or diagnostic is absent or synthetic.", "The new target is no longer isolated from parallel-session changes."],
  "essential_context_preservation": "The test retains dispatch identity, harness identity, provider and model provenance, terminal status, exit code, diagnostic, session linkage, and the existing generic telemetry contract."
}
```

Work item description: Current dispatcher-produced Cursor E telemetry keeps every worker field null on both successful governed verdict runs and classified timeout exits. Evidence includes successful dispatch 2026-07-16T21-16-19Z-loyal-opposition-E-49b8df and exit-124 dispatches 2026-07-16T21-22-19Z-loyal-opposition-E-f95390, 2026-07-16T21-24-34Z-loyal-opposition-E-a07ac1, 2026-07-16T21-27-07Z-loyal-opposition-E-3f38b8, and 2026-07-16T21-27-41Z-loyal-opposition-E-66ad40. WI-5255 proposes the shared role-neutral dispatcher reconciliation substrate but its reviewed title, evidence, tests, and acceptance explicitly cover B/C and declare E inert/out of scope. Extend trusted provenance coverage to E without parsing verdict prose: identity/model fields come from dispatcher-selected context, role/source only from a matching per-dispatch session document, missing or conflicting authority stays fail-closed with a bounded diagnostic, and richer provider records are preserved. Sequence after WI-5255 and the coherent implementation-authorization baseline required by its latest NO-GO; do not mutate retained telemetry, runtime state, eligibility, leases, or unrelated dirty source.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5369` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `platform_tests/scripts/test_cursor_dispatch_telemetry_provenance.py`.

## Specification Links

- `SPEC-SHIM-HARNESS-DISPATCH-TELEMETRY-001` - auto-linked governing or work-item specification.
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
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - auto-linked governing or work-item specification.
- `GOV-SESSION-ROLE-AUTHORITY-001` - auto-linked governing or work-item specification.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - auto-linked governing or work-item specification.
- `DCL-DISPATCH-ENVELOPE-RULES-001` - auto-linked governing or work-item specification.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - auto-linked governing or work-item specification.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-202666374` - Loyal Opposition Review - WI-5153 fail-closed artifact evaluability
- `DELIB-202666410` - Loyal Opposition Defect-Fix Proposal Review - GO - WI-5227 Ollama D Abrupt-Exit Diagnostics
- `DELIB-202666551` - Loyal Opposition Proposal Review - GO - WI-5345 Cursor Timeout Recovery
- `DELIB-202666260` - Loyal Opposition Proposal Review - WI-5255 B/C Telemetry Worker Provenance
- `DELIB-202666230` - Reviewed Body

## Owner Decisions / Input

- `PAUTH-DISPATCHER-BLACK-BOX-WI5369-CURSOR-TELEMETRY-PROVENANCE-20260717` - active project authorization covering `WI-5369`.

## Proposed Scope

- Add one isolated integration test for Cursor E success and failed-run telemetry provenance through the existing production reconciliation path.
- Assert dispatch id, harness id E, provider, actual model, terminal status, exit code, diagnostic, and session linkage without mocking away the production API boundary.
- Do not modify dispatcher_runtime.py or shim_dispatch_telemetry.py; if the current role-neutral implementation fails, return through the bridge for an explicitly authorized source-bearing revision.
- Preserve all active workers and make no dispatcher, TAFE, runtime, eligibility, lease, credential, or Git-state mutation.

## Cross-Harness Disposition

- **A**: No production behavior change; existing Codex telemetry remains covered by the generic suite.
- **B**: No production behavior change; existing Claude telemetry remains covered by the generic suite.
- **C**: No production behavior change; existing Antigravity telemetry remains covered by the generic suite.
- **D**: No production behavior change; existing Ollama telemetry remains covered by the generic suite.
- **E**: Directly covered by new success and failure production-path provenance tests.
- **F**: No production behavior change; existing OpenRouter telemetry remains covered by the generic suite.
- **H**: No production behavior change; existing Alibaba telemetry remains covered by the generic suite.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `SPEC-SHIM-HARNESS-DISPATCH-TELEMETRY-001` | Run the new Cursor E production-path integration test plus the existing shim telemetry suite. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Prove the dispatcher completion reconciliation path persists success and failure provenance without a Cursor-specific production branch. |
| `GOV-SESSION-ROLE-AUTHORITY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-DISPATCH-ENVELOPE-RULES-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | Verify Cursor E uses the same governed telemetry contract as the active fleet. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Run existing A/B/C/D/F/H-neutral telemetry regressions and confirm production source bytes remain unchanged. |

## Acceptance Criteria

- The new test exercises the real production reconciliation entry point for Cursor E success and failure cases.
- The focused test, the existing 23-test shim telemetry suite, and the focused runtime reconciliation tests pass.
- Ruff check and format check pass for the new test file.
- No production source, dispatcher, TAFE, runtime, harness, eligibility, worker, lease, credential, Git staging, push, deployment, or release state changes.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `platform_tests/scripts/test_cursor_dispatch_telemetry_provenance.py`

## Recommended Commit Type

`feat`
