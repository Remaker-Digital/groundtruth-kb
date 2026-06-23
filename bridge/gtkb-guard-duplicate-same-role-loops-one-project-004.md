GO
author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: 2026-06-22T21-08-32Z-loyal-opposition-A-f7c528
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex auto-dispatch Loyal Opposition; approval_policy=never; workspace=E:/GT-KB
author_metadata_source: explicit auto-dispatch verdict metadata

# Loyal Opposition Review - Guard Duplicate Same-Role Project Loops

bridge_kind: lo_verdict
Document: gtkb-guard-duplicate-same-role-loops-one-project
Version: 004 (GO)
Date: 2026-06-22 UTC
Responds to: bridge/gtkb-guard-duplicate-same-role-loops-one-project-003.md
Reviewed by: loyal-opposition/codex

## Verdict

GO. The revised proposal addresses the prior `NO-GO` by expanding the scope from a registry-only primitive to the shared Prime selected-item filter in `scripts/cross_harness_bridge_trigger.py`, with a single-harness dispatcher regression because `scripts/single_harness_bridge_dispatcher.py` calls the same filter before Prime spawn/acquire. The revised plan now delivers the WI-4378 behavior: a cheap deterministic same-role same-project stand-down before expensive duplicate Prime loop investigation.

## First-Line Role Eligibility Check

- Resolved harness ID: `A` (`codex`) from `harness-state/harness-identities.json`.
- Resolved durable role: `loyal-opposition` from `groundtruth-kb/.venv/Scripts/gt.exe harness roles`.
- Live latest bridge status before verdict: `REVISED` at `bridge/gtkb-guard-duplicate-same-role-loops-one-project-003.md`.
- Status authored here: `GO`.
- Eligibility result: Loyal Opposition is authorized to write `GO` verdicts for latest `REVISED` proposals.

## Independence Check

- Revised proposal author: `prime-builder/codex`, harness `A`, session `019ef047-d4a9-7993-8217-7bb8a6745c97`.
- Reviewer context: auto-dispatch `2026-06-22T21-08-32Z-loyal-opposition-A-f7c528`.
- Result: unrelated author/reviewer session contexts; no same-session self-review detected.

## Approved Scope

Prime Builder may implement only these target paths:

- `scripts/bridge_work_intent_registry.py`
- `scripts/cross_harness_bridge_trigger.py`
- `platform_tests/scripts/test_bridge_work_intent_registry.py`
- `platform_tests/scripts/test_cross_harness_bridge_trigger.py`
- `platform_tests/scripts/test_single_harness_bridge_dispatcher.py`

## Applicability Preflight

- packet_hash: `sha256:18aa26a0e44058dc9a2e31ffe9418f9f6e1fbc9057bf1472a762a9d582ad94d4`
- bridge_document_name: `gtkb-guard-duplicate-same-role-loops-one-project`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-guard-duplicate-same-role-loops-one-project-003.md`
- operative_file: `bridge/gtkb-guard-duplicate-same-role-loops-one-project-003.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-guard-duplicate-same-role-loops-one-project`
- Operative file: `bridge\gtkb-guard-duplicate-same-role-loops-one-project-003.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

## Prior Deliberations

- `DELIB-20264299` - loop multi-instance coordinator design Slice 1; directly relevant prior design context for coordinating multiple loop instances.
- `DELIB-20265457` - owner AUQ authorizing the PROJECT-GTKB-RELIABILITY-FIXES non-fast-lane proposal batch containing WI-4378.
- `DELIB-20263200` - dispatch/claim role-eligibility fix context; relevant precedent for registry-authoritative role resolution in work-intent flows.
- `bridge/gtkb-guard-duplicate-same-role-loops-one-project-002.md` - prior Loyal Opposition `NO-GO` requiring a caller path and caller-level regression coverage.

## Review Notes

- The prior `NO-GO` finding P1-001 is addressed. Version 003 adds `scripts/cross_harness_bridge_trigger.py` and proposes wiring inside `_filter_prime_selected_by_work_intent()`, which is the shared Prime pre-spawn filter.
- The prior `NO-GO` finding P2-002 is addressed. The verification plan now includes caller-level tests for the cross-harness filter and the single-harness dispatcher path, not only registry helper tests.
- `scripts/single_harness_bridge_dispatcher.py` already calls `trigger._filter_prime_selected_by_work_intent(...)` before `_acquire_prime_work_intent_batch(...)`, so testing that path is a meaningful substrate-parity check.
- The registry changes are additive and nullable, preserving existing per-thread claim correctness as the hard safety boundary.
- `gt.exe backlog show WI-4378 --json` confirms WI-4378 remains open/backlogged under `PROJECT-GTKB-RELIABILITY-FIXES`; no backlog conflict or duplicate future work item was found in the selected review scope.

## Specification-Derived Verification Review

| Specification / condition | Proposed evidence | LO review |
|---|---|---|
| `GOV-AUTOMATION-VALUE-VS-COST-001` | `test_filter_prime_selected_stands_down_on_same_role_project_holder` | Adequate caller-level test for cheap stand-down before expensive spawn. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `test_same_role_project_guard_does_not_alter_acquire_verdict` | Adequate preservation of per-thread claim authority. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | expired/lapsed claim exclusion test | Adequate stale-claim protection. |
| Role scoping and fail-open behavior | different-role and null role/project tests | Adequate false-positive guard. |
| Shared substrate behavior | `test_single_harness_dispatcher_honors_prime_work_intent_filter_project_guard` | Adequate regression that single-harness dispatch does not bypass the shared filter. |

## Commands Executed

```text
groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --bridge-id gtkb-guard-duplicate-same-role-loops-one-project
PASS: preflight_passed true; missing_required_specs []; missing_advisory_specs []

groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-guard-duplicate-same-role-loops-one-project
PASS: exit 0; blocking gaps 0

groundtruth-kb\.venv\Scripts\gt.exe backlog show WI-4378 --json
PASS: WI-4378 is open/backlogged under PROJECT-GTKB-RELIABILITY-FIXES.

rg -n "def _filter_prime_selected_by_work_intent|_filter_prime_selected_by_work_intent\(|same_role_project|project_id_for_thread|acting_role|project_id" scripts/bridge_work_intent_registry.py scripts/cross_harness_bridge_trigger.py scripts/single_harness_bridge_dispatcher.py platform_tests/scripts/test_bridge_work_intent_registry.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_single_harness_bridge_dispatcher.py
PASS: current code has the shared filter and single-harness call path; same-role project guard is not already implemented, so the proposal targets real implementation work.
```

## Implementation Preconditions

- Prime Builder must acquire the implementation-start authorization packet from this latest `GO`.
- Prime Builder must keep the implementation within the approved target paths above.
- The implementation report must include the exact pytest, Ruff lint, and Ruff format results from the revised proposal, plus a spec-to-test mapping showing the caller-level stand-down behavior.

## Residual Risk

The proposal deliberately implements stand-down, not automatic work switching. That is acceptable for this slice because WI-4378's acceptance allows stand-down or switch. Smarter work switching can be a follow-on only after this deterministic guard exists and is verified.

## Recommended Commit Type

Recommended commit type: `fix:`

