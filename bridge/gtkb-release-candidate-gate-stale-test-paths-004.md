NO-GO

# Loyal Opposition Review - Release-Candidate Gate Stale Test Paths REVISED-1

bridge_kind: lo_verdict
Document: gtkb-release-candidate-gate-stale-test-paths
Version: 004
Reviewer: Codex (harness A, Loyal Opposition)
Date: 2026-05-11 UTC
Reviewed file: `bridge/gtkb-release-candidate-gate-stale-test-paths-003.md`
Verdict: NO-GO

## Claim

REVISED-1 correctly expands the scope from the pytest list to the full
`_python_gates()` static-path lane, and it correctly removes `--skip-python`
from the lane-runnability check. It cannot receive GO yet because the proposed
post-implementation verification commands still are not executable in the
declared Windows/PowerShell environment: they pipe through `tail`, which is not
available here. The proposal also miscounts the pytest path inventory, which
would make the post-implementation evidence harder to audit.

## Role Authority

- Active harness: Codex.
- Durable harness ID: `A`, per `harness-state/harness-identities.json`.
- Durable role: `loyal-opposition`, per `harness-state/role-assignments.json`.
- Review-start bridge state: live `bridge/INDEX.md` listed this thread latest
  status as `REVISED: bridge/gtkb-release-candidate-gate-stale-test-paths-003.md`,
  actionable for Loyal Opposition.

## Prior Deliberations

Deliberation search was run before review for:

```text
release candidate gate stale paths ruff bandit detect_import_cycles applications Agent_Red platform_tests
```

Relevant prior-decision evidence:

- `DELIB-1871` / `DELIB-1479` - tests-package collision and verification
  context for the `tests/` to `platform_tests/` rename.
- `DELIB-1483` / `DELIB-1486` - Agent Red relocation context for
  `applications/Agent_Red/`.
- `DELIB-1074` - Agent Red governance adoption and release-readiness context.

No prior deliberation found waives executable verification commands for a
bridge proposal.

## Applicability Preflight

Command:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-release-candidate-gate-stale-test-paths
```

Result: pass.

```text
## Applicability Preflight

- packet_hash: `sha256:42154ce12874a8352bcf5b5f10d5866811056ba3b2de6559831825aa3106b1c3`
- bridge_document_name: `gtkb-release-candidate-gate-stale-test-paths`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-release-candidate-gate-stale-test-paths-003.md`
- operative_file: `bridge/gtkb-release-candidate-gate-stale-test-paths-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:applications/**, content:applications/, content:Agent Red |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:deferred, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

Command:

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-release-candidate-gate-stale-test-paths
```

Result: pass.

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-release-candidate-gate-stale-test-paths`
- Operative file: `bridge\gtkb-release-candidate-gate-stale-test-paths-003.md`
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

## Findings

### F1 - P1 - Verification commands still use unavailable `tail`

Observation:

- REVISED-1 states that F2 is closed by replacing the prior skipped-lane
  command with `python scripts/release_candidate_gate.py --skip-frontend`
  (`bridge/gtkb-release-candidate-gate-stale-test-paths-003.md:39`).
- The post-implementation verification commands pipe several required checks
  through `tail`, including Ruff, import-cycles, Bandit, pytest collect-only,
  and the release gate command itself
  (`bridge/gtkb-release-candidate-gate-stale-test-paths-003.md:202`,
  `:205`, `:208`, `:211`, `:214`).
- In this PowerShell checkout, `tail` is not available:

  ```text
  python --version 2>&1 | tail -10
  ```

  returns:

  ```text
  tail : The term 'tail' is not recognized as the name of a cmdlet, function, script file, or operable program.
  ```

Deficiency rationale:

The proposal fixed the `--skip-python` problem but introduced or retained a
different non-executable verification surface. This is the same class of
Windows/PowerShell command defect already corrected in the Axis 2 bridge
thread for `grep`.

Impact:

If GO were issued, the post-implementation report could not run the required
verification commands as written. The central F2 closure claim depends on
commands that fail at the shell before their underlying checks are evaluated.

Recommended action:

Revise the verification commands to avoid Unix-only `tail`. Acceptable options:

- remove the `tail` pipe entirely and report the full command output summary;
- use PowerShell-native capture, for example
  `... 2>&1 | Select-Object -Last 10`; or
- use a short Python wrapper that runs the command and prints the last N lines.

The release-gate lane-runnability command must remain `--skip-frontend` only;
do not reintroduce `--skip-python`.

Decision needed from owner: none.

### F2 - P2 - Path-count inventory is internally inconsistent

Observation:

- REVISED-1 states the pytest sub-lane has 38 paths and that the total rewrite
  count is `3 + 38 = 41`
  (`bridge/gtkb-release-candidate-gate-stale-test-paths-003.md:107`,
  `:168`, `:176`, `:189`, `:194`, `:211`, `:264`).
- The table itself lists pytest rows for lines 298 through 336 inclusive,
  which is 39 pytest paths.
- The current `_python_gates()` pytest list also contains 39 `.py` path
  arguments.
- Codex checked the proposed rewritten destinations and found 39 proposed
  pytest files, all present at the filesystem:

  ```text
  count=39 missing=0
  ```

Deficiency rationale:

The count mismatch is not the behavioral repair's core defect, but the proposal
uses the count repeatedly as an acceptance and audit control. A post-impl
report that says "41 paths" while changing 42 path arguments would recreate
the same evidence drift this thread is trying to remove.

Impact:

Future verification could compare the wrong expected count and miss an omitted
or extra rewrite.

Recommended action:

Revise the proposal to state `39` pytest paths and `42` total path rewrites
if the table is intended to remain as written. If one row is not intended to
be part of the rewrite, remove it explicitly and explain why.

Decision needed from owner: none.

## Positive Confirmations

- Applicability and ADR/DCL clause preflights pass on the operative `-003`
  proposal.
- The current root `src/` and `tests/` directories are absent, and the proposed
  destination roots `applications/Agent_Red/src`,
  `applications/Agent_Red/tests`, and `platform_tests` exist.
- All 39 proposed pytest destination files in the table exist.
- Expanding F1 closure to Ruff, Bandit, `detect_import_cycles.py`, and pytest
  is the right scope; the prior `-001` proposal was too narrow.
- Using `python scripts/release_candidate_gate.py --skip-frontend` rather than
  `--skip-python --skip-frontend` is the correct verification direction once
  the shell command is made executable.

## Decision

NO-GO. Prime Builder should file REVISED-2 with PowerShell-executable
verification commands and corrected path-count accounting. No broader design
change is required by this verdict.

## Commands Executed

- `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-release-candidate-gate-stale-test-paths`
- `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-release-candidate-gate-stale-test-paths`
- `$env:PYTHONPATH='groundtruth-kb\src'; $env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations search "release candidate gate stale paths ruff bandit detect_import_cycles applications Agent_Red platform_tests" --limit 10`
- `Test-Path` checks for `applications\Agent_Red\src`, `applications\Agent_Red\tests`, `platform_tests`, `groundtruth-kb\src`, `groundtruth-kb\tests`, `src`, `tests`, and `requirements.txt`.
- Targeted read of `scripts/release_candidate_gate.py` lines 270-370.
- `python --version 2>&1 | tail -10`
- PowerShell path-existence check for the 39 proposed pytest destination files.
- Targeted reads over the full bridge thread `-001` through `-003`.

File bridge scan contribution: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
