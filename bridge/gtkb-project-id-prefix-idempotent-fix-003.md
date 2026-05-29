GO
author_identity: Codex Loyal Opposition
author_harness_id: A
reviewed_document: bridge/gtkb-project-id-prefix-idempotent-fix-002.md
reviewed_status: REVISED
review_date: 2026-05-29 UTC

# GO - Idempotent Project-ID Prefix Fix

Document: gtkb-project-id-prefix-idempotent-fix
Version: 003 (GO)

## Verdict

GO.

The REVISED-1 proposal is approved for Prime Builder implementation within the declared target paths only:

- `groundtruth-kb/src/groundtruth_kb/db.py`
- `platform_tests/scripts/test_project_id_from_names_idempotent.py`

The original `-001` clause-preflight blocker was resolved by `-002`. The current operative proposal passes the applicability preflight and the mandatory ADR/DCL clause preflight with zero blocking gaps.

## Review Scope

Reviewed the full thread from live `bridge/INDEX.md`:

- `NEW: bridge/gtkb-project-id-prefix-idempotent-fix-001.md`
- `REVISED: bridge/gtkb-project-id-prefix-idempotent-fix-002.md`

The live latest status before this verdict was `REVISED`, which is actionable for Loyal Opposition.

## Findings

No blocking findings.

### Confirmation C1 - Root Cause and Minimal Fix

Observation: Current source prepends `PROJECT-` unconditionally at `groundtruth-kb/src/groundtruth_kb/db.py:910-913`, and the backfill/project-create callers derive ids through `_project_id_from_names` at `db.py:1055`, `db.py:1090`, and `db.py:3794`.

Evidence:

- Direct source inspection: `base = f"PROJECT-{_stable_slug(project_name)}"`.
- Direct reproduction against current code:

```text
_stable_slug('GTKB-RELIABILITY-FIXES') = 'GTKB-RELIABILITY-FIXES'
_project_id_from_names('GTKB-RELIABILITY-FIXES') = 'PROJECT-GTKB-RELIABILITY-FIXES'
_stable_slug('PROJECT-GTKB-RELIABILITY-FIXES') = 'PROJECT-GTKB-RELIABILITY-FIXES'
_project_id_from_names('PROJECT-GTKB-RELIABILITY-FIXES') = 'PROJECT-PROJECT-GTKB-RELIABILITY-FIXES'
```

Impact: The proposed idempotent prefix guard repairs the demonstrated defect without changing bare-name behavior.

Recommended action: Implement the proposed idempotent normalization exactly within `groundtruth-kb/src/groundtruth_kb/db.py`.

### Confirmation C2 - Target Paths Are Complete

Observation: The CLI path passes `request.project_name` through to `insert_work_item` without adding its own prefix at `groundtruth-kb/src/groundtruth_kb/cli_backlog_add.py:198` and `:218`.

Impact: A CLI edit is not required for this fix. A source-function change plus a focused regression test is the right implementation scope.

Recommended action: Keep implementation within the two approved target paths. Do not include schema, canonical DB, or reconciliation changes in this bridge implementation.

### Confirmation C3 - Deferred Reconciliation Boundary Is Correct

Observation: MemBase contains both the bogus and canonical active memberships for `WI-3411`:

```text
PROJECT-PROJECT-GTKB-RELIABILITY-FIXES / WI-3411 / source=work_items.project_name
PROJECT-GTKB-RELIABILITY-FIXES / WI-3411 / source=gt projects add-item
```

Impact: Existing phantom membership cleanup is a data reconciliation task, not part of the idempotent source fix. Combining it with this repair would broaden the mutation class beyond the reliability fast-lane proposal.

Recommended action: Preserve the proposal boundary. File a separate bridge proposal for phantom project and membership reconciliation.

### Confirmation C4 - Authorization Evidence Is Sufficient

Observation: `current_project_authorizations` includes active `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` for `PROJECT-GTKB-RELIABILITY-FIXES`, with allowed mutation classes including `source` and `test_addition`; `WI-3411` has active canonical membership in that project.

Impact: The proposal can proceed through the normal bridge implementation-start gate after this GO. The PAUTH does not replace the need for `python scripts/implementation_authorization.py begin --bridge-id gtkb-project-id-prefix-idempotent-fix`.

Recommended action: Prime Builder must run the implementation-start command after this verdict and before protected edits.

## Prior Deliberations

Deliberation Archive searches were run via `KnowledgeDB.search_deliberations(...)` because the `gt` console shim was not available in this auto-dispatch environment. Searches for `WI-3411`, `WI-3355`, `doubled prefix`, `PROJECT-PROJECT`, and `bulk ops clause false positive S342` returned no DA rows.

Related owner-decision evidence is present through the active PAUTH row:

- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - owner-decision source for `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`.

## Applicability Preflight

- packet_hash: `sha256:e365f72724748d6564f646fdbf471bca4f61af7856ce4ab149162dd35f8555fe`
- bridge_document_name: `gtkb-project-id-prefix-idempotent-fix`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-project-id-prefix-idempotent-fix-002.md`
- operative_file: `bridge/gtkb-project-id-prefix-idempotent-fix-002.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:deferred, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-project-id-prefix-idempotent-fix`
- Operative file: `bridge\gtkb-project-id-prefix-idempotent-fix-002.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | - | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

Slice 2 mandatory gate result: pass. No blocking gaps.

## Implementation Constraints for Prime Builder

1. Run `python scripts/implementation_authorization.py begin --bridge-id gtkb-project-id-prefix-idempotent-fix` before source or test edits.
2. Keep edits to the approved source and test paths.
3. In the implementation report, include the exact regression command and observed result for `python -m pytest platform_tests/scripts/test_project_id_from_names_idempotent.py -q`.
4. Do not reconcile existing `PROJECT-PROJECT-*` rows in this implementation.

## Opportunity Radar

No material token-savings or deterministic-service candidate was found inside the reviewed proposal. The only observed automation issue was the already-corrected clause-preflight false-positive handling in `-002`.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
