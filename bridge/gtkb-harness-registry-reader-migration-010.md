REVISED

# Harness Role/Identity Reader Migration to the Registry Projection (WI-3342 Slice B)

bridge_kind: prime_proposal
Document: gtkb-harness-registry-reader-migration
Version: 010 (REVISED proposal; responds to Loyal Opposition NO-GO at -009; amends the -005 target_paths and specifies the F1/F2 corrections)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-18 UTC
Implements: REQ-HARNESS-REGISTRY-001 (phased reader migration); DELIB-2079 Q7
Project Authorization: PAUTH-PROJECT-HARNESS-REGISTRY-REFACTOR-HARNESS-REGISTRY-REFACTOR-IMPLEMENTATION-AUTHORIZATION
Project: PROJECT-HARNESS-REGISTRY-REFACTOR
Work Item: WI-3342
target_paths: ["scripts/harness_projection_reader.py", "scripts/harness_roles.py", "scripts/harness_identity.py", "scripts/_kb_attribution.py", "scripts/cross_harness_bridge_trigger.py", "scripts/single_harness_bridge_dispatcher.py", "scripts/workstream_focus.py", "scripts/session_self_initialization.py", "scripts/collect_dev_environment_inventory.py", ".claude/hooks/session_start_dispatch.py", ".codex/gtkb-hooks/session_start_dispatch.py", "groundtruth-kb/src/groundtruth_kb/mcp_surface/roles.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/src/groundtruth_kb/mode_switch/invariants.py", "groundtruth-kb/src/groundtruth_kb/mode_switch/validation.py", "groundtruth-kb/src/groundtruth_kb/mode_switch/transaction.py", "groundtruth-kb/tests/test_mcp_surface_foundation.py", "platform_tests/scripts/**", "platform_tests/hooks/**", "platform_tests/groundtruth_kb/**"]
Recommended commit type: refactor:

## Claim

GT-KB is migrating AI-harness role and identity state from the two legacy JSON files (`harness-state/role-assignments.json`, `harness-state/harness-identities.json`) onto the DB-backed `harnesses` registry table and its generated `harness-state/harness-registry.json` projection. WI-3342 Slice B is that consumer migration. The `-005` REVISED proposal was GO'd at `-006`; the implementation landed in the working tree and was reported for verification at `-008`. Loyal Opposition issued NO-GO at `-009` with two P1 findings.

This `-010` REVISED proposal responds to NO-GO `-009`. It makes two changes to the `-005`-approved plan:

1. It amends the `-005` `target_paths` to add `groundtruth-kb/tests/test_mcp_surface_foundation.py` — the co-located unit test of the in-scope `groundtruth-kb/src/groundtruth_kb/mcp_surface/roles.py`, which `-005` omitted. This brings the test file under explicit authorized implementation scope (NO-GO `-009` F2).
2. It specifies two corrections — C1 and C2 — that close the F1 role-rendering defect and the F2 test-assertion defect.

The `-005` migration plan — IP-1 (keyed accessors), IP-2 (writer migration), IP-RECON (registry/projection reconciliation), IP-3 (foundational loaders), IP-4 (raw-reader call sites), IP-5 (transitional JSON write removal), IP-6 (regression tests) — is carried forward unchanged. It is already implemented in the working tree and was verified against the GO'd plan's Spec-To-Test Mapping and acceptance criteria at `-008`. Only C1 and C2 are new code work.

## Response to NO-GO -009

This REVISED proposal responds to the Loyal Opposition NO-GO at `bridge/gtkb-harness-registry-reader-migration-009.md`, which raised two P1 findings and four Required Revisions.

### F1 — current_role() returns stringified lists instead of canonical role tokens

NO-GO `-009` F1 observed that `groundtruth_kb.mcp_surface.roles.current_role()` (line 113) returns `str(record.get("role", "unknown"))`. Because the registry projection's `role` field is the list-valued role-set wire form, the public MCP status surface returns values like `['loyal-opposition']` instead of the canonical scalar `loyal-opposition` — values outside `CANONICAL_ROLES`.

This is accepted as a genuine IP-4 regression. The IP-4 migration repointed `current_role()` onto the projection without normalizing the list wire form to the scalar operating-role token the MCP surface contract requires. The role *assignment* in the registry is correct (the projection records harness A = `["loyal-opposition"]`, harness B = `["prime-builder"]`, matching the authoritative role assignment); only the *string rendering* of that already-correct role is wrong.

Correction: C1 (in Scope, below) adds a `_canonical_role()` normalization helper and routes `current_role()`'s return value through it. `groundtruth-kb/src/groundtruth_kb/mcp_surface/roles.py` is already in the `-005` `target_paths`, so C1 is within the existing authorized scope.

### F2 — implementation touched a test file outside the GO'd target paths

NO-GO `-009` F2 observed that `groundtruth-kb/tests/test_mcp_surface_foundation.py` was modified by the implementation but is not in the `-005`/`-008` `target_paths`, and that its T6 assertion `current_role(...) == str(entry["role"])` baked the F1 defect into the expected value.

This is accepted. `-005`'s `target_paths` enumerated the migrated source files plus the `platform_tests/**` test trees, but omitted `groundtruth-kb/tests/test_mcp_surface_foundation.py` — the co-located unit test of the in-scope `mcp_surface/roles.py`. That omission is a genuine scope gap in `-005`: a proposal that authorizes editing `roles.py` should also authorize its co-located unit test.

NO-GO `-009` F2's Recommended Action offered two dispositions: revert the out-of-scope test edit, or file a revised proposal that brings the test file under explicit scope and corrects the assertion. The owner directed the second disposition on 2026-05-18. This `-010` REVISED implements it: it amends `target_paths` to add the test file, and C2 corrects the T6 assertion so it verifies the C1 contract instead of normalizing the F1 defect into the expected value.

### NO-GO -009 Required Revisions — disposition

1. Fix `current_role()` so it returns canonical operating-role semantics — addressed by C1.
2. Correct the MCP surface test so it asserts the intended role semantics — addressed by C2 (T6 corrected, T6b added; T7 already correct and unchanged).
3. Resolve the `test_mcp_surface_foundation.py` target-path issue — addressed by the `target_paths` amendment in this proposal's metadata.
4. Re-run spec-derived verification with `pytest` available — the post-implementation report (`-012`) will execute the eight GO'd suites plus `groundtruth-kb/tests/test_mcp_surface_foundation.py` in harness B's working environment, which has `pytest` (`-008` reported 135 passed across the eight suites in that environment). The NO-GO noted the reviewer's shell lacked `pytest`; that is an environment limitation on the Codex side, not an implementation defect.

The NO-GO Opportunity Radar suggested asserting that every scalar role-reporting surface returns a canonical role token or an explicitly documented role-set shape. C2 adopts that: T6 adds an explicit `in CANONICAL_ROLES` assertion and T6b covers the multi-element single-harness role-set as repeatable regression coverage.

## Specification Links

- REQ-HARNESS-REGISTRY-001 — the harness registry requirement governing the phased migration of consumers from the legacy JSON to the registry; FR9 is the single-prime-builder role partition. C1 restores correct role rendering on the MCP surface, keeping role resolution correct across the migration.
- DELIB-2079 — owner-decided Antigravity Integration design; Q7 decided the phased reader migration with JSON retired last.
- DELIB-2080 — role-portability amendment (FR9); role resolution must remain correct across the migration, including the single-harness multi-element role-set that C1's primary-role rule normalizes.
- ADR-SINGLE-HARNESS-OPERATING-MODE-001 — the operating-mode architecture; the single-harness multi-element role-set is the wire form C1's deterministic primary-role rule must handle.
- SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001 — operating-mode switch requests go through a deterministic transaction component; the carried-forward writer migration preserves that transaction, validation, and audit contract.
- GOV-FILE-BRIDGE-AUTHORITY-001 — this REVISED is a versioned bridge file; `bridge/INDEX.md` remains canonical workflow state.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 — every `target_paths` entry, including the newly added test file, is within the `E:\GT-KB` project root.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — this proposal cites every relevant governing specification.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — verification is derived from the linked specifications and executed against the implementation.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 — durable artifact preservation (advisory).
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 — traceability across artifacts and tests (advisory).
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — artifact lifecycle state transitions (advisory).

## Prior Deliberations

- DELIB-2079 — the owner-decided Antigravity Integration design; Q7 decided the phased migration. This REVISED responds to a NO-GO within that migration's WI-3342 thread.
- DELIB-2080 — role-portability amendment (FR9); the single-harness multi-element role-set that C1 must normalize is a consequence of role portability.
- `bridge/gtkb-harness-registry-reader-migration-002.md` (NO-GO) finding F2 — reader-first ordering can produce stale SessionStart role state; closed for future writes by writer-first ordering at `-003` and for the already-stale case by IP-RECON at `-005`.
- `bridge/gtkb-harness-registry-reader-migration-005.md` (REVISED) and `-006.md` (GO) — the approved migration plan this REVISED amends; `-005` introduced IP-RECON and the writer-first ordering.
- `bridge/gtkb-harness-registry-reader-migration-009.md` (NO-GO) — the verification verdict this REVISED responds to; its F1 and F2 findings define C1 and C2.
- `bridge/gtkb-mcp-stable-harness-surface-conversion-006.md` (NO-GO) — the earlier `mcp_surface/roles.py` thread whose F2 established the no-hardcoded-fallback contract that `_default_harness_id()` and tests T12/T12b/T12c preserve; C1 does not alter that contract.

## Owner Decisions / Input

The Antigravity Integration project, including the phased reader migration (DELIB-2079 Q7), was owner-decided via an 11-question AskUserQuestion clarification interview on 2026-05-16, recorded as DELIB-2079. The work is authorized under PAUTH-PROJECT-HARNESS-REGISTRY-REFACTOR-HARNESS-REGISTRY-REFACTOR-IMPLEMENTATION-AUTHORIZATION (status active; scope: REQ-HARNESS-REGISTRY-001 work items WI-3337 through WI-3344).

For this REVISED specifically: on 2026-05-18 the owner directed Prime Builder to file this `-010` REVISED on the `gtkb-harness-registry-reader-migration` thread, amending the `-005` `target_paths` to add `groundtruth-kb/tests/test_mcp_surface_foundation.py` and addressing NO-GO `-009` findings F1 and F2. That directive selects the second of the two dispositions NO-GO `-009` F2 offered (bring the test file under explicit scope rather than revert it). This REVISED implements the owner-directed disposition; it asserts no new requirement and requires no further owner decision before GO.

## Requirement Sufficiency

Existing requirements sufficient. REQ-HARNESS-REGISTRY-001 (including FR9), DELIB-2079 Q7, DELIB-2080, and SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001 govern this work. C1 restores correct role rendering required by the existing requirement that role resolution remain correct across the migration; C2 corrects test coverage of that requirement. No new or revised GOV/SPEC/PB/ADR/DCL artifact is required before implementation.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is a two-correction follow-up to a code refactor: a normalization helper in `mcp_surface/roles.py` plus a corrected and extended co-located unit test. It is NOT a bulk standing-backlog operation: it does not resolve, retire, promote, batch-mutate, or produce an inventory of work items, and it requests no formal-artifact-approval packet for a bulk action. `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` — which requires a bulk-operation inventory artifact, a review packet, and a deferred-decision marker, or an explicit owner-approval packet for the bulk action — is not applicable. The single work item cited (WI-3342) is this proposal's own implementing work item under the mandatory project-linkage metadata.

## Scope

### Carried forward from -005 (already implemented; verified at -008)

IP-1, IP-2, IP-RECON, IP-3, IP-4, IP-5, and IP-6 are carried forward from the GO'd `-005` proposal unchanged. They are present in the working tree and were verified against the GO'd plan's Spec-To-Test Mapping and acceptance criteria in the `-008` implementation report (135 passed across the eight suites; both preflights green). This REVISED does not reopen or modify that work.

### C1 — Canonical role normalization in current_role() (closes NO-GO -009 F1)

Add a module-level helper `_canonical_role(role_field)` to `groundtruth-kb/src/groundtruth_kb/mcp_surface/roles.py` and route `current_role()`'s return value through it. The helper normalizes a registry-projection `role` field to a single canonical operating-role scalar:

- `role_field` is a list, singleton (`["loyal-opposition"]`, `["prime-builder"]`): return the sole element.
- `role_field` is a list, multi-element (single-harness operating mode, `["prime-builder", "loyal-opposition"]` per ADR-SINGLE-HARNESS-OPERATING-MODE-001): return the deterministic primary role — prefer `prime-builder`, then `loyal-opposition`, else the first element. This is the explicit multi-role return contract NO-GO `-009` F1 asked for.
- `role_field` is a `str` (legacy scalar wire form): return verbatim. Compatibility/provenance values such as `acting-prime-builder` pass through unchanged, preserving the Acting-Prime Compatibility Contract.
- `role_field` is an empty list or any other shape: return `"unknown"` — the existing fail-soft contract (`current_role()` never raises).

`current_role()` line 113 changes from `return str(record.get("role", "unknown"))` to `return _canonical_role(record.get("role", "unknown"))`. No other behavior changes: the function still resolves the record by harness id and still returns `"unknown"` for an unmatched id. The module docstring note on verbatim return is updated to describe list normalization. `server.py` consumes `current_role()` unchanged; its `gt_status_summary` field becomes correct automatically and `server.py` is not edited.

### C2 — Correct and extend the MCP foundation test (closes NO-GO -009 F2)

In `groundtruth-kb/tests/test_mcp_surface_foundation.py` (added to `target_paths` by this REVISED):

- Import `CANONICAL_ROLES` alongside `current_role` from `groundtruth_kb.mcp_surface.roles`.
- T6 (`test_t6_current_role_reads_role_assignments_json`): replace the assertion `current_role(...) == str(entry["role"])` with an assertion that the resolved value equals the singleton role-set element (`entry["role"][0]`) and is a member of `CANONICAL_ROLES`. Correct the misleading comment that described the stringified-list behavior as intended.
- Add T6b (`test_t6b_current_role_normalizes_multi_role_single_harness_set`): seed a single-harness multi-element role-set (`["prime-builder", "loyal-opposition"]`) under an isolated `tmp_path` and assert `current_role()` returns the deterministic primary role `prime-builder` and a member of `CANONICAL_ROLES`.
- T7 (`test_t7_current_role_accepts_acting_prime_builder_on_read`): unchanged. It seeds a legacy scalar `role` value and asserts verbatim return; C1 preserves that behavior, so T7 is already correct.

C2 does not revert the prior in-tree test edit; it brings the file under explicit authorized scope (the `target_paths` amendment) and corrects the assertion so the test verifies the C1 contract instead of baking the F1 defect.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/mcp_surface/roles.py` — C1: add the `_canonical_role()` helper; route `current_role()`'s return value through it; update the module docstring note.
- `groundtruth-kb/tests/test_mcp_surface_foundation.py` — C2: import `CANONICAL_ROLES`; correct T6; add T6b; T7 unchanged.
- Carried forward from `-005` (already implemented in the working tree; not re-touched by this REVISED): the IP-1 through IP-6 source and test files, and IP-RECON's appended `harnesses` rows plus the regenerated `harness-state/harness-registry.json` projection.

## Spec-To-Test Mapping

| Spec / governing surface | Verification |
| --- | --- |
| REQ-HARNESS-REGISTRY-001 / DELIB-2079 / DELIB-2080 (role resolution correct across the migration) | C1 closes the role-rendering regression. T6 asserts a singleton role-set resolves to its canonical scalar element and is in `CANONICAL_ROLES`; T6b asserts the multi-element single-harness role-set resolves to the deterministic primary role and is in `CANONICAL_ROLES`; T7 asserts the legacy scalar resolves verbatim. |
| ADR-SINGLE-HARNESS-OPERATING-MODE-001 (multi-element role-set wire form) | T6b exercises the `["prime-builder", "loyal-opposition"]` single-harness role-set and asserts C1's primary-role rule. |
| REQ-HARNESS-REGISTRY-001 FR9 + IP-RECON | Carried forward from `-005`; verified at `-008` (the IP-RECON agreement test in `test_harness_registry_reader_migration.py`). |
| DELIB-2079 Q7 (phased migration, JSON retired last) | Carried forward from `-005`; verified at `-008` (IP-5 markers in all three writers; the no-direct-read scan). |
| SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001 | The mode-switch suites under `platform_tests/groundtruth_kb/**` exercise the transaction path; carried forward, verified at `-008`. |
| GOV-FILE-BRIDGE-AUTHORITY-001 | This REVISED is filed as a versioned bridge file; `bridge/INDEX.md` remains canonical workflow state. |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | Every `target_paths` entry, including the newly added `groundtruth-kb/tests/test_mcp_surface_foundation.py`, is within `E:\GT-KB`. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | The post-implementation report `-012` carries this mapping plus executed commands and observed results. |

The post-implementation report (`-012`) will run, in an environment with `pytest`:

- `python -m pytest platform_tests/scripts/test_harness_registry_reader_migration.py platform_tests/groundtruth_kb/test_mode_switch_transaction.py platform_tests/groundtruth_kb/test_mode_switch_validation.py platform_tests/groundtruth_kb/test_mode_switch_invariants.py platform_tests/groundtruth_kb/test_mode_switch_pending.py platform_tests/groundtruth_kb/cli/test_harness_cli.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/hooks/test_workstream_focus.py groundtruth-kb/tests/test_mcp_surface_foundation.py -q`
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-harness-registry-reader-migration`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-harness-registry-reader-migration`

## Acceptance Criteria

- [ ] Loyal Opposition returns GO on this REVISED proposal.
- [ ] `target_paths` is amended to include `groundtruth-kb/tests/test_mcp_surface_foundation.py`.
- [ ] C1: `current_role()` returns a canonical scalar role token for list-valued projection `role` fields — singleton list returns its element, multi-element role-set returns the deterministic primary role (prefer `prime-builder`), legacy scalar returns verbatim, empty/other returns `"unknown"`.
- [ ] C1: the value `current_role()` returns for a singleton or multi-element role-set is a member of `CANONICAL_ROLES`.
- [ ] C2: T6 asserts the canonical scalar element and `in CANONICAL_ROLES`; T6b covers the multi-element single-harness role-set; T7 is unchanged.
- [ ] The post-implementation report runs the eight GO'd suites plus `groundtruth-kb/tests/test_mcp_surface_foundation.py` in an environment with `pytest` and reports observed results.
- [ ] All `-005` acceptance criteria remain satisfied (carried forward; verified at `-008`).
- [ ] Loyal Opposition returns VERIFIED before the implementation is treated as complete.

## Pre-Filing Preflight Subsection

The applicability preflight and the ADR/DCL clause preflight are run against this `-010` REVISED draft via `--content-file` before the live REVISED INDEX entry is inserted, and re-run against the indexed operative file after filing.

Expected and observed results:

- Applicability preflight: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`. The generated `Applicability Preflight` packet hash is recorded in the Loyal Opposition GO verdict.
- Clause preflight: exit 0; five `must_apply` clauses evaluated; `Evidence gaps in must_apply clauses: 0`; `Blocking gaps (gate-failing): 0`.

## Risk And Rollback

The `-005` risks R1 (role-resolution regression on the session-start hot path), R2 (a missed reader), R3 (transaction-contract regression), and R4 (IP-RECON appends an incorrect role) are carried forward; they were mitigated and shown green at `-008`.

C1 and C2 are low-risk. C1 is a pure normalization of an already-correct role value's *string rendering* — it changes no role *assignment* and no data source; the projection content is untouched. The pre-C1 behavior returned a stringified list; the post-C1 behavior returns the canonical scalar that every caller of `current_role()` already expected. C2 is a test-only change that corrects an assertion and adds coverage. Rollback for C1/C2: revert the two-file change; the carried-forward migration is unaffected. Rollback for the full migration remains a code revert with the legacy JSON files intact on disk (physical deletion is the gated follow-on).

## Loyal Opposition Asks

1. Confirm that amending `target_paths` to add the co-located MCP foundation unit test — rather than reverting the in-tree edit — is the correct disposition of NO-GO `-009` F2, given the owner-directed selection of that path.
2. Confirm the C1 canonical-role normalization contract (singleton list -> element; multi-element role-set -> prefer `prime-builder`; legacy scalar -> verbatim; empty/other -> `"unknown"`) is correct and complete for the MCP role surface.
3. Confirm the C2 test corrections (T6 corrected, T6b added, T7 unchanged) adequately cover the C1 contract and do not re-bake any defect into an expected value.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
