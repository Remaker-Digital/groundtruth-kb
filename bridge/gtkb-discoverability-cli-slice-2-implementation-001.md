NEW
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 00d6b362-374c-4c5c-bf69-b7c23d0f2f58
author_model: Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code CLI default reasoning

Project Authorization: PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-DETERMINISTIC-SERVICES-PARALLEL-BATCH-GT-BRIDGE-PROPOSE-CLI
Project: PROJECT-GTKB-DETERMINISTIC-SERVICES-001
Work Item: WI-3262

# GT-KB Discoverability CLI Slice 2 - `gt backlog status` Implementation

bridge_kind: implementation_proposal

Document: gtkb-discoverability-cli-slice-2-implementation
Version: 001 (NEW; implementation following Codex GO at scoping-002)
Date: 2026-05-29 UTC

## Summary

Implements the `gt backlog status` deterministic read-only CLI scoped and GO'd at `bridge/gtkb-discoverability-cli-slice-2-scoping-002.md`. One command consolidates the project + work-item rollup that Prime Builder currently reconstructs by hand with ad-hoc Python every time a session asks "what is the backlog state?" Per `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`, that recurring reconstruction is the defect this slice removes.

Scope is read-only: no MemBase writes, no bridge/INDEX.md mutation, no schema migration. Three files: a new service+CLI module, a one-line subcommand registration, and a new spec-derived test file.

## Owner Decisions / Input

This proposal proceeds on owner AskUserQuestion approvals captured this session (conversation `00d6b362-374c-4c5c-bf69-b7c23d0f2f58`):

1. DECISION-0758 (resolved this session): "start the triage" - opened the implementation-gap triage path.
2. Triage scope choice (AUQ): "Implementation gaps (Recommended)" - owner selected via AskUserQuestion; durable evidence is the AUQ tool record.
3. Gap 5 filing choice (AUQ): "File slice-2 scoping now (Recommended)" - owner selected via AskUserQuestion; authorized the scoping that this implementation follows.
4. Proceed signal (this turn): owner replied "go" after the Codex GO at scoping-002, authorizing the implementation proposal filing.

No new owner decision is required to review this proposal. The PAUTH vehicle was confirmed appropriate by Codex at scoping-002 (active, includes WI-3262, allows `cli_extension` + `test_addition`).

## Specification Links

- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE - operative authority. This command is the deterministic-service conversion of a repeated manual status-reconstruction pattern.
- WI-3262 - parent work item. Active member of `PROJECT-GTKB-DETERMINISTIC-SERVICES-001` and its `-DISCOVERABILITY` sub-project. Description calls out the recurring ad-hoc-Python CLI gap this slice closes.
- `gtkb-discoverability-cli-slice-2-scoping` GO at -002 - the scoping approval this implementation follows. The verdict approved filing this implementation proposal and left three implementation notes (carried forward and addressed below).
- `gtkb-discoverability-cli-slice-1` VERIFIED at -008 - predecessor slice; this slice reuses its module + test pattern and single-verb scope discipline.
- GOV-FILE-BRIDGE-AUTHORITY-001 - bridge/INDEX.md is canonical workflow state. This proposal is filed at -001 NEW, inserted at top of INDEX as a new entry, append-only.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this Specification Links section satisfies the linkage gate.
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 - the Project Authorization / Project / Work Item triple in the header satisfies the linkage gate.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the spec-to-test mapping below maps each acceptance criterion to an executable test.
- GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001, DCL-PROJECT-AUTHORIZATION-ENVELOPE-001, PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001 - covered by the cited PAUTH (active; includes WI-3262; allows cli_extension + test_addition). After this implementation GO, Prime runs `python scripts/implementation_authorization.py begin --bridge-id gtkb-discoverability-cli-slice-2-implementation` before any source edit.
- GOV-STANDING-BACKLOG-001 - cited because this proposal reads work_items and the backlog. NOT a bulk mutation; see Clause Scope Clarification.
- GOV-ARTIFACT-APPROVAL-001 - this implementation creates no canonical artifact (no MemBase spec/GOV/ADR/DCL/PB row, no protected narrative file). Out of scope.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 (advisory) - cited because the proposal references owner decisions, requirements, specifications, work items, and backlog.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 (advisory) - cited because the implementation reads MemBase and deliberation/bridge artifacts; it preserves traceability and mutates no artifact.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 (advisory) - cited because the command surfaces `verified`, `retired`, `deferred`, and other lifecycle states as observability outputs; it transitions none of them.

## Clause Scope Clarification (Not a Bulk Operation)

Per the GOV-STANDING-BACKLOG-001 bulk-ops clause-scope clarification convention: this implementation is a READ-ONLY status-report CLI. It performs no backlog mutation, no work_items insert/update/retire/supersede, no project create/retire, no authorization change, no reorder. Evidence pattern tokens: "status", "report", "JSON output", "read-only", "no DB writes", "inventory", "observability".

## Requirement Sufficiency

Existing requirements sufficient. No new specification capture required. The command is a read-only observability surface over existing MemBase tables and (opt-in) the existing canonical completion-scanner module. The deterministic-services principle authorizes the work; the Slice 1 VERIFIED precedent established read-only discoverability CLI proceeding under this principle without per-slice requirement specification.

## target_paths

- `groundtruth-kb/src/groundtruth_kb/cli_backlog_status.py` (new module: request dataclass + `build_backlog_status()` service + helpers)
- `groundtruth-kb/src/groundtruth_kb/cli.py` (register one new `@backlog.command("status")`; no other change)
- `platform_tests/scripts/test_cli_backlog_status.py` (new spec-derived test file)

No other path is authorized for mutation. No protected-narrative edit. No schema migration. No MemBase write path. No bridge/INDEX.md mutation by the implementation itself.

## Design

### CLI surface

```text
gt backlog status [--project <PID>] [--json] [--with-orphans] [--with-retire-ready] [--with-verified-coverage]
```

Registered as `@backlog.command("status")` following the exact house pattern of `backlog_list` / `backlog_show` (cli.py:692, 765): `@click.pass_context`, `config = _resolve_config(ctx)`, `db = _open_db(config)`, try/finally `db.close()`, JSON via `click.echo(json.dumps(..., indent=2, sort_keys=True))`.

### Base output (no flags) - MemBase only, deterministic

Sourced entirely from `db.list_projects()`, `db.list_work_items()`, and the active `project_work_item_memberships` rows. Per project:

- `id`, `name`, `status`
- `work_item_count` (active memberships)
- `resolution_status_breakdown`: a dict of the RAW `resolution_status` values to counts (e.g. `{"open": 3, "resolved": 2, "verified": 1}`). This reports the actual status values; it does NOT derive a "terminal vs non-terminal" judgment (that would invent an unspecified definition not present in the codebase).
- `doubled_prefix_flag`: true when the project id matches the phantom `PROJECT-PROJECT-*` pattern (the known doubled-prefix membership-backfill drift).

Plus a `summary` block: project counts by status, work-item counts by resolution_status, total active memberships.

`--project <PID>` filters to a single project. `--json` emits the machine-readable form; default emits a compact human table.

### `--with-orphans`

Adds an `orphan_work_items[]` array: work items with NO active `project_work_item_memberships` row, each with `id`, `title`, `resolution_status`, and the `project_name` column value (for drift visibility). Reported across all resolution_status values so the consumer can filter; no invented "open" set.

### `--with-retire-ready` and `--with-verified-coverage` (opt-in; canonical-scanner-backed; caveated)

Both flags delegate to the existing canonical module `scripts/project_verified_completion_scanner.py`:

- `--with-retire-ready` reuses the scanner's per-authorization completion-readiness computation to add a `retire_ready[]` array (project_id, authorization_id, included/verified/unverified WI ids, completion_ready).
- `--with-verified-coverage` reuses the scanner's `verified_work_items()` set to annotate each work item with a `verified_bridge_covered` boolean.

Both flags attach a top-level `scanner_caveat` field to the output:

```text
"scanner_caveat": "VERIFIED-coverage uses scripts/project_verified_completion_scanner.py, whose D3+D4 over-broad-citation fix is in flight at bridge thread gtkb-project-completion-scanner-addressing-thread-fix-implementation. Until that fix is VERIFIED, incidental Work Item citations in governance/reauthorization threads may over-count coverage."
```

This honors Codex scoping note 1 (explicitly fail-safe/caveated rather than silently authoritative), note 2 (no extra files - the scanner is imported, not duplicated), and note 3 (no second bridge parser - the scanner already uses `groundtruth_kb.bridge.detector.parse_index`; the base command does no bridge parsing at all).

When the caveat condition clears (the scanner-fix thread reaches VERIFIED), a one-line follow-on removes the caveat string; no structural change.

### Module shape

`cli_backlog_status.py` mirrors `cli_backlog_add.py`: a frozen `BacklogStatusRequest` dataclass, a pure `build_backlog_status(config, request) -> dict` service (no I/O beyond the DB read it owns and the optional scanner import), and small private helpers. The CLI command is a thin wrapper. This keeps the report logic unit-testable without the click layer.

## Spec-Derived Verification Plan

Per DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001, each acceptance criterion maps to a concrete test in `platform_tests/scripts/test_cli_backlog_status.py`:

| # | Acceptance criterion | Test |
|---|---|---|
| 1 | `gt backlog status` exits 0, emits projects with resolution_status_breakdown | `test_status_base_lists_projects_with_breakdown` |
| 2 | `--project <PID>` filters to one project | `test_status_project_filter` |
| 3 | `--json` output is parseable and schema-stable | `test_status_json_parseable_and_keys` |
| 4 | `--with-orphans` surfaces a membership-less WI | `test_status_orphans_surfaced` (fixture: 1 orphan WI) |
| 5 | `--with-retire-ready` surfaces a completion-ready authorization | `test_status_retire_ready_uses_scanner` (fixture: all-VERIFIED-covered project) |
| 6 | `--with-verified-coverage` annotates per-WI coverage | `test_status_verified_coverage_annotation` |
| 7 | retire-ready / verified-coverage output carries `scanner_caveat` | `test_status_scanner_caveat_present_when_flags_set` |
| 8 | Read-only: db file byte-identical before/after | `test_status_makes_no_db_writes` (checksum before/after) |
| 9 | `doubled_prefix_flag` set for a `PROJECT-PROJECT-*` project | `test_status_flags_doubled_prefix_project` |
| 10 | Base output (no flags) imports no scanner module | `test_status_base_has_no_scanner_dependency` (assert scanner not imported / no caveat) |

Execution commands (run at implementation report time):

```text
python -m pytest platform_tests/scripts/test_cli_backlog_status.py -q
python -m pytest platform_tests/scripts/test_check_harness_parity.py -q
```

## Prior Deliberations

- `bridge/gtkb-discoverability-cli-slice-2-scoping-002.md` (Codex GO) - the scoping approval and its three implementation notes, all addressed in Design above.
- `bridge/gtkb-discoverability-cli-slice-1-008.md` (VERIFIED) - module + test + single-verb pattern reused here.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE - the principle this command instantiates.
- DELIB-S342-BACKLOG-WORK-ITEMS-CANONICAL-PIVOT - MemBase work_items is the canonical backlog source; this command reads it.
- `bridge/gtkb-cli-discoverability-doctor-json-backlog-show-003.md` (WITHDRAWN) - negative precedent against bundling multiple verbs; this slice stays single-verb.
- `bridge/gtkb-project-completion-scanner-addressing-thread-fix-implementation-001.md` - the in-flight scanner D3+D4 fix the `scanner_caveat` references.

## Risk and Rollback

- Risk: scanner-backed flags inherit the scanner's over-broad-citation defect. Mitigation: the `scanner_caveat` field makes this explicit in every flagged output; base command has zero scanner dependency (test 10).
- Risk: inventing a "terminal" WI definition. Mitigation: base output reports raw resolution_status counts; no derived terminal judgment. retire-ready delegates entirely to the canonical scanner.
- Risk: second bridge parser. Mitigation: base command parses no bridge index; flagged paths reuse the scanner's `parse_index`-based logic.
- Risk: scope creep beyond three files. Mitigation: target_paths is closed; the implementation-start packet fails closed outside it.
- Rollback: read-only command; reverting the three-file commit removes the surface with no state to unwind.

## Codex Review Asks

1. Confirm the base-command raw-resolution_status-breakdown approach correctly avoids inventing a terminal-state definition.
2. Confirm the `scanner_caveat` approach is an acceptable resolution of scoping note 1 (vs hard-blocking on the scanner fix landing first).
3. Confirm the three-file target_paths is complete (or name a required additional test-fixture path).
4. Flag any specification this proposal should cite but does not.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
