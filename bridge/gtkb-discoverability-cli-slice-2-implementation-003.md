REVISED
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 00d6b362-374c-4c5c-bf69-b7c23d0f2f58
author_model: Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code CLI default reasoning

Project Authorization: PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-DETERMINISTIC-SERVICES-PARALLEL-BATCH-GT-BRIDGE-PROPOSE-CLI
Project: PROJECT-GTKB-DETERMINISTIC-SERVICES-001
Work Item: WI-3262

# GT-KB Discoverability CLI Slice 2 - `gt backlog status` Implementation (REVISED-1)

bridge_kind: prime_proposal

Document: gtkb-discoverability-cli-slice-2-implementation
Version: 003 (REVISED-1; responds to Codex NO-GO at -002)
Date: 2026-05-29 UTC

## Response to NO-GO (-002)

Codex NO-GO at -002 raised one P1 finding (F1): the `scanner_caveat` text and Prior Deliberations cited `gtkb-project-completion-scanner-addressing-thread-fix-implementation`, which went terminal `WITHDRAWN` (at -004) during this session's parallel activity. The canonical scanner-fix thread is `gtkb-project-completion-scanner-addressing-thread-fix`, latest `GO` at `bridge/gtkb-project-completion-scanner-addressing-thread-fix-004.md` (verified against live `bridge/INDEX.md` before this revision). This was the cross-thread citation-freshness hazard under fast-trigger cycles.

Three corrections applied (no scope, design, or target_paths change):

1. `scanner_caveat` bridge reference changed to `gtkb-project-completion-scanner-addressing-thread-fix`.
2. Prior Deliberations updated to cite the canonical thread's GO at -004 (the withdrawn `-implementation` duplicate is noted as historical context only).
3. The scanner-caveat test expectation now asserts the canonical thread slug, not the withdrawn duplicate.

All Codex positive confirmations from -002 (read-only scope, single verb, narrow target_paths, raw-resolution_status base output, opt-in scanner flags, test matrix) are preserved unchanged.

## Summary

Implements the `gt backlog status` deterministic read-only CLI scoped and GO'd at `bridge/gtkb-discoverability-cli-slice-2-scoping-002.md`. One command consolidates the project + work-item rollup that Prime Builder currently reconstructs by hand with ad-hoc Python every time a session asks "what is the backlog state?" Per `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`, that recurring reconstruction is the defect this slice removes.

Scope is read-only: no MemBase writes, no bridge/INDEX.md mutation, no schema migration. Three files: a new service+CLI module, a one-line subcommand registration, and a new spec-derived test file.

## Owner Decisions / Input

This proposal proceeds on owner AskUserQuestion approvals captured this session (conversation `00d6b362-374c-4c5c-bf69-b7c23d0f2f58`):

1. DECISION-0758 (resolved this session): "start the triage".
2. Triage scope choice (AUQ): "Implementation gaps (Recommended)".
3. Gap 5 filing choice (AUQ): "File slice-2 scoping now (Recommended)".
4. Proceed signal: owner replied "go" after the Codex GO at scoping-002, authorizing the implementation proposal.

No new owner decision is required to review this revision (Codex stated "Prime can revise autonomously" on the -002 NO-GO). The PAUTH vehicle was confirmed appropriate by Codex at scoping-002.

## Specification Links

- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE - operative authority. This command is the deterministic-service conversion of a repeated manual status-reconstruction pattern.
- WI-3262 - parent work item. Active member of `PROJECT-GTKB-DETERMINISTIC-SERVICES-001` and its `-DISCOVERABILITY` sub-project.
- `gtkb-discoverability-cli-slice-2-scoping` GO at -002 - the scoping approval this implementation follows; left three implementation notes, all addressed in Design.
- `gtkb-discoverability-cli-slice-1` VERIFIED at -008 - predecessor slice; module + test pattern and single-verb scope discipline reused here.
- GOV-FILE-BRIDGE-AUTHORITY-001 - bridge/INDEX.md is canonical workflow state. This REVISED version is filed at -003, inserted atop the existing INDEX entry, append-only (the -001 NEW and -002 NO-GO versions are preserved).
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this Specification Links section satisfies the linkage gate.
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 - the Project Authorization / Project / Work Item triple in the header satisfies the linkage gate.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the spec-to-test mapping below maps each acceptance criterion to an executable test.
- GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001, DCL-PROJECT-AUTHORIZATION-ENVELOPE-001, PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001 - covered by the cited PAUTH (active; includes WI-3262; allows cli_extension + test_addition). After GO, Prime runs `python scripts/implementation_authorization.py begin --bridge-id gtkb-discoverability-cli-slice-2-implementation` before any source edit.
- GOV-STANDING-BACKLOG-001 - cited because this proposal reads work_items and the backlog. NOT a bulk mutation; see Clause Scope Clarification.
- GOV-ARTIFACT-APPROVAL-001 - this implementation creates no canonical artifact. Out of scope.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 (advisory) - references owner decisions, requirements, specifications, work items, and backlog.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 (advisory) - reads MemBase and deliberation/bridge artifacts; preserves traceability; mutates no artifact.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 (advisory) - surfaces `verified`, `retired`, `deferred` lifecycle states as observability outputs; transitions none.

## Clause Scope Clarification (Not a Bulk Operation)

Per the GOV-STANDING-BACKLOG-001 bulk-ops clause-scope clarification convention: this implementation is a READ-ONLY status-report CLI. It performs no backlog mutation, no work_items insert/update/retire/supersede, no project create/retire, no authorization change, no reorder, and no inventory mutation of existing rows. Evidence tokens: "status", "report", "JSON output", "read-only", "no DB writes", "inventory", "observability".

## Requirement Sufficiency

Existing requirements sufficient. No new specification capture required. The command is a read-only observability surface over existing MemBase tables and (opt-in) the existing canonical completion-scanner module.

## target_paths

- `groundtruth-kb/src/groundtruth_kb/cli_backlog_status.py` (new module: request dataclass + `build_backlog_status()` service + helpers)
- `groundtruth-kb/src/groundtruth_kb/cli.py` (register one new `@backlog.command("status")`; no other change)
- `platform_tests/scripts/test_cli_backlog_status.py` (new spec-derived test file)

No other path is authorized. No protected-narrative edit. No schema migration. No MemBase write path. No bridge/INDEX.md mutation by the implementation itself.

## Design

### CLI surface

```text
gt backlog status [--project <PID>] [--json] [--with-orphans] [--with-retire-ready] [--with-verified-coverage]
```

Registered as `@backlog.command("status")` following the exact house pattern of `backlog_list` / `backlog_show` (cli.py:692, 765): `@click.pass_context`, `config = _resolve_config(ctx)`, `db = _open_db(config)`, try/finally `db.close()`, JSON via `click.echo(json.dumps(..., indent=2, sort_keys=True))`.

### Base output (no flags) - MemBase only, deterministic

Sourced entirely from `db.list_projects()`, `db.list_work_items()`, and active `project_work_item_memberships` rows. Per project: `id`, `name`, `status`, `work_item_count`, `resolution_status_breakdown` (raw `resolution_status` values to counts - no derived terminal judgment), `doubled_prefix_flag` (true when id matches the phantom `PROJECT-PROJECT-*` pattern). Plus a `summary` block. `--project <PID>` filters to one project; `--json` emits machine-readable form.

### `--with-orphans`

Adds `orphan_work_items[]`: work items with NO active membership row, each with `id`, `title`, `resolution_status`, `project_name` column value. Reported across all resolution_status values; no invented "open" set.

### `--with-retire-ready` and `--with-verified-coverage` (opt-in; canonical-scanner-backed; caveated)

Both flags delegate to the existing canonical module `scripts/project_verified_completion_scanner.py`:

- `--with-retire-ready` reuses the scanner's per-authorization completion-readiness computation to add a `retire_ready[]` array.
- `--with-verified-coverage` reuses the scanner's `verified_work_items()` set to annotate each work item with a `verified_bridge_covered` boolean.

Both attach a top-level `scanner_caveat` field:

```text
"scanner_caveat": "VERIFIED-coverage uses scripts/project_verified_completion_scanner.py, whose D3+D4 over-broad-citation fix is in flight at bridge thread gtkb-project-completion-scanner-addressing-thread-fix (canonical thread; latest GO at bridge/gtkb-project-completion-scanner-addressing-thread-fix-004.md). Until that fix is VERIFIED, incidental Work Item citations in governance/reauthorization threads may over-count coverage."
```

(REVISED-1: the caveat slug is the canonical `gtkb-project-completion-scanner-addressing-thread-fix`; the previously-cited `-implementation` duplicate was WITHDRAWN.)

This honors Codex scoping note 1 (explicitly fail-safe/caveated), note 2 (no extra files - the scanner is imported, not duplicated), and note 3 (no second bridge parser - the scanner already uses `groundtruth_kb.bridge.detector.parse_index`; the base command does no bridge parsing).

When the canonical scanner-fix thread reaches VERIFIED, a one-line follow-on removes the caveat string; no structural change.

### Module shape

`cli_backlog_status.py` mirrors `cli_backlog_add.py`: a frozen `BacklogStatusRequest` dataclass, a pure `build_backlog_status(config, request) -> dict` service, and small private helpers. The CLI command is a thin wrapper.

## Spec-Derived Verification Plan

Per DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001, each acceptance criterion maps to a concrete test in `platform_tests/scripts/test_cli_backlog_status.py`:

| # | Acceptance criterion | Test |
|---|---|---|
| 1 | `gt backlog status` exits 0, emits projects with resolution_status_breakdown | `test_status_base_lists_projects_with_breakdown` |
| 2 | `--project <PID>` filters to one project | `test_status_project_filter` |
| 3 | `--json` output is parseable and schema-stable | `test_status_json_parseable_and_keys` |
| 4 | `--with-orphans` surfaces a membership-less WI | `test_status_orphans_surfaced` |
| 5 | `--with-retire-ready` surfaces a completion-ready authorization | `test_status_retire_ready_uses_scanner` |
| 6 | `--with-verified-coverage` annotates per-WI coverage | `test_status_verified_coverage_annotation` |
| 7 | retire-ready / verified-coverage output carries `scanner_caveat` naming the CANONICAL thread `gtkb-project-completion-scanner-addressing-thread-fix` (asserts the canonical slug; asserts the withdrawn `-implementation` slug is absent) | `test_status_scanner_caveat_present_when_flags_set` |
| 8 | Read-only: db file byte-identical before/after | `test_status_makes_no_db_writes` |
| 9 | `doubled_prefix_flag` set for a `PROJECT-PROJECT-*` project | `test_status_flags_doubled_prefix_project` |
| 10 | Base output (no flags) imports no scanner module | `test_status_base_has_no_scanner_dependency` |

Execution commands (at implementation report time):

```text
python -m pytest platform_tests/scripts/test_cli_backlog_status.py -q
python -m pytest platform_tests/scripts/test_check_harness_parity.py -q
```

## Recommended Commit Type

`feat:` - net-new CLI capability (`gt backlog status`) plus its spec-derived test file.

## Prior Deliberations

- `bridge/gtkb-discoverability-cli-slice-2-scoping-002.md` (Codex GO) - the scoping approval and its three implementation notes, all addressed in Design.
- `bridge/gtkb-discoverability-cli-slice-2-implementation-002.md` (Codex NO-GO) - the verdict this revision responds to (F1 stale citation).
- `bridge/gtkb-discoverability-cli-slice-1-008.md` (VERIFIED) - module + test + single-verb pattern reused here.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE - the principle this command instantiates.
- DELIB-S342-BACKLOG-WORK-ITEMS-CANONICAL-PIVOT - MemBase work_items is the canonical backlog source; this command reads it.
- `bridge/gtkb-cli-discoverability-doctor-json-backlog-show-003.md` (WITHDRAWN) - negative precedent against bundling multiple verbs; this slice stays single-verb.
- `bridge/gtkb-project-completion-scanner-addressing-thread-fix-004.md` (canonical scanner-fix thread, GO) - the in-flight D3+D4 fix the corrected `scanner_caveat` references. (The earlier-cited `gtkb-project-completion-scanner-addressing-thread-fix-implementation` duplicate thread was WITHDRAWN at -004 and is no longer the dependency.)
- `memory/feedback_bridge_protocol_iteration_throughput_s341.md` - the cross-thread citation-freshness hazard that produced the -002 NO-GO; verified live INDEX state before re-citing.

## Risk and Rollback

- Risk: scanner-backed flags inherit the scanner's over-broad-citation defect. Mitigation: the `scanner_caveat` field (now naming the canonical fix thread) makes this explicit in every flagged output; base command has zero scanner dependency (test 10).
- Risk: citation re-staleness if the canonical thread's status changes again. Mitigation: implementation reads the caveat target at implement time; the caveat is removed by design when that thread reaches VERIFIED.
- Risk: inventing a "terminal" WI definition. Mitigation: base output reports raw resolution_status counts; retire-ready delegates to the canonical scanner.
- Risk: second bridge parser. Mitigation: base command parses no bridge index; flagged paths reuse the scanner's `parse_index`-based logic.
- Rollback: read-only command; reverting the three-file commit removes the surface with no state to unwind.

## Codex Review Asks

1. Confirm the corrected canonical `scanner_caveat` thread reference resolves F1.
2. Confirm the base-command raw-resolution_status-breakdown approach avoids inventing a terminal-state definition.
3. Confirm the three-file target_paths is complete.
4. Flag any specification this proposal should cite but does not.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
