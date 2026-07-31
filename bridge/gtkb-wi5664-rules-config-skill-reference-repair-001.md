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

# Implementation Proposal - Sweep S3: fix stale skill-rename refs in .claude/rules and config/agent-control mirrors and command-surface.toml

bridge_kind: prime_proposal
Document: gtkb-wi5664-rules-config-skill-reference-repair
Version: 001
Date: 2026-07-24 UTC

Project Authorization: PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION
Project Authorization Candidates: [{"project_authorization_id":"PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION","coverage":"explicit_list","included_work_item_count":7,"specificity_rank":[1,7],"selected":true}]
Project: GTKB-SKILL-RENAME-REFERENCE-SWEEP
Work Item: WI-5664

target_paths: ["groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/agent-control/command-surface.toml", "config/agent-control/gtkb-auto-finalization-sweep.md", "config/agent-control/CONTROL-MAP.md", "config/agent-control/command-surface.toml", "config/agent-control/gtkb-command-surface.toml", "config/agent-control/gtkb-control-map.md", ".claude/rules/auto-finalization-sweep.md", "config/agent-control/gtkb-file-bridge-protocol.md", ".claude/rules/codex-session-bootstrap.md", ".claude/rules/codex-review-gate.md", ".claude/rules/codex-knowledge-base-index.md", ".claude/rules/file-bridge-protocol.md", "config/agent-control/gtkb-knowledge-base-index.md", "config/agent-control/gtkb-loyal-opposition.md", "config/agent-control/gtkb-review-gate.md", "config/agent-control/gtkb-session-bootstrap.md", "config/agent-control/gtkb-session-startup-control-map.md", "config/agent-control/gtkb-role-capability-manifest.md", ".claude/rules/loyal-opposition.md", "config/agent-control/ROLE-CAPABILITY-MANIFEST.md", "config/agent-control/SESSION-STARTUP-CONTROL-MAP.md"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

File a governed implementation proposal for `WI-5664` using deterministic project, authorization, target-path, and preflight wiring.

Work item description: _No work item description supplied._

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5664` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/agent-control/command-surface.toml`, `config/agent-control/gtkb-auto-finalization-sweep.md`, `config/agent-control/CONTROL-MAP.md`, `config/agent-control/command-surface.toml`, `config/agent-control/gtkb-command-surface.toml`, `config/agent-control/gtkb-control-map.md`, `.claude/rules/auto-finalization-sweep.md`, `config/agent-control/gtkb-file-bridge-protocol.md`, `.claude/rules/codex-session-bootstrap.md`, `.claude/rules/codex-review-gate.md`, `.claude/rules/codex-knowledge-base-index.md`, `.claude/rules/file-bridge-protocol.md`, `config/agent-control/gtkb-knowledge-base-index.md`, `config/agent-control/gtkb-loyal-opposition.md`, `config/agent-control/gtkb-review-gate.md`, `config/agent-control/gtkb-session-bootstrap.md`, `config/agent-control/gtkb-session-startup-control-map.md`, `config/agent-control/gtkb-role-capability-manifest.md`, `.claude/rules/loyal-opposition.md`, `config/agent-control/ROLE-CAPABILITY-MANIFEST.md`, `config/agent-control/SESSION-STARTUP-CONTROL-MAP.md`.

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
- `DELIB-20265355` - Loyal Opposition Review - Environment-Access Escalation - gtkb-propose-scaffold-invalid-bridge-kind - 020
- `DELIB-20265364` - Verdict

## Owner Decisions / Input

- `PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION` - active project authorization covering `WI-5664`.

## Proposed Scope

- Replace bare pre-rename skill-directory references in the declared rules, control-surface mirrors, and canonical command-surface registry projection.
- Preserve source-of-record and generated-mirror roles; do not change bridge lifecycle behavior, policy meaning, or unrelated configuration.

## Cross-Harness Disposition

- **codex**: Primary implementation and focused validation runner.
- **claude**: No code change; independent Loyal Opposition review required.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5664; PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION; generated by gt bridge file-implementation-proposal",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and the governed bridge proposal generators",
  "primary_route": "gt bridge file-implementation-proposal",
  "before_behavior": "WI-5664 has no implemented behavior yet; this proposal defines the slice.",
  "after_behavior": "File a governed implementation proposal for `WI-5664` using deterministic project, authorization, target-path, and preflight wiring.",
  "self_descriptive_naming": "The generated title, work-item id, target paths, scope, and acceptance criteria name the proposed effect.",
  "obsolete_guidance_disposition": "No guidance is retired by proposal filing; implementation must explicitly disposition obsolete guidance.",
  "history_preservation": "The numbered bridge chain remains append-only; rollback never deletes proposal or verdict artifacts.",
  "baseline": {
    "work_item": "WI-5664",
    "project": "GTKB-SKILL-RENAME-REFERENCE-SWEEP",
    "target_paths": [
      "groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/agent-control/command-surface.toml",
      "config/agent-control/gtkb-auto-finalization-sweep.md",
      "config/agent-control/CONTROL-MAP.md",
      "config/agent-control/command-surface.toml",
      "config/agent-control/gtkb-command-surface.toml",
      "config/agent-control/gtkb-control-map.md",
      ".claude/rules/auto-finalization-sweep.md",
      "config/agent-control/gtkb-file-bridge-protocol.md",
      ".claude/rules/codex-session-bootstrap.md",
      ".claude/rules/codex-review-gate.md",
      ".claude/rules/codex-knowledge-base-index.md",
      ".claude/rules/file-bridge-protocol.md",
      "config/agent-control/gtkb-knowledge-base-index.md",
      "config/agent-control/gtkb-loyal-opposition.md",
      "config/agent-control/gtkb-review-gate.md",
      "config/agent-control/gtkb-session-bootstrap.md",
      "config/agent-control/gtkb-session-startup-control-map.md",
      "config/agent-control/gtkb-role-capability-manifest.md",
      ".claude/rules/loyal-opposition.md",
      "config/agent-control/ROLE-CAPABILITY-MANIFEST.md",
      "config/agent-control/SESSION-STARTUP-CONTROL-MAP.md"
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
    "summary": "File a governed implementation proposal for `WI-5664` using deterministic project, authorization, target-path, and preflight wiring.",
    "scope": [
      "Replace bare pre-rename skill-directory references in the declared rules, control-surface mirrors, and canonical command-surface registry projection.",
      "Preserve source-of-record and generated-mirror roles; do not change bridge lifecycle behavior, policy meaning, or unrelated configuration."
    ],
    "acceptance_criteria": [
      "Every declared rules/config reference names the gtkb-prefixed canonical skill directory.",
      "The command-surface source and registry projection remain semantically aligned after the path correction."
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
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run the focused configuration/reference migration checks and command-surface parity validation. |
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

- Every declared rules/config reference names the gtkb-prefixed canonical skill directory.
- The command-surface source and registry projection remain semantically aligned after the path correction.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/agent-control/command-surface.toml`
- `config/agent-control/gtkb-auto-finalization-sweep.md`
- `config/agent-control/CONTROL-MAP.md`
- `config/agent-control/command-surface.toml`
- `config/agent-control/gtkb-command-surface.toml`
- `config/agent-control/gtkb-control-map.md`
- `.claude/rules/auto-finalization-sweep.md`
- `config/agent-control/gtkb-file-bridge-protocol.md`
- `.claude/rules/codex-session-bootstrap.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/codex-knowledge-base-index.md`
- `.claude/rules/file-bridge-protocol.md`
- `config/agent-control/gtkb-knowledge-base-index.md`
- `config/agent-control/gtkb-loyal-opposition.md`
- `config/agent-control/gtkb-review-gate.md`
- `config/agent-control/gtkb-session-bootstrap.md`
- `config/agent-control/gtkb-session-startup-control-map.md`
- `config/agent-control/gtkb-role-capability-manifest.md`
- `.claude/rules/loyal-opposition.md`
- `config/agent-control/ROLE-CAPABILITY-MANIFEST.md`
- `config/agent-control/SESSION-STARTUP-CONTROL-MAP.md`

## Recommended Commit Type

`feat`
