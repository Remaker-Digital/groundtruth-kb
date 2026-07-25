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

# Implementation Proposal - Sweep S1: fix stale skill-rename refs in canonical SKILL.md docs and helper docstrings/hints

bridge_kind: prime_proposal
Document: gtkb-wi5662-canonical-skill-reference-repair
Version: 001
Date: 2026-07-24 UTC

Project Authorization: PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION
Project Authorization Candidates: [{"project_authorization_id":"PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION","coverage":"explicit_list","included_work_item_count":7,"specificity_rank":[1,7],"selected":true}]
Project: GTKB-SKILL-RENAME-REFERENCE-SWEEP
Work Item: WI-5662

target_paths: [".claude/skills/gtkb-advisory-disposition/SKILL.md", ".claude/skills/gtkb-advisory-proposal/SKILL.md", ".claude/skills/gtkb-advisory-intake/SKILL.md", ".claude/skills/gtkb-bridge/SKILL.md", ".claude/skills/gtkb-managed-skill-adoption-review/SKILL.md", ".claude/skills/gtkb-lo-hygiene-assessment/SKILL.md", ".claude/skills/gtkb-harness-parity-review/SKILL.md", ".claude/skills/gtkb-skill-governance-lifecycle/SKILL.md", ".claude/skills/gtkb-proposal-review/SKILL.md", ".claude/skills/gtkb-skill-rollout/SKILL.md", ".claude/skills/gtkb-query/SKILL.md", ".claude/skills/gtkb-verify/SKILL.md", ".claude/skills/gtkb-bridge/helpers/scan_bridge.py", ".claude/skills/gtkb-bridge/helpers/show_thread_bridge.py", ".claude/skills/gtkb-verify/helpers/write_verdict.py", "scripts/session_self_initialization.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

File a governed implementation proposal for `WI-5662` using deterministic project, authorization, target-path, and preflight wiring.

Work item description: _No work item description supplied._

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5662` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `.claude/skills/gtkb-advisory-disposition/SKILL.md`, `.claude/skills/gtkb-advisory-proposal/SKILL.md`, `.claude/skills/gtkb-advisory-intake/SKILL.md`, `.claude/skills/gtkb-bridge/SKILL.md`, `.claude/skills/gtkb-managed-skill-adoption-review/SKILL.md`, `.claude/skills/gtkb-lo-hygiene-assessment/SKILL.md`, `.claude/skills/gtkb-harness-parity-review/SKILL.md`, `.claude/skills/gtkb-skill-governance-lifecycle/SKILL.md`, `.claude/skills/gtkb-proposal-review/SKILL.md`, `.claude/skills/gtkb-skill-rollout/SKILL.md`, `.claude/skills/gtkb-query/SKILL.md`, `.claude/skills/gtkb-verify/SKILL.md`, `.claude/skills/gtkb-bridge/helpers/scan_bridge.py`, `.claude/skills/gtkb-bridge/helpers/show_thread_bridge.py`, `.claude/skills/gtkb-verify/helpers/write_verdict.py`, `scripts/session_self_initialization.py`.

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

- `DELIB-20260724-WI5661-PROCESS-AUTHORIZATION` - Process the eight most recent skill-rename work items
- `DELIB-202667193` - GTKB Skill-Rename Reference Sweep - owner decisions (sequence, scaffold rename, self-driving harness, scoped PAUTH)
- `DELIB-202667099` - LO Review: Governance friction reduction advisory
- `DELIB-202667093` - LO Verification: GFR Slice D — Drift & generator hygiene
- `DELIB-202667105` - Loyal Opposition Review: Canonical Skill Renaming Rollout v003 — GO

## Owner Decisions / Input

- `PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION` - active project authorization covering `WI-5662`.

## Proposed Scope

- Replace bare pre-rename skill-directory references in the canonical SKILL.md documents and named helper/docstring surfaces with their gtkb-prefixed canonical paths.
- Keep generated adapters, rules/config mirrors, tests, docs outside canonical skills, and scaffold/template rename work in their dedicated successor slices.

## Cross-Harness Disposition

- **codex**: Primary implementation and focused validation runner.
- **claude**: No code change; independent Loyal Opposition review required.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5662; PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION; generated by gt bridge file-implementation-proposal",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and the governed bridge proposal generators",
  "primary_route": "gt bridge file-implementation-proposal",
  "before_behavior": "WI-5662 has no implemented behavior yet; this proposal defines the slice.",
  "after_behavior": "File a governed implementation proposal for `WI-5662` using deterministic project, authorization, target-path, and preflight wiring.",
  "self_descriptive_naming": "The generated title, work-item id, target paths, scope, and acceptance criteria name the proposed effect.",
  "obsolete_guidance_disposition": "No guidance is retired by proposal filing; implementation must explicitly disposition obsolete guidance.",
  "history_preservation": "The numbered bridge chain remains append-only; rollback never deletes proposal or verdict artifacts.",
  "baseline": {
    "work_item": "WI-5662",
    "project": "GTKB-SKILL-RENAME-REFERENCE-SWEEP",
    "target_paths": [
      ".claude/skills/gtkb-advisory-disposition/SKILL.md",
      ".claude/skills/gtkb-advisory-proposal/SKILL.md",
      ".claude/skills/gtkb-advisory-intake/SKILL.md",
      ".claude/skills/gtkb-bridge/SKILL.md",
      ".claude/skills/gtkb-managed-skill-adoption-review/SKILL.md",
      ".claude/skills/gtkb-lo-hygiene-assessment/SKILL.md",
      ".claude/skills/gtkb-harness-parity-review/SKILL.md",
      ".claude/skills/gtkb-skill-governance-lifecycle/SKILL.md",
      ".claude/skills/gtkb-proposal-review/SKILL.md",
      ".claude/skills/gtkb-skill-rollout/SKILL.md",
      ".claude/skills/gtkb-query/SKILL.md",
      ".claude/skills/gtkb-verify/SKILL.md",
      ".claude/skills/gtkb-bridge/helpers/scan_bridge.py",
      ".claude/skills/gtkb-bridge/helpers/show_thread_bridge.py",
      ".claude/skills/gtkb-verify/helpers/write_verdict.py",
      "scripts/session_self_initialization.py"
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
    "summary": "File a governed implementation proposal for `WI-5662` using deterministic project, authorization, target-path, and preflight wiring.",
    "scope": [
      "Replace bare pre-rename skill-directory references in the canonical SKILL.md documents and named helper/docstring surfaces with their gtkb-prefixed canonical paths.",
      "Keep generated adapters, rules/config mirrors, tests, docs outside canonical skills, and scaffold/template rename work in their dedicated successor slices."
    ],
    "acceptance_criteria": [
      "Every declared canonical source resolves only the gtkb-prefixed skill directories and retains documented helper behavior.",
      "The adapter-regeneration slice can consume the corrected canonical sources without reintroducing bare references."
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
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run the focused canonical-skill reference checks and the adapter-generation check in dry-run mode. |
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

- Every declared canonical source resolves only the gtkb-prefixed skill directories and retains documented helper behavior.
- The adapter-regeneration slice can consume the corrected canonical sources without reintroducing bare references.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `.claude/skills/gtkb-advisory-disposition/SKILL.md`
- `.claude/skills/gtkb-advisory-proposal/SKILL.md`
- `.claude/skills/gtkb-advisory-intake/SKILL.md`
- `.claude/skills/gtkb-bridge/SKILL.md`
- `.claude/skills/gtkb-managed-skill-adoption-review/SKILL.md`
- `.claude/skills/gtkb-lo-hygiene-assessment/SKILL.md`
- `.claude/skills/gtkb-harness-parity-review/SKILL.md`
- `.claude/skills/gtkb-skill-governance-lifecycle/SKILL.md`
- `.claude/skills/gtkb-proposal-review/SKILL.md`
- `.claude/skills/gtkb-skill-rollout/SKILL.md`
- `.claude/skills/gtkb-query/SKILL.md`
- `.claude/skills/gtkb-verify/SKILL.md`
- `.claude/skills/gtkb-bridge/helpers/scan_bridge.py`
- `.claude/skills/gtkb-bridge/helpers/show_thread_bridge.py`
- `.claude/skills/gtkb-verify/helpers/write_verdict.py`
- `scripts/session_self_initialization.py`

## Recommended Commit Type

`feat`
