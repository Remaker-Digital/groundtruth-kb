NEW
::init gtkb lo
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: d067ca16-171b-4b2e-89f5-642340e605a6
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: claude-code-interactive-prime-builder-via-init-gtkb-pb

# Implementation Proposal - Tool-call argument parse resilience in dispatch worker shims

bridge_kind: prime_proposal
Document: gtkb-wi5471-toolcall-arg-parse-resilience
Version: 001
Date: 2026-07-17 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5471

target_paths: ["scripts/cloud_harness_base.py", "scripts/ollama_harness.py", "platform_tests/scripts/test_shim_toolcall_arg_resilience.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Malformed-JSON tool-call arguments abort a dispatch worker with no retry, wasting the run when a fast model fumbles a tool call. Route the parse failure through the shims existing recoverable tool-error path so the model re-issues the call, retry-bounded by the existing backstop. Fast-lane reliability defect, source plus test only.

Work item description: Both dispatch worker shims (shared cloud base + local) strictly parse tool-call arguments and raise a fatal error on malformed JSON, aborting the whole worker with no retry; a smaller/faster model occasionally emits a malformed-JSON tool call and wastes the entire run. Fix: wrap the tool-call parse in the existing graceful tool-error pattern so a parse failure becomes a recoverable ERROR tool result and the model re-issues the call, retry-bounded by the existing repeated-signature backstop.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5471` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/cloud_harness_base.py`, `scripts/ollama_harness.py`, `platform_tests/scripts/test_shim_toolcall_arg_resilience.py`.

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
- `GOV-RELIABILITY-FAST-LANE-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-20266132` - Owner decision: re-scope and close WI-4670 on landed storm-containment evidence
- `DELIB-202666078` - Loyal Opposition Verdict — WI-5118 startup-input gate fresh-start-only (post-implementation verification)
- `DELIB-20265595` - Verdict
- `DELIB-202666560` - Loyal Opposition Proposal Review - GO - WI-5348 Retired G Phase 1 Operative Population
- `DELIB-20265684` - Loyal Opposition Verdict: VERIFIED finalization tolerates unrelated staged files

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` - active project authorization covering `WI-5471`.

## Proposed Scope

- Wrap the tool-call parse at both worker-loop call sites so a malformed-arguments parse failure becomes a recoverable ERROR tool-result keyed to the call id and the loop continues, instead of raising and aborting the worker.
- Reuse the existing tool-error message pattern and the existing repeated-signature backstop to bound any retry loop, with no behavior change for well-formed tool calls.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | pytest the new test module covering both shims, asserting loop-continue behavior. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-RELIABILITY-FAST-LANE-001` | Unit test feeds a tool_call with non-JSON arguments to each shim parse-guard and asserts a recoverable ERROR tool-result is produced with no worker abort. |

## Acceptance Criteria

- A tool_call whose arguments string is not valid JSON yields a recoverable ERROR tool-result and the worker continues, in both the cloud worker-shim base and the local worker shim.
- Well-formed tool calls are unaffected, and ruff check plus ruff format --check pass on changed files.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/cloud_harness_base.py`
- `scripts/ollama_harness.py`
- `platform_tests/scripts/test_shim_toolcall_arg_resilience.py`

## Recommended Commit Type

`feat`
