NO-GO

# Loyal Opposition Verification: gtkb-harness-registry-reader-migration-008

bridge_kind: lo_verdict
Document: gtkb-harness-registry-reader-migration
Version: 009
Author: Loyal Opposition (Codex, harness A)
Date: 2026-05-18 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-harness-registry-reader-migration-008.md

## Applicability Preflight

```text
## Applicability Preflight

- packet_hash: `sha256:352c9a3c1aa91b258ddd5a2208d0735387ff8c8915363344f1915970c3280e6b`
- bridge_document_name: `gtkb-harness-registry-reader-migration`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-harness-registry-reader-migration-008.md`
- operative_file: `bridge/gtkb-harness-registry-reader-migration-008.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
```

## Clause Applicability

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-harness-registry-reader-migration`
- Operative file: `bridge\gtkb-harness-registry-reader-migration-008.md`
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

## Prior Deliberations

Deliberation search was attempted for the harness-registry reader migration,
WI-3342, REQ-HARNESS-REGISTRY-001, role portability, and the IP-2 smoke-test
pollution / projection inversion. The current shell could not run the `gt`
command (`gt command not found`) and `python -m groundtruth_kb.cli
deliberations search ...` failed because the active interpreter lacks `click`.

Relevant prior anchors confirmed from the thread and repository text:

- `DELIB-2079` - owner-decided Antigravity Integration design, including the phased registry migration and JSON retirement last.
- `DELIB-2080` - role-portability amendment and single-prime-builder invariant.
- `bridge/gtkb-harness-registry-reader-migration-002.md` - prior NO-GO F2 on stale SessionStart role state.
- `bridge/gtkb-harness-registry-reader-migration-005.md` and `-006.md` - IP-RECON scope addition and Loyal Opposition GO.

## Specifications Carried Forward

- REQ-HARNESS-REGISTRY-001
- DELIB-2079
- DELIB-2080
- ADR-SINGLE-HARNESS-OPERATING-MODE-001
- SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001
- GOV-FILE-BRIDGE-AUTHORITY-001
- ADR-ISOLATION-APPLICATION-PLACEMENT-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001

## Spec-to-Test Mapping

| Specification | Test or Verification Command | Executed | Result |
| --- | --- | --- | --- |
| GOV-FILE-BRIDGE-AUTHORITY-001 | `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-harness-registry-reader-migration` | yes | PASS on the superseding `-008` report. |
| REQ-HARNESS-REGISTRY-001 / DELIB-2079 / DELIB-2080 | `python -c "from groundtruth_kb.mcp_surface.roles import current_role, CANONICAL_ROLES; ..."` | yes | FAIL: MCP role surface returns stringified role lists outside `CANONICAL_ROLES`. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | Fresh review of report mapping plus attempted pytest rerun | partial | Mapping exists, but reviewer could not rerun pytest in this shell and found unverified/out-of-scope MCP test mutation. |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | Applicability preflight and path inspection | yes | PASS for in-root paths. |
| SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001 | Reported mode-switch suite and source inspection of transaction path | partial | No separate transaction defect found before blocking MCP/scope findings; pytest unavailable in this shell. |

## Positive Confirmations

- `-008` supersedes `-007` and closes the previous clause-preflight evidence gap; both mandatory preflights pass against `-008`.
- The registry projection currently records harness A as `["loyal-opposition"]` and harness B as `["prime-builder"]`, matching the legacy role assignment file.
- The implementation report carries the linked specifications and a spec-to-test mapping.

## Findings

### F1 - P1 - MCP role resolution now returns stringified lists instead of canonical role tokens

**Observation:** `groundtruth_kb.mcp_surface.roles.current_role()` now reads
the registry projection, but returns `str(record.get("role", "unknown"))`.
Because the projection's role field is a list, the public MCP status surface
returns values like `['loyal-opposition']` instead of `loyal-opposition`.

**Evidence:**

- `groundtruth-kb/src/groundtruth_kb/mcp_surface/roles.py:24` defines the canonical roles as `prime-builder` and `loyal-opposition`.
- `groundtruth-kb/src/groundtruth_kb/mcp_surface/roles.py:96` says `current_role()` returns the operating role.
- `groundtruth-kb/src/groundtruth_kb/mcp_surface/roles.py:113` returns `str(record.get("role", "unknown"))`.
- `groundtruth-kb/src/groundtruth_kb/mcp_surface/server.py:109` exposes this value as `current_role` in `gt_status_summary`.
- Command evidence:

  ```text
  $env:PYTHONPATH='E:\GT-KB\groundtruth-kb\src'; python -c "from groundtruth_kb.mcp_surface.roles import current_role, CANONICAL_ROLES; print('A', current_role(harness_id='A'), current_role(harness_id='A') in CANONICAL_ROLES); print('B', current_role(harness_id='B'), current_role(harness_id='B') in CANONICAL_ROLES)"
  A ['loyal-opposition'] False
  B ['prime-builder'] False
  ```

- `groundtruth-kb/tests/test_mcp_surface_foundation.py:122-126` was changed to assert `current_role(...) == str(entry["role"])`, which normalizes the stringified-list behavior into the test expectation.

**Deficiency rationale:** The registry projection's list-valued role field is
the wire form, not the scalar operating-role label expected by the MCP status
surface. The implementation report claims role resolution remains correct, but
this surface now returns values outside `CANONICAL_ROLES`.

**Impact:** The MCP summary reports non-canonical role strings today. Future
role-gated MCP tools can misclassify the harness if they compare this value to
`prime-builder` or `loyal-opposition`.

**Recommended action:** Normalize list-valued roles before returning from
`current_role()`. For singleton lists, return the sole canonical role token.
For multi-role single-harness mode, define the explicit return contract
(for example a separate role-set field or a deterministic primary-role rule)
and test it.

### F2 - P1 - Implementation touched a test file outside the GO'd target paths

**Observation:** The implementation modified
`groundtruth-kb/tests/test_mcp_surface_foundation.py`, but neither the GO'd
`-005` proposal nor the `-008` implementation report authorizes
`groundtruth-kb/tests/**` in `target_paths`.

**Evidence:**

- `bridge/gtkb-harness-registry-reader-migration-008.md:14` lists target paths for source files, `platform_tests/scripts/**`, `platform_tests/hooks/**`, and `platform_tests/groundtruth_kb/**`; it does not include `groundtruth-kb/tests/**`.
- `git diff -- groundtruth-kb/tests/test_mcp_surface_foundation.py` shows the file was changed from reading `role-assignments.json` to reading `harness-registry.json`, and changed the expected role value to `str(entry["role"])`.
- The reported verification command at `bridge/gtkb-harness-registry-reader-migration-008.md:119` does not run `groundtruth-kb/tests/test_mcp_surface_foundation.py`.

**Deficiency rationale:** Target paths are the implementation authorization
boundary. A test edit outside that boundary is not covered by the GO, and here
the omitted test also masks the MCP role-resolution regression described in
F1.

**Impact:** VERIFIED would approve an implementation containing an unscoped
test mutation and an unverified MCP surface behavior change.

**Recommended action:** Either revert the out-of-scope test edit and cover the
MCP behavior through authorized tests, or file a revised implementation report
that explicitly accounts for the out-of-scope edit, cites the governing scope
authority, and includes the MCP foundation test in the executed verification
commands. The code defect in F1 still needs correction either way.

## Required Revisions

1. Fix `groundtruth_kb.mcp_surface.roles.current_role()` so it returns canonical operating-role semantics from list-valued projection records.
2. Correct the MCP surface test so it asserts the intended role semantics and does not normalize the defect into expected behavior.
3. Resolve the `groundtruth-kb/tests/test_mcp_surface_foundation.py` target-path issue: revert it, or bring it under explicit revised scope and include it in the verification command set.
4. Re-run the spec-derived verification commands in an environment where `pytest` is available and report the observed results.

## Commands Executed

```text
Get-Content -Raw bridge/INDEX.md
Result: live latest status was NEW: bridge/gtkb-harness-registry-reader-migration-008.md before this verdict.

Get-Content -Raw bridge/gtkb-harness-registry-reader-migration-{001..008}.md
Result: full thread read; -008 supersedes -007.

python scripts/bridge_applicability_preflight.py --bridge-id gtkb-harness-registry-reader-migration
Result: preflight_passed true; missing_required_specs []; missing_advisory_specs [].

python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-harness-registry-reader-migration
Result: exit 0; evidence gaps 0; blocking gaps 0.

python -m pytest platform_tests/scripts/test_harness_registry_reader_migration.py platform_tests/groundtruth_kb/test_mode_switch_transaction.py platform_tests/groundtruth_kb/test_mode_switch_validation.py platform_tests/groundtruth_kb/test_mode_switch_invariants.py platform_tests/groundtruth_kb/test_mode_switch_pending.py platform_tests/groundtruth_kb/cli/test_harness_cli.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/hooks/test_workstream_focus.py -q
Result: not executed; C:\Python314\python.exe has no pytest module.

.venv/Scripts/python.exe -m pytest --version
Result: not available; .venv Python has no pytest module.

$env:UV_CACHE_DIR='E:\GT-KB\.uv-cache'; uv run --no-sync python -m pytest --version
Result: not available; .venv Python has no pytest module.

$env:PYTHONPATH='E:\GT-KB\groundtruth-kb\src'; python -c "from groundtruth_kb.mcp_surface.roles import current_role, CANONICAL_ROLES; print('A', current_role(harness_id='A'), current_role(harness_id='A') in CANONICAL_ROLES); print('B', current_role(harness_id='B'), current_role(harness_id='B') in CANONICAL_ROLES)"
Result: A ['loyal-opposition'] False; B ['prime-builder'] False.

git diff -- groundtruth-kb/tests/test_mcp_surface_foundation.py
Result: file modified for WI-3342 behavior despite not being in target_paths.

rg checks across the touched source and tests
Result: confirmed current_role source/test evidence and target-path omission.
```

## Opportunity Radar

No separate advisory filed. The actionable automation opportunity is local to
this thread: add a regression assertion that every scalar role-reporting
surface returns a canonical role token or an explicitly documented role-set
shape, and include the MCP foundation test in the standard verification
surface when `mcp_surface/roles.py` changes.

## Owner Action Required

None for this NO-GO verdict.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
