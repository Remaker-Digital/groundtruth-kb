NEW

# WI-5412: Restore the missing gap-state capture source residue

bridge_kind: prime_proposal
Document: gtkb-wi5412-gap-state-capture-source-residue
Version: 001
Author: Prime Builder (Codex A)
Date: 2026-07-17 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: codex-desktop-019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: interactive desktop Prime Builder A

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5412

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli_deliberations_record.py", "groundtruth-kb/src/groundtruth_kb/governance/approval_packet.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Adopt only the current two-file gap-state capture hunks omitted when WI-3378
was marked resolved. The committed tests already require formal-artifact
capture to bind a gap-state bridge id, reason, and intended canonical database
operation into the approval packet. HEAD lacks that source behavior. The
candidate adds default-preserving request fields, conditional packet metadata,
and fail-closed validation while leaving ordinary deliberation recording
unchanged; all 32 focused approval-packet, deliberation-record, and spec-record
tests pass.

This is hunk-scoped residue closure inside two already tracked files. It does
not create a formal artifact, execute a database operation, alter bridge state,
touch dispatcher/TAFE/harness state, or perform any Git operation. Independent
review must bind the exact diff hashes so a later mechanical finalizer cannot
absorb neighboring work.

## Specification Links

- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — requires explicit lifecycle states and applicable approval evidence when formal capture proceeds through a gap state.
- `GOV-ARTIFACT-APPROVAL-001` — requires formal-artifact writes to remain bound to complete owner approval evidence.
- `GOV-SPEC-CAPTURE-TRANSPARENCY-001` — requires capture decisions and full approval context to remain visible rather than being inferred from an unbound fallback.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` — requires ordinary recording behavior to remain unchanged and missing gap-state evidence to fail closed.
- `GOV-WORK-TREE-HYGIENE-001` — requires exact ownership and governed finalization of the two dirty source hunks without absorbing foreign dirt.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — requires independent GO before protected source adoption and independent verification afterward.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — binds the exact source residue to all governing requirements and focused tests.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — binds WI-5412 to its active tree-stabilization authorization.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — requires every cited requirement to be independently tested before VERIFIED.

## Prior Deliberations

- `INTAKE-5d260fb0` — Intake: Bridge protocol represents worker incapability as a first-class in-protocol state

That intake establishes that a workflow gap is represented explicitly inside
the governed protocol rather than hidden or worked around. WI-5412 carries the
same principle into formal-artifact capture by binding the exact bridge gap and
intended canonical operation into owner-visible approval evidence; it does not
change bridge state semantics.

## Owner Decisions / Input

The owner authorized the full modernization program at the project level and
directed every discovered flaw or omission to become an `origin=hygiene` work
item while work continues. Active authorization
`PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE` covers source,
test, metadata, and governance evidence while retaining independent GO,
claim/start, VERIFIED, and mechanical Git gates. No additional owner decision
is required for this proposal or its independently GO-approved hunk adoption.

## Requirement Sufficiency

Existing requirements sufficient. The artifact-lifecycle, approval,
transparency, non-impairment, worktree-hygiene, bridge, and project-linkage
requirements fully define the behavior and transaction. No requirement change
is proposed.

## Spec-Derived Verification Plan

`DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `GOV-ARTIFACT-APPROVAL-001`, and
`GOV-SPEC-CAPTURE-TRANSPARENCY-001` map to the approval-packet and record-command
tests. Expected result: gap-state capture includes bridge id, reason, and
intended operation; missing evidence fails; ordinary capture remains valid.

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/groundtruth_kb/governance/test_approval_packet.py platform_tests/groundtruth_kb/cli/test_deliberations_record.py platform_tests/groundtruth_kb/cli/test_spec_record.py -q --tb=short
```

`GOV-WORK-TREE-HYGIENE-001` maps to exact hunk and source hygiene. Expected
result: only the reviewed gap-state additions appear in the two target diffs,
with clean lint, format, and whitespace checks.

```text
groundtruth-kb/.venv/Scripts/ruff.exe check groundtruth-kb/src/groundtruth_kb/cli_deliberations_record.py groundtruth-kb/src/groundtruth_kb/governance/approval_packet.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check groundtruth-kb/src/groundtruth_kb/cli_deliberations_record.py groundtruth-kb/src/groundtruth_kb/governance/approval_packet.py
git diff --check -- groundtruth-kb/src/groundtruth_kb/cli_deliberations_record.py groundtruth-kb/src/groundtruth_kb/governance/approval_packet.py
```

`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` maps to independent LO review
of normalized exact diff hashes and all commands above. Expected result: the
next terminal verdict is `VERIFIED` only when candidate hunks and evidence
match.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5412 recovering falsely closed WI-3378 source residue under the modernization worktree-finalization contract",
  "canonical_authority": "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 and GOV-ARTIFACT-APPROVAL-001",
  "primary_route": "gt deliberations record with conditional gap-state capture fields and canonical approval-packet validation",
  "before_behavior": "committed tests describe gap-state approval evidence but HEAD source cannot bind a bridge gap or intended database operation",
  "after_behavior": "gap-state capture is explicit, owner-visible, operation-bound, and fail-closed while ordinary deliberation capture remains unchanged",
  "self_descriptive_naming": "gap_state_capture, gap_state_bridge_id, gap_state_reason, capture_context, and intended_db_operation state their evidence semantics",
  "obsolete_guidance_disposition": "no guidance is changed; the falsely closed source-absent state is superseded by exact reviewed hunks",
  "history_preservation": "WI-3378 and existing commits remain unchanged while WI-5412 records the physical residue append-only",
  "baseline": {
    "target_files_dirty": 2,
    "head_gap_state_source_present": false,
    "focused_tests": "32 passed in 6.54 seconds"
  },
  "expected_result": {
    "ordinary_capture_regression": "unchanged and passing",
    "gap_state_capture": "approval packet binds bridge id, reason, and intended operation",
    "foreign_hunks_changed": 0
  },
  "rollback": {
    "instructions": "under separate authority, revert only the later focused hunk commit without amending history",
    "test": "rerun the 32 focused tests and exact two-file diff inspection"
  },
  "hard_invariants": [
    "formal capture still requires owner-presented AUQ evidence and canonical packet validation",
    "gap-state mode fails closed without bridge id, reason, or intended operation method",
    "no formal artifact, database row, bridge state, dispatcher, TAFE, harness, credential, deployment, release, or Git mutation occurs in this implementation transaction"
  ],
  "fail_closed_conditions": [
    "candidate diff hashes differ from independent review",
    "any focused test, lint, format, or whitespace check fails",
    "implementation-start authority is absent or mismatched",
    "any unrelated hunk or path would be included"
  ],
  "essential_context_preservation": "owner approval evidence, full content hash, ordinary capture defaults, WI-3378 history, independent bridge gates, and all foreign worktree bytes remain intact"
}
```

## Risk / Rollback

Risk is bounded to formal approval-packet construction and deliberation-record
request defaults; an incorrect conditional could weaken owner evidence or alter
ordinary capture. Exact hunk hashes and 32 focused tests constrain that risk.
Under separate mechanical authority, finalization should be one focused `fix`
commit containing only the reviewed additions. Rollback, if later required, is
a separately governed revert of that exact commit; history is not amended and
foreign worktree content is untouched.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5412-gap-state-capture-source-residue`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` — restores source behavior already required by committed tests and a
falsely closed work item; it is not a new feature or test-only change.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
