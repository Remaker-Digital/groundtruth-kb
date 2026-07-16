NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6bf6-3e6d-7761-be14-fb894a0e84d2
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: OpenAI Codex desktop interactive; reasoning=xhigh; approval_policy=never

# Implementation Proposal - Recover repeated Cursor E headless review timeouts waiting for Cursor Agent

bridge_kind: prime_proposal
Document: gtkb-wi5345-cursor-timeout-recovery
Version: 001
Date: 2026-07-16 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5345-CURSOR-TIMEOUT-RECOVERY-20260716
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5345

target_paths: ["scripts/cursor_harness.py", "platform_tests/scripts/test_cursor_harness.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Recover repeated genuine Cursor E headless review timeouts by preserving actionable TimeoutExpired evidence and returning exit 124 into the dispatcher's existing governed timeout-recovery path, without disabling E or changing routing/TAFE state.

Work item description: Two genuine Cursor E Loyal Opposition dispatches failed on distinct substantive governed reviews with exit 1 and the sole 52-byte diagnostic 'cursor_harness: timed out waiting for Cursor Agent': 2026-07-16T17-30-44Z-loyal-opposition-E-dd4c0c ran 679 seconds over WI-5328/WI-5307, and 2026-07-16T18-27-58Z-loyal-opposition-E-6bf2f1 ran 628 seconds over WI-5337. Diagnose the Cursor harness wait boundary and make a timed-out agent attempt preserve actionable provider/process diagnostics, release and reoffer documents exactly once, and recover without disabling E or impairing other lanes. Preserve full configured model/session allowances and do not infer failure from ordinary worker silence before the adapter's own terminal timeout evidence.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5345` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/cursor_harness.py`, `platform_tests/scripts/test_cursor_harness.py`.

## Specification Links

- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - auto-linked governing or work-item specification.
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
- `ADR-DISPATCHER-ARCHITECTURE-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-20266410` - Separation Check
- `DELIB-20266436` - Separation Check
- `DELIB-DISPATCHER-CLAUDE-CURSOR-HARDEN-FIRST-20260626` - Dispatcher daemon Claude+Cursor headless collaboration: harden-first, go-live-later
- `DELIB-20266446` - Separation Check
- `DELIB-20266447` - Separation Check

## Owner Decisions / Input

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` - owner-decision evidence supplied to this command.
- `PAUTH-DISPATCHER-BLACK-BOX-WI5345-CURSOR-TIMEOUT-RECOVERY-20260716` - active project authorization covering `WI-5345`.

## Proposed Scope

- Catch subprocess.TimeoutExpired only after the configured Cursor adapter timeout and preserve bounded partial stdout/stderr without exposing the full prompt or command arguments.
- Return conventional exit 124 with a stable actionable diagnostic containing timeout seconds, skill route, output format, mode, and safe executable basename so existing dispatcher worker_timeout classification is used.
- Preserve Cursor process provenance recording, hidden-process launch, existing timeout values, full model/session allowances, eligibility, routing, live workers, dispatcher/TAFE state, and all unrelated files.
- Use existing dispatcher timeout, exact-once lease-release, telemetry reconciliation, and reoffer/backoff behavior as read-only integration evidence; do not modify dispatcher runtime.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | Run focused Cursor adapter tests covering TimeoutExpired, partial output, redaction boundary, exit 124, provenance, and ordinary delayed success. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Require fresh GO, exact claim, implementation-start, report, independent verdict, and focused finalization before closure. |
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
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Run existing dispatcher-runtime timeout, exact-once lease release, and reoffer/backoff tests without changing dispatcher source. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Review the exact two-file diff and dispatcher report to prove the repair stays in the harness shim and uses existing centralized reconciliation. |

## Acceptance Criteria

- An explicit Cursor subprocess timeout returns 124, not generic exit 1, and emits bounded partial output plus a stable timeout diagnostic without prompt text or credentials.
- String and byte partial stdout/stderr are handled deterministically and truncation is explicit; absent partial output remains valid.
- Ordinary delayed success within the configured allowance remains success and is never inferred as failure from silence.
- Existing dispatcher tests prove exit 124 becomes worker_timeout, releases each document lease exactly once, reconciles telemetry, and reoffers under governed backoff.
- Cursor E remains active and dispatchable; no eligibility, routing, cap, TAFE/runtime, or live-worker mutation occurs.
- Focused pytest, ruff, applicability, clause preflight, independent LO verification, and focused commit gates pass.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/cursor_harness.py`
- `platform_tests/scripts/test_cursor_harness.py`

## Recommended Commit Type

`feat`
