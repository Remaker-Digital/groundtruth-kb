NEW
::init gtkb lo
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: reasoning_effort=xhigh; thread_source=user
author_metadata_source: x-codex-turn-metadata

# Implementation Proposal - Update test_ollama_harness.py stale malformed-arguments test post WI-5471

bridge_kind: prime_proposal
Document: gtkb-wi5550-ollama-malformed-argument-test-contract
Version: 001
Date: 2026-07-18 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project Authorization Candidates: [{"project_authorization_id":"PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING","coverage":"project_membership_fallback","included_work_item_count":null,"specificity_rank":[2,0],"selected":true}]
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5550

target_paths: ["platform_tests/scripts/test_ollama_harness.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Replace one stale affected-module Ollama assertion with a deterministic two-turn regression for WI-5471 recoverable malformed-tool-argument behavior. This is a test-only correction under the standing reliability fast-lane; no provider source or dispatcher/TAFE state changes.

Work item description: platform_tests/scripts/test_ollama_harness.py::test_tool_loop_rejects_malformed_tool_arguments asserts the pre-WI-5471 behavior (a single malformed tool call immediately raises OllamaHarnessError). WI-5471 made this recoverable; the test now fails (gets max-turn exhaustion instead of the immediate raise it expects) because it is outside WI-5471's declared target_paths and the implementation-start gate correctly blocked editing it as an out-of-scope mutation. platform_tests/scripts/test_shim_toolcall_arg_resilience.py already covers the corrected single-call-recovers behavior for both shims; a follow-up REVISED proposal should replace this one stale assertion in test_ollama_harness.py with either a repeated-signature-backstop test (matching the equivalent test drafted but not landed in this session) or simply delete it as redundant with the new shared test file.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5550` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `platform_tests/scripts/test_ollama_harness.py`.

## Specification Links

- `GOV-RELIABILITY-FAST-LANE-001` - auto-linked governing or work-item specification.
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
- `DCL-OLLAMA-TOOL-PARITY-GATE-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-20265519` - Loyal Opposition Verification Verdict - WI-4237 bridge reconciliation operator skill
- `DELIB-202666257` - Loyal Opposition Proposal Review - WI-5253 Ollama D Publisher Failure Recovery
- `DELIB-202666408` - Loyal Opposition NO-GO — WI-5222 60-Minute Generous Dispatch Envelope Implementation Report
- `DELIB-202666194` - Loyal Opposition NO-GO — WI-5222 60-Minute Generous Dispatch Envelope Implementation Report
- `DELIB-202666241` - Loyal Opposition Review - Dispatcher runtime current-HEAD verification fixtures block WI-5222 and WI-5233

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` - active project authorization covering `WI-5550`.

## Proposed Scope

- Replace only test_tool_loop_rejects_malformed_tool_arguments with a deterministic two-turn regression: the first Ollama response emits malformed JSON arguments with a stable tool-call id; the second inspects the correlated ERROR tool result and returns recovered final text.
- Preserve the existing WI-5471 provider implementation and the separate repeated-signature and max-turn backstops; do not alter scripts/ollama_harness.py or any provider source.
- Do not mutate dispatcher configuration, TAFE/runtime state, leases, roles, eligibility, routing, caps, allowances, live workers, unrelated dirty bytes, Git staging, push, deployment, or release.

## Cross-Harness Disposition

- **A**: Prime Builder only; proposal authoring and later test-only implementation after all gates, with no LO verdict authority.
- **D**: Directly affected LO provider contract; test behavior only, no Ollama source, model, route, cap, allowance, or eligibility change.
- **F**: No target change; the shared WI-5471 resilience suite remains required verification evidence.
- **B/C/E/H**: No source, test, role, routing, eligibility, provider, or runtime change.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5550; PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING; generated by gt bridge file-implementation-proposal",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and the governed bridge proposal generators",
  "primary_route": "gt bridge file-implementation-proposal",
  "before_behavior": "platform_tests/scripts/test_ollama_harness.py::test_tool_loop_rejects_malformed_tool_arguments asserts the pre-WI-5471 behavior (a single malformed tool call immediately raises OllamaHarnessError). WI-5471 made this recoverable; the test now fails (gets max-turn exhaustion instead of the immediate raise it expects) because it is outside WI-5471's declared target_paths and the implementation-start gate correctly blocked editing it as an out-of-scope mutation. platform_tests/scripts/test_shim_toolcall_arg_resilience.py already covers the corrected single-call-recovers behavior for both shims; a follow-up REVISED proposal should replace this one stale assertion in test_ollama_harness.py with either a repeated-signature-backstop test (matching the equivalent test drafted but not landed in this session) or simply delete it as redundant with the new shared test file.",
  "after_behavior": "Replace one stale affected-module Ollama assertion with a deterministic two-turn regression for WI-5471 recoverable malformed-tool-argument behavior. This is a test-only correction under the standing reliability fast-lane; no provider source or dispatcher/TAFE state changes.",
  "self_descriptive_naming": "The generated title, work-item id, target paths, scope, and acceptance criteria name the proposed effect.",
  "obsolete_guidance_disposition": "No guidance is retired by proposal filing; implementation must explicitly disposition obsolete guidance.",
  "history_preservation": "The numbered bridge chain remains append-only; rollback never deletes proposal or verdict artifacts.",
  "baseline": {
    "work_item": "WI-5550",
    "project": "PROJECT-GTKB-RELIABILITY-FIXES",
    "target_paths": [
      "platform_tests/scripts/test_ollama_harness.py"
    ],
    "linked_specifications": [
      "GOV-RELIABILITY-FAST-LANE-001",
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
      "DCL-OLLAMA-TOOL-PARITY-GATE-001"
    ]
  },
  "expected_result": {
    "summary": "Replace one stale affected-module Ollama assertion with a deterministic two-turn regression for WI-5471 recoverable malformed-tool-argument behavior. This is a test-only correction under the standing reliability fast-lane; no provider source or dispatcher/TAFE state changes.",
    "scope": [
      "Replace only test_tool_loop_rejects_malformed_tool_arguments with a deterministic two-turn regression: the first Ollama response emits malformed JSON arguments with a stable tool-call id; the second inspects the correlated ERROR tool result and returns recovered final text.",
      "Preserve the existing WI-5471 provider implementation and the separate repeated-signature and max-turn backstops; do not alter scripts/ollama_harness.py or any provider source.",
      "Do not mutate dispatcher configuration, TAFE/runtime state, leases, roles, eligibility, routing, caps, allowances, live workers, unrelated dirty bytes, Git staging, push, deployment, or release."
    ],
    "acceptance_criteria": [
      "The focused affected-module regression proves malformed JSON is returned as a correlated ERROR tool result and a corrected next turn completes without immediate worker abort.",
      "The complete platform_tests/scripts/test_ollama_harness.py module passes.",
      "The dedicated platform_tests/scripts/test_shim_toolcall_arg_resilience.py module remains green and Ruff check plus format check pass for the one target file."
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
| `GOV-RELIABILITY-FAST-LANE-001` | Run the focused regression and complete affected Ollama harness module; expect all tests to pass with a one-file test-only diff. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Require independent GO, an exact matching claim, schema-v3 implementation-start authorization, operation-time validation, and independent post-implementation verification. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Candidate and live applicability preflights must report no missing required specifications. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Execute the focused test, complete affected module, dedicated WI-5471 resilience module, Ruff check, and Ruff format check before VERIFIED. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Read back active PAUTH, project membership, WI-5550, TEST-11630, and the exact single target path. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-OLLAMA-TOOL-PARITY-GATE-001` | Confirm only the test contract changes and existing Ollama guard-adapter and bounded retry behavior remain untouched. |

## Acceptance Criteria

- The focused affected-module regression proves malformed JSON is returned as a correlated ERROR tool result and a corrected next turn completes without immediate worker abort.
- The complete platform_tests/scripts/test_ollama_harness.py module passes.
- The dedicated platform_tests/scripts/test_shim_toolcall_arg_resilience.py module remains green and Ruff check plus format check pass for the one target file.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `platform_tests/scripts/test_ollama_harness.py`

## Recommended Commit Type

`feat`
