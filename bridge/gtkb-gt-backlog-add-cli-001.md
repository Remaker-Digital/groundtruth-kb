NEW

# Implementation Proposal - gt backlog add CLI (WI-3270)

bridge_kind: prime_proposal
Document: gtkb-gt-backlog-add-cli
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350

Project Authorization: PAUTH-PROJECT-GTKB-BACKLOG-CAPTURE-001-BACKLOG-CAPTURE-COMMAND-APPROVAL-STATE-TAXONOMY
Project: PROJECT-GTKB-BACKLOG-CAPTURE-001
Work Item: WI-3270

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/tests/test_cli_backlog.py"]

This NEW proposal implements a governed `gt backlog add` CLI subcommand for capturing noticed issues / enhancement opportunities as MemBase work_items in a single one-shot invocation. Currently agents capture future work via prose in feedback memory files; this surface lets them write directly to the authoritative `work_items` table.

## Claim

Add `gt backlog add` CLI accepting `--title`, `--origin`, `--component`, `--description`, optional `--source-spec-id`, `--priority`, `--project-name`. Wraps `db.insert_work_item()` with `resolution_status='open'`, `stage='created'`. Generates `WI-NNNN` ID from highest existing.

## In-Root Placement Evidence

All target paths in-root. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `GOV-STANDING-BACKLOG-001` - source spec; this CLI is the governed-creation surface the spec mandates.
- `SPEC-AUQ-POLICY-ENGINE-001` - new CLI surface; non-mutating subcommand registration.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage cited.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping.
- `DELIB-S350-BATCH2-THREE-PROJECT-AUTHORIZATIONS` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S350-BATCH2-THREE-PROJECT-AUTHORIZATIONS` - batch-2 authorization.

## Owner Decisions / Input

- 2026-05-14 UTC, S350+: owner AUQ "Authorize all 3 groups (7 WIs added)".

## Requirement Sufficiency

Existing requirements sufficient. WI-3270 description + GOV-STANDING-BACKLOG-001 fully specify the surface.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. WI-3270 is a single-WI feature; member of PROJECT-GTKB-BACKLOG-CAPTURE-001 per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch2-three-project-authorizations.json`. Review-packet inventory: IP-1 (CLI) + IP-2 (tests) single thread.

## Bridge INDEX Update Evidence

NEW filed at `bridge/gtkb-gt-backlog-add-cli-001.md`; new top entry prepended.

## Proposed Scope

### IP-1: CLI subcommand

In `groundtruth-kb/src/groundtruth_kb/cli.py`, add `backlog` command group with `add` subcommand. Click-style:

```python
@backlog.command("add")
@click.option("--title", required=True)
@click.option("--origin", required=True, type=click.Choice(["new", "defect", "regression", "hygiene"]))
@click.option("--component", required=True)
@click.option("--description", required=True)
@click.option("--source-spec-id", default=None)
@click.option("--priority", default=None)
@click.option("--project-name", default=None)
def backlog_add(title, origin, component, description, source_spec_id, priority, project_name):
    wi_id = _next_wi_id(db)  # WI-NNNN auto-increment
    db.insert_work_item(id=wi_id, title=title, origin=origin, component=component,
                       resolution_status="open", changed_by="gt-cli/backlog-add",
                       change_reason="Created via gt backlog add",
                       description=description, source_spec_id=source_spec_id,
                       priority=priority, project_name=project_name)
    click.echo(f"Created: {wi_id}")
```

`_next_wi_id` queries max `CAST(SUBSTR(id, 4) AS INTEGER)` from work_items where id matches `WI-\d+`.

### IP-2: Tests + spec promotion

Tests + promote `GOV-STANDING-BACKLOG-001` source-spec status? — GOV is already implemented; no promotion needed for this WI.

## Specification-Derived Verification Plan

| Behavior | Test |
|---|---|
| Add with minimum args | `test_backlog_add_minimum_args_creates_wi` |
| Add with all args | `test_backlog_add_full_args_creates_wi` |
| Missing required arg fails | `test_backlog_add_missing_title_fails` |
| Auto-ID is monotonic | `test_backlog_add_id_increments` |
| --project-name attaches via membership | `test_backlog_add_project_name_creates_membership` |
| Output format | `test_backlog_add_emits_wi_id` |

Run: `python -m pytest groundtruth-kb/tests/test_cli_backlog.py -v`.

## Acceptance Criteria

- IP-1 CLI landed; 6 tests PASS.
- Both preflights PASS.

## Risks / Rollback

- Risk: rapid auto-ID generation under concurrent invocation could race. Mitigation: SQLite txn around max-id + insert.
- Rollback: remove subcommand registration.

## Recommended Commit Type

`feat` - new CLI surface. ~50 LOC.
