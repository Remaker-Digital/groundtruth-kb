NEW
::init gtkb lo
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: reasoning_effort=xhigh; thread_source=user
author_metadata_source: x-codex-turn-metadata

# Implementation Proposal - Canonicalize harness-context registries under ops authority

bridge_kind: prime_proposal
Document: gtkb-wi5596-context-registry-canonical-advisory-routes
Version: 001
Date: 2026-07-18 UTC

Project Authorization: PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-WI-5596-CONTEXT-REGISTRY-OPS-2026-07-18
Project Authorization Candidates: [{"project_authorization_id":"PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-WI-5596-CONTEXT-REGISTRY-OPS-2026-07-18","coverage":"exact_singleton","included_work_item_count":1,"specificity_rank":[0,1],"selected":true},{"project_authorization_id":"PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-PROJECT-LEVEL-APPROVAL-STATE-RETIREMENT-2026-06-30","coverage":"project_membership_fallback","included_work_item_count":null,"specificity_rank":[2,0],"selected":false}]
Project: PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE
Work Item: WI-5596

target_paths: ["groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/agent-control/activity-disposition-profiles.toml", "groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/agent-control/system-interface-map.toml"]

implementation_scope: configuration
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Canonicalize the two harness-context registry copies so advisory lookup and output identities refer only to numbered bridge, Deliberation Archive, and MemBase routes while preserving unrelated registry entries and schema. This build session may prepare and file proposal metadata only; a separate future ops activity envelope is mandatory for configuration mutation.

Work item description: Ops activity-envelope child of WI-5582 and scope split from WI-5586. Mutate exactly groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/agent-control/activity-disposition-profiles.toml and groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/agent-control/system-interface-map.toml. Replace unsupported advisory lookup or output identities with canonical numbered bridge, Deliberation Archive, and MemBase identities while preserving unrelated registry entries and schema. Build-envelope implementation, dispatcher configuration/control, TAFE state, runtime state, credentials, deployment, release, push, history rewrite, destructive cleanup, and every other path are excluded.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5596` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/agent-control/activity-disposition-profiles.toml`, `groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/agent-control/system-interface-map.toml`.

## Specification Links

- `DCL-ACTIVITY-DISPOSITION-PROFILE-001` - auto-linked governing or work-item specification.
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
- `ADR-0001` - auto-linked governing or work-item specification.
- `DCL-ADVISORY-ROUTING-001` - auto-linked governing or work-item specification.
- `SPEC-ADVISORY-REPORT-TEMPLATE-001` - auto-linked governing or work-item specification.
- `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001` - auto-linked governing or work-item specification.
- `DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-202666121` - Verdict
- `DELIB-20265490` - LO Review Verdict - WI-4700 Harness Metadata Freshness Guard
- `DELIB-20265869` - Loyal Opposition Review - dispatcher live-state and consistency reconciliation - WI-4768
- `DELIB-202666264` - Loyal Opposition GO Verdict - WI-5257 Compact Live Dispatch Attribution
- `DELIB-202665597` - Loyal Opposition Review — WI-4840 Advisory Disposition Skill Scaffold

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-WI-5596-CONTEXT-REGISTRY-OPS-2026-07-18` - active project authorization covering `WI-5596`.

## Proposed Scope

- In this build session, perform only governed proposal preparation and project or MemBase metadata; do not mutate either TOML target.
- In a separate future ops activity envelope after independent GO, exact claim, and schema-v3 start, replace unsupported advisory lookup or output identities with canonical numbered bridge, Deliberation Archive, and MemBase identities.
- Preserve all unrelated registry entries, identifiers, ordering, schema, and consumer contracts.
- Do not inspect or mutate dispatcher configuration/control, TAFE state, runtime state, source, tests, credentials, deployment, release, Git history, or any path outside the two exact targets.

## Cross-Harness Disposition

- **activity-disposition profiles**: Preserve ordinary, ops, build, and test authority semantics while changing only advisory carrier identities.
- **system interface map**: Keep all harness consumers on the same canonical advisory interfaces without altering dispatcher configuration/control.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5596; PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-WI-5596-CONTEXT-REGISTRY-OPS-2026-07-18; generated by gt bridge file-implementation-proposal",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and the governed bridge proposal generators",
  "primary_route": "gt bridge file-implementation-proposal",
  "before_behavior": "Ops activity-envelope child of WI-5582 and scope split from WI-5586. Mutate exactly groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/agent-control/activity-disposition-profiles.toml and groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/agent-control/system-interface-map.toml. Replace unsupported advisory lookup or output identities with canonical numbered bridge, Deliberation Archive, and MemBase identities while preserving unrelated registry entries and schema. Build-envelope implementation, dispatcher configuration/control, TAFE state, runtime state, credentials, deployment, release, push, history rewrite, destructive cleanup, and every other path are excluded.",
  "after_behavior": "Canonicalize the two harness-context registry copies so advisory lookup and output identities refer only to numbered bridge, Deliberation Archive, and MemBase routes while preserving unrelated registry entries and schema. This build session may prepare and file proposal metadata only; a separate future ops activity envelope is mandatory for configuration mutation.",
  "self_descriptive_naming": "The generated title, work-item id, target paths, scope, and acceptance criteria name the proposed effect.",
  "obsolete_guidance_disposition": "No guidance is retired by proposal filing; implementation must explicitly disposition obsolete guidance.",
  "history_preservation": "The numbered bridge chain remains append-only; rollback never deletes proposal or verdict artifacts.",
  "baseline": {
    "work_item": "WI-5596",
    "project": "PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE",
    "target_paths": [
      "groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/agent-control/activity-disposition-profiles.toml",
      "groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/agent-control/system-interface-map.toml"
    ],
    "linked_specifications": [
      "DCL-ACTIVITY-DISPOSITION-PROFILE-001",
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
      "ADR-0001",
      "DCL-ADVISORY-ROUTING-001",
      "SPEC-ADVISORY-REPORT-TEMPLATE-001",
      "GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001",
      "DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001"
    ]
  },
  "expected_result": {
    "summary": "Canonicalize the two harness-context registry copies so advisory lookup and output identities refer only to numbered bridge, Deliberation Archive, and MemBase routes while preserving unrelated registry entries and schema. This build session may prepare and file proposal metadata only; a separate future ops activity envelope is mandatory for configuration mutation.",
    "scope": [
      "In this build session, perform only governed proposal preparation and project or MemBase metadata; do not mutate either TOML target.",
      "In a separate future ops activity envelope after independent GO, exact claim, and schema-v3 start, replace unsupported advisory lookup or output identities with canonical numbered bridge, Deliberation Archive, and MemBase identities.",
      "Preserve all unrelated registry entries, identifiers, ordering, schema, and consumer contracts.",
      "Do not inspect or mutate dispatcher configuration/control, TAFE state, runtime state, source, tests, credentials, deployment, release, Git history, or any path outside the two exact targets."
    ],
    "acceptance_criteria": [
      "Proposal and metadata activity under build changes no configuration byte.",
      "Future implementation starts only in an ops envelope with current GO, exact claim, schema-v3 authorization, and both targets clean.",
      "Both registries contain only canonical numbered bridge, Deliberation Archive, and MemBase advisory identities for the affected entries.",
      "Unrelated registry entries and TOML schema remain byte-stable or semantically unchanged as explicitly mapped.",
      "Activity-disposition and system-interface-map focused tests pass without dispatcher configuration/control or runtime mutation."
    ]
  },
  "rollback": {
    "instructions": "Revert only the approved configuration targets under separate authority.",
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
| `DCL-ACTIVITY-DISPOSITION-PROFILE-001` | Run platform_tests/scripts/test_activity_disposition_profiles.py and confirm the ops profile retains its authority boundary and canonical dispositions. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run candidate and live bridge applicability preflights; implementation report must record targeted existing-test and deterministic configuration evidence. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must record targeted existing-test and deterministic configuration evidence. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must record targeted existing-test and deterministic configuration evidence. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must record targeted existing-test and deterministic configuration evidence. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must record targeted existing-test and deterministic configuration evidence. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must record targeted existing-test and deterministic configuration evidence. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must record targeted existing-test and deterministic configuration evidence. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must record targeted existing-test and deterministic configuration evidence. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must record targeted existing-test and deterministic configuration evidence. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must record targeted existing-test and deterministic configuration evidence. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must record targeted existing-test and deterministic configuration evidence. |
| `ADR-0001` | Run candidate and live bridge applicability preflights; implementation report must record targeted existing-test and deterministic configuration evidence. |
| `DCL-ADVISORY-ROUTING-001` | Run platform_tests/scripts/test_system_interface_map.py and confirm advisory lookup/output routes use the canonical interface identities. |
| `SPEC-ADVISORY-REPORT-TEMPLATE-001` | Run candidate and live bridge applicability preflights; implementation report must record targeted existing-test and deterministic configuration evidence. |
| `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001` | Run candidate and live bridge applicability preflights; implementation report must record targeted existing-test and deterministic configuration evidence. |
| `DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001` | Run candidate and live bridge applicability preflights; implementation report must record targeted existing-test and deterministic configuration evidence. |

## Acceptance Criteria

- Proposal and metadata activity under build changes no configuration byte.
- Future implementation starts only in an ops envelope with current GO, exact claim, schema-v3 authorization, and both targets clean.
- Both registries contain only canonical numbered bridge, Deliberation Archive, and MemBase advisory identities for the affected entries.
- Unrelated registry entries and TOML schema remain byte-stable or semantically unchanged as explicitly mapped.
- Activity-disposition and system-interface-map focused tests pass without dispatcher configuration/control or runtime mutation.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a separately governed revert of only the two configuration targets. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/agent-control/activity-disposition-profiles.toml`
- `groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/agent-control/system-interface-map.toml`

## Recommended Commit Type

`fix(governance)`
