VERIFIED

# WI-5207 Loyal Opposition Verdict — VERIFIED (post-implementation)

bridge_kind: lo_verdict
Document: gtkb-wi5207-per-document-batch-completion
Version: 004
Responds to: bridge/gtkb-wi5207-per-document-batch-completion-003.md (NEW post-implementation report)
Approved proposal: bridge/gtkb-wi5207-per-document-batch-completion-001.md
Prior GO: bridge/gtkb-wi5207-per-document-batch-completion-002.md
Reviewer: Loyal Opposition (Claude, harness B)
Date: 2026-07-12 UTC

author_identity: loyal-opposition/claude/B
author_harness_id: B
author_session_context_id: 2026-07-12T07-40-30Z-loyal-opposition-B-52e8af
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code headless bridge dispatch; resolved role loyal-opposition via ::init gtkb lo; max reasoning effort

## Verdict

**VERIFIED.** The WI-5207 per-selected-document batch-completion implementation
is independently confirmed against canonical state, not merely accepted from the
report. The five-path diff is purely WI-5207 with no foreign hunk; the seven
WI-5207 acceptance tests pass in the main tree and in an isolated
HEAD-plus-five-paths worktree; ruff lint and format are clean; and the eleven
broad-suite failures are proven pre-existing at the merge base (they reproduce
byte-identically on a clean checkout and are all non-WI-5207 nodes). The change
adds seven passing tests and zero new failures.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` — truthful dispatcher lifecycle outcomes; a multi-document batch may not report success while a selected document is unhandled.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — role-correct per-document status transitions are the completion authority.
- `DCL-NO-ACTION-STATUS-SEMANTICS-001` — a selected latest NO-ACTION requires its own corrected verdict; no-verdict is never completion.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — concrete governing links (satisfied).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — project/WI/PAUTH metadata (satisfied).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-derived partial/full/single/mixed/race evidence executed below.
- `GOV-STANDING-BACKLOG-001` — WI-5207 / TEST-11361 durable defect record.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — dispatch/verdict/WI/test/report/verdict traceability preserved.

## Independent Verification Against Canonical State

Scope isolation (the report's "no foreign hunk" claim, independently checked by reading the full working-tree diff of all five paths against the merge base):

- Every hunk in the two source files traces to per-selected-document completion tracking: the new helpers `_selected_bridge_ids_for_launch`, `_selected_top_versions_for_launch`, `_selected_document_signatures_for_launch`, and `_selected_document_verdicts`; the rewritten loyal-opposition branch of `_process_pending_exit_codes`; per-document signature retention via `last_dispatched_signatures_by_document`; the new `SELECTED_DOCUMENTS_INCOMPLETE` runtime constant; and the distinct `selected_documents_incomplete` classification added to `bridge_dispatch_config.py`. No atomic-write, registry, or other unrelated hunk appears in any of the five files.
- The three test files are pure additions (zero deletions). Every added module-level function is a `test_wi5207_*` node or the `_wi5207_batch_launch` fixture helper; imports are standard-library only. There is no dependency on an uncommitted sibling symbol (contrast the WI-5189 `_write_index` failure mode), so the scoped commit resolves in isolation.
- `scripts/gtkb_dispatcher_daemon.py` is clean in the working tree, confirming the report's "daemon source unchanged; delegation only" claim.

Isolation classification: the surrounding heavily-commingled tree's foreign drift lives in separate files that the include set excludes; there is no sub-hunk interleave inside any of the five paths and no test-to-uncommitted-sibling-source coupling. This is a cleanly-isolatable finalization, not a commingled-shared-file wall, and is finalized as a scoped commit consistent with the recent owner-tolerated per-WI VERIFIED commits on this branch.

Substance: the fix computes a completion outcome for every selected document before a single atomic state write (race-safe), declares batch success only when every selected document reaches a role-correct verdict, retains completed-document signatures while clearing incomplete-document signatures and the aggregate signature so only unhandled documents re-offer, preserves single-document `no_verdict_produced` compatibility, and classifies the partial batch as a distinct non-provider warning. The reoffer-only-missing behavior is exercised end to end by an executed next-tick fixture, not merely asserted.

## Spec-to-Test Mapping

| Specification / Requirement | Test (executed) | Executed | Observed result |
| --- | --- | --- | --- |
| SPEC-CENTRALIZED-DISPATCH-SERVICE-001 — partial batch preserves completed signature, reoffers only missing | test_wi5207_partial_batch_preserves_completed_signature_and_reoffers_only_missing | yes | pass |
| SPEC-CENTRALIZED-DISPATCH-SERVICE-001 — full batch retains every document signature | test_wi5207_full_batch_retains_every_document_signature | yes | pass |
| DCL-NO-ACTION-STATUS-SEMANTICS-001 — mixed NEW plus NO-ACTION requires each corrected verdict | test_wi5207_mixed_new_no_action_batch_requires_each_corrected_verdict | yes | pass |
| Single-document compatibility — no-verdict keeps legacy no_verdict_produced failure | test_wi5207_single_document_no_verdict_keeps_legacy_failure | yes | pass |
| Late-verdict/version race — outcome snapshotted before recipient-state mutation | test_wi5207_late_verdict_is_snapshotted_before_recipient_state_mutation | yes | pass |
| SPEC-CENTRALIZED-DISPATCH-SERVICE-001 — distinct non-provider classification | test_wi5207_selected_documents_incomplete_is_distinct_nonprovider_warning | yes | pass |
| GOV-FILE-BRIDGE-AUTHORITY-001 — daemon delegates per-document exit reconciliation | test_wi5207_daemon_delegates_per_document_exit_reconciliation | yes | pass |

All seven mapped nodes pass in both the main tree and the isolated merge-base-plus-five-paths worktree.

## Commands Executed

1. Seven WI-5207 acceptance nodes (main tree): pytest over the three dispatcher/config test modules with `-k wi5207`. Observed: `7 passed, 294 deselected`.
2. Full three-file suite (main tree): the same three modules without a selector. Observed: `290 passed, 11 failed`.
3. Baseline at the merge base (isolated detached worktree, PYTHONPATH pinned to the worktree src, five paths clean): the same three modules. Observed: `283 passed, 11 failed` — the identical eleven non-WI-5207 daemon nodes.
4. Isolated committed state (merge base plus only the five WI-5207 paths applied by `git apply`): the same three modules. Observed: `7 passed` for the WI-5207 selection and `290 passed, 11 failed` for the full suite, matching the main tree exactly; the scoped commit is not broken in isolation.
5. Ruff lint on all five paths via `python -m ruff check`. Observed: `All checks passed!`.
6. Ruff format check on all five paths via `python -m ruff format --check`. Observed: `5 files already formatted`.

Delta: 290 minus 283 equals the seven added WI-5207 tests; the failure count is unchanged at eleven. The eleven failures are all in the daemon test module (work-intent/provenance fixtures plus two per-role worker-lifetime expectations superseded by the committed 29,400-second generous lifetime) and reproduce at the clean merge base, so WI-5207 neither introduces nor masks them.

## Applicability Preflight

- packet_hash: `sha256:9c5c56b0026347a7ab3620ca8b4d17938626cf2f28069c6dea58f74b78b1033a`
- bridge_document_name: `gtkb-wi5207-per-document-batch-completion`
- operative_file: `bridge/gtkb-wi5207-per-document-batch-completion-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory only; `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` is cited and covers the artifact-oriented governance intent)

## Clause Applicability

- Clauses evaluated: 5 — must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0 (adr_dcl_clause_preflight exit 0)

| Clause | Applicability | Evidence |
| --- | --- | --- |
| GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL | must_apply | yes |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS | must_apply | yes |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING | must_apply | yes |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT | may_apply | — |
| GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS | may_apply | — |

## Review Independence

- Reviewed artifact author session: `019f5474-93a6-7f70-8e54-d6d8b0a31bb4` (Codex, harness A).
- Reviewer session: `2026-07-12T07-40-30Z-loyal-opposition-B-52e8af` (Claude, harness B, headless bridge dispatch).
- Distinct session contexts; the same-session self-review condition does not apply. The prior GO was authored by a different Claude-B session, so this verification is independent of both the implementation and the earlier proposal review.

## Prior Deliberations

- `DELIB-202666173` — owner directive to correct every defect discovered during genuine six-harness proof; the standing authority for WI-5207.
- The proposal's own prior-deliberation set (INTAKE-a815f782 per-document lease/suppression granularity; INTAKE-fd012ad6 inspection-backed operational evidence; WI-5205 canonical NO-ACTION consumer semantics, committed at the current merge base) is consistent with the archive; WI-5207 extends that granularity to completion evidence. No previously-rejected approach is revisited.

## Recommended Commit Type

Recommended commit type: `fix` — corrects a false-success/suppressed-work defect in multi-document dispatch completion (behavior repair with new regression coverage, no new capability surface).

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

## Commit Finalization Evidence

- Finalization helper: `.claude/skills/verify/helpers/write_verdict.py --finalize-verified`
- Intended commit subject: `fix(dispatch): WI-5207 per-selected-document batch completion - LO VERIFIED`
- Same-transaction path set:
- `scripts/dispatcher_runtime.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`
- `platform_tests/scripts/test_gtkb_dispatcher_daemon.py`
- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`
- `platform_tests/scripts/test_bridge_dispatch_config.py`
- `bridge/gtkb-wi5207-per-document-batch-completion-001.md`
- `bridge/gtkb-wi5207-per-document-batch-completion-002.md`
- `bridge/gtkb-wi5207-per-document-batch-completion-003.md`
- `bridge/gtkb-wi5207-per-document-batch-completion-004.md`
- Final commit SHA is emitted by the helper after commit creation; it is intentionally not self-embedded in this verdict file.
