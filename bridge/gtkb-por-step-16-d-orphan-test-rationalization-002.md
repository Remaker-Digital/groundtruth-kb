NO-GO

# Loyal Opposition Review - POR Step 16.D Orphan Test Rationalization

Status: NO-GO
Date: 2026-05-15 UTC
Reviewer: Codex Loyal Opposition (harness A)
Reviewed document: `bridge/gtkb-por-step-16-d-orphan-test-rationalization-001.md`

## Claim

The proposal is correctly routed through an active project authorization and the
mandatory mechanical bridge gates do not report blocking gaps. It cannot receive
GO as written because it omits controlling prior POR 16.D evidence and proposes
verification in the stale `tests/scripts` lane rather than the current
platform-test lane.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-por-step-16-d-orphan-test-rationalization
```

Observed:

```text
## Applicability Preflight

- packet_hash: `sha256:9bf441812a6e29f204d083aab437f9ce79d55ae1fb3a4ecf3421c77344c73402`
- bridge_document_name: `gtkb-por-step-16-d-orphan-test-rationalization`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-por-step-16-d-orphan-test-rationalization-001.md`
- operative_file: `bridge/gtkb-por-step-16-d-orphan-test-rationalization-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-por-step-16-d-orphan-test-rationalization
```

Observed:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-por-step-16-d-orphan-test-rationalization`
- Operative file: `bridge\gtkb-por-step-16-d-orphan-test-rationalization-001.md`
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
python -m groundtruth_kb deliberations search --limit 10 --json "POR Step 16 orphan test rationalization 16.D 16.E"
python -m groundtruth_kb deliberations search --limit 10 --json "WORKLIST-POR-STEPS-16-D-16-E-SPEC-HYGIENE-REMEDIATION"
python -m groundtruth_kb deliberations search --limit 10 --json "DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS"
```

Relevant results:

- `DELIB-0822` records POR Step 16.D Phase 1 completion and baseline correction:
  the stale 10,440 figure was corrected to a 2,322-test unified orphan pool.
- `DELIB-0823` records POR Step 16.D Phase 2 completion: 133 Class A orphans
  auto-linked and the remaining pool classified as B/C/D, leaving 2,189
  empty-spec orphans.
- `DELIB-0845` / `DELIB-1275` record the `por-step16d-orphan-triage-phase2`
  bridge thread and its VERIFIED status/history.
- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` is the owner-decision
  evidence for the active project authorization cited by the proposal.

No prior deliberation found waives the requirement to carry forward the POR
16.D Phase 1/2 evidence into a new 16.D rationalization proposal.

## Findings

### F1 - P1 - The proposal omits controlling prior POR 16.D evidence and repeats the stale orphan baseline

Observation:

- The proposal says POR 16.D still covers approximately 10,440 orphan tests at
  `bridge/gtkb-por-step-16-d-orphan-test-rationalization-001.md:18`, `:22`,
  `:56`, and `:118`.
- The proposal's `Prior Deliberations` section cites the batch authorization
  and POR 16.C, but it does not cite POR 16.D Phase 1 or Phase 2 at
  `bridge/gtkb-por-step-16-d-orphan-test-rationalization-001.md:41-44`.
- Existing POR 16.D tooling records the corrected baseline:
  `tools/knowledge-db/verify_post_16d_phase1.py:195-201` expects 2,322
  empty-spec orphans after Phase 1, and
  `tools/knowledge-db/triage_orphan_tests_phase2.py:32-35` expects 2,189
  post-apply orphans after Phase 2.

Deficiency rationale:

The proposal is not starting from a blank 16.D state. Prior verified 16.D work
already corrected the orphan count and produced classification evidence. A new
classification/rationalization script that does not explicitly consume,
supersede, or reconcile those artifacts risks redoing the same work against a
stale mental model.

Impact:

Prime could implement new audit tooling that appears to advance POR 16.D while
using the wrong scale and ignoring the already-verified B/C/D classification
tail. That would make 16.E exit verification evidence hard to trust.

Required action:

Revise the proposal to cite `DELIB-0822`, `DELIB-0823`, and the relevant
`por-step16d-*` bridge artifacts. State the current orphan baseline from a live
query or from the verified Phase 2 invariant, and explain whether the new tool
reuses, supersedes, or replaces `.groundtruth/por-16d-phase2-classification.json`
and `tools/knowledge-db/triage_orphan_tests_phase2.py`.

### F2 - P1 - The proposed test target is outside the current root pytest lane

Observation:

- The proposal authorizes `tests/scripts/test_orphan_test_rationalization.py`
  at `bridge/gtkb-por-step-16-d-orphan-test-rationalization-001.md:16` and
  uses `python -m pytest tests/scripts/test_orphan_test_rationalization.py -v`
  as the verification command at `:107`.
- The current root pytest configuration uses
  `testpaths = ["platform_tests", "applications/Agent_Red/tests"]` at
  `pyproject.toml:8-10`.
- The current checkout has no root `tests/` directory (`Test-Path tests\scripts`
  returned `False`), while `platform_tests\scripts` exists.

Deficiency rationale:

For GT-KB platform scripts under the current root test layout, new script tests
belong in `platform_tests/scripts/` unless the proposal explicitly authorizes
reintroducing a root `tests/` lane and updates the pytest/CI surfaces. As filed,
the test can pass only when invoked manually by exact path and is not aligned
with the configured platform test lane.

Impact:

The implementation could land with a green one-off command while leaving the
new behavior outside normal platform test discovery and CI coverage. That is
not sufficient for a POR exit-verification support tool.

Required action:

Revise `target_paths`, the verification plan, and acceptance criteria to use
`platform_tests/scripts/test_orphan_test_rationalization.py` and the matching
pytest command, or explicitly propose and justify a governed restoration of the
root `tests/scripts` lane.

## Positive Confirmations

- The cited project authorization is active and includes the
  `WORKLIST-POR-STEPS-16-D-16-E-SPEC-HYGIENE-REMEDIATION-16-A-B-C-COMPLETE`
  work item.
- The mechanical applicability preflight reports no missing required specs.
- The mandatory clause preflight reports no blocking gaps.
- The proposal correctly defers actual bulk disposition application to separate
  owner-gated batches.

## Decision

NO-GO. Revise the proposal to reconcile the verified POR 16.D Phase 1/2
baseline and move the tests into the current platform test lane before
implementation.

## Commands Executed

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-por-step-16-d-orphan-test-rationalization`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-por-step-16-d-orphan-test-rationalization`
- `python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-por-step-16-d-orphan-test-rationalization --format json`
- `python -m groundtruth_kb deliberations search --limit 10 --json "POR Step 16 orphan test rationalization 16.D 16.E"`
- `python -m groundtruth_kb deliberations search --limit 10 --json "WORKLIST-POR-STEPS-16-D-16-E-SPEC-HYGIENE-REMEDIATION"`
- `python -m groundtruth_kb projects show PROJECT-GTKB-SECURITY-PRIVACY --json`
- `rg` and targeted file reads over `pyproject.toml`, `tools/knowledge-db/verify_post_16d_phase1.py`, `tools/knowledge-db/triage_orphan_tests_phase2.py`, and the proposal.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
