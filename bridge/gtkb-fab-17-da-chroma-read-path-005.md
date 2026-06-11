NO-GO

bridge_kind: loyal_opposition_review
Document: gtkb-fab-17-da-chroma-read-path
Version: 005
Author: loyal-opposition (Codex, harness A)
Date: 2026-06-11 UTC
Responds-To: bridge/gtkb-fab-17-da-chroma-read-path-004.md

# Corrective Loyal Opposition Review - FAB-17 DA/Chroma Read Path

## Review Scope

Reviewed the full FAB-17 bridge thread after a concurrent Loyal Opposition
verdict filed `bridge/gtkb-fab-17-da-chroma-read-path-004.md` as GO:

- `bridge/gtkb-fab-17-da-chroma-read-path-001.md`
- `bridge/gtkb-fab-17-da-chroma-read-path-002.md`
- `bridge/gtkb-fab-17-da-chroma-read-path-003.md`
- `bridge/gtkb-fab-17-da-chroma-read-path-004.md`

This corrective review is filed because the `-003` proposal still does not
cover all live Chroma duplicate-store paths named by the source hygiene
finding and required by the prior NO-GO.

## Same-Session Guard

This Loyal Opposition session did not author the proposal under review or the
concurrent `GO -004` verdict. The operative revision was authored by Prime
Builder, harness B, session `9660f4cb-1b84-410e-a024-febdabe7c541`. The
concurrent GO was authored by Loyal Opposition (Antigravity, harness C).

## Applicability Preflight

Command:

```powershell
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-fab-17-da-chroma-read-path
```

Observed output:

```text
## Applicability Preflight

- packet_hash: `sha256:ea9ce347d8c0b0bf676be0bd3e7460a2acf5a8f277bb1f6472f3af62f8203dd8`
- bridge_document_name: `gtkb-fab-17-da-chroma-read-path`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-fab-17-da-chroma-read-path-003.md`
- operative_file: `bridge/gtkb-fab-17-da-chroma-read-path-003.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

Command:

```powershell
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-fab-17-da-chroma-read-path
```

Observed output:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-fab-17-da-chroma-read-path`
- Operative file: `bridge\gtkb-fab-17-da-chroma-read-path-003.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |
```

## Prior Deliberations

- `DELIB-FAB17-REMEDIATION-20260610`: owner decision batch for DA/Chroma
  read-path reliability, benchmark CLI repair, and Chroma triplication
  resolution. Direct DB read reports outcome `owner_decision`, work item
  `WI-4429`, session `S430`.
- `DELIB-FABLE-GRILL-20260610-Q1..Q7`: project-chartering decisions cited by
  the proposal and backlog item.

## Authority Check

Direct read from `groundtruth.db` confirmed:

- `PAUTH-FAB17-20260610` is active for `PROJECT-FABLE-INVESTIGATION`, includes
  `WI-4429`, and allows DA read-path source edits, benchmark CLI source edits,
  Chroma index deduplication, and test additions.
- The same PAUTH forbids push/deploy, external Agent Red repository mutation,
  and canonical MemBase/DA record mutation.
- `WI-4429` exists, is open/backlogged, has no `depends_on_work_items` or
  `blocks_work_items`, and is linked to
  `bridge/gtkb-fable-investigation-advisory-001.md`.

## Blocking Finding

### F1 - Chroma dedup target_paths still omit two live duplicate stores

`bridge/gtkb-fab-17-da-chroma-read-path-002.md` required the revised proposal
to either:

1. add concrete target paths for the canonical Chroma index and every duplicate
   index path/glob to be removed or consolidated; or
2. defer Chroma deduplication to a separate bridge item.

`bridge/gtkb-fab-17-da-chroma-read-path-003.md` adds only
`.groundtruth-chroma/**` to `target_paths`, then narrows Area 3 to duplicate
removal "within `.groundtruth-chroma/**`." That does not cover the actual
duplicate-store topology named by the source hygiene report and present on
disk.

Source finding evidence:

- `independent-progress-assessments/GT-KB-ARCHITECTURE-HYGIENE-INVESTIGATION-2026-06-10.md`
  names "Three ChromaDB stores on disk: canonical .groundtruth-chroma ... plus
  two stray default-path instances at root chroma/ and
  groundtruth-kb/.groundtruth-chroma".

Live path evidence:

```text
.groundtruth-chroma exists=True is_dir=True
chroma exists=True is_dir=True
groundtruth-kb/.groundtruth-chroma exists=True is_dir=True
```

Because the proposal neither includes `chroma/**` and
`groundtruth-kb/.groundtruth-chroma/**` nor explicitly defers those duplicate
stores, it still cannot satisfy the prior NO-GO requirement. Prime Builder
would be authorized only to touch `.groundtruth-chroma/**`, leaving two live
duplicate Chroma stores unresolved despite the proposal claiming Chroma
triplication resolution.

## Required Revision

Submit a REVISED proposal that either:

1. adds matcher-valid target paths for every live Chroma store involved in
   deduplication, including `chroma/**` and
   `groundtruth-kb/.groundtruth-chroma/**`, with verification that canonical
   `groundtruth.db` / DA records remain unmutated; or
2. explicitly defers all out-of-`.groundtruth-chroma/**` duplicate-store
   cleanup to a separate bridge item and narrows FAB-17's acceptance criteria
   accordingly.

The revision should preserve the benchmark-path correction, the Chroma
fallback/timeout scope, and the prohibition on canonical MemBase/DA mutation.

## Opportunity Radar

- Defect pass: the duplicate-store target-path perimeter remains incomplete.
- Token-savings pass: no new separate advisory; the issue is a target-path
  lint gap inside the active bridge workflow.
- Deterministic-service pass: proposal lint could enumerate live non-temp
  Chroma stores when a proposal claims Chroma deduplication, then require
  coverage or explicit deferral.
- Surface eligibility: draft-linter or target-path preflight; residual human
  judgement is classifying fixture/temp stores as out of scope.
- Routing: no new advisory filed; this should ride the active lint/preflight
  improvement lane already represented in the FABLE campaign.

## Verdict

NO-GO. This corrective verdict supersedes the concurrent `GO -004` as the
latest bridge state because the Chroma deduplication target-path blocker
remains unresolved.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
