NO-GO

# Loyal Opposition Review - Bridge Citation Freshness Preflight

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-15 UTC
Reviewed proposal: `bridge/gtkb-bridge-citation-freshness-preflight-001.md`
Verdict: NO-GO

## Claim

The proposal is directionally useful and passes the mandatory mechanical bridge
gates, but it is not ready for implementation. The verification file path is
outside the active platform test lane, and the proposal narrows WI-3267's
acceptance surface by omitting the work item's required cleanup/update hint and
named fixture coverage.

## Prior Deliberations

Deliberation searches executed:

```text
python -m groundtruth_kb deliberations search "WI-3267 bridge citation freshness preflight" --limit 5
python -m groundtruth_kb deliberations search "gtkb-bridge-advisory-status REVISED-3 NO-GO citation stale" --limit 5
python -m groundtruth_kb deliberations get DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS
```

Relevant results:

- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` records the owner decision
  authorizing the project grouping that includes this bridge-protocol reliability
  work.
- `DELIB-1878` records the related `gtkb-bridge-advisory-status-001` thread
  with latest status `NO-GO`, matching the stale cross-thread citation problem
  this WI is intended to reduce.

## Applicability Preflight

- packet_hash: `sha256:1146cd6152455a643081fc213b444e16bd575267523084b903dbbbd808f37031`
- bridge_document_name: `gtkb-bridge-citation-freshness-preflight`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-bridge-citation-freshness-preflight-001.md`
- operative_file: `bridge/gtkb-bridge-citation-freshness-preflight-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:superseded, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-bridge-citation-freshness-preflight`
- Operative file: `bridge\gtkb-bridge-citation-freshness-preflight-001.md`
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

## Findings

### F1 - Proposed regression test path is outside the active platform test lane

Severity: P1 governance drift

Observation: The proposal authorizes
`tests/scripts/test_bridge_citation_freshness_preflight.py` in `target_paths`
and names `python -m pytest tests/scripts/test_bridge_citation_freshness_preflight.py -v`
as the verification command.

Evidence:

- `bridge/gtkb-bridge-citation-freshness-preflight-001.md:16` lists the test
  target under `tests/scripts`.
- `bridge/gtkb-bridge-citation-freshness-preflight-001.md:91` names the same
  `tests/scripts` path in the verification command.
- `pyproject.toml:9` sets pytest `testpaths` to `platform_tests` and
  `applications/Agent_Red/tests`, not `tests`.
- `.github/workflows/groundtruth-kb-tests.yml:42` runs
  `python -m pytest platform_tests/ -q --tb=short`.
- Existing script/preflight tests in this checkout live under
  `platform_tests/scripts/`, for example
  `platform_tests/scripts/test_bridge_applicability_preflight.py`.

Impact: Prime could implement a targeted test that passes only when explicitly
addressed by path, while the normal platform pytest lane and CI workflow would
not exercise it. That weakens the durable regression protection required by the
spec-derived verification gate.

Recommended action: Revise `target_paths` and the verification command to use
`platform_tests/scripts/test_bridge_citation_freshness_preflight.py`, or include
the necessary pytest/CI configuration changes in scope with explicit tests that
prove the new location is collected by the platform lane.

### F2 - Proposal omits part of WI-3267's acceptance surface

Severity: P2 capability overclaim

Observation: The proposal states that stale citations produce warning entries
with `{cited_slug, cited_version, latest_version, severity: "warn"}` and tests
matching/stale/multiple/missing-slug/output schema cases. It does not require a
suggested updated citation or cleanup hint, and it does not preserve the work
item's named fixture requirement.

Evidence:

- A direct MemBase read of latest `work_items` row `WI-3267` reports: "Slice 1
  acceptance: detector handles N=2 fixture cases (workflow-contract-adr vs
  runtime thread) + emits cleanup hint + reviewer-facing markdown section that
  Codex can cite."
- `bridge/gtkb-bridge-citation-freshness-preflight-001.md:72` defines the
  warning payload without a suggested replacement or cleanup hint.
- `bridge/gtkb-bridge-citation-freshness-preflight-001.md:82` through `:89`
  list tests, but no test pins the N=2 fixture cases or cleanup-hint behavior.

Impact: The implementation could satisfy the proposal while leaving the work
item only partially closed. That would push the missing acceptance behavior into
post-implementation review instead of making it part of the approved scope.

Recommended action: Revise the proposal to require a reviewer-facing cleanup or
suggested-update hint, and add explicit tests for the two WI fixture cases plus
the markdown section that Codex can cite.

## Positive Checks

- Project authorization exists and is active:
  `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-BRIDGE-PROTOCOL-RELIABILITY-BATCH`.
- `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY` includes `WI-3267`.
- Mandatory applicability preflight passed with no missing required specs.
- Mandatory ADR/DCL clause preflight passed with zero blocking gaps.

## Commands Executed

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-citation-freshness-preflight`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-citation-freshness-preflight`
- `python -m groundtruth_kb deliberations search "WI-3267 bridge citation freshness preflight" --limit 5`
- `python -m groundtruth_kb deliberations search "gtkb-bridge-advisory-status REVISED-3 NO-GO citation stale" --limit 5`
- `python -m groundtruth_kb projects show PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`
- `python -m groundtruth_kb projects authorizations PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`
- SQLite read of latest `work_items` row for `WI-3267`
- Source inspection of `pyproject.toml`, `.github/workflows/groundtruth-kb-tests.yml`, and `platform_tests/scripts/`

File bridge scan: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
