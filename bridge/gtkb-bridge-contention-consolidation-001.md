NEW

bridge_kind: governance_advisory
Document: gtkb-bridge-contention-consolidation
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-06-01 UTC
Session: S384
Recommended commit type: chore
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Items Affected: WI-3513, WI-3280, WI-3485, WI-AUTO-SPEC-INTAKE-57A736, WI-3265, WI-4213, WI-3320, WI-3334, WI-3322
author_identity: Claude Prime Builder
author_harness_id: B
author_session_context_id: S384-bridge-contention-consolidation
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code CLI on Windows 11 (harness B, explanatory output style)

target_paths: [".gtkb-state/apply-bridge-contention-consolidation.py"]

# Bridge Kind Justification

`governance_review`: a one-time MemBase backlog-structure grooming. It creates
sub-project grouping rows under an existing project and adds work-item
memberships; it does not modify source, tests, hooks, rules, specifications, or
work-item lifecycle state. No `Project Authorization` is required (no protected
mutation); owner approval is the S384 AUQ in the Owner Decisions / Input
section. Execution is idempotent via one in-root helper at
`.gtkb-state/apply-bridge-contention-consolidation.py`.

# Owner Decisions / Input

- 2026-06-01 UTC, S384 — AUQ ("Next step"): after Prime delivered a 3-layer
  review of bridge contention across 5 fragmented projects, the owner selected
  **"Consolidate contention work under one project view"** — re-home the
  genuinely-open bridge-contention WIs under `PROJECT-GTKB-BRIDGE-PROTOCOL-
  RELIABILITY` with a coherent taxonomy and flag the stale-done WIs.
- 2026-06-01 UTC, S384 — AUQ ("Harness C role") + clarification: dual-PB is
  intended; "active" is capability-gated on bridge-event reception. Establishes
  that bridge-item contention from C's interactive INDEX writes is a standing
  condition the consolidation must make legible (Layer 1).

# Claim

Impose a coherent, three-layer sub-structure on
`PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY` so it is the single authoritative
"state of bridge contention" surface, gather the genuinely-open
contention WIs currently scattered across four other projects, and flag the
retired-but-still-"open"-reading poller WIs for retirement reconciliation.

# Evidence: current fragmentation (live MemBase, 2026-06-01)

The contention work spans five projects with no unifying structure:

- `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY` already holds WI-3513, WI-3280,
  WI-3485, WI-AUTO-SPEC-INTAKE-57A736 — but **flat**, alongside three
  `resolution_status=retired` poller WIs that still surface as open work.
- `PROJECT-GTKB-RELIABILITY-FIXES` (70 open WIs) buries WI-3320, WI-3334,
  WI-3322 — the gate/hook-race contention bugs.
- `PROJECT-GTKB-DETERMINISTIC-SERVICES-001-BRIDGE-MECHANICS` holds WI-3265
  (dispatch reliability).
- `PROJECT-GTKB-ROLE-STATUS-ORTHOGONALITY-DISPATCH` holds WI-4213 (active-status
  capability gate).

The contention-control primitives are already VERIFIED — the
`gtkb-bridge-scheduler-lanes-leases` program landed all six slices (lease
registry, serialized `atomic_index_update` INDEX writer, per-role concurrency,
lanes, aging). Remaining contention work is adoption + race-bug cleanup, not new
infrastructure. This consolidation makes that legible.

# Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority; INDEX is canonical.
- `GOV-STANDING-BACKLOG-001` — backlog-structure grooming authority; project
  membership + sub-project grouping are governed here.
- `.claude/rules/bridge-essential.md` — "Bridge integrity is the top-priority
  task" — making contention work legible serves the mandate.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — owner decision archived; cited.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — all current-state evidence read live
  from MemBase, not caches.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — execution helper is in-root
  (`.gtkb-state/`).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping below
  (read-back verification for a structural KB-grooming change).
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — flags retired poller WIs for lifecycle
  reconciliation.

# Prior Deliberations

- `DELIB-S378-ROLE-STATUS-ORTHOGONALITY-DISPATCH` — role/status model; Layer-2
  dispatch context.
- `DELIB-S381-ROLE-ENHANCEMENT-ISOLATION-DEPENDENCY-REFRAME` — S381 dogfooded
  the INDEX lost-update (the live Layer-1 evidence motivating WI-3513).
- The `gtkb-bridge-scheduler-lanes-leases` slice-1..6 VERIFIED thread family —
  the primitives this consolidation organizes adoption around.
- No prior deliberation consolidates the bridge-contention backlog; this is
  novel grooming. (Deliberation search:
  `bridge contention consolidation INDEX dispatch race`; nearest hits were the
  helper-parity NO-GOs and INDEX drift repair, none a consolidation.)

# Requirement Sufficiency

Existing requirements sufficient. No new requirement is introduced; this groups
already-tracked work items and flags retired ones. The owner directive is
grooming, not feature scope.

# Proposed Scope (itemized mutations for review)

## IP-1: Create three Layer sub-projects under BRIDGE-PROTOCOL-RELIABILITY

`insert_project` with `parent_project_id=PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`:

1. `PROJECT-GTKB-BRIDGE-CONTENTION-L1-INDEX-WRITES` — lost-update / concurrent
   INDEX-write contention.
2. `PROJECT-GTKB-BRIDGE-CONTENTION-L2-DISPATCH` — which-harness-handles-the-event
   dispatch contention.
3. `PROJECT-GTKB-BRIDGE-CONTENTION-L3-GATE-RACES` — concurrent hook/gate races on
   shared bridge state.

## IP-2: Assign work-item memberships (additive; home memberships preserved)

`link_project_work_item` (membership_role=member). Multi-membership is preserved
so each WI's existing home-project view is not orphaned; the new memberships
give the consolidated contention view.

- L1: WI-3513 (agent-edit serialization), WI-3280 (INDEX edit race coordination).
- L2: WI-3265 (trigger unreliable in codex exec), WI-3485 (active-session
  suppression), WI-4213 (active-status capability gate),
  WI-AUTO-SPEC-INTAKE-57A736 (per-document lease dispatch suppression).
- L3: WI-3320 (compliance-audit shared-file race), WI-3334 (gate fires on every
  INDEX edit), WI-3322 (auto-WI rejected by gate).

**Open design question for Loyal Opposition**: additive multi-membership vs.
move-and-reparent. This proposal recommends additive membership to avoid
disrupting `RELIABILITY-FIXES` / `BRIDGE-MECHANICS` / `ROLE-STATUS-ORTHOGONALITY`
rollups, but defers to LO if move semantics are preferred to avoid double-count
in the parent rollup.

## IP-3: Flag retired-but-open poller WIs for lifecycle reconciliation

Set `status_detail` (no lifecycle-state mutation) on the three
`resolution_status=retired` poller WIs already in BRIDGE-PROTOCOL-RELIABILITY
(`GTKB-BRIDGE-POLLER-001`, `GTKB-BRIDGE-POLLER-PRIME-CLASSIFICATION-REFINEMENT`,
`GTKB-BRIDGE-POLLER-COMPLEXITY-REFACTOR`) noting they are superseded by the
retired-poller → event-trigger decision and should not surface as open
contention work. Retirement of the WI lifecycle itself remains an owner/
governance action (not performed here).

# Specification-Derived Verification Plan

| Behavior | Verification command (in-root venv) | Expected |
|---|---|---|
| 3 sub-projects exist with correct parent | `groundtruth-kb\.venv\Scripts\python.exe -c "from groundtruth_kb.db import KnowledgeDB; db=KnowledgeDB(); print([p['id'] for p in db.list_projects() if p.get('parent_project_id')=='PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY'])"` | Lists the three `PROJECT-GTKB-BRIDGE-CONTENTION-L{1,2,3}-*` ids. |
| L1 membership | `groundtruth-kb\.venv\Scripts\python.exe -c "from groundtruth_kb.db import KnowledgeDB; print(sorted(w['work_item_id'] for w in KnowledgeDB().list_project_work_items('PROJECT-GTKB-BRIDGE-CONTENTION-L1-INDEX-WRITES')))"` | `['WI-3280', 'WI-3513']`. |
| L2 membership | analogous for L2 | contains WI-3265, WI-3485, WI-4213, WI-AUTO-SPEC-INTAKE-57A736. |
| L3 membership | analogous for L3 | `['WI-3320', 'WI-3322', 'WI-3334']`. |
| Retired pollers flagged | `groundtruth-kb\.venv\Scripts\python.exe -c "from groundtruth_kb.db import KnowledgeDB; db=KnowledgeDB(); print(db.get_work_item('GTKB-BRIDGE-POLLER-001').get('status_detail'))"` | Contains the supersession note. |
| Helper idempotent | rerun `apply-bridge-contention-consolidation.py` | Second run reports all `skipped_existing`. |

(No automated test; this is a non-source KB-grooming change verified by read-back.)

# Acceptance Criteria

- Helper `.gtkb-state/apply-bridge-contention-consolidation.py` exists; `--dry-run`
  previews all mutations; live run produces the five verification outputs above.
- Both preflights pass on this bridge id.
- No work-item lifecycle state is transitioned (memberships + status_detail only).

# Risks / Rollback

- **Risk**: additive multi-membership double-counts WIs in the parent rollup.
  **Mitigation**: documented as an open question for LO; sub-project rollups are
  views, not authoritative state; append-only correction possible.
- **Risk**: sub-project proliferation. **Mitigation**: exactly three, mapped to
  the durable 3-layer taxonomy; not per-WI.
- **Rollback**: append-only — set sub-project `status=retired` via new version
  and membership rows `membership_status=inactive`; no destructive deletes.

# Bridge INDEX Update Evidence

NEW entry inserted at top via the serialized `atomic_index_update` writer
(dogfooding `gtkb-index-agent-edit-serialization-scoping`):

```text
Document: gtkb-bridge-contention-consolidation
NEW: bridge/gtkb-bridge-contention-consolidation-001.md
```

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
