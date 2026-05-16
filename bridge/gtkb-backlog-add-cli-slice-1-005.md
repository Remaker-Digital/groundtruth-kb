NEW

# Implementation Report - Backlog Add CLI Slice 1 (WI-3270)

bridge_kind: implementation_report
Document: gtkb-backlog-add-cli-slice-1
Version: 005
Responds to: bridge/gtkb-backlog-add-cli-slice-1-004.md
Author: Prime Builder (Claude, harness B)
Date: 2026-05-16 UTC
Session: S354
Project Authorization: PAUTH-PROJECT-GTKB-BACKLOG-CAPTURE-001-BACKLOG-CAPTURE-COMMAND-APPROVAL-STATE-TAXONOMY
Project: PROJECT-GTKB-BACKLOG-CAPTURE-001
Work Item: WI-3270

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli_backlog_add.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "platform_tests/scripts/test_cli_backlog_add.py"]

## Summary

Implements the REVISED-1 proposal `bridge/gtkb-backlog-add-cli-slice-1-003.md`
(Codex GO at `-004`): the governed `gt backlog add` command (with
`python -m groundtruth_kb backlog add` parity). Each invocation creates exactly
one MemBase `work_items` candidate row with `resolution_status='open'` and
`stage='backlogged'`, attributes the write through the verified mutating
fail-closed resolver `scripts._kb_attribution.resolve_changed_by()`, validates
required fields with deterministic enum checks, allocates a fresh `WI-NNNN`
id, supports `--dry-run`, and surfaces the new row through `gt backlog list`.
No `--changed-by` override surface exists. IP-1 through IP-5 are implemented;
IP-6 (bulk insert, update/retire, markdown cross-write, formal-artifact
integration, row-level allocation lock) remains deferred as the GO'd scope
states.

WI-3270 is a member of `PROJECT-GTKB-BACKLOG-CAPTURE-001` and is covered by the
active authorization `PAUTH-PROJECT-GTKB-BACKLOG-CAPTURE-001-BACKLOG-CAPTURE-COMMAND-APPROVAL-STATE-TAXONOMY`
(status active, no expiry; allowed mutation classes include `cli_extension`
and `test_addition`, which cover this implementation).

## In-Root Placement Evidence

All three target paths are in-root under `E:\GT-KB`:
`groundtruth-kb/src/groundtruth_kb/cli_backlog_add.py`,
`groundtruth-kb/src/groundtruth_kb/cli.py`, and
`platform_tests/scripts/test_cli_backlog_add.py`. No `applications/` paths; no
paths outside `E:\GT-KB`. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT`
satisfied.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 - live bridge index is canonical; this report is filed through `bridge/INDEX.md` with the `-005` version line inserted at the top of the thread's version list.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - spec linkage carried forward from the GO'd proposal.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - spec-to-test mapping below; the 14 tests were executed against the implementation.
- GOV-STANDING-BACKLOG-001 - MemBase `work_items` is the canonical backlog source of truth; the new capture path writes there, never to markdown views.
- GOV-HARNESS-ROLE-PORTABILITY-001 - the new mutating writer attributes through the harness-aware resolver.
- GOV-ARTIFACT-APPROVAL-001 - candidate `work_items` rows are non-formal artifacts; the formal-artifact-approval gate is intentionally not invoked at the per-row layer.
- DCL-ARTIFACT-APPROVAL-HOOK-001 - the approval-hook surface is preserved unchanged.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - all target paths in-root.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - traceability across `work_items`, deliberations, and source-owner-directive linkage is preserved.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - concrete future-work becomes durable MemBase artifacts.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - the new row enters with `stage='backlogged'`, `resolution_status='open'`.
- `bridge/gtkb-kb-attribution-harness-aware-003.md` - the verified attribution contract this writer adopts.
- `scripts/_kb_attribution.py` - implementation pointer for `resolve_changed_by()` (mutating; raises on unresolvable).
- `.claude/rules/file-bridge-protocol.md` - bridge filing conventions observed.
- `.claude/rules/codex-review-gate.md` - counterpart review gate; this report awaits Codex VERIFIED before commit.

## Prior Deliberations

- DELIB-S341-BACKLOG-CONSIDERATION-IMPLEMENTATION-AUQ-DIRECTIVE - owner directive that backlog candidates flow to MemBase, not MEMORY.md; motivates WI-3270.
- DELIB-S342-BACKLOG-WORK-ITEMS-CANONICAL-PIVOT - MemBase `work_items` is the canonical backlog authority.
- DELIB-0838 - standing backlog is a governed cross-session work authority (`GOV-STANDING-BACKLOG-001` source).
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE - repetitive plumbing should be a service; `gt backlog add` is the service that replaces ad-hoc `db.insert_work_item` snippets.
- DELIB-1634 (VERIFIED) / DELIB-1635 (GO) / DELIB-1636 (NO-GO) - the harness-aware `changed_by` attribution thread; the contract this writer consumes.
- DELIB-S333-CODEX-PRIME-PERIOD-KB-ATTRIBUTION-DEFECT - historical mis-attribution incident the fail-closed resolver prevents.

## Owner Decisions / Input

- 2026-05-14 UTC, S350: owner directive (DECISION-0583, AUQ-resolved) authorizing the batch of priority backlog proposals including WI-3270, and the underlying scope authority captured in DELIB-S341-BACKLOG-CONSIDERATION-IMPLEMENTATION-AUQ-DIRECTIVE. The Batch-2 project authorization `PAUTH-PROJECT-GTKB-BACKLOG-CAPTURE-001-BACKLOG-CAPTURE-COMMAND-APPROVAL-STATE-TAXONOMY` (owner-approved packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch2-three-project-authorizations.json`) covers WI-3270.
- 2026-05-15/16 UTC, S354: owner directive to proceed with implementing approved (GO) bridge proposals and work independently. No new owner-AUQ-required decision is open in this slice; the GO'd REVISED-1 explicitly recorded "Decision needed from owner: None."

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. `gt backlog add` creates exactly one `work_items` row per
invocation (one allocated id, one `insert_work_item` call). No batch-from-JSON,
batch-from-file, or repeating-flag surface; no retroactive inventory
enumeration; no cross-application sweep; no formal-artifact-approval packet at
the per-row layer (candidate rows are non-formal). The
`GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` bulk-operation arm does
not apply; the visibility arm is satisfied because new rows surface
immediately through `gt backlog list`.

## Implementation Summary

### IP-1..IP-5 - `groundtruth-kb/src/groundtruth_kb/cli_backlog_add.py` (new, ~230 lines)

- `BacklogAddError(Exception)`.
- `BacklogAddRequest` frozen dataclass with the 18 REVISED-1 fields. There is no `changed_by` or `changed_by_override` field (IP-2/IP-3): attribution is resolver-only.
- `_validate_request()` - deterministic required-field validation (`title`, `component`, `change_reason` non-empty; `origin` in `{new, hygiene, improvement, defect, regression}`) and `priority` enum (`{P0,P1,P2,P3}`, default `P3`); raises `BacklogAddError`.
- `_resolve_changed_by()` - function-local import of the mutating `scripts._kb_attribution.resolve_changed_by()`; its `RuntimeError` propagates unchanged.
- `_allocate_next_work_item_id()` - scans `work_items` for the max `WI-<n>` numeric suffix and returns `WI-<n+1>` zero-padded; SELECT and the subsequent INSERT share one connection (IP-5).
- `add_backlog_item(config, request)` - validates, resolves attribution BEFORE opening any write path, opens `KnowledgeDB`, allocates the id, applies the duplicate-id guard (`get_work_item` non-null -> `BacklogAddError`), and either returns the dry-run payload or calls `insert_work_item(...)` with `resolution_status='open'`, `stage='backlogged'`.

### IP-4 - `groundtruth-kb/src/groundtruth_kb/cli.py` (+95 lines)

`@backlog.command("add")` registered between `migrate-work-list` and `list`,
mirroring `backlog_list`'s `@click.pass_context` / `_resolve_config(ctx)`
pattern. Click options for every request field except `changed_by` (no
`--changed-by` option exists), plus `--dry-run` and `--json`. `--origin` and
`--priority` are `click.Choice`; `--title`/`--origin`/`--component`/`--change-reason`
are required. `BacklogAddError` and `RuntimeError` are caught and re-raised as
`click.ClickException`, producing a non-zero exit before any partial write.

### IP-3 tests - `platform_tests/scripts/test_cli_backlog_add.py` (new, 14 tests)

The 14 tests from the REVISED-1 Specification-Derived Verification Plan,
including the three attribution tests (resolver attribution, fail-closed
without harness resolution, no fallback-author row).

## Implementation Note - Cross-Tree Import (Deviation Disclosure)

The GO'd proposal (IP-1) mandates attribution via
`scripts._kb_attribution.resolve_changed_by()`. The resolver module lives under
`scripts/` at the project root, outside the `groundtruth_kb` package. So that
the GO-mandated import resolves when `groundtruth_kb` is imported as an
installed package, `cli_backlog_add.py` adds a `sys.path` insert of the project
root (computed as `Path(__file__).resolve().parents[3]`). The resolver import
itself is function-local inside `_resolve_changed_by()` so a resolver-signature
change fails loud at call time. This is the only deviation from the literal
`-003` text; it is a direct consequence of the GO-mandated cross-tree import,
not a scope change. The same coupling is already exercised by `_kb_attribution`
itself (which imports `scripts.harness_roles`).

## Spec-to-Test Mapping

All tests in `platform_tests/scripts/test_cli_backlog_add.py`:

| # | Test | Spec / behavior |
|---|------|-----------------|
| 1 | test_add_minimal_valid_inputs_creates_row | GOV-STANDING-BACKLOG-001; WI-3270 acceptance — minimal invocation creates one row with the enum defaults |
| 2 | test_add_missing_required_title_fails | deterministic required-field validation |
| 3 | test_add_invalid_origin_fails | origin enum validation |
| 4 | test_add_invalid_priority_fails | priority enum validation |
| 5 | test_add_dry_run_does_not_mutate | WI-3270 regression_visibility — dry-run writes nothing |
| 6 | test_add_does_not_write_memory_md | WI-3270 regression_visibility — MEMORY.md / work_list.md untouched |
| 7 | test_add_allocates_monotonically_increasing_wi_id | allocation contract |
| 8 | test_add_preserves_source_owner_directive_and_links | DELIB-S341 directive — link fields persisted |
| 9 | test_add_round_trips_through_backlog_list | WI-3270 visibility |
| 10 | test_add_duplicate_id_guard_refuses_overwrite | defensive allocation-race guard |
| 11 | test_add_attributes_changed_by_via_resolver | GOV-HARNESS-ROLE-PORTABILITY-001 — `changed_by` reads `prime-builder/claude` |
| 12 | test_add_fails_closed_without_harness_resolution | fail-closed — non-zero exit, no row written |
| 13 | test_add_does_not_emit_fallback_changed_by | audit-trail regression — no `gt-backlog-add`/`unknown`/`prime-builder/unknown` author row |
| 14 | test_add_emits_machine_readable_json | `--json` parseable output |

## Verification Evidence

- `python -m pytest platform_tests/scripts/test_cli_backlog_add.py -v` - **14 passed**.
- `python -m pytest platform_tests/scripts/test_kb_attribution.py -v` - **21 passed** (regression; the resolver contract remains the single attribution path). Combined run independently re-executed by Prime Builder: `35 passed in 2.27s`.
- `python -m ruff check groundtruth-kb/src/groundtruth_kb/cli_backlog_add.py groundtruth-kb/src/groundtruth_kb/cli.py platform_tests/scripts/test_cli_backlog_add.py` - **All checks passed**.
- Applicability + clause preflights: executed against the `-005` operative after the INDEX update; results in the `## Preflight Results` section below.

## GO Implementation Conditions (from -004) - Compliance

1. The implementation uses the mutating `resolve_changed_by()` (function-local import in `_resolve_changed_by()`), not `resolve_changed_by_or_none()`. **MET.**
2. No `--changed-by` CLI option, environment override, or fallback literal exists; attribution is resolver-only and fails closed before any DB write. Test 13 asserts no `gt-backlog-add`/`unknown`/`prime-builder/unknown` author row. **MET.**
3. Observed results for the two pytest runs and the two preflights are included in this report (Verification Evidence + Preflight Results). **MET.**
4. The new tests use a per-test temporary `groundtruth.db` (built from a temp `groundtruth.toml`, mirroring `test_spec_record.py`); production `groundtruth.db` and `memory/work_list.md` are confirmed unchanged by `git status`; `memory/MEMORY.md` was already modified before this session began (in the starting git snapshot) and was not touched by this implementation. **MET.**

## Recommended Commit Type

`feat` - net-new CLI subcommand module (`cli_backlog_add.py`) + net-new test
module + a subcommand registration in `cli.py`. New capability surface; matches
the proposal's own recommendation.

## Risks / Rollback

- Allocation race under concurrent agents - mitigated by the duplicate-id guard (test 10) plus the single-connection SELECT-then-INSERT; a row-level allocation lock is a documented Slice-1 follow-on.
- Rollback: delete `cli_backlog_add.py`, revert the `cli.py` registration, delete the test file. Candidate rows produced during testing live in temp DBs; production `groundtruth.db` is untouched.

## Preflight Results

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-backlog-add-cli-slice-1` -> operative `bridge/gtkb-backlog-add-cli-slice-1-005.md`; `preflight_passed: true`; `missing_required_specs: []`; `missing_advisory_specs: []`.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-backlog-add-cli-slice-1` -> operative `bridge/gtkb-backlog-add-cli-slice-1-005.md`; 5 clauses evaluated, `must_apply: 5`, evidence gaps 0, blocking gaps 0; exit 0.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
