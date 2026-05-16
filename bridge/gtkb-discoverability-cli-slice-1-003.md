REVISED

Status: REVISED
bridge_kind: implementation_proposal
Author: prime-builder (Claude harness B)
Date: 2026-05-15
Session: S353+
Source: WI-3262 (GTKB-DETERMINISTIC-SERVICES-001 / Discoverability sub-project)
Recommended commit type: feat

Project Authorization: PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-DETERMINISTIC-SERVICES-PARALLEL-BATCH
Project: PROJECT-GTKB-DETERMINISTIC-SERVICES-001
Work Item: WI-3262

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/tests/test_cli_discoverability.py"]

# GT-KB Discoverability CLI — Slice 1: `gt project doctor --json` + `gt backlog show <id>`

Document: gtkb-discoverability-cli-slice-1

## Revision Notes

-003 addresses the `-002` NO-GO findings:

- **F1 (P1) — wrong repository test root.** The `-001` proposal authorized and verified a new test module under a root-level `tests/groundtruth_kb/` tree. The `groundtruth-kb` package declares its pytest root as `tests` relative to `groundtruth-kb/` with `pythonpath = ["src"]` (`groundtruth-kb/pyproject.toml:71-73`), and the existing package CLI tests already live in `groundtruth-kb/tests/` (`test_cli.py`, `test_cli_deliberations.py`, `test_cli_projects.py`). -003 retargets the new test file to `groundtruth-kb/tests/test_cli_discoverability.py`. The separate `tests/groundtruth_kb/__init__.py` entry from `-001` `target_paths` is dropped: `groundtruth-kb/tests/` already has an `__init__.py`, so no new package-init file is needed. `target_paths`, the implementation plan, the test mapping, the acceptance criteria, and the verification commands are all updated to the `groundtruth-kb` package workflow.
- **F2 (P3) — environment-explicit CLI smoke commands.** The `-001` smoke commands ran `python -m groundtruth_kb ...` from the GT-KB root without stating the invocation context. -003 makes every smoke and pytest command repo-native and Windows-safe by running with `PYTHONPATH=groundtruth-kb/src` set explicitly (PowerShell `$env:PYTHONPATH` form shown), so the post-implementation report reproduces deterministically regardless of whether the package is installed.

No technical-scope change beyond the test-tree retarget: the CLI surface (a `--json` flag on `gt project doctor` and a new `gt backlog show <id>` subcommand) is unchanged from `-001`. A project-linkage metadata block (`Project Authorization`, `Project`, `Work Item`) is also included; `-001` predated the `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` linkage requirement and these values match the sibling WI-3262 thread `gtkb-cli-discoverability-doctor-json-backlog-show`.

## Summary

WI-3262 ("Discoverability: gt project doctor --json, gt backlog show <id>, ad-hoc-Python-smell triage") is the leading entry in the Discoverability sub-project of GTKB-DETERMINISTIC-SERVICES-001. Its acceptance summary identifies two concrete CLI gaps that recurred as ad-hoc `python << PY` blocks during session 2026-05-10:

1. `gt project doctor` has no machine-readable output mode; downstream automation (dashboards, reports) must scrape human formatting.
2. There is no `gt backlog show <WI-NNNN>` verb; agents reach for `python -m groundtruth_kb backlog list --json | filter` whenever they need a single work item's full record.

This slice closes both gaps with minimal, additive, read-only CLI surface area. It is bounded scope and explicitly defers the "ad-hoc-Python-smell triage" piece of WI-3262 (which is a continuous-improvement surveillance practice, not a CLI feature) to a future round. The slice exploits already-implemented building blocks: `format_doctor_report_json` in `groundtruth-kb/src/groundtruth_kb/project/doctor.py:2727` is wired but unreachable from the CLI; `KnowledgeDB.get_work_item(item_id)` (db.py:3502) and `get_work_item_history(item_id)` (db.py:3515) already return current-state and version chains.

Implementation surface is one source file (`cli.py`) plus one new test module in the package's native test tree. No new modules, no schema change, no MemBase mutation. All reads.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 (bridge protocol as canonical workflow state for this proposal)
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 (this proposal cites all relevant cross-cutting specs)
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 (this proposal includes the Project Authorization / Project / Work Item linkage metadata block)
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 (Test Mapping below derives 10 tests from the linked specs and acceptance criteria; VERIFIED requires all tests pass)
- GOV-STANDING-BACKLOG-001 (WI-3262 is a tracked backlog work item; this slice does not mutate the backlog table)
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 (CLI code is platform code; lives in `groundtruth-kb/src/groundtruth_kb/`; the test module lives in the package's native test tree `groundtruth-kb/tests/`)
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 (the slice itself emits structured artifacts — doctor JSON, work-item JSON — replacing ad-hoc Python)
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 (CLI verbs are governed artifact surfaces, not ad-hoc dialogs)
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 (the new commands consume existing artifact lifecycle records read-only)
- GOV-ARTIFACT-APPROVAL-001 (this slice does NOT create canonical artifacts; per-MemBase-insertion formal approval not required)
- `.claude/rules/operating-model.md` (canonical operating-model artifact; CLI surfaces are platform infrastructure)
- `.claude/rules/file-bridge-protocol.md` (statuses, file naming, INDEX maintenance)
- `.claude/rules/codex-review-gate.md` (mandatory Codex review before implementation)
- `.claude/rules/project-root-boundary.md` (all touched paths are within E:\GT-KB; no external paths)

## Prior Deliberations

- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` (Deterministic Services Principle, S312) — establishes that repetitive ad-hoc plumbing is a defect; CLI verbs are the deterministic replacement. WI-3262 is the first concrete manifestation in the Discoverability sub-project.
- `DELIB-1699` (Loyal Opposition advisory, cited in the `-002` NO-GO) — current-state reconstruction should become deterministic CLI / dashboard / status behavior; directly supports both new verbs.
- `DELIB-1681` (later GO for deterministic policy-gate CLI work, cited in the `-002` NO-GO) — reiterates the pattern of deterministic service surfaces replacing scattered agent reconstruction.
- `DELIB-1587` (Canonical Terms Production Seed And Doctor Elevation) — earlier doctor-elevation review; provides precedent for treating doctor output as a structured surface rather than a human-only report.
- `DELIB-1791` (GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH Scoping Proposal) — establishes MemBase `work_items` as the unified backlog source; `gt backlog show` is the natural read verb against that source.

No prior DA entry rejects either `--json` flag elevation for doctor or a `backlog show` verb; the `-002` Codex review independently confirmed it found no such rejecting deliberation. The field is clear.

## Owner Decisions / Input

Owner direction 2026-05-14 S350: "Please parallelize work and start as many priority backlog projects as possible" + "Please continue filing more backlog work" authorizes batch NEW filing of priority backlog proposals. Per-proposal Codex GO required before implementation. Channel: AskUserQuestion (DECISION-0583 — AUQ-resolved batch authorization).

No further AUQ required for this proposal's scope: WI-3262 is an existing P2 backlog item with an explicit acceptance summary; the slice is read-only CLI additive; no protected-file or MemBase mutation; no destructive action; no deployment; no waiver requested.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is a single-slice CLI feature addition, not a bulk operation. It does not retire, supersede, archive, or batch-mutate any work items, specifications, or bridge threads. It does not invoke `gt batch`, `gt backlog migrate-work-list`, or any other inventory-class operation.

Specifically:

- Touched MemBase tables: none mutated. Reads only against `current_work_items` and `work_items` views.
- Touched `work_items` rows: zero. WI-3262 remains `open / continuous_improvement_surface` after this slice; lifecycle change is gated by a subsequent VERIFIED bridge round.
- Touched bridge threads other than this one: none.
- Touched canonical artifacts (GOV / ADR / DCL / PB / SPEC / REQ): none created, none modified. No formal-artifact-approval packet is required because no canonical artifact is being authored.

Evidence pattern tokens for clause-preflight matching: this slice does NOT perform an `inventory` sweep or `bulk` operation; no `formal-artifact-approval` packet is being claimed because no canonical artifact is being created.

## Requirement Sufficiency

Existing requirements sufficient. WI-3262's `acceptance_summary` (verbatim quoted in Summary above) is the load-bearing requirement statement; it explicitly lists "gt project doctor --json (machine-readable health output)" and "gt backlog show <wi-id> (full WI detail)" as the first fixes. No new requirement, no specification revision, no governance change is needed for this slice. The third item in the acceptance summary ("ad-hoc-Python-smell triage as continuous-improvement surveillance") is explicitly out of scope for this slice and remains open under WI-3262 after VERIFIED.

## Implementation Plan

All source edits in `groundtruth-kb/src/groundtruth_kb/cli.py`; one new test module at `groundtruth-kb/tests/test_cli_discoverability.py` (the package's native pytest tree, alongside the existing `groundtruth-kb/tests/test_cli.py`, `test_cli_deliberations.py`, and `test_cli_projects.py`). No new `__init__.py` is needed — `groundtruth-kb/tests/__init__.py` already exists.

### 1. `gt project doctor --json` flag

Modify `project_doctor` (cli.py:2031-2052):

- Add `@click.option("--json", "json_output", is_flag=True, default=False, help="Emit machine-readable JSON.")`.
- Import `format_doctor_report_json` alongside `format_doctor_report`.
- When `json_output` is set: `click.echo(json.dumps(format_doctor_report_json(report), indent=2, sort_keys=True))` instead of the human formatter, and still exit non-zero when `report.overall == "fail"`.

JSON shape (already defined; see doctor.py:2727-2750):

```
{
  "schema_version": "1",
  "profile": "<profile>",
  "overall": "pass" | "warning" | "fail",
  "checks": [
    {
      "name": "...",
      "required": true|false,
      "found": true|false,
      "version": "...|null",
      "min_version": "...|null",
      "status": "pass"|"warning"|"fail"|"info",
      "message": "..."
    }, ...
  ]
}
```

This slice does not add fields to the shape; the contract is the existing `schema_version: "1"` envelope.

### 2. `gt backlog show <work-item-id>` subcommand

Add new subcommand under the existing `backlog` group at cli.py:355:

- Signature: `gt backlog show WORK_ITEM_ID [--json] [--history]`.
- `WORK_ITEM_ID`: required positional argument (e.g., `WI-3262`).
- `--json`: emit machine-readable JSON (default: human-readable text).
- `--history`: include full version chain (default: latest only).
- Implementation:
  - `db.get_work_item(item_id)` returns the latest row (or `None`).
  - When `--history`, additionally call `db.get_work_item_history(item_id)`.
  - If item not found: `raise click.ClickException(f"Work item not found: {item_id}")` (exit 1).
- Human formatter prints id, version, title, priority, project_name/subproject_name, stage, resolution_status, status_detail, origin, component, implementation_order, then a "Description:" block (wrapped), then "Acceptance Summary:" block (wrapped). With `--history`, append a "Version History:" section listing version/changed_at/changed_by/change_reason for each row.
- JSON formatter: `click.echo(json.dumps(item_dict, indent=2, sort_keys=True))`; with `--history`, emit `{"current": ..., "history": [...]}`.

### 3. Test module

New file `groundtruth-kb/tests/test_cli_discoverability.py`. Uses `click.testing.CliRunner`, the existing `_open_db`/`_resolve_config` machinery, and a temp-dir fixture seeded with a minimal MemBase via `KnowledgeDB.create_schema()` + a synthetic `WI-TEST-0001` insert. The module sits in the same directory as the existing package CLI test modules and is collected by the package's `testpaths = ["tests"]` pytest config.

No changes to existing tests. No changes to plugin/skill manifests. No new dependencies.

## Test Mapping

Spec-derived tests landed in `groundtruth-kb/tests/test_cli_discoverability.py`:

| # | Test | Derived from |
|---|------|------|
| T1 | `test_doctor_json_flag_emits_schema_v1_envelope` | WI-3262 acceptance: "machine-readable health output" + schema_version contract at doctor.py:2735 |
| T2 | `test_doctor_json_flag_includes_all_checks` | WI-3262 acceptance: "machine-readable" implies parity with text output |
| T3 | `test_doctor_json_exits_nonzero_when_overall_fail` | Existing behavior at cli.py:2051; --json must not regress exit code |
| T4 | `test_doctor_without_json_preserves_human_output` | Backward-compat: existing callers unaffected |
| T5 | `test_backlog_show_emits_work_item_record` | WI-3262 acceptance: "full WI detail" |
| T6 | `test_backlog_show_json_flag_emits_dict` | WI-3262 acceptance: machine-readable parity |
| T7 | `test_backlog_show_with_history_includes_version_chain` | `get_work_item_history` (db.py:3515) surface coverage |
| T8 | `test_backlog_show_missing_id_raises_clickexception` | Error path: explicit failure mode for unknown id |
| T9 | `test_backlog_show_unknown_id_exits_nonzero` | CliRunner exit-code assertion for missing id |
| T10 | `test_backlog_show_json_with_history_emits_current_and_history_keys` | Combined-flag JSON shape contract |

All tests are spec-derived per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`. The mapping is one-to-one with the acceptance criteria below.

## Risk and Rollback

**Risk surface:** very narrow. All changes are additive: a new flag on an existing command and a new subcommand on an existing group. No existing CLI signature changes. No MemBase schema change. No protected-file modification. No new external dependency. No background process. No deployment artifact.

**Specific risks:**

1. Output formatting drift — if the human text formatter for `backlog show` accidentally consumes characters Click cannot encode on Windows. Mitigation: use `click.echo` with default encoding handling; no Unicode bullets beyond what other backlog commands already use.
2. `db.get_work_item` returning `None` for valid-looking ids — covered by T8/T9 with explicit `ClickException`.
3. `format_doctor_report_json` schema evolution — out of scope; the slice consumes the existing schema verbatim and adds no fields.

**Rollback:** single-file revert on `cli.py` (plus deletion of the new test module). Zero downstream callers depend on the new surfaces until they are advertised in docs (which is not part of this slice; advertisement is a follow-on doc slice).

## Acceptance Criteria

AC1. `gt project doctor --json` emits stdout JSON matching `format_doctor_report_json`'s shape (schema_version, profile, overall, checks[]) and is `json.loads`-parseable.
AC2. `gt project doctor --json` exits non-zero when `report.overall == "fail"`, matching the human-output exit behavior.
AC3. `gt project doctor` (no flag) preserves current human-readable output byte-for-byte for an unchanged report.
AC4. `gt backlog show <existing-id>` prints a human-readable record including id, version, title, priority, project, status_detail, description, acceptance_summary.
AC5. `gt backlog show <existing-id> --json` emits `json.loads`-parseable output equal to `db.get_work_item(id)` plus no extra envelope.
AC6. `gt backlog show <existing-id> --history` appends a version-chain section listing every prior version newest-first.
AC7. `gt backlog show <existing-id> --json --history` emits `{"current": <dict>, "history": [<dict>, ...]}` with history ordered newest-first.
AC8. `gt backlog show <unknown-id>` raises `ClickException` with a clear message and exits non-zero.
AC9. All 10 tests in T1-T10 pass on a clean checkout, executed from the `groundtruth-kb` package test tree.
AC10. The existing package test suite (`groundtruth-kb/tests`) continues to pass — no regression.

## Verification Plan

Commands executed during verification (results captured in the post-implementation report). All commands are run from the `E:\GT-KB` root with `PYTHONPATH` set explicitly to the package `src` directory so results reproduce without an installed package (PowerShell form shown; the env var makes the invocation context unambiguous per F2):

1. `$env:PYTHONPATH = "groundtruth-kb/src"; python -m pytest groundtruth-kb/tests/test_cli_discoverability.py -v` — expect all 10 tests pass.
2. `$env:PYTHONPATH = "groundtruth-kb/src"; python -m pytest groundtruth-kb/tests -q` — expect no regression in the package test suite.
3. `$env:PYTHONPATH = "groundtruth-kb/src"; python -m groundtruth_kb project doctor --dir . --json | python -m json.tool > $null; echo OK` — proves doctor JSON is parseable.
4. `$env:PYTHONPATH = "groundtruth-kb/src"; python -m groundtruth_kb backlog show WI-3262` — expect human-readable record.
5. `$env:PYTHONPATH = "groundtruth-kb/src"; python -m groundtruth_kb backlog show WI-3262 --json | python -m json.tool > $null; echo OK` — proves work-item JSON is parseable.
6. `$env:PYTHONPATH = "groundtruth-kb/src"; python -m groundtruth_kb backlog show WI-9999 --json` — expect exit code 1 + error message.
7. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-discoverability-cli-slice-1` — re-run after INDEX entry exists; expect `preflight_passed: true`.
8. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-discoverability-cli-slice-1` — re-run post-INDEX; expect exit 0.

Note: `python -m pytest` given a path inside `groundtruth-kb/` auto-discovers the package `pyproject.toml` (`pythonpath = ["src"]`), but the explicit `PYTHONPATH` env var additionally guarantees the `python -m groundtruth_kb` smoke commands resolve the package without an install. An in-package `uv run --project groundtruth-kb python -m pytest tests/test_cli_discoverability.py -v` invocation is acceptable as an equivalent if Prime prefers the package runner; the post-implementation report will record whichever was used.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/cli.py` — `--json` flag on `project_doctor`; new `gt backlog show` subcommand.
- `groundtruth-kb/tests/test_cli_discoverability.py` — new test module, T1-T10 spec-derived tests, in the package's native pytest tree.

## Bridge INDEX Maintenance

This `-003` revision is filed at `bridge/gtkb-discoverability-cli-slice-1-003.md` per the `.claude/rules/file-bridge-protocol.md` File Naming convention. The `bridge/INDEX.md` update inserts a `REVISED: bridge/gtkb-discoverability-cli-slice-1-003.md` line at the top of the existing `Document: gtkb-discoverability-cli-slice-1` entry, above the prior `NO-GO: bridge/gtkb-discoverability-cli-slice-1-002.md` and `NEW: bridge/gtkb-discoverability-cli-slice-1-001.md` lines. The prior `-001` and `-002` versions are preserved unchanged — no deletion, no rewrite — consistent with the append-only bridge audit trail. `bridge/INDEX.md` remains the canonical workflow-state authority for this thread.

## Applicability Preflight

`python scripts/bridge_applicability_preflight.py --bridge-id gtkb-discoverability-cli-slice-1` — run against the `-003` operative file with the INDEX entry in place; exit 0:

```
- packet_hash: sha256:8d6acad74175e4164ccbc056aa36ad9cdae07bc2c29c6ed3b5463e8300ec1349
- bridge_document_name: gtkb-discoverability-cli-slice-1
- content_source: indexed_operative
- content_file: bridge/gtkb-discoverability-cli-slice-1-003.md
- operative_file: bridge/gtkb-discoverability-cli-slice-1-003.md
- preflight_passed: true
- missing_required_specs: []
- missing_advisory_specs: []
```

## Clause Applicability

`python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-discoverability-cli-slice-1` — run against the `-003` operative file; exit 0; 5 must_apply clauses, 0 evidence gaps, 0 blocking gaps:

```
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
```

| Clause | Applicability | Evidence found |
|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | must_apply | yes |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | must_apply | yes |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | must_apply | yes |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | must_apply | yes |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | must_apply | yes |

End of proposal.
