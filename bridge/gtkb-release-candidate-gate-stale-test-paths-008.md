VERIFIED

# Loyal Opposition Verification - Release-Candidate Gate Stale Test Paths Fix

bridge_kind: verification
Document: gtkb-release-candidate-gate-stale-test-paths
Version: 008
Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-11 UTC
Responds-To: `bridge/gtkb-release-candidate-gate-stale-test-paths-007.md`

## Decision

VERIFIED. The implementation report demonstrates that the release-candidate
gate's `_python_gates()` static path surface was rewritten to the current
`applications/Agent_Red/` and `platform_tests/` locations, and independent
review commands confirm that the target paths resolve. The remaining Ruff and
pytest failures are baseline content/import failures on resolved files, not
stale path-collection failures, and were explicitly out of scope for the GO'd
proposal.

Decision needed from owner: none.

## Prior Deliberations

Deliberation search was run before verification:

```text
python -m groundtruth_kb deliberations search "gtkb-release-candidate-gate-stale-test-paths release_candidate_gate platform_tests Agent_Red" --limit 10
```

Relevant context carried forward from the implementation report:

- `DELIB-1871` - compressed `gtkb-tests-package-collision-resolution` thread,
  the source-of-truth context for the `tests/` to `platform_tests/` rename.
- `DELIB-1479` - Loyal Opposition verification of the tests-package collision
  resolution.
- `DELIB-1483` and `DELIB-1486` - Agent Red relocation context for
  `applications/Agent_Red/`.
- `DELIB-S342-BACKLOG-ADDITION-OWNER-DIRECTIVE` - owner directive context for
  filing and acting on notice-worthy release-gate issues.

No prior deliberation found contradicts verification of the path rewrites.

## Applicability Preflight

Command:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-release-candidate-gate-stale-test-paths
```

Observed result:

```text
## Applicability Preflight

- packet_hash: `sha256:1bd717a9e80613d4352a72909b25f6a595051dcc2a9d223c44ceddb562f1ed7b`
- bridge_document_name: `gtkb-release-candidate-gate-stale-test-paths`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-release-candidate-gate-stale-test-paths-007.md`
- operative_file: `bridge/gtkb-release-candidate-gate-stale-test-paths-007.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:applications/**, path:.claude/rules/file-bridge-protocol.md, content:applications/, content:Agent Red |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md |
```

## Clause Applicability

Command:

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-release-candidate-gate-stale-test-paths
```

Observed result:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-release-candidate-gate-stale-test-paths`
- Operative file: `bridge\gtkb-release-candidate-gate-stale-test-paths-007.md`
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

## Verification Evidence

### VE-1 - Reviewed line range no longer contains stale root paths

Reviewed `scripts/release_candidate_gate.py` lines 282-336, the `_python_gates()`
range scoped by the GO'd proposal. Observed:

```text
reviewed_line_range 282-336
root_src_tests_refs 0
missing_target_literals 0
```

The upstream `groundtruth-kb/tests/` invocation at lines 351-369 remains
outside the edited range and is intentionally untouched.

### VE-2 - GTKB-GOV-010 input is reachable at the new path

Command:

```text
python -m pytest platform_tests/scripts/test_standing_backlog_harvest.py -q
```

Observed result:

```text
5 passed, 1 warning in 1.19s
```

This satisfies the GTKB-GOV-010 reachability check for the standing-backlog
harvest test.

### VE-3 - Release-gate sub-lanes resolve their rewritten targets

Commands and observed results:

```text
python scripts\detect_import_cycles.py applications\Agent_Red\src
OK: 281 modules scanned, no circular imports
```

```text
python -m bandit -r applications/Agent_Red/src/ -ll -c pyproject.toml
No issues identified. EXIT=0
```

```text
python -m ruff check applications/Agent_Red/src/ applications/Agent_Red/tests/ platform_tests/ --select E,F --no-cache
Found 163 errors. EXIT=1
```

The Ruff command reached resolved files and produced lint findings, matching the
implementation report's baseline-failure interpretation.

### VE-4 - Pytest target list resolves before baseline import failure

Reviewer extraction found 39 pytest target paths and zero missing files. The
collection command then loaded the target files and reached the known baseline
import failure:

```text
pytest_paths 39
missing 0
ModuleNotFoundError: No module named 'lib.scaling_enforcement'
808 tests collected, 1 error in 2.85s
EXIT 2
```

This is not a stale-path failure: pytest found the listed files and began
collection. The single import failure is in the resolved test module's own
imports and is outside the approved scope.

## Findings

No blocking findings.

## Commands Executed

- `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-release-candidate-gate-stale-test-paths`
- `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-release-candidate-gate-stale-test-paths`
- `$env:PYTHONPATH='groundtruth-kb\src'; $env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations search "gtkb-release-candidate-gate-stale-test-paths release_candidate_gate platform_tests Agent_Red" --limit 10`
- Line-range path-surface check over `scripts\release_candidate_gate.py` lines 282-336.
- `python -m pytest platform_tests/scripts/test_standing_backlog_harvest.py -q`
- `python scripts\detect_import_cycles.py applications\Agent_Red\src`
- `python -m bandit -r applications/Agent_Red/src/ -ll -c pyproject.toml`
- `python -m ruff check applications/Agent_Red/src/ applications/Agent_Red/tests/ platform_tests/ --select E,F --no-cache`
- Extracted and collection-checked the 39 pytest paths from `_python_gates()`.
- Targeted reads over the full bridge thread `-001` through `-007`.

File bridge scan contribution: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
