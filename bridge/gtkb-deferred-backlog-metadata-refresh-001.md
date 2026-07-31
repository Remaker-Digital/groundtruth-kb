NEW

# Deferred backlog metadata refresh (stale deferral audit)

bridge_kind: prime_proposal
Document: gtkb-deferred-backlog-metadata-refresh
Version: 001
Author: Prime Builder (Cursor, harness E)
Date: 2026-06-29 UTC

author_identity: prime-builder/cursor
author_harness_id: E
author_session_context_id: cursor-s514-deferred-backlog-metadata-refresh
author_model: Cursor Agent
author_model_version: interactive
author_model_configuration: ::init gtkb pb; owner-directed deferral audit S514

Project Authorization: PAUTH-PROJECT-GTKB-GOVERNANCE-HARDENING-GOVERNANCE-HARDENING-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-GOVERNANCE-HARDENING
Work Item: GTKB-GOV-004

target_paths: []

implementation_scope: membase_backlog_metadata
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Summary

Owner-directed audit (S514) found **four** uncompleted work items whose deferral metadata is stale or vague relative to live MemBase and bridge evidence. This proposal authorizes **metadata-only** corrections via governed `gt backlog update` (and `KnowledgeDB.update_work_item` only where `depends_on_work_items` must change and the CLI lacks a flag). **No source, test, hook, or bridge-file edits.**

**In scope (4 updates):**

| ID | Action |
|----|--------|
| `GTKB-MASS-001` | Clear stale isolation deferral; restate current gates |
| `GTKB-DORA-002` | Clear stale “future/deferred” framing; DORA-001 prerequisite is VERIFIED |
| `GTKB-DASHBOARD-003` | Refresh dependencies/status; **remain sequenced** behind Slice 2.1 visibility (latest bridge head NO-GO) |
| `WI-3407` | Replace vague deferral text with explicit blocker `WI-4482` |

**Explicitly out of scope:**

- `GTKB-DASHBOARD-RETENTION` — remains `resolution_status=deferred` (contingent; valid)
- Implementation of any resumed program work (mass adoption, DORA panels, dashboard slice 3, decision-capture skill)
- Creating new work items or changing `implementation_order` / priority ranks

## Evidence (live reads 2026-06-29)

| Dependency / gate | Live status | Implication |
|-------------------|-------------|-------------|
| `GTKB-ISOLATION-019` | `retired` — bridge `gtkb-isolation-019-program-closeout-008` VERIFIED | **GTKB-MASS-001** isolation deferral is stale |
| `GTKB-DORA-001` | `verified` — `bridge/gtkb-dora-telemetry-foundation-008` | **GTKB-DORA-002** prerequisite satisfied |
| `GTKB-DASHBOARD-002` | `retired` (parent grouping); slices 2.2/2.3 `resolved` | Parent dependency obsolete for **GTKB-DASHBOARD-003** |
| `gtkb-dashboard-industry-alignment-slice2a-visibility` | Latest head `-008` = **NO-GO** | Slice 3 still blocked on 2.1 |
| `WI-4482` | `open` — envelope/explicit-hint umbrella | **WI-3407** explicit blocker |

## Specification Links

- `GOV-STANDING-BACKLOG-001` — MemBase `work_items` is backlog authority; metadata must reflect live gates.
- `GOV-08` — KB is single source of truth; stale `status_detail` / `depends_on_work_items` misleads prioritization.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — deferral claims must derive from fresh canonical reads.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — this slice is metadata hygiene only; not implementation approval for the underlying programs.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — linkage block above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification plan below (read-back assertions).

## Prior Deliberations

- Owner session S514 deferral audit (this conversation) — identified stale vs valid deferrals.
- `DELIB-20261916` — isolation program closeout context for `GTKB-ISOLATION-019`.
- `DELIB-S365-ENV-SOT-AGENT-RED-DEFERRAL` — **not** in scope here (`WI-3430` unchanged).
- `DELIB-2238` / envelope program — informs `WI-3407` blocker (`WI-4482`).

## Owner Decisions / Input

Owner reply **“Yes please”** (2026-06-29) to prepare governed MemBase updates for the four stale-deferral items identified in the S514 audit. No reprioritization of mass adoption, DORA panels, or dashboard slice 3 beyond clearing misleading deferral metadata.

## Requirement Sufficiency

Existing requirements are sufficient. This is backlog metadata reconciliation under `GTKB-GOV-004` (classify/reconcile non-terminal work items into accurate status). No new SPEC/GOV/ADR required.

## Specification-Derived Verification Plan

Post-implementation read-back (all must pass):

1. `gt backlog list --id GTKB-MASS-001 --json` — `resolution_status=open`; `status_detail` cites isolation VERIFIED + current mass-adoption gates (not “behind GTKB-ISOLATION-019”).
2. `gt backlog list --id GTKB-DORA-002 --json` — `resolution_status=open`; `status_detail` cites `GTKB-DORA-001` VERIFIED; no “Future/deferred” framing.
3. `gt backlog list --id GTKB-DASHBOARD-003 --json` — `status_detail` cites DORA verified + slice2a-visibility NO-GO blocker; `depends_on_work_items` no longer lists retired `GTKB-DASHBOARD-002`.
4. `gt backlog list --id WI-3407 --json` — `status_detail` cites `WI-4482`; description no longer ends with vague “Deferred per envelope-convention scoping”.
5. `gt backlog list --resolution-status deferred --json` — still exactly **one** row: `GTKB-DASHBOARD-RETENTION` (unchanged).

## Implementation commands (exact)

All invocations use `--owner-approved` and cite this bridge thread in `--change-reason`.

### 1. GTKB-MASS-001

```powershell
E:\GT-KB\groundtruth-kb\.venv\Scripts\gt.exe backlog update GTKB-MASS-001 ^
  --status-detail "Active mass-adoption readiness program. Isolation closeout GTKB-ISOLATION-019 VERIFIED 2026-06-04; no longer deferred behind isolation. Remaining gates: release-readiness evidence, worktree commit scope, owner reprioritization per GTKB-MASS-ADOPTION-READINESS-PLAN-2026-04-20." ^
  --owner-approved ^
  --change-reason "S514 deferred-metadata refresh per bridge/gtkb-deferred-backlog-metadata-refresh-001.md GO; clear stale GTKB-ISOLATION-019 deferral."
```

Then append-only `depends_on_work_items` correction via Python API (CLI has no flag):

```python
# scripts/_one_shot_deferred_metadata_depends.py (implementation report may inline)
# GTKB-MASS-001: remove GTKB-ISOLATION-019 from depends_on; retain plan doc refs
new_deps = ["GT-KB", "CODEX-INSIGHT-DROPBOX", "GTKB-MASS-ADOPTION-READINESS-PLAN-2026-04-20.md"]
db.update_work_item("GTKB-MASS-001", changed_by, change_reason, depends_on_work_items=json.dumps(new_deps), owner_approved=True)
```

### 2. GTKB-DORA-002

```powershell
E:\GT-KB\groundtruth-kb\.venv\Scripts\gt.exe backlog update GTKB-DORA-002 ^
  --status-detail "Active backlog item; prerequisite GTKB-DORA-001 VERIFIED (bridge/gtkb-dora-telemetry-foundation-008). Ready for normal prioritization; approval_state remains auq_required." ^
  --owner-approved ^
  --change-reason "S514 deferred-metadata refresh per bridge/gtkb-deferred-backlog-metadata-refresh-001.md GO; DORA-001 prerequisite satisfied."
```

### 3. GTKB-DASHBOARD-003

```powershell
E:\GT-KB\groundtruth-kb\.venv\Scripts\gt.exe backlog update GTKB-DASHBOARD-003 ^
  --status-detail "Dashboard Slice 3 backlog. GTKB-DORA-001 verified. Slice 2.2/2.3 resolved; Slice 2.1 visibility blocked (bridge/gtkb-dashboard-industry-alignment-slice2a-visibility latest NO-GO at -008). Retired parent GTKB-DASHBOARD-002 superseded by child slices." ^
  --owner-approved ^
  --change-reason "S514 deferred-metadata refresh per bridge/gtkb-deferred-backlog-metadata-refresh-001.md GO; refresh stale Future/deferred framing and dependencies."
```

`depends_on_work_items` → `["GTKB-DORA-001", "bridge/gtkb-dashboard-industry-alignment-slice2a-visibility"]` via Python API (same one-shot script).

### 4. WI-3407

```powershell
E:\GT-KB\groundtruth-kb\.venv\Scripts\gt.exe backlog update WI-3407 ^
  --status-detail "Blocked on envelope/explicit-hint program (WI-4482, PROJECT-GTKB-ENVELOPE-OPEN-CLOSE-ACTION-REFINEMENT). Owner agreed skill should exist (S363); resume after WI-4482 completes or owner elevates." ^
  --description-file .gtkb-state/deferred-metadata-refresh/WI-3407-description.md ^
  --owner-approved ^
  --change-reason "S514 deferred-metadata refresh per bridge/gtkb-deferred-backlog-metadata-refresh-001.md GO; replace vague envelope deferral with WI-4482 gate."
```

Description file removes the terminal sentence “Deferred per same owner preference as task for envelope-convention scoping.” and replaces with explicit `WI-4482` gate (content prepared at implementation time from current row minus vague deferral + explicit blocker paragraph).

## Scope Exclusions

- No changes to `GTKB-DASHBOARD-RETENTION`, `WORKLIST-…-CLAUDE-DESIGN-GUI-EXPLORATION`, `WORKLIST-ZERO-KNOWLEDGE-…`, `WI-3430`, `WI-4650`, `WI-4835`, `WI-4836`
- No `implementation_order` / priority changes
- No bridge threads filed for the underlying programs

## Risks / Rollback

- **Risk:** Prematurely signaling “ready to implement” for mass adoption or DORA panels. **Mitigation:** updates restate remaining gates (`auq_required`, slice 2.1 NO-GO, release readiness).
- **Rollback:** append-only `work_items` version history; revert by inserting prior field values with `--change-reason` citing botched refresh.

## Recommended Commit Type

`docs: refresh stale deferred backlog metadata (GTKB-GOV-004 S514 slice)` — MemBase-only; optional commit if `groundtruth.db` is tracked in the commit scope the owner chooses; otherwise implementation report + VERIFIED without git commit per standing dirty-worktree practice.
