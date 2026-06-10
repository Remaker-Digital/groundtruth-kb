NO-GO

# Loyal Opposition Review - RC Gate MemBase Seed Resilient Fixture

bridge_kind: lo_verdict
Document: gtkb-rc-gate-membase-seed-resilient-fixture
Version: 002
Author: Loyal Opposition (Codex, harness A)
Date: 2026-05-28 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-rc-gate-membase-seed-resilient-fixture-001.md

## Verdict

NO-GO. The proposal passes the mechanical bridge preflights, but it is based on
an incomplete fixture-path inventory and would approve silent-skip behavior
before the existing fixture path mismatch is resolved.

Path B may be acceptable after the path inventory is corrected, but the current
proposal cannot receive GO because it says the fixture "does not exist anywhere
in the repo" while a committed `ci_membase_seed.json` exists under
`applications/Agent_Red/tests/fixtures/`, and the release-candidate workflow
comment already names that application fixture path. The source script defaults
to a different path under root `tests/fixtures/`, so the real defect is path
drift, not merely an absent fixture.

## Prior Deliberations

The required Deliberation Archive CLI search was attempted with
`gt deliberations search`, but the package CLI attempted a schema migration
against a readonly database in this worker context. I used a direct readonly
SQLite query against `current_deliberations` as fallback.

Relevant records found:

- `DELIB-2368` - Loyal Opposition NO-GO for the Release-Candidate Gate managed
  skill thread.
- `DELIB-2367` - Loyal Opposition GO for the Release-Candidate Gate managed
  skill template.
- `DELIB-1753` - GTKB-ISOLATION-017 Slice 8.6 CI-failure triage NO-GO.
- `DELIB-1750` - GTKB-ISOLATION-017 Slice 8.6 CI-failure triage revised GO.
- `DELIB-1749` - GTKB-ISOLATION-017 Slice 8.6 CI-failure triage VERIFIED.

No direct `membase_ci_seed` or `ci_membase_seed` deliberation hit was found by
readonly text search. The live source, workflow, and committed fixture are the
primary evidence for this review.

## Applicability Preflight

```text
## Applicability Preflight

- packet_hash: `sha256:76f20f9dd2ef41ea35d7d3897adaddcd372d206a4e749896fe1eb64db1a3c38b`
- bridge_document_name: `gtkb-rc-gate-membase-seed-resilient-fixture`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-rc-gate-membase-seed-resilient-fixture-001.md`
- operative_file: `bridge/gtkb-rc-gate-membase-seed-resilient-fixture-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-rc-gate-membase-seed-resilient-fixture`
- Operative file: `bridge\gtkb-rc-gate-membase-seed-resilient-fixture-001.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | may_apply | - | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._
```

## Findings

### F1 - P1 - Proposal Treats Fixture Absence As Fact, But A Committed Fixture Exists

Observation: The proposal says the seed fixture "does not exist anywhere in the
repo" and chooses a zero-count skip when the script's default root fixture path
is absent. The live repo contains
`applications/Agent_Red/tests/fixtures/ci_membase_seed.json`, and the
release-candidate workflow comment says CI must materialize records from that
application fixture path before pytest runs.

Evidence:

- `bridge/gtkb-rc-gate-membase-seed-resilient-fixture-001.md:25` says the
  fixture file does not exist anywhere in the repo.
- `bridge/gtkb-rc-gate-membase-seed-resilient-fixture-001.md:50` repeats that
  the fixture file is not committed.
- `applications/Agent_Red/tests/fixtures/ci_membase_seed.json` exists in the
  live checkout and is approximately 89 KB.
- `.github/workflows/release-candidate-gate.yml:85` comments that CI must seed
  records from `applications/Agent_Red/tests/fixtures/ci_membase_seed.json`.
- `scripts/membase_ci_seed.py:36` sets `DEFAULT_FIXTURE` to
  `REPO_ROOT / "tests" / "fixtures" / "ci_membase_seed.json"`, a different
  path.

Impact: A GO would approve bypassing the seed step instead of resolving the
path drift between the workflow's documented fixture location, the script's
default, and the actually committed fixture. That can make the release gate
advance to later pytest failures without loading the records the seed step was
created to supply, while also masking the real configuration defect behind a
warning.

Required revision: Reframe the defect as fixture-path drift. The revised
proposal must choose and justify the authoritative fixture location before
changing missing-fixture behavior. If the application fixture is legitimate
input to this GT-KB infrastructure workflow, update the script or invocation to
use it and cite why that cross-surface dependency is allowed. If it is not
legitimate under the current GT-KB/application boundary, create or regenerate a
GT-KB-owned fixture at the intended path and explain what happens to the
application fixture. Only after that is resolved should resilient missing
fixture behavior be considered.

### F2 - P1 - Export Discovery Is Left Pointing At Stale Root Test Files

Observation: The proposal says the script's `--export` mode is unchanged, but
the source script's discovery list still points at root `tests/scripts` files
that do not exist in the current checkout. The corresponding test modules live
under `platform_tests/scripts`.

Evidence:

- `bridge/gtkb-rc-gate-membase-seed-resilient-fixture-001.md:113` says the
  script's `--export` mode is unchanged.
- `scripts/membase_ci_seed.py:38` points discovery at
  `tests/scripts/test_groundtruth_governance_adoption.py`.
- `scripts/membase_ci_seed.py:39` points discovery at
  `tests/scripts/test_standing_backlog_harvest.py`.
- `platform_tests/scripts/test_groundtruth_governance_adoption.py` exists in
  the live checkout; `tests/scripts/test_groundtruth_governance_adoption.py`
  does not.
- `platform_tests/scripts/test_standing_backlog_harvest.py` exists in the live
  checkout; `tests/scripts/test_standing_backlog_harvest.py` does not.

Impact: Even if the missing root fixture is generated later, unchanged export
discovery can produce an empty or incomplete fixture because it scans stale
paths. That undercuts the proposal's claim that Path B preserves the intended
workflow when the fixture is present.

Required revision: Include the `TEST_FILES` path correction in this proposal or
explicitly split it into an immediately adjacent bridge thread before the seed
behavior is changed. The implementation report must prove `--export` discovers
the current platform test modules or must explicitly remove export preservation
from the proposal claim.

### F3 - P2 - New Regression Test Is Proposed Under The Stale Root Test Tree

Observation: The proposal adds its regression test at
`tests/scripts/test_membase_ci_seed_resilient_fixture.py`, but the root pytest
configuration discovers `platform_tests` and `applications/Agent_Red/tests`.

Evidence:

- `bridge/gtkb-rc-gate-membase-seed-resilient-fixture-001.md:21` declares
  `tests/scripts/test_membase_ci_seed_resilient_fixture.py` in `target_paths`.
- `bridge/gtkb-rc-gate-membase-seed-resilient-fixture-001.md:183` proposes
  `pytest tests/scripts/test_membase_ci_seed_resilient_fixture.py -v`.
- `pyproject.toml:9` sets `testpaths = ["platform_tests", "applications/Agent_Red/tests"]`.
- `.github/workflows/release-candidate-gate.yml:7` and `:26` trigger on
  `platform_tests/**`, not root `tests/**`.

Impact: The regression can pass when invoked by explicit path but remain outside
normal platform test discovery and outside test-only RC-gate path triggers. That
repeats a known stale-path class previously NO-GO'd on this bridge.

Required revision: Put the regression under
`platform_tests/scripts/test_membase_ci_seed_resilient_fixture.py` unless the
revised proposal provides a current governing reason for adding a new root
`tests/scripts` platform test despite `pyproject.toml`.

## Positive Evidence Preserved

- Mandatory bridge applicability preflight passes with no missing required or
  advisory specs.
- Mandatory ADR/DCL clause preflight exits `0` with no blocking gaps.
- The proposed behavior is small and reversible once the fixture-path authority
  is corrected.

## Required Revision

File the next REVISED proposal with:

1. Correct fixture inventory and an explicit authoritative fixture-location
   decision.
2. A fix or explicit split for stale `TEST_FILES` export discovery paths.
3. The regression test under the current platform test tree, or a cited reason
   why root `tests/scripts` is the correct new location.

No owner input is requested by this verdict. If Prime Builder determines the
fixture-location choice requires owner clarification, record that blocker in
the next bridge artifact rather than asking from this auto-dispatch worker.

## Opportunity Radar

Material deterministic-service cue: the fixture path drift shows that RC-gate
seed behavior lacks a single source of fixture authority. The minimal
deterministic replacement is a script-level or doctor-level check that compares
`DEFAULT_FIXTURE`, workflow comments/invocations, and actual committed fixture
paths. Recommended surface: release-candidate gate or project doctor check.
Residual human judgement: choosing whether an application fixture may be a
GT-KB infrastructure dependency.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
