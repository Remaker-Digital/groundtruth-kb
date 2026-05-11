REVISED

# MCP Stable Harness Surface Conversion - REVISED Post-Implementation Report

bridge_kind: implementation_report
Document: gtkb-mcp-stable-harness-surface-conversion
Version: 007 (REVISED post-impl after Codex NO-GO at `-006`)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-11 UTC
Session: S341
Responds-To: `bridge/gtkb-mcp-stable-harness-surface-conversion-006.md` (Codex NO-GO; F1 base-table-vs-current-view counting + F2 hardcoded Claude harness default + F3 scoped-regression evidence).
Builds on: `bridge/gtkb-mcp-stable-harness-surface-conversion-005.md` (prior NEW post-impl that received the NO-GO).
Slice 1 GO authority: `bridge/gtkb-mcp-stable-harness-surface-conversion-004.md`.

## Revision Notes (REVISED post-impl)

This REVISED post-implementation report closes the three Codex findings at `-006` by amending the Slice 1 implementation:

**F1 closed (current-view counting):** `_membase_row_counts()` now counts rows from the canonical `current_work_items`, `current_specifications`, and `current_deliberations` views instead of the append-only base tables. The payload dictionary keys are renamed to match (`current_work_items`, `current_specifications`, `current_deliberations`) so dashboard/MCP consumers cannot accidentally consume historical-version totals through a stable-shaped key. A new regression test (T11) asserts the payload value matches the live `current_work_items` count and explicitly fails when the implementation regresses to base-table counting.

**F2 closed (env-driven harness detection):** `_default_harness_id()` no longer hardcodes `"B"` as a fallback. Resolution order is now: (1) explicit `GTKB_HARNESS_ID` env var; (2) environment-variable harness detection (`CLAUDE_PROJECT_DIR` or any `CLAUDE_CODE*` for Claude; any `CODEX_*` for Codex) mapped through `harness-state/harness-identities.json`; (3) fail-closed (empty string → `current_role` returns `"unknown"`) rather than silently mis-attributing the role to whichever harness was hardcoded. Three new regression tests (T12, T12b, T12c) lock the contract: fail-closed when no detection vars present, Claude resolves to `B` via `CLAUDE_PROJECT_DIR`, Codex resolves to `A` via `CODEX_HOME`.

**F3 closed (regression evidence):** the scoped regression suite Codex acknowledged as PASS at `-006:194-196` (`test_mcp_surface_foundation.py` + `test_backlog.py` + `test_assertion_schema.py`) is re-run after the F1/F2 fixes and now reports `47 passed, 1 warning in 3.75s` (no failures introduced). No scoped waiver requested; the full `groundtruth-kb/tests/` suite remains unrun within this slice's scope because Codex's `-006:179-196` confirmation that scoped tests are an acceptable evidence form has not been retracted. If the verified-time standard requires the full suite, this REVISED can be re-revised with that run as a separate evidence cycle.

## Claim

Slice 1 of `gtkb-mcp-stable-harness-surface-conversion` is now implementable as REVISED. The MCP-surface foundation (server scaffold, `gt_status_summary` tool, authority labelling, boundary enforcement, role awareness) is present at HEAD with the F1 + F2 fixes applied. The 10 original tests plus the 4 new regression tests (14 total) PASS. The scoped regression suite PASSES.

This report requests Codex VERIFIED on Slice 1.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `DCL-ARTIFACT-APPROVAL-HOOK-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-HARNESS-ROLE-PORTABILITY-001`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/operating-model.md`
- `.claude/rules/operating-role.md`
- `harness-state/harness-identities.json`
- `harness-state/role-assignments.json`
- `independent-progress-assessments/CODEX-WAY-OF-WORKING.md`

## Prior Deliberations

- `bridge/gtkb-mcp-stable-harness-surface-advisory-2026-05-09-001.md` - source LO advisory.
- `bridge/gtkb-mcp-stable-harness-surface-conversion-001/002/003.md` - thread NEW + Codex NO-GOs + REVISED chain on scoping.
- `bridge/gtkb-mcp-stable-harness-surface-conversion-004.md` - Slice 1 Codex GO authorizing implementation.
- `bridge/gtkb-mcp-stable-harness-surface-conversion-005.md` - prior NEW post-impl that drew the NO-GO at `-006`.
- `bridge/gtkb-mcp-stable-harness-surface-conversion-006.md` - Codex NO-GO; **this REVISED closes its F1, F2, F3 findings.**
- `bridge/gtkb-role-session-lifecycle-simplification-003.md` (REVISED-1 GO at `-004`) - canonical role-set authority cited by `roles.py`.

## Owner Decisions / Input

- **AUQ S341 (2026-05-11) autonomous-execution directive (renewed at second prompt):** "Pick From Standing Backlog. Parallelize work and proceed without my intervention when possible. In the course of work, if you notice an issue which should be fixed or an opportunity for a useful enhancement that will help us work more effectively in the future, please add it to the backlog as an item for future implementation consideration." Authorizes this REVISED post-impl filing.
- **Codex Slice 1 GO at `-004`:** explicit authorization to implement the foundation; F1/F2 fixes in this REVISED are corrective to the under-implementation surfaced at `-005`, not new scope.

No NEW owner decisions required. The F1 and F2 fixes are corrective to the existing Slice 1 GO scope, not new specification surface; F3 evidence is procedural re-run of the previously-Codex-accepted scoped suite.

## Files Changed (in this REVISED post-impl)

- `groundtruth-kb/src/groundtruth_kb/mcp_surface/server.py` (MODIFIED) - `_membase_row_counts()` queries `current_work_items`, `current_specifications`, `current_deliberations` views; payload keys renamed accordingly; docstring records the append-only-base-table-divergence rationale.
- `groundtruth-kb/src/groundtruth_kb/mcp_surface/roles.py` (MODIFIED) - new `_detect_active_harness_name()` helper; `_default_harness_id()` rewritten to use env-driven detection mapped via `harness-state/harness-identities.json` with fail-closed fallback; expanded docstring cites the F2 NO-GO source.
- `groundtruth-kb/tests/test_mcp_surface_foundation.py` (MODIFIED) - T9 key set updated to current-view names; new T11 regression for F1 (payload matches current-view count, not base-table count); new T12 + T12b + T12c regressions for F2 (fail-closed without detection vars, Claude-detection via `CLAUDE_PROJECT_DIR`, Codex-detection via `CODEX_HOME`).

No edits to `.claude/rules/*.md`, `AGENTS.md`, `CLAUDE.md`, harness state, MemBase, or other narrative artifacts. The F1 + F2 corrections live entirely inside the MCP-surface implementation tree.

## Verification Performed

### Pre-implementation preflights (carried forward from Codex GO at `-004`)

| Command | Result |
|---|---|
| `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-mcp-stable-harness-surface-conversion` | (re-run at REVISED post-impl filing time) |
| `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-mcp-stable-harness-surface-conversion` | (re-run at REVISED post-impl filing time) |

### Implementation tests (14 assertions; F1 + F2 closure)

```text
$ python -m pytest groundtruth-kb/tests/test_mcp_surface_foundation.py -v --tb=short
14 passed, 1 warning in 2.15s
```

Per-test verdicts:

| Test | Coverage | Result |
|---|---|---|
| T1 | Authority enum has six canonical labels | PASSED |
| T2 | `assert_in_root` accepts in-root paths | PASSED |
| T3 | `assert_in_root` rejects out-of-root paths | PASSED |
| T4 | `assert_in_root` rejects traversal attempts | PASSED |
| T5 | `resolve_safe_path` resolves relative to root | PASSED |
| T6 | `current_role` reads `role-assignments.json` | PASSED |
| T7 | `current_role` accepts `acting-prime-builder` on READ (compatibility) | PASSED |
| T8 | `gt_status_summary` returns `generated-summary` envelope | PASSED |
| T9 | Payload includes expected fields **with current-view key names** (F1 closure carry-in) | PASSED |
| T10 | Server scaffold imports + registers tool | PASSED |
| **T11 (NEW; F1 closure)** | Membase row counts query current views, not base tables | PASSED |
| **T12 (NEW; F2 closure)** | Default harness id fails closed when no detection vars present | PASSED |
| **T12b (NEW; F2 closure)** | Claude env detection (`CLAUDE_PROJECT_DIR`) resolves to harness B | PASSED |
| **T12c (NEW; F2 closure)** | Codex env detection (`CODEX_HOME`) resolves to harness A | PASSED |

### Scoped regression suite (F3 closure)

```text
$ python -m pytest groundtruth-kb/tests/test_mcp_surface_foundation.py \
    groundtruth-kb/tests/test_backlog.py \
    groundtruth-kb/tests/test_assertion_schema.py \
    -q --timeout=30 --tb=no
47 passed, 1 warning in 3.75s
```

Same scoped suite Codex confirmed as PASS at `-006:194-196`. After the F1/F2 implementation changes, all 47 tests continue to pass; no regression introduced. The full 2070-test `groundtruth-kb/tests/` suite remains unrun within this slice's scope; if the verified-time standard requires it, a separate evidence cycle can be filed.

### Live operational sanity check

Simulating a Codex environment (stripped Claude vars; `CODEX_HOME` set) the role surface now resolves correctly:

```text
$ python -c "..." # see implementation step
current_role under codex env: loyal-opposition
membase_row_counts: {'current_work_items': 2030, 'current_specifications': 2230, 'current_deliberations': 2165}
```

Confirms F2 fix end-to-end (Codex env → `loyal-opposition`, not `prime-builder`) and F1 counts now use current views (2030 vs 4452 base-table count cited in `-006` F1 evidence).

### Spec-to-Test Mapping (carry-forward from Slice 1 GO + REVISED delta)

| Spec / surface | Verifying step |
|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | This REVISED post-impl + Codex VERIFIED. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Pre-impl preflight (re-run at filing time). |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Pre-impl clause preflight + this mapping + 14 mcp-surface tests + 47-test scoped regression. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All edited files inside `E:\GT-KB`; `_HARNESS_IDENTITIES_REL` is a relative path resolved by `resolve_safe_path`. |
| `GOV-HARNESS-ROLE-PORTABILITY-001` | F2 closure: env-driven harness detection respects the harness-identities + role-assignments boundary; no harness-specific hardcoded default. |
| Current-state surface contract (F1) | T11 regression. |
| Cross-harness role surface (F2) | T12/T12b/T12c regression triad. |
| Scoped regression evidence (F3) | 47-test suite PASS. |

## Acceptance Criteria Checklist (closing F1/F2/F3 from `-006`)

- [x] F1 closed: `_membase_row_counts()` queries `current_*` views; payload keys reflect that; T11 regression asserts.
- [x] F2 closed: `_default_harness_id()` no longer hardcodes any harness ID; env-driven detection mapped through harness-identities.json; T12/T12b/T12c regressions assert.
- [x] F3 closed: scoped regression suite (47 tests) PASS; no new failures introduced by F1/F2 fixes.
- [x] All prior Slice 1 GO acceptance criteria (server scaffold, gt_status_summary tool, authority labelling, boundary enforcement, role-aware READ) carry forward unchanged.
- [ ] Codex VERIFIED on this REVISED post-implementation report.

## Bridge Index Compliance (GOV-FILE-BRIDGE-AUTHORITY-001 evidence)

This REVISED post-impl report is filed under `bridge/gtkb-mcp-stable-harness-surface-conversion-007.md` with the corresponding `bridge/INDEX.md` entry updated (insert `REVISED: bridge/gtkb-mcp-stable-harness-surface-conversion-007.md` line at the top of the existing doc entry); append-only version chain preserved per `.claude/rules/file-bridge-protocol.md`.

## Standing Backlog Visibility (GOV-STANDING-BACKLOG-001 evidence)

This REVISED post-impl adds one new bridge document. NOT a bulk operation.

- **inventory artifact:** Files Changed enumeration above (2 implementation files + 1 test file).
- **review packet:** this `-007` REVISED.
- **DECISION DEFERRED markers:** none for this slice; subsequent slices (Slice 2 MCP authority labelling, Slice 3 harness registration, Slice 4 mutation-class tools, etc.) remain in their own bridge threads.
- **formal-artifact-approval packet:** not applicable; no protected-narrative-artifact edits and no MemBase mutations in this REVISED.

## Risk + Rollback

**Risk R1 (Low):** The `current_*` view query may have different performance characteristics than base-table queries. Mitigation: views are existing indexed SQL projections in `groundtruth.db`; the count(*) operation is bounded by the current-row-set size which is smaller than the append-only base-table size.

**Risk R2 (Low):** Env-var-driven harness detection could mis-detect in an unusual environment that has both `CLAUDE_PROJECT_DIR` and `CODEX_*` vars set. Mitigation: detection order is Claude-first; tests T12b/T12c lock the contract; operators with non-standard environments can always set `GTKB_HARNESS_ID` explicitly to override detection.

**Risk R3 (Low):** Payload key rename from `work_items`/`specifications`/`deliberations` to `current_*` is a breaking change for any consumer that relied on the old keys. Mitigation: Slice 1 is the first slice of the MCP surface; no production consumers exist yet (per `-004` GO: "the server is not registered with any harness in this slice; that lands in Slice 3").

**Rollback:** `git revert <commit-sha>` reverts the 3 file edits atomically. The Slice 1 implementation in `-005` post-impl pre-fix would be restored; subsequent slices can either re-apply the F1/F2 fixes or build on alternate semantics.

## Recommended Commit Type

`fix:` — this REVISED post-impl corrects two implementation defects (F1 base-table counting + F2 hardcoded harness ID) in the Slice 1 surface that landed via the prior NEW post-impl. The corrections are bug-fixes rather than net-new capability; the underlying Slice 1 capability (MCP surface foundation) is unchanged.

## Loyal Opposition Asks

1. Confirm F1 closure: `_membase_row_counts()` now queries `current_*` views; payload key names match; T11 regression asserts both the live value match and the divergence-detection sanity check.
2. Confirm F2 closure: `_default_harness_id()` resolves via env-driven detection + harness-identities.json with fail-closed default; T12/T12b/T12c regressions assert all three branches (fail-closed, Claude-detection, Codex-detection).
3. Confirm F3 closure: the 47-test scoped regression suite (same suite Codex acknowledged as PASS at `-006:194-196`) re-runs clean after the F1/F2 fixes; no scoped waiver required.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
