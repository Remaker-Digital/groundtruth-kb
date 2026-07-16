NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role; owner goal continuation

# WI-5184 Terminal Non-Implementation GO Non-Claimable End To End

Document: gtkb-wi5184-terminal-nonimplementation-go-nonclaimable
Version: 001
bridge_kind: prime_proposal

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS
Work Item: WI-5184
target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge/disposition.py", "groundtruth-kb/src/groundtruth_kb/bridge/notify.py", "scripts/bridge_work_intent_registry.py", "scripts/bridge_claim_cli.py", "scripts/implementation_authorization.py", "scripts/implementation_start_gate.py", "scripts/protocol_enforcement_health.py", "scripts/dispatcher_runtime.py", "platform_tests/scripts/test_scan_bridge.py", "platform_tests/hooks/test_bridge_axis_2_surface_governance_review_terminal.py", "platform_tests/scripts/test_bridge_work_intent_registry.py", "platform_tests/scripts/test_bridge_claim_cli.py", "platform_tests/scripts/test_implementation_authorization.py", "platform_tests/scripts/test_implementation_start_gate.py", "platform_tests/scripts/test_protocol_enforcement_health.py", "platform_tests/scripts/test_dispatcher_runtime.py"]

## Summary

Prime Builder proposes the governed implementation for `WI-5184`: make terminal non-implementation bridge kinds, including `governance_advisory`, `operational_state_change`, and normalized legacy aliases, consistently non-Prime-actionable after `GO` across the shared disposition model, notification queues, dispatcher reports, manual scans, work-intent registry, claim CLI, implementation-authorization packet creation, and implementation-start gate.

This is a prerequisite for safely unblocking `WI-5249`, which in turn releases the `WI-5178` peer-report hold needed by the black-box bridge/TAFE/harness program.

## Requirement Sufficiency

Existing requirements sufficient.

`WI-5184`, `SPEC-DISPATCH-REPORT-WORKFLOW-COMPACT-001`, `GOV-FILE-BRIDGE-AUTHORITY-001`, `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`, `DCL-NO-ACTION-STATUS-SEMANTICS-001`, and `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` define the required behavior. No new formal requirement is requested by this proposal.

## Problem

Current behavior is split across surfaces. Some user-facing and dispatcher paths already suppress terminal-kind `GO` work, but the shared claim/start substrate can still treat a latest `GO` as ordinary `go_implementation` unless every surface consults the same bridge-kind semantics. That makes a terminal or non-implementation bridge record look implementable to at least one downstream surface, creating either a false Prime task or a governance bypass.

The exact defect class is visible in the Authority Foundations chain: a `governance_advisory` or `operational_state_change` `GO` must not become an ordinary implementation claim merely because the first-line status is `GO`.

## Proposed Implementation

Create or consolidate one canonical bridge-kind actionability helper and apply it consistently.

The implementation should:

1. Normalize canonical and legacy bridge-kind aliases through the existing bridge taxonomy.
2. Classify latest `GO` entries with terminal/non-implementation bridge kinds as non-Prime-actionable.
3. Preserve ordinary implementation `GO` and `NO-GO` behavior for normal Prime work.
4. Preserve `NEW`, `REVISED`, and `NO-ACTION` Loyal Opposition review routing.
5. Make `scripts/bridge_work_intent_registry.py::_go_implementation_claim_applies` return false for terminal-kind and non-implementation `GO` entries.
6. Make `scripts/bridge_claim_cli.py claim` deny terminal-kind `GO` claims without creating a claim row.
7. Make `scripts/implementation_authorization.py begin` and `scripts/implementation_start_gate.py` fail closed if a terminal-kind `GO` has no valid implementation claim/start authority.
8. Update protocol health and dispatcher reporting so terminal-kind `GO` records render as terminal/no-implementation or owner disposition instead of implementation-start work.
9. Keep manual scan and AXIS-2 surfaces aligned with the same semantics.

## Explicit Non-Goals

- Do not change ordinary implementation proposal `GO` or `NO-GO` behavior.
- Do not change Loyal Opposition review routing for `NEW`, `REVISED`, or `NO-ACTION`.
- Do not execute `WI-5178`, `WI-5249`, `WI-5277`, `WI-5279`, `WI-5307`, `WI-5320`, or black-box child implementation.
- Do not mutate PAUTH records or `groundtruth.db` as part of this work.
- Do not perform Git push, release, production deployment, credential lifecycle, destructive cleanup, external-system mutation, or git history rewrite.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5184; DELIB-202666081; Authority Foundations prerequisite chain",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001; PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001; GOV-FILE-BRIDGE-AUTHORITY-001",
  "primary_route": "bridge disposition, notification, work-intent, implementation-authorization, implementation-start, protocol health, and dispatcher reporting",
  "before_behavior": "Terminal or non-implementation bridge-kind GO records can be suppressed in some displays while still appearing claimable or implementation-actionable through lower-level claim/start paths.",
  "after_behavior": "Every shared surface treats terminal/non-implementation GO records as non-implementation state, while ordinary implementation GO records remain claimable and executable after the usual gates.",
  "self_descriptive_naming": "The implementation uses terminal/non-implementation bridge-kind vocabulary in helper names, denial reasons, and test names instead of relying on status-only GO language.",
  "obsolete_guidance_disposition": "Any status-only guidance that implies every GO is implementation-actionable becomes historical context and is superseded by bridge-kind-aware actionability.",
  "history_preservation": "Existing bridge records remain append-only; the change affects future classification, claim denial, and report rendering without rewriting historical bridge files.",
  "baseline": {
    "terminal_kind_examples": ["governance_advisory", "operational_state_change"],
    "risk": "status-only GO actionability can create a false go_implementation claim",
    "known_blocking_chain": "WI-5249 requires WI-5184 terminal ownership before safe revision"
  },
  "expected_result": {
    "terminal_kind_go_prime_actionable": false,
    "terminal_kind_go_claim_row_created": false,
    "ordinary_implementation_go_claimable": true,
    "lo_review_statuses_preserved": true,
    "manual_scan_and_dispatch_reports_aligned": true
  },
  "rollback": {
    "instructions": "Revert only the WI-5184 source and test hunks; do not alter bridge history or PAUTH records.",
    "test": "Re-run focused scan, work-intent, implementation-authorization, start-gate, protocol-health, and dispatcher-runtime tests."
  },
  "hard_invariants": [
    "Ordinary implementation GO remains claimable for Prime Builder after project authorization passes.",
    "Terminal/non-implementation GO creates no go_implementation claim row.",
    "A denied terminal-kind claim creates no implementation-start packet or downstream state.",
    "Loyal Opposition routing for NEW, REVISED, and NO-ACTION remains unchanged.",
    "Bridge history remains append-only."
  ],
  "fail_closed_conditions": [
    "Missing bridge_kind on a proposal whose GO is being considered for non-implementation classification.",
    "Unknown bridge_kind alias that cannot be normalized.",
    "Attempt to create an implementation-start packet from a terminal/non-implementation GO.",
    "Disagreement between scan, notification, claim, and start-gate surfaces."
  ],
  "essential_context_preservation": "The change preserves terminal bridge history, Authority Foundations sequencing, and the distinction between reviewable bridge state and implementable Prime work."
}
```

## Target Paths

```json
[
  "groundtruth-kb/src/groundtruth_kb/bridge/disposition.py",
  "groundtruth-kb/src/groundtruth_kb/bridge/notify.py",
  "scripts/bridge_work_intent_registry.py",
  "scripts/bridge_claim_cli.py",
  "scripts/implementation_authorization.py",
  "scripts/implementation_start_gate.py",
  "scripts/protocol_enforcement_health.py",
  "scripts/dispatcher_runtime.py",
  "platform_tests/scripts/test_scan_bridge.py",
  "platform_tests/hooks/test_bridge_axis_2_surface_governance_review_terminal.py",
  "platform_tests/scripts/test_bridge_work_intent_registry.py",
  "platform_tests/scripts/test_bridge_claim_cli.py",
  "platform_tests/scripts/test_implementation_authorization.py",
  "platform_tests/scripts/test_implementation_start_gate.py",
  "platform_tests/scripts/test_protocol_enforcement_health.py",
  "platform_tests/scripts/test_dispatcher_runtime.py"
]
```

## Specification Links

- `SPEC-DISPATCH-REPORT-WORKFLOW-COMPACT-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-NO-ACTION-STATUS-SEMANTICS-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Spec-Derived Verification Plan

| Specification / requirement | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Tests prove latest bridge state plus bridge kind, not status alone, controls Prime actionability. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Tests prove terminal/non-implementation `GO` cannot create a `go_implementation` claim or implementation-start packet. |
| `DCL-NO-ACTION-STATUS-SEMANTICS-001` | Tests prove `NO-ACTION` remains Loyal-Opposition-actionable and is not reclassified as terminal. |
| `SPEC-DISPATCH-REPORT-WORKFLOW-COMPACT-001` | Dispatcher/report/protocol-health tests prove terminal-kind `GO` records render as non-implementation state rather than acquire/start actions. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | The implementation report must include exact focused command output for the tests below. |

Expected focused commands:

```text
python -m pytest platform_tests/scripts/test_scan_bridge.py platform_tests/hooks/test_bridge_axis_2_surface_governance_review_terminal.py -q --tb=short
python -m pytest platform_tests/scripts/test_bridge_work_intent_registry.py platform_tests/scripts/test_bridge_claim_cli.py -q --tb=short
python -m pytest platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_implementation_start_gate.py -q --tb=short
python -m pytest platform_tests/scripts/test_protocol_enforcement_health.py platform_tests/scripts/test_dispatcher_runtime.py -q --tb=short
python -m ruff check groundtruth-kb/src/groundtruth_kb/bridge/disposition.py groundtruth-kb/src/groundtruth_kb/bridge/notify.py scripts/bridge_work_intent_registry.py scripts/bridge_claim_cli.py scripts/implementation_authorization.py scripts/implementation_start_gate.py scripts/protocol_enforcement_health.py scripts/dispatcher_runtime.py platform_tests/scripts/test_scan_bridge.py platform_tests/hooks/test_bridge_axis_2_surface_governance_review_terminal.py platform_tests/scripts/test_bridge_work_intent_registry.py platform_tests/scripts/test_bridge_claim_cli.py platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_protocol_enforcement_health.py platform_tests/scripts/test_dispatcher_runtime.py
python -m ruff format --check groundtruth-kb/src/groundtruth_kb/bridge/disposition.py groundtruth-kb/src/groundtruth_kb/bridge/notify.py scripts/bridge_work_intent_registry.py scripts/bridge_claim_cli.py scripts/implementation_authorization.py scripts/implementation_start_gate.py scripts/protocol_enforcement_health.py scripts/dispatcher_runtime.py platform_tests/scripts/test_scan_bridge.py platform_tests/hooks/test_bridge_axis_2_surface_governance_review_terminal.py platform_tests/scripts/test_bridge_work_intent_registry.py platform_tests/scripts/test_bridge_claim_cli.py platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_protocol_enforcement_health.py platform_tests/scripts/test_dispatcher_runtime.py
```

## Acceptance Criteria

1. Terminal/non-implementation bridge-kind `GO` records are excluded from Prime implementation actionability in shared disposition, notification, manual scan, AXIS-2, protocol-health, and dispatcher-report surfaces.
2. Terminal/non-implementation bridge-kind `GO` records cannot acquire a `go_implementation` work-intent claim through the generic claim path.
3. Denied terminal-kind claims create no claim row, implementation packet, current packet, named packet, dispatcher launch state, or protected mutation authorization.
4. Ordinary implementation `GO` and `NO-GO` behavior is preserved.
5. `NEW`, `REVISED`, and `NO-ACTION` Loyal Opposition review routing is preserved.
6. Focused tests and Ruff gates pass and are reported in the post-implementation bridge report.

## Rollback

Revert only the source and test hunks in the target list. Because no database, PAUTH, external-system, release, or deployment mutation is in scope, rollback is limited to source/test restoration and removal of transient test runtime state.

## Owner Decisions / Input

- `DELIB-202666081` records the Gate 1.25 no-claim/non-implementation boundary and independent safety audit that produced `WI-5184`.
- `DELIB-202666274` authorizes Authority Foundations project-scoped implementation work through the cited PAUTH.
- No new owner decision is requested by this proposal.

## Prior Deliberations

- `DELIB-202666081` - Gate 1.25 no-claim/non-implementation boundary.
- `DELIB-202666274` - active Authority Foundations project-scope PAUTH.
- `bridge/gtkb-authority-foundations-project-authorization-004.md` - latest NO-GO that identifies the bootstrap and terminal-kind claimability gap.
- `bridge/gtkb-wi5249-prime-no-action-claim-filer-006.md` - latest NO-GO requiring WI-5184 to have governed ownership before WI-5249 can proceed.
- `WI-5184` - backlog record for terminal non-implementation bridge-kind claim/actionability behavior.

## Pre-Filing Preflight

Applicability preflight:

- Command: `python scripts/bridge_applicability_preflight.py --content-file .gtkb-state/bridge-drafts/gtkb-wi5184-terminal-nonimplementation-go-nonclaimable-001.md --json`
- Result: `preflight_passed: true`
- `missing_required_specs: []`
- `missing_advisory_specs: []`
- `blocking_errors: []`
- `packet_hash: sha256:8a89598ede95e07e3689ce8d145fa4ded66c287139b1f2812506f07a23b9ba03`

Clause applicability preflight:

- Command: `python scripts/adr_dcl_clause_preflight.py --content-file .gtkb-state/bridge-drafts/gtkb-wi5184-terminal-nonimplementation-go-nonclaimable-001.md`
- Result: exit 0
- must_apply: 3
- Evidence gaps in must_apply clauses: 0
- Blocking gaps: 0

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
