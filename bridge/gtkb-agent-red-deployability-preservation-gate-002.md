NO-GO

# Loyal Opposition Review - Agent Red Deployability Preservation Gate

Status: NO-GO
Date: 2026-05-15 UTC
Reviewer: Codex Loyal Opposition (harness A)
Reviewed document: `bridge/gtkb-agent-red-deployability-preservation-gate-001.md`

## Claim

The proposal is correctly owner-authorized as GT-KB scope through the
`PROJECT-GTKB-ADOPTER-EXPERIENCE` amendment, and the mandatory mechanical
bridge gates do not report blocking gaps. It cannot receive GO because the
proposed gate is narrower than the owner-approved WI-3248 deployability
contract and omits the existing `SPEC-DEPLOY-*` family that directly governs
this work.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-agent-red-deployability-preservation-gate
```

Observed:

```text
## Applicability Preflight

- packet_hash: `sha256:0cd1e5878553ff3fffd05ddbe2424c7595ece8cce2b7c0dcc218574c487898fd`
- bridge_document_name: `gtkb-agent-red-deployability-preservation-gate`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-agent-red-deployability-preservation-gate-001.md`
- operative_file: `bridge/gtkb-agent-red-deployability-preservation-gate-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:applications/, content:Agent Red |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:* |
```

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-agent-red-deployability-preservation-gate
```

Observed:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-agent-red-deployability-preservation-gate`
- Operative file: `bridge\gtkb-agent-red-deployability-preservation-gate-001.md`
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
python -m groundtruth_kb deliberations search --limit 10 --json "WI-3248 Agent Red deployability preservation SPEC-DEPLOY"
python -m groundtruth_kb deliberations search --limit 10 --json "gtkb-agent-red-deployability-preservation-gate-slice-1-scoping NO-GO SPEC-DEPLOY"
python -m groundtruth_kb deliberations search --limit 10 --json "DELIB-S350-BATCH6-P0P1-AUTHORIZATION"
```

Relevant context:

- `DELIB-S350-BATCH6-P0P1-AUTHORIZATION` confirms the owner authorized adding
  `WI-3248` to `PROJECT-GTKB-ADOPTER-EXPERIENCE` as GT-KB platform scope.
- `DELIB-0319` and `DELIB-0327` remain relevant Agent Red deployability
  history around hard release paths, staging/prod promotion, and artifact-lane
  proof.
- The prior local bridge verdict
  `bridge/gtkb-agent-red-deployability-preservation-gate-slice-1-scoping-002.md`
  already NO-GO'd the same family for omitting the `SPEC-DEPLOY-*` specs. No
  relevant deliberation found in this review waives that requirement.

## Findings

### F1 - P1 - The proposal omits the existing SPEC-DEPLOY family that directly governs WI-3248

Observation:

- The proposal's `Specification Links` section at
  `bridge/gtkb-agent-red-deployability-preservation-gate-001.md:28-39` cites no
  `SPEC-DEPLOY-*` specs.
- The owner-approved `WI-3248` packet says deployability preservation must prove
  the release-candidate path, Python 3.12 gate, frontend/admin/widget build
  surfaces, Docker/container build surfaces, deployment workflow
  inputs/artifacts, and a safe maintain/enhance smoke path at
  `.groundtruth/formal-artifact-approvals/2026-05-05-wi-3248-agent-red-preservation-gate.json:6`.
- The owner-approved deployability spec batch lists
  `SPEC-DEPLOY-SOURCE-BUILD-001`,
  `SPEC-DEPLOY-RC-GATE-PYTHON-3-12-001`,
  `SPEC-DEPLOY-CONTAINER-BUILD-001`,
  `SPEC-DEPLOY-FRONTEND-BUNDLES-001`,
  `SPEC-DEPLOY-WORKFLOW-INPUTS-001`,
  `SPEC-DEPLOY-MAINTAIN-ENHANCE-PATH-001`, and
  `SPEC-DEPLOY-EVIDENCE-FRESHNESS-001` at
  `.groundtruth/formal-artifact-approvals/2026-05-04-spec-deploy-family-batch.json:4-15`.
- The prior local scoping review required the same family to be cited and mapped
  at `bridge/gtkb-agent-red-deployability-preservation-gate-slice-1-scoping-002.md:109-164`.

Deficiency rationale:

Under `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` and the file
bridge protocol, a proposal cannot receive GO when relevant governing
specifications are missing or the proposed tests do not derive from those
specifications. The `SPEC-DEPLOY-*` family was created for this exact
deployability-preservation surface, so it is not optional background.

Impact:

Approving this proposal would allow implementation against a reduced four-check
interpretation of WI-3248 while bypassing the formal deployability evidence
contract already approved by the owner.

Required action:

Revise the proposal to cite the full `SPEC-DEPLOY-*` family and add a
spec-to-check/test matrix showing how each deployability spec is satisfied by
the library, CLI, fixtures, and acceptance criteria.

### F2 - P1 - The proposed checks are materially narrower than WI-3248 and the deployability spec family

Observation:

- The proposal defines four checks at
  `bridge/gtkb-agent-red-deployability-preservation-gate-001.md:22`:
  release-candidate path, Python gate, frontend build path, and test suite
  collection.
- The proposed library returns only `check_rc_gate`, `check_python_gate`,
  `check_frontend_build_path`, and `check_test_suite_collects` at
  `bridge/gtkb-agent-red-deployability-preservation-gate-001.md:75-80`.
- The proposed test map at
  `bridge/gtkb-agent-red-deployability-preservation-gate-001.md:96-104` lacks
  tests for source build artifacts, Docker/container build proof, deployment
  workflow input/artifact discovery, maintain/enhance smoke proof, and evidence
  freshness.

Deficiency rationale:

`WI-3248` and the `SPEC-DEPLOY-*` family define a deployability-preservation
contract broader than "RC gate + Python + frontend + pytest collection." A
test-collection check is useful, but it is not a substitute for source-build,
container-build, workflow-input, maintain/enhance, and evidence-freshness
proofs.

Impact:

The new gate could pass while Agent Red remains non-deployable by the owner-
approved criteria. That is the exact failure class WI-3248 exists to prevent
before irreversible adopter migration or restructuring work.

Required action:

Either expand this implementation slice to cover all required proofs or narrow
the proposal title and claim to an explicitly partial slice with downstream
threads for the missing proofs. If sliced, state which `SPEC-DEPLOY-*` specs are
covered now, which are intentionally deferred, and what prevents irreversible
work until the full preservation gate exists.

### F3 - P2 - The command-surface claim and target paths do not match

Observation:

- The proposal claims it will build a `gt adopter deployability-check` command
  at `bridge/gtkb-agent-red-deployability-preservation-gate-001.md:22`.
- `target_paths` at
  `bridge/gtkb-agent-red-deployability-preservation-gate-001.md:16` authorize
  only a new adoption library, a root script wrapper, and one test file. They do
  not authorize the package CLI registry where a `gt ...` command would be
  wired.
- The proposed CLI section at
  `bridge/gtkb-agent-red-deployability-preservation-gate-001.md:86-88` describes
  only `python scripts/adopter_deployability_check.py --adopter-root <path>`.

Deficiency rationale:

The implementation scope can be either a root script wrapper or a first-class
`gt` command, but the proposal currently claims both while authorizing only the
script-wrapper path. This matters because CLI registry changes are protected
implementation paths and need explicit target authorization and tests.

Impact:

Prime could either implement less than the proposal claims or modify additional
CLI package files outside the GO'd target list. Both outcomes weaken the
implementation-start gate.

Required action:

Revise the scope. If this slice creates only the script wrapper, remove the
`gt adopter deployability-check` claim. If this slice creates a real `gt`
subcommand, add the concrete CLI package target paths and CLI-command tests.

### F4 - P2 - The proposed test target is outside the current root pytest lane

Observation:

- The proposal authorizes `tests/scripts/test_adopter_deployability_check.py`
  at `bridge/gtkb-agent-red-deployability-preservation-gate-001.md:16` and
  uses `python -m pytest tests/scripts/test_adopter_deployability_check.py -v`
  at `:106`.
- The current root pytest configuration uses
  `testpaths = ["platform_tests", "applications/Agent_Red/tests"]` at
  `pyproject.toml:8-10`.
- The current checkout has no root `tests/` directory (`Test-Path tests\scripts`
  returned `False`), while `platform_tests\scripts` exists.

Deficiency rationale:

For GT-KB platform root scripts under the current test layout, new tests should
land in `platform_tests/scripts/` unless the proposal explicitly restores a
root `tests/` lane and updates CI/test discovery.

Impact:

A one-off manual pytest target can pass while normal platform discovery and CI
miss the new deployability-gate tests.

Required action:

Revise `target_paths`, verification plan, and acceptance criteria to use
`platform_tests/scripts/test_adopter_deployability_check.py`, or explicitly
propose and justify a governed restoration of the root `tests/scripts` lane.

## Positive Confirmations

- The cited project authorization
  `PAUTH-PROJECT-GTKB-ADOPTER-EXPERIENCE-ADOPTER-EXPERIENCE-BATCH-P0-DEPLOYABILITY-GATE`
  is active and includes `WI-3248`.
- `DELIB-S350-BATCH6-P0P1-AUTHORIZATION` confirms the owner-authorized GT-KB
  platform scope for this WI despite its legacy Agent Red release-readiness
  project name.
- The mechanical applicability preflight reports no missing required specs.
- The mandatory clause preflight reports no blocking gaps.

## Decision

NO-GO. Revise the proposal to cite and map the `SPEC-DEPLOY-*` family, cover or
explicitly slice the full WI-3248 deployability contract, reconcile the CLI
claim with target paths, and move tests into the current platform test lane.

## Commands Executed

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-agent-red-deployability-preservation-gate`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-agent-red-deployability-preservation-gate`
- `python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-agent-red-deployability-preservation-gate --format json`
- `python -m groundtruth_kb deliberations search --limit 10 --json "WI-3248 Agent Red deployability preservation SPEC-DEPLOY"`
- `python -m groundtruth_kb deliberations search --limit 10 --json "gtkb-agent-red-deployability-preservation-gate-slice-1-scoping NO-GO SPEC-DEPLOY"`
- `python -m groundtruth_kb deliberations search --limit 10 --json "DELIB-S350-BATCH6-P0P1-AUTHORIZATION"`
- `python -m groundtruth_kb projects show PROJECT-GTKB-ADOPTER-EXPERIENCE --json`
- `python -m groundtruth_kb projects authorizations PROJECT-GTKB-ADOPTER-EXPERIENCE --json`
- `rg` and targeted file reads over the proposal, `pyproject.toml`, `.groundtruth/formal-artifact-approvals/2026-05-04-spec-deploy-family-batch.json`, and `.groundtruth/formal-artifact-approvals/2026-05-05-wi-3248-agent-red-preservation-gate.json`.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
