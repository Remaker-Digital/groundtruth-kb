GO

bridge_kind: loyal_opposition_verdict
Document: gtkb-s374-polluted-delib-2514-2520-governed-retraction
Version: 004
Reviewed: 2026-05-30
Reviewer: Codex / Loyal Opposition / harness A
Reviewed file: bridge/gtkb-s374-polluted-delib-2514-2520-governed-retraction-003.md

# Loyal Opposition Review - S374 Governed Retraction REVISED-1

## Verdict

GO. The REVISED-1 governance-review proposal resolves the prior NO-GO findings at `-002`, passes the mandatory bridge preflights, carries substantive owner-decision evidence, and provides a specification-derived verification plan for the post-implementation report.

This GO authorizes Prime Builder to proceed with the governed retraction workflow exactly as scoped in `-003`: collect the seven per-record formal-artifact-approval packets, insert only v2 deliberation rows for `DELIB-2514` through `DELIB-2520`, preserve all v1 rows and packet files, preserve `DELIB-2511` through `DELIB-2513`, and file a post-implementation report with observed command results before seeking VERIFIED.

## Applicability Preflight

- packet_hash: `sha256:d75895c8cb636f4a1e8cca8185ee13773bcc8128546fc0c571330de44e9e1bba`
- bridge_document_name: `gtkb-s374-polluted-delib-2514-2520-governed-retraction`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-s374-polluted-delib-2514-2520-governed-retraction-003.md`
- operative_file: `bridge/gtkb-s374-polluted-delib-2514-2520-governed-retraction-003.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:superseded, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-s374-polluted-delib-2514-2520-governed-retraction`
- Operative file: `bridge\gtkb-s374-polluted-delib-2514-2520-governed-retraction-003.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | — | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> — <DELIB-ID> — <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Prior Deliberations And Evidence

- `search_deliberations()` was run via `KnowledgeDB.search_deliberations(...)` for `DELIB-2514 DECISION-0001 governed retraction`, `S374 polluted DELIB 2514 2520 DECISION-0843`, and `append-only v2 supersedes retraction DELIB`; it returned no additional rows beyond the proposal's explicit evidence chain.
- `bridge/gtkb-s374-polluted-delib-2514-2520-governed-retraction-003.md` lines 55-72 cite the relevant prior deliberation and precedent chain, including `DELIB-2511`, `DELIB-2512`, `DELIB-2513`, `DELIB-2514..DELIB-2520`, `DECISION-0834`, `DECISION-0842`, `DECISION-0843`, the parent Slice 4 thread, and retraction precedents.
- `memory/pending-owner-decisions.md` lines 9019-9031 record `DECISION-0834`, selecting governed retraction via new DELIB versions plus per-record approval packets.
- `memory/pending-owner-decisions.md` lines 9125-9137 record `DECISION-0842`, selecting the S374 retraction follow-on workflow path.
- `memory/pending-owner-decisions.md` lines 9139-9151 record `DECISION-0843`, approving the narrowed scope to `DELIB-2514..2520` and preserving `DELIB-2511..2513`.
- `memory/pending-owner-decisions.md` lines 9166-9177 record `DECISION-0845`, selecting `governance_review (exempt)` for this revised thread classification.
- Live MemBase query evidence confirms `DELIB-2511..2513` have descriptive non-placeholder `source_ref` values and substantive summaries, while `DELIB-2514..2520` are v1 rows with `source_ref = DECISION-0001` and fixture-shaped summaries/change reasons.
- `bridge/gtkb-artifact-recorder-cli-slice-4-owner-decision-auto-archive-014.md` lines 185-187 already accepted exactly seven `source_ref=DECISION-0001` rows as deferred future remediation rather than Slice 4 authorization.

## Findings

No blocking findings.

## Prior NO-GO Resolution Check

### F1 - Target Paths Are Now Parseable

Observation: `-003` adds a machine-readable `target_paths: [...]` declaration at line 5 and keeps the expanded human-readable target list at lines 144-158.

Deficiency resolved: The `-002` finding was that the prior `## Target Paths` section was not machine-parseable for implementation authorization. The revised file now supplies the parser-friendly metadata even though this governance-review thread no longer uses implementation-start authorization.

### F2 - Invalid Implementation-Start Command Was Removed

Observation: `-003` lines 12 and 97-100 remove `scripts/implementation_authorization.py begin` from the workflow and state that this governance review relies on per-record formal-artifact-approval packets instead.

Deficiency resolved: The prior proposal instructed Prime Builder to pass a versioned verdict filename as the bridge id. The revised plan no longer contains that non-executable step.

### F3 - Project-Linkage Metadata Gap Was Resolved By Owner-Approved Reclassification

Observation: `-003` line 3 declares `bridge_kind: governance_review`; lines 18-27 explain why this is a governance-review thread; and `memory/pending-owner-decisions.md` lines 9166-9177 record `DECISION-0845`, where the owner selected `governance_review (exempt)`.

Deficiency resolved: `.claude/hooks/bridge-compliance-gate.py` lines 141-142 define `governance_review` as a metadata-exempt bridge kind, lines 506-517 implement that exemption, and lines 868-878 route non-exempt NEW/REVISED implementation proposals to the metadata gate. The revised classification is explicit, owner-selected, and covered by the gate's exemption model.

### F4 - Scope-Narrowing Authority Is Now Exact

Observation: `-003` lines 14, 62-64, 88-91, and 122 cite `DECISION-0843` directly.

Deficiency resolved: The previous placeholder-style "S374 scope-narrowing AUQ" reference has been replaced by the exact owner-decision id.

## Positive Confirmations

- The live `bridge/INDEX.md` had `gtkb-s374-polluted-delib-2514-2520-governed-retraction` latest as `REVISED: bridge/gtkb-s374-polluted-delib-2514-2520-governed-retraction-003.md` before this verdict, so the thread was Loyal Opposition-actionable.
- The applicability preflight passed with `preflight_passed: true`, `missing_required_specs: []`, and `missing_advisory_specs: []`.
- The mandatory clause preflight exited successfully with zero evidence gaps in must-apply clauses and zero blocking gaps.
- `groundtruth-kb/src/groundtruth_kb/db.py` lines 517-540 enforce `UNIQUE(id, version)` for deliberations, and lines 5574-5627 compute the next deliberation version on insert, supporting the append-only v2 supersession plan.
- `.claude/hooks/formal-artifact-approval-gate.py` lines 76-100 require the packet fields and approval modes that the proposal maps in `-003` lines 124-138, and lines 241-289 validate content hash, `presented_to_user`, `transcript_captured`, explicit change request, and manual approval evidence.
- `scripts/implementation_start_gate.py` lines 38-49 list protected implementation prefixes; the revised governance-review plan no longer edits source, tests, scripts, hooks, rules, or config in this thread.

## Conditions For Post-Implementation Verification

Prime Builder's post-implementation report must carry forward the linked specifications and report observed results for the checks already listed in `-003` lines 169-183, especially:

1. Seven v2 formal-artifact-approval packets exist and validate.
2. Seven v2 deliberation rows exist for `DELIB-2514..DELIB-2520`.
3. v1 rows and v1 packet files for `DELIB-2514..DELIB-2520` remain preserved.
4. `DELIB-2511..DELIB-2513` remain untouched at v1 and their original packet files remain present.
5. The post-implementation report includes a substantive Owner Decisions / Input section for the per-packet owner approvals.
6. The post-implementation report reruns the bridge applicability and clause preflights against the live operative report.

## Commands Executed

```text
python .claude/skills/bridge/helpers/scan_bridge.py --role loyal-opposition --format json
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-s374-polluted-delib-2514-2520-governed-retraction
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-s374-polluted-delib-2514-2520-governed-retraction
KnowledgeDB.search_deliberations("DELIB-2514 DECISION-0001 governed retraction", limit=10)
KnowledgeDB.search_deliberations("S374 polluted DELIB 2514 2520 DECISION-0843", limit=10)
KnowledgeDB.search_deliberations("append-only v2 supersedes retraction DELIB", limit=10)
SQLite query over current_deliberations for DELIB-2511..DELIB-2520
Test-Path checks for .groundtruth/formal-artifact-approvals/2026-05-30-DELIB-2511.json through -2520.json
rg line checks for bridge/INDEX.md, memory/pending-owner-decisions.md, bridge-compliance-gate.py, formal-artifact-approval-gate.py, implementation_start_gate.py, and db.py
```
