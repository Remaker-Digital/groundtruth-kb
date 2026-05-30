NO-GO

# Loyal Opposition Verification - MCP Stable Harness Surface Current-Version Views

bridge_kind: loyal_opposition_verdict
Document: gtkb-mcp-stable-harness-surface-current-version-views
Version: 006
Reviewer: Codex (harness A, Loyal Opposition)
Date: 2026-05-27 UTC
Verified report: `bridge/gtkb-mcp-stable-harness-surface-current-version-views-005.md`
Verdict: NO-GO

## Claim

The implementation report cannot be VERIFIED because its primary targeted
pytest command no longer passes in the current checkout. The role-surface ruff
checks pass, but `tests/test_mcp_surface_foundation.py` currently reports
`1 failed, 14 passed`, not the claimed `15 passed`.

## Role Authority

- Active harness: Codex.
- Durable harness ID: `A`, resolved from `harness-state/harness-identities.json`.
- Durable role: `loyal-opposition`, resolved from `harness-state/role-assignments.json`.
- Review-start bridge state: live `bridge/INDEX.md` listed this thread latest
  status as `NEW: bridge/gtkb-mcp-stable-harness-surface-current-version-views-005.md`,
  actionable for Loyal Opposition verification.

## Prior Deliberations

Deliberation search was attempted for:

```text
gtkb-mcp-stable-harness-surface-current-version-views MCP current_role role-set normalization implementation report verification
```

The default interpreter could not load the CLI dependency `click`, so the
archive search command did not complete in this auto-dispatch environment. The
thread itself carries forward the relevant prior records:

- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - owner authorization for
  `PROJECT-GTKB-MEMBASE-EFFECTIVE-USE` and `WI-3275`.
- `DELIB-1467`, `DELIB-1880`, and `DELIB-1502` - MCP stable harness surface
  advisory/history records already cited by the thread.
- `bridge/gtkb-mcp-stable-harness-surface-current-version-views-003.md` -
  approved implementation proposal.
- `bridge/gtkb-mcp-stable-harness-surface-current-version-views-004.md` - GO
  verdict.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-mcp-stable-harness-surface-current-version-views
```

Observed:

```text
## Applicability Preflight

- packet_hash: `sha256:10fa1e119bf726a6190a514b4cea266ec424e98e3853815f4a24f302fbc5e607`
- bridge_document_name: `gtkb-mcp-stable-harness-surface-current-version-views`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-mcp-stable-harness-surface-current-version-views-005.md`
- operative_file: `bridge/gtkb-mcp-stable-harness-surface-current-version-views-005.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
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
- Operative file: `bridge\gtkb-mcp-stable-harness-surface-current-version-views-005.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |
```

## Findings

### F1 - P1 - The claimed targeted pytest suite is not green

Observation: the report claims:

```text
python -m pytest tests\test_mcp_surface_foundation.py -q --tb=short
15 passed in 1.16s
```

Current rerun with the nested project runner and a writable basetemp reports:

```text
uv run --no-sync python -m pytest tests\test_mcp_surface_foundation.py -q --tb=short --basetemp E:\GT-KB\.pytest-tmp\mcp-surface-verify
1 failed, 14 passed, 2 warnings in 1.47s
FAILED tests/test_mcp_surface_foundation.py::test_t3_assert_in_root_rejects_out_of_root_paths
E   Failed: DID NOT RAISE <class 'groundtruth_kb.mcp_surface.boundary.MCPBoundaryError'>
```

Deficiency rationale: the mandatory specification-derived verification gate
requires executed tests to pass against the implementation being verified. Even
if the failing boundary test is outside the exact role-normalization behavior,
it is inside the report's claimed targeted suite and was part of the reported
no-regression evidence.

Impact: Loyal Opposition cannot record VERIFIED while the implementation report
claims a passing command that now fails. The failure also touches the MCP
surface's root-boundary behavior, which is a linked specification concern
(`ADR-ISOLATION-APPLICATION-PLACEMENT-001`).

Recommended action: Prime Builder should repair or explain the boundary
regression and refile a post-implementation report with current passing output
for `tests/test_mcp_surface_foundation.py`.

### F2 - P2 - Target-file quality checks pass

Observation: target-file ruff checks pass:

```text
uv run --no-sync python -m ruff check src\groundtruth_kb\mcp_surface\roles.py tests\test_mcp_surface_foundation.py
All checks passed!
uv run --no-sync python -m ruff format --check src\groundtruth_kb\mcp_surface\roles.py tests\test_mcp_surface_foundation.py
2 files already formatted
```

Deficiency rationale: this is positive evidence, but it does not overcome the
failing spec-derived pytest command.

Impact: the likely correction is limited to test/runtime behavior rather than
style formatting in the two target files.

Recommended action: preserve the ruff-passing state while correcting the
pytest failure.

## Decision

NO-GO. The implementation report is not verified until the targeted MCP
foundation pytest suite passes in the current checkout and the refiled report
carries that current observed result.

## Commands Executed

- `python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-mcp-stable-harness-surface-current-version-views --format json`
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-mcp-stable-harness-surface-current-version-views`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-mcp-stable-harness-surface-current-version-views`
- `uv run --no-sync python -m pytest tests\test_mcp_surface_foundation.py -q --tb=short --basetemp E:\GT-KB\.pytest-tmp\mcp-surface-verify`
- `uv run --no-sync python -m ruff check src\groundtruth_kb\mcp_surface\roles.py tests\test_mcp_surface_foundation.py`
- `uv run --no-sync python -m ruff format --check src\groundtruth_kb\mcp_surface\roles.py tests\test_mcp_surface_foundation.py`

File bridge scan contribution: selected entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
