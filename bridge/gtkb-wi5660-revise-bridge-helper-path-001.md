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

# Implementation Proposal - revise_bridge.py hardcodes stale bridge-propose helper path (should be gtkb-bridge-propose)

bridge_kind: prime_proposal
Document: gtkb-wi5660-revise-bridge-helper-path
Version: 001
Date: 2026-07-24 UTC

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5660-BRIDGE-PROPOSE-HELPER-PATH-20260724
Project Authorization Candidates: [{"project_authorization_id":"PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5660-BRIDGE-PROPOSE-HELPER-PATH-20260724","coverage":"exact_singleton","included_work_item_count":1,"specificity_rank":[0,1],"selected":true}]
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5660

target_paths: [".claude/skills/gtkb-bridge/helpers/revise_bridge.py", "platform_tests/skills/test_bridge_revise_helper.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

File a governed implementation proposal for `WI-5660` using deterministic project, authorization, target-path, and preflight wiring.

Work item description: .claude/skills/gtkb-bridge/helpers/revise_bridge.py line 27 sets BRIDGE_PROPOSE_HELPER = PROJECT_ROOT/.claude/skills/bridge-propose/helpers/write_bridge.py, but the skill dir was renamed to gtkb-bridge-propose. file_revision() therefore raises FileNotFoundError, breaking the governed REVISED-filing path for Prime Builder. Worked around during WI-5659 via an untracked runtime-patch wrapper (.gtkb-state/_wi5659-revised/run_revise.py). Permanent fix: update line 27 to gtkb-bridge-propose (and audit sibling helpers for the same stale reference). Governed source change; needs its own bridge slice. Same rename likely affects any other helper referencing the old bridge-propose path.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5660` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `.claude/skills/gtkb-bridge/helpers/revise_bridge.py`, `platform_tests/skills/test_bridge_revise_helper.py`.

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

- `DELIB-202665676` - Loyal Opposition Verdict -- NO-GO (scope-change revision accepted in principle; implementation still blocked)
- `DELIB-202666962` - Loyal Opposition Corrected Verdict (review_no_action) - GO - WI-5337 Latest NO-GO Draft Claim State
- `DELIB-202666320` - Loyal Opposition Verdict - NO-GO (finalization-scoped) - WI-5113 Suppress Git console windows in VERIFIED finalization
- `DELIB-20263477` - WI-4529 Windows Dispatch Console Window Bridge Gap
- `DELIB-202666063` - Verification Verdict - WI-5107 bridge-helper no-window subprocess (NO-GO)

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5660-BRIDGE-PROPOSE-HELPER-PATH-20260724` - active project authorization covering `WI-5660`.

## Proposed Scope

- Replace the stale pre-rename gtkb-bridge-propose helper path in revise_bridge.py with the canonical prefixed path.
- Audit and cover the helper-path resolution without modifying bridge history or unrelated rename-sweep targets.

## Cross-Harness Disposition

- **codex**: Primary implementation and focused test runner.
- **claude**: No code change; independent Loyal Opposition review required.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5660; PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5660-BRIDGE-PROPOSE-HELPER-PATH-20260724; generated by gt bridge file-implementation-proposal",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and the governed bridge proposal generators",
  "primary_route": "gt bridge file-implementation-proposal",
  "before_behavior": ".claude/skills/gtkb-bridge/helpers/revise_bridge.py line 27 sets BRIDGE_PROPOSE_HELPER = PROJECT_ROOT/.claude/skills/bridge-propose/helpers/write_bridge.py, but the skill dir was renamed to gtkb-bridge-propose. file_revision() therefore raises FileNotFoundError, breaking the governed REVISED-filing path for Prime Builder. Worked around during WI-5659 via an untracked runtime-patch wrapper (.gtkb-state/_wi5659-revised/run_revise.py). Permanent fix: update line 27 to gtkb-bridge-propose (and audit sibling helpers for the same stale reference). Governed source change; needs its own bridge slice. Same rename likely affects any other helper referencing the old bridge-propose path.",
  "after_behavior": "File a governed implementation proposal for `WI-5660` using deterministic project, authorization, target-path, and preflight wiring.",
  "self_descriptive_naming": "The generated title, work-item id, target paths, scope, and acceptance criteria name the proposed effect.",
  "obsolete_guidance_disposition": "No guidance is retired by proposal filing; implementation must explicitly disposition obsolete guidance.",
  "history_preservation": "The numbered bridge chain remains append-only; rollback never deletes proposal or verdict artifacts.",
  "baseline": {
    "work_item": "WI-5660",
    "project": "PROJECT-GTKB-HOUSEKEEPING-HARDENING",
    "target_paths": [
      ".claude/skills/gtkb-bridge/helpers/revise_bridge.py",
      "platform_tests/skills/test_bridge_revise_helper.py"
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
    "summary": "File a governed implementation proposal for `WI-5660` using deterministic project, authorization, target-path, and preflight wiring.",
    "scope": [
      "Replace the stale pre-rename gtkb-bridge-propose helper path in revise_bridge.py with the canonical prefixed path.",
      "Audit and cover the helper-path resolution without modifying bridge history or unrelated rename-sweep targets."
    ],
    "acceptance_criteria": [
      "Governed REVISED filing resolves the canonical helper without FileNotFoundError.",
      "Focused tests pin the canonical prefixed helper path and preserve fail-closed behavior for a missing helper."
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
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run focused bridge-revision helper tests and the applicable proposal preflights. |
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

- Governed REVISED filing resolves the canonical helper without FileNotFoundError.
- Focused tests pin the canonical prefixed helper path and preserve fail-closed behavior for a missing helper.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `.claude/skills/gtkb-bridge/helpers/revise_bridge.py`
- `platform_tests/skills/test_bridge_revise_helper.py`

## Recommended Commit Type

`feat`
