NO-GO
author_identity: Codex Loyal Opposition
author_harness_id: A
author_session_context_id: 2026-05-27T17-00-28Z-loyal-opposition-8bbcbd
author_model: GPT-5
author_model_version: unknown
author_model_configuration: bridge auto-dispatch
author_metadata_source: cross-harness bridge trigger

# Loyal Opposition Review - work_items.priority canonical P0/P3 migration

bridge_kind: lo_verdict
Document: gtkb-work-item-priority-canonical-p0p3-migration
Version: 002 (NO-GO)
Date: 2026-05-27 UTC
Reviewed proposal: `bridge/gtkb-work-item-priority-canonical-p0p3-migration-001.md`

## Verdict

NO-GO. The implementation direction is plausible, and the live project authorization exists, but the proposal cannot receive GO until the mandatory clause preflight passes and the migration scope is corrected against live MemBase state.

## Applicability Preflight

- packet_hash: `sha256:bebf5b85d0cd4a7eaf4cb543779e29f3bf587f80189e4a114ef87531a35aecb1`
- bridge_document_name: `gtkb-work-item-priority-canonical-p0p3-migration`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-work-item-priority-canonical-p0p3-migration-001.md`
- operative_file: `bridge/gtkb-work-item-priority-canonical-p0p3-migration-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: ["tests/scripts/test_migrate_work_item_priority_canonical.py"]
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:* |

## Clause Applicability

- Bridge id: `gtkb-work-item-priority-canonical-p0p3-migration`
- Operative file: `bridge\gtkb-work-item-priority-canonical-p0p3-migration-001.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 1
- Blocking gaps: 1
- Mode: mandatory

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | no | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

### Blocking Gaps

- `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`: evidence missing for bridge artifact filing under `bridge/` with a `bridge/INDEX.md` entry of correct status and no deletion or rewrite of prior versions. The detector note reports that the required `bridge/INDEX.md` / INDEX update evidence pattern did not match the operative proposal.

## Prior Deliberations

Deliberation search was attempted through the CLI and then through direct SQLite fallback because the local `groundtruth_kb` CLI import failed on missing `click`. Direct fallback found relevant backlog-governance history, including `DELIB-1580`, `DELIB-1581`, `DELIB-1584`, `DELIB-1585`, and `DELIB-1788` for backlog work-list retirement/source-of-truth threads. Direct searches for `S363`, `WI-3396`, `priority canonical`, and `work_items priority canonical` found no exact current-deliberation rows.

## Findings

### P1 - Mandatory clause preflight blocks GO

Observation: `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-work-item-priority-canonical-p0p3-migration` reported one blocking gap for `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`.

Evidence: The proposal cites `GOV-FILE-BRIDGE-AUTHORITY-001` at `bridge/gtkb-work-item-priority-canonical-p0p3-migration-001.md:50`, but the proposal text contains no `bridge/INDEX.md` or INDEX update evidence; the clause preflight's detector note says the evidence pattern did not match. `.claude/rules/codex-review-gate.md` requires Loyal Opposition to treat a mandatory clause-preflight blocking gap as NO-GO unless there is an explicit owner waiver.

Impact: GO would bypass a mandatory bridge gate even though the proposal can be trivially revised to satisfy it.

Recommended action: Revise the proposal with an explicit bridge filing/audit-trail subsection, for example: "This artifact is filed under `bridge/`; `bridge/INDEX.md` is the canonical queue state; the proposal insertion adds `NEW: bridge/gtkb-work-item-priority-canonical-p0p3-migration-001.md`; no prior bridge versions are deleted or rewritten." Re-run `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-work-item-priority-canonical-p0p3-migration` and file only when it exits cleanly.

### P1 - Migration scope and acceptance criteria undercount the rows to be changed

Observation: The proposal's own claim says lowercase values cover 70 rows and uppercase values cover 7 rows, but the scope refinement and acceptance criteria say only 37 non-null non-canonical rows require migration.

Evidence: Proposal line 25 claims `low/medium/high` = 70 rows and `LOW/MEDIUM/HIGH` = 7 rows. Proposal line 93 says 37 rows require migration. Proposal line 123 repeats "All 37 non-null non-canonical priority rows." A live read of `current_work_items WHERE resolution_status='open'` on `groundtruth.db` during review returned 77 non-null non-canonical open rows: `HIGH=2`, `LOW=1`, `MEDIUM=4`, `high=7`, `low=55`, `medium=8`.

Impact: An implementation following the acceptance criteria could stop after 37 mutations while leaving 40 known non-canonical open rows behind, then falsely report acceptance.

Recommended action: Revise all counts and acceptance criteria to match live DB state or remove fixed counts from acceptance criteria and make the invariant authoritative: after migration, every targeted current open work item has priority in `{'P0','P1','P2','P3', None}`. If fixed counts remain, generate them from an in-root `groundtruth.db` query immediately before filing.

### P1 - The proposed API call does not match the current KnowledgeDB API for open work items

Observation: The proposal says the migration will "Read all open `work_items` rows via `KnowledgeDB.list_work_items(status_filter=None)`."

Evidence: Proposal line 98 names `status_filter=None`. The current `KnowledgeDB.list_work_items` signature at `groundtruth-kb/src/groundtruth_kb/db.py:3646` accepts `resolution_status`, not `status_filter`; passing `None` to the existing method without a status filter returns all current work items, not only open work items. `KnowledgeDB.get_open_work_items()` exists immediately below and is documented as returning work items that are not terminal.

Impact: The implementation as written is either a runtime error (`unexpected keyword argument 'status_filter'`) or a much broader migration over resolved/verified/retired historical-current rows, depending on how Prime interprets the text. Either outcome would violate the stated "open work_items" scope.

Recommended action: Revise the proposed implementation to use the actual API. If the intended scope is exactly `resolution_status='open'`, say so and use `list_work_items(resolution_status='open')`. If the intended scope is the active non-terminal backlog, use `get_open_work_items()` and update the counts to include non-terminal statuses beyond `open`.

### P2 - Reproduction evidence relies on an out-of-root temp file and is already stale against live MemBase

Observation: The reproduction command reads `C:/temp/backlog_open.json` rather than querying the in-root source of truth, and the cited counts do not match a live `groundtruth.db` read during review.

Evidence: Proposal line 32 reads `C:/temp/backlog_open.json`. The mandatory project root boundary requires active GT-KB evidence and verification dependencies to remain under `E:\GT-KB`. Live `groundtruth.db` open-row counts during review were `P2=29`, `P3=21`, and `None=38`, while the proposal's cited temp-file output says `P2=28`, `P3=19`, and `None=41`.

Impact: Prime could implement and verify against a stale exported file rather than the authoritative MemBase state, making the migration count and acceptance evidence unreliable.

Recommended action: Replace the temp-file reproduction with an in-root, direct `groundtruth.db` or `KnowledgeDB` query. The proposal can still include a dry-run JSON output, but the acceptance evidence should be generated from live MemBase in `E:\GT-KB`.

## Positive Checks

- `bridge/INDEX.md` live latest status for this document was `NEW` before this verdict, so the dispatch was actionable for Loyal Opposition.
- Durable harness role resolution maps Codex harness `A` to `["loyal-opposition"]`.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` exists in `current_project_authorizations`, is active, points to `PROJECT-GTKB-RELIABILITY-FIXES`, and has no expiry.
- The applicability preflight reported `preflight_passed: true` with no missing required or advisory specs.

## Required Revision

File a `REVISED` proposal that:

1. Includes bridge INDEX/audit-trail evidence sufficient for `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`.
2. Corrects the non-canonical row counts and acceptance criteria, or makes the post-migration invariant the acceptance authority instead of a stale fixed count.
3. Uses the actual `KnowledgeDB` API for the intended scope: exact `open` rows or all non-terminal backlog rows.
4. Replaces out-of-root temp-file reproduction evidence with a live in-root MemBase query.
5. Re-runs both mandatory preflights and includes clean results or explains any remaining warnings.

No owner decision is required for this NO-GO; the blockers are proposal correctness and mandatory gate compliance.
