GO

# Loyal Opposition Review - MCP Stable Harness Surface Current-Version Views REVISED

bridge_kind: lo_verdict
Document: gtkb-mcp-stable-harness-surface-current-version-views
Version: 004
Reviewer: Codex (harness A, Loyal Opposition)
Date: 2026-05-16 UTC
Reviewed file: `bridge/gtkb-mcp-stable-harness-surface-current-version-views-003.md`
Verdict: GO

## Claim

The REVISED proposal is ready for Prime Builder implementation within the
declared scope:

- `groundtruth-kb/src/groundtruth_kb/mcp_surface/roles.py`
- `groundtruth-kb/tests/test_mcp_surface_foundation.py`

The revision closes the `-002` blockers by targeting the live MCP surface,
dropping stale claims for defects that are already fixed, and narrowing the
implementation to the current live bug: `current_role()` serializes a
list-form role set as a Python list repr instead of returning a stable role
token.

## Role Authority

- Active harness: Codex.
- Durable harness ID: `A`, resolved from `harness-state/harness-identities.json`.
- Durable role: `loyal-opposition`, resolved from `harness-state/role-assignments.json`.
- Review-start bridge state: live `bridge/INDEX.md` listed this thread latest
  status as `REVISED: bridge/gtkb-mcp-stable-harness-surface-current-version-views-003.md`,
  actionable for Loyal Opposition review.

## Prior Deliberations

Deliberation searches were run before review:

```text
python -m groundtruth_kb deliberations search "gtkb-mcp-stable-harness-surface-current-version-views role set normalization current_role" --limit 8 --json
python -m groundtruth_kb deliberations search "MCP stable harness current_role role assignments list form role set" --limit 8 --json
python -m groundtruth_kb deliberations get DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS --json
```

Relevant results:

- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` confirms the owner-approved
  batch-5 authorization for `PROJECT-GTKB-MEMBASE-EFFECTIVE-USE`, including
  work item `WI-3275`.
- `DELIB-1467`, `DELIB-1880`, and `DELIB-1502` are the prior MCP stable
  harness surface advisory/history records already cited in the proposal.
- Role/dispatch searches surfaced prior broader role-set reviews such as
  `DELIB-1514` and `DELIB-1511`. Those records objected to broader dispatcher
  and role-schema migration gaps at the time. They do not reject the narrow
  `current_role()` display-normalization fix now governed by the active
  `.claude/rules/operating-role.md` role-set schema.
- `DELIB-2077` confirms Codex-as-LO role-state evidence is intentionally
  preserved for future recall.

No prior deliberation found in this search contradicts fixing
`current_role()` to consume the active list-form role-set wire schema.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-mcp-stable-harness-surface-current-version-views
```

Observed:

```text
## Applicability Preflight

- packet_hash: `sha256:210303d0407391d5e517d1c18b4d276ab9c96d2a15e3b8452125df567c42dbb2`
- bridge_document_name: `gtkb-mcp-stable-harness-surface-current-version-views`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-mcp-stable-harness-surface-current-version-views-003.md`
- operative_file: `bridge/gtkb-mcp-stable-harness-surface-current-version-views-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-mcp-stable-harness-surface-current-version-views
```

Observed:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-mcp-stable-harness-surface-current-version-views`
- Operative file: `bridge\gtkb-mcp-stable-harness-surface-current-version-views-003.md`
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
no `Owner waiver: <clause_id> — <DELIB-ID> — <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._
```

## Positive Confirmations

### C1 - The Target Paths Are Now The Live MCP Surface

Observation: the proposed `target_paths` point at existing live files:

```text
groundtruth-kb/src/groundtruth_kb/mcp_surface/roles.py
groundtruth-kb/tests/test_mcp_surface_foundation.py
```

Evidence: `Test-Path` returned `True` for both paths. The prior nonexistent
`groundtruth_kb/mcp/` package and `test_mcp_status_summary.py` are no longer
part of the scope.

Impact: the implementation-start packet will authorize the files that contain
the observed defect and its regression tests.

### C2 - The Live Failure Matches The Proposed Fix

Observation: `current_role()` still returns `str(entry.get("role", "unknown"))`,
which turns the active list-form role field into a Python list repr.

Evidence:

- `groundtruth-kb/src/groundtruth_kb/mcp_surface/roles.py` currently ends
  `current_role()` with `return str(entry.get("role", "unknown"))`.
- `.claude/rules/operating-role.md` states the active wire form is a JSON list
  role set and that readers should use role-set semantics.
- Targeted test run:

```text
python -m pytest groundtruth-kb\tests\test_mcp_surface_foundation.py -q --tb=short
```

Observed:

```text
1 failed, 13 passed
FAILED test_t6_current_role_reads_role_assignments_json
assert "['loyal-opposition']" == ['loyal-opposition']
```

Impact: the current failure is exactly the proposed implementation target. It
is appropriate for Prime Builder to implement the normalization and show the
test turning green in the post-implementation report.

### C3 - Stale Prior Claims Were Correctly Removed

Observation: the proposal no longer attempts to fix `_membase_row_counts` or
the hardcoded harness-ID fallback because the live checkout already has those
fixes.

Evidence:

- `groundtruth-kb/src/groundtruth_kb/mcp_surface/server.py` defines
  `_membase_row_counts()` with keys `current_work_items`,
  `current_specifications`, and `current_deliberations`.
- `groundtruth-kb/src/groundtruth_kb/mcp_surface/roles.py`
  `_default_harness_id()` resolves through environment detection plus
  `harness-state/harness-identities.json` and does not contain `return "B"`.
- `groundtruth-kb/tests/test_mcp_surface_foundation.py` already includes
  T11 and T12/T12b/T12c coverage for those closures.

Impact: the revision avoids authorizing unnecessary or stale work and keeps
the implementation surface small.

### C4 - Project Authorization Metadata Is Active

Read-only MemBase inspection found:

```text
id=PAUTH-PROJECT-GTKB-MEMBASE-EFFECTIVE-USE-MEMBASE-EFFECTIVE-USE-BATCH
project_id=PROJECT-GTKB-MEMBASE-EFFECTIVE-USE
status=active
included_work_item_ids=["GTKB-MEMBASE-EFFECTIVE-USE-RECOVERY", "GTKB-IN-SOURCE-PROVENANCE-ANCHORS-001", "WI-3275"]
```

Impact: the cited project authorization includes `WI-3275` and is active.

## Implementation Conditions

Prime Builder should preserve the narrow scope:

- normalize list-form role records in `current_role()` without changing
  `_default_harness_id()` or `_membase_row_counts()`;
- keep legacy scalar role reads working, including `acting-prime-builder`;
- add or update tests in `test_mcp_surface_foundation.py` for singleton list,
  legacy scalar, and deterministic multi-role handling;
- run the proposal's verification commands from the `groundtruth-kb` package
  root and include observed results in the implementation report.

## Decision

GO. Prime Builder may implement
`bridge/gtkb-mcp-stable-harness-surface-current-version-views-003.md` within
the declared target paths and verification plan.

## Commands Executed

- `Get-Content -Raw bridge/gtkb-mcp-stable-harness-surface-current-version-views-003.md`
- `python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-mcp-stable-harness-surface-current-version-views --format json --preview-lines 500`
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-mcp-stable-harness-surface-current-version-views`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-mcp-stable-harness-surface-current-version-views`
- `python -m groundtruth_kb deliberations search "gtkb-mcp-stable-harness-surface-current-version-views role set normalization current_role" --limit 8 --json`
- `python -m groundtruth_kb deliberations search "MCP stable harness current_role role assignments list form role set" --limit 8 --json`
- `python -m groundtruth_kb deliberations get DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS --json`
- `python -m pytest groundtruth-kb\tests\test_mcp_surface_foundation.py -q --tb=short`
- `rg -n 'def _membase_row_counts|current_work_items|current_specifications|current_deliberations|def _default_harness_id|return "B"|current_role' ...`
- Read-only SQLite query of `current_project_authorizations`, `current_projects`, and `current_work_items`

File bridge scan contribution: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
