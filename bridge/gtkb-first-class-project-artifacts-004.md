GO

# Loyal Opposition Review - First-Class Project Artifacts Without Backlog Authority Drift

bridge_kind: loyal_opposition_verdict
Document: gtkb-first-class-project-artifacts
Version: 004
Reviewer: Codex (harness A, Loyal Opposition dispatch mode)
Date: 2026-05-12 UTC
Reviewed: `bridge/gtkb-first-class-project-artifacts-003.md`
Prior NO-GO: `bridge/gtkb-first-class-project-artifacts-002.md`
Verdict: GO

## Claim

The revised proposal closes the three prior blocking findings and is approved for implementation within the revised scope.

This GO authorizes a first-class project layer over the existing MemBase `work_items` / `current_work_items` backlog authority. It does not authorize a `backlog_items` table, a wrapper queue table, a `subjects` table in Slice 1, formal GOV/ADR/DCL/SPEC/rule mutation without approval packets, or any replacement of the existing `application`, `platform`, `hosted application`, or `work subject` terminology.

## Prior Deliberations

Required deliberation searches were performed before review:

```text
$env:PYTHONPATH='groundtruth-kb/src'; $env:PYTHONIOENCODING='utf-8'; python -c "from groundtruth_kb.cli import main; main()" deliberations search "first class project artifacts work_items current_work_items subject project backlog" --limit 8
$env:PYTHONPATH='groundtruth-kb/src'; $env:PYTHONIOENCODING='utf-8'; python -c "from groundtruth_kb.cli import main; main()" deliberations search "DELIB-S342-BACKLOG-WORK-ITEMS-CANONICAL-PIVOT work_items current_work_items backlog_items never existed" --limit 6
```

Relevant results:

- `DELIB-S342-BACKLOG-WORK-ITEMS-CANONICAL-PIVOT` - owner directive that MemBase `work_items` is the canonical backlog source of truth and the pivot away from a separate `backlog_items` table is ratified.
- `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE` - predecessor owner directive for formal backlog DB schema work, now constrained by the S342 pivot.
- `DELIB-1791` and `DELIB-1790` - prior Loyal Opposition NO-GO reviews on backlog source-of-truth, including the `work_items` versus `backlog_items` identity problem.
- `DELIB-0839` - standing backlog harvest snapshot and reconciliation obligations.
- `DELIB-S341-BACKLOG-CONSIDERATION-IMPLEMENTATION-AUQ-DIRECTIVE` - future-work candidates flow to MemBase `work_items` / `current_work_items`; implementation approval remains AUQ-protected.

No deliberation result rejects first-class project artifacts. The controlling constraint is that project artifacts must extend current backlog authority unless a separate owner-approved supersession is proposed.

## Applicability Preflight

Command:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-first-class-project-artifacts
```

Observed:

- packet_hash: `sha256:ba45dea5e64cc246ee27313f5d8a066f2df7d0bc86fdbc1609f8bc6fadd1007d`
- bridge_document_name: `gtkb-first-class-project-artifacts`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-first-class-project-artifacts-003.md`
- operative_file: `bridge/gtkb-first-class-project-artifacts-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:Agent Red |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:blocked, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

Command:

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-first-class-project-artifacts
```

Observed:

- Bridge id: `gtkb-first-class-project-artifacts`
- Operative file: `bridge\gtkb-first-class-project-artifacts-003.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory. Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

## Review Results

### C1 - Backlog authority drift is closed

Observation: the revised proposal makes `work_items` / `current_work_items` non-negotiable backlog authority and explicitly excludes `backlog_items`, `backlog_entries`, wrapper queue tables, and alternate canonical backlog work-record tables.

Evidence:

- `bridge/gtkb-first-class-project-artifacts-003.md:18` says no `backlog_items` table, queue, or authority path is proposed.
- `bridge/gtkb-first-class-project-artifacts-003.md:30` says projects are an organizing and planning layer, not a replacement backlog authority.
- `bridge/gtkb-first-class-project-artifacts-003.md:90-94` defines the non-negotiable backlog authority and requires separate formal supersession for any future rankable queue table.
- `bridge/gtkb-first-class-project-artifacts-003.md:122-130` keeps Slice 1 implementation over `work_items` / `current_work_items` and forbids `backlog_items` or equivalent wrapper queue tables.

Impact: the prior P1 authority conflict is closed.

### C2 - Owner input section is exact and substantive

Observation: the revised proposal uses the exact required heading `## Owner Decisions / Input`.

Evidence:

- `bridge/gtkb-first-class-project-artifacts-003.md:66` contains the exact heading.
- `bridge/gtkb-first-class-project-artifacts-003.md:68-78` preserves the owner-direction evidence and correctly states it is direct chat evidence, not AskUserQuestion evidence or a formal artifact approval packet.

Impact: the bridge owner-input gate is satisfied for this proposal.

### C3 - Subject schema implementation is deferred

Observation: Slice 1 no longer creates a schema-level `Subject` artifact. The proposal requires terminology/governance disambiguation before any future subject table.

Evidence:

- `bridge/gtkb-first-class-project-artifacts-003.md:106-118` defines `Subject Deferral` and disambiguation requirements.
- `bridge/gtkb-first-class-project-artifacts-003.md:129` says Slice 1 does not create a `subjects` table.
- `bridge/gtkb-first-class-project-artifacts-003.md:142-146` requires a separate terminology/governance proposal before subject schema work.
- `bridge/gtkb-first-class-project-artifacts-003.md:151` lists `Creating a subjects table in Slice 1` as out of scope.

Impact: the prior P2 terminology/schema ambiguity is closed for the approved Slice 1 scope.

## GO Conditions

Implementation is approved with these constraints:

- Keep `work_items` and `current_work_items` as canonical backlog work-record authority.
- Do not create `backlog_items`, `backlog_entries`, or any equivalent wrapper queue/work-record authority.
- Do not create a `subjects` table in Slice 1.
- Before any future subject schema work, file a terminology/governance proposal that disambiguates `Subject` from `application`, `platform`, `hosted application`, and `work subject`, with applicable approval evidence for formal artifact mutations.
- Carry forward the proposal's spec-derived tests, especially `T-work-items-authority`, `T-many-to-many`, `T-project-dependencies`, `T-artifact-links`, `T-compat-migration`, `T-no-subject-table`, and `T-reporting`.
- Produce migration/backfill evidence before converting existing `project_name` / `subproject_name` strings into first-class project records.
- Preserve bulk-operation visibility: any migration or backfill that converts existing backlog/project strings must produce an inventory artifact, a review packet, and a `DECISION DEFERRED` marker for any unresolved conversion, retirement, compatibility, or formal-artifact-approval decision.

## Owner Action

None.

File bridge scan contribution: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
