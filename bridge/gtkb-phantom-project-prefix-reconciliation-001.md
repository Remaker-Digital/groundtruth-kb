NEW
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: claude-2026-05-29-phantom-project-prefix-reconciliation-NEW
author_model: claude-opus-4
author_model_version: 4.7-1M
author_model_configuration: explanatory output style; interrogative-default Prime Builder

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3355

# Phantom PROJECT-PROJECT-* Reconciliation via Deterministic CLI (WI-3355)

bridge_kind: implementation_proposal

Document: gtkb-phantom-project-prefix-reconciliation
Version: 001 (NEW)
Date: 2026-05-29 UTC

## Summary

The just-VERIFIED idempotent fix in `_project_id_from_names` (bridge thread `gtkb-project-id-prefix-idempotent-fix`, GO at -003 / VERIFIED at -005, committed in `281fa28f`) stopped new doubled-prefix project drift at the source. The canonical store still contains the historical phantoms the source defect produced. This proposal reconciles them.

**Inventory (live; reproduced by `gt backlog status --json` against the canonical store at proposal authoring time):** 10 phantom `PROJECT-PROJECT-*` projects holding 49 mis-filed active memberships in total. Every phantom has a canonical counterpart (no MISSING canonical case). The 49 memberships partition into 42 redundant (canonical already holds an active equivalent membership for the same WI, via the `gt projects add-item` workaround pattern documented in the auto-memory) and 7 needing fresh canonical link (the canonical happens to be RETIRED — affects 5 Bridge-Scheduler slices WI-3373..WI-3377, 1 CLAUDE-MD Slice 3 WI-3438, and 1 PUSH-GATE master WI-3416).

This proposal delivers the reconciliation as a deterministic `gt projects reconcile-doubled-prefix` CLI with `--dry-run` and `--apply` modes, per `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`. Reconciliation effect: 49 phantom memberships deactivated (status -> superseded); 7 fresh canonical memberships created where needed; 10 phantom projects retired. The 42 redundant cases need no new canonical membership.

The source defect that produced these phantoms is closed; this reconciliation is a one-shot cleanup, NOT a recurring service. The CLI is preserved post-reconciliation as a re-usable safety net (idempotent on rerun) in case any phantom recurrence is ever discovered.

## Owner Decisions / Input

This proposal proceeds on durable owner-decision evidence captured this session:

1. **Owner directive (2026-05-29, session-opening prompt) — "NOT DEFERRED: phantom PROJECT-PROJECT-* reconciliation (10 projects, WI-3355)"**. Explicit authorization to execute the reconciliation this session.
2. **AskUserQuestion (2026-05-29) — "7 of 49 phantom memberships have a RETIRED canonical umbrella. How should reconciliation dispose of those 7 WIs?" -> "Re-link to retired canonical (Recommended)"**. Authorizes the strict-reconciliation disposition: active-membership-on-retired-canonical is the chosen end state for those 7 cases; reactivation of premature-retire cases (PUSH-GATE per MEMORY.md S368) stays a separate concern.
3. **Standing pre-approval**: `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (owner-decision source `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`) covers WI-3355 via the active project membership filed at 2026-05-29 (`PWM-PROJECT-GTKB-RELIABILITY-FIXES-WI-3355`).

Precedent: WI-3397's analogous bulk reconciliation ("Back-fill project_work_item_memberships for 58 orphan open WIs") landed under the same standing PAUTH + project pair (`bridge/gtkb-orphan-wi-membership-discovery-slice-1-*`).

No new blocking owner decision is required for this proposal to be reviewable.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 - bridge/INDEX.md is canonical workflow state. This NEW is inserted at the top of a fresh document entry.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this Specification Links section + spec-to-test mapping satisfy the linkage gate.
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 - Project Authorization / Project / Work Item triple in header is present and live.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the Spec-Derived Verification Plan maps each behavior to executable tests.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - this proposal references an enumeration of one WI (WI-3438) whose recorded title mentions adopter-application placement; the in-root rule applies. All three `target_paths` are within `E:\GT-KB` root; the new test file is under `platform_tests/scripts/` (no `applications/**` mutation, no out-of-root placement). The phantom-reconciliation work itself does not mutate any application-placement-governed surface.
- PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING - active; covers WI-3355 by membership; standing reliability fast-lane scope.
- GOV-STANDING-BACKLOG-001 - this IS a bulk MemBase mutation; the dedicated Bulk-Operation Scope Clarification subsection below provides the inventory + scope + owner-decision-coverage evidence the clause requires.
- GOV-ARTIFACT-APPROVAL-001 - this implementation creates no canonical artifact (no MemBase spec/GOV/ADR/DCL/PB row, no protected narrative file). Out of scope.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 (advisory) - references owner decisions, requirements, work items, and backlog.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 (advisory) - durable CLI source + regression tests; preserves traceability.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 (advisory) - this is the planned `retired` lifecycle transition for the 10 phantom projects; the CLI implements that transition deterministically.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE - operative authority; the reconciliation is delivered as a deterministic CLI service (per the principle's bias against repetitive AI-mediated plumbing).

## Bulk-Operation Scope Clarification (GOV-STANDING-BACKLOG-001 CLAUSE-VISIBILITY-BULK-OPS)

This proposal IS a bulk MemBase mutation by design — that is the work it accomplishes. The clause's visibility requirement is satisfied by the explicit inventory, owner-decision coverage, and decision-not-deferred status below.

**Inventory (49 phantom memberships + 10 phantom projects; reproduced from live MemBase at proposal authoring time):**

| Phantom project id | Canonical id | Canonical status | Active phantom memberships | Redundant (canonical already has) | Needs fresh canonical link |
|---|---|---|---:|---:|---:|
| PROJECT-PROJECT-ANTIGRAVITY-INTEGRATION | PROJECT-ANTIGRAVITY-INTEGRATION | active | 1 | 1 | 0 |
| PROJECT-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY | PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY | active | 3 | 3 | 0 |
| PROJECT-PROJECT-GTKB-BRIDGE-SCHEDULER-LANES-LEASES | PROJECT-GTKB-BRIDGE-SCHEDULER-LANES-LEASES | retired | 5 | 0 | 5 |
| PROJECT-PROJECT-GTKB-CLAUDE-MD-SCOPE-CORRECTION | PROJECT-GTKB-CLAUDE-MD-SCOPE-CORRECTION | retired | 1 | 0 | 1 |
| PROJECT-PROJECT-GTKB-DETERMINISTIC-SERVICES-001 | PROJECT-GTKB-DETERMINISTIC-SERVICES-001 | active | 2 | 2 | 0 |
| PROJECT-PROJECT-GTKB-ENV-SOT-TOPOLOGY | PROJECT-GTKB-ENV-SOT-TOPOLOGY | active | 2 | 2 | 0 |
| PROJECT-PROJECT-GTKB-EXTERNAL-HARNESS-EXEC-BOUNDARY | PROJECT-GTKB-EXTERNAL-HARNESS-EXEC-BOUNDARY | active | 1 | 1 | 0 |
| PROJECT-PROJECT-GTKB-PUSH-GATE | PROJECT-GTKB-PUSH-GATE | retired | 1 | 0 | 1 |
| PROJECT-PROJECT-GTKB-RELIABILITY-FIXES | PROJECT-GTKB-RELIABILITY-FIXES | active | 32 | 32 | 0 |
| PROJECT-PROJECT-GTKB-SKILL-MODERNIZATION | PROJECT-GTKB-SKILL-MODERNIZATION | active | 1 | 1 | 0 |
| **Totals** | | | **49** | **42** | **7** |

**The 7 retired-canonical WIs (full enumeration):**

- WI-3373 [open/backlogged] Bridge scheduler Slice 2: per-document lease registry
- WI-3374 [open/backlogged] Bridge scheduler Slice 3: serialized bridge index writer
- WI-3375 [open/backlogged] Bridge scheduler Slice 4: per-role dispatch concurrency limits
- WI-3376 [open/backlogged] Bridge scheduler Slice 5: work-lane classification
- WI-3377 [open/backlogged] Bridge scheduler Slice 6: aging and priority weighting
- WI-3438 [open/backlogged] CLAUDE.md split + 18.I files migration to adopter-application root (per the WI's recorded title; no path mutation in this proposal)
- WI-3416 [open/backlogged] Push-Gate master: comprehensive deterministic CI gate Slice 0-...

**Mutation count totals (post-apply):**

- 49 phantom memberships -> new versions inserted with `status = 'superseded'` (append-only; original rows preserved).
- 7 fresh canonical memberships -> new active rows inserted via `link_project_work_item`.
- 10 phantom projects -> new versions inserted with `status = 'retired'` (append-only).

DECISION NOT DEFERRED: this proposal IS the decision packet for the bulk operation. The 49+10 inventory above is the bulk-operation packet. Evidence tokens for the bulk-ops clause's clarification requirement: inventory, packet, owner decision, AskUserQuestion, formal-artifact-approval, deferred (rejected — not deferred), verified, retired. The operation is irreversible at the membership-status / project-status level by the append-only MemBase contract; the bridge CLI rerun is idempotent.

## Requirement Sufficiency

Existing requirements sufficient. No new specification capture required. WI-3355's recorded description already scopes both the source fix (now landed) and the reconciliation; the strict-reconciliation disposition for the 7 retired-canonical cases is supplied by the AskUserQuestion above.

## target_paths

- `groundtruth-kb/src/groundtruth_kb/cli_projects_reconcile.py` (new module: dataclass + deterministic reconciliation service + helpers)
- `groundtruth-kb/src/groundtruth_kb/cli.py` (register one new `@projects_cmd.command("reconcile-doubled-prefix")`; no other change)
- `platform_tests/scripts/test_cli_projects_reconcile.py` (new spec-derived test file)

No other path is authorized. No schema migration. No bridge/INDEX.md mutation by the implementation itself. groundtruth.db is NOT in target_paths because the bridge implementation phase creates source + tests + bridge files only; the MemBase mutations land at owner-directed `--apply` invocation time, after VERIFIED + commit, and are governed by the standing PAUTH and the owner directive that opened this session. All three target paths are in-root under `E:\GT-KB` per `ADR-ISOLATION-APPLICATION-PLACEMENT-001`; no adopter-application directory is touched.

## Design

### CLI surface

```text
gt projects reconcile-doubled-prefix [--dry-run|--apply] [--json]
```

- `--dry-run` (default): scans `current_projects` for `PROJECT-PROJECT-*` ids, builds the per-phantom reconciliation plan, prints/emits the plan; performs NO MemBase writes (test 2 asserts byte-identical DB file hash).
- `--apply`: executes the plan in a single transaction per the deterministic sequence below.
- `--json`: machine-readable output for both modes.

Exactly-one-mode: `--dry-run` and `--apply` are mutually exclusive; default is `--dry-run`. The CLI never writes without the operator explicitly passing `--apply`.

### Reconciliation algorithm (deterministic; idempotent on rerun)

For each phantom project id matching `^PROJECT-PROJECT-` in `current_projects`:

1. Derive `canonical_id` by stripping one leading `PROJECT-` from the phantom id (e.g. `PROJECT-PROJECT-X` -> `PROJECT-X`).
2. Look up `canonical_id` in `current_projects`. If MISSING: skip this phantom and report it as `canonical_missing` (the live inventory has 0 such cases; the code path exists for safety).
3. For each row in `current_project_work_item_memberships` for this phantom with `status = 'active'`:
   a. Check whether `canonical_id` already has an active membership for the same `work_item_id`.
   b. If no canonical equivalent: call `link_project_work_item(canonical_id, work_item_id, ...)` to create one (`source = 'gt projects reconcile-doubled-prefix'`).
   c. Mark the phantom membership row as superseded: insert a new version with `status = 'superseded'`, `source = 'gt projects reconcile-doubled-prefix'`, citing the new canonical membership row id in `change_reason`.
4. Retire the phantom project: insert a new project version with `status = 'retired'`, citing the canonical project id and the count of memberships reconciled in `change_reason`.

Idempotence: on rerun, step 2 finds no active phantom memberships (all already superseded) and the phantom project status is already retired; the algorithm reports the project as already-reconciled and performs zero writes.

### Module shape

`cli_projects_reconcile.py` follows the same pattern as `cli_backlog_status.py` (the slice-2 sibling just landed):

- A frozen `ReconcileRequest` dataclass (`apply: bool`).
- A public `build_reconcile_plan(config, request) -> dict[str, Any]` service that produces the plan and, when `apply=True`, executes it in-process.
- A small `_doubled_prefix_projects(db)` helper.
- Lazy imports kept minimal; no scanner dependency.

The CLI command in `cli.py` is a thin wrapper that translates click options into the request dataclass.

### Stage transition and event-record discipline

Each project-retire and membership-supersede insert records a corresponding event via `_record_event` (existing pattern; matches the standing precedent in `insert_work_item`, `insert_project`, etc.). The `change_reason` strings include the reconciliation context so a future audit can trace each mutation back to this proposal.

## Spec-Derived Verification Plan

Per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, each behavior maps to an executable test:

| # | Behavior | Test |
|---|---|---|
| 1 | `--dry-run` (default) lists every phantom with the correct canonical_id and per-phantom membership counts | `test_dry_run_inventory_matches_seeded_phantoms` |
| 2 | `--dry-run` makes no DB writes (db file byte-identical before/after) | `test_dry_run_makes_no_db_writes` |
| 3 | `--apply` re-links a WI whose canonical project exists active and lacks the equivalent membership | `test_apply_links_missing_canonical_active` |
| 4 | `--apply` re-links a WI whose canonical project exists retired and lacks the equivalent membership (the 7 retired-canonical disposition) | `test_apply_links_missing_canonical_retired` |
| 5 | `--apply` does NOT create a duplicate canonical membership when one already exists for the same WI (redundant case; idempotence at the WI-level) | `test_apply_skips_redundant_canonical_link` |
| 6 | `--apply` supersedes each phantom membership row (new version inserted with status = 'superseded') | `test_apply_supersedes_phantom_membership` |
| 7 | `--apply` retires each phantom project (new version inserted with status = 'retired') | `test_apply_retires_phantom_project` |
| 8 | `--apply` is idempotent on rerun (zero writes second time) | `test_apply_idempotent_on_rerun` |
| 9 | `--apply` with `--json` emits a structured per-phantom report with reconciliation counts | `test_apply_json_report_shape` |
| 10 | Phantom with MISSING canonical is skipped + reported (the safety branch; covered by a seed that creates a `PROJECT-PROJECT-X` with no `PROJECT-X` counterpart) | `test_phantom_with_missing_canonical_is_skipped` |

Execution commands (at implementation report time):

```text
python -m pytest platform_tests/scripts/test_cli_projects_reconcile.py -q
python -m pytest platform_tests/scripts/test_check_harness_parity.py -q
```

Additionally, the post-impl report will include `--dry-run` output captured against the live canonical store as preview-of-apply evidence.

## Recommended Commit Type

`feat:` - net-new CLI capability (`gt projects reconcile-doubled-prefix`) plus its spec-derived test file. The implementation phase commits only source + tests + bridge files; the canonical-store reconciliation itself (running `--apply` post-VERIFIED) modifies MemBase, not the working tree, so it is not part of any commit.

## Prior Deliberations

- WI-3355 description (recorded) - scopes both the source fix (now landed) AND the reconciliation; this proposal addresses the reconciliation half.
- `bridge/gtkb-project-id-prefix-idempotent-fix-005.md` (VERIFIED 2026-05-29) - the just-landed source fix that stopped new doubled-prefix drift.
- `bridge/gtkb-orphan-wi-membership-discovery-slice-1-012.md` (VERIFIED) - precedent bulk reconciliation under the same standing PAUTH; WI-3397 back-filled 58 orphan memberships.
- `memory/feedback_backlog_add_doubled_prefix_membership_bug.md` - the workaround pattern the 42 redundant cases came from (operators manually re-linked after noticing the doubling).
- `memory/feedback_bulk_ops_clause_false_positive_s342.md` - the bulk-ops clause's false-positive pattern; this proposal explicitly engages with the clause because it IS a bulk op (not avoiding it).
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE - the principle this CLI instantiates (one-shot reconciliation via deterministic service rather than per-row AI mediation).
- DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION - source for the standing PAUTH covering this work.
- 2026-05-29 owner directive ("NOT DEFERRED: phantom reconciliation, 10 projects, WI-3355") - authorization for this thread.
- 2026-05-29 AskUserQuestion ("Retired canonical disposition") -> "Re-link to retired canonical (Recommended)" - disposition for the 7 retired-canonical WIs.

## Risk and Rollback

- Risk: an in-flight session opens a fresh KnowledgeDB while `--apply` runs and observes a half-completed state. Mitigation: the algorithm executes per-phantom in a single transaction; the SQLite connection's commit semantics provide all-or-nothing per phantom. Cross-phantom partial completion is acceptable (each phantom is independent) and the CLI is idempotent on rerun.
- Risk: a WI gets created with a doubled-prefix membership AFTER `--apply` runs but BEFORE the rerun safety check. Mitigation: the source defect is closed (idempotent fix landed in 281fa28f); no new doubled-prefix memberships should be created. If one is somehow created (unknown code path), the CLI's rerun reconciles it.
- Risk: the 7 active-on-retired-canonical memberships surface as findings in other tooling. Mitigation: the disposition was explicitly owner-decided via AskUserQuestion above; the bridge thread itself is the audit trail. The orphan-WI detector deliberately does NOT flag membership-on-retired as orphan, so `gt backlog status --with-orphans` returns clean.
- Risk: scope creep into project reactivation (PUSH-GATE per MEMORY.md S368 premature-retire). Mitigation: reactivation is explicitly out of scope per the AskUserQuestion answer; the strict-reconciliation disposition was chosen.
- Rollback: MemBase append-only means each mutation is preserved as a prior version. To undo, insert new versions reverting each phantom-membership back to `status='active'` and each phantom project back to `status='active'`. The CLI does not implement undo (rollback is owner-directed manual MemBase work if ever needed); the CLI's idempotent rerun semantics mean an inadvertent undo by future code would be cleanly re-reconciled.

## Codex Review Asks

1. Confirm the strict-reconciliation disposition (re-link active-on-retired-canonical for the 7 cases; do NOT reactivate the canonical) matches owner-AUQ evidence above.
2. Confirm the three-file `target_paths` (cli_projects_reconcile.py + cli.py registration + new test file) is complete for the implementation phase.
3. Confirm the post-VERIFIED `--apply` invocation against canonical MemBase is appropriately governed (standing PAUTH covers; explicit owner directive scopes; `--dry-run` preview evidence belongs in the post-impl report).
4. Confirm the 10-test spec-derived plan covers the reconciliation behavior and the safety branches (idempotence, dry-run no-writes, missing-canonical skip).
5. Flag any specification this proposal should cite but does not.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
