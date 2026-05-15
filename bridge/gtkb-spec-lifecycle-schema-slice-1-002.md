NO-GO

# Loyal Opposition Review - Spec Lifecycle Schema Slice 1

**Document:** `gtkb-spec-lifecycle-schema-slice-1`
**Reviewed version:** `bridge/gtkb-spec-lifecycle-schema-slice-1-001.md`
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-05-14 UTC

## Verdict

NO-GO. The mechanical bridge gates pass, and the proposal is correctly scoped to the first additive schema slice in broad terms. However, the concrete source-link table/API shape in this Slice 1 proposal diverges from the parent GO's operative contract without identifying that as an intentional scope change or carrying the changed contract into later slice dependencies. That creates a high-likelihood schema/API drift before implementation starts.

File bridge scan: 1 entry processed.

## Command Evidence

```text
python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-spec-lifecycle-schema-slice-1 --format json --preview-lines 400
```

Result: `found: true`; `drift: []`; latest INDEX status chain was only `NEW: bridge/gtkb-spec-lifecycle-schema-slice-1-001.md`.

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-spec-lifecycle-schema-slice-1
```

Result:

```text
## Applicability Preflight

- packet_hash: `sha256:4b98625bc14d96279996c3c3d1e2f6b58aeb80d8bae70d15d975df80b678c28b`
- bridge_document_name: `gtkb-spec-lifecycle-schema-slice-1`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-spec-lifecycle-schema-slice-1-001.md`
- operative_file: `bridge/gtkb-spec-lifecycle-schema-slice-1-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-spec-lifecycle-schema-slice-1
```

Result:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-spec-lifecycle-schema-slice-1`
- Operative file: `bridge\gtkb-spec-lifecycle-schema-slice-1-001.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._
```

```text
python -m groundtruth_kb deliberations search "spec lifecycle schema" --limit 10
python -m groundtruth_kb deliberations search "implementation_verified_at retired_at parent specification_deliberation_sources" --limit 10
python -m groundtruth_kb deliberations search "SPEC-LIFECYCLE-SCHEMA-MIGRATION" --limit 10
```

Relevant results included `DELIB-0707` (owner decision that existing specs must be migrated to the enriched schema using implementation as reference), `DELIB-1852` (GO on the revised lifecycle schema migration scoping thread), and `DELIB-1853` (prior NO-GO on the initial lifecycle schema migration scoping thread).

```text
Test-Path -LiteralPath 'E:\GT-KB\bridge\gtkb-spec-lifecycle-schema-slice-1-002.md'
git status --short -- bridge/INDEX.md bridge/gtkb-spec-lifecycle-schema-slice-1-001.md bridge/gtkb-spec-lifecycle-schema-slice-1-002.md
```

Pre-filing drift result: `False` for the `-002` file path. Scoped git status showed `M bridge/INDEX.md` and `?? bridge/gtkb-spec-lifecycle-schema-slice-1-001.md`; no existing `-002` file.

## Prior Deliberations

- `DELIB-0707` supports the need for a real schema migration and makes deterministic backfill/provenance evidence relevant to review.
- `DELIB-1852` records the parent scoping GO. That GO is permissive only for follow-on slice proposals; it does not pre-approve implementation details that diverge from the operative parent contract.
- `DELIB-1853` records the earlier NO-GO on the same lifecycle-schema program, so this slice must preserve the revised parent constraints precisely.

## Findings

### F1 - P1 - Source-link table/API contract drifts from the parent GO

**Observation:** The parent operative proposal defines Slice 1's `specification_deliberation_sources` table with columns `spec_id`, `spec_version`, `deliberation_id`, `source_role`, `added_at`, `added_by`, and `UNIQUE(spec_id, spec_version, deliberation_id)` (`bridge/gtkb-spec-lifecycle-schema-2026-04-29-003.md` lines 72-83). It also names the later API method as `link_spec_deliberation_source` (`-003.md` lines 118-120), and Slice 4 assumes deliberation provenance lands in that same table (`-003.md` lines 126-130).

The Slice 1 proposal instead defines `specification_id`, `specification_version`, `deliberation_id`, `relationship`, and `created_at`, adds foreign keys, omits `added_by`, omits the unique constraint, and names the API `KnowledgeDB.link_specification_deliberation(...)` (`bridge/gtkb-spec-lifecycle-schema-slice-1-001.md` lines 87-100).

**Deficiency rationale:** This is not a harmless naming difference. The parent GO explicitly says each implementation slice needs its own proposal, but the parent remains the operative scoping contract (`bridge/gtkb-spec-lifecycle-schema-2026-04-29-004.md` lines 10-12). Implementing a different table shape now would force later slices to either follow the old parent vocabulary or the new Slice 1 vocabulary, creating schema/API ambiguity before the migration has even begun. The omitted `added_by` field and uniqueness constraint also reduce the auditability and idempotence of the deliberation-source relationship that the parent planned.

**Impact:** Prime could implement a table and method that pass the local Slice 1 tests but are incompatible with the approved Slice 2 and Slice 4 design. That would push drift into future bridge threads, making verification depend on unstated assumptions rather than the parent contract.

**Recommended action:** Revise the proposal to do one of the following:

1. Adopt the parent-approved table and API names exactly: `spec_id`, `spec_version`, `source_role`, `added_at`, `added_by`, `UNIQUE(spec_id, spec_version, deliberation_id)`, and `link_spec_deliberation_source`.
2. Or explicitly propose the schema/API contract change as part of this Slice 1 revision, including rationale, compatibility effects on Slice 2 and Slice 4, updated tests, and a statement that the parent scoping contract is being narrowed or amended for this table shape.

The minimal path is option 1 because it preserves the parent GO and avoids a second design decision in an implementation slice.

### F2 - P2 - Tracking work-item insertion is not fully verifiable

**Observation:** IP-4 says only "One `work_items` row: origin=`new`, component=`spec-lifecycle`, source_spec_id=`SPEC-LIFECYCLE-SCHEMA-MIGRATION`" (`bridge/gtkb-spec-lifecycle-schema-slice-1-001.md` lines 111-113). The current schema/API require additional fields for a valid work item, including `id`, `title`, `resolution_status`, `stage`, `changed_by`, `changed_at`, and `change_reason` (`groundtruth-kb/src/groundtruth_kb/db.py` lines 259-292; API arguments at lines 3260-3292). The verification plan only says "MemBase tracking WI inserted per IP-4" (`-001.md` lines 115-121).

**Deficiency rationale:** This leaves the KB mutation under-specified. Loyal Opposition cannot later verify that the correct tracking work item was inserted because the proposal does not define the expected row id/title/status/change reason or the read-back query/fixture assertion that proves it.

**Impact:** Prime could insert a technically valid but semantically untraceable tracking item, or choose field values that conflict with later project/backlog hygiene conventions.

**Recommended action:** In the revision, specify the exact work-item id, title, resolution status, stage, changed_by/change_reason convention, and the verification query or test assertion that proves the row exists exactly once with the expected fields.

## Decision Needed From Owner

None. This is a Prime Builder revision issue, not an owner-decision blocker.

## Revision Checklist

- Keep the mechanical preflights green.
- Align the table/API names with the parent GO, or explicitly amend the parent contract in this slice.
- Make the IP-4 work-item row fully machine-verifiable.
- Keep the populated-fixture migration test in scope.

