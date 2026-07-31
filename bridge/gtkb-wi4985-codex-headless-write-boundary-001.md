NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f247b-4dc8-7b32-a2ab-25839614d33f
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive Prime Builder session; runtime reasoning profile not exposed

# Implementation Proposal - Fix Codex headless dispatch write boundary for Prime Builder source edits

bridge_kind: prime_proposal
Document: gtkb-wi4985-codex-headless-write-boundary
Version: 001
Date: 2026-07-03 UTC

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4985-CODEX-HEADLESS-WRITE-BOUNDARY
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-4985

target_paths: ["harness-state/harness-registry.json", "groundtruth.db", "platform_tests/groundtruth_kb/cli/test_harness_cli.py", "platform_tests/scripts/test_dispatcher_runtime.py", "scripts/verify_codex_dispatch.py", "platform_tests/scripts/test_verify_codex_dispatch.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Fix Codex A headless Prime Builder dispatch so approved in-root source/test edits run under the intended GPT-5.5 Extra High, noninteractive, write-capable surface instead of failing apply_patch before mutation.

Work item description: Live 2026-07-03 bridge soak proved Ollama D can file LO verdicts, but Codex A headless PB repeatedly fails authorized source edits with 'patch rejected: writing outside of the project; rejected by user approval settings'. Remediate the Codex headless invocation/config so Prime Builder dispatch can write approved in-root target paths without interactive intervention, while retaining approval_policy=never, GPT-5.5, Extra High reasoning, and bridge authorization gates.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-4985` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `harness-state/harness-registry.json`, `groundtruth.db`, `platform_tests/groundtruth_kb/cli/test_harness_cli.py`, `platform_tests/scripts/test_dispatcher_runtime.py`, `scripts/verify_codex_dispatch.py`, `platform_tests/scripts/test_verify_codex_dispatch.py`.

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
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs bounded project implementation authority.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - requires bounded PAUTH envelopes for new authorization state.

## Prior Deliberations

- _No prior deliberations auto-loaded; author must confirm before review._

## Owner Decisions / Input

- `DELIB-202665265` - owner-decision evidence supplied to this command.
- `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4985-CODEX-HEADLESS-WRITE-BOUNDARY` - active project authorization covering `WI-4985`.

## Proposed Scope

- Update Codex A headless invocation surface so dispatched Prime Builder workers keep GPT-5.5, approval_policy=never, and model_reasoning_effort=xhigh while also selecting a project-root write-capable Codex sandbox/root mode.
- Refresh harness-registry projection and MemBase-backed invocation-surface state through governed harness CLI plumbing rather than manual dispatcher-rule edits.
- Add static readiness/test coverage proving the Codex headless argv contains the model pin, Extra High reasoning pin, noninteractive approval policy, project-root selector, and write-capable sandbox before dispatch.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run implementation-start/work-intent gated path only after GO; verify proposal/report/status chain and no protected source/config edit before GO. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run focused pytest coverage plus live dispatcher smoke/soak evidence before filing implementation report. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Confirm WI-4985 is covered by PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4985-CODEX-HEADLESS-WRITE-BOUNDARY before mutation. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | Verify changed paths stay within bridge, harness-registry, source, and tests mutation classes allowed by the PAUTH. |

## Acceptance Criteria

- gt harness show --harness A reports a headless argv that includes --model gpt-5.5, approval_policy=never, model_reasoning_effort=xhigh, a project-root selector, and a write-capable sandbox argument suitable for noninteractive in-root edits.
- Focused harness CLI, dispatcher runtime, and Codex readiness tests pass and fail closed if the Codex headless surface regresses to the prior no-sandbox form.
- A bounded live dispatcher retry after GO can launch Codex A without the previous apply_patch outside-project rejection; if a downstream implementation still fails, the failure is no longer the Codex write-boundary blocker.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `harness-state/harness-registry.json`
- `groundtruth.db`
- `platform_tests/groundtruth_kb/cli/test_harness_cli.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`
- `scripts/verify_codex_dispatch.py`
- `platform_tests/scripts/test_verify_codex_dispatch.py`

## Recommended Commit Type

`feat`
