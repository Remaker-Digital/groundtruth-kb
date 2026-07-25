NEW
::init gtkb pb
::open build
author_identity: codex
author_harness_id: A
author_session_context_id: A-2026-07-24T14-31-49Z
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=default; thread_source=codex-desktop
author_metadata_source: x-codex-turn-metadata

# Implementation Proposal - Protected-commit checker: treat superseded predecessor VERIFIED as non-authoritative history

bridge_kind: prime_proposal
Document: gtkb-wi5657-terminal-finalization-recovery
Version: 001
Date: 2026-07-24 UTC

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI-5657-PROTECTED-COMMIT-CHECKER-SUPERSEDED-PREDECESSOR-VERIFIED-FIX
Project Authorization Candidates: [{"project_authorization_id":"PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI-5657-PROTECTED-COMMIT-CHECKER-SUPERSEDED-PREDECESSOR-VERIFIED-FIX","coverage":"exact_singleton","included_work_item_count":1,"specificity_rank":[0,1],"selected":true}]
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5657

target_paths: ["scripts/check_protected_commit_authorization.py", "platform_tests/scripts/test_check_protected_commit_authorization.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Recover terminal verification for committed WI-5657 through the canonical finalizer, never a file-only verdict.

Work item description: scripts/check_protected_commit_authorization.py counts a superseded predecessor VERIFIED (a file-only VERIFIED with a higher-numbered version in the same numbered chain) as a live terminal candidate, failing atomic finalization with 'exactly one VERIFIED candidate; found 2' and 'terminal VERIFIED lacks Commit Finalization Evidence'. Fix: treat superseded versioned bridge files as non-authoritative history in both the candidate collector and the finalization-evidence finding. Unblocks WI-5441 Phase 1B finalization and the WI-5113 dirty-finalizer class.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5657` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/check_protected_commit_authorization.py`, `platform_tests/scripts/test_check_protected_commit_authorization.py`.

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

- `DELIB-202666934` - Loyal Opposition Corrected Verdict - NO-GO - WI-5269 Activity-Envelope Authority Validators (Predecessor/Dirty-Target Hold Confirmed)
- `DELIB-202667082` - Loyal Opposition Verification Verdict - NO-GO - WI-5617 Dispatcher Next Foundation Spike
- `DELIB-202666429` - Loyal Opposition Verification Verdict - VERIFIED - WI-5254 PAUTH Amendment Evidence Preflight Stand-Down
- `DELIB-202666425` - Loyal Opposition Verification Verdict - VERIFIED - WI-5249 Prime NO-ACTION Claim/Filer Stand-Down
- `DELIB-202666421` - Loyal Opposition Disposition Verdict - WI-5240 WI-5236 PAUTH Registered Vocabulary Stand-Down

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI-5657-PROTECTED-COMMIT-CHECKER-SUPERSEDED-PREDECESSOR-VERIFIED-FIX` - active project authorization covering `WI-5657`.

## Proposed Scope

- Preserve the committed WI-5657 implementation at 7b838d9e7606a8b1f8be75ade78881f63beda170 and the committed 001-004 audit chain; do not modify or restage source/test paths.
- Revalidate the WI-5657 focused behavior, then exercise only the canonical helper-mediated terminal finalization path after the checker control-plane recovery is independently accepted.
- If the helper requires an owner-approved by-reference waiver for the already-committed source/test claim, fail closed and route that exact waiver question; never create a file-only VERIFIED verdict.

## Cross-Harness Disposition

- **Protected-commit checker**: No new behavior change; recover only the governed terminal lifecycle for the committed implementation.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5657; PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI-5657-PROTECTED-COMMIT-CHECKER-SUPERSEDED-PREDECESSOR-VERIFIED-FIX; generated by gt bridge file-implementation-proposal",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and the governed bridge proposal generators",
  "primary_route": "gt bridge file-implementation-proposal",
  "before_behavior": "scripts/check_protected_commit_authorization.py counts a superseded predecessor VERIFIED (a file-only VERIFIED with a higher-numbered version in the same numbered chain) as a live terminal candidate, failing atomic finalization with 'exactly one VERIFIED candidate; found 2' and 'terminal VERIFIED lacks Commit Finalization Evidence'. Fix: treat superseded versioned bridge files as non-authoritative history in both the candidate collector and the finalization-evidence finding. Unblocks WI-5441 Phase 1B finalization and the WI-5113 dirty-finalizer class.",
  "after_behavior": "Recover terminal verification for committed WI-5657 through the canonical finalizer, never a file-only verdict.",
  "self_descriptive_naming": "The generated title, work-item id, target paths, scope, and acceptance criteria name the proposed effect.",
  "obsolete_guidance_disposition": "No guidance is retired by proposal filing; implementation must explicitly disposition obsolete guidance.",
  "history_preservation": "The numbered bridge chain remains append-only; rollback never deletes proposal or verdict artifacts.",
  "baseline": {
    "work_item": "WI-5657",
    "project": "PROJECT-GTKB-HOUSEKEEPING-HARDENING",
    "target_paths": [
      "scripts/check_protected_commit_authorization.py",
      "platform_tests/scripts/test_check_protected_commit_authorization.py"
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
    "summary": "Recover terminal verification for committed WI-5657 through the canonical finalizer, never a file-only verdict.",
    "scope": [
      "Preserve the committed WI-5657 implementation at 7b838d9e7606a8b1f8be75ade78881f63beda170 and the committed 001-004 audit chain; do not modify or restage source/test paths.",
      "Revalidate the WI-5657 focused behavior, then exercise only the canonical helper-mediated terminal finalization path after the checker control-plane recovery is independently accepted.",
      "If the helper requires an owner-approved by-reference waiver for the already-committed source/test claim, fail closed and route that exact waiver question; never create a file-only VERIFIED verdict."
    ],
    "acceptance_criteria": [
      "Current WI-5657 focused tests and quality checks pass against HEAD and the implementation commit has the exact two declared source/test paths plus its recorded audit chain.",
      "Any terminal verdict is created through --finalize-verified and has complete commit-finalization evidence; otherwise the recovery remains non-terminal.",
      "No later WI-5658/WI-5659 source hunks are attributed to WI-5657."
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
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run the WI-5657 focused selectors and the canonical finalizer only on its governed bridge-audit transaction after independent LO review. |
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

- Current WI-5657 focused tests and quality checks pass against HEAD and the implementation commit has the exact two declared source/test paths plus its recorded audit chain.
- Any terminal verdict is created through --finalize-verified and has complete commit-finalization evidence; otherwise the recovery remains non-terminal.
- No later WI-5658/WI-5659 source hunks are attributed to WI-5657.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/check_protected_commit_authorization.py`
- `platform_tests/scripts/test_check_protected_commit_authorization.py`

## Recommended Commit Type

`feat`
