REVISED

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ef07d-dbf6-7083-bd4c-3c997d20f111
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex auto-builder automation; approval_policy=never; workspace=E:\GT-KB; resolved_role=prime-builder
author_metadata_source: automation-prompt-live-state

# Implementation Proposal - GOV-REQUIREMENTS-COLLECTION-HOOK-001 tag cleanup

bridge_kind: prime_proposal
Document: gtkb-gov-requirements-collection-hook-tag-cleanup
Version: 003
Date: 2026-06-22 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-NONFASTLANE-BATCH-2026-06-21
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3381

target_paths: [".groundtruth/formal-artifact-approvals/*-GOV-REQUIREMENTS-COLLECTION-HOOK-001-v5.json", "groundtruth.db", "platform_tests/scripts/test_gov_requirements_collection_hook_tags.py"]

Implementation proposal for a bounded platform-metadata correction: a
versioned MemBase tag-field supersession for
`GOV-REQUIREMENTS-COLLECTION-HOOK-001` plus an additive regression test.

## Revision Claim

This revision resolves the `-002` NO-GO by adding `groundtruth.db` to
`target_paths`, because the proposed implementation explicitly includes a
MemBase v5 supersession. The database mutation remains constrained to the
canonical MemBase writer path and still requires the formal-artifact approval
packet before insertion.

No behavioral scope is broadened. The correction still only removes the stale
`llm-classification` and `retrieval-augmented` tags from the latest version of
`GOV-REQUIREMENTS-COLLECTION-HOOK-001`; it does not alter the hook, the spec
body, the title, or any assertion.

## NO-GO Resolution

The latest Loyal Opposition finding was:

> `groundtruth.db` is planned but not authorized by `target_paths`.

Resolution:

- `groundtruth.db` is now an explicit target path.
- The approval-packet target remains declared.
- The additive regression test target remains declared.
- Implementation remains blocked until a live GO exists, a matching
  implementation-start packet is active, and the formal-artifact approval
  packet is present and approved.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`:

- `.groundtruth/formal-artifact-approvals/*-GOV-REQUIREMENTS-COLLECTION-HOOK-001-v5.json`
- `groundtruth.db`
- `platform_tests/scripts/test_gov_requirements_collection_hook_tags.py`

No adopter/application path under `applications/` is touched.

## Specification Links

- `GOV-REQUIREMENTS-COLLECTION-HOOK-001` - the target GOV record whose latest
  tags are corrected by v5.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge state and append-only numbered
  bridge files are the canonical workflow state.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the correction is preserved through
  WI-3381, this bridge thread, the approval packet, MemBase v5, tests, and the
  post-implementation report.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal
  cites the requirements governing the metadata correction.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project authorization,
  project, work item, and target paths are declared above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification derives from
  the cited metadata and governance requirements.
- `SPEC-AUQ-POLICY-ENGINE-001` - the spec governs deterministic AUQ hook
  behavior, so its tags must not advertise abandoned LLM/retrieval designs.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths are in-root
  GT-KB platform surfaces.
- `GOV-STANDING-BACKLOG-001` - WI-3381 is open backlog work.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - the tag correction preserves the
  existing hook parity contract without changing hook code.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the correction is versioned and
  artifact-backed, not an in-place or chat-only edit.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the spec and work item move through
  explicit lifecycle transitions with durable evidence.

## Requirement Sufficiency

Existing requirements remain sufficient. The v3/v4 body of
`GOV-REQUIREMENTS-COLLECTION-HOOK-001` already mandates a deterministic
regex-based hook and forbids LLM or retrieval-augmented behavior. WI-3381 only
aligns the latest tags with that existing verified body. No new or revised GOV,
SPEC, ADR, DCL, or PB requirement is introduced.

## Proposed Scope

### IP-1: Issue v5 with corrected tags

Insert version 5 of `GOV-REQUIREMENTS-COLLECTION-HOOK-001` through the canonical
MemBase writer. The v5 tags are exactly:

`["governance", "requirements-collection", "user-prompt-submit-hook", "3-option-clarification"]`

All non-tag fields, including title, body, assertions, type, and status, are
carried forward from v4 unchanged. v4 remains preserved on the append-only
record.

The v5 insertion must carry a dated formal-artifact approval packet under
`.groundtruth/formal-artifact-approvals/` whose presented content matches the
inserted v5 record and whose approval evidence shows owner approval before
insertion.

### IP-2: Add regression coverage

Add `platform_tests/scripts/test_gov_requirements_collection_hook_tags.py`.
The test reads `GOV-REQUIREMENTS-COLLECTION-HOOK-001` through the canonical
MemBase reader against the root `groundtruth.db` and asserts:

- `llm-classification` is absent from the current tag set;
- `retrieval-augmented` is absent from the current tag set;
- `governance`, `requirements-collection`, `user-prompt-submit-hook`, and
  `3-option-clarification` remain present;
- the current status remains `verified`;
- the title remains unchanged from v4.

### Out Of Scope

- No change to `.claude/hooks/spec-classifier.py`.
- No change to `.codex/hooks.json` or any hook registration.
- No rewrite of v1-v4 records.
- No direct database edit outside the canonical writer.
- No production deployment, credential lifecycle change, or external mutation.

## Specification-Derived Verification Plan

| Spec clause | Derived test / inspection | Assertion |
|---|---|---|
| `GOV-REQUIREMENTS-COLLECTION-HOOK-001` deterministic no-LLM/no-retrieval contract | `test_no_abandoned_design_tags` | Current tags contain neither `llm-classification` nor `retrieval-augmented`. |
| `GOV-REQUIREMENTS-COLLECTION-HOOK-001` no over-correction | `test_retained_tags_and_status_preserved` | Retained tags are present; status remains `verified`; title is unchanged. |
| `SPEC-AUQ-POLICY-ENGINE-001` deterministic engine metadata | Structural v5-v4 inspection in the post-implementation report | Only `tags` changed; v5 body/title match v4. |
| Formal-artifact approval requirements | Approval-packet inspection in the post-implementation report | Approval packet is present, owner-approved, and matches the inserted v5 content. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Post-implementation report | Report carries this mapping plus command evidence. |

Execution commands:

```text
python -m pytest platform_tests/scripts/test_gov_requirements_collection_hook_tags.py -q --tb=short
python -m ruff check platform_tests/scripts/test_gov_requirements_collection_hook_tags.py
python -m ruff format --check platform_tests/scripts/test_gov_requirements_collection_hook_tags.py
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-gov-requirements-collection-hook-tag-cleanup
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-gov-requirements-collection-hook-tag-cleanup
```

## Prior Deliberations

- `DELIB-2261` - LO review context for the predecessor S358 W3 title-only
  correction on this spec.
- `DELIB-2262` - LO review of the W3 revised report, confirming the prior
  correction was title-scoped.
- `DELIB-S358-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION` - owner
  authorization and scope for the predecessor governance-correction project.
- `DELIB-2282` - sibling governance-correction review precedent for
  metadata-only inspection-based verification.
- `DELIB-20265457` - owner AUQ authorizing the
  `PROJECT-GTKB-RELIABILITY-FIXES` proposal batch that includes WI-3381.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-NONFASTLANE-BATCH-2026-06-21` covers
  this WI-3381 bridge proposal path.
- Formal artifact mutation approval is still required at implementation time:
  the v5 approval packet must be presented and approved before the MemBase
  insertion. This proposal does not treat the batch authorization as that
  per-artifact approval.

No additional owner input is required for Loyal Opposition to review this
revised proposal.

## Pre-Filing Preflight Subsection

Prime Builder will file this REVISED artifact only through
`.codex/skills/bridge/helpers/revise_bridge.py file`, which runs both candidate
preflights before publishing live bridge state:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-gov-requirements-collection-hook-tag-cleanup --content-file <candidate> --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-gov-requirements-collection-hook-tag-cleanup --content-file <candidate>
```

The filed artifact will be the next numbered bridge file,
`bridge/gtkb-gov-requirements-collection-hook-tag-cleanup-003.md`, preserving
the append-only versioned bridge file chain. Prior versions `-001` and `-002`
will not be deleted or rewritten.

## Acceptance Criteria

1. v5 of `GOV-REQUIREMENTS-COLLECTION-HOOK-001` exists with the corrected tag
   set and all non-tag fields carried forward from v4.
2. The v5 insertion carries owner-approved formal-artifact approval evidence.
3. The additive tag regression test exists and passes.
4. Ruff check and format-check pass on the new test.
5. Bridge applicability and ADR/DCL clause preflights pass on the
   implementation report.

## Risks / Rollback

- Risk: a non-tag v5 field diverges from v4. Mitigation: include structural
  v5-v4 comparison in the report and test title/status preservation.
- Risk: the test blocks future legitimate tags. Mitigation: assert absence of
  the two stale tags and presence of retained tags, not exact-list equality.
- Rollback: a GOV-spec supersession is append-only and reversible through a
  later versioned correction; the additive test file is removable in isolation.

## Files Expected To Change

- `.groundtruth/formal-artifact-approvals/*-GOV-REQUIREMENTS-COLLECTION-HOOK-001-v5.json`
- `groundtruth.db`
- `platform_tests/scripts/test_gov_requirements_collection_hook_tags.py`

## Recommended Commit Type

`fix`
