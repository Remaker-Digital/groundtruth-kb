NO-GO

bridge_kind: lo_verdict
Document: gtkb-tafe-dual-write-slice-b-shadow-ingestion
Version: 002
Author: Loyal Opposition (Codex, harness A)
author_identity: loyal-opposition/codex
author_harness_id: A
reviewed_document: bridge/gtkb-tafe-dual-write-slice-b-shadow-ingestion-001.md
Date: 2026-06-13 UTC

# NO-GO - WI-4508 Shadow Bridge-to-TAFE Ingestion

## Verdict

NO-GO. The proposal is directionally within the owner-authorized WI-4508 to
WI-4510 cutover envelope, but this specific slice is not safe to implement as
filed. The blockers are scope collision and missing implementation contract, not
missing owner authorization.

## Applicability Preflight

Command:

```powershell
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-tafe-dual-write-slice-b-shadow-ingestion
```

Output:

```text
## Applicability Preflight

- packet_hash: `sha256:154b95857b1a07b9ece2690dcc40ca7357818d1fed9817317541bd51a7c5d693`
- bridge_document_name: `gtkb-tafe-dual-write-slice-b-shadow-ingestion`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-tafe-dual-write-slice-b-shadow-ingestion-001.md`
- operative_file: `bridge/gtkb-tafe-dual-write-slice-b-shadow-ingestion-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []
```

## Clause Applicability

Command:

```powershell
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-tafe-dual-write-slice-b-shadow-ingestion
```

Output:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-tafe-dual-write-slice-b-shadow-ingestion`
- Operative file: `bridge\gtkb-tafe-dual-write-slice-b-shadow-ingestion-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.
```

## Prior Deliberations And Related Work

- `DELIB-20263195` - owner AUQ authorizing the full TAFE cutover sequence WI-4508, WI-4509, WI-4510, with each WI/slice still requiring bridge proposal, Loyal Opposition GO, implementation report, and VERIFIED.
- `bridge/gtkb-tafe-dual-write-index-parity-004.md` - accepted Slice A revised proposal, which explicitly deferred Slice B as bridge-document to TAFE ingestion plus lost-block detection and stated the Slice-B ingestion mapping plus lost-block oracle requires design review/ADR before implementation.
- `bridge/gtkb-tafe-dual-write-index-parity-006.md` and `-007.md` - implementation report and VERIFIED verdict preserving the Slice A/Slice B boundary and the absent-from-text lost-block deferral.
- Concurrent live proposal: `bridge/gtkb-tafe-dual-write-slice-b-oracle-001.md`, also declaring WI-4508 Slice B, overlapping `groundtruth-kb/src/groundtruth_kb/cli.py`, and explicitly re-scoping Slice B to the read-only lost-block oracle while deferring ingestion to a later Slice C.

## Findings

### F1 - Two live proposals claim the same WI-4508 Slice B lane

Observation: `bridge/INDEX.md` currently contains two latest `NEW` WI-4508
proposals:

- `gtkb-tafe-dual-write-slice-b-shadow-ingestion-001.md`
- `gtkb-tafe-dual-write-slice-b-oracle-001.md`

Both are authored by Prime Builder harness B, both cite the same PAUTH and
WI-4508, both call themselves Slice B, and both include
`groundtruth-kb/src/groundtruth_kb/cli.py` in `target_paths`. They define
different ordering semantics: this proposal implements bridge-to-TAFE shadow
ingestion now, while the oracle proposal says Slice B should be the read-only
lost-block oracle and the ingestion mapping should be a later Slice C.

Deficiency rationale: Loyal Opposition cannot approve two conflicting Slice B
definitions for the same work item and shared CLI surface. That would create
duplicate effort and an immediate merge/design conflict for Prime Builder. It
also makes later verification ambiguous: a terminal result for one Slice B would
not prove the other Slice B's acceptance criteria.

Required correction: Prime Builder must choose one active Slice B definition and
withdraw or revise the other. If ingestion remains desired, refile it with a
distinct slice name/order after the lost-block oracle and ADR/design-constraint
question are settled.

### F2 - The accepted Slice A boundary required a design review/ADR before ingestion

Observation: The accepted Slice A thread states that the deferred Slice B
included the bridge-document to TAFE flow/artifact mapping plus lost-block
detection, and that this follow-on required design review/ADR before
implementation. The verified source also says absent-from-text lost-block
detection requires an external expected-document oracle and is deferred to
Slice B.

Deficiency rationale: This proposal moves directly into TAFE writes and
structural parity without carrying the external lost-block oracle and without
the promised design constraint/ADR for mapping bridge thread history into TAFE
flow/stage records. The PAUTH allows dual-write work, but the prior accepted
slice boundary added a design-quality condition before that write surface is
implemented.

Required correction: Either implement the read-only oracle first and defer
ingestion, or revise the ingestion proposal to cite and satisfy the design
constraint/ADR requirement, including why ingestion can safely proceed before or
alongside lost-block completeness.

### F3 - The ingestion design lacks a replay-safe idempotence contract

Observation: The proposal says ingestion creates a flow instance for each
`DocumentBlock` and a stage instance for each version line. Current TAFE runtime
APIs (`FlowRuntimeService.create_flow_instance`, `create_stage_instance`) append
versioned rows under caller-supplied ids, while the schema uniqueness is on
`(id, version)` rather than `(subject_id, flow_definition_id)` or
`(flow_instance_id, stage_id, stage_index)`. The proposal does not define stable
ids, upsert/update semantics, duplicate handling, or a repeat-ingest test.

Deficiency rationale: A shadow ingestion command for a live canonical index will
be run more than once. Without deterministic ids and replay semantics, repeated
ingests can append duplicate flow/stage versions or create ambiguous parity
results. A parity checker that only proves "there exists a matching flow/stage"
does not prove "there is exactly one canonical representation and no stale
duplicate shadow state."

Required correction: The revised proposal must specify deterministic flow and
stage ids, define replay/upsert semantics, and add tests proving repeated
ingest of the same parsed index is idempotent or intentionally versioned with no
duplicate-current-state ambiguity.

## Required Revisions

- Resolve the live duplicate Slice B collision with
  `gtkb-tafe-dual-write-slice-b-oracle`.
- Reconcile the proposal with the accepted Slice A design boundary that tied
  ingestion mapping to lost-block oracle/design review.
- Add an explicit replay/idempotence contract for TAFE flow/stage writes and
  tests for repeated ingestion.
- Keep the irreversible cutover and authoritative generated INDEX writer out of
  scope, as already stated.

## Non-Blocking Notes

- Mechanical applicability and clause preflights passed.
- `DELIB-20263195` and the active PAUTH authorize WI-4508 work in general; this
  NO-GO does not challenge the owner authorization, only this slice shape.
- The `bridge_proposal_wi_id_collision_check.py` command reported cited IDs
  WI-4507, WI-4509, and WI-4510 as non-declared collisions. In this review those
  are treated as related sequencing context, not as standalone blockers.

## Commands Executed

```powershell
python .claude\skills\bridge\helpers\show_thread_bridge.py gtkb-tafe-dual-write-slice-b-shadow-ingestion --format json
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-tafe-dual-write-slice-b-shadow-ingestion
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-tafe-dual-write-slice-b-shadow-ingestion
python scripts\bridge_proposal_wi_id_collision_check.py --content-file bridge\gtkb-tafe-dual-write-slice-b-shadow-ingestion-001.md --declared-wi WI-4508
python -m groundtruth_kb.cli deliberations get DELIB-20263195
python -m groundtruth_kb.cli projects show PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE --json
rg -n "Slice-B ingestion mapping|lost-block|external oracle|Slice B" bridge\gtkb-tafe-dual-write-index-parity-006.md bridge\gtkb-tafe-dual-write-index-parity-007.md bridge\gtkb-tafe-dual-write-index-parity-004.md
rg -n "def create_flow_instance|class FlowRuntimeService|flow_instances|subject_id|UNIQUE" groundtruth-kb\src\groundtruth_kb groundtruth-kb\tests
```

## Owner Action Required

None.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
