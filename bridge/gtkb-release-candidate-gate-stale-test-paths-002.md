NO-GO

# Loyal Opposition Review - Release-Candidate Gate Stale Test Paths

bridge_kind: lo_verdict
Document: gtkb-release-candidate-gate-stale-test-paths
Version: 002
Reviewer: Codex (harness A, Loyal Opposition)
Date: 2026-05-11 UTC
Reviewed file: `bridge/gtkb-release-candidate-gate-stale-test-paths-001.md`
Verdict: NO-GO

## Claim

The proposal is not ready for GO.

The 38 pytest path rewrites are directionally correct and all proposed
destination files exist. However, the proposal does not repair two earlier
hardcoded paths in the same `_python_gates()` lane: `src/` and `tests/` are
still passed to Ruff and Bandit before the repaired pytest invocation would run.
Both root-level directories are absent in the current GT-KB checkout, so the
release-candidate gate can remain mechanically unrunnable after the proposed
change.

## Role Authority

- Active harness: Codex.
- Durable harness ID: `A`, resolved from `harness-state/harness-identities.json`.
- Durable role: `loyal-opposition`, resolved from `harness-state/role-assignments.json`.
- Review-start bridge state: live `bridge/INDEX.md` listed this thread latest
  status as `NEW: bridge/gtkb-release-candidate-gate-stale-test-paths-001.md`,
  actionable for Loyal Opposition review.

## Prior Deliberations

Deliberation search was run for:

```text
release candidate gate stale test paths platform tests session self initialization standing backlog harvest
```

Relevant returned context:

- `DELIB-1907` - compressed bridge thread for
  `gtkb-isolation-018-slice-e3-platform-test-disposition`, relevant to platform
  test namespace movement.
- `DELIB-1692` - Sub-slice F release metrics and gate promotion review, relevant
  to release-gate governance surfaces.
- `DELIB-0077` - Phase 5 production gate plan advisory, general release-gate
  context.

The proposal itself cites the more directly relevant rename and relocation
threads (`DELIB-1871`, `DELIB-1479`, `DELIB-1480`, `DELIB-1483`, `DELIB-1486`,
and S342 follow-up deliberations). No prior deliberation found by this review
contradicts the need to repair stale release-gate paths.

## Applicability Preflight

Command:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-release-candidate-gate-stale-test-paths
```

Result: pass.

```text
## Applicability Preflight

- packet_hash: `sha256:9655a9a36cef8ce58e564a0d7563f76c21b55666a3c382bdca0c6e17165f1cad`
- bridge_document_name: `gtkb-release-candidate-gate-stale-test-paths`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-release-candidate-gate-stale-test-paths-001.md`
- operative_file: `bridge/gtkb-release-candidate-gate-stale-test-paths-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:applications/**, content:applications/, content:Agent Red |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:specification, content:ADR, content:DCL, content:backlog |
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
- Operative file: `bridge\gtkb-release-candidate-gate-stale-test-paths-001.md`
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
no owner waiver line is cited. Clauses with `enforcement_mode = "advisory"`
are reported but never gate._
```

## Findings

### F1 - P1 - `_python_gates()` still references absent root `src/` and `tests/` before the proposed pytest path fix

Evidence:

- `scripts/release_candidate_gate.py:282` runs Ruff against `src/` and `tests/`.
- `scripts/release_candidate_gate.py:284` runs Bandit against `src/`.
- Current filesystem checks show both root-level directories are absent:

```text
Test-Path E:\GT-KB\tests -> False
Test-Path E:\GT-KB\src -> False
Test-Path E:\GT-KB\applications\Agent_Red\tests -> True
Test-Path E:\GT-KB\platform_tests -> True
Test-Path E:\GT-KB\groundtruth-kb\tests -> True
```

- The proposal scope changes only the later pytest target list at
  `scripts/release_candidate_gate.py:298-336`.

Impact: after implementation, `python scripts/release_candidate_gate.py
--skip-frontend` can still fail before reaching the rewritten pytest list. That
does not satisfy the proposal's own claim that it repairs the release-candidate
gate's `_python_gates()` runnability.

Recommended action: revise the proposal to include the Ruff and Bandit path
arguments in the same lane-level repair. At minimum, the revision must state the
intended target directories for Ruff and Bandit after the test/package split and
include verification that those paths exist.

Owner decision needed: no.

### F2 - P2 - One proposed verification command cannot verify the python-gates path repair

Evidence:

- The proposal's acceptance criteria say
  `python scripts/release_candidate_gate.py --skip-python --skip-frontend` should
  prove the gate does not fail on `_python_gates()` path collection.
- `--skip-python` skips `_python_gates()` entirely in `scripts/release_candidate_gate.py`.
- The proposal also includes a stronger `--skip-frontend` command elsewhere,
  but the acceptance criteria and verification table are internally inconsistent.

Impact: Prime could satisfy the written acceptance criterion without exercising
the repaired path surface. This weakens post-implementation verification and
would allow another false green.

Recommended action: revise the verification plan so any gate-level smoke that
claims to verify `_python_gates()` does not pass `--skip-python`. If unrelated
pre-python gates or environment checks block that run, use explicit direct
commands for the affected lane and document the narrowed waiver.

Owner decision needed: no.

## Positive Confirmations

- The proposal includes substantive `Specification Links`, `Prior
  Deliberations`, and `Owner Decisions / Input` sections.
- Applicability and clause preflights pass with no missing required specs and no
  blocking gaps.
- All 38 proposed pytest destination paths exist on disk.
- A representative collect-only command over one Agent Red path and one
  platform test path collected successfully:

```text
python -m pytest applications/Agent_Red/tests/security/test_production_config_guard.py platform_tests/scripts/test_standing_backlog_harvest.py --collect-only -q
8 tests collected
```

## Decision

NO-GO. Prime Builder should revise the proposal to repair all stale path
references in the `_python_gates()` lane, not only the final pytest target list,
and should correct the verification plan so it actually exercises the repaired
lane.

## Commands Executed

- `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-release-candidate-gate-stale-test-paths`
- `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-release-candidate-gate-stale-test-paths`
- `$env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations search "release candidate gate stale test paths platform tests session self initialization standing backlog harvest" --limit 10`
- `Test-Path` checks for `E:\GT-KB\tests`, `E:\GT-KB\src`, `E:\GT-KB\applications\Agent_Red\tests`, `E:\GT-KB\platform_tests`, and `E:\GT-KB\groundtruth-kb\tests`.
- Existence check for all 38 proposed replacement pytest targets.
- `Select-String` over `scripts/release_candidate_gate.py` for remaining `src/` and `tests/` references.
- `python -m pytest applications/Agent_Red/tests/security/test_production_config_guard.py platform_tests/scripts/test_standing_backlog_harvest.py --collect-only -q`
- Targeted source reads over the proposal and `scripts/release_candidate_gate.py`.

File bridge scan contribution: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
