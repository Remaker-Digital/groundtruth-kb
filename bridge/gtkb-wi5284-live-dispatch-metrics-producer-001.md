NEW
::init gtkb lo
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: gpt-5.5
author_model_version: 5.5
author_model_configuration: Codex desktop interactive; resolved Prime Builder via ::init gtkb pb

# Implementation Proposal - Populate canonical dispatch metrics snapshots from live dispatcher telemetry

bridge_kind: prime_proposal
Document: gtkb-wi5284-live-dispatch-metrics-producer
Version: 001
Date: 2026-07-18 UTC

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-COMPLEX-CLI-WI-5284-IMPLEMENTATION-PROPOSAL-FILING
Project: PROJECT-GTKB-DISPATCHER-COMPLEX-CLI
Work Item: WI-5284

target_paths: ["groundtruth-kb/src/groundtruth_kb/dispatch_default_metrics.py", "scripts/dispatcher_runtime.py", "platform_tests/groundtruth_kb/test_dispatch_default_metrics.py", "platform_tests/scripts/test_dispatcher_runtime.py", "platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Populate canonical dispatch metrics from live completion reconciliation, producing one privacy-bounded idempotent event per assigned bridge item and explicit failure evidence for WI-5549's later acceptance ledger.

Work item description: The VERIFIED WI-5180 substrate can persist allowlisted metric events and bounded snapshots, and WI-5181 renders the latest active snapshot, but no production caller invokes persist_metric_event or persist_metrics_snapshot. The live compact dispatcher report therefore returns recent-work metrics unavailable: canonical_snapshot_unavailable even though WI-5175 acceptance requires the always-on metrics set to populate the unified report. Add a deterministic low-overhead producer/cadence that derives only approved telemetry, persists bounded canonical events/snapshots, preserves null/privacy semantics, remains observational, and reports explicit stale/unavailable state when generation cannot run.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5284` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/dispatch_default_metrics.py`, `scripts/dispatcher_runtime.py`, `platform_tests/groundtruth_kb/test_dispatch_default_metrics.py`, `platform_tests/scripts/test_dispatcher_runtime.py`, `platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py`.

## Specification Links

- `SPEC-DISPATCH-DEFAULT-METRICS-SNAPSHOT-001` - auto-linked governing or work-item specification.
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
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - auto-linked governing or work-item specification.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - auto-linked governing or work-item specification.
- `DCL-REPORTING-SURFACE-FRESH-READ-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-202666127` - Loyal Opposition Verdict — WI-5180 default dispatch metrics snapshot (proposal review)
- `DELIB-202666126` - Loyal Opposition Verdict — WI-5180 default dispatch metrics events and bounded snapshots (post-implementation verification)
- `DELIB-20266107` - Owner decision: reconcile dispatch can_receive_dispatch drift to Honest-ON (WI-4821)
- `DELIB-202666129` - gtkb-wi5181-report-metrics-enrichment — Loyal Opposition Verdict (GO)
- `DELIB-20263358` - TAFE Agent Capability Snapshots Schema - VERIFIED

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-DISPATCHER-COMPLEX-CLI-WI-5284-IMPLEMENTATION-PROPOSAL-FILING` - active project authorization covering `WI-5284`.

## Proposed Scope

- After WI-5389 and every other exact scripts/dispatcher_runtime.py owner are terminal, add a low-overhead production completion producer at the existing worker-reconciliation boundary; do not modify the daemon, dispatcher configuration, TAFE, harness registry, roles, eligibility, caps, routing, allowances, leases, or launch behavior.
- Promote only allowlisted deterministic completion facts into canonical dispatch metric events and bounded snapshots. Emit one idempotent event per assigned bridge item, bound to dispatch id, harness id, assigned role, document slug and before/after version, governed output path and status, author provenance, outcome, timing, and failure class; emit explicit dispatch-level error evidence when completion cannot be attributed to one item.
- Preserve prompt, message, provider body, generated prose, tool arguments, credentials, environment values, and all other content-bearing data as absent. Never treat ephemeral execution byproducts, chat notes, or scratch material as canonical proof.
- Persist snapshots on the governed reconciliation cadence with bounded retry/idempotency semantics and explicit stale or unavailable disposition. The producer is observational and must not change selection, retries, recovery, publication, or bridge lifecycle state.
- Keep WI-5549 as a separate dependent slice: WI-5284 supplies the canonical per-item event stream; WI-5549 later derives the consecutive success/reset ledger and report projection without changing this producer's operational behavior.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `SPEC-DISPATCH-DEFAULT-METRICS-SNAPSHOT-001` | Run TEST-11439 through focused metrics and dispatcher-runtime fixtures proving one event per assigned item, deterministic bounded snapshots, idempotency, privacy exclusions, and unavailable/stale behavior. |
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
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Run focused dispatcher reconciliation tests proving metrics persistence is observational and does not alter selection, launch, recovery, lease, or completion behavior. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | Run compact report CLI tests proving fresh, partial, stale, invalid, and unavailable canonical snapshots are rendered without configuration or live-state mutation. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Exercise fresh, partial, stale, invalid, and unavailable snapshot fixtures and require explicit disposition for each. |
| `DCL-REPORTING-SURFACE-FRESH-READ-001` | Run report tests against current canonical snapshots and prove no cached or ephemeral fallback is accepted. |

## Acceptance Criteria

- TEST-11439 passes: a successful single-document dispatch persists exactly one allowlisted canonical event and a fresh or partial bounded snapshot consumed by the compact dispatcher report.
- A successful two-document dispatch persists exactly two distinct item events sharing one dispatch id; retries are idempotent and cannot duplicate either item.
- Provider, process, timeout, publication, attribution, duplicate, and partial-batch failures persist explicit failure classification without fabricating successful item completion.
- No content-bearing provider, prompt, message, tool-argument, credential, environment, routing, or tuning data enters the canonical event or snapshot.
- Producer failure leaves dispatch behavior unchanged and exposes explicit unavailable or stale metrics; it cannot fail, delay, retry, recover, complete, or reconfigure bridge work.
- Focused tests, Ruff check, Ruff format check, compile checks, applicability preflight, clause preflight, independent post-implementation verification, and focused commit all pass before closure.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/dispatch_default_metrics.py`
- `scripts/dispatcher_runtime.py`
- `platform_tests/groundtruth_kb/test_dispatch_default_metrics.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`
- `platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py`

## Recommended Commit Type

`feat`
