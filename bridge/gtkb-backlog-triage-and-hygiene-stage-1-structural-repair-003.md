REVISED

bridge_kind: prime_proposal
Document: gtkb-backlog-triage-and-hygiene-stage-1-structural-repair
Version: 003
Author: prime-builder (Claude Opus 4.7, harness B) - interactive owner session
Date: 2026-06-11
Responds-To: bridge/gtkb-backlog-triage-and-hygiene-stage-1-structural-repair-002.md

Project: PROJECT-GTKB-BACKLOG-TRIAGE-AND-HYGIENE-001
Work Item: WI-4454
Project Authorization: PAUTH-PROJECT-GTKB-BACKLOG-TRIAGE-AND-HYGIENE-001-BACKLOG-TRIAGE-AND-HYGIENE-BOUNDED-IMPLEMENTATION-AUTHORIZATION

author_identity: prime-builder
author_harness_id: B
author_session_context_id: 0c0caa91-3f63-41d1-b4c6-960f9b137180
author_model: claude-opus-4-7
author_model_version: 4.7
author_model_configuration: interactive owner session, ::init gtkb pb

target_paths: ["scripts/hygiene/prefix_split_detector.py", "platform_tests/scripts/test_prefix_split_detector.py"]

No KB mutation at GO time: this proposal authorizes adding a read-only detector script and its test. The two execution paths that DO mutate the canonical store - `gt projects reconcile-doubled-prefix --apply` and `python scripts/hygiene/prefix_split_detector.py --apply ...` - run AFTER bridge GO AND a separate per-batch owner AskUserQuestion per the bounded authorization PAUTH (v4; `forbid project_retirement_without_stage_batch_auq`, `forbid work_item_reorder_without_stage_batch_auq`). `groundtruth.db` is intentionally NOT in target_paths; mutations are owner-gated at execution time, not at file-Write time.

---

# Stage 1 - Structural Defect Repair (REVISED-1 addressing -002 NO-GO)

Stage 1 of `PROJECT-GTKB-BACKLOG-TRIAGE-AND-HYGIENE-001` (WI-4454). Chartered by owner decision `DELIB-20261667`. This REVISED-1 addresses Codex's `-002` NO-GO findings; the underlying direction is unchanged but the live counts, the detector contract, and the test assertions are tightened so the proposed disposition matches reality.

## Revision Scope

Addresses both findings in `-002` NO-GO:

- **FINDING-P1 (prefix-split apply semantics can leave active memberships behind a retired project):** The original proposal said the prefix-split work was "8 memberships re-linked from the non-canonical prefix-split id to the canonical" with idempotent "re-linking already-canonical members is a no-op." Live DB inspection confirms what Codex observed: the 8 work items on `GTKB-V1-RELEASE-STRATEGY-001` (WI-3400..WI-3407) **are already active members of the canonical project too**. So the live counts are `canonical_links_to_create = 0` and `non_canonical_memberships_to_deactivate = 8`. Under the old contract the detector could implement a "no-op re-link" that satisfies the tests yet leaves 8 active memberships pointing at the retired non-canonical project - the exact failure Stage 1 must prevent. **Fix:** the detector plan now exposes the three distinct fields, the proposal cites the live counts (0/8/true), and the tests assert that the post-apply state has no active memberships against the retired non-canonical project AND no duplicate active canonical membership is created.
- **FINDING-P2 (doubled-prefix Stage 1.A owner-AUQ counts stale):** The original proposal said "1 phantom to retire" for the existing reconciliation. Live dry-run shows `PROJECT-PROJECT-GTKB-RELIABILITY-FIXES` already has `phantom_status: retired` and `retire_phantom: false`; the only live work is `phantom_memberships_to_supersede = 71` with `canonical_links_to_create = 0`. **Fix:** Stage 1.A AUQ description replaced with the actual dry-run shape; the owner approves a 71-membership supersede with zero project-retire (unless a fresh dry-run at execution time flips the value).

The read-only / no-KB-mutation boundaries, the safety-belt design, the spec linkage, and the project-deferral statements (WI-3500/WI-3501 for the `project_name` divergence) are all preserved.

## Summary

Read-only probes of the live `groundtruth.db` (verified 2026-06-11T15:29:59Z against canonical commit `e6190bfeab10`) confirm Stage 1's actual scope:

- **Doubled-prefix cleanup**: 9 of 10 phantom projects are already fully reconciled. The one remaining phantom (`PROJECT-PROJECT-GTKB-RELIABILITY-FIXES`) has `phantom_status: retired` AND `retire_phantom: false`. The only live work is **71 phantom memberships to supersede** + **0 canonical links to create** (the canonical project `PROJECT-GTKB-RELIABILITY-FIXES` is active and already holds all needed memberships). One `gt projects reconcile-doubled-prefix --apply` invocation; no project-retire side-effect this execution.
- **Prefix-split projects**: exactly **1 active-BOTH pair** - `GTKB-V1-RELEASE-STRATEGY-001` (8 active memberships) vs `PROJECT-GTKB-V1-RELEASE-STRATEGY-001` (10 active memberships). Verified live overlap (Codex `-002` Commands Executed reproduced): the 8 non-canonical memberships (WI-3400..WI-3407) **are 100% overlap** with canonical memberships. Canonical has 2 canonical-only items (WI-3395, WI-4303). So the live cleanup counts are `canonical_links_to_create = 0`, `non_canonical_memberships_to_deactivate = 8`, `non_canonical_project_to_retire = true`.
- **`project_name` field vs membership-table divergence**: Stage 0 reports 111 inconsistent items. Already owned by `WI-3500` + `WI-3501`. **Stage 1 defers** - unchanged from `-001`.

Total live state mutation Stage 1 would authorize (after owner per-batch AUQ at execution time): 71 phantom memberships superseded (no project retire), 8 non-canonical memberships deactivated (no new canonical links needed), 1 non-canonical project retired. **No new state is created.**

## Specification Links

- `GOV-STANDING-BACKLOG-001` - standing-backlog governance authority; Stage 1 reconciles structural defects under it (linked in PAUTH).
- `SPEC-AUTO-BACKLOG-FOR-IMPLEMENTATION-BEARING-SPECS-001` - auto-backlog substrate Stage 1 operates over (linked in PAUTH).
- `GOV-08` - KB is the single source of truth; Stage 1 mutates only the canonical tables it governs and only through governed paths (existing CLI + new detector with explicit `--apply` flag).
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - the freshness principle; the new detector reads canonical tables directly (no cached snapshots).
- `ADR-STANDING-BACKLOG-DB-AUTHORITY-001` / `DCL-STANDING-BACKLOG-DB-SCHEMA-001` - the schema authority being repaired (phantom rows + duplicate canonical ids violate the implied uniqueness of project canonical form). Critically, retiring a project does NOT deactivate that project's active memberships - the detector and tests must do that explicitly (the `-002` NO-GO P1 fix).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all Stage 1 changes are in-root; see Isolation Placement Compliance below.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the durable-artifact discipline; the detector is itself a tracked durable surface (S347 owner-directive bias).
- `GOV-FILE-BRIDGE-AUTHORITY-001` - filed under `bridge/` with a matching `REVISED` INDEX entry; append-only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - all relevant specs cited here.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification derived below.

## Prior Deliberations

- `DELIB-20261667` - owner decision chartering this project (5 decisions + 7-stage shape, including D2 staged batch-approval and D3 priority-preserving ranking). This Stage 1 implements that decision's Stage 1 with the live-data tightening.
- `bridge/gtkb-backlog-triage-and-hygiene-stage-1-structural-repair-002.md` (NO-GO) - Codex's findings this REVISED-1 directly addresses. Both P1 and P2 were verified independently against the live DB before drafting; see Revision Scope above.
- `WI-3355` - the originating doubled-prefix defect (`insert_work_item` `project_name` backfill doubled an already-`PROJECT-`-prefixed id). The originating cause was fixed in commit `281fa28f`; this Stage 1 closes out the historical phantoms.
- `WI-3500` - startup-rollup uses legacy `work_items.project_name` column rather than the canonical membership table (the 111-item divergence Stage 1 explicitly defers to).
- `WI-3501` - formalize the source-of-truth-freshness principle as governance (GOV + DCL); Stage 1 defers to this for the field-vs-membership divergence remediation.
- `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE` - owner directive on the backlog DB schema; informs the canonical-form choice (PROJECT-prefixed id).
- `DELIB-S339-LO-STARTUP-PROJECT-STATE-REPORT` - Loyal Opposition's startup project-state report that surfaced the doubled-prefix and prefix-split classes.
- `DELIB-S357-WI-3353-PAUTH-COMPLETION` - prior session's correction that linked `WI-3353` to its real project after the doubled-prefix defect mis-filed it; demonstrates the operational remediation pattern.
- `DELIB-2505` / `DELIB-2506` / `DELIB-20261050` - substantial DA records on the WI-3355 reconciliation work; the existing CLI's behavior contract is grounded here.
- `bridge/gtkb-backlog-triage-and-hygiene-stage-0-analyzer-011.md` (VERIFIED) - the Stage 0 analyzer that established the `current_project_work_item_memberships` read-only access pattern Stage 1 reuses.

## Owner Decisions / Input

Collected via `AskUserQuestion` during the `/grill-me-for-clarification` interview on 2026-06-11, persisted to `DELIB-20261667`:

1. **D1 - Triage scope = GT-KB platform + a separate labeled Agent Red stage.** Stage 1's reconciliation operates on platform projects; the one prefix-split case is a platform project. No AR-scope action here.
2. **D2 - Retirement model = staged batch-approval.** Stage 1's `--apply` execution paths are explicitly NOT authorized by this bridge GO. Each execution path requires its own per-batch owner AskUserQuestion at impl time, citing the live dry-run output as evidence.
3. **D3 - Ranking axis = composite, priority-preserving.** Stage 1 does not reorder items; it only fixes project membership/identity. Item priorities are untouched.
4. **D4 - Advisory-router corpus = signal-classify + bulk-dispose.** Stage 1 does not dispose of router items; that is Stage 2's scope.
5. **D5 - Include stop-the-leak stage.** The new detector script also serves as the regression scaffold the Stage 3 stop-the-leak surface can extend.
6. **Continuation approval - "Yes" (2026-06-11).** Owner approved continuation after the Stage 0 thread reached VERIFIED at `-011`.

The TWO execution-time owner decisions Stage 1 implementation will collect via separate AskUserQuestion calls (NOT authorized by this proposal's GO), now with the live-corrected counts:

- **Stage 1.A AUQ (per `-002` NO-GO P2 revision)** - approve `gt projects reconcile-doubled-prefix --apply` based on the live dry-run shape: **71 phantom memberships to supersede, 0 canonical links to create, 0 phantom projects to retire** (the remaining phantom `PROJECT-PROJECT-GTKB-RELIABILITY-FIXES` is already retired). At execution time a fresh dry-run is presented to the owner; if `retire_phantom` flips to true the AUQ text must reflect the live value rather than this proposal's snapshot.
- **Stage 1.B AUQ (per `-002` NO-GO P1 revision)** - approve the prefix-split apply for the pair (`GTKB-V1-RELEASE-STRATEGY-001` -> `PROJECT-GTKB-V1-RELEASE-STRATEGY-001`): **0 canonical links to create** (the 8 items WI-3400..WI-3407 are already active members of the canonical project), **8 non-canonical memberships to deactivate** (append non-active successor versions for each of the 8 active membership rows on the non-canonical project), **1 non-canonical project to retire** AFTER the 8 memberships are deactivated (never before - so the retire never leaves active memberships behind it).

## Requirement Sufficiency

**Existing requirements sufficient.** The doubled-prefix reconciliation contract is already specified by the existing `gt projects reconcile-doubled-prefix` CLI's behavior. The prefix-split case follows the same append-only pattern (non-active successor version for each duplicate active membership), now made explicit in the detector contract per the `-002` NO-GO P1 revision. `GOV-STANDING-BACKLOG-001`, `GOV-08`, `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`, `ADR-STANDING-BACKLOG-DB-AUTHORITY-001`, and `DCL-STANDING-BACKLOG-DB-SCHEMA-001` already constrain the data-authority and freshness surfaces. No new requirement is needed.

## Backlog Visibility

`GOV-STANDING-BACKLOG-001` bulk-ops clause: the `--apply` execution paths perform bulk-class operations on `current_projects` + `current_project_work_item_memberships`. Per D2 of `DELIB-20261667`, each operation requires its own per-batch owner AskUserQuestion at execution time, citing the live dry-run output. The bounded PAUTH (v4) explicitly forbids `project_retirement_without_stage_batch_auq` and `work_item_reorder_without_stage_batch_auq`. This proposal authorizes ONLY the addition of a read-only detector script and its test; the execution paths are owner-gated separately.

## Scope and Boundaries

In scope: (1) a new `scripts/hygiene/prefix_split_detector.py` read-only detector with an opt-in `--apply` path for the specific merge case; (2) a pytest at `platform_tests/scripts/test_prefix_split_detector.py`. Out of scope and explicitly excluded: any direct mutation of `groundtruth.db` at Write time; the `project_name`-vs-membership divergence (deferred to `WI-3500` and `WI-3501`); Stage 2's router-corpus disposition; Stage 3's stop-the-leak; Stage 4's re-ranking; Stage 5's Agent Red lane; Stage 6's closeout; deploy/push. The existing-CLI invocation and the new-CLI invocation with `--apply` happen AFTER this proposal's GO and AFTER their separate owner batch AUQ.

## Proposed Implementation

**`scripts/hygiene/prefix_split_detector.py` (new).** A read-only detector module patterned on the existing `gt projects reconcile-doubled-prefix` CLI. Behavior:

1. Open `groundtruth.db` with a read-only SQLite URI (`file:...?mode=ro`).
2. Read `current_projects` and group project ids by canonical stem (strip a leading `PROJECT-` prefix if present). Identify stems with more than one id whose statuses are both `active`.
3. For each active-BOTH split, build a per-pair plan with THREE distinct fields (per `-002` NO-GO P1 revision):
   - `canonical_id` = the `PROJECT-`-prefixed variant; `non_canonical_id` = the bare-stem variant.
   - `canonical_links_to_create` = list of `(work_item_id, ...)` for items that are active on the non-canonical project but NOT on the canonical project (i.e., the items that need a new active membership row pointing at the canonical project).
   - `non_canonical_memberships_to_deactivate` = list of `(work_item_id, current_membership_id)` for every item that is active on the non-canonical project (regardless of whether it is also already on the canonical project). The detector ALWAYS lists these because retire alone does not deactivate active memberships.
   - `non_canonical_project_to_retire` = boolean; `true` when the non-canonical project status is still `active`.
4. Default mode (no `--apply`) emits the plan as JSON to stdout (idempotent, deterministic - sorted by canonical id, sorted by work_item_id within each pair).
5. `--apply` flag - explicitly opt-in - performs the merge for a single owner-specified pair (`--canonical PROJECT-X --merge-from X`). The script will REFUSE to operate if either id is not in the dry-run's active-BOTH set. Per `-002` NO-GO P1 revision, the apply order is strict:
   - For each item in `canonical_links_to_create`: append a new active membership row pointing at the canonical project.
   - For each item in `non_canonical_memberships_to_deactivate`: append a non-active successor version that deactivates the existing active row on the non-canonical project - even when the canonical membership already exists (this is the load-bearing change vs `-001`).
   - Only AFTER all non-canonical memberships are deactivated, retire the non-canonical project. This ordering guarantees that no retired project is ever left with active memberships.
   - Idempotent on rerun: each step checks whether its successor row already exists; if so, that step is a no-op.

**`platform_tests/scripts/test_prefix_split_detector.py` (new).** Tests covering, per `-002` NO-GO P1 revision:

- **Detection structure**: on a synthetic fixture, the dry-run plan exposes all three fields (`canonical_links_to_create`, `non_canonical_memberships_to_deactivate`, `non_canonical_project_to_retire`).
- **Live-counts fidelity**: a fixture matching the live shape (8 items all overlapping) produces `canonical_links_to_create == []`, `non_canonical_memberships_to_deactivate` listing all 8, `non_canonical_project_to_retire == true`.
- **Post-apply state invariants** (the load-bearing assertions per the NO-GO):
   - Zero duplicate active canonical memberships are created (the 8 items each have exactly one active membership on the canonical project after apply, not two).
   - The 8 non-canonical memberships are no longer active (a non-active successor version exists for each).
   - The non-canonical project is retired.
   - **The retired non-canonical project has zero active memberships pointing at it** (this is the structural-defect assertion Stage 1 exists to enforce).
- **Apply-order discipline**: the project retire happens after all non-canonical memberships are deactivated; a regression test simulates a partial apply (deactivations done but project still active) and asserts the rerun completes the retire.
- **Refusal guard**: `--apply --canonical X --merge-from Y` refuses if (X, Y) is not in the dry-run's active-BOTH set; `--apply` without those flags refuses with an "owner must specify the pair" error.
- **Read-only / no-mutation** (default mode): AST scan asserts no `commit`/`UPDATE`/`DELETE`/`INSERT` on the default-mode path; the DB connection is opened read-only; a row-count-unchanged guard confirms `current_projects` and `current_project_work_item_memberships` are unchanged after a default-mode run.
- **Determinism**: two runs over identical input produce identical output.
- **Idempotency on rerun**: a second `--apply` over an already-completed pair writes zero new versions.
- **No regression to sibling benchmarks**: registering the module does not break existing benchmarks (importability assert).

**No changes to `groundtruth-kb/src/groundtruth_kb/*`.** The new detector lives under `scripts/hygiene/`.

## Isolation Placement Compliance

`ADR-ISOLATION-APPLICATION-PLACEMENT-001`: all Stage 1 changes are in-root under `E:\GT-KB\` - the detector under `scripts/hygiene/`, the test under `platform_tests/scripts/`, and this bridge file under `E:\GT-KB\bridge\`.

## Spec-Derived Verification Plan

| Spec / requirement | Derived test |
|---|---|
| `GOV-STANDING-BACKLOG-001` + `ADR-STANDING-BACKLOG-DB-AUTHORITY-001` (canonical project id uniqueness; retiring a project does NOT deactivate its memberships) | test: on a synthetic fixture, the detector identifies the active-BOTH pair, exposes all three plan fields, and `--apply` leaves the post-state with (a) no duplicate active canonical memberships, (b) the 8 non-canonical memberships non-active, (c) the non-canonical project retired, (d) the retired non-canonical project has zero active memberships pointing at it |
| `GOV-08` (read-only at Write time; no canonical mutation in default mode) | test: AST scan of `prefix_split_detector.py` asserts no `commit`/`UPDATE`/`DELETE`/`INSERT` write paths in the default (no `--apply`) code path; the DB connection is opened read-only; row-count-unchanged guard |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` (canonical reads; live execution-time data) | test: dry-run reads `current_projects` + `current_project_work_item_memberships` directly; the Stage 1.A and Stage 1.B AUQ paths re-derive their counts from a fresh dry-run at execution time, NOT from this proposal's snapshot |
| D2 (per-batch owner AUQ; refuse stale plans) | test: `--apply` without `--canonical` + `--merge-from` refuses; `--apply --canonical X --merge-from Y` refuses if (X, Y) is not in the live dry-run's active-BOTH set |
| `-002` NO-GO P1 (apply-order: deactivate before retire) | test: a partial-state fixture (non-canonical project still active, deactivations done) makes the rerun complete only the retire step; a partial-state fixture (project retired but deactivations not done) is treated as a defective prior state and the tool reports it without auto-recovering (owner-AUQ-only path) |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python -m pytest platform_tests/scripts/test_prefix_split_detector.py -q`; `ruff check` AND `ruff format --check` on every changed Python file |

## Acceptance Criteria

1. `scripts/hygiene/prefix_split_detector.py` exists, runs read-only by default, and emits a deterministic JSON plan with the three named fields (`canonical_links_to_create`, `non_canonical_memberships_to_deactivate`, `non_canonical_project_to_retire`) for every active-BOTH prefix-split pair.
2. `--apply --canonical X --merge-from Y` is the only path that mutates the DB; refuses to operate on any pair not present in the current dry-run; performs the steps in strict order (link-create -> memberships-deactivate -> project-retire); is idempotent on rerun.
3. After `--apply` on the live `GTKB-V1-RELEASE-STRATEGY-001` / `PROJECT-GTKB-V1-RELEASE-STRATEGY-001` pair (under owner Stage 1.B AUQ), the retired non-canonical project has zero active memberships pointing at it; the 8 items (WI-3400..WI-3407) each have exactly one active canonical membership (not two).
4. The no-mutation AST scan, the read-only connection check, and the row-count-unchanged guard all pass for the default mode.
5. Classification + plan emission is deterministic across two runs on identical input.
6. All new tests pass; `ruff check` and `ruff format --check` are clean on every changed Python file.

## Bridge Protocol Compliance

Filed at `bridge/gtkb-backlog-triage-and-hygiene-stage-1-structural-repair-003.md` with a matching `REVISED` entry directly below the Document header at the top of `bridge/INDEX.md`; append-only. `GOV-FILE-BRIDGE-AUTHORITY-001` is honored; nothing implements until Loyal Opposition records `GO`. At implementation time the implementation-start packet will be minted from the GO against the bounded authorization PAUTH (v4) under the `source_addition` / `test_addition` mutation classes. The `--apply` executions execute only AFTER bridge GO AND a fresh dry-run AND their per-batch owner AskUserQuestion - not at file Write time.

## Risk and Rollback

- **Risk - `--apply` deactivates a non-canonical membership that some other workflow relies on:** the dry-run lists every (work_item, project) pair before any mutation; owner can refuse the Stage 1.B AUQ if they spot something wrong. Append-only versioning: each deactivation is a non-active successor version, reversible by inserting another active successor. **Rollback per item:** insert an active successor membership row.
- **Risk - partial `--apply` execution leaves an inconsistent state (deactivations done but project not retired, or vice-versa):** the strict apply order (link-create -> deactivate -> retire) plus rerun idempotency means a re-execution completes the remaining steps. **Rollback:** rerun `--apply` on the same pair; idempotent steps are no-ops, missing steps execute.
- **Risk - `gt projects reconcile-doubled-prefix --apply` superseded a phantom membership the owner needed:** the dry-run lists every affected membership before any mutation. Append-only versioning means each supersede is reversible. **Rollback per affected membership:** insert a successor active row.
- **Risk - between this REVISED-1 filing and execution, the live data drifts (e.g., a parallel session adds a third active membership variant):** the execution-time dry-run is authoritative; the Stage 1.A and Stage 1.B AUQ owner-facing text MUST be re-derived from the fresh dry-run at execution time, not from this proposal's snapshot. The proposal's snapshot is verifiable evidence the contract was correct when reviewed; the execution-time dry-run is the source of truth at apply time.

## Recommended Implementation Routing

**Claude/Codex (deterministic source + test).** Stage 1 is greenfield read-only source plus a pytest under an existing PAUTH with no protected-narrative or KB-mutation surface at Write time. The intellectual care is in two places: (a) the apply-order discipline (link-create -> deactivate -> retire, NEVER reorder); (b) the post-apply state invariants tested as load-bearing assertions, especially "retired non-canonical project has zero active memberships pointing at it" - that is the test that closes the structural-defect class Stage 1 exists to repair.

## Recommended Commit Type

`feat:` - net-new detector script + test suite (a new measurement + safe-merge capability), with no behavior change to existing surfaces. The `--apply` executions that occur separately are not part of the commit Stage 1 produces.
