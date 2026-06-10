NEW
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: claude-2026-05-29-orphan-wi-backfill-slice-2-implementation-00d6b362
author_model: claude-opus-4-8
author_model_version: opus-4-8
author_model_configuration: explanatory output style; interrogative-default Prime Builder

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3450

# Orphan-WI Membership Backfill — Slice 2 Implementation (WI-3450)

bridge_kind: prime_proposal

Document: gtkb-orphan-wi-membership-backfill-slice-2-implementation
Version: 001 (NEW; implementation proposal following scoping GO)
Date: 2026-05-29 UTC

## Summary

Implements Slice 2 of the orphan-WI-membership workstream, whose approach was approved at `gtkb-orphan-wi-membership-backfill-slice-2-scoping` (Codex GO at `-002`). Slice 1 (`gtkb-orphan-wi-membership-discovery-slice-1` VERIFIED `-012`) shipped a read-only discovery scanner (`scripts/discover_orphan_wi_memberships.py`) that inventories open work items with no active project membership and classifies each by recoverability. Slice 2 delivers the **resolution driver** (`scripts/resolve_orphan_wi_memberships.py`): a deterministic service that re-runs discovery, builds a per-orphan resolution plan, and applies owner-decision-gated mutations through the existing deterministic `gt projects` service.

This implementation delivers the **driver + spec-derived tests + a dry-run plan over the live orphan set**. Per the scoping GO's Implementation Constraints, the canonical `--apply` resolution of the live orphans (the data mutation) is **owner-AUQ-gated runtime execution deferred to a separate resolution session** — it is NOT performed by this proposal. Consequently this proposal's canonical-store footprint is read-only; `groundtruth.db` is intentionally absent from `target_paths` (see § target_paths and § Canonical Mutation Deferral).

## Owner Decisions / Input

1. **Implement-Gap-6 selection** (AskUserQuestion, S373 2026-05-29, this session): owner chose "Implement Gap 6 impl proposal" — authorizing this conversation to file the orphan-wi-membership-backfill slice-2 implementation proposal, get Codex GO, and implement the driver. This is the durable owner authorization for filing this NEW proposal.
2. **Scoping-approach selection** (AskUserQuestion, S364 2026-05-29, carried forward): owner chose "Gap 6 first: scope orphan-WI Slice 2" — authorizing the Slice 2 work item (WI-3450) and the scoping proposal whose GO this implementation follows.
3. **Standing pre-approval**: `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (source `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`) covers WI-3450 by active project membership. Per the scoping GO, the standing PAUTH's `source` + `test_addition` classes cover building the driver + tests (this proposal's scope). It does NOT cover the canonical data-migration mutation; that is deferred (§ Canonical Mutation Deferral).
4. **Per-orphan resolution decisions** are NOT collected by this proposal. They are collected via AskUserQuestion at runtime in the deferred resolution-execution session, each producing durable decision evidence the driver's `--apply` consumes.

No new blocking owner decision is required to review this implementation proposal.

## Specification Links

- `SPEC-AUQ-POLICY-ENGINE-001` — per-orphan resolution is AUQ-gated; AskUserQuestion is the only valid owner-decision channel. The driver's `--apply` is fail-closed: it refuses any orphan lacking durable owner-decision evidence in the decisions artifact.
- `GOV-STANDING-BACKLOG-001` — backlog is the unified known-work view; every work item belongs to a project/sub-project grouping. The driver restores membership for orphan open work items. See § Clause Scope Clarification — this is a per-orphan AUQ-gated resolution driver, not a blind bulk mutation.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — resolution actions are lifecycle transitions (membership creation; owner-approved retire/exclude). The driver routes every mutation through the deterministic `gt projects` service and the approval-packet pathway.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all artifacts are in-root under `E:\GT-KB`: the driver under `scripts/`, the test under `platform_tests/scripts/`, runtime plan/decision artifacts under `.gtkb-state/orphan-wi-discovery/`. No application-directory placement; orphan rows are GT-KB platform backlog items, not application files.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — carries the `Project Authorization:` / `Project:` / `Work Item:` triple; `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` is active and covers WI-3450.
- `GOV-ARTIFACT-APPROVAL-001` — owner-approved retire/exclude decisions for unrecoverable orphans require formal-artifact-approval packets; the driver's `--apply` refuses a retire/exclude action whose decision entry lacks an `approval_packet` reference (fail-closed).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this section satisfies the linkage gate; all relevant cross-cutting specs are cited.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the § Spec-Derived Verification Plan maps each behavior to an executable test; all run against temporary DBs, not canonical.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — filed under the canonical bridge protocol; `bridge/INDEX.md` is authoritative; this entry inserts the new thread at the top with no deletion or rewrite of prior versions.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — resolution is artifact-first: the discovery report is the inventory artifact; the resolution plan and the decisions artifact are durable; membership rows and approval-gated retires are the resolution artifacts.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — the driver is the deterministic service; it performs no ad-hoc `db.insert_*`; all mutation routes through `gt projects` (`ProjectLifecycleService`) and the approval-packet pathway.

## Prior Deliberations

- `gtkb-orphan-wi-membership-backfill-slice-2-scoping` (GO `-002`) — the scoping approval this implementation realizes; its Implementation Constraints (carry `target_paths`, declare `groundtruth.db` where mutation applies, owner-AUQ-gate unrecoverable/low-confidence decisions, provide the spec-derived test map) are honored below.
- `gtkb-orphan-wi-membership-discovery-slice-1` (VERIFIED `-012`) — the predecessor; its `build_inventory()` + classification taxonomy (`recoverable_via_source_spec` 0.95 → `recoverable_via_title_match` 0.70 → `unrecoverable` 0.00) is the driver's input contract, reused by import (DRY; no reclassification logic duplicated).
- `DELIB-S357-WI-3353-PAUTH-COMPLETION` — precedent for owner-decision over project-authorization completion; the unrecoverable-orphan retire/assign owner-decision pattern reuses it.
- `DELIB-S353-GRILL-SKILL-NEW-PROJECT-2026-05-15` — precedent for an owner-decision creating a new dedicated project for an orphan-like work item (an unrecoverable-orphan resolution option).
- Deliberation Archive search `orphan work item resolution driver apply decisions retire exclude membership backfill` (run S373 2026-05-29) returned the slice-1 review chain and the PAUTH-completion precedent; no prior Slice 2 implementation design exists. This is the first.

## Requirement Sufficiency

Existing requirements sufficient. No new specification capture required. `SPEC-AUQ-POLICY-ENGINE-001`, `GOV-STANDING-BACKLOG-001`, `GOV-ARTIFACT-APPROVAL-001`, and the Slice 1 discovery contract fully constrain the driver. The driver introduces no new owner-facing requirement; it operationalizes the approved Slice 2 approach.

## target_paths

- `scripts/resolve_orphan_wi_memberships.py` (new resolution-driver module; sibling to `scripts/discover_orphan_wi_memberships.py`)
- `platform_tests/scripts/test_resolve_orphan_wi_memberships.py` (new spec-derived test file)

`groundtruth.db` is deliberately NOT in `target_paths`: this proposal builds and tests the driver and runs only `--dry-run` (read-only) against the canonical store. The driver's `--apply` writes canonical MemBase, but is exercised in tests only against temporary DBs; the canonical `--apply` resolution of the live orphan set is deferred (§ Canonical Mutation Deferral). The driver also does NOT touch `groundtruth-kb/src/groundtruth_kb/cli.py` — it is a standalone `scripts/` module (matching the slice-1 discovery scanner's location), so this thread carries no shared-CLI-registration entanglement.

## Canonical Mutation Deferral

Per the scoping GO's Implementation Constraints ("the standing reliability PAUTH's `source`, `test_addition`, and `hook_upgrade` classes are not, by themselves, a data-migration envelope"), this proposal does NOT perform the canonical orphan resolution. It delivers:

- the resolution driver (`source`, covered by the standing PAUTH);
- spec-derived tests (`test_addition`, covered by the standing PAUTH);
- a `--dry-run` plan over the live orphan set as read-only evidence.

The canonical `--apply` execution (which writes membership rows and approval-gated retires for the live orphans) is a separate owner-AUQ-gated runtime step. It requires its own authorization surface at execution time: per-orphan owner-decision evidence (AskUserQuestion) plus, for retire/exclude, formal-artifact-approval packets — and, if executed as a batch data migration, an authorization that explicitly covers that mutation class. That execution is intentionally out of scope here so this proposal stays inside `source` + `test_addition`.

## Live Orphan State (probed read-only at authoring)

`python scripts/discover_orphan_wi_memberships.py --run-id impl-scope-2026-05-29 --json` reported:

- `orphan_count`: 30 (drifted from 27 at the scoping GO, 58 at Slice 1 — confirming the "re-run discovery first" requirement; the count is not stable between slices).
- `orphan_count_by_class`: all 30 currently `unrecoverable` (no heuristic yields a candidate project; this matches the legacy `wont_fix`-adjacent / no-source-spec block).
- The driver's recoverable-class branches are therefore exercised by seeded test fixtures, not the current live set (the live set is entirely unrecoverable today; the recoverable classes appear as the open-WI population changes).

## Design

### Module: `scripts/resolve_orphan_wi_memberships.py`

Reuses Slice 1 by import — `from scripts.discover_orphan_wi_memberships import build_inventory, _open_db` — so classification is single-sourced (no duplicate heuristics).

**Public API:**

- `RESOLUTION_ACTIONS` — frozenset `{"assign_candidate", "owner_pick", "owner_decision", "already_member_noop"}`.
- `HIGH_CONFIDENCE_THRESHOLD = 0.80` — the threshold the scoping deferred to the implementation. Mapping to Slice 1's class confidences: `recoverable_via_source_spec` (0.95), `recoverable_via_bridge_thread` (0.85), `recoverable_via_id_match` (0.80) are high-confidence (>= 0.80 → `assign_candidate`); `recoverable_via_title_match` (0.70) is low-confidence (< 0.80 → `owner_pick`); `unrecoverable` (0.00 → `owner_decision`). The threshold sits exactly at `id_match` so the three structural-evidence classes are auto-mappable and the title-only guess is owner-picked.
- `build_resolution_plan(inventory: dict, *, high_confidence_threshold: float = HIGH_CONFIDENCE_THRESHOLD) -> dict` — pure function; consumes a discovery inventory and emits a per-orphan plan with one `RESOLUTION_ACTION` each. No DB access, no mutation.
- `apply_resolution(plan: dict, decisions: dict, service: ProjectLifecycleService, *, db: KnowledgeDB) -> dict` — applies the plan given a decisions artifact. Fail-closed semantics:
  - An orphan with no matching decision entry is **skipped** and reported under `skipped_no_decision` (NOT mutated).
  - `assign` decision → `service.add_project_item(project_id, work_item_id, ...)` (the deterministic `gt projects add-item` path).
  - `retire` / `exclude` decision → requires `decision["approval_packet"]` to reference an existing `.groundtruth/formal-artifact-approvals/*.json`; absent → refused and reported under `refused_missing_packet` (fail-closed, never mutates).
  - An orphan that already has an active membership for the target project → `already_member_noop` (idempotent; no second row).
- `build_and_run(db_path, *, apply, decisions_path, run_id) -> dict` — the CLI entry: re-runs `build_inventory` (fresh discovery), builds the plan, and (when `apply`) loads the decisions artifact and calls `apply_resolution`. Default is dry-run.

**CLI:** `python scripts/resolve_orphan_wi_memberships.py [--apply --decisions <path>] [--json] [--db-path <path>] [--run-id <id>]`. `--apply` requires `--decisions`; without `--apply` the driver is dry-run (plan only, no mutation). Mirrors the discovery scanner's argparse surface.

### Decisions artifact (the AUQ → script bridge)

A script cannot call AskUserQuestion. The deterministic-services split: the owner-AUQ session (Claude) reviews the dry-run plan, collects owner decisions via AskUserQuestion, and writes a `decisions.json` mapping `work_item_id -> {action, project_id?, approval_packet?, auq_evidence}`. The driver's `--apply` consumes that artifact and is fail-closed for any orphan absent from it. This keeps the irreversible owner-gated judgment in the session and the deterministic mutation in the script.

## Spec-Derived Verification Plan

Per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, each behavior maps to an executable test in `platform_tests/scripts/test_resolve_orphan_wi_memberships.py`. All tests run against temporary DBs (seeded fixtures), never canonical.

| # | Behavior (from scoping § Verification Approach) | Test |
|---|---|---|
| 1 | `build_resolution_plan` reads an inventory and produces a per-orphan plan without mutating canonical state (dry-run) | `test_plan_generation_is_pure_no_db_access` |
| 2 | high-confidence recoverable (>= 0.80) maps to `assign_candidate` with the orphan's `candidate_project_id` | `test_high_confidence_maps_to_candidate_assign` |
| 3 | low-confidence recoverable (`title_match` 0.70) maps to `owner_pick` (no auto-assign) | `test_low_confidence_maps_to_owner_pick` |
| 4 | unrecoverable maps to `owner_decision`; `apply_resolution` refuses it without a decision entry (fail-closed) | `test_unrecoverable_requires_owner_decision` |
| 5 | `apply_resolution` performs the membership write for an `assign` decision (via `add_project_item`) | `test_apply_assigns_with_decision_evidence` |
| 6 | `apply_resolution` refuses a `retire`/`exclude` decision lacking an `approval_packet` reference (fail-closed) | `test_apply_retire_refused_without_packet` |
| 7 | idempotency: applying an `assign` for an already-membered WI is a no-op (no duplicate row) | `test_apply_idempotent_already_member` |
| 8 | the driver re-runs discovery (calls `build_inventory`) before planning — fresh orphan set, not a stale report | `test_driver_reruns_discovery_for_fresh_set` |
| 9 | threshold boundary: `id_match` (0.80) is `assign_candidate`; `title_match` (0.70) is `owner_pick` | `test_threshold_boundary_at_080` |
| 10 | `--apply` without `--decisions` errors (the CLI guard) | `test_apply_requires_decisions_path` |

Execution commands (at implementation-report time):

```text
python -m pytest platform_tests/scripts/test_resolve_orphan_wi_memberships.py -q
python scripts/resolve_orphan_wi_memberships.py --json    # dry-run plan over live orphans (read-only evidence)
```

## Clause Scope Clarification (Not a Bulk Operation)

This proposal mentions "standing backlog" and "work item" but is NOT a bulk-operation standing-backlog mutation. It builds a resolution driver and runs only `--dry-run` (read-only) against canonical. The driver's `--apply` resolves orphans through per-orphan / grouped owner AskUserQuestion with formal-artifact-approval evidence for retire/exclude — and that `--apply` canonical execution is deferred (§ Canonical Mutation Deferral). The `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` clarifying evidence is the Slice 1 discovery inventory artifact (`report.json`) plus, at the deferred execution, per-orphan owner-decision formal-artifact-approval evidence. No blind bulk write occurs at any stage of this proposal.

## Slice Boundaries

**In scope (this proposal):** the resolution driver (`build_resolution_plan` + `apply_resolution` + CLI) and its spec-derived tests; a dry-run plan over the live orphan set as evidence.

**Out of scope (deferred):** the canonical `--apply` resolution of the live 30 orphans (owner-AUQ-gated runtime execution requiring per-orphan decisions + retire approval packets, possibly a data-migration authorization); repairing the originating code paths that create orphans (Slice 1's `root_cause_changed_by` feeds a separate reliability work item); the broader open-work-item reconciliation (Slice 2 resolves membership orphans only).

## Recommended Commit Type

`feat:` — a net-new deterministic resolution driver (`scripts/resolve_orphan_wi_memberships.py`) plus its spec-derived test file. No canonical MemBase mutation in this proposal; `groundtruth.db` is `.gitignore`-excluded regardless.

## Risk / Rollback

- **Risk:** the driver's `--apply` could mutate canonical if mis-run. Mitigation: default is dry-run; `--apply` requires `--decisions`; `apply_resolution` is fail-closed (skips orphans with no decision, refuses retire/exclude without an approval-packet reference). This proposal does not run `--apply` against canonical at all.
- **Risk:** classification drift between Slice 1 and Slice 2. Mitigation: the driver imports Slice 1's `build_inventory` rather than reimplementing classification, so the taxonomy is single-sourced.
- **Risk:** `tests/scripts/` vs `platform_tests/scripts/` location. Slice 1's discovery test lives at `tests/scripts/test_discover_orphan_wi_memberships.py`, but `pyproject.toml` `testpaths = ["platform_tests", "applications/Agent_Red/tests"]`. This proposal places its test under `platform_tests/scripts/` so it is collected by the default pytest run. The slice-1 test's `tests/scripts/` location is flagged as a separate possible collection gap (candidate reliability WI; not fixed here).
- **Rollback:** the driver is additive (new script + new test); rollback is removing the two files. No canonical state is changed by this proposal, so there is nothing to compensate.

## Acceptance Criteria

- [ ] `scripts/resolve_orphan_wi_memberships.py` implements `build_resolution_plan` + `apply_resolution` + CLI per § Design, importing Slice 1's `build_inventory`.
- [ ] 10 spec-derived tests in `platform_tests/scripts/test_resolve_orphan_wi_memberships.py` pass.
- [ ] dry-run over the live orphan set produces a plan with no canonical mutation.
- [ ] `apply_resolution` is fail-closed (no decision → skip; retire/exclude without packet → refuse).
- [ ] No `groundtruth.db` mutation by this proposal; no `cli.py` edit.

## Notes for Loyal Opposition

- This is AXIS-1 dispatchable implementation review.
- The driver location (`scripts/`) intentionally matches the Slice 1 discovery scanner and avoids the shared `groundtruth-kb/src/groundtruth_kb/cli.py` (which is currently entangled with multiple uncommitted parallel work-streams; keeping this thread out of it is deliberate).
- Canonical resolution is deferred per the scoping GO's data-migration-envelope constraint; please confirm that deferral is the correct reading of your `-002` Implementation Constraints, or NO-GO if you expect the live-orphan resolution to be executed within this thread (in which case the authorization surface + AUQ batching would need to be added).

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
