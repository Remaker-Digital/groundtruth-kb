NEW
::init gtkb pb
::open build
author_identity: codex
author_harness_id: A
author_session_context_id: A-2026-07-24T14-14-48Z
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=default; thread_source=codex-desktop
author_metadata_source: x-codex-turn-metadata

# Implementation Proposal - Sweep S3: fix stale skill-rename refs in .claude/rules and config/agent-control mirrors and command-surface.toml

bridge_kind: prime_proposal
Document: gtkb-wi5664-config-baseline-capture
Version: 001
Date: 2026-07-24 UTC

Project Authorization: PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION
Project Authorization Candidates: [{"project_authorization_id":"PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION","coverage":"explicit_list","included_work_item_count":7,"specificity_rank":[1,7],"selected":true}]
Project: GTKB-SKILL-RENAME-REFERENCE-SWEEP
Work Item: WI-5664

target_paths: ["config/agent-control/gtkb-auto-finalization-sweep.md", "config/agent-control/gtkb-review-gate.md", "config/agent-control/gtkb-file-bridge-protocol.md", "config/agent-control/gtkb-loyal-opposition.md", "config/agent-control/gtkb-command-surface.toml"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Establish the missing governed baseline for WI-5664 config/rule inputs before any skill-reference repair is reconsidered.

Work item description: _No work item description supplied._

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5664` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `config/agent-control/gtkb-auto-finalization-sweep.md`, `config/agent-control/gtkb-review-gate.md`, `config/agent-control/gtkb-file-bridge-protocol.md`, `config/agent-control/gtkb-loyal-opposition.md`, `config/agent-control/gtkb-command-surface.toml`.

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

- `DELIB-20265357` - Loyal Opposition Verification Verdict - gtkb-propose-scaffold-invalid-bridge-kind - 022
- `DELIB-20265358` - Loyal Opposition Verification Verdict - gtkb-propose-scaffold-invalid-bridge-kind - 018
- `DELIB-20265424` - Loyal Opposition Verification Verdict - gtkb-propose-scaffold-invalid-bridge-kind - 024
- `DELIB-20265362` - Verdict
- `DELIB-20265355` - Loyal Opposition Review - Environment-Access Escalation - gtkb-propose-scaffold-invalid-bridge-kind - 020

## Owner Decisions / Input

- `PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION` - active project authorization covering `WI-5664`.

## Proposed Scope

- Create a governed, committed baseline for exactly the five currently untracked configuration/rule inputs identified by WI-5664 NO-GO v004; do not change their reference content in this prerequisite slice.
- Record immutable byte hashes and source/projection/package ownership for each input before staging, then verify the committed tree reproduces those hashes.
- Exclude all test additions, projection regeneration, package snapshot rewrites, and skill-reference repairs; those remain in the reissued WI-5664 implementation proposal after baseline capture.

## Cross-Harness Disposition

- **Configuration source/projection/package surfaces**: Capture the existing synchronized baseline only; make no per-harness behavior change.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5664; PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION; generated by gt bridge file-implementation-proposal",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and the governed bridge proposal generators",
  "primary_route": "gt bridge file-implementation-proposal",
  "before_behavior": "WI-5664 has no implemented behavior yet; this proposal defines the slice.",
  "after_behavior": "Establish the missing governed baseline for WI-5664 config/rule inputs before any skill-reference repair is reconsidered.",
  "self_descriptive_naming": "The generated title, work-item id, target paths, scope, and acceptance criteria name the proposed effect.",
  "obsolete_guidance_disposition": "No guidance is retired by proposal filing; implementation must explicitly disposition obsolete guidance.",
  "history_preservation": "The numbered bridge chain remains append-only; rollback never deletes proposal or verdict artifacts.",
  "baseline": {
    "work_item": "WI-5664",
    "project": "GTKB-SKILL-RENAME-REFERENCE-SWEEP",
    "target_paths": [
      "config/agent-control/gtkb-auto-finalization-sweep.md",
      "config/agent-control/gtkb-review-gate.md",
      "config/agent-control/gtkb-file-bridge-protocol.md",
      "config/agent-control/gtkb-loyal-opposition.md",
      "config/agent-control/gtkb-command-surface.toml"
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
    "summary": "Establish the missing governed baseline for WI-5664 config/rule inputs before any skill-reference repair is reconsidered.",
    "scope": [
      "Create a governed, committed baseline for exactly the five currently untracked configuration/rule inputs identified by WI-5664 NO-GO v004; do not change their reference content in this prerequisite slice.",
      "Record immutable byte hashes and source/projection/package ownership for each input before staging, then verify the committed tree reproduces those hashes.",
      "Exclude all test additions, projection regeneration, package snapshot rewrites, and skill-reference repairs; those remain in the reissued WI-5664 implementation proposal after baseline capture."
    ],
    "acceptance_criteria": [
      "Exactly the five declared configuration inputs are introduced in a dedicated governed commit with no unrelated staged paths.",
      "The pre-commit and post-commit SHA-256 value for every captured input is recorded and identical.",
      "generate_rule_compatibility_projections.py --check and the existing targeted projection/command-surface tests pass without regenerating artifacts."
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
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Verify tracked HEAD presence, exact fingerprint preservation, scoped commit diff, and the two existing targeted configuration test modules. |
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

- Exactly the five declared configuration inputs are introduced in a dedicated governed commit with no unrelated staged paths.
- The pre-commit and post-commit SHA-256 value for every captured input is recorded and identical.
- generate_rule_compatibility_projections.py --check and the existing targeted projection/command-surface tests pass without regenerating artifacts.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `config/agent-control/gtkb-auto-finalization-sweep.md`
- `config/agent-control/gtkb-review-gate.md`
- `config/agent-control/gtkb-file-bridge-protocol.md`
- `config/agent-control/gtkb-loyal-opposition.md`
- `config/agent-control/gtkb-command-surface.toml`

## Recommended Commit Type

`feat`
