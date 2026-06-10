GO

# Loyal Opposition Review: gtkb-harness-registry-reader-migration-010

bridge_kind: lo_verdict
Document: gtkb-harness-registry-reader-migration
Version: 011
Author: Loyal Opposition (Codex, harness A)
Date: 2026-05-18 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-harness-registry-reader-migration-010.md

## Decision

GO. The `-010` REVISED proposal adequately responds to the `-009` NO-GO findings.

The proposal brings `groundtruth-kb/tests/test_mcp_surface_foundation.py` under explicit `target_paths`, fixes the MCP role-rendering defect by specifying scalar normalization for list-valued registry roles, and adds regression coverage for singleton and multi-element role-set inputs. It also carries forward the prior `-005` migration scope and requires the post-implementation report to rerun the eight previously GO'd suites plus the MCP foundation test.

No owner action is required before implementation.

## Applicability Preflight

```text
## Applicability Preflight

- packet_hash: `sha256:9b21f031efa573fef078a1f126c1b6661a254c3c67f86a66ee5c21ded843cfd1`
- bridge_document_name: `gtkb-harness-registry-reader-migration`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-harness-registry-reader-migration-010.md`
- operative_file: `bridge/gtkb-harness-registry-reader-migration-010.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:groundtruth-kb/src/groundtruth_kb/project/** |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-harness-registry-reader-migration`
- Operative file: `bridge\gtkb-harness-registry-reader-migration-010.md`
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

## Prior Deliberations

Deliberation search was run through the DB API for:

- `harness registry reader migration WI-3342 REQ-HARNESS-REGISTRY-001`
- `role portability DELIB-2080 single harness prime builder loyal opposition`
- `current_role MCP surface canonical role token harness registry`

The semantic search returned no additional hits in this shell. Direct retrieval confirmed the proposal-cited deliberations:

- `DELIB-2079` - Antigravity Integration project design, including the DB-backed harness registry and phased migration.
- `DELIB-2080` - role-portability amendment and single-prime-builder invariant.

Relevant bridge-thread prior deliberations also remain:

- `bridge/gtkb-harness-registry-reader-migration-009.md` - NO-GO findings F1 and F2, which define the correction scope.
- `bridge/gtkb-harness-registry-reader-migration-005.md` and `-006.md` - approved migration plan carried forward by this revision.

## Evidence Review

### Live Queue And Thread State

- `bridge/INDEX.md` latest status for `gtkb-harness-registry-reader-migration` was `REVISED: bridge/gtkb-harness-registry-reader-migration-010.md` before this verdict.
- `python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-harness-registry-reader-migration --format json --preview-lines 400` loaded the full thread chain with no drift: `NEW -001`, `NO-GO -002`, `REVISED -003`, `GO -004`, `REVISED -005`, `GO -006`, `NEW -007`, `NEW -008`, `NO-GO -009`, `REVISED -010`.

### Mechanical Gates

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-harness-registry-reader-migration` passed with `missing_required_specs: []` and `missing_advisory_specs: []`.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-harness-registry-reader-migration` exited 0 with 5 must-apply clauses, 0 evidence gaps, and 0 blocking gaps.

### Response To NO-GO -009

- `-009` F1 required `current_role()` to return canonical operating-role semantics from list-valued projection records. `-010` C1 adds `_canonical_role()` and routes the `current_role()` return through it.
- `-009` F2 required the MCP surface test mutation to be either reverted or brought under explicit revised scope and verified. `-010` amends `target_paths` to include `groundtruth-kb/tests/test_mcp_surface_foundation.py` and requires the post-implementation report to run that test.
- `-010` C2 replaces the defective `str(entry["role"])` test expectation with canonical scalar assertions and adds T6b for the single-harness multi-role role-set.

### Role-Set Semantics

The C1 primary-role rule is acceptable for this MCP `current_role()` scalar display surface. It is consistent with the existing `scripts/harness_roles.py::primary_role()` Prime-first scalar helper. It does not replace the canonical role-set membership and role-slot helpers used by routing/topology code; `groundtruth_kb.mode_switch.derive.role_slot_from_active_harness()` still returns `shared` for multi-element single-harness role-sets.

Implementation must keep that distinction explicit in the `current_role()` docstring or nearby helper comments so future MCP mutation-gate work does not confuse a scalar primary role with full role-set authority.

## Specification-Linkage Review

The proposal cites the relevant governing surfaces for this correction:

- `REQ-HARNESS-REGISTRY-001`, `DELIB-2079`, and `DELIB-2080` for the harness-registry migration and role-portability semantics.
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` for the multi-element role-set case.
- `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` for the carried-forward writer/transaction scope.
- `GOV-FILE-BRIDGE-AUTHORITY-001`, `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, and `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` for bridge, root-boundary, proposal-linkage, and verification gates.

The spec-to-test mapping is adequate for GO. Verification remains blocked until the post-implementation report executes the mapped commands and reports observed results.

## Implementation Conditions

These conditions are non-blocking for GO but blocking for later VERIFIED:

1. `groundtruth-kb/src/groundtruth_kb/mcp_surface/roles.py` must normalize singleton list role values to their scalar token, preserve legacy scalar values such as `acting-prime-builder`, return `unknown` for empty or malformed shapes, and implement the documented primary-role rule for multi-element role-sets.
2. `groundtruth-kb/tests/test_mcp_surface_foundation.py` must import `CANONICAL_ROLES`, correct T6, add T6b, and leave T7's legacy scalar compatibility behavior intact.
3. The post-implementation report must run the eight previously GO'd suites plus `groundtruth-kb/tests/test_mcp_surface_foundation.py` in an environment with `pytest`, then report observed results.
4. The implementation report must preserve the scalar-primary-role versus role-set-membership distinction; routing/topology code must continue to use membership/role-slot helpers where full role authority matters.

## Opportunity Radar

No separate advisory filed. The material opportunity from `-009` is already included in this revision: C2 adds deterministic regression coverage for scalar role-reporting surfaces, including the single-harness multi-element role-set case.

## Commands Executed

```text
Get-Content -Raw bridge/INDEX.md
Result: latest status for gtkb-harness-registry-reader-migration was REVISED at bridge/gtkb-harness-registry-reader-migration-010.md before this verdict.

python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-harness-registry-reader-migration --format json --preview-lines 400
Result: full thread loaded; no drift.

Get-Content -Raw bridge/gtkb-harness-registry-reader-migration-010.md
Result: reviewed latest REVISED proposal.

Get-Content -Raw bridge/gtkb-harness-registry-reader-migration-009.md
Result: reviewed prior NO-GO findings and required revisions.

python scripts/bridge_applicability_preflight.py --bridge-id gtkb-harness-registry-reader-migration
Result: preflight_passed true; missing_required_specs []; missing_advisory_specs [].

python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-harness-registry-reader-migration
Result: exit 0; evidence gaps 0; blocking gaps 0.

$env:PYTHONPATH='E:\GT-KB\groundtruth-kb\src'; python - <<DB API deliberation search>>
Result: semantic search returned no additional hits; direct get_deliberation confirmed DELIB-2079 and DELIB-2080.

rg checks across bridge proposal, prior NO-GO, role helpers, MCP role surface, and MCP tests
Result: confirmed target-path amendment, C1/C2 mapping, current defect location, and existing primary-role / role-slot helper semantics.
```

## Owner Action Required

None for this GO verdict.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
