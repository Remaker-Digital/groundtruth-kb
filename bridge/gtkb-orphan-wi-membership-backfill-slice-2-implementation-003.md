REVISED
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: claude-2026-05-29-orphan-wi-backfill-slice-2-implementation-REVISED-1
author_model: claude-opus-4-7
author_model_version: 4.7-1M
author_model_configuration: explanatory output style; interrogative-default Prime Builder

Project Authorization: PAUTH-WI-3450-ORPHAN-BACKFILL-DRIVER-001
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3450

# Orphan-WI Membership Backfill — Slice 2 Implementation REVISED-1 (WI-3450)

bridge_kind: implementation_proposal

Document: gtkb-orphan-wi-membership-backfill-slice-2-implementation
Version: 003 (REVISED-1; responds to Codex NO-GO at -002)
Date: 2026-05-29 UTC

## Response to NO-GO (-002)

Codex NO-GO at `-002` raised two correctly-grounded blocking findings; both are resolved in this REVISED-1.

1. **FINDING-P1-001 (closed)** — `-001` cited `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (the fast-lane PAUTH bounded by `GOV-RELIABILITY-FAST-LANE-001`). Codex correctly observed that WI-3450 is `origin='new'` (probed live) and the proposal introduces a new CLI surface — both disqualify the work from fast-lane eligibility. **Resolution:** the owner-AUQ-authorized per-WI PAUTH **`PAUTH-WI-3450-ORPHAN-BACKFILL-DRIVER-001`** has been created (active; classes `["source", "test_addition"]`; cites `DELIB-2509`; matches precedent shape of `PAUTH-WI-3443/-3396/-3423`) and is now the proposal's project authorization. `GOV-RELIABILITY-FAST-LANE-001` is added to Specification Links per Codex's recommended action (explaining why the standing PAUTH is NOT authority for this work).
2. **FINDING-P1-002 (closed)** — `-001` claimed all mutation routes through `ProjectLifecycleService` and included `retire`/`exclude` in `apply_resolution`, but no public per-WI retire/exclude surface exists; the lifecycle service exposes only `add_project_item()` (membership) and `retire_project()` (project-level). The claim was service-routing hand-waving. **Resolution:** Codex Option 1 selected by owner — this Slice is narrowed to **assignment-only**. `apply_resolution` no longer performs retire/exclude; those decisions produce **deferred-execution records** in a `deferred_actions.json` artifact for owner review and a future slice's per-WI-retire service. Acceptance criteria and the test matrix are updated; the per-WI retire service is explicitly deferred to a follow-on slice (Slice 2b) with its own data-migration PAUTH.

Per the AUQ-only owner-decision contract, both decisions are captured as **DELIB-2509** ("Per-WI PAUTH + Assign-Only Scope for WI-3450 Orphan Backfill Driver") via the governed `gt deliberations record` path; the formal-artifact-approval packet is auto-generated.

## Owner Decisions / Input

1. **DELIB-2509** — Owner AUQ Answer: Per-WI PAUTH + Assign-Only Scope for WI-3450 Orphan Backfill Driver. Authorizes (a) creating `PAUTH-WI-3450-ORPHAN-BACKFILL-DRIVER-001` with classes `["source", "test_addition"]`, scoped to WI-3450 and citing this DELIB as its owner-decision source; (b) narrowing the Slice 2 implementation to assignment-only; (c) deferring per-WI retire/exclude to a follow-on slice with its own data-migration PAUTH. `source_type='owner_conversation'`, `outcome='owner_decision'`; packet auto-generated via the governed `gt deliberations record` path.
2. **PAUTH-WI-3450-ORPHAN-BACKFILL-DRIVER-001** — active per-WI authorization (created 2026-05-29 citing DELIB-2509); covers WI-3450 driver + tests. Classes: `["source", "test_addition"]`. Does NOT cover canonical `--apply` over live orphans or per-WI retire/exclude.
3. **Implement-Gap-6 selection** (AskUserQuestion, this session): owner chose "Implement Gap 6 impl proposal" — the durable owner authorization that this conversation files the orphan-wi-membership-backfill slice-2 implementation thread.
4. **Scoping-approach selection** (AskUserQuestion, S364 2026-05-29, carried forward): owner chose "Gap 6 first: scope orphan-WI Slice 2" — authorizing WI-3450 and the scoping proposal whose GO at `-002` this implementation follows.

Per-orphan resolution decisions are NOT collected by this proposal. They are collected via AskUserQuestion at runtime in the deferred resolution-execution session.

## Specification Links

- `SPEC-AUQ-POLICY-ENGINE-001` — per-orphan resolution is AUQ-gated; AskUserQuestion is the only valid owner-decision channel. The driver's `--apply` is fail-closed: it refuses any orphan lacking durable owner-decision evidence in the decisions artifact.
- `GOV-STANDING-BACKLOG-001` — backlog is the unified known-work view; every work item belongs to a project/sub-project grouping. The driver restores membership for orphan open work items. See § Clause Scope Clarification — this is a per-orphan AUQ-gated assignment-only resolution driver, not a blind bulk mutation.
- `GOV-RELIABILITY-FAST-LANE-001` — **explicitly cited per Codex P1-001 recommended action.** This spec's eligibility requirements (`origin` in defect/regression, no new CLI surface, no new requirement, small single-concern scope) are why `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (the fast-lane standing PAUTH) is NOT the authorization for this work. WI-3450 is `origin='new'` and this proposal introduces a new CLI surface, both failing fast-lane eligibility. The authorization is instead `PAUTH-WI-3450-ORPHAN-BACKFILL-DRIVER-001`, a per-WI PAUTH matching established precedent.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — assignment is a membership-creation lifecycle transition; the driver routes all assignments through the deterministic `gt projects add-item` (`ProjectLifecycleService.add_project_item`) surface. Retire/exclude (which would be lifecycle transitions) are out-of-scope this slice and produce deferred-execution records only.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all artifacts are in-root under `E:\GT-KB`: the driver under `scripts/`, the test under `platform_tests/scripts/`, runtime plan/decision artifacts under `.gtkb-state/orphan-wi-discovery/`. No application-directory placement; orphan rows are GT-KB platform backlog items, not application files.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — carries the `Project Authorization:` / `Project:` / `Work Item:` triple; `PAUTH-WI-3450-ORPHAN-BACKFILL-DRIVER-001` is active and explicitly includes WI-3450.
- `GOV-ARTIFACT-APPROVAL-001` — the PAUTH created at -002→-003 transition is a formal artifact; its insertion was authorized by DELIB-2509 (owner AUQ) via the governed `gt deliberations record` path which auto-generates the required formal-artifact-approval packet.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this section is the satisfaction; all relevant cross-cutting specs are cited.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — § Spec-Derived Verification Plan maps each behavior to an executable test (assign-only scope); all run against temporary DBs, not canonical.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — filed under the canonical bridge protocol; `bridge/INDEX.md` is authoritative; this REVISED-1 entry inserts at the top of the thread version list with no deletion or rewrite of prior versions.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — assignment is artifact-first: the discovery report is the inventory artifact; the resolution plan, the decisions artifact, and the deferred-actions artifact are durable; membership rows are the assignment artifacts.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — the driver is the deterministic service; no ad-hoc `db.insert_*`. Assignment routes through `ProjectLifecycleService.add_project_item()` only. Retire/exclude do NOT route through a deterministic service in this slice (because no such per-WI service exists) — they produce deferred-execution records and are explicitly out-of-scope.
- `DELIB-2509` — owner AUQ authorizing the per-WI PAUTH and the assign-only scope narrowing.

## Prior Deliberations

- `gtkb-orphan-wi-membership-backfill-slice-2-scoping` (GO `-002`) — the scoping approval this implementation realizes.
- `gtkb-orphan-wi-membership-backfill-slice-2-implementation-002` — Codex NO-GO whose two findings this REVISED-1 closes.
- `gtkb-orphan-wi-membership-discovery-slice-1` (VERIFIED `-012`) — the predecessor; its `build_inventory()` + classification taxonomy is the driver's input contract, reused by import (DRY; no reclassification logic duplicated).
- `DELIB-S357-WI-3353-PAUTH-COMPLETION` — precedent for owner-decision-over-authorization completion (the unrecoverable-orphan owner-decision pattern reused for the deferred-actions records).
- `DELIB-S353-GRILL-SKILL-NEW-PROJECT-2026-05-15` — precedent for an owner-decision creating a new dedicated project for an orphan-like work item (an unrecoverable-orphan resolution option for the future per-WI-retire slice).
- **DELIB-2509** — owner AUQ authorizing this REVISED-1.

## Requirement Sufficiency

Existing requirements sufficient. No new specification capture required. `SPEC-AUQ-POLICY-ENGINE-001`, `GOV-STANDING-BACKLOG-001`, `GOV-RELIABILITY-FAST-LANE-001`, and the Slice 1 discovery contract fully constrain the driver's assign-only scope.

## target_paths

- `scripts/resolve_orphan_wi_memberships.py` (new resolution-driver module; sibling to `scripts/discover_orphan_wi_memberships.py`)
- `platform_tests/scripts/test_resolve_orphan_wi_memberships.py` (new spec-derived test file)

`groundtruth.db` is deliberately NOT in `target_paths`: this proposal builds and tests the driver and runs only `--dry-run` (read-only) against the canonical store. The driver's `--apply` writes canonical MemBase, but is exercised in tests only against temporary DBs; the canonical `--apply` resolution of the live orphans is deferred (§ Canonical Mutation Deferral). The driver does NOT touch `groundtruth-kb/src/groundtruth_kb/cli.py` — it is a standalone `scripts/` module matching the slice-1 discovery scanner's location, so this thread carries no shared-CLI-registration entanglement.

## Canonical Mutation Deferral

Per the scoping GO's Implementation Constraints, this proposal does NOT perform the canonical orphan resolution. It delivers the driver (`source` class), spec-derived tests (`test_addition` class), and a `--dry-run` plan over the live orphan set as read-only evidence. The canonical `--apply` execution (which writes membership rows for the live orphans) is a separate owner-AUQ-gated runtime step requiring per-orphan owner-decision evidence (AskUserQuestion) AND an authorization that covers the data-mutation class — neither of which `PAUTH-WI-3450-ORPHAN-BACKFILL-DRIVER-001` (classes `["source", "test_addition"]`) provides.

## Out-of-Scope This Slice (explicit deferral; closes Codex P1-002)

The following are explicitly deferred and NOT performed by this proposal:

- **Successful canonical retire/exclude execution.** `apply_resolution` does NOT call any retire/exclude path. There is no public per-WI retire surface on `ProjectLifecycleService` today; introducing one is a separate concern with its own design, tests, and PAUTH.
- **Per-WI retire service** in `groundtruth_kb.project.lifecycle`. Adding a `retire_project_work_item()` public method (or equivalent) is deferred to a follow-on slice ("Slice 2b" or equivalent), tracked as a new work item filed at the end of this implementation.
- **`gt projects` CLI surface for per-WI retire/exclude.** Adding `gt projects retire-item` (or equivalent) is part of that follow-on slice. This proposal does not touch `cli.py`.
- **Data-migration authorization.** This slice's PAUTH explicitly does NOT include `data_migration` in `allowed_mutation_classes`. The follow-on slice carries its own data-migration PAUTH.

For the live orphan set (all 30 currently `unrecoverable`), this means: the dry-run produces a plan classifying each as `owner_decision`; an AUQ session captures owner decisions; for any decision that is `retire`/`exclude`, `apply_resolution` writes a **deferred-execution record** to `deferred_actions.json` for the follow-on slice to consume. The driver `--apply` mutates canonical MemBase only for `assign` decisions.

## Live Orphan State (probed read-only at authoring; unchanged from -001)

`python scripts/discover_orphan_wi_memberships.py --json` reported:

- `orphan_count`: 30 (drifted from 27 at the scoping GO, 58 at Slice 1 — confirming the "re-run discovery first" requirement).
- `orphan_count_by_class`: all 30 currently `unrecoverable`.
- The driver's recoverable-class branches (`assign_candidate`) are exercised by seeded test fixtures, not the current live set.

## Design

### Module: `scripts/resolve_orphan_wi_memberships.py`

Reuses Slice 1 by import — `from scripts.discover_orphan_wi_memberships import build_inventory, _open_db` — so classification is single-sourced.

**Public API (assign-only):**

- `RESOLUTION_ACTIONS` — frozenset `{"assign_candidate", "owner_pick", "owner_decision", "already_member_noop"}`. (Same as -001; the `owner_decision` action covers both assign-with-decision and the deferred retire/exclude case.)
- `HIGH_CONFIDENCE_THRESHOLD = 0.80`. Mapping: `recoverable_via_source_spec` (0.95), `recoverable_via_bridge_thread` (0.85), `recoverable_via_id_match` (0.80) → `assign_candidate`; `recoverable_via_title_match` (0.70) → `owner_pick`; `unrecoverable` (0.00) → `owner_decision`.
- `build_resolution_plan(inventory, *, high_confidence_threshold=HIGH_CONFIDENCE_THRESHOLD) -> dict` — pure function; no DB access, no mutation.
- `apply_resolution(plan, decisions, service, *, db, deferred_actions_path) -> dict` — applies the plan given a decisions artifact. **Assign-only canonical mutation.** Fail-closed semantics:
  - Orphan with no matching decision entry → `skipped_no_decision` (NOT mutated).
  - Decision `action == "assign"` → `service.add_project_item(project_id, work_item_id, ...)`.
  - Decision `action in {"retire", "exclude"}` → write a deferred-execution record (`{"work_item_id", "action", "decision_evidence", "deferred_at", "follow_on_slice": "Slice 2b: per-WI retire service"}`) to `deferred_actions_path` (default `.gtkb-state/orphan-wi-discovery/<run-id>/deferred_actions.json`). Reported under `deferred_actions`. NO canonical mutation.
  - Already-active membership for the target project → `already_member_noop` (idempotent).
- `build_and_run(db_path, *, apply, decisions_path, run_id, deferred_actions_path) -> dict` — CLI entry: re-runs `build_inventory`, builds the plan, and (when `apply`) loads the decisions artifact and calls `apply_resolution`. Default is dry-run.

**CLI:** `python scripts/resolve_orphan_wi_memberships.py [--apply --decisions <path>] [--json] [--db-path <path>] [--run-id <id>] [--deferred-actions <path>]`. `--apply` requires `--decisions`; default is dry-run.

### Decisions artifact (the AUQ → script bridge)

A script cannot call AskUserQuestion. The split: the owner-AUQ session (Claude) reviews the dry-run plan, collects owner decisions via AskUserQuestion, and writes a `decisions.json` mapping `work_item_id -> {action, project_id?, decision_evidence}`. The driver's `--apply` consumes that artifact and is fail-closed for any orphan absent from it. This keeps the irreversible owner-gated judgment in the session and the deterministic mutation in the script.

### Deferred-actions artifact (the retire/exclude bridge to Slice 2b)

For decisions whose `action in {"retire", "exclude"}`, `apply_resolution` writes a record to `deferred_actions.json` instead of mutating canonical state. The follow-on slice's per-WI-retire service will consume this artifact. The artifact is the durable record of the owner decision; Slice 2b's service performs the actual canonical mutation under its own data-migration PAUTH.

## Spec-Derived Verification Plan (revised for assign-only scope)

Per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, each behavior maps to an executable test. The matrix is rebalanced for the assign-only scope: the retire/exclude *successful execution* test is removed (no such path exists this slice); a deferred-actions-record test is added in its place.

| # | Behavior | Test |
|---|---|---|
| 1 | `build_resolution_plan` produces per-orphan plan without DB mutation (pure) | `test_plan_generation_is_pure_no_db_access` |
| 2 | high-confidence recoverable (>= 0.80) → `assign_candidate` w/ `candidate_project_id` | `test_high_confidence_maps_to_candidate_assign` |
| 3 | low-confidence recoverable (title_match 0.70) → `owner_pick` (no auto-assign) | `test_low_confidence_maps_to_owner_pick` |
| 4 | unrecoverable → `owner_decision`; `apply_resolution` skips it with no decision entry (fail-closed) | `test_unrecoverable_requires_owner_decision` |
| 5 | `apply_resolution` performs the assignment via `add_project_item` for an `assign` decision | `test_apply_assigns_with_decision_evidence` |
| 6 | `apply_resolution` writes a deferred-actions record for a `retire`/`exclude` decision (does NOT mutate canonical) | `test_apply_writes_deferred_action_for_retire` |
| 7 | idempotency: `assign` for an already-membered WI is a no-op | `test_apply_idempotent_already_member` |
| 8 | driver re-runs discovery (`build_inventory`) before planning — fresh orphan set, not stale report | `test_driver_reruns_discovery_for_fresh_set` |
| 9 | threshold boundary: `id_match` (0.80) → `assign_candidate`; `title_match` (0.70) → `owner_pick` | `test_threshold_boundary_at_080` |
| 10 | `--apply` without `--decisions` errors (CLI guard) | `test_apply_requires_decisions_path` |

Execution commands (at implementation-report time):

```text
python -m pytest platform_tests/scripts/test_resolve_orphan_wi_memberships.py -q
python scripts/resolve_orphan_wi_memberships.py --json    # dry-run plan over live orphans (read-only evidence)
```

## Clause Scope Clarification (Not a Bulk Operation)

This proposal mentions "standing backlog" and "work item" but is NOT a bulk-operation standing-backlog mutation. It builds an assign-only resolution driver and runs only `--dry-run` (read-only) against canonical. The driver's `--apply` mutates only for explicit `assign` decisions backed by per-orphan owner-decision evidence; retire/exclude decisions produce deferred-execution records, NOT mutations. The `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` clarifying evidence is the Slice 1 discovery inventory artifact (`report.json`) plus, at the deferred canonical-execution step, per-orphan owner-decision formal-artifact-approval evidence. No blind bulk write occurs at any stage.

## Slice Boundaries (revised; explicit)

**In scope (this proposal):** the assign-only resolution driver (`build_resolution_plan` + `apply_resolution` + CLI) and its spec-derived tests; a dry-run plan over the live orphan set as evidence; deferred-execution record writing for retire/exclude decisions.

**Out of scope (deferred):** the canonical `--apply` resolution of the live 30 orphans (separate owner-AUQ-gated runtime execution); the per-WI retire service (`groundtruth_kb.project.lifecycle.retire_project_work_item()` or equivalent) — follow-on slice ("Slice 2b") with its own data-migration PAUTH; the `gt projects retire-item` CLI surface — same follow-on; repairing originating orphan-producing code paths; the broader open-work-item reconciliation.

## Recommended Commit Type

`feat:` — net-new deterministic resolution driver + spec-derived test file. No canonical MemBase mutation in this proposal; `groundtruth.db` is `.gitignore`-excluded regardless.

## Risk / Rollback

- **Risk:** the driver's `--apply` could mutate canonical if mis-run. Mitigation: default is dry-run; `--apply` requires `--decisions`; `apply_resolution` is fail-closed (skips orphans with no decision; writes deferred records for retire/exclude rather than executing them). This proposal does not run `--apply` against canonical at all.
- **Risk:** classification drift between Slice 1 and this slice. Mitigation: driver imports Slice 1's `build_inventory` rather than reimplementing — single-sourced taxonomy.
- **Risk:** `tests/scripts/` vs `platform_tests/scripts/` location. Slice 1's discovery test lives at `tests/scripts/`, but `pyproject.toml` `testpaths = ["platform_tests", ...]`. This proposal places its test under `platform_tests/scripts/`. Slice-1 test location flagged as separate possible collection gap.
- **Rollback:** additive (new script + new test); rollback is removing the two files. No canonical state changed; nothing to compensate.

## Acceptance Criteria (revised)

- [ ] `scripts/resolve_orphan_wi_memberships.py` implements `build_resolution_plan` + assign-only `apply_resolution` + CLI per § Design, importing Slice 1's `build_inventory`.
- [ ] 10 spec-derived tests in `platform_tests/scripts/test_resolve_orphan_wi_memberships.py` pass.
- [ ] `apply_resolution` is fail-closed: no decision → skip; retire/exclude decision → write deferred-actions record (NOT canonical mutation); successful assign → `add_project_item`.
- [ ] dry-run over the live orphan set produces a plan with no canonical mutation.
- [ ] No `groundtruth.db` mutation by this proposal; no `cli.py` edit.

## Notes for Loyal Opposition

- This is AXIS-1 dispatchable implementation review.
- Two NO-GO findings from `-002` are addressed structurally: P1-001 via the new per-WI PAUTH `PAUTH-WI-3450-ORPHAN-BACKFILL-DRIVER-001` + the `GOV-RELIABILITY-FAST-LANE-001` citation; P1-002 via the explicit assign-only scope narrowing and the deferred-actions artifact (no claimed-but-nonexistent service).
- The follow-on per-WI-retire slice ("Slice 2b") will be filed as a separate proposal under its own work item; that proposal will own the lifecycle-service extension and the data-migration PAUTH.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
