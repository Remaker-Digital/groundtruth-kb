NO-GO

# Loyal Opposition Review - Zero-Knowledge Architecture Phase 4 Scoping

Reviewed: `bridge/gtkb-zero-knowledge-architecture-phase-4-scoping-001.md`
Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-15 UTC
Verdict: NO-GO

## Claim

The proposal is not ready for implementation. The mechanical preflights pass,
but the proposal would start Phase 4 scoping/source work while the current
work-item record says Phase 4 depends on substantial POR Step 16 completion and
the POR Step 16.D/16.E dependency is still open. The proposed verification plan
also lacks an executable package test for the new planner module.

## Review Scope

- Read live `bridge/INDEX.md` before acting. Latest status for this document was
  `NEW: bridge/gtkb-zero-knowledge-architecture-phase-4-scoping-001.md`.
- Read the full thread version chain; only `-001` exists.
- Resolved durable role from `harness-state/harness-identities.json` and
  `harness-state/role-assignments.json`: Codex harness `A` is assigned
  `loyal-opposition`.
- Read required bridge review rules:
  `.claude/rules/file-bridge-protocol.md`,
  `.claude/rules/codex-review-gate.md`,
  `.claude/rules/deliberation-protocol.md`,
  `.claude/rules/operating-model.md`,
  `.claude/rules/loyal-opposition.md`, and
  `.claude/rules/report-depth-prime-builder-context.md`.
- Searched the Deliberation Archive for the ZK specs and inspected current
  work-item dependency state.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-zero-knowledge-architecture-phase-4-scoping
```

Observed:

```text
## Applicability Preflight

- packet_hash: `sha256:a294d85b43a07d01292a008577a1dfe00607f25bfb5d6df5ea11d919be9743fc`
- bridge_document_name: `gtkb-zero-knowledge-architecture-phase-4-scoping`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-zero-knowledge-architecture-phase-4-scoping-001.md`
- operative_file: `bridge/gtkb-zero-knowledge-architecture-phase-4-scoping-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:deferred, content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:* |
```

The advisory omissions should be fixed in the revision, especially
`GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, but they are not the blocking basis for
this NO-GO because the preflight reports `missing_required_specs: []`.

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-zero-knowledge-architecture-phase-4-scoping
```

Observed:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-zero-knowledge-architecture-phase-4-scoping`
- Operative file: `bridge\gtkb-zero-knowledge-architecture-phase-4-scoping-001.md`
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

## Prior Deliberations

Deliberation Archive searches were run through `KnowledgeDB.search_deliberations`
and `KnowledgeDB.get_deliberations_for_spec` against the active `groundtruth.db`
/ `.groundtruth-chroma` surfaces.

Relevant results:

- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` records the batch-5 project
  grouping authorization and says bridge proposals were not filed in that batch.
- Spec-linked DA lookups for the cited ZK/security specs returned existing
  context, including `DELIB-0542`, `DELIB-0510`, `DELIB-0504`, `DELIB-0503`,
  and `DELIB-0195` for `SPEC-1843`; `DELIB-0195` for `SPEC-1844`;
  `DELIB-0314` for `SPEC-1644`; and `DELIB-0194`, `DELIB-0187`,
  `DELIB-0186`, `DELIB-0185`, and `DELIB-0116` for `SPEC-1840`.

The proposal cites only the S350 batch authorization in `## Prior
Deliberations`. The revision should carry forward the relevant ZK/spec-linked
deliberation context or explain why it is not relevant to the Phase 4 scoping
slice.

## Findings

### F1 - Phase 4 prerequisite is still open

Severity: P1 dependency / sequencing failure; blocking.

Observation: the proposal acknowledges that Phase 4 has the prerequisite "POR
Step 16 substantially complete" while proposing a Phase 4 scoping document and
planner module:
`bridge/gtkb-zero-knowledge-architecture-phase-4-scoping-001.md:16-18` and
`:70-78`. The current MemBase work-item row for
`WORKLIST-ZERO-KNOWLEDGE-ARCHITECTURE-PHASE-4-LONGER-TERM` reports
`stage=backlogged`, `status_detail=Longer-term architecture item; prerequisites
include substantial POR Step 16 completion`, and dependency
`WORKLIST-POR-STEPS-16-D-16-E-SPEC-HYGIENE-REMEDIATION-16-A-B-C-COMPLETE`.
That dependency is also `stage=backlogged` with status detail "Open POR
follow-up: 16.A/16.B/16.C verified; 16.D orphan test rationalization and 16.E
exit verification remain." A live bridge entry for that dependency is still
`NEW: bridge/gtkb-por-step-16-d-orphan-test-rationalization-001.md`.

Deficiency rationale: the proposal has a planner that would report
`ready=False`, but the bridge `GO` would still authorize Phase 4 artifacts under
`docs/` and `groundtruth-kb/src/`. That is not just read-only prerequisite
inspection; it is the first source/documentation implementation slice of the
Phase 4 program.

Impact: a `GO` would start the longer-term ZK Phase 4 program before the
recorded POR prerequisite is complete, and before the active POR 16.D/16.E
bridge thread has even received Loyal Opposition review.

Required action: revise after POR Step 16.D/16.E has completion evidence, or
cite an explicit owner decision that authorizes this specific pre-prerequisite
Phase 4 scoping slice despite the open dependency. If Prime only wants a
read-only prerequisite-status report, narrow the proposal to that report and
avoid creating Phase 4 source modules until the dependency is satisfied.

### F2 - The verification plan does not include an executable test for the new package module

Severity: P1 verification-plan failure; blocking.

Observation: the proposal targets a new package module at
`groundtruth-kb/src/groundtruth_kb/security/zk_phase_4_planner.py` but has no
test file in `target_paths`:
`bridge/gtkb-zero-knowledge-architecture-phase-4-scoping-001.md:16`. The
verification plan uses grep, import smoke, and a manual current-state check:
`bridge/gtkb-zero-knowledge-architecture-phase-4-scoping-001.md:79-90`.
`groundtruth-kb/pyproject.toml` defines the package test root as `tests` and
Python path as `src`: `groundtruth-kb/pyproject.toml:72-73`.

Deficiency rationale: DCL-verified spec-derived testing requires tests or
verification procedures derived from linked specs and executed against the
implementation. A new planner module with prerequisite and sequencing logic
should have executable fixture-based tests for ready/blocked states and
`next_phase()` behavior, not only an import smoke test and manual observation.

Impact: the implementation could receive a post-implementation report with no
repeatable regression coverage for the module's core decisions, leaving Phase 4
sequencing dependent on manual review each time.

Required action: add an explicit package test target such as
`groundtruth-kb/tests/security/test_zk_phase_4_planner.py`, include it in
`target_paths`, and update the command to run the package test lane from
`groundtruth-kb` or with the appropriate package pytest invocation.

### F3 - Prior ZK/spec deliberation context is not carried forward

Severity: P2 review-context gap.

Observation: the proposal cites the four ZK/security specs and the S350 batch
authorization, but its Prior Deliberations section cites only the S350 batch
authorization:
`bridge/gtkb-zero-knowledge-architecture-phase-4-scoping-001.md:30-47`. Direct
DA spec-link lookups found prior deliberations for all four cited specs,
including the DELIB IDs listed above.

Deficiency rationale: Loyal Opposition is required to question cited
requirements and disambiguate owner intent. For a multi-phase zero-knowledge
program, prior review context around tenant data access, key access, key
identity, and origin restriction is part of the requirement interpretation
surface.

Impact: the scoping document could restate the four specs as labels without
carrying forward the earlier review findings and rejected/accepted constraints
that shaped them.

Required action: cite the relevant spec-linked deliberations in the revised
proposal, or explicitly explain why the prior records are out of scope for this
Phase 4 scoping slice.

## Required Revised Proposal Evidence

Prime Builder should file
`bridge/gtkb-zero-knowledge-architecture-phase-4-scoping-003.md` as `REVISED`
only after:

1. Showing POR Step 16.D/16.E completion evidence or explicit owner
   authorization to start this Phase 4 scoping slice before that dependency is
   complete.
2. Adding executable package tests for the planner module and updating the
   `target_paths` plus verification command accordingly.
3. Carrying forward relevant ZK/spec-linked prior deliberations or documenting
   why they are out of scope.
4. Rerunning both bridge preflights against the revised operative file.

No owner decision is required from this verdict. The current bridge result is
NO-GO.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
