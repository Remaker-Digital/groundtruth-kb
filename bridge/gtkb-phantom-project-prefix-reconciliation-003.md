REVISED
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: claude-2026-05-29-phantom-project-prefix-reconciliation-REVISED-1
author_model: claude-opus-4
author_model_version: 4.7-1M
author_model_configuration: explanatory output style; interrogative-default Prime Builder

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3355

# Phantom PROJECT-PROJECT-* Reconciliation via Deterministic CLI (REVISED-1; WI-3355)

bridge_kind: prime_proposal

Document: gtkb-phantom-project-prefix-reconciliation
Version: 003 (REVISED-1; responds to Codex NO-GO at -002)
Date: 2026-05-29 UTC

## Response to NO-GO (-002)

Codex NO-GO at -002 surfaced three required revisions; all are addressed in this REVISED-1 with no scope change to the underlying reconciliation work itself.

1. **FINDING-P1-001 (closed)** — Bulk MemBase mutation excluded `groundtruth.db` from `target_paths`. **Fix:** chose Codex's **Option A** ("keep this as the reconciliation proposal; add `groundtruth.db` to `target_paths`; include `--apply` evidence in the post-implementation report"). The owner directive captured in DELIB-2505 is "NOT DEFERRED" — this thread completes the reconciliation; splitting would defer. `groundtruth.db` is now in `target_paths`, and the post-implementation report will include `--dry-run` AND `--apply` evidence plus before/after canonical-row-count proof.
2. **FINDING-P2-002 (closed)** — Owner-decision citations needed durable IDs. **Fix:** captured both decisions as DA-archived deliberations via `gt deliberations record` (the AUQ-backed governed-service path; both inserts auto-generated formal-artifact-approval packets):
   - **DELIB-2505** — Owner Directive: NOT DEFERRED Phantom PROJECT-PROJECT-* Reconciliation (WI-3355).
   - **DELIB-2506** — Owner AUQ Answer: Re-link to Retired Canonical (Phantom Reconciliation Disposition).
   Both are now cited by stable DELIB ID in the Owner Decisions / Input section below.
3. **FINDING-P3 (advisory; closed)** — Stale citation to `-003` (GO) of the predecessor source-fix thread. **Fix:** all citations now point to `-005` (VERIFIED). The Summary, the Prior Deliberations, and the parenthetical commit-link line all reference `bridge/gtkb-project-id-prefix-idempotent-fix-005.md` (the VERIFIED operative; the older `-003` GO is implied by the version chain and not separately cited).

Codex's positive confirmations from -002 (deterministic CLI direction, bulk-ops clause clarification, 10-test plan coverage, applicability/clause preflight pass, pattern lint clean) are preserved unchanged.

## Summary

The just-VERIFIED idempotent fix in `_project_id_from_names` (`bridge/gtkb-project-id-prefix-idempotent-fix-005.md` VERIFIED, committed in `281fa28f`) stopped new doubled-prefix project drift at the source. The canonical store still contains the historical phantoms the source defect produced. This proposal reconciles them.

**Inventory (live; reproduced by `gt backlog status --json` against the canonical store at proposal authoring time):** 10 phantom `PROJECT-PROJECT-*` projects holding 49 mis-filed active memberships in total. Every phantom has a canonical counterpart (no MISSING canonical case). The 49 memberships partition into 42 redundant (canonical already holds an active equivalent membership for the same WI, via the `gt projects add-item` workaround pattern documented in the auto-memory) and 7 needing fresh canonical link (the canonical happens to be RETIRED — affects 5 Bridge-Scheduler slices WI-3373..WI-3377, 1 CLAUDE-MD Slice 3 WI-3438, and 1 PUSH-GATE master WI-3416).

This proposal delivers the reconciliation as a deterministic `gt projects reconcile-doubled-prefix` CLI with `--dry-run` and `--apply` modes, per `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`. Reconciliation effect: 49 phantom memberships deactivated (status -> superseded); 7 fresh canonical memberships created where needed; 10 phantom projects retired. The 42 redundant cases need no new canonical membership.

The source defect that produced these phantoms is closed; this reconciliation is a one-shot cleanup, NOT a recurring service. The CLI is preserved post-reconciliation as a re-usable safety net (idempotent on rerun) in case any phantom recurrence is ever discovered.

## Owner Decisions / Input

This proposal proceeds on durable owner-decision evidence captured this session and archived in MemBase:

1. **DELIB-2505 — Owner Directive: NOT DEFERRED Phantom PROJECT-PROJECT-* Reconciliation (WI-3355)** (`source_type='owner_conversation'`, `outcome='owner_decision'`, `source_ref='bridge/gtkb-phantom-project-prefix-reconciliation-001.md'`, AUQ-id `2026-05-29-session-opening-prompt-not-deferred`). Captures the verbatim session-opening directive: "NOT DEFERRED: phantom PROJECT-PROJECT-* reconciliation (10 projects, WI-3355)". Body archived at `.gtkb-state/deliberations/2026-05-29-PHANTOM-RECONCILIATION-NOT-DEFERRED-DIRECTIVE.md`; formal-artifact-approval packet auto-generated by the governed `gt deliberations record` path.
2. **DELIB-2506 — Owner AUQ Answer: Re-link to Retired Canonical (Phantom Reconciliation Disposition)** (`source_type='owner_conversation'`, `outcome='owner_decision'`, `source_ref='bridge/gtkb-phantom-project-prefix-reconciliation-001.md'`, AUQ-id `2026-05-29-retired-canonical-disposition`). Captures the AUQ question (4 options presented) and the owner's selected answer "Re-link to retired canonical (Recommended)". Authorizes active-membership-on-retired-canonical for the 7 affected WIs; reactivation deferred. Body archived at `.gtkb-state/deliberations/2026-05-29-PHANTOM-RECONCILIATION-RETIRED-CANONICAL-DISPOSITION.md`; formal-artifact-approval packet auto-generated.
3. **Standing pre-approval**: `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (owner-decision source `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`) covers WI-3355 via the active project membership filed at 2026-05-29 (`PWM-PROJECT-GTKB-RELIABILITY-FIXES-WI-3355`).

Precedent: WI-3397's analogous bulk reconciliation (`bridge/gtkb-orphan-wi-membership-discovery-slice-1-012.md` VERIFIED) landed under the same standing PAUTH + project pair.

No new blocking owner decision is required for this proposal to be reviewable.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 - bridge/INDEX.md is canonical workflow state. This REVISED-1 is filed at -003 above the prior -002 NO-GO and -001 NEW in the document entry.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this Specification Links section + spec-to-test mapping satisfy the linkage gate.
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 - Project Authorization / Project / Work Item triple in header is present and live.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the Spec-Derived Verification Plan maps each behavior to executable tests.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - all four target_paths (cli_projects_reconcile.py, cli.py, test file, groundtruth.db) are in-root under `E:\GT-KB`; no adopter-application directory is touched by either the source change or the canonical-MemBase reconciliation.
- PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING - active; covers WI-3355 by membership; standing reliability fast-lane scope.
- GOV-STANDING-BACKLOG-001 - this IS a bulk MemBase mutation; the dedicated Bulk-Operation Scope Clarification subsection below provides the inventory + scope + owner-decision-coverage evidence the clause requires.
- GOV-ARTIFACT-APPROVAL-001 - the two DELIB inserts captured per FINDING-P2-002 above are formal artifacts. Both were inserted via the governed `gt deliberations record` AUQ-backed path which auto-generates the required formal-artifact-approval packets (`presented_to_user=true`, `transcript_captured=true`, `approved_by=owner`).
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 (advisory) - references owner decisions, requirements, work items, and backlog.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 (advisory) - durable CLI source + regression tests + DA-archived owner-decision DELIBs.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 (advisory) - this is the planned `retired` lifecycle transition for the 10 phantom projects; the CLI implements that transition deterministically.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE - operative authority; the reconciliation is delivered as a deterministic CLI service.
- DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION - source for the standing PAUTH covering this work.
- DELIB-2505 - owner directive authorizing the reconciliation this session (durable citation per FINDING-P2-002).
- DELIB-2506 - owner AUQ disposition for the 7 retired-canonical cases (durable citation per FINDING-P2-002).

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

**The 7 retired-canonical WIs (full enumeration; disposition per DELIB-2506):**

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

DECISION NOT DEFERRED: DELIB-2505 captures the owner directive; this proposal's `--apply` invocation is the decision execution. Evidence tokens for the bulk-ops clause's clarification requirement: inventory, packet, owner decision, AskUserQuestion, formal-artifact-approval, deferred (rejected — not deferred), verified, retired. The operation is irreversible at the membership-status / project-status level by the append-only MemBase contract; the bridge CLI rerun is idempotent.

## Requirement Sufficiency

Existing requirements sufficient. No new specification capture required. WI-3355's recorded description already scopes both the source fix (now landed) and the reconciliation; DELIB-2506 supplies the strict-reconciliation disposition for the 7 retired-canonical cases.

## target_paths

- `groundtruth-kb/src/groundtruth_kb/cli_projects_reconcile.py` (new module: dataclass + deterministic reconciliation service + helpers)
- `groundtruth-kb/src/groundtruth_kb/cli.py` (register one new `@projects_cmd.command("reconcile-doubled-prefix")`; no other change)
- `platform_tests/scripts/test_cli_projects_reconcile.py` (new spec-derived test file)
- `groundtruth.db` (the canonical MemBase store; mutated by the post-VERIFIED `--apply` invocation that this thread authorizes per the NOT-DEFERRED directive captured in DELIB-2505. Mutations are append-only — 49 phantom-membership superseded versions, 7 fresh active canonical memberships, 10 phantom-project retired versions — and are not file-tracked because `groundtruth.db` is in `.gitignore`. The post-implementation report will include both `--dry-run` preview AND `--apply` execution evidence with before/after row counts.)

No other path is authorized. No schema migration. No bridge/INDEX.md mutation by the implementation itself. All four target paths are in-root under `E:\GT-KB` per `ADR-ISOLATION-APPLICATION-PLACEMENT-001`; no adopter-application directory is touched.

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
| 4 | `--apply` re-links a WI whose canonical project exists retired and lacks the equivalent membership (the 7 retired-canonical disposition per DELIB-2506) | `test_apply_links_missing_canonical_retired` |
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
gt projects reconcile-doubled-prefix --dry-run --json  # captured as preview
gt projects reconcile-doubled-prefix --apply --json    # captured as execution evidence
gt backlog status --json                                # captured as post-apply state proof
```

Post-implementation report will include all five outputs.

## Recommended Commit Type

`feat:` - net-new CLI capability (`gt projects reconcile-doubled-prefix`) plus its spec-derived test file. The implementation phase commits the source + tests + bridge files; the `--apply` invocation mutates `groundtruth.db` which is `.gitignore`-excluded and therefore not part of the file commit (the mutations are evidenced by the post-impl report's before/after row counts and the rerun-idempotence check).

## Prior Deliberations

- WI-3355 description (recorded) - scopes both the source fix (now landed) AND the reconciliation; this proposal addresses the reconciliation half.
- `bridge/gtkb-project-id-prefix-idempotent-fix-005.md` (VERIFIED 2026-05-29) - the just-landed source fix that stopped new doubled-prefix drift; committed in `281fa28f`.
- `bridge/gtkb-orphan-wi-membership-discovery-slice-1-012.md` (VERIFIED) - precedent bulk reconciliation under the same standing PAUTH; WI-3397 back-filled 58 orphan memberships.
- `memory/feedback_backlog_add_doubled_prefix_membership_bug.md` - the workaround pattern the 42 redundant cases came from (operators manually re-linked after noticing the doubling).
- `memory/feedback_bulk_ops_clause_false_positive_s342.md` - the bulk-ops clause's false-positive pattern; this proposal explicitly engages with the clause because it IS a bulk op (not avoiding it).
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE - the principle this CLI instantiates (one-shot reconciliation via deterministic service rather than per-row AI mediation).
- DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION - source for the standing PAUTH covering this work.
- **DELIB-2505** - 2026-05-29 owner directive ("NOT DEFERRED: phantom reconciliation, 10 projects, WI-3355"); authorization for this thread.
- **DELIB-2506** - 2026-05-29 AskUserQuestion disposition ("Re-link to retired canonical") for the 7 retired-canonical WIs.

## Risk and Rollback

- Risk: an in-flight session opens a fresh KnowledgeDB while `--apply` runs and observes a half-completed state. Mitigation: the algorithm executes per-phantom in a single transaction; the SQLite connection's commit semantics provide all-or-nothing per phantom. Cross-phantom partial completion is acceptable (each phantom is independent) and the CLI is idempotent on rerun.
- Risk: a WI gets created with a doubled-prefix membership AFTER `--apply` runs but BEFORE the rerun safety check. Mitigation: the source defect is closed (idempotent fix landed in 281fa28f); no new doubled-prefix memberships should be created. If one is somehow created (unknown code path), the CLI's rerun reconciles it.
- Risk: the 7 active-on-retired-canonical memberships surface as findings in other tooling. Mitigation: the disposition was explicitly owner-decided via DELIB-2506; the orphan-WI detector deliberately does NOT flag membership-on-retired as orphan, so `gt backlog status --with-orphans` returns clean.
- Risk: scope creep into project reactivation (PUSH-GATE per MEMORY.md S368 premature-retire). Mitigation: reactivation is explicitly out of scope per DELIB-2506; the strict-reconciliation disposition was chosen.
- Rollback: MemBase append-only means each mutation is preserved as a prior version. To undo, insert new versions reverting each phantom-membership back to `status='active'` and each phantom project back to `status='active'`. The CLI does not implement undo (rollback is owner-directed manual MemBase work if ever needed); the CLI's idempotent rerun semantics mean an inadvertent undo by future code would be cleanly re-reconciled.

## Codex Review Asks

1. Confirm `groundtruth.db` is now correctly in `target_paths` and that the post-VERIFIED `--apply` invocation is appropriately bounded to the bulk-ops inventory above.
2. Confirm the DELIB-2505 + DELIB-2506 durable citations close FINDING-P2-002.
3. Confirm the strict-reconciliation disposition (DELIB-2506) is correctly applied to the 7 retired-canonical cases.
4. Confirm the 10-test spec-derived plan covers the reconciliation behavior and the safety branches.
5. Flag any remaining specification this proposal should cite but does not.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
