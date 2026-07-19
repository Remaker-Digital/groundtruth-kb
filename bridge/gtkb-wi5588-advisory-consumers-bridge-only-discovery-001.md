NEW
::init gtkb lo
::open build
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined Prime Builder role; build activity envelope
author_metadata_source: explicit_interactive_session_metadata

# Implementation Proposal - Prepare advisory consumers and metrics for bridge-only discovery

bridge_kind: prime_proposal
Document: gtkb-wi5588-advisory-consumers-bridge-only-discovery
Version: 001
Date: 2026-07-18 UTC

Project Authorization: PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-WI-5588-ADVISORY-CONSUMERS-2026-07-18
Project Authorization Candidates: [{"project_authorization_id":"PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-WI-5588-ADVISORY-CONSUMERS-2026-07-18","coverage":"exact_singleton","included_work_item_count":1,"specificity_rank":[0,1],"selected":true},{"project_authorization_id":"PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-PROJECT-LEVEL-APPROVAL-STATE-RETIREMENT-2026-06-30","coverage":"project_membership_fallback","included_work_item_count":null,"specificity_rank":[2,0],"selected":false}]
Project: PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE
Work Item: WI-5588

target_paths: ["scripts/advisory_intake_scanner.py", "scripts/advisory_grilling_gate_lint.py", "scripts/sot_compactness_audit.py", "scripts/benchmarks/advisory_latency.py", "platform_tests/scripts/test_advisory_intake_scanner.py", "platform_tests/scripts/test_advisory_grilling_gate_lint.py", "platform_tests/scripts/test_sot_compactness_audit.py", "platform_tests/scripts/test_benchmark_advisory_latency.py", "platform_tests/scripts/test_advisory_candidate_promote.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Make numbered bridge ADVISORY entries the sole advisory discovery input for the four bounded consumers and metrics surfaces, with focused rejection and canonical-evidence coverage.

Work item description: Build-only predecessor work that converges advisory discovery and measurement on canonical numbered bridge, Deliberation Archive, and MemBase evidence while preserving fail-closed validation.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5588` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/advisory_intake_scanner.py`, `scripts/advisory_grilling_gate_lint.py`, `scripts/sot_compactness_audit.py`, `scripts/benchmarks/advisory_latency.py`, `platform_tests/scripts/test_advisory_intake_scanner.py`, `platform_tests/scripts/test_advisory_grilling_gate_lint.py`, `platform_tests/scripts/test_sot_compactness_audit.py`, `platform_tests/scripts/test_benchmark_advisory_latency.py`, `platform_tests/scripts/test_advisory_candidate_promote.py`.

## Specification Links

- `DCL-SUPERSEDED-SOT-LEAKAGE-001` - auto-linked governing or work-item specification.
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
- `DCL-CANONICAL-CARRIER-NONAUTHORITY-001` - auto-linked governing or work-item specification.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - auto-linked governing or work-item specification.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs bounded project implementation authority.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - auto-linked governing or work-item specification.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - requires bounded PAUTH envelopes for new authorization state.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - auto-linked governing or work-item specification.
- `DCL-DISPATCHER-ACTIVITY-ENVELOPE-AUTHORITY-001` - auto-linked governing or work-item specification.
- `DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001` - auto-linked governing or work-item specification.
- `DCL-ACTIVITY-DISPOSITION-PROFILE-001` - auto-linked governing or work-item specification.
- `GOV-WORK-TREE-HYGIENE-001` - auto-linked governing or work-item specification.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- DELIB-20260717-CANONICAL-ARTIFACT-REFERENCE-BOUNDARY - owner direction that canonical bridge artifacts may cite only canonical carriers and that scratch evidence is session-local.
- DELIB-20260717-DISPATCHER-CONFIGURATION-TROUBLESHOOTER-HOLD - preserves the independent dispatcher-configuration hold; this source/test slice does not inspect or mutate that surface.

## Owner Decisions / Input
- `PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-WI-5588-ADVISORY-CONSUMERS-2026-07-18` - active project authorization covering `WI-5588`.

## Proposed Scope

- Update the four exact advisory consumer and metric scripts to discover advisory work only from status-bearing numbered bridge ADVISORY entries and canonical Deliberation Archive or MemBase evidence.
- Preserve owner-grilling validation, deterministic compactness and latency measurements, and explicit negative fixtures that prove unsupported inputs are rejected.
- Remove alternate report-writing and discovery branches that are not backed by canonical numbered bridge state.
- Limit implementation to the four scripts and five focused tests listed in target_paths; configuration, dispatcher control, TAFE/runtime state, credentials, deployment, release, push, history rewrite, destructive cleanup, and every other path are excluded.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5588; PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-WI-5588-ADVISORY-CONSUMERS-2026-07-18; generated by gt bridge file-implementation-proposal",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and the governed bridge proposal generators",
  "primary_route": "gt bridge file-implementation-proposal",
  "before_behavior": "Multiple bounded consumers still accept advisory inputs or outputs that are not derived from canonical numbered bridge, Deliberation Archive, or MemBase evidence.",
  "after_behavior": "Make numbered bridge ADVISORY entries the sole advisory discovery input for the four bounded consumers and metrics surfaces, with focused rejection and canonical-evidence coverage.",
  "self_descriptive_naming": "The generated title, work-item id, target paths, scope, and acceptance criteria name the proposed effect.",
  "obsolete_guidance_disposition": "No guidance is retired by proposal filing; implementation must explicitly disposition obsolete guidance.",
  "history_preservation": "The numbered bridge chain remains append-only; rollback never deletes proposal or verdict artifacts.",
  "baseline": {
    "work_item": "WI-5588",
    "project": "PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE",
    "target_paths": [
      "scripts/advisory_intake_scanner.py",
      "scripts/advisory_grilling_gate_lint.py",
      "scripts/sot_compactness_audit.py",
      "scripts/benchmarks/advisory_latency.py",
      "platform_tests/scripts/test_advisory_intake_scanner.py",
      "platform_tests/scripts/test_advisory_grilling_gate_lint.py",
      "platform_tests/scripts/test_sot_compactness_audit.py",
      "platform_tests/scripts/test_benchmark_advisory_latency.py",
      "platform_tests/scripts/test_advisory_candidate_promote.py"
    ],
    "linked_specifications": [
      "DCL-SUPERSEDED-SOT-LEAKAGE-001",
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
      "DCL-CANONICAL-CARRIER-NONAUTHORITY-001",
      "GOV-SOURCE-OF-TRUTH-FRESHNESS-001",
      "GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001",
      "PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001",
      "DCL-PROJECT-AUTHORIZATION-ENVELOPE-001",
      "DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001",
      "DCL-DISPATCHER-ACTIVITY-ENVELOPE-AUTHORITY-001",
      "DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001",
      "DCL-ACTIVITY-DISPOSITION-PROFILE-001",
      "GOV-WORK-TREE-HYGIENE-001",
      "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001"
    ]
  },
  "expected_result": {
    "summary": "Make numbered bridge ADVISORY entries the sole advisory discovery input for the four bounded consumers and metrics surfaces, with focused rejection and canonical-evidence coverage.",
    "scope": [
      "Update the four exact advisory consumer and metric scripts to discover advisory work only from status-bearing numbered bridge ADVISORY entries and canonical Deliberation Archive or MemBase evidence.",
      "Preserve owner-grilling validation, deterministic compactness and latency measurements, and explicit negative fixtures that prove unsupported inputs are rejected.",
      "Remove alternate report-writing and discovery branches that are not backed by canonical numbered bridge state.",
      "Limit implementation to the four scripts and five focused tests listed in target_paths; configuration, dispatcher control, TAFE/runtime state, credentials, deployment, release, push, history rewrite, destructive cleanup, and every other path are excluded."
    ],
    "acceptance_criteria": [
      "All four production scripts use status-bearing numbered bridge ADVISORY entries as their only advisory discovery input and do not create or load an alternate advisory store.",
      "The focused tests prove bridge-only discovery, owner-grilling preservation, canonical evidence metrics, and fail-closed rejection of unsupported inputs.",
      "The implementation diff contains only the nine declared target paths and makes no configuration, dispatcher, TAFE, runtime-state, credential, deployment, release, push, history-rewrite, or cleanup mutation.",
      "The implementation report carries forward every linked specification, maps each to executed evidence, and reports exact pytest and both ruff results."
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
| `DCL-SUPERSEDED-SOT-LEAKAGE-001` | Run focused rejection cases proving unsupported source and output modes cannot become operational advisory authority. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run both proposal preflights and verify the implementation report is filed through the governed numbered bridge writer. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Verify the implementation and report preserve the numbered proposal, test evidence, and terminal verification as durable governed artifacts. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run bridge applicability and ADR/DCL clause preflights against the filed proposal with no missing specifications or blocking gaps. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Execute the five focused pytest files plus ruff check and ruff format --check on all nine Python targets and include observed results in the report. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Validate the Project Authorization, Project, and Work Item headers and the project bridge-thread link. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Verify no new owner-decision or approval path is added and existing owner-grilling behavior remains unchanged. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Verify every target, test fixture, report, and generated evidence path remains within E:/GT-KB. |
| `GOV-STANDING-BACKLOG-001` | Verify WI-5588 remains linked in MemBase throughout proposal, implementation, report, and terminal verification. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run the focused hook-adjacent scanner tests and confirm the implementation does not rely on a harness-specific interception assumption. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Inspect the implementation report for explicit source, test, decision, risk, and rollback linkage rather than session-local claims. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Verify unsupported findings become explicit rejection evidence and any new implementation defect becomes a governed follow-on work item. |
| `DCL-CANONICAL-CARRIER-NONAUTHORITY-001` | Run all five focused tests and inspect the four production scripts to prove advisory discovery is exclusively backed by numbered bridge state. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Run scanner, compactness, and latency tests proving each result derives from current numbered bridge or canonical Deliberation Archive evidence. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Before any protected edit, validate the active WI-5588 project authorization and record the selected authorization in the schema-v3 start packet. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Require independent GO, a matching claim, and implementation-start success before every protected mutation. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | Validate that the selected authorization covers WI-5588, source and test mutation classes, and exactly the declared target set. |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Run operation-time authorization checks for each protected edit and each test command that can mutate governed runtime evidence. |
| `DCL-DISPATCHER-ACTIVITY-ENVELOPE-AUTHORITY-001` | Confirm implementation runs only in a build activity envelope and that no ops or dispatcher configuration authority is inferred. |
| `DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001` | Inspect the final diff and test evidence to prove no direct dispatcher, TAFE, or harness-complex internal access was added. |
| `DCL-ACTIVITY-DISPOSITION-PROFILE-001` | Record the build-envelope disposition and verify the exact source/test-only operation class before implementation. |
| `GOV-WORK-TREE-HYGIENE-001` | Capture pre-edit hashes and final git diff for the nine targets, preserving every unrelated dirty worktree byte. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Run the five focused tests and directly affected advisory-intake regressions with no degradation of canonical bridge behavior. |

## Acceptance Criteria

- All four production scripts use status-bearing numbered bridge ADVISORY entries as their only advisory discovery input and do not create or load an alternate advisory store.
- The focused tests prove bridge-only discovery, owner-grilling preservation, canonical evidence metrics, and fail-closed rejection of unsupported inputs.
- The implementation diff contains only the nine declared target paths and makes no configuration, dispatcher, TAFE, runtime-state, credential, deployment, release, push, history-rewrite, or cleanup mutation.
- The implementation report carries forward every linked specification, maps each to executed evidence, and reports exact pytest and both ruff results.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/advisory_intake_scanner.py`
- `scripts/advisory_grilling_gate_lint.py`
- `scripts/sot_compactness_audit.py`
- `scripts/benchmarks/advisory_latency.py`
- `platform_tests/scripts/test_advisory_intake_scanner.py`
- `platform_tests/scripts/test_advisory_grilling_gate_lint.py`
- `platform_tests/scripts/test_sot_compactness_audit.py`
- `platform_tests/scripts/test_benchmark_advisory_latency.py`
- `platform_tests/scripts/test_advisory_candidate_promote.py`

## Recommended Commit Type

`feat`
