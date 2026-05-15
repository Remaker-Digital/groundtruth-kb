NO-GO

# Loyal Opposition Review - Proposal-Standards Test-Claim Re-Run Verifier

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-14 UTC
Reviewed proposal: `bridge/gtkb-proposal-standards-test-claim-rerun-verifier-001.md`
Verdict: NO-GO

## Claim

The proposal cannot receive GO because its implementation scope does not match
the operative Slice 2 work item. Slice 2 is specifically about parsing claimed
`pytest` output blocks in post-implementation reports and re-running the same
commands in a fixture environment to catch stale or false pass claims. The
proposal instead targets bridge proposals, parses planned test names from
`Specification-Derived Verification Plan` sections, verifies that test functions
exist, and optionally runs `pytest -k <name>`. That is a different verifier and
does not satisfy the stated Slice 2 outcome.

## Prior Deliberations

Deliberation search was run before review:

`python -m groundtruth_kb deliberations search "proposal standards test claim rerun verifier Slice 2" --limit 8`

Relevant records:

- `DELIB-0991` - prior Loyal Opposition review of
  `gtkb-gov-proposal-standards-slice1`, relevant parent-thread context.
- `DELIB-1667`, `DELIB-1806`, `DELIB-1852` - proposal/review history with
  related bridge and verification concerns surfaced by semantic search.

The work-item text in `memory/work_list.md` is more directly controlling for
this Slice 2 scope than the semantic deliberation hits.

## Findings

### FINDING-P1-001 - Proposed verifier checks the wrong artifact and the wrong claim type

Observation:
The Slice 2 backlog entry requires a verifier for claimed `pytest` output blocks
in post-implementation reports. The proposal instead reads bridge proposals,
locates verification-plan sections, extracts `test_*` names, and reports whether
test functions are found.

Evidence:

- `memory/work_list.md:1340` through `:1342` defines Slice 2 as parsing
  claimed pytest output blocks in post-implementation reports and re-running
  the same commands, failing when real output diverges.
- `memory/work_list.md:1363` through `:1368` repeats the required outcome:
  parse claimed `pytest` output blocks in post-implementation reports, re-run
  the same commands in a fixture environment, and fail the pre-commit gate when
  real output diverges from claimed output.
- The proposal's summary says it parses `pytest` claims out of bridge
  proposals' `Specification-Derived Verification Plan` sections at
  `bridge/gtkb-proposal-standards-test-claim-rerun-verifier-001.md:18`.
- The proposal's CLI behavior verifies test existence and optionally runs
  `pytest -k <name>` at
  `bridge/gtkb-proposal-standards-test-claim-rerun-verifier-001.md:22`.
- The detailed scope reads `bridge/<bridge-id>-NNN.md`, locates
  `Specification-Derived Verification Plan`, extracts names matching
  `test_[a-z0-9_]+`, and emits `{claim, found, file}` at
  `bridge/gtkb-proposal-standards-test-claim-rerun-verifier-001.md:62` through
  `:69`.

Deficiency rationale:
Pre-implementation proposals often list planned tests that do not exist yet and
do not claim an observed pytest outcome. The stale-claim risk Slice 2 is meant
to close is in post-implementation reports that assert command output already
occurred. A test-name existence checker over proposal plans would not catch the
explicit regression described in the work item: a report claiming "44 tests
pass" when the live run had failures.

Impact:
GO would authorize a tool that can pass its own tests while leaving the actual
failure mode unaddressed. Prime could later claim Slice 2 is implemented even
though stale pytest-output blocks in post-implementation reports still are not
mechanically re-run and compared.

Recommended action:
Revise the proposal so the tool:

1. targets post-implementation reports, not ordinary implementation proposals;
2. parses fenced or indented command/output blocks for explicit `pytest`
   invocations and claimed observed results;
3. re-runs the same command in a controlled in-root fixture environment;
4. compares observed exit code/output summary to the claimed output; and
5. includes the stale "44 tests pass" vs "7 failed, 16 passed" regression as a
   fixture.

### FINDING-P2-002 - Verification plan omits the stated gate behavior and one authorized test surface

Observation:
The proposal's test plan covers parsing tables/inline mentions, locating test
functions, missing-test reporting, strict-mode pytest per claim, and JSON schema.
It does not test post-implementation report output-block parsing, same-command
re-run behavior, fixture-environment isolation, output-divergence failure, or
pre-commit gate integration. The target paths also include
`platform_tests/scripts/test_bridge_proposal_test_claim_verifier.py`, but the
only run command executes `tests/scripts/test_bridge_proposal_test_claim_verifier.py`.

Evidence:

- Target paths include both root `tests/scripts/...` and
  `platform_tests/scripts/...` at
  `bridge/gtkb-proposal-standards-test-claim-rerun-verifier-001.md:16`.
- The proposed verification table at
  `bridge/gtkb-proposal-standards-test-claim-rerun-verifier-001.md:75` through
  `:85` covers only extraction/location/strict-mode/schema behaviors.
- The run command at
  `bridge/gtkb-proposal-standards-test-claim-rerun-verifier-001.md:87` executes
  only `tests/scripts/test_bridge_proposal_test_claim_verifier.py`.
- Read-only filesystem check during review found no root `tests` directory in
  the current checkout, while `platform_tests/scripts` exists and is the
  established location for root-script tests.

Deficiency rationale:
The bridge review gate requires tests derived from the linked specifications and
work-item behavior. The listed tests do not exercise the central required
outcome, and the command does not cover one of the authorized test paths. The
proposal also authorizes creating a root `tests` tree without explaining why the
existing `platform_tests/scripts` convention is insufficient.

Impact:
Post-implementation verification would have no mechanical evidence that the
tool handles the real stale-output claim mode. It would also have an ambiguous
test surface split between an absent root `tests` tree and existing
`platform_tests`.

Recommended action:
Revise the test plan around the actual output-block verifier:

- parse post-implementation report command/output blocks;
- re-run the exact command in an in-root fixture workspace;
- fail on output summary divergence;
- pass on matching output;
- reject unsafe/out-of-root commands;
- cover pre-commit gate invocation or explicitly defer gate wiring to a named
  follow-on slice; and
- execute the actual test file path(s) listed in `target_paths`.

## Applicability Preflight

- packet_hash: `sha256:6273bbb25202a443035374a19a36ce010c75b3573da9c147a196a37ad098123c`
- bridge_document_name: `gtkb-proposal-standards-test-claim-rerun-verifier`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-proposal-standards-test-claim-rerun-verifier-001.md`
- operative_file: `bridge/gtkb-proposal-standards-test-claim-rerun-verifier-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-proposal-standards-test-claim-rerun-verifier`
- Operative file: `bridge\gtkb-proposal-standards-test-claim-rerun-verifier-001.md`
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

## Verification Performed

- `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-proposal-standards-test-claim-rerun-verifier` - PASS; no missing required specs.
- `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-proposal-standards-test-claim-rerun-verifier` - PASS; zero blocking gaps.
- `python -m groundtruth_kb deliberations search "proposal standards test claim rerun verifier Slice 2" --limit 8` - completed; relevant records listed above.
- Read `memory/work_list.md`, the proposal, and current target-path state.
- `Test-Path tests` - missing.
- `Test-Path platform_tests\scripts` - present.

## Required Revision

File `bridge/gtkb-proposal-standards-test-claim-rerun-verifier-003.md` as
REVISED. Align the scope with the actual Slice 2 work item: post-implementation
report pytest-output blocks, same-command re-run, fixture-environment isolation,
divergence failure, and a regression for the stale "44 tests pass" claim. Also
make the target paths and pytest command match the actual test surface.

No owner decision is required from Loyal Opposition at this stage.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
