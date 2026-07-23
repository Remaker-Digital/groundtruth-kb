NEW
::init gtkb lo
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 87ea6b9f-89d5-4e90-a637-a7f9fe8cb561
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive Prime Builder; resolved role prime-builder via ::init gtkb pb

# Implementation Proposal - Protected-commit checker: treat superseded predecessor VERIFIED as non-authoritative history

bridge_kind: prime_proposal
Document: gtkb-wi5657-protected-commit-superseded-verified
Version: 001
Date: 2026-07-23 UTC

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

Teach the protected-commit checker to treat a superseded predecessor VERIFIED (higher-numbered same-slug version staged or in worktree) as non-authoritative history in the candidate collector and finalization-evidence finding. Unblocks WI-5441 Phase 1B finalization and the WI-5113 dirty-finalizer class. Source+test only; safety-preserving.

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
- `GOV-WORK-TREE-HYGIENE-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-202667082` - Loyal Opposition Verification Verdict - NO-GO - WI-5617 Dispatcher Next Foundation Spike
- `DELIB-202666429` - Loyal Opposition Verification Verdict - VERIFIED - WI-5254 PAUTH Amendment Evidence Preflight Stand-Down
- `DELIB-202666934` - Loyal Opposition Corrected Verdict - NO-GO - WI-5269 Activity-Envelope Authority Validators (Predecessor/Dirty-Target Hold Confirmed)
- `DELIB-202666425` - Loyal Opposition Verification Verdict - VERIFIED - WI-5249 Prime NO-ACTION Claim/Filer Stand-Down
- `DELIB-202666421` - Loyal Opposition Disposition Verdict - WI-5240 WI-5236 PAUTH Registered Vocabulary Stand-Down

## Owner Decisions / Input

- `DELIB-202667182` - owner-decision evidence supplied to this command.
- `PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI-5657-PROTECTED-COMMIT-CHECKER-SUPERSEDED-PREDECESSOR-VERIFIED-FIX` - active project authorization covering `WI-5657`.

## Proposed Scope

- Add helper _superseded_versioned_bridge(root, rel_path, snapshot): True when a higher-numbered same-slug version exists (staged in snapshot.selected_paths OR present in worktree bridge/) via VERSIONED_BRIDGE_CAPTURE_RE bridge_id+version, exact-slug matching.
- In _load_transaction_verified_evidence, skip a superseded first-line-VERIFIED staged file from candidates so only the latest-per-chain VERIFIED counts toward the exactly-one-candidate clearance.
- In _verified_bridge_finalization_finding, return None for a superseded VERIFIED so it commits as inert history without a Commit-Finalization-Evidence requirement.
- No change to single-latest-VERIFIED validation: the sole live candidate still gets full manifest/latest-strict-state/independence/evidence-anchor checks; superseded files authorize nothing.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5657; PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI-5657-PROTECTED-COMMIT-CHECKER-SUPERSEDED-PREDECESSOR-VERIFIED-FIX; generated by gt bridge file-implementation-proposal",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and the governed bridge proposal generators",
  "primary_route": "gt bridge file-implementation-proposal",
  "before_behavior": "scripts/check_protected_commit_authorization.py counts a superseded predecessor VERIFIED (a file-only VERIFIED with a higher-numbered version in the same numbered chain) as a live terminal candidate, failing atomic finalization with 'exactly one VERIFIED candidate; found 2' and 'terminal VERIFIED lacks Commit Finalization Evidence'. Fix: treat superseded versioned bridge files as non-authoritative history in both the candidate collector and the finalization-evidence finding. Unblocks WI-5441 Phase 1B finalization and the WI-5113 dirty-finalizer class.",
  "after_behavior": "Teach the protected-commit checker to treat a superseded predecessor VERIFIED (higher-numbered same-slug version staged or in worktree) as non-authoritative history in the candidate collector and finalization-evidence finding. Unblocks WI-5441 Phase 1B finalization and the WI-5113 dirty-finalizer class. Source+test only; safety-preserving.",
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
      "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001",
      "GOV-WORK-TREE-HYGIENE-001"
    ]
  },
  "expected_result": {
    "summary": "Teach the protected-commit checker to treat a superseded predecessor VERIFIED (higher-numbered same-slug version staged or in worktree) as non-authoritative history in the candidate collector and finalization-evidence finding. Unblocks WI-5441 Phase 1B finalization and the WI-5113 dirty-finalizer class. Source+test only; safety-preserving.",
    "scope": [
      "Add helper _superseded_versioned_bridge(root, rel_path, snapshot): True when a higher-numbered same-slug version exists (staged in snapshot.selected_paths OR present in worktree bridge/) via VERSIONED_BRIDGE_CAPTURE_RE bridge_id+version, exact-slug matching.",
      "In _load_transaction_verified_evidence, skip a superseded first-line-VERIFIED staged file from candidates so only the latest-per-chain VERIFIED counts toward the exactly-one-candidate clearance.",
      "In _verified_bridge_finalization_finding, return None for a superseded VERIFIED so it commits as inert history without a Commit-Finalization-Evidence requirement.",
      "No change to single-latest-VERIFIED validation: the sole live candidate still gets full manifest/latest-strict-state/independence/evidence-anchor checks; superseded files authorize nothing."
    ],
    "acceptance_criteria": [
      "Superseded VERIFIED (-004) plus single latest VERIFIED (-007) passes clearance with the latest as sole candidate.",
      "Superseded VERIFIED yields no finalization-evidence finding; a non-superseded terminal VERIFIED lacking evidence still yields it.",
      "Only-VERIFIED-is-superseded (latest NO-GO) yields zero live candidates and no authorization (fails closed).",
      "Exact-slug matching: a prefix-sharing slug is not a sibling.",
      "Existing checker test suite continues to pass (no regression)."
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
| `GOV-FILE-BRIDGE-AUTHORITY-001` | New tests in platform_tests/scripts/test_check_protected_commit_authorization.py assert superseded predecessor VERIFIED is excluded from candidacy and finalization-evidence findings; full existing suite re-run for no regression. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Spec-derived tests map candidate exclusion, finding suppression, fail-closed on zero live candidates, and exact-slug matching to explicit pytest assertions. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-WORK-TREE-HYGIENE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |

## Acceptance Criteria

- Superseded VERIFIED (-004) plus single latest VERIFIED (-007) passes clearance with the latest as sole candidate.
- Superseded VERIFIED yields no finalization-evidence finding; a non-superseded terminal VERIFIED lacking evidence still yields it.
- Only-VERIFIED-is-superseded (latest NO-GO) yields zero live candidates and no authorization (fails closed).
- Exact-slug matching: a prefix-sharing slug is not a sibling.
- Existing checker test suite continues to pass (no regression).

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/check_protected_commit_authorization.py`
- `platform_tests/scripts/test_check_protected_commit_authorization.py`

## Recommended Commit Type

`feat`
