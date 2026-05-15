---
Status: NEW
Author: prime-builder (claude harness B)
Date: 2026-05-14
Session: S350
Source: WI-3270 (Add governed backlog item creation command)
Project: GTKB-BACKLOG-CAPTURE-001
Recommended commit type: feat
bridge_kind: implementation_proposal
target_paths: ["groundtruth-kb/src/groundtruth_kb/cli_backlog_add.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "platform_tests/scripts/test_cli_backlog_add.py"]
---

Document: gtkb-backlog-add-cli-slice-1

## Summary

Add a governed single-item backlog-creation command `gt backlog add` (with `python -m groundtruth_kb backlog add` parity) that lets agents capture noticed issues or enhancement opportunities as MemBase `work_items` candidate rows during normal work, satisfying WI-3270 and the standing-backlog source-of-truth contract. The command writes through `KnowledgeDB.insert_work_item`, validates required fields (title, origin, component) with deterministic enum checks, allocates a fresh `WI-NNNN` id, supports `--dry-run`, preserves `source_owner_directive` + related-spec/deliberation/bridge links, defaults the new row to a backlogged candidate state (`stage='backlogged'`, `resolution_status='open'`, `priority='P3'` unless overridden), and emits the created id on stdout. It never mutates `memory/MEMORY.md`, `memory/work_list.md`, or harness-local auto-memory.

Capture is NOT implementation approval. The new row records a candidate for future implementation consideration. Implementation of the captured item still requires a normal bridge proposal, Loyal Opposition `GO`, and (where applicable) project authorization or per-artifact owner approval through the standard governance path.

Slice 1 is deliberately minimal: one single-item insert per invocation, no bulk-insert surface, no edit/update surface, no retire surface, no parallel write to legacy markdown views. Future slices may add `gt backlog update`, `gt backlog retire`, or batch-from-JSON capabilities once Slice 1 stabilizes.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 — live bridge index authority; this proposal is filed through the file bridge.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — proposal cites all relevant governing specifications.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — spec-derived test mapping enumerated below.
- GOV-STANDING-BACKLOG-001 — standing backlog is the durable cross-session work authority; MemBase `work_items` is the canonical source of truth; new capture path writes to that source, not to markdown views.
- GOV-ARTIFACT-APPROVAL-001 — formal artifact approval gate. Backlog candidates are MemBase records but are NOT formal artifacts (GOV/ADR/DCL/PB/SPEC); the standard approval-packet gate is intentionally NOT invoked for candidate work-item rows. See § "Owner Decisions / Input" for the AUQ evidence chain authorizing the capture path itself.
- DCL-ARTIFACT-APPROVAL-HOOK-001 — the approval-hook surface is preserved unchanged; this proposal does NOT bypass it for any artifact class the hook governs.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 — all touched paths remain inside `E:\GT-KB` (`groundtruth-kb/src/groundtruth_kb/` and `platform_tests/scripts/`).
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 — preserves traceability across `work_items`, deliberations, and source-owner-directive linkage.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 — concrete future-work items become durable MemBase artifacts rather than chat/markdown sediment.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — the new row enters with explicit `stage='backlogged'` and `resolution_status='open'`, surfaced through existing `gt backlog list` retrieval.
- `.claude/rules/file-bridge-protocol.md` — bridge filing conventions.
- `.claude/rules/codex-review-gate.md` — counterpart review gate; this proposal awaits Codex GO before implementation.
- `.claude/rules/project-root-boundary.md` — all paths inside `E:\GT-KB`.

## Prior Deliberations

- DELIB-S341-BACKLOG-CONSIDERATION-IMPLEMENTATION-AUQ-DIRECTIVE — owner directive that backlog candidates flow to MemBase, not MEMORY.md; directly motivates WI-3270.
- DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE — S327 owner directive formalizing standing backlog as DB-backed source-of-truth; supports `work_items`-only write target.
- DELIB-0838 — owner decision that the standing backlog is a governed cross-session work authority (`GOV-STANDING-BACKLOG-001` source).
- DELIB-0839 — standing-backlog harvest snapshot and reconciliation obligations; the new command must not bypass reconciliation invariants.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE — repetitive plumbing should be a service. A governed `backlog add` CLI is the service that replaces ad-hoc Python snippets and prevents recurrent MEMORY.md mistakes.
- DELIB-1404 — candidate-specification statements backlog advisory; informs the candidate-state default.
- DELIB-1585 — Loyal Opposition review of backlog work-list retirement directive; confirms the legacy markdown surface should not be cross-written.

## Owner Decisions / Input

Owner direction 2026-05-14 S350: "Please parallelize work and start as many priority backlog projects as possible" + "Please continue filing more backlog work" authorizes batch NEW filing of priority backlog proposals. Per-proposal Codex GO required before implementation. Channel: AskUserQuestion (DECISION-0583 — AUQ-resolved batch authorization).

Underlying scope authority for WI-3270 itself: owner directive 2026-05-11 captured in DELIB-S341-BACKLOG-CONSIDERATION-IMPLEMENTATION-AUQ-DIRECTIVE — backlog capture must use MemBase, not MEMORY.md, and must not require implementation approval at capture time. WI-3270 was inserted with `source_owner_directive` reflecting this directive.

No owner-AUQ-required decision is open inside this slice. Implementation stays within `groundtruth-kb/src/groundtruth_kb/` CLI source, a new test file, and the existing MemBase write path; no protected narrative artifact is touched.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal adds a single-item CLI insert path. It is NOT a bulk operation:

- One invocation creates exactly one `work_items` row (one new id, one `insert_work_item` call).
- No batch-from-JSON, batch-from-file, or repeating-flag surface is introduced.
- No retroactive enumeration of existing inventory occurs.
- No cross-application sweep or hygiene back-fill occurs.

The bulk-operation `GOV-STANDING-BACKLOG-001` enforcement clause (which guards mass `work_items` mutation) does not apply to this slice. The slice is governed by the standard single-row write contract already exercised by `gt backlog migrate-work-list` (one row per parsed entry, with `formal-artifact-approval` exclusion documented at the per-item layer because each row is a non-formal candidate, not a GOV/ADR/DCL/PB/SPEC formal artifact).

Tokens for clause-preflight matching: `inventory`, `formal-artifact-approval`.

## Requirement Sufficiency

Existing requirements sufficient. WI-3270 acceptance_summary and source-owner-directive, together with GOV-STANDING-BACKLOG-001 and DELIB-S341-BACKLOG-CONSIDERATION-IMPLEMENTATION-AUQ-DIRECTIVE, fully specify the capture path's required behavior. No new or revised requirement is needed before implementation.

## Implementation Plan

### New file: `groundtruth-kb/src/groundtruth_kb/cli_backlog_add.py`

A small module mirroring `cli_spec_record.py`'s shape but without an approval-packet write (work-items are not formal artifacts):

1. `BacklogAddRequest` dataclass with fields: `title`, `origin`, `component`, `priority`, `project_name`, `subproject_name`, `description`, `source_owner_directive`, `source_spec_id`, `source_deliberation_query`, `related_spec_ids_at_creation`, `related_deliberation_ids`, `related_bridge_threads`, `depends_on_work_items`, `acceptance_summary`, `regression_visibility`, `change_reason`, `changed_by_override`, `dry_run`.
2. `add_backlog_item(config, request) -> dict`:
   - Validate required fields: `title` non-empty, `origin` in `{'new', 'hygiene', 'improvement', 'defect', 'regression'}`, `component` non-empty string, `change_reason` non-empty.
   - Validate optional enum: `priority` in `{'P0','P1','P2','P3', None}`; default `P3` when omitted (low-ceremony candidate default).
   - Allocate next `WI-NNNN` id by querying `current_work_items` for `MAX(CAST(SUBSTR(id, 4) AS INTEGER))` where `id GLOB 'WI-[0-9]*'` and adding 1. The same allocation path is wrapped in a DB transaction with a SELECT-then-INSERT inside the same connection to keep the slice simple; concurrent-allocation safety is documented as a known follow-on (see § Risk and Rollback).
   - Resolve `changed_by` via `GTKB_HARNESS_ID` / `GTKB_ACTIVE_HARNESS_ID` / `CODEX_HARNESS_ID` (matches `cli_spec_record._changed_by`); fallback `gt-backlog-add`. The `--changed-by` override is accepted only when `GTKB_ALLOW_CHANGED_BY_OVERRIDE=1` is set; otherwise it is ignored to preserve attribution integrity.
   - If `--dry-run`: return `{created: false, dry_run: true, id: <allocated-id>, kwargs: <insert_kwargs>}` without writing.
   - Otherwise: call `db.insert_work_item(...)` with `stage='backlogged'`, `resolution_status='open'`, and the validated kwargs; return `{created: true, dry_run: false, id: <new-id>, row: <readback row>}`.
   - Refuse to write if `db.get_work_item(<allocated-id>)` is non-null (defensive guard against allocation race; bubble up an error message).

### Edit: `groundtruth-kb/src/groundtruth_kb/cli.py`

Register the new command under the existing `gt backlog` Click group:

```python
@backlog.command("add")
@click.option("--title", required=True)
@click.option("--origin", required=True, type=click.Choice(["new", "hygiene", "improvement", "defect", "regression"]))
@click.option("--component", required=True)
@click.option("--priority", type=click.Choice(["P0", "P1", "P2", "P3"]), default="P3", show_default=True)
@click.option("--project-name", default=None)
@click.option("--subproject-name", default=None)
@click.option("--description", default=None)
@click.option("--source-owner-directive", default=None)
@click.option("--source-spec-id", default=None)
@click.option("--related-spec-ids", default=None, help="JSON array of spec ids")
@click.option("--related-deliberation-ids", default=None, help="JSON array of DELIB ids")
@click.option("--related-bridge-threads", default=None, help="JSON array of bridge file paths")
@click.option("--depends-on-work-items", default=None, help="JSON array of WI ids")
@click.option("--acceptance-summary", default=None)
@click.option("--regression-visibility", default=None)
@click.option("--change-reason", required=True)
@click.option("--changed-by", default=None, help="Honored only when GTKB_ALLOW_CHANGED_BY_OVERRIDE=1")
@click.option("--dry-run", is_flag=True)
@click.option("--json", "json_output", is_flag=True)
@click.pass_context
def backlog_add(ctx, ...):
    from groundtruth_kb.cli_backlog_add import add_backlog_item, BacklogAddRequest
    config = _resolve_config(ctx)
    request = BacklogAddRequest(...)
    result = add_backlog_item(config, request)
    if json_output:
        click.echo(json.dumps(result, indent=2, sort_keys=True, default=str))
    else:
        action = "Would create" if result["dry_run"] else "Created"
        click.echo(f"{action} {result['id']}")
```

`python -m groundtruth_kb backlog add ...` parity is automatic because `python -m groundtruth_kb` resolves the same Click group.

### Tests: `platform_tests/scripts/test_cli_backlog_add.py`

See § Test Mapping. Tests use a temp `groundtruth.db` initialized via the existing fixture pattern (mirroring `test_cli_spec_record.py`).

### Out of scope (deferred to future slices)

- Bulk insert from JSON / batch file.
- `gt backlog update` / `gt backlog retire`.
- Cross-write to `memory/work_list.md` (legacy view).
- Formal-artifact-approval integration (candidates are not formal artifacts).
- Concurrent-allocation lock; Slice 1 documents the SELECT-then-INSERT pattern's race as a known follow-on tracked in the post-impl report.

## Test Mapping

Spec ↔ test derivation (all under `platform_tests/scripts/test_cli_backlog_add.py`):

1. `test_add_minimal_valid_inputs_creates_row` — GOV-STANDING-BACKLOG-001, WI-3270 acceptance_summary. Verifies a minimal `gt backlog add --title --origin --component --change-reason` invocation creates exactly one new `current_work_items` row with the expected enum defaults (`stage='backlogged'`, `resolution_status='open'`, `priority='P3'`).
2. `test_add_missing_required_title_fails` — DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 (deterministic field validation). Click rejects the invocation with a non-zero exit.
3. `test_add_invalid_origin_fails` — same as above; enum validation rejects values outside the allowed set.
4. `test_add_invalid_priority_fails` — enum validation for `--priority`.
5. `test_add_dry_run_does_not_mutate` — WI-3270 regression_visibility ("dry-run does not mutate"). Row count before == after; allocated id is reported but not persisted.
6. `test_add_does_not_write_memory_md` — WI-3270 regression_visibility ("candidate creation does not write MEMORY.md"). Assert `memory/MEMORY.md` and `memory/work_list.md` mtimes unchanged across the invocation.
7. `test_add_allocates_monotonically_increasing_wi_id` — Allocation contract. Insert two rows in sequence; ids must be `WI-<n>` and `WI-<n+1>` with `n` greater than the prior `MAX`.
8. `test_add_preserves_source_owner_directive_and_links` — DELIB-S341-BACKLOG-CONSIDERATION-IMPLEMENTATION-AUQ-DIRECTIVE. `source_owner_directive`, `related_spec_ids_at_creation`, `related_deliberation_ids`, `related_bridge_threads` are persisted exactly as supplied (JSON-encoded for list fields).
9. `test_add_round_trips_through_backlog_list` — WI-3270 regression_visibility ("backlog list surfaces the created row"). `gt backlog list --json` includes the new id after creation.
10. `test_add_duplicate_id_guard_refuses_overwrite` — Defensive guard. Pre-insert a row at the allocated id (via direct `db.insert_work_item`) and confirm `gt backlog add` errors out rather than versioning over it.
11. `test_add_changed_by_override_requires_env_flag` — Attribution integrity. `--changed-by alt` is ignored unless `GTKB_ALLOW_CHANGED_BY_OVERRIDE=1`.
12. `test_add_emits_machine_readable_json` — `--json` returns parseable JSON with `id`, `created`, `dry_run` keys.

Execution command: `python -m pytest platform_tests/scripts/test_cli_backlog_add.py -v`.

## Risk and Rollback

**Risk 1: Allocation race under concurrent agents.** Two simultaneous `gt backlog add` invocations could allocate the same `WI-NNNN` id between SELECT and INSERT. Slice 1 mitigates via the duplicate-id guard (test 10) which fails the second write rather than silently versioning, plus the SQLite default per-connection transaction wrapping the SELECT-INSERT pair. A future slice may add a row-level allocation lock or sequence table. The remaining race in Slice 1 is documented in the post-impl report.

**Risk 2: Origin-enum drift.** New origin values added later to existing rows would need the Click choice updated. Mitigation: enum reads from a single module-level constant; the test suite asserts the full allowed set.

**Risk 3: Candidate rows polluting in-flight backlog views.** Candidates appear in `gt backlog list` immediately. This is intentional per WI-3270 (`backlog list surfaces the created row`). Owner-priority filtering is a downstream concern, not a Slice 1 problem.

**Rollback:** Revert the two source edits (`cli_backlog_add.py` removal + Click registration removal in `cli.py`) and the test file. No data migration is required because candidate `work_items` rows produced during testing live in a temp DB; production `groundtruth.db` is not touched until owner uses the command post-VERIFIED.

## Acceptance Criteria

A1. `python -m groundtruth_kb backlog add --title "<t>" --origin hygiene --component backlog --change-reason "<r>"` creates one new `WI-NNNN` row with `stage='backlogged'`, `resolution_status='open'`, `priority='P3'`, and emits the id on stdout.

A2. `--dry-run` reports the allocated id but does not write to the database.

A3. Missing or invalid required fields produce non-zero exit with a deterministic error message; no partial row is created.

A4. The command never writes to `memory/MEMORY.md`, `memory/work_list.md`, or any harness-local auto-memory file.

A5. `source_owner_directive`, `source_spec_id`, `related_spec_ids_at_creation`, `related_deliberation_ids`, `related_bridge_threads`, `depends_on_work_items` are preserved exactly as supplied.

A6. The new row appears in `gt backlog list --json` immediately after creation.

A7. `python -m pytest platform_tests/scripts/test_cli_backlog_add.py` passes with 12 tests (per § Test Mapping).

A8. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-backlog-add-cli-slice-1` reports `preflight_passed: true` against the live bridge file post-INDEX-update.

A9. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-backlog-add-cli-slice-1` exits 0 (no blocking clause gaps).

## Bridge Index Discipline (GOV-FILE-BRIDGE-AUTHORITY-001)

This proposal is filed at `bridge/gtkb-backlog-add-cli-slice-1-001.md` with status NEW. Prime will insert a new entry at the top of `bridge/INDEX.md` of the form:

```
Document: gtkb-backlog-add-cli-slice-1
NEW: bridge/gtkb-backlog-add-cli-slice-1-001.md
```

Per the file-bridge-protocol contract, no prior versions exist; no deletion or rewrite of prior versions occurs. All subsequent versions (Codex GO/NO-GO, post-impl REVISED, VERIFIED) will append new numbered files and add the verdict line at the top of this entry's version list. `bridge/INDEX.md` remains the canonical workflow state for this thread.

## Verification Plan

Loyal Opposition will, before issuing GO:

1. Confirm `Specification Links` cites every governing spec listed above.
2. Confirm the `target_paths` JSON enumerates the three touched files and no others.
3. Re-run `bridge_applicability_preflight.py` and `adr_dcl_clause_preflight.py` against the current bridge file; both must pass.
4. Confirm § Test Mapping derives directly from WI-3270 acceptance_summary + regression_visibility + the cited specs.
5. Confirm the INDEX update follows § Bridge Index Discipline above.

After implementation, Loyal Opposition will, before issuing VERIFIED:

1. Confirm the new files are present at the declared paths and contain only the in-scope behavior.
2. Run `python -m pytest platform_tests/scripts/test_cli_backlog_add.py -v` and confirm 12/12 passing.
3. Spot-run `python -m groundtruth_kb backlog add --dry-run ...` against a temp DB and confirm no production-DB mutation.
4. Spot-check that `cli.py`'s click registration didn't accidentally break the existing `gt backlog list` / `gt backlog migrate-work-list` commands (regression check: `gt backlog --help` lists three subcommands; the two existing tests for those subcommands still pass).
5. Confirm the post-impl report's spec-to-test mapping carries forward the linked specs from this proposal.

## Applicability Preflight

Mechanical preflight on the pre-INDEX content shows the proposal cites the cross-cutting required spec set (GOV-FILE-BRIDGE-AUTHORITY-001, DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001, DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001) plus the advisory set triggered by the content-match tokens "work item", "backlog", "MemBase", "candidate", and "artifact". Final preflight will be re-run by Loyal Opposition against the live bridge file once the INDEX entry lands; Prime's content-file preflight run is recorded in the proposal-prep evidence and reproduced in the post-impl report.

End of proposal.
