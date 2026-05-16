REVISED

# Implementation Proposal - gt backlog add CLI (WI-3270) - REVISED-1

bridge_kind: implementation_proposal
Document: gtkb-gt-backlog-add-cli
Version: 003
Responds to: bridge/gtkb-gt-backlog-add-cli-002.md
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S353+

Project Authorization: PAUTH-PROJECT-GTKB-BACKLOG-CAPTURE-001-BACKLOG-CAPTURE-COMMAND-APPROVAL-STATE-TAXONOMY
Project: PROJECT-GTKB-BACKLOG-CAPTURE-001
Work Item: WI-3270

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/tests/test_cli_backlog.py"]

This REVISED-1 (`-003`) implements `WI-3270`: a governed `gt backlog add` CLI subcommand for capturing a noticed issue / enhancement opportunity as a MemBase `work_items` row in one invocation, preserving the evidence and provenance the work item requires.

## Revision Notes

This `-003` REVISED-1 addresses every finding in the `-002` NO-GO:

- **F1 (P1) — the CLI omitted WI-3270's required evidence and dry-run fields.** Resolved. The `backlog add` command gains the provenance options that the live `insert_work_item` API already supports: `--source-owner-directive`, `--related-deliberation-ids`, `--related-spec-ids` (persisted to `related_spec_ids_at_creation`), and `--related-bridge-threads`; plus a `--dry-run` flag and an explicit candidate-state default. The verification plan adds tests asserting each evidence field persists and that `--dry-run` mutates nothing. See IP-1, the Candidate-State Default section, and the verification plan.
- **F2 (P1) — the project-membership test could not be satisfied by the proposed implementation.** Resolved. `--project-name` is now **real, immediate, same-connection membership**: after `insert_work_item`, the command resolves the project id from the name (stable-id derivation, matching the existing `gt projects` id convention) and calls `db.link_project_work_item(project_id, work_item_id, ...)` in the same command/process. The membership test asserts visibility on the **same connection** (no DB reopen). The compatibility-backfill `project_name` field is no longer relied on for the membership promise. See IP-1.
- **F3 (P1) — the auto-ID race mitigation was asserted but not specified.** Resolved. The Auto-ID Allocation section specifies the transaction boundary: max-id allocation and the insert run inside a single `BEGIN IMMEDIATE` transaction (acquiring the SQLite reserved write lock before the `MAX(id)` read), with a bounded retry-on-`UNIQUE`-conflict loop as defense in depth. A concurrency regression test exercises two simultaneous `gt backlog add` invocations and asserts two distinct WI ids.
- **F4 (P2) — applicability preflight reported missing advisory specs.** Resolved. `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, and `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` are now cited in `## Specification Links`. Both preflights were re-run on this `-003` content; results are embedded below.

## Claim

Add a `gt backlog add` CLI subcommand. Required options: `--title`, `--origin` (`new|defect|regression|hygiene`), `--component`, `--description`. Evidence/provenance options: `--source-owner-directive`, `--source-deliberation-query`, `--related-deliberation-ids`, `--related-spec-ids`, `--related-bridge-threads`. Other options: `--source-spec-id`, `--priority`, `--project-name`, `--changed-by`, `--dry-run`. The command allocates a `WI-NNNN` id, calls `db.insert_work_item(...)` with a defined candidate-state default, optionally links the WI to a project, and emits the created WI id. `--dry-run` prints the would-create payload and writes nothing.

## In-Root Placement Evidence

All `target_paths` are inside `E:\GT-KB`. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `GOV-STANDING-BACKLOG-001` - source specification; this CLI is the governed-creation surface the standing-backlog spec mandates, and it writes to the authoritative `work_items` table.
- `SPEC-AUQ-POLICY-ENGINE-001` - the CLI is a deterministic surface for backlog capture.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority governing this proposal.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites every relevant governing specification.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the spec-to-test mapping below derives every test from a linked spec.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - artifact-oriented governance baseline; the created work item is a governed artifact and the CLI preserves its provenance.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - durable artifact-graph model; the evidence fields (`source_owner_directive`, `related_deliberation_ids`, `related_spec_ids_at_creation`, `related_bridge_threads`) link the new WI into the artifact graph.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - artifact lifecycle trigger discipline; the command creates the WI at the lifecycle-start candidate state, not a later stage.

## Prior Deliberations

- `DELIB-S350-BATCH2-THREE-PROJECT-AUTHORIZATIONS` - batch-2 owner authorization for `PROJECT-GTKB-BACKLOG-CAPTURE-001` and WI-3270.
- `DELIB-S341-BACKLOG-CONSIDERATION-IMPLEMENTATION-AUQ-DIRECTIVE` - owner decision that future-work candidates flow to MemBase, not `MEMORY.md`, while implementation approval remains separate; this CLI is the MemBase-capture surface that directive implies.
- `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE` - owner directive formalizing the backlog as a DB-backed source of truth with provenance and linkage fields; the evidence options in this revision satisfy that directive.
- `DELIB-1790` / `DELIB-1791` - prior NO-GOs on the `GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH` scoping thread; relevant to backlog source-of-truth and verification strictness.

No retrieved deliberation waives the requirement that a backlog-creation surface preserve the provenance fields the owner directive established.

## Owner Decisions / Input

This proposal is filed under an active project authorization and is authorized by:

- 2026-05-14 UTC, S350+: owner AUQ "Authorize all 3 groups (7 WIs added)" — authorized `PROJECT-GTKB-BACKLOG-CAPTURE-001` including WI-3270. Recorded as `DELIB-S350-BATCH2-THREE-PROJECT-AUTHORIZATIONS`.

No new owner decision is required for this revision; `-003` only widens the CLI surface to match the WI-3270 description and fixes the membership/auto-ID specification.

## Requirement Sufficiency

Existing requirements sufficient. The WI-3270 work-item description — a backlog-capture command defaulting to a review/consideration candidate state, requiring normal evidence fields, preserving the source owner directive and related specs/bridge threads, supporting dry-run output, and emitting the created WI id — plus `GOV-STANDING-BACKLOG-001` and the cited owner directives (`DELIB-S327`, `DELIB-S341`) fully specify the surface. The live `insert_work_item` API already exposes every required provenance field. No new or revised requirement or specification is created.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is a single-WI implementation proposal (WI-3270). It performs no batch resolve, promote, or retire of work items or specifications — the `gt backlog add` command creates exactly one work item per invocation. References to "work item", "backlog", and "standing backlog" describe WI-3270's single-item creation surface. The review-packet inventory is one bridge thread: IP-1 (CLI subcommand) + IP-2 (tests). WI-3270's project membership is recorded under the formal-artifact-approval packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch2-three-project-authorizations.json`.

## Bridge INDEX Maintenance

This proposal keeps `bridge/INDEX.md` as the canonical bridge workflow state. The `-003` REVISED line is inserted under the existing `Document: gtkb-gt-backlog-add-cli` entry; the prior `-001` NEW and `-002` NO-GO lines are preserved unchanged.

## Candidate-State Default (resolves F1)

The live `work_items` schema has no `candidate` value for `resolution_status` (valid values: `open`, `in_progress`, `resolved`, `verified`) and `stage` starts at `created`. The "review/consideration candidate" state WI-3270 calls for is therefore expressed with the existing fields:

- `resolution_status = "open"` — the WI is open work.
- `stage = "created"` — the lifecycle start; the WI is NOT yet `backlogged` / `implementing`. It is a captured candidate awaiting review, not committed work.
- `status_detail = "review-consideration candidate"` — an explicit human-readable marker recording that the WI was captured for review/consideration and has not received implementation approval.

This default is applied automatically by `gt backlog add`; the command does not expose a stage override (capture always lands at the candidate state). This keeps capture distinct from implementation approval per `DELIB-S341-BACKLOG-CONSIDERATION-IMPLEMENTATION-AUQ-DIRECTIVE`.

## Auto-ID Allocation (resolves F3)

`WI-NNNN` ids are allocated as follows:

- The command opens a single transaction with `BEGIN IMMEDIATE` (acquiring the SQLite reserved write lock) BEFORE reading `MAX(CAST(SUBSTR(id, 4) AS INTEGER))` over `work_items` rows whose `id` matches `WI-\d+`. Because the reserved lock is held, no other writer can read the same max and insert the same next id before this transaction commits.
- The `insert_work_item` write occurs inside the same transaction; the transaction commits only after the insert succeeds.
- Defense in depth: if a `UNIQUE` constraint violation on `work_items.id` is nevertheless observed (e.g. a writer outside this code path), the command retries id allocation up to a bounded number of attempts (e.g. 5) before failing with a clear error.
- A concurrency regression test launches two `gt backlog add` invocations concurrently and asserts they produce two distinct WI ids and two persisted rows.

## Proposed Scope

### IP-1: `gt backlog add` subcommand

In `groundtruth-kb/src/groundtruth_kb/cli.py`, add an `add` subcommand to the existing `backlog` Click group (the group already exists at `cli.py` line ~359). Sketch:

```python
@backlog.command("add")
@click.option("--title", required=True)
@click.option("--origin", required=True, type=click.Choice(["new", "defect", "regression", "hygiene"]))
@click.option("--component", required=True)
@click.option("--description", required=True)
@click.option("--source-spec-id", default=None)
@click.option("--source-owner-directive", default=None, help="Verbatim owner directive that prompted this capture.")
@click.option("--source-deliberation-query", default=None, help="DA search query used when capturing.")
@click.option("--related-deliberation-ids", default=None, help="Comma/space-separated DELIB ids.")
@click.option("--related-spec-ids", default=None, help="Related spec ids at creation (-> related_spec_ids_at_creation).")
@click.option("--related-bridge-threads", default=None, help="Related bridge thread slugs.")
@click.option("--priority", default=None)
@click.option("--project-name", default=None, help="Attach the new WI to this project as an immediate member.")
@click.option("--changed-by", default="gt-cli/backlog-add", show_default=True)
@click.option("--dry-run", is_flag=True, help="Print the would-create payload; write nothing.")
@click.pass_context
def backlog_add(ctx, title, origin, component, description, source_spec_id,
                source_owner_directive, source_deliberation_query,
                related_deliberation_ids, related_spec_ids, related_bridge_threads,
                priority, project_name, changed_by, dry_run):
    db = ctx.obj["db"]
    payload = dict(
        title=title, origin=origin, component=component, description=description,
        resolution_status="open", stage="created",
        status_detail="review-consideration candidate",
        source_spec_id=source_spec_id, source_owner_directive=source_owner_directive,
        source_deliberation_query=source_deliberation_query,
        related_deliberation_ids=related_deliberation_ids,
        related_spec_ids_at_creation=related_spec_ids,
        related_bridge_threads=related_bridge_threads, priority=priority,
        changed_by=changed_by, change_reason="Created via gt backlog add",
    )
    if dry_run:
        click.echo(json.dumps({"would_create": payload, "project_name": project_name}, indent=2))
        return
    # BEGIN IMMEDIATE + MAX(id) + insert in one transaction, with bounded retry.
    wi_id = _allocate_and_insert_work_item(db, payload)
    if project_name:
        project_id = _project_id_from_name(project_name)  # stable-id derivation
        db.link_project_work_item(project_id, wi_id, changed_by=changed_by,
                                  change_reason="Linked via gt backlog add")
    click.echo(f"Created: {wi_id}")
```

- `_allocate_and_insert_work_item` implements the `BEGIN IMMEDIATE` transaction + bounded retry described above; it calls `db.insert_work_item(id=wi_id, **payload)`.
- `_project_id_from_name` derives the stable project id from the project name using the same convention the existing `gt projects` commands use (per `cli.py` `--id` "stable id from name" default), so `--project-name` resolves to the project the user means.
- `db.link_project_work_item(project_id, work_item_id, changed_by, change_reason, ...)` creates the membership row immediately on the same connection.
- `--dry-run` returns before any transaction; nothing is written.

### IP-2: Tests

`groundtruth-kb/tests/test_cli_backlog.py` covers minimum-args creation, full-args creation with every evidence field, missing-required-arg failure, monotonic auto-id, same-connection project membership, `--dry-run` no-write, evidence-field persistence, candidate-state default, and the two-invocation concurrency regression.

## Specification-Derived Verification Plan

Every linked specification maps to at least one test in `groundtruth-kb/tests/test_cli_backlog.py`.

| Linked spec | Behavior verified | Test |
|---|---|---|
| `GOV-STANDING-BACKLOG-001` | `gt backlog add` with the minimum required args creates a `work_items` row | `test_backlog_add_minimum_args_creates_wi` |
| `GOV-STANDING-BACKLOG-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | every evidence field (`source_owner_directive`, `source_deliberation_query`, `related_deliberation_ids`, `related_spec_ids_at_creation`, `related_bridge_threads`) is persisted to the created row | `test_backlog_add_persists_all_evidence_fields` |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | the created WI lands at the candidate state (`resolution_status=open`, `stage=created`, `status_detail` marks review-consideration) | `test_backlog_add_candidate_state_default` |
| `GOV-STANDING-BACKLOG-001` | `--dry-run` prints the would-create payload and writes nothing (`work_items` count unchanged) | `test_backlog_add_dry_run_no_write` |
| `SPEC-AUQ-POLICY-ENGINE-001` | a missing required option (`--title`) fails with a clear error | `test_backlog_add_missing_title_fails` |
| `GOV-STANDING-BACKLOG-001` | auto-allocated WI ids are monotonic across sequential invocations | `test_backlog_add_id_increments` |
| `GOV-STANDING-BACKLOG-001` / `GOV-FILE-BRIDGE-AUTHORITY-001` | two concurrent `gt backlog add` invocations produce two distinct WI ids and two persisted rows | `test_backlog_add_concurrent_invocations_distinct_ids` |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `--project-name` creates an immediate, same-connection project membership (`db.link_project_work_item` is called; membership visible without a DB reopen) | `test_backlog_add_project_name_creates_membership_same_connection` |
| `SPEC-AUQ-POLICY-ENGINE-001` | the command emits the created WI id on success | `test_backlog_add_emits_wi_id` |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` / `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | full-args invocation creates a complete, well-formed `work_items` row | `test_backlog_add_full_args_creates_wi` |

Run: `python -m pytest groundtruth-kb/tests/test_cli_backlog.py -v --tb=short`.

Lint: `python -m ruff check groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_cli_backlog.py`.

## Acceptance Criteria

- IP-1 (CLI subcommand), IP-2 (tests) landed; all tests in `test_cli_backlog.py` PASS.
- Both bridge preflights PASS for this proposal (`-003`).
- The command persists every evidence field; a test proves it.
- `--dry-run` writes nothing; a test proves the `work_items` count is unchanged.
- The created WI lands at the candidate state (`resolution_status=open`, `stage=created`, `status_detail` marks review-consideration); a test proves it.
- `--project-name` creates an immediate same-connection membership via `db.link_project_work_item`; a test proves visibility without a DB reopen.
- Two concurrent invocations produce two distinct WI ids; a concurrency regression test proves it.
- `ruff check` is clean on the touched files.

## Risks / Rollback

- Risk: rapid auto-ID generation under concurrent agent use could race. Mitigation: `BEGIN IMMEDIATE` transaction around max-id allocation + insert, plus a bounded retry-on-`UNIQUE`-conflict loop; covered by a concurrency regression test.
- Risk: `--project-name` referencing a non-existent project. Mitigation: `_project_id_from_name` derives the stable id; if the project does not exist, `link_project_work_item` surfaces the error and the command reports it (the WI itself is already created — the failure is on the optional membership link, reported clearly).
- Risk: a wide option surface invites misuse. Mitigation: only `--title`, `--origin`, `--component`, `--description` are required; evidence options are optional but recommended; `--dry-run` lets the author preview before writing.
- Rollback: remove the `add` subcommand registration from the `backlog` group and the two helper functions. No existing surface is modified.

## Recommended Commit Type

`feat` - a new `gt backlog add` CLI subcommand plus tests; a new backlog-capture capability with no behavior change to existing surfaces.

## Applicability Preflight

Command: `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-gt-backlog-add-cli`

- packet_hash: `sha256:0f4bbaa5c666eaad02ec2375331b36868e1c39a2086d266062a55c9e15d15b6c`
- bridge_document_name: `gtkb-gt-backlog-add-cli`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-gt-backlog-add-cli-003.md`
- operative_file: `bridge/gtkb-gt-backlog-add-cli-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

Command: `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-gt-backlog-add-cli`

- Bridge id: `gtkb-gt-backlog-add-cli`
- Operative file: `bridge\gtkb-gt-backlog-add-cli-003.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory (default invocation); exit code `0`

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |
