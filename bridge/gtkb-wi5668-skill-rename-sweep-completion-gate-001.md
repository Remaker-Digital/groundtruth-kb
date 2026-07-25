NEW
::init gtkb lo
::open build
author_identity: codex
author_harness_id: A
author_session_context_id: A-2026-07-24T08-18-23Z
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=default; thread_source=codex-desktop
author_metadata_source: x-codex-turn-metadata

# Implementation Proposal - Sweep completion gate: gt project doctor check for zero remaining pre-rename skill refs

bridge_kind: prime_proposal
Document: gtkb-wi5668-skill-rename-sweep-completion-gate
Version: 001
Date: 2026-07-24 UTC

Project Authorization: PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION
Project Authorization Candidates: [{"project_authorization_id":"PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION","coverage":"explicit_list","included_work_item_count":7,"specificity_rank":[1,7],"selected":true}]
Project: GTKB-SKILL-RENAME-REFERENCE-SWEEP
Work Item: WI-5668

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/tests/test_doctor.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

File a governed implementation proposal for `WI-5668` using deterministic project, authorization, target-path, and preflight wiring.

Work item description: Add a gt project doctor check (_check_skill_rename_reference_sweep_complete) that counts remaining bare pre-rename skill-dir references (bridge, verify, bridge-propose and all renamed skills) across tracked files, EXCLUDING bridge/*.md audit trail, RETIRED-*/BARRED-*/archive historical, .gtkb-state runtime, and the sweep's own tracking artifacts. WARN with an accurate count + sample files while count > 0; PASS at zero. This is the objective completion signal for GTKB-SKILL-RENAME-REFERENCE-SWEEP and a release-gate blocker; a companion DCL assertion can surface it at session start. Makes the program self-driving: incompleteness stays loud until zero. NOT fast-lane (origin=improvement, new mechanism); standard bridge path; requires the project to be authorized (PAUTH) before implementation-start.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5668` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/project/doctor.py`, `groundtruth-kb/tests/test_doctor.py`.

## Specification Links

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

- `DELIB-202667193` - GTKB Skill-Rename Reference Sweep - owner decisions (sequence, scaffold rename, self-driving harness, scoped PAUTH)
- `DELIB-202667105` - Loyal Opposition Review: Canonical Skill Renaming Rollout v003 — GO
- `DELIB-202667099` - LO Review: Governance friction reduction advisory
- `DELIB-20260724-WI5661-PROCESS-AUTHORIZATION` - Process the eight most recent skill-rename work items
- `DELIB-1240` - Bridge thread: gtkb-skill-decision-capture (12 versions, ORPHAN)

## Owner Decisions / Input

- `PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION` - active project authorization covering `WI-5668`.

## Proposed Scope

- Add a project-doctor completion check that detects remaining bare pre-rename skill-directory references only in tracked, non-historical, non-runtime files.
- Report a warning with a stable count and representative samples until the sweep reaches zero, then report pass without weakening existing doctor checks.

## Cross-Harness Disposition

- **codex**: Primary implementation and focused test runner.
- **claude**: No code change; independent Loyal Opposition review required.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5668; PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION; generated by gt bridge file-implementation-proposal",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and the governed bridge proposal generators",
  "primary_route": "gt bridge file-implementation-proposal",
  "before_behavior": "Add a gt project doctor check (_check_skill_rename_reference_sweep_complete) that counts remaining bare pre-rename skill-dir references (bridge, verify, bridge-propose and all renamed skills) across tracked files, EXCLUDING bridge/*.md audit trail, RETIRED-*/BARRED-*/archive historical, .gtkb-state runtime, and the sweep's own tracking artifacts. WARN with an accurate count + sample files while count > 0; PASS at zero. This is the objective completion signal for GTKB-SKILL-RENAME-REFERENCE-SWEEP and a release-gate blocker; a companion DCL assertion can surface it at session start. Makes the program self-driving: incompleteness stays loud until zero. NOT fast-lane (origin=improvement, new mechanism); standard bridge path; requires the project to be authorized (PAUTH) before implementation-start.",
  "after_behavior": "File a governed implementation proposal for `WI-5668` using deterministic project, authorization, target-path, and preflight wiring.",
  "self_descriptive_naming": "The generated title, work-item id, target paths, scope, and acceptance criteria name the proposed effect.",
  "obsolete_guidance_disposition": "No guidance is retired by proposal filing; implementation must explicitly disposition obsolete guidance.",
  "history_preservation": "The numbered bridge chain remains append-only; rollback never deletes proposal or verdict artifacts.",
  "baseline": {
    "work_item": "WI-5668",
    "project": "GTKB-SKILL-RENAME-REFERENCE-SWEEP",
    "target_paths": [
      "groundtruth-kb/src/groundtruth_kb/project/doctor.py",
      "groundtruth-kb/tests/test_doctor.py"
    ],
    "linked_specifications": [
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
      "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001"
    ]
  },
  "expected_result": {
    "summary": "File a governed implementation proposal for `WI-5668` using deterministic project, authorization, target-path, and preflight wiring.",
    "scope": [
      "Add a project-doctor completion check that detects remaining bare pre-rename skill-directory references only in tracked, non-historical, non-runtime files.",
      "Report a warning with a stable count and representative samples until the sweep reaches zero, then report pass without weakening existing doctor checks."
    ],
    "acceptance_criteria": [
      "The check excludes bridge audit history, RETIRED/BARRED/archive trees, runtime state, and its own tracking artifacts.",
      "A focused regression suite proves both warning and pass behavior with deterministic counts and samples."
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
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run focused project-doctor tests covering the completion-gate warning and pass cases. |
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

## Acceptance Criteria

- The check excludes bridge audit history, RETIRED/BARRED/archive trees, runtime state, and its own tracking artifacts.
- A focused regression suite proves both warning and pass behavior with deterministic counts and samples.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/project/doctor.py`
- `groundtruth-kb/tests/test_doctor.py`

## Recommended Commit Type

`feat`
