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

# Implementation Proposal - Canonicalize Deliberation Archive harvest inputs

bridge_kind: prime_proposal
Document: gtkb-wi5589-da-tooling-canonical-inputs
Version: 001
Date: 2026-07-18 UTC

Project Authorization: PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-WI-5589-DELIBERATION-TOOLING-2026-07-18
Project Authorization Candidates: [{"project_authorization_id":"PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-WI-5589-DELIBERATION-TOOLING-2026-07-18","coverage":"exact_singleton","included_work_item_count":1,"specificity_rank":[0,1],"selected":true},{"project_authorization_id":"PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-PROJECT-LEVEL-APPROVAL-STATE-RETIREMENT-2026-06-30","coverage":"project_membership_fallback","included_work_item_count":null,"specificity_rank":[2,0],"selected":false}]
Project: PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE
Work Item: WI-5589

target_paths: ["scripts/backfill_lo_reports.py", "scripts/deliberation_health.py", "scripts/harvest_session_deliberations.py", "scripts/inventory_lo_bridge_history_backfill.py", "platform_tests/unit/test_lo_report_backfill.py", "platform_tests/scripts/test_deliberation_archive_spec2098_coverage.py", "platform_tests/scripts/test_harvest_session_thread_level.py", "platform_tests/scripts/test_harvest_loud_wrap.py", "platform_tests/scripts/test_inventory_lo_bridge_history_backfill.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Converge Deliberation Archive backfill, health, harvest, and inventory tooling on canonical MemBase and numbered bridge inputs.

Work item description: Build-only Deliberation Archive tooling work that converges backfill, health, harvest, and inventory behavior on canonical MemBase and numbered bridge inputs.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5589` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/backfill_lo_reports.py`, `scripts/deliberation_health.py`, `scripts/harvest_session_deliberations.py`, `scripts/inventory_lo_bridge_history_backfill.py`, `platform_tests/unit/test_lo_report_backfill.py`, `platform_tests/scripts/test_deliberation_archive_spec2098_coverage.py`, `platform_tests/scripts/test_harvest_session_thread_level.py`, `platform_tests/scripts/test_harvest_loud_wrap.py`, `platform_tests/scripts/test_inventory_lo_bridge_history_backfill.py`.

## Specification Links

- `DCL-CANONICAL-CARRIER-NONAUTHORITY-001` - auto-linked governing or work-item specification.
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
- `DCL-SUPERSEDED-SOT-LEAKAGE-001` - auto-linked governing or work-item specification.
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
- `ADR-0001` - auto-linked governing or work-item specification.
- `SPEC-2098` - auto-linked governing or work-item specification.
- `SPEC-DA-HARVEST-INCLUSION` - auto-linked governing or work-item specification.
- `SPEC-DA-HARVEST-EXCLUSION` - auto-linked governing or work-item specification.
- `SPEC-DA-RETROACTIVE-SWEEP` - auto-linked governing or work-item specification.
- `SPEC-DA-THREAD-COMPRESSION` - auto-linked governing or work-item specification.
- `SPEC-DA-COVERAGE-METRIC` - auto-linked governing or work-item specification.
- `SPEC-DA-MECHANICAL-ENFORCE` - auto-linked governing or work-item specification.

## Prior Deliberations

- DELIB-20260717-CANONICAL-ARTIFACT-REFERENCE-BOUNDARY - owner direction that canonical artifacts may depend only on canonical evidence carriers.
- DELIB-0621 - prior Deliberation Archive review covering dedupe, source taxonomy, relation links, redaction, and harvest-test obligations.
- DELIB-20260717-DISPATCHER-CONFIGURATION-TROUBLESHOOTER-HOLD - preserves the independent dispatcher-configuration hold; this source/test slice does not inspect or mutate that surface.

## Owner Decisions / Input
- `PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-WI-5589-DELIBERATION-TOOLING-2026-07-18` - active project authorization covering `WI-5589`.

## Proposed Scope

- Remove default or implicit scan and import routes that are not backed by canonical MemBase, Deliberation Archive, or status-bearing numbered bridge artifacts.
- Preserve reusable pure verdict parsing, redaction, dedupe, thread compression, relation linking, and deterministic inventory behavior.
- Treat historical source_ref values as append-only data that cannot become live filesystem dependencies.
- Limit implementation to the four scripts and five focused tests in target_paths; configuration, dispatcher control, TAFE/runtime state, credentials, deployment, release, push, history rewrite, destructive cleanup, and every other path are excluded.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5589; PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-WI-5589-DELIBERATION-TOOLING-2026-07-18; generated by gt bridge file-implementation-proposal",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and the governed bridge proposal generators",
  "primary_route": "gt bridge file-implementation-proposal",
  "before_behavior": "Deliberation Archive tooling still contains implicit input and output assumptions that are not consistently derived from canonical MemBase or numbered bridge authority.",
  "after_behavior": "Converge Deliberation Archive backfill, health, harvest, and inventory tooling on canonical MemBase and numbered bridge inputs.",
  "self_descriptive_naming": "The generated title, work-item id, target paths, scope, and acceptance criteria name the proposed effect.",
  "obsolete_guidance_disposition": "No guidance is retired by proposal filing; implementation must explicitly disposition obsolete guidance.",
  "history_preservation": "The numbered bridge chain remains append-only; rollback never deletes proposal or verdict artifacts.",
  "baseline": {
    "work_item": "WI-5589",
    "project": "PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE",
    "target_paths": [
      "scripts/backfill_lo_reports.py",
      "scripts/deliberation_health.py",
      "scripts/harvest_session_deliberations.py",
      "scripts/inventory_lo_bridge_history_backfill.py",
      "platform_tests/unit/test_lo_report_backfill.py",
      "platform_tests/scripts/test_deliberation_archive_spec2098_coverage.py",
      "platform_tests/scripts/test_harvest_session_thread_level.py",
      "platform_tests/scripts/test_harvest_loud_wrap.py",
      "platform_tests/scripts/test_inventory_lo_bridge_history_backfill.py"
    ],
    "linked_specifications": [
      "DCL-CANONICAL-CARRIER-NONAUTHORITY-001",
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
      "DCL-SUPERSEDED-SOT-LEAKAGE-001",
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
      "ADR-0001",
      "SPEC-2098",
      "SPEC-DA-HARVEST-INCLUSION",
      "SPEC-DA-HARVEST-EXCLUSION",
      "SPEC-DA-RETROACTIVE-SWEEP",
      "SPEC-DA-THREAD-COMPRESSION",
      "SPEC-DA-COVERAGE-METRIC",
      "SPEC-DA-MECHANICAL-ENFORCE"
    ]
  },
  "expected_result": {
    "summary": "Converge Deliberation Archive backfill, health, harvest, and inventory tooling on canonical MemBase and numbered bridge inputs.",
    "scope": [
      "Remove default or implicit scan and import routes that are not backed by canonical MemBase, Deliberation Archive, or status-bearing numbered bridge artifacts.",
      "Preserve reusable pure verdict parsing, redaction, dedupe, thread compression, relation linking, and deterministic inventory behavior.",
      "Treat historical source_ref values as append-only data that cannot become live filesystem dependencies.",
      "Limit implementation to the four scripts and five focused tests in target_paths; configuration, dispatcher control, TAFE/runtime state, credentials, deployment, release, push, history rewrite, destructive cleanup, and every other path are excluded."
    ],
    "acceptance_criteria": [
      "Backfill, health, harvest, and inventory tools accept only canonical MemBase, Deliberation Archive, and numbered bridge discovery inputs.",
      "Historical source references remain queryable data but are never opened, imported, copied, or resolved as live paths.",
      "Dedupe, source taxonomy, relation links, redaction, thread compression, coverage metrics, and non-mutating inventory tests all pass.",
      "The final implementation diff contains exactly the nine declared paths or a reviewed subset, with both ruff gates and focused pytest green."
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
| `DCL-CANONICAL-CARRIER-NONAUTHORITY-001` | Run all five focused suites and inspect four tools to prove DA harvest and health inputs are restricted to MemBase, Deliberation Archive, and status-bearing numbered bridge artifacts. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run proposal preflights and verify numbered bridge history remains canonical, append-only, and the sole bridge input. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Verify harvested decisions, findings, links, reports, and review outcomes remain durable governed artifacts. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run applicability and clause preflights against the filed proposal with no missing specs or blocking gaps. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Execute all five focused test files plus ruff check and ruff format --check on every Python target and report exact results. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Validate project authorization, project, work item, target paths, and project bridge linkage. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Verify DA tooling does not invent owner decisions and preserves existing owner-conversation provenance. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Verify all inputs, fixtures, reports, and outputs remain within E:/GT-KB and canonical MemBase. |
| `GOV-STANDING-BACKLOG-001` | Verify WI-5589 remains linked in MemBase through proposal, implementation, report, and terminal verification. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run focused tooling tests directly and prove correctness is independent of one harness interception implementation. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Inspect traceability from source artifact through DA row, links, health evidence, proposal, report, and verification. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Verify inclusion, exclusion, drift, and already-harvested classifications remain explicit and deterministic. |
| `DCL-SUPERSEDED-SOT-LEAKAGE-001` | Run negative fixtures proving historical source_ref text is treated as append-only data and never resolved as a live filesystem dependency. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Run health, harvest, and inventory tests proving current claims derive from fresh MemBase and numbered bridge reads. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Validate the active WI-5589 exact-singleton PAUTH before protected edits and record it in the schema-v3 start packet. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Require independent GO, claim, start packet, and operation-time authorization before every protected mutation. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | Verify the selected PAUTH covers WI-5589 source/test classes and exactly the nine declared targets. |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Revalidate the selected authorization before each protected edit and governed evidence operation. |
| `DCL-DISPATCHER-ACTIVITY-ENVELOPE-AUTHORITY-001` | Confirm implementation runs only in a build activity envelope and receives no ops or dispatcher configuration authority. |
| `DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001` | Inspect the final diff to prove DA tooling adds no direct dispatcher, TAFE, or harness-complex internal access. |
| `DCL-ACTIVITY-DISPOSITION-PROFILE-001` | Record and validate the source/test-only build disposition at start and operation time. |
| `GOV-WORK-TREE-HYGIENE-001` | Capture pre-edit hashes and final nine-path diff while preserving unrelated dirty worktree bytes. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Run the complete focused DA harvest/health suites with no regression in dedupe, compression, redaction, or health metrics. |
| `ADR-0001` | Verify MemBase, operational notepad, and Deliberation Archive tiers remain distinct in every harvested and health path. |
| `SPEC-2098` | Execute the full SPEC-2098 coverage test for source types, fields, redaction, dedupe, linking, freshness, and indexing behavior. |
| `SPEC-DA-HARVEST-INCLUSION` | Run eligible and already-harvested classification tests against canonical numbered bridge inputs. |
| `SPEC-DA-HARVEST-EXCLUSION` | Run size, redaction-survivor, unsupported-input, and non-authoritative-source exclusion tests. |
| `SPEC-DA-RETROACTIVE-SWEEP` | Run deterministic manifest, content-drift reclassification, and idempotent replay tests. |
| `SPEC-DA-THREAD-COMPRESSION` | Run thread-level harvest tests proving one stable deliberation identity per bridge thread where compression applies. |
| `SPEC-DA-COVERAGE-METRIC` | Run health and inventory tests proving coverage metrics derive from per-file canonical evidence. |
| `SPEC-DA-MECHANICAL-ENFORCE` | Run inventory tests proving inventory remains non-mutating and harvest mutation occurs only through the governed DA writer. |

## Acceptance Criteria

- Backfill, health, harvest, and inventory tools accept only canonical MemBase, Deliberation Archive, and numbered bridge discovery inputs.
- Historical source references remain queryable data but are never opened, imported, copied, or resolved as live paths.
- Dedupe, source taxonomy, relation links, redaction, thread compression, coverage metrics, and non-mutating inventory tests all pass.
- The final implementation diff contains exactly the nine declared paths or a reviewed subset, with both ruff gates and focused pytest green.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/backfill_lo_reports.py`
- `scripts/deliberation_health.py`
- `scripts/harvest_session_deliberations.py`
- `scripts/inventory_lo_bridge_history_backfill.py`
- `platform_tests/unit/test_lo_report_backfill.py`
- `platform_tests/scripts/test_deliberation_archive_spec2098_coverage.py`
- `platform_tests/scripts/test_harvest_session_thread_level.py`
- `platform_tests/scripts/test_harvest_loud_wrap.py`
- `platform_tests/scripts/test_inventory_lo_bridge_history_backfill.py`

## Recommended Commit Type

`feat`
