NEW
::init gtkb lo
::open build

# Implementation Proposal — GFR Slice C: CLI affordances

bridge_kind: prime_proposal
Document: gtkb-gfr-slice-c-cli-affordances
Version: 001
Date: 2026-07-21 UTC
author_identity: prime-builder/goose
author_harness_id: G
author_session_context_id: G-2026-07-21T08-15-00Z
author_model: GLM-5.2
author_model_version: GLM-5.2-2026
author_model_configuration: standard

Project Authorization: PAUTH-GFR-PROGRAM-20260721
Project: PROJECT-GTKB-GOVERNANCE-FRICTION-REDUCTION
Work Item: WI-5645

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/cli_backlog_add_work_item.py", "platform_tests/scripts/test_cli_backlog_list_phases.py", "platform_tests/scripts/test_cli_projects_authorizations_covers_path.py", "platform_tests/scripts/test_cli_backlog_add_work_item_project_flag.py"]

Implementation proposal for governance friction reduction — Slice C (CLI affordances).

## Claim

Slice C of the Governance Friction Reduction program (per GO'd advisory `bridge/gtkb-governance-friction-reduction-002.md`) eliminates three CLI discoverability gaps that caused 10+ failed invocations in the advisory session. Each finding surfaces data that currently requires a database dump or help-text parsing to discover. The fix is to add convenience commands and flags — **no existing gate is weakened**.

This slice implements three findings:

1. **Finding 1.4 — Expose valid test-plan-phase values**: The advisory documented burning 10+ tool calls discovering valid `PHASE-001`…`PHASE-016` values through `projects list`, help output, and a direct sqlite query. The fix adds a `gt backlog list-phases` command that queries `test_plan_phases` and prints the table, eliminating the need for a DB dump.

2. **Finding 4.2 — PAUTH covers-path lookup**: The advisory documented that finding which PAUTH covers a target path required running `projects authorizations <id>` and reading the envelope manually. The fix adds a `--covers-path <path>` flag to `gt projects authorizations` that filters the output to authorizations whose `allowed_mutation_classes` and target classification match the given path.

3. **Finding 2.6 — Atomic WI+project creation**: The advisory documented that `add-work-item` then `projects add-item` is two commands with two failure surfaces. The fix adds a `--project` flag to `gt backlog add-work-item` that links the newly created work item to the specified project in the same invocation, making WI creation atomic. LO note N4 verified: `gt projects add-item` takes positional `PROJECT_ID` + `WORK_ITEM_ID` (no `--work-item` flag), so adding `--project` to `add-work-item` is the correct seam.

## Requirement Sufficiency

Existing requirements are sufficient for this slice. The advisory's findings are all CLI convenience additions — no new specifications or requirement changes are needed.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`:
- `groundtruth-kb/src/groundtruth_kb/cli.py` ✅
- `groundtruth-kb/src/groundtruth_kb/cli_backlog_add_work_item.py` ✅
- `platform_tests/scripts/test_cli_backlog_list_phases.py` ✅ (new test file)
- `platform_tests/scripts/test_cli_projects_authorizations_covers_path.py` ✅ (new test file)
- `platform_tests/scripts/test_cli_backlog_add_work_item_project_flag.py` ✅ (new test file)

## Specification Links

- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites all relevant governing specifications.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — defines who may author which status tokens; this proposal is authored by Prime Builder.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — these CLI affordances surface data that was previously discoverable only by DB dumps.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification requires spec-to-test mapping; TEST-11690 covers new CLI commands.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — this proposal includes the three mandatory header lines.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all target paths are within the GT-KB root boundary.
- `GOV-STANDING-BACKLOG-001` — the GFR program was added via WIs WI-5643–WI-5646 under formal-artifact-approval DELIB-202667078.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — CLI commands convert informal DB-dump discovery into durable, reproducible interfaces.
- `GOV-12` — work-item test-spec requirement (relevant to `--project` flag atomicity).
- `GOV-13` — test-plan-phase assignment (relevant to `list-phases` command).

## Prior Deliberations

- `DELIB-202667078` — Owner approval: Governance Friction Reduction program. Owner approved the 4-slice program.
- `DELIB-20263490` — Loyal Opposition Progress & Verification Report — Terminology & Bridge Reconciliation.

### Helper-suggested candidates

_No prior deliberations beyond those listed above._

## Owner Decisions / Input

- `DELIB-202667078` (AUQ GFR-PAUTH-001) — Owner answer: "1 - Yes, proceed".
- `PAUTH-GFR-PROGRAM-20260721` — Active project authorization covering WI-5643–WI-5646.

## Cross-Harness Disposition

This proposal touches only `groundtruth-kb/src/` and `platform_tests/` files — no harness-surface files. No adapter regeneration is required.

| Harness | Surface | Parity Status | Disposition |
|---|---|---|---|
| All harnesses | `groundtruth-kb/src/` (platform code) | N/A — platform code | Changes are to platform CLI, not harness-surface files. |

**No typed waiver required.** No downstream adapter regeneration needed.

## Proposed Scope

### Finding 1.4 — `gt backlog list-phases` command

**File:** `groundtruth-kb/src/groundtruth_kb/cli.py`

Add a new `list-phases` subcommand to the `backlog` command group:

```python
@backlog.command("list-phases")
@click.option("--json", "json_output", is_flag=True, help="Emit machine-readable JSON.")
@click.pass_context
def backlog_list_phases(ctx, json_output):
    """List valid test-plan phases (GOV-13)."""
    config = _resolve_config(ctx)
    db = KnowledgeDB(config.db_path)
    rows = db._get_conn().execute(
        "SELECT phase_id, phase_name, status FROM test_plan_phases ORDER BY phase_id"
    ).fetchall()
    if json_output:
        click.echo(json.dumps([{"phase_id": r[0], "phase_name": r[1], "status": r[2]} for r in rows], indent=2))
        return
    for row in rows:
        click.echo(f"{row[0]}  {row[1]}  ({row[2]})")
```

**Key design:** This is a read-only query — no mutations. It surfaces exactly the data that the advisory session spent 10+ calls discovering.

### Finding 4.2 — `--covers-path` flag on `projects authorizations`

**File:** `groundtruth-kb/src/groundtruth_kb/cli.py`

Add a `--covers-path` option to the existing `projects authorizations` command. When supplied, the command:
1. Loads the active PAUTH rows as before
2. For each PAUTH, classifies the `--covers-path` value using `classify_target` from `project_authorization_operation_time`
3. Checks if the resulting `mutation_class` is in the PAUTH's `allowed_mutation_classes`
4. Filters the output to only matching PAUTHs

```python
@click.option("--covers-path", default=None, help="Filter to authorizations covering this target path.")
```

When `--covers-path` is set and no PAUTHs match, print a clear message: "No active project authorization covers path: <path>".

**Key design:** This is read-only lookup — it does not grant or create PAUTHs. It directly answers the advisory's "which PAUTH covers this target" question.

### Finding 2.6 — `--project` flag on `add-work-item`

**File:** `groundtruth-kb/src/groundtruth_kb/cli_backlog_add_work_item.py`

Add a `project_id: str | None` field to `AddWorkItemRequest`. After successful WI+test+phase creation, if `project_id` is set, perform the same DB write that `gt projects add-item` does (insert a `project_members` row linking the new WI to the project).

**File:** `groundtruth-kb/src/groundtruth_kb/cli.py`

Add `--project` option to `backlog_add_work_item`:

```python
@click.option("--project", "project_id", default=None, help="Project id to link the new work item to (atomic).")
```

Pass `project_id` through to `AddWorkItemRequest`.

**Key design (LO note N4):** Verified that `gt projects add-item` takes positional `PROJECT_ID` + `WORK_ITEM_ID` (no `--work-item` flag). Adding `--project` to `add-work-item` is the correct seam — it wraps the same `project_members` write, just ordered atomically with WI creation. If the project linkage fails, the WI creation is still committed (the WI exists), but the error is reported — this is fail-open for WI creation, fail-loud for linkage, matching the advisory's "safe because it is the same two DB writes, just ordered" recommendation.

### Test additions

**File:** `platform_tests/scripts/test_cli_backlog_list_phases.py` (new)

Test that `list-phases` command:
1. Returns all phases from the test_plan_phases table
2. `--json` output is valid JSON with `phase_id`, `phase_name`, `status` fields
3. Phases are sorted by phase_id

**File:** `platform_tests/scripts/test_cli_projects_authorizations_covers_path.py` (new)

Test that `--covers-path` flag:
1. Filters to only PAUTHs whose `allowed_mutation_classes` cover the path's mutation class
2. Returns empty list (with clear message) when no PAUTH covers the path
3. Works with both `--json` and default output

**File:** `platform_tests/scripts/test_cli_backlog_add_work_item_project_flag.py` (new)

Test that `--project` flag:
1. Creates a `project_members` row linking the new WI to the specified project
2. Without `--project`, no project membership is created (backward compat)
3. Reports an error (but WI still exists) when the project id is invalid

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "CLI convenience additions (new subcommands and flags)",
  "provenance": "GO'd advisory gtkb-governance-friction-reduction-002; owner decision DELIB-202667078",
  "canonical_authority": "cli.py; cli_backlog_add_work_item.py",
  "primary_route": "additive: new subcommand, new flag, new test files",
  "before_behavior": "agents discover valid phases, PAUTH coverage, and project linkage through DB dumps and multi-step commands",
  "after_behavior": "agents use gt backlog list-phases, gt projects authorizations --covers-path, and gt backlog add-work-item --project",
  "self_descriptive_naming": "list-phases, --covers-path, --project — all self-descriptive",
  "obsolete_guidance_disposition": "no existing guidance is superseded; all changes are additive",
  "history_preservation": "no existing artifacts are deleted or rewritten",
  "baseline": "existing tests + ruff check + ruff format --check",
  "expected_result": "all tests pass, ruff clean, new CLI commands work",
  "rollback": "revert the commit; no data migration or state change",
  "hard_invariants": "GOV-12/GOV-13 chain intact; PAUTH grant is not automated; existing commands unchanged",
  "fail_closed_conditions": "list-phases is read-only; --covers-path is read-only; --project fails loud on linkage error",
  "essential_context_preservation": "all changes are durable code artifacts (CLI, tests)"
}
```

## Specification-Derived Verification Plan

| Specification | Test or Verification Command | Executed | Result |
|---|---|---|---|
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Visual inspection of spec links | yes | (pending) |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python -m pytest platform_tests/scripts/test_cli_backlog_list_phases.py platform_tests/scripts/test_cli_projects_authorizations_covers_path.py platform_tests/scripts/test_cli_backlog_add_work_item_project_flag.py -q --tb=short` | (pending) | (pending) |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Verify proposal author identity | yes | (pending) |
| `GOV-12` | Verify TEST-11690 exists and is linked to WI-5645 | yes | (pending) |
| `GOV-13` | Verify TEST-11690 is assigned to PHASE-001 | yes | (pending) |

## Acceptance Criteria

1. `gt backlog list-phases` prints all valid test-plan phases with phase_id, phase_name, and status.
2. `gt backlog list-phases --json` emits valid JSON.
3. `gt projects authorizations <PROJECT_ID> --covers-path <path>` filters to PAUTHs covering the path's mutation class.
4. `gt projects authorizations <PROJECT_ID> --covers-path <path> --json` emits valid JSON.
5. `gt backlog add-work-item --project <PROJECT_ID> ...` creates a project_members row linking the new WI.
6. `gt backlog add-work-item` without `--project` is backward-compatible (no membership created).
7. New test files pass.
8. All existing tests pass.
9. `ruff check` and `ruff format --check` pass on modified files.
10. No existing governance gate is weakened or removed.

## Risks / Rollback

- **Risk: `list-phases` column name drift** — if the `test_plan_phases` schema changes, the query may fail. Mitigation: use explicit column names and fail gracefully.
- **Risk: `--covers-path` classifier mismatch** — the `classify_target` function may classify a path differently than the PAUTH evaluator. Mitigation: use the same `classify_target` and `normalize_mutation_class` functions, ensuring consistency.
- **Risk: `--project` atomicity** — if the project linkage fails after WI creation, the WI exists without a project link. Mitigation: report the error clearly; the WI is still usable, and `gt projects add-item` can be run manually.
- **Rollback:** Revert the commit. No data migration. All changes are additive CLI code and tests.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/cli.py` — add `list-phases` subcommand, `--covers-path` flag, `--project` flag
- `groundtruth-kb/src/groundtruth_kb/cli_backlog_add_work_item.py` — add `project_id` to `AddWorkItemRequest`, project linkage after WI creation
- `platform_tests/scripts/test_cli_backlog_list_phases.py` — new test file
- `platform_tests/scripts/test_cli_projects_authorizations_covers_path.py` — new test file
- `platform_tests/scripts/test_cli_backlog_add_work_item_project_flag.py` — new test file

## Recommended Commit Type

`feat`

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
