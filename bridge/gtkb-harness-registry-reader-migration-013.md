NEW

# Post-Implementation Report: Harness Registry Reader Migration — C1/C2 Corrections (WI-3342)

bridge_kind: implementation_report
Document: gtkb-harness-registry-reader-migration
Version: 013 (post-implementation report; supersedes -012, which lacked an explicit GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL evidence line; implements C1 and C2 from the -010 REVISED proposal; responds to Loyal Opposition GO at -011)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-18 UTC
Implements: REQ-HARNESS-REGISTRY-001 (phased reader migration); DELIB-2079 Q7
Project Authorization: PAUTH-PROJECT-HARNESS-REGISTRY-REFACTOR-HARNESS-REGISTRY-REFACTOR-IMPLEMENTATION-AUTHORIZATION
Project: PROJECT-HARNESS-REGISTRY-REFACTOR
Work Item: WI-3342
Recommended commit type: refactor:

## Summary

This post-implementation report covers the C1 and C2 corrections specified in the `-010` REVISED proposal and approved by Loyal Opposition GO at `-011`. C1 closes NO-GO `-009` finding F1 (the MCP `current_role()` surface returned stringified role-set lists instead of canonical scalar role tokens). C2 closes NO-GO `-009` finding F2 (the MCP foundation unit test baked the F1 defect into its expected value; the `-010` REVISED amended `target_paths` to bring the test file under explicit authorized scope).

Only `groundtruth-kb/src/groundtruth_kb/mcp_surface/roles.py` (C1) and `groundtruth-kb/tests/test_mcp_surface_foundation.py` (C2) were edited, both under impl-auth packet `sha256:1086cef97c072c41110541e7a61096c4dca42ec0e7683b1b05c7080c77c046e3` (minted against GO `-011`, 2026-05-18T16:36:43Z). The carried-forward `-005` migration (IP-1 through IP-6 plus IP-RECON) is unchanged; it was verified at `-008` and remains green in this report's eight-suite re-run.

Verification: 150 passed, 3 skipped, 2 xfailed across the eight GO'd suites plus `groundtruth-kb/tests/test_mcp_surface_foundation.py`; both the applicability preflight and the ADR/DCL clause preflight are green.

This `-013` supersedes `-012`. `-012` was filed without an explicit `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` evidence line, which the ADR/DCL clause preflight flagged as a blocking gap. `-013` adds that evidence; the implementation and the verification results are otherwise identical. `-012` is retained in the version chain as the append-only audit trail (it is not deleted or rewritten in place).

## Specification Links

- REQ-HARNESS-REGISTRY-001 — the harness registry requirement governing the phased migration of consumers from the legacy JSON to the registry; FR9 is the single-prime-builder role partition. C1 restores correct role rendering on the MCP surface, keeping role resolution correct across the migration.
- DELIB-2079 — owner-decided Antigravity Integration design; Q7 decided the phased reader migration with JSON retired last.
- DELIB-2080 — role-portability amendment (FR9); role resolution must remain correct across the migration, including the single-harness multi-element role-set that C1's primary-role rule normalizes.
- ADR-SINGLE-HARNESS-OPERATING-MODE-001 — the operating-mode architecture; the single-harness multi-element role-set is the wire form C1's deterministic primary-role rule must handle.
- SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001 — operating-mode switch requests go through a deterministic transaction component; the carried-forward writer migration preserves that transaction, validation, and audit contract.
- GOV-FILE-BRIDGE-AUTHORITY-001 — this report is a versioned bridge artifact filed under bridge/; its NEW-status entry is inserted at the top of the gtkb-harness-registry-reader-migration entry in bridge/INDEX.md, which remains the canonical workflow state. No prior version in the thread is deleted or rewritten; -012 is retained in the version chain.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 — every edited file is within the E:\GT-KB project root.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — this report cites every relevant governing specification.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — verification is derived from the linked specifications and executed against the implementation.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 — durable artifact preservation (advisory).
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 — traceability across artifacts and tests (advisory).
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — artifact lifecycle state transitions (advisory).

## Prior Deliberations

- DELIB-2079 — the owner-decided Antigravity Integration design; Q7 decided the phased migration. This report closes a NO-GO within that migration's WI-3342 thread.
- DELIB-2080 — role-portability amendment (FR9); the single-harness multi-element role-set that C1 normalizes is a consequence of role portability.
- bridge/gtkb-harness-registry-reader-migration-009.md (NO-GO) — findings F1 and F2 define the C1 and C2 correction scope this report implements.
- bridge/gtkb-harness-registry-reader-migration-010.md (REVISED proposal) — the GO'd proposal this report implements; it amended target_paths and specified C1 and C2.
- bridge/gtkb-harness-registry-reader-migration-011.md (GO) — the verdict authorizing this implementation; its Implementation Conditions are dispositioned below.
- bridge/gtkb-harness-registry-reader-migration-012.md — the predecessor post-implementation report this version supersedes; it lacked an explicit CLAUSE-INDEX-IS-CANONICAL evidence line.
- bridge/gtkb-harness-registry-reader-migration-005.md (REVISED) and -006.md (GO) — the approved migration plan carried forward; verified at -008.
- bridge/gtkb-mcp-stable-harness-surface-conversion-006.md (NO-GO) — the earlier mcp_surface/roles.py thread whose F2 established the no-hardcoded-fallback contract preserved by tests T12/T12b/T12c; C1 does not alter that contract.

## Owner Decisions / Input

The Antigravity Integration project, including the phased reader migration (DELIB-2079 Q7), was owner-decided via an 11-question AskUserQuestion clarification interview on 2026-05-16, recorded as DELIB-2079. The work is authorized under PAUTH-PROJECT-HARNESS-REGISTRY-REFACTOR-HARNESS-REGISTRY-REFACTOR-IMPLEMENTATION-AUTHORIZATION (status active; scope: REQ-HARNESS-REGISTRY-001 work items WI-3337 through WI-3344).

On 2026-05-18 the owner directed Prime Builder to file the `-010` REVISED selecting the second of the two dispositions NO-GO `-009` F2 offered — bring `groundtruth-kb/tests/test_mcp_surface_foundation.py` under explicit scope rather than revert the in-tree edit. This report implements that owner-directed disposition. It asserts no new requirement and requires no further owner decision before VERIFIED.

## Bridge Filing And INDEX Canonicality

This report satisfies `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`. It is a versioned bridge artifact filed under `bridge/` as `bridge/gtkb-harness-registry-reader-migration-013.md`. Its `NEW`-status line is inserted at the top of the `gtkb-harness-registry-reader-migration` document entry in `bridge/INDEX.md`, which remains the single canonical workflow state for this thread. No prior version is deleted or rewritten: `-012` (and every earlier version) is retained on disk and in the `bridge/INDEX.md` entry as the append-only audit trail. The `-012` to `-013` correction is itself an INDEX update that adds a new version line rather than mutating an existing one.

## Clause Scope Clarification (Not a Bulk Operation)

This report covers a two-correction follow-up to a code refactor: a normalization helper in mcp_surface/roles.py plus a corrected and extended co-located unit test. It is NOT a bulk standing-backlog operation: it does not resolve, retire, promote, batch-mutate, or produce an inventory of work items, and it requests no formal-artifact-approval packet for a bulk action. GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS is not applicable. The single work item cited (WI-3342) is this report's own implementing work item under the mandatory project-linkage metadata.

## Implementation — What Changed

### C1 — Canonical role normalization in current_role() (closes NO-GO -009 F1)

`groundtruth-kb/src/groundtruth_kb/mcp_surface/roles.py`:

- Added a module-level helper `_canonical_role(role_field)` placed immediately before `current_role()`. It normalizes a registry-projection `role` field to one canonical scalar role token:
  - a singleton list returns its sole element;
  - a multi-element list (single-harness operating mode) returns the deterministic primary role — `prime-builder` if present, else `loyal-opposition`, else the first element;
  - a legacy scalar `str` (e.g. `acting-prime-builder`) is returned verbatim, preserving the Acting-Prime Compatibility Contract;
  - an empty list or any other shape returns `"unknown"` (fail-soft; the helper never raises).
- Routed `current_role()`'s return value through the helper: the line `return str(record.get("role", "unknown"))` is now `return _canonical_role(record.get("role", "unknown"))`. No other behavior changed — `current_role()` still resolves the record by harness id and still returns `"unknown"` for an unmatched id.
- Updated the `current_role()` docstring to describe the list-to-scalar normalization and to state explicitly that the returned scalar is a primary role for display and labelling and is NOT full role-set authority — routing and topology code that must detect the single-harness shared slot uses the role-set membership and role-slot helpers. The `_canonical_role()` docstring carries the same distinction. This satisfies GO `-011` Implementation Condition 4.
- `server.py` is unchanged: it consumes `current_role()`'s return value, which is now the canonical scalar the `gt_status_summary` field always expected.

### C2 — Correct and extend the MCP foundation test (closes NO-GO -009 F2)

`groundtruth-kb/tests/test_mcp_surface_foundation.py`:

- Imported `CANONICAL_ROLES` alongside `current_role` from `groundtruth_kb.mcp_surface.roles`.
- T6 (`test_t6_current_role_reads_role_assignments_json`): replaced the defective assertion `current_role(...) == str(entry["role"])` with `resolved == entry["role"][0]` and `resolved in CANONICAL_ROLES`. Corrected the misleading comment that had described the stringified-list behavior as intended.
- Added T6b (`test_t6b_current_role_normalizes_multi_role_single_harness_set`): seeds a single-harness multi-element role-set `["prime-builder", "loyal-opposition"]` under an isolated `tmp_path` and asserts `current_role()` returns the deterministic primary role `prime-builder` and a member of `CANONICAL_ROLES`.
- T7 (`test_t7_current_role_accepts_acting_prime_builder_on_read`): unchanged. It seeds a legacy scalar `role` value and asserts verbatim return; C1's scalar pass-through preserves that behavior.

### Carried forward from -005 (unchanged)

IP-1 through IP-6 and IP-RECON are carried forward from the GO'd `-005` proposal unchanged. They are present in the working tree and were verified at `-008`. This report does not reopen or modify that work; the eight GO'd suites re-run here confirm no regression.

## Spec-To-Test Mapping

| Spec / governing surface | Verification | Result |
| --- | --- | --- |
| REQ-HARNESS-REGISTRY-001 / DELIB-2079 / DELIB-2080 (role resolution correct across the migration) | T6 asserts a singleton role-set resolves to its canonical scalar element and is in CANONICAL_ROLES; T7 asserts a legacy scalar resolves verbatim | PASS |
| ADR-SINGLE-HARNESS-OPERATING-MODE-001 (multi-element role-set wire form) | T6b exercises the ["prime-builder", "loyal-opposition"] single-harness role-set and asserts C1's primary-role rule | PASS |
| REQ-HARNESS-REGISTRY-001 FR9 + IP-RECON | test_harness_registry_reader_migration.py (the IP-RECON agreement test); carried forward from -005, re-run here | PASS |
| DELIB-2079 Q7 (phased migration, JSON retired last) | test_harness_registry_reader_migration.py IP-5 markers + the no-direct-read scan; carried forward | PASS |
| SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001 | the mode-switch suites under platform_tests/groundtruth_kb (transaction, validation, invariants, pending) | PASS |
| GOV-FILE-BRIDGE-AUTHORITY-001 | this report is filed as a versioned bridge file under bridge/ with a NEW entry inserted at the top of the thread's bridge/INDEX.md entry; the INDEX remains canonical workflow state | satisfied by filing |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | every edited file is within E:\GT-KB | satisfied |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | this report carries the mapping plus the executed commands and observed results below | satisfied |

## Verification — Commands and Observed Results

Run in harness B's working environment (Python 3.14.0, pytest 9.0.2) on 2026-05-18.

Command 1 — the eight GO'd suites plus the MCP foundation test:

```
python -m pytest platform_tests/scripts/test_harness_registry_reader_migration.py platform_tests/groundtruth_kb/test_mode_switch_transaction.py platform_tests/groundtruth_kb/test_mode_switch_validation.py platform_tests/groundtruth_kb/test_mode_switch_invariants.py platform_tests/groundtruth_kb/test_mode_switch_pending.py platform_tests/groundtruth_kb/cli/test_harness_cli.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/hooks/test_workstream_focus.py groundtruth-kb/tests/test_mcp_surface_foundation.py -q
```

Observed: `150 passed, 3 skipped, 2 xfailed in 14.46s` (155 collected). `groundtruth-kb/tests/test_mcp_surface_foundation.py` reports 15 passed — including the corrected T6, the new T6b, and the unchanged T7. The eight GO'd suites alone account for 135 passed, 3 skipped, 2 xfailed — identical to the `-008` report's eight-suite result. The 3 skipped and 2 xfailed are pre-existing markers in `test_workstream_focus.py`; they are not introduced or altered by C1/C2, which touch only `roles.py` and `test_mcp_surface_foundation.py`.

Command 2 — applicability preflight:

```
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-harness-registry-reader-migration
```

Observed: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`.

Command 3 — ADR/DCL clause preflight:

```
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-harness-registry-reader-migration
```

Observed: 5 clauses evaluated; `Evidence gaps in must_apply clauses: 0`; `Blocking gaps (gate-failing): 0`; exit 0.

## GO -011 Implementation Conditions — Disposition

GO `-011` listed four conditions, non-blocking for GO but blocking for VERIFIED:

1. `mcp_surface/roles.py` must normalize singleton list role values to their scalar token, preserve legacy scalar values such as `acting-prime-builder`, return `unknown` for empty or malformed shapes, and implement the documented primary-role rule for multi-element role-sets. — DONE: `_canonical_role()` implements all four shapes; T6, T6b, and T7 cover the singleton, multi-element, and legacy-scalar cases.
2. `test_mcp_surface_foundation.py` must import `CANONICAL_ROLES`, correct T6, add T6b, and leave T7 intact. — DONE: see C2 above.
3. The post-implementation report must run the eight GO'd suites plus `test_mcp_surface_foundation.py` with `pytest` and report observed results. — DONE: see Verification above.
4. The report must preserve the scalar-primary-role versus role-set-membership distinction; routing and topology code must continue to use membership and role-slot helpers where full role authority matters. — DONE: both the `_canonical_role()` and `current_role()` docstrings state this distinction explicitly; no routing or topology code was changed — C1 touches only the MCP scalar display surface.

## Acceptance Criteria

- [x] Loyal Opposition returned GO on the `-010` REVISED proposal (`-011`).
- [x] `target_paths` was amended to include `groundtruth-kb/tests/test_mcp_surface_foundation.py` (in `-010`).
- [x] C1: `current_role()` returns a canonical scalar role token for list-valued projection `role` fields.
- [x] C1: the value `current_role()` returns for a singleton or multi-element role-set is a member of `CANONICAL_ROLES` (asserted by T6 and T6b).
- [x] C2: T6 asserts the canonical scalar element and `in CANONICAL_ROLES`; T6b covers the multi-element single-harness role-set; T7 is unchanged.
- [x] The eight GO'd suites plus `test_mcp_surface_foundation.py` were run with `pytest`; observed results reported above.
- [x] All `-005` acceptance criteria remain satisfied (carried forward; verified at `-008`; the eight GO'd suites re-run here confirm no regression).
- [ ] Loyal Opposition returns VERIFIED — requested by this report.

## Recommended Commit Type

`refactor:` — consistent with the `-010` proposal. The WI-3342 thread is the harness role and identity reader migration: a structural change moving consumers from the legacy JSON files onto the DB-backed registry projection. C1 is a regression fix within that refactor (it restores the `current_role()` scalar contract the migration temporarily broke); C2 is the co-located test correction. The dominant change in the eventual commit is the migration refactor, so `refactor:` is the accurate Conventional Commits type. The commit is scoped to the WI-3342 `target_paths`; where clean isolation is not possible because the working tree carries unrelated in-flight work, the DECISION-0655 bundle precedent applies and the bundling is disclosed in the commit message.

## Risk and Rollback

C1 and C2 are low-risk. C1 is a pure normalization of an already-correct role value's string rendering — it changes no role assignment and no data source; the registry projection content is untouched. C2 is a test-only change. Rollback for C1/C2 is a two-file revert; the carried-forward migration is unaffected. The `-005` risks R1 through R4 were mitigated and shown green at `-008` and remain green in this report's eight-suite re-run.

## Pre-Filing Preflight Subsection

The applicability preflight and the ADR/DCL clause preflight were run as Commands 2 and 3 above. The predecessor `-012` passed the applicability preflight but failed the ADR/DCL clause preflight with one blocking gap: `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` lacked a matching evidence line. `-013` adds that evidence in the Specification Links bullet, the Bridge Filing And INDEX Canonicality section, and the Spec-To-Test Mapping row. This `-013` content was re-checked with the clause preflight via `--content-file` before its `NEW` INDEX entry was inserted; both preflights are re-run against the indexed `-013` operative after filing. Expected and observed: applicability preflight `preflight_passed: true` with empty `missing_*_specs`; clause preflight 0 evidence gaps and 0 blocking gaps.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
