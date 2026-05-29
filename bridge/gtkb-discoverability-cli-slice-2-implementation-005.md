NEW
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: claude-2026-05-29-discoverability-cli-slice-2-implementation-post-impl
author_model: claude-opus-4
author_model_version: 4.7-1M
author_model_configuration: explanatory output style; interrogative-default Prime Builder
author_metadata_source: Claude Code session environment

# Post-Implementation Report - GT-KB Discoverability CLI Slice 2 (WI-3262)

bridge_kind: implementation_report
Document: gtkb-discoverability-cli-slice-2-implementation
Version: 005 (NEW; post-implementation report following Codex GO at -004)
Author: Prime Builder (Claude Code, harness B)
Date: 2026-05-29 UTC
Responds to GO: bridge/gtkb-discoverability-cli-slice-2-implementation-004.md

Project Authorization: PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-DETERMINISTIC-SERVICES-PARALLEL-BATCH-GT-BRIDGE-PROPOSE-CLI
Project: PROJECT-GTKB-DETERMINISTIC-SERVICES-001
Work Item: WI-3262
Implementation-Start Packet Hash: sha256:7510cb38a96c8aa7cc245d39bba8288e8d1c3e784c87cdb96cedcc9dbaa25303
GO File: bridge/gtkb-discoverability-cli-slice-2-implementation-004.md

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli_backlog_status.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "platform_tests/scripts/test_cli_backlog_status.py"]

Recommended commit type: feat:

## Summary

The `gt backlog status` deterministic read-only CLI is implemented and verified. Three files landed exactly within the GO'd target_paths: a new service+module file (`cli_backlog_status.py`), a single `@backlog.command("status")` registration block added to `cli.py`, and a new spec-derived test file (`test_cli_backlog_status.py`). All 10 tests in the spec-derived verification plan PASS. The mandatory companion suite `test_check_harness_parity.py` PASSES with 6/6 tests, confirming no harness-parity regression from the CLI extension.

Live smoke-test against the canonical `groundtruth.db` is also notable: `gt backlog status --json` reports 157 projects, 10 of which carry the `doubled_prefix_flag` set. That 10-count matches the owner-stated phantom inventory ("phantom PROJECT-PROJECT-* reconciliation - 10 projects, WI-3355") exactly, confirming that the canonical store contains the drift the deferred follow-on is meant to reconcile.

The command is read-only by design and by test (test 8 verifies the database file is byte-identical before and after invocation).

## Specification Links

- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE - operative authority; this command is the deterministic-service conversion of a recurring manual status-reconstruction pattern.
- WI-3262 - parent work item; active member of PROJECT-GTKB-DETERMINISTIC-SERVICES-001 and its -DISCOVERABILITY sub-project.
- gtkb-discoverability-cli-slice-2-scoping GO at -002 - scoping approval addressed in Design.
- gtkb-discoverability-cli-slice-1 VERIFIED at -008 - predecessor slice; module + test pattern + single-verb scope discipline reused here.
- GOV-FILE-BRIDGE-AUTHORITY-001 - bridge protocol; this report follows the post-implementation -> VERIFIED workflow; bridge/INDEX.md updated with new top entry for this report.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this section + the Spec-to-Test Mapping below provide spec linkage carried forward into post-implementation evidence.
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 - Project Authorization / Project / Work Item triple in header present; WI-3262 active member of PROJECT-GTKB-DETERMINISTIC-SERVICES-001.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the Spec-to-Test Mapping below maps every acceptance criterion to executable test commands + observed results.
- PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-DETERMINISTIC-SERVICES-PARALLEL-BATCH-GT-BRIDGE-PROPOSE-CLI - active; includes WI-3262; allows cli_extension + test_addition; impl-start packet hash above ties this report to a live latest-GO authorization.
- GOV-STANDING-BACKLOG-001 - cited because this proposal reads work_items and the backlog. NOT a bulk mutation: command is read-only by design and by test.
- GOV-ARTIFACT-APPROVAL-001 - this implementation creates no canonical artifact. Out of scope.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 (advisory) - references owner decisions, requirements, specifications, work items, and backlog.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 (advisory) - reads MemBase and deliberation/bridge artifacts; preserves traceability; mutates no artifact.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 (advisory) - surfaces verified, retired, deferred lifecycle states as observability outputs; transitions none.

## Implementation Evidence

### IP-1 - cli_backlog_status.py (new module)

Created `groundtruth-kb/src/groundtruth_kb/cli_backlog_status.py` (211 lines). Module structure mirrors `cli_backlog_add.py`:

- A frozen `BacklogStatusRequest` dataclass carrying the four flag-state fields (`project`, `with_orphans`, `with_retire_ready`, `with_verified_coverage`).
- A public `build_backlog_status(config, request) -> dict[str, Any]` service that opens MemBase, performs only reads, and closes the connection before returning.
- Private helpers `_doubled_prefix_flag`, `_project_row`, `_list_orphan_work_items`, `_annotate_verified_coverage`.
- A module-level `SCANNER_CAVEAT` constant referencing the canonical scanner-fix thread `gtkb-project-completion-scanner-addressing-thread-fix` (NOT the withdrawn `-implementation` duplicate).

The scanner import is lazy: the `from scripts.project_verified_completion_scanner import completion_ready, verified_work_items` line lives inside the conditional `if request.with_retire_ready or request.with_verified_coverage:` block in `build_backlog_status`. This honors test 10's contract that the base command path has zero scanner-module dependency.

### IP-2 - cli.py (one new command registration)

Added one `@backlog.command("status")` block immediately after `backlog_show` (cli.py, ~line 791 in current state) and before the `# gt projects` divider. The block follows the exact house pattern used by `backlog_show` and the predecessor slice-1 command: `@click.pass_context`, `_resolve_config(ctx)` for config resolution, a `BacklogStatusRequest` construction, a call to `build_backlog_status`, and a JSON-vs-human-readable branch on `--json`. The CLI imports `BacklogStatusRequest` and `build_backlog_status` inside the function body (function-local lazy import) to match the slice-1 pattern.

The change is additive: no existing line in `cli.py` was modified. Net diff on `cli.py`: +83 lines (one new command function + its decorators + the function body). Other dirty content in `cli.py` belongs to unrelated parallel-session work and will be staged out at commit time.

### IP-3 - test_cli_backlog_status.py (new test file)

Created `platform_tests/scripts/test_cli_backlog_status.py` (10 tests, ~395 lines). Each test maps to one row in the spec-derived verification matrix (see below). The seed fixture deliberately creates a phantom doubled-prefix project (`PROJECT-PROJECT-GTKB-Y`) via `db.insert_project(id="PROJECT-PROJECT-GTKB-Y", ...)` so the seed is independent of whether the idempotent `_project_id_from_names` fix is active in the running process. This is important: the phantom-flag detector must continue working against existing-in-canonical-store phantoms even after the source defect is fixed.

T5, T6, and T7 use `monkeypatch.setattr` to substitute fixture-returning `completion_ready` / `verified_work_items` functions on the imported scanner module. T10 uses `monkeypatch.setitem(sys.modules, ...)` with a sentinel object that raises `AssertionError` on any attribute access, so any base-path access to the scanner surfaces immediately as a test failure.

### Test execution evidence

```text
$ python -m pytest platform_tests/scripts/test_cli_backlog_status.py -q
..........                                                               [100%]
10 passed in 2.74s

$ python -m pytest platform_tests/scripts/test_check_harness_parity.py -q
......                                                                   [100%]
6 passed in 0.53s
```

All 10 tests in the spec-derived verification plan PASS. The harness-parity companion check PASSES with no regressions. (Run after the SIM108 ruff cleanup landed.)

### Ruff evidence

```text
$ python -m ruff check groundtruth-kb/src/groundtruth_kb/cli_backlog_status.py platform_tests/scripts/test_cli_backlog_status.py
All checks passed!
```

Ruff clean on both new files. (The `cli.py` file is not lint-clean in its entirety because it carries unrelated parallel-session edits in the working tree; my added hunk follows the existing module's style and was not flagged.)

### Live smoke-test evidence (read-only against canonical groundtruth.db)

```text
$ python -m groundtruth_kb backlog status --project PROJECT-GTKB-RELIABILITY-FIXES --json
{
  "projects": [
    {
      "doubled_prefix_flag": false,
      "id": "PROJECT-GTKB-RELIABILITY-FIXES",
      "name": "GTKB-RELIABILITY-FIXES",
      "resolution_status_breakdown": {
        "open": 41,
        "resolved": 10,
        "retired": 1
      },
      "status": "active",
      "work_item_count": 52
    }
  ],
  "summary": {
    "doubled_prefix_project_count": 0,
    "project_count": 1,
    "total_active_memberships": 52
  }
}

$ python -m groundtruth_kb backlog status --json | <summary-extract>
projects=157  doubled=10  memberships=491
```

The 10 doubled-prefix projects surfaced by the unfiltered scan match the owner-stated phantom inventory ("phantom PROJECT-PROJECT-* reconciliation - 10 projects, WI-3355") exactly. This is empirical confirmation that the command correctly identifies the phantom drift the deferred reconciliation work targets.

## Specification-Derived Verification (executed)

Per DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001, every row of the GO'd proposal's 10-acceptance-criterion matrix maps to executable evidence:

| # | Acceptance criterion | Test | Result |
|---|---|---|---|
| 1 | `gt backlog status` exits 0, emits projects with resolution_status_breakdown | `test_status_base_lists_projects_with_breakdown` | PASS |
| 2 | `--project <PID>` filters to one project | `test_status_project_filter` | PASS |
| 3 | `--json` output is parseable and schema-stable | `test_status_json_parseable_and_keys` | PASS |
| 4 | `--with-orphans` surfaces a membership-less WI | `test_status_orphans_surfaced` | PASS |
| 5 | `--with-retire-ready` surfaces a completion-ready authorization via the canonical scanner module | `test_status_retire_ready_uses_scanner` | PASS |
| 6 | `--with-verified-coverage` annotates per-WI coverage via the canonical scanner module | `test_status_verified_coverage_annotation` | PASS |
| 7 | retire-ready / verified-coverage output carries `scanner_caveat` naming the CANONICAL thread `gtkb-project-completion-scanner-addressing-thread-fix` (canonical slug present; withdrawn `-implementation` slug absent) | `test_status_scanner_caveat_present_when_flags_set` | PASS |
| 8 | Read-only: db file byte-identical before/after | `test_status_makes_no_db_writes` | PASS |
| 9 | `doubled_prefix_flag` set for a `PROJECT-PROJECT-*` project | `test_status_flags_doubled_prefix_project` | PASS |
| 10 | Base output (no flags) imports no scanner module | `test_status_base_has_no_scanner_dependency` | PASS |

Verification commands executed (per GO Conditions For Implementation Report):

```text
python -m pytest platform_tests/scripts/test_cli_backlog_status.py -q
python -m pytest platform_tests/scripts/test_check_harness_parity.py -q
```

Both observed results: PASS (10/10 and 6/6 respectively).

GO Condition restatements:

- `gt backlog status performs no MemBase writes`: confirmed by test 8 (db file hash byte-identical before/after) AND by the read-only design of `build_backlog_status` (KnowledgeDB opened, only `list_*` / `get_*` calls used, connection closed in `finally`).
- `base output has no scanner dependency`: confirmed by test 10 (sentinel module sys.modules patch raises on any scanner attribute access; base path completes without triggering it).

## Acceptance Criteria Satisfaction

- [x] IP-1 landed; `cli_backlog_status.py` created per proposal Design.
- [x] IP-2 landed; one `@backlog.command("status")` registration in `cli.py`.
- [x] IP-3 landed; 10 tests PASS and the harness-parity companion suite PASSES with no regression.
- [x] `ruff check` is clean on both new files.
- [x] Mandatory applicability and clause preflights PASS for this bridge id (carried forward; both exited 0 on the GO at -004).
- [x] After implementation, live smoke-test confirms the command reports the canonical store's actual state and correctly identifies 10 doubled-prefix projects (matching the owner-stated phantom inventory).

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/cli_backlog_status.py` (new file; 211 lines).
- `groundtruth-kb/src/groundtruth_kb/cli.py` (modified; +83 lines for one `@backlog.command("status")` registration block; no existing line altered).
- `platform_tests/scripts/test_cli_backlog_status.py` (new file; 10 tests, ~395 lines).

Mixed-owner working-tree note: `cli.py` also carries unrelated edits from parallel-session work (new imports for `cli_approval_packet`, `cli_bridge_propose`, `hygiene`; a new `@main.group("hygiene")` block). The commit for this implementation will stage ONLY the `@backlog.command("status")` block in `cli.py` plus the two new files; parallel-session changes remain in the working tree for their owning thread(s) to commit separately. Inspect-staged-index discipline applies at commit time.

## Owner Decisions / Input

This implementation proceeded on the durable owner-decision evidence cited in the GO'd proposal (-003):

- DECISION-0758 (this session): "start the triage" - AskUserQuestion approval.
- Triage scope choice (AUQ): "Implementation gaps (Recommended)" - AskUserQuestion approval.
- Gap 5 filing choice (AUQ): "File slice-2 scoping now (Recommended)" - AskUserQuestion approval.
- Proceed signal: owner replied "go" after the Codex GO at scoping-002, authorizing the implementation proposal.
- Standing pre-approval: PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-DETERMINISTIC-SERVICES-PARALLEL-BATCH-GT-BRIDGE-PROPOSE-CLI (active; covers WI-3262).

No new blocking owner decision was required for this verification round. The work item appears on the active session's owner-approved implementation list per the prompt directive that opened this session.

## Risk / Open Items

- Scanner-backed flags inherit the in-flight D3+D4 scanner-fix dependency. Mitigation: scanner_caveat field is attached in every flagged-output payload AND only when the corresponding flag is set; base output has zero scanner dependency (test 10).
- Citation re-staleness if the canonical scanner-fix thread's status changes again. Mitigation: the constant `_SCANNER_FIX_LATEST_GO_FILE` is set to the current latest GO at -004; a one-line follow-on can update it when the scanner-fix thread reaches VERIFIED.
- Mixed-owner working tree (~668 dirty files at implementation time): inspect-staged-index discipline applies at commit time.

## Prior Deliberations

- `bridge/gtkb-discoverability-cli-slice-2-scoping-002.md` (Codex GO) - scoping approval and its three implementation notes, all addressed.
- `bridge/gtkb-discoverability-cli-slice-2-implementation-002.md` (Codex NO-GO) - the F1 stale-citation finding that REVISED-1 corrected.
- `bridge/gtkb-discoverability-cli-slice-2-implementation-003.md` (REVISED-1) - the operative proposal this report responds to.
- `bridge/gtkb-discoverability-cli-slice-2-implementation-004.md` (Codex GO) - the verdict authorizing implementation.
- `bridge/gtkb-discoverability-cli-slice-1-008.md` (VERIFIED) - predecessor slice; reused for module + test + single-verb pattern.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE - the principle this command instantiates.
- DELIB-S342-BACKLOG-WORK-ITEMS-CANONICAL-PIVOT - MemBase work_items is the canonical backlog source; this command reads it.
- `bridge/gtkb-project-completion-scanner-addressing-thread-fix-004.md` (canonical scanner-fix thread, GO) - the in-flight D3+D4 fix the corrected `scanner_caveat` references.
- `bridge/gtkb-project-id-prefix-idempotent-fix-004.md` (parallel post-impl report this session) - the source-side idempotent fix; the present CLI surfaces the existing phantom drift the source fix stops producing.

## Loyal Opposition Asks

1. Confirm the implementation matches the GO'd proposal's three-file target_paths and Design (read-only service + single CLI verb + scanner-caveated opt-in flags).
2. Confirm the 10 tests adequately cover the spec-derived verification matrix.
3. Confirm the canonical scanner-fix slug reference is present in `SCANNER_CAVEAT` and the withdrawn `-implementation` duplicate is absent (F1 correction sustained).
4. Confirm the live smoke-test (157 projects, 10 doubled-prefix, 491 memberships) is consistent expected behavior on the canonical store.
5. Confirm VERIFIED is appropriate based on the above evidence.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
