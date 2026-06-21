NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 96b4ab64-e440-47b7-8c81-cd55bc7a5c1e
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: default

# Implementation Proposal - GOV-REQUIREMENTS-COLLECTION-HOOK-001 tags retain abandoned-design remnants

bridge_kind: prime_proposal
Document: gtkb-gov-requirements-collection-hook-tag-cleanup
Version: 001 (DRAFT; non-dispatchable)
Date: 2026-06-21 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-NONFASTLANE-BATCH-2026-06-21
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3381

target_paths: [".groundtruth/formal-artifact-approvals/*-GOV-REQUIREMENTS-COLLECTION-HOOK-001-v5.json", "platform_tests/scripts/test_gov_requirements_collection_hook_tags.py"]

Implementation proposal for a bounded platform-metadata correction (MemBase tag-field supersession) plus an additive regression test.

## Claim

`GOV-REQUIREMENTS-COLLECTION-HOOK-001` is at version 4, status `verified`. Its `tags` field still reads `["governance", "requirements-collection", "user-prompt-submit-hook", "llm-classification", "3-option-clarification", "retrieval-augmented"]`. Two of those tags - `llm-classification` and `retrieval-augmented` - advertise the abandoned design that the S332 owner cost directive removed: the v3/v4 body mandates a deterministic fixed-regex gate and explicitly forbids any LLM or retrieval-augmented mechanism ("The hook MUST NOT make external API calls (no LLM, no retrieval-augmented options)"), and the implementation (`.claude/hooks/spec-classifier.py`) is a deterministic regex classifier whose module docstring states "The hook is a regex gate, not an LLM classifier." The S358 W3 fix (this same spec's v4) removed the identical "(LLM classification + retrieval-augmented options)" parenthetical from the title, but the W3 GO-approved scope was title-only, so the two stale tags were carried forward unchanged from v3 to v4. The stale tags misrepresent a verified governance spec for tag-based search: a search on `llm-classification` or `retrieval-augmented` surfaces a spec that forbids exactly those mechanisms.

This proposal issues version 5 of `GOV-REQUIREMENTS-COLLECTION-HOOK-001` whose only change from v4 is the `tags` field, dropping the two abandoned-design tags. The v5 tags are exactly: `["governance", "requirements-collection", "user-prompt-submit-hook", "3-option-clarification"]`. The v4 title, description/body, assertions, type, status, and every other field are carried forward unchanged; v4 remains on the append-only record. No behavioral rule is touched - it is already correct and verified. This proposal also adds one additive regression test that pins the corrected v5 tag set so the abandoned-design tags cannot silently return.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-REQUIREMENTS-COLLECTION-HOOK-001` v3/v4 already establishes the deterministic-regex, no-LLM/no-retrieval behavioral contract; this fix only makes the spec's `tags` metadata consistent with the already-correct body and implementation by dropping two stale tags. No new or revised requirement/specification is introduced; the v5 record exists solely to correct stale tag metadata, and the additive test pins the corrected state. (This WI is covered by `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-NONFASTLANE-BATCH-2026-06-21` per `DELIB-20265457`; no new spec is required.)

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: the v5 formal-artifact-approval packet under `.groundtruth/formal-artifact-approvals/` (a new dated `*-GOV-REQUIREMENTS-COLLECTION-HOOK-001-v5.json` file), `platform_tests/scripts/test_gov_requirements_collection_hook_tags.py`, and the MemBase write target `groundtruth.db` (root of `E:\GT-KB`). No application path under `applications/` is touched.

## Specification Links

- `GOV-REQUIREMENTS-COLLECTION-HOOK-001` - the target spec; this proposal issues its v5 to drop the stale `llm-classification` and `retrieval-augmented` tags. Cited as the artifact being corrected.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge state and versioned bridge files are canonical workflow state; this proposal is filed and reviewed through that workflow and the v5 supersession proceeds only on a GO.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the correction is preserved as durable artifacts: WI-3381, this proposal, the GOV v5 record, the v5 approval packet, the regression test, and the post-implementation report.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal carries a complete, relevance-closed Specification Links section citing every spec that constrains the tag correction.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan derives a test/inspection from each cited spec (the additive tag-pinning test plus structural MemBase inspection of the v5 vs v4 fields).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries the mandatory Project Authorization, Project, and Work Item header lines.
- `SPEC-AUQ-POLICY-ENGINE-001` - the spec-classifier hook participates in the deterministic AUQ policy engine; dropping the LLM/retrieval tags keeps the spec's metadata consistent with the deterministic engine the implementation already realizes.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - the only write targets (MemBase `groundtruth.db`, the v5 approval packet, and a platform test) are in-root GT-KB platform surfaces; no adopter/application placement boundary is crossed.
- `GOV-STANDING-BACKLOG-001` - WI-3381 is a standing-backlog work item (origin=hygiene, P3) under PROJECT-GTKB-RELIABILITY-FIXES.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - the underlying spec governs the `spec-classifier.py` UserPromptSubmit hook whose Codex-side parity is maintained per this ADR; the tag correction does not alter the hook or its parity registration, so this ADR's parity contract is preserved unchanged.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the tag correction remains artifact-backed (a versioned v4-to-v5 MemBase supersession) rather than an in-place edit; traceability is preserved across WI-3381, the bridge thread, the approval packet, and the report.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - WI-3381 moves through open, in-progress, and verified lifecycle states; the spec moves from v4 to v5; the correction is recorded as an append-only artifact lifecycle transition.

## Prior Deliberations

A Deliberation Archive search was performed for the requirements-collection hook and the LLM-classifier-abandonment decision; the relevant prior decisions are the S358 W3 title-fix thread (the predecessor correction on this exact spec) and the S332 cost directive that abandoned the LLM design.

- `DELIB-2261` - Loyal Opposition Review: gtkb-s358-w3-requirements-collection-hook-title-fix-009 - LO review context for the predecessor W3 title-only correction on this exact spec, establishing that the abandoned-design wording must be removed wherever it appears.
- `DELIB-2262` - Loyal Opposition Review - W3 GOV-REQUIREMENTS-COLLECTION-HOOK-001 Title Fix REVISED-2 - the LO review of the W3 REVISED report; confirms the title-only scope that left the tags uncorrected (the gap this WI closes).
- `DELIB-S358-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION` - Owner decision authorizing and scoping the S358 combined governance-correction project; records that W3 was metadata-only and title-scoped, which is why the two stale tags were carried forward and now require this follow-on v5 correction.
- `DELIB-2282` - Loyal Opposition Review - W1 Retirement-Machinery Correction - sibling S358 governance-correction workstream context; establishes the inspection-based verification model accepted for metadata-only governance corrections in that project.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-NONFASTLANE-BATCH-2026-06-21` - the non-fast-lane batch project authorization covering all open PROJECT-GTKB-RELIABILITY-FIXES work items authored in this 2026-06-21 batch; WI-3381 (origin=hygiene, P3) is in scope, so this proposal proceeds under that envelope without a fresh per-item AUQ for authoring.
- `DELIB-20265457` - owner AUQ (2026-06-21) authorizing the PROJECT-GTKB-RELIABILITY-FIXES proposal batch; WI-3381 is one of the open work items this decision directs to be authored as a NEW proposal.
- Implementation-time owner approval is still required: the GOV v5 supersession is a formal-artifact mutation requiring a formal-artifact-approval packet presented to and approved by the owner before insertion, with the exact v5 tag list and the carried-forward v4 body/title in the packet. This batch authorization authorizes the workstream; it does not pre-grant the per-artifact formal-artifact approval.

## Proposed Scope

### IP-1: Issue v5 of GOV-REQUIREMENTS-COLLECTION-HOOK-001 with the corrected tags

Insert a version 5 of `GOV-REQUIREMENTS-COLLECTION-HOOK-001` via the canonical MemBase writer (`db.insert_spec` / `gt`-CLI spec path), whose `tags` field is the v4 tags with `llm-classification` and `retrieval-augmented` removed. The v5 tags are exactly:

`["governance", "requirements-collection", "user-prompt-submit-hook", "3-option-clarification"]`

Every other field - title, description/body, assertions, type, status, and all remaining metadata - is carried forward from v4 unchanged. v4 stays on the append-only record. The v5 insertion carries a new dated formal-artifact-approval packet (`.groundtruth/formal-artifact-approvals/2026-06-21-GOV-REQUIREMENTS-COLLECTION-HOOK-001-v5.json`) whose presented content is the v5 record (corrected tags plus the carried-forward v4 title/body), owner-approved before insertion. `changed_by` accurately reflects the active Prime Builder harness identity; `change_reason` cites WI-3381, this bridge thread, and the v5 approval-packet path.

### IP-2: Add a regression test pinning the corrected tag set

Add `platform_tests/scripts/test_gov_requirements_collection_hook_tags.py`. The test reads `GOV-REQUIREMENTS-COLLECTION-HOOK-001` through the canonical MemBase reader (`groundtruth_kb.db.KnowledgeDB.get_spec`) against the root `groundtruth.db` and asserts: (a) the abandoned-design tags `llm-classification` and `retrieval-augmented` are absent from the current (latest-version) tag set; (b) the retained tags `governance`, `requirements-collection`, `user-prompt-submit-hook`, and `3-option-clarification` are present; (c) the spec's current status remains `verified` and the title is unchanged (guards against over-correction). The test is read-only and additive; it introduces no new public surface.

### Out of scope

This proposal does not change the v4 behavioral rule, body, title, or any assertion. It does not modify `.claude/hooks/spec-classifier.py` (already a correct deterministic regex gate), `.codex/hooks.json`, or any other source, hook, or configuration. It does not rewrite v1-v4 (append-only). The WI's alternative framing ("model/display that automatic completion can precede report verification") is not applicable to this hygiene tag correction. No behavior or contract change is proposed.

## Specification-Derived Verification Plan

| Spec clause | Derived test / inspection | Assertion |
|---|---|---|
| `GOV-REQUIREMENTS-COLLECTION-HOOK-001` (tags must reflect the deterministic, no-LLM/no-retrieval contract) | `test_no_abandoned_design_tags` (in `platform_tests/scripts/test_gov_requirements_collection_hook_tags.py`) | The current `GOV-REQUIREMENTS-COLLECTION-HOOK-001` tag set, read via `KnowledgeDB.get_spec`, contains neither `llm-classification` nor `retrieval-augmented`. |
| `GOV-REQUIREMENTS-COLLECTION-HOOK-001` (no false-negative / over-correction regression) | `test_retained_tags_and_status_preserved` | The tag set still contains `governance`, `requirements-collection`, `user-prompt-submit-hook`, and `3-option-clarification`; status is `verified` and the title is unchanged from v4. |
| `SPEC-AUQ-POLICY-ENGINE-001` (metadata consistent with deterministic engine) | structural MemBase inspection (recorded in the post-implementation report) | v5 changed only the `tags` field; the v5 body/title hash equals v4 byte-for-byte; v4 is preserved on the append-only record. |
| `GOV-ARTIFACT-APPROVAL-001` / `DCL-ARTIFACT-APPROVAL-HOOK-001` (formal-artifact approval) | approval-packet inspection (recorded in the post-implementation report) | The v5 supersession carries `.groundtruth/formal-artifact-approvals/2026-06-21-GOV-REQUIREMENTS-COLLECTION-HOOK-001-v5.json` with `presented_to_user=true`, `approved_by=owner`, and a content hash matching the inserted v5 record. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (spec-to-test mapping with executed evidence) | the post-implementation report | The report carries this mapping plus executed pytest/ruff command evidence for the new test and the structural-inspection evidence for the v5 row. |

Execution commands (run at implementation time; not run in this draft):
- `python -m pytest platform_tests/scripts/test_gov_requirements_collection_hook_tags.py -q --tb=short`
- `python -m ruff check platform_tests/scripts/test_gov_requirements_collection_hook_tags.py`
- `python -m ruff format --check platform_tests/scripts/test_gov_requirements_collection_hook_tags.py`

The MemBase v5 supersession itself is verified by structural inspection (the v5 vs v4 field-level comparison and the approval-packet read), recorded in the post-implementation report; that is the inspection-based verification model accepted for the S358 governance-correction workstreams on this same spec.

## Acceptance Criteria

1. A v5 record of `GOV-REQUIREMENTS-COLLECTION-HOOK-001` exists in MemBase whose `tags` field is exactly `["governance", "requirements-collection", "user-prompt-submit-hook", "3-option-clarification"]`.
2. The v5 title, body, assertions, and all non-tag fields equal v4 byte-for-byte; v4 is preserved on the append-only record.
3. The v5 supersession carries an owner-approved formal-artifact-approval packet at `.groundtruth/formal-artifact-approvals/2026-06-21-GOV-REQUIREMENTS-COLLECTION-HOOK-001-v5.json` with a matching content hash.
4. `platform_tests/scripts/test_gov_requirements_collection_hook_tags.py` exists, its derived tests pass, and `ruff check` / `ruff format --check` are clean on the new test file.
5. Both bridge preflights pass on the post-implementation report.

## Risks / Rollback

- Risk: the v5 carry-forward diverges from v4 on a non-tag field (title/body). Mitigation: the acceptance criteria require a byte-for-byte non-tag comparison; the approval packet's presented content is inspected against v4 before insertion.
- Risk: over-correction (dropping a tag that should be kept). Mitigation: the proposal states the exact v5 tag list verbatim; `test_retained_tags_and_status_preserved` asserts the four retained tags, status, and unchanged title.
- Risk: the additive test pins the tag set too tightly and breaks on a future legitimate tag addition. Mitigation: the test asserts absence of the two stale tags and presence of the four retained tags via membership, not exact-list equality, so a future legitimate tag does not falsely fail it.
- Rollback: a GOV-spec supersession is an append-only versioned MemBase mutation reversible by a further versioned correction; the new test file is removable in isolation. No migration is involved.

## Files Expected To Change

- `.groundtruth/formal-artifact-approvals/2026-06-21-GOV-REQUIREMENTS-COLLECTION-HOOK-001-v5.json` (new v5 approval packet)
- `groundtruth.db` (MemBase v5 GOV-spec supersession; canonical writer, not a direct file edit)
- `platform_tests/scripts/test_gov_requirements_collection_hook_tags.py` (new additive regression test)

## Recommended Commit Type

`fix` - WI-3381 is origin=hygiene/defect: the v4 tag metadata misrepresents the spec, and this corrects it with a versioned v5 tag-only supersession plus a regression test. No new capability surface is added (the additive test guards the corrected state). The post-implementation report will carry the recommended type matching the final change set per the Conventional Commits Type Discipline.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
