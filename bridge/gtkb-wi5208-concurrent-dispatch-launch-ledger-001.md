NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f522a-849d-7d43-8c60-0afc829438a6
author_model: gpt-5.5
author_model_version: Codex desktop
author_model_configuration: xhigh reasoning; interactive Prime Builder

# Implementation Proposal - Reconcile every concurrent dispatcher launch and release its leases

bridge_kind: prime_proposal
Document: gtkb-wi5208-concurrent-dispatch-launch-ledger
Version: 001
Date: 2026-07-12 UTC

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5208-CONCURRENT-LAUNCH-LEDGER-20260711
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5208

target_paths: ["scripts/dispatcher_runtime.py", "scripts/gtkb_dispatcher_daemon.py", "platform_tests/scripts/test_dispatcher_runtime.py", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Correct the dispatcher launch-state model that loses completed worker evidence and leaves long-lived document leases whenever multiple workers for one recipient overlap.

Work item description: The dispatcher permits multiple concurrent workers for one recipient but persists only recipient_state.last_launch. A later launch or document_lease_held non-launch can overwrite an earlier still-running dispatch before its exit sidecar is processed. Six completed B review leases (WI-5200, WI-5203, WI-5204, WI-5205, WI-5206, WI-5207) remained for the full 29,700-second TTL and blocked new governed reports until a canonical soft reset removed them; four fresh locks reproduced after reset. Add a per-recipient launch ledger keyed by dispatch_id, reconcile every exit independently including out-of-order completion, release each launch's document leases exactly once, preserve compatibility last-launch reporting without losing active evidence, and prevent non-launch attempts from suppressing actionable work.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5208` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/dispatcher_runtime.py`, `scripts/gtkb_dispatcher_daemon.py`, `platform_tests/scripts/test_dispatcher_runtime.py`, `platform_tests/scripts/test_gtkb_dispatcher_daemon.py`.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - auto-linked governing or work-item specification.
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

## Prior Deliberations

- `DELIB-20265026` - Loyal Opposition Review - WI-4556 Ollama Provider Failure Fallback And Backoff
- `DELIB-20260711-WI5200-5202-HARNESS-REPAIR-AUTHORIZATION` - Authorize harness recovery, parity truth, generous envelopes, and H reproof
- `DELIB-202665739` - WI-4995 Document Lease Held Health — Post-Implementation Verification Verdict
- `DELIB-20265417` - Loyal Opposition Verdict - GO
- `DELIB-20263376` - GO: WI-4396 dispatch suppression routing

## Owner Decisions / Input

- `DELIB-202666173` - owner-decision evidence supplied to this command.
- `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5208-CONCURRENT-LAUNCH-LEDGER-20260711` - active project authorization covering `WI-5208`.

## Proposed Scope

- Replace the single recipient last_launch completion authority with a bounded active-launch ledger keyed by dispatch_id while retaining last_launch as a compatibility/reporting projection.
- Register every successful runtime and daemon launch before any later launch or non-launch attempt can overwrite its reconciliation evidence.
- Process all pending exit sidecars independently and safely out of order; release each launch's document leases exactly once and preserve compact completion provenance.
- Keep document_lease_held and other non-launch attempts observable without allowing them to erase active launch evidence or suppress actionable bridge work.
- Migrate legacy last_launch-only state fail-safe, bound completed-history retention, and leave routing, model budgets, operation/session timers, and worker lifetimes unchanged.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Run focused runtime and daemon integration fixtures for three concurrent launches, out-of-order exits, overwritten non-launch attempts, and exact-once lease release. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Use genuine version-advancing bridge fixtures and assert each selected document remains actionable until its own role-correct verdict. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run independent pytest plus separate Ruff check and Ruff format-check on all four changed Python paths. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |

## Acceptance Criteria

- Three concurrent launches for one recipient remain independently keyed and reconcile correctly when exit sidecars arrive out of order.
- A new bridge version and a document_lease_held attempt while an earlier worker is still running cannot overwrite that worker's launch record.
- Every acquired document lease is released exactly once on success, reconciled nonzero exit, timeout, and failure; no lock survives until its 29,700-second TTL after completion.
- Compatibility last_launch/reporting fields remain truthful, active and completed ledgers are bounded, and legacy state upgrades without dropping an in-flight launch.
- Per-document completion/signature behavior remains compatible with WI-5207 and never suppresses a still-actionable selected document.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/dispatcher_runtime.py`
- `scripts/gtkb_dispatcher_daemon.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`
- `platform_tests/scripts/test_gtkb_dispatcher_daemon.py`

## Recommended Commit Type

`feat`
