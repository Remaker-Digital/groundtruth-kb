GO

# Loyal Opposition Review - Bridge Preflight Missing Parent Directory Warning REVISED-1

bridge_kind: loyal_opposition_review
Document: gtkb-bridge-preflight-path-warning
Version: 004
Reviewer: Codex (harness A, Loyal Opposition)
Date: 2026-05-15 UTC
Reviewed proposal: `bridge/gtkb-bridge-preflight-path-warning-003.md`
Verdict: GO

## Claim

The `-003` revision resolves the prior NO-GO findings from
`bridge/gtkb-bridge-preflight-path-warning-002.md`. Prime Builder may implement
the revised proposal within the stated scope: add a non-blocking
missing-parent-directory warning to `scripts/bridge_applicability_preflight.py`
using a narrow cited-path collector, and add focused tests in
`platform_tests/scripts/test_bridge_applicability_preflight.py`.

This GO does not authorize changing existing applicability pass/fail semantics,
using the broad document-wide `PATH_TOKEN_RE` scan as the warning source, or
creating a new top-level test-root layout for this work.

## Review Scope

- Read live `bridge/INDEX.md`; latest status for
  `gtkb-bridge-preflight-path-warning` was `REVISED`, actionable for Loyal
  Opposition.
- Read the full thread chain:
  `bridge/gtkb-bridge-preflight-path-warning-001.md`,
  `bridge/gtkb-bridge-preflight-path-warning-002.md`, and
  `bridge/gtkb-bridge-preflight-path-warning-003.md`.
- Read `.claude/rules/file-bridge-protocol.md` and the bridge skill operating
  contract.
- Ran mandatory applicability and ADR/DCL clause preflights.
- Searched and retrieved deliberation evidence.
- Inspected the current preflight parser and the current platform test path.

## Prior Deliberations

Commands:

```text
python -m groundtruth_kb deliberations search "WI-3272 bridge applicability preflight target_paths parent directory warning DELIB-S350" --limit 8 --json
python -m groundtruth_kb deliberations get DELIB-S350-BATCH2-THREE-PROJECT-AUTHORIZATIONS --json
```

Relevant result:

- `DELIB-S350-BATCH2-THREE-PROJECT-AUTHORIZATIONS` records the 2026-05-14
  owner authorization for `PAUTH-PROJECT-GTKB-BRIDGE-TOOLING-ENHANCEMENTS`,
  including WI-3272.

No prior deliberation surfaced that contradicts adding this advisory warning.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-preflight-path-warning
```

Observed:

```text
## Applicability Preflight

- packet_hash: `sha256:776a6f85188a5bf866c564f1e3c7bae8a38966a11c5c5154ae2873660edc3bbb`
- bridge_document_name: `gtkb-bridge-preflight-path-warning`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-bridge-preflight-path-warning-003.md`
- operative_file: `bridge/gtkb-bridge-preflight-path-warning-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-preflight-path-warning
```

Observed:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-bridge-preflight-path-warning`
- Operative file: `bridge\gtkb-bridge-preflight-path-warning-003.md`
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

No blocking findings.

### C1 - Prior F1 is resolved: verification path now targets the live platform test file

Evidence:

- `bridge/gtkb-bridge-preflight-path-warning-003.md:14` limits
  `target_paths` to `scripts/bridge_applicability_preflight.py` and
  `platform_tests/scripts/test_bridge_applicability_preflight.py`.
- `bridge/gtkb-bridge-preflight-path-warning-003.md:169` corrects the
  verification command to
  `python -m pytest platform_tests/scripts/test_bridge_applicability_preflight.py -q --tb=short`.
- `Test-Path` confirmed
  `platform_tests/scripts/test_bridge_applicability_preflight.py` exists and
  `tests/scripts` does not exist. The top-level `tests` directory currently
  exists, but the old `tests/scripts/...` target remains absent; that does not
  affect this revised scope.

Impact: Prime Builder now has an executable, in-root verification target.

### C2 - Prior F2 is resolved: the warning source is precise enough for GO

Evidence:

- The current parser still uses broad `PATH_TOKEN_RE` extraction in
  `extract_target_paths()` (`scripts/bridge_applicability_preflight.py:41`,
  `scripts/bridge_applicability_preflight.py:150`,
  `scripts/bridge_applicability_preflight.py:164`).
- The revised proposal explicitly adds a separate
  `collect_cited_implementation_paths()` collector and states the missing-parent
  warning must be computed from explicit `target_paths` metadata plus a
  dedicated `Files Changed` / `Files Expected To Change` section parser, not
  from the broad document scan
  (`bridge/gtkb-bridge-preflight-path-warning-003.md:32-44`,
  `bridge/gtkb-bridge-preflight-path-warning-003.md:105-134`).
- The proposed test plan includes
  `test_preflight_warning_ignores_incidental_prose_paths`
  (`bridge/gtkb-bridge-preflight-path-warning-003.md:151`,
  `bridge/gtkb-bridge-preflight-path-warning-003.md:166`).

Impact: The revised implementation plan now guards the main false-positive risk
identified in the NO-GO.

### C3 - Prior F3 is resolved: applicability preflight is clean

Evidence: the live mandatory preflight on the indexed `-003` operative file
reports `preflight_passed: true`, `missing_required_specs: []`, and
`missing_advisory_specs: []`.

Impact: The proposal now satisfies the bridge specification-linkage floor.

### C4 - Baseline targeted tests are executable

Command:

```text
python -m pytest platform_tests/scripts/test_bridge_applicability_preflight.py -q --tb=short
```

Observed result: 6 passed.

Impact: The target test file is healthy before Prime Builder adds the new
spec-derived cases.

## Opportunity Radar

No additional material advisory is needed. This reviewed item is itself a
deterministic-service/tooling enhancement, and the revised design keeps the
new automation narrow enough to avoid recurring review noise.

## Expected Implementation Report Evidence

The post-implementation report should carry forward:

- the linked specifications from the `-003` proposal;
- exact files changed;
- evidence that `extract_target_paths()` broad matching remains unchanged;
- evidence that `warnings.missing_parent_dirs` is computed only from
  `collect_cited_implementation_paths()`;
- observed results for
  `python -m pytest platform_tests/scripts/test_bridge_applicability_preflight.py -q --tb=short`
  and `python -m ruff check .`;
- applicability and clause preflight outputs after implementation.

## Decision

GO. Prime Builder may implement `bridge/gtkb-bridge-preflight-path-warning-003.md`
within the approved scope.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
