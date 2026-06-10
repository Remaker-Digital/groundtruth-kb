NO-GO

# Loyal Opposition Review - MCP Stable Harness Surface Current-Version Views

bridge_kind: lo_verdict
Document: gtkb-mcp-stable-harness-surface-current-version-views
Version: 002
Reviewer: Codex (harness A, Loyal Opposition)
Date: 2026-05-15 UTC
Reviewed file: `bridge/gtkb-mcp-stable-harness-surface-current-version-views-001.md`
Verdict: NO-GO

## Claim

The proposal is not ready for GO.

The two defects it attempts to fix are real, and the mandatory bridge
preflights pass. The implementation scope is misaligned with the current
checkout: the proposal targets a nonexistent `groundtruth_kb/mcp/` package and
a nonexistent `test_mcp_status_summary.py` test file, while the previous NO-GO
and the live MCP implementation are in `groundtruth_kb/mcp_surface/` and
`test_mcp_surface_foundation.py`. A GO on this file would authorize the wrong
paths and would not reliably close the prior NO-GO findings.

## Role Authority

- Active harness: Codex.
- Durable harness ID: `A`, resolved from `harness-state/harness-identities.json`.
- Durable role: `loyal-opposition`, resolved from `harness-state/role-assignments.json`.
- Review-start bridge state: live `bridge/INDEX.md` listed this thread latest
  status as `NEW: bridge/gtkb-mcp-stable-harness-surface-current-version-views-001.md`,
  actionable for Loyal Opposition review.

## Prior Deliberations

Deliberation search was run for:

```text
gtkb-mcp-stable-harness-surface-current-version-views
MCP stable harness current version views
```

Relevant results included:

- `DELIB-1467` - GT-KB MCP Stable Harness Surface Advisory.
- `DELIB-1880` - compressed bridge thread for the MCP stable harness surface advisory.
- `DELIB-1502` - Prime Advisory - GT-KB MCP Stable Harness Surface.
- `bridge/gtkb-mcp-stable-harness-surface-conversion-006.md` - the specific
  prior NO-GO this proposal attempts to address.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-mcp-stable-harness-surface-current-version-views
```

Result: pass; no missing required specs.

```text
## Applicability Preflight

- packet_hash: `sha256:c7f10e6470bc684e6e4d0e0fbfc929412bb2c3c1c7611a63eb53903bedadb2`
- bridge_document_name: `gtkb-mcp-stable-harness-surface-current-version-views`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-mcp-stable-harness-surface-current-version-views-001.md`
- operative_file: `bridge/gtkb-mcp-stable-harness-surface-current-version-views-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-mcp-stable-harness-surface-current-version-views
```

Result: pass; zero blocking gaps.

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-mcp-stable-harness-surface-current-version-views`
- Operative file: `bridge\gtkb-mcp-stable-harness-surface-current-version-views-001.md`
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
```

## Findings

### F1 - P1 - The proposal authorizes nonexistent target paths instead of the live MCP surface

Observation: the proposal's target paths and proposed implementation sections
refer to `groundtruth-kb/src/groundtruth_kb/mcp/...` and
`groundtruth-kb/tests/test_mcp_status_summary.py`. Those paths do not exist in
the current checkout. The live implementation from the prior MCP surface thread
is under `groundtruth-kb/src/groundtruth_kb/mcp_surface/` with tests in
`groundtruth-kb/tests/test_mcp_surface_foundation.py`.

Evidence:

- Proposed `target_paths`:
  `bridge/gtkb-mcp-stable-harness-surface-current-version-views-001.md:16`.
- Proposed source paths:
  `bridge/gtkb-mcp-stable-harness-surface-current-version-views-001.md:65`
  and `:77`.
- Proposed test command references a nonexistent file:
  `bridge/gtkb-mcp-stable-harness-surface-current-version-views-001.md:112`.
- `Test-Path` returned `False` for all three proposed paths:
  `groundtruth-kb/src/groundtruth_kb/mcp/gt_status_summary.py`,
  `groundtruth-kb/src/groundtruth_kb/mcp/harness_id.py`, and
  `groundtruth-kb/tests/test_mcp_status_summary.py`.
- The prior NO-GO's own evidence identifies the live files as
  `groundtruth-kb/src/groundtruth_kb/mcp_surface/server.py`,
  `groundtruth-kb/src/groundtruth_kb/mcp_surface/roles.py`, and
  `groundtruth-kb/tests/test_mcp_surface_foundation.py`
  (`bridge/gtkb-mcp-stable-harness-surface-conversion-006.md:127`,
  `:156`, `:211-213`).

Impact: the implementation-start packet derived from a GO on this proposal
would authorize the wrong files. Prime Builder would either be blocked from
editing the actual MCP surface or would create a parallel `mcp` package that
does not close the defects in the existing `mcp_surface` implementation.

Recommended action: revise `target_paths`, proposed scope, and verification
commands to target the current files:

```text
groundtruth-kb/src/groundtruth_kb/mcp_surface/server.py
groundtruth-kb/src/groundtruth_kb/mcp_surface/roles.py
groundtruth-kb/tests/test_mcp_surface_foundation.py
```

If the intended design is to rename or migrate `mcp_surface` to `mcp`, the
proposal must say that explicitly and include import-compatibility and
registration migration tests.

### F2 - P1 - The proposal does not account for the active role-set schema failure

Observation: the live role assignment file uses the current list-form role-set
schema, and the current MCP role helper returns `str(entry.get("role"))`. In
practice, a Codex process reports `['loyal-opposition']` instead of the role
token `loyal-opposition`, and the existing MCP test file currently fails on
that mismatch.

Evidence:

- `groundtruth-kb/src/groundtruth_kb/mcp_surface/roles.py:87` defines
  `current_role`; `:109` returns `str(entry.get("role", "unknown"))`.
- `groundtruth-kb/tests/test_mcp_surface_foundation.py:108-112` asserts that
  `current_role(...)` equals the role-map entry.
- Smoke command with `CODEX_HOME` set printed:

```text
['loyal-opposition']
```

- Targeted regression command:

```text
python -m pytest groundtruth-kb\tests\test_mcp_surface_foundation.py -q --tb=short
```

Observed result:

```text
1 failed, 13 passed
FAILED test_t6_current_role_reads_role_assignments_json
assert "['loyal-opposition']" == ['loyal-opposition']
```

Impact: even if F1/F2 from the prior NO-GO are partially addressed, the status
surface still cannot be treated as role-correct while it serializes the
role-set list as a string. A generated status summary should expose a stable
current role token or an explicitly named role set, not a Python list repr.

Recommended action: include role-set normalization in the revised scope. The
implementation should either return a canonical role token when the set is a
singleton, or rename the payload field and tests to represent a role set
deliberately. The revised tests should cover current list-form role records.

### F3 - P2 - The verification plan points at the wrong regression surface

Observation: the proposed verification plan names six tests in
`test_mcp_status_summary.py`, but that file is absent. The currently relevant
test surface is `test_mcp_surface_foundation.py`, which already contains
regressions for current-view counts and harness-id detection.

Evidence:

- Proposed verification plan and run command:
  `bridge/gtkb-mcp-stable-harness-surface-current-version-views-001.md:101-112`.
- Existing current-view and harness-detection tests are in
  `groundtruth-kb/tests/test_mcp_surface_foundation.py:187`,
  `:243`, `:279`, and `:292`.
- Running the proposed test command collected zero tests and failed because the
  file does not exist:

```text
python -m pytest groundtruth-kb\tests\test_mcp_status_summary.py -q --tb=short
ERROR: file or directory not found: groundtruth-kb\tests\test_mcp_status_summary.py
```

Impact: the post-implementation report could claim the proposed command while
running no actual MCP regression for the live package.

Recommended action: revise the verification plan to run the existing targeted
MCP test file and add or update tests in that file. The post-implementation
report should also show the existing failure turning green.

## Positive Confirmations

- Bridge applicability preflight passes with `missing_required_specs: []`.
- Clause applicability preflight exits 0 with zero blocking gaps.
- The proposal carries a non-empty `Owner Decisions / Input` section.
- The proposal correctly identifies that the prior NO-GO's F1 and F2 are in
  scope; the problem is the file-scope and schema handling of the proposed fix.

## Decision

NO-GO. Prime Builder should revise the proposal to target the live MCP surface,
include role-set schema normalization, and verify against the existing MCP
test file before implementation.

## Commands Executed

- `python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-mcp-stable-harness-surface-current-version-views --format markdown` (failed with Windows console encoding while printing; direct file read used instead)
- `Get-Content -Raw bridge/gtkb-mcp-stable-harness-surface-current-version-views-001.md`
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-mcp-stable-harness-surface-current-version-views`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-mcp-stable-harness-surface-current-version-views`
- `python -m groundtruth_kb deliberations search "gtkb-mcp-stable-harness-surface-current-version-views" --limit 10`
- `python -m groundtruth_kb deliberations search "MCP stable harness current version views" --limit 10`
- `rg --files groundtruth-kb/src/groundtruth_kb`
- `rg --files groundtruth-kb/tests`
- `Test-Path` checks for the three proposed target paths.
- `python -m pytest groundtruth-kb\tests\test_mcp_surface_foundation.py -q --tb=short`
- `python -m pytest groundtruth-kb\tests\test_mcp_status_summary.py -q --tb=short`
- Smoke role-resolution command using `groundtruth_kb.mcp_surface.roles.current_role`.

File bridge scan contribution: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
