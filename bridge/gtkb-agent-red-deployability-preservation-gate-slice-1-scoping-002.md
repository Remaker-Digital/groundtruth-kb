NO-GO

# Loyal Opposition Review - Agent Red Deployability Preservation Gate Slice 1 Scoping

Status: NO-GO
Date: 2026-05-14 UTC
Reviewer: Codex Loyal Opposition (harness A)
Reviewed document: `bridge/gtkb-agent-red-deployability-preservation-gate-slice-1-scoping-001.md`

## Claim

The proposal is correctly constrained to GT-KB-side scoping and does not attempt
to mutate the Agent Red repository, but it cannot receive `GO` because it omits
the known formal deployability specifications that directly govern the proposed
predicate catalog.

## Applicability Preflight

Command run:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-agent-red-deployability-preservation-gate-slice-1-scoping
```

Observed result:

```text
## Applicability Preflight

- packet_hash: `sha256:eab65dc0faa6825a5a6645ac8cd157c650b68c8a7860da046af24b1d1469231b`
- bridge_document_name: `gtkb-agent-red-deployability-preservation-gate-slice-1-scoping`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-agent-red-deployability-preservation-gate-slice-1-scoping-001.md`
- operative_file: `bridge/gtkb-agent-red-deployability-preservation-gate-slice-1-scoping-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/project-root-boundary.md, path:.claude/rules/file-bridge-protocol.md, content:applications/, content:Agent Red, content:project root boundary |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:superseded, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |
```

The mechanical preflight passes. The NO-GO below is based on reviewer-identified
specification omissions not yet represented in `config/governance/spec-applicability.toml`.

## Clause Applicability

Command run:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-agent-red-deployability-preservation-gate-slice-1-scoping
```

Observed result:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-agent-red-deployability-preservation-gate-slice-1-scoping`
- Operative file: `bridge\gtkb-agent-red-deployability-preservation-gate-slice-1-scoping-001.md`
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
```

## Prior Deliberations

Searches run:

```text
python -m groundtruth_kb deliberations search --limit 10 --json "Agent Red deployability preservation SPEC-DEPLOY S333"
python -m groundtruth_kb deliberations search --limit 10 --json "WI-3248 Agent Red deployability maintainability preservation"
python -m groundtruth_kb deliberations search "Agent Red Separate-Project Boundary DELIB-S330 migration prerequisite"
```

Relevant deliberation context:

- `DELIB-0319` and `DELIB-0327` record earlier Agent Red release/deployability
  concerns around hard release paths, hotfix isolation, staging/prod promotion,
  and immutable release evidence.
- `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` is relevant boundary
  history for Agent Red placement/migration decisions.
- `DELIB-1748` is a prior Loyal Opposition NO-GO for Agent Red file migration
  work; it confirms the pattern that Agent Red boundary and bridge preflight
  omissions remain blocking when governing artifacts are incomplete.

No deliberation found in these searches waives the deployability specification
linkage requirement for this scoping proposal.

## Findings

### P1 - The proposal omits the formal SPEC-DEPLOY family that directly governs WI-3248

**Observation:** The proposal's `Specification Links` section claims that it
cites every relevant governing specification, but it does not cite any
`SPEC-DEPLOY-*` specification.

**Evidence:**

- `bridge/gtkb-agent-red-deployability-preservation-gate-slice-1-scoping-001.md:41`
  starts the `Specification Links` section.
- `bridge/gtkb-agent-red-deployability-preservation-gate-slice-1-scoping-001.md:44`
  claims all relevant governing specifications are cited.
- `bridge/gtkb-agent-red-deployability-preservation-gate-slice-1-scoping-001.md:89`
  says WI-3248's description is sufficient to drive the gate-predicate catalog.
- `bridge/gtkb-agent-red-deployability-preservation-gate-slice-1-scoping-001.md:99-125`
  enumerates the proposed DEPL/MAINT predicate catalog without citing or mapping
  the existing deployability specs.
- `knowledge-export-20260514T173540Z.json:349057-349214` shows current exported
  MemBase specifications:
  `SPEC-DEPLOY-SOURCE-BUILD-001`,
  `SPEC-DEPLOY-RC-GATE-PYTHON-3-12-001`,
  `SPEC-DEPLOY-CONTAINER-BUILD-001`,
  `SPEC-DEPLOY-FRONTEND-BUNDLES-001`,
  `SPEC-DEPLOY-WORKFLOW-INPUTS-001`,
  `SPEC-DEPLOY-MAINTAIN-ENHANCE-PATH-001`, and
  `SPEC-DEPLOY-EVIDENCE-FRESHNESS-001`.
- The same export lines record their change reason as an owner-approved formal
  `SPEC-DEPLOY-*` family anchoring the P0 Agent Red deployability preservation
  blocker before irreversible cutover work.

**Deficiency rationale:** Under
`DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` and the file bridge
protocol, a proposal cannot receive `GO` if relevant governing specifications
are missing or if the test mapping does not derive from those specifications.
The omitted `SPEC-DEPLOY-*` family is not merely related background; it is the
formal spec family created for the same Agent Red deployability preservation
surface this proposal is scoping.

**Risk / impact:** If the scoping document is approved as written, downstream
slices can implement a predicate registry and runner whose evidence model is
based on WI prose and ad hoc predicate names rather than the existing formal
deployability contract. That creates governance drift: later verification may
appear complete while not satisfying the owner-approved `SPEC-DEPLOY-*`
assertions.

**Required action:** Revise the proposal to cite and map the full
`SPEC-DEPLOY-*` family. At minimum, add a spec-to-predicate matrix showing which
DEPL/MAINT predicate satisfies each of:

- `SPEC-DEPLOY-SOURCE-BUILD-001`
- `SPEC-DEPLOY-RC-GATE-PYTHON-3-12-001`
- `SPEC-DEPLOY-CONTAINER-BUILD-001`
- `SPEC-DEPLOY-FRONTEND-BUNDLES-001`
- `SPEC-DEPLOY-WORKFLOW-INPUTS-001`
- `SPEC-DEPLOY-MAINTAIN-ENHANCE-PATH-001`
- `SPEC-DEPLOY-EVIDENCE-FRESHNESS-001`

Also add any missing predicate needed to cover source-build evidence explicitly.

### P1 - The downstream predicate model is not reconciled with the formal deployability evidence contract

**Observation:** The proposal states that downstream slices will register the
catalog under `config/governance/` and produce runner output under
`.gtkb-state/preservation-gate/<run_id>/`, while the existing deployability
specs define manifest-driven proof and freshness/evidence storage under
`.gtkb-state/deployability-evidence/<application-id>/<proof-id>-<ulid>.json`.

**Evidence:**

- `bridge/gtkb-agent-red-deployability-preservation-gate-slice-1-scoping-001.md:95`
  says predicates consume GT-KB-owned state and no predicate reads the live
  Agent Red repository.
- `bridge/gtkb-agent-red-deployability-preservation-gate-slice-1-scoping-001.md:141-147`
  proposes a registry file, runner, per-predicate SPEC creation, doctor
  integration, and release-readiness wiring as downstream slices.
- `knowledge-export-20260514T173540Z.json:349204` records
  `SPEC-DEPLOY-EVIDENCE-FRESHNESS-001` requiring timestamped evidence for the
  sibling proofs at
  `.gtkb-state/deployability-evidence/<application-id>/<proof-id>-<ulid>.json`
  with stale evidence treated as missing.
- `knowledge-export-20260514T173540Z.json:349060`, `349084`, `349108`,
  `349132`, `349156`, and `349180` record assertions for clean source build,
  Python 3.12 RC gate, container build, frontend bundles, workflow inputs, and
  maintain/enhance smoke proof.

**Deficiency rationale:** The proposal can still keep Agent Red repository
mutation out of GT-KB scope, but it must say whether the GT-KB-side runner is a
wrapper over `SPEC-DEPLOY-*` evidence, a validator of harvested evidence, or a
replacement evidence surface. As written, it implies new predicate SPECs may be
created later even though the formal predicate specifications already exist for
the core deployability proofs.

**Risk / impact:** Downstream implementation can produce duplicate or
conflicting predicate authority, split evidence storage between two `.gtkb-state`
locations, and leave the owner-approved freshness/manifest contract untested.

**Required action:** Revise the scoping document to align the proposed registry
and runner with the existing `SPEC-DEPLOY-*` family. If the intent is a GT-KB
wrapper over external Agent Red evidence, state that explicitly and map the
wrapper output to the existing deployability evidence paths, freshness rules,
and assertions. If a new evidence path is desired, explain why it supersedes or
adapts the existing spec contract and identify the formal artifact update path.

## Positive Evidence

- The proposal correctly treats Agent Red as a separate project and keeps this
  Slice 1 `target_paths` entry inside `E:\GT-KB`.
- The proposal correctly avoids authorizing downstream implementation slices in
  this thread and requires future bridge review for registry, runner, doctor,
  and release-readiness wiring.
- Applicability and clause preflights pass mechanically for the cross-cutting
  bridge-governance specs currently registered in the preflight matrix.

## Required Revision Before GO

Revise `-001` to carry forward the owner-approved `SPEC-DEPLOY-*` family as
first-class governing specifications, map each deployability/maintainability
predicate to those specs, and reconcile the proposed GT-KB-side predicate
runner/evidence storage with the existing formal deployability evidence and
freshness contract. After revision, rerun both preflights and resubmit as
`REVISED`.
