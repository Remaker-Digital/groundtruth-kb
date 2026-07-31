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

# Implementation Proposal - Expose a canonical consecutive dispatcher-item success ledger

bridge_kind: prime_proposal
Document: gtkb-wi5549-consecutive-dispatch-item-success-ledger
Version: 001
Date: 2026-07-18 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project Authorization Candidates: [{"project_authorization_id":"PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING","coverage":"project_membership_fallback","included_work_item_count":null,"specificity_rank":[2,0],"selected":true}]
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5549

target_paths: ["groundtruth-kb/src/groundtruth_kb/dispatch_default_metrics.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_report.py", "platform_tests/groundtruth_kb/test_dispatch_default_metrics.py", "platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Derive and expose an exact canonical 60-item consecutive dispatcher-success ledger from the WI-5284 per-item event stream, without reading or mutating dispatcher runtime state.

Work item description: The active fleet acceptance requires 60 dispatcher-produced bridge items in one error-free sequence, distributed across every currently dispatchable harness, but gt bridge dispatch report currently returns recent_work_metrics unavailable with reason canonical_snapshot_unavailable. WI-5284 owns the general live metrics event/snapshot producer; this distinct acceptance slice must derive an item-level governed success ledger from canonical persisted dispatcher completion events and versioned bridge transitions. Each counted item must bind dispatch_id, harness id, assigned role, document slug/version, target-authored governed output path/status, and terminal success without provider, process, timeout, publication, attribution, duplicate, or partial-batch error. Multi-document workers count each successfully advanced assigned item exactly once. Any qualifying error resets the consecutive streak. The compact report must expose current streak, per-harness distribution, sequence bounds, and the first reset reason without treating runtime JSON, logs, chat notes, or scratch artifacts as canonical proof. Preserve fixed topology, TAFE, routing, eligibility, caps, allowances, live workers, privacy/null semantics, and observational behavior.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5549` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/dispatch_default_metrics.py`, `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_report.py`, `platform_tests/groundtruth_kb/test_dispatch_default_metrics.py`, `platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py`.

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
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - auto-linked governing or work-item specification.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - auto-linked governing or work-item specification.
- `DCL-REPORTING-SURFACE-FRESH-READ-001` - auto-linked governing or work-item specification.
- `GOV-RELIABILITY-FAST-LANE-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-202666121` - Verdict
- `DELIB-202665613` - Loyal Opposition Review Verdict - NO-GO
- `DELIB-202665612` - Loyal Opposition Review Verdict - NO-GO
- `DELIB-20260716-WI5169-ALIBABA-H-REARM-BUDGET-LIVE` - Owner decision: Alibaba budget live; re-arm harness H dispatch eligibility now (WI-5169 EXPEDITE)
- `DELIB-20263296` - GO - WI-4534 Role-Eligibility Guard on go_implementation Claims

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` - active project authorization covering `WI-5549`.

## Proposed Scope

- Do not begin implementation until WI-5284 is terminal VERIFIED and committed; consume only its canonical persisted per-item completion and dispatch-error events.
- Count an assigned bridge document exactly once only when its canonical event binds dispatch id, harness id, assigned role, document slug and version, target-authored governed output path and status, author provenance, and error-free terminal completion.
- Order deterministically by canonical event time and stable event id; a provider, process, timeout, publication, attribution, duplicate, malformed-provenance, partial-batch, or dispatch-level error resets the consecutive streak and records the first reset reason.
- Expose current streak length, 60-item threshold disposition, sequence start/end identities and timestamps, per-harness and per-role distribution, and last reset reason through the compact canonical dispatcher report.
- Use a bounded canonical event window large enough to prove at least 60 consecutive items; never read or cite runtime JSON, logs, leases, claims, chat notes, scratchpads, caches, or temporary artifacts as proof.
- Preserve dispatcher and TAFE configuration/runtime, topology, roles, eligibility, caps, routing, allowances, leases, live workers, provider behavior, privacy/null semantics, and the full report contract.

## Cross-Harness Disposition

- **A**: Required Prime Builder participant in the measured sequence; no role or dispatchability change.
- **D**: Required Ollama Loyal Opposition participant in the measured sequence; no provider, role, or dispatchability change.
- **F**: Required OpenRouter Loyal Opposition participant in the measured sequence; no provider, role, or dispatchability change.
- **B**: Non-selected parity consumer only; no runtime or configuration change.
- **C**: Non-selected parity consumer only; no runtime or configuration change.
- **E**: Non-selected parity consumer only; no runtime or configuration change.
- **H**: Non-selected parity consumer only; no runtime or configuration change.
- **G**: No installed harness; retired registry residue only and no implementation target.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5549; PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING; generated by gt bridge file-implementation-proposal",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and the governed bridge proposal generators",
  "primary_route": "gt bridge file-implementation-proposal",
  "before_behavior": "The active fleet acceptance requires 60 dispatcher-produced bridge items in one error-free sequence, distributed across every currently dispatchable harness, but gt bridge dispatch report currently returns recent_work_metrics unavailable with reason canonical_snapshot_unavailable. WI-5284 owns the general live metrics event/snapshot producer; this distinct acceptance slice must derive an item-level governed success ledger from canonical persisted dispatcher completion events and versioned bridge transitions. Each counted item must bind dispatch_id, harness id, assigned role, document slug/version, target-authored governed output path/status, and terminal success without provider, process, timeout, publication, attribution, duplicate, or partial-batch error. Multi-document workers count each successfully advanced assigned item exactly once. Any qualifying error resets the consecutive streak. The compact report must expose current streak, per-harness distribution, sequence bounds, and the first reset reason without treating runtime JSON, logs, chat notes, or scratch artifacts as canonical proof. Preserve fixed topology, TAFE, routing, eligibility, caps, allowances, live workers, privacy/null semantics, and observational behavior.",
  "after_behavior": "Derive and expose an exact canonical 60-item consecutive dispatcher-success ledger from the WI-5284 per-item event stream, without reading or mutating dispatcher runtime state.",
  "self_descriptive_naming": "The generated title, work-item id, target paths, scope, and acceptance criteria name the proposed effect.",
  "obsolete_guidance_disposition": "No guidance is retired by proposal filing; implementation must explicitly disposition obsolete guidance.",
  "history_preservation": "The numbered bridge chain remains append-only; rollback never deletes proposal or verdict artifacts.",
  "baseline": {
    "work_item": "WI-5549",
    "project": "PROJECT-GTKB-RELIABILITY-FIXES",
    "target_paths": [
      "groundtruth-kb/src/groundtruth_kb/dispatch_default_metrics.py",
      "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_report.py",
      "platform_tests/groundtruth_kb/test_dispatch_default_metrics.py",
      "platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py"
    ],
    "linked_specifications": [
      "SPEC-DISPATCH-DEFAULT-METRICS-SNAPSHOT-001",
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
      "SPEC-CENTRALIZED-DISPATCH-SERVICE-001",
      "SPEC-DISPATCHER-CONTROL-SURFACE-001",
      "GOV-DOCUMENT-AUTHOR-PROVENANCE-001",
      "GOV-SOURCE-OF-TRUTH-FRESHNESS-001",
      "DCL-REPORTING-SURFACE-FRESH-READ-001",
      "GOV-RELIABILITY-FAST-LANE-001"
    ]
  },
  "expected_result": {
    "summary": "Derive and expose an exact canonical 60-item consecutive dispatcher-success ledger from the WI-5284 per-item event stream, without reading or mutating dispatcher runtime state.",
    "scope": [
      "Do not begin implementation until WI-5284 is terminal VERIFIED and committed; consume only its canonical persisted per-item completion and dispatch-error events.",
      "Count an assigned bridge document exactly once only when its canonical event binds dispatch id, harness id, assigned role, document slug and version, target-authored governed output path and status, author provenance, and error-free terminal completion.",
      "Order deterministically by canonical event time and stable event id; a provider, process, timeout, publication, attribution, duplicate, malformed-provenance, partial-batch, or dispatch-level error resets the consecutive streak and records the first reset reason.",
      "Expose current streak length, 60-item threshold disposition, sequence start/end identities and timestamps, per-harness and per-role distribution, and last reset reason through the compact canonical dispatcher report.",
      "Use a bounded canonical event window large enough to prove at least 60 consecutive items; never read or cite runtime JSON, logs, leases, claims, chat notes, scratchpads, caches, or temporary artifacts as proof.",
      "Preserve dispatcher and TAFE configuration/runtime, topology, roles, eligibility, caps, routing, allowances, leases, live workers, provider behavior, privacy/null semantics, and the full report contract."
    ],
    "acceptance_criteria": [
      "TEST-11655: exactly 60 qualifying item events distributed across A, D, and F produce streak=60, threshold_met=true, exact sequence bounds, and exact per-harness counts.",
      "A qualifying error after item 30 resets the sequence; 30 later successes produce streak=30 with threshold_met=false and the exact canonical reset reason.",
      "A two-document dispatch counts each assigned document once; idempotent duplicate events cannot inflate the streak or distribution.",
      "Missing, conflicting, unassigned, or non-target-authored provenance never counts as success and produces an explicit bounded reset or invalid disposition.",
      "Compact JSON and human reporting expose the same bounded ledger; full report JSON remains unchanged and unavailable/stale canonical snapshot states remain explicit.",
      "Focused metrics/report tests, Ruff, compile, applicability, clause, independent verification, and focused commit gates pass before closure."
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
| `SPEC-DISPATCH-DEFAULT-METRICS-SNAPSHOT-001` | Run TEST-11655 against canonical event and snapshot fixtures covering 60-success, reset, deduplication, bounded-window, stale, invalid, and unavailable states. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run proposal and implementation-report applicability/clause preflights and preserve role-correct numbered bridge publication. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Carry TEST-11655 and every linked-spec mapping into the implementation report with exact observed commands and results. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Prove each dispatcher-assigned document is counted once with dispatch, harness, role, version, output, provenance, and completion bindings and that all defined failures reset the streak. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | Run compact JSON and human report parity tests while proving full report JSON and dispatcher control behavior remain unchanged. |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | Reject missing, conflicting, unassigned, or non-target-authored completion provenance in deterministic fixtures. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Require current canonical event/snapshot evidence and explicit stale, invalid, empty, and unavailable dispositions. |
| `DCL-REPORTING-SURFACE-FRESH-READ-001` | Prove the report reads only current canonical persisted metrics and has no runtime, log, lease, claim, cache, or scratch fallback. |
| `GOV-RELIABILITY-FAST-LANE-001` | Keep the implementation additive, observational, target-bounded, independently reviewed, and free of dispatcher behavior or configuration mutation. |

## Acceptance Criteria

- TEST-11655: exactly 60 qualifying item events distributed across A, D, and F produce streak=60, threshold_met=true, exact sequence bounds, and exact per-harness counts.
- A qualifying error after item 30 resets the sequence; 30 later successes produce streak=30 with threshold_met=false and the exact canonical reset reason.
- A two-document dispatch counts each assigned document once; idempotent duplicate events cannot inflate the streak or distribution.
- Missing, conflicting, unassigned, or non-target-authored provenance never counts as success and produces an explicit bounded reset or invalid disposition.
- Compact JSON and human reporting expose the same bounded ledger; full report JSON remains unchanged and unavailable/stale canonical snapshot states remain explicit.
- Focused metrics/report tests, Ruff, compile, applicability, clause, independent verification, and focused commit gates pass before closure.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/dispatch_default_metrics.py`
- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_report.py`
- `platform_tests/groundtruth_kb/test_dispatch_default_metrics.py`
- `platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py`

## Recommended Commit Type

`feat`
