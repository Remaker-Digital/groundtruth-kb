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

# Implementation Proposal - Restrict migration and rehearsal utilities to canonical inputs

bridge_kind: prime_proposal
Document: gtkb-wi5592-migration-rehearsal-canonical-inputs
Version: 001
Date: 2026-07-18 UTC

Project Authorization: PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-WI-5592-MIGRATION-REHEARSAL-2026-07-18
Project Authorization Candidates: [{"project_authorization_id":"PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-WI-5592-MIGRATION-REHEARSAL-2026-07-18","coverage":"exact_singleton","included_work_item_count":1,"specificity_rank":[0,1],"selected":true},{"project_authorization_id":"PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-PROJECT-LEVEL-APPROVAL-STATE-RETIREMENT-2026-06-30","coverage":"project_membership_fallback","included_work_item_count":null,"specificity_rank":[2,0],"selected":false}]
Project: PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE
Work Item: WI-5592

target_paths: ["scripts/record_core_spec_intake_governance.py", "scripts/migrate_docs_to_kb.py", "scripts/migrate_root_to_gtkb.py", "scripts/rehearse_isolation.py", "scripts/rehearse/_common.py", "platform_tests/scripts/test_rehearse_common_validation.py", "platform_tests/scripts/test_rehearse_db_filter_dryrun.py", "platform_tests/scripts/test_rehearse_isolation.py", "platform_tests/scripts/test_retired_carrier_migration_guards.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Restrict migration and rehearsal utilities to explicit in-root canonical inputs and reject retired or out-of-root live dependencies.

Work item description: Build-only migration and rehearsal slice that removes implicit auxiliary input routes, requires explicit canonical in-root inputs, preserves deny fixtures, and adds focused regression coverage.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5592` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/record_core_spec_intake_governance.py`, `scripts/migrate_docs_to_kb.py`, `scripts/migrate_root_to_gtkb.py`, `scripts/rehearse_isolation.py`, `scripts/rehearse/_common.py`, `platform_tests/scripts/test_rehearse_common_validation.py`, `platform_tests/scripts/test_rehearse_db_filter_dryrun.py`, `platform_tests/scripts/test_rehearse_isolation.py`, `platform_tests/scripts/test_retired_carrier_migration_guards.py`.

## Specification Links

- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps this platform command out of adopter application scope.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge authority and numbered-file filing.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - auto-linked governing or work-item specification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links in implementation proposals.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived verification evidence before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.
- `SPEC-AUQ-POLICY-ENGINE-001` - auto-linked governing or work-item specification.
- `GOV-STANDING-BACKLOG-001` - auto-linked governing or work-item specification.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - auto-linked governing or work-item specification.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - auto-linked governing or work-item specification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - auto-linked governing or work-item specification.
- `DCL-CANONICAL-CARRIER-NONAUTHORITY-001` - auto-linked governing or work-item specification.
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
- `GOV-08` - auto-linked governing or work-item specification.
- `GOV-20` - auto-linked governing or work-item specification.
- `ADR-0001` - auto-linked governing or work-item specification.
- `SPEC-CORE-INTAKE-001` - auto-linked governing or work-item specification.
- `SPEC-CORE-INTAKE-002` - auto-linked governing or work-item specification.
- `ADR-CORE-INTAKE-001` - auto-linked governing or work-item specification.
- `DCL-CORE-INTAKE-001` - auto-linked governing or work-item specification.
- `ADR-APPLICATION-ISOLATION-CONTRACT-001` - auto-linked governing or work-item specification.
- `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` - auto-linked governing or work-item specification.
- `DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001` - auto-linked governing or work-item specification.
- `DCL-APP-ROOT-MINIMIZATION-001` - auto-linked governing or work-item specification.
- `SPEC-DEPLOY-MAINTAIN-ENHANCE-PATH-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-20260717-CANONICAL-ARTIFACT-REFERENCE-BOUNDARY` - owner direction that canonical artifacts depend only on canonical evidence carriers and governed identities.
- `DELIB-0875` - owner approval for persisted, idempotent core specification intake with canonical MemBase completion evidence.
- `DELIB-S325-DB-RECONCILIATION-STRATEGY-CHOICE` - canonical rehearsal database reconciliation strategy used by the retained manifest validation.
- `DELIB-S325-UNCLASSIFIED-DISPOSITION-CHOICE` - canonical disposition choices for unclassified rehearsal rows.
- `DELIB-20260717-DISPATCHER-CONFIGURATION-TROUBLESHOOTER-HOLD` - preserves the independent dispatcher-configuration hold; this source/test proposal neither inspects nor mutates that surface.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-WI-5592-MIGRATION-REHEARSAL-2026-07-18` - active project authorization covering `WI-5592`.

## Proposed Scope

- Remove fixed references, implicit discovery, import, copy, manifest, and source-list behavior for noncanonical auxiliary inputs from the five declared migration and rehearsal utilities.
- Require explicitly bounded in-root canonical inputs for historical migration operations and reject retired, unsupported, or out-of-root live dependencies before side effects.
- Preserve explicit deny and tombstone fixtures as inert regression data and retain idempotence, dry-run, target-root, manifest, database-filter, rollback, and warning semantics.
- Limit implementation to the nine declared targets; configuration, dispatcher control, TAFE/runtime state, credentials, deployment, release, push, history rewrite, destructive cleanup, and every other path are excluded.

## Existing Worktree Ownership

At proposal filing, `platform_tests/scripts/test_rehearse_isolation.py` contains a pre-existing unstaged fixture-only diff not authored by this session. This proposal grants no authority to overwrite or absorb those bytes. Implementation must first establish terminal predecessor ownership or use an independently reviewed hunk-isolation plan that preserves the foreign bytes exactly.

## Cross-Harness Disposition

- **Codex**: Uses the same explicit in-root canonical-input and fail-closed rejection contract.
- **Claude Code**: Uses the same explicit in-root canonical-input and fail-closed rejection contract.
- **Antigravity**: Uses the same explicit in-root canonical-input and fail-closed rejection contract.
- **Cursor**: Uses the same explicit in-root canonical-input and fail-closed rejection contract.
- **Headless and interactive callers**: Receive identical validation, dry-run, and rejection behavior.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5592; PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-WI-5592-MIGRATION-REHEARSAL-2026-07-18; generated by gt bridge file-implementation-proposal",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and the governed bridge proposal generators",
  "primary_route": "gt bridge file-implementation-proposal",
  "before_behavior": "Build activity-envelope child of WI-5582. Mutate exactly scripts/record_core_spec_intake_governance.py, scripts/migrate_docs_to_kb.py, scripts/migrate_root_to_gtkb.py, scripts/rehearse_isolation.py, scripts/rehearse/_common.py, platform_tests/scripts/test_rehearse_common_validation.py, platform_tests/scripts/test_rehearse_db_filter_dryrun.py, platform_tests/scripts/test_rehearse_isolation.py, and platform_tests/scripts/test_retired_carrier_migration_guards.py. Remove fixed references, auto-discovery, import, copy, manifest, or source-list behavior for the owner-retired advisory carrier and eliminate live dependencies outside the mandatory project root. Historical migration commands may accept explicitly bounded canonical inputs but must reject retired-carrier and out-of-root inputs. Preserve explicit deny/tombstone fixtures. Configuration, dispatcher, TAFE, runtime state, credentials, deployment, release, push, history rewrite, destructive cleanup, and all other paths are excluded.",
  "after_behavior": "Restrict migration and rehearsal utilities to explicit in-root canonical inputs and reject retired or out-of-root live dependencies.",
  "self_descriptive_naming": "The generated title, work-item id, target paths, scope, and acceptance criteria name the proposed effect.",
  "obsolete_guidance_disposition": "No guidance is retired by proposal filing; implementation must explicitly disposition obsolete guidance.",
  "history_preservation": "The numbered bridge chain remains append-only; rollback never deletes proposal or verdict artifacts.",
  "baseline": {
    "work_item": "WI-5592",
    "project": "PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE",
    "target_paths": [
      "scripts/record_core_spec_intake_governance.py",
      "scripts/migrate_docs_to_kb.py",
      "scripts/migrate_root_to_gtkb.py",
      "scripts/rehearse_isolation.py",
      "scripts/rehearse/_common.py",
      "platform_tests/scripts/test_rehearse_common_validation.py",
      "platform_tests/scripts/test_rehearse_db_filter_dryrun.py",
      "platform_tests/scripts/test_rehearse_isolation.py",
      "platform_tests/scripts/test_retired_carrier_migration_guards.py"
    ],
    "linked_specifications": [
      "ADR-ISOLATION-APPLICATION-PLACEMENT-001",
      "GOV-FILE-BRIDGE-AUTHORITY-001",
      "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001",
      "DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001",
      "DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001",
      "DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001",
      "SPEC-AUQ-POLICY-ENGINE-001",
      "GOV-STANDING-BACKLOG-001",
      "ADR-CODEX-HOOK-PARITY-FALLBACK-001",
      "ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001",
      "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001",
      "DCL-CANONICAL-CARRIER-NONAUTHORITY-001",
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
      "GOV-08",
      "GOV-20",
      "ADR-0001",
      "SPEC-CORE-INTAKE-001",
      "SPEC-CORE-INTAKE-002",
      "ADR-CORE-INTAKE-001",
      "DCL-CORE-INTAKE-001",
      "ADR-APPLICATION-ISOLATION-CONTRACT-001",
      "GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001",
      "DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001",
      "DCL-APP-ROOT-MINIMIZATION-001",
      "SPEC-DEPLOY-MAINTAIN-ENHANCE-PATH-001"
    ]
  },
  "expected_result": {
    "summary": "Restrict migration and rehearsal utilities to explicit in-root canonical inputs and reject retired or out-of-root live dependencies.",
    "scope": [
      "Remove fixed references, implicit discovery, import, copy, manifest, and source-list behavior for noncanonical auxiliary inputs from the five declared migration and rehearsal utilities.",
      "Require explicitly bounded in-root canonical inputs for historical migration operations and reject retired, unsupported, or out-of-root live dependencies before side effects.",
      "Preserve explicit deny and tombstone fixtures as inert regression data and retain idempotence, dry-run, target-root, manifest, database-filter, rollback, and warning semantics.",
      "Limit implementation to the nine declared targets; configuration, dispatcher control, TAFE/runtime state, credentials, deployment, release, push, history rewrite, destructive cleanup, and every other path are excluded."
    ],
    "acceptance_criteria": [
      "No declared utility contains a default, source list, auto-discovery path, import, or copy route that can consume a noncanonical auxiliary location as live input.",
      "Historical migration commands accept only explicitly bounded canonical in-root inputs and fail closed on retired, unsupported, or out-of-root inputs before mutation.",
      "Core-intake governance recording remains idempotent and cites only canonical source identities; deny and tombstone fixtures remain inert test data.",
      "All four focused test files, ruff check, and ruff format --check pass; final WI-5592 hunks preserve the disclosed foreign rehearsal-test bytes and leave dispatcher configuration untouched."
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
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run rehearsal target-root and manifest tests proving adopter placement remains under the applications namespace while explicitly bounded test sandboxes remain supported. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run both proposal preflights and require the later implementation report to use the governed numbered bridge writer. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Verify migration results, rejected inputs, work-item state, reports, and review outcomes remain durable governed artifacts rather than auxiliary files. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run applicability and ADR/DCL clause preflights against the exact filed proposal with no missing specifications or blocking gaps. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Execute all four focused test files plus ruff check and ruff format --check on all nine declared Python targets and report exact results. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Validate the exact PAUTH, project, work item, inline target_paths, and project bridge-thread link. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Verify migration utilities consume recorded owner decisions but never infer or create owner approval from discovered files. |
| `GOV-STANDING-BACKLOG-001` | Verify WI-5592 remains linked in MemBase through proposal, implementation, report, and terminal verification. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run focused migration and rehearsal tests directly and prove safety does not depend on one harness hook implementation. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Inspect traceability from canonical input identity through migration classification, focused test, implementation report, and independent verdict. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run explicit accepted, rejected, orphaned, unclassified, dry-run, and already-migrated lifecycle cases. |
| `DCL-CANONICAL-CARRIER-NONAUTHORITY-001` | Inspect all five utilities and run negative tests proving auxiliary historical locations are never opened, copied, imported, or treated as live authority. |
| `DCL-SUPERSEDED-SOT-LEAKAGE-001` | Run explicit rejection cases for retired, unsupported, auto-discovered, and out-of-root inputs while preserving deny fixtures as inert test data. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Verify current migration and rehearsal state derives from fresh explicit canonical inputs and records absent or stale evidence as non-passing. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Validate the active exact-singleton WI-5592 authorization before protected edits and bind it into the schema-v3 start packet. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Require independent GO, exact claim, schema-v3 start, and operation-time authorization before any protected mutation. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | Verify the selected PAUTH covers WI-5592, bridge/metadata/source/test classes, and exactly the nine declared targets. |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Revalidate authorization for every protected edit and governed evidence-producing side effect. |
| `DCL-DISPATCHER-ACTIVITY-ENVELOPE-AUTHORITY-001` | Confirm implementation runs only in a build activity envelope and receives no ops or dispatcher-configuration authority. |
| `DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001` | Inspect the final diff to prove no migration utility gains direct dispatcher, TAFE, or harness-complex internal access. |
| `DCL-ACTIVITY-DISPOSITION-PROFILE-001` | Record and validate the source/test-only build disposition at implementation start and operation time. |
| `GOV-WORK-TREE-HYGIENE-001` | Capture pre-edit hashes, preserve the disclosed foreign rehearsal-test bytes, and prove the final WI-5592 hunks are isolated to reviewed ownership. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Run all focused suites and prove idempotence, dry-run, target-root, manifest, warning, and rollback semantics remain intact. |
| `GOV-08` | Run migration tests proving MemBase remains the canonical knowledge destination and only explicitly selected in-root documents are ingested. |
| `GOV-20` | Verify architecture-decision and design-constraint rows are created only from canonical approved inputs with stable IDs and idempotent behavior. |
| `ADR-0001` | Verify MemBase and Deliberation Archive writes remain distinct from operational notes and no auxiliary filesystem report becomes authority. |
| `SPEC-CORE-INTAKE-001` | Run core-intake recording tests proving the persisted missing-core-spec contract remains represented by the canonical requirement row. |
| `SPEC-CORE-INTAKE-002` | Run idempotence and persisted-completion cases proving repeated execution does not create duplicate or inferred completion records. |
| `ADR-CORE-INTAKE-001` | Inspect the core-intake recorder and tests proving completion evidence remains canonical MemBase state rather than a discovered file. |
| `DCL-CORE-INTAKE-001` | Verify the corrected recorder preserves automation-safe, non-interactive, idempotent behavior and does not change scaffold semantics. |
| `ADR-APPLICATION-ISOLATION-CONTRACT-001` | Run rehearsal placement, manifest partition, database filter, and dry-run tests proving platform/application lifecycle isolation remains explicit. |
| `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` | Run positive and negative target-root tests proving named adopter roots remain under the applications namespace and platform paths are refused. |
| `DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001` | Execute the focused structural checks for namespace purity, valid child naming, and refusal of conflated platform surfaces. |
| `DCL-APP-ROOT-MINIMIZATION-001` | Run manifest and database-filter tests proving only classified adopter-owned content is carried forward. |
| `SPEC-DEPLOY-MAINTAIN-ENHANCE-PATH-001` | Run rehearsal dry-run and validation suites proving the corrected canonical-input boundary preserves a usable repeatable maintenance path. |

## Acceptance Criteria

- No declared utility contains a default, source list, auto-discovery path, import, or copy route that can consume a noncanonical auxiliary location as live input.
- Historical migration commands accept only explicitly bounded canonical in-root inputs and fail closed on retired, unsupported, or out-of-root inputs before mutation.
- Core-intake governance recording remains idempotent and cites only canonical source identities; deny and tombstone fixtures remain inert test data.
- All four focused test files, ruff check, and ruff format --check pass; final WI-5592 hunks preserve the disclosed foreign rehearsal-test bytes and leave dispatcher configuration untouched.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/record_core_spec_intake_governance.py`
- `scripts/migrate_docs_to_kb.py`
- `scripts/migrate_root_to_gtkb.py`
- `scripts/rehearse_isolation.py`
- `scripts/rehearse/_common.py`
- `platform_tests/scripts/test_rehearse_common_validation.py`
- `platform_tests/scripts/test_rehearse_db_filter_dryrun.py`
- `platform_tests/scripts/test_rehearse_isolation.py`
- `platform_tests/scripts/test_retired_carrier_migration_guards.py`

## Recommended Commit Type

`feat`
