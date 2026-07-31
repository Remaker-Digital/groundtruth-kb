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

# Implementation Proposal - Emit canonical audit-helper outputs without auxiliary files

bridge_kind: prime_proposal
Document: gtkb-wi5590-audit-helper-canonical-outputs
Version: 001
Date: 2026-07-18 UTC

Project Authorization: PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-WI-5590-AUDIT-REPORT-WRITERS-2026-07-18
Project Authorization Candidates: [{"project_authorization_id":"PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-WI-5590-AUDIT-REPORT-WRITERS-2026-07-18","coverage":"exact_singleton","included_work_item_count":1,"specificity_rank":[0,1],"selected":true},{"project_authorization_id":"PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-PROJECT-LEVEL-APPROVAL-STATE-RETIREMENT-2026-06-30","coverage":"project_membership_fallback","included_work_item_count":null,"specificity_rank":[2,0],"selected":false}]
Project: PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE
Work Item: WI-5590

target_paths: ["scripts/audit_spa_cluster_test_id_inventory.py", "scripts/generate_codex_backlog_cleanup_inventory.py", "scripts/generate_codex_backlog_cleanup_review_packet.py", "scripts/harness_skill_effectiveness.py", "scripts/project_child_wi_checklist.py", "scripts/evidence_freshness_boundary.py", "platform_tests/scripts/test_audit_spa_cluster_test_id_inventory.py", "platform_tests/scripts/test_codex_backlog_cleanup_inventory.py", "platform_tests/scripts/test_evidence_freshness_boundary.py", "platform_tests/scripts/test_harness_skill_effectiveness.py", "platform_tests/scripts/test_project_child_wi_checklist.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Replace auxiliary file-output defaults in bounded audit and checklist helpers with deterministic stdout or JSON for governed promotion.

Work item description: Build-only report-writer slice that removes implicit auxiliary file creation from six audit and checklist helpers, preserves their read-only computations, and adds five focused tests.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5590` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/audit_spa_cluster_test_id_inventory.py`, `scripts/generate_codex_backlog_cleanup_inventory.py`, `scripts/generate_codex_backlog_cleanup_review_packet.py`, `scripts/harness_skill_effectiveness.py`, `scripts/project_child_wi_checklist.py`, `scripts/evidence_freshness_boundary.py`, `platform_tests/scripts/test_audit_spa_cluster_test_id_inventory.py`, `platform_tests/scripts/test_codex_backlog_cleanup_inventory.py`, `platform_tests/scripts/test_evidence_freshness_boundary.py`, `platform_tests/scripts/test_harness_skill_effectiveness.py`, `platform_tests/scripts/test_project_child_wi_checklist.py`.

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
- `PB-STANDING-BACKLOG-CONTINUITY-001` - auto-linked governing or work-item specification.
- `SPEC-1816` - auto-linked governing or work-item specification.
- `SPEC-1818` - auto-linked governing or work-item specification.
- `SPEC-1819` - auto-linked governing or work-item specification.
- `SPEC-1820` - auto-linked governing or work-item specification.
- `SPEC-1821` - auto-linked governing or work-item specification.
- `SPEC-1822` - auto-linked governing or work-item specification.
- `SPEC-1823` - auto-linked governing or work-item specification.
- `SPEC-1824` - auto-linked governing or work-item specification.
- `SPEC-1826` - auto-linked governing or work-item specification.
- `SPEC-1827` - auto-linked governing or work-item specification.
- `SPEC-1837` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-20260717-CANONICAL-ARTIFACT-REFERENCE-BOUNDARY` - owner direction that canonical artifacts depend only on canonical evidence carriers and governed identities.
- `DELIB-20260717-DISPATCHER-CONFIGURATION-TROUBLESHOOTER-HOLD` - preserves the independent dispatcher-configuration hold; this source/test proposal neither inspects nor mutates that surface.
- _No additional directly applicable prior deliberation was found in the canonical Deliberation Archive search for WI-5590 and its exact helper scope._

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-WI-5590-AUDIT-REPORT-WRITERS-2026-07-18` - active project authorization covering `WI-5590`.

## Proposed Scope

- Remove implicit file-output defaults and output-path options from the six declared audit, inventory, effectiveness, checklist, and freshness helpers.
- Emit deterministic stdout or JSON only so callers can promote results through governed canonical writers when a durable artifact is required.
- Preserve read-only calculation, classification, ordering, and freshness behavior and add focused coverage for the SPA inventory CLI.
- Limit implementation to the eleven declared targets; configuration, dispatcher control, TAFE/runtime state, credentials, deployment, release, push, history rewrite, destructive cleanup, and every other path are excluded.

## Cross-Harness Disposition

- **Codex**: Consumes the same deterministic stdout or JSON contract; no Codex-only file output.
- **Claude Code**: Consumes the same deterministic stdout or JSON contract; no Claude-only file output.
- **Antigravity**: Consumes the same deterministic stdout or JSON contract; no Antigravity-only file output.
- **Cursor**: Consumes the same deterministic stdout or JSON contract; no Cursor-only file output.
- **Headless and interactive callers**: Receive identical deterministic output and no implicit auxiliary file creation.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5590; PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-WI-5590-AUDIT-REPORT-WRITERS-2026-07-18; generated by gt bridge file-implementation-proposal",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and the governed bridge proposal generators",
  "primary_route": "gt bridge file-implementation-proposal",
  "before_behavior": "Build activity-envelope child of WI-5582. Mutate exactly scripts/audit_spa_cluster_test_id_inventory.py, scripts/generate_codex_backlog_cleanup_inventory.py, scripts/generate_codex_backlog_cleanup_review_packet.py, scripts/harness_skill_effectiveness.py, scripts/project_child_wi_checklist.py, scripts/evidence_freshness_boundary.py, platform_tests/scripts/test_audit_spa_cluster_test_id_inventory.py, platform_tests/scripts/test_codex_backlog_cleanup_inventory.py, platform_tests/scripts/test_evidence_freshness_boundary.py, platform_tests/scripts/test_harness_skill_effectiveness.py, and platform_tests/scripts/test_project_child_wi_checklist.py. Remove file-output defaults and options that can recreate the owner-retired carrier; emit deterministic stdout/JSON for callers to promote through governed Advisory Proposal, Deliberation Archive, MemBase, or numbered bridge writers. Preserve read-only calculation behavior and add focused coverage for the currently untested SPA inventory CLI. Configuration, dispatcher, TAFE, runtime state, credentials, deployment, release, push, history rewrite, destructive cleanup, and all other paths are excluded.",
  "after_behavior": "Replace auxiliary file-output defaults in bounded audit and checklist helpers with deterministic stdout or JSON for governed promotion.",
  "self_descriptive_naming": "The generated title, work-item id, target paths, scope, and acceptance criteria name the proposed effect.",
  "obsolete_guidance_disposition": "No guidance is retired by proposal filing; implementation must explicitly disposition obsolete guidance.",
  "history_preservation": "The numbered bridge chain remains append-only; rollback never deletes proposal or verdict artifacts.",
  "baseline": {
    "work_item": "WI-5590",
    "project": "PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE",
    "target_paths": [
      "scripts/audit_spa_cluster_test_id_inventory.py",
      "scripts/generate_codex_backlog_cleanup_inventory.py",
      "scripts/generate_codex_backlog_cleanup_review_packet.py",
      "scripts/harness_skill_effectiveness.py",
      "scripts/project_child_wi_checklist.py",
      "scripts/evidence_freshness_boundary.py",
      "platform_tests/scripts/test_audit_spa_cluster_test_id_inventory.py",
      "platform_tests/scripts/test_codex_backlog_cleanup_inventory.py",
      "platform_tests/scripts/test_evidence_freshness_boundary.py",
      "platform_tests/scripts/test_harness_skill_effectiveness.py",
      "platform_tests/scripts/test_project_child_wi_checklist.py"
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
      "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
      "PB-STANDING-BACKLOG-CONTINUITY-001",
      "SPEC-1816",
      "SPEC-1818",
      "SPEC-1819",
      "SPEC-1820",
      "SPEC-1821",
      "SPEC-1822",
      "SPEC-1823",
      "SPEC-1824",
      "SPEC-1826",
      "SPEC-1827",
      "SPEC-1837"
    ]
  },
  "expected_result": {
    "summary": "Replace auxiliary file-output defaults in bounded audit and checklist helpers with deterministic stdout or JSON for governed promotion.",
    "scope": [
      "Remove implicit file-output defaults and output-path options from the six declared audit, inventory, effectiveness, checklist, and freshness helpers.",
      "Emit deterministic stdout or JSON only so callers can promote results through governed canonical writers when a durable artifact is required.",
      "Preserve read-only calculation, classification, ordering, and freshness behavior and add focused coverage for the SPA inventory CLI.",
      "Limit implementation to the eleven declared targets; configuration, dispatcher control, TAFE/runtime state, credentials, deployment, release, push, history rewrite, destructive cleanup, and every other path are excluded."
    ],
    "acceptance_criteria": [
      "None of the six helpers creates an auxiliary report or inventory file by default, by compatibility fallback, or through a retained output-path option.",
      "Each helper emits stable stdout or JSON with its existing calculation and classification semantics preserved.",
      "All five focused test files, ruff check, and ruff format --check pass on the exact declared targets.",
      "The final implementation diff contains exactly the eleven declared paths or a reviewed subset and leaves dispatcher configuration and runtime control untouched."
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
| `DCL-SUPERSEDED-SOT-LEAKAGE-001` | Run negative CLI cases proving no default, option, or fallback recreates an auxiliary report file and unsupported output destinations fail closed. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run both proposal preflights and require the later implementation report to use the governed numbered bridge writer. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Verify helper results are deterministic stdout or JSON that callers can promote through canonical MemBase, Deliberation Archive, Advisory Proposal, or numbered bridge writers. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run applicability and ADR/DCL clause preflights against the exact filed proposal with no missing specifications or blocking gaps. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Execute all five focused test files plus ruff check and ruff format --check on all eleven declared Python targets and report exact results. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Validate the exact PAUTH, project, work item, inline target_paths, and project bridge-thread link. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Verify audit helpers neither invent owner decisions nor treat generated inventory output as owner approval. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Verify all helper inputs, test fixtures, and emitted results remain inside E:/GT-KB or canonical MemBase and no external live dependency is opened. |
| `GOV-STANDING-BACKLOG-001` | Run the backlog inventory and child-checklist tests proving complete deterministic WI coverage without auxiliary report files. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run focused CLI tests directly and prove output behavior is independent of any one harness interception path. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Inspect traceability from each deterministic observation to its work item, specification, test, implementation report, and independent verdict. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run checklist tests proving missing, blocked, terminal, and ready child states remain explicit and deterministic. |
| `DCL-CANONICAL-CARRIER-NONAUTHORITY-001` | Inspect all six helpers and run negative tests proving they emit data only and do not create an auxiliary authority surface. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Run freshness-boundary and inventory cases proving every state claim derives from a current canonical read and records stale or unavailable state explicitly. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Validate the active exact-singleton WI-5590 authorization before protected edits and bind it into the schema-v3 start packet. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Require independent GO, exact claim, schema-v3 start, and operation-time authorization before any protected mutation. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | Verify the selected PAUTH covers WI-5590, bridge/metadata/source/test classes, and exactly the eleven declared targets. |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Revalidate authorization for every protected edit and governed evidence-producing side effect. |
| `DCL-DISPATCHER-ACTIVITY-ENVELOPE-AUTHORITY-001` | Confirm implementation runs only in a build activity envelope and receives no ops or dispatcher-configuration authority. |
| `DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001` | Inspect the final diff to prove no helper adds direct dispatcher, TAFE, or harness-complex internal access. |
| `DCL-ACTIVITY-DISPOSITION-PROFILE-001` | Record and validate the source/test-only build disposition at implementation start and operation time. |
| `GOV-WORK-TREE-HYGIENE-001` | Capture pre-edit hashes and the final eleven-path diff while preserving unrelated dirty and staged bytes. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Run all focused suites and compare deterministic JSON/stdout fields to prove existing audit, checklist, effectiveness, and freshness semantics remain available. |
| `PB-STANDING-BACKLOG-CONTINUITY-001` | Run backlog inventory and review-packet cases proving no open WI is omitted and no generated file becomes a competing continuation authority. |
| `SPEC-1816` | Run the new SPA audit CLI test proving the entitlement API specification receives an explicit current binding classification. |
| `SPEC-1818` | Run the new SPA audit CLI test proving full service-management specification coverage is reported from current MemBase bindings. |
| `SPEC-1819` | Run the new SPA audit CLI test proving runtime-configuration specification coverage is reported from current MemBase bindings. |
| `SPEC-1820` | Run the new SPA audit CLI test proving allow/block-list specification coverage is reported from current MemBase bindings. |
| `SPEC-1821` | Run the new SPA audit CLI test proving back-off/retry specification coverage is reported from current MemBase bindings. |
| `SPEC-1822` | Run the new SPA audit CLI test proving alert-threshold specification coverage is reported from current MemBase bindings. |
| `SPEC-1823` | Run the new SPA audit CLI test proving notification-channel specification coverage is reported from current MemBase bindings. |
| `SPEC-1824` | Run the new SPA audit CLI test proving feature-flag specification coverage is reported from current MemBase bindings. |
| `SPEC-1826` | Run the new SPA audit CLI test proving test-execution-trigger specification coverage is reported from current MemBase bindings. |
| `SPEC-1827` | Run the new SPA audit CLI test proving diagnostic-export specification coverage is reported from current MemBase bindings. |
| `SPEC-1837` | Run recycled-test-ID cases proving latest-version bindings to log-retention remain distinct from the SPA specification set. |

## Acceptance Criteria

- None of the six helpers creates an auxiliary report or inventory file by default, by compatibility fallback, or through a retained output-path option.
- Each helper emits stable stdout or JSON with its existing calculation and classification semantics preserved.
- All five focused test files, ruff check, and ruff format --check pass on the exact declared targets.
- The final implementation diff contains exactly the eleven declared paths or a reviewed subset and leaves dispatcher configuration and runtime control untouched.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/audit_spa_cluster_test_id_inventory.py`
- `scripts/generate_codex_backlog_cleanup_inventory.py`
- `scripts/generate_codex_backlog_cleanup_review_packet.py`
- `scripts/harness_skill_effectiveness.py`
- `scripts/project_child_wi_checklist.py`
- `scripts/evidence_freshness_boundary.py`
- `platform_tests/scripts/test_audit_spa_cluster_test_id_inventory.py`
- `platform_tests/scripts/test_codex_backlog_cleanup_inventory.py`
- `platform_tests/scripts/test_evidence_freshness_boundary.py`
- `platform_tests/scripts/test_harness_skill_effectiveness.py`
- `platform_tests/scripts/test_project_child_wi_checklist.py`

## Recommended Commit Type

`feat`
