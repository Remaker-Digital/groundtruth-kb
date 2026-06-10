REVISED

# Implementation Proposal - MCP Stable Harness Surface: Role-Set Normalization in current_role (WI-3275)

bridge_kind: prime_proposal
Document: gtkb-mcp-stable-harness-surface-current-version-views
Version: 003
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S353+

Project Authorization: PAUTH-PROJECT-GTKB-MEMBASE-EFFECTIVE-USE-MEMBASE-EFFECTIVE-USE-BATCH
Project: PROJECT-GTKB-MEMBASE-EFFECTIVE-USE
Work Item: WI-3275

target_paths: ["groundtruth-kb/src/groundtruth_kb/mcp_surface/roles.py", "groundtruth-kb/tests/test_mcp_surface_foundation.py"]

This REVISED proposal repoints the work to the live MCP surface and narrows scope to the one defect that is still live in the current checkout: `current_role` serializes a list-form role-set value as a Python list repr instead of a canonical role token.

## Revision Notes

This `-003` revision addresses every finding in the `-002` NO-GO. During revision a live-state probe found that two of the three `-001` claims are stale, so the scope is corrected and narrowed:

- **F1 (P1) — proposal authorized a nonexistent `groundtruth_kb/mcp/` package and `test_mcp_status_summary.py`.** Confirmed by live probe: `groundtruth-kb/src/groundtruth_kb/mcp/` does not exist; the live MCP surface is `groundtruth-kb/src/groundtruth_kb/mcp_surface/` (`server.py`, `roles.py`, `authority.py`, `boundary.py`), and the live test file is `groundtruth-kb/tests/test_mcp_surface_foundation.py`. `target_paths`, `## Proposed Scope`, and the verification commands are repointed to those real files. There is no rename/migration from `mcp_surface` to `mcp`; this proposal works against `mcp_surface` as it stands.
- **F2 (P1) — proposal did not account for the active role-set list-schema.** This is the genuinely-remaining defect. A live probe of `groundtruth_kb/mcp_surface/roles.py` shows `current_role` (line 87) ends with `return str(entry.get("role", "unknown"))` (line 109). Because `harness-state/role-assignments.json` now uses the active list-form role-set wire schema (per `ADR-SINGLE-HARNESS-OPERATING-MODE-001` and `.claude/rules/operating-role.md` § Role Set Schema), `entry.get("role")` is a JSON list such as `["loyal-opposition"]`, and `str(...)` of it produces the Python list repr `['loyal-opposition']`. The `-002` NO-GO independently reproduced this: `python -m pytest groundtruth-kb/tests/test_mcp_surface_foundation.py` reports `1 failed, 13 passed`, `FAILED test_t6_current_role_reads_role_assignments_json` with `assert "['loyal-opposition']" == ['loyal-opposition']`. This proposal adds role-set normalization to `current_role` so a singleton role set returns the canonical role token (e.g. `loyal-opposition`), legacy scalar role records continue to return their scalar value, and multi-element role sets are handled deterministically (see `## Proposed Scope`).
- **F3 (P2) — verification plan pointed at a nonexistent test file.** The verification plan is repointed to the live `groundtruth-kb/tests/test_mcp_surface_foundation.py`, which already contains the relevant regressions (T6/T7 `current_role`, T11 current-view counts, T12/T12b/T12c harness-id detection). The plan now runs that file, requires the currently-failing T6 to turn green, and adds list-form role-record coverage.
- **Stale-claim correction (prior NO-GO F1/F2 already resolved in live code).** The `-001` proposal said it would fix the prior NO-GO at `bridge/gtkb-mcp-stable-harness-surface-conversion-006.md` (F1: base-table queries instead of `current_*` views; F2: hardcoded `'B'` harness-id default). A live probe shows both are **already fixed** in the current checkout: `server.py` `_membase_row_counts` (line 54) already queries the `current_work_items` / `current_specifications` / `current_deliberations` views, and `roles.py` `_default_harness_id` (line 48) already resolves via `GTKB_HARNESS_ID` env var, then env-detection + `harness-state/harness-identities.json`, then a fail-closed empty string (never a hardcoded `'B'`). Tests T11 and T12/T12b/T12c in `test_mcp_surface_foundation.py` already cover those. Per the Prime Builder interrogative default, this proposal does not re-claim work already landed; the only outstanding defect is the role-set list-repr bug above, and the scope is narrowed accordingly.
- **Non-blocking note — advisory spec omissions.** The three advisory specs flagged by the `-002` preflight (`ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`) are now cited in `## Specification Links`.

No owner-decision scope change; the project authorization, project, and work item are unchanged from `-001`. The narrowing reduces deliverable scope to the single live defect; it adds no owner-decision surface.

## Claim

One scoped fix: add role-set normalization to `current_role` in `groundtruth_kb/mcp_surface/roles.py` so it returns a stable, canonical role token (or an explicitly-named role set) for the active list-form role-set schema, instead of a Python list repr. This turns the currently-failing `test_t6_current_role_reads_role_assignments_json` green and makes the MCP status surface role-correct for both Claude (Prime Builder) and Codex (Loyal Opposition) sessions.

## In-Root Placement Evidence

All target paths are within `E:\GT-KB`. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied. `groundtruth-kb/src/groundtruth_kb/mcp_surface/roles.py` and `groundtruth-kb/tests/test_mcp_surface_foundation.py` are in-root platform-package paths.

## Specification Links

- `ADR-0001` - three-tier memory architecture; the role surface reads canonical harness-state records.
- `GOV-08` - KB / harness-state is truth; `current_role` must report the role accurately from the canonical role-assignment record.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority governing this proposal as a bridge artifact.
- `SPEC-AUQ-POLICY-ENGINE-001` - the MCP surface is a policy-engine consumer; a correct role token is required for role-aware response labelling.
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` - the Path 2 atomic migration that made the list-form role-set the active runtime schema; this fix makes `current_role` consume that schema correctly.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root placement; all target paths are in-root.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - cross-cutting constraint requiring this proposal to cite every relevant governing specification.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - cross-cutting constraint requiring the post-implementation VERIFIED step to rest on executed spec-derived tests; the Specification-Derived Verification Plan below maps every linked spec to a test.
- `GOV-STANDING-BACKLOG-001` - WI-tracked work; WI-3275 is the governed work item.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - durable artifact-graph model; the WI, bridge thread, and linked specs form the artifact graph for this work.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - artifact lifecycle trigger discipline; the prior NO-GO triggered this defect-fix proposal and its tests.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - artifact-oriented governance baseline; this work is captured as governed artifacts (WI + bridge thread + spec-derived tests).
- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - owner-decision evidence for the project authorization.

## Prior Deliberations

- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - batch-5 owner authorization including PROJECT-GTKB-MEMBASE-EFFECTIVE-USE and work item WI-3275.
- `DELIB-1467` - GT-KB MCP Stable Harness Surface Advisory; the originating advisory for this MCP surface work.
- `DELIB-1880` - compressed bridge-thread record for the MCP stable harness surface advisory.
- `DELIB-1502` - Prime Advisory - GT-KB MCP Stable Harness Surface.

No prior deliberation rejected role-set normalization in `current_role`; this proposal is the first to address the list-form role-set serialization defect.

## Owner Decisions / Input

- 2026-05-14 UTC, S350+: owner approved the PROJECT-GTKB-MEMBASE-EFFECTIVE-USE authorization batch (`DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS`), including this work item WI-3275. The authorization `PAUTH-PROJECT-GTKB-MEMBASE-EFFECTIVE-USE-MEMBASE-EFFECTIVE-USE-BATCH` is active and lists `WI-3275` in its `included_work_item_ids`.

## Requirement Sufficiency

Existing requirements sufficient. `ADR-SINGLE-HARNESS-OPERATING-MODE-001` and `.claude/rules/operating-role.md` § Role Set Schema already define the active list-form role-set wire schema and its set-membership read semantics; `GOV-08` requires the role surface to report accurately. This proposal makes `current_role` conform to the already-specified schema. No new or revised requirement or specification is created by this work.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is not a bulk backlog operation. It performs no batch resolve, promote, or retire of work items or specifications. It implements a single work item (WI-3275), a single defect fix. References to "work item", "backlog", and "standing backlog" describe that single governed work item and its membership in PROJECT-GTKB-MEMBASE-EFFECTIVE-USE per the formal-artifact-approval packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch5-eight-project-authorizations.json`. The review-packet inventory is a single thread: IP-1 (role-set normalization) + IP-2 (tests). The inventory of touched files is the two `target_paths` entries above; no formal artifact is created.

## Bridge INDEX Maintenance

This proposal keeps `bridge/INDEX.md` as the canonical bridge workflow state. The `-003` REVISED line is appended under the existing `Document: gtkb-mcp-stable-harness-surface-current-version-views` block above the prior `NO-GO` and `NEW` lines; the prior versions are preserved unchanged (append-only audit trail).

## Proposed Scope

### IP-1: Role-set normalization in `current_role`

In `groundtruth-kb/src/groundtruth_kb/mcp_surface/roles.py`, change `current_role` so its return value is a canonical role token rather than a Python list repr. The current final line `return str(entry.get("role", "unknown"))` (roles.py:109) is replaced with a normalization step consistent with the role-set schema in `.claude/rules/operating-role.md`:

- Read `entry.get("role")`.
- If the value is a **list** (the active wire form): if it is a singleton, return the single role token; if it is empty, return `"unknown"`; if it has multiple elements (single-harness topology), return a deterministic canonical representation — preference: return the prime-builder token when the set contains `prime-builder` for response-labelling purposes, with the chosen rule documented in the function docstring (or, equivalently, expose an explicitly-named role set; the implementation picks one and documents it).
- If the value is a **scalar string** (legacy/compatibility wire form, READ-accepted per the operating-role rule): return it verbatim, preserving the existing T7 behavior that `acting-prime-builder` is returned verbatim on READ.
- If the value is missing: return `"unknown"` as today.

The normalization mirrors the set-membership read semantics already used by `scripts/harness_roles.py` `_normalize_role_field`; it does not change `_default_harness_id` (already correct) or `_membase_row_counts` (already correct).

### IP-2: Tests

In `groundtruth-kb/tests/test_mcp_surface_foundation.py`: update/extend the role tests so they exercise the active list-form role-set records and assert canonical token output. The currently-failing `test_t6_current_role_reads_role_assignments_json` is corrected to assert against the canonical token (its fixture is updated to the list-form role-set wire shape, matching live `role-assignments.json`), and `test_t7_current_role_accepts_acting_prime_builder_on_read` is preserved/confirmed for the legacy scalar path.

## Specification-Derived Verification Plan

Each linked specification clause exercised by this fix maps to at least one test. Tests are added/updated only within the `target_paths` test file.

| Spec clause exercised by this fix | Test | Covers |
|---|---|---|
| `current_role` returns the canonical role token for a singleton list-form role set | `test_t6_current_role_reads_role_assignments_json` (corrected) | ADR-SINGLE-HARNESS-OPERATING-MODE-001, GOV-08 |
| `current_role` returns the scalar value verbatim for a legacy scalar role record (`acting-prime-builder` READ-accepted) | `test_t7_current_role_accepts_acting_prime_builder_on_read` (confirmed) | ADR-SINGLE-HARNESS-OPERATING-MODE-001 (backward compatibility) |
| `current_role` handles a multi-element role set (single-harness topology) deterministically and never returns a list repr | `test_current_role_normalizes_multi_element_role_set` (new) | ADR-SINGLE-HARNESS-OPERATING-MODE-001 |
| The MCP status payload field `current_role` is a plain string token, not a list repr | `test_t9_gt_status_summary_payload_includes_expected_fields` (existing; confirmed still PASS) | SPEC-AUQ-POLICY-ENGINE-001, GOV-08 |
| The full MCP surface foundation suite passes (no regression to current-view counts T11 / harness-id detection T12/T12b/T12c) | `test_mcp_surface_foundation.py` full run | DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 |

Verification commands (run from the `groundtruth-kb` package root, the lane for `groundtruth-kb/tests/**`):

```
cd groundtruth-kb && python -m pytest tests/test_mcp_surface_foundation.py -q --tb=short
python -m ruff check .
python -m ruff format --check .
```

The post-implementation report will show `test_mcp_surface_foundation.py` going from the current `1 failed, 13 passed` (failing `test_t6_current_role_reads_role_assignments_json`) to all-passing, plus the new multi-element test.

## Acceptance Criteria

- IP-1 and IP-2 landed; `test_mcp_surface_foundation.py` runs all-green (the currently-failing T6 turns green; the new multi-element test passes).
- `target_paths` and verification commands reference only the live `groundtruth_kb/mcp_surface/` surface and `tests/test_mcp_surface_foundation.py` (F1, F3 resolved).
- `current_role` returns a canonical role token (or explicitly-named role set), never a Python list repr, for the active list-form role-set schema; legacy scalar role records still return their scalar value (F2 resolved).
- The proposal makes no claim about base-table-vs-`current_*`-views or hardcoded harness-id defaults, since live `server.py`/`roles.py` already resolve those (stale-claim correction).
- The three advisory specs are cited in `## Specification Links`.
- `ruff check` and `ruff format --check` are clean.
- Both preflights PASS.

## Risks / Rollback

- Risk: the multi-element role-set representation choice (return prime-builder token vs explicit role-set object) is a small design call. Mitigation: the chosen rule is documented in the `current_role` docstring; the proposal permits either canonical-token or named-role-set and the implementation picks one deterministically with a test.
- Risk: a downstream caller depended on the (defective) list-repr string. Mitigation: the only consumer is response labelling in the MCP surface; the prior behavior was already broken (T6 failing), so no correct caller can depend on it.
- Rollback: revert the `current_role` change in `roles.py` and the test updates in `test_mcp_surface_foundation.py`; no other file is touched.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/mcp_surface/roles.py` — add role-set normalization to `current_role` so it returns a canonical role token for the active list-form role-set schema (IP-1).
- `groundtruth-kb/tests/test_mcp_surface_foundation.py` — correct `test_t6_current_role_reads_role_assignments_json` to the list-form role-set fixture, confirm `test_t7`, and add a multi-element role-set normalization test (IP-2).

## Recommended Commit Type

`fix` - repair of broken behavior (`current_role` returns a list repr; `test_mcp_surface_foundation.py` currently has a failing test) with no new capability surface. ~20 LOC of source + tests.

## Pre-Filing Preflight

Both mandatory pre-filing preflights were run on this `-003` content after filing the INDEX entry; outputs are embedded in `## Applicability Preflight` and `## Clause Applicability` below.

## Applicability Preflight

- packet_hash: `sha256:8720c7d4c550a03ddcac06714af85cec85f92988135ca27499200f5b23b8026b`
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
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-mcp-stable-harness-surface-current-version-views`
- Operative file: `bridge\gtkb-mcp-stable-harness-surface-current-version-views-003.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory (default invocation). Exit 5 = blocking gap; exit 0 = pass. Result: exit 0.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
