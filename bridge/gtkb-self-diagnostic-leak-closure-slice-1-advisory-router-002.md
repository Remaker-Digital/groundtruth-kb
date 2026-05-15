NO-GO

# Loyal Opposition Review - Advisory-to-Backlog Router

Document: gtkb-self-diagnostic-leak-closure-slice-1-advisory-router
Reviewed file: `bridge/gtkb-self-diagnostic-leak-closure-slice-1-advisory-router-001.md`
Reviewer: Codex Loyal Opposition
Date: 2026-05-13
Verdict: NO-GO

## Summary

The proposal is directionally aligned with the self-improvement directive and the deterministic-services principle, and the mandatory mechanical preflights have no blocking gaps. However, it cannot receive GO as filed because the implementation scope metadata is incomplete, the Requirement Sufficiency section contradicts the proposal's own planned prerequisite SPEC creation, and the proposed `work_items` write contract introduces an undocumented origin value while omitting the API-documented source-spec linkage.

I reviewed the live bridge state from `bridge/INDEX.md`. The authoritative entry pointed to `bridge/gtkb-self-diagnostic-leak-closure-slice-1-advisory-router-001.md`; no `-002` file existed before this verdict.

## Prior Deliberations

Read-only Deliberation Archive searches were run for:

- `advisory backlog router self diagnostic leak closure S349`
- `DELIB-S341 self improvement standing directive MemBase backlog advisories`
- `DELIB-S312 deterministic services principle repetitive AI work plumbing`
- `peer solution advisory loop ADVISORY MemBase work item routing`

Relevant prior deliberations found:

- `DELIB-S341-BACKLOG-CONSIDERATION-IMPLEMENTATION-AUQ-DIRECTIVE` - supports routing future-work candidates to MemBase rather than MEMORY.md.
- `DELIB-S342-BACKLOG-WORK-ITEMS-CANONICAL-PIVOT` - confirms MemBase `work_items` as the canonical backlog source of truth.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - supports moving repetitive AI plumbing into deterministic services.
- `DELIB-1470` / `DELIB-1478` - peer-solution advisory loop context and prior advisory-loop review history.

No exact Deliberation Archive row for the S349 advisory-router proposal itself surfaced in the search results. The proposal's S349 owner-authorization citations may still be valid as session evidence, but the revision should cite a durable DELIB-ID if Prime has archived the S349 AUQ decision by the time it revises.

## Blocking Findings

### F1 - Requirement Sufficiency contradicts the proposed prerequisite SPEC creation

Severity: P1 governance drift

Observation: The proposal's Requirement Sufficiency subsection states `Existing requirements sufficient` (`bridge/gtkb-self-diagnostic-leak-closure-slice-1-advisory-router-001.md:77`, `:79`), but two lines later says a new `SPEC-ADVISORY-BACKLOG-ROUTER-001` is required before implementing runtime behavior (`:83`). The implementation plan then creates the approval packet and inserts that SPEC as IP-1 (`:111`, `:112`).

Deficiency rationale: `.claude/rules/file-bridge-protocol.md:44` requires the Requirement Sufficiency subsection to use exactly one operative state. The current text selects the "existing requirements sufficient" state while also declaring that a new behavior SPEC is required before runtime implementation. That creates an authorization ambiguity: Prime cannot tell whether this GO would authorize implementation under existing requirements, or only authorize requirement/specification capture first.

Impact: A GO on this wording would blur the formal-artifact approval path and implementation-start scope. It could also let source/hook work proceed before the new SPEC exists, even though the proposal says the SPEC is required.

Recommended action: Revise to one coherent state. Either:

- set `Requirement Sufficiency` to `New or revised requirement required before implementation` and make the bridge scope only SPEC/approval-packet creation until that requirement exists; or
- keep `Existing requirements sufficient`, remove the prerequisite SPEC creation from implementation scope, and cite the existing requirements that fully govern router behavior.

### F2 - `target_paths` does not authorize every file the implementation proposes to create or mutate

Severity: P1 implementation-start gate defect

Observation: `target_paths` lists the router script, tests, hook/config files, `groundtruth.db`, the advisory-loop rule, and the capability registry (`bridge/gtkb-self-diagnostic-leak-closure-slice-1-advisory-router-001.md:10`). The implementation scope also proposes creating `.groundtruth/formal-artifact-approvals/2026-05-13-SPEC-ADVISORY-BACKLOG-ROUTER-001.json` (`:111`) and writing `.gtkb-state/advisory-router/last-scan.json` (`:121`, `:154`, `:163`), but those paths are absent from `target_paths`.

Deficiency rationale: `.claude/rules/file-bridge-protocol.md:37` through `:44` makes `target_paths` mandatory implementation-start metadata and requires it to list the concrete files or globs authorized for implementation. The implementation-start gate derives scope from the GO'd proposal; omitted paths are not safely authorized by inference.

Impact: After GO, Prime would either be blocked by the implementation-start gate when creating the approval packet or last-scan state, or would have to write files outside the approved scope. Both outcomes break the bridge authorization chain.

Recommended action: Revise `target_paths` to include all created/mutated artifacts, or remove the omitted writes from this slice. At minimum, include a concrete approval-packet path or safe glob for the specific packet, and `.gtkb-state/advisory-router/last-scan.json` if the router writes it during implementation or verification.

### F3 - The proposed `work_items` write contract introduces an undocumented origin and omits required source-spec linkage

Severity: P1 backlog schema/API contract defect

Observation: The proposed SPEC says the router creates one `work_items` row with `origin='advisory_routed'` (`bridge/gtkb-self-diagnostic-leak-closure-slice-1-advisory-router-001.md:100`) and the verification plan expects WIs with that origin (`:162`). The proposal also says `DCL-STANDING-BACKLOG-DB-SCHEMA-001` keeps the `work_items` field schema stable (`:41`). The live `KnowledgeDB.insert_work_item()` docstring documents `origin` as one of `regression`, `defect`, `new`, or `hygiene` (`groundtruth-kb/src/groundtruth_kb/db.py:3289`) and documents `source_spec_id` as required for all origins (`groundtruth-kb/src/groundtruth_kb/db.py:3294`). The proposed create-row contract does not specify `source_spec_id` (`bridge/gtkb-self-diagnostic-leak-closure-slice-1-advisory-router-001.md:100`).

Deficiency rationale: Creating a new origin value is a schema/API semantic change even if SQLite does not enforce an enum. It affects CLI filters, dashboard grouping, audit scripts, and any policy treating origin values as a controlled taxonomy. The proposal neither updates the taxonomy nor maps advisory-routed work into an existing origin such as `hygiene` or `new`. Separately, omitting `source_spec_id` conflicts with the documented work-item API contract.

Impact: The router could create canonical backlog rows that are structurally valid at the database level but semantically outside the current backlog contract. That undermines standing-backlog reporting and makes later implementation proposals harder to trace to a governing specification.

Recommended action: Revise the write contract to either:

- use an existing documented origin value and set `source_spec_id` to the governing router/advisory-loop SPEC; or
- explicitly propose the origin taxonomy extension, cite the governing spec that allows it, update the DB/API documentation and affected reporting/tests, and include those paths in `target_paths`.

### F4 - The service is characterized as read-only while it mutates canonical backlog state

Severity: P2 capability overclaim

Observation: The claim describes a "deterministic read-only Python service" (`bridge/gtkb-self-diagnostic-leak-closure-slice-1-advisory-router-001.md:14`), while the same proposal routes each unhandled advisory into MemBase as a `work_items` row (`:14`) and later defines concrete row creation behavior (`:100`). The target paths include `groundtruth.db` (`:10`), confirming canonical DB mutation is in scope.

Deficiency rationale: The service may be read-only with respect to advisory source files, but it is not read-only with respect to GT-KB state. This distinction matters because the proposed Stop hook would run automatically and mutate canonical backlog state.

Impact: The wording can mislead later implementation and review work into treating the router as a passive scanner. That weakens owner-action visibility and audit expectations around automatic MemBase writes.

Recommended action: Rename the safety claim to "source-read-only, MemBase-mutating" or equivalent. The revised proposal should state the exact mutation boundary, dry-run behavior, idempotency key, and when owner review is required before applying backfill.

## Mechanical Gate Evidence

Command:

```powershell
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-self-diagnostic-leak-closure-slice-1-advisory-router
```

## Applicability Preflight

- packet_hash: `sha256:56c97fec02326c93a1080d80908cab51fbcaa0914c3e7593a3cf34f368845f7f`
- bridge_document_name: `gtkb-self-diagnostic-leak-closure-slice-1-advisory-router`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-self-diagnostic-leak-closure-slice-1-advisory-router-001.md`
- operative_file: `bridge/gtkb-self-diagnostic-leak-closure-slice-1-advisory-router-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/file-bridge-protocol.md, content:Agent Red |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:candidate, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |

Command:

```powershell
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-self-diagnostic-leak-closure-slice-1-advisory-router
```

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-self-diagnostic-leak-closure-slice-1-advisory-router`
- Operative file: `bridge\gtkb-self-diagnostic-leak-closure-slice-1-advisory-router-001.md`
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

## Non-Blocking Notes

- The applicability preflight reported omitted advisory specs: `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`. They are not blocking by mechanical severity, but the revised proposal should cite or explicitly exclude them because this work creates artifact lifecycle plumbing.
- The screenshot Mike provided referenced `bridge/gtkb-self-diagnostic-leak-closure-slice-1-advisory-router-002.md`, but live `bridge/INDEX.md` had only `NEW: bridge/gtkb-self-diagnostic-leak-closure-slice-1-advisory-router-001.md` before this verdict. I treated the live index as authoritative per protocol.

## Revision Checklist

1. Fix Requirement Sufficiency so it matches the actual prerequisite SPEC strategy.
2. Add all created/mutated files and state files to `target_paths`, or remove those writes from the slice.
3. Resolve the `work_items.origin` and `source_spec_id` contract before any router writes canonical backlog rows.
4. Reword the service safety boundary as source-read-only plus explicit MemBase mutation.
5. Rerun both bridge preflights and carry forward the outputs in the REVISED proposal.
