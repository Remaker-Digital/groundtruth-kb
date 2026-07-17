NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop Prime Builder; transcript-defined PB role; no direct harness contact

# Implementation Proposal - Cloud-harness publisher treats peer-held verdict claim as fatal: 36-min H run burned then exit 1 no_progress_loop instead of neutral stand-down

bridge_kind: prime_proposal
Document: gtkb-wi5400-cloud-verdict-claim-lifecycle
Version: 001
Date: 2026-07-17 UTC

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5400

target_paths: ["scripts/dispatcher_runtime.py", "platform_tests/scripts/test_dispatcher_runtime.py", "scripts/cloud_harness_base.py", "platform_tests/scripts/test_cloud_harness_base.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Repair the cloud LO verdict-claim lifecycle so the dispatcher owns a worker-lifetime-aligned claim before provider spend, publication renews or reacquires the worker claim, and peer-held races stand down neutrally without retry or breaker churn.

Work item description: Run 2026-07-16T23-58-59Z-loyal-opposition-H-db9529 performed ~36 minutes (2185s) of substantive review on gtkb-wi5332-wi5113-invalid-terminal-verdict-reissue, produced a verdict, then bridge verdict publisher recovery exhausted after 4 attempts with: PublishBridgeVerdict did not return a verdict_path: governed bridge verdict publication failed: provider verdict claim for the thread is held by another session. Exit 1, stop_reason no_progress_loop (evidence .gtkb-state/bridge-poller/dispatch-runs/2026-07-16T23-58-59Z-loyal-opposition-H-db9529.stderr.log). Root: under multi-LO fleet saturation, a peer session holds the thread verdict claim; the shared cloud-harness publisher-recovery path retries then classifies as subprocess_execution_failed, feeding the failure counter/breaker and wasting the full provider spend, instead of recognizing claim-contention as the WI-5203-style neutral stand-down (peer is completing the same thread; correct outcome is a cheap non-failure exit citing the peer claim). Distinct from resolved WI-5253 (D publisher receiving non-publisher calls) and from WI-5391 (SessionStart hook timeouts). Suggested repair in scripts/cloud_harness_base.py publisher recovery: on claim-held-by-another-session, verify peer verdict/thread state and exit neutral (stand-down evidence), no failure classification, no breaker feed.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5400` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/dispatcher_runtime.py`, `platform_tests/scripts/test_dispatcher_runtime.py`, `scripts/cloud_harness_base.py`, `platform_tests/scripts/test_cloud_harness_base.py`.

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
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - auto-linked governing or work-item specification.
- `ADR-DISPATCHER-ARCHITECTURE-001` - auto-linked governing or work-item specification.
- `GOV-HARNESS-ISOLATION-001` - auto-linked governing or work-item specification.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-202666173` - Loyal Opposition Verdict: NO-GO (finalization-scoped) — WI-5210 Provider LO Governed Verdict Publication
- `DELIB-202666250` - Loyal Opposition Verification Verdict - WI-5245 Alibaba H Publisher Recovery
- `DELIB-202666178` - WI-5213 - Loyal Opposition Post-Implementation Verification: VERIFIED
- `DELIB-20265758` - Verdict
- `DELIB-20265754` - Loyal Opposition Verification Verdict - WI-4723 VERIFIED finalization index-lock retry

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE` - active project authorization covering `WI-5400`.

## Proposed Scope

- Acquire LO document work-intent claims after trusted worker-session creation and before provider launch, using that worker session id and a TTL no shorter than the configured worker lifetime and document lease.
- When another active session owns the claim before launch, suppress provider launch as a neutral held-work outcome without queue mutation, failure-count increment, circuit-breaker feed, direct harness contact, or dispatcher/TAFE reconfiguration.
- Stamp LO claim provenance and release only the worker own claims on launch failure or observed incomplete exit, while preserving the governed verdict writer release on successful publication.
- Before governed cloud-verdict publication, renew or reacquire an absent or expired same-session draft claim; treat a verified peer-held publication race as a bounded neutral stand-down with structured evidence and no four-attempt publisher model loop.
- Preserve fail-closed behavior for malformed verdicts, authorization and guard failures, and non-contention publication errors; preserve the full configured model, session, worker-lifetime, and lease allowances.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Writer and claim tests prove same-session claim enforcement, successful release, and neutral peer-held disposition. |
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
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Dispatcher regressions prove pre-spawn LO claim ownership, peer-held launch suppression, worker-session provenance, and owned-claim cleanup without queue or routing mutation. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Tests prove the daemon remains the control-plane owner and cloud harnesses use only the governed writer/claim services. |
| `GOV-HARNESS-ISOLATION-001` | Review confirms no direct harness contact, runtime reconfiguration, or cross-harness awareness is introduced. |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | Cloud-harness regressions prove publication recovery stays bounded and fail closed outside the explicit contention stand-down. |

## Acceptance Criteria

- A cloud LO worker with a missing or expired own claim renews or reacquires it and publishes through the governed bridge writer.
- A peer-held claim detected before launch causes no provider spawn or usage and no failure-count or circuit-breaker change.
- A peer-held race detected during publication produces structured neutral stand-down evidence without four publisher retries and without a subprocess_execution_failed classification.
- Launch failure and incomplete worker exit release only claims owned by that worker session; successful publication retains the writer release contract.
- Focused cloud-harness and dispatcher-runtime regressions pass while existing malformed-publication failures and full runtime allowances remain unchanged.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/dispatcher_runtime.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`
- `scripts/cloud_harness_base.py`
- `platform_tests/scripts/test_cloud_harness_base.py`

## Recommended Commit Type

`feat`
