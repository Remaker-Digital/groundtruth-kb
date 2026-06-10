REVISED

# Implementation Proposal - gt backlog add CLI (WI-3270) - REVISED-2

bridge_kind: prime_proposal
Document: gtkb-gt-backlog-add-cli
Version: 005
Responds to: bridge/gtkb-gt-backlog-add-cli-004.md
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S353+

Project Authorization: PAUTH-PROJECT-GTKB-BACKLOG-CAPTURE-001-BACKLOG-CAPTURE-COMMAND-APPROVAL-STATE-TAXONOMY
Project: PROJECT-GTKB-BACKLOG-CAPTURE-001
Work Item: WI-3270

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/tests/test_cli_backlog.py"]

This REVISED-2 (`-005`) implements `WI-3270`: a governed `gt backlog add` CLI subcommand for capturing a noticed issue / enhancement opportunity as a MemBase `work_items` row in one invocation, preserving the evidence and provenance the work item requires.

## Revision Notes

This `-005` REVISED-2 addresses every finding in the `-004` NO-GO. The prior `-003` REVISED-1 fixes for the `-002` findings (dry-run, same-connection project membership, `BEGIN IMMEDIATE` auto-ID transaction, advisory-spec citation) are carried forward unchanged.

- **F1 (P1) — evidence/provenance fields were still optional despite WI-3270 requiring normal evidence.** Resolved. The `-003` revision exposed the provenance options but left them optional ("evidence options are optional but recommended"). The live WI-3270 row says the command must "require the normal evidence fields, preserve source owner directive and related specs/bridge threads." `-005` makes the evidence fields **enforced at CLI validation time**, not merely accepted:
  - `--source-owner-directive` is **required**.
  - A source-context field is **required**: at least one of `--source-deliberation-query` or `--related-deliberation-ids` must be supplied.
  - A related-artifacts field is **required**: at least one of `--related-spec-ids` or `--related-bridge-threads` must be supplied, OR the explicit escape valve `--no-related-artifacts "<reason>"` must be supplied (which persists the stated reason into `status_detail` so the no-related-artifacts decision is itself recorded evidence).
  - Validation runs before any DB write and before `--dry-run` payload emission; a missing required evidence field fails the command with a clear error.
  See the rewritten Evidence Field Enforcement section, the updated IP-1 sketch, and the verification plan.
- **F1 test correction — the minimum-args test proved evidence-free creation succeeds.** Resolved. The old `test_backlog_add_minimum_args_creates_wi` is removed. It is replaced by (a) `test_backlog_add_required_evidence_creates_wi`, which supplies the now-required evidence fields and proves a well-formed row is created, and (b) `test_backlog_add_missing_source_owner_directive_fails`, `test_backlog_add_missing_source_context_fails`, and `test_backlog_add_missing_related_artifacts_fails`, which prove the command refuses to create a row when a required evidence field is absent. `test_backlog_add_persists_all_evidence_fields` continues to prove every evidence field reaches the persisted row.
- **F2 (P1) — standing-backlog DB authority and schema specs were missing from Specification Links.** Resolved. `ADR-STANDING-BACKLOG-DB-AUTHORITY-001` (v3; the spec that makes `current_work_items` backed by append-only `work_items` the standing-backlog authority) and `DCL-STANDING-BACKLOG-DB-SCHEMA-001` (v3; the spec that names the backlog evidence columns this CLI writes) are now cited in `## Specification Links`. The verification plan adds two spec-to-test rows: `test_backlog_add_wi_visible_via_current_work_items` proves the created WI is visible through the canonical `current_work_items` read path (the same path `gt backlog list` uses), and `test_backlog_add_evidence_fields_use_schema_field_names` proves the evidence values are persisted under the exact DCL-named columns (`source_owner_directive`, `source_deliberation_query`, `related_deliberation_ids`, `related_spec_ids_at_creation`, `related_bridge_threads`).

## Claim

Add a `gt backlog add` CLI subcommand. Required options: `--title`, `--origin` (`new|defect|regression|hygiene`), `--component`, `--description`, `--source-owner-directive`, plus a source-context field (`--source-deliberation-query` or `--related-deliberation-ids`) and a related-artifacts field (`--related-spec-ids` or `--related-bridge-threads`, or the explicit `--no-related-artifacts "<reason>"` escape valve). Other options: `--source-spec-id`, `--priority`, `--project-name`, `--changed-by`, `--dry-run`. The command validates the required evidence set, allocates a `WI-NNNN` id, calls `db.insert_work_item(...)` with a defined candidate-state default, optionally links the WI to a project, and emits the created WI id. `--dry-run` validates the evidence set, prints the would-create payload, and writes nothing.

## In-Root Placement Evidence

All `target_paths` are inside `E:\GT-KB`. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `GOV-STANDING-BACKLOG-001` - source specification; this CLI is the governed-creation surface the standing-backlog spec mandates, and it writes to the authoritative `work_items` table.
- `ADR-STANDING-BACKLOG-DB-AUTHORITY-001` - v3; establishes `current_work_items` backed by append-only `work_items` as the standing-backlog authority. This CLI is a write surface for that authority; the verification plan proves the created WI is visible through `current_work_items`.
- `DCL-STANDING-BACKLOG-DB-SCHEMA-001` - v3; names the backlog schema columns (`source_owner_directive`, `source_deliberation_query`, `related_deliberation_ids`, `related_spec_ids_at_creation`, `related_bridge_threads`) this CLI persists. The verification plan proves the evidence values land under those exact field names.
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
- `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE` - owner directive formalizing the backlog as a DB-backed source of truth with provenance and linkage fields; the enforced evidence options in this revision satisfy that directive.
- `DELIB-1790` / `DELIB-1791` - prior NO-GOs on the `GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH` scoping thread; relevant to backlog source-of-truth and verification strictness.

No retrieved deliberation waives the requirement that a backlog-creation surface preserve the provenance fields the owner directive established.

## Owner Decisions / Input

This proposal is filed under an active project authorization and is authorized by:

- 2026-05-14 UTC, S350+: owner AUQ "Authorize all 3 groups (7 WIs added)" — authorized `PROJECT-GTKB-BACKLOG-CAPTURE-001` including WI-3270. Recorded as `DELIB-S350-BATCH2-THREE-PROJECT-AUTHORIZATIONS`.

No new owner decision is required for this revision; `-005` only tightens the CLI surface so the WI-3270 evidence requirement is enforced rather than optional, and adds the standing-backlog DB authority/schema specifications.

## Requirement Sufficiency

Existing requirements sufficient. The WI-3270 work-item description — a backlog-capture command defaulting to a review/consideration candidate state, **requiring the normal evidence fields**, preserving the source owner directive and related specs/bridge threads, supporting dry-run output, and emitting the created WI id — plus `GOV-STANDING-BACKLOG-001`, `ADR-STANDING-BACKLOG-DB-AUTHORITY-001`, `DCL-STANDING-BACKLOG-DB-SCHEMA-001`, and the cited owner directives (`DELIB-S327`, `DELIB-S341`) fully specify the surface. The live `insert_work_item` API already exposes every required provenance field. No new or revised requirement or specification is created.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is a single-WI implementation proposal (WI-3270). It performs no batch resolve, promote, or retire of work items or specifications — the `gt backlog add` command creates exactly one work item per invocation. References to "work item", "backlog", and "standing backlog" describe WI-3270's single-item creation surface. The review-packet inventory is one bridge thread: IP-1 (CLI subcommand) + IP-2 (tests). WI-3270's project membership is recorded under the formal-artifact-approval packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch2-three-project-authorizations.json`.

## Bridge INDEX Maintenance

This proposal keeps `bridge/INDEX.md` as the canonical bridge workflow state. The `-005` REVISED line is inserted under the existing `Document: gtkb-gt-backlog-add-cli` entry; the prior `-001` NEW, `-002` NO-GO, `-003` REVISED, and `-004` NO-GO lines are preserved unchanged.

## Evidence Field Enforcement (resolves F1)

WI-3270 requires the normal evidence fields. The `-003` revision exposed the provenance option names but left them optional; `-005` enforces them at CLI validation time. The enforcement is implemented as a `_validate_backlog_evidence(...)` precheck that runs before any DB write and before the `--dry-run` payload print:

- **Source owner directive — required.** `--source-owner-directive` must be a non-empty string. This is the verbatim owner directive that prompted the capture; without it a reviewer cannot reconstruct the "why".
- **Source context — required (one-of).** At least one of `--source-deliberation-query` (the DA search query used at capture time) or `--related-deliberation-ids` (one or more `DELIB-` ids) must be supplied. This records how the capture was situated against prior decisions.
- **Related artifacts — required (one-of, with explicit escape valve).** At least one of `--related-spec-ids` or `--related-bridge-threads` must be supplied. When a capture genuinely has no related specs or bridge threads, the author must pass `--no-related-artifacts "<reason>"`; the stated reason is appended to `status_detail` so the no-related-artifacts decision is itself recorded as evidence. `--no-related-artifacts` is mutually exclusive with `--related-spec-ids` / `--related-bridge-threads`.

If any required evidence field is missing, the command exits non-zero with a message naming the missing field and (for the one-of groups) the acceptable alternatives. The escape valve prevents the enforcement from blocking genuinely-novel captures while still requiring the author to record an explicit reason rather than silently omitting evidence.

## Candidate-State Default (carried forward from -003; resolves -002 F1)

The live `work_items` schema has no `candidate` value for `resolution_status` (valid values: `open`, `in_progress`, `resolved`, `verified`) and `stage` starts at `created`. The "review/consideration candidate" state WI-3270 calls for is therefore expressed with the existing fields:

- `resolution_status = "open"` — the WI is open work.
- `stage = "created"` — the lifecycle start; the WI is NOT yet `backlogged` / `implementing`. It is a captured candidate awaiting review, not committed work.
- `status_detail = "review-consideration candidate"` — an explicit human-readable marker recording that the WI was captured for review/consideration and has not received implementation approval. When `--no-related-artifacts "<reason>"` is supplied, the reason is appended (e.g. `review-consideration candidate; no related artifacts: <reason>`).

This default is applied automatically by `gt backlog add`; the command does not expose a stage override (capture always lands at the candidate state). This keeps capture distinct from implementation approval per `DELIB-S341-BACKLOG-CONSIDERATION-IMPLEMENTATION-AUQ-DIRECTIVE`.

## Auto-ID Allocation (carried forward from -003; resolves -002 F3)

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
@click.option("--source-owner-directive", required=True, help="Verbatim owner directive that prompted this capture.")
@click.option("--source-deliberation-query", default=None, help="DA search query used when capturing (source context, one-of).")
@click.option("--related-deliberation-ids", default=None, help="Comma/space-separated DELIB ids (source context, one-of).")
@click.option("--related-spec-ids", default=None, help="Related spec ids at creation (-> related_spec_ids_at_creation; related artifacts, one-of).")
@click.option("--related-bridge-threads", default=None, help="Related bridge thread slugs (related artifacts, one-of).")
@click.option("--no-related-artifacts", default=None, help="Explicit reason this capture has no related specs/bridge threads.")
@click.option("--priority", default=None)
@click.option("--project-name", default=None, help="Attach the new WI to this project as an immediate member.")
@click.option("--changed-by", default="gt-cli/backlog-add", show_default=True)
@click.option("--dry-run", is_flag=True, help="Validate evidence, print the would-create payload; write nothing.")
@click.pass_context
def backlog_add(ctx, title, origin, component, description, source_spec_id,
                source_owner_directive, source_deliberation_query,
                related_deliberation_ids, related_spec_ids, related_bridge_threads,
                no_related_artifacts, priority, project_name, changed_by, dry_run):
    db = ctx.obj["db"]
    # F1: evidence enforcement runs before any write and before dry-run print.
    _validate_backlog_evidence(
        source_owner_directive=source_owner_directive,
        source_deliberation_query=source_deliberation_query,
        related_deliberation_ids=related_deliberation_ids,
        related_spec_ids=related_spec_ids,
        related_bridge_threads=related_bridge_threads,
        no_related_artifacts=no_related_artifacts,
    )  # raises click.UsageError naming the missing field on failure
    status_detail = "review-consideration candidate"
    if no_related_artifacts:
        status_detail += f"; no related artifacts: {no_related_artifacts}"
    payload = dict(
        title=title, origin=origin, component=component, description=description,
        resolution_status="open", stage="created", status_detail=status_detail,
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

- `_validate_backlog_evidence` enforces the F1 evidence rules: non-empty `source_owner_directive`; at least one source-context field; at least one related-artifacts field OR `--no-related-artifacts` with a reason; `--no-related-artifacts` mutually exclusive with the related-artifacts fields. It raises `click.UsageError` with a message naming the missing field on failure.
- `_allocate_and_insert_work_item` implements the `BEGIN IMMEDIATE` transaction + bounded retry described above; it calls `db.insert_work_item(id=wi_id, **payload)`.
- `_project_id_from_name` derives the stable project id from the project name using the same convention the existing `gt projects` commands use (per `cli.py` `--id` "stable id from name" default), so `--project-name` resolves to the project the user means.
- `db.link_project_work_item(project_id, work_item_id, changed_by, change_reason, ...)` creates the membership row immediately on the same connection.
- `--dry-run` runs evidence validation, then returns before any transaction; nothing is written.

### IP-2: Tests

`groundtruth-kb/tests/test_cli_backlog.py` covers: required-evidence creation, full-args creation with every evidence field, missing-required-arg failure, the three missing-evidence-field failure cases, the `--no-related-artifacts` escape valve, monotonic auto-id, same-connection project membership, `--dry-run` no-write, evidence-field persistence under DCL-named columns, `current_work_items` read-back, candidate-state default, and the two-invocation concurrency regression.

## Specification-Derived Verification Plan

Every linked specification maps to at least one test in `groundtruth-kb/tests/test_cli_backlog.py`.

| Linked spec | Behavior verified | Test |
|---|---|---|
| `GOV-STANDING-BACKLOG-001` | `gt backlog add` with the required args (including the enforced evidence fields) creates a `work_items` row | `test_backlog_add_required_evidence_creates_wi` |
| `GOV-STANDING-BACKLOG-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | every evidence field is persisted to the created row | `test_backlog_add_persists_all_evidence_fields` |
| `DCL-STANDING-BACKLOG-DB-SCHEMA-001` | the evidence values are persisted under the exact DCL-named columns (`source_owner_directive`, `source_deliberation_query`, `related_deliberation_ids`, `related_spec_ids_at_creation`, `related_bridge_threads`) | `test_backlog_add_evidence_fields_use_schema_field_names` |
| `ADR-STANDING-BACKLOG-DB-AUTHORITY-001` | the created WI is visible through the canonical `current_work_items` read path (the same path `gt backlog list` uses) | `test_backlog_add_wi_visible_via_current_work_items` |
| `GOV-STANDING-BACKLOG-001` | `gt backlog add` refuses to create a row when `--source-owner-directive` is absent | `test_backlog_add_missing_source_owner_directive_fails` |
| `GOV-STANDING-BACKLOG-001` | `gt backlog add` refuses to create a row when no source-context field is supplied | `test_backlog_add_missing_source_context_fails` |
| `GOV-STANDING-BACKLOG-001` | `gt backlog add` refuses to create a row when no related-artifacts field and no `--no-related-artifacts` reason are supplied | `test_backlog_add_missing_related_artifacts_fails` |
| `GOV-STANDING-BACKLOG-001` | `--no-related-artifacts "<reason>"` permits creation and records the reason in `status_detail` | `test_backlog_add_no_related_artifacts_escape_valve` |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | the created WI lands at the candidate state (`resolution_status=open`, `stage=created`, `status_detail` marks review-consideration) | `test_backlog_add_candidate_state_default` |
| `GOV-STANDING-BACKLOG-001` | `--dry-run` validates evidence, prints the would-create payload, and writes nothing (`work_items` count unchanged) | `test_backlog_add_dry_run_no_write` |
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
- Both bridge preflights PASS for this proposal (`-005`).
- The evidence fields are enforced: a test proves the command refuses creation when `--source-owner-directive`, a source-context field, or a related-artifacts field (without `--no-related-artifacts`) is absent.
- The `--no-related-artifacts "<reason>"` escape valve permits creation and records the reason; a test proves it.
- The command persists every evidence field under the DCL-named columns; a test proves it.
- The created WI is visible through `current_work_items`; a test proves it.
- `--dry-run` writes nothing; a test proves the `work_items` count is unchanged.
- The created WI lands at the candidate state (`resolution_status=open`, `stage=created`, `status_detail` marks review-consideration); a test proves it.
- `--project-name` creates an immediate same-connection membership via `db.link_project_work_item`; a test proves visibility without a DB reopen.
- Two concurrent invocations produce two distinct WI ids; a concurrency regression test proves it.
- `ruff check` is clean on the touched files.

## Risks / Rollback

- Risk: rapid auto-ID generation under concurrent agent use could race. Mitigation: `BEGIN IMMEDIATE` transaction around max-id allocation + insert, plus a bounded retry-on-`UNIQUE`-conflict loop; covered by a concurrency regression test.
- Risk: `--project-name` referencing a non-existent project. Mitigation: `_project_id_from_name` derives the stable id; if the project does not exist, `link_project_work_item` surfaces the error and the command reports it (the WI itself is already created — the failure is on the optional membership link, reported clearly).
- Risk: enforcing the evidence fields could block a genuinely-novel capture that has no related specs or bridge threads. Mitigation: the `--no-related-artifacts "<reason>"` escape valve permits such captures while still requiring the author to record an explicit reason, which is itself persisted as evidence in `status_detail`.
- Risk: the wider required-option surface raises the cost of a quick capture. Mitigation: the evidence fields are exactly the provenance WI-3270 and `DELIB-S327` mandate; `--dry-run` lets the author preview the validated payload before writing.
- Rollback: remove the `add` subcommand registration from the `backlog` group and the helper functions (`_validate_backlog_evidence`, `_allocate_and_insert_work_item`, `_project_id_from_name`). No existing surface is modified.

## Recommended Commit Type

`feat` - a new `gt backlog add` CLI subcommand plus tests; a new backlog-capture capability with no behavior change to existing surfaces.

## Applicability Preflight

Command: `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-gt-backlog-add-cli`

- packet_hash: `sha256:c3953e1cd3db9b907062ac6f6c6cc936082b92723dcf08ba150ed16842b049e6`
- bridge_document_name: `gtkb-gt-backlog-add-cli`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-gt-backlog-add-cli-005.md`
- operative_file: `bridge/gtkb-gt-backlog-add-cli-005.md`
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
- Operative file: `bridge\gtkb-gt-backlog-add-cli-005.md`
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
